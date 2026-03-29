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
    ISO_42001_MAP, GOVERNANCE_OBSERVATIONS, BIAS_RISK_PATTERNS,
)

# Policy configuration
from policy_config import (
    get_policy, get_governance_contacts, get_regulatory_basis,
    _parse_yaml_fallback,
)


# ---------------------------------------------------------------------------
# Pre-compiled pattern caches
#
# All hot-path classification functions use these instead of calling
# re.compile() on every invocation. Patterns used against text.lower()
# are compiled without IGNORECASE; patterns used on raw text use IGNORECASE.
# ---------------------------------------------------------------------------
_PROHIBITED_COMPILED = {
    name: [re.compile(p) for p in cfg["patterns"]]
    for name, cfg in PROHIBITED_PATTERNS.items()
}
_HIGH_RISK_COMPILED = {
    name: [re.compile(p) for p in cfg["patterns"]]
    for name, cfg in HIGH_RISK_PATTERNS.items()
}
_LIMITED_RISK_COMPILED = {
    name: [re.compile(p) for p in cfg["patterns"]]
    for name, cfg in LIMITED_RISK_PATTERNS.items()
}
_AI_INDICATORS_COMPILED = {
    cat: [re.compile(p) for p in patterns]
    for cat, patterns in AI_INDICATORS.items()
}
_GOVERNANCE_COMPILED = {
    name: [re.compile(p) for p in cfg["patterns"]]
    for name, cfg in GOVERNANCE_OBSERVATIONS.items()
}
_BIAS_RISK_COMPILED = {
    name: [re.compile(p, re.IGNORECASE) for p in cfg["patterns"]]
    for name, cfg in BIAS_RISK_PATTERNS.items()
}
_AI_SECURITY_COMPILED = {
    name: [re.compile(p, re.IGNORECASE) for p in cfg["patterns"]]
    for name, cfg in AI_SECURITY_PATTERNS.items()
}
_GPAI_TRAINING_COMPILED = [re.compile(p, re.IGNORECASE) for p in GPAI_TRAINING_PATTERNS]

# ---------------------------------------------------------------------------
# Confidence score constants
#
# Base scores reflect tier-level certainty without context. Calibrated
# against the pattern library: prohibited patterns are tightly scoped
# (high base), high-risk patterns match broad categories (lower base).
# Match bonus: +8 per corroborating indicator, capped at 15 (diminishing
# returns after 2 matches). AI context bonus: +10 when code imports
# AI libraries, disambiguating mentions in docs or comments.
# ---------------------------------------------------------------------------
_CONFIDENCE_BASE = {
    "prohibited": 75,       # Article 5 — tightly scoped prohibited practices
    "high_risk": 55,        # Annex III — broad category, context-dependent
    "limited_risk": 40,     # Article 50 — transparency markers; often in docs
    "minimal_risk": 15,     # Lowest-signal tier
}
_CONFIDENCE_DEFAULT_BASE = 10
_CONFIDENCE_MATCH_BONUS_PER = 8     # per additional corroborating indicator
_CONFIDENCE_MATCH_BONUS_MAX = 15    # cap after ~2 matches
_CONFIDENCE_AI_CONTEXT_BONUS = 10   # when code imports AI libraries
_CONFIDENCE_MAX = 100

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

    for name, compiled_patterns in _AI_SECURITY_COMPILED.items():
        config = AI_SECURITY_PATTERNS[name]
        for rx in compiled_patterns:
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

                if rx.search(line):
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
    return any(rx.search(text) for rx in _GPAI_TRAINING_COMPILED)


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

    for name, compiled_patterns in _GOVERNANCE_COMPILED.items():
        config = GOVERNANCE_OBSERVATIONS[name]
        found = any(rx.search(text_lower) for rx in compiled_patterns)

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


def check_bias_risk(text: str) -> list:
    """Detect protected class attributes used as ML features.

    Returns a list of observation dicts (article + observation).
    Only meaningful for code that also has AI indicators.

    Limitation: this is a static pattern check. It can detect whether
    protected attributes appear in ML code and whether fairness evaluation
    is absent. It cannot determine whether a model is actually biased.
    """
    observations = []
    text_lower = text.lower()

    # Check for protected class feature usage
    feature_patterns = _BIAS_RISK_COMPILED.get("protected_class_as_feature", [])
    has_protected_feature = any(rx.search(text_lower) for rx in feature_patterns)

    if has_protected_feature:
        cfg = BIAS_RISK_PATTERNS["protected_class_as_feature"]
        observations.append({
            "article": cfg["article"],
            "observation": cfg["observation"],
        })

        # Only check for missing fairness eval when protected features found
        fairness_patterns = _BIAS_RISK_COMPILED.get("missing_fairness_evaluation", [])
        has_fairness_eval = any(rx.search(text_lower) for rx in fairness_patterns)
        if not has_fairness_eval:
            cfg2 = BIAS_RISK_PATTERNS["missing_fairness_evaluation"]
            observations.append({
                "article": cfg2["article"],
                "observation": cfg2["absence_observation"],
            })

    return observations


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def _compute_confidence_score(tier: str, num_matches: int, has_ai_indicator: bool) -> int:
    """Compute a 0-100 confidence score based on tier, match count, and AI context.

    See _CONFIDENCE_BASE and related constants above for calibration rationale.
    """
    base = _CONFIDENCE_BASE.get(tier, _CONFIDENCE_DEFAULT_BASE)
    match_bonus = min(num_matches * _CONFIDENCE_MATCH_BONUS_PER, _CONFIDENCE_MATCH_BONUS_MAX)
    ai_bonus = _CONFIDENCE_AI_CONTEXT_BONUS if has_ai_indicator else 0
    return min(base + match_bonus + ai_bonus, _CONFIDENCE_MAX)


# ---------------------------------------------------------------------------
# Core classification functions
# ---------------------------------------------------------------------------

def is_ai_related(text: str) -> bool:
    text_lower = text.lower()
    for compiled_patterns in _AI_INDICATORS_COMPILED.values():
        for rx in compiled_patterns:
            if rx.search(text_lower):
                return True
    return False


def check_prohibited(text: str) -> Optional[Classification]:
    text_lower = text.lower()
    matches = []
    for name, compiled_patterns in _PROHIBITED_COMPILED.items():
        for rx in compiled_patterns:
            if rx.search(text_lower):
                matches.append(PROHIBITED_PATTERNS[name] | {"indicator": name})
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
    for name, compiled_patterns in _HIGH_RISK_COMPILED.items():
        for rx in compiled_patterns:
            if rx.search(text_lower):
                matches.append(HIGH_RISK_PATTERNS[name] | {"indicator": name})
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
    for name, compiled_patterns in _LIMITED_RISK_COMPILED.items():
        for rx in compiled_patterns:
            if rx.search(text_lower):
                matches.append(LIMITED_RISK_PATTERNS[name] | {"indicator": name})
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
