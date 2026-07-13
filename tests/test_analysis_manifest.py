"""Tests for the AnalysisManifest completion signal (DEF-004).

The manifest is Regula's proof-of-scan-completion. A CI gate uses its presence
and `completion_status == "completed"` to distinguish a genuinely clean scan
from a failed/empty/malformed one, so that a broken scan can never report a
green compliance gate (fail closed).

These tests run under both the custom runner (tests/test_classification.py)
and pytest. They avoid pytest fixtures (tmp_path/monkeypatch) by creating and
cleaning up their own temp directories, so the custom runner picks them up via
its globals() walk.
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
_CLI = _REPO / "scripts" / "cli.py"


def _run_check(project_arg, out_dir, extra=None):
    """Invoke `regula check` as a subprocess; return (exit_code, out_dir)."""
    sarif = Path(out_dir) / "out.sarif"
    manifest = Path(out_dir) / "m.json"
    cmd = [
        sys.executable, str(_CLI), "check", str(project_arg),
        "--format", "sarif", "--output", str(sarif),
        "--manifest", str(manifest),
    ]
    if extra:
        cmd.extend(extra)
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    return proc.returncode, Path(out_dir)


def test_manifest_written_on_clean_scan():
    """AC5: an empty project scans successfully and produces a completed
    manifest with zero findings — a clean scan of nothing, distinct from a
    failure."""
    with tempfile.TemporaryDirectory() as d:
        proj = Path(d) / "proj"
        proj.mkdir()
        exit_code, out = _run_check(proj, d)
        manifest_path = out / "m.json"
        assert exit_code == 0, f"expected exit 0, got {exit_code}"
        assert manifest_path.exists(), "manifest must be written on clean scan"
        m = json.loads(manifest_path.read_text())
        assert m["completion_status"] == "completed"
        assert m["exit_code"] == 0
        assert m["counts"]["findings_total"] == 0
        assert m["counts"]["prohibited"] == 0
        assert m["counts"]["skipped_total"] == 0
        assert m["manifest_version"] == "3"


def test_manifest_records_prohibited_finding():
    """AC2: a prohibited pattern yields exit 1, a completed manifest, an exact
    prohibited count, and a SARIF digest."""
    with tempfile.TemporaryDirectory() as d:
        proj = Path(d) / "proj"
        proj.mkdir()
        # social scoring of natural persons — Article 5 prohibited indicator
        (proj / "s.py").write_text(
            "def social_credit_score(citizen):\n"
            "    return compute_social_score(citizen.behavior_history)\n"
        )
        exit_code, out = _run_check(proj, d)
        m = json.loads((out / "m.json").read_text())
        assert exit_code == 1, f"expected exit 1 on BLOCK finding, got {exit_code}"
        assert m["completion_status"] == "completed"
        assert m["exit_code"] == 1
        assert m["counts"]["prohibited"] >= 1
        assert m["counts"]["findings_total"] >= 1
        assert m["sarif_sha256"] is not None and len(m["sarif_sha256"]) == 64


def test_no_manifest_on_scan_failure():
    """AC3/AC4: scanning a nonexistent path fails (exit 2) and writes NO
    manifest. The absence is the failure signal the CI gate relies on."""
    with tempfile.TemporaryDirectory() as d:
        missing = Path(d) / "does_not_exist"
        exit_code, out = _run_check(missing, d)
        assert exit_code == 2, f"expected exit 2 on bad path, got {exit_code}"
        assert not (out / "m.json").exists(), (
            "manifest must NOT exist after a failed scan"
        )


def test_unknown_counts_are_null_not_fabricated():
    """Per the fix's honesty constraint: per-file counts genuinely not measured
    by scan_files() are recorded as null, never guessed. (scanned IS measured
    now; discovered/eligible/unsupported remain unmeasured.)"""
    with tempfile.TemporaryDirectory() as d:
        proj = Path(d) / "proj"
        proj.mkdir()
        (proj / "ok.py").write_text("x = 1\n")
        _exit_code, out = _run_check(proj, d)
        m = json.loads((out / "m.json").read_text())
        for k in ("discovered", "eligible", "unsupported"):
            assert m["counts"][k] is None, f"{k} should be null (unknown), not fabricated"
        # scanned IS measured — must be a real integer, not null.
        assert isinstance(m["counts"]["scanned"], int)


def test_corrupt_notebook_forces_partial_status():
    """Review F1: a corrupt/unparseable notebook is skipped by the scanner.
    The manifest must report completion_status='completed_with_skips' (NOT
    'completed') so a CI gate fails closed — a prohibited pattern could hide
    in the file that was not analysed."""
    with tempfile.TemporaryDirectory() as d:
        proj = Path(d) / "proj"
        proj.mkdir()
        # Not valid notebook JSON — extract_code returns "" and the file is skipped.
        (proj / "bad.ipynb").write_text("{ this is not valid notebook json")
        _exit_code, out = _run_check(proj, d)
        m = json.loads((out / "m.json").read_text())
        assert m["completion_status"] == "completed_with_skips", m["completion_status"]
        assert m["counts"]["skipped_total"] >= 1
        assert m["counts"]["skip_reasons"].get("notebook_corrupt", 0) >= 1
        assert any("bad.ipynb" in e["path"] for e in m["skipped_files"])


def test_unreadable_file_forces_partial_status():
    """Review F1: a file that cannot be read (permission denied) is skipped;
    the manifest must flag the partial scan."""
    import os
    import stat
    with tempfile.TemporaryDirectory() as d:
        proj = Path(d) / "proj"
        proj.mkdir()
        secret = proj / "locked.py"
        secret.write_text("x = 1\n")
        os.chmod(secret, 0)  # remove all perms
        try:
            # Skip if running as root (root bypasses permission bits).
            if os.getuid() == 0:
                return
        except AttributeError:
            pass  # non-POSIX; attempt anyway
        try:
            _exit_code, out = _run_check(proj, d)
            m = json.loads((out / "m.json").read_text())
            # If the OS still let us read it, the scan is clean — only assert
            # the partial path when a skip actually occurred.
            if m["counts"]["skipped_total"] >= 1:
                assert m["completion_status"] == "completed_with_skips"
                assert m["counts"]["skip_reasons"].get("unreadable", 0) >= 1
        finally:
            os.chmod(secret, stat.S_IRUSR | stat.S_IWUSR)  # restore for cleanup


def test_json_format_also_writes_manifest():
    """The manifest must be produced for --format json too (not only sarif).
    sarif_sha256 is null when no SARIF was written."""
    with tempfile.TemporaryDirectory() as d:
        proj = Path(d) / "proj"
        proj.mkdir()
        (proj / "ok.py").write_text("x = 1\n")
        manifest = Path(d) / "mj.json"
        proc = subprocess.run(
            [sys.executable, str(_CLI), "check", str(proj),
             "--format", "json", "--manifest", str(manifest)],
            capture_output=True, text=True, timeout=120,
        )
        assert proc.returncode == 0
        assert manifest.exists(), "manifest must be written for --format json"
        m = json.loads(manifest.read_text())
        assert m["completion_status"] == "completed"
        assert m["sarif_sha256"] is None


def test_manifest_optional_omitting_it_still_scans():
    """AC10: omitting --manifest reproduces legacy behaviour (scan still runs,
    no manifest, exit code unchanged)."""
    with tempfile.TemporaryDirectory() as d:
        proj = Path(d) / "proj"
        proj.mkdir()
        (proj / "ok.py").write_text("x = 1\n")
        sarif = Path(d) / "out.sarif"
        proc = subprocess.run(
            [sys.executable, str(_CLI), "check", str(proj),
             "--format", "sarif", "--output", str(sarif)],
            capture_output=True, text=True, timeout=120,
        )
        assert proc.returncode == 0
        assert sarif.exists()
        assert not (Path(d) / "m.json").exists()


def test_annotation_only_prohibited_not_dropped():
    """Review F1 (HIGH): a .py file with a prohibited phrase but no
    def/class/call/assignment token must NOT be silently dropped by the
    annotation-only precision filter. The prohibited finding must be emitted
    and the exit code must be 1 (BLOCK) — not a green PASS."""
    with tempfile.TemporaryDirectory() as d:
        proj = Path(d) / "proj"
        proj.mkdir()
        # No def/class/call/BOL-assignment — this used to be skipped entirely.
        (proj / "annot.py").write_text('x: "predictive policing"\n')
        exit_code, out = _run_check(proj, d)
        m = json.loads((out / "m.json").read_text())
        assert m["counts"]["prohibited"] >= 1, (
            "prohibited pattern in an annotation-only file must be detected"
        )
        assert exit_code == 1, f"expected BLOCK exit 1, got {exit_code}"
        # It was analysed, so it is a clean completion (no skip).
        assert m["completion_status"] == "completed"


def test_non_utf8_file_forces_partial_status():
    """Review F2 (MED): a non-UTF-8 (e.g. UTF-16) source file was previously
    read with errors='ignore' and scanned as garbage, hiding any pattern. It
    must now be recorded as an undecodable skip so the scan is partial."""
    with tempfile.TemporaryDirectory() as d:
        proj = Path(d) / "proj"
        proj.mkdir()
        # UTF-16 encoded Python — invalid UTF-8.
        (proj / "enc.py").write_bytes('x = "predictive policing"\n'.encode("utf-16"))
        _exit_code, out = _run_check(proj, d)
        m = json.loads((out / "m.json").read_text())
        assert m["completion_status"] == "completed_with_skips", m["completion_status"]
        assert m["counts"]["skip_reasons"].get("undecodable", 0) >= 1


def test_notebook_partial_cells_forces_partial_status():
    """Review F3 (MED): a notebook that parses but has a code cell with an
    unusable (non-string) source drops that cell. The scan is partial."""
    with tempfile.TemporaryDirectory() as d:
        proj = Path(d) / "proj"
        proj.mkdir()
        nb = {
            "cells": [
                {"cell_type": "code", "source": "import os\n"},
                {"cell_type": "code", "source": 12345},  # unusable → dropped
            ],
            "metadata": {}, "nbformat": 4, "nbformat_minor": 5,
        }
        (proj / "partial.ipynb").write_text(json.dumps(nb))
        _exit_code, out = _run_check(proj, d)
        m = json.loads((out / "m.json").read_text())
        assert m["completion_status"] == "completed_with_skips", m["completion_status"]
        assert m["counts"]["skip_reasons"].get("notebook_partial", 0) >= 1


def test_empty_valid_notebook_is_not_a_skip():
    """Review F4 (MED / false-positive): a VALID notebook with zero code cells
    (markdown-only / freshly created) must be a clean completion, NOT flagged
    as a skip — otherwise benign, common input breaks CI."""
    with tempfile.TemporaryDirectory() as d:
        proj = Path(d) / "proj"
        proj.mkdir()
        nb = {
            "cells": [{"cell_type": "markdown", "source": ["# notes"]}],
            "metadata": {}, "nbformat": 4, "nbformat_minor": 5,
        }
        (proj / "notes.ipynb").write_text(json.dumps(nb))
        exit_code, out = _run_check(proj, d)
        m = json.loads((out / "m.json").read_text())
        assert m["completion_status"] == "completed", m["completion_status"]
        assert m["counts"]["skipped_total"] == 0
        assert exit_code == 0
