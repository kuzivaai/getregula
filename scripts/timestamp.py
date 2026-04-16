# regula-ignore
#!/usr/bin/env python3
"""
Regula RFC 3161 Timestamping

Sends audit trail hashes to a trusted timestamp authority (TSA) and returns
a timestamp token (TST) — a cryptographically signed, externally witnessed
proof that the hash existed at a specific time.

Uses only Python stdlib (urllib, struct, hashlib). No external dependencies.

Default TSA: FreeTSA (https://freetsa.org) — free, no registration required.
Custom TSA: set REGULA_TSA_URL environment variable.
"""

import hashlib
import os
import secrets
import struct
import urllib.request
import urllib.error
from datetime import datetime, timezone
from typing import Optional


def _require_http_url(url: str) -> None:
    """Reject non-http(s) schemes before urlopen (bandit B310 / semgrep
    dynamic-urllib guard). TSA URLs come from environment — must be
    validated because an operator could set REGULA_TSA_URL to file:// ."""
    if not isinstance(url, str) or not (url.startswith("http://") or url.startswith("https://")):
        raise ValueError(f"Refusing non-http(s) TSA URL: {url!r}")

DEFAULT_TSA_URL = os.environ.get("REGULA_TSA_URL", "https://freetsa.org/tsr")

# SHA-256 OID: 2.16.840.1.101.3.4.2.1 in DER encoding
_SHA256_OID_DER = bytes([
    0x30, 0x0d,                               # SEQUENCE (13 bytes)
    0x06, 0x09,                               # OID (9 bytes)
    0x60, 0x86, 0x48, 0x01, 0x65,            # 2.16.840.1.101
    0x03, 0x04, 0x02, 0x01,                  # .3.4.2.1
    0x05, 0x00,                               # NULL
])


def _der_len(n: int) -> bytes:
    """Encode an ASN.1 length in DER (short or long form)."""
    if n < 0x80:
        return bytes([n])
    elif n < 0x100:
        return bytes([0x81, n])
    else:
        return bytes([0x82, (n >> 8) & 0xFF, n & 0xFF])


def _der_seq(content: bytes) -> bytes:
    """Wrap bytes in DER SEQUENCE."""
    return bytes([0x30]) + _der_len(len(content)) + content


def _der_int(value: int, min_bytes: int = 1) -> bytes:
    """Encode a non-negative integer as DER INTEGER."""
    if value == 0:
        raw = b'\x00'
    else:
        raw = value.to_bytes((value.bit_length() + 7) // 8, 'big')
    # Prepend 0x00 if high bit set (avoid sign confusion)
    if raw[0] & 0x80:
        raw = b'\x00' + raw
    return bytes([0x02]) + _der_len(len(raw)) + raw


def _build_tsq(hash_bytes: bytes, nonce: Optional[int] = None) -> bytes:
    """Build a RFC 3161 TimeStampQuery DER structure for a SHA-256 hash.

    Parameters
    ----------
    hash_bytes : bytes
        The 32-byte SHA-256 digest to timestamp.
    nonce : int, optional
        Random nonce for replay protection. Generated if not provided.

    Returns
    -------
    bytes
        DER-encoded TimeStampReq suitable for POSTing to a TSA.
    """
    if len(hash_bytes) != 32:
        raise ValueError(f"Expected 32-byte SHA-256 hash, got {len(hash_bytes)} bytes")

    if nonce is None:
        nonce = int.from_bytes(secrets.token_bytes(8), 'big')

    # MessageImprint: SEQUENCE { AlgorithmIdentifier, OCTET STRING (hash) }
    hash_octet = bytes([0x04]) + _der_len(len(hash_bytes)) + hash_bytes
    msg_imprint = _der_seq(_SHA256_OID_DER + hash_octet)

    # version INTEGER (1)
    version = _der_int(1)

    # nonce INTEGER
    nonce_asn1 = _der_int(nonce)

    # certReq BOOLEAN TRUE
    cert_req = bytes([0x01, 0x01, 0xff])

    return _der_seq(version + msg_imprint + nonce_asn1 + cert_req)


def parse_tsr(tsr_bytes: bytes) -> dict:
    """Parse a RFC 3161 TimeStampResponse to extract status and token bytes.

    Only extracts PKIStatus and the raw token bytes. Full ASN.1 parsing is
    out of scope — the token is stored as hex for later verification.

    Returns
    -------
    dict with keys: status (int), token_hex (str)

    Raises
    ------
    ValueError
        If the response is not a valid DER SEQUENCE.
    """
    if not tsr_bytes or tsr_bytes[0] != 0x30:
        raise ValueError("TSR is not a DER SEQUENCE (expected 0x30 tag)")

    if len(tsr_bytes) < 4:
        raise ValueError("TSR too short to be valid")

    # PKIStatusInfo is the first element — extract status integer
    # TimeStampResp SEQUENCE {
    #   status PKIStatusInfo,  -- starts after outer SEQUENCE header
    #   timeStampToken [0] OPTIONAL
    # }
    # PKIStatusInfo SEQUENCE { status INTEGER, ... }
    # We navigate: outer_seq -> status_seq -> status_int
    try:
        pos = 1
        # Skip outer length
        if tsr_bytes[pos] & 0x80:
            len_bytes = tsr_bytes[pos] & 0x7f
            pos += len_bytes + 1
        else:
            pos += 1

        # Now at PKIStatusInfo SEQUENCE
        if tsr_bytes[pos] != 0x30:
            raise ValueError("Expected PKIStatusInfo SEQUENCE")
        pos += 1
        if tsr_bytes[pos] & 0x80:
            si_len_bytes = tsr_bytes[pos] & 0x7f
            pos += si_len_bytes + 1
        else:
            pos += 1

        # First element inside PKIStatusInfo is status INTEGER
        if tsr_bytes[pos] != 0x02:
            raise ValueError("Expected INTEGER for PKIStatus")
        pos += 1
        int_len = tsr_bytes[pos]
        pos += 1
        status_val = int.from_bytes(tsr_bytes[pos:pos + int_len], 'big')

    except (IndexError, struct.error) as e:
        raise ValueError(f"Failed to parse TSR structure: {e}") from e

    return {
        "status": status_val,
        "token_hex": tsr_bytes.hex(),
        "token_length": len(tsr_bytes),
    }


def request_timestamp(hash_hex: str, tsa_url: str = DEFAULT_TSA_URL, timeout: int = 10) -> dict:
    """Send a hash to a RFC 3161 TSA and return the timestamp token.

    Parameters
    ----------
    hash_hex : str
        Hex-encoded SHA-256 hash of the data to timestamp.
    tsa_url : str
        TSA endpoint URL. Defaults to FreeTSA.
    timeout : int
        Request timeout in seconds.

    Returns
    -------
    dict with keys: tsa_url, timestamp, tst_hex, hash_hex, status

    Raises
    ------
    RuntimeError
        On network error or TSA rejection.
    """
    _require_http_url(tsa_url)
    hash_bytes = bytes.fromhex(hash_hex)
    nonce = int.from_bytes(secrets.token_bytes(8), 'big')
    tsq = _build_tsq(hash_bytes, nonce=nonce)

    req = urllib.request.Request(
        tsa_url,
        data=tsq,
        headers={"Content-Type": "application/timestamp-query"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # nosec B310  # nosemgrep: dynamic-urllib-use-detected — scheme validated by _require_http_url above
            tsr_bytes = resp.read()
    except urllib.error.URLError as e:
        raise RuntimeError(f"TSA request failed: {e}") from e

    try:
        parsed = parse_tsr(tsr_bytes)
    except ValueError as e:
        raise RuntimeError(f"TSA returned invalid response: {e}") from e

    if parsed["status"] != 0:
        raise RuntimeError(
            f"TSA rejected request with status {parsed['status']} "
            f"(0=granted, 1=grantedWithMods, 2=rejection, 3=waiting)"
        )

    return {
        "tsa_url": tsa_url,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tst_hex": parsed["token_hex"],
        "hash_hex": hash_hex,
        "status": parsed["status"],
    }


# =====================================================================
# Regula Evidence Format v1.1 helpers (spec §4.6)
# =====================================================================
#
# Signing (v1.1) covers manifest integrity via Ed25519; timestamping
# (v1.1) adds *external* provenance — a TSA witness that the signed
# manifest existed at a given moment. The code above handles audit-
# trail timestamps with pure stdlib. Manifest timestamps go a step
# deeper: we need to extract messageImprint from the TimeStampToken
# at verification time, which requires proper ASN.1 decoding. That
# is gated behind the optional `asn1crypto` dependency (part of
# `regula[signing]`). Network requests remain stdlib-only.


class TimestampUnavailable(RuntimeError):
    """Raised when the `asn1crypto` dependency is not installed."""


class TimestampError(RuntimeError):
    """Raised when a timestamp operation fails (network, TSA, parse)."""


def _require_asn1crypto():
    """Return (tsp, algos, core) or raise TimestampUnavailable."""
    try:
        from asn1crypto import tsp, algos, core
    except ImportError as exc:
        raise TimestampUnavailable(
            "RFC 3161 manifest timestamping requires the `asn1crypto` "
            "package. Install it with: pip install regula-ai[signing]"
        ) from exc
    return tsp, algos, core


def request_manifest_timestamp(
    message: bytes,
    tsa_url: str = DEFAULT_TSA_URL,
    timeout: int = 30,
) -> dict:
    """Request an RFC 3161 timestamp over `message` for embedding in a manifest.

    Reuses the stdlib request path above (pure-DER TimeStampReq, urllib
    POST). Extracts the embedded TimeStampToken from the TSR so consumers
    don't need to carry the PKIStatusInfo wrapper.

    Returns a dict suitable for direct embedding as the manifest's
    `timestamp_authority` block:
        {
          "format": "rfc3161",
          "hash_algorithm": "sha256",
          "message_imprint": "<hex of sha256(message)>",
          "tsa_url": <url>,
          "requested_at": <iso8601>,
          "token": "<base64-encoded TimeStampToken bytes>",
          "gen_time": <iso8601 from TSTInfo>,
          "tsa_name": <str or None>,
          "chain_verified": false
        }

    Requires `regula[signing]` (uses asn1crypto to extract the token
    from the TSR envelope).
    """
    tsp, _, _ = _require_asn1crypto()
    _require_http_url(tsa_url)

    digest = hashlib.sha256(message).digest()
    digest_hex = digest.hex()

    # Use the existing stdlib request_timestamp — it returns the TSR hex
    result = request_timestamp(digest_hex, tsa_url=tsa_url, timeout=timeout)
    tsr_bytes = bytes.fromhex(result["tst_hex"])

    try:
        response = tsp.TimeStampResp.load(tsr_bytes)
        token = response["time_stamp_token"]
        token_bytes = token.dump()
        encap = token["content"]["encap_content_info"]
        encap_content = encap["content"]
        # asn1crypto auto-parses the TSTInfo if content_type == tst_info;
        # fall back to explicit load from raw DER bytes if not.
        if hasattr(encap_content, "parsed") and isinstance(encap_content.parsed, tsp.TSTInfo):
            tst_info = encap_content.parsed
        else:
            tst_info = tsp.TSTInfo.load(encap_content.contents)
        gen_time = tst_info["gen_time"].native.isoformat()
        imprint_hash_algo = tst_info["message_imprint"]["hash_algorithm"]["algorithm"].native
        imprint_hash = tst_info["message_imprint"]["hashed_message"].native
    except Exception as exc:
        raise TimestampError(
            f"Cannot parse TSR from {tsa_url}: {exc.__class__.__name__}: {exc}"
        ) from exc

    if imprint_hash_algo != "sha256":
        raise TimestampError(
            f"TSA response used {imprint_hash_algo!r} for message imprint, "
            f"but v1.1 requires sha256."
        )
    if imprint_hash != digest:
        raise TimestampError(
            "TSA response messageImprint does not match our request "
            "(possible replay or TSA misbehaviour)."
        )

    # asn1crypto fields use [] access and return VOID for absent optional
    # fields. Use a defensive try/except in case the TSA omitted the tsa
    # field altogether.
    tsa_name = None
    try:
        tsa_field = tst_info["tsa"]
        tsa_native = tsa_field.native
        if tsa_native is not None:
            tsa_name = str(tsa_native)
    except (KeyError, Exception):
        tsa_name = None

    return {
        "format": "rfc3161",
        "hash_algorithm": "sha256",
        "message_imprint": digest_hex,
        "tsa_url": tsa_url,
        "requested_at": result["timestamp"],
        "token": _base64_encode(token_bytes),
        "gen_time": gen_time,
        "tsa_name": tsa_name,
        "chain_verified": False,
    }


def _base64_encode(data: bytes) -> str:
    import base64
    return base64.b64encode(data).decode("ascii")


def verify_manifest_timestamp(
    manifest: dict,
    expected_message: bytes,
) -> tuple[bool, str]:
    """Verify a manifest's `timestamp_authority` block.

    Returns (ok, message). ok=True iff the block is present, parses as
    an RFC 3161 TimeStampToken, the messageImprint uses SHA-256, and
    its hash matches SHA-256(expected_message).

    The TSA's PKCS#7 signer-cert chain is NOT independently verified in
    v1.1. A consumer that needs strong TSA trust can extract the token
    and run it through a dedicated tool. We warn; we do not fail.

    If no timestamp block is present, returns (False, "no timestamp block").
    """
    block = manifest.get("timestamp_authority")
    if not block:
        return False, "no timestamp block"

    token_b64 = block.get("token")
    if not token_b64:
        return False, "timestamp block missing `token` field"

    import base64
    try:
        token_bytes = base64.b64decode(token_b64)
    except (ValueError, TypeError) as exc:
        return False, f"timestamp token is not valid base64: {exc}"

    try:
        tsp, _, _ = _require_asn1crypto()
        token = tsp.ContentInfo.load(token_bytes)
        encap = token["content"]["encap_content_info"]
        encap_content = encap["content"]
        # asn1crypto auto-parses the TSTInfo if content_type == tst_info;
        # fall back to explicit load from raw DER bytes if not.
        if hasattr(encap_content, "parsed") and isinstance(encap_content.parsed, tsp.TSTInfo):
            tst_info = encap_content.parsed
        else:
            tst_info = tsp.TSTInfo.load(encap_content.contents)
        imprint = tst_info["message_imprint"]
        digest = imprint["hashed_message"].native
        hash_algo = imprint["hash_algorithm"]["algorithm"].native
    except TimestampUnavailable as exc:
        return False, f"cannot verify — asn1crypto not installed: {exc}"
    except Exception as exc:
        return False, f"cannot parse timestamp token: {exc.__class__.__name__}: {exc}"

    if hash_algo != "sha256":
        return False, (
            f"timestamp hash_algorithm {hash_algo!r} is not sha256"
        )

    expected = hashlib.sha256(expected_message).digest()
    if digest != expected:
        return False, (
            f"timestamp messageImprint does not match manifest digest "
            f"(expected {expected.hex()[:16]}…, got {digest.hex()[:16]}…)"
        )

    return True, (
        f"timestamp hash matches manifest; gen_time="
        f"{tst_info['gen_time'].native.isoformat()} "
        f"(signer-chain NOT independently verified)"
    )


def is_manifest_timestamp_available() -> bool:
    """Return True iff asn1crypto is importable."""
    try:
        _require_asn1crypto()
        return True
    except TimestampUnavailable:
        return False
