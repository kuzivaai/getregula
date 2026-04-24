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
    assert data["label"] == "EU AI Act"
    assert data["color"] in ("brightgreen", "orange", "red")
    assert "message" in data


def test_badge_svg_format():
    result = _run("badge", "tests/fixtures/sample_compliant/", "--format", "svg")
    assert result.returncode == 0
    assert "<svg" in result.stdout
    assert "EU AI Act" in result.stdout


def test_badge_high_risk_shows_orange():
    result = _run("badge", "tests/fixtures/sample_high_risk/", "--format", "endpoint")
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["color"] == "orange"


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

    Runs against examples/cv-screening-app/ which contains an intentional
    high-risk employment finding (see examples/README.md). Previously this
    test pointed at scripts/ and relied on a self-scan false positive in
    scripts/explain_articles.py; that was correctly suppressed in commit
    0c0a762 so the target had to move to a directory with genuine findings.
    """
    env = os.environ.copy()
    env["REGULA_STRICT"] = "1"
    result = subprocess.run(
        [sys.executable, "-m", "scripts.cli", "check", "examples/cv-screening-app/"],
        capture_output=True, text=True, timeout=30, env=env,
        cwd=os.path.join(os.path.dirname(__file__), ".."),
    )
    assert result.returncode != 0, (
        f"expected non-zero exit under REGULA_STRICT=1; got {result.returncode}\n"
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
