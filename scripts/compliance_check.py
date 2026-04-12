#!/usr/bin/env python3
# regula-ignore
"""
Regula EU AI Act Compliance Gap Assessment

Scans a project for evidence of compliance infrastructure required by
Articles 9-15 of the EU AI Act. Returns a structured gap assessment
showing what exists, what is missing, and an overall compliance score.

This module uses file scanning (glob/grep patterns) and optionally
integrates with the AST analysis module for deeper Python file inspection.

No external dependencies — stdlib only.
"""

import argparse
import fnmatch
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Optional imports from sibling modules (graceful fallback)
# ---------------------------------------------------------------------------

_scripts_dir = str(Path(__file__).parent)
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)
from degradation import check_optional

_ast_analysis_available = check_optional("ast_analysis", "AST logging/oversight detection", "included with regula")
if _ast_analysis_available:
    from ast_analysis import detect_logging_practices, detect_human_oversight

try:
    from ast_engine import analyse_file as _ast_engine_analyse
    _HAS_AST_ENGINE = True
except ImportError:
    _HAS_AST_ENGINE = False

_classify_available = check_optional("classify_risk", "risk classification", "included with regula")
if _classify_available:
    from classify_risk import classify, RiskTier

_report_available = check_optional("report", "file scanning", "included with regula")
if _report_available:
    from report import SKIP_DIRS, CODE_EXTENSIONS
else:
    from constants import CODE_EXTENSIONS, SKIP_DIRS

_dep_scan_available = check_optional("dependency_scan", "dependency scanning", "included with regula")
if _dep_scan_available:
    from dependency_scan import scan_dependencies as _scan_dependencies


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DOC_EXTENSIONS = {".md", ".txt", ".rst", ".yaml", ".yml", ".json", ".toml"}
ALL_SCANNABLE = CODE_EXTENSIONS | DOC_EXTENSIONS
ARTICLE_NUMBERS = ["9", "10", "11", "12", "13", "14", "15"]

ARTICLE_TITLES = {
    "9": "Risk Management",
    "10": "Data Governance",
    "11": "Technical Documentation",
    "12": "Record-Keeping",
    "13": "Transparency",
    "14": "Human Oversight",
    "15": "Accuracy, Robustness, Cybersecurity",
}


# ---------------------------------------------------------------------------
# File discovery helpers
# ---------------------------------------------------------------------------

def _walk_project(project_path: str):
    """Yield (relative_path, absolute_path) for all scannable files."""
    project = Path(project_path).resolve()
    for root, dirs, files in os.walk(project):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for filename in files:
            filepath = Path(root) / filename
            if filepath.suffix.lower() in ALL_SCANNABLE:
                try:
                    rel = str(filepath.relative_to(project))
                except ValueError:
                    rel = str(filepath)
                yield rel, str(filepath)


def _read_file(filepath: str) -> Optional[str]:
    """Read file content, returning None on failure."""
    try:
        return Path(filepath).read_text(encoding="utf-8", errors="ignore")
    except (PermissionError, OSError):
        return None


def _file_matches_glob(rel_path: str, patterns: list) -> bool:
    """Check if a relative path matches any of the given glob patterns."""
    basename = os.path.basename(rel_path).lower()
    rel_lower = rel_path.lower()
    for pattern in patterns:
        if fnmatch.fnmatch(basename, pattern.lower()):
            return True
        if fnmatch.fnmatch(rel_lower, pattern.lower()):
            return True
    return False


def _search_content(content: str, patterns: list) -> list:
    """Search content for regex patterns. Return list of matched pattern strings."""
    content_lower = content.lower()
    matched = []
    for pattern in patterns:
        if re.search(pattern, content_lower):
            matched.append(pattern)
    return matched


def _is_in_directory(rel_path: str, dir_names: list) -> bool:
    """Check if a file is inside any of the named directories."""
    parts = Path(rel_path).parts
    return any(d.lower() in [p.lower() for p in parts[:-1]] for d in dir_names)


def _determine_highest_risk(project_path: str) -> str:
    """Determine the highest risk tier found in the project."""
    if not _classify_available:
        return "unknown"

    highest = RiskTier.NOT_AI
    priority = {
        RiskTier.NOT_AI: 0,
        RiskTier.MINIMAL_RISK: 1,
        RiskTier.LIMITED_RISK: 2,
        RiskTier.HIGH_RISK: 3,
        RiskTier.PROHIBITED: 4,
    }

    project = Path(project_path).resolve()
    for root, dirs, files in os.walk(project):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for filename in files:
            filepath = Path(root) / filename
            if filepath.suffix.lower() not in CODE_EXTENSIONS:
                continue
            content = _read_file(str(filepath))
            if content is None:
                continue
            result = classify(content)
            if priority.get(result.tier, 0) > priority.get(highest, 0):
                highest = result.tier
                if highest == RiskTier.PROHIBITED:
                    return highest.value

    return highest.value


# ---------------------------------------------------------------------------
# Article-specific evidence checkers
#
# Each checker returns (score: int, evidence: list[str], gaps: list[str]).
# Scores are 0-100 following the rubric in the module docstring.
# ---------------------------------------------------------------------------

def _check_article_9(project_path: str, files_index: list) -> tuple:
    """Article 9 — Risk Management System."""
    evidence = []
    gaps = []
    score = 0

    risk_file_patterns = [
        "risk_assessment*", "risk_register*", "risk_management*",
        "risk_matrix*", "risk_analysis*",
    ]
    risk_content_patterns = [
        r"risk\s+assessment", r"risk\s+register", r"risk\s+mitigation",
        r"risk\s+treatment", r"risk\s+management\s+system",
        r"risk\s+matrix", r"residual\s+risk",
    ]
    ai_system_patterns = [
        r"ai\s+system", r"machine\s+learning", r"model\s+risk",
        r"algorithmic\s+risk", r"automated\s+decision",
    ]

    risk_files_found = []
    risk_content_found = []
    references_ai = False

    for rel_path, abs_path in files_index:
        in_compliance_dir = _is_in_directory(rel_path, ["docs", "compliance", "governance", "risk"])

        if _file_matches_glob(rel_path, risk_file_patterns):
            risk_files_found.append(rel_path)
            evidence.append(f"Risk management file: {rel_path}")

        if Path(rel_path).suffix.lower() in DOC_EXTENSIONS or in_compliance_dir:
            content = _read_file(abs_path)
            if content is None:
                continue
            matched = _search_content(content, risk_content_patterns)
            if matched:
                risk_content_found.append(rel_path)
                if rel_path not in [e.split(": ", 1)[-1] for e in evidence]:
                    evidence.append(f"Risk management content in: {rel_path}")

            ai_matched = _search_content(content, ai_system_patterns)
            if ai_matched and matched:
                references_ai = True

    # Scoring rubric for Article 9 — Risk Management System
    # Components: (1) risk files exist, (2) they reference the AI system, (3) structured mitigations.
    # 0 = no risk docs; 30 = generic risk docs not mentioning AI; 60 = risk docs reference
    # the AI system; 100 = structured register with mitigations (owners/deadlines/statuses).
    # Thresholds are heuristic, not empirically calibrated — chosen to penalise generic risk
    # docs that don't address AI-specific risks per Article 9(2).
    if not risk_files_found and not risk_content_found:
        score = 0
        gaps.append("No risk assessment documentation found")
        gaps.append("No risk register or risk management files detected")
    elif risk_files_found or risk_content_found:
        score = 30
        if not references_ai:
            gaps.append("Risk documentation does not reference the AI system specifically")
        else:
            score = 60
            # Check for structured mitigations
            has_mitigations = False
            for rel_path, abs_path in files_index:
                if rel_path in risk_files_found or rel_path in risk_content_found:
                    content = _read_file(abs_path)
                    if content and re.search(
                        r"(mitigation|treatment|control|countermeasure).*\n.*"
                        r"(status|owner|deadline|priority|accept|transfer|avoid|reduce)",
                        content.lower(),
                    ):
                        has_mitigations = True
                        break
            if has_mitigations:
                score = 100
                evidence.append("Structured risk register with mitigations detected")
            else:
                gaps.append("Risk documentation lacks structured mitigations (status, owners, deadlines)")

    return score, evidence, gaps


def _check_article_10(project_path: str, files_index: list) -> tuple:
    """Article 10 — Data Governance."""
    evidence = []
    gaps = []
    component_scores = {"data_docs": 0, "bias_checks": 0, "data_validation": 0}

    data_doc_patterns = [
        "data_dictionary*", "data_catalog*", "data_documentation*",
        "data_governance*", "data_lineage*", "dataset_card*",
        "datasheet*",
    ]
    data_content_patterns = [
        r"training\s+data", r"data\s+governance", r"data\s+quality",
        r"representative", r"data\s+lineage", r"data\s+dictionary",
        r"data\s+collection", r"annotation\s+guideline",
    ]
    bias_libraries = [
        r"fairlearn", r"aequitas", r"aif360", r"ai.fairness",
        r"bias.?detect", r"fairness.?metric", r"disparate.?impact",
        r"equalized.?odds",
    ]
    validation_libraries = [
        r"great_expectations", r"great\.expectations", r"pandera",
        r"pydantic", r"cerberus", r"marshmallow", r"jsonschema",
        r"voluptuous", r"data.?validation", r"schema.?valid",
    ]

    for rel_path, abs_path in files_index:
        if _file_matches_glob(rel_path, data_doc_patterns):
            evidence.append(f"Data documentation file: {rel_path}")
            component_scores["data_docs"] = 1

        content = _read_file(abs_path)
        if content is None:
            continue

        if Path(rel_path).suffix.lower() in DOC_EXTENSIONS:
            if _search_content(content, data_content_patterns):
                if component_scores["data_docs"] == 0:
                    evidence.append(f"Data governance content in: {rel_path}")
                    component_scores["data_docs"] = 1

        if Path(rel_path).suffix.lower() in CODE_EXTENSIONS | {".txt", ".toml", ".cfg"}:
            basename = os.path.basename(rel_path).lower()
            is_deps_file = basename in (
                "requirements.txt", "setup.py", "setup.cfg", "pyproject.toml",
                "package.json", "pipfile", "conda.yaml", "environment.yml",
            )

            bias_matched = _search_content(content, bias_libraries)
            if bias_matched:
                lib_name = bias_matched[0].replace(r"\.", ".").replace(r".?", " ")
                location = "dependencies" if is_deps_file else rel_path
                evidence.append(f"Bias checking library ({lib_name}) detected in {location}")
                component_scores["bias_checks"] = 1

            val_matched = _search_content(content, validation_libraries)
            if val_matched:
                lib_name = val_matched[0].replace(r"\.", ".").replace(r".?", " ")
                location = "dependencies" if is_deps_file else rel_path
                evidence.append(f"Data validation ({lib_name}) detected in {location}")
                component_scores["data_validation"] = 1

    if component_scores["data_docs"] == 0:
        gaps.append("No data documentation or data dictionary found")
    if component_scores["bias_checks"] == 0:
        gaps.append("No bias detection or fairness checking libraries found")
    if component_scores["data_validation"] == 0:
        gaps.append("No data validation framework detected")

    # Scoring: 3 components — data_docs, bias_checks, data_validation.
    # 0 = nothing; 30 = 1 component (minimal awareness); 65 = 2 (partial governance);
    # 100 = all 3 (docs + bias + validation). Heuristic, not empirically calibrated.
    total_components = sum(component_scores.values())
    score_map = {0: 0, 1: 30, 2: 65, 3: 100}
    score = score_map[total_components]

    return score, evidence, gaps


# ---------------------------------------------------------------------------
# Model card completeness validation
# ---------------------------------------------------------------------------

# Required sections for a complete model card (based on HuggingFace model card standard)
MODEL_CARD_REQUIRED_SECTIONS = {
    "intended_use": ["intended use", "intended purpose", "use case", "intended for"],
    "limitations": ["limitation", "known issue", "known limitation", "not suitable", "should not be used"],
    "training_data": ["training data", "dataset", "trained on", "fine-tuned on"],
    "performance": ["performance", "accuracy", "metric", "evaluation", "benchmark", "f1", "precision", "recall"],
    "ethical": ["ethical", "bias", "fairness", "responsible", "societal impact", "environmental"],
}


def validate_model_card(content: str) -> dict:
    """Validate a model card for completeness against EU AI Act requirements.

    Checks for presence of required sections matching Articles 11 and 13.
    Returns dict with:
        completeness_score: 0-100
        sections_found: list of section names found
        sections_missing: list of section names missing
    """
    content_lower = content.lower()
    found = []
    missing = []

    for section_name, keywords in MODEL_CARD_REQUIRED_SECTIONS.items():
        if any(kw in content_lower for kw in keywords):
            found.append(section_name)
        else:
            missing.append(section_name)

    total = len(MODEL_CARD_REQUIRED_SECTIONS)
    score = int((len(found) / total) * 100) if total > 0 else 0

    return {
        "completeness_score": score,
        "sections_found": found,
        "sections_missing": missing,
    }


def _check_article_11(project_path: str, files_index: list) -> tuple:
    """Article 11 — Technical Documentation."""
    evidence = []
    gaps = []
    component_scores = {"annex_iv": 0, "model_card": 0, "system_desc": 0, "regula_docs": 0}

    tech_doc_file_patterns = [
        "*annex_iv*", "*annex-iv*", "*technical_doc*", "*technical-doc*",
        "*model_card*", "*model-card*", "*system_description*",
        "*system-description*", "*architecture*",
    ]
    annex_iv_headings = [
        r"general\s+description", r"intended\s+purpose",
        r"interaction\s+with\s+hardware", r"design\s+specification",
        r"development\s+process", r"validation\s+and\s+testing",
        r"post.?market\s+monitoring", r"conformity\s+assessment",
    ]
    model_card_content = [
        r"model\s+architecture", r"training\s+procedure",
        r"evaluation\s+results", r"model\s+details",
        r"model\s+description", r"hyperparameter",
    ]
    regula_doc_patterns = [
        "regula-report*", ".regula/*", "regula_output*",
        "*compliance_report*", "*compliance-report*",
    ]

    for rel_path, abs_path in files_index:
        # Check for Regula-generated docs
        if _file_matches_glob(rel_path, regula_doc_patterns):
            evidence.append(f"Regula-generated documentation: {rel_path}")
            component_scores["regula_docs"] = 1

        if _file_matches_glob(rel_path, tech_doc_file_patterns):
            basename_lower = os.path.basename(rel_path).lower()
            if "annex" in basename_lower:
                evidence.append(f"Annex IV documentation: {rel_path}")
                component_scores["annex_iv"] = 1
            elif "model_card" in basename_lower or "model-card" in basename_lower:
                filepath = Path(abs_path)
                try:
                    card_content = filepath.read_text(encoding="utf-8", errors="ignore")
                    validation = validate_model_card(card_content)
                    if validation["completeness_score"] >= 60:
                        evidence.append(f"Model card {validation['completeness_score']}% complete: {', '.join(validation['sections_found'])}")
                    else:
                        evidence.append(f"Model card found but only {validation['completeness_score']}% complete")
                        for section in validation["sections_missing"]:
                            gaps.append(f"Model card missing: {section.replace('_', ' ')}")
                except (OSError, IOError):
                    evidence.append(f"Model card: {rel_path}")
                component_scores["model_card"] = 1
            else:
                evidence.append(f"Technical documentation: {rel_path}")
                component_scores["system_desc"] = 1

        content = _read_file(abs_path)
        if content is None:
            continue

        if Path(rel_path).suffix.lower() in DOC_EXTENSIONS:
            annex_matched = _search_content(content, annex_iv_headings)
            if len(annex_matched) >= 3:
                if component_scores["annex_iv"] == 0:
                    evidence.append(
                        f"Annex IV section headings ({len(annex_matched)} found) in: {rel_path}"
                    )
                    component_scores["annex_iv"] = 1

            model_matched = _search_content(content, model_card_content)
            if len(model_matched) >= 2:
                if component_scores["model_card"] == 0:
                    validation = validate_model_card(content)
                    if validation["completeness_score"] >= 60:
                        evidence.append(f"Model card {validation['completeness_score']}% complete: {', '.join(validation['sections_found'])}")
                    else:
                        evidence.append(f"Model description content in: {rel_path} (only {validation['completeness_score']}% complete)")
                        for section in validation["sections_missing"]:
                            gaps.append(f"Model card missing: {section.replace('_', ' ')}")
                    component_scores["model_card"] = 1

    if component_scores["annex_iv"] == 0:
        gaps.append("No Annex IV technical documentation found")
    if component_scores["model_card"] == 0:
        gaps.append("No model card or model description found")
    if component_scores["system_desc"] == 0 and component_scores["annex_iv"] == 0:
        gaps.append("No system architecture or design documentation found")

    # Scoring: 4 components — annex_iv, model_card, system_desc, regula_docs.
    # 0 = nothing; 25 = 1 (token effort); 55 = 2; 80 = 3 (near-complete); 100 = all 4.
    # More granular than other articles because Annex IV documentation has more distinct
    # deliverables. Heuristic, not empirically calibrated.
    total = sum(component_scores.values())
    score_map = {0: 0, 1: 25, 2: 55, 3: 80, 4: 100}
    score = score_map[total]

    return score, evidence, gaps


def _check_article_12(project_path: str, files_index: list) -> tuple:
    """Article 12 — Record-Keeping (Logging)."""
    evidence = []
    gaps = []
    component_scores = {"logging_present": 0, "ai_ops_logged": 0, "structured_logging": 0}

    logging_patterns = [
        r"import\s+logging", r"from\s+logging\s+import", r"getLogger",
        r"logger\s*=", r"logger\.", r"log_event", r"audit_log",
        r"audit_trail", r"winston", r"pino", r"bunyan",
    ]
    # NOTE: console.log/info/warn deliberately excluded — they are not
    # structured audit logging and should not give Article 12 credit.
    monitoring_patterns = [
        r"prometheus", r"datadog", r"sentry", r"new.?relic",
        r"grafana", r"elastic.?search", r"kibana", r"splunk",
        r"cloudwatch",
    ]
    ai_logging_patterns = [
        r"log.{0,30}(predict|inference|model|decision|score|output)",
        r"(predict|inference|model|decision).{0,30}log",
        r"audit.{0,20}(ai|model|predict|decision)",
        r"(ai|model|predict|decision).{0,20}audit",
        r"mlflow", r"wandb", r"weights.?and.?biases", r"neptune",
        r"experiment.?track", r"model.?registry",
    ]
    structured_logging_patterns = [
        r"structlog", r"json.?log", r"structured.?log",
        r"log.?format.*json", r"logging\.config",
        r"log_event\(", r"event_log",
    ]

    python_files = []

    for rel_path, abs_path in files_index:
        if Path(rel_path).suffix.lower() not in CODE_EXTENSIONS:
            continue

        if Path(rel_path).suffix.lower() == ".py":
            python_files.append((rel_path, abs_path))

        content = _read_file(abs_path)
        if content is None:
            continue

        if _search_content(content, logging_patterns):
            if component_scores["logging_present"] == 0:
                evidence.append(f"Logging detected in: {rel_path}")
                component_scores["logging_present"] = 1

        if _search_content(content, monitoring_patterns):
            evidence.append(f"Monitoring/observability library in: {rel_path}")
            component_scores["logging_present"] = 1

        ai_matched = _search_content(content, ai_logging_patterns)
        if ai_matched:
            evidence.append(f"AI operation logging in: {rel_path}")
            component_scores["ai_ops_logged"] = 1

        if _search_content(content, structured_logging_patterns):
            evidence.append(f"Structured logging in: {rel_path}")
            component_scores["structured_logging"] = 1

    # AST analysis for Python files (deeper inspection)
    if _ast_analysis_available and python_files:
        for rel_path, abs_path in python_files:
            content = _read_file(abs_path)
            if content is None:
                continue
            try:
                ast_result = detect_logging_practices(content)
                if ast_result and ast_result.get("has_logging"):
                    if component_scores["logging_present"] == 0:
                        evidence.append(f"AST: logging practices detected in: {rel_path}")
                        component_scores["logging_present"] = 1
                    if ast_result.get("ai_operations_logged"):
                        evidence.append(f"AST: AI operations logged in: {rel_path}")
                        component_scores["ai_ops_logged"] = 1
                    if ast_result.get("structured"):
                        evidence.append(f"AST: structured logging in: {rel_path}")
                        component_scores["structured_logging"] = 1
            except (SyntaxError, ValueError, TypeError) as e:
                print(f"regula: AST analysis failed for {rel_path}: {e}", file=sys.stderr)

    if component_scores["logging_present"] == 0:
        gaps.append("No logging framework detected in code files")
    if component_scores["ai_ops_logged"] == 0:
        gaps.append("No evidence of AI-specific operation logging (predictions, decisions, model outputs)")
    if component_scores["structured_logging"] == 0:
        gaps.append("No structured or auditable logging format detected")

    # Scoring: 3 components — logging_present, ai_ops_logged, structured_logging.
    # 0 = no logging; 30 = basic logging exists; 65 = AI ops or structured logging;
    # 100 = all 3 (structured audit trail of AI operations).
    # Same 0/30/65/100 curve as Articles 10 and 13. Heuristic, not empirically calibrated.
    total = sum(component_scores.values())
    score_map = {0: 0, 1: 30, 2: 65, 3: 100}
    score = score_map[total]

    return score, evidence, gaps


def _check_article_13(project_path: str, files_index: list) -> tuple:
    """Article 13 — Transparency."""
    evidence = []
    gaps = []
    component_scores = {"model_card": 0, "capabilities_docs": 0, "user_disclosure": 0}

    transparency_file_patterns = [
        "*model_card*", "*model-card*", "TRANSPARENCY*",
        "*capabilities*", "*limitations*", "*user_guide*",
        "*user-guide*",
    ]
    capability_content_patterns = [
        r"intended\s+purpose", r"capabilities", r"limitations",
        r"known\s+issues", r"performance\s+characteristics",
        r"intended\s+use", r"out.?of.?scope", r"ethical\s+considerations",
    ]
    disclosure_patterns = [
        r"ai.?generated", r"ai.?powered", r"automated\s+decision",
        r"machine.?generated", r"this.{0,20}(ai|model|algorithm)",
        r"transparency\s+notice", r"ai\s+disclosure",
        r"generated\s+by\s+(ai|model|algorithm)",
    ]

    for rel_path, abs_path in files_index:
        if _file_matches_glob(rel_path, transparency_file_patterns):
            basename_lower = os.path.basename(rel_path).lower()
            if "model_card" in basename_lower or "model-card" in basename_lower:
                filepath = Path(abs_path)
                try:
                    card_content = filepath.read_text(encoding="utf-8", errors="ignore")
                    validation = validate_model_card(card_content)
                    if validation["completeness_score"] >= 60:
                        evidence.append(f"Transparency model card {validation['completeness_score']}% complete: {', '.join(validation['sections_found'])}")
                    else:
                        evidence.append(f"Transparency model card found but only {validation['completeness_score']}% complete")
                        for section in validation["sections_missing"]:
                            gaps.append(f"Model card missing: {section.replace('_', ' ')}")
                except (OSError, IOError):
                    evidence.append(f"Transparency documentation: {rel_path}")
            else:
                evidence.append(f"Transparency documentation: {rel_path}")
            component_scores["model_card"] = 1

        content = _read_file(abs_path)
        if content is None:
            continue

        if Path(rel_path).suffix.lower() in DOC_EXTENSIONS:
            cap_matched = _search_content(content, capability_content_patterns)
            if len(cap_matched) >= 2:
                if component_scores["capabilities_docs"] == 0:
                    evidence.append(
                        f"Capability/limitation documentation ({len(cap_matched)} topics) in: {rel_path}"
                    )
                    component_scores["capabilities_docs"] = 1

        if Path(rel_path).suffix.lower() in CODE_EXTENSIONS:
            if _search_content(content, disclosure_patterns):
                if component_scores["user_disclosure"] == 0:
                    evidence.append(f"AI disclosure/transparency notice in: {rel_path}")
                    component_scores["user_disclosure"] = 1

    if component_scores["model_card"] == 0:
        gaps.append("No model card or transparency documentation found")
    if component_scores["capabilities_docs"] == 0:
        gaps.append("No documentation of system capabilities and limitations found")
    if component_scores["user_disclosure"] == 0:
        gaps.append("No user-facing AI disclosure or transparency notice found in code")

    # Scoring: 3 components — model_card, capabilities_docs, user_disclosure.
    # 0 = nothing; 30 = 1 (e.g. model card only); 65 = 2 (docs + disclosure);
    # 100 = all 3 (full transparency chain from docs to user-facing notice).
    # Same curve as Articles 10/12. Heuristic, not empirically calibrated.
    total = sum(component_scores.values())
    score_map = {0: 0, 1: 30, 2: 65, 3: 100}
    score = score_map[total]

    return score, evidence, gaps


def _check_article_14(project_path: str, files_index: list) -> tuple:
    """Article 14 — Human Oversight."""
    evidence = []
    gaps = []
    component_scores = {"oversight_mechanisms": 0, "review_before_action": 0}

    oversight_content_patterns = [
        r"human\s+oversight", r"human.?in.?the.?loop", r"human\s+review",
        r"manual\s+review", r"override", r"escalation",
        r"approval\s+workflow", r"review\s+queue", r"moderat",
    ]
    code_oversight_patterns = [
        r"require.?approval", r"needs.?review", r"await.?review",
        r"human.?review", r"manual.?override", r"escalat",
        r"review.?required", r"approval.?gate", r"review_decision",
        r"confirm.?before", r"human.?confirm",
    ]
    review_before_action_patterns = [
        r"(review|approv|confirm|verif).{0,30}(before|prior|first|then).{0,30}(action|deploy|send|publish|execute)",
        r"pending.?review", r"awaiting.?approval", r"draft.?state",
        r"human.?check.{0,20}(output|result|decision)",
    ]

    python_files = []

    for rel_path, abs_path in files_index:
        content = _read_file(abs_path)
        if content is None:
            continue

        if Path(rel_path).suffix.lower() == ".py":
            python_files.append((rel_path, abs_path))

        if Path(rel_path).suffix.lower() in DOC_EXTENSIONS:
            if _search_content(content, oversight_content_patterns):
                if component_scores["oversight_mechanisms"] == 0:
                    evidence.append(f"Human oversight documentation in: {rel_path}")
                    component_scores["oversight_mechanisms"] = 1

        if Path(rel_path).suffix.lower() in CODE_EXTENSIONS:
            if _search_content(content, code_oversight_patterns):
                evidence.append(f"Human oversight mechanism in code: {rel_path}")
                component_scores["oversight_mechanisms"] = 1

            if _search_content(content, review_before_action_patterns):
                evidence.append(f"Review-before-action pattern in: {rel_path}")
                component_scores["review_before_action"] = 1

    # AST analysis for Python files
    if _ast_analysis_available and python_files:
        for rel_path, abs_path in python_files:
            content = _read_file(abs_path)
            if content is None:
                continue
            try:
                ast_result = detect_human_oversight(content)
                if ast_result and ast_result.get("has_oversight"):
                    evidence.append(f"AST: human oversight pattern detected in: {rel_path}")
                    component_scores["oversight_mechanisms"] = 1
                    if ast_result.get("review_before_action"):
                        evidence.append(
                            f"AST: review-before-action flow detected in: {rel_path}"
                        )
                        component_scores["review_before_action"] = 1
            except (SyntaxError, ValueError, TypeError) as e:
                print(f"regula: AST oversight analysis failed for {rel_path}: {e}", file=sys.stderr)

    # JS/TS files: use ast_engine for oversight detection
    if _HAS_AST_ENGINE:
        js_ts_exts = {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"}
        for rel_path, abs_path in files_index:
            if Path(rel_path).suffix.lower() not in js_ts_exts:
                continue
            content = _read_file(abs_path)
            if content is None:
                continue
            try:
                engine_result = _ast_engine_analyse(content, rel_path)
                oversight = engine_result.get("oversight", {})
                if oversight.get("has_oversight"):
                    evidence.append(f"JS/TS oversight pattern in: {rel_path}")
                    component_scores["oversight_mechanisms"] = 1
                for ad in oversight.get("automated_decisions", []):
                    gaps.append(f"JS/TS automated decision without review: {rel_path}:{ad.get('line', '?')}")
            except Exception as e:
                print(f"regula: JS/TS AST analysis failed for {rel_path}: {e}", file=sys.stderr)

    if component_scores["oversight_mechanisms"] == 0:
        gaps.append("No human oversight mechanisms found (approval workflows, review gates, overrides)")
    if component_scores["review_before_action"] == 0:
        gaps.append("No evidence that AI outputs are reviewed by humans before action is taken")

    # Scoring: 2 components — oversight_mechanisms, review_before_action.
    # 0 = nothing; 45 = oversight exists but no review-before-action gate;
    # 100 = both present. The 45 midpoint (vs 30 for other articles) reflects that
    # any human-in-the-loop mechanism is a significant step. Heuristic, not empirically
    # calibrated.
    total = sum(component_scores.values())
    score_map = {0: 0, 1: 45, 2: 100}
    score = score_map[total]

    return score, evidence, gaps


def _check_article_15(project_path: str, files_index: list) -> tuple:
    """Article 15 — Accuracy, Robustness, Cybersecurity."""
    evidence = []
    gaps = []
    component_scores = {
        "tests": 0, "security": 0, "monitoring": 0,
        "performance": 0, "credentials": 0,
    }

    test_file_patterns = [
        "test_*", "*_test.py", "*_test.js", "*_test.ts",
        "*.test.js", "*.test.ts", "*.test.jsx", "*.test.tsx",
        "*.spec.js", "*.spec.ts",
    ]
    test_dir_names = ["tests", "test", "__tests__", "spec"]

    security_file_patterns = [
        ".snyk", ".safety", "security.md", "SECURITY.md",
        ".bandit", ".semgrep*", "trivy*", ".trivyignore",
    ]
    security_content_patterns = [
        r"safety\s+check", r"bandit", r"semgrep", r"snyk",
        r"dependency.?scan", r"vulnerability.?scan",
        r"security.?test", r"penetration.?test", r"owasp",
        r"input.?validat", r"sanitiz", r"escap",
    ]
    monitoring_patterns = [
        r"health.?check", r"readiness.?probe", r"liveness.?probe",
        r"alert", r"monitoring", r"uptime", r"heartbeat",
        r"performance.?monitor", r"model.?monitor",
        r"drift.?detect", r"data.?drift",
    ]
    performance_patterns = [
        r"benchmark", r"evaluat", r"metric", r"accuracy",
        r"precision", r"recall", r"f1.?score", r"auc",
        r"confusion.?matrix", r"cross.?validat",
        r"test.?accuracy", r"model.?eval",
    ]
    credential_patterns = [
        r"os\.environ", r"process\.env", r"getenv",
        r"dotenv", r"\.env", r"secret.?manager",
        r"vault", r"key.?management",
    ]
    hardcoded_secret_patterns = [
        r"['\"]sk-[a-zA-Z0-9]{20,}['\"]",
        r"api.?key\s*=\s*['\"][a-zA-Z0-9]{20,}['\"]",
        r"password\s*=\s*['\"][^'\"]{8,}['\"]",
    ]

    has_test_dir = False
    test_file_count = 0

    for rel_path, abs_path in files_index:
        # Test files
        if _file_matches_glob(rel_path, test_file_patterns):
            test_file_count += 1
            if component_scores["tests"] == 0:
                evidence.append(f"Test file: {rel_path}")
                component_scores["tests"] = 1

        if _is_in_directory(rel_path, test_dir_names):
            has_test_dir = True
            test_file_count += 1
            if component_scores["tests"] == 0:
                evidence.append(f"Test directory with files: {rel_path}")
                component_scores["tests"] = 1

        # Security config files
        if _file_matches_glob(rel_path, security_file_patterns):
            evidence.append(f"Security configuration: {rel_path}")
            component_scores["security"] = 1

        content = _read_file(abs_path)
        if content is None:
            continue

        if Path(rel_path).suffix.lower() in CODE_EXTENSIONS:
            if _search_content(content, security_content_patterns):
                if component_scores["security"] == 0:
                    evidence.append(f"Security measures in: {rel_path}")
                    component_scores["security"] = 1

            if _search_content(content, monitoring_patterns):
                if component_scores["monitoring"] == 0:
                    evidence.append(f"Monitoring/alerting in: {rel_path}")
                    component_scores["monitoring"] = 1

            if _search_content(content, performance_patterns):
                if component_scores["performance"] == 0:
                    evidence.append(f"Performance evaluation in: {rel_path}")
                    component_scores["performance"] = 1

            if _search_content(content, credential_patterns):
                if component_scores["credentials"] == 0:
                    evidence.append(f"Environment-based credential management in: {rel_path}")
                    component_scores["credentials"] = 1

            if _search_content(content, hardcoded_secret_patterns):
                gaps.append(f"Possible hardcoded secret in: {rel_path}")

            # Check for AI security antipatterns
            try:
                from classify_risk import check_ai_security
                sec_findings = check_ai_security(content)
                for sf in sec_findings:
                    if sf["severity"] in ("critical", "high"):
                        gaps.append(f"AI security issue in {Path(rel_path).name}: {sf['description']} (OWASP {sf['owasp']})")
                    else:
                        evidence.append(f"AI security check ran on {Path(rel_path).name}")
            except (ImportError, ValueError, TypeError) as e:
                print(f"regula: security check failed for {Path(rel_path).name}: {e}", file=sys.stderr)

    if test_file_count > 1:
        evidence.append(f"Total test files found: {test_file_count}")

    if component_scores["tests"] == 0:
        gaps.append("No test files or test directories found")
    if component_scores["security"] == 0:
        gaps.append("No security scanning or dependency vulnerability checking detected")
    if component_scores["monitoring"] == 0:
        gaps.append("No health checks, alerting, or performance monitoring detected")
    if component_scores["performance"] == 0:
        gaps.append("No model evaluation, benchmarks, or accuracy metrics found")
    if component_scores["credentials"] == 0:
        gaps.append("No environment-based credential management detected (risk of hardcoded secrets)")

    # Dependency pinning analysis (Article 15 — Cybersecurity)
    dep_pinning_score = 0
    if _dep_scan_available:
        try:
            dep_results = _scan_dependencies(project_path)
            pinning_score = dep_results.get("pinning_score", 100)
            lockfiles = dep_results.get("lockfiles", [])
            compromised_count = dep_results.get("compromised_count", 0)
            unpinned_ai = [
                d for d in dep_results.get("ai_dependencies", [])
                if d.get("pinning") == "unpinned"
            ]

            # Add lockfile evidence
            for lf in lockfiles:
                lockfile_name = Path(lf).name
                evidence.append(f"Lockfile present: {lockfile_name}")

            # Add gaps
            if pinning_score < 50:
                gaps.append(
                    f"AI dependencies are poorly pinned (score: {pinning_score}/100). "
                    "Unpinned dependencies are vulnerable to supply chain attacks."
                )
            if compromised_count > 0:
                gaps.append(
                    f"CRITICAL: {compromised_count} known compromised AI package version(s) detected"
                )
            if unpinned_ai:
                names = ", ".join(d["name"] for d in unpinned_ai)
                gaps.append(f"Unpinned AI dependencies detected: {names}")

            # Contribute to score: map pinning_score (0-100) → 0-1 component
            dep_pinning_score = 1 if pinning_score >= 50 else 0
        except Exception as e:
            print(f"regula: dependency pinning analysis failed: {e}", file=sys.stderr)

    # Scoring: 6 components — tests, security, monitoring, performance, credentials,
    # dep_pinning. Uses a piecewise linear formula rather than a lookup table because
    # there are more components. 0 = nothing; 20/40 = 1-2 (basic hygiene); 45/60 = 3-4
    # (moderate coverage); 90 = 5; 100 = all 6. The diminishing increments (20→15→30→10)
    # reflect that early components (tests, security) matter most. Heuristic, not
    # empirically calibrated.
    total = sum(component_scores.values()) + dep_pinning_score
    if total == 0:
        score = 0
    elif total <= 2:
        score = 20 * total
    elif total <= 4:
        score = 30 + 15 * (total - 2)
    elif total <= 5:
        score = 90
    else:
        score = 100

    return score, evidence, gaps


# ---------------------------------------------------------------------------
# Article checker dispatch
# ---------------------------------------------------------------------------

ARTICLE_CHECKERS = {
    "9": _check_article_9,
    "10": _check_article_10,
    "11": _check_article_11,
    "12": _check_article_12,
    "13": _check_article_13,
    "14": _check_article_14,
    "15": _check_article_15,
}


# ---------------------------------------------------------------------------
# Status classification
# ---------------------------------------------------------------------------

def _score_to_status(score: int) -> str:
    """Convert a numeric score to a human-readable status label."""
    if score == 0:
        return "not_found"
    elif score < 50:
        return "partial"
    elif score < 80:
        return "moderate"
    else:
        return "strong"


# ---------------------------------------------------------------------------
# Core assessment function
# ---------------------------------------------------------------------------

# Article 6 guidance disclosure — embedded in every assessment dict.
# TODO: Update when the Commission publishes Article 6(5) guidelines. The Feb 2026
# deadline was missed; publication is expected but not confirmed as of April 2026.
# When published, set "missed" to False, update "current_status", and revise the
# "implication" text to reflect the actual guidance content.
ARTICLE_6_GUIDELINES_STATUS = {
    "deadline": "2026-02-02",
    "deadline_source": "EU AI Act Article 6(5)",
    "missed": True,
    "draft_promised_by": "2026-02-28",
    "current_status": "not_finalised",
    "verified_on": "2026-04-08",
    "implication": (
        "Self-assessment under Article 6(3) is currently unguided. Providers "
        "should err on the side of treating systems as high-risk and document "
        "the rationale thoroughly. Re-evaluate when guidelines publish."
    ),
    "next_steps": [
        "regula exempt - structured Article 6(3) decision tree",
    ],
}


def assess_compliance(
    project_path: str,
    articles: Optional[list] = None,
    frameworks: Optional[list] = None,
) -> dict:
    """Scan a project and return a compliance gap assessment.

    Args:
        project_path: Path to the project root directory.
        articles: Optional list of article numbers to check (e.g. ["9", "14"]).
                  Defaults to all articles (9-15).

    Returns:
        A dict containing per-article scores, evidence, gaps, and an overall
        compliance score from 0-100.
    """
    project = Path(project_path).resolve()
    if not project.is_dir():
        raise ValueError(f"Project path is not a directory: {project}")

    project_name = project.name
    articles_to_check = articles if articles else ARTICLE_NUMBERS

    # Build file index once (shared across all article checkers)
    files_index = list(_walk_project(str(project)))

    # Determine highest risk tier in the project
    highest_risk = _determine_highest_risk(str(project))

    # Run article checkers
    article_results = {}
    for article_num in articles_to_check:
        if article_num not in ARTICLE_CHECKERS:
            continue
        checker = ARTICLE_CHECKERS[article_num]
        score, evidence_list, gaps_list = checker(str(project), files_index)
        status = _score_to_status(score)
        article_results[article_num] = {
            "title": ARTICLE_TITLES[article_num],
            "status": status,
            "score": score,
            "evidence": evidence_list,
            "gaps": gaps_list,
        }

    # Compute overall score (weighted average)
    if article_results:
        total_score = sum(r["score"] for r in article_results.values())
        overall_score = round(total_score / len(article_results))
    else:
        overall_score = 0

    # Generate summary
    status_counts = {"not_found": 0, "partial": 0, "moderate": 0, "strong": 0}
    for result in article_results.values():
        status_counts[result["status"]] = status_counts.get(result["status"], 0) + 1

    parts = []
    total_articles = len(article_results)
    found = total_articles - status_counts["not_found"]

    if status_counts["strong"] > 0:
        parts.append(f"{status_counts['strong']} of {total_articles} articles have strong evidence")
    if status_counts["moderate"] > 0:
        parts.append(f"{status_counts['moderate']} have moderate evidence")
    if status_counts["partial"] > 0:
        parts.append(f"{status_counts['partial']} have partial evidence")
    if status_counts["not_found"] > 0:
        parts.append(f"{status_counts['not_found']} have no evidence")

    summary = ". ".join(parts) + "." if parts else "No articles assessed."

    # Optionally enrich each article result with cross-framework mappings
    if frameworks:
        try:
            from framework_mapper import map_to_frameworks
            for article_num, result_data in article_results.items():
                fw_map = map_to_frameworks(articles=[article_num], frameworks=frameworks)
                article_map = fw_map.get(article_num, {})
                if article_map:
                    result_data["frameworks"] = article_map
        except ImportError:
            pass  # framework_mapper unavailable — degrade silently

    # Add multi-regulation overlap data
    regulation_overlap = _compute_regulation_overlap(highest_risk)

    return {
        "project": project_name,
        "highest_risk": highest_risk,
        "assessment_date": datetime.now(timezone.utc).isoformat(),
        "articles": article_results,
        "overall_score": overall_score,
        "summary": summary,
        "regulation_overlap": regulation_overlap,
        "article_6_guidelines_status": ARTICLE_6_GUIDELINES_STATUS,
    }


# ---------------------------------------------------------------------------
# Multi-regulation overlap
# ---------------------------------------------------------------------------

# Static mapping of EU AI Act articles to overlapping regulation obligations.
# These overlaps are based on the regulation texts, not dynamic analysis.
_REGULATION_OVERLAP = {
    "9": {
        "gdpr": "Article 35 — DPIA required when AI processing creates high risk to rights",
        "dora": None,
        "nis2": None,
    },
    "10": {
        "gdpr": "Articles 5(1)(d), 25 — Data accuracy and data protection by design",
        "dora": None,
        "nis2": None,
    },
    "11": {
        "gdpr": "Article 30 — Records of processing activities",
        "dora": "Article 9 — Protection and prevention (documented ICT policies and procedures)",
        "nis2": None,
    },
    "12": {
        "gdpr": "Article 30 — Records of processing activities; Article 33 — Breach notification logs",
        "dora": "Article 10 — Incident detection and logging",
        "nis2": "Article 21 — Incident handling and logging",
    },
    "13": {
        "gdpr": "Articles 13-14 — Right to information about automated decision-making",
        "dora": None,
        "nis2": None,
    },
    "14": {
        "gdpr": "Article 22 — Right not to be subject to solely automated decisions",
        "dora": None,
        "nis2": None,
    },
    "15": {
        "gdpr": "Article 32 — Security of processing",
        "dora": "Articles 5-7 — ICT risk management, testing, resilience",
        "nis2": "Article 21 — Cybersecurity risk management measures",
    },
}


def _compute_regulation_overlap(highest_risk: str) -> dict:
    """Return regulation overlap data for the gap assessment."""
    if highest_risk not in ("high_risk", "prohibited"):
        return {}

    overlap = {}
    for article, regs in _REGULATION_OVERLAP.items():
        active = {}
        for reg_name, obligation in regs.items():
            if obligation:
                active[reg_name] = obligation
        if active:
            overlap[article] = active
    return overlap


# ---------------------------------------------------------------------------
# Output formatters
# ---------------------------------------------------------------------------

def format_gap_text(assessment: dict) -> str:
    """Format assessment as human-readable CLI output."""
    lines = []
    lines.append(f"EU AI Act Compliance Gap Assessment: {assessment['project']}")
    lines.append(f"Highest risk tier: {assessment['highest_risk']}")
    lines.append(f"Assessment date:   {assessment['assessment_date']}")
    lines.append(f"Overall score:     {assessment['overall_score']}%")
    lines.append("")

    status_indicators = {
        "not_found": "NOT FOUND",
        "partial": "PARTIAL",
        "moderate": "MODERATE",
        "strong": "STRONG",
    }

    for article_num in sorted(assessment["articles"].keys(), key=int):
        result = assessment["articles"][article_num]
        title = result["title"]
        score = result["score"]
        status_label = status_indicators.get(result["status"], result["status"].upper())

        # Fixed-width formatting for alignment
        header = f"Article {article_num:<3s} {title:<35s} [{score:>3d}%] {status_label}"
        lines.append(header)

        for ev in result["evidence"]:
            lines.append(f"  Evidence: {ev}")
        for gap in result["gaps"]:
            lines.append(f"  Gap:      {gap}")

        fw_data = result.get("frameworks", {})
        if fw_data:
            lines.append("  Frameworks:")
            _FW_LABELS = {
                "lgpd": "LGPD (Lei 13.709/2018 — Brasil)",
                "marco_legal_ia": "Marco Legal da IA (PL 2338/2023 — Brasil)",
                "nist_ai_rmf": "NIST AI RMF 1.0", "iso_42001": "ISO/IEC 42001:2023",
                "nist_csf": "NIST CSF 2.0", "soc2": "SOC 2",
                "iso_27001": "ISO 27001:2022", "owasp_llm_top10": "OWASP LLM Top 10",
                "mitre_atlas": "MITRE ATLAS",
            }
            for fw_key, fw_content in fw_data.items():
                label = _FW_LABELS.get(fw_key, fw_key.upper())
                status = fw_content.get("status", "")
                lines.append(f"    {label} [{status}]" if status else f"    {label}")
                for art in fw_content.get("articles", []):
                    lines.append(f"      \u2022 {art}")
                for ctrl in fw_content.get("controls", []):
                    lines.append(f"      \u2022 {ctrl}")
                functions = fw_content.get("functions", [])
                if functions:
                    lines.append(f"      Functions: {', '.join(functions)}")
                for sub in fw_content.get("subcategories", []):
                    lines.append(f"      \u2022 {sub}")
                if fw_content.get("notes"):
                    lines.append(f"      Note: {fw_content['notes']}")

        lines.append("")

    # Regulation overlap section
    overlap = assessment.get("regulation_overlap", {})
    if overlap:
        lines.append("Regulation Overlap (AI Act + GDPR + DORA + NIS2):")
        lines.append("")
        _REG_LABELS = {"gdpr": "GDPR", "dora": "DORA", "nis2": "NIS2"}
        for article_num in sorted(overlap.keys(), key=int):
            regs = overlap[article_num]
            lines.append(f"  Article {article_num}:")
            for reg_key, obligation in regs.items():
                label = _REG_LABELS.get(reg_key, reg_key.upper())
                lines.append(f"    {label}: {obligation}")
            lines.append("")

    lines.append(f"Summary: {assessment['summary']}")
    lines.append("")
    lines.append("Article 6 guidance status (verified 2026-04-08):")
    lines.append("  The European Commission MISSED its 2 February 2026 deadline")
    lines.append("  for publishing guidelines on Article 6 high-risk classification")
    lines.append("  (Article 6(5)). A draft was promised by end-February 2026 and")
    lines.append("  has not been finalised. Self-assessment under Article 6(3) is")
    lines.append("  currently UNGUIDED. If you are considering the exemption, run:")
    lines.append("    regula exempt    - structured Article 6(3) decision tree")
    lines.append("")
    return "\n".join(lines)


def format_gap_json(assessment: dict) -> str:
    """Format assessment as JSON."""
    return json.dumps(assessment, indent=2)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="EU AI Act compliance gap assessment (Articles 9-15)"
    )
    parser.add_argument(
        "--project", "-p",
        required=True,
        help="Path to the project directory to assess",
    )
    parser.add_argument(
        "--format", "-f",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--article", "-a",
        help="Check a specific article only (e.g. 14)",
    )
    args = parser.parse_args()

    project_path = os.path.abspath(args.project)
    if not os.path.isdir(project_path):
        print(f"Error: {project_path} is not a directory", file=sys.stderr)
        sys.exit(1)

    articles = [args.article] if args.article else None
    if articles and articles[0] not in ARTICLE_NUMBERS:
        print(
            f"Error: Article {articles[0]} is not supported. "
            f"Valid articles: {', '.join(ARTICLE_NUMBERS)}",
            file=sys.stderr,
        )
        sys.exit(1)

    assessment = assess_compliance(project_path, articles=articles)

    if args.format == "json":
        print(format_gap_json(assessment))
    else:
        print(format_gap_text(assessment))


if __name__ == "__main__":
    main()
