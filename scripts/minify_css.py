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

    Comments are stripped FIRST: apostrophes inside prose comments
    ("don't", "it's") would otherwise pair up across comment boundaries
    and swallow real rules into a fake string token. CSS comments cannot
    nest and this stylesheet contains no string with an embedded "/*"
    (asserted below), so comment-first is safe. Quoted strings are then
    tokenised so whitespace collapsing can never corrupt
    `content: "..."` or url("...") values.
    """
    assert not re.search(r'"[^"\n]*/\*', css), \
        "string containing /* found — comment-first stripping unsafe"
    out = re.sub(r"/\*.*?\*/", "", css, flags=re.S)           # comments

    strings: list[str] = []

    def _stash(m: re.Match) -> str:
        strings.append(m.group(0))
        return f"\x00{len(strings) - 1}\x00"

    out = re.sub(r'"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\'', _stash, out)
    out = re.sub(r"\s+", " ", out)                            # collapse ws
    out = re.sub(r"\s*([{};:,>~+])\s*", r"\1", out)           # around punct
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
