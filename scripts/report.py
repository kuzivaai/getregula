#!/usr/bin/env python3
"""
Regula Report Generator

Generates HTML and SARIF reports from scan results and audit data.
HTML reports are single-file, portable, and designed for non-developer
stakeholders (DPOs, compliance officers, auditors).
"""

__all__ = [
    "scan_files", "scan_config_files",
    "generate_html_report", "generate_sarif", "generate_sales_report",
]

import json
import os
import re
import sys
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent))

from classify_risk import classify, RiskTier, is_ai_related, AI_INDICATORS, PROHIBITED_PATTERNS, HIGH_RISK_PATTERNS, LIMITED_RISK_PATTERNS, generate_observations, check_ai_security
from domain_scoring import compute_domain_boost
from ast_engine import detect_language
from log_event import query_events, verify_chain
from credential_check import check_secrets
from remediation import get_remediation
from agent_monitor import detect_autonomous_actions
from scan_cache import ScanCache


# ---------------------------------------------------------------------------
# File scanner (used by both HTML and SARIF generators)
# ---------------------------------------------------------------------------

from constants import CODE_EXTENSIONS, SKIP_DIRS, MODEL_EXTENSIONS, VERSION
CONFIG_FILES = {".env", ".env.production", ".env.local", "docker-compose.yml", "docker-compose.yaml", "Dockerfile"}

# AI service patterns in config/env files
_AI_CONFIG_PATTERNS = [
    (re.compile(r"OPENAI_API_KEY|ANTHROPIC_API_KEY|COHERE_API_KEY|MISTRAL_API_KEY|GROQ_API_KEY|REPLICATE_API_TOKEN|HUGGINGFACE_TOKEN|HF_TOKEN", re.IGNORECASE), "AI API key configured"),
    (re.compile(r"AZURE_OPENAI|VERTEX_AI|BEDROCK|SAGEMAKER", re.IGNORECASE), "Cloud AI service configured"),
    (re.compile(r"tensorflow/serving|vllm|ollama|tritonserver|text-generation-inference", re.IGNORECASE), "AI model serving container"),
    (re.compile(r"openai|anthropic|google.generativeai|aws.sagemaker|azurerm_openai", re.IGNORECASE), "AI provider reference"),
]


def scan_config_files(project_path: str) -> list:
    """Scan config/env files for AI service references.

    Returns findings for AI infrastructure detected in configuration files.
    """
    project = Path(project_path).resolve()
    findings = []

    for root, dirs, files in os.walk(project):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for filename in files:
            if filename not in CONFIG_FILES:
                continue
            filepath = Path(root) / filename
            try:
                content = filepath.read_text(encoding="utf-8", errors="ignore")
            except (PermissionError, OSError):
                continue

            rel_path = str(filepath.relative_to(project))
            for rx, description in _AI_CONFIG_PATTERNS:
                match = rx.search(content)
                if match:
                    # Find line number
                    line_num = 1
                    for i, line in enumerate(content.split("\n"), 1):
                        if rx.search(line):
                            line_num = i
                            break
                    findings.append({
                        "file": rel_path,
                        "line": line_num,
                        "tier": "minimal_risk",
                        "category": "AI Infrastructure",
                        "description": f"{description}: {match.group()[:40]}",
                        "indicators": ["ai_config"],
                        "confidence_score": 30,
                        "suppressed": False,
                    })
                    break  # One finding per config file

    return findings


def _is_test_file(filepath: Path) -> bool:
    """Detect if a file is a test file (findings should be deprioritised).

    Catches standard test conventions across Python, JS/TS ecosystems,
    plus package-level test directories (e.g. langchain_tests/, standard-tests/).
    """
    name = filepath.name.lower()
    parts = [p.lower() for p in filepath.parts]
    # File name patterns
    if name.startswith("test_") or name.endswith("_test.py") or name == "conftest.py":
        return True
    if name.endswith(".spec.ts") or name.endswith(".spec.js") or name.endswith(".test.ts") or name.endswith(".test.js"):
        return True
    # Directory patterns — exact matches
    if "test" in parts or "tests" in parts or "__tests__" in parts or "spec" in parts:
        return True
    # Directory patterns — suffix/prefix matches (e.g. standard-tests, langchain_tests)
    if any(p.endswith("tests") or p.endswith("_tests") or p.startswith("test_") for p in parts):
        return True
    return False


def _is_example_file(filepath: Path) -> bool:
    """Detect example/demo/tutorial files (findings should be deprioritised)."""
    parts = [p.lower() for p in filepath.parts]
    return any(p in ("example", "examples", "demo", "demos", "tutorial",
                      "tutorials", "sample", "samples", "cookbook")
               for p in parts)


def _is_init_file(filepath: Path) -> bool:
    """Detect __init__.py files (usually re-exports, not real logic)."""
    return filepath.name == "__init__.py"


def _has_mock_patterns(content: str) -> bool:
    """Detect if file is primarily mock/fixture/stub code."""
    indicators = 0
    lower = content.lower()
    for pattern in ("unittest.mock", "from mock import", "mock.patch",
                    "@patch", "mocker.patch", "pytest.fixture",
                    "create_autospec", "magicmock", "fakeclient"):
        if pattern in lower:
            indicators += 1
    return indicators >= 2


def _compute_context_penalty(filepath: Path, content: str, is_test: bool) -> int:
    """Compute additional confidence penalty based on file context.

    Returns a penalty to subtract (0 = no penalty). Test files keep the
    existing -40 flat penalty; this function adds penalties for other
    low-signal contexts that weren't previously handled.
    """
    # Test files handled separately (existing -40 flat, don't double-penalise)
    if is_test:
        return 0

    penalty = 0

    if _is_example_file(filepath):
        penalty = max(penalty, 20)

    if _is_init_file(filepath):
        penalty = max(penalty, 25)

    if _has_mock_patterns(content):
        penalty = max(penalty, 25)

    return penalty


def _scan_agent_autonomy(content, lines, rel_path, is_test, respect_ignores):
    """Detect agent autonomy risks in a single file.

    Runs on ALL code files (not just AI-related) because agent tool
    infrastructure may not import AI libraries directly.
    """
    results = []
    try:
        autonomy_findings = detect_autonomous_actions(content, rel_path)
        for af in autonomy_findings:
            base_confidence = 70 if not af["has_human_gate"] else 45
            if af.get("detection_mode") == "contextual":
                base_confidence -= 10
            confidence = max(base_confidence - (40 if is_test else 0), 10)

            suppressed = False
            if respect_ignores:
                for line in lines:
                    stripped = line.strip()
                    if "regula-ignore" in stripped:
                        if "regula-ignore:" not in stripped:
                            suppressed = True
                        elif "agent-autonomy" in stripped:
                            suppressed = True

            results.append({
                "file": rel_path,
                "line": af["line"],
                "tier": "agent_autonomy",
                "category": f"Agent Autonomy ({af['owasp_ref']})",
                "description": af["description"],
                "indicators": [af["action_pattern"]],
                "confidence_score": confidence,
                "suppressed": suppressed,
            })
    except (ValueError, KeyError, AttributeError):
        pass
    return results


def _scan_credentials(content, lines, rel_path, is_test, suppressed):
    """Detect credential exposure in a single file."""
    results = []
    try:
        secret_findings = check_secrets(content)
        for sf in secret_findings:
            secret_line = 1
            for i, line_text in enumerate(lines, 1):
                if sf.redacted_value[:4] in line_text:
                    secret_line = i
                    break

            results.append({
                "file": rel_path,
                "line": secret_line,
                "tier": "credential_exposure",
                "category": "AI Credential Governance (Article 15)",
                "description": (
                    f"{sf.description} in AI system code. "
                    f"Article 15 requires cybersecurity measures for high-risk systems. "
                    f"Fix: {sf.remediation}"
                ),
                "indicators": [sf.pattern_name],
                "confidence_score": max(sf.confidence_score - 40, 10) if is_test else sf.confidence_score,
                "suppressed": suppressed,
            })
    except (ValueError, KeyError, AttributeError):
        pass
    return results


def _scan_ai_security(content, rel_path, is_test, suppressed):
    """Detect AI security antipatterns in a single file."""
    results = []
    try:
        security_findings = check_ai_security(content)
        for sf in security_findings:
            results.append({
                "file": rel_path,
                "line": sf["line"],
                "tier": "ai_security",
                "category": f"AI Security ({sf['owasp']})",
                "description": sf["description"],
                "indicators": [sf["pattern_name"]],
                "confidence_score": max({"critical": 90, "high": 80, "medium": 60, "low": 40}.get(sf["severity"], 50) - (40 if is_test else 0), 10),
                "suppressed": suppressed,
                "remediation": sf["remediation"],
            })
    except (ValueError, KeyError, AttributeError):
        pass
    return results


def _parse_suppression_rules(lines, respect_ignores):
    """Extract suppression rules from regula-ignore comments."""
    suppressed_rules = set()
    if respect_ignores:
        for line in lines:
            stripped = line.strip()
            if "regula-ignore" in stripped:
                if ":" in stripped and "regula-ignore:" in stripped:
                    rule_part = stripped.split("regula-ignore:")[-1].strip()
                    suppressed_rules.add(rule_part.lower())
                else:
                    suppressed_rules.add("*")
    return suppressed_rules


def scan_files(project_path: str, respect_ignores: bool = True,
               skip_tests: bool = False, min_tier: str = "") -> list:
    """Scan project files and return findings with file locations.

    Args:
        project_path: Directory to scan.
        respect_ignores: Honour regula-ignore comments.
        skip_tests: Exclude test files entirely from results.
        min_tier: Minimum tier to include ("prohibited", "high_risk",
                  "limited_risk", "minimal_risk"). Empty string means all.
    """
    project = Path(project_path).resolve()
    findings = []

    # Initialise scan cache (failures must never block a scan)
    cache = None
    try:
        cache = ScanCache()
    except Exception:
        pass

    # Tier ordering for --min-tier filtering
    _TIER_ORDER = {
        "prohibited": 4, "credential_exposure": 3, "high_risk": 3,
        "ai_security": 3, "agent_autonomy": 3,
        "limited_risk": 2, "minimal_risk": 1,
    }
    min_tier_level = _TIER_ORDER.get(min_tier, 0)

    # Single-file mode: synthesise a walk-compatible structure for one file
    if project.is_file():
        walk_iter = [(str(project.parent), [], [project.name])]
        project = project.parent
    else:
        walk_iter = os.walk(project)

    for root, dirs, files in walk_iter:
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for filename in files:
            filepath = Path(root) / filename
            is_test = _is_test_file(filepath)

            # Skip test files entirely if requested
            if skip_tests and is_test:
                continue

            # Model files
            if filepath.suffix.lower() in MODEL_EXTENSIONS:
                if min_tier_level <= 1:
                    findings.append({
                        "file": str(filepath.relative_to(project)),
                        "line": 1,
                        "tier": "minimal_risk",
                        "category": "Model File",
                        "description": f"AI model file detected: {filepath.suffix}",
                        "indicators": [filepath.suffix],
                        "confidence_score": 30,
                        "suppressed": False,
                    })
                continue

            if filepath.suffix not in CODE_EXTENSIONS:
                continue

            try:
                lines = filepath.read_text(encoding="utf-8", errors="ignore").split("\n")
            except (PermissionError, OSError):
                continue

            content = "\n".join(lines)
            rel_path = str(filepath.relative_to(project))

            # Check scan cache — if content unchanged, reuse cached findings
            try:
                if cache is not None:
                    cached = cache.get(rel_path, content)
                    if cached is not None:
                        if min_tier_level > 0:
                            cached = [f for f in cached
                                      if _TIER_ORDER.get(f.get("tier", ""), 0) >= min_tier_level]
                        findings.extend(cached)
                        continue
            except Exception:
                pass

            # Track per-file findings for caching
            file_findings_start = len(findings)

            # Agent autonomy detection (runs on ALL code files)
            if min_tier_level <= _TIER_ORDER.get("agent_autonomy", 3):
                findings.extend(_scan_agent_autonomy(content, lines, rel_path, is_test, respect_ignores))

            if not is_ai_related(content):
                try:
                    if cache is not None:
                        cache.put(rel_path, content, findings[file_findings_start:])
                except Exception:
                    pass
                continue

            suppressed_rules = _parse_suppression_rules(lines, respect_ignores)

            # Credential governance (AI-related files only)
            secret_suppressed = "*" in suppressed_rules or "secrets" in suppressed_rules
            if min_tier_level <= _TIER_ORDER.get("credential_exposure", 3):
                findings.extend(_scan_credentials(content, lines, rel_path, is_test, secret_suppressed))

            # AI security antipatterns
            if min_tier_level <= _TIER_ORDER.get("ai_security", 3):
                findings.extend(_scan_ai_security(content, rel_path, is_test, secret_suppressed or "*" in suppressed_rules))

            lang = detect_language(filename) or "python"
            result = classify(content, language=lang)
            if result.tier in (RiskTier.NOT_AI, RiskTier.MINIMAL_RISK) and not result.indicators_matched:
                if min_tier_level <= 1:
                    findings.append({
                        "file": rel_path,
                        "line": 1,
                        "tier": "minimal_risk",
                        "category": "AI Code",
                        "description": "AI-related code with no specific risk indicators",
                        "indicators": [],
                        "confidence_score": 20,
                        "suppressed": "*" in suppressed_rules,
                    })
                try:
                    if cache is not None:
                        cache.put(rel_path, content, findings[file_findings_start:])
                except Exception:
                    pass
                continue

            # Skip findings below min_tier threshold
            tier_level = _TIER_ORDER.get(result.tier.value, 0)
            if tier_level < min_tier_level:
                try:
                    if cache is not None:
                        cache.put(rel_path, content, findings[file_findings_start:])
                except Exception:
                    pass
                continue

            is_suppressed = "*" in suppressed_rules
            for indicator in result.indicators_matched:
                if indicator.lower() in suppressed_rules:
                    is_suppressed = True

            # Calculate confidence score
            base_score = {
                "prohibited": 85, "high_risk": 65,
                "limited_risk": 45, "minimal_risk": 20,
            }.get(result.tier.value, 20)
            indicator_bonus = min(len(result.indicators_matched) * 8, 15)

            # Domain-aware boost: co-occurrence of AI + regulatory domain keywords
            domain_result = compute_domain_boost(content, is_ai_related(content))
            domain_boost = domain_result["boost"]

            confidence_score = min(base_score + indicator_bonus + domain_boost, 100)

            # Deprioritise test file findings (reduce to INFO tier)
            if is_test and result.tier.value != "prohibited":
                confidence_score = max(confidence_score - 40, 10)

            # Context-aware penalty for examples, __init__, mocks
            if result.tier.value != "prohibited":
                ctx_penalty = _compute_context_penalty(filepath, content, is_test)
                if ctx_penalty > 0:
                    confidence_score = max(confidence_score - ctx_penalty, 10)

            # Generate Article-specific observations for high-risk findings
            observations = []
            if result.tier == RiskTier.HIGH_RISK:
                try:
                    observations = generate_observations(content)
                except (ValueError, KeyError, TypeError):
                    pass

            findings.append({
                "file": rel_path,
                "line": 1,
                "tier": result.tier.value,
                "category": result.category or "Unknown",
                "description": result.description or result.message or "",
                "indicators": result.indicators_matched,
                "articles": result.applicable_articles,
                "exceptions": result.exceptions,
                "confidence_score": confidence_score,
                "suppressed": is_suppressed,
                "observations": observations,
            })

            # Cache findings collected for this file
            try:
                if cache is not None:
                    cache.put(rel_path, content, findings[file_findings_start:])
            except Exception:
                pass

    # Flush cache to disk
    try:
        if cache is not None:
            cache.flush()
    except Exception:
        pass

    # Config/env file scanning for AI service references
    try:
        config_findings = scan_config_files(project_path)
        if min_tier_level <= 1:  # only include if minimal_risk tier is in scope
            findings.extend(config_findings)
    except Exception:
        pass

    return findings


# ---------------------------------------------------------------------------
# HTML report
# ---------------------------------------------------------------------------

_CSS = """
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background: #f8f9fa; color: #212529; line-height: 1.6; }
.container { max-width: 1100px; margin: 0 auto; padding: 24px; }
header { background: #1a1a2e; color: #fff; padding: 32px 0; margin-bottom: 24px; }
header .container { display: flex; justify-content: space-between; align-items: center; }
header h1 { font-size: 1.5rem; font-weight: 600; }
header .meta { font-size: 0.85rem; opacity: 0.8; text-align: right; }
.disclaimer { background: #fff3cd; border: 1px solid #ffc107; border-radius: 6px; padding: 16px; margin-bottom: 24px; font-size: 0.85rem; color: #664d03; }
.summary-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 24px; }
.card { background: #fff; border-radius: 8px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
.card .number { font-size: 2rem; font-weight: 700; }
.card .label { font-size: 0.85rem; color: #6c757d; margin-top: 4px; }
.card.red { border-left: 4px solid #dc3545; }
.card.red .number { color: #dc3545; }
.card.amber { border-left: 4px solid #fd7e14; }
.card.amber .number { color: #fd7e14; }
.card.green { border-left: 4px solid #198754; }
.card.green .number { color: #198754; }
.card.blue { border-left: 4px solid #0d6efd; }
.card.blue .number { color: #0d6efd; }
.card.purple { border-left: 4px solid #6f42c1; }
.card.purple .number { color: #6f42c1; }
.section { background: #fff; border-radius: 8px; padding: 24px; margin-bottom: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
.section h2 { font-size: 1.1rem; margin-bottom: 16px; padding-bottom: 8px; border-bottom: 1px solid #dee2e6; }
table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
th { background: #f8f9fa; text-align: left; padding: 10px 12px; border-bottom: 2px solid #dee2e6; font-weight: 600; }
td { padding: 10px 12px; border-bottom: 1px solid #eee; vertical-align: top; }
tr:hover { background: #f8f9fa; }
tr.suppressed { opacity: 0.5; text-decoration: line-through; }
.badge { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; }
.badge.prohibited { background: #dc3545; color: #fff; }
.badge.high-risk { background: #fd7e14; color: #fff; }
.badge.limited-risk { background: #0d6efd; color: #fff; }
.badge.minimal-risk { background: #198754; color: #fff; }
.badge.credential-exposure { background: #6f42c1; color: #fff; }
.confidence-bar { display: inline-block; width: 60px; height: 8px; background: #e9ecef; border-radius: 4px; overflow: hidden; vertical-align: middle; }
.confidence-fill { height: 100%; border-radius: 4px; }
.top3 { list-style: none; }
.top3 li { padding: 8px 0; border-bottom: 1px solid #eee; }
.top3 li:last-child { border-bottom: none; }
.chain-status { font-weight: 600; }
.chain-valid { color: #198754; }
.chain-invalid { color: #dc3545; }
footer { text-align: center; padding: 24px; font-size: 0.8rem; color: #6c757d; }
.dep-score { font-size: 2rem; font-weight: 700; }
.dep-score.good { color: #198754; }
.dep-score.moderate { color: #fd7e14; }
.dep-score.poor { color: #dc3545; }
.badge.hash { background: #198754; color: #fff; }
.badge.exact { background: #198754; color: #fff; }
.badge.range { background: #fd7e14; color: #fff; }
.badge.unpinned { background: #dc3545; color: #fff; }
.badge.compromised { background: #dc3545; color: #fff; animation: pulse 1s infinite; }
@keyframes pulse { 0%,100% { opacity:1; } 50% { opacity:0.7; } }
.framework-table td { font-size: 0.8rem; }
"""


def _tier_badge(tier: str) -> str:
    display = tier.upper().replace("_", "-")
    css_class = tier.replace("_", "-")
    return f'<span class="badge {css_class}">{display}</span>'


def _confidence_bar(score: int) -> str:
    color = "#dc3545" if score >= 80 else "#fd7e14" if score >= 50 else "#198754"
    return (
        f'<span class="confidence-bar">'
        f'<span class="confidence-fill" style="width:{score}%;background:{color}"></span>'
        f'</span> {score}'
    )


def generate_html_report(
    findings: list,
    project_name: str,
    audit_events: Optional[list] = None,
    chain_valid: Optional[bool] = None,
    dependency_results: Optional[dict] = None,
    framework_mappings: Optional[dict] = None,
) -> str:
    """Generate a single-file HTML report."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # Calculate stats
    active = [f for f in findings if not f.get("suppressed")]
    prohibited_count = sum(1 for f in active if f["tier"] == "prohibited")
    high_risk_count = sum(1 for f in active if f["tier"] == "high_risk")
    limited_count = sum(1 for f in active if f["tier"] == "limited_risk")
    minimal_count = sum(1 for f in active if f["tier"] == "minimal_risk")
    credential_count = sum(1 for f in active if f["tier"] == "credential_exposure")
    suppressed_count = sum(1 for f in findings if f.get("suppressed"))
    total_files = len(set(f["file"] for f in findings))

    # Top risks — include credential exposure as a priority finding
    top_risks = []
    seen_categories = set()
    for f in sorted(active, key=lambda x: -x.get("confidence_score", 0)):
        cat = f.get("category", "")
        if cat and cat not in seen_categories and f["tier"] in ("prohibited", "high_risk", "credential_exposure"):
            seen_categories.add(cat)
            top_risks.append(f)
            if len(top_risks) >= 3:
                break

    # Build HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Regula Report — {escape(project_name)}</title>
<style>{_CSS}</style>
</head>
<body>

<header>
<div class="container">
<div>
<h1>Regula — AI Governance Report</h1>
<div style="margin-top:4px;font-size:0.9rem;">{escape(project_name)}</div>
</div>
<div class="meta">
Generated: {now}<br>
Regula v{VERSION}
</div>
</div>
</header>

<div class="container">

<div class="disclaimer">
<strong>Important:</strong> This report contains pattern-based risk <em>indications</em>,
not legal risk classifications. The EU AI Act (Article 6) requires contextual assessment
of intended purpose and deployment context. Results should be reviewed by qualified
personnel. This is not legal advice.
</div>

<div class="summary-grid">
<div class="card red">
<div class="number">{prohibited_count}</div>
<div class="label">Prohibited Patterns</div>
</div>
<div class="card amber">
<div class="number">{high_risk_count}</div>
<div class="label">High-Risk Indicators</div>
</div>
<div class="card blue">
<div class="number">{limited_count}</div>
<div class="label">Limited-Risk</div>
</div>
<div class="card purple">
<div class="number">{credential_count}</div>
<div class="label">Credential Findings</div>
</div>
<div class="card green">
<div class="number">{total_files}</div>
<div class="label">AI Files Scanned</div>
</div>
</div>
"""

    # Executive summary — plain-English block for non-technical readers
    scanned_files = len(set(f["file"] for f in findings if not f.get("suppressed")))
    if total_files == 0:
        exec_verdict = "No AI-related files detected"
        exec_colour = "#6b7280"
        exec_detail = (
            "Regula did not find any AI-related source files in the scanned directory. "
            "This may mean the scan path is incorrect, the project has not yet integrated AI components, "
            "or all files were excluded by ignore rules. Verify the scan path before treating this as a clean result."
        )
    elif prohibited_count > 0:
        exec_verdict = "Action required before deployment"
        exec_colour = "#dc2626"
        exec_detail = (
            f"This codebase contains {prohibited_count} pattern(s) associated with practices "
            "that are prohibited under EU AI Act Article 5 (e.g. social scoring, real-time biometric surveillance). "
            "These must be resolved before the system can lawfully enter the EU market."
        )
        if credential_count > 0:
            exec_detail += (
                f" Additionally, {credential_count} credential finding(s) were detected and should be reviewed."
            )
    elif high_risk_count > 0:
        exec_verdict = "High-risk indicators detected — compliance review needed"
        exec_colour = "#d97706"
        exec_detail = (
            f"This codebase contains {high_risk_count} indicator(s) of high-risk AI functionality "
            "(Article 6). If this system is deployed in the EU in a high-risk context (e.g. credit scoring, "
            "employment, healthcare), it will be subject to mandatory obligations including risk management, "
            "data governance, human oversight, and technical documentation. "
            "A compliance review is recommended before deployment."
        )
        if credential_count > 0:
            exec_detail += (
                f" Additionally, {credential_count} credential finding(s) were detected and should be reviewed."
            )
    elif credential_count > 0:
        exec_verdict = "Credential exposure detected — security review needed"
        exec_colour = "#7c3aed"
        exec_detail = (
            f"No prohibited or high-risk AI patterns were found, but {credential_count} credential "
            "finding(s) were detected. Exposed API keys or secrets represent a data security risk "
            "and should be reviewed and rotated before deployment."
        )
    else:
        exec_verdict = "No prohibited or high-risk patterns detected"
        exec_colour = "#16a34a"
        exec_detail = (
            "This codebase does not show patterns associated with prohibited or high-risk AI under the EU AI Act. "
            f"{limited_count} limited-risk indicator(s) were found — these carry transparency obligations "
            "(e.g. disclosing automated decision-making to users) but do not require the full high-risk compliance regime."
            if limited_count > 0 else
            "This codebase does not show patterns associated with prohibited, high-risk, or limited-risk AI under the EU AI Act."
        )

    html += f"""
<div class="section" style="border-left:4px solid {exec_colour};padding-left:20px;margin-bottom:24px;">
<h2 style="color:{exec_colour};margin-bottom:8px;">Executive Summary</h2>
<p style="font-size:1.05rem;font-weight:600;color:#1a1a2e;margin-bottom:8px;">{escape(exec_verdict)}</p>
<p style="color:#5a5a6e;line-height:1.6;">{escape(exec_detail)}</p>
<p style="margin-top:12px;font-size:0.85rem;color:#9b9baa;">
Scanned {total_files} file(s) &middot; {prohibited_count} prohibited &middot; {high_risk_count} high-risk &middot;
{limited_count} limited-risk &middot; {credential_count} credential finding(s) &middot; Generated {now}
</p>
</div>
"""

    # Top risks section
    if top_risks:
        html += '<div class="section"><h2>Priority Risk Indicators</h2><ul class="top3">'
        for r in top_risks:
            html += f'<li>{_tier_badge(r["tier"])} <strong>{escape(r.get("category", ""))}</strong> — {escape(r.get("description", ""))} ({escape(r["file"])})</li>'
        html += '</ul></div>'

    # Audit status
    if chain_valid is not None:
        status_class = "chain-valid" if chain_valid else "chain-invalid"
        status_text = "Valid" if chain_valid else "INTEGRITY FAILURE"
        audit_count = len(audit_events) if audit_events else 0
        blocked_count = sum(1 for e in (audit_events or []) if e.get("event_type") == "blocked")
        html += f"""
<div class="section">
<h2>Audit Trail Status</h2>
<p>Hash chain integrity: <span class="chain-status {status_class}">{status_text}</span></p>
<p>Events logged: {audit_count} | Blocked actions: {blocked_count} | Suppressed findings: {suppressed_count}</p>
</div>
"""

    # Dependency analysis section
    if dependency_results is not None:
        pinning_score = dependency_results.get("pinning_score", 0)
        if pinning_score >= 80:
            score_class = "good"
        elif pinning_score >= 50:
            score_class = "moderate"
        else:
            score_class = "poor"

        ai_deps = dependency_results.get("ai_dependencies", [])
        lockfiles = dependency_results.get("lockfiles", [])
        compromised_count = dependency_results.get("compromised_count", 0)
        compromised = dependency_results.get("compromised", [])

        lockfile_status = escape(", ".join(lockfiles)) if lockfiles else "None detected"
        compromised_card_class = "red" if compromised_count > 0 else "green"

        html += f"""
<div class="section">
<h2>Dependency Supply Chain Analysis</h2>
<div class="summary-grid">
<div class="card {'green' if pinning_score >= 80 else 'amber' if pinning_score >= 50 else 'red'}">
<div class="dep-score {score_class}">{pinning_score}</div>
<div class="label">Pinning Score (0–100)</div>
</div>
<div class="card blue">
<div class="number">{len(ai_deps)}</div>
<div class="label">AI Dependencies</div>
</div>
<div class="card {'green' if lockfiles else 'amber'}">
<div class="number" style="font-size:1rem;margin-top:4px;">{escape(lockfile_status)}</div>
<div class="label">Lockfile Status</div>
</div>
<div class="card {compromised_card_class}">
<div class="number">{compromised_count}</div>
<div class="label">Compromised Packages</div>
</div>
</div>
"""
        if ai_deps:
            html += """<table>
<thead>
<tr><th>Name</th><th>Version</th><th>Pinning Quality</th><th>Status</th></tr>
</thead>
<tbody>
"""
            compromised_names = {c if isinstance(c, str) else c.get("name", "") for c in compromised}
            for dep in ai_deps:
                name = dep.get("name", "")
                version = dep.get("version", "—")
                pinning = dep.get("pinning", "unpinned").lower()
                is_compromised = name in compromised_names
                status_badge = '<span class="badge compromised">COMPROMISED</span>' if is_compromised else '<span style="color:#198754;">OK</span>'
                pinning_badge = f'<span class="badge {escape(pinning)}">{escape(pinning.upper())}</span>'
                html += f"""<tr>
<td>{escape(name)}</td>
<td>{escape(str(version))}</td>
<td>{pinning_badge}</td>
<td>{status_badge}</td>
</tr>
"""
            html += "</tbody>\n</table>\n"
        html += "</div>\n"

    # Framework mapping section — auto-load if not supplied by caller
    if framework_mappings is None:
        try:
            from framework_mapper import map_to_frameworks
            framework_mappings = map_to_frameworks(["9", "10", "11", "12", "13", "14", "15"])
        except Exception:
            framework_mappings = None

    if framework_mappings is not None:
        html += """
<div class="section">
<h2>Regulatory Framework Mappings</h2>
<table class="framework-table">
<thead>
<tr><th>Article</th><th>EU AI Act</th><th>NIST AI RMF</th><th>ISO 42001</th><th>UK ICO</th></tr>
</thead>
<tbody>
"""
        for article, mapping in framework_mappings.items():
            eu = mapping.get("eu_ai_act", {})
            eu_text = escape(eu.get("title", "—")) if isinstance(eu, dict) else escape(str(eu))

            nist = mapping.get("nist_ai_rmf", {})
            if isinstance(nist, dict) and nist.get("subcategories"):
                nist_text = escape(", ".join(nist["subcategories"][:2]))
            elif isinstance(nist, dict) and nist.get("functions"):
                nist_text = escape(", ".join(nist["functions"]))
            else:
                nist_text = escape(str(nist)) if nist else "—"

            iso = mapping.get("iso_42001", {})
            if isinstance(iso, dict) and iso.get("controls"):
                iso_text = escape(", ".join(iso["controls"][:2]))
            else:
                iso_text = escape(str(iso)) if iso else "—"

            ico = mapping.get("ico_ai", {})
            if isinstance(ico, dict) and ico.get("principles"):
                ico_text = escape("; ".join(ico["principles"][:2]))
            elif isinstance(ico, dict) and ico.get("source"):
                ico_text = escape(ico["source"])
            else:
                ico_text = "—"

            html += f"""<tr>
<td><strong>Art. {escape(str(article))}</strong></td>
<td>{eu_text}</td>
<td>{nist_text}</td>
<td>{iso_text}</td>
<td>{ico_text}</td>
</tr>
"""
        html += "</tbody>\n</table>\n</div>\n"

    # Findings table
    html += """
<div class="section">
<h2>All Findings</h2>
<table>
<thead>
<tr><th>File</th><th>Risk Tier</th><th>Category</th><th>Confidence</th><th>Description</th><th>Remediation</th></tr>
</thead>
<tbody>
"""
    for f in sorted(findings, key=lambda x: (
        {"prohibited": 0, "credential_exposure": 1, "high_risk": 2, "limited_risk": 3, "minimal_risk": 4}.get(x["tier"], 5),
        -x.get("confidence_score", 0),
    )):
        row_class = ' class="suppressed"' if f.get("suppressed") else ""
        desc = escape(f.get("description", ""))
        if f.get("exceptions"):
            desc += f' <em>(Exception: {escape(f["exceptions"])})</em>'
        if f.get("suppressed"):
            desc += " [SUPPRESSED]"
        # Generate remediation for non-minimal findings
        rem_html = ""
        if f["tier"] in ("prohibited", "high_risk", "credential_exposure", "limited_risk"):
            rem = get_remediation(
                f["tier"],
                f.get("category", ""),
                f.get("indicators", []),
                f.get("file", ""),
                f.get("description", ""),
            )
            rem_parts = []
            if rem.get("summary"):
                rem_parts.append(f'<strong>{escape(rem["summary"])}</strong>')
            if rem.get("fix_command"):
                rem_parts.append(f'<code>{escape(rem["fix_command"])}</code>')
            if rem.get("article"):
                rem_parts.append(f'<em>{escape(rem["article"])}</em>')
            rem_html = "<br>".join(rem_parts)
        html += f"""<tr{row_class}>
<td>{escape(f["file"])}</td>
<td>{_tier_badge(f["tier"])}</td>
<td>{escape(f.get("category", "—"))}</td>
<td>{_confidence_bar(f.get("confidence_score", 0))}</td>
<td>{desc}</td>
<td>{rem_html}</td>
</tr>
"""

    html += f"""
</tbody>
</table>
</div>

</div>

<footer>
Generated by Regula v{VERSION} — AI Governance Risk Indication<br>
Pattern-based analysis only. Not a substitute for legal advice or DPO review.
</footer>

</body>
</html>"""

    return html


# ---------------------------------------------------------------------------
# SARIF output
# ---------------------------------------------------------------------------

SARIF_SEVERITY_MAP = {
    "prohibited": "error",
    "credential_exposure": "error",
    "agent_autonomy": "warning",
    "high_risk": "warning",
    "limited_risk": "note",
    "minimal_risk": "none",
    "ai_security": "warning",
}


def generate_sarif(findings: list, project_name: str) -> dict:
    """Generate SARIF v2.1.0 output for CI/CD integration."""
    rules = {}
    results = []

    # Build rules from pattern definitions
    for rule_id, config in PROHIBITED_PATTERNS.items():
        rules[f"regula/prohibited/{rule_id}"] = {
            "id": f"regula/prohibited/{rule_id}",
            "name": rule_id.replace("_", " ").title(),
            "shortDescription": {"text": config["description"]},
            "fullDescription": {"text": f"EU AI Act Article {config['article']}: {config['description']}"},
            "defaultConfiguration": {"level": "error"},
            "helpUri": f"https://artificialintelligenceact.eu/article/5/",
        }

    for rule_id, config in HIGH_RISK_PATTERNS.items():
        rules[f"regula/high-risk/{rule_id}"] = {
            "id": f"regula/high-risk/{rule_id}",
            "name": rule_id.replace("_", " ").title(),
            "shortDescription": {"text": config["description"]},
            "fullDescription": {"text": f"EU AI Act {config['category']}: {config['description']}. Articles {', '.join(config['articles'])} may apply."},
            "defaultConfiguration": {"level": "warning"},
            "helpUri": "https://artificialintelligenceact.eu/annex/3/",
        }

    # Credential governance rules
    from credential_check import SECRET_PATTERNS
    for rule_id, config in SECRET_PATTERNS.items():
        rules[f"regula/credential/{rule_id}"] = {
            "id": f"regula/credential/{rule_id}",
            "name": config["description"],
            "shortDescription": {"text": f"AI credential governance: {config['description']}"},
            "fullDescription": {"text": f"EU AI Act Article 15 cybersecurity: {config['description']}. {config['remediation']}"},
            "defaultConfiguration": {"level": "error" if config["confidence"] == "high" else "warning"},
            "helpUri": "https://artificialintelligenceact.eu/article/15/",
        }

    for rule_id, config in LIMITED_RISK_PATTERNS.items():
        rules[f"regula/limited-risk/{rule_id}"] = {
            "id": f"regula/limited-risk/{rule_id}",
            "name": rule_id.replace("_", " ").title(),
            "shortDescription": {"text": config["description"]},
            "fullDescription": {"text": f"EU AI Act Article 50: {config['description']}. Transparency obligation applies."},
            "defaultConfiguration": {"level": "note"},
            "helpUri": "https://artificialintelligenceact.eu/article/50/",
        }

    # Build results from findings
    for f in findings:
        if f.get("suppressed"):
            continue

        tier = f["tier"]
        indicators = f.get("indicators", [])
        primary_indicator = indicators[0] if indicators else "unknown"

        # Match to a rule
        if tier == "prohibited":
            rule_id = f"regula/prohibited/{primary_indicator}"
        elif tier == "credential_exposure":
            rule_id = f"regula/credential/{primary_indicator}"
        elif tier == "high_risk":
            rule_id = f"regula/high-risk/{primary_indicator}"
        elif tier == "agent_autonomy":
            rule_id = f"regula/agent-autonomy/{primary_indicator}"
        elif tier == "ai_security":
            rule_id = f"regula/ai-security/{primary_indicator}"
        elif tier == "limited_risk":
            rule_id = f"regula/limited-risk/{primary_indicator}"
        else:
            continue  # Don't include minimal-risk in SARIF

        result = {
            "ruleId": rule_id,
            "level": SARIF_SEVERITY_MAP.get(tier, "none"),
            "message": {
                "text": f.get("description", "Risk indicator detected"),
            },
            "locations": [{
                "physicalLocation": {
                    "artifactLocation": {"uri": f["file"]},
                    "region": {"startLine": f.get("line", 1)},
                },
            }],
            "properties": {
                "confidence_score": f.get("confidence_score", 0),
            },
        }
        results.append(result)

    return {
        "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/main/sarif-2.1/schema/sarif-schema-2.1.0.json",
        "version": "2.1.0",
        "runs": [{
            "tool": {
                "driver": {
                    "name": "Regula",
                    "version": VERSION,
                    "informationUri": "https://github.com/kuzivaai/getregula",
                    "rules": list(rules.values()),
                },
            },
            "results": results,
        }],
    }


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def generate_sales_report(findings: list, project_name: str) -> str:
    """Generate a compact, shareable HTML compliance summary.

    Designed to be sent to enterprise buyers who ask for evidence of EU AI Act
    compliance awareness before signing contracts. Single-file, no external deps.
    """
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    active = [f for f in findings if not f.get("suppressed")]
    prohibited = [f for f in active if f["tier"] == "prohibited"]
    high_risk = [f for f in active if f["tier"] == "high_risk"]
    limited = [f for f in active if f["tier"] == "limited_risk"]
    total_files = len(set(f["file"] for f in findings))

    # Overall status
    if prohibited:
        status_label = "Action Required — Prohibited Pattern"
        status_color = "#dc2626"
        status_bg = "#fef2f2"
    elif high_risk:
        status_label = "High-Risk Indicators Detected"
        status_color = "#d97706"
        status_bg = "#fffbeb"
    elif limited:
        status_label = "Limited-Risk — Transparency Obligations Apply"
        status_color = "#2563eb"
        status_bg = "#eff6ff"
    else:
        status_label = "No High-Risk Indicators Found"
        status_color = "#16a34a"
        status_bg = "#f0fdf4"

    def _rows(items: list) -> str:
        if not items:
            return "<tr><td colspan='3' style='color:#6b7280;font-style:italic'>None detected</td></tr>"
        rows = []
        for f in items[:10]:  # cap at 10 rows
            cat = escape(f.get("category", f.get("tier", "")))
            art = ", ".join(f"Art. {a}" for a in f.get("articles", []))
            file_ = escape(f.get("file", ""))
            rows.append(f"<tr><td>{cat}</td><td>{art}</td><td style='font-family:monospace;font-size:0.8em'>{file_}</td></tr>")
        return "\n".join(rows)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>EU AI Act Compliance Summary — {escape(project_name)}</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;font-size:15px;color:#111;background:#f9fafb;padding:32px 16px}}
.card{{background:#fff;border:1px solid #e5e7eb;border-radius:8px;padding:28px;max-width:800px;margin:0 auto}}
h1{{font-size:1.3rem;font-weight:700;margin-bottom:4px}}
.sub{{color:#6b7280;font-size:0.9rem;margin-bottom:24px}}
.status{{padding:16px 20px;border-radius:6px;background:{status_bg};border-left:4px solid {status_color};margin-bottom:24px}}
.status-label{{font-weight:700;color:{status_color};font-size:1rem}}
.grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:24px}}
.stat{{background:#f9fafb;border:1px solid #e5e7eb;border-radius:6px;padding:14px;text-align:center}}
.stat-n{{font-size:1.8rem;font-weight:800;line-height:1}}
.stat-l{{font-size:0.75rem;color:#6b7280;margin-top:4px}}
h2{{font-size:1rem;font-weight:600;margin:20px 0 10px}}
table{{width:100%;border-collapse:collapse;font-size:0.85rem}}
th{{text-align:left;padding:8px 10px;background:#f3f4f6;border-bottom:1px solid #e5e7eb;font-weight:600}}
td{{padding:8px 10px;border-bottom:1px solid #f3f4f6;vertical-align:top}}
.footer{{margin-top:28px;padding-top:16px;border-top:1px solid #e5e7eb;font-size:0.8rem;color:#9ca3af}}
</style>
</head>
<body>
<div class="card">
  <h1>EU AI Act Compliance Summary</h1>
  <div class="sub">{escape(project_name)} &nbsp;·&nbsp; Scanned {now} &nbsp;·&nbsp; {total_files} files</div>

  <div class="status">
    <div class="status-label">{status_label}</div>
    <div style="margin-top:6px;font-size:0.875rem;color:#374151">
      Pattern-based risk indication. Findings are indicators for human review,
      not legal determinations. Full report available on request.
    </div>
  </div>

  <div class="grid">
    <div class="stat">
      <div class="stat-n" style="color:#dc2626">{len(prohibited)}</div>
      <div class="stat-l">Prohibited<br>indicators</div>
    </div>
    <div class="stat">
      <div class="stat-n" style="color:#d97706">{len(high_risk)}</div>
      <div class="stat-l">High-risk<br>indicators</div>
    </div>
    <div class="stat">
      <div class="stat-n" style="color:#2563eb">{len(limited)}</div>
      <div class="stat-l">Limited-risk<br>indicators</div>
    </div>
    <div class="stat">
      <div class="stat-n" style="color:#374151">{total_files}</div>
      <div class="stat-l">Files<br>scanned</div>
    </div>
  </div>

  <h2>High-Risk Indicators (Annex III)</h2>
  <table>
    <thead><tr><th>Category</th><th>Articles</th><th>File</th></tr></thead>
    <tbody>{_rows(high_risk)}</tbody>
  </table>

  <h2>Prohibited Practice Indicators (Article 5)</h2>
  <table>
    <thead><tr><th>Category</th><th>Article</th><th>File</th></tr></thead>
    <tbody>{_rows(prohibited)}</tbody>
  </table>

  <div class="footer">
    Generated by <strong>Regula</strong> (github.com/kuzivaai/getregula) &nbsp;·&nbsp;
    EU AI Act pattern-based risk indication &nbsp;·&nbsp;
    This summary does not constitute legal advice. For full compliance
    assessment, consult qualified legal counsel.
  </div>
</div>
</body>
</html>"""
    return html


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Generate Regula reports")
    parser.add_argument("--project", "-p", default=".", help="Project to scan")
    parser.add_argument("--format", "-f", choices=["html", "sarif", "json", "sales"], default="html")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--name", "-n", help="Project name")
    parser.add_argument("--include-audit", action="store_true", help="Include audit trail data")
    args = parser.parse_args()

    project_path = str(Path(args.project).resolve())
    project_name = args.name or Path(project_path).name

    print(f"Scanning {project_path}...", file=sys.stderr)
    findings = scan_files(project_path)
    print(f"Found {len(findings)} findings in {len(set(f['file'] for f in findings))} files", file=sys.stderr)

    # Optionally include audit data
    audit_events = None
    chain_valid = None
    if args.include_audit:
        try:
            audit_events = query_events(limit=10000)
            chain_valid, _ = verify_chain()
        except (OSError, ValueError, KeyError):
            pass

    if args.format == "html":
        content = generate_html_report(findings, project_name, audit_events, chain_valid)
        suffix = ".html"
    elif args.format == "sarif":
        content = json.dumps(generate_sarif(findings, project_name), indent=2)
        suffix = ".sarif.json"
    else:
        content = json.dumps(findings, indent=2)
        suffix = ".json"

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(content, encoding="utf-8")
        print(f"Report written to {out_path}", file=sys.stderr)
    else:
        print(content)


if __name__ == "__main__":
    main()
