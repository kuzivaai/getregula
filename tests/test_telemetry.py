import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))


def test_consent_default_is_none(monkeypatch, tmp_path):
    """Fresh install: consent is None (not asked yet)."""
    monkeypatch.setenv("REGULA_CONFIG_DIR", str(tmp_path))
    import importlib, telemetry
    importlib.reload(telemetry)
    assert telemetry.get_consent() is None


def test_consent_set_true(monkeypatch, tmp_path):
    monkeypatch.setenv("REGULA_CONFIG_DIR", str(tmp_path))
    import importlib, telemetry
    importlib.reload(telemetry)
    telemetry.set_consent(True)
    assert telemetry.get_consent() is True


def test_consent_set_false(monkeypatch, tmp_path):
    monkeypatch.setenv("REGULA_CONFIG_DIR", str(tmp_path))
    import importlib, telemetry
    importlib.reload(telemetry)
    telemetry.set_consent(False)
    assert telemetry.get_consent() is False


def test_no_sentry_init_without_consent(monkeypatch, tmp_path):
    """init_sentry() must be a no-op when consent is False."""
    monkeypatch.setenv("REGULA_CONFIG_DIR", str(tmp_path))
    import importlib, telemetry
    importlib.reload(telemetry)
    telemetry.set_consent(False)
    telemetry.init_sentry()  # must not raise


def test_build_feedback_url_false_positive(monkeypatch, tmp_path):
    import importlib, telemetry
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
    import importlib, telemetry
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
    import importlib, telemetry
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
    import argparse, importlib
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
    import argparse, importlib, telemetry
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
