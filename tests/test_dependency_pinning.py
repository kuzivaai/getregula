"""Tests for the pinning-level classifier in scripts/dependency_scan.py.

Covers the `bounded-range` distinction introduced alongside the pyproject
dependency tightening on 2026-04-16. Kept out of test_classification.py
per the project convention that new tests live in dedicated files.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from dependency_scan import (  # noqa: E402
    _classify_pinning_req,
    calculate_pinning_score,
)


# ── Classifier behaviour ──────────────────────────────────────────


def test_classify_none_is_unpinned():
    assert _classify_pinning_req(None) == ("unpinned", None)


def test_classify_empty_is_unpinned():
    assert _classify_pinning_req("") == ("unpinned", None)


def test_classify_exact():
    pinning, version = _classify_pinning_req("==1.6.2")
    assert pinning == "exact"
    assert version == "1.6.2"


def test_classify_compatible():
    pinning, version = _classify_pinning_req("~=2.8")
    assert pinning == "compatible"
    assert version == "2.8"


def test_classify_compatible_with_minor():
    pinning, version = _classify_pinning_req("~=6.0")
    assert pinning == "compatible"
    assert version == "6.0"


def test_classify_hash():
    pinning, _ = _classify_pinning_req("--hash=sha256:abc")
    assert pinning == "hash"


def test_classify_unbounded_lower_is_range():
    """`>=X` alone has no upper bound — flagged as plain range."""
    pinning, version = _classify_pinning_req(">=7.0")
    assert pinning == "range"
    assert version == "7.0"


def test_classify_bounded_range_explicit():
    """`>=X,<Y` has both bounds — classified as bounded-range."""
    pinning, version = _classify_pinning_req(">=62,<69")
    assert pinning == "bounded-range"
    assert version == "62"


def test_classify_bounded_range_with_lte():
    pinning, _ = _classify_pinning_req(">=1.0,<=2.0")
    assert pinning == "bounded-range"


def test_classify_bounded_range_gt_lt():
    pinning, _ = _classify_pinning_req(">1.0,<3.0")
    assert pinning == "bounded-range"


def test_classify_unbounded_upper_is_range():
    """`<X` alone (no lower bound) is still a one-sided range."""
    pinning, _ = _classify_pinning_req("<3.0")
    assert pinning == "range"


# ── Scoring behaviour ─────────────────────────────────────────────


def test_bounded_range_weight_is_between_compatible_and_range():
    """bounded-range (50) sits between range (30) and compatible (60)."""
    compat = calculate_pinning_score(
        [{"name": "x", "pinning": "compatible", "is_ai": False}]
    )
    bounded = calculate_pinning_score(
        [{"name": "x", "pinning": "bounded-range", "is_ai": False}]
    )
    ranged = calculate_pinning_score(
        [{"name": "x", "pinning": "range", "is_ai": False}]
    )
    assert compat > bounded > ranged
    assert bounded == 50
    assert compat == 60
    assert ranged == 30


def test_lockfile_bonus_applied():
    with_lock = calculate_pinning_score(
        [{"name": "x", "pinning": "compatible", "is_ai": False}],
        has_lockfile=True,
    )
    without_lock = calculate_pinning_score(
        [{"name": "x", "pinning": "compatible", "is_ai": False}],
        has_lockfile=False,
    )
    assert with_lock == without_lock + 20


def test_score_capped_at_100():
    score = calculate_pinning_score(
        [{"name": "x", "pinning": "hash", "is_ai": False}],
        has_lockfile=True,
    )
    assert score == 100
