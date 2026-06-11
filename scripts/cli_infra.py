"""Infrastructure and setup commands for Regula CLI.

Covers: doctor, self-test, config, install, quickstart, init,
telemetry, metrics, security-self-check.

NOTE: Do NOT add 'from cli import ...' at module level.
cli.py imports this module (via cli_util) at module level, creating a
circular dependency. All imports from cli must stay inside function bodies.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


def cmd_doctor(args) -> None:
    """Check installation health."""
    from cli import json_output
    from doctor import run_doctor
    result = run_doctor(format_type=args.format)
    if args.format == "json":
        json_output("doctor", result, exit_code=0 if result["healthy"] else 1)
        sys.exit(0 if result["healthy"] else 1)
    else:
        sys.exit(0 if result else 1)


def cmd_self_test(args) -> None:
    """Run built-in self-test assertions."""
    from self_test import run_self_test
    ok = run_self_test()
    sys.exit(0 if ok else 1)


def cmd_config(args) -> None:
    """Config management commands."""
    from cli import json_output
    from config_validator import validate_config
    if args.config_action == "validate":
        result = validate_config(
            path=getattr(args, "file", None),
            format_type=args.format,
        )
        if args.format == "json":
            json_output("config validate", result, exit_code=0 if result["valid"] else 2)
        sys.exit(0 if result["valid"] else 2)
    else:
        print(f"Unknown config action: {args.config_action}", file=sys.stderr)
        sys.exit(2)


def cmd_install(args) -> None:
    """Install hooks for a platform."""
    from install import PLATFORMS, list_platforms, _find_regula_root

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


def cmd_quickstart(args) -> None:
    """60-second onboarding."""
    from cli import json_output
    from quickstart import run_quickstart
    result = run_quickstart(
        project_dir=args.project,
        org=getattr(args, "org", "My Organisation"),
        format_type=args.format,
    )
    if args.format == "json":
        json_output("quickstart", result)
    sys.exit(0)


def cmd_init(args) -> None:
    """Guided setup wizard."""
    from init_wizard import run_init
    run_init(Path(args.project).resolve(), interactive=args.interactive,
             dry_run=getattr(args, 'dry_run', False))


def cmd_telemetry(args) -> None:
    """Manage anonymous crash report consent (GDPR Article 7)."""
    from telemetry import get_consent, set_consent
    action = getattr(args, "telemetry_action", "status") or "status"

    if action == "status":
        consent = get_consent()
        if consent is None:
            print("Telemetry: not yet configured (will be asked on next run)")
        elif consent:
            print("Telemetry: enabled \u2014 anonymous crash reports are sent to help fix bugs")
            print("  To opt out: regula telemetry disable")
        else:
            print("Telemetry: disabled \u2014 no data is sent")
            print("  To opt in:  regula telemetry enable")
    elif action == "enable":
        set_consent(True)
        print("Telemetry enabled. Thank you \u2014 crash reports help fix bugs faster.")
    elif action == "disable":
        set_consent(False)
        print("Telemetry disabled. No crash reports will be sent.")


def cmd_metrics(args) -> None:
    """Show local usage statistics."""
    from cli import json_output, _print_metrics_text
    from metrics import get_stats, reset_stats
    if args.reset:
        reset_stats()
        print("Metrics reset.")
        return
    stats = get_stats()
    if args.format == "json":
        json_output("metrics", stats)
    else:
        _print_metrics_text(stats)


def cmd_security_self_check(args) -> None:
    """Scan regula's own source with its own rules."""
    from cli import json_output
    from security_self_check import run_security_self_check
    result = run_security_self_check(format_type=args.format)
    if args.format == "json":
        json_output("security-self-check", result, exit_code=0 if result["passed"] else 1)
    sys.exit(0 if result["passed"] else 1)
