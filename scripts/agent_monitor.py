#!/usr/bin/env python3
# regula-ignore
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
sys.path.insert(0, str(Path(__file__).parent))

from log_event import query_events


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


# ---------------------------------------------------------------------------
# MCP Server Permission Analysis
# Based on: OWASP Agentic Top 10 (#1 Excessive Agency, #2 Uncontrolled Tool Use,
# #5 Identity and Authentication Gaps)
# ---------------------------------------------------------------------------

# Known MCP server categories and their risk implications
MCP_SERVER_RISK_PROFILES = {
    "filesystem": {"category": "file_access", "severity": "HIGH",
                   "description": "File system access — can read/write/delete files",
                   "owasp_agentic": "#1 Excessive Agency, #2 Uncontrolled Tool Use"},
    "postgres": {"category": "database", "severity": "HIGH",
                 "description": "Database access — can read/modify/delete data",
                 "owasp_agentic": "#1 Excessive Agency, #7 Data Exfiltration"},
    "sqlite": {"category": "database", "severity": "MEDIUM",
               "description": "Local database access",
               "owasp_agentic": "#1 Excessive Agency"},
    "github": {"category": "code_repository", "severity": "MEDIUM",
               "description": "GitHub access — can read/modify repositories",
               "owasp_agentic": "#1 Excessive Agency, #8 Supply Chain"},
    "slack": {"category": "communication", "severity": "MEDIUM",
              "description": "Slack messaging — can send messages as agent",
              "owasp_agentic": "#1 Excessive Agency, #7 Data Exfiltration"},
    "everything": {"category": "unrestricted", "severity": "CRITICAL",
                   "description": "Unrestricted access — development/testing server",
                   "owasp_agentic": "#1 Excessive Agency"},
    "puppeteer": {"category": "browser", "severity": "HIGH",
                  "description": "Browser automation — can navigate and interact with web pages",
                  "owasp_agentic": "#2 Uncontrolled Tool Use, #7 Data Exfiltration"},
    "fetch": {"category": "network", "severity": "MEDIUM",
              "description": "HTTP request capability",
              "owasp_agentic": "#2 Uncontrolled Tool Use"},
}

# Credential patterns in MCP config values
_CREDENTIAL_PATTERNS = [
    (r"sk-[a-zA-Z0-9\-]{20,}", "API key (OpenAI/Anthropic format)"),
    (r"ghp_[A-Za-z0-9_]{36,}", "GitHub personal access token"),
    (r"AKIA[0-9A-Z]{16}", "AWS access key"),
    (r"password\s*[:=]\s*\S+", "Password in configuration"),
    (r"://[^:]+:[^@]+@", "Credentials in connection string"),
]


def parse_mcp_servers(config: dict) -> list:
    """Parse MCP server definitions from a config dict.

    Handles both Claude Code format (mcpServers key) and
    Cursor format (mcpServers key).

    Returns list of server dicts with: name, command, args, env.
    """
    servers = []
    mcp_section = config.get("mcpServers", {})

    for name, server_config in mcp_section.items():
        if not isinstance(server_config, dict):
            continue
        servers.append({
            "name": name,
            "command": server_config.get("command", ""),
            "args": server_config.get("args", []),
            "env": server_config.get("env", {}),
        })

    return servers


def assess_mcp_risk(servers: list) -> list:
    """Assess risk of MCP server configurations.

    Maps to OWASP Agentic Top 10 and EU AI Act Article 14 (human oversight).

    Returns list of risk findings, each with:
        server, category, severity, description, owasp_agentic, remediation
    """
    risks = []

    for server in servers:
        name = server["name"]
        args_str = " ".join(str(a) for a in server.get("args", []))
        env = server.get("env", {})

        # Check against known server profiles
        for profile_key, profile in MCP_SERVER_RISK_PROFILES.items():
            if profile_key in name.lower() or profile_key in args_str.lower():
                risks.append({
                    "server": name,
                    "category": profile["category"],
                    "severity": profile["severity"],
                    "description": profile["description"],
                    "owasp_agentic": profile["owasp_agentic"],
                    "remediation": f"Review permissions for '{name}'. Apply least-privilege principle.",
                })
                break
        else:
            # Unknown server — flag for review
            risks.append({
                "server": name,
                "category": "unknown",
                "severity": "MEDIUM",
                "description": f"Unknown MCP server '{name}' — capabilities not assessed",
                "owasp_agentic": "#8 Supply Chain Risks",
                "remediation": f"Review '{name}' capabilities and restrict to required tools.",
            })

        # Check for credentials in env
        for env_key, env_val in env.items():
            env_val_str = str(env_val)
            for pattern, desc in _CREDENTIAL_PATTERNS:
                if re.search(pattern, env_val_str):
                    risks.append({
                        "server": name,
                        "category": "credential_in_env",
                        "severity": "MEDIUM",
                        "description": f"{desc} found in env var '{env_key}'",
                        "owasp_agentic": "#5 Identity and Authentication Gaps",
                        "remediation": "Use a secret manager instead of environment variables where possible.",
                    })
                    break

        # Check for credentials hardcoded in args
        for arg in server.get("args", []):
            arg_str = str(arg)
            for pattern, desc in _CREDENTIAL_PATTERNS:
                if re.search(pattern, arg_str):
                    risks.append({
                        "server": name,
                        "category": "credential_hardcoded",
                        "severity": "HIGH",
                        "description": f"{desc} hardcoded in command arguments",
                        "owasp_agentic": "#5 Identity and Authentication Gaps",
                        "remediation": "Move credentials to environment variables or secret manager.",
                    })
                    break

    return risks


def format_mcp_risk_text(risks: list) -> str:
    """Format MCP risk assessment as human-readable text."""
    if not risks:
        return "No MCP server risks detected.\n"

    lines = [
        "",
        "=" * 60,
        "  MCP Server Risk Assessment",
        "=" * 60,
    ]

    for r in risks:
        severity = r["severity"]
        lines.append(f"  [{severity}] {r['server']}: {r['description']}")
        if r.get("owasp_agentic"):
            lines.append(f"         OWASP Agentic: {r['owasp_agentic']}")
        lines.append(f"         Fix: {r['remediation']}")

    lines.append("=" * 60)
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Autonomous Action Detection in Source Code
# Based on: OWASP LLM08 (Excessive Agency), OWASP Agentic #6 (Unmonitored
# Autonomous Actions), EU AI Act Article 14 (Human Oversight)
# ---------------------------------------------------------------------------

# Patterns where AI output flows to external actions
_AI_OUTPUT_PATTERNS = [
    r"(?:response|result|completion|output|message)\.(?:choices|content|text|data)",
    r"(?:client|openai|anthropic)\.\w+\.(?:create|generate|invoke|run)",
    r"model\.\w*(?:predict|generate|forward|infer)\(",
]

# External action patterns that should have human gates
_EXTERNAL_ACTION_PATTERNS = [
    (r"subprocess\.(?:run|call|Popen)", "System command execution"),
    (r"os\.system\(", "System command execution"),
    (r"requests\.(?:post|put|patch|delete)\(", "HTTP mutation request"),
    (r"httpx\.(?:post|put|patch|delete)\(", "HTTP mutation request"),
    (r"(?:cursor|conn|connection|session|db|engine)\.execute\(", "Database query execution"),
    (r"(?:smtp|email|mail|sendgrid|ses|postmark|mailgun|twilio|slack).*\.send\(", "Message/email sending"),
    (r"send_(?:email|message|notification|sms)\(", "Message/email sending"),
    (r"shutil\.(?:rmtree|move|copy)", "File system modification"),
    (r"os\.(?:remove|unlink|rename)\(", "File system modification"),
]

# Human gate patterns that mitigate autonomous action risk
_HUMAN_GATE_PATTERNS = [
    r"if\s+.*(?:approved|confirmed|user_approved|human_review)",
    r"input\(",
    r"click\.confirm",
    r"if\s+.*(?:dry_run|preview|simulate)",
    r"approval_required",
    r"human_in_the_loop",
]


def detect_autonomous_actions(code: str, filepath: str = "") -> list:
    """Detect AI output -> external action patterns without human gates.

    Two detection modes:
    1. Direct: AI output patterns + external actions in same file
    2. Contextual: External actions in files whose path indicates agent/tool
       infrastructure (agent/, tool/, middleware/, plugin/, executor/).
       Per OWASP Agentic Top 10 (2026) ASI02 & ASI04, agent tool code that
       executes subprocess/system commands is a risk even when AI output
       is consumed in a different module.

    Returns list of findings, each with:
        line, action_pattern, description, owasp_ref, has_human_gate
    """
    findings = []
    lines = code.split("\n")

    # Check if code has AI patterns at all
    has_ai = any(re.search(p, code, re.IGNORECASE) for p in _AI_OUTPUT_PATTERNS)

    # Contextual detection: files in agent/tool infrastructure paths
    # These files provide tool capabilities to agents even if AI output
    # is consumed in a separate orchestration module
    _AGENT_PATH_INDICATORS = (
        "agent", "tool", "middleware", "plugin", "executor",
        "action", "capability", "sandbox",
    )
    fp_lower = filepath.lower()
    is_agent_infra = any(ind in fp_lower for ind in _AGENT_PATH_INDICATORS)

    if not has_ai and not is_agent_infra:
        return findings

    # Check for human gates anywhere in the code
    has_gate = any(re.search(p, code, re.IGNORECASE) for p in _HUMAN_GATE_PATTERNS)

    # Find external action patterns
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("#") or stripped.startswith("//"):
            continue

        for pattern, desc in _EXTERNAL_ACTION_PATTERNS:
            if re.search(pattern, line):
                if has_ai:
                    detail = f"AI output may flow to {desc}"
                else:
                    detail = f"Agent tool infrastructure: {desc}"
                if not has_gate:
                    detail += " — no human gate detected"
                else:
                    detail += " — human gate pattern detected nearby"

                findings.append({
                    "line": i,
                    "action_pattern": desc,
                    "description": detail,
                    "owasp_ref": "OWASP Agentic ASI02 Tool Misuse / ASI04 Missing Guardrails",
                    "has_human_gate": has_gate,
                    "detection_mode": "direct" if has_ai else "contextual",
                })
                break

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


# ---------------------------------------------------------------------------
# OWASP Top 10 for Agentic Applications (Dec 2025)
# https://owasp.org/www-project-top-10-for-agentic-applications/
# ---------------------------------------------------------------------------

OWASP_AGENTIC_RISKS = [
    {"id": "ASI01", "name": "Agent Goal Hijack"},
    {"id": "ASI02", "name": "Tool Misuse and Exploitation"},
    {"id": "ASI03", "name": "Identity and Privilege Abuse"},
    {"id": "ASI04", "name": "Agentic Supply Chain Vulnerabilities"},
    {"id": "ASI05", "name": "Unexpected Code Execution (RCE)"},
    {"id": "ASI06", "name": "Memory & Context Poisoning"},
    {"id": "ASI07", "name": "Insecure Inter-Agent Communication"},
    {"id": "ASI08", "name": "Cascading Failures"},
    {"id": "ASI09", "name": "Human-Agent Trust Exploitation"},
    {"id": "ASI10", "name": "Rogue Agents"},
]

# Vulnerability patterns (presence = risk) and control patterns (presence = mitigation)
OWASP_AGENTIC_PATTERNS = {
    "ASI01": {
        "vuln": [
            r"(?:system_prompt|instructions)\s*[=+]\s*.*(?:user_input|request\.)",
            r"\.format\(.*(?:user_input|prompt|message)\)",
            r"f['\"].*\{(?:user_input|prompt|query|message)\}",
            r"messages\s*\.\s*append\(\s*\{[^}]*role.*user_input",
        ],
        "control": [
            r"(?:sanitize|validate|filter)_(?:prompt|input|instruction)",
            r"input_(?:sanitization|validation|filtering)",
            r"prompt_(?:guard|shield|filter|validator)",
            r"(?:ALLOWED_INSTRUCTIONS|INSTRUCTION_ALLOWLIST)",
        ],
    },
    "ASI02": {
        "vuln": [
            r"tools\s*=\s*\[\s*['\"]?\*['\"]?\s*\]",
            r"allow_all_tools|enabled_tools\s*=\s*None",
            r"tool_choice\s*=\s*['\"](?:any|auto)['\"]",
            r"@tool\s*\n\s*def\s+\w+.*(?:subprocess|os\.system|eval|exec)",
        ],
        "control": [
            r"(?:ALLOWED_TOOLS|TOOL_ALLOWLIST|tool_whitelist)",
            r"tool_(?:validator|guard|filter|permissions)",
            r"if\s+.*tool.*not\s+in\s+.*allowed",
            r"(?:restrict|limit)_tools",
        ],
    },
    "ASI03": {
        "vuln": [
            r"(?:SHARED_API_KEY|GLOBAL_TOKEN|common_credentials)",
            r"agent.*\.(?:token|key|credentials)\s*=\s*(?:os\.environ|config)\[",
            r"run_as_(?:root|admin|superuser)",
            r"(?:sudo|chmod\s+777|chmod\s+\+x)",
        ],
        "control": [
            r"(?:per_agent_identity|agent_identity|agent_credentials)",
            r"(?:RBAC|role_based|permission_check|authorize_agent)",
            r"least_privilege|minimal_permissions",
            r"scope\s*=\s*\[",
        ],
    },
    "ASI04": {
        "vuln": [
            r"pip\s+install\s+(?!-r)(?!--requirement)\S+\s+--(?:no-verify|trusted-host)",
            r"(?:curl|wget)\s+.*\|\s*(?:bash|sh|python)",
            r"load_plugin\(.*(?:url|remote|http)",
            r"importlib\.import_module\(.*(?:user|input|config)\[",
        ],
        "control": [
            r"(?:verify_integrity|check_hash|checksum|signature_verify)",
            r"(?:TRUSTED_PLUGINS|PLUGIN_ALLOWLIST|approved_tools)",
            r"(?:pin|lock)_(?:dependencies|versions)",
            r"(?:requirements\.txt|poetry\.lock|Pipfile\.lock)",
        ],
    },
    "ASI05": {
        "vuln": [
            r"eval\s*\(",
            r"exec\s*\(",
            r"compile\s*\(.*['\"]exec['\"]",
            r"subprocess\.(?:run|call|Popen).*shell\s*=\s*True",
            r"os\.system\s*\(",
            r"code_interpreter|execute_code|run_code",
        ],
        "control": [
            r"(?:sandbox|jail|isolate|container)_(?:exec|run|code)",
            r"(?:RestrictedPython|ast\.literal_eval)",
            r"shell\s*=\s*False",
            r"(?:seccomp|apparmor|no_new_privs)",
            r"(?:timeout|resource_limit|max_execution)",
        ],
    },
    "ASI06": {
        "vuln": [
            r"(?:conversation|history|memory|context)\s*\.\s*(?:append|extend|insert)\s*\(",
            r"(?:load|restore)_(?:context|memory|history)\s*\(",
            r"(?:pickle|marshal|shelve)\.(?:load|loads)\s*\(",
            r"(?:deserializ|unpickl)",
        ],
        "control": [
            r"(?:validate|verify|check)_(?:context|memory|history)",
            r"(?:context|memory)_(?:integrity|hash|signature)",
            r"(?:hmac|sign|digest)\s*\(",
            r"(?:immutable|frozen|read_only)_(?:context|memory)",
        ],
    },
    "ASI07": {
        "vuln": [
            r"(?:send|receive)_(?:message|task)\s*\(.*(?:json|str|dict)\s*\)",
            r"agent_(?:call|invoke|send)\s*\(",
            r"(?:inter_agent|agent_to_agent|a2a)_(?:message|comm)",
            r"(?:grpc|rabbitmq|redis).*(?:publish|send)\s*\(",
        ],
        "control": [
            r"(?:authenticate|verify|validate)_(?:agent|sender|message)",
            r"(?:encrypt|tls|ssl|mtls|mTLS).*(?:agent|message|channel)",
            r"(?:message|agent)_(?:auth|token|signature)",
            r"(?:signed|encrypted)_(?:message|payload)",
        ],
    },
    "ASI08": {
        "vuln": [
            r"while\s+True\s*:.*(?:retry|attempt|try)",
            r"except\s*:.*(?:pass|continue)",
            r"except\s+Exception\s*:.*(?:pass|continue)",
            r"(?:max_retries|retry_count)\s*=\s*(?:None|float\(['\"]inf)",
        ],
        "control": [
            r"(?:circuit_breaker|CircuitBreaker)",
            r"(?:max_retries|retry_limit)\s*=\s*\d+",
            r"(?:error_boundary|fault_tolerance|fallback)",
            r"(?:timeout|deadline)\s*=\s*\d+",
            r"(?:backoff|exponential_backoff)",
        ],
    },
    "ASI09": {
        "vuln": [
            r"(?:pretend|act_as|impersonate|role_play)\s*.*(?:human|person|user)",
            r"(?:name|identity|role)\s*=\s*['\"](?:.*(?:assistant|agent|bot).*)['\"]",
            r"(?:hide|conceal|mask)_(?:identity|ai_status|bot_status)",
        ],
        "control": [
            r"(?:human_in_the_loop|HITL|human_review|human_approval)",
            r"(?:is_ai|is_bot|ai_disclosure|bot_disclosure)",
            r"(?:require_human|await_human|pending_review)",
            r"(?:transparency|disclose_ai|ai_label)",
        ],
    },
    "ASI10": {
        "vuln": [
            r"(?:autonomous|self_directed|unrestricted)_(?:mode|agent|run)",
            r"(?:no_limit|unlimited)_(?:actions|tools|scope)",
            r"(?:bypass|skip|disable)_(?:governance|policy|guard|limit)",
        ],
        "control": [
            r"(?:kill_switch|emergency_stop|shutdown|terminate_agent)",
            r"(?:governance_policy|policy_check|compliance_check)",
            r"(?:resource_limit|rate_limit|budget_limit|max_actions)",
            r"(?:audit_log|agent_log|action_log)",
        ],
    },
}


def _scan_files_for_patterns(project_path: str) -> dict:
    """Scan project files and collect pattern matches per OWASP risk."""
    p = Path(project_path)
    if not p.is_dir():
        return {}

    extensions = {".py", ".js", ".ts", ".jsx", ".tsx", ".mjs", ".cjs"}
    results = {}  # risk_id -> {"vuln": [(file, line, match)], "control": [(file, line, match)]}

    for risk in OWASP_AGENTIC_RISKS:
        results[risk["id"]] = {"vuln": [], "control": []}

    files_scanned = 0
    for f in p.rglob("*"):
        if f.suffix not in extensions:
            continue
        if any(part.startswith(".") or part == "node_modules" for part in f.parts):
            continue
        try:
            content = f.read_text(encoding="utf-8", errors="ignore")
        except (PermissionError, OSError):
            continue
        files_scanned += 1
        rel = str(f.relative_to(p))

        for risk_id, patterns in OWASP_AGENTIC_PATTERNS.items():
            for ptype in ("vuln", "control"):
                for pat in patterns[ptype]:
                    for i, line in enumerate(content.split("\n"), 1):
                        if re.search(pat, line, re.IGNORECASE):
                            results[risk_id][ptype].append((rel, i, line.strip()[:120]))

    return results


def assess_owasp_agentic(project_path: str) -> dict:
    """Assess project against OWASP Top 10 for Agentic Applications.

    Returns dict with:
    - risks: list of {id, name, status, evidence, recommendations}
    - coverage_score: 0-100 (% of risks with controls detected)
    - summary: text summary
    """
    raw = _scan_files_for_patterns(project_path)
    risks = []
    mitigated_count = 0

    for risk_info in OWASP_AGENTIC_RISKS:
        rid = risk_info["id"]
        rname = risk_info["name"]
        matches = raw.get(rid, {"vuln": [], "control": []})

        has_vuln = len(matches["vuln"]) > 0
        has_control = len(matches["control"]) > 0

        if has_vuln and has_control:
            status = "mitigated"
        elif has_vuln and not has_control:
            status = "at_risk"
        elif not has_vuln and has_control:
            status = "mitigated"
        else:
            status = "not_assessed"

        if status == "mitigated":
            mitigated_count += 1

        evidence_items = []
        for (fpath, lineno, text) in matches["vuln"][:3]:
            evidence_items.append(f"VULN {fpath}:{lineno} — {text}")
        for (fpath, lineno, text) in matches["control"][:3]:
            evidence_items.append(f"CTRL {fpath}:{lineno} — {text}")

        rec = _recommendation_for(rid, status)

        risks.append({
            "id": rid,
            "name": rname,
            "status": status,
            "evidence": evidence_items,
            "vuln_count": len(matches["vuln"]),
            "control_count": len(matches["control"]),
            "recommendations": rec,
        })

    coverage = int((mitigated_count / len(OWASP_AGENTIC_RISKS)) * 100) if OWASP_AGENTIC_RISKS else 0
    at_risk = sum(1 for r in risks if r["status"] == "at_risk")
    not_assessed = sum(1 for r in risks if r["status"] == "not_assessed")

    summary = (
        f"OWASP Agentic Top 10: {mitigated_count}/10 mitigated, "
        f"{at_risk} at risk, {not_assessed} not assessed. "
        f"Coverage score: {coverage}%."
    )

    return {
        "risks": risks,
        "coverage_score": coverage,
        "summary": summary,
    }


_RECOMMENDATIONS = {
    "ASI01": "Add input sanitisation before injecting user content into agent instructions. Use an instruction allowlist.",
    "ASI02": "Define an explicit tool allowlist. Reject tool calls not on the list.",
    "ASI03": "Assign per-agent credentials with least-privilege scopes. Implement RBAC for agent actions.",
    "ASI04": "Pin dependency versions, verify plugin integrity with checksums, maintain an approved-tools list.",
    "ASI05": "Use sandboxed execution (RestrictedPython, containers). Never pass unsanitised input to eval/exec/subprocess.",
    "ASI06": "Validate context integrity with HMAC or signatures. Use immutable conversation history.",
    "ASI07": "Authenticate inter-agent messages. Use mTLS or signed payloads for agent-to-agent communication.",
    "ASI08": "Add circuit breakers, bounded retries (max_retries=N), and timeouts to all agent chains.",
    "ASI09": "Require AI disclosure in all agent outputs. Add human-in-the-loop gates for consequential actions.",
    "ASI10": "Implement kill switches, resource limits, governance policy checks, and audit logging for all agents.",
}


def _recommendation_for(risk_id: str, status: str) -> str:
    if status == "mitigated":
        return "Controls detected. Verify they cover all code paths."
    return _RECOMMENDATIONS.get(risk_id, "Review OWASP Agentic Top 10 guidance for this risk.")


def format_owasp_agentic_text(result: dict) -> str:
    """Format OWASP Agentic assessment for terminal output."""
    lines = [
        "",
        "=" * 70,
        "  OWASP Top 10 for Agentic Applications — Assessment",
        "=" * 70,
        "",
        f"  Coverage Score: {result['coverage_score']}%",
        f"  {result['summary']}",
        "",
    ]

    # Group by status: at_risk first, then not_assessed, then mitigated
    status_order = {"at_risk": 0, "not_assessed": 1, "mitigated": 2}
    sorted_risks = sorted(result["risks"], key=lambda r: status_order.get(r["status"], 9))

    status_icons = {
        "at_risk": "\033[91m✗ AT RISK\033[0m",
        "not_assessed": "\033[93m? NOT ASSESSED\033[0m",
        "mitigated": "\033[92m✓ MITIGATED\033[0m",
    }

    current_status = None
    for risk in sorted_risks:
        s = risk["status"]
        if s != current_status:
            current_status = s
            label = {"at_risk": "ACTION NEEDED", "not_assessed": "NOT ASSESSED", "mitigated": "MITIGATED"}
            lines.append(f"  ── {label.get(s, s)} ──")

        icon = status_icons.get(s, s)
        lines.append(f"  {risk['id']} | {risk['name']:<42} | {icon}")

        if risk["evidence"]:
            lines.append(f"         Evidence: {risk['evidence'][0]}")
        lines.append(f"         Rec: {risk['recommendations']}")
        lines.append("")

    lines.append("=" * 70)
    at_risk_ids = [r["id"] for r in result["risks"] if r["status"] == "at_risk"]
    if at_risk_ids:
        lines.append(f"  Run 'regula agent --fix {at_risk_ids[0]}' for remediation guidance")
    else:
        lines.append("  No critical gaps detected.")
    lines.append("")

    return "\n".join(lines)


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
