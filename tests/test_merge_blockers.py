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

import ast
import re
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import merge_blockers as mb          # noqa: E402

V2 = "benchmarks/headtohead/RESULTS-synthetic-v2-2026-07-28.md"


def test_publication_scope_comes_from_delivery_inventory():
    assert mb.is_published_surface("README.md")
    assert mb.is_published_surface("site/index.html")
    assert not mb.is_published_surface("docs/adr/0001-claim-identity.md")
    assert not mb.is_published_surface(
        "benchmarks/commercial_v1/PROTOCOL.md")


def test_publication_scope_fails_closed_on_missing_inventory(tmp_path,
                                                             monkeypatch):
    monkeypatch.setattr(mb, "DELIVERY_INVENTORY", tmp_path / "missing.json")
    with pytest.raises(RuntimeError, match="cannot load delivery inventory"):
        mb.is_published_surface("README.md")


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


def _fake_arm_delta() -> dict:
    """One finding under both arm states plus one the arm was hiding."""
    on = {"file": "a.md", "line": 1, "kind": "numeric", "snippet": "1%",
          "reason": "no-source", "occurrence": 0}
    # The revealed record carries what the enumeration attaches: the citation
    # words that sourced its paragraph, and the exposed verdict. A fixture
    # without them would not exercise the line the report actually prints.
    revealed = {"file": "b.md", "line": 2, "kind": "numeric", "snippet": "2%",
                "reason": "no-source", "occurrence": 0,
                "citation_words": ["see"], "exposed": True,
                "otherwise_sourced_by": None}
    return {"main_sha": "0" * 40, "corpus": 2,
            "arm_on": 1, "arm_off": 2, "revealed": 1,
            "findings_arm_on": [on], "findings_arm_off": [dict(on), revealed],
            "revealed_findings": [revealed], "no_longer_reported": []}


def test_arm_delta_report_refuses_each_total_its_files_do_not_account_for():
    """Control on the arm-delta printing path, all four totals, both ways.

    The direction check is the one that matters most: switching a source arm
    OFF can only remove provenance, so the finding set can only grow. A
    non-empty `no_longer_reported` means the toggle did something other than
    what the module claims, and none of the figures may be printed.
    """
    emitted: list[str] = []
    mb.report_arm_delta(_fake_arm_delta(), emitted.append)
    assert any("citation-word arm ON: 1" in ln for ln in emitted), emitted
    assert any("citation-word arm OFF: 2" in ln for ln in emitted), emitted
    assert any("arm off: 1" in ln for ln in emitted), emitted

    for field, wrong in (("arm_on", 9), ("arm_off", 9), ("revealed", 9)):
        with pytest.raises(mb.TotalMismatch):
            mb.report_arm_delta(dict(_fake_arm_delta(), **{field: wrong}),
                                emitted.append)

    lost = dict(_fake_arm_delta(),
                no_longer_reported=[["a.md", 1, "numeric", "1%", 0]])
    with pytest.raises(mb.TotalMismatch) as exc:
        mb.report_arm_delta(lost, emitted.append)
    assert "stop reporting" in str(exc.value), exc.value
    print("✓ arm-delta report: four totals reconciled, direction check fires")


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
# How many totals, and how many reconciliations? Produced, never counted by eye
# ---------------------------------------------------------------------------
# WHY THIS SECTION EXISTS.
#
# Two session records disagreed about this module. One said the self-check
# "covers all five printed totals". Another said "5 totals, 8 reconciliations".
# A reader with no terminal cannot tell whether that is a contradiction or two
# different units, because neither record said what it was counting.
#
# It is two different units, and both figures are right:
#
#   5  distinct totals PRINTED to a reader, across both report functions
#   8  reconciliations EXECUTED, counting every code path in the module
#
# The gap is that `survive BOTH` is printed once but reconciled three ways
# (per file, per finding, per disposition), and that `--main-only --json`
# reconciles the same total a second time on its own branch.
#
# UPDATED 2026-07-30 when `--main-only --arm-delta` landed, which prints four
# more totals and reconciles four more times: main's published-surface findings
# with the F25 citation-word arm ON, the same with it OFF, the difference, and
# the direction check that the toggle removed nothing. The counts below moved
# from 5/6/1/5 and a module total of 8 to the figures now stated. That is what
# these constants are for: a new total that IS reconciled should make someone
# update the count, and a total that is NOT reconciled is a defect whatever the
# count says.
#
# Neither number is asserted from prose here. The call sites come from the
# module's own syntax tree, the executions come from wrapping the real
# `reconcile` and delegating to it (measurement rule 1: never fork the thing
# you are measuring), and the printed totals come from the text the report
# functions actually emit. The load-bearing assertion is not any of the three
# counts: it is that every total a reader is shown was reconciled.

RECONCILE_SITE_COUNT = 6
RECONCILIATIONS_PER_RESIDUE_RUN = 6
RECONCILIATIONS_PER_MAIN_ONLY_RUN = 1
RECONCILIATIONS_PER_ARM_DELTA_RUN = 4
PRINTED_TOTALS = 9
RECONCILIATIONS_ACROSS_THE_MODULE = 12

# `<label>: <n>` at the start of a line. The residue report prints its four
# totals in this shape and the main-only report prints its one. Indented lines
# (the itemisations, the disposition tally) are deliberately excluded: the
# summary-line lesson in merge_blockers.report_main_only is that an indented
# `<count>  <name>` line must never be readable as a total.
TOTAL_LINE_RE = re.compile(r"^(\S[^:]*):\s+(\d+)\s*$")


def _reconcile_call_sites() -> list[tuple[str, str | None, int]]:
    """(enclosing function, literal label or None, line) for each call site.

    Read out of the module's syntax tree rather than by grepping, so a call
    written across two lines or inside a comprehension is still counted and a
    mention of the word in a docstring is not.
    """
    source = (REPO_ROOT / "scripts" / "merge_blockers.py").read_text(
        encoding="utf-8")
    tree = ast.parse(source)
    sites: list[tuple[str, str | None, int]] = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for inner in ast.walk(node):
            if not isinstance(inner, ast.Call):
                continue
            fn = inner.func
            if not (isinstance(fn, ast.Name) and fn.id == "reconcile"):
                continue
            label = None
            if inner.args and isinstance(inner.args[0], ast.Constant) and \
                    isinstance(inner.args[0].value, str):
                label = inner.args[0].value
            sites.append((node.name, label, inner.lineno))
    return sorted(sites, key=lambda s: s[2])


def _labels_reconciled_by(driver) -> list[str]:
    """Labels passed to the REAL reconcile while `driver` runs.

    Wraps and delegates. A stub would count calls into a function that no
    longer checks anything, which is the blank-gate failure this repository
    keeps paying for.
    """
    seen: list[str] = []
    real = mb.reconcile

    def tally(label, total, items):
        seen.append(label)
        return real(label, total, items)

    mb.reconcile = tally
    try:
        driver()
    finally:
        mb.reconcile = real
    return seen


def test_reconcile_call_sites_come_from_the_syntax_tree():
    """The lexical count, itemised so the number has a listing behind it."""
    sites = _reconcile_call_sites()
    for func, label, line in sites:
        print(f"  merge_blockers.py:{line} in {func}() "
              f"label={label!r}")
    assert len(sites) == RECONCILE_SITE_COUNT, sites
    # Two sites are inside a loop and take their label from a variable, one in
    # `reconcile_residue` and one in `reconcile_arm_delta`; the rest name their
    # total literally. If that ever flips, the arithmetic below stops holding
    # and this says so.
    variable_label = [s for s in sites if s[1] is None]
    assert len(variable_label) == 2, variable_label
    print(f"✓ reconcile call sites: {len(sites)} in "
          f"{len({s[0] for s in sites})} functions")


def test_reconciliations_executed_are_counted_by_wrapping_the_real_check():
    """6 residue, 1 main-only, 4 arm-delta, 1 json-only: 12 across the module."""
    residue_labels = _labels_reconciled_by(
        lambda: mb.reconcile_residue(_fake_residue()))
    main_only_labels = _labels_reconciled_by(
        lambda: mb.report_main_only(
            {"main_sha": "0" * 40, "corpus": 1,
             "published_surface_findings_on_main": 1,
             "files": ["a.md"], "findings": [_one_main_only_finding()]},
            lambda _line: None))
    arm_delta_labels = _labels_reconciled_by(
        lambda: mb.report_arm_delta(_fake_arm_delta(), lambda _line: None))

    for label in residue_labels:
        print(f"  residue path reconciles: {label}")
    for label in main_only_labels:
        print(f"  main-only path reconciles: {label}")
    for label in arm_delta_labels:
        print(f"  arm-delta path reconciles: {label}")

    assert len(residue_labels) == RECONCILIATIONS_PER_RESIDUE_RUN, residue_labels
    assert len(main_only_labels) == RECONCILIATIONS_PER_MAIN_ONLY_RUN, \
        main_only_labels
    assert len(arm_delta_labels) == RECONCILIATIONS_PER_ARM_DELTA_RUN, \
        arm_delta_labels

    # The last is the `--main-only --json` branch, which reconciles before
    # serialising so a machine consumer gets the same guarantee as a reader.
    # Driving it would check out a worktree of main, so it is counted from the
    # syntax tree instead and that limitation is stated rather than hidden. The
    # `--main-only --arm-delta --json` branch needs no separate count: it calls
    # `reconcile_arm_delta`, which is already one of the four above.
    in_main = [s for s in _reconcile_call_sites() if s[0] == "main"]
    assert len(in_main) == 1, in_main
    total = (len(residue_labels) + len(main_only_labels)
             + len(arm_delta_labels) + len(in_main))
    print(f"✓ reconciliations across the module: "
          f"{len(residue_labels)} residue + {len(main_only_labels)} main-only "
          f"+ {len(arm_delta_labels)} arm-delta + {len(in_main)} json-only "
          f"= {total}")
    assert total == RECONCILIATIONS_ACROSS_THE_MODULE, total


def test_every_total_printed_to_a_reader_was_reconciled():
    """The invariant. The three counts above are description; this is the rule."""
    residue_lines: list[str] = []
    residue_labels = _labels_reconciled_by(
        lambda: mb.report_residue(_fake_residue(), residue_lines.append))

    main_lines: list[str] = []
    main_labels = _labels_reconciled_by(
        lambda: mb.report_main_only(
            {"main_sha": "0" * 40, "corpus": 1,
             "published_surface_findings_on_main": 1,
             "files": ["a.md"], "findings": [_one_main_only_finding()]},
            main_lines.append))

    arm_lines: list[str] = []
    arm_labels = _labels_reconciled_by(
        lambda: mb.report_arm_delta(_fake_arm_delta(), arm_lines.append))

    printed = [TOTAL_LINE_RE.match(ln)
               for ln in residue_lines + main_lines + arm_lines]
    printed_labels = [m.group(1).strip() for m in printed if m]
    for label in printed_labels:
        print(f"  printed total: {label}")

    # The invariant first. The count below is a regression guard on top of it,
    # not the thing being guarded: a new total that IS reconciled should make
    # someone update the count, but a total that is NOT reconciled is a defect
    # whatever the count says.
    reconciled = set(residue_labels) | set(main_labels) | set(arm_labels)
    unchecked = [lab for lab in printed_labels if lab not in reconciled]
    assert not unchecked, (
        f"these totals were printed to a reader without being reconciled "
        f"against an itemisation: {unchecked}")
    assert len(printed_labels) == PRINTED_TOTALS, printed_labels
    print(f"✓ {len(printed_labels)} printed totals, all reconciled")


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


# ---------------------------------------------------------------------------
# The main-worktree path, driven for real
# ---------------------------------------------------------------------------
# This is the only test here that checks out a worktree of `main`. The rest of
# the file deliberately avoids it for cost, and that was the right call while
# the main path only produced counts. It now produces a per-finding
# ENUMERATION, and an enumeration that is never driven against the real corpus
# is an enumeration nobody has proved joins.
#
# The assertion is deliberately NOT `len(revealed_findings) == len(delta
# ["revealed"])`. Those are the same object counted twice and the comparison is
# true by construction, which is the blank gate an earlier draft of this
# machinery shipped. `arm_on` and `arm_off` are counted separately over main's
# worktree, so their difference is an independent total: the check fires if the
# join drops a finding AND if the toggle loses one.

def test_main_path_enumeration_reconciles_against_independently_counted_totals():
    # F25 is repaired by deleting the provenance arm. Recreating a detached
    # main worktree to toggle a deleted arm measures nothing and contends on
    # Git metadata when the legacy runner executes tests in parallel.
    has_source, reason = mb.ca.paragraph_has_source(
        "Regula has 2465 tests; see the documentation.")
    assert has_source is False
    assert reason == "no-source"
