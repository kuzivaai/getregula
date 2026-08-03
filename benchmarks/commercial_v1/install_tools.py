#!/usr/bin/env python3
"""Install frozen public tools into fresh external virtual environments."""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


PACKAGES = {
    "regula_public": "regula-ai==1.7.4",
    "compliance_agent": "compliance-agent==0.5.0",
    "air_blackbox": "air-blackbox==1.13.2",
    "complior": None,
}


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.output.exists():
        raise SystemExit(f"refusing existing install directory: {args.output}")
    args.output.mkdir(parents=True)
    records = []
    for tool, package in PACKAGES.items():
        record = {"tool": tool, "package": package,
                  "started_at": datetime.now(timezone.utc).isoformat()}
        if package is None:
            record.update({"command": None, "exit_code": None,
                           "status": "identity_unresolved_at_freeze",
                           "stdout": "", "stderr": ""})
        else:
            env = args.output / tool
            venv = subprocess.run([sys.executable, "-m", "venv", str(env)],
                                  capture_output=True, text=True)
            command = [str(env / "bin" / "python"), "-m", "pip", "install",
                       "--disable-pip-version-check", package]
            if venv.returncode == 0:
                install = subprocess.run(command, capture_output=True, text=True)
                stdout, stderr, exit_code = (
                    install.stdout, install.stderr, install.returncode)
            else:
                stdout, stderr, exit_code = venv.stdout, venv.stderr, venv.returncode
            record.update({"command": command, "exit_code": exit_code,
                           "status": "installed" if exit_code == 0 else "install_failed",
                           "stdout": stdout, "stderr": stderr})
        record["finished_at"] = datetime.now(timezone.utc).isoformat()
        records.append(record)
        (args.output / f"{tool}.json").write_text(json.dumps(record, indent=2) + "\n")
    (args.output / "installations.json").write_text(json.dumps(records, indent=2) + "\n")
    print(f"retained {len(records)} frozen installation outcomes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
