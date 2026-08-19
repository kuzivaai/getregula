# regula-ignore
"""A green delivery-surface audit must not hide the surfaces it never read.

MEASURED 2026-08-17 at `bc36b66`. `claim_auditor.delivery_surface_paths()`
returned 108 active, claim-capable delivery surfaces. `scan_file` returned
`scanned=False` for 6 of them, because they are `.yml`, `.toml`, `.py`, `.json`
and `.xml` and `SCANNED_SUFFIXES` holds only prose carriers. `main` then
filtered its reports with `if r.scanned` and printed nothing about the rest, so
`--delivery-surfaces` reported "all claims sourced — OK" over a population it
could not read. The instrument N64 built to stop an unchanged delivery surface
carrying an unsourced claim had an invisible hole in exactly that place.

The six were `action.yml`, `pyproject.toml`, `scripts/cli.py`,
`scripts/mcp_server.py`, `site/sa-tracker.json` and `site/sitemap.xml`. Two of
those are read by no claim instrument at all.

WHY THE FIX IS NOT "ADD THE SUFFIXES". Measured by toggling one variable on the
real module: with `.py` and `.yml` in scope, `action.yml` produced 5 findings
and `scripts/cli.py` produced 14, and almost every one is `ATTRIBUTED_CLAIM`
matching the verb `write` inside `write(f"`. That is the N34 false-positive
class. Absorbing them would need the allowlist or the quarantine, and using
either to make a check pass is prohibited outright. So the gap is declared and
printed at the point of use instead, which is measurement rule 5 applied to the
report rather than to a post-mortem.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import claim_auditor  # noqa: E402


def test_the_population_reconciles_against_its_own_partition():
    """Every delivery surface is either scanned or declared. No third bucket."""
    everything = claim_auditor.delivery_surface_paths()
    unscannable = claim_auditor.unscannable_delivery_surfaces()
    unscannable_paths = {p for paths in unscannable.values() for p in paths}
    scannable = {p for p in everything
                 if Path(p).suffix.lower() in claim_auditor.SCANNED_SUFFIXES}
    assert scannable | unscannable_paths == everything
    assert not (scannable & unscannable_paths)
    assert len(scannable) + len(unscannable_paths) == len(everything)


def test_the_hole_is_real_and_this_check_is_not_vacuous():
    """If the population were empty this whole module would pass for free."""
    everything = claim_auditor.delivery_surface_paths()
    assert len(everything) > 50, len(everything)
    unscannable = claim_auditor.unscannable_delivery_surfaces()
    assert unscannable, (
        "no unscannable delivery surface was found. Either the hole closed, in "
        "which case delete this module and the register, or the inventory "
        "stopped being read, in which case this passed for the wrong reason.")


def test_no_unscannable_delivery_surface_is_undeclared():
    problems = claim_auditor.audit_scan_coverage()
    assert not problems, "\n  ".join(problems)


def test_a_missing_record_is_a_failure_not_a_default(monkeypatch):
    """Control: removing a record must turn the audit red, naming the paths."""
    real = claim_auditor.load_scan_coverage()
    thinned = {k: v for k, v in real.items() if k != ".toml"}
    monkeypatch.setattr(claim_auditor, "load_scan_coverage", lambda: thinned)
    problems = claim_auditor.audit_scan_coverage()
    assert any(".toml" in p and "pyproject.toml" in p for p in problems), problems


def test_a_record_that_matches_nothing_fails_as_stale(monkeypatch):
    """Control: an exclusion must not outlive its premise.

    Same discipline `count_record_policy.not_a_count_claim` and the quarantine's
    burn-downs apply. Without it a suffix could stop being delivered and its
    declared coverage would sit here forever, reading as though somebody had
    checked.
    """
    real = dict(claim_auditor.load_scan_coverage())
    real[".rs"] = {"covered_for": [], "covered_by": [], "not_covered_for": []}
    monkeypatch.setattr(claim_auditor, "load_scan_coverage", lambda: real)
    problems = claim_auditor.audit_scan_coverage()
    assert any(p.startswith(".rs:") and "outlived its premise" in p
               for p in problems), problems


def test_a_covered_class_must_name_an_instrument(monkeypatch):
    """"Covered" with nothing named is the shape of an unchecked assurance."""
    real = dict(claim_auditor.load_scan_coverage())
    real[".toml"] = {"covered_for": ["unsourced numeric claim"],
                     "covered_by": [],
                     "not_covered_for": []}
    monkeypatch.setattr(claim_auditor, "load_scan_coverage", lambda: real)
    problems = claim_auditor.audit_scan_coverage()
    assert any("no instrument named" in p for p in problems), problems


def test_an_unreadable_register_is_fatal_not_empty(monkeypatch, tmp_path):
    """An unknown coverage population must never become a green audit.

    Same rule `delivery_surface_paths` already applies to the inventory it
    reads, and the opposite of the N55(a) swallow that returned the PASS value
    when git never ran.
    """
    monkeypatch.setattr(claim_auditor, "CLAIM_SCAN_COVERAGE_PATH",
                        tmp_path / "absent.json")
    try:
        claim_auditor.load_scan_coverage()
    except claim_auditor.CoverageError:
        return
    raise AssertionError("a missing register was read as empty coverage")


def test_every_record_states_what_is_not_covered():
    """The half a coverage document is normally missing.

    Naming who else is looking is easy and reassuring. Naming what nobody is
    looking for is the part that makes the statement honest, and it is what
    measurement rule 5 asks for: say what the gate tests, and compare it to what
    is being claimed.
    """
    coverage = claim_auditor.load_scan_coverage()
    for suffix, record in coverage.items():
        assert record["not_covered_for"], (
            f"{suffix}: declares no uncovered class. Every instrument named "
            f"here is narrower than the auditor it stands in for; a record "
            f"claiming otherwise has not been thought about.")
        assert isinstance(record["covered_by"], list), suffix


def test_the_register_is_valid_json_with_its_reasoning_attached():
    payload = json.loads(
        claim_auditor.CLAIM_SCAN_COVERAGE_PATH.read_text(encoding="utf-8"))
    for field in ("_what_this_is", "_why", "_rule",
                  "_why_not_just_widen_the_suffix_set"):
        assert field in payload and len(payload[field]) > 80, field


def test_the_coverage_statement_names_the_paths_it_could_not_read():
    """The report a reader sees must carry the gap, not only the test suite."""
    statement = claim_auditor.format_scan_coverage()
    assert "NOT READ BY THIS AUDITOR" in statement
    for path in ("pyproject.toml", "site/sitemap.xml", "action.yml"):
        assert path in statement, path
    assert "NOT covered" in statement
