"""Cover the totals `scripts/merge_blockers.py` prints.

WHY THIS EXISTS
---------------
`LEDGER.md` N12 recorded this script as reporting 168 published-surface findings
on `main` "in 29 files", and 168 against a 29-file listing was raised as a
discrepancy with ten findings unaccounted for.

MEASURED 2026-07-29, the discrepancy does not reproduce. `--main-only` reports
168 and itemises 33 files summing to 168, both at `f286562` and at `ec484b7`,
the commit that introduced the script and recorded the figure. The listing has
always accounted for the total; the 29 has no recorded apparatus.

That is a reason to fix the ledger, not a reason to skip the guard. Nothing
forced a printed total to agree with the breakdown printed under it, so the
question "do these two numbers agree?" could only ever be answered by hand, and
answering it by hand is what produced the 29 in the first place.

WHAT IS GUARDED
---------------
`reconcile()` is the single door every total passes through, and the itemisation
it checks is the same list the reader is shown. The controls below plant a
mismatch in both directions and on the real reporting paths, not only on the
helper, so the guard cannot pass by being wired to nothing.

One further finding of this session is pinned here: the residue disposition
predicate classified per finding while the remedy, a citation, operates per
paragraph. `RESULTS-synthetic-v2-2026-07-28.md` has a reproducible figure
sharing a paragraph with two withdrawn ones, so it cannot be sourced without
citing a withdrawn figure. It is now classed `blocked` by predicate.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import merge_blockers as mb          # noqa: E402

V2 = "benchmarks/headtohead/RESULTS-synthetic-v2-2026-07-28.md"


# ---------------------------------------------------------------------------
# reconcile(): the arithmetic
# ---------------------------------------------------------------------------

def test_reconcile_accepts_an_itemisation_that_accounts_for_the_total():
    items = [("a.md", 3), ("b.md", 4)]
    assert mb.reconcile("x", 7, items) == items
    print("✓ reconcile: matching itemisation accepted")


def test_reconcile_rejects_a_total_its_items_do_not_reach():
    """The exact shape the ledger reported: 168 over a listing summing to 158."""
    with pytest.raises(mb.TotalMismatch) as exc:
        mb.reconcile("published-surface findings ON MAIN", 168,
                     [("a.md", 100), ("b.md", 58)])
    msg = str(exc.value)
    assert "168" in msg, msg
    assert "158" in msg, msg
    assert "difference 10" in msg, msg
    print("✓ reconcile: under-counted itemisation rejected, gap named")


def test_reconcile_rejects_an_itemisation_that_overshoots_the_total():
    """Both directions. A guard that only catches one is half a guard."""
    with pytest.raises(mb.TotalMismatch) as exc:
        mb.reconcile("x", 5, [("a.md", 9)])
    assert "difference -4" in str(exc.value)
    print("✓ reconcile: over-counted itemisation rejected")


def test_reconcile_accepts_zero_against_an_empty_itemisation():
    assert mb.reconcile("x", 0, []) == []
    with pytest.raises(mb.TotalMismatch):
        mb.reconcile("x", 1, [])
    print("✓ reconcile: empty itemisation cannot stand in for a nonzero total")


# ---------------------------------------------------------------------------
# The real reporting paths, driven with doctored records
# ---------------------------------------------------------------------------

def _one_main_only_finding() -> dict:
    return {"file": "a.md", "line": 1, "kind": "numeric",
            "snippet": "1%", "reason": "no-source"}


def test_main_only_report_refuses_a_total_its_files_do_not_account_for():
    """Control on the printing path, both ways, not just on the helper."""
    findings = [_one_main_only_finding()]
    good = {"main_sha": "0" * 40, "corpus": 1,
            "published_surface_findings_on_main": 1,
            "files": ["a.md"], "findings": findings}

    emitted: list[str] = []
    mb.report_main_only(good, emitted.append)
    assert any("published-surface findings ON MAIN: 1" in line
               for line in emitted), emitted
    assert any("reconciled: 1 files account for 1 findings" in line
               for line in emitted), emitted

    bad = dict(good, published_surface_findings_on_main=11)
    with pytest.raises(mb.TotalMismatch):
        mb.report_main_only(bad, emitted.append)
    print("✓ main-only report: reconciles before printing, both directions")


def _fake_residue() -> dict:
    f = {"file": "x.md", "line": 1, "kind": "numeric", "snippet": "1%",
         "reason": "no-source", "bucket": "everything else",
         "present_at_base": False, "disposition": "fixable", "why": "w"}
    return {"head": "a" * 40, "base_sha": "b" * 40, "tree": "/tmp",
            "total": 1, "introduced_only": 1, "published_only": 1,
            "both": 1, "residue": [f],
            "all_findings": [f], "introduced": [f], "published": [f]}


def test_residue_report_refuses_each_total_that_stops_matching():
    """Every printed total is covered, not only the one that was questioned."""
    good = _fake_residue()
    emitted: list[str] = []
    mb.report_residue(good, emitted.append)
    assert any("total findings" in line for line in emitted), emitted

    for key in ("total", "introduced_only", "published_only", "both"):
        broken = _fake_residue()
        broken[key] = broken[key] + 7
        with pytest.raises(mb.TotalMismatch):
            mb.reconcile_residue(broken)
    print("✓ residue report: all four totals reconciled")


def test_residue_disposition_tally_is_reconciled_too():
    """`survive BOTH` is printed three ways; a drift in any one must fire."""
    broken = _fake_residue()
    broken["residue"] = broken["residue"] + [dict(broken["residue"][0])]
    # `both` still says 1 while the residue list now holds 2.
    with pytest.raises(mb.TotalMismatch):
        mb.reconcile_residue(broken)
    print("✓ residue report: per-finding and per-disposition views reconciled")


# ---------------------------------------------------------------------------
# The paragraph-granularity finding
# ---------------------------------------------------------------------------

def test_paragraph_withdrawn_predicate_is_decided_by_the_marker():
    assert mb.paragraph_carries_a_withdrawn_figure(
        ["| a | **10/30 = 33%** |",
         "| b | **14/30 = 47%** [NOT REPRODUCIBLE] |"])
    assert not mb.paragraph_carries_a_withdrawn_figure(
        ["| a | **10/30 = 33%** |", "| b | **16/30 = 53%** |"])
    print("✓ withdrawn-paragraph predicate follows the marker")


def test_paragraph_lines_uses_the_auditors_own_splitter():
    """A real paragraph, located by content so the test does not pin a line."""
    lines = (REPO_ROOT / V2).read_text(encoding="utf-8").splitlines()
    target = [i + 1 for i, ln in enumerate(lines)
              if "**Default scan**" in ln and "10/30" in ln]
    assert len(target) == 1, target
    para = mb.paragraph_lines(V2, target[0])
    assert any("Default scan" in ln for ln in para), para
    assert any("[NOT REPRODUCIBLE]" in ln for ln in para), para
    print("✓ paragraph_lines: the reproducible row shares its paragraph")


def test_the_reproducible_row_is_blocked_not_fixable():
    """The finding: this figure cannot be sourced without citing a withdrawn one.

    Located by content, not by line number, so editing the document above it
    does not silently retarget the assertion.
    """
    lines = (REPO_ROOT / V2).read_text(encoding="utf-8").splitlines()
    reproducible = [i + 1 for i, ln in enumerate(lines)
                    if "**Default scan**" in ln and "10/30" in ln]
    withdrawn = [i + 1 for i, ln in enumerate(lines)
                 if "[NOT REPRODUCIBLE]" in ln and "14/30" in ln]
    assert len(reproducible) == 1 and len(withdrawn) == 1

    cls, why = mb.disposition({"file": V2, "line": reproducible[0]})
    assert cls == "blocked", (cls, why)
    assert "paragraph-granular" in why

    # The withdrawn row itself must stay inherited: it must not be sourced.
    assert mb.disposition({"file": V2, "line": withdrawn[0]})[0] == "inherited"
    print("✓ disposition: reproducible row blocked, withdrawn row inherited")
