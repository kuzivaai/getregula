"""Scanning commands for Regula CLI.

NOTE: Do NOT add 'from cli import ...' at module level.
cli.py imports this module at module level, creating a circular dependency.
All imports from cli must stay inside function bodies.
"""

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


def _should_exclude_for_production_scope(finding: dict) -> bool:
    """Determine if a finding should be excluded in --scope production.

    Tier-aware rules (each traceable to why exclusion is safe or unsafe):

    - prohibited: NEVER exclude. A prohibited practice in a test file is
      still a prohibited practice — Article 5 has no test-code exemption.
    - credential_exposure: NEVER exclude. Real credentials in test files
      are a genuine security risk.
    - __init__.py: exclude only for minimal_risk. An __init__.py can
      legitimately wire up a high-risk biometric pipeline (e.g.
      deepface/__init__.py re-exports face verification functions).
    - example: exclude only for non-minimal tiers. Per LABELLING_CRITERIA
      context rule 1, example code that demonstrates real AI usage IS a
      finding — it teaches patterns users will replicate. But example
      code flagged as high_risk/agent_autonomy is less actionable.
    - All other non-production provenance + non-exempt tiers: exclude.
    """
    tier = finding.get("tier", "")
    provenance = finding.get("provenance", "production")

    # Never exclude prohibited or credential findings
    if tier in ("prohibited", "credential_exposure"):
        return False

    # Production files are never excluded
    if provenance == "production":
        return False

    # Tooling provenance with tier-dependent rules:
    # - __init__.py: exclude only for minimal_risk (can wire high-risk pipelines)
    # - types/ directories: exclude only for minimal_risk (type defs are
    #   structural, but a types/ dir could contain validation logic for high-risk)
    # - _utils/ directories: exclude only for minimal_risk (utility code,
    #   but could contain functional logic in high-risk contexts)
    # - setup.py, CI, build files: exclude for all non-exempt tiers
    filepath = finding.get("file", "")
    if provenance == "tooling":
        _is_structural = (
            filepath.endswith("__init__.py")
            or "/types/" in filepath or "\\types\\" in filepath
            or "/_utils/" in filepath or "\\_utils\\" in filepath
        )
        if _is_structural:
            return tier == "minimal_risk"
        # Non-structural tooling (setup.py, CI, build): exclude for all
        return True

    # Example code: keep for minimal_risk (demonstrates real AI usage),
    # exclude for other tiers (less actionable for compliance)
    if provenance == "example":
        return tier != "minimal_risk"

    # All other non-production provenance (test, documentation): exclude
    return True


# Mapping from Regula's display tier to GitHub Actions workflow command level.
# ::error     — surfaces as a red annotation on the file/line in PR diffs
# ::warning   — yellow annotation
# ::notice    — blue/informational annotation
_GHA_LEVEL = {"block": "error", "warn": "warning", "info": "notice"}


def _gha_escape(value: str) -> str:
    """Percent-encode characters that break GitHub workflow-command parsing.

    Workflow commands are terminated by a newline, so CR/LF must be escaped.
    Colons and commas inside parameter *values* (file path) are escaped too —
    the message itself only needs CR/LF escaping.
    See: https://docs.github.com/actions/reference/workflow-commands-for-github-actions
    """
    return (
        value.replace("%", "%25")
        .replace("\r", "%0D")
        .replace("\n", "%0A")
    )


def _emit_github_annotations(args, display_view) -> None:
    """Emit one workflow command per finding when running in GitHub Actions.

    Activates only when GITHUB_ACTIONS=true AND --ci (or REGULA_STRICT) is set,
    so local runs and non-CI environments stay quiet. SARIF output remains
    available via --format sarif for repos that want CodeQL integration.
    """
    if os.environ.get("GITHUB_ACTIONS", "").lower() != "true":
        return
    if not getattr(args, "ci", False):
        return

    scan_root = Path(getattr(args, "path", ".") or ".")

    def _as_repo_path(rel: str) -> str:
        # Finding paths are relative to the scan root. Prepend scan root so
        # GitHub can resolve the file in the repo checkout.
        if not rel:
            return ""
        if rel.startswith(str(scan_root)) or Path(rel).is_absolute():
            return rel
        joined = scan_root / rel if str(scan_root) not in ("", ".") else Path(rel)
        return str(joined).replace("\\", "/")

    for display_tier in ("block", "warn", "info"):
        level = _GHA_LEVEL[display_tier]
        for finding in display_view.get(display_tier, []):
            file_path = _gha_escape(_as_repo_path(finding.get("file", "")))
            line = finding.get("line") or 1
            msg = finding.get("description") or finding.get("message") or ""
            score = finding.get("confidence_score")
            if score is not None:
                msg = f"{msg} (confidence: {score})"
            msg = _gha_escape(msg)
            # stdout, not stderr — GitHub Actions parses workflow commands
            # from either stream, but stdout is the documented default.
            print(f"::{level} file={file_path},line={line}::{msg}")


def _write_analysis_manifest(
    manifest_path: str,
    *,
    scan_target: str,
    started_at: str,
    view: dict,
    scan_stats: dict | None,
    sarif_path: str | None,
    exit_code: int,
) -> None:
    """Write an AnalysisManifest JSON proving the scan completed.

    Rationale (DEF-004): a CI gate cannot safely treat "0 findings" as PASS
    unless it can independently confirm the scan actually ran to completion.
    This manifest is the completion signal. It is written ONLY here, after the
    scan and any artifact write succeeded; if the scan raises earlier, the file
    is never created, and its ABSENCE is the failure signal for the action.

    Completion is TWO-tier (review findings F1-F5):
      - "completed"            : every eligible code file was fully analysed.
      - "completed_with_skips" : the scan finished, but one or more eligible
                                 code files could not be fully analysed —
                                 unreadable, undecodable (non-UTF-8), a corrupt
                                 notebook, or a notebook with undropped-able
                                 code cells. A prohibited pattern could hide in
                                 such a file, so a strict CI gate MUST treat
                                 this as not-clean and fail closed rather than
                                 trust "0 findings". Legitimate exclusions
                                 (non-code files, type stubs, empty-but-valid
                                 files, test files under skip_tests) are NOT
                                 skips and do not downgrade the status.

    Counts sourced from the findings partition are exact. Per-file counts come
    from scan_files.last_stats where available; anything genuinely unmeasured
    is recorded as null (explicitly unknown) rather than fabricated.
    """
    from datetime import datetime, timezone
    from constants import VERSION

    sarif_sha256 = None
    if sarif_path:
        try:
            import hashlib
            sarif_sha256 = hashlib.sha256(
                Path(sarif_path).read_bytes()
            ).hexdigest()
        except OSError:
            sarif_sha256 = None  # SARIF unreadable — leave null, do not guess

    stats = scan_stats or {}
    scanned = stats.get("files_scanned")
    skipped_files = stats.get("skipped_files", []) or []
    skipped_total = stats.get("skipped_total", len(skipped_files)) or 0

    # Break the skip reasons down so the gate/report can explain WHY a scan is
    # partial (unreadable / undecodable / notebook_corrupt / notebook_partial).
    skip_reasons: dict = {}
    for entry in skipped_files:
        reason = entry.get("reason", "unknown") if isinstance(entry, dict) else "unknown"
        skip_reasons[reason] = skip_reasons.get(reason, 0) + 1

    # F1: any eligible code file that could not be fully analysed makes this a
    # PARTIAL scan — "0 findings" cannot be trusted to cover it.
    completion_status = "completed_with_skips" if skipped_total > 0 else "completed"

    # maint-F5: Derive manifest tier counts programmatically instead of hardcoding.
    tier_counts: dict[str, int] = {
        "prohibited": 0,
        "high_risk": 0,
        "credential_exposure": 0,
        "limited_risk": 0,
        "minimal_risk": 0,
        "agent_autonomy": 0,
        "ai_security": 0,
    }
    active = view.get("active", [])
    for f in active:
        t = f.get("tier", "unknown")
        tier_counts[t] = tier_counts.get(t, 0) + 1

    manifest = {
        "manifest_version": "3",
        "regula_version": VERSION,
        "scan_target": scan_target,
        "started_at": started_at,
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "completion_status": completion_status,
        "exit_code": exit_code,
        "counts": {
            # Measured by scan_files(); null only if stats were unavailable.
            "scanned": scanned,
            "skipped_total": skipped_total,
            "skip_reasons": skip_reasons,
            # Not yet measured — recorded null, never fabricated.
            "discovered": None,
            "eligible": None,
            "unsupported": None,
            # Exact, from the findings partition.
            "findings_total": len(active),
            "suppressed": len(view.get("suppressed", [])),
            **tier_counts,
        },
        # Bounded so a pathological repo cannot bloat the manifest.
        "skipped_files": sorted(
            skipped_files,
            key=lambda e: e.get("path", "") if isinstance(e, dict) else str(e),
        )[:100],
        "sarif_sha256": sarif_sha256,
    }
    out = Path(manifest_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"Analysis manifest written to {out}", file=sys.stderr)


def cmd_check(args) -> None:
    """Scan files for risk indicators."""
    from datetime import datetime, timezone
    _manifest_started_at = datetime.now(timezone.utc).isoformat()
    _sarif_written_path = None
    from cli import (
        json_output, _validate_path, _get_changed_files,
        _resolve_jurisdictions, _enrich_findings_with_jurisdictions,
        _enrich_findings_with_domain_obligations,
        _print_remediation,
    )
    from report import scan_files

    # F2: --manifest is only honoured for scan-output formats. Warn loudly if
    # combined with a mode that exits early and cannot produce one, so a CI
    # author is never silently misled into a missing-manifest fail-closed loop.
    if getattr(args, "manifest", None) and (
        getattr(args, "audit_suppressions", False) or args.format == "html"
    ):
        _mode = "--audit-suppressions" if getattr(args, "audit_suppressions", False) else "--format html"
        print(
            f"Warning: --manifest is not written for {_mode}; use --format "
            f"text/json/sarif to get a completion manifest.",
            file=sys.stderr,
        )

    _validate_path(args.path)
    project = str(Path(args.path).resolve())
    declared_domains = set()
    if getattr(args, "domain", None):
        declared_domains = {d.strip().lower() for d in args.domain.split(",")}
    findings = scan_files(
        project,
        respect_ignores=not args.no_ignore,
        skip_tests=getattr(args, "skip_tests", False),
        min_tier=getattr(args, "min_tier", "") or "",
        declared_domains=declared_domains,
    )
    # Capture scan statistics immediately (side-channel on the function).
    # Used to record honest scanned/skipped counts in the completion
    # manifest so a PARTIAL scan cannot masquerade as clean (review F1).
    _scan_stats = dict(getattr(scan_files, "last_stats", {}) or {})

    # Scope filtering: exclude non-production files when --scope production.
    # Tier-aware: prohibited and credential_exposure findings are NEVER
    # excluded (a real credential in a test file is still dangerous; a
    # prohibited practice in any file must be flagged). __init__.py files
    # are excluded only for minimal_risk (they can wire high-risk pipelines).
    scope = getattr(args, "scope", "production")
    _scope_excluded = []
    if scope == "production":
        kept = []
        for f in findings:
            if _should_exclude_for_production_scope(f):
                _scope_excluded.append(f)
            else:
                kept.append(f)
        if _scope_excluded:
            print(f"  Scope: {len(_scope_excluded)} non-production finding(s) excluded "
                  f"(--scope all to include)", file=sys.stderr)
        findings = kept

    # GDPR dual-compliance patterns: merge into findings when requested
    if getattr(args, "include_gdpr", False):
        from gdpr_scan import scan_gdpr
        gdpr_result = scan_gdpr(project, scope=scope)
        findings.extend(gdpr_result["findings"])

    # Diff mode: filter findings to only changed files
    if args.diff:
        changed = _get_changed_files(project, args.diff)
        if changed:
            findings = [f for f in findings if f.get("file", "") in changed]
            print(f"  Diff mode: {len(changed)} files changed since {args.diff}", file=sys.stderr)
        else:
            print(f"  Diff mode: no changed files found since {args.diff} (showing all)", file=sys.stderr)

    # Lifecycle phase filter: keep only findings matching the requested phase
    lifecycle_filter = getattr(args, "lifecycle", None)
    if lifecycle_filter:
        findings = [f for f in findings if lifecycle_filter in f.get("lifecycle_phases", [])]

    # Multi-jurisdiction mapping: enrich findings with cross-framework labels
    jurisdiction_pairs = []
    if getattr(args, "jurisdictions", None):
        jurisdiction_pairs = _resolve_jurisdictions(args.jurisdictions)
        if jurisdiction_pairs:
            _enrich_findings_with_jurisdictions(findings, jurisdiction_pairs)
            _enrich_findings_with_domain_obligations(findings, jurisdiction_pairs)

    # Partition findings via the pure function in findings_view.
    # This used to be 16 inlined lines mutating the input list; the
    # extraction lets us unit-test the partition (test_findings_view.py)
    # without going through the CLI.
    from findings_view import partition_findings
    _view = partition_findings(findings)
    active = _view["active"]
    suppressed = _view["suppressed"]
    accepted = _view.get("accepted", [])
    prohibited = _view["prohibited"]
    credentials = _view["credentials"]
    high_risk = _view["high_risk"]
    limited = _view["limited"]
    autonomy = _view["autonomy"]
    block_findings = _view["block"]
    warn_findings = _view["warn"]
    info_findings = _view["info"]

    # Compute the exit code ONCE, here, before any output format branch, so
    # every format (json/sarif/html/text) reports the SAME verdict via BOTH
    # the process exit code AND any exit_code field embedded in machine-
    # readable output. Previously, --format json's envelope always hardcoded
    # exit_code=0 regardless of findings, while the real process exit code
    # (computed separately, later) correctly reflected block/warn findings —
    # a single JSON response could assert two contradictory outcomes
    # depending on which field a consumer checked. Any automation reading
    # the JSON body's exit_code field (a natural thing to do, since the
    # field exists specifically for that purpose) would be silently misled
    # into treating a prohibited/high-risk finding as a clean pass.
    strict = args.strict or getattr(args, "ci", False)
    if block_findings:
        _exit_code = 1
    elif warn_findings and strict:
        _exit_code = 1
    else:
        _exit_code = 0

    # --audit-suppressions: list all annotations with status (ISO 42001 9.1)
    if getattr(args, "audit_suppressions", False):
        _print_suppression_audit(findings)
        issues = [f for f in findings
                  if f.get("risk_decision") and (
                      f["risk_decision"].get("warning")
                      or f["risk_decision"].get("error")
                      or f["risk_decision"].get("overdue")
                  )]
        sys.exit(1 if issues else 0)

    # Record scan metrics with per-pattern breakdown (best-effort)
    try:
        from metrics import record_scan as _record_scan
        # Pass full findings so metrics can track per-pattern stats
        _record_scan(findings)
    except Exception:
        pass  # scan telemetry is best-effort; don't block output

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
        # Reuse the shared _exit_code (computed once, above) rather than a
        # narrower local check — this branch previously ignored
        # warn_findings+--strict/--ci, exiting 0 in a case where every
        # other format (text/json/sarif) correctly exits 1.
        sys.exit(_exit_code)
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
                    continue  # file unreadable; skip
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
            json_output("check", {"findings": findings, "explanations": explained}, exit_code=_exit_code, deterministic=det)
        else:
            # Sort findings for deterministic output
            findings.sort(key=lambda f: (f.get('file', ''), f.get('line', 0), f.get('pattern', '')))
            det = getattr(args, 'deterministic', False)
            json_output("check", findings, exit_code=_exit_code, deterministic=det)
    elif args.format == "sarif":
        from report import generate_sarif
        name = args.name or Path(project).name
        sarif_text = json.dumps(generate_sarif(findings, name), indent=2)
        output_file = getattr(args, "output", None)
        if output_file:
            out_path = Path(output_file)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(sarif_text, encoding="utf-8")
            print(f"SARIF written to {out_path}", file=sys.stderr)
            _sarif_written_path = str(out_path)
        else:
            print(sarif_text)
    else:
        # Human-readable output
        from i18n import t
        from term_style import red, yellow, blue, magenta
        print(f"\n{t('scan_header', path=project)}")
        print(f"{'=' * 60}")

        # === First-run verdict: answer "Am I affected?" ===
        # Placed at the TOP so it's the first thing users see.
        # Indication framing, not legal determination: Regula reports
        # pattern-based indicators; Article 6 classification depends on
        # intended purpose and context (positioning rule — the tool must
        # never present itself as issuing a legal classification).
        if prohibited:
            verdict_tier = "PROHIBITED"
            verdict_desc = "Your project contains indicators of AI practices prohibited under EU AI Act Article 5."
            verdict_action = "Review these findings — confirmed prohibited practices must be removed before deployment in the EU."
            verdict_color = red
        elif high_risk or credentials:
            verdict_tier = "HIGH-RISK"
            verdict_desc = "Your project shows indicators of high-risk AI under EU AI Act Annex III."
            verdict_action = "If confirmed high-risk (Article 6), Articles 9-15 obligations apply before the enforcement deadline."
            verdict_color = yellow
        elif limited:
            verdict_tier = "LIMITED-RISK"
            verdict_desc = "Your project has indicators of limited-risk AI components (Article 50 transparency)."
            verdict_action = "If confirmed, Article 50 requires disclosing AI usage to users."
            verdict_color = blue
        elif active:
            verdict_tier = "MINIMAL-RISK"
            verdict_desc = "Your project uses AI but with minimal regulatory obligations."
            verdict_action = "No mandatory requirements, but good governance is recommended."
            verdict_color = lambda x: x  # identity function — no color applied
        else:
            _pre_stats = getattr(scan_files, "last_stats", {}) or {}
            _pre_gated = _pre_stats.get("domain_gated_count", 0)
            verdict_tier = "NO AI DETECTED"
            if _pre_gated > 0:
                _pre_cats = ", ".join(_pre_stats.get("domain_gated_categories", []))
                verdict_desc = (
                    f"No active findings. {_pre_gated} high-risk finding(s) "
                    f"suppressed by domain gating (see below)."
                )
                verdict_action = f"Use --domain <domain> to activate ({_pre_cats})."
            else:
                verdict_desc = "No AI components or risk indicators found in your project."
                verdict_action = "The EU AI Act likely does not apply to this project."
            verdict_color = lambda x: x  # identity function — no color applied

        print(f"\n  {verdict_color('Verdict')}: {verdict_color(verdict_tier)}")
        print(f"  {verdict_desc}")
        print(f"  {verdict_action}")

        # Top findings driving the verdict
        top = sorted(
            [f for f in active if not f.get("open_question")],
            key=lambda f: -f.get("confidence_score", 0),
        )[:3]
        if top:
            print("\n  Why:")
            for i, f in enumerate(top, 1):
                arts_raw = f.get("articles", [])[:2]
                arts = ", ".join(f"Art. {a}" for a in arts_raw) if arts_raw else ""
                desc = f.get("description", "")[:100]
                print(f"    {i}. {f['file']}:{f.get('line', '?')} — {desc}")
                if arts:
                    print(f"       ({arts})")

        # Use the scanner's real count, not "files with findings" —
        # the old derivation made empty scans look like nothing ran.
        stats = getattr(scan_files, "last_stats", {}) or {}
        total_files = stats.get("files_scanned", len(set(f["file"] for f in findings)))
        tests_skipped = int(stats.get("tests_skipped", 0))
        suffix = ""
        # Only blame the test-file exclusion when tests were ACTUALLY
        # skipped. Without this check, an empty directory or one with
        # only non-code files would misleadingly claim tests were excluded.
        if total_files == 0 and tests_skipped > 0:
            suffix = (
                f" ({tests_skipped} test file(s) excluded — "
                f"use --no-skip-tests to include)"
            )
        elif total_files == 0:
            suffix = " (no code files matched; check path and extensions)"
        files_label = f"{total_files}{suffix}"
        print(f"  {t('files_scanned'):<20}{files_label}")
        print(f"  {t('prohibited'):<20}{len(prohibited)}")
        print(f"  {t('credentials'):<20}{len(credentials)}")
        print(f"  {t('high_risk'):<20}{len(high_risk)}")
        print(f"  {t('agent_autonomy'):<20}{len(autonomy)}")
        print(f"  {t('limited_risk'):<20}{len(limited)}")
        _gated_for_display = stats.get("domain_gated_count", 0)
        _suppressed_total = len(suppressed) + _gated_for_display
        print(f"  {t('suppressed'):<20}{_suppressed_total}")
        if accepted:
            overdue = [f for f in accepted if f.get("risk_decision", {}).get("overdue")]
            print(f"  {'Accepted risks:':<20}{len(accepted)}  ({len(overdue)} overdue)")
        # Warn on undocumented suppressions
        no_rationale = [f for f in suppressed
                        if f.get("risk_decision") and not f["risk_decision"].get("rationale")]
        if no_rationale:
            print(f"\n  \u26a0 {len(no_rationale)} suppression(s) without rationale"
                  " \u2014 run regula check --audit-suppressions for details")
        if accepted:
            overdue_list = [f for f in accepted if f.get("risk_decision", {}).get("overdue")]
            if overdue_list:
                print(f"  \u26a0 {len(overdue_list)} accepted risk(s) overdue for review"
                      " \u2014 run regula check --audit-suppressions for details")
        print(f"  {t('block_tier'):<20}{len(block_findings)}")
        print(f"  {t('warn_tier'):<20}{len(warn_findings)}")
        print(f"  {t('info_tier'):<20}{len(info_findings)}")

        # Lifecycle phase breakdown
        phase_counts = {}
        for f in active:
            for phase in f.get("lifecycle_phases", ["develop"]):
                phase_counts[phase] = phase_counts.get(phase, 0) + 1
        if phase_counts:
            phase_str = ", ".join(f"{p}: {c}" for p, c in sorted(phase_counts.items()))
            print(f"  {'Lifecycle:':<20}{phase_str}")

        # Domain gating INFO: tell users about --domain when findings were suppressed
        gated_count = stats.get("domain_gated_count", 0)
        gated_cats = stats.get("domain_gated_categories", [])
        if gated_count > 0:
            cats_str = ", ".join(gated_cats)
            print(f"\n  INFO: {gated_count} high-risk finding(s) suppressed by domain gating")
            print(f"        Categories: {cats_str}")
            print("        To activate, use: regula check --domain <domain>")
            print("        Or add domain-specific imports to your project.")

        if prohibited:
            print(f"\n  {red('PROHIBITED INDICATORS')}:")
            for f in prohibited:
                score = f.get("confidence_score", 0)
                tier_label = f.get("_finding_tier", "block").upper()
                lp = f" [{f.get('lifecycle_phases', ['develop'])[0]}]" if f.get("lifecycle_phases") else ""
                print(f"    [{tier_label}] [{score:3d}] {f['file']} — {f.get('description', '')}{lp}")
                _print_remediation(f)

        if credentials:
            print(f"\n  {red('CREDENTIAL EXPOSURE')} (Article 15):")
            for f in credentials:
                score = f.get("confidence_score", 0)
                tier_label = f.get("_finding_tier", "warn").upper()
                lp = f" [{f.get('lifecycle_phases', ['develop'])[0]}]" if f.get("lifecycle_phases") else ""
                print(f"    [{tier_label}] [{score:3d}] {f['file']}:{f.get('line', '?')} — {f.get('description', '')}{lp}")
                _print_remediation(f)

        if high_risk:
            print(f"\n  {yellow('HIGH-RISK INDICATORS')}:")
            for f in high_risk:
                score = f.get("confidence_score", 0)
                tier_label = f.get("_finding_tier", "warn").upper()
                lp = f" [{f.get('lifecycle_phases', ['develop'])[0]}]" if f.get("lifecycle_phases") else ""
                print(f"    [{tier_label}] [{score:3d}] {f['file']} — {f.get('description', '')}{lp}")
                _print_remediation(f)

        if autonomy:
            print(f"\n  {magenta('AGENT AUTONOMY')} (OWASP Agentic ASI02):")
            for f in autonomy:
                score = f.get("confidence_score", 0)
                tier_label = f.get("_finding_tier", "warn").upper()
                lp = f" [{f.get('lifecycle_phases', ['develop'])[0]}]" if f.get("lifecycle_phases") else ""
                print(f"    [{tier_label}] [{score:3d}] {f['file']}:{f.get('line', '?')} — {f.get('description', '')}{lp}")
                _print_remediation(f)

        if limited:
            # Limited-risk findings (Article 50 transparency) are surfaced
            # the same way high-risk and credential findings are: one row
            # per finding, no verbose-only suppression. The previous
            # behaviour skipped every INFO-tier row while still printing
            # the section header, producing a header with no rows beneath.
            print(f"\n  {blue('LIMITED-RISK')} (Article 50):")
            for f in limited:
                score = f.get("confidence_score", 0)
                tier_label = f.get("_finding_tier", "info").upper()
                lp = f" [{f.get('lifecycle_phases', ['develop'])[0]}]" if f.get("lifecycle_phases") else ""
                print(f"    [{tier_label}] [{score:3d}] {f['file']}:{f.get('line', '?')} — {f.get('description', '')}{lp}")

        if getattr(args, "verbose", False) and info_findings:
            info_non_limited = [f for f in info_findings if f["tier"] not in ("limited_risk",)]
            if info_non_limited:
                print("\n  INFO (verbose):")
                for f in info_non_limited:
                    score = f.get("confidence_score", 0)
                    lp = f" [{f.get('lifecycle_phases', ['develop'])[0]}]" if f.get("lifecycle_phases") else ""
                    print(f"    [INFO] [{score:3d}] {f['file']} — {f.get('description', '')}{lp}")

        # Open questions: low-confidence findings that need human judgment
        # suppressed findings already excluded by _is_open_question
        open_qs = [f for f in findings if f.get("open_question")]
        if open_qs:
            print(f"\n  Questions for human review ({len(open_qs)}):")
            for f in open_qs[:10]:
                print(f"    ? {f['file']}:{f.get('line', '?')} — {f.get('category', 'Unknown')}")
                print(f"      {f.get('description', '')} (confidence: {f.get('confidence_score', 0)}%)")
            if len(open_qs) > 10:
                print(f"    ... and {len(open_qs) - 10} more (use --format json to see all)")

        # Multi-jurisdiction domain obligations summary
        if jurisdiction_pairs:
            _any_domain_obs = any(f.get("domain_obligations") for f in findings)
            if _any_domain_obs:
                print(f"\n  {'─' * 56}")
                print(f"  {yellow('MULTI-JURISDICTION OBLIGATIONS')}:")
                # Collect unique (jurisdiction, domain, obligations) across all findings
                _seen_jur_domains = set()
                for f in findings:
                    for jur_name, jur_data in (f.get("domain_obligations") or {}).items():
                        for cd in jur_data.get("covered_domains", []):
                            key = (jur_name, cd["domain"])
                            if key in _seen_jur_domains:
                                continue
                            _seen_jur_domains.add(key)
                # Print per-jurisdiction summary
                for short_name, _fw_key in jurisdiction_pairs:
                    _jur_domains = [(j, d) for j, d in _seen_jur_domains if j == short_name]
                    if not _jur_domains:
                        continue
                    # Get summary from first finding that has this jurisdiction
                    _jur_info = None
                    for f in findings:
                        _jur_info = (f.get("domain_obligations") or {}).get(short_name)
                        if _jur_info:
                            break
                    if not _jur_info:
                        continue
                    print(f"\n    {_jur_info['jurisdiction']} ({_jur_info['law']})")
                    print(f"    Status: {_jur_info['status']} | Penalties: {_jur_info['penalty_range']}")
                    for cd in _jur_info.get("covered_domains", []):
                        print(f"      • {cd['domain']}: {cd['risk_level']} — "
                              f"{len(cd['obligations'])} obligations (Articles {', '.join(cd['articles'])})")

        print(f"{'=' * 60}")
        print(f"  {t('confidence_note')}")
        print(f"  {t('tier_note')}")
        print(f"  {t('suppress_note')}")
        print()

        # === Next steps for the user ===
        print(f"\n  {'─' * 56}")
        print("  Next steps:")
        step_num = 1
        if prohibited:
            print(f"    {step_num}. regula fix --project .         Remove prohibited practices")
            step_num += 1
        if high_risk or limited:
            print(f"    {step_num}. regula gap --project .         See which articles you need to address")
            step_num += 1
            print(f"    {step_num}. regula roadmap --project .     Get a week-by-week compliance plan")
            step_num += 1
        if active:
            print(f"    {step_num}. regula evidence-pack --project . --bundle   Generate auditor-ready evidence")
            step_num += 1
        if not active:
            print(f"    {step_num}. regula gap --project .         Verify compliance documentation exists")
            step_num += 1
        print()

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
            print("  DETAILED EXPLANATION")
            print(f"{'=' * 60}")
            project_root = Path(args.path).resolve()
            for rel_path in sorted(explain_files):
                full_path = project_root / rel_path
                if not full_path.is_file():
                    continue
                try:
                    content = full_path.read_text(encoding="utf-8", errors="ignore")
                except (PermissionError, OSError):
                    continue  # file unreadable; skip
                lang = _detect_lang(full_path.name) or "python"
                result = explain_classification(content, filepath=rel_path, language=lang)
                print(f"\n--- {rel_path} ---")
                print(format_explanation(result, filepath=rel_path))
                print()

    # GitHub Actions workflow-command annotations. Emits inline PR comments
    # without SARIF/CodeQL setup. Gated on GITHUB_ACTIONS=true + --ci so
    # local runs stay quiet. No-op in any other context.
    _emit_github_annotations(
        args,
        {"block": block_findings, "warn": warn_findings, "info": info_findings},
    )

    # Overdue risk acceptance warnings in CI (ISO 42001 Clause 8.2, AI Act 9(2))
    if os.environ.get("GITHUB_ACTIONS") and getattr(args, "ci", False):
        for f in accepted:
            rd = f.get("risk_decision", {})
            if rd.get("overdue"):
                fpath = f.get("file", "unknown")
                fline = f.get("line", 1)
                pat = rd.get("pattern", "unknown")
                rev = rd.get("review_date", "unknown")
                own = rd.get("owner", "unknown")
                print(f"::warning file={fpath},line={fline}"
                      f"::Accepted risk '{pat}' is overdue for review"
                      f" (was due {rev}, owner {own})")

    # Exit code (1 if any BLOCK-tier findings, 1 if WARN-tier and
    # (--strict or --ci), 0 otherwise) was already computed once, early,
    # right after block_findings/warn_findings were derived from the
    # findings partition — see _exit_code above. Reusing that same value
    # here (rather than recomputing it) is what guarantees --format json's
    # embedded exit_code field can never drift out of sync with the actual
    # process exit code below.

    # DEF-004: emit the completion manifest ONLY on successful completion,
    # after all scanning and artifact writes have succeeded. Reaching this
    # line means the scan did not raise. A failed scan exits earlier (e.g.
    # _validate_path -> exit 2) and never writes the manifest — its absence
    # is the failure signal the CI gate relies on.
    if getattr(args, "manifest", None):
        _write_analysis_manifest(
            args.manifest,
            scan_target=project,
            started_at=_manifest_started_at,
            view=_view,
            scan_stats=_scan_stats,
            sarif_path=_sarif_written_path,
            exit_code=_exit_code,
        )

    sys.exit(_exit_code)


def cmd_classify(args) -> None:
    """Classify a text input."""
    from cli import json_output, _validate_path
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

    # Compute the verdict exit code ONCE so json and text modes agree (DEF-008
    # class: previously the json branch returned with a hardcoded envelope
    # exit_code=0 AND skipped the sys.exit below, so `classify --format json`
    # on prohibited content reported "clear" via BOTH the envelope field and
    # the process exit code, while text mode correctly exited 1).
    _classify_exit = 1 if result.tier.value == "prohibited" else 0

    if args.format == "json":
        import json as _json
        try:
            data = _json.loads(result.to_json())
        except (ValueError, TypeError, AttributeError):
            data = result.to_json()
        json_output("classify", data, exit_code=_classify_exit)
        sys.exit(_classify_exit)
    else:
        print(result.message)
        if result.exceptions:
            print(f"  Exceptions: {result.exceptions}")

    sys.exit(_classify_exit)


def cmd_discover(args) -> None:
    """Discover AI systems."""
    from cli import json_output, _validate_path

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
            except (OSError, ValueError, KeyError, TypeError, ImportError, AttributeError) as e:
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


def cmd_guardrails(args) -> None:
    """Detect guardrail implementation coverage."""
    from cli import json_output, _validate_path
    from guardrail_scanner import scan_for_guardrails, format_guardrails_text

    if args.project != ".":
        _validate_path(args.project)
    result = scan_for_guardrails(args.project)
    fmt = getattr(args, "format", "text")
    # Compute the verdict exit code ONCE so json and text modes agree
    # (DEF-008 class: json_output("guardrails", ...) previously always
    # hardcoded envelope exit_code=0, contradicting the real process exit
    # code under --strict/--ci with a low overall_score).
    _guardrails_exit = 0
    if (getattr(args, "strict", False) or getattr(args, "ci", False)) and result.get("overall_score", 0) < 50:
        _guardrails_exit = 1
    if fmt == "json":
        json_output("guardrails", result, exit_code=_guardrails_exit)
    else:
        print(format_guardrails_text(result))
    if _guardrails_exit:
        sys.exit(_guardrails_exit)


def _print_suppression_audit(findings: list) -> None:
    """Print a table of all regula-ignore and regula-accept annotations."""
    decisions = [f for f in findings if f.get("risk_decision")]
    if not decisions:
        print("\nNo regula-ignore or regula-accept annotations found.")
        return

    print(f"\n{'Type':<8} {'File':<30} {'Line':>5}  {'Pattern':<20} {'Rationale':<35} {'Owner':<10} {'Review':<12} {'Status'}")
    print("-" * 135)
    for f in decisions:
        rd = f["risk_decision"]
        dtype = rd.get("dtype", rd.get("type", "?"))
        fpath = f.get("file", "?")
        if len(fpath) > 28:
            fpath = "..." + fpath[-25:]
        line = f.get("line", 0)
        pattern = rd.get("pattern", "?")[:18]
        rationale = (rd.get("rationale") or "\u2014")[:33]
        owner = rd.get("owner", "\u2014") if dtype == "accept" else "\u2014"
        review = rd.get("review_date", "\u2014") if dtype == "accept" else "\u2014"

        status = "OK"
        if rd.get("error"):
            status = "\u26a0 ERROR"
        elif rd.get("warning"):
            status = "\u26a0 NO RATIONALE"
        elif rd.get("overdue"):
            status = "\u26a0 OVERDUE"

        print(f"{dtype:<8} {fpath:<30} {line:>5}  {pattern:<20} {rationale:<35} {owner:<10} {review:<12} {status}")


def cmd_gdpr(args) -> None:
    """Scan for GDPR code patterns with dual-compliance hotspot detection."""
    from cli import json_output, _validate_path
    from gdpr_scan import scan_gdpr

    if args.project != ".":
        _validate_path(args.project)
    project_path = str(Path(args.project).resolve())
    scope = getattr(args, "scope", "all")

    result = scan_gdpr(project_path, scope=scope)

    if args.format == "json":
        json_output("gdpr", result)
        return

    findings = result["findings"]
    summary = result["summary"]

    if not findings:
        print(f"No GDPR-relevant patterns found in {project_path}")
        return

    print(f"\n  GDPR Code Pattern Scan — {project_path}\n")
    print(f"  {summary['total_findings']} finding(s): {summary['high_confidence']} high, "
          f"{summary['medium_confidence']} medium, {summary['low_confidence']} low confidence")

    if summary["dual_compliance_hotspot_files"] > 0:
        print(f"  {summary['dual_compliance_hotspot_files']} file(s) with dual-compliance hotspots "
              f"({summary['dual_compliance_findings']} finding(s), GDPR + EU AI Act)")

    print()
    for f in findings[:20]:
        prefix = "!" if f.get("dual_compliance") else " "
        arts = ", ".join(f"Art. {a}" for a in f["gdpr_articles"])
        print(f"  {prefix} {f['file']}:{f['line']} [{arts}] {f['description']}")
        if f.get("dual_compliance"):
            print(f"      Hotspot: {f.get('hotspot_description', '')}")

    if len(findings) > 20:
        print(f"\n  ... and {len(findings) - 20} more (use --format json to see all)")

    print("\n  All findings are indicators that GDPR obligations may apply — not violations.")
    print("  Consult a data protection specialist for compliance determination.\n")
