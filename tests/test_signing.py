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


def test_cli_conform_sign_and_verify_round_trip(tmp_path):
    """`conform --sign` produces a signed pack; `verify` confirms it."""
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
    assert "Signed: Ed25519" in out, f"expected signed confirmation in stdout: {out!r}"

    # Locate the pack dir (only one should exist under out_dir)
    pack_dirs = [p for p in out_dir.iterdir() if p.is_dir()]
    assert len(pack_dirs) == 1
    pack_dir = pack_dirs[0]

    # Manifest should declare format_version 1.1 and carry a signing block
    manifest = json.loads((pack_dir / "manifest.json").read_text())
    assert manifest["format_version"] == "1.1"
    assert "signing" in manifest
    assert manifest["signing"]["algorithm"] == "ed25519"

    # Verify picks up the signature cleanly
    rc2, out2, err2 = _run_regula("verify", str(pack_dir), env=env)
    assert rc2 == 0, f"verify failed: rc={rc2}\nstdout={out2}\nstderr={err2}"
    assert "Signature: VERIFIED" in out2, f"expected signature VERIFIED: {out2!r}"


def test_cli_verify_rejects_tampered_signed_manifest(tmp_path):
    """Editing a signed pack's file hash causes verify to exit non-zero."""
    key_path = tmp_path / "signing.key"
    out_dir = tmp_path / "pack-out"
    env = {"REGULA_SIGNING_KEY": str(key_path)}

    rc, _, err = _run_regula(
        "conform",
        "--project", "examples/code-completion-tool",
        "--output", str(out_dir),
        "--sign",
        env=env,
    )
    assert rc == 0, err

    pack_dir = next(p for p in out_dir.iterdir() if p.is_dir())
    manifest_path = pack_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text())

    # Tamper: flip the first byte of the first file's sha256 entry
    first_file = manifest["files"][0]
    original_hash = first_file["sha256"]
    swapped = ("1" if original_hash[0] == "0" else "0") + original_hash[1:]
    first_file["sha256"] = swapped
    manifest_path.write_text(json.dumps(manifest, indent=2))

    rc2, out2, err2 = _run_regula("verify", str(pack_dir), env=env)
    assert rc2 != 0, "verify should fail on tampered signed manifest"
    combined = (out2 + err2).lower()
    assert "signature" in combined or "invalid" in combined, (
        f"expected signature/invalid in output; got stdout={out2!r} stderr={err2!r}"
    )


def test_cli_verify_unsigned_pack_passes_non_strict(tmp_path):
    """An unsigned v1.0 pack verifies cleanly without --strict."""
    out_dir = tmp_path / "pack-out"
    rc, out, err = _run_regula(
        "conform",
        "--project", "examples/code-completion-tool",
        "--output", str(out_dir),
    )
    assert rc == 0, err
    pack_dir = next(p for p in out_dir.iterdir() if p.is_dir())
    # No signing block should be present
    manifest = json.loads((pack_dir / "manifest.json").read_text())
    assert "signing" not in manifest
    assert manifest["format_version"] == "1.0"

    rc2, out2, err2 = _run_regula("verify", str(pack_dir))
    assert rc2 == 0, f"unsigned pack should verify: {err2}"
    assert "Signature:" not in out2  # no signature line when none present


def test_cli_verify_unsigned_pack_warns_under_strict(tmp_path):
    """Under --strict, an unsigned pack emits a warning (but still exits 0)."""
    out_dir = tmp_path / "pack-out"
    rc, _, err = _run_regula(
        "conform",
        "--project", "examples/code-completion-tool",
        "--output", str(out_dir),
    )
    assert rc == 0, err
    pack_dir = next(p for p in out_dir.iterdir() if p.is_dir())

    rc2, out2, err2 = _run_regula("verify", str(pack_dir), "--strict")
    # Unsigned is not a strict-mode FAILURE — the spec treats signing as
    # optional. The warning SHOULD surface though.
    assert rc2 == 0, f"unsigned pack under strict should still exit 0: rc={rc2}"
    assert "unsigned" in out2.lower() or "unsigned" in err2.lower()
