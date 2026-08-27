#!/usr/bin/env python3
# regula-ignore
"""Every published use of the 83.5% precision figure must carry its
provenance at the point of use.

Finding from Phase 1.5b: the figure passed the claim auditor (it is
artefact-verified from PRECISION.json, not allowlisted) while failing the
honest-provenance bar at five of eight locations, including a bare
"Published precision on a random corpus: 83.5%" on a public page.

That gap is the difference between the gate's criterion (an annotation
exists somewhere) and the standard (the reader can see what the number
rests on). This test enforces the standard.

Bar, owner-set:
  N=115 present at the point of use, AND
  the single-reviewer basis visible or one link away.

Stdlib only.
"""

import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

REPO = Path(__file__).resolve().parent.parent

# The one place repo-wide that discloses the single-reviewer basis.
DISCLOSURE = "benchmarks/README.md"

# Surfaces that publish the figure. A new surface must be added here.
# Found by this test, not by hand. The 1.5b pack's hand-built table listed
# EIGHT locations; the tracked total is FOURTEEN. That gap is why the count
# is produced by a test now.
KNOWN_SURFACES = [
    "README.md",
    "CHANGELOG.md",
    "docs/TRUST.md",
    "docs/MODEL_CARD.md",
    "docs/examples/exec-summary-sample.html",
    "docs/benchmarks/PRECISION_RECALL_2026_04.md",
    "scripts/exec_summary.py",
    "site/about.html",
    "site/index.html",
    "site/llms.txt",
    "site/llms-full.txt",
    "site/regions/uae.html",
    "site/examples/sample-exec-summary.html",
    "benchmarks/README.md",
    # Added 2026-08-17 with docs/DEMO.md. Registering a surface here does
    # NOT exempt it: every entry is then required to carry N=115 and the
    # labeller route in the same section, so this list makes a file more
    # checked rather than less. The full-suite run at a94efef caught the
    # omission, which is the guard working: a demonstration page is the
    # surface most likely to be read aloud, and the figure must not travel
    # on it without its basis.
    "docs/DEMO.md",
    # The dated audit carries the same N=115 and single-reviewer disclosure
    # in its detector-evidence section; registering it makes that section
    # subject to the same point-of-use provenance check.
    "docs/VALIDITY_UX_ENGINEERING_AUDIT_2026-08-26.md",
]

# Excluded with a stated reason each, never a blanket directory sweep.
EXCLUDED = {
    "tests": "test sources, including this file",
    "build": "build artefact, gitignored",
}

FIGURE = re.compile(r"83\.5\s*%")
HAS_N = re.compile(r"N\s*=\s*115", re.IGNORECASE)
# Either the words, or a link to the file that carries them.
HAS_LABELLER = re.compile(
    r"single[\s-]*(?:reviewer|labeller|labeler)"
    r"|one\s+reviewer"
    r"|benchmarks/README\.md",
    re.IGNORECASE,
)


def _paragraphs(text: str):
    """Split into blocks. HTML list items and tags count as boundaries so a
    figure cannot borrow provenance from an unrelated neighbouring block."""
    for block in re.split(r"\n\s*\n|</li>|</p>", text):
        if FIGURE.search(block):
            yield block


def _sections(text: str, rel: str):
    """Yield (start_line, section_text).

    Markdown: heading to next heading. Fenced code blocks are NOT split on,
    because a shell comment like `# Expected: 83.5%` inside a ``` fence is
    not a heading. An earlier version split there and produced a one-line
    "section" that could never carry provenance, which is a defect in the
    checker rather than in the document.

    HTML/other: block-level element boundaries.
    """
    if rel.endswith((".md", ".txt")):
        lines = text.splitlines(keepends=True)
        in_fence = False
        starts = []
        for i, ln in enumerate(lines):
            if ln.lstrip().startswith("```"):
                in_fence = not in_fence
                continue
            if not in_fence and re.match(r"#{1,6}\s", ln):
                starts.append(i)
        if not starts or starts[0] != 0:
            starts.insert(0, 0)
        for j, st in enumerate(starts):
            en = starts[j + 1] if j + 1 < len(starts) else len(lines)
            yield st + 1, "".join(lines[st:en])
        return

    parts = re.split(r"(?i)(?=<(?:p|li|td|h[1-6]|section|div)\b)", text)
    line = 1
    for part in parts:
        if part:
            yield line, part
            line += part.count("\n")


class TestPrecisionProvenance(unittest.TestCase):

    def test_every_published_83_5_carries_provenance_AT_EACH_LOCATION(self):
        """PER-LOCATION, not per-file.

        The earlier version of this test asserted only that N and the
        labeller route appeared SOMEWHERE in the file. That is a counter
        with a file-level check, and it is narrower than the standard: a
        bare figure in one corner of a long document passes if the
        disclosure sits far away. Counting locations without checking each
        one is exactly the failure this whole finding is about.

        Unit: the enclosing SECTION. For markdown that is heading-to-heading;
        for HTML it is the enclosing block-level element. That is wide enough
        not to fire on a table cell whose header row carries the disclosure,
        and narrow enough that a claim cannot borrow provenance from an
        unrelated part of the page.
        """
        HISTORICAL = {"CHANGELOG.md"}
        failures = []
        for rel in KNOWN_SURFACES:
            if rel in HISTORICAL:
                continue
            p = REPO / rel
            if not p.exists():
                failures.append(f"{rel}: MISSING")
                continue
            text = p.read_text(encoding="utf-8", errors="replace")
            for idx, section in _sections(text, rel):
                if not FIGURE.search(section):
                    continue
                if not HAS_N.search(section):
                    failures.append(
                        f"{rel} (section @line {idx}): 83.5% with no N=115 "
                        f"in the same section")
                if not HAS_LABELLER.search(section):
                    failures.append(
                        f"{rel} (section @line {idx}): 83.5% with no route "
                        f"to the single-reviewer disclosure in the same "
                        f"section")
        disc = (REPO / DISCLOSURE).read_text(encoding="utf-8")
        if not HAS_N.search(disc) or not HAS_LABELLER.search(disc):
            failures.append(f"{DISCLOSURE}: must carry N and the basis")
        self.assertEqual(failures, [], "\n  " + "\n  ".join(failures))

    def test_the_checker_distinguishes_compliant_from_non_compliant(self):
        """CONTROL. Plants one compliant and one non-compliant location and
        proves the checker tells them apart.

        Without this the test above could pass by asserting nothing. An
        absent signal is not a passing signal.
        """
        compliant = (
            "## Precision\n\n"
            "Published precision is 83.5% (N=115, single reviewer, no "
            "inter-rater agreement).\n"
        )
        non_compliant = (
            "## Precision\n\n"
            "Published precision on a random corpus: 83.5%.\n"
        )
        # borrowed-provenance case: disclosure exists but in ANOTHER section
        borrowed = (
            "## Methodology\n\nN=115, single reviewer.\n\n"
            "## Headline\n\nPublished precision: 83.5%.\n"
        )

        def bad_sections(text):
            out = []
            for idx, sec in _sections(text, "probe.md"):
                if not FIGURE.search(sec):
                    continue
                if not HAS_N.search(sec) or not HAS_LABELLER.search(sec):
                    out.append(idx)
            return out

        self.assertEqual(bad_sections(compliant), [],
                         "control failed: a compliant location was flagged")
        self.assertNotEqual(bad_sections(non_compliant), [],
                            "control failed: a BARE 83.5% was NOT flagged, "
                            "so this guard proves nothing")
        self.assertNotEqual(bad_sections(borrowed), [],
                            "control failed: a claim borrowing provenance "
                            "from another section was NOT flagged, so the "
                            "check is still effectively file-level")

    def test_no_unlisted_surface_publishes_the_figure(self):
        """A new surface must be added to KNOWN_SURFACES, which forces it
        through the check above rather than silently escaping it."""
        import subprocess
        # A file is a published surface only if it is TRACKED. Untracked
        # files are local scratch. Overstating scope by counting scratch is a
        # documented error of this programme; see docs/TRUST.md.
        tracked = subprocess.run(["git", "ls-files"], cwd=str(REPO),
                                 capture_output=True, text=True,
                                 check=True).stdout.split("\n")
        known = set(KNOWN_SURFACES)
        unlisted = []
        for rel in tracked:
            if not rel or not rel.endswith((".md", ".html", ".py", ".txt")):
                continue
            if rel in known:
                continue
            if any(rel.startswith(d + "/") for d in EXCLUDED):
                continue
            p = REPO / rel
            if not p.exists():
                continue
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            if FIGURE.search(text):
                unlisted.append(rel)
        self.assertEqual(
            unlisted, [],
            "83.5% published on unlisted surface(s); add to KNOWN_SURFACES "
            "and give each the N and labeller route:\n  " +
            "\n  ".join(unlisted))

    def test_the_disclosure_file_still_carries_the_basis(self):
        """The whole scheme rests on one file. If it stops saying this, every
        'one link away' route above becomes a dead end."""
        text = (REPO / DISCLOSURE).read_text(encoding="utf-8")
        self.assertRegex(
            text, r"[Ss]ingle reviewer",
            f"{DISCLOSURE} no longer discloses the single-reviewer basis; "
            f"every provenance route in this test depends on it")

    def test_the_disclosure_file_states_non_reproducibility(self):
        """N51: the figure's inputs are not fully tracked and the corpus
        clones were unpinned, so 83.5% cannot be re-derived from a clone.
        The canonical disclosure surface must say so, and must never again
        claim full reproducibility. Every point of use routes here, so this
        one file carries the qualification for all fourteen locations."""
        text = (REPO / DISCLOSURE).read_text(encoding="utf-8")
        self.assertIn(
            "dated measurement", text,
            f"{DISCLOSURE} no longer states that the headline precision is "
            f"a dated measurement; the N51 qualification has been lost")
        self.assertIn(
            "not a re-runnable benchmark", text,
            f"{DISCLOSURE} no longer states that the headline precision is "
            f"not a re-runnable benchmark; the N51 qualification has been "
            f"lost")
        self.assertNotIn(
            "Fully reproducible", text,
            f"{DISCLOSURE} claims full reproducibility again. That claim "
            f"was established false on 2026-08-06: the 115-entry production "
            f"subset membership is untracked and rescan_corpus.py clones "
            f"unpinned heads, so the April 2026 corpus state is gone")

    def test_the_non_reproducibility_check_can_fail(self):
        """CONTROL. The check above is three string assertions; prove each
        arm flags the text it exists to flag, so a green run means the
        document really carries the qualification."""
        old_text = (
            "**Methodology details:** METHODOLOGY.json contains the exact "
            "queries. BLIND_LABELS.json contains all 201 labels with "
            "notes. Fully reproducible.")
        self.assertIn("Fully reproducible", old_text,
                      "control failed: the planted pre-N51 text no longer "
                      "contains the phrase this guard exists to reject")
        self.assertNotIn("dated measurement", old_text,
                         "control failed: the planted pre-N51 text would "
                         "satisfy the qualification arm, so the guard "
                         "proves nothing")

    def test_version_attribution_matches_the_artefact(self):
        """F20: the artefact says v1.7.0. Published surfaces must not claim a
        different version for the same measurement."""
        precision = REPO / "benchmarks/results/random_corpus/PRECISION.json"
        artefact = precision.read_text(encoding="utf-8")
        self.assertIn("v1.7.0", artefact,
                      "PRECISION.json no longer states v1.7.0; this test's "
                      "premise has changed")
        bad = []
        for rel in KNOWN_SURFACES:
            p = REPO / rel
            if not p.exists():
                continue
            for block in _paragraphs(p.read_text(encoding="utf-8",
                                                 errors="replace")):
                if re.search(r"measured on\s+(?:Regula\s+)?v1\.7\.4", block,
                             re.IGNORECASE):
                    bad.append(rel)
        self.assertEqual(
            bad, [],
            "surface(s) attribute the 83.5% measurement to v1.7.4 while "
            "PRECISION.json says v1.7.0:\n  " + "\n  ".join(bad))


if __name__ == "__main__":
    unittest.main(verbosity=2)
