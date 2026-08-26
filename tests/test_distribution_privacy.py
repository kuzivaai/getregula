"""Tests for privacy checks on built wheel and source distributions."""

from __future__ import annotations

import io
import sys
import tarfile
import tempfile
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import verify_distribution_privacy as verifier


def _text(values: list[int]) -> str:
    return "".join(chr(value) for value in values)


def test_clean_wheel_passes_distribution_privacy_scan():
    with tempfile.TemporaryDirectory() as directory:
        wheel = Path(directory) / "regula_ai-9.9.9-py3-none-any.whl"
        with zipfile.ZipFile(wheel, "w") as archive:
            archive.writestr("scripts/core.py", "VALUE = 1\n")
            archive.writestr(
                "regula_ai-9.9.9.dist-info/METADATA",
                "Name: regula-ai\nAuthor-email: support@getregula.com\n",
            )
        assert verifier.scan_distribution(wheel) == []


def test_wheel_scan_detects_identity_without_echoing_value():
    with tempfile.TemporaryDirectory() as directory:
        wheel = Path(directory) / "regula_ai-9.9.9-py3-none-any.whl"
        identity = _text([112, 104, 117, 108, 117, 115, 111])
        with zipfile.ZipFile(wheel, "w") as archive:
            archive.writestr("scripts/core.py", f"reviewer = {identity!r}\n")
        findings = verifier.scan_distribution(wheel)
        assert [finding.rule for finding in findings] == ["personal-identity"]
        assert identity not in repr(findings)


def test_sdist_scan_strips_root_before_applying_private_path_rules():
    with tempfile.TemporaryDirectory() as directory:
        sdist = Path(directory) / "regula_ai-9.9.9.tar.gz"
        data = b"private state\n"
        with tarfile.open(sdist, "w:gz") as archive:
            member = tarfile.TarInfo(
                "regula_ai-9.9.9/docs/handover/state.md"
            )
            member.size = len(data)
            archive.addfile(member, io.BytesIO(data))
        findings = verifier.scan_distribution(sdist)
        assert [finding.rule for finding in findings] == ["private-path"]


def test_distribution_scan_rejects_path_traversal():
    with tempfile.TemporaryDirectory() as directory:
        wheel = Path(directory) / "regula_ai-9.9.9-py3-none-any.whl"
        with zipfile.ZipFile(wheel, "w") as archive:
            archive.writestr("../outside.txt", "unsafe\n")
        try:
            verifier.scan_distribution(wheel)
        except verifier.ArchiveSafetyError:
            return
        raise AssertionError("archive path traversal was accepted")


def test_distribution_scan_detects_concrete_credential_shape():
    with tempfile.TemporaryDirectory() as directory:
        sdist = Path(directory) / "regula_ai-9.9.9.tar.gz"
        value = _text([65, 75, 73, 65] + [48] * 16).encode("ascii")
        with tarfile.open(sdist, "w:gz") as archive:
            member = tarfile.TarInfo("regula_ai-9.9.9/scripts/config.py")
            member.size = len(value)
            archive.addfile(member, io.BytesIO(value))
        findings = verifier.scan_distribution(sdist)
        assert [finding.rule for finding in findings] == ["aws-access-key"]
