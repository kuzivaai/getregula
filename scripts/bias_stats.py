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
    n_resamples: int = 1000,
    alpha: float = 0.05,
    seed: Optional[int] = None,
) -> Tuple[float, float]:
    """Bootstrap confidence interval for the mean of a list of values.

    Uses percentile method (simple, unbiased for symmetric distributions).

    Parameters
    ----------
    values : list[float]
        Observed values.
    n_resamples : int
        Number of bootstrap resamples.
    alpha : float
        Significance level (default 0.05 = 95% CI).
    seed : int, optional
        Random seed for reproducibility.

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
    lo_idx = int(math.floor(n_resamples * (alpha / 2)))
    hi_idx = int(math.ceil(n_resamples * (1 - alpha / 2))) - 1
    lo_idx = max(0, min(lo_idx, n_resamples - 1))
    hi_idx = max(0, min(hi_idx, n_resamples - 1))
    return (means[lo_idx], means[hi_idx])


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
