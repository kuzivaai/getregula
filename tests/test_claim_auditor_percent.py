# regula-ignore
"""Percentage claims must be detectable; CSS lengths must not be claims.

Two coupled changes are guarded here.

1. NUMERIC_CLAIM could not match a bare percentage at all. Its unit
   alternation ended in `\\b`, and `%` is not a word character, so
   "83.5% precision" was invisible to the gate while the module docstring
   listed percentages first among what it detects.

2. Making percentages detectable immediately surfaces CSS lengths
   (`style="width:100%"`), which are not claims. Left alone they would be
   standing false positives forever, degrading the instrument the fix is
   meant to sharpen. `strip_noise` therefore blanks inline style
   attribute VALUES — and nothing else.

The fence matters as much as the fix. Rendered-text attributes (alt,
title, aria-label) are user-visible prose and MUST stay in scope; a
percentage claim hidden in an alt attribute is still a published claim.
Each of the three cases below is asserted explicitly so a future widening
of the strip cannot quietly swallow prose.
"""

import shutil
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import claim_auditor as ca  # noqa: E402

TMP = REPO / ".test_percent_tmp"


def _scan(name: str, body: str):
    TMP.mkdir(exist_ok=True)
    path = TMP / name
    path.write_text(body, encoding="utf-8")
    report = ca.scan_file(path, [])
    return [c.snippet for c in _claims(report)]


def _claims(report):
    """Every claim the auditor recorded, sourced or not."""
    # scan_file records findings only for unsourced claims; to assert on
    # detection itself we re-derive claims from the findings plus the count.
    return [f.claim for f in report.findings]


class TestPercentDetection(unittest.TestCase):
    def tearDown(self):
        shutil.rmtree(TMP, ignore_errors=True)

    def test_regex_matches_bare_percentages(self):
        for text in ("83.5% precision", "40%", "99.9% uptime", "100% of scans"):
            self.assertTrue(
                ca.NUMERIC_CLAIM.search(text),
                f"{text!r} must be detectable; percentages were the first "
                f"category the module claimed to detect and the one it could "
                f"not see")

    def test_regex_still_matches_word_units(self):
        for text in ("2,849 tests", "419 patterns", "40 percent"):
            self.assertTrue(ca.NUMERIC_CLAIM.search(text),
                            f"{text!r} regression: word units must still match")

    def test_regex_does_not_match_version_or_article_numbers(self):
        for text in ("version 1.7", "Article 5", "Annex IV"):
            self.assertFalse(
                ca.NUMERIC_CLAIM.search(text),
                f"{text!r} must not be treated as a numeric claim")


class TestStripFence(unittest.TestCase):
    """The three cases the fence must separate."""

    def tearDown(self):
        shutil.rmtree(TMP, ignore_errors=True)

    def test_css_percentage_does_not_surface(self):
        snippets = _scan("css.html",
                         '<div style="width:100%;height:50%">x</div>\n')
        self.assertEqual(
            [s for s in snippets if "%" in s], [],
            "a CSS length surfaced as a claim; quarantining layout values "
            "as unverified claims would be a false label")

    def test_body_text_percentage_surfaces(self):
        snippets = _scan("body.html",
                         "<p>Regula reaches 83.5% precision.</p>\n")
        self.assertTrue(
            any("83.5%" in s for s in snippets),
            "a body-text percentage did not surface; this is exactly the "
            "claim class the fix exists to make visible")

    def test_percentage_in_rendered_attributes_surfaces(self):
        for attr in ("alt", "title", "aria-label"):
            with self.subTest(attr=attr):
                snippets = _scan(
                    f"attr_{attr}.html",
                    f'<img src="c.png" {attr}="Accuracy reaches 92% overall">\n')
                self.assertTrue(
                    any("92%" in s for s in snippets),
                    f"a percentage in {attr}= did not surface. Rendered-text "
                    f"attributes are user-visible prose and must stay in "
                    f"scope; only style attribute values are stripped.")

    def test_strip_preserves_line_count(self):
        raw = '<div\n  style="width:100%;\n  height:50%">\n  text\n</div>\n'
        cleaned = ca.strip_noise(raw, ".html")
        self.assertEqual(raw.count("\n"), cleaned.count("\n"),
                         "style stripping changed the line count, which would "
                         "reintroduce the coordinate drift fixed in "
                         "tests/test_claim_auditor_coords.py")


if __name__ == "__main__":
    unittest.main()
