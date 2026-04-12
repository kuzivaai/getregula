#!/usr/bin/env python3
"""
Regula Multi-Platform Installer

Generates platform-specific configuration to enable Regula hooks across
AI coding assistants and development tools.

Supported platforms:
  claude-code  - Claude Code PreToolUse/PostToolUse hooks
  copilot-cli  - GitHub Copilot CLI hooks (GA Feb 2026)
  windsurf     - Windsurf Cascade hooks
  pre-commit   - pre-commit framework hook
  git-hooks    - Direct git pre-commit hook
"""

import argparse
import json
import stat
import sys
from pathlib import Path


def _find_regula_root() -> Path:
    """Find the Regula installation directory."""
    # Check if we're running from the source tree
    script_dir = Path(__file__).parent.resolve()
    if (script_dir.parent / "SKILL.md").exists():
        return script_dir.parent

    # Check common install locations
    for candidate in [
        Path.home() / ".claude" / "skills" / "regula",
        Path.cwd(),
    ]:
        if (candidate / "SKILL.md").exists():
            return candidate

    return script_dir.parent


def _find_python() -> str:
    """Find the Python executable path."""
    return sys.executable or "python3"


def install_claude_code(regula_root: Path, project_dir: Path) -> None:
    """Generate Claude Code hooks configuration."""
    hooks_dir = regula_root / "hooks"
    python = _find_python()

    config = {
        "hooks": {
            "PreToolUse": [{
                "matcher": "Bash|Write|Edit|MultiEdit",
                "hooks": [{
                    "type": "command",
                    "command": f"{python} {hooks_dir / 'pre_tool_use.py'}",
                }],
            }],
            "PostToolUse": [{
                "matcher": "Bash|Write|Edit|MultiEdit",
                "hooks": [{
                    "type": "command",
                    "command": f"{python} {hooks_dir / 'post_tool_use.py'}",
                }],
            }],
        }
    }

    # Write to project .claude directory
    settings_dir = project_dir / ".claude"
    settings_dir.mkdir(parents=True, exist_ok=True)
    settings_file = settings_dir / "settings.local.json"

    if settings_file.exists():
        try:
            existing = json.loads(settings_file.read_text(encoding="utf-8"))
            if "hooks" in existing:
                print(f"WARNING: {settings_file} already has hooks configured.")
                print("Existing hooks will be preserved. Regula hooks will be merged.")
                # Merge hooks
                for event, hook_list in config["hooks"].items():
                    if event not in existing["hooks"]:
                        existing["hooks"][event] = hook_list
                    else:
                        # Check if regula hooks already present
                        existing_cmds = [h.get("hooks", [{}])[0].get("command", "") for h in existing["hooks"][event]]
                        for hook in hook_list:
                            cmd = hook.get("hooks", [{}])[0].get("command", "")
                            if not any("regula" in ec for ec in existing_cmds):
                                existing["hooks"][event].append(hook)
                config = existing
        except (json.JSONDecodeError, KeyError) as e:
            print(f"regula: existing config malformed, overwriting: {e}", file=sys.stderr)

    settings_file.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    print(f"Claude Code hooks written to {settings_file}")


def install_copilot_cli(regula_root: Path, project_dir: Path) -> None:
    """Generate GitHub Copilot CLI hooks configuration."""
    hooks_dir = regula_root / "hooks"
    python = _find_python()

    config = {
        "version": 1,
        "hooks": {
            "preToolUse": {
                "command": f"{python} {hooks_dir / 'pre_tool_use.py'}",
                "description": "Regula AI governance risk indication",
            },
            "postToolUse": {
                "command": f"{python} {hooks_dir / 'post_tool_use.py'}",
                "description": "Regula audit trail logging",
            },
        },
    }

    hooks_dir_out = project_dir / ".github" / "hooks"
    hooks_dir_out.mkdir(parents=True, exist_ok=True)
    config_file = hooks_dir_out / "regula.json"

    config_file.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    print(f"Copilot CLI hooks written to {config_file}")


def install_windsurf(regula_root: Path, project_dir: Path) -> None:
    """Generate Windsurf Cascade hooks configuration."""
    hooks_dir = regula_root / "hooks"
    python = _find_python()

    config = {
        "hooks": {
            "PreToolUse": [{
                "matcher": "Bash|Write|Edit",
                "hooks": [{
                    "type": "command",
                    "command": f"{python} {hooks_dir / 'pre_tool_use.py'}",
                }],
            }],
            "PostToolUse": [{
                "matcher": "Bash|Write|Edit",
                "hooks": [{
                    "type": "command",
                    "command": f"{python} {hooks_dir / 'post_tool_use.py'}",
                }],
            }],
        },
    }

    config_dir = project_dir / ".windsurf"
    config_dir.mkdir(parents=True, exist_ok=True)
    config_file = config_dir / "hooks.json"

    config_file.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    print(f"Windsurf hooks written to {config_file}")


def install_pre_commit(regula_root: Path, project_dir: Path) -> None:
    """Generate pre-commit framework configuration."""
    python = _find_python()
    check_script = regula_root / "scripts" / "report.py"

    config_content = f"""# Regula AI Governance — pre-commit hook
# Add this to your .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: regula-check
        name: Regula AI Governance Check
        entry: {python} {check_script} --format json --project .
        language: system
        always_run: true
        pass_filenames: false
        stages: [pre-commit]
"""

    config_file = project_dir / ".pre-commit-config.yaml"
    if config_file.exists():
        print(f"WARNING: {config_file} already exists.")
        print("Add the following to your existing config:")
        print(config_content)
    else:
        config_file.write_text(config_content, encoding="utf-8")
        print(f"pre-commit config written to {config_file}")


def install_git_hooks(regula_root: Path, project_dir: Path) -> None:
    """Install a direct git pre-commit hook."""
    python = _find_python()
    report_script = regula_root / "scripts" / "report.py"

    hook_content = f"""#!/bin/sh
# Regula AI Governance — git pre-commit hook
# Scans staged files for AI risk indicators

echo "Regula: Scanning for AI governance risk indicators..."

result=$({python} {report_script} --project . --format json 2>/dev/null)

# Check for prohibited findings
prohibited=$(echo "$result" | {python} -c "
import sys, json
findings = json.load(sys.stdin)
blocked = [f for f in findings if f.get('tier') == 'prohibited' and not f.get('suppressed')]
if blocked:
    for f in blocked:
        print(f'  BLOCKED: {{f.get(\"file\", \"unknown\")}} — {{f.get(\"description\", \"\")}}')
    sys.exit(1)
sys.exit(0)
" 2>/dev/null)

if [ $? -ne 0 ]; then
    echo ""
    echo "Regula: PROHIBITED AI PRACTICE INDICATORS DETECTED"
    echo "$prohibited"
    echo ""
    echo "Commit blocked. Review the findings above."
    echo "To suppress a finding, add '# regula-ignore' to the relevant file."
    exit 1
fi

echo "Regula: No prohibited indicators found."
"""

    git_dir = project_dir / ".git" / "hooks"
    if not git_dir.exists():
        print(f"ERROR: {project_dir} is not a git repository.")
        sys.exit(1)

    hook_file = git_dir / "pre-commit"
    if hook_file.exists():
        print(f"WARNING: {hook_file} already exists. Appending Regula check.")
        existing = hook_file.read_text(encoding="utf-8")
        hook_file.write_text(existing + "\n" + hook_content, encoding="utf-8")
    else:
        hook_file.write_text(hook_content, encoding="utf-8")

    # Make executable
    hook_file.chmod(hook_file.stat().st_mode | stat.S_IEXEC)
    print(f"Git pre-commit hook installed at {hook_file}")


PLATFORMS = {
    "claude-code": install_claude_code,
    "copilot-cli": install_copilot_cli,
    "windsurf": install_windsurf,
    "pre-commit": install_pre_commit,
    "git-hooks": install_git_hooks,
}


def list_platforms() -> None:
    """List available platforms."""
    print("Available platforms:")
    print("  claude-code  — Claude Code PreToolUse/PostToolUse hooks")
    print("  copilot-cli  — GitHub Copilot CLI hooks")
    print("  windsurf     — Windsurf Cascade hooks")
    print("  pre-commit   — pre-commit framework hook")
    print("  git-hooks    — Direct git pre-commit hook")


def main():
    parser = argparse.ArgumentParser(
        description="Install Regula hooks for AI coding platforms"
    )
    parser.add_argument(
        "platform",
        nargs="?",
        choices=list(PLATFORMS.keys()) + ["list"],
        help="Platform to install hooks for",
    )
    parser.add_argument(
        "--project", "-p", default=".",
        help="Project directory (default: current directory)",
    )
    args = parser.parse_args()

    if not args.platform or args.platform == "list":
        list_platforms()
        return

    regula_root = _find_regula_root()
    project_dir = Path(args.project).resolve()

    print(f"Regula root: {regula_root}")
    print(f"Project: {project_dir}")
    print(f"Platform: {args.platform}")
    print()

    installer = PLATFORMS[args.platform]
    installer(regula_root, project_dir)

    print()
    print("Installation complete. Run 'python3 scripts/report.py --project .' to verify.")


if __name__ == "__main__":
    main()
