#!/usr/bin/env python3
"""Frozen, stdlib-only scoring primitives for commercial_v1."""

import math
import hashlib
import json
from pathlib import Path


def wilson95(successes, total):
    """Return the two-sided Wilson 95% interval for a binomial rate."""
    if total <= 0:
        return {"low": None, "high": None}
    z = 1.959963984540054
    rate = successes / total
    denominator = 1 + z * z / total
    centre = (rate + z * z / (2 * total)) / denominator
    spread = z * math.sqrt(
        rate * (1 - rate) / total + z * z / (4 * total * total)
    ) / denominator
    return {"low": max(0.0, centre - spread),
            "high": min(1.0, centre + spread)}


def _rate(numerator, denominator):
    return {
        "numerator": numerator,
        "denominator": denominator,
        "value": numerator / denominator if denominator else None,
        "wilson95": wilson95(numerator, denominator),
    }


def binary_metrics(tp, fp, fn, tn):
    """Return confusion counts and denominator-preserving metrics."""
    precision_den = tp + fp
    recall_den = tp + fn
    total = tp + fp + fn + tn
    f1_den = 2 * tp + fp + fn
    mcc_den = math.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
    return {
        "counts": {"tp": tp, "fp": fp, "fn": fn, "tn": tn,
                   "decisions": total},
        "precision": _rate(tp, precision_den),
        "recall": _rate(tp, recall_den),
        "f1": {"numerator": 2 * tp, "denominator": f1_den,
               "value": 2 * tp / f1_den if f1_den else None},
        "mcc": ((tp * tn - fp * fn) / mcc_den) if mcc_den else None,
    }


def score_result_files(labels_path, result_paths):
    labels = {row["decision_id"]: row for row in json.loads(
        Path(labels_path).read_text())}
    reports = []
    for result_path in result_paths:
        path = Path(result_path)
        payload = json.loads(path.read_text())
        records = payload["records"]
        actual_ids = [row.get("decision_id") for row in records]
        duplicate_ids = sorted({item for item in actual_ids
                                if actual_ids.count(item) > 1 and item is not None})
        actual = set(actual_ids)
        expected = set(labels)
        failures = [row["decision_id"] for row in records
                    if row.get("exit_code") != 0 or row.get("timed_out")
                    or row.get("parse_error") or row.get("predicted") is None]
        by_candidate = {}
        for candidate in ("A", "B"):
            candidate_ids = {key for key, value in labels.items()
                             if value.get("candidate") == candidate}
            complete = (actual == expected and not duplicate_ids and not any(
                key in failures for key in candidate_ids)
            )
            counts = {"tp": 0, "fp": 0, "fn": 0, "tn": 0}
            for record in records:
                identifier = record["decision_id"]
                if identifier not in candidate_ids or identifier in failures:
                    continue
                truth = labels[identifier]["expected"]
                predicted = record["predicted"]
                key = ("tp" if truth and predicted else
                       "fn" if truth else "fp" if predicted else "tn")
                counts[key] += 1
            by_candidate[candidate] = {
                "complete": complete,
                "applicable_decisions": len(candidate_ids),
                "valid_decisions": sum(counts.values()),
                "failed_decision_ids": sorted(set(failures) & candidate_ids),
                "metrics": binary_metrics(**counts),
                "strata": _strata(records, labels, candidate_ids, failures),
                "synthetic_metric_eligible": complete,
                "headline_eligible": False,
                "headline_blockers": [
                    "synthetic transformations are correlated families",
                    "real-repository labelled accuracy unavailable",
                    "comparative, determinism, network, public-claim and demand gates are evaluated outside this score file"
                ],
            }
        reports.append({
            "result_path": str(path), "tool": payload["tool"],
            "result_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "enumeration_complete": actual == expected,
            "missing_ids": sorted(expected - actual),
            "extra_ids": sorted(actual - expected),
            "duplicate_ids": duplicate_ids,
            "failed_ids": sorted(failures), "candidates": by_candidate,
        })
    return {
        "schema_version": "commercial_v1.score.1",
        "labels_sha256": hashlib.sha256(Path(labels_path).read_bytes()).hexdigest(),
        "reports": reports,
    }


def _strata(records, labels, candidate_ids, failures):
    groups = {}
    for record in records:
        identifier = record.get("decision_id")
        if identifier not in candidate_ids or identifier in failures:
            continue
        for dimension in ("language", "transform"):
            key = f"{dimension}:{record.get(dimension, 'missing')}"
            counts = groups.setdefault(key, {"tp": 0, "fp": 0, "fn": 0, "tn": 0})
            truth = labels[identifier]["expected"]
            predicted = record["predicted"]
            cell = ("tp" if truth and predicted else
                    "fn" if truth else "fp" if predicted else "tn")
            counts[cell] += 1
    return {key: binary_metrics(**counts) for key, counts in sorted(groups.items())}


def main(argv=None):
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--labels", type=Path, required=True)
    parser.add_argument("--result", type=Path, action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    report = score_result_files(args.labels, args.result)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(f"scored {len(args.result)} result file(s); labels opened only in scoring")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
