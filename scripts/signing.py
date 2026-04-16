#!/usr/bin/env python3
# regula-ignore
"""Ed25519 manifest signing for Regula Evidence Format v1.1.

Implements the optional `signing` block reserved in the v1 spec §4.3.
Signing is OFF by default and gated behind the `regula[signing]` optional
extra; the core Regula CLI remains stdlib-only. A manifest may carry a
signing block; consumers that cannot verify it (e.g. `cryptography` not
installed) MUST warn but not fail unless `--strict` is set.

Canonical form: the bytes signed are a JSON serialisation of the manifest
**with the `signing` block excluded**, produced with:
    json.dumps(manifest_without_signing, sort_keys=True, separators=(",", ":"))
encoded as UTF-8. Consumers MUST reproduce this form exactly before
verifying. The canonical form is stable across Regula versions.

Key material:
- Default key path: `~/.regula/signing.key` (private, PEM, no passphrase).
- Corresponding public key: `~/.regula/signing.key.pub` (PEM).
- If the private key does not exist, a new Ed25519 keypair is generated on
  first `--sign` use. Users should back up the key before relying on it
  as a provenance root.

All errors are raised as `SigningUnavailable` (missing dependency) or
`SigningError` (operational failures). The caller decides whether to
degrade gracefully or abort.
"""

from __future__ import annotations

import base64
import json
import os
import stat
from pathlib import Path
from typing import Any


class SigningUnavailable(RuntimeError):
    """Raised when the `cryptography` dependency is not installed."""


class SigningError(RuntimeError):
    """Raised when signing or verification fails operationally."""


SIGNATURE_ALGORITHM = "ed25519"
CANONICAL_SERIALIZATION = "json-sort-keys-no-whitespace-utf8"

# Default on-disk key location. Overridable via REGULA_SIGNING_KEY env var.
DEFAULT_KEY_DIR = Path.home() / ".regula"
DEFAULT_KEY_PATH = DEFAULT_KEY_DIR / "signing.key"


def _require_cryptography() -> Any:
    """Return the `cryptography` module, or raise SigningUnavailable."""
    try:
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric import ed25519
    except ImportError as exc:
        raise SigningUnavailable(
            "Ed25519 signing requires the `cryptography` package. "
            "Install it with: pip install regula-ai[signing]"
        ) from exc
    return serialization, ed25519


def default_key_path() -> Path:
    """Return the active signing key path (env var override supported)."""
    override = os.environ.get("REGULA_SIGNING_KEY")
    if override:
        return Path(override).expanduser().resolve()
    return DEFAULT_KEY_PATH


def load_or_create_keypair(
    key_path: Path | None = None,
) -> tuple[Any, Any]:
    """Load an existing Ed25519 private key or create a new one.

    Returns (private_key, public_key) as `cryptography` key objects. The
    caller must handle serialisation separately if storing them.
    """
    serialization, ed25519 = _require_cryptography()

    path = key_path or default_key_path()
    pub_path = path.with_suffix(path.suffix + ".pub")

    if path.exists():
        try:
            private_bytes = path.read_bytes()
            private_key = serialization.load_pem_private_key(
                private_bytes, password=None
            )
        except Exception as exc:
            raise SigningError(f"Cannot load private key from {path}: {exc}") from exc
        public_key = private_key.public_key()
        return private_key, public_key

    # Generate new keypair
    path.parent.mkdir(parents=True, exist_ok=True)
    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key = private_key.public_key()

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    path.write_bytes(private_pem)
    # Restrict private key permissions on POSIX systems
    try:
        os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)
    except OSError:
        import warnings
        warnings.warn(
            f"Could not restrict permissions on {path} — the private key "
            f"may be readable by other users on this system. Consider "
            f"moving it to a secure location with restricted permissions.",
            stacklevel=2,
        )

    pub_path.write_bytes(public_pem)
    return private_key, public_key


# Keys that are layered onto the manifest AFTER the canonical bytes are
# fixed. All must be stripped before serialisation so a sign-then-timestamp
# producer and a verifier both compute the same canonical form.
_POST_CANONICAL_KEYS = frozenset({"signing", "timestamp_authority"})


def canonicalize_manifest_for_signing(manifest: dict) -> bytes:
    """Produce the canonical byte sequence that a signature covers.

    The `signing` AND `timestamp_authority` blocks are stripped before
    serialisation so a freshly signed manifest produces the same canonical
    bytes as the one later verified, even if a timestamp was layered in
    after signing. The serialisation is sorted-key, no-whitespace JSON.
    """
    payload = {k: v for k, v in manifest.items() if k not in _POST_CANONICAL_KEYS}
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def public_key_pem_b64(public_key: Any) -> str:
    """Serialise a public key as base64-encoded PEM for embedding."""
    serialization, _ = _require_cryptography()
    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return base64.b64encode(pem).decode("ascii")


def load_public_key_from_b64(pem_b64: str) -> Any:
    """Load a public key from a base64-encoded PEM blob."""
    serialization, _ = _require_cryptography()
    try:
        pem = base64.b64decode(pem_b64)
        return serialization.load_pem_public_key(pem)
    except Exception as exc:
        raise SigningError(f"Cannot parse embedded public key: {exc}") from exc


def sign_manifest(
    manifest: dict,
    private_key: Any | None = None,
    key_path: Path | None = None,
) -> dict:
    """Return a `signing` block for the given manifest.

    If `private_key` is None, load (or create) the default keypair at
    `key_path` (or the REGULA_SIGNING_KEY path).
    """
    if private_key is None:
        private_key, public_key = load_or_create_keypair(key_path)
    else:
        public_key = private_key.public_key()

    canonical = canonicalize_manifest_for_signing(manifest)
    signature = private_key.sign(canonical)

    return {
        "algorithm": SIGNATURE_ALGORITHM,
        "canonical_serialization": CANONICAL_SERIALIZATION,
        "signature": base64.b64encode(signature).decode("ascii"),
        "public_key": public_key_pem_b64(public_key),
    }


def verify_manifest_signature(manifest: dict) -> tuple[bool, str]:
    """Verify a manifest's signing block against its canonical form.

    Returns (ok, message). `ok` is True only if a signing block is present,
    well-formed, uses Ed25519, and cryptographically verifies against the
    embedded public key. If no signing block is present, returns
    (False, "no signing block"). Callers distinguish that case from
    verification failure.
    """
    signing_block = manifest.get("signing")
    if not signing_block:
        return False, "no signing block"

    if signing_block.get("algorithm") != SIGNATURE_ALGORITHM:
        return False, (
            f"unsupported algorithm {signing_block.get('algorithm')!r}; "
            f"only {SIGNATURE_ALGORITHM!r} is recognised in v1.1"
        )

    if signing_block.get("canonical_serialization") != CANONICAL_SERIALIZATION:
        return False, (
            f"unknown canonical_serialization "
            f"{signing_block.get('canonical_serialization')!r}"
        )

    try:
        signature = base64.b64decode(signing_block["signature"])
    except (KeyError, ValueError) as exc:
        return False, f"malformed signature field: {exc}"

    try:
        public_key = load_public_key_from_b64(signing_block["public_key"])
    except (KeyError, SigningError) as exc:
        return False, f"malformed public_key field: {exc}"

    canonical = canonicalize_manifest_for_signing(manifest)

    # cryptography's verify() raises InvalidSignature on mismatch.
    # Narrow the catch so a genuine library-level bug (e.g. algorithm
    # backend failure) does not get mis-attributed as "signature invalid"
    # — the operator needs to distinguish tampering from infrastructure
    # failure. InvalidSignature is the one we expect and convert to a
    # clear verdict; anything else propagates.
    try:
        from cryptography.exceptions import InvalidSignature
    except ImportError as exc:  # should not happen if we got this far
        return False, f"cryptography import failed: {exc}"
    try:
        public_key.verify(signature, canonical)
    except InvalidSignature:
        return False, "signature invalid: manifest does not match signed canonical form"

    return True, "ed25519 signature verified"


def is_signing_available() -> bool:
    """Return True if `cryptography` is importable."""
    try:
        _require_cryptography()
        return True
    except SigningUnavailable:
        return False
