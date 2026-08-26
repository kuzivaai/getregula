#!/usr/bin/env python3
"""The versioned JSON output envelope — single source of truth.

Every JSON-emitting surface (CLI ``--format json``, the local API server)
must build its envelope HERE. The format is a compatibility contract
(see AGENTS.md: do not change it); before July 2026
it was duplicated byte-for-byte in cli.py and api_server.py, which made
that rule unenforceable — a version bump in one file would silently not
apply to the other.
"""
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from constants import VERSION

ENVELOPE_FORMAT_VERSION = "1.0"


def build_envelope(command: str, data, exit_code: int = 0) -> dict:
    """Build the standard JSON envelope dict."""
    return {
        "format_version": ENVELOPE_FORMAT_VERSION,
        "regula_version": VERSION,
        "command": command,
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "exit_code": exit_code,
        "data": data,
    }
