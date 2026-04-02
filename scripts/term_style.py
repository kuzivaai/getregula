#!/usr/bin/env python3
# regula-ignore
"""Terminal styling using ANSI escape codes. No dependencies.

Automatically disables colour when stdout is not a TTY (piped output,
CI environments, --format json). Safe to import anywhere.
"""

import os
import sys

_NO_COLOR = (
    not hasattr(sys.stdout, "isatty")
    or not sys.stdout.isatty()
    or os.environ.get("NO_COLOR", "") != ""
    or os.environ.get("TERM", "") == "dumb"
)


def _code(n: str) -> str:
    return "" if _NO_COLOR else f"\033[{n}m"


# Colours
RED = _code("31")
GREEN = _code("32")
YELLOW = _code("33")
BLUE = _code("34")
MAGENTA = _code("35")
CYAN = _code("36")
WHITE = _code("37")
DIM = _code("2")
BOLD = _code("1")
RESET = _code("0")


def red(s: str) -> str:
    return f"{RED}{s}{RESET}"


def green(s: str) -> str:
    return f"{GREEN}{s}{RESET}"


def yellow(s: str) -> str:
    return f"{YELLOW}{s}{RESET}"


def blue(s: str) -> str:
    return f"{BLUE}{s}{RESET}"


def bold(s: str) -> str:
    return f"{BOLD}{s}{RESET}"


def magenta(s: str) -> str:
    return f"{MAGENTA}{s}{RESET}"


def dim(s: str) -> str:
    return f"{DIM}{s}{RESET}"


# Tier-specific colours
TIER_COLORS = {
    "prohibited": RED,
    "high_risk": YELLOW,
    "limited_risk": BLUE,
    "minimal_risk": DIM,
    "agent_autonomy": MAGENTA,
    "credential_exposure": RED,
    "ai_security": YELLOW,
}


def tier_color(tier: str, text: str) -> str:
    """Colour text based on risk tier."""
    color = TIER_COLORS.get(tier, "")
    return f"{color}{text}{RESET}" if color else text
