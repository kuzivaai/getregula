# regula-ignore
"""regwatch — warn when Regula's installed ruleset is older than the
most recent regulatory change recorded in the delta log.

Reads `content/regulations/delta-log/index.json` (produced by
`scripts/build_delta_log.py`) and compares the latest entry date
against the `last_reviewed` field in `regula-policy.yaml`.

Exit codes:
  0 = ruleset is up to date
  1 = ruleset is older than the most recent regulatory change
  2 = delta log or policy file missing / malformed
"""
from __future__ import annotations

import json
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
DELTA_INDEX = REPO_ROOT / "content" / "regulations" / "delta-log" / "index.json"
# After the IA restructure the policy lives under configs/; fall back to
# the root for older checkouts so this keeps working in both layouts.
_POLICY_CANDIDATES = [
    REPO_ROOT / "configs" / "regula-policy.yaml",
    REPO_ROOT / "regula-policy.yaml",
]
POLICY_PATH = next((p for p in _POLICY_CANDIDATES if p.exists()), _POLICY_CANDIDATES[0])


def _parse_iso_date(s: str) -> date | None:
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None


def _load_last_reviewed() -> date | None:
    if not POLICY_PATH.exists():
        return None
    try:
        import yaml  # optional — policy file is YAML
        data = yaml.safe_load(POLICY_PATH.read_text(encoding="utf-8"))
    except Exception:
        # Minimal line-based fallback so regwatch works without PyYAML
        for line in POLICY_PATH.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped.startswith("last_reviewed:"):
                raw = stripped.split(":", 1)[1].strip().strip('"').strip("'")
                return _parse_iso_date(raw)
        return None
    basis = (data or {}).get("regulatory_basis", {})
    return _parse_iso_date(basis.get("last_reviewed", ""))


def run(format_: str = "text") -> dict[str, Any]:
    if not DELTA_INDEX.exists():
        return {
            "status": "error",
            "message": (
                "Delta log index not found. Run "
                "`python3 scripts/build_delta_log.py` first."
            ),
            "exit_code": 2,
        }
    try:
        index = json.loads(DELTA_INDEX.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return {"status": "error", "message": f"invalid delta log: {e}",
                "exit_code": 2}

    today = date.today()
    # Ignore future-dated placeholder entries (e.g. trilogue targets) —
    # only count regulatory changes that have actually happened.
    past_entries = [
        e for e in index.get("entries", [])
        if (_parse_iso_date(e.get("date", "")) or today) <= today
    ]
    latest_entry_date = (
        max(
            (_parse_iso_date(e["date"]) for e in past_entries
             if _parse_iso_date(e["date"])),
            default=None,
        )
        if past_entries
        else _parse_iso_date(index.get("latest_date", ""))
    )
    last_reviewed = _load_last_reviewed()

    if latest_entry_date is None:
        return {"status": "error",
                "message": "delta log has no latest_date field",
                "exit_code": 2}

    if last_reviewed is None:
        return {
            "status": "warn",
            "message": (
                "Could not determine pattern_version last_reviewed date "
                "from regula-policy.yaml."
            ),
            "latest_entry_date": latest_entry_date.isoformat(),
            "exit_code": 2,
        }

    stale = latest_entry_date > last_reviewed
    return {
        "status": "stale" if stale else "up-to-date",
        "latest_entry_date": latest_entry_date.isoformat(),
        "pattern_last_reviewed": last_reviewed.isoformat(),
        "days_stale": (latest_entry_date - last_reviewed).days if stale else 0,
        "total_entries": index.get("total_entries", 0),
        "message": (
            f"Ruleset last reviewed {last_reviewed.isoformat()} is older "
            f"than the most recent regulatory change "
            f"({latest_entry_date.isoformat()}). Review "
            f"content/regulations/delta-log/SUMMARY.md and update "
            f"regula-policy.yaml.regulatory_basis.last_reviewed."
            if stale else
            f"Ruleset reviewed {last_reviewed.isoformat()} — up to date "
            f"against delta log (latest change {latest_entry_date.isoformat()})."
        ),
        "exit_code": 1 if stale else 0,
    }


def run_cli(format_: str = "text") -> int:
    result = run(format_)
    if format_ == "json":
        print(json.dumps(result, indent=2))
    else:
        status = result["status"]
        icon = {"up-to-date": "PASS", "stale": "WARN",
                "warn": "INFO", "error": "FAIL"}.get(status, "?")
        print(f"regwatch [{icon}]: {result['message']}")
    return int(result.get("exit_code", 0))


if __name__ == "__main__":
    sys.exit(run_cli())
