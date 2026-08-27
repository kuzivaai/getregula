"""Regressions derived from the preregistered external diagnostic corpus.

These are minimal constructions, not copied third-party source and not legal
ground-truth labels. They pin the specific parser/rule interactions observed on
26 August 2026 so later changes cannot silently reintroduce them.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from classify_risk import RiskTier, classify
from report import _is_test_file, scan_files


def test_cross_language_test_filenames_are_recognised():
    for name in (
        "worker_test.go", "widget.test.tsx", "widget.spec.jsx",
        "PolicyTest.java", "PolicyTests.java",
    ):
        assert _is_test_file(Path("src") / name), name


def test_concurrency_race_detector_is_not_sensitive_biometric_categorisation():
    result = classify(
        'import torch\nmessage = "CI uses the Go race detector"\n'
    )
    assert result.tier is not RiskTier.PROHIBITED
    actual_biometric = classify(
        'import torch\nmode = "race detection from face photos"\n'
    )
    assert actual_biometric.tier is RiskTier.PROHIBITED


def test_infrastructure_and_audio_terms_are_not_biometric_identification():
    benign_cases = (
        "import torch\nssl_verify_identity = True\n",
        "import torch\nspeaker_diarization = True\nspeaker_identifier = 'A'\n",
        "import torch\ndef match_faces_for_animation(a, b): return (a, b)\n",
        "import torch\nmode = 'face verification for account login'\n",
    )
    for code in benign_cases:
        assert classify(code).tier is not RiskTier.HIGH_RISK, code


def test_face_recognition_application_activates_biometric_review():
    with tempfile.TemporaryDirectory() as tmp:
        Path(tmp, "attendance.py").write_text(
            "import face_recognition\n"
            "known = face_recognition.face_encodings(image)\n"
            "matches = face_recognition.compare_faces(known, candidate)\n"
        )
        findings = scan_files(tmp, declared_domains={"biometrics"})
    assert any(
        finding["tier"] == "high_risk"
        and "biometrics" in finding.get("indicators", [])
        for finding in findings
    )


def test_employment_prompt_requires_and_responds_to_declared_context():
    with tempfile.TemporaryDirectory() as tmp:
        Path(tmp, "screening.py").write_text(
            "import autogen\n"
            "screening_prompt = '''Evaluate whether the candidate has the "
            "experience required for this role.'''\n"
        )
        undeclared = scan_files(tmp)
        declared = scan_files(tmp, declared_domains={"employment"})
    assert not any(f["tier"] == "high_risk" for f in undeclared)
    assert any(
        f["tier"] == "high_risk" and "employment" in f.get("indicators", [])
        for f in declared
    )


def test_credit_decision_label_requires_and_responds_to_declared_context():
    with tempfile.TemporaryDirectory() as tmp:
        Path(tmp, "model.py").write_text(
            "from sklearn.linear_model import LogisticRegression\n"
            "target = data['Receive or not receive credit']\n"
            "prediction = LogisticRegression().fit(features, target).predict(features)\n"
        )
        undeclared = scan_files(tmp)
        declared = scan_files(tmp, declared_domains={"finance"})
    assert not any(f["tier"] == "high_risk" for f in undeclared)
    assert any(
        f["tier"] == "high_risk"
        and "high_risk__credit_scoring" in f.get("indicators", [])
        for f in declared
    )


def test_agent_command_service_is_visible_in_agent_path():
    from agent_monitor import detect_autonomous_actions

    findings = detect_autonomous_actions(
        "export function run(command) { return runtime.executeCommand(command); }",
        filepath="src/api/agent-runtime-service.ts",
    )
    assert findings
    assert all(item["detection_mode"] == "contextual" for item in findings)
