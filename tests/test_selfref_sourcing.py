# regula-ignore
"""F21 — a page's own address is not a source for anything on that page.

`paragraph_has_source()` returned True on the first URL it saw. An HTML
`<head>` parses as a single paragraph, and it is dense with URLs that are
not citations: `<link rel="canonical">`, `og:url`, `og:image`, stylesheet
and preconnect hrefs, icon links. So every numeric claim in a
`<meta name="description">` was permanently "sourced" by the page's own
address, or by its favicon.

MEASURED 2026-07-28, before this repair: 27 numeric matches inside
description-like `<meta>` tags across the 56 tracked site pages (24 after
exemptions, 8 under `name="description"` alone), and every one of their
paragraphs reported source reason "url".

The class is wider than the canonical tag, and this file guards the whole
class:

1. Self-reference   — the page's own URL, on any tag or in prose.
2. Machine metadata — link/meta/img/source/iframe URLs are infrastructure,
                      not references a reader can follow as a citation.
3. Fragment anchors — `href="#section"` points back into the same page.
4. Self file-refs   — a document citing its own filename.

The required regression pair (1.5c) is
`test_pair_selfref_url_fails` / `test_pair_genuine_citation_passes`:
the same page, one paragraph sourced only by its own URL and one properly
sourced, must come out on opposite sides of the gate.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import claim_auditor as ca  # noqa: E402


PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<link rel="canonical" href="https://getregula.com/about.html">
<meta name="description" content="Regula maps 13 frameworks today.">
<link rel="stylesheet" href="https://cdn.example.com/site.css">
</head>
<body>
<p>Regula ships 419 patterns and nothing here says where that came from.</p>

<p>The penalty ceiling is 35 million euro under
<a href="https://eur-lex.europa.eu/eli/reg/2024/1689/oj">Article 99</a>.</p>

<p>Jump to 62 commands via <a href="#commands">the index</a>.</p>
</body>
</html>
"""


def _paras(text: str) -> dict[str, str]:
    """Paragraphs of PAGE keyed by a distinctive substring."""
    out = {}
    for _s, _e, para in ca.split_paragraphs(ca.strip_noise(text, ".html")):
        out[para] = para
    return out


def _para_containing(text: str, needle: str) -> str:
    for _s, _e, para in ca.split_paragraphs(ca.strip_noise(text, ".html")):
        if needle in para:
            return para
    raise AssertionError(f"no paragraph containing {needle!r}")


class TestF21RegressionPair(unittest.TestCase):
    """The pair the 1.5c directive requires, on one page."""

    def test_pair_selfref_url_fails(self):
        """A claim whose only 'source' is the page's own canonical URL."""
        head = _para_containing(PAGE, 'name="description"')
        self.assertIn("13 frameworks", head)
        has_src, reason = ca.paragraph_has_source(head)
        self.assertFalse(
            has_src,
            f"the head block claims a source ({reason!r}). Its URLs are the "
            f"page's own canonical address and a stylesheet CDN. Neither is "
            f"a citation for '13 frameworks'.")

    def test_pair_genuine_citation_passes(self):
        """A claim on the same page with a real external citation."""
        body = _para_containing(PAGE, "35 million")
        has_src, _reason = ca.paragraph_has_source(body)
        self.assertTrue(
            has_src,
            "an EUR-Lex anchor is a genuine citation and must still pass. "
            "A repair that fails this has broken the gate, not fixed it.")


class TestSelfReferenceClass(unittest.TestCase):
    """The rest of the class, so the repair is not canonical-tag-shaped."""

    def test_canonical_tag_url_alone_is_not_a_source(self):
        para = ('<link rel="canonical" href="https://getregula.com/x.html">\n'
                '<meta name="description" content="We ship 419 patterns.">')
        self.assertFalse(ca.paragraph_has_source(para)[0])

    def test_og_url_alone_is_not_a_source(self):
        para = ('<meta property="og:url" content="https://getregula.com/x">\n'
                '<meta property="og:description" content="419 patterns">')
        self.assertFalse(ca.paragraph_has_source(para)[0])

    def test_stylesheet_and_icon_urls_are_not_sources(self):
        """The favicon was sourcing the landing page's numbers."""
        para = ('<link rel="icon" href="https://getregula.com/favicon.ico">\n'
                '<link rel="preconnect" href="https://fonts.example.com">\n'
                '<meta name="description" content="8 languages supported">')
        self.assertFalse(ca.paragraph_has_source(para)[0])

    def test_fragment_only_anchor_is_not_a_source(self):
        para = 'We ship 62 commands, listed in <a href="#commands">the index</a>.'
        self.assertFalse(
            ca.paragraph_has_source(para)[0],
            "an in-page anchor points back at the same page")

    def test_document_citing_its_own_filename_is_not_sourced(self):
        """A self file-ref is the markdown shape of the same defect."""
        para = "Precision is 83.5% as recorded in docs/TRUST.md."
        identity = ca.page_identity("", "docs/TRUST.md")
        self.assertFalse(
            ca.paragraph_has_source(para, identity)[0],
            "TRUST.md citing TRUST.md is a circle, not a source")

    def test_same_file_ref_from_a_different_document_still_sources(self):
        """Control: the file-ref mechanism itself must survive."""
        para = "Precision is 83.5% as recorded in docs/TRUST.md."
        identity = ca.page_identity("", "README.md")
        self.assertTrue(
            ca.paragraph_has_source(para, identity)[0],
            "README citing TRUST.md is a genuine cross-reference")

    def test_page_url_in_prose_is_not_a_source_for_that_page(self):
        para = ("Read more at https://getregula.com/about.html — "
                "we ship 419 patterns.")
        identity = ca.page_identity(
            '<link rel="canonical" href="https://getregula.com/about.html">',
            "site/about.html")
        self.assertFalse(ca.paragraph_has_source(para, identity)[0])

    def test_a_different_page_url_in_prose_still_sources(self):
        """Control: the URL mechanism itself must survive."""
        para = ("Method described at https://example.org/method — "
                "we ship 419 patterns.")
        identity = ca.page_identity(
            '<link rel="canonical" href="https://getregula.com/about.html">',
            "site/about.html")
        self.assertTrue(ca.paragraph_has_source(para, identity)[0])


class TestSourceMechanismsSurvive(unittest.TestCase):
    """Controls. A gate that stops accepting real citations is not a fix."""

    def test_external_anchor_still_sources(self):
        para = ('Fines reach 35 million euro '
                '<a href="https://eur-lex.europa.eu/x">Article 99</a>.')
        self.assertTrue(ca.paragraph_has_source(para)[0])

    def test_markdown_link_still_sources(self):
        para = "Fines reach 35 million euro ([Article 99](https://eur-lex.europa.eu/x))."
        self.assertTrue(ca.paragraph_has_source(para)[0])

    def test_bare_external_url_still_sources(self):
        para = "419 patterns, per https://example.org/benchmark-report"
        self.assertTrue(ca.paragraph_has_source(para)[0])

    def test_citation_word_still_sources(self):
        para = "419 patterns. Source: the pattern registry."
        self.assertTrue(ca.paragraph_has_source(para)[0])

    def test_resolvable_repo_file_ref_still_sources(self):
        para = "419 patterns, counted by scripts/site_facts.py."
        self.assertTrue(ca.paragraph_has_source(para)[0])


class TestPageIdentity(unittest.TestCase):
    def test_identity_collects_canonical_og_and_alternate(self):
        head = (
            '<link rel="canonical" href="https://getregula.com/a.html">\n'
            '<meta property="og:url" content="https://getregula.com/a.html">\n'
            '<link rel="alternate" hreflang="de" '
            'href="https://getregula.com/locales/de.html">\n'
        )
        ident = ca.page_identity(head, "site/a.html")
        self.assertIn("https://getregula.com/a.html", ident.urls)
        self.assertIn("https://getregula.com/locales/de.html", ident.urls)

    def test_identity_records_the_repo_relative_path(self):
        ident = ca.page_identity("", "docs/TRUST.md")
        self.assertEqual(ident.rel_path, "docs/TRUST.md")


if __name__ == "__main__":
    unittest.main()
