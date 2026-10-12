#!/usr/bin/env python3
"""Shared schema for reviewable evidence produced from code observations.

The schema deliberately leaves legal conclusions empty. Detector output can
populate an observation and point a reviewer to a provision, but it cannot
resolve applicability, legal tier, duties, compliance, or non-applicability.
"""

import sys
from pathlib import Path
from typing import Any, Iterable, Mapping, Optional, TypedDict

sys.path.insert(0, str(Path(__file__).parent))


SCHEMA_VERSION = "1.0"


class SourceLocation(TypedDict):
    path: str
    line: Optional[int]


class SourceReference(TypedDict):
    reference: str
    source_version: Optional[str]
    source_date: Optional[str]
    status: str


class ReviewEvidenceRecord(TypedDict):
    schema_version: str
    record_type: str
    observation: str
    source_location: SourceLocation
    indicator: str
    observation_confidence: Optional[dict]
    declared_context: list
    missing_context: list[str]
    contradictory_context: list
    source_references: list[SourceReference]
    reviewer_questions: list[str]
    suggested_human_review_steps: list[str]
    explicit_limitations: list[str]
    human_decision: None


DEFAULT_MISSING_CONTEXT = [
    "Whether the subject is an AI system within the relevant legal definition",
    "The provider, deployer, importer, distributor, or other actor role",
    "Intended purpose, deployment context, affected people, and jurisdiction",
    "Conditions, exclusions, exceptions, and evidence not present in source code",
]

DEFAULT_REVIEWER_QUESTIONS = [
    "What intended purpose and deployment context does the accountable owner declare?",
    "Which actor role and jurisdiction are supported by non-code evidence?",
    "Do relevant conditions, exclusions, or exceptions change the analysis?",
]

DEFAULT_REVIEW_STEPS = [
    "Confirm the code observation at the recorded source location",
    "Collect declared context and preserve unknown or contradictory answers",
    "Review the potentially relevant provision with an accountable qualified reviewer",
    "Record the human decision and its evidence separately",
]

DEFAULT_LIMITATIONS = [
    "Static code observations do not determine legal applicability or legal risk tier",
    "Absence of a configured indicator does not prove absence of legal relevance",
    "The human decision field is intentionally empty until accountable review",
]


def _references(finding: Mapping[str, Any]) -> list[SourceReference]:
    raw = finding.get("suggested_provisions", finding.get("articles", [])) or []
    if isinstance(raw, (str, int)):
        raw = [raw]
    return [
        {
            "reference": str(reference),
            "source_version": None,
            "source_date": None,
            "status": "potentially_relevant",
        }
        for reference in raw
    ]


def review_record_from_finding(
    finding: Mapping[str, Any],
    *,
    declared_context: Optional[Iterable[Mapping[str, Any]]] = None,
    contradictory_context: Optional[Iterable[Mapping[str, Any]]] = None,
) -> ReviewEvidenceRecord:
    """Convert one detector finding without manufacturing a legal decision."""
    score = finding.get("confidence_score")
    confidence = None
    if score is not None:
        confidence = {
            "kind": "detector_priority",
            "value": score,
            "limitation": "Priority is not a probability or legal confidence score",
        }
    line = finding.get("line")
    try:
        line = int(line) if line is not None else None
    except (TypeError, ValueError):
        line = None

    return {
        "schema_version": SCHEMA_VERSION,
        "record_type": "reviewable_evidence",
        "observation": str(
            finding.get("description")
            or finding.get("observation")
            or "A configured code pattern was found"
        ),
        "source_location": {
            "path": str(finding.get("file", finding.get("path", "unknown"))),
            "line": line,
        },
        "indicator": str(
            finding.get("category")
            or finding.get("pattern")
            or finding.get("detector_class")
            or "configured_pattern"
        ),
        "observation_confidence": confidence,
        "declared_context": [dict(item) for item in (declared_context or [])],
        "missing_context": list(DEFAULT_MISSING_CONTEXT),
        "contradictory_context": [
            dict(item) for item in (contradictory_context or [])
        ],
        "source_references": _references(finding),
        "reviewer_questions": list(DEFAULT_REVIEWER_QUESTIONS),
        "suggested_human_review_steps": list(DEFAULT_REVIEW_STEPS),
        "explicit_limitations": list(DEFAULT_LIMITATIONS),
        "human_decision": None,
    }


def review_records_from_findings(findings: Iterable[Mapping[str, Any]]) -> list:
    """Build review records for unsuppressed detector findings."""
    return [
        review_record_from_finding(finding)
        for finding in findings
        if not finding.get("suppressed")
    ]


__all__ = [
    "SCHEMA_VERSION",
    "ReviewEvidenceRecord",
    "review_record_from_finding",
    "review_records_from_findings",
]
