#!/usr/bin/env python3
"""
Regula CLI — AI Governance Risk Indication

Unified command-line interface for all Regula functionality.

Usage:
    regula check [path]              Scan files for risk indicators
    regula classify [--input text]   Classify a text input
    regula report [--format html]    Generate reports (HTML, SARIF, JSON)
    regula audit [verify|export]     Manage audit trail
    regula discover [--project .]    Discover AI systems
    regula install [platform]        Install hooks for a platform
    regula status                    Show registry status
"""

import argparse
import json
import sys
from pathlib import Path

# Ensure scripts directory is importable
sys.path.insert(0, str(Path(__file__).parent))


def cmd_check(args):
    """Scan files for risk indicators."""
    from report import scan_files

    project = str(Path(args.path).resolve())
    findings = scan_files(project, respect_ignores=not args.no_ignore)

    active = [f for f in findings if not f.get("suppressed")]
    suppressed = [f for f in findings if f.get("suppressed")]

    prohibited = [f for f in active if f["tier"] == "prohibited"]
    credentials = [f for f in active if f["tier"] == "credential_exposure"]
    high_risk = [f for f in active if f["tier"] == "high_risk"]
    limited = [f for f in active if f["tier"] == "limited_risk"]

    if args.format == "json":
        print(json.dumps(findings, indent=2))
    elif args.format == "sarif":
        from report import generate_sarif
        name = args.name or Path(project).name
        print(json.dumps(generate_sarif(findings, name), indent=2))
    else:
        # Human-readable output
        print(f"\nRegula Scan: {project}")
        print(f"{'=' * 60}")
        total_files = len(set(f["file"] for f in findings))
        print(f"  Files scanned:      {total_files}")
        print(f"  Prohibited:         {len(prohibited)}")
        print(f"  Credentials:        {len(credentials)}")
        print(f"  High-risk:          {len(high_risk)}")
        print(f"  Limited-risk:       {len(limited)}")
        print(f"  Suppressed:         {len(suppressed)}")

        if prohibited:
            print(f"\n  PROHIBITED INDICATORS:")
            for f in prohibited:
                score = f.get("confidence_score", 0)
                print(f"    [{score:3d}] {f['file']} — {f.get('description', '')}")

        if credentials:
            print(f"\n  CREDENTIAL EXPOSURE (Article 15):")
            for f in credentials:
                score = f.get("confidence_score", 0)
                print(f"    [{score:3d}] {f['file']}:{f.get('line', '?')} — {f.get('description', '')}")

        if high_risk:
            print(f"\n  HIGH-RISK INDICATORS:")
            for f in high_risk:
                score = f.get("confidence_score", 0)
                print(f"    [{score:3d}] {f['file']} — {f.get('description', '')}")

        if limited:
            print(f"\n  LIMITED-RISK:")
            for f in limited:
                score = f.get("confidence_score", 0)
                print(f"    [{score:3d}] {f['file']} — {f.get('description', '')}")

        print(f"{'=' * 60}")
        print(f"  Confidence scores: 0-100 (higher = more indicators matched)")
        print(f"  Suppress findings: add '# regula-ignore' to file")
        print()

    # Exit code: 2 if prohibited found, 1 if high-risk, 0 otherwise
    if prohibited:
        sys.exit(2)
    elif high_risk and args.strict:
        sys.exit(1)
    sys.exit(0)


def cmd_classify(args):
    """Classify a text input."""
    from classify_risk import classify

    if args.file:
        text = Path(args.file).read_text(encoding="utf-8", errors="ignore")
    elif args.input:
        text = args.input
    elif not sys.stdin.isatty():
        text = sys.stdin.read()
    else:
        print("Error: provide --input, --file, or pipe text to stdin", file=sys.stderr)
        sys.exit(1)

    result = classify(text)

    if args.format == "json":
        print(result.to_json())
    else:
        print(result.message)
        if result.exceptions:
            print(f"  Exceptions: {result.exceptions}")

    sys.exit(2 if result.tier.value == "prohibited" else 0)


def cmd_report(args):
    """Generate reports."""
    # Delegate to report.py main
    sys.argv = ["report.py"]
    if args.project:
        sys.argv += ["--project", args.project]
    if args.format:
        sys.argv += ["--format", args.format]
    if args.output:
        sys.argv += ["--output", args.output]
    if args.name:
        sys.argv += ["--name", args.name]
    if args.include_audit:
        sys.argv += ["--include-audit"]

    from report import main as report_main
    report_main()


def cmd_audit(args):
    """Manage audit trail."""
    sys.argv = ["log_event.py", args.subcommand or "verify"]
    if args.subcommand == "export":
        if args.audit_format:
            sys.argv += ["--format", args.audit_format]
        if args.output:
            sys.argv += ["--output", args.output]
    elif args.subcommand == "query":
        if args.event_type:
            sys.argv += ["--event-type", args.event_type]
        if args.limit:
            sys.argv += ["--limit", str(args.limit)]

    from log_event import main as audit_main
    audit_main()


def cmd_discover(args):
    """Discover AI systems."""
    sys.argv = ["discover_ai_systems.py"]
    if args.project:
        sys.argv += ["--project", args.project]
    if args.register:
        sys.argv += ["--register"]

    from discover_ai_systems import main as discover_main
    discover_main()


def cmd_install(args):
    """Install hooks for a platform."""
    sys.argv = ["install.py"]
    if args.platform:
        sys.argv += [args.platform]
    if args.project:
        sys.argv += ["--project", args.project]

    from install import main as install_main
    install_main()


def cmd_status(args):
    """Show registry status."""
    from discover_ai_systems import print_registry_status
    print_registry_status()


def cmd_init(args):
    """Guided setup wizard."""
    from init_wizard import run_init
    run_init(Path(args.project).resolve(), interactive=args.interactive)


def cmd_feed(args):
    """Fetch AI governance news feed."""
    from feed import fetch_governance_news, format_text, format_html, FEED_SOURCES
    if args.sources:
        print("\nRegula Governance Feed — Curated Sources\n")
        for s in FEED_SOURCES:
            print(f"  {s['name']}")
            print(f"    Authority: {s['authority']}")
            print()
        return
    articles = fetch_governance_news(days=args.days, use_cache=not args.no_cache)
    if args.format == "json":
        content = json.dumps(articles, indent=2)
    elif args.format == "html":
        content = format_html(articles)
    else:
        content = format_text(articles)
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(content, encoding="utf-8")
        print(f"Feed written to {args.output} ({len(articles)} articles)", file=sys.stderr)
    else:
        print(content)


def cmd_questionnaire(args):
    """Context-driven risk assessment questionnaire."""
    from questionnaire import generate_questionnaire, evaluate_questionnaire, format_questionnaire_cli
    if args.evaluate:
        try:
            if Path(args.evaluate).exists():
                answers = json.loads(Path(args.evaluate).read_text())
            else:
                answers = json.loads(args.evaluate)
        except (json.JSONDecodeError, OSError) as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        result = evaluate_questionnaire(answers)
        print(result.to_json() if args.format == "json" else result.message)
    else:
        q = generate_questionnaire()
        if args.format == "json":
            print(json.dumps(q, indent=2))
        else:
            print(format_questionnaire_cli(q))


def cmd_session(args):
    """Session-level risk aggregation."""
    from session import aggregate_session, format_session_text
    import os
    profile = aggregate_session(
        session_id=args.session or os.environ.get("CLAUDE_SESSION_ID"),
        hours=args.hours,
    )
    if args.format == "json":
        print(json.dumps(profile, indent=2))
    else:
        print(format_session_text(profile))


def cmd_baseline(args):
    """CI/CD baseline comparison."""
    from baseline import save_baseline, compare_to_baseline, format_comparison_text
    if args.subcommand == "save":
        bl = save_baseline(args.project, getattr(args, "output", None))
        print(f"Baseline saved: {bl['findings_count']} findings")
    elif args.subcommand == "compare":
        result = compare_to_baseline(args.project, getattr(args, "baseline_file", None))
        if args.format == "json":
            print(json.dumps(result, indent=2))
        else:
            print(format_comparison_text(result))
        if args.fail_on_new and result.get("summary", {}).get("new", 0) > 0:
            sys.exit(1)
    else:
        print("Usage: regula baseline [save|compare]")


def cmd_timeline(args):
    """EU AI Act enforcement timeline."""
    from timeline import format_timeline_text, TIMELINE
    if args.format == "json":
        from datetime import date
        print(json.dumps({"as_of": date.today().isoformat(), "timeline": TIMELINE}, indent=2))
    else:
        print(format_timeline_text())


def main():
    parser = argparse.ArgumentParser(
        prog="regula",
        description="AI Governance Risk Indication for Code",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  regula check .                          Scan current directory
  regula check --format sarif .           Output SARIF for CI/CD
  regula classify --input "import torch"  Classify a text input
  regula report --format html -o report.html  Generate HTML report
  regula feed                             AI governance news feed
  regula feed --format html -o feed.html  Feed as HTML digest
  regula questionnaire                    Context-driven risk assessment
  regula session                          Session risk aggregation
  regula baseline save                    Save compliance baseline
  regula baseline compare --fail-on-new   CI/CD incremental compliance
  regula timeline                         EU AI Act enforcement dates
  regula install claude-code              Install Claude Code hooks
  regula install copilot-cli              Install Copilot CLI hooks
  regula audit verify                     Verify audit chain integrity
""",
    )
    subparsers = parser.add_subparsers(dest="command")

    # --- init ---
    p_init = subparsers.add_parser("init", help="Guided setup wizard")
    p_init.add_argument("--project", "-p", default=".", help="Project directory")
    p_init.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
    p_init.set_defaults(func=cmd_init)

    # --- check ---
    p_check = subparsers.add_parser("check", help="Scan files for risk indicators")
    p_check.add_argument("path", nargs="?", default=".", help="Path to scan")
    p_check.add_argument("--format", "-f", choices=["text", "json", "sarif"], default="text")
    p_check.add_argument("--name", "-n", help="Project name for SARIF output")
    p_check.add_argument("--no-ignore", action="store_true", help="Don't respect regula-ignore comments")
    p_check.add_argument("--strict", action="store_true", help="Exit 1 on high-risk findings")
    p_check.set_defaults(func=cmd_check)

    # --- classify ---
    p_classify = subparsers.add_parser("classify", help="Classify a text input")
    p_classify.add_argument("--input", "-i", help="Text to classify")
    p_classify.add_argument("--file", "-f", help="File to classify")
    p_classify.add_argument("--format", choices=["text", "json"], default="text")
    p_classify.set_defaults(func=cmd_classify)

    # --- report ---
    p_report = subparsers.add_parser("report", help="Generate reports (HTML, SARIF, JSON)")
    p_report.add_argument("--project", "-p", default=".")
    p_report.add_argument("--format", "-f", choices=["html", "sarif", "json"], default="html")
    p_report.add_argument("--output", "-o", help="Output file")
    p_report.add_argument("--name", "-n", help="Project name")
    p_report.add_argument("--include-audit", action="store_true", help="Include audit trail data")
    p_report.set_defaults(func=cmd_report)

    # --- audit ---
    p_audit = subparsers.add_parser("audit", help="Manage audit trail")
    p_audit.add_argument("subcommand", nargs="?", choices=["verify", "export", "query"], default="verify")
    p_audit.add_argument("--format", dest="audit_format", choices=["json", "csv"])
    p_audit.add_argument("--output", "-o")
    p_audit.add_argument("--event-type", "-t")
    p_audit.add_argument("--limit", type=int)
    p_audit.set_defaults(func=cmd_audit)

    # --- discover ---
    p_discover = subparsers.add_parser("discover", help="Discover AI systems in a project")
    p_discover.add_argument("--project", "-p", default=".")
    p_discover.add_argument("--register", "-r", action="store_true")
    p_discover.set_defaults(func=cmd_discover)

    # --- install ---
    p_install = subparsers.add_parser("install", help="Install hooks for a platform")
    p_install.add_argument("platform", nargs="?", help="Platform (claude-code, copilot-cli, windsurf, pre-commit, git-hooks)")
    p_install.add_argument("--project", "-p", default=".")
    p_install.set_defaults(func=cmd_install)

    # --- status ---
    p_status = subparsers.add_parser("status", help="Show system registry status")
    p_status.set_defaults(func=cmd_status)

    # --- feed ---
    p_feed = subparsers.add_parser("feed", help="AI governance news from curated sources")
    p_feed.add_argument("--days", "-d", type=int, default=7, help="Articles from last N days")
    p_feed.add_argument("--format", "-f", choices=["text", "json", "html"], default="text")
    p_feed.add_argument("--output", "-o", help="Output file")
    p_feed.add_argument("--no-cache", action="store_true", help="Bypass cache")
    p_feed.add_argument("--sources", action="store_true", help="List sources")
    p_feed.set_defaults(func=cmd_feed)

    # --- questionnaire ---
    p_quest = subparsers.add_parser("questionnaire", help="Context-driven risk assessment")
    p_quest.add_argument("--evaluate", "-e", help="Evaluate answers (JSON)")
    p_quest.add_argument("--format", "-f", choices=["text", "json"], default="text")
    p_quest.set_defaults(func=cmd_questionnaire)

    # --- session ---
    p_session = subparsers.add_parser("session", help="Session-level risk aggregation")
    p_session.add_argument("--session", "-s", help="Session ID")
    p_session.add_argument("--hours", type=int, default=8, help="Look back N hours")
    p_session.add_argument("--format", "-f", choices=["text", "json"], default="text")
    p_session.set_defaults(func=cmd_session)

    # --- baseline ---
    p_baseline = subparsers.add_parser("baseline", help="CI/CD baseline comparison")
    p_baseline.add_argument("subcommand", nargs="?", choices=["save", "compare"], default="compare")
    p_baseline.add_argument("--project", "-p", default=".")
    p_baseline.add_argument("--output", "-o")
    p_baseline.add_argument("--baseline-file", "-b")
    p_baseline.add_argument("--format", "-f", choices=["text", "json"], default="text")
    p_baseline.add_argument("--fail-on-new", action="store_true", help="Exit 1 on new findings (CI/CD)")
    p_baseline.set_defaults(func=cmd_baseline)

    # --- timeline ---
    p_timeline = subparsers.add_parser("timeline", help="EU AI Act enforcement timeline")
    p_timeline.add_argument("--format", "-f", choices=["text", "json"], default="text")
    p_timeline.set_defaults(func=cmd_timeline)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    args.func(args)


if __name__ == "__main__":
    main()
