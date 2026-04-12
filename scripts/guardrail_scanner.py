#!/usr/bin/env python3
# regula-ignore
"""
Regula Guardrail Scanner — Runtime AI Guardrail Detection

Scans a codebase for runtime guardrail implementations covering:
- Input validation (Art 15.4 — robustness)
- Output filtering (Art 15.3/10 — accuracy, data quality)
- Execution controls (Art 14 — human oversight)
- Monitoring & audit (Art 12/13 — record-keeping, transparency)
- Known guardrail libraries

No external dependencies — stdlib only.
"""

import os
import re
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent))

from constants import CODE_EXTENSIONS, SKIP_DIRS


# ---------------------------------------------------------------------------
# Guardrail pattern definitions
# ---------------------------------------------------------------------------

GUARDRAIL_CATEGORIES = {
    "input_validation": {
        "article_ref": "Art 15.4",
        "description": "Input validation and robustness against errors/faults",
        "patterns": {
            "prompt_injection_defence": [
                r"prompt.?injection", r"injection.?detect", r"injection.?filter",
                r"llm.?as.?judge", r"semantic.?check", r"input.?guard",
                r"canary.?token", r"delimiter.?check",
            ],
            "input_length_limit": [
                r"max.?tokens", r"max.?length", r"token.?limit",
                r"len\s*\(\s*(?:prompt|input|query|message)", r"truncat",
                r"MAX_INPUT", r"input.?size.?limit",
            ],
            "input_sanitisation": [
                r"sanitiz", r"sanitise", r"strip.?html", r"escape.?special",
                r"bleach\.clean", r"html\.escape", r"markupsafe",
                r"input.?clean", r"normalize.?input",
            ],
            "pii_detection": [
                r"pii.?detect", r"pii.?redact", r"presidio",
                r"anonymi[sz]", r"redact.?(?:email|phone|ssn|name)",
                r"personal.?data.?filter", r"data.?masking",
            ],
            "content_allowlist_blocklist": [
                r"(?:allow|block|deny|ban).?list", r"(?:white|black).?list",
                r"forbidden.?(?:words|terms|topics)", r"content.?filter.?(?:input|request)",
                r"topic.?restrict", r"keyword.?filter",
            ],
            "rate_limiting": [
                r"rate.?limit", r"throttl", r"requests?.?per.?(?:second|minute|hour)",
                r"token.?bucket", r"leaky.?bucket", r"sliding.?window.?rate",
                r"slowapi", r"ratelimit",
            ],
        },
        "gap_messages": {
            "prompt_injection_defence": "No prompt injection defences detected",
            "input_length_limit": "No input length/token limits found",
            "input_sanitisation": "No input sanitisation detected",
            "pii_detection": "No PII detection or redaction found",
            "content_allowlist_blocklist": "No content allow/blocklists found",
            "rate_limiting": "No rate limiting on input endpoints detected",
        },
    },
    "output_filtering": {
        "article_ref": "Art 15.3, Art 10",
        "description": "Output filtering for accuracy and data quality",
        "patterns": {
            "toxicity_filtering": [
                r"detoxify", r"perspective.?api", r"toxicity.?(?:score|filter|check|detect)",
                r"nsfw.?(?:filter|detect|check)", r"content.?moderat",
                r"harmful.?content", r"safety.?filter",
            ],
            "hallucination_detection": [
                r"hallucination.?(?:detect|check|score)", r"fact.?check",
                r"ground(?:ing|ed).?(?:check|verif)", r"retrieval.?verif",
                r"citation.?verif", r"faithfulness.?(?:score|check)",
                r"source.?attribution",
            ],
            "output_pii_scrubbing": [
                r"(?:output|response).?(?:pii|redact|scrub|sanitiz)",
                r"scrub.?(?:pii|personal)", r"mask.?(?:output|response)",
            ],
            "output_format_validation": [
                r"json.?schema.?valid", r"structured.?output",
                r"output.?schema", r"response.?format.?valid",
                r"pydantic.?(?:model|BaseModel)", r"jsonschema\.validate",
                r"output.?pars(?:e|ing).?valid",
            ],
            "confidence_threshold": [
                r"confidence.?(?:threshold|score|check)", r"abstain",
                r"uncertain(?:ty)?.?threshold", r"(?:low|min).?confidence",
                r"refuse.?to.?answer", r"idk.?response",
            ],
            "response_length_limit": [
                r"max.?(?:output|response).?(?:length|tokens|chars)",
                r"truncat.?(?:output|response)", r"response.?size.?limit",
                r"MAX_OUTPUT", r"max.?completion.?tokens",
            ],
        },
        "gap_messages": {
            "toxicity_filtering": "No toxicity/content filtering detected",
            "hallucination_detection": "No hallucination detection found",
            "output_pii_scrubbing": "No output PII scrubbing found",
            "output_format_validation": "No output format validation detected",
            "confidence_threshold": "No confidence thresholds or abstention logic found",
            "response_length_limit": "No response length limits found",
        },
    },
    "execution_controls": {
        "article_ref": "Art 14",
        "description": "Execution controls for human oversight",
        "patterns": {
            "human_in_the_loop": [
                r"human.?in.?the.?loop", r"human.?(?:approval|review|confirm)",
                r"manual.?(?:approval|review|confirm)", r"approval.?gate",
                r"requires?.?(?:human|manual).?(?:approval|review)",
                r"pending.?(?:approval|review)",
            ],
            "tool_call_restrictions": [
                r"(?:tool|function).?(?:allow|white|permit).?list",
                r"allowed.?(?:tools|functions)", r"tool.?restrict",
                r"function.?(?:call|calling).?(?:restrict|limit|filter)",
                r"tool.?(?:guard|gate|policy)",
            ],
            "resource_limits": [
                r"(?:memory|cpu|cost|budget).?limit", r"token.?budget",
                r"max.?(?:cost|spend|budget)", r"resource.?(?:limit|quota)",
                r"usage.?(?:limit|cap|ceiling)",
            ],
            "timeout_enforcement": [
                r"timeout", r"deadline", r"time.?limit",
                r"max.?(?:duration|wait|execution.?time)",
                r"asyncio\.wait_for", r"signal\.alarm",
            ],
            "retry_limits": [
                r"max.?retries", r"retry.?limit", r"backoff",
                r"tenacity", r"retry.?count", r"exponential.?backoff",
                r"max.?attempts",
            ],
            "sandboxed_execution": [
                r"sandbox", r"gvisor", r"nsjail", r"firejail",
                r"docker.?(?:run|exec|container)", r"isolated.?(?:env|execution)",
                r"seccomp", r"AppArmor",
            ],
        },
        "gap_messages": {
            "human_in_the_loop": "No human-in-the-loop approval gates detected",
            "tool_call_restrictions": "No tool/function call restrictions found",
            "resource_limits": "No resource limits (memory, CPU, cost, token budgets) found",
            "timeout_enforcement": "No timeout enforcement detected",
            "retry_limits": "No retry limits with backoff found",
            "sandboxed_execution": "No sandboxed execution (Docker, gVisor, nsjail) detected",
        },
    },
    "monitoring_audit": {
        "article_ref": "Art 12, Art 13",
        "description": "Monitoring and audit for record-keeping and transparency",
        "patterns": {
            "io_logging": [
                r"(?:input|output|request|response).?log",
                r"log\.(?:info|debug|warning)\s*\(.*(?:input|output|request|response)",
                r"audit.?log", r"conversation.?log", r"interaction.?log",
                r"logger\.(?:info|debug)", r"logging\.getLogger",
            ],
            "error_tracking": [
                r"sentry", r"bugsnag", r"rollbar", r"airbrake",
                r"exception.?(?:track|report|log|handler)",
                r"error.?(?:track|report|handler)",
                r"sys\.excepthook",
            ],
            "usage_metrics": [
                r"(?:usage|telemetry|metric).?(?:collect|track|record|send)",
                r"prometheus", r"statsd", r"datadog", r"opentelemetry",
                r"metric\.(?:inc|observe|record)", r"counter\.(?:inc|add)",
            ],
            "audit_trail": [
                r"audit.?trail", r"audit.?(?:record|entry|event)",
                r"immutable.?log", r"tamper.?(?:proof|evident)",
                r"event.?sourc", r"append.?only.?log",
            ],
            "model_monitoring": [
                r"model.?(?:monitor|performance|metric|drift)",
                r"prediction.?(?:monitor|track|log)",
                r"(?:accuracy|latency|throughput).?(?:monitor|track|metric)",
                r"mlflow", r"wandb", r"weights.?(?:and|&).?biases",
            ],
            "drift_detection": [
                r"drift.?detect", r"data.?drift", r"concept.?drift",
                r"distribution.?shift", r"feature.?drift",
                r"evidently", r"deepchecks", r"alibi.?detect",
            ],
        },
        "gap_messages": {
            "io_logging": "No input/output logging detected",
            "error_tracking": "No error and exception tracking found",
            "usage_metrics": "No usage metrics collection detected",
            "audit_trail": "No audit trail generation found",
            "model_monitoring": "No model performance monitoring detected",
            "drift_detection": "No drift detection found",
        },
    },
}

# Known guardrail libraries: (import_pattern, display_name, type)
KNOWN_LIBRARIES = [
    (r"nemoguardrails|nemo_guardrails|from\s+nemoguardrails", "NeMo Guardrails (NVIDIA)", "open-source"),
    (r"guardrails\.guard|from\s+guardrails\s+import|import\s+guardrails", "Guardrails AI", "open-source"),
    (r"llm_guard|from\s+llm_guard|import\s+llm_guard", "LLM Guard (Protect AI)", "open-source"),
    (r"lakera|lakera_guard|from\s+lakera", "Lakera Guard", "commercial"),
    (r"rebuff|from\s+rebuff|import\s+rebuff", "Rebuff", "open-source"),
    (r"whylabs|whylogs|from\s+whylabs|from\s+whylogs", "WhyLabs", "open-source"),
    (r"fiddler|from\s+fiddler|import\s+fiddler", "Fiddler", "commercial"),
    (r"presidio(?:_analyzer|_anonymizer)?|from\s+presidio", "Presidio (Microsoft)", "open-source"),
]

# Map libraries to categories they contribute to
LIBRARY_CATEGORY_MAP = {
    "NeMo Guardrails (NVIDIA)": ["input_validation", "output_filtering"],
    "Guardrails AI": ["input_validation", "output_filtering"],
    "LLM Guard (Protect AI)": ["input_validation", "output_filtering"],
    "Lakera Guard": ["input_validation"],
    "Rebuff": ["input_validation"],
    "WhyLabs": ["monitoring_audit"],
    "Fiddler": ["monitoring_audit"],
    "Presidio (Microsoft)": ["input_validation"],
}


# ---------------------------------------------------------------------------
# File discovery
# ---------------------------------------------------------------------------

def _walk_project(project_path: str):
    """Yield (relative_path, absolute_path) for scannable code files."""
    project = Path(project_path).resolve()
    for root, dirs, files in os.walk(project):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for filename in files:
            filepath = Path(root) / filename
            if filepath.suffix.lower() in CODE_EXTENSIONS:
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


# ---------------------------------------------------------------------------
# Core scanning
# ---------------------------------------------------------------------------

def _scan_file_for_patterns(content: str, patterns: list) -> list:
    """Return list of matched pattern strings (case-insensitive)."""
    matched = []
    for pattern in patterns:
        if re.search(pattern, content, re.IGNORECASE):
            matched.append(pattern)
    return matched


def _find_line_number(content: str, pattern: str) -> int:
    """Find the first line number where pattern matches."""
    for i, line in enumerate(content.split("\n"), 1):
        if re.search(pattern, line, re.IGNORECASE):
            return i
    return 0


def scan_for_guardrails(project_path: str) -> dict:
    """Scan codebase for guardrail implementation.

    Returns structured result with per-category scores, detected patterns,
    gaps, library detections, overall score, and recommendations.
    """
    project_path = str(Path(project_path).resolve())
    files_index = list(_walk_project(project_path))

    # Read all file contents once
    file_contents = {}
    for rel_path, abs_path in files_index:
        content = _read_file(abs_path)
        if content:
            file_contents[rel_path] = content

    # Detect known libraries
    libraries_detected = []
    library_names_found = set()
    for rel_path, content in file_contents.items():
        for lib_pattern, lib_name, lib_type in KNOWN_LIBRARIES:
            if lib_name not in library_names_found:
                if re.search(lib_pattern, content, re.IGNORECASE):
                    libraries_detected.append({
                        "name": lib_name,
                        "file": rel_path,
                        "type": lib_type,
                    })
                    library_names_found.add(lib_name)

    # Determine which categories get library bonus
    library_category_bonus = set()
    for lib in libraries_detected:
        for cat in LIBRARY_CATEGORY_MAP.get(lib["name"], []):
            library_category_bonus.add(cat)

    # Scan each category
    categories = {}
    for cat_key, cat_def in GUARDRAIL_CATEGORIES.items():
        detected = []
        patterns_matched = set()

        for sub_key, sub_patterns in cat_def["patterns"].items():
            for rel_path, content in file_contents.items():
                matches = _scan_file_for_patterns(content, sub_patterns)
                if matches:
                    patterns_matched.add(sub_key)
                    for m in matches:
                        line = _find_line_number(content, m)
                        detected.append({
                            "pattern": sub_key,
                            "file": rel_path,
                            "line": line,
                            "confidence": "high" if sub_key in (
                                "pii_detection", "toxicity_filtering",
                                "human_in_the_loop", "io_logging",
                            ) else "medium",
                            "match": m,
                        })

        # Deduplicate: keep first detection per (pattern, file)
        seen = set()
        unique_detected = []
        for d in detected:
            key = (d["pattern"], d["file"])
            if key not in seen:
                seen.add(key)
                unique_detected.append(d)
        detected = unique_detected

        # Scoring: library=10, code patterns=5 each (cap 15), total cap 20
        library_score = 10 if cat_key in library_category_bonus else 0
        pattern_score = min(15, len(patterns_matched) * 5)
        score = min(20, library_score + pattern_score)

        # Gaps
        gaps = []
        for sub_key, gap_msg in cat_def["gap_messages"].items():
            if sub_key not in patterns_matched:
                gaps.append(gap_msg)

        categories[cat_key] = {
            "score": score,
            "detected": detected,
            "gaps": gaps,
            "article_ref": cat_def["article_ref"],
            "description": cat_def["description"],
        }

    # Overall score — normalise from 0-80 raw to 0-100 percentage
    max_raw = len(GUARDRAIL_CATEGORIES) * 20  # 4 categories * 20 max each
    raw_score = sum(c["score"] for c in categories.values())
    overall_score = round(raw_score * 100 / max_raw)

    # Recommendations
    recommendations = _generate_recommendations(categories, library_names_found)

    return {
        "categories": categories,
        "libraries_detected": libraries_detected,
        "overall_score": overall_score,
        "recommendations": recommendations,
    }


def _generate_recommendations(categories: dict, libraries_found: set) -> list:
    """Generate prioritised recommendations based on gaps."""
    recs = []

    # P0: Critical gaps
    if categories["input_validation"]["score"] < 5:
        recs.append({
            "priority": "P0",
            "action": "Add input validation guardrails. Install: pip install guardrails-ai",
            "article": "Art 15.4",
        })
    if categories["monitoring_audit"]["score"] < 5:
        recs.append({
            "priority": "P0",
            "action": "Add logging and audit trail. EU AI Act Art 12 requires record-keeping for high-risk systems",
            "article": "Art 12",
        })
    if categories["execution_controls"]["score"] < 5:
        recs.append({
            "priority": "P0",
            "action": "Add human oversight controls. EU AI Act Art 14 requires human-in-the-loop for high-risk systems",
            "article": "Art 14",
        })

    # P1: Important gaps
    if categories["output_filtering"]["score"] < 10:
        recs.append({
            "priority": "P1",
            "action": "Add output filtering. Install: pip install detoxify (toxicity) or guardrails-ai (structured output)",
            "article": "Art 15.3",
        })
    pii_covered = any(
        d["pattern"] == "pii_detection"
        for d in categories["input_validation"]["detected"]
    )
    if not pii_covered:
        recs.append({
            "priority": "P1",
            "action": "Add PII detection/redaction. Install: pip install presidio-analyzer presidio-anonymizer",
            "article": "Art 15.4",
        })
    if "WhyLabs" not in libraries_found and \
       categories["monitoring_audit"]["score"] < 15:
        drift_found = any(
            d["pattern"] == "drift_detection"
            for d in categories["monitoring_audit"]["detected"]
        )
        if not drift_found:
            recs.append({
                "priority": "P1",
                "action": "Add drift detection. Install: pip install evidently (open-source)",
                "article": "Art 12",
            })

    # P2: Nice-to-haves
    if "NeMo Guardrails (NVIDIA)" not in libraries_found and \
       "Guardrails AI" not in libraries_found and \
       "LLM Guard (Protect AI)" not in libraries_found:
        recs.append({
            "priority": "P2",
            "action": "Consider a guardrail framework: NeMo Guardrails (pip install nemoguardrails), Guardrails AI (pip install guardrails-ai), or LLM Guard (pip install llm-guard)",
            "article": "Art 15",
        })
    sandbox_found = any(
        d["pattern"] == "sandboxed_execution"
        for d in categories["execution_controls"]["detected"]
    )
    if not sandbox_found:
        recs.append({
            "priority": "P2",
            "action": "Consider sandboxed execution for agent tool calls (Docker, gVisor, nsjail)",
            "article": "Art 14",
        })

    # Sort by priority
    priority_order = {"P0": 0, "P1": 1, "P2": 2}
    recs.sort(key=lambda r: priority_order.get(r["priority"], 99))
    return recs


# ---------------------------------------------------------------------------
# Text formatting
# ---------------------------------------------------------------------------

def _bar(score: int, max_score: int, width: int = 20) -> str:
    """Create a text-based progress bar."""
    filled = int(width * score / max_score) if max_score > 0 else 0
    return "\u2588" * filled + "\u2591" * (width - filled)


def _colour_score(score: int) -> str:
    """Return ANSI-coloured score string."""
    if score >= 80:
        return f"\033[92m{score}/100\033[0m"  # green
    elif score >= 50:
        return f"\033[93m{score}/100\033[0m"  # yellow
    elif score >= 25:
        return f"\033[33m{score}/100\033[0m"  # orange
    else:
        return f"\033[91m{score}/100\033[0m"  # red


def format_guardrails_text(result: dict) -> str:
    """Format guardrail scan results as human-readable text."""
    lines = []
    score = result["overall_score"]

    # Header
    lines.append("")
    lines.append(f"  Guardrail Coverage: {_colour_score(score)}")
    lines.append("")

    # Category breakdown
    cat_display = {
        "input_validation": "Input Validation",
        "output_filtering": "Output Filtering",
        "execution_controls": "Execution Controls",
        "monitoring_audit": "Monitoring & Audit",
    }

    for cat_key, display_name in cat_display.items():
        cat = result["categories"][cat_key]
        pct = int(cat["score"] / 20 * 100)
        bar = _bar(cat["score"], 20)
        ref = cat["article_ref"]
        lines.append(f"  {display_name:<20s} {bar}  {pct:>3d}%  ({ref})")

    # Libraries
    lines.append("")
    if result["libraries_detected"]:
        lines.append("  Libraries detected:")
        for lib in result["libraries_detected"]:
            marker = "\u2713" if lib["type"] == "open-source" else "\u25cf"
            lines.append(f"    {marker} {lib['name']} [{lib['type']}] in {lib['file']}")
    else:
        lines.append("  Libraries detected: none")

    # Gaps by category
    lines.append("")
    lines.append("  Gaps:")
    any_gaps = False
    for cat_key, display_name in cat_display.items():
        cat = result["categories"][cat_key]
        if cat["gaps"]:
            any_gaps = True
            for gap in cat["gaps"]:
                lines.append(f"    \u2717 {gap} ({cat['article_ref']})")
    if not any_gaps:
        lines.append("    None — all categories covered")

    # Recommendations
    if result["recommendations"]:
        lines.append("")
        lines.append("  Recommendations:")
        for rec in result["recommendations"]:
            lines.append(f"    [{rec['priority']}] {rec['action']} ({rec['article']})")

    lines.append("")
    return "\n".join(lines)
