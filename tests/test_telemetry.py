import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))


def test_consent_default_is_none(monkeypatch, tmp_path):
    """Fresh install: consent is None (not asked yet)."""
    monkeypatch.setenv("REGULA_CONFIG_DIR", str(tmp_path))
    import importlib
    import telemetry
    importlib.reload(telemetry)
    assert telemetry.get_consent() is None


def test_consent_set_true(monkeypatch, tmp_path):
    monkeypatch.setenv("REGULA_CONFIG_DIR", str(tmp_path))
    import importlib
    import telemetry
    importlib.reload(telemetry)
    telemetry.set_consent(True)
    assert telemetry.get_consent() is True


def test_consent_set_false(monkeypatch, tmp_path):
    monkeypatch.setenv("REGULA_CONFIG_DIR", str(tmp_path))
    import importlib
    import telemetry
    importlib.reload(telemetry)
    telemetry.set_consent(False)
    assert telemetry.get_consent() is False


def test_no_sentry_init_without_consent(monkeypatch, tmp_path):
    """init_sentry() must be a no-op when consent is False."""
    monkeypatch.setenv("REGULA_CONFIG_DIR", str(tmp_path))
    import importlib
    import telemetry
    importlib.reload(telemetry)
    telemetry.set_consent(False)
    telemetry.init_sentry()  # must not raise


def test_build_feedback_url_false_positive(monkeypatch, tmp_path):
    import importlib
    import telemetry
    importlib.reload(telemetry)
    url = telemetry.build_feedback_url(
        kind="false-positive",
        pattern_id="HIGH_RISK_BIOMETRIC",
        file_path="src/face_verify.py",
        line_number=42,
        regula_version="1.5.0",
        description=None,
    )
    assert "HIGH_RISK_BIOMETRIC" in url
    assert "face_verify.py" in url
    assert "false-positive" in url


def test_build_feedback_url_false_negative(monkeypatch, tmp_path):
    import importlib
    import telemetry
    importlib.reload(telemetry)
    url = telemetry.build_feedback_url(
        kind="false-negative",
        pattern_id="MISSED_RISK",
        file_path="src/model.py",
        line_number=10,
        regula_version="1.5.0",
        description=None,
    )
    assert "MISSED_RISK" in url
    assert "false-negative" in url


def test_build_feedback_url_bug(monkeypatch, tmp_path):
    import importlib
    import telemetry
    importlib.reload(telemetry)
    url = telemetry.build_feedback_url(
        kind="bug",
        pattern_id=None,
        file_path=None,
        line_number=None,
        regula_version="1.5.0",
        description="regula check crashed with AttributeError",
    )
    assert "crash" in url
    assert "AttributeError" in url


def test_feedback_command_false_positive(capsys, monkeypatch, tmp_path):
    import argparse
    import importlib
    monkeypatch.setenv("REGULA_CONFIG_DIR", str(tmp_path))
    monkeypatch.setenv("CI", "true")
    import cli
    importlib.reload(cli)
    args = argparse.Namespace(
        feedback_kind="false-positive",
        pattern="HIGH_RISK_BIOMETRIC",
        file="src/face_verify.py",
        line=42,
        description=None,
        no_browser=True,
    )
    cli.cmd_feedback(args)
    out = capsys.readouterr().out
    assert "github.com/kuzivaai/getregula/issues/new" in out
    assert "HIGH_RISK_BIOMETRIC" in out


def test_telemetry_status_enabled(capsys, monkeypatch, tmp_path):
    import argparse
    import importlib
    import telemetry
    monkeypatch.setenv("REGULA_CONFIG_DIR", str(tmp_path))
    importlib.reload(telemetry)
    telemetry.set_consent(True)
    import cli
    importlib.reload(cli)
    args = argparse.Namespace(telemetry_action="status")
    cli.cmd_telemetry(args)
    out = capsys.readouterr().out
    assert "enabled" in out.lower()


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])


# ── Privacy regression guards (21 Jul 2026) ───────────────────────
#
# Between 43da24c (10 Apr 2026) and 21 Jul 2026, `_SENTRY_DSN` was
# hardcoded to a live endpoint while docs/TRUST.md §8.2 stated it was
# empty. Nothing failed, because nothing asserted it. These tests exist so
# that specific regression cannot recur silently.


def _fresh(monkeypatch, tmp_path):
    """Reload telemetry with an isolated config dir and a clean environment."""
    monkeypatch.setenv("REGULA_CONFIG_DIR", str(tmp_path))
    for var in ("DO_NOT_TRACK", "REGULA_NO_TELEMETRY", "CI", "REGULA_SENTRY_DSN"):
        monkeypatch.delenv(var, raising=False)
    import importlib
    import telemetry
    importlib.reload(telemetry)
    return telemetry


def test_published_builds_hardcode_no_sentry_dsn(monkeypatch, tmp_path):
    """THE regression guard: no endpoint may be baked into the source.

    A hardcoded DSN silently falsifies docs/TRUST.md for every installed
    user. If someone re-adds one, this test fails and says why.
    """
    telemetry = _fresh(monkeypatch, tmp_path)
    assert telemetry._SENTRY_DSN == "", (
        "A Sentry DSN has been hardcoded into scripts/telemetry.py. "
        "docs/TRUST.md tells users published builds ship none; set "
        "REGULA_SENTRY_DSN in the environment instead."
    )
    assert telemetry._resolve_dsn() == ""


def test_dsn_comes_from_environment_when_set(monkeypatch, tmp_path):
    telemetry = _fresh(monkeypatch, tmp_path)
    monkeypatch.setenv("REGULA_SENTRY_DSN", "https://k@o1.ingest.de.sentry.io/1")
    assert telemetry._resolve_dsn() == "https://k@o1.ingest.de.sentry.io/1"


def test_do_not_track_suppresses_even_with_consent(monkeypatch, tmp_path):
    """DO_NOT_TRACK is the cross-tool CLI convention and must win."""
    telemetry = _fresh(monkeypatch, tmp_path)
    telemetry.set_consent(True)
    monkeypatch.setenv("REGULA_SENTRY_DSN", "https://k@o1.ingest.de.sentry.io/1")
    monkeypatch.setenv("DO_NOT_TRACK", "1")
    assert telemetry.telemetry_suppressed() is True


def test_regula_no_telemetry_suppresses_sending_not_just_the_prompt(monkeypatch, tmp_path):
    """Regression: this variable used to gate ONLY the first-run prompt, so a
    user who had consented once and later set it kept transmitting."""
    telemetry = _fresh(monkeypatch, tmp_path)
    telemetry.set_consent(True)
    monkeypatch.setenv("REGULA_SENTRY_DSN", "https://k@o1.ingest.de.sentry.io/1")
    monkeypatch.setenv("REGULA_NO_TELEMETRY", "1")
    assert telemetry.telemetry_suppressed() is True


def test_ci_suppresses_telemetry(monkeypatch, tmp_path):
    telemetry = _fresh(monkeypatch, tmp_path)
    monkeypatch.setenv("CI", "true")
    assert telemetry.telemetry_suppressed() is True


def test_falsey_values_do_not_suppress(monkeypatch, tmp_path):
    """Per the DO_NOT_TRACK convention, '0' means not enabled."""
    telemetry = _fresh(monkeypatch, tmp_path)
    for falsey in ("0", "false", "no", ""):
        monkeypatch.setenv("DO_NOT_TRACK", falsey)
        assert telemetry.telemetry_suppressed() is False, falsey


def test_no_suppression_on_clean_environment(monkeypatch, tmp_path):
    telemetry = _fresh(monkeypatch, tmp_path)
    assert telemetry.telemetry_suppressed() is False


def test_init_sentry_is_noop_when_suppressed(monkeypatch, tmp_path):
    """Consent + endpoint + DO_NOT_TRACK must still send nothing."""
    telemetry = _fresh(monkeypatch, tmp_path)
    telemetry.set_consent(True)
    monkeypatch.setenv("REGULA_SENTRY_DSN", "https://k@o1.ingest.de.sentry.io/1")
    monkeypatch.setenv("DO_NOT_TRACK", "1")

    called = []
    try:
        import sentry_sdk
    except ImportError:
        telemetry.init_sentry()  # must not raise
        return
    monkeypatch.setattr(sentry_sdk, "init", lambda **kw: called.append(kw))
    telemetry.init_sentry()
    assert called == [], "sentry_sdk.init was called despite DO_NOT_TRACK"


def test_init_sentry_disables_local_variables_and_hostname(monkeypatch, tmp_path):
    """Data minimisation: Regula's scan frames hold whole scanned files in
    `content`, so sentry-sdk's include_local_variables default of True would
    ship a user's proprietary source on any crash."""
    telemetry = _fresh(monkeypatch, tmp_path)
    telemetry.set_consent(True)
    monkeypatch.setenv("REGULA_SENTRY_DSN", "https://k@o1.ingest.de.sentry.io/1")

    try:
        import sentry_sdk
    except ImportError:
        return  # optional extra not installed
    captured = {}
    monkeypatch.setattr(sentry_sdk, "init", lambda **kw: captured.update(kw))
    telemetry.init_sentry()

    assert captured, "sentry_sdk.init was not called"
    assert captured["include_local_variables"] is False
    assert captured["send_default_pii"] is False
    assert captured["server_name"] == "redacted"
    assert captured["traces_sample_rate"] == 0.0
