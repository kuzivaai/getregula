# regula-ignore
"""Tests for domain_scoring module — domain-aware confidence scoring."""
import sys
from pathlib import Path
from unittest.mock import patch

# Bare import convention: point at scripts/ directory
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from domain_scoring import (
    compute_domain_boost,
    DOMAIN_KEYWORDS,
    REGULATED_DOMAINS,
    INFORMATIONAL_DOMAINS,
    _DECISION_PATTERNS,
    _DOMAIN_COMPILED,
)


# ---------------------------------------------------------------------------
# Helper: patch get_declared_domain to return non-regulated by default,
# so keyword-detection logic is exercised (not short-circuited by policy).
# ---------------------------------------------------------------------------

def _no_policy():
    """Return a non-regulated domain so keyword detection runs."""
    return {"domain": "general_purpose", "risk_level": "", "name": "", "is_regulated": False}


# ===================================================================
# 1. compute_domain_boost — basic behaviour
# ===================================================================


@patch("domain_scoring.get_declared_domain", side_effect=_no_policy)
def test_no_ai_indicator_returns_zero_boost(_mock):
    """No AI indicator -> boost must be 0 regardless of domain keywords."""
    text = "This is a hiring and recruitment application for resume screening."
    result = compute_domain_boost(text, has_ai_indicator=False)
    assert result["boost"] == 0, f"Expected 0 boost without AI indicator, got {result['boost']}"
    assert result["domains_matched"] == []
    assert result["has_decision_logic"] is False
    assert result["detail"] == ""


@patch("domain_scoring.get_declared_domain", side_effect=_no_policy)
def test_ai_indicator_with_employment_keywords(_mock):
    """AI indicator + employment keywords -> non-zero boost."""
    text = "import sklearn\napplicant_score = model.predict(resume_data)"
    result = compute_domain_boost(text, has_ai_indicator=True)
    assert result["boost"] > 0, f"Expected positive boost, got {result['boost']}"
    assert "employment" in result["domains_matched"]


@patch("domain_scoring.get_declared_domain", side_effect=_no_policy)
def test_ai_indicator_with_finance_keywords(_mock):
    """AI indicator + finance keywords -> non-zero boost."""
    text = "import xgboost\ncredit_score = model.predict(applicant_data)\nloan default risk"
    result = compute_domain_boost(text, has_ai_indicator=True)
    assert result["boost"] > 0
    assert "finance" in result["domains_matched"]


@patch("domain_scoring.get_declared_domain", side_effect=_no_policy)
def test_ai_indicator_with_medical_keywords(_mock):
    """AI indicator + medical keywords -> non-zero boost."""
    text = "import tensorflow\npatient diagnosis clinical treatment triage"
    result = compute_domain_boost(text, has_ai_indicator=True)
    assert result["boost"] > 0
    assert "medical" in result["domains_matched"]


@patch("domain_scoring.get_declared_domain", side_effect=_no_policy)
def test_ai_indicator_with_education_keywords(_mock):
    """AI indicator + education keywords -> education boost (12)."""
    text = "import torch\nstudent admission exam grade university enrollment"
    result = compute_domain_boost(text, has_ai_indicator=True)
    assert result["boost"] > 0
    assert "education" in result["domains_matched"]
    # Education boost is 12, not 15
    cfg = DOMAIN_KEYWORDS["education"]
    assert cfg["boost"] == 12


@patch("domain_scoring.get_declared_domain", side_effect=_no_policy)
def test_ai_indicator_with_biometrics_keywords(_mock):
    """AI indicator + biometric keywords -> biometrics boost."""
    text = "import cv2\nbiometric facial recognition face recognition system"
    result = compute_domain_boost(text, has_ai_indicator=True)
    assert result["boost"] > 0
    assert "biometrics" in result["domains_matched"]


@patch("domain_scoring.get_declared_domain", side_effect=_no_policy)
def test_ai_indicator_with_law_enforcement_keywords(_mock):
    """AI indicator + law enforcement keywords -> boost."""
    text = "import sklearn\npolice criminal suspect surveillance investigation"
    result = compute_domain_boost(text, has_ai_indicator=True)
    assert result["boost"] > 0
    assert "law_enforcement" in result["domains_matched"]


@patch("domain_scoring.get_declared_domain", side_effect=_no_policy)
def test_ai_indicator_with_infrastructure_keywords(_mock):
    """AI indicator + infrastructure keywords -> infrastructure boost (12)."""
    text = "import tensorflow\nenergy grid water supply power plant scada"
    result = compute_domain_boost(text, has_ai_indicator=True)
    assert result["boost"] > 0
    assert "infrastructure" in result["domains_matched"]
    cfg = DOMAIN_KEYWORDS["infrastructure"]
    assert cfg["boost"] == 12


@patch("domain_scoring.get_declared_domain", side_effect=_no_policy)
def test_ai_indicator_with_migration_keywords(_mock):
    """AI indicator + migration keywords -> boost."""
    text = "import sklearn\nasylum visa border control immigration refugee"
    result = compute_domain_boost(text, has_ai_indicator=True)
    assert result["boost"] > 0
    assert "migration" in result["domains_matched"]


@patch("domain_scoring.get_declared_domain", side_effect=_no_policy)
def test_ai_indicator_no_domain_keywords(_mock):
    """AI indicator but no domain keywords -> 0 boost."""
    text = "import numpy\nx = np.array([1, 2, 3])\ny = x ** 2"
    result = compute_domain_boost(text, has_ai_indicator=True)
    assert result["boost"] == 0
    assert result["domains_matched"] == []


# ===================================================================
# 2. exclude_if patterns — employment suppression
# ===================================================================


@patch("domain_scoring.get_declared_domain", side_effect=_no_policy)
def test_exclude_import_threading_suppresses_employment(_mock):
    """import threading with employment keywords -> employment suppressed."""
    text = "import threading\nworker = threading.Thread(target=hire_candidates)"
    result = compute_domain_boost(text, has_ai_indicator=True)
    assert "employment" not in result["domains_matched"], \
        f"employment should be suppressed by 'import threading', got {result['domains_matched']}"


@patch("domain_scoring.get_declared_domain", side_effect=_no_policy)
def test_exclude_import_multiprocessing_suppresses_employment(_mock):
    """import multiprocessing with employment keywords -> employment suppressed."""
    text = "import multiprocessing\ndef hire_process(applicant):\n    pass"
    result = compute_domain_boost(text, has_ai_indicator=True)
    assert "employment" not in result["domains_matched"], \
        "employment should be suppressed by 'import multiprocessing'"


@patch("domain_scoring.get_declared_domain", side_effect=_no_policy)
def test_exclude_import_joblib_suppresses_employment(_mock):
    """import joblib with employment keywords -> employment suppressed."""
    text = "import joblib\ndef process_hiring_data(applicant_list):\n    pass"
    result = compute_domain_boost(text, has_ai_indicator=True)
    assert "employment" not in result["domains_matched"], \
        "employment should be suppressed by 'import joblib'"


@patch("domain_scoring.get_declared_domain", side_effect=_no_policy)
def test_exclude_concurrent_futures_suppresses_employment(_mock):
    """concurrent.futures reference with employment keywords -> employment suppressed."""
    text = "from concurrent.futures import ProcessPoolExecutor\ndef process_applicant_data():\n    pass"
    result = compute_domain_boost(text, has_ai_indicator=True)
    assert "employment" not in result["domains_matched"], \
        "employment should be suppressed by 'concurrent.futures'"


@patch("domain_scoring.get_declared_domain", side_effect=_no_policy)
def test_exclude_from_threading_suppresses_employment(_mock):
    """from threading import ... with hiring keywords -> employment suppressed."""
    text = "from threading import Thread\ndef hiring_pipeline():\n    pass"
    result = compute_domain_boost(text, has_ai_indicator=True)
    assert "employment" not in result["domains_matched"], \
        "employment should be suppressed by 'from threading'"


@patch("domain_scoring.get_declared_domain", side_effect=_no_policy)
def test_exclude_process_pool_executor_suppresses_employment(_mock):
    """ProcessPoolExecutor with hiring keywords -> employment suppressed."""
    text = "executor = ProcessPoolExecutor(max_workers=4)\ndef hire_batch(applicants):\n    pass"
    result = compute_domain_boost(text, has_ai_indicator=True)
    assert "employment" not in result["domains_matched"], \
        "employment should be suppressed by 'ProcessPoolExecutor'"


@patch("domain_scoring.get_declared_domain", side_effect=_no_policy)
def test_exclude_thread_pool_executor_suppresses_employment(_mock):
    """ThreadPoolExecutor with hiring keywords -> employment suppressed."""
    text = "pool = ThreadPoolExecutor()\ndef hire_candidate(resume):\n    pass"
    result = compute_domain_boost(text, has_ai_indicator=True)
    assert "employment" not in result["domains_matched"], \
        "employment should be suppressed by 'ThreadPoolExecutor'"


@patch("domain_scoring.get_declared_domain", side_effect=_no_policy)
def test_exclude_celery_suppresses_employment(_mock):
    """import celery with hiring keywords -> employment suppressed."""
    text = "import celery\ndef process_recruitment_batch(applicants):\n    pass"
    result = compute_domain_boost(text, has_ai_indicator=True)
    assert "employment" not in result["domains_matched"], \
        "employment should be suppressed by 'import celery'"


@patch("domain_scoring.get_declared_domain", side_effect=_no_policy)
def test_exclude_ray_suppresses_employment(_mock):
    """import ray with hiring keywords -> employment suppressed."""
    text = "import ray\ndef distribute_hiring_workload(applicant_queue):\n    pass"
    result = compute_domain_boost(text, has_ai_indicator=True)
    assert "employment" not in result["domains_matched"], \
        "employment should be suppressed by 'import ray'"


@patch("domain_scoring.get_declared_domain", side_effect=_no_policy)
def test_exclude_dask_suppresses_employment(_mock):
    """import dask with hiring keywords -> employment suppressed."""
    text = "import dask\ndef hiring_analytics(applicant_df):\n    pass"
    result = compute_domain_boost(text, has_ai_indicator=True)
    assert "employment" not in result["domains_matched"], \
        "employment should be suppressed by 'import dask'"


@patch("domain_scoring.get_declared_domain", side_effect=_no_policy)
def test_exclude_does_not_suppress_other_domains(_mock):
    """Compute excludes only suppress employment, not other domains like medical."""
    text = "import threading\npatient diagnosis clinical treatment"
    result = compute_domain_boost(text, has_ai_indicator=True)
    assert "medical" in result["domains_matched"], \
        "medical should NOT be suppressed by threading import"


@patch("domain_scoring.get_declared_domain", side_effect=_no_policy)
def test_genuine_employment_without_compute_not_suppressed(_mock):
    """Employment keywords WITHOUT compute imports -> employment IS matched."""
    text = "def score_applicant(resume):\n    return model.predict(hiring_features)"
    result = compute_domain_boost(text, has_ai_indicator=True)
    assert "employment" in result["domains_matched"], \
        "employment should match when no compute imports are present"


# ===================================================================
# 3. Decision logic detection
# ===================================================================


@patch("domain_scoring.get_declared_domain", side_effect=_no_policy)
def test_decision_logic_if_predict(_mock):
    """if ... predict pattern -> has_decision_logic = True."""
    text = "if model.predict(x) > 0.5:\n    hire(applicant)"
    result = compute_domain_boost(text, has_ai_indicator=True)
    assert result["has_decision_logic"] is True


@patch("domain_scoring.get_declared_domain", side_effect=_no_policy)
def test_decision_logic_if_score(_mock):
    """if ... score pattern -> has_decision_logic = True."""
    text = "if score > threshold:\n    approve(application)\nhiring model"
    result = compute_domain_boost(text, has_ai_indicator=True)
    assert result["has_decision_logic"] is True


@patch("domain_scoring.get_declared_domain", side_effect=_no_policy)
def test_decision_logic_reject_if(_mock):
    """reject ... if pattern -> has_decision_logic = True."""
    text = "reject applicant if score < 0.3\nloan application"
    result = compute_domain_boost(text, has_ai_indicator=True)
    assert result["has_decision_logic"] is True


@patch("domain_scoring.get_declared_domain", side_effect=_no_policy)
def test_decision_logic_approve_if(_mock):
    """approve ... if pattern -> has_decision_logic = True."""
    text = "approve loan if credit_score > 700\ncreditworthiness assessment"
    result = compute_domain_boost(text, has_ai_indicator=True)
    assert result["has_decision_logic"] is True


@patch("domain_scoring.get_declared_domain", side_effect=_no_policy)
def test_decision_logic_deny_if(_mock):
    """deny ... if pattern -> has_decision_logic = True."""
    text = "deny application if score below minimum\nloan default risk"
    result = compute_domain_boost(text, has_ai_indicator=True)
    assert result["has_decision_logic"] is True


@patch("domain_scoring.get_declared_domain", side_effect=_no_policy)
def test_no_decision_logic(_mock):
    """Plain code without decision patterns -> has_decision_logic = False."""
    text = "x = model.predict(data)\nresult = transform(x)\nhiring pipeline"
    result = compute_domain_boost(text, has_ai_indicator=True)
    assert result["has_decision_logic"] is False


@patch("domain_scoring.get_declared_domain", side_effect=_no_policy)
def test_decision_logic_adds_boost(_mock):
    """Domain keywords + decision logic -> boost is increased (capped at 20)."""
    # With decision logic
    text_with = "if model.predict(applicant_data) > 0.5:\n    hire(applicant)"
    result_with = compute_domain_boost(text_with, has_ai_indicator=True)

    # Without decision logic
    text_without = "result = model.predict(applicant_data)\nhire(applicant)"
    result_without = compute_domain_boost(text_without, has_ai_indicator=True)

    # Both should match employment
    assert "employment" in result_with["domains_matched"]
    assert "employment" in result_without["domains_matched"]

    # Decision logic should add boost
    assert result_with["boost"] > result_without["boost"], \
        f"Decision logic should increase boost: {result_with['boost']} vs {result_without['boost']}"


@patch("domain_scoring.get_declared_domain", side_effect=_no_policy)
def test_decision_logic_boost_capped_at_20(_mock):
    """Boost with decision logic must not exceed 20."""
    text = "if model.predict(x) > 0.5:\n    reject applicant if score < threshold\n" \
           "credit_score loan mortgage default_risk underwriting"
    result = compute_domain_boost(text, has_ai_indicator=True)
    assert result["boost"] <= 20, f"Boost should be capped at 20, got {result['boost']}"


# ===================================================================
# 4. Multiple domains matched
# ===================================================================


@patch("domain_scoring.get_declared_domain", side_effect=_no_policy)
def test_multiple_domains_matched(_mock):
    """Text with keywords from multiple domains -> all matched, max boost used."""
    text = ("import sklearn\nhiring applicant resume\n"
            "patient diagnosis clinical\n"
            "credit_score loan mortgage")
    result = compute_domain_boost(text, has_ai_indicator=True)
    assert len(result["domains_matched"]) >= 2, \
        f"Expected multiple domains matched, got {result['domains_matched']}"
    # Max boost from 15-boost domains
    assert result["boost"] == 15


@patch("domain_scoring.get_declared_domain", side_effect=_no_policy)
def test_multiple_domains_with_different_boosts(_mock):
    """Mix of 12-boost and 15-boost domains -> max wins."""
    # education=12, finance=15
    text = "student admission exam grade\ncredit_score loan default_risk"
    result = compute_domain_boost(text, has_ai_indicator=True)
    assert "education" in result["domains_matched"]
    assert "finance" in result["domains_matched"]
    assert result["boost"] == 15, f"Max boost should be 15, got {result['boost']}"


# ===================================================================
# 5. Return structure validation
# ===================================================================


@patch("domain_scoring.get_declared_domain", side_effect=_no_policy)
def test_return_structure_with_match(_mock):
    """Return dict has all required keys with correct types."""
    text = "hiring applicant resume interview"
    result = compute_domain_boost(text, has_ai_indicator=True)
    assert isinstance(result, dict)
    assert "boost" in result
    assert "domains_matched" in result
    assert "has_decision_logic" in result
    assert "detail" in result
    assert isinstance(result["boost"], int)
    assert isinstance(result["domains_matched"], list)
    assert isinstance(result["has_decision_logic"], bool)
    assert isinstance(result["detail"], str)


@patch("domain_scoring.get_declared_domain", side_effect=_no_policy)
def test_return_structure_no_match(_mock):
    """Zero-match result still has all keys."""
    result = compute_domain_boost("x = 1", has_ai_indicator=True)
    assert result["boost"] == 0
    assert result["domains_matched"] == []
    assert result["has_decision_logic"] is False
    assert result["detail"] == ""


@patch("domain_scoring.get_declared_domain", side_effect=_no_policy)
def test_detail_contains_domain_name_on_match(_mock):
    """Detail string mentions matched domain(s)."""
    text = "credit_score loan default_risk"
    result = compute_domain_boost(text, has_ai_indicator=True)
    assert "finance" in result["detail"]


@patch("domain_scoring.get_declared_domain", side_effect=_no_policy)
def test_detail_mentions_decision_logic(_mock):
    """Detail string mentions decision logic when present."""
    text = "if score > threshold:\n    reject applicant\nhiring pipeline"
    result = compute_domain_boost(text, has_ai_indicator=True)
    assert "decision logic" in result["detail"].lower()


# ===================================================================
# 6. Declared domain from policy (overrides keyword detection)
# ===================================================================


def test_declared_regulated_domain_overrides_keywords():
    """When policy declares a regulated domain, keyword detection is bypassed."""
    with patch("domain_scoring.get_declared_domain", return_value={
        "domain": "employment", "risk_level": "high",
        "name": "HR Tool", "is_regulated": True,
    }):
        # Text has NO employment keywords, but policy says employment
        result = compute_domain_boost("import numpy\nx = 1", has_ai_indicator=True)
        assert result["boost"] > 0, "Declared domain should provide boost even without keywords"
        assert "employment" in result["domains_matched"]
        assert "Declared domain" in result["detail"]


def test_declared_medical_domain():
    """Declared medical domain -> medical boost."""
    with patch("domain_scoring.get_declared_domain", return_value={
        "domain": "medical", "risk_level": "high",
        "name": "Diagnostics", "is_regulated": True,
    }):
        result = compute_domain_boost("x = 1", has_ai_indicator=True)
        assert result["boost"] == 15
        assert "medical" in result["domains_matched"]


def test_declared_creditworthiness_maps_to_finance():
    """Declared creditworthiness domain maps to finance internally."""
    with patch("domain_scoring.get_declared_domain", return_value={
        "domain": "creditworthiness", "risk_level": "high",
        "name": "Credit Scoring", "is_regulated": True,
    }):
        result = compute_domain_boost("x = 1", has_ai_indicator=True)
        assert "finance" in result["domains_matched"]


def test_declared_non_regulated_domain_falls_through():
    """Non-regulated declared domain -> keyword detection runs normally."""
    with patch("domain_scoring.get_declared_domain", return_value={
        "domain": "customer_support", "risk_level": "",
        "name": "Chatbot", "is_regulated": False,
    }):
        # No domain keywords -> 0 boost
        result = compute_domain_boost("x = 1", has_ai_indicator=True)
        assert result["boost"] == 0


# ===================================================================
# 7. Module-level constants sanity checks
# ===================================================================


def test_regulated_domains_set():
    """REGULATED_DOMAINS should contain known high-risk domains."""
    expected = {"creditworthiness", "employment", "insurance", "education",
                "legal", "law_enforcement", "migration", "biometric", "medical"}
    assert REGULATED_DOMAINS == expected


def test_informational_domains_set():
    """INFORMATIONAL_DOMAINS should contain known non-regulated domains."""
    expected = {"customer_support", "internal_tooling", "content_generation", "general_purpose"}
    assert INFORMATIONAL_DOMAINS == expected


def test_all_domains_have_required_keys():
    """Every domain in DOMAIN_KEYWORDS has keywords, category, and boost."""
    for domain, cfg in DOMAIN_KEYWORDS.items():
        assert "keywords" in cfg, f"{domain} missing 'keywords'"
        assert "category" in cfg, f"{domain} missing 'category'"
        assert "boost" in cfg, f"{domain} missing 'boost'"
        assert isinstance(cfg["keywords"], list), f"{domain} keywords is not a list"
        assert len(cfg["keywords"]) > 0, f"{domain} has empty keywords"
        assert isinstance(cfg["boost"], int), f"{domain} boost is not int"


def test_employment_has_exclude_if():
    """Employment domain must have exclude_if patterns."""
    assert "exclude_if" in DOMAIN_KEYWORDS["employment"]
    assert len(DOMAIN_KEYWORDS["employment"]["exclude_if"]) > 0


def test_all_domains_have_exclude_if():
    """All domains should have exclude_if patterns for precision."""
    for domain, cfg in DOMAIN_KEYWORDS.items():
        assert "exclude_if" in cfg, f"{domain} missing exclude_if"
        assert len(cfg["exclude_if"]) > 0, f"{domain} has empty exclude_if"


def test_compiled_patterns_match_source():
    """_DOMAIN_COMPILED should have entries for every source domain."""
    assert set(_DOMAIN_COMPILED.keys()) == set(DOMAIN_KEYWORDS.keys())


def test_decision_patterns_are_compiled():
    """All decision patterns should be compiled regex objects."""
    import re
    for p in _DECISION_PATTERNS:
        assert isinstance(p, re.Pattern), f"Expected compiled regex, got {type(p)}"


# ===================================================================
# 8. Edge cases
# ===================================================================


@patch("domain_scoring.get_declared_domain", side_effect=_no_policy)
def test_empty_text(_mock):
    """Empty text -> 0 boost."""
    result = compute_domain_boost("", has_ai_indicator=True)
    assert result["boost"] == 0
    assert result["domains_matched"] == []


@patch("domain_scoring.get_declared_domain", side_effect=_no_policy)
def test_case_insensitive_matching(_mock):
    """Keywords should match regardless of case."""
    text = "HIRING APPLICANT RESUME INTERVIEW"
    result = compute_domain_boost(text, has_ai_indicator=True)
    assert "employment" in result["domains_matched"]


@patch("domain_scoring.get_declared_domain", side_effect=_no_policy)
def test_exclude_also_case_insensitive(_mock):
    """Exclude patterns should match regardless of case."""
    text = "IMPORT THREADING\nhiring applicant"
    result = compute_domain_boost(text, has_ai_indicator=True)
    assert "employment" not in result["domains_matched"]


@patch("domain_scoring.get_declared_domain", side_effect=_no_policy)
def test_word_boundary_prevents_false_match(_mock):
    r"""Word boundary \\b prevents 'cv' from matching inside words like 'cv2'."""
    # "cv" alone should match employment, but "cv2" should not
    text_cv2 = "import cv2\nimage = cv2.imread(path)"
    result = compute_domain_boost(text_cv2, has_ai_indicator=True)
    # cv2 alone should not trigger employment (the word boundary means \bcv\b
    # would match "cv" but not "cv2" because "2" is a word character)
    # However, the regex is r"\bcv\b" which requires word boundary after "cv"
    # In "cv2", the "2" is a word char so \b won't match — correct behaviour
    assert "employment" not in result["domains_matched"] or \
        any(kw != "cv" for kw in ["applicant", "hire", "resume"]
            if kw in text_cv2.lower()), \
        "cv2 alone should not trigger employment domain"


@patch("domain_scoring.get_declared_domain", side_effect=_no_policy)
def test_filter_score_decision_pattern(_mock):
    """filter ... score pattern matches decision logic."""
    text = "filter candidates by score\nhiring pipeline applicant"
    result = compute_domain_boost(text, has_ai_indicator=True)
    assert result["has_decision_logic"] is True
