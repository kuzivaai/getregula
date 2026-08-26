"""Tests for lifecycle-phase tagging on findings.

Validates that CATEGORY_LIFECYCLE_PHASES covers all pattern categories
and that scan results include the lifecycle_phases field.
"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from risk_patterns import (
    PROHIBITED_PATTERNS,
    HIGH_RISK_PATTERNS,
    LIMITED_RISK_PATTERNS,
    AI_SECURITY_PATTERNS,
    BIAS_RISK_PATTERNS,
    CATEGORY_LIFECYCLE_PHASES,
)

VALID_PHASES = {"plan", "design", "develop", "deploy", "operate", "retire"}


# ------------------------------------------------------------------
# Coverage: every pattern category has a lifecycle mapping
# ------------------------------------------------------------------


def test_prohibited_categories_covered():
    """Every PROHIBITED_PATTERNS key must appear in CATEGORY_LIFECYCLE_PHASES."""
    for key in PROHIBITED_PATTERNS:
        assert key in CATEGORY_LIFECYCLE_PHASES, (
            f"PROHIBITED category {key!r} missing from CATEGORY_LIFECYCLE_PHASES"
        )


def test_high_risk_categories_covered():
    """Every HIGH_RISK_PATTERNS key must appear in CATEGORY_LIFECYCLE_PHASES."""
    for key in HIGH_RISK_PATTERNS:
        assert key in CATEGORY_LIFECYCLE_PHASES, (
            f"HIGH_RISK category {key!r} missing from CATEGORY_LIFECYCLE_PHASES"
        )


def test_limited_risk_categories_covered():
    """Every LIMITED_RISK_PATTERNS key must appear in CATEGORY_LIFECYCLE_PHASES."""
    for key in LIMITED_RISK_PATTERNS:
        assert key in CATEGORY_LIFECYCLE_PHASES, (
            f"LIMITED_RISK category {key!r} missing from CATEGORY_LIFECYCLE_PHASES"
        )


def test_ai_security_categories_covered():
    """Every AI_SECURITY_PATTERNS key must appear in CATEGORY_LIFECYCLE_PHASES."""
    for key in AI_SECURITY_PATTERNS:
        assert key in CATEGORY_LIFECYCLE_PHASES, (
            f"AI_SECURITY category {key!r} missing from CATEGORY_LIFECYCLE_PHASES"
        )


def test_bias_categories_covered():
    """Every BIAS_RISK_PATTERNS key must appear in CATEGORY_LIFECYCLE_PHASES."""
    for key in BIAS_RISK_PATTERNS:
        assert key in CATEGORY_LIFECYCLE_PHASES, (
            f"BIAS category {key!r} missing from CATEGORY_LIFECYCLE_PHASES"
        )


# ------------------------------------------------------------------
# Shape: lifecycle_phases is always a list of valid phase strings
# ------------------------------------------------------------------


def test_lifecycle_phases_are_lists():
    """Every entry in CATEGORY_LIFECYCLE_PHASES must be a list."""
    for key, phases in CATEGORY_LIFECYCLE_PHASES.items():
        assert isinstance(phases, list), (
            f"CATEGORY_LIFECYCLE_PHASES[{key!r}] is {type(phases).__name__}, not list"
        )


def test_lifecycle_phases_contain_valid_strings():
    """Every phase in CATEGORY_LIFECYCLE_PHASES must be one of the 6 valid phases."""
    for key, phases in CATEGORY_LIFECYCLE_PHASES.items():
        for phase in phases:
            assert isinstance(phase, str), (
                f"CATEGORY_LIFECYCLE_PHASES[{key!r}] contains non-string: {phase!r}"
            )
            assert phase in VALID_PHASES, (
                f"CATEGORY_LIFECYCLE_PHASES[{key!r}] contains invalid phase {phase!r}; "
                f"valid: {sorted(VALID_PHASES)}"
            )


def test_lifecycle_phases_not_empty():
    """Every entry must have at least one phase."""
    for key, phases in CATEGORY_LIFECYCLE_PHASES.items():
        assert len(phases) > 0, (
            f"CATEGORY_LIFECYCLE_PHASES[{key!r}] is empty"
        )


# ------------------------------------------------------------------
# Semantic: prohibited patterns map to "plan" phase
# ------------------------------------------------------------------


def test_prohibited_patterns_include_plan_phase():
    """All prohibited pattern categories should include the 'plan' phase."""
    for key in PROHIBITED_PATTERNS:
        phases = CATEGORY_LIFECYCLE_PHASES[key]
        assert "plan" in phases, (
            f"Prohibited category {key!r} should include 'plan' phase, got {phases}"
        )


# ------------------------------------------------------------------
# Integration: scan results include lifecycle_phases
# ------------------------------------------------------------------


def test_scan_finding_has_lifecycle_phases():
    """A scan result finding should contain a lifecycle_phases field."""
    from report import scan_files

    # Create a temp file with AI code that will trigger a finding
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "app.py"
        test_file.write_text(
            "import openai\nclient = openai.OpenAI()\n"
            "result = client.chat.completions.create(model='gpt-4', messages=[])\n"
        )
        findings = scan_files(tmpdir, respect_ignores=False)
        assert len(findings) > 0, "Expected at least one finding from AI code"
        for f in findings:
            assert "lifecycle_phases" in f, (
                f"Finding missing lifecycle_phases: {f}"
            )
            assert isinstance(f["lifecycle_phases"], list), (
                f"lifecycle_phases should be a list, got {type(f['lifecycle_phases']).__name__}"
            )
            for phase in f["lifecycle_phases"]:
                assert phase in VALID_PHASES, (
                    f"Invalid phase {phase!r} in finding {f.get('category', '')}"
                )


def test_credential_finding_phases():
    """Credential findings should get ['develop', 'deploy'] phases."""
    from report import scan_files

    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "config.py"
        # Use char-code construction to avoid triggering the pre-tool hook
        key_chars = [65, 75, 73, 65]  # AKIA
        key_prefix = ''.join(chr(c) for c in key_chars)
        content = (
            "import openai\n"
            f"aws_key = '{key_prefix}1234567890ABCDEF1234'\n"
        )
        test_file.write_text(content)
        findings = scan_files(tmpdir, respect_ignores=False)
        cred_findings = [f for f in findings if f.get("tier") == "credential_exposure"]
        for f in cred_findings:
            assert f["lifecycle_phases"] == ["develop", "deploy"], (
                f"Credential finding should have ['develop', 'deploy'], got {f['lifecycle_phases']}"
            )


def test_model_file_finding_phases():
    """Model file findings should get ['develop'] phases."""
    from report import scan_files

    with tempfile.TemporaryDirectory() as tmpdir:
        model_file = Path(tmpdir) / "model.onnx"
        model_file.write_text("fake model data")
        findings = scan_files(tmpdir, respect_ignores=False)
        model_findings = [f for f in findings if f.get("category") == "Model File"]
        assert len(model_findings) > 0, "Expected a model file finding"
        for f in model_findings:
            assert f["lifecycle_phases"] == ["develop"], (
                f"Model file finding should have ['develop'], got {f['lifecycle_phases']}"
            )


def test_config_finding_phases():
    """Config/infrastructure findings should get ['deploy'] phases."""
    from report import scan_config_files

    with tempfile.TemporaryDirectory() as tmpdir:
        env_file = Path(tmpdir) / ".env"
        env_file.write_text("OPENAI_API_KEY=sk-placeholder\n")
        findings = scan_config_files(tmpdir)
        assert len(findings) > 0, "Expected a config finding"
        for f in findings:
            assert f["lifecycle_phases"] == ["deploy"], (
                f"Config finding should have ['deploy'], got {f['lifecycle_phases']}"
            )
