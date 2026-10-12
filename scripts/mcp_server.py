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

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict

sys.path.insert(0, str(Path(__file__).parent))

# Directories that must not be scanned.  Two categories:
#   _BLOCKED_EXACT  — block the directory itself but NOT user subdirectories
#                      (e.g. /home is blocked, /home/USER/project is allowed)
#   _BLOCKED_PREFIXES — block the directory AND all children
#                      (e.g. /proc, /sys — nothing useful for code scanning)
_BLOCKED_EXACT = {Path(p) for p in ("/", "/home", "/root")}
_BLOCKED_PREFIXES = [
    Path(p) for p in (
        "/etc", "/usr", "/var", "/bin", "/sbin",
        # Denied scan prefix, not a temporary-file destination.
        "/tmp",  # nosec B108
        "/proc", "/sys", "/dev", "/boot",
    )
]

MAX_MCP_TEXT_CHARS = 1_048_576
MAX_MCP_REQUEST_BYTES = 2 * 1024 * 1024
MAX_MCP_FILES = 10_000
MAX_MCP_TOTAL_BYTES = 256 * 1024 * 1024

_SENSITIVE_NAMES = {
    ".env", ".env.local", ".env.production", ".env.development",
    "credentials.json", "secrets.json", "id_rsa", "id_ed25519",
}
_SENSITIVE_SUFFIXES = {".key", ".pem", ".p12", ".pfx"}
_SENSITIVE_DIRECTORIES = {".aws", ".ssh", ".gnupg"}
_WORKSPACE_ROOT: Path | None = None

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
            "Returns detector observations separately from a human-review record."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path within the explicitly authorised workspace. Defaults to the workspace root.",
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
            "Returns detector observations separately from a human-review record."
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
            "Returns code and documentation observations for human review. "
            "Article 9: Risk Management, 10: Data Governance, 11: Technical Docs, "
            "12: Record-Keeping, 13: Transparency, 14: Human Oversight, 15: Accuracy/Security."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path within the explicitly authorised workspace.",
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


def _is_sensitive_path(path: Path, root: Path) -> bool:
    """Return whether a workspace-relative path has a secret-bearing shape."""
    try:
        relative = path.relative_to(root)
    except ValueError:
        return True
    parts = {part.lower() for part in relative.parts}
    name = path.name.lower()
    return (
        bool(parts & _SENSITIVE_DIRECTORIES)
        or name in _SENSITIVE_NAMES
        or name.startswith(".env.")
        or path.suffix.lower() in _SENSITIVE_SUFFIXES
    )


def configure_workspace_root(path: str | Path) -> Path:
    """Set the one explicit filesystem capability used by MCP path tools."""
    global _WORKSPACE_ROOT
    if not isinstance(path, (str, Path)) or not str(path).strip():
        raise ValueError("MCP workspace root must be a non-empty path")
    resolved = Path(path).resolve()
    if not resolved.is_dir():
        raise ValueError("MCP workspace root must be an existing directory")
    broad_roots = _BLOCKED_EXACT | set(_BLOCKED_PREFIXES)
    if resolved in broad_roots:
        raise ValueError("MCP workspace root is too broad or is a system directory")
    _WORKSPACE_ROOT = resolved
    return resolved


def _resolve_workspace_target(path: object) -> Path:
    """Resolve a caller target inside the configured workspace capability."""
    if _WORKSPACE_ROOT is None:
        raise PermissionError(
            "MCP workspace root is not configured; start the server with "
            "--workspace-root PATH"
        )
    if not isinstance(path, str) or not path.strip() or "\x00" in path:
        raise ValueError("path must be a non-empty string")

    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = _WORKSPACE_ROOT / candidate
    lexical = Path(os.path.abspath(candidate))
    try:
        lexical.relative_to(_WORKSPACE_ROOT)
    except ValueError as exc:
        raise PermissionError(
            "target must be within the authorised MCP workspace root"
        ) from exc

    resolved = lexical.resolve()
    try:
        resolved.relative_to(_WORKSPACE_ROOT)
    except ValueError as exc:
        raise PermissionError(
            "target resolves outside the authorised MCP workspace root"
        ) from exc
    if not resolved.exists():
        raise ValueError("path does not exist inside the authorised workspace")
    if not resolved.is_dir() and not resolved.is_file():
        raise ValueError("path is not a regular file or directory")
    if _is_sensitive_path(resolved, _WORKSPACE_ROOT):
        raise PermissionError("direct access to a sensitive workspace path is not permitted")
    return resolved


def _enforce_work_budget(target: Path) -> str | None:
    """Return an error when a target exceeds bounded local MCP work limits."""
    from constants import SKIP_DIRS

    file_count = 0
    total_bytes = 0
    if target.is_file():
        try:
            total_bytes = target.stat().st_size
        except OSError as exc:
            return f"Error: target could not be measured: {exc}"
        if total_bytes > MAX_MCP_TOTAL_BYTES:
            return f"Error: target exceeds MCP work limit ({MAX_MCP_TOTAL_BYTES} bytes)"
        return None

    for root, dirs, files in os.walk(target, followlinks=False):
        root_path = Path(root)
        dirs[:] = [
            name for name in dirs
            if name not in SKIP_DIRS
            and name.lower() not in _SENSITIVE_DIRECTORIES
            and not (root_path / name).is_symlink()
        ]
        for name in files:
            candidate = root_path / name
            if candidate.is_symlink() or _is_sensitive_path(candidate, target):
                continue
            try:
                size = candidate.stat().st_size
            except OSError as exc:
                return f"Error: workspace work could not be measured: {exc}"
            file_count += 1
            total_bytes += size
            if file_count > MAX_MCP_FILES:
                return f"Error: workspace exceeds MCP file limit ({MAX_MCP_FILES})"
            if total_bytes > MAX_MCP_TOTAL_BYTES:
                return (
                    "Error: workspace exceeds MCP total-work limit "
                    f"({MAX_MCP_TOTAL_BYTES} bytes)"
                )
    return None


def _validate_scan_path(path: str) -> str | None:
    """Return an error string if `path` is outside MCP authority, else None.

    Shared by every MCP tool that accepts a caller-supplied path. Arguments
    reach these tools from an MCP client, so they are model-driven and
    prompt-influenceable; each entry point must apply the same capability.
    """
    try:
        target = _resolve_workspace_target(path)
    except (ValueError, PermissionError, OSError) as exc:
        return f"Error: {exc}"
    return _enforce_work_budget(target)


def _audit_mcp_call(name: str, arguments: dict, outcome: str, result: object) -> None:
    """Record bounded MCP call metadata without source or prompt contents."""
    try:
        from log_event import log_event
        data = {"surface": "mcp", "tool": name, "outcome": outcome}
        if name == "regula_classify":
            value = arguments.get("input")
            data["input_chars"] = len(value) if isinstance(value, str) else 0
        elif _WORKSPACE_ROOT is not None:
            raw_path = arguments.get("path", ".")
            try:
                target = _resolve_workspace_target(raw_path)
                data["workspace_target"] = str(target.relative_to(_WORKSPACE_ROOT)) or "."
            except Exception:
                data["workspace_target"] = "rejected"
        if isinstance(result, dict):
            observations = result.get("detector_findings")
            if isinstance(observations, list):
                data["observation_count"] = len(observations)
        log_event(
            "mcp_tool_call", data,
            project_path=str(_WORKSPACE_ROOT) if _WORKSPACE_ROOT is not None else None,
        )
    except Exception as exc:
        print(f"regula: MCP audit record failed: {exc}", file=sys.stderr)


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
    target = _resolve_workspace_target(path)

    try:
        findings = scan_files(
            str(target), skip_tests=skip_tests, min_tier=min_tier,
            include_config_files=False,
        )
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
    if not isinstance(text, str):
        return "Error: 'input' must be a string"
    if len(text) > MAX_MCP_TEXT_CHARS:
        return f"Error: 'input' too large (max {MAX_MCP_TEXT_CHARS} characters)"

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
    target = _resolve_workspace_target(path)

    articles_filter = [str(article)] if article is not None else None
    try:
        assessment = assess_compliance(
            str(target), articles=articles_filter, exclude_sensitive_paths=True)
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
            _audit_mcp_call(name, arguments, "invalid_request", str(e))
            return err(-32602, str(e))
        except Exception as e:
            _audit_mcp_call(name, arguments, "execution_error", str(e))
            return err(-32603, f"Tool execution error: {e}")

        if isinstance(text, dict):
            _audit_mcp_call(name, arguments, "success", text)
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
        _audit_mcp_call(name, arguments, "refused", text)
        return ok({"content": [{"type": "text", "text": text}], "isError": True})

    elif method == "ping":
        return ok({})

    else:
        return err(-32601, f"Method not found: {method}")


def run_server(workspace_root: str | Path):
    """Run the MCP server, reading JSON-RPC requests from stdin line by line."""
    configure_workspace_root(workspace_root)
    while True:
        line = sys.stdin.readline(MAX_MCP_REQUEST_BYTES + 1)
        if not line:
            break
        if len(line.encode("utf-8")) > MAX_MCP_REQUEST_BYTES:
            while line and not line.endswith("\n"):
                line = sys.stdin.readline(MAX_MCP_REQUEST_BYTES + 1)
            print(json.dumps({
                "jsonrpc": "2.0", "id": None,
                "error": {"code": -32600, "message": "Request exceeds MCP size limit"},
            }), flush=True)
            continue
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
    parser = argparse.ArgumentParser(description="Regula MCP stdio server")
    parser.add_argument(
        "--workspace-root", required=True,
        help="Explicit directory that MCP path tools are authorised to read",
    )
    cli_args = parser.parse_args()
    run_server(cli_args.workspace_root)
