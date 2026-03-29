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
        with urllib.request.urlopen(req, timeout=timeout) as resp:
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
