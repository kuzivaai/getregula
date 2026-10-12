#!/usr/bin/env python3
"""Thin adapters from product surfaces to the canonical decision kernel.

Static-analysis signals are observations, not substitutes for the legal facts
required by the model. Surfaces that have no declared facts therefore receive
an honest insufficient-information result.
"""

import sys
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Optional

sys.path.insert(0, str(Path(__file__).parent))

from decision_kernel import DecisionInputError, DecisionKernel
from evidence_review import (
    DEFAULT_LIMITATIONS,
    DEFAULT_REVIEWER_QUESTIONS,
    DEFAULT_REVIEW_STEPS,
    review_record_from_finding,
)


PUBLIC_REVIEW_SCHEMA_VERSION = "2.0"


def _public_reference_rows(result: Mapping[str, Any]) -> list:
    rows = []
    for item in result.get("indications", []) or []:
        rows.append({
            "reference": str(item.get("provision", "unspecified provision")),
            "status": "potentially_relevant",
            "source_version": None,
            "source_date": None,
        })
    for item in result.get("obligations", []) or []:
        rows.append({
            "reference": str(item.get("provision", "unspecified provision")),
            "status": "potentially_relevant",
            "source_version": None,
            "source_date": None,
        })
    basis = result.get("outside_scope_basis") or {}
    if basis.get("provision"):
        rows.append({
            "reference": str(basis["provision"]),
            "status": "unresolved_scope_question",
            "source_version": None,
            "source_date": None,
        })
    for unresolved in result.get("unresolved_predicates", []) or []:
        for affected in unresolved.get("would_resolve", []) or []:
            if affected.get("provision"):
                rows.append({
                    "reference": str(affected["provision"]),
                    "status": "unresolved_question",
                    "source_version": None,
                    "source_date": None,
                })

    deduplicated = []
    seen = set()
    for row in rows:
        key = (row["reference"], row["status"])
        if key in seen:
            continue
        seen.add(key)
        deduplicated.append(row)
    return deduplicated


def public_review_result(result: Mapping[str, Any]) -> dict:
    """Remove machine legal outcomes from an internal predicate evaluation."""
    unresolved = list(result.get("unresolved_predicates", []) or [])
    missing_context = [
        {
            "fact_id": item.get("fact_id"),
            "reason": item.get("reason"),
            "question": item.get("question"),
            "observed_values": list(item.get("observed_values", []) or []),
        }
        for item in unresolved
        if item.get("reason") != "contradictory"
    ]
    contradictory_context = [
        {
            "fact_id": item.get("fact_id"),
            "question": item.get("question"),
            "observed_values": list(item.get("observed_values", []) or []),
        }
        for item in unresolved
        if item.get("reason") == "contradictory"
    ]
    review_status = (
        "insufficient_information"
        if result.get("result_type") == "insufficient_information"
        else "human_review_required"
    )
    return {
        "schema_version": PUBLIC_REVIEW_SCHEMA_VERSION,
        "record_type": "declared_context_review",
        "review_status": review_status,
        "model_version": result.get("model_version"),
        "jurisdiction": result.get("jurisdiction"),
        "evidence_completeness": dict(result.get("evidence_completeness") or {}),
        "declared_context": list(result.get("matched_evidence", []) or []),
        "missing_context": missing_context,
        "contradictory_context": contradictory_context,
        "potentially_relevant_provisions": _public_reference_rows(result),
        "reviewer_questions": [
            item["question"] for item in missing_context
            if item.get("question")
        ] or list(DEFAULT_REVIEWER_QUESTIONS),
        "suggested_human_review_steps": list(DEFAULT_REVIEW_STEPS),
        "explicit_limitations": list(DEFAULT_LIMITATIONS),
        "probability_calibration": dict(
            result.get("probability_calibration") or {"available": False}
        ),
        "human_decision": None,
    }


def empty_decision(
    jurisdiction: str = "eu",
    source_ref: str = "adapter:no-declared-facts",
    kernel: Optional[DecisionKernel] = None,
) -> dict:
    """Return a public review result with no declared facts."""
    del source_ref  # Describes the absence at the caller; no fact is fabricated.
    active_kernel = kernel or DecisionKernel()
    result = active_kernel.evaluate({
        "model_version": active_kernel.model_version,
        "jurisdiction": jurisdiction,
        "facts": {},
    })
    return public_review_result(result)


def evaluate_payload(
    payload: Mapping[str, Any],
    kernel: Optional[DecisionKernel] = None,
) -> dict:
    """Evaluate the public canonical payload, defaulting only model_version."""
    if not isinstance(payload, Mapping):
        raise DecisionInputError("decision_request must be an object")
    active_kernel = kernel or DecisionKernel()
    request = dict(payload)
    request.setdefault("model_version", active_kernel.model_version)
    return public_review_result(active_kernel.evaluate(request))


def fact_value(
    state: str,
    jurisdiction: str,
    source_ref: str,
    timestamp: Optional[str] = None,
) -> dict:
    """Build one explicitly sourced canonical value for a presentation adapter."""
    return {
        "state": state,
        "provenance": {
            "source_type": "user_declaration",
            "source_ref": source_ref,
        },
        "jurisdiction": jurisdiction,
        "timestamp": timestamp or datetime.now(timezone.utc).isoformat(),
    }


def detector_finding(finding: Mapping[str, Any]) -> dict:
    """Rename decision-like scanner fields so observations cannot pose as law."""
    output = dict(finding)
    output["reviewable_evidence"] = review_record_from_finding(finding)
    if "tier" in output:
        output["detector_class"] = output.pop("tier")
    if "confidence_score" in output:
        output["detector_priority"] = output.pop("confidence_score")
    if "confidence" in output:
        output.pop("confidence")
    if "articles" in output:
        output["suggested_provisions"] = output.pop("articles")
    if "applicable_articles" in output:
        output["suggested_provisions"] = output.pop("applicable_articles")
    if "effort_hours" in output:
        output["detector_remediation_size"] = output.pop("effort_hours")
    for key in (
        "deadline",
        "deadline_note",
        "deadline_status",
        "omnibus_deadline",
        "domain_obligations",
    ):
        output.pop(key, None)
    if "observations" in output:
        contexts = []
        for raw in output.pop("observations") or []:
            provision = str(raw.get("article", "")).strip()
            contexts.append({
                "suggested_provision": provision,
                "detector_observation": (
                    "A code pattern was found for review against Article "
                    f"{provision}; applicability remains unresolved."
                ),
            })
        output["detector_context"] = contexts
    return output


def detector_findings(findings) -> list:
    return [detector_finding(finding) for finding in findings]


def detector_explanation(result: Mapping[str, Any], filepath: str) -> dict:
    """Keep explain-mode observations without its copied legal conclusions."""
    classification = result.get("classification")
    if hasattr(classification, "to_dict"):
        classification = classification.to_dict()
    classification_observation = detector_finding(classification or {})

    matches = []
    for raw in result.get("pattern_matches", []):
        match = dict(raw)
        if "legal_basis" in match:
            match["suggested_provision"] = match.pop("legal_basis")
        matches.append(match)

    role = dict(result.get("provider_deployer") or {})
    if "role" in role:
        role["detector_role_candidate"] = role.pop("role")
    if "confidence" in role:
        role["detector_priority_label"] = role.pop("confidence")

    return {
        "file": filepath,
        "classification_observation": classification_observation,
        "pattern_matches": matches,
        "role_observation": role,
    }


def format_detector_explanation(result: Mapping[str, Any]) -> str:
    """Render explain-mode observations without duties or effort estimates."""
    source = str(result.get("file", "unknown"))
    lines = [f"Detector explanation: {source}"]
    observation = result.get("classification_observation") or {}
    detector_class = observation.get("detector_class", "unclassified")
    lines.append(f"Detector class: {detector_class}")
    for match in result.get("pattern_matches", []):
        location = f"{source}:{match.get('line', '?')}"
        pattern = match.get("pattern") or match.get("matched_pattern") or "pattern"
        lines.append(f"  - {location}: {pattern}")
        if match.get("suggested_provision"):
            lines.append(
                f"    Suggested provision for review: {match['suggested_provision']}"
            )
    role = result.get("role_observation") or {}
    if role:
        lines.append(
            "Role detector candidate: "
            + str(role.get("detector_role_candidate", "unclear"))
        )
    lines.append(
        "No obligation or effort estimate is produced from detector observations."
    )
    return "\n".join(lines)


def format_decision_text(result: Mapping[str, Any], command: str = "check") -> str:
    """Render declared-context review status without adding legal conclusions."""
    lines = [
        f"Review status: {result['review_status']}",
        f"Model: {result['model_version']}",
        f"Jurisdiction: {result['jurisdiction']}",
        "Human decision: not recorded",
    ]
    if result["review_status"] == "insufficient_information":
        unresolved = result.get("missing_context", [])
        contradictory = result.get("contradictory_context", [])
        lines.append(f"Declared context needed for review: {len(unresolved)}")
        for item in unresolved[:5]:
            lines.append(
                f"  - {item['fact_id']}: "
                f"{item.get('question', 'Resolve this fact.')}"
            )
        if len(unresolved) > 5:
            lines.append(f"  - {len(unresolved) - 5} additional unresolved facts in JSON output")
        if contradictory:
            lines.append(f"Contradictory declared facts: {len(contradictory)}")
        if unresolved:
            lines.append(f"  Declare one with: regula {command} . --fact "
                         f"{unresolved[0]['fact_id']}=yes|no|unknown|not_applicable")
    else:
        lines.append("Potentially relevant provisions for accountable review:")
        for item in result.get("potentially_relevant_provisions", [])[:10]:
            lines.append(f"  - {item['reference']} ({item['status']})")
    return "\n".join(lines)


def resolved_gap_evidence(assessment: Mapping[str, Any], decision: Mapping[str, Any]) -> dict:
    """Keep gap observations as review leads, never as resolved duties."""
    articles = assessment.get("articles") or {}
    held_observations = {
        str(article): {
            "potentially_relevant_provision": f"Article {article}",
            "title": details.get("title"),
            "review_status": "held_for_human_review",
            "observed_evidence": list(details.get("evidence", []) or []),
            "not_observed_by_configured_scan": list(
                details.get("gaps", []) or []
            ),
            "explicit_limitation": (
                "A detected or missing artefact does not establish that the "
                "provision applies or that any legal duty is met."
            ),
        }
        for article, details in articles.items()
    }
    return {
        "project_path": assessment.get("project_path"),
        "article_observations": {},
        "held_article_observations": held_observations,
        "not_assessed_article_count": len(held_observations),
        "review_status": (
            "held_for_human_review" if held_observations else "no_observation"
        ),
        "potentially_relevant_provisions": list(
            decision.get("potentially_relevant_provisions", []) or []
        ),
        "note": (
            "Code and documentation observations remain held because no "
            "accountable human decision is recorded. They do not establish "
            "applicability, a legal duty, compliance, or non-compliance."
        ),
    }


def unresolved_documentation_draft(text: str, project_path: Optional[str] = None) -> str:
    """Remove classifier conclusions from a draft produced without legal facts."""
    output = re.sub(
        r"\*\*Overall Risk Classification:\*\*[^\n]*",
        "**Decision status:** INSUFFICIENT INFORMATION",
        text,
    )
    output = re.sub(
        r"\*\*Classification:\*\*[^\n]*",
        "**Decision status:** INSUFFICIENT INFORMATION",
        output,
    )
    output = output.replace("| File | Risk Tier | Indicators | Applicable Articles |",
                            "| File | Detector Class | Indicators | Suggested Provisions |")
    output = output.replace("| File | Risk tier | Indicators | Articles |",
                            "| File | Detector class | Indicators | Suggested provisions |")
    output = output.replace("| _No AI components detected_ |", "| _No detector patterns found_ |")
    output = output.replace(
        "Articles 9-15 apply. See Annex IV documentation for full compliance status.",
        "No Article 9 to 15 duty is attached until applicability is resolved.",
    )
    output = output.replace(
        "Article 14 compliance required.",
        "Article 14 must be evaluated if the kernel later resolves that duty.",
    )
    output = output.replace(
        "Transparency obligations apply under Article 50.",
        "Article 50 applicability remains unresolved.",
    )
    output = output.replace(
        "Articles 9-15 obligations apply.",
        "Article 9 to 15 applicability remains unresolved.",
    )
    output = output.replace(
        "Transparency obligations apply under Article 50.",
        "Article 50 applicability remains unresolved.",
    )
    output = re.sub(
        r"\*\*Risk tier:\*\*[^\n]*",
        "**Detector class:** unverified code-pattern observation",
        output,
    )
    output = output.replace(
        "**[COMPLETE THESE]** (Article 10 — Data Governance)",
        "**[COMPLETE THESE]** (conditional Article 10 template; "
        "applicability unresolved)",
    )
    output = output.replace(
        "_No human oversight patterns detected._ Review Article 14 requirements.",
        "_No human oversight patterns detected._ If Article 14 is later "
        "resolved applicable, review its requirements.",
    )
    output = output.replace(
        "_No logging infrastructure detected._ Article 12 requires automatic "
        "recording of events.",
        "_No logging infrastructure detected._ If Article 12 is later resolved "
        "applicable, evaluate its automatic event-recording requirement.",
    )
    output = output.replace(
        "## 5. Risk Management System (Article 9)",
        "## 5. Conditional Risk Management Template "
        "(Article 9; applicability unresolved)",
    )
    if project_path:
        output = output.replace(project_path, Path(project_path).name)
    gate = (
        "> **RELIANCE GATE:** The decision kernel returned insufficient information. "
        "This unverified scaffold does not establish that the subject is an AI "
        "system, that a provision applies, or that a duty is satisfied. Resolve "
        "the accompanying facts list before use as regulatory evidence.\n\n"
    )
    return gate + output
