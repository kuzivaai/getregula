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


# A <form> open tag, so its attributes can be judged rather than its existence.
FORM_TAG_RE = re.compile(r"<form\b([^>]*)>", re.IGNORECASE)

# The attributes that make a form able to send anything anywhere. A form with
# none of them cannot transmit: submitting it can only reload the same URL, and
# every form on this site calls preventDefault before even that.
TRANSMITTING_ATTRS = ("action=", "method=", "formaction=", "enctype=")

# Markers of capture or of a processor the privacy notice does not name.
CAPTURE_MARKERS = ('type="email"', "type='email'", 'type="tel"', 'type="password"',
                   "formspree", "unpkg.com", "mailchimp", "hsforms", "typeform")


def transmitting_forms(text):
    """Form open tags that could send data somewhere."""
    return [tag.strip() for tag in FORM_TAG_RE.findall(text)
            if any(a in tag.lower() for a in TRANSMITTING_ATTRS)]


def test_no_email_capture_or_transmitting_form():
    """The privacy notice says there are no sign-up forms and no form that
    submits data to us. Keep that true.

    NARROWED 2026-08-18, and the narrowing is the point. This used to forbid
    the substring "<form" outright. That is a proxy for the real invariant, and
    the front page now groups five radio questions in a form element so that a
    keyboard and a screen reader treat them as one group with one submit
    action; it has no action, no method, and its handler calls preventDefault.
    Forbidding the tag would have cost real assistive-technology semantics to
    protect a promise the tag does not break.

    What the notice actually promises, in all three languages, is that no form
    submits data to us and no visitor analytics or form processor runs. That is
    what is tested now: a form that can transmit, an input that captures an
    identity, or a named third-party form processor. The narrowed check is
    proved able to catch the original defect by
    test_the_form_check_still_catches_the_defect_it_was_written_for.
    """
    offenders = []
    for path, text in shipped_pages():
        for tag in transmitting_forms(text):
            offenders.append(f"{path.relative_to(ROOT)}: <form {tag[:80]}>")
        for marker in CAPTURE_MARKERS:
            if marker in text:
                offenders.append(f"{path.relative_to(ROOT)}: {marker}")
    assert not offenders, (
        "the published privacy notice states this site has no sign-up forms, "
        "no form that submits data to us, and no visitor analytics or form "
        "processor; adding one means changing that notice and resolving the "
        "lawful basis first:\n  "
        + "\n  ".join(offenders))


def test_the_form_check_still_catches_the_defect_it_was_written_for():
    """Control. A narrowed check that cannot fail is worse than no check.

    The defect this test was written for was an email capture form on the
    homepage posting to a third-party processor. Both halves are replayed
    against the real predicate, together with the shape that is now allowed, so
    the narrowing is shown to be a narrowing and not a removal.
    """
    posted = '<form action="https://formspree.io/f/abc" method="POST">'
    assert transmitting_forms(posted), "a form with an action is not detected"
    assert transmitting_forms('<form method="get">'), "a method is not detected"
    assert any(m in '<input type="email" name="email">' for m in CAPTURE_MARKERS), (
        "an email input is not detected")
    assert not transmitting_forms('<form id="qual-form" novalidate>'), (
        "the client-side question group is misreported as transmitting")


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


def test_the_homepage_reading_list_count_matches_the_index_it_links_to():
    """"All N guides & M articles" must equal what that index actually links.

    It did not. The homepage advertised 14 articles while
    site/blog/writing.html linked 15, so a reader following the label was
    told the wrong size of the thing they were about to open. Nothing caught
    it because the figure is prose on one page describing a different page.

    Both numbers are derived here from the index's own links rather than from
    a list, so adding or removing an article moves the check rather than
    breaking it silently.
    """
    index = (SITE / "blog" / "writing.html").read_text(encoding="utf-8")
    guides = len(set(re.findall(r'href="/guides/[a-z0-9-]+\.html"', index)))
    articles = len(set(re.findall(r'href="/blog/blog-[a-z0-9-]+\.html"', index)))
    assert guides and articles, "the derivation stopped finding links"

    label = re.compile(r"All (\d+) guides &(?:amp;)? (\d+) articles")
    seen = 0
    for path, text in shipped_pages():
        for found_guides, found_articles in label.findall(text):
            seen += 1
            assert (int(found_guides), int(found_articles)) == (guides, articles), (
                f"{path.relative_to(ROOT)} advertises {found_guides} guides and "
                f"{found_articles} articles; site/blog/writing.html links "
                f"{guides} and {articles}")
    assert seen == 1, (
        f"expected exactly one page to carry the reading-list label, found {seen}; "
        f"a second carrier is a second thing to keep in sync")
