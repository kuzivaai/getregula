# regula-ignore
"""F22 - the auditor silently skipped any stale number below half canonical.

`claim_auditor.verify_facts()` compared published counts against canonical
ones from `site_facts`, then contained this:

    if found_val < int(actual_str) * 0.5:
        continue

MEASURED 2026-07-28: canonical test count 2,363, so the floor sat at
1,181.5. Any published figure below it was skipped without a word - a
stale "1,100 tests" badge, a "553 findings" drift, a halved pattern count.
The programme's own P0 control cleared that floor by a 2% margin, which is
to say the gate was one small edit away from being blind to its own test.

The floor existed for a real reason: a legitimately different quantity can
share a unit word ("14 GDPR patterns" against a canonical 419). Deleting it
outright trades silent misses for false positives. So it is replaced by an
EXPLICIT exemption list rather than a magnitude guess: every suppression is
named, reviewable data, and anything not named is flagged whatever its size.

The required regression pair (1.5c) is
`test_pair_planted_stale_1100_is_caught` /
`test_pair_legitimate_subcount_does_not_false_positive`.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import claim_auditor as ca  # noqa: E402


class TestF22RegressionPair(unittest.TestCase):
    """The pair the 1.5c directive requires."""

    def test_pair_planted_stale_1100_is_caught(self):
        """1,100 against canonical 2,363 sits under the old 0.5 floor."""
        self.assertLess(1100, 2363 * 0.5,
                        "fixture invalid: 1,100 must sit UNDER the old floor "
                        "for this test to prove the floor is gone")
        flagged, why = ca.stale_number_verdict(
            fact_name="tests", actual_val=2363, found_val=1100,
            rel_path="docs/EXAMPLE.md", matched_text="1,100 tests")
        self.assertTrue(
            flagged,
            f"a stale 1,100 against canonical 2,363 was not flagged ({why}). "
            f"This is F22: the 0.5 magnitude floor is still swallowing it.")

    def test_pair_legitimate_subcount_does_not_false_positive(self):
        """A genuinely different quantity, named in the exemption list."""
        exempt = dict(ca.STALE_CHECK_EXEMPTIONS)
        exempt[("docs/EXAMPLE.md", "tests")] = {
            "phrases": ["14 tests"],
            "why": "fixture: a per-module count, not the suite total",
        }
        flagged, why = ca.stale_number_verdict(
            fact_name="tests", actual_val=2363, found_val=14,
            rel_path="docs/EXAMPLE.md", matched_text="14 tests",
            exemptions=exempt)
        self.assertFalse(
            flagged,
            f"an explicitly exempted sub-count was flagged ({why}). The "
            f"exemption list is what replaces the magnitude floor; if it "
            f"does not suppress, the replacement has failed.")


class TestTheFloorIsGone(unittest.TestCase):
    """Magnitude must no longer decide anything."""

    def test_a_tiny_unexempted_number_is_still_caught(self):
        flagged, _ = ca.stale_number_verdict(
            fact_name="tests", actual_val=2363, found_val=12,
            rel_path="docs/EXAMPLE.md", matched_text="12 tests")
        self.assertTrue(
            flagged,
            "12 is 0.5% of canonical. Under the old floor it vanished. "
            "Small is not the same as unrelated.")

    def test_a_near_miss_is_caught(self):
        flagged, _ = ca.stale_number_verdict(
            fact_name="tests", actual_val=2363, found_val=2353,
            rel_path="docs/EXAMPLE.md", matched_text="2,353 tests")
        self.assertTrue(flagged, "a one-cascade-old count must still flag")

    def test_the_canonical_number_itself_never_flags(self):
        flagged, why = ca.stale_number_verdict(
            fact_name="tests", actual_val=2363, found_val=2363,
            rel_path="docs/EXAMPLE.md", matched_text="2,363 tests")
        self.assertFalse(flagged, f"the correct number was flagged ({why})")

    def test_no_magnitude_ratio_constant_survives_in_the_module(self):
        """Control: the defect was a constant. Prove it is not still there.

        Comment lines are excluded on purpose - the module quotes the old
        line verbatim so the defect stays legible to the next reader.
        """
        src = (REPO_ROOT / "scripts" / "claim_auditor.py").read_text(
            encoding="utf-8")
        live = [ln for ln in src.splitlines()
                if not ln.lstrip().startswith("#")]
        offenders = [ln for ln in live if "* 0.5" in ln]
        self.assertEqual(
            offenders, [],
            f"a magnitude floor comparison is back in executable code: "
            f"{offenders}")


class TestExemptionsAreHonestData(unittest.TestCase):
    """An exemption list is only safer than a heuristic if it stays visible."""

    def test_every_exemption_states_a_reason(self):
        for key, entry in ca.STALE_CHECK_EXEMPTIONS.items():
            self.assertIn("why", entry, f"{key} has no stated reason")
            self.assertTrue(entry["why"].strip(), f"{key} has an empty reason")
            self.assertIn("phrases", entry, f"{key} lists no phrases")
            self.assertTrue(entry["phrases"], f"{key} has no phrases")

    def test_exemptions_are_phrase_scoped_not_file_scoped(self):
        """A file-wide exemption would re-create the silent skip."""
        exempt = {("docs/EXAMPLE.md", "tests"): {
            "phrases": ["14 tests"], "why": "fixture"}}
        flagged, _ = ca.stale_number_verdict(
            fact_name="tests", actual_val=2363, found_val=99,
            rel_path="docs/EXAMPLE.md", matched_text="99 tests",
            exemptions=exempt)
        self.assertTrue(
            flagged,
            "an unlisted phrase in an exempted file was suppressed; "
            "exemptions must be per-phrase, exactly like the quarantine")

    def test_an_exemption_does_not_leak_across_files(self):
        exempt = {("docs/EXAMPLE.md", "tests"): {
            "phrases": ["14 tests"], "why": "fixture"}}
        flagged, _ = ca.stale_number_verdict(
            fact_name="tests", actual_val=2363, found_val=14,
            rel_path="docs/OTHER.md", matched_text="14 tests",
            exemptions=exempt)
        self.assertTrue(flagged, "the exemption leaked to another file")


class TestEndToEndThroughVerifyFacts(unittest.TestCase):
    """The unit test proves the decision; this proves the wiring."""

    def test_planted_stale_count_fails_verify_facts(self):
        import tempfile
        with tempfile.TemporaryDirectory(dir=str(REPO_ROOT)) as td:
            tmp = Path(td)
            planted = tmp / "PLANTED.md"
            planted.write_text(
                "# Fixture\n\nThe suite carries 1,100 tests today.\n",
                encoding="utf-8")
            rel = str(planted.relative_to(REPO_ROOT))
            original = list(ca.VERIFY_FACTS_FILES)
            try:
                ca.VERIFY_FACTS_FILES.append(rel)
                rc = ca.verify_facts()
            finally:
                ca.VERIFY_FACTS_FILES[:] = original
        self.assertEqual(
            rc, 1,
            "verify_facts passed a file publishing 1,100 tests against a "
            "canonical 2,363. The unit-level fix is not wired into the gate.")

    def test_the_real_repo_still_passes(self):
        """Control: the repair must not red the gate on a clean tree."""
        self.assertEqual(
            ca.verify_facts(), 0,
            "verify_facts now fails on the real repo. Either a genuine "
            "stale number surfaced (fix it) or the replacement over-fires "
            "(narrow it) - do not lower the bar to make this pass.")


if __name__ == "__main__":
    unittest.main()
