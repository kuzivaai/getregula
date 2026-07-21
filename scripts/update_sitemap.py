#!/usr/bin/env python3
"""Set every sitemap <lastmod> from git history — accuracy or nothing.

Google uses <lastmod> only when it is consistently truthful; a sitemap
whose dates say 10 July while pages changed on the 18th trains crawlers
to ignore the signal entirely (found 19 Jul 2026). This derives each
URL's lastmod from the last commit that touched its source file, so the
value can only be wrong if git is.

Region pages are built artifacts: their real change date is the last
commit touching EITHER the built page or its content/regulations source.

Run after any site change (idempotent):  python3 scripts/update_sitemap.py
"""
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

REPO = Path(__file__).resolve().parent.parent
SITEMAP = REPO / "site" / "sitemap.xml"

# Built pages whose true change date includes their generator source.
SOURCE_MAP = {
    "site/regions/brazil-ai-regulation.html": "content/regulations/brazil.py",
    "site/regions/colorado-ai-regulation.html": "content/regulations/colorado.py",
    "site/regions/south-africa-ai-policy.html": "content/regulations/south-africa.py",
    "site/regions/south-korea-ai-regulation.html": "content/regulations/south-korea.py",
    "site/regions/uk-ai-regulation.html": "content/regulations/united-kingdom.py",
}


def git_date(*paths: str) -> str | None:
    """Last commit date (YYYY-MM-DD) touching any of ``paths``, or None if the
    file has no commit history.

    Raises RuntimeError on an actual git failure (not a repo, git binary
    missing, locked/corrupt repo). Without this, such a failure returned empty
    stdout -> None, which main() treated identically to "no history": it kept
    the STALE date and still printed success — defeating the file's whole
    "accuracy or nothing" premise. sbom.py guards its git call the same way.
    """
    try:
        proc = subprocess.run(
            ["git", "log", "-1", "--format=%cs", "--", *paths],
            capture_output=True, text=True, cwd=REPO,
        )
    except (OSError, subprocess.SubprocessError) as e:
        raise RuntimeError(f"git unavailable: {e}") from e
    if proc.returncode != 0:
        detail = proc.stderr.strip() or f"exit {proc.returncode}"
        raise RuntimeError(f"git log failed: {detail}")
    return proc.stdout.strip() or None


def url_to_path(url: str) -> str:
    rel = url.replace("https://getregula.com/", "").split("#")[0]
    if rel == "" or rel.endswith("/"):
        rel += "index.html"
    return f"site/{rel}"


def main() -> int:
    text = SITEMAP.read_text(encoding="utf-8")
    changed = 0
    matched = 0
    missing = []

    def repl(m: re.Match) -> str:
        nonlocal changed, matched
        matched += 1
        url, old = m.group(1), m.group(2)
        rel = url_to_path(url)
        paths = [rel] + ([SOURCE_MAP[rel]] if rel in SOURCE_MAP else [])
        if not (REPO / rel).exists():
            missing.append(url)
            return m.group(0)
        date = git_date(*paths)
        if not date or date == old:
            return m.group(0)
        changed += 1
        return m.group(0).replace(f"<lastmod>{old}</lastmod>",
                                  f"<lastmod>{date}</lastmod>")

    try:
        new = re.sub(
            r"<loc>([^<]+)</loc>\s*<lastmod>([^<]+)</lastmod>",
            repl, text)
    except RuntimeError as e:
        # A git failure means we cannot derive accurate dates — error out
        # rather than silently keep stale ones and report success.
        print(f"sitemap: ERROR — {e}", file=sys.stderr)
        return 1

    # Parity guard: every <loc> must have been processed. A URL whose
    # <loc>/<lastmod> tags are not adjacent would otherwise be silently skipped
    # (neither updated nor reported), quietly eroding the accuracy guarantee.
    total_locs = text.count("<loc>")
    if matched != total_locs:
        print(f"sitemap: ERROR — matched {matched} of {total_locs} <loc> "
              "entries (loc/lastmod not adjacent?); refusing to write a "
              "partial update", file=sys.stderr)
        return 1

    if missing:
        print(f"sitemap: ERROR — {len(missing)} URLs have no file: {missing}",
              file=sys.stderr)
        return 1
    if changed:
        SITEMAP.write_text(new, encoding="utf-8")
    print(f"sitemap: {changed} lastmod value(s) updated from git history")
    return 0


if __name__ == "__main__":
    sys.exit(main())
