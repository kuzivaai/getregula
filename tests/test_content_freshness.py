"""Content freshness invariants for the shipped site.

Each test here exists because the state it forbids was actually shipped:

- Guides, blog posts and region pages carried three different labels for the
  same idea ("Last verified", "Last updated", nothing at all) and two date
  formats inside one section, so a reader could not tell how current a page
  was.
- The blog index advertised a tracker as last updated 8 April 2026 while the
  tracker itself said 4 August 2026.
- A precision figure under an explicit claim freeze sat on the homepage in
  three languages. The English scan missed the German and Portuguese copies
  because those write it "83,5%" with a comma decimal.
- The published privacy notice stated in all three languages that the site has
  "no sign-up forms, no newsletter" while the homepage carried an email capture
  form posting to a third-party processor that the notice did not name.

These are cheap greps. They are here because prose promises do not survive a
context reset and a test does.
"""
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"

# Figures frozen by the claim-integrity record. The comma-decimal forms are
# listed explicitly: an English-only scan reported zero while three pages
# shipped them.
FROZEN_FIGURES = ("83.5", "83,5", "10/30", "16/30", "23/30", "0/40")

# Pages that carry regulatory content and must therefore date themselves.
DATED_SECTIONS = ("guides", "blog", "regions")

REVIEW_LABEL_RE = re.compile(
    r"<strong>Last reviewed:</strong>\s*"
    r"(\d{1,2} (?:January|February|March|April|May|June|July|August|"
    r"September|October|November|December) \d{4})")


# Machine-readable surfaces are published from site/ exactly as the pages are.
# They are listed here because scoping the frozen-figure sweep to *.html left
# site/llms.txt and site/llms-full.txt still carrying the frozen precision
# figure, and its per-tier breakdown, after every HTML page had been cleared.
# An agent reading llms.txt got a number no human-facing page carried.
MACHINE_READABLE_SUFFIXES = (".txt", ".json", ".xml")


def shipped_pages(subdir=None):
    """Every shipped HTML page, excluding redirect stubs and generated samples."""
    root = SITE / subdir if subdir else SITE
    for path in sorted(root.rglob("*.html")):
        if "examples" in path.parts:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if 'content="noindex' in text:      # redirect stub, not content
            continue
        yield path, text


def shipped_claim_surfaces():
    """Every shipped surface a reader or an agent can quote: pages plus text."""
    yield from shipped_pages()
    for path in sorted(SITE.rglob("*")):
        if path.suffix.lower() not in MACHINE_READABLE_SUFFIXES or not path.is_file():
            continue
        if "examples" in path.parts:
            continue
        yield path, path.read_text(encoding="utf-8", errors="replace")


def test_no_frozen_figure_is_published():
    """The claim freeze covers every locale and every published file type."""
    offenders = []
    for path, text in shipped_claim_surfaces():
        for figure in FROZEN_FIGURES:
            if figure in text:
                offenders.append(f"{path.relative_to(ROOT)}: {figure}")
    assert not offenders, (
        "frozen figures must not appear as published claims:\n  "
        + "\n  ".join(offenders))


def test_frozen_figure_sweep_actually_reaches_machine_readable_files():
    """Guard the guard: prove the sweep is not silently HTML-only again.

    The previous version walked *.html and reported a clean sweep while
    site/llms.txt shipped the frozen figure. A count that can go to zero by
    scoping rather than by fixing is the failure this pins down.
    """
    scanned = {path.suffix.lower() for path, _ in shipped_claim_surfaces()}
    assert ".txt" in scanned, scanned
    names = {path.name for path, _ in shipped_claim_surfaces()}
    assert {"llms.txt", "llms-full.txt"} <= names, sorted(names)


def test_no_email_capture_or_third_party_form():
    """The privacy notice says there are no sign-up forms. Keep that true."""
    offenders = []
    for path, text in shipped_pages():
        for marker in ("<form", 'type="email"', "formspree", "unpkg.com"):
            if marker in text:
                offenders.append(f"{path.relative_to(ROOT)}: {marker}")
    assert not offenders, (
        "the published privacy notice states this site has no sign-up forms "
        "and names no processor beyond Plausible; adding one means changing "
        "that notice and resolving the lawful basis first:\n  "
        + "\n  ".join(offenders))


@pytest.mark.parametrize("subdir", DATED_SECTIONS)
def test_regulatory_pages_carry_a_review_date(subdir):
    """Every guide, blog post and region page dates itself, in one format."""
    undated = []
    for path, text in shipped_pages(subdir):
        if not REVIEW_LABEL_RE.search(text):
            undated.append(str(path.relative_to(ROOT)))
    assert not undated, (
        "these pages carry regulatory content with no visible "
        "'Last reviewed: D Month YYYY' line:\n  " + "\n  ".join(undated))


def test_review_label_is_used_consistently():
    """One label, so a reader is not left comparing three vocabularies."""
    superseded = []
    for path, text in shipped_pages():
        for label in ("Last verified:", "Last checked:"):
            if label in text:
                superseded.append(f"{path.relative_to(ROOT)}: {label}")
    assert not superseded, (
        "use 'Last reviewed:' throughout; these carry a superseded label:\n  "
        + "\n  ".join(superseded))


def test_blog_index_dates_match_the_pages_they_link_to():
    """The index advertised a tracker four months staler than the tracker was."""
    index = SITE / "blog" / "writing.html"
    text = index.read_text(encoding="utf-8")
    mismatches = []
    pattern = re.compile(
        r'href="(/(?:blog|regions)/[^"]+)"[^>]*>\s*<div class="art-meta">(.*?)</div>',
        re.S)
    for match in pattern.finditer(text):
        href, meta = match.group(1), match.group(2)
        listed = re.search(r"Last updated:\s*([^<]+)", meta)
        if not listed:
            continue
        target = SITE / href.lstrip("/")
        if not target.exists():
            continue
        target_text = target.read_text(encoding="utf-8", errors="replace")
        actual = REVIEW_LABEL_RE.search(target_text)
        if not actual:
            actual = re.search(r"Last updated:\s*([0-9]{4}-[0-9]{2}-[0-9]{2}"
                               r"|\d{1,2} [A-Za-z]+ \d{4})", target_text)
        if actual and listed.group(1).strip() not in actual.group(1):
            mismatches.append(
                f"{href}: index says {listed.group(1).strip()!r}, "
                f"page says {actual.group(1).strip()!r}")
    assert not mismatches, (
        "the blog index must not advertise a date the target page contradicts:"
        "\n  " + "\n  ".join(mismatches))
