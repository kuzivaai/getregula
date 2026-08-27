#!/usr/bin/env python3
"""Audit already-fetched Git refs for material excluded from the public tree.

The normal public-repository guard checks the current tracked tree. Historical
pull-request refs are a separate publication surface: GitHub can retain them
after the default branch is replaced, and ordinary pushes cannot update them.

This command is deliberately read-only and does not fetch. Run it in an
isolated clone after explicitly fetching the refs to be audited. It reports
paths and rule names, never matched values.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from public_repo_guard import is_text_path, scan_text

ROOT = Path(__file__).resolve().parents[1]


class AuditError(RuntimeError):
    """The reachable-ref audit could not establish a complete result."""


@dataclass(frozen=True)
class ReachableFinding:
    path: str
    rule: str
    blob_count: int


@dataclass(frozen=True)
class AuditResult:
    base_ref: str
    refs: tuple[str, ...]
    commits_outside_base: int
    unique_path_blobs: int
    findings: tuple[ReachableFinding, ...]
    affected_refs: tuple[str, ...]


def _run_git(
    repo: Path,
    *args: str,
    input_bytes: bytes | None = None,
) -> bytes:
    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=repo,
            input=input_bytes,
            capture_output=True,
            check=False,
        )
    except OSError as error:
        raise AuditError(f"cannot run git for {args[0] if args else 'audit'}") from error
    if proc.returncode:
        raise AuditError(
            f"git {args[0] if args else 'audit'} failed with exit {proc.returncode}"
        )
    return proc.stdout


def _lines(data: bytes) -> list[str]:
    return [
        line.decode("utf-8", "replace")
        for line in data.splitlines()
        if line
    ]


def list_refs(repo: Path, prefixes: tuple[str, ...]) -> tuple[str, ...]:
    refs: set[str] = set()
    for prefix in prefixes:
        refs.update(_lines(_run_git(
            repo,
            "for-each-ref",
            "--format=%(refname)",
            prefix,
        )))
    return tuple(sorted(refs))


def _cat_blobs(repo: Path, object_ids: list[str]) -> dict[str, bytes]:
    """Read blobs through one bounded cat-file process instead of one per blob."""
    if not object_ids:
        return {}
    try:
        proc = subprocess.Popen(
            ["git", "cat-file", "--batch"],
            cwd=repo,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except OSError as error:
        raise AuditError("cannot start git cat-file") from error
    assert proc.stdin is not None
    assert proc.stdout is not None
    result: dict[str, bytes] = {}
    try:
        for oid in object_ids:
            proc.stdin.write(oid.encode("ascii") + b"\n")
            proc.stdin.flush()
            header = proc.stdout.readline().decode("ascii", "replace").strip()
            parts = header.split()
            if len(parts) != 3 or parts[1] != "blob":
                raise AuditError("git cat-file returned a non-blob or incomplete object")
            size = int(parts[2])
            data = proc.stdout.read(size)
            separator = proc.stdout.read(1)
            if len(data) != size or separator != b"\n":
                raise AuditError("git cat-file returned truncated blob data")
            result[oid] = data
    finally:
        proc.stdin.close()
        returncode = proc.wait()
    if returncode:
        raise AuditError(f"git cat-file failed with exit {returncode}")
    return result


def audit(
    repo: Path,
    base_ref: str,
    ref_prefixes: tuple[str, ...],
) -> AuditResult:
    repo = repo.resolve()
    refs = list_refs(repo, ref_prefixes)
    if not refs:
        raise AuditError("no refs matched the requested prefixes")

    commits = set(_lines(_run_git(
        repo,
        "rev-list",
        *refs,
        "--not",
        base_ref,
    )))

    occurrence_commits: dict[tuple[str, str], set[str]] = defaultdict(set)
    text_blobs: set[str] = set()
    for commit in sorted(commits):
        tree = _run_git(repo, "ls-tree", "-r", "-z", commit)
        for entry in tree.split(b"\0"):
            if not entry:
                continue
            try:
                metadata, raw_path = entry.split(b"\t", 1)
                _mode, kind, raw_oid = metadata.split(b" ", 2)
            except ValueError as error:
                raise AuditError("git ls-tree returned an invalid entry") from error
            if kind != b"blob":
                continue
            path = raw_path.decode("utf-8", "surrogateescape")
            oid = raw_oid.decode("ascii")
            occurrence_commits[(path, oid)].add(commit)
            if is_text_path(path):
                text_blobs.add(oid)

    blob_data = _cat_blobs(repo, sorted(text_blobs))
    finding_blobs: dict[tuple[str, str], set[str]] = defaultdict(set)
    finding_commits: set[str] = set()
    for (path, oid), containing_commits in occurrence_commits.items():
        findings = scan_text(path, "")
        if is_text_path(path):
            try:
                text = blob_data[oid].decode("utf-8")
            except UnicodeDecodeError:
                text = ""
            findings.extend(scan_text(path, text))
        for finding in findings:
            finding_blobs[(finding.path, finding.rule)].add(oid)
            finding_commits.update(containing_commits)

    affected_refs: list[str] = []
    for ref in refs:
        ref_commits = set(_lines(_run_git(
            repo,
            "rev-list",
            ref,
            "--not",
            base_ref,
        )))
        if ref_commits & finding_commits:
            affected_refs.append(ref)

    findings = tuple(
        ReachableFinding(path, rule, len(blobs))
        for (path, rule), blobs in sorted(finding_blobs.items())
    )
    return AuditResult(
        base_ref=base_ref,
        refs=refs,
        commits_outside_base=len(commits),
        unique_path_blobs=len(occurrence_commits),
        findings=findings,
        affected_refs=tuple(affected_refs),
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", type=Path, default=ROOT)
    parser.add_argument("--base-ref", default="origin/main")
    parser.add_argument(
        "--ref-prefix",
        action="append",
        default=[],
        help="already-fetched ref prefix; repeat for more than one prefix",
    )
    parser.add_argument(
        "--list-paths",
        action="store_true",
        help="list finding paths and rules without printing matched values",
    )
    args = parser.parse_args(argv)
    prefixes = tuple(args.ref_prefix or ["refs/remotes/origin/pull/"])
    try:
        result = audit(args.repo, args.base_ref, prefixes)
    except (AuditError, OSError, ValueError) as error:
        print(f"reachable-privacy: cannot complete audit: {error}", file=sys.stderr)
        return 2

    counts: dict[str, int] = defaultdict(int)
    for finding in result.findings:
        counts[finding.rule] += 1
    print(f"reachable-privacy: base_ref={result.base_ref}")
    print(f"  refs={len(result.refs)}")
    print(f"  commits_outside_base={result.commits_outside_base}")
    print(f"  unique_path_blobs={result.unique_path_blobs}")
    print(f"  finding_keys={len(result.findings)}")
    print(f"  affected_refs={len(result.affected_refs)}")
    for rule, count in sorted(counts.items()):
        print(f"  rule {rule}: {count}")
    if args.list_paths:
        for finding in result.findings:
            print(
                f"  finding {finding.rule}: {finding.path} "
                f"({finding.blob_count} blob(s))"
            )
    for ref in result.affected_refs:
        print(f"  affected {ref}")
    return 1 if result.findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
