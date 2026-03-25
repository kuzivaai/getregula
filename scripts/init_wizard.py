#!/usr/bin/env python3
"""
Regula Init — Guided Setup Wizard

Detects the development environment, installs appropriate hooks,
creates a default policy file, and runs an initial scan.
"""

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

REGULA_ROOT = Path(__file__).parent.parent.resolve()


def _detect_platforms(project_dir: Path) -> list:
    """Detect which AI coding platforms are present."""
    platforms = []

    # Claude Code
    if (project_dir / ".claude").exists() or (Path.home() / ".claude").exists():
        platforms.append("claude-code")

    # GitHub Copilot CLI
    if (project_dir / ".github").exists():
        platforms.append("copilot-cli")

    # Windsurf
    if (project_dir / ".windsurf").exists():
        platforms.append("windsurf")

    # Git (always available as fallback)
    if (project_dir / ".git").exists():
        platforms.append("git-hooks")

    return platforms


def _detect_python() -> str:
    """Detect Python version."""
    v = sys.version_info
    return f"{v.major}.{v.minor}.{v.micro}"


def _policy_exists(project_dir: Path) -> bool:
    """Check if a policy file exists."""
    return (project_dir / "regula-policy.yaml").exists() or \
           (project_dir / "regula-policy.json").exists()


def _create_default_policy(project_dir: Path) -> None:
    """Create a default regula-policy.yaml."""
    policy = """version: "1.0"
organisation: "Your Organisation"

frameworks:
  - eu_ai_act

rules:
  risk_classification:
    force_high_risk: []
    exempt: []

  logging:
    retention_years: 10
    pii_redaction: true
    export_format: [json, csv]
"""
    (project_dir / "regula-policy.yaml").write_text(policy, encoding="utf-8")


def _run_quick_scan(project_dir: Path) -> dict:
    """Run a quick scan and return summary."""
    try:
        from report import scan_files
        findings = scan_files(str(project_dir))
        active = [f for f in findings if not f.get("suppressed")]
        return {
            "total_files": len(set(f["file"] for f in findings)),
            "prohibited": sum(1 for f in active if f["tier"] == "prohibited"),
            "high_risk": sum(1 for f in active if f["tier"] == "high_risk"),
            "limited_risk": sum(1 for f in active if f["tier"] == "limited_risk"),
            "minimal_risk": sum(1 for f in active if f["tier"] == "minimal_risk"),
        }
    except Exception as e:
        return {"error": str(e)}


def run_init(project_dir: Path, interactive: bool = False) -> None:
    """Run the init wizard."""
    print()
    print("=" * 60)
    print("  Regula — AI Governance Setup")
    print("=" * 60)
    print()

    # 1. Environment detection
    python_version = _detect_python()
    platforms = _detect_platforms(project_dir)
    has_policy = _policy_exists(project_dir)

    print(f"  Project:    {project_dir}")
    print(f"  Python:     {python_version}")
    print(f"  Platforms:  {', '.join(platforms) if platforms else 'none detected'}")
    print(f"  Policy:     {'found' if has_policy else 'not found'}")
    print()

    # 2. Python version check
    if sys.version_info < (3, 10):
        print("  WARNING: Python 3.10+ required. Current version may not work.")
        print()

    # 3. Create policy if missing
    if not has_policy:
        if interactive:
            answer = input("  Create default regula-policy.yaml? [Y/n] ").strip().lower()
            if answer in ("", "y", "yes"):
                _create_default_policy(project_dir)
                print("  Created regula-policy.yaml")
            else:
                print("  Skipped policy creation.")
        else:
            _create_default_policy(project_dir)
            print("  Created regula-policy.yaml (edit to customise)")
    else:
        print("  Policy file already exists.")
    print()

    # 4. Install hooks for detected platform
    if platforms:
        primary = platforms[0]
        if interactive:
            print(f"  Detected platform: {primary}")
            for i, p in enumerate(platforms):
                print(f"    {i + 1}. {p}")
            choice = input(f"  Install hooks for {primary}? [Y/n/number] ").strip().lower()
            if choice.isdigit() and 1 <= int(choice) <= len(platforms):
                primary = platforms[int(choice) - 1]
            elif choice in ("n", "no"):
                primary = None

        if primary:
            try:
                from install import PLATFORMS, _find_regula_root
                regula_root = _find_regula_root()
                installer = PLATFORMS.get(primary)
                if installer:
                    print(f"  Installing hooks for {primary}...")
                    installer(regula_root, project_dir)
                else:
                    print(f"  No installer for {primary}.")
            except Exception as e:
                print(f"  Hook installation failed: {e}")
                print(f"  Run manually: python3 scripts/install.py {primary}")
    else:
        print("  No AI coding platform detected.")
        print("  Run 'python3 scripts/install.py list' to see options.")
    print()

    # 5. Quick scan
    print("  Running initial scan...")
    summary = _run_quick_scan(project_dir)

    if "error" in summary:
        print(f"  Scan error: {summary['error']}")
    else:
        print(f"  AI files found:    {summary['total_files']}")
        print(f"  Prohibited:        {summary['prohibited']}")
        print(f"  High-risk:         {summary['high_risk']}")
        print(f"  Limited-risk:      {summary['limited_risk']}")
        print(f"  Minimal-risk:      {summary['minimal_risk']}")
    print()

    # 6. Next steps
    print("  " + "-" * 56)
    print("  Setup complete. Next steps:")
    print()
    print("  1. Edit regula-policy.yaml to customise for your org")
    print("  2. Run 'python3 scripts/cli.py check .' for a full scan")
    print("  3. Run 'python3 scripts/cli.py report --format html \\")
    print("         --output report.html' for a governance report")
    print("  4. Run 'python3 scripts/cli.py feed' for governance news")
    print("  5. Run 'python3 scripts/cli.py timeline' for EU AI Act dates")
    print("  " + "-" * 56)
    print()


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Regula guided setup")
    parser.add_argument("--project", "-p", default=".", help="Project directory")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
    args = parser.parse_args()

    run_init(Path(args.project).resolve(), interactive=args.interactive)


if __name__ == "__main__":
    main()
