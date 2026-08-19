# regula-ignore — compliance command copy names articles and risk categories in help text and headings
"""Compliance commands for Regula CLI.

NOTE: Do NOT add 'from cli import ...' at module level.
cli.py imports this module at module level, creating a circular dependency.
All imports from cli must stay inside function bodies.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


def cmd_comply(args) -> None:
    """Report evidence only for obligations resolved by the decision kernel."""
    from cli import json_output
    from compliance_check import ARTICLE_NUMBERS, assess_compliance
    from cli_scan import _declared_facts, _print_fact_catalogue

    if getattr(args, "list_facts", False):
        _print_fact_catalogue(command="comply")
        return

    project = str(Path(getattr(args, "project", ".")).resolve())
    # If --article specified, show deep-dive for that article
    article_filter = getattr(args, "article", None)
    articles = [article_filter] if article_filter else None

    from decision_adapters import empty_decision, evaluate_payload, format_decision_text
    declared_facts, fact_notices = _declared_facts(
        args, project, "eu", source_ref="cli:comply --fact"
    )
    decision = (
        evaluate_payload({"jurisdiction": "eu", "facts": declared_facts})
        if declared_facts else empty_decision("eu", "cli:comply")
    )

    if article_filter == "50":
        from article50_evidence import format_article50_text, scan_article50
        resolved_declared_fact_ids = set()
        for fact_id, entry in declared_facts.items():
            decisive_states = {
                value.get("state") for value in entry.get("values", [])
                if value.get("state") != "unknown"
            }
            if len(decisive_states) == 1:
                resolved_declared_fact_ids.add(fact_id)
        observations = scan_article50(
            project, resolved_fact_ids=resolved_declared_fact_ids
        )
        scope_trace = next(
            (trace for trace in decision.get("decision_trace", [])
             if trace.get("predicate_id") == "eu_scope"),
            None,
        )
        article50_traces = [
            trace for trace in decision.get("decision_trace", [])
            if trace.get("predicate_id", "").startswith("eu_transparency_")
        ]
        article50_obligations = [
            obligation for obligation in decision.get("obligations", [])
            if "Article 50(" in obligation.get("provision", "")
        ]
        resolved_outside_scope = bool(
            scope_trace and scope_trace.get("state") == "false"
        )
        all_paths_resolved = (
            scope_trace is not None
            and scope_trace.get("state") == "true"
            and len(article50_traces) == 5
            and all(trace.get("state") != "unresolved"
                    for trace in article50_traces)
        )
        applicability_resolution = (
            "resolved_applicable" if article50_obligations
            else "resolved_not_applicable"
            if resolved_outside_scope or all_paths_resolved
            else "unresolved"
        )
        evidence = {
            "project_path": project,
            "article_observations": {},
            "not_assessed_article_count": (
                1 if applicability_resolution == "unresolved" else 0
            ),
            "applicability_resolution": applicability_resolution,
            "resolved_article50_obligations": article50_obligations,
            "technical_observations": {"50": observations},
            "note": (
                "Article 50 applicability is evaluated only from declared "
                "facts. Static trigger and control signals remain separate "
                "review leads and are not treated as legal facts or a "
                "compliance score."
            ),
        }
        if getattr(args, "format", "text") == "json":
            json_output("comply", {
                "decision": decision,
                "declared_facts": declared_facts,
                "declared_facts_notices": fact_notices,
                "evidence": evidence,
            })
            return
        print(format_decision_text(decision, command="comply"))
        if declared_facts:
            import fact_store as fs
            print(f"\nDeclared facts: {len(declared_facts)} "
                  "(asserted by a person, not established by Regula)")
            for line in fs.describe(declared_facts):
                print(line)
        for notice in fact_notices:
            print(f"  INFO: {notice}", file=sys.stderr)
        print()
        print(format_article50_text(observations))
        return

    if article_filter and article_filter not in ARTICLE_NUMBERS:
        valid = ", ".join(ARTICLE_NUMBERS + ["50"])
        print(
            f"Error: unsupported article {article_filter!r}. "
            f"Supported article filters: {valid}.",
            file=sys.stderr,
        )
        raise SystemExit(2)

    assessment = assess_compliance(project, articles=articles)
    from decision_adapters import (
        resolved_gap_evidence,
    )
    evidence = resolved_gap_evidence(assessment, decision)

    if getattr(args, "format", "text") == "json":
        json_output("comply", {
            "decision": decision,
            "declared_facts": declared_facts,
            "declared_facts_notices": fact_notices,
            "evidence": evidence,
        })
        return

    print(format_decision_text(decision, command="comply"))
    if declared_facts:
        import fact_store as fs
        print(f"\nDeclared facts: {len(declared_facts)} "
              "(asserted by a person, not established by Regula)")
        for line in fs.describe(declared_facts):
            print(line)
    for notice in fact_notices:
        print(f"  INFO: {notice}", file=sys.stderr)
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
        # These are labels YOU set on your own systems in your own registry.
        # Regula never sets one: a discovered system is always recorded as
        # not_started and an existing value is preserved untouched. The heading
        # read "Regula Compliance Status Workflow", which presented the states
        # as Regula's, and made `compliant` read as an end-state Regula awards
        # for using it. The owner ruled on 2026-08-17 to keep the stored values,
        # so no registry migrates, and to correct the framing here instead.
        # LEDGER N125.
        print("\n  Self-recorded compliance status: the labels you can set")
        print("  " + "=" * 50)
        print("  not_started \u2192 assessment \u2192 implementing \u2192 compliant \u2192 review_due")
        print("  These record YOUR assessment of your own system. Regula does")
        print("  not set, check or endorse any of them, and setting `compliant`")
        print("  is your declaration, not a determination by this tool.")
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
    from compliance_check import assess_compliance
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
    from errors import UsageError

    if args.project != ".":
        _validate_path(args.project)
    from decision_adapters import empty_decision, format_decision_text

    # This command emits no plan: `empty_decision` is unconditional, so
    # applicability never resolves here and the task list is always absent.
    # `--done` therefore has no task it could refer to, whatever id is given.
    # It used to write `{"<id>": "completed"}` into `.regula/plan-status.json`
    # and print success for any string at all, which manufactured an evidence
    # record with no referent. Refusing is the accurate answer, and it matches
    # what `--status` already says.
    if args.done:
        raise UsageError(
            "Cannot mark a task complete: this command emits no plan while "
            "applicability is unresolved, so there is no task list to mark "
            "against. Nothing was written."
        )

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

    sys.exit(run_assess(output_format, answers=answers,
                        save_facts=getattr(args, "save_facts", None)))


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
