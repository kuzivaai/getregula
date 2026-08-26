# regula-ignore
"""Tests for the head-to-head FP-penalising scoring (CASTLE-adapted)."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "benchmarks" / "headtohead"))

import scoring


class TestScoreCase(unittest.TestCase):
    def test_clean_detection_earns_base_plus_bonus(self):
        case = {"id": "x", "expected_tier": "high_risk",
                "findings": ["high_risk"]}
        self.assertEqual(scoring.score_case(case), 5 + 4)

    def test_extraneous_findings_cost_a_point_each(self):
        case = {"id": "x", "expected_tier": "prohibited",
                "findings": ["prohibited", "limited_risk", "minimal_risk"]}
        self.assertEqual(scoring.score_case(case), 5 - 2 + 5)

    def test_true_negative(self):
        self.assertEqual(
            scoring.score_case({"id": "x", "expected_tier": None,
                                "findings": []}), 2)

    def test_false_alarms_on_clean_case(self):
        case = {"id": "x", "expected_tier": None,
                "findings": ["high_risk", "limited_risk"]}
        self.assertEqual(scoring.score_case(case), -2)

    def test_missed_with_wrong_tier_findings(self):
        case = {"id": "x", "expected_tier": "high_risk",
                "findings": ["minimal_risk"]}
        self.assertEqual(scoring.score_case(case), -1)

    def test_missed_with_no_findings_scores_zero(self):
        case = {"id": "x", "expected_tier": "high_risk", "findings": []}
        self.assertEqual(scoring.score_case(case), 0)


class TestScoreRun(unittest.TestCase):
    def test_aggregate_matches_self_test_example(self):
        cases = [
            {"id": "t1", "expected_tier": "high_risk",
             "findings": ["high_risk"]},
            {"id": "t2", "expected_tier": "prohibited",
             "findings": ["prohibited", "limited_risk", "minimal_risk"]},
            {"id": "t3", "expected_tier": None, "findings": []},
            {"id": "t4", "expected_tier": None,
             "findings": ["high_risk", "high_risk", "limited_risk"]},
            {"id": "t5", "expected_tier": "high_risk",
             "findings": ["minimal_risk"]},
        ]
        result = scoring.score_run(cases)
        self.assertEqual(result["score"], 15)
        self.assertEqual(result["positives"], 3)
        self.assertEqual(result["detected"], 2)
        self.assertEqual(result["clean_cases"], 2)
        self.assertEqual(result["clean_cases_with_false_alarms"], 1)


class TestAdapterGuards(unittest.TestCase):
    def test_competitor_adapters_refuse_to_guess(self):
        sys.path.insert(0, str(Path(__file__).parent.parent
                               / "benchmarks" / "headtohead"))
        import adapters
        for name in ("air-blackbox", "systima", "ark-forge"):
            with self.assertRaises(NotImplementedError):
                adapters.ADAPTERS[name](".")


if __name__ == "__main__":
    unittest.main()
