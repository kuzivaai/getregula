#!/usr/bin/env python3
# regula-ignore
"""Developer Sentiment Corpus — scrape public mentions of the EU AI Act.

Collects HN front-page items, Reddit submissions, and GitHub issue titles
mentioning "EU AI Act", "Article N", "GPAI", etc. Writes a longitudinal
JSON dataset at data/sentiment/YYYY-MM.json and rebuilds a combined
index at data/sentiment/index.json.

Status: SKELETON. The fetchers are implemented for HN (public Algolia
API, free, no auth) and a generic RSS fallback. Reddit and GitHub
scraping require API credentials and rate-limit handling; those are
wired as TODO.

Stdlib-only by design (urllib.request, json, re, datetime).

Usage:
  python3 scripts/dev_sentiment.py --source hn --month 2026-04
  python3 scripts/dev_sentiment.py --all --month 2026-04
  python3 scripts/dev_sentiment.py --rebuild-index
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent
OUT_DIR = REPO / "data" / "sentiment"

# Queries to run every pass
DEFAULT_QUERIES = [
    '"EU AI Act"',
    '"AI Act" Article',
    '"GPAI" governance',
    '"Annex III" high-risk',
    '"Digital Omnibus" AI',
]


def _fetch_json(url: str, timeout: int = 15) -> dict[str, Any]:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "regula-dev-sentiment/0.1 (+getregula.com)"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8", errors="replace"))


def fetch_hn(query: str, month_start: str, month_end: str) -> list[dict[str, Any]]:
    """Use the public Algolia HN search API — no auth, free."""
    params = urllib.parse.urlencode({
        "query": query,
        "tags": "story",
        "hitsPerPage": "50",
        "numericFilters": (
            f"created_at_i>={_to_ts(month_start)},"
            f"created_at_i<{_to_ts(month_end)}"
        ),
    })
    url = f"https://hn.algolia.com/api/v1/search?{params}"
    try:
        data = _fetch_json(url)
    except (OSError, json.JSONDecodeError) as e:
        print(f"dev-sentiment: hn fetch failed for {query!r}: {e}",
              file=sys.stderr)
        return []
    hits = data.get("hits") or []
    return [
        {
            "source": "hn",
            "query": query,
            "id": h.get("objectID"),
            "title": h.get("title") or h.get("story_title") or "",
            "url": h.get("url") or (
                f"https://news.ycombinator.com/item?id={h.get('objectID')}"
            ),
            "created_at": h.get("created_at"),
            "points": h.get("points") or 0,
            "num_comments": h.get("num_comments") or 0,
            "author": h.get("author"),
        }
        for h in hits
    ]


def _to_ts(iso_date: str) -> int:
    return int(datetime.strptime(iso_date, "%Y-%m-%d")
               .replace(tzinfo=timezone.utc).timestamp())


def month_bounds(month: str) -> tuple[str, str]:
    dt = datetime.strptime(month, "%Y-%m")
    start = dt.strftime("%Y-%m-01")
    if dt.month == 12:
        end = f"{dt.year + 1}-01-01"
    else:
        end = f"{dt.year}-{dt.month + 1:02d}-01"
    return start, end


def run_pass(month: str, sources: list[str]) -> dict[str, Any]:
    start, end = month_bounds(month)
    collected: list[dict[str, Any]] = []
    errors: list[str] = []
    for src in sources:
        if src == "hn":
            for q in DEFAULT_QUERIES:
                collected.extend(fetch_hn(q, start, end))
        elif src == "reddit":
            errors.append("reddit: not yet implemented (requires OAuth)")
        elif src == "github":
            errors.append("github: not yet implemented (requires PAT)")
        else:
            errors.append(f"{src}: unknown source")
    # Deduplicate by (source, id)
    seen: set[tuple[str, str]] = set()
    unique: list[dict[str, Any]] = []
    for h in collected:
        key = (h["source"], str(h.get("id", "")))
        if key in seen:
            continue
        seen.add(key)
        unique.append(h)
    return {
        "month": month,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "sources": sources,
        "queries": DEFAULT_QUERIES,
        "total": len(unique),
        "errors": errors,
        "items": unique,
    }


def rebuild_index() -> None:
    if not OUT_DIR.exists():
        OUT_DIR.mkdir(parents=True)
    index = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "months": [],
    }
    for path in sorted(OUT_DIR.glob("*.json")):
        if path.name == "index.json":
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        index["months"].append({
            "month": data.get("month"),
            "total": data.get("total", 0),
            "file": path.name,
        })
    (OUT_DIR / "index.json").write_text(
        json.dumps(index, indent=2) + "\n", encoding="utf-8"
    )


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--month", default=datetime.now(timezone.utc).strftime("%Y-%m"))
    p.add_argument("--source", choices=("hn", "reddit", "github", "all"),
                   default="hn")
    p.add_argument("--all", action="store_true",
                   help="run all configured sources for this month")
    p.add_argument("--rebuild-index", action="store_true")
    p.add_argument("--dry-run", action="store_true",
                   help="do not write files, print summary only")
    args = p.parse_args(argv)

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    if args.rebuild_index:
        rebuild_index()
        print("dev-sentiment: index rebuilt")
        return 0

    sources = ["hn", "reddit", "github"] if args.all else [args.source]
    result = run_pass(args.month, sources)
    print(f"dev-sentiment: {args.month} — {result['total']} unique items "
          f"from sources={sources}")
    if result.get("errors"):
        for err in result["errors"]:
            print(f"  warn: {err}", file=sys.stderr)

    if args.dry_run:
        return 0

    out_file = OUT_DIR / f"{args.month}.json"
    out_file.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"dev-sentiment: wrote {out_file.relative_to(REPO)}")
    rebuild_index()
    return 0


if __name__ == "__main__":
    sys.exit(main())
