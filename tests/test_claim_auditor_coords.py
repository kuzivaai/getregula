# regula-ignore
"""The claim auditor must report the line a claim is actually on.

Regression guard for a coordinate-drift defect: `strip_noise` blanked
inline-code spans with spaces, but the inline-code regex (`` `[^`]*` ``)
matches across line breaks. A span that wrapped lines therefore lost its
newlines, shifting every later reported line number up by one per wrapped
span — so the deeper a claim sat in a file, the further wrong its
coordinates were.

Why it matters enough to test: the auditor's output is a work order.
Wrong coordinates send whoever is clearing a finding to the wrong line,
and the cost repeats for every finding and every contributor.

These tests plant claims at known lines and require the auditor to report
exactly those lines and exactly those snippets.
"""

import shutil
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import claim_auditor as ca  # noqa: E402

# A number with no allowlist entry and no canonical meaning, so the claim
# is genuinely unsourced rather than exempted by an existing rule.
CLAIM_TEXT = "Regula ships 777 patterns."
CLAIM_SNIPPET = "777 patterns"


class _Fixture:
    """Writes a fixture inside the repo (the auditor rejects outside paths)."""

    def __init__(self, name, lines):
        self.dir = REPO / ".test_coords_tmp"
        self.dir.mkdir(exist_ok=True)
        self.path = self.dir / name
        self.path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        self.claim_line = next(
            i for i, l in enumerate(lines, start=1) if CLAIM_SNIPPET in l)

    def scan(self):
        return ca.scan_file(self.path, ca.load_allowlist())

    def cleanup(self):
        shutil.rmtree(self.dir, ignore_errors=True)


class TestReportedCoordinates(unittest.TestCase):
    def tearDown(self):
        shutil.rmtree(REPO / ".test_coords_tmp", ignore_errors=True)

    def _assert_exact(self, fx, why):
        report = fx.scan()
        matching = [f for f in report.findings
                    if CLAIM_SNIPPET in f.claim.snippet]
        self.assertEqual(
            len(matching), 1,
            f"{why}: expected exactly one finding for {CLAIM_SNIPPET!r}, "
            f"got {[(f.claim.line, f.claim.snippet) for f in report.findings]}")
        found = matching[0].claim
        self.assertEqual(
            found.line, fx.claim_line,
            f"{why}: auditor reported line {found.line} but the claim is on "
            f"line {fx.claim_line}. Wrong coordinates send contributors to "
            f"the wrong line.")
        self.assertIn(
            CLAIM_SNIPPET, found.snippet,
            f"{why}: reported snippet {found.snippet!r} does not contain the "
            f"planted claim text")

    def test_plain_file_reports_exact_line(self):
        fx = _Fixture("plain.md",
                      ["# Title"] + [f"filler {i}" for i in range(2, 10)]
                      + ["", CLAIM_TEXT, "", "tail"])
        self._assert_exact(fx, "plain file")

    def test_line_wrapping_inline_code_does_not_shift_coordinates(self):
        """The actual regression: a backtick span wrapping a line break."""
        lines = [
            "# Title", "",
            "Some prose with a `wrapped inline",
            "code span` that crosses a line break.", "",
            "More prose here.", "",
            CLAIM_TEXT, "",
            "tail",
        ]
        fx = _Fixture("wrapped.md", lines)
        self._assert_exact(fx, "wrapped inline-code span")

    def test_many_wrapped_spans_do_not_accumulate_drift(self):
        """Drift was cumulative — one line per wrapped span."""
        lines = ["# Title", ""]
        for i in range(6):
            lines += [f"Prose {i} with a `span that", "wraps` here.", ""]
        lines += [CLAIM_TEXT, "", "tail"]
        fx = _Fixture("many.md", lines)
        self._assert_exact(fx, "six wrapped spans")

    def test_strip_noise_preserves_line_count(self):
        """Root-cause guard, independent of any single fixture."""
        raw = (
            "# T\n\nprose `a\nb` more\n\n"
            "```\nfenced\nblock\n```\n\n"
            "<!-- a\ncomment -->\n\ntail\n"
        )
        cleaned = ca.strip_noise(raw, ".md")
        self.assertEqual(
            raw.count("\n"), cleaned.count("\n"),
            "strip_noise changed the line count; every reported coordinate "
            "after the altered region will be wrong")


if __name__ == "__main__":
    unittest.main()
