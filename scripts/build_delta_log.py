#!/usr/bin/env python3
# regula-ignore
"""Build delta-log index, RSS feed, and Markdown summary from JSON entries.

Reads content/regulations/delta-log/entries/*.json, validates each against
schema.json (structurally — stdlib-only, no jsonschema dependency),
produces:
  - content/regulations/delta-log/index.json   machine-readable manifest
  - content/regulations/delta-log/feed.xml     RSS 2.0
  - content/regulations/delta-log/SUMMARY.md   human-readable timeline

Usage:
  python3 scripts/build_delta_log.py              # build all outputs
  python3 scripts/build_delta_log.py --validate   # validate only, exit 1 on error

Exit codes: 0 = success, 1 = validation failure, 2 = internal error.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from email.utils import format_datetime
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent
LOG_DIR = REPO / "content" / "regulations" / "delta-log"
ENTRIES_DIR = LOG_DIR / "entries"
INDEX_PATH = LOG_DIR / "index.json"
FEED_PATH = LOG_DIR / "feed.xml"
SUMMARY_PATH = LOG_DIR / "SUMMARY.md"
SITE_URL = "https://getregula.com"

REQUIRED_FIELDS = {
    "id", "date", "type", "source_url", "source_title",
    "affected_articles", "summary", "confidence",
}
VALID_TYPES = {
    "regulation-adoption", "amendment-proposal", "council-position",
    "parliament-position", "trilogue-outcome", "commission-guidance",
    "delegated-act", "implementing-act", "national-transposition",
    "harmonised-standard", "enforcement-action", "court-ruling",
    "notified-body-decision",
}
VALID_CONFIDENCE = {
    "verified-primary", "verified-secondary",
    "reported-unverified", "speculative",
}


def load_entries() -> list[dict[str, Any]]:
    if not ENTRIES_DIR.exists():
        return []
    entries: list[dict[str, Any]] = []
    for path in sorted(ENTRIES_DIR.glob("*.json")):
        try:
            entries.append(json.loads(path.read_text(encoding="utf-8")))
        except json.JSONDecodeError as e:
            raise SystemExit(f"delta-log: invalid JSON in {path.name}: {e}")
    return entries


def validate(entries: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    ids_seen: set[str] = set()
    for e in entries:
        where = e.get("id") or "<no id>"
        missing = REQUIRED_FIELDS - e.keys()
        if missing:
            errors.append(f"{where}: missing fields {sorted(missing)}")
        if e.get("id") in ids_seen:
            errors.append(f"{where}: duplicate id")
        ids_seen.add(e.get("id", ""))
        if e.get("type") not in VALID_TYPES:
            errors.append(f"{where}: invalid type {e.get('type')!r}")
        if e.get("confidence") not in VALID_CONFIDENCE:
            errors.append(f"{where}: invalid confidence {e.get('confidence')!r}")
        if not isinstance(e.get("affected_articles"), list) or not e["affected_articles"]:
            errors.append(f"{where}: affected_articles must be a non-empty list")
        try:
            datetime.strptime(e.get("date", ""), "%Y-%m-%d")
        except ValueError:
            errors.append(f"{where}: invalid date {e.get('date')!r} (expected YYYY-MM-DD)")
    return errors


def build_index(entries: list[dict[str, Any]]) -> dict[str, Any]:
    by_date = sorted(entries, key=lambda e: e["date"], reverse=True)
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_entries": len(entries),
        "latest_date": by_date[0]["date"] if by_date else None,
        "types": sorted({e["type"] for e in entries}),
        "entries": [
            {
                "id": e["id"],
                "date": e["date"],
                "type": e["type"],
                "affected_articles": e["affected_articles"],
                "summary": e["summary"][:200],
                "confidence": e["confidence"],
                "source_url": e["source_url"],
                "file": f"entries/{e['id']}.json",
            }
            for e in by_date
        ],
    }


def _xml_escape(s: str) -> str:
    return (
        s.replace("&", "&amp;")
         .replace("<", "&lt;")
         .replace(">", "&gt;")
         .replace('"', "&quot;")
         .replace("'", "&apos;")
    )


def build_rss(entries: list[dict[str, Any]]) -> str:
    by_date = sorted(entries, key=lambda e: e["date"], reverse=True)
    now = format_datetime(datetime.now(timezone.utc))
    items: list[str] = []
    for e in by_date:
        pub = datetime.strptime(e["date"], "%Y-%m-%d").replace(tzinfo=timezone.utc)
        articles = ", ".join(
            f"Art. {a}" if a != "*" else "all articles"
            for a in e["affected_articles"]
        )
        title = f"[{e['type']}] {articles}: {e['source_title'][:80]}"
        link = e["source_url"]
        guid = f"{SITE_URL}/content/regulations/delta-log/entries/{e['id']}.json"
        desc = f"{e['summary']} (confidence: {e['confidence']})"
        items.append(
            "    <item>\n"
            f"      <title>{_xml_escape(title)}</title>\n"
            f"      <link>{_xml_escape(link)}</link>\n"
            f"      <guid isPermaLink=\"false\">{_xml_escape(guid)}</guid>\n"
            f"      <pubDate>{format_datetime(pub)}</pubDate>\n"
            f"      <description>{_xml_escape(desc)}</description>\n"
            "    </item>"
        )
    return (
        "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
        "<rss version=\"2.0\">\n"
        "  <channel>\n"
        "    <title>Regula — EU AI Act Regulatory Delta Log</title>\n"
        f"    <link>{SITE_URL}/content/regulations/delta-log/</link>\n"
        "    <description>Primary-source-linked changelog for the EU AI Act. "
        "Every entry is article-keyed and machine-readable.</description>\n"
        "    <language>en-GB</language>\n"
        f"    <lastBuildDate>{now}</lastBuildDate>\n"
        + "\n".join(items) + "\n"
        "  </channel>\n"
        "</rss>\n"
    )


def build_summary(entries: list[dict[str, Any]]) -> str:
    by_date = sorted(entries, key=lambda e: e["date"], reverse=True)
    lines = [
        "# EU AI Act — Delta Log Summary",
        "",
        "*Auto-generated by `scripts/build_delta_log.py`. Do not edit by hand.*",
        "",
        f"Total entries: **{len(entries)}** · "
        f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        "| Date | Type | Articles | Summary | Confidence |",
        "|---|---|---|---|---|",
    ]
    for e in by_date:
        arts = ", ".join(e["affected_articles"])
        conf = e["confidence"].replace("-", " ")
        summary_short = e["summary"][:120].replace("|", "\\|")
        lines.append(
            f"| {e['date']} | `{e['type']}` | {arts} | [{summary_short}]({e['source_url']}) | {conf} |"
        )
    lines.append("")
    lines.append("## Sources")
    lines.append("")
    for e in by_date:
        lines.append(f"- [{e['source_title']}]({e['source_url']}) — `{e['id']}`")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--validate", action="store_true",
                   help="validate only, do not write outputs")
    args = p.parse_args(argv)

    entries = load_entries()
    errors = validate(entries)
    if errors:
        print("delta-log: validation errors:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1
    if args.validate:
        print(f"delta-log: {len(entries)} entries OK")
        return 0

    index = build_index(entries)
    rss = build_rss(entries)
    summary = build_summary(entries)

    INDEX_PATH.write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
    FEED_PATH.write_text(rss, encoding="utf-8")
    SUMMARY_PATH.write_text(summary, encoding="utf-8")

    print(f"delta-log: wrote {INDEX_PATH.relative_to(REPO)}")
    print(f"delta-log: wrote {FEED_PATH.relative_to(REPO)}")
    print(f"delta-log: wrote {SUMMARY_PATH.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
