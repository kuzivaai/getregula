#!/usr/bin/env python3
"""Generate the minified CSS the site pages actually load.

site/assets/site.css and fonts.css stay readable (the source of truth);
the pages reference site.min.css / fonts.min.css. Deterministic and
stdlib-only so `tests/test_site_critical_css.py` can enforce that the
committed .min.css files are exactly minify(source) — a stale minified
file fails CI instead of silently serving old styles.

Run after any CSS change:  python3 scripts/minify_css.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

SITE_ASSETS = Path(__file__).resolve().parent.parent / "site" / "assets"
PAIRS = [("site.css", "site.min.css"), ("fonts.css", "fonts.min.css")]


def minify(css: str) -> str:
    """Conservative CSS minifier: strings are preserved verbatim.

    Strings and comments are handled in ONE pass: the alternation matches
    whichever opens first, so an apostrophe inside a prose comment
    ("don't") can never pair up across comment boundaries, and a "/*"
    inside a quoted string can never start a comment. Matched strings are
    stashed so whitespace collapsing can never corrupt `content: "..."`
    or url("...") values; matched comments are dropped.

    Punctuation collapsing deliberately excludes `+` and `~` (spaces
    around them are REQUIRED inside calc() expressions) and never removes
    a space BEFORE `:` (that space is a descendant combinator, as in
    `.card :hover` — collapsing it changes which elements match).
    """
    strings: list[str] = []

    def _stash_or_drop(m: re.Match) -> str:
        if m.group(1) is None:          # a comment — drop it
            return ""
        strings.append(m.group(1))      # a string — preserve verbatim
        return f"\x00{len(strings) - 1}\x00"

    out = re.sub(
        r'("(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\')|/\*.*?\*/',
        _stash_or_drop, css, flags=re.S,
    )
    out = re.sub(r"\s+", " ", out)                            # collapse ws
    out = re.sub(r"\s*([{};,>])\s*", r"\1", out)              # around punct
    out = re.sub(r":\s+", ":", out)                           # after colon only
    out = out.replace(";}", "}")                              # last ;
    out = out.strip()
    return re.sub(r"\x00(\d+)\x00", lambda m: strings[int(m.group(1))], out)


def main() -> int:
    for src_name, min_name in PAIRS:
        src = SITE_ASSETS / src_name
        minified = minify(src.read_text(encoding="utf-8"))
        (SITE_ASSETS / min_name).write_text(minified + "\n", encoding="utf-8")
        print(f"{min_name}: {src.stat().st_size} -> {len(minified) + 1} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
