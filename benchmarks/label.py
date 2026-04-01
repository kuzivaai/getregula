#!/usr/bin/env python3
"""
Benchmark finding labeller for Regula.

Samples findings from benchmark results and generates a labelling sheet.
After manual labelling, calculates precision/recall per tier.

Usage:
    # Generate labelling sheet (50 samples per project)
    python3 benchmarks/label.py sample --per-project 50

    # Calculate precision from completed labels
    python3 benchmarks/label.py score
"""

import argparse
import json
import random
import sys
from pathlib import Path

RESULTS_DIR = Path(__file__).parent / "results"
LABELS_FILE = Path(__file__).parent / "labels.json"


def cmd_sample(args):
    """Sample findings from benchmark results for manual labelling."""
    per_project = args.per_project
    results_dir = RESULTS_DIR

    all_samples = []

    for result_file in sorted(results_dir.glob("*.json")):
        if result_file.name == "SUMMARY.json":
            continue

        project = result_file.stem
        findings = json.load(result_file.open())

        # Group by tier
        by_tier = {}
        for f in findings:
            tier = f.get("tier", "unknown")
            if tier not in by_tier:
                by_tier[tier] = []
            by_tier[tier].append(f)

        # Sample proportionally per tier, up to per_project total
        total = len(findings)
        sampled = 0
        for tier, tier_findings in sorted(by_tier.items()):
            # Proportion of this tier in total findings
            proportion = len(tier_findings) / total if total > 0 else 0
            n_sample = max(1, round(proportion * per_project))
            n_sample = min(n_sample, len(tier_findings))

            chosen = random.sample(tier_findings, n_sample)
            for f in chosen:
                all_samples.append({
                    "project": project,
                    "file": f.get("file", ""),
                    "line": f.get("line", 1),
                    "tier": tier,
                    "description": f.get("description", "")[:120],
                    "confidence_score": f.get("confidence_score", 0),
                    "indicators": f.get("indicators", []),
                    "label": None,  # TO BE FILLED: "tp" or "fp"
                    "notes": "",    # Optional human notes
                })
                sampled += 1

        print(f"{project}: {sampled} samples from {total} findings ({len(by_tier)} tiers)")

    # Load existing labels if any (preserve previous work)
    existing = {}
    if LABELS_FILE.exists():
        try:
            for item in json.load(LABELS_FILE.open()):
                key = f"{item['project']}:{item['file']}:{item['tier']}"
                existing[key] = item
        except (json.JSONDecodeError, KeyError):
            pass

    # Merge: keep existing labels, add new unlabelled samples
    merged = []
    for s in all_samples:
        key = f"{s['project']}:{s['file']}:{s['tier']}"
        if key in existing and existing[key].get("label"):
            merged.append(existing[key])
        else:
            merged.append(s)

    LABELS_FILE.write_text(json.dumps(merged, indent=2))
    print(f"\nWrote {len(merged)} samples to {LABELS_FILE}")

    labelled = sum(1 for s in merged if s.get("label"))
    unlabelled = len(merged) - labelled
    print(f"  Labelled: {labelled}")
    print(f"  Unlabelled: {unlabelled}")
    print(f"\nNext: open {LABELS_FILE} and set 'label' to 'tp' or 'fp' for each finding.")
    print("  tp = true positive (Regula correctly identified a risk indicator)")
    print("  fp = false positive (Regula flagged something that isn't a risk)")


def cmd_score(args):
    """Calculate precision per tier from labelled findings."""
    if not LABELS_FILE.exists():
        print(f"No labels file found at {LABELS_FILE}")
        print("Run: python3 benchmarks/label.py sample --per-project 50")
        sys.exit(1)

    labels = json.load(LABELS_FILE.open())
    labelled = [l for l in labels if l.get("label") in ("tp", "fp")]
    unlabelled = [l for l in labels if not l.get("label")]

    if not labelled:
        print("No labelled findings yet. Open labels.json and set 'label' to 'tp' or 'fp'.")
        sys.exit(1)

    print(f"Labelled: {len(labelled)} / {len(labels)} ({len(unlabelled)} remaining)\n")

    # Per-tier precision
    tier_stats = {}
    for l in labelled:
        tier = l["tier"]
        if tier not in tier_stats:
            tier_stats[tier] = {"tp": 0, "fp": 0}
        if l["label"] == "tp":
            tier_stats[tier]["tp"] += 1
        else:
            tier_stats[tier]["fp"] += 1

    print(f"{'Tier':<22} {'TP':>4} {'FP':>4} {'Total':>6} {'Precision':>10}")
    print(f"{'-'*22} {'-'*4} {'-'*4} {'-'*6} {'-'*10}")

    overall_tp = 0
    overall_fp = 0
    for tier in sorted(tier_stats.keys()):
        s = tier_stats[tier]
        total = s["tp"] + s["fp"]
        precision = s["tp"] / total if total > 0 else 0
        overall_tp += s["tp"]
        overall_fp += s["fp"]
        print(f"{tier:<22} {s['tp']:>4} {s['fp']:>4} {total:>6} {precision:>9.1%}")

    overall_total = overall_tp + overall_fp
    overall_precision = overall_tp / overall_total if overall_total > 0 else 0
    print(f"{'-'*22} {'-'*4} {'-'*4} {'-'*6} {'-'*10}")
    print(f"{'OVERALL':<22} {overall_tp:>4} {overall_fp:>4} {overall_total:>6} {overall_precision:>9.1%}")

    # Per-project precision
    print(f"\n{'Project':<22} {'TP':>4} {'FP':>4} {'Precision':>10}")
    print(f"{'-'*22} {'-'*4} {'-'*4} {'-'*10}")
    project_stats = {}
    for l in labelled:
        p = l["project"]
        if p not in project_stats:
            project_stats[p] = {"tp": 0, "fp": 0}
        if l["label"] == "tp":
            project_stats[p]["tp"] += 1
        else:
            project_stats[p]["fp"] += 1
    for p in sorted(project_stats.keys()):
        s = project_stats[p]
        total = s["tp"] + s["fp"]
        precision = s["tp"] / total if total > 0 else 0
        print(f"{p:<22} {s['tp']:>4} {s['fp']:>4} {precision:>9.1%}")

    # Write summary
    summary = {
        "total_labelled": len(labelled),
        "total_unlabelled": len(unlabelled),
        "overall_precision": round(overall_precision, 3),
        "by_tier": {t: {"tp": s["tp"], "fp": s["fp"],
                        "precision": round(s["tp"] / (s["tp"] + s["fp"]), 3) if (s["tp"] + s["fp"]) > 0 else 0}
                    for t, s in tier_stats.items()},
        "by_project": {p: {"tp": s["tp"], "fp": s["fp"],
                           "precision": round(s["tp"] / (s["tp"] + s["fp"]), 3) if (s["tp"] + s["fp"]) > 0 else 0}
                       for p, s in project_stats.items()},
    }
    summary_path = RESULTS_DIR / "PRECISION.json"
    summary_path.write_text(json.dumps(summary, indent=2))
    print(f"\nPrecision summary written to {summary_path}")


def main():
    parser = argparse.ArgumentParser(description="Regula benchmark finding labeller")
    sub = parser.add_subparsers(dest="command")

    p_sample = sub.add_parser("sample", help="Sample findings for labelling")
    p_sample.add_argument("--per-project", type=int, default=50,
                          help="Number of samples per project (default: 50)")

    sub.add_parser("score", help="Calculate precision from labels")

    args = parser.parse_args()
    if args.command == "sample":
        cmd_sample(args)
    elif args.command == "score":
        cmd_score(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
