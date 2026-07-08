#!/usr/bin/env python3
# regula-ignore
"""Verify scanner.js pattern data stays in sync with risk_patterns.py.

Compares pattern group counts and category names between the Python source
of truth (risk_patterns.py) and the JS port (scanner.js). Fails if they
diverge, which means scanner.js needs regeneration.

Run: python3 tests/test_pattern_sync.py
"""
from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
RISK_PATTERNS_PY = REPO / "scripts" / "risk_patterns.py"
SCANNER_JS = REPO / "site" / "assess" / "scanner.js"


def load_python_patterns():
    """Load risk_patterns.py and count entries per category."""
    spec = importlib.util.spec_from_file_location(
        "risk_patterns", RISK_PATTERNS_PY
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load risk_patterns.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    counts = {}
    for var_name in [
        "PROHIBITED_PATTERNS", "HIGH_RISK_PATTERNS",
        "LIMITED_RISK_PATTERNS", "AI_SECURITY_PATTERNS",
        "AI_INDICATORS", "GOVERNANCE_OBSERVATIONS",
        "BIAS_RISK_PATTERNS",
    ]:
        obj = getattr(module, var_name, {})
        if isinstance(obj, dict):
            counts[var_name] = len(obj)

    gpai = getattr(module, "GPAI_TRAINING_PATTERNS", [])
    counts["GPAI_TRAINING_PATTERNS"] = len(gpai)

    return counts


def count_js_pattern_groups():
    """Count top-level keys in each pattern const in scanner.js."""
    content = SCANNER_JS.read_text(encoding="utf-8")
    counts = {}

    # Match: const VAR_NAME = { ... };
    # Some dicts have object values (e.g. PROHIBITED_PATTERNS),
    # others have array values (e.g. AI_INDICATORS).
    for var_name in [
        "PROHIBITED_PATTERNS", "HIGH_RISK_PATTERNS",
        "LIMITED_RISK_PATTERNS", "AI_SECURITY_PATTERNS",
        "AI_INDICATORS", "GOVERNANCE_OBSERVATIONS",
        "BIAS_RISK_PATTERNS",
    ]:
        pattern = rf'const\s+{var_name}\s*=\s*\{{(.*?)\n\}};'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            block = match.group(1)
            # Count top-level keys: "key": { or "key": [
            keys = re.findall(
                r'^\s{2}"(\w+)":\s*[\{\[]', block, re.MULTILINE
            )
            counts[var_name] = len(keys)
        else:
            counts[var_name] = 0

    # GPAI_TRAINING_PATTERNS is a list of regex strings
    gpai_match = re.search(
        r'const\s+GPAI_TRAINING_PATTERNS\s*=\s*\[(.*?)\];',
        content, re.DOTALL
    )
    if gpai_match:
        entries = re.findall(r'"[^"]*"', gpai_match.group(1))
        # Filter to actual regex strings (not empty)
        counts["GPAI_TRAINING_PATTERNS"] = len(
            [e for e in entries if len(e) > 2]
        )
    else:
        counts["GPAI_TRAINING_PATTERNS"] = 0

    return counts


def main() -> int:
    py_counts = load_python_patterns()
    js_counts = count_js_pattern_groups()

    print("Pattern sync check: risk_patterns.py vs scanner.js\n")
    print(f"{'Category':<30} {'Python':>8} {'JS':>8} {'Status':>8}")
    print("─" * 58)

    mismatches = []
    for var_name in sorted(set(list(py_counts.keys()) + list(js_counts.keys()))):
        py = py_counts.get(var_name, 0)
        js = js_counts.get(var_name, 0)
        status = "OK" if py == js else "DRIFT"
        print(f"  {var_name:<28} {py:>8} {js:>8} {status:>8}")
        if py != js:
            mismatches.append((var_name, py, js))

    py_total = sum(py_counts.values())
    js_total = sum(js_counts.values())
    print("─" * 58)
    print(f"  {'TOTAL':<28} {py_total:>8} {js_total:>8} "
          f"{'OK' if py_total == js_total else 'DRIFT':>8}")

    if mismatches:
        print(f"\nFAIL: {len(mismatches)} category(ies) out of sync:")
        for var, py, js in mismatches:
            print(f"  {var}: Python has {py}, JS has {js}")
        print("\nTo fix: regenerate scanner.js from risk_patterns.py")
        print("See site/assess/scanner.js header for regeneration steps.")
        return 1

    print("\nPASS: scanner.js is in sync with risk_patterns.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())


# ── pytest entry point ─────────────────────────────────────────────
# Without a test_* function this file silently contributes nothing to
# `python3 -m pytest tests/` — the Python↔scanner.js drift check the
# quality rules require would only run when invoked by hand.

def test_scanner_js_in_sync_with_risk_patterns():
    """site/assess/scanner.js pattern counts must match risk_patterns.py."""
    assert main() == 0, "scanner.js has drifted from risk_patterns.py — see stdout"
