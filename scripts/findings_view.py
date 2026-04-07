# regula-ignore
"""
Pure-function partition of scan findings into the categories the CLI
output formats consume.

Extracted from scripts/cli.py:cmd_check during the C2 tech-debt fix.
The partition was previously inlined in a 200-line CLI handler with
no unit tests; this module makes it testable in isolation.

Design notes:
- The partition does NOT mutate the input list. The previous in-place
  assignment of `f["_finding_tier"] = ...` is now done on shallow
  copies returned in the view.
- The view is a plain dict for stability — no dataclass dependency.
- Suppressed findings are kept under their own key so consumers that
  want to display them (e.g. text output's "suppressed: N" line) can.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent))

from risk_types import compute_finding_tier

__all__ = ["partition_findings", "FindingsView"]

# Type alias for clarity — this is just `dict[str, Any]` at runtime.
FindingsView = dict[str, Any]


def _finding_tier(finding: dict) -> str:
    """Compute display tier (block/warn/info) from a finding dict."""
    return compute_finding_tier(
        finding.get("tier", ""),
        finding.get("confidence_score", 0),
    )


def partition_findings(findings: list[dict]) -> FindingsView:
    """
    Partition a list of scan findings into the buckets the CLI output
    formats consume.

    Returns a dict with these keys:
        active        — findings where suppressed is falsy
        suppressed    — findings where suppressed is truthy
        prohibited    — active findings with tier == "prohibited"
        credentials   — active findings with tier == "credential_exposure"
        high_risk     — active findings with tier == "high_risk"
        limited       — active findings with tier == "limited_risk"
        autonomy      — active findings with tier == "agent_autonomy"
        block         — active findings whose computed display tier is "block"
        warn          — active findings whose computed display tier is "warn"
        info          — active findings whose computed display tier is "info"

    Active-bucket findings are shallow-copied with a `_finding_tier`
    field added (block / warn / info). The input list is not mutated.

    The function is pure: same input → same output, no side effects.
    """
    active_raw = [f for f in findings if not f.get("suppressed")]
    suppressed = [f for f in findings if f.get("suppressed")]

    # Shallow-copy each active finding so we can annotate without
    # mutating the caller's data.
    active = []
    for f in active_raw:
        copy = dict(f)
        copy["_finding_tier"] = _finding_tier(copy)
        active.append(copy)

    by_tier = {
        "prohibited":  [f for f in active if f.get("tier") == "prohibited"],
        "credentials": [f for f in active if f.get("tier") == "credential_exposure"],
        "high_risk":   [f for f in active if f.get("tier") == "high_risk"],
        "limited":     [f for f in active if f.get("tier") == "limited_risk"],
        "autonomy":    [f for f in active if f.get("tier") == "agent_autonomy"],
    }

    by_display = {
        "block": [f for f in active if f["_finding_tier"] == "block"],
        "warn":  [f for f in active if f["_finding_tier"] == "warn"],
        "info":  [f for f in active if f["_finding_tier"] == "info"],
    }

    return {
        "active":     active,
        "suppressed": suppressed,
        **by_tier,
        **by_display,
    }
