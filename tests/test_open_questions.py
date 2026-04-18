"""Tests for open question flagging on low-confidence findings."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))


def test_high_confidence_not_open_question():
    finding = {"confidence_score": 75, "tier": "high_risk"}
    from report import _is_open_question
    assert _is_open_question(finding) is False


def test_low_confidence_is_open_question():
    finding = {"confidence_score": 45, "tier": "limited_risk"}
    from report import _is_open_question
    assert _is_open_question(finding) is True


def test_prohibited_never_open_question():
    finding = {"confidence_score": 30, "tier": "prohibited"}
    from report import _is_open_question
    assert _is_open_question(finding) is False


def test_boundary_60_not_open_question():
    finding = {"confidence_score": 60, "tier": "high_risk"}
    from report import _is_open_question
    assert _is_open_question(finding) is False


def test_suppressed_not_open_question():
    finding = {"confidence_score": 30, "tier": "high_risk", "suppressed": True}
    from report import _is_open_question
    assert _is_open_question(finding) is False
