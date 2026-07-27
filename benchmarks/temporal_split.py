#!/usr/bin/env python3
# regula-ignore
"""Chronological (temporal) train/test split for the labelled corpus.

PrimeVul (ICSE 2025) showed random splits leak near-identical code across
train/test; the defensible alternative is a chronological split. For this
corpus the unit is the PROJECT (all findings from one repository stay on
one side of the cutoff), keyed by a per-project date.

DATA REQUIREMENT (stated, not hidden): the random-corpus methodology
(benchmarks/results/random_corpus/METHODOLOGY.json) records only the
corpus-level scan date (2026-04-25), not per-project dates. Before a
temporal split can be published, capture per-project dates at rescan time
(repository created_at and pushed_at from the GitHub API, recorded by
benchmarks/rescan_corpus.py) into a dates manifest:

    {"project": {"created_at": "YYYY-MM-DD", "pushed_at": "YYYY-MM-DD"}}

This tool then produces the split deterministically. Run with --missing to
list projects lacking dates.

Usage:
    python3 benchmarks/temporal_split.py LABELS DATES_MANIFEST CUTOFF
    python3 benchmarks/temporal_split.py benchmarks/labels.json dates.json 2026-01-01
    python3 benchmarks/temporal_split.py LABELS DATES_MANIFEST --missing
"""

import json
import sys
from collections import defaultdict
from pathlib import Path

DATE_FIELD = "created_at"   # split on repository creation by default


def load_entries(path: Path) -> list:
    data = json.load(Path(path).open())
    return data if isinstance(data, list) else data.get(
        "labels", data.get("candidates", []))


def split(entries: list, dates: dict, cutoff: str) -> dict:
    by_project = defaultdict(list)
    for e in entries:
        by_project[e.get("project")].append(e)

    train, test, missing = [], [], []
    for project, items in sorted(by_project.items()):
        info = dates.get(project)
        date = (info or {}).get(DATE_FIELD)
        if not date:
            missing.append(project)
            continue
        (train if date < cutoff else test).extend(items)

    return {
        "cutoff": cutoff,
        "date_field": DATE_FIELD,
        "projects_total": len(by_project),
        "projects_missing_dates": missing,
        "train": {"projects": len({e['project'] for e in train}),
                  "findings": len(train)},
        "test": {"projects": len({e['project'] for e in test}),
                 "findings": len(test)},
        "publishable": not missing,
        "note": (None if not missing else
                 "NOT publishable: capture dates for the missing projects "
                 "first (see module docstring)"),
    }


def main() -> int:
    args = sys.argv[1:]
    if len(args) < 3 and not (len(args) == 3 and args[2] == "--missing"):
        if len(args) != 3:
            print(__doc__)
            return 2
    labels_path, dates_path, third = args[0], args[1], args[2]
    entries = load_entries(Path(labels_path))
    dates = json.loads(Path(dates_path).read_text(encoding="utf-8"))

    if third == "--missing":
        projects = sorted({e.get("project") for e in entries})
        missing = [p for p in projects
                   if not (dates.get(p) or {}).get(DATE_FIELD)]
        print(json.dumps({"projects": len(projects),
                          "missing_dates": missing}, indent=2))
        return 0

    print(json.dumps(split(entries, dates, third), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
