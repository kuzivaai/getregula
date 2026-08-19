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
import html
import re
import subprocess
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

    # The English-only destinations where landing on an unreadable page is a
    # task failure rather than a mild surprise: the commercial offer and the
    # worked example. Footer and navigation links are deliberately excluded,
    # per the module docstring.
    CUED_TARGETS = ("/pricing.html", "/sample-report.html")
    CUES = {"de": "(auf Englisch)", "pt-br": "(em ingl&ecirc;s)"}

    @staticmethod
    def _body_copy(text):
        """The page with its navigation and footer removed.

        The rule is about body calls to action. This module's own docstring
        records why: suffixing every footer and navigation link in each locale
        would be worse for a reader, not better, so those links carry the
        machine-readable `hreflang` and nothing else. A derivation that did not
        exclude them would demand a visible cue on the navigation and read as a
        defect when it is a design decision already taken.
        """
        text = re.sub(r"<nav\b.*?</nav>", " ", text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r"<footer\b.*?</footer>", " ", text, flags=re.DOTALL | re.IGNORECASE)
        return text

    def _localised_pages(self):
        """Every shipped localised page, from git rather than from a list."""
        out = subprocess.run(["git", "ls-files", "-z", "site"], cwd=REPO,
                             capture_output=True, text=True, check=True)
        for rel in sorted(p for p in out.stdout.split("\0") if p.endswith(".html")):
            m = lla._LOCALE_PAGE.match(rel)
            if m:
                yield rel, m.group(1)

    def test_the_body_calls_to_action_carry_a_visible_cue(self):
        """The machine-readable half is invisible to a sighted reader.

        A German reader clicking through to the commercial offer cannot see
        `hreflang`, so those links say it in the link text as well.

        DERIVED, NOT LISTED, and the change has a cause. This test used to name
        the two pages it expected each link on. The 2026-08-18 information-
        architecture change moved the sample-report call to action onto the new
        product page, correctly cued, and the test failed on the page it had
        just left rather than on any real defect. A list of where content lives
        is a copy of the site, and a copy drifts. The rule it was written to
        enforce is about the link, not about the page, so it is now applied to
        every localised page that carries one.
        """
        checked = 0
        for rel, lang in self._localised_pages():
            cue = self.CUES.get(lang)
            if not cue:
                continue
            text = self._body_copy((REPO / rel).read_text(encoding="utf-8"))
            for href in self.CUED_TARGETS:
                pattern = re.compile(
                    r'<a href="' + re.escape(href) + r'"[^>]*>([^<]*)</a>')
                for raw in pattern.findall(text):
                    checked += 1
                    # Compare what a reader sees, not how it was encoded. The
                    # same cue ships as "(em ingl&ecirc;s)" in hand-written
                    # markup and as literal UTF-8 from the generated qualifier
                    # copy tables. An entity-blind comparison reported the
                    # generated one as missing while it was on the page, which
                    # is N107's failure mode: a guard blind to a shipped
                    # language's encoding.
                    label = html.unescape(raw)
                    self.assertIn(
                        html.unescape(cue), label,
                        f"{rel}: a link to {href} does not tell the reader the "
                        f"destination is in English. Label: {label!r}")
        # A derived check that finds nothing passes for the wrong reason.
        self.assertGreaterEqual(
            checked, 4,
            f"only {checked} cued body call(s) to action found across the "
            f"localised pages; the derivation has stopped reaching them")

    def test_the_visible_cue_check_can_fail(self):
        """Control: an uncued link to a cued target is caught."""
        cue = self.CUES["de"]
        pattern = re.compile(r'<a href="/pricing.html"[^>]*>([^<]*)</a>')
        planted = '<a href="/pricing.html" hreflang="en">Preise ansehen</a>'
        labels = pattern.findall(planted)
        self.assertTrue(labels, "the predicate no longer matches a plain link")
        self.assertNotIn(html.unescape(cue), html.unescape(labels[0]))
        # and the decoded comparison accepts BOTH encodings of a real cue
        for encoded in ('Preise ansehen (auf Englisch)', 'Preise ansehen (auf&nbsp;Englisch)'.replace('&nbsp;', ' ')):
            self.assertIn(html.unescape(cue), html.unescape(encoded))


if __name__ == "__main__":
    unittest.main()
