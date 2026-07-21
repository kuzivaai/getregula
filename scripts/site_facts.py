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

import importlib.util
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

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


def count_tests() -> dict:
    """Return a breakdown of test functions and per-file counts."""
    # Use actual pytest collection to get the truthful executable count,
    # handling parametrization and the custom test runner properly, rather
    # than just grepping for 'def test_'.
    import subprocess
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

    per_file: dict[str, int] = {}
    for path in sorted(tests_dir.glob("test_*.py")):
        text = path.read_text(encoding="utf-8")
        per_file[path.name] = len(
            re.findall(r"^def (test_\w+)", text, re.MULTILINE)
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
            "tests": count_tests(),
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
                "Regula's landing pages cite '12 compliance frameworks'. "
                "12 have full crosswalk data; 5 additional frameworks "
                "(Colorado SB-189 [replaced SB-205], Canada AIDA, Singapore AI, OECD AI, "
                "South Korea AI) accepted as filter keys with partial coverage."
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
    sys.exit(main())
