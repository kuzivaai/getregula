#!/usr/bin/env python3
# regula-ignore
"""The cascade tool must be incapable of touching anything off-manifest.

The required control (owner-set): plant an out-of-manifest literal AND a
lockfile in a fixture tree, and prove both come through untouched. Without
that, the tool is a promise rather than a mechanism.

Stdlib only.
"""

import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import cascade_count as cc  # noqa: E402


UV_LOCK_FRAGMENT = """
wheels = [
    {{ url = "https://files.pythonhosted.org/packages/47/c0/80ecd9bd45776109fab14040e478bf63e456967c9ddee{old}d8330ed8de1/brotlicffi.whl", hash = "sha256:3c9544f83cb715d95d7eab3af4adbbef8b2093ad63822{old}5feb1a57ec", size = 222{old}, upload-time = "2026-03-05T19:53:52.215Z" }},
]
"""


class TestCascadeRefusal(unittest.TestCase):

    def test_lockfile_class_is_refused_even_if_manifested(self):
        """The second belt. A manifest edit must not be able to add one."""
        for name in ("uv.lock", "poetry.lock", "go.sum", "Cargo.lock",
                     "package-lock.json", "sig.asc", "x.sha256"):
            with self.assertRaises(cc.RefusedError, msg=name):
                cc.assert_permitted(name)

    def test_path_escape_is_refused(self):
        for bad in ("../outside.md", "/etc/passwd"):
            with self.assertRaises(cc.RefusedError, msg=bad):
                cc.assert_permitted(bad)

    def test_ordinary_surfaces_are_permitted(self):
        for ok in ("README.md", "site/index.html", "data/site_facts.json"):
            cc.assert_permitted(ok)  # must not raise

    def test_the_real_uv_lock_content_survives_the_replacement_logic(self):
        """THE CONTROL, reproducing the actual near-miss.

        The 28 July near-miss rewrote a URL hash path and an integrity size
        field inside uv.lock when 2353 -> 2354 was applied globally. Here the
        same content is fed through the tool's own matcher. Nothing may
        change: the digits sit inside longer alphanumeric runs, so the
        context-bound pattern must not match them.
        """
        old, new = 2353, 2354
        content = UV_LOCK_FRAGMENT.format(old=old)
        result = content
        for rx in cc._patterns(old):
            result = rx.sub(str(new), result)
        self.assertEqual(
            result, content,
            "the cascade matcher rewrote lockfile content; the context-bound "
            "pattern is not tight enough and the 28 July near-miss would "
            "recur")

    def test_out_of_manifest_literal_is_never_a_candidate(self):
        """Refusal is by construction: the tool iterates the manifest, so a
        file that is not in it is never opened. Assert the manifest does not
        contain any denied class, which is the only way one could be reached.
        """
        for rel in cc.manifest_surfaces():
            cc.assert_permitted(rel)

    def test_stale_value_detection_is_bounded(self):
        """A wide net is how a size field gets rewritten. The protections
        are the candidate SHAPE (4-digit or grouped thousands, non-word
        boundaries) and the COUNT_TEMPLATES unit requirement. There is no
        magnitude window any more; see the next test for why."""
        new = 2354
        text = "tests 2353 passing and size 222353"
        stale = cc._stale_values(text, new)
        self.assertIn(2353, stale, "a real stale count was not detected")
        self.assertNotIn(222353, stale, "6-digit value treated as a count")

    def test_out_of_band_stale_counts_are_nominated(self):
        """N57 sub-item 1. An undisclosed [0.5x, 2x] window meant the tool
        structurally could not see docs/architecture.md's "1,223 tests"
        against a canonical of 2,618; that file was corrected by hand and
        only the at-rest test and claim_auditor, which have no floor, could
        have caught a recurrence. The window is gone: magnitude must never
        decide staleness, only shape and unit."""
        below_half = cc._stale_values("45 test files, 1,223 tests", 2618)
        self.assertIn(1223, below_half,
                      "a stale count below half of canonical was skipped; "
                      "the N57-1 magnitude floor is back")
        above_double = cc._stale_values("we ship 6,000 tests", 2618)
        self.assertIn(6000, above_double,
                      "a stale count above double canonical was skipped; "
                      "the N57-1 magnitude ceiling is back")

    def test_years_in_band_are_not_rewritten(self):
        """THE SECOND CONTROL. With canonical 2,354 the +/-20% band spans
        1883-2824, which contains the year 2026. An earlier draft would have
        rewritten dates. Semantic context is what prevents it."""
        new = 2354
        for text in ("Released 2 August 2026 under the Act",
                     "verified 2026-07-28",
                     "Regulation (EU) 2024/1689 applies",
                     "port 2000 is reserved"):
            self.assertEqual(
                cc._stale_values(text, new), set(),
                f"non-count number treated as a stale count in: {text!r}")

    def test_canonical_source_is_the_only_input(self):
        """The new value may never come from an argument."""
        self.assertIsInstance(cc.canonical_count(), int)
        self.assertGreater(cc.canonical_count(), 0)

    def test_repo_is_currently_in_sync(self):
        """--check must be clean at HEAD, or the cascade was done by hand.

        NOT SUFFICIENT ON ITS OWN, and the reason is recorded because this
        test passed green for three days while the landing page published a
        count 258 short. It asks the tool whether the tool found drift, so
        it inherits every blindness the tool has. The independent at-rest
        check is TestEveryPublishedSurfaceCarriesTheCanonicalCount below.
        """
        self.assertEqual(
            cc.main(["--check"]), 0,
            "manifest surfaces drift from the canonical count; run "
            "python3 scripts/cascade_count.py --apply")


class TestCountsAreSeenInsidePublishedMarkup(unittest.TestCase):
    """A count is published inside HTML and in non-English number formats.

    Both shapes below were live on getregula.com while `--check` reported
    "all manifest surfaces already carry the canonical value". Neither is
    hypothetical: they are the exact bytes from site/index.html:346 and
    site/locales/de.html:328.
    """

    def test_count_behind_inline_markup_is_detected(self):
        """`</strong> ` is not `\\s`, so a `{n}\\s+tests` template misses it."""
        text = '<strong style="color:var(--text);">2,354</strong> tests'
        self.assertEqual(
            cc._stale_values(text, 2612), {2354},
            "a count separated from its unit word by inline markup was not "
            "seen; this is how site/index.html published 2,354 for 3 days")
        self.assertEqual(
            cc._stale_values("# Expected: 2354 collected", 2622), {2354},
            "a reproduction command's stale expected collection count was "
            "hidden by a current count elsewhere in the same file")

    def test_dot_grouped_count_is_detected(self):
        """de-DE and pt-BR group thousands with a full stop."""
        for text, label in (
                ('<strong style="color:var(--text);">2.349</strong> Tests',
                 "de"),
                ('<strong style="color:var(--text);">2.349</strong> testes',
                 "pt-br")):
            self.assertEqual(
                cc._stale_values(text, 2612), {2349},
                f"dot-grouped count invisible to the scanner ({label})")

    def test_dot_grouped_count_keeps_its_separator_when_rewritten(self):
        """Detecting it is half the job. Writing `2,612` into German copy
        would fix the number and break the language."""
        text = '<strong>2.349</strong> Tests'
        out = text
        for old in cc._stale_values(text, 2612):
            for rx in cc._count_regexes(old):
                out = rx.sub(lambda m: cc._swap(m.group(0), old, 2612), out)
        self.assertIn("2.612", out, f"separator style not preserved: {out!r}")
        self.assertNotIn("2,612", out, f"English separator written: {out!r}")

    def test_markup_tolerance_does_not_reach_across_a_sentence(self):
        """THE CONTROL. Tolerating markup must not become tolerating text.
        If it did, any number in the same paragraph as the word `tests`
        would become a rewrite candidate, which is the heuristic this
        module's header records as tried and abandoned twice."""
        text = "We shipped 2,354 features in 2026. The suite has 2,612 tests."
        self.assertEqual(
            cc._stale_values(text, 2612), set(),
            "an unrelated number in the same sentence became a candidate")

    def test_space_entities_and_comments_are_markup_too(self):
        """`&nbsp;` is a separator by the same reasoning that made
        `</strong> ` one, and it appears 64 times in the published site.

        A guard that saw tags but not entities would repeat this
        repository's documented entity-blindness failure, where a check for
        the literal em dash let seven `&mdash;` entities render live.
        """
        for text, label in (
                ('<strong>2,354</strong>&nbsp;tests', "named entity"),
                ('2,354&#160;tests', "numeric entity"),
                ('2,354&#xA0;tests', "hex entity"),
                ('2,354<!-- build stamp -->tests', "HTML comment")):
            self.assertEqual(
                cc._stale_values(text, 2622), {2354},
                f"a count separated by {label} was not seen")

    def test_the_gap_never_crosses_a_block_boundary(self):
        """THE CONTROL for the widening. A number in one block and a unit
        word in the next are not one claim, and treating them as one puts
        years back in scope: `<h2>Roadmap 2026</h2>\\n<p>tests ...` nominated
        2026 under the first version of GAP.
        """
        for text, label in (
                ('<h2>Roadmap 2026</h2>\n<p>tests were rewritten</p>',
                 "year across h2/p"),
                ('<tr><td>2,468</td><td>Tests updated</td></tr>',
                 "adjacent table cells"),
                ('<ul><li>2,595</li><li>tests</li></ul>',
                 "adjacent list items"),
                ('<em>2026</em>\n\ntests', "paragraph break")):
            self.assertEqual(
                cc._stale_values(text, 2622), set(),
                f"the gap crossed a block boundary ({label}), so an "
                f"unrelated number became a rewrite candidate")

    def test_swap_rewrites_exactly_one_occurrence(self):
        """Measurement rule 4d, reopened and closed again.

        Once GAP pulls complete tags into the match, the matched fragment
        carries attribute values. Three chained unbounded `str.replace`
        calls rewrote digits inside an href and an id, which is the uv.lock
        near-miss class in a different file.
        """
        frag = ('<strong>2,354</strong>'
                '<a href="/c#build-2354" id="n2354"> tests</a>')
        out = cc._swap(frag, 2354, 2622)
        self.assertTrue(
            out.startswith('<strong>2,622</strong>'),
            f"the published number was not rewritten: {out!r}")
        self.assertIn('href="/c#build-2354"', out,
                      f"an href was rewritten: {out!r}")
        self.assertIn('id="n2354"', out, f"an id was rewritten: {out!r}")

    def test_swap_still_handles_the_badge_where_the_number_is_not_first(self):
        """The other half of the one-substitution rule: the badge template
        does not put the count first, so a `startswith` shortcut alone would
        silently stop maintaining the README badge."""
        self.assertEqual(
            cc._swap("tests-2354%20passing", 2354, 2622),
            "tests-2622%20passing")

    def test_years_behind_markup_are_still_not_rewritten(self):
        """The other control: markup tolerance must not resurrect the year
        class that COUNT_TEMPLATES exists to prevent."""
        for text in ('<strong>2026</strong> was the year',
                     '<em>2024</em>/1689 applies',
                     '<span>2026</span>-07-28'):
            self.assertEqual(
                cc._stale_values(text, 2612), set(),
                f"non-count number became a candidate in: {text!r}")


class TestEveryPublishedSurfaceCarriesTheCanonicalCount(unittest.TestCase):
    """At rest, on the real repository, INDEPENDENTLY of the tool AND
    INDEPENDENTLY of the manifest.

    Two separate failures made this shape necessary, both measured
    2026-07-31:

    1. Deliberately does not import COUNT_TEMPLATES. A test that reuses the
       tool's own matcher passes for exactly the reason the tool is wrong.
       `test_repo_is_currently_in_sync` above did precisely that and stayed
       green through cascades to 2,595, 2,608 and 2,612 while three manifest
       surfaces carried 2,354 and 2.349.

    2. Deliberately does not iterate the manifest either. The manifest is a
       hand-maintained list, and measurement rule 4c says a completeness
       claim must come from enumeration. It did not: `docs/architecture.md`
       published "1,223 tests" against a canonical of 2,618 (short by
       1,395 at that instant) while absent from both the
       manifest and claim_auditor's VERIFY_FACTS_FILES, a gap
       claim_auditor.py:1109-1114 had recorded as known and parked. Covering
       only manifest entries would have left it wrong.

    The corpus is `git ls-files`, so untracked scratch is out of scope
    (rule 4b), and the exemptions below are named and justified rather than
    being a pattern that quietly swallows real surfaces.

    Plural unit words only. `1,059 test functions` in docs/TRUST.md is a
    different quantity and must not be flagged.
    """

    # Matched case-insensitively, and the badge form is included. An
    # adversarial review on 2026-07-31 showed the first version, a hand-listed
    # set of case variants matched case-sensitively with a `\s*` separator,
    # could not see the README/llms-full.txt badge (`tests-2622%20passing`),
    # `TESTS`, `Testes`, or the "automated tests" phrasing claim_auditor
    # supports. For the badge that left coverage resting on exactly the two
    # things this class exists not to trust: the tool and the manifest.
    # `collected` is listed bare as well as inside `pytest-collected`.
    # MEASURED 2026-08-06: without it, `tests-2683%20collected` on README.md:10
    # matched nothing here while `tests-2683%20passing` and `2683 tests` both
    # matched, so the matcher was live and blind at the same time. Alternation
    # is positional, so the longer `pytest-collected` still wins where it
    # applies and no existing match changes meaning.
    UNIT = (r"(?:tests|testes|pytest-collected|collected|passing"
            r"|automated\s+tests)")
    SEP = r"(?:\s|%20|&nbsp;|&\#160;|<!--.*?-->|</?[a-zA-Z][^>]*>)*"

    # Historical and verbatim records. A changelog entry, a ledger row and a
    # rules file citing a past incident MUST keep the number that was true
    # when written; rewriting them would falsify the record. Everything else
    # tracked is treated as a live surface.
    EXEMPT_PREFIXES = (
        "docs/improvement/",     # ledger, session logs, review packs
        "docs/venture/REGULA_VENTURE_EVIDENCE_DOSSIER_2026-08-04.md",  # dated measured record
        "benchmarks/results/",   # dated scan artefacts
        ".claude/rules/",        # rules quoting past wrong numbers verbatim
        "CHANGELOG.md",          # per-release record of what was true then
        "tests/",                # test fixtures and this file's own examples
        "scripts/",              # docstrings citing the incidents by number
    )

    @staticmethod
    def _centrally_classified_records():
        """Exact dated records, from N70's central registry, not a local list.

        A prefix tuple and a hash-pinned registry are two notions of "this is
        an immutable dated record", and two lists drift. N56 is the precedent:
        claim_auditor kept its own copy of the gap regex and now IMPORTS
        cascade_count.GAP for exactly this reason.

        The registry is the stronger of the two by construction: it pins an
        exact path, a capture date that must appear in that path, the evidence
        commit and the blob's SHA-256, so a rename, an edit or a fabricated
        entry fails closed. A file still cannot classify itself.
        """
        policy = json.loads(
            (cc.REPO / "data/count_record_classes.json").read_text(
                encoding="utf-8"))
        return {r["path"] for r in policy.get("records", [])}

    def _tracked_surfaces(self):
        classified = self._centrally_classified_records()
        out = subprocess.run(
            ["git", "ls-files", "-z"], cwd=str(cc.REPO),
            capture_output=True, text=True, check=True).stdout
        for rel in out.split("\0"):
            if not rel or rel.startswith(self.EXEMPT_PREFIXES):
                continue
            if rel in classified:
                continue
            if rel.endswith((".md", ".html", ".txt")):
                yield rel

    def test_no_tracked_surface_publishes_a_stale_count(self):
        canonical = cc.canonical_count()
        wrong = []
        for rel in self._tracked_surfaces():
            path = cc.REPO / rel
            flat = path.read_text(encoding="utf-8", errors="replace")
            for m in re.finditer(
                    rf"(\d{{1,3}}[.,]\d{{3}}|\d{{4}})"
                    rf"{self.SEP}{self.UNIT}\b", flat, re.IGNORECASE):
                value = int(m.group(1).replace(",", "").replace(".", ""))
                if value != canonical:
                    wrong.append(f"{rel}: publishes {m.group(1)}")
        self.assertEqual(
            wrong, [],
            f"canonical is {canonical:,} but these tracked surfaces "
            f"disagree: {wrong}. Add the file to the manifest and re-run "
            f"`python3 scripts/cascade_count.py --apply`, or correct it by "
            f"hand if the shape is not one the cascade tool may touch.")

    # ANY shields.io badge carrying a count-shaped number next to a count
    # unit word, whatever the word and whatever the separator. Deliberately
    # independent of both COUNT_TEMPLATES and UNIT: those two are lists
    # someone has to remember to extend, and this check exists precisely for
    # the case where nobody did.
    BADGE_COUNT = re.compile(
        r"img\.shields\.io/badge/[^)\"'\s]*?"
        r"(?<![\w,.])(\d{1,3}[.,]\d{3}|\d{4})(?![\w,.])"
        r"(?:%20|[-_])"
        r"(tests|testes|pytest-collected|collected|passing)",
        re.IGNORECASE)

    def test_no_badge_publishes_a_stale_count(self):
        """A badge is a published claim and its unit word is not fixed.

        MEASURED 2026-08-06: README.md:10 published `tests-2683%20collected`
        while site/llms-full.txt:16 published `tests-2716%20passing`. One
        quantity, two unit words, and only the second was covered by anything.
        Accepting any unit word is the point: a third spelling fails here
        rather than publishing silently, and the failure message says to add
        the template rather than to widen this check.
        """
        canonical = cc.canonical_count()
        wrong = []
        for rel in self._tracked_surfaces():
            flat = (cc.REPO / rel).read_text(
                encoding="utf-8", errors="replace")
            for m in self.BADGE_COUNT.finditer(flat):
                value = int(m.group(1).replace(",", "").replace(".", ""))
                if value != canonical:
                    wrong.append(
                        f"{rel}: badge publishes {m.group(1)} {m.group(2)}")
        self.assertEqual(
            wrong, [],
            f"canonical is {canonical:,} but these badges disagree: {wrong}. "
            f"If the cascade tool did not fix it, its badge form is missing "
            f"from cascade_count.COUNT_TEMPLATES; add the form there rather "
            f"than editing the badge by hand.")

    def test_the_badge_scan_reaches_a_real_badge(self):
        """POSITIVE PROOF (measurement rule 4).

        A badge check that matches nothing passes for the wrong reason, and
        this repository has shipped exactly that failure before.
        """
        seen = [rel for rel in self._tracked_surfaces()
                if self.BADGE_COUNT.search(
                    (cc.REPO / rel).read_text(
                        encoding="utf-8", errors="replace"))]
        self.assertTrue(
            seen, "the badge matcher found no count badge anywhere, so the "
                  "check above passed by scanning nothing")
        for required in ("README.md", "site/llms-full.txt"):
            self.assertIn(
                required, seen,
                f"{required} carries a count badge that the matcher missed")

    def test_non_count_badges_are_not_read_as_counts(self):
        """THE CONTROL. Breadth must not become a heuristic.

        These are the real non-count badges in this repository. The citations
        badge is the sharp one: it carries `arXiv.2211.02701`, which is
        digit-rich and must not be read as a test count.
        """
        for url in (
                "https://img.shields.io/badge/python-3.10+-blue.svg",
                "https://img.shields.io/badge/License-Apache_2.0-blue.svg",
                "https://img.shields.io/badge/license-Apache%202.0-green.svg",
                "https://img.shields.io/badge/accessibility%20target-"
                "WCAG%202.2%20AA-blue.svg",
                "https://img.shields.io/badge/docker-pull-green.svg"
                "?logo=docker&logoColor=white",
                "https://img.shields.io/badge/dynamic/json?label=citations"
                "&query=%24.citationCount&url=https%3A%2F%2Fapi."
                "semanticscholar.org%2Fgraph%2Fv1%2Fpaper%2FDOI%3A10.48550"
                "%2FarXiv.2211.02701%3Ffields%3DcitationCount"):
            self.assertEqual(
                self.BADGE_COUNT.findall(url), [],
                f"a non-count badge was read as a published count: {url}")

    def test_central_records_cannot_exempt_a_live_surface(self):
        """THE ANTI-SUPPRESSION CONTROL for honouring the registry here.

        Consulting a registry to skip files is one edit away from being a
        silencer, so the invariant is asserted at the point of use rather
        than trusted from the other instrument: no manifest published surface
        may ever appear in the dated-record set. `validate_record_policy`
        already refuses such an entry, and this fails in the file that would
        benefit from the loophole if that ever stops being true.
        """
        classified = self._centrally_classified_records()
        self.assertTrue(
            classified,
            "the dated-record registry read as empty, so the exemption path "
            "is untested and a future record would be skipped silently")
        live = set(cc.manifest_surfaces())
        self.assertEqual(
            sorted(classified & live), [],
            "a published surface is registered as an immutable dated record, "
            "which would let a live stale count be classified instead of "
            "corrected")

    def test_the_two_instruments_share_one_gap_definition(self):
        """cascade_count and claim_auditor must agree on what separates a
        count from its unit word.

        claim_auditor's comment beside unit_patterns["tests"] asserts the
        two "agree on what a test-count claim looks like". That assertion
        was already false once: cascade_count used `\\s+` and claim_auditor
        `(?:\\s*|%20)`, and BOTH were blind to `</strong> `. Asserting the
        identity here is what stops a repair to one from leaving the other
        behind.
        """
        import claim_auditor
        # Value equality detects DRIFT. It does NOT detect that the import
        # failed and the copied fallback is live, because while the two are
        # equal the assertion passes either way; an adversarial review
        # demonstrated exactly that by blocking the import via sys.meta_path.
        # _GAP_SOURCE is what makes the fallback observable.
        self.assertEqual(
            claim_auditor._GAP_SOURCE, "cascade_count",
            "claim_auditor fell back to its copied gap regex instead of "
            "importing cascade_count.GAP; the two can now drift, and an "
            "import error (including a syntax error in cascade_count) is "
            "being swallowed silently")
        self.assertEqual(
            claim_auditor._GAP, cc.GAP,
            "claim_auditor's gap regex has drifted from cascade_count.GAP")
        self.assertEqual(claim_auditor._dotted(2619), "2.619")

    def test_the_enumeration_actually_reaches_the_known_surfaces(self):
        """POSITIVE PROOF THE CORPUS IS NOT EMPTY (measurement rule 4).

        Without this, an exemption typo that excluded everything would make
        the test above pass by scanning nothing, which is the exact failure
        mode it exists to catch.
        """
        found = set(self._tracked_surfaces())
        for required in ("README.md", "site/index.html", "docs/TRUST.md",
                         "site/locales/de.html", "docs/architecture.md"):
            self.assertIn(
                required, found,
                f"{required} is not reached by the enumeration, so its "
                f"count is unchecked")


if __name__ == "__main__":
    unittest.main(verbosity=2)


class TestTheRunnerFunctionCountIsCascadedSeparately(unittest.TestCase):
    """The SECOND published quantity, added 2026-08-14.

    `docs/TRUST.md` publishes the custom runner's function count twice, three
    lines from the collected count. It was outside the cascade, so it drifted
    silently until `tests/test_published_count_manifest.py` was written to
    catch it, and then drifted twice more in one session, each time costing a
    full suite run to discover.

    The danger in fixing it is conflation: two quantities on the same line,
    written by one tool. These controls exist to prove they cannot cross.
    """

    LINE = ("| Test suite | `tests/` (2,808 unique tests, 2,808 "
            "pytest-collected; the legacy `tests/test_classification.py` "
            "runner executes 1,182 functions, 442 defined in-file) |")
    PROSE = "The runner currently discovers 1,182 functions, a count machine-checked by"

    def test_runner_templates_match_both_published_shapes(self):
        for text in (self.LINE, self.PROSE):
            self.assertTrue(
                any(rx.search(text)
                    for rx in cc._count_regexes(1182, cc.RUNNER_TEMPLATES)),
                f"no RUNNER_TEMPLATE matched: {text!r}")

    def test_runner_pass_never_nominates_the_collected_count(self):
        """2,808 must not be visible to the runner templates."""
        stale = cc._stale_values(self.LINE, 1182, cc.RUNNER_TEMPLATES)
        self.assertNotIn(2808, stale, stale)

    def test_collected_pass_never_nominates_the_runner_count(self):
        """1,182 must not be visible to the collected-count templates."""
        stale = cc._stale_values(self.LINE, 2808, cc.COUNT_TEMPLATES)
        self.assertNotIn(1182, stale, stale)

    def test_the_third_quantity_on_the_same_line_is_never_touched(self):
        """`442 defined in-file` is neither a collected count nor a runner count.

        The runner shapes are anchored on the verb for exactly this reason: a
        template keyed on the word "functions" alone would reach it.
        """
        for canonical, templates in ((1182, cc.RUNNER_TEMPLATES),
                                     (2808, cc.COUNT_TEMPLATES)):
            self.assertNotIn(442, cc._stale_values(self.LINE, canonical, templates))

    def test_a_stale_runner_count_is_nominated_and_rewritten(self):
        """Positive control: the pass must be able to fire, not just abstain."""
        stale_line = self.PROSE.replace("1,182", "1,175")
        nominated = cc._stale_values(stale_line, 1182, cc.RUNNER_TEMPLATES)
        self.assertIn(1175, nominated, nominated)
        out = stale_line
        for rx in cc._count_regexes(1175, cc.RUNNER_TEMPLATES):
            out = rx.sub(lambda m: cc._swap(m.group(0), 1175, 1182), out)
        self.assertIn("discovers 1,182 functions", out)
        self.assertNotIn("1,175", out)

    def test_canonical_runner_count_refuses_a_missing_field(self):
        """Fail closed rather than cascade a quantity with no canonical source."""
        original = cc.CANONICAL
        try:
            import tempfile
            with tempfile.TemporaryDirectory() as d:
                path = Path(d) / "site_facts.json"
                path.write_text(json.dumps({"counts": {"tests": {"total_collected": 1}}}))
                cc.CANONICAL = path
                with self.assertRaises(cc.RefusedError):
                    cc.canonical_runner_count()
        finally:
            cc.CANONICAL = original
