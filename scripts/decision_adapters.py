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


def empty_decision(
    jurisdiction: str = "eu",
    source_ref: str = "adapter:no-declared-facts",
    kernel: Optional[DecisionKernel] = None,
) -> dict:
    """Evaluate an empty fact map without converting detector output to facts."""
    del source_ref  # Describes the absence at the caller; no fact is fabricated.
    active_kernel = kernel or DecisionKernel()
    return active_kernel.evaluate({
        "model_version": active_kernel.model_version,
        "jurisdiction": jurisdiction,
        "facts": {},
    })


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
    return active_kernel.evaluate(request)


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
    lines = [f"Detector explanation: {result.get('file', 'unknown')}"]
    observation = result.get("classification_observation") or {}
    detector_class = observation.get("detector_class", "unclassified")
    lines.append(f"Detector class: {detector_class}")
    for match in result.get("pattern_matches", []):
        location = f"line {match.get('line', '?')}"
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


def format_decision_text(result: Mapping[str, Any]) -> str:
    """Render a compact decision without introducing adapter conclusions."""
    lines = [
        f"Decision: {result['result_type']}",
        f"Model: {result['model_version']}",
        f"Jurisdiction: {result['jurisdiction']}",
        f"Rule resolution: {result['rule_resolution']}",
    ]
    if result["result_type"] == "insufficient_information":
        unresolved = result.get("unresolved_predicates", [])
        lines.append(f"Facts needed to resolve the next decision: {len(unresolved)}")
        for item in unresolved[:5]:
            # The kernel already ranks by leverage; the count was simply never
            # shown, so a list of 46 read as a wall rather than as an ordering.
            # Every figure here is the kernel's own (N149).
            advances = len(item.get("would_resolve", []) or [])
            suffix = (f"  [answering this advances {advances} provision"
                      f"{'' if advances == 1 else 's'}]") if advances else ""
            lines.append(
                f"  - {item['fact_id']}: {item.get('question', 'Resolve this fact.')}{suffix}"
            )
        if len(unresolved) > 5:
            lines.append(f"  - {len(unresolved) - 5} additional unresolved facts in JSON output")
        if unresolved:
            lines.append("  Declare one with: regula check . --fact "
                         f"{unresolved[0]['fact_id']}=yes|no|unknown|not_applicable")
    elif result["result_type"] == "indication":
        for item in result.get("indications", []):
            lines.append(
                f"  - {item['classification']}: {item['provision']}"
            )
    else:
        basis = result.get("outside_scope_basis", {})
        lines.append(f"Basis: {basis.get('provision', 'resolved predicate path')}")
    return "\n".join(lines)


def resolved_gap_evidence(assessment: Mapping[str, Any], decision: Mapping[str, Any]) -> dict:
    """Keep gap observations only for obligations resolved by the kernel."""
    obligation_articles = {
        obligation["provision"].split("Article ", 1)[1].split(",", 1)[0]
        for obligation in decision.get("obligations", [])
        if "Article " in obligation.get("provision", "")
    }
    articles = assessment.get("articles") or {}
    resolved_articles = {
        article: data
        for article, data in articles.items()
        if str(article) in obligation_articles
    }
    return {
        "project_path": assessment.get("project_path"),
        "article_observations": resolved_articles,
        "not_assessed_article_count": len(articles) - len(resolved_articles),
        "note": (
            "Article evidence is attached only where the decision kernel "
            "resolved the corresponding obligation."
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
