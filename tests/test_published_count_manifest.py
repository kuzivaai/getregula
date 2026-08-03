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
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MANIFEST = REPO / "data" / "published_count_manifest.json"
SITE_FACTS = REPO / "data" / "site_facts.json"


def _manifest() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def _canonical_count() -> int:
    facts = json.loads(SITE_FACTS.read_text(encoding="utf-8"))
    return int(facts["counts"]["tests"]["total_collected"])


def _tracked_files() -> list:
    out = subprocess.run(["git", "ls-files"], cwd=str(REPO),
                         capture_output=True, text=True, check=False).stdout
    return [Path(p) for p in out.splitlines() if p]



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
    """
    grouped = f"{count:,}"
    variants = {str(count), grouped, grouped.replace(",", ".")}
    return re.compile(
        r"(?<!\w)(" + "|".join(re.escape(v) for v in sorted(variants))
        + r")(?!\d)")

class TestPublishedCountManifest(unittest.TestCase):
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
            rx.findall(f"| {count:,} |"), [f"{count:,}"],
            "the narrowed lookbehind stopped seeing a real published claim, "
            "so the guard has been blinded rather than corrected")

    def test_count_literal_appears_nowhere_outside_the_manifest(self):
        count = _canonical_count()
        m = _manifest()
        allowed = set(m["published_surfaces"])
        allowed |= {e["path"] for e in m["non_surface_carriers"]}
        allowed_prefixes = tuple(
            e["path"] for e in m["excluded_by_design"])

        # Match the number both bare and comma-grouped, and the DE/PT-BR
        # dot-grouped form, since those defeated a manual sweep before.
        pattern = _count_pattern(count)

        # A digit sequence is not a claim just because it appears in a file
        # (measurement rule 4d). Machine-generated scan artefacts carry
        # structural integers -- source line numbers, offsets, counts of
        # findings in someone else's repository -- and one of them will
        # collide with the test count sooner or later. That happened on
        # 2026-07-31: a `"line":` value in
        # benchmarks/results/blog_scan_2026_04/khoj.json equalled the
        # published count exactly. The colliding figure is deliberately not
        # written here, because this file is inside the corpus the test
        # scans, so quoting it would fail the very check it explains.
        #
        # This exempts the COLLISION, never the file: any other occurrence in
        # the same file still fails the test, so a genuine stale claim sitting
        # in a JSON artefact is still caught. The keys below are structural by
        # definition; none of them can hold a published test count.
        structural_json_key = re.compile(
            r'"(line|line_number|start_line|end_line|lineno|offset|column|'
            r'total_lines|loc|size|bytes)"\s*:\s*$')

        def _is_structural(text, match):
            """True when the match is the value of a structural JSON key."""
            return bool(structural_json_key.search(text[:match.start()]))

        violations = []
        for rel in _tracked_files():
            posix = rel.as_posix()
            if posix in allowed or posix.startswith(allowed_prefixes):
                continue
            if rel.suffix.lower() not in (
                    ".md", ".html", ".txt", ".json", ".py", ".yaml", ".yml"):
                continue
            path = REPO / rel
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            hits = [m for m in pattern.finditer(text)
                    if not _is_structural(text, m)]
            if hits:
                violations.append(posix)

        self.assertEqual(
            violations, [],
            f"the published test count ({count}) appears in files not "
            f"listed in data/published_count_manifest.json: {violations}. "
            f"Either add the file to the manifest (and to every future "
            f"count correction), or remove the literal. A surface that "
            f"carries the number without being in the manifest will be "
            f"missed by the next correction and left publishing a stale "
            f"figure.")

    def test_scan_would_actually_catch_a_violation(self):
        """Vacuity control: prove the scan can return a negative."""
        count = _canonical_count()
        grouped = f"{count:,}"
        pattern = re.compile(
            r"(?<!\d)(" + re.escape(str(count)) + "|"
            + re.escape(grouped) + r")(?!\d)")
        planted = f"This page claims {grouped} tests were run."
        self.assertTrue(
            pattern.search(planted),
            "the violation pattern does not match a planted literal, so a "
            "clean run of the scan above would prove nothing")

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
