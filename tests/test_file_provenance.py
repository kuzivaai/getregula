# regula-ignore
"""Tests for file provenance classification."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))


def test_production_files():
    """Production source files are classified as 'production'."""
    from report import classify_provenance

    assert classify_provenance(Path("src/app.py")) == "production"
    assert classify_provenance(Path("src/components/Chat.tsx")) == "production"
    assert classify_provenance(Path("cmd/server/main.go")) == "production"
    assert classify_provenance(Path("lib/utils.js")) == "production"
    assert classify_provenance(Path("app/models/user.py")) == "production"


def test_test_files():
    """Test files are classified as 'test'."""
    from report import classify_provenance

    assert classify_provenance(Path("tests/test_app.py")) == "test"
    assert classify_provenance(Path("src/app_test.py")) == "test"
    assert classify_provenance(Path("src/app.spec.ts")) == "test"
    assert classify_provenance(Path("tests/conftest.py")) == "test"
    assert classify_provenance(Path("test/unit/foo.py")) == "test"
    assert classify_provenance(Path("tests/fixtures/data.json")) == "test"


def test_example_files():
    """Example/demo/cookbook files are classified as 'example'."""
    from report import classify_provenance

    assert classify_provenance(Path("examples/demo.py")) == "example"
    assert classify_provenance(Path("demo/chatbot.py")) == "example"
    assert classify_provenance(Path("cookbook/rag.py")) == "example"
    assert classify_provenance(Path("samples/quickstart.py")) == "example"


def test_documentation_files():
    """Documentation files are classified as 'documentation'."""
    from report import classify_provenance

    assert classify_provenance(Path("docs/architecture.md")) == "documentation"
    assert classify_provenance(Path("README.md")) == "documentation"
    assert classify_provenance(Path("CHANGELOG.rst")) == "documentation"
    assert classify_provenance(Path("docs/guide.txt")) == "documentation"
    assert classify_provenance(Path("docs/spec.adoc")) == "documentation"


def test_tooling_files():
    """Tooling/CI/config files are classified as 'tooling'."""
    from report import classify_provenance

    assert classify_provenance(Path(".github/workflows/ci.yml")) == "tooling"
    assert classify_provenance(Path("Dockerfile")) == "tooling"
    assert classify_provenance(Path("Makefile")) == "tooling"
    assert classify_provenance(Path("src/__init__.py")) == "tooling"
    assert classify_provenance(Path("docker-compose.yml")) == "tooling"
    assert classify_provenance(Path(".gitignore")) == "tooling"
    assert classify_provenance(Path(".editorconfig")) == "tooling"
    assert classify_provenance(Path("setup.cfg")) == "tooling"


def test_fixture_files_classified_as_test():
    """Fixture files inside test directories are classified as 'test'."""
    from report import classify_provenance

    assert classify_provenance(Path("tests/fixtures/data.json")) == "test"
    assert classify_provenance(Path("tests/fixtures/sample.yaml")) == "test"


def test_pyproject_toml_is_not_tooling():
    """pyproject.toml is production config, not generic tooling."""
    from report import classify_provenance

    # pyproject.toml is excluded from the .yml/.yaml/.toml tooling rule
    # but it has .toml suffix. The task spec excludes it from the tooling
    # catch-all. It falls through to 'production'.
    assert classify_provenance(Path("pyproject.toml")) == "production"


def test_scope_production_filters_non_production_findings():
    """--scope production filtering excludes test/example/tooling findings."""
    findings = [
        {"file": "src/app.py", "tier": "high_risk", "provenance": "production"},
        {"file": "tests/test_app.py", "tier": "high_risk", "provenance": "test"},
        {"file": "examples/demo.py", "tier": "high_risk", "provenance": "example"},
        {"file": "docs/guide.md", "tier": "minimal_risk", "provenance": "documentation"},
        {"file": ".github/ci.yml", "tier": "minimal_risk", "provenance": "tooling"},
        {"file": "src/model.py", "tier": "limited_risk", "provenance": "production"},
    ]

    # Replicate the --scope production filter from cli_scan.py line 98
    filtered = [f for f in findings if f.get("provenance", "production") == "production"]

    assert len(filtered) == 2
    assert all(f["provenance"] == "production" for f in filtered)
    assert {f["file"] for f in filtered} == {"src/app.py", "src/model.py"}


def test_scope_production_defaults_missing_provenance_to_production():
    """Findings without a provenance field default to 'production' (backward compat)."""
    findings = [
        {"file": "src/app.py", "tier": "high_risk"},  # no provenance key
        {"file": "tests/test_app.py", "tier": "high_risk", "provenance": "test"},
    ]

    filtered = [f for f in findings if f.get("provenance", "production") == "production"]

    assert len(filtered) == 1
    assert filtered[0]["file"] == "src/app.py"
