"""Tests for scripts/tree_guard.py, working-tree drift detection.

Every test builds its own throwaway git repository so nothing here reads or
mutates the real working tree; the guard exists precisely because that tree
has changed outside recorded sessions, and a test that relied on it would
inherit the same exposure.
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import tree_guard  # noqa: E402


def _make_repo(tmp):
    """A minimal repo: one committed file, clean tree."""
    root = Path(tmp)
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "t@t"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=root, check=True)
    (root / "a.txt").write_text("committed content\n")
    subprocess.run(["git", "add", "a.txt"], cwd=root, check=True)
    subprocess.run(["git", "commit", "-qm", "init"], cwd=root, check=True)
    return root


def _rebind(root):
    """Point the module at the throwaway repo for the duration of a test."""
    saved = (tree_guard.REPO_ROOT, tree_guard.STATE_PATH)
    tree_guard.REPO_ROOT = root
    tree_guard.STATE_PATH = root / ".claude" / "tree-state.json"
    return saved


def _restore(saved):
    tree_guard.REPO_ROOT, tree_guard.STATE_PATH = saved


def test_clean_tree_records_and_matches():
    """Record on a clean tree, compare immediately: no drift."""
    with tempfile.TemporaryDirectory() as tmp:
        root = _make_repo(tmp)
        saved = _rebind(root)
        try:
            tree_guard.record(note="test baseline")
            drift = tree_guard.compare()
            assert drift == [], f"expected no drift, got {drift}"
        finally:
            _restore(saved)


def test_planted_change_is_named_then_restore_passes():
    """The control the guard exists for, run both ways: plant a change
    between the record and the check, confirm the check names the exact
    path; restore, confirm it passes again."""
    with tempfile.TemporaryDirectory() as tmp:
        root = _make_repo(tmp)
        saved = _rebind(root)
        try:
            tree_guard.record()
            (root / "a.txt").write_text("mutated outside any session\n")
            drift = tree_guard.compare()
            assert drift, "planted change was not detected"
            assert any("a.txt" in line for line in drift), \
                f"drift does not name the mutated path: {drift}"
            (root / "a.txt").write_text("committed content\n")
            drift = tree_guard.compare()
            assert drift == [], f"restore should clear the drift, got {drift}"
        finally:
            _restore(saved)


def test_silent_revert_to_head_is_detected():
    """The recorded incident class: a file that was modified at record time
    reverts to byte-identical HEAD content, so it vanishes from
    `git status`. The path-set comparison must name it."""
    with tempfile.TemporaryDirectory() as tmp:
        root = _make_repo(tmp)
        saved = _rebind(root)
        try:
            (root / "a.txt").write_text("session edit in progress\n")
            tree_guard.record()
            # The silent revert: back to exactly the committed bytes.
            (root / "a.txt").write_text("committed content\n")
            drift = tree_guard.compare()
            assert drift, "silent revert to HEAD content was not detected"
            assert any("a.txt" in line and "no longer modified" in line
                       for line in drift), f"unexpected drift shape: {drift}"
        finally:
            _restore(saved)


def test_new_untracked_file_is_detected():
    """A file appearing from nowhere is drift too."""
    with tempfile.TemporaryDirectory() as tmp:
        root = _make_repo(tmp)
        saved = _rebind(root)
        try:
            tree_guard.record()
            (root / "dropped-in.py").write_text("print('who wrote this')\n")
            drift = tree_guard.compare()
            assert any("dropped-in.py" in line for line in drift), \
                f"new file not named: {drift}"
        finally:
            _restore(saved)


def test_head_move_is_reported():
    """A commit made between record and check is drift (attributable via
    the reflog, but the guard must still surface it)."""
    with tempfile.TemporaryDirectory() as tmp:
        root = _make_repo(tmp)
        saved = _rebind(root)
        try:
            tree_guard.record()
            (root / "b.txt").write_text("second file\n")
            subprocess.run(["git", "add", "b.txt"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "second"], cwd=root, check=True)
            drift = tree_guard.compare()
            assert any("HEAD moved" in line for line in drift), \
                f"HEAD move not reported: {drift}"
        finally:
            _restore(saved)


def test_cli_exit_codes_discriminate():
    """--check exits 0 clean, 3 on drift, 2 with no baseline; --status
    always 0. The distinct drift code exists so a caller can branch on it
    without parsing prose."""
    with tempfile.TemporaryDirectory() as tmp:
        root = _make_repo(tmp)
        saved = _rebind(root)
        try:
            assert tree_guard.main(["--check"]) == 2, "no baseline must exit 2"
            assert tree_guard.main(["--status"]) == 0
            tree_guard.record()
            assert tree_guard.main(["--check"]) == 0, "clean must exit 0"
            (root / "a.txt").write_text("drifted\n")
            assert tree_guard.main(["--check"]) == 3, "drift must exit 3"
            assert tree_guard.main(["--status"]) == 0, "--status never fails"
        finally:
            _restore(saved)


def test_stamp_silent_without_baseline_and_loud_with_drift():
    """stamp() must stay silent when no baseline exists (test environments,
    fresh clones), emit a MATCHES line when clean, and name paths on drift,
    all without raising or touching exit codes."""
    import io
    with tempfile.TemporaryDirectory() as tmp:
        root = _make_repo(tmp)
        saved = _rebind(root)
        try:
            out = io.StringIO()
            tree_guard.stamp(stream=out)
            assert out.getvalue() == "", \
                f"stamp must be silent with no baseline, got {out.getvalue()!r}"
            tree_guard.record()
            out = io.StringIO()
            tree_guard.stamp(stream=out)
            assert "matches baseline" in out.getvalue()
            (root / "a.txt").write_text("drifted\n")
            out = io.StringIO()
            tree_guard.stamp(stream=out)
            assert "TREE CHANGED" in out.getvalue()
            assert "a.txt" in out.getvalue()
        finally:
            _restore(saved)


def test_change_inside_small_ignored_dir_is_detected():
    """The motivating incident class: a gitignored directory inside a
    tracked fixture (.regula/registry/) fed a published measurement, and a
    plain-porcelain guard cannot see it. Files in small ignored dirs are
    hashed individually, so a content change there is named."""
    with tempfile.TemporaryDirectory() as tmp:
        root = _make_repo(tmp)
        saved = _rebind(root)
        try:
            (root / ".gitignore").write_text(".hidden/\n.claude/\n")
            subprocess.run(["git", "add", ".gitignore"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "ignore"], cwd=root, check=True)
            hidden = root / ".hidden"
            hidden.mkdir()
            (hidden / "registry.json").write_text('{"v": 1}\n')
            tree_guard.record()
            (hidden / "registry.json").write_text('{"v": 2}\n')
            drift = tree_guard.compare()
            assert any(".hidden/registry.json" in line
                       and "content changed" in line for line in drift), \
                f"ignored-file mutation not named: {drift}"
            (hidden / "registry.json").write_text('{"v": 1}\n')
            drift = tree_guard.compare()
            assert drift == [], f"restore should clear the drift, got {drift}"
        finally:
            _restore(saved)


def test_large_ignored_dir_recorded_as_count_only():
    """Above the budget an ignored directory costs one presence-and-count
    entry (the .venv class), and a file-count change is still drift."""
    with tempfile.TemporaryDirectory() as tmp:
        root = _make_repo(tmp)
        saved = _rebind(root)
        try:
            (root / ".gitignore").write_text("bulk/\n.claude/\n")
            subprocess.run(["git", "add", ".gitignore"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "ignore"], cwd=root, check=True)
            bulk = root / "bulk"
            bulk.mkdir()
            budget = tree_guard.IGNORED_DIR_HASH_BUDGET
            for i in range(budget + 1):
                (bulk / f"f{i}.txt").write_text(str(i))
            tree_guard.record()
            state = json.loads(tree_guard.STATE_PATH.read_text())
            assert state["entries"].get("bulk/", {}).get("blob") == \
                f"count:{budget + 1}", "large dir must record count only"
            (bulk / "extra.txt").write_text("one more")
            drift = tree_guard.compare()
            assert any("bulk/" in line for line in drift), \
                f"count change in large ignored dir not surfaced: {drift}"
        finally:
            _restore(saved)


def test_state_file_is_gitignored_in_this_repo():
    """Recording a baseline must not itself dirty the tree it measures.
    This is the one test that reads the REAL repository, read-only."""
    real_root = Path(__file__).resolve().parent.parent
    result = subprocess.run(
        ["git", "check-ignore", ".claude/tree-state.json"],
        cwd=real_root, capture_output=True, text=True,
    )
    assert result.returncode == 0, \
        ".claude/tree-state.json must be gitignored or recording state dirties the tree"


if __name__ == "__main__":
    tests = [
        test_clean_tree_records_and_matches,
        test_planted_change_is_named_then_restore_passes,
        test_silent_revert_to_head_is_detected,
        test_new_untracked_file_is_detected,
        test_head_move_is_reported,
        test_cli_exit_codes_discriminate,
        test_stamp_silent_without_baseline_and_loud_with_drift,
        test_change_inside_small_ignored_dir_is_detected,
        test_large_ignored_dir_recorded_as_count_only,
        test_state_file_is_gitignored_in_this_repo,
    ]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"  PASS: {t.__name__}")
        except Exception as e:
            failed += 1
            print(f"  FAIL: {t.__name__}: {e}")
    print(f"Results: {len(tests) - failed} passed, {failed} failed")
    sys.exit(1 if failed else 0)
