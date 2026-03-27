#!/usr/bin/env python3
"""
Regula Benchmark — Precision & Recall Measurement Tooling

Scans one or more project directories, produces structured findings, and
outputs reports suitable for manual labelling. After human review, the
labelled results can be re-imported to calculate precision, recall, and F1
scores per risk tier.

Workflow:
  1. Scan projects → structured JSON results
  2. Export CSV for manual labelling
  3. Human labels each finding: tp / fp / debatable
  4. Re-import labelled CSV → calculate metrics

Stdlib only (plus Regula's own modules).
"""

import argparse
import csv
import io
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Import from Regula's own modules
# ---------------------------------------------------------------------------

sys.path.insert(0, str(Path(__file__).parent))

from report import scan_files, SKIP_DIRS, CODE_EXTENSIONS, MODEL_EXTENSIONS
from classify_risk import classify, RiskTier, is_ai_related


# ---------------------------------------------------------------------------
# Context extraction
# ---------------------------------------------------------------------------

def _extract_context(filepath: Path, target_line: int, context_lines: int = 2) -> str:
    """Extract surrounding lines from a file for labeller context.

    Returns up to `context_lines` before and after the target line,
    formatted as a single string with line numbers.
    """
    try:
        lines = filepath.read_text(encoding="utf-8", errors="ignore").splitlines()
    except (PermissionError, OSError):
        return ""

    if not lines:
        return ""

    # Clamp to valid range (target_line is 1-indexed)
    idx = max(0, target_line - 1)
    start = max(0, idx - context_lines)
    end = min(len(lines), idx + context_lines + 1)

    context_parts = []
    for i in range(start, end):
        marker = ">>>" if i == idx else "   "
        context_parts.append(f"{marker} {i + 1:4d} | {lines[i]}")

    return "\n".join(context_parts)


def _find_first_indicator_line(filepath: Path, indicators: list) -> int:
    """Find the first line number where any indicator pattern matches.

    Falls back to line 1 if no match is found or the file is unreadable.
    """
    import re

    if not indicators:
        return 1

    try:
        lines = filepath.read_text(encoding="utf-8", errors="ignore").splitlines()
    except (PermissionError, OSError):
        return 1

    for i, line in enumerate(lines, 1):
        line_lower = line.lower()
        for indicator in indicators:
            # Indicators may be regex-like pattern names; search as substring first
            if indicator.lower() in line_lower:
                return i
            try:
                if re.search(indicator, line_lower):
                    return i
            except re.error:
                pass

    return 1


# ---------------------------------------------------------------------------
# Core benchmark functions
# ---------------------------------------------------------------------------

def benchmark_project(project_path: str) -> dict:
    """Scan a single project and return structured benchmark results.

    Each finding includes surrounding code context for manual labelling.
    The `label` field is null until a human reviewer fills it in.
    """
    project = Path(project_path).resolve()
    if not project.is_dir():
        raise ValueError(f"Project path does not exist or is not a directory: {project}")

    project_name = project.name
    scan_date = datetime.now(timezone.utc).isoformat()

    # Count total files scanned (code + model files, excluding skipped dirs)
    files_scanned = 0
    ai_files_found = 0
    for root, dirs, files in os.walk(project):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for filename in files:
            fp = Path(root) / filename
            if fp.suffix in CODE_EXTENSIONS or fp.suffix.lower() in MODEL_EXTENSIONS:
                files_scanned += 1

    # Run the actual scan
    raw_findings = scan_files(str(project))

    # Track unique AI files
    ai_file_set = set()

    # Enrich findings with context and precise line numbers
    findings = []
    for rf in raw_findings:
        filepath = project / rf["file"]
        ai_file_set.add(rf["file"])

        # Refine the line number: scan_files often reports line 1;
        # try to locate the actual indicator match
        line = rf.get("line", 1)
        if line == 1 and rf.get("indicators"):
            line = _find_first_indicator_line(filepath, rf["indicators"])

        context = _extract_context(filepath, line)

        findings.append({
            "file": rf["file"],
            "line": line,
            "tier": rf["tier"],
            "category": rf.get("category", "Unknown"),
            "indicators": rf.get("indicators", []),
            "confidence_score": rf.get("confidence_score", 0),
            "context": context,
            "description": rf.get("description", ""),
            "suppressed": rf.get("suppressed", False),
            "label": None,  # null = unlabelled; tp / fp / debatable
        })

    ai_files_found = len(ai_file_set)

    # Aggregate stats by tier
    stats = {
        "prohibited": 0,
        "high_risk": 0,
        "limited_risk": 0,
        "minimal_risk": 0,
        "credential_exposure": 0,
    }
    for f in findings:
        tier = f["tier"]
        if tier in stats:
            stats[tier] += 1

    return {
        "project": project_name,
        "path": str(project),
        "scan_date": scan_date,
        "files_scanned": files_scanned,
        "ai_files_found": ai_files_found,
        "findings": findings,
        "stats": stats,
    }


def benchmark_suite(projects: list) -> dict:
    """Run benchmarks across multiple projects.

    Args:
        projects: List of dicts with "name" and "path" keys.

    Returns:
        Aggregate results with per-project breakdowns.
    """
    suite_date = datetime.now(timezone.utc).isoformat()
    project_results = []
    total_files = 0
    total_ai_files = 0
    total_findings = 0
    findings_by_tier = {
        "prohibited": 0,
        "high_risk": 0,
        "limited_risk": 0,
        "minimal_risk": 0,
        "credential_exposure": 0,
    }
    findings_by_category = {}

    for proj in projects:
        name = proj.get("name", Path(proj["path"]).name)
        path = proj["path"]

        print(f"  Scanning: {name} ({path})...", file=sys.stderr)

        try:
            result = benchmark_project(path)
        except (ValueError, OSError) as exc:
            print(f"  SKIPPED: {name} — {exc}", file=sys.stderr)
            continue

        project_results.append(result)
        total_files += result["files_scanned"]
        total_ai_files += result["ai_files_found"]
        total_findings += len(result["findings"])

        for tier, count in result["stats"].items():
            findings_by_tier[tier] = findings_by_tier.get(tier, 0) + count

        for f in result["findings"]:
            cat = f.get("category", "Unknown")
            findings_by_category[cat] = findings_by_category.get(cat, 0) + 1

    return {
        "suite_date": suite_date,
        "projects_scanned": len(project_results),
        "total_files": total_files,
        "total_ai_files": total_ai_files,
        "total_findings": total_findings,
        "findings_by_tier": findings_by_tier,
        "findings_by_category": findings_by_category,
        "projects": project_results,
        # Populated after manual labelling:
        "precision": None,
        "recall": None,
        "labelled_count": 0,
    }


# ---------------------------------------------------------------------------
# Labelling and metrics
# ---------------------------------------------------------------------------

def load_labelled_results(path: str) -> dict:
    """Load previously saved benchmark results with manual labels applied.

    Supports two formats:
      - JSON: Full benchmark output (project or suite) with label fields filled.
      - CSV: Re-import a labelled CSV exported by format_labelling_csv().
    """
    filepath = Path(path)
    if not filepath.exists():
        raise FileNotFoundError(f"Results file not found: {path}")

    content = filepath.read_text(encoding="utf-8")

    if filepath.suffix == ".json":
        data = json.loads(content)
        # Could be a single project result or a suite result
        return data

    if filepath.suffix == ".csv":
        return _import_labelled_csv(content)

    raise ValueError(f"Unsupported file format: {filepath.suffix} (expected .json or .csv)")


def _import_labelled_csv(csv_content: str) -> dict:
    """Parse a labelled CSV back into a findings structure.

    The CSV must have columns: project, file, line, tier, category,
    indicators, context, confidence_score, label
    """
    reader = csv.DictReader(io.StringIO(csv_content))

    projects = {}
    for row in reader:
        proj_name = row.get("project", "unknown")
        if proj_name not in projects:
            projects[proj_name] = {
                "project": proj_name,
                "path": "",
                "scan_date": "",
                "files_scanned": 0,
                "ai_files_found": 0,
                "findings": [],
                "stats": {},
            }

        label = row.get("label", "").strip().lower()
        if label not in ("tp", "fp", "debatable", ""):
            label = ""

        # Parse indicators back from semicolon-separated string
        raw_indicators = row.get("indicators", "")
        indicators = [i.strip() for i in raw_indicators.split(";") if i.strip()]

        try:
            confidence = int(row.get("confidence_score", 0))
        except (ValueError, TypeError):
            confidence = 0

        try:
            line = int(row.get("line", 1))
        except (ValueError, TypeError):
            line = 1

        projects[proj_name]["findings"].append({
            "file": row.get("file", ""),
            "line": line,
            "tier": row.get("tier", ""),
            "category": row.get("category", ""),
            "indicators": indicators,
            "confidence_score": confidence,
            "context": row.get("context", ""),
            "label": label if label else None,
        })

    # If single project, return it directly
    project_list = list(projects.values())
    if len(project_list) == 1:
        return project_list[0]

    # Multiple projects: wrap in suite structure
    return {
        "suite_date": "",
        "projects_scanned": len(project_list),
        "total_files": 0,
        "total_ai_files": 0,
        "total_findings": sum(len(p["findings"]) for p in project_list),
        "findings_by_tier": {},
        "findings_by_category": {},
        "projects": project_list,
        "precision": None,
        "recall": None,
        "labelled_count": 0,
    }


def _collect_all_findings(results: dict) -> list:
    """Extract all findings from either a project result or a suite result."""
    if "projects" in results and isinstance(results["projects"], list):
        # Suite result
        all_findings = []
        for proj in results["projects"]:
            for f in proj.get("findings", []):
                all_findings.append(f)
        return all_findings
    elif "findings" in results:
        # Single project result
        return results["findings"]
    return []


def calculate_metrics(results: dict) -> dict:
    """Calculate precision, recall, and F1 from labelled results.

    Labels:
      - "tp": true positive — the finding correctly identifies a real risk
      - "fp": false positive — the finding is spurious / not a real risk
      - "debatable": ambiguous — could reasonably be argued either way

    Precision = tp / (tp + fp)
    Precision (with debatable) = (tp + debatable) / (tp + fp + debatable)
    """
    all_findings = _collect_all_findings(results)
    total = len(all_findings)

    labelled = [f for f in all_findings if f.get("label") in ("tp", "fp", "debatable")]
    unlabelled = total - len(labelled)

    tp = sum(1 for f in labelled if f["label"] == "tp")
    fp = sum(1 for f in labelled if f["label"] == "fp")
    debatable = sum(1 for f in labelled if f["label"] == "debatable")

    # Precision calculations (avoid division by zero)
    precision = tp / (tp + fp) if (tp + fp) > 0 else None
    precision_with_debatable = (
        (tp + debatable) / (tp + fp + debatable)
        if (tp + fp + debatable) > 0
        else None
    )

    # F1 requires recall. Recall = tp / (tp + fn).
    # We cannot compute fn (false negatives: real risks the scanner missed)
    # from labelled findings alone — it requires a ground-truth corpus.
    # We report recall as null unless the results include a known_positives count.
    known_positives = results.get("known_positives")
    if known_positives and known_positives > 0:
        recall = tp / known_positives
        f1 = (2 * precision * recall / (precision + recall)) if precision and recall else None
    else:
        recall = None
        f1 = None

    # Per-tier breakdown
    by_tier = {}
    tier_names = ["prohibited", "high_risk", "limited_risk", "minimal_risk", "credential_exposure"]
    for tier in tier_names:
        tier_findings = [f for f in labelled if f.get("tier") == tier]
        tier_tp = sum(1 for f in tier_findings if f["label"] == "tp")
        tier_fp = sum(1 for f in tier_findings if f["label"] == "fp")
        tier_debatable = sum(1 for f in tier_findings if f["label"] == "debatable")
        tier_total = tier_tp + tier_fp + tier_debatable

        by_tier[tier] = {
            "tp": tier_tp,
            "fp": tier_fp,
            "debatable": tier_debatable,
            "total": tier_total,
            "precision": tier_tp / (tier_tp + tier_fp) if (tier_tp + tier_fp) > 0 else None,
        }

    return {
        "total_findings": total,
        "labelled": len(labelled),
        "unlabelled": unlabelled,
        "true_positives": tp,
        "false_positives": fp,
        "debatable": debatable,
        "precision": _round_or_none(precision),
        "precision_with_debatable": _round_or_none(precision_with_debatable),
        "recall": _round_or_none(recall),
        "f1": _round_or_none(f1),
        "by_tier": by_tier,
    }


def _round_or_none(value: Optional[float], digits: int = 3) -> Optional[float]:
    """Round a float or return None."""
    if value is None:
        return None
    return round(value, digits)


# ---------------------------------------------------------------------------
# Output formatters
# ---------------------------------------------------------------------------

def format_benchmark_text(results: dict) -> str:
    """Format benchmark results as a human-readable text summary."""
    lines = []

    # Determine if this is a suite or single project
    is_suite = "projects" in results and "suite_date" in results
    projects = results.get("projects", [results]) if is_suite else [results]

    lines.append("=" * 70)
    if is_suite:
        lines.append(f"  Regula Benchmark Suite")
        lines.append(f"  Date: {results.get('suite_date', 'N/A')}")
        lines.append(f"  Projects: {results.get('projects_scanned', len(projects))}")
    else:
        lines.append(f"  Regula Benchmark: {results.get('project', 'Unknown')}")
        lines.append(f"  Date: {results.get('scan_date', 'N/A')}")
        lines.append(f"  Path: {results.get('path', 'N/A')}")
    lines.append("=" * 70)
    lines.append("")

    # Aggregate stats
    if is_suite:
        lines.append(f"  Total files scanned:    {results.get('total_files', 0):,}")
        lines.append(f"  Total AI files:         {results.get('total_ai_files', 0):,}")
        lines.append(f"  Total findings:         {results.get('total_findings', 0):,}")
        lines.append("")
        by_tier = results.get("findings_by_tier", {})
        lines.append("  Findings by tier:")
        for tier in ["prohibited", "high_risk", "limited_risk", "minimal_risk", "credential_exposure"]:
            count = by_tier.get(tier, 0)
            display = tier.upper().replace("_", "-")
            lines.append(f"    {display:<25} {count:>6}")
        lines.append("")

    # Per-project summaries
    for proj in projects:
        lines.append(f"  --- {proj.get('project', 'Unknown')} ---")
        lines.append(f"  Files scanned:    {proj.get('files_scanned', 0):,}")
        lines.append(f"  AI files found:   {proj.get('ai_files_found', 0):,}")
        stats = proj.get("stats", {})
        findings = proj.get("findings", [])
        lines.append(f"  Findings:         {len(findings)}")
        for tier in ["prohibited", "high_risk", "limited_risk", "minimal_risk", "credential_exposure"]:
            count = stats.get(tier, 0)
            if count > 0:
                display = tier.upper().replace("_", "-")
                lines.append(f"    {display}: {count}")
        lines.append("")

        # Show high-priority findings (prohibited + high_risk + credential)
        priority = [f for f in findings if f["tier"] in ("prohibited", "high_risk", "credential_exposure")]
        if priority:
            lines.append("  Priority findings:")
            for f in sorted(priority, key=lambda x: -x.get("confidence_score", 0))[:20]:
                tier_display = f["tier"].upper().replace("_", "-")
                indicators_str = ", ".join(f.get("indicators", []))
                lines.append(
                    f"    [{tier_display}] {f['file']}:{f['line']} "
                    f"(confidence: {f.get('confidence_score', 0)}) "
                    f"— {f.get('category', '')} [{indicators_str}]"
                )
            if len(priority) > 20:
                lines.append(f"    ... and {len(priority) - 20} more")
            lines.append("")

    # Metrics summary (if labelled)
    all_findings = _collect_all_findings(results)
    labelled_count = sum(1 for f in all_findings if f.get("label") in ("tp", "fp", "debatable"))
    if labelled_count > 0:
        metrics = calculate_metrics(results)
        lines.append("  --- Metrics ---")
        lines.append(f"  Labelled:                  {metrics['labelled']} / {metrics['total_findings']}")
        lines.append(f"  True positives:            {metrics['true_positives']}")
        lines.append(f"  False positives:           {metrics['false_positives']}")
        lines.append(f"  Debatable:                 {metrics['debatable']}")
        p = metrics.get("precision")
        lines.append(f"  Precision:                 {_fmt_pct(p)}")
        pwd = metrics.get("precision_with_debatable")
        lines.append(f"  Precision (w/ debatable):  {_fmt_pct(pwd)}")
        r = metrics.get("recall")
        lines.append(f"  Recall:                    {_fmt_pct(r)}")
        f1 = metrics.get("f1")
        lines.append(f"  F1:                        {_fmt_pct(f1)}")
        lines.append("")

        # Per-tier breakdown
        lines.append("  Per-tier precision:")
        for tier, data in metrics.get("by_tier", {}).items():
            if data["total"] > 0:
                display = tier.upper().replace("_", "-")
                p_tier = data.get("precision")
                lines.append(
                    f"    {display:<25} "
                    f"tp={data['tp']} fp={data['fp']} dbt={data['debatable']} "
                    f"precision={_fmt_pct(p_tier)}"
                )
        lines.append("")

    lines.append("=" * 70)
    return "\n".join(lines)


def _fmt_pct(value: Optional[float]) -> str:
    """Format a 0-1 float as a percentage string, or 'N/A'."""
    if value is None:
        return "N/A"
    return f"{value:.1%}"


def format_benchmark_json(results: dict) -> str:
    """Format benchmark results as indented JSON."""
    return json.dumps(results, indent=2, default=str)


def format_labelling_csv(results: dict) -> str:
    """Export findings as CSV for manual labelling.

    Columns: project, file, line, tier, category, indicators,
             context, confidence_score, label

    The `label` column is left empty for the reviewer to fill with:
    tp, fp, or debatable.
    """
    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow([
        "project", "file", "line", "tier", "category",
        "indicators", "context", "confidence_score", "label",
    ])

    # Collect findings from suite or single project
    is_suite = "projects" in results and isinstance(results.get("projects"), list)
    if is_suite:
        for proj in results["projects"]:
            proj_name = proj.get("project", "unknown")
            for f in proj.get("findings", []):
                _write_csv_row(writer, proj_name, f)
    else:
        proj_name = results.get("project", "unknown")
        for f in results.get("findings", []):
            _write_csv_row(writer, proj_name, f)

    return output.getvalue()


def _write_csv_row(writer: csv.writer, project: str, finding: dict) -> None:
    """Write a single finding as a CSV row."""
    # Join indicators with semicolons (commas would conflict with CSV)
    indicators = ";".join(finding.get("indicators", []))

    # Collapse context to single line for CSV (use | as line separator)
    context = finding.get("context", "")
    context_oneline = context.replace("\n", " | ") if context else ""

    # If there's already a label, preserve it
    label = finding.get("label") or ""

    writer.writerow([
        project,
        finding.get("file", ""),
        finding.get("line", 1),
        finding.get("tier", ""),
        finding.get("category", ""),
        indicators,
        context_oneline,
        finding.get("confidence_score", 0),
        label,
    ])


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Regula Benchmark — Measure precision and recall against real codebases",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scan a single project
  python3 scripts/benchmark.py --project /path/to/langchain

  # Scan multiple projects from a manifest file
  python3 scripts/benchmark.py --manifest projects.json

  # Output CSV for manual labelling
  python3 scripts/benchmark.py --project /path/to/project --format csv -o findings.csv

  # Calculate metrics from labelled CSV
  python3 scripts/benchmark.py --metrics labelled_findings.csv

  # Save full results as JSON
  python3 scripts/benchmark.py --project /path/to/project --format json -o results.json
""",
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--project", "-p",
        help="Path to a project directory to scan",
    )
    group.add_argument(
        "--manifest", "-m",
        help="Path to a JSON manifest listing projects to scan. "
             'Format: [{"name": "...", "path": "..."}, ...]',
    )
    group.add_argument(
        "--metrics",
        help="Path to a labelled CSV or JSON file — calculate precision/recall metrics",
    )

    parser.add_argument(
        "--format", "-f",
        choices=["text", "json", "csv"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--output", "-o",
        help="Write output to file instead of stdout",
    )

    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    # --- Metrics mode ---
    if args.metrics:
        print(f"Loading labelled results from {args.metrics}...", file=sys.stderr)
        results = load_labelled_results(args.metrics)
        metrics = calculate_metrics(results)

        if args.format == "json":
            output = json.dumps(metrics, indent=2, default=str)
        else:
            # Text summary of metrics
            lines = []
            lines.append("=" * 70)
            lines.append("  Regula Benchmark Metrics")
            lines.append("=" * 70)
            lines.append(f"  Total findings:            {metrics['total_findings']}")
            lines.append(f"  Labelled:                  {metrics['labelled']}")
            lines.append(f"  Unlabelled:                {metrics['unlabelled']}")
            lines.append(f"  True positives:            {metrics['true_positives']}")
            lines.append(f"  False positives:           {metrics['false_positives']}")
            lines.append(f"  Debatable:                 {metrics['debatable']}")
            lines.append("")
            lines.append(f"  Precision:                 {_fmt_pct(metrics.get('precision'))}")
            lines.append(f"  Precision (w/ debatable):  {_fmt_pct(metrics.get('precision_with_debatable'))}")
            lines.append(f"  Recall:                    {_fmt_pct(metrics.get('recall'))}")
            lines.append(f"  F1:                        {_fmt_pct(metrics.get('f1'))}")
            lines.append("")
            lines.append("  Per-tier breakdown:")
            for tier, data in metrics.get("by_tier", {}).items():
                if data["total"] > 0:
                    display = tier.upper().replace("_", "-")
                    p = data.get("precision")
                    lines.append(
                        f"    {display:<25} "
                        f"tp={data['tp']} fp={data['fp']} dbt={data['debatable']} "
                        f"precision={_fmt_pct(p)}"
                    )
            lines.append("=" * 70)
            output = "\n".join(lines)

        _emit(output, args.output)
        return

    # --- Scan mode ---
    if args.project:
        print(f"Scanning project: {args.project}", file=sys.stderr)
        results = benchmark_project(args.project)
        print(
            f"Done: {results['files_scanned']} files scanned, "
            f"{len(results['findings'])} findings",
            file=sys.stderr,
        )
    elif args.manifest:
        manifest_path = Path(args.manifest)
        if not manifest_path.exists():
            print(f"Manifest file not found: {args.manifest}", file=sys.stderr)
            sys.exit(1)

        projects = json.loads(manifest_path.read_text(encoding="utf-8"))
        if not isinstance(projects, list):
            print("Manifest must be a JSON array of {name, path} objects", file=sys.stderr)
            sys.exit(1)

        print(f"Running benchmark suite ({len(projects)} projects)...", file=sys.stderr)
        results = benchmark_suite(projects)
        print(
            f"Done: {results['projects_scanned']} projects, "
            f"{results['total_findings']} total findings",
            file=sys.stderr,
        )
    else:
        parser.print_help()
        sys.exit(1)

    # --- Format output ---
    if args.format == "json":
        output = format_benchmark_json(results)
    elif args.format == "csv":
        output = format_labelling_csv(results)
    else:
        output = format_benchmark_text(results)

    _emit(output, args.output)


def _emit(content: str, output_path: Optional[str]) -> None:
    """Write content to file or stdout."""
    if output_path:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(content, encoding="utf-8")
        print(f"Output written to {out}", file=sys.stderr)
    else:
        print(content)


if __name__ == "__main__":
    main()
