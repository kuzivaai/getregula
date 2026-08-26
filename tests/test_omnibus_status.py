"""Tests for the Omnibus enactment single source of truth in report.py.

These tests verify that:
- OMNIBUS_OJ_DATE is "2026-07-24" (Regulation (EU) 2026/1744, published in
  the Official Journal 24 July 2026; in force from 27 July 2026)
- OMNIBUS_ENACTED is True now the OJ date is set
- OMNIBUS_STATUS carries the published/in-force wording, date-qualified
- _enrich_deadlines produces in-force copy, never "pending OJ publication"
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))


def test_omnibus_oj_date_is_set():
    """OMNIBUS_OJ_DATE records the actual OJ publication date."""
    from report import OMNIBUS_OJ_DATE
    assert OMNIBUS_OJ_DATE == "2026-07-24", (
        f"OMNIBUS_OJ_DATE should be 2026-07-24 (Regulation (EU) 2026/1744); "
        f"got {OMNIBUS_OJ_DATE!r}"
    )


def test_omnibus_enacted_is_true():
    """OMNIBUS_ENACTED must be True now the OJ date is set, and the derived
    in-force date must be publication + 3 days."""
    from report import OMNIBUS_ENACTED
    from omnibus import OMNIBUS_IN_FORCE_DATE
    assert OMNIBUS_ENACTED is True, (
        f"OMNIBUS_ENACTED should be True with OMNIBUS_OJ_DATE set; got {OMNIBUS_ENACTED!r}"
    )
    assert OMNIBUS_IN_FORCE_DATE == "2026-07-27", (
        f"in-force date must derive as OJ + 3 days = 2026-07-27; got {OMNIBUS_IN_FORCE_DATE!r}"
    )


def test_omnibus_status_contains_published_wording():
    """OMNIBUS_STATUS must carry the published + date-qualified in-force
    wording and never the pending copy."""
    from report import OMNIBUS_STATUS
    assert "Published in OJ 2026-07-24" in OMNIBUS_STATUS, (
        f"OMNIBUS_STATUS should say 'Published in OJ 2026-07-24'; got: {OMNIBUS_STATUS!r}"
    )
    assert "in force from 2026-07-27" in OMNIBUS_STATUS, (
        f"OMNIBUS_STATUS should be date-qualified ('in force from 2026-07-27'), "
        f"which stays truthful before, on and after the date; got: {OMNIBUS_STATUS!r}"
    )
    assert "pending OJ publication" not in OMNIBUS_STATUS, (
        f"OMNIBUS_STATUS must not say pending — the OJ published 24 Jul 2026; "
        f"got: {OMNIBUS_STATUS!r}"
    )


def test_omnibus_status_parenthetical_records_adoption_history():
    """The deadline parenthetical must keep the adoption history AND the
    publication record (history is not erased by enactment)."""
    from omnibus import status_parenthetical
    paren = status_parenthetical()
    assert "16 Jun 2026" in paren, (
        f"parenthetical should keep EP approval (16 Jun 2026); got: {paren!r}"
    )
    assert "29 Jun 2026" in paren, (
        f"parenthetical should keep Council approval (29 Jun 2026); got: {paren!r}"
    )
    assert "published in OJ 2026-07-24" in paren, (
        f"parenthetical should record OJ publication; got: {paren!r}"
    )


def test_enrich_deadlines_enacted_wording_high_risk():
    """High-risk deadline notes carry the deferred date and the OJ record,
    never the pending copy."""
    from report import _enrich_deadlines
    findings = [{"tier": "high_risk", "category": "Employment and Workers Management"}]
    _enrich_deadlines(findings)
    note = findings[0]["deadline_note"]
    assert "pending OJ publication" not in note, (
        f"high_risk deadline_note must not say pending after OJ publication; got: {note!r}"
    )
    assert "2 Dec 2027" in note or "2027-12-02" in note, (
        f"high_risk deadline_note should carry the deferred Annex III date; got: {note!r}"
    )
    assert "in force from 2026-07-27" in note, (
        f"high_risk deadline_note must be date-qualified; got: {note!r}"
    )


def test_enrich_deadlines_enacted_wording_limited_risk():
    """Limited-risk deadline notes drop the pending copy after OJ publication."""
    from report import _enrich_deadlines
    findings = [{"tier": "limited_risk", "category": "Article 50 Transparency"}]
    _enrich_deadlines(findings)
    note = findings[0]["deadline_note"]
    assert "pending OJ publication" not in note, (
        f"limited_risk deadline_note must not say pending after OJ publication; got: {note!r}"
    )


def test_enrich_deadlines_enacted_wording_agent_autonomy():
    """Agent-autonomy deadline notes drop the pending copy after OJ publication."""
    from report import _enrich_deadlines
    findings = [{"tier": "agent_autonomy", "category": "Article 14 Human Oversight"}]
    _enrich_deadlines(findings)
    note = findings[0]["deadline_note"]
    assert "pending OJ publication" not in note, (
        f"agent_autonomy deadline_note must not say pending after OJ publication; got: {note!r}"
    )


def test_enrich_deadlines_prohibited_unaffected():
    """Prohibited tier deadline notes are unaffected by Omnibus status."""
    from report import _enrich_deadlines
    findings = [{"tier": "prohibited", "category": "Article 5"}]
    _enrich_deadlines(findings)
    note = findings[0]["deadline_note"]
    assert "2 Feb 2025" in note, f"prohibited note should mention Feb 2025; got: {note!r}"
    assert findings[0]["deadline_status"] == "enforceable"


# ---------------------------------------------------------------------------
# Consumer wiring (P3 / H8 class fix, 16 Jul 2026): every script that
# emits deadline copy derives it from omnibus.py, so setting
# OMNIBUS_OJ_DATE is the whole flip. These assertions hold both before
# and after enactment.
# ---------------------------------------------------------------------------

def test_remediation_plan_deadline_derived():
    """Plan deadline lines carry the binding baseline PLUS the adopted-
    Omnibus context (16 Jul 2026 revision — the earlier gate pinned the
    bare baseline date, which was accurate but materially incomplete;
    every other consumer already rendered the status context)."""
    import omnibus
    import remediation_plan
    assert remediation_plan.DEADLINE_HIGH_RISK == omnibus.annex_iii_deadline_line()


def test_exec_summary_limited_uses_original_prose():
    import omnibus
    from exec_summary import TIER_DESCRIPTIONS
    assert omnibus.ORIGINAL_PROSE in TIER_DESCRIPTIONS["limited_risk"]


def test_explain_articles_when_derived():
    import omnibus
    from explain_articles import ARTICLES
    for art in ("6", "9", "10", "11", "12", "13", "14", "15", "17"):
        when = ARTICLES[art]["when"]
        if omnibus.OMNIBUS_ENACTED:
            assert omnibus.ANNEX_III_PROSE in when, (art, when)
        else:
            assert omnibus.ORIGINAL_PROSE in when, (art, when)
            assert "pending OJ" in when, (art, when)


def test_register_deadlines_current():
    import omnibus
    from register import _current_deadlines
    d = _current_deadlines({"applicable_deadline": "stale",
                            "omnibus_proposed_deadline": "stale",
                            "omnibus_status": "stale"})
    if omnibus.OMNIBUS_ENACTED:
        assert d["applicable_deadline"] == omnibus.DEADLINE_OMNIBUS_ANNEX_III
        assert "in_force" in d["omnibus_status"]
    else:
        assert d["applicable_deadline"] == omnibus.DEADLINE_CURRENT_LAW
        assert "pending_oj_publication" in d["omnibus_status"]
    assert d["omnibus_proposed_deadline"] == omnibus.DEADLINE_OMNIBUS_ANNEX_III


def test_no_binding_deadline_literals_outside_omnibus():
    """Class guard: the human-readable binding-deadline literal may only
    appear in scripts that are the source of truth or that record it as
    a historical/statutory fact. Everything else must derive from
    omnibus.py, or the OJ flip silently misses it (the 8 Jul audit's H8
    found six such scripts; the 16 Jul pass found five more)."""
    from pathlib import Path
    allowed = {
        "omnibus.py",       # the single source of truth
        "timeline.py",      # historical narrative + statutory rows (Art 5,
                            # GPAI, Art 50 dates unchanged by the Omnibus),
                            # status suffix already derived from omnibus.py
        "gpai_check.py",    # docstring: statutory GPAI enforcement date,
                            # unchanged by the Omnibus
    }
    offenders = []
    scripts_dir = Path(__file__).parent.parent / "scripts"
    for p in sorted(scripts_dir.glob("*.py")):
        if p.name in allowed:
            continue
        if "2 August 2026" in p.read_text(encoding="utf-8"):
            offenders.append(p.name)
    assert not offenders, (
        "binding-deadline literal found outside omnibus.py — derive from "
        f"omnibus.py instead: {offenders}")
