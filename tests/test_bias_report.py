"""Tests for bias report formatting (text, JSON, Annex IV)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))


def _mock_crowspairs_result():
    return {
        "status": "ok",
        "benchmark": "crowspairs",
        "method": "logprob",
        "method_description": "Log-probability, mean per-token normalised",
        "scores": {
            "gender": {"score": 62, "ci_lower": 0.48, "ci_upper": 0.74, "n": 26, "confidence": "moderate"},
            "race": {"score": 58, "ci_lower": 0.42, "ci_upper": 0.72, "n": 18, "confidence": "moderate"},
        },
        "overall_score": 60,
        "overall_ci": {"lower": 52.0, "upper": 68.0},
        "pairs_evaluated": 44,
        "pairs_skipped": 6,
        "categories_excluded": [],
        "interpretation": "Score of 50 = no bias.",
        "limitations": ["CrowS-Pairs has known reliability issues"],
        "citation": "Nangia et al. (2020)",
    }


def _mock_bbq_result():
    return {
        "status": "ok",
        "benchmark": "bbq",
        "method": "question-answering",
        "method_description": "BBQ multiple-choice QA",
        "scores": {
            "ambiguous": {
                "gender": {"bias_score": 34, "ci_lower": 0.2, "ci_upper": 0.5, "n": 15, "confidence": "moderate"},
            },
            "disambiguated": {
                "gender": {"accuracy": 88, "bias_override_rate": 12, "ci_lower": 0.04, "ci_upper": 0.28, "n": 15, "confidence": "moderate"},
            },
        },
        "overall_ambiguous_bias": 34,
        "overall_disambiguated_accuracy": 88,
        "items_evaluated": 30,
        "items_skipped": 0,
        "interpretation": "Ambiguous: 0% = ideal.",
        "limitations": ["English-only"],
        "citation": "Parrish et al. (2022)",
    }


def test_format_text_report():
    """Text report contains key sections."""
    from bias_report import format_text_report
    text = format_text_report(
        crowspairs=_mock_crowspairs_result(),
        bbq=_mock_bbq_result(),
        model="llama3",
        endpoint="http://localhost:11434",
    )
    assert "CrowS-Pairs" in text
    assert "BBQ" in text
    assert "gender" in text
    assert "62" in text
    assert "CI" in text or "ci" in text.lower()
    print("✓ Report: text format contains key sections")


def test_format_json_report():
    """JSON report has correct envelope structure."""
    from bias_report import format_json_report
    data = format_json_report(
        crowspairs=_mock_crowspairs_result(),
        bbq=_mock_bbq_result(),
        model="llama3",
        endpoint="http://localhost:11434",
    )
    assert "benchmarks" in data
    assert "crowspairs" in data["benchmarks"]
    assert "bbq" in data["benchmarks"]
    assert "reproducibility" in data
    assert "model" in data["reproducibility"]
    print("✓ Report: JSON format has correct structure")


def test_format_annex_iv():
    """Annex IV output contains required documentation sections."""
    from bias_report import format_annex_iv
    text = format_annex_iv(
        crowspairs=_mock_crowspairs_result(),
        bbq=_mock_bbq_result(),
        model="llama3",
        endpoint="http://localhost:11434",
    )
    assert "Article 10" in text or "Annex IV" in text
    assert "Methodology" in text
    assert "Results" in text
    assert "Limitations" in text
    assert "Follow-Up" in text or "follow-up" in text.lower()
    print("✓ Report: Annex IV format contains required sections")


def test_reproducibility_metadata():
    """Reproducibility metadata includes model, timestamp, version."""
    from bias_report import build_reproducibility_metadata
    meta = build_reproducibility_metadata(model="llama3", endpoint="http://localhost:11434")
    assert meta["model"] == "llama3"
    assert "timestamp" in meta
    assert "regula_version" in meta
    assert "python_version" in meta
    assert "platform" in meta
    print("✓ Report: reproducibility metadata complete")


if __name__ == "__main__":
    test_format_text_report()
    test_format_json_report()
    test_format_annex_iv()
    test_reproducibility_metadata()
    print("\nAll bias_report tests passed!")
