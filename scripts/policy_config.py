# regula-ignore
"""Policy configuration loading and management for Regula.

Loads regula-policy.yaml/json from standard locations, provides cached
access to policy values, governance contacts, and regulatory basis.
"""

__all__ = [
    "get_policy", "get_governance_contacts", "get_regulatory_basis",
    "get_policy_parse_error",
]

import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from degradation import check_optional

# Set to (path_str, error_str) when a policy file is found but fails to parse.
# None means no parse error has occurred.
_POLICY_PARSE_ERROR = None


def get_policy_parse_error():
    """Return the parse error tuple (path, error) or None if no error occurred.

    Callers (e.g. the doctor command) can use this to surface a clear
    warning when a policy file was found but could not be loaded.
    """
    return _POLICY_PARSE_ERROR


def _load_policy() -> dict:
    """Load policy configuration. Tries YAML (via pyyaml) then JSON fallback."""
    global _POLICY_PARSE_ERROR

    candidates = []
    env_path = os.environ.get("REGULA_POLICY")
    if env_path:
        candidates.append(Path(env_path))
    candidates.append(Path.cwd() / "regula-policy.yaml")
    candidates.append(Path.cwd() / "regula-policy.json")
    # After the IA restructure, Regula's own policy lives under configs/.
    # User projects keep their policy at project root — this is additive.
    candidates.append(Path.cwd() / "configs" / "regula-policy.yaml")
    candidates.append(Path.cwd() / "configs" / "regula-policy.json")
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
        except Exception as e:
            _POLICY_PARSE_ERROR = (str(path), str(e))
            print(
                f"regula: WARNING — policy file {path} exists but failed to parse: {e}. "
                "Running with default settings.",
                file=sys.stderr,
            )
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
            item_text = stripped[2:].strip()
            # Flow mapping in list: - {key: val, key2: val2}
            if item_text.startswith("{") and item_text.endswith("}"):
                flow_dict = _parse_flow_mapping(item_text)
                if isinstance(current, list):
                    current.append(flow_dict)
                elif isinstance(current, dict):
                    # Parent expected a dict but got list items — find the
                    # last key added and convert its value to a list
                    parent = stack[-2] if len(stack) > 1 else None
                    if parent and isinstance(parent, dict):
                        for k in reversed(list(parent.keys())):
                            if parent[k] is current:
                                parent[k] = [flow_dict]
                                stack[-1] = parent[k]
                                break
            else:
                item = item_text.strip('"').strip("'")
                if isinstance(current, list):
                    current.append(item)
                elif isinstance(current, dict):
                    # Parent expected a dict but got list items — convert
                    parent = stack[-2] if len(stack) > 1 else None
                    if parent and isinstance(parent, dict):
                        for k in reversed(list(parent.keys())):
                            if parent[k] is current:
                                parent[k] = [item]
                                stack[-1] = parent[k]
                                break
            continue

        # Key-value
        if ":" in stripped:
            key, _, val = stripped.partition(":")
            key = key.strip()
            val = val.strip()

            if not val:
                # New dict section (may be converted to list if followed by - items)
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
                val = val.strip()
                # Quoted values stay as strings — no numeric coercion
                was_quoted = (val.startswith('"') and val.endswith('"')) or \
                             (val.startswith("'") and val.endswith("'"))
                val = val.strip('"').strip("'")
                if not was_quoted:
                    if val.lower() == "true":
                        val = True
                    elif val.lower() == "false":
                        val = False
                    elif val.isdigit():
                        val = int(val)
                    else:
                        try:
                            val = float(val)
                        except ValueError:
                            pass
                if isinstance(current, dict):
                    current[key] = val

    return result


def _parse_flow_mapping(text: str) -> dict:
    """Parse a YAML flow mapping like {key: val, key2: val2} into a dict.

    Handles quoted values and nested colons in values.
    Values remain as strings — no numeric coercion, since flow mappings
    are used for obligation dicts where article references must stay strings.
    """
    result = {}
    inner = text.strip().strip("{}").strip()
    if not inner:
        return result
    # Split on commas not inside quotes
    parts = re.split(r',\s*(?=(?:[^"]*"[^"]*")*[^"]*$)', inner)
    for part in parts:
        part = part.strip()
        if ":" not in part:
            continue
        k, _, v = part.partition(":")
        k = k.strip().strip('"').strip("'")
        v = v.strip().strip('"').strip("'")
        if v.lower() == "true":
            v = True
        elif v.lower() == "false":
            v = False
        # No numeric coercion — article refs like "9", "6-1-1702" must stay strings
        result[k] = v
    return result


_POLICY = _load_policy()


def get_policy(path: str = None) -> dict:
    """Return the cached policy, or load from a specific path if given.

    The path parameter exists for testability — callers can inject a
    different policy file without monkeypatching module state.
    """
    if path is not None:
        return _load_policy_from(path)
    return _POLICY


def _load_policy_from(path: str) -> dict:
    """Load policy from a specific file path."""
    global _POLICY_PARSE_ERROR

    p = Path(path)
    if not p.exists():
        return {}
    try:
        content = p.read_text(encoding="utf-8")
        if p.suffix == ".json":
            return json.loads(content)
        if check_optional("yaml", "using fallback YAML parser", "pip install pyyaml"):
            import yaml
            return yaml.safe_load(content) or {}
        else:
            return _parse_yaml_fallback(content)
    except Exception as e:
        _POLICY_PARSE_ERROR = (str(p), str(e))
        print(
            f"regula: WARNING — policy file {p} exists but failed to parse: {e}. "
            "Running with default settings.",
            file=sys.stderr,
        )
        return {}


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
