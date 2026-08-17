#!/usr/bin/env python3
"""The ledger must be countable by a command, not by hand.

On 2026-08-15 a handover asserted "23 of 51" ledger entries were open, under a
heading reading "Produced by enumeration, not from memory". It was not
enumerated. A keyword scan of the same file returned 29, the two lists agreed
on only 22, and neither could be reproduced, because the file recorded state
only as prose and there was nothing to enumerate.

Measurement rule 4c: a completeness claim is a measurement, and the set behind
it must come from an executed enumeration. These tests make that possible and
keep it possible.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import ledger_status  # noqa: E402


def test_every_entry_has_exactly_one_state_token():
    """A new entry without a token is invisible to every count of this file."""
    entries = ledger_status.parse()
    assert entries, "no ledger entries parsed"
    ids = [n for n, _ in entries]
    assert len(ids) == len(set(ids)), f"duplicate ids: {ids}"
    for nid, state in entries:
        assert state in ledger_status.VALID_STATES, f"{nid}: {state}"
    print(f"  PASS  every one of {len(entries)} ledger entries carries a state")


def test_parse_refuses_an_entry_with_no_state_token():
    """Control. The check above is only worth anything if it can fail."""
    missing = "## N900. an entry nobody tokenised\n\nsome prose\n"
    try:
        ledger_status.parse(missing)
    except ValueError as e:
        assert "N900" in str(e) and "expected exactly" in str(e), str(e)
    else:
        raise AssertionError(
            "parse accepted an entry with no State token, so the enumeration "
            "would silently omit it and every count taken would be short")
    print("  PASS  control: an untokenised entry is refused")


def test_parse_refuses_an_unknown_state():
    """Control. A typo must not become a fourth silent category."""
    bad = "## N901. typo\n\n**State:** OPNE\n\nprose\n"
    try:
        ledger_status.parse(bad)
    except ValueError as e:
        assert "OPNE" in str(e), str(e)
    else:
        raise AssertionError("parse accepted an unknown state")
    print("  PASS  control: an unknown state is refused")


def test_parse_refuses_two_tokens_in_one_entry():
    """Control. Two tokens means the entry has no single answer."""
    two = "## N902. ambiguous\n\n**State:** OPEN\n\nprose\n\n**State:** CLOSED\n"
    try:
        ledger_status.parse(two)
    except ValueError as e:
        assert "N902" in str(e), str(e)
    else:
        raise AssertionError("parse accepted an entry with two State tokens")
    print("  PASS  control: a doubly-tokenised entry is refused")


def test_counts_are_derived_not_asserted():
    """The counts must come from the parse, and the three must sum to the whole.

    A category that does not sum means an entry was counted twice or dropped,
    which is how a hand-built total goes wrong in the first place.
    """
    entries = ledger_status.parse()
    from collections import Counter
    counts = Counter(s for _, s in entries)
    total = sum(counts[s] for s in ledger_status.VALID_STATES)
    assert total == len(entries), (
        f"states sum to {total} but there are {len(entries)} entries")
    print(f"  PASS  {len(entries)} entries = "
          + " + ".join(f"{counts[s]} {s}" for s in ledger_status.VALID_STATES))


def test_a_state_contradicting_its_own_status_names_what_resolved_it():
    """A CLOSED entry whose Status prose still reads open must say why.

    Status prose is the historical record and is never rewritten, so an entry
    whose residual is closed by a LATER entry ends up contradicting itself.
    Reviewing all 55 assignments on 2026-08-15 found the rule silent on this
    and two entries treated differently as a result: N112 says "UNDERLYING
    DEFECT OPEN" and was CLOSED because N113 fixed it, while N108 said its
    detector reading was "OPEN and undiagnosed" and was PARTIAL although N110
    had diagnosed it. Same shape, two answers, and nothing in the file
    distinguished either from an assignment error.

    A `**Resolved by:**` line makes the divergence explicit and auditable.
    """
    undocumented = [nid for nid, refs in ledger_status.divergences() if not refs]
    assert not undocumented, (
        f"{undocumented} are CLOSED while their own Status prose still reads "
        f"as outstanding, and no '**Resolved by:** Nxxx' line says which entry "
        f"closed it. Either add that line, or the State is wrong.")
    print("  PASS  every self-contradicting state names what resolved it")


def test_resolved_by_ids_all_exist():
    """A pointer to nothing is worse than no pointer: it reads as evidence."""
    known = {nid for nid, _ in ledger_status.parse()}
    for nid, state, body in ledger_status.parse_full():
        for ref in ledger_status.resolved_by(body):
            assert ref in known, f"{nid} is resolved by {ref}, which does not exist"
            assert ref != nid, f"{nid} cannot resolve itself"
    print("  PASS  every 'Resolved by' reference resolves to a real entry")


def test_control_an_undocumented_divergence_is_refused():
    """Control. The check above is only worth anything if it can fail."""
    bad = ("## N900. an entry whose state contradicts its prose\n\n"
           "**State:** CLOSED\n\n**Status:** UNRESOLVED and OPEN.\n")
    entries = ledger_status.parse_full(bad)
    found = ledger_status.divergences(entries)
    assert found == [("N900", [])], found
    print("  PASS  control: an undocumented divergence is detected")


def test_control_a_documented_divergence_is_accepted():
    """The other direction. The check must not refuse a legitimate record."""
    good = ("## N900. an entry a later one closed\n\n"
            "**State:** CLOSED\n\n**Resolved by:** N901\n\n"
            "**Status:** UNRESOLVED and OPEN.\n"
            "## N901. the entry that closed it\n\n**State:** CLOSED\n\n"
            "**Status:** done.\n")
    entries = ledger_status.parse_full(good)
    assert ledger_status.divergences(entries) == [("N900", ["N901"])]
    print("  PASS  control: a documented divergence is accepted")


def test_control_the_outstanding_marker_does_not_fire_on_standing_verdicts(
):
    """Control for the marker set, not the mechanism.

    The first draft matched "remains" and flagged three entries that were not
    diverging: "no `cryptography <50` remains in any tracked file" means
    nothing remains, and "external action remains NOT AUTHORISED" is a
    standing governance verdict rather than this entry's residual work. A gate
    that is wrong three times in four gets ignored, so the false positives are
    pinned here as well as the true one.
    """
    for phrase in ("FULLY CLOSED. No `cryptography` pin remains in any file.",
                   "complete; external action remains NOT AUTHORISED.",
                   "public review complete; exact H1 remains ABANDONED."):
        body = f"\n**State:** CLOSED\n\n**Status:** {phrase}\n"
        assert not ledger_status.status_reads_outstanding(body), phrase
    assert ledger_status.status_reads_outstanding(
        "\n**Status:** GATE FIXED, UNDERLYING DEFECT OPEN.\n"), (
        "the marker set no longer fires on the one real divergence")
    print("  PASS  control: standing verdicts are not read as residual work")


if __name__ == "__main__":
    for t in (test_every_entry_has_exactly_one_state_token,
              test_parse_refuses_an_entry_with_no_state_token,
              test_parse_refuses_an_unknown_state,
              test_parse_refuses_two_tokens_in_one_entry,
              test_counts_are_derived_not_asserted,
              test_a_state_contradicting_its_own_status_names_what_resolved_it,
              test_resolved_by_ids_all_exist,
              test_control_an_undocumented_divergence_is_refused,
              test_control_a_documented_divergence_is_accepted,
              test_control_the_outstanding_marker_does_not_fire_on_standing_verdicts):
        t()
