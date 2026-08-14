# regula-ignore: * -- quotes regulatory text for verification, does not implement a practice
"""Verify that quoted regulatory passages on the site are verbatim.

A quotation is a promise that the source says exactly this. The site has
already shipped one that was not: site/blog/blog-does-ai-act-apply.html quoted
Article 3(4) as "any natural or legal person ... under its authority." where
Regulation (EU) 2024/1689 says "a natural or legal person", and the quotation
dropped the personal non-professional exclusion entirely, closing on a full
stop as though the definition ended there.

The check is deliberately narrow. It judges a passage only when it is (a)
inside quotation marks, (b) at least MIN_QUOTE_CHARS long, so a quoted phrase
or a UI label is not treated as a citation, and (c) near an Article, Annex or
Recital reference. Anything it cannot judge is counted and reported as out of
scope rather than silently passed, because a checker that quietly ignores what
it cannot judge reads as a clean bill of health.

Corpora are cached under references/corpora/*.txt.gz so the check runs offline
and in CI. Refresh them with --refresh, which needs network.

Usage:
  python3 scripts/verify_quotations.py             # check the site
  python3 scripts/verify_quotations.py --verbose   # list every passage checked
  python3 scripts/verify_quotations.py --refresh   # re-download the corpora

Exit codes: 0 = no mismatches, 1 = at least one mismatch or missing corpus.
"""
import argparse
import gzip
import html
import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
CORPORA = ROOT / "references" / "corpora"

# Primary sources. EUR-Lex's own web front end returns HTTP 202 with an empty
# body to automated fetches; the Publications Office CELLAR endpoint serves the
# same Official Journal text and is what these URLs use.
SOURCES = {
    "eu_ai_act_en": {
        "url": "https://publications.europa.eu/resource/celex/32024R1689",
        "lang": "eng",
        "label": "Regulation (EU) 2024/1689 (EU AI Act), English OJ text",
    },
    "eu_omnibus_en": {
        "url": "https://publications.europa.eu/resource/celex/32026R1744",
        "lang": "eng",
        "label": "Regulation (EU) 2026/1744 (Digital Omnibus), English OJ text",
    },
}

MIN_QUOTE_CHARS = 40
MAX_QUOTE_CHARS = 600
# The site marks citations two ways: &ldquo;/&rdquo; on the guides, and plain
# straight quotes on the blog, including the fabricated Article 3(4) quotation
# that prompted this script. Both must be read, and each fails differently.
#
# Typographic pairs are unambiguous. Straight quotes are not: opening and
# closing are the same character, so matching across a whole stripped page
# pairs the end of one sentence with the start of the next and invents
# passages nobody wrote (6 such on guides/article-9-risk-management.html, a
# page with no citation at all). Restricting to typographic pairs instead
# silently skipped the blog page entirely, which is the worse failure.
#
# So candidates are extracted per block-level element. Inside one paragraph or
# list item, straight quotes pair correctly and cannot splice across a heading.
QUOTE_RE = re.compile(
    r'[“«"]([^“”«»"]{%d,%d})[”»"]'
    % (MIN_QUOTE_CHARS, MAX_QUOTE_CHARS))
NEAR_RE = re.compile(r"Article\s+\d+|Annex\s+[IVX]+|Recital\s+\d+", re.I)
BLOCK_SPLIT_RE = re.compile(
    r"</(?:p|li|h[1-6]|td|th|blockquote|figcaption|dd|dt)\s*>", re.I)
# A quotation may legitimately carry a trailing sentence stop inside the marks;
# that is a typographic convention, not a misquotation of substance.
TRAILING_PUNCT_RE = re.compile(r"[.,;:]+$")

# Passages that sit near an Article reference but are not quoting legislation:
# tool output, code, shell lines and file paths the page is describing.
NOT_LEGISLATION = re.compile(
    r"json\.load|import sys|print\(|\.py\b|\.js\b|regula |findings|--json|\$ |"
    r"Patterns:|line \d+:|src/|sys\.stdin", re.I)


def normalise(text: str) -> str:
    """Fold typography so a real quotation is not failed for smart quotes."""
    text = unicodedata.normalize("NFC", text)
    for source, target in (
        ("“", '"'), ("”", '"'), ("„", '"'),
        ("«", '"'), ("»", '"'),
        ("’", "'"), ("‘", "'"),
        # En dash and em dash, written as escapes: this project forbids the
        # literal characters in source, and this table exists to fold them.
        ("\u2013", "-"), ("\u2014", "-"),
        (" ", " "),
    ):
        text = text.replace(source, target)
    return re.sub(r"\s+", " ", text).strip()


def visible_text(raw_html: str) -> str:
    body = re.sub(r"<script.*?</script>|<style.*?</style>", " ", raw_html,
                  flags=re.S | re.I)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", body)))


ANCHOR_WORDS = 6


def anchors_in_corpora(needle: str, corpora: dict) -> bool:
    """True if any run of ANCHOR_WORDS words from the passage is in a corpus.

    This separates "a misquotation of the AI Act" from "not a quotation of the
    AI Act at all". A real citation that has drifted still shares long runs of
    wording with the source; a forum comment or a code sample shares none. The
    distinction matters because reporting the second kind as a misquote would
    manufacture findings, and a checker that cries wolf gets switched off.
    """
    words = needle.split()
    if len(words) < ANCHOR_WORDS:
        return False
    for index in range(len(words) - ANCHOR_WORDS + 1):
        window = " ".join(words[index:index + ANCHOR_WORDS])
        if any(window in text for text in corpora.values()):
            return True
    return False


def load_corpora() -> dict:
    corpora = {}
    for key in SOURCES:
        path = CORPORA / f"{key}.txt.gz"
        if not path.exists():
            print(f"quotation-check: corpus missing: "
                  f"{path.relative_to(ROOT)}. Run --refresh (needs network).",
                  file=sys.stderr)
            return {}
        with gzip.open(path, "rt", encoding="utf-8") as handle:
            corpora[key] = normalise(handle.read())
    return corpora


def refresh_corpora() -> int:
    import urllib.request
    CORPORA.mkdir(parents=True, exist_ok=True)
    for key, meta in SOURCES.items():
        request = urllib.request.Request(
            meta["url"],
            headers={"Accept": "application/xhtml+xml",
                     "Accept-Language": meta["lang"]},
        )
        with urllib.request.urlopen(request, timeout=180) as response:
            raw = response.read().decode("utf-8", errors="replace")
        text = visible_text(raw)
        with gzip.open(CORPORA / f"{key}.txt.gz", "wt", encoding="utf-8") as out:
            out.write(text)
        print(f"quotation-check: refreshed {key} "
              f"({len(text)} chars) from {meta['url']}")
    (CORPORA / "SOURCES.json").write_text(
        json.dumps(SOURCES, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


def candidate_quotations():
    """Yield (path, quotation, in_scope) for quoted passages on the site.

    Extraction is per block-level element so straight-quote pairs cannot span
    two sentences in different elements. Scope context is the whole page,
    because a page may name the Article in a heading above the quotation.
    """
    for path in sorted(SITE.rglob("*.html")):
        raw = path.read_text(encoding="utf-8", errors="replace")
        if 'content="noindex' in raw:          # redirect stubs are not content
            continue
        page_text = visible_text(raw)
        if not NEAR_RE.search(page_text):
            continue
        for block in BLOCK_SPLIT_RE.split(raw):
            block_text = visible_text(block)
            for match in QUOTE_RE.finditer(block_text):
                quote = match.group(1).strip()
                yield path, quote, not NOT_LEGISLATION.search(quote)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Verify quoted regulatory passages against primary sources.")
    parser.add_argument("--refresh", action="store_true",
                        help="re-download the primary corpora (needs network)")
    parser.add_argument("--verbose", action="store_true",
                        help="list every passage checked, not only mismatches")
    args = parser.parse_args(argv)

    if args.refresh:
        return refresh_corpora()

    corpora = load_corpora()
    if not corpora:
        return 1

    checked = verbatim = skipped = out_of_scope = 0
    mismatches = []
    for path, quote, in_scope in candidate_quotations():
        if not in_scope:
            skipped += 1
            continue
        needle = normalise(quote)
        found_in = [name for name, text in corpora.items() if needle in text]
        if not found_in:
            trimmed = TRAILING_PUNCT_RE.sub("", needle)
            found_in = [name for name, text in corpora.items()
                        if trimmed and trimmed in text]
        if not found_in and not anchors_in_corpora(needle, corpora):
            # Nothing in this passage appears in the corpora at all, so it is
            # not a quotation of these instruments: it is a forum comment, a
            # code sample, or a citation of another source such as the UK white
            # paper or the Colorado Act. Judging it would be inventing a
            # finding, so it is counted as out of scope and reported as such.
            out_of_scope += 1
            continue
        checked += 1
        if found_in:
            verbatim += 1
            if args.verbose:
                print(f"  OK   {path.relative_to(ROOT)}: verbatim in "
                      f"{found_in[0]} ({len(quote)} chars)")
        else:
            mismatches.append((path.relative_to(ROOT), quote))

    print(f"quotation-check: {checked} passage(s) judged, "
          f"{verbatim} verbatim, {len(mismatches)} mismatched; "
          f"{out_of_scope} not a quotation of these instruments, "
          f"{skipped} skipped as code or tool output")
    if mismatches:
        print("\n  Not found verbatim in a primary corpus. Each is either a "
              "paraphrase presented as a quotation, a quotation of a source "
              "not in the corpora, or a misquote:\n")
        for relative, quote in mismatches:
            print(f"  {relative}\n      “{quote[:240]}”\n")
        return 1
    print("  every quoted regulatory passage matches its primary source")
    return 0


if __name__ == "__main__":
    sys.exit(main())
