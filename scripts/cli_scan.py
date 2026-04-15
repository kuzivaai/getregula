"""Scanning commands for Regula CLI.

NOTE: Do NOT add 'from cli import ...' at module level.
cli.py imports this module at module level, creating a circular dependency.
All imports from cli must stay inside function bodies.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


def cmd_check(args) -> None:
    """Scan files for risk indicators."""
    from cli import (
        json_output, _validate_path, _is_tty, _get_changed_files,
        _resolve_jurisdictions, _enrich_findings_with_jurisdictions,
        _print_remediation, JURISDICTION_MAP,
    )
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

    # Multi-jurisdiction mapping: enrich findings with cross-framework labels
    jurisdiction_pairs = []
    if getattr(args, "jurisdictions", None):
        jurisdiction_pairs = _resolve_jurisdictions(args.jurisdictions)
        if jurisdiction_pairs:
            _enrich_findings_with_jurisdictions(findings, jurisdiction_pairs)

    # Partition findings via the pure function in findings_view.
    # This used to be 16 inlined lines mutating the input list; the
    # extraction lets us unit-test the partition (test_findings_view.py)
    # without going through the CLI.
    from findings_view import partition_findings
    _view = partition_findings(findings)
    active = _view["active"]
    suppressed = _view["suppressed"]
    prohibited = _view["prohibited"]
    credentials = _view["credentials"]
    high_risk = _view["high_risk"]
    limited = _view["limited"]
    autonomy = _view["autonomy"]
    block_findings = _view["block"]
    warn_findings = _view["warn"]
    info_findings = _view["info"]

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
        pass  # scan telemetry is best-effort; don't block output

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
                    continue  # file unreadable; skip
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
            # Sort findings for deterministic output
            findings.sort(key=lambda f: (f.get('file', ''), f.get('line', 0), f.get('pattern', '')))
            det = getattr(args, 'deterministic', False)
            json_output("check", {"findings": findings, "explanations": explained}, deterministic=det)
        else:
            # Sort findings for deterministic output
            findings.sort(key=lambda f: (f.get('file', ''), f.get('line', 0), f.get('pattern', '')))
            det = getattr(args, 'deterministic', False)
            json_output("check", findings, deterministic=det)
    elif args.format == "sarif":
        from report import generate_sarif
        name = args.name or Path(project).name
        print(json.dumps(generate_sarif(findings, name), indent=2))
    else:
        # Human-readable output
        from i18n import t
        from term_style import red, yellow, blue, magenta
        print(f"\n{t('scan_header', path=project)}")
        print(f"{'=' * 60}")
        # Use the scanner's real count, not "files with findings" —
        # the old derivation made empty scans look like nothing ran.
        stats = getattr(scan_files, "last_stats", {}) or {}
        total_files = stats.get("files_scanned", len(set(f["file"] for f in findings)))
        skip_tests_active = bool(stats.get("skip_tests", getattr(args, "skip_tests", False)))
        suffix = ""
        if total_files == 0 and skip_tests_active:
            suffix = " (test files excluded — use --no-skip-tests to include)"
        elif total_files == 0:
            suffix = " (no code files matched; check path and extensions)"
        files_label = f"{total_files}{suffix}"
        print(f"  {t('files_scanned'):<20}{files_label}")
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

        # Next-step suggestions (TTY only, when there are findings)
        if _is_tty() and active:
            first_file = active[0].get("file", "<file>")
            print("  Next steps:", file=sys.stderr)
            print(f"    regula explain --file {first_file:<30s} Explain why this was flagged", file=sys.stderr)
            print(f"    regula gap{'':<37s} Check Article 9-15 compliance gaps", file=sys.stderr)
            print(f"    regula timeline{'':<32s} See your enforcement deadlines", file=sys.stderr)
            print(file=sys.stderr)

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
                    continue  # file unreadable; skip
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


def cmd_classify(args) -> None:
    """Classify a text input."""
    from cli import json_output, _validate_path
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
        except (ValueError, TypeError, AttributeError):
            data = result.to_json()
        json_output("classify", data)
        return
    else:
        print(result.message)
        if result.exceptions:
            print(f"  Exceptions: {result.exceptions}")

    sys.exit(1 if result.tier.value == "prohibited" else 0)


def cmd_discover(args) -> None:
    """Discover AI systems."""
    from cli import json_output, _validate_path

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
            except (OSError, ValueError, KeyError, TypeError, ImportError, AttributeError) as e:
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


def cmd_guardrails(args) -> None:
    """Detect guardrail implementation coverage."""
    from cli import json_output, _validate_path
    from guardrail_scanner import scan_for_guardrails, format_guardrails_text

    if args.project != ".":
        _validate_path(args.project)
    result = scan_for_guardrails(args.project)
    fmt = getattr(args, "format", "text")
    if fmt == "json":
        json_output("guardrails", result)
    else:
        print(format_guardrails_text(result))
    if getattr(args, "strict", False) or getattr(args, "ci", False):
        if result.get("overall_score", 0) < 50:
            sys.exit(1)
