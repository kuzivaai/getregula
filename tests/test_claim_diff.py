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
from collections import Counter
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
    base_keys = Counter({claim_diff.claim_key("docs/claims.md", "83.5%"): 1})
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
    base_keys = Counter({claim_diff.claim_key("a.md", "83.5%"): 1})
    findings = [{"file": "a.md", "snippet": "91%"}]
    claim_diff.classify_findings(findings, base_keys)
    assert findings[0]["present_at_base"] is False


# --------------------------------------------------------------------------
# The N37 ordinal class, audited across the programme on 2026-07-30.
#
# N37 was a comparison whose KEY was coarser than the UNIT it resolved to:
# a finding key with the line dropped, differenced to pick out one occurrence
# among several, giving a correct total of 70 and a wrong attribution (the
# difference resolved to line 213 while the finding revealed was at line 210).
#
# `classify_findings` carried the same root cause in a different shape. Its
# key also drops the line, and it compared a SET, so multiplicity was lost
# rather than position. These tests are the shape of the 210/213 case: two
# occurrences of one claim string in one file, where the comparison must not
# collapse them. A count-only check cannot catch this class, so every
# assertion below is about attribution and about which occurrence carries it.
# --------------------------------------------------------------------------

def test_a_second_occurrence_of_a_base_claim_is_introduced_not_inherited():
    """The defect, in the 210/213 shape. Set membership answered 0 introduced.

    Base has the claim ONCE. Head has it TWICE. Exactly one occurrence is new.
    A set says "the key is present at base" for both and the introduced
    occurrence disappears from the bucket the merge gate reads.
    """
    base = Counter({claim_diff.claim_key("a.md", "43%"): 1})
    findings = [
        {"file": "a.md", "line": 210, "snippet": "43%", "occurrence": 1},
        {"file": "a.md", "line": 213, "snippet": "43%", "occurrence": 2},
    ]
    claim_diff.classify_findings(findings, base)
    introduced = [f for f in findings if not f["present_at_base"]]
    assert len(introduced) == 1, [
        (f["line"], f["present_at_base"]) for f in findings]
    assert introduced[0]["line"] == 213, "the declared tie-break is the TAIL"
    assert all(f["present_at_base_ambiguous"] for f in findings), (
        "base>0 and head>base: which occurrence is new is undecidable from "
        "counts and the record must say so")
    print("✓ a second occurrence of a base claim reads as introduced")


def test_the_surplus_is_the_tail_and_the_ambiguity_is_declared():
    """Three at head against two at base: one new, and it is not guessed at."""
    base = Counter({claim_diff.claim_key("a.md", "43%"): 2})
    findings = [
        {"file": "a.md", "line": 10, "snippet": "43%", "occurrence": 1},
        {"file": "a.md", "line": 20, "snippet": "43%", "occurrence": 2},
        {"file": "a.md", "line": 30, "snippet": "43%", "occurrence": 3},
    ]
    claim_diff.classify_findings(findings, base)
    assert [f["present_at_base"] for f in findings] == [True, True, False]
    assert all(f["present_at_base_ambiguous"] for f in findings)
    print("✓ the surplus is the tail, and the tie-break is flagged, not hidden")


def test_an_unambiguous_group_is_not_flagged_ambiguous():
    """A flag that is always on carries no information. Both directions pinned."""
    absent = Counter()
    findings = [
        {"file": "a.md", "line": 10, "snippet": "43%", "occurrence": 1},
        {"file": "a.md", "line": 20, "snippet": "43%", "occurrence": 2},
    ]
    claim_diff.classify_findings(findings, absent)
    assert [f["present_at_base"] for f in findings] == [False, False]
    assert not any(f["present_at_base_ambiguous"] for f in findings), (
        "base 0 means every occurrence is new; nothing is undecidable")

    covered = Counter({claim_diff.claim_key("b.md", "43%"): 5})
    more = [{"file": "b.md", "line": 10, "snippet": "43%", "occurrence": 1}]
    claim_diff.classify_findings(more, covered)
    assert more[0]["present_at_base"] is True
    assert more[0]["present_at_base_ambiguous"] is False
    print("✓ the ambiguity flag is off where nothing is ambiguous")


def test_the_tie_break_is_document_order_not_list_order():
    """Stable under reordering, so the answer does not depend on scan order."""
    base = Counter({claim_diff.claim_key("a.md", "43%"): 1})
    shuffled = [
        {"file": "a.md", "line": 213, "snippet": "43%", "occurrence": 2},
        {"file": "a.md", "line": 210, "snippet": "43%", "occurrence": 1},
    ]
    claim_diff.classify_findings(shuffled, base)
    by_line = {f["line"]: f["present_at_base"] for f in shuffled}
    assert by_line == {210: True, 213: False}, by_line
    print("✓ the tie-break follows document order, not the input list order")


def test_classify_findings_refuses_a_set_rather_than_coercing_it():
    """A set is the defect. Coercing it would be a different wrong answer."""
    with pytest.raises(TypeError) as exc:
        claim_diff.classify_findings(
            [{"file": "a.md", "line": 1, "snippet": "43%"}],
            {claim_diff.claim_key("a.md", "43%")})
    assert "multiset" in str(exc.value), exc.value
    print("✓ a set is refused, with the reason, rather than silently accepted")


def test_extract_claims_returns_a_multiset_that_counts_repeats(tmp_path):
    """The base side must count, not collapse. Measured on a real scan."""
    doc = tmp_path / "a.md"
    doc.write_text(
        "The figure is 43% here.\n\nAnd the figure is 43% again here.\n",
        encoding="utf-8")

    class _Shim:
        pass
    for name in ("SCANNED_SUFFIXES", "strip_noise", "split_paragraphs",
                 "STRUCTURAL_REFS", "HTML_TAG", "NUMERIC_CLAIM",
                 "CURRENCY_CLAIM", "SUPERLATIVE_CLAIM", "ATTRIBUTED_CLAIM",
                 "is_exempt_number"):
        setattr(_Shim, name, getattr(ca, name))
    _Shim.REPO_ROOT = tmp_path
    _Shim.__name__ = "shim"

    counts = claim_diff.extract_claims(_Shim, tmp_path, ["a.md"])
    assert isinstance(counts, Counter), type(counts)
    key = claim_diff.claim_key("a.md", "43%")
    assert counts[key] == 2, dict(counts)
    print("✓ extract_claims counts repeated occurrences instead of collapsing")


def test_gate_probe_keys_stay_split_by_question():
    """The N37 fix itself, re-asserted here so this audit has one home.

    `finding_key` is same-tree and MUST carry the line; `content_signature` is
    cross-commit and MUST NOT carry any coordinate. Collapsing them back into
    one key is what produced the 210-versus-213 misattribution.
    """
    import gate_probe as gp
    a = {"file": "a.md", "line": 210, "kind": "numeric",
         "snippet": "43%", "occurrence": 1}
    b = dict(a, line=213, occurrence=2)
    assert gp.finding_key(a) != gp.finding_key(b), "same-tree key lost the line"
    assert gp.content_signature(a) == gp.content_signature(b), (
        "cross-commit signature grew a coordinate and is now unstable")
    print("✓ the two keys remain split by the question they answer")


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


# ---------------------------------------------------------------------------
# --blocker-delta: what did a commit add to the merge blocker?
# ---------------------------------------------------------------------------
# The blocker read 274 unsourced at f2de2ff and 279 at 2c1f080 and nothing said
# which five appeared. These cover the reporting path with doctored records, so
# the arithmetic is proved without checking out two worktrees on every run.


def _delta(added=(), removed=(), older_total=10, newer_total=10) -> dict:
    return {
        "older": "a" * 40, "older_tree": "b" * 40, "older_total": older_total,
        "older_corpus": 1, "older_scanned": 1,
        "newer": "c" * 40, "newer_tree": "d" * 40, "newer_total": newer_total,
        "newer_corpus": 1, "newer_scanned": 1,
        "added": list(added), "removed": list(removed),
        "added_occurrences": sum(r["count"] for r in added),
        "removed_occurrences": sum(r["count"] for r in removed),
        "net": newer_total - older_total,
        "carried_instrument": [],
    }


def _row(file="x.md", snippet="5%", count=1, was=0, now=1, lines=(9,)):
    return {"file": file, "kind": "numeric", "snippet": snippet,
            "count": count, "was": was, "now": now, "lines": list(lines),
            "lines_older": [] if was == 0 else list(lines),
            "lines_newer": list(lines), "ambiguous": was > 0}


def test_blocker_delta_report_reconciles_added_removed_and_net():
    lines: list[str] = []
    claim_diff.report_blocker_delta(
        _delta(added=[_row()], older_total=10, newer_total=11), lines.append)
    assert any("findings added to the blocker: 1" in ln for ln in lines), lines
    assert any("net movement, as added minus removed: 1" in ln
               for ln in lines), lines


def test_blocker_delta_report_refuses_a_net_its_rows_do_not_account_for():
    """Control: the net must equal added minus removed, or nothing prints."""
    bad = _delta(added=[_row()], older_total=10, newer_total=99)
    with pytest.raises(claim_diff.TotalMismatch) as exc:
        claim_diff.report_blocker_delta(bad, lambda _l: None)
    assert "net movement" in str(exc.value), exc.value


def test_blocker_delta_report_refuses_an_added_total_its_files_miss():
    bad = _delta(added=[_row()], older_total=10, newer_total=11)
    bad["added_occurrences"] = 7
    with pytest.raises(claim_diff.TotalMismatch):
        claim_diff.report_blocker_delta(bad, lambda _l: None)


def test_a_signature_that_already_existed_is_reported_as_ambiguous():
    """Identical claim text repeated in one file cannot be told apart.

    Reporting a confident line number for it would be a fabricated attribution.
    The row says so and prints both sides instead.
    """
    lines: list[str] = []
    row = _row(was=1, now=2, lines=(5, 336))
    claim_diff.report_blocker_delta(
        _delta(added=[row], older_total=10, newer_total=11), lines.append)
    assert any("AMBIGUOUS" in ln for ln in lines), lines
    assert any("was 1x at [5, 336]" in ln or "was 1x at" in ln
               for ln in lines), lines


def test_content_signature_is_what_the_delta_keys_on():
    """Lines move between commits; the signature must not depend on them."""
    a = {"file": "d.md", "line": 5, "kind": "superlative", "snippet": "the only"}
    b = {"file": "d.md", "line": 336, "kind": "superlative",
         "snippet": "The Only"}
    assert claim_diff.content_signature(a) == claim_diff.content_signature(b)
