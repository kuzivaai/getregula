"""A citation must be TRACKED, not merely present on disk. Finding N1.

`paragraph_has_source` and `strip_noise` both accepted a file reference when
`(REPO_ROOT / ref).exists()`. That consults the working tree, so a gitignored
file counted as provenance on a developer's machine and was absent in CI. The
same commit scored 276 findings locally and 277 in a clean worktree.

`.claude/rules/measurement.md` rule 4b already establishes that untracked files
are not published surfaces, on the grounds that nobody outside the machine can
read them. A citation is held to the same bar: a reader cannot follow a
reference to a file that is not in the repository.

The discriminator under test is TRACKEDNESS, not existence. Every "must fail"
case below uses a file that genuinely EXISTS on disk at the moment of the
assertion, so the test cannot pass because the path was missing.

There are three call sites and one predicate. All three are covered:
  strip_noise  bare-span form     (`scripts/foo.py`)
  strip_noise  command form       (`scripts/foo.py --flag`)
  paragraph_has_source            file-ref arm
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import claim_auditor as ca  # noqa: E402

# A file that is definitely tracked, verified against git rather than assumed.
TRACKED_REF = "scripts/claim_auditor.py"


@pytest.fixture(scope="module")
def tracked_ref() -> str:
    out = subprocess.run(
        ["git", "ls-files", TRACKED_REF], cwd=REPO_ROOT,
        capture_output=True, text=True, check=True).stdout.strip()
    assert out == TRACKED_REF, (
        f"fixture precondition failed: {TRACKED_REF} is not tracked, so this "
        f"file cannot serve as the positive half of the contrast"
    )
    return TRACKED_REF


@pytest.fixture
def untracked_ref():
    """Create a real, untracked file inside the repo and remove it after.

    It must EXIST while the assertion runs, otherwise a 'not sourced' result
    would prove nothing about trackedness.
    """
    rel = "_n1_untracked_citation_fixture.md"
    path = REPO_ROOT / rel
    path.write_text("fixture for tests/test_tracked_citation.py\n",
                    encoding="utf-8")
    ca.tracked_paths.cache_clear()
    try:
        assert path.exists(), "fixture file was not created"
        listed = subprocess.run(
            ["git", "ls-files", rel], cwd=REPO_ROOT,
            capture_output=True, text=True, check=True).stdout.strip()
        assert listed == "", (
            f"fixture precondition failed: {rel} is tracked, so it cannot "
            f"serve as the negative half of the contrast"
        )
        yield rel
    finally:
        path.unlink(missing_ok=True)
        ca.tracked_paths.cache_clear()


# --------------------------------------------------------------------------
# paragraph_has_source: the file-ref arm
# --------------------------------------------------------------------------

# NOTE ON WORDING. These paragraphs deliberately avoid `source`, `see`, `ref`
# and the other CITATION_WORDS tokens. `citation-word` is tested at line 490 of
# claim_auditor.py and `file-ref` at line 499, first match wins, so a sentence
# containing "See" is sourced by the word and never reaches the file-ref arm.
# The first draft of this test used "See ..." and passed for that wrong reason.
# That masking is finding F25 and is still open.

def test_tracked_file_reference_is_a_source(tracked_ref):
    para = f"Precision is 83.5% on the random corpus, measured by {tracked_ref}."
    ok, reason = ca.paragraph_has_source(para)
    assert ok, f"a tracked reference must source the paragraph, got {reason}"
    assert reason.startswith("file-ref:"), (
        f"expected the file-ref arm to answer, got {reason!r}; if this says "
        f"'citation-word' the test sentence has picked up a CITATION_WORDS "
        f"token and is no longer testing what it claims to test"
    )


def test_untracked_file_reference_is_NOT_a_source(untracked_ref):
    """The N1 assertion. Fails before the fix, passes after."""
    para = f"Precision is 83.5% on the random corpus, measured by {untracked_ref}."
    ok, reason = ca.paragraph_has_source(para)
    assert not ok, (
        f"an UNTRACKED file must not source a paragraph, but the gate "
        f"accepted it with reason {reason!r}. The file exists on disk; that "
        f"is precisely the defect (N1)."
    )
    assert reason == "no-source", reason


def test_the_discriminator_is_trackedness_not_existence(tracked_ref,
                                                        untracked_ref):
    """Same construction, same shape, one tracked and one not.

    A single assertion in isolation could pass for the wrong reason. This
    contrast can only pass if trackedness is what the gate tests, because
    both files exist on disk at the moment of the assertion.
    """
    assert (REPO_ROOT / tracked_ref).exists()
    assert (REPO_ROOT / untracked_ref).exists()
    good = f"The figure is 41 items, measured by {tracked_ref}."
    bad = f"The figure is 41 items, measured by {untracked_ref}."
    ok_good, why_good = ca.paragraph_has_source(good)
    ok_bad, why_bad = ca.paragraph_has_source(bad)
    assert ok_good and why_good.startswith("file-ref:"), why_good
    assert not ok_bad and why_bad == "no-source", why_bad


def test_leading_dot_slash_is_normalised(untracked_ref):
    """`./x.yaml` and `x.yaml` are the same path; both must be untracked."""
    assert ca.ref_is_tracked(f"./{untracked_ref}") is False


def test_tracked_ref_with_leading_dot_slash_still_resolves(tracked_ref):
    assert ca.ref_is_tracked(f"./{tracked_ref}") is True


def test_path_escaping_the_repo_is_not_tracked():
    assert ca.ref_is_tracked("../etc/passwd.md") is False


# --------------------------------------------------------------------------
# strip_noise: both preservation arms
# --------------------------------------------------------------------------

def test_strip_noise_preserves_a_tracked_bare_span(tracked_ref):
    line = f"Development corpus precision (`{tracked_ref}`):"
    cleaned = ca.strip_noise(line, ".md")
    assert tracked_ref in cleaned, (
        f"a tracked bare span must survive strip_noise, got {cleaned!r}")


def test_strip_noise_blanks_an_untracked_bare_span(untracked_ref):
    line = f"Development corpus precision (`{untracked_ref}`):"
    cleaned = ca.strip_noise(line, ".md")
    assert untracked_ref not in cleaned, (
        f"an UNTRACKED bare span must be blanked, but survived: {cleaned!r}")


def test_strip_noise_preserves_a_tracked_command_span(tracked_ref):
    """The F32 form: a command that names a tracked file."""
    line = f"Measured with (`python3 {tracked_ref} --verify-facts`):"
    cleaned = ca.strip_noise(line, ".md")
    assert tracked_ref in cleaned, cleaned


def test_strip_noise_blanks_an_untracked_command_span(untracked_ref):
    line = f"Measured with (`python3 {untracked_ref} --verify-facts`):"
    cleaned = ca.strip_noise(line, ".md")
    assert untracked_ref not in cleaned, (
        f"an UNTRACKED command span must be blanked, but survived: {cleaned!r}")


# --------------------------------------------------------------------------
# Control: the tracked set must be real
# --------------------------------------------------------------------------

def test_control_tracked_set_is_populated_and_matches_git():
    """If this returned an empty set every citation would silently fail.

    Measurement rule 4: an absent signal is not a passing signal. A repo with
    zero tracked files is impossible, so an empty set means the loader broke,
    not that nothing is tracked.
    """
    paths = ca.tracked_paths()
    assert len(paths) > 100, f"tracked set implausibly small: {len(paths)}"
    expected = set(subprocess.run(
        ["git", "ls-files"], cwd=REPO_ROOT,
        capture_output=True, text=True, check=True).stdout.split())
    assert paths == frozenset(expected)


def test_source_does_not_resolve_citations_against_the_working_tree():
    """Anti-regression. The defect was a shape, so guard the shape.

    Reintroducing `(REPO_ROOT / ref).exists()` as a citation check would
    restore N1 silently: every test above would still pass, because they
    assert behaviour at three call sites and a fourth could be added.
    """
    src = (REPO_ROOT / "scripts" / "claim_auditor.py").read_text(
        encoding="utf-8")
    import re as _re
    # A backtick immediately before means the text is prose inside a
    # docstring or comment describing the old defect, not live code.
    offenders = _re.findall(
        r"(?<!`)\(REPO_ROOT\s*/\s*(?:ref|inner)[^)]*\)\.exists\(\)", src)
    assert offenders == [], (
        f"citation resolution must go through ref_is_tracked(), but found "
        f"{offenders}. See finding N1."
    )


def test_citation_resolution_never_consults_the_filesystem():
    """Tree independence, asserted at the predicate rather than the corpus.

    N1's property is that the auditor's verdict cannot depend on files
    absent from a clean checkout. Post-fix that holds by construction:
    `ref_is_tracked` reads the git index, so a gitignored file is invisible
    to it whether or not it sits on disk.

    An earlier draft of this test asserted something stronger and wrong:
    that no document anywhere cites an untracked path. That would force
    content churn in working documents for no benefit, and it conflated a
    content question with the apparatus question N1 is about. A working
    document citing a local scratch file SHOULD become an ordinary
    unsourced finding; it should not be special-cased.

    The empirical two-tree comparison that proves the property end to end
    is recorded in docs/improvement/LEDGER.md under N1, because it needs a
    second checkout and does not belong in the unit suite.
    """
    # A path that exists on disk but is not in the index must be rejected,
    # and the ONLY way to know that is to consult the index.
    existing_untracked = [
        p for p in ("docs/FULL_REVIEW.md", "regula-policy.yaml",
                    "AI_GOVERNANCE.md", "MODEL_CARD.md")
        if (REPO_ROOT / p).exists()
    ]
    if not existing_untracked:
        pytest.skip("no gitignored artefact present to discriminate against; "
                    "this machine cannot exercise the contrast")
    for rel in existing_untracked:
        assert (REPO_ROOT / rel).exists()
        assert ca.ref_is_tracked(rel) is False, (
            f"{rel} exists on disk and is NOT tracked, so it must not "
            f"resolve as a citation. If this passes on your machine and "
            f"fails in CI, N1 has regressed."
        )
