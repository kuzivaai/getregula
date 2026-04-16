"""CLI integration tests — exercise top commands via subprocess."""
import os
import subprocess
import sys
import tempfile

import pytest


def run_cli(*args, env_overrides=None):
    """Run regula CLI and return (returncode, stdout, stderr)."""
    env = os.environ.copy()
    if env_overrides:
        env.update(env_overrides)
    result = subprocess.run(
        [sys.executable, "-m", "scripts.cli"] + list(args),
        capture_output=True, text=True, timeout=60,
        cwd=str(__import__("pathlib").Path(__file__).resolve().parents[1]),
        env=env,
    )
    return result.returncode, result.stdout, result.stderr


def test_check_sample_high_risk():
    rc, out, err = run_cli("check", "tests/fixtures/sample_high_risk")
    assert rc == 0
    assert "high" in out.lower() or "findings" in out.lower() or "risk" in out.lower()


def test_assess_auto():
    rc, out, err = run_cli("assess", "--answers", "yes,yes,no,yes,no")
    assert rc == 0
    assert "high" in out.lower() or "risk" in out.lower()


def test_plan():
    rc, out, err = run_cli("plan", "--project", "tests/fixtures/sample_high_risk")
    assert rc == 0


def test_gap():
    rc, out, err = run_cli("gap", "--project", "tests/fixtures/sample_high_risk")
    assert rc == 0
    assert "Art" in out or "article" in out.lower()


def test_self_test():
    rc, out, err = run_cli("self-test")
    assert rc == 0
    assert "passed" in out.lower() or "pass" in out.lower()


def test_doctor():
    rc, out, err = run_cli("doctor")
    assert rc == 0
    assert "passed" in out.lower() or "pass" in out.lower()


def test_sbom():
    rc, out, err = run_cli("sbom")
    assert rc == 0


def test_handoff_garak():
    rc, out, err = run_cli("handoff", "garak", "tests/fixtures/sample_high_risk")
    assert rc == 0


def test_regwatch():
    rc, out, err = run_cli("regwatch")
    assert rc == 0


def test_inventory():
    rc, out, err = run_cli("inventory", "tests/fixtures/sample_high_risk")
    assert rc == 0


def test_governance(tmp_path):
    out = tmp_path / "AI_GOVERNANCE.md"
    rc, stdout, stderr = run_cli("governance", "--project", "tests/fixtures/sample_high_risk", "--output", str(out))
    assert rc == 0
    assert out.exists()
    content = out.read_text()
    assert "AI Governance" in content or "governance" in content.lower()
    assert "scaffold" in content.lower() or "TO BE COMPLETED" in content


def test_model_card(tmp_path):
    out = tmp_path / "MODEL_CARD.md"
    rc, stdout, stderr = run_cli("model-card", "--project", "tests/fixtures/sample_high_risk", "--output", str(out))
    assert rc == 0
    assert out.exists()
    content = out.read_text()
    assert "Model Card" in content or "model" in content.lower()


def test_governance_empty_project(tmp_path):
    out = tmp_path / "AI_GOVERNANCE.md"
    empty = tmp_path / "empty_proj"
    empty.mkdir()
    rc, stdout, stderr = run_cli("governance", "--project", str(empty), "--output", str(out))
    assert rc == 0
    assert out.exists()  # should produce valid scaffold even for empty project


def test_model_card_empty_project(tmp_path):
    out = tmp_path / "MODEL_CARD.md"
    empty = tmp_path / "empty_proj"
    empty.mkdir()
    rc, stdout, stderr = run_cli("model-card", "--project", str(empty), "--output", str(out))
    assert rc == 0
    assert out.exists()


def test_empty_directory():
    with tempfile.TemporaryDirectory() as tmp:
        rc, out, err = run_cli("check", tmp)
        assert rc == 0  # should not crash on empty dir


def test_github_annotations_emitted_under_github_actions():
    """With GITHUB_ACTIONS=true and --ci, each finding gets a workflow command.

    This lets CI surface findings as inline PR annotations without needing
    SARIF/CodeQL setup. Uses the real high-risk cv-screening-app fixture so
    the test is grounded in the actual Regula output — no fabricated messages.
    """
    rc, stdout, stderr = run_cli(
        "check", "--ci", "examples/cv-screening-app",
        env_overrides={"GITHUB_ACTIONS": "true"},
    )
    # CI mode exits 1 on WARN or BLOCK findings.
    assert rc == 1, f"expected rc=1 (WARN in CI mode), got {rc}\nstderr={stderr}"
    # Exactly one high-risk WARN finding expected for cv-screening-app.
    warning_lines = [ln for ln in stdout.splitlines() if ln.startswith("::warning")]
    assert len(warning_lines) == 1, f"expected 1 ::warning, got {len(warning_lines)}\nstdout={stdout}"
    ann = warning_lines[0]
    # Path must resolve to the file inside the scanned project, not just `app.py`.
    assert "file=examples/cv-screening-app/app.py" in ann, ann
    assert ",line=" in ann, ann
    # Message content must match what the scanner actually produced.
    assert "Employment" in ann, ann


def test_github_annotations_suppressed_without_github_actions():
    """Without GITHUB_ACTIONS=true, --ci mode does NOT emit workflow commands.

    Local runs should stay quiet so a developer running `regula check --ci`
    at their terminal isn't spammed with ::warning lines.
    """
    rc, stdout, stderr = run_cli(
        "check", "--ci", "examples/cv-screening-app",
        env_overrides={"GITHUB_ACTIONS": ""},
    )
    assert rc == 1
    assert not any(
        ln.startswith("::warning") or ln.startswith("::error") or ln.startswith("::notice")
        for ln in stdout.splitlines()
    ), f"expected zero workflow commands, got stdout={stdout}"


def test_github_annotations_suppressed_without_ci_flag():
    """GITHUB_ACTIONS=true without --ci should not emit annotations either.

    Annotations are a CI-mode-only feature — the `regula check` default is
    reserved for the human-readable report.
    """
    rc, stdout, stderr = run_cli(
        "check", "examples/cv-screening-app",
        env_overrides={"GITHUB_ACTIONS": "true"},
    )
    # No --ci means WARN does not fail the run.
    assert rc == 0
    assert not any(
        ln.startswith("::warning") or ln.startswith("::error") or ln.startswith("::notice")
        for ln in stdout.splitlines()
    ), f"expected zero workflow commands, got stdout={stdout}"
