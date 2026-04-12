"""Tests for bias statistical utilities."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))


def test_wilson_ci_known_values():
    """Wilson CI for known inputs matches hand-calculated values."""
    from bias_stats import wilson_ci
    lo, hi = wilson_ci(7, 10)
    assert 0.35 < lo < 0.42, f"Lower bound {lo} not in expected range"
    assert 0.86 < hi < 0.93, f"Upper bound {hi} not in expected range"
    print("✓ Wilson CI: known values match hand-calculated bounds")


def test_wilson_ci_perfect_score():
    """Wilson CI for 100% success rate."""
    from bias_stats import wilson_ci
    lo, hi = wilson_ci(10, 10)
    assert hi == 1.0
    assert lo > 0.7
    print("✓ Wilson CI: perfect score has upper bound 1.0")


def test_wilson_ci_zero_score():
    """Wilson CI for 0% success rate."""
    from bias_stats import wilson_ci
    lo, hi = wilson_ci(0, 10)
    assert lo == 0.0
    assert hi < 0.3
    print("✓ Wilson CI: zero score has lower bound 0.0")


def test_wilson_ci_zero_total():
    """Wilson CI with zero observations returns full range."""
    from bias_stats import wilson_ci
    lo, hi = wilson_ci(0, 0)
    assert lo == 0.0 and hi == 1.0
    print("✓ Wilson CI: zero observations returns (0.0, 1.0)")


def test_bootstrap_ci_synthetic():
    """Bootstrap CI on synthetic data contains the true mean."""
    from bias_stats import bootstrap_ci
    import random
    random.seed(42)
    values = [0.6 + (random.random() - 0.5) * 0.2 for _ in range(100)]
    true_mean = sum(values) / len(values)
    lo, hi = bootstrap_ci(values, n_resamples=2000, seed=42)
    assert lo < true_mean < hi, f"True mean {true_mean} not in [{lo}, {hi}]"
    print("✓ Bootstrap CI: synthetic data interval contains true mean")


def test_bootstrap_ci_deterministic():
    """Bootstrap CI with same seed produces same result."""
    from bias_stats import bootstrap_ci
    values = [0.5, 0.6, 0.7, 0.4, 0.8]
    r1 = bootstrap_ci(values, seed=123)
    r2 = bootstrap_ci(values, seed=123)
    assert r1 == r2
    print("✓ Bootstrap CI: deterministic with same seed")


def test_bootstrap_ci_empty():
    """Bootstrap CI with empty list returns full range."""
    from bias_stats import bootstrap_ci
    lo, hi = bootstrap_ci([])
    assert lo == 0.0 and hi == 1.0
    print("✓ Bootstrap CI: empty input returns (0.0, 1.0)")


def test_confidence_label():
    """Sample size maps to correct confidence labels."""
    from bias_stats import confidence_label
    assert confidence_label(3) == "insufficient"
    assert confidence_label(7) == "low"
    assert confidence_label(15) == "moderate"
    assert confidence_label(30) == "moderate"
    assert confidence_label(50) == "high"
    print("✓ Confidence labels: correct for all thresholds")


if __name__ == "__main__":
    test_wilson_ci_known_values()
    test_wilson_ci_perfect_score()
    test_wilson_ci_zero_score()
    test_wilson_ci_zero_total()
    test_bootstrap_ci_synthetic()
    test_bootstrap_ci_deterministic()
    test_bootstrap_ci_empty()
    test_confidence_label()
    print("\nAll bias_stats tests passed!")
