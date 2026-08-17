# regula-ignore
"""A link that changes language must declare it.

The 15 August audit recorded one instance: the German and Brazilian pages link
to `/pricing.html`, and only `site/pricing.html` is tracked, so a reader
following a German call to action lands on an English page unwarned.

Enumerated rather than read, per measurement rule 4c, it was 82 links across
8 localised pages, and hand-reading found 4 pages. Two rounds of hand
enumeration have now failed in this programme for the same reason; this is a
third, and the tool is the source of the number rather than this docstring.

WHAT THIS DOES NOT CLAIM. `hreflang` is best practice, not a WCAG 2.2 AA
success criterion: 3.1.2 Language of Parts governs content IN a page, not a
link's destination. This is not a conformance fix and must not be reported as
one. It is a machine-readable fact that was absent and is now true, plus a
visible cue on the four body-copy calls to action, where landing on an
unreadable page is a task failure rather than a mild surprise.

The real fix for a reader who cannot read English is a translated page, which
is a content and commercial decision under `PRODUCT_BUILD STOP` and
`PAYMENT_GATE NOT_ACTIVE` and is not made here.
"""
import re
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import locale_link_audit as lla  # noqa: E402


class TestLocaleLinkLanguage(unittest.TestCase):

    def test_every_cross_language_link_declares_its_language(self):
        findings = lla.audit()
        self.assertTrue(
            findings,
            "the audit found no cross-language links at all, which this site "
            "certainly has; the discovery is broken, not the site")
        wrong = [f for f in findings if f[3] != f[4]]
        self.assertEqual(
            wrong, [],
            "these links change language without declaring it: "
            + "; ".join(f"{p}:{ln} -> {h} want {w!r} got {g!r}"
                        for p, ln, h, w, g in wrong)
            + ". Run: python3 scripts/locale_link_audit.py --apply")

    def test_discovery_finds_every_localised_page(self):
        """Control for the enumeration, which is where the count went wrong.

        Hand-reading found four localised pages. There are eight: the two
        assess pages and the two locale landing pages, plus privacy and terms
        in both languages, which use a `-de`/`-pt-br` SUFFIX rather than a
        filename. A discovery that misses a shape reports a clean result for
        pages it never opened.
        """
        pages = lla.locale_pages(lla.tracked_site_files())
        for expected in ("site/locales/de.html", "site/locales/pt-br.html",
                         "site/assess/de.html", "site/assess/pt-br.html",
                         "site/privacy-de.html", "site/privacy-pt-br.html",
                         "site/terms-de.html", "site/terms-pt-br.html"):
            self.assertIn(expected, pages,
                          f"{expected} is a localised page and was not discovered")

    def test_a_language_switcher_is_not_labelled_english(self):
        """Control. The first draft called every non-German target English.

        `/assess/pt-br.html` on the German page is a deliberate pointer to the
        Portuguese version. Marking it `hreflang="en"` would be a false
        statement in markup, which is worse than the missing attribute it
        replaced.
        """
        self.assertEqual(lla.expected_hreflang("/assess/pt-br.html", "de"),
                         "pt-BR")
        self.assertEqual(lla.expected_hreflang("/privacy-de.html", "pt-br"),
                         "de")
        self.assertEqual(lla.expected_hreflang("/about.html", "de"), "en")

    def test_a_same_language_link_needs_no_declaration(self):
        """Control the other way. hreflang declares a CHANGE of language.

        Adding it to every link would make the attribute noise, and noise is
        how a real signal stops being read.
        """
        self.assertIsNone(lla.expected_hreflang("/assess/de.html", "de"))
        self.assertIsNone(lla.expected_hreflang("/privacy-pt-br.html", "pt-br"))

    def test_pt_br_is_not_parsed_as_br(self):
        """Control for the longest-match ordering in _KNOWN_LANGS."""
        self.assertEqual(lla.target_language("/locales/pt-br.html"), "pt-br")
        self.assertEqual(lla.target_language("/terms-pt-br.html"), "pt-br")

    def test_the_body_calls_to_action_carry_a_visible_cue(self):
        """The machine-readable half is invisible to a sighted reader.

        A German reader clicking "Kostenlose Fragen und geplante Beratung"
        cannot see `hreflang`. These four links are the ones where the
        destination being unreadable defeats the task, so they say so in the
        link text as well.
        """
        for path, cue, hrefs in (
                ("site/locales/de.html", "(auf Englisch)",
                 ("/pricing.html", "/sample-report.html")),
                ("site/locales/pt-br.html", "(em ingl&ecirc;s)",
                 ("/pricing.html", "/sample-report.html"))):
            text = (REPO / path).read_text(encoding="utf-8")
            for href in hrefs:
                pattern = re.compile(
                    r'<a href="' + re.escape(href) + r'"[^>]*>([^<]*)</a>')
                labels = pattern.findall(text)
                self.assertTrue(
                    any(cue in label for label in labels),
                    f"{path}: no link to {href} tells the reader the "
                    f"destination is in English. Found: {labels}")


if __name__ == "__main__":
    unittest.main()
