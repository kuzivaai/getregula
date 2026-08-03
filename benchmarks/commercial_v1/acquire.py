#!/usr/bin/env python3
"""Acquire every preregistered public repository at its exact commit."""

import argparse
import hashlib
import json
import subprocess
from pathlib import Path


def run(command, cwd=None):
    return subprocess.run(command, cwd=cwd, capture_output=True, text=True,
                          check=True)


def tree_digest(root):
    digest = hashlib.sha256()
    for path in sorted(p for p in Path(root).rglob("*") if p.is_file()
                       and ".git" not in p.parts):
        digest.update(path.relative_to(root).as_posix().encode() + b"\0")
        digest.update(hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest()


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.output.exists():
        raise SystemExit(f"refusing existing acquisition directory: {args.output}")
    manifest = json.loads(args.manifest.read_text())
    args.output.mkdir(parents=True)
    records = []
    for entry in manifest["layers"]["public_repositories"]:
        target = args.output / entry["id"].replace("/", "__")
        url = f"https://github.com/{entry['id']}.git"
        command = ["git", "clone", "--filter=blob:none", "--no-checkout", url,
                   str(target)]
        clone = run(command)
        fetch_command = ["git", "fetch", "--depth", "1", "origin", entry["commit"]]
        fetch = run(fetch_command, cwd=target)
        checkout = run(["git", "checkout", "--detach", entry["commit"]], cwd=target)
        head = run(["git", "rev-parse", "HEAD"], cwd=target).stdout.strip()
        if head != entry["commit"]:
            raise RuntimeError(f"wrong commit for {entry['id']}: {head}")
        licences = sorted(str(path.relative_to(target)) for pattern in
                          ("LICENSE*", "COPYING*") for path in target.glob(pattern))
        if not licences:
            raise RuntimeError(f"no root licence file found for {entry['id']}")
        records.append({
            "id": entry["id"], "url": url, "commit": head,
            "clone_command": command, "clone_stdout": clone.stdout,
            "clone_stderr": clone.stderr, "fetch_command": fetch_command,
            "fetch_stdout": fetch.stdout, "fetch_stderr": fetch.stderr,
            "checkout_stdout": checkout.stdout, "checkout_stderr": checkout.stderr,
            "licence_files": licences, "source_tree_sha256": tree_digest(target),
        })
    (args.output / "acquisition.json").write_text(json.dumps(records, indent=2) + "\n")
    print(f"acquired and verified {len(records)} public repositories")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
