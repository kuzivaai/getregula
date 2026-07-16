"""Tests for the Omnibus enactment single source of truth in report.py.

These tests verify that:
- OMNIBUS_OJ_DATE is None (OJ publication not yet happened as of 2026-07-02)
- OMNIBUS_ENACTED is False when OMNIBUS_OJ_DATE is None
- OMNIBUS_STATUS contains the correct pending wording
- _enrich_deadlines produces "pending OJ publication" copy while unenacted
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))


def test_omnibus_oj_date_is_none():
    """OMNIBUS_OJ_DATE must be None until the OJ is published."""
    from report import OMNIBUS_OJ_DATE
    assert OMNIBUS_OJ_DATE is None, (
        f"OMNIBUS_OJ_DATE should be None until the OJ is published; got {OMNIBUS_OJ_DATE!r}"
    )


def test_omnibus_enacted_is_false():
    """OMNIBUS_ENACTED must be False while OJ date is unset."""
    from report import OMNIBUS_ENACTED
    assert OMNIBUS_ENACTED is False, (
        f"OMNIBUS_ENACTED should be False when OMNIBUS_OJ_DATE is None; got {OMNIBUS_ENACTED!r}"
    )


def test_omnibus_status_contains_pending_oj_publication():
    """OMNIBUS_STATUS should reference pending OJ publication (not 'pending Council adoption')."""
    from report import OMNIBUS_STATUS
    assert "pending OJ publication" in OMNIBUS_STATUS, (
        f"OMNIBUS_STATUS should say 'pending OJ publication'; got: {OMNIBUS_STATUS!r}"
    )
    # Council has approved — must NOT claim it is pending Council adoption
    assert "pending Council adoption" not in OMNIBUS_STATUS, (
        f"OMNIBUS_STATUS must not say 'pending Council adoption' — Council approved 29 Jun 2026; "
        f"got: {OMNIBUS_STATUS!r}"
    )


def test_omnibus_status_records_ep_and_council_approval():
    """OMNIBUS_STATUS must record both EP and Council approval dates."""
    from report import OMNIBUS_STATUS
    assert "16 Jun 2026" in OMNIBUS_STATUS or "Jun 2026" in OMNIBUS_STATUS, (
        f"OMNIBUS_STATUS should mention EP approval (16 Jun 2026); got: {OMNIBUS_STATUS!r}"
    )
    assert "29 Jun 2026" in OMNIBUS_STATUS or "Council approved" in OMNIBUS_STATUS, (
        f"OMNIBUS_STATUS should mention Council approval (29 Jun 2026); got: {OMNIBUS_STATUS!r}"
    )


def test_enrich_deadlines_pending_wording_high_risk():
    """While unenacted, high-risk deadline notes reference pending OJ publication."""
    from report import _enrich_deadlines
    findings = [{"tier": "high_risk", "category": "Employment and Workers Management"}]
    _enrich_deadlines(findings)
    note = findings[0]["deadline_note"]
    assert "pending OJ publication" in note, (
        f"high_risk deadline_note should say 'pending OJ publication'; got: {note!r}"
    )
    assert "pending Council adoption" not in note, (
        f"high_risk deadline_note must not say 'pending Council adoption'; got: {note!r}"
    )


def test_enrich_deadlines_pending_wording_limited_risk():
    """While unenacted, limited-risk deadline notes reference pending OJ publication."""
    from report import _enrich_deadlines
    findings = [{"tier": "limited_risk", "category": "Article 50 Transparency"}]
    _enrich_deadlines(findings)
    note = findings[0]["deadline_note"]
    assert "pending OJ publication" in note, (
        f"limited_risk deadline_note should say 'pending OJ publication'; got: {note!r}"
    )
    assert "pending Council adoption" not in note, (
        f"limited_risk deadline_note must not say 'pending Council adoption'; got: {note!r}"
    )


def test_enrich_deadlines_pending_wording_agent_autonomy():
    """While unenacted, agent_autonomy deadline notes reference pending OJ publication."""
    from report import _enrich_deadlines
    findings = [{"tier": "agent_autonomy", "category": "Article 14 Human Oversight"}]
    _enrich_deadlines(findings)
    note = findings[0]["deadline_note"]
    assert "pending OJ publication" in note, (
        f"agent_autonomy deadline_note should say 'pending OJ publication'; got: {note!r}"
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
    import omnibus
    import remediation_plan
    expected = (omnibus.ANNEX_III_PROSE if omnibus.OMNIBUS_ENACTED
                else omnibus.ORIGINAL_PROSE)
    assert remediation_plan.DEADLINE_HIGH_RISK == expected


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
