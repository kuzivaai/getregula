#!/usr/bin/env python3
# regula-ignore
"""
Regula Documentation Generator

Generates EU AI Act Annex IV documentation SCAFFOLDS and QMS (Quality Management
System) templates from project analysis.

Output is a starting point that requires human review and completion — it is
NOT complete compliance documentation and should not be presented as such.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from classify_risk import classify, RiskTier, is_ai_related, get_governance_contacts, check_ai_security
from cli import VERSION
from log_event import log_event
from code_analysis import analyse_project_code
from ast_analysis import parse_python_file, detect_human_oversight, detect_logging_practices, trace_ai_data_flow
from dependency_scan import parse_requirements_txt, parse_pyproject_toml, is_ai_dependency


def extract_ai_dependencies(project_path: str) -> list:
    """Extract AI dependency names and versions from requirements.txt/pyproject.toml.

    Returns a list of dicts: {name, version, source_file}
    """
    project = Path(project_path).resolve()
    ai_deps = []
    seen = set()

    for dep_file, parser in [
        ("requirements.txt", parse_requirements_txt),
        ("pyproject.toml", parse_pyproject_toml),
    ]:
        path = project / dep_file
        if not path.exists():
            continue
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
            deps = parser(content)
            for d in deps:
                if d["is_ai"] and d["name"] not in seen:
                    seen.add(d["name"])
                    ai_deps.append({
                        "name": d["name"],
                        "version": d.get("version"),
                        "source_file": dep_file,
                    })
        except (OSError, ValueError, KeyError):
            continue

    return ai_deps


def scan_project(project_path: str) -> dict:
    """Scan a project directory for AI-related files and patterns."""
    project = Path(project_path).resolve()
    findings = {
        "ai_files": [],
        "model_files": [],
        "classifications": [],
        "highest_risk": RiskTier.NOT_AI,
    }

    risk_order = {
        RiskTier.NOT_AI: 0, RiskTier.MINIMAL_RISK: 1,
        RiskTier.LIMITED_RISK: 2, RiskTier.HIGH_RISK: 3, RiskTier.PROHIBITED: 4,
    }

    skip_dirs = {".git", "node_modules", "__pycache__", "venv", ".venv", "dist", "build", ".next"}
    code_extensions = {".py", ".js", ".ts", ".jsx", ".tsx", ".mjs", ".cjs"}
    model_extensions = {".onnx", ".pt", ".pth", ".pkl", ".joblib", ".h5", ".hdf5", ".safetensors", ".gguf", ".ggml"}

    for root, dirs, files in os.walk(project):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for filename in files:
            filepath = Path(root) / filename
            rel_path = filepath.relative_to(project)

            if filepath.suffix in model_extensions:
                findings["model_files"].append(str(rel_path))
                continue

            if filepath.suffix in code_extensions:
                try:
                    content = filepath.read_text(encoding="utf-8", errors="ignore")
                except (PermissionError, OSError):
                    continue

                if is_ai_related(content):
                    findings["ai_files"].append(str(rel_path))
                    result = classify(content)
                    findings["classifications"].append({
                        "file": str(rel_path),
                        "tier": result.tier.value,
                        "indicators": result.indicators_matched,
                        "articles": result.applicable_articles,
                        "description": result.description,
                    })
                    if risk_order.get(result.tier, 0) > risk_order.get(findings["highest_risk"], 0):
                        findings["highest_risk"] = result.tier

    return findings


def ast_analyse_project(project_path: str) -> dict:
    """Run AST-based analysis across Python files to populate documentation sections.

    Returns:
        ai_imports      — sorted list of unique AI library imports detected
        ai_functions    — list of dicts {file, name, args} for non-test AI functions
        oversight_score — average oversight score (0-100) across files with AI calls
        oversight_evidence — list of oversight pattern dicts with file context
        automated_decisions — list of unreviewed automated decision paths
        logging_score   — average logging score (0-100) across files with AI calls
        total_logged    — AI operations with nearby logging
        total_unlogged  — AI operations without nearby logging
    """
    project = Path(project_path).resolve()
    skip_dirs = {".git", "node_modules", "__pycache__", "venv", ".venv",
                 "dist", "build", ".next", ".tox", "tests"}

    all_ai_imports: set = set()
    all_ai_functions: list = []
    oversight_scores: list = []
    all_oversight_evidence: list = []
    all_automated_decisions: list = []
    logging_scores: list = []
    total_logged = 0
    total_unlogged = 0
    all_data_flows: list = []

    for filepath in project.rglob("*.py"):
        if any(d in filepath.relative_to(project).parts for d in skip_dirs):
            continue
        try:
            content = filepath.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue

        rel = str(filepath.relative_to(project))

        parsed = parse_python_file(content)
        if not parsed["has_ai_code"]:
            continue

        # Collect AI imports
        all_ai_imports.update(parsed["ai_imports"])

        # Collect non-test function signatures (including new fields)
        for fn in parsed["function_defs"]:
            if not fn["is_test"]:
                all_ai_functions.append({
                    "file": rel,
                    "name": fn["name"],
                    "args": fn["args"],
                    "line": fn.get("line"),
                    "return_type": fn.get("return_type"),
                    "docstring": fn.get("docstring"),
                })

        # Oversight analysis
        oversight = detect_human_oversight(content)
        oversight_scores.append(oversight["oversight_score"])
        for p in oversight["oversight_patterns"]:
            all_oversight_evidence.append(dict(p, file=rel))
        for d in oversight["automated_decisions"]:
            all_automated_decisions.append(dict(d, file=rel))

        # Logging analysis
        logging = detect_logging_practices(content)
        logging_scores.append(logging["logging_score"])
        total_logged += logging["ai_operations_logged"]
        total_unlogged += logging["ai_operations_unlogged"]

        # Data flow tracing
        flows = trace_ai_data_flow(content)
        for flow in flows:
            all_data_flows.append(dict(flow, file=rel))

    oversight_score = int(sum(oversight_scores) / len(oversight_scores)) if oversight_scores else 50
    logging_score = int(sum(logging_scores) / len(logging_scores)) if logging_scores else 50

    # Normalise AI import names to top-level library names for readability
    top_level_imports: set = set()
    for imp in all_ai_imports:
        top_level_imports.add(imp.split(".")[0])

    return {
        "ai_imports": sorted(top_level_imports),
        "ai_functions": all_ai_functions,
        "oversight_score": oversight_score,
        "oversight_evidence": all_oversight_evidence,
        "automated_decisions": all_automated_decisions,
        "logging_score": logging_score,
        "total_logged": total_logged,
        "total_unlogged": total_unlogged,
        "data_flows": all_data_flows,
    }


def _governance_section() -> str:
    """Generate the governance contacts section from policy."""
    contacts = get_governance_contacts()
    if not contacts:
        return """### Governance Contacts
_[TO BE COMPLETED — configure in regula-policy.yaml]_

- **AI Officer:** _[Name, Role, Email]_
- **DPO:** _[Name, Email]_
"""

    ai_officer = contacts.get("ai_officer", {})
    dpo = contacts.get("dpo", {})

    lines = ["### Governance Contacts\n"]

    if ai_officer and (ai_officer.get("name") or ai_officer.get("role")):
        name = ai_officer.get("name", "_[TO BE COMPLETED]_")
        role = ai_officer.get("role", "AI Officer")
        email = ai_officer.get("email", "_[TO BE COMPLETED]_")
        lines.append(f"- **AI Officer:** {name} ({role}) — {email}")
    else:
        lines.append("- **AI Officer:** _[TO BE COMPLETED — set governance.ai_officer in regula-policy.yaml]_")

    if dpo and (dpo.get("name") or dpo.get("email")):
        name = dpo.get("name", "_[TO BE COMPLETED]_")
        email = dpo.get("email", "_[TO BE COMPLETED]_")
        lines.append(f"- **DPO:** {name} — {email}")
    else:
        lines.append("- **DPO:** _[TO BE COMPLETED — set governance.dpo in regula-policy.yaml]_")

    lines.append("")
    return "\n".join(lines)


def generate_annex_iv(findings: dict, project_name: str, project_path: str) -> str:
    """Generate Annex IV compliant documentation."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    highest = findings["highest_risk"]
    if isinstance(highest, RiskTier):
        highest = highest.value

    doc = f"""# Annex IV — Technical Documentation Scaffold

> **IMPORTANT:** This is an auto-generated scaffold, NOT complete compliance
> documentation. All sections marked _[TO BE COMPLETED]_ require human input.
> Risk indicators are pattern-based and may not reflect the actual risk
> classification under Article 6. This document must be reviewed by qualified
> personnel before being used as regulatory evidence.

## AI System: {project_name}

**Generated by:** Regula v{VERSION}
**Date:** {now}
**Overall Risk Classification:** {highest.upper().replace('_', '-')}

---

## 0. Governance

{_governance_section()}
---

## 1. General Description

### 1.1 System Identity
- **System name:** {project_name}
- **Project path:** {project_path}
- **Documentation date:** {now}
- **Classification:** {highest.upper().replace('_', '-')}

### 1.2 AI Components Detected

| File | Risk Tier | Indicators | Applicable Articles |
|------|-----------|------------|---------------------|
"""

    for c in findings["classifications"]:
        articles = ", ".join(c["articles"]) if c["articles"] else "N/A"
        indicators = ", ".join(c["indicators"]) if c["indicators"] else "N/A"
        doc += f"| {c['file']} | {c['tier'].upper().replace('_', '-')} | {indicators} | {articles} |\n"

    if not findings["classifications"]:
        doc += "| _No AI components detected_ | — | — | — |\n"

    if findings["model_files"]:
        doc += "\n### 1.3 Model Files\n\n"
        for mf in findings["model_files"]:
            doc += f"- `{mf}`\n"

    # Auto-populate sections 2-4 from code analysis
    analysis = analyse_project_code(project_path)
    ast_data = ast_analyse_project(project_path)

    # Extract dependency versions
    ai_deps = extract_ai_dependencies(project_path)

    # Track completion per section for --completion flag
    completion = {}

    doc += "\n---\n\n## 2. Detailed Description of Elements and Development Process\n\n"

    # 2.1 Development Methods — auto-populated from AST + dependency versions
    doc += "### 2.1 Development Methods\n\n"
    section_auto = False
    if ai_deps or ast_data["ai_imports"]:
        doc += "**[AUTO-DETECTED]**\n\n"
        section_auto = True

        # Dependency table with versions
        if ai_deps:
            doc += "**AI dependencies (from project manifest):**\n\n"
            doc += "| Library | Version | Source |\n"
            doc += "|---------|---------|--------|\n"
            for dep in ai_deps:
                ver = dep["version"] or "_unpinned_"
                doc += f"| {dep['name']} | {ver} | {dep['source_file']} |\n"
            doc += "\n"
        elif ast_data["ai_imports"]:
            doc += "**AI frameworks/libraries (from imports):**\n"
            for imp in ast_data["ai_imports"]:
                doc += f"- `{imp}`\n"
            doc += "\n"

        # Function table with signatures, docstrings, line numbers
        if ast_data["ai_functions"]:
            doc += "**Functions detected:**\n\n"
            doc += "| Function | File | Signature | Docstring |\n"
            doc += "|----------|------|-----------|-----------|\n"
            for fn in ast_data["ai_functions"][:20]:
                args = ", ".join(fn["args"]) if fn["args"] else ""
                sig = f"({args})"
                ret = fn.get("return_type")
                if ret:
                    sig += f" -> {ret}"
                docstr = fn.get("docstring") or "_None_"
                # Truncate long values for table readability
                if len(docstr) > 60:
                    docstr = docstr[:57] + "..."
                if len(sig) > 50:
                    sig = sig[:47] + "..."
                line = fn.get("line", "?")
                doc += f"| {fn['name']} | {fn['file']}:{line} | `{sig}` | {docstr} |\n"
            if len(ast_data["ai_functions"]) > 20:
                doc += f"\n_...and {len(ast_data['ai_functions']) - 20} more functions_\n"
            doc += "\n"

    doc += "**[COMPLETE THESE]**\n\n"
    doc += "Model selection rationale:\n"
    doc += "> We selected __________ because __________.\n"
    doc += "> Alternatives considered: __________.\n\n"
    doc += "Training methodology:\n"
    doc += "> Trained on __________ using __________.\n"
    doc += "> Split: __% train / __% val / __% test.\n\n"
    completion["2.1"] = "partial" if section_auto else "empty"

    # 2.2 Data Requirements — auto-detected + guided template
    doc += "### 2.2 Data Requirements\n\n"
    if analysis["data_sources"]:
        doc += "**[AUTO-DETECTED]** Data sources found:\n\n"
        for ds in analysis["data_sources"]:
            doc += f"- {ds}\n"
        doc += "\n"
        completion["2.2"] = "partial"
    else:
        completion["2.2"] = "empty"
    doc += "**[COMPLETE THESE]** (Article 10 — Data Governance)\n\n"
    doc += "Training data:\n"
    doc += "> Dataset: __________ | Size: __________ records\n"
    doc += "> Collection method: __________\n"
    doc += "> Time period: __________ to __________\n\n"
    doc += "Bias examination:\n"
    doc += "> Protected attributes checked: __________\n"
    doc += "> Bias mitigation applied: __________ (e.g., resampling, reweighting, none)\n"
    doc += "> Known data gaps: __________\n\n"

    # 2.3 Model Architecture — auto-detected + guided template
    doc += "### 2.3 Model Architecture\n\n"
    if analysis["architectures"]:
        doc += "**[AUTO-DETECTED]** Frameworks/architectures:\n\n"
        for arch in analysis["architectures"]:
            doc += f"- {arch}\n"
        doc += "\n"
        completion["2.3"] = "partial"
    else:
        completion["2.3"] = "empty"
    doc += "**[COMPLETE THESE]**\n\n"
    doc += "Architecture:\n"
    doc += "> Model type: __________ (e.g., transformer, gradient boosting, logistic regression)\n"
    doc += "> Parameters: __________ | Input format: __________ | Output format: __________\n\n"
    doc += "Training:\n"
    doc += "> Hardware: __________ | Duration: __________ | Final loss: __________\n"
    doc += "> Hyperparameters: __________\n\n"

    doc += "---\n\n## 3. Monitoring, Functioning, and Control\n\n"

    # 3.1 Performance Metrics — guided template
    doc += "### 3.1 Performance Metrics\n\n"
    doc += "**[COMPLETE THESE]** (Article 13 — Transparency)\n\n"
    doc += "| Metric | Value | Dataset | Date Measured |\n"
    doc += "|--------|-------|---------|---------------|\n"
    doc += "| Accuracy | __________ | __________ | __________ |\n"
    doc += "| Precision | __________ | __________ | __________ |\n"
    doc += "| Recall | __________ | __________ | __________ |\n"
    doc += "| F1 Score | __________ | __________ | __________ |\n"
    doc += "| False positive rate | __________ | __________ | __________ |\n\n"
    doc += "> Acceptable performance thresholds: __________\n"
    doc += "> Performance degrades when: __________\n\n"
    completion["3.1"] = "empty"

    # 3.2 Known Limitations — guided template
    doc += "### 3.2 Known Limitations\n\n"
    doc += "**[COMPLETE THESE]** (Article 13 — Transparency)\n\n"
    doc += "| Limitation | Impact | Mitigation |\n"
    doc += "|-----------|--------|------------|\n"
    doc += "| __________ | __________ | __________ |\n"
    doc += "| __________ | __________ | __________ |\n\n"
    doc += "> Foreseeable misuse scenarios: __________\n"
    doc += "> Populations the system should NOT be used for: __________\n\n"
    completion["3.2"] = "empty"

    # 3.3 Human Oversight — AST-derived score + evidence (Article 14)
    doc += "### 3.3 Human Oversight\n\n"
    has_ai_ops = ast_data["total_logged"] + ast_data["total_unlogged"] > 0
    if has_ai_ops or ast_data["oversight_evidence"] or ast_data["automated_decisions"]:
        doc += "**[AUTO-DETECTED]** AST analysis found the following oversight indicators:\n\n"
        doc += f"**Oversight score:** {ast_data['oversight_score']}/100\n\n"
        if ast_data["oversight_evidence"]:
            doc += "**Oversight mechanisms detected:**\n"
            for ev in ast_data["oversight_evidence"][:10]:
                doc += f"- {ev['detail']} (line {ev['line']}) — `{ev['file']}`\n"
            doc += "\n"
        if ast_data["automated_decisions"]:
            doc += f"**Automated decision paths (no human review gate detected):** {len(ast_data['automated_decisions'])}\n"
            for ad in ast_data["automated_decisions"][:5]:
                doc += f"- `{ad['source']}` (line {ad['source_line']}) → automated at line {ad['decision_line']} — `{ad['file']}`\n"
            doc += "\n"
        elif not ast_data["oversight_evidence"]:
            doc += "_No human review gates detected in AI operation paths._\n\n"
        doc += "_Verify these mechanisms meet Article 14 requirements (human oversight, override capability)._\n\n"
        completion["3.3"] = "partial"
    elif analysis["oversight"]:
        doc += "**[AUTO-DETECTED]** Oversight patterns found:\n\n"
        for o in analysis["oversight"]:
            doc += f"- {o}\n"
        doc += "\n_Verify these mechanisms meet Article 14 requirements._\n\n"
        completion["3.3"] = "partial"
    else:
        doc += "_No human oversight patterns detected._ Review Article 14 requirements.\n\n"
        completion["3.3"] = "empty"

    # 3.4 Logging — AST-derived score + per-operation coverage table (Article 12)
    doc += "### 3.4 Logging Infrastructure\n\n"
    total_ops = ast_data["total_logged"] + ast_data["total_unlogged"]
    if total_ops > 0:
        pct = int(ast_data["total_logged"] / total_ops * 100) if total_ops > 0 else 0
        doc += f"**Coverage:** {ast_data['total_logged']}/{total_ops} AI operations ({pct}%)\n\n"

        # Per-operation coverage table from AI functions
        if ast_data["ai_functions"]:
            doc += "| Operation | Location | Status | What to log |\n"
            doc += "|-----------|----------|--------|-------------|\n"
            for fn in ast_data["ai_functions"][:15]:
                line = fn.get("line", "?")
                # Heuristic: if the function has logging nearby, mark as covered
                # (simplified — actual detection is in ast_analysis)
                status = "check" # can't determine per-function from aggregate data
                what_to_log = "input_hash, timestamp, model_version, output_summary"
                doc += f"| {fn['name']} | {fn['file']}:{line} | {status} | {what_to_log} |\n"
            doc += "\n"

        if ast_data["total_unlogged"] > 0:
            doc += (
                f"**To comply with Article 12:**\n"
                f"Add logging that captures input hashes (not raw data), timestamps,\n"
                f"model versions, and output summaries for each AI operation.\n\n"
            )
        else:
            doc += "_All detected AI operations have logging coverage._\n\n"
        completion["3.4"] = "partial" if ast_data["total_unlogged"] > 0 else "auto"
    elif analysis["logging"]:
        doc += "**[AUTO-DETECTED]** Logging mechanisms found:\n\n"
        for lg in analysis["logging"]:
            doc += f"- {lg}\n"
        doc += "\n_Verify logging meets Article 12 record-keeping requirements._\n\n"
        completion["3.4"] = "partial"
    else:
        doc += "_No logging infrastructure detected._ Article 12 requires automatic recording of events.\n\n"
        completion["3.4"] = "empty"

    # 3.5 Data Flow — AST-derived AI operation flow tracing
    doc += "### 3.5 AI Data Flow\n\n"
    if ast_data["data_flows"]:
        doc += "**[AUTO-DETECTED]** AST analysis traced the following AI operation data flows:\n\n"
        for flow in ast_data["data_flows"][:15]:  # cap to avoid walls of text
            dests = flow.get("destinations", [])
            dest_strs = []
            for d in dests:
                dest_strs.append(f"{d['type']} (line {d['line']})")
            dest_summary = ", ".join(dest_strs) if dest_strs else "no traced destinations"
            doc += f"- AI operation at line {flow['source_line']} flows to: {dest_summary} — `{flow['file']}`\n"
        if len(ast_data["data_flows"]) > 15:
            doc += f"- _...and {len(ast_data['data_flows']) - 15} more_\n"
        doc += "\n_Review data flow paths to ensure AI outputs pass through appropriate oversight and logging._\n\n"
        completion["3.5"] = "auto"
    else:
        doc += "_No AI data flows detected._ If the system produces AI-generated outputs, document how they flow through the application.\n\n"
        completion["3.5"] = "empty"

    # 4. Risk Register — auto-populated from security findings
    doc += "---\n\n## 4. Risk Management System (Article 9)\n\n"
    security_findings = []
    for c in findings["classifications"]:
        filepath = Path(project_path) / c["file"]
        if filepath.exists():
            try:
                text = filepath.read_text(encoding="utf-8", errors="ignore")
                sf = check_ai_security(text)
                for f in sf:
                    f["file"] = c["file"]
                security_findings.extend(sf)
            except OSError:
                pass

    completion["1"] = "auto"  # Section 1 is always auto-populated from scan
    if security_findings or findings["classifications"]:
        doc += "### Risk Register\n\n"
        doc += "**[AUTO-DETECTED]**\n\n"
        doc += "| Risk ID | File | Description | OWASP Mapping | Severity | Mitigation |\n"
        doc += "|---------|------|-------------|---------------|----------|------------|\n"
        rid = 1
        for c in findings["classifications"]:
            tier = c["tier"].upper().replace("_", "-")
            doc += f"| R{rid:03d} | {c['file']} | {c['description']} ({tier}) | — | {tier} | _[TO BE COMPLETED]_ |\n"
            rid += 1
        for sf in security_findings:
            doc += f"| R{rid:03d} | {sf['file']} | {sf['description']} | {sf['owasp']} | {sf['severity'].upper()} | {sf['remediation'][:60]} |\n"
            rid += 1
        doc += "\n"
        completion["4"] = "partial"
    else:
        doc += "_[TO BE COMPLETED BY DEVELOPMENT TEAM]_\n\n"
        completion["4"] = "empty"

    doc += "---\n\n## 5. Compliance Requirements\n\n"


    if highest in ("high_risk", "prohibited"):
        doc += """The following EU AI Act articles apply to this system:

| Article | Requirement | Status |
|---------|-------------|--------|
| Article 9 | Risk management system | [ ] Not started |
| Article 10 | Data governance | [ ] Not started |
| Article 11 | Technical documentation | [ ] In progress (this document) |
| Article 12 | Record-keeping | [ ] Not started |
| Article 13 | Transparency | [ ] Not started |
| Article 14 | Human oversight | [ ] Not started |
| Article 15 | Accuracy, robustness, cybersecurity | [ ] Not started |

**Compliance deadline:** 2 August 2026
"""
    elif highest == "limited_risk":
        doc += """**Article 50 (Transparency) applies.**

| Requirement | Status |
|-------------|--------|
| Users informed of AI interaction | [ ] Not started |
| AI-generated content labelled | [ ] Not started |
"""
    else:
        doc += "No specific EU AI Act compliance requirements identified for this risk tier.\n"

    doc += f"""
---

## 6. Audit Trail Reference

Regula audit events for this system are stored in `~/.regula/audit/`.
Verify chain integrity: `python3 scripts/log_event.py verify`

---

## 7. EU Declaration of Conformity
_[TO BE COMPLETED BEFORE MARKET PLACEMENT]_

---

_Generated by Regula v{VERSION} — AI Governance Risk Indication_
_Template based on EU AI Act (Regulation 2024/1689) Annex IV_
_Generated on {now}_
"""

    # Store completion data on the doc string for retrieval
    doc = doc.rstrip()
    doc += "\n"

    # Attach completion metadata (retrievable by generate_completion_report)
    _last_completion.clear()
    _last_completion.update(completion)

    return doc


# Module-level completion cache for --completion flag
_last_completion: dict = {}


def generate_completion_report(project_name: str) -> str:
    """Generate a completion percentage report for the last Annex IV generation.

    Must be called after generate_annex_iv().
    """
    completion = _last_completion
    if not completion:
        return "No completion data available. Run `regula docs` first."

    section_names = {
        "1": "General Description",
        "2.1": "Development Methods",
        "2.2": "Data Requirements",
        "2.3": "Model Architecture",
        "3.1": "Performance Metrics",
        "3.2": "Known Limitations",
        "3.3": "Human Oversight",
        "3.4": "Logging Infrastructure",
        "3.5": "AI Data Flow",
        "4": "Risk Management",
    }

    status_labels = {
        "auto": "Auto-populated",
        "partial": "Partial (needs human input)",
        "empty": "Empty (needs human input)",
    }

    lines = [f"Annex IV Completion Report — {project_name}\n"]
    lines.append(f"{'Section':<30} {'Status':<35}")
    lines.append(f"{'-'*30} {'-'*35}")

    auto_count = 0
    partial_count = 0
    empty_count = 0
    total = 0

    for key in sorted(section_names.keys()):
        name = section_names[key]
        status = completion.get(key, "empty")
        label = status_labels.get(status, status)
        lines.append(f"  {key:<6} {name:<22} {label}")
        total += 1
        if status == "auto":
            auto_count += 1
        elif status == "partial":
            partial_count += 1
        else:
            empty_count += 1

    pct_auto = int(auto_count / total * 100) if total else 0
    pct_partial = int(partial_count / total * 100) if total else 0
    pct_empty = int(empty_count / total * 100) if total else 0

    lines.append("")
    lines.append(f"  Auto-populated:  {auto_count}/{total} ({pct_auto}%)")
    lines.append(f"  Partial:         {partial_count}/{total} ({pct_partial}%)")
    lines.append(f"  Needs input:     {empty_count}/{total} ({pct_empty}%)")
    lines.append("")

    return "\n".join(lines)


def generate_qms_scaffold(findings: dict, project_name: str, project_path: str) -> str:
    """Generate a Quality Management System scaffold per Article 17.

    Article 17 requires providers of high-risk AI systems to put in place a
    quality management system. This scaffold covers the required elements.
    """
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    highest = findings["highest_risk"]
    if isinstance(highest, RiskTier):
        highest = highest.value

    doc = f"""# Quality Management System Scaffold — Article 17

> **IMPORTANT:** This is an auto-generated scaffold. All sections require
> human completion and review by qualified personnel. A QMS cannot be
> auto-generated — this provides the structure, not the substance.

## AI System: {project_name}

**Generated by:** Regula v{VERSION}
**Date:** {now}

---

## 0. Governance and Accountability

{_governance_section()}
**Accountability structure:**

| Role | Responsibility | Person |
|------|---------------|--------|
| AI Officer | Overall AI governance accountability | _[TO BE COMPLETED]_ |
| DPO | Data protection oversight | _[TO BE COMPLETED]_ |
| Technical Lead | System design and implementation | _[TO BE COMPLETED]_ |
| Risk Owner | Risk assessment and monitoring | _[TO BE COMPLETED]_ |

---

## 1. Strategy and Compliance Objectives (Art. 17(1)(a))

_[TO BE COMPLETED]_

- Regulatory framework: EU AI Act (Regulation 2024/1689)
- Risk classification: {highest.upper().replace('_', '-')}
- Compliance target date: _[TO BE COMPLETED]_

---

## 2. Techniques, Procedures, and Actions for Design and Development (Art. 17(1)(b))

_[TO BE COMPLETED]_

### 2.1 Development Lifecycle
- [ ] Requirements specification
- [ ] Design documentation
- [ ] Implementation standards
- [ ] Code review procedures
- [ ] Testing methodology

### 2.2 Data Management (Article 10)
- [ ] Training data documentation
- [ ] Data quality assessment
- [ ] Bias detection procedures
- [ ] Data governance framework

---

## 3. Techniques, Procedures, and Actions for Testing and Validation (Art. 17(1)(c))

_[TO BE COMPLETED]_

- [ ] Performance testing criteria
- [ ] Bias and fairness testing
- [ ] Robustness testing
- [ ] Security testing
- [ ] Validation against intended purpose

---

## 4. Technical Specifications and Standards (Art. 17(1)(d))

_[TO BE COMPLETED]_

| Standard | Status | Notes |
|----------|--------|-------|
| ISO 42001 (AI Management System) | [ ] Not started | |
| prEN 18286 (QMS for AI) | [ ] Awaiting publication | Public enquiry closes Oct 2026 |
| ISO 23894 (AI Risk Management) | [ ] Not started | |

---

## 5. Systems and Procedures for Data Management (Art. 17(1)(e))

_[TO BE COMPLETED]_

- [ ] Data inventory
- [ ] Data lineage tracking
- [ ] Data quality metrics
- [ ] Data retention policy

---

## 6. Risk Management System (Art. 17(1)(f), Art. 9)

_[TO BE COMPLETED]_

### 6.1 Known Risks

| Risk | Likelihood | Impact | Mitigation | Owner |
|------|-----------|--------|------------|-------|
| _[TO BE COMPLETED]_ | | | | |

### 6.2 Risk Monitoring
- [ ] Monitoring frequency defined
- [ ] Risk escalation procedures
- [ ] Incident response plan

---

## 7. Post-Market Monitoring (Art. 17(1)(g), Art. 72)

_[TO BE COMPLETED]_

- [ ] Monitoring plan documented
- [ ] Feedback collection mechanism
- [ ] Performance degradation detection
- [ ] Incident reporting procedures

---

## 8. Record-Keeping (Art. 17(1)(h), Art. 12)

- Regula audit trail: `~/.regula/audit/`
- Chain integrity verification: `regula audit verify`
- [ ] Additional logging requirements identified
- [ ] Log retention policy: _[TO BE COMPLETED]_ years

---

## 9. Corrective Actions (Art. 17(1)(i))

_[TO BE COMPLETED]_

- [ ] Non-conformity identification process
- [ ] Root cause analysis procedures
- [ ] Corrective action implementation
- [ ] Effectiveness verification

---

## 10. Communication with Authorities (Art. 17(1)(j))

_[TO BE COMPLETED]_

- National competent authority: _[TO BE COMPLETED]_
- Notification procedures: _[TO BE COMPLETED]_
- Serious incident reporting: _[TO BE COMPLETED]_

---

## 11. Human Oversight (Art. 14)

_[TO BE COMPLETED]_

- [ ] Human oversight mechanism defined
- [ ] Override capability documented
- [ ] Operator training programme
- [ ] Decision escalation criteria

---

## 12. Transparency (Art. 13)

_[TO BE COMPLETED]_

- [ ] Instructions for use documented
- [ ] Capabilities and limitations described
- [ ] Performance characteristics disclosed
- [ ] Intended purpose clearly defined

---

## Review Schedule

| Review | Frequency | Next Due | Responsible |
|--------|-----------|----------|-------------|
| Full QMS review | Annual | _[TO BE COMPLETED]_ | AI Officer |
| Risk assessment | Quarterly | _[TO BE COMPLETED]_ | Risk Owner |
| Audit trail verification | Monthly | _[TO BE COMPLETED]_ | Technical Lead |
| Incident review | Per incident | — | AI Officer |

---

_Generated by Regula v{VERSION} — AI Governance Risk Indication_
_Template based on EU AI Act (Regulation 2024/1689) Article 17_
_Generated on {now}_
"""

    return doc


def generate_model_card(findings: dict, project_name: str, project_path: str) -> str:
    """Generate a HuggingFace-compatible model card.

    See https://huggingface.co/docs/hub/model-cards for format.
    """
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    highest = findings["highest_risk"]
    if isinstance(highest, RiskTier):
        highest = highest.value

    analysis = analyse_project_code(project_path)

    doc = f"""---
license: _[TO BE COMPLETED]_
tags:
  - regula-scanned
  - eu-ai-act
---

# Model Card: {project_name}

> _[AUTO-DETECTED — VERIFY]_ This model card was auto-generated by Regula v{VERSION}.
> All sections require human review before publication.

## Model Details

### Model Description

- **Developed by:** _[TO BE COMPLETED]_
- **Model type:** {', '.join(analysis['architectures']) if analysis['architectures'] else '_[TO BE COMPLETED]_'}
- **Language(s):** _[TO BE COMPLETED]_
- **License:** _[TO BE COMPLETED]_
- **EU AI Act Risk Classification:** {highest.upper().replace('_', '-')}

### Model Sources

- **Repository:** {project_path}
- **Documentation:** _[TO BE COMPLETED]_

## Uses

### Direct Use
_[TO BE COMPLETED]_

### Out-of-Scope Use
_[TO BE COMPLETED]_

## Training Details

### Training Data
"""
    if analysis["data_sources"]:
        doc += "_[AUTO-DETECTED — VERIFY]_ Detected data sources:\n\n"
        for ds in analysis["data_sources"]:
            doc += f"- {ds}\n"
    else:
        doc += "_[TO BE COMPLETED]_\n"

    doc += """
### Training Procedure
_[TO BE COMPLETED]_

## Evaluation

### Metrics
_[TO BE COMPLETED]_

### Results
_[TO BE COMPLETED]_

## Environmental Impact
_[TO BE COMPLETED]_

## Technical Specifications
_[TO BE COMPLETED]_

## EU AI Act Compliance

"""
    if highest in ("high_risk", "prohibited"):
        doc += f"**Risk tier:** {highest.upper().replace('_', '-')}\n\n"
        doc += "Articles 9-15 apply. See Annex IV documentation for full compliance status.\n\n"
        if analysis["oversight"]:
            doc += "**Human oversight mechanisms detected:**\n\n"
            for o in analysis["oversight"]:
                doc += f"- _[AUTO-DETECTED — VERIFY]_ {o}\n"
        else:
            doc += "**No human oversight mechanisms detected.** Article 14 compliance required.\n"
    elif highest == "limited_risk":
        doc += "**Risk tier:** LIMITED-RISK\n\nArticle 50 transparency requirements apply.\n"
    else:
        doc += "**Risk tier:** MINIMAL-RISK\n\nNo specific EU AI Act requirements.\n"

    doc += f"""
---

_Generated by Regula v{VERSION} on {now}_
"""
    return doc


def main():
    parser = argparse.ArgumentParser(description="Generate Annex IV technical documentation and QMS scaffolds")
    parser.add_argument("--project", "-p", default=".", help="Project directory to scan")
    parser.add_argument("--output", "-o", default="docs", help="Output directory")
    parser.add_argument("--name", "-n", help="Project name (defaults to directory name)")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    parser.add_argument("--qms", action="store_true", help="Also generate QMS scaffold (Article 17)")
    parser.add_argument("--all", action="store_true", help="Generate all documentation types")
    args = parser.parse_args()

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

    if args.format == "json":
        output_file = output_dir / f"{project_name}_annex_iv.json"
        json_findings = dict(findings)
        json_findings["highest_risk"] = highest
        output_file.write_text(json.dumps(json_findings, indent=2, default=str), encoding="utf-8")
        print(f"Documentation written to {output_file}")
    else:
        # Annex IV
        output_file = output_dir / f"{project_name}_annex_iv.md"
        doc = generate_annex_iv(findings, project_name, project_path)
        output_file.write_text(doc, encoding="utf-8")
        print(f"Annex IV documentation written to {output_file}")

        # QMS scaffold
        if args.qms or getattr(args, "all", False):
            qms_file = output_dir / f"{project_name}_qms.md"
            qms_doc = generate_qms_scaffold(findings, project_name, project_path)
            qms_file.write_text(qms_doc, encoding="utf-8")
            print(f"QMS scaffold written to {qms_file}")

    try:
        log_event("documentation_generated", {
            "project": project_name, "highest_risk": highest,
            "ai_files": ai_count, "model_files": model_count,
            "types": ["annex_iv"] + (["qms"] if args.qms or getattr(args, "all", False) else []),
        })
    except (OSError,):
        pass


def generate_conformity_declaration(
    project_path: str,
    system_name: str = "",
    version: str = "1.0",
    provider_name: str = "",
    provider_address: str = "",
    annex_iii_provision: str = "",
) -> str:
    """Generate an EU Declaration of Conformity scaffold per Annex XIII.

    Returns a markdown string. All [TO BE COMPLETED] sections require
    human review and signature before use.

    Annex XIII requires:
    (a) Provider name and address
    (b) AI system name, version, and description
    (c) Applicable Annex III provision
    (d) Declaration statement
    (e) Reference to technical documentation
    (f) Conformity assessment procedure
    (g) Standards applied
    (h) Notified body (if applicable)
    (i) Place, date, signature
    """
    scan = scan_project(project_path)
    risk = scan.get("highest_risk", RiskTier.NOT_AI)
    risk_str = risk.value if isinstance(risk, RiskTier) else str(risk)

    contacts = get_governance_contacts()
    ai_officer = contacts.get("ai_officer", {})

    prov = provider_name or contacts.get("provider_name", "_[TO BE COMPLETED \u2014 Company legal name]_")
    prov_addr = provider_address or contacts.get("provider_address", "_[TO BE COMPLETED \u2014 Registered address]_")
    sys_name = system_name or Path(project_path).name
    annex_iii = annex_iii_provision or "_[TO BE COMPLETED \u2014 Specify which Annex III provision applies, e.g. Annex III(1)(a): biometric identification]_"
    officer_name = ai_officer.get("name", "_[TO BE COMPLETED]_")
    officer_role = ai_officer.get("role", "_[TO BE COMPLETED]_")

    today = datetime.now(timezone.utc).strftime("%d %B %Y")

    return f"""# EU Declaration of Conformity

> **AUTO-GENERATED SCAFFOLD \u2014 Requires legal review and authorised signature before use.**
> This is NOT a legally valid Declaration of Conformity until completed and signed.
> Reference: EU AI Act Article 47 and Annex XIII.

---

## Declaration

We, the undersigned,

**Provider:** {prov}
**Address:** {prov_addr}

hereby declare that the following AI system:

**AI system name:** {sys_name}
**Version:** {version}
**Risk classification (auto-detected):** {risk_str.upper()} \u2014 _[VERIFY against intended purpose and deployment context]_

is in conformity with Regulation (EU) 2024/1689 of the European Parliament and of the Council on Artificial Intelligence (the EU AI Act).

---

## (a) Provider Details

| Field | Value |
|-------|-------|
| Legal name | {prov} |
| Registered address | {prov_addr} |
| Contact for this declaration | {officer_name}, {officer_role} |

---

## (b) AI System Description

| Field | Value |
|-------|-------|
| System name | {sys_name} |
| Version/release | {version} |
| Intended purpose | _[TO BE COMPLETED \u2014 Describe the specific intended purpose per Article 9(2)(a)]_ |
| Deployment context | _[TO BE COMPLETED \u2014 EU member states where system is placed on market/put into service]_ |

---

## (c) Applicable Annex III Provision

This AI system falls under:

{annex_iii}

---

## (d) Declaration Statement

The AI system identified above, in the version described in this declaration, is in conformity with the following requirements of Regulation (EU) 2024/1689:

- Article 9: Risk management system
- Article 10: Data and data governance
- Article 11: Technical documentation (Annex IV)
- Article 12: Record keeping
- Article 13: Transparency and provision of information to deployers
- Article 14: Human oversight
- Article 15: Accuracy, robustness and cybersecurity

---

## (e) Technical Documentation Reference

Technical documentation maintained per Article 11 and Annex IV is available at:

_[TO BE COMPLETED \u2014 Internal document reference or location]_

Annex IV scaffold generated by Regula is available in the project repository.

---

## (f) Conformity Assessment Procedure

The following conformity assessment procedure was applied (per Article 43):

- [ ] Internal control (Annex VI) \u2014 applicable to most high-risk systems
- [ ] Third-party assessment by notified body (Annex VII) \u2014 required for certain biometric systems

_[TO BE COMPLETED \u2014 Select the applicable procedure]_

---

## (g) Harmonised Standards and Common Specifications Applied

| Standard | Scope | Applied |
|----------|-------|---------|
| ISO/IEC 42001:2023 | AI management systems | _[YES/NO/PARTIAL]_ |
| ISO/IEC 23894:2023 | AI risk management | _[YES/NO/PARTIAL]_ |
| ISO/IEC TR 24368 | AI ethical concerns | _[YES/NO/PARTIAL]_ |
| CEN/CENELEC (pending) | EU AI Act harmonised standards | _[Targeting end of 2026]_ |

_Note: EU AI Act harmonised standards were not finalised as of the date of this scaffold (targeting end of 2026)._

---

## (h) Notified Body

_[TO BE COMPLETED \u2014 If a notified body was involved in the conformity assessment, provide its name, identification number, and a description of the intervention. Otherwise state: "Not applicable \u2014 internal control procedure under Annex VI was applied."]_

---

## (i) Signature

| | |
|---|---|
| Place | _[TO BE COMPLETED]_ |
| Date | {today} |
| Name | {officer_name} |
| Function | {officer_role} |
| Signature | _[SIGNATURE REQUIRED]_ |

---

_This declaration was scaffolded by Regula v{VERSION} on {today}. It must be reviewed by a qualified legal professional before use as a compliance document._
"""


if __name__ == "__main__":
    main()
