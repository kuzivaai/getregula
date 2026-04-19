"""Governance commands for Regula CLI.

NOTE: Do NOT add 'from cli import ...' at module level.
cli.py imports this module at module level, creating a circular dependency.
All imports from cli must stay inside function bodies.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


def cmd_governance(args) -> None:
    """Generate AI governance scaffold."""
    from cli import json_output, _validate_path
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


def cmd_agent(args) -> None:
    """Agentic AI governance monitoring."""
    from cli import json_output
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


def cmd_oversight(args) -> None:
    """Article 14 human oversight analysis (cross-file)."""
    from cli import json_output
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

    # Handle not-analysed case (e.g. JS/TS-only project, no Python files)
    if not result.get("analysed", True):
        reason = result.get(
            "reason", "Analysis could not be performed"
        )
        print(f"  {reason}")
        note = summary.get("note", "")
        if note:
            print(f"  {note}")
        print()
        print("No oversight score computed \u2014 analysis did not run.")
        return

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


def cmd_model_card(args) -> None:
    """Generate model card scaffold."""
    from cli import json_output, _validate_path
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


def cmd_register(args) -> None:
    """Generate an Annex VIII registration packet for a project (Article 49)."""
    import os
    from cli import (
        json_output, _validate_path, _highest_annex_iii_point,
        _read_code_blob, _print_register_text,
    )
    from errors import PathError
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
        except (OSError, ValueError, KeyError, TypeError, AttributeError) as e:
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


def cmd_disclose(args) -> None:
    """Generate Article 50 transparency disclosures."""
    from cli import json_output
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


def cmd_feedback(args) -> None:
    """Open a pre-filled GitHub Issue to report a false positive, false negative, or bug."""
    import os
    from constants import VERSION
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
    print("Opening GitHub Issue in browser...")
    print(f"URL: {url}")
    print(note)
    webbrowser.open(url)


def cmd_handoff(args) -> None:
    """Emit a red-team config file for Garak, Giskard, or Promptfoo."""
    from cli import json_output, _validate_path
    from pathlib import Path as _Path
    from handoff import run_handoff
    _validate_path(args.project)
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


def cmd_feedback_summary(args) -> None:
    """Show a summary of local feedback events from ~/.regula/feedback.json."""
    from cli import json_output
    from risk_decisions import load_feedback

    records = load_feedback()
    fmt = getattr(args, "format", "text")

    # Aggregate
    by_kind: dict[str, int] = {}
    by_pattern: dict[str, int] = {}
    pattern_detail: dict[str, dict[str, int]] = {}  # pattern -> {ignore: N, accept: N}

    for r in records:
        kind = r.get("kind", "unknown")
        by_kind[kind] = by_kind.get(kind, 0) + 1

        pattern = r.get("pattern", "*")
        if kind in ("suppress", "accept"):
            by_pattern[pattern] = by_pattern.get(pattern, 0) + 1
            if pattern not in pattern_detail:
                pattern_detail[pattern] = {"ignore": 0, "accept": 0}
            if kind == "suppress":
                pattern_detail[pattern]["ignore"] += 1
            elif kind == "accept":
                pattern_detail[pattern]["accept"] += 1

    total = len(records)
    false_positives = by_kind.get("false-positive", 0)
    suppressions = by_kind.get("suppress", 0) + by_kind.get("accept", 0)

    # Sort patterns by count descending
    most_suppressed = sorted(by_pattern.items(), key=lambda x: -x[1])

    if fmt == "json":
        json_output("feedback-summary", {
            "total_events": total,
            "by_kind": by_kind,
            "by_pattern": by_pattern,
            "most_suppressed": most_suppressed,
        })
        return

    # Text output
    print()
    print("Feedback Summary")
    print("=" * 60)
    print(f"  {'Total feedback events:':<28}{total}")
    print(f"  {'False positives reported:':<28}{false_positives}")
    print(f"  {'Suppressions recorded:':<28}{suppressions}")

    if most_suppressed:
        print()
        print("  Most suppressed patterns:")
        for pattern, count in most_suppressed[:10]:
            detail = pattern_detail.get(pattern, {})
            ignore_n = detail.get("ignore", 0)
            accept_n = detail.get("accept", 0)
            parts = []
            if ignore_n:
                parts.append(f"{ignore_n} ignore")
            if accept_n:
                parts.append(f"{accept_n} accept")
            detail_str = f" ({', '.join(parts)})" if parts else ""
            print(f"    {pattern:<24}{count} times{detail_str}")

    # Patterns with 0 suppressions (from all known feedback patterns)
    all_suppressed_patterns = set(by_pattern.keys())
    all_feedback_patterns = set()
    for r in records:
        p = r.get("pattern", "")
        if p and p != "*":
            all_feedback_patterns.add(p)
    unsuppressed = all_feedback_patterns - all_suppressed_patterns
    if unsuppressed:
        print()
        print("  Patterns with 0 suppressions (high signal):")
        print(f"    {', '.join(sorted(unsuppressed))}")

    print("=" * 60)
