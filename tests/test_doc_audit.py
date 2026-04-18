# regula-ignore
"""Tests for document quality scoring (doc-audit)."""

import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from doc_audit import ARTICLE_CHECKLISTS, score_document, audit_project


def test_all_articles_have_checklists():
    """Articles 9-15 must all have checklists."""
    for art in range(9, 16):
        assert str(art) in ARTICLE_CHECKLISTS, f"Article {art} missing from ARTICLE_CHECKLISTS"
        checklist = ARTICLE_CHECKLISTS[str(art)]
        assert "name" in checklist
        assert "doc_patterns" in checklist
        assert "sections" in checklist
        assert "depth_terms" in checklist
        assert len(checklist["sections"]) > 0
        assert len(checklist["depth_terms"]) > 0


def test_empty_document_scores_zero():
    """An empty document should score 0 across all dimensions."""
    result = score_document("", "9")
    assert result["coverage"] == 0, f"Expected coverage 0, got {result['coverage']}"
    assert result["depth"] == 0, f"Expected depth 0, got {result['depth']}"
    assert result["structure"] == 0, f"Expected structure 0, got {result['structure']}"
    assert result["total"] == 0, f"Expected total 0, got {result['total']}"


def test_full_document_scores_high():
    """A document with all sections and depth terms should score >= 70."""
    content = """# Risk Management Policy

Version: 1.0
Date: 2026-01-15
Author: AI Safety Team

## Hazard Identification

This section covers hazard identification procedures including risk assessment
and risk register maintenance. We evaluate likelihood and severity of each
identified risk throughout the lifecycle.

## Residual Risk

After mitigation, residual risk is documented. Risk treatment plans are
applied using continuous monitoring.

## Testing

Comprehensive testing procedures ensure all controls are validated.

## Mitigation

Mitigation strategies address identified risks with appropriate controls.
""" + " ".join(["compliance"] * 500)  # pad to get word count up

    result = score_document(content, "9")
    assert result["total"] >= 70, (
        f"Expected total >= 70, got {result['total']} "
        f"(cov={result['coverage']}, dep={result['depth']}, str={result['structure']})"
    )


def test_headings_only_scores_low_depth():
    """A document with headings but minimal content should score low on depth."""
    content = """# Risk Management

## Hazard Identification
## Residual Risk
## Testing
## Mitigation
"""
    result = score_document(content, "9")
    assert result["depth"] <= 10, f"Expected depth <= 10, got {result['depth']}"
    assert result["coverage"] > 0, "Expected some coverage from section keywords"


def test_shallow_document_low_depth():
    """A very short document gets low depth score."""
    content = "This is a brief risk document."
    result = score_document(content, "9")
    assert result["depth"] <= 5, f"Expected depth <= 5, got {result['depth']}"


def test_coverage_plus_depth_plus_structure_equals_total():
    """The three sub-scores must sum to total."""
    content = """# Data Governance
Version: 2.0
Date: 2026-03-01
Author: Data Team

## Training Data
Details about training data quality and annotation processes.
Dataset validation set procedures with demographic analysis and preprocessing.

## Data Quality
Ensuring bias detection and representative sampling.
"""
    result = score_document(content, "10")
    assert result["coverage"] + result["depth"] + result["structure"] == result["total"], (
        f"Sub-scores {result['coverage']}+{result['depth']}+{result['structure']} "
        f"!= total {result['total']}"
    )


def test_audit_project_finds_docs_in_root_and_docs():
    """audit_project should find docs in both project root and docs/ subdirectory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a doc in root
        root_doc = os.path.join(tmpdir, "RISK_MANAGEMENT.md")
        Path(root_doc).write_text("# Risk Management\n## Hazard Identification\n", encoding="utf-8")

        # Create docs/ subdirectory with another doc
        docs_dir = os.path.join(tmpdir, "docs")
        os.makedirs(docs_dir)
        sub_doc = os.path.join(docs_dir, "transparency.md")
        Path(sub_doc).write_text("# Transparency\n## User Instruction\n", encoding="utf-8")

        results = audit_project(tmpdir)
        assert len(results) == 2, f"Expected 2 documents, found {len(results)}"

        filenames = {r["filename"] for r in results}
        assert "RISK_MANAGEMENT.md" in filenames
        assert "transparency.md" in filenames


def test_audit_project_empty_returns_empty():
    """audit_project returns empty list when no compliance docs found."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a non-compliance doc
        Path(os.path.join(tmpdir, "README.md")).write_text("# Hello", encoding="utf-8")
        results = audit_project(tmpdir)
        assert results == [], f"Expected empty list, got {len(results)} results"


def test_unknown_article_returns_zero():
    """Scoring against an unknown article number returns zero with a gap message."""
    result = score_document("some content", "99")
    assert result["total"] == 0
    assert len(result["gaps"]) > 0


def test_structure_scoring():
    """Verify structure scoring components work."""
    # No structure
    result = score_document("plain text without any structure", "9")
    assert result["structure"] == 0

    # With headings, version, date, and author
    content = """# Title
## Section
Version: 1.0
Date: 2026-01-01
Author: Test
"""
    result = score_document(content, "9")
    assert result["structure"] > 0, "Expected non-zero structure score"
