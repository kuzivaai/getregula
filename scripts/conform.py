#!/usr/bin/env python3
# regula-ignore
"""
Regula Conformity Assessment Evidence Pack Generator

Produces a structured folder mapped to EU AI Act articles (9-15) plus
supply chain and declaration of conformity artifacts. Each sub-folder
contains evidence files and a coverage.json that honestly states what
Regula can auto-detect versus what requires human input.

No external dependencies — stdlib only.
"""

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from constants import VERSION


# ---------------------------------------------------------------------------
# Article definitions with human-required items
# ---------------------------------------------------------------------------

ARTICLES = {
    "9": {
        "title": "Risk Management",
        "folder": "02-risk-management-art9",
        "auto_detected_keys": [
            "Compliance gap score for Article 9",
            "Evidence of risk management patterns in code",
        ],
        "requires_human": [
            "Risk management system documentation",
            "Residual risk assessment",
            "Risk acceptance criteria",
            "Post-market monitoring plan",
            "Stakeholder consultation records",
        ],
    },
    "10": {
        "title": "Data Governance",
        "folder": "03-data-governance-art10",
        "auto_detected_keys": [
            "Compliance gap score for Article 10",
            "Evidence of data handling patterns in code",
        ],
        "requires_human": [
            "Training data provenance documentation",
            "Data quality metrics and validation reports",
            "Bias examination on your deployment data (regula bias covers benchmarks only)",
            "Data governance policy document",
            "Dataset labelling procedures",
        ],
    },
    "11": {
        "title": "Technical Documentation",
        "folder": "04-technical-documentation-art11",
        "auto_detected_keys": [
            "Auto-generated Annex IV draft",
            "Architecture detection results",
        ],
        "requires_human": [
            "Intended purpose description",
            "Design specifications not derivable from code",
            "Interaction with other systems documentation",
            "Hardware requirements specification",
            "Validation and testing methodology",
        ],
    },
    "12": {
        "title": "Record-Keeping",
        "folder": "05-record-keeping-art12",
        "auto_detected_keys": [
            "Audit trail events (if regula audit is used)",
            "Compliance gap score for Article 12",
        ],
        "requires_human": [
            "Automatic logging system design documentation",
            "Log retention policy",
            "Log access control procedures",
            "Event traceability documentation",
        ],
    },
    "13": {
        "title": "Transparency",
        "folder": "06-transparency-art13",
        "auto_detected_keys": [
            "Compliance gap score for Article 13",
            "Evidence of transparency patterns in code",
        ],
        "requires_human": [
            "Instructions for use document",
            "Intended purpose statement for deployers",
            "Human-readable explanation of system capabilities and limitations",
            "Contact information for the provider",
        ],
    },
    "14": {
        "title": "Human Oversight",
        "folder": "07-human-oversight-art14",
        "auto_detected_keys": [
            "Compliance gap score for Article 14",
            "Evidence of human oversight patterns in code",
        ],
        "requires_human": [
            "Human oversight measures documentation",
            "Human-machine interface design rationale",
            "Override and intervention procedures",
            "Operator training requirements",
        ],
    },
    "15": {
        "title": "Accuracy, Robustness, Cybersecurity",
        "folder": "08-accuracy-robustness-art15",
        "auto_detected_keys": [
            "Compliance gap score for Article 15",
            "CycloneDX SBOM (supply chain analysis)",
            "Dependency vulnerability scan",
        ],
        "requires_human": [
            "Accuracy metrics and benchmarks",
            "Robustness testing results",
            "Cybersecurity risk assessment",
            "Redundancy and fail-safe documentation",
        ],
    },
}


def _derive_deadline_summary(findings: list) -> dict:
    """Derive deadline range from actual finding data instead of hard-coding."""
    deadline_dates = {f.get("deadline") for f in findings if f.get("deadline")}
    omnibus_dates = {f.get("omnibus_deadline") for f in findings if f.get("omnibus_deadline")}
    return {
        "earliest_enforceable": min(deadline_dates) if deadline_dates else "2026-08-02",
        "omnibus_proposed_range": sorted(omnibus_dates) if omnibus_dates else ["2027-12-02"],
        "note": "Per-finding deadlines available in 01-risk-classification/findings.json",
    }


def _sha256(content: str) -> str:
    """Return hex SHA-256 of string content."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _write_and_record(path: Path, content: str, records: list, pack_dir: Path = None):
    """Write a file, record its hash with path relative to pack root."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    # Store relative path if pack_dir provided, else filename only
    rel = str(path.resolve().relative_to(pack_dir.resolve())) if pack_dir else path.name
    records.append({
        "filename": rel,
        "sha256": _sha256(content),
        "size_bytes": len(content.encode("utf-8")),
    })


def _make_coverage(article_num: str, auto_detected: list, gap_data: dict) -> dict:
    """Build coverage.json for an article."""
    meta = ARTICLES[article_num]
    score = gap_data.get("score", 0) if gap_data else 0
    return {
        "article": int(article_num),
        "title": meta["title"],
        "auto_detected": auto_detected,
        "requires_human_input": meta["requires_human"],
        "readiness": f"{score}%",
    }


def generate_sme_simplified_pack(
    project_path: str,
    output_dir: str = ".",
    project_name: str = None,
) -> dict:
    """Generate the SME-simplified Annex IV technical documentation.

    Article 11(1) second subparagraph allows SME providers to provide the
    elements of Annex IV in a simplified manner. The Commission is
    required to establish an official simplified form for SMEs but had
    not published it as of 2026-04-08. This function produces the
    interim simplified format as a single Markdown file (rather than the
    full multi-folder pack produced by `generate_conformity_pack`).

    Returns a dict matching the shape `cmd_conform` expects, with
    summary["overall_readiness"] reflecting the simplified form's
    readiness rather than the full Article 9-15 gap score.
    """
    from generate_documentation import scan_project, generate_sme_simplified_annex_iv

    project = Path(project_path).resolve()
    name = project_name or project.name
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y-%m-%d")

    out_dir = Path(output_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"simplified-annex-iv-{name}-{date_str}.md"

    doc_findings = scan_project(str(project))
    doc = generate_sme_simplified_annex_iv(doc_findings, name, str(project))
    out_path.write_text(doc, encoding="utf-8")

    sha256 = hashlib.sha256(doc.encode("utf-8")).hexdigest()
    file_record = {
        "path": out_path.name,
        "sha256": sha256,
        "size_bytes": len(doc.encode("utf-8")),
    }

    manifest = {
        "regula_version": VERSION,
        "generated_at": now.isoformat(),
        "project": name,
        "project_directory": project.name,
        "form": "sme_simplified_annex_iv",
        "interim_format_disclosure": (
            "Article 11(1) second subparagraph allows SMEs to provide the "
            "elements of Annex IV in a simplified manner. The Commission is "
            "required to establish an official simplified form for SMEs but "
            "had not published it as of 2026-04-08. This document is an "
            "interim format that should be replaced with the official "
            "Commission template when published."
        ),
        "files": [file_record],
    }

    summary = {
        "regula_version": VERSION,
        "generated_at": now.isoformat(),
        "project": name,
        "form": "sme_simplified_annex_iv",
        "overall_readiness": "interim — Commission template pending",
        "output_file": str(out_path),
    }

    return {
        "pack_dirname": out_path.name,
        "pack_path": str(out_path),
        "manifest": manifest,
        "summary": summary,
    }


def generate_conformity_pack(
    project_path: str,
    output_dir: str = ".",
    project_name: str = None,
) -> dict:
    """Generate a conformity assessment evidence pack mapped by article.

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
    name = project_name or project.name
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y-%m-%d")
    pack_name = f"conformity-evidence-{name}-{date_str}"
    pack_dir = (Path(output_dir) / pack_name).resolve()
    pack_dir.mkdir(parents=True, exist_ok=True)

    file_records = []

    # --- Gather data from existing modules ---
    findings = scan_files(str(project))
    gap = assess_compliance(str(project))
    doc_findings = scan_project(str(project))
    annex_iv = generate_annex_iv(doc_findings, name, str(project))
    plan = generate_plan(findings, gap, project_name=name)
    plan_text = format_plan_text(plan)

    # SBOM (optional)
    sbom_data = None
    try:
        from sbom import generate_sbom
        sbom_data = generate_sbom(str(project), project_name=name, ai_bom=True)
    except ImportError:
        pass
    except Exception as e:
        print(f"Warning: SBOM generation failed: {e}", file=sys.stderr)

    # Audit trail (optional)
    audit_data = None
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
    except ImportError:
        pass
    except (OSError, ValueError) as e:
        print(f"Note: audit trail not available: {e}", file=sys.stderr)

    # Dependency report (optional)
    dep_report = None
    try:
        from dependency_scan import scan_dependencies
        dep_report = scan_dependencies(str(project))
    except ImportError:
        pass
    except (OSError, ValueError, KeyError) as e:
        print(f"Note: dependency scan not available: {e}", file=sys.stderr)

    articles_data = gap.get("articles", {})

    # --- 01: Risk Classification ---
    rc_dir = pack_dir / "01-risk-classification"
    rc_dir.mkdir(parents=True, exist_ok=True)
    findings_json = json.dumps(findings, indent=2, default=str)
    _write_and_record(rc_dir / "findings.json", findings_json, file_records, pack_dir)

    auto_items_rc = []
    total = len(findings)
    prohibited = sum(1 for f in findings if f.get("tier") == "prohibited")
    high = sum(1 for f in findings if f.get("tier") == "high_risk")
    limited = sum(1 for f in findings if f.get("tier") == "limited_risk")
    auto_items_rc.append(f"Scanned project: {total} findings ({prohibited} prohibited, {high} high-risk, {limited} limited)")

    rc_coverage = {
        "article": "classification",
        "title": "Risk Classification",
        "auto_detected": auto_items_rc,
        "requires_human_input": [
            "Confirmation of intended purpose",
            "Verification of risk tier assignment",
            "Determination of Annex III applicability",
        ],
        "readiness": "complete" if total > 0 else "not-run",
    }
    _write_and_record(rc_dir / "coverage.json", json.dumps(rc_coverage, indent=2), file_records, pack_dir)

    # --- Articles 9-15 ---
    article_summary = {}
    for art_num in ["9", "10", "11", "12", "13", "14", "15"]:
        meta = ARTICLES[art_num]
        art_dir = pack_dir / meta["folder"]
        art_dir.mkdir(parents=True, exist_ok=True)
        art_gap = articles_data.get(art_num, {})

        auto_detected = []
        if art_gap:
            auto_detected.append(f"Compliance gap score: {art_gap.get('score', 0)}%")
            for ev in art_gap.get("evidence", []):
                if isinstance(ev, str):
                    auto_detected.append(ev)
                elif isinstance(ev, dict):
                    auto_detected.append(ev.get("description", str(ev)))

        # Article-specific extra files
        if art_num == "11":
            # Annex IV draft
            _write_and_record(art_dir / "annex-iv-draft.md", annex_iv, file_records, pack_dir)
            auto_detected.append("Auto-generated Annex IV technical documentation draft")

        if art_num == "12" and audit_data:
            _write_and_record(art_dir / "audit-trail.json", json.dumps(audit_data, indent=2, default=str), file_records, pack_dir)
            auto_detected.append(f"Audit trail: {audit_data['event_count']} events, chain valid: {audit_data['chain_valid']}")

        if art_num == "14":
            # Cross-file Article 14 oversight analysis
            try:
                from cross_file_flow import analyse_project_oversight
                oversight_result = analyse_project_oversight(str(project))
                oversight_json = json.dumps(oversight_result, indent=2, default=str)
                _write_and_record(art_dir / "oversight-analysis.json", oversight_json, file_records, pack_dir)
                summary = oversight_result.get("summary", {})
                total_paths = summary.get("total_paths", 0)
                reviewed = summary.get("reviewed", 0)
                unreviewed = summary.get("unreviewed", 0)
                if total_paths > 0:
                    auto_detected.append(f"Cross-file oversight analysis: {reviewed}/{total_paths} AI flow paths have human oversight gates")
                    if unreviewed > 0:
                        auto_detected.append(f"WARNING: {unreviewed} AI output path(s) reach user-facing output without human oversight")
                else:
                    auto_detected.append("Cross-file oversight analysis: no AI output sources detected")
            except (ImportError, Exception) as e:
                print(f"Warning: oversight analysis failed: {e}", file=sys.stderr)

        if art_num == "10":
            # Bias evaluation (optional — requires Ollama)
            try:
                from bias_eval import load_crowspairs_sample, evaluate_with_ollama
                from bias_bbq import load_bbq_sample, evaluate_bbq_full
                from bias_report import format_annex_iv, format_json_report

                # Try CrowS-Pairs
                cp_result = None
                try:
                    pairs = load_crowspairs_sample(max_pairs=100)
                    cp_result = evaluate_with_ollama(pairs, timeout=10)
                except Exception:
                    pass

                # Try BBQ
                bbq_result = None
                try:
                    items = load_bbq_sample(max_items=100)
                    bbq_result = evaluate_bbq_full(items, timeout=10)
                except Exception:
                    pass

                has_results = (
                    (cp_result and cp_result.get("status") == "ok")
                    or (bbq_result and bbq_result.get("status") == "ok")
                )

                if has_results:
                    annex_iv_bias = format_annex_iv(cp_result, bbq_result, "llama3", "http://localhost:11434")
                    _write_and_record(art_dir / "bias-evaluation.md", annex_iv_bias, file_records, pack_dir)
                    bias_json = format_json_report(cp_result, bbq_result, "llama3", "http://localhost:11434")
                    _write_and_record(art_dir / "bias-evaluation.json", json.dumps(bias_json, indent=2, default=str), file_records, pack_dir)
                    auto_detected.append("Bias evaluation: CrowS-Pairs + BBQ benchmark results with confidence intervals")
                else:
                    auto_detected.append("Bias evaluation: Ollama not available — run 'regula bias' separately to generate bias evidence")
            except ImportError:
                auto_detected.append("Bias evaluation: run 'regula bias' separately to generate bias evidence")
            except Exception as e:
                print(f"Note: bias evaluation skipped: {e}", file=sys.stderr)

        if art_num == "15" and sbom_data:
            _write_and_record(art_dir / "sbom.json", json.dumps(sbom_data, indent=2, default=str), file_records, pack_dir)
            auto_detected.append("CycloneDX 1.6 SBOM generated")

        # Evidence file (gap data)
        evidence = {
            "article": int(art_num),
            "title": meta["title"],
            "gap_score": art_gap.get("score", 0),
            "status": art_gap.get("status", "not_found"),
            "evidence_found": art_gap.get("evidence", []),
            "gaps_identified": art_gap.get("gaps", []),
        }
        _write_and_record(art_dir / "evidence.json", json.dumps(evidence, indent=2, default=str), file_records, pack_dir)

        # Coverage file
        coverage = _make_coverage(art_num, auto_detected, art_gap)
        _write_and_record(art_dir / "coverage.json", json.dumps(coverage, indent=2, default=str), file_records, pack_dir)

        score = art_gap.get("score", 0)
        status = art_gap.get("status", "not_found")
        evidence_files = [
            str(Path(meta["folder"]) / "evidence.json"),
            str(Path(meta["folder"]) / "coverage.json"),
        ]
        article_summary[art_num] = {
            "title": meta["title"],
            "status": status,
            "auto_coverage": f"{score}%",
            "evidence_files": evidence_files,
        }

    # --- 09: Supply Chain ---
    sc_dir = pack_dir / "09-supply-chain"
    sc_dir.mkdir(parents=True, exist_ok=True)
    if dep_report:
        _write_and_record(sc_dir / "dependency-report.json", json.dumps(dep_report, indent=2, default=str), file_records, pack_dir)
    if sbom_data:
        _write_and_record(sc_dir / "sbom.json", json.dumps(sbom_data, indent=2, default=str), file_records, pack_dir)
    if not dep_report and not sbom_data:
        placeholder = json.dumps({"note": "No dependency or SBOM data available. Run regula sbom for supply chain analysis."}, indent=2)
        _write_and_record(sc_dir / "dependency-report.json", placeholder, file_records, pack_dir)

    # --- 10: Declaration of Conformity ---
    decl_dir = pack_dir / "10-declaration-of-conformity"
    decl_dir.mkdir(parents=True, exist_ok=True)
    overall_score = gap.get("overall_score", 0)
    declaration = _generate_declaration_template(name, now, overall_score, gap.get("highest_risk", "unknown"))
    _write_and_record(decl_dir / "declaration-template.md", declaration, file_records, pack_dir)

    # --- 11: Remediation ---
    rem_dir = pack_dir / "11-remediation"
    rem_dir.mkdir(parents=True, exist_ok=True)
    _write_and_record(rem_dir / "remediation-plan.md", plan_text, file_records, pack_dir)

    # --- Determine what's auto-generated vs human-required ---
    human_required = [
        "Intended purpose description",
        "Fundamental Rights Impact Assessment (FRIA)",
        "Post-market monitoring plan",
        "Training data provenance documentation",
        "Instructions for use",
        "Human oversight measures documentation",
        "Accuracy metrics and benchmarks",
        "Robustness testing results",
    ]
    auto_generated = [
        "Risk classification",
        "Technical documentation draft (Annex IV)",
        "Supply chain analysis (SBOM)",
        "Audit trail",
        "Remediation plan",
        "Per-article gap assessment",
    ]

    # --- 00: Assessment Summary ---
    summary = {
        "regula_version": VERSION,
        "generated_at": now.isoformat(),
        "project": name,
        "conformity_type": "internal (Annex VI, Module A)",
        "overall_readiness": f"{overall_score}%",
        "articles": article_summary,
        "deadline": _derive_deadline_summary(findings),
        "human_required": human_required,
        "auto_generated": auto_generated,
    }
    _write_and_record(pack_dir / "00-assessment-summary.json", json.dumps(summary, indent=2), file_records, pack_dir)

    # --- README ---
    readme = _generate_readme(name, date_str, overall_score)
    _write_and_record(pack_dir / "README.md", readme, file_records, pack_dir)

    # --- Manifest (written last — file_records already contain relative paths) ---

    manifest = {
        "regula_version": VERSION,
        "generated_at": now.isoformat(),
        "project": name,
        "project_directory": project.name,
        "files": file_records,
    }
    manifest_json = json.dumps(manifest, indent=2)
    (pack_dir / "manifest.json").write_text(manifest_json, encoding="utf-8")

    return {
        "pack_dirname": pack_name,
        "pack_path": str(pack_dir),
        "manifest": manifest,
        "summary": summary,
    }


def _generate_declaration_template(name: str, now: datetime, score: int, risk_tier: str) -> str:
    """Generate an Article 47 declaration of conformity template."""
    return f"""# EU Declaration of Conformity

**Pursuant to Article 47 of Regulation (EU) 2024/1689 (AI Act)**

---

## 1. AI System Identification

- **System name:** {name}
- **Version:** [TO BE COMPLETED]
- **EU Identification Number:** [TO BE COMPLETED — assigned at registration in Article 71 EU database]
- **Unique identification:** [TO BE COMPLETED]

## 2. Provider Information

- **Name:** [TO BE COMPLETED]
- **Address:** [TO BE COMPLETED]
- **Contact:** [TO BE COMPLETED]

## 3. Declaration

This declaration of conformity is issued under the sole responsibility of the provider.

The AI system described above is in conformity with the following provisions of Regulation (EU) 2024/1689:

- [ ] Article 9 — Risk management system
- [ ] Article 10 — Data and data governance
- [ ] Article 11 — Technical documentation
- [ ] Article 12 — Record-keeping
- [ ] Article 13 — Transparency and provision of information to deployers
- [ ] Article 14 — Human oversight
- [ ] Article 15 — Accuracy, robustness and cybersecurity

## 4. Conformity Assessment

- **Assessment type:** Internal (Annex VI, Module A)
- **Assessment date:** {now.strftime("%Y-%m-%d")}
- **Automated readiness score:** {score}% (generated by Regula v{VERSION})

## 5. Standards Applied

[TO BE COMPLETED — list harmonised standards or common specifications applied]

## 6. Notified Body

[If applicable — not required for internal conformity assessment under Module A]

## 7. Signature

Signed at [place], on [date]

[Name, function]
[Signature]

---

_This template was pre-filled by Regula v{VERSION}. All fields marked
[TO BE COMPLETED] require human input. The automated readiness score
is an indicator only — it does not constitute a legal determination
of conformity. The risk tier detected was: {risk_tier}._
"""


def _generate_readme(name: str, date_str: str, score: int) -> str:
    """Generate the README for the conformity evidence pack."""
    return f"""# Conformity Assessment Evidence Pack: {name}

Generated on {date_str} by Regula v{VERSION}.

## What is this?

This folder contains evidence structured by EU AI Act article for a
conformity assessment of the AI system "{name}" under Regulation (EU)
2024/1689. It follows the internal conformity assessment procedure
described in Annex VI (Module A).

## How to use this pack

**For auditors / notified bodies:**
1. Start with `00-assessment-summary.json` for overall readiness
2. Each numbered folder maps to an EU AI Act article
3. Every folder contains a `coverage.json` that honestly states what
   was auto-detected vs what requires human input
4. Review `10-declaration-of-conformity/` for the declaration template

**For providers / developers:**
1. Check `00-assessment-summary.json` to see your readiness score
2. Review `human_required` items — these cannot be auto-generated
3. Work through `11-remediation/remediation-plan.md`
4. Re-run `regula conform` after making changes to track progress

## Honesty note

Regula auto-generates what it can from code analysis. Many conformity
requirements (intended purpose, FRIA, training data provenance) require
human knowledge that cannot be derived from source code. Each coverage.json
file explicitly lists what Regula cannot determine. This transparency is
intentional — it prevents false confidence in automated compliance.

## Overall readiness: {score}%

## Integrity verification

`manifest.json` contains SHA-256 hashes of every file in this pack.

---

_Generated by Regula v{VERSION} — AI Governance Risk Indication_
_Findings are indicators, not legal determinations._
"""
