"""Utility commands for Regula CLI.

NOTE: Do NOT add 'from cli import ...' at module level.
cli.py imports this module at module level, creating a circular dependency.
All imports from cli must stay inside function bodies.
"""

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


def cmd_doctor(args) -> None:
    """Check installation health."""
    from cli import json_output
    from doctor import run_doctor
    result = run_doctor(format_type=args.format)
    if args.format == "json":
        json_output("doctor", result, exit_code=0 if result["healthy"] else 1)
        sys.exit(0 if result["healthy"] else 1)
    else:
        sys.exit(0 if result else 1)


def cmd_self_test(args) -> None:
    """Run built-in self-test assertions."""
    from self_test import run_self_test
    ok = run_self_test()
    sys.exit(0 if ok else 1)


def cmd_config(args) -> None:
    """Config management commands."""
    from cli import json_output
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


def cmd_install(args) -> None:
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


def cmd_quickstart(args) -> None:
    """60-second onboarding."""
    from cli import json_output
    from quickstart import run_quickstart
    result = run_quickstart(
        project_dir=args.project,
        org=getattr(args, "org", "My Organisation"),
        format_type=args.format,
    )
    if args.format == "json":
        json_output("quickstart", result)
    sys.exit(0)


def cmd_init(args) -> None:
    """Guided setup wizard."""
    from init_wizard import run_init
    run_init(Path(args.project).resolve(), interactive=args.interactive,
             dry_run=getattr(args, 'dry_run', False))


def cmd_fix(args) -> None:
    """Generate compliance fix scaffolds for findings."""
    from cli import json_output, _validate_path

    if args.project != ".":
        _validate_path(args.project)
    project_path = str(Path(args.project).resolve())

    from report import scan_files
    from remediation import get_remediation, remediate_observation

    print(f"Scanning {project_path}...", file=sys.stderr)
    findings = scan_files(project_path)

    # Filter to actionable findings across all significant tiers
    actionable_tiers = {"high_risk", "prohibited", "ai_security", "credential_exposure"}
    actionable = [
        f for f in findings
        if f.get("tier") in actionable_tiers and not f.get("suppressed")
    ]

    if not actionable:
        if args.format == "json":
            json_output("fix", {"fixes": [], "message": "No actionable findings."})
        else:
            print("No actionable findings to fix.")
        return

    fixes = []
    seen_obs_keys = set()  # deduplicate observation-based fixes per file
    for finding in actionable:
        rem = get_remediation(
            finding.get("tier", ""),
            finding.get("category", ""),
            finding.get("indicators", []),
            finding.get("file", ""),
            finding.get("description", ""),
        )
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

        # Process governance observations attached to high-risk findings
        for obs in finding.get("observations", []):
            obs_text = obs.get("observation", "")
            obs_key = None
            if "no logging" in obs_text.lower() or "article 12" in obs_text.lower():
                obs_key = "no_logging"
            elif "fairness evaluation" in obs_text.lower():
                obs_key = "missing_fairness_evaluation"
            elif "automated decision" in obs_text.lower() or "article 13" in obs_text.lower():
                obs_key = "automated_decision"

            dedup = (finding.get("file", "?"), obs_key)
            if obs_key and dedup not in seen_obs_keys:
                seen_obs_keys.add(dedup)
                obs_rem = remediate_observation(obs_key)
                if obs_rem:
                    fixes.append({
                        "file": finding.get("file", "?"),
                        "line": finding.get("line", "?"),
                        "tier": "governance_observation",
                        "category": obs_key,
                        "summary": obs_rem["summary"],
                        "article": obs_rem["article"],
                        "explanation": obs_rem["explanation"],
                        "fix_code": obs_rem.get("fix_code", ""),
                    })

    if args.format == "json":
        json_output("fix", {"fixes": fixes, "total": len(fixes)})
    else:
        print(f"# Compliance Fixes \u2014 {len(fixes)} actionable findings\n")
        seen_categories = set()
        for fix in fixes:
            cat = fix["category"]
            if cat in seen_categories:
                continue
            seen_categories.add(cat)

            print(f"## {fix['file']}:{fix['line']} \u2014 {fix['tier'].upper().replace('_', '-')}")
            print(f"   Category: {fix['category']}")
            print(f"   Article: {fix['article']}")
            print(f"   {fix['summary']}")
            print(f"   {fix['explanation']}")
            if fix["fix_code"]:
                print(f"\n   Suggested code scaffold:")
                print(f"   {'\u2500' * 40}")
                for code_line in fix["fix_code"].replace("\\n", "\n").split("\n"):
                    print(f"   {code_line}")
                print(f"   {'\u2500' * 40}")
            print()

        if args.output:
            out_path = Path(args.output)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            lines = []
            for fix in fixes:
                cat = fix["category"]
                lines.append(f"# {fix['file']}:{fix['line']} \u2014 {fix['article']}")
                lines.append(f"# {fix['summary']}")
                if fix["fix_code"]:
                    lines.append(fix["fix_code"].replace("\\n", "\n"))
                lines.append("")
            out_path.write_text("\n".join(lines), encoding="utf-8")
            print(f"Fix scaffolds written to {out_path}", file=sys.stderr)


def cmd_explain_article(args) -> None:
    """Explain an EU AI Act article in plain language."""
    from cli import json_output
    from explain_articles import ARTICLES

    article_num = args.article.lstrip("article").lstrip("art").lstrip(".").lstrip(" ")

    if article_num not in ARTICLES:
        available = ", ".join(sorted(ARTICLES.keys(), key=lambda x: int(x)))
        print(f"Article {article_num} not found. Available: {available}")
        return

    a = ARTICLES[article_num]

    if args.format == "json":
        json_output("explain-article", {"article": article_num, **a})
        return

    print(f"\n  Article {article_num} \u2014 {a['title']}")
    print(f"  {'=' * (len(a['title']) + len(article_num) + 14)}\n")
    print(f"  {a['summary']}\n")
    print(f"  Who:   {a['who']}")
    print(f"  When:  {a['when']}\n")
    print(f"  What Regula checks:")
    print(f"  {a['what_regula_checks']}\n")


def cmd_deps(args) -> None:
    """Dependency supply chain analysis."""
    from cli import json_output, _validate_path

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


def cmd_timeline(args) -> None:
    """EU AI Act enforcement timeline."""
    from cli import json_output
    from timeline import format_timeline_text, TIMELINE
    if args.format == "json":
        from datetime import date
        json_output("timeline", {"as_of": date.today().isoformat(), "timeline": TIMELINE})
    else:
        print(format_timeline_text())


def cmd_regwatch(args) -> None:
    """Warn when pattern ruleset is older than latest regulatory change."""
    from cli import json_output
    from regwatch import run as _regwatch_run
    result = _regwatch_run(getattr(args, "format", "text"))
    fmt = getattr(args, "format", "text")
    if fmt == "json":
        json_output("regwatch", result)
    else:
        status = result.get("status", "unknown")
        icon = {"up-to-date": "PASS", "stale": "WARN",
                "warn": "INFO", "error": "FAIL"}.get(status, "?")
        print(f"regwatch [{icon}]: {result.get('message', '')}")
    sys.exit(int(result.get("exit_code", 0)))


def cmd_feed(args) -> None:
    """Fetch AI governance news feed."""
    from cli import _build_envelope
    from feed import fetch_governance_news, format_text, format_html, FEED_SOURCES
    if args.sources:
        print("\nRegula Governance Feed \u2014 Curated Sources\n")
        for s in FEED_SOURCES:
            print(f"  {s['name']}")
            print(f"    Authority: {s['authority']}")
            print()
        return
    articles = fetch_governance_news(days=args.days, use_cache=not args.no_cache)
    if args.format == "json":
        content = json.dumps(_build_envelope("feed", articles), indent=2, default=str)
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


def cmd_bias(args) -> None:
    """Evaluate model stereotype bias using multiple benchmarks."""
    from cli import json_output
    from bias_eval import load_crowspairs_sample, evaluate_with_ollama
    from bias_bbq import load_bbq_sample, evaluate_bbq_full
    from bias_report import format_text_report, format_json_report, format_annex_iv

    benchmark = getattr(args, "benchmark", "all")
    method = getattr(args, "method", "auto")
    method_arg = None if method == "auto" else method
    seed = getattr(args, "seed", None)
    confidence_n = getattr(args, "confidence", 1000)
    fmt = getattr(args, "format", "text")

    crowspairs_result = None
    bbq_result = None

    if benchmark in ("all", "crowspairs"):
        pairs = load_crowspairs_sample(csv_path=getattr(args, "csv", None), max_pairs=args.sample)
        print(f"CrowS-Pairs: loaded {len(pairs)} pairs. Evaluating with {args.model}...", file=sys.stderr)
        crowspairs_result = evaluate_with_ollama(
            pairs, model=args.model, endpoint=args.endpoint,
            method=method_arg, seed=seed, bootstrap_resamples=confidence_n,
        )

    if benchmark in ("all", "bbq"):
        items = load_bbq_sample(max_items=args.sample)
        print(f"BBQ: loaded {len(items)} items. Evaluating with {args.model}...", file=sys.stderr)
        bbq_result = evaluate_bbq_full(items, model=args.model, endpoint=args.endpoint)

    all_error = True
    if crowspairs_result and crowspairs_result.get("status") == "ok":
        all_error = False
    if bbq_result and bbq_result.get("status") == "ok":
        all_error = False

    if all_error:
        msg = "All benchmarks failed"
        if crowspairs_result:
            msg += f" \u2014 CrowS-Pairs: {crowspairs_result.get('message', 'unknown error')}"
        if bbq_result:
            msg += f" \u2014 BBQ: {bbq_result.get('message', 'unknown error')}"
        if fmt == "json":
            json_output("bias", {"status": "error", "message": msg}, exit_code=1)
        else:
            print(f"Error: {msg}", file=sys.stderr)
        sys.exit(1)

    if fmt == "json":
        report = format_json_report(crowspairs_result, bbq_result, args.model, args.endpoint, seed)
        json_output("bias", report)
    elif fmt == "annex-iv":
        print(format_annex_iv(crowspairs_result, bbq_result, args.model, args.endpoint))
    else:
        print(format_text_report(crowspairs_result, bbq_result, args.model, args.endpoint))


def cmd_attest(args) -> None:
    """Generate scan attestation (in-toto Statement v1)."""
    import hmac
    import subprocess
    from cli import _validate_path
    from constants import VERSION
    from report import scan_files
    from findings_view import partition_findings

    _validate_path(args.path)
    project = str(Path(args.path).resolve())
    findings = scan_files(project)

    view = partition_findings(findings)

    # Get git commit if available
    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            stderr=subprocess.DEVNULL,
            text=True,
            cwd=project,
        ).strip()
    except Exception:
        commit = "unknown"

    # Create scan result digest
    scan_json = json.dumps(findings, sort_keys=True, default=str)
    digest = hashlib.sha256(scan_json.encode()).hexdigest()

    statement = {
        "_type": "https://in-toto.io/Statement/v1",
        "subject": [{
            "name": f"regula-scan-{args.path}",
            "digest": {"sha256": digest},
        }],
        "predicateType": "https://regula.dev/attestation/scan/v1",
        "predicate": {
            "scanner": {
                "name": "regula",
                "version": VERSION,
            },
            "invocation": {
                "parameters": ["check", args.path],
                "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            },
            "target": {
                "repository": args.path,
                "commit": commit,
            },
            "result": {
                "findings_count": len(findings),
                "prohibited_count": len(view["prohibited"]),
                "high_risk_count": len(view["high_risk"]),
                "digest": digest,
            },
        },
    }

    if args.sign_key:
        key = args.sign_key.encode()
        sig = hmac.new(
            key, json.dumps(statement, sort_keys=True).encode(), hashlib.sha256
        ).hexdigest()
        statement["signatures"] = [{
            "sig": sig,
            "keyid": hashlib.sha256(key).hexdigest()[:16],
        }]

    output = json.dumps(statement, indent=2)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output, encoding="utf-8")
        print(f"Attestation written to {args.output}")
    else:
        print(output)


def cmd_verify(args) -> None:
    """Verify integrity of an evidence pack or conformity pack."""
    from cli import json_output

    pack_path = Path(args.pack_path).resolve()

    # Accept either a directory or a manifest.json directly
    if pack_path.is_file() and pack_path.name == "manifest.json":
        manifest_path = pack_path
        pack_dir = pack_path.parent
    elif pack_path.is_dir():
        # Look for manifest.json or 00-assessment-summary.json
        manifest_path = pack_dir = pack_path
        for candidate in ["manifest.json", "00-assessment-summary.json"]:
            p = pack_path / candidate
            if p.exists():
                manifest_path = p
                break
        else:
            print(f"No manifest.json or 00-assessment-summary.json found in {pack_path}")
            sys.exit(1)
    else:
        print(f"Path not found: {pack_path}")
        sys.exit(1)

    manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))

    # Extract file list — evidence packs use "files", conform packs use "files"
    files = manifest_data.get("files", [])
    if not files:
        print("No files listed in manifest.")
        sys.exit(1)

    passed = 0
    failed = 0
    results = []

    for entry in files:
        filename = entry.get("filename", entry.get("name", ""))
        expected_hash = entry.get("sha256", "")
        filepath = pack_dir / filename

        if not filepath.exists():
            results.append({"file": filename, "status": "MISSING", "expected": expected_hash})
            failed += 1
            continue

        actual_hash = hashlib.sha256(filepath.read_bytes()).hexdigest()
        if actual_hash == expected_hash:
            results.append({"file": filename, "status": "OK"})
            passed += 1
        else:
            results.append({
                "file": filename, "status": "MODIFIED",
                "expected": expected_hash, "actual": actual_hash,
            })
            failed += 1

    if args.format == "json":
        json_output("verify", {
            "pack_path": str(pack_dir),
            "total": len(files),
            "passed": passed,
            "failed": failed,
            "results": results,
        })
    else:
        print(f"\nVerifying: {pack_dir}")
        print(f"{'=' * 60}")
        for r in results:
            icon = "\u2713" if r["status"] == "OK" else "\u2717"
            print(f"  {icon} {r['file']} \u2014 {r['status']}")
        print(f"{'=' * 60}")
        print(f"  {passed}/{len(files)} files verified, {failed} issues")
        if failed > 0:
            print("  WARNING: Pack integrity compromised. Do not submit to auditor.")
            sys.exit(1)
        else:
            print("  All files match manifest. Pack integrity confirmed.")


def cmd_status(args) -> None:
    """Show registry status."""
    from cli import json_output
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
                          f"{rc.get('file', '?')} \u2014 {rc.get('description', '')}")
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
    print(f"  Regula System Registry \u2014 {len(systems)} system(s)")
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


def cmd_audit(args) -> None:
    """Manage audit trail."""
    from cli import json_output
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


def cmd_mcp_server(args) -> None:
    """Start the Regula MCP server over stdio."""
    from mcp_server import run_server
    run_server()


def cmd_questionnaire(args) -> None:
    """Context-driven risk assessment questionnaire."""
    from cli import json_output
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
            except (ValueError, TypeError, AttributeError):
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


def cmd_session(args) -> None:
    """Session-level risk aggregation."""
    from cli import json_output
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


def cmd_docs(args) -> None:
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
        pass  # audit log write failed; non-critical


def cmd_telemetry(args) -> None:
    """Manage anonymous crash report consent (GDPR Article 7)."""
    from telemetry import get_consent, set_consent
    action = getattr(args, "telemetry_action", "status") or "status"

    if action == "status":
        consent = get_consent()
        if consent is None:
            print("Telemetry: not yet configured (will be asked on next run)")
        elif consent:
            print("Telemetry: enabled \u2014 anonymous crash reports are sent to help fix bugs")
            print("  To opt out: regula telemetry disable")
        else:
            print("Telemetry: disabled \u2014 no data is sent")
            print("  To opt in:  regula telemetry enable")
    elif action == "enable":
        set_consent(True)
        print("Telemetry enabled. Thank you \u2014 crash reports help fix bugs faster.")
    elif action == "disable":
        set_consent(False)
        print("Telemetry disabled. No crash reports will be sent.")


def cmd_metrics(args) -> None:
    """Show local usage statistics."""
    from cli import json_output, _print_metrics_text
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


def cmd_security_self_check(args) -> None:
    """Scan regula's own source with its own rules."""
    from cli import json_output
    from security_self_check import run_security_self_check
    result = run_security_self_check(format_type=args.format)
    if args.format == "json":
        json_output("security-self-check", result, exit_code=0 if result["passed"] else 1)
    sys.exit(0 if result["passed"] else 1)


def cmd_owasp_agentic(args) -> None:
    """OWASP Top 10 for Agentic Applications assessment."""
    from cli import json_output, _validate_path
    from agent_monitor import assess_owasp_agentic, format_owasp_agentic_text

    if args.project != ".":
        _validate_path(args.project)
    result = assess_owasp_agentic(args.project)
    fmt = getattr(args, "format", "text")
    if fmt == "json":
        json_output("owasp-agentic", result)
    else:
        print(format_owasp_agentic_text(result))
    # CI mode: exit 1 if any risk is at_risk
    if getattr(args, "strict", False) or getattr(args, "ci", False):
        at_risk = [r for r in result.get("risks", []) if r.get("status") == "at_risk"]
        if at_risk:
            sys.exit(1)


def cmd_ai_codegen(args) -> None:
    """AI-generated code governance scanner."""
    from cli import json_output, _validate_path
    from ai_code_governance import scan_ai_generated_code, format_ai_codegen_text

    if args.project != ".":
        _validate_path(args.project)
    result = scan_ai_generated_code(
        args.project,
        include_git=not getattr(args, "no_git", False),
    )
    fmt = getattr(args, "format", "text")
    if fmt == "json":
        json_output("ai-codegen", result)
    else:
        print(format_ai_codegen_text(result))
    if getattr(args, "strict", False) or getattr(args, "ci", False):
        if not result.get("summary", {}).get("transparency_compliant", False):
            sys.exit(1)
