"""Tests for the public-repository privacy boundary."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import public_repo_guard as guard


def _text(values: list[int]) -> str:
    """Build sensitive-looking test data without placing it in source."""
    return "".join(chr(value) for value in values)


def test_public_repo_guard_rejects_private_record_path(tmp_path: Path):
    path = tmp_path / "docs" / "handover" / "state.md"
    path.parent.mkdir(parents=True)
    path.write_text("internal state", encoding="utf-8")
    findings = guard.scan_path(path, tmp_path)
    assert guard.Finding("docs/handover/state.md", "private-path") in findings


def test_public_repo_guard_rejects_personal_machine_path(tmp_path: Path):
    path = tmp_path / "docs" / "example.md"
    path.parent.mkdir(parents=True)
    value = _text([47, 104, 111, 109, 101, 47, 97, 108, 105, 99, 101])
    path.write_text(value, encoding="utf-8")
    findings = guard.scan_path(path, tmp_path)
    assert guard.Finding("docs/example.md", "personal-machine-path") in findings


def test_public_repo_guard_accepts_portable_placeholders(tmp_path: Path):
    path = tmp_path / "docs" / "example.md"
    path.parent.mkdir(parents=True)
    path.write_text(
        "/home/USER and /mnt/c/Users/USER and LOCAL-MACHINE",
        encoding="utf-8",
    )
    assert guard.scan_path(path, tmp_path) == []


def test_public_repo_guard_rejects_non_project_email(tmp_path: Path):
    path = tmp_path / "docs" / "example.md"
    path.parent.mkdir(parents=True)
    address = _text([112, 101, 114, 115, 111, 110, 64, 112, 114, 105, 118, 97, 116, 101, 46, 116, 101, 115, 116])
    path.write_text(address, encoding="utf-8")
    findings = guard.scan_path(path, tmp_path)
    assert guard.Finding("docs/example.md", "non-project-email") in findings


def test_public_repo_guard_accepts_project_and_example_emails(tmp_path: Path):
    path = tmp_path / "docs" / "example.md"
    path.parent.mkdir(parents=True)
    path.write_text(
        "support@getregula.com and reviewer@example.com",
        encoding="utf-8",
    )
    assert guard.scan_path(path, tmp_path) == []


def test_public_repo_guard_rejects_known_personal_identity(tmp_path: Path):
    path = tmp_path / "benchmarks" / "labels.json"
    path.parent.mkdir(parents=True)
    value = _text([112, 104, 117, 108, 117, 115, 111])
    path.write_text(value, encoding="utf-8")
    findings = guard.scan_path(path, tmp_path)
    assert guard.Finding("benchmarks/labels.json", "personal-identity") in findings


def test_public_repo_guard_rejects_private_program_marker(tmp_path: Path):
    path = tmp_path / "docs" / "status.md"
    path.parent.mkdir(parents=True)
    value = _text([112, 114, 111, 100, 117, 99, 116, 95, 98, 117, 105, 108, 100])
    path.write_text(value, encoding="utf-8")
    findings = guard.scan_path(path, tmp_path)
    assert guard.Finding("docs/status.md", "private-program-marker") in findings


def test_public_repo_guard_rejects_concrete_credential_shape(tmp_path: Path):
    path = tmp_path / "docs" / "example.md"
    path.parent.mkdir(parents=True)
    value = _text([65, 75, 73, 65] + [48] * 16)
    path.write_text(value, encoding="utf-8")
    findings = guard.scan_path(path, tmp_path)
    assert guard.Finding("docs/example.md", "aws-access-key") in findings
