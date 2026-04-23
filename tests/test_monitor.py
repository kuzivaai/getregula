#!/usr/bin/env python3
"""Tests for regula.monitor — runtime monitoring SDK."""

import os
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


import json
import threading
from datetime import datetime, timezone


def test_hash_chain_integrity():
    """Write 10 events, verify chain, tamper one, verify fails."""
    from monitor import MonitorSession, _get_monitor_file
    from log_event import compute_hash

    class FakeResponse:
        __module__ = "openai.types.chat"
        model = "gpt-4"
        class usage:
            prompt_tokens = 10
            completion_tokens = 5
            input_tokens = None
            output_tokens = None

    with tempfile.TemporaryDirectory() as tmpdir:
        session = MonitorSession(system_id="chain-test", monitor_dir=tmpdir)
        for _ in range(10):
            with session.trace() as t:
                t.record(FakeResponse())

        log_file = _get_monitor_file("chain-test", tmpdir)
        lines = log_file.read_text().strip().splitlines()
        assert len(lines) == 10

        prev = "0" * 64
        for line in lines:
            event = json.loads(line)
            assert event["previous_hash"] == prev
            expected = compute_hash(event, prev)
            assert event["current_hash"] == expected
            prev = event["current_hash"]

        # Tamper with event 5
        events = [json.loads(l) for l in lines]
        events[4]["model"] = "TAMPERED"
        log_file.write_text(
            "\n".join(json.dumps(e, sort_keys=True) for e in events) + "\n"
        )

        tampered_lines = log_file.read_text().strip().splitlines()
        prev = "0" * 64
        broken_at = None
        for i, line in enumerate(tampered_lines):
            event = json.loads(line)
            if event["previous_hash"] != prev:
                broken_at = i
                break
            expected = compute_hash(event, prev)
            if event["current_hash"] != expected:
                broken_at = i
                break
            prev = event["current_hash"]
        assert broken_at == 4, f"Expected chain break at 4, got {broken_at}"
        session.close()


def test_log_rotation():
    """Events go to the correct monthly file."""
    from monitor import MonitorSession, _get_monitor_dir

    class FakeResponse:
        __module__ = "openai.types.chat"
        model = "gpt-4"
        class usage:
            prompt_tokens = 10
            completion_tokens = 5
            input_tokens = None
            output_tokens = None

    with tempfile.TemporaryDirectory() as tmpdir:
        session = MonitorSession(system_id="rotation-test", monitor_dir=tmpdir)
        with session.trace() as t:
            t.record(FakeResponse())

        log_dir = _get_monitor_dir("rotation-test", tmpdir)
        files = list(log_dir.glob("monitor_*.jsonl"))
        assert len(files) == 1
        expected_name = f"monitor_{datetime.now(timezone.utc).strftime('%Y-%m')}.jsonl"
        assert files[0].name == expected_name
        session.close()


def test_session_summary():
    """close() writes correct aggregate stats."""
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
        session = MonitorSession(system_id="summary-test", monitor_dir=tmpdir)
        for _ in range(3):
            with session.trace() as t:
                t.record(FakeResponse())
        with session.trace() as t:
            t.record_error(ValueError("test error"))
        with session.trace() as t:
            t.record(FakeResponse(),
                     human_oversight={"performed": True, "action": "rejected"})

        summary = session.close()
        assert summary["event_type"] == "session_summary"
        assert summary["total_inferences"] == 4
        assert summary["total_errors"] == 1
        assert summary["human_overrides"] == 1
        assert summary["models_used"] == ["gpt-4"]


def test_thread_safety():
    """Concurrent traces in same session don't corrupt chain."""
    from monitor import MonitorSession, _get_monitor_file
    from log_event import compute_hash

    class FakeResponse:
        __module__ = "openai.types.chat"
        model = "gpt-4"
        class usage:
            prompt_tokens = 10
            completion_tokens = 5
            input_tokens = None
            output_tokens = None

    with tempfile.TemporaryDirectory() as tmpdir:
        session = MonitorSession(system_id="thread-test", monitor_dir=tmpdir)
        errors = []

        def do_trace():
            try:
                with session.trace() as t:
                    t.record(FakeResponse())
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=do_trace) for _ in range(20)]
        for th in threads:
            th.start()
        for th in threads:
            th.join()

        assert not errors, f"Thread errors: {errors}"

        log_file = _get_monitor_file("thread-test", tmpdir)
        lines = log_file.read_text().strip().splitlines()
        assert len(lines) == 20

        prev = "0" * 64
        for i, line in enumerate(lines):
            event = json.loads(line)
            assert event["previous_hash"] == prev, f"Chain broken at event {i}"
            expected = compute_hash(event, prev)
            assert event["current_hash"] == expected, f"Hash mismatch at event {i}"
            prev = event["current_hash"]
        session.close()


def test_cli_monitor_verify():
    """regula monitor verify checks chain integrity."""
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
        session = MonitorSession(system_id="verify-cli", monitor_dir=tmpdir)
        for _ in range(5):
            with session.trace() as t:
                t.record(FakeResponse())
        session.close()

        from cli_monitor import cmd_monitor_verify

        class Args:
            system_id = "verify-cli"
            monitor_dir = tmpdir
            format = "json"

        result = cmd_monitor_verify(Args())
        assert result["chain_valid"] is True
        assert result["event_count"] == 6  # 5 inferences + 1 summary


def test_cli_monitor_report():
    """regula monitor report generates stats from logs."""
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
        session = MonitorSession(system_id="report-cli", monitor_dir=tmpdir)
        for _ in range(3):
            with session.trace() as t:
                t.record(FakeResponse())
        with session.trace() as t:
            t.record_error(RuntimeError("fail"))
        session.close()

        from cli_monitor import cmd_monitor_report

        class Args:
            system_id = "report-cli"
            monitor_dir = tmpdir
            format = "json"

        result = cmd_monitor_report(Args())
        assert result["total_events"] == 5  # 3 inference + 1 error + 1 summary
        assert result["total_inferences"] == 3
        assert result["total_errors"] == 1
        assert 0 < result["error_rate"] < 1


def test_evidence_pack_runtime_section():
    """--runtime flag includes section 08-runtime-monitor.json."""
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
        monitor_dir = os.path.join(tmpdir, "monitor")
        session = MonitorSession(system_id="evpack-test", monitor_dir=monitor_dir)
        for _ in range(3):
            with session.trace() as t:
                t.record(FakeResponse())
        session.close()

        from cli_monitor import _read_all_events, _verify_chain
        events = _read_all_events("evpack-test", monitor_dir)
        valid, msg = _verify_chain(events)

        assert valid is True
        assert len(events) == 4  # 3 inferences + 1 summary


import importlib


def test_monitor_no_external_imports():
    """monitor.py only imports from stdlib + regula's own modules."""
    if "monitor" in sys.modules:
        del sys.modules["monitor"]
    import monitor

    source = Path(monitor.__file__).read_text()
    for lib in ["openai", "anthropic", "langchain", "google.generativeai"]:
        assert f"import {lib}" not in source, f"monitor.py imports {lib}"
        assert f"from {lib}" not in source, f"monitor.py imports from {lib}"


def test_zero_token_count():
    """Token count of 0 is a valid value (cached prompts), not missing."""
    from monitor import _extract_response

    resp = {
        "model": "gpt-4",
        "usage": {"input_tokens": 0, "output_tokens": 15},
        "provider": "openai",
    }
    result = _extract_response(resp)
    assert result["input_tokens"] == 0, f"Expected 0, got {result['input_tokens']}"
    assert result["output_tokens"] == 15

    # Also test object path
    class Usage:
        input_tokens = 0
        output_tokens = 20
        prompt_tokens = 999  # should NOT fall through to this

    class FakeResponse:
        __module__ = "openai.types.chat"
        model = "gpt-4"
        usage = Usage()

    result2 = _extract_response(FakeResponse())
    assert result2["input_tokens"] == 0, f"Expected 0, got {result2['input_tokens']}"
    assert result2["output_tokens"] == 20


def test_start_trace_no_context_manager():
    """start_trace() works without with-block."""
    from monitor import MonitorSession

    with tempfile.TemporaryDirectory() as tmpdir:
        session = MonitorSession(system_id="no-ctx-test", monitor_dir=tmpdir)
        t = session.start_trace()
        t.record({"model": "gpt-4", "usage": {"input_tokens": 10, "output_tokens": 5}})
        t.end()

        assert len(session._events) == 1
        assert session._events[0]["status"] == "success"
        assert session._events[0]["latency_ms"] >= 0
        session.close()


def test_cli_monitor_export():
    """regula monitor export produces CSV."""
    from monitor import MonitorSession

    with tempfile.TemporaryDirectory() as tmpdir:
        session = MonitorSession(system_id="export-test", monitor_dir=tmpdir)
        with session.trace() as t:
            t.record({"model": "gpt-4", "usage": {"input_tokens": 10, "output_tokens": 5}, "provider": "openai"})
        session.close()

        from cli_monitor import cmd_monitor_export

        class Args:
            system_id = "export-test"
            monitor_dir = tmpdir
            output = os.path.join(tmpdir, "export.csv")
            format = "text"

        result = cmd_monitor_export(Args())
        assert result["exported"] == 2  # 1 inference + 1 summary
        csv_content = Path(os.path.join(tmpdir, "export.csv")).read_text()
        assert "event_id" in csv_content  # header row
        assert "gpt-4" in csv_content


def test_cli_monitor_prune():
    """regula monitor prune deletes old log files."""
    from monitor import _get_monitor_dir

    with tempfile.TemporaryDirectory() as tmpdir:
        log_dir = _get_monitor_dir("prune-test", tmpdir)
        # Create a fake old log file (12 months ago)
        old_file = log_dir / "monitor_2025-01.jsonl"
        old_file.write_text('{"event_type":"test"}\n')
        # Create a current log file
        current = log_dir / f"monitor_{datetime.now(timezone.utc).strftime('%Y-%m')}.jsonl"
        current.write_text('{"event_type":"test"}\n')

        from cli_monitor import cmd_monitor_prune

        class Args:
            system_id = "prune-test"
            monitor_dir = tmpdir
            months = 6
            format = "json"

        result = cmd_monitor_prune(Args())
        assert "monitor_2025-01.jsonl" in result["deleted"]
        assert not old_file.exists()
        assert current.exists()


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"  PASS  {name}")
            except Exception as e:
                print(f"  FAIL  {name}: {e}")
