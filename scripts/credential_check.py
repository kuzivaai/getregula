#!/usr/bin/env python3
# regula-ignore
"""
Regula Secret Detection — Credential Leak Prevention in AI Tool Inputs

Detects hardcoded credentials and API keys in tool inputs before they are
executed. Focused on AI-related credentials (OpenAI, Anthropic, AWS, Google,
GitHub) that commonly leak through AI coding assistant interactions.

Evidence: GitGuardian found Copilot repositories have 6.4% secret leak rate,
40% higher than average. 8.5% of prompts to AI tools include sensitive
information (PurpleSec 2026). GitHub shipped MCP secret scanning 17 March 2026.

Design decisions:
  - HIGH confidence patterns (prefixed keys): BLOCK with bypass path
    (matches GitHub push protection behaviour — 85% developer acceptance)
  - MEDIUM confidence patterns (generic): WARN via additionalContext
  - Never display full secret in any output — redact to first 4 chars
  - Secrets detection is separate from AI risk classification (SRP)
  - This module covers tool inputs only, not general file scanning
    (use gitleaks/truffleHog/detect-secrets for file-level scanning)
"""

import re
from dataclasses import dataclass
@dataclass
class SecretFinding:
    pattern_name: str
    confidence: str  # "high" or "medium"
    confidence_score: int  # 0-100
    redacted_value: str  # First 4 chars + ****
    description: str
    remediation: str


# ---------------------------------------------------------------------------
# Patterns — validated against secrets-patterns-db and GitGuardian
#
# High confidence: specific prefix format, very low false positive rate
# Medium confidence: contextual patterns, moderate false positive rate
# ---------------------------------------------------------------------------

SECRET_PATTERNS = {
    # --- HIGH confidence (prefixed, block-worthy) ---
    "openai_api_key": {
        "pattern": r"sk-(?!ant-)[a-zA-Z0-9][a-zA-Z0-9\-]{19,}",
        "confidence": "high",
        "confidence_score": 95,
        "description": "OpenAI API key detected",
        "remediation": "Use environment variable OPENAI_API_KEY instead of hardcoding.",
        "source": "GitGuardian pattern database",
    },
    "anthropic_api_key": {
        "pattern": r"sk-ant-[a-zA-Z0-9\-]{20,}",
        "confidence": "high",
        "confidence_score": 95,
        "description": "Anthropic API key detected",
        "remediation": "Use environment variable ANTHROPIC_API_KEY instead of hardcoding.",
        "source": "GitGuardian pattern database",
    },
    "aws_access_key": {
        "pattern": r"AKIA[0-9A-Z]{16}",
        "confidence": "high",
        "confidence_score": 95,
        "description": "AWS access key ID detected",
        "remediation": "Use AWS credential provider chain or environment variables.",
        "source": "AWS documentation, GitGuardian",
    },
    "google_api_key": {
        "pattern": r"AIza[0-9A-Za-z\-_]{35}",
        "confidence": "high",
        "confidence_score": 90,
        "description": "Google API key detected",
        "remediation": "Use environment variable or Google Cloud credential provider.",
        "source": "GitGuardian pattern database",
    },
    "github_token": {
        "pattern": r"gh[ps]_[A-Za-z0-9_]{36,}",
        "confidence": "high",
        "confidence_score": 95,
        "description": "GitHub personal access token detected",
        "remediation": "Use environment variable GITHUB_TOKEN or credential helper.",
        "source": "GitHub documentation",
    },
    "private_key": {
        "pattern": r"-----BEGIN (?:RSA |DSA |EC |OPENSSH )?PRIVATE KEY-----",
        "confidence": "high",
        "confidence_score": 98,
        "description": "Private key detected",
        "remediation": "Never include private keys in commands. Use SSH agent or key file path.",
        "source": "Standard PEM format",
    },

    # --- MEDIUM confidence (contextual, warn-worthy) ---
    "generic_api_key": {
        "pattern": r"(?i)(?:api[_-]?key|api[_-]?secret|access[_-]?token|auth[_-]?token)\s*[:=]\s*['\"]([A-Za-z0-9\-_.]{20,})['\"]",
        "confidence": "medium",
        "confidence_score": 60,
        "description": "Possible API key or token in assignment",
        "remediation": "Move credentials to environment variables or a secrets manager.",
        "source": "secrets-patterns-db",
    },
    "connection_string": {
        "pattern": r"(?i)(?:mongodb|postgres|mysql|redis|amqp):\/\/(?!localhost)[^\s'\"]{10,}",
        "confidence": "medium",
        "confidence_score": 70,
        "description": "Database connection string with possible credentials",
        "remediation": "Use environment variable for connection strings. Never hardcode credentials.",
        "source": "Standard URI format",
    },
    "aws_secret_key": {
        "pattern": r"(?i)aws.{0,20}(?:secret|key).{0,20}['\"][0-9a-zA-Z/+=]{40}['\"]",
        "confidence": "medium",
        "confidence_score": 75,
        "description": "Possible AWS secret access key",
        "remediation": "Use AWS credential provider chain or environment variables.",
        "source": "secrets-patterns-db",
    },

    # --- HIGH confidence: AI/ML service keys (prefixed, block-worthy) ---
    "pinecone_api_key": {
        "pattern": r"pcsk_[a-zA-Z0-9]{40,}",
        "confidence": "high",
        "confidence_score": 95,
        "description": "Pinecone API key detected",
        "remediation": "Use environment variable PINECONE_API_KEY instead of hardcoding.",
        "source": "Pinecone documentation",
    },
    "langsmith_api_key": {
        "pattern": r"ls__[a-zA-Z0-9]{32,}",
        "confidence": "high",
        "confidence_score": 95,
        "description": "LangSmith/LangChain API key detected",
        "remediation": "Use environment variable LANGCHAIN_API_KEY instead of hardcoding.",
        "source": "LangSmith documentation",
    },
    "replicate_api_token": {
        "pattern": r"r8_[a-zA-Z0-9]{36,}",
        "confidence": "high",
        "confidence_score": 95,
        "description": "Replicate API token detected",
        "remediation": "Use environment variable REPLICATE_API_TOKEN instead of hardcoding.",
        "source": "Replicate documentation",
    },
    "fireworks_ai_key": {
        "pattern": r"fw_[a-zA-Z0-9]{32,}",
        "confidence": "high",
        "confidence_score": 90,
        "description": "Fireworks AI API key detected",
        "remediation": "Use environment variable FIREWORKS_API_KEY instead of hardcoding.",
        "source": "Fireworks AI documentation",
    },

    # --- MEDIUM confidence: AI/ML service keys (contextual) ---
    "qdrant_api_key": {
        "pattern": r"(?i)qdrant.*api[_\-]?key\s*[:=]\s*[\"'][^\"']{10,}",
        "confidence": "medium",
        "confidence_score": 70,
        "description": "Possible Qdrant API key in assignment",
        "remediation": "Use environment variable QDRANT_API_KEY instead of hardcoding.",
        "source": "Qdrant documentation",
    },
    "cohere_api_key": {
        "pattern": r"(?i)cohere.*api[_\-]?key\s*[:=]\s*[\"'][a-zA-Z0-9]{40,}",
        "confidence": "medium",
        "confidence_score": 70,
        "description": "Possible Cohere API key in assignment",
        "remediation": "Use environment variable CO_API_KEY instead of hardcoding.",
        "source": "Cohere documentation",
    },
    "wandb_api_key": {
        "pattern": r"(?i)wandb.*api[_\-]?key\s*[:=]\s*[\"'][a-f0-9]{40}",
        "confidence": "medium",
        "confidence_score": 70,
        "description": "Weights & Biases API key detected",
        "remediation": "Use environment variable WANDB_API_KEY instead of hardcoding.",
        "source": "Weights & Biases documentation",
    },
    "mlflow_tracking_token": {
        "pattern": r"(?i)mlflow.*token\s*[:=]\s*[\"'][^\"']{10,}",
        "confidence": "medium",
        "confidence_score": 65,
        "description": "Possible MLflow tracking token in assignment",
        "remediation": "Use environment variable MLFLOW_TRACKING_TOKEN instead of hardcoding.",
        "source": "MLflow documentation",
    },
    "weaviate_api_key": {
        "pattern": r"(?i)weaviate.*(?:api[_\-]?key|auth[_\-]?token)\s*[:=]\s*[\"'][^\"']{10,}",
        "confidence": "medium",
        "confidence_score": 65,
        "description": "Possible Weaviate API key in assignment",
        "remediation": "Use environment variable WEAVIATE_API_KEY instead of hardcoding.",
        "source": "Weaviate documentation",
    },
}


def _redact(value: str) -> str:
    """Redact a secret value, showing only the first 4 characters."""
    if len(value) <= 4:
        return "****"
    return value[:4] + "****"


def check_secrets(text: str) -> list[SecretFinding]:
    """Check text for hardcoded secrets and credentials.

    Returns a list of SecretFinding objects, sorted by confidence (high first).
    """
    findings = []
    for name, config in SECRET_PATTERNS.items():
        match = re.search(config["pattern"], text)
        if match:
            matched_value = match.group(0)
            findings.append(SecretFinding(
                pattern_name=name,
                confidence=config["confidence"],
                confidence_score=config["confidence_score"],
                redacted_value=_redact(matched_value),
                description=config["description"],
                remediation=config["remediation"],
            ))

    # Sort: high confidence first
    findings.sort(key=lambda f: -f.confidence_score)
    return findings


def has_high_confidence_secret(text: str) -> bool:
    """Quick check: does the text contain any high-confidence secret?"""
    for config in SECRET_PATTERNS.values():
        if config["confidence"] == "high" and re.search(config["pattern"], text):
            return True
    return False


def format_secret_warning(findings: list[SecretFinding]) -> str:
    """Format secret findings as a warning message for hooks."""
    if not findings:
        return ""

    high = [f for f in findings if f.confidence == "high"]
    medium = [f for f in findings if f.confidence == "medium"]

    lines = []

    if high:
        lines.append("CREDENTIAL EXPOSURE RISK DETECTED")
        lines.append("")
        for f in high:
            lines.append(f"  {f.description}")
            lines.append(f"  Value: {f.redacted_value}")
            lines.append(f"  Fix: {f.remediation}")
            lines.append("")
        lines.append("This action has been blocked to prevent credential leakage.")
        lines.append("If this is a false positive or test value, you can proceed")
        lines.append("by removing the credential from the command and using an")
        lines.append("environment variable instead.")

    if medium:
        if high:
            lines.append("")
            lines.append("Additional warnings:")
        else:
            lines.append("CREDENTIAL WARNING")
            lines.append("")
        for f in medium:
            lines.append(f"  {f.description}: {f.redacted_value}")
            lines.append(f"  Fix: {f.remediation}")

    return "\n".join(lines)
