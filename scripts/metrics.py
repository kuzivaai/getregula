"""
Regula local usage metrics — tracks scan counts and finding tiers.

Data is stored in ~/.regula/metrics.json as an append-friendly list of records.
Metrics are never sent anywhere; they exist only on the local machine.
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path


def _metrics_path() -> Path:
    return Path.home() / ".regula" / "metrics.json"


def _load_records() -> list:
    """Load all records from metrics.json. Returns empty list if missing or corrupt."""
    path = _metrics_path()
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return data
        return []
    except (json.JSONDecodeError, OSError):
        return []


def record_scan(findings: list) -> None:
    """Append scan stats to ~/.regula/metrics.json.

    findings is a list of finding dicts with at least a 'tier' key
    (e.g. 'BLOCK', 'WARN', 'INFO', or lower-case equivalents).
    """
    # Count by tier (normalise to upper-case)
    tier_counts: dict = {}
    for f in findings:
        tier = str(f.get("tier", "UNKNOWN")).upper()
        tier_counts[tier] = tier_counts.get(tier, 0) + 1

    record = {
        "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "findings": tier_counts,
    }

    path = _metrics_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    records = _load_records()
    records.append(record)

    path.write_text(json.dumps(records, indent=2), encoding="utf-8")


def get_stats() -> dict:
    """Read ~/.regula/metrics.json and return aggregated stats.

    Returns:
        {
            "total_scans": int,
            "first_scan": "ISO8601 string or null",
            "last_scan": "ISO8601 string or null",
            "findings_by_tier": {"BLOCK": int, "WARN": int, ...},
            "total_findings": int,
        }
    """
    records = _load_records()

    if not records:
        return {
            "total_scans": 0,
            "first_scan": None,
            "last_scan": None,
            "findings_by_tier": {},
            "total_findings": 0,
        }

    findings_by_tier: dict = {}
    for rec in records:
        for tier, count in rec.get("findings", {}).items():
            findings_by_tier[tier] = findings_by_tier.get(tier, 0) + count

    timestamps = [r["ts"] for r in records if r.get("ts")]

    return {
        "total_scans": len(records),
        "first_scan": min(timestamps) if timestamps else None,
        "last_scan": max(timestamps) if timestamps else None,
        "findings_by_tier": findings_by_tier,
        "total_findings": sum(findings_by_tier.values()),
    }


def reset_stats() -> None:
    """Delete ~/.regula/metrics.json."""
    path = _metrics_path()
    if path.exists():
        path.unlink()
