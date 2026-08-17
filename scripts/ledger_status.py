#!/usr/bin/env python3
"""Enumerate the open-items ledger.

Why this exists. The ledger recorded each entry's state only as prose, so no
count of it could be produced by enumeration, only by hand. On 2026-08-15 a
handover asserted "23 of 51" under a heading reading "Produced by enumeration,
not from memory". It was not: a keyword scan of the same file returned 29, the
two lists agreed on 22, and neither was reproducible. Measurement rule 4c says
a completeness claim is a measurement and must come from an executed
enumeration. This is that enumeration.

Each entry carries `**State:** OPEN | PARTIAL | CLOSED`, assigned from the
entry's own Status prose by one rule:

    CLOSED   the status names no residual work at all
    PARTIAL  the substantive work is done but the status names something
             outstanding: a verification, a gate, a sub-item, a sibling
    OPEN     the substantive work is not done

The distinction matters because the two figures above were not disagreeing
about facts, they were using different definitions. "Open" alone is ambiguous
here: the OPEN count and the OPEN + PARTIAL count differ by more than twenty,
so state which you mean or the number carries no information.

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
"""
import argparse
import re
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LEDGER = REPO_ROOT / "docs" / "improvement" / "LEDGER.md"

VALID_STATES = ("OPEN", "PARTIAL", "CLOSED")

_HEADING = re.compile(r'^#{2,3} \*?\*?N(\d+)[.\s—-]', re.M)
_STATE = re.compile(r'^\*\*State:\*\* *(\w+) *$', re.M)
_RESOLVED_BY = re.compile(r'^\*\*Resolved by:\*\* *(.+?) *$', re.M)
_NID = re.compile(r'N\d+')

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
    """Return [(id, state)] for every N-entry, in file order.

    Raises ValueError if any entry lacks exactly one State token, so a new
    entry cannot be added without one and quietly fall out of every count.
    """
    return [(nid, state) for nid, state, _ in parse_full(text)]


def parse_full(text: str = None) -> list:
    """Return [(id, state, body)] for every N-entry, in file order."""
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

    if args.list:
        for nid, state in entries:
            print(f"{nid}\t{state}")
        return 0

    counts = Counter(s for _, s in entries)
    print(f"ledger-status: {len(entries)} entries in {LEDGER.name}")
    for state in VALID_STATES:
        print(f"  {state:8s} {counts[state]}")
    print(f"  substantive work outstanding (OPEN)          : {counts['OPEN']}")
    print(f"  anything outstanding at all (OPEN + PARTIAL) : "
          f"{counts['OPEN'] + counts['PARTIAL']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
