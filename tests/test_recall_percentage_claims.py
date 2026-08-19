# regula-ignore
"""N177 - the recall gate could not see a recall figure written as a percentage.

`claim_auditor.check_recall_claims` enforced the artefact's own
`_publication_rule` (every published recall fraction must state its path and
its gate condition) against `FRACTION_RE` alone. Two things followed, and both
were live:

1. **Form.** A recall figure written as `100%` rather than `16/30` was
   invisible to the gate built to police recall figures. That is measurement
   rule 5 inside the instrument: the gate tests something narrower than the
   claim its passing result reads as.
2. **Corpus.** `RECALL_CHECKED_FILES` was eight hand-listed files, so the two
   surfaces that carried the defect were never opened. Measurement rule 4c:
   a completeness claim must come from enumeration.

The cost, measured 2026-08-18: `site/blog/blog-aicdi-governance-gaps.html`
published "100% / 100% on 13 hand-crafted fixtures" under a heading reading
"Honest baselines (measured, reproducible)", with an invitation to reproduce it
by a command that prints a different number, three weeks after the repository's
own `docs/benchmarks/PRECISION_RECALL_2026_04.md` flagged that figure "STALE AND
CONTRADICTED, do not cite". `site/llms-full.txt` carried the same figure in a
table and as an expected command output while withdrawing it in its citation
block 260 lines further down.

Every test below is paired: one proves the check fires, one proves it does not
fire on the thing next to it. A gate that flags everything is as useless as a
gate that flags nothing, and the first draft of the percentage arm swept every
precision figure that shared a paragraph with the word "recall".
"""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import claim_auditor as ca  # noqa: E402


class TestThePercentageFormIsSeen(unittest.TestCase):
    def test_bare_recall_percentage_fails(self):
        text = "Recall on the synthetic fixtures is 53%.\n"
        problems = ca.check_recall_percentages(text, "docs/EXAMPLE.md")
        self.assertTrue(
            problems,
            "a bare recall percentage passed. This is the exact string the CI "
            "benchmark step used to print (ledger N151).")

    def test_a_labelled_recall_percentage_passes(self):
        text = ("On the synthetic corpus the scanner path with no flags "
                "(default scan) recalls 33% of the high-risk fixtures.\n")
        self.assertEqual(
            ca.check_recall_percentages(text, "docs/EXAMPLE.md"), [],
            "a percentage naming both its path and its gate condition was "
            "rejected")

    def test_a_precision_percentage_is_not_swept(self):
        """Control. The first draft flagged every precision figure that
        shared a paragraph with the word 'recall'."""
        text = ("Precision on the synthetic fixtures is 100%. Recall is "
                "reported per condition in RECALL.json.\n")
        self.assertEqual(
            ca.check_recall_percentages(text, "docs/EXAMPLE.md"), [],
            "a figure bound to the word 'precision' was treated as a recall "
            "claim")

    def test_a_percentage_outside_the_synthetic_corpus_is_not_swept(self):
        """Control. The artefact only knows one corpus."""
        text = "Recall on the OSS corpus is not measured; coverage is 40%.\n"
        self.assertEqual(
            ca.check_recall_percentages(text, "docs/EXAMPLE.md"), [],
            "a percentage in a paragraph that names no synthetic corpus was "
            "treated as a synthetic-corpus recall claim")

    def test_an_unlabelled_pair_is_a_finding_in_its_own_right(self):
        """'precision and recall: 100% / 100%' says which is which for
        neither, and one half of that exact pair was wrong for three weeks."""
        text = ("Synthetic benchmark precision and recall: 100% / 100% on "
                "hand-crafted fixtures.\n")
        problems = ca.check_recall_percentages(text, "docs/EXAMPLE.md")
        self.assertTrue(problems, "an unlabelled precision/recall pair passed")
        self.assertIn("labelled as neither", problems[0][1])


class TestTableCellsAreReachable(unittest.TestCase):
    """The metric of a table cell is named in its column header, several
    words away. A prose-window rule cannot see it, and this is the shape the
    defect actually took on site/llms-full.txt."""

    TABLE = ("| Corpus | Tier | Precision | Recall |\n"
             "|---|---|---:|---:|\n"
             "| **Synthetic** | all | **100%** | **100%** |\n")

    def test_recall_column_cell_is_checked(self):
        problems = ca.check_recall_percentages(self.TABLE, "docs/EXAMPLE.md")
        self.assertTrue(problems, "a recall percentage in a table cell passed")
        self.assertIn("Recall", problems[0][1])

    def test_the_precision_column_of_the_same_row_is_not_flagged(self):
        """Control: exactly one of the two cells is a finding."""
        problems = ca.check_recall_percentages(self.TABLE, "docs/EXAMPLE.md")
        self.assertEqual(
            len(problems), 1,
            f"the precision cell of the same row was swept too: {problems}")

    def test_a_withdrawn_marker_in_the_row_is_accepted(self):
        table = ("| Corpus | Tier | Precision | Recall |\n"
                 "|---|---|---:|---:|\n"
                 "| **Synthetic** | all | **100%** | **100% [SUPERSEDED]** |\n")
        self.assertEqual(
            ca.check_recall_percentages(table, "docs/EXAMPLE.md"), [],
            "a row that marks its own figure superseded was rejected; "
            "deleting a corrected number destroys the record of the "
            "correction")

    def test_the_marker_is_a_label_and_not_a_general_bypass(self):
        """Control on the control: the marker must not exempt a row that
        merely mentions the word in passing elsewhere."""
        table = ("| Corpus | Tier | Precision | Recall |\n"
                 "|---|---|---:|---:|\n"
                 "| **Synthetic** | all | **100%** | **100%** |\n")
        self.assertTrue(ca.check_recall_percentages(table, "docs/EXAMPLE.md"))


class TestTheCorpusComesFromEnumeration(unittest.TestCase):
    def test_the_hand_list_is_a_floor_not_the_corpus(self):
        files = ca.recall_checked_files()
        self.assertGreater(
            len(files), len(ca.RECALL_CHECKED_FILES),
            "recall_checked_files() returned no more than the hand-maintained "
            "list, so the gate is back to the reach that missed the defect")
        for entry in ca.RECALL_CHECKED_FILES:
            self.assertIn(entry, files,
                          f"{entry} was dropped by enumeration; the hand list "
                          f"must only ever widen the corpus")

    def test_the_surfaces_that_carried_the_defect_are_now_in_scope(self):
        files = set(ca.recall_checked_files())
        for entry in ("site/blog/blog-aicdi-governance-gaps.html",
                      "docs/benchmarks/PRECISION_RECALL_2026_04.md"):
            self.assertIn(
                entry, files,
                f"{entry} published a superseded recall figure and is still "
                f"outside the gate's reach")

    def test_the_programme_record_stays_out_of_scope(self):
        """docs/improvement/ quotes superseded figures ON PURPOSE. Widening
        the corpus must not drag the record of past corrections into it."""
        offenders = [f for f in ca.recall_checked_files()
                     if f.startswith("docs/improvement/")]
        self.assertEqual(
            offenders, [],
            f"the programme record entered the checked corpus: {offenders}")

    def test_every_checked_file_is_tracked(self):
        """Measurement rule 4b: an untracked file is not a surface."""
        tracked = set(subprocess.run(
            ["git", "ls-files"], cwd=str(REPO_ROOT),
            capture_output=True, text=True, check=True).stdout.split())
        for entry in ca.recall_checked_files():
            if not (REPO_ROOT / entry).exists():
                continue
            self.assertIn(entry, tracked,
                          f"{entry} is checked as a published surface but is "
                          f"not tracked")


class TestTheLiveTreeIsClean(unittest.TestCase):
    def test_no_published_surface_carries_an_unlabelled_recall_percentage(self):
        offenders = []
        for rel_path in ca.recall_checked_files():
            fpath = REPO_ROOT / rel_path
            if not fpath.exists():
                continue
            text = fpath.read_text(encoding="utf-8", errors="replace")
            for line_num, problem in ca.check_recall_percentages(text, rel_path):
                offenders.append(f"{rel_path}:L{line_num} — {problem}")
        self.assertEqual(offenders, [], "\n  " + "\n  ".join(offenders))


if __name__ == "__main__":
    unittest.main()
