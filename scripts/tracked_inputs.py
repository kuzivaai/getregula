#!/usr/bin/env python3
"""Reject untracked or ignored inputs to reproducible artefact builds.

Generated evidence must be derivable from a clean clone.  This module asks
Git for untracked and ignored paths below a build input and fails loudly when
any are present.  Modified, renamed, or deleted tracked files are deliberately
not treated as untracked inputs.
"""

from __future__ import annotations

import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


class UntrackedInputError(RuntimeError):
    """A build input contains content that is absent from the repository."""


def _git_status(target: Path, root: Path) -> str:
    result = subprocess.run(
        [
            "git",
            "status",
            "--porcelain",
            "-z",
            "--ignored=matching",
            "--",
            str(target),
        ],
        cwd=str(root),
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


def untracked_inputs(path: str | Path, root: str | Path | None = None) -> list[str]:
    """Return sorted repository-relative untracked or ignored input paths."""
    repo = Path(root or REPO_ROOT).resolve()
    target = Path(path)
    if not target.is_absolute():
        target = repo / target
    if not target.exists():
        raise FileNotFoundError(
            f"cannot check inputs under {target}: the path does not exist"
        )

    found: list[str] = []
    for record in _git_status(target, repo).split("\0"):
        if len(record) < 4:
            continue
        code, name = record[:2], record[3:]
        if code in {"??", "!!"}:
            found.append(name)
    return sorted(found)


def assert_inputs_tracked(
    path: str | Path, root: str | Path | None = None
) -> None:
    """Raise when a build target contains untracked or ignored content."""
    found = untracked_inputs(path, root=root)
    if not found:
        return
    listed = "\n  ".join(found)
    raise UntrackedInputError(
        f"{path} holds content that is not in the repository, so an artefact "
        f"built from it would not reproduce in a clean clone:\n  {listed}\n"
        "Remove it, or track it, before regenerating."
    )
