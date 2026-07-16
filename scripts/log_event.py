# regula-ignore
#!/usr/bin/env python3
"""
Regula Audit Trail Logger

Append-only, hash-chained event log for governance audit trails.

SCOPING: Events attributed to a project (via the ``project_path``
argument, or the ``REGULA_PROJECT_DIR`` environment variable) are
written to that project's own chain under
``<audit_root>/projects/<slug>/``. Unattributed events go to the
machine-wide store at the audit root, as in previous releases.
Deliverable surfaces (evidence packs, conformity packs, reports) MUST
use :func:`collect_audit_trail`, which only ever reads the target
project's chain — events from other projects on the same machine are
never embedded in a deliverable (client confidentiality).

ROTATION: Log files rotate monthly. A new monthly file continues the
chain from the previous file's last hash. Versions prior to v1.7.5
seeded each new monthly file with the genesis hash instead;
:func:`verify_chain` therefore treats a genesis seed at the START of a
file as a reported "legacy restart" rather than a failure. A genesis
seed anywhere else, or any non-genesis mismatch, still fails
verification. Consequence: truncating a legacy store exactly at a
month boundary is not detectable by the chain alone — see LIMITATION.

LIMITATION: The hash chain is self-attesting — the same user who could
modify log entries also controls the chain. For regulatory evidence that
meets ISO 27001 A.12.4 or SOC 2 standards, supplement with an external
timestamp authority (RFC 3161) or remote log forwarding.
"""

__all__ = [
    "AuditEvent", "log_event", "query_events", "verify_chain",
    "verify_chain_dir", "collect_audit_trail", "export_csv",
    "get_audit_dir", "project_slug",
]

import argparse
import csv
import hashlib
import io
import json
import os
import re
import sys
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List, Dict, Any

# Optional RFC 3161 timestamping — imported lazily so log_event works without timestamp.py
try:
    sys.path.insert(0, str(Path(__file__).parent))
    from timestamp import request_timestamp  # noqa: F401
except ImportError:
    request_timestamp = None  # type: Optional[Any]

# Cross-platform file locking
if sys.platform == "win32":
    import msvcrt

    def _lock_file(f):
        """Acquire exclusive lock (Windows).

        Always lock byte 0 so all concurrent processes contend on the
        same byte regardless of append-mode file position.
        """
        f.seek(0)
        msvcrt.locking(f.fileno(), msvcrt.LK_LOCK, 1)

    def _unlock_file(f):
        """Release exclusive lock (Windows)."""
        try:
            f.seek(0)
            msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
        except OSError:
            pass  # unlock failure is non-fatal on Windows
else:
    import fcntl

    def _lock_file(f):
        """Acquire exclusive lock (Unix/macOS)."""
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)

    def _unlock_file(f):
        """Release exclusive lock (Unix/macOS)."""
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)


GENESIS_HASH = "0" * 64


def project_slug(project_path) -> str:
    """Stable, filesystem-safe identifier for a project's audit chain.

    Combines the sanitised directory name (human-readable) with a short
    hash of the resolved absolute path (collision-resistant), so two
    projects with the same directory name never share a chain.
    """
    resolved = Path(project_path).resolve()
    name = re.sub(r"[^a-zA-Z0-9_\-]", "_", resolved.name) or "project"
    digest = hashlib.sha256(str(resolved).encode("utf-8")).hexdigest()[:8]
    return f"{name.lower()}-{digest}"


def get_audit_dir(project_path=None) -> Path:
    """Audit directory: machine-wide root, or a project's chain directory."""
    root = Path(os.environ.get("REGULA_AUDIT_DIR", Path.home() / ".regula" / "audit"))
    audit_dir = root / "projects" / project_slug(project_path) if project_path else root
    audit_dir.mkdir(parents=True, exist_ok=True)
    return audit_dir


def get_audit_file(project_path=None) -> Path:
    return get_audit_dir(project_path) / f"audit_{datetime.now(timezone.utc).strftime('%Y-%m')}.jsonl"


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
    Uses a separate read to avoid interfering with the append-mode
    write handle that holds the lock.
    """
    if not audit_file.exists() or audit_file.stat().st_size == 0:
        return "0" * 64
    try:
        # Read entire file content — audit files are append-only and bounded
        # by monthly rotation, so size is manageable
        content = audit_file.read_text(encoding="utf-8")
        # Find last non-empty line
        for line in reversed(content.splitlines()):
            stripped = line.strip()
            if stripped:
                return json.loads(stripped).get("current_hash", "0" * 64)
        return "0" * 64
    except (json.JSONDecodeError, OSError, KeyError):
        return "0" * 64


def _read_seed_hash(audit_file: Path, pattern: str = "audit_*.jsonl") -> str:
    """Chain seed for the next append to audit_file.

    Continues the chain across monthly rotation: if audit_file is new or
    empty, the seed is the last hash of the most recent earlier file in
    the same directory. Genesis only when no earlier file has content.
    (Versions prior to v1.7.5 seeded every new monthly file with genesis,
    which structurally broke verify_chain at each month boundary.)

    Called while holding the file lock — do not call independently.
    """
    if audit_file.exists() and audit_file.stat().st_size > 0:
        return _read_last_hash(audit_file)
    prior = sorted(
        p for p in audit_file.parent.glob(pattern)
        if p.name < audit_file.name
    )
    for p in reversed(prior):
        try:
            if p.stat().st_size > 0:
                return _read_last_hash(p)
        except OSError:
            continue
    return GENESIS_HASH


def log_event(
    event_type: str,
    data: Dict[str, Any],
    session_id: Optional[str] = None,
    project: Optional[str] = None,
    external_timestamp: bool = False,
    project_path: Optional[str] = None,
) -> AuditEvent:
    """Append an event to the audit trail with file locking.

    When project_path is given (or REGULA_PROJECT_DIR is set), the event
    is written to that project's own chain under
    <audit_root>/projects/<slug>/ and the event's `project` field is
    auto-filled with the directory name unless `project` is passed.
    Without a project path, the event goes to the machine-wide store
    (behaviour of previous releases).

    Uses fcntl.flock to prevent concurrent writes from corrupting the
    hash chain when PreToolUse and PostToolUse hooks run in parallel.
    """
    if project_path is None:
        project_path = os.environ.get("REGULA_PROJECT_DIR") or None
    project_name = project or os.environ.get("REGULA_PROJECT")
    if project_name is None and project_path:
        project_name = Path(project_path).resolve().name

    audit_file = get_audit_file(project_path)

    # Open in append mode and acquire exclusive lock
    with open(audit_file, "a", encoding="utf-8") as f:
        _lock_file(f)
        try:
            # Read seed hash while holding lock (continues the chain
            # across monthly rotation)
            previous_hash = _read_seed_hash(audit_file)

            event = AuditEvent(
                event_id=str(uuid.uuid4()),
                timestamp=datetime.now(timezone.utc).isoformat(),
                event_type=event_type,
                session_id=session_id or os.environ.get("CLAUDE_SESSION_ID"),
                project=project_name,
                data=dict(data),  # copy to allow mutation
                previous_hash=previous_hash,
            )
            event.current_hash = compute_hash(event.to_dict(), previous_hash)

            # Optional RFC 3161 external timestamp (best-effort, never blocks)
            if external_timestamp:
                try:
                    tst = request_timestamp(event.current_hash)
                    event.data["tst_hex"] = tst["tst_hex"]
                    event.data["tsa_url"] = tst["tsa_url"]
                    # Recompute hash with TST included in data
                    event.current_hash = compute_hash(event.to_dict(), previous_hash)
                except Exception as e:
                    print(f"regula: RFC 3161 timestamping failed: {e}", file=sys.stderr)

            f.write(event.to_json() + "\n")
            f.flush()
        finally:
            _unlock_file(f)

    return event


def _read_events_from_files(
    files: List[Path],
    event_type: Optional[str],
    after: Optional[str],
    before: Optional[str],
    limit: Optional[int],
) -> List[dict]:
    """Read filtered events from a list of chain files, in file order."""
    events = []
    for audit_file in files:
        try:
            with open(audit_file, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        event = json.loads(line.strip())
                    except json.JSONDecodeError:
                        continue  # skip malformed log line
                    if event_type and event.get("event_type") != event_type:
                        continue
                    if after and event.get("timestamp", "") < after:
                        continue
                    if before and event.get("timestamp", "") > before:
                        continue
                    events.append(event)
                    if limit is not None and len(events) >= limit:
                        return events
        except OSError:
            continue  # unreadable audit file; skip
    return events


def _project_chain_dirs(root: Path) -> List[Path]:
    """All per-project chain directories under the audit root."""
    projects_dir = root / "projects"
    if not projects_dir.is_dir():
        return []
    return sorted(p for p in projects_dir.iterdir() if p.is_dir())


def query_events(
    event_type: Optional[str] = None,
    after: Optional[str] = None,
    before: Optional[str] = None,
    limit: int = 100,
    project_path: Optional[str] = None,
) -> List[dict]:
    """Query audit events.

    With project_path: only that project's chain, in chain order (so a
    prefix of the result is independently verifiable). Without: the
    whole machine — the machine-wide store plus every project chain,
    merged in timestamp order.
    """
    if project_path is not None:
        files = sorted(get_audit_dir(project_path).glob("audit_*.jsonl"))
        return _read_events_from_files(files, event_type, after, before, limit)

    root = get_audit_dir()
    project_dirs = _project_chain_dirs(root)
    root_files = sorted(root.glob("audit_*.jsonl"))
    if not project_dirs:
        # Single-store fast path: stream with early exit at limit.
        return _read_events_from_files(root_files, event_type, after, before, limit)

    events = _read_events_from_files(root_files, event_type, after, before, None)
    for pdir in project_dirs:
        events.extend(_read_events_from_files(
            sorted(pdir.glob("audit_*.jsonl")), event_type, after, before, None,
        ))
    events.sort(key=lambda e: e.get("timestamp", ""))
    return events[:limit] if limit is not None else events


def verify_chain_dir(dir_path, pattern: str = "audit_*.jsonl") -> tuple:
    """Verify hash-chain integrity across one directory of chain files.

    A genesis previous_hash at the START of a file (when the chain has
    already advanced) is tolerated as a "legacy restart" — the pre-v1.7.5
    writer seeded every new monthly file with genesis, so requiring
    continuity would permanently invalidate every existing store. Legacy
    restarts are reported in the returned message so nothing is hidden.
    Any other mismatch, tampering, or a genesis seed mid-file fails.

    Returns (True, None) for a fully continuous valid chain,
    (True, note) when valid apart from reported legacy restarts,
    (False, error_message) when broken.
    """
    previous_hash = GENESIS_HASH
    restarts = []
    for audit_file in sorted(Path(dir_path).glob(pattern)):
        first_in_file = True
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
                        if first_in_file and event.get("previous_hash") == GENESIS_HASH:
                            restarts.append(audit_file.name)
                            previous_hash = GENESIS_HASH
                        else:
                            return False, f"Chain broken at {audit_file.name}:{line_num}"
                    expected = compute_hash(event, previous_hash)
                    if event.get("current_hash") != expected:
                        return False, f"Hash mismatch at {audit_file.name}:{line_num}"
                    previous_hash = event["current_hash"]
                    first_in_file = False
        except OSError as e:
            return False, f"Cannot read {audit_file.name}: {e}"
    if restarts:
        return True, (
            f"chain valid with {len(restarts)} legacy month-boundary "
            f"restart(s) at: {', '.join(restarts)} (written by a version "
            f"without cross-file continuity; new events link across files)"
        )
    return True, None


def verify_chain(project_path: Optional[str] = None) -> tuple:
    """Verify hash chain integrity.

    With project_path: verifies only that project's chain. Without:
    verifies the machine-wide store and every project chain; all must
    pass. Returns (True, None) if fully valid, (True, note) when valid
    with reported legacy restarts, (False, error_message) if broken.
    """
    if project_path is not None:
        return verify_chain_dir(get_audit_dir(project_path))

    root = get_audit_dir()
    problems = []
    notes = []
    valid, msg = verify_chain_dir(root)
    if not valid:
        problems.append(f"machine store: {msg}")
    elif msg:
        notes.append(f"machine store: {msg}")
    for pdir in _project_chain_dirs(root):
        valid, msg = verify_chain_dir(pdir)
        if not valid:
            problems.append(f"project {pdir.name}: {msg}")
        elif msg:
            notes.append(f"project {pdir.name}: {msg}")
    if problems:
        return False, "; ".join(problems)
    return True, ("; ".join(notes) or None)


def collect_audit_trail(project_path, limit: int = 10000) -> dict:
    """Project-scoped audit-trail payload for deliverable surfaces.

    This is the ONLY way evidence packs, conformity packs, and reports
    may embed audit events. It reads exclusively from the target
    project's own chain — events from other projects or from the
    machine-wide store are never included (client confidentiality for
    multi-client consultants).

    Embedded events are the chain PREFIX in chain order, so the subset
    is independently verifiable from genesis even when limit is reached.
    """
    resolved = Path(str(project_path)).resolve()
    events = query_events(limit=limit + 1, project_path=str(project_path))
    limit_reached = len(events) > limit
    events = events[:limit]
    chain_valid, chain_msg = verify_chain(project_path=str(project_path))
    return {
        "scope": "project",
        "project": resolved.name,
        "project_slug": project_slug(str(project_path)),
        "chain_valid": chain_valid,
        "chain_message": chain_msg,
        "event_count": len(events),
        "limit_reached": limit_reached,
        "scope_note": (
            "Audit events are scoped to this project's own hash chain. "
            "Events from other projects or from the machine-wide store "
            "are never included in deliverables. Events recorded by "
            "Regula versions without project-scoped logging remain in "
            "the machine-wide store and are excluded."
        ),
        "events": events,
    }


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
    log_p.add_argument("--project", "-p", help="Attribute to a project (path)")

    query_p = subparsers.add_parser("query")
    query_p.add_argument("--event-type", "-t")
    query_p.add_argument("--after")
    query_p.add_argument("--before")
    query_p.add_argument("--limit", type=int, default=100)
    query_p.add_argument("--project", "-p",
                         help="Scope to one project's chain (path); default: whole machine")

    export_p = subparsers.add_parser("export")
    export_p.add_argument("--format", "-f", choices=["json", "csv"], default="json")
    export_p.add_argument("--event-type", "-t")
    export_p.add_argument("--after")
    export_p.add_argument("--before")
    export_p.add_argument("--output", "-o", help="Output file path")
    export_p.add_argument("--project", "-p",
                          help="Scope to one project's chain (path); default: whole machine")

    verify_p = subparsers.add_parser("verify")
    verify_p.add_argument("--project", "-p",
                          help="Scope to one project's chain (path); default: whole machine")

    args = parser.parse_args()
    project = getattr(args, "project", None)

    if args.command == "log":
        data = json.loads(args.data) if args.data else {}
        event = log_event(args.event_type, data, project_path=project)
        print(json.dumps({"status": "logged", "event_id": event.event_id}))
    elif args.command == "query":
        events = query_events(args.event_type, args.after, args.before,
                              args.limit, project_path=project)
        print(json.dumps(events, indent=2))
    elif args.command == "export":
        events = query_events(
            getattr(args, "event_type", None),
            getattr(args, "after", None),
            getattr(args, "before", None),
            limit=100000,
            project_path=project,
        )
        content = export_csv(events) if args.format == "csv" else json.dumps(events, indent=2)
        if args.output:
            out_path = Path(args.output).resolve()
            if not out_path.parent.is_dir():
                print(f"Error: parent directory does not exist: {out_path.parent}", file=sys.stderr)
                sys.exit(1)
            out_path.write_text(content, encoding="utf-8")
            print(f"Exported {len(events)} events to {out_path}")
        else:
            print(content)
    elif args.command == "verify":
        valid, error = verify_chain(project_path=project)
        print(json.dumps({"status": "valid" if valid else "invalid", "error": error}))
        sys.exit(0 if valid else 1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
