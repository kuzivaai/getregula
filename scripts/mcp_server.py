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
import os
import tempfile
from pathlib import Path
from typing import Any, Dict

sys.path.insert(0, str(Path(__file__).parent))

PROTOCOL_VERSION = "2024-11-05"
SERVER_INFO = {"name": "regula", "version": "1.2.0"}

TOOLS = [
    {
        "name": "regula_check",
        "description": (
            "Scan a project directory for EU AI Act compliance issues. "
            "Detects prohibited practices (Article 5), high-risk patterns (Annex III), "
            "limited-risk systems (Article 50), credential exposure, and agent autonomy signals. "
            "Returns findings with tier (BLOCK/WARN/INFO), confidence, and remediation guidance."
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
            },
            "required": [],
        },
    },
    {
        "name": "regula_classify",
        "description": (
            "Classify a code snippet or text against EU AI Act risk tiers. "
            "Returns: PROHIBITED (Article 5), HIGH-RISK (Annex III), LIMITED-RISK (Article 50), "
            "or MINIMAL-RISK, with confidence score and applicable articles."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "input": {
                    "type": "string",
                    "description": "Code snippet or description to classify.",
                }
            },
            "required": ["input"],
        },
    },
    {
        "name": "regula_gap",
        "description": (
            "Assess compliance gaps for Articles 9-15 of the EU AI Act against a project directory. "
            "Returns a score (0-100) per article with evidence and gaps. "
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
            },
            "required": [],
        },
    },
]


def _call_regula_check(arguments: dict) -> str:
    """Invoke regula check and return text output."""
    from report import scan_files

    path = arguments.get("path", ".")
    skip_tests = arguments.get("skip_tests", False)
    min_tier = arguments.get("min_tier", "")

    try:
        findings = scan_files(path, skip_tests=skip_tests, min_tier=min_tier)
    except Exception as e:
        return f"Error scanning {path}: {e}"

    if not findings:
        return f"No findings for {path} — no AI indicators detected above {min_tier or 'minimal_risk'} tier."

    lines = [f"Regula scan: {path}", f"Found {len(findings)} finding(s)\n"]
    for f in findings:
        tier = f.get("tier", "unknown").upper()
        conf = f.get("confidence", 0)
        file_ = f.get("file", "")
        line_ = f.get("line", "")
        desc = f.get("description", "")
        lines.append(f"[{tier}] {conf}% {file_}:{line_} — {desc}")
        if f.get("remediation"):
            lines.append(f"  Fix: {f['remediation']}")
    return "\n".join(lines)


def _call_regula_classify(arguments: dict) -> str:
    """Invoke regula classify and return text output."""
    from classify_risk import classify

    text = arguments.get("input", "")
    if not text:
        return "Error: 'input' is required"

    result = classify(text)
    tier = result.tier.value if hasattr(result.tier, "value") else str(result.tier)
    parts = [
        f"Tier: {tier.upper()}",
        f"Confidence: {result.confidence}%",
    ]
    if result.applicable_articles:
        parts.append(f"Articles: {', '.join(result.applicable_articles)}")
    if result.description:
        parts.append(f"Description: {result.description}")
    if result.indicators_matched:
        parts.append(f"Indicators: {', '.join(result.indicators_matched[:3])}")
    return "\n".join(parts)


def _call_regula_gap(arguments: dict) -> str:
    """Invoke regula gap assessment and return text output."""
    from compliance_check import check_compliance

    path = arguments.get("path", ".")
    article = arguments.get("article")

    try:
        results = check_compliance(path)
    except Exception as e:
        return f"Error running gap assessment on {path}: {e}"

    lines = [f"Compliance gap assessment: {path}\n"]
    for art_num, art_data in sorted(results.items()):
        if article and int(art_num.replace("article_", "").replace("art", "")) != article:
            continue
        score = art_data.get("score", 0)
        name = art_data.get("name", art_num)
        status = "STRONG" if score >= 80 else "ADEQUATE" if score >= 50 else "WEAK"
        lines.append(f"Article {art_num}  {name:<30} [{score:3d}%] {status}")
        for gap in art_data.get("gaps", [])[:2]:
            lines.append(f"  Gap: {gap}")
    return "\n".join(lines)


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
        except Exception as e:
            return err(-32603, f"Tool execution error: {e}")

        return ok({"content": [{"type": "text", "text": text}]})

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
