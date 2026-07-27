# regula-ignore
"""Tests for the multi-annotator agreement, dedup and temporal-split tools."""

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "benchmarks"))

import annotation_stats
import dedup_check
import temporal_split


class TestFleissKappa(unittest.TestCase):
    def test_worked_example(self):
        """Hand-computed: rows (3,0),(2,1),(1,2),(0,3) -> kappa = 1/3."""
        r1 = {"a": "tp", "b": "tp", "c": "tp", "d": "fp"}
        r2 = {"a": "tp", "b": "tp", "c": "fp", "d": "fp"}
        r3 = {"a": "tp", "b": "fp", "c": "fp", "d": "fp"}
        result = annotation_stats.fleiss_kappa([r1, r2, r3])
        self.assertEqual(result["kappa"], round(1 / 3, 4))
        self.assertEqual(result["n_items"], 4)
        self.assertEqual(result["n_raters"], 3)
        self.assertEqual(result["unanimous"], 2)

    def test_perfect_agreement_mixed_categories(self):
        r = {"a": "tp", "b": "fp", "c": "tp"}
        result = annotation_stats.fleiss_kappa([dict(r), dict(r), dict(r)])
        self.assertEqual(result["kappa"], 1.0)

    def test_zero_variance_is_undefined_not_one(self):
        r = {"a": "tp", "b": "tp"}
        result = annotation_stats.fleiss_kappa([dict(r), dict(r)])
        self.assertIsNone(result["kappa"])
        self.assertIn("undefined", result["note"])

    def test_no_common_items(self):
        result = annotation_stats.fleiss_kappa([{"a": "tp"}, {"b": "fp"}])
        self.assertEqual(result["n_items"], 0)
        self.assertIn("error", result)

    def test_interpret_bands(self):
        self.assertIn("publishable as-is", annotation_stats.interpret(0.75))
        self.assertIn("disclosure", annotation_stats.interpret(0.65))
        self.assertIn("publishable finding", annotation_stats.interpret(0.4))
        self.assertIn("undefined", annotation_stats.interpret(None))

    def test_loads_existing_rater_packet_format(self):
        """The loader must read the real rater1 packet shape."""
        path = Path(__file__).parent.parent / "benchmarks" / "rater1_blind_subset.json"
        labels = annotation_stats.load_rater(path)
        self.assertEqual(len(labels), 50)
        self.assertTrue(all(v in ("tp", "fp") for v in labels.values()))


class TestDedupCheck(unittest.TestCase):
    def test_exact_duplicate_detection(self):
        entries = [
            {"project": "p", "file": "a.py", "line": 1, "tier": "t",
             "description": "d", "indicators": []},
            {"project": "p", "file": "a.py", "line": 1, "tier": "t",
             "description": "d", "indicators": []},
            {"project": "p", "file": "a.py", "line": 2, "tier": "t",
             "description": "d", "indicators": []},
        ]
        result = dedup_check.analyse(entries)
        self.assertEqual(result["exact_duplicates"]["count"], 1)

    def test_cross_project_candidates(self):
        entries = [
            {"project": "p1", "file": "a.py", "line": 1, "tier": "t",
             "description": "same pattern", "indicators": ["x"]},
            {"project": "p2", "file": "b.py", "line": 9, "tier": "t",
             "description": "same pattern", "indicators": ["x"]},
        ]
        result = dedup_check.analyse(entries)
        self.assertEqual(result["cross_project_candidates"]["count"], 1)
        self.assertIn("human review",
                      result["cross_project_candidates"]["note"])


class TestTemporalSplit(unittest.TestCase):
    ENTRIES = [
        {"project": "old_repo", "file": "a.py", "line": 1},
        {"project": "old_repo", "file": "b.py", "line": 2},
        {"project": "new_repo", "file": "c.py", "line": 3},
    ]

    def test_split_by_cutoff(self):
        dates = {"old_repo": {"created_at": "2024-01-01"},
                 "new_repo": {"created_at": "2026-03-01"}}
        result = temporal_split.split(self.ENTRIES, dates, "2026-01-01")
        self.assertEqual(result["train"]["findings"], 2)
        self.assertEqual(result["test"]["findings"], 1)
        self.assertTrue(result["publishable"])

    def test_missing_dates_block_publication(self):
        dates = {"old_repo": {"created_at": "2024-01-01"}}
        result = temporal_split.split(self.ENTRIES, dates, "2026-01-01")
        self.assertFalse(result["publishable"])
        self.assertEqual(result["projects_missing_dates"], ["new_repo"])
        self.assertIn("NOT publishable", result["note"])


if __name__ == "__main__":
    unittest.main()
