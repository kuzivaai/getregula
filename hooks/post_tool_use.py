#!/usr/bin/env python3
"""Regula PostToolUse Hook — Logs completed tool executions with classification."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

try:
    from classify_risk import classify
    from log_event import log_event
except ImportError:
    def classify(text):
        class R:
            tier = type("o", (), {"value": "not_ai"})()
            indicators_matched = []
            applicable_articles = []
            description = ""
            category = ""
        return R()
    def log_event(*a, **k): pass


def main():
    try:
        input_data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    try:
        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {})
        tool_response = input_data.get("tool_response", {})
        session_id = input_data.get("session_id")

        text = f"{tool_name} {json.dumps(tool_input)}"
        result = classify(text)

        event_data = {
            "tool_name": tool_name,
            "tool_input": str(tool_input)[:500],
            "tier": result.tier.value,
        }

        if result.tier.value != "not_ai":
            event_data["indicators"] = result.indicators_matched
            event_data["articles"] = result.applicable_articles
            event_data["description"] = result.description
            event_data["category"] = result.category

        if tool_response:
            event_data["tool_response"] = str(tool_response)[:500]

        log_event("tool_use", event_data, session_id=session_id)
    except Exception:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
