"""Regression coverage for the no-subcommand CLI decision path."""

import subprocess
import sys
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
CLI = REPO_ROOT / "scripts" / "cli.py"


def test_bare_scan_requires_facts_before_decision_claims():
    """Detector observations alone cannot become a tier or readiness score."""
    with tempfile.TemporaryDirectory() as project:
        Path(project, "app.py").write_text(
            "import openai\nclient = openai.OpenAI()\n",
            encoding="utf-8",
        )
        result = subprocess.run(
            [sys.executable, str(CLI)],
            cwd=project,
            capture_output=True,
            text=True,
            timeout=60,
        )

    assert result.returncode in (0, 1), result.stderr
    assert "Decision: insufficient_information" in result.stdout
    assert "Facts needed to resolve the next decision:" in result.stdout
    assert "is_ai_system:" in result.stdout
    assert "Compliance score:" not in result.stdout
    assert "Highest risk tier:" not in result.stdout
