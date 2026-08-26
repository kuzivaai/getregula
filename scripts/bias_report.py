#!/usr/bin/env python3
"""
Multi-benchmark bias report formatting.

Produces text, JSON, and Annex IV documentation from CrowS-Pairs
and BBQ evaluation results.
"""

import platform
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional

sys.path.insert(0, str(Path(__file__).parent))


def build_reproducibility_metadata(
    model: str,
    endpoint: str,
    seed: Optional[int] = None,
) -> Dict:
    """Build reproducibility metadata for a bias evaluation run."""
    try:
        from constants import VERSION
    except ImportError:
        VERSION = "unknown"

    return {
        "model": model,
        "endpoint": endpoint,
        "seed": seed,
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "regula_version": VERSION,
        "python_version": platform.python_version(),
        "platform": platform.platform(),
    }


def format_text_report(
    crowspairs: Optional[Dict],
    bbq: Optional[Dict],
    model: str,
    endpoint: str,
) -> str:
    """Format multi-benchmark bias report as human-readable text."""
    lines = []
    lines.append(f"Regula Bias Report — {model} @ {endpoint}")
    lines.append("=" * 60)
    lines.append("")

    if crowspairs and crowspairs.get("status") == "ok":
        lines.append("Benchmark 1: CrowS-Pairs (Likelihood Scoring)")
        lines.append(f"Method: {crowspairs['method_description']}")
        lines.append(f"Pairs evaluated: {crowspairs['pairs_evaluated']}")
        lines.append("")
        lines.append(f"{'Category':<25} {'Score':>6}  {'95% CI':<16} {'N':>4}  {'Confidence'}")
        lines.append("-" * 72)
        for cat, data in sorted(crowspairs["scores"].items()):
            ci_str = f"[{data['ci_lower']:.0%}, {data['ci_upper']:.0%}]"
            lines.append(f"{cat:<25} {data['score']:>5}%  {ci_str:<16} {data['n']:>4}  {data['confidence']}")
        lines.append("-" * 72)
        oci = crowspairs.get("overall_ci", {})
        ci_str = f"[{oci.get('lower', 0):.0f}%, {oci.get('upper', 100):.0f}%]" if oci else ""
        lines.append(f"{'Overall':<25} {crowspairs['overall_score']:>5}%  {ci_str}")
        if crowspairs.get("categories_excluded"):
            lines.append(f"  Excluded (insufficient data): {', '.join(crowspairs['categories_excluded'])}")
        lines.append("")

    if bbq and bbq.get("status") == "ok":
        lines.append("Benchmark 2: BBQ (Question Answering)")
        lines.append(f"Items evaluated: {bbq['items_evaluated']}")
        lines.append("")

        if bbq["scores"].get("ambiguous"):
            lines.append("Ambiguous contexts (ideal: model says 'unknown'):")
            lines.append(f"{'Category':<25} {'Bias':>6}  {'95% CI':<16} {'N':>4}  {'Confidence'}")
            lines.append("-" * 72)
            for cat, data in sorted(bbq["scores"]["ambiguous"].items()):
                ci_str = f"[{data['ci_lower']:.0%}, {data['ci_upper']:.0%}]"
                lines.append(f"{cat:<25} {data['bias_score']:>5}%  {ci_str:<16} {data['n']:>4}  {data['confidence']}")
            lines.append("")

        if bbq["scores"].get("disambiguated"):
            lines.append("Disambiguated contexts (ideal: model answers correctly):")
            lines.append(f"{'Category':<25} {'Acc':>5}  {'Bias Override':>14}  {'N':>4}  {'Confidence'}")
            lines.append("-" * 72)
            for cat, data in sorted(bbq["scores"]["disambiguated"].items()):
                lines.append(f"{cat:<25} {data['accuracy']:>4}%  {data['bias_override_rate']:>13}%  {data['n']:>4}  {data['confidence']}")
            lines.append("")

        lines.append(f"Overall ambiguous bias: {bbq['overall_ambiguous_bias']}% (0% = no bias)")
        lines.append(f"Overall disambiguated accuracy: {bbq['overall_disambiguated_accuracy']}%")
        lines.append("")

    lines.append("Limitations:")
    all_limitations = set()
    if crowspairs and crowspairs.get("limitations"):
        all_limitations.update(crowspairs["limitations"])
    if bbq and bbq.get("limitations"):
        all_limitations.update(bbq["limitations"])
    all_limitations.add("Neither benchmark constitutes a complete Article 10 bias assessment")
    for lim in sorted(all_limitations):
        lines.append(f"  - {lim}")
    lines.append("")

    citations = []
    if crowspairs:
        citations.append(crowspairs.get("citation", ""))
    if bbq:
        citations.append(bbq.get("citation", ""))
    if citations:
        lines.append(f"Citations: {'; '.join(c for c in citations if c)}")

    return "\n".join(lines)


def format_json_report(
    crowspairs: Optional[Dict],
    bbq: Optional[Dict],
    model: str,
    endpoint: str,
    seed: Optional[int] = None,
) -> Dict:
    """Format multi-benchmark bias report as structured JSON."""
    benchmarks = {}
    if crowspairs:
        benchmarks["crowspairs"] = crowspairs
    if bbq:
        benchmarks["bbq"] = bbq

    return {
        "benchmarks": benchmarks,
        "reproducibility": build_reproducibility_metadata(model, endpoint, seed),
    }


def format_annex_iv(
    crowspairs: Optional[Dict],
    bbq: Optional[Dict],
    model: str,
    endpoint: str,
) -> str:
    """Format bias results as an Annex IV section 2 technical documentation section."""
    lines = []
    lines.append("## Examination for Possible Biases (Article 10, Annex IV §2)")
    lines.append("")
    lines.append("### Methodology")
    lines.append("")
    lines.append("Two complementary benchmarks were used to examine the AI system for social biases:")
    lines.append("")

    if crowspairs and crowspairs.get("status") == "ok":
        lines.append(f"1. **CrowS-Pairs** (Nangia et al., 2020, EMNLP): {crowspairs['pairs_evaluated']} sentence pairs "
                     f"evaluated using {crowspairs['method_description']}. Each pair compares a stereotyped sentence "
                     f"against an anti-stereotyped variant. Score of 50% indicates no bias.")
        lines.append("")

    if bbq and bbq.get("status") == "ok":
        lines.append(f"2. **BBQ** (Parrish et al., 2022, ACL Findings): {bbq['items_evaluated']} question-answering items "
                     f"testing whether the model relies on stereotypes when answering ambiguous questions. "
                     f"Measures downstream QA behaviour rather than internal likelihood preferences.")
        lines.append("")

    lines.append("### Results")
    lines.append("")

    if crowspairs and crowspairs.get("status") == "ok":
        lines.append("**CrowS-Pairs (Stereotype Likelihood):**")
        lines.append("")
        lines.append("| Category | Score | 95% CI | N | Confidence |")
        lines.append("|----------|-------|--------|---|------------|")
        for cat, data in sorted(crowspairs["scores"].items()):
            ci = f"[{data['ci_lower']:.0%}, {data['ci_upper']:.0%}]"
            lines.append(f"| {cat} | {data['score']}% | {ci} | {data['n']} | {data['confidence']} |")
        oci = crowspairs.get("overall_ci", {})
        lines.append(f"\nOverall: {crowspairs['overall_score']}% [{oci.get('lower', 0):.0f}%, {oci.get('upper', 100):.0f}%]")
        lines.append("")

    if bbq and bbq.get("status") == "ok":
        lines.append("**BBQ (Question Answering Behaviour):**")
        lines.append(f"\nOverall ambiguous bias: {bbq['overall_ambiguous_bias']}%")
        lines.append(f"Overall disambiguated accuracy: {bbq['overall_disambiguated_accuracy']}%")
        lines.append("")

    lines.append("### Limitations")
    lines.append("")
    lines.append("- CrowS-Pairs has documented reliability issues (Blodgett et al., ACL 2021)")
    lines.append("- Both benchmarks are English-only and US-centric")
    lines.append("- Bundled sample subsets — not full datasets")
    lines.append("- Automated benchmarks measure representational/behavioural bias in language; "
                 "they do not assess real-world discriminatory impact in the deployment context")
    lines.append("- This evaluation does not measure fairness metrics (demographic parity, equalized odds)")
    lines.append("- Single-run results; production monitoring requires repeated evaluation")
    lines.append("")

    lines.append("### Recommended Follow-Up")
    lines.append("")
    lines.append("1. Test with the provider's actual training/evaluation data (not just benchmarks)")
    lines.append("2. Evaluate bias in the specific deployment language(s) and cultural context")
    lines.append("3. Measure fairness metrics relevant to the use case and jurisdiction")
    lines.append("4. Conduct human review of model outputs in high-risk scenarios")
    lines.append("5. Establish ongoing monitoring for bias drift in production")

    return "\n".join(lines)
