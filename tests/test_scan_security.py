"""Tests for scan-time path-safety controls (Phase 5 threat model, 2026-07-13).

A scanned repository is untrusted input (e.g. a third-party PR scanned in
CI). Two verified gaps were closed in scripts/report.py:_is_safe_to_scan:

  1. symlink_escape — a symlink inside the scan root that resolves outside
     project_root was previously followed and its content scanned. This
     let a malicious repository read arbitrary files reachable by the
     scanning process (CI secrets, SSH keys, /etc/passwd, etc).
  2. oversized       — filepath.read_bytes() had no size limit, so a single
     huge file (accidental or adversarial) could exhaust memory.

Both are reproduced here exactly as they were reproduced manually before
the fix, and asserted closed. A skipped file of either kind must also mark
the scan as partial (completion_status == "completed_with_skips"), since a
prohibited pattern could be hiding in the excluded content — the same
invariant as the F1-F5 skip-accounting fixes.

These tests run under both the custom runner (tests/test_classification.py)
and pytest, following the tests/test_analysis_manifest.py convention.
"""

import json
import os
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
_CLI = _REPO / "scripts" / "cli.py"


def _run_check(project_arg, out_dir):
    """Invoke `regula check` as a subprocess; return (exit_code, manifest_dict)."""
    sarif = Path(out_dir) / "out.sarif"
    manifest = Path(out_dir) / "m.json"
    proc = subprocess.run(
        [sys.executable, str(_CLI), "check", str(project_arg),
         "--format", "sarif", "--output", str(sarif),
         "--manifest", str(manifest)],
        capture_output=True, text=True, timeout=120,
    )
    m = json.loads(manifest.read_text()) if manifest.exists() else None
    return proc.returncode, m


def test_symlink_escape_is_not_followed():
    """A symlink inside the scan root pointing to a file OUTSIDE the root
    must not be read. Reproduces the verified pre-fix behaviour: the
    symlinked file's content (containing a prohibited-pattern trigger) was
    silently scanned and could have been reported."""
    with tempfile.TemporaryDirectory() as d:
        outside = Path(d) / "outside"
        outside.mkdir()
        secret = outside / "secret.py"
        secret.write_text(
            "def social_credit_score(citizen):\n"
            "    return compute_social_score(citizen.behavior_history)\n"
        )

        proj = Path(d) / "proj"
        proj.mkdir()
        link = proj / "linked.py"
        try:
            link.symlink_to(secret)
        except OSError:
            return  # symlinks unsupported on this platform/filesystem — skip

        exit_code, m = _run_check(proj, d)
        assert exit_code == 0, "the escaped file's prohibited pattern must NOT be reported"
        assert m is not None
        assert m["counts"]["findings_total"] == 0, (
            "content outside the scan root must never produce a finding"
        )
        assert m["completion_status"] == "completed_with_skips", m["completion_status"]
        assert m["counts"]["skip_reasons"].get("symlink_escape", 0) >= 1
        assert any("linked.py" in e["path"] for e in m["skipped_files"])


def test_symlink_within_project_root_is_still_scanned():
    """A symlink that resolves to a target INSIDE the project root is safe
    and legitimate (e.g. a monorepo convenience symlink) — it must still be
    scanned normally, not rejected as an escape (false-positive check)."""
    with tempfile.TemporaryDirectory() as d:
        proj = Path(d) / "proj"
        proj.mkdir()
        real = proj / "real.py"
        real.write_text(
            "def social_credit_score(citizen):\n"
            "    return compute_social_score(citizen.behavior_history)\n"
        )
        link = proj / "alias.py"
        try:
            link.symlink_to(real)
        except OSError:
            return  # symlinks unsupported on this platform/filesystem — skip

        exit_code, m = _run_check(proj, d)
        assert m is not None
        # Two files resolve to the same content; at least one must be scanned
        # and the finding reported — an in-root symlink is not a threat.
        assert m["counts"]["findings_total"] >= 1
        assert exit_code == 1


def test_oversized_file_is_rejected_before_reading():
    """A file exceeding MAX_FILE_SIZE_BYTES must be skipped WITHOUT being
    read into memory, and the scan must be marked partial. Reproduces the
    verified pre-fix behaviour: read_bytes() had no size ceiling."""
    with tempfile.TemporaryDirectory() as d:
        proj = Path(d) / "proj"
        proj.mkdir()
        huge = proj / "huge.py"
        # Sparse file: 11 MB, exceeds the 10 MB MAX_FILE_SIZE_BYTES limit.
        with open(huge, "wb") as f:
            f.seek(11 * 1024 * 1024)
            f.write(b"\0")

        exit_code, m = _run_check(proj, d)
        assert exit_code == 0
        assert m is not None
        assert m["completion_status"] == "completed_with_skips", m["completion_status"]
        assert m["counts"]["skip_reasons"].get("oversized", 0) >= 1
        assert any("huge.py" in e["path"] for e in m["skipped_files"])


def test_file_under_size_limit_scans_normally():
    """A normal-sized file well under the limit must be completely
    unaffected by the size check (regression / false-positive check)."""
    with tempfile.TemporaryDirectory() as d:
        proj = Path(d) / "proj"
        proj.mkdir()
        (proj / "app.py").write_text(
            "def social_credit_score(citizen):\n"
            "    return compute_social_score(citizen.behavior_history)\n"
        )
        exit_code, m = _run_check(proj, d)
        assert exit_code == 1
        assert m["completion_status"] == "completed"
        assert m["counts"]["skipped_total"] == 0
        assert m["counts"]["findings_total"] >= 1
