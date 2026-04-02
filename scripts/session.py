# regula-ignore
#!/usr/bin/env python3
"""
Regula Session Aggregation — Session-Level Risk Profile

Aggregates individual tool classifications into a session-level risk profile.
Tracks which risk domains were touched across the session.

Evidence base: Agentic AI governance gap identified by Mayer Brown (Feb 2026),
World Economic Forum (March 2026). Multi-agent systems create accountability
gaps when individual tool calls are logged but session-level patterns are not.
"""

import json
import os
import sys
from collections import Counter
from datetime import datetime, timezone, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from log_event import query_events, log_event


def aggregate_session(session_id: str = None, hours: int = 8) -> dict:
    """Aggregate events for a session into a risk profile.

    If session_id is None, aggregates all events from the last N hours.
    """
    after = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
    events = query_events(after=after, limit=50000)

    if session_id:
        events = [e for e in events if e.get("session_id") == session_id]

    if not events:
        return {"session_id": session_id, "events": 0, "risk_profile": "none"}

    # Categorise events
    blocked = []
    high_risk = []
    limited_risk = []
    tool_uses = []
    domains_touched = Counter()
    tiers_seen = Counter()

    for e in events:
        etype = e.get("event_type", "")
        data = e.get("data", {})
        tier = data.get("tier", "")

        if etype == "blocked":
            blocked.append(data)
            tiers_seen["prohibited"] += 1
        elif etype == "classification":
            if tier == "high_risk":
                high_risk.append(data)
                category = data.get("category", "Unknown")
                domains_touched[category] += 1
            elif tier == "limited_risk":
                limited_risk.append(data)
            tiers_seen[tier] += 1
        elif etype == "tool_use":
            tool_uses.append(data)
            if tier and tier != "not_ai":
                tiers_seen[tier] += 1

    # Determine session risk level
    if blocked:
        session_risk = "critical"
    elif high_risk:
        session_risk = "high"
    elif limited_risk:
        session_risk = "moderate"
    elif tool_uses:
        session_risk = "low"
    else:
        session_risk = "none"

    # Build unique tool list
    tools_used = Counter()
    for e in events:
        tn = e.get("data", {}).get("tool_name")
        if tn:
            tools_used[tn] += 1

    profile = {
        "session_id": session_id or "aggregate",
        "time_range": f"last {hours} hours",
        "total_events": len(events),
        "session_risk": session_risk,
        "blocked_count": len(blocked),
        "high_risk_count": len(high_risk),
        "limited_risk_count": len(limited_risk),
        "tool_use_count": len(tool_uses),
        "domains_touched": dict(domains_touched.most_common(10)),
        "tiers_distribution": dict(tiers_seen.most_common()),
        "tools_used": dict(tools_used.most_common(10)),
        "blocked_details": [
            {"description": b.get("description", ""), "indicators": b.get("indicators", [])}
            for b in blocked
        ],
        "high_risk_details": [
            {"category": h.get("category", ""), "description": h.get("description", "")}
            for h in high_risk[:10]
        ],
    }

    return profile


def format_session_text(profile: dict) -> str:
    """Format session profile for CLI output."""
    risk_labels = {
        "critical": "CRITICAL (prohibited patterns blocked)",
        "high": "HIGH (high-risk domains detected)",
        "moderate": "MODERATE (limited-risk only)",
        "low": "LOW (minimal-risk activity)",
        "none": "NONE (no governance events)",
    }

    lines = [
        "",
        "=" * 60,
        "  Regula — Session Risk Profile",
        "=" * 60,
        f"  Session:       {profile['session_id']}",
        f"  Period:        {profile['time_range']}",
        f"  Risk Level:    {risk_labels.get(profile['session_risk'], profile['session_risk'])}",
        f"  Total Events:  {profile['total_events']}",
        f"  Blocked:       {profile['blocked_count']}",
        f"  High-Risk:     {profile['high_risk_count']}",
        f"  Limited-Risk:  {profile['limited_risk_count']}",
    ]

    if profile["domains_touched"]:
        lines.append("")
        lines.append("  Risk Domains Touched:")
        for domain, count in profile["domains_touched"].items():
            lines.append(f"    - {domain} ({count} events)")

    if profile["blocked_details"]:
        lines.append("")
        lines.append("  Blocked Actions:")
        for b in profile["blocked_details"]:
            lines.append(f"    - {b['description']}")

    if profile["tools_used"]:
        lines.append("")
        lines.append("  Tools Used:")
        for tool, count in profile["tools_used"].items():
            lines.append(f"    - {tool}: {count} calls")

    lines.append("=" * 60)
    lines.append("")
    return "\n".join(lines)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Session-level risk aggregation")
    parser.add_argument("--session", "-s", help="Session ID (default: aggregate all)")
    parser.add_argument("--hours", type=int, default=8, help="Look back N hours (default: 8)")
    parser.add_argument("--format", "-f", choices=["text", "json"], default="text")
    parser.add_argument("--log", action="store_true", help="Log the profile to audit trail")
    args = parser.parse_args()

    profile = aggregate_session(
        session_id=args.session or os.environ.get("CLAUDE_SESSION_ID"),
        hours=args.hours,
    )

    if args.format == "json":
        print(json.dumps(profile, indent=2))
    else:
        print(format_session_text(profile))

    if args.log:
        try:
            log_event("session_risk_profile", profile, session_id=args.session)
            print("  Profile logged to audit trail.", file=sys.stderr)
        except (OSError,):
            pass


if __name__ == "__main__":
    main()
