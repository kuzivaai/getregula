#!/usr/bin/env python3
"""Auditable human review queue for ambiguous historical ledger rows.

The bot organises evidence; it does not infer a state from ambiguous prose.
Two distinct reviewers must independently agree before a row has proposed
consensus. Disagreement is surfaced for adjudication, never averaged away.

Usage:
    python3 scripts/ledger_review.py summary
    python3 scripts/ledger_review.py list
    python3 scripts/ledger_review.py show F1
    python3 scripts/ledger_review.py record F1 --reviewer reviewer-a \
        --state OPEN --evidence "status says ..." --rationale "..."
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import ledger_status

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_STORE = REPO_ROOT / "data" / "ledger_legacy_review_register.json"
FORMAT_VERSION = "1.0"
REVIEW_STATES = ("OPEN", "PARTIAL", "CLOSED", "ABSTAIN")
RESOLVED_STATES = ("OPEN", "PARTIAL", "CLOSED")

STATE_CRITERIA = {
    "OPEN": "Substantive work described by the row remains unfinished.",
    "PARTIAL": "The main work is done, but a named verification, gate, or residual item remains.",
    "CLOSED": "The row names no residual work, or later evidence explicitly resolves every residual.",
    "ABSTAIN": "The available row and linked evidence are insufficient for a defensible state.",
}


def review_queue(text: str | None = None) -> list[dict]:
    """Return every REVIEW_REQUIRED row with its exact source evidence."""
    classifications = {
        row["id"]: row for row in ledger_status.legacy_classifications(text)
    }
    queue = []
    for record in ledger_status.legacy_records(text):
        classification = classifications[record["id"]]
        if classification["state"] != "REVIEW_REQUIRED":
            continue
        queue.append({
            **record,
            "migration_state": "REVIEW_REQUIRED",
            "migration_basis": classification["basis"],
            "criteria": dict(STATE_CRITERIA),
        })
    return queue


def empty_register() -> dict:
    return {"format_version": FORMAT_VERSION, "decisions": []}


def load_register(path: Path) -> dict:
    if not path.exists():
        return empty_register()
    doc = json.loads(path.read_text(encoding="utf-8"))
    if doc.get("format_version") != FORMAT_VERSION:
        raise ValueError(
            f"unsupported review register format {doc.get('format_version')!r}"
        )
    if not isinstance(doc.get("decisions"), list):
        raise ValueError("review register decisions must be a list")
    return doc


def active_decisions(row: dict, register: dict) -> list[dict]:
    """Latest decision per reviewer, excluding decisions over stale source."""
    latest = {}
    for decision in register.get("decisions", []):
        if decision.get("row_id") != row["id"]:
            continue
        if decision.get("source_hash") != row["source_hash"]:
            continue
        latest[decision.get("reviewer", "")] = decision
    return [latest[key] for key in sorted(latest) if key]


def review_state(row: dict, register: dict) -> dict:
    decisions = active_decisions(row, register)
    substantive = [d for d in decisions if d.get("state") in RESOLVED_STATES]
    states = {d["state"] for d in substantive}
    if len(substantive) < 2:
        status = "AWAITING_INDEPENDENT_REVIEWS"
        proposed = None
    elif len(states) == 1:
        status = "CONSENSUS_PROPOSED"
        proposed = next(iter(states))
    else:
        status = "ADJUDICATION_REQUIRED"
        proposed = None
    return {
        "row_id": row["id"],
        "status": status,
        "proposed_state": proposed,
        "active_reviews": len(decisions),
        "substantive_reviews": len(substantive),
        "decisions": decisions,
    }


def append_decision(
    register: dict,
    row: dict,
    reviewer: str,
    state: str,
    evidence: str,
    rationale: str,
    recorded_at: str | None = None,
) -> dict:
    reviewer = reviewer.strip()
    evidence = evidence.strip()
    rationale = rationale.strip()
    if not reviewer:
        raise ValueError("reviewer must not be empty")
    if state not in REVIEW_STATES:
        raise ValueError(f"state must be one of {', '.join(REVIEW_STATES)}")
    if not evidence:
        raise ValueError("evidence must cite the row or linked source")
    if not rationale:
        raise ValueError("rationale must explain how the evidence meets the criteria")
    decision = {
        "row_id": row["id"],
        "reviewer": reviewer,
        "state": state,
        "evidence": evidence,
        "rationale": rationale,
        "source_hash": row["source_hash"],
        "recorded_at": recorded_at or datetime.now(timezone.utc).isoformat(),
    }
    register.setdefault("decisions", []).append(decision)
    return decision


def save_register(path: Path, register: dict) -> None:
    """Atomically replace the review register; prior decisions stay in history."""
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(register, indent=2, sort_keys=True) + "\n"
    fd, temp_name = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(payload)
        Path(temp_name).replace(path)
    finally:
        temp = Path(temp_name)
        if temp.exists():
            temp.unlink()


def _queue_by_id() -> dict[str, dict]:
    return {row["id"]: row for row in review_queue()}


def _print_summary(queue: list[dict], register: dict) -> None:
    states = [review_state(row, register) for row in queue]
    counts = Counter(item["status"] for item in states)
    print(f"ledger-review: {len(queue)} REVIEW_REQUIRED legacy rows")
    for status in (
        "AWAITING_INDEPENDENT_REVIEWS",
        "CONSENSUS_PROPOSED",
        "ADJUDICATION_REQUIRED",
    ):
        print(f"  {status:30s} {counts[status]}")
    print("  No proposed consensus is applied to LEDGER.md automatically.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--store", type=Path, default=DEFAULT_STORE)
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("summary")
    sub.add_parser("list")
    show = sub.add_parser("show")
    show.add_argument("row_id")
    record = sub.add_parser("record")
    record.add_argument("row_id")
    record.add_argument("--reviewer", required=True)
    record.add_argument("--state", required=True, choices=REVIEW_STATES)
    record.add_argument("--evidence", required=True)
    record.add_argument("--rationale", required=True)
    export = sub.add_parser("export")
    export.add_argument("--format", choices=("json",), default="json")
    args = parser.parse_args(argv)

    try:
        queue = review_queue()
        rows = {row["id"]: row for row in queue}
        register = load_register(args.store)
        command = args.command or "summary"
        if command == "summary":
            _print_summary(queue, register)
        elif command == "list":
            for row in queue:
                state = review_state(row, register)
                print(f"{row['id']}\t{state['status']}\t{row['finding']}")
        elif command == "show":
            row = rows.get(args.row_id)
            if row is None:
                raise ValueError(f"{args.row_id} is not in the REVIEW_REQUIRED queue")
            print(json.dumps({**row, "review": review_state(row, register)}, indent=2))
        elif command == "record":
            row = rows.get(args.row_id)
            if row is None:
                raise ValueError(f"{args.row_id} is not in the REVIEW_REQUIRED queue")
            append_decision(
                register, row, args.reviewer, args.state,
                args.evidence, args.rationale,
            )
            save_register(args.store, register)
            print(json.dumps(review_state(row, register), indent=2))
        elif command == "export":
            print(json.dumps({
                "format_version": FORMAT_VERSION,
                "criteria": STATE_CRITERIA,
                "rows": [
                    {**row, "review": review_state(row, register)}
                    for row in queue
                ],
            }, indent=2))
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"ledger-review: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
