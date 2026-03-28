# regula-ignore
#!/usr/bin/env python3
"""
Regula Risk Indication Engine

Detects patterns in code that correlate with EU AI Act risk tiers.

IMPORTANT: This engine performs pattern-based risk INDICATION, not legal
risk CLASSIFICATION. The EU AI Act Article 6 requires a contextual
assessment of intended purpose and deployment context that automated
pattern matching cannot provide. Results should be treated as flags
for human review, not as legal determinations.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Optional

# Core types
from risk_types import RiskTier, Classification

# Pattern definitions
from risk_patterns import (
    PROHIBITED_PATTERNS, HIGH_RISK_PATTERNS, LIMITED_RISK_PATTERNS,
    AI_SECURITY_PATTERNS, AI_INDICATORS, GPAI_TRAINING_PATTERNS,
    ISO_42001_MAP, GOVERNANCE_OBSERVATIONS,
)

# Policy configuration
from policy_config import (
    get_policy, get_governance_contacts, get_regulatory_basis,
    _parse_yaml_fallback,
)


# ---------------------------------------------------------------------------
# AI security check
# ---------------------------------------------------------------------------

def check_ai_security(text: str) -> list:
    """Check for AI-specific security antipatterns.

    Skips comments and docstrings to avoid false positives on
    documentation that merely mentions these patterns.

    Returns a list of finding dicts, each with:
        pattern_name, owasp, description, severity, remediation, line, matched_line
    """
    findings = []
    lines = text.split("\n")
    in_docstring = False

    for name, config in AI_SECURITY_PATTERNS.items():
        for pattern in config["patterns"]:
            for i, line in enumerate(lines, 1):
                # Skip extremely long lines to prevent regex performance issues
                if len(line) > 2000:
                    continue
                stripped = line.strip()

                # Skip comments (Python #, JS //, C++ //)
                if stripped.startswith("#") or stripped.startswith("//"):
                    continue

                # Skip docstrings (triple quotes)
                if '"""' in stripped or "'''" in stripped:
                    # Toggle docstring state (simple heuristic)
                    count = stripped.count('"""') + stripped.count("'''")
                    if count == 1:
                        in_docstring = not in_docstring
                    continue
                if in_docstring:
                    continue

                # Skip lines that are clearly string literals containing examples
                # (e.g., docstring args descriptions, help text)
                if stripped.startswith(("Args:", "Returns:", "Example:", ">>>", ".. ")):
                    continue

                if re.search(pattern, line, re.IGNORECASE):
                    findings.append({
                        "pattern_name": name,
                        "owasp": config["owasp"],
                        "description": config["description"],
                        "severity": config["severity"],
                        "remediation": config["remediation"],
                        "line": i,
                        "matched_line": stripped[:100],
                    })
                    break  # One match per pattern per file is enough
        # Reset docstring state between patterns
        in_docstring = False

    return findings


# ---------------------------------------------------------------------------
# Training activity detection
# ---------------------------------------------------------------------------

def is_training_activity(text: str) -> bool:
    """Detect whether code involves model training/fine-tuning (not just inference)."""
    return any(re.search(p, text, re.IGNORECASE) for p in GPAI_TRAINING_PATTERNS)


# ---------------------------------------------------------------------------
# Governance observations
# ---------------------------------------------------------------------------

def generate_observations(text: str) -> list:
    """Generate Article-specific governance observations from code patterns.

    Returns a list of dicts with 'article' and 'observation' keys.
    Only runs on text already classified as high-risk.
    """
    observations = []
    text_lower = text.lower()

    for name, config in GOVERNANCE_OBSERVATIONS.items():
        found = any(re.search(p, text_lower) for p in config["patterns"])

        if name == "no_logging":
            # Flag absence of logging, not presence
            if not found:
                observations.append({
                    "article": config["article"],
                    "observation": config["absence_observation"],
                })
        elif found and config.get("observation"):
            observations.append({
                "article": config["article"],
                "observation": config["observation"],
            })

    return observations


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def _compute_confidence_score(tier: str, num_matches: int, has_ai_indicator: bool) -> int:
    """Compute a 0-100 confidence score based on tier, match count, and context."""
    base = {"prohibited": 75, "high_risk": 55, "limited_risk": 40, "minimal_risk": 15}.get(tier, 10)
    match_bonus = min(num_matches * 8, 15)
    ai_bonus = 10 if has_ai_indicator else 0
    return min(base + match_bonus + ai_bonus, 100)


# ---------------------------------------------------------------------------
# Core classification functions
# ---------------------------------------------------------------------------

def is_ai_related(text: str) -> bool:
    text_lower = text.lower()
    for category in AI_INDICATORS.values():
        for pattern in category:
            if re.search(pattern, text_lower):
                return True
    return False


def check_prohibited(text: str) -> Optional[Classification]:
    text_lower = text.lower()
    matches = []
    for name, config in PROHIBITED_PATTERNS.items():
        for pattern in config["patterns"]:
            if re.search(pattern, text_lower):
                matches.append(config | {"indicator": name})
                break

    if matches:
        primary = matches[0]
        has_ai = is_ai_related(text)
        return Classification(
            tier=RiskTier.PROHIBITED,
            confidence="high" if len(matches) >= 2 else "medium",
            indicators_matched=[m["indicator"] for m in matches],
            applicable_articles=[primary["article"]],
            category="Prohibited (Article 5)",
            description=primary["description"],
            action="block",
            message=f"PROHIBITED: {primary['description']}",
            exceptions=primary.get("exceptions"),
            confidence_score=_compute_confidence_score("prohibited", len(matches), has_ai),
        )
    return None


def check_high_risk(text: str) -> Optional[Classification]:
    text_lower = text.lower()
    matches = []
    for name, config in HIGH_RISK_PATTERNS.items():
        for pattern in config["patterns"]:
            if re.search(pattern, text_lower):
                matches.append(config | {"indicator": name})
                break

    if matches:
        all_articles = set()
        for m in matches:
            all_articles.update(m["articles"])
        primary = matches[0]
        return Classification(
            tier=RiskTier.HIGH_RISK,
            confidence="high" if len(matches) >= 2 else "medium",
            indicators_matched=[m["indicator"] for m in matches],
            applicable_articles=sorted(all_articles, key=int),
            category=primary["category"],
            description=primary["description"],
            action="allow_with_requirements",
            message=f"HIGH-RISK: {primary['description']} - Articles {', '.join(sorted(all_articles, key=int))}",
            confidence_score=_compute_confidence_score("high_risk", len(matches), True),
        )
    return None


def check_limited_risk(text: str) -> Optional[Classification]:
    text_lower = text.lower()
    matches = []
    for name, config in LIMITED_RISK_PATTERNS.items():
        for pattern in config["patterns"]:
            if re.search(pattern, text_lower):
                matches.append(config | {"indicator": name})
                break

    if matches:
        primary = matches[0]
        return Classification(
            tier=RiskTier.LIMITED_RISK,
            confidence="high" if len(matches) >= 2 else "medium",
            indicators_matched=[m["indicator"] for m in matches],
            applicable_articles=["50"],
            category="Limited Risk (Article 50)",
            description=primary["description"],
            action="allow_with_transparency",
            message=f"LIMITED-RISK: {primary['description']}",
            confidence_score=_compute_confidence_score("limited_risk", len(matches), True),
        )
    return None


def _check_policy_overrides(text: str) -> Optional[Classification]:
    """Check policy-defined force_high_risk and exempt lists.

    NOTE: This is only called for non-prohibited classifications.
    Prohibited practices CANNOT be exempted by policy — see classify().
    """
    policy = get_policy()
    rules = policy.get("rules", {})
    if not isinstance(rules, dict):
        return None
    risk_rules = rules.get("risk_classification", {})
    if not isinstance(risk_rules, dict):
        return None

    text_lower = text.lower()

    # Check exempt list
    exempt = risk_rules.get("exempt", [])
    if isinstance(exempt, list):
        for pattern in exempt:
            if isinstance(pattern, str) and pattern.lower() in text_lower:
                return Classification(
                    tier=RiskTier.MINIMAL_RISK, confidence="high",
                    indicators_matched=[], applicable_articles=[],
                    category="Policy Exempt",
                    description=f"Exempt per policy: {pattern}",
                    action="allow",
                    message=f"EXEMPT: '{pattern}' is exempt per regula-policy.yaml",
                )

    # Check force_high_risk list
    force_high = risk_rules.get("force_high_risk", [])
    if isinstance(force_high, list):
        for pattern in force_high:
            if not isinstance(pattern, str):
                continue
            normalised = pattern.lower().replace("_", " ")
            if normalised in text_lower or pattern.lower() in text_lower:
                return Classification(
                    tier=RiskTier.HIGH_RISK, confidence="high",
                    indicators_matched=[pattern],
                    applicable_articles=["9", "10", "11", "12", "13", "14", "15"],
                    category="Policy Override",
                    description=f"Forced high-risk per policy: {pattern}",
                    action="allow_with_requirements",
                    message=f"HIGH-RISK (policy override): '{pattern}' is force-classified as high-risk",
                )

    return None


def classify(text: str) -> Classification:
    """Classify text against EU AI Act risk tiers.

    Priority order (safety-first):
      1. Prohibited practices — ALWAYS checked, CANNOT be overridden by policy
      2. Policy overrides (force_high_risk, exempt)
      3. Pattern-based classification (high-risk, limited-risk, minimal-risk)
    """
    # 1. ALWAYS check prohibited first — policy cannot override Article 5
    prohibited = check_prohibited(text)
    if prohibited:
        return prohibited

    # 2. Policy overrides (only for non-prohibited classifications)
    policy_result = _check_policy_overrides(text)
    if policy_result:
        return policy_result

    # 3. Standard classification
    if not is_ai_related(text):
        return Classification(
            tier=RiskTier.NOT_AI, confidence="high",
            action="allow", message="No AI indicators detected.",
        )

    high_risk = check_high_risk(text)
    if high_risk:
        result = high_risk
    else:
        limited_risk = check_limited_risk(text)
        if limited_risk:
            result = limited_risk
        else:
            result = Classification(
                tier=RiskTier.MINIMAL_RISK, confidence="medium", action="allow",
                message="Minimal-risk AI system. No specific EU AI Act requirements.",
            )

    # Confidence threshold filtering (policy-configurable)
    policy = get_policy()
    min_conf = 0
    try:
        min_conf = int(policy.get("thresholds", {}).get("min_confidence", 0))
    except (TypeError, ValueError):
        min_conf = 0

    if min_conf > 0 and result.tier != RiskTier.PROHIBITED and result.confidence_score < min_conf:
        return Classification(
            tier=RiskTier.MINIMAL_RISK, confidence="low",
            action="allow",
            message=f"Finding suppressed (confidence {result.confidence_score} < threshold {min_conf})",
            confidence_score=result.confidence_score,
        )

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Detect EU AI Act risk indicators in AI operations"
    )
    parser.add_argument("--input", "-i", help="Text to classify")
    parser.add_argument("--file", "-f", help="File to classify")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()

    if args.file:
        text = Path(args.file).read_text(encoding="utf-8", errors="ignore")
    elif args.input:
        text = args.input
    else:
        parser.print_help()
        sys.exit(1)

    result = classify(text)
    print(result.to_json() if args.format == "json" else result.message)
    sys.exit(2 if result.tier == RiskTier.PROHIBITED else 0)


if __name__ == "__main__":
    main()
