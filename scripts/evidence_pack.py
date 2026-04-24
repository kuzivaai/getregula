#!/usr/bin/env python3
# regula-ignore
"""
Regula Evidence Pack Generator

Produces a structured folder containing every artifact a consultant or
auditor needs to assess EU AI Act compliance readiness.

Each file is independently useful. The manifest provides tamper-evidence
via SHA-256 content hashes.
"""

import hashlib
import json
import re
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from constants import VERSION


def _sha256(content: str) -> str:
    """Return hex SHA-256 of string content."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def generate_evidence_pack(
    project_path: str,
    output_dir: str = ".",
    project_name: str = None,
    **kwargs,
) -> dict:
    """Generate a complete evidence pack for a project.

    Args:
        project_path: Path to the project to scan.
        output_dir: Parent directory for the pack folder.
        project_name: Human-readable name (defaults to directory name).

    Returns:
        Dict with pack_dirname, pack_path, and manifest.
    """
    from report import scan_files
    from compliance_check import assess_compliance
    from generate_documentation import scan_project, generate_annex_iv
    from remediation_plan import generate_plan, format_plan_text

    project = Path(project_path).resolve()
    # Sanitise project name to prevent path traversal (OWASP input validation)
    name = re.sub(r'[^a-zA-Z0-9_\-]', '_', project_name or project.name)
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y-%m-%d")
    pack_name = f"evidence-pack-{name}-{date_str}"
    pack_dir = Path(output_dir) / pack_name
    pack_dir.mkdir(parents=True, exist_ok=True)

    file_records = []

    # --- 01: Scan results ---
    findings = scan_files(str(project))
    scan_json = json.dumps(findings, indent=2, default=str)
    _write_and_record(pack_dir, "01-scan-results.json", scan_json, file_records)

    # --- 02: Gap assessment ---
    gap = assess_compliance(str(project))
    gap_json = json.dumps(gap, indent=2, default=str)
    _write_and_record(pack_dir, "02-gap-assessment.json", gap_json, file_records)

    # --- 03: Annex IV documentation ---
    doc_findings = scan_project(str(project))
    annex_iv = generate_annex_iv(doc_findings, name, str(project))
    _write_and_record(pack_dir, "03-annex-iv-draft.md", annex_iv, file_records)

    # --- 04: Dependency report ---
    try:
        from dependency_scan import scan_dependencies
        dep_report = scan_dependencies(str(project))
        dep_json = json.dumps(dep_report, indent=2, default=str)
        _write_and_record(pack_dir, "04-dependency-report.json", dep_json, file_records)
    except (ImportError, OSError, ValueError, KeyError):
        pass  # optional section; skip if module missing or data error

    # --- 05: Audit trail ---
    try:
        from log_event import query_events, verify_chain
        events = query_events(limit=10000)
        chain_valid, chain_msg = verify_chain()
        audit_data = {
            "chain_valid": chain_valid,
            "chain_message": chain_msg,
            "event_count": len(events),
            "events": events,
        }
        audit_json = json.dumps(audit_data, indent=2, default=str)
        _write_and_record(pack_dir, "05-audit-trail.json", audit_json, file_records)
    except (ImportError, OSError, ValueError):
        pass  # optional section; skip if module missing or data error

    # --- 06: Remediation plan ---
    plan = generate_plan(findings, gap, project_name=name)
    plan_text = format_plan_text(plan)
    _write_and_record(pack_dir, "06-remediation-plan.md", plan_text, file_records)

    # --- 07: Risk decisions (ISO 42001 6.1.4, EU AI Act Article 11) ---
    all_decisions = [
        f.get("risk_decision") for f in findings if f.get("risk_decision")
    ]
    suppressed_list = [d for d in all_decisions if d.get("type") == "ignore"]
    accepted_list = [d for d in all_decisions if d.get("type") == "accept"]
    overdue_count = sum(1 for d in accepted_list if d.get("overdue", False))
    risk_decisions_data = {
        "schema_version": "1.0",
        "generated_at": now.isoformat(),
        "suppressed_findings": suppressed_list,
        "accepted_risks": accepted_list,
        "summary": {
            "total_suppressed": len(suppressed_list),
            "total_accepted": len(accepted_list),
            "accepted_overdue": overdue_count,
        },
    }
    rd_json = json.dumps(risk_decisions_data, indent=2, default=str)
    _write_and_record(pack_dir, "07-risk-decisions.json", rd_json, file_records)

    # --- 08: Runtime monitor (optional) ---
    runtime_system = kwargs.get("runtime_system_id")
    if runtime_system:
        try:
            from cli_monitor import _read_all_events, _verify_chain
            rt_events = _read_all_events(runtime_system)
            rt_valid, rt_msg = _verify_chain(rt_events)
            inferences = [e for e in rt_events if e.get("event_type") == "inference"]
            errors = [e for e in rt_events if e.get("status") == "error"]
            summaries = [e for e in rt_events if e.get("event_type") == "session_summary"]
            rt_data = {
                "system_id": runtime_system,
                "chain_valid": rt_valid,
                "chain_message": rt_msg,
                "total_events": len(rt_events),
                "total_inferences": len(inferences),
                "total_errors": len(errors),
                "sessions": len(summaries),
                "session_summaries": summaries,
            }
            rt_json = json.dumps(rt_data, indent=2, default=str)
            _write_and_record(pack_dir, "08-runtime-monitor.json", rt_json, file_records)
        except (ImportError, OSError, ValueError):
            pass

    # --- 00: Executive summary (written last, uses data from above) ---
    summary = _generate_summary(name, now, findings, gap, plan)
    _write_and_record(pack_dir, "00-summary.md", summary, file_records)

    # --- README ---
    readme = _generate_readme(name, date_str)
    _write_and_record(pack_dir, "README.md", readme, file_records)

    # --- Manifest (written last) ---
    manifest = {
        "schema_version": "1.0",
        "regula_version": VERSION,
        "generated_at": now.isoformat(),
        "project": name,
        "project_path": str(project),
        "files": file_records,
    }
    manifest_json = json.dumps(manifest, indent=2)
    (pack_dir / "manifest.json").write_text(manifest_json, encoding="utf-8")

    return {
        "pack_dirname": pack_name,
        "pack_path": str(pack_dir),
        "manifest": manifest,
    }


def _write_and_record(pack_dir: Path, filename: str, content: str, records: list):
    """Write a file and record its hash."""
    (pack_dir / filename).write_text(content, encoding="utf-8")
    records.append({
        "filename": filename,
        "sha256": _sha256(content),
        "size_bytes": len(content.encode("utf-8")),
    })


def _generate_summary(name, now, findings, gap, plan):
    """Generate the executive summary document."""
    highest = gap.get("highest_risk", "unknown")
    overall_score = gap.get("overall_score", 0)
    total_findings = len(findings)
    prohibited_count = sum(1 for f in findings if f.get("tier") == "prohibited")
    high_risk_count = sum(1 for f in findings if f.get("tier") == "high_risk")
    limited_count = sum(1 for f in findings if f.get("tier") == "limited_risk")

    articles = gap.get("articles", {})
    article_lines = []
    for num in sorted(articles.keys(), key=lambda x: int(x)):
        data = articles[num]
        article_lines.append(
            f"| Article {num} | {data['title']} | {data['score']}% | {data['status'].upper()} |"
        )

    plan_total = plan.get("total_tasks", 0)
    effort_low = sum(
        t["effort_hours"][0] for t in plan.get("tasks", [])
        if isinstance(t.get("effort_hours"), (list, tuple))
    )
    effort_high = sum(
        t["effort_hours"][1] for t in plan.get("tasks", [])
        if isinstance(t.get("effort_hours"), (list, tuple))
    )

    return f"""# Evidence Pack — Executive Summary

**Project:** {name}
**Generated:** {now.strftime("%Y-%m-%d %H:%M UTC")}
**Tool:** Regula v{VERSION}

---

## Risk Classification

**Highest risk tier found:** {highest.upper().replace('_', '-')}

| Category | Count |
|----------|-------|
| Prohibited findings | {prohibited_count} |
| High-risk findings | {high_risk_count} |
| Limited-risk findings | {limited_count} |
| Total findings | {total_findings} |

## Compliance Gap Assessment

**Overall compliance score:** {overall_score}%

| Article | Requirement | Score | Status |
|---------|-------------|-------|--------|
{chr(10).join(article_lines)}

## Remediation Summary

**Total tasks:** {plan_total}
**Estimated effort:** ~{effort_low}-{effort_high} hours
**Primary deadline:** 2 August 2026

## Pack Contents

| File | Description |
|------|-------------|
| 00-summary.md | This document |
| 01-scan-results.json | All scan findings with file locations and risk tiers |
| 02-gap-assessment.json | Per-article compliance gap scores and evidence |
| 03-annex-iv-draft.md | Auto-generated Annex IV technical documentation |
| 04-dependency-report.json | AI dependency pinning scores and supply chain analysis |
| 05-audit-trail.json | Hash-chained audit events with integrity verification |
| 06-remediation-plan.md | Prioritised action items with effort estimates |
| manifest.json | SHA-256 hashes of all files for tamper detection |

---

_This evidence pack is generated by automated analysis and is not a legal
determination. All findings should be reviewed by qualified personnel._
"""


def _generate_readme(name, date_str):
    """Generate the README for the evidence pack."""
    return f"""# Evidence Pack: {name}

Generated on {date_str} by Regula v{VERSION}.

## How to use this pack

This folder contains everything needed for a compliance readiness review
of the AI system "{name}" under the EU AI Act (Regulation 2024/1689).

**For consultants / auditors:**
1. Start with `00-summary.md` for an overview
2. Review `02-gap-assessment.json` for per-article compliance scores
3. Review `03-annex-iv-draft.md` for technical documentation status
4. Check `06-remediation-plan.md` for outstanding tasks

**For developers:**
1. Read `06-remediation-plan.md` and work through tasks in order
2. Re-run `regula evidence-pack` after completing tasks to update scores

## Integrity verification

`manifest.json` contains SHA-256 hashes of every file in this pack.
To verify no files have been modified:

```python
import hashlib, json, pathlib
manifest = json.loads(pathlib.Path("manifest.json").read_text())
for f in manifest["files"]:
    content = pathlib.Path(f["filename"]).read_bytes()
    actual = hashlib.sha256(content).hexdigest()
    status = "OK" if actual == f["sha256"] else "MODIFIED"
    print(f"  {{status}}: {{f['filename']}}")
```

---

_Generated by Regula — AI Governance Risk Indication_
_Findings are indicators, not legal determinations._
"""


_VERIFY_SCRIPT = '''\
#!/usr/bin/env python3
"""Standalone integrity verifier for a Regula evidence bundle.

Run this script from the directory containing the extracted evidence files
and manifest.json. It checks SHA-256 hashes of every file listed in the
manifest and reports any mismatches or missing files.

Exit code 0 = all files verified. Exit code 1 = integrity error(s).
"""
import hashlib
import json
import sys
from pathlib import Path


def main():
    manifest_path = Path("manifest.json")
    if not manifest_path.exists():
        print("FAIL: manifest.json not found in current directory")
        sys.exit(1)

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = manifest.get("files", [])

    if not files:
        print("FAIL: manifest contains no file entries")
        sys.exit(1)

    errors = 0
    for entry in files:
        filename = entry["filename"]
        expected_sha = entry["sha256"]
        if ".." in Path(filename).parts:
            print(f"  SKIP (invalid path): {filename}", file=sys.stderr)
            continue
        fpath = Path(filename)
        if not fpath.exists():
            print(f"  MISSING: {filename}")
            errors += 1
            continue
        actual_sha = hashlib.sha256(fpath.read_bytes()).hexdigest()
        if actual_sha != expected_sha:
            print(f"  MODIFIED: {filename}")
            errors += 1
        else:
            print(f"  OK: {filename}")

    if errors:
        print(f"FAIL: {errors} integrity error(s)")
        sys.exit(1)
    else:
        print(f"OK: {len(files)} files verified")
        sys.exit(0)


if __name__ == "__main__":
    main()
'''


def generate_bundle(pack_dir: str) -> str:
    """Package an evidence pack directory into a self-verifying ZIP bundle."""
    pack = Path(pack_dir)
    if not (pack / "manifest.json").exists():
        raise FileNotFoundError(f"No manifest.json in {pack_dir}")

    bundle_path = str(pack) + ".regula-evidence.zip"
    with zipfile.ZipFile(bundle_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for fpath in sorted(pack.iterdir()):
            if fpath.is_file():  # Pack dirs are flat by design; subdirs skipped
                zf.write(fpath, fpath.name)
        zf.writestr("verify.py", _VERIFY_SCRIPT)
    return bundle_path
