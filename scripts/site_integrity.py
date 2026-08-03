# regula-ignore
"""Site integrity guard — makes region-page drift structurally visible.

Born from the 16 Jul 2026 finding that the shipped Colorado page had
drifted from its generator source while the builder silently wrote to
the wrong directory. Four checks:

  1. REGEN     every sourced region page is re-rendered in memory and
               compared byte-for-byte with the shipped page. Identical
               → OK. Drift matching a recorded fingerprint in
               KNOWN_DRIFT → WARN (ticketed debt, visible every run).
               Any other drift → FAIL.
  2. SOURCES   every site/regions/*.html must have a content source in
               content/regulations/ or an entry in EXEMPT_NO_SOURCE.
               A new unsourced page → FAIL.
  3. LINKS     every internal href/src across site/**/*.html resolves.
  4. CLAIMS    scripts/claim_auditor.py runs over all site pages;
               unsourced numeric claims → FAIL.

Usage:
  python3 scripts/site_integrity.py            # all checks
  python3 scripts/site_integrity.py --root DIR # run against a copy
  python3 scripts/site_integrity.py --check regen,links

Exit codes: 0 = OK (warnings allowed), 1 = any FAIL, 2 = usage error.
"""

import argparse
import hashlib
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

ROOT = Path(__file__).resolve().parents[1]

# Pages with no generator source. Each entry is explicit and reviewed;
# adding a page here requires the same review. DQ-7 resolved 16 Jul
# 2026: brazil and south-africa converted to content/regulations/
# sources; uae formally exempted (see reason).
EXEMPT_NO_SOURCE = {
    "regulations.html": "hub index page, hand-maintained",
    "uae.html": "conversion LANDING page (hero CTA, copy buttons, demo "
                "terminal, sector cards) — a different information "
                "architecture from the tracker template; forcing it "
                "through the tracker schema would destroy it. Formally "
                "exempted by DQ-7 decision, 16 Jul 2026.",
}

# Sourced pages with known, reviewed drift between source and shipped
# HTML. Value = sha256 of the unified diff at the time the drift was
# reviewed. If the diff changes (new drift on top), the check FAILS.
# DQ-6 (Korea) reconciled 16 Jul 2026: shipped content ported into
# content/regulations/south-korea.py, page rebuilt through the
# pipeline. The 21 Jul pass now only re-verifies the amendment against
# primary text.
KNOWN_DRIFT = {}


def _diff_fingerprint(shipped: str, rendered: str) -> str:
    import difflib
    diff = "\n".join(difflib.unified_diff(
        shipped.splitlines(), rendered.splitlines(), lineterm=""))
    return hashlib.sha256(diff.encode("utf-8")).hexdigest()[:16]


def check_regen(root: Path, fingerprint_mode: bool = False) -> list:
    """Render every sourced region and compare with the shipped page."""
    sys.path.insert(0, str(root / "scripts"))
    import importlib
    import build_regulations
    importlib.reload(build_regulations)
    failures = []
    content_dir = root / "content" / "regulations"
    for src in sorted(content_dir.glob("*.py")):
        if src.name.startswith("_"):
            continue
        region = build_regulations._load_region(src)
        rendered = build_regulations.render_region(region)
        shipped_path = root / "site" / "regions" / f"{region['slug']}.html"
        if not shipped_path.exists():
            failures.append(f"FAIL regen: {region['slug']}.html missing from site/regions/")
            continue
        shipped = shipped_path.read_text(encoding="utf-8")
        if rendered == shipped:
            print(f"  OK   regen {src.name}: source and shipped page identical")
            continue
        fp = _diff_fingerprint(shipped, rendered)
        if fingerprint_mode:
            print(f"  FP   {src.stem}: \"{fp}\"")
            continue
        known = KNOWN_DRIFT.get(src.stem)
        if known == fp:
            print(f"  WARN regen {src.name}: known reviewed drift ({fp}) — reconciliation ticketed (DQ-6)")
        else:
            failures.append(
                f"FAIL regen: {src.name} drift fingerprint {fp} != recorded "
                f"{known or '(none)'} — unreviewed drift between source and shipped page")
    return failures


def check_sources(root: Path) -> list:
    """Every shipped region page needs a source or an exemption entry."""
    failures = []
    content_dir = root / "content" / "regulations"
    slugs = set()
    for src in content_dir.glob("*.py"):
        if src.name.startswith("_"):
            continue
        text = src.read_text(encoding="utf-8")
        m = re.search(r'"slug":\s*"([^"]+)"', text)
        if m:
            slugs.add(m.group(1) + ".html")
    for page in sorted((root / "site" / "regions").glob("*.html")):
        if page.name in slugs:
            print(f"  OK   source {page.name}: generated from content/regulations/")
        elif page.name in EXEMPT_NO_SOURCE:
            print(f"  WARN source {page.name}: exempt — {EXEMPT_NO_SOURCE[page.name]}")
        else:
            failures.append(
                f"FAIL source: site/regions/{page.name} has no content source "
                f"and no exemption entry in site_integrity.py")
    return failures


def check_links(root: Path) -> list:
    """Static internal link/anchor crawl over site/**/*.html."""
    site = root / "site"
    attr_re = re.compile(r'(?:href|src)="([^"]+)"')
    id_re = re.compile(r'id="([^"]+)"')
    dead = []
    checked = 0
    for page in sorted(site.rglob("*.html")):
        html = page.read_text(encoding="utf-8", errors="replace")
        ids = set(id_re.findall(html))
        for url in attr_re.findall(html):
            if url.startswith(("http://", "https://", "mailto:", "tel:",
                               "//", "data:", "javascript:")):
                continue
            checked += 1
            base, _, frag = url.partition("#")
            if not base:
                if frag and frag not in ids:
                    dead.append(f"FAIL link: {page.relative_to(site)} -> {url} (missing anchor)")
                continue
            base = base.split("?")[0]
            target = (site / base.lstrip("/")) if base.startswith("/") else (page.parent / base).resolve()
            if target.is_dir():
                target = target / "index.html"
            if not target.exists():
                dead.append(f"FAIL link: {page.relative_to(site)} -> {url} (missing file)")
    print(f"  {'OK  ' if not dead else 'FAIL'} links: {checked} internal refs, {len(dead)} dead")
    return dead


def check_version(root: Path) -> list:
    """Homepage version badges must match scripts/constants.py VERSION.

    The badge went stale silently at the 1.7.4 release (all three
    locales still said v1.7.3 three weeks later); this makes the drift
    a guard failure so every release flips it or fails.
    """
    import re as _re
    failures = []
    version_file = (root / "scripts" / "constants.py").read_text(encoding="utf-8")
    m = _re.search(r'^VERSION\s*=\s*"([^"]+)"', version_file, _re.M)
    if not m:
        return ["FAIL version: could not read VERSION from scripts/constants.py"]
    version = m.group(1)
    pages = [root / "site" / "index.html",
             root / "site" / "locales" / "de.html",
             root / "site" / "locales" / "pt-br.html"]
    for page in pages:
        text = page.read_text(encoding="utf-8")
        badges = _re.findall(r"v(\d+\.\d+\.\d+)\s*&middot;", text)
        stale = [b for b in badges if b != version]
        if stale:
            failures.append(
                f"FAIL version: {page.relative_to(root)} badge says "
                f"v{stale[0]} but scripts/constants.py VERSION is {version}")
        else:
            print(f"  OK   version {page.name}: badge matches v{version}")
    return failures


def check_claims(root: Path) -> list:
    """Run the claim auditor across every site page."""
    pages = [str(p) for p in sorted((root / "site").rglob("*.html"))]
    result = subprocess.run(
        [sys.executable, str(root / "scripts" / "claim_auditor.py")] + pages,
        capture_output=True, text=True, timeout=300)
    tail = (result.stdout or result.stderr).strip().splitlines()[-1:]
    print(f"  {'OK  ' if result.returncode == 0 else 'FAIL'} claims: {tail[0] if tail else '(no output)'}")
    return [] if result.returncode == 0 else [f"FAIL claims: {tail[0] if tail else 'auditor failed'}"]


def main() -> int:
    parser = argparse.ArgumentParser(description="Regula site integrity guard")
    parser.add_argument("--root", default=str(ROOT),
                        help="Repo root to check (default: this repo). "
                             "Use a copy for sandbox/seeded-drift testing.")
    parser.add_argument("--check", default="regen,sources,links,claims,version",
                        help="Comma-separated subset: regen,sources,links,claims,version")
    parser.add_argument("--fingerprint", action="store_true",
                        help="Print drift fingerprints for KNOWN_DRIFT entries instead of judging")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not (root / "site").exists():
        print(f"error: {root} has no site/ directory", file=sys.stderr)
        return 2

    wanted = {c.strip() for c in args.check.split(",") if c.strip()}
    failures = []
    print(f"Site integrity — root: {root}")
    if "regen" in wanted:
        failures += check_regen(root, fingerprint_mode=args.fingerprint)
    if "sources" in wanted:
        failures += check_sources(root)
    if "links" in wanted:
        failures += check_links(root)
    if "claims" in wanted:
        failures += check_claims(root)
    if "version" in wanted:
        failures += check_version(root)

    print("=" * 60)
    if failures:
        for f in failures:
            print(f"  {f}")
        print(f"  RESULT: FAIL ({len(failures)} failure(s))")
        return 1
    print("  RESULT: OK (warnings, if any, are ticketed debt)")
    return 0


if __name__ == "__main__":
    from tree_guard import stamp
    stamp()
    sys.exit(main())
