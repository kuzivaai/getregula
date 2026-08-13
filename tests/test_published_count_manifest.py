# regula-ignore
"""The published test count may appear only where the manifest permits.

Inverted class-kill, mirroring tests/test_packaged_data.py. That test
derives what MUST be declared from the filesystem; this one enumerates
where a value is ALLOWED and then scans the repository for violations.

Why it exists: "nine published surfaces" was once carried in prose,
inherited from a label whose own components summed to ten, and repeated
without anyone counting them. The same trusting-prose-over-measurement
error produced a false claim that verify_seo gated CI. A surface list
that lives only in prose will drift again; a surface list that is
committed data and enforced by a scan cannot.

The consequence this prevents: an eleventh surface starts carrying the
count, nobody notices, and a future correction misses it — leaving a
known-false number published somewhere while every audited surface reads
correct.
"""

import json
import re
import subprocess
import sys
import unittest
from unittest import mock
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MANIFEST = REPO / "data" / "published_count_manifest.json"
SITE_FACTS = REPO / "data" / "site_facts.json"
RECORD_CLASSES = REPO / "data" / "count_record_classes.json"

sys.path.insert(0, str(REPO / "scripts"))
from count_record_policy import (  # noqa: E402
    classify_count_occurrences,
    discover_tracked_files,
    read_tracked_files,
    validate_record_policy,
    verify_record_provenance,
)


def _manifest() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def _canonical_count() -> int:
    facts = json.loads(SITE_FACTS.read_text(encoding="utf-8"))
    return int(facts["counts"]["tests"]["total_collected"])


def _tracked_files() -> list:
    return discover_tracked_files(REPO)



def _count_pattern(count: int):
    """The literal-scan regex, shared so a test can exercise it directly.

    Matches the count bare, comma-grouped and dot-grouped (the DE/PT-BR
    form, which defeated a manual sweep before).

    `(?<!\\w)`, not `(?<!\\d)`. Excluding only a preceding DIGIT lets the
    count match inside a longer alphanumeric run, which is the exact defect
    scripts/cascade_count.py::_patterns already carries a comment about
    ("ee2353d8330 must NOT match ... the 28 July near-miss"). MEASURED
    2026-07-31: at one canonical value the scan failed naming
    scripts/report.py, where every hit was inside a hex colour literal of
    the form `#dcNNNN` and nothing else. A hex colour is not a published
    claim, and allowlisting the file would have blinded the guard to every
    real claim in it. The colliding value is deliberately not written into
    this file, for the same reason the note inside the test gives.

    `(?!\\w)`, not `(?!\\d)`, for the symmetric reason. MEASURED
    2026-08-07: at one canonical value the scan failed naming
    data/public_claim_surfaces.json, where the only hit was inside a
    stable_id of the form `cli:NNNNfb52a8321880`: the count at the START
    of a hex run, which the leading lookbehind cannot see. Excluding only
    a trailing digit let hex letters follow the count.
    """
    grouped = f"{count:,}"
    variants = {str(count), grouped, grouped.replace(",", ".")}
    return re.compile(
        r"(?<!\w)(" + "|".join(re.escape(v) for v in sorted(variants))
        + r")(?!\w)")

class TestPublishedCountManifest(unittest.TestCase):
    def _policy(self, *historical):
        return {
            "schema_version": 1,
            "records": [
                {
                    "path": path,
                    "record_class": "dated_evidence",
                    "recorded_at": "2026-08-05",
                    "evidence_commit": "a" * 40,
                    "immutable_sha256": digest,
                    "rationale": "Synthetic dated measurement record.",
                }
                for path, digest in historical
            ],
        }

    def test_dated_evidence_preserves_historically_true_count(self):
        count = 2000 + 468
        files = {"records/2026-08-05-one.md": f"At capture: {count:,} tests.\n"}
        digest = __import__("hashlib").sha256(
            files["records/2026-08-05-one.md"].encode()).hexdigest()
        violations = classify_count_occurrences(
            count, files, set(), set(), self._policy(
                ("records/2026-08-05-one.md", digest)))
        self.assertEqual(violations, [])

    def test_stale_current_count_fails(self):
        count = 2000 + 468
        violations = classify_count_occurrences(
            count, {"current.md": f"Current: {count:,} tests.\n"},
            set(), set(), self._policy())
        self.assertEqual(violations, ["current.md"])

    def test_sibling_dated_records_receive_same_treatment(self):
        count = 2000 + 468
        files = {
            "records/2026-08-05-one.md": f"At capture: {count:,} tests.\n",
            "records/2026-08-05-two.md": f"At capture: {count} tests.\n",
        }
        historical = tuple(
            (path, __import__("hashlib").sha256(text.encode()).hexdigest())
            for path, text in files.items())
        self.assertEqual(classify_count_occurrences(
            count, files, set(), set(), self._policy(*historical)), [])

    def test_self_claimed_historical_file_fails_without_registry_metadata(self):
        count = 2000 + 468
        files = {"ordinary.md": (
            f"record_class: dated_evidence\nAt capture: {count:,} tests.\n")}
        self.assertEqual(classify_count_occurrences(
            count, files, set(), set(), self._policy()), ["ordinary.md"])

    def test_current_surface_cannot_be_registered_as_historical(self):
        count = 2000 + 468
        text = f"Current: {count:,} tests.\n"
        digest = __import__("hashlib").sha256(text.encode()).hexdigest()
        with self.assertRaisesRegex(ValueError, "current surface"):
            validate_record_policy(
                self._policy(("current.md", digest)), {"current.md": text},
                {"current.md"}, set())

    def test_renamed_record_does_not_inherit_historical_class(self):
        count = 2000 + 468
        old = f"At capture: {count:,} tests.\n"
        digest = __import__("hashlib").sha256(old.encode()).hexdigest()
        with self.assertRaisesRegex(ValueError, "missing tracked file"):
            validate_record_policy(
                self._policy(("records/old.md", digest)),
                {"records/new.md": old}, set(), set())

    def test_duplicate_literal_only_nonhistorical_record_violates(self):
        count = 2000 + 468
        files = {
            "records/2026-08-05-old.md": f"At capture: {count:,} tests.\n",
            "current.md": f"Current: {count:,} tests.\n",
        }
        digest = __import__("hashlib").sha256(
            files["records/2026-08-05-old.md"].encode()).hexdigest()
        self.assertEqual(classify_count_occurrences(
            count, files, set(), set(),
            self._policy(("records/2026-08-05-old.md", digest))), ["current.md"])

    def test_discovery_failure_cannot_become_empty_clean_result(self):
        failed = subprocess.CompletedProcess(
            ["git", "ls-files", "-z"], 128, stdout=b"", stderr=b"fatal")
        with mock.patch("count_record_policy.subprocess.run",
                        return_value=failed):
            with self.assertRaisesRegex(RuntimeError, "git ls-files failed"):
                discover_tracked_files(REPO)

    def test_git_nonzero_with_partial_output_still_fails(self):
        failed = subprocess.CompletedProcess(
            ["git", "ls-files", "-z"], 1,
            stdout=b"README.md\0", stderr=b"partial failure")
        with mock.patch("count_record_policy.subprocess.run",
                        return_value=failed):
            with self.assertRaisesRegex(RuntimeError, "partial failure"):
                discover_tracked_files(REPO)

    def test_broad_path_exclusions_are_rejected(self):
        policy = self._policy()
        policy["excluded_by_design"] = [{"path": "docs/improvement/"}]
        with self.assertRaisesRegex(ValueError, "broad exclusion"):
            validate_record_policy(policy, {}, set(), set())

    def test_unlisted_text_suffix_is_scanned(self):
        count = 2000 + 468
        files = {"claims.csv": f"claim,count\ntests,{count}\n"}
        self.assertEqual(classify_count_occurrences(
            count, files, set(), set(), self._policy()), ["claims.csv"])

    def test_tracked_file_read_failure_is_not_silently_skipped(self):
        with mock.patch("pathlib.Path.read_bytes",
                        side_effect=OSError("unreadable")):
            with self.assertRaisesRegex(RuntimeError, "cannot read tracked file"):
                read_tracked_files(REPO, [Path("ordinary.txt")])

    def test_nonexistent_evidence_commit_fails(self):
        record = self._policy(("records/2026-08-05.md", "b" * 64))["records"][0]
        failed = subprocess.CompletedProcess([], 128, stdout=b"", stderr=b"fatal")
        with mock.patch("count_record_policy.subprocess.run",
                        return_value=failed):
            with self.assertRaisesRegex(ValueError, "does not exist"):
                verify_record_provenance(REPO, record)

    def test_path_missing_at_evidence_commit_fails(self):
        record = self._policy(("records/2026-08-05.md", "b" * 64))["records"][0]
        results = [
            subprocess.CompletedProcess([], 0, stdout=b"", stderr=b""),
            subprocess.CompletedProcess([], 128, stdout=b"", stderr=b"missing"),
        ]
        with mock.patch("count_record_policy.subprocess.run",
                        side_effect=results):
            with self.assertRaisesRegex(ValueError, "path missing"):
                verify_record_provenance(REPO, record)

    def test_evidence_commit_blob_mismatch_fails(self):
        record = self._policy(("records/2026-08-05.md", "b" * 64))["records"][0]
        results = [
            subprocess.CompletedProcess([], 0, stdout=b"", stderr=b""),
            subprocess.CompletedProcess([], 0, stdout=b"historical", stderr=b""),
        ]
        with mock.patch("count_record_policy.subprocess.run",
                        side_effect=results):
            with self.assertRaisesRegex(ValueError, "blob hash mismatch"):
                verify_record_provenance(REPO, record)

    def test_manifest_is_wellformed(self):
        m = _manifest()
        self.assertTrue(m["published_surfaces"], "manifest lists no surfaces")
        for entry in m["published_surfaces"]:
            self.assertTrue(
                (REPO / entry).exists(),
                f"manifest lists {entry} which does not exist; a stale "
                f"manifest protects nothing")
        for entry in m["non_surface_carriers"]:
            self.assertIn(entry["role"], ("source", "generated"))
            self.assertTrue((REPO / entry["path"]).exists())

        files = read_tracked_files(REPO, _tracked_files())
        validate_record_policy(
            json.loads(RECORD_CLASSES.read_text(encoding="utf-8")), files,
            set(m["published_surfaces"]),
            {entry["path"] for entry in m["non_surface_carriers"]}, REPO)

    def test_a_hex_colour_is_not_a_published_count(self):
        """THE CONTROL for the lookbehind, both ways.

        Constructed from the live canonical rather than a literal, because
        this file is inside the corpus the scan walks and a literal here
        would fail the very check it explains.
        """
        count = _canonical_count()
        rx = _count_pattern(count)
        self.assertEqual(
            rx.findall(f'    exec_colour = "#dc{count}"'), [],
            "the count matched inside a hex colour literal, so any file "
            "using that colour is a false violation")
        self.assertEqual(
            rx.findall(f"sha256:ee{count}d8330ed8de1"), [],
            "the count matched inside a hash path (the 28 July near-miss)")
        self.assertEqual(
            rx.findall(f'"stable_id": "cli:{count}fb52a8321880"'), [],
            "the count matched at the START of a hex run (the 7 August "
            "public_claim_surfaces.json collision); the trailing lookahead "
            "must exclude any word character, not just a digit")
        self.assertEqual(
            rx.findall(f"| {count:,} |"), [f"{count:,}"],
            "the narrowed lookbehind stopped seeing a real published claim, "
            "so the guard has been blinded rather than corrected")

    def test_count_literal_appears_nowhere_outside_the_manifest(self):
        count = _canonical_count()
        m = _manifest()
        files = read_tracked_files(REPO, _tracked_files())

        violations = classify_count_occurrences(
            count, files, set(m["published_surfaces"]),
            {entry["path"] for entry in m["non_surface_carriers"]},
            json.loads(RECORD_CLASSES.read_text(encoding="utf-8")), REPO)

        self.assertEqual(
            violations, [],
            f"the published test count ({count}) appears in files not "
            f"authorised by the current-carrier or dated-record policies: "
            f"{violations}. Classify the exact immutable dated record with "
            f"provenance, add a genuine current carrier to the manifest, or "
            f"remove the literal. A surface that "
            f"carries the number without being in the manifest will be "
            f"missed by the next correction and left publishing a stale "
            f"figure.")

    def test_scan_would_actually_catch_a_violation(self):
        """Vacuity control: prove the scan can return a negative."""
        count = _canonical_count()
        planted = {"planted.rst": f"This page claims {count:,} tests.\n"}
        self.assertEqual(
            classify_count_occurrences(
                count, planted, set(), set(), self._policy()),
            ["planted.rst"],
            "the production classifier missed a planted violation")

    def test_canonical_source_is_generated_not_handwritten(self):
        """The number must come from collection, never a hand-typed literal."""
        src = (REPO / "scripts" / "site_facts.py").read_text(encoding="utf-8")
        self.assertIn(
            "--collect-only", src,
            "site_facts.count_tests no longer derives the count from pytest "
            "collection; a hand-maintained count is how the double-count "
            "went unnoticed for so long")

    def test_trust_publishes_the_custom_runners_own_function_count(self):
        """The SECOND published test count, which nothing was guarding.

        `docs/TRUST.md` publishes how many functions the legacy
        `tests/test_classification.py` runner executes, alongside the
        pytest-collected count. `scripts/cascade_count.py` propagates only the
        collected count, so this one drifts silently.

        MEASURED 2026-07-29: wiring two new test files into the runner, which
        `.claude/rules/tests.md` requires, moved the runner from 963 functions
        to 978 while `docs/TRUST.md` still read 963. The cascade did not catch
        it because the figure is outside the manifest, and no test referenced
        the number at all.

        Both figures are recomputed here rather than asserted, so neither can
        go stale without this failing. The total mirrors the runner's own
        selection predicate: module-level callables named `test_*` or carrying
        RUNNER_ALIAS_PREFIX.

        ENUMERATED, not spotted. `git ls-files | xargs grep -n 963` finds the
        figure in two places on a published surface, `docs/TRUST.md` line 95
        (inside a reproduction instruction) and line 381 (in the summary
        table), and this guard covers BOTH. The other tracked hits are
        `CHANGELOG.md`, `docs/improvement/*` and two code comments, all of
        which legitimately record what was true on a past date, plus hash
        coincidences in `uv.lock` that must never be text-replaced.

        NOT machine-checked, and stated rather than left implied: the runner's
        `N passed` figure. Deriving it costs a full runner execution, about
        twenty minutes, which does not belong in a unit test. It has to be
        re-derived by hand whenever the runner is next run to completion.
        """
        sys.path.insert(0, str(REPO / "tests"))
        import test_classification as tc

        total = len([
            name for name, obj in vars(tc).items()
            if (name.startswith("test_")
                or name.startswith(tc.RUNNER_ALIAS_PREFIX))
            and callable(obj)])
        in_file = len(re.findall(
            r"^def (test_\w+)",
            (REPO / "tests" / "test_classification.py").read_text(
                encoding="utf-8"),
            re.M))

        trust = (REPO / "docs" / "TRUST.md").read_text(encoding="utf-8")
        m = re.search(
            r"runner executes ([\d,]+) functions, ([\d,]+) defined in-file",
            trust)
        self.assertIsNotNone(
            m, "docs/TRUST.md no longer states the runner's function count in "
               "the expected form; this guard has lost its target and must be "
               "retargeted rather than deleted")
        published_total = int(m.group(1).replace(",", ""))
        published_in_file = int(m.group(2).replace(",", ""))

        self.assertEqual(
            published_total, total,
            f"docs/TRUST.md publishes {published_total} runner functions; the "
            f"runner selects {total}. Wiring a test file into "
            f"tests/test_classification.py changes this number and "
            f"scripts/cascade_count.py does not propagate it.")
        self.assertEqual(
            published_in_file, in_file,
            f"docs/TRUST.md publishes {published_in_file} in-file test "
            f"functions; the file defines {in_file}.")

        # The second location: the reproduction instruction.  Do not require
        # it to quote a pass total: that total is only trustworthy after a
        # complete run, whereas discovery is cheap and deterministic.
        quoted = re.search(
            r"runner currently discovers ([\d,]+) functions", trust)
        self.assertIsNotNone(
            quoted,
            "docs/TRUST.md no longer states the runner's discovered count in the "
            "expected form; retarget this guard rather than dropping it")
        self.assertEqual(
            int(quoted.group(1).replace(",", "")), total,
            f"the runner reproduction text in docs/TRUST.md names "
            f"{quoted.group(1)} test functions; the runner selects {total}. "
            f"A reader following that instruction sees a different number.")


if __name__ == "__main__":
    unittest.main()
