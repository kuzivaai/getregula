#!/usr/bin/env python3
"""Statistical utilities for bias evaluation.

Provides:
- Wilson score confidence interval for binomial proportions
- Bootstrap confidence interval (percentile method) for aggregate scores
- Sample size confidence labels

All stdlib — zero external dependencies.
"""

import math
import random
import sys
from pathlib import Path
from typing import List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).parent))


def wilson_ci(successes: int, total: int, z: float = 1.96) -> Tuple[float, float]:
    """Wilson score interval for a binomial proportion.

    Parameters
    ----------
    successes : int
        Number of successes (e.g., stereotyped preferences).
    total : int
        Total number of observations.
    z : float
        Z-score for confidence level (default 1.96 = 95%).

    Returns
    -------
    tuple[float, float]
        (lower_bound, upper_bound) as proportions in [0, 1].
    """
    if total == 0:
        return (0.0, 1.0)
    p_hat = successes / total
    z2 = z ** 2
    denom = 1 + z2 / total
    centre = (p_hat + z2 / (2 * total)) / denom
    spread = z * math.sqrt(p_hat * (1 - p_hat) / total + z2 / (4 * total ** 2)) / denom
    return (max(0.0, centre - spread), min(1.0, centre + spread))


def bootstrap_ci(
    values: List[float],
    n_resamples: int = 10_000,
    alpha: float = 0.05,
    seed: Optional[int] = None,
    method: str = "bca",
) -> Tuple[float, float]:
    """Bootstrap confidence interval for the mean of a list of values.

    Parameters
    ----------
    values : list[float]
        Observed values.
    n_resamples : int
        Number of bootstrap resamples.  Default 10,000 per Efron &
        Tibshirani (1993) recommendation for stable 95% CIs.
    alpha : float
        Significance level (default 0.05 = 95% CI).
    seed : int, optional
        Random seed for reproducibility.
    method : str
        "bca" (bias-corrected and accelerated, recommended) or
        "percentile" (simple, for backward compatibility).

    Returns
    -------
    tuple[float, float]
        (lower_bound, upper_bound).
    """
    if not values:
        return (0.0, 1.0)

    rng = random.Random(seed)
    n = len(values)
    means = []
    for _ in range(n_resamples):
        sample = [rng.choice(values) for _ in range(n)]
        means.append(sum(sample) / n)

    means.sort()

    if method == "bca" and n >= 5:
        # --- BCa (bias-corrected and accelerated) interval ---
        # Ref: Efron (1987), "Better Bootstrap Confidence Intervals"
        theta_hat = sum(values) / n

        # Bias correction factor (z0)
        count_below = sum(1 for m in means if m < theta_hat)
        p0 = count_below / n_resamples
        # Clamp to avoid infinite z0 at edges
        p0 = max(1e-6, min(1 - 1e-6, p0))
        z0 = _norm_ppf(p0)

        # Acceleration factor (a) via jackknife
        jackknife_means = []
        for i in range(n):
            jk_sum = sum(values) - values[i]
            jackknife_means.append(jk_sum / (n - 1))
        jk_bar = sum(jackknife_means) / n
        num = sum((jk_bar - jk) ** 3 for jk in jackknife_means)
        den = sum((jk_bar - jk) ** 2 for jk in jackknife_means)
        a = num / (6.0 * den ** 1.5) if den > 0 else 0.0

        # Adjusted percentiles
        z_lo = _norm_ppf(alpha / 2)
        z_hi = _norm_ppf(1 - alpha / 2)

        a1 = _norm_cdf(z0 + (z0 + z_lo) / (1 - a * (z0 + z_lo)))
        a2 = _norm_cdf(z0 + (z0 + z_hi) / (1 - a * (z0 + z_hi)))

        lo_idx = max(0, min(int(math.floor(n_resamples * a1)), n_resamples - 1))
        hi_idx = max(0, min(int(math.ceil(n_resamples * a2)) - 1, n_resamples - 1))
        return (means[lo_idx], means[hi_idx])

    # --- Percentile method (fallback) ---
    lo_idx = int(math.floor(n_resamples * (alpha / 2)))
    hi_idx = int(math.ceil(n_resamples * (1 - alpha / 2))) - 1
    lo_idx = max(0, min(lo_idx, n_resamples - 1))
    hi_idx = max(0, min(hi_idx, n_resamples - 1))
    return (means[lo_idx], means[hi_idx])


def _norm_ppf(p: float) -> float:
    """Approximate inverse normal CDF (percent point function).

    Uses rational approximation from Abramowitz & Stegun (1964), formula 26.2.23.
    Accurate to ~4.5e-4 absolute error.  Stdlib-only — no scipy dependency.
    """
    if p <= 0:
        return -6.0
    if p >= 1:
        return 6.0

    # Coefficients for rational approximation
    c0, c1, c2 = 2.515517, 0.802853, 0.010328
    d1, d2, d3 = 1.432788, 0.189269, 0.001308

    if p < 0.5:
        t = math.sqrt(-2.0 * math.log(p))
        return -(t - (c0 + c1 * t + c2 * t * t) / (1 + d1 * t + d2 * t * t + d3 * t * t * t))
    else:
        t = math.sqrt(-2.0 * math.log(1 - p))
        return t - (c0 + c1 * t + c2 * t * t) / (1 + d1 * t + d2 * t * t + d3 * t * t * t)


def _norm_cdf(x: float) -> float:
    """Approximate normal CDF using math.erf (exact within float precision)."""
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def cohens_h(p1: float, p2: float = 0.5) -> float:
    """Cohen's h effect size for two proportions.

    Measures practical significance of a bias score vs. the no-bias
    baseline of 50%.  Interpretation (Cohen 1988):
    - |h| < 0.2: negligible
    - 0.2 ≤ |h| < 0.5: small
    - 0.5 ≤ |h| < 0.8: medium
    - |h| ≥ 0.8: large

    Parameters
    ----------
    p1 : float
        Observed proportion (e.g., stereotype preference rate).
    p2 : float
        Reference proportion (default 0.5 = no bias).

    Returns
    -------
    float
        Cohen's h value (signed: positive = pro-stereotypical bias).
    """
    p1 = max(0.0, min(1.0, p1))
    p2 = max(0.0, min(1.0, p2))
    return 2 * math.asin(math.sqrt(p1)) - 2 * math.asin(math.sqrt(p2))


def effect_size_label(h: float) -> str:
    """Map Cohen's h to a human-readable effect size label."""
    ah = abs(h)
    if ah < 0.2:
        return "negligible"
    elif ah < 0.5:
        return "small"
    elif ah < 0.8:
        return "medium"
    else:
        return "large"


def confidence_label(n: int) -> str:
    """Map sample size to a human-readable confidence label.

    Thresholds based on binomial CI width at 50% base rate:
    - n < 5:  insufficient (CI width > 60%)
    - n < 10: low (CI width > 40%)
    - n <= 30: moderate (CI width > 20%)
    - n > 30:  high (CI width < 20%)
    """
    if n < 5:
        return "insufficient"
    elif n < 10:
        return "low"
    elif n <= 30:
        return "moderate"
    else:
        return "high"


def require_http_url(url: str) -> None:
    """Reject non-http(s) schemes before urlopen (bandit B310 / semgrep guard).

    Shared by bias_eval.py and bias_bbq.py to avoid duplication.
    """
    from urllib.parse import urlparse
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"Endpoint scheme must be http or https, got: {parsed.scheme!r}")
