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

from errors import RegulaError, PathError


def _validate_path(path_str: str) -> Path:
    """Validate a path exists. Raises PathError if not."""
    p = Path(path_str)
    if not p.exists():
        raise PathError(f"Path does not exist: {path_str}")
    return p


def _get_changed_files(project_path: str, git_ref: str = "HEAD~1") -> list[str]:
    """Get list of files changed since git_ref.

    Uses git diff to find changed/added files. Falls back to scanning all files
    if git is not available or the path is not a git repo.
    """
    import subprocess
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "--diff-filter=ACMR", git_ref],
            capture_output=True, text=True, timeout=10,
            cwd=project_path,
        )
        if result.returncode == 0:
            files = [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]
            return files
    except (subprocess.SubprocessError, FileNotFoundError):
        print("Note: git not available, scanning all files", file=sys.stderr)
    return []  # Empty = scan all files (fallback)


def _get_finding_tier_from_dict(finding: dict) -> str:
    """Compute finding tier from a scan result dict using policy thresholds."""
    from classify_risk import get_policy, RiskTier
    policy = get_policy()
    thresholds = policy.get("thresholds", {})
    block_above = int(thresholds.get("block_above", 80))
    warn_above = int(thresholds.get("warn_above", 50))

    # Prohibited always blocks regardless of confidence
    if finding.get("tier") == "prohibited":
        return "block"

    score = finding.get("confidence_score", 0)
    if score >= block_above:
        return "block"
    elif score >= warn_above:
        return "warn"
    else:
        return "info"


def _print_remediation(finding):
    """Print inline remediation for a finding (BLOCK/WARN only)."""
    from remediation import get_remediation
    tier_label = finding.get("_finding_tier", "info")
    if tier_label == "info":
        return
    rem = get_remediation(
        finding["tier"],
        finding.get("category", ""),
        finding.get("indicators", []),
        finding["file"],
        finding.get("description", ""),
    )
    if rem.get("fix_command"):
        print(f"      Fix: {rem['fix_command']}")
    if rem.get("summary"):
        print(f"      {rem['summary']}")


def cmd_check(args):
    """Scan files for risk indicators."""
    from report import scan_files

    _validate_path(args.path)
    project = str(Path(args.path).resolve())
    findings = scan_files(project, respect_ignores=not args.no_ignore)

    # Diff mode: filter findings to only changed files
    if args.diff:
        changed = _get_changed_files(project, args.diff)
        if changed:
            findings = [f for f in findings if f.get("file", "") in changed]
            print(f"  Diff mode: {len(changed)} files changed since {args.diff}", file=sys.stderr)
        else:
            print(f"  Diff mode: no changed files found since {args.diff} (showing all)", file=sys.stderr)

    active = [f for f in findings if not f.get("suppressed")]
    suppressed = [f for f in findings if f.get("suppressed")]

    prohibited = [f for f in active if f["tier"] == "prohibited"]
    credentials = [f for f in active if f["tier"] == "credential_exposure"]
    high_risk = [f for f in active if f["tier"] == "high_risk"]
    limited = [f for f in active if f["tier"] == "limited_risk"]

    # Assign finding tiers to all active findings
    for f in active:
        f["_finding_tier"] = _get_finding_tier_from_dict(f)

    block_findings = [f for f in active if f["_finding_tier"] == "block"]
    warn_findings = [f for f in active if f["_finding_tier"] == "warn"]
    info_findings = [f for f in active if f["_finding_tier"] == "info"]

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
        print(f"  BLOCK tier:         {len(block_findings)}")
        print(f"  WARN tier:          {len(warn_findings)}")
        print(f"  INFO tier:          {len(info_findings)}")

        if prohibited:
            print(f"\n  PROHIBITED INDICATORS:")
            for f in prohibited:
                score = f.get("confidence_score", 0)
                tier_label = f.get("_finding_tier", "block").upper()
                print(f"    [{tier_label}] [{score:3d}] {f['file']} — {f.get('description', '')}")
                _print_remediation(f)

        if credentials:
            print(f"\n  CREDENTIAL EXPOSURE (Article 15):")
            for f in credentials:
                score = f.get("confidence_score", 0)
                tier_label = f.get("_finding_tier", "warn").upper()
                print(f"    [{tier_label}] [{score:3d}] {f['file']}:{f.get('line', '?')} — {f.get('description', '')}")
                _print_remediation(f)

        if high_risk:
            print(f"\n  HIGH-RISK INDICATORS:")
            for f in high_risk:
                score = f.get("confidence_score", 0)
                tier_label = f.get("_finding_tier", "warn").upper()
                print(f"    [{tier_label}] [{score:3d}] {f['file']} — {f.get('description', '')}")
                _print_remediation(f)

        if limited:
            print(f"\n  LIMITED-RISK:")
            for f in limited:
                score = f.get("confidence_score", 0)
                tier_label = f.get("_finding_tier", "info").upper()
                if tier_label == "INFO" and not getattr(args, "verbose", False):
                    continue
                print(f"    [{tier_label}] [{score:3d}] {f['file']} — {f.get('description', '')}")

        if getattr(args, "verbose", False) and info_findings:
            info_non_limited = [f for f in info_findings if f["tier"] not in ("limited_risk",)]
            if info_non_limited:
                print(f"\n  INFO (verbose):")
                for f in info_non_limited:
                    score = f.get("confidence_score", 0)
                    print(f"    [INFO] [{score:3d}] {f['file']} — {f.get('description', '')}")

        print(f"{'=' * 60}")
        print(f"  Confidence scores: 0-100 (higher = more indicators matched)")
        print(f"  Tiers: BLOCK (>=80 or prohibited), WARN (50-79), INFO (<50)")
        print(f"  Suppress findings: add '# regula-ignore' to file")
        print()

    # Exit codes: 1 if any BLOCK-tier findings, 1 if WARN-tier and --strict, 0 otherwise
    if block_findings:
        sys.exit(1)
    elif warn_findings and args.strict:
        sys.exit(1)
    sys.exit(0)


def cmd_classify(args):
    """Classify a text input."""
    from classify_risk import classify

    if args.file:
        _validate_path(args.file)
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
    if hasattr(args, 'project') and args.project != ".":
        _validate_path(args.project)
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
    if args.project != ".":
        _validate_path(args.project)
    if args.csv:
        from discover_ai_systems import format_registry_csv
        print(format_registry_csv())
        return

    if args.eu_register:
        from discover_ai_systems import generate_eu_registration
        reg = generate_eu_registration(args.eu_register)
        print(json.dumps(reg, indent=2))
        return

    if args.org:
        from discover_ai_systems import scan_organization
        results = scan_organization(args.project)
        if args.format == "json":
            print(json.dumps(results, indent=2, default=str))
        else:
            print(f"\nOrganization Scan: {results['base_path']}")
            print(f"Projects scanned: {results['projects_scanned']}")
            print(f"AI projects found: {results['ai_projects_found']}")
            print(f"Risk distribution: {results['risk_distribution']}")
        return

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


def cmd_docs(args):
    """Generate documentation scaffolds."""
    sys.argv = ["generate_documentation.py"]
    if args.project:
        sys.argv += ["--project", args.project]
    if args.output:
        sys.argv += ["--output", args.output]
    if args.name:
        sys.argv += ["--name", args.name]
    if args.qms:
        sys.argv += ["--qms"]
    if getattr(args, "all", False):
        sys.argv += ["--all"]

    from generate_documentation import main as docs_main
    docs_main()


def cmd_compliance(args):
    """Manage compliance status of registered AI systems."""
    from discover_ai_systems import update_compliance_status, load_registry, COMPLIANCE_TRANSITIONS, COMPLIANCE_STATUSES

    if args.subcommand == "update":
        try:
            entry = update_compliance_status(args.system, args.status, args.note or "")
            print(f"Updated '{args.system}' to '{args.status}'")
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.subcommand == "history":
        registry = load_registry()
        system = registry.get("systems", {}).get(args.system)
        if not system:
            print(f"System '{args.system}' not found.", file=sys.stderr)
            sys.exit(1)
        history = system.get("compliance_history", [])
        if args.format == "json":
            print(json.dumps(history, indent=2))
        else:
            print(f"\n  Compliance History: {args.system}")
            print(f"  Current: {system.get('compliance_status', 'not_started')}")
            if not history:
                print("  No history recorded.")
            else:
                for h in history:
                    print(f"    {h['date'][:10]}: {h['from']} → {h['to']}{' — ' + h['note'] if h.get('note') else ''}")
            print()

    elif args.subcommand == "workflow":
        print("\n  Regula Compliance Status Workflow")
        print("  " + "=" * 50)
        print("  not_started → assessment → implementing → compliant → review_due")
        print()
        for status, transitions in COMPLIANCE_TRANSITIONS.items():
            print(f"    {status:<20} → {', '.join(transitions)}")
        print()

    else:
        registry = load_registry()
        systems = registry.get("systems", {})
        if not systems:
            print("No systems registered. Run 'regula discover --register' first.")
            return
        if args.format == "json":
            summary = {name: {"status": s.get("compliance_status", "not_started"), "risk": s.get("highest_risk", "unknown")} for name, s in systems.items()}
            print(json.dumps(summary, indent=2))
        else:
            print(f"\n  {'System':<30} {'Status':<20} {'Risk':<15}")
            print(f"  {'-'*30} {'-'*20} {'-'*15}")
            for name, s in systems.items():
                status = s.get("compliance_status", "not_started")
                risk = s.get("highest_risk", "unknown").upper().replace("_", "-")
                print(f"  {name:<30} {status:<20} {risk:<15}")
            print()


def cmd_gap(args):
    """Compliance gap assessment."""
    if args.project != ".":
        _validate_path(args.project)
    from compliance_check import assess_compliance, format_gap_text, format_gap_json
    articles = [args.article] if args.article else None
    assessment = assess_compliance(args.project, articles=articles)
    if args.format == "json":
        print(format_gap_json(assessment))
    else:
        print(format_gap_text(assessment))
    # Exit 1 if overall score < 50 and --strict
    if args.strict and assessment.get("overall_score", 0) < 50:
        sys.exit(1)


def cmd_benchmark(args):
    """Run real-world validation benchmark."""
    from benchmark import benchmark_project, benchmark_suite, calculate_metrics, load_labelled_results
    from benchmark import format_benchmark_text, format_benchmark_json, format_labelling_csv

    if args.metrics:
        results = load_labelled_results(args.metrics)
        metrics = calculate_metrics(results)
        print(json.dumps(metrics, indent=2))
        return

    if args.manifest:
        projects = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
        results = benchmark_suite(projects)
    else:
        results = benchmark_project(args.project)

    if args.format == "csv":
        content = format_labelling_csv(results)
    elif args.format == "json":
        content = format_benchmark_json(results)
    else:
        content = format_benchmark_text(results)

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(content, encoding="utf-8")
        print(f"Benchmark output written to {args.output}", file=sys.stderr)
    else:
        print(content)


def cmd_timeline(args):
    """EU AI Act enforcement timeline."""
    from timeline import format_timeline_text, TIMELINE
    if args.format == "json":
        from datetime import date
        print(json.dumps({"as_of": date.today().isoformat(), "timeline": TIMELINE}, indent=2))
    else:
        print(format_timeline_text())


def cmd_sbom(args):
    """Generate AI Software Bill of Materials (CycloneDX 1.6)."""
    if args.project != ".":
        _validate_path(args.project)
    from sbom import generate_sbom, format_sbom_json, format_sbom_summary
    bom = generate_sbom(args.project, project_name=args.name)
    if args.format == "json":
        content = format_sbom_json(bom)
    else:
        content = format_sbom_summary(bom)
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(content, encoding="utf-8")
        print(f"SBOM written to {args.output}", file=sys.stderr)
    else:
        print(content)


def cmd_agent(args):
    """Agentic AI governance monitoring."""
    from agent_monitor import analyse_agent_session, check_mcp_config, format_agent_text, format_agent_json

    if args.check_mcp:
        findings = check_mcp_config(getattr(args, "config_file", None))
        if args.format == "json":
            print(json.dumps(findings, indent=2))
        else:
            if findings:
                print(f"\nFound {len(findings)} credential(s) in MCP configuration:")
                for f in findings:
                    print(f"  {f['file']}: {f['description']}")
            else:
                print("No credentials found in MCP configuration files.")
        return

    analysis = analyse_agent_session(
        session_id=args.session,
        hours=args.hours,
    )
    if args.format == "json":
        print(format_agent_json(analysis))
    else:
        print(format_agent_text(analysis))


def cmd_deps(args):
    """Dependency supply chain analysis."""
    if args.project != ".":
        _validate_path(args.project)
    from dependency_scan import scan_dependencies, format_dep_text, format_dep_json
    results = scan_dependencies(args.project)
    if args.format == "json":
        print(format_dep_json(results))
    else:
        print(format_dep_text(results))
    if results.get("compromised_count", 0) > 0:
        sys.exit(1)
    elif args.strict and results.get("pinning_score", 100) < 50:
        sys.exit(1)


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
  regula compliance                       View compliance status of all systems
  regula compliance update -s MyApp --status assessment
  regula gap --project .                  Compliance gap assessment (Articles 9-15)
  regula gap --project . --article 14    Check Article 14 (human oversight) only
  regula compliance workflow              Show compliance status transitions
  regula docs --project . --qms          Generate Annex IV + QMS scaffolds
  regula benchmark --project .           Benchmark precision/recall
  regula benchmark --project . -f csv -o findings.csv  Export for labelling
  regula timeline                         EU AI Act enforcement dates
  regula deps --project .                 AI dependency supply chain analysis
  regula deps --project . --format json  Dependency scan as JSON
  regula install claude-code              Install Claude Code hooks
  regula install copilot-cli              Install Copilot CLI hooks
  regula audit verify                     Verify audit chain integrity
""",
    )
    parser.add_argument("--framework", choices=["eu-ai-act", "nist-ai-rmf", "iso-42001", "nist-csf", "soc2", "iso-27001", "owasp-llm-top10", "mitre-atlas", "all"], default="eu-ai-act",
                        help="Compliance framework to map findings to")
    parser.add_argument("--ci", action="store_true",
                        help="CI mode: exit 0=pass, 1=findings, 2=blocked")
    parser.add_argument("--config", help="Custom policy configuration file path")

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
    p_check.add_argument("--strict", action="store_true", help="Exit 1 on WARN-tier findings")
    p_check.add_argument("--verbose", "-v", action="store_true", help="Show INFO-tier findings")
    p_check.add_argument("--diff", metavar="REF", nargs="?", const="HEAD~1",
                         help="Only scan files changed since REF (default: HEAD~1)")
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
    p_discover.add_argument("--org", action="store_true", help="Scan all projects in directory (org-level inventory)")
    p_discover.add_argument("--csv", action="store_true", help="Export registry as CSV")
    p_discover.add_argument("--eu-register", help="Generate EU AI Database registration for a system")
    p_discover.add_argument("--format", "-f", choices=["text", "json"], default="text")
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

    # --- docs ---
    p_docs = subparsers.add_parser("docs", help="Generate documentation scaffolds (Annex IV, QMS)")
    p_docs.add_argument("--project", "-p", default=".")
    p_docs.add_argument("--output", "-o", default="docs", help="Output directory")
    p_docs.add_argument("--name", "-n", help="Project name")
    p_docs.add_argument("--qms", action="store_true", help="Also generate QMS scaffold (Article 17)")
    p_docs.add_argument("--all", action="store_true", help="Generate all documentation types")
    p_docs.set_defaults(func=cmd_docs)

    # --- compliance ---
    p_compliance = subparsers.add_parser("compliance", help="Manage compliance status of AI systems")
    p_compliance.add_argument("subcommand", nargs="?", choices=["update", "history", "workflow"], default=None)
    p_compliance.add_argument("--system", "-s", help="System name")
    p_compliance.add_argument("--status", help="New compliance status")
    p_compliance.add_argument("--note", "-n", help="Note for the status change")
    p_compliance.add_argument("--format", "-f", choices=["text", "json"], default="text")
    p_compliance.set_defaults(func=cmd_compliance)

    # --- gap ---
    p_gap = subparsers.add_parser("gap", help="Compliance gap assessment (Articles 9-15)")
    p_gap.add_argument("--project", "-p", default=".")
    p_gap.add_argument("--format", "-f", choices=["text", "json"], default="text")
    p_gap.add_argument("--article", "-a", help="Check specific article only (e.g., 14)")
    p_gap.add_argument("--strict", action="store_true", help="Exit 1 if overall score < 50")
    p_gap.set_defaults(func=cmd_gap)

    # --- benchmark ---
    p_bench = subparsers.add_parser("benchmark", help="Real-world validation benchmark")
    p_bench.add_argument("--project", "-p", default=".")
    p_bench.add_argument("--manifest", "-m", help="JSON manifest of projects to scan")
    p_bench.add_argument("--metrics", help="Calculate metrics from labelled CSV/JSON")
    p_bench.add_argument("--format", "-f", choices=["text", "json", "csv"], default="text")
    p_bench.add_argument("--output", "-o", help="Output file")
    p_bench.set_defaults(func=cmd_benchmark)

    # --- timeline ---
    p_timeline = subparsers.add_parser("timeline", help="EU AI Act enforcement timeline")
    p_timeline.add_argument("--format", "-f", choices=["text", "json"], default="text")
    p_timeline.set_defaults(func=cmd_timeline)

    # --- deps ---
    p_deps = subparsers.add_parser("deps", help="AI dependency supply chain analysis")
    p_deps.add_argument("--project", "-p", default=".")
    p_deps.add_argument("--format", "-f", choices=["text", "json"], default="text")
    p_deps.add_argument("--strict", action="store_true", help="Exit 1 if pinning score < 50")
    p_deps.set_defaults(func=cmd_deps)

    # --- sbom ---
    p_sbom = subparsers.add_parser("sbom", help="Generate AI Software Bill of Materials (CycloneDX 1.6)")
    p_sbom.add_argument("--project", "-p", default=".")
    p_sbom.add_argument("--format", "-f", choices=["json", "text"], default="json")
    p_sbom.add_argument("--output", "-o", help="Output file path")
    p_sbom.add_argument("--name", "-n", help="Project name")
    p_sbom.set_defaults(func=cmd_sbom)

    # --- agent ---
    p_agent = subparsers.add_parser("agent", help="Agentic AI governance monitoring")
    p_agent.add_argument("--session", "-s", help="Session ID")
    p_agent.add_argument("--hours", type=int, default=8)
    p_agent.add_argument("--format", "-f", choices=["text", "json"], default="text")
    p_agent.add_argument("--check-mcp", action="store_true", help="Check MCP configs for credentials")
    p_agent.add_argument("--config-file", help="Specific MCP config to check")
    p_agent.set_defaults(func=cmd_agent)

    args = parser.parse_args()

    if hasattr(args, 'config') and args.config:
        import os
        os.environ["REGULA_POLICY"] = args.config

    if not args.command:
        parser.print_help()
        sys.exit(2)

    try:
        args.func(args)
    except RegulaError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(e.exit_code)
    except KeyboardInterrupt:
        sys.exit(130)
    except BrokenPipeError:
        sys.exit(0)


if __name__ == "__main__":
    main()
