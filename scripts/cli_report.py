"""Reporting commands for Regula CLI.

NOTE: Do NOT add 'from cli import ...' at module level.
cli.py imports this module at module level, creating a circular dependency.
All imports from cli must stay inside function bodies.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


def cmd_report(args) -> None:
    """Generate reports."""
    from cli import json_output, _validate_path, _build_envelope
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
            pass  # audit trail unavailable; continue without it

    if args.format == "html":
        content = generate_html_report(findings, project_name, audit_events, chain_valid)
    elif args.format == "sales":
        content = generate_sales_report(findings, project_name)
    elif args.format == "sarif":
        content = json.dumps(generate_sarif(findings, project_name), indent=2)
    else:
        # JSON format — wrap in standard envelope
        envelope = _build_envelope("report", findings)
        content = json.dumps(envelope, indent=2, default=str)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(content, encoding="utf-8")
        print(f"Report written to {out_path}", file=sys.stderr)
    else:
        print(content)


def cmd_evidence_pack(args) -> None:
    """Generate compliance evidence pack."""
    from cli import json_output, _validate_path

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
        runtime_system_id=getattr(args, "runtime", None),
    )

    if getattr(args, "bundle", False):
        from evidence_pack import generate_bundle
        bundle_path = generate_bundle(result["pack_path"])
        if args.format == "json":
            result["bundle_path"] = bundle_path
            json_output("evidence-pack", result)
        else:
            print(f"Evidence bundle written to: {bundle_path}")
            print(f"Verify with: unzip {Path(bundle_path).name} -d verify && cd verify && python3 verify.py")
        return

    if args.format == "json":
        json_output("evidence-pack", result)
    else:
        pack_path = result["pack_path"]
        file_count = len(result["manifest"]["files"])
        print(f"Evidence pack written to: {pack_path}")
        print(f"Contains {file_count} files with SHA-256 integrity hashes.")
        print(f"Start with: {pack_path}/00-summary.md")


def cmd_sbom(args) -> None:
    """Generate AI Software Bill of Materials (CycloneDX 1.7)."""
    from cli import json_output, _validate_path

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


def cmd_benchmark(args) -> None:
    """Run real-world validation benchmark."""
    from cli import json_output, _build_envelope
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
        content = json.dumps(_build_envelope("benchmark", results), indent=2, default=str)
    else:
        content = format_benchmark_text(results)

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(content, encoding="utf-8")
        print(f"Benchmark output written to {args.output}", file=sys.stderr)
    else:
        print(content)


def cmd_inventory(args) -> None:
    """Scan codebase for AI model references with GPAI tier annotations."""
    from cli import json_output, _validate_path
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


def cmd_badge(args) -> None:
    """Generate compliance badge from scan results."""
    from cli import json_output, _validate_path
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


def cmd_aibom(args) -> None:
    """Generate AI Bill of Materials."""
    from cli import json_output, _validate_path
    from aibom import generate_aibom, format_cyclonedx, format_aibom_markdown

    if args.project != ".":
        _validate_path(args.project)
    project_path = str(Path(args.project).resolve())

    result = generate_aibom(project_path)

    if args.format == "json":
        json_output("aibom", result)
    elif args.format == "cyclonedx":
        import json as _json
        print(_json.dumps(format_cyclonedx(result), indent=2))
    elif args.format == "markdown":
        print(format_aibom_markdown(result))
    else:
        # Default text output
        components = result["components"]
        if not components:
            print(f"No AI components found in {project_path}")
            return
        print(f"\n  AI Bill of Materials — {Path(project_path).name}\n")
        print(f"  {'Component':<30s} {'Kind':<20s} {'Version':<12s} {'Files':>5s}")
        print(f"  {'─' * 30} {'─' * 20} {'─' * 12} {'─' * 5}")
        for c in components:
            print(f"  {c['name']:<30s} {c['kind']:<20s} {c.get('version', '?'):<12s} {len(c['files']):>5d}")
        summary = result["summary"]
        print(f"\n  {summary['total_components']} AI component(s) across {len(summary['kinds'])} kind(s)")
        print("  Note: AI BOM supports Annex IV/XI documentation — it is not a regulatory requirement.\n")


def cmd_doc_audit(args) -> None:
    """Score compliance document quality."""
    from cli import json_output, _validate_path
    from doc_audit import audit_project

    if args.project != ".":
        _validate_path(args.project)
    project_path = str(Path(args.project).resolve())
    results = audit_project(project_path)

    if args.format == "json":
        json_output("doc-audit", {"documents": results, "project": project_path})
        return

    if not results:
        print(f"No compliance documents found in {project_path}")
        print("Expected files like: RISK_MANAGEMENT.md, TRANSPARENCY.md, etc.")
        print("Run 'regula docs --project .' to generate templates.")
        return

    print(f"\n  Document Quality Audit — {project_path}\n")
    print(f"  {'Document':<35s} {'Article':<35s} {'Score':>5s}  {'Cov':>4s}  {'Dep':>4s}  {'Str':>4s}")
    print(f"  {'─' * 35} {'─' * 35} {'─' * 5}  {'─' * 4}  {'─' * 4}  {'─' * 4}")
    for r in results:
        print(f"  {r['filename']:<35s} {r.get('article_name', ''):<35s} {r['total']:>5d}  {r['coverage']:>4d}  {r['depth']:>4d}  {r['structure']:>4d}")
        if r["gaps"]:
            for gap in r["gaps"][:3]:
                print(f"    ↳ {gap}")
    avg = sum(r["total"] for r in results) / len(results) if results else 0
    print(f"\n  Average score: {avg:.0f}/100 across {len(results)} document(s)")
    print("  Note: scores reflect structural completeness, not semantic adequacy.\n")
