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
            category = ""
            action = "allow"
        return R()
    class RiskTier:
        PROHIBITED = type('o', (), {'value': 'prohibited'})()
    def log_event(*a, **k): pass


PROHIBITED_MESSAGE = """🛑 PROHIBITED AI PRACTICE — ACTION BLOCKED

This operation matches a prohibited practice under EU AI Act Article 5.

Specific prohibition: {article}
Description: {description}
Indicator detected: {indicators}

This action CANNOT proceed. The EU AI Act prohibits this practice entirely,
with penalties up to €35 million or 7% of global annual turnover.

If you believe this classification is incorrect, contact your DPO for review."""


HIGH_RISK_MESSAGE = """⚠️ HIGH-RISK AI SYSTEM DETECTED

This operation involves a high-risk AI system under EU AI Act Annex III.

Category: {category}
Description: {description}
Indicators: {indicators}

Applicable Requirements (effective 2 August 2026):
• Article 9: Implement risk management system
• Article 10: Ensure training data is representative and bias-examined
• Article 11: Maintain technical documentation (Annex IV)
• Article 12: Enable automatic logging of decisions
• Article 13: Provide transparency to affected persons
• Article 14: Implement human oversight mechanism
• Article 15: Validate accuracy and implement security measures

This action has been logged. Proceed with compliance requirements in mind."""


LIMITED_RISK_MESSAGE = """ℹ️ Limited-Risk AI System

Description: {description}
Transparency obligation (Article 50): Ensure users are informed of AI involvement.

This action has been logged."""


def main():
    try:
        input_data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})
    text = f"{tool_name} {json.dumps(tool_input)}"

    result = classify(text)
    response = {"hookSpecificOutput": {"hookEventName": "PreToolUse"}}

    if result.tier == RiskTier.PROHIBITED or result.tier.value == "prohibited":
        articles = result.applicable_articles
        article_str = articles[0] if articles else "5"
        indicators = ", ".join(result.indicators_matched) if result.indicators_matched else "unknown"

        reason = PROHIBITED_MESSAGE.format(
            article=f"Article {article_str}",
            description=result.description or "Prohibited AI practice",
            indicators=indicators,
        )

        response["hookSpecificOutput"]["permissionDecision"] = "deny"
        response["hookSpecificOutput"]["permissionDecisionReason"] = reason

        try:
            log_event("blocked", {
                "tier": "prohibited",
                "indicators": result.indicators_matched,
                "articles": result.applicable_articles,
                "description": result.description,
                "tool_name": tool_name,
                "tool_input": str(tool_input)[:500],
            })
        except Exception:
            pass

        print(json.dumps(response))
        sys.exit(2)

    if result.tier.value == "high_risk":
        indicators = ", ".join(result.indicators_matched) if result.indicators_matched else "unknown"
        context = HIGH_RISK_MESSAGE.format(
            category=result.category or "High-Risk",
            description=result.description or "High-risk AI system",
            indicators=indicators,
        )
        response["hookSpecificOutput"]["permissionDecision"] = "allow"
        response["hookSpecificOutput"]["additionalContext"] = context

        try:
            log_event("classification", {
                "tier": "high_risk",
                "indicators": result.indicators_matched,
                "articles": result.applicable_articles,
                "category": result.category,
                "description": result.description,
                "tool_name": tool_name,
            })
        except Exception:
            pass

    elif result.tier.value == "limited_risk":
        context = LIMITED_RISK_MESSAGE.format(
            description=result.description or "Limited-risk AI system",
        )
        response["hookSpecificOutput"]["permissionDecision"] = "allow"
        response["hookSpecificOutput"]["additionalContext"] = context

        try:
            log_event("classification", {
                "tier": "limited_risk",
                "indicators": result.indicators_matched,
                "description": result.description,
                "tool_name": tool_name,
            })
        except Exception:
            pass

    else:
        response["hookSpecificOutput"]["permissionDecision"] = "allow"

    print(json.dumps(response))
    sys.exit(0)


if __name__ == "__main__":
    main()
