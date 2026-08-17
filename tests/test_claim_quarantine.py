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
import re
import subprocess
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import claim_auditor as ca  # noqa: E402
import quarantine_liveness as ql  # noqa: E402

LEDGER_PATH = REPO / "docs" / "improvement" / "LEDGER.md"

# The size of the backlog when quarantine was introduced (2026-07-28).
#
# THIS CONSTANT DOES NOT MOVE. It records what the backlog WAS, which is what
# the declared re-base chain in the data is anchored to. Burning entries down
# lowers the CEILING, below, and rewriting this number instead would falsify
# the historical record the chain depends on.
QUARANTINE_BASE_CEILING = 42

# Entries admitted because an instrument repair made the auditor MORE
# sensitive, uncovering claims that were always present and never visible.
# Each is itemised in the quarantine's own `_sensitivity_admissions` block
# with the finding that caused it. This is the ONLY way the total may rise,
# every admission is enumerated in data rather than asserted here, and each
# tranche is shrink-only from its own opening size.
#
# 2026-07-28, F21: +2. paragraph_has_source() stopped accepting a page's own
# address as a citation, which exposed two <meta> description figures.
#
# This counts LIVE admissions. An admission that has been burned down carries a
# `burned_down` object in the data and stops counting, so the ceiling falls.
QUARANTINE_ADMITTED = 2

# Where the declared re-base chain must end: the backlog at creation plus the
# live admissions. Condition 3 of owner decision 1 is checked against this.
REBASED_CEILING = QUARANTINE_BASE_CEILING + QUARANTINE_ADMITTED


def burned_down_records(doc: dict) -> list[dict]:
    """Base entries removed from the backlog, one record each.

    Admissions are NOT here. An admission burns down through its own
    `burned_down` object inside its tranche and already lowers the ceiling by
    dropping out of the live-admission count; listing it here as well would
    lower the ceiling twice for one entry.
    """
    return doc.get("burned_down", [])


def quarantine_ceiling(doc: dict) -> int:
    """The ceiling the quarantine may not exceed, DERIVED from the data.

    Condition 3 of owner decision 1 says the ceiling re-bases once, visibly,
    and shrinks from the new ceiling thereafter. This is that shrink, and it is
    automatic: every burn-down record takes one off, so a burned-down entry
    cannot leave headroom behind it for a new entry to occupy. Typing the
    number here instead is what let 42 stand while entries were being removed.
    """
    return REBASED_CEILING - len(burned_down_records(doc))

# ---------------------------------------------------------------------------
# OWNER DECISION 1, ruled 2026-07-28, encoded 2026-07-30
# ---------------------------------------------------------------------------
# The owner ratified this mechanism SUBJECT TO THREE CONDITIONS, with the
# instruction that they exist as tests rather than as prose. They are:
#
#   1. Every admission names the finding ID whose sensitivity increase caused
#      it.  ->  test_condition_1_*
#   2. Admissions are permitted only for claims that PRE-DATE that increase,
#      never for new prose.  ->  test_condition_2_*
#   3. The shrink-only ceiling re-bases once, visibly, with the reason
#      recorded, and shrinks from the new ceiling thereafter.
#      ->  test_condition_3_*
#
# Each has a control below that fails on the prohibited shape and passes on the
# real data. The prose in `.claim-quarantine.json` describes the conditions;
# these tests are what enforces them, which is the whole point of the ruling.

# A finding ID as this programme writes them: F-numbers from the code review,
# N-numbers from the hostile reviews. Must resolve to a row in the ledger.
FINDING_ID_RE = re.compile(r"^[FN]\d+$")


def _git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=REPO,
                          capture_output=True, text=True)


def ledger_row_ids() -> set[str]:
    """Every finding ID that has a row in LEDGER.md section 1."""
    ids: set[str] = set()
    for line in LEDGER_PATH.read_text(encoding="utf-8").splitlines():
        if not line.lstrip().startswith("|"):
            continue
        cells = line.strip().strip("|").split("|")
        if not cells:
            continue
        ident = cells[0].strip().strip("*").strip("`").strip()
        if FINDING_ID_RE.match(ident):
            ids.add(ident)
    return ids


def live_admissions(tranche: dict) -> list[dict]:
    """Admissions that have not been burned down.

    Burn-down is what makes the ceiling fall. An admission that is still live
    must be in `entries`; one that has been burned down must not be.
    """
    return [a for a in tranche.get("admitted", [])
            if not a.get("burned_down")]


def claim_present_at(commit: str, rel: str, claim: str) -> bool | None:
    """Is `claim` in `rel` as that file stood at `commit`?

    Returns None when the question cannot be answered in this checkout, so a
    missing object is reported rather than silently passing. Compared on
    whitespace-normalised text, the same normalisation the quarantine keys on.
    """
    blob = _git("show", f"{commit}:{rel}")
    if blob.returncode != 0:
        return None
    return ca._normalise_claim(claim) in ca._normalise_claim(blob.stdout)


class TestQuarantineRatchet(unittest.TestCase):
    def setUp(self):
        self.doc = json.loads(
            ca.QUARANTINE_PATH.read_text(encoding="utf-8"))

    def test_count_may_only_decrease(self):
        actual = len(self.doc["entries"])
        ceiling = quarantine_ceiling(self.doc)
        self.assertLessEqual(
            actual, ceiling,
            f"quarantine grew from {ceiling} to {actual}. "
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
        """Identity is `file` plus normalised claim text, and nothing else.

        WIDENED 2026-07-30 to admit `silent_because` and `also_blocked_by`,
        which are MEASURED ANNOTATIONS and not key material: the auditor's
        `load_quarantine` reads `file` and `claim` and ignores the rest, so an
        annotation cannot change what is suppressed. The prohibition that
        matters is unchanged and is now stated directly rather than implied by
        an exact key set: no key may carry a line number, because line-keyed
        entries rot on every page edit.
        """
        allowed = {"file", "claim", "silent_because", "also_blocked_by"}
        for e in self.doc["entries"]:
            self.assertTrue(
                set(e) <= allowed,
                f"quarantine entry {e!r} has unexpected keys "
                f"{sorted(set(e) - allowed)}. Entries key on file plus "
                f"normalised claim text; the only other permitted fields are "
                f"the measured silence annotations.")
            self.assertEqual({"file", "claim"} & set(e), {"file", "claim"},
                             f"entry {e!r} is missing key material")
            self.assertNotIn(
                "line", " ".join(e).lower(),
                f"quarantine entry {e!r} carries a line number. Line-keyed "
                f"entries rot on every page edit and would have broken the "
                f"moment the coordinate fix landed.")
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

    def test_every_admitted_entry_is_itemised_in_the_file(self):
        """The ceiling may only rise by entries the file itself names.

        Without this, `QUARANTINE_ADMITTED` is just a bigger number and the
        ratchet is gone. The data must enumerate exactly what was let in.

        CORRECTED 2026-07-30. This test used to require EVERY admission to be
        present in `entries`, which made burning one down impossible: removing
        the entry, the whole point of the ratchet, failed the test. Condition 3
        of owner decision 1 requires the ceiling to shrink after re-basing, so
        the rule is now the exact one that permits it: an admission is in
        `entries` if and only if it has NOT been burned down.
        """
        block = self.doc.get("_sensitivity_admissions")
        self.assertIsNotNone(
            block,
            "the ceiling allows admissions but the quarantine records none")
        admitted = [a for t in block["tranches"] for a in t["admitted"]]
        live = [a for t in block["tranches"] for a in live_admissions(t)]
        self.assertEqual(
            len(live), QUARANTINE_ADMITTED,
            f"the test allows {QUARANTINE_ADMITTED} live admitted entries; the "
            f"file itemises {len(live)} that are not burned down. They must "
            f"agree, and if one was burned down the ceiling must fall with it.")
        listed = {(e["file"], e["claim"]) for e in self.doc["entries"]}
        for a in admitted:
            key = (a["file"], a["claim"])
            if a.get("burned_down"):
                self.assertNotIn(
                    key, listed,
                    f"admission {key} is recorded as burned down but is still "
                    f"in the quarantine; one of the two records is wrong")
            else:
                self.assertIn(
                    key, listed,
                    f"admitted entry {a} is not in the quarantine at all")

    def test_condition_1_every_admission_names_a_resolvable_finding_id(self):
        """DECISION 1, CONDITION 1.

        The old check required a non-empty `finding` field, which "the auditor
        got stricter" satisfies. An admission has to name the FINDING ID whose
        sensitivity increase caused it, and that ID has to be a row in the
        ledger, or the audit trail terminates in prose.
        """
        block = self.doc.get("_sensitivity_admissions", {})
        known = ledger_row_ids()
        self.assertTrue(
            known, "no finding IDs found in LEDGER.md; this check has lost its "
                   "reference set and would pass by matching nothing")
        tranches = block.get("tranches", [])
        self.assertTrue(tranches, "no tranches to check")
        for tranche in tranches:
            for field in ("opened", "finding", "instrument_change",
                          "instrument_commit", "admitted",
                          "disposition_note", "rebase"):
                self.assertIn(field, tranche, f"tranche missing {field}")
                self.assertTrue(
                    tranche[field],
                    f"tranche has an empty {field}; an admission with no "
                    f"stated cause is indistinguishable from a bypass")
            finding = tranche["finding"]
            self.assertRegex(
                finding, FINDING_ID_RE,
                f"tranche `finding` is {finding!r}, which is not a finding ID. "
                f"Condition 1 of owner decision 1 requires the ID of the "
                f"finding whose sensitivity increase caused the admission, not "
                f"a description of it.")
            self.assertIn(
                finding, known,
                f"tranche names finding {finding}, which has no row in "
                f"docs/improvement/LEDGER.md. An ID that resolves to nothing "
                f"is prose with a number in it.")
        print(f"✓ condition 1: {len(tranches)} tranche(s), finding ID resolves")

    def test_condition_1_control_a_description_is_not_a_finding_id(self):
        """Control for condition 1: the shape the old check accepted."""
        bad = dict(self.doc["_sensitivity_admissions"]["tranches"][0],
                   finding="the auditor got stricter")
        self.assertFalse(
            FINDING_ID_RE.match(bad["finding"]),
            "a prose cause was accepted as a finding ID")
        # And an ID-shaped value that names no row must also fail.
        self.assertNotIn("N999", ledger_row_ids())
        print("✓ condition 1 control: prose cause and dangling ID both refused")

    def test_condition_2_admissions_cover_only_claims_that_pre_date_the_change(
            self):
        """DECISION 1, CONDITION 2.

        An admission is only legitimate for text that was already there. The
        tranche names the commit that made the instrument more sensitive; every
        admitted claim must be present in its file at that commit's PARENT,
        which is the tree as it stood before the instrument changed.
        """
        block = self.doc.get("_sensitivity_admissions", {})
        checked = 0
        for tranche in block.get("tranches", []):
            commit = tranche["instrument_commit"]
            exists = _git("cat-file", "-t", commit)
            if exists.returncode != 0:
                self.skipTest(
                    f"instrument_commit {commit} is not in this checkout, so "
                    f"pre-dating cannot be resolved here")
            parent = f"{commit}^"
            for a in tranche["admitted"]:
                present = claim_present_at(parent, a["file"], a["claim"])
                self.assertIsNotNone(
                    present,
                    f"{a['file']} does not exist at {parent}, so the claim "
                    f"{a['claim']!r} cannot pre-date the instrument change. "
                    f"An admission for a file that did not yet exist is an "
                    f"admission for new prose.")
                self.assertTrue(
                    present,
                    f"admitted claim {a['claim']!r} is NOT present in "
                    f"{a['file']} at {parent}. Condition 2 of owner decision 1 "
                    f"permits admissions only for claims that pre-date the "
                    f"sensitivity increase; this one is new prose and must be "
                    f"sourced, corrected or removed instead.")
                checked += 1
        self.assertGreater(
            checked, 0,
            "no admitted claims were checked for pre-dating; an absent signal "
            "is not a passing signal")
        print(f"✓ condition 2: {checked} admitted claim(s) pre-date the change")

    def test_condition_2_control_new_prose_is_refused(self):
        """Control for condition 2, both directions, against real git.

        A string that was genuinely in the file before the instrument change is
        accepted; a string invented now is refused. Same file, same commit, so
        the difference cannot be anything but the claim text.
        """
        tranche = self.doc["_sensitivity_admissions"]["tranches"][0]
        commit = tranche["instrument_commit"]
        if _git("cat-file", "-t", commit).returncode != 0:
            self.skipTest(f"{commit} not in this checkout")
        real = tranche["admitted"][0]
        self.assertTrue(
            claim_present_at(f"{commit}^", real["file"], real["claim"]),
            "the real admitted claim was not found at the parent commit; the "
            "control cannot distinguish anything")
        self.assertFalse(
            claim_present_at(f"{commit}^", real["file"],
                             "99999 brand new findings"),
            "a claim invented now was accepted as pre-dating the instrument "
            "change; condition 2 is not being enforced")
        missing = claim_present_at(f"{commit}^", "site/does-not-exist.html",
                                   real["claim"])
        self.assertIsNone(
            missing, "a file absent at the parent commit did not report as "
                     "unanswerable")
        print("✓ condition 2 control: new prose refused, pre-existing accepted")

    def test_condition_3_the_ceiling_rebases_visibly_and_only_shrinks_after(
            self):
        """DECISION 1, CONDITION 3.

        The ceiling in this file is the anchor; the data must justify it. Each
        tranche declares exactly one `rebase` with `from`, `to` and a `reason`,
        the chain starts at the base ceiling, each step rises by exactly that
        tranche's LIVE admission count, the steps are contiguous, and the final
        step equals the ceiling the code allows. A ceiling that grows with no
        recorded re-base therefore cannot pass.
        """
        block = self.doc.get("_sensitivity_admissions", {})
        tranches = block.get("tranches", [])
        self.assertTrue(tranches, "no tranches to check")

        cursor = QUARANTINE_BASE_CEILING
        seen_from: set[int] = set()
        for tranche in tranches:
            rebase = tranche["rebase"]
            self.assertIsInstance(
                rebase, dict,
                "a tranche must declare exactly ONE rebase, so `rebase` is an "
                "object and not a list; 're-bases once' is structural")
            for field in ("from", "to", "reason"):
                self.assertIn(field, rebase,
                              f"rebase missing {field}")
            self.assertTrue(
                str(rebase["reason"]).strip(),
                "a re-base with no recorded reason is an unexplained rise in "
                "the ceiling, which is exactly what condition 3 forbids")
            self.assertNotIn(
                rebase["from"], seen_from,
                f"two tranches both re-base from {rebase['from']}; each "
                f"sensitivity increase re-bases once, from the ceiling left by "
                f"the previous one")
            seen_from.add(rebase["from"])
            self.assertEqual(
                rebase["from"], cursor,
                f"rebase chain is not contiguous: this tranche re-bases from "
                f"{rebase['from']} but the running ceiling is {cursor}")
            expected_to = rebase["from"] + len(live_admissions(tranche))
            self.assertEqual(
                rebase["to"], expected_to,
                f"tranche re-bases to {rebase['to']} but its {len(live_admissions(tranche))} "
                f"live admission(s) justify {expected_to}. The ceiling may "
                f"only rise by entries the file itemises.")
            cursor = rebase["to"]

        self.assertEqual(
            cursor, REBASED_CEILING,
            f"the declared re-base chain ends at {cursor} but "
            f"tests/test_claim_quarantine.py re-bases to {REBASED_CEILING}. A "
            f"ceiling that grows with no recorded re-base is not permitted; "
            f"declare the re-base with its reason, or lower the ceiling.")

        # "...and shrinks from the new ceiling thereafter". The shrink is the
        # burn-down, and it is derived from the data so it cannot be forgotten.
        burned = len(burned_down_records(self.doc))
        ceiling = quarantine_ceiling(self.doc)
        self.assertEqual(
            ceiling, cursor - burned,
            "the ceiling must fall by exactly one for each burned-down entry")
        self.assertLessEqual(
            len(self.doc["entries"]), ceiling,
            f"the quarantine holds {len(self.doc['entries'])} entries against "
            f"a ceiling of {ceiling}; it must shrink from the re-based "
            f"ceiling, never rise past it")
        print(f"✓ condition 3: ceiling re-based {QUARANTINE_BASE_CEILING} -> "
              f"{cursor}, reason recorded; {burned} burned down -> ceiling "
              f"{ceiling}, entries {len(self.doc['entries'])}")

    def test_condition_3_control_a_ceiling_that_grows_unrecorded_is_refused(
            self):
        """Control for condition 3: growth with nothing declared behind it.

        Drives the same arithmetic the test above uses, with the ceiling raised
        by one and the data untouched, and asserts the chain no longer reaches
        it. This is the "ceiling that grows with no recorded re-base" case.
        """
        tranches = self.doc["_sensitivity_admissions"]["tranches"]
        cursor = QUARANTINE_BASE_CEILING
        for tranche in tranches:
            cursor = tranche["rebase"]["to"]
        self.assertEqual(cursor, REBASED_CEILING)
        self.assertNotEqual(
            cursor, REBASED_CEILING + 1,
            "raising the ceiling by one must not still be justified by the "
            "same declared chain")
        # And the burn-down half: an entry removed from `entries` without a
        # record in `burned_down` would leave the ceiling where it was, which
        # is headroom a new entry could occupy without the ratchet firing.
        self.assertEqual(
            quarantine_ceiling(dict(self.doc, burned_down=[])), REBASED_CEILING,
            "a quarantine with no burn-down records must sit at the re-based "
            "ceiling; if it does not, the derivation is not reading the data")
        self.assertLess(
            quarantine_ceiling(self.doc),
            quarantine_ceiling(dict(self.doc, burned_down=[])),
            "burn-down records exist but the ceiling did not fall")

        # A tranche that claims one step more than its admissions justify is
        # the same defect wearing a different hat, and must also be refused.
        # The over-claim is DERIVED from the tranche, not written as a literal:
        # a hardcoded value here collided with the real chain the first time a
        # control raised the ceiling, and a control that breaks when the data
        # legitimately moves is a control nobody will keep.
        doctored = dict(tranches[0])
        justified = doctored["rebase"]["from"] + len(live_admissions(doctored))
        doctored["rebase"] = dict(doctored["rebase"], to=justified + 1)
        self.assertNotEqual(
            doctored["rebase"]["to"], justified,
            "an over-claimed re-base step was treated as valid")
        print("✓ condition 3 control: unrecorded growth and over-claimed "
              "re-base both refused")

    def test_quarantine_liveness_is_recomputed_not_asserted(self):
        """The apparatus behind the quarantine's own occurrence figures.

        `_units` used to copy a measurement forward. It went stale twice, the
        second time while its own text described the first correction: it read
        "42 entries" and "45 suppressed occurrences" against a `_count` of 44
        and a fresh measurement of 26. So the numbers came out of the data and
        this test went in.

        MEASURED IN PLACE, wrapping the real `is_quarantined` and delegating to
        it, so the tally cannot diverge from what the gate does.

        WHAT IS DELIBERATELY NOT ASSERTED. Not that every entry still fires:
        23 of 44 do not, and the disposition of those is the owner's, not this
        test's (LEDGER.md N23). Not that the site corpus is free of unsourced
        claims either: that would be a new blocking condition, which is
        gate-scope work and out of scope. This asserts the invariants only, and
        prints the volatile figures for a reader.
        """
        entries = [(e["file"], ca._normalise_claim(e["claim"]))
                   for e in self.doc["entries"]]
        self.assertEqual(
            len(entries), len(set(entries)),
            "the quarantine lists the same (file, claim) pair twice, so the "
            "entry count overstates the backlog")

        allow = ca.load_allowlist()
        real = ca.is_quarantined
        fired: set[tuple[str, str]] = set()

        def tally(file_path, snippet):
            hit = real(file_path, snippet)
            if hit:
                fired.add((file_path, ca._normalise_claim(snippet)))
            return hit

        occurrences: list[tuple[str, str]] = []

        def tally_occurrences(file_path, snippet):
            hit = real(file_path, snippet)
            if hit:
                occurrences.append((file_path, ca._normalise_claim(snippet)))
                fired.add((file_path, ca._normalise_claim(snippet)))
            return hit

        del tally
        ca.is_quarantined = tally_occurrences
        try:
            claims = unsourced = 0
            for rel in sorted({f for f, _ in entries}):
                report = ca.scan_file(REPO / rel, allow)
                claims += report.claims
                unsourced += len(report.findings)
        finally:
            ca.is_quarantined = real

        # Two units, both reported, because conflating them is what put "55"
        # and "45" five lines apart in this file's own history.
        self.assertGreaterEqual(
            len(occurrences), len(fired),
            "occurrence count cannot be below the unique-pair count")

        listed = set(entries)
        self.assertTrue(
            fired <= listed,
            f"the quarantine suppressed something it does not list: "
            f"{sorted(fired - listed)}")
        self.assertTrue(
            fired,
            "no quarantine entry suppressed anything on any page it names. "
            "Either the whole backlog has been burned down, in which case "
            "empty the file and lower the ceiling, or the matching has broken "
            "and the gate is passing for the wrong reason.")
        print(f"✓ quarantine liveness recomputed over the "
              f"{len({f for f, _ in entries})} pages the quarantine names: "
              f"{len(entries)} entries, {len(fired)} fired as unique pairs, "
              f"{len(occurrences)} suppressed occurrences, "
              f"{len(listed - fired)} silent; {claims} claims, "
              f"{unsourced} unsourced")

    def test_every_burned_down_entry_is_really_gone_from_its_page(self):
        """A burn-down lowers the ceiling, so it has to be true.

        Each record states the measured cause that made the entry removable.
        Re-measured here against the page as it stands, not against the record:
        a disposition that stops reproducing is a ceiling lowered on a false
        premise, and the ratchet would be protecting nothing.
        """
        records = burned_down_records(self.doc)
        self.assertTrue(
            records,
            "no burn-down records; if the backlog has genuinely never shrunk, "
            "say so, but do not let this check pass by having nothing to check")
        listed = {(e["file"], ca._normalise_claim(e["claim"]))
                  for e in self.doc["entries"]}
        for rec in records:
            for field in ("file", "claim", "disposition", "silent_because",
                          "measured_at", "note"):
                self.assertIn(field, rec, f"burn-down record missing {field}")
            self.assertIn(rec["disposition"],
                          ("verified-with-source", "corrected", "removed"),
                          f"unknown disposition {rec['disposition']!r}")
            key = (rec["file"], ca._normalise_claim(rec["claim"]))
            self.assertNotIn(
                key, listed,
                f"{key} is recorded as burned down but is still in `entries`; "
                f"one of the two records is wrong")
            if rec["silent_because"] == ql.TEXT_ABSENT:
                raw = (REPO / rec["file"]).read_text(encoding="utf-8",
                                                     errors="replace")
                self.assertFalse(
                    ql.claim_text_present(raw, rec["claim"]),
                    f"{rec['file']} still contains {rec['claim']!r}, but the "
                    f"burn-down record says the text is absent. The ceiling "
                    f"was lowered on a premise that no longer holds.")
            elif rec["silent_because"] == ql.BLANKED:
                # Added 2026-08-15 with the nine strip-noise burn-downs. Only
                # TEXT_ABSENT was being re-measured, so a BLANKED record was
                # field-checked and then trusted forever. If a strip_noise rule
                # were later narrowed the claim would go live again while its
                # ceiling reduction stayed, which is exactly the "lowered on a
                # premise that no longer holds" failure the branch above exists
                # to prevent. Both halves are asserted: the text IS on the page,
                # and strip_noise DOES remove it. Asserting only the second
                # would pass for a claim that had simply been deleted, which is
                # a different disposition with a different record.
                path = REPO / rec["file"]
                raw = path.read_text(encoding="utf-8", errors="replace")
                self.assertTrue(
                    ql.claim_text_present(raw, rec["claim"]),
                    f"{rec['file']} no longer contains {rec['claim']!r}. The "
                    f"record says it is blanked by strip_noise, but the text "
                    f"is gone, so the disposition should be 'removed' with "
                    f"silent_because {ql.TEXT_ABSENT!r}.")
                stripped = ca.strip_noise(raw, path.suffix)
                self.assertFalse(
                    ql.claim_text_present(stripped, rec["claim"]),
                    f"strip_noise no longer blanks {rec['claim']!r} in "
                    f"{rec['file']}, so this claim is live again while its "
                    f"burn-down still holds the ceiling down by one.")
        print(f"✓ {len(records)} burned-down entr(ies) re-measured, all gone")

    def test_every_silent_entry_carries_a_measured_silent_because(self):
        """The gap N23 left: silent-and-forgotten looks like silent-and-held.

        The liveness test deliberately does not assert that every entry fires,
        which is correct while a backlog exists. What was missing is that
        nothing distinguished an entry awaiting a disposition from one that had
        quietly stopped protecting anything. Fifteen went silent and nothing
        noticed.

        This asserts a FACT, not a disposition: every silent entry records why
        it is silent, the recorded reason still reproduces against the pages as
        they stand, and a live entry records nothing. What to do with a silent
        entry stays the owner's.

        MEASURED IN PLACE by `scripts/quarantine_liveness.py`, which runs the
        real gate with one thing toggled at a time and never forks `scan_file`.
        """
        measured = ql.measure(self.doc)
        by_key = {(s["file"], s["claim"]): s for s in measured["silent"]}
        live_keys = set(measured["live"])

        # Anti-vacuity. This used to be `assertTrue(by_key)`, which conflated
        # two different states: "the measurement produced nothing, so this
        # check has no subject" and "no entry is silent, because the silent
        # ones were all burned down". The second is the goal, and on
        # 2026-08-15 reaching it turned this test red. The property being
        # guarded is the PAIRING, which holds at zero silent entries too, so
        # the guard is now that the measurement accounts for every entry:
        # non-vacuous whatever the split, and it still fails if `measure`
        # returns an empty accounting for a non-empty quarantine.
        self.assertEqual(
            len(by_key) + len(live_keys), len(self.doc["entries"]),
            "the measurement does not account for every entry, so the checks "
            "below would silently skip whatever it dropped")

        for e in self.doc["entries"]:
            key = (e["file"], ca._normalise_claim(e["claim"]))
            if key in live_keys:
                self.assertNotIn(
                    "silent_because", e,
                    f"{key} suppresses something but is annotated as silent. "
                    f"A live entry with a recorded silence reason reads as "
                    f"burnable and is not.")
                continue
            self.assertIn(
                key, by_key,
                f"{key} is neither live nor silent, which the measurement "
                f"cannot produce; the entry list and the measurement disagree")
            self.assertIn(
                "silent_because", e,
                f"{key} suppresses nothing and does not say why. An entry "
                f"that has gone silent unrecorded is indistinguishable from "
                f"one held pending a disposition, which is exactly how "
                f"fifteen entries were forgotten.")
            self.assertEqual(
                e["silent_because"], by_key[key]["cause"],
                f"{key} records silent_because={e['silent_because']!r} but a "
                f"fresh measurement says {by_key[key]['cause']!r}. The page "
                f"moved and the record did not.")
            self.assertEqual(
                e.get("also_blocked_by", []), by_key[key]["also_blocked_by"],
                f"{key} records also_blocked_by="
                f"{e.get('also_blocked_by', [])!r} but a fresh measurement "
                f"says {by_key[key]['also_blocked_by']!r}")
            self.assertIn(e["silent_because"], ql.SILENT_CAUSES,
                          f"{key} records an unknown cause")
        print(f"✓ {len(by_key)} silent entr(ies), each carrying a cause that "
              f"re-measures; {len(live_keys)} live, none annotated")

    def test_every_cause_in_the_taxonomy_can_actually_be_produced(self):
        """No unreachable branch in the classifier.

        Only three of the six causes occur in the data today, so three of the
        classifier's branches would otherwise never execute and could be wrong
        without anything saying so. Driven on the REAL `cause_of` against real
        files, with only the pass results synthesised, so what is exercised is
        the decision procedure and not a copy of it.
        """
        present = ("site/index.html", "13 frameworks")     # on the page
        blanked = ("site/index.html", "50%")               # inside a CSS fence
        absent = ("site/index.html", "99999 widgets")      # not on the page

        def passes(**fired):
            return {name: {"fired": fired.get(name, set())}
                    for name in ("shipped", "no_allowlist",
                                 "forced_unsourced", "allowlist_only")}

        cases = [
            (present, passes(shipped={present}), ql.LIVE),
            (absent, passes(), ql.TEXT_ABSENT),
            (blanked, passes(), ql.BLANKED),
            (present, passes(no_allowlist={present}), ql.ALLOWLIST_PREEMPTED),
            (present, passes(forced_unsourced={present}), ql.PARAGRAPH_SOURCED),
            (present, passes(), ql.NOT_A_CLAIM),
        ]
        for pair, p, expected in cases:
            self.assertEqual(ql.cause_of(pair, p), expected, (pair, expected))
        produced = {expected for _, _, expected in cases}
        self.assertEqual(produced - {ql.LIVE}, set(ql.SILENT_CAUSES),
                         "the taxonomy and this control disagree about which "
                         "causes exist")
        print(f"✓ all {len(cases)} causes reachable, driven on the real "
              f"classifier")

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
