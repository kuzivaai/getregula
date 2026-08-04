# regula-ignore
"""
Regula telemetry — opt-in crash reporting with no default endpoint.

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

# Published builds ship NO endpoint. Regula's audience is compliance and
# security teams, many of whom cannot lawfully send anything to a third
# party — shipping a live endpoint in the wheel would contradict the
# posture documented in docs/TRUST.md §8. Operators who want crash reports
# set REGULA_SENTRY_DSN to a Sentry instance of their own choosing.
#
# Do NOT hardcode a DSN here. Doing so silently makes docs/TRUST.md false
# for every installed user (it happened once, in 43da24c, and went
# unnoticed from 10 Apr to 20 Jul 2026).
_SENTRY_DSN = ""


def _resolve_dsn() -> str:
    """Return the configured Sentry DSN, or "" when none is set."""
    return os.environ.get("REGULA_SENTRY_DSN", _SENTRY_DSN).strip()


def telemetry_suppressed() -> bool:
    """True when the environment forbids telemetry, regardless of consent.

    `DO_NOT_TRACK` is the cross-tool convention (consoledonottrack.com);
    `REGULA_NO_TELEMETRY` is our own kill switch; `CI` covers unattended
    runs. All three are checked here so they suppress *sending*, not merely
    the first-run prompt — the earlier code checked them only at the prompt,
    so a user who had consented once and later set REGULA_NO_TELEMETRY was
    still transmitting.
    """
    for var in ("DO_NOT_TRACK", "REGULA_NO_TELEMETRY", "CI"):
        val = os.environ.get(var)
        if val is not None and val.strip().lower() not in ("", "0", "false", "no"):
            return True
    return False


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
    lines = [ln for ln in existing if not ln.strip().startswith("telemetry")]
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
    if telemetry_suppressed():
        return
    if get_consent() is not None:
        return
    # Nothing to consent TO when no endpoint is configured — asking would
    # imply data leaves the machine when it cannot.
    if not _resolve_dsn():
        return

    print()
    print("  Regula can send crash reports to help fix bugs faster.")
    print("  Sent on an uncaught error: the exception type and message, a")
    print("  stack trace through Regula's own code, and the Regula, OS and")
    print("  Python versions.")
    print("  Not sent: your source code, the contents of scanned files,")
    print("  local variables, or your hostname. Note that an error message")
    print("  can itself contain a file path (e.g. a permission error).")
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
    if telemetry_suppressed():
        return
    dsn = _resolve_dsn()
    if not dsn:
        return
    try:
        import sentry_sdk
        sentry_sdk.init(
            dsn=dsn,
            release=f"regula@{VERSION}",
            traces_sample_rate=0.0,  # errors only — no performance tracing
            send_default_pii=False,
            # Data minimisation (UK/EU GDPR Art. 5(1)(c)). sentry-sdk
            # defaults this to True, which would attach every stack frame's
            # locals — and Regula's scan frames hold whole scanned files in
            # `content`, so a crash would ship a user's proprietary source
            # to the endpoint. This is the decisive setting, not a nicety.
            include_local_variables=False,
            # Suppress the auto-detected hostname, which is often a person's
            # name or an internal machine identifier.
            server_name="redacted",
        )
    except ImportError:
        pass  # sentry-sdk not installed — silent no-op


def dsn_is_configured() -> bool:
    """Return True if a Sentry DSN is configured (env var or, historically,
    this module). Must go through `_resolve_dsn` so `regula doctor` reflects
    an endpoint set via REGULA_SENTRY_DSN."""
    return bool(_resolve_dsn())


def build_feedback_url(
    kind: str,
    pattern_id: "str | None",
    file_path: "str | None",
    line_number: "int | None",
    regula_version: str,
    description: "str | None",
    confidence_score: "int | None" = None,
    tier: "str | None" = None,
) -> str:
    """
    Build a pre-filled GitHub Issue URL.

    kind: "false-positive" | "false-negative" | "bug"
    """
    if kind == "false-positive":
        title = f"False positive: {pattern_id or 'unknown'}"
        label = "false-positive"
        line_info = f"Line: {line_number}" if line_number else "Line: unknown"
        conf_line = f"**Confidence score:** `{confidence_score}`\n" if confidence_score is not None else ""
        tier_line = f"**Finding tier:** `{tier}`\n" if tier else ""
        body = (
            f"**Pattern flagged:** `{pattern_id or 'unknown'}`\n"
            f"**File:** `{file_path or 'unknown'}`\n"
            f"**{line_info}**\n"
            f"{conf_line}{tier_line}"
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
