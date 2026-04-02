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
from datetime import datetime, timezone
from pathlib import Path

# Ensure scripts directory is importable
sys.path.insert(0, str(Path(__file__).parent))

from errors import RegulaError, PathError

VERSION = "1.5.0"


def json_output(command: str, data, exit_code: int = 0):
    """Standard JSON envelope for all --format json output."""
    envelope = {
        "format_version": "1.0",
        "regula_version": VERSION,
        "command": command,
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "exit_code": exit_code,
        "data": data,
    }
    print(json.dumps(envelope, indent=2, default=str))


def _validate_path(path_str: str) -> Path:
    """Validate and canonicalise a path. Raises PathError if invalid.

    Resolves symlinks to prevent traversal via symlink chains.
    """
    p = Path(path_str).resolve()
    if not p.exists():
        raise PathError(
            f"Path does not exist: {path_str}\n"
            f"  Check the path is correct and try again."
        )
    if not p.is_dir() and not p.is_file():
        raise PathError(
            f"Path is not a file or directory: {path_str}\n"
            f"  Usage: regula check /path/to/project or regula check file.py"
        )
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
    findings = scan_files(
        project,
        respect_ignores=not args.no_ignore,
        skip_tests=getattr(args, "skip_tests", False),
        min_tier=getattr(args, "min_tier", "") or "",
    )

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
    autonomy = [f for f in active if f["tier"] == "agent_autonomy"]

    # Assign finding tiers to all active findings
    for f in active:
        f["_finding_tier"] = _get_finding_tier_from_dict(f)

    block_findings = [f for f in active if f["_finding_tier"] == "block"]
    warn_findings = [f for f in active if f["_finding_tier"] == "warn"]
    info_findings = [f for f in active if f["_finding_tier"] == "info"]

    # Record scan metrics (best-effort, never blocks a scan)
    try:
        from metrics import record_scan as _record_scan
        display_tier_findings = (
            [{"tier": "BLOCK"}] * len(block_findings)
            + [{"tier": "WARN"}] * len(warn_findings)
            + [{"tier": "INFO"}] * len(info_findings)
        )
        _record_scan(display_tier_findings)
    except Exception:
        pass

    if args.format == "html":
        from pdf_export import generate_compliance_html_report
        from model_inventory import scan_for_models
        project_name = getattr(args, "name", None) or Path(project).name
        # Gather model inventory
        model_data = scan_for_models(project)
        # Gather framework names if requested
        fw_arg = getattr(args, "framework", None)
        framework_names = [f.strip() for f in fw_arg.split(",")] if fw_arg else None
        html_content = generate_compliance_html_report(
            findings,
            project_name,
            model_data=model_data,
            framework_names=framework_names,
        )
        output_file = getattr(args, "output", None)
        if output_file:
            out_path = Path(output_file)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(html_content, encoding="utf-8")
            print(f"Report written to {out_path}", file=sys.stderr)
        else:
            print(html_content)
        sys.exit(1 if block_findings else 0)
    elif args.format == "json":
        if getattr(args, "explain", False):
            from explain import explain_classification
            from ast_engine import detect_language as _detect_lang_json
            project_root = Path(args.path).resolve()
            explained = []
            seen_files = set()
            for f in active:
                if f["tier"] in ("minimal_risk",) or f["file"] in seen_files:
                    continue
                seen_files.add(f["file"])
                full_path = project_root / f["file"]
                if not full_path.is_file():
                    continue
                try:
                    content = full_path.read_text(encoding="utf-8", errors="ignore")
                except (PermissionError, OSError):
                    continue
                lang = _detect_lang_json(full_path.name) or "python"
                result = explain_classification(content, filepath=f["file"], language=lang)
                explained.append({
                    "file": f["file"],
                    "classification": result["classification"].to_dict(),
                    "pattern_matches": result["pattern_matches"],
                    "provider_deployer": result["provider_deployer"],
                    "obligation_roadmap": result["obligation_roadmap"],
                    "total_effort_hours": result["total_effort_hours"],
                })
            json_output("check", {"findings": findings, "explanations": explained})
        else:
            json_output("check", findings)
    elif args.format == "sarif":
        from report import generate_sarif
        name = args.name or Path(project).name
        print(json.dumps(generate_sarif(findings, name), indent=2))
    else:
        # Human-readable output
        from i18n import t
        from term_style import red, yellow, blue, magenta, bold, dim
        print(f"\n{t('scan_header', path=project)}")
        print(f"{'=' * 60}")
        total_files = len(set(f["file"] for f in findings))
        print(f"  {t('files_scanned'):<20}{total_files}")
        print(f"  {t('prohibited'):<20}{len(prohibited)}")
        print(f"  {t('credentials'):<20}{len(credentials)}")
        print(f"  {t('high_risk'):<20}{len(high_risk)}")
        print(f"  {t('agent_autonomy'):<20}{len(autonomy)}")
        print(f"  {t('limited_risk'):<20}{len(limited)}")
        print(f"  {t('suppressed'):<20}{len(suppressed)}")
        print(f"  {t('block_tier'):<20}{len(block_findings)}")
        print(f"  {t('warn_tier'):<20}{len(warn_findings)}")
        print(f"  {t('info_tier'):<20}{len(info_findings)}")

        if prohibited:
            print(f"\n  {red('PROHIBITED INDICATORS')}:")
            for f in prohibited:
                score = f.get("confidence_score", 0)
                tier_label = f.get("_finding_tier", "block").upper()
                print(f"    [{tier_label}] [{score:3d}] {f['file']} — {f.get('description', '')}")
                _print_remediation(f)

        if credentials:
            print(f"\n  {red('CREDENTIAL EXPOSURE')} (Article 15):")
            for f in credentials:
                score = f.get("confidence_score", 0)
                tier_label = f.get("_finding_tier", "warn").upper()
                print(f"    [{tier_label}] [{score:3d}] {f['file']}:{f.get('line', '?')} — {f.get('description', '')}")
                _print_remediation(f)

        if high_risk:
            print(f"\n  {yellow('HIGH-RISK INDICATORS')}:")
            for f in high_risk:
                score = f.get("confidence_score", 0)
                tier_label = f.get("_finding_tier", "warn").upper()
                print(f"    [{tier_label}] [{score:3d}] {f['file']} — {f.get('description', '')}")
                _print_remediation(f)

        if autonomy:
            print(f"\n  {magenta('AGENT AUTONOMY')} (OWASP Agentic ASI02/ASI04):")
            for f in autonomy:
                score = f.get("confidence_score", 0)
                tier_label = f.get("_finding_tier", "warn").upper()
                print(f"    [{tier_label}] [{score:3d}] {f['file']}:{f.get('line', '?')} — {f.get('description', '')}")
                _print_remediation(f)

        if limited:
            print(f"\n  {blue('LIMITED-RISK')}:")
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
        print(f"  {t('confidence_note')}")
        print(f"  {t('tier_note')}")
        print(f"  {t('suppress_note')}")
        print()

    # Explain mode: show detailed reasoning for each file
    if getattr(args, "explain", False) and args.format == "text":
        from explain import explain_classification, format_explanation
        from ast_engine import detect_language as _detect_lang

        # Collect unique files with non-trivial findings
        explain_files = set()
        for f in active:
            if f["tier"] not in ("minimal_risk",):
                explain_files.add(f["file"])

        if explain_files:
            print(f"\n{'=' * 60}")
            print(f"  DETAILED EXPLANATION")
            print(f"{'=' * 60}")
            project_root = Path(args.path).resolve()
            for rel_path in sorted(explain_files):
                full_path = project_root / rel_path
                if not full_path.is_file():
                    continue
                try:
                    content = full_path.read_text(encoding="utf-8", errors="ignore")
                except (PermissionError, OSError):
                    continue
                lang = _detect_lang(full_path.name) or "python"
                result = explain_classification(content, filepath=rel_path, language=lang)
                print(f"\n--- {rel_path} ---")
                print(format_explanation(result, filepath=rel_path))
                print()

    # Exit codes: 1 if any BLOCK-tier findings, 1 if WARN-tier and (--strict or --ci), 0 otherwise
    strict = args.strict or getattr(args, "ci", False)
    if block_findings:
        sys.exit(1)
    elif warn_findings and strict:
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
        import json as _json
        try:
            data = _json.loads(result.to_json())
        except Exception:
            data = result.to_json()
        json_output("classify", data)
        return
    else:
        print(result.message)
        if result.exceptions:
            print(f"  Exceptions: {result.exceptions}")

    sys.exit(1 if result.tier.value == "prohibited" else 0)


def cmd_report(args):
    """Generate reports."""
    from report import scan_files, generate_html_report, generate_sarif

    if hasattr(args, 'project') and args.project != ".":
        _validate_path(args.project)

    project_path = str(Path(args.project).resolve())
    project_name = args.name or Path(project_path).name

    print(f"Scanning {project_path}...", file=sys.stderr)
    findings = scan_files(project_path)
    print(f"Found {len(findings)} findings in {len(set(f['file'] for f in findings))} files", file=sys.stderr)

    audit_events = None
    chain_valid = None
    if args.include_audit:
        try:
            from log_event import query_events as _qe, verify_chain as _vc
            audit_events = _qe(limit=10000)
            chain_valid, _ = _vc()
        except (OSError, ValueError, KeyError):
            pass

    if args.format == "html":
        content = generate_html_report(findings, project_name, audit_events, chain_valid)
    elif args.format == "sarif":
        content = json.dumps(generate_sarif(findings, project_name), indent=2)
    else:
        # JSON format — wrap in standard envelope
        envelope = {
            "format_version": "1.0",
            "regula_version": VERSION,
            "command": "report",
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "exit_code": 0,
            "data": findings,
        }
        content = json.dumps(envelope, indent=2, default=str)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(content, encoding="utf-8")
        print(f"Report written to {out_path}", file=sys.stderr)
    else:
        print(content)


def cmd_audit(args):
    """Manage audit trail."""
    from log_event import log_event as _log, query_events, verify_chain, export_csv

    subcommand = args.subcommand or "verify"

    if subcommand == "log":
        data = json.loads(args.data) if getattr(args, "data", None) else {}
        ext_ts = getattr(args, "external_timestamp", False)
        event = _log(args.event_type, data, external_timestamp=ext_ts)
        json_output("audit log", {"status": "logged", "event_id": event.event_id})
    elif subcommand == "query":
        events = query_events(
            getattr(args, "event_type", None),
            getattr(args, "after", None),
            getattr(args, "before", None),
            getattr(args, "limit", 100),
        )
        json_output("audit query", events)
    elif subcommand == "export":
        events = query_events(
            getattr(args, "event_type", None),
            getattr(args, "after", None),
            getattr(args, "before", None),
            limit=100000,
        )
        fmt = getattr(args, "audit_format", "json") or "json"
        content = export_csv(events) if fmt == "csv" else json.dumps(events, indent=2)
        if args.output:
            out_path = Path(args.output).resolve()
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(content, encoding="utf-8")
            print(f"Exported {len(events)} events to {out_path}")
        else:
            print(content)
    elif subcommand == "verify":
        valid, error = verify_chain()
        json_output("audit verify", {"status": "valid" if valid else "invalid", "error": error},
                    exit_code=0 if valid else 1)
        if not valid:
            sys.exit(1)
    else:
        print(f"Unknown audit subcommand: {subcommand}", file=sys.stderr)
        sys.exit(2)


def cmd_mcp_server(args):
    """Start the Regula MCP server over stdio."""
    from mcp_server import run_server
    run_server()


def cmd_bias(args):
    """Evaluate model stereotype bias using CrowS-Pairs dataset."""
    from bias_eval import load_crowspairs_sample, evaluate_with_ollama
    pairs = load_crowspairs_sample(csv_path=getattr(args, "csv", None), max_pairs=args.sample)
    print(f"Loaded {len(pairs)} CrowS-Pairs pairs. Evaluating with {args.model}...")
    result = evaluate_with_ollama(pairs, model=args.model, endpoint=args.endpoint)
    fmt = getattr(args, "format", "text")
    if fmt == "json":
        json_output("bias", result)
    else:
        if result["status"] == "error":
            print(f"Error: {result['message']}", file=sys.stderr)
            sys.exit(1)
        print(f"\nBias Evaluation Results ({result['pairs_evaluated']} pairs)\n")
        print(f"{'Category':<25} {'Score':>6}  {'Interpretation'}")
        print("-" * 60)
        for cat, score in sorted(result["scores"].items()):
            interp = "neutral" if 45 <= score <= 55 else ("stereotyped" if score > 55 else "anti-stereotype")
            print(f"{cat:<25} {score:>5}%  {interp}")
        print("-" * 60)
        print(f"{'Overall':<25} {result['overall_score']:>5}%")
        print(f"\n{result['interpretation']}")


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
        json_output("discover", reg)
        return

    if args.org:
        from discover_ai_systems import scan_organization
        results = scan_organization(args.project)
        if args.format == "json":
            json_output("discover", results)
        else:
            print(f"\nOrganization Scan: {results['base_path']}")
            print(f"Projects scanned: {results['projects_scanned']}")
            print(f"AI projects found: {results['ai_projects_found']}")
            print(f"Risk distribution: {results['risk_distribution']}")
        return

    from discover_ai_systems import discover, print_discovery, register_system, load_registry, REGISTRY_PATH

    if getattr(args, "sync", False):
        # Re-scan all previously registered projects
        registry = load_registry()
        systems = registry.get("systems", {})
        if not systems:
            print("No systems registered. Run 'regula discover --register' first.")
            return
        synced = 0
        for name, info in list(systems.items()):
            project_path = info.get("project_path", "")
            if not project_path or not Path(project_path).is_dir():
                print(f"  Skipping {name}: path not found ({project_path})", file=sys.stderr)
                continue
            try:
                disc = discover(project_path)
                register_system(disc)
                synced += 1
                risk = disc["highest_risk"].upper().replace("_", "-")
                print(f"  Synced: {name} ({risk})")
            except Exception as e:  # Intentional: multiple error sources
                print(f"  Error syncing {name}: {e}", file=sys.stderr)
        print(f"\n{synced}/{len(systems)} systems synced.")
        return

    discovery = discover(args.project)

    if args.format == "json":
        json_output("discover", discovery)
        return
    else:
        print_discovery(discovery)

    if args.register:
        register_system(discovery)
        print(f"System '{discovery['project_name']}' registered in {REGISTRY_PATH}")


def cmd_install(args):
    """Install hooks for a platform."""
    from install import PLATFORMS, list_platforms, _find_regula_root

    if not args.platform or args.platform == "list":
        list_platforms()
        return

    regula_root = _find_regula_root()
    project_dir = Path(args.project).resolve()

    print(f"Regula root: {regula_root}")
    print(f"Project: {project_dir}")
    print(f"Platform: {args.platform}")
    print()

    installer = PLATFORMS[args.platform]
    installer(regula_root, project_dir)

    print()
    print("Installation complete. Run 'python3 scripts/report.py --project .' to verify.")


def cmd_status(args):
    """Show registry status."""
    from discover_ai_systems import load_registry, format_registry_csv

    registry = load_registry()
    systems = registry.get("systems", {})

    # --show <name>: detailed view of one system
    show_name = getattr(args, "show", None)
    if show_name:
        if show_name not in systems:
            print(f"System '{show_name}' not found in registry.", file=sys.stderr)
            sys.exit(1)
        info = systems[show_name]
        if getattr(args, "format", "text") == "json":
            json_output("status", {show_name: info})
        else:
            risk = info.get("highest_risk", "unknown").upper().replace("_", "-")
            prev = info.get("previous_highest_risk", "")
            trend = ""
            if prev:
                trend = f" (was: {prev.upper().replace('_', '-')})"
            print(f"\n  System:     {show_name}")
            print(f"  Risk:       {risk}{trend}")
            print(f"  Compliance: {info.get('compliance_status', 'unknown')}")
            print(f"  Registered: {info.get('registered_at', 'unknown')[:10]}")
            print(f"  Last scan:  {info.get('last_scanned', 'never')[:10]}")
            print(f"  Path:       {info.get('project_path', 'unknown')}")
            print(f"  Language:   {info.get('primary_language', 'unknown')}")
            libs = info.get("ai_libraries", [])
            print(f"  Libraries:  {', '.join(libs) if libs else 'none'}")
            models = info.get("model_files", [])
            print(f"  Model files: {len(models)}")
            code_files = info.get("ai_code_files", [])
            print(f"  AI files:   {len(code_files)}")
            risks = info.get("risk_classifications", [])
            if risks:
                print(f"  Findings:")
                for rc in risks:
                    print(f"    [{rc.get('tier', '?').upper().replace('_', '-')}] "
                          f"{rc.get('file', '?')} — {rc.get('description', '')}")
            print()
        return

    # --format csv: export
    fmt = getattr(args, "format", "text")
    if fmt == "csv":
        print(format_registry_csv(registry))
        return

    # --format json: structured export
    if fmt == "json":
        json_output("status", {"systems": systems, "count": len(systems)})
        return

    # Default: text table
    if not systems:
        print("No systems registered. Run 'regula discover --register' first.")
        return

    print(f"\n{'=' * 60}")
    print(f"  Regula System Registry — {len(systems)} system(s)")
    print(f"{'=' * 60}")

    for name, info in systems.items():
        risk = info.get("highest_risk", "unknown").upper().replace("_", "-")
        prev = info.get("previous_highest_risk", "")
        trend = f" (was {prev.upper().replace('_', '-')})" if prev else ""
        status = info.get("compliance_status", "unknown")
        libs = len(info.get("ai_libraries", []))
        last = info.get("last_scanned", "never")[:10]
        print(f"  {name:<30} {risk:<15}{trend:<20} {status:<15} {libs} libs  (scanned: {last})")

    print(f"{'=' * 60}\n")


def cmd_init(args):
    """Guided setup wizard."""
    from init_wizard import run_init
    run_init(Path(args.project).resolve(), interactive=args.interactive,
             dry_run=getattr(args, 'dry_run', False))


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
        envelope = {
            "format_version": "1.0",
            "regula_version": VERSION,
            "command": "feed",
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "exit_code": 0,
            "data": articles,
        }
        content = json.dumps(envelope, indent=2, default=str)
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
        if args.format == "json":
            import json as _json
            try:
                data = _json.loads(result.to_json())
            except Exception:
                data = result.to_json()
            json_output("questionnaire", data)
            return
        print(result.message)
    else:
        q = generate_questionnaire()
        if args.format == "json":
            json_output("questionnaire", q)
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
        json_output("session", profile)
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
            json_output("baseline", result)
        else:
            print(format_comparison_text(result))
        if args.fail_on_new and result.get("summary", {}).get("new", 0) > 0:
            sys.exit(1)
    else:
        print("Usage: regula baseline [save|compare]")


def cmd_docs(args):
    """Generate documentation scaffolds."""
    from generate_documentation import scan_project, generate_annex_iv, generate_qms_scaffold, generate_model_card
    from classify_risk import RiskTier

    project_path = str(Path(args.project).resolve())
    project_name = args.name or Path(project_path).name

    print(f"Scanning {project_path}...")
    findings = scan_project(project_path)

    ai_count = len(findings["ai_files"])
    model_count = len(findings["model_files"])
    highest = findings["highest_risk"]
    if isinstance(highest, RiskTier):
        highest = highest.value
    print(f"Found {ai_count} AI-related files, {model_count} model files")
    print(f"Highest risk tier: {highest.upper().replace('_', '-')}")

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    fmt = getattr(args, "format", "markdown")

    if fmt == "pdf":
        from pdf_export import generate_annex_iv_html, render_to_pdf
        html = generate_annex_iv_html(project_path, system_name=project_name)
        pdf_bytes = render_to_pdf(html, fallback_to_html=True)
        out_path = Path(args.output) if getattr(args, "output", None) and args.output != "docs" else Path(project_path) / "annex_iv.pdf"
        if pdf_bytes[:4] == b'%PDF':
            out_path.write_bytes(pdf_bytes)
            print(f"PDF written to: {out_path}")
        else:
            html_path = out_path.with_suffix(".html")
            html_path.write_text(html, encoding="utf-8")
            print(f"weasyprint not installed. HTML written to: {html_path}")
            print("Open in browser \u2192 File \u2192 Print \u2192 Save as PDF")
    elif fmt == "conformity-declaration":
        from generate_documentation import generate_conformity_declaration
        doc = generate_conformity_declaration(project_path, system_name=project_name)
        out_path = Path(project_path) / "declaration_of_conformity.md"
        out_path.write_text(doc, encoding="utf-8")
        print(f"Declaration of Conformity scaffold written to: {out_path}")
        print("IMPORTANT: This document requires legal review and authorised signature before use.")
    elif fmt == "model-card":
        card = generate_model_card(findings, project_name, project_path)
        card_file = output_dir / f"{project_name}_model_card.md"
        card_file.write_text(card, encoding="utf-8")
        print(f"Model card written to {card_file}")
    else:
        # Annex IV
        output_file = output_dir / f"{project_name}_annex_iv.md"
        doc = generate_annex_iv(findings, project_name, project_path)
        output_file.write_text(doc, encoding="utf-8")
        print(f"Annex IV documentation written to {output_file}")

        # Completion report
        if getattr(args, "completion", False):
            from generate_documentation import generate_completion_report
            print()
            print(generate_completion_report(project_name))

        # QMS scaffold
        if args.qms or getattr(args, "all", False):
            qms_file = output_dir / f"{project_name}_qms.md"
            qms_doc = generate_qms_scaffold(findings, project_name, project_path)
            qms_file.write_text(qms_doc, encoding="utf-8")
            print(f"QMS scaffold written to {qms_file}")

    try:
        from log_event import log_event as _log
        _log("documentation_generated", {
            "project": project_name, "highest_risk": highest,
            "ai_files": ai_count, "model_files": model_count,
            "types": ["annex_iv"] + (["qms"] if args.qms or getattr(args, "all", False) else []),
        })
    except (OSError,):
        pass


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
            json_output("compliance", history)
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
            json_output("compliance", summary)
        else:
            print(f"\n  {'System':<30} {'Status':<20} {'Risk':<15}")
            print(f"  {'-'*30} {'-'*20} {'-'*15}")
            for name, s in systems.items():
                status = s.get("compliance_status", "not_started")
                risk = s.get("highest_risk", "unknown").upper().replace("_", "-")
                print(f"  {name:<30} {status:<20} {risk:<15}")
            print()


def cmd_inventory(args):
    """Scan codebase for AI model references with GPAI tier annotations."""
    from model_inventory import scan_for_models, format_table
    import json as _json

    path = getattr(args, "path", ".") or "."
    if path != ".":
        _validate_path(path)

    result = scan_for_models(path)
    fmt = getattr(args, "format", "table")

    output_file = getattr(args, "output", None)
    if fmt == "json":
        if output_file:
            content = _json.dumps(result, indent=2)
            from pathlib import Path as _Path
            _Path(output_file).write_text(content, encoding="utf-8")
            print(f"Inventory written to {output_file}", file=sys.stderr)
        else:
            json_output("inventory", result)
        return
    else:
        content = format_table(result)

    if output_file:
        from pathlib import Path as _Path
        _Path(output_file).write_text(content, encoding="utf-8")
        print(f"Inventory written to {output_file}", file=sys.stderr)
    else:
        print(content)


def cmd_gap(args):
    """Compliance gap assessment."""
    if args.project != ".":
        _validate_path(args.project)
    from compliance_check import assess_compliance, format_gap_text
    articles = [args.article] if args.article else None
    fw_arg = getattr(args, "framework", None)
    frameworks = [f.strip() for f in fw_arg.split(",")] if fw_arg else None
    assessment = assess_compliance(args.project, articles=articles, frameworks=frameworks)
    if args.format == "json":
        json_output("gap", assessment)
    else:
        print(format_gap_text(assessment))
    # Exit 1 if overall score < 50 and --strict
    if args.strict and assessment.get("overall_score", 0) < 50:
        sys.exit(1)


def cmd_plan(args):
    """Generate prioritised remediation plan."""
    if args.project != ".":
        _validate_path(args.project)
    project_path = str(Path(args.project).resolve())
    project_name = args.name or Path(project_path).name

    from report import scan_files
    from compliance_check import assess_compliance
    from remediation_plan import generate_plan, format_plan_text, format_plan_status
    from remediation_plan import load_plan_status, mark_task_done

    if args.done:
        status = mark_task_done(project_path, args.done)
        print(f"Marked {args.done} as completed.")
        return

    if args.status:
        print(f"Scanning {project_path}...", file=sys.stderr)
        findings = scan_files(project_path)
        gap = assess_compliance(project_path)
        plan = generate_plan(findings, gap, project_name=project_name)
        status = load_plan_status(project_path)
        print(format_plan_status(plan, status))
        return

    print(f"Scanning {project_path}...", file=sys.stderr)
    findings = scan_files(project_path)
    gap = assess_compliance(project_path)
    plan = generate_plan(findings, gap, project_name=project_name)

    if args.format == "json":
        json_output("plan", plan)
    else:
        output = format_plan_text(plan)
        if args.output:
            out_path = Path(args.output)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(output, encoding="utf-8")
            print(f"Plan written to {out_path}", file=sys.stderr)
        else:
            print(output)


def cmd_disclose(args):
    """Generate Article 50 transparency disclosures."""
    from transparency import generate_disclosure, format_disclosure_text

    disclosure_type = args.type
    output_fmt = getattr(args, "template_format", "all")
    system_name = args.name or "AI System"

    result = generate_disclosure(disclosure_type, output_fmt, system_name)

    if args.format == "json":
        json_output("disclose", result)
    else:
        if isinstance(result, dict) and "type" not in result and "error" not in result:
            text = format_disclosure_text(result)
        else:
            text = format_disclosure_text({result.get("type", "?"): result})
        print(text)


def cmd_fix(args):
    """Generate compliance fix scaffolds for findings."""
    if args.project != ".":
        _validate_path(args.project)
    project_path = str(Path(args.project).resolve())

    from report import scan_files
    from remediation import get_remediation

    print(f"Scanning {project_path}...", file=sys.stderr)
    findings = scan_files(project_path)

    # Filter to actionable findings (high-risk and prohibited only)
    actionable = [
        f for f in findings
        if f.get("tier") in ("high_risk", "prohibited") and not f.get("suppressed")
    ]

    if not actionable:
        if args.format == "json":
            json_output("fix", {"fixes": [], "message": "No actionable findings."})
        else:
            print("No high-risk or prohibited findings to fix.")
        return

    fixes = []
    for finding in actionable:
        rem = get_remediation(finding)
        fix_entry = {
            "file": finding.get("file", "?"),
            "line": finding.get("line", "?"),
            "tier": finding["tier"],
            "category": finding.get("category", "unknown"),
            "summary": rem.get("summary", ""),
            "article": rem.get("article", ""),
            "explanation": rem.get("explanation", ""),
            "fix_code": rem.get("fix_code", ""),
        }
        fixes.append(fix_entry)

    if args.format == "json":
        json_output("fix", {"fixes": fixes, "total": len(fixes)})
    else:
        print(f"# Compliance Fixes — {len(fixes)} actionable findings\n")
        seen_categories = set()
        for fix in fixes:
            cat = fix["category"]
            if cat in seen_categories:
                continue
            seen_categories.add(cat)

            print(f"## {fix['file']}:{fix['line']} — {fix['tier'].upper().replace('_', '-')}")
            print(f"   Category: {fix['category']}")
            print(f"   Article: {fix['article']}")
            print(f"   {fix['summary']}")
            print(f"   {fix['explanation']}")
            if fix["fix_code"]:
                print(f"\n   Suggested code scaffold:")
                print(f"   {'─' * 40}")
                for code_line in fix["fix_code"].replace("\\n", "\n").split("\n"):
                    print(f"   {code_line}")
                print(f"   {'─' * 40}")
            print()

        if args.output:
            out_path = Path(args.output)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            lines = []
            for fix in fixes:
                cat = fix["category"]
                lines.append(f"# {fix['file']}:{fix['line']} — {fix['article']}")
                lines.append(f"# {fix['summary']}")
                if fix["fix_code"]:
                    lines.append(fix["fix_code"].replace("\\n", "\n"))
                lines.append("")
            out_path.write_text("\n".join(lines), encoding="utf-8")
            print(f"Fix scaffolds written to {out_path}", file=sys.stderr)


def cmd_evidence_pack(args):
    """Generate compliance evidence pack."""
    if args.project != ".":
        _validate_path(args.project)
    project_path = str(Path(args.project).resolve())
    project_name = args.name or Path(project_path).name

    from evidence_pack import generate_evidence_pack

    print(f"Generating evidence pack for {project_path}...", file=sys.stderr)
    result = generate_evidence_pack(
        project_path,
        output_dir=args.output,
        project_name=project_name,
    )

    if args.format == "json":
        json_output("evidence-pack", result)
    else:
        pack_path = result["pack_path"]
        file_count = len(result["manifest"]["files"])
        print(f"Evidence pack written to: {pack_path}")
        print(f"Contains {file_count} files with SHA-256 integrity hashes.")
        print(f"Start with: {pack_path}/00-summary.md")


def cmd_benchmark(args):
    """Run real-world validation benchmark."""
    from benchmark import benchmark_project, benchmark_suite, calculate_metrics, load_labelled_results
    from benchmark import format_benchmark_text, format_benchmark_json, format_labelling_csv

    if args.metrics:
        results = load_labelled_results(args.metrics)
        metrics = calculate_metrics(results)
        json_output("benchmark", metrics)
        return

    if args.manifest:
        projects = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
        results = benchmark_suite(projects)
    else:
        results = benchmark_project(args.project)

    if args.format == "csv":
        content = format_labelling_csv(results)
    elif args.format == "json":
        envelope = {"format_version": "1.0", "regula_version": VERSION,
                    "command": "benchmark", "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                    "exit_code": 0, "data": results}
        content = json.dumps(envelope, indent=2, default=str)
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
        json_output("timeline", {"as_of": date.today().isoformat(), "timeline": TIMELINE})
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
            json_output("agent", findings)
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
        json_output("agent", analysis)
    else:
        print(format_agent_text(analysis))


def cmd_deps(args):
    """Dependency supply chain analysis."""
    if args.project != ".":
        _validate_path(args.project)
    from dependency_scan import scan_dependencies, format_dep_text
    results = scan_dependencies(args.project)
    if args.format == "json":
        json_output("deps", results)
    else:
        print(format_dep_text(results))
    if results.get("compromised_count", 0) > 0:
        sys.exit(1)
    elif args.strict and results.get("pinning_score", 100) < 50:
        sys.exit(1)


def cmd_doctor(args):
    """Check installation health."""
    from doctor import run_doctor
    result = run_doctor(format_type=args.format)
    if args.format == "json":
        json_output("doctor", result, exit_code=0 if result["healthy"] else 1)
        sys.exit(0 if result["healthy"] else 1)
    else:
        sys.exit(0 if result else 1)


def cmd_security_self_check(args):
    """Scan regula's own source with its own rules."""
    from security_self_check import run_security_self_check
    result = run_security_self_check(format_type=args.format)
    if args.format == "json":
        json_output("security-self-check", result, exit_code=0 if result["passed"] else 1)
    sys.exit(0 if result["passed"] else 1)


def _print_metrics_text(stats: dict) -> None:
    """Print metrics in human-readable format."""
    from i18n import t
    print(f"\n{t('metrics_header')}\n")

    total_scans = stats.get("total_scans", 0)
    total_findings = stats.get("total_findings", 0)
    first_scan = stats.get("first_scan")
    last_scan = stats.get("last_scan")

    first_str = first_scan[:10] if first_scan else "N/A"
    last_str = last_scan[:10] if last_scan else "N/A"

    print(f"  {t('metrics_total_scans'):<20}{total_scans}")
    print(f"  {t('metrics_total_findings'):<20}{total_findings}")
    print(f"  {t('metrics_first_scan'):<20}{first_str}")
    print(f"  {t('metrics_last_scan'):<20}{last_str}")

    findings_by_tier = stats.get("findings_by_tier", {})
    if findings_by_tier:
        print(f"\n  {t('metrics_by_tier')}")
        for tier, count in sorted(findings_by_tier.items()):
            print(f"    {tier:<8} {count}")
    print()


def cmd_metrics(args):
    """Show local usage statistics."""
    from metrics import get_stats, reset_stats
    if args.reset:
        reset_stats()
        print("Metrics reset.")
        return
    stats = get_stats()
    if args.format == "json":
        json_output("metrics", stats)
    else:
        _print_metrics_text(stats)


def cmd_self_test(args):
    """Run built-in self-test assertions."""
    from self_test import run_self_test
    ok = run_self_test()
    sys.exit(0 if ok else 1)


def cmd_quickstart(args):
    """60-second onboarding — create policy, run first scan, show next steps."""
    from quickstart import run_quickstart
    result = run_quickstart(
        project_dir=args.project,
        org=getattr(args, "org", "My Organisation"),
        format_type=args.format,
    )
    if args.format == "json":
        json_output("quickstart", result)
    sys.exit(0)


def cmd_config(args):
    """Config management commands."""
    from config_validator import validate_config
    if args.config_action == "validate":
        result = validate_config(
            path=getattr(args, "file", None),
            format_type=args.format,
        )
        if args.format == "json":
            json_output("config validate", result, exit_code=0 if result["valid"] else 2)
        sys.exit(0 if result["valid"] else 2)
    else:
        print(f"Unknown config action: {args.config_action}", file=sys.stderr)
        sys.exit(2)


_MAIN_EPILOG = """
Examples:
  regula check .                          Scan current directory
  regula check --format sarif .           Output SARIF for CI/CD
  regula plan --project .                 Prioritised remediation plan
  regula evidence-pack --project .        Auditor-ready evidence package
  regula fix --project .                  Compliance code scaffolds
  regula disclose --type chatbot          Article 50 transparency notices
  regula docs --project . --qms          Generate Annex IV + QMS scaffolds
  regula gap --project .                  Compliance gap assessment (Articles 9-15)
  regula timeline                         EU AI Act enforcement dates
  regula deps --project .                 AI dependency supply chain analysis
  regula audit verify                     Verify audit chain integrity
"""


def _build_subparsers(subparsers):
    """Define all CLI subcommands. Extracted from main() for readability."""
    p_init = subparsers.add_parser("init", help="Guided setup wizard")
    p_init.add_argument("--project", "-p", default=".", help="Project directory")
    p_init.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
    p_init.add_argument("--dry-run", action="store_true", help="Show analysis without creating files")
    p_init.set_defaults(func=cmd_init)

    # --- check ---
    p_check = subparsers.add_parser("check", help="Scan files for risk indicators")
    p_check.add_argument("path", nargs="?", default=".", help="Path to scan")
    p_check.add_argument("--format", "-f", choices=["text", "json", "sarif", "html"], default="text")
    p_check.add_argument("--output", "-o", help="Output file (use with --format html)")
    p_check.add_argument(
        "--framework",
        metavar="FRAMEWORKS",
        help="Include cross-framework mappings in HTML report (comma-separated): "
             "nist-ai-rmf, iso-42001, nist-csf, soc2, iso-27001, owasp-llm-top10, mitre-atlas, all",
    )
    p_check.add_argument("--name", "-n", help="Project name for SARIF output")
    p_check.add_argument("--no-ignore", action="store_true", help="Don't respect regula-ignore comments")
    p_check.add_argument("--strict", action="store_true", help="Exit 1 on WARN-tier findings")
    p_check.add_argument("--ci", action="store_true", default=False,
                         help="CI mode: exit 1 on any WARN or BLOCK finding (implies --strict)")
    p_check.add_argument("--verbose", "-v", action="store_true", help="Show INFO-tier findings")
    p_check.add_argument("--skip-tests", action="store_true", default=True,
                         help="Exclude test files from results (default: on, use --no-skip-tests to include)")
    p_check.add_argument("--no-skip-tests", dest="skip_tests", action="store_false",
                         help="Include test files in results")
    p_check.add_argument("--min-tier", choices=["prohibited", "high_risk", "limited_risk", "minimal_risk"],
                         default="limited_risk", help="Minimum risk tier to include (default: limited_risk, use minimal_risk to see all)")
    p_check.add_argument("--diff", metavar="REF", nargs="?", const="HEAD~1",
                         help="Only scan files changed since REF (default: HEAD~1)")
    p_check.add_argument("--rules", help="Path to custom rules file (regula-rules.yaml)")
    p_check.add_argument("--explain", action="store_true",
                         help="Show detailed classification reasoning, obligation roadmap, and effort estimates")
    p_check.add_argument("--lang", choices=["en", "pt-BR", "de"], default=None,
                         help="Output language (default: en)")
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
    p_audit.add_argument(
        "--external-timestamp", action="store_true",
        help="Attach RFC 3161 timestamp from FreeTSA to new audit events (requires network)"
    )
    p_audit.set_defaults(func=cmd_audit)

    # --- mcp-server ---
    p_mcp = subparsers.add_parser("mcp-server", help="Start the Regula MCP server (stdio transport)")
    p_mcp.set_defaults(func=cmd_mcp_server)

    # --- bias ---
    p_bias = subparsers.add_parser("bias", help="Evaluate model bias using CrowS-Pairs dataset")
    p_bias.add_argument("--model", default="llama3", help="Ollama model name (default: llama3)")
    p_bias.add_argument("--endpoint", default="http://localhost:11434", help="Ollama API endpoint")
    p_bias.add_argument("--sample", type=int, default=100, help="Number of pairs to evaluate (default: 100)")
    p_bias.add_argument("--csv", help="Path to local CrowS-Pairs CSV file")
    p_bias.add_argument("--format", choices=["text", "json"], default="text")
    p_bias.set_defaults(func=cmd_bias)

    # --- discover ---
    p_discover = subparsers.add_parser("discover", help="Discover AI systems in a project")
    p_discover.add_argument("--project", "-p", default=".")
    p_discover.add_argument("--register", "-r", action="store_true")
    p_discover.add_argument("--org", action="store_true", help="Scan all projects in directory (org-level inventory)")
    p_discover.add_argument("--csv", action="store_true", help="Export registry as CSV")
    p_discover.add_argument("--eu-register", help="Generate EU AI Database registration for a system")
    p_discover.add_argument("--sync", action="store_true", help="Re-scan all previously registered projects")
    p_discover.add_argument("--format", "-f", choices=["text", "json"], default="text")
    p_discover.set_defaults(func=cmd_discover)

    # --- install ---
    p_install = subparsers.add_parser("install", help="Install hooks for a platform")
    p_install.add_argument("platform", nargs="?", help="Platform (claude-code, copilot-cli, windsurf, pre-commit, git-hooks)")
    p_install.add_argument("--project", "-p", default=".")
    p_install.set_defaults(func=cmd_install)

    # --- status ---
    p_status = subparsers.add_parser("status", help="Show system registry status")
    p_status.add_argument("--show", metavar="NAME", help="Show detailed info for one system")
    p_status.add_argument("--format", "-f", choices=["text", "json", "csv"], default="text")
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
    p_docs.add_argument("--format", "-f", choices=["markdown", "model-card", "pdf", "conformity-declaration"], default="markdown")
    p_docs.add_argument("--qms", action="store_true", help="Also generate QMS scaffold (Article 17)")
    p_docs.add_argument("--all", action="store_true", help="Generate all documentation types")
    p_docs.add_argument("--completion", action="store_true", help="Show completion percentage per Annex IV section")
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
    p_gap.add_argument(
        "--framework",
        metavar="FRAMEWORKS",
        help="Cross-reference findings to other frameworks (comma-separated): "
             "nist-ai-rmf, iso-42001, nist-csf, soc2, iso-27001, owasp-llm-top10, mitre-atlas, all",
    )
    p_gap.set_defaults(func=cmd_gap)

    # --- plan ---
    p_plan = subparsers.add_parser("plan", help="Generate prioritised remediation plan")
    p_plan.add_argument("--project", "-p", default=".")
    p_plan.add_argument("--format", "-f", choices=["text", "json"], default="text")
    p_plan.add_argument("--output", "-o", help="Write plan to file")
    p_plan.add_argument("--name", "-n", help="Project name")
    p_plan.add_argument("--status", action="store_true", help="Show completion progress")
    p_plan.add_argument("--done", metavar="TASK-ID", help="Mark a task as completed")
    p_plan.set_defaults(func=cmd_plan)

    # --- disclose ---
    p_disclose = subparsers.add_parser("disclose", help="Generate Article 50 transparency disclosures")
    p_disclose.add_argument("--type", "-t", choices=["chatbot", "synthetic_text", "emotion_recognition", "deepfake", "all"],
                            default="all", help="Disclosure type (default: all)")
    p_disclose.add_argument("--template-format", choices=["text", "html", "code", "all"], default="all",
                            help="Template format to generate")
    p_disclose.add_argument("--name", "-n", help="AI system name for templates")
    p_disclose.add_argument("--format", "-f", choices=["text", "json"], default="text")
    p_disclose.set_defaults(func=cmd_disclose)

    # --- fix ---
    p_fix = subparsers.add_parser("fix", help="Generate compliance fix scaffolds for findings")
    p_fix.add_argument("--project", "-p", default=".")
    p_fix.add_argument("--format", "-f", choices=["text", "json"], default="text")
    p_fix.add_argument("--output", "-o", help="Write fix scaffolds to file")
    p_fix.set_defaults(func=cmd_fix)

    # --- evidence-pack ---
    p_evidence = subparsers.add_parser("evidence-pack", help="Generate compliance evidence pack for auditors")
    p_evidence.add_argument("--project", "-p", default=".")
    p_evidence.add_argument("--output", "-o", default=".", help="Output directory for the pack folder")
    p_evidence.add_argument("--name", "-n", help="Project name")
    p_evidence.add_argument("--format", "-f", choices=["text", "json"], default="text")
    p_evidence.set_defaults(func=cmd_evidence_pack)

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

    # --- doctor ---
    p_doctor = subparsers.add_parser("doctor", help="Check installation health")
    p_doctor.add_argument("--format", "-f", choices=["text", "json"], default="text")
    p_doctor.set_defaults(func=cmd_doctor)

    # --- metrics ---
    p_metrics = subparsers.add_parser("metrics", help="Show local usage statistics (never sent)")
    p_metrics.add_argument("--format", "-f", choices=["text", "json"], default="text")
    p_metrics.add_argument("--reset", action="store_true", help="Clear all local metrics")
    p_metrics.set_defaults(func=cmd_metrics)

    # --- security-self-check ---
    p_ssc = subparsers.add_parser("security-self-check", help="Verify regula's own source is clean")
    p_ssc.add_argument("--format", "-f", choices=["text", "json"], default="text")
    p_ssc.set_defaults(func=cmd_security_self_check)

    # --- self-test ---
    p_selftest = subparsers.add_parser("self-test", help="Verify installation works")
    p_selftest.set_defaults(func=cmd_self_test)

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

    # --- inventory ---
    p_inventory = subparsers.add_parser("inventory", help="Scan codebase for AI model references (GPAI tier annotations)")
    p_inventory.add_argument("path", nargs="?", default=".", help="Path to scan")
    p_inventory.add_argument("--format", "-f", choices=["table", "json"], default="table")
    p_inventory.add_argument("--output", "-o", help="Output file (optional)")
    p_inventory.set_defaults(func=cmd_inventory)

    # --- quickstart ---
    p_qs = subparsers.add_parser("quickstart", help="60-second onboarding (create policy + first scan)")
    p_qs.add_argument("--project", "-p", default=".", help="Project directory")
    p_qs.add_argument("--org", default="My Organisation", help="Organisation name for policy file")
    p_qs.add_argument("--format", "-f", choices=["text", "json"], default="text")
    p_qs.set_defaults(func=cmd_quickstart)

    # --- config ---
    p_config = subparsers.add_parser("config", help="Config management (validate, etc.)")
    config_sub = p_config.add_subparsers(dest="config_action")

    p_config_validate = config_sub.add_parser("validate", help="Validate policy config file")
    p_config_validate.add_argument("--file", "-f", help="Path to config file (auto-discovers if omitted)")
    p_config_validate.add_argument("--format", choices=["text", "json"], default="text")
    p_config.set_defaults(func=cmd_config, config_action="validate")
    p_config_validate.set_defaults(func=cmd_config, config_action="validate")


def main():
    parser = argparse.ArgumentParser(
        prog="regula",
        description="AI Governance Risk Indication for Code",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=_MAIN_EPILOG,
    )
    parser.add_argument("--ci", action="store_true",
                        help="CI mode: exit 1 on any WARN or BLOCK finding (implies --strict)")
    parser.add_argument("--config", help="Custom policy configuration file path")
    parser.add_argument("--rules", help="Path to custom rules file (regula-rules.yaml)")
    parser.add_argument("--lang", choices=["en", "pt-BR", "de"], default="en",
                        help="Output language (default: en)")

    subparsers = parser.add_subparsers(dest="command")
    _build_subparsers(subparsers)

    args = parser.parse_args()

    if hasattr(args, 'lang') and args.lang:
        from i18n import set_language
        set_language(args.lang)

    if hasattr(args, 'config') and args.config:
        import os
        os.environ["REGULA_POLICY"] = args.config

    if hasattr(args, 'rules') and args.rules:
        from custom_rules import load_custom_rules
        import classify_risk
        classify_risk._CUSTOM_RULES = load_custom_rules(args.rules)

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
    except Exception as e:
        print(f"Internal error: {e}", file=sys.stderr)
        print("This is a bug in Regula. Please report it at https://github.com/kuzivaai/getregula/issues", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
