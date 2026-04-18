"""Scanning commands for Regula CLI.

NOTE: Do NOT add 'from cli import ...' at module level.
cli.py imports this module at module level, creating a circular dependency.
All imports from cli must stay inside function bodies.
"""

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


# Mapping from Regula's display tier to GitHub Actions workflow command level.
# ::error     — surfaces as a red annotation on the file/line in PR diffs
# ::warning   — yellow annotation
# ::notice    — blue/informational annotation
_GHA_LEVEL = {"block": "error", "warn": "warning", "info": "notice"}


def _gha_escape(value: str) -> str:
    """Percent-encode characters that break GitHub workflow-command parsing.

    Workflow commands are terminated by a newline, so CR/LF must be escaped.
    Colons and commas inside parameter *values* (file path) are escaped too —
    the message itself only needs CR/LF escaping.
    See: https://docs.github.com/actions/reference/workflow-commands-for-github-actions
    """
    return (
        value.replace("%", "%25")
        .replace("\r", "%0D")
        .replace("\n", "%0A")
    )


def _emit_github_annotations(args, display_view) -> None:
    """Emit one workflow command per finding when running in GitHub Actions.

    Activates only when GITHUB_ACTIONS=true AND --ci (or REGULA_STRICT) is set,
    so local runs and non-CI environments stay quiet. SARIF output remains
    available via --format sarif for repos that want CodeQL integration.
    """
    if os.environ.get("GITHUB_ACTIONS", "").lower() != "true":
        return
    if not getattr(args, "ci", False):
        return

    scan_root = Path(getattr(args, "path", ".") or ".")

    def _as_repo_path(rel: str) -> str:
        # Finding paths are relative to the scan root. Prepend scan root so
        # GitHub can resolve the file in the repo checkout.
        if not rel:
            return ""
        if rel.startswith(str(scan_root)) or Path(rel).is_absolute():
            return rel
        joined = scan_root / rel if str(scan_root) not in ("", ".") else Path(rel)
        return str(joined).replace("\\", "/")

    for display_tier in ("block", "warn", "info"):
        level = _GHA_LEVEL[display_tier]
        for finding in display_view.get(display_tier, []):
            file_path = _gha_escape(_as_repo_path(finding.get("file", "")))
            line = finding.get("line") or 1
            msg = finding.get("description") or finding.get("message") or ""
            score = finding.get("confidence_score")
            if score is not None:
                msg = f"{msg} (confidence: {score})"
            msg = _gha_escape(msg)
            # stdout, not stderr — GitHub Actions parses workflow commands
            # from either stream, but stdout is the documented default.
            print(f"::{level} file={file_path},line={line}::{msg}")


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

    # Scope filtering: exclude non-production files when --scope production
    scope = getattr(args, "scope", "all")
    if scope == "production":
        findings = [f for f in findings if f.get("provenance", "production") == "production"]

    # GDPR dual-compliance patterns: merge into findings when requested
    if getattr(args, "include_gdpr", False):
        from gdpr_scan import scan_gdpr
        gdpr_result = scan_gdpr(project, scope=scope)
        findings.extend(gdpr_result["findings"])

    # Diff mode: filter findings to only changed files
    if args.diff:
        changed = _get_changed_files(project, args.diff)
        if changed:
            findings = [f for f in findings if f.get("file", "") in changed]
            print(f"  Diff mode: {len(changed)} files changed since {args.diff}", file=sys.stderr)
        else:
            print(f"  Diff mode: no changed files found since {args.diff} (showing all)", file=sys.stderr)

    # Lifecycle phase filter: keep only findings matching the requested phase
    lifecycle_filter = getattr(args, "lifecycle", None)
    if lifecycle_filter:
        findings = [f for f in findings if lifecycle_filter in f.get("lifecycle_phases", [])]

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
    accepted = _view.get("accepted", [])
    prohibited = _view["prohibited"]
    credentials = _view["credentials"]
    high_risk = _view["high_risk"]
    limited = _view["limited"]
    autonomy = _view["autonomy"]
    block_findings = _view["block"]
    warn_findings = _view["warn"]
    info_findings = _view["info"]

    # --audit-suppressions: list all annotations with status (ISO 42001 9.1)
    if getattr(args, "audit_suppressions", False):
        _print_suppression_audit(findings)
        issues = [f for f in findings
                  if f.get("risk_decision") and (
                      f["risk_decision"].get("warning")
                      or f["risk_decision"].get("error")
                      or f["risk_decision"].get("overdue")
                  )]
        sys.exit(1 if issues else 0)

    # Record scan metrics with per-pattern breakdown (best-effort)
    try:
        from metrics import record_scan as _record_scan
        # Pass full findings so metrics can track per-pattern stats
        _record_scan(findings)
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
        tests_skipped = int(stats.get("tests_skipped", 0))
        suffix = ""
        # Only blame the test-file exclusion when tests were ACTUALLY
        # skipped. Without this check, an empty directory or one with
        # only non-code files would misleadingly claim tests were excluded.
        if total_files == 0 and tests_skipped > 0:
            suffix = (
                f" ({tests_skipped} test file(s) excluded — "
                f"use --no-skip-tests to include)"
            )
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
        if accepted:
            overdue = [f for f in accepted if f.get("risk_decision", {}).get("overdue")]
            print(f"  {'Accepted risks:':<20}{len(accepted)}  ({len(overdue)} overdue)")
        # Warn on undocumented suppressions
        no_rationale = [f for f in suppressed
                        if f.get("risk_decision") and not f["risk_decision"].get("rationale")]
        if no_rationale:
            print(f"\n  \u26a0 {len(no_rationale)} suppression(s) without rationale"
                  " \u2014 run regula check --audit-suppressions for details")
        if accepted:
            overdue_list = [f for f in accepted if f.get("risk_decision", {}).get("overdue")]
            if overdue_list:
                print(f"  \u26a0 {len(overdue_list)} accepted risk(s) overdue for review"
                      " \u2014 run regula check --audit-suppressions for details")
        print(f"  {t('block_tier'):<20}{len(block_findings)}")
        print(f"  {t('warn_tier'):<20}{len(warn_findings)}")
        print(f"  {t('info_tier'):<20}{len(info_findings)}")

        # Lifecycle phase breakdown
        phase_counts = {}
        for f in active:
            for phase in f.get("lifecycle_phases", ["develop"]):
                phase_counts[phase] = phase_counts.get(phase, 0) + 1
        if phase_counts:
            phase_str = ", ".join(f"{p}: {c}" for p, c in sorted(phase_counts.items()))
            print(f"  {'Lifecycle:':<20}{phase_str}")

        # === First-run verdict: answer "Am I affected?" ===
        if prohibited:
            verdict_tier = "PROHIBITED"
            verdict_desc = "Your project contains AI practices prohibited under EU AI Act Article 5."
            verdict_action = "These must be removed before deployment in the EU."
            verdict_color = red
        elif high_risk or credentials:
            verdict_tier = "HIGH-RISK"
            verdict_desc = "Your project is classified as high-risk under EU AI Act Annex III."
            verdict_action = "You must comply with Articles 9-15 before the enforcement deadline."
            verdict_color = yellow
        elif limited:
            verdict_tier = "LIMITED-RISK"
            verdict_desc = "Your project has limited-risk AI components (Article 50 transparency)."
            verdict_action = "You must disclose AI usage to users."
            verdict_color = blue
        elif active:
            verdict_tier = "MINIMAL-RISK"
            verdict_desc = "Your project uses AI but with minimal regulatory obligations."
            verdict_action = "No mandatory requirements, but good governance is recommended."
            verdict_color = lambda x: x
        else:
            verdict_tier = "NO AI DETECTED"
            verdict_desc = "No AI components or risk indicators found in your project."
            verdict_action = "The EU AI Act likely does not apply to this project."
            verdict_color = lambda x: x

        print(f"\n  {verdict_color('Verdict')}: {verdict_color(verdict_tier)}")
        print(f"  {verdict_desc}")
        print(f"  {verdict_action}")

        # Top findings driving the verdict
        top = sorted(
            [f for f in active if not f.get("open_question")],
            key=lambda f: -f.get("confidence_score", 0),
        )[:3]
        if top:
            print(f"\n  Why:")
            for i, f in enumerate(top, 1):
                arts = ", ".join(f.get("articles", [])[:2]) if f.get("articles") else f.get("tier", "")
                print(f"    {i}. {f['file']}:{f.get('line', '?')} — {f.get('description', '')[:80]}")
                if arts:
                    print(f"       ({arts})")

        if prohibited:
            print(f"\n  {red('PROHIBITED INDICATORS')}:")
            for f in prohibited:
                score = f.get("confidence_score", 0)
                tier_label = f.get("_finding_tier", "block").upper()
                lp = f" [{f.get('lifecycle_phases', ['develop'])[0]}]" if f.get("lifecycle_phases") else ""
                print(f"    [{tier_label}] [{score:3d}] {f['file']} — {f.get('description', '')}{lp}")
                _print_remediation(f)

        if credentials:
            print(f"\n  {red('CREDENTIAL EXPOSURE')} (Article 15):")
            for f in credentials:
                score = f.get("confidence_score", 0)
                tier_label = f.get("_finding_tier", "warn").upper()
                lp = f" [{f.get('lifecycle_phases', ['develop'])[0]}]" if f.get("lifecycle_phases") else ""
                print(f"    [{tier_label}] [{score:3d}] {f['file']}:{f.get('line', '?')} — {f.get('description', '')}{lp}")
                _print_remediation(f)

        if high_risk:
            print(f"\n  {yellow('HIGH-RISK INDICATORS')}:")
            for f in high_risk:
                score = f.get("confidence_score", 0)
                tier_label = f.get("_finding_tier", "warn").upper()
                lp = f" [{f.get('lifecycle_phases', ['develop'])[0]}]" if f.get("lifecycle_phases") else ""
                print(f"    [{tier_label}] [{score:3d}] {f['file']} — {f.get('description', '')}{lp}")
                _print_remediation(f)

        if autonomy:
            print(f"\n  {magenta('AGENT AUTONOMY')} (OWASP Agentic ASI02/ASI04):")
            for f in autonomy:
                score = f.get("confidence_score", 0)
                tier_label = f.get("_finding_tier", "warn").upper()
                lp = f" [{f.get('lifecycle_phases', ['develop'])[0]}]" if f.get("lifecycle_phases") else ""
                print(f"    [{tier_label}] [{score:3d}] {f['file']}:{f.get('line', '?')} — {f.get('description', '')}{lp}")
                _print_remediation(f)

        if limited:
            # Limited-risk findings (Article 50 transparency) are surfaced
            # the same way high-risk and credential findings are: one row
            # per finding, no verbose-only suppression. The previous
            # behaviour skipped every INFO-tier row while still printing
            # the section header, producing a header with no rows beneath.
            print(f"\n  {blue('LIMITED-RISK')} (Article 50):")
            for f in limited:
                score = f.get("confidence_score", 0)
                tier_label = f.get("_finding_tier", "info").upper()
                lp = f" [{f.get('lifecycle_phases', ['develop'])[0]}]" if f.get("lifecycle_phases") else ""
                print(f"    [{tier_label}] [{score:3d}] {f['file']}:{f.get('line', '?')} — {f.get('description', '')}{lp}")

        if getattr(args, "verbose", False) and info_findings:
            info_non_limited = [f for f in info_findings if f["tier"] not in ("limited_risk",)]
            if info_non_limited:
                print(f"\n  INFO (verbose):")
                for f in info_non_limited:
                    score = f.get("confidence_score", 0)
                    lp = f" [{f.get('lifecycle_phases', ['develop'])[0]}]" if f.get("lifecycle_phases") else ""
                    print(f"    [INFO] [{score:3d}] {f['file']} — {f.get('description', '')}{lp}")

        # Open questions: low-confidence findings that need human judgment
        # suppressed findings already excluded by _is_open_question
        open_qs = [f for f in findings if f.get("open_question")]
        if open_qs:
            print(f"\n  Questions for human review ({len(open_qs)}):")
            for f in open_qs[:10]:
                print(f"    ? {f['file']}:{f.get('line', '?')} — {f.get('category', 'Unknown')}")
                print(f"      {f.get('description', '')} (confidence: {f.get('confidence_score', 0)}%)")
            if len(open_qs) > 10:
                print(f"    ... and {len(open_qs) - 10} more (use --format json to see all)")

        print(f"{'=' * 60}")
        print(f"  {t('confidence_note')}")
        print(f"  {t('tier_note')}")
        print(f"  {t('suppress_note')}")
        print()

        # === Next steps for the user ===
        print(f"\n  {'─' * 56}")
        print(f"  Next steps:")
        step_num = 1
        if prohibited:
            print(f"    {step_num}. regula fix --project .         Remove prohibited practices")
            step_num += 1
        if high_risk or limited:
            print(f"    {step_num}. regula gap --project .         See which articles you need to address")
            step_num += 1
            print(f"    {step_num}. regula roadmap --project .     Get a week-by-week compliance plan")
            step_num += 1
        if active:
            print(f"    {step_num}. regula evidence-pack --project . --bundle   Generate auditor-ready evidence")
            step_num += 1
        if not active:
            print(f"    {step_num}. regula gap --project .         Verify compliance documentation exists")
            step_num += 1
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
                    continue  # file unreadable; skip
                lang = _detect_lang(full_path.name) or "python"
                result = explain_classification(content, filepath=rel_path, language=lang)
                print(f"\n--- {rel_path} ---")
                print(format_explanation(result, filepath=rel_path))
                print()

    # GitHub Actions workflow-command annotations. Emits inline PR comments
    # without SARIF/CodeQL setup. Gated on GITHUB_ACTIONS=true + --ci so
    # local runs stay quiet. No-op in any other context.
    _emit_github_annotations(
        args,
        {"block": block_findings, "warn": warn_findings, "info": info_findings},
    )

    # Overdue risk acceptance warnings in CI (ISO 42001 Clause 8.2, AI Act 9(2))
    if os.environ.get("GITHUB_ACTIONS") and getattr(args, "ci", False):
        for f in accepted:
            rd = f.get("risk_decision", {})
            if rd.get("overdue"):
                fpath = f.get("file", "unknown")
                fline = f.get("line", 1)
                pat = rd.get("pattern", "unknown")
                rev = rd.get("review_date", "unknown")
                own = rd.get("owner", "unknown")
                print(f"::warning file={fpath},line={fline}"
                      f"::Accepted risk '{pat}' is overdue for review"
                      f" (was due {rev}, owner {own})")

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


def _print_suppression_audit(findings: list) -> None:
    """Print a table of all regula-ignore and regula-accept annotations."""
    decisions = [f for f in findings if f.get("risk_decision")]
    if not decisions:
        print("\nNo regula-ignore or regula-accept annotations found.")
        return

    print(f"\n{'Type':<8} {'File':<30} {'Line':>5}  {'Pattern':<20} {'Rationale':<35} {'Owner':<10} {'Review':<12} {'Status'}")
    print("-" * 135)
    for f in decisions:
        rd = f["risk_decision"]
        dtype = rd.get("dtype", rd.get("type", "?"))
        fpath = f.get("file", "?")
        if len(fpath) > 28:
            fpath = "..." + fpath[-25:]
        line = f.get("line", 0)
        pattern = rd.get("pattern", "?")[:18]
        rationale = (rd.get("rationale") or "\u2014")[:33]
        owner = rd.get("owner", "\u2014") if dtype == "accept" else "\u2014"
        review = rd.get("review_date", "\u2014") if dtype == "accept" else "\u2014"

        status = "OK"
        if rd.get("error"):
            status = "\u26a0 ERROR"
        elif rd.get("warning"):
            status = "\u26a0 NO RATIONALE"
        elif rd.get("overdue"):
            status = "\u26a0 OVERDUE"

        print(f"{dtype:<8} {fpath:<30} {line:>5}  {pattern:<20} {rationale:<35} {owner:<10} {review:<12} {status}")


def cmd_gdpr(args) -> None:
    """Scan for GDPR code patterns with dual-compliance hotspot detection."""
    from cli import json_output, _validate_path
    from gdpr_scan import scan_gdpr

    if args.project != ".":
        _validate_path(args.project)
    project_path = str(Path(args.project).resolve())
    scope = getattr(args, "scope", "all")

    result = scan_gdpr(project_path, scope=scope)

    if args.format == "json":
        json_output("gdpr", result)
        return

    findings = result["findings"]
    summary = result["summary"]

    if not findings:
        print(f"No GDPR-relevant patterns found in {project_path}")
        return

    print(f"\n  GDPR Code Pattern Scan — {project_path}\n")
    print(f"  {summary['total_findings']} finding(s): {summary['high_confidence']} high, "
          f"{summary['medium_confidence']} medium, {summary['low_confidence']} low confidence")

    if summary["dual_compliance_hotspot_files"] > 0:
        print(f"  {summary['dual_compliance_hotspot_files']} file(s) with dual-compliance hotspots "
              f"({summary['dual_compliance_findings']} finding(s), GDPR + EU AI Act)")

    print()
    for f in findings[:20]:
        prefix = "!" if f.get("dual_compliance") else " "
        arts = ", ".join(f"Art. {a}" for a in f["gdpr_articles"])
        print(f"  {prefix} {f['file']}:{f['line']} [{arts}] {f['description']}")
        if f.get("dual_compliance"):
            print(f"      Hotspot: {f.get('hotspot_description', '')}")

    if len(findings) > 20:
        print(f"\n  ... and {len(findings) - 20} more (use --format json to see all)")

    print(f"\n  All findings are indicators that GDPR obligations may apply — not violations.")
    print(f"  Consult a data protection specialist for compliance determination.\n")
