#!/usr/bin/env python3
"""Protocol-deviation runner for case-insensitive repository licences.

The frozen `benchmarks/commercial_v1/acquire.py` failed on the lowercase root
`license` in the pinned `sindresorhus/ky` repository. Its exit-1 control is
retained. This runner changes only licence-file discovery and otherwise uses
the same acquisition algorithm. It lives outside the frozen protocol input
set so the original hashes continue to verify.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "benchmarks" / "commercial_v1"))

from acquire import run, tree_digest  # noqa: E402


def discover_licence_files(root):
    accepted = ("license", "licence", "copying", "notice")
    return sorted(path.name for path in Path(root).iterdir() if path.is_file()
                  and path.name.lower().startswith(accepted))


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
        licences = discover_licence_files(target)
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
