#!/usr/bin/env python3
# regula-ignore
"""Duplicate and near-duplicate detection across labelled corpus findings.

PrimeVul (ICSE 2025, arXiv:2403.18624) showed that duplication between
benchmark entries inflates reported scores; the corpus upgrade adopts its
"label accuracy + de-duplication + temporal split" triad. This tool covers
the de-duplication leg at the level the stored labels support:

- EXACT duplicates: identical (project, file, line) keys appearing more
  than once across label files.
- INTRA-PROJECT clusters: same project + same pattern description on
  many lines (one vendored utility triggering repeatedly should not count
  as N independent corpus items).
- CROSS-PROJECT candidates: identical (tier, description, indicators)
  tuples in different projects — the available proxy for copied code.

LIMITATION (stated, not hidden): snippet-level near-duplicate detection
needs the code text, which label files deliberately do not carry. Run
benchmarks/rescan_corpus.py to materialise code context, then extend this
check with normalised-snippet hashing. Until then, cross-project findings
here are CANDIDATES for human review, not verdicts.

Usage:
    python3 benchmarks/dedup_check.py FILE [FILE ...]
    python3 benchmarks/dedup_check.py benchmarks/labels.json \
        benchmarks/results/random_corpus/BLIND_LABELS.json
"""

import json
import sys
from collections import defaultdict
from pathlib import Path


def load_entries(path: Path) -> list:
    data = json.load(Path(path).open())
    entries = data if isinstance(data, list) else data.get(
        "labels", data.get("candidates", []))
    for e in entries:
        e["_source_file"] = str(path)
    return entries


def exact_key(e: dict) -> tuple:
    return (e.get("project"), e.get("file"), e.get("line"))


def content_key(e: dict) -> tuple:
    indicators = e.get("indicators")
    if isinstance(indicators, list):
        indicators = tuple(sorted(map(str, indicators)))
    return (e.get("tier"), e.get("description"), indicators)


def analyse(entries: list) -> dict:
    exact = defaultdict(list)
    intra = defaultdict(list)
    cross = defaultdict(set)
    for e in entries:
        exact[exact_key(e)].append(e)
        intra[(e.get("project"), e.get("description"))].append(e)
        cross[content_key(e)].add(e.get("project"))

    exact_dups = {k: v for k, v in exact.items() if len(v) > 1}
    intra_clusters = {k: v for k, v in intra.items() if len(v) >= 5}
    cross_candidates = {k: sorted(p for p in v if p)
                        for k, v in cross.items()
                        if len({p for p in v if p}) > 1}
    return {
        "total_entries": len(entries),
        "exact_duplicates": {
            "count": len(exact_dups),
            "keys": [list(map(str, k)) for k in sorted(exact_dups,
                                                       key=str)][:50],
        },
        "intra_project_clusters_5plus": {
            "count": len(intra_clusters),
            "clusters": [
                {"project": k[0], "description": (k[1] or "")[:80],
                 "n": len(v)}
                for k, v in sorted(intra_clusters.items(),
                                   key=lambda kv: -len(kv[1]))
            ][:25],
        },
        "cross_project_candidates": {
            "count": len(cross_candidates),
            "note": ("candidates for human review only; snippet-level "
                     "confirmation requires rescan (see module docstring)"),
            "items": [
                {"tier": k[0], "description": (k[1] or "")[:80],
                 "projects": v}
                for k, v in sorted(cross_candidates.items(),
                                   key=lambda kv: -len(kv[1]))
            ][:25],
        },
    }


def main() -> int:
    paths = sys.argv[1:]
    if not paths:
        print(__doc__)
        return 2
    entries = []
    for p in paths:
        entries.extend(load_entries(Path(p)))
    print(json.dumps(analyse(entries), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
