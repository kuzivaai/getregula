# regula-ignore
#!/usr/bin/env python3
"""MCP server protocol tests for Regula JSON-RPC 2.0 interface."""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from mcp_server import handle_request, SERVER_INFO, PROTOCOL_VERSION
import mcp_server as _mcp_server

import helpers
from helpers import assert_eq, assert_true, assert_in


def _authorise_fixture_workspace():
    return _mcp_server.configure_workspace_root(Path(__file__).parent / "fixtures")


# ── Initialize ─────────────────────────────────────────────────────

def test_mcp_initialize_response():
    """initialize returns server info and capabilities."""
    resp = handle_request({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
    assert_eq(resp["jsonrpc"], "2.0", "jsonrpc version")
    assert_eq(resp["id"], 1, "response id matches request id")
    result = resp["result"]
    assert_eq(result["protocolVersion"], PROTOCOL_VERSION, "protocol version")
    assert_eq(result["serverInfo"], SERVER_INFO, "server info")
    assert_true("tools" in result["capabilities"], "capabilities includes tools")


# ── Tools List ─────────────────────────────────────────────────────

def test_mcp_tools_list():
    """tools/list returns available tools including regula_check and regula_classify."""
    resp = handle_request({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
    assert_eq(resp["id"], 2, "response id")
    tools = resp["result"]["tools"]
    tool_names = [t["name"] for t in tools]
    assert_in("regula_check", tool_names, "regula_check in tools")
    assert_in("regula_classify", tool_names, "regula_classify in tools")
    assert_in("regula_gap", tool_names, "regula_gap in tools")
    # Each tool must have inputSchema
    for t in tools:
        assert_true("inputSchema" in t, f"{t['name']} has inputSchema")


# ── Classify Tool ──────────────────────────────────────────────────

def test_mcp_regula_classify():
    """Classify separates detector output from the kernel decision."""
    resp = handle_request({
        "jsonrpc": "2.0", "id": 3, "method": "tools/call",
        "params": {
            "name": "regula_classify",
            "arguments": {"input": "social scoring system that evaluates citizens"},
        },
    })
    assert_eq(resp["id"], 3, "response id")
    result = resp["result"]
    content = result["content"]
    assert_true(len(content) > 0, "content is non-empty")
    assert_eq(content[0]["type"], "text", "content type is text")
    structured = result["structuredContent"]
    assert_eq(structured["decision"]["review_status"], "insufficient_information",
              "undeclared legal facts remain unresolved")
    assert_true(structured["decision"]["human_decision"] is None,
                "human decision remains empty")
    observation = structured["detector_observation"]
    assert_true("detector_class" in observation, "detector class is explicit")
    assert_true("tier" not in observation, "no legal-looking tier is emitted")
    assert_true("confidence" not in observation, "no decision confidence is emitted")


# ── Check Tool ─────────────────────────────────────────────────────

def test_mcp_regula_check():
    """tools/call with regula_check scans a fixture directory."""
    _authorise_fixture_workspace()
    fixture_path = str(Path(__file__).parent / "fixtures" / "sample_prohibited")
    resp = handle_request({
        "jsonrpc": "2.0", "id": 4, "method": "tools/call",
        "params": {
            "name": "regula_check",
            "arguments": {"path": fixture_path},
        },
    })
    assert_eq(resp["id"], 4, "response id")
    result = resp["result"]
    structured = result["structuredContent"]
    assert_true(bool(structured["detector_findings"]), "fixture produces detector findings")
    assert_eq(structured["decision"]["review_status"], "insufficient_information",
              "scan patterns do not become legal facts")
    assert_true(structured["decision"]["human_decision"] is None,
                "scan does not manufacture a human decision")


# ── Gap Tool ───────────────────────────────────────────────────────

def test_mcp_regula_gap_returns_assessment():
    """tools/call with regula_gap renders an assessment, not an error.

    Regression guard: regula_gap imported a function that does not exist
    (check_compliance; the real name is assess_compliance), so every call
    failed before reaching any logic, and nothing executed this path.
    """
    _authorise_fixture_workspace()
    fixture_path = str(Path(__file__).parent / "fixtures" / "sample_high_risk")
    resp = handle_request({
        "jsonrpc": "2.0", "id": 7, "method": "tools/call",
        "params": {"name": "regula_gap", "arguments": {"path": fixture_path}},
    })
    assert_eq(resp["id"], 7, "response id")
    assert_true("result" in resp, "gap call returns a result, not a JSON-RPC error")
    structured = resp["result"]["structuredContent"]
    assert_eq(structured["decision"]["review_status"], "insufficient_information",
              "gap scan does not decide applicability")
    assert_true(bool(structured["evidence"]["held_article_observations"]),
                "review evidence is preserved while applicability remains unresolved")
    assert_true(not structured["evidence"]["article_observations"],
                "held observations are not presented as emitted duties")
    assert_true("do not establish applicability" in structured["evidence"]["note"],
                "evidence carries the non-determination boundary")


def test_mcp_regula_gap_blocked_path_refused():
    """regula_gap applies the same path denylist as regula_check.

    Regression guard: the gap tool previously applied none of the path
    validation, so the weakest tool set the real security boundary.
    Strengthened 2026-08-14: the refusal must also carry isError, because a
    refusal presented as a successful result is ledger finding N82's class.
    """
    _authorise_fixture_workspace()
    resp = handle_request({
        "jsonrpc": "2.0", "id": 8, "method": "tools/call",
        "params": {"name": "regula_gap", "arguments": {"path": "/etc"}},
    })
    assert_true("result" in resp, "refusal is a tool result, not a protocol error")
    text = resp["result"]["content"][0]["text"]
    assert_in("workspace", text.lower(), "outside path is refused")
    assert_true(resp["result"].get("isError") is True,
                "refusal is flagged as a tool error, not presented as success")


# ── Tool-level error semantics (N82 class closure, 2026-08-14) ─────
#
# Every string-returning error path in the three tool functions must surface
# as an MCP tool-result error (isError: true), never as an ordinary success.
# One test per string-return site in scripts/mcp_server.py, plus a control
# proving success results carry no error flag.

def test_mcp_nonexistent_path_is_tool_error():
    """regula_check on a path that does not exist is a flagged tool error."""
    workspace = _authorise_fixture_workspace()
    resp = handle_request({
        "jsonrpc": "2.0", "id": 20, "method": "tools/call",
        "params": {"name": "regula_check",
                   "arguments": {"path": str(workspace / "definitely-not-here")}},
    })
    result = resp["result"]
    assert_in("does not exist", result["content"][0]["text"], "error names the cause")
    assert_true(result.get("isError") is True, "missing path is a flagged tool error")
    assert_true("structuredContent" not in result,
                "an error result carries no structured success payload")


def test_mcp_blocked_path_is_tool_error():
    """regula_check on a denylisted path is a flagged tool error."""
    _authorise_fixture_workspace()
    resp = handle_request({
        "jsonrpc": "2.0", "id": 21, "method": "tools/call",
        "params": {"name": "regula_check", "arguments": {"path": "/etc"}},
    })
    result = resp["result"]
    assert_in("workspace", result["content"][0]["text"].lower(),
              "refusal names the authority boundary")
    assert_true(result.get("isError") is True, "blocked path is a flagged tool error")


def test_mcp_classify_empty_input_is_tool_error():
    """regula_classify with an empty input is a flagged tool error."""
    resp = handle_request({
        "jsonrpc": "2.0", "id": 22, "method": "tools/call",
        "params": {"name": "regula_classify", "arguments": {"input": ""}},
    })
    result = resp["result"]
    assert_in("required", result["content"][0]["text"], "error names the missing argument")
    assert_true(result.get("isError") is True, "missing input is a flagged tool error")


def test_mcp_scan_exception_is_tool_error():
    """A scanner failure inside regula_check is a flagged tool error.

    The tool function catches the exception and returns an error string;
    before 2026-08-14 that string presented as a successful scan result.
    """
    from unittest.mock import patch

    _authorise_fixture_workspace()
    fixture_path = str(Path(__file__).parent / "fixtures" / "sample_prohibited")
    with patch("report.scan_files", side_effect=RuntimeError("planted scan failure")):
        resp = handle_request({
            "jsonrpc": "2.0", "id": 23, "method": "tools/call",
            "params": {"name": "regula_check", "arguments": {"path": fixture_path}},
        })
    result = resp["result"]
    assert_in("Error scanning", result["content"][0]["text"], "error names the operation")
    assert_in("planted scan failure", result["content"][0]["text"], "error carries the cause")
    assert_true(result.get("isError") is True, "scan failure is a flagged tool error")


def test_mcp_gap_exception_is_tool_error():
    """An assessment failure inside regula_gap is a flagged tool error."""
    from unittest.mock import patch

    _authorise_fixture_workspace()
    fixture_path = str(Path(__file__).parent / "fixtures" / "sample_high_risk")
    with patch("compliance_check.assess_compliance",
               side_effect=RuntimeError("planted gap failure")):
        resp = handle_request({
            "jsonrpc": "2.0", "id": 24, "method": "tools/call",
            "params": {"name": "regula_gap", "arguments": {"path": fixture_path}},
        })
    result = resp["result"]
    assert_in("Error running gap assessment", result["content"][0]["text"],
              "error names the operation")
    assert_true(result.get("isError") is True, "gap failure is a flagged tool error")


def test_mcp_success_results_carry_no_error_flag():
    """The control in the other direction: a successful call is not flagged.

    Without this, an implementation that flags every result would pass the
    error-path tests while breaking every success, which is the vacuity
    shape measurement rule 4 exists to catch.
    """
    resp = handle_request({
        "jsonrpc": "2.0", "id": 25, "method": "tools/call",
        "params": {"name": "regula_classify",
                   "arguments": {"input": "social scoring system"}},
    })
    result = resp["result"]
    assert_true("structuredContent" in result, "success carries the structured payload")
    assert_true("isError" not in result, "success is not flagged as an error")


# ── Explicit workspace and bounded authority ───────────────────────

def test_mcp_path_tools_require_an_explicit_workspace_root(monkeypatch):
    fixture_path = str(Path(__file__).parent / "fixtures" / "sample_prohibited")
    monkeypatch.setattr(_mcp_server, "_WORKSPACE_ROOT", None, raising=False)
    resp = handle_request({
        "jsonrpc": "2.0", "id": 30, "method": "tools/call",
        "params": {"name": "regula_check", "arguments": {"path": fixture_path}},
    })
    result = resp["result"]
    assert_true(result.get("isError") is True,
                "path tool without an authorised root is refused")
    assert_in("workspace root", result["content"][0]["text"].lower(),
              "refusal names the missing authority")


def test_mcp_rejects_existing_target_outside_workspace(monkeypatch, tmp_path):
    workspace = tmp_path / "workspace"
    outside = tmp_path / "outside"
    workspace.mkdir()
    outside.mkdir()
    (outside / "app.py").write_text("import openai\n", encoding="utf-8")
    monkeypatch.setattr(_mcp_server, "_WORKSPACE_ROOT", workspace.resolve(),
                        raising=False)
    resp = handle_request({
        "jsonrpc": "2.0", "id": 31, "method": "tools/call",
        "params": {"name": "regula_check", "arguments": {"path": str(outside)}},
    })
    assert_true(resp["result"].get("isError") is True,
                "existing out-of-workspace target is refused")
    assert_in("workspace", resp["result"]["content"][0]["text"].lower(),
              "containment error does not rely on a system-root denylist")


def test_mcp_rejects_symlink_escape_from_workspace(monkeypatch, tmp_path):
    workspace = tmp_path / "workspace"
    outside = tmp_path / "outside"
    workspace.mkdir()
    outside.mkdir()
    link = workspace / "linked"
    try:
        link.symlink_to(outside, target_is_directory=True)
    except OSError:
        return
    monkeypatch.setattr(_mcp_server, "_WORKSPACE_ROOT", workspace.resolve(),
                        raising=False)
    resp = handle_request({
        "jsonrpc": "2.0", "id": 32, "method": "tools/call",
        "params": {"name": "regula_gap", "arguments": {"path": str(link)}},
    })
    assert_true(resp["result"].get("isError") is True,
                "symlink escape is refused")


def test_mcp_rejects_direct_secret_path(monkeypatch, tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    secret = workspace / ".env"
    secret.write_text("SECRET_SHAPE_FOR_TEST=redacted\n", encoding="utf-8")
    monkeypatch.setattr(_mcp_server, "_WORKSPACE_ROOT", workspace.resolve(),
                        raising=False)
    resp = handle_request({
        "jsonrpc": "2.0", "id": 33, "method": "tools/call",
        "params": {"name": "regula_check", "arguments": {"path": str(secret)}},
    })
    assert_true(resp["result"].get("isError") is True,
                "direct secret target is refused before reading")
    assert_in("sensitive", resp["result"]["content"][0]["text"].lower(),
              "refusal explains the secret-path boundary")


def test_mcp_classify_enforces_rest_equivalent_text_limit(monkeypatch):
    from unittest.mock import patch

    oversized = "x" * (1_048_576 + 1)
    with patch("classify_risk.classify",
               side_effect=AssertionError("oversized text reached classifier")):
        resp = handle_request({
            "jsonrpc": "2.0", "id": 34, "method": "tools/call",
            "params": {"name": "regula_classify",
                       "arguments": {"input": oversized}},
        })
    assert_true(resp["result"].get("isError") is True,
                "oversized text is a tool-level refusal")
    assert_in("too large", resp["result"]["content"][0]["text"].lower(),
              "text-size refusal names the limit")


def test_mcp_explicit_workspace_can_be_under_tmp(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    configured = _mcp_server.configure_workspace_root(workspace)
    assert_eq(configured, workspace.resolve(),
              "an explicit project capability may be beneath a temporary root")


def test_mcp_rejects_broad_workspace_root():
    try:
        _mcp_server.configure_workspace_root("/")
    except ValueError as exc:
        assert_in("too broad", str(exc), "broad-root refusal names the problem")
    else:
        raise AssertionError("filesystem root was accepted as an MCP workspace")


def test_mcp_check_disables_config_file_scan(monkeypatch, tmp_path):
    from unittest.mock import patch

    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "app.py").write_text("print('bounded')\n", encoding="utf-8")
    _mcp_server.configure_workspace_root(workspace)
    with patch("report.scan_files", return_value=[]) as scanner:
        response = handle_request({
            "jsonrpc": "2.0", "id": 35, "method": "tools/call",
            "params": {"name": "regula_check", "arguments": {"path": "."}},
        })
    assert_true("structuredContent" in response["result"], "bounded scan succeeds")
    assert_true(scanner.call_args.kwargs["include_config_files"] is False,
                "MCP does not activate the config-file scanner")


def test_mcp_gap_excludes_sensitive_paths(monkeypatch, tmp_path):
    from unittest.mock import patch

    workspace = tmp_path / "workspace"
    workspace.mkdir()
    _mcp_server.configure_workspace_root(workspace)
    assessment = {"articles": {}, "highest_risk": "not_ai"}
    with patch("compliance_check.assess_compliance", return_value=assessment) as checker:
        handle_request({
            "jsonrpc": "2.0", "id": 36, "method": "tools/call",
            "params": {"name": "regula_gap", "arguments": {"path": "."}},
        })
    assert_true(checker.call_args.kwargs["exclude_sensitive_paths"] is True,
                "MCP gap assessment excludes secret-shaped paths")


def test_mcp_file_count_budget_refuses_before_scan(monkeypatch, tmp_path):
    from unittest.mock import patch

    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "one.py").write_text("print(1)\n", encoding="utf-8")
    (workspace / "two.py").write_text("print(2)\n", encoding="utf-8")
    _mcp_server.configure_workspace_root(workspace)
    monkeypatch.setattr(_mcp_server, "MAX_MCP_FILES", 1)
    with patch("report.scan_files",
               side_effect=AssertionError("over-budget workspace reached scanner")):
        response = handle_request({
            "jsonrpc": "2.0", "id": 37, "method": "tools/call",
            "params": {"name": "regula_check", "arguments": {"path": "."}},
        })
    result = response["result"]
    assert_true(result.get("isError") is True, "over-budget workspace is refused")
    assert_in("file limit", result["content"][0]["text"].lower(),
              "refusal identifies the bounded-work limit")


def test_mcp_audit_record_does_not_log_classify_source(monkeypatch):
    from unittest.mock import patch

    planted_source = "private source content for negative control"
    with patch("log_event.log_event") as audit:
        handle_request({
            "jsonrpc": "2.0", "id": 38, "method": "tools/call",
            "params": {"name": "regula_classify",
                       "arguments": {"input": planted_source}},
        })
    logged = audit.call_args.args[1]
    assert_eq(logged["input_chars"], len(planted_source),
              "audit preserves bounded work metadata")
    assert_true(planted_source not in str(audit.call_args),
                "audit record does not contain source input")


# ── Unknown Method ─────────────────────────────────────────────────

def test_mcp_unknown_method():
    """Unknown method returns JSON-RPC error."""
    resp = handle_request({"jsonrpc": "2.0", "id": 5, "method": "nonexistent/method", "params": {}})
    assert_eq(resp["id"], 5, "response id")
    assert_true("error" in resp, "response contains error")
    assert_eq(resp["error"]["code"], -32601, "error code is method not found")
    assert_in("Method not found", resp["error"]["message"], "error message")


# ── Unknown Tool ───────────────────────────────────────────────────

def test_mcp_unknown_tool():
    """Unknown tool name returns JSON-RPC error."""
    resp = handle_request({
        "jsonrpc": "2.0", "id": 6, "method": "tools/call",
        "params": {"name": "nonexistent_tool", "arguments": {}},
    })
    assert_eq(resp["id"], 6, "response id")
    assert_true("error" in resp, "response contains error")
    assert_eq(resp["error"]["code"], -32601, "error code for unknown tool")
    assert_in("Unknown tool", resp["error"]["message"], "error message mentions unknown tool")


# ── Runner ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    tests = [
        test_mcp_initialize_response,
        test_mcp_tools_list,
        test_mcp_regula_classify,
        test_mcp_regula_check,
        test_mcp_regula_gap_returns_assessment,
        test_mcp_regula_gap_blocked_path_refused,
        test_mcp_unknown_method,
        test_mcp_unknown_tool,
        test_mcp_nonexistent_path_is_tool_error,
        test_mcp_blocked_path_is_tool_error,
        test_mcp_classify_empty_input_is_tool_error,
        test_mcp_scan_exception_is_tool_error,
        test_mcp_gap_exception_is_tool_error,
        test_mcp_success_results_carry_no_error_flag,
    ]
    print("MCP Server Protocol Tests")
    print("=" * 40)
    for t in tests:
        name = t.__name__
        try:
            t()
            print(f"  PASS: {name}")
        except Exception as e:
            helpers.failed += 1
            print(f"  ERROR: {name} — {e}")
    print("=" * 40)
    print(f"Results: {helpers.passed} passed, {helpers.failed} failed")
    sys.exit(1 if helpers.failed else 0)
