#!/usr/bin/env python3
# regula-ignore
"""Pre-landing gate for claim batches: no paragraph may be sourced ONLY by
its own page's canonical URL.

This is the F21 mechanism. `paragraph_has_source()` returns True on the
first URL it sees, and a page's `<link rel="canonical">` sits in the same
`<head>` paragraph as its `<meta name="description">`. So a number in that
head is permanently "sourced" by the page's own address, which is not a
source for anything.

The full repair lands in 1.5c. This script closes the hole for exactly the
surfaces a batch touches, so a correction cannot be landed onto a paragraph
that only looks sourced.

Usage:
    python3 scripts/check_selfref_sourcing.py FILE [FILE ...]
    python3 scripts/check_selfref_sourcing.py --pack   # files named in PACK-1.5b.md

Exit 0 = clean. Exit 1 = at least one paragraph is self-referentially
sourced; source it properly within the batch or hold that item for 1.5c.

Stdlib only.
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import claim_auditor as ca  # noqa: E402

SELFREF_ATTRS = re.compile(
    r'rel\s*=\s*["\'](?:canonical|alternate)["\']'
    r'|property\s*=\s*["\']og:url["\']'
    r'|name\s*=\s*["\']twitter:url["\']',
    re.IGNORECASE,
)

URL_IN_LINE = re.compile(r'https?://[^\s"\'<>]+')


def _selfref_urls(paragraph: str) -> list[str]:
    """URLs in this paragraph that sit on a self-referential tag."""
    out = []
    for line in paragraph.splitlines():
        if SELFREF_ATTRS.search(line):
            out.extend(URL_IN_LINE.findall(line))
    return out


def audit(paths: list[Path]) -> int:
    """Report paragraphs whose ONLY source is a self-referential URL."""
    offenders = []
    checked = 0

    for p in paths:
        if not p.exists():
            print(f"  SKIP (missing): {p}")
            continue
        raw = p.read_text(encoding="utf-8", errors="replace")
        cleaned = ca.strip_noise(raw, p.suffix.lower())

        for start, end, para in ca.split_paragraphs(cleaned):
            claims = list(ca.NUMERIC_CLAIM.finditer(para))
            if not claims:
                continue
            checked += 1
            has_src, reason = ca.paragraph_has_source(para)
            if not has_src or reason != "url":
                continue

            selfref = _selfref_urls(para)
            if not selfref:
                continue

            # Would it still be sourced with the self-referential URLs removed?
            stripped = para
            for u in selfref:
                stripped = stripped.replace(u, "")
            still, _ = ca.paragraph_has_source(stripped)
            if not still:
                offenders.append((p, start, end,
                                  [c.group(0) for c in claims][:4],
                                  selfref[0]))

    print(f"paragraphs with numeric claims checked: {checked}")
    if not offenders:
        print("RESULT: CLEAN. No paragraph is sourced solely by its own "
              "canonical URL.")
        return 0

    print(f"RESULT: {len(offenders)} PARAGRAPH(S) SOURCED ONLY BY A "
          f"SELF-REFERENTIAL URL\n")
    for p, start, end, claims, url in offenders:
        rel = p.relative_to(ca.REPO_ROOT) if p.is_absolute() else p
        print(f"  {rel}:{start}-{end}")
        print(f"      claims : {claims}")
        print(f"      'source': {url}")
    print("\nEach must be sourced properly within the batch, or that item "
          "held for 1.5c.")
    return 1


def _pack_files() -> list[Path]:
    """Files named in PACK-1.5b.md, so the gate follows the pack."""
    pack = ca.REPO_ROOT / "docs/improvement/PACK-1.5b.md"
    if not pack.exists():
        print("PACK-1.5b.md not found", file=sys.stderr)
        raise SystemExit(2)
    text = pack.read_text(encoding="utf-8")
    found = set()
    for m in re.finditer(r'`?((?:site|docs|scripts|benchmarks)/[\w./-]+'
                         r'\.(?:html|md|py|txt))', text):
        found.add(m.group(1))
    return sorted(ca.REPO_ROOT / f for f in found)


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        raise SystemExit(2)
    if args[0] == "--pack":
        targets = _pack_files()
        print(f"auditing {len(targets)} file(s) named in PACK-1.5b.md")
    else:
        targets = [Path(a) for a in args]
    raise SystemExit(audit(targets))
