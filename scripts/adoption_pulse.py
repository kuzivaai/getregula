#!/usr/bin/env python3
# regula-ignore
"""
Regula adoption pulse — passive signals from PyPI and GitHub.

Polls public APIs (no authentication required) and appends a
timestamped snapshot to ~/.regula/adoption.json. Run weekly via
cron or manually: python3 scripts/adoption_pulse.py

No code changes needed in Regula core. No telemetry. No user data.
"""

import argparse
import json
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from constants import VERSION

# --- endpoints (all public, no auth required) ---
PYPI_STATS_URL = "https://pypistats.org/api/packages/regula-ai/recent"
GITHUB_REPO_URL = "https://api.github.com/repos/kuzivaai/getregula"
PYPI_PKG_URL = "https://pypi.org/pypi/regula-ai/json"

ADOPTION_FILE = Path.home() / ".regula" / "adoption.json"
REQUEST_TIMEOUT = 15  # seconds


def _get_json(url):
    """Fetch JSON from a URL. Returns parsed dict or None on failure."""
    req = urllib.request.Request(url, headers={"User-Agent": "regula-adoption-pulse"})
    try:
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, OSError, ValueError) as exc:
        print(f"  warning: {url} — {exc}", file=sys.stderr)
        return None


def fetch_pypi_downloads():
    """Return dict with last_day, last_week, last_month download counts."""
    data = _get_json(PYPI_STATS_URL)
    if data and "data" in data:
        recent = data["data"]
        return {
            "downloads_last_day": recent.get("last_day", 0),
            "downloads_last_week": recent.get("last_week", 0),
            "downloads_last_month": recent.get("last_month", 0),
        }
    return None


def fetch_pypi_version():
    """Return current published version string from PyPI."""
    data = _get_json(PYPI_PKG_URL)
    if data and "info" in data:
        return data["info"].get("version")
    return None


def fetch_github_stats():
    """Return dict with stars, forks, open_issues, watchers."""
    data = _get_json(GITHUB_REPO_URL)
    if data and "stargazers_count" in data:
        return {
            "stars": data.get("stargazers_count", 0),
            "forks": data.get("forks_count", 0),
            "open_issues": data.get("open_issues_count", 0),
            "watchers": data.get("subscribers_count", 0),
        }
    return None


def build_snapshot():
    """Fetch all sources and build a timestamped snapshot record."""
    ts = datetime.now(timezone.utc).isoformat()

    pypi_dl = fetch_pypi_downloads()
    pypi_ver = fetch_pypi_version()
    github = fetch_github_stats()

    snapshot = {"ts": ts}

    if pypi_dl is not None or pypi_ver is not None:
        snapshot["pypi"] = {}
        if pypi_dl:
            snapshot["pypi"].update(pypi_dl)
        if pypi_ver:
            snapshot["pypi"]["current_version"] = pypi_ver

    if github is not None:
        snapshot["github"] = github

    return snapshot


def save_snapshot(snapshot):
    """Append snapshot to ~/.regula/adoption.json (create if missing)."""
    ADOPTION_FILE.parent.mkdir(parents=True, exist_ok=True)

    history = []
    if ADOPTION_FILE.exists():
        try:
            history = json.loads(ADOPTION_FILE.read_text(encoding="utf-8"))
            if not isinstance(history, list):
                history = [history]
        except (json.JSONDecodeError, ValueError):
            # Corrupted file — start fresh but warn
            print("  warning: existing adoption.json was corrupted, starting fresh", file=sys.stderr)
            history = []

    history.append(snapshot)
    ADOPTION_FILE.write_text(json.dumps(history, indent=2) + "\n", encoding="utf-8")


def print_snapshot(snapshot):
    """Print a human-readable summary to stdout."""
    print(f"Regula adoption pulse — {snapshot['ts']}")
    print()

    pypi = snapshot.get("pypi", {})
    if pypi:
        print("  PyPI (regula-ai):")
        if "downloads_last_day" in pypi:
            print(f"    Downloads last day:   {pypi['downloads_last_day']:,}")
        if "downloads_last_week" in pypi:
            print(f"    Downloads last week:  {pypi['downloads_last_week']:,}")
        if "downloads_last_month" in pypi:
            print(f"    Downloads last month: {pypi['downloads_last_month']:,}")
        if "current_version" in pypi:
            print(f"    Published version:    {pypi['current_version']}")
    else:
        print("  PyPI: unavailable")

    print()

    gh = snapshot.get("github", {})
    if gh:
        print("  GitHub (kuzivaai/getregula):")
        print(f"    Stars:        {gh.get('stars', '?')}")
        print(f"    Forks:        {gh.get('forks', '?')}")
        print(f"    Open issues:  {gh.get('open_issues', '?')}")
        print(f"    Watchers:     {gh.get('watchers', '?')}")
    else:
        print("  GitHub: unavailable")

    print()
    print(f"  Local version: {VERSION}")
    print(f"  Saved to: {ADOPTION_FILE}")


def show_last_snapshot():
    """Show the most recent saved snapshot, or a message if none exists."""
    if not ADOPTION_FILE.exists():
        print("No adoption data yet. Run without --show to fetch.")
        return

    try:
        history = json.loads(ADOPTION_FILE.read_text(encoding="utf-8"))
        if isinstance(history, list) and history:
            print_snapshot(history[-1])
        else:
            print("No snapshots found in adoption.json.")
    except (json.JSONDecodeError, ValueError):
        print("adoption.json is corrupted. Run without --show to fetch fresh data.")


def main():
    parser = argparse.ArgumentParser(
        description="Regula adoption pulse — passive PyPI + GitHub signals"
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="Show the last saved snapshot instead of fetching new data",
    )
    args = parser.parse_args()

    if args.show:
        show_last_snapshot()
        return

    snapshot = build_snapshot()
    save_snapshot(snapshot)
    print_snapshot(snapshot)


if __name__ == "__main__":
    main()
