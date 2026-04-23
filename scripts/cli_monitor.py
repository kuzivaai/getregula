#!/usr/bin/env python3
# regula-ignore
"""
Regula Monitor CLI — runtime monitoring commands.

Subcommands: status, report, verify, prune, export.
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from log_event import compute_hash
from monitor import _get_monitor_dir


def _read_all_events(system_id: str, monitor_dir: str = None) -> list:
    """Read all events from all log files for a system."""
    log_dir = _get_monitor_dir(system_id, monitor_dir)
    events = []
    for f in sorted(log_dir.glob("monitor_*.jsonl")):
        for line in f.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                events.append(json.loads(line))
    return events


def _verify_chain(events: list) -> tuple:
    """Verify hash chain integrity. Returns (valid, message)."""
    if not events:
        return True, "No events to verify"
    prev = "0" * 64
    for i, event in enumerate(events):
        if event.get("previous_hash") != prev:
            return False, f"Chain broken at event {i}: previous_hash mismatch"
        expected = compute_hash(event, prev)
        if event.get("current_hash") != expected:
            return False, f"Chain broken at event {i}: current_hash mismatch"
        prev = event["current_hash"]
    return True, f"Chain valid: {len(events)} events verified"


def cmd_monitor_verify(args) -> dict:
    """Verify hash chain integrity for a system's monitor logs."""
    events = _read_all_events(args.system_id, getattr(args, "monitor_dir", None))
    valid, message = _verify_chain(events)
    result = {
        "system_id": args.system_id,
        "chain_valid": valid,
        "chain_message": message,
        "event_count": len(events),
    }
    if getattr(args, "format", "text") == "json":
        return result
    status = "PASS" if valid else "FAIL"
    print(f"  {status}  {message}")
    return result


def cmd_monitor_report(args) -> dict:
    """Generate compliance report from runtime logs."""
    events = _read_all_events(args.system_id, getattr(args, "monitor_dir", None))

    inferences = [e for e in events if e.get("event_type") == "inference"]
    errors = [e for e in events if e.get("status") == "error"]
    summaries = [e for e in events if e.get("event_type") == "session_summary"]
    consequential = [e for e in inferences if e.get("consequential")]
    reviewed = [e for e in inferences
                if e.get("human_oversight", {}).get("performed")]

    latencies = [e["latency_ms"] for e in inferences if e.get("latency_ms")]
    models = sorted({e.get("model") for e in inferences if e.get("model")})

    safety_counts = {}
    for e in events:
        safety = e.get("safety", {})
        if safety:
            for key, val in safety.items():
                if val:
                    safety_counts[key] = safety_counts.get(key, 0) + 1

    total_non_summary = len([e for e in events if e.get("event_type") != "session_summary"])
    result = {
        "system_id": args.system_id,
        "total_events": len(events),
        "total_inferences": len(inferences),
        "total_errors": len(errors),
        "error_rate": round(len(errors) / max(total_non_summary, 1), 3),
        "sessions": len(summaries),
        "models_used": models,
        "consequential_calls": len(consequential),
        "human_reviewed": len(reviewed),
        "oversight_rate": round(len(reviewed) / max(len(consequential), 1), 3) if consequential else None,
        "avg_latency_ms": int(sum(latencies) / max(len(latencies), 1)) if latencies else 0,
        "p95_latency_ms": int(sorted(latencies)[int(len(latencies) * 0.95)]) if latencies else 0,
        "safety_events": safety_counts,
    }

    if getattr(args, "format", "text") == "json":
        return result

    print(f"\nRegula Monitor Report: {args.system_id}")
    print(f"{'=' * 50}")
    print(f"  Events:      {result['total_events']}")
    print(f"  Inferences:  {result['total_inferences']}")
    print(f"  Errors:      {result['total_errors']} ({result['error_rate']:.1%})")
    print(f"  Sessions:    {result['sessions']}")
    print(f"  Models:      {', '.join(models) if models else 'none'}")
    if latencies:
        print(f"  Latency:     avg {result['avg_latency_ms']}ms, p95 {result['p95_latency_ms']}ms")
    if consequential:
        print(f"  Consequential calls: {len(consequential)}")
        print(f"  Human reviewed:      {len(reviewed)} ({result['oversight_rate']:.0%})")
    if safety_counts:
        print(f"  Safety events: {safety_counts}")
    print()
    return result


def cmd_monitor_status(args) -> dict:
    """Show monitored systems and log sizes."""
    base = Path(os.environ.get(
        "REGULA_MONITOR_DIR",
        Path.home() / ".regula" / "monitor",
    ))
    if getattr(args, "monitor_dir", None):
        base = Path(args.monitor_dir)

    systems = []
    if base.exists():
        for d in sorted(base.iterdir()):
            if d.is_dir():
                files = list(d.glob("monitor_*.jsonl"))
                total_bytes = sum(f.stat().st_size for f in files)
                event_count = sum(
                    sum(1 for line in f.read_text().splitlines() if line.strip())
                    for f in files
                )
                systems.append({
                    "system_id": d.name,
                    "log_files": len(files),
                    "total_bytes": total_bytes,
                    "event_count": event_count,
                })

    result = {"systems": systems}
    if getattr(args, "format", "text") == "json":
        return result

    if not systems:
        print("No monitored systems found.")
    else:
        print(f"\n{'System':<30} {'Files':<8} {'Events':<10} {'Size':<10}")
        print("-" * 58)
        for s in systems:
            size = f"{s['total_bytes'] / 1024:.1f}KB" if s['total_bytes'] > 1024 else f"{s['total_bytes']}B"
            print(f"{s['system_id']:<30} {s['log_files']:<8} {s['event_count']:<10} {size:<10}")
    print()
    return result


def cmd_monitor_prune(args) -> dict:
    """Delete monitor logs older than retention period."""
    retention = getattr(args, "months", 6)
    log_dir = _get_monitor_dir(args.system_id, getattr(args, "monitor_dir", None))

    now = datetime.now(timezone.utc)
    deleted = []
    for f in sorted(log_dir.glob("monitor_*.jsonl")):
        try:
            parts = f.stem.split("_", 1)
            if len(parts) == 2:
                file_date = datetime.strptime(parts[1], "%Y-%m").replace(tzinfo=timezone.utc)
                age_months = (now.year - file_date.year) * 12 + (now.month - file_date.month)
                if age_months > retention:
                    f.unlink()
                    deleted.append(f.name)
        except (ValueError, IndexError):
            continue

    result = {"system_id": args.system_id, "deleted": deleted, "retention_months": retention}
    if getattr(args, "format", "text") == "json":
        return result
    if deleted:
        print(f"Pruned {len(deleted)} log files older than {retention} months")
    else:
        print(f"No log files older than {retention} months")
    return result


def cmd_monitor_export(args) -> dict:
    """Export monitor logs as CSV."""
    import csv
    import io

    events = _read_all_events(args.system_id, getattr(args, "monitor_dir", None))
    if not events:
        print("No events to export.")
        return {"exported": 0}

    output = io.StringIO()
    fields = ["event_id", "timestamp", "event_type", "system_id", "provider",
              "model", "input_tokens", "output_tokens", "latency_ms",
              "status", "error", "consequential"]
    writer = csv.DictWriter(output, fieldnames=fields, extrasaction="ignore")
    writer.writeheader()
    for e in events:
        writer.writerow(e)

    csv_text = output.getvalue()
    out_file = getattr(args, "output", None)
    if out_file:
        Path(out_file).write_text(csv_text, encoding="utf-8")
        print(f"Exported {len(events)} events to {out_file}")
    else:
        print(csv_text)
    return {"exported": len(events)}
