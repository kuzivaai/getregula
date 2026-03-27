#!/usr/bin/env python3
"""
Regula Agent Monitor — Agentic AI Governance

Monitors AI agent behaviour for EU AI Act compliance:
- Tracks tool-call frequency and patterns
- Detects sensitive resource access
- Scores agent autonomy level
- Flags agent sessions without human checkpoints

Based on: Partnership on AI 2026 priorities, Gartner forecast (40% of
enterprise apps will embed autonomous agents by end of 2026), GitGuardian
finding of 24,008 secrets in MCP configuration files.
"""

import json
import os
import re
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).parent))

from log_event import query_events, log_event


# Sensitive resource patterns that agents should not access without oversight
SENSITIVE_RESOURCE_PATTERNS = {
    "database_write": [r"INSERT\s+INTO", r"UPDATE\s+.*SET", r"DELETE\s+FROM", r"DROP\s+TABLE",
                       r"\.save\(\)", r"\.create\(\)", r"\.update\(\)", r"\.delete\(\)"],
    "file_system_write": [r"write_text\(", r"write_bytes\(", r"open\(.+['\"]w", r"shutil\.rmtree",
                          r"os\.remove", r"pathlib.*unlink"],
    "network_request": [r"requests\.(post|put|patch|delete)", r"urllib\.request\.urlopen",
                        r"fetch\(", r"axios\.(post|put|patch|delete)"],
    "credential_access": [r"os\.environ\[", r"getenv\(", r"\.env", r"secrets\.",
                          r"keyring\.", r"vault\."],
    "system_command": [r"subprocess\.(run|call|Popen)", r"os\.system\(", r"exec\(", r"eval\("],
}


def analyse_agent_session(session_id: str = None, hours: int = 8) -> dict:
    """Analyse an agent session for governance metrics.

    Returns:
        {
            "session_id": str,
            "time_range": str,
            "total_tool_calls": int,
            "tool_call_rate": float,  # calls per minute
            "sensitive_access": [
                {"type": str, "count": int, "examples": [str]}
            ],
            "autonomy_score": int,  # 0-100 (0=fully supervised, 100=fully autonomous)
            "human_checkpoints": int,
            "risk_level": str,  # "low", "moderate", "high", "critical"
            "recommendations": [str],
        }
    """
    after = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
    events = query_events(after=after, limit=50000)

    if session_id:
        events = [e for e in events if e.get("session_id") == session_id]

    if not events:
        return {
            "session_id": session_id or "aggregate",
            "time_range": f"last {hours} hours",
            "total_tool_calls": 0,
            "tool_call_rate": 0.0,
            "sensitive_access": [],
            "autonomy_score": 0,
            "human_checkpoints": 0,
            "risk_level": "none",
            "recommendations": [],
        }

    # Count tool calls
    tool_calls = [e for e in events if e.get("event_type") in ("tool_use", "classification", "blocked")]
    total = len(tool_calls)

    # Calculate rate
    timestamps = [e.get("timestamp", "") for e in events if e.get("timestamp")]
    if len(timestamps) >= 2:
        first = datetime.fromisoformat(timestamps[0].replace("Z", "+00:00"))
        last = datetime.fromisoformat(timestamps[-1].replace("Z", "+00:00"))
        duration_minutes = max((last - first).total_seconds() / 60, 1)
        rate = total / duration_minutes
    else:
        rate = 0.0

    # Detect sensitive resource access
    sensitive = {}
    for e in events:
        tool_input = str(e.get("data", {}).get("tool_input", ""))
        for category, patterns in SENSITIVE_RESOURCE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, tool_input, re.IGNORECASE):
                    if category not in sensitive:
                        sensitive[category] = {"count": 0, "examples": []}
                    sensitive[category]["count"] += 1
                    if len(sensitive[category]["examples"]) < 3:
                        sensitive[category]["examples"].append(tool_input[:100])
                    break

    sensitive_list = [
        {"type": cat, "count": info["count"], "examples": info["examples"]}
        for cat, info in sensitive.items()
    ]

    # Count human checkpoints (blocked events where human made a decision)
    blocked = [e for e in events if e.get("event_type") == "blocked"]
    human_checkpoints = len(blocked)  # Each block requires human decision

    # Calculate autonomy score
    # High tool calls + low checkpoints + sensitive access = high autonomy
    autonomy = 50  # Base
    if total > 50:
        autonomy += 15
    if total > 200:
        autonomy += 15
    if human_checkpoints == 0 and total > 10:
        autonomy += 20
    elif human_checkpoints > 0:
        autonomy -= min(human_checkpoints * 10, 30)
    if sensitive_list:
        autonomy += min(len(sensitive_list) * 10, 20)
    autonomy = max(0, min(100, autonomy))

    # Determine risk level
    if autonomy >= 80 or any(s["type"] in ("credential_access", "system_command") for s in sensitive_list):
        risk_level = "critical"
    elif autonomy >= 60 or sensitive_list:
        risk_level = "high"
    elif autonomy >= 40:
        risk_level = "moderate"
    else:
        risk_level = "low"

    # Generate recommendations
    recommendations = []
    if human_checkpoints == 0 and total > 10:
        recommendations.append("No human checkpoints detected. Article 14 requires human oversight for high-risk AI. Add approval gates for sensitive operations.")
    if any(s["type"] == "credential_access" for s in sensitive_list):
        recommendations.append("Agent is accessing credentials. Ensure proper access controls and audit trail per Article 15.")
    if any(s["type"] == "database_write" for s in sensitive_list):
        recommendations.append("Agent is writing to databases. Add confirmation step before data modifications.")
    if rate > 10:
        recommendations.append(f"High tool-call rate ({rate:.1f}/min). Consider rate limiting for cost control and safety.")
    if autonomy >= 70:
        recommendations.append(f"High autonomy score ({autonomy}/100). Review whether this agent needs more human oversight per Article 14.")

    return {
        "session_id": session_id or "aggregate",
        "time_range": f"last {hours} hours",
        "total_tool_calls": total,
        "tool_call_rate": round(rate, 2),
        "sensitive_access": sensitive_list,
        "autonomy_score": autonomy,
        "human_checkpoints": human_checkpoints,
        "risk_level": risk_level,
        "recommendations": recommendations,
    }


def check_mcp_config(config_path: str = None) -> list:
    """Check MCP configuration files for exposed credentials.

    Scans .claude/settings.json, .cursor/mcp.json, and similar files
    for hardcoded secrets in MCP server configurations.

    Based on: GitGuardian 2026 report found 24,008 secrets in MCP config files.
    """
    from credential_check import check_secrets

    findings = []

    # Default paths to check
    config_paths = []
    if config_path:
        config_paths.append(Path(config_path))
    else:
        home = Path.home()
        config_paths.extend([
            home / ".claude" / "settings.json",
            home / ".claude" / "settings.local.json",
            home / ".cursor" / "mcp.json",
            home / ".config" / "claude" / "settings.json",
            Path.cwd() / ".claude" / "settings.json",
            Path.cwd() / ".claude" / "settings.local.json",
        ])

    for path in config_paths:
        if not path.exists():
            continue
        try:
            content = path.read_text(encoding="utf-8")
            secrets = check_secrets(content)
            for secret in secrets:
                findings.append({
                    "file": str(path),
                    "pattern": secret.pattern_name,
                    "confidence": secret.confidence,
                    "description": f"Credential in MCP config: {secret.description}",
                    "remediation": f"Move to environment variable. {secret.remediation}",
                })
        except (PermissionError, OSError):
            continue

    return findings


def format_agent_text(analysis: dict) -> str:
    """Format agent analysis for CLI output."""
    risk_labels = {
        "critical": "CRITICAL — high autonomy with sensitive access",
        "high": "HIGH — elevated autonomy or sensitive resource access",
        "moderate": "MODERATE — standard agent activity",
        "low": "LOW — supervised agent activity",
        "none": "NONE — no agent activity detected",
    }

    lines = [
        "",
        "=" * 60,
        "  Regula — Agent Governance Report",
        "=" * 60,
        f"  Session:          {analysis['session_id']}",
        f"  Period:           {analysis['time_range']}",
        f"  Tool calls:       {analysis['total_tool_calls']}",
        f"  Call rate:        {analysis['tool_call_rate']}/min",
        f"  Human checkpoints: {analysis['human_checkpoints']}",
        f"  Autonomy score:   {analysis['autonomy_score']}/100",
        f"  Risk level:       {risk_labels.get(analysis['risk_level'], analysis['risk_level'])}",
    ]

    if analysis["sensitive_access"]:
        lines.append("")
        lines.append("  Sensitive Resource Access:")
        for sa in analysis["sensitive_access"]:
            lines.append(f"    - {sa['type']}: {sa['count']} access(es)")

    if analysis["recommendations"]:
        lines.append("")
        lines.append("  Recommendations:")
        for rec in analysis["recommendations"]:
            lines.append(f"    - {rec}")

    lines.append("=" * 60)
    lines.append("")
    return "\n".join(lines)


def format_agent_json(analysis: dict) -> str:
    """Format agent analysis as JSON."""
    return json.dumps(analysis, indent=2)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Agentic AI governance monitoring")
    parser.add_argument("--session", "-s", help="Session ID")
    parser.add_argument("--hours", type=int, default=8)
    parser.add_argument("--format", "-f", choices=["text", "json"], default="text")
    parser.add_argument("--check-mcp", action="store_true", help="Check MCP configs for exposed credentials")
    parser.add_argument("--config", help="Specific MCP config file to check")
    args = parser.parse_args()

    if args.check_mcp:
        findings = check_mcp_config(args.config)
        if args.format == "json":
            print(json.dumps(findings, indent=2))
        else:
            if findings:
                print(f"\nFound {len(findings)} credential(s) in MCP configuration:")
                for f in findings:
                    print(f"  {f['file']}: {f['description']}")
                    print(f"    Fix: {f['remediation']}")
            else:
                print("No credentials found in MCP configuration files.")
        return

    analysis = analyse_agent_session(
        session_id=args.session or os.environ.get("CLAUDE_SESSION_ID"),
        hours=args.hours,
    )

    if args.format == "json":
        print(format_agent_json(analysis))
    else:
        print(format_agent_text(analysis))


if __name__ == "__main__":
    main()
