#!/usr/bin/env python3
"""Regula Stop Hook - Session summary"""

import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

try:
    from log_event import query_events, verify_chain
except ImportError:
    def query_events(**k): return []
    def verify_chain(): return True, None


def main():
    try:
        after = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
        events = query_events(after=after, limit=1000)
        if events:
            stats = {"total": len(events), "blocked": sum(1 for e in events if e.get("event_type") == "blocked")}
            valid, _ = verify_chain()
            sys.stderr.write(f"Regula: {stats['total']} events, {stats['blocked']} blocked, chain {'valid' if valid else 'INVALID'}\n")
    except:
        pass
    sys.exit(0)


if __name__ == "__main__":
    main()
