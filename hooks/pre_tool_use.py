#!/usr/bin/env python3
"""Regula PreToolUse Hook - Intercepts and classifies tool calls"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

try:
    from classify_risk import classify, RiskTier
    from log_event import log_event
except ImportError:
    def classify(text):
        class R:
            tier = type('o', (), {'value': 'minimal_risk'})()
            indicators_matched = []
            applicable_articles = []
            description = ""
        return R()
    class RiskTier:
        PROHIBITED = type('o', (), {'value': 'prohibited'})()
    def log_event(*a, **k): pass


def main():
    try:
        input_data = json.load(sys.stdin)
    except:
        sys.exit(0)
    
    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})
    text = f"{tool_name} {json.dumps(tool_input)}"
    
    result = classify(text)
    response = {"hookSpecificOutput": {"hookEventName": "PreToolUse"}}
    
    if result.tier == RiskTier.PROHIBITED or result.tier.value == "prohibited":
        response["hookSpecificOutput"]["permissionDecision"] = "deny"
        response["hookSpecificOutput"]["permissionDecisionReason"] = f"🛑 PROHIBITED: {result.description}"
        try:
            log_event("blocked", {"tier": "prohibited", "indicators": result.indicators_matched})
        except:
            pass
        print(json.dumps(response))
        sys.exit(2)
    
    response["hookSpecificOutput"]["permissionDecision"] = "allow"
    if result.tier.value == "high_risk":
        response["hookSpecificOutput"]["additionalContext"] = f"⚠️ HIGH-RISK: Articles {', '.join(result.applicable_articles)} apply"
    
    print(json.dumps(response))
    sys.exit(0)


if __name__ == "__main__":
    main()
