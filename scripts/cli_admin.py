"""Admin, registry, and operational commands for Regula CLI.

Covers: status, audit, session, timeline, regwatch, feed,
api-server, mcp-server.

NOTE: Do NOT add 'from cli import ...' at module level.
cli.py imports this module (via cli_util) at module level, creating a
circular dependency. All imports from cli must stay inside function bodies.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


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
                print("  Findings:")
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
    # --project scopes to one project's audit chain; default is the
    # whole machine (machine store + every project chain).
    project = getattr(args, "audit_project", None)

    if subcommand == "log":
        data = json.loads(args.data) if getattr(args, "data", None) else {}
        ext_ts = getattr(args, "external_timestamp", False)
        event = _log(args.event_type, data, external_timestamp=ext_ts,
                     project_path=project)
        json_output("audit log", {"status": "logged", "event_id": event.event_id})
    elif subcommand == "query":
        events = query_events(
            getattr(args, "event_type", None),
            getattr(args, "after", None),
            getattr(args, "before", None),
            getattr(args, "limit", 100),
            project_path=project,
        )
        json_output("audit query", events)
    elif subcommand == "export":
        events = query_events(
            getattr(args, "event_type", None),
            getattr(args, "after", None),
            getattr(args, "before", None),
            limit=100000,
            project_path=project,
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
        valid, error = verify_chain(project_path=project)
        json_output("audit verify", {"status": "valid" if valid else "invalid", "error": error},
                    exit_code=0 if valid else 1)
        if not valid:
            sys.exit(1)
    else:
        print(f"Unknown audit subcommand: {subcommand}", file=sys.stderr)
        sys.exit(2)


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


def cmd_api_server(args) -> None:
    """Start the Regula REST API server with web dashboard."""
    from api_server import main as run_api
    import sys
    # Pass through CLI args to api_server's argparse
    api_args = []
    if hasattr(args, 'port') and args.port:
        api_args.extend(['--port', str(args.port)])
    if hasattr(args, 'host') and args.host:
        api_args.extend(['--host', args.host])
    sys.argv = ['regula api-server'] + api_args
    run_api()


def cmd_mcp_server(args) -> None:
    """Start the Regula MCP server over stdio."""
    from mcp_server import run_server
    run_server()
