# regula-ignore
#!/usr/bin/env python3
"""
Regula Governance Feed — AI Governance News Aggregator

Fetches AI governance news from curated, reputable sources via RSS/Atom feeds.
No external dependencies — uses stdlib urllib and xml.etree only.

Sources are selected for: institutional authority, editorial independence,
and relevance to AI governance practitioners. Vendor marketing blogs are
excluded. Each source is verified to publish structured feeds.
"""

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone, timedelta
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from typing import Optional
from urllib.error import URLError
from urllib.request import Request, urlopen
from xml.etree import ElementTree


# ---------------------------------------------------------------------------
# Curated sources — verified reputable, verified to have RSS/Atom feeds
# ---------------------------------------------------------------------------

FEED_SOURCES = [
    {
        "name": "IAPP News",
        "url": "https://iapp.org/rss/news.xml",
        "type": "rss",
        "authority": "International Association of Privacy Professionals — industry standard body for privacy and AI governance professionals. 670+ professional survey base.",
    },
    {
        "name": "NIST AI Publications",
        "url": "https://www.nist.gov/blogs/cybersecurity-insights/rss.xml",
        "type": "rss",
        "authority": "US National Institute of Standards and Technology — federal standards body. Publishes AI RMF, AI 600-1 (GenAI Profile), and cybersecurity frameworks.",
    },
    {
        "name": "EU AI Act Updates",
        "url": "https://artificialintelligenceact.eu/feed/",
        "type": "rss",
        "authority": "Most comprehensive independent EU AI Act reference site. Tracks implementation timeline, article text, and standard-setting progress.",
    },
    {
        "name": "MIT Technology Review",
        "url": "https://www.technologyreview.com/feed/",
        "type": "rss",
        "authority": "MIT Technology Review — independent journalism on technology policy. Covers AI governance, regulation, and societal impact with editorial independence.",
    },
    {
        "name": "Future of Life Institute",
        "url": "https://futureoflife.org/feed/",
        "type": "rss",
        "authority": "Future of Life Institute — non-profit focused on existential risk from AI. Publishes AI governance policy analysis and coordinates open letters.",
    },
    {
        "name": "Help Net Security",
        "url": "https://www.helpnetsecurity.com/feed/",
        "type": "rss",
        "authority": "Independent cybersecurity news outlet. Covers AI security and governance tools with editorial independence from vendors.",
    },
    {
        "name": "EFF AI Policy",
        "url": "https://www.eff.org/rss/updates.xml",
        "type": "rss",
        "authority": "Electronic Frontier Foundation — non-profit defending civil liberties in digital spaces. Covers AI regulation, surveillance, and rights implications.",
    },
]

# Keywords for filtering — articles must contain at least one
GOVERNANCE_KEYWORDS = [
    # Regulatory
    "ai act", "ai governance", "ai regulation", "ai compliance", "ai risk",
    "eu ai act", "ai audit", "ai oversight", "ai policy", "high-risk ai",
    "prohibited ai", "conformity assessment", "iso 42001", "nist ai rmf",
    "artificial intelligence act", "digital omnibus", "harmonised standard",
    "annex iii", "annex iv", "annex viii", "article 5", "article 6", "article 9",
    "article 43", "article 49", "article 53", "article 55",
    "gpai code of practice", "jtc 21", "cen-cenelec",
    "colorado ai act", "south korea ai basic act", "korea ai act",
    # Governance concepts
    "ai safety", "ai ethics", "responsible ai", "ai transparency",
    "ai accountability", "model governance", "ai assurance", "trustworthy ai",
    "ai certification", "ai framework", "bias detection", "fairness",
    "ai bill of materials", "ai-bom", "agentic ai", "ai agent",
    "shadow ai", "ai standard", "automated decision",
    # Broader AI policy (widens match for MIT Tech Review, HelpNetSec, EFF)
    "artificial intelligence regulation", "ai legislation", "ai law",
    "machine learning governance", "deepfake", "facial recognition",
    "surveillance", "algorithmic bias", "algorithmic accountability",
    "ai security", "ai vulnerability", "prompt injection",
    "ai copyright", "training data", "generative ai regulation",
    "foundation model", "large language model", "llm governance",
    "ai workforce", "ai hiring", "ai discrimination",
]

CACHE_DIR = Path(os.environ.get("REGULA_CACHE_DIR", Path.home() / ".regula" / "cache"))
CACHE_FILE = CACHE_DIR / "feed_cache.json"
CACHE_MAX_AGE_HOURS = 2


# ---------------------------------------------------------------------------
# HTML tag stripper
# ---------------------------------------------------------------------------

class _HTMLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self._text = []

    def handle_data(self, data):
        self._text.append(data)

    def get_text(self):
        return " ".join(self._text)


def strip_html(html_text: str) -> str:
    if not html_text:
        return ""
    stripper = _HTMLStripper()
    try:
        stripper.feed(unescape(html_text))
        return stripper.get_text().strip()
    except Exception:
        return re.sub(r"<[^>]+>", "", unescape(html_text)).strip()


# ---------------------------------------------------------------------------
# Feed fetching and parsing
# ---------------------------------------------------------------------------

def _fetch_url(url: str, timeout: int = 15) -> Optional[bytes]:
    """Fetch URL content with timeout and user-agent."""
    try:
        req = Request(url, headers={
            "User-Agent": "Regula/1.0 (+https://github.com/kuzivaai/getregula)",
            "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml",
        })
        with urlopen(req, timeout=timeout) as resp:
            return resp.read()
    except (URLError, OSError, TimeoutError):
        return None


def _parse_date(date_str: str) -> Optional[datetime]:
    """Parse common RSS/Atom date formats."""
    if not date_str:
        return None
    # Try common formats
    formats = [
        "%a, %d %b %Y %H:%M:%S %z",       # RFC 822 (RSS)
        "%a, %d %b %Y %H:%M:%S %Z",
        "%Y-%m-%dT%H:%M:%S%z",             # ISO 8601 (Atom)
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
    ]
    date_str = date_str.strip()
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            continue
    return None


def _parse_feed(xml_bytes: bytes, source_name: str) -> list:
    """Parse RSS or Atom feed XML into article dicts."""
    articles = []
    try:
        root = ElementTree.fromstring(xml_bytes)
    except ElementTree.ParseError:
        return []

    # Detect feed type and extract items
    ns = {"atom": "http://www.w3.org/2005/Atom"}

    # RSS 2.0
    for item in root.iter("item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        description = strip_html(item.findtext("description") or "")
        pub_date = _parse_date(item.findtext("pubDate") or "")
        if title and link:
            articles.append({
                "title": title,
                "link": link,
                "description": description[:300],
                "date": pub_date.isoformat() if pub_date else None,
                "source": source_name,
            })

    # Atom
    for entry in root.iter("{http://www.w3.org/2005/Atom}entry"):
        title = (entry.findtext("{http://www.w3.org/2005/Atom}title") or "").strip()
        link_el = entry.find("{http://www.w3.org/2005/Atom}link")
        link = link_el.get("href", "") if link_el is not None else ""
        summary = strip_html(entry.findtext("{http://www.w3.org/2005/Atom}summary") or
                            entry.findtext("{http://www.w3.org/2005/Atom}content") or "")
        updated = _parse_date(
            entry.findtext("{http://www.w3.org/2005/Atom}published") or
            entry.findtext("{http://www.w3.org/2005/Atom}updated") or ""
        )
        if title and link:
            articles.append({
                "title": title,
                "link": link,
                "description": summary[:300],
                "date": updated.isoformat() if updated else None,
                "source": source_name,
            })

    return articles


def _is_relevant(article: dict) -> bool:
    """Check if article is relevant to AI governance."""
    text = f"{article.get('title', '')} {article.get('description', '')}".lower()
    return any(kw in text for kw in GOVERNANCE_KEYWORDS)


def _dedup_key(title: str) -> str:
    """Generate dedup key from title."""
    cleaned = re.sub(r"[^a-z0-9 ]", "", title.lower())
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return hashlib.md5(cleaned.encode()).hexdigest()


# ---------------------------------------------------------------------------
# Cache management
# ---------------------------------------------------------------------------

def _load_cache() -> dict:
    if CACHE_FILE.exists():
        try:
            data = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
            cached_at = datetime.fromisoformat(data.get("cached_at", "2000-01-01T00:00:00+00:00"))
            age = datetime.now(timezone.utc) - cached_at
            if age < timedelta(hours=CACHE_MAX_AGE_HOURS):
                return data
        except (json.JSONDecodeError, ValueError, KeyError):
            pass
    return {}


def _save_cache(articles: list) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    data = {
        "cached_at": datetime.now(timezone.utc).isoformat(),
        "articles": articles,
    }
    CACHE_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


# ---------------------------------------------------------------------------
# Main fetch logic
# ---------------------------------------------------------------------------

def fetch_governance_news(days: int = 7, use_cache: bool = True) -> list:
    """Fetch and filter AI governance news from all sources."""
    # Try cache first
    if use_cache:
        cache = _load_cache()
        if cache.get("articles"):
            cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
            return [a for a in cache["articles"]
                    if not a.get("date") or a["date"] >= cutoff]

    all_articles = []
    errors = []

    for source in FEED_SOURCES:
        xml_data = _fetch_url(source["url"])
        if xml_data is None:
            errors.append(source["name"])
            continue
        articles = _parse_feed(xml_data, source["name"])
        all_articles.extend(articles)

    if errors:
        print(f"  Warning: Could not reach {len(errors)} source(s): {', '.join(errors)}", file=sys.stderr)

    # Filter for relevance
    relevant = [a for a in all_articles if _is_relevant(a)]

    # Deduplicate
    seen = set()
    unique = []
    for article in relevant:
        key = _dedup_key(article["title"])
        if key not in seen:
            seen.add(key)
            unique.append(article)

    # Sort by date (newest first)
    unique.sort(key=lambda a: a.get("date") or "0000", reverse=True)

    # Filter by days
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    filtered = [a for a in unique if not a.get("date") or a["date"] >= cutoff]

    # Cache results
    _save_cache(unique)

    return filtered


# ---------------------------------------------------------------------------
# Output formatters
# ---------------------------------------------------------------------------

def format_text(articles: list) -> str:
    """Format articles for CLI output."""
    if not articles:
        return "No AI governance articles found for this period.\n"

    lines = [
        "",
        f"  Regula Governance Feed — {len(articles)} articles",
        "  " + "=" * 56,
        "",
    ]

    current_date = None
    for a in articles:
        date_str = a.get("date", "")[:10] if a.get("date") else "Unknown"
        if date_str != current_date:
            current_date = date_str
            lines.append(f"  [{date_str}]")

        lines.append(f"    {a['title']}")
        lines.append(f"    {a['source']} — {a['link']}")
        if a.get("description"):
            desc = a["description"][:120]
            if len(a["description"]) > 120:
                desc += "..."
            lines.append(f"    {desc}")
        lines.append("")

    lines.append(f"  Sources: {', '.join(s['name'] for s in FEED_SOURCES)}")
    lines.append(f"  Filtered by {len(GOVERNANCE_KEYWORDS)} governance keywords")
    lines.append("")
    return "\n".join(lines)


def format_html(articles: list) -> str:
    """Format articles as a single-file HTML digest."""
    from html import escape
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    items_html = ""
    for a in articles:
        date_str = a.get("date", "")[:10] if a.get("date") else ""
        desc = escape(a.get("description", "")[:200])
        items_html += f"""
        <div class="article">
            <div class="article-meta">{escape(a['source'])} — {date_str}</div>
            <div class="article-title"><a href="{escape(a['link'])}">{escape(a['title'])}</a></div>
            <div class="article-desc">{desc}</div>
        </div>"""

    if not articles:
        items_html = '<div class="article"><div class="article-desc">No articles found for this period.</div></div>'

    source_list = ", ".join(s["name"] for s in FEED_SOURCES)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Regula Governance Feed</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, sans-serif; background: #f8f9fa; color: #212529; line-height: 1.6; }}
.container {{ max-width: 800px; margin: 0 auto; padding: 24px; }}
header {{ background: #1a1a2e; color: #fff; padding: 24px 0; margin-bottom: 24px; }}
header .container {{ display: flex; justify-content: space-between; align-items: center; }}
header h1 {{ font-size: 1.3rem; font-weight: 600; }}
header .meta {{ font-size: 0.8rem; opacity: 0.8; }}
.stats {{ background: #fff; padding: 16px 20px; border-radius: 6px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); font-size: 0.85rem; color: #6c757d; }}
.article {{ background: #fff; padding: 16px 20px; border-radius: 6px; margin-bottom: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }}
.article-meta {{ font-size: 0.75rem; color: #6c757d; margin-bottom: 4px; }}
.article-title {{ font-size: 0.95rem; font-weight: 600; margin-bottom: 4px; }}
.article-title a {{ color: #0d6efd; text-decoration: none; }}
.article-title a:hover {{ text-decoration: underline; }}
.article-desc {{ font-size: 0.85rem; color: #495057; }}
footer {{ text-align: center; padding: 24px; font-size: 0.75rem; color: #6c757d; }}
</style>
</head>
<body>
<header>
<div class="container">
<h1>Regula — AI Governance Feed</h1>
<div class="meta">{now}</div>
</div>
</header>
<div class="container">
<div class="stats">{len(articles)} articles from {len(FEED_SOURCES)} sources: {source_list}</div>
{items_html}
</div>
<footer>Generated by Regula v1.0.0 — AI Governance Risk Indication<br>
Sources selected for institutional authority and editorial independence.</footer>
</body>
</html>"""


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="AI governance news feed from curated, reputable sources"
    )
    parser.add_argument("--days", "-d", type=int, default=7, help="Articles from last N days (default: 7)")
    parser.add_argument("--format", "-f", choices=["text", "json", "html"], default="text")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--no-cache", action="store_true", help="Bypass cache, fetch fresh")
    parser.add_argument("--sources", action="store_true", help="List sources and exit")
    args = parser.parse_args()

    if args.sources:
        print("\nRegula Governance Feed — Curated Sources\n")
        for s in FEED_SOURCES:
            print(f"  {s['name']}")
            print(f"    URL: {s['url']}")
            print(f"    Authority: {s['authority']}")
            print()
        return

    articles = fetch_governance_news(days=args.days, use_cache=not args.no_cache)

    if args.format == "json":
        content = json.dumps(articles, indent=2)
    elif args.format == "html":
        content = format_html(articles)
    else:
        content = format_text(articles)

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(content, encoding="utf-8")
        print(f"Feed written to {args.output} ({len(articles)} articles)", file=sys.stderr)
    else:
        print(content)


if __name__ == "__main__":
    main()
