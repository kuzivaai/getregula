"""Tests for lifecycle phase visibility in output."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)


def _write_ai_code(directory):
    """Write AI code that triggers high-risk findings."""
    (directory / "app.py").write_text(
        "import openai\n"
        "client = openai.OpenAI()\n"
        "result = client.chat.completions.create(model='gpt-4', messages=[])\n"
        "# hiring decision system\n"
        "def evaluate_candidate(resume):\n"
        "    score = client.chat.completions.create(model='gpt-4', messages=[{'role': 'user', 'content': resume}])\n"
        "    return score\n"
    )


def test_check_text_output_contains_lifecycle(tmp_path):
    """Text output should show lifecycle phase tags."""
    src = tmp_path / "src"
    src.mkdir()
    _write_ai_code(src)
    result = subprocess.run(
        [sys.executable, "-m", "scripts.cli", "check", str(src), "--no-skip-tests"],
        capture_output=True, text=True,
        cwd=PROJECT_ROOT,
    )
    # Should contain at least one lifecycle tag in square brackets
    assert "[develop]" in result.stdout or "[deploy]" in result.stdout or "[plan]" in result.stdout, \
        f"No lifecycle tag found in output: {result.stdout[:500]}"


def test_lifecycle_summary_in_header(tmp_path):
    """Scan header should include a Lifecycle: summary line."""
    src = tmp_path / "src"
    src.mkdir()
    _write_ai_code(src)
    result = subprocess.run(
        [sys.executable, "-m", "scripts.cli", "check", str(src), "--no-skip-tests"],
        capture_output=True, text=True,
        cwd=PROJECT_ROOT,
    )
    assert "Lifecycle:" in result.stdout, \
        f"No Lifecycle summary found in output: {result.stdout[:500]}"


def test_lifecycle_filter_reduces_findings(tmp_path):
    """--lifecycle flag should filter to only matching findings."""
    src = tmp_path / "src"
    src.mkdir()
    _write_ai_code(src)
    # Get all findings count
    result_all = subprocess.run(
        [sys.executable, "-m", "scripts.cli", "check", str(src), "--no-skip-tests", "--format", "json"],
        capture_output=True, text=True,
        cwd=PROJECT_ROOT,
    )
    # Get filtered findings (plan phase has fewer findings than develop)
    result_filtered = subprocess.run(
        [sys.executable, "-m", "scripts.cli", "check", str(src), "--no-skip-tests",
         "--lifecycle", "plan", "--format", "json"],
        capture_output=True, text=True,
        cwd=PROJECT_ROOT,
    )
    all_findings = json.loads(result_all.stdout)["data"]
    filtered_findings = json.loads(result_filtered.stdout)["data"]
    # Filtered should be <= all (plan phase has fewer findings than develop)
    assert len(filtered_findings) <= len(all_findings)
    # All filtered findings should include "plan" in their lifecycle_phases
    for f in filtered_findings:
        assert "plan" in f.get("lifecycle_phases", []), \
            f"Finding {f.get('file')} does not have 'plan' phase"


def test_lifecycle_filter_retire_empty(tmp_path):
    """--lifecycle retire should return no findings for typical AI code."""
    src = tmp_path / "src"
    src.mkdir()
    _write_ai_code(src)
    result = subprocess.run(
        [sys.executable, "-m", "scripts.cli", "check", str(src), "--no-skip-tests",
         "--lifecycle", "retire", "--format", "json"],
        capture_output=True, text=True,
        cwd=PROJECT_ROOT,
    )
    findings = json.loads(result.stdout)["data"]
    assert len(findings) == 0, \
        f"Expected no findings for 'retire' phase, got {len(findings)}"


def test_json_output_unaffected(tmp_path):
    """JSON output should still have lifecycle_phases as list."""
    src = tmp_path / "src"
    src.mkdir()
    _write_ai_code(src)
    result = subprocess.run(
        [sys.executable, "-m", "scripts.cli", "check", str(src), "--no-skip-tests", "--format", "json"],
        capture_output=True, text=True,
        cwd=PROJECT_ROOT,
    )
    data = json.loads(result.stdout)
    findings = data["data"]
    assert len(findings) > 0, "Expected at least one finding"
    for f in findings[:5]:
        assert isinstance(f.get("lifecycle_phases"), list), "lifecycle_phases should be a list in JSON"
