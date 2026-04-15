#!/usr/bin/env python3
# regula-ignore
"""Tests for guardrail_scanner module."""

import os
import sys
import tempfile
import shutil
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from guardrail_scanner import scan_for_guardrails, format_guardrails_text
from constants import CODE_EXTENSIONS

import helpers
from helpers import assert_eq, assert_true, assert_in, assert_gte, assert_lte


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_project(files: dict) -> str:
    """Create a temp project directory with given files. Returns path."""
    tmpdir = tempfile.mkdtemp(prefix="regula_test_guardrails_")
    for name, content in files.items():
        filepath = Path(tmpdir) / name
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_text(content)
    return tmpdir


def _cleanup(path: str):
    shutil.rmtree(path, ignore_errors=True)


# ---------------------------------------------------------------------------
# Tests: Empty project
# ---------------------------------------------------------------------------

def test_empty_project():
    proj = _make_project({})
    try:
        result = scan_for_guardrails(proj)
        assert_eq(result["overall_score"], 0, "empty project score=0")
        for cat_key, cat in result["categories"].items():
            assert_eq(cat["score"], 0, f"empty {cat_key} score=0")
            assert_true(len(cat["gaps"]) > 0, f"empty {cat_key} has gaps")
            assert_eq(cat["detected"], [], f"empty {cat_key} no detections")
        assert_eq(result["libraries_detected"], [], "empty: no libraries")
        assert_true(len(result["recommendations"]) > 0, "empty: has recommendations")
    finally:
        _cleanup(proj)


# ---------------------------------------------------------------------------
# Tests: Library detection
# ---------------------------------------------------------------------------

def test_detect_nemo_guardrails():
    proj = _make_project({"app.py": "from nemoguardrails import RailsConfig\n"})
    try:
        result = scan_for_guardrails(proj)
        lib_names = [l["name"] for l in result["libraries_detected"]]
        assert_in("NeMo Guardrails (NVIDIA)", lib_names, "detect NeMo")
        assert_eq(result["libraries_detected"][0]["type"], "open-source", "NeMo is open-source")
    finally:
        _cleanup(proj)


def test_detect_guardrails_ai():
    proj = _make_project({"guard.py": "from guardrails import Guard\n"})
    try:
        result = scan_for_guardrails(proj)
        lib_names = [l["name"] for l in result["libraries_detected"]]
        assert_in("Guardrails AI", lib_names, "detect Guardrails AI")
    finally:
        _cleanup(proj)


def test_detect_llm_guard():
    proj = _make_project({"scan.py": "from llm_guard import scan_prompt\n"})
    try:
        result = scan_for_guardrails(proj)
        lib_names = [l["name"] for l in result["libraries_detected"]]
        assert_in("LLM Guard (Protect AI)", lib_names, "detect LLM Guard")
    finally:
        _cleanup(proj)


def test_detect_lakera():
    proj = _make_project({"sec.py": "import lakera_guard\n"})
    try:
        result = scan_for_guardrails(proj)
        lib_names = [l["name"] for l in result["libraries_detected"]]
        assert_in("Lakera Guard", lib_names, "detect Lakera")
        assert_eq(result["libraries_detected"][0]["type"], "commercial", "Lakera is commercial")
    finally:
        _cleanup(proj)


def test_detect_presidio():
    proj = _make_project({"pii.py": "from presidio_analyzer import AnalyzerEngine\n"})
    try:
        result = scan_for_guardrails(proj)
        lib_names = [l["name"] for l in result["libraries_detected"]]
        assert_in("Presidio (Microsoft)", lib_names, "detect Presidio")
    finally:
        _cleanup(proj)


def test_detect_whylabs():
    proj = _make_project({"monitor.py": "import whylogs\n"})
    try:
        result = scan_for_guardrails(proj)
        lib_names = [l["name"] for l in result["libraries_detected"]]
        assert_in("WhyLabs", lib_names, "detect WhyLabs")
    finally:
        _cleanup(proj)


def test_detect_rebuff():
    proj = _make_project({"defend.py": "from rebuff import Rebuff\n"})
    try:
        result = scan_for_guardrails(proj)
        lib_names = [l["name"] for l in result["libraries_detected"]]
        assert_in("Rebuff", lib_names, "detect Rebuff")
    finally:
        _cleanup(proj)


def test_detect_fiddler():
    proj = _make_project({"observe.py": "import fiddler\n"})
    try:
        result = scan_for_guardrails(proj)
        lib_names = [l["name"] for l in result["libraries_detected"]]
        assert_in("Fiddler", lib_names, "detect Fiddler")
        assert_eq(result["libraries_detected"][0]["type"], "commercial", "Fiddler is commercial")
    finally:
        _cleanup(proj)


# ---------------------------------------------------------------------------
# Tests: Code pattern detection per category
# ---------------------------------------------------------------------------

def test_input_validation_patterns():
    proj = _make_project({"validate.py": """
if len(prompt) > MAX_TOKENS:
    raise ValueError("Input too long")

def sanitize_input(text):
    return html.escape(text)

# rate limiting
from slowapi import Limiter
"""})
    try:
        result = scan_for_guardrails(proj)
        cat = result["categories"]["input_validation"]
        assert_true(cat["score"] > 0, "input_validation score > 0")
        patterns_found = {d["pattern"] for d in cat["detected"]}
        assert_in("input_length_limit", patterns_found, "detect input length limit")
        assert_in("input_sanitisation", patterns_found, "detect sanitisation")
        assert_in("rate_limiting", patterns_found, "detect rate limiting")
    finally:
        _cleanup(proj)


def test_output_filtering_patterns():
    proj = _make_project({"filter.py": """
from detoxify import Detoxify
toxicity_score = check_toxicity(response)

if confidence_threshold < 0.5:
    return "I'm not sure about that"

schema = jsonschema.validate(output, output_schema)
max_output_length = 4096
"""})
    try:
        result = scan_for_guardrails(proj)
        cat = result["categories"]["output_filtering"]
        assert_true(cat["score"] > 0, "output_filtering score > 0")
        patterns_found = {d["pattern"] for d in cat["detected"]}
        assert_in("toxicity_filtering", patterns_found, "detect toxicity filtering")
        assert_in("confidence_threshold", patterns_found, "detect confidence threshold")
        assert_in("output_format_validation", patterns_found, "detect output format validation")
    finally:
        _cleanup(proj)


def test_execution_controls_patterns():
    proj = _make_project({"controls.py": """
# Human approval gate
if not human_approval(action):
    raise PermissionError("Requires human approval")

allowed_tools = ["search", "calculator"]
timeout = 30
max_retries = 3
"""})
    try:
        result = scan_for_guardrails(proj)
        cat = result["categories"]["execution_controls"]
        assert_true(cat["score"] > 0, "execution_controls score > 0")
        patterns_found = {d["pattern"] for d in cat["detected"]}
        assert_in("timeout_enforcement", patterns_found, "detect timeout")
        assert_in("retry_limits", patterns_found, "detect retry limits")
    finally:
        _cleanup(proj)


def test_monitoring_audit_patterns():
    proj = _make_project({"monitor.py": """
import logging
logger = logging.getLogger(__name__)
logger.info("Request: %s", request_log)

# Sentry error tracking
import sentry_sdk

# Prometheus metrics
from prometheus_client import Counter
metric.inc()

# Audit trail
audit_trail.append({"action": action, "timestamp": ts})
"""})
    try:
        result = scan_for_guardrails(proj)
        cat = result["categories"]["monitoring_audit"]
        assert_true(cat["score"] > 0, "monitoring_audit score > 0")
        patterns_found = {d["pattern"] for d in cat["detected"]}
        assert_in("io_logging", patterns_found, "detect logging")
        assert_in("error_tracking", patterns_found, "detect error tracking")
        assert_in("usage_metrics", patterns_found, "detect metrics")
        assert_in("audit_trail", patterns_found, "detect audit trail")
    finally:
        _cleanup(proj)


# ---------------------------------------------------------------------------
# Tests: Scoring
# ---------------------------------------------------------------------------

def test_scoring_empty():
    proj = _make_project({})
    try:
        result = scan_for_guardrails(proj)
        assert_eq(result["overall_score"], 0, "empty score=0")
    finally:
        _cleanup(proj)


def test_scoring_category_cap():
    """Each category caps at 20 points."""
    proj = _make_project({"all.py": """
from nemoguardrails import RailsConfig
prompt_injection_defence = True
input_length_limit = True
sanitize(input)
pii_detect(input)
blocklist_check(input)
rate_limit(input)
"""})
    try:
        result = scan_for_guardrails(proj)
        cat = result["categories"]["input_validation"]
        assert_lte(cat["score"], 20, "category score capped at 20")
    finally:
        _cleanup(proj)


def test_scoring_library_bonus():
    """Library detection gives +10 to category score."""
    proj = _make_project({"app.py": "from nemoguardrails import RailsConfig\n"})
    try:
        result = scan_for_guardrails(proj)
        cat = result["categories"]["input_validation"]
        assert_gte(cat["score"], 10, "library gives at least 10 points")
    finally:
        _cleanup(proj)


def test_scoring_full_project():
    """A fully instrumented project should score high."""
    proj = _make_project({"full.py": """
# Input validation
from nemoguardrails import RailsConfig
prompt_injection_filter(input)
if len(prompt) > max_tokens: pass
sanitize_input(text)
pii_detection(text)
blocklist = ["bad"]
rate_limit()

# Output filtering
from guardrails import Guard
toxicity_score = detoxify(output)
hallucination_check(output)
output_pii_redact(response)
json_schema_valid = jsonschema.validate(output, schema)
confidence_threshold = 0.7
max_output_length = 4096

# Execution controls
human_in_the_loop = True
allowed_tools = ["search"]
token_budget = 1000
timeout = 30
max_retries = 3
sandbox_execution()

# Monitoring
import logging
logger = logging.getLogger(__name__)
import sentry_sdk
from prometheus_client import Counter
audit_trail = []
model_monitoring()
drift_detection()
"""})
    try:
        result = scan_for_guardrails(proj)
        assert_gte(result["overall_score"], 80, "full project score >= 80")
    finally:
        _cleanup(proj)


def test_scoring_mixed_project():
    """A project with some categories covered scores partially."""
    proj = _make_project({"partial.py": """
import logging
logger = logging.getLogger(__name__)
import sentry_sdk
timeout = 30
max_retries = 3
"""})
    try:
        result = scan_for_guardrails(proj)
        assert_true(0 < result["overall_score"] < 100, "mixed project partial score")
        # Monitoring should have some score
        assert_true(result["categories"]["monitoring_audit"]["score"] > 0, "monitoring has score")
        # Input validation should be 0
        assert_eq(result["categories"]["input_validation"]["score"], 0, "input_validation=0 in partial")
    finally:
        _cleanup(proj)


# ---------------------------------------------------------------------------
# Tests: Recommendations
# ---------------------------------------------------------------------------

def test_recommendations_priority_ordering():
    proj = _make_project({})
    try:
        result = scan_for_guardrails(proj)
        recs = result["recommendations"]
        assert_true(len(recs) > 0, "empty project has recommendations")
        # Check P0 comes before P1 which comes before P2
        priorities = [r["priority"] for r in recs]
        p0_indices = [i for i, p in enumerate(priorities) if p == "P0"]
        p1_indices = [i for i, p in enumerate(priorities) if p == "P1"]
        p2_indices = [i for i, p in enumerate(priorities) if p == "P2"]
        if p0_indices and p1_indices:
            assert_true(max(p0_indices) < min(p1_indices), "P0 before P1")
        if p1_indices and p2_indices:
            assert_true(max(p1_indices) < min(p2_indices), "P1 before P2")
    finally:
        _cleanup(proj)


def test_recommendations_have_articles():
    proj = _make_project({})
    try:
        result = scan_for_guardrails(proj)
        for rec in result["recommendations"]:
            assert_true("article" in rec, "recommendation has article field")
            assert_true(rec["article"].startswith("Art"), f"article ref: {rec['article']}")
    finally:
        _cleanup(proj)


# ---------------------------------------------------------------------------
# Tests: Text formatting
# ---------------------------------------------------------------------------

def test_format_text_output():
    proj = _make_project({})
    try:
        result = scan_for_guardrails(proj)
        text = format_guardrails_text(result)
        assert_true("Guardrail Coverage" in text, "header present")
        assert_true("Input Validation" in text, "input validation label")
        assert_true("Output Filtering" in text, "output filtering label")
        assert_true("Execution Controls" in text, "execution controls label")
        assert_true("Monitoring & Audit" in text, "monitoring audit label")
        assert_true("Gaps:" in text, "gaps section")
        assert_true("Recommendations:" in text, "recommendations section")
    finally:
        _cleanup(proj)


def test_format_text_with_libraries():
    proj = _make_project({"app.py": "from nemoguardrails import RailsConfig\n"})
    try:
        result = scan_for_guardrails(proj)
        text = format_guardrails_text(result)
        assert_true("NeMo Guardrails" in text, "library name in output")
        assert_true("open-source" in text, "library type in output")
    finally:
        _cleanup(proj)


# ---------------------------------------------------------------------------
# Tests: File extension filtering
# ---------------------------------------------------------------------------

def test_ignores_non_code_files():
    proj = _make_project({
        "readme.md": "prompt_injection_filter()",
        "app.py": "# nothing here",
    })
    try:
        result = scan_for_guardrails(proj)
        # .md is not in CODE_EXTENSIONS so patterns from readme.md should not be detected
        assert_eq(result["categories"]["input_validation"]["score"], 0,
                  "non-code files ignored")
    finally:
        _cleanup(proj)


def test_scans_js_files():
    proj = _make_project({"guard.js": """
const timeout = 30000;
const maxRetries = 3;
"""})
    try:
        result = scan_for_guardrails(proj)
        cat = result["categories"]["execution_controls"]
        assert_true(cat["score"] > 0, "JS files scanned")
    finally:
        _cleanup(proj)


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    test_funcs = [(name, obj) for name, obj in sorted(globals().items())
                  if name.startswith("test_") and callable(obj)]
    print(f"Running {len(test_funcs)} guardrail scanner tests...")
    for name, func in test_funcs:
        print(f"  {name}...", end=" ")
        try:
            func()
            print("ok")
        except Exception as e:
            helpers.failed += 1
            print(f"ERROR: {e}")
    print(f"\n{helpers.passed} passed, {helpers.failed} failed")
    sys.exit(1 if helpers.failed else 0)
