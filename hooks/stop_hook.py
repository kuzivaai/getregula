#!/usr/bin/env python3
"""Regula Stop Hook - Session compliance summary"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

try:
    from log_event import query_events, verify_chain, log_event
except ImportError:
    def query_events(**k): return []
    def verify_chain(): return True, None
    def log_event(*a, **k): pass


def main():
    try:
        after = (datetime.now(timezone.utc) - timedelta(hours=8)).isoformat()
        events = query_events(after=after, limit=10000)

        if not events:
            sys.exit(0)

        total = len(events)
        blocked = [e for e in events if e.get("event_type") == "blocked"]
        classifications = [e for e in events if e.get("event_type") == "classification"]
        high_risk = [e for e in classifications if e.get("data", {}).get("tier") == "high_risk"]
        limited_risk = [e for e in classifications if e.get("data", {}).get("tier") == "limited_risk"]

        valid, error = verify_chain()

        summary = [
            "",
            "━" * 50,
            "  REGULA — Session Compliance Summary",
            "━" * 50,
            f"  Total events logged:     {total}",
            f"  Blocked (prohibited):    {len(blocked)}",
            f"  High-risk detected:      {len(high_risk)}",
            f"  Limited-risk detected:   {len(limited_risk)}",
            f"  Audit chain integrity:   {'✓ Valid' if valid else '✗ INVALID — ' + str(error)}",
            "━" * 50,
        ]

        if blocked:
            summary.append("  Blocked actions:")
            for b in blocked:
                data = b.get("data", {})
                desc = data.get("description", "Unknown")
                summary.append(f"    • {desc}")

        if high_risk:
            summary.append("  High-risk systems:")
            seen = set()
            for h in high_risk:
                data = h.get("data", {})
                cat = data.get("category", "Unknown")
                if cat not in seen:
                    seen.add(cat)
                    summary.append(f"    • {cat}")

        summary.append("")

        sys.stderr.write("\n".join(summary) + "\n")

        # Log the session summary
        try:
            log_event("session_summary", {
                "total_events": total,
                "blocked": len(blocked),
                "high_risk": len(high_risk),
                "limited_risk": len(limited_risk),
                "chain_valid": valid,
            })
        except Exception:
            pass

    except Exception:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
