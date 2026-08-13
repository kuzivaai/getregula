#!/usr/bin/env python3
# regula-ignore
"""Produce the landing page's decision demos from real command output.

The former gap, comply, check, and plan panels presented detector-derived
risk tiers, article duties, readiness percentages, deadlines, and effort
estimates as command output. The decision kernel cannot emit those claims
without sourced applicability facts. This script runs all four commands
against a tracked-only snapshot of a committed fixture and records their
honest resolvable-facts responses in `data/gap_demo.json`.

`tests/test_gap_demo.py` re-runs the commands, checks the artefact, and binds
the published panels to these outputs. A `$` prompt is treated as a claim
about real command behaviour, not as decorative copy.

WHY THIS FIXTURE
----------------
`tests/fixtures/sample_high_risk` is tracked. The criterion was fixed
before any score was looked at: the target must be committed and must be
scanned as the page depicts it, with no flags.

Choosing a tracked target is not sufficient when ignored content can sit
inside its directory. The builder therefore asks Git for the fixture's
tracked files, copies only those files to a temporary snapshot, and runs all four
commands there. Git failure, an empty tracked population, a copy failure, or
a command/build failure is fatal. Local ignored state is never an input.

Two candidates were rejected for reasons independent of their scores:

- `regula gap .` on the Regula repository itself scores 100%, and that
  number is computed partly over `conformity-evidence-project-*`
  directories which are untracked and gitignored. No clone reproduces it.
  Measurement rule 4b: untracked files are not surfaces.
- A purpose-built fixture would be the shop window chosen by its author,
  which is the metric gaming PROGRAMME.md principle 3 forbids.

The result is intentionally independent of detector ranking: unresolved
scope facts yield `insufficient_information`, zero attached article
observations, and a ranked list of facts the user can resolve next.

Usage:
    python3 scripts/build_gap_demo.py           # write the artefact
    python3 scripts/build_gap_demo.py --check   # compare, do not write

Stdlib only.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

# Self-protection for the bare sibling import in __main__ (tree_guard), per
# .claude/rules/python-scripts.md: without it the module imports only when a
# caller happens to have seeded sys.path first.
sys.path.insert(0, str(Path(__file__).parent))

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURE = "tests/fixtures/sample_high_risk"
ARTEFACT = REPO_ROOT / "data/gap_demo.json"

RESULT_TYPE = re.compile(r"^Decision:\s+(\S+)", re.MULTILINE)
MODEL_VERSION = re.compile(r"^Model:\s+(\S+)", re.MULTILINE)
RULE_RESOLUTION = re.compile(r"^Rule resolution:\s+(\S+)", re.MULTILINE)
UNRESOLVED_COUNT = re.compile(
    r"^Facts needed to resolve the next decision:\s+(\d+)", re.MULTILINE)
FACT_ID = re.compile(r"^\s+-\s+([a-z0-9_]+):", re.MULTILINE)
ARTICLE_COUNTS = re.compile(
    r"^Article observations emitted:\s+(\d+); held pending applicability:\s+(\d+)",
    re.MULTILINE,
)


def _run(args: list[str]) -> str:
    # N53: policy_config resolves $REGULA_POLICY, then ./regula-policy.yaml,
    # then ./configs/. With cwd=REPO_ROOT a gitignored root policy file
    # shadows the tracked configs/regula-policy.yaml, and no git-based guard
    # on the fixture can see it. Pinning the tracked policy through the
    # highest-precedence route makes the generator's input explicit instead
    # of resolved-by-search.
    env = dict(os.environ,
               REGULA_POLICY=str(REPO_ROOT / "configs" / "regula-policy.yaml"))
    proc = subprocess.run([sys.executable, *args], cwd=str(REPO_ROOT),
                          env=env,
                          capture_output=True, text=True, timeout=1800)
    if proc.returncode not in (0, 1):
        raise RuntimeError(f"{args} failed rc={proc.returncode}: "
                           f"{proc.stderr[:400]}")
    if not proc.stdout.strip():
        raise RuntimeError(f"{args} produced no output")
    return proc.stdout


@contextmanager
def _tracked_fixture_snapshot():
    """Yield a directory containing exactly Git's tracked fixture files."""
    proc = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "ls-files", "-z", "--", FIXTURE],
        capture_output=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            "Git could not derive the gap-demo inputs: "
            + proc.stderr.decode("utf-8", errors="replace")[:400]
        )
    paths = [Path(raw.decode("utf-8")) for raw in proc.stdout.split(b"\0") if raw]
    if not paths:
        raise RuntimeError(f"Git reported no tracked files under {FIXTURE}")

    with tempfile.TemporaryDirectory(prefix="regula-gap-demo-") as tmp:
        snapshot = Path(tmp) / Path(FIXTURE).name
        for relative in paths:
            try:
                within_fixture = relative.relative_to(FIXTURE)
            except ValueError as exc:
                raise RuntimeError(
                    f"Git returned an input outside {FIXTURE}: {relative}"
                ) from exc
            source = REPO_ROOT / relative
            destination = snapshot / within_fixture
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
        yield snapshot


def _decision_output(text: str, require_article_counts: bool = False) -> dict:
    matches = {
        "result_type": RESULT_TYPE.search(text),
        "model_version": MODEL_VERSION.search(text),
        "rule_resolution": RULE_RESOLUTION.search(text),
        "unresolved_count": UNRESOLVED_COUNT.search(text),
    }
    article_counts = ARTICLE_COUNTS.search(text)
    if require_article_counts:
        matches["article_counts"] = article_counts
    missing = [name for name, match in matches.items() if match is None]
    if missing:
        raise RuntimeError(
            "could not parse real decision output fields: " + ", ".join(missing)
        )
    output = {
        "result_type": matches["result_type"].group(1),
        "model_version": matches["model_version"].group(1),
        "rule_resolution": matches["rule_resolution"].group(1),
        "unresolved_count": int(matches["unresolved_count"].group(1)),
        "unresolved_fact_ids": FACT_ID.findall(text),
    }
    if article_counts:
        output["article_observations_emitted"] = int(article_counts.group(1))
        output["article_observations_held"] = int(article_counts.group(2))
    return output


def build() -> dict:
    with _tracked_fixture_snapshot() as snapshot:
        check_out = _run([
            "-m", "scripts.cli", "check", str(snapshot), "--explain"
        ])
        plan_out = _run([
            "-m", "scripts.cli", "plan", "--project", str(snapshot)
        ])
        gap_out = _run(["-m", "scripts.cli", "gap", str(snapshot)])
        comply_out = _run(
            ["-m", "scripts.cli", "comply", str(snapshot), "--all"]
        )

    check = _decision_output(check_out)
    plan = _decision_output(plan_out)
    gap = _decision_output(gap_out, require_article_counts=True)
    comply = _decision_output(comply_out, require_article_counts=True)

    return {
        "_what_this_is": (
            "The landing page's terminal demo, parsed from real command "
            "output against a committed fixture. Produced by "
            "scripts/build_gap_demo.py. Never hand-edited: "
            "tests/test_gap_demo.py re-runs all four commands and fails on "
            "disagreement, and fails if the site shows a percentage this "
            "file does not contain."),
        "_why_it_exists": (
            "The block it replaces was invented output shown behind a $ "
            "prompt. A visitor reads that as a real scan."),
        "fixture": FIXTURE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check": {
            "command": "regula check " + FIXTURE + " --explain",
            **check,
        },
        "plan": {
            "command": "regula plan --project " + FIXTURE,
            **plan,
        },
        "gap": {
            "command": "regula gap " + FIXTURE,
            **gap,
        },
        "comply": {
            "command": "regula comply " + FIXTURE + " --all",
            **comply,
        },
    }


def _comparable(doc: dict) -> str:
    return json.dumps({k: v for k, v in doc.items() if k != "generated_at"},
                      indent=2, sort_keys=True)


def main(argv: list[str]) -> int:
    fresh = build()
    if "--check" in argv:
        if not ARTEFACT.exists():
            print(f"MISSING: {ARTEFACT.relative_to(REPO_ROOT)}",
                  file=sys.stderr)
            return 1
        committed = json.loads(ARTEFACT.read_text(encoding="utf-8"))
        if _comparable(committed) != _comparable(fresh):
            print("data/gap_demo.json disagrees with a fresh run. Re-run "
                  "scripts/build_gap_demo.py and update the site blocks it "
                  "feeds.", file=sys.stderr)
            return 1
        print("data/gap_demo.json matches a fresh run.")
        return 0

    ARTEFACT.write_text(json.dumps(fresh, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8")
    print(f"wrote {ARTEFACT.relative_to(REPO_ROOT)}")
    print(f"  gap    {fresh['gap']['result_type']}  "
          f"{fresh['gap']['article_observations_emitted']} article observations")
    print(f"  comply {fresh['comply']['result_type']}  "
          f"{fresh['comply']['article_observations_emitted']} article observations")
    print(f"  check  {fresh['check']['result_type']}")
    print(f"  plan   {fresh['plan']['result_type']}")
    return 0


if __name__ == "__main__":
    from tree_guard import stamp
    stamp()
    raise SystemExit(main(sys.argv[1:]))
