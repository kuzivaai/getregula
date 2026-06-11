# regula-ignore
"""Tests for the executive summary report generator."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))


def test_exec_summary_generates_valid_html():
    """exec-summary produces valid HTML with required structural elements."""
    from exec_summary import generate_exec_summary
    html = generate_exec_summary([], "test-project")
    assert "<!DOCTYPE html>" in html
    assert "<html" in html
    assert "<head>" in html
    assert "<body>" in html
    assert "</html>" in html


def test_exec_summary_title_is_indicator_summary():
    """Title must say 'Risk Indicator Summary', not 'compliance report'."""
    from exec_summary import generate_exec_summary
    html = generate_exec_summary([], "test-project")
    assert "AI Act Risk Indicator Summary" in html


def test_exec_summary_subtitle_says_not_legal():
    """Subtitle must say 'not a legal determination'."""
    from exec_summary import generate_exec_summary
    html = generate_exec_summary([], "test-project")
    assert "not a legal determination" in html


def test_exec_summary_article_6_disclaimer():
    """Disclaimer must reference Article 6 and its limitations."""
    from exec_summary import generate_exec_summary
    html = generate_exec_summary([], "test-project")
    assert "Article 6" in html
    assert "significant risk" in html
    assert "contextual determinations" in html


def test_exec_summary_data_residency():
    """Data residency line must state no transmission."""
    from exec_summary import generate_exec_summary
    html = generate_exec_summary([], "test-project")
    assert "No code, findings, or metadata were transmitted" in html


def test_exec_summary_no_conformity_language():
    """Output must NOT contain language implying conformity assessment."""
    from exec_summary import generate_exec_summary
    html = generate_exec_summary([], "test-project")
    # The footer says "not a conformity assessment" — that's a negation, which is fine.
    # But the document must not CLAIM to be one.
    # Split at the negation phrase to check the rest
    before_negation = html.split("not a conformity assessment")[0]
    assert "conformity assessment" not in before_negation, \
        "Document claims to be a conformity assessment before the negation"
    assert "compliance certificate" not in before_negation, \
        "Document claims to be a compliance certificate"


def test_exec_summary_footer_negations():
    """Footer must explicitly negate conformity/legal/certificate claims."""
    from exec_summary import generate_exec_summary
    html = generate_exec_summary([], "test-project")
    assert "not a conformity assessment" in html
    assert "not a" in html and "compliance certificate" in html
    assert "automated scan summary" in html


def test_exec_summary_version_stamp():
    """Output must include Regula version."""
    from exec_summary import generate_exec_summary
    from constants import VERSION
    html = generate_exec_summary([], "test-project")
    assert f"v{VERSION}" in html


def test_exec_summary_with_findings():
    """Output with findings shows the highest tier and finding details."""
    from exec_summary import generate_exec_summary
    findings = [
        {
            "tier": "high_risk",
            "category": "employment",
            "file": "app/screening.py",
            "line": 42,
            "description": "Resume screening function detected",
            "confidence_score": 75,
            "applicable_articles": ["Article 6", "Annex III Category 4"],
        }
    ]
    html = generate_exec_summary(findings, "test-project")
    assert "HIGH RISK" in html or "HIGH_RISK" in html
    assert "screening.py" in html
    assert "employment" in html.lower() or "Employment" in html
