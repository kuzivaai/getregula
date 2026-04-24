#!/usr/bin/env python3
"""Submit URLs to search engines via IndexNow protocol.

Usage:
    python3 scripts/indexnow.py https://getregula.com/blog/blog-article-5.html
    python3 scripts/indexnow.py --all-blogs
    python3 scripts/indexnow.py --sitemap

Requires the key file to be deployed to the live site first.
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path

SITE_DIR = Path(__file__).resolve().parent.parent / "site"
KEY = os.environ.get("INDEXNOW_KEY", "")
HOST = "getregula.com"
INDEXNOW_ENDPOINTS = [
    "https://api.indexnow.org/indexnow",
    "https://www.bing.com/indexnow",
    "https://yandex.com/indexnow",
]


def submit_urls(urls: list[str]) -> dict:
    """Submit URLs to all IndexNow endpoints. Returns {endpoint: status}."""
    payload = json.dumps({
        "host": HOST,
        "key": KEY,
        "urlList": urls,
    }).encode()

    results = {}
    for endpoint in INDEXNOW_ENDPOINTS:
        try:
            req = urllib.request.Request(
                endpoint,
                data=payload,
                headers={"Content-Type": "application/json; charset=utf-8"},
                method="POST",
            )
            resp = urllib.request.urlopen(req, timeout=15)
            results[endpoint] = f"OK ({resp.status})"
        except urllib.error.HTTPError as e:
            results[endpoint] = f"HTTP {e.code}"
        except urllib.error.URLError as e:
            results[endpoint] = f"Error: {e.reason}"
    return results


def get_blog_urls() -> list[str]:
    """Get all blog URLs from the blog directory."""
    urls = []
    for f in sorted(SITE_DIR.glob("blog/blog-*.html")):
        urls.append(f"https://{HOST}/blog/{f.name}")
    return urls


def get_sitemap_urls() -> list[str]:
    """Parse sitemap.xml for all URLs."""
    import xml.etree.ElementTree as ET
    sitemap = SITE_DIR / "sitemap.xml"
    tree = ET.parse(sitemap)
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    return [loc.text for loc in tree.findall(".//sm:loc", ns)]


def main():
    parser = argparse.ArgumentParser(description="Submit URLs via IndexNow")
    parser.add_argument("urls", nargs="*", help="URLs to submit")
    parser.add_argument("--all-blogs", action="store_true", help="Submit all blog URLs")
    parser.add_argument("--sitemap", action="store_true", help="Submit all sitemap URLs")
    parser.add_argument("--dry-run", action="store_true", help="Print URLs without submitting")
    args = parser.parse_args()

    urls = list(args.urls)
    if args.all_blogs:
        urls.extend(get_blog_urls())
    if args.sitemap:
        urls.extend(get_sitemap_urls())

    if not urls:
        print("No URLs to submit. Provide URLs as arguments or use --all-blogs/--sitemap.", file=sys.stderr)
        sys.exit(1)

    if not KEY:
        print("INDEXNOW_KEY environment variable not set.", file=sys.stderr)
        sys.exit(1)

    urls = list(dict.fromkeys(urls))  # dedupe preserving order
    print(f"Submitting {len(urls)} URL(s):")
    for u in urls:
        print(f"  {u}")

    if args.dry_run:
        print("\n(dry run — no submissions made)")
        return

    print()
    results = submit_urls(urls)
    for endpoint, status in results.items():
        print(f"  {endpoint}: {status}")


if __name__ == "__main__":
    main()
