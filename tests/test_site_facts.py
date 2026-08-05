"""Tests for scripts/site_facts.py — the canonical-counts generator whose
artifacts (data/site_facts.{json,md}) CI diffs against the committed copies.

Covers the two defects found on 2026-07-16:
- count_tests() silently published total_collected=0 when pytest collection
  was unavailable (the CI claim-audit job had no pytest installed), turning
  an unmeasured value into a "canonical fact". It must raise instead.
- main() stamped generated_at=now() on every run, so CI's
  regenerate-then-`git diff --exit-code` gate could never pass. It must
  preserve the previous timestamp when the computed facts are unchanged.
"""
from __future__ import annotations

import json
import subprocess
import sys
import types
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import pytest  # noqa: E402

import site_facts  # noqa: E402


# ---------------------------------------------------------------------------
# count_tests: unmeasurable collection must raise, never publish 0
# ---------------------------------------------------------------------------

def _fake_run(returncode: int, stdout: str = "", stderr: str = ""):
    def fake(*args, **kwargs):
        return types.SimpleNamespace(
            returncode=returncode, stdout=stdout, stderr=stderr
        )
    return fake


def test_count_tests_raises_when_pytest_missing(monkeypatch):
    """rc!=0 (e.g. 'No module named pytest') must raise, not return 0."""
    monkeypatch.setattr(
        subprocess, "run",
        _fake_run(1, stderr="/usr/bin/python3: No module named pytest"),
    )
    with pytest.raises(RuntimeError, match="refusing to publish"):
        site_facts.count_tests()


def test_count_tests_raises_when_summary_line_absent(monkeypatch):
    """rc==0 but no 'N tests collected' line is equally unmeasurable."""
    monkeypatch.setattr(
        subprocess, "run", _fake_run(0, stdout="garbage output")
    )
    with pytest.raises(RuntimeError, match="refusing to publish"):
        site_facts.count_tests()


def test_count_tests_parses_collected_total(monkeypatch):
    monkeypatch.setattr(
        subprocess, "run",
        _fake_run(0, stdout="2678 tests collected in 0.42s\n"),
    )
    result = site_facts.count_tests()
    assert result["total_collected"] == 2678


# ---------------------------------------------------------------------------
# main: generated_at is "when the facts last changed", not "last run"
# ---------------------------------------------------------------------------

def _wire_main(monkeypatch, tmp_path: Path, compute_results: list[dict]):
    """Point the artifact paths at tmp_path and feed main() canned facts."""
    seq = iter(compute_results)
    monkeypatch.setattr(site_facts, "compute", lambda: next(seq))
    monkeypatch.setattr(site_facts, "OUT_JSON", tmp_path / "site_facts.json")
    monkeypatch.setattr(site_facts, "OUT_MD", tmp_path / "site_facts.md")
    monkeypatch.setattr(site_facts, "render_markdown", lambda d: "md\n")
    # main() prints a summary keyed off counts; keep the shape it needs.


def _facts(ts: str, collected: int) -> dict:
    return {
        "generated_at": ts,
        "counts": {
            "commands": 61,
            "patterns": {
                "historical_330_bucket": 479,
                "grand_total": 722,
                "tier_groups": 57,
            },
            "frameworks": 12,
            "languages": 8,
            "tests": {"total_collected": collected, "total_functions": 1},
        },
    }


def test_main_preserves_timestamp_when_facts_unchanged(monkeypatch, tmp_path):
    _wire_main(
        monkeypatch, tmp_path,
        [_facts("T1", 100), _facts("T2", 100)],
    )
    assert site_facts.main() == 0
    assert site_facts.main() == 0
    written = json.loads((tmp_path / "site_facts.json").read_text())
    assert written["generated_at"] == "T1"


def test_main_updates_timestamp_when_facts_change(monkeypatch, tmp_path):
    _wire_main(
        monkeypatch, tmp_path,
        [_facts("T1", 100), _facts("T2", 200)],
    )
    assert site_facts.main() == 0
    assert site_facts.main() == 0
    written = json.loads((tmp_path / "site_facts.json").read_text())
    assert written["generated_at"] == "T2"
    assert written["counts"]["tests"]["total_collected"] == 200


def test_main_fails_closed_when_compute_raises(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(
        site_facts, "compute",
        lambda: (_ for _ in ()).throw(RuntimeError("collection failed")),
    )
    monkeypatch.setattr(site_facts, "OUT_JSON", tmp_path / "site_facts.json")
    monkeypatch.setattr(site_facts, "OUT_MD", tmp_path / "site_facts.md")
    assert site_facts.main() == 1
    assert not (tmp_path / "site_facts.json").exists()
    assert not (tmp_path / "site_facts.md").exists()
    assert "ERROR" in capsys.readouterr().err


# --- Count provenance: every contributor to a published count must be tracked
#
# N52. count_tests() enumerates by working-tree glob (`tests_dir.glob`) and by
# `pytest --collect-only` over the working tree, unlike claim_auditor,
# f25_exposure, merge_blockers and check_decompositions, which all select
# their corpus with `git ls-files`. So an UNTRACKED test file is counted into
# total_collected and per_file, and those figures cascade to nine published
# surfaces including the README badge.
#
# This is the same class as N43 (untracked content reaching a published
# number) on the generator that publishes the most numbers. It has already
# fired once: on 2026-07-31 a new, still-untracked test file was counted into
# the canonical artefact, and the published figures were only correct because
# the file happened to be committed in the same commit.
#
# The invariant these tests hold: every key in counts.tests.per_file names a
# file that git tracks. If it does not, the published count is not derivable
# from a clean checkout.


def test_untracked_contributors_flags_a_file_git_does_not_track():
    """The predicate must name a contributor that is not tracked.

    Constructed rather than pinned to today's tree: passing the real per_file
    would assert current state, and would stop testing anything the moment the
    tree changed. Keys are repo-relative paths (N55: basenames could not be
    compared soundly against tracked paths).
    """
    per_file = {"tests/test_real_tracked_example.py": 3,
                "tests/test_never_committed.py": 7}
    tracked = {"tests/test_real_tracked_example.py"}
    found = site_facts.untracked_test_contributors(per_file, tracked=tracked)
    assert found == ["tests/test_never_committed.py"], (
        f"unexpected result: {found}")


def test_untracked_contributors_is_quiet_when_every_contributor_is_tracked():
    """The other half. Without this, a predicate that flagged everything
    would pass the test above and break every legitimate run."""
    per_file = {"tests/test_a.py": 1, "tests/sub/test_b.py": 2}
    found = site_facts.untracked_test_contributors(
        per_file, tracked={"tests/test_a.py", "tests/sub/test_b.py"})
    assert found == [], f"clean input reported {found}"


def test_untracked_contributors_defaults_to_asking_git():
    """With no explicit tracked set, the predicate must consult git rather
    than assume. Read against the real repository, where the committed
    artefact's contributors are all tracked."""
    facts = json.loads(
        (REPO_ROOT / "data" / "site_facts.json").read_text(encoding="utf-8"))
    per_file = facts["counts"]["tests"]["per_file"]
    assert per_file, "artefact has no per_file entries; nothing to check"
    found = site_facts.untracked_test_contributors(per_file)
    assert found == [], (
        "the committed canonical count was generated from test files that "
        f"git does not track, so it does not reproduce in a clean "
        f"checkout: {found}. Commit them, or regenerate after removing them.")


def test_generation_warns_when_a_contributor_is_untracked(monkeypatch, capsys):
    """count_tests must say so at the moment it counts, not leave the reader
    to discover it later from a cascade that already shipped."""
    monkeypatch.setattr(
        site_facts, "untracked_test_contributors",
        lambda per_file, tracked=None: ["tests/test_never_committed.py"])
    monkeypatch.setattr(
        site_facts, "missing_tracked_contributors",
        lambda per_file, tracked=None: [], raising=False)
    monkeypatch.setattr(
        subprocess, "run",
        lambda *a, **k: types.SimpleNamespace(
            returncode=0, stdout="42 tests collected in 0.1s", stderr=""))
    site_facts.count_tests()
    err = capsys.readouterr().err
    assert "test_never_committed.py" in err, f"warning omits the file: {err!r}"
    assert "not tracked" in err.lower(), f"warning does not say why: {err!r}"


# --- N55: the guard must fail closed, see recursively, and look both ways.
#
# Three holes, all measured on 2026-07-31 (ledger N55) and reproduced on
# 2026-08-05 before the correction:
# (a) a git failure inside untracked_test_contributors returned [], the PASS
#     value, so the at-rest enforcement could not distinguish "everything is
#     tracked" from "git never ran" (measurement rule 4);
# (b) per_file came from a top-level glob while total_collected came from
#     recursive pytest collection, so a nested test file inflated the
#     published count with no per_file key for the predicate to see;
# (c) the predicate only looked from per_file towards git, so a tracked test
#     file deleted without `git rm` lowered the count silently.


def test_git_discovery_failure_raises_not_clean(monkeypatch):
    """IMP-01 (N55a): a git failure must raise, never return the PASS value."""
    def boom(*a, **k):
        raise OSError("git binary missing")
    monkeypatch.setattr(subprocess, "run", boom)
    with pytest.raises(site_facts.GitDiscoveryError, match="git ls-files"):
        site_facts.untracked_test_contributors({"tests/test_x.py": 1})


def test_git_nonzero_exit_raises_not_clean(monkeypatch):
    """IMP-01 (N55a): rc!=0 is a failure, not an empty clean answer."""
    monkeypatch.setattr(
        subprocess, "run",
        _fake_run(128, stdout="", stderr="fatal: not a git repository"))
    with pytest.raises(site_facts.GitDiscoveryError,
                       match="not a git repository"):
        site_facts.untracked_test_contributors({"tests/test_x.py": 1})


def test_git_success_with_everything_tracked_is_distinguishably_clean(
        monkeypatch):
    """IMP-01 negative control: a genuine all-tracked answer is [], so the
    fail-closed change cannot be satisfied by refusing everything."""
    monkeypatch.setattr(
        subprocess, "run",
        _fake_run(0, stdout="tests/test_a.py\0tests/sub/test_b.py\0"))
    found = site_facts.untracked_test_contributors(
        {"tests/test_a.py": 1, "tests/sub/test_b.py": 2})
    assert found == [], f"clean tracked population reported {found}"


def test_nested_contributors_are_inventoried_with_the_collector(
        monkeypatch, tmp_path):
    """IMP-02 (N55b): the per-file inventory must agree with the REAL
    recursive collector, exercised end to end on a scratch tree."""
    tests = tmp_path / "tests"
    (tests / "sub").mkdir(parents=True)
    (tests / "test_top.py").write_text(
        "def test_a():\n    assert True\n", encoding="utf-8")
    (tests / "sub" / "test_nested.py").write_text(
        "def test_b():\n    assert True\n\n\ndef test_c():\n    assert True\n",
        encoding="utf-8")
    monkeypatch.setattr(site_facts, "REPO", tmp_path)
    result = site_facts.count_tests()
    assert result["total_collected"] == 3, result
    assert set(result["per_file"]) == {
        "tests/test_top.py", "tests/sub/test_nested.py"}, (
        "the contributor inventory does not match the population the "
        f"collector counted: {sorted(result['per_file'])}")
    assert result["total_functions"] == 3, result


def test_deleted_tracked_contributor_is_reported():
    """IMP-03 (N55c): a tracked test file absent from the inventory is an
    under-count and must be named."""
    found = site_facts.missing_tracked_contributors(
        {"tests/test_alive.py": 4},
        tracked={"tests/test_alive.py",
                 "tests/test_deleted_without_git_rm.py"})
    assert found == ["tests/test_deleted_without_git_rm.py"], (
        f"unexpected result: {found}")


def test_reverse_direction_is_quiet_when_populations_agree():
    found = site_facts.missing_tracked_contributors(
        {"tests/test_a.py": 1}, tracked={"tests/test_a.py"})
    assert found == [], f"agreeing populations reported {found}"


def test_reverse_direction_demands_only_collector_pattern_files():
    """conftest.py, helpers and fixture sources are tracked but are not test
    files under python_files = test_*.py; the reverse check must not demand
    them as contributors."""
    found = site_facts.missing_tracked_contributors(
        {"tests/test_a.py": 1},
        tracked={"tests/test_a.py", "tests/conftest.py", "tests/helpers.py",
                 "tests/fixtures/sample_high_risk/app.py"})
    assert found == [], f"non-test tracked files demanded: {found}"


def test_committed_artefact_covers_every_tracked_test_file():
    """The reverse at-rest enforcement (IMP-03), against the real repository:
    every tracked test file must appear in the committed artefact, or the
    published count under-reports a deletion nobody recorded."""
    facts = json.loads(
        (REPO_ROOT / "data" / "site_facts.json").read_text(encoding="utf-8"))
    per_file = facts["counts"]["tests"]["per_file"]
    assert per_file, "artefact has no per_file entries; nothing to check"
    found = site_facts.missing_tracked_contributors(per_file)
    assert found == [], (
        "tracked test files are missing from the committed canonical count, "
        f"so it under-reports the suite a checkout would run: {found}. "
        "Either `git rm` the deletion deliberately and regenerate, or "
        "restore the files.")


def test_committed_artefact_keys_are_repo_relative_paths():
    """A basename key cannot be compared soundly against tracked paths (a
    tracked nested file would mask an untracked top-level one of the same
    name), so a stale basename-keyed artefact must fail loudly here rather
    than pass the two at-rest checks above vacuously."""
    facts = json.loads(
        (REPO_ROOT / "data" / "site_facts.json").read_text(encoding="utf-8"))
    per_file = facts["counts"]["tests"]["per_file"]
    offenders = [k for k in per_file
                 if not k.startswith("tests/") or "\\" in k]
    assert offenders == [], (
        f"artefact keys are not repo-relative posix paths: {offenders[:5]}")
