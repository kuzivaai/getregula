# regula-ignore
"""Graceful degradation for optional dependencies.

Provides consistent messaging when optional packages are unavailable.

By default the nag is SILENT — the fallback works and users would otherwise
see the same warning on every CLI invocation. Set REGULA_VERBOSE=1 to opt
back into per-process notices.

The full optional-dependency picture is available any time via:

    regula doctor

which lists every optional package with PASS/INFO status.
"""

import importlib
import os
import sys

_warned: set = set()


def check_optional(package_name: str, feature: str, install_hint: str) -> bool:
    """Check if an optional package is importable.

    Returns True if available, False if not.
    Silent by default. With REGULA_VERBOSE=1 set, prints one-line guidance
    to stderr on first miss per package per process.
    """
    try:
        importlib.import_module(package_name)
        return True
    except ImportError:
        if os.environ.get("REGULA_VERBOSE") and package_name not in _warned:
            _warned.add(package_name)
            print(f"Note: {package_name} not installed — {feature} ({install_hint})",
                  file=sys.stderr)
        return False
