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
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import claim_auditor as ca          # noqa: E402
import f25_exposure as fx           # noqa: E402


def test_the_citation_word_arm_really_is_tried_before_the_file_ref_arm():
    """F25's mechanism, read from the source rather than remembered.

    The finding was originally recorded with line numbers 490 and 499, then
    re-recorded as 544 and 553, and both had moved again by the time this was
    written. The ORDER is the claim; the line numbers are just where it happens
    to live today.
    """
    order = dict(fx.arm_order())
    assert "citation-word" in order, order
    assert "file-ref" in order, order
    assert order["citation-word"] < order["file-ref"], (
        f"the citation-word arm is no longer tried before the file-reference "
        f"arm ({order}). If that was deliberate, F25 is fixed and this "
        f"module should be retired, not edited to agree.")
    print(f"✓ arm order: citation-word at :{order['citation-word']} "
          f"before file-ref at :{order['file-ref']}")


def test_every_arm_the_module_names_was_found_in_the_source():
    """A needle that stops matching would silently drop an arm from the table."""
    names = [name for name, _ in fx.arm_order()]
    assert names == ["url", "md-link", "html-link", "citation-word",
                     "verification-label", "file-ref"], names


def test_the_never_pattern_matches_nothing():
    """The toggle is only as good as the pattern that replaces the real one."""
    for text in ("", "see", "source: x", "reference", "x", "xx", "cf.",
                 "verdict:", "\n\n", "https://example.com"):
        assert not fx.NEVER.search(text), text
    print("✓ the off-switch pattern matches nothing")


def test_switching_the_arm_off_can_only_reveal_findings():
    """Direction check on the real gate over a small real corpus.

    Removing a source arm removes provenance, so the finding set can only grow.
    A shrink would mean the toggle changed something other than what the module
    claims, and the numbers would be unpublishable.
    """
    paths = fx.CORPORA["manifest"]()
    assert paths, "the manifest corpus is empty; this proves nothing"
    delta = fx.gate_delta(paths)
    assert delta["no_longer_reported"] == [], delta["no_longer_reported"]
    assert delta["findings_with_arm_off"] >= delta["findings_now"]
    assert len(delta["revealed"]) == (
        delta["findings_with_arm_off"] - delta["findings_now"])
    print(f"✓ arm off reveals {len(delta['revealed'])}, hides 0")


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


def test_a_corpus_that_drops_a_named_surface_says_so():
    """Finding N6, surfaced rather than absorbed.

    `site/llms-full.txt` is on the published-count manifest and `.txt` is
    outside `SCANNED_SUFFIXES`, so the manifest corpus is 9 of 10. A corpus that
    silently loses a member reports less exposure and reads as better news.
    """
    fx.CORPORA["manifest"]()          # populates DROPPED as a side effect
    dropped = fx.DROPPED.get("manifest", [])
    assert any("llms-full.txt" in d for d in dropped), dropped
    assert all("N6" in d for d in dropped), dropped
    print(f"✓ manifest corpus names its {len(dropped)} unscannable surface(s)")


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
    """A module left patched would corrupt every later scan in the process."""
    original = ca.CITATION_WORDS
    boom = RuntimeError("planted")

    def explode(_paths):
        raise boom

    real_findings = fx._findings
    fx._findings = explode
    try:
        with pytest.raises(RuntimeError):
            fx.gate_delta(["README.md"])
    finally:
        fx._findings = real_findings

    assert ca.CITATION_WORDS is original, (
        "CITATION_WORDS was left patched after a failure; every subsequent "
        "scan in this process would report the wrong thing")
    assert ca.CITATION_WORDS.search("see the table"), (
        "the restored pattern no longer matches a citation word")
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
    print(f"✓ {len(fx.CORPORA)} corpus definitions, all tracked and scannable")


def test_the_module_docstring_states_its_corpus_definitions():
    """The brief required the corpus definition to live inside the file."""
    doc = fx.__doc__ or ""
    assert "CORPUS DEFINITIONS" in doc
    for name in fx.CORPORA:
        assert re.search(rf"^\s+{re.escape(name)}\s", doc, re.M), name
