#!/usr/bin/env python3
# regula-ignore
"""Tool adapters for the head-to-head benchmark.

Each adapter normalises one tool's output into the common case format
scoring.py consumes. Only the Regula adapter is implemented: competitor
adapters must be written against their CURRENT output formats at run
time (see PREREGISTRATION.md) — guessing them in advance would bake in
unfairness, so attempting to use one raises with instructions instead of
silently producing wrong mappings.

Stdlib only.
"""

import json
import subprocess
import sys
from pathlib import Path


def run_regula(target: str) -> list:
    """Run Regula on a target path, return normalised findings.

    Each normalised finding: {"file": str, "line": int, "tier": str}.
    """
    repo_root = Path(__file__).resolve().parents[2]
    proc = subprocess.run(
        [sys.executable, "-m", "scripts.cli", "check", target,
         "--format", "json"],
        capture_output=True, text=True, cwd=str(repo_root), timeout=600)
    if not proc.stdout.strip():
        raise RuntimeError(
            f"regula produced no output (rc={proc.returncode}): "
            f"{proc.stderr[:300]}")
    doc = json.loads(proc.stdout)
    payload = doc.get("data", doc) if isinstance(doc, dict) else doc
    if isinstance(payload, list):
        findings = payload
    else:
        findings = payload.get("findings", [])
    return [
        {
            "file": f.get("file"),
            "line": f.get("line"),
            "tier": f.get("tier"),
        }
        for f in findings
    ]


def _not_yet(tool: str, hint: str):
    raise NotImplementedError(
        f"{tool} adapter is deliberately unimplemented: write it against "
        f"the tool's CURRENT output format at run time and record the "
        f"mapping in the results file (PREREGISTRATION.md rule 3). {hint}")


def run_air_blackbox(target: str) -> list:
    _not_yet("AIR Blackbox", "PyPI package air-blackbox; pin version.")


def run_systima(target: str) -> list:
    _not_yet("Systima Comply", "npm package; pin version.")


def run_ark_forge(target: str) -> list:
    _not_yet("ark-forge mcp-eu-ai-act", "GitHub MIT repo; pin commit.")


ADAPTERS = {
    "regula": run_regula,
    "air-blackbox": run_air_blackbox,
    "systima": run_systima,
    "ark-forge": run_ark_forge,
}


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in ADAPTERS:
        print(f"usage: adapters.py {{{','.join(ADAPTERS)}}} TARGET")
        raise SystemExit(2)
    print(json.dumps(ADAPTERS[sys.argv[1]](sys.argv[2]), indent=2))
