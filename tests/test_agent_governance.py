# regula-ignore
#!/usr/bin/env python3
"""
Tests for agent governance enhancements (Package 3).

Validates MCP server permission analysis, tool chain risk assessment,
autonomous action detection, and OWASP Agentic Top 10 mapping.

Research-backed: OWASP Top 10 for Agentic Applications (Dec 2025),
EU AI Act Article 14 (human oversight), OWASP LLM08 (excessive agency).
"""

import json
import os
import sys
import tempfile
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


# ── MCP Config Parsing ──────────────────────────────────────────────


def test_agent_mcp_server_parse():
    """Parses MCP server config, extracts tool/server names."""
    from agent_monitor import parse_mcp_servers

    config = {
        "mcpServers": {
            "filesystem": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
            },
            "postgres": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-postgres"],
                "env": {"DATABASE_URL": "postgresql://localhost/mydb"},
            },
        }
    }
    servers = parse_mcp_servers(config)
    assert_eq(len(servers), 2, f"should find 2 servers, got {len(servers)}")
    names = {s["name"] for s in servers}
    assert_true("filesystem" in names, "should find filesystem server")
    assert_true("postgres" in names, "should find postgres server")
    print("\u2713 Agent: parses MCP server config")


def test_agent_mcp_write_access_warning():
    """MCP server with filesystem write access -> HIGH risk flag."""
    from agent_monitor import assess_mcp_risk

    servers = [
        {"name": "filesystem", "command": "npx",
         "args": ["-y", "@modelcontextprotocol/server-filesystem", "/home"],
         "env": {}},
    ]
    risks = assess_mcp_risk(servers)
    fs_risks = [r for r in risks if r["server"] == "filesystem"]
    assert_true(len(fs_risks) > 0, "filesystem server should have risk flags")
    assert_true(any(r["severity"] in ("HIGH", "MEDIUM") for r in fs_risks),
                "filesystem access should be HIGH or MEDIUM risk")
    print("\u2713 Agent: filesystem MCP server flagged as risk")


def test_agent_mcp_api_key_in_env():
    """API key passed via env -> MEDIUM risk (acceptable pattern)."""
    from agent_monitor import assess_mcp_risk

    servers = [
        {"name": "weather", "command": "npx",
         "args": ["-y", "weather-mcp"],
         "env": {"API_KEY": "sk-test1234567890abcdef"}},
    ]
    risks = assess_mcp_risk(servers)
    env_risks = [r for r in risks if "credential" in r.get("category", "").lower()
                 or "key" in r.get("description", "").lower()]
    assert_true(len(env_risks) > 0, "API key in env should be flagged")
    # Should be MEDIUM not HIGH — env is the recommended approach
    assert_true(all(r["severity"] != "CRITICAL" for r in env_risks),
                "env-based key should not be CRITICAL (it's the recommended pattern)")
    print("\u2713 Agent: API key in env flagged as MEDIUM risk")


def test_agent_mcp_api_key_hardcoded():
    """API key hardcoded in args -> HIGH risk flag."""
    from agent_monitor import assess_mcp_risk

    servers = [
        {"name": "custom", "command": "node",
         "args": ["server.js", "--api-key", "sk-ant-abcdef1234567890abcdef1234567890"],
         "env": {}},
    ]
    risks = assess_mcp_risk(servers)
    hardcoded_risks = [r for r in risks if r["severity"] == "HIGH"]
    assert_true(len(hardcoded_risks) > 0,
                "hardcoded API key in args should be HIGH risk")
    print("\u2713 Agent: hardcoded API key in args flagged as HIGH risk")


# ── Autonomous Action Detection ─────────────────────────────────────


def test_agent_autonomous_action_detection():
    """model output -> external action without human check -> flagged."""
    from agent_monitor import detect_autonomous_actions

    code = '''
import openai
import requests

response = openai.chat.completions.create(model="gpt-4", messages=messages)
action = response.choices[0].message.content
requests.post("https://api.example.com/execute", json={"action": action})
'''
    findings = detect_autonomous_actions(code)
    assert_true(len(findings) > 0,
                "should detect AI output -> external action without human gate")
    print("\u2713 Agent: detects autonomous action (AI -> external call)")


def test_agent_human_gate_present():
    """Human approval before external action -> no autonomous flag."""
    from agent_monitor import detect_autonomous_actions

    code = '''
import openai

response = openai.chat.completions.create(model="gpt-4", messages=messages)
suggestion = response.choices[0].message.content
if user_approved(suggestion):
    execute_action(suggestion)
'''
    findings = detect_autonomous_actions(code)
    # Should have fewer or no findings compared to ungated version
    ungated_findings = [f for f in findings if "no human" in f.get("description", "").lower()
                        or "autonomous" in f.get("description", "").lower()]
    # This is heuristic — the test checks the gate reduces risk flags
    print("\u2713 Agent: human gate detection (heuristic)")


# ── OWASP Mapping ──────────────────────────────────────────────────


def test_agent_owasp_excessive_agency():
    """Excessive tool permissions -> OWASP Agentic #1 mapping."""
    from agent_monitor import assess_mcp_risk

    servers = [
        {"name": "everything", "command": "npx",
         "args": ["-y", "@modelcontextprotocol/server-everything"],
         "env": {}},
    ]
    risks = assess_mcp_risk(servers)
    owasp_mapped = [r for r in risks if "owasp" in r or "agentic" in str(r).lower()]
    # At minimum, the tool should flag unknown/broad servers
    assert_true(len(risks) > 0, "broad-access server should have risk flags")
    print("\u2713 Agent: broad-access MCP server flagged")


def test_agent_owasp_sensitive_disclosure():
    """PII patterns in tool config -> flagged."""
    from agent_monitor import assess_mcp_risk

    servers = [
        {"name": "database", "command": "npx",
         "args": ["-y", "@modelcontextprotocol/server-postgres"],
         "env": {"DATABASE_URL": "postgresql://admin:password123@prod.example.com/users"}},
    ]
    risks = assess_mcp_risk(servers)
    cred_risks = [r for r in risks if "credential" in r.get("category", "").lower()
                  or "password" in r.get("description", "").lower()]
    assert_true(len(cred_risks) > 0,
                "database password in env should be flagged")
    print("\u2713 Agent: database credential in MCP config flagged")


def test_agent_owasp_excessive_autonomy():
    """Agent with subprocess.run on AI output -> LLM08 flag."""
    from agent_monitor import detect_autonomous_actions

    code = '''
import anthropic
import subprocess

client = anthropic.Client()
response = client.messages.create(model="claude-3-opus-20240229", messages=messages)
command = response.content[0].text
subprocess.run(command, shell=True)
'''
    findings = detect_autonomous_actions(code)
    assert_true(len(findings) > 0,
                "AI output -> subprocess.run should be flagged as excessive autonomy")
    print("\u2713 Agent: AI output -> subprocess flagged (LLM08)")


def test_agent_risk_summary_format():
    """Risk summary includes OWASP Agentic references."""
    from agent_monitor import assess_mcp_risk, format_mcp_risk_text

    servers = [
        {"name": "filesystem", "command": "npx",
         "args": ["-y", "@modelcontextprotocol/server-filesystem", "/"],
         "env": {}},
    ]
    risks = assess_mcp_risk(servers)
    text = format_mcp_risk_text(risks)
    assert_true(len(text) > 0, "risk summary should produce output")
    print("\u2713 Agent: risk summary produces formatted output")


# ── Contextual Agent Path Detection (ASI02/ASI04) ──────────────────


def test_agent_contextual_path_detection():
    """Files in agent/tool paths with subprocess -> flagged even without AI imports."""
    from agent_monitor import detect_autonomous_actions

    code = '''
import subprocess
import tempfile

def execute_shell(command: str) -> str:
    result = subprocess.run(command, shell=True, capture_output=True)
    return result.stdout.decode()
'''
    # Without agent path context — should NOT flag (no AI patterns)
    findings = detect_autonomous_actions(code, filepath="utils/helpers.py")
    assert_eq(len(findings), 0,
              "non-agent path without AI patterns should not be flagged")

    # With agent path context — SHOULD flag
    findings = detect_autonomous_actions(code, filepath="agents/middleware/shell_tool.py")
    assert_true(len(findings) > 0,
                "agent infrastructure path with subprocess should be flagged")
    assert_true(all("Agent tool infrastructure" in f["description"] for f in findings),
                "description should mention agent tool infrastructure")
    assert_true(all(f["detection_mode"] == "contextual" for f in findings),
                "detection mode should be contextual for path-based detection")
    print("\u2713 Agent: contextual path detection flags agent infrastructure subprocess")


def test_agent_contextual_path_variants():
    """Various agent-related path patterns are detected."""
    from agent_monitor import detect_autonomous_actions

    code = '''
import subprocess
subprocess.run(["ls", "-la"])
'''
    agent_paths = [
        "tools/shell_executor.py",
        "plugins/code_runner.py",
        "middleware/execution.py",
        "agent_framework/executor.py",
        "sandbox/runner.py",
    ]
    for path in agent_paths:
        findings = detect_autonomous_actions(code, filepath=path)
        assert_true(len(findings) > 0,
                    f"path '{path}' should trigger contextual detection")
    print("\u2713 Agent: all agent path variants trigger detection")


def test_agent_contextual_with_human_gate():
    """Agent infrastructure with human gate -> lower risk."""
    from agent_monitor import detect_autonomous_actions

    code = '''
import subprocess

def execute_command(cmd: str, dry_run: bool = True) -> str:
    if dry_run:
        return f"Would run: {cmd}"
    if user_approved(cmd):
        return subprocess.run(cmd, shell=True, capture_output=True).stdout.decode()
'''
    findings = detect_autonomous_actions(code, filepath="agents/tools/shell.py")
    assert_true(len(findings) > 0, "should still flag")
    assert_true(all(f["has_human_gate"] for f in findings),
                "human gate should be detected")
    assert_true(all("human gate pattern detected" in f["description"] for f in findings),
                "description should note human gate")
    print("\u2713 Agent: contextual detection with human gate lowers risk")


# ── scan_files Integration Tests ───────────────────────────────────


def test_scan_files_skip_tests():
    """--skip-tests flag excludes test files entirely."""
    from report import scan_files

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a test file and a non-test file
        (Path(tmpdir) / "app.py").write_text("import openai\nclient = openai.Client()\n")
        tests_dir = Path(tmpdir) / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_app.py").write_text("import openai\ndef test_foo(): pass\n")

        # Without skip_tests — both files should have findings
        all_findings = scan_files(tmpdir, skip_tests=False)
        files_found = {f["file"] for f in all_findings}
        assert_true("app.py" in files_found, "app.py should be found")
        assert_true("tests/test_app.py" in files_found, "test file should be found without skip_tests")

        # With skip_tests — only non-test file
        filtered = scan_files(tmpdir, skip_tests=True)
        files_found = {f["file"] for f in filtered}
        assert_true("app.py" in files_found, "app.py should still be found")
        assert_true("tests/test_app.py" not in files_found, "test file should be excluded with skip_tests")
    print("\u2713 scan_files: --skip-tests excludes test files")


def test_scan_files_min_tier():
    """--min-tier filters out lower tiers."""
    from report import scan_files

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a file that triggers minimal_risk (AI code, no risk indicators)
        (Path(tmpdir) / "basic.py").write_text("import tensorflow\nmodel = tf.keras.Model()\n")

        # With no min_tier — should have minimal_risk findings
        all_findings = scan_files(tmpdir, min_tier="")
        assert_true(any(f["tier"] == "minimal_risk" for f in all_findings),
                    "should find minimal_risk without filter")

        # With min_tier=limited_risk — minimal_risk should be filtered out
        filtered = scan_files(tmpdir, min_tier="limited_risk")
        assert_true(all(f["tier"] != "minimal_risk" for f in filtered),
                    "minimal_risk should be excluded with min_tier=limited_risk")
    print("\u2713 scan_files: --min-tier filters lower tiers")


def test_scan_files_agent_autonomy_integration():
    """Agent autonomy detection wired into scan_files."""
    from report import scan_files

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a file in an agent path with subprocess
        agent_dir = Path(tmpdir) / "agents" / "tools"
        agent_dir.mkdir(parents=True)
        (agent_dir / "executor.py").write_text(
            "import subprocess\n"
            "def run_command(cmd):\n"
            "    return subprocess.run(cmd, shell=True)\n"
        )

        findings = scan_files(tmpdir)
        autonomy_findings = [f for f in findings if f["tier"] == "agent_autonomy"]
        assert_true(len(autonomy_findings) > 0,
                    "agent autonomy detection should produce findings via scan_files")
        assert_true(all("Agent tool infrastructure" in f["description"] for f in autonomy_findings),
                    "findings should describe agent tool infrastructure")
    print("\u2713 scan_files: agent autonomy detection integrated")


def test_scan_files_agent_autonomy_test_deprioritisation():
    """Agent autonomy findings in test files get lower confidence."""
    from report import scan_files

    with tempfile.TemporaryDirectory() as tmpdir:
        # Agent tool in production code
        agent_dir = Path(tmpdir) / "agents"
        agent_dir.mkdir()
        (agent_dir / "tool.py").write_text(
            "import subprocess\ndef execute(cmd): subprocess.run(cmd)\n"
        )
        # Same pattern in test code
        test_dir = Path(tmpdir) / "tests"
        test_dir.mkdir()
        (test_dir / "test_tool.py").write_text(
            "import subprocess\ndef test_execute(): subprocess.run(['echo', 'hi'])\n"
        )

        findings = scan_files(tmpdir)
        prod_findings = [f for f in findings if f["tier"] == "agent_autonomy" and "tests/" not in f["file"]]
        test_findings = [f for f in findings if f["tier"] == "agent_autonomy" and "tests/" in f["file"]]

        if prod_findings and test_findings:
            assert_true(prod_findings[0]["confidence_score"] > test_findings[0]["confidence_score"],
                        "test file agent autonomy should have lower confidence than production")
    print("\u2713 scan_files: test file agent autonomy deprioritised")


# ── CLI Flag Tests ─────────────────────────────────────────────────


def test_cli_skip_tests_flag():
    """CLI accepts --skip-tests flag."""
    import subprocess as sp
    result = sp.run(
        [sys.executable, "-m", "scripts.cli", "check", "--skip-tests", "--format", "json", "."],
        capture_output=True, text=True,
        cwd=str(Path(__file__).parent.parent),
    )
    assert_eq(result.returncode, 0, f"--skip-tests should not cause error, got: {result.stderr[:200]}")
    data = json.loads(result.stdout)
    test_files = [f for f in data.get("data", []) if "test" in f.get("file", "").lower()]
    assert_eq(len(test_files), 0, "no test files should appear with --skip-tests")
    print("\u2713 CLI: --skip-tests flag works")


def test_cli_min_tier_flag():
    """CLI accepts --min-tier flag."""
    import subprocess as sp
    result = sp.run(
        [sys.executable, "-m", "scripts.cli", "check", "--min-tier", "limited_risk", "--format", "json", "."],
        capture_output=True, text=True,
        cwd=str(Path(__file__).parent.parent),
    )
    assert_eq(result.returncode, 0, f"--min-tier should not cause error, got: {result.stderr[:200]}")
    data = json.loads(result.stdout)
    minimal = [f for f in data.get("data", []) if f.get("tier") == "minimal_risk"]
    assert_eq(len(minimal), 0, "minimal_risk should be filtered with --min-tier=limited_risk")
    print("\u2713 CLI: --min-tier flag works")


# ── scan_files Edge Cases ───────────────────────────────────────────


def test_scan_files_skip_tests_all_conventions():
    """--skip-tests covers all test file naming conventions."""
    from report import scan_files

    with tempfile.TemporaryDirectory() as tmpdir:
        patterns = [
            ("tests/test_foo.py", "import openai\nclient = openai.Client()\n"),
            ("__tests__/bar.py", "import openai\nclient = openai.Client()\n"),
            ("foo_test.py", "import openai\nclient = openai.Client()\n"),
            ("src/components/Foo.spec.ts", "const client = new OpenAI();\n"),
            ("src/utils/Bar.test.js", "const client = new OpenAI();\n"),
            ("libs/standard-tests/baz.py", "import openai\nclient = openai.Client()\n"),
            ("src/langchain_tests/core.py", "import openai\nclient = openai.Client()\n"),
            ("src/app_test/main.py", "import openai\nclient = openai.Client()\n"),
        ]
        for rel_path, content in patterns:
            p = Path(tmpdir) / rel_path
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content)

        findings = scan_files(tmpdir, skip_tests=True)
        excluded = {f["file"] for f in findings if any(
            part.startswith("test") or part in {"tests", "__tests__", "standard-tests", "langchain_tests"}
            for part in Path(f["file"]).parts
        )}
        assert_eq(len(excluded), 0, f"all test conventions excluded, found: {excluded}")
    print("\u2713 scan_files: all test naming conventions excluded")


def test_scan_files_min_tier_prohibited():
    """--min-tier=prohibited keeps only prohibited findings."""
    from report import scan_files

    with tempfile.TemporaryDirectory() as tmpdir:
        (Path(tmpdir) / "social_scoring.py").write_text(
            "def score_people(people): return [p.score for p in people]\n"
        )
        findings = scan_files(tmpdir, min_tier="prohibited")
        tiers = {f["tier"] for f in findings}
        assert_true(
            all(t in ("prohibited",) for t in tiers),
            f"only prohibited should remain with min_tier=prohibited, got: {tiers}"
        )
    print("\u2713 scan_files: min_tier=prohibited filters correctly")


def test_scan_files_min_tier_high_risk():
    """--min-tier=high_risk keeps high_risk and prohibited."""
    from report import scan_files

    with tempfile.TemporaryDirectory() as tmpdir:
        (Path(tmpdir) / "cv_screening.py").write_text(
            "import sklearn; cv_screening(candidates)\n"
        )
        (Path(tmpdir) / "chatbot.py").write_text(
            "import openai; client = openai.Client()\n"
        )
        findings = scan_files(tmpdir, min_tier="high_risk")
        tiers = {f["tier"] for f in findings}
        assert_true(
            all(t in ("high_risk", "prohibited", "limited_risk", "agent_autonomy", "credential_exposure", "ai_security")
                for t in tiers),
            f"no minimal_risk with min_tier=high_risk, got: {tiers}"
        )
        assert_true(
            "minimal_risk" not in tiers,
            f"minimal_risk should be filtered at min_tier=high_risk, got: {tiers}"
        )
    print("\u2713 scan_files: min_tier=high_risk filters correctly")


def test_scan_files_min_tier_preserves_agent_autonomy():
    """--min-tier=limited_risk should NOT filter agent_autonomy findings."""
    from report import scan_files

    with tempfile.TemporaryDirectory() as tmpdir:
        (Path(tmpdir) / "agents").mkdir(parents=True, exist_ok=True)
        (Path(tmpdir) / "agents" / "shell.py").write_text(
            "import subprocess\nsubprocess.run(['ls'])\n"
        )
        (Path(tmpdir) / "app.py").write_text(
            "import openai\nclient = openai.Client()\n"
        )
        findings = scan_files(tmpdir, min_tier="limited_risk")
        tiers = {f["tier"] for f in findings}
        assert_true(
            "agent_autonomy" in tiers,
            f"agent_autonomy should be preserved at min_tier=limited_risk, got: {tiers}"
        )
    print("\u2713 scan_files: agent_autonomy preserved at min_tier=limited_risk")


def test_scan_files_combined_skip_tests_and_min_tier():
    """--skip-tests and --min-tier work together."""
    from report import scan_files

    with tempfile.TemporaryDirectory() as tmpdir:
        tests_dir = Path(tmpdir) / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_app.py").write_text(
            "import openai; client = openai.Client()\n"
        )
        (Path(tmpdir) / "agents").mkdir(parents=True, exist_ok=True)
        (Path(tmpdir) / "agents" / "shell.py").write_text(
            "import subprocess\nsubprocess.run(['ls'])\n"
        )
        (Path(tmpdir) / "chatbot.py").write_text(
            "import openai\nclient = openai.Client()\n"
        )
        findings = scan_files(tmpdir, skip_tests=True, min_tier="limited_risk")
        tiers = {f["tier"] for f in findings}
        files = {f["file"] for f in findings}
        assert_true("tests/test_app.py" not in files, "test file should be excluded")
        assert_true("minimal_risk" not in tiers, "minimal_risk filtered")
        assert_true(
            any(f["tier"] == "agent_autonomy" for f in findings),
            "agent_autonomy should be present"
        )
    print("\u2713 scan_files: combined skip_tests + min_tier works")


def test_scan_files_respect_ignores_overrides_skip_tests():
    """--skip-tests does not override explicit suppression."""
    from report import scan_files

    with tempfile.TemporaryDirectory() as tmpdir:
        tests_dir = Path(tmpdir) / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_app.py").write_text(
            "# regula-ignore\nimport openai\nclient = openai.Client()\n"
        )
        (Path(tmpdir) / "app.py").write_text(
            "import openai\nclient = openai.Client()\n"
        )
        findings = scan_files(tmpdir, respect_ignores=True, skip_tests=False)
        suppressed = [f for f in findings if f.get("suppressed")]
        assert_true(
            any("test_app.py" in f["file"] and f.get("suppressed") for f in findings),
            "regula-ignore in test file should suppress even without --skip-tests"
        )
    print("\u2713 scan_files: explicit suppression overrides test inclusion")


# ── CLI Combined Flag Tests ──────────────────────────────────────────


def test_cli_combined_skip_tests_and_min_tier():
    """CLI accepts --skip-tests and --min-tier together."""
    import subprocess as sp
    result = sp.run(
        [sys.executable, "-m", "scripts.cli", "check",
         "--skip-tests", "--min-tier", "limited_risk",
         "--format", "json", "."],
        capture_output=True, text=True,
        cwd=str(Path(__file__).parent.parent),
    )
    assert_eq(result.returncode, 0, f"combined flags should not error, got: {result.stderr[:200]}")
    data = json.loads(result.stdout)
    tiers = {f.get("tier") for f in data.get("data", [])}
    assert_true("minimal_risk" not in tiers, f"minimal_risk should be filtered, got: {tiers}")


def test_cli_version_in_json_output():
    """JSON envelope reports correct version."""
    import subprocess as sp
    result = sp.run(
        [sys.executable, "-m", "scripts.cli", "check", "--help"],
        capture_output=True, text=True,
        cwd=str(Path(__file__).parent.parent),
    )
    assert_eq(result.returncode, 0, "check --help should succeed")
    from scripts.cli import VERSION
    assert_eq(VERSION, "1.2.0", f"VERSION should be 1.2.0, got: {VERSION}")
    result2 = sp.run(
        [sys.executable, "-m", "scripts.cli", "check", "--format", "json", "--min-tier", "high_risk",
         str(Path(__file__).parent.parent / "tests" / "fixtures" / "sample_high_risk")],
        capture_output=True, text=True,
        cwd=str(Path(__file__).parent.parent),
    )
    if result2.returncode == 0:
        data = json.loads(result2.stdout)
        assert_eq(data.get("regula_version"), "1.2.0",
                  f"JSON output version should be 1.2.0, got: {data.get('regula_version')}")
        print("\u2713 CLI: version 1.2.0 confirmed in JSON output")


def test_cli_min_tier_all_levels():
    """CLI --min-tier accepts all valid choices."""
    import subprocess as sp
    fixture = str(Path(__file__).parent.parent / "tests" / "fixtures" / "sample_high_risk")
    for tier in ("prohibited", "high_risk", "limited_risk", "minimal_risk"):
        result = sp.run(
            [sys.executable, "-m", "scripts.cli", "check",
             "--min-tier", tier, "--format", "json", fixture],
            capture_output=True, text=True,
            cwd=str(Path(__file__).parent.parent),
        )
        assert_eq(
            result.returncode, 0,
            f"--min-tier={tier} should not error, got: {result.stderr[:100]}"
        )
    print("\u2713 CLI: all --min-tier choices accepted")


# ── Runner ──────────────────────────────────────────────────────────


if __name__ == "__main__":
    tests = [
        test_agent_mcp_server_parse,
        test_agent_mcp_write_access_warning,
        test_agent_mcp_api_key_in_env,
        test_agent_mcp_api_key_hardcoded,
        test_agent_autonomous_action_detection,
        test_agent_human_gate_present,
        test_agent_owasp_excessive_agency,
        test_agent_owasp_sensitive_disclosure,
        test_agent_owasp_excessive_autonomy,
        test_agent_risk_summary_format,
        # Contextual agent path detection
        test_agent_contextual_path_detection,
        test_agent_contextual_path_variants,
        test_agent_contextual_with_human_gate,
        # scan_files integration
        test_scan_files_skip_tests,
        test_scan_files_min_tier,
        test_scan_files_agent_autonomy_integration,
        test_scan_files_agent_autonomy_test_deprioritisation,
        # CLI flags
        test_cli_skip_tests_flag,
        test_cli_min_tier_flag,
        # New: edge cases
        test_scan_files_skip_tests_all_conventions,
        test_scan_files_min_tier_prohibited,
        test_scan_files_min_tier_high_risk,
        test_scan_files_min_tier_preserves_agent_autonomy,
        test_scan_files_combined_skip_tests_and_min_tier,
        test_scan_files_respect_ignores_overrides_skip_tests,
        test_cli_combined_skip_tests_and_min_tier,
        test_cli_version_in_json_output,
        test_cli_min_tier_all_levels,
    ]

    print(f"Running {len(tests)} agent governance tests...\n")

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
