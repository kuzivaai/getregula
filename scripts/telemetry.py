# regula-ignore
"""
Regula telemetry — GDPR-compliant opt-in crash reporting.

Consent is stored in ~/.regula/config.toml (or $REGULA_CONFIG_DIR/config.toml).
No data is sent unless the user explicitly opted in.

GDPR Article 7(3): withdrawal must be as easy as giving consent.
Use: regula telemetry disable
"""
import os
import sys
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from constants import VERSION

_SENTRY_DSN = "https://7ac96f66fc31c43edd6072c3a0d0c9b2@o4511163062353920.ingest.de.sentry.io/4511196620914768"


def _config_dir() -> Path:
    """Config dir. Override via REGULA_CONFIG_DIR env var (used in tests)."""
    override = os.environ.get("REGULA_CONFIG_DIR")
    if override:
        return Path(override)
    return Path.home() / ".regula"


def _config_path() -> Path:
    return _config_dir() / "config.toml"


def get_consent() -> "bool | None":
    """Return True (opted in), False (opted out), or None (never asked)."""
    p = _config_path()
    if not p.exists():
        return None
    for line in p.read_text().splitlines():
        stripped = line.strip()
        if stripped.startswith("telemetry"):
            val = stripped.split("=", 1)[-1].strip().lower().strip('"\'')
            if val in ("true", "1", "yes"):
                return True
            if val in ("false", "0", "no"):
                return False
    return None


def set_consent(value: bool) -> None:
    """Persist consent choice. Creates ~/.regula/ if needed."""
    d = _config_dir()
    d.mkdir(parents=True, exist_ok=True)
    p = _config_path()
    existing = p.read_text().splitlines() if p.exists() else []
    lines = [l for l in existing if not l.strip().startswith("telemetry")]
    lines.append(f'telemetry = {"true" if value else "false"}')
    p.write_text("\n".join(lines) + "\n")


def prompt_consent_if_needed() -> None:
    """
    First-run prompt. No-op if:
    - already answered
    - running in CI (CI env var set)
    - stdin is not a tty (piped/redirected)
    - REGULA_NO_TELEMETRY env var is set
    """
    if not sys.stdin.isatty():
        return
    if os.environ.get("CI") or os.environ.get("REGULA_NO_TELEMETRY"):
        return
    if get_consent() is not None:
        return

    print()
    print("  Regula can send anonymous crash reports to help fix bugs faster.")
    print("  No source code, file paths, or personal data are ever sent.")
    print("  Change this at any time: regula telemetry enable|disable")
    print()
    try:
        answer = input("  Send anonymous crash reports? [y/N] ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        return
    set_consent(answer in ("y", "yes"))
    print()


def init_sentry() -> None:
    """Initialise Sentry if consent=True, DSN is set, and sentry-sdk is installed."""
    if get_consent() is not True:
        return
    if not _SENTRY_DSN:
        return
    try:
        import sentry_sdk
        sentry_sdk.init(
            dsn=_SENTRY_DSN,
            release=f"regula@{VERSION}",
            traces_sample_rate=0.0,  # errors only — no performance tracing
            send_default_pii=False,
        )
    except ImportError:
        pass  # sentry-sdk not installed — silent no-op


def dsn_is_configured() -> bool:
    """Return True if a Sentry DSN has been set in this file."""
    return bool(_SENTRY_DSN)


def build_feedback_url(
    kind: str,
    pattern_id: "str | None",
    file_path: "str | None",
    line_number: "int | None",
    regula_version: str,
    description: "str | None",
) -> str:
    """
    Build a pre-filled GitHub Issue URL.

    kind: "false-positive" | "false-negative" | "bug"
    """
    if kind == "false-positive":
        title = f"False positive: {pattern_id or 'unknown'}"
        label = "false-positive"
        line_info = f"Line: {line_number}" if line_number else "Line: unknown"
        body = (
            f"**Pattern flagged:** `{pattern_id or 'unknown'}`\n"
            f"**File:** `{file_path or 'unknown'}`\n"
            f"**{line_info}**\n"
            f"**Regula version:** `{regula_version}`\n\n"
            "**Why this is a false positive:**\n"
            "<!-- Describe why this code is not actually a risk -->\n\n"
            "**Code snippet (optional):**\n"
            "```\n\n```\n"
        )
    elif kind == "false-negative":
        title = f"False negative (missed risk): {pattern_id or 'unknown'}"
        label = "false-negative"
        line_info = f"Line: {line_number}" if line_number else "Line: unknown"
        body = (
            f"**Pattern that should have been flagged:** `{pattern_id or 'describe below'}`\n"
            f"**File:** `{file_path or 'unknown'}`\n"
            f"**{line_info}**\n"
            f"**Regula version:** `{regula_version}`\n\n"
            "**Why this should have been flagged:**\n"
            "<!-- Describe the risk and why Regula missed it -->\n\n"
            "**Code snippet (optional):**\n"
            "```\n\n```\n"
        )
    else:  # bug / crash
        title = f"Bug report: {(description or 'unexpected behaviour')[:60]}"
        label = "crash"
        body = (
            f"**Regula version:** `{regula_version}`\n\n"
            f"**What happened:**\n{description or '<!-- Describe the error -->'}\n\n"
            "**Command run:**\n"
            "```\nregula \n```\n\n"
            "**Full error output:**\n"
            "```\n\n```\n\n"
            "**Python version / OS:**\n"
            "<!-- e.g. Python 3.11, Ubuntu 22.04 -->\n"
        )

    params = urllib.parse.urlencode({
        "title": title,
        "body": body,
        "labels": label,
    })
    return f"https://github.com/kuzivaai/getregula/issues/new?{params}"
