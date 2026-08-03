#!/usr/bin/env python3
"""Run a Python CLI with socket creation denied and retain the outcome."""

import argparse
import json
import os
import subprocess
from pathlib import Path


SITE_CUSTOMIZE = """\
import socket
class NetworkDenied(RuntimeError): pass
def denied(*args, **kwargs):
    raise NetworkDenied('commercial_v1 socket-denial control')
socket.socket = denied
socket.create_connection = denied
"""


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    if args.output.exists() or not args.command:
        raise SystemExit("fresh --output and a command are required")
    args.output.mkdir(parents=True)
    hook = args.output / "sitecustomize.py"
    hook.write_text(SITE_CUSTOMIZE)
    env = {**os.environ, "PYTHONPATH": str(args.output) + os.pathsep +
           os.environ.get("PYTHONPATH", "")}
    result = subprocess.run(args.command, capture_output=True, text=True, env=env)
    record = {
        "method": "Python sitecustomize socket-construction denial",
        "limitation": "does not observe non-Python syscalls or prove absence of attempted DNS/network operations that bypass Python socket",
        "command": args.command, "exit_code": result.returncode,
        "stdout": result.stdout, "stderr": result.stderr,
        "socket_denial_triggered": "commercial_v1 socket-denial control" in
                                    (result.stdout + result.stderr),
    }
    (args.output / "network-probe.json").write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps(record, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
