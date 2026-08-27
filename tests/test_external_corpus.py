"""Safety and claim-boundary controls for the external diagnostic corpus."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "benchmarks"))
import run_external_corpus as corpus


def _manifest() -> dict:
    return json.loads(corpus.DEFAULT_MANIFEST.read_text(encoding="utf-8"))


def test_external_corpus_manifest_is_valid_and_pinned():
    payload = _manifest()
    assert corpus.validate_manifest(payload) == []
    assert len(payload["repositories"]) >= 12
    assert all(entry["commit"] != "HEAD" for entry in payload["repositories"])


def test_external_corpus_rejects_mutable_or_short_commit():
    payload = copy.deepcopy(_manifest())
    payload["repositories"][0]["commit"] = "HEAD"
    assert any("40-character SHA" in item for item in corpus.validate_manifest(payload))


def test_external_corpus_rejects_unlicensed_repository():
    payload = copy.deepcopy(_manifest())
    payload["repositories"][0]["license_spdx"] = "NOASSERTION"
    assert any("license_spdx" in item for item in corpus.validate_manifest(payload))


def test_external_corpus_rejects_non_github_or_mismatched_url():
    payload = copy.deepcopy(_manifest())
    payload["repositories"][0]["url"] = "https://example.invalid/repo.git"
    assert any("GitHub clone URL" in item for item in corpus.validate_manifest(payload))


def test_external_corpus_rejects_target_execution():
    payload = copy.deepcopy(_manifest())
    payload["scan_configuration"]["target_code_execution"] = True
    assert any("target_code_execution" in item for item in corpus.validate_manifest(payload))


def test_external_corpus_summary_contains_metadata_not_source_context():
    findings = [{"file": "src/app.py", "line": 7,
                 "detector_class": "limited_risk", "detector_priority": 42,
                 "category": "Transparency", "pattern_name": "chatbot",
                 "indicators": ["chatbot"], "suppressed": False,
                 "code_context": "private third-party source"}]
    summary = corpus._summarise_findings(findings)
    assert "private third-party source" not in json.dumps(summary)
    assert summary["by_detector_class"] == {"limited_risk": 1}


def test_external_corpus_expectations_are_diagnostic_not_accuracy_labels():
    expectations = [{"kind": "any_detector_class", "classes": ["high_risk"],
                     "rationale": "diagnostic probe"}]
    outcome = corpus._evaluate(expectations, {"high_risk": 0})[0]
    assert outcome["passed"] is False
    assert "independent contextual annotation" in outcome["interpretation"]
    assert "false-negative" in outcome["interpretation"]


def test_external_corpus_freeze_hashes_uncommitted_scanner_sources():
    paths = [REPO / "scripts" / "report.py", REPO / "scripts" / "risk_patterns.py"]
    first = corpus._files_sha256(paths)
    second = corpus._files_sha256(list(reversed(paths)))
    assert first == second
    assert len(first) == 64


def test_external_corpus_provenance_scope_covers_all_python_scanner_sources():
    source_paths = sorted((REPO / "scripts").glob("*.py")) + [
        REPO / "references" / "decision_model.v1.json",
        REPO / "references" / "framework_crosswalk.yaml",
        *sorted((REPO / "references" / "jurisdictions").glob("*.yaml")),
    ]
    assert len(source_paths) > 50
    assert all(path.is_file() for path in source_paths)
    assert len(corpus._files_sha256(source_paths)) == 64
