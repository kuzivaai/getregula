#!/usr/bin/env python3
# regula-ignore
"""The cascade tool must be incapable of touching anything off-manifest.

The required control (owner-set): plant an out-of-manifest literal AND a
lockfile in a fixture tree, and prove both come through untouched. Without
that, the tool is a promise rather than a mechanism.

Stdlib only.
"""

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
        """A wide net is how a size field gets rewritten. Only 4-digit values
        within 20% of canonical count as stale."""
        new = 2354
        text = "tests 2353 passing and size 222353"
        stale = cc._stale_values(text, new)
        self.assertIn(2353, stale, "a real stale count was not detected")
        self.assertNotIn(222353, stale, "6-digit value treated as a count")

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
    UNIT = r"(?:tests|testes|pytest-collected|passing|automated\s+tests)"
    SEP = r"(?:\s|%20|&nbsp;|&\#160;|<!--.*?-->|</?[a-zA-Z][^>]*>)*"

    # Historical and verbatim records. A changelog entry, a ledger row and a
    # rules file citing a past incident MUST keep the number that was true
    # when written; rewriting them would falsify the record. Everything else
    # tracked is treated as a live surface.
    EXEMPT_PREFIXES = (
        "docs/improvement/",     # ledger, session logs, review packs
        "benchmarks/results/",   # dated scan artefacts
        ".claude/rules/",        # rules quoting past wrong numbers verbatim
        "CHANGELOG.md",          # per-release record of what was true then
        "tests/",                # test fixtures and this file's own examples
        "scripts/",              # docstrings citing the incidents by number
    )

    def _tracked_surfaces(self):
        out = subprocess.run(
            ["git", "ls-files", "-z"], cwd=str(cc.REPO),
            capture_output=True, text=True, check=True).stdout
        for rel in out.split("\0"):
            if not rel or rel.startswith(self.EXEMPT_PREFIXES):
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
