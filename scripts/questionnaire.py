#!/usr/bin/env python3
"""
Regula Questionnaire — Context-Driven Risk Assessment

When pattern-based classification produces ambiguous results (low confidence
or conflicting indicators), this questionnaire gathers context about intended
purpose and deployment to produce a more accurate classification.

Evidence base: appliedAI study found 40% of AI systems cannot be clearly
classified by patterns alone. European Commission missed its Article 6
guidance deadline (February 2026). Questionnaire-driven assessment is the
industry standard approach (Credo AI, Google SAIF, AI Verify).

Questions are derived from EU AI Act Article 6 criteria for high-risk
classification, specifically the two-step test (Annex III area + significant
risk of harm) and Article 6(3) exemptions.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent))

from classify_risk import Classification, RiskTier


# ---------------------------------------------------------------------------
# Question definitions — derived from Article 6 criteria
# ---------------------------------------------------------------------------

QUESTIONS = [
    {
        "id": "autonomous_decisions",
        "text": "Does this system make or materially influence decisions about individuals without human review of each decision?",
        "help": "Article 14 requires human oversight. Systems where humans review every output before action may have lower risk.",
        "weight": {"yes": 30, "no": -20, "unsure": 10},
        "risk_signal": "high_risk",
    },
    {
        "id": "affected_domain",
        "text": "Does this system operate in any of these domains: employment/hiring, credit/finance, education/admissions, healthcare, law enforcement, immigration, critical infrastructure?",
        "help": "These domains are listed in EU AI Act Annex III as areas where AI systems may be classified as high-risk.",
        "weight": {"yes": 25, "no": -15, "unsure": 10},
        "risk_signal": "high_risk",
    },
    {
        "id": "significant_harm",
        "text": "Could errors or failures in this system cause significant harm to individuals' health, safety, or fundamental rights?",
        "help": "Article 6 requires the system to pose a 'significant risk of harm' to qualify as high-risk, beyond just operating in an Annex III area.",
        "weight": {"yes": 25, "no": -15, "unsure": 10},
        "risk_signal": "high_risk",
    },
    {
        "id": "narrow_procedural",
        "text": "Does this system perform only narrow procedural tasks (e.g., data formatting, document sorting, pattern matching for human review)?",
        "help": "Article 6(3)(a) exempts systems that perform narrow procedural tasks from high-risk classification.",
        "weight": {"yes": -25, "no": 10, "unsure": 0},
        "risk_signal": "exemption",
    },
    {
        "id": "improves_human_activity",
        "text": "Does this system only improve the result of a previously completed human activity (e.g., grammar check on human-written text)?",
        "help": "Article 6(3)(b) exempts systems that improve previously completed human activities.",
        "weight": {"yes": -20, "no": 5, "unsure": 0},
        "risk_signal": "exemption",
    },
    {
        "id": "public_facing",
        "text": "Will individuals be informed they are interacting with an AI system?",
        "help": "Article 50 requires transparency for chatbots, emotion recognition, deepfakes, and biometric systems.",
        "weight": {"yes": -5, "no": 15, "unsure": 5},
        "risk_signal": "transparency",
    },
    {
        "id": "biometric_data",
        "text": "Does this system process biometric data (face, fingerprint, voice, gait)?",
        "help": "Biometric processing appears in both Annex III Category 1 and Article 5 prohibited practices depending on context.",
        "weight": {"yes": 20, "no": -5, "unsure": 10},
        "risk_signal": "high_risk",
    },
    {
        "id": "deployment_eu",
        "text": "Will this system be deployed in the EU or affect EU residents?",
        "help": "The EU AI Act applies to systems placed on the EU market or whose output is used in the EU.",
        "weight": {"yes": 10, "no": -10, "unsure": 5},
        "risk_signal": "jurisdiction",
    },
]


def generate_questionnaire(
    pattern_result: Optional[Classification] = None,
) -> dict:
    """Generate a questionnaire for context-driven risk assessment.

    Returns a dict with questions and the pattern-based result for context.
    """
    context = None
    if pattern_result:
        context = {
            "pattern_tier": pattern_result.tier.value,
            "pattern_confidence": pattern_result.confidence_score,
            "pattern_indicators": pattern_result.indicators_matched,
            "pattern_description": pattern_result.description,
        }

    return {
        "type": "risk_assessment_questionnaire",
        "version": "1.0",
        "context": context,
        "instructions": (
            "Regula detected AI patterns but cannot determine the risk tier "
            "from code alone. The EU AI Act (Article 6) requires assessment "
            "of intended purpose and deployment context. Please answer the "
            "following questions to produce a more accurate classification."
        ),
        "questions": [
            {
                "id": q["id"],
                "text": q["text"],
                "help": q["help"],
                "options": ["yes", "no", "unsure"],
            }
            for q in QUESTIONS
        ],
    }


def evaluate_questionnaire(
    answers: dict,
    pattern_result: Optional[Classification] = None,
) -> Classification:
    """Evaluate questionnaire answers to produce a classification.

    Args:
        answers: dict mapping question ID to "yes", "no", or "unsure"
        pattern_result: optional pattern-based classification for context
    """
    # Start from pattern-based score if available
    base_score = 0
    if pattern_result:
        base_score = pattern_result.confidence_score

    # Calculate questionnaire adjustment
    adjustment = 0
    for q in QUESTIONS:
        answer = answers.get(q["id"], "unsure")
        adjustment += q["weight"].get(answer, 0)

    # Combine: pattern score contributes 30%, questionnaire 70%
    if pattern_result and pattern_result.tier != RiskTier.NOT_AI:
        pattern_weight = base_score * 0.3
    else:
        pattern_weight = 0

    # Questionnaire score: map adjustment to 0-100
    # Max possible positive adjustment: ~130 (all yes on risk, all no on exemptions)
    questionnaire_score = max(0, min(100, 50 + int(adjustment * 0.6)))
    combined_score = int(pattern_weight + questionnaire_score * 0.7)

    # Determine tier from combined score
    if combined_score >= 70:
        tier = RiskTier.HIGH_RISK
        action = "allow_with_requirements"
        articles = ["9", "10", "11", "12", "13", "14", "15"]
        category = "Questionnaire Assessment"
        description = "Classified as high-risk based on intended purpose and deployment context"
    elif combined_score >= 40:
        tier = RiskTier.LIMITED_RISK
        action = "allow_with_transparency"
        articles = ["50"]
        category = "Questionnaire Assessment"
        description = "Classified as limited-risk — transparency obligations apply"
    else:
        tier = RiskTier.MINIMAL_RISK
        action = "allow"
        articles = []
        category = "Questionnaire Assessment"
        description = "Classified as minimal-risk based on context assessment"

    # Build indicator list from answers
    indicators = []
    if answers.get("autonomous_decisions") == "yes":
        indicators.append("autonomous_decisions")
    if answers.get("affected_domain") == "yes":
        indicators.append("regulated_domain")
    if answers.get("significant_harm") == "yes":
        indicators.append("significant_harm_potential")
    if answers.get("biometric_data") == "yes":
        indicators.append("biometric_processing")

    return Classification(
        tier=tier,
        confidence="high",
        indicators_matched=indicators,
        applicable_articles=articles,
        category=category,
        description=description,
        action=action,
        message=f"QUESTIONNAIRE RESULT: {description} (score: {combined_score}/100)",
        confidence_score=combined_score,
    )


def format_questionnaire_cli(questionnaire: dict) -> str:
    """Format questionnaire for CLI output."""
    lines = [
        "",
        "=" * 60,
        "  Regula — Context-Driven Risk Assessment",
        "=" * 60,
        "",
        f"  {questionnaire['instructions']}",
        "",
    ]

    if questionnaire.get("context"):
        ctx = questionnaire["context"]
        lines.append(f"  Pattern-based result: {ctx['pattern_tier'].upper().replace('_', '-')}")
        lines.append(f"  Pattern confidence: {ctx['pattern_confidence']}/100")
        lines.append("")

    for i, q in enumerate(questionnaire["questions"], 1):
        lines.append(f"  {i}. {q['text']}")
        lines.append(f"     [{', '.join(q['options'])}]")
        lines.append(f"     Help: {q['help']}")
        lines.append("")

    lines.append("=" * 60)
    return "\n".join(lines)


def main():
    """CLI entry point — generate or evaluate questionnaire."""
    import argparse

    parser = argparse.ArgumentParser(description="Context-driven AI risk assessment")
    parser.add_argument("--generate", "-g", action="store_true", help="Generate questionnaire (JSON)")
    parser.add_argument("--evaluate", "-e", help="Evaluate answers (JSON file or string)")
    parser.add_argument("--format", "-f", choices=["json", "text"], default="text")
    args = parser.parse_args()

    if args.generate:
        q = generate_questionnaire()
        if args.format == "json":
            print(json.dumps(q, indent=2))
        else:
            print(format_questionnaire_cli(q))

    elif args.evaluate:
        try:
            if Path(args.evaluate).exists():
                answers = json.loads(Path(args.evaluate).read_text())
            else:
                answers = json.loads(args.evaluate)
        except (json.JSONDecodeError, OSError) as e:
            print(f"Error parsing answers: {e}", file=sys.stderr)
            sys.exit(1)

        result = evaluate_questionnaire(answers)
        if args.format == "json":
            print(result.to_json())
        else:
            print(result.message)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
