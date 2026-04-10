"""CLI integration tests — exercise top commands via subprocess."""
import subprocess
import sys
import tempfile

import pytest


def run_cli(*args):
    """Run regula CLI and return (returncode, stdout, stderr)."""
    result = subprocess.run(
        [sys.executable, "-m", "scripts.cli"] + list(args),
        capture_output=True, text=True, timeout=60,
        cwd=str(__import__("pathlib").Path(__file__).resolve().parents[1]),
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


def test_empty_directory():
    with tempfile.TemporaryDirectory() as tmp:
        rc, out, err = run_cli("check", tmp)
        assert rc == 0  # should not crash on empty dir
