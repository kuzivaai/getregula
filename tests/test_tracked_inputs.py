"""Tests for the tracked-inputs guard: an artefact that backs a published
number must be derivable from tracked content alone.

Why this exists. `data/gap_demo.json` publishes an overall score of 9 and
Article 11 at 25 on `site/index.html` and both locale pages. No clean
checkout reproduces those figures: the fixture the generator scans,
`tests/fixtures/sample_high_risk`, carries a gitignored `.regula/registry/`
directory locally, and `scripts/compliance_check.py` credits any `.regula/*`
match as one of Article 11's four components. Ledger row N43 records the
control both ways.

The instance (the wrong published figures) needs an owner decision, because
correcting it moves numbers on reader-facing pages. The CLASS does not: a
generator must not be able to build a published artefact from inputs that
are not in the repository. That is what these tests hold closed.

Every test builds its own throwaway git repository. None reads the real
fixture, deliberately: a test pinned to today's contamination would assert
current behaviour rather than correct behaviour, and would start passing for
the wrong reason the moment the owner cleans the fixture.
"""

import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import tree_guard  # noqa: E402


def _make_repo(tmp):
    """A repo with a tracked fixture directory and a .gitignore."""
    root = Path(tmp)
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "t@t"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=root, check=True)
    fixture = root / "fixtures" / "sample"
    fixture.mkdir(parents=True)
    (fixture / "app.py").write_text("print('tracked')\n")
    (root / ".gitignore").write_text(".regula/\nlocal-only.yaml\n")
    subprocess.run(["git", "add", "-A"], cwd=root, check=True)
    subprocess.run(["git", "commit", "-qm", "init"], cwd=root, check=True)
    return root, fixture


def test_clean_fixture_reports_nothing():
    """A directory whose every file is tracked yields an empty list."""
    with tempfile.TemporaryDirectory() as tmp:
        root, fixture = _make_repo(tmp)
        found = tree_guard.untracked_inputs(fixture, root=root)
        assert found == [], f"clean fixture reported {found}"


def test_untracked_file_is_reported():
    """A plain untracked file inside the fixture is named."""
    with tempfile.TemporaryDirectory() as tmp:
        root, fixture = _make_repo(tmp)
        (fixture / "dropped-in.txt").write_text("who put this here\n")
        found = tree_guard.untracked_inputs(fixture, root=root)
        assert any("dropped-in.txt" in p for p in found), \
            f"untracked file not named: {found}"


def test_ignored_file_is_reported():
    """The N43 class proper: a GITIGNORED file is invisible to
    `git status --porcelain` yet still feeds the scanner, so it must be
    reported. This is the arm that a naive implementation misses."""
    with tempfile.TemporaryDirectory() as tmp:
        root, fixture = _make_repo(tmp)
        (fixture / "local-only.yaml").write_text("key: value\n")
        plain = subprocess.run(
            ["git", "status", "--porcelain", str(fixture)],
            cwd=root, capture_output=True, text=True,
        ).stdout
        assert plain.strip() == "", (
            "precondition failed: the planted file should be invisible to a "
            f"plain porcelain call, got {plain!r}"
        )
        found = tree_guard.untracked_inputs(fixture, root=root)
        assert any("local-only.yaml" in p for p in found), \
            f"ignored file not named: {found}"


def test_ignored_directory_contents_are_reported():
    """The exact real-world shape: a gitignored DIRECTORY (.regula/) holding
    a registry file, sitting inside a tracked fixture."""
    with tempfile.TemporaryDirectory() as tmp:
        root, fixture = _make_repo(tmp)
        registry = fixture / ".regula" / "registry"
        registry.mkdir(parents=True)
        (registry / "abc123.json").write_text('{"scanned": true}\n')
        found = tree_guard.untracked_inputs(fixture, root=root)
        assert any(".regula" in p for p in found), \
            f"ignored directory not named: {found}"


def test_restoring_the_directory_clears_the_report():
    """Both ways: remove the contamination and the guard goes quiet."""
    with tempfile.TemporaryDirectory() as tmp:
        root, fixture = _make_repo(tmp)
        stray = fixture / "local-only.yaml"
        stray.write_text("key: value\n")
        assert tree_guard.untracked_inputs(fixture, root=root) != []
        stray.unlink()
        assert tree_guard.untracked_inputs(fixture, root=root) == [], \
            "guard still reports contamination after it was removed"


def test_assert_inputs_tracked_raises_with_the_paths_named():
    """The generator-facing wrapper refuses, and its message names what to
    remove. A refusal that does not say which file is unactionable."""
    with tempfile.TemporaryDirectory() as tmp:
        root, fixture = _make_repo(tmp)
        (fixture / "local-only.yaml").write_text("key: value\n")
        try:
            tree_guard.assert_inputs_tracked(fixture, root=root)
        except tree_guard.UntrackedInputError as exc:
            assert "local-only.yaml" in str(exc), \
                f"refusal does not name the offending path: {exc}"
        else:
            raise AssertionError("assert_inputs_tracked did not refuse")


def test_assert_inputs_tracked_passes_on_a_clean_target():
    """The other half: a clean target must not raise, or the guard would
    block every legitimate regeneration."""
    with tempfile.TemporaryDirectory() as tmp:
        root, fixture = _make_repo(tmp)
        tree_guard.assert_inputs_tracked(fixture, root=root)


def test_modified_tracked_file_is_not_reported():
    """A tracked file that is merely modified must NOT trip the guard.

    Its content is in the repository, so an artefact built from it still
    reproduces from a checkout. The first version of this function returned
    every porcelain line, so an uncommitted edit under a guarded fixture
    blocked regeneration and advised the author to "track it", which they
    already had. Found by adversarial review, 2026-07-31.
    """
    with tempfile.TemporaryDirectory() as tmp:
        root, fixture = _make_repo(tmp)
        (fixture / "app.py").write_text("print('edited but tracked')\n")
        found = tree_guard.untracked_inputs(fixture, root=root)
        assert found == [], f"a modified TRACKED file was reported: {found}"
        tree_guard.assert_inputs_tracked(fixture, root=root)


def test_deleted_and_renamed_tracked_files_are_not_reported():
    """The other two porcelain states that are not untracked content."""
    with tempfile.TemporaryDirectory() as tmp:
        root, fixture = _make_repo(tmp)
        (fixture / "app.py").unlink()
        assert tree_guard.untracked_inputs(fixture, root=root) == [], \
            "a deleted tracked file was reported as untracked input"
        subprocess.run(["git", "checkout", "--", "."], cwd=root, check=True)
        subprocess.run(["git", "mv", "fixtures/sample/app.py",
                        "fixtures/sample/renamed.py"], cwd=root, check=True)
        found = tree_guard.untracked_inputs(fixture, root=root)
        assert found == [], f"a staged rename was reported: {found}"


def test_nonexistent_target_raises_rather_than_passing_silently():
    """A typo'd path constant must not turn the guard into a no-op.

    Measurement rule 4: an absent signal is not a passing signal.
    """
    with tempfile.TemporaryDirectory() as tmp:
        root, _ = _make_repo(tmp)
        try:
            tree_guard.untracked_inputs(root / "fixtures" / "typo", root=root)
        except FileNotFoundError:
            pass
        else:
            raise AssertionError(
                "a nonexistent target returned quietly instead of raising"
            )


def test_awkward_filenames_are_reported_unescaped():
    """Git C-quotes names with spaces or non-ASCII bytes. The refusal must
    name the real path, or its advice is not actionable."""
    with tempfile.TemporaryDirectory() as tmp:
        root, fixture = _make_repo(tmp)
        (fixture / "stray file.txt").write_text("spaces\n")
        (fixture / "café.txt").write_text("non-ascii\n")
        found = tree_guard.untracked_inputs(fixture, root=root)
        joined = " ".join(found)
        assert "stray file.txt" in joined and '\\' not in joined, \
            f"name with a space was escaped or lost: {found}"
        assert "café.txt" in joined, f"non-ASCII name mangled: {found}"


def _clone_with_working_tree_scripts(repo, dest):
    """Clone `repo` to `dest`, then overlay the CURRENT working-tree copies of
    the modules under test.

    `git clone` reproduces committed state, so a clone alone tests whatever is
    in HEAD rather than the change being verified. The first version of the
    test below cloned and nothing else, and consequently passed judgement on
    HEAD's generator; it failed for that reason and is fixed here. The clone
    still supplies the real tracked fixture and a real git structure, which is
    what makes the guard's git queries meaningful.
    """
    subprocess.run(
        ["git", "clone", "--quiet", "--no-hardlinks", str(repo), str(dest)],
        check=True, capture_output=True,
    )
    for rel in ("scripts/tree_guard.py", "scripts/build_gap_demo.py",
                "scripts/build_recall_artefact.py"):
        (dest / rel).write_bytes((repo / rel).read_bytes())
    return dest


def test_generator_refuses_and_does_not_write_when_inputs_are_untracked():
    """The claim this whole change rests on: a contaminated fixture means NO
    artefact is written. Behaviour, not a substring search.

    The first version of this test asserted only that the string
    "assert_inputs_tracked" appeared in the generator source. An adversarial
    review moved the guard to AFTER the write and every test still passed
    while the artefact was rewritten. That test proved nothing; this one
    executes the real entry point and checks the file on disk.
    """
    repo = Path(__file__).resolve().parent.parent
    with tempfile.TemporaryDirectory() as tmp:
        work = _clone_with_working_tree_scripts(repo, Path(tmp) / "repo")
        fixture = work / "tests" / "fixtures" / "sample_high_risk"
        artefact = work / "data" / "gap_demo.json"
        before = artefact.read_bytes()

        # A clean clone has no contamination, so plant the exact shape the
        # real defect had: a gitignored directory inside the tracked fixture.
        registry = fixture / ".regula" / "registry"
        registry.mkdir(parents=True)
        (registry / "planted.json").write_text('{"planted": true}\n')

        proc = subprocess.run(
            [sys.executable, "scripts/build_gap_demo.py"],
            cwd=work, capture_output=True, text=True,
        )
        assert proc.returncode != 0, (
            "generator wrote an artefact from contaminated inputs "
            f"(rc={proc.returncode})"
        )
        assert "REFUSED" in proc.stderr, f"no refusal message: {proc.stderr}"
        assert artefact.read_bytes() == before, \
            "the artefact was rewritten despite the refusal"


def test_generator_writes_normally_when_inputs_are_clean():
    """The other half. Without this, a guard that refused unconditionally
    would pass the test above and break every legitimate regeneration."""
    repo = Path(__file__).resolve().parent.parent
    with tempfile.TemporaryDirectory() as tmp:
        work = _clone_with_working_tree_scripts(repo, Path(tmp) / "repo")
        proc = subprocess.run(
            [sys.executable, "scripts/build_gap_demo.py"],
            cwd=work, capture_output=True, text=True,
        )
        assert proc.returncode == 0, (
            f"clean clone refused a legitimate build: {proc.stderr}"
        )
        assert "REFUSED" not in proc.stderr


if __name__ == "__main__":
    tests = [
        test_clean_fixture_reports_nothing,
        test_untracked_file_is_reported,
        test_ignored_file_is_reported,
        test_ignored_directory_contents_are_reported,
        test_restoring_the_directory_clears_the_report,
        test_assert_inputs_tracked_raises_with_the_paths_named,
        test_assert_inputs_tracked_passes_on_a_clean_target,
        test_modified_tracked_file_is_not_reported,
        test_deleted_and_renamed_tracked_files_are_not_reported,
        test_nonexistent_target_raises_rather_than_passing_silently,
        test_awkward_filenames_are_reported_unescaped,
        test_generator_refuses_and_does_not_write_when_inputs_are_untracked,
        test_generator_writes_normally_when_inputs_are_clean,
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
