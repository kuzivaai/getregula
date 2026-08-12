#!/usr/bin/env python3
# regula-ignore
"""
Regula Evidence Pack Generator

Produces a structured folder of detector observations, declared facts, and
supporting material for qualified regulatory review.

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
    sign: bool = False,
    signing_key_path=None,
    timestamp: bool = False,
    tsa_url: str = None,
    engagement: dict = None,
    **kwargs,
) -> dict:
    """Generate a complete evidence pack for a project.

    Args:
        project_path: Path to the project to scan.
        output_dir: Parent directory for the pack folder.
        project_name: Human-readable name (defaults to directory name).
        engagement: Optional consultant engagement metadata (see
            engagement.py: client / prepared_by / reference). When
            present, an `engagement` object is added to the manifest
            (inside the signed content, so it is tamper-evident). When
            absent, the manifest is byte-identical to previous releases.
        sign: Sign the manifest with an Ed25519 key (Regula Evidence
            Format v1.1 §4.5). When any security option is active the
            manifest additionally declares the Evidence Format v1 fields
            (`format`, `format_version`, `schema_uri`, `hash_algorithm`)
            so `regula verify` accepts the pack; the legacy
            `schema_version` field is kept for older consumers.
        signing_key_path: Optional Ed25519 key location override
            (default ~/.regula/signing.key or REGULA_SIGNING_KEY).
        timestamp: Request an RFC 3161 timestamp over the signed
            canonical manifest form (§4.6). Implies sign.
        tsa_url: TSA endpoint (default FreeTSA).

    Returns:
        Dict with pack_dirname, pack_path, and manifest.
    """
    # Reject invalid combinations before writing any files.
    if timestamp and not sign:
        raise ValueError(
            "--timestamp requires --sign (timestamp covers the signed "
            "canonical manifest form per spec §4.6)."
        )

    project = Path(project_path).resolve()
    # Sanitise project name to prevent path traversal (OWASP input validation)
    name = re.sub(r'[^a-zA-Z0-9_\-]', '_', project_name or project.name)
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y-%m-%d")
    pack_name = f"evidence-pack-{name}-{date_str}"
    pack_dir = Path(output_dir) / pack_name
    # Fail-closed: if generation aborts after files are written but before
    # manifest.json exists (e.g. --sign without the [signing] extra), a
    # half-pack that `regula verify` rejects must not be left on disk —
    # an evidence artefact either completes with its manifest or does not
    # exist. Only a directory WE created is removed on failure; a
    # pre-existing same-day directory is left in place and the error
    # message from the CLI layer still explains the failure.
    _pack_dir_pre_existing = pack_dir.exists()
    pack_dir.mkdir(parents=True, exist_ok=True)

    try:
        return _generate_pack_contents(
            project, name, now, date_str, pack_name, pack_dir,
            sign=sign, signing_key_path=signing_key_path,
            timestamp=timestamp, tsa_url=tsa_url,
            engagement=engagement, **kwargs,
        )
    except BaseException:
        if not _pack_dir_pre_existing:
            import shutil
            shutil.rmtree(pack_dir, ignore_errors=True)
        raise


def _generate_pack_contents(
    project, name, now, date_str, pack_name, pack_dir,
    *, sign, signing_key_path, timestamp, tsa_url, engagement, **kwargs,
):
    """Write every pack artefact and the manifest. See generate_evidence_pack."""
    from report import scan_files
    from compliance_check import assess_compliance
    from generate_documentation import scan_project, generate_annex_iv
    from decision_adapters import (
        detector_findings,
        empty_decision,
        resolved_gap_evidence,
        unresolved_documentation_draft,
    )

    file_records = []

    # --- 01: Scan results ---
    findings = scan_files(str(project))
    decision = empty_decision("eu", "evidence-pack:no-declared-facts")
    scan_json = json.dumps(detector_findings(findings), indent=2, default=str)
    _write_and_record(pack_dir, "01-scan-results.json", scan_json, file_records)

    # --- 02: Gap assessment ---
    gap = assess_compliance(str(project))
    gap_json = json.dumps({
        "decision": decision,
        "evidence": resolved_gap_evidence(gap, decision),
    }, indent=2, default=str)
    _write_and_record(pack_dir, "02-gap-assessment.json", gap_json, file_records)

    # --- 03: Annex IV documentation ---
    doc_findings = scan_project(str(project))
    annex_iv = generate_annex_iv(doc_findings, name, str(project))
    annex_iv = unresolved_documentation_draft(annex_iv, str(project))
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
    # Strictly project-scoped: collect_audit_trail reads only this
    # project's own chain. A client pack must never contain audit events
    # from other projects on the consultant's machine.
    try:
        from log_event import collect_audit_trail
        audit_data = collect_audit_trail(str(project))
        audit_json = json.dumps(audit_data, indent=2, default=str)
        _write_and_record(pack_dir, "05-audit-trail.json", audit_json, file_records)
    except (ImportError, OSError, ValueError):
        pass  # optional section; skip if module missing or data error

    # --- 06: Facts required for a determination ---
    facts_text = _generate_resolvable_facts(decision)
    _write_and_record(pack_dir, "06-resolvable-facts.md", facts_text, file_records)

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
            from cli_monitor import _read_all_events, verify_monitor_chain
            rt_events = _read_all_events(runtime_system)
            rt_valid, rt_msg = verify_monitor_chain(runtime_system)
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

    # --- 09: DPV-AIAct machine-readable export (optional) ---
    # Off by default so the manifest stays byte-identical to prior releases
    # (backward-compat rule); `regula evidence-pack --dpv` opts in. Reuses the
    # findings already scanned above — no second scan. Aligned to the DPVCG
    # EU-AIAct vocabulary (a W3C Community Group report, not a ratified
    # standard); risk indication, not classification.
    include_dpv = (
        bool(kwargs.get("include_dpv"))
        and decision["result_type"] == "indication"
    )
    if include_dpv:
        try:
            from dpv_export import build_dpv_jsonld, format_dpv_jsonld
            dpv_meta = {
                "findingsScanned": len(findings),
                "activeFindings": sum(1 for f in findings if not f.get("suppressed")),
            }
            dpv_doc = build_dpv_jsonld(
                findings, project_name=name, scan_meta=dpv_meta,
                created=now.strftime("%Y-%m-%dT%H:%M:%SZ"))
            dpv_json = format_dpv_jsonld(dpv_doc)
            _write_and_record(pack_dir, "09-dpv-aiact.jsonld", dpv_json, file_records)
        except (ImportError, OSError, ValueError, KeyError, RuntimeError):
            # RuntimeError covers dpv_export._validate_mappings() firing on a
            # drifted vocab snapshot at import. The DPV section is OPTIONAL —
            # a vocab problem must only drop this one artifact, never abort (and
            # via the fail-closed handler, delete) the whole evidence pack.
            include_dpv = False  # section absent; README must not advertise it

    # --- 00: Executive summary (written last, uses data from above) ---
    summary = _generate_summary(name, now, findings, decision)
    _write_and_record(pack_dir, "00-summary.md", summary, file_records)

    # --- README ---
    readme = _generate_readme(name, date_str, include_dpv=include_dpv)
    _write_and_record(pack_dir, "README.md", readme, file_records)

    # --- Manifest (written last) ---
    # Every manifest declares the Evidence Format v1 fields (spec §4.1
    # lists `format` as REQUIRED). Until this change the declaration was
    # added only on the signing path, so every fresh UNSIGNED pack failed
    # spec conformance and `regula verify` hedged with "v0 best-effort
    # semantics" on packs Regula itself had just generated (walkthrough
    # P6). The change is versioned by the `format_version` field itself;
    # consumers MUST ignore unrecognised fields (spec §4.3), and `regula
    # verify` retains the v0 path for packs from older releases. The
    # legacy `schema_version` field is kept for older consumers.
    manifest = {
        "format": "regula.evidence.v1",
        "format_version": "1.0",  # bumped to 1.1 by apply_manifest_security
        "schema_uri": "https://getregula.com/spec/regula.manifest.v1.schema.json",
        "hash_algorithm": "sha256",
        "schema_version": "1.0",
        "regula_version": VERSION,
        "generated_at": now.isoformat(),
        "project": name,
        "project_directory": project.name,
        # Record the project BASENAME, not the absolute host path. Evidence
        # packs are shared with clients/auditors; the full resolved path
        # (str(project)) leaks the consultant's local directory layout and
        # usually the OS username, with no value to a recipient who cannot use
        # a path on someone else's machine.
        "project_path": project.name,
        "files": file_records,
    }
    # Optional consultant engagement block. Added before signing so the
    # signature and any RFC 3161 timestamp cover it. Omitted entirely
    # when not configured.
    if engagement:
        manifest["engagement"] = dict(engagement)
    if sign:
        from signing import apply_manifest_security
        apply_manifest_security(
            manifest,
            sign=sign,
            signing_key_path=signing_key_path,
            timestamp=timestamp,
            tsa_url=tsa_url,
        )
    manifest_json = json.dumps(manifest, indent=2)
    # newline="\n": write_text defaults to os.linesep translation, which
    # would break the recorded SHA-256 hashes on Windows (hashes are
    # computed on the LF content).
    (pack_dir / "manifest.json").write_text(manifest_json, encoding="utf-8", newline="\n")

    return {
        "pack_dirname": pack_name,
        "pack_path": str(pack_dir),
        "manifest": manifest,
    }


def _write_and_record(pack_dir: Path, filename: str, content: str, records: list):
    """Write a file and record its hash."""
    (pack_dir / filename).write_text(content, encoding="utf-8", newline="\n")
    records.append({
        "filename": filename,
        "sha256": _sha256(content),
        "size_bytes": len(content.encode("utf-8")),
    })


def _generate_summary(name, now, findings, decision):
    """Put the reliance qualification before every supporting artefact."""
    total_findings = len(findings)
    prohibited_count = sum(1 for f in findings if f.get("tier") == "prohibited")
    high_risk_count = sum(1 for f in findings if f.get("tier") == "high_risk")
    limited_count = sum(1 for f in findings if f.get("tier") == "limited_risk")
    unresolved_count = len(decision.get("unresolved_predicates", []))

    return f"""# Evidence Pack: Review Handoff

**Project:** {name}
**Generated:** {now.strftime("%Y-%m-%d %H:%M UTC")}
**Tool:** Regula v{VERSION}

## Decision status

**Kernel result:** `{decision['result_type']}`
**Model:** `{decision['model_version']}`
**Rule resolution:** `{decision['rule_resolution']}`
**Unresolved facts:** {unresolved_count}

No legal classification, article duty, readiness percentage, or effort estimate
is emitted because the generator received no sourced decision facts. Resolve
the questions in `06-resolvable-facts.md` before relying on an applicability
conclusion.

## Detector observations

| Category | Count |
|----------|-------|
| Article 5 pattern observations | {prohibited_count} |
| Annex III pattern observations | {high_risk_count} |
| Article 50 pattern observations | {limited_count} |
| Total detector observations | {total_findings} |

## Pack contents

| File | Description |
|------|-------------|
| 00-summary.md | This reliance gate and handoff summary |
| 01-scan-results.json | Code detector observations, not legal facts |
| 02-gap-assessment.json | Kernel decision plus evidence held pending applicability |
| 03-annex-iv-draft.md | Unverified documentation draft |
| 04-dependency-report.json | Supply-chain observations |
| 05-audit-trail.json | Project-scoped audit events and integrity observations |
| 06-resolvable-facts.md | Sourced facts needed for a determination |
| manifest.json | SHA-256 hashes of pack files |

Stop here before relying on the remaining content. Automated observations do
not establish applicability or compliance. Qualified review must resolve the
listed facts and verify every supporting artefact.
"""


def _generate_resolvable_facts(decision):
    lines = [
        "# Facts required before a determination",
        "",
        "The generator received no sourced decision facts. Each answer must include provenance and a timestamp.",
        "",
    ]
    for index, item in enumerate(decision.get("unresolved_predicates", []), 1):
        lines.append(f"{index}. `{item['fact_id']}`: {item['question']}")
        paths = "; ".join(
            f"{path['predicate_id']} ({path['provision']})"
            for path in item.get("would_resolve", [])
        )
        if paths:
            lines.append(f"   Resolves: {paths}")
    lines.extend(["", "Do not infer an answer from the absence of a detector finding.", ""])
    return "\n".join(lines)


def _generate_readme(name, date_str, include_dpv=False):
    """Generate the README for the evidence pack.

    include_dpv adds a line documenting the optional 09-dpv-aiact.jsonld
    artifact. It is False by default so the README (and therefore the manifest
    that hashes it) stays byte-identical to prior releases unless the DPV
    export was actually written.
    """
    dpv_line = (
        "\n**Machine-readable (optional):**\n"
        "- `09-dpv-aiact.jsonld` — the risk indication as JSON-LD tagged with "
        "DPVCG EU-AIAct vocabulary IRIs, for ingestion by RDF/GRC tooling. "
        "Aligned to a W3C Community Group vocabulary (not a ratified standard); "
        "risk indication, not classification.\n"
        if include_dpv else ""
    )
    return f"""# Evidence Pack: {name}

Generated on {date_str} by Regula v{VERSION}.

## How to use this pack

This folder contains detector observations and supporting material for review.
It does not establish that the subject is an AI system, that the EU AI Act
applies, or that any article duty attaches.

**Reliance gate:** Read `00-summary.md` and `06-resolvable-facts.md` before any
other artefact. Do not rely on templates or observations until those facts are
resolved with provenance.

**For consultants / auditors:**
1. Start with `00-summary.md` for an overview
2. Review `02-gap-assessment.json` for the kernel decision and held evidence
3. Review `03-annex-iv-draft.md` for technical documentation status
4. Resolve `06-resolvable-facts.md` with sourced evidence

**For developers:**
1. Resolve the facts in `06-resolvable-facts.md`
2. Re-run the decision assessment with sourced values
{dpv_line}

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
        if Path(filename).is_absolute() or ".." in Path(filename).parts:
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
