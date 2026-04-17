# regula-ignore
"""Tests for risk_decisions.py — annotation parser for regula-ignore / regula-accept.

Standards: ISO 42001 Clause 6.1.3 (risk acceptance), NIST AI RMF MANAGE.
"""
import sys
from pathlib import Path
from datetime import date, timedelta

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from risk_decisions import parse_annotations, build_suppression_set, RiskDecision, record_feedback, load_feedback


# ── 1. Bare ignore ─────────────────────────────────────────────────

def test_bare_ignore_still_works():
    """Bare `# regula-ignore` -> pattern='*', warning about no rationale."""
    lines = ["x = do_something()  # regula-ignore"]
    decisions = parse_annotations(lines, "app.py")
    assert len(decisions) == 1
    d = decisions[0]
    assert d.dtype == "ignore"
    assert d.pattern == "*"
    assert d.warning is not None and "rationale" in d.warning.lower()
    assert d.error is None


# ── 2. Ignore with pattern and rationale ───────────────────────────

def test_ignore_with_pattern_and_rationale():
    """Full ignore with rationale -> no warning."""
    lines = ["x = score()  # regula-ignore: employment -- test fixture, not production code"]
    decisions = parse_annotations(lines, "test_app.py")
    assert len(decisions) == 1
    d = decisions[0]
    assert d.dtype == "ignore"
    assert d.pattern == "employment"
    assert d.rationale == "test fixture, not production code"
    assert d.warning is None
    assert d.error is None


# ── 3. Ignore with pattern but no rationale ────────────────────────

def test_ignore_with_pattern_no_rationale():
    """Pattern but no rationale -> warning."""
    lines = ["x = score()  # regula-ignore: employment"]
    decisions = parse_annotations(lines, "app.py")
    assert len(decisions) == 1
    d = decisions[0]
    assert d.dtype == "ignore"
    assert d.pattern == "employment"
    assert d.rationale is None
    assert d.warning is not None and "rationale" in d.warning.lower()
    assert d.error is None


# ── 4. Accept with all fields ──────────────────────────────────────

def test_accept_full_annotation():
    """All fields present -> no error, is_valid_accept() True."""
    lines = [
        "model = train()  # regula-accept: employment "
        "-- risk accepted per board review | owner=@alice | review=2027-06-01"
    ]
    decisions = parse_annotations(lines, "train.py")
    assert len(decisions) == 1
    d = decisions[0]
    assert d.dtype == "accept"
    assert d.pattern == "employment"
    assert d.rationale == "risk accepted per board review"
    assert d.owner == "@alice"
    assert d.review_date == "2027-06-01"
    assert d.error is None
    assert d.is_valid_accept()


# ── 5. Accept missing owner ────────────────────────────────────────

def test_accept_missing_owner():
    """No owner= -> error mentioning 'owner', is_valid_accept() False."""
    lines = [
        "x = predict()  # regula-accept: employment "
        "-- accepted risk | review=2027-06-01"
    ]
    decisions = parse_annotations(lines, "app.py")
    assert len(decisions) == 1
    d = decisions[0]
    assert d.error is not None and "owner" in d.error.lower()
    assert not d.is_valid_accept()


# ── 6. Accept missing review date ─────────────────────────────────

def test_accept_missing_review_date():
    """No review= -> error mentioning 'review', is_valid_accept() False."""
    lines = [
        "x = predict()  # regula-accept: employment "
        "-- accepted risk | owner=@bob"
    ]
    decisions = parse_annotations(lines, "app.py")
    assert len(decisions) == 1
    d = decisions[0]
    assert d.error is not None and "review" in d.error.lower()
    assert not d.is_valid_accept()


# ── 7. Accept overdue ──────────────────────────────────────────────

def test_accept_overdue():
    """Past review date -> is_overdue() True."""
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    lines = [
        f"x = predict()  # regula-accept: employment "
        f"-- accepted risk | owner=@charlie | review={yesterday}"
    ]
    decisions = parse_annotations(lines, "app.py")
    assert len(decisions) == 1
    assert decisions[0].is_overdue() is True


# ── 8. Accept not overdue ─────────────────────────────────────────

def test_accept_not_overdue():
    """Future review date -> is_overdue() False."""
    future = (date.today() + timedelta(days=365)).isoformat()
    lines = [
        f"x = predict()  # regula-accept: employment "
        f"-- accepted risk | owner=@dave | review={future}"
    ]
    decisions = parse_annotations(lines, "app.py")
    assert len(decisions) == 1
    assert decisions[0].is_overdue() is False


# ── 9. Multiple annotations ───────────────────────────────────────

def test_multiple_annotations_in_file():
    """Two annotations on different lines, correct line numbers."""
    lines = [
        "import os",
        "x = score()  # regula-ignore: employment -- test fixture",
        "y = predict()",
        "z = train()  # regula-accept: social_scoring "
        "-- accepted per review | owner=@eve | review=2027-01-01",
    ]
    decisions = parse_annotations(lines, "multi.py")
    assert len(decisions) == 2
    assert decisions[0].line == 2
    assert decisions[0].pattern == "employment"
    assert decisions[1].line == 4
    assert decisions[1].pattern == "social_scoring"


# ── 10. to_dict roundtrip ─────────────────────────────────────────

def test_to_dict_roundtrip():
    """Serialisation includes all fields."""
    lines = [
        "x = predict()  # regula-accept: employment "
        "-- board approved | owner=@frank | review=2027-12-31"
    ]
    decisions = parse_annotations(lines, "ser.py")
    d = decisions[0].to_dict()
    assert d["dtype"] == "accept"
    assert d["file"] == "ser.py"
    assert d["line"] == 1
    assert d["pattern"] == "employment"
    assert d["rationale"] == "board approved"
    assert d["owner"] == "@frank"
    assert d["review_date"] == "2027-12-31"
    assert d["error"] is None
    assert d["warning"] is None
    assert "raw" in d


# ── 11. build_suppression_set ──────────────────────────────────────

def test_build_suppression_set():
    """ignore adds to set, valid accept adds, invalid accept does NOT."""
    lines = [
        "a = f()  # regula-ignore: employment -- test fixture",
        "b = g()  # regula-accept: social_scoring "
        "-- ok | owner=@gina | review=2027-06-01",
        "c = h()  # regula-accept: biometric_categorisation "
        "-- missing owner | review=2027-06-01",
    ]
    decisions = parse_annotations(lines, "mix.py")
    suppressed = build_suppression_set(decisions)
    assert "employment" in suppressed, "ignore should suppress"
    assert "social_scoring" in suppressed, "valid accept should suppress"
    assert "biometric_categorisation" not in suppressed, "invalid accept must NOT suppress"


# ── 12. findings_view partitions accepted ─────────────────────────

def test_findings_view_partitions_accepted():
    """findings_view.py separates active, suppressed (ignore), and accepted."""
    from findings_view import partition_findings

    findings = [
        {"tier": "high_risk", "suppressed": False, "confidence_score": 70,
         "risk_decision": None},
        {"tier": "high_risk", "suppressed": True, "confidence_score": 65,
         "risk_decision": {"dtype": "ignore", "rationale": "test fixture"}},
        {"tier": "high_risk", "suppressed": True, "confidence_score": 72,
         "risk_decision": {"dtype": "accept", "owner": "@kuziva",
                           "review_date": "2099-12-31", "overdue": False}},
    ]
    view = partition_findings(findings)
    assert len(view["active"]) == 1
    assert len(view["suppressed"]) == 1  # ignore only
    assert len(view["accepted"]) == 1    # accept only


# ── 13. evidence pack includes risk-decisions.json ───────────────

def test_evidence_pack_includes_risk_decisions():
    """Evidence pack must contain 07-risk-decisions.json (Article 11 + Annex IV)."""
    import json
    import tempfile
    from evidence_pack import generate_evidence_pack

    with tempfile.TemporaryDirectory() as tmpdir:
        example = str(ROOT / "examples" / "cv-screening-app")
        result = generate_evidence_pack(example, output_dir=tmpdir)
        pack_path = Path(result["pack_path"])

        rd_path = pack_path / "07-risk-decisions.json"
        assert rd_path.exists(), "07-risk-decisions.json missing from evidence pack"

        rd = json.loads(rd_path.read_text())
        assert rd["schema_version"] == "1.0"
        assert "generated_at" in rd
        assert "suppressed_findings" in rd
        assert "accepted_risks" in rd
        assert "summary" in rd
        assert "total_suppressed" in rd["summary"]
        assert "total_accepted" in rd["summary"]
        assert "accepted_overdue" in rd["summary"]

        # Check it's in the manifest
        manifest = json.loads((pack_path / "manifest.json").read_text())
        filenames = [f["filename"] for f in manifest["files"]]
        assert "07-risk-decisions.json" in filenames


# ── 14. record_feedback creates file ─────────────────────────────

def test_record_feedback_creates_file():
    """record_feedback writes to ~/.regula/feedback.json."""
    import tempfile
    from unittest.mock import patch

    with tempfile.TemporaryDirectory() as tmpdir:
        mock_home = Path(tmpdir)
        with patch("risk_decisions.Path.home", return_value=mock_home):
            record_feedback(
                kind="false-positive",
                pattern="employment",
                file="app.py",
                line=42,
                confidence=72,
                tier="WARN",
                rationale="test fixture",
            )
            fb_path = mock_home / ".regula" / "feedback.json"
            assert fb_path.exists(), "feedback.json was not created"
            import json
            records = json.loads(fb_path.read_text())
            assert len(records) == 1
            assert records[0]["kind"] == "false-positive"
            assert records[0]["pattern"] == "employment"
            assert records[0]["file"] == "app.py"
            assert records[0]["line"] == 42
            assert records[0]["confidence"] == 72
            assert records[0]["tier"] == "WARN"
            assert records[0]["rationale"] == "test fixture"
            assert "timestamp" in records[0]


# ── 15. record_feedback appends to existing ──────────────────────

def test_record_feedback_appends():
    """Subsequent calls append to the same file."""
    import tempfile
    from unittest.mock import patch

    with tempfile.TemporaryDirectory() as tmpdir:
        mock_home = Path(tmpdir)
        with patch("risk_decisions.Path.home", return_value=mock_home):
            record_feedback(kind="suppress", pattern="employment",
                            file="a.py", line=1)
            record_feedback(kind="accept", pattern="biometrics",
                            file="b.py", line=10)
            fb_path = mock_home / ".regula" / "feedback.json"
            import json
            records = json.loads(fb_path.read_text())
            assert len(records) == 2
            assert records[0]["pattern"] == "employment"
            assert records[1]["pattern"] == "biometrics"


# ── 16. load_feedback reads records ──────────────────────────────

def test_load_feedback_reads_records():
    """load_feedback returns stored records."""
    import tempfile
    from unittest.mock import patch

    with tempfile.TemporaryDirectory() as tmpdir:
        mock_home = Path(tmpdir)
        with patch("risk_decisions.Path.home", return_value=mock_home):
            record_feedback(kind="false-positive", pattern="credit_scoring",
                            file="c.py", line=5)
            records = load_feedback()
            assert len(records) == 1
            assert records[0]["kind"] == "false-positive"


# ── 17. load_feedback returns empty when no file ─────────────────

def test_load_feedback_empty_when_no_file():
    """load_feedback returns [] when ~/.regula/feedback.json does not exist."""
    import tempfile
    from unittest.mock import patch

    with tempfile.TemporaryDirectory() as tmpdir:
        mock_home = Path(tmpdir)
        with patch("risk_decisions.Path.home", return_value=mock_home):
            records = load_feedback()
            assert records == []
