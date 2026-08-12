# regula-ignore — compliance command copy names articles and risk categories in help text and headings
"""Compliance commands for Regula CLI.

NOTE: Do NOT add 'from cli import ...' at module level.
cli.py imports this module at module level, creating a circular dependency.
All imports from cli must stay inside function bodies.
"""

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
    # Canonical skip set + shared path guard. constants.py states the
    # invariant explicitly: every scanner path must import THIS set and
    # never define its own ("six independently-drifted copies shipped
    # once"). This module had drifted — its inline set omitted 12 entries
    # including examples/, benchmarks/ and site-packages/, so `regula
    # comply` walked directories every other scanner skips.
    from constants import SKIP_DIRS
    from scan_safety import read_bytes_if_safe
    import re

    project = Path(project_path).resolve()
    checks = []

    # Gather all code content
    code_content = ""
    doc_content = ""
    _root_resolved = Path(project).resolve()
    for root, dirs, files in os.walk(project):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fn in files:
            fp = Path(root) / fn
            if fp.suffix.lower() in (".py", ".js", ".ts", ".java", ".go", ".rs"):
                _raw, _ = read_bytes_if_safe(fp, _root_resolved)
                if _raw is not None:
                    code_content += _raw.decode("utf-8", errors="ignore")
            elif fp.suffix.lower() in (".md", ".txt", ".html", ".yaml", ".yml"):
                _raw, _ = read_bytes_if_safe(fp, _root_resolved)
                if _raw is not None:
                    doc_content += _raw.decode("utf-8", errors="ignore")

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
    """Report evidence only for obligations resolved by the decision kernel."""
    from cli import json_output
    from compliance_check import assess_compliance

    project = str(Path(getattr(args, "project", ".")).resolve())
    # If --article specified, show deep-dive for that article
    article_filter = getattr(args, "article", None)
    articles = [article_filter] if article_filter else None

    assessment = assess_compliance(project, articles=articles)
    from decision_adapters import (
        empty_decision,
        format_decision_text,
        resolved_gap_evidence,
    )
    decision = empty_decision("eu", "cli:comply")
    evidence = resolved_gap_evidence(assessment, decision)

    if getattr(args, "format", "text") == "json":
        json_output("comply", {"decision": decision, "evidence": evidence})
        return

    print(format_decision_text(decision))
    print("\nEvidence scan:")
    print(evidence["note"])
    print(
        f"Article observations emitted: {len(evidence['article_observations'])}; "
        f"held pending applicability: {evidence['not_assessed_article_count']}"
    )


def cmd_compliance(args) -> None:
    """Manage compliance status of registered AI systems."""
    from cli import json_output
    from discover_ai_systems import update_compliance_status, load_registry, COMPLIANCE_TRANSITIONS

    if args.subcommand == "update":
        try:
            update_compliance_status(args.system, args.status, args.note or "")
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
                    note_suffix = f" — {h['note']}" if h.get("note") else ""
                    print(f"    {h['date'][:10]}: {h['from']} \u2192 {h['to']}{note_suffix}")
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
    # cannot verify from code (Art. 9 RMS, Art. 17 QMS, Art. 27 FRIA,
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
            print(f"Status: {result['summary']['document_status']}")
            print(
                "Note: this is an interim format under Article 11(1) second subparagraph. "
                "Replace with the official Commission SME template when published."
            )
        return

    from conform import generate_conformity_pack

    print(f"Generating conformity assessment evidence pack for {project_path}...", file=sys.stderr)

    # --sign and --signing-key both enable signing; --signing-key also
    # overrides the key location. --timestamp implies --sign (the
    # timestamp covers the signed canonical form per spec §4.6).
    # If an optional extra is missing, surface the Unavailable error
    # with an actionable install hint rather than a raw ImportError stack.
    timestamp_requested = bool(getattr(args, "timestamp", False))
    sign_requested = bool(
        getattr(args, "sign", False)
        or getattr(args, "signing_key", None)
        or timestamp_requested
    )
    signing_key_path = None
    if getattr(args, "signing_key", None):
        from pathlib import Path as _P
        signing_key_path = _P(args.signing_key).expanduser().resolve()
    tsa_url = getattr(args, "tsa_url", None)

    try:
        result = generate_conformity_pack(
            project_path,
            output_dir=args.output,
            project_name=project_name,
            model=args.model,
            endpoint=args.endpoint,
            sign=sign_requested,
            signing_key_path=signing_key_path,
            timestamp=timestamp_requested,
            tsa_url=tsa_url,
        )
    except ImportError as exc:
        # Malformed install where signing.py or timestamp.py is absent.
        print(
            f"Signing/timestamping unavailable: {exc}\n\n"
            f"Install the signing extra:\n"
            f"  pipx install \"regula-ai[signing]\"\n"
            f"  # or: pip install \"regula-ai[signing]\"",
            file=sys.stderr,
        )
        sys.exit(2)
    except Exception as exc:
        # SigningUnavailable, SigningError, TimestampUnavailable, or
        # TimestampError — show the message and exit 2. Avoid importing
        # signing/timestamp at module scope so the core CLI stays stdlib-
        # only when the optional extras are not installed.
        name = exc.__class__.__name__
        if name in (
            "SigningUnavailable", "SigningError",
            "TimestampUnavailable", "TimestampError",
        ):
            kind = "Timestamping" if name.startswith("Timestamp") else "Signing"
            print(f"{kind} failed: {exc}", file=sys.stderr)
            sys.exit(2)
        raise

    # Optional: emit a .regula.zip bundle alongside the pack directory
    # (Regula Evidence Format v1 §3.2). Bundles are portable across machines
    # and verifiable directly via `regula verify <bundle>.regula.zip`.
    bundle_path = None
    if getattr(args, "zip_bundle", False):
        import zipfile
        pack_dir = Path(result["pack_path"])
        bundle_path = pack_dir.parent / f"{pack_dir.name}.regula.zip"
        with zipfile.ZipFile(bundle_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for file_record in result["manifest"]["files"]:
                fname = file_record.get("filename") or file_record.get("path")
                if not fname:
                    continue
                src = pack_dir / fname
                if src.exists():
                    zf.write(src, arcname=f"{pack_dir.name}/{fname}")
            # include the manifest itself at the root of the pack dir
            zf.write(pack_dir / "manifest.json", arcname=f"{pack_dir.name}/manifest.json")
        result["bundle_path"] = str(bundle_path)

    if args.format == "json":
        json_output("conform", result)
    else:
        pack_path = result["pack_path"]
        file_count = len(result["manifest"]["files"])
        manifest = result["manifest"]
        fmt_version = manifest.get("format_version", "1.0")
        print(f"Conformity evidence pack written to: {pack_path}")
        print(f"Format: regula.evidence.v1 (format_version {fmt_version})")
        print(f"Contains {file_count} files with SHA-256 integrity hashes.")
        decision = result["summary"].get("decision", {})
        print(f"Decision: {decision.get('result_type', 'unresolved')}")
        print("No readiness percentage or article duty is emitted without resolved applicability.")
        if "signing" in manifest:
            print(f"Signed: Ed25519 signature embedded (verify with "
                  f"`regula verify {pack_path}`).")
        if "timestamp_authority" in manifest:
            ts = manifest["timestamp_authority"]
            print(f"Timestamped: RFC 3161 token from {ts.get('tsa_url', '?')} "
                  f"at {ts.get('gen_time', 'unknown')}.")
        if bundle_path is not None:
            print(f"Bundle written to:      {bundle_path}")
            print(f"Verify bundle with:     regula verify {bundle_path}")
        print(f"Start with: {pack_path}/00-assessment-summary.json")


def cmd_gap(args) -> None:
    """Compliance gap assessment."""
    from cli import json_output, _validate_path, _current_pattern_version

    if args.project != ".":
        _validate_path(args.project)
    from compliance_check import assess_compliance, format_gap_text
    from decision_adapters import empty_decision, format_decision_text, resolved_gap_evidence
    articles = [args.article] if args.article else None
    fw_arg = getattr(args, "framework", None)
    frameworks = [f.strip() for f in fw_arg.split(",")] if fw_arg else None
    assessment = assess_compliance(args.project, articles=articles, frameworks=frameworks)
    decision = empty_decision("eu", "cli:gap")
    evidence = resolved_gap_evidence(assessment, decision)
    # Stamp the pattern version so auditors can reproduce the assessment
    # against the exact same ruleset later (C3: --pattern-version).
    pv = getattr(args, "pattern_version", None)
    if pv:
        assessment["stamped_pattern_version"] = pv
    else:
        assessment["pattern_version"] = _current_pattern_version()
    # Compute the verdict exit code ONCE so json and text modes agree
    # (DEF-008 class: json_output("gap", ...) previously always hardcoded
    # envelope exit_code=0, contradicting the real process exit code under
    # --strict with a low overall_score).
    _gap_exit = 1 if (args.strict and decision["result_type"] != "indication") else 0
    if args.format == "json":
        json_output(
            "gap",
            {"decision": decision, "evidence": evidence},
            exit_code=_gap_exit,
        )
    else:
        print(format_decision_text(decision))
        print("\nEvidence scan:")
        print(evidence["note"])
        print(
            f"Article observations emitted: {len(evidence['article_observations'])}; "
            f"held pending applicability: {evidence['not_assessed_article_count']}"
        )
        if pv:
            print(f"\n[stamped against pattern version: {pv}]")
    if _gap_exit:
        sys.exit(_gap_exit)


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
    # Compute the verdict exit code ONCE so json and text modes agree
    # (DEF-008 class: json_output("gpai-check", ...) previously always
    # hardcoded envelope exit_code=0, contradicting the real process exit
    # code under --strict with a FAIL present).
    _gpai_exit = 1 if (getattr(args, "strict", False) and result["summary"].get("FAIL", 0) > 0) else 0
    if args.format == "json":
        json_output("gpai-check", result, exit_code=_gpai_exit)
    else:
        print(format_gpai_check_text(result))
    if _gpai_exit:
        sys.exit(_gpai_exit)


def cmd_plan(args) -> None:
    """Emit a plan only after the kernel resolves applicable obligations."""
    from cli import json_output, _validate_path

    if args.project != ".":
        _validate_path(args.project)
    project_path = str(Path(args.project).resolve())
    from decision_adapters import empty_decision, format_decision_text
    from remediation_plan import mark_task_done

    if args.done:
        status = mark_task_done(project_path, args.done)
        print(f"Marked {args.done} as completed.")
        return

    if args.status:
        print("Existing plan status cannot be interpreted until applicability is resolved.")

    decision = empty_decision("eu", "cli:plan")
    if args.format == "json":
        json_output("plan", {"decision": decision, "plan": None})
    else:
        print(format_decision_text(decision))
        print("\nNo obligation plan or effort estimate was emitted because applicability is unresolved.")


def cmd_assess(args) -> None:
    """AI regulation applicability check -- no code required."""
    from assess import run_assess
    output_format = getattr(args, "format", "text")
    answers = getattr(args, "answers", None)
    jurisdiction = getattr(args, "jurisdiction", "eu")

    # Korea and Colorado assessments are web-only for now
    if jurisdiction != "eu":
        jur_urls = {"korea": "?j=kr", "colorado": "?j=co"}
        url_param = jur_urls.get(jurisdiction, "")
        print(
            f"The {jurisdiction} assessment is available via the web tool:\n"
            f"  https://getregula.com/assess/{url_param}\n\n"
            f"The CLI assess command currently supports EU AI Act only.\n"
            f"For CLI multi-jurisdiction scanning, use:\n"
            f"  regula check . --jurisdictions {jurisdiction}",
            file=sys.stderr,
        )
        sys.exit(0)

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


def cmd_roadmap(args) -> None:
    """Emit a roadmap only after the kernel resolves applicable obligations."""
    from cli import json_output, _validate_path
    from decision_adapters import empty_decision, format_decision_text

    if args.project != ".":
        _validate_path(args.project)
    decision = empty_decision("eu", "cli:roadmap")

    if args.format == "json":
        json_output("roadmap", {"decision": decision, "roadmap": None})
    else:
        print(format_decision_text(decision))
        print("\nNo deadline, obligation roadmap, or effort estimate was emitted because applicability is unresolved.")
