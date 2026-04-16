"""Tests for Ed25519 manifest signing (Regula Evidence Format v1.1).

Covers the four scenarios the v1.1 spec §4.5.3 requires a verifier to
handle: signed+valid (round-trip), signed+tampered (fail), unsigned
under normal verify (pass), and unsigned under --strict (warn not fail).

Kept in a dedicated test file per project convention — do NOT extend
tests/test_classification.py.

Skipped entirely if `cryptography` is not importable (the signing extra
is optional).
"""
from __future__ import annotations

import base64
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

# Skip this whole module if `cryptography` is not available — signing
# is an optional extra, not a core requirement.
cryptography = pytest.importorskip("cryptography")


@pytest.fixture
def signing_key_env(tmp_path, monkeypatch):
    """Redirect the signing key to a temp path so the user's real key
    at ~/.regula/signing.key is never read or written by tests."""
    key_path = tmp_path / "test-signing.key"
    monkeypatch.setenv("REGULA_SIGNING_KEY", str(key_path))
    yield key_path


# ── Module-level unit tests ────────────────────────────────────────


def test_canonical_form_is_deterministic():
    from signing import canonicalize_manifest_for_signing
    m1 = {"format": "regula.evidence.v1", "format_version": "1.1", "files": []}
    m2 = {"files": [], "format_version": "1.1", "format": "regula.evidence.v1"}
    assert canonicalize_manifest_for_signing(m1) == canonicalize_manifest_for_signing(m2)


def test_canonical_form_excludes_signing_block():
    from signing import canonicalize_manifest_for_signing
    base = {"format": "regula.evidence.v1", "files": []}
    with_sig = dict(base, signing={"algorithm": "ed25519"})
    assert canonicalize_manifest_for_signing(base) == canonicalize_manifest_for_signing(with_sig)


def test_canonical_form_uses_sorted_keys_no_whitespace():
    from signing import canonicalize_manifest_for_signing
    m = {"b": 2, "a": 1}
    bs = canonicalize_manifest_for_signing(m)
    # Sorted keys, no whitespace at separators
    assert bs == b'{"a":1,"b":2}'


def test_canonical_form_non_ascii_deterministic_and_byte_stable():
    """M9: canonical form handles non-ASCII project names and special chars.

    The spec (§4.5.1) says:
        json.dumps(..., sort_keys=True, separators=(",", ":"),
                   ensure_ascii=False).encode("utf-8")

    This test proves:
    1. Non-ASCII (e.g. "café") survives canonicalization as raw UTF-8,
       NOT as \\u escape sequences (ensure_ascii=False).
    2. HTML-special characters (&, <, >) are NOT entity-encoded —
       JSON has no obligation to escape them.
    3. The output is deterministic (identical bytes on repeated calls).
    4. Keys are sorted and no whitespace separates tokens.

    Cross-language notes (informative, not executable):
    - JavaScript's JSON.stringify(obj, null, 0) does NOT sort keys by
      default; an explicit sorted-keys replacer is needed. With a custom
      replacer the output would match byte-for-byte.
    - Go's json.Marshal sorts map keys alphabetically and does NOT
      escape &, <, > (unlike html/template). Output would match
      byte-for-byte IF ensure_ascii=False is used on the Python side
      (which the spec requires).
    """
    from signing import canonicalize_manifest_for_signing

    manifest = {
        "format": "regula.evidence.v1",
        "format_version": "1.1",
        "project": "café",
        "files": [
            {
                "filename": "finding-with-special-chars.json",
                "sha256": "a" * 64,
                "size_bytes": 42,
            }
        ],
        "findings_summary": "Risk: severity > threshold & category < limit",
        "description": "Tags: <model> & <dataset> output > input",
    }

    canonical_1 = canonicalize_manifest_for_signing(manifest)
    canonical_2 = canonicalize_manifest_for_signing(manifest)

    # 1. Deterministic: identical bytes on repeated calls
    assert canonical_1 == canonical_2

    # 2. Valid UTF-8: decode without errors
    text = canonical_1.decode("utf-8")

    # 3. Non-ASCII preserved as literal characters, not \\u escapes
    assert "café" in text, (
        "expected literal 'café' in canonical form (ensure_ascii=False), "
        f"got: {text!r}"
    )
    # The UTF-8 byte sequence for "é" is 0xC3 0xA9
    assert b"\xc3\xa9" in canonical_1

    # 4. HTML-special characters are NOT escaped — raw JSON, not HTML
    assert "&" in text
    assert "<" in text
    assert ">" in text

    # 5. Sorted keys: verify key ordering in the output
    # All top-level keys, sorted: description, files, findings_summary,
    # format, format_version, project
    keys_in_order = [
        '"description"',
        '"files"',
        '"findings_summary"',
        '"format"',
        '"format_version"',
        '"project"',
    ]
    positions = [text.index(k) for k in keys_in_order]
    assert positions == sorted(positions), (
        f"keys not in sorted order; positions: {dict(zip(keys_in_order, positions))}"
    )

    # 6. No whitespace between JSON tokens (compact form):
    # There should be no spaces or newlines outside of string values.
    # Quick structural check: no ", " or ": " at the top level
    assert '", "' not in text.replace('\\"', ''), (
        "found ', ' separator — expected compact (no-whitespace) form"
    )
    assert '": ' not in text, "found ': ' separator — expected compact form"
    assert "\n" not in text, "newlines found — expected single-line compact form"

    # 7. signing and timestamp_authority blocks excluded even if present
    manifest_with_signing = dict(manifest, signing={"algorithm": "ed25519"})
    manifest_with_both = dict(
        manifest_with_signing,
        timestamp_authority={"format": "rfc3161"},
    )
    assert canonicalize_manifest_for_signing(manifest_with_signing) == canonical_1
    assert canonicalize_manifest_for_signing(manifest_with_both) == canonical_1


def test_sign_then_verify_round_trip(signing_key_env):
    from signing import sign_manifest, verify_manifest_signature

    manifest = {
        "format": "regula.evidence.v1",
        "format_version": "1.1",
        "regula_version": "1.6.2",
        "hash_algorithm": "sha256",
        "files": [{"filename": "a.json", "sha256": "a" * 64, "size_bytes": 1}],
    }
    signing_block = sign_manifest(manifest)
    manifest_signed = dict(manifest, signing=signing_block)

    ok, detail = verify_manifest_signature(manifest_signed)
    assert ok is True
    assert "verified" in detail.lower()


def test_tampered_manifest_fails_verification(signing_key_env):
    from signing import sign_manifest, verify_manifest_signature

    manifest = {
        "format": "regula.evidence.v1",
        "format_version": "1.1",
        "regula_version": "1.6.2",
        "files": [{"filename": "a.json", "sha256": "a" * 64, "size_bytes": 1}],
    }
    signing_block = sign_manifest(manifest)
    tampered = dict(manifest, signing=signing_block)
    # Tamper: change a file hash after signing
    tampered["files"] = [{"filename": "a.json", "sha256": "b" * 64, "size_bytes": 1}]

    ok, detail = verify_manifest_signature(tampered)
    assert ok is False
    assert "invalid" in detail.lower()


def test_no_signing_block_returns_false_with_marker():
    from signing import verify_manifest_signature
    manifest = {"format": "regula.evidence.v1", "files": []}
    ok, detail = verify_manifest_signature(manifest)
    assert ok is False
    assert detail == "no signing block"


def test_wrong_algorithm_rejected(signing_key_env):
    from signing import sign_manifest, verify_manifest_signature
    manifest = {"format": "regula.evidence.v1", "files": []}
    signing_block = sign_manifest(manifest)
    signing_block["algorithm"] = "rsa-pss"  # pretend someone swapped
    tampered = dict(manifest, signing=signing_block)
    ok, detail = verify_manifest_signature(tampered)
    assert ok is False
    assert "unsupported algorithm" in detail


def test_wrong_canonical_serialization_rejected(signing_key_env):
    from signing import sign_manifest, verify_manifest_signature
    manifest = {"format": "regula.evidence.v1", "files": []}
    signing_block = sign_manifest(manifest)
    signing_block["canonical_serialization"] = "cbor-cose"
    tampered = dict(manifest, signing=signing_block)
    ok, detail = verify_manifest_signature(tampered)
    assert ok is False
    assert "canonical_serialization" in detail


def test_key_generated_on_first_use(signing_key_env):
    """If no key exists at the path, load_or_create_keypair creates one."""
    from signing import load_or_create_keypair
    assert not signing_key_env.exists()
    priv, pub = load_or_create_keypair(signing_key_env)
    assert signing_key_env.exists()
    # Reading the private key file back should get the same key (idempotent load)
    priv2, pub2 = load_or_create_keypair(signing_key_env)
    # Ed25519 keys should be equal if loaded from the same file
    from cryptography.hazmat.primitives import serialization
    pub_bytes_1 = pub.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    pub_bytes_2 = pub2.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    assert pub_bytes_1 == pub_bytes_2


def test_public_key_round_trip(signing_key_env):
    """Embedding the public key via base64(PEM) and reloading is lossless."""
    from signing import load_or_create_keypair, public_key_pem_b64, load_public_key_from_b64
    _, pub = load_or_create_keypair(signing_key_env)
    b64 = public_key_pem_b64(pub)
    pub_loaded = load_public_key_from_b64(b64)
    from cryptography.hazmat.primitives import serialization
    assert pub.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    ) == pub_loaded.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )


# ── End-to-end tests via the CLI ───────────────────────────────────


def _run_regula(*argv, env=None):
    """Invoke `python3 -m scripts.cli` with the given args, return (rc, out, err)."""
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    proc = subprocess.run(
        [sys.executable, "-m", "scripts.cli", *argv],
        cwd=str(ROOT),
        env=merged_env,
        capture_output=True,
        text=True,
        timeout=180,
    )
    return proc.returncode, proc.stdout, proc.stderr


def test_cli_conform_sign_and_verify_round_trip_json(tmp_path):
    """`conform --sign --format json` produces a signed pack; `verify --format json` confirms it.

    Asserts on JSON envelope fields (stable contract) instead of stdout
    text substrings. This is the primary signing round-trip test.
    """
    key_path = tmp_path / "signing.key"
    out_dir = tmp_path / "pack-out"
    env = {"REGULA_SIGNING_KEY": str(key_path)}

    rc, out, err = _run_regula(
        "conform",
        "--project", "examples/code-completion-tool",
        "--output", str(out_dir),
        "--sign",
        "--format", "json",
        env=env,
    )
    assert rc == 0, f"conform failed: rc={rc}\nstdout={out}\nstderr={err}"
    conform_data = json.loads(out)
    assert conform_data["command"] == "conform"
    assert conform_data["exit_code"] == 0
    manifest = conform_data["data"]["manifest"]
    assert manifest["format_version"] == "1.1"
    assert "signing" in manifest
    assert manifest["signing"]["algorithm"] == "ed25519"
    pack_path = conform_data["data"]["pack_path"]

    # Verify picks up the signature cleanly via JSON mode
    rc2, out2, err2 = _run_regula(
        "verify", pack_path, "--format", "json", env=env,
    )
    assert rc2 == 0, f"verify failed: rc={rc2}\nstdout={out2}\nstderr={err2}"
    verify_data = json.loads(out2)
    assert verify_data["command"] == "verify"
    assert verify_data["exit_code"] == 0
    report = verify_data["data"]
    assert report["signature_status"] == "VERIFIED"
    assert report["failed"] == 0
    assert report["passed"] == report["total"]


def test_cli_conform_sign_and_verify_round_trip_text_smoke(tmp_path):
    """Smoke test: human-readable text output mentions signing and verification.

    Kept as a single text-mode sanity check; the JSON test above is the
    authoritative round-trip assertion.
    """
    key_path = tmp_path / "signing.key"
    out_dir = tmp_path / "pack-out"
    env = {"REGULA_SIGNING_KEY": str(key_path)}

    rc, out, err = _run_regula(
        "conform",
        "--project", "examples/code-completion-tool",
        "--output", str(out_dir),
        "--sign",
        env=env,
    )
    assert rc == 0, f"conform failed: rc={rc}\nstdout={out}\nstderr={err}"
    # Loose check -- any mention of signing/ed25519 suffices
    assert "sign" in out.lower() or "ed25519" in out.lower(), (
        f"expected signing mention in text output: {out!r}"
    )

    pack_dir = next(p for p in out_dir.iterdir() if p.is_dir())
    rc2, out2, err2 = _run_regula("verify", str(pack_dir), env=env)
    assert rc2 == 0, f"verify failed: rc={rc2}\nstdout={out2}\nstderr={err2}"
    assert "verified" in out2.lower(), (
        f"expected 'verified' in text output: {out2!r}"
    )


def test_cli_verify_rejects_tampered_signed_manifest_json(tmp_path):
    """Editing a signed pack's file hash causes verify to exit non-zero (JSON mode)."""
    key_path = tmp_path / "signing.key"
    out_dir = tmp_path / "pack-out"
    env = {"REGULA_SIGNING_KEY": str(key_path)}

    rc, out, err = _run_regula(
        "conform",
        "--project", "examples/code-completion-tool",
        "--output", str(out_dir),
        "--sign",
        "--format", "json",
        env=env,
    )
    assert rc == 0, err
    conform_data = json.loads(out)
    pack_path = conform_data["data"]["pack_path"]

    manifest_path = Path(pack_path) / "manifest.json"
    manifest = json.loads(manifest_path.read_text())

    # Tamper: flip the first byte of the first file's sha256 entry
    first_file = manifest["files"][0]
    original_hash = first_file["sha256"]
    swapped = ("1" if original_hash[0] == "0" else "0") + original_hash[1:]
    first_file["sha256"] = swapped
    manifest_path.write_text(json.dumps(manifest, indent=2))

    rc2, out2, err2 = _run_regula(
        "verify", str(pack_path), "--format", "json", env=env,
    )
    # verify should fail -- exit code 1 for invalid signature
    assert rc2 != 0, "verify should fail on tampered signed manifest"
    # The CLI may sys.exit(1) before emitting JSON, so check combined text
    combined = (out2 + err2).lower()
    assert "signature" in combined or "invalid" in combined, (
        f"expected signature/invalid in output; got stdout={out2!r} stderr={err2!r}"
    )


def test_cli_verify_unsigned_pack_passes_non_strict_json(tmp_path):
    """An unsigned v1.0 pack verifies cleanly without --strict (JSON mode)."""
    out_dir = tmp_path / "pack-out"
    rc, out, err = _run_regula(
        "conform",
        "--project", "examples/code-completion-tool",
        "--output", str(out_dir),
        "--format", "json",
    )
    assert rc == 0, err
    conform_data = json.loads(out)
    manifest = conform_data["data"]["manifest"]
    assert "signing" not in manifest
    assert manifest["format_version"] == "1.0"
    pack_path = conform_data["data"]["pack_path"]

    rc2, out2, err2 = _run_regula(
        "verify", pack_path, "--format", "json",
    )
    assert rc2 == 0, f"unsigned pack should verify: {err2}"
    verify_data = json.loads(out2)
    report = verify_data["data"]
    assert report["failed"] == 0
    # No signature_status key when unsigned and non-strict
    assert "signature_status" not in report


def test_cli_verify_unsigned_pack_warns_under_strict_json(tmp_path):
    """Under --strict, an unsigned pack emits a warning (but still exits 0) in JSON."""
    out_dir = tmp_path / "pack-out"
    rc, _, err = _run_regula(
        "conform",
        "--project", "examples/code-completion-tool",
        "--output", str(out_dir),
    )
    assert rc == 0, err
    pack_dir = next(p for p in out_dir.iterdir() if p.is_dir())

    rc2, out2, err2 = _run_regula(
        "verify", str(pack_dir), "--strict", "--format", "json",
    )
    assert rc2 == 0, f"unsigned pack under strict should still exit 0: rc={rc2}"
    verify_data = json.loads(out2)
    report = verify_data["data"]
    # Strict mode adds a warning about the missing signature
    assert "warnings" in report
    warning_text = " ".join(report["warnings"]).lower()
    assert "unsigned" in warning_text or "signing" in warning_text


def test_cli_verify_signed_zip_bundle_round_trip(tmp_path):
    """L6: `conform --sign --zip` produces a .regula.zip; `verify` on the zip succeeds.

    Timestamping is omitted because it requires a real TSA (network call)
    or the mock_tsa fixture which lives in test_manifest_timestamp.py.
    The core assertion is: sign + zip + verify round-trip works end-to-end.
    """
    key_path = tmp_path / "signing.key"
    out_dir = tmp_path / "pack-out"
    env = {"REGULA_SIGNING_KEY": str(key_path)}

    rc, out, err = _run_regula(
        "conform",
        "--project", "examples/code-completion-tool",
        "--output", str(out_dir),
        "--sign",
        "--zip",
        "--format", "json",
        env=env,
    )
    assert rc == 0, f"conform --sign --zip failed: rc={rc}\nstdout={out}\nstderr={err}"
    conform_data = json.loads(out)
    assert conform_data["exit_code"] == 0

    # The JSON envelope should include a bundle_path
    bundle_path = conform_data["data"].get("bundle_path")
    assert bundle_path is not None, (
        f"expected bundle_path in conform JSON data; keys={list(conform_data['data'].keys())}"
    )
    assert Path(bundle_path).exists(), f"bundle not found at {bundle_path}"
    assert bundle_path.endswith(".regula.zip")

    # Verify the zip bundle directly
    rc2, out2, err2 = _run_regula(
        "verify", bundle_path, "--format", "json", env=env,
    )
    assert rc2 == 0, f"verify on zip bundle failed: rc={rc2}\nstdout={out2}\nstderr={err2}"
    verify_data = json.loads(out2)
    report = verify_data["data"]
    assert report["signature_status"] == "VERIFIED"
    assert report["failed"] == 0
    assert report["passed"] == report["total"]
