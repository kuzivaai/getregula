#!/usr/bin/env python3
"""Tests for regula.monitor — runtime monitoring SDK."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))


def test_extract_openai_chat_completion():
    """OpenAI Chat Completions: .model, .usage.prompt_tokens, .usage.completion_tokens"""
    from monitor import _extract_response

    class Usage:
        prompt_tokens = 100
        completion_tokens = 50
        input_tokens = None
        output_tokens = None

    class FakeResponse:
        __module__ = "openai.types.chat.chat_completion"
        model = "gpt-4-turbo-2025-04-09"
        usage = Usage()

    result = _extract_response(FakeResponse())
    assert result["model"] == "gpt-4-turbo-2025-04-09"
    assert result["input_tokens"] == 100
    assert result["output_tokens"] == 50
    assert result["provider"] == "openai"


def test_extract_openai_responses_api():
    """OpenAI Responses API: .model, .usage.input_tokens, .usage.output_tokens"""
    from monitor import _extract_response

    class Usage:
        input_tokens = 200
        output_tokens = 80
        prompt_tokens = None
        completion_tokens = None

    class FakeResponse:
        __module__ = "openai.types.responses.response"
        model = "gpt-4o-2025-03-26"
        usage = Usage()

    result = _extract_response(FakeResponse())
    assert result["model"] == "gpt-4o-2025-03-26"
    assert result["input_tokens"] == 200
    assert result["output_tokens"] == 80
    assert result["provider"] == "openai"


def test_extract_anthropic():
    """Anthropic Messages: .model, .usage.input_tokens, .usage.output_tokens"""
    from monitor import _extract_response

    class Usage:
        input_tokens = 150
        output_tokens = 60

    class FakeResponse:
        __module__ = "anthropic.types.message"
        model = "claude-sonnet-4-20250514"
        usage = Usage()

    result = _extract_response(FakeResponse())
    assert result["model"] == "claude-sonnet-4-20250514"
    assert result["input_tokens"] == 150
    assert result["output_tokens"] == 60
    assert result["provider"] == "anthropic"


def test_extract_raw_dict():
    """Raw dict from HTTP client."""
    from monitor import _extract_response

    resp = {
        "model": "gpt-4",
        "usage": {"prompt_tokens": 50, "completion_tokens": 25},
        "provider": "openai",
    }
    result = _extract_response(resp)
    assert result["model"] == "gpt-4"
    assert result["input_tokens"] == 50
    assert result["output_tokens"] == 25
    assert result["provider"] == "openai"


def test_extract_raw_dict_anthropic_naming():
    """Raw dict with Anthropic field names."""
    from monitor import _extract_response

    resp = {
        "model": "claude-sonnet-4-20250514",
        "usage": {"input_tokens": 100, "output_tokens": 40},
    }
    result = _extract_response(resp)
    assert result["model"] == "claude-sonnet-4-20250514"
    assert result["input_tokens"] == 100
    assert result["output_tokens"] == 40
    assert result["provider"] == "unknown"


def test_extract_unknown_object():
    """Unknown object: graceful fallback to nulls."""
    from monitor import _extract_response

    class Mystery:
        __module__ = "some.random.module"

    result = _extract_response(Mystery())
    assert result["model"] is None
    assert result.get("input_tokens") is None
    assert result.get("output_tokens") is None
    assert result["provider"] == "unknown"


def test_extract_no_external_imports():
    """monitor.py must not import openai, anthropic, or any provider SDK."""
    from monitor import _extract_response  # noqa: F401
    assert "openai" not in sys.modules or sys.modules["openai"] is None
    assert "anthropic" not in sys.modules or sys.modules["anthropic"] is None


import tempfile
import time


def test_monitor_session_creation():
    """Tier 2 defaults stored correctly."""
    from monitor import MonitorSession

    with tempfile.TemporaryDirectory() as tmpdir:
        session = MonitorSession(
            system_id="test-bot",
            system_version="1.0.0",
            environment="test",
            consequential=False,
            human_oversight_required=True,
            user_informed_ai=True,
            domain="testing",
            monitor_dir=tmpdir,
        )
        assert session.system_id == "test-bot"
        assert session.system_version == "1.0.0"
        assert session.environment == "test"
        assert session.defaults["consequential"] is False
        assert session.defaults["human_oversight_required"] is True
        assert session.defaults["user_informed_ai"] is True
        assert session.defaults["domain"] == "testing"
        session.close()


def test_trace_captures_latency():
    """Trace context manager records latency_ms > 0."""
    from monitor import MonitorSession

    class FakeResponse:
        __module__ = "openai.types.chat"
        model = "gpt-4"
        class usage:
            prompt_tokens = 10
            completion_tokens = 5
            input_tokens = None
            output_tokens = None

    with tempfile.TemporaryDirectory() as tmpdir:
        session = MonitorSession(
            system_id="latency-test",
            monitor_dir=tmpdir,
        )
        with session.trace() as t:
            time.sleep(0.01)
            t.record(FakeResponse())

        assert len(session._events) == 1
        assert session._events[0]["latency_ms"] >= 10
        session.close()


def test_trace_record_error():
    """record_error captures exception details."""
    from monitor import MonitorSession

    with tempfile.TemporaryDirectory() as tmpdir:
        session = MonitorSession(
            system_id="error-test",
            monitor_dir=tmpdir,
        )
        with session.trace() as t:
            try:
                raise ConnectionError("API timeout")
            except Exception as e:
                t.record_error(e)

        assert len(session._events) == 1
        evt = session._events[0]
        assert evt["status"] == "error"
        assert "API timeout" in evt["error"]
        session.close()


def test_tier3_overrides():
    """Per-event overrides replace session defaults."""
    from monitor import MonitorSession

    class FakeResponse:
        __module__ = "openai.types.chat"
        model = "gpt-4"
        class usage:
            prompt_tokens = 10
            completion_tokens = 5
            input_tokens = None
            output_tokens = None

    with tempfile.TemporaryDirectory() as tmpdir:
        session = MonitorSession(
            system_id="override-test",
            consequential=False,
            monitor_dir=tmpdir,
        )
        with session.trace() as t:
            t.record(FakeResponse(), consequential=True,
                     human_oversight={"performed": True, "action": "rejected",
                                      "reviewer": "role:analyst",
                                      "override_reason": "PII in output"})

        evt = session._events[0]
        assert evt["consequential"] is True
        assert evt["human_oversight"]["performed"] is True
        assert evt["human_oversight"]["action"] == "rejected"
        session.close()


def test_human_oversight_all_actions():
    """All four oversight action types are stored."""
    from monitor import MonitorSession

    class FakeResponse:
        __module__ = "openai.types.chat"
        model = "gpt-4"
        class usage:
            prompt_tokens = 10
            completion_tokens = 5
            input_tokens = None
            output_tokens = None

    with tempfile.TemporaryDirectory() as tmpdir:
        session = MonitorSession(system_id="actions-test", monitor_dir=tmpdir)
        for action in ["approved", "modified", "rejected", "pending"]:
            with session.trace() as t:
                t.record(FakeResponse(),
                         human_oversight={"performed": True, "action": action})
        assert len(session._events) == 4
        actions = [e["human_oversight"]["action"] for e in session._events]
        assert actions == ["approved", "modified", "rejected", "pending"]
        session.close()


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"  PASS  {name}")
            except Exception as e:
                print(f"  FAIL  {name}: {e}")
