"""Tests for first-run experience (verdict + next steps)."""
import sys
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))


def test_check_output_contains_verdict(tmp_path):
    """regula check text output should contain a Verdict line."""
    (tmp_path / "app.py").write_text("import openai\nclient = openai.OpenAI()")
    result = subprocess.run(
        [sys.executable, "-m", "scripts.cli", "check", str(tmp_path)],
        capture_output=True, text=True,
        cwd=str(Path(__file__).resolve().parent.parent),
    )
    assert "Verdict" in result.stdout, f"No Verdict in output: {result.stdout[:500]}"


def test_check_output_contains_next_steps(tmp_path):
    """regula check text output should contain Next steps."""
    (tmp_path / "app.py").write_text("import openai\nclient = openai.OpenAI()")
    result = subprocess.run(
        [sys.executable, "-m", "scripts.cli", "check", str(tmp_path)],
        capture_output=True, text=True,
        cwd=str(Path(__file__).resolve().parent.parent),
    )
    assert "Next steps" in result.stdout, f"No Next steps in output: {result.stdout[:500]}"


def test_check_no_ai_shows_no_ai_detected(tmp_path):
    """A project with no AI should show NO AI DETECTED verdict."""
    (tmp_path / "hello.py").write_text("print('hello world')")
    result = subprocess.run(
        [sys.executable, "-m", "scripts.cli", "check", str(tmp_path)],
        capture_output=True, text=True,
        cwd=str(Path(__file__).resolve().parent.parent),
    )
    assert "NO AI DETECTED" in result.stdout or "MINIMAL" in result.stdout


def test_check_json_no_verdict():
    """JSON output should NOT contain verdict text (it's data, not narrative)."""
    result = subprocess.run(
        [sys.executable, "-m", "scripts.cli", "check", ".", "--format", "json"],
        capture_output=True, text=True,
        cwd=str(Path(__file__).resolve().parent.parent),
    )
    assert "Verdict" not in result.stdout
