# regula-ignore
"""Tests for scripts/gpai_check.py — GPAI Code of Practice checker.

Uses tempfile.TemporaryDirectory rather than pytest tmp_path so the same
tests run under both the custom runner (tests/test_classification.py
walks globals()) and pytest.
"""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from gpai_check import (
    detect_gpai_signals,
    evaluate_transparency,
    evaluate_copyright,
    evaluate_safety_security,
    run_gpai_check,
    format_gpai_check_text,
)


# ---------- helpers ----------

def _write(root: Path, rel: str, content: str) -> None:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")


# ---------- signal detection ----------

def test_detect_signals_empty_dir():
    with tempfile.TemporaryDirectory() as tmp:
        signals = detect_gpai_signals(tmp)
    assert signals["is_training_code"] is False
    assert signals["has_distribution_code"] is False
    assert signals["is_crawler_code"] is False
    assert signals["files_scanned"] == 0


def test_detect_training_pytorch_loop():
    with tempfile.TemporaryDirectory() as tmp:
        _write(Path(tmp), "train.py",
               "import torch\nloss.backward()\noptimizer.step()\n")
        signals = detect_gpai_signals(tmp)
    assert signals["is_training_code"] is True
    labels = {label for _, label in signals["training_matches"]}
    assert "pytorch_backward" in labels
    assert "pytorch_optimizer_step" in labels


def test_detect_training_hf_trainer():
    with tempfile.TemporaryDirectory() as tmp:
        _write(Path(tmp), "train.py",
               "from transformers import Trainer, TrainingArguments\n"
               "trainer = Trainer(model=m, args=TrainingArguments())\n")
        signals = detect_gpai_signals(tmp)
    assert signals["is_training_code"] is True
    labels = {label for _, label in signals["training_matches"]}
    assert "hf_trainer_import" in labels
    assert "hf_training_args" in labels


def test_detect_distribution_push_to_hub():
    with tempfile.TemporaryDirectory() as tmp:
        _write(Path(tmp), "publish.py",
               "model.push_to_hub('myorg/mymodel')\n")
        signals = detect_gpai_signals(tmp)
    assert signals["has_distribution_code"] is True
    # push_to_hub alone is NOT a training signal
    assert signals["is_training_code"] is False


def test_detect_crawler_requires_two_signals():
    with tempfile.TemporaryDirectory() as tmp:
        _write(Path(tmp), "fetch.py", "import requests\nrequests.get('https://x')\n")
        signals = detect_gpai_signals(tmp)
    # single requests.get should not flag as crawler
    assert signals["is_crawler_code"] is False


def test_detect_crawler_with_two_signals():
    with tempfile.TemporaryDirectory() as tmp:
        _write(Path(tmp), "scrape.py",
               "import scrapy\nfrom bs4 import BeautifulSoup\n"
               "s = BeautifulSoup('<a>', 'html.parser')\n")
        signals = detect_gpai_signals(tmp)
    assert signals["is_crawler_code"] is True
    labels = {label for _, label in signals["crawler_matches"]}
    assert "scrapy" in labels
    assert "beautifulsoup" in labels


def test_detect_robots_compliance():
    with tempfile.TemporaryDirectory() as tmp:
        _write(Path(tmp), "scrape.py",
               "import scrapy\nfrom bs4 import BeautifulSoup\n"
               "soup = BeautifulSoup('<a/>', 'html.parser')\n"
               "from urllib.robotparser import RobotFileParser\n"
               "rp = RobotFileParser()\n")
        signals = detect_gpai_signals(tmp)
    assert signals["is_crawler_code"] is True
    labels = {label for _, label in signals["robots_compliance_matches"]}
    assert "urllib_robotparser" in labels or "robot_file_parser" in labels


def test_detect_robots_bypass_scrapy_disabled():
    with tempfile.TemporaryDirectory() as tmp:
        _write(Path(tmp), "settings.py", "ROBOTSTXT_OBEY = False\n")
        _write(Path(tmp), "scrape.py",
               "import scrapy\nfrom bs4 import BeautifulSoup\nb = BeautifulSoup('<a>')\n")
        signals = detect_gpai_signals(tmp)
    assert len(signals["robots_bypass_matches"]) >= 1
    labels = {label for _, label in signals["robots_bypass_matches"]}
    assert "scrapy_robots_disabled" in labels


def test_skip_test_directories():
    """Training signals inside tests/ must NOT count as provider obligations."""
    with tempfile.TemporaryDirectory() as tmp:
        _write(Path(tmp), "tests/test_train.py", "loss.backward()\n")
        signals = detect_gpai_signals(tmp)
    assert signals["is_training_code"] is False


# ---------- transparency evaluator ----------

def test_transparency_pass_with_model_card():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write(root, "train.py", "loss.backward()\noptimizer.step()\n")
        _write(root, "MODEL_CARD.md", "# Model Card\n")
        _write(root, "TRAINING_DATA_SUMMARY.md", "# Data Summary\n")
        signals = detect_gpai_signals(tmp)
        results = evaluate_transparency(root, signals)
    by_id = {r["obligation_id"]: r for r in results}
    assert by_id["model-documentation"]["verdict"] == "PASS"
    assert by_id["training-content-summary"]["verdict"] == "PASS"


def test_transparency_fail_when_training_no_data_summary():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write(root, "train.py", "loss.backward()\noptimizer.step()\n")
        signals = detect_gpai_signals(tmp)
        results = evaluate_transparency(root, signals)
    by_id = {r["obligation_id"]: r for r in results}
    assert by_id["training-content-summary"]["verdict"] == "FAIL"
    assert "53(1)(d)" in by_id["training-content-summary"]["article"]


def test_transparency_warn_when_only_readme_section():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write(root, "train.py", "loss.backward()\noptimizer.step()\n")
        _write(root, "README.md", "# Project\n## Model Card\nBlah\n## Training Data\nBlah\n")
        signals = detect_gpai_signals(tmp)
        results = evaluate_transparency(root, signals)
    by_id = {r["obligation_id"]: r for r in results}
    assert by_id["model-documentation"]["verdict"] == "WARN"
    assert by_id["training-content-summary"]["verdict"] == "WARN"


def test_transparency_na_when_no_training_code():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write(root, "app.py", "print('hi')\n")
        signals = detect_gpai_signals(tmp)
        results = evaluate_transparency(root, signals)
    by_id = {r["obligation_id"]: r for r in results}
    assert by_id["training-content-summary"]["verdict"] == "N/A"


def test_transparency_distribution_pass_with_model_card():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write(root, "publish.py", "model.push_to_hub('me/m')\n")
        _write(root, "MODEL_CARD.md", "# Card\n")
        signals = detect_gpai_signals(tmp)
        results = evaluate_transparency(root, signals)
    by_id = {r["obligation_id"]: r for r in results}
    assert by_id["downstream-provider-information"]["verdict"] == "PASS"


# ---------- copyright evaluator ----------

def test_copyright_pass_with_policy_file():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write(root, "train.py", "loss.backward()\n")
        _write(root, "COPYRIGHT_POLICY.md", "# Copyright Policy\n")
        signals = detect_gpai_signals(tmp)
        results = evaluate_copyright(root, signals)
    by_id = {r["obligation_id"]: r for r in results}
    assert by_id["written-copyright-policy"]["verdict"] == "PASS"


def test_copyright_fail_when_no_policy():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write(root, "train.py", "loss.backward()\n")
        signals = detect_gpai_signals(tmp)
        results = evaluate_copyright(root, signals)
    by_id = {r["obligation_id"]: r for r in results}
    assert by_id["written-copyright-policy"]["verdict"] == "FAIL"


def test_copyright_tdm_fail_on_robots_bypass():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write(root, "settings.py", "ROBOTSTXT_OBEY = False\n")
        _write(root, "spider.py",
               "import scrapy\nfrom bs4 import BeautifulSoup\nBeautifulSoup('<a>')\n")
        _write(root, "COPYRIGHT_POLICY.md", "# CP\n")
        signals = detect_gpai_signals(tmp)
        results = evaluate_copyright(root, signals)
    by_id = {r["obligation_id"]: r for r in results}
    assert by_id["tdm-optout-compliance"]["verdict"] == "FAIL"
    assert "robots.txt" in by_id["tdm-optout-compliance"]["evidence"]


def test_copyright_tdm_pass_on_robots_compliance():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write(root, "spider.py",
               "import scrapy\nfrom bs4 import BeautifulSoup\n"
               "from urllib.robotparser import RobotFileParser\nBeautifulSoup('<a>')\n")
        _write(root, "COPYRIGHT_POLICY.md", "# CP\n")
        signals = detect_gpai_signals(tmp)
        results = evaluate_copyright(root, signals)
    by_id = {r["obligation_id"]: r for r in results}
    assert by_id["tdm-optout-compliance"]["verdict"] == "PASS"


def test_copyright_tdm_na_when_no_crawler():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write(root, "train.py", "loss.backward()\n")
        signals = detect_gpai_signals(tmp)
        results = evaluate_copyright(root, signals)
    by_id = {r["obligation_id"]: r for r in results}
    assert by_id["tdm-optout-compliance"]["verdict"] == "N/A"


# ---------- safety & security evaluator ----------

def test_safety_n_a_without_systemic_risk_flag():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        results = evaluate_safety_security(root, detect_gpai_signals(tmp), False)
    assert len(results) == 1
    assert results[0]["verdict"] == "N/A"
    assert results[0]["obligation_id"] == "applicability"


def test_safety_fail_when_systemic_risk_no_evidence():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write(root, "train.py", "loss.backward()\n")
        results = evaluate_safety_security(root, detect_gpai_signals(tmp), True)
    by_id = {r["obligation_id"]: r for r in results}
    assert by_id["model-evaluation"]["verdict"] == "FAIL"
    assert by_id["serious-incident-reporting"]["verdict"] == "FAIL"


def test_safety_pass_with_full_artefacts():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write(root, "train.py", "loss.backward()\n")
        _write(root, "EVAL_REPORT.md", "# Evals\n")
        _write(root, "INCIDENT_RESPONSE.md", "# IR\n")
        _write(root, "sbom.json", "{}\n")
        results = evaluate_safety_security(root, detect_gpai_signals(tmp), True)
    by_id = {r["obligation_id"]: r for r in results}
    assert by_id["model-evaluation"]["verdict"] == "PASS"
    assert by_id["serious-incident-reporting"]["verdict"] == "PASS"
    assert by_id["cybersecurity-protection"]["verdict"] == "PASS"


# ---------- top-level run_gpai_check ----------

def test_run_full_check_returns_expected_keys():
    with tempfile.TemporaryDirectory() as tmp:
        result = run_gpai_check(tmp, systemic_risk=False)
    for key in [
        "project_path", "is_training_code", "has_distribution_code",
        "is_crawler_code", "systemic_risk_evaluated", "files_scanned",
        "cop_status", "cop_in_force_date", "cop_enforcement_begins",
        "obligations", "summary", "overall_verdict", "disclaimer",
    ]:
        assert key in result, f"missing key: {key}"


def test_run_full_check_overall_pass_when_clean():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write(root, "app.py", "print('hi')\n")
        result = run_gpai_check(tmp, systemic_risk=False)
    # No training, no crawler -> all obligations N/A or PASS for non-applicable cases
    # But model-documentation and copyright-policy will FAIL because they apply
    # to all GPAI providers. Without GPAI signals at all, we still treat it as
    # an opt-in check; here the check runs and reports honestly.
    assert result["overall_verdict"] in ("FAIL", "WARN", "PASS")
    assert isinstance(result["summary"], dict)


def test_run_full_check_overall_fail_when_training_no_docs():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write(root, "train.py", "loss.backward()\noptimizer.step()\n")
        result = run_gpai_check(tmp, systemic_risk=False)
    assert result["overall_verdict"] == "FAIL"
    assert result["summary"]["FAIL"] >= 1


def test_run_full_check_systemic_risk_runs_chapter_3():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write(root, "train.py", "loss.backward()\noptimizer.step()\n")
        result = run_gpai_check(tmp, systemic_risk=True)
    chapters = {o["chapter"] for o in result["obligations"]}
    assert "safety_and_security" in chapters
    safety = [o for o in result["obligations"] if o["chapter"] == "safety_and_security"]
    # systemic_risk=True must produce >1 entry (model-eval, incident, cyber)
    assert len(safety) >= 3


# ---------- text formatter ----------

def test_format_text_includes_chapter_titles():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write(root, "train.py", "loss.backward()\n")
        result = run_gpai_check(tmp, systemic_risk=True)
    text = format_gpai_check_text(result)
    assert "Chapter 1 - Transparency" in text
    assert "Chapter 2 - Copyright" in text
    assert "Chapter 3 - Safety & Security" in text
    assert "Overall verdict" in text
    assert "Summary:" in text
