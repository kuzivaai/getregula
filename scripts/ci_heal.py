#!/usr/bin/env python3
# regula-ignore
"""CI Healer — classify failing CI jobs and prepare a minimal-fix plan.

This is the local, stdlib-only helper that the self-healing CI workflow
invokes before spinning up a Claude Code session. It takes a raw workflow
log (from `gh run view --log` or the Actions API), identifies the failure
class (lint / type / test / build / unknown), extracts the minimum set of
files and error snippets needed to produce a fix, and writes a JSON plan
that the Claude Code subagent consumes.

It never modifies source files. It never runs tests. It never calls an LLM.
It is deterministic, testable, and backtestable against historical runs.

Usage:
  # Classify a log file
  python3 scripts/ci_heal.py classify --log path/to/log.txt --out plan.json

  # Fetch a specific run's failed logs and classify (requires `gh` CLI)
  python3 scripts/ci_heal.py fetch --run-id 24154460371 --out plan.json

  # Backtest: classify the last N failing CI runs and report
  python3 scripts/ci_heal.py backtest --limit 10

Exit codes:
  0 = classification produced (plan written); may still be out of scope
  1 = classification is out of scope for auto-fix (requires human)
  2 = internal error (cannot read log, etc.)
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRATCH = REPO_ROOT / ".ci-heal"

# Maximum size of a fix this script will green-light for the LLM. Anything
# larger is treated as architectural and requires human intervention.
MAX_AFFECTED_FILES = 5
MAX_LINES_CHANGED_HINT = 50

# ---------------------------------------------------------------------------
# Failure signatures
# ---------------------------------------------------------------------------

# Pytest assertion / failure
PYTEST_FAILED_LINE = re.compile(
    r"FAILED\s+(?P<path>tests/[\w/.\-]+\.py)(?:::(?P<test>[\w\[\]\-_.]+))?"
)
PYTEST_ERROR_HEADER = re.compile(
    r"^(?P<path>tests/[\w/.\-]+\.py):(?P<line>\d+):\s+(?P<etype>\w+Error)",
    re.MULTILINE,
)
PYTEST_SUMMARY = re.compile(
    r"(?P<failed>\d+)\s+failed(?:,\s*(?P<passed>\d+)\s+passed)?"
)

# Python traceback anchors
TRACEBACK_FILE = re.compile(
    r'File\s+"(?P<path>[^"]+)",\s+line\s+(?P<line>\d+)'
)
MODULE_NOT_FOUND = re.compile(
    r"ModuleNotFoundError:\s+No module named ['\"]([^'\"]+)['\"]"
)
IMPORT_ERROR = re.compile(
    r"ImportError:\s+(?P<msg>.*)"
)
SYNTAX_ERROR = re.compile(
    r'\s*File\s+"(?P<path>[^"]+)",\s+line\s+(?P<line>\d+).*\n.*\nSyntaxError:'
)

# Type-checker (mypy / pyright)
MYPY_ERROR = re.compile(
    r"(?P<path>[\w/.\-]+\.py):(?P<line>\d+):\s*error:\s*(?P<msg>.*)"
)
PYRIGHT_ERROR = re.compile(
    r"(?P<path>[\w/.\-]+\.py):(?P<line>\d+):\d+\s*-\s*error:"
)
TSC_ERROR = re.compile(
    r"(?P<path>[\w/.\-]+\.tsx?):(?P<line>\d+):\d+\s*-\s*error\s+TS\d+:"
)

# Linters
FLAKE8_ERROR = re.compile(
    r"(?P<path>[\w/.\-]+\.py):(?P<line>\d+):\d+:\s*(?P<code>[EWF]\d+)"
)
ESLINT_ERROR = re.compile(
    r"(?P<path>[\w/.\-]+\.(?:js|ts|tsx|jsx)):(?P<line>\d+):\d+\s+(?:error|warning)"
)

# Build system
NPM_FAIL = re.compile(
    r"npm ERR!|ERR_\w+|Build failed|webpack compiled with (\d+) errors?"
)
PROCESS_EXIT = re.compile(
    r"##\[error\]Process completed with exit code (\d+)"
)

# Claim auditor
CLAIM_AUDITOR_FAIL = re.compile(
    r"claim-auditor:.*?(\d+)\s+unsourced"
)
CLAIM_AUDITOR_FILE = re.compile(
    r"^\s+(?P<path>[\w/.\-]+\.md)\s+—\s+(?P<count>\d+)\s+unsourced",
    re.MULTILINE,
)

# Deploy race condition
DEPLOY_RACE = re.compile(
    r"due to in progress deployment"
)

# Regula-specific
REGULA_SELFTEST_FAIL = re.compile(
    r"Regula\s+Self[- ]Test.*?FAIL", re.DOTALL | re.IGNORECASE
)

# ---------------------------------------------------------------------------
# Plan
# ---------------------------------------------------------------------------


@dataclass
class FailureEvidence:
    path: str
    line: int | None = None
    snippet: str = ""


@dataclass
class HealPlan:
    run_id: str | None
    failure_type: str            # test | type | lint | claim | build | import | deploy-race | unknown
    confidence: str              # high | medium | low
    affected_files: list[str]
    failing_tests: list[str] = field(default_factory=list)
    error_snippets: list[str] = field(default_factory=list)
    missing_modules: list[str] = field(default_factory=list)
    out_of_scope: bool = False
    out_of_scope_reason: str = ""
    minimal_intervention: str = ""
    instructions_for_agent: str = ""

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2)


# ---------------------------------------------------------------------------
# Log loading
# ---------------------------------------------------------------------------


def strip_ansi(text: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*[A-Za-z]", "", text)


def strip_gha_timestamps(text: str) -> str:
    """Remove the `2026-04-08T19:36:14.8200605Z ` prefix that GHA adds."""
    return re.sub(
        r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z\s?", "", text,
        flags=re.MULTILINE,
    )


def load_log(path: Path) -> str:
    raw = path.read_text(encoding="utf-8", errors="replace")
    return strip_gha_timestamps(strip_ansi(raw))


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------


def _dedupe(seq: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in seq:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


def classify(log_text: str, run_id: str | None = None) -> HealPlan:
    """Walk the log in order of specificity, most specific signals first."""
    plan = HealPlan(
        run_id=run_id,
        failure_type="unknown",
        confidence="low",
        affected_files=[],
    )
    # --- 1. pytest failures ---------------------------------------------
    pytest_failures = list(PYTEST_FAILED_LINE.finditer(log_text))
    if pytest_failures:
        plan.failure_type = "test"
        plan.confidence = "high"
        plan.failing_tests = _dedupe(
            f"{m.group('path')}::{m.group('test') or ''}".rstrip(":")
            for m in pytest_failures
        )
        plan.affected_files = _dedupe(m.group("path") for m in pytest_failures)
        # Capture the AssertionError / Error header lines for context
        for m in PYTEST_ERROR_HEADER.finditer(log_text):
            snippet = _context_around(log_text, m.start(), before=4, after=2)
            plan.error_snippets.append(snippet)
        if len(plan.error_snippets) > 10:
            plan.error_snippets = plan.error_snippets[:10]

    # --- 2. import / module errors --------------------------------------
    mod_misses = _dedupe(m.group(1) for m in MODULE_NOT_FOUND.finditer(log_text))
    if mod_misses:
        plan.missing_modules = mod_misses
        if plan.failure_type == "unknown":
            plan.failure_type = "import"
            plan.confidence = "high"
        plan.error_snippets.append(
            f"ModuleNotFoundError: {', '.join(mod_misses)}"
        )

    # --- 3. type checker errors -----------------------------------------
    type_hits = (
        list(MYPY_ERROR.finditer(log_text))
        + list(PYRIGHT_ERROR.finditer(log_text))
        + list(TSC_ERROR.finditer(log_text))
    )
    if type_hits and plan.failure_type == "unknown":
        plan.failure_type = "type"
        plan.confidence = "medium"
        plan.affected_files = _dedupe(m.group("path") for m in type_hits)
        for m in type_hits[:10]:
            plan.error_snippets.append(
                f"{m.group('path')}:{m.group('line')} — {m.group(0)[:200]}"
            )

    # --- 4. linter errors ------------------------------------------------
    lint_hits = (
        list(FLAKE8_ERROR.finditer(log_text))
        + list(ESLINT_ERROR.finditer(log_text))
    )
    if lint_hits and plan.failure_type == "unknown":
        plan.failure_type = "lint"
        plan.confidence = "high"
        plan.affected_files = _dedupe(m.group("path") for m in lint_hits)
        for m in lint_hits[:10]:
            plan.error_snippets.append(m.group(0)[:200])

    # --- 4b. claim-auditor failures --------------------------------------
    claim_hits = list(CLAIM_AUDITOR_FILE.finditer(log_text))
    if claim_hits and plan.failure_type == "unknown":
        plan.failure_type = "claim"
        plan.confidence = "high"
        plan.affected_files = _dedupe(m.group("path") for m in claim_hits)
        for m in claim_hits:
            plan.error_snippets.append(
                f"{m.group('path')} — {m.group('count')} unsourced claim(s)"
            )
        plan.instructions_for_agent = (
            "Fix unsourced claims by adding a URL, markdown link, or "
            "reference to an existing file in the same paragraph. "
            "Do NOT add claims to .claim-allowlist unless the claim is "
            "contextual/comparative rather than factual."
        )

    # --- 4c. deploy race condition (not fixable by code change) ----------
    if DEPLOY_RACE.search(log_text) and plan.failure_type == "unknown":
        plan.failure_type = "deploy-race"
        plan.confidence = "high"
        plan.out_of_scope = True
        plan.out_of_scope_reason = (
            "GitHub Pages deployment race condition — transient, "
            "resolves on next push. No code fix needed."
        )

    # --- 5. build errors -------------------------------------------------
    if plan.failure_type == "unknown" and NPM_FAIL.search(log_text):
        plan.failure_type = "build"
        plan.confidence = "medium"

    # --- 6. generic exit 1 -----------------------------------------------
    if plan.failure_type == "unknown":
        # Syntax error with traceback
        if "SyntaxError" in log_text:
            plan.failure_type = "syntax"
            plan.confidence = "high"
            tracebacks = list(TRACEBACK_FILE.finditer(log_text))
            plan.affected_files = _dedupe(
                m.group("path") for m in tracebacks
                if "/site-packages/" not in m.group("path")
            )[:MAX_AFFECTED_FILES]
        elif PROCESS_EXIT.search(log_text):
            plan.failure_type = "unknown"
            plan.confidence = "low"
            plan.error_snippets.append(
                "Process exited non-zero but no structured error signature matched."
            )

    # --- 7. scope check --------------------------------------------------
    if len(plan.affected_files) > MAX_AFFECTED_FILES:
        plan.out_of_scope = True
        plan.out_of_scope_reason = (
            f"{len(plan.affected_files)} files affected "
            f"(cap is {MAX_AFFECTED_FILES}). Architectural or cross-cutting "
            f"failure — human review required."
        )
    elif plan.failure_type == "unknown":
        plan.out_of_scope = True
        plan.out_of_scope_reason = (
            "No structured failure signature matched — cannot determine "
            "root cause automatically."
        )

    # --- 8. minimal intervention & agent brief --------------------------
    plan.minimal_intervention = _minimal_intervention(plan)
    plan.instructions_for_agent = _agent_instructions(plan)
    return plan


def _context_around(text: str, pos: int, before: int, after: int) -> str:
    """Return `before` lines before and `after` lines after position `pos`."""
    lines = text.splitlines()
    # Count newlines before pos to get the line index
    line_idx = text.count("\n", 0, pos)
    lo = max(0, line_idx - before)
    hi = min(len(lines), line_idx + after + 1)
    return "\n".join(lines[lo:hi])[:600]


def _minimal_intervention(plan: HealPlan) -> str:
    if plan.out_of_scope:
        return "NONE — out of scope for auto-heal."
    if plan.failure_type == "test":
        return (
            "Identify the smallest code change that makes the listed failing "
            "tests pass WITHOUT modifying the test files. If the test is "
            "legitimately wrong, abort and leave a comment — do not delete "
            "or weaken tests."
        )
    if plan.failure_type == "import":
        mods = ", ".join(plan.missing_modules)
        return (
            f"Missing module(s): {mods}. Either (a) add the import/install "
            f"to the workflow if it is a legitimate new dependency, or (b) "
            f"restore the file that defines it if it was deleted by mistake."
        )
    if plan.failure_type == "type":
        return (
            "Fix the type errors in the affected files with the smallest "
            "possible change. Decompose functions, narrow types, or correct "
            "signatures. DO NOT add `# type: ignore`, `@ts-ignore`, or "
            "equivalent suppressions."
        )
    if plan.failure_type == "lint":
        return (
            "Fix the lint issues in the affected files. DO NOT add "
            "`# noqa`, `eslint-disable`, `biome-ignore`, or any other "
            "suppression comment. Rewrite the offending code."
        )
    if plan.failure_type == "syntax":
        return "Fix the Python syntax error at the reported file/line."
    if plan.failure_type == "build":
        return (
            "Fix the build failure. Check for missing dependencies, "
            "stale lockfile, TypeScript errors, webpack config."
        )
    return "Diagnose and fix the failing step with the smallest possible change."


def _agent_instructions(plan: HealPlan) -> str:
    if plan.out_of_scope:
        return (
            "DO NOT attempt an auto-fix. Post a PR comment explaining the "
            "classification and ask a human to triage."
        )
    return (
        "Strict scope — follow exactly:\n"
        "1. Read ONLY the files listed in `affected_files` and any file they "
        "   transitively depend on. Do not touch unrelated files.\n"
        "2. Apply the smallest possible diff that makes the failing step pass. "
        "   Prefer fixing one file over refactoring many.\n"
        "3. NEVER modify test files to make tests pass. If a test is wrong, "
        "   abort and leave a comment for the human.\n"
        "4. NEVER suppress lint/type errors. Fix the underlying code.\n"
        "5. NEVER refactor, rename, or restructure code beyond the fix.\n"
        "6. Run `python3 tests/test_classification.py && python3 -m scripts.cli "
        "   self-test && python3 -m scripts.cli doctor` locally and confirm "
        "   all three exit zero.\n"
        "7. If the fix requires more than 5 files or more than ~50 lines "
        "   changed, abort and leave a comment for the human.\n"
        "8. Commit with trailer `Ci-Heal-Attempt: N` so the workflow can "
        "   count retries.\n"
    )


# ---------------------------------------------------------------------------
# gh integration
# ---------------------------------------------------------------------------


def gh(*args: str) -> tuple[int, str]:
    if shutil.which("gh") is None:
        return 127, "gh CLI not found"
    # args are hardcoded strings at each call site; no shell injection risk
    proc = subprocess.run(
        ["gh", *args], cwd=REPO_ROOT,
        capture_output=True, text=True, check=False,
    )
    return proc.returncode, proc.stdout + proc.stderr


def _gh_repo_slug() -> str | None:
    rc, out = gh("repo", "view", "--json", "nameWithOwner", "-q",
                 ".nameWithOwner")
    if rc != 0:
        return None
    return out.strip()


def fetch_run_log(run_id: str, dest: Path) -> Path:
    """Fetch a run's failing-job logs via the Actions API (robust for old runs).

    Strategy:
      1. List jobs for the run via `/actions/runs/<id>/jobs`.
      2. For each failing job, fetch `/actions/jobs/<id>/logs` (plain text).
      3. Concatenate into a single log file.
      4. If anything goes wrong, fall back to `gh run view --log`.
    """
    dest.parent.mkdir(parents=True, exist_ok=True)
    slug = _gh_repo_slug()
    collected: list[str] = []
    if slug:
        rc, out = gh(
            "api", f"/repos/{slug}/actions/runs/{run_id}/jobs",
            "--jq", ".jobs[] | select(.conclusion==\"failure\") | .id",
        )
        if rc == 0 and out.strip():
            job_ids = [j for j in out.strip().splitlines() if j.strip()]
            for job_id in job_ids:
                rc2, logs = gh(
                    "api", f"/repos/{slug}/actions/jobs/{job_id}/logs",
                )
                if rc2 == 0 and logs:
                    collected.append(f"\n===== job {job_id} =====\n{logs}")
    if not collected:
        rc, out = gh("run", "view", run_id, "--log")
        if rc == 0:
            collected.append(out)
        else:
            rc2, out2 = gh("run", "view", run_id, "--log-failed")
            if rc2 == 0:
                collected.append(out2)
    dest.write_text("".join(collected), encoding="utf-8")
    return dest


def list_failing_runs(limit: int) -> list[dict]:
    rc, out = gh(
        "run", "list", "--status", "failure", "--workflow", "CI",
        "--limit", str(limit),
        "--json", "databaseId,displayTitle,headBranch,createdAt",
    )
    if rc != 0:
        return []
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        return []


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def cmd_classify(args: argparse.Namespace) -> int:
    log_path = Path(args.log)
    if not log_path.exists():
        print(f"ci-heal: log not found: {log_path}", file=sys.stderr)
        return 2
    text = load_log(log_path)
    plan = classify(text, run_id=args.run_id)
    out_path = Path(args.out) if args.out else None
    if out_path:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(plan.to_json(), encoding="utf-8")
    else:
        print(plan.to_json())
    print_summary(plan)
    return 1 if plan.out_of_scope else 0


def cmd_fetch(args: argparse.Namespace) -> int:
    SCRATCH.mkdir(parents=True, exist_ok=True)
    log_path = SCRATCH / f"{args.run_id}.log"
    fetch_run_log(args.run_id, log_path)
    plan = classify(load_log(log_path), run_id=args.run_id)
    out_path = Path(args.out) if args.out else SCRATCH / "plan.json"
    out_path.write_text(plan.to_json(), encoding="utf-8")
    print_summary(plan)
    return 1 if plan.out_of_scope else 0


def cmd_backtest(args: argparse.Namespace) -> int:
    SCRATCH.mkdir(parents=True, exist_ok=True)
    runs = list_failing_runs(args.limit)
    if not runs:
        print("ci-heal: no failing runs found (is `gh auth` configured?)",
              file=sys.stderr)
        return 2
    print(f"\nci-heal backtest — last {len(runs)} failing CI runs\n")
    header = f"{'run_id':<13} {'type':<8} {'conf':<7} {'scope':<7} {'files':<18} subject"
    print(header)
    print("-" * len(header))
    results: list[dict] = []
    for run in runs:
        run_id = str(run["databaseId"])
        log_path = SCRATCH / f"{run_id}.log"
        if not log_path.exists():
            fetch_run_log(run_id, log_path)
        plan = classify(load_log(log_path), run_id=run_id)
        results.append({
            "run_id": run_id,
            "type": plan.failure_type,
            "confidence": plan.confidence,
            "out_of_scope": plan.out_of_scope,
            "affected": len(plan.affected_files),
            "subject": run.get("displayTitle", ""),
        })
        scope = "human" if plan.out_of_scope else "auto"
        files_display = f"{len(plan.affected_files)} file(s)"
        subj = (run.get("displayTitle") or "")[:40]
        print(f"{run_id:<13} {plan.failure_type:<8} {plan.confidence:<7} "
              f"{scope:<7} {files_display:<18} {subj}")
    print("-" * len(header))
    auto = sum(1 for r in results if not r["out_of_scope"])
    print(f"classified as auto-healable: {auto} / {len(results)}")
    summary_path = SCRATCH / "backtest.json"
    summary_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"full JSON: {summary_path.relative_to(REPO_ROOT)}")
    return 0


def print_summary(plan: HealPlan) -> None:
    print(
        f"\nci-heal: type={plan.failure_type} confidence={plan.confidence} "
        f"files={len(plan.affected_files)} "
        f"{'OUT_OF_SCOPE' if plan.out_of_scope else 'IN_SCOPE'}",
        file=sys.stderr,
    )
    if plan.out_of_scope:
        print(f"  reason: {plan.out_of_scope_reason}", file=sys.stderr)
    if plan.affected_files:
        print(f"  files: {plan.affected_files[:5]}", file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)

    pc = sub.add_parser("classify", help="classify a log file already on disk")
    pc.add_argument("--log", required=True)
    pc.add_argument("--out")
    pc.add_argument("--run-id")
    pc.set_defaults(func=cmd_classify)

    pf = sub.add_parser("fetch", help="fetch a run's log via gh and classify")
    pf.add_argument("--run-id", required=True)
    pf.add_argument("--out")
    pf.set_defaults(func=cmd_fetch)

    pb = sub.add_parser("backtest", help="classify recent failing runs")
    pb.add_argument("--limit", type=int, default=10)
    pb.set_defaults(func=cmd_backtest)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
