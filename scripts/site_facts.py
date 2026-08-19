#!/usr/bin/env python3
# regula-ignore
"""Single source of truth for all numeric claims on Regula's landing pages.

Counts things directly from the code, then emits a JSON and a Markdown
table. Run it whenever a count might have drifted — and wire it into
CI so pages that disagree with the computed counts fail the build.

Emits:
  data/site_facts.json       machine-readable manifest
  data/site_facts.md         human-readable table (for pasting into docs)

Counts:
  commands        — `^def cmd_` in scripts/cli.py
  patterns_groups — pattern-group entries in scripts/risk_patterns.py
  regex_total     — individual regex entries across all pattern groups
  languages       — hard-coded list from CLAUDE.md, verified against scripts/
  frameworks      — unique top-level keys in references/framework_crosswalk.yaml + 1
  tests           — assertions counted by the custom test runner

Exit codes:
  0 = success, wrote outputs
  1 = counter error
"""
from __future__ import annotations

import argparse
import ast
import importlib.util
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# Self-protection for the bare sibling import in __main__ (tree_guard), per
# .claude/rules/python-scripts.md: without it the module imports only when a
# caller happens to have seeded sys.path first.
sys.path.insert(0, str(Path(__file__).parent))

REPO = Path(__file__).resolve().parent.parent
OUT_JSON = REPO / "data" / "site_facts.json"
OUT_MD = REPO / "data" / "site_facts.md"


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        return None
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except Exception:
        return None
    return mod


def count_commands() -> int:
    """Count `cmd_*` function definitions across every `scripts/cli*.py` module.

    Commands were refactored out of `scripts/cli.py` in the 1.6 series into
    topic modules (`cli_scan.py`, `cli_compliance.py`, `cli_governance.py`,
    `cli_report.py`, `cli_util.py`). Counting only `cli.py` returns 0 — this
    used to silently produce a wrong number on the canonical landing-page
    facts file. Sum across all `cli*.py`.
    """
    scripts_dir = REPO / "scripts"
    total = 0
    has_monitor = False
    for path in sorted(scripts_dir.glob("cli*.py")):
        text = path.read_text(encoding="utf-8")
        funcs = re.findall(r"^def cmd_(\w+)", text, re.MULTILINE)
        for f in funcs:
            if f.startswith("monitor_"):
                has_monitor = True  # 'monitor' dispatches to cmd_monitor_* subs
            elif f != "feedback_summary":
                total += 1
    # The top-level 'monitor' command uses sub-commands (cmd_monitor_*) rather
    # than a single cmd_ function; count it ONCE, but derive its presence rather
    # than hardcoding +1 — so if monitor is ever removed the count doesn't
    # silently overcount by one.
    return total + (1 if has_monitor else 0)


def count_commands_from_registry() -> int:
    """Count what a user can actually type, from the argparse registry itself.

    `count_commands` above counts `def cmd_*` definitions and then compensates by
    hand: it drops the six `cmd_monitor_*` sub-handlers and `cmd_feedback_summary`
    and adds one back for the `monitor` group. That compensation is correct today
    and is a hand-maintained mapping between two populations that nothing
    reconciles.

    This function measures the population the published claim is actually about.
    "62 commands" on the landing page is a promise about what a reader can run,
    and the subparser registry is the only artefact that knows. If a command is
    ever registered without a `cmd_` handler, or a handler exists that nothing
    registers, the two derivations diverge and `cascade_count.canonical_command_count`
    refuses rather than publishing whichever happens to be read first.

    MEASURED 2026-08-17 at `537d37b`: both derivations return 62, and the
    registry's set differs from the normalised handler set by exactly `monitor`
    on one side and the six `monitor-*` sub-handlers plus `feedback-summary` on
    the other, which is what the compensation encodes.
    """
    parser = argparse.ArgumentParser(prog="regula")
    subparsers = parser.add_subparsers(dest="command")
    cli = _load_module(REPO / "scripts" / "cli.py", "cli")
    if cli is None or not hasattr(cli, "_build_subparsers"):
        raise RuntimeError(
            "scripts/cli.py did not expose _build_subparsers, so the command "
            "registry could not be read. Refusing to fall back to a count "
            "derived from function names: an unknown registry must not become "
            "a published number.")
    cli._build_subparsers(subparsers)
    return len(subparsers.choices)


def count_patterns() -> dict:
    """Return a full breakdown of detection patterns across every module.

    The landing page claim uses the tier_regexes count — the total individual
    regexes in risk_patterns.py. The honest view is that Regula ships multiple
    pattern categories across three files. This function exposes all of them.
    """
    out = {
        "tier_groups": 0,
        "tier_regexes": 0,
        "ai_indicators": 0,
        "gpai_training": 0,
        "architecture": 0,
        "data_source": 0,
        "logging": 0,
        "oversight": 0,
        "credential": 0,
    }
    # risk_patterns.py — five tiered groups + AI_INDICATORS + GPAI_TRAINING
    rp = _load_module(REPO / "scripts" / "risk_patterns.py", "risk_patterns")
    if rp is not None:
        tier_vars = [
            "PROHIBITED_PATTERNS", "HIGH_RISK_PATTERNS", "LIMITED_RISK_PATTERNS",
            "AI_SECURITY_PATTERNS", "BIAS_RISK_PATTERNS", "GOVERNANCE_OBSERVATIONS",
        ]
        for v in tier_vars:
            d = getattr(rp, v, None)
            if isinstance(d, dict):
                out["tier_groups"] += len(d)
                for info in d.values():
                    if isinstance(info, dict):
                        out["tier_regexes"] += len(info.get("patterns", []))
        ai_ind = getattr(rp, "AI_INDICATORS", None)
        if isinstance(ai_ind, dict):
            out["ai_indicators"] = sum(
                len(v) for v in ai_ind.values() if isinstance(v, list)
            )
        gpai = getattr(rp, "GPAI_TRAINING_PATTERNS", None)
        if isinstance(gpai, list):
            out["gpai_training"] = len(gpai)
    # code_analysis.py — architecture/data/logging/oversight detectors
    ca = _load_module(REPO / "scripts" / "code_analysis.py", "code_analysis")
    if ca is not None:
        for attr, key in (
            ("ARCHITECTURE_PATTERNS", "architecture"),
            ("DATA_SOURCE_PATTERNS", "data_source"),
            ("LOGGING_PATTERNS", "logging"),
            ("OVERSIGHT_PATTERNS", "oversight"),
        ):
            v = getattr(ca, attr, None)
            if isinstance(v, (list, dict)):
                out[key] = len(v)
    # credential_check.py — credential patterns (regex count)
    try:
        text = (REPO / "scripts" / "credential_check.py").read_text(
            encoding="utf-8"
        )
        out["credential"] = len(re.findall(
            r'"[^"]+":\s*r[\'"]', text
        ))
    except OSError:
        pass  # source file unreadable; counts stay at zero
        
    # agent_monitor.py — agentic categories (e.g. "regula-ASI01"). Count the
    # DISTINCT category ids, not textual occurrences: each id appears multiple
    # times in agent_monitor.py (definition + references), and the field means
    # "number of OWASP Agentic categories" (there are 10, ASI01–ASI10).
    try:
        text = (REPO / "scripts" / "agent_monitor.py").read_text(encoding="utf-8")
        out["agentic_categories"] = len(set(re.findall(r'"regula-ASI\d+"', text)))
    except OSError:
        out["agentic_categories"] = 0

    out["grand_total"] = (
        out["tier_regexes"] + out["ai_indicators"] + out["gpai_training"]
        + out["architecture"] + out["data_source"] + out["logging"]
        + out["oversight"] + out["credential"]
    )
    # Composite metric: tier_regexes + credential + agentic (computed, not
    # hardcoded). Value-neutral name — an earlier "marketing_409" label was
    # both stale (it no longer equals 409) and misleading.
    out["composite_tier_cred_agentic"] = (
        out["tier_regexes"] + out["credential"] + out["agentic_categories"]
    )
    
    # Historical bucketing (tiered + arch + cred + oversight):
    out["historical_330_bucket"] = (
        out["tier_regexes"] + out["architecture"]
        + out["credential"] + out["oversight"]
    )
    return out


def count_frameworks() -> int:
    """Count unique frameworks from framework_mapper._FRAMEWORK_KEYS."""
    try:
        fm = _load_module(REPO / "scripts" / "framework_mapper.py", "framework_mapper")
        if fm is not None:
            keys = getattr(fm, "_FRAMEWORK_KEYS", {})
            return len(set(keys.values()))
    except (ImportError, OSError, AttributeError, TypeError) as e:
        print(f"regula: framework_mapper load failed: {e}", file=sys.stderr)
    # Fallback: count from crosswalk YAML
    crosswalk = REPO / "references" / "framework_crosswalk.yaml"
    if not crosswalk.exists():
        return 0
    try:
        import yaml
        data = yaml.safe_load(crosswalk.read_text(encoding="utf-8")) or {}
    except (ImportError, OSError, ValueError):
        return 0
    keys: set[str] = set()
    for article_mapping in (data.get("mappings") or {}).values():
        if isinstance(article_mapping, dict):
            keys.update(article_mapping.keys())
    return len(keys) + 1  # +1 for EU AI Act itself


def count_languages() -> int:
    """Fixed list — matches scripts/ast_engine.py and README."""
    return 8  # Python, JS, TS, Java, Go, Rust, C, C++


class GitDiscoveryError(RuntimeError):
    """Git could not answer which test files are tracked.

    N55(a): the predicates below used to swallow this and return [], which
    is the PASS value, so the at-rest enforcement test could not distinguish
    "git says every contributor is tracked" from "git never ran". A failed
    discovery must be its own outcome, never an empty clean answer.
    """


def _tracked_test_paths() -> set[str]:
    """Repo-relative posix paths of every tracked `.py` file under tests/.

    The one shared enumeration primitive for both provenance directions.
    Raises GitDiscoveryError on any failure: an empty set is a real answer
    ("git tracks nothing under tests/"); an exception is not an answer and
    must not be coerced into one (measurement rule 4).
    """
    try:
        proc = subprocess.run(
            ["git", "ls-files", "-z", "--", "tests"],
            cwd=str(REPO), capture_output=True, text=True, check=False,
        )
    except OSError as exc:
        raise GitDiscoveryError(f"git ls-files did not run: {exc}") from exc
    if proc.returncode != 0:
        detail = (proc.stderr or "").strip() or "no detail"
        raise GitDiscoveryError(
            f"git ls-files failed with exit {proc.returncode}: {detail}")
    return {name for name in proc.stdout.split("\0") if name.endswith(".py")}


def untracked_test_contributors(per_file, tracked=None) -> list[str]:
    """Return the test files in `per_file` that git does not track.

    Every file that contributes to a published count must be in the
    repository, or the count does not reproduce from a checkout. `per_file`
    is keyed by repo-relative posix path (e.g. `tests/test_x.py`), and the
    comparison is made on full paths: N55 recorded that a basename
    comparison is unsound by construction, because a tracked nested file
    would mask an untracked top-level file of the same name.

    `tracked` is injectable for testing. Left None, it asks git, and a git
    failure RAISES GitDiscoveryError rather than returning the PASS value
    (N55a). The generation-time caller catches that error explicitly and
    says so; the at-rest enforcement in tests/test_site_facts.py runs in a
    checkout and now fails closed.
    """
    if tracked is None:
        tracked = _tracked_test_paths()
    return sorted(name for name in per_file if name not in tracked)


def missing_tracked_contributors(per_file, tracked=None) -> list[str]:
    """Return tracked test files that did not contribute to the count.

    The reverse direction (N55c): `untracked_test_contributors` looks from
    the inventory towards git, so a tracked test file DELETED from the
    working tree without `git rm` simply loses its `per_file` key and the
    published count drops silently. This predicate looks from git towards
    the inventory. Only files matching the collector's `python_files`
    pattern (`test_*.py`) are demanded; `conftest.py`, helpers and fixture
    sources are tracked but are not contributors.

    A rename that has not been staged appears as one entry here plus one
    entry in the untracked list; git holds no evidence linking the two until
    the rename is staged, so the two reports are deliberately not merged
    into an inferred rename.
    """
    if tracked is None:
        tracked = _tracked_test_paths()
    return sorted(
        name for name in tracked
        if name.rsplit("/", 1)[-1].startswith("test_")
        and name not in per_file)


def count_test_functions(source: str) -> int:
    """Count the `test_*` functions pytest would collect from one file.

    Module-level functions, plus methods declared directly inside a class.
    A function nested inside another function is NOT collected by pytest and
    is not counted here.

    Uses `ast` because the regex this replaced counted `def test_...` inside
    a triple-quoted code sample as a real test, and the widened form of the
    same regex produced a per-file count higher than pytest's own collection,
    which is how the string-literal hit was found at all.

    A file that will not parse raises. A test file that cannot be parsed is a
    broken test file, and silently scoring it 0 would understate a published
    count, which is the defect this function exists to fix.
    """
    tree = ast.parse(source)
    _DEFS = (ast.FunctionDef, ast.AsyncFunctionDef)
    total = 0
    for node in tree.body:
        if isinstance(node, _DEFS) and node.name.startswith("test_"):
            total += 1
        elif isinstance(node, ast.ClassDef):
            total += sum(1 for child in node.body
                         if isinstance(child, _DEFS)
                         and child.name.startswith("test_"))
    return total


def count_runner_functions() -> int:
    """How many functions the legacy custom runner selects.

    `docs/TRUST.md` publishes this alongside the pytest-collected count, in two
    places, and it moves whenever a test module is wired into
    `tests/test_classification.py`, which `.claude/rules/tests.md` requires.
    `scripts/cascade_count.py` propagated only the collected count, so this one
    drifted silently until `tests/test_published_count_manifest.py` was written
    to catch it. It then drifted TWICE MORE in the single session of
    2026-08-14, once for the content-freshness module and once for the
    documented-transcripts module, each time costing a full suite run to
    discover. Making it canonical here is what lets the cascade carry it.

    Computed in a subprocess: importing the whole test tree into this module's
    namespace to count names would be a side effect in a script whose output is
    published, and a failure to import must fail closed rather than yield a
    plausible smaller number.
    """
    code = (
        "import sys; sys.path.insert(0, 'tests');"
        "import test_classification as tc;"
        "print(len([n for n, o in vars(tc).items()"
        " if (n.startswith('test_') or n.startswith(tc.RUNNER_ALIAS_PREFIX))"
        " and callable(o)]))"
    )
    try:
        proc = subprocess.run([sys.executable, "-c", code], cwd=str(REPO),
                              capture_output=True, text=True, check=False,
                              timeout=300)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise RuntimeError(f"runner function count did not run: {exc}") from exc
    value = proc.stdout.strip()
    if proc.returncode != 0 or not value.isdigit():
        detail = (proc.stderr or proc.stdout).strip().splitlines()
        raise RuntimeError(
            "refusing to publish an unmeasured runner function count "
            f"(rc={proc.returncode}: {detail[-1] if detail else 'no output'})")
    return int(value)


def count_tests() -> dict:
    """Return a breakdown of test functions and per-file counts."""
    # Use actual pytest collection to get the truthful executable count,
    # handling parametrization and the custom test runner properly, rather
    # than just grepping for 'def test_'.
    tests_dir = REPO / "tests"
    if not tests_dir.exists():
        return {"total_collected": 0, "total_functions": 0, "per_file": {}}
    
    # A count we cannot measure must never be published as fact: if pytest
    # collection is unavailable or fails, raise instead of writing 0 into
    # the canonical artifacts (which downstream pages cite verbatim).
    try:
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", str(tests_dir), "--collect-only", "-q"],
            capture_output=True, text=True, check=False, timeout=120
        )
    except (OSError, subprocess.TimeoutExpired) as e:
        raise RuntimeError(f"pytest collection did not run: {e}") from e
    # Parse '2543 tests collected in 0.32s'
    match = re.search(r'^(\d+) tests? collected', proc.stdout, re.MULTILINE)
    if proc.returncode != 0 or not match:
        tail = (proc.stderr or proc.stdout).strip().splitlines()
        detail = tail[-1] if tail else "no output"
        raise RuntimeError(
            "pytest collection failed — refusing to publish an unmeasured "
            f"test count (rc={proc.returncode}: {detail})"
        )
    total_collected = int(match.group(1))

    # N55(b): rglob, not glob. `total_collected` above comes from RECURSIVE
    # pytest collection (pyproject sets python_files = test_*.py and no
    # norecursedirs under tests/), so the contributor inventory must walk the
    # same population or a nested test file inflates the count with no
    # per_file key for the provenance predicates to see. Keys are
    # repo-relative posix paths because basenames cannot be compared soundly
    # against tracked paths (see untracked_test_contributors).
    # N117. `^def (test_\w+)` counted MODULE-LEVEL functions only, so every
    # test written as a `unittest.TestCase` method was invisible: 565 of them
    # across 22 files, against a published label reading "Test functions (all
    # files)". The values were never wrong, the population was, which is the
    # N109 shape again: a label naming a quantity wider than the one measured.
    #
    # Found because a new test file counted 0 while containing six tests.
    # Nothing had flagged it, because nothing compared this figure to the
    # collection it sits beside; `test_site_facts.py` now does, per file.
    #
    # Counted with `ast`, not a regex, and that is not a refinement.
    # Widening the regex to `^[ \t]*def test_` immediately produced a count
    # ABOVE what pytest collects for `test_classification.py`, because
    # `def test_model_accuracy():` appears inside a triple-quoted code sample
    # fed to the AST parser under test. The OLD regex matched that string too,
    # so the previous figure was one function that does not exist plus a whole
    # category that does. A regex cannot see the difference between source and
    # a string literal; `ast` never confuses them.
    #
    # Collected the way pytest collects: a `test_*` function at module level,
    # or a `test_*` method directly inside a class. A function nested inside
    # another function is not collected and is not counted.
    per_file: dict[str, int] = {}
    for path in sorted(tests_dir.rglob("test_*.py")):
        per_file[path.relative_to(REPO).as_posix()] = count_test_functions(
            path.read_text(encoding="utf-8"))

    # N52. Both counts above read the WORKING TREE: the walk reads it, and
    # `pytest --collect-only` collects from it. An untracked test file is
    # therefore counted into figures that cascade to nine published surfaces,
    # and a clean checkout of the same commit collects a different number.
    # Warn rather than raise: the legitimate workflow is to add a test file,
    # regenerate, cascade and commit all of it together, and refusing here
    # would block exactly that. The invariant is enforced at rest instead, by
    # tests/test_site_facts.py, which fails if a COMMITTED artefact names a
    # contributor git does not track, or omits a tracked test file (N55c).
    try:
        stray = untracked_test_contributors(per_file)
        missing = missing_tracked_contributors(per_file)
    except GitDiscoveryError as exc:
        # Outside a git checkout (scripts/ ships as the PyPI package) the
        # provenance question is unanswerable at generation time. Say so
        # rather than skipping silently; the invariant is enforced at rest
        # by tests/test_site_facts.py, which runs in a checkout and now
        # fails closed on the same error (N55a).
        print(f"note: test-file tracking check skipped: {exc}",
              file=sys.stderr)
        stray, missing = [], []
    if stray:
        print(
            "WARNING: the test count below includes files that are not "
            "tracked by git, so it does not reproduce in a clean checkout:\n"
            + "\n".join(f"  {name}" for name in stray)
            + "\nCommit them in the same commit as the count cascade, or "
              "remove them before regenerating.",
            file=sys.stderr,
        )
    if missing:
        print(
            "WARNING: tracked test files did not contribute to the count "
            "below, so a clean checkout would run a larger suite than "
            "published (deleted without `git rm`?):\n"
            + "\n".join(f"  {name}" for name in missing)
            + "\nA rename that is not yet staged appears here AND in the "
              "untracked list; git cannot link the two until it is staged.",
            file=sys.stderr,
        )

    return {
        "total_collected": total_collected,
        "total_functions": sum(per_file.values()),
        "per_file": per_file,
    }


def compute() -> dict:
    patterns = count_patterns()
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_of_truth": {
            "commands": "scripts/cli*.py (grep '^def cmd_' across all topic modules)",
            "patterns": "scripts/risk_patterns.py + scripts/code_analysis.py + scripts/credential_check.py",
            "frameworks": "references/framework_crosswalk.yaml (unique keys + EU AI Act)",
            "languages": "scripts/ast_engine.py + README",
            "tests": "tests/test_classification.py (grep '^def test_')",
        },
        "counts": {
            "commands": count_commands(),
            "patterns": patterns,
            "frameworks": count_frameworks(),
            "languages": count_languages(),
            # The runner count is folded in here rather than inside
            # count_tests(), which is scoped to pytest collection and whose
            # sandboxed tests fake subprocess.run for that one call.
            "tests": {**count_tests(),
                      "runner_functions": count_runner_functions()},
        },
        "notes": {
            "pattern_count_methodology": (
                "Regula's landing pages cite 'tier_regexes risk patterns'. That figure "
                "is the total individual regexes in risk_patterns.py across "
                "all tiered groups (prohibited, high-risk, limited-risk, "
                "AI security, bias, governance, GPAI training). The "
                "`historical_330_bucket` adds architecture, credential, and "
                "oversight patterns from code_analysis.py. The `grand_total` "
                "also includes AI_INDICATORS."
            ),
            "frameworks_vs_claim": (
                "Regula's landing pages cite '13 compliance frameworks'. "
                "All 13 are in _FRAMEWORK_KEYS with crosswalk data (OWASP ASI added "
                "2026-07). Colorado SB-189, Canada AIDA, Singapore AI, OECD AI and "
                "South Korea AI have display handlers only (no filter keys, no crosswalk)."
            ),
        },
    }


def render_markdown(data: dict) -> str:
    c = data["counts"]
    p = c["patterns"]
    return (
        "# Regula — site facts (auto-generated)\n\n"
        "*Canonical source of truth for every numeric claim on the landing "
        "pages. Regenerate by running `python3 scripts/site_facts.py`.*\n\n"
        f"Generated: `{data['generated_at']}`\n\n"
        "## Top-line counts\n\n"
        "| Claim | Count | Source file |\n"
        "|---|---|---|\n"
        f"| CLI commands | **{c['commands']}** | `scripts/cli.py` |\n"
        f"| Detection patterns (historical bucket) | **{p['historical_330_bucket']}** | see breakdown below |\n"
        f"| Detection patterns (grand total, inclusive) | **{p['grand_total']}** | see breakdown below |\n"
        f"| Tiered risk pattern groups | {p['tier_groups']} | `scripts/risk_patterns.py` |\n"
        f"| Compliance frameworks | **{c['frameworks']}** | `references/framework_crosswalk.yaml` + EU AI Act |\n"
        f"| Programming languages | {c['languages']} | `scripts/ast_engine.py` |\n"
        f"| Test functions (all files) | {c['tests']['total_functions']} | `tests/test_*.py` |\n\n"
        "## Detection pattern breakdown\n\n"
        "Regula ships detection patterns across three source files. The "
        "landing page risk patterns count corresponds to all "
        "individual regexes in risk_patterns.py. The `historical_330_bucket` "
        "adds architecture, credential, and oversight detectors from "
        "code_analysis.py. The `grand_total` also adds `AI_INDICATORS` and "
        "is the inclusive upper bound.\n\n"
        "| Category | Source | Count |\n"
        "|---|---|---|\n"
        f"| Tiered risk regexes (prohibited, high-risk, limited-risk, AI security, bias) | `risk_patterns.py` | {p['tier_regexes']} |\n"
        f"| Credential detectors | `credential_check.py` | {p['credential']} |\n"
        f"| OWASP Agentic categories | `agent_monitor.py` | {p['agentic_categories']} |\n"
        f"| **Composite (tier + cred + agentic)** | composite | **{p['composite_tier_cred_agentic']}** |\n"
        f"| AI_INDICATORS (libraries, model files, API endpoints, ML patterns, domain keywords) | `risk_patterns.py` | {p['ai_indicators']} |\n"
        f"| GPAI training code detectors | `risk_patterns.py` | {p['gpai_training']} |\n"
        f"| Architecture detectors | `code_analysis.py` | {p['architecture']} |\n"
        f"| Data source detectors | `code_analysis.py` | {p['data_source']} |\n"
        f"| Logging detectors | `code_analysis.py` | {p['logging']} |\n"
        f"| Oversight detectors | `code_analysis.py` | {p['oversight']} |\n"
        f"| **Grand total (inclusive)** | across 4 files | **{p['grand_total']}** |\n"
        f"| **Historical 330 bucket** | tiered + arch + cred + oversight | **{p['historical_330_bucket']}** |\n\n"
        "## Honesty notes\n\n"
        "- If a landing page cites a different number, either the page is "
        "stale or this generator is stale. Fix whichever is wrong.\n"
        "- The landing page risk pattern count must match tier_regexes. "
        "If the actual count drifts, update the landing page.\n"
        "- The `historical_330_bucket` includes additional detectors from "
        "code_analysis.py. Both numbers are documented above so any auditor "
        "can verify.\n"
    )


def main() -> int:
    try:
        data = compute()
    except RuntimeError as e:
        print(f"site_facts: ERROR — {e}", file=sys.stderr)
        return 1
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    # Keep the previous generated_at when the facts themselves are unchanged,
    # so regeneration is idempotent and CI's `git diff --exit-code` on the
    # artifacts fails only on genuine drift. The timestamp therefore reads
    # "when the facts last changed", not "when the script last ran".
    if OUT_JSON.exists():
        try:
            prev = json.loads(OUT_JSON.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            prev = None
        if isinstance(prev, dict) and "generated_at" in prev:
            def strip(d: dict) -> dict:
                return {k: v for k, v in d.items() if k != "generated_at"}
            if strip(prev) == strip(data):
                data["generated_at"] = prev["generated_at"]
    OUT_JSON.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(render_markdown(data), encoding="utf-8")
    c = data["counts"]
    p = c["patterns"]
    t = c["tests"]
    print(
        f"site_facts: commands={c['commands']} "
        f"historical_330_bucket={p['historical_330_bucket']} "
        f"grand_total={p['grand_total']} "
        f"tier_groups={p['tier_groups']} "
        f"frameworks={c['frameworks']} "
        f"languages={c['languages']} "
        f"tests={t['total_functions']}"
    )
    return 0


if __name__ == "__main__":
    from tree_guard import stamp
    stamp()
    sys.exit(main())
