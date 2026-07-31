#!/usr/bin/env python3
"""Apply every preregistered conjunct without subjective escape hatches."""

import argparse
import json
from pathlib import Path


THRESHOLDS = {
    "A": {"precision_low": 0.90, "recall_low": 0.90},
    "B": {"precision_low": 0.90, "recall_low": 0.80},
}


def evaluate(candidate, metrics, external):
    threshold = THRESHOLDS[candidate]
    checks = {
        "synthetic_complete": bool(external.get("synthetic_complete")),
        "precision_lower_bound": (
            metrics["precision"]["wilson95"]["low"] is not None and
            metrics["precision"]["wilson95"]["low"] >= threshold["precision_low"]),
        "recall_lower_bound": (
            metrics["recall"]["wilson95"]["low"] is not None and
            metrics["recall"]["wilson95"]["low"] >= threshold["recall_low"]),
        "independent_repository_labels_30": external.get(
            "independently_labelled_repositories", 0) >= 30,
        "two_clean_identical_runs": bool(external.get("determinism_pass")),
        "evidence_manifest_verified": bool(external.get("manifest_verified")),
        "all_failed_runs_visible": bool(external.get("failed_runs_visible")),
        "public_release_core_journey": bool(external.get("public_journey_pass")),
        "no_material_network_contradiction": not bool(external.get(
            "material_network_contradiction")),
        "public_claim_integrity_pass": external.get(
            "public_claim_integrity") == "PASS",
        "comparative_advantage": external.get(
            "comparative_advantage") == "DEMONSTRATED",
        "no_hidden_weak_stratum": bool(external.get("all_strata_reported")),
    }
    return {"candidate": candidate, "checks": checks,
            "claim_ready": all(checks.values()),
            "failed_checks": sorted(key for key, value in checks.items()
                                    if not value)}


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--score", type=Path, required=True)
    parser.add_argument("--external", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    score = json.loads(args.score.read_text())
    external = json.loads(args.external.read_text())
    # Local HEAD is required for the product gate; ambiguity is an error.
    matching = [row for row in score["reports"] if row["tool"] == "local_head"]
    if len(matching) != 1:
        raise SystemExit(f"expected one local_head score report, got {len(matching)}")
    report = matching[0]
    result = {candidate: evaluate(candidate,
                                  report["candidates"][candidate]["metrics"],
                                  external[candidate])
              for candidate in ("A", "B")}
    result["C"] = {
        "candidate": "C", "claim_ready": False,
        "status": "MODEL_PROVISIONAL",
        "failed_checks": ["two independent human raters", "adjudication"],
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
