# regula-ignore
#!/usr/bin/env python3
"""Tests for Regula session aggregation logic."""

import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from session import aggregate_session, format_session_text

passed = 0
failed = 0


def assert_eq(actual, expected, msg=""):
    global passed, failed
    if actual == expected:
        passed += 1
    else:
        failed += 1
        print(f"  FAIL: {msg} — expected {expected!r}, got {actual!r}")


def assert_true(val, msg=""):
    assert_eq(val, True, msg)


def assert_in(needle, haystack, msg=""):
    global passed, failed
    if needle in haystack:
        passed += 1
    else:
        failed += 1
        print(f"  FAIL: {msg} — {needle!r} not found in {haystack!r}")


# ── Empty / nonexistent session ────────────────────────────────────────

def test_aggregate_empty_session():
    """Nonexistent session_id returns events=0, risk_profile='none'."""
    with patch("session.query_events", return_value=[]):
        result = aggregate_session(session_id="nonexistent-id-12345")
    assert_eq(result["session_id"], "nonexistent-id-12345", "session_id preserved")
    assert_eq(result["events"], 0, "empty session has 0 events")
    assert_eq(result["risk_profile"], "none", "empty session risk_profile is 'none'")
    print("✓ aggregate_empty_session")


# ── Result structure ───────────────────────────────────────────────────

def test_aggregate_session_structure():
    """Full result has all expected keys."""
    events = [
        {
            "event_type": "classification",
            "session_id": "sess-1",
            "timestamp": "2026-03-31T00:00:00+00:00",
            "data": {"tier": "high_risk", "category": "Biometrics", "tool_name": "scanner"},
        },
        {
            "event_type": "tool_use",
            "session_id": "sess-1",
            "timestamp": "2026-03-31T00:01:00+00:00",
            "data": {"tier": "minimal_risk", "tool_name": "linter"},
        },
    ]
    with patch("session.query_events", return_value=events):
        result = aggregate_session(session_id="sess-1")

    expected_keys = {
        "session_id", "time_range", "total_events", "session_risk",
        "blocked_count", "high_risk_count", "limited_risk_count",
        "tool_use_count", "domains_touched", "tiers_distribution",
        "tools_used", "blocked_details", "high_risk_details",
    }
    for key in expected_keys:
        assert_in(key, result, f"result has key '{key}'")
    print("✓ aggregate_session_structure")


# ── Risk profile: critical ─────────────────────────────────────────────

def test_risk_profile_critical():
    """Blocked events produce session_risk='critical'."""
    events = [
        {
            "event_type": "blocked",
            "session_id": "sess-b",
            "timestamp": "2026-03-31T00:00:00+00:00",
            "data": {"description": "Prohibited social scoring", "indicators": ["social_scoring"]},
        },
    ]
    with patch("session.query_events", return_value=events):
        result = aggregate_session(session_id="sess-b")
    assert_eq(result["session_risk"], "critical", "blocked -> critical")
    assert_eq(result["blocked_count"], 1, "blocked_count is 1")
    assert_eq(len(result["blocked_details"]), 1, "blocked_details has 1 entry")
    print("✓ risk_profile_critical")


# ── Risk profile: high ─────────────────────────────────────────────────

def test_risk_profile_high():
    """High-risk classification events produce session_risk='high'."""
    events = [
        {
            "event_type": "classification",
            "session_id": "sess-h",
            "timestamp": "2026-03-31T00:00:00+00:00",
            "data": {"tier": "high_risk", "category": "Employment", "description": "CV screening"},
        },
    ]
    with patch("session.query_events", return_value=events):
        result = aggregate_session(session_id="sess-h")
    assert_eq(result["session_risk"], "high", "high_risk classification -> high")
    assert_eq(result["high_risk_count"], 1, "high_risk_count is 1")
    assert_in("Employment", result["domains_touched"], "domains_touched includes Employment")
    print("✓ risk_profile_high")


# ── Risk profile: moderate ─────────────────────────────────────────────

def test_risk_profile_moderate():
    """Limited-risk only sessions produce session_risk='moderate'."""
    events = [
        {
            "event_type": "classification",
            "session_id": "sess-m",
            "timestamp": "2026-03-31T00:00:00+00:00",
            "data": {"tier": "limited_risk", "category": "Chatbot"},
        },
    ]
    with patch("session.query_events", return_value=events):
        result = aggregate_session(session_id="sess-m")
    assert_eq(result["session_risk"], "moderate", "limited_risk only -> moderate")
    assert_eq(result["limited_risk_count"], 1, "limited_risk_count is 1")
    print("✓ risk_profile_moderate")


# ── Risk profile: low ──────────────────────────────────────────────────

def test_risk_profile_low():
    """Tool-use only sessions produce session_risk='low'."""
    events = [
        {
            "event_type": "tool_use",
            "session_id": "sess-l",
            "timestamp": "2026-03-31T00:00:00+00:00",
            "data": {"tier": "minimal_risk", "tool_name": "formatter"},
        },
    ]
    with patch("session.query_events", return_value=events):
        result = aggregate_session(session_id="sess-l")
    assert_eq(result["session_risk"], "low", "tool_use only -> low")
    assert_eq(result["tool_use_count"], 1, "tool_use_count is 1")
    print("✓ risk_profile_low")


# ── Domain counting ────────────────────────────────────────────────────

def test_domains_counted():
    """Multiple high-risk events in different categories count correctly."""
    events = [
        {
            "event_type": "classification",
            "session_id": "sess-d",
            "timestamp": "2026-03-31T00:00:00+00:00",
            "data": {"tier": "high_risk", "category": "Employment"},
        },
        {
            "event_type": "classification",
            "session_id": "sess-d",
            "timestamp": "2026-03-31T00:01:00+00:00",
            "data": {"tier": "high_risk", "category": "Employment"},
        },
        {
            "event_type": "classification",
            "session_id": "sess-d",
            "timestamp": "2026-03-31T00:02:00+00:00",
            "data": {"tier": "high_risk", "category": "Biometrics"},
        },
    ]
    with patch("session.query_events", return_value=events):
        result = aggregate_session(session_id="sess-d")
    assert_eq(result["domains_touched"].get("Employment"), 2, "Employment counted twice")
    assert_eq(result["domains_touched"].get("Biometrics"), 1, "Biometrics counted once")
    print("✓ domains_counted")


# ── Tools used tracking ────────────────────────────────────────────────

def test_tools_used_tracked():
    """Tools used counter aggregates tool_name from event data."""
    events = [
        {
            "event_type": "tool_use",
            "session_id": "sess-t",
            "timestamp": "2026-03-31T00:00:00+00:00",
            "data": {"tier": "minimal_risk", "tool_name": "scanner"},
        },
        {
            "event_type": "tool_use",
            "session_id": "sess-t",
            "timestamp": "2026-03-31T00:01:00+00:00",
            "data": {"tier": "minimal_risk", "tool_name": "scanner"},
        },
        {
            "event_type": "classification",
            "session_id": "sess-t",
            "timestamp": "2026-03-31T00:02:00+00:00",
            "data": {"tier": "limited_risk", "tool_name": "chatbot"},
        },
    ]
    with patch("session.query_events", return_value=events):
        result = aggregate_session(session_id="sess-t")
    assert_eq(result["tools_used"].get("scanner"), 2, "scanner used twice")
    assert_eq(result["tools_used"].get("chatbot"), 1, "chatbot used once")
    print("✓ tools_used_tracked")


# ── Aggregate mode (no session_id) ────────────────────────────────────

def test_aggregate_no_session_id():
    """When session_id is None, result uses 'aggregate' as session_id."""
    with patch("session.query_events", return_value=[]):
        result = aggregate_session(session_id=None)
    # Empty events path returns early with session_id=None
    assert_eq(result["session_id"], None, "None session_id preserved in empty path")
    assert_eq(result["risk_profile"], "none", "empty aggregate -> none")
    print("✓ aggregate_no_session_id")


# ── format_session_text ────────────────────────────────────────────────

def test_format_session_text_produces_string():
    """format_session_text returns a non-empty string with expected sections."""
    profile = {
        "session_id": "test-sess",
        "time_range": "last 8 hours",
        "total_events": 5,
        "session_risk": "high",
        "blocked_count": 0,
        "high_risk_count": 3,
        "limited_risk_count": 2,
        "tool_use_count": 0,
        "domains_touched": {"Employment": 2, "Biometrics": 1},
        "tiers_distribution": {"high_risk": 3, "limited_risk": 2},
        "tools_used": {"scanner": 3},
        "blocked_details": [],
        "high_risk_details": [
            {"category": "Employment", "description": "CV screening tool"},
        ],
    }
    text = format_session_text(profile)
    assert_true(isinstance(text, str), "output is a string")
    assert_true(len(text) > 0, "output is non-empty")
    assert_in("test-sess", text, "session_id in output")
    assert_in("HIGH", text, "risk label in output")
    assert_in("Employment", text, "domain name in output")
    assert_in("scanner", text, "tool name in output")
    print("✓ format_session_text_produces_string")


def test_format_session_text_blocked():
    """format_session_text renders blocked details when present."""
    profile = {
        "session_id": "blocked-sess",
        "time_range": "last 8 hours",
        "total_events": 1,
        "session_risk": "critical",
        "blocked_count": 1,
        "high_risk_count": 0,
        "limited_risk_count": 0,
        "tool_use_count": 0,
        "domains_touched": {},
        "tiers_distribution": {"prohibited": 1},
        "tools_used": {},
        "blocked_details": [{"description": "Social scoring detected", "indicators": ["social_scoring"]}],
        "high_risk_details": [],
    }
    text = format_session_text(profile)
    assert_in("CRITICAL", text, "CRITICAL label in output")
    assert_in("Social scoring detected", text, "blocked description in output")
    print("✓ format_session_text_blocked")


# ── Priority: blocked overrides high_risk ──────────────────────────────

def test_blocked_overrides_high_risk():
    """Session with both blocked and high-risk events is 'critical'."""
    events = [
        {
            "event_type": "blocked",
            "session_id": "sess-mix",
            "timestamp": "2026-03-31T00:00:00+00:00",
            "data": {"description": "Prohibited", "indicators": []},
        },
        {
            "event_type": "classification",
            "session_id": "sess-mix",
            "timestamp": "2026-03-31T00:01:00+00:00",
            "data": {"tier": "high_risk", "category": "Employment"},
        },
    ]
    with patch("session.query_events", return_value=events):
        result = aggregate_session(session_id="sess-mix")
    assert_eq(result["session_risk"], "critical", "blocked + high_risk -> critical")
    print("✓ blocked_overrides_high_risk")


if __name__ == "__main__":
    tests = [
        test_aggregate_empty_session,
        test_aggregate_session_structure,
        test_risk_profile_critical,
        test_risk_profile_high,
        test_risk_profile_moderate,
        test_risk_profile_low,
        test_domains_counted,
        test_tools_used_tracked,
        test_aggregate_no_session_id,
        test_format_session_text_produces_string,
        test_format_session_text_blocked,
        test_blocked_overrides_high_risk,
    ]

    print(f"Running {len(tests)} session aggregation tests...\n")

    for test in tests:
        try:
            test()
        except Exception as e:
            failed += 1
            print(f"  EXCEPTION in {test.__name__}: {e}")

    print(f"\n{'=' * 50}")
    print(f"Results: {passed} passed, {failed} failed ({len(tests)} test functions)")
    if failed:
        print("SOME TESTS FAILED")
        sys.exit(1)
    else:
        print("All tests passed!")
