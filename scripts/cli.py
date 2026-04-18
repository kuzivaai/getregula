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



def _build_envelope(command: str, data, exit_code: int = 0) -> dict:
    """Build the standard JSON envelope dict."""
    return {
        "format_version": "1.0",
        "regula_version": VERSION,
        "command": command,
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "exit_code": exit_code,
        "data": data,
    }


def json_output(command: str, data, exit_code: int = 0, deterministic: bool = False) -> None:
    """Standard JSON envelope for all --format json output."""
    envelope = _build_envelope(command, data, exit_code)
    if deterministic:
        envelope.pop("timestamp", None)
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
    except (ImportError, OSError, ValueError, KeyError, TypeError, AttributeError):
        return f"{VERSION}-patterns"  # Fallback when policy file unavailable


# Primary commands shown in default --help (progressive disclosure).
# All 52 commands remain functional — use --help-all to see them.
_PRIMARY_COMMANDS = {
    "check", "comply", "gap", "plan", "init", "quickstart", "demo",
}


def _run_bare_scan() -> None:
    """Run when the user types bare `regula` with no subcommand.

    Performs a quick scan of the current directory and shows:
    1. Risk findings summary
    2. Compliance gap score
    3. Contextual next steps based on what was found

    Designed to deliver value in under 30 seconds (per clig.dev:
    "suggest the next best step users should take").
    """
    import time
    from report import scan_files
    from findings_view import partition_findings

    project = str(Path(".").resolve())
    project_name = Path(project).name
    start = time.time()

    # Scan
    findings = scan_files(project)
    view = partition_findings(findings)
    active = view["active"]
    blocks = view["block"]
    warns = view["warn"]
    infos = view["info"]
    prohibited = view["prohibited"]

    # Quick gap score (best-effort, don't fail the whole command)
    gap_score = None
    highest_risk = None
    try:
        from compliance_check import assess_compliance
        assessment = assess_compliance(project)
        gap_score = assessment.get("overall_score", 0)
        highest_risk = assessment.get("highest_risk", "unknown")
    except Exception:
        pass  # gap assessment is best-effort

    elapsed = time.time() - start

    # Stats from scanner
    stats = getattr(scan_files, "last_stats", {}) or {}
    total_files = stats.get("files_scanned", len(set(f.get("file", "") for f in findings)))

    # Output
    print(f"\nRegula — {project_name}")
    print(f"{'=' * 60}")
    print(f"  {'Files scanned:':<24}{total_files}")
    print(f"  {'BLOCK findings:':<24}{len(blocks)}")
    print(f"  {'WARN findings:':<24}{len(warns)}")
    print(f"  {'INFO findings:':<24}{len(infos)}")
    if gap_score is not None:
        print(f"  {'Compliance score:':<24}{gap_score}/100")
    if highest_risk and highest_risk != "unknown":
        print(f"  {'Highest risk tier:':<24}{highest_risk}")
    print(f"  {'Scan time:':<24}{elapsed:.1f}s")

    # Top findings (up to 3)
    # Deduplicate by file+description for concise output
    seen = set()
    top = []
    for f in (prohibited + list(blocks) + list(warns)):
        key = (f.get("file", ""), f.get("description", ""))
        if key not in seen:
            seen.add(key)
            top.append(f)
        if len(top) >= 3:
            break
    if top:
        print(f"\n  Top findings:")
        for f in top:
            score = f.get("confidence_score", 0)
            tier = f.get("_finding_tier", "info").upper()
            print(f"    [{tier}] [{score:3d}] {f.get('file', '?')}")
            desc = f.get("description", "")
            if desc:
                print(f"          {desc}")

    print(f"{'=' * 60}")

    # Contextual next steps based on findings
    steps = []
    if blocks:
        steps.append(f"regula check .{'':<30s}Review {len(blocks)} BLOCK finding(s) in detail")
    if gap_score is not None and gap_score < 50:
        steps.append(f"regula comply{'':<31s}See your EU AI Act obligation checklist")
    elif gap_score is not None:
        steps.append(f"regula comply{'':<31s}Check obligations you still need to address")
    if warns:
        steps.append(f"regula plan --project .{'':<22s}Get a prioritised remediation plan")
    if not blocks and not warns:
        steps.append(f"regula check --verbose .{'':<20s}Show all findings including INFO tier")
    steps.append(f"regula gap --project .{'':<22s}Detailed compliance gap assessment")
    if not any("evidence" in s for s in steps):
        steps.append(f"regula evidence-pack --project .{'':<13s}Generate auditor-ready evidence")

    print(f"\n  Next steps:")
    for i, step in enumerate(steps[:5], 1):
        print(f"    {i}. {step}")
    print()

    sys.exit(1 if blocks else 0)


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


# ---------------------------------------------------------------------------
# Private helpers used by cmd_register (cli_governance.py)
# ---------------------------------------------------------------------------

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
            continue  # file unreadable; skip
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


# ---------------------------------------------------------------------------
# Organisational questionnaire (used by cmd_conform in cli_compliance.py)
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Metrics text helper (used by cmd_metrics in cli_util.py)
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Epilog for main parser
# ---------------------------------------------------------------------------

_MAIN_EPILOG = """
Quick start:
  regula                                  Scan current directory + compliance score
  regula check .                          Detailed risk scan
  regula comply                           EU AI Act obligation checklist
  regula check --ci .                     CI/CD mode (exit codes + SARIF)

Examples:
  regula gap --project .                  Compliance gap assessment (Articles 9-15)
  regula plan --project .                 Prioritised remediation plan
  regula evidence-pack --project .        Auditor-ready evidence package
  regula docs --project . --qms          Generate Annex IV + QMS scaffolds

Run 'regula --help-all' to see all commands.

Environment variables (override defaults when CLI flag not provided):
  REGULA_FORMAT       Output format (text, json, sarif)
  REGULA_STRICT       Enable CI mode when set to 1/true/yes
  REGULA_MIN_TIER     Minimum risk tier to report
  REGULA_LANG         Output language (en, pt-BR, de)
  REGULA_SKIP_TESTS   Skip test files when set to 1/true/yes
  REGULA_FRAMEWORK    Compliance framework
"""


# ---------------------------------------------------------------------------
# Import command functions from domain modules
# ---------------------------------------------------------------------------

from cli_scan import cmd_check, cmd_classify, cmd_discover, cmd_guardrails
from cli_report import (
    cmd_report, cmd_evidence_pack, cmd_sbom, cmd_benchmark,
    cmd_inventory, cmd_badge, cmd_doc_audit,
)
from cli_compliance import (
    cmd_comply, cmd_compliance, cmd_conform, cmd_gap, cmd_exempt,
    cmd_gpai_check, cmd_plan, cmd_assess, cmd_baseline, cmd_roadmap,
)
from cli_governance import (
    cmd_governance, cmd_agent, cmd_oversight, cmd_model_card,
    cmd_register, cmd_disclose, cmd_feedback, cmd_feedback_summary,
    cmd_handoff,
)
from cli_util import (
    cmd_doctor, cmd_self_test, cmd_config, cmd_install,
    cmd_quickstart, cmd_init, cmd_fix, cmd_explain_article,
    cmd_deps, cmd_timeline, cmd_regwatch, cmd_feed, cmd_bias,
    cmd_attest, cmd_verify, cmd_status, cmd_audit, cmd_mcp_server,
    cmd_questionnaire, cmd_session, cmd_docs, cmd_telemetry,
    cmd_metrics, cmd_security_self_check, cmd_owasp_agentic,
    cmd_ai_codegen,
)


def cmd_demo(args):
    """Run Regula against the bundled example project to show real output."""
    import os
    example_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "examples", "cv-screening-app",
    )
    if not os.path.isdir(example_dir):
        print("Demo requires the examples/ directory (available in the git repo).")
        print("Try: git clone https://github.com/kuzivaai/getregula && cd getregula")
        print("     regula demo")
        print()
        print("Or scan your own project: regula check .")
        return
    print("=" * 60)
    print("  Regula Demo \u2014 scanning examples/cv-screening-app")
    print("  (a hiring system that triggers Annex III high-risk)")
    print("=" * 60)
    print()
    # Reuse the existing check logic
    args.path = example_dir
    args.format = getattr(args, "format", "text")
    args.no_ignore = False
    args.skip_tests = True
    args.min_tier = None
    args.diff = None
    args.jurisdictions = None
    args.explain = False
    args.name = None
    args.framework = None
    args.output = None
    args.deterministic = False
    args.verbose = False
    args.strict = False
    args.ci = False
    args.lang = None
    args.rules = None
    try:
        cmd_check(args)
    except SystemExit:
        pass
    print()
    print("=" * 60)
    print("  Next steps:")
    print("    regula check .          Scan YOUR project")
    print("    regula assess           Am I even in scope? (no code needed)")
    print("    regula gap .            Per-article compliance score")
    print("    regula evidence-pack .  Generate auditor-ready evidence")
    print("=" * 60)


def cmd_risks(args):
    """Risk register summary view (ISO 42001 6.1.2, AI Act 9(2)(a))."""
    from report import scan_files
    from findings_view import partition_findings

    project = getattr(args, "project", ".")
    findings = scan_files(project)
    view = partition_findings(findings)

    active = view["active"]
    accepted_list = view.get("accepted", [])
    suppressed = view["suppressed"]
    no_rationale = [f for f in suppressed
                    if f.get("risk_decision") and not f["risk_decision"].get("rationale")]
    overdue = [f for f in accepted_list
               if f.get("risk_decision", {}).get("overdue")]

    data = {
        "active_findings": len(active),
        "accepted_risks": len(accepted_list),
        "accepted_overdue": len(overdue),
        "suppressed_fp": len(suppressed),
        "suppressed_no_rationale": len(no_rationale),
    }

    fmt = getattr(args, "format", "text")
    if fmt == "json":
        json_output("risks", data)
        return

    name = Path(project).resolve().name
    print(f"\nRisk Register \u2014 {name}")
    print("=" * 60)
    print(f"  Active findings:        {len(active):>3}  (require assessment)")
    print(f"  Accepted risks:         {len(accepted_list):>3}  (documented, {len(overdue)} overdue)")
    print(f"  Suppressed (FP):        {len(suppressed):>3}  (documented)")
    if no_rationale:
        print(f"  Suppressed (no reason): {len(no_rationale):>3}  \u26a0")
    print("=" * 60)


def _build_subparsers(subparsers):
    """Define all CLI subcommands. Extracted from main() for readability."""
    p_init = subparsers.add_parser(
        "init",
        help="Guided setup wizard",
        description=(
            "Set Regula up for a project: detect the AI coding platform "
            "(Claude Code, Copilot, Windsurf, or plain Git), create a "
            "default policy file, install the matching pre-commit / hook "
            "integration, and run a first scan. For a minimal no-install "
            "first run, use `regula quickstart` instead."
        ),
    )
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
    p_check.add_argument("--audit-suppressions", action="store_true",
                         help="List all regula-ignore and regula-accept annotations with status (ISO 42001 9.1)")
    p_check.add_argument("--strict", action="store_true", help="Exit 1 on WARN-tier findings")
    p_check.add_argument("--ci", action="store_true", default=False,
                         help="CI mode: exit 1 on any WARN or BLOCK finding (implies --strict)")
    p_check.add_argument("--verbose", "-v", action="store_true", help="Show INFO-tier findings")
    p_check.add_argument("--skip-tests", action="store_true", default=True,
                         help="Exclude test files from results (default: on, use --no-skip-tests to include)")
    p_check.add_argument("--no-skip-tests", dest="skip_tests", action="store_false",
                         help="Include test files in results")
    p_check.add_argument("--scope", choices=["all", "production"], default="all",
                         help="Scan scope: 'production' excludes test/example/generated/tooling files")
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

    # --- comply ---
    p_comply = subparsers.add_parser("comply",
                                     help="EU AI Act obligation checklist with status")
    p_comply.add_argument("--project", "-p", default=".", help="Project directory")
    p_comply.add_argument("--article", "-a", help="Deep-dive into a specific article (e.g. 9, 14)")
    p_comply.add_argument("--all", action="store_true",
                          help="Show full Articles 9-15 assessment regardless of detected risk tier")
    p_comply.add_argument("--format", "-f", choices=["text", "json"], default="text")
    p_comply.set_defaults(func=cmd_comply)

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
    p_bias = subparsers.add_parser("bias", help="Evaluate model bias using CrowS-Pairs + BBQ benchmarks (requires Ollama)")
    p_bias.add_argument("--model", default="llama3", help="Ollama model name (default: llama3)")
    p_bias.add_argument("--endpoint", default="http://localhost:11434", help="Ollama API endpoint")
    p_bias.add_argument("--sample", type=int, default=100, help="Max items per benchmark (default: 100)")
    p_bias.add_argument("--csv", help="Path to local CrowS-Pairs CSV file")
    p_bias.add_argument("--method", choices=["auto", "logprob", "prompt"],
                        default="auto",
                        help="CrowS-Pairs method: logprob (gold standard), prompt (fallback), auto (default)")
    p_bias.add_argument("--benchmark", choices=["all", "crowspairs", "bbq"],
                        default="all",
                        help="Which benchmarks to run (default: all)")
    p_bias.add_argument("--format", choices=["text", "json", "annex-iv"], default="text",
                        help="Output format: text, json, or annex-iv (Annex IV documentation)")
    p_bias.add_argument("--confidence", type=int, default=1000,
                        help="Bootstrap resamples for confidence intervals (default: 1000)")
    p_bias.add_argument("--seed", type=int, help="Random seed for reproducibility")
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
    p_feed = subparsers.add_parser("feed", help="[experimental] AI governance news feed from curated regulatory sources")
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
    p_session = subparsers.add_parser("session", help="Aggregate risk findings across a Claude Code session — shows cumulative risk from all tool calls")
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
             "(e.g., '1.7.0-patterns-2026-04-16') for reproducible audits. "
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

    # --- roadmap ---
    p_roadmap = subparsers.add_parser("roadmap",
                                       help="Generate week-by-week compliance roadmap")
    p_roadmap.add_argument("--project", "-p", default=".")
    p_roadmap.add_argument("--target-date", "-t", default="2 August 2026",
                           help="Compliance deadline (default: 2 August 2026)")
    p_roadmap.add_argument("--format", "-f", choices=["text", "json"], default="text")
    p_roadmap.set_defaults(func=cmd_roadmap)

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
    p_evidence.add_argument("--bundle", action="store_true",
                            help="Package output as a self-verifying .regula-evidence.zip")
    p_evidence.set_defaults(func=cmd_evidence_pack)

    # --- doc-audit ---
    p_doc_audit = subparsers.add_parser("doc-audit",
                                         help="Score compliance document quality (0-100 per article)")
    p_doc_audit.add_argument("--project", "-p", default=".")
    p_doc_audit.add_argument("--format", "-f", choices=["text", "json"], default="text")
    p_doc_audit.set_defaults(func=cmd_doc_audit)

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
    p_conform.add_argument("--model", default="llama3", help="Ollama model name for bias evaluation (default: llama3)")
    p_conform.add_argument("--endpoint", default="http://localhost:11434", help="Ollama endpoint URL (default: http://localhost:11434)")
    p_conform.add_argument("--format", "-f", choices=["text", "json"], default="text")
    p_conform.add_argument(
        "--zip",
        dest="zip_bundle",
        action="store_true",
        help="Also emit a .regula.zip bundle of the pack for portable exchange "
             "(Regula Evidence Format v1, §3.2)",
    )
    p_conform.add_argument(
        "--sign",
        action="store_true",
        help="Sign the pack manifest with your Ed25519 key (Regula Evidence "
             "Format v1.1, §4.5). Generates a keypair at ~/.regula/signing.key "
             "on first use. Requires the regula[signing] optional extra.",
    )
    p_conform.add_argument(
        "--signing-key",
        dest="signing_key",
        metavar="PATH",
        help="Path to an Ed25519 private key (PEM, PKCS8). Overrides the "
             "default ~/.regula/signing.key and the REGULA_SIGNING_KEY env "
             "variable. Implies --sign.",
    )
    p_conform.add_argument(
        "--timestamp",
        action="store_true",
        help="Request an RFC 3161 timestamp from a TSA over the signed "
             "canonical manifest form and embed it as timestamp_authority "
             "(Regula Evidence Format v1.1, §4.6). Implies --sign and "
             "requires network access to the TSA.",
    )
    p_conform.add_argument(
        "--tsa-url",
        dest="tsa_url",
        metavar="URL",
        help="TSA endpoint URL (default: https://freetsa.org/tsr). Any "
             "RFC 3161-compliant TSA works.",
    )
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
    p_sbom = subparsers.add_parser("sbom", help="Generate AI Software Bill of Materials (CycloneDX 1.7)")
    p_sbom.add_argument("--project", "-p", default=".")
    p_sbom.add_argument("--format", "-f", choices=["json", "text"], default="json")
    p_sbom.add_argument("--output", "-o", help="Output file path")
    p_sbom.add_argument("--name", "-n", help="Project name")
    p_sbom.add_argument("--ai-bom", action="store_true", help="Include AI-specific BOM fields (model provenance, GPAI tiers, datasets)")
    p_sbom.set_defaults(func=cmd_sbom)

    # --- agent ---
    p_agent = subparsers.add_parser("agent", help="Monitor agentic AI sessions for risk patterns — analyses Claude Code audit logs or MCP config files")
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

    # --- demo ---
    p_demo = subparsers.add_parser("demo", help="Run Regula on a bundled example project (see it in action)")
    p_demo.add_argument("--format", "-f", choices=["text", "json"], default="text")
    p_demo.set_defaults(func=cmd_demo)

    # --- risks ---
    p_risks = subparsers.add_parser(
        "risks",
        help="Risk register summary \u2014 active findings, accepted risks, suppressed FPs (ISO 42001 6.1.2)",
    )
    p_risks.add_argument("--project", "-p", default=".", help="Project directory")
    p_risks.add_argument("--format", "-f", choices=["text", "json"], default="text")
    p_risks.set_defaults(func=cmd_risks)

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

    p_fb_summary = feedback_sub.add_parser("summary", help="Show summary of local feedback events")
    p_fb_summary.add_argument("--format", "-f", choices=["text", "json"], default="text")
    p_fb_summary.set_defaults(func=cmd_feedback_summary)

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

    p_verify = subparsers.add_parser(
        "verify",
        help="Verify integrity of a Regula Evidence Pack (spec: docs/spec/regula-evidence-format-v1.md)",
        description=(
            "Verify a Regula Evidence Pack against the Regula Evidence "
            "Format v1 spec. Checks every file's SHA-256 against the "
            "manifest, validates the Ed25519 signature if a v1.1 signing "
            "block is present, and validates the RFC 3161 timestamp if a "
            "v1.1 timestamp block is present. Accepts a pack directory, "
            "a manifest.json file, or a .regula.zip bundle. Exit codes: "
            "0 = integrity confirmed, 1 = file missing/modified or "
            "signature invalid, 2 = manifest unreadable or strict "
            "verification failed."
        ),
    )
    p_verify.add_argument(
        "pack_path",
        help="Path to a pack directory, a manifest.json file, or a .regula.zip bundle",
    )
    p_verify.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format for the verify report (default: text). "
             "JSON emits a regula.verify.v1 envelope.",
    )
    p_verify.add_argument(
        "--strict",
        action="store_true",
        help="Fail (exit 2) if the pack does not declare "
             "format=regula.evidence.v1, if a signed manifest's signature "
             "cannot be verified (missing cryptography library), or if a "
             "timestamped manifest's token cannot be parsed. Under "
             "non-strict, these cases warn but exit 0.",
    )
    p_verify.add_argument(
        "--report",
        metavar="PATH",
        help="Write a regula.verify.v1.json report to PATH",
    )
    p_verify.set_defaults(func=cmd_verify)


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


def _make_progressive_help(parser, subparsers):
    """Override default help to show only primary commands.

    Progressive disclosure (per clig.dev, Atlassian): show the 6 commands
    most users need. The full set is available via --help-all.
    """
    original_format_usage = parser.format_help

    def progressive_help():
        # Build a condensed help showing only primary commands
        lines = []
        lines.append(f"usage: regula [command] [options]\n")
        lines.append("AI Governance Risk Indication for Code\n")
        lines.append("")
        lines.append("  Running 'regula' with no command scans the current directory.\n")
        lines.append("")
        lines.append("Primary commands:")
        # Primary commands with descriptions
        primary_descs = [
            ("check", "Scan files for risk indicators"),
            ("comply", "EU AI Act obligation checklist with status"),
            ("gap", "Compliance gap assessment (Articles 9-15)"),
            ("plan", "Prioritised remediation plan"),
            ("init", "Guided setup wizard"),
            ("quickstart", "60-second onboarding (create policy + first scan)"),
            ("demo", "Run Regula on a bundled example project"),
        ]
        for name, desc in primary_descs:
            lines.append(f"  {name:<16}{desc}")
        lines.append("")
        total = len(subparsers.choices)
        lines.append(f"  Run 'regula --help-all' to see all {total} commands.")
        lines.append(f"  Run 'regula <command> --help' for command-specific help.\n")
        lines.append("")
        lines.append("Options:")
        lines.append("  --ci              CI mode: exit 1 on any WARN or BLOCK finding")
        lines.append("  --lang {en,pt-BR,de}")
        lines.append("                    Output language (default: en)")
        lines.append("  --version         Show version and exit")
        lines.append("  --help-all        Show all commands")
        lines.append("  -h, --help        Show this help message")
        lines.append("")
        # Epilog
        lines.append("Quick start:")
        lines.append("  regula                                  Scan + compliance score")
        lines.append("  regula check .                          Detailed risk scan")
        lines.append("  regula comply                           Obligation checklist")
        lines.append("  regula check --ci .                     CI/CD mode")
        lines.append("")
        return "\n".join(lines)

    return progressive_help


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
    parser.add_argument("--help-all", action="store_true",
                        help="Show all commands (default --help shows primary commands only)")

    subparsers = parser.add_subparsers(dest="command")
    _build_subparsers(subparsers)

    # Override default help with progressive version
    _progressive = _make_progressive_help(parser, subparsers)
    original_print_help = parser.print_help

    def _print_progressive_help(file=None):
        print(_progressive(), file=file or sys.stdout)

    parser.print_help = _print_progressive_help

    args = parser.parse_args(args)

    # --help-all: show the original argparse help with all 52 commands
    if getattr(args, 'help_all', False):
        original_print_help()
        sys.exit(0)

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
        # Bare `regula`: auto-scan current directory with next steps
        _run_bare_scan()
        return

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
        except (ImportError, AttributeError):
            pass  # sentry unavailable; fall through to stderr
        print(f"Internal error: {e}", file=sys.stderr)
        print("This is a bug in Regula. Please report it at https://github.com/kuzivaai/getregula/issues", file=sys.stderr)
        print("Or run: regula feedback --bug \"<description>\"", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
