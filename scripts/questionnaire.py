# regula-ignore — risk questionnaire prose describes risk domains to elicit context from the user
#!/usr/bin/env python3
"""EU AI Act questionnaire adapter for the canonical decision kernel."""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent))

from classify_risk import Classification, RiskTier
from decision_kernel import DecisionInputError, DecisionKernel, fact


# ---------------------------------------------------------------------------
# Question definitions mapped to named facts in the decision model
# ---------------------------------------------------------------------------

QUESTIONS = [
    {
        "id": "deployment_eu",
        "fact_id": "jurisdiction_in_scope",
        "text": "Is the organisation and system within the territorial and operator scope of the EU AI Act?",
        "help": "Article 2 defines territorial, provider, deployer, importer, distributor, and affected-person scope.",
    },
    {
        "id": "is_ai_system",
        "fact_id": "is_ai_system",
        "text": "Does the subject meet the EU AI Act definition of an AI system?",
        "help": "Resolve this from Article 3(1), not merely from a library or keyword match.",
    },
    {
        "id": "role_provider",
        "fact_id": "role_provider",
        "text": "Is the organisation acting as the provider of this system?",
        "help": "Provider-specific duties, including Article 17, require this role to be established.",
    },
    {
        "id": "role_deployer",
        "fact_id": "role_deployer",
        "text": "Is the organisation using or deploying this system under its authority?",
        "help": "Deployer-specific duties require this role to be established.",
    },
    {
        "id": "affected_domain",
        "fact_id": "eu_annex_iii_use",
        "text": "Is the intended purpose one of the use cases specifically listed in Annex III?",
        "help": "Article 6(2) applies to systems in an Annex III use case, subject to Article 6(3).",
    },
    {
        "id": "significant_harm",
        "fact_id": "eu_significant_risk",
        "text": "Does the Annex III use pose a significant risk of harm to health, safety, or fundamental rights, including materially influencing a decision outcome?",
        "help": "Article 6(3) makes significant risk and material influence decision-critical.",
    },
    {
        "id": "profiling",
        "fact_id": "eu_profiling",
        "text": "Does the system perform profiling of natural persons?",
        "help": "Under Article 6(3), an Annex III system that performs profiling is always high-risk.",
    },
    {
        "id": "narrow_procedural",
        "fact_id": "eu_narrow_procedural_task",
        "text": "Is the system limited to a narrow procedural task?",
        "help": "Article 6(3)(a) is one condition relevant to the Annex III significant-risk exception.",
    },
    {
        "id": "improves_human_activity",
        "fact_id": "eu_improves_completed_human_activity",
        "text": "Does the system only improve the result of a previously completed human activity?",
        "help": "Article 6(3)(b) is one condition relevant to the Annex III significant-risk exception.",
    },
    {
        "id": "pattern_detection",
        "fact_id": "eu_pattern_detection_without_replacement",
        "text": "Does it only detect decision patterns or deviations without replacing or influencing the completed human assessment, with proper human review?",
        "help": "These are the cumulative conditions in Article 6(3)(c).",
    },
    {
        "id": "preparatory_task",
        "fact_id": "eu_preparatory_task",
        "text": "Does it only perform a preparatory task to an Annex III assessment?",
        "help": "Article 6(3)(d) is one condition relevant to the Annex III significant-risk exception.",
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


def generate_questionnaire(pattern_result: Optional[Classification] = None) -> dict:
    """Generate the EU fact questionnaire without assigning decision weights."""
    kernel = DecisionKernel()
    return {
        "type": "risk_assessment_questionnaire",
        "version": "2.0",
        "model_version": kernel.model_version,
        "jurisdiction": "eu",
        "context": None if pattern_result is None else {
            "detector_priority": pattern_result.confidence_score,
            "detector_tier": pattern_result.tier.value,
            "detector_indicators": pattern_result.indicators_matched,
            "decision_effect": "none",
        },
        "instructions": (
            "Answer from sourced evidence. Missing and unsure answers do not "
            "become no. The result may identify additional facts needed before "
            "a determination can be made."
        ),
        "questions": [
            {
                "id": q["id"],
                "text": q["text"],
                "help": q["help"],
                "fact_id": q["fact_id"],
                "options": ["yes", "no", "unsure", "not_applicable"],
            }
            for q in QUESTIONS
        ],
    }


def evaluate_questionnaire(
    answers: dict,
    pattern_result: Optional[Classification] = None,
) -> dict:
    """Translate sourced answers to facts and return the kernel result."""
    if not isinstance(answers, dict):
        raise DecisionInputError("questionnaire answers must be an object")
    question_by_id = {question["id"]: question for question in QUESTIONS}
    unknown_ids = sorted(set(answers) - set(question_by_id))
    if unknown_ids:
        raise DecisionInputError(f"unknown questionnaire answer ids: {unknown_ids}")
    valid_states = {"yes", "no", "unsure", "not_applicable"}
    now = datetime.now(timezone.utc).isoformat()
    facts = {}
    for answer_id, answer in answers.items():
        if answer not in valid_states:
            raise DecisionInputError(
                f"answer {answer_id!r} must be yes, no, unsure, or not_applicable"
            )
        question = question_by_id[answer_id]
        state = "unknown" if answer == "unsure" else answer
        facts[question["fact_id"]] = fact(
            state,
            f"questionnaire:{answer_id}",
            "eu",
            now,
            source_type="user_attestation",
        )
    kernel = DecisionKernel()
    return kernel.evaluate({
        "model_version": kernel.model_version,
        "jurisdiction": "eu",
        "facts": facts,
    })


def format_decision_result_cli(result: dict) -> str:
    """Render the tagged decision result without inventing a tier or score."""
    lines = [f"Decision result: {result['result_type']}"]
    if result["result_type"] == "indication":
        for indication in result.get("indications", []):
            lines.append(
                f"- {indication['classification']}: {indication['provision']}"
            )
        if result.get("unresolved_predicates"):
            lines.append("Additional unresolved facts:")
    elif result["result_type"] == "outside_scope_candidate":
        lines.append(
            f"Basis: {result['outside_scope_basis']['provision']}"
        )
    else:
        lines.append("Facts needed before a determination:")
    for unresolved in result.get("unresolved_predicates", []):
        lines.append(f"- {unresolved['question']} ({unresolved['reason']})")
    return "\n".join(lines)


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
        lines.append(
            f"  Detector tier: {ctx['detector_tier'].upper().replace('_', '-')}"
        )
        lines.append(f"  Detector priority: {ctx['detector_priority']}/100")
        lines.append("  Detector output does not decide legal applicability.")
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
                lines.append("     [yes, no, unsure]")
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
            print(json.dumps(result, indent=2))
        else:
            print(format_decision_result_cli(result))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
