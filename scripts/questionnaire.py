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


EXEMPTION_QUESTIONS = [
    {
        "id": "narrow_procedural_task",
        "text": "Does this AI system perform ONLY narrow procedural tasks (e.g., converting data between formats, sorting documents by metadata, matching records against a fixed template)?",
        "help": "Article 6(3)(a) exempts AI systems that perform narrow procedural tasks. The task must be purely procedural — no decision-making about individuals.",
        "article": "6(3)(a)",
        "weight": {"yes": -30, "no": 5, "unsure": 0},
        "exemption_signal": True,
    },
    {
        "id": "improves_human_output",
        "text": "Does this AI system ONLY improve the result of a previously completed human activity (e.g., grammar checking human-written text, enhancing a human-taken photo, auto-formatting a human-created document)?",
        "help": "Article 6(3)(b) exempts AI that improves previously completed human activities. The human activity must be complete before the AI acts on it.",
        "article": "6(3)(b)",
        "weight": {"yes": -25, "no": 5, "unsure": 0},
        "exemption_signal": True,
    },
    {
        "id": "pattern_detection_no_replacement",
        "text": "Does this AI system detect patterns for human review WITHOUT replacing or substituting the human's own assessment (e.g., flagging anomalies for an analyst, highlighting potential matches for a reviewer)?",
        "help": "Article 6(3)(c) exempts AI that detects patterns without replacing human assessment. The human must make the final determination, not the AI.",
        "article": "6(3)(c)",
        "weight": {"yes": -25, "no": 5, "unsure": 0},
        "exemption_signal": True,
    },
    {
        "id": "preparatory_task",
        "text": "Does this AI system ONLY perform preparatory tasks for a human assessor (e.g., pre-sorting applications, extracting key data points for review, generating summaries for human decision-makers)?",
        "help": "Article 6(3)(d) exempts AI performing preparatory tasks for assessments. The human assessor must still make the substantive decision.",
        "article": "6(3)(d)",
        "weight": {"yes": -20, "no": 5, "unsure": 0},
        "exemption_signal": True,
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


def generate_exemption_assessment(answers: dict) -> dict:
    """Assess whether an AI system qualifies for Article 6(3) exemption.

    Returns:
        likely_exempt: bool
        exemption_type: str or None (which exemption applies)
        documentation: str (text documenting the assessment, as required by Art 6(3))
        confidence: str
    """
    exemptions_triggered = []
    for q in EXEMPTION_QUESTIONS:
        if answers.get(q["id"]) == "yes":
            exemptions_triggered.append(q["article"])

    likely_exempt = len(exemptions_triggered) > 0

    if len(exemptions_triggered) == 0:
        exemption_type = None
        confidence = "low"
    elif len(exemptions_triggered) == 1:
        exemption_type = exemptions_triggered[0]
        confidence = "medium"
    else:
        exemption_type = ", ".join(exemptions_triggered)
        confidence = "high"

    # Build documentation text
    if likely_exempt:
        article_list = ", ".join(f"Article {a}" for a in exemptions_triggered)
        evidence_lines = []
        for q in EXEMPTION_QUESTIONS:
            if answers.get(q["id"]) == "yes":
                evidence_lines.append(
                    f"  - Article {q['article']}: {q['help']}"
                )
        evidence_text = "\n".join(evidence_lines)

        documentation = (
            f"ARTICLE 6(3) EXEMPTION ASSESSMENT\n"
            f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}\n"
            f"\n"
            f"ASSESSMENT OUTCOME: This AI system may qualify for exemption from\n"
            f"high-risk classification under EU AI Act Article 6(3).\n"
            f"\n"
            f"APPLICABLE EXEMPTION(S): {article_list}\n"
            f"\n"
            f"SUPPORTING EVIDENCE:\n"
            f"{evidence_text}\n"
            f"\n"
            f"CONFIDENCE LEVEL: {confidence.upper()}\n"
            f"\n"
            f"CAVEAT: This assessment is generated by automated analysis and does\n"
            f"not constitute legal advice. Article 6(3) exemption claims must be\n"
            f"reviewed by qualified legal counsel before reliance. Providers should\n"
            f"maintain documentation of this assessment as evidence of due diligence."
        )
    else:
        documentation = (
            f"ARTICLE 6(3) EXEMPTION ASSESSMENT\n"
            f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}\n"
            f"\n"
            f"ASSESSMENT OUTCOME: No Article 6(3) exemption criteria were met.\n"
            f"This system does not appear to qualify for exemption from high-risk\n"
            f"classification under EU AI Act Article 6(3).\n"
            f"\n"
            f"CAVEAT: This assessment is generated by automated analysis and does\n"
            f"not constitute legal advice. Results should be reviewed by qualified\n"
            f"legal counsel."
        )

    return {
        "likely_exempt": likely_exempt,
        "exemption_type": exemption_type,
        "documentation": documentation,
        "confidence": confidence,
    }


def format_exemption_text(assessment: dict) -> str:
    """Format exemption assessment for CLI text output."""
    lines = [
        "",
        "=" * 60,
        "  Regula — Article 6(3) Exemption Assessment",
        "=" * 60,
        "",
    ]

    if assessment["likely_exempt"]:
        lines.append(f"  RESULT: Likely exempt ({assessment['exemption_type']})")
        lines.append(f"  Confidence: {assessment['confidence'].upper()}")
    else:
        lines.append("  RESULT: No exemption criteria met")
        lines.append("  Confidence: LOW")

    lines.append("")
    lines.append("  DOCUMENTATION:")
    for line in assessment["documentation"].splitlines():
        lines.append(f"  {line}")
    lines.append("")
    lines.append("=" * 60)
    return "\n".join(lines)


def format_exemption_json(assessment: dict) -> str:
    """Format exemption assessment as JSON."""
    return json.dumps(
        {
            "type": "article_6_3_exemption_assessment",
            "version": "1.0",
            "likely_exempt": assessment["likely_exempt"],
            "exemption_type": assessment["exemption_type"],
            "confidence": assessment["confidence"],
            "documentation": assessment["documentation"],
        },
        indent=2,
    )


def main():
    """CLI entry point — generate or evaluate questionnaire."""
    import argparse

    parser = argparse.ArgumentParser(description="Context-driven AI risk assessment")
    parser.add_argument("--generate", "-g", action="store_true", help="Generate questionnaire (JSON)")
    parser.add_argument("--evaluate", "-e", help="Evaluate answers (JSON file or string)")
    parser.add_argument("--format", "-f", choices=["json", "text"], default="text")
    parser.add_argument("--exemption", "-x", action="store_true", help="Assess Article 6(3) exemption eligibility")
    args = parser.parse_args()

    if args.exemption:
        if not args.evaluate:
            # Print exemption questions only
            lines = [
                "",
                "=" * 60,
                "  Regula — Article 6(3) Exemption Questions",
                "=" * 60,
                "",
                "  Answer the following questions to assess whether this",
                "  AI system may qualify for an Article 6(3) exemption.",
                "",
            ]
            for i, q in enumerate(EXEMPTION_QUESTIONS, 1):
                lines.append(f"  {i}. {q['text']}")
                lines.append(f"     [yes, no, unsure]")
                lines.append(f"     Help: {q['help']}")
                lines.append(f"     Relevant article: Art. {q['article']}")
                lines.append("")
            lines.append("=" * 60)
            print("\n".join(lines))
        else:
            try:
                if Path(args.evaluate).exists():
                    answers = json.loads(Path(args.evaluate).read_text())
                else:
                    answers = json.loads(args.evaluate)
            except (json.JSONDecodeError, OSError) as e:
                print(f"Error parsing answers: {e}", file=sys.stderr)
                sys.exit(1)

            assessment = generate_exemption_assessment(answers)
            if args.format == "json":
                print(format_exemption_json(assessment))
            else:
                print(format_exemption_text(assessment))

    elif args.generate:
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
