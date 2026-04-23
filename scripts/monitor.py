#!/usr/bin/env python3
# regula-ignore
"""
Regula Runtime Monitor — Article 12 logging for AI applications.

Provides MonitorSession and Trace for developers to instrument LLM calls
in their own applications. Produces hash-chained JSONL audit logs that
map to EU AI Act Articles 9, 12, 13, 14, and 50.

Limitation: self-attesting evidence. The same developer who controls
the application controls the logs. Supplement with RFC 3161 external
timestamps for audit-grade independence.
"""

import json
import os
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.insert(0, str(Path(__file__).parent))

from log_event import compute_hash, _read_last_hash, _lock_file, _unlock_file


def _extract_response(response) -> dict:
    """Duck-type across provider response formats.

    Handles three input types:
    - Provider SDK objects (OpenAI, Anthropic): use getattr()
    - Raw dicts (from HTTP clients): use dict access
    - Unknown objects: graceful fallback to nulls
    """
    data: Dict[str, Any] = {}

    if isinstance(response, dict):
        data["model"] = response.get("model")
        usage = response.get("usage", {})
        inp = usage.get("input_tokens")
        data["input_tokens"] = inp if inp is not None else usage.get("prompt_tokens")
        out = usage.get("output_tokens")
        data["output_tokens"] = out if out is not None else usage.get("completion_tokens")
        data["provider"] = response.get("provider", "unknown")
        return data

    data["model"] = getattr(response, "model", None)

    usage = getattr(response, "usage", None)
    if usage:
        inp = getattr(usage, "input_tokens", None)
        data["input_tokens"] = inp if inp is not None else getattr(usage, "prompt_tokens", None)
        out = getattr(usage, "output_tokens", None)
        data["output_tokens"] = out if out is not None else getattr(usage, "completion_tokens", None)

    module = type(response).__module__ or ""
    if "openai" in module:
        data["provider"] = "openai"
    elif "anthropic" in module:
        data["provider"] = "anthropic"
    elif "google" in module:
        data["provider"] = "google"
    else:
        data["provider"] = getattr(response, "provider", "unknown")

    return data


def _get_monitor_dir(system_id: str, base_dir: Optional[str] = None) -> Path:
    """Return the monitor log directory for a system."""
    if base_dir:
        d = Path(base_dir) / system_id
    else:
        d = Path(os.environ.get(
            "REGULA_MONITOR_DIR",
            Path.home() / ".regula" / "monitor",
        )) / system_id
    d.mkdir(parents=True, exist_ok=True)
    return d


def _get_monitor_file(system_id: str, base_dir: Optional[str] = None) -> Path:
    """Return the current month's log file for a system."""
    d = _get_monitor_dir(system_id, base_dir)
    return d / f"monitor_{datetime.now(timezone.utc).strftime('%Y-%m')}.jsonl"


class Trace:
    """Context manager for timing and recording a single LLM call."""

    def __init__(self, session: "MonitorSession"):
        self._session = session
        self._start: float = 0.0
        self._recorded = False

    def __enter__(self):
        self._start = time.monotonic()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self._recorded and exc_type is not None:
            self.record_error(exc_val)
        return False

    def record(self, response, **overrides) -> dict:
        """Record a successful LLM call."""
        elapsed_ms = int((time.monotonic() - self._start) * 1000)
        extracted = _extract_response(response)

        event = {
            "event_id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": "inference",
            "system_id": self._session.system_id,
            "system_version": self._session.system_version,
            "environment": self._session.environment,
            "deployment_id": self._session.deployment_id,
            "provider": extracted.get("provider"),
            "model": extracted.get("model"),
            "model_version": extracted.get("model_version"),
            "input_tokens": extracted.get("input_tokens"),
            "output_tokens": extracted.get("output_tokens"),
            "latency_ms": elapsed_ms,
            "status": "success",
            "error": None,
            "consequential": self._session.defaults.get("consequential", False),
            "human_oversight": {
                "required": self._session.defaults.get("human_oversight_required", False),
            },
            "transparency": {
                "user_informed_ai": self._session.defaults.get("user_informed_ai", False),
            },
            "domain": self._session.defaults.get("domain"),
        }

        if "consequential" in overrides:
            event["consequential"] = overrides["consequential"]
        if "human_oversight" in overrides:
            event["human_oversight"].update(overrides["human_oversight"])
        if "transparency" in overrides:
            event["transparency"].update(overrides["transparency"])
        if "safety" in overrides:
            event["safety"] = overrides["safety"]
        if "tags" in overrides:
            event["tags"] = overrides["tags"]
        if "metadata" in overrides:
            event["metadata"] = overrides["metadata"]

        self._session._append_event(event)
        self._recorded = True
        return event

    def record_error(self, exception: Exception) -> dict:
        """Record a failed LLM call."""
        elapsed_ms = int((time.monotonic() - self._start) * 1000)
        event = {
            "event_id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": "error",
            "system_id": self._session.system_id,
            "system_version": self._session.system_version,
            "environment": self._session.environment,
            "deployment_id": self._session.deployment_id,
            "provider": None,
            "model": None,
            "model_version": None,
            "input_tokens": None,
            "output_tokens": None,
            "latency_ms": elapsed_ms,
            "status": "error",
            "error": f"{type(exception).__name__}: {exception}",
            "consequential": self._session.defaults.get("consequential", False),
            "human_oversight": {
                "required": self._session.defaults.get("human_oversight_required", False),
            },
            "transparency": {
                "user_informed_ai": self._session.defaults.get("user_informed_ai", False),
            },
            "domain": self._session.defaults.get("domain"),
        }
        self._session._append_event(event)
        self._recorded = True
        return event

    def end(self):
        """Explicit end for non-context-manager usage."""
        pass


class MonitorSession:
    """Runtime monitoring session for an AI system.

    Tier 2 defaults are set at creation and apply to all events
    unless overridden per-event (Tier 3).
    """

    def __init__(
        self,
        system_id: str,
        system_version: str = "0.0.0",
        environment: str = "development",
        deployment_id: Optional[str] = None,
        consequential: bool = False,
        human_oversight_required: bool = False,
        user_informed_ai: bool = False,
        domain: Optional[str] = None,
        retention_months: int = 6,
        monitor_dir: Optional[str] = None,
    ):
        self.system_id = system_id
        self.system_version = system_version
        self.environment = environment
        self.deployment_id = deployment_id
        self.retention_months = retention_months
        self._monitor_dir = monitor_dir

        self.defaults = {
            "consequential": consequential,
            "human_oversight_required": human_oversight_required,
            "user_informed_ai": user_informed_ai,
            "domain": domain,
        }

        self.session_id = str(uuid.uuid4())
        self._started = datetime.now(timezone.utc).isoformat()
        self._events: List[dict] = []

    def trace(self) -> Trace:
        """Create a trace context manager for timing an LLM call."""
        return Trace(self)

    def start_trace(self) -> Trace:
        """Create a trace without context manager."""
        t = Trace(self)
        t._start = time.monotonic()
        return t

    def _append_event(self, event: dict) -> None:
        """Write event to log file with hash chain and file locking."""
        log_file = _get_monitor_file(self.system_id, self._monitor_dir)

        with open(log_file, "a", encoding="utf-8") as f:
            _lock_file(f)
            try:
                previous_hash = _read_last_hash(log_file)
                event["previous_hash"] = previous_hash
                event["current_hash"] = compute_hash(event, previous_hash)
                f.write(json.dumps(event, sort_keys=True) + "\n")
                f.flush()
            finally:
                _unlock_file(f)

        self._events.append(event)

    def close(self) -> dict:
        """End the session and write a summary record."""
        ended = datetime.now(timezone.utc).isoformat()
        inferences = [e for e in self._events if e.get("event_type") == "inference"]
        errors = [e for e in self._events if e.get("status") == "error"]
        overrides = [e for e in self._events
                     if e.get("human_oversight", {}).get("action") in
                     ("modified", "rejected")]
        latencies = [e["latency_ms"] for e in inferences if e.get("latency_ms")]
        models = list({e.get("model") for e in inferences if e.get("model")})

        safety_events = {}
        for e in self._events:
            safety = e.get("safety", {})
            if safety:
                for key in ("pii_detected", "guardrail_triggered"):
                    if safety.get(key):
                        safety_events[key] = safety_events.get(key, 0) + 1

        total = len(self._events)
        summary = {
            "event_type": "session_summary",
            "system_id": self.system_id,
            "session_id": self.session_id,
            "started": self._started,
            "ended": ended,
            "total_inferences": len(inferences),
            "total_errors": len(errors),
            "error_rate": round(len(errors) / max(total, 1), 3),
            "human_overrides": len(overrides),
            "models_used": sorted(models),
            "avg_latency_ms": int(sum(latencies) / max(len(latencies), 1)) if latencies else 0,
            "p95_latency_ms": int(sorted(latencies)[int(len(latencies) * 0.95)] if latencies else 0),
            "safety_events": safety_events,
        }

        self._append_event(summary)
        return summary
