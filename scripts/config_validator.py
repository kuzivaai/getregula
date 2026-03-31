# regula-ignore
"""Config file validator for Regula policy files (regula-policy.yaml/json).

Validates structure, threshold logic, and governance completeness.
"""

import json
import os
from pathlib import Path


VALID_FRAMEWORKS = {"eu_ai_act", "iso_42001", "nist_ai_rmf", "owasp_llm_top10", "iso_27001"}


def _discover_config_path() -> Path | None:
    """Discover config file using same search order as policy_config.py."""
    candidates = []
    env_path = os.environ.get("REGULA_POLICY")
    if env_path:
        candidates.append(Path(env_path))
    candidates.append(Path.cwd() / "regula-policy.yaml")
    candidates.append(Path.cwd() / "regula-policy.json")
    candidates.append(Path.home() / ".regula" / "regula-policy.yaml")
    candidates.append(Path.home() / ".regula" / "regula-policy.json")
    for p in candidates:
        if p.exists():
            return p
    return None


def _parse_config(path: Path) -> tuple[dict | None, str | None]:
    """Parse YAML or JSON config. Returns (data, error_message)."""
    content = path.read_text(encoding="utf-8")
    if path.suffix == ".json":
        try:
            return json.loads(content), None
        except json.JSONDecodeError as e:
            return None, f"JSON parse error: {e}"
    # YAML
    try:
        import yaml
        data = yaml.safe_load(content)
        return (data or {}), None
    except ImportError:
        pass
    except Exception as e:
        return None, f"YAML parse error: {e}"
    # Fallback: try json anyway (handles .yaml files that are valid JSON)
    try:
        return json.loads(content), None
    except Exception:
        pass
    # Last resort: minimal YAML-subset parser (same approach as policy_config.py)
    try:
        import sys
        from pathlib import Path as _Path
        scripts_dir = _Path(__file__).parent
        if str(scripts_dir) not in sys.path:
            sys.path.insert(0, str(scripts_dir))
        from policy_config import _parse_yaml_fallback
        return _parse_yaml_fallback(content), None
    except Exception as e:
        return None, f"YAML parse error (fallback): {e}"


def validate_config(path: str | None = None, format_type: str = "text") -> dict:
    """
    Validate a Regula policy config file.

    Args:
        path: path to config file, or None to auto-discover.
        format_type: "text" prints human-readable output; "silent" returns dict only;
                     "json" is handled by the CLI layer (same as "silent" here).

    Returns:
        {
            "valid": bool,
            "path": str | None,
            "errors": list[str],
            "warnings": list[str],
        }
    """
    errors: list[str] = []
    warnings: list[str] = []
    resolved_path: str | None = None

    # --- Resolve path ---
    if path is not None:
        config_path = Path(path)
        if not config_path.exists():
            errors.append(f"Config file not found: {path}")
            result = {"valid": False, "path": path, "errors": errors, "warnings": warnings}
            if format_type == "text":
                _print_result(result)
            return result
        resolved_path = str(config_path.resolve())
    else:
        discovered = _discover_config_path()
        if discovered is None:
            result = {
                "valid": True,
                "path": None,
                "errors": [],
                "warnings": ["No policy file found. Run 'regula init' to create one."],
            }
            if format_type == "text":
                _print_result(result)
            return result
        config_path = discovered
        resolved_path = str(config_path.resolve())

    # --- Parse ---
    data, parse_error = _parse_config(config_path)
    if parse_error is not None:
        errors.append(parse_error)
        result = {"valid": False, "path": resolved_path, "errors": errors, "warnings": warnings}
        if format_type == "text":
            _print_result(result)
        return result

    if data is None:
        data = {}

    # --- Validate version ---
    version = data.get("version")
    version_ok = bool(version)

    # --- Validate governance ---
    governance = data.get("governance", {})
    ai_officer = governance.get("ai_officer", {}) if isinstance(governance, dict) else {}
    ai_officer_defined = bool(ai_officer)
    ai_officer_name = ai_officer.get("name", "") if isinstance(ai_officer, dict) else ""
    ai_officer_name_empty = not bool(ai_officer_name)

    if ai_officer_name_empty:
        warnings.append(
            "governance.ai_officer.name is empty (EU AI Act Article 4 recommends a named person)"
        )

    # --- Validate thresholds ---
    thresholds = data.get("thresholds", {}) if isinstance(data.get("thresholds"), dict) else {}
    block_above = thresholds.get("block_above")
    warn_above = thresholds.get("warn_above")

    block_above_valid = True
    warn_above_valid = True

    if block_above is not None:
        if isinstance(block_above, bool) or not isinstance(block_above, int) or not (0 <= block_above <= 100):
            errors.append(
                f"thresholds.block_above ({block_above!r}) must be an integer 0-100"
            )
            block_above_valid = False
    else:
        warnings.append("thresholds.block_above missing (will use default: 80)")

    if warn_above is not None:
        if isinstance(warn_above, bool) or not isinstance(warn_above, int) or not (0 <= warn_above <= 100):
            errors.append(
                f"thresholds.warn_above ({warn_above!r}) must be an integer 0-100"
            )
            warn_above_valid = False

    if (
        block_above is not None and warn_above is not None
        and block_above_valid and warn_above_valid
        and warn_above >= block_above
    ):
        errors.append(
            f"thresholds.warn_above ({warn_above}) >= block_above ({block_above}) "
            f"— no findings would be shown"
        )

    # --- Validate frameworks ---
    frameworks = data.get("frameworks", [])
    if isinstance(frameworks, list):
        for fw in frameworks:
            if fw not in VALID_FRAMEWORKS:
                warnings.append(
                    f"frameworks contains unrecognised value: {fw!r} "
                    f"(valid: {', '.join(sorted(VALID_FRAMEWORKS))})"
                )

    # --- Version warning ---
    if not version_ok:
        warnings.append("version field missing")

    valid = len(errors) == 0
    result = {
        "valid": valid,
        "path": resolved_path,
        "errors": errors,
        "warnings": warnings,
        # extra context for text output
        "_version": version,
        "_ai_officer_defined": ai_officer_defined,
        "_ai_officer_name_empty": ai_officer_name_empty,
        "_block_above": block_above,
        "_warn_above": warn_above,
    }

    if format_type == "text":
        _print_result(result)

    # Strip internal keys before returning
    return {k: v for k, v in result.items() if not k.startswith("_")}


def _print_result(result: dict) -> None:
    """Print human-readable validation output."""
    print("\nRegula Config Validate\n")

    path = result.get("path")
    if path:
        print(f"  File: {path}\n")
    else:
        print("  File: (none found)\n")

    # Per-check lines (only when we have parsed data — no errors from parse/not-found)
    if not result["errors"] or all("not found" not in e and "parse error" not in e.lower() for e in result["errors"]):
        version = result.get("_version")
        ai_officer_defined = result.get("_ai_officer_defined", False)
        ai_officer_name_empty = result.get("_ai_officer_name_empty", True)
        block_above = result.get("_block_above")
        warn_above = result.get("_warn_above")

        if version:
            print(f'  PASS  version: "{version}"')
        # Only print governance line if we have something to say
        if ai_officer_defined and not ai_officer_name_empty:
            print("  PASS  governance.ai_officer: defined")
        elif ai_officer_defined and ai_officer_name_empty:
            print("  PASS  governance.ai_officer: defined")
            print("  WARN  governance.ai_officer.name is empty (EU AI Act Article 4 recommends a named person)")
        else:
            pass  # Covered by warnings list

        if block_above is not None and warn_above is not None:
            threshold_error = any("warn_above" in e and ">=" in e for e in result["errors"])
            if threshold_error:
                print(f"  ERROR  thresholds.warn_above ({warn_above}) >= block_above ({block_above}) — no findings would be shown")
            else:
                print(f"  PASS  thresholds: block_above={block_above}, warn_above={warn_above}")
        elif block_above is not None:
            print(f"  PASS  thresholds: block_above={block_above}")
        elif warn_above is not None:
            print(f"  WARN  thresholds.block_above missing (will use default: 80)")

    # Errors (non-threshold ones)
    for e in result["errors"]:
        if "warn_above" not in e or ">=" not in e:
            print(f"  ERROR  {e}")

    # Warnings
    for w in result["warnings"]:
        already_printed = (
            "ai_officer.name is empty" in w and result.get("_ai_officer_name_empty")
        )
        if not already_printed:
            print(f"  WARN  {w}")

    print()
    n_errors = len(result["errors"])
    n_warnings = len(result["warnings"])
    print(f"  {n_warnings} warning(s), {n_errors} error(s)")
    if result["valid"]:
        print("  Config is valid.")
    else:
        print("  Config is invalid.")
    print()
