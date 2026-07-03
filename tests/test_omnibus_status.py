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
