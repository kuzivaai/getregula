# regula-ignore
#!/usr/bin/env python3
"""
Tests for registry usability enhancements.

Tests the enhanced status command (--show, --format, --sync)
and risk trend tracking in the registry.
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import helpers
from helpers import assert_eq, assert_true


# ── Helper ──────────────────────────────────────────────────────────


def _make_registry(tmp_dir, systems=None):
    """Create a test registry.json in tmp_dir and set env var."""
    registry = {"version": "1.0", "systems": systems or {}}
    reg_path = Path(tmp_dir) / "registry.json"
    reg_path.write_text(json.dumps(registry, indent=2), encoding="utf-8")
    return str(reg_path)


def _run_cli(*args, registry_path=None):
    """Run CLI command with optional custom registry path."""
    env = os.environ.copy()
    if registry_path:
        env["REGULA_REGISTRY"] = registry_path
    return subprocess.run(
        [sys.executable, "scripts/cli.py"] + list(args),
        capture_output=True, text=True, timeout=30,
        cwd=str(Path(__file__).parent.parent),
        env=env,
    )


SAMPLE_SYSTEM = {
    "registered_at": "2026-03-20T10:00:00+00:00",
    "last_scanned": "2026-03-25T10:00:00+00:00",
    "project_path": "/home/test/myproject",
    "ai_libraries": ["openai", "torch"],
    "primary_language": "python",
    "model_files": [{"path": "model.pt", "extension": ".pt", "size_mb": 5.2}],
    "ai_code_files": ["app.py", "model.py"],
    "api_endpoints": ["api.openai.com"],
    "risk_classifications": [
        {"file": "app.py", "tier": "high_risk", "indicators": ["employment"],
         "description": "Employment and workers management"}
    ],
    "highest_risk": "high_risk",
    "compliance_status": "assessment",
    "notes": "",
}


# ── Test: Empty Registry ────────────────────────────────────────────


def test_status_empty_registry():
    """Empty registry returns clean message, not error."""
    with tempfile.TemporaryDirectory() as tmp:
        reg_path = _make_registry(tmp, systems={})
        r = _run_cli("status", registry_path=reg_path)
        assert_eq(r.returncode, 0, "empty registry should exit 0")
        assert_true("no systems" in r.stdout.lower() or "0 system" in r.stdout.lower(),
                    f"should mention no systems, got: {r.stdout[:200]}")
    print("\u2713 Registry: empty registry shows clean message")


# ── Test: Status List ───────────────────────────────────────────────


def test_status_list_with_systems():
    """Status shows table with name, risk, compliance, last_scan."""
    with tempfile.TemporaryDirectory() as tmp:
        reg_path = _make_registry(tmp, systems={"MyApp": SAMPLE_SYSTEM})
        r = _run_cli("status", registry_path=reg_path)
        assert_eq(r.returncode, 0, "status with systems should exit 0")
        assert_true("MyApp" in r.stdout, "should show system name")
        assert_true("HIGH" in r.stdout.upper(), "should show risk tier")
    print("\u2713 Registry: status lists registered systems")


# ── Test: Status Show Detail ────────────────────────────────────────


def test_status_show_existing():
    """--show <name> returns detailed info for known system."""
    with tempfile.TemporaryDirectory() as tmp:
        reg_path = _make_registry(tmp, systems={"MyApp": SAMPLE_SYSTEM})
        r = _run_cli("status", "--show", "MyApp", registry_path=reg_path)
        assert_eq(r.returncode, 0, "show existing should exit 0")
        assert_true("MyApp" in r.stdout, "should show system name")
        assert_true("openai" in r.stdout.lower() or "torch" in r.stdout.lower(),
                    "should show AI libraries")
    print("\u2713 Registry: --show displays detailed system info")


def test_status_show_missing():
    """--show <name> for unknown system returns error message."""
    with tempfile.TemporaryDirectory() as tmp:
        reg_path = _make_registry(tmp, systems={"MyApp": SAMPLE_SYSTEM})
        r = _run_cli("status", "--show", "NonExistent", registry_path=reg_path)
        assert_true(r.returncode in (0, 1, 2), "should not crash")
        output = r.stdout + r.stderr
        assert_true("not found" in output.lower() or "no system" in output.lower(),
                    f"should say system not found, got: {output[:200]}")
    print("\u2713 Registry: --show unknown system shows error")


# ── Test: Status Export ─────────────────────────────────────────────


def test_status_export_csv():
    """--format csv produces valid CSV with headers."""
    with tempfile.TemporaryDirectory() as tmp:
        reg_path = _make_registry(tmp, systems={"MyApp": SAMPLE_SYSTEM})
        r = _run_cli("status", "--format", "csv", registry_path=reg_path)
        assert_eq(r.returncode, 0, "csv export should exit 0")
        lines = r.stdout.strip().split("\n")
        assert_true(len(lines) >= 2, f"CSV should have header + data, got {len(lines)} lines")
        assert_true("System Name" in lines[0] or "system" in lines[0].lower(),
                    f"CSV should have header row, got: {lines[0]}")
        assert_true("MyApp" in lines[1], f"CSV data should contain system name, got: {lines[1]}")
    print("\u2713 Registry: --format csv produces valid CSV")


def test_status_export_json():
    """--format json produces valid JSON with systems."""
    with tempfile.TemporaryDirectory() as tmp:
        reg_path = _make_registry(tmp, systems={"MyApp": SAMPLE_SYSTEM})
        r = _run_cli("status", "--format", "json", registry_path=reg_path)
        assert_eq(r.returncode, 0, "json export should exit 0")
        data = json.loads(r.stdout)
        assert_true("systems" in data or "data" in data,
                    f"JSON should contain systems, got keys: {list(data.keys())}")
    print("\u2713 Registry: --format json produces valid JSON")


# ── Test: Discover Sync ─────────────────────────────────────────────


def test_discover_sync_rescans():
    """--sync re-scans all previously registered projects."""
    with tempfile.TemporaryDirectory() as tmp:
        # Register a real fixture project
        fixtures = str(Path(__file__).parent / "fixtures" / "sample_compliant")
        reg_path = _make_registry(tmp, systems={
            "sample_compliant": {
                **SAMPLE_SYSTEM,
                "project_path": fixtures,
                "last_scanned": "2026-01-01T00:00:00+00:00",
            }
        })
        r = _run_cli("discover", "--sync", registry_path=reg_path)
        assert_eq(r.returncode, 0, f"sync should exit 0, got {r.returncode}: {r.stderr[:200]}")
        # Read updated registry
        updated = json.loads(Path(reg_path).read_text(encoding="utf-8"))
        system = updated["systems"].get("sample_compliant", {})
        assert_true(system.get("last_scanned", "") > "2026-01-01",
                    f"last_scanned should be updated, got: {system.get('last_scanned')}")
    print("\u2713 Registry: --sync re-scans and updates timestamps")


# ── Test: Risk Trend Tracking ───────────────────────────────────────


def test_risk_trend_tracking():
    """Re-registering tracks previous_highest_risk for trend detection."""
    with tempfile.TemporaryDirectory() as tmp:
        reg_path = _make_registry(tmp, systems={
            "sample_compliant": {
                **SAMPLE_SYSTEM,
                "highest_risk": "high_risk",
                "project_path": str(Path(__file__).parent / "fixtures" / "sample_compliant"),
            }
        })
        # Re-scan the compliant fixture (should be minimal_risk now)
        env = os.environ.copy()
        env["REGULA_REGISTRY"] = reg_path
        r = subprocess.run(
            [sys.executable, "scripts/cli.py", "discover", "--register",
             "--project", "tests/fixtures/sample_compliant/"],
            capture_output=True, text=True, timeout=30,
            cwd=str(Path(__file__).parent.parent),
            env=env,
        )
        assert_eq(r.returncode, 0, f"re-register should exit 0: {r.stderr[:200]}")
        updated = json.loads(Path(reg_path).read_text(encoding="utf-8"))
        system = updated["systems"].get("sample_compliant", {})
        assert_true("previous_highest_risk" in system,
                    f"should track previous_highest_risk, got keys: {list(system.keys())}")
        assert_eq(system["previous_highest_risk"], "high_risk",
                  "previous_highest_risk should be the old value")
    print("\u2713 Registry: re-scan tracks previous_highest_risk for trend")


# ── Runner ──────────────────────────────────────────────────────────


if __name__ == "__main__":
    tests = [
        test_status_empty_registry,
        test_status_list_with_systems,
        test_status_show_existing,
        test_status_show_missing,
        test_status_export_csv,
        test_status_export_json,
        test_discover_sync_rescans,
        test_risk_trend_tracking,
    ]

    print(f"Running {len(tests)} registry tests...\n")

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
