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


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"  PASS  {name}")
            except Exception as e:
                print(f"  FAIL  {name}: {e}")
