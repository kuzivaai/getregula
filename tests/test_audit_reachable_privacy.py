"""Tests for privacy auditing across already-fetched Git refs."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import audit_reachable_privacy as reachable


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _commit(repo: Path, message: str) -> None:
    _git(repo, "add", ".")
    _git(
        repo,
        "-c",
        "user.name=Example Maintainer",
        "-c",
        "user.email=maintainer@example.com",
        "commit",
        "-m",
        message,
    )


def _repository(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-b", "main")
    (repo / "README.md").write_text("public product\n", encoding="utf-8")
    _commit(repo, "initial")
    _git(repo, "branch", "origin/main")
    return repo


def test_audit_finds_private_content_reachable_only_from_review_ref(tmp_path: Path):
    repo = _repository(tmp_path)
    _git(repo, "switch", "-c", "review")
    path = repo / "docs" / "improvement" / "STATE.md"
    path.parent.mkdir(parents=True)
    path.write_text("internal record\n", encoding="utf-8")
    _commit(repo, "add internal record")
    _git(repo, "branch", "origin/pull/1")
    _git(repo, "switch", "main")

    result = reachable.audit(
        repo,
        "origin/main",
        ("refs/heads/origin/pull/",),
    )

    assert result.commits_outside_base == 1
    assert result.affected_refs == ("refs/heads/origin/pull/1",)
    assert reachable.ReachableFinding(
        "docs/improvement/STATE.md",
        "private-path",
        1,
    ) in result.findings


def test_audit_reports_clean_review_ref_without_vacuous_pass(tmp_path: Path):
    repo = _repository(tmp_path)
    _git(repo, "switch", "-c", "review")
    (repo / "feature.py").write_text("value = 1\n", encoding="utf-8")
    _commit(repo, "add feature")
    _git(repo, "branch", "origin/pull/2")

    result = reachable.audit(
        repo,
        "origin/main",
        ("refs/heads/origin/pull/",),
    )

    assert result.commits_outside_base == 1
    assert result.unique_path_blobs == 2
    assert result.findings == ()
    assert result.affected_refs == ()


def test_audit_fails_when_requested_ref_prefix_is_empty(tmp_path: Path):
    repo = _repository(tmp_path)
    try:
        reachable.audit(repo, "origin/main", ("refs/heads/missing/",))
    except reachable.AuditError as error:
        assert "no refs matched" in str(error)
    else:
        raise AssertionError("empty ref discovery must fail closed")
