# regula-ignore
"""South Africa's draft AI policy has three withdrawal dates, and only one withdrew it.

LEDGER N127 recorded that four records gave three different answers for when the
draft National AI Policy was withdrawn, two of them contradicting themselves
inside a single card and inside the sourced generator file. Researched at source
on 2026-08-17, the disagreement was not an error about one date. It was a missing
distinction between three separate events:

  26 April 2026  the Minister ANNOUNCED the withdrawal after an internal process
  5 June 2026    CABINET APPROVED the withdrawal at a post-Cabinet briefing
  12 June 2026   the notice was WITHDRAWN BY GAZETTE, which is the operative act

Every surface in the repository dated the withdrawal by when it was announced or
approved. **None recorded the gazetted act at all**, and for a tool whose subject
is regulatory obligation the date an instrument took effect is the one that
matters. A reader deciding whether the draft bound them on 1 June would have been
told it was already withdrawn.

WHAT THIS DOES NOT CLAIM. The gazette itself was not retrieved: gov.za was
unreachable from the machine this was researched on, so the operative wording is
taken from ITWeb of 15 June 2026 quoting the notice verbatim, and the tracker row
carries `state: secondary` to say so. The withdrawal gazette's own number is
deliberately not asserted anywhere, because it was not read. If someone opens the
gazette and the date differs, this test is what tells them which surfaces to move.

A CORRECTION THIS FILE EXISTS TO PREVENT REPEATING. N127 hypothesised that
`CLAUDE.md`'s "27 April 2026" was a conflation with Colorado's 27 April
enforcement stay, because every other 27 April in the repository is Colorado.
That was wrong. 27 April is when the South African press reported the
announcement, so it was a one-day error on a real event, and the Colorado theory
was pattern-matching. Recorded because a plausible diagnosis that survives
because nobody checked it is the failure mode this programme keeps paying for.
"""
import json
import re
import subprocess
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TRACKER = REPO / "content" / "regulations" / "sa-tracker.json"
SOURCE = REPO / "content" / "regulations" / "south-africa.py"

GAZETTED = "12 June 2026"
GAZETTED_SHORT = "12 Jun 2026"
GAZETTED_ISO = "2026-06-12"

# Forms that state an announcement or approval date AS the withdrawal date. Each
# was live on a tracked surface before 2026-08-17.
WITHDRAWAL_MISDATED = re.compile(
    r"[Ww]ithdrawn\s+(?:~\s*)?(?:on\s+)?(?:2[567]\s+Apr|5\s+Jun)", re.I)


def _tracked(*globs) -> list[Path]:
    out = subprocess.run(["git", "ls-files", "-z", *globs], cwd=REPO,
                         capture_output=True, text=True, check=True)
    return [REPO / p for p in out.stdout.split("\0") if p]


class TestTheOperativeActIsRecorded(unittest.TestCase):

    def test_the_tracker_records_the_gazetted_date_as_its_own_field(self):
        d = json.loads(TRACKER.read_text(encoding="utf-8"))
        self.assertEqual(GAZETTED_ISO, d.get("withdrawn_by_gazette"))
        self.assertEqual("2026-04-26", d.get("withdrawal_announced"))
        self.assertEqual("2026-06-05", d.get("withdrawal_approved_by_cabinet"))

    def test_the_gazetted_row_declares_its_evidence_is_secondary(self):
        """The gazette was not opened, so the row must not claim it was."""
        d = json.loads(TRACKER.read_text(encoding="utf-8"))
        rows = [r for r in d["rows"] if "gazetted" in r["label"].lower()]
        self.assertEqual(1, len(rows), f"expected one gazetted row, got {rows}")
        row = rows[0]
        self.assertEqual(
            "secondary", row["state"],
            "the operative wording is quoted by a news outlet, not read from the "
            "gazette. Marking it verified would overstate the provenance.")
        self.assertIn(GAZETTED, row["value"])

    def test_the_withdrawal_gazette_number_is_not_asserted(self):
        """54477 is the PUBLICATION gazette. The withdrawal gazette was not read.

        Guards against the obvious wrong repair: reusing the number of the gazette
        that published the draft as the number of the gazette that withdrew it.
        """
        d = json.loads(TRACKER.read_text(encoding="utf-8"))
        rows = [r for r in d["rows"] if "gazetted" in r["label"].lower()]
        self.assertNotIn(
            "54477", rows[0]["value"].split("Government Gazette Number 54477")[-1]
            if "Government Gazette Number 54477" in rows[0]["value"] else "",
            "a gazette number was attached to the withdrawal that nobody read")


class TestNoSurfaceMisdatesTheWithdrawal(unittest.TestCase):

    def test_no_tracked_surface_calls_an_announcement_the_withdrawal(self):
        offenders = []
        for path in _tracked("site/**/*.html", "site/*.html", "content/**/*.py",
                             "content/**/*.json", "CLAUDE.md", "README.md"):
            if "docs/improvement" in str(path):
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for m in WITHDRAWAL_MISDATED.finditer(text):
                line = text[:m.start()].count("\n") + 1
                offenders.append(f"{path.relative_to(REPO)}:{line}: {m.group(0)}")
        self.assertEqual(
            [], offenders,
            "a surface states an announcement or Cabinet-approval date as the "
            f"date the draft was withdrawn: {offenders}")

    def test_the_generated_page_carries_all_three_events(self):
        page = (REPO / "site" / "regions" / "south-africa-ai-policy.html")
        text = page.read_text(encoding="utf-8")
        for needle in ("26 April 2026", "5 June 2026", GAZETTED):
            self.assertIn(needle, text, f"{needle} absent from the region page")

    def test_both_locale_cards_name_the_gazetted_date(self):
        for rel in ("site/locales/de.html", "site/locales/pt-br.html"):
            text = (REPO / rel).read_text(encoding="utf-8")
            card = text[text.index("South Africa draft AI policy"):][:400]
            self.assertIn(GAZETTED_SHORT, card, f"{rel} card does not name the "
                                                "gazetted withdrawal date")


class TestTheFallbackAgreesWithTheJson(unittest.TestCase):
    """The docstring in south-africa.py requires these be kept in sync.

    Nothing enforced it and they had drifted: the JSON recorded Cabinet approval
    as 25 March 2026 combined with the Special Sitting of 1 April, and the static
    no-JS fallback said 2 April, which is when the post-Cabinet briefing
    announced it. A reader with JavaScript disabled got a different date from a
    reader with it enabled.
    """

    def _static(self) -> str:
        return SOURCE.read_text(encoding="utf-8")

    def _json_row(self, label_fragment: str) -> str:
        d = json.loads(TRACKER.read_text(encoding="utf-8"))
        for r in d["rows"]:
            if label_fragment.lower() in r["label"].lower():
                return r["value"]
        raise AssertionError(f"no tracker row matching {label_fragment!r}")

    def test_cabinet_approval_dates_agree(self):
        static = self._static()
        row = self._json_row("Cabinet approval")
        for needle in ("25 March 2026", "1 April 2026"):
            self.assertIn(needle, row, f"{needle} missing from the tracker JSON")
            self.assertIn(needle, static,
                          f"{needle} missing from the static no-JS fallback, so "
                          "the two disagree again")

    def test_the_static_fallback_does_not_date_cabinet_approval_to_the_briefing(self):
        self.assertNotIn(
            "2 April 2026 — draft approved", self._static(),
            "the fallback dates Cabinet approval to the briefing that announced "
            "it, which is the class of error this whole module is about")


class TestTheChecksCanFail(unittest.TestCase):
    """Controls. Each guard above is only worth having if it can fail."""

    def test_the_misdating_pattern_fires_on_every_form_that_was_live(self):
        for planted in ("withdrawn 26 Apr 2026",
                        "Withdrawn ~26 Apr 2026",
                        "withdrawn on 27 April 2026",
                        "Withdrawn 5 Jun 2026"):
            self.assertTrue(WITHDRAWAL_MISDATED.search(planted),
                            f"pattern missed {planted!r}")

    def test_the_misdating_pattern_does_not_fire_on_correct_copy(self):
        for legitimate in (
            "withdrawal announced 26 April 2026, gazetted 12 June 2026",
            "approved by Cabinet 5 June 2026",
            "Withdrawn by gazette 12 Jun 2026",
            "the comment window closed on 10 June 2026",
        ):
            self.assertIsNone(WITHDRAWAL_MISDATED.search(legitimate),
                              f"pattern wrongly fired on {legitimate!r}")


if __name__ == "__main__":
    unittest.main()
