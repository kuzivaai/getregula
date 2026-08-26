"""Tests for scan-time path-safety and CPU/memory-exhaustion controls
(Phase 5 threat model, 2026-07-13 and 2026-07-14).

A scanned repository is untrusted input (e.g. a third-party PR scanned in
CI). Verified gaps closed in scripts/report.py and scripts/ast_context.py:

  1. symlink_escape             — a symlink inside the scan root resolving
     outside project_root was previously followed and its content scanned.
     Let a malicious repository read arbitrary files reachable by the
     scanning process (CI secrets, SSH keys, /etc/passwd, etc).
  2. oversized                  — filepath.read_bytes() had no size limit,
     so a single huge file (accidental or adversarial) could exhaust memory.
  3. oversized_for_classification — several built-in prohibited/high-risk
     regex patterns use a (?:word)[^"\n]{0,30}(?:word) shape applied via
     re.search() against WHOLE-FILE content. Dense adversarial repetition
     of the leading trigger word degrades near-linearly with length:
     measured 27.8s worst-case on a 10MB adversarial file across the full
     4-call classification pipeline. MAX_CLASSIFY_CHARS bounds this.
  4. ast.parse() MemoryError    — CPython's own parser can raise MemoryError
     on pathological (but TINY, ~10-20 KB) input consisting of many bare
     word tokens with no other structure. This was uncaught in
     build_context_map() and crashed the scan of the ENTIRE repository
     (not just the one file) with no manifest written — a single small
     adversarial or malformed .py file anywhere in a repo denied service
     to scanning every other file in it.

The SAME MemoryError gap (item 4) was also present at 7 further ast.parse()
call sites outside the main scan loop, found by grepping the whole codebase
for every ast.parse() call after fixing build_context_map():
  - scripts/ast_analysis.py (5 sites): parse_python_file, classify_context,
    trace_ai_data_flow, detect_human_oversight, detect_logging_practices.
    Reachable from `regula gap` (scripts/compliance_check.py) — reproduced
    a silent failure: `regula gap` on a project containing one ~20KB
    adversarial file exited 0 with a generic "Internal error" and NO real
    gap-analysis output, rather than the genuine report it should produce.
  - scripts/cross_file_flow.py (2 sites): _build_symbol_table,
    build_import_map. Reachable from analyse_project_oversight(), which
    report.py's --enrich-oversight path already wraps in a bare
    `except Exception` (MemoryError/RecursionError both derive from
    Exception, so that ONE call site was accidentally resilient already —
    verified by direct reproduction — but the underlying ast.parse() calls
    themselves were still unhardened, and analyse_project_oversight() is
    also called directly/reachable from other contexts without that
    wrapper, e.g. scripts/compliance_check.py).
All 7 were fixed identically to build_context_map(): add
(MemoryError, RecursionError) to each except clause, returning the same
graceful-degradation value already used for SyntaxError.

All are reproduced here exactly as they were reproduced manually before
the fix, and asserted closed. A skipped file of any dangerous-skip kind
must also mark the scan as partial (completion_status ==
"completed_with_skips"), since a prohibited pattern could be hiding in the
excluded content — the same invariant as the F1-F5 skip-accounting fixes.

These tests run under both the custom runner (tests/test_classification.py)
and pytest, following the tests/test_analysis_manifest.py convention.
"""

import json
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


def test_dense_trigger_content_is_capped_for_classification():
    """A file saturated with a regex trigger keyword (dense repetition of
    e.g. "score ") must not cause pathological classification slowdown.
    Reproduces the verified pre-fix cost: a single such pattern took 2.48s
    on a 10MB file, and the full classification pipeline took 27.8s.
    Content beyond MAX_CLASSIFY_CHARS is truncated for classification and
    the file is marked as a dangerous (partial-scan) skip."""
    import time
    with tempfile.TemporaryDirectory() as d:
        proj = Path(d) / "proj"
        proj.mkdir()
        # ~2.9 MB of dense trigger-word repetition — well over
        # MAX_CLASSIFY_CHARS (1 MB) but under MAX_FILE_SIZE_BYTES (10 MB),
        # so it reaches the classification cap specifically.
        (proj / "adversarial.py").write_text("score " * 500_000)

        start = time.perf_counter()
        exit_code, m = _run_check(proj, d)
        elapsed = time.perf_counter() - start

        assert elapsed < 15.0, (
            f"classification took {elapsed:.1f}s on adversarial content; "
            "expected the MAX_CLASSIFY_CHARS cap to bound this well under "
            "the un-capped worst case (27.8s measured pre-fix on 10MB)"
        )
        assert exit_code == 0
        assert m["completion_status"] == "completed_with_skips", m["completion_status"]
        assert m["counts"]["skip_reasons"].get("oversized_for_classification", 0) >= 1


def test_ast_parse_memory_error_does_not_crash_entire_scan():
    """A tiny (~20 KB) file consisting of many bare word tokens with no
    other Python structure can make CPython's own ast.parse() raise
    MemoryError. Before the fix, this was uncaught in
    ast_context.build_context_map() and crashed the scan of the ENTIRE
    project — including losing findings in unrelated, legitimate files —
    with exit code 2 and no manifest written. After the fix, the crashing
    file degrades gracefully (same as a SyntaxError) and every other file
    in the project is still scanned and reported correctly."""
    with tempfile.TemporaryDirectory() as d:
        proj = Path(d) / "proj"
        proj.mkdir()
        # Reproduces the exact minimal trigger verified during investigation:
        # ast.parse("a " * 5000) raises MemoryError in CPython 3.11.
        (proj / "tiny_crash.py").write_text("a " * 10000)
        (proj / "normal.py").write_text(
            "def social_credit_score(citizen):\n"
            "    return compute_social_score(citizen.behavior_history)\n"
        )

        exit_code, m = _run_check(proj, d)

        assert exit_code == 1, (
            "the legitimate prohibited finding in normal.py must still be "
            "detected and reported even though tiny_crash.py would have "
            "crashed ast.parse() prior to the fix"
        )
        assert m is not None, (
            "a manifest must be written — the crash must not abort the "
            "whole scan before completion"
        )
        assert m["completion_status"] == "completed"
        assert m["counts"]["scanned"] == 2
        assert m["counts"]["prohibited"] >= 1


def test_regula_gap_does_not_crash_on_pathological_file():
    """The SAME MemoryError gap (DEF-007) was also present in
    scripts/ast_analysis.py's 5 ast.parse() call sites, reachable from the
    separate `regula gap` command (scripts/compliance_check.py) rather than
    the main scan loop. Before the fix, `regula gap` on a project containing
    one ~20 KB adversarial file exited 0 with a generic "Internal error" and
    produced NO real gap-analysis output — silently failing while reporting
    success. After the fix, it completes and produces its genuine report."""
    with tempfile.TemporaryDirectory() as d:
        proj = Path(d) / "proj"
        proj.mkdir()
        (proj / "tiny_crash.py").write_text("a " * 10000)

        proc = subprocess.run(
            [sys.executable, str(_CLI), "gap", str(proj)],
            capture_output=True, text=True, timeout=60,
        )

        assert "Internal error" not in proc.stdout, (
            "regula gap must not silently swallow the crash and print a "
            "generic internal-error message instead of a real report"
        )
        # The evidence-gated result is the genuine report for an input that
        # supplies no sourced applicability facts. Its tagged decision and
        # actionable fact list prove the command completed instead of
        # failing silently or manufacturing article gaps.
        assert "Decision: insufficient_information" in proc.stdout, (
            f"expected a real gap-analysis report, got: {proc.stdout[:300]!r}"
        )
        assert "Facts needed to resolve the next decision" in proc.stdout
        assert "Overall readiness" not in proc.stdout


def test_analyse_project_oversight_does_not_crash():
    """The SAME MemoryError gap was also present in the 2 ast.parse() call
    sites in scripts/cross_file_flow.py (_build_symbol_table,
    build_import_map), reachable via analyse_project_oversight(). Direct
    reproduction confirmed this crashed uncaught prior to the fix, even
    though report.py's --enrich-oversight integration point happened to
    already be protected by an unrelated bare `except Exception` (which
    catches MemoryError/RecursionError as a side effect, not by design)."""
    with tempfile.TemporaryDirectory() as d:
        proj = Path(d) / "proj"
        proj.mkdir()
        (proj / "tiny_crash.py").write_text("a " * 10000)

        sys.path.insert(0, str(_REPO / "scripts"))
        from cross_file_flow import analyse_project_oversight
        result = analyse_project_oversight(str(proj))

        assert result.get("analysed") is True, (
            f"expected a completed analysis, got: {result}"
        )
