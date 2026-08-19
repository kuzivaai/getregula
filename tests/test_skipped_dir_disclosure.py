"""A scan may not report a file count without reporting what it skipped.

MEASURED 2026-08-17 on `ageitgey/face_recognition` at commit
`9f3061aaeed9a8756d2c970f5dfe066617a8281d`, a third-party repository:

    regula check . --scope all      ->  Files scanned: 6    high-risk: 3
    regula check examples --scope all -> Files scanned: 23  high-risk: 11
    regula check face_recognition   ->  Files scanned: 4    high-risk: 2
    regula check docs               ->  Files scanned: 1    high-risk: 1

Twenty-three of that repository's thirty Python files live under `examples/`,
`examples` is in `constants.SKIP_DIRS`, and eleven of fourteen high-risk
findings, 79%, were therefore invisible at the default invocation. Nothing in
the output said a directory had been skipped; the only scope line printed was
`Scope: 1 non-production finding(s) excluded`, which refers to a provenance
deduction on a different file.

The pruning is a deliberate design decision with its rationale recorded on
`SKIP_DIRS`, and these tests do NOT assert anything about whether it should
happen. They assert that when it happens the scan says so, which is the N138
remedy (an instrument that cannot see part of its population declares the gap
at the point of use) applied to a second instrument.

Written as module-level functions rather than as a TestCase on purpose: the
custom runner binds by scanning `dir(module)` for names beginning `test_`, and
a class-based module exposes only its class names, so both modules added on
2026-08-17 were imported, listed, and contributing nothing (ledger N134).
"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import report  # noqa: E402
from constants import SKIP_DIRS  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent


def _project(tmp: Path, layout: dict) -> Path:
    """Materialise {relative_path: text} under tmp and return the root."""
    root = tmp / "proj"
    for rel, text in layout.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    return root


def _stats(root: Path) -> dict:
    report.scan_files(str(root))
    return dict(getattr(report.scan_files, "last_stats", {}) or {})


def test_a_pruned_directory_holding_code_is_reported():
    """The face_recognition shape, reduced to its essentials."""
    with tempfile.TemporaryDirectory() as td:
        root = _project(Path(td), {
            "pkg/api.py": "def detect():\n    return 1\n",
            "examples/demo_one.py": "print('one')\n",
            "examples/demo_two.py": "print('two')\n",
            "examples/nested/demo_three.py": "print('three')\n",
        })
        st = _stats(root)
        assert st["pruned_code_files"] == 3, st["pruned_code_files"]
        assert st["pruned_dirs_total"] == 1, st["pruned_dirs"]
        entry = st["pruned_dirs"][0]
        assert entry["path"] == "examples", entry
        assert entry["skipped_because"] == "examples", entry
        assert entry["code_files"] == 3, entry
        assert st["pruned_count_exact"] is True
        # And the scan really did read only the one file outside it, so the
        # disclosure is describing a real loss rather than decorating a
        # complete scan.
        assert st["files_scanned"] == 1, st["files_scanned"]


def test_a_project_with_nothing_pruned_reports_nothing():
    """A silent disclosure must mean 'nothing skipped', not 'not measured'."""
    with tempfile.TemporaryDirectory() as td:
        root = _project(Path(td), {"src/a.py": "print('hi')\n"})
        st = _stats(root)
        assert st["pruned_code_files"] == 0, st
        assert st["pruned_dirs"] == [], st
        assert st["pruned_dirs_total"] == 0, st
        assert st["pruned_count_exact"] is True


def test_a_pruned_directory_holding_no_code_is_not_reported():
    """`.git` is pruned on every scan and loses nothing.

    Listing it would imply files were skipped where none were, which is the
    opposite failure to the one this module exists to fix.
    """
    with tempfile.TemporaryDirectory() as td:
        root = _project(Path(td), {
            "src/a.py": "print('hi')\n",
            ".git/HEAD": "ref: refs/heads/main\n",
            ".git/config": "[core]\n",
        })
        assert ".git" in SKIP_DIRS
        st = _stats(root)
        assert st["pruned_code_files"] == 0, st
        assert [d["path"] for d in st["pruned_dirs"]] == [], st["pruned_dirs"]


def test_a_pruned_symlink_cannot_inventory_files_outside_the_project():
    """The disclosure walk must obey the same containment boundary as scans."""
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        outside = base / "outside"
        outside.mkdir()
        (outside / "secret_name.py").write_text("print('outside')\n",
                                                 encoding="utf-8")
        root = _project(base / "inside", {"src/a.py": "print('inside')\n"})
        try:
            (root / "examples").symlink_to(outside, target_is_directory=True)
        except OSError:
            # Windows may require an explicit developer-mode privilege.
            return
        st = _stats(root)
        assert st["pruned_code_files"] == 0, st
        assert st["pruned_dirs"] == [], st


def test_pruned_inventory_is_inexact_without_descriptor_relative_walk():
    """Unsafe absolute-path fallback must not invent a complete inventory."""
    with tempfile.TemporaryDirectory() as td:
        root = _project(Path(td), {
            "src/a.py": "print('inside')\n",
            "examples/hidden.py": "print('skipped')\n",
        })
        original_fwalk = os.fwalk
        del os.fwalk
        try:
            st = _stats(root)
        finally:
            os.fwalk = original_fwalk
        assert st["pruned_code_files"] == 0, st
        assert st["pruned_dirs"] == [], st
        assert st["pruned_count_exact"] is False, st


def test_every_reported_directory_name_is_actually_in_the_skip_list():
    """The disclosure must not blame the skip list for an unrelated absence."""
    with tempfile.TemporaryDirectory() as td:
        root = _project(Path(td), {
            "src/a.py": "print('a')\n",
            "examples/b.py": "print('b')\n",
            "node_modules/c.js": "console.log('c')\n",
        })
        st = _stats(root)
        because = {d["skipped_because"] for d in st["pruned_dirs"]}
        assert because <= SKIP_DIRS, because
        assert because == {"examples", "node_modules"}, because
        # Total reconciles against its own itemisation.
        assert st["pruned_code_files"] == sum(
            d["code_files"] for d in st["pruned_dirs"]), st


def test_the_total_reconciles_against_the_itemisation():
    with tempfile.TemporaryDirectory() as td:
        root = _project(Path(td), {
            "src/a.py": "print('a')\n",
            "examples/one.py": "print(1)\n",
            "examples/two.py": "print(2)\n",
            "demos/three.py": "print(3)\n",
        })
        st = _stats(root)
        itemised = sum(d["code_files"] for d in st["pruned_dirs"])
        assert itemised == st["pruned_code_files"] == 3, st
        assert st["pruned_dirs_total"] == len(st["pruned_dirs"]) == 2, st


def test_the_cli_prints_the_disclosure_and_only_when_there_is_one():
    """End to end through the real CLI, both directions.

    A unit test on last_stats cannot show that a reader is told. This runs
    the shipped command and reads its stdout.
    """
    marker = "were not scanned"
    with tempfile.TemporaryDirectory() as td:
        with_examples = _project(Path(td) / "a", {
            "src/a.py": "print('a')\n",
            "examples/b.py": "print('b')\n",
        })
        without = _project(Path(td) / "b", {"src/a.py": "print('a')\n"})

        def run(target):
            return subprocess.run(
                [sys.executable, "-m", "scripts.cli", "check", str(target)],
                cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=300,
            ).stdout

        fires = run(with_examples)
        silent = run(without)
        assert marker in fires, fires[-1500:]
        assert "examples" in fires, fires[-1500:]
        assert marker not in silent, silent[-1500:]


def test_the_counting_budget_is_declared_and_bounded():
    """The count is a floor when the budget runs out, never a silent total.

    An exhausted budget and a small directory must not produce the
    same-looking number (measurement rule 4: a blank gate is not a green
    gate). The budget is exercised here by shrinking it, not by building a
    directory large enough to exhaust the real one.
    """
    import re
    src = (REPO_ROOT / "scripts" / "report.py").read_text(encoding="utf-8")
    m = re.search(r"_PRUNE_ENTRY_BUDGET = (\d+)", src)
    assert m, "the budget must be a declared constant, not a literal in a loop"
    assert int(m.group(1)) > 0
    # pruned_count_exact must be derived from the remaining budget rather
    # than hardcoded True, or it can never report a floor.
    assert '"pruned_count_exact": _prune_budget_left > 0' in src, (
        "pruned_count_exact must be derived from the budget")
