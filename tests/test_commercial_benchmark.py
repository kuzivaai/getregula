"""Integrity controls for the preregistered commercial_v1 benchmark."""

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "benchmarks" / "commercial_v1"))

import normalise  # noqa: E402
import score  # noqa: E402
import verify  # noqa: E402
import gate  # noqa: E402


def _git_repo(tmp):
    root = Path(tmp)
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "benchmark@test"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "benchmark"], cwd=root, check=True)
    (root / "case.py").write_text("import example_ai\n")
    subprocess.run(["git", "add", "case.py"], cwd=root, check=True)
    subprocess.run(["git", "commit", "-qm", "fixture"], cwd=root, check=True)
    return root


def test_verify_refuses_untracked_and_ignored_inputs():
    with tempfile.TemporaryDirectory() as tmp:
        root = _git_repo(tmp)
        (root / ".gitignore").write_text("ignored.py\n")
        subprocess.run(["git", "add", ".gitignore"], cwd=root, check=True)
        subprocess.run(["git", "commit", "-qm", "ignore rule"], cwd=root, check=True)
        (root / "untracked.py").write_text("x = 1\n")
        (root / "ignored.py").write_text("x = 2\n")
        try:
            verify.assert_clean_inputs(root, ["case.py", "untracked.py", "ignored.py"])
        except verify.IntegrityError as exc:
            text = str(exc)
            assert "untracked.py" in text and "ignored.py" in text
        else:
            raise AssertionError("untracked and ignored inputs were accepted")


def test_verify_refuses_missing_git_instead_of_passing_vacuously():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "case.py").write_text("x = 1\n")
        try:
            verify.assert_clean_inputs(root, ["case.py"])
        except verify.IntegrityError as exc:
            assert "git" in str(exc).lower()
        else:
            raise AssertionError("non-git input root passed")


def test_manifest_enumeration_is_bidirectional_and_hash_bound():
    with tempfile.TemporaryDirectory() as tmp:
        root = _git_repo(tmp)
        digest = hashlib.sha256((root / "case.py").read_bytes()).hexdigest()
        entries = [{"path": "case.py", "sha256": digest}]
        verify.verify_enumeration(root, entries, ["case.py"])
        for discovered in (["case.py", "extra.py"], []):
            try:
                verify.verify_enumeration(root, entries, discovered)
            except verify.IntegrityError:
                pass
            else:
                raise AssertionError(f"bad discovery set passed: {discovered}")
        entries[0]["sha256"] = "0" * 64
        try:
            verify.verify_enumeration(root, entries, ["case.py"])
        except verify.IntegrityError:
            pass
        else:
            raise AssertionError("wrong input hash passed")


def test_result_verifier_rejects_missing_duplicate_and_failed_runs():
    expected = {"a", "b"}
    valid = [
        {"decision_id": "a", "exit_code": 0, "timed_out": False,
         "parse_error": None, "predicted": False},
        {"decision_id": "b", "exit_code": 0, "timed_out": False,
         "parse_error": None, "predicted": False},
    ]
    verify.verify_results(expected, valid)
    for records in (valid[:1], valid + [valid[0]]):
        try:
            verify.verify_results(expected, records)
        except verify.IntegrityError:
            pass
        else:
            raise AssertionError(f"invalid results passed: {records}")
    adverse = [valid[0], {**valid[1], "exit_code": 2}]
    assert verify.verify_results(expected, adverse, require_success=False) == ["b"]
    try:
        verify.verify_results(expected, adverse, require_success=True)
    except verify.IntegrityError:
        pass
    else:
        raise AssertionError("failed execution was headline-eligible")


def test_normalisation_is_deterministic_and_drops_volatile_fields():
    records = [{"path": "b.py", "tier": "high_risk", "timestamp": "later",
                "command": ["/usr/bin/python3", "/tmp/run-1/cases/a-positive-01"]},
               {"path": "a.py", "tier": "limited_risk", "duration": 2.1,
                "command": ["/opt/python3", "/tmp/run-2/cases/a-positive-01"]}]
    first = normalise.normalise(records)
    second = normalise.normalise(list(reversed(records)))
    assert first == second
    assert all("timestamp" not in row and "duration" not in row for row in first)
    commands = [row["command"] for row in first]
    assert commands[0] == commands[1] == ["<PYTHON>", "<CASE_DIR>"]


def test_score_uses_fractions_and_wilson_intervals():
    result = score.binary_metrics(tp=27, fp=3, fn=3, tn=27)
    assert result["precision"]["numerator"] == 27
    assert result["precision"]["denominator"] == 30
    assert result["recall"]["numerator"] == 27
    assert result["recall"]["denominator"] == 30
    assert 0 < result["precision"]["wilson95"]["low"] < 0.90
    assert result["precision"]["wilson95"]["high"] <= 1


def test_frozen_manifest_hash_mismatch_is_rejected():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "manifest.json"
        path.write_text(json.dumps({"protocol_version": "commercial_v1"}))
        try:
            verify.load_hash_bound_json(path, "0" * 64)
        except verify.IntegrityError:
            pass
        else:
            raise AssertionError("changed manifest was accepted")


def test_gate_is_conjunctive_and_cannot_pass_on_metrics_alone():
    metrics = score.binary_metrics(tp=40, fp=0, fn=0, tn=40)
    external = {
        "synthetic_complete": True,
        "independently_labelled_repositories": 0,
        "determinism_pass": True,
        "manifest_verified": True,
        "failed_runs_visible": True,
        "public_journey_pass": True,
        "material_network_contradiction": False,
        "public_claim_integrity": "PASS",
        "comparative_advantage": "DEMONSTRATED",
        "all_strata_reported": True,
    }
    result = gate.evaluate("A", metrics, external)
    assert result["claim_ready"] is False
    assert "independent_repository_labels_30" in result["failed_checks"]
    external["independently_labelled_repositories"] = 30
    assert gate.evaluate("A", metrics, external)["claim_ready"] is True


def test_score_duplicate_decisions_are_never_headline_eligible():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        labels = root / "labels.json"
        labels.write_text(json.dumps([
            {"decision_id": "a-positive-01", "candidate": "A", "expected": True},
            {"decision_id": "b-negative-01", "candidate": "B", "expected": False},
        ]))
        record_a = {"decision_id": "a-positive-01", "candidate": "A",
                    "language": "python", "transform": "direct",
                    "exit_code": 0, "timed_out": False,
                    "parse_error": None, "predicted": True}
        record_b = {"decision_id": "b-negative-01", "candidate": "B",
                    "language": "html", "transform": "comment",
                    "exit_code": 0, "timed_out": False,
                    "parse_error": None, "predicted": False}
        results = root / "results.json"
        results.write_text(json.dumps({"tool": "local_head",
                                       "records": [record_a, record_a, record_b]}))
        report = score.score_result_files(labels, [results])["reports"][0]
        assert report["duplicate_ids"] == ["a-positive-01"]
        assert report["candidates"]["A"]["synthetic_metric_eligible"] is False
