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
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# Ensure scripts directory is importable
sys.path.insert(0, str(Path(__file__).parent))

from constants import VERSION
from errors import RegulaError, PathError

# Map jurisdiction short names to framework_mapper keys
JURISDICTION_MAP = {
    'eu': 'eu-ai-act',
    'colorado': 'colorado-sb205',
    'korea': 'south-korea-ai',
    'canada': 'canada-aida',
    'singapore': 'singapore-ai',
    'oecd': 'oecd-ai',
    'uk': 'ico-ai-guidance',
    'brazil': 'lgpd',
    'nist': 'nist-ai-rmf',
    'iso': 'iso-42001',
}


def _is_tty():
    """Check if stdout is a terminal."""
    return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()


def _use_color():
    """Check if color output should be used."""
    if os.environ.get('NO_COLOR') or os.environ.get('REGULA_NO_COLOR'):
        return False
    if not _is_tty():
        return False
    return True


def _info(msg):
    """Print informational message to stderr."""
    if _is_tty():
        print(msg, file=sys.stderr)


def json_output(command: str, data, exit_code: int = 0, deterministic: bool = False):
    """Standard JSON envelope for all --format json output."""
    envelope = {
        "format_version": "1.0",
        "regula_version": VERSION,
        "command": command,
        "exit_code": exit_code,
        "data": data,
    }
    if not deterministic:
        envelope["timestamp"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    print(json.dumps(envelope, indent=2, sort_keys=True, default=str))


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


def _current_pattern_version() -> str:
    """Read the pattern_version from regula-policy.yaml (best-effort)."""
    try:
        import yaml as _yaml
        policy_path = Path(__file__).parent.parent / "regula-policy.yaml"
        data = _yaml.safe_load(policy_path.read_text(encoding="utf-8"))
        basis = (data or {}).get("regulatory_basis", {})
        return f"{basis.get('pattern_version', 'unknown')}-{basis.get('last_reviewed', 'unknown')}"
    except Exception:
        return f"{VERSION}-patterns"  # Fallback when policy file unavailable


_SAFE_GIT_REF = re.compile(r'^[a-zA-Z0-9_.~^@{}/:\-]+$')


def _get_changed_files(project_path: str, git_ref: str = "HEAD~1") -> list[str]:
    """Get list of files changed since git_ref.

    Uses git diff to find changed/added files. Falls back to scanning all files
    if git is not available or the path is not a git repo.
    """
    import subprocess
    if not _SAFE_GIT_REF.match(git_ref):
        print(f"Error: unsafe git ref: {git_ref!r}", file=sys.stderr)
        return []
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
    from risk_types import compute_finding_tier
    return compute_finding_tier(finding.get("tier", ""), finding.get("confidence_score", 0))


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


def _resolve_jurisdictions(jurisdictions_arg):
    """Resolve a comma-separated jurisdictions string to framework keys.

    Returns a list of (short_name, framework_key) tuples for valid jurisdictions.
    Prints a warning to stderr for unknown jurisdiction names.
    """
    resolved = []
    for j in jurisdictions_arg.split(","):
        j = j.strip().lower()
        if not j:
            continue
        fw_key = JURISDICTION_MAP.get(j)
        if fw_key:
            resolved.append((j, fw_key))
        else:
            print(f"  Warning: unknown jurisdiction '{j}' — "
                  f"valid: {', '.join(sorted(JURISDICTION_MAP))}", file=sys.stderr)
    return resolved


def _enrich_findings_with_jurisdictions(findings, jurisdiction_pairs):
    """Add jurisdiction mapping labels to each finding based on its articles.

    Mutates findings in place, adding a 'jurisdictions' key with a dict of
    {jurisdiction_short_name: [label_strings]}.
    """
    from framework_mapper import map_to_frameworks, _FRAMEWORK_KEYS, format_mapping_text

    # Build the list of internal framework keys to query
    fw_keys = [fw_key for _, fw_key in jurisdiction_pairs]

    # Jurisdiction display names
    _JURISDICTION_DISPLAY = {
        'eu': 'EU AI Act',
        'colorado': 'Colorado SB-205',
        'korea': 'South Korea AI Basic Act',
        'canada': 'Canada AIDA',
        'singapore': 'Singapore AI Governance',
        'oecd': 'OECD AI Principles',
        'uk': 'UK ICO AI Guidance',
        'brazil': 'LGPD (Brazil)',
        'nist': 'NIST AI RMF',
        'iso': 'ISO/IEC 42001',
    }

    for finding in findings:
        articles = finding.get("articles") or []
        if not articles:
            continue

        mapping = map_to_frameworks(articles=articles, frameworks=fw_keys)
        jurisdiction_labels = {}

        for short_name, fw_key in jurisdiction_pairs:
            # Resolve to internal key (e.g. 'eu-ai-act' -> 'eu_ai_act')
            internal_key = _FRAMEWORK_KEYS.get(fw_key, fw_key)
            labels = []
            for article, fw_data in mapping.items():
                data = fw_data.get(internal_key, {})
                if not data:
                    continue
                # Extract a human-readable label from the mapping data
                label = _extract_jurisdiction_label(short_name, internal_key, data, finding)
                if label:
                    labels.append(label)
            if labels:
                jurisdiction_labels[short_name] = labels

        if jurisdiction_labels:
            finding["jurisdictions"] = jurisdiction_labels


def _extract_jurisdiction_label(short_name, internal_key, data, finding):
    """Extract a single human-readable label from framework mapping data."""
    category = finding.get("category", "")
    desc = finding.get("description", "")
    context = category or desc

    if internal_key == "eu_ai_act":
        title = data.get("title", "")
        return f"EU AI Act: {title}" if title else "EU AI Act"
    elif internal_key == "colorado_sb205":
        reqs = data.get("requirements", [])
        return f"Colorado SB-205: {reqs[0]}" if reqs else "Colorado SB-205: Consequential decision"
    elif internal_key == "south_korea_ai":
        reqs = data.get("requirements", [])
        return f"South Korea: {reqs[0]}" if reqs else "South Korea: High-impact AI"
    elif internal_key == "canada_aida":
        reqs = data.get("requirements", [])
        return f"Canada AIDA: {reqs[0]}" if reqs else "Canada AIDA"
    elif internal_key == "singapore_ai":
        principles = data.get("principles", [])
        return f"Singapore: {principles[0]}" if principles else "Singapore AI Governance"
    elif internal_key == "oecd_ai":
        principles = data.get("principles", [])
        return f"OECD: {principles[0]}" if principles else "OECD AI Principles"
    elif internal_key == "ico_ai":
        principles = data.get("principles", [])
        return f"UK ICO: {principles[0]}" if principles else "UK ICO AI Guidance"
    elif internal_key == "lgpd":
        articles = data.get("articles", [])
        return f"LGPD: {articles[0]}" if articles else "LGPD (Brazil)"
    elif internal_key == "nist_ai_rmf":
        functions = data.get("functions", [])
        return f"NIST AI RMF: {', '.join(functions)}" if functions else "NIST AI RMF"
    elif internal_key == "iso_42001":
        controls = data.get("controls", [])
        return f"ISO 42001: {controls[0]}" if controls else "ISO/IEC 42001"
    return short_name


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
    from report import scan_files, generate_html_report, generate_sarif, generate_sales_report

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
    elif args.format == "sales":
        content = generate_sales_report(findings, project_name)
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

    # C4: --merge — combine multiple per-repo inventory fragments into
    # a single org-level inventory without requiring a hosted registry.
    merge_files = getattr(args, "merge", None)
    if merge_files:
        merged = {"models": [], "source_repos": [], "merged_at": None}
        from datetime import datetime, timezone
        merged["merged_at"] = datetime.now(timezone.utc).isoformat()
        for mf in merge_files:
            try:
                data = _json.loads(Path(mf).read_text(encoding="utf-8"))
            except (OSError, _json.JSONDecodeError) as e:
                print(f"inventory --merge: skipping {mf}: {e}", file=sys.stderr)
                continue
            # Handle various inventory JSON shapes: dict with "models"
            # key, dict with "data.models", or a raw list of model entries.
            if isinstance(data, list):
                models = data
            elif isinstance(data, dict):
                models = data.get("models") or data.get("data", {}).get("models", [])
            else:
                models = []
            if isinstance(models, list):
                for m in models:
                    m["_source_file"] = mf
                merged["models"].extend(models)
            merged["source_repos"].append(mf)
        merged["total_models"] = len(merged["models"])
        fmt = getattr(args, "format", "table")
        if fmt == "json":
            json_output("inventory", merged)
        else:
            print(f"Merged inventory: {merged['total_models']} models from "
                  f"{len(merged['source_repos'])} repos")
            for m in merged["models"]:
                name = m.get("name") or m.get("model_name") or "unnamed"
                src = m.get("_source_file", "?")
                print(f"  {name} ← {src}")
        return

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


def cmd_exempt(args):
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


def cmd_gpai_check(args):
    """GPAI Code of Practice check (Chapters 1-3)."""
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


def cmd_register(args):
    """Generate an Annex VIII registration packet for a project (Article 49)."""
    import os
    from register import build_packet, write_packet, write_gaps_yaml
    from discover_ai_systems import discover
    from explain import detect_provider_deployer

    project_path = args.path or "."
    try:
        project = _validate_path(project_path)
    except PathError as e:
        print(str(e), file=sys.stderr)
        sys.exit(2)

    if not project.is_dir():
        print(f"register: PATH must be a directory, got {project}", file=sys.stderr)
        sys.exit(2)

    # Determine output directory before chdir so relative --output is interpreted from CWD
    if args.output:
        out_dir = Path(args.output).parent
        if not out_dir.is_absolute():
            out_dir = (Path.cwd() / out_dir).resolve()
    else:
        out_dir = (project / ".regula" / "registry").resolve()

    # chdir into project so resolve_autofill's Path(".regula/...") helpers see the right files
    original_cwd = Path.cwd()
    try:
        os.chdir(project)

        discovery = discover(str(project))
        annex_iii_point = _highest_annex_iii_point(discovery)
        code_blob = _read_code_blob(project)
        pd = detect_provider_deployer(code_blob)
        role = pd["role"]  # provider | deployer | unclear

        deployer_type = getattr(args, "deployer_type", "none") or "none"
        art_6_3_exempted = getattr(args, "art_6_3_exempted", False)

        forced_section = getattr(args, "section", "auto")
        if forced_section != "auto":
            if forced_section == "B":
                art_6_3_exempted = True
            elif forced_section == "C" and role != "deployer":
                print(f"register: --section C requires a deployer role, got {role}", file=sys.stderr)
                sys.exit(2)

        try:
            packet = build_packet(
                discovery=discovery, role=role, annex_iii_point=annex_iii_point,
                deployer_type=deployer_type, art_6_3_exempted=art_6_3_exempted,
            )
        except Exception as e:
            print(f"register: failed to build packet: {e}", file=sys.stderr)
            sys.exit(2)
    finally:
        os.chdir(original_cwd)

    try:
        out_path = write_packet(packet, output_dir=out_dir, force=args.force)
    except FileExistsError as e:
        print(f"register: {e}", file=sys.stderr)
        sys.exit(2)

    if not getattr(args, "no_gaps_yaml", False) and packet.get("_gaps"):
        write_gaps_yaml(packet, output_dir=out_dir)

    if args.format == "json":
        json_output("register", packet)
    else:
        _print_register_text(packet, out_path)


def _highest_annex_iii_point(discovery: dict):
    """Return the Annex III point number for the highest-risk classification, or None.

    Reads the actual discover_ai_systems shape: each risk_classifications entry has
    `indicators` (list of pattern names) and `description` (free text). Earlier
    revisions of this helper looked for `category`/`patterns` which don't exist,
    causing all packets to fall through to not_applicable. Fixed.
    """
    risk_classifications = discovery.get("risk_classifications", []) or []
    pattern_to_point = {
        "biometrics": 1,
        "critical_infrastructure": 2,
        "education": 3,
        "employment": 4,
        "essential_services": 5,
        "law_enforcement": 6,
        "migration": 7,
        "justice": 8,
    }
    for rc in risk_classifications:
        # Search indicators (the actual pattern names) and description (free text)
        haystack = " ".join([
            *(rc.get("indicators") or []),
            (rc.get("description") or ""),
            (rc.get("category") or ""),  # legacy compatibility, harmless
        ]).lower()
        for k, v in pattern_to_point.items():
            if k in haystack:
                return v
        for pat in (rc.get("patterns") or []):
            for k, v in pattern_to_point.items():
                if k in pat.lower():
                    return v
    return None


def _read_code_blob(project: Path) -> str:
    """Concatenate up to ~200 KB of .py source from the project for role detection."""
    chunks = []
    total = 0
    for py in project.rglob("*.py"):
        s = str(py)
        if "/.regula/" in s or "/__pycache__/" in s:
            continue
        try:
            content = py.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        chunks.append(content)
        total += len(content)
        if total > 200_000:
            break
    return "\n".join(chunks)


def _print_register_text(packet: dict, out_path) -> None:
    """Human-readable summary."""
    print(f"\n=== Annex VIII Registration Packet ===")
    print(f"  System:           {packet.get('system_name', '?')}")
    print(f"  System ID:        {packet.get('system_id', '?')}")
    kind = packet.get("kind", "?")
    print(f"  Kind:             {kind}")
    if kind == "registration_required":
        print(f"  Section:          {packet.get('annex_viii_section')} (Article {packet.get('article')})")
        print(f"  Submission target: {packet.get('submission_target')}")
        print(f"  Status:           {packet.get('submission_status')}")
        comp = packet.get("completeness", {})
        print(f"  Completeness:     {comp.get('filled')}/{comp.get('total')} ({comp.get('percentage')}%)")
        gaps = packet.get("_gaps", [])
        if gaps:
            print(f"  Gaps to fill:     {len(gaps)} field(s) — see {out_path.with_suffix('.gaps.yaml').name}")
    else:
        print(f"  Reason:           {packet.get('reason', '')}")
        print(f"  Next steps:")
        for r in packet.get("redirects", []):
            print(f"    - {r}")
    d = packet.get("deadlines", {})
    print(f"\n  Deadline (current law):    {d.get('applicable_deadline')}")
    print(f"  Deadline (Omnibus prop.):  {d.get('omnibus_proposed_deadline')}  [{d.get('omnibus_status')}]")
    print(f"\n  Packet written to: {out_path}")
    print()


def cmd_feedback(args):
    """Open a pre-filled GitHub Issue to report a false positive, false negative, or bug."""
    import os
    from telemetry import build_feedback_url

    kind = getattr(args, "feedback_kind", "false-positive") or "false-positive"
    url = build_feedback_url(
        kind=kind,
        pattern_id=getattr(args, "pattern", None),
        file_path=getattr(args, "file", None),
        line_number=getattr(args, "line", None),
        regula_version=VERSION,
        description=getattr(args, "description", None),
    )

    no_browser = getattr(args, "no_browser", False)
    in_ci = not sys.stdin.isatty() or bool(os.environ.get("CI"))

    note = "(Label will apply automatically if it exists in the repo)"

    if no_browser or in_ci:
        print(f"Report URL:\n{url}")
        print(note)
        return

    import webbrowser
    print(f"Opening GitHub Issue in browser...")
    print(f"URL: {url}")
    print(note)
    webbrowser.open(url)


def cmd_telemetry(args):
    """Manage anonymous crash report consent (GDPR Article 7)."""
    from telemetry import get_consent, set_consent
    action = getattr(args, "telemetry_action", "status") or "status"

    if action == "status":
        consent = get_consent()
        if consent is None:
            print("Telemetry: not yet configured (will be asked on next run)")
        elif consent:
            print("Telemetry: enabled — anonymous crash reports are sent to help fix bugs")
            print("  To opt out: regula telemetry disable")
        else:
            print("Telemetry: disabled — no data is sent")
            print("  To opt in:  regula telemetry enable")
    elif action == "enable":
        set_consent(True)
        print("Telemetry enabled. Thank you — crash reports help fix bugs faster.")
    elif action == "disable":
        set_consent(False)
        print("Telemetry disabled. No crash reports will be sent.")


def cmd_fix(args):
    """Generate compliance fix scaffolds for findings."""
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


_ORGANISATIONAL_QUESTIONS = {
    "article_9_risk_management": {
        "article": "Article 9",
        "title": "Risk Management System",
        "questions": [
            ("rms_documented", "Is a documented risk management system in place for this AI system?"),
            ("rms_operated", "Is the RMS actively operated (not just documented)?"),
            ("rms_reviewed", "Has the RMS been reviewed in the last 12 months?"),
            ("rms_owner", "Is there a named person accountable for the RMS?"),
            ("rms_residual", "Have residual risks been identified and accepted by management?"),
        ],
    },
    "article_17_qms": {
        "article": "Article 17",
        "title": "Quality Management System",
        "questions": [
            ("qms_documented", "Is a documented quality management system in place?"),
            ("qms_design_verification", "Does the QMS cover design verification and validation?"),
            ("qms_data_management", "Does the QMS include data management procedures?"),
            ("qms_post_market", "Does the QMS include post-market monitoring procedures?"),
            ("qms_complaint_handling", "Is there a complaint-handling process for AI system issues?"),
            ("qms_audit_internal", "Have internal QMS audits been conducted?"),
        ],
    },
    "article_29a_fria": {
        "article": "Article 29a",
        "title": "Fundamental Rights Impact Assessment",
        "questions": [
            ("fria_conducted", "Has a fundamental rights impact assessment been conducted?"),
            ("fria_stakeholders", "Were affected persons or their representatives consulted?"),
            ("fria_documented", "Is the FRIA documented and available for inspection?"),
            ("fria_mitigations", "Have identified fundamental-rights risks been mitigated?"),
        ],
    },
    "article_72_pmm": {
        "article": "Article 72",
        "title": "Post-Market Monitoring",
        "questions": [
            ("pmm_plan", "Is there a documented post-market monitoring plan?"),
            ("pmm_active", "Is post-market monitoring actively collecting data?"),
            ("pmm_incidents", "Is there a process for reporting serious incidents per Article 73?"),
            ("pmm_corrective", "Is there a corrective-action process when monitoring detects issues?"),
        ],
    },
}


def _run_organisational_questionnaire(args):
    """Interactive questionnaire for organisational AI Act obligations.

    These are the articles Regula cannot verify from code — Art. 9 (RMS),
    Art. 17 (QMS), Art. 29a (FRIA), Art. 72 (PMM). The output is a
    structured evidence document, NOT a compliance certificate.
    """
    import json as _json
    from datetime import datetime, timezone

    fmt = getattr(args, "format", "text")
    project_name = getattr(args, "name", None) or "unnamed-system"
    output_dir = getattr(args, "output", None)

    results: dict = {
        "command": "conform --organisational",
        "project_name": project_name,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "regula_version": VERSION,
        "disclaimer": (
            "This is a structured questionnaire, NOT a compliance certificate. "
            "Regula cannot verify organisational processes from code. The answers "
            "below are self-reported by the operator and must be independently "
            "verified by an auditor, notified body, or internal governance function."
        ),
        "sections": {},
    }

    total_yes = 0
    total_questions = 0

    interactive = fmt != "json"

    for section_key, section in _ORGANISATIONAL_QUESTIONS.items():
        if interactive:
            print(f"\n--- {section['article']}: {section['title']} ---")
        section_result = {
            "article": section["article"],
            "title": section["title"],
            "answers": {},
        }
        yes_count = 0
        for q_id, question in section["questions"]:
            total_questions += 1
            if fmt == "json":
                # Non-interactive mode: default to "not answered"
                section_result["answers"][q_id] = {
                    "question": question,
                    "answer": "not_answered",
                    "note": "",
                }
                continue
            while True:
                answer = input(f"  {question} [y/n/skip]: ").strip().lower()
                if answer in ("y", "yes"):
                    section_result["answers"][q_id] = {
                        "question": question, "answer": "yes", "note": "",
                    }
                    yes_count += 1
                    total_yes += 1
                    break
                elif answer in ("n", "no"):
                    note = input("    Brief note (why not, or planned date): ").strip()
                    section_result["answers"][q_id] = {
                        "question": question, "answer": "no", "note": note,
                    }
                    break
                elif answer in ("s", "skip"):
                    section_result["answers"][q_id] = {
                        "question": question, "answer": "skipped", "note": "",
                    }
                    break
                else:
                    print("    Please enter y, n, or skip.")

        section_result["score"] = (
            f"{yes_count}/{len(section['questions'])}"
        )
        results["sections"][section_key] = section_result

    results["summary"] = {
        "total_questions": total_questions,
        "answered_yes": total_yes,
        "overall_score": f"{total_yes}/{total_questions}",
    }

    if fmt == "json":
        json_output("conform", results)
    else:
        print(f"\n{'='*60}")
        print(f"Organisational compliance self-assessment: "
              f"{total_yes}/{total_questions}")
        for sk, sv in results["sections"].items():
            print(f"  {sv['article']} {sv['title']}: {sv['score']}")
        print(f"\nDisclaimer: {results['disclaimer']}")

        if output_dir:
            out_path = Path(output_dir) / "organisational-assessment.json"
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(
                _json.dumps(results, indent=2) + "\n", encoding="utf-8"
            )
            print(f"\nWritten to {out_path}")


def cmd_conform(args):
    """Generate conformity assessment evidence pack."""
    # F1: --organisational — questionnaire mode for the articles Regula
    # cannot verify from code (Art. 9 RMS, Art. 17 QMS, Art. 29a FRIA,
    # Art. 72 PMM). This does NOT scan code — it asks structured yes/no
    # questions and produces an evidence document from the answers.
    if getattr(args, "organisational", False):
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


def cmd_governance(args):
    """Generate AI governance scaffold."""
    from generate_documentation import scan_project, generate_ai_governance

    if args.project != ".":
        _validate_path(args.project)
    project_path = str(Path(args.project).resolve())
    project_name = args.name or Path(project_path).name

    print(f"Scanning {project_path}...", file=sys.stderr)
    findings = scan_project(project_path)

    doc = generate_ai_governance(findings, project_name, project_path)

    output = Path(args.output)
    output.write_text(doc, encoding="utf-8")
    print(f"AI governance scaffold written to: {output}")
    print("IMPORTANT: This document requires human review and completion.")

    if getattr(args, "format", "text") == "json":
        json_output("governance", {"output_file": str(output), "project": project_name})


def cmd_model_card(args):
    """Generate model card scaffold."""
    from generate_documentation import scan_project, generate_model_card

    if args.project != ".":
        _validate_path(args.project)
    project_path = str(Path(args.project).resolve())
    project_name = args.name or Path(project_path).name

    print(f"Scanning {project_path}...", file=sys.stderr)
    findings = scan_project(project_path)

    doc = generate_model_card(findings, project_name, project_path)

    output = Path(args.output)
    output.write_text(doc, encoding="utf-8")
    print(f"Model card scaffold written to: {output}")
    print("IMPORTANT: This document requires human review before publication.")

    if getattr(args, "format", "text") == "json":
        json_output("model-card", {"output_file": str(output), "project": project_name})


def cmd_benchmark(args):
    """Run real-world validation benchmark."""
    from benchmark import benchmark_project, benchmark_suite, calculate_metrics, load_labelled_results
    from benchmark import format_benchmark_text, format_labelling_csv

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
    bom = generate_sbom(args.project, project_name=args.name, ai_bom=getattr(args, 'ai_bom', False))
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


def cmd_owasp_agentic(args):
    """OWASP Top 10 for Agentic Applications assessment."""
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


def cmd_guardrails(args):
    """Detect guardrail implementation coverage."""
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


def cmd_ai_codegen(args):
    """AI-generated code governance scanner."""
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


def cmd_agent(args):
    """Agentic AI governance monitoring."""
    from agent_monitor import analyse_agent_session, check_mcp_config, format_agent_text

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


def cmd_assess(args):
    """EU AI Act applicability check -- no code required."""
    from assess import run_assess
    output_format = getattr(args, "format", "text")
    answers = getattr(args, "answers", None)
    sys.exit(run_assess(output_format, answers=answers))


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


def cmd_handoff(args):
    """Emit a red-team config file for Garak, Giskard, or Promptfoo,
    scoped to the LLM entrypoints Regula detects in the project.

    Regula does static analysis; runtime model behaviour testing is
    complementary. This command positions Regula as a partner to those
    tools, not a competitor.
    """
    from pathlib import Path as _Path
    from handoff import run_handoff
    result = run_handoff(args.tool, _Path(args.project),
                         _Path(args.output) if args.output else None)
    fmt = getattr(args, "format", "text")
    if fmt == "json":
        json_output("handoff", result)
    else:
        if "error" in result:
            print(f"handoff: {result['error']}", file=sys.stderr)
            sys.exit(2)
        print(f"handoff ({result['tool']}): wrote {result['config_path']}")
        print(f"  entrypoints detected: {result['entrypoint_count']}")
        if result['entrypoint_count']:
            print("  sample:")
            for e in result['entrypoints'][:5]:
                print(f"    {e['file']}:{e['line']} [{e['kind']}]")
        # Show red-team coverage score if available
        coverage = result.get("coverage")
        if coverage:
            from handoff import format_coverage_text
            print()
            print(format_coverage_text(coverage))
        else:
            print(f"\n{result['note']}")


def cmd_regwatch(args):
    """Warn when Regula's pattern ruleset is older than the most recent
    regulatory change recorded in the delta log."""
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


def cmd_oversight(args):
    """Article 14 human oversight analysis (cross-file)."""
    from cross_file_flow import analyse_project_oversight

    project = getattr(args, "project", ".")
    result = analyse_project_oversight(project)
    fmt = getattr(args, "format", "text")

    if fmt == "json":
        json_output("oversight", result)
        return

    # Text output
    summary = result["summary"]
    print("Article 14 Human Oversight Analysis")
    print("=" * 36)
    print("Scope: Static analysis of direct imports and explicit function calls.")
    print("NOT analysed: dynamic imports, decorator-wrapped routes, cross-service calls,")
    print("              third-party library internals.")
    print()

    ai_count = len(result.get("ai_sources", []))
    total = summary.get("total_paths", 0)
    if ai_count == 0:
        print("No AI output sources found in scanned Python files.")
    else:
        print(f"Found {ai_count} AI output source{'s' if ai_count != 1 else ''}:")
        for src in result["ai_sources"]:
            print(f"  - {src['source']} at {src['file']}:{src['source_line']}")
        print()

        reviewed = summary["reviewed"]
        print(f"Human oversight gates detected on flow path: {reviewed} of {total}")
        for path in result["flow_paths"]:
            marker = "\u2713" if path["has_oversight"] else "\u26a0"
            loc = f"{path['source_file']}:{path['source_line']}"
            if path["hops"]:
                hop = path["hops"][0]
                target = f"{hop['to_file']}:{hop['line']} ({hop['function']})"
                tag = "human oversight detected" if path["has_oversight"] else "NO oversight gate found"
                print(f"  {marker} {loc} \u2192 {target} ({tag})")
            else:
                tag = "in-file oversight" if path["has_oversight"] else "NO oversight gate found"
                print(f"  {marker} {loc} ({tag})")

    print()
    print(f"Confidence: {result['confidence'].upper()}")
    print("Note: This analysis detects code paths for oversight, not whether oversight")
    print("      is meaningfully exercised. See ICO ADM guidance (March 2026).")

    if summary["unreviewed"] > 0:
        sys.exit(1)


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

Environment variables (override defaults when CLI flag not provided):
  REGULA_FORMAT       Output format (text, json, sarif)
  REGULA_STRICT       Enable CI mode when set to 1/true/yes
  REGULA_MIN_TIER     Minimum risk tier to report
  REGULA_LANG         Output language (en, pt-BR, de)
  REGULA_SKIP_TESTS   Skip test files when set to 1/true/yes
  REGULA_FRAMEWORK    Compliance framework
"""


def cmd_badge(args):
    """Generate compliance badge from scan results."""
    from report import scan_files
    from findings_view import partition_findings

    _validate_path(args.path)
    project = str(Path(args.path).resolve())
    findings = scan_files(project)

    view = partition_findings(findings)
    prohibited = view["prohibited"]
    high_risk = view["high_risk"]

    if prohibited:
        color = "red"
        message = f"{len(prohibited)} prohibited"
    elif high_risk:
        color = "orange"
        message = f"{len(high_risk)} high-risk"
    else:
        color = "brightgreen"
        message = "compliant"

    if args.format == "endpoint":
        badge = {
            "schemaVersion": 1,
            "label": "EU AI Act",
            "message": message,
            "color": color,
        }
        print(json.dumps(badge, indent=2))
    elif args.format == "svg":
        label = "EU AI Act"
        label_width = len(label) * 7 + 10
        msg_width = len(message) * 7 + 10
        total_width = label_width + msg_width
        colors = {"brightgreen": "#4c1", "orange": "#fe7d37", "red": "#e05d44"}
        fill = colors.get(color, "#9f9f9f")
        svg = (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{total_width}" height="20">\n'
            f'  <linearGradient id="b" x2="0" y2="100%">'
            f'<stop offset="0" stop-color="#bbb" stop-opacity=".1"/>'
            f'<stop offset="1" stop-opacity=".1"/></linearGradient>\n'
            f'  <mask id="a"><rect width="{total_width}" height="20" rx="3" fill="#fff"/></mask>\n'
            f'  <g mask="url(#a)">'
            f'<rect width="{label_width}" height="20" fill="#555"/>'
            f'<rect x="{label_width}" width="{msg_width}" height="20" fill="{fill}"/>'
            f'<rect width="{total_width}" height="20" fill="url(#b)"/></g>\n'
            f'  <g fill="#fff" text-anchor="middle" '
            f'font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="11">\n'
            f'    <text x="{label_width / 2}" y="15" fill="#010101" fill-opacity=".3">{label}</text>\n'
            f'    <text x="{label_width / 2}" y="14">{label}</text>\n'
            f'    <text x="{label_width + msg_width / 2}" y="15" fill="#010101" fill-opacity=".3">'
            f'{message}</text>\n'
            f'    <text x="{label_width + msg_width / 2}" y="14">{message}</text>\n'
            f'  </g>\n'
            f'</svg>'
        )
        print(svg)
    else:
        # Markdown snippet
        shield_url = (
            f"https://img.shields.io/badge/EU%20AI%20Act-{message.replace(' ', '%20')}-{color}"
        )
        print(f"[![EU AI Act]({shield_url})](https://getregula.com)")


def cmd_attest(args):
    """Generate scan attestation (in-toto Statement v1)."""
    import hashlib
    import hmac
    import subprocess

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


def cmd_explain_article(args):
    """Explain an EU AI Act article in plain language."""
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
    p_check.add_argument("--deterministic", action="store_true", default=False,
                         help="Deterministic JSON output (omit timestamp) for CI baseline comparison")
    p_check.add_argument("--jurisdictions",
                         help="Comma-separated jurisdictions (e.g. eu,colorado,korea). "
                              "Applies all relevant framework mappings simultaneously. "
                              "Valid: " + ", ".join(sorted(JURISDICTION_MAP)))
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
    p_report.add_argument("--format", "-f", choices=["html", "sarif", "json", "sales"], default="html")
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
        "--pattern-version",
        metavar="VERSION",
        help="Stamp the assessment against a specific pattern ruleset version "
             "(e.g., '1.6.1-patterns-2026-04-09') for reproducible audits. "
             "If omitted, the current pattern version from regula-policy.yaml is used.",
    )
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

    # --- exempt ---
    p_exempt = subparsers.add_parser(
        "exempt",
        help="Article 6(3) high-risk exemption decision tree (interactive or --answers)",
    )
    p_exempt.add_argument(
        "--answers",
        help=("Non-interactive mode: comma-separated yes/no values in order "
              "annex_iii,profiling,narrow_procedural,improve_human,detect_patterns,preparatory"),
    )
    p_exempt.add_argument("--format", "-f", choices=["text", "json"], default="text")
    p_exempt.set_defaults(func=cmd_exempt)

    # --- gpai-check ---
    p_gpai = subparsers.add_parser(
        "gpai-check",
        help="Map GPAI provider code to the three Code of Practice chapters (Art 53 + Art 55)",
    )
    p_gpai.add_argument("path", nargs="?", default=".", help="Project path (default: current dir)")
    p_gpai.add_argument("--systemic-risk", action="store_true",
                        help="Evaluate Chapter 3 (Safety & Security) — applies only when training compute >= 10^25 FLOPs (Art 51)")
    p_gpai.add_argument("--strict", action="store_true",
                        help="Exit 1 if any obligation FAILs")
    p_gpai.add_argument("--format", "-f", choices=["text", "json"], default="text")
    p_gpai.set_defaults(func=cmd_gpai_check)

    # --- register ---
    p_register = subparsers.add_parser("register", help="Generate Annex VIII registration packet (Article 49)")
    p_register.add_argument("path", nargs="?", default=".", help="Project path (default: current dir)")
    p_register.add_argument("--section", choices=["auto", "A", "B", "C"], default="auto",
                            help="Force a section (default: auto-detect via role)")
    p_register.add_argument("--target", choices=["auto", "eu_public", "eu_non_public", "national"],
                            default="auto", help="Force submission target")
    p_register.add_argument("--deployer-type", choices=["none", "public_authority"],
                            default="none", help="Override role detection")
    p_register.add_argument("--art-6-3-exempted", action="store_true",
                            help="Provider has self-assessed as non-high-risk under Art 6(3)")
    p_register.add_argument("--output", "-o", help="Output path (default: .regula/registry/<system-id>.json)")
    p_register.add_argument("--format", "-f", choices=["text", "json"], default="text")
    p_register.add_argument("--force", action="store_true", help="Overwrite existing packet")
    p_register.add_argument("--no-gaps-yaml", action="store_true", help="Skip companion .gaps.yaml")
    p_register.set_defaults(func=cmd_register)

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

    # --- conform ---
    p_conform = subparsers.add_parser(
        "conform",
        help="Generate conformity assessment evidence pack (Article 43), "
             "SME simplified Annex IV (Article 11(1)), or organisational "
             "compliance questionnaire (Articles 9/17/29a/72)",
    )
    p_conform.add_argument("--project", "-p", default=".")
    p_conform.add_argument("--output", "-o", default=".", help="Output directory for the pack folder")
    p_conform.add_argument("--name", "-n", help="Project name")
    p_conform.add_argument("--sme", action="store_true",
                           help="Generate the SME-simplified Annex IV single-file form (Article 11(1) second subparagraph) instead of the full multi-folder evidence pack")
    p_conform.add_argument("--organisational", action="store_true",
                           help="Interactive questionnaire for organisational AI Act obligations "
                                "(Articles 9 RMS, 17 QMS, 29a FRIA, 72 PMM) that Regula cannot "
                                "verify from code. Produces a self-assessment evidence document, "
                                "NOT a compliance certificate.")
    p_conform.add_argument("--format", "-f", choices=["text", "json"], default="text")
    p_conform.set_defaults(func=cmd_conform)

    # --- governance ---
    p_governance = subparsers.add_parser("governance", help="Generate AI governance scaffold (Article 4, ISO 42001)")
    p_governance.add_argument("--project", "-p", default=".")
    p_governance.add_argument("--output", "-o", default="AI_GOVERNANCE.md")
    p_governance.add_argument("--name", "-n", help="Project name")
    p_governance.add_argument("--format", "-f", choices=["text", "json"], default="text")
    p_governance.set_defaults(func=cmd_governance)

    # --- model-card ---
    p_model_card = subparsers.add_parser("model-card", help="Generate model card scaffold (Annex IV, ISO 42001 Annex B)")
    p_model_card.add_argument("--project", "-p", default=".")
    p_model_card.add_argument("--output", "-o", default="MODEL_CARD.md")
    p_model_card.add_argument("--name", "-n", help="Project name")
    p_model_card.add_argument("--format", "-f", choices=["text", "json"], default="text")
    p_model_card.set_defaults(func=cmd_model_card)

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

    p_handoff = subparsers.add_parser(
        "handoff",
        help="Emit a red-team config for Garak, Giskard, or Promptfoo "
             "scoped to the LLM entrypoints detected in this project",
    )
    p_handoff.add_argument("tool", choices=("garak", "giskard", "promptfoo"))
    p_handoff.add_argument("project", nargs="?", default=".",
                           help="Project directory to scan (default: .)")
    p_handoff.add_argument("--output", "-o",
                           help="Output file (default: <tool>.regula.yaml in project)")
    p_handoff.add_argument("--format", "-f", choices=["text", "json"], default="text")
    p_handoff.set_defaults(func=cmd_handoff)

    p_regwatch = subparsers.add_parser(
        "regwatch",
        help="Warn when Regula's pattern ruleset is older than the most "
             "recent regulatory change recorded in the delta log",
    )
    p_regwatch.add_argument("--format", "-f", choices=["text", "json"], default="text")
    p_regwatch.set_defaults(func=cmd_regwatch)

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
    p_sbom.add_argument("--ai-bom", action="store_true", help="Include AI-specific BOM fields (model provenance, GPAI tiers, datasets)")
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
    p_inventory = subparsers.add_parser(
        "inventory",
        help="Scan codebase for AI model references (GPAI tier annotations). "
             "Use --merge to combine per-repo inventories into an org-level view.",
    )
    p_inventory.add_argument("path", nargs="?", default=".", help="Path to scan")
    p_inventory.add_argument("--format", "-f", choices=["table", "json"], default="table")
    p_inventory.add_argument("--output", "-o", help="Output file (optional)")
    p_inventory.add_argument(
        "--merge", nargs="+", metavar="FILE",
        help="Merge multiple per-repo inventory JSON files into an org-level "
             "view (e.g., regula inventory --merge repo-a.json repo-b.json)",
    )
    p_inventory.set_defaults(func=cmd_inventory)

    # --- assess ---
    p_assess = subparsers.add_parser(
        "assess",
        help="EU AI Act applicability check -- does this apply to your product? (no code required)",
    )
    p_assess.add_argument("--format", "-f", choices=["text", "json"], default="text")
    p_assess.add_argument(
        "--answers",
        help=(
            "Non-interactive: comma-separated yes/no answers in order "
            "uses_ai,eu_users,prohibited,high_risk_domain,"
            "non_eu_provider|transparency_trigger "
            "(the 5th slot is non_eu_provider when high_risk=yes, "
            "else transparency_trigger)."
        ),
    )
    p_assess.set_defaults(func=cmd_assess)

    # --- quickstart ---
    p_qs = subparsers.add_parser("quickstart", help="60-second onboarding (create policy + first scan)")
    p_qs.add_argument("--project", "-p", default=".", help="Project directory")
    p_qs.add_argument("--org", default="My Organisation", help="Organisation name for policy file")
    p_qs.add_argument("--format", "-f", choices=["text", "json"], default="text")
    p_qs.set_defaults(func=cmd_quickstart)

    # --- feedback ---
    p_feedback = subparsers.add_parser(
        "feedback",
        help="Report a false positive, false negative, or bug (opens pre-filled GitHub Issue)",
    )
    feedback_sub = p_feedback.add_subparsers(dest="feedback_kind")

    p_fp = feedback_sub.add_parser("false-positive", help="Regula flagged code that is not a risk")
    p_fp.add_argument("--pattern", "-p", help="Pattern ID that was incorrectly flagged")
    p_fp.add_argument("--file", "-f", help="File where the false positive occurred")
    p_fp.add_argument("--line", "-l", type=int, help="Line number")
    p_fp.add_argument("--no-browser", action="store_true", help="Print URL instead of opening browser")
    p_fp.set_defaults(func=cmd_feedback, feedback_kind="false-positive")

    p_fn = feedback_sub.add_parser("false-negative", help="Regula missed a risk that should have been flagged")
    p_fn.add_argument("--pattern", "-p", help="Pattern ID that should have been flagged (if known)")
    p_fn.add_argument("--file", "-f", help="File where the risk exists")
    p_fn.add_argument("--line", "-l", type=int, help="Line number")
    p_fn.add_argument("--no-browser", action="store_true", help="Print URL instead of opening browser")
    p_fn.set_defaults(func=cmd_feedback, feedback_kind="false-negative")

    p_bug = feedback_sub.add_parser("bug", help="Regula crashed or behaved unexpectedly")
    p_bug.add_argument("--description", "-d", help="One-line description of what happened")
    p_bug.add_argument("--no-browser", action="store_true", help="Print URL instead of opening browser")
    p_bug.set_defaults(func=cmd_feedback, feedback_kind="bug")

    p_feedback.set_defaults(func=cmd_feedback, feedback_kind="false-positive")

    # --- telemetry ---
    p_telemetry = subparsers.add_parser("telemetry", help="Manage anonymous crash report consent")
    telemetry_sub = p_telemetry.add_subparsers(dest="telemetry_action")
    telemetry_sub.add_parser("status", help="Show current telemetry setting")
    telemetry_sub.add_parser("enable", help="Opt in to anonymous crash reports")
    telemetry_sub.add_parser("disable", help="Opt out of anonymous crash reports")
    p_telemetry.set_defaults(func=cmd_telemetry, telemetry_action="status")

    # --- config ---
    p_config = subparsers.add_parser("config", help="Config management (validate, etc.)")
    config_sub = p_config.add_subparsers(dest="config_action")

    p_config_validate = config_sub.add_parser("validate", help="Validate policy config file")
    p_config_validate.add_argument("--file", "-f", help="Path to config file (auto-discovers if omitted)")
    p_config_validate.add_argument("--format", choices=["text", "json"], default="text")
    p_config.set_defaults(func=cmd_config, config_action="validate")
    p_config_validate.set_defaults(func=cmd_config, config_action="validate")

    # --- oversight ---
    p_oversight = subparsers.add_parser(
        "oversight",
        help="Article 14 human oversight analysis (cross-file)",
    )
    p_oversight.add_argument("--project", "-p", default=".", help="Project directory to analyse")
    p_oversight.add_argument("--format", "-f", choices=["text", "json"], default="text")
    p_oversight.set_defaults(func=cmd_oversight)

    # --- owasp-agentic ---
    p_owasp = subparsers.add_parser(
        "owasp-agentic",
        help="OWASP Top 10 for Agentic Applications assessment",
    )
    p_owasp.add_argument("--project", "-p", default=".", help="Project directory to assess")
    p_owasp.add_argument("--format", "-f", choices=["text", "json"], default="text")
    p_owasp.add_argument("--strict", action="store_true", help="Exit 1 if any risk is at_risk")
    p_owasp.set_defaults(func=cmd_owasp_agentic)

    # --- guardrails ---
    p_guardrails = subparsers.add_parser(
        "guardrails",
        help="Detect guardrail implementation coverage (Art 15)",
    )
    p_guardrails.add_argument("--project", "-p", default=".", help="Project directory to scan")
    p_guardrails.add_argument("--format", "-f", choices=["text", "json"], default="text")
    p_guardrails.add_argument("--strict", action="store_true", help="Exit 1 if coverage < 50%%")
    p_guardrails.set_defaults(func=cmd_guardrails)

    # --- ai-codegen ---
    p_codegen = subparsers.add_parser(
        "ai-codegen",
        help="AI-generated code governance scanner (Art 50/52)",
    )
    p_codegen.add_argument("--project", "-p", default=".", help="Project directory to scan")
    p_codegen.add_argument("--format", "-f", choices=["text", "json"], default="text")
    p_codegen.add_argument("--no-git", action="store_true", help="Skip git log scanning")
    p_codegen.add_argument("--strict", action="store_true",
                           help="Exit 1 if transparency not compliant")
    p_codegen.set_defaults(func=cmd_ai_codegen)

    # --- badge ---
    p_badge = subparsers.add_parser("badge", help="Generate compliance badge")
    p_badge.add_argument("path", nargs="?", default=".", help="Path to scan")
    p_badge.add_argument("--format", "-f", choices=["endpoint", "svg", "markdown"], default="endpoint")
    p_badge.set_defaults(func=cmd_badge)

    # --- attest ---
    p_attest = subparsers.add_parser("attest", help="Generate scan attestation (in-toto v1)")
    p_attest.add_argument("path", nargs="?", default=".", help="Path to scan")
    p_attest.add_argument("--sign-key", help="HMAC-SHA256 signing key")
    p_attest.add_argument("--output", "-o", help="Output file path")
    p_attest.add_argument("--format", "-f", choices=["json"], default="json")
    p_attest.set_defaults(func=cmd_attest)

    # --- explain-article ---
    p_explain = subparsers.add_parser("explain-article", help="Plain-language EU AI Act article explainer")
    p_explain.add_argument("article", help="Article number (e.g. 5, 14, 50)")
    p_explain.add_argument("--format", choices=["text", "json"], default="text")
    p_explain.set_defaults(func=cmd_explain_article)


def _apply_env_defaults(args):
    """Apply environment variable defaults where CLI flags weren't set.

    Precedence: CLI flags > environment variables > argparse defaults.
    """
    # REGULA_FORMAT — applies to any subcommand with a --format arg
    env_format = os.environ.get('REGULA_FORMAT')
    if env_format and hasattr(args, 'format') and args.format == 'text':
        args.format = env_format

    # REGULA_STRICT — enable CI mode
    if not args.ci and os.environ.get('REGULA_STRICT', '').lower() in ('1', 'true', 'yes'):
        args.ci = True

    # REGULA_MIN_TIER
    env_min_tier = os.environ.get('REGULA_MIN_TIER')
    if env_min_tier and hasattr(args, 'min_tier') and not args.min_tier:
        args.min_tier = env_min_tier

    # REGULA_LANG — override only if user didn't pass --lang explicitly
    env_lang = os.environ.get('REGULA_LANG')
    if env_lang and args.lang == 'en':
        args.lang = env_lang

    # REGULA_SKIP_TESTS
    env_skip = os.environ.get('REGULA_SKIP_TESTS', '').lower()
    if env_skip in ('1', 'true', 'yes') and hasattr(args, 'skip_tests'):
        args.skip_tests = True
    elif env_skip in ('0', 'false', 'no') and hasattr(args, 'skip_tests'):
        args.skip_tests = False

    # REGULA_FRAMEWORK
    env_framework = os.environ.get('REGULA_FRAMEWORK')
    if env_framework and hasattr(args, 'framework') and not args.framework:
        args.framework = env_framework

    return args


def main(args=None):
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
    parser.add_argument("--version", action="version", version=f"regula {VERSION}")

    subparsers = parser.add_subparsers(dest="command")
    _build_subparsers(subparsers)

    args = parser.parse_args(args)
    _apply_env_defaults(args)

    # Telemetry: prompt on first run, then init Sentry if consented.
    # Skip prompt when user is explicitly managing telemetry settings.
    from telemetry import prompt_consent_if_needed, init_sentry
    if args.command != "telemetry":
        prompt_consent_if_needed()
    init_sentry()

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
        try:
            import sentry_sdk
            sentry_sdk.capture_exception(e)
        except Exception:
            pass
        print(f"Internal error: {e}", file=sys.stderr)
        print("This is a bug in Regula. Please report it at https://github.com/kuzivaai/getregula/issues", file=sys.stderr)
        print("Or run: regula feedback --bug \"<description>\"", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
