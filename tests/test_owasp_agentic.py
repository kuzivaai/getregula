# regula-ignore
#!/usr/bin/env python3
"""
Tests for OWASP Top 10 for Agentic Applications detection.

Validates pattern detection for all 10 OWASP Agentic risks,
coverage scoring, and text formatting.
"""

import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

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


def _make_project(files: dict) -> str:
    """Create a temp project with given files. Returns path."""
    d = tempfile.mkdtemp()
    for name, content in files.items():
        p = Path(d) / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)
    return d


# ── ASI01: Agent Goal Hijack ──────────────────────────────────────


def test_asi01_vuln_detected():
    """Prompt injection pattern -> at_risk."""
    from agent_monitor import assess_owasp_agentic
    proj = _make_project({"agent.py": 'instructions = f"Do {user_input} now"\n'})
    result = assess_owasp_agentic(proj)
    r = [x for x in result["risks"] if x["id"] == "regula-ASI01"][0]
    assert_eq(r["status"], "at_risk", "ASI01 vuln without control should be at_risk")
    print("\u2713 ASI01: goal hijack vulnerability detected")


def test_asi01_mitigated():
    """Prompt injection + sanitisation -> mitigated."""
    from agent_monitor import assess_owasp_agentic
    proj = _make_project({"agent.py": (
        'instructions = f"Do {user_input} now"\n'
        'sanitize_input(user_input)\n'
    )})
    result = assess_owasp_agentic(proj)
    r = [x for x in result["risks"] if x["id"] == "regula-ASI01"][0]
    assert_eq(r["status"], "mitigated", "ASI01 vuln + control should be mitigated")
    print("\u2713 ASI01: goal hijack mitigated when control present")


# ── ASI02: Tool Misuse ────────────────────────────────────────────


def test_asi02_vuln_detected():
    """Wildcard tool access -> at_risk."""
    from agent_monitor import assess_owasp_agentic
    proj = _make_project({"tools.py": 'tools = ["*"]\n'})
    result = assess_owasp_agentic(proj)
    r = [x for x in result["risks"] if x["id"] == "regula-ASI02"][0]
    assert_eq(r["status"], "at_risk", "ASI02 wildcard tools should be at_risk")
    print("\u2713 ASI02: tool misuse vulnerability detected")


def test_asi02_mitigated():
    """Tool allowlist present -> mitigated."""
    from agent_monitor import assess_owasp_agentic
    proj = _make_project({"tools.py": (
        'tools = ["*"]\n'
        'ALLOWED_TOOLS = ["search", "calculate"]\n'
    )})
    result = assess_owasp_agentic(proj)
    r = [x for x in result["risks"] if x["id"] == "regula-ASI02"][0]
    assert_eq(r["status"], "mitigated", "ASI02 with allowlist should be mitigated")
    print("\u2713 ASI02: tool misuse mitigated with allowlist")


# ── ASI03: Identity and Privilege Abuse ───────────────────────────


def test_asi03_vuln_detected():
    """Shared credentials -> at_risk."""
    from agent_monitor import assess_owasp_agentic
    proj = _make_project({"auth.py": 'SHARED_API_KEY = "abc123"\n'})
    result = assess_owasp_agentic(proj)
    r = [x for x in result["risks"] if x["id"] == "regula-ASI03"][0]
    assert_eq(r["status"], "at_risk", "ASI03 shared key should be at_risk")
    print("\u2713 ASI03: identity abuse vulnerability detected")


def test_asi03_mitigated():
    """RBAC present -> mitigated."""
    from agent_monitor import assess_owasp_agentic
    proj = _make_project({"auth.py": (
        'SHARED_API_KEY = "abc123"\n'
        'def authorize_agent(agent, action): pass\n'
    )})
    result = assess_owasp_agentic(proj)
    r = [x for x in result["risks"] if x["id"] == "regula-ASI03"][0]
    assert_eq(r["status"], "mitigated", "ASI03 with RBAC should be mitigated")
    print("\u2713 ASI03: identity abuse mitigated with RBAC")


# ── ASI04: Supply Chain Vulnerabilities ───────────────────────────


def test_asi04_vuln_detected():
    """Piped curl install -> at_risk."""
    from agent_monitor import assess_owasp_agentic
    proj = _make_project({"setup.py": 'os.system("curl http://example.com/install | bash")\n'})
    result = assess_owasp_agentic(proj)
    r = [x for x in result["risks"] if x["id"] == "regula-ASI04"][0]
    assert_eq(r["status"], "at_risk", "ASI04 piped install should be at_risk")
    print("\u2713 ASI04: supply chain vulnerability detected")


def test_asi04_mitigated():
    """Integrity checks -> mitigated."""
    from agent_monitor import assess_owasp_agentic
    proj = _make_project({"setup.py": (
        'os.system("curl http://example.com/install | bash")\n'
        'verify_integrity(plugin_path)\n'
    )})
    result = assess_owasp_agentic(proj)
    r = [x for x in result["risks"] if x["id"] == "regula-ASI04"][0]
    assert_eq(r["status"], "mitigated", "ASI04 with integrity check should be mitigated")
    print("\u2713 ASI04: supply chain mitigated with integrity checks")


# ── ASI05: Unexpected Code Execution ──────────────────────────────


def test_asi05_vuln_detected():
    """eval() without sandbox -> at_risk."""
    from agent_monitor import assess_owasp_agentic
    proj = _make_project({"runner.py": 'result = eval(user_code)\n'})
    result = assess_owasp_agentic(proj)
    r = [x for x in result["risks"] if x["id"] == "regula-ASI05"][0]
    assert_eq(r["status"], "at_risk", "ASI05 eval should be at_risk")
    print("\u2713 ASI05: RCE vulnerability detected")


def test_asi05_mitigated():
    """Sandbox present -> mitigated."""
    from agent_monitor import assess_owasp_agentic
    proj = _make_project({"runner.py": (
        'result = eval(user_code)\n'
        'sandbox_exec(code, timeout=30)\n'
    )})
    result = assess_owasp_agentic(proj)
    r = [x for x in result["risks"] if x["id"] == "regula-ASI05"][0]
    assert_eq(r["status"], "mitigated", "ASI05 with sandbox should be mitigated")
    print("\u2713 ASI05: RCE mitigated with sandbox")


# ── ASI06: Memory & Context Poisoning ─────────────────────────────


def test_asi06_vuln_detected():
    """Unvalidated context append -> at_risk."""
    from agent_monitor import assess_owasp_agentic
    proj = _make_project({"memory.py": 'conversation.append(new_message)\n'})
    result = assess_owasp_agentic(proj)
    r = [x for x in result["risks"] if x["id"] == "regula-ASI06"][0]
    assert_eq(r["status"], "at_risk", "ASI06 unvalidated context should be at_risk")
    print("\u2713 ASI06: memory poisoning vulnerability detected")


def test_asi06_mitigated():
    """Context validation present -> mitigated."""
    from agent_monitor import assess_owasp_agentic
    proj = _make_project({"memory.py": (
        'conversation.append(new_message)\n'
        'validate_context(conversation)\n'
    )})
    result = assess_owasp_agentic(proj)
    r = [x for x in result["risks"] if x["id"] == "regula-ASI06"][0]
    assert_eq(r["status"], "mitigated", "ASI06 with validation should be mitigated")
    print("\u2713 ASI06: memory poisoning mitigated with validation")


# ── ASI07: Insecure Inter-Agent Communication ─────────────────────


def test_asi07_vuln_detected():
    """Unauth agent calls -> at_risk."""
    from agent_monitor import assess_owasp_agentic
    proj = _make_project({"comms.py": 'agent_call(target_agent, payload)\n'})
    result = assess_owasp_agentic(proj)
    r = [x for x in result["risks"] if x["id"] == "regula-ASI07"][0]
    assert_eq(r["status"], "at_risk", "ASI07 unauth comms should be at_risk")
    print("\u2713 ASI07: insecure comms vulnerability detected")


def test_asi07_mitigated():
    """Agent auth present -> mitigated."""
    from agent_monitor import assess_owasp_agentic
    proj = _make_project({"comms.py": (
        'agent_call(target_agent, payload)\n'
        'authenticate_agent(sender_id)\n'
    )})
    result = assess_owasp_agentic(proj)
    r = [x for x in result["risks"] if x["id"] == "regula-ASI07"][0]
    assert_eq(r["status"], "mitigated", "ASI07 with auth should be mitigated")
    print("\u2713 ASI07: insecure comms mitigated with auth")


# ── ASI08: Cascading Failures ─────────────────────────────────────


def test_asi08_vuln_detected():
    """Bare except with pass -> at_risk."""
    from agent_monitor import assess_owasp_agentic
    proj = _make_project({"chain.py": 'except: pass\n'})
    result = assess_owasp_agentic(proj)
    r = [x for x in result["risks"] if x["id"] == "regula-ASI08"][0]
    assert_eq(r["status"], "at_risk", "ASI08 bare except should be at_risk")
    print("\u2713 ASI08: cascading failure vulnerability detected")


def test_asi08_mitigated():
    """Circuit breaker present -> mitigated."""
    from agent_monitor import assess_owasp_agentic
    proj = _make_project({"chain.py": (
        'except: pass\n'
        'cb = CircuitBreaker(max_failures=3)\n'
    )})
    result = assess_owasp_agentic(proj)
    r = [x for x in result["risks"] if x["id"] == "regula-ASI08"][0]
    assert_eq(r["status"], "mitigated", "ASI08 with circuit breaker should be mitigated")
    print("\u2713 ASI08: cascading failures mitigated with circuit breaker")


# ── ASI09: Human-Agent Trust Exploitation ─────────────────────────


def test_asi09_vuln_detected():
    """Agent impersonation -> at_risk."""
    from agent_monitor import assess_owasp_agentic
    proj = _make_project({"bot.py": 'hide_identity(agent)\n'})
    result = assess_owasp_agentic(proj)
    r = [x for x in result["risks"] if x["id"] == "regula-ASI09"][0]
    assert_eq(r["status"], "at_risk", "ASI09 impersonation should be at_risk")
    print("\u2713 ASI09: trust exploitation vulnerability detected")


def test_asi09_mitigated():
    """AI disclosure present -> mitigated."""
    from agent_monitor import assess_owasp_agentic
    proj = _make_project({"bot.py": (
        'hide_identity(agent)\n'
        'ai_disclosure(response)\n'
    )})
    result = assess_owasp_agentic(proj)
    r = [x for x in result["risks"] if x["id"] == "regula-ASI09"][0]
    assert_eq(r["status"], "mitigated", "ASI09 with disclosure should be mitigated")
    print("\u2713 ASI09: trust exploitation mitigated with disclosure")


# ── ASI10: Rogue Agents ───────────────────────────────────────────


def test_asi10_vuln_detected():
    """Unrestricted mode -> at_risk."""
    from agent_monitor import assess_owasp_agentic
    proj = _make_project({"agent.py": 'autonomous_mode = True\n'})
    result = assess_owasp_agentic(proj)
    r = [x for x in result["risks"] if x["id"] == "regula-ASI10"][0]
    assert_eq(r["status"], "at_risk", "ASI10 autonomous mode should be at_risk")
    print("\u2713 ASI10: rogue agent vulnerability detected")


def test_asi10_mitigated():
    """Kill switch present -> mitigated."""
    from agent_monitor import assess_owasp_agentic
    proj = _make_project({"agent.py": (
        'autonomous_mode = True\n'
        'kill_switch(agent_id)\n'
    )})
    result = assess_owasp_agentic(proj)
    r = [x for x in result["risks"] if x["id"] == "regula-ASI10"][0]
    assert_eq(r["status"], "mitigated", "ASI10 with kill switch should be mitigated")
    print("\u2713 ASI10: rogue agent mitigated with kill switch")


# ── Coverage Score ────────────────────────────────────────────────


def test_coverage_score_empty():
    """Empty project -> 0% coverage, all not_assessed."""
    from agent_monitor import assess_owasp_agentic
    proj = _make_project({})
    result = assess_owasp_agentic(proj)
    assert_eq(result["coverage_score"], 0, "empty project should be 0% coverage")
    assert_true(all(r["status"] == "not_assessed" for r in result["risks"]),
                "all risks should be not_assessed for empty project")
    print("\u2713 Coverage: empty project = 0%")


def test_coverage_score_full():
    """All 10 mitigated -> 100%."""
    from agent_monitor import assess_owasp_agentic
    # Build a project that triggers both vuln + control for all 10
    proj = _make_project({"all.py": (
        'instructions = f"Do {user_input} now"\n'
        'sanitize_input(x)\n'
        'tools = ["*"]\n'
        'ALLOWED_TOOLS = ["a"]\n'
        'SHARED_API_KEY = "x"\n'
        'authorize_agent(a, b)\n'
        'os.system("curl http://x | bash")\n'
        'verify_integrity(p)\n'
        'eval(code)\n'
        'sandbox_exec(code)\n'
        'conversation.append(msg)\n'
        'validate_context(c)\n'
        'agent_call(a, b)\n'
        'authenticate_agent(s)\n'
        'except: pass\n'
        'CircuitBreaker()\n'
        'hide_identity(a)\n'
        'ai_disclosure(r)\n'
        'autonomous_mode = True\n'
        'kill_switch(a)\n'
    )})
    result = assess_owasp_agentic(proj)
    assert_eq(result["coverage_score"], 100, "fully mitigated project should be 100%")
    print("\u2713 Coverage: fully mitigated = 100%")


# ── Text Formatting ───────────────────────────────────────────────


def test_format_output_structure():
    """Format output has required sections."""
    from agent_monitor import assess_owasp_agentic, format_owasp_agentic_text
    proj = _make_project({"agent.py": 'eval(code)\n'})
    result = assess_owasp_agentic(proj)
    text = format_owasp_agentic_text(result)
    assert_true("OWASP" in text, "output should mention OWASP")
    assert_true("Coverage Score" in text, "output should show coverage score")
    assert_true("regula-ASI05" in text, "output should show risk IDs")
    assert_true("AT RISK" in text or "ACTION NEEDED" in text,
                "output should show at_risk status")
    print("\u2713 Format: output has required structure")


def test_format_grouping_order():
    """at_risk items appear before mitigated items."""
    from agent_monitor import assess_owasp_agentic, format_owasp_agentic_text
    proj = _make_project({"agent.py": (
        'eval(code)\n'
        'conversation.append(msg)\n'
        'validate_context(c)\n'
    )})
    result = assess_owasp_agentic(proj)
    text = format_owasp_agentic_text(result)
    action_pos = text.find("ACTION NEEDED")
    mitigated_pos = text.find("MITIGATED")
    if action_pos >= 0 and mitigated_pos >= 0:
        assert_true(action_pos < mitigated_pos, "ACTION NEEDED should appear before MITIGATED")
    print("\u2713 Format: at_risk grouped before mitigated")


# ── Runner ────────────────────────────────────────────────────────


if __name__ == "__main__":
    tests = [
        test_asi01_vuln_detected,
        test_asi01_mitigated,
        test_asi02_vuln_detected,
        test_asi02_mitigated,
        test_asi03_vuln_detected,
        test_asi03_mitigated,
        test_asi04_vuln_detected,
        test_asi04_mitigated,
        test_asi05_vuln_detected,
        test_asi05_mitigated,
        test_asi06_vuln_detected,
        test_asi06_mitigated,
        test_asi07_vuln_detected,
        test_asi07_mitigated,
        test_asi08_vuln_detected,
        test_asi08_mitigated,
        test_asi09_vuln_detected,
        test_asi09_mitigated,
        test_asi10_vuln_detected,
        test_asi10_mitigated,
        test_coverage_score_empty,
        test_coverage_score_full,
        test_format_output_structure,
        test_format_grouping_order,
    ]

    print(f"Running {len(tests)} OWASP Agentic tests...\n")

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
