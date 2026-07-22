# regula-ignore
"""Unit tests for compliance_check.py — EU AI Act gap assessment engine.

Tests the helper functions, article-specific checkers, scoring logic,
model card validation, regulation overlap, and output formatters.
"""
import sys
import tempfile
import shutil
from pathlib import Path

_scripts_dir = str(Path(__file__).resolve().parent.parent / "scripts")
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

_tests_dir = str(Path(__file__).resolve().parent)
if _tests_dir not in sys.path:
    sys.path.insert(0, _tests_dir)

from helpers import assert_eq, assert_true, assert_false, assert_in, assert_gte, assert_lte

from compliance_check import (
    _file_matches_glob,
    _search_content,
    _is_in_directory,
    _score_to_status,
    _walk_project,
    _read_file,
    _compute_regulation_overlap,
    validate_model_card,
    assess_compliance,
    format_gap_text,
    format_gap_json,
    ARTICLE_NUMBERS,
    ARTICLE_TITLES,
    ARTICLE_CHECKERS,
    MODEL_CARD_REQUIRED_SECTIONS,
    ARTICLE_6_GUIDELINES_STATUS,
    _check_article_9,
    _check_article_10,
    _check_article_11,
    _check_article_12,
    _check_article_13,
    _check_article_14,
    _check_article_15,
    _check_article_17,
)


# ---------------------------------------------------------------------------
# Helper: create a temporary project with specific files
# ---------------------------------------------------------------------------

def _make_project(files: dict) -> str:
    """Create a temp directory with the given files and return its path.

    Args:
        files: dict mapping relative paths to file content strings.
    Returns:
        Absolute path to the temp directory.
    """
    tmp = tempfile.mkdtemp(prefix="regula_test_cc_")
    for rel_path, content in files.items():
        full = Path(tmp) / rel_path
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(content, encoding="utf-8")
    return tmp


def _cleanup(path: str):
    shutil.rmtree(path, ignore_errors=True)


def _build_index(project_path: str) -> list:
    """Build the file index the same way assess_compliance does."""
    return list(_walk_project(project_path))


# ======================================================================
# _file_matches_glob
# ======================================================================

def test_file_matches_glob_basename_match():
    """_file_matches_glob matches by basename."""
    assert_true(
        _file_matches_glob("docs/risk_assessment.md", ["risk_assessment*"]),
        "glob matches basename risk_assessment.md",
    )
    print("  PASS  _file_matches_glob basename match")


def test_file_matches_glob_no_match():
    """_file_matches_glob returns False when no patterns match."""
    assert_false(
        _file_matches_glob("src/main.py", ["risk_assessment*", "model_card*"]),
        "glob should not match unrelated file",
    )
    print("  PASS  _file_matches_glob no match")


def test_file_matches_glob_case_insensitive():
    """_file_matches_glob is case-insensitive."""
    assert_true(
        _file_matches_glob("docs/RISK_ASSESSMENT.md", ["risk_assessment*"]),
        "glob case-insensitive match",
    )
    print("  PASS  _file_matches_glob case insensitive")


def test_file_matches_glob_full_path_pattern():
    """_file_matches_glob can match against the full relative path."""
    assert_true(
        _file_matches_glob(".regula/report.json", [".regula/*"]),
        "glob matches full relative path",
    )
    print("  PASS  _file_matches_glob full path pattern")


# ======================================================================
# _search_content
# ======================================================================

def test_search_content_finds_patterns():
    """_search_content returns matched patterns."""
    content = "This project uses a risk management system for AI safety."
    patterns = [r"risk\s+management", r"data\s+governance", r"ai\s+safety"]
    matched = _search_content(content, patterns)
    assert_in(r"risk\s+management", matched, "risk management matched")
    assert_in(r"ai\s+safety", matched, "ai safety matched")
    assert_eq(len(matched), 2, "exactly 2 patterns matched")
    print("  PASS  _search_content finds patterns")


def test_search_content_no_matches():
    """_search_content returns empty list when nothing matches."""
    content = "This is a simple web app."
    patterns = [r"risk\s+management", r"data\s+governance"]
    matched = _search_content(content, patterns)
    assert_eq(len(matched), 0, "no patterns matched")
    print("  PASS  _search_content no matches")


def test_search_content_case_insensitive():
    """_search_content is case-insensitive (lowercases content)."""
    content = "RISK MANAGEMENT system for compliance."
    patterns = [r"risk\s+management"]
    matched = _search_content(content, patterns)
    assert_eq(len(matched), 1, "case-insensitive match")
    print("  PASS  _search_content case insensitive")


# ======================================================================
# _is_in_directory
# ======================================================================

def test_is_in_directory_positive():
    """_is_in_directory returns True when file is in named directory."""
    assert_true(
        _is_in_directory("docs/risk/assessment.md", ["docs"]),
        "file is in docs directory",
    )
    print("  PASS  _is_in_directory positive")


def test_is_in_directory_negative():
    """_is_in_directory returns False when file is not in named directory."""
    assert_false(
        _is_in_directory("src/main.py", ["docs", "compliance"]),
        "file not in named directories",
    )
    print("  PASS  _is_in_directory negative")


def test_is_in_directory_nested():
    """_is_in_directory matches any ancestor directory."""
    assert_true(
        _is_in_directory("project/compliance/audits/report.md", ["compliance"]),
        "matches nested directory",
    )
    print("  PASS  _is_in_directory nested")


def test_is_in_directory_file_not_dir():
    """_is_in_directory does not match the filename itself, only parent dirs."""
    assert_false(
        _is_in_directory("docs.md", ["docs"]),
        "filename itself should not match",
    )
    print("  PASS  _is_in_directory file not dir")


# ======================================================================
# _score_to_status
# ======================================================================

def test_score_to_status_not_found():
    """Score 0 maps to not_found."""
    assert_eq(_score_to_status(0), "not_found", "0 -> not_found")
    print("  PASS  _score_to_status not_found")


def test_score_to_status_partial():
    """Score 1-49 maps to partial."""
    assert_eq(_score_to_status(1), "partial", "1 -> partial")
    assert_eq(_score_to_status(30), "partial", "30 -> partial")
    assert_eq(_score_to_status(49), "partial", "49 -> partial")
    print("  PASS  _score_to_status partial")


def test_score_to_status_moderate():
    """Score 50-79 maps to moderate."""
    assert_eq(_score_to_status(50), "moderate", "50 -> moderate")
    assert_eq(_score_to_status(65), "moderate", "65 -> moderate")
    assert_eq(_score_to_status(79), "moderate", "79 -> moderate")
    print("  PASS  _score_to_status moderate")


def test_score_to_status_strong():
    """Score 80-100 maps to strong."""
    assert_eq(_score_to_status(80), "strong", "80 -> strong")
    assert_eq(_score_to_status(100), "strong", "100 -> strong")
    print("  PASS  _score_to_status strong")


# ======================================================================
# _walk_project
# ======================================================================

def test_walk_project_finds_scannable_files():
    """_walk_project yields .py and .md files but not .jpg."""
    tmp = _make_project({
        "main.py": "print('hello')",
        "README.md": "# readme",
        "image.jpg": "binary",
    })
    try:
        results = list(_walk_project(tmp))
        rel_paths = [r[0] for r in results]
        assert_in("main.py", rel_paths, "finds .py")
        assert_in("README.md", rel_paths, "finds .md")
        assert_true("image.jpg" not in rel_paths, "skips .jpg")
    finally:
        _cleanup(tmp)
    print("  PASS  _walk_project finds scannable files")


def test_walk_project_skips_node_modules():
    """_walk_project skips common skip directories like node_modules."""
    tmp = _make_project({
        "app.py": "import os",
        "node_modules/dep/index.js": "module.exports = {}",
    })
    try:
        results = list(_walk_project(tmp))
        rel_paths = [r[0] for r in results]
        node_files = [p for p in rel_paths if "node_modules" in p]
        assert_eq(len(node_files), 0, "no node_modules files")
    finally:
        _cleanup(tmp)
    print("  PASS  _walk_project skips node_modules")


# ======================================================================
# _read_file
# ======================================================================

def test_read_file_success():
    """_read_file reads content from an existing file."""
    tmp = _make_project({"test.txt": "hello world"})
    try:
        content = _read_file(str(Path(tmp) / "test.txt"))
        assert_eq(content, "hello world", "reads file content")
    finally:
        _cleanup(tmp)
    print("  PASS  _read_file success")


def test_read_file_nonexistent():
    """_read_file returns None for nonexistent file."""
    result = _read_file("/nonexistent/path/that/does/not/exist.txt")
    assert_eq(result, None, "returns None for missing file")
    print("  PASS  _read_file nonexistent")


# ======================================================================
# validate_model_card
# ======================================================================

def test_validate_model_card_complete():
    """A model card with all sections scores 100%."""
    card = """
    # Model Card
    ## Intended Use
    This model is intended for text classification.
    ## Limitations
    Known limitation: poor performance on low-resource languages.
    ## Training Data
    Trained on the XYZ dataset.
    ## Performance
    Accuracy: 95%. F1 score: 0.93.
    ## Ethical Considerations
    We assessed bias and fairness implications.
    """
    result = validate_model_card(card)
    assert_eq(result["completeness_score"], 100, "complete model card scores 100")
    assert_eq(len(result["sections_missing"]), 0, "no sections missing")
    assert_eq(len(result["sections_found"]), 5, "all 5 sections found")
    print("  PASS  validate_model_card complete")


def test_validate_model_card_partial():
    """A model card with some sections has a partial score."""
    card = """
    # Model Card
    ## Intended Use
    Classification of documents.
    ## Training Data
    Trained on public corpus.
    """
    result = validate_model_card(card)
    assert_eq(result["completeness_score"], 40, "2/5 sections = 40%")
    assert_eq(len(result["sections_found"]), 2, "2 sections found")
    assert_eq(len(result["sections_missing"]), 3, "3 sections missing")
    print("  PASS  validate_model_card partial")


def test_validate_model_card_empty():
    """An empty model card scores 0%."""
    result = validate_model_card("")
    assert_eq(result["completeness_score"], 0, "empty card scores 0")
    assert_eq(len(result["sections_missing"]), 5, "all 5 sections missing")
    print("  PASS  validate_model_card empty")


# ======================================================================
# _compute_regulation_overlap
# ======================================================================

def test_regulation_overlap_high_risk():
    """High-risk projects get regulation overlap data."""
    overlap = _compute_regulation_overlap("high_risk")
    assert_true(len(overlap) > 0, "high_risk has overlap entries")
    # Article 15 should overlap with GDPR, DORA, and NIS2
    assert_in("15", overlap, "Article 15 present in overlap")
    assert_in("gdpr", overlap["15"], "GDPR overlap for Art 15")
    assert_in("dora", overlap["15"], "DORA overlap for Art 15")
    assert_in("nis2", overlap["15"], "NIS2 overlap for Art 15")
    print("  PASS  _compute_regulation_overlap high_risk")


def test_regulation_overlap_minimal_risk():
    """Minimal-risk projects get no regulation overlap."""
    overlap = _compute_regulation_overlap("minimal_risk")
    assert_eq(len(overlap), 0, "minimal_risk has no overlap")
    print("  PASS  _compute_regulation_overlap minimal_risk")


def test_regulation_overlap_not_ai():
    """Non-AI projects get no regulation overlap."""
    overlap = _compute_regulation_overlap("not_ai")
    assert_eq(len(overlap), 0, "not_ai has no overlap")
    print("  PASS  _compute_regulation_overlap not_ai")


def test_regulation_overlap_prohibited():
    """Prohibited tier also gets regulation overlap."""
    overlap = _compute_regulation_overlap("prohibited")
    assert_true(len(overlap) > 0, "prohibited has overlap entries")
    print("  PASS  _compute_regulation_overlap prohibited")


# ======================================================================
# Individual article checkers — tested with synthetic temp projects
# ======================================================================

def test_article_9_no_risk_docs():
    """Article 9: empty project scores 0 with gaps."""
    tmp = _make_project({"main.py": "print('hello')"})
    try:
        idx = _build_index(tmp)
        score, evidence, gaps = _check_article_9(tmp, idx)
        assert_eq(score, 0, "no risk docs -> score 0")
        assert_true(len(gaps) > 0, "gaps reported for no risk docs")
        assert_true(
            any("risk assessment" in g.lower() or "risk register" in g.lower() for g in gaps),
            "gap mentions risk assessment or register",
        )
    finally:
        _cleanup(tmp)
    print("  PASS  Article 9: no risk docs")


def test_article_9_generic_risk_docs():
    """Article 9: generic risk docs without AI reference score 30."""
    tmp = _make_project({
        "docs/risk_assessment.md": (
            "# Risk Assessment\n"
            "Risk management system for the project.\n"
            "Residual risk must be tracked.\n"
        ),
    })
    try:
        idx = _build_index(tmp)
        score, evidence, gaps = _check_article_9(tmp, idx)
        assert_eq(score, 30, "generic risk docs -> score 30")
        assert_true(len(evidence) > 0, "evidence found for risk docs")
    finally:
        _cleanup(tmp)
    print("  PASS  Article 9: generic risk docs")


def test_article_9_ai_risk_docs():
    """Article 9: risk docs referencing AI system score 60."""
    tmp = _make_project({
        "docs/risk_assessment.md": (
            "# Risk Assessment\n"
            "Risk management system for the AI system.\n"
            "Machine learning model risk mitigation.\n"
        ),
    })
    try:
        idx = _build_index(tmp)
        score, evidence, gaps = _check_article_9(tmp, idx)
        assert_eq(score, 60, "AI risk docs -> score 60")
    finally:
        _cleanup(tmp)
    print("  PASS  Article 9: AI-referenced risk docs")


def test_article_9_structured_mitigations():
    """Article 9: structured risk register with mitigations scores 100."""
    tmp = _make_project({
        "docs/risk_assessment.md": (
            "# Risk Assessment\n"
            "Risk management system for the AI system.\n"
            "Machine learning risk mitigation plan:\n"
            "Mitigation: retrain model\n"
            "Status: in_progress\nOwner: team_lead\nDeadline: 2026-06-01\n"
        ),
    })
    try:
        idx = _build_index(tmp)
        score, evidence, gaps = _check_article_9(tmp, idx)
        assert_eq(score, 100, "structured mitigations -> score 100")
    finally:
        _cleanup(tmp)
    print("  PASS  Article 9: structured mitigations")


def test_article_10_no_data_governance():
    """Article 10: empty project scores 0."""
    tmp = _make_project({"app.py": "x = 1"})
    try:
        idx = _build_index(tmp)
        score, evidence, gaps = _check_article_10(tmp, idx)
        assert_eq(score, 0, "no data governance -> score 0")
        assert_true(len(gaps) >= 3, "at least 3 gaps for data governance")
    finally:
        _cleanup(tmp)
    print("  PASS  Article 10: no data governance")


def test_article_10_with_data_docs_and_validation():
    """Article 10: data docs + validation library scores 65."""
    tmp = _make_project({
        "docs/data_dictionary.md": "# Data Dictionary\nTraining data description.\n",
        "requirements.txt": "pydantic>=2.0\ntorch>=2.0\n",
    })
    try:
        idx = _build_index(tmp)
        score, evidence, gaps = _check_article_10(tmp, idx)
        assert_eq(score, 65, "data docs + validation -> score 65")
    finally:
        _cleanup(tmp)
    print("  PASS  Article 10: data docs + validation")


def test_article_11_no_tech_docs():
    """Article 11: empty project scores 0."""
    tmp = _make_project({"app.py": "x = 1"})
    try:
        idx = _build_index(tmp)
        score, evidence, gaps = _check_article_11(tmp, idx)
        assert_eq(score, 0, "no tech docs -> score 0")
        assert_true(len(gaps) > 0, "gaps present for no tech docs")
    finally:
        _cleanup(tmp)
    print("  PASS  Article 11: no tech docs")


def test_article_11_model_card_file():
    """Article 11: project with a model card file gets credit."""
    card_content = (
        "# Model Card\n"
        "## Intended Use\nText classification.\n"
        "## Limitations\nPoor on rare languages.\n"
        "## Training Data\nPublic corpus.\n"
        "## Performance\nAccuracy: 95%.\n"
        "## Ethical Considerations\nBias assessed.\n"
    )
    tmp = _make_project({"model_card.md": card_content})
    try:
        idx = _build_index(tmp)
        score, evidence, gaps = _check_article_11(tmp, idx)
        assert_true(score > 0, "model card gives nonzero score")
        assert_true(
            any("model card" in e.lower() for e in evidence),
            "evidence mentions model card",
        )
    finally:
        _cleanup(tmp)
    print("  PASS  Article 11: model card file")


def test_article_12_no_logging():
    """Article 12: project without logging scores 0."""
    tmp = _make_project({"app.py": "x = 1 + 2\nprint(x)\n"})
    try:
        idx = _build_index(tmp)
        score, evidence, gaps = _check_article_12(tmp, idx)
        assert_eq(score, 0, "no logging -> score 0")
        assert_true(len(gaps) >= 3, "at least 3 gaps for logging")
    finally:
        _cleanup(tmp)
    print("  PASS  Article 12: no logging")


def test_article_12_basic_logging():
    """Article 12: project with basic logging scores 30."""
    tmp = _make_project({
        "app.py": (
            "import logging\n"
            "logger = logging.getLogger(__name__)\n"
            "logger.info('starting app')\n"
        ),
    })
    try:
        idx = _build_index(tmp)
        score, evidence, gaps = _check_article_12(tmp, idx)
        assert_eq(score, 30, "basic logging -> score 30")
        assert_true(
            any("logging" in e.lower() for e in evidence),
            "evidence mentions logging",
        )
    finally:
        _cleanup(tmp)
    print("  PASS  Article 12: basic logging")


def test_article_12_ai_logging():
    """Article 12: project with AI operation logging scores higher."""
    tmp = _make_project({
        "app.py": (
            "import logging\n"
            "logger = logging.getLogger(__name__)\n"
            "logger.info('model prediction output: %s', result)\n"
            "audit_log(prediction=result, model='v1')\n"
        ),
    })
    try:
        idx = _build_index(tmp)
        score, evidence, gaps = _check_article_12(tmp, idx)
        assert_gte(score, 65, "AI logging -> score >= 65")
    finally:
        _cleanup(tmp)
    print("  PASS  Article 12: AI operation logging")


def test_article_13_no_transparency():
    """Article 13: empty project scores 0."""
    tmp = _make_project({"app.py": "x = 1"})
    try:
        idx = _build_index(tmp)
        score, evidence, gaps = _check_article_13(tmp, idx)
        assert_eq(score, 0, "no transparency -> score 0")
    finally:
        _cleanup(tmp)
    print("  PASS  Article 13: no transparency")


def test_article_13_with_disclosure():
    """Article 13: code with AI disclosure gets credit."""
    tmp = _make_project({
        "app.py": (
            "# This output is AI-generated and should be reviewed.\n"
            "def generate():\n"
            "    return 'ai-powered response'\n"
        ),
    })
    try:
        idx = _build_index(tmp)
        score, evidence, gaps = _check_article_13(tmp, idx)
        assert_true(score > 0, "AI disclosure gives nonzero score")
    finally:
        _cleanup(tmp)
    print("  PASS  Article 13: with disclosure")


def test_article_14_no_oversight():
    """Article 14: empty project scores 0."""
    tmp = _make_project({"app.py": "x = 1"})
    try:
        idx = _build_index(tmp)
        score, evidence, gaps = _check_article_14(tmp, idx)
        assert_eq(score, 0, "no oversight -> score 0")
        assert_true(
            any("oversight" in g.lower() for g in gaps),
            "gap mentions oversight",
        )
    finally:
        _cleanup(tmp)
    print("  PASS  Article 14: no oversight")


def test_article_14_with_oversight_mechanism():
    """Article 14: code with human review mechanism scores 45."""
    tmp = _make_project({
        "app.py": (
            "def process_request(request):\n"
            "    result = model.predict(request)\n"
            "    if needs_review(result):\n"
            "        return require_approval(result)\n"
            "    return result\n"
        ),
    })
    try:
        idx = _build_index(tmp)
        score, evidence, gaps = _check_article_14(tmp, idx)
        assert_eq(score, 45, "oversight mechanism -> score 45")
    finally:
        _cleanup(tmp)
    print("  PASS  Article 14: oversight mechanism")


def test_article_14_with_oversight_docs():
    """Article 14: documentation with human oversight content scores 45."""
    tmp = _make_project({
        "docs/oversight.md": (
            "# Human Oversight\n"
            "All model outputs undergo human review before deployment.\n"
            "Escalation procedures are in place.\n"
        ),
    })
    try:
        idx = _build_index(tmp)
        score, evidence, gaps = _check_article_14(tmp, idx)
        assert_eq(score, 45, "oversight docs -> score 45")
    finally:
        _cleanup(tmp)
    print("  PASS  Article 14: oversight docs")


def test_article_15_no_security():
    """Article 15: project without tests/security/monitoring has low score.

    Note: score may be 20 (not 0) because when dependency_scan is available
    and there are no dependencies, pinning_score defaults to 100 (trivially
    fully pinned), contributing 1 component and thus score = 20.
    """
    tmp = _make_project({"app.py": "x = 1"})
    try:
        idx = _build_index(tmp)
        score, evidence, gaps = _check_article_15(tmp, idx)
        assert_lte(score, 20, "minimal project -> score <= 20")
        assert_true(
            any("test" in g.lower() for g in gaps),
            "gap mentions tests",
        )
        assert_true(
            any("security" in g.lower() for g in gaps),
            "gap mentions security",
        )
    finally:
        _cleanup(tmp)
    print("  PASS  Article 15: no security")


def test_article_15_with_tests():
    """Article 15: project with test files gets tests credit."""
    tmp = _make_project({
        "app.py": "def add(a, b): return a + b",
        "tests/test_app.py": "def test_add(): assert add(1, 2) == 3",
    })
    try:
        idx = _build_index(tmp)
        score, evidence, gaps = _check_article_15(tmp, idx)
        assert_true(score > 0, "test files give nonzero score")
        assert_true(
            any("test" in e.lower() for e in evidence),
            "evidence mentions tests",
        )
    finally:
        _cleanup(tmp)
    print("  PASS  Article 15: with tests")


def test_article_15_with_security_file():
    """Article 15: SECURITY.md file gives security credit."""
    tmp = _make_project({
        "app.py": "x = 1",
        "SECURITY.md": "# Security Policy\nReport vulnerabilities to security@example.com\n",
    })
    try:
        idx = _build_index(tmp)
        score, evidence, gaps = _check_article_15(tmp, idx)
        assert_true(score > 0, "SECURITY.md gives nonzero score")
        assert_true(
            any("security" in e.lower() for e in evidence),
            "evidence mentions security",
        )
    finally:
        _cleanup(tmp)
    print("  PASS  Article 15: SECURITY.md")


def test_article_17_no_qms():
    """Article 17: empty project scores 0."""
    tmp = _make_project({"app.py": "x = 1"})
    try:
        idx = _build_index(tmp)
        score, evidence, gaps = _check_article_17(tmp, idx)
        assert_eq(score, 0, "no QMS -> score 0")
        assert_true(len(gaps) == 3, "3 gaps for QMS")
    finally:
        _cleanup(tmp)
    print("  PASS  Article 17: no QMS")


def test_article_17_with_qms_docs():
    """Article 17: QMS documentation gives credit."""
    tmp = _make_project({
        "docs/quality_management.md": (
            "# Quality Management System\n"
            "ISO 42001 certified.\n"
            "Quality policy: continuous improvement.\n"
            "Quality objectives defined quarterly.\n"
            "Standard operating procedure for model validation.\n"
            "SOP for change management and corrective action.\n"
        ),
    })
    try:
        idx = _build_index(tmp)
        score, evidence, gaps = _check_article_17(tmp, idx)
        assert_eq(score, 100, "full QMS docs -> score 100")
        assert_eq(len(gaps), 0, "no gaps with full QMS")
    finally:
        _cleanup(tmp)
    print("  PASS  Article 17: with QMS docs")


# ======================================================================
# assess_compliance — integration-level
# ======================================================================

def test_assess_compliance_structure():
    """assess_compliance returns all required top-level keys."""
    tmp = _make_project({"main.py": "print('hello')"})
    try:
        result = assess_compliance(tmp)
        for key in ("project", "highest_risk", "assessment_date", "articles",
                     "overall_score", "summary", "regulation_overlap",
                     "article_6_guidelines_status"):
            assert_in(key, result, f"result has key {key}")
    finally:
        _cleanup(tmp)
    print("  PASS  assess_compliance structure")


def test_assess_compliance_all_articles():
    """assess_compliance checks all 8 articles by default."""
    tmp = _make_project({"main.py": "print('hello')"})
    try:
        result = assess_compliance(tmp)
        assert_eq(len(result["articles"]), 8, "8 articles assessed")
        for art_num in ARTICLE_NUMBERS:
            assert_in(art_num, result["articles"], f"article {art_num} assessed")
    finally:
        _cleanup(tmp)
    print("  PASS  assess_compliance all articles")


def test_assess_compliance_single_article():
    """assess_compliance can check a single article."""
    tmp = _make_project({"main.py": "print('hello')"})
    try:
        result = assess_compliance(tmp, articles=["14"])
        assert_eq(len(result["articles"]), 1, "only 1 article assessed")
        assert_in("14", result["articles"], "article 14 assessed")
    finally:
        _cleanup(tmp)
    print("  PASS  assess_compliance single article")


def test_assess_compliance_article_result_keys():
    """Each article result has score, evidence, gaps, title, status."""
    tmp = _make_project({"main.py": "print('hello')"})
    try:
        result = assess_compliance(tmp)
        for art_num, art_data in result["articles"].items():
            for key in ("title", "status", "score", "evidence", "gaps"):
                assert_in(key, art_data, f"article {art_num} has {key}")
            assert_true(
                isinstance(art_data["score"], int),
                f"article {art_num} score is int",
            )
            assert_true(
                isinstance(art_data["evidence"], list),
                f"article {art_num} evidence is list",
            )
            assert_true(
                isinstance(art_data["gaps"], list),
                f"article {art_num} gaps is list",
            )
    finally:
        _cleanup(tmp)
    print("  PASS  assess_compliance article result keys")


def test_assess_compliance_invalid_path():
    """assess_compliance raises ValueError for invalid path."""
    try:
        assess_compliance("/nonexistent/path/that/does/not/exist")
        assert_true(False, "should have raised ValueError")
    except ValueError:
        assert_true(True, "ValueError raised for invalid path")
    print("  PASS  assess_compliance invalid path")


def test_assess_compliance_overall_score_range():
    """Overall score is between 0 and 100."""
    tmp = _make_project({"main.py": "print('hello')"})
    try:
        result = assess_compliance(tmp)
        assert_gte(result["overall_score"], 0, "overall score >= 0")
        assert_lte(result["overall_score"], 100, "overall score <= 100")
    finally:
        _cleanup(tmp)
    print("  PASS  assess_compliance overall score range")


# ======================================================================
# format_gap_text
# ======================================================================

def test_format_gap_text_contains_key_sections():
    """format_gap_text includes project name, scores, and summary."""
    tmp = _make_project({"main.py": "print('hello')"})
    try:
        assessment = assess_compliance(tmp)
        text = format_gap_text(assessment)
        assert_true("Compliance Gap Assessment" in text, "header present")
        assert_true("Overall score:" in text, "overall score present")
        assert_true("Summary:" in text, "summary present")
        assert_true("Article 6" in text, "Article 6 guidance present")
        # Check that all articles appear
        for art_num in ARTICLE_NUMBERS:
            assert_in(f"Article {art_num}", text, f"Article {art_num} in output")
    finally:
        _cleanup(tmp)
    print("  PASS  format_gap_text contains key sections")


def test_format_gap_text_status_labels():
    """format_gap_text uses correct status labels."""
    tmp = _make_project({"main.py": "print('hello')"})
    try:
        assessment = assess_compliance(tmp)
        text = format_gap_text(assessment)
        # An empty project should have NOT FOUND labels
        assert_true("NOT FOUND" in text, "NOT FOUND status label present")
    finally:
        _cleanup(tmp)
    print("  PASS  format_gap_text status labels")


# ======================================================================
# format_gap_json
# ======================================================================

def test_format_gap_json_is_valid():
    """format_gap_json produces valid JSON."""
    import json
    tmp = _make_project({"main.py": "print('hello')"})
    try:
        assessment = assess_compliance(tmp)
        json_str = format_gap_json(assessment)
        parsed = json.loads(json_str)
        assert_in("articles", parsed, "JSON has articles")
        assert_in("overall_score", parsed, "JSON has overall_score")
    finally:
        _cleanup(tmp)
    print("  PASS  format_gap_json is valid")


# ======================================================================
# Constants and configuration
# ======================================================================

def test_article_numbers_are_strings():
    """ARTICLE_NUMBERS are all string representations of ints."""
    for num in ARTICLE_NUMBERS:
        assert_true(isinstance(num, str), f"{num} is a string")
        assert_true(num.isdigit(), f"{num} is a digit string")
    print("  PASS  ARTICLE_NUMBERS are strings")


def test_article_titles_match_numbers():
    """Every ARTICLE_NUMBER has a corresponding title."""
    for num in ARTICLE_NUMBERS:
        assert_in(num, ARTICLE_TITLES, f"Article {num} has a title")
    print("  PASS  ARTICLE_TITLES match NUMBERS")


def test_article_checkers_match_numbers():
    """Every ARTICLE_NUMBER has a corresponding checker function."""
    for num in ARTICLE_NUMBERS:
        assert_in(num, ARTICLE_CHECKERS, f"Article {num} has a checker")
        assert_true(callable(ARTICLE_CHECKERS[num]), f"Article {num} checker is callable")
    print("  PASS  ARTICLE_CHECKERS match NUMBERS")


def test_article_6_guidelines_status_structure():
    """ARTICLE_6_GUIDELINES_STATUS has required keys."""
    for key in ("deadline", "deadline_source", "missed", "current_status",
                "verified_on", "implication", "next_steps"):
        assert_in(key, ARTICLE_6_GUIDELINES_STATUS, f"Art 6 status has {key}")
    assert_true(ARTICLE_6_GUIDELINES_STATUS["missed"], "Art 6 deadline marked as missed")
    print("  PASS  ARTICLE_6_GUIDELINES_STATUS structure")


def test_model_card_required_sections_structure():
    """MODEL_CARD_REQUIRED_SECTIONS has expected section names."""
    expected = {"intended_use", "limitations", "training_data", "performance", "ethical"}
    assert_eq(set(MODEL_CARD_REQUIRED_SECTIONS.keys()), expected, "expected section names")
    for name, keywords in MODEL_CARD_REQUIRED_SECTIONS.items():
        assert_true(isinstance(keywords, list), f"{name} keywords is a list")
        assert_true(len(keywords) > 0, f"{name} has at least one keyword")
    print("  PASS  MODEL_CARD_REQUIRED_SECTIONS structure")


def test_highest_risk_honours_suppressions_like_check():
    """gap's header tier must come from the same pipeline as `regula
    check`. Regression for the July 2026 drift where
    _determine_highest_risk classified raw file content — no
    regula-ignore handling — and reported a risk tier on a project
    whose check verdict was NO AI DETECTED (this repo)."""
    from compliance_check import _determine_highest_risk

    ai_snippet = (
        "import openai\nimport langchain\n"
        "from langchain.chat_models import ChatOpenAI\n"
        "chatbot = ChatOpenAI(model='gpt-4')\n"
        "response = chatbot.predict('hello user')\n"
    )

    with tempfile.TemporaryDirectory() as tmp:
        app = Path(tmp) / "app.py"
        app.write_text("# regula-ignore\n" + ai_snippet, encoding="utf-8")
        tier = _determine_highest_risk(tmp)
        assert_eq(tier, "not_ai",
                  "file-level regula-ignore must suppress the gap tier")

    # And without the suppression, a genuinely flagged project must NOT
    # come back not_ai — the pipeline must still surface real findings.
    with tempfile.TemporaryDirectory() as tmp:
        app = Path(tmp) / "app.py"
        app.write_text(ai_snippet, encoding="utf-8")
        tier = _determine_highest_risk(tmp)
        assert_true(tier != "not_ai",
                    f"unsuppressed AI findings must surface a tier, got {tier}")
    print("  PASS  _determine_highest_risk honours suppressions like check")


def test_read_file_serves_from_the_per_scan_cache():
    """During a scan, _read_file must return cached content, and outside a
    scan it must fall back to a safe by-name read.

    This is the mechanism that closes the ancestor-directory race (#33): the
    content is read once during the walk through the os.fwalk descriptor and
    cached, so the eight checkers never reopen a path by name mid-scan. The
    test pins that _read_file honours the cache and that the cache is
    per-thread state that clears cleanly.
    """
    import compliance_check as cc

    abs_path = "/anywhere/pinned.py"
    # No scan in progress: cache is absent, so a real (missing) file is None.
    cc._scan.content = None
    assert cc._read_file("/does/not/exist/x.py") is None

    # Simulate an in-progress scan: a hit is served verbatim, even for a path
    # that does not exist on disk, proving the value came from the cache.
    cc._scan.content = {abs_path: "CACHED-SENTINEL"}
    try:
        assert cc._read_file(abs_path) == "CACHED-SENTINEL"
        # A miss inside a scan still falls back to the guard (None for a
        # nonexistent file), not to an empty string.
        assert cc._read_file("/does/not/exist/y.py") is None
    finally:
        cc._scan.content = None


def test_compliance_scan_clears_its_cache_after_running():
    """assess_compliance must not leak cached file content past the scan."""
    import os
    import compliance_check as cc

    if not os.path.isdir("examples/cv-screening-app"):
        return  # example not present in this checkout
    cc.assess_compliance("examples/cv-screening-app")
    assert getattr(cc._scan, "content", None) is None, (
        "the per-scan content cache must be cleared once assess returns"
    )
