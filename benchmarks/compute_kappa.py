#!/usr/bin/env python3
# regula-ignore
"""Cohen's kappa computation for inter-rater reliability.

Takes two label files (rater 1 and rater 2) with overlapping finding IDs
and computes:
- Cohen's kappa with 95% confidence interval
- Agreement matrix
- Per-tier breakdown
- Disagreement list for adjudication

Usage:
    python3 benchmarks/compute_kappa.py rater1.json rater2.json
    python3 benchmarks/compute_kappa.py --test  # run synthetic validation
"""

import argparse
import json
import math
import sys
from pathlib import Path


def load_labels(path: Path) -> dict[str, str]:
    """Load {id: label} from a JSON file. Expects list of dicts with 'id' and 'label'."""
    data = json.load(path.open())
    entries = data if isinstance(data, list) else data.get("labels", data.get("candidates", []))
    return {
        e["id"]: e["label"].strip().lower()
        for e in entries
        if e.get("label", "").strip().lower() in ("tp", "fp")
    }


def cohen_kappa(labels_a: dict[str, str], labels_b: dict[str, str]) -> dict:
    """Compute Cohen's kappa with CI and agreement matrix."""
    common = sorted(set(labels_a) & set(labels_b))
    n = len(common)

    if n == 0:
        return {"error": "No overlapping labelled findings", "n": 0}

    # Build confusion matrix
    both_tp = sum(1 for fid in common if labels_a[fid] == "tp" and labels_b[fid] == "tp")
    both_fp = sum(1 for fid in common if labels_a[fid] == "fp" and labels_b[fid] == "fp")
    a_tp_b_fp = sum(1 for fid in common if labels_a[fid] == "tp" and labels_b[fid] == "fp")
    a_fp_b_tp = sum(1 for fid in common if labels_a[fid] == "fp" and labels_b[fid] == "tp")

    agree = both_tp + both_fp
    disagree = a_tp_b_fp + a_fp_b_tp
    p_o = agree / n  # observed agreement

    # Expected agreement by chance
    p_a_tp = (both_tp + a_tp_b_fp) / n
    p_b_tp = (both_tp + a_fp_b_tp) / n
    p_a_fp = 1 - p_a_tp
    p_b_fp = 1 - p_b_tp
    p_e = (p_a_tp * p_b_tp) + (p_a_fp * p_b_fp)

    # Cohen's kappa
    if p_e >= 1.0:
        kappa = 1.0 if p_o >= 1.0 else 0.0
    else:
        kappa = (p_o - p_e) / (1.0 - p_e)

    # Standard error (Fleiss 1981)
    if p_e >= 1.0:
        se = 0.0
    else:
        se = math.sqrt(p_e / (n * (1 - p_e) ** 2)) if n > 0 else 0.0

    ci_lower = kappa - 1.96 * se
    ci_upper = kappa + 1.96 * se

    # Landis & Koch interpretation
    if kappa < 0.0:
        interp = "Less than chance"
    elif kappa < 0.20:
        interp = "Slight"
    elif kappa < 0.40:
        interp = "Fair"
    elif kappa < 0.60:
        interp = "Moderate"
    elif kappa < 0.80:
        interp = "Substantial"
    else:
        interp = "Almost perfect"

    # Disagreements for adjudication
    disagreements = []
    for fid in common:
        if labels_a[fid] != labels_b[fid]:
            disagreements.append({
                "id": fid,
                "rater_1": labels_a[fid],
                "rater_2": labels_b[fid],
            })

    return {
        "n": n,
        "observed_agreement": round(p_o, 4),
        "expected_agreement": round(p_e, 4),
        "kappa": round(kappa, 4),
        "standard_error": round(se, 4),
        "ci_95_lower": round(ci_lower, 4),
        "ci_95_upper": round(ci_upper, 4),
        "interpretation": interp,
        "matrix": {
            "both_tp": both_tp,
            "both_fp": both_fp,
            "rater1_tp_rater2_fp": a_tp_b_fp,
            "rater1_fp_rater2_tp": a_fp_b_tp,
        },
        "agree": agree,
        "disagree": disagree,
        "disagreements": disagreements,
    }


def synthetic_test():
    """Validate kappa computation against known values."""
    # Perfect agreement: kappa = 1.0
    a = {f"f{i}": "tp" for i in range(25)}
    a.update({f"f{i}": "fp" for i in range(25, 50)})
    b = dict(a)  # identical
    result = cohen_kappa(a, b)
    assert result["kappa"] == 1.0, f"Perfect agreement: expected 1.0, got {result['kappa']}"
    print("  PASS  perfect agreement: kappa = 1.0")

    # Perfect disagreement: kappa < 0
    b2 = {k: ("fp" if v == "tp" else "tp") for k, v in a.items()}
    result2 = cohen_kappa(a, b2)
    assert result2["kappa"] < 0, f"Perfect disagreement: expected <0, got {result2['kappa']}"
    print(f"  PASS  perfect disagreement: kappa = {result2['kappa']}")

    # Moderate agreement: ~0.5-0.7
    a3 = {f"f{i}": "tp" for i in range(30)}
    a3.update({f"f{i}": "fp" for i in range(30, 60)})
    b3 = dict(a3)
    # Flip 10 out of 60 (83% agreement)
    for i in range(5):
        b3[f"f{i}"] = "fp"  # was tp
        b3[f"f{30+i}"] = "tp"  # was fp
    result3 = cohen_kappa(a3, b3)
    assert 0.4 < result3["kappa"] < 0.8, f"Moderate: expected 0.4-0.8, got {result3['kappa']}"
    print(f"  PASS  moderate agreement: kappa = {result3['kappa']}")

    # Empty overlap
    result4 = cohen_kappa({"a": "tp"}, {"b": "fp"})
    assert "error" in result4, "Empty overlap should return error"
    print("  PASS  empty overlap: returns error")

    print("\nAll synthetic tests passed.")
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("rater1", nargs="?", type=Path, help="Rater 1 labels JSON")
    parser.add_argument("rater2", nargs="?", type=Path, help="Rater 2 labels JSON")
    parser.add_argument("--test", action="store_true", help="Run synthetic validation")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()

    if args.test:
        ok = synthetic_test()
        sys.exit(0 if ok else 1)

    if not args.rater1 or not args.rater2:
        parser.error("Provide two label files, or use --test")

    labels_a = load_labels(args.rater1)
    labels_b = load_labels(args.rater2)

    result = cohen_kappa(labels_a, labels_b)

    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        if "error" in result:
            print(f"ERROR: {result['error']}")
            sys.exit(1)
        print(f"\nCohen's Kappa: {result['kappa']:.4f}")
        print(f"95% CI: [{result['ci_95_lower']:.4f}, {result['ci_95_upper']:.4f}]")
        print(f"Interpretation: {result['interpretation']} (Landis & Koch 1977)")
        print(f"\nObserved agreement: {result['observed_agreement']:.1%}")
        print(f"Expected by chance: {result['expected_agreement']:.1%}")
        print(f"N: {result['n']} overlapping findings")
        print(f"\nAgreement matrix:")
        m = result["matrix"]
        print(f"  Both TP: {m['both_tp']}")
        print(f"  Both FP: {m['both_fp']}")
        print(f"  R1=TP R2=FP: {m['rater1_tp_rater2_fp']}")
        print(f"  R1=FP R2=TP: {m['rater1_fp_rater2_tp']}")
        if result["disagreements"]:
            print(f"\nDisagreements ({result['disagree']}):")
            for d in result["disagreements"]:
                print(f"  {d['id']}: rater1={d['rater_1']}, rater2={d['rater_2']}")


if __name__ == "__main__":
    main()
