"""Graceful degradation for optional dependencies.

Provides consistent messaging when optional packages are unavailable.
Warns once per package per process to avoid spam.
"""

import importlib
import sys

_warned: set = set()


def check_optional(package_name: str, feature: str, install_hint: str) -> bool:
    """Check if an optional package is importable.

    Returns True if available, False if not.
    Prints one-line guidance to stderr on first miss per package per process.
    """
    try:
        importlib.import_module(package_name)
        return True
    except ImportError:
        if package_name not in _warned:
            _warned.add(package_name)
            print(f"Note: {package_name} not installed — {feature} ({install_hint})",
                  file=sys.stderr)
        return False
