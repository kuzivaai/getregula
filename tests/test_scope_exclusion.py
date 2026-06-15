"""Tests for the file-path exclusion layer (Session 17, item 1A).

Tests the tier-aware production-scope filter that excludes non-production
files while preserving prohibited and credential_exposure findings.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from report import classify_provenance
from cli_scan import _should_exclude_for_production_scope


# =========================================================================
# classify_provenance tests
# =========================================================================

class TestClassifyProvenance:
    """Test that file paths are classified into the correct provenance."""

    # --- Test files ---
    def test_test_file_by_name(self):
        assert classify_provenance(Path("src/test_scoring.py")) == "test"

    def test_test_file_by_dir(self):
        assert classify_provenance(Path("tests/unit/test_main.py")) == "test"

    def test_conftest(self):
        assert classify_provenance(Path("tests/conftest.py")) == "test"

    def test_spec_file(self):
        assert classify_provenance(Path("src/app.spec.ts")) == "test"

    def test_jest_test(self):
        assert classify_provenance(Path("src/app.test.js")) == "test"

    def test_nested_test_dir(self):
        assert classify_provenance(Path("lib/crewai/tests/cli/tools/test_main.py")) == "test"

    def test_standard_tests_dir(self):
        assert classify_provenance(Path("libs/standard-tests/tests/unit_tests/test_decorated_tool.py")) == "test"

    # --- Example files ---
    def test_examples_dir(self):
        assert classify_provenance(Path("examples/logfire-fastapi/server.py")) == "example"

    def test_demo_dir(self):
        assert classify_provenance(Path("demo/app.py")) == "example"

    def test_cookbook_dir(self):
        assert classify_provenance(Path("cookbook/rag/main.py")) == "example"

    # --- Tooling files ---
    def test_setup_py(self):
        assert classify_provenance(Path("setup.py")) == "tooling"

    def test_setup_cfg(self):
        assert classify_provenance(Path("setup.cfg")) == "tooling"

    def test_init_py(self):
        assert classify_provenance(Path("deepface/__init__.py")) == "tooling"

    def test_dockerfile(self):
        assert classify_provenance(Path("Dockerfile")) == "tooling"

    def test_github_workflow(self):
        assert classify_provenance(Path(".github/workflows/ci.yml")) == "tooling"

    def test_noxfile(self):
        assert classify_provenance(Path("noxfile.py")) == "tooling"

    # --- Documentation ---
    def test_docs_conf_py(self):
        assert classify_provenance(Path("docs/conf.py")) == "documentation"

    def test_markdown_file(self):
        assert classify_provenance(Path("docs/guide.md")) == "documentation"

    def test_rst_file(self):
        assert classify_provenance(Path("docs/api.rst")) == "documentation"

    # --- Production (must NOT be excluded) ---
    def test_production_python(self):
        assert classify_provenance(Path("deepface/modules/verification.py")) == "production"

    def test_production_api(self):
        assert classify_provenance(Path("deepface/api/src/app.py")) == "production"

    def test_production_model(self):
        assert classify_provenance(Path("deepface/models/facial_recognition/ArcFace.py")) == "production"

    def test_production_notebook(self):
        assert classify_provenance(Path("notebooks/3_pd_modeling.ipynb")) == "production"

    def test_production_database(self):
        assert classify_provenance(Path("deepface/modules/database/milvus.py")) == "production"

    def test_production_cli(self):
        assert classify_provenance(Path("face_recognition/face_detection_cli.py")) == "production"

    def test_pyproject_toml_is_production(self):
        """pyproject.toml is exempted from the .toml→tooling rule."""
        assert classify_provenance(Path("pyproject.toml")) == "production"

    # --- Type directories and utilities ---
    def test_types_dir_tooling(self):
        assert classify_provenance(Path("src/openai/types/beta/params.py")) == "tooling"

    def test_utils_dir_tooling(self):
        assert classify_provenance(Path("src/openai/_utils/_logs.py")) == "tooling"


# =========================================================================
# _should_exclude_for_production_scope tests
# =========================================================================

class TestShouldExcludeForProductionScope:
    """Test the tier-aware scope filter."""

    # --- Never exclude prohibited ---
    def test_prohibited_in_test_file(self):
        """A prohibited practice in a test file must still be flagged."""
        finding = {"tier": "prohibited", "provenance": "test", "file": "tests/test_social_scoring.py"}
        assert _should_exclude_for_production_scope(finding) is False

    def test_prohibited_in_setup_py(self):
        finding = {"tier": "prohibited", "provenance": "tooling", "file": "setup.py"}
        assert _should_exclude_for_production_scope(finding) is False

    # --- Never exclude credential_exposure ---
    def test_credential_in_test(self):
        """Real credentials in test files are genuinely dangerous."""
        finding = {"tier": "credential_exposure", "provenance": "test", "file": "tests/conftest.py"}
        assert _should_exclude_for_production_scope(finding) is False

    # --- __init__.py: tier-dependent ---
    def test_init_minimal_risk_excluded(self):
        """__init__.py excluded for minimal_risk (pure re-exports)."""
        finding = {"tier": "minimal_risk", "provenance": "tooling", "file": "sklearn/datasets/__init__.py"}
        assert _should_exclude_for_production_scope(finding) is True

    def test_init_high_risk_not_excluded(self):
        """__init__.py NOT excluded for high_risk (can wire biometric pipelines)."""
        finding = {"tier": "high_risk", "provenance": "tooling", "file": "deepface/__init__.py"}
        assert _should_exclude_for_production_scope(finding) is False

    def test_init_agent_autonomy_not_excluded(self):
        finding = {"tier": "agent_autonomy", "provenance": "tooling", "file": "crewai/__init__.py"}
        assert _should_exclude_for_production_scope(finding) is False

    def test_types_dir_minimal_risk_excluded(self):
        finding = {"tier": "minimal_risk", "provenance": "tooling", "file": "src/openai/types/image.py"}
        assert _should_exclude_for_production_scope(finding) is True

    def test_types_dir_high_risk_not_excluded(self):
        """types/ dir NOT excluded for high_risk — could contain validation logic."""
        finding = {"tier": "high_risk", "provenance": "tooling", "file": "src/types/risk_model.py"}
        assert _should_exclude_for_production_scope(finding) is False

    def test_utils_dir_minimal_risk_excluded(self):
        finding = {"tier": "minimal_risk", "provenance": "tooling", "file": "src/openai/_utils/_logs.py"}
        assert _should_exclude_for_production_scope(finding) is True

    # --- Standard exclusions ---
    def test_test_file_minimal_risk_excluded(self):
        finding = {"tier": "minimal_risk", "provenance": "test", "file": "tests/test_utils.py"}
        assert _should_exclude_for_production_scope(finding) is True

    def test_test_file_high_risk_excluded(self):
        finding = {"tier": "high_risk", "provenance": "test", "file": "tests/test_eval.py"}
        assert _should_exclude_for_production_scope(finding) is True

    def test_test_file_agent_autonomy_excluded(self):
        finding = {"tier": "agent_autonomy", "provenance": "test", "file": "tests/test_linter.py"}
        assert _should_exclude_for_production_scope(finding) is True

    def test_setup_py_high_risk_excluded(self):
        finding = {"tier": "high_risk", "provenance": "tooling", "file": "setup.py"}
        assert _should_exclude_for_production_scope(finding) is True

    def test_docs_conf_excluded(self):
        finding = {"tier": "high_risk", "provenance": "documentation", "file": "docs/conf.py"}
        assert _should_exclude_for_production_scope(finding) is True

    def test_example_agent_autonomy_excluded(self):
        finding = {"tier": "agent_autonomy", "provenance": "example", "file": "examples/demo.py"}
        assert _should_exclude_for_production_scope(finding) is True

    # --- Example files: tier-dependent ---
    def test_example_minimal_risk_not_excluded(self):
        """Example code demonstrating real AI usage should be flagged."""
        finding = {"tier": "minimal_risk", "provenance": "example", "file": "examples/demo.py"}
        assert _should_exclude_for_production_scope(finding) is False

    def test_example_high_risk_excluded(self):
        """High-risk finding in example code is less actionable."""
        finding = {"tier": "high_risk", "provenance": "example", "file": "examples/demo.py"}
        assert _should_exclude_for_production_scope(finding) is True

    # --- Production files NEVER excluded ---
    def test_production_not_excluded(self):
        finding = {"tier": "high_risk", "provenance": "production", "file": "deepface/verification.py"}
        assert _should_exclude_for_production_scope(finding) is False

    def test_production_minimal_not_excluded(self):
        finding = {"tier": "minimal_risk", "provenance": "production", "file": "src/app.py"}
        assert _should_exclude_for_production_scope(finding) is False

    # --- Adversarial: production file under near-miss path ---
    def test_testing_utils_production_not_excluded(self):
        """A file named 'testing_utils.py' in a production path is NOT a test file."""
        # This depends on classify_provenance — testing_utils.py doesn't match
        # test_ prefix or tests/ dir, so provenance should be "production"
        provenance = classify_provenance(Path("src/testing_utils.py"))
        finding = {"tier": "high_risk", "provenance": provenance, "file": "src/testing_utils.py"}
        assert _should_exclude_for_production_scope(finding) is False

    def test_test_in_production_dir(self):
        """A file with 'test' in its name but NOT matching test patterns."""
        # "contest.py" or "latest.py" should not be matched
        provenance = classify_provenance(Path("src/contest.py"))
        assert provenance == "production"


# =========================================================================
# Integration: verify zero TP suppression on known data
# =========================================================================

def test_provenance_classification_counts():
    """Verify the provenance distribution matches Session 16's analysis.

    This is a design-validation test, not an independent precision measurement.
    It confirms the exclusion rules match the patterns they were designed for.
    """
    import json
    blind_path = Path(__file__).resolve().parent.parent / "benchmarks" / "rater1_blind_subset.json"
    if not blind_path.exists():
        return  # skip if labelling not yet done

    with open(blind_path) as f:
        data = json.load(f)

    # Count how many FP entries would be excluded
    excluded_fps = 0
    suppressed_tps = 0
    for entry in data["labels"]:
        filepath = entry.get("file", "")
        provenance = classify_provenance(Path(filepath))
        finding = {
            "tier": entry.get("tier", ""),
            "provenance": provenance,
            "file": filepath,
        }
        if _should_exclude_for_production_scope(finding):
            if entry.get("label") == "fp":
                excluded_fps += 1
            elif entry.get("label") == "tp":
                suppressed_tps += 1

    # The critical invariant: zero TPs suppressed
    assert suppressed_tps == 0, f"CRITICAL: {suppressed_tps} true positives would be suppressed!"
    # Design validation: file-path exclusion catches the test/tooling/docs FPs.
    # The remaining FPs (vocabulary mismatches, wrong categories) require
    # different techniques (items 1B/1C/2B) and are out of scope here.
    assert excluded_fps >= 18, f"Expected >=18 FPs excluded, got {excluded_fps}"
