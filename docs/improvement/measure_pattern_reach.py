#!/usr/bin/env python3
# regula-ignore
"""Measure how much of the detection surface any test input actually reaches.

Phase 1 instrument. Compiles every tier regex and searches it against the
concatenated text of every file the test suite can feed the engine. A
regex that matches nothing in that corpus is UNGUARDED: it may work
perfectly today (many do), but no test would notice if it stopped.

This is a measurement tool, not a gate. The Phase 4 fix is a generated
table-driven test with positive and near-miss fixtures per pattern; this
script produces the worklist for it and lets the figure be re-measured
rather than trusted.

Usage:
    python3 docs/improvement/measure_pattern_reach.py
    python3 docs/improvement/measure_pattern_reach.py --json OUT.json
"""

import json
import os
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

TIER_VARS = [
    "PROHIBITED_PATTERNS",
    "HIGH_RISK_PATTERNS",
    "LIMITED_RISK_PATTERNS",
    "AI_SECURITY_PATTERNS",
    "BIAS_RISK_PATTERNS",
]

CORPUS_ROOTS = ["tests", "benchmarks/synthetic/fixtures"]
CORPUS_SUFFIXES = (".py", ".js", ".ts", ".java", ".go", ".rs", ".c",
                   ".cpp", ".txt", ".json")


def collect_groups() -> dict:
    import risk_patterns as rp
    groups = {}
    for var in TIER_VARS:
        for gname, val in getattr(rp, var, {}).items():
            pats = val.get("patterns") if isinstance(val, dict) else val
            if isinstance(pats, list):
                groups[f"{var}:{gname}"] = pats
    return groups


def collect_corpus() -> tuple:
    texts, count = [], 0
    for root in CORPUS_ROOTS:
        for dirpath, dirnames, filenames in os.walk(ROOT / root):
            dirnames[:] = [d for d in dirnames
                           if d not in ("__pycache__", ".git")]
            for fn in filenames:
                if fn.endswith(CORPUS_SUFFIXES):
                    try:
                        texts.append(Path(dirpath, fn).read_text(
                            encoding="utf-8", errors="ignore"))
                        count += 1
                    except OSError:
                        pass
    return "\n".join(texts), count


def main() -> int:
    groups = collect_groups()
    blob, n_files = collect_corpus()
    total = sum(len(v) for v in groups.values())

    never, uncompilable = [], []
    for gname, pats in groups.items():
        for p in pats:
            try:
                rx = re.compile(p, re.I)
            except re.error as exc:
                uncompilable.append({"group": gname, "pattern": p,
                                     "error": str(exc)})
                continue
            if not rx.search(blob):
                never.append({"group": gname, "pattern": p})

    pct = (100.0 * len(never) / total) if total else 0.0
    print(f"test corpus:            {n_files} files, {len(blob):,} chars")
    print(f"total tier regexes:     {total}")
    print(f"fail to compile:        {len(uncompilable)}")
    print(f"unguarded (no match):   {len(never)} ({pct:.1f}%)")
    by_var = Counter(g["group"].split(":")[0] for g in never)
    print("\nunguarded by tier variable:")
    for k, v in by_var.most_common():
        print(f"  {k}: {v}")

    if "--json" in sys.argv:
        out = sys.argv[sys.argv.index("--json") + 1]
        Path(out).write_text(json.dumps({
            "total_regexes": total,
            "corpus_files": n_files,
            "unguarded_count": len(never),
            "unguarded_pct": round(pct, 1),
            "uncompilable": uncompilable,
            "unguarded": never,
        }, indent=2) + "\n", encoding="utf-8")
        print(f"\nwrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
