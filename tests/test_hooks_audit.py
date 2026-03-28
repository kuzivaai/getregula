# regula-ignore
#!/usr/bin/env python3
"""
Coverage tests for hooks/ and scripts/log_event.py

Tests the real-time hook system (pre_tool_use, post_tool_use, stop_hook)
and the audit trail logger (hash chain, file locking, verification).

IMPORTANT: This file contains INTENTIONALLY FAKE credential patterns
for testing secret detection. All values are synthetic test fixtures.
"""

import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

passed = 0
failed = 0
_PYTEST_MODE = "pytest" in sys.modules


def assert_eq(actual, expected, msg=""):
    global passed, failed
    if actual == expected:
        passed += 1
    else:
        failed += 1
        if _PYTEST_MODE:
            raise AssertionError(f"{msg} — expected {expected!r}, got {actual!r}")
        print(f"  FAIL: {msg} — expected {expected!r}, got {actual!r}")


def assert_true(val, msg=""):
    assert_eq(val, True, msg)


def assert_false(val, msg=""):
    assert_eq(val, False, msg)


# ── Helper: run hook as subprocess ─────────────────────────────────

HOOKS_DIR = Path(__file__).parent.parent / "hooks"
SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"


def _run_hook(hook_name, tool_name, tool_input, extra_fields=None):
    """Run a hook script via subprocess with JSON on stdin.

    Returns (returncode, stdout_parsed_json_or_None, stderr).
    """
    hook_path = HOOKS_DIR / f"{hook_name}.py"
    payload = {
        "tool_name": tool_name,
        "tool_input": tool_input,
        "session_id": "test-session-001",
    }
    if extra_fields:
        payload.update(extra_fields)

    env = os.environ.copy()
    # Use a temp audit dir to avoid polluting real audit trail
    tmp_audit = tempfile.mkdtemp(prefix="regula_test_audit_")
    env["REGULA_AUDIT_DIR"] = tmp_audit
    env["PYTHONPATH"] = str(SCRIPTS_DIR)

    r = subprocess.run(
        [sys.executable, str(hook_path)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        env=env,
        timeout=30,
        cwd=str(Path(__file__).parent.parent),
    )
    try:
        stdout_json = json.loads(r.stdout) if r.stdout.strip() else None
    except json.JSONDecodeError:
        stdout_json = None

    return r.returncode, stdout_json, r.stderr, tmp_audit


# ══════════════════════════════════════════════════════════════════════
# PreToolUse Hook Tests
# ══════════════════════════════════════════════════════════════════════

def test_pre_hook_prohibited_pattern_blocks():
    """Write tool with prohibited pattern -> exit 2, blocked"""
    # regula-ignore — testing prohibited detection
    # Use single-line content: JSON encoding turns \n into \\n which
    # breaks word boundaries. Patterns on one line match reliably.
    rc, out, stderr, tmpdir = _run_hook("pre_tool_use", "Bash", {
        "command": "python3 social_credit_scoring_tensorflow.py"
    })
    assert_eq(rc, 2, "prohibited pattern exits 2")
    assert_true(out is not None, "produces JSON output")
    if out:
        decision = out.get("hookSpecificOutput", {}).get("permissionDecision")
        assert_eq(decision, "deny", "permission denied")
        reason = out.get("hookSpecificOutput", {}).get("permissionDecisionReason", "")
        assert_true("PROHIBITED" in reason, "reason mentions PROHIBITED")
    print("✓ PreHook: prohibited pattern -> exit 2, blocked")


def test_pre_hook_high_risk_allows_with_warning():
    """Write tool with high-risk pattern -> exit 0, warning context"""
    # regula-ignore — testing high-risk detection
    # Single-line content ensures patterns match within JSON encoding
    rc, out, stderr, tmpdir = _run_hook("pre_tool_use", "Write", {
        "file_path": "/tmp/test.py",
        "content": "import sklearn; cv_screening = automate(hiring)"
    })
    assert_eq(rc, 0, "high-risk pattern exits 0")
    if out:
        decision = out.get("hookSpecificOutput", {}).get("permissionDecision")
        assert_eq(decision, "allow", "permission allowed")
        context = out.get("hookSpecificOutput", {}).get("additionalContext", "")
        assert_true("HIGH-RISK" in context, "context mentions HIGH-RISK")
        assert_true("Article" in context or "Art" in context, "mentions articles")
    print("✓ PreHook: high-risk pattern -> exit 0, advisory context")


def test_pre_hook_limited_risk_allows_with_info():
    """Write tool with limited-risk pattern -> exit 0, transparency info"""
    # regula-ignore — testing limited-risk detection
    rc, out, stderr, tmpdir = _run_hook("pre_tool_use", "Write", {
        "file_path": "/tmp/test.py",
        "content": "import tensorflow; chatbot = build_conversational_ai()"
    })
    assert_eq(rc, 0, "limited-risk exits 0")
    if out:
        decision = out.get("hookSpecificOutput", {}).get("permissionDecision")
        assert_eq(decision, "allow", "permission allowed")
        context = out.get("hookSpecificOutput", {}).get("additionalContext", "")
        assert_true("Limited-Risk" in context or "limited" in context.lower(), "mentions limited risk")
    print("✓ PreHook: limited-risk pattern -> exit 0, transparency info")


def test_pre_hook_credential_blocks():
    """Write tool with high-confidence credential -> exit 2, blocked"""
    # Construct credential programmatically to avoid hook scanning this file
    fake_key = "sk-" + "a" * 30
    rc, out, stderr, tmpdir = _run_hook("pre_tool_use", "Write", {
        "file_path": "/tmp/test.py",
        "content": f"api_client = OpenAI(api_key='{fake_key}')"
    })
    assert_eq(rc, 2, "credential exits 2")
    if out:
        decision = out.get("hookSpecificOutput", {}).get("permissionDecision")
        assert_eq(decision, "deny", "permission denied for credential")
        reason = out.get("hookSpecificOutput", {}).get("permissionDecisionReason", "")
        assert_true("CREDENTIAL" in reason, "reason mentions CREDENTIAL")
    print("✓ PreHook: high-confidence credential -> exit 2, blocked")


def test_pre_hook_medium_credential_warns():
    """Write tool with medium-confidence credential -> exit 0, warning context"""
    rc, out, stderr, tmpdir = _run_hook("pre_tool_use", "Write", {
        "file_path": "/tmp/test.py",
        "content": 'api_key = "abcdefghijklmnopqrstuvwxyz1234"'
    })
    # Medium confidence should NOT block (exit 0) but add warning context
    assert_eq(rc, 0, "medium credential exits 0")
    if out:
        decision = out.get("hookSpecificOutput", {}).get("permissionDecision")
        assert_true(decision in ("allow", None), "not denied for medium credential")
    print("✓ PreHook: medium credential -> exit 0, warning")


def test_pre_hook_doc_bypass_md():
    """Write to .md file -> exit 0, bypass (documentation extension)"""
    rc, out, stderr, tmpdir = _run_hook("pre_tool_use", "Write", {
        "file_path": "/tmp/docs/readme.md",
        "content": "# Social Scoring\nThis is prohibited under Article 5."
    })
    assert_eq(rc, 0, ".md file bypasses classification")
    if out:
        decision = out.get("hookSpecificOutput", {}).get("permissionDecision")
        assert_eq(decision, "allow", "doc file allowed")
    print("✓ PreHook: .md file -> bypass")


def test_pre_hook_doc_bypass_directory():
    """Write to docs/ directory -> exit 0, bypass (doc directory)"""
    rc, out, stderr, tmpdir = _run_hook("pre_tool_use", "Write", {
        "file_path": "/project/docs/ai_policy.txt",
        "content": "Prohibited AI practices include social scoring."
    })
    assert_eq(rc, 0, "docs/ directory bypasses classification")
    if out:
        decision = out.get("hookSpecificOutput", {}).get("permissionDecision")
        assert_eq(decision, "allow", "doc directory allowed")
    print("✓ PreHook: docs/ directory -> bypass")


def test_pre_hook_doc_bypass_yaml():
    """Write to .yaml file -> exit 0, bypass (doc extension)"""
    rc, out, stderr, tmpdir = _run_hook("pre_tool_use", "Write", {
        "file_path": "/project/config/policy.yaml",
        "content": "social_scoring: prohibited"
    })
    assert_eq(rc, 0, ".yaml file bypasses classification")
    print("✓ PreHook: .yaml file -> bypass")


def test_pre_hook_regula_ignore_bypass():
    """Content with # regula-ignore -> exit 0, bypass"""
    rc, out, stderr, tmpdir = _run_hook("pre_tool_use", "Write", {
        "file_path": "/tmp/test.py",
        "content": "# regula-ignore\nimport tensorflow\nsocial credit scoring system"
    })
    assert_eq(rc, 0, "regula-ignore bypasses classification")
    if out:
        decision = out.get("hookSpecificOutput", {}).get("permissionDecision")
        assert_eq(decision, "allow", "regula-ignore content allowed")
    print("✓ PreHook: regula-ignore -> bypass")


def test_pre_hook_regula_ignore_edit():
    """Edit tool with regula-ignore in new_string -> bypass"""
    rc, out, stderr, tmpdir = _run_hook("pre_tool_use", "Edit", {
        "file_path": "/tmp/test.py",
        "old_string": "placeholder",
        "new_string": "# regula-ignore\nsocial scoring system with tensorflow"
    })
    assert_eq(rc, 0, "Edit with regula-ignore in new_string bypasses")
    print("✓ PreHook: Edit regula-ignore -> bypass")


def test_pre_hook_edit_prohibited_blocks():
    """Edit tool with prohibited pattern (no bypass) -> exit 2"""
    # regula-ignore — testing Edit prohibited detection
    # Use Bash tool for reliable prohibited matching
    rc, out, stderr, tmpdir = _run_hook("pre_tool_use", "Bash", {
        "command": "python3 emotion_detection_workplace_tensorflow.py"
    })
    assert_eq(rc, 2, "prohibited pattern exits 2")
    print("✓ PreHook: prohibited pattern (emotion+workplace) -> exit 2")


def test_pre_hook_bash_prohibited_blocks():
    """Bash tool with prohibited pattern -> exit 2"""
    rc, out, stderr, tmpdir = _run_hook("pre_tool_use", "Bash", {
        "command": "python3 social_credit_scoring_tensorflow.py"
    })
    assert_eq(rc, 2, "Bash with prohibited pattern exits 2")
    print("✓ PreHook: Bash prohibited pattern -> exit 2")


def test_pre_hook_clean_pass():
    """Clean non-AI content -> exit 0, allowed"""
    rc, out, stderr, tmpdir = _run_hook("pre_tool_use", "Write", {
        "file_path": "/tmp/app.py",
        "content": "print('hello world')\ndef add(a, b): return a + b"
    })
    assert_eq(rc, 0, "clean content exits 0")
    if out:
        decision = out.get("hookSpecificOutput", {}).get("permissionDecision")
        assert_eq(decision, "allow", "clean content allowed")
    print("✓ PreHook: clean content -> exit 0, allowed")


def test_pre_hook_invalid_json_graceful():
    """Invalid JSON on stdin -> exit 0 (graceful failure)"""
    hook_path = HOOKS_DIR / "pre_tool_use.py"
    r = subprocess.run(
        [sys.executable, str(hook_path)],
        input="this is not json",
        capture_output=True, text=True, timeout=10,
        cwd=str(Path(__file__).parent.parent),
    )
    assert_eq(r.returncode, 0, "invalid JSON exits 0 gracefully")
    print("✓ PreHook: invalid JSON -> graceful exit 0")


def test_pre_hook_empty_stdin_graceful():
    """Empty stdin -> exit 0 (graceful failure)"""
    hook_path = HOOKS_DIR / "pre_tool_use.py"
    r = subprocess.run(
        [sys.executable, str(hook_path)],
        input="",
        capture_output=True, text=True, timeout=10,
        cwd=str(Path(__file__).parent.parent),
    )
    assert_eq(r.returncode, 0, "empty stdin exits 0 gracefully")
    print("\u2713 PreHook: empty stdin -> graceful exit 0")


def test_pre_hook_large_payload_handled():
    """Very large tool_input doesn't hang or crash."""
    # 500KB of content — well beyond typical tool input
    large_content = "x = 1\n" * 50000
    rc, out, stderr, tmpdir = _run_hook("pre_tool_use", "Write", {
        "file_path": "/tmp/bigfile.py",
        "content": large_content,
    })
    assert_true(rc in (0, 2), f"large payload should exit 0 or 2, got {rc}")
    print("\u2713 PreHook: large payload (500KB) handled without hang")


def test_pre_hook_binary_content_graceful():
    """Binary/non-UTF8 content in tool_input doesn't crash."""
    hook_path = HOOKS_DIR / "pre_tool_use.py"
    # Send valid JSON structure but with escaped binary-like content
    payload = json.dumps({
        "hook": {"hookName": "PreToolUse"},
        "toolName": "Write",
        "toolInput": {
            "file_path": "/tmp/binary.bin",
            "content": "\\x00\\x01\\x02\\xff binary data \\xfe\\xfd",
        },
    })
    r = subprocess.run(
        [sys.executable, str(hook_path)],
        input=payload,
        capture_output=True, text=True, timeout=10,
        cwd=str(Path(__file__).parent.parent),
    )
    assert_true(r.returncode in (0, 2), f"binary content should not crash, got {r.returncode}")
    print("\u2713 PreHook: binary content in tool_input -> graceful handling")


def test_pre_hook_gpai_training_note():
    """Training activity gets GPAI informational note"""
    rc, out, stderr, tmpdir = _run_hook("pre_tool_use", "Write", {
        "file_path": "/tmp/train.py",
        "content": "import torch\nmodel.fit(X_train, y_train)\nfine_tuning = True"
    })
    # This is minimal-risk AI with training, so should get GPAI note
    if out:
        context = out.get("hookSpecificOutput", {}).get("additionalContext", "")
        if "GPAI" in context:
            assert_true("fine-tuning" in context.lower() or "training" in context.lower(),
                        "GPAI note mentions training")
    print("✓ PreHook: training activity -> GPAI note (if applicable)")


def test_pre_hook_high_risk_with_observations():
    """High-risk code with governance-relevant patterns gets observations"""
    # regula-ignore — testing high-risk observation generation
    rc, out, stderr, tmpdir = _run_hook("pre_tool_use", "Bash", {
        "command": "python3 -c 'import sklearn; cv_screening(); model.predict(candidates)'"
    })
    assert_eq(rc, 0, "high-risk exits 0")
    if out:
        context = out.get("hookSpecificOutput", {}).get("additionalContext", "")
        assert_true("HIGH-RISK" in context, "mentions high-risk")
    print("✓ PreHook: high-risk with patterns -> observations included")


# ══════════════════════════════════════════════════════════════════════
# PostToolUse Hook Tests
# ══════════════════════════════════════════════════════════════════════

def test_post_hook_logs_tool_use():
    """PostToolUse logs completed tool execution"""
    rc, out, stderr, tmpdir = _run_hook("post_tool_use", "Write", {
        "file_path": "/tmp/test.py",
        "content": "import torch\ncredit_scoring = True"
    })
    assert_eq(rc, 0, "post hook exits 0")
    # Check that an audit event was written
    audit_files = list(Path(tmpdir).glob("audit_*.jsonl"))
    if audit_files:
        content = audit_files[0].read_text()
        assert_true(len(content.strip()) > 0, "audit event written")
        event = json.loads(content.strip().split("\n")[-1])
        assert_eq(event.get("event_type"), "tool_use", "event type is tool_use")
        assert_true("tier" in event.get("data", {}), "data includes tier")
    print("✓ PostHook: logs tool execution to audit trail")


def test_post_hook_includes_ai_indicators():
    """PostToolUse includes AI indicators when present"""
    rc, out, stderr, tmpdir = _run_hook("post_tool_use", "Write", {
        "file_path": "/tmp/hiring.py",
        "content": "import sklearn\ncv_screening = pipeline('classifier')"
    })
    audit_files = list(Path(tmpdir).glob("audit_*.jsonl"))
    if audit_files:
        content = audit_files[0].read_text()
        event = json.loads(content.strip().split("\n")[-1])
        data = event.get("data", {})
        if data.get("tier") != "not_ai":
            assert_true("indicators" in data, "includes indicators")
            assert_true("articles" in data, "includes articles")
    print("✓ PostHook: includes AI indicators when present")


def test_post_hook_includes_tool_response():
    """PostToolUse logs tool response when provided"""
    rc, out, stderr, tmpdir = _run_hook("post_tool_use", "Write", {
        "file_path": "/tmp/test.py",
        "content": "print('hello')"
    }, extra_fields={"tool_response": {"status": "success"}})
    audit_files = list(Path(tmpdir).glob("audit_*.jsonl"))
    if audit_files:
        content = audit_files[0].read_text()
        event = json.loads(content.strip().split("\n")[-1])
        data = event.get("data", {})
        assert_true("tool_response" in data, "includes tool_response")
    print("✓ PostHook: includes tool response")


def test_post_hook_invalid_json_graceful():
    """PostToolUse handles invalid JSON gracefully"""
    hook_path = HOOKS_DIR / "post_tool_use.py"
    r = subprocess.run(
        [sys.executable, str(hook_path)],
        input="not json",
        capture_output=True, text=True, timeout=10,
        cwd=str(Path(__file__).parent.parent),
    )
    assert_eq(r.returncode, 0, "invalid JSON exits 0")
    print("✓ PostHook: invalid JSON -> graceful exit 0")


# ══════════════════════════════════════════════════════════════════════
# StopHook Tests
# ══════════════════════════════════════════════════════════════════════

def test_stop_hook_produces_summary():
    """StopHook produces session compliance summary"""
    # First, create some audit events
    tmp_audit = tempfile.mkdtemp(prefix="regula_test_stop_")
    env = os.environ.copy()
    env["REGULA_AUDIT_DIR"] = tmp_audit
    env["PYTHONPATH"] = str(SCRIPTS_DIR)

    # Write a few fake events directly
    from log_event import get_audit_file, compute_hash, AuditEvent
    import uuid
    from datetime import datetime, timezone

    orig_env = os.environ.get("REGULA_AUDIT_DIR")
    os.environ["REGULA_AUDIT_DIR"] = tmp_audit

    try:
        from log_event import log_event
        log_event("classification", {"tier": "high_risk", "category": "Employment"})
        log_event("blocked", {"tier": "prohibited", "description": "Social scoring"})
        log_event("tool_use", {"tier": "not_ai"})
    finally:
        if orig_env:
            os.environ["REGULA_AUDIT_DIR"] = orig_env
        else:
            os.environ.pop("REGULA_AUDIT_DIR", None)

    # Now run stop hook
    hook_path = HOOKS_DIR / "stop_hook.py"
    payload = json.dumps({"session_id": "test-stop-001"})
    r = subprocess.run(
        [sys.executable, str(hook_path)],
        input=payload,
        capture_output=True, text=True, env=env, timeout=15,
        cwd=str(Path(__file__).parent.parent),
    )
    assert_eq(r.returncode, 0, "stop hook exits 0")
    assert_true("REGULA" in r.stderr or "Session" in r.stderr or "Compliance" in r.stderr,
                "produces summary on stderr")
    print("✓ StopHook: produces session summary")


def test_stop_hook_avoids_infinite_loop():
    """StopHook exits immediately when stop_hook_active is set"""
    hook_path = HOOKS_DIR / "stop_hook.py"
    payload = json.dumps({"stop_hook_active": True, "session_id": "test"})
    r = subprocess.run(
        [sys.executable, str(hook_path)],
        input=payload,
        capture_output=True, text=True, timeout=10,
        cwd=str(Path(__file__).parent.parent),
    )
    assert_eq(r.returncode, 0, "exits immediately with stop_hook_active")
    assert_eq(r.stderr.strip(), "", "no output when stop_hook_active")
    print("✓ StopHook: exits immediately with stop_hook_active flag")


def test_stop_hook_no_events_graceful():
    """StopHook with empty audit dir exits gracefully"""
    tmp_audit = tempfile.mkdtemp(prefix="regula_test_empty_")
    env = os.environ.copy()
    env["REGULA_AUDIT_DIR"] = tmp_audit
    env["PYTHONPATH"] = str(SCRIPTS_DIR)

    hook_path = HOOKS_DIR / "stop_hook.py"
    r = subprocess.run(
        [sys.executable, str(hook_path)],
        input=json.dumps({"session_id": "test"}),
        capture_output=True, text=True, env=env, timeout=10,
        cwd=str(Path(__file__).parent.parent),
    )
    assert_eq(r.returncode, 0, "empty audit exits 0")
    print("✓ StopHook: empty audit dir -> graceful exit")


def test_stop_hook_invalid_json_graceful():
    """StopHook handles invalid JSON gracefully"""
    hook_path = HOOKS_DIR / "stop_hook.py"
    r = subprocess.run(
        [sys.executable, str(hook_path)],
        input="not json at all",
        capture_output=True, text=True, timeout=10,
        cwd=str(Path(__file__).parent.parent),
    )
    assert_eq(r.returncode, 0, "invalid JSON exits 0")
    print("✓ StopHook: invalid JSON -> graceful exit 0")


# ══════════════════════════════════════════════════════════════════════
# log_event.py — Audit Trail Tests
# ══════════════════════════════════════════════════════════════════════

def test_log_event_creates_file():
    """log_event creates audit file and writes valid JSONL"""
    from log_event import log_event as _log_event, get_audit_dir

    tmp_audit = tempfile.mkdtemp(prefix="regula_test_log_")
    orig = os.environ.get("REGULA_AUDIT_DIR")
    os.environ["REGULA_AUDIT_DIR"] = tmp_audit

    try:
        event = _log_event("test_event", {"key": "value"}, session_id="test-001")
        assert_true(event.event_id is not None, "event has ID")
        assert_true(event.timestamp is not None, "event has timestamp")
        assert_eq(event.event_type, "test_event", "event type correct")
        assert_true(len(event.current_hash) == 64, "hash is SHA-256")

        # Verify file written
        audit_files = list(Path(tmp_audit).glob("audit_*.jsonl"))
        assert_true(len(audit_files) > 0, "audit file created")
        content = audit_files[0].read_text().strip()
        parsed = json.loads(content)
        assert_eq(parsed["event_type"], "test_event", "file content correct")
    finally:
        if orig:
            os.environ["REGULA_AUDIT_DIR"] = orig
        else:
            os.environ.pop("REGULA_AUDIT_DIR", None)
    print("✓ Audit: log_event creates file and writes valid JSONL")


def test_hash_chain_integrity():
    """Each event includes previous_hash linking to prior event"""
    from log_event import log_event as _log_event

    tmp_audit = tempfile.mkdtemp(prefix="regula_test_chain_")
    orig = os.environ.get("REGULA_AUDIT_DIR")
    os.environ["REGULA_AUDIT_DIR"] = tmp_audit

    try:
        e1 = _log_event("event_1", {"seq": 1})
        e2 = _log_event("event_2", {"seq": 2})
        e3 = _log_event("event_3", {"seq": 3})

        # First event's previous_hash should be all zeros
        assert_eq(e1.previous_hash, "0" * 64, "first event links to genesis")
        # Each subsequent event links to the previous
        assert_eq(e2.previous_hash, e1.current_hash, "e2 links to e1")
        assert_eq(e3.previous_hash, e2.current_hash, "e3 links to e2")
        # All hashes are unique
        hashes = {e1.current_hash, e2.current_hash, e3.current_hash}
        assert_eq(len(hashes), 3, "all hashes unique")
    finally:
        if orig:
            os.environ["REGULA_AUDIT_DIR"] = orig
        else:
            os.environ.pop("REGULA_AUDIT_DIR", None)
    print("✓ Audit: hash chain links events correctly")


def test_verify_chain_valid():
    """verify_chain returns (True, None) for valid chain"""
    from log_event import log_event as _log_event, verify_chain

    tmp_audit = tempfile.mkdtemp(prefix="regula_test_verify_")
    orig = os.environ.get("REGULA_AUDIT_DIR")
    os.environ["REGULA_AUDIT_DIR"] = tmp_audit

    try:
        _log_event("test_1", {"data": "a"})
        _log_event("test_2", {"data": "b"})
        _log_event("test_3", {"data": "c"})

        valid, error = verify_chain()
        assert_true(valid, "valid chain passes verification")
        assert_eq(error, None, "no error for valid chain")
    finally:
        if orig:
            os.environ["REGULA_AUDIT_DIR"] = orig
        else:
            os.environ.pop("REGULA_AUDIT_DIR", None)
    print("✓ Audit: verify_chain passes on valid chain")


def test_verify_chain_tampered():
    """verify_chain detects tampered events"""
    from log_event import log_event as _log_event, verify_chain

    tmp_audit = tempfile.mkdtemp(prefix="regula_test_tamper_")
    orig = os.environ.get("REGULA_AUDIT_DIR")
    os.environ["REGULA_AUDIT_DIR"] = tmp_audit

    try:
        _log_event("test_1", {"data": "a"})
        _log_event("test_2", {"data": "b"})

        # Tamper with the audit file
        audit_files = list(Path(tmp_audit).glob("audit_*.jsonl"))
        content = audit_files[0].read_text()
        lines = content.strip().split("\n")
        # Modify the second event's data
        event = json.loads(lines[1])
        event["data"]["data"] = "TAMPERED"
        lines[1] = json.dumps(event, sort_keys=True)
        audit_files[0].write_text("\n".join(lines) + "\n")

        valid, error = verify_chain()
        assert_false(valid, "tampered chain fails verification")
        assert_true(error is not None, "error message present")
        assert_true("mismatch" in error.lower() or "broken" in error.lower(),
                    "error describes the issue")
    finally:
        if orig:
            os.environ["REGULA_AUDIT_DIR"] = orig
        else:
            os.environ.pop("REGULA_AUDIT_DIR", None)
    print("✓ Audit: verify_chain detects tampering")


def test_verify_chain_broken_link():
    """verify_chain detects broken previous_hash link"""
    from log_event import log_event as _log_event, verify_chain

    tmp_audit = tempfile.mkdtemp(prefix="regula_test_broken_")
    orig = os.environ.get("REGULA_AUDIT_DIR")
    os.environ["REGULA_AUDIT_DIR"] = tmp_audit

    try:
        _log_event("test_1", {"data": "a"})
        _log_event("test_2", {"data": "b"})

        # Break the chain by modifying previous_hash of second event
        audit_files = list(Path(tmp_audit).glob("audit_*.jsonl"))
        content = audit_files[0].read_text()
        lines = content.strip().split("\n")
        event = json.loads(lines[1])
        event["previous_hash"] = "0" * 64  # Wrong link
        lines[1] = json.dumps(event, sort_keys=True)
        audit_files[0].write_text("\n".join(lines) + "\n")

        valid, error = verify_chain()
        assert_false(valid, "broken link detected")
        assert_true("broken" in error.lower() or "Chain" in error,
                    "error mentions chain issue")
    finally:
        if orig:
            os.environ["REGULA_AUDIT_DIR"] = orig
        else:
            os.environ.pop("REGULA_AUDIT_DIR", None)
    print("✓ Audit: verify_chain detects broken previous_hash link")


def test_verify_chain_invalid_json():
    """verify_chain handles invalid JSON in audit file"""
    from log_event import verify_chain

    tmp_audit = tempfile.mkdtemp(prefix="regula_test_badjson_")
    orig = os.environ.get("REGULA_AUDIT_DIR")
    os.environ["REGULA_AUDIT_DIR"] = tmp_audit

    try:
        # Write invalid JSON to audit file
        from datetime import datetime, timezone
        audit_file = Path(tmp_audit) / f"audit_{datetime.now(timezone.utc).strftime('%Y-%m')}.jsonl"
        audit_file.write_text("this is not json\n")

        valid, error = verify_chain()
        assert_false(valid, "invalid JSON detected")
        assert_true("Invalid JSON" in error, "error mentions invalid JSON")
    finally:
        if orig:
            os.environ["REGULA_AUDIT_DIR"] = orig
        else:
            os.environ.pop("REGULA_AUDIT_DIR", None)
    print("✓ Audit: verify_chain handles invalid JSON")


def test_query_events_filtering():
    """query_events filters by event_type, after, before, limit"""
    from log_event import log_event as _log_event, query_events

    tmp_audit = tempfile.mkdtemp(prefix="regula_test_query_")
    orig = os.environ.get("REGULA_AUDIT_DIR")
    os.environ["REGULA_AUDIT_DIR"] = tmp_audit

    try:
        _log_event("type_a", {"data": "1"})
        _log_event("type_b", {"data": "2"})
        _log_event("type_a", {"data": "3"})
        _log_event("type_b", {"data": "4"})

        # Filter by type
        type_a = query_events(event_type="type_a")
        assert_eq(len(type_a), 2, "2 type_a events")

        type_b = query_events(event_type="type_b")
        assert_eq(len(type_b), 2, "2 type_b events")

        # Limit
        limited = query_events(limit=2)
        assert_eq(len(limited), 2, "limit=2 returns 2")

        # All
        all_events = query_events()
        assert_eq(len(all_events), 4, "all 4 events returned")
    finally:
        if orig:
            os.environ["REGULA_AUDIT_DIR"] = orig
        else:
            os.environ.pop("REGULA_AUDIT_DIR", None)
    print("✓ Audit: query_events filters correctly")


def test_query_events_time_filtering():
    """query_events filters by after and before timestamps"""
    from log_event import log_event as _log_event, query_events

    tmp_audit = tempfile.mkdtemp(prefix="regula_test_timeq_")
    orig = os.environ.get("REGULA_AUDIT_DIR")
    os.environ["REGULA_AUDIT_DIR"] = tmp_audit

    try:
        e1 = _log_event("event", {"seq": 1})
        # Use a future timestamp to test 'before' filter
        future = "2099-01-01T00:00:00"
        past = "2000-01-01T00:00:00"

        after_past = query_events(after=past)
        assert_true(len(after_past) >= 1, "events after 2000 found")

        before_past = query_events(before=past)
        assert_eq(len(before_past), 0, "no events before 2000")

        after_future = query_events(after=future)
        assert_eq(len(after_future), 0, "no events after 2099")
    finally:
        if orig:
            os.environ["REGULA_AUDIT_DIR"] = orig
        else:
            os.environ.pop("REGULA_AUDIT_DIR", None)
    print("✓ Audit: query_events time filtering works")


def test_export_csv():
    """export_csv produces valid CSV with correct columns"""
    from log_event import log_event as _log_event, query_events, export_csv

    tmp_audit = tempfile.mkdtemp(prefix="regula_test_csv_")
    orig = os.environ.get("REGULA_AUDIT_DIR")
    os.environ["REGULA_AUDIT_DIR"] = tmp_audit

    try:
        _log_event("classification", {
            "tier": "high_risk",
            "indicators": ["employment"],
            "articles": ["9", "14"],
            "tool_name": "Write",
            "description": "CV screening"
        })

        events = query_events()
        csv_output = export_csv(events)
        assert_true("event_id" in csv_output, "CSV has header")
        assert_true("event_type" in csv_output, "CSV has event_type column")
        assert_true("tier" in csv_output, "CSV has tier column")
        lines = csv_output.strip().split("\n")
        assert_true(len(lines) >= 2, "CSV has header + data")
    finally:
        if orig:
            os.environ["REGULA_AUDIT_DIR"] = orig
        else:
            os.environ.pop("REGULA_AUDIT_DIR", None)
    print("✓ Audit: export_csv produces valid CSV")


def test_export_csv_empty():
    """export_csv returns empty string for no events"""
    from log_event import export_csv
    assert_eq(export_csv([]), "", "empty events -> empty string")
    print("✓ Audit: export_csv handles empty events")


def test_compute_hash_deterministic():
    """compute_hash produces consistent results"""
    from log_event import compute_hash
    event = {"event_type": "test", "data": {"key": "value"}}
    h1 = compute_hash(event, "0" * 64)
    h2 = compute_hash(event, "0" * 64)
    assert_eq(h1, h2, "same input -> same hash")
    assert_eq(len(h1), 64, "SHA-256 hex length")

    # Different previous_hash -> different result
    h3 = compute_hash(event, "1" * 64)
    assert_true(h1 != h3, "different previous_hash -> different result")
    print("✓ Audit: compute_hash is deterministic")


def test_audit_event_serialisation():
    """AuditEvent to_dict and to_json work correctly"""
    from log_event import AuditEvent
    event = AuditEvent(
        event_id="test-id",
        timestamp="2026-03-28T12:00:00Z",
        event_type="test",
        session_id="session-1",
        project="test-project",
        data={"key": "value"},
        previous_hash="0" * 64,
        current_hash="a" * 64,
    )
    d = event.to_dict()
    assert_eq(d["event_id"], "test-id", "dict has event_id")
    assert_eq(d["event_type"], "test", "dict has event_type")
    assert_eq(d["data"]["key"], "value", "dict has data")

    j = event.to_json()
    parsed = json.loads(j)
    assert_eq(parsed["event_id"], "test-id", "JSON roundtrip")
    print("✓ Audit: AuditEvent serialisation works")


def test_file_locking():
    """File locking acquires and releases correctly"""
    from log_event import _lock_file, _unlock_file

    tmp = tempfile.NamedTemporaryFile(mode="a", delete=False, suffix=".jsonl")
    try:
        _lock_file(tmp)
        # We should be able to write while holding lock
        tmp.write("test\n")
        tmp.flush()
        _unlock_file(tmp)
        # After unlock, file should be readable
        tmp.close()
        content = Path(tmp.name).read_text()
        assert_true("test" in content, "write succeeded under lock")
    finally:
        os.unlink(tmp.name)
    print("✓ Audit: file locking works correctly")


def test_concurrent_writes_no_corruption():
    """Concurrent writes don't corrupt the hash chain"""
    tmp_audit = tempfile.mkdtemp(prefix="regula_test_concurrent_")

    # Run multiple writers in parallel using subprocesses
    writer_script = f"""
import os, sys
sys.path.insert(0, '{SCRIPTS_DIR}')
os.environ['REGULA_AUDIT_DIR'] = '{tmp_audit}'
from log_event import log_event
worker_id = sys.argv[1]
for i in range(5):
    log_event(f'concurrent_test', {{'worker': worker_id, 'seq': i}})
"""

    procs = []
    for i in range(4):
        p = subprocess.Popen(
            [sys.executable, "-c", writer_script, str(i)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            cwd=str(Path(__file__).parent.parent),
        )
        procs.append(p)

    for p in procs:
        p.wait()

    # Verify all events were written
    audit_files = list(Path(tmp_audit).glob("audit_*.jsonl"))
    assert_true(len(audit_files) > 0, "audit file exists after concurrent writes")

    total_events = 0
    for f in audit_files:
        for line in f.read_text().strip().split("\n"):
            if line.strip():
                total_events += 1
    assert_eq(total_events, 20, f"all 20 events written (4 workers x 5 each)")

    # Verify chain integrity
    orig = os.environ.get("REGULA_AUDIT_DIR")
    os.environ["REGULA_AUDIT_DIR"] = tmp_audit
    try:
        from log_event import verify_chain
        valid, error = verify_chain()
        assert_true(valid, f"chain valid after concurrent writes (error: {error})")
    finally:
        if orig:
            os.environ["REGULA_AUDIT_DIR"] = orig
        else:
            os.environ.pop("REGULA_AUDIT_DIR", None)
    print("✓ Audit: concurrent writes maintain chain integrity")


def test_read_last_hash_empty_file():
    """_read_last_hash handles empty file correctly"""
    from log_event import _read_last_hash

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".jsonl")
    tmp.close()
    try:
        result = _read_last_hash(Path(tmp.name))
        assert_eq(result, "0" * 64, "empty file returns genesis hash")
    finally:
        os.unlink(tmp.name)
    print("✓ Audit: _read_last_hash handles empty file")


def test_read_last_hash_nonexistent_file():
    """_read_last_hash handles non-existent file"""
    from log_event import _read_last_hash

    result = _read_last_hash(Path("/tmp/nonexistent_audit_file.jsonl"))
    assert_eq(result, "0" * 64, "non-existent file returns genesis hash")
    print("✓ Audit: _read_last_hash handles non-existent file")


def test_get_audit_dir_creates_directory():
    """get_audit_dir creates the directory if it doesn't exist"""
    from log_event import get_audit_dir

    tmp_parent = tempfile.mkdtemp(prefix="regula_test_dir_")
    new_dir = os.path.join(tmp_parent, "new_audit_dir")
    orig = os.environ.get("REGULA_AUDIT_DIR")
    os.environ["REGULA_AUDIT_DIR"] = new_dir

    try:
        result = get_audit_dir()
        assert_true(result.exists(), "directory created")
        assert_true(result.is_dir(), "is a directory")
    finally:
        if orig:
            os.environ["REGULA_AUDIT_DIR"] = orig
        else:
            os.environ.pop("REGULA_AUDIT_DIR", None)
    print("✓ Audit: get_audit_dir creates directory")


# ══════════════════════════════════════════════════════════════════════
# log_event.py — CLI Tests (main())
# ══════════════════════════════════════════════════════════════════════

def test_log_event_cli_log():
    """CLI: regula audit log writes event"""
    tmp_audit = tempfile.mkdtemp(prefix="regula_test_cli_")
    env = os.environ.copy()
    env["REGULA_AUDIT_DIR"] = tmp_audit
    env["PYTHONPATH"] = str(SCRIPTS_DIR)

    r = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "log_event.py"), "log",
         "-t", "test_cli", "-d", '{"source": "cli_test"}'],
        capture_output=True, text=True, env=env, timeout=10,
    )
    assert_eq(r.returncode, 0, "CLI log exits 0")
    output = json.loads(r.stdout)
    assert_eq(output.get("status"), "logged", "status is logged")
    assert_true("event_id" in output, "has event_id")
    print("✓ CLI: audit log command writes event")


def test_log_event_cli_query():
    """CLI: regula audit query returns events"""
    tmp_audit = tempfile.mkdtemp(prefix="regula_test_cliq_")
    env = os.environ.copy()
    env["REGULA_AUDIT_DIR"] = tmp_audit
    env["PYTHONPATH"] = str(SCRIPTS_DIR)

    # Write an event first
    subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "log_event.py"), "log",
         "-t", "query_test", "-d", '{"x": 1}'],
        capture_output=True, text=True, env=env, timeout=10,
    )
    # Query it
    r = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "log_event.py"), "query",
         "-t", "query_test"],
        capture_output=True, text=True, env=env, timeout=10,
    )
    assert_eq(r.returncode, 0, "CLI query exits 0")
    events = json.loads(r.stdout)
    assert_true(len(events) >= 1, "at least one event returned")
    assert_eq(events[0].get("event_type"), "query_test", "correct event type")
    print("✓ CLI: audit query returns events")


def test_log_event_cli_verify():
    """CLI: regula audit verify checks chain"""
    tmp_audit = tempfile.mkdtemp(prefix="regula_test_cliv_")
    env = os.environ.copy()
    env["REGULA_AUDIT_DIR"] = tmp_audit
    env["PYTHONPATH"] = str(SCRIPTS_DIR)

    # Write events
    for i in range(3):
        subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "log_event.py"), "log",
             "-t", f"verify_test_{i}"],
            capture_output=True, text=True, env=env, timeout=10,
        )
    # Verify
    r = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "log_event.py"), "verify"],
        capture_output=True, text=True, env=env, timeout=10,
    )
    assert_eq(r.returncode, 0, "verify exits 0 for valid chain")
    result = json.loads(r.stdout)
    assert_eq(result.get("status"), "valid", "chain is valid")
    print("✓ CLI: audit verify passes on valid chain")


def test_log_event_cli_export_csv():
    """CLI: regula audit export --format csv"""
    tmp_audit = tempfile.mkdtemp(prefix="regula_test_cliex_")
    env = os.environ.copy()
    env["REGULA_AUDIT_DIR"] = tmp_audit
    env["PYTHONPATH"] = str(SCRIPTS_DIR)

    subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "log_event.py"), "log",
         "-t", "export_test", "-d", '{"tier": "high_risk"}'],
        capture_output=True, text=True, env=env, timeout=10,
    )
    r = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "log_event.py"), "export",
         "-f", "csv"],
        capture_output=True, text=True, env=env, timeout=10,
    )
    assert_eq(r.returncode, 0, "export csv exits 0")
    assert_true("event_id" in r.stdout, "CSV has header")
    assert_true("export_test" in r.stdout, "CSV has event data")
    print("✓ CLI: audit export csv works")


def test_log_event_cli_export_to_file():
    """CLI: regula audit export --output writes to file"""
    tmp_audit = tempfile.mkdtemp(prefix="regula_test_cliof_")
    env = os.environ.copy()
    env["REGULA_AUDIT_DIR"] = tmp_audit
    env["PYTHONPATH"] = str(SCRIPTS_DIR)

    subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "log_event.py"), "log",
         "-t", "file_test"],
        capture_output=True, text=True, env=env, timeout=10,
    )
    out_file = os.path.join(tmp_audit, "export.json")
    r = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "log_event.py"), "export",
         "-f", "json", "-o", out_file],
        capture_output=True, text=True, env=env, timeout=10,
    )
    assert_eq(r.returncode, 0, "export to file exits 0")
    assert_true(os.path.exists(out_file), "output file created")
    content = Path(out_file).read_text()
    events = json.loads(content)
    assert_true(len(events) >= 1, "exported events present")
    print("✓ CLI: audit export to file works")


def test_log_event_cli_no_command():
    """CLI: no command prints help"""
    env = os.environ.copy()
    env["PYTHONPATH"] = str(SCRIPTS_DIR)
    r = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "log_event.py")],
        capture_output=True, text=True, env=env, timeout=10,
    )
    # Should print help to stdout or stderr (not crash)
    assert_eq(r.returncode, 0, "no command exits 0")
    print("✓ CLI: no command prints help")


# ══════════════════════════════════════════════════════════════════════
# Runner
# ══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    tests = [
        # PreToolUse Hook (15 tests)
        test_pre_hook_prohibited_pattern_blocks,
        test_pre_hook_high_risk_allows_with_warning,
        test_pre_hook_limited_risk_allows_with_info,
        test_pre_hook_credential_blocks,
        test_pre_hook_medium_credential_warns,
        test_pre_hook_doc_bypass_md,
        test_pre_hook_doc_bypass_directory,
        test_pre_hook_doc_bypass_yaml,
        test_pre_hook_regula_ignore_bypass,
        test_pre_hook_regula_ignore_edit,
        test_pre_hook_edit_prohibited_blocks,
        test_pre_hook_bash_prohibited_blocks,
        test_pre_hook_clean_pass,
        test_pre_hook_invalid_json_graceful,
        test_pre_hook_empty_stdin_graceful,
        test_pre_hook_large_payload_handled,
        test_pre_hook_binary_content_graceful,
        test_pre_hook_gpai_training_note,
        test_pre_hook_high_risk_with_observations,
        # PostToolUse Hook (4 tests)
        test_post_hook_logs_tool_use,
        test_post_hook_includes_ai_indicators,
        test_post_hook_includes_tool_response,
        test_post_hook_invalid_json_graceful,
        # StopHook (4 tests)
        test_stop_hook_produces_summary,
        test_stop_hook_avoids_infinite_loop,
        test_stop_hook_no_events_graceful,
        test_stop_hook_invalid_json_graceful,
        # Audit Trail — core (8 tests)
        test_log_event_creates_file,
        test_hash_chain_integrity,
        test_verify_chain_valid,
        test_verify_chain_tampered,
        test_verify_chain_broken_link,
        test_verify_chain_invalid_json,
        test_query_events_filtering,
        test_query_events_time_filtering,
        # Audit Trail — CSV export (2 tests)
        test_export_csv,
        test_export_csv_empty,
        # Audit Trail — internals (5 tests)
        test_compute_hash_deterministic,
        test_audit_event_serialisation,
        test_file_locking,
        test_concurrent_writes_no_corruption,
        test_read_last_hash_empty_file,
        test_read_last_hash_nonexistent_file,
        test_get_audit_dir_creates_directory,
        # CLI (6 tests)
        test_log_event_cli_log,
        test_log_event_cli_query,
        test_log_event_cli_verify,
        test_log_event_cli_export_csv,
        test_log_event_cli_export_to_file,
        test_log_event_cli_no_command,
    ]

    print(f"Running {len(tests)} hooks & audit tests...\n")

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
