#!/usr/bin/env python3
"""
Benchmark finding labeller for Regula.

Samples findings from benchmark results and generates a labelling sheet.
After manual labelling, calculates precision metrics per tier, category,
language, and corpus type.

Usage:
    # Generate labelling sheet (50 samples per project)
    python3 benchmarks/label.py sample --per-project 50

    # Sample only app-level results
    python3 benchmarks/label.py sample --corpus app --per-project 30

    # Calculate precision from completed labels
    python3 benchmarks/label.py score

    # Score only app corpus
    python3 benchmarks/label.py score --corpus app

    # Score with category and language breakdowns
    python3 benchmarks/label.py score --breakdown
"""

import argparse
import json
import math
import os
import random
import sys
from pathlib import Path

RESULTS_DIR = Path(__file__).parent / "results"
LABELS_FILE = Path(__file__).parent / "labels.json"

# Files to skip when scanning results
SKIP_FILES = {"SUMMARY.json", "PRECISION.json"}

# App-level projects have "app_" prefix in their result filename
APP_PREFIX = "app_"


def _classify_corpus(project_name):
    """Classify a project as 'app' or 'library' based on naming convention."""
    if project_name.startswith(APP_PREFIX):
        return "app"
    return "library"


def _file_language(filepath):
    """Infer language from file extension."""
    ext_map = {
        "py": "Python",
        "js": "JavaScript",
        "ts": "TypeScript",
        "tsx": "TypeScript",
        "jsx": "JavaScript",
        "java": "Java",
        "kt": "Kotlin",
        "rb": "Ruby",
        "go": "Go",
        "rs": "Rust",
        "cpp": "C++",
        "c": "C",
        "cs": "C#",
        "php": "PHP",
        "swift": "Swift",
        "r": "R",
        "jl": "Julia",
        "scala": "Scala",
        "ipynb": "Jupyter",
    }
    ext = filepath.rsplit(".", 1)[-1].lower() if "." in filepath else ""
    return ext_map.get(ext, ext.upper() if ext else "Unknown")


def _precision(tp, fp):
    total = tp + fp
    return tp / total if total > 0 else 0.0


def _collect_result_files(corpus_filter="all"):
    """Collect result JSON files, optionally filtered by corpus type."""
    files = []
    for result_file in sorted(RESULTS_DIR.glob("*.json")):
        if result_file.name in SKIP_FILES:
            continue
        project = result_file.stem
        corpus = _classify_corpus(project)
        if corpus_filter != "all" and corpus != corpus_filter:
            continue
        files.append(result_file)
    return files


def cmd_sample(args):
    """Sample findings from benchmark results for manual labelling."""
    per_project = args.per_project
    corpus_filter = args.corpus

    all_samples = []
    result_files = _collect_result_files(corpus_filter)

    for result_file in result_files:
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
                    "category": f.get("category", ""),
                    "description": f.get("description", "")[:120],
                    "confidence_score": f.get("confidence_score", 0),
                    "indicators": f.get("indicators", []),
                    "label": None,  # TO BE FILLED: "tp" or "fp"
                    "notes": "",    # Optional human notes
                })
                sampled += 1

        corpus = _classify_corpus(project)
        print(f"{project} [{corpus}]: {sampled} samples from {total} findings ({len(by_tier)} tiers)")

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
    seen_keys = set()
    for s in all_samples:
        key = f"{s['project']}:{s['file']}:{s['tier']}"
        if key in seen_keys:
            continue
        seen_keys.add(key)
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
    print(f"\nLabelling criteria: see benchmarks/LABELLING_CRITERIA.md")


def _accumulate(stats_dict, key, label):
    """Increment TP or FP count for a stats bucket."""
    if key not in stats_dict:
        stats_dict[key] = {"tp": 0, "fp": 0}
    if label == "tp":
        stats_dict[key]["tp"] += 1
    else:
        stats_dict[key]["fp"] += 1


def _print_table(title, stats_dict, min_col_width=30):
    """Print a precision table for a stats dictionary."""
    if not stats_dict:
        return
    print(f"\n{title}")
    print(f"{'':─<{min_col_width}} {'TP':>4} {'FP':>4} {'Total':>6} {'Precision':>10}")

    overall_tp = 0
    overall_fp = 0
    for key in sorted(stats_dict.keys()):
        s = stats_dict[key]
        total = s["tp"] + s["fp"]
        precision = _precision(s["tp"], s["fp"])
        overall_tp += s["tp"]
        overall_fp += s["fp"]
        display_key = key[:min_col_width]
        print(f"{display_key:<{min_col_width}} {s['tp']:>4} {s['fp']:>4} {total:>6} {precision:>9.1%}")

    overall_total = overall_tp + overall_fp
    overall_precision = _precision(overall_tp, overall_fp)
    print(f"{'':─<{min_col_width}} {'':─>4} {'':─>4} {'':─>6} {'':─>10}")
    print(f"{'OVERALL':<{min_col_width}} {overall_tp:>4} {overall_fp:>4} {overall_total:>6} {overall_precision:>9.1%}")
    return {"tp": overall_tp, "fp": overall_fp, "precision": round(overall_precision, 3)}


def _json_stats(stats_dict):
    """Convert stats dict to JSON-serialisable dict with precision."""
    return {k: {"tp": s["tp"], "fp": s["fp"],
                "precision": round(_precision(s["tp"], s["fp"]), 3)}
            for k, s in stats_dict.items()}


def cmd_score(args):
    """Calculate precision per tier from labelled findings."""
    if not LABELS_FILE.exists():
        print(f"No labels file found at {LABELS_FILE}")
        print("Run: python3 benchmarks/label.py sample --per-project 50")
        sys.exit(1)

    labels = json.load(LABELS_FILE.open())
    corpus_filter = args.corpus
    breakdown = args.breakdown

    # Filter by corpus type
    if corpus_filter != "all":
        labels = [l for l in labels if _classify_corpus(l["project"]) == corpus_filter]

    labelled = [l for l in labels if l.get("label") in ("tp", "fp")]
    unlabelled = [l for l in labels if not l.get("label")]

    if not labelled:
        print("No labelled findings yet. Open labels.json and set 'label' to 'tp' or 'fp'.")
        sys.exit(1)

    corpus_label = f" [{corpus_filter}]" if corpus_filter != "all" else ""
    print(f"Labelled{corpus_label}: {len(labelled)} / {len(labelled) + len(unlabelled)}"
          f" ({len(unlabelled)} remaining)\n")

    # Per-tier precision
    tier_stats = {}
    project_stats = {}
    category_stats = {}
    language_stats = {}

    for l in labelled:
        _accumulate(tier_stats, l["tier"], l["label"])
        _accumulate(project_stats, l["project"], l["label"])

        # Category (may not exist in older labels)
        cat = l.get("category", "")
        if cat:
            _accumulate(category_stats, cat, l["label"])

        # Language from file extension
        lang = _file_language(l.get("file", ""))
        _accumulate(language_stats, lang, l["label"])

    # Print tier table
    tier_totals = _print_table("Precision by Tier", tier_stats, 22)

    # Print project table
    _print_table("\nPrecision by Project", project_stats, 22)

    if breakdown:
        # Print category table
        if category_stats:
            _print_table("\nPrecision by Category", category_stats, 50)
        else:
            print("\nNo category data in labels (older format). Re-sample to add categories.")

        # Print language table
        if language_stats:
            _print_table("\nPrecision by Language", language_stats, 15)

    # Corpus comparison (only when scoring 'all')
    if corpus_filter == "all":
        corpus_stats = {}
        for l in labelled:
            corpus_type = _classify_corpus(l["project"])
            _accumulate(corpus_stats, corpus_type, l["label"])
        if len(corpus_stats) > 1:
            _print_table("\nPrecision by Corpus Type", corpus_stats, 15)

    # Metrics note
    overall_tp = tier_totals["tp"] if tier_totals else 0
    overall_fp = tier_totals["fp"] if tier_totals else 0
    overall_precision = tier_totals["precision"] if tier_totals else 0

    print(f"\n── Additional Metrics ──")
    print(f"Precision: {overall_precision:.1%} (measured)")
    print(f"Recall:    N/A (requires planted corpus with known FN count)")
    print(f"F1 Score:  N/A (requires recall)")
    print(f"Youden J:  N/A (requires TN count — OWASP Benchmark standard)")
    print(f"MCC:       N/A (requires TN and FN counts)")
    print(f"\nTo compute recall-dependent metrics, build a planted corpus")
    print(f"with known issues and run: python3 benchmarks/label.py recall")

    # Write summary
    summary = {
        "corpus": corpus_filter,
        "total_labelled": len(labelled),
        "total_unlabelled": len(unlabelled),
        "overall_precision": round(overall_precision, 3),
        "by_tier": _json_stats(tier_stats),
        "by_project": _json_stats(project_stats),
    }
    if category_stats:
        summary["by_category"] = _json_stats(category_stats)
    if language_stats:
        summary["by_language"] = _json_stats(language_stats)

    summary_path = RESULTS_DIR / "PRECISION.json"
    summary_path.write_text(json.dumps(summary, indent=2))
    print(f"\nPrecision summary written to {summary_path}")


def cmd_recall(args):
    """Measure recall using the synthetic corpus with known ground truth."""
    synthetic_dir = Path(__file__).parent / "synthetic"
    manifest_path = synthetic_dir / "manifest.json"

    if not manifest_path.exists():
        print(f"No synthetic manifest at {manifest_path}")
        sys.exit(1)

    manifest = json.load(manifest_path.open())
    print(f"Synthetic corpus: {len(manifest.get('fixtures', []))} fixtures")
    print(f"\nRecall measurement from synthetic fixtures is available via:")
    print(f"  python3 benchmarks/synthetic/run.py")
    print(f"\nThis runs Regula against controlled fixtures with known issues")
    print(f"and measures detection rate (recall) per tier.")
    print(f"\nNote: Synthetic recall + labelled precision can yield F1, but")
    print(f"the corpora differ, so the F1 is approximate, not rigorous.")


def cmd_compare(args):
    """Compare precision between two PRECISION.json snapshots."""
    baseline_path = Path(args.baseline)
    if not baseline_path.exists():
        print(f"Baseline not found: {baseline_path}")
        sys.exit(1)

    current_path = RESULTS_DIR / "PRECISION.json"
    if not current_path.exists():
        print("No current PRECISION.json. Run: python3 benchmarks/label.py score")
        sys.exit(1)

    baseline = json.load(baseline_path.open())
    current = json.load(current_path.open())

    print(f"{'Metric':<25} {'Baseline':>10} {'Current':>10} {'Delta':>10}")
    print(f"{'-'*25} {'-'*10} {'-'*10} {'-'*10}")

    b_prec = baseline.get("overall_precision", 0)
    c_prec = current.get("overall_precision", 0)
    delta = c_prec - b_prec
    direction = "↑" if delta > 0 else "↓" if delta < 0 else "="
    print(f"{'Overall precision':<25} {b_prec:>9.1%} {c_prec:>9.1%} {delta:>+9.1%} {direction}")

    b_n = baseline.get("total_labelled", 0)
    c_n = current.get("total_labelled", 0)
    print(f"{'Labelled findings':<25} {b_n:>10} {c_n:>10} {c_n - b_n:>+10}")

    # Per-tier comparison
    all_tiers = set(list(baseline.get("by_tier", {}).keys()) +
                    list(current.get("by_tier", {}).keys()))
    if all_tiers:
        print(f"\n{'Tier':<25} {'Baseline':>10} {'Current':>10} {'Delta':>10}")
        print(f"{'-'*25} {'-'*10} {'-'*10} {'-'*10}")
        for tier in sorted(all_tiers):
            b_t = baseline.get("by_tier", {}).get(tier, {}).get("precision", 0)
            c_t = current.get("by_tier", {}).get(tier, {}).get("precision", 0)
            d = c_t - b_t
            direction = "↑" if d > 0.001 else "↓" if d < -0.001 else "="
            print(f"{tier:<25} {b_t:>9.1%} {c_t:>9.1%} {d:>+9.1%} {direction}")


def cmd_compare_human(args):
    """Compare AI labels with human labels and compute Cohen's kappa."""
    human_path = Path(args.human_file)
    if not human_path.exists():
        print(f"Human labelling sheet not found: {human_path}")
        sys.exit(1)

    human = json.load(human_path.open())
    human_labels = {h["id"]: h.get("your_label", "").strip().lower()
                    for h in human if h.get("your_label", "").strip().lower() in ("tp", "fp")}

    if not human_labels:
        print("No human labels found. Fill in 'your_label' with 'tp' or 'fp' in the sheet.")
        sys.exit(1)

    # Load AI blind labels
    blind_path = Path(__file__).parent / "results" / "random_corpus" / "BLIND_LABELS.json"
    if not blind_path.exists():
        print(f"AI blind labels not found at {blind_path}")
        sys.exit(1)

    ai_labels_list = json.load(blind_path.open())
    ai_labels = {a["id"]: a.get("label", "").strip().lower()
                 for a in ai_labels_list if a.get("label") in ("tp", "fp")}

    # Find overlapping IDs
    common = set(human_labels.keys()) & set(ai_labels.keys())
    if not common:
        print("No overlapping IDs between human and AI labels.")
        sys.exit(1)

    print(f"Comparing {len(common)} findings labelled by both human and AI\n")

    # Agreement matrix
    agree = 0
    disagree = 0
    both_tp = both_fp = human_tp_ai_fp = human_fp_ai_tp = 0

    for fid in sorted(common):
        h = human_labels[fid]
        a = ai_labels[fid]
        if h == a:
            agree += 1
            if h == "tp":
                both_tp += 1
            else:
                both_fp += 1
        else:
            disagree += 1
            if h == "tp" and a == "fp":
                human_tp_ai_fp += 1
            else:
                human_fp_ai_tp += 1

    total = agree + disagree
    raw_agreement = agree / total if total > 0 else 0

    # Cohen's kappa
    p_human_tp = (both_tp + human_tp_ai_fp) / total if total > 0 else 0
    p_ai_tp = (both_tp + human_fp_ai_tp) / total if total > 0 else 0
    p_human_fp = 1 - p_human_tp
    p_ai_fp = 1 - p_ai_tp
    p_e = (p_human_tp * p_ai_tp) + (p_human_fp * p_ai_fp)
    kappa = (raw_agreement - p_e) / (1 - p_e) if (1 - p_e) > 0 else 0

    print(f"{'':─<30}")
    print(f"{'Agreement matrix':^30}")
    print(f"{'':─<30}")
    print(f"{'':15s} {'AI: TP':>7} {'AI: FP':>7}")
    print(f"{'Human: TP':15s} {both_tp:>7} {human_tp_ai_fp:>7}")
    print(f"{'Human: FP':15s} {human_fp_ai_tp:>7} {both_fp:>7}")
    print(f"{'':─<30}")
    print(f"\nRaw agreement: {raw_agreement:.1%} ({agree}/{total})")
    print(f"Cohen's kappa: {kappa:.3f}")

    # Interpret kappa
    if kappa < 0.20:
        interp = "Poor"
    elif kappa < 0.40:
        interp = "Fair"
    elif kappa < 0.60:
        interp = "Moderate"
    elif kappa < 0.80:
        interp = "Substantial"
    else:
        interp = "Almost perfect"
    print(f"Interpretation: {interp} agreement (Landis & Koch 1977)")

    # Per-label precision comparison
    h_tp = sum(1 for fid in common if human_labels[fid] == "tp")
    h_fp = sum(1 for fid in common if human_labels[fid] == "fp")
    a_tp = sum(1 for fid in common if ai_labels[fid] == "tp")
    a_fp = sum(1 for fid in common if ai_labels[fid] == "fp")

    h_prec = h_tp / (h_tp + h_fp) if (h_tp + h_fp) > 0 else 0
    a_prec = a_tp / (a_tp + a_fp) if (a_tp + a_fp) > 0 else 0

    print(f"\nHuman precision: {h_prec:.1%} ({h_tp} TP / {h_fp} FP)")
    print(f"AI precision:    {a_prec:.1%} ({a_tp} TP / {a_fp} FP)")
    print(f"Delta:           {a_prec - h_prec:+.1%}")

    if disagree > 0:
        print(f"\nDisagreements ({disagree}):")
        for fid in sorted(common):
            if human_labels[fid] != ai_labels[fid]:
                h_entry = next((h for h in human if h["id"] == fid), {})
                a_entry = next((a for a in ai_labels_list if a["id"] == fid), {})
                print(f"  {fid}: human={human_labels[fid]}, ai={ai_labels[fid]}"
                      f"  [{h_entry.get('tier', '')}] {h_entry.get('file', '')[:40]}")


def main():
    parser = argparse.ArgumentParser(description="Regula benchmark finding labeller")
    sub = parser.add_subparsers(dest="command")

    p_sample = sub.add_parser("sample", help="Sample findings for labelling")
    p_sample.add_argument("--per-project", type=int, default=50,
                          help="Number of samples per project (default: 50)")
    p_sample.add_argument("--corpus", choices=["library", "app", "all"],
                          default="all", help="Corpus type to sample (default: all)")

    p_score = sub.add_parser("score", help="Calculate precision from labels")
    p_score.add_argument("--corpus", choices=["library", "app", "all"],
                         default="all", help="Filter by corpus type (default: all)")
    p_score.add_argument("--breakdown", action="store_true",
                         help="Show per-category and per-language breakdowns")

    sub.add_parser("recall", help="Measure recall from synthetic corpus")

    p_compare = sub.add_parser("compare", help="Compare precision snapshots")
    p_compare.add_argument("baseline", help="Path to baseline PRECISION.json")

    p_human = sub.add_parser("compare-human", help="Compare AI vs human labels (Cohen's kappa)")
    p_human.add_argument("human_file", help="Path to human labelling sheet JSON")

    args = parser.parse_args()
    if args.command == "sample":
        cmd_sample(args)
    elif args.command == "score":
        cmd_score(args)
    elif args.command == "recall":
        cmd_recall(args)
    elif args.command == "compare":
        cmd_compare(args)
    elif args.command == "compare-human":
        cmd_compare_human(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
