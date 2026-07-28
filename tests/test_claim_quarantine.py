# regula-ignore
"""The claim quarantine is a ratchet: it may only shrink.

Quarantine holds claims that existed before the auditor could detect bare
percentages. It is NOT approval — the entries are unverified, and the
file says so in its own header. Its purpose is narrow: let the gate go
green for NEW claims immediately, so the fix delivers its benefit today,
while the backlog is burned down in batches.

The failure mode this guards is obvious and tempting: adding an entry
instead of sourcing a claim. That would turn a temporary backlog into a
permanent bypass, which is how the next auditor blind spot gets built.
So the count may fall and never rise, and the labelling must stay honest.
"""

import json
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import claim_auditor as ca  # noqa: E402

# The size of the backlog when quarantine was introduced (2026-07-28).
# This number may be LOWERED as items are burned down. It may never rise.
QUARANTINE_CEILING = 42


class TestQuarantineRatchet(unittest.TestCase):
    def setUp(self):
        self.doc = json.loads(
            ca.QUARANTINE_PATH.read_text(encoding="utf-8"))

    def test_count_may_only_decrease(self):
        actual = len(self.doc["entries"])
        self.assertLessEqual(
            actual, QUARANTINE_CEILING,
            f"quarantine grew from {QUARANTINE_CEILING} to {actual}. "
            f"Quarantine is a backlog being burned down, not a bypass for "
            f"new claims. Source the claim, correct it, or remove it — do "
            f"not add an entry. If a legitimate pre-existing claim was "
            f"genuinely missed, lower this ceiling in the same commit that "
            f"explains why.")

    def test_declared_count_matches_entries(self):
        self.assertEqual(
            self.doc["_count"], len(self.doc["entries"]),
            "the quarantine's self-declared _count disagrees with its "
            "entries; a stale header hides the true backlog size")

    def test_entries_key_on_file_and_claim_never_line_numbers(self):
        for e in self.doc["entries"]:
            self.assertEqual(
                set(e), {"file", "claim"},
                f"quarantine entry {e!r} has unexpected keys. Entries key on "
                f"file plus normalised claim text only. Line numbers rot on "
                f"every page edit and would have broken the moment the "
                f"coordinate fix landed.")
            self.assertTrue(e["claim"].strip(), "empty claim text")

    def test_status_labelling_stays_honest(self):
        status = self.doc["_status"]
        for word in ("UNVERIFIED", "QUARANTINED", "NOT ENDORSED"):
            self.assertIn(
                word, status,
                f"quarantine status must keep saying {word!r}; softening the "
                f"label is how an unverified backlog starts reading as an "
                f"approved one")

    def test_quarantined_files_still_exist(self):
        """A stale entry silently protects nothing and inflates the count."""
        missing = [e["file"] for e in self.doc["entries"]
                   if not (REPO / e["file"]).exists()]
        self.assertEqual(
            missing, [],
            f"quarantine references files that no longer exist: {missing}. "
            f"Remove them — they inflate the backlog without protecting "
            f"anything.")

    def test_quarantine_actually_suppresses_only_listed_claims(self):
        """Control: an unlisted claim in a quarantined file still fires."""
        listed = self.doc["entries"][0]
        self.assertTrue(
            ca.is_quarantined(listed["file"], listed["claim"]),
            "a listed entry is not being matched; the quarantine is not "
            "doing what the file says it does")
        self.assertFalse(
            ca.is_quarantined(listed["file"], "999 unrelated widgets"),
            "an unlisted claim in a quarantined file was suppressed; "
            "quarantine must be per-claim, not per-file")


if __name__ == "__main__":
    unittest.main()
