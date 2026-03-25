#!/usr/bin/env python3
"""
Regula Baseline Comparison — Incremental CI/CD Compliance

Saves scan results as a baseline and compares subsequent scans against it.
Only reports net-new findings, reducing noise from existing technical debt.

Evidence base: HN thread on engineering team compliance pain points —
teams need incremental compliance progress, not full-repo noise that
overwhelms and gets ignored. Matches Snyk/SonarQube "new code" approach.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from report import scan_files

BASELINE_FILE = ".regula-baseline.json"


def save_baseline(project_path: str, output_path: str = None) -> dict:
    """Scan project and save results as baseline."""
    findings = scan_files(project_path)

    baseline = {
        "version": "1.0",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "project_path": str(Path(project_path).resolve()),
        "findings_count": len(findings),
        "findings": findings,
    }

    out = Path(output_path or (Path(project_path) / BASELINE_FILE))
    out.write_text(json.dumps(baseline, indent=2), encoding="utf-8")
    return baseline


def load_baseline(project_path: str, baseline_path: str = None) -> dict:
    """Load an existing baseline."""
    path = Path(baseline_path or (Path(project_path) / BASELINE_FILE))
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _finding_key(f: dict) -> str:
    """Generate a stable key for a finding to track across scans."""
    return f"{f.get('file', '')}:{f.get('tier', '')}:{':'.join(sorted(f.get('indicators', [])))}"


def compare_to_baseline(project_path: str, baseline_path: str = None) -> dict:
    """Scan project and compare to baseline. Return only net-new findings."""
    baseline = load_baseline(project_path, baseline_path)
    if not baseline:
        return {
            "error": f"No baseline found. Run 'regula baseline save' first.",
            "new_findings": [],
            "resolved_findings": [],
            "unchanged_findings": [],
        }

    current_findings = scan_files(project_path)

    # Build key sets
    baseline_keys = {_finding_key(f) for f in baseline.get("findings", [])}
    current_keys = {_finding_key(f) for f in current_findings}

    new_keys = current_keys - baseline_keys
    resolved_keys = baseline_keys - current_keys
    unchanged_keys = current_keys & baseline_keys

    new_findings = [f for f in current_findings if _finding_key(f) in new_keys]
    resolved_findings = [f for f in baseline.get("findings", []) if _finding_key(f) in resolved_keys]
    unchanged_findings = [f for f in current_findings if _finding_key(f) in unchanged_keys]

    return {
        "baseline_date": baseline.get("created_at", "unknown"),
        "scan_date": datetime.now(timezone.utc).isoformat(),
        "new_findings": new_findings,
        "resolved_findings": resolved_findings,
        "unchanged_findings": unchanged_findings,
        "summary": {
            "new": len(new_findings),
            "resolved": len(resolved_findings),
            "unchanged": len(unchanged_findings),
            "net_change": len(new_findings) - len(resolved_findings),
        },
    }


def format_comparison_text(result: dict) -> str:
    """Format comparison result for CLI."""
    if result.get("error"):
        return f"\n  Error: {result['error']}\n"

    s = result["summary"]
    lines = [
        "",
        "=" * 60,
        "  Regula — Baseline Comparison",
        "=" * 60,
        f"  Baseline: {result['baseline_date'][:10]}",
        f"  Current:  {result['scan_date'][:10]}",
        "",
        f"  New findings:      {s['new']}",
        f"  Resolved:          {s['resolved']}",
        f"  Unchanged:         {s['unchanged']}",
        f"  Net change:        {'+' if s['net_change'] >= 0 else ''}{s['net_change']}",
    ]

    if result["new_findings"]:
        lines.append("")
        lines.append("  NEW FINDINGS (require attention):")
        for f in result["new_findings"]:
            tier = f["tier"].upper().replace("_", "-")
            lines.append(f"    [{tier}] {f['file']} — {f.get('description', '')}")

    if result["resolved_findings"]:
        lines.append("")
        lines.append("  RESOLVED (no longer present):")
        for f in result["resolved_findings"]:
            tier = f["tier"].upper().replace("_", "-")
            lines.append(f"    [{tier}] {f['file']} — {f.get('description', '')}")

    lines.append("=" * 60)
    lines.append("")
    return "\n".join(lines)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Baseline comparison for incremental compliance")
    sub = parser.add_subparsers(dest="command")

    save_p = sub.add_parser("save", help="Save current scan as baseline")
    save_p.add_argument("--project", "-p", default=".")
    save_p.add_argument("--output", "-o", help="Baseline file path")

    compare_p = sub.add_parser("compare", help="Compare current scan to baseline")
    compare_p.add_argument("--project", "-p", default=".")
    compare_p.add_argument("--baseline", "-b", help="Baseline file path")
    compare_p.add_argument("--format", "-f", choices=["text", "json"], default="text")
    compare_p.add_argument("--fail-on-new", action="store_true", help="Exit 1 if new findings (for CI/CD)")

    args = parser.parse_args()

    if args.command == "save":
        baseline = save_baseline(args.project, args.output)
        print(f"Baseline saved: {baseline['findings_count']} findings")

    elif args.command == "compare":
        result = compare_to_baseline(args.project, args.baseline)
        if args.format == "json":
            print(json.dumps(result, indent=2))
        else:
            print(format_comparison_text(result))

        if args.fail_on_new and result.get("summary", {}).get("new", 0) > 0:
            sys.exit(1)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
