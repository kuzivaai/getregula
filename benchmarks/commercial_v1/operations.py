#!/usr/bin/env python3
"""Run frozen tools over the pinned repository corpus for operations evidence."""

import argparse
import hashlib
import json
import os
import resource
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


COMMANDS = {
    "local_head": lambda executable, repo: [
        executable, "-m", "scripts.cli", "check", str(repo), "--format", "json",
        "--deterministic"],
    "regula_public": lambda executable, repo: [
        executable, "check", str(repo), "--format", "json", "--deterministic"],
    "compliance_agent_default": lambda executable, repo: [
        executable, "scan", str(repo), "--format", "json"],
    "compliance_agent_configured": lambda executable, repo: [
        executable, "scan", str(repo), "--format", "json", "--no-update-check"],
    "air_blackbox": lambda executable, repo: [
        executable, "comply", "--scan", str(repo)],
}


def _digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--acquisitions", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--tool", choices=tuple(COMMANDS), required=True)
    parser.add_argument("--executable", required=True)
    parser.add_argument("--timeout", type=int, default=900)
    args = parser.parse_args(argv)
    if args.output.exists():
        raise SystemExit(f"refusing existing operations directory: {args.output}")
    args.output.mkdir(parents=True)
    manifest = json.loads(args.manifest.read_text())
    acquired = {row["id"]: row for row in json.loads(
        (args.acquisitions / "acquisition.json").read_text())}
    records = []
    for entry in manifest["layers"]["public_repositories"]:
        if entry["id"] not in acquired:
            raise SystemExit(f"missing acquired repository: {entry['id']}")
        repo = args.acquisitions / entry["id"].replace("/", "__")
        command = COMMANDS[args.tool](args.executable, repo)
        start = time.monotonic_ns()
        started = datetime.now(timezone.utc).isoformat()
        timed_out = False
        try:
            completed = subprocess.run(command, capture_output=True, text=True,
                                       timeout=args.timeout,
                                       env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
            stdout, stderr, exit_code = (
                completed.stdout, completed.stderr, completed.returncode)
        except subprocess.TimeoutExpired as exc:
            stdout, stderr, exit_code, timed_out = (
                exc.stdout or "", exc.stderr or "", 124, True)
        out = args.output / f"{entry['id'].replace('/', '__')}.stdout"
        err = args.output / f"{entry['id'].replace('/', '__')}.stderr"
        out.write_text(stdout)
        err.write_text(stderr)
        records.append({
            "repository": entry["id"], "commit": entry["commit"],
            "tool": args.tool, "command": command, "started_at": started,
            "finished_at": datetime.now(timezone.utc).isoformat(),
            "duration_seconds": (time.monotonic_ns() - start) / 1e9,
            "peak_child_memory_kb_cumulative": resource.getrusage(
                resource.RUSAGE_CHILDREN).ru_maxrss,
            "memory_limit": "cumulative child high-water mark; not per-invocation peak",
            "exit_code": exit_code, "timed_out": timed_out,
            "stdout_sha256": _digest(out), "stderr_sha256": _digest(err),
            "raw_stdout": str(out), "raw_stderr": str(err),
        })
    (args.output / "operations.json").write_text(json.dumps(records, indent=2) + "\n")
    print(f"{args.tool}: retained {len(records)} repository outcomes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
