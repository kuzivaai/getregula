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
    from cli import _validate_path, _build_envelope
    from report import scan_files, generate_html_report, generate_sarif, generate_sales_report
    from exec_summary import generate_exec_summary

    if hasattr(args, 'project') and args.project != ".":
        _validate_path(args.project)

    project_path = str(Path(args.project).resolve())
    project_name = args.name or Path(project_path).name

    declared_domains = set()
    if getattr(args, "domain", None):
        declared_domains = {d.strip().lower() for d in args.domain.split(",")}

    print(f"Scanning {project_path}...", file=sys.stderr)
    findings = scan_files(project_path, declared_domains=declared_domains)
    if getattr(args, "scope", "all") == "production":
        # Same tier-aware exclusion `regula check` uses (single source).
        from cli_scan import _should_exclude_for_production_scope
        excluded = [f for f in findings if _should_exclude_for_production_scope(f)]
        if excluded:
            print(f"  Scope: {len(excluded)} non-production finding(s) excluded "
                  f"(--scope all to include)", file=sys.stderr)
            findings = [f for f in findings if not _should_exclude_for_production_scope(f)]
    print(f"Found {len(findings)} findings in {len(set(f['file'] for f in findings))} files", file=sys.stderr)

    audit_events = None
    chain_valid = None
    if args.include_audit:
        try:
            # Project-scoped: never embed other projects' audit events
            from log_event import collect_audit_trail
            _audit = collect_audit_trail(project_path)
            audit_events = _audit["events"]
            chain_valid = _audit["chain_valid"]
        except (OSError, ValueError, KeyError):
            pass  # audit trail unavailable; continue without it

    if args.format == "html":
        content = generate_html_report(findings, project_name, audit_events, chain_valid)
    elif args.format == "exec-summary":
        from engagement import load_engagement, engagement_from_args
        engagement = load_engagement(overrides=engagement_from_args(args),
                                     project_path=project_path)
        content = generate_exec_summary(findings, project_name,
                                        engagement=engagement)
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

    # Same flag semantics as `regula conform`: --signing-key and
    # --timestamp both imply --sign.
    timestamp_requested = bool(getattr(args, "timestamp", False))
    sign_requested = bool(
        getattr(args, "sign", False)
        or getattr(args, "signing_key", None)
        or timestamp_requested
    )
    signing_key_path = None
    if getattr(args, "signing_key", None):
        signing_key_path = Path(args.signing_key).expanduser().resolve()

    from engagement import load_engagement, engagement_from_args
    engagement = load_engagement(overrides=engagement_from_args(args),
                                 project_path=project_path)

    print(f"Generating evidence pack for {project_path}...", file=sys.stderr)
    try:
        result = generate_evidence_pack(
            project_path,
            output_dir=args.output,
            project_name=project_name,
            runtime_system_id=getattr(args, "runtime", None),
            include_dpv=getattr(args, "dpv", False),
            sign=sign_requested,
            signing_key_path=signing_key_path,
            timestamp=timestamp_requested,
            tsa_url=getattr(args, "tsa_url", None),
            engagement=engagement,
        )
    except ImportError as exc:
        # Malformed install where signing.py or timestamp.py is absent.
        print(
            f"Signing/timestamping unavailable: {exc}\n\n"
            f"Install the signing extra:\n"
            f"  Install the signing extra from the reviewed source.\n"
            f"  See docs/installation.md.",
            file=sys.stderr,
        )
        sys.exit(2)
    except Exception as exc:
        # SigningUnavailable, SigningError, TimestampUnavailable,
        # TimestampError, or an invalid flag combination (ValueError) —
        # actionable one-liner, not a stack trace. Same handling as
        # `regula conform` (cli_compliance.cmd_conform); class names are
        # matched by string so the core CLI stays stdlib-only when the
        # optional extras are not installed.
        name = exc.__class__.__name__
        if name in (
            "SigningUnavailable", "SigningError",
            "TimestampUnavailable", "TimestampError",
        ):
            kind = "Timestamping" if name.startswith("Timestamp") else "Signing"
            print(f"{kind} failed: {exc}", file=sys.stderr)
            sys.exit(2)
        if isinstance(exc, ValueError):
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(2)
        raise

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
        if sign_requested:
            ts_note = " + RFC 3161 timestamp" if timestamp_requested else ""
            print(f"Signed: Ed25519 signature embedded{ts_note} "
                  f"(verify with `regula verify {pack_path}`).")
        else:
            print("\n  For a signed, timestamped evidence pack suitable for auditors,")
            print("  run: regula evidence-pack --sign . (or visit getregula.com/pricing)")


def cmd_sbom(args) -> None:
    """Generate AI Software Bill of Materials (CycloneDX 1.7)."""
    from cli import _validate_path

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


def cmd_dpv(args) -> None:
    """Export risk indication as DPV-AIAct JSON-LD.

    Aligned to the DPVCG EU-AIAct vocabulary (a W3C Community Group report,
    not a ratified W3C Standard). This is risk indication, not classification.
    """
    from cli import _validate_path

    project = getattr(args, "project_path_positional", None) or args.project
    if project != ".":
        _validate_path(project)
    from dpv_export import generate_dpv_export, format_dpv_jsonld
    doc = generate_dpv_export(project, project_name=getattr(args, "name", None))
    content = format_dpv_jsonld(doc)
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(content, encoding="utf-8")
        print(f"DPV-AIAct export written to {args.output}", file=sys.stderr)
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


# A badge is the one output designed to be pasted into a third party's README,
# where it travels with no disclaimer and carries an implied endorsement from
# this project. Until 2026-08-17 this function put the REGULATION's name in the
# label and a COMPLIANCE STATE in the message, coloured brightgreen, whenever a
# scan produced no prohibited and no high-risk findings. On a directory
# containing only `print('hello')` that rendered a pasteable badge asserting EU
# AI Act compliance, which project policy prohibits. The former output is
# described and not quoted here,
# because quoting it reintroduces it. `determination_guard.py` fired on the
# first draft of this very comment, which is the third occurrence of the
# same self-inflicted documentation trap.
#
# The determination never came from the badge mechanism. It came from two
# choices: naming the REGULATION in the label, and naming a COMPLIANCE STATE in
# the message. Both are removed. The label names the tool, so the badge can only
# say what this scan did, and the message reports an indicator count, which is a
# fact about the scan rather than a conclusion about the law.
#
# BADGE_CAVEAT_URL is load-bearing rather than decorative. The objection to a
# badge is that it detaches from every qualification on the page that generated
# it, so the qualification is attached to the badge itself, as its link target.
BADGE_LABEL = "regula"
BADGE_CAVEAT_URL = (
    "https://github.com/kuzivaai/getregula/blob/main/docs/what-regula-does-not-do.md"
)
# Deliberately NOT brightgreen for the zero case. A green badge beside a
# regulation's name is read as a pass whatever the message says, and green is
# what made the old output dangerous. Grey reports without commending.
BADGE_NEUTRAL_COLOUR = "lightgrey"


def cmd_badge(args) -> None:
    """Render a scan-result badge: an indicator count, never a compliance state."""
    from cli import _validate_path
    from report import scan_files
    from findings_view import partition_findings

    _validate_path(args.path)
    project = str(Path(args.path).resolve())
    findings = scan_files(project)

    view = partition_findings(findings)
    prohibited = view["prohibited"]
    high_risk = view["high_risk"]

    def _plural(n: int) -> str:
        return "indicator" if n == 1 else "indicators"

    if prohibited:
        color = "red"
        message = f"{len(prohibited)} prohibited-pattern {_plural(len(prohibited))}"
    elif high_risk:
        color = "orange"
        message = f"{len(high_risk)} high-risk-pattern {_plural(len(high_risk))}"
    else:
        color = BADGE_NEUTRAL_COLOUR
        message = "no indicators found"

    if args.format == "endpoint":
        badge = {
            "schemaVersion": 1,
            "label": BADGE_LABEL,
            "message": message,
            "color": color,
        }
        print(json.dumps(badge, indent=2))
    elif args.format == "svg":
        label = BADGE_LABEL
        label_width = len(label) * 7 + 10
        msg_width = len(message) * 7 + 10
        total_width = label_width + msg_width
        # Only the three states this function can produce. The green entry was
        # still in this map after the message stopped asserting a state, so the
        # capability to render a green pass outlived the removal of the words,
        # and BADGE_NEUTRAL_COLOUR was resolving through the fallback by accident
        # rather than by name. `fill = colors[color]` now raises on an unknown
        # state instead of quietly substituting grey. Caught by
        # tests/test_determination_guard.py, not by reading.
        colors = {
            BADGE_NEUTRAL_COLOUR: "#9f9f9f",
            "orange": "#fe7d37",
            "red": "#e05d44",
        }
        fill = colors[color]
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
        # Markdown snippet. The link goes to the limitations document, not the
        # marketing homepage, so a reader who clicks the badge in someone else's
        # README lands on what Regula does not do.
        shield_url = (
            f"https://img.shields.io/badge/{BADGE_LABEL}-"
            f"{message.replace(' ', '%20')}-{color}"
        )
        print(f"[![{BADGE_LABEL} scan result]({shield_url})]({BADGE_CAVEAT_URL})")


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
