#!/usr/bin/env python3
# regula-ignore
"""Compare re-scanned results against BLIND_LABELS to measure precision.

For each labelled finding, checks whether it still appears in the new scan.
Calculates precision per tier and overall, comparing old vs new.

Usage:
    python3 benchmarks/compare_precision.py
"""
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
LABELS_PATH = ROOT / "benchmarks" / "results" / "random_corpus" / "BLIND_LABELS.json"
OLD_PRECISION = ROOT / "benchmarks" / "results" / "random_corpus" / "PRECISION.json"
NEW_RESULTS_DIR = ROOT / "benchmarks" / "results" / "random_corpus_v2"


def _wilson_ci(p, n, z=1.96):
    """Wilson score interval for binomial proportion."""
    if n == 0:
        return 0, 0
    denom = 1 + z**2 / n
    centre = (p + z**2 / (2 * n)) / denom
    spread = z * math.sqrt((p * (1 - p) + z**2 / (4 * n)) / n) / denom
    return max(0, centre - spread), min(1, centre + spread)


def load_new_findings():
    """Load all findings from the v2 re-scan."""
    all_findings = []
    for f in sorted(NEW_RESULTS_DIR.glob("*.json")):
        if f.name in ("SUMMARY.json", "PRECISION_COMPARISON.json"):
            continue
        data = json.loads(f.read_text())
        if not isinstance(data, list):
            continue
        # Tag each finding with the repo slug
        slug = f.stem.replace("__", "/")
        for finding in data:
            finding["_repo"] = slug
        all_findings.extend(data)
    return all_findings


def match_label_to_findings(label, repo_findings):
    """Check if a labelled finding still exists in the new scan results.

    Matching strategy: same file + same tier + overlapping indicators.
    """
    label_file = label["file"]
    label_tier = label["tier"]
    label_indicators = set(label.get("indicators", []))

    for f in repo_findings:
        if f.get("tier") != label_tier:
            continue
        if f.get("file") != label_file:
            continue
        f_indicators = set(f.get("indicators", []))
        if f_indicators & label_indicators:
            return True
    return False


def main():
    labels = json.loads(LABELS_PATH.read_text())
    new_findings = load_new_findings()

    # Group new findings by repo
    by_repo = {}
    for f in new_findings:
        repo = f.get("_repo", "")
        by_repo.setdefault(repo, []).append(f)

    # Map label repos to scan repos
    # Labels don't have repo info directly — need to infer from file paths
    # The label IDs correspond to the METHODOLOGY repo order
    method_path = ROOT / "benchmarks" / "results" / "random_corpus" / "METHODOLOGY.json"
    method = json.loads(method_path.read_text())
    repos = method["selection_repos"]

    # Load per-repo scan results to match labels
    # Each original scan result has the repo-specific findings
    old_results_dir = ROOT / "benchmarks" / "results" / "random_corpus"

    # Build a lookup: for each label, find which repo it came from
    # by checking which old result file contains a matching finding
    label_to_repo = {}
    for repo_slug in repos:
        safe_name = repo_slug.replace("/", "__")
        old_path = old_results_dir / f"{safe_name}.json"
        if not old_path.exists():
            continue
        old_findings = json.loads(old_path.read_text())
        for label in labels:
            if label["id"] in label_to_repo:
                continue
            label_file = label["file"]
            label_tier = label["tier"]
            label_indicators = set(label.get("indicators", []))
            for of in old_findings:
                if (of.get("file") == label_file
                        and of.get("tier") == label_tier
                        and set(of.get("indicators", [])) & label_indicators):
                    label_to_repo[label["id"]] = repo_slug
                    break

    # Now check each label against new findings
    still_emitted = {}
    for label in labels:
        lid = label["id"]
        repo = label_to_repo.get(lid)
        if repo is None:
            still_emitted[lid] = "unknown_repo"
            continue
        repo_findings = by_repo.get(repo, [])
        if match_label_to_findings(label, repo_findings):
            still_emitted[lid] = True
        else:
            still_emitted[lid] = False

    # Calculate precision
    print("=" * 60)
    print("PRECISION COMPARISON: Old (70%) vs New (domain-gated)")
    print("=" * 60)

    tiers = {}
    for label in labels:
        tier = label["tier"]
        tiers.setdefault(tier, {"old_tp": 0, "old_fp": 0, "new_tp": 0, "new_fp": 0})
        is_tp = label["label"] == "tp"
        emitted = still_emitted.get(label["id"])

        if is_tp:
            tiers[tier]["old_tp"] += 1
            if emitted is True:
                tiers[tier]["new_tp"] += 1
        else:
            tiers[tier]["old_fp"] += 1
            if emitted is True:
                tiers[tier]["new_fp"] += 1

    # Print per-tier
    total_old_tp = 0
    total_old_fp = 0
    total_new_tp = 0
    total_new_fp = 0
    unknown = sum(1 for v in still_emitted.values() if v == "unknown_repo")

    for tier in sorted(tiers.keys()):
        t = tiers[tier]
        old_total = t["old_tp"] + t["old_fp"]
        old_prec = t["old_tp"] / old_total if old_total > 0 else 0
        new_total = t["new_tp"] + t["new_fp"]
        new_prec = t["new_tp"] / new_total if new_total > 0 else 0

        removed_fp = t["old_fp"] - t["new_fp"]
        removed_tp = t["old_tp"] - t["new_tp"]

        print(f"\n{tier}:")
        print(f"  OLD: {t['old_tp']} TP, {t['old_fp']} FP = {old_prec:.1%} ({old_total} total)")
        print(f"  NEW: {t['new_tp']} TP, {t['new_fp']} FP = {new_prec:.1%} ({new_total} total)")
        print(f"  Removed: {removed_fp} FP, {removed_tp} TP")

        total_old_tp += t["old_tp"]
        total_old_fp += t["old_fp"]
        total_new_tp += t["new_tp"]
        total_new_fp += t["new_fp"]

    # Overall
    old_total = total_old_tp + total_old_fp
    new_total = total_new_tp + total_new_fp
    old_prec = total_old_tp / old_total if old_total > 0 else 0
    new_prec = total_new_tp / new_total if new_total > 0 else 0

    ci_low, ci_high = _wilson_ci(new_prec, new_total)

    print(f"\n{'=' * 60}")
    print(f"OVERALL:")
    print(f"  OLD: {total_old_tp} TP, {total_old_fp} FP = {old_prec:.1%} (N={old_total})")
    print(f"  NEW: {total_new_tp} TP, {total_new_fp} FP = {new_prec:.1%} (N={new_total})")
    print(f"  95% CI: {ci_low:.1%} - {ci_high:.1%}")
    print(f"  FP removed: {total_old_fp - total_new_fp}")
    print(f"  TP lost: {total_old_tp - total_new_tp}")
    if unknown:
        print(f"  Labels with unknown repo: {unknown}")
    print(f"{'=' * 60}")

    # Save results
    result = {
        "methodology": "Re-scan of random corpus with domain-gated Regula, compared against existing BLIND_LABELS",
        "date": __import__("time").strftime("%Y-%m-%d"),
        "sample_size_labelled": len(labels),
        "labels_matched": sum(1 for v in still_emitted.values() if v is not False and v != "unknown_repo"),
        "labels_suppressed": sum(1 for v in still_emitted.values() if v is False),
        "labels_unmatched": unknown,
        "old_precision": round(old_prec, 3),
        "new_precision": round(new_prec, 3),
        "ci_95_low": round(ci_low * 100, 1),
        "ci_95_high": round(ci_high * 100, 1),
        "by_tier": {
            tier: {
                "old_tp": t["old_tp"], "old_fp": t["old_fp"],
                "old_precision": round(t["old_tp"] / (t["old_tp"] + t["old_fp"]), 3) if (t["old_tp"] + t["old_fp"]) > 0 else 0,
                "new_tp": t["new_tp"], "new_fp": t["new_fp"],
                "new_precision": round(t["new_tp"] / (t["new_tp"] + t["new_fp"]), 3) if (t["new_tp"] + t["new_fp"]) > 0 else 0,
            }
            for tier, t in sorted(tiers.items())
        },
    }
    out_path = NEW_RESULTS_DIR / "PRECISION_COMPARISON.json"
    out_path.write_text(json.dumps(result, indent=2))
    print(f"\nSaved to {out_path}")


if __name__ == "__main__":
    main()
