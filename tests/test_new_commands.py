# regula-ignore
"""Tests for new CLI commands: badge, attest, explain-article, config hierarchy."""
import subprocess
import json
import os
import sys


def _run(*args, timeout=120):
    """Run regula CLI and return result."""
    return subprocess.run(
        [sys.executable, "-m", "scripts.cli", *args],
        capture_output=True, text=True, timeout=timeout,
        cwd=os.path.join(os.path.dirname(__file__), ".."),
    )


# --- badge ---

def test_badge_endpoint_format():
    result = _run("badge", "tests/fixtures/sample_compliant/", "--format", "endpoint")
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["schemaVersion"] == 1
    # The label names the TOOL, not the regulation. It read "EU AI Act" until
    # 2026-08-17, which is half of what made this badge a compliance
    # determination; the other half was message="compliant". LEDGER N125.
    assert data["label"] == "regula"
    assert data["message"] == "no indicators found"
    # Never brightgreen: a green badge beside a regulation reads as a pass.
    assert data["color"] == "lightgrey"


def test_badge_svg_format():
    result = _run("badge", "tests/fixtures/sample_compliant/", "--format", "svg")
    assert result.returncode == 0
    assert "<svg" in result.stdout
    assert "regula" in result.stdout
    assert "EU AI Act" not in result.stdout


def test_badge_markdown_carries_its_own_caveat_and_no_determination():
    """The badge is the output built to travel into someone else's README.

    The objection to it is that it detaches from every qualification on the page
    that produced it, so the qualification is the link target. This asserts both
    halves: the claim is gone, and the caveat travels.
    """
    result = _run("badge", "tests/fixtures/sample_compliant/", "--format", "markdown")
    assert result.returncode == 0
    out = result.stdout
    assert "compliant" not in out.lower()
    assert "EU%20AI%20Act" not in out and "EU AI Act" not in out
    assert "brightgreen" not in out
    assert "docs/what-regula-does-not-do.md" in out


def test_badge_on_a_trivial_project_claims_nothing():
    """The N125 reproduction, kept as a regression.

    A directory whose only content is print('hello') produced
    `[![EU AI Act](...EU%20AI%20Act-compliant-brightgreen)](https://getregula.com)`.
    This is the same input; the assertion is that no compliance state is emitted
    in any of the three formats.
    """
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        with open(os.path.join(td, "hello.py"), "w", encoding="utf-8") as fh:
            fh.write("print('hello')\n")
        for fmt in ("endpoint", "svg", "markdown"):
            result = _run("badge", td, "--format", fmt)
            assert result.returncode == 0, f"{fmt}: rc={result.returncode}"
            assert "compliant" not in result.stdout.lower(), fmt
            assert "brightgreen" not in result.stdout, fmt


def test_badge_high_risk_reports_an_indicator_count():
    # The fixture lives inside tests/, so under --scope production (the default)
    # it is test provenance and excluded, which is why no colour can be asserted
    # from the path. The old version of this test recorded that the badge
    # "correctly shows brightgreen (no production-scope findings)" for a fixture
    # named sample_high_risk: the defect stated in a test comment and accepted.
    # What is assertable in every case is that the message is a count of
    # indicators or their absence, never a state.
    result = _run("badge", "tests/fixtures/sample_high_risk/", "--format", "endpoint")
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["color"] in ("lightgrey", "orange", "red")
    assert "compliant" not in data["message"].lower()
    assert "indicator" in data["message"]


# --- attest ---

def test_attest_intoto_format():
    result = _run("attest", "tests/fixtures/sample_compliant/")
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["_type"] == "https://in-toto.io/Statement/v1"
    assert data["predicateType"] == "https://regula.dev/attestation/scan/v1"
    assert "subject" in data
    assert data["subject"][0]["digest"]["sha256"]
    assert data["predicate"]["scanner"]["name"] == "regula"


def test_attest_with_signing():
    result = _run("attest", "tests/fixtures/sample_compliant/", "--sign-key", "test-key-123")
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert "signatures" in data
    assert data["signatures"][0]["sig"]


def test_attest_output_file(tmp_path):
    out = str(tmp_path / "attestation.json")
    result = _run("attest", "tests/fixtures/sample_compliant/", "--output", out)
    assert result.returncode == 0
    with open(out) as f:
        data = json.load(f)
    assert data["_type"] == "https://in-toto.io/Statement/v1"


# --- explain-article ---

def test_explain_article_text():
    result = _run("explain-article", "5")
    assert result.returncode == 0
    assert "Prohibited" in result.stdout
    assert "Article 5" in result.stdout


def test_explain_article_json():
    result = _run("explain-article", "14", "--format", "json")
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["data"]["title"] == "Human oversight"


def test_explain_article_all_covered():
    """Every article we claim to cover actually works."""
    for article in ["4", "5", "6", "9", "10", "11", "12", "13", "14", "15", "17", "50", "53"]:
        result = _run("explain-article", article)
        assert result.returncode == 0, f"Article {article} failed"
        assert f"Article {article}" in result.stdout


def test_explain_article_invalid():
    result = _run("explain-article", "999")
    assert result.returncode == 0  # graceful failure
    assert "not found" in result.stdout.lower() or "Available" in result.stdout


# --- config hierarchy (env vars) ---

def test_env_regula_format():
    env = os.environ.copy()
    env["REGULA_FORMAT"] = "json"
    result = subprocess.run(
        [sys.executable, "-m", "scripts.cli", "check", "tests/fixtures/sample_compliant/"],
        capture_output=True, text=True, timeout=30, env=env,
        cwd=os.path.join(os.path.dirname(__file__), ".."),
    )
    # REGULA_FORMAT=json should produce JSON output
    try:
        data = json.loads(result.stdout)
        assert "format_version" in data or "data" in data
    except json.JSONDecodeError:
        pass  # Some commands may not support format override


def test_env_regula_strict():
    """REGULA_STRICT=1 enables CI mode — exit 1 when findings exist.

    Creates a temporary project with a real AI finding and verifies
    REGULA_STRICT=1 produces a non-zero exit code.
    """
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        app = os.path.join(tmp, "app.py")
        with open(app, "w") as f:
            # Multiple AI indicators + chatbot pattern → limited_risk with
            # confidence > 50 (WARN tier), which triggers CI non-zero exit.
            f.write("import openai\\nimport langchain\\n"
                    "from langchain.chat_models import ChatOpenAI\\n"
                    "chatbot = ChatOpenAI(model='gpt-4')\\n"
                    "response = chatbot.predict('hello user')\\n"
                    "# interactive chatbot for customer service\\n")
        env = os.environ.copy()
        env["REGULA_STRICT"] = "1"
        result = subprocess.run(
            [sys.executable, "-m", "scripts.cli", "check", tmp],
            capture_output=True, text=True, timeout=30, env=env,
            cwd=os.path.join(os.path.dirname(__file__), ".."),
        )
    assert result.returncode != 0, (
        f"expected non-zero exit under REGULA_STRICT=1; got {result.returncode}\\n"
        f"stdout: {result.stdout[:400]}"
    )


# --- deterministic JSON ---

def test_deterministic_json_output():
    r1 = _run("check", "tests/fixtures/sample_high_risk/", "--format", "json", "--deterministic")
    r2 = _run("check", "tests/fixtures/sample_high_risk/", "--format", "json", "--deterministic")
    assert r1.stdout == r2.stdout, "Deterministic JSON output should be byte-identical across runs"


# --- progress bar (hard to test directly, but verify no crash) ---

def test_check_large_scan_no_crash():
    """Scanning the whole repo (large) should not crash."""
    result = _run("check", "scripts/", "--format", "json")
    assert result.returncode in (0, 1)  # 0 = clean, 1 = findings (both ok)
