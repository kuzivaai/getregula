#!/usr/bin/env python3
"""Regula PostToolUse Hook - Logs completed tool executions"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

try:
    from log_event import log_event
except ImportError:
    def log_event(*a, **k): pass


def main():
    try:
        input_data = json.load(sys.stdin)
        log_event("tool_use", {
            "tool_name": input_data.get("tool_name"),
            "tool_input": str(input_data.get("tool_input", {}))[:500]
        })
    except:
        pass
    sys.exit(0)


if __name__ == "__main__":
    main()
