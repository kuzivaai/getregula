# regula-ignore
"""Compliance commands for Regula CLI.

NOTE: Do NOT add 'from cli import ...' at module level.
cli.py imports this module at module level, creating a circular dependency.
All imports from cli must stay inside function bodies.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


def _check_article_50(project_path: str) -> list:
    """Check Article 50 transparency obligations for limited-risk systems.

    Returns a list of dicts with check name, status, and detail.
    Based on EU AI Act Article 50(1)-(5), verified against the
    EC AI Act Service Desk (ai-act-service-desk.ec.europa.eu).
    """
    import os
    import re

    project = Path(project_path).resolve()
    checks = []

    # Gather all code content
    code_content = ""
    doc_content = ""
    for root, dirs, files in os.walk(project):
        dirs[:] = [d for d in dirs if d not in {
            ".git", "__pycache__", "node_modules", ".venv", "venv",
            ".tox", ".mypy_cache", "dist", "build", ".egg-info",
        }]
        for fn in files:
            fp = Path(root) / fn
            if fp.suffix.lower() in (".py", ".js", ".ts", ".java", ".go", ".rs"):
                try:
                    code_content += fp.read_text(encoding="utf-8", errors="ignore")
                except (PermissionError, OSError):
                    pass
            elif fp.suffix.lower() in (".md", ".txt", ".html", ".yaml", ".yml"):
                try:
                    doc_content += fp.read_text(encoding="utf-8", errors="ignore")
                except (PermissionError, OSError):
                    pass

    all_content = (code_content + doc_content).lower()

    # Art 50(1): AI interaction disclosure
    ai_disclosure_patterns = [
        r"ai.?disclos", r"ai.?system.?notice", r"interacting.?with.?ai",
        r"powered.?by.?ai", r"ai.?generated", r"this.?is.?an?.?ai",
        r"automated.?system", r"bot.?disclosure", r"ai.?transparency",
    ]
    has_disclosure = any(re.search(p, all_content) for p in ai_disclosure_patterns)
    checks.append({
        "article": "50(1)",
        "title": "AI interaction disclosure",
        "obligation": "Users must be informed they are interacting with an AI system",
        "status": "found" if has_disclosure else "not_found",
    })

    # Art 50(2): Synthetic content marking
    marking_patterns = [
        r"content.?mark", r"watermark", r"c2pa", r"content.?credentials",
        r"synthetic.?label", r"ai.?generated.?mark", r"provenance",
        r"content.?authenticity", r"machine.?readable.?mark",
    ]
    has_marking = any(re.search(p, all_content) for p in marking_patterns)
    checks.append({
        "article": "50(2)",
        "title": "Synthetic content marking",
        "obligation": "AI-generated content must be marked in machine-readable format",
        "status": "found" if has_marking else "not_found",
    })

    # Art 50(3): Emotion recognition / biometric notice
    emotion_patterns = [
        r"emotion.?recogn", r"sentiment.?analy", r"affect.?detect",
        r"biometric.?categori", r"age.?estimat", r"gender.?detect",
    ]
    has_emotion_system = any(re.search(p, code_content.lower()) for p in emotion_patterns)
    if has_emotion_system:
        inform_patterns = [
            r"inform.{0,30}(emotion|biometric|categori)",
            r"(emotion|biometric).{0,30}(notice|disclos|consent|inform)",
        ]
        has_inform = any(re.search(p, all_content) for p in inform_patterns)
        checks.append({
            "article": "50(3)",
            "title": "Emotion/biometric system notice",
            "obligation": "Persons exposed must be informed of system operation",
            "status": "found" if has_inform else "not_found",
        })

    # Art 50(4): Deep fake / synthetic media disclosure
    deepfake_patterns = [
        r"deepfake", r"face.?swap", r"voice.?clon",
        r"synthetic.?media", r"image.?generat",
    ]
    has_deepfake = any(re.search(p, code_content.lower()) for p in deepfake_patterns)
    if has_deepfake:
        disclosure_patterns = [
            r"(deepfake|synthetic|generated).{0,30}(disclos|label|notice|warn)",
            r"(disclos|label|notice).{0,30}(deepfake|synthetic|generated)",
        ]
        has_df_disclosure = any(re.search(p, all_content) for p in disclosure_patterns)
        checks.append({
            "article": "50(4)",
            "title": "Deep fake / synthetic media disclosure",
            "obligation": "Content must be disclosed as artificially generated or manipulated",
            "status": "found" if has_df_disclosure else "not_found",
        })

    return checks


def cmd_comply(args) -> None:
    """EU AI Act obligation checklist with status.

    Scopes obligations to the detected risk tier:
    - High-risk/prohibited: Articles 9-15 + Article 50 (where applicable)
    - Limited-risk: Article 50 transparency obligations only
    - Minimal-risk: No mandatory requirements
    Use --all to show the full Articles 9-15 assessment regardless of tier.
    """
    from cli import json_output, _is_tty
    from compliance_check import assess_compliance, ARTICLE_TITLES

    project = str(Path(getattr(args, "project", ".")).resolve())
    project_name = Path(project).name
    show_all = getattr(args, "all", False)

    # If --article specified, show deep-dive for that article
    article_filter = getattr(args, "article", None)
    articles = [article_filter] if article_filter else None

    assessment = assess_compliance(project, articles=articles)
    highest_risk = assessment.get("highest_risk", "unknown")

    if getattr(args, "format", "text") == "json":
        # Enrich JSON with Article 50 checks and tier scoping
        assessment["article_50_checks"] = _check_article_50(project)
        assessment["scoped_to_tier"] = highest_risk
        json_output("comply", assessment)
        return

    # Status symbols and labels
    _STATUS = {
        "strong": ("\u2713", "PASS"),
        "moderate": ("~", "PARTIAL"),
        "partial": ("\u2717", "NEEDS WORK"),
        "not_found": ("\u2717", "NOT FOUND"),
    }

    print(f"\nEU AI Act Compliance Checklist: {project_name}")
    print(f"{'=' * 60}")

    # --- MINIMAL RISK ---
    if highest_risk in ("minimal_risk", "not_ai") and not show_all:
        print(f"  Highest risk tier: {highest_risk}")
        print(f"\n  No mandatory EU AI Act requirements apply to minimal-risk")
        print(f"  or non-AI systems. Voluntary codes of conduct may apply")
        print(f"  (Article 95).")
        print(f"\n{'=' * 60}")
        print(f"\n  Next steps:")
        print(f"    1. regula assess{'':<25s}Verify this classification with guided questions")
        print(f"    2. regula comply --all{'':<19s}Show full Articles 9-15 assessment anyway")
        print()
        return

    # --- LIMITED RISK ---
    if highest_risk == "limited_risk" and not show_all:
        print(f"  Highest risk tier: limited_risk")
        print(f"  Applicable:        Article 50 (Transparency)")
        print()

        art50_checks = _check_article_50(project)
        pass_count = sum(1 for c in art50_checks if c["status"] == "found")
        total = len(art50_checks)

        for c in art50_checks:
            symbol = "\u2713" if c["status"] == "found" else "\u2717"
            label = "FOUND" if c["status"] == "found" else "NOT FOUND"
            print(f"  [{symbol}] Art. {c['article']:<6s} {c['title']:<35s} {label}")
            print(f"          {c['obligation']}")

        print(f"\n{'=' * 60}")
        print(f"  {pass_count}/{total} transparency obligations have evidence")
        if pass_count < total:
            print(f"  {total - pass_count} obligation(s) need attention")

        print(f"\n  Note: Articles 9-15 do NOT apply to limited-risk systems.")
        print(f"  They apply only to high-risk systems (Annex III / Article 6).")

        if _is_tty():
            print(f"\n  Next steps:")
            print(f"    1. regula check .{'':<24s}See detailed scan findings")
            print(f"    2. regula comply --all{'':<19s}Show Articles 9-15 assessment (informational)")
            print(f"    3. regula assess{'':<25s}Verify risk tier with guided questions")
        print()
        return

    # --- HIGH RISK / PROHIBITED (or --all) ---
    tier_label = highest_risk
    if show_all and highest_risk in ("limited_risk", "minimal_risk", "not_ai"):
        tier_label = f"{highest_risk} (showing all articles per --all flag)"

    print(f"  Overall compliance score: {assessment['overall_score']}/100")
    print(f"  Highest risk tier:        {tier_label}")
    print()

    # Articles 9-15 checklist
    pass_count = 0
    needs_work = []
    for article_num in sorted(assessment["articles"].keys(), key=int):
        result = assessment["articles"][article_num]
        status = result["status"]
        symbol, label = _STATUS.get(status, ("?", status.upper()))
        score = result["score"]

        if status == "strong":
            pass_count += 1
        else:
            needs_work.append(article_num)

        print(f"  [{symbol}] Article {article_num:<3s} {result['title']:<35s} {score:>3d}% {label}")

        # Deep-dive mode: show evidence and gaps for requested article
        if article_filter:
            if result["evidence"]:
                print(f"      Evidence found:")
                for ev in result["evidence"]:
                    print(f"        \u2713 {ev}")
            if result["gaps"]:
                print(f"      Gaps to address:")
                for gap in result["gaps"]:
                    print(f"        \u2717 {gap}")
            print()

    # Also show Article 50 checks for high-risk (they apply alongside Art 9-15)
    art50_checks = _check_article_50(project)
    if art50_checks:
        print()
        for c in art50_checks:
            symbol = "\u2713" if c["status"] == "found" else "\u2717"
            label = "FOUND" if c["status"] == "found" else "NOT FOUND"
            print(f"  [{symbol}] Art. {c['article']:<6s} {c['title']:<35s} {label}")

    total = len(assessment["articles"])
    print(f"\n{'=' * 60}")
    print(f"  {pass_count}/{total} high-risk obligations have strong evidence")

    if needs_work and not article_filter:
        print(f"  {len(needs_work)} obligation(s) need attention: Articles {', '.join(needs_work)}")

    if show_all and highest_risk not in ("high_risk", "prohibited"):
        print(f"\n  Note: This project is classified as {highest_risk}.")
        print(f"  Articles 9-15 are shown for informational purposes (--all flag).")
        print(f"  They are legally required only for high-risk systems.")

    # Contextual next steps
    if _is_tty():
        steps = []
        if needs_work and not article_filter:
            weakest = min(needs_work, key=lambda a: assessment["articles"][a]["score"])
            steps.append(
                f"regula comply --article {weakest}{'':<20s}Deep-dive into Article {weakest} ({ARTICLE_TITLES.get(weakest, '')})"
            )
        if assessment["overall_score"] < 80:
            steps.append(
                f"regula plan --project .{'':<22s}Prioritised remediation plan"
            )
        if assessment["overall_score"] >= 50:
            steps.append(
                f"regula evidence-pack --project .{'':<13s}Generate auditor-ready evidence"
            )
        if highest_risk in ("high_risk", "prohibited"):
            steps.append(
                f"regula conform --project .{'':<19s}Generate conformity assessment evidence"
            )
        if not steps:
            steps.append(
                f"regula evidence-pack --project .{'':<13s}Generate auditor-ready evidence"
            )

        print(f"\n  Next steps:")
        for i, step in enumerate(steps[:4], 1):
            print(f"    {i}. {step}")
    print()


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

    # Interactive mode requires a TTY
    if not answers and not (hasattr(sys.stdin, 'isatty') and sys.stdin.isatty()):
        print(
            "Error: `regula assess` requires an interactive terminal,\n"
            "or pass --answers as a comma-separated list of yes/no values in order:\n"
            "  uses_ai,eu_users,prohibited,high_risk_domain,non_eu_provider|transparency_trigger\n"
            "Or use `regula questionnaire` for the richer non-interactive flow.",
            file=sys.stderr,
        )
        sys.exit(2)

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
