#!/usr/bin/env python3
"""Fail-closed integrity checks for the commercial_v1 benchmark."""

import hashlib
import json
import subprocess
from pathlib import Path


class IntegrityError(RuntimeError):
    """The frozen evaluation evidence is incomplete or inconsistent."""


def _git(root, *args):
    try:
        result = subprocess.run(
            ["git", *args], cwd=root, capture_output=True, check=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise IntegrityError(f"git invocation failed: {exc}") from exc
    return result.stdout


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_hash_bound_json(path, expected_sha256):
    path = Path(path)
    actual = sha256_file(path)
    if actual != expected_sha256:
        raise IntegrityError(
            f"hash mismatch for {path}: expected {expected_sha256}, got {actual}")
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise IntegrityError(f"malformed JSON in {path}: {exc}") from exc


def assert_clean_inputs(root, paths):
    """Require a real Git repo and reject untracked or ignored inputs."""
    root = Path(root)
    inside = _git(root, "rev-parse", "--is-inside-work-tree").decode().strip()
    if inside != "true":
        raise IntegrityError(f"git did not identify {root} as a work tree")
    bad = []
    for rel in paths:
        path = root / rel
        if not path.is_file():
            raise IntegrityError(f"listed input is missing: {rel}")
        tracked = subprocess.run(
            ["git", "ls-files", "--error-unmatch", "--", rel], cwd=root,
            capture_output=True,
        )
        ignored = subprocess.run(
            ["git", "check-ignore", "-q", "--", rel], cwd=root,
        )
        if tracked.returncode != 0 or ignored.returncode == 0:
            bad.append(rel)
    if bad:
        raise IntegrityError("untracked or ignored inputs: " + ", ".join(bad))


def verify_enumeration(root, entries, discovered):
    """Require exact manifest/discovery agreement and matching file hashes."""
    root = Path(root)
    listed = [entry["path"] for entry in entries]
    if len(listed) != len(set(listed)):
        raise IntegrityError("manifest contains duplicate input paths")
    if set(listed) != set(discovered):
        missing = sorted(set(listed) - set(discovered))
        extra = sorted(set(discovered) - set(listed))
        raise IntegrityError(f"enumeration mismatch: missing={missing}, extra={extra}")
    for entry in entries:
        path = root / entry["path"]
        if not path.is_file():
            raise IntegrityError(f"manifest input missing: {entry['path']}")
        actual = sha256_file(path)
        if actual != entry["sha256"]:
            raise IntegrityError(
                f"input hash mismatch for {entry['path']}: "
                f"expected {entry['sha256']}, got {actual}")


def verify_results(expected_ids, records, require_success=True):
    """Validate complete authentic records and retain adverse executions."""
    ids = [record.get("decision_id") for record in records]
    if len(ids) != len(set(ids)):
        raise IntegrityError("duplicate decisions in result set")
    if set(ids) != set(expected_ids):
        raise IntegrityError(
            f"result enumeration mismatch: expected={sorted(expected_ids)}, "
            f"actual={sorted(item for item in ids if item is not None)}")
    failures = []
    for record in records:
        if record.get("timed_out") or record.get("exit_code") != 0:
            failures.append(record["decision_id"])
        elif record.get("parse_error") or record.get("predicted") is None:
            failures.append(record["decision_id"])
    if require_success and failures:
        raise IntegrityError("unsuccessful result records: " + ", ".join(failures))
    return failures


def discover_repository_inputs(repo):
    """Independently discover all tracked commercial_v1 benchmark inputs."""
    prefix = "benchmarks/commercial_v1/"
    output = _git(repo, "ls-files", "-z", "--", prefix).decode()
    return sorted(path for path in output.split("\0") if path and
                  not path.endswith(("manifest.json", "freeze.json")))


def verify_freeze(root, freeze_path, product_root):
    freeze = json.loads(Path(freeze_path).read_text())
    base = Path(freeze_path).parent
    for name, expected in freeze["hashes"].items():
        path = base / name
        if not path.is_file() or sha256_file(path) != expected:
            raise IntegrityError(f"frozen input mismatch: {name}")
    head = _git(product_root, "rev-parse", "HEAD").decode().strip()
    if head != freeze["regula_commit"]:
        raise IntegrityError(
            f"product freeze mismatch: expected {freeze['regula_commit']}, got {head}")


def main(argv=None):
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--product-repo", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--freeze", type=Path, required=True)
    args = parser.parse_args(argv)
    manifest = json.loads(args.manifest.read_text())
    verify_freeze(args.repo, args.freeze, args.product_repo)
    paths = [entry["path"] for entry in manifest["repository_inputs"]]
    product_head = _git(args.product_repo, "rev-parse", "HEAD").decode().strip()
    if product_head != manifest["regula_commit"]:
        raise IntegrityError(
            f"wrong product commit: manifest={manifest['regula_commit']}, "
            f"HEAD={product_head}")
    assert_clean_inputs(args.repo, paths)
    discovered = discover_repository_inputs(args.repo)
    verify_enumeration(args.repo, manifest["repository_inputs"], discovered)
    print(f"commercial_v1 integrity: {len(paths)} repository inputs verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
