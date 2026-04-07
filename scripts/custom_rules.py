# regula-ignore
"""Custom rule engine — load user-defined risk patterns from regula-rules.yaml.

Allows teams to define organisation-specific risk patterns that supplement
Regula's built-in patterns. Creates a defensible moat: community-contributed
rules create switching costs and network effects.

Rule file locations (checked in order):
  1. Path from --rules CLI flag
  2. ./regula-rules.yaml (project root)
  3. ~/.regula/regula-rules.yaml (user home)
"""
from pathlib import Path

try:
    import yaml
    _HAS_PYYAML = True
except ImportError:
    _HAS_PYYAML = False


_EMPTY_RULES = {
    "prohibited": [],
    "high_risk": [],
    "limited_risk": [],
    "ai_indicators": [],
}


def _parse_yaml(text: str) -> dict:
    """Parse YAML text, using pyyaml if available."""
    if _HAS_PYYAML:
        return yaml.safe_load(text) or {}
    # Minimal fallback — import the project's own fallback parser
    from policy_config import _parse_yaml_fallback
    return _parse_yaml_fallback(text)


def _find_rules_file() -> str | None:
    """Search default locations for a regula-rules.yaml file."""
    # 1. Project root (cwd)
    cwd_path = Path.cwd() / "regula-rules.yaml"
    if cwd_path.is_file():
        return str(cwd_path)

    # 2. User home
    home_path = Path.home() / ".regula" / "regula-rules.yaml"
    if home_path.is_file():
        return str(home_path)

    return None


def load_custom_rules(path: str = None) -> dict:
    """Load custom rules from a YAML file.

    Args:
        path: Explicit path to a rules file. If None, searches default
              locations (./regula-rules.yaml, ~/.regula/regula-rules.yaml).

    Returns:
        {
            "prohibited": [{"name": str, "patterns": [str], "description": str, "article": str}],
            "high_risk": [{"name": str, "patterns": [str], "description": str, "articles": [str], "category": str}],
            "limited_risk": [{"name": str, "patterns": [str], "description": str}],
            "ai_indicators": [str],
        }

    Returns empty dict structure if no file found (not an error).
    """
    if path is None:
        path = _find_rules_file()
    if path is None:
        return dict(_EMPTY_RULES)

    try:
        content = Path(path).read_text(encoding="utf-8")
    except (OSError, IOError):
        return dict(_EMPTY_RULES)

    data = _parse_yaml(content)
    if not isinstance(data, dict):
        return dict(_EMPTY_RULES)

    rules = data.get("rules", {})
    if not isinstance(rules, dict):
        return dict(_EMPTY_RULES)

    result = {
        "prohibited": [],
        "high_risk": [],
        "limited_risk": [],
        "ai_indicators": [],
    }

    # Validate and load each section
    for rule in rules.get("prohibited", []) or []:
        if isinstance(rule, dict) and "patterns" in rule:
            result["prohibited"].append({
                "name": rule.get("name", "custom_prohibited"),
                "patterns": rule["patterns"],
                "description": rule.get("description", "Custom prohibited rule"),
                "article": rule.get("article", "5"),
            })

    for rule in rules.get("high_risk", []) or []:
        if isinstance(rule, dict) and "patterns" in rule:
            result["high_risk"].append({
                "name": rule.get("name", "custom_high_risk"),
                "patterns": rule["patterns"],
                "description": rule.get("description", "Custom high-risk rule"),
                "articles": rule.get("articles", ["6"]),
                "category": rule.get("category", "Custom High-Risk"),
            })

    for rule in rules.get("limited_risk", []) or []:
        if isinstance(rule, dict) and "patterns" in rule:
            result["limited_risk"].append({
                "name": rule.get("name", "custom_limited_risk"),
                "patterns": rule["patterns"],
                "description": rule.get("description", "Custom limited-risk rule"),
            })

    indicators = rules.get("ai_indicators", []) or []
    if isinstance(indicators, list):
        result["ai_indicators"] = [str(i) for i in indicators if i]

    return result
