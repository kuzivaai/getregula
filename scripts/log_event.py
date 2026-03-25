#!/usr/bin/env python3
"""Regula Audit Trail Logger"""

import argparse
import hashlib
import json
import os
import sys
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List, Dict, Any


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


def get_previous_hash(audit_file: Path) -> str:
    if not audit_file.exists():
        return "0" * 64
    try:
        with open(audit_file, "rb") as f:
            f.seek(-2, os.SEEK_END)
            while f.read(1) != b"\n":
                f.seek(-2, os.SEEK_CUR)
            last_line = f.readline().decode("utf-8")
        return json.loads(last_line.strip()).get("current_hash", "0" * 64)
    except:
        return "0" * 64


def log_event(event_type: str, data: Dict[str, Any], session_id: Optional[str] = None, project: Optional[str] = None) -> AuditEvent:
    audit_file = get_audit_file()
    previous_hash = get_previous_hash(audit_file)
    event = AuditEvent(
        event_id=str(uuid.uuid4()), timestamp=datetime.now(timezone.utc).isoformat(),
        event_type=event_type, session_id=session_id or os.environ.get("CLAUDE_SESSION_ID"),
        project=project or os.environ.get("REGULA_PROJECT"), data=data, previous_hash=previous_hash
    )
    event.current_hash = compute_hash(event.to_dict(), previous_hash)
    with open(audit_file, "a", encoding="utf-8") as f:
        f.write(event.to_json() + "\n")
    return event


def query_events(event_type: Optional[str] = None, after: Optional[str] = None, before: Optional[str] = None, limit: int = 100) -> List[dict]:
    events = []
    for audit_file in sorted(get_audit_dir().glob("audit_*.jsonl")):
        with open(audit_file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    event = json.loads(line.strip())
                    if event_type and event.get("event_type") != event_type:
                        continue
                    if after and event.get("timestamp", "") < after:
                        continue
                    if before and event.get("timestamp", "") > before:
                        continue
                    events.append(event)
                    if len(events) >= limit:
                        return events
                except:
                    continue
    return events


def verify_chain() -> tuple:
    previous_hash = "0" * 64
    for audit_file in sorted(get_audit_dir().glob("audit_*.jsonl")):
        with open(audit_file, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                try:
                    event = json.loads(line.strip())
                    if event.get("previous_hash") != previous_hash:
                        return False, f"Chain broken at {audit_file.name}:{line_num}"
                    if event.get("current_hash") != compute_hash(event, previous_hash):
                        return False, f"Hash mismatch at {audit_file.name}:{line_num}"
                    previous_hash = event.get("current_hash")
                except:
                    return False, f"Invalid JSON at {audit_file.name}:{line_num}"
    return True, None


def main():
    parser = argparse.ArgumentParser(description="Regula audit trail management")
    subparsers = parser.add_subparsers(dest="command")
    
    log_p = subparsers.add_parser("log")
    log_p.add_argument("--event-type", "-t", required=True)
    log_p.add_argument("--data", "-d")
    
    query_p = subparsers.add_parser("query")
    query_p.add_argument("--event-type", "-t")
    query_p.add_argument("--after")
    query_p.add_argument("--limit", type=int, default=100)
    
    subparsers.add_parser("verify")
    
    args = parser.parse_args()
    
    if args.command == "log":
        data = json.loads(args.data) if args.data else {}
        event = log_event(args.event_type, data)
        print(json.dumps({"status": "logged", "event_id": event.event_id}))
    elif args.command == "query":
        print(json.dumps(query_events(args.event_type, args.after, limit=args.limit), indent=2))
    elif args.command == "verify":
        valid, error = verify_chain()
        print(json.dumps({"status": "valid" if valid else "invalid", "error": error}))
        sys.exit(0 if valid else 1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
