#!/usr/bin/env python3
"""Fail closed unless every independently reviewed publication condition is met."""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STATUS = ROOT / "data" / "publication_status.json"
REQUIRED_CONDITIONS = frozenset({
    "durable_name_decision_recorded",
    "fresh_reachable_privacy_audit_clear",
    "historical_pull_request_refs_remediated",
    "pypi_control_confirmed",
})


def validate_status(document: object) -> list[str]:
    errors: list[str] = []
    if not isinstance(document, dict):
        return ["status root must be an object"]
    if document.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if not isinstance(document.get("publication_allowed"), bool):
        errors.append("publication_allowed must be boolean")
    reviewed_on = document.get("reviewed_on")
    if not isinstance(reviewed_on, str):
        errors.append("reviewed_on must be an ISO date")
    else:
        try:
            date.fromisoformat(reviewed_on)
        except ValueError:
            errors.append("reviewed_on must be an ISO date")
    if not isinstance(document.get("reason_code"), str) or not document.get("reason_code"):
        errors.append("reason_code must be a non-empty string")

    conditions = document.get("conditions")
    if not isinstance(conditions, dict):
        errors.append("conditions must be an object")
        return errors
    keys = set(conditions)
    missing = sorted(REQUIRED_CONDITIONS - keys)
    unexpected = sorted(keys - REQUIRED_CONDITIONS)
    if missing:
        errors.append("missing conditions: " + ", ".join(missing))
    if unexpected:
        errors.append("unexpected conditions: " + ", ".join(unexpected))
    for name in sorted(REQUIRED_CONDITIONS & keys):
        if not isinstance(conditions[name], bool):
            errors.append(f"condition {name} must be boolean")
    return errors


def evaluate(document: object) -> list[str]:
    errors = validate_status(document)
    if errors or not isinstance(document, dict):
        return errors
    conditions = document["conditions"]
    assert isinstance(conditions, dict)
    unmet = sorted(name for name, value in conditions.items() if value is not True)
    if document["publication_allowed"] is not True:
        errors.append("publication_allowed is false")
    if unmet:
        errors.append("unmet conditions: " + ", ".join(unmet))
    return errors


def load_status(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"cannot read a valid publication status: {path}") from error


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--status", type=Path, default=DEFAULT_STATUS)
    args = parser.parse_args(argv)
    try:
        document = load_status(args.status)
    except ValueError as error:
        print(f"publication-gate: FAIL: {error}")
        return 2
    errors = evaluate(document)
    if errors:
        print("publication-gate: BLOCKED")
        for error in errors:
            print(f"  {error}")
        return 1
    print("publication-gate: PASS: all reviewed conditions are true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
