# regula-ignore
#!/usr/bin/env python3
"""MCP server protocol tests for Regula JSON-RPC 2.0 interface."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from mcp_server import handle_request, TOOLS, SERVER_INFO, PROTOCOL_VERSION

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


def assert_in(needle, haystack, msg=""):
    global passed, failed
    if needle in haystack:
        passed += 1
    else:
        failed += 1
        if _PYTEST_MODE:
            raise AssertionError(f"{msg} — {needle!r} not found in {haystack!r}")
        print(f"  FAIL: {msg} — {needle!r} not found in {haystack!r}")


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
    """tools/call with regula_classify returns a classification result."""
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
    text = content[0]["text"]
    assert_in("Tier:", text, "output contains Tier")
    assert_in("Confidence:", text, "output contains Confidence")


# ── Check Tool ─────────────────────────────────────────────────────

def test_mcp_regula_check():
    """tools/call with regula_check scans a fixture directory."""
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
    text = result["content"][0]["text"]
    # sample_prohibited fixture should produce findings
    assert_true(len(text) > 0, "check output is non-empty")
    assert_in("Regula scan:", text, "output contains scan header")


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
        test_mcp_unknown_method,
        test_mcp_unknown_tool,
    ]
    print("MCP Server Protocol Tests")
    print("=" * 40)
    for t in tests:
        name = t.__name__
        try:
            t()
            print(f"  PASS: {name}")
        except Exception as e:
            failed += 1
            print(f"  ERROR: {name} — {e}")
    print("=" * 40)
    print(f"Results: {passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)
