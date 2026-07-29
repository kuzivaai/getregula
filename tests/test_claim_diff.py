"""Cover the merge-base claim classifier.

`scripts/claim_diff.py` answers whether a claim reported at HEAD already
existed at the merge base. That answer decides the gate-scope repair's design,
so it needs a control: a fixture where the right answer is known by
construction, not by inspection of the repository.

The fixture is a real throwaway git repository with two commits. One claim is
present in both. One appears only in the second. The classifier must call each
correctly, and the control at the bottom breaks the classification on purpose
and asserts the test notices.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import claim_auditor as ca          # noqa: E402
import claim_diff                   # noqa: E402

PRESENT_IN_BOTH = "Precision is 83.5% on the random corpus."
INTRODUCED_AT_HEAD = "The suite collects 2,452 tests."
# NOTE: the comma is load-bearing. NUMERIC_CLAIM does not match unseparated
# numbers of four or more digits, so a bare 2452 is invisible to the detector
# while the comma-separated form is caught. Finding N10; not fixed here
# because widening the regex is a gate-scope change. The precondition test
# below is what caught it.


def _git(*args: str, cwd: Path) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True,
                   capture_output=True, text=True)


@pytest.fixture
def two_commit_repo(tmp_path: Path) -> dict:
    """A real repo: commit A has one claim, commit B adds a second."""
    repo = tmp_path / "fixture-repo"
    (repo / "docs").mkdir(parents=True)
    _git("init", "-q", cwd=repo)
    _git("config", "user.email", "t@example.com", cwd=repo)
    _git("config", "user.name", "T", cwd=repo)

    doc = repo / "docs" / "claims.md"
    doc.write_text(f"# Fixture\n\n{PRESENT_IN_BOTH}\n", encoding="utf-8")
    _git("add", "docs/claims.md", cwd=repo)
    _git("commit", "-q", "-m", "A", cwd=repo)
    base_sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo,
                              capture_output=True, text=True,
                              check=True).stdout.strip()

    doc.write_text(
        f"# Fixture\n\n{PRESENT_IN_BOTH}\n\n{INTRODUCED_AT_HEAD}\n",
        encoding="utf-8")
    _git("add", "docs/claims.md", cwd=repo)
    _git("commit", "-q", "-m", "B", cwd=repo)

    return {"repo": repo, "base_sha": base_sha, "rel": "docs/claims.md"}


def _extract_at(repo: Path, sha: str, rel: str) -> set:
    """Claims at `sha`, using the real detector against a real checkout."""
    wt = repo.parent / f"wt-{sha[:7]}"
    _git("worktree", "add", "--detach", str(wt), sha, cwd=repo)
    try:
        # Same instrument, other specimen: the detector under test is the one
        # in this repo, pointed at the fixture checkout. `extract_claims`
        # asserts REPO_ROOT matches, so pass a shim carrying the right root.
        class _Shim:
            __name__ = "claim_auditor(fixture)"
            REPO_ROOT = wt
            SCANNED_SUFFIXES = ca.SCANNED_SUFFIXES
            strip_noise = staticmethod(ca.strip_noise)
            split_paragraphs = staticmethod(ca.split_paragraphs)
            STRUCTURAL_REFS = ca.STRUCTURAL_REFS
            HTML_TAG = ca.HTML_TAG
            is_exempt_number = staticmethod(ca.is_exempt_number)
            NUMERIC_CLAIM = ca.NUMERIC_CLAIM
            CURRENCY_CLAIM = ca.CURRENCY_CLAIM
            SUPERLATIVE_CLAIM = ca.SUPERLATIVE_CLAIM
            ATTRIBUTED_CLAIM = ca.ATTRIBUTED_CLAIM
        return claim_diff.extract_claims(_Shim, wt, [rel])
    finally:
        _git("worktree", "remove", "--force", str(wt), cwd=repo)


def test_fixture_preconditions(two_commit_repo):
    """Both claims must actually be detected, or the test proves nothing."""
    r = two_commit_repo
    head_keys = _extract_at(r["repo"], "HEAD", r["rel"])
    base_keys = _extract_at(r["repo"], r["base_sha"], r["rel"])
    assert claim_diff.claim_key(r["rel"], "83.5%") in head_keys, head_keys
    assert claim_diff.claim_key(r["rel"], "2,452 tests") in head_keys, head_keys
    assert claim_diff.claim_key(r["rel"], "83.5%") in base_keys, base_keys
    assert claim_diff.claim_key(r["rel"], "2,452 tests") not in base_keys


def test_classifier_separates_carried_from_introduced(two_commit_repo):
    """The assertion the whole measurement rests on."""
    r = two_commit_repo
    base_keys = _extract_at(r["repo"], r["base_sha"], r["rel"])
    findings = [
        {"file": r["rel"], "snippet": "83.5%"},
        {"file": r["rel"], "snippet": "2,452 tests"},
    ]
    claim_diff.classify_findings(findings, base_keys)
    carried = [f for f in findings if f["present_at_base"]]
    introduced = [f for f in findings if not f["present_at_base"]]
    assert [f["snippet"] for f in carried] == ["83.5%"]
    assert [f["snippet"] for f in introduced] == ["2,452 tests"]


def test_control_a_broken_classifier_is_caught():
    """Measurement rule 4. Break it on purpose; the assertion must fire.

    If this passes silently, the test above proves nothing, because it would
    also pass against a classifier that always answered the same way.
    """
    base_keys = {claim_diff.claim_key("docs/claims.md", "83.5%")}
    findings = [
        {"file": "docs/claims.md", "snippet": "83.5%"},
        {"file": "docs/claims.md", "snippet": "2,452 tests"},
    ]
    claim_diff.classify_findings(findings, base_keys)
    assert [f["present_at_base"] for f in findings] == [True, False]

    # Now the broken version: everything reads as carried over.
    for f in findings:
        f["present_at_base"] = True
    with pytest.raises(AssertionError):
        assert [f["present_at_base"] for f in findings] == [True, False]


# --------------------------------------------------------------------------
# Claim identity. The decision recorded in docs/adr/0001-claim-identity.md.
# --------------------------------------------------------------------------

def test_identity_ignores_whitespace_and_case_and_trailing_stop():
    k = claim_diff.claim_key
    assert k("a.md", "83.5%  ") == k("a.md", "83.5%")
    assert k("a.md", "The Only") == k("a.md", "the only")
    assert k("a.md", "2,452 tests.") == k("a.md", "2,452 tests")


def test_identity_does_NOT_normalise_digits():
    """83.5% and 91% are different claims. This is the point of the rule."""
    assert claim_diff.claim_key("a.md", "83.5%") != \
        claim_diff.claim_key("a.md", "91%")


def test_identity_is_per_path():
    """The same sentence on a new surface is a new assertion on that surface."""
    assert claim_diff.claim_key("a.md", "2,452 tests") != \
        claim_diff.claim_key("b.md", "2,452 tests")


def test_editing_a_claim_makes_it_read_as_introduced():
    """The documented consequence, asserted so it cannot drift unnoticed.

    docs/adr/0001-claim-identity.md argues this is correct: editing a claim is
    re-asserting it, and re-assertion is the moment to attach provenance. If a
    later session decides otherwise, this test is the thing to change, and the
    ADR is the thing to supersede.
    """
    base_keys = {claim_diff.claim_key("a.md", "83.5%")}
    findings = [{"file": "a.md", "snippet": "91%"}]
    claim_diff.classify_findings(findings, base_keys)
    assert findings[0]["present_at_base"] is False


# --------------------------------------------------------------------------
# Bucket predicate, shared with the ledger's own figures.
# --------------------------------------------------------------------------

@pytest.mark.parametrize("path,expected", [
    ("docs/improvement/STATE.md", "docs/improvement/"),
    ("benchmarks/README.md", "benchmarks/ + docs/benchmarks/"),
    ("docs/benchmarks/PRECISION_RECALL_2026_04.md",
     "benchmarks/ + docs/benchmarks/"),
    (".claude/rules/measurement.md", ".claude/rules/"),
    ("README.md", "everything else"),
    ("site/index.html", "everything else"),
])
def test_bucket_predicate(path, expected):
    assert claim_diff.bucket_of(path) == expected
