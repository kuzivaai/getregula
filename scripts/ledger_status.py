#!/usr/bin/env python3
"""Enumerate machine-state entries and disclose the ledger coverage boundary.

Why this exists. The ledger recorded each entry's state only as prose, so no
count of it could be produced by enumeration, only by hand. On 2026-08-15 a
handover asserted "23 of 51" under a heading reading "Produced by enumeration,
not from memory". It was not: a keyword scan of the same file returned 29, the
two lists agreed on 22, and neither was reproducible. Measurement rule 4c says
a completeness claim is a measurement and must come from an executed
enumeration. This is that enumeration.

Each heading-form entry in the machine-state section carries `**State:** OPEN
| PARTIAL | CLOSED`, assigned from the entry's own Status prose by one rule:

    CLOSED   the status names no residual work at all
    PARTIAL  the substantive work is done but the status names something
             outstanding: a verification, a gate, a sub-item, a sibling
    OPEN     the substantive work is not done

The distinction matters because the two figures above were not disagreeing
about facts, they were using different definitions. "Open" alone is ambiguous
here: the OPEN count and the OPEN + PARTIAL count differ by more than twenty,
so state which you mean or the number carries no information.

The older table remains outside those heading-form totals. It is now also
enumerated through a conservative migration view: only explicit, unambiguous
opening declarations map to OPEN/PARTIAL/CLOSED; mixed or non-state prose maps
to REVIEW_REQUIRED rather than being guessed.

WHEN A LATER ENTRY RESOLVES AN EARLIER ONE. The rule above reads each entry's
own Status prose, and that prose is the historical record: it is never
rewritten. So an entry whose residual is closed later has a State that
contradicts its own text, and the reader has no way to tell that from an
assignment error.

Reviewing all 55 assignments on 2026-08-15 found the rule silent on this and
two entries treated differently because of it. N112 says "UNDERLYING DEFECT
OPEN" and is CLOSED, because N113 fixed it. N108 says its detector reading is
"OPEN and undiagnosed" and was PARTIAL, though N110 diagnosed it and N112 and
N113 fixed it. Same shape, two answers.

An entry may therefore carry `**Resolved by:** Nxxx[, Nyyy]`, naming the
entries that closed what its own Status still describes as outstanding. It is
REQUIRED whenever the State is CLOSED and the Status prose still reads as
outstanding, so the divergence is always explained rather than silent, and the
ids must resolve to real entries. `tests/test_ledger_enumeration.py` enforces
both, each with a control.

No count is written into this docstring on purpose. Run the command. A figure
recorded in prose next to the tool that derives it is the drift this module
exists to end, and the first draft of this file carried two that were stale
within the hour.

Usage:
    python3 scripts/ledger_status.py            # counts
    python3 scripts/ledger_status.py --list     # every entry and its state
    python3 scripts/ledger_status.py --state OPEN
    python3 scripts/ledger_status.py --legacy  # conservative legacy view
"""
import argparse
import re
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LEDGER = REPO_ROOT / "docs" / "improvement" / "LEDGER.md"

VALID_STATES = ("OPEN", "PARTIAL", "CLOSED")
VALID_LEGACY_STATES = ("OPEN", "PARTIAL", "CLOSED", "REVIEW_REQUIRED")

_HEADING = re.compile(r'^#{2,3} \*?\*?N(\d+)[.\s—-]', re.M)
_STATE = re.compile(r'^\*\*State:\*\* *(\w+) *$', re.M)
_RESOLVED_BY = re.compile(r'^\*\*Resolved by:\*\* *(.+?) *$', re.M)
_NID = re.compile(r'N\d+')
_LEGACY_ROW = re.compile(
    r'^\|\s+\*{0,2}([FN]\d+)\*{0,2}\s+\|', re.MULTILINE)
_LEGACY_LINE = re.compile(
    r'^\|\s+\*{0,2}([FN]\d+)\*{0,2}\s+\|.*$', re.MULTILINE)
_LEGACY_STATUS_AFTER_DATE = re.compile(
    r'\|\s+\*{0,2}2026-[^|]*?\*{0,2}\s+\|\s*(.*)\|\s*$')
_OPENING_BOLD = re.compile(r'^\*\*(.+?)\*\*', re.S)

# Read against the Status prose only, and only from its opening clause: the
# body of an entry legitimately discusses what was open at the time. The
# question is narrow, "does this entry's own headline still read as
# outstanding", so a wider window would flag almost everything.
_STATUS_HEAD = re.compile(r'\*\*Status:\*\*\s*(.{0,240})', re.S)
# Markers that denote residual work ON THIS ENTRY. Deliberately narrow.
#
# The first draft also matched "remains", "blocked" and "not started", and
# flagged three entries that were not diverging at all: N74's "no
# `cryptography <50` remains in any tracked file" (nothing remains), and
# N67/N68's "external action remains NOT AUTHORISED" (a standing governance
# verdict, which is not this entry's residual work). A gate that cries wolf
# three times in four gets switched off, so the marker set is the one that
# only fires on the real thing.
_READS_OUTSTANDING = re.compile(
    r'\b(OPEN|PENDING|OUTSTANDING|NOT CLOSED|UNDIAGNOSED|UNRESOLVED)\b')


def parse(text: str = None) -> list:
    """Return [(id, state)] for every heading-form N-entry, in file order.

    Raises ValueError if any entry lacks exactly one State token, so a new
    entry cannot be added without one and quietly fall out of every count.
    """
    return [(nid, state) for nid, state, _ in parse_full(text)]


def parse_full(text: str = None) -> list:
    """Return [(id, state, body)] for heading-form N-entries, in file order."""
    text = LEDGER.read_text(encoding="utf-8") if text is None else text
    marks = list(_HEADING.finditer(text))
    entries = []
    for i, m in enumerate(marks):
        nid = "N" + m.group(1)
        end = marks[i + 1].start() if i + 1 < len(marks) else len(text)
        body = text[m.end():end]
        found = _STATE.findall(body)
        if len(found) != 1:
            raise ValueError(
                f"{nid} has {len(found)} '**State:**' tokens, expected exactly "
                f"1. Every ledger entry needs one or it is invisible to every "
                f"count taken of this file.")
        if found[0] not in VALID_STATES:
            raise ValueError(
                f"{nid} has state {found[0]!r}, expected one of "
                f"{', '.join(VALID_STATES)}")
        entries.append((nid, found[0], body))
    if not entries:
        raise ValueError(f"no ledger entries found in {LEDGER}")
    dupes = [k for k, v in Counter(n for n, _, _ in entries).items() if v > 1]
    if dupes:
        raise ValueError(f"duplicate ledger ids: {sorted(dupes)}")
    return entries


def legacy_rows(text: str = None) -> list[str]:
    """Return ids in the historical findings table, which has no State token.

    They remain separate from heading-form machine-state totals. Use
    `legacy_classifications()` for the conservative migration view.
    """
    text = LEDGER.read_text(encoding="utf-8") if text is None else text
    return _LEGACY_ROW.findall(text)


def legacy_classifications(text: str = None) -> list[dict]:
    """Classify every historical table row without inferring from prose.

    The table predates machine-state tokens. Its status cells often mix a
    closed measurement defect with an open product defect, or use words such
    as "measured", "built" and "settled" that do not unambiguously declare a
    state. Only an explicit opening declaration is migrated automatically:

    * OPEN -> OPEN
    * PARTIALLY CLOSED / PARTIAL -> PARTIAL
    * CLOSED -> CLOSED only when the same status cell does not also declare
      residual OPEN/PENDING/OUTSTANDING/UNRESOLVED work
    * everything else -> REVIEW_REQUIRED

    REVIEW_REQUIRED is a classification, not a guess. It makes the coverage
    boundary enumerable while preserving the need for a human ruling.
    """
    text = LEDGER.read_text(encoding="utf-8") if text is None else text
    rows = []
    for match in _LEGACY_LINE.finditer(text):
        nid = match.group(1)
        line = match.group(0)
        status_match = _LEGACY_STATUS_AFTER_DATE.search(line)
        if not status_match:
            rows.append({
                "id": nid,
                "state": "REVIEW_REQUIRED",
                "basis": "status cell could not be isolated without guessing",
            })
            continue
        status = status_match.group(1).strip()
        opening_match = _OPENING_BOLD.match(status)
        opening = (opening_match.group(1) if opening_match else status).strip()
        normalised = opening.upper()
        full_status = re.sub(r'[`*_~]', '', status).upper()
        if normalised.startswith("OPEN"):
            state = "OPEN"
            basis = "status opens with an explicit OPEN declaration"
        elif normalised.startswith(("PARTIALLY CLOSED", "PARTIAL")):
            state = "PARTIAL"
            basis = "status opens with an explicit partial-closure declaration"
        elif normalised.startswith("CLOSED") and not _READS_OUTSTANDING.search(
                full_status):
            state = "CLOSED"
            basis = "status opens CLOSED and declares no residual work"
        elif not opening_match and normalised.startswith("CLOSED") \
                and not _READS_OUTSTANDING.search(full_status):
            state = "CLOSED"
            basis = "status cell opens CLOSED and declares no residual work"
        else:
            state = "REVIEW_REQUIRED"
            basis = (
                "status does not make one unambiguous machine-state declaration"
            )
        rows.append({"id": nid, "state": state, "basis": basis})
    ids = [row["id"] for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate legacy row ids")
    return rows


def resolved_by(body: str) -> list:
    """Entry ids named on this entry's `**Resolved by:**` line, if any."""
    m = _RESOLVED_BY.search(body)
    return _NID.findall(m.group(1)) if m else []


def status_reads_outstanding(body: str) -> bool:
    """Does this entry's Status headline still describe residual work?"""
    m = _STATUS_HEAD.search(body)
    return bool(m) and bool(_READS_OUTSTANDING.search(m.group(1)))


def divergences(entries=None) -> list:
    """Entries marked CLOSED whose own Status prose still reads as open.

    Each is legitimate ONLY with a `**Resolved by:**` line naming the entries
    that closed it. Returns [(id, resolved_by_ids)] so the caller can tell a
    documented divergence from an undocumented one.
    """
    entries = parse_full() if entries is None else entries
    return [(nid, resolved_by(body)) for nid, state, body in entries
            if state == "CLOSED" and status_reads_outstanding(body)]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--list", action="store_true", help="print every entry")
    ap.add_argument("--state", choices=VALID_STATES, help="print ids in a state")
    ap.add_argument(
        "--legacy", action="store_true",
        help="list every legacy table row with its conservative migration state",
    )
    args = ap.parse_args()

    try:
        entries = parse()
    except ValueError as e:
        print(f"ledger-status: {e}", file=sys.stderr)
        return 1

    if args.state:
        ids = [n for n, s in entries if s == args.state]
        print(" ".join(sorted(ids, key=lambda x: int(x[1:]))))
        return 0

    if args.legacy:
        for row in legacy_classifications():
            print(f"{row['id']}\t{row['state']}\t{row['basis']}")
        return 0

    if args.list:
        for nid, state in entries:
            print(f"{nid}\t{state}")
        return 0

    counts = Counter(s for _, s in entries)
    legacy = legacy_classifications()
    legacy_counts = Counter(row["state"] for row in legacy)
    print(
        f"ledger-status: {len(entries)} machine-state entries in {LEDGER.name}"
    )
    for state in VALID_STATES:
        print(f"  {state:8s} {counts[state]}")
    print(f"  substantive work outstanding (OPEN)          : {counts['OPEN']}")
    print(f"  anything outstanding at all (OPEN + PARTIAL) : "
          f"{counts['OPEN'] + counts['PARTIAL']}")
    print(
        f"  legacy migration view: {len(legacy)} table rows are excluded from "
        "the machine-state totals above"
    )
    for state in VALID_LEGACY_STATES:
        print(f"    {state:15s} {legacy_counts[state]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
