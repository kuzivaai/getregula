# regula-ignore
#!/usr/bin/env python3
"""
Regula Doctor — Installation health checks.

Validates environment, dependencies, policy, and security configuration.
"""

import json
import os
import sys
from pathlib import Path


def _check_python_version():
    """Check Python version >= 3.10."""
    v = sys.version_info
    version_str = f"{v.major}.{v.minor}.{v.micro}"
    if v >= (3, 10):
        return {"name": "Python version", "status": "PASS",
                "detail": f"Python {version_str} (>= 3.10 required)"}
    return {"name": "Python version", "status": "FAIL",
            "detail": f"Python {version_str} (>= 3.10 required)"}


def _check_optional_dep(module_name, install_hint):
    """Check if an optional dependency is importable.

    Optional dependencies fall back to INFO when missing, not WARN.
    Reason: a fresh `pip install regula-ai` does not pull in optional
    extras. Showing those as WARN made first-run users see "5 warnings"
    on a perfectly healthy install and assume something was broken.
    INFO communicates "this feature is available if you want it" which
    matches the actual state.
    """
    try:
        __import__(module_name)
        return {"name": f"{module_name}", "status": "PASS",
                "detail": f"{module_name} installed"}
    except ImportError:
        return {"name": f"{module_name}", "status": "INFO",
                "detail": f"{module_name} optional — install with: {install_hint}"}


def _check_policy_file():
    """Check if a policy file exists and is readable."""
    candidates = []
    env_path = os.environ.get("REGULA_POLICY")
    if env_path:
        candidates.append(Path(env_path))
    candidates.append(Path.cwd() / "regula-policy.yaml")
    candidates.append(Path.cwd() / "regula-policy.json")
    # After the IA restructure, Regula's own policy lives under configs/.
    candidates.append(Path.cwd() / "configs" / "regula-policy.yaml")
    candidates.append(Path.cwd() / "configs" / "regula-policy.json")
    candidates.append(Path.home() / ".regula" / "regula-policy.yaml")
    candidates.append(Path.home() / ".regula" / "regula-policy.json")

    for p in candidates:
        if p.exists():
            if os.access(p, os.R_OK):
                return {"name": "Policy file", "status": "PASS",
                        "detail": f"Found and readable: {p}"}
            else:
                return {"name": "Policy file", "status": "FAIL",
                        "detail": f"Found but not readable: {p}"}

    return {"name": "Policy file", "status": "INFO",
            "detail": "No policy file found (using defaults). Run 'regula init' to create one."}


def _check_audit_directory():
    """Check if audit directory is writable."""
    audit_dir = Path.home() / ".regula" / "audit"
    if audit_dir.exists():
        if os.access(audit_dir, os.W_OK):
            return {"name": "Audit directory", "status": "PASS",
                    "detail": f"Writable: {audit_dir}"}
        else:
            return {"name": "Audit directory", "status": "FAIL",
                    "detail": f"Not writable: {audit_dir}"}
    else:
        # Try to create it
        try:
            audit_dir.mkdir(parents=True, exist_ok=True)
            return {"name": "Audit directory", "status": "PASS",
                    "detail": f"Created: {audit_dir}"}
        except OSError as e:
            return {"name": "Audit directory", "status": "FAIL",
                    "detail": f"Cannot create {audit_dir}: {e}"}


def _check_hooks():
    """Detect hooks in common AI coding assistant directories."""
    hook_dirs = [
        (Path.cwd() / ".claude" / "hooks", "Claude Code"),
        (Path.cwd() / ".cursor", "Cursor"),
        (Path.cwd() / ".windsurf", "Windsurf"),
    ]
    found = []
    for d, name in hook_dirs:
        if d.exists():
            found.append(name)

    if found:
        return {"name": "Hooks detected", "status": "PASS",
                "detail": f"Found: {', '.join(found)}"}
    return {"name": "Hooks detected", "status": "INFO",
            "detail": "No hooks installed. Run 'regula install <platform>' to set up."}


def _check_config_validation():
    """Validate policy config has ai_officer if policy exists."""
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from classify_risk import get_policy
        policy = get_policy()
        if not policy:
            return {"name": "Config validation", "status": "INFO",
                    "detail": "No policy loaded (using defaults)"}
        governance = policy.get("governance", {}) or {}
        # Support both the historical `contacts.ai_officer` nesting and
        # the flat `governance.ai_officer` schema used by the current
        # policy template.
        ai_officer = (
            governance.get("contacts", {}).get("ai_officer")
            or governance.get("ai_officer")
        )
        # Treat a dict with at least a non-empty `name` as "defined"
        if isinstance(ai_officer, dict):
            defined = bool((ai_officer.get("name") or "").strip())
        else:
            defined = bool(ai_officer)
        if defined:
            return {"name": "Config validation", "status": "PASS",
                    "detail": "ai_officer defined in policy"}
        return {"name": "Config validation", "status": "INFO",
                "detail": "ai_officer not defined in policy (recommended for Article 4)"}
    except Exception as e:
        return {"name": "Config validation", "status": "WARN",
                "detail": f"Could not validate config: {e}"}


def _check_security():
    """Check .gitignore includes audit patterns, files not world-readable.

    Only WARN about a missing .gitignore when the cwd is actually inside
    a git repository — otherwise the recommendation is moot and shows
    up as a false-positive warning on fresh non-git directories.
    """
    issues = []
    audit_patterns = [".regula/", ".regula/audit", "regula-audit"]

    # Walk up looking for a .git/ directory; cap at filesystem root.
    in_git_repo = False
    cur = Path.cwd().resolve()
    for _ in range(20):
        if (cur / ".git").exists():
            in_git_repo = True
            break
        if cur.parent == cur:
            break
        cur = cur.parent

    gitignore = Path.cwd() / ".gitignore"
    if gitignore.exists():
        try:
            content = gitignore.read_text(encoding="utf-8", errors="ignore")
            has_pattern = any(p in content for p in audit_patterns)
            if not has_pattern:
                issues.append("audit patterns not in .gitignore")
        except OSError:
            issues.append("cannot read .gitignore")
    elif in_git_repo:
        # Only complain if we're actually in a git repo.
        issues.append(".gitignore not found")

    if issues:
        return {"name": "Security", "status": "WARN",
                "detail": "; ".join(issues)}
    if not in_git_repo:
        return {"name": "Security", "status": "INFO",
                "detail": "Not inside a git repository — .gitignore check skipped"}
    return {"name": "Security", "status": "PASS",
            "detail": "Audit patterns in .gitignore, no world-readable policy files"}


def _check_telemetry():
    """Check telemetry consent status and DSN configuration."""
    try:
        from telemetry import get_consent, dsn_is_configured
        consent = get_consent()
        dsn_ok = dsn_is_configured()

        if consent is None:
            return {"name": "Telemetry", "status": "INFO",
                    "detail": "Not yet configured — run 'regula telemetry enable|disable'"}
        if consent and not dsn_ok:
            return {"name": "Telemetry", "status": "INFO",
                    "detail": "Consent is enabled, no crash-reporting backend configured (self-hosted deployment). "
                              "Optional: set _SENTRY_DSN in scripts/telemetry.py to receive crash reports."}
        if consent and dsn_ok:
            return {"name": "Telemetry", "status": "PASS",
                    "detail": "Enabled — anonymous crash reports active"}
        return {"name": "Telemetry", "status": "INFO",
                "detail": "Disabled — run 'regula telemetry enable' to opt in"}
    except Exception as exc:
        return {"name": "Telemetry", "status": "WARN",
                "detail": f"Could not check telemetry: {exc}"}


def _check_domain_declaration():
    """Suggest domain declaration for domain-gated high-risk patterns."""
    try:
        policy_path = Path(__file__).parent.parent / "regula-policy.yaml"
        if policy_path.exists():
            try:
                import yaml
                data = yaml.safe_load(policy_path.read_text(encoding="utf-8")) or {}
                system = data.get("system", {})
                if system.get("domain"):
                    return {"name": "Domain", "status": "PASS",
                            "detail": f"Domain declared: {system['domain']}"}
            except (ImportError, ValueError, KeyError, TypeError):
                pass
        return {"name": "Domain", "status": "INFO",
                "detail": "No domain declared. Use --domain or set system.domain in regula-policy.yaml "
                          "to activate domain-specific high-risk patterns (e.g. employment, medical)"}
    except Exception as exc:
        return {"name": "Domain", "status": "INFO",
                "detail": f"Could not check domain declaration: {exc}"}


def run_doctor(format_type="text"):
    """Run all health checks.

    Returns:
        dict with keys: healthy (bool), checks (list of check dicts),
        summary (dict with pass/warn/fail counts).
    """
    checks = [
        _check_python_version(),
        _check_optional_dep("yaml", "pip install regula[yaml]"),
        _check_optional_dep("tree_sitter", "pip install regula[ast]"),
        _check_optional_dep("tree_sitter_javascript", "pip install regula[ast]"),
        _check_optional_dep("tree_sitter_typescript", "pip install regula[ast]"),
        _check_policy_file(),
        _check_audit_directory(),
        _check_hooks(),
        _check_config_validation(),
        _check_security(),
        _check_telemetry(),
        _check_domain_declaration(),
    ]

    pass_count = sum(1 for c in checks if c["status"] == "PASS")
    info_count = sum(1 for c in checks if c["status"] == "INFO")
    warn_count = sum(1 for c in checks if c["status"] == "WARN")
    fail_count = sum(1 for c in checks if c["status"] == "FAIL")
    healthy = fail_count == 0

    result = {
        "healthy": healthy,
        "checks": checks,
        "summary": {
            "passed": pass_count,
            "info": info_count,
            "warnings": warn_count,
            "failures": fail_count,
        },
    }

    if format_type == "text":
        _print_text(checks, pass_count, info_count, warn_count, fail_count)

    return result if format_type == "json" else healthy


def _print_text(checks, pass_count, info_count, warn_count, fail_count):
    """Print human-readable doctor output."""
    print("\nRegula Doctor\n")
    for c in checks:
        status = c["status"]
        if status == "PASS":
            label = "  PASS "
        elif status == "INFO":
            label = "  INFO "
        elif status == "WARN":
            label = "  WARN "
        else:
            label = "  FAIL "
        print(f"  {label} {c['detail']}")
    parts = [f"{pass_count} passed"]
    if info_count:
        parts.append(f"{info_count} info")
    if warn_count:
        parts.append(f"{warn_count} warnings")
    if fail_count:
        parts.append(f"{fail_count} failures")
    print(f"\n{', '.join(parts)}\n")
