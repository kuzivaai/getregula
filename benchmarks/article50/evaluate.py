#!/usr/bin/env python3
"""Evaluate Article 50 lexical observations on a synthetic regression corpus."""

import argparse
import json
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from article50_evidence import BRANCHES, scan_article50  # noqa: E402


CORPUS_PATH = Path(__file__).with_name("corpus.json")
RESULTS_PATH = Path(__file__).with_name("results.json")


def _metrics(counts):
    tp = counts["true_positive"]
    fp = counts["false_positive"]
    fn = counts["false_negative"]
    precision = tp / (tp + fp) if tp + fp else None
    recall = tp / (tp + fn) if tp + fn else None
    return {
        **counts,
        "precision": precision,
        "recall": recall,
    }


def evaluate_corpus(corpus=None):
    corpus = corpus or json.loads(CORPUS_PATH.read_text(encoding="utf-8"))
    counts = {
        kind: {"true_positive": 0, "true_negative": 0,
               "false_positive": 0, "false_negative": 0}
        for kind in ("trigger", "control")
    }
    errors = []
    case_results = []
    for case in corpus["cases"]:
        with tempfile.TemporaryDirectory(prefix="regula_article50_") as tmp:
            Path(tmp, "fixture.py").write_text(case["content"], encoding="utf-8")
            observed = scan_article50(tmp)["branches"]
        row = {"id": case["id"], "checks": []}
        for branch_id in BRANCHES:
            expected = case.get("expected", {}).get(branch_id, {})
            for kind, output_key in (
                ("trigger", "trigger_observations"),
                ("control", "control_observations"),
            ):
                expected_value = bool(expected.get(kind, False))
                observed_value = bool(observed[branch_id][output_key])
                outcome = (
                    "true_positive" if expected_value and observed_value
                    else "false_negative" if expected_value
                    else "false_positive" if observed_value
                    else "true_negative"
                )
                counts[kind][outcome] += 1
                check = {
                    "branch": branch_id,
                    "kind": kind,
                    "expected": expected_value,
                    "observed": observed_value,
                    "outcome": outcome,
                }
                row["checks"].append(check)
                if outcome in {"false_positive", "false_negative"}:
                    errors.append({"case_id": case["id"], **check})
        case_results.append(row)
    return {
        "schema_version": "1.0",
        "corpus_kind": corpus["corpus_kind"],
        "label_status": corpus["label_status"],
        "representative_of_production_code": False,
        "legal_accuracy_benchmark": False,
        "case_count": len(corpus["cases"]),
        "metrics": {kind: _metrics(values) for kind, values in counts.items()},
        "error_count": len(errors),
        "errors": errors,
        "case_results": case_results,
        "limitations": [
            "Synthetic regression fixtures are not representative production code.",
            "Labels were not independently annotated.",
            "Metrics describe lexical signal detection, not legal or compliance accuracy.",
            "A control string does not establish runtime timing, visibility, accessibility, robustness, or effectiveness."
        ],
    }


def render_results():
    return json.dumps(evaluate_corpus(), indent=2, sort_keys=True) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    rendered = render_results()
    if args.write:
        RESULTS_PATH.write_text(rendered, encoding="utf-8")
        print(f"wrote {RESULTS_PATH.relative_to(ROOT)}")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
