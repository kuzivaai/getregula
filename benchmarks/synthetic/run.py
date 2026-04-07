#!/usr/bin/env python3
"""
Synthetic-fixture precision/recall runner.

Scans benchmarks/synthetic/fixtures/ with `regula check`, joins findings
against manifest.json, and reports per-tier precision and recall on a
fully labelled (TP/FP/FN known) corpus.

This complements benchmarks/labels.json (which is real OSS but only
covers minimal/limited/agent_autonomy tiers) by providing measurable
precision and recall for the prohibited and high_risk tiers — the
ones where false negatives have legal consequences and where the
real-OSS benchmark contains zero examples.

The corpus is small (13 fixtures) and synthetic by design. Numbers are
fixture-bound; they tell you whether the prohibited and high_risk
detectors fire on textbook positive cases and stay quiet on textbook
negative cases. They do not generalise to "Regula's precision in the
wild" — the OSS benchmark is the right tool for that.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent
FIXTURES = ROOT / "fixtures"
MANIFEST = ROOT / "manifest.json"

# Use Regula's own scanner
sys.path.insert(0, str(ROOT.parent.parent / "scripts"))
from report import scan_files


def file_to_highest_tier(findings_for_file: list[dict]) -> str:
    """Reduce a file's findings to its highest tier."""
    order = {"prohibited": 4, "high_risk": 3, "limited_risk": 2, "minimal_risk": 1, "not_ai": 0}
    if not findings_for_file:
        return "not_ai"
    return max(findings_for_file, key=lambda f: order.get(f.get("tier", "not_ai"), 0)).get("tier", "not_ai")


def evaluate(verbose: bool = True) -> dict:
    manifest = json.loads(MANIFEST.read_text())
    expectations = manifest["expectations"]

    # Run Regula against the fixture directory
    findings = scan_files(str(FIXTURES))
    by_file: dict[str, list[dict]] = defaultdict(list)
    for f in findings:
        # `file` field is relative to the scanned project root
        rel = f.get("file", "")
        # We want just the basename to match manifest keys
        by_file[Path(rel).name].append(f)

    results = []
    tier_stats: dict[str, dict[str, int]] = defaultdict(lambda: {"tp": 0, "fp": 0, "fn": 0, "tn": 0})

    for fname, expected in expectations.items():
        actual = file_to_highest_tier(by_file.get(fname, []))
        is_negative = expected == "not_high"

        if is_negative:
            # negative fixture: any tier other than prohibited or high_risk is correct
            correct = actual not in ("prohibited", "high_risk")
            verdict = "TN" if correct else "FP"
            # FP attributed to whichever tier was wrongly fired
            if not correct:
                tier_stats[actual]["fp"] += 1
            else:
                # TN counted against both tiers we care about
                tier_stats["prohibited"]["tn"] += 1
                tier_stats["high_risk"]["tn"] += 1
        else:
            correct = actual == expected
            verdict = "TP" if correct else "FN"
            if correct:
                tier_stats[expected]["tp"] += 1
            else:
                tier_stats[expected]["fn"] += 1

        results.append({"file": fname, "expected": expected, "actual": actual, "verdict": verdict})

    if verbose:
        print(f"\n{'File':40s}  {'Expected':12s}  {'Actual':12s}  Verdict")
        print("-" * 80)
        for r in results:
            mark = "✓" if r["verdict"] in ("TP", "TN") else "✗"
            print(f"{mark} {r['file']:38s}  {r['expected']:12s}  {r['actual']:12s}  {r['verdict']}")

        print("\nPer-tier stats (TP/FP/FN/TN):")
        for tier in ("prohibited", "high_risk"):
            s = tier_stats[tier]
            tp, fp, fn, tn = s["tp"], s["fp"], s["fn"], s["tn"]
            prec = tp / (tp + fp) if (tp + fp) else None
            rec = tp / (tp + fn) if (tp + fn) else None
            f1 = (2 * prec * rec / (prec + rec)) if prec and rec else None
            prec_s = f"{prec*100:.0f}%" if prec is not None else "n/a"
            rec_s = f"{rec*100:.0f}%" if rec is not None else "n/a"
            f1_s = f"{f1*100:.0f}%" if f1 is not None else "n/a"
            print(f"  {tier:12s}  tp={tp}  fp={fp}  fn={fn}  tn={tn}  precision={prec_s}  recall={rec_s}  f1={f1_s}")

    return {
        "results": results,
        "tier_stats": dict(tier_stats),
    }


def metrics_dict() -> dict:
    """Return per-tier precision/recall/f1 as a flat dict for tests."""
    out = evaluate(verbose=False)
    summary = {}
    for tier in ("prohibited", "high_risk"):
        s = out["tier_stats"].get(tier, {"tp": 0, "fp": 0, "fn": 0, "tn": 0})
        tp, fp, fn = s["tp"], s["fp"], s["fn"]
        prec = tp / (tp + fp) if (tp + fp) else None
        rec = tp / (tp + fn) if (tp + fn) else None
        summary[tier] = {"tp": tp, "fp": fp, "fn": fn, "tn": s.get("tn", 0), "precision": prec, "recall": rec}
    return summary


if __name__ == "__main__":
    evaluate()
