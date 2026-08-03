# regula-ignore
"""Guard `scripts/gate_probe.py`, the probe every gate measurement shares.

WHY THIS EXISTS
---------------
Three pieces of machinery were extracted into `gate_probe` on 2026-07-30 so
that `f25_exposure` (this branch's working tree), `merge_blockers` (a clean
worktree of `main`) and `claim_diff` (two commits) all ask their questions with
one predicate. The whole benefit of that is lost if the shared piece is wrong,
so the properties the callers depend on are pinned here rather than in any one
caller's test file.

WHAT IS PINNED
--------------
- the off-switch really matches nothing, and every caller holds the SAME object
- the same-tree key includes the line, and the cross-commit signature does not
- `findings_over` counts occurrences the way the auditor's own list does
- `enumerate_revealed` reconciles against an INDEPENDENTLY counted total, and
  refuses a finding it cannot join to a citation-word paragraph

THE KEY DEFECT THIS FILE EXISTS TO PREVENT RECURRING
----------------------------------------------------
A first draft dropped the line from the same-tree key so one key could serve
both comparisons. That made the occurrence ordinal positionally unstable: when
the arm-off pass adds a finding EARLIER in a file, every later identical
snippet shifts ordinal, and the set difference returns the tail of the list
rather than the findings actually revealed. Measured on
`site/guides/eu-ai-act-recruitment-hiring.html` at `main`: `43%` yields one
finding with the arm on (line 213) and two with it off (lines 210 and 213), and
the keyless difference resolved to line 213, an unsourced paragraph, while the
finding actually revealed is line 210. The count stayed right and the
attribution went wrong.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import claim_auditor as ca          # noqa: E402
import claim_diff                   # noqa: E402
import f25_exposure as fx           # noqa: E402
import gate_probe as gp             # noqa: E402
import merge_blockers as mb         # noqa: E402


def test_every_caller_shares_one_off_switch_object():
    """Not "equal patterns": the same object. Two copies would drift."""
    assert fx.NEVER is gp.ARM_OFF
    assert mb.ARM_OFF is gp.ARM_OFF
    for text in ("", "see", "source: x", "reference", "cf.", "verdict:", "x"):
        assert not gp.ARM_OFF.search(text), text
    print("✓ one off-switch object, shared by every caller, matching nothing")


def test_every_caller_shares_one_reconciler():
    """`reconcile` had to leave merge_blockers to be reachable from claim_diff."""
    assert mb.reconcile is gp.reconcile
    assert fx.reconcile is gp.reconcile
    assert claim_diff.reconcile is gp.reconcile
    assert mb.TotalMismatch is gp.TotalMismatch is fx.TotalMismatch
    print("✓ one reconciler and one TotalMismatch across all three callers")


def test_the_same_tree_key_includes_the_line_and_the_signature_does_not():
    """The measured defect, pinned as a property rather than as prose."""
    a = {"file": "p.html", "line": 210, "kind": "numeric", "snippet": "43%",
         "occurrence": 0}
    b = {"file": "p.html", "line": 213, "kind": "numeric", "snippet": "43%",
         "occurrence": 0}
    assert gp.finding_key(a) != gp.finding_key(b), (
        "the same claim text on two different lines of one file must be two "
        "different findings when comparing two arm states over one tree; "
        "collapsing them is what mis-attributed line 210 to line 213")
    assert gp.content_signature(a) == gp.content_signature(b), (
        "across commits the line is not identity, because an insertion above a "
        "finding moves it without changing it")
    print("✓ same-tree key separates lines; cross-commit signature does not")


def test_the_ordinal_still_separates_repeats_on_one_line():
    """The 267-versus-273 undercount, which the line alone does not fix."""
    a = {"file": "d.md", "line": 22, "kind": "numeric", "snippet": "15 files",
         "occurrence": 0}
    b = dict(a, occurrence=1)
    assert gp.finding_key(a) != gp.finding_key(b)
    assert len({gp.finding_key(a), gp.finding_key(b)}) == 2
    print("✓ two identical claims on one line remain two findings")


def test_findings_over_agrees_with_the_auditors_own_list():
    """The shared counter must equal the instrument it delegates to."""
    paths = fx.CORPORA["manifest"]()
    assert paths, "the manifest corpus is empty; this proves nothing"
    mine = gp.findings_over(ca, REPO_ROOT, paths)
    allow = ca.load_allowlist()
    theirs = sum(len(ca.scan_file(REPO_ROOT / rel, allow).findings)
                 for rel in paths)
    assert len(mine) == theirs, (len(mine), theirs)
    assert len({gp.finding_key(f) for f in mine}) == len(mine), (
        "the key collapsed two distinct findings into one")
    print(f"✓ findings_over agrees with the auditor: {theirs} over "
          f"{len(paths)} file(s)")


def _joinable():
    finding = {"file": "a.md", "line": 3, "kind": "numeric", "snippet": "1%",
               "occurrence": 0, "paragraph_start": 2, "paragraph_end": 4}
    row = {"file": "a.md", "paragraph_start": 2, "paragraph_end": 4,
           "exposed": True, "otherwise_sourced_by": None, "words": ["see"]}
    return finding, row


def test_enumeration_reconciles_against_an_independently_counted_total():
    """The blank gate this replaced, and the control that proves it can fire.

    Reconciling the enumeration against `len(delta["revealed"])` would compare
    a list with the object it was built from and could never fail.
    `findings_with_arm_off` and `findings_now` are counted separately, so their
    difference is an independent total and the check fires on a real gap.
    """
    finding, row = _joinable()
    result = {"rows": [row]}

    ok = gp.enumerate_revealed(
        result, {"revealed": [finding], "findings_now": 0,
                 "findings_with_arm_off": 1})
    assert len(ok) == 1 and ok[0]["citation_words"] == ["see"]

    with pytest.raises(gp.TotalMismatch) as exc:
        gp.enumerate_revealed(
            result, {"revealed": [finding], "findings_now": 0,
                     "findings_with_arm_off": 3})
    assert "difference 2" in str(exc.value), exc.value
    print("✓ enumeration reconciles against the gate totals and names the gap")


def test_enumeration_refuses_a_finding_it_cannot_join():
    """A join failure means the two passes disagree about paragraphs."""
    finding, _row = _joinable()
    with pytest.raises(gp.UnjoinedFinding) as exc:
        gp.enumerate_revealed(
            {"rows": []}, {"revealed": [finding], "findings_now": 0,
                           "findings_with_arm_off": 1})
    assert "a.md" in str(exc.value), exc.value
    print("✓ an unjoinable revealed finding refuses to enumerate, and names it")
