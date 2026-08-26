"""Tests for first-run experience (verdict + next steps)."""
import sys
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))


def test_check_output_contains_resolvable_decision(tmp_path):
    """A detector match without declared facts must request those facts."""
    (tmp_path / "app.py").write_text("import openai\nclient = openai.OpenAI()")
    result = subprocess.run(
        [sys.executable, "-m", "scripts.cli", "check", str(tmp_path)],
        capture_output=True, text=True,
        cwd=str(Path(__file__).resolve().parent.parent),
    )
    assert result.returncode == 0, result.stderr
    assert "Decision: insufficient_information" in result.stdout
    assert "Facts needed to resolve the next decision:" in result.stdout
    assert "is_ai_system:" in result.stdout
    assert "jurisdiction_in_scope:" in result.stdout
    assert "Verdict" not in result.stdout


def test_check_output_contains_next_steps(tmp_path):
    """regula check text output should contain Next steps."""
    (tmp_path / "app.py").write_text("import openai\nclient = openai.OpenAI()")
    result = subprocess.run(
        [sys.executable, "-m", "scripts.cli", "check", str(tmp_path)],
        capture_output=True, text=True,
        cwd=str(Path(__file__).resolve().parent.parent),
    )
    assert "Next steps" in result.stdout, f"No Next steps in output: {result.stdout[:500]}"


def test_check_no_detector_match_does_not_become_outside_scope(tmp_path):
    """No detector match is not evidence that the legal scope predicates fail."""
    (tmp_path / "hello.py").write_text("print('hello world')")
    result = subprocess.run(
        [sys.executable, "-m", "scripts.cli", "check", str(tmp_path)],
        capture_output=True, text=True,
        cwd=str(Path(__file__).resolve().parent.parent),
    )
    assert result.returncode == 0, result.stderr
    assert "Decision: insufficient_information" in result.stdout
    assert "NO AI DETECTED" not in result.stdout
    assert "MINIMAL" not in result.stdout
    assert "is_ai_system:" in result.stdout


def test_check_json_no_verdict():
    """JSON output should NOT contain verdict text (it's data, not narrative)."""
    result = subprocess.run(
        [sys.executable, "-m", "scripts.cli", "check", ".", "--format", "json"],
        capture_output=True, text=True,
        cwd=str(Path(__file__).resolve().parent.parent),
    )
    assert "Verdict" not in result.stdout
