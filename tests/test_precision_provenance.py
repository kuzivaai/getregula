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
]

# Excluded with a stated reason each, never a blanket directory sweep.
EXCLUDED = {
    "docs/improvement": "programme finding record; quotes wrong numbers AS findings",
    ".claude/rules": "loaded rules; quote the figure as a worked example of the defect",
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


class TestPrecisionProvenance(unittest.TestCase):

    def test_every_published_83_5_carries_n_and_labeller_route(self):
        """FILE-level, deliberately, and here is the limit of that choice.

        An earlier draft checked every block that mentions the figure. That
        failed on table cells, code-sample comments and back-references
        inside files whose disclosure is two paragraphs away, which is noise
        rather than a defect.

        File level is sufficient to catch all five documented failures:
        site/about.html carried neither N nor the basis; docs/TRUST.md had N
        but no basis; docs/MODEL_CARD.md linked METHODOLOGY.json, which has
        no labeller field; and both exec summaries inherited TRUST.md's gap.

        What this does NOT catch: a bare figure in one corner of a long file
        whose disclosure sits far away. If that recurs, tighten to
        section-level rather than block-level.
        """
        # CHANGELOG.md is a historical release record, not a live claim.
        # strip_noise() already skips historical CHANGELOG sections for the
        # same reason. Excluded here with that reason, not silently.
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
            if not FIGURE.search(text):
                continue
            if not HAS_N.search(text):
                failures.append(f"{rel}: publishes 83.5% with no N=115 anywhere")
            if not HAS_LABELLER.search(text):
                failures.append(
                    f"{rel}: publishes 83.5% with no route to the "
                    f"single-reviewer disclosure")
        self.assertEqual(failures, [], "\n  " + "\n  ".join(failures))

    def test_no_unlisted_surface_publishes_the_figure(self):
        """A new surface must be added to KNOWN_SURFACES, which forces it
        through the check above rather than silently escaping it."""
        import subprocess
        # A file is a published surface only if it is TRACKED. Untracked
        # files are local scratch. Overstating scope by counting scratch is a
        # documented error of this programme; see .claude/rules/measurement.md.
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
