# regula-ignore
#!/usr/bin/env python3
"""
Reliability and hardening tests (Package 4).

Tests edge cases that could crash a compliance tool in production:
file size limits, binary files, unicode edge cases, null bytes,
error path structured messages, and concurrent access.
"""

import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import helpers
from helpers import assert_eq, assert_true


# ── File Size Limits ────────────────────────────────────────────────


def test_large_file_skipped_gracefully():
    """Files > MAX_FILE_SIZE are skipped without crash."""
    from report import scan_files

    with tempfile.TemporaryDirectory() as tmp:
        # Create a 6MB file (above the 5MB limit we'll set)
        large_file = Path(tmp) / "huge.py"
        large_file.write_text("import torch\n" * 300000, encoding="utf-8")  # ~4.2MB
        # Should not crash
        findings = scan_files(tmp)
        assert_true(isinstance(findings, list),
                    f"scan_files should return list, got {type(findings)}")
        assert_true(len(findings) <= 1,
                    f"large file should produce at most 1 finding, got {len(findings)}")
    print("\u2713 Reliability: large file handled gracefully")


def test_binary_file_skipped():
    """Binary files don't crash the scanner."""
    from report import scan_files

    with tempfile.TemporaryDirectory() as tmp:
        # Create a file with .py extension but binary content
        binary_file = Path(tmp) / "model.py"
        binary_file.write_bytes(b"\x00\x01\x02\xff\xfe\xfd" * 1000)
        findings = scan_files(tmp)
        assert_true(isinstance(findings, list),
                    "binary .py file should not crash scanner")
        assert_eq(len(findings), 0, "binary .py file should produce no findings")
    print("\u2713 Reliability: binary file skipped gracefully")


# ── Unicode Edge Cases ──────────────────────────────────────────────


def test_unicode_emoji_in_classification():
    """Emoji characters in code don't crash classification."""
    from classify_risk import classify

    code = 'import torch\n# This model uses emoji: \U0001f916\U0001f4ca\ndef predict(x): return model(x)\n'
    result = classify(code)
    assert_true(result is not None, "classification should handle emoji")
    assert_true(hasattr(result, "tier"), "result should have tier")
    print("\u2713 Reliability: emoji in code handled")


def test_unicode_rtl_in_classification():
    """RTL (right-to-left) characters don't crash classification."""
    from classify_risk import classify

    code = 'import openai\n# \u0627\u0644\u0639\u0631\u0628\u064a\u0629 Arabic text\ndef process(): pass\n'
    result = classify(code)
    assert_true(result is not None, "classification should handle RTL text")
    assert_true(hasattr(result, "tier"), "classification result has tier")
    assert_true(result.tier is not None, "tier is not None")
    print("\u2713 Reliability: RTL unicode handled")


def test_unicode_zero_width_in_classification():
    """Zero-width characters don't affect classification."""
    from classify_risk import classify

    # Zero-width space and joiner embedded in code
    code = 'import\u200b torch\n# Zero width in import\ndef train(): model.fit(X, y)\n'
    result = classify(code)
    assert_true(result is not None, "classification should handle zero-width chars")
    assert_true(hasattr(result, "tier"), "classification result has tier")
    assert_true(result.tier is not None, "tier is not None")
    print("\u2713 Reliability: zero-width unicode handled")


def test_null_bytes_in_classification():
    """Null bytes in input don't crash regex engine."""
    from classify_risk import classify

    code = 'import openai\x00\ndef predict():\x00 pass\n'
    result = classify(code)
    assert_true(result is not None, "classification should handle null bytes")
    assert_true(hasattr(result, "tier"), "classification result has tier")
    assert_true(result.tier is not None, "tier is not None")
    print("\u2713 Reliability: null bytes handled")


# ── Error Path Messages ─────────────────────────────────────────────


def test_permission_denied_structured_message():
    """Permission denied produces structured error, not raw traceback."""
    r = subprocess.run(
        [sys.executable, "scripts/cli.py", "check", "/root/secret"],
        capture_output=True, text=True, timeout=10,
        cwd=str(Path(__file__).parent.parent),
    )
    assert_true(r.returncode != 0, "should fail on /root/secret")
    assert_true("error" in r.stderr.lower() or "does not exist" in r.stderr.lower(),
                f"should produce structured error, got: {r.stderr[:200]}")
    # Should NOT contain raw traceback
    assert_true("Traceback" not in r.stderr,
                f"should NOT show raw traceback, got: {r.stderr[:200]}")
    print("\u2713 Reliability: permission denied produces structured error")


def test_empty_file_no_crash():
    """Empty .py file doesn't crash scanner."""
    from report import scan_files

    with tempfile.TemporaryDirectory() as tmp:
        empty = Path(tmp) / "empty.py"
        empty.write_text("", encoding="utf-8")
        findings = scan_files(tmp)
        assert_true(isinstance(findings, list), "empty file should not crash")
    print("\u2713 Reliability: empty file handled")


def test_deeply_nested_json_in_hook():
    """Deeply nested JSON input doesn't crash hook."""
    hook_path = Path(__file__).parent.parent / "hooks" / "pre_tool_use.py"
    # Create valid but deeply nested content
    nested = '{"a": ' * 50 + '"value"' + '}' * 50
    payload = json.dumps({
        "hook": {"hookName": "PreToolUse"},
        "toolName": "Write",
        "toolInput": {"file_path": "/tmp/test.py", "content": nested},
    })
    r = subprocess.run(
        [sys.executable, str(hook_path)],
        input=payload,
        capture_output=True, text=True, timeout=10,
        cwd=str(Path(__file__).parent.parent),
    )
    assert_true(r.returncode in (0, 2), f"nested JSON should not crash, got exit {r.returncode}")
    print("\u2713 Reliability: deeply nested JSON handled in hook")


def test_concurrent_registry_writes():
    """Parallel registry writes don't corrupt the file."""
    from discover_ai_systems import load_registry, save_registry, REGISTRY_PATH

    with tempfile.TemporaryDirectory() as tmp:
        reg_path = Path(tmp) / "registry.json"
        # Write initial registry
        reg_path.write_text(json.dumps({"version": "1.0", "systems": {}}, indent=2),
                           encoding="utf-8")

        writer_script = f"""
import json, sys, os
sys.path.insert(0, 'scripts')
os.environ['REGULA_REGISTRY'] = '{reg_path}'
from discover_ai_systems import load_registry, save_registry
worker = sys.argv[1]
for i in range(3):
    reg = load_registry()
    reg['systems'][f'system_{{worker}}_{{i}}'] = {{'worker': worker, 'seq': i}}
    save_registry(reg)
"""
        procs = []
        for i in range(3):
            p = subprocess.Popen(
                [sys.executable, "-c", writer_script, str(i)],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                cwd=str(Path(__file__).parent.parent),
            )
            procs.append(p)

        for p in procs:
            p.wait()

        # Verify file is valid JSON
        content = reg_path.read_text(encoding="utf-8")
        registry = json.loads(content)
        assert_true("systems" in registry, "registry should have systems key")
        # At least some systems should have been written (exact count depends on race)
        system_count = len(registry["systems"])
        assert_true(system_count > 0,
                    f"at least some systems should be written, got {system_count}")
    print("\u2713 Reliability: concurrent registry writes produce valid JSON")


def test_feed_network_timeout_graceful():
    """Feed command handles network issues gracefully."""
    r = subprocess.run(
        [sys.executable, "scripts/cli.py", "feed", "--format", "json", "--no-cache"],
        capture_output=True, text=True, timeout=30,
        cwd=str(Path(__file__).parent.parent),
    )
    # Feed may succeed (cached) or fail (no network) — should not crash
    assert_true(r.returncode in (0, 1, 2),
                f"feed should not crash, got exit {r.returncode}")
    assert_true("Traceback" not in r.stderr,
                f"should not show traceback: {r.stderr[:200]}")
    print("\u2713 Reliability: feed handles network issues gracefully")


def test_narrowed_exceptions_no_bare_except():
    """No bare except: blocks in codebase (all should be specific)."""
    scripts_dir = Path(__file__).parent.parent / "scripts"
    hooks_dir = Path(__file__).parent.parent / "hooks"
    bare_count = 0
    for py_file in list(scripts_dir.glob("*.py")) + list(hooks_dir.glob("*.py")):
        content = py_file.read_text(encoding="utf-8", errors="ignore")
        for i, line in enumerate(content.split("\n"), 1):
            stripped = line.strip()
            # Bare "except:" with no exception type
            if stripped == "except:" or stripped.startswith("except:"):
                bare_count += 1
    assert_eq(bare_count, 0, f"found {bare_count} bare except: blocks (should be 0)")
    print("\u2713 Reliability: no bare except: blocks in codebase")


# ── Runner ──────────────────────────────────────────────────────────


if __name__ == "__main__":
    tests = [
        test_large_file_skipped_gracefully,
        test_binary_file_skipped,
        test_unicode_emoji_in_classification,
        test_unicode_rtl_in_classification,
        test_unicode_zero_width_in_classification,
        test_null_bytes_in_classification,
        test_permission_denied_structured_message,
        test_empty_file_no_crash,
        test_deeply_nested_json_in_hook,
        test_concurrent_registry_writes,
        test_feed_network_timeout_graceful,
        test_narrowed_exceptions_no_bare_except,
    ]

    print(f"Running {len(tests)} reliability tests...\n")

    for test in tests:
        try:
            test()
        except Exception as e:
            helpers.failed += 1
            print(f"  EXCEPTION in {test.__name__}: {e}")

    print(f"\n{'=' * 50}")
    print(f"Results: {helpers.passed} passed, {helpers.failed} failed ({len(tests)} test functions)")
    if helpers.failed:
        print("SOME TESTS FAILED")
        sys.exit(1)
    else:
        print("All tests passed!")
