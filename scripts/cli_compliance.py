"""Compliance commands for Regula CLI.

NOTE: Do NOT add 'from cli import ...' at module level.
cli.py imports this module at module level, creating a circular dependency.
All imports from cli must stay inside function bodies.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


def cmd_compliance(args) -> None:
    """Manage compliance status of registered AI systems."""
    from cli import json_output
    from discover_ai_systems import update_compliance_status, load_registry, COMPLIANCE_TRANSITIONS

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
                    print(f"    {h['date'][:10]}: {h['from']} \u2192 {h['to']}{' \u2014 ' + h['note'] if h.get('note') else ''}")
            print()

    elif args.subcommand == "workflow":
        print("\n  Regula Compliance Status Workflow")
        print("  " + "=" * 50)
        print("  not_started \u2192 assessment \u2192 implementing \u2192 compliant \u2192 review_due")
        print()
        for status, transitions in COMPLIANCE_TRANSITIONS.items():
            print(f"    {status:<20} \u2192 {', '.join(transitions)}")
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


def cmd_conform(args) -> None:
    """Generate conformity assessment evidence pack."""
    from cli import json_output, _validate_path

    # F1: --organisational — questionnaire mode for the articles Regula
    # cannot verify from code (Art. 9 RMS, Art. 17 QMS, Art. 29a FRIA,
    # Art. 72 PMM). This does NOT scan code — it asks structured yes/no
    # questions and produces an evidence document from the answers.
    if getattr(args, "organisational", False):
        from cli import _run_organisational_questionnaire
        _run_organisational_questionnaire(args)
        return

    if args.project != ".":
        _validate_path(args.project)
    project_path = str(Path(args.project).resolve())
    project_name = args.name or Path(project_path).name

    if getattr(args, "sme", False):
        from conform import generate_sme_simplified_pack
        print(
            f"Generating SME-simplified Annex IV (Article 11(1) interim form) for {project_path}...",
            file=sys.stderr,
        )
        result = generate_sme_simplified_pack(
            project_path,
            output_dir=args.output,
            project_name=project_name,
        )
        if args.format == "json":
            json_output("conform", result)
        else:
            print(f"Simplified Annex IV written to: {result['pack_path']}")
            print(f"Form: {result['summary']['form']}")
            print(f"Status: {result['summary']['overall_readiness']}")
            print(
                "Note: this is an interim format under Article 11(1) second subparagraph. "
                "Replace with the official Commission SME template when published."
            )
        return

    from conform import generate_conformity_pack

    print(f"Generating conformity assessment evidence pack for {project_path}...", file=sys.stderr)
    result = generate_conformity_pack(
        project_path,
        output_dir=args.output,
        project_name=project_name,
        model=args.model,
        endpoint=args.endpoint,
    )

    if args.format == "json":
        json_output("conform", result)
    else:
        pack_path = result["pack_path"]
        file_count = len(result["manifest"]["files"])
        readiness = result["summary"]["overall_readiness"]
        print(f"Conformity evidence pack written to: {pack_path}")
        print(f"Contains {file_count} files with SHA-256 integrity hashes.")
        print(f"Overall readiness: {readiness}")
        print(f"Start with: {pack_path}/00-assessment-summary.json")


def cmd_gap(args) -> None:
    """Compliance gap assessment."""
    from cli import json_output, _validate_path, _current_pattern_version

    if args.project != ".":
        _validate_path(args.project)
    from compliance_check import assess_compliance, format_gap_text
    articles = [args.article] if args.article else None
    fw_arg = getattr(args, "framework", None)
    frameworks = [f.strip() for f in fw_arg.split(",")] if fw_arg else None
    assessment = assess_compliance(args.project, articles=articles, frameworks=frameworks)
    # Stamp the pattern version so auditors can reproduce the assessment
    # against the exact same ruleset later (C3: --pattern-version).
    pv = getattr(args, "pattern_version", None)
    if pv:
        assessment["stamped_pattern_version"] = pv
    else:
        assessment["pattern_version"] = _current_pattern_version()
    if args.format == "json":
        json_output("gap", assessment)
    else:
        print(format_gap_text(assessment))
        if pv:
            print(f"\n[stamped against pattern version: {pv}]")
    # Exit 1 if overall score < 50 and --strict
    if args.strict and assessment.get("overall_score", 0) < 50:
        sys.exit(1)


def cmd_exempt(args) -> None:
    """Article 6(3) self-assessment decision tree."""
    from exempt_check import run_exempt, parse_answers_csv
    answers = None
    if getattr(args, "answers", None):
        answers = parse_answers_csv(args.answers)
        if answers is None:
            print(
                "Error: --answers must be six comma-separated yes/no values in order:\n"
                "  annex_iii,profiling,narrow_procedural,improve_human,detect_patterns,preparatory",
                file=sys.stderr,
            )
            sys.exit(2)
    sys.exit(run_exempt(output_format=args.format, answers=answers))


def cmd_gpai_check(args) -> None:
    """GPAI Code of Practice check (Chapters 1-3)."""
    from cli import json_output, _validate_path

    if args.path != ".":
        _validate_path(args.path)
    from gpai_check import run_gpai_check, format_gpai_check_text
    result = run_gpai_check(args.path, systemic_risk=getattr(args, "systemic_risk", False))
    if args.format == "json":
        json_output("gpai-check", result)
    else:
        print(format_gpai_check_text(result))
    # Exit code: 1 only if --strict and there is at least one FAIL.
    if getattr(args, "strict", False) and result["summary"].get("FAIL", 0) > 0:
        sys.exit(1)


def cmd_plan(args) -> None:
    """Generate prioritised remediation plan."""
    from cli import json_output, _validate_path

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


def cmd_assess(args) -> None:
    """EU AI Act applicability check -- no code required."""
    from assess import run_assess
    output_format = getattr(args, "format", "text")
    answers = getattr(args, "answers", None)
    sys.exit(run_assess(output_format, answers=answers))


def cmd_baseline(args) -> None:
    """CI/CD baseline comparison."""
    from cli import json_output

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
