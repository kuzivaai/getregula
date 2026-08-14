# regula-ignore
#!/usr/bin/env python3
"""
Regula MCP Server

Exposes Regula's compliance tools via the Model Context Protocol (MCP)
over stdio transport using JSON-RPC 2.0.

Run: python3 scripts/mcp_server.py
Or:  regula mcp-server

Claude Code config (~/.claude/settings.json):
  {
    "mcpServers": {
      "regula": {
        "command": "python3",
        "args": ["/path/to/getregula/scripts/mcp_server.py"]
      }
    }
  }
"""

# SECURITY NOTE: This server uses stdio transport only and has no
# authentication. This is standard for MCP stdio servers (the parent
# process controls access). Do NOT expose this server over TCP/HTTP
# without adding authentication first.

import json
import sys
from pathlib import Path
from typing import Any, Dict

sys.path.insert(0, str(Path(__file__).parent))

# Directories that must not be scanned.  Two categories:
#   _BLOCKED_EXACT  — block the directory itself but NOT user subdirectories
#                      (e.g. /home is blocked, /home/user/project is allowed)
#   _BLOCKED_PREFIXES — block the directory AND all children
#                      (e.g. /proc, /sys — nothing useful for code scanning)
_BLOCKED_EXACT = {Path(p) for p in ("/", "/home", "/root")}
_BLOCKED_PREFIXES = [
    Path(p) for p in (
        "/etc", "/usr", "/var", "/bin", "/sbin", "/tmp",
        "/proc", "/sys", "/dev", "/boot",
    )
]

from constants import VERSION
from decision_kernel import DecisionInputError

PROTOCOL_VERSION = "2024-11-05"
SERVER_INFO = {"name": "regula", "version": VERSION}

TOOLS = [
    {
        "name": "regula_check",
        "description": (
            "Scan a project directory for code indicators relevant to EU AI Act review. "
            "Detects prohibited practices (Article 5), high-risk patterns (Annex III), "
            "limited-risk systems (Article 50), credential exposure, and agent autonomy signals. "
            "Returns detector observations separately from an evidence-aware legal decision."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Absolute or relative path to the project directory to scan. Defaults to current directory.",
                },
                "min_tier": {
                    "type": "string",
                    "enum": ["minimal_risk", "limited_risk", "high_risk", "prohibited"],
                    "description": "Only return findings at or above this risk tier.",
                },
                "skip_tests": {
                    "type": "boolean",
                    "description": "Exclude test files from findings.",
                },
                "decision_request": {
                    "type": "object",
                    "description": "Canonical versioned fact request for the decision kernel.",
                },
            },
            "required": [],
        },
    },
    {
        "name": "regula_classify",
        "description": (
            "Return a provisional, pattern-based risk indication for code or text; "
            "this is not a legal classification of an AI system. "
            "Returns detector observations separately from an evidence-aware legal decision."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "input": {
                    "type": "string",
                    "description": "Code snippet or description to classify.",
                },
                "decision_request": {
                    "type": "object",
                    "description": "Canonical versioned fact request for the decision kernel.",
                },
            },
            "required": ["input"],
        },
    },
    {
        "name": "regula_gap",
        "description": (
            "Assess the presence of project evidence relevant to Articles 9-15 of the EU AI Act. "
            "Returns observed evidence only for duties resolved by the decision kernel. "
            "Article 9: Risk Management, 10: Data Governance, 11: Technical Docs, "
            "12: Record-Keeping, 13: Transparency, 14: Human Oversight, 15: Accuracy/Security."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Absolute or relative path to the project directory.",
                },
                "article": {
                    "type": "integer",
                    "minimum": 9,
                    "maximum": 15,
                    "description": "Specific article to assess (9-15). If omitted, assesses all.",
                },
                "decision_request": {
                    "type": "object",
                    "description": "Canonical versioned fact request for the decision kernel.",
                },
            },
            "required": [],
        },
    },
]


def _validate_scan_path(path: str) -> str | None:
    """Return an error string if `path` must not be scanned, else None.

    Shared by every MCP tool that accepts a caller-supplied path. Arguments
    reach these tools from an MCP client, so they are model-driven and
    prompt-influenceable; each entry point must apply the same denylist.
    regula_gap previously applied none of this while regula_check applied all
    of it, so the weaker tool set the real security boundary.
    """
    from pathlib import Path as _Path

    # Validate path — prevent unbounded filesystem scans
    resolved = _Path(path).resolve()
    if not resolved.is_dir() and not resolved.is_file():
        return f"Error: path does not exist: {path}"
    # Block scanning system directories.
    # Exact-match: /, /home, /root — these are too broad, but user projects
    # UNDER them (e.g. /home/user/project) are allowed.
    # Prefix-match: /etc, /proc, /sys, etc. — nothing scannable lives here.
    # nosec B108 — this is a denylist of paths we refuse to scan, not a path
    # used for writing.
    if resolved in _BLOCKED_EXACT:
        return f"Error: scanning {resolved} is not permitted — specify a project directory."
    for bp in _BLOCKED_PREFIXES:
        if resolved == bp or resolved.is_relative_to(bp):
            return f"Error: scanning {resolved} is not permitted — specify a project directory."
    return None


def _call_regula_check(arguments: dict) -> str:
    """Invoke regula check and return text output."""
    from decision_adapters import detector_findings, empty_decision, evaluate_payload
    from report import scan_files

    path = arguments.get("path", ".")
    skip_tests = arguments.get("skip_tests", False)
    min_tier = arguments.get("min_tier", "")

    err = _validate_scan_path(path)
    if err:
        return err

    try:
        findings = scan_files(path, skip_tests=skip_tests, min_tier=min_tier)
    except Exception as e:
        return f"Error scanning {path}: {e}"

    request = arguments.get("decision_request")
    decision = evaluate_payload(request) if request is not None else empty_decision(
        "eu", "mcp:regula_check"
    )
    return {"detector_findings": detector_findings(findings), "decision": decision}


def _call_regula_classify(arguments: dict) -> str:
    """Invoke regula classify and return text output."""
    from classify_risk import classify
    from decision_adapters import detector_finding, empty_decision, evaluate_payload

    text = arguments.get("input", "")
    if not text:
        return "Error: 'input' is required"

    result = classify(text)
    request = arguments.get("decision_request")
    decision = evaluate_payload(request) if request is not None else empty_decision(
        "eu", "mcp:regula_classify"
    )
    return {
        "detector_observation": detector_finding(result.to_dict()),
        "decision": decision,
    }


def _call_regula_gap(arguments: dict) -> str:
    """Invoke regula gap assessment and return text output.

    This previously imported `check_compliance`, which does not exist in
    compliance_check (the function is `assess_compliance`), so every call
    raised ImportError before reaching any logic. The rendering loop was also
    written against a flat {article: data} mapping; the real return nests the
    articles under an "articles" key and stores `score` as a string.
    """
    from compliance_check import assess_compliance
    from decision_adapters import empty_decision, evaluate_payload, resolved_gap_evidence

    path = arguments.get("path", ".")
    article = arguments.get("article")

    err = _validate_scan_path(path)
    if err:
        return err

    articles_filter = [str(article)] if article is not None else None
    try:
        assessment = assess_compliance(path, articles=articles_filter)
    except Exception as e:
        return f"Error running gap assessment on {path}: {e}"

    request = arguments.get("decision_request")
    decision = evaluate_payload(request) if request is not None else empty_decision(
        "eu", "mcp:regula_gap"
    )
    return {"decision": decision, "evidence": resolved_gap_evidence(assessment, decision)}


def handle_request(request: Dict[str, Any]) -> Dict[str, Any]:
    """Process a single MCP JSON-RPC request and return a response dict."""
    req_id = request.get("id")
    method = request.get("method", "")
    params = request.get("params", {})

    def ok(result):
        return {"jsonrpc": "2.0", "id": req_id, "result": result}

    def err(code, message):
        return {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}

    if method == "initialize":
        return ok({
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {"tools": {}},
            "serverInfo": SERVER_INFO,
        })

    elif method == "notifications/initialized":
        return None  # No response for notifications

    elif method == "tools/list":
        return ok({"tools": TOOLS})

    elif method == "tools/call":
        name = params.get("name", "")
        arguments = params.get("arguments", {})

        try:
            if name == "regula_check":
                text = _call_regula_check(arguments)
            elif name == "regula_classify":
                text = _call_regula_classify(arguments)
            elif name == "regula_gap":
                text = _call_regula_gap(arguments)
            else:
                return err(-32601, f"Unknown tool: {name}")
        except DecisionInputError as e:
            return err(-32602, str(e))
        except Exception as e:
            return err(-32603, f"Tool execution error: {e}")

        if isinstance(text, dict):
            return ok({
                "content": [{"type": "text", "text": json.dumps(text, sort_keys=True)}],
                "structuredContent": text,
            })
        # Contract: a tool function returns a dict on success and a str ONLY
        # for a tool-level error (invalid path, blocked path, scan failure,
        # missing input). Before 2026-08-14 that str flowed into an ordinary
        # success result, so an MCP client saw "Error scanning ..." as a
        # successful tool call. That is ledger finding N82's class surviving
        # on the string paths after the exception paths were fixed. Every
        # str return is now flagged per the MCP tool-result error form, so
        # no future string-returning error path can present as success.
        return ok({"content": [{"type": "text", "text": text}], "isError": True})

    elif method == "ping":
        return ok({})

    else:
        return err(-32601, f"Method not found: {method}")


def run_server():
    """Run the MCP server, reading JSON-RPC requests from stdin line by line."""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
        except json.JSONDecodeError as e:
            error_resp = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": f"Parse error: {e}"}
            }
            print(json.dumps(error_resp), flush=True)
            continue

        response = handle_request(request)
        if response is not None:  # Notifications have no response
            print(json.dumps(response), flush=True)


if __name__ == "__main__":
    run_server()
