# regula-ignore
"""F24 - recall must be derivable from a committed artefact.

`claim_auditor` could derive precision from PRECISION.json and could not
derive a recall figure at all. Every published recall number therefore sat
outside the reach of the gate whose whole purpose is published numbers.
That is how an 80% figure computed on five fixtures reached a plan, and how
three different gate conditions came to be quoted as if they were one
measurement.

The repair has two halves and this file guards both:

1. `benchmarks/synthetic/RECALL.json` is produced by
   `scripts/build_recall_artefact.py` from an actual run, and is never
   hand-edited. `test_committed_artefact_matches_a_fresh_run` re-runs the
   measurement and fails on any disagreement.
2. `claim_auditor.check_recall_claims()` verifies published fractions
   against it AND requires each to name its path and gate condition,
   because on this corpus the same tier scores 10/30, 16/30 and 23/30
   depending only on which gates are satisfied.

The required regression pair (1.5c) is
`test_pair_compliant_fraction_passes` / `test_pair_bare_fraction_fails`.
"""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import claim_auditor as ca  # noqa: E402

ARTEFACT = REPO_ROOT / "benchmarks/synthetic/RECALL.json"


def _artefact() -> dict:
    return json.loads(ARTEFACT.read_text(encoding="utf-8"))


class TestF24RegressionPair(unittest.TestCase):
    """The pair the 1.5c directive requires."""

    def test_pair_compliant_fraction_passes(self):
        text = (
            "On the synthetic corpus the scanner path with no flags "
            "(default scan) recalls 10/30 high-risk fixtures.\n")
        problems = ca.check_recall_claims(text, "docs/EXAMPLE.md", _artefact())
        self.assertEqual(
            problems, [],
            f"a fraction that matches the artefact and names both its path "
            f"and its gate condition was rejected: {problems}")

        # Control. This assertion is not decoration: the first version of
        # this test passed because RECALL_CONTEXT did not match "recalls",
        # so the paragraph was never inspected and an empty problem list
        # meant nothing. Strip the labels from the same sentence and it
        # must fail, which proves the paragraph is genuinely in scope.
        stripped = "The corpus recalls 10/30 high-risk fixtures.\n"
        self.assertTrue(
            ca.check_recall_claims(stripped, "docs/EXAMPLE.md", _artefact()),
            "the compliant case is passing because the paragraph is never "
            "inspected, not because it is compliant")

    def test_pair_bare_fraction_fails(self):
        text = "Regula achieves 10/30 recall on the synthetic corpus.\n"
        problems = ca.check_recall_claims(text, "docs/EXAMPLE.md", _artefact())
        self.assertTrue(
            problems,
            "a bare recall fraction passed. On this corpus the same tier "
            "scores 10/30, 16/30 and 23/30 depending on gates alone, so an "
            "unlabelled fraction is not a measurement.")

    def test_mismatched_fraction_fails(self):
        text = ("Scanner path, default scan: recall is 27/30 on the "
                "synthetic corpus.\n")
        problems = ca.check_recall_claims(text, "docs/EXAMPLE.md", _artefact())
        self.assertTrue(problems, "a fraction absent from the artefact passed")
        self.assertIn("not in RECALL.json", problems[0][1])


class TestLabellingIsEnforcedOnBothAxes(unittest.TestCase):
    def test_path_named_but_gate_condition_missing_fails(self):
        text = "The scanner recalls 10/30 high-risk fixtures.\n"
        problems = ca.check_recall_claims(text, "docs/EXAMPLE.md", _artefact())
        self.assertTrue(problems)
        self.assertIn("gate condition", problems[0][1])

    def test_gate_condition_named_but_path_missing_fails(self):
        text = "With a default scan, recall is 10/30 high-risk fixtures.\n"
        problems = ca.check_recall_claims(text, "docs/EXAMPLE.md", _artefact())
        self.assertTrue(problems)
        self.assertIn("path", problems[0][1])

    def test_a_fraction_outside_a_recall_paragraph_is_not_inspected(self):
        """Control: the check must not sweep unrelated fractions."""
        text = "Article 5 covers 3/30 of the categories in this table.\n"
        self.assertEqual(
            ca.check_recall_claims(text, "docs/EXAMPLE.md", _artefact()), [],
            "a fraction in a paragraph that never mentions recall was "
            "treated as a recall claim")


class TestWithdrawnLabelIsNotABypass(unittest.TestCase):
    def test_withdrawn_figure_may_be_recorded(self):
        text = ("The 14/30 domain-declared figure is NOT REPRODUCIBLE from "
                "any committed artefact and is withdrawn.\n")
        self.assertEqual(
            ca.check_recall_claims(text, "docs/EXAMPLE.md", _artefact()), [],
            "a properly labelled withdrawn figure was rejected; deleting a "
            "corrected number destroys the record of the correction")

    def test_the_same_figure_without_the_label_still_fails(self):
        text = "The domain-declared scanner recall figure is 14/30.\n"
        self.assertTrue(
            ca.check_recall_claims(text, "docs/EXAMPLE.md", _artefact()),
            "the withdrawal marker is acting as a general bypass")


class TestTheArtefactIsProducedNotWritten(unittest.TestCase):
    def test_committed_artefact_matches_a_fresh_run(self):
        """The strong guarantee: the file cannot be edited by hand."""
        proc = subprocess.run(
            [sys.executable, "scripts/build_recall_artefact.py", "--check"],
            cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=1800)
        self.assertEqual(
            proc.returncode, 0,
            f"RECALL.json disagrees with a fresh run.\n"
            f"stdout: {proc.stdout}\nstderr: {proc.stderr}")

    def test_every_condition_states_path_gates_and_invocation(self):
        for cond_id, cond in _artefact()["conditions"].items():
            for field in ("path", "gates", "invocation", "note"):
                self.assertIn(field, cond, f"{cond_id} has no {field}")
                self.assertTrue(str(cond[field]).strip(),
                                f"{cond_id} has an empty {field}")

    def test_every_fraction_carries_its_missed_fixtures(self):
        """Named misses are what a trace starts from."""
        for cond_id, cond in _artefact()["conditions"].items():
            for tier, stats in cond["tiers"].items():
                expected_misses = stats["total"] - stats["hits"]
                self.assertEqual(
                    len(stats["missed"]), expected_misses,
                    f"{cond_id} {tier}: fraction says {expected_misses} "
                    f"misses, {len(stats['missed'])} are named")

    def test_the_artefact_declares_its_hit_definition(self):
        doc = _artefact()
        self.assertIn("_hit_definition", doc)
        self.assertIn("_publication_rule", doc)


class TestSuiteRecallPinIsArtefactBacked(unittest.TestCase):
    """F26 fallout: a test pinned recall at 1.0 while the measured figure
    was 16/30, and stayed red across six commits."""

    def test_classifier_high_risk_recall_matches_the_artefact(self):
        sys.path.insert(0, str(REPO_ROOT / "benchmarks" / "synthetic"))
        if "run" in sys.modules:
            del sys.modules["run"]
        import run as synthetic_run  # noqa: E402
        measured = synthetic_run.metrics_dict()["high_risk"]["recall"]
        stats = (_artefact()["conditions"]["classifier/domains-declared"]
                 ["tiers"]["high_risk"])
        self.assertAlmostEqual(
            measured, stats["hits"] / stats["total"], places=6,
            msg="the live classifier recall disagrees with RECALL.json; "
                "one of them is stale")


if __name__ == "__main__":
    unittest.main()
