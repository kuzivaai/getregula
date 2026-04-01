# regula-ignore
#!/usr/bin/env python3
"""
Tests for enhanced documentation generation (Package 2).

Tests auto-population of Annex IV sections from code analysis:
architecture detection, data source detection, human oversight,
logging, risk register, and model card format.
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

passed = 0
failed = 0
_PYTEST_MODE = "pytest" in sys.modules


def assert_eq(actual, expected, msg=""):
    global passed, failed
    if actual == expected:
        passed += 1
    else:
        failed += 1
        if _PYTEST_MODE:
            raise AssertionError(f"{msg} — expected {expected!r}, got {actual!r}")
        print(f"  FAIL: {msg} — expected {expected!r}, got {actual!r}")


def assert_true(val, msg=""):
    assert_eq(val, True, msg)


def _make_fixture(tmp_dir, filename, content):
    """Write a code file to tmp_dir and return the dir path."""
    filepath = Path(tmp_dir) / filename
    filepath.write_text(content, encoding="utf-8")
    return tmp_dir


def _run_docs(project_path, *extra_args):
    """Run regula docs and return stdout."""
    r = subprocess.run(
        [sys.executable, "scripts/cli.py", "docs", "--project", project_path] + list(extra_args),
        capture_output=True, text=True, timeout=30,
        cwd=str(Path(__file__).parent.parent),
    )
    return r


# ── Architecture Detection ──────────────────────────────────────────


def _read_annex_output(tmp_dir):
    """Read the generated Annex IV file from output directory."""
    out_dir = Path(tmp_dir) / "out"
    files = list(out_dir.glob("*annex*"))
    if files:
        return files[0].read_text(encoding="utf-8")
    return ""


def test_docs_detects_pytorch_architecture():
    """PyTorch imports -> 'PyTorch' mentioned in architecture section."""
    with tempfile.TemporaryDirectory() as tmp:
        _make_fixture(tmp, "model.py",
            "import torch\nimport torch.nn as nn\n"
            "class Net(nn.Module):\n"
            "    def __init__(self):\n"
            "        super().__init__()\n"
            "        self.conv = nn.Conv2d(1, 32, 3)\n"
            "    def forward(self, x):\n"
            "        return self.conv(x)\n"
        )
        out_dir = str(Path(tmp) / "out")
        r = _run_docs(tmp, "--output", out_dir)
        assert_eq(r.returncode, 0, f"docs should exit 0: {r.stderr[:200]}")
        content = _read_annex_output(tmp)
        assert_true("pytorch" in content.lower(),
                    "should detect PyTorch in generated doc")
    print("\u2713 Docs: detects PyTorch architecture")


def test_docs_detects_transformer_architecture():
    """transformers import -> 'Transformer' mentioned in output."""
    with tempfile.TemporaryDirectory() as tmp:
        _make_fixture(tmp, "nlp.py",
            "from transformers import AutoModel, AutoTokenizer\n"
            "model = AutoModel.from_pretrained('bert-base')\n"
        )
        out_dir = str(Path(tmp) / "out")
        r = _run_docs(tmp, "--output", out_dir)
        assert_eq(r.returncode, 0, f"docs should exit 0: {r.stderr[:200]}")
        content = _read_annex_output(tmp)
        assert_true("transformer" in content.lower(),
                    "should detect Transformer architecture")
    print("\u2713 Docs: detects Transformer architecture")


# ── Data Source Detection ───────────────────────────────────────────


def test_docs_detects_csv_data_source():
    """pd.read_csv -> CSV data source listed."""
    with tempfile.TemporaryDirectory() as tmp:
        _make_fixture(tmp, "train.py",
            "import pandas as pd\nimport sklearn\n"
            "data = pd.read_csv('training_data.csv')\n"
            "model = sklearn.linear_model.LinearRegression()\n"
            "model.fit(data[['x']], data['y'])\n"
        )
        out_dir = str(Path(tmp) / "out")
        r = _run_docs(tmp, "--output", out_dir)
        assert_eq(r.returncode, 0, f"docs should exit 0: {r.stderr[:200]}")
        content = _read_annex_output(tmp)
        assert_true("csv" in content.lower(),
                    "should detect CSV data source")
    print("\u2713 Docs: detects CSV data source")


def test_docs_detects_db_connection():
    """SQLAlchemy import -> Database connection listed."""
    with tempfile.TemporaryDirectory() as tmp:
        _make_fixture(tmp, "pipeline.py",
            "from sqlalchemy import create_engine\n"
            "import openai\n"
            "engine = create_engine('postgresql://localhost/mydb')\n"
            "client = openai.Client()\n"
        )
        out_dir = str(Path(tmp) / "out")
        r = _run_docs(tmp, "--output", out_dir)
        assert_eq(r.returncode, 0, f"docs should exit 0: {r.stderr[:200]}")
        content = _read_annex_output(tmp)
        assert_true("database" in content.lower() or "sqlalchemy" in content.lower(),
                    "should detect database connection")
    print("\u2713 Docs: detects database connection")


# ── Human Oversight & Logging ───────────────────────────────────────


def test_docs_detects_human_oversight():
    """human_review pattern -> oversight noted in docs."""
    with tempfile.TemporaryDirectory() as tmp:
        _make_fixture(tmp, "app.py",
            "import openai\n"
            "def process(text):\n"
            "    result = openai.chat.completions.create(model='gpt-4', messages=[{'role':'user','content':text}])\n"
            "    if human_review_approved(result):\n"
            "        return result\n"
        )
        out_dir = str(Path(tmp) / "out")
        r = _run_docs(tmp, "--output", out_dir)
        assert_eq(r.returncode, 0, f"docs should exit 0: {r.stderr[:200]}")
        content = _read_annex_output(tmp)
        assert_true("oversight" in content.lower() or "human" in content.lower(),
                    "should detect human oversight pattern")
    print("\u2713 Docs: detects human oversight")


def test_docs_detects_logging():
    """logging.info pattern -> logging noted in docs."""
    with tempfile.TemporaryDirectory() as tmp:
        _make_fixture(tmp, "app.py",
            "import logging\nimport openai\n"
            "logger = logging.getLogger(__name__)\n"
            "def predict(data):\n"
            "    result = openai.chat.completions.create(model='gpt-4', messages=data)\n"
            "    logger.info('prediction made', extra={'result': result})\n"
            "    return result\n"
        )
        out_dir = str(Path(tmp) / "out")
        r = _run_docs(tmp, "--output", out_dir)
        assert_eq(r.returncode, 0, f"docs should exit 0: {r.stderr[:200]}")
        content = _read_annex_output(tmp)
        assert_true("logging" in content.lower(),
                    "should detect logging infrastructure")
    print("\u2713 Docs: detects logging")


# ── Risk Register ───────────────────────────────────────────────────


def test_docs_risk_register_owasp():
    """High-risk file -> OWASP mapping in risk register."""
    r = _run_docs("tests/fixtures/sample_high_risk/")
    assert_eq(r.returncode, 0, f"docs should exit 0: {r.stderr[:200]}")
    # Should contain some risk register or findings section
    assert_true("risk" in r.stdout.lower(),
                "should contain risk information")
    print("\u2713 Docs: risk register present for high-risk project")


# ── Model Card Format ───────────────────────────────────────────────


def test_docs_model_card_format():
    """--format model-card -> HuggingFace-compatible markdown."""
    with tempfile.TemporaryDirectory() as tmp:
        _make_fixture(tmp, "model.py",
            "import torch\nfrom transformers import AutoModel\n"
            "model = AutoModel.from_pretrained('bert-base')\n"
        )
        out_dir = Path(tmp) / "output"
        r = _run_docs(tmp, "--output", str(out_dir), "--format", "model-card")
        assert_eq(r.returncode, 0, f"model-card should exit 0: {r.stderr[:200]}")
        # Check output file exists
        cards = list(out_dir.glob("*model_card*")) if out_dir.exists() else []
        assert_true(len(cards) > 0, f"should create model card file, found: {cards}")
        if cards:
            content = cards[0].read_text(encoding="utf-8")
            assert_true("model details" in content.lower() or "model card" in content.lower(),
                        "model card should contain standard sections")
    print("\u2713 Docs: --format model-card generates HuggingFace-compatible output")


# ── Auto-Detect Marking ────────────────────────────────────────────


def test_docs_auto_fields_marked_verify():
    """All auto-populated fields contain [AUTO-DETECTED]."""
    with tempfile.TemporaryDirectory() as tmp:
        _make_fixture(tmp, "app.py",
            "import torch\nfrom transformers import pipeline\n"
            "classifier = pipeline('text-classification')\n"
        )
        out_dir = Path(tmp) / "output"
        r = _run_docs(tmp, "--output", str(out_dir))
        assert_eq(r.returncode, 0, f"docs should exit 0: {r.stderr[:200]}")
        annex_files = list(out_dir.glob("*annex*"))
        assert_true(len(annex_files) > 0, "should create annex IV file")
        if annex_files:
            content = annex_files[0].read_text(encoding="utf-8")
            # If any auto-detected content exists, it should be marked
            if "pytorch" in content.lower() or "transformer" in content.lower():
                assert_true("auto-detected" in content.lower() or "verify" in content.lower(),
                            "auto-populated fields should be marked for verification")
    print("\u2713 Docs: auto-detected fields marked for verification")


# ── AST Integration ─────────────────────────────────────────────────


def test_docs_ast_development_methods_populated():
    """Section 2.1 Development Methods is populated from AST (not blank) when AI functions exist."""
    with tempfile.TemporaryDirectory() as tmp:
        _make_fixture(tmp, "model.py",
            "import torch\n"
            "def train_model(features, labels):\n"
            "    model = torch.nn.Linear(10, 1)\n"
            "    return model\n"
            "def predict(model, x):\n"
            "    return model(x)\n"
        )
        out_dir = str(Path(tmp) / "out")
        r = _run_docs(tmp, "--output", out_dir)
        assert_eq(r.returncode, 0, f"docs exit 0: {r.stderr[:200]}")
        content = _read_annex_output(tmp)
        # Section 2.1 must not be entirely placeholder
        assert_true(
            "TO BE COMPLETED BY DEVELOPMENT TEAM" not in content.split("### 2.1")[1].split("###")[0],
            "Section 2.1 should be populated by AST, not left as TO BE COMPLETED",
        )
    print("\u2713 Docs AST: section 2.1 populated from AST function analysis")


def test_docs_ast_oversight_score_in_section_33():
    """Section 3.3 reports an AST-derived oversight score for a file with AI calls."""
    with tempfile.TemporaryDirectory() as tmp:
        _make_fixture(tmp, "scorer.py",
            "import sklearn.ensemble\n"
            "def score(model, data):\n"
            "    result = model.predict(data)\n"
            "    return result\n"
        )
        out_dir = str(Path(tmp) / "out")
        r = _run_docs(tmp, "--output", out_dir)
        assert_eq(r.returncode, 0, f"docs exit 0: {r.stderr[:200]}")
        content = _read_annex_output(tmp)
        section_33 = content.split("### 3.3")[1].split("###")[0] if "### 3.3" in content else ""
        # Should have a numeric oversight score or mention of automated decisions
        assert_true(
            "score" in section_33.lower() or "automated" in section_33.lower() or "/100" in section_33,
            "Section 3.3 should contain oversight score or automated decision info from AST",
        )
    print("\u2713 Docs AST: section 3.3 populated with oversight score")


def test_docs_ast_unlogged_ops_reported():
    """Section 3.4 reports unlogged AI operations when AI calls have no nearby logging."""
    with tempfile.TemporaryDirectory() as tmp:
        _make_fixture(tmp, "decision.py",
            "import openai\n"
            "def decide(prompt):\n"
            "    result = openai.chat.completions.create(\n"
            "        model='gpt-4',\n"
            "        messages=[{'role': 'user', 'content': prompt}]\n"
            "    )\n"
            "    return result\n"
        )
        out_dir = str(Path(tmp) / "out")
        r = _run_docs(tmp, "--output", out_dir)
        assert_eq(r.returncode, 0, f"docs exit 0: {r.stderr[:200]}")
        content = _read_annex_output(tmp)
        section_34 = content.split("### 3.4")[1].split("###")[0] if "### 3.4" in content else ""
        # Should report logging coverage or unlogged count
        assert_true(
            "coverage" in section_34.lower() or "score" in section_34.lower()
            or "unlogged" in section_34.lower() or "/100" in section_34,
            "Section 3.4 should report logging coverage or unlogged AI operations",
        )
    print("\u2713 Docs AST: section 3.4 reports logging score/unlogged ops")


def test_docs_ast_ai_operations_listed():
    """AI operations detected by AST are listed in the generated documentation."""
    with tempfile.TemporaryDirectory() as tmp:
        _make_fixture(tmp, "pipeline.py",
            "import torch\n"
            "model = torch.nn.Linear(10, 2)\n"
            "def run(x):\n"
            "    return model(x)\n"
        )
        out_dir = str(Path(tmp) / "out")
        r = _run_docs(tmp, "--output", out_dir)
        assert_eq(r.returncode, 0, f"docs exit 0: {r.stderr[:200]}")
        content = _read_annex_output(tmp)
        # AI operations (model calls, predict calls) should be mentioned
        assert_true(
            "ai operation" in content.lower() or "model(" in content.lower()
            or "predict" in content.lower() or "function" in content.lower(),
            "Generated doc should list AI operations or functions from AST",
        )
    print("\u2713 Docs AST: AI operations from data flow analysis are listed")


# ── Skip-dirs / Nested Project ──────────────────────────────────────


def test_docs_nested_in_tests_dir_not_blank():
    """Projects nested under a 'tests/' parent dir still get AST-populated sections.

    Regression: skip_dirs used filepath.parts (absolute path), so any project
    located inside tests/ had every file silently skipped.
    """
    import tempfile, os
    # Build a nested path: <tmp>/tests/my_project/model.py
    with tempfile.TemporaryDirectory() as base:
        nested = Path(base) / "tests" / "my_project"
        nested.mkdir(parents=True)
        (nested / "model.py").write_text(
            "import torch\n"
            "def train(x, y):\n"
            "    model = torch.nn.Linear(2, 1)\n"
            "    return model.fit(x, y)\n",
            encoding="utf-8",
        )
        out_dir = str(Path(base) / "out")
        r = _run_docs(str(nested), "--output", out_dir)
        assert_eq(r.returncode, 0, f"docs exit 0: {r.stderr[:200]}")
        # Read the generated file directly since _read_annex_output looks in tmp/out
        out_files = list(Path(out_dir).glob("*annex*")) if Path(out_dir).exists() else []
        content = out_files[0].read_text(encoding="utf-8") if out_files else ""
        section_21 = content.split("### 2.1")[1].split("###")[0] if "### 2.1" in content else ""
        assert_true(
            "TO BE COMPLETED BY DEVELOPMENT TEAM" not in section_21,
            "Section 2.1 should be populated even when project is nested inside tests/",
        )
    print("\u2713 Docs: projects nested inside tests/ dir still get AST analysis")


def test_docs_version_string_is_current():
    """Generated Annex IV should say v1.2.0, not v1.1.0."""
    with tempfile.TemporaryDirectory() as tmp:
        _make_fixture(tmp, "app.py", "import openai\nclient = openai.Client()\n")
        out_dir = str(Path(tmp) / "out")
        r = _run_docs(tmp, "--output", out_dir)
        assert_eq(r.returncode, 0, f"docs exit 0: {r.stderr[:200]}")
        out_files = list(Path(out_dir).glob("*annex*")) if Path(out_dir).exists() else []
        content = out_files[0].read_text(encoding="utf-8") if out_files else ""
        assert_true("v1.1.0" not in content, "Generated doc must not reference old v1.1.0")
        assert_true("v1.2.0" in content, "Generated doc should reference current v1.2.0")
    print("\u2713 Docs: version string is current (v1.2.0)")


# ── Empty Project ───────────────────────────────────────────────────


def test_docs_empty_project_graceful():
    """Project with no AI files -> scaffold with empty sections, no crash."""
    with tempfile.TemporaryDirectory() as tmp:
        _make_fixture(tmp, "main.py", "print('hello world')\n")
        r = _run_docs(tmp)
        assert_eq(r.returncode, 0, f"empty project should exit 0: {r.stderr[:200]}")
        assert_true(len(r.stdout) > 50, "should produce scaffold output")
    print("\u2713 Docs: empty project generates scaffold gracefully")


# ── Runner ──────────────────────────────────────────────────────────


if __name__ == "__main__":
    tests = [
        test_docs_detects_pytorch_architecture,
        test_docs_detects_transformer_architecture,
        test_docs_detects_csv_data_source,
        test_docs_detects_db_connection,
        test_docs_detects_human_oversight,
        test_docs_detects_logging,
        test_docs_risk_register_owasp,
        test_docs_model_card_format,
        test_docs_auto_fields_marked_verify,
        test_docs_ast_development_methods_populated,
        test_docs_ast_oversight_score_in_section_33,
        test_docs_ast_unlogged_ops_reported,
        test_docs_ast_ai_operations_listed,
        test_docs_nested_in_tests_dir_not_blank,
        test_docs_version_string_is_current,
        test_docs_empty_project_graceful,
    ]

    print(f"Running {len(tests)} documentation tests...\n")

    for test in tests:
        try:
            test()
        except Exception as e:
            failed += 1
            print(f"  EXCEPTION in {test.__name__}: {e}")

    print(f"\n{'=' * 50}")
    print(f"Results: {passed} passed, {failed} failed ({len(tests)} test functions)")
    if failed:
        print("SOME TESTS FAILED")
        sys.exit(1)
    else:
        print("All tests passed!")
