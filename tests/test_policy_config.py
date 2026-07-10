# regula-ignore
"""Tests for scripts/policy_config.py — malformed policy file handling."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


# ── Malformed policy file tests ────────────────────────────────────


def test_malformed_yaml_policy_prints_warning_and_returns_empty(tmp_path, capsys, monkeypatch):
    """A policy file that exists but contains invalid YAML prints a clear warning
    to stderr and causes get_policy_parse_error() to return a non-None tuple.
    The tool must not crash and must return an empty dict."""
    import policy_config

    # Write a deliberately malformed YAML file
    bad_policy = tmp_path / "regula-policy.yaml"
    bad_policy.write_text("key: [\nunot closed brace\n", encoding="utf-8")

    # Point REGULA_POLICY at it so it is the first candidate
    monkeypatch.setenv("REGULA_POLICY", str(bad_policy))

    # Reset module state so _load_policy() runs fresh with new env
    monkeypatch.setattr(policy_config, "_POLICY_PARSE_ERROR", None)
    result = policy_config._load_policy()

    captured = capsys.readouterr()

    # 1. Tool must not crash — result is a dict
    assert isinstance(result, dict), "must return a dict on parse failure"

    # 2. Warning printed to stderr with file path
    assert str(bad_policy) in captured.err, (
        f"stderr must include the policy file path; got: {captured.err!r}"
    )
    assert "WARNING" in captured.err, (
        f"stderr must include 'WARNING'; got: {captured.err!r}"
    )
    assert "default" in captured.err.lower(), (
        f"stderr must mention 'default'; got: {captured.err!r}"
    )

    # 3. Error is accessible via get_policy_parse_error()
    parse_error = policy_config.get_policy_parse_error()
    assert parse_error is not None, "get_policy_parse_error() must return a tuple after a parse failure"
    assert isinstance(parse_error, tuple) and len(parse_error) == 2
    err_path, err_msg = parse_error
    assert str(bad_policy) in err_path, "error tuple must contain the file path"
    assert isinstance(err_msg, str) and len(err_msg) > 0, "error tuple must contain the error message"

    print("✓ policy_config: malformed YAML — warning printed, error accessible, no crash")


def test_malformed_json_policy_prints_warning_and_returns_empty(tmp_path, capsys, monkeypatch):
    """A malformed JSON policy file also triggers the warning path."""
    import policy_config

    bad_policy = tmp_path / "regula-policy.json"
    bad_policy.write_text("{invalid json{{", encoding="utf-8")

    monkeypatch.setenv("REGULA_POLICY", str(bad_policy))
    monkeypatch.setattr(policy_config, "_POLICY_PARSE_ERROR", None)
    result = policy_config._load_policy()

    captured = capsys.readouterr()

    assert isinstance(result, dict)
    assert str(bad_policy) in captured.err
    assert "WARNING" in captured.err

    parse_error = policy_config.get_policy_parse_error()
    assert parse_error is not None
    err_path, _ = parse_error
    assert str(bad_policy) in err_path

    print("✓ policy_config: malformed JSON — warning printed, error accessible, no crash")


def test_valid_policy_no_parse_error(tmp_path, monkeypatch):
    """A valid policy file sets no parse error."""
    import policy_config

    good_policy = tmp_path / "regula-policy.json"
    good_policy.write_text('{"version": "1.0"}', encoding="utf-8")

    monkeypatch.setenv("REGULA_POLICY", str(good_policy))
    monkeypatch.setattr(policy_config, "_POLICY_PARSE_ERROR", None)
    result = policy_config._load_policy()

    assert isinstance(result, dict)
    assert result.get("version") == "1.0"
    assert policy_config.get_policy_parse_error() is None, (
        "no parse error should be set for a valid policy file"
    )

    print("✓ policy_config: valid policy — no parse error set")


def test_missing_policy_no_parse_error(tmp_path, monkeypatch):
    """When no policy file exists at all, no parse error is set."""
    import policy_config

    nonexistent = tmp_path / "does-not-exist.yaml"
    monkeypatch.setenv("REGULA_POLICY", str(nonexistent))
    monkeypatch.setattr(policy_config, "_POLICY_PARSE_ERROR", None)
    result = policy_config._load_policy()

    assert isinstance(result, dict)
    assert policy_config.get_policy_parse_error() is None, (
        "a missing file is not a parse error — no error should be set"
    )

    print("✓ policy_config: missing policy file — no parse error set")


def test_get_policy_parse_error_initial_state():
    """get_policy_parse_error() returns None before any parse failure."""
    import policy_config
    # We cannot guarantee the initial state if the module was already loaded
    # with a bad policy, so we just assert the return type contract.
    result = policy_config.get_policy_parse_error()
    assert result is None or (isinstance(result, tuple) and len(result) == 2), (
        "get_policy_parse_error() must return None or a (path, error) tuple"
    )
    print("✓ policy_config: get_policy_parse_error() return type is correct")
