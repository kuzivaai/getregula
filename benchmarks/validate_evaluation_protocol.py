#!/usr/bin/env python3
"""Validate the public detector-evaluation protocol without dependencies."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEFAULT_PROTOCOL = ROOT / "evaluation_protocol.v1.json"


def _require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def validate(payload: dict) -> list[str]:
    """Return stable, non-sensitive validation errors for one protocol."""
    errors: list[str] = []
    _require(payload.get("schema_version") == "1.0",
             "schema_version must be 1.0", errors)
    _require(payload.get("status") in {"preregistration_template", "frozen"},
             "status must be preregistration_template or frozen", errors)

    target = payload.get("measurement_target", {})
    excluded = set(target.get("excluded_outcomes", []))
    _require({"legal_applicability", "legal_risk_classification", "conformity", "compliance"} <= excluded,
             "measurement target must exclude legal determinations", errors)

    freeze = payload.get("freeze", {})
    digests = set(freeze.get("required_digests", []))
    _require({"ruleset_sha256", "configuration_sha256", "corpus_manifest_sha256", "codebook_sha256"} <= digests,
             "freeze must require rule, config, corpus and codebook digests", errors)
    _require(freeze.get("changes_create_new_evaluation_version") is True,
             "frozen changes must create a new evaluation version", errors)

    corpus = payload.get("corpus", {})
    _require(corpus.get("split_unit") == "repository",
             "split unit must be repository", errors)
    _require(corpus.get("split_strategy") == "chronological_project_held_out",
             "split strategy must be chronological and project-held-out", errors)
    dedup = set(corpus.get("deduplicate_before_split", []))
    _require({"exact_source_identity", "normalised_snippet_sha256"} <= dedup,
             "de-duplication must include exact identity and snippet hash", errors)
    _require(corpus.get("acquisition_failures_and_exclusions_recorded") is True,
             "acquisition failures and exclusions must be recorded", errors)

    annotation = payload.get("annotation", {})
    _require(annotation.get("minimum_independent_human_raters", 0) >= 3,
             "at least three independent human raters are required", errors)
    _require(set(annotation.get("labels", [])) == {"tp", "fp", "uncertain", "not_assessable"},
             "annotation labels must preserve uncertainty and non-assessability", errors)
    _require(annotation.get("not_assessable_treatment") == "missing_not_negative",
             "not_assessable must be missing, not negative", errors)
    _require(annotation.get("original_ratings_immutable") is True,
             "original ratings must be immutable", errors)
    _require(annotation.get("public_rater_ids_non_identifying") is True,
             "public rater IDs must be non-identifying", errors)
    _require("detector_priority_score" in annotation.get("blinded_from", []),
             "raters must be blinded from detector priority", errors)

    agreement = payload.get("agreement", {})
    _require(agreement.get("primary") == "krippendorff_alpha_nominal",
             "primary agreement must handle missing nominal ratings", errors)
    _require(agreement.get("confidence_interval") == "item_bootstrap_95",
             "agreement must use an item-bootstrap interval", errors)
    _require(agreement.get("universal_publishability_threshold") is False,
             "agreement must not use a universal publishability threshold", errors)

    metrics = payload.get("metrics", {})
    _require(metrics.get("integer_confusion_counts_before_derived_metrics") is True,
             "integer confusion counts must precede derived metrics", errors)
    _require(metrics.get("priority_score_is_correctness_probability") is False,
             "priority score must not be a correctness probability", errors)
    _require(metrics.get("calibration_requires_independent_representative_calibration_set") is True,
             "calibration must require independent representative data", errors)
    _require({"coverage", "selective_error", "abstained_error"} <= set(metrics.get("abstention_report", [])),
             "abstention reporting is incomplete", errors)

    repeatability = payload.get("repeatability", {})
    _require(repeatability.get("minimum_clean_runs", 0) >= 2,
             "at least two clean runs are required", errors)
    _require(set(repeatability.get("completion_statuses", [])) == {"completed", "completed_with_skips", "failed"},
             "completion statuses must distinguish skips and failure", errors)
    _require(repeatability.get("compare_content_hashes_and_case_ids") is True,
             "repeatability must compare hashes and case IDs", errors)
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("protocol", nargs="?", type=Path, default=DEFAULT_PROTOCOL)
    args = parser.parse_args(argv)
    try:
        payload = json.loads(args.protocol.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"evaluation-protocol: unreadable: {error}")
        return 2
    errors = validate(payload)
    for error in errors:
        print(f"evaluation-protocol: {error}")
    if errors:
        return 1
    print(f"evaluation-protocol: valid schema {payload['schema_version']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
