#!/usr/bin/env python3
"""
Regula Audit Trail Logger

Append-only, hash-chained event log for governance audit trails.

LIMITATION: The hash chain is self-attesting — the same user who could
modify log entries also controls the chain. For regulatory evidence that
meets ISO 27001 A.12.4 or SOC 2 standards, supplement with an external
timestamp authority (RFC 3161) or remote log forwarding.
"""

import argparse
import csv
import hashlib
import io
import json
import os
import sys
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List, Dict, Any

# Cross-platform file locking
if sys.platform == "win32":
    import msvcrt

    def _lock_file(f):
        """Acquire exclusive lock (Windows)."""
        msvcrt.locking(f.fileno(), msvcrt.LK_LOCK, 1)

    def _unlock_file(f):
        """Release exclusive lock (Windows)."""
        try:
            msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
        except OSError:
            pass
else:
    import fcntl

    def _lock_file(f):
        """Acquire exclusive lock (Unix/macOS)."""
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)

    def _unlock_file(f):
        """Release exclusive lock (Unix/macOS)."""
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)


def get_audit_dir() -> Path:
    audit_dir = Path(os.environ.get("REGULA_AUDIT_DIR", Path.home() / ".regula" / "audit"))
    audit_dir.mkdir(parents=True, exist_ok=True)
    return audit_dir


def get_audit_file() -> Path:
    return get_audit_dir() / f"audit_{datetime.now(timezone.utc).strftime('%Y-%m')}.jsonl"


@dataclass
class AuditEvent:
    event_id: str
    timestamp: str
    event_type: str
    session_id: Optional[str]
    project: Optional[str]
    data: Dict[str, Any]
    previous_hash: str
    current_hash: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True)


def compute_hash(event_dict: dict, previous_hash: str) -> str:
    event_copy = {k: v for k, v in event_dict.items() if k != "current_hash"}
    content = json.dumps(event_copy, sort_keys=True) + previous_hash
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _read_last_hash(audit_file: Path) -> str:
    """Read the current_hash of the last event in the file.

    Called while holding the file lock — do not call independently.
    """
    if not audit_file.exists() or audit_file.stat().st_size == 0:
        return "0" * 64
    try:
        with open(audit_file, "r", encoding="utf-8") as f:
            last_line = ""
            for line in f:
                stripped = line.strip()
                if stripped:
                    last_line = stripped
        if not last_line:
            return "0" * 64
        return json.loads(last_line).get("current_hash", "0" * 64)
    except (json.JSONDecodeError, OSError, KeyError):
        return "0" * 64


def log_event(
    event_type: str,
    data: Dict[str, Any],
    session_id: Optional[str] = None,
    project: Optional[str] = None,
) -> AuditEvent:
    """Append an event to the audit trail with file locking.

    Uses fcntl.flock to prevent concurrent writes from corrupting the
    hash chain when PreToolUse and PostToolUse hooks run in parallel.
    """
    audit_file = get_audit_file()

    # Open in append mode and acquire exclusive lock
    with open(audit_file, "a", encoding="utf-8") as f:
        _lock_file(f)
        try:
            # Read previous hash while holding lock
            previous_hash = _read_last_hash(audit_file)

            event = AuditEvent(
                event_id=str(uuid.uuid4()),
                timestamp=datetime.now(timezone.utc).isoformat(),
                event_type=event_type,
                session_id=session_id or os.environ.get("CLAUDE_SESSION_ID"),
                project=project or os.environ.get("REGULA_PROJECT"),
                data=data,
                previous_hash=previous_hash,
            )
            event.current_hash = compute_hash(event.to_dict(), previous_hash)
            f.write(event.to_json() + "\n")
            f.flush()
        finally:
            _unlock_file(f)

    return event


def query_events(
    event_type: Optional[str] = None,
    after: Optional[str] = None,
    before: Optional[str] = None,
    limit: int = 100,
) -> List[dict]:
    events = []
    for audit_file in sorted(get_audit_dir().glob("audit_*.jsonl")):
        try:
            with open(audit_file, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        event = json.loads(line.strip())
                    except json.JSONDecodeError:
                        continue
                    if event_type and event.get("event_type") != event_type:
                        continue
                    if after and event.get("timestamp", "") < after:
                        continue
                    if before and event.get("timestamp", "") > before:
                        continue
                    events.append(event)
                    if len(events) >= limit:
                        return events
        except OSError:
            continue
    return events


def verify_chain() -> tuple:
    """Verify hash chain integrity across all audit files.

    Returns (True, None) if valid, (False, error_message) if broken.
    """
    previous_hash = "0" * 64
    for audit_file in sorted(get_audit_dir().glob("audit_*.jsonl")):
        try:
            with open(audit_file, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    stripped = line.strip()
                    if not stripped:
                        continue
                    try:
                        event = json.loads(stripped)
                    except json.JSONDecodeError:
                        return False, f"Invalid JSON at {audit_file.name}:{line_num}"
                    if event.get("previous_hash") != previous_hash:
                        return False, f"Chain broken at {audit_file.name}:{line_num}"
                    expected = compute_hash(event, previous_hash)
                    if event.get("current_hash") != expected:
                        return False, f"Hash mismatch at {audit_file.name}:{line_num}"
                    previous_hash = event["current_hash"]
        except OSError as e:
            return False, f"Cannot read {audit_file.name}: {e}"
    return True, None


def export_csv(events: List[dict]) -> str:
    """Export events as CSV."""
    if not events:
        return ""
    output = io.StringIO()
    fields = [
        "event_id", "timestamp", "event_type", "session_id", "project",
        "tier", "indicators", "articles", "action", "tool_name", "description",
    ]
    writer = csv.DictWriter(output, fieldnames=fields, extrasaction="ignore")
    writer.writeheader()
    for event in events:
        data = event.get("data", {})
        indicators = data.get("indicators", [])
        articles = data.get("articles", [])
        row = {
            "event_id": event.get("event_id", ""),
            "timestamp": event.get("timestamp", ""),
            "event_type": event.get("event_type", ""),
            "session_id": event.get("session_id", ""),
            "project": event.get("project", ""),
            "tier": data.get("tier", ""),
            "indicators": "; ".join(indicators) if isinstance(indicators, list) else str(indicators),
            "articles": "; ".join(articles) if isinstance(articles, list) else str(articles),
            "action": data.get("action", ""),
            "tool_name": data.get("tool_name", ""),
            "description": data.get("description", ""),
        }
        writer.writerow(row)
    return output.getvalue()


def main():
    parser = argparse.ArgumentParser(description="Regula audit trail management")
    subparsers = parser.add_subparsers(dest="command")

    log_p = subparsers.add_parser("log")
    log_p.add_argument("--event-type", "-t", required=True)
    log_p.add_argument("--data", "-d")

    query_p = subparsers.add_parser("query")
    query_p.add_argument("--event-type", "-t")
    query_p.add_argument("--after")
    query_p.add_argument("--before")
    query_p.add_argument("--limit", type=int, default=100)

    export_p = subparsers.add_parser("export")
    export_p.add_argument("--format", "-f", choices=["json", "csv"], default="json")
    export_p.add_argument("--event-type", "-t")
    export_p.add_argument("--after")
    export_p.add_argument("--before")
    export_p.add_argument("--output", "-o", help="Output file path")

    subparsers.add_parser("verify")

    args = parser.parse_args()

    if args.command == "log":
        data = json.loads(args.data) if args.data else {}
        event = log_event(args.event_type, data)
        print(json.dumps({"status": "logged", "event_id": event.event_id}))
    elif args.command == "query":
        events = query_events(args.event_type, args.after, args.before, args.limit)
        print(json.dumps(events, indent=2))
    elif args.command == "export":
        events = query_events(
            getattr(args, "event_type", None),
            getattr(args, "after", None),
            getattr(args, "before", None),
            limit=100000,
        )
        content = export_csv(events) if args.format == "csv" else json.dumps(events, indent=2)
        if args.output:
            Path(args.output).write_text(content, encoding="utf-8")
            print(f"Exported {len(events)} events to {args.output}")
        else:
            print(content)
    elif args.command == "verify":
        valid, error = verify_chain()
        print(json.dumps({"status": "valid" if valid else "invalid", "error": error}))
        sys.exit(0 if valid else 1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
