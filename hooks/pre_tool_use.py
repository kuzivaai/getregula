#!/usr/bin/env python3
"""Regula PreToolUse Hook — Intercepts and classifies tool calls."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

try:
    from classify_risk import classify, RiskTier, is_training_activity, ISO_42001_MAP
    from log_event import log_event
    from credential_check import check_secrets, has_high_confidence_secret, format_secret_warning
except ImportError:
    def classify(text):
        class R:
            tier = type("o", (), {"value": "minimal_risk"})()
            indicators_matched = []
            applicable_articles = []
            description = ""
            category = ""
            action = "allow"
            exceptions = None
        return R()
    class RiskTier:
        PROHIBITED = type("o", (), {"value": "prohibited"})()
    def log_event(*a, **k): pass
    def check_secrets(text): return []
    def has_high_confidence_secret(text): return False
    def format_secret_warning(findings): return ""


def _build_prohibited_message(result) -> str:
    articles = result.applicable_articles
    article_str = articles[0] if articles else "5"
    indicators = ", ".join(result.indicators_matched) if result.indicators_matched else "unknown"

    lines = [
        "PROHIBITED AI PRACTICE — ACTION BLOCKED",
        "",
        "This operation matches a pattern associated with a prohibited",
        f"practice under EU AI Act Article {article_str}.",
        "",
        f"Prohibition: {result.description or 'Prohibited AI practice'}",
        f"Pattern detected: {indicators}",
    ]

    # Include conditions if available
    conditions = getattr(result, "conditions", None)
    if conditions:
        lines += ["", f"Conditions: {conditions}"]

    # Include exceptions if available — this is legally important
    exceptions = getattr(result, "exceptions", None)
    if exceptions:
        lines += ["", f"Exceptions: {exceptions}"]

    lines += [
        "",
        "IMPORTANT: This is a pattern-based risk indication, not a legal",
        "determination. The EU AI Act requires contextual assessment of",
        "intended purpose. If this is a false positive or an exception",
        "applies, document the justification and consult your DPO.",
        "",
        "Penalties for actual prohibited practices: up to EUR 35 million",
        "or 7% of global annual turnover.",
    ]

    return "\n".join(lines)


def _build_high_risk_message(result) -> str:
    indicators = ", ".join(result.indicators_matched) if result.indicators_matched else "unknown"

    return "\n".join([
        "HIGH-RISK AI SYSTEM INDICATORS DETECTED",
        "",
        f"Category: {result.category or 'High-Risk'}",
        f"Description: {result.description or 'High-risk AI system'}",
        f"Patterns: {indicators}",
        "",
        "This operation matches patterns associated with a high-risk AI",
        "system under EU AI Act Annex III. Whether Articles 9-15 apply",
        "depends on whether the system poses a significant risk of harm",
        "(Article 6). Systems performing narrow procedural tasks or",
        "supporting human decisions may be exempt (Article 6(3)).",
        "",
        "If this IS a high-risk system, these requirements apply",
        "(effective 2 August 2026):",
        "  Art 9:  Risk management — ISO 42001: 6.1, A.5.3",
        "  Art 10: Data governance — ISO 42001: A.6.6",
        "  Art 11: Technical docs — ISO 42001: A.6.4, 7.5",
        "  Art 12: Event logging — ISO 42001: A.6.10",
        "  Art 13: Transparency — ISO 42001: A.6.8",
        "  Art 14: Human oversight — ISO 42001: A.6.3",
        "  Art 15: Accuracy/security — ISO 42001: A.6.9",
        "",
        "This action has been logged to the audit trail.",
    ])


def _build_limited_risk_message(result) -> str:
    return "\n".join([
        "Limited-Risk AI System",
        "",
        f"Description: {result.description or 'Limited-risk AI system'}",
        "Transparency obligation (Article 50): Ensure users are informed",
        "they are interacting with an AI system.",
        "",
        "This action has been logged.",
    ])


def main():
    try:
        input_data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})
    session_id = input_data.get("session_id")
    text = f"{tool_name} {json.dumps(tool_input)}"
    response = {"hookSpecificOutput": {"hookEventName": "PreToolUse"}}

    # --- Secret detection (runs first, before AI risk classification) ---
    secret_findings = check_secrets(text)
    if secret_findings:
        high_confidence = [f for f in secret_findings if f.confidence == "high"]

        try:
            log_event("secret_detected", {
                "count": len(secret_findings),
                "high_confidence": len(high_confidence),
                "patterns": [f.pattern_name for f in secret_findings],
                "tool_name": tool_name,
            }, session_id=session_id)
        except Exception:
            pass

        if high_confidence:
            # Block: high-confidence credential in tool input
            warning = format_secret_warning(secret_findings)
            response["hookSpecificOutput"]["permissionDecision"] = "deny"
            response["hookSpecificOutput"]["permissionDecisionReason"] = warning
            print(json.dumps(response))
            sys.exit(2)
        else:
            # Warn: medium-confidence patterns only
            warning = format_secret_warning(secret_findings)
            response["hookSpecificOutput"]["additionalContext"] = warning
            # Don't return yet — continue to AI risk classification

    # --- AI risk classification ---
    result = classify(text)

    if result.tier == RiskTier.PROHIBITED or result.tier.value == "prohibited":
        reason = _build_prohibited_message(result)
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
            }, session_id=session_id)
        except Exception:
            pass

        print(json.dumps(response))
        sys.exit(2)

    if result.tier.value == "high_risk":
        context = _build_high_risk_message(result)
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
            }, session_id=session_id)
        except Exception:
            pass

    elif result.tier.value == "limited_risk":
        context = _build_limited_risk_message(result)
        response["hookSpecificOutput"]["permissionDecision"] = "allow"
        response["hookSpecificOutput"]["additionalContext"] = context

        try:
            log_event("classification", {
                "tier": "limited_risk",
                "indicators": result.indicators_matched,
                "description": result.description,
                "tool_name": tool_name,
            }, session_id=session_id)
        except Exception:
            pass

    else:
        response["hookSpecificOutput"]["permissionDecision"] = "allow"

    # --- GPAI awareness (non-blocking, informational) ---
    try:
        if is_training_activity(text):
            gpai_note = (
                "\n\nGPAI Note: This operation involves model training or fine-tuning. "
                "If you are building a general-purpose AI model (trained with >10^23 FLOPs) "
                "or making a significant modification (>1/3 of original compute), GPAI "
                "transparency obligations apply (EU AI Act Articles 53-55, in force since "
                "2 August 2025). Obligations include: technical documentation, training data "
                "summary (Commission template), copyright policy, and downstream provider "
                "notification. Most fine-tuning (LoRA, adapters) does NOT meet the 1/3 "
                "threshold and does NOT create GPAI provider obligations."
            )
            existing = response["hookSpecificOutput"].get("additionalContext", "")
            response["hookSpecificOutput"]["additionalContext"] = existing + gpai_note if existing else gpai_note.strip()
    except Exception:
        pass

    print(json.dumps(response))
    sys.exit(0)


if __name__ == "__main__":
    main()
