# regula-ignore
"""Guard `scripts/f25_exposure.py`, the committed apparatus for finding F25.

WHY THIS EXISTS
---------------
Owner decision 3 was unanswerable for five sessions because the exposure figure
on record, 22 / 46, had no committed apparatus and a second pass produced
29 / 53 instead. The remedy was a committed script. A committed script with
nothing checking it is the same problem one step later, so the properties the
measurement depends on are pinned here.

WHAT IS PINNED, AND WHAT IS DELIBERATELY NOT
--------------------------------------------
NOT the figures. They move whenever the corpus moves, which is every commit that
edits a tracked document, and pinning them would turn this into the treadmill
`LEDGER.md` rule 24 warns about.

What is pinned is that the instrument works:

- the citation-word arm really is tried before the file-reference arm, which is
  the whole mechanism of F25 and is read out of the auditor's source
- switching the arm off can only reveal findings, never hide them
- the gate unit agrees with `claim_auditor --diff-base main` exactly, which is
  what caught a six-finding undercount from a set that merged duplicate claims
- every total is reconciled against its own itemisation
- the module restores `CITATION_WORDS` even when a measurement raises
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import claim_auditor as ca          # noqa: E402
import f25_exposure as fx           # noqa: E402
import gate_probe as gp             # noqa: E402


def test_the_citation_word_arm_has_been_removed():
    """F25 is repaired only if ordinary prose is no longer a source arm."""
    order = dict(fx.arm_order())
    assert "citation-word" not in order, order
    assert "file-ref" in order, order


def test_every_arm_the_module_names_was_found_in_the_source():
    """A needle that stops matching would silently drop an arm from the table."""
    names = [name for name, _ in fx.arm_order()]
    assert names == ["url", "md-link", "html-link",
                     "verification-label", "file-ref"], names


def test_the_never_pattern_matches_nothing():
    """The toggle is only as good as the pattern that replaces the real one."""
    for text in ("", "see", "source: x", "reference", "x", "xx", "cf.",
                 "verdict:", "\n\n", "https://example.com"):
        assert not fx.NEVER.search(text), text
    print("✓ the off-switch pattern matches nothing")


def test_legacy_off_switch_is_now_a_noop():
    """Direction check on the real gate over a small real corpus.

    Removing a source arm removes provenance, so the finding set can only grow.
    A shrink would mean the toggle changed something other than what the module
    claims, and the numbers would be unpublishable.
    """
    paths = fx.CORPORA["manifest"]()
    assert paths, "the manifest corpus is empty; this proves nothing"
    delta = fx.gate_delta(paths)
    assert delta["no_longer_reported"] == [], delta["no_longer_reported"]
    assert delta["findings_with_arm_off"] == delta["findings_now"]
    assert delta["revealed"] == []


def test_the_gate_unit_agrees_with_the_auditors_own_total():
    """The undercount this caught, pinned.

    Keyed on (file, line, kind, snippet) alone, the finding set was 267 where
    `--diff-base main` reported 273 over the same 59 files: six claims repeat
    identically on a single line. The occurrence ordinal fixed it. This asserts
    the two instruments agree, whatever the number is today.
    """
    paths = fx.CORPORA["diff-base"]()
    delta = fx.gate_delta(paths)

    allow = ca.load_allowlist()
    listed = sum(len(ca.scan_file(REPO_ROOT / rel, allow).findings)
                 for rel in paths)
    assert delta["findings_now"] == listed, (
        f"f25_exposure counts {delta['findings_now']} findings where the "
        f"auditor's own list has {listed} over the same {len(paths)} files. A "
        f"set that merges duplicate claims undercounts.")
    print(f"✓ gate unit agrees with the auditor: {listed} findings over "
          f"{len(paths)} files")


def _joinable(file="a.md", line=3, start=2, end=4):
    """One revealed finding and the citation-word row it must join to."""
    finding = {"file": file, "line": line, "kind": "numeric", "snippet": "1%",
               "occurrence": 0, "paragraph_start": start, "paragraph_end": end}
    row = {"file": file, "paragraph_start": start, "paragraph_end": end,
           "exposed": True, "otherwise_sourced_by": None, "words": ["see"]}
    return finding, row


def test_the_revealed_enumeration_accounts_for_the_revealed_count():
    """The per-finding enumeration, checked against the count it itemises.

    WHY THIS TEST EXISTS. Before it, this module reported how MANY findings the
    citation-word arm holds green and never which ones. The 26 on the live site
    could only be listed by writing a throwaway script, and a figure whose
    apparatus is gone is the exact defect that made owner decision 3
    unanswerable for five sessions.

    TWO corpora, because a length equality on one could hold by accident, and
    both are asserted non-empty first: an absent signal is not a passing
    signal, and a corpus with nothing revealed proves nothing about an
    enumeration of revealed findings.
    """
    for name in ("manifest", "site"):
        m = fx.measure(name)
        revealed = m["claim_unit"]["revealed"]
        listed = m["revealed_findings"]
        assert revealed == 0, (name, m["claim_unit"])
        assert listed == [], (name, listed)


def test_enumeration_refuses_a_finding_it_cannot_join_to_a_paragraph():
    """Control A: the two passes disagreeing about paragraph boundaries.

    Driven on the real function with a row set that cannot satisfy the join, so
    the guard is proved to fire rather than assumed to.
    """
    finding, row = _joinable()
    delta = {"revealed": [finding], "findings_now": 0,
             "findings_with_arm_off": 1}

    assert fx.enumerate_revealed({"rows": [row]}, delta), "the joinable case " \
        "must succeed, or this control cannot distinguish anything"

    with pytest.raises(fx.UnjoinedFinding) as exc:
        fx.enumerate_revealed({"rows": []}, delta)
    assert "a.md" in str(exc.value), exc.value
    print("✓ an unjoinable revealed finding refuses to enumerate, and names it")


def test_enumeration_is_reconciled_against_the_difference_of_the_gate_totals():
    """Control B: the enumeration is checked against an INDEPENDENT total.

    Reconciling `len(revealed)` against the list built from `revealed` could
    never fail. The check is against `findings_with_arm_off - findings_now`,
    counted separately, so a toggle that lost a finding fires it too.
    """
    finding, row = _joinable()
    result = {"rows": [row]}

    ok = fx.enumerate_revealed(
        result, {"revealed": [finding], "findings_now": 0,
                 "findings_with_arm_off": 1})
    assert len(ok) == 1

    with pytest.raises(fx.TotalMismatch) as exc:
        fx.enumerate_revealed(
            result, {"revealed": [finding], "findings_now": 0,
                     "findings_with_arm_off": 3})
    assert "difference 2" in str(exc.value), exc.value
    print("✓ enumeration reconciles against the gate totals, and refuses a gap")


def test_manifest_corpus_includes_machine_readable_text_surfaces():
    """Finding N6, surfaced rather than absorbed.

    `site/llms-full.txt` is on the published-count manifest and `.txt` is
    outside `SCANNED_SUFFIXES`, so the manifest corpus is 9 of 10. A corpus that
    silently loses a member reports less exposure and reads as better news.
    """
    fx.CORPORA["manifest"]()          # populates DROPPED as a side effect
    dropped = fx.DROPPED.get("manifest", [])
    assert not any("llms-full.txt" in d for d in dropped), dropped


def test_every_total_is_reconciled_against_its_itemisation():
    """`reconcile` is imported from merge_blockers, so drive it and prove it."""
    m = fx.measure("manifest")
    p = m["paragraph_unit"]
    assert p["exposed"] + p["masked"] == p["citation_word_sourced"]
    c = m["claim_unit"]
    assert c["findings_now"] + c["revealed"] == c["findings_with_arm_off"]

    with pytest.raises(fx.TotalMismatch):
        fx.reconcile("planted", 5, [("a", 1)])
    print("✓ totals reconcile, and the imported check still refuses a mismatch")


def test_citation_words_is_restored_even_when_a_measurement_raises():
    """A module left patched would corrupt every later scan in the process.

    RETARGETED 2026-07-30. The toggle moved into `gate_probe.arm_delta` when
    the probe was made shared, so patching `f25_exposure._findings` no longer
    intercepts the call path and this test would have passed by never raising,
    which is the blank-gate failure it exists to prevent. It now patches the
    function `arm_delta` actually calls.
    """
    original = ca.CITATION_WORDS
    boom = RuntimeError("planted")

    def explode(_module, _root, _paths):
        raise boom

    real_findings = gp.findings_over
    gp.findings_over = explode
    try:
        with pytest.raises(RuntimeError):
            fx.gate_delta(["README.md"])
    finally:
        gp.findings_over = real_findings

    assert ca.CITATION_WORDS is original, (
        "CITATION_WORDS was left patched after a failure; every subsequent "
        "scan in this process would report the wrong thing")
    assert not ca.paragraph_has_source("see the table with 47 tests")[0]
    print("✓ CITATION_WORDS restored after a raising measurement")


def test_recorded_figures_are_declared_as_data_not_buried_in_prose():
    """Whatever the answer, the two figures under test must be named."""
    assert fx.RECORDED_FIGURES == {"22 / 46": (22, 46), "29 / 53": (29, 53)}


def test_recovery_reporting_is_honest_in_both_directions():
    """A hit must be reported as a hit and a miss as a miss.

    Driven with synthetic measurements so this does not depend on today's
    corpus. If the reporter could only ever say "not recoverable", the result
    in the ledger would be worthless.
    """
    def fake(exposed, total):
        return [{"corpus": "synthetic",
                 "paragraph_unit": {"exposed": exposed,
                                    "citation_word_sourced": total,
                                    "masked": total - exposed},
                 "claim_unit": {"findings_now": 0,
                                "findings_with_arm_off": 0, "revealed": 0}}]

    lines: list[str] = []
    hit = fx.report_recovery(fake(22, 46), lines.append)
    assert hit is True, lines
    assert any("RECOVERED 22 / 46" in ln for ln in lines), lines

    lines = []
    miss = fx.report_recovery(fake(1, 2), lines.append)
    assert miss is False, lines
    assert any("NOT RECOVERABLE 22 / 46" in ln for ln in lines), lines
    print("✓ recovery reporting distinguishes a hit from a miss")


def test_corpus_definitions_are_all_tracked_and_scannable():
    """Rule 4b: an untracked file is not a surface, in every corpus."""
    tracked = set(fx._tracked_scannable())
    for name, build in fx.CORPORA.items():
        paths = build()
        assert paths, f"corpus {name} is empty"
        stray = [p for p in paths if p not in tracked]
        assert not stray, f"corpus {name} includes untracked paths: {stray}"
        bad = [p for p in paths
               if Path(p).suffix.lower() not in ca.SCANNED_SUFFIXES]
        assert not bad, f"corpus {name} includes unscannable paths: {bad}"

    original_git = fx._git
    def detached_git(*args):
        if args[0] == "merge-base":
            raise subprocess.CalledProcessError(128, ["git", *args])
        if args[0] == "cat-file":
            return "tree t\nparent base-parent\nparent topic-parent\n\nmessage\n"
        if args[0] == "diff":
            assert args[2] == "base-parent"
            return "README.md\n"
        if args[0] == "ls-files":
            return "README.md\0"
        raise AssertionError(args)
    try:
        fx._git = detached_git
        assert fx._diff_base("main") == ["README.md"]
    finally:
        fx._git = original_git
    print(f"✓ {len(fx.CORPORA)} corpus definitions, all tracked and scannable")


def test_the_module_docstring_states_its_corpus_definitions():
    """The brief required the corpus definition to live inside the file."""
    doc = fx.__doc__ or ""
    assert "CORPUS DEFINITIONS" in doc
    for name in fx.CORPORA:
        assert re.search(rf"^\s+{re.escape(name)}\s", doc, re.M), name
