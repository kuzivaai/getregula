#!/usr/bin/env python3
# regula-ignore
"""Links from a localised page to an English-only page must say so.

WHY THIS EXISTS
---------------
The 15 August audit recorded one instance: the German and Brazilian pages both
link to `/pricing.html`, and only `site/pricing.html` is tracked, so a reader
following a German call to action lands on an English page with no warning.

Enumerated rather than read, per measurement rule 4c, it is not one instance.
Four localised pages carry roughly fifty links to English-only targets: the
pricing and sample-report calls to action, every blog post, every region page
and the about page. Fixing the two that were noticed would have left the class
open and the count wrong.

WHAT IS AND IS NOT CLAIMED
--------------------------
`hreflang` is best practice, not a WCAG 2.2 AA success criterion. 3.1.2
Language of Parts governs content IN a page, not the language of a link's
destination, and no AA criterion requires warning about it. So this tool is
not "a WCAG fix" and must not be described as one. It makes a machine-readable
fact true that was previously absent, which helps assistive technology and
search engines, and it is the part that can be applied mechanically to fifty
links without touching a word of published copy.

The part that genuinely changes what a reader sees, a visible "(auf Englisch)"
or "(em ingles)" cue, is applied by hand and only to body-copy calls to action,
where landing on an unreadable page is a task failure rather than a mild
surprise. Suffixing nineteen footer links in each locale would be worse for a
reader, not better, and that is a design judgement rather than an omission.

The real fix for a reader who cannot read English is a translated page. Until
one exists, a visible language cue on task-critical links and a machine-readable
`hreflang` value make the limitation explicit. Pricing is a claim-sensitive
surface, so translated copies must be generated and checked together.

Usage:
    python3 scripts/locale_link_audit.py            # report
    python3 scripts/locale_link_audit.py --check    # exit 1 if any are missing
    python3 scripts/locale_link_audit.py --apply    # add hreflang="en"
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# A localised page and the language it is written in, derived from the tracked
# file list rather than listed here, so a new locale cannot be missed.
_LOCALE_PAGE = re.compile(r'^site/(?:.*/)?(?:.*-)?(de|pt-br)\.html$')

# An internal link to another page in this site.
_ANCHOR = re.compile(r'<a\s[^>]*?href="(/[^"#?]*\.html)(?:[^"]*)"[^>]*>')
_HREF_ATTR = re.compile(r'(href="/[^"]*\.html[^"]*")')


def tracked_site_files() -> set:
    out = subprocess.run(["git", "ls-files", "site"], cwd=REPO_ROOT,
                         capture_output=True, text=True, check=False)
    if out.returncode != 0:
        raise RuntimeError(f"git ls-files failed: {out.stderr.strip()}")
    return {line for line in out.stdout.split("\n") if line}


def locale_pages(tracked: set) -> dict:
    """{path: language} for every tracked localised page."""
    pages = {}
    for path in sorted(tracked):
        m = _LOCALE_PAGE.match(path)
        if m:
            pages[path] = m.group(1)
    return pages


# BCP 47 tags for the site's locales. `pt-br` on disk, `pt-BR` in markup.
_HREFLANG = {"de": "de", "pt-br": "pt-BR", "en": "en"}
_KNOWN_LANGS = ("pt-br", "de")  # longest first: `pt-br` must beat `br`


def target_language(href: str) -> str:
    """The language of the link's own target, from its path.

    Two shapes are in use and both must count, or the audit reports links that
    are already correct: `/locales/de.html` and `/assess/de.html` name the
    language as the filename, `/privacy-de.html` and `/terms-de.html` as a
    suffix. Missing either is how a hand sweep produces a wrong total, and the
    first draft of this audit did exactly that.

    Anything with no locale marker is English, which is the site's default.
    """
    stem = href[:-len(".html")]
    for lang in _KNOWN_LANGS:
        if stem.endswith(f"/{lang}") or stem.endswith(f"-{lang}"):
            return lang
    return "en"


def expected_hreflang(href: str, page_lang: str) -> str | None:
    """The hreflang this link should carry, or None if it needs none.

    None when the target is in the same language as the page it sits on: the
    attribute exists to declare a CHANGE of language, and adding it everywhere
    would make it noise.

    A language switcher is not an English link. `/assess/pt-br.html` on the
    German page is a deliberate pointer to the Portuguese version and wants
    `hreflang="pt-BR"`. The first draft called every non-German target English
    and would have mislabelled all four switchers.
    """
    target = target_language(href)
    if target == page_lang:
        return None
    return _HREFLANG[target]


def audit(tracked: set = None) -> list:
    """Return [(path, line, href, expected, actual)] for cross-language links."""
    tracked = tracked_site_files() if tracked is None else tracked
    findings = []
    for path, lang in locale_pages(tracked).items():
        text = (REPO_ROOT / path).read_text(encoding="utf-8", errors="replace")
        for m in _ANCHOR.finditer(text):
            href = m.group(1)
            if f"site{href}" not in tracked:
                continue  # a broken link is site_integrity.py's job, not this
            want = expected_hreflang(href, lang)
            if want is None:
                continue
            have = re.search(r'hreflang="([^"]*)"', m.group(0))
            findings.append((path, text[:m.start()].count("\n") + 1, href,
                             want, have.group(1) if have else None))
    return findings


def apply_hreflang(tracked: set = None) -> int:
    """Insert hreflang="en" after the href of every cross-language link.

    Rewrites by anchor position, from the END of the file backwards, so an
    inserted attribute cannot shift the offsets of anchors not yet processed.
    """
    tracked = tracked_site_files() if tracked is None else tracked
    changed = 0
    for path, lang in locale_pages(tracked).items():
        file = REPO_ROOT / path
        text = file.read_text(encoding="utf-8")
        edits = []
        for m in _ANCHOR.finditer(text):
            href = m.group(1)
            if f"site{href}" not in tracked:
                continue
            want = expected_hreflang(href, lang)
            if want is None:
                continue
            if "hreflang=" in m.group(0):
                continue
            tag = m.group(0)
            new_tag = _HREF_ATTR.sub(rf'\1 hreflang="{want}"', tag, count=1)
            if new_tag == tag:
                raise RuntimeError(f"could not place hreflang in {path}: {tag}")
            edits.append((m.start(), m.end(), new_tag))
        for start, end, new_tag in reversed(edits):
            text = text[:start] + new_tag + text[end:]
        if edits:
            file.write_text(text, encoding="utf-8")
            changed += len(edits)
    return changed


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if any cross-language link is unmarked or wrong")
    ap.add_argument("--apply", action="store_true",
                    help="add the correct hreflang to every one that lacks it")
    args = ap.parse_args(argv)

    if args.apply:
        n = apply_hreflang()
        print(f"locale-link-audit: added hreflang to {n} link(s)")

    findings = audit()
    wrong = [f for f in findings if f[3] != f[4]]
    print(f"locale-link-audit: {len(findings)} cross-language link(s) across "
          f"{len({f[0] for f in findings})} localised page(s); "
          f"{len(wrong)} unmarked or mislabelled")
    for path, line, href, want, have in wrong:
        print(f"  {path}:{line} -> {href}  expected hreflang=\"{want}\", "
              f"found {have!r}")
    if args.check and wrong:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
