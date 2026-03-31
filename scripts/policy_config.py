# regula-ignore
"""Policy configuration loading and management for Regula.

Loads regula-policy.yaml/json from standard locations, provides cached
access to policy values, governance contacts, and regulatory basis.
"""

import json
import os
import re
from pathlib import Path
from degradation import check_optional


def _load_policy() -> dict:
    """Load policy configuration. Tries YAML (via pyyaml) then JSON fallback."""
    candidates = []
    env_path = os.environ.get("REGULA_POLICY")
    if env_path:
        candidates.append(Path(env_path))
    candidates.append(Path.cwd() / "regula-policy.yaml")
    candidates.append(Path.cwd() / "regula-policy.json")
    candidates.append(Path.home() / ".regula" / "regula-policy.yaml")
    candidates.append(Path.home() / ".regula" / "regula-policy.json")

    for path in candidates:
        if not path.exists():
            continue
        try:
            content = path.read_text(encoding="utf-8")
            if path.suffix == ".json":
                return json.loads(content)
            # YAML: try pyyaml first, then safe fallback
            if check_optional("yaml", "using fallback YAML parser", "pip install pyyaml"):
                import yaml
                return yaml.safe_load(content) or {}
            else:
                return _parse_yaml_fallback(content)
        except Exception:
            continue
    return {}


def _parse_yaml_fallback(text: str) -> dict:
    """
    Minimal YAML-subset parser used ONLY when pyyaml is not installed.
    Handles the specific structure of regula-policy.yaml: scalar values,
    inline lists, and up to 3 levels of nesting.

    This is NOT a general YAML parser. Install pyyaml for full support.
    """
    result = {}
    stack = [result]  # stack of current dict context
    indent_stack = [-1]  # indentation levels

    for line in text.split("\n"):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        indent = len(line) - len(line.lstrip())

        # Pop stack to correct level
        while len(indent_stack) > 1 and indent <= indent_stack[-1]:
            indent_stack.pop()
            stack.pop()

        current = stack[-1]

        # List item
        if stripped.startswith("- "):
            item = stripped[2:].strip().strip('"').strip("'")
            if isinstance(current, list):
                current.append(item)
            continue

        # Key-value
        if ":" in stripped:
            key, _, val = stripped.partition(":")
            key = key.strip()
            val = val.strip()

            if not val:
                # New dict section
                new_dict = {}
                if isinstance(current, dict):
                    current[key] = new_dict
                    stack.append(new_dict)
                    indent_stack.append(indent)
            elif val.startswith("["):
                # Inline list
                items = re.findall(r'["\']?([^"\',\[\]]+)["\']?', val)
                if isinstance(current, dict):
                    current[key] = [i.strip() for i in items if i.strip()]
            else:
                # Scalar value — strip inline comments first
                if "#" in val and not val.startswith('"') and not val.startswith("'"):
                    val = val[:val.index("#")]
                val = val.strip().strip('"').strip("'")
                if val.lower() == "true":
                    val = True
                elif val.lower() == "false":
                    val = False
                elif val.isdigit():
                    val = int(val)
                if isinstance(current, dict):
                    current[key] = val

    return result


_POLICY = _load_policy()


def get_policy() -> dict:
    return _POLICY


def get_governance_contacts() -> dict:
    """Return the governance contacts from policy (AI Officer, DPO)."""
    policy = get_policy()
    governance = policy.get("governance", {})
    if not isinstance(governance, dict):
        return {}
    return governance


def get_regulatory_basis() -> dict:
    """Return the regulatory basis from policy (version pinning for auditors)."""
    policy = get_policy()
    basis = policy.get("regulatory_basis", {})
    if not isinstance(basis, dict):
        return {}
    return basis
