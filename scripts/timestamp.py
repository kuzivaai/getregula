#!/usr/bin/env python3
# regula-ignore
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
import ipaddress
import os
import secrets
import struct
import urllib.parse
import urllib.request
import urllib.error
from datetime import datetime, timezone
from typing import Optional

# RFC 1918 / loopback / link-local networks that must never be reachable via
# an operator-supplied TSA URL (SSRF protection).
_BLOCKED_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),      # IPv4 loopback
    ipaddress.ip_network("10.0.0.0/8"),        # RFC 1918
    ipaddress.ip_network("172.16.0.0/12"),     # RFC 1918
    ipaddress.ip_network("192.168.0.0/16"),    # RFC 1918
    ipaddress.ip_network("169.254.0.0/16"),    # link-local / AWS metadata
    ipaddress.ip_network("::1/128"),           # IPv6 loopback
    ipaddress.ip_network("fc00::/7"),          # IPv6 ULA
    ipaddress.ip_network("fe80::/10"),         # IPv6 link-local
]


def _require_http_url(url: str) -> None:
    """Reject non-http(s) schemes and internal/metadata hosts before urlopen.

    Guards against:
    - Non-http(s) schemes (file://, ftp://, etc.)  — bandit B310 / semgrep
      dynamic-urllib guard.
    - SSRF to loopback, RFC 1918, and cloud-metadata addresses — an operator
      could set REGULA_TSA_URL to http://169.254.169.254/latest/meta-data/.

    The _REGULA_TESTING_ALLOW_LOCAL env var bypasses the private-IP check
    for test suites that run a local mock TSA on 127.0.0.1.  This variable
    is never set in production; it is only used in the test harness.
    """
    if not isinstance(url, str) or not (url.startswith("http://") or url.startswith("https://")):
        raise ValueError(f"Refusing non-http(s) TSA URL: {url!r}")

    # Test harness bypass: allow localhost when explicitly opted in.
    if os.environ.get("_REGULA_TESTING_ALLOW_LOCAL") == "1":
        return

    parsed = urllib.parse.urlparse(url)
    hostname = parsed.hostname or ""

    # Reject bare "localhost" and any case variant
    if hostname.lower() in ("localhost", "localhost."):
        raise ValueError(f"Refusing internal TSA URL (localhost): {url!r}")

    # Attempt to resolve the hostname as a literal IP address.  A DNS-based
    # SSRF bypass (resolving a public name to a private IP) is out of scope
    # for a stdlib-only check — the operator controls the DNS environment.
    try:
        addr = ipaddress.ip_address(hostname)
    except ValueError:
        # Not a literal IP — accept the hostname (DNS lookup happens later).
        return

    for net in _BLOCKED_NETWORKS:
        if addr in net:
            raise ValueError(
                f"Refusing TSA URL pointing to internal/metadata address "
                f"{addr} (matched {net}): {url!r}"
            )

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


def request_timestamp(hash_hex: str, tsa_url: str = DEFAULT_TSA_URL, timeout: int = 30) -> dict:
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

    # asn1crypto fields use [] access and may return a VOID sentinel for
    # absent optional fields. Narrow the catch so a real bug inside
    # asn1crypto (e.g. a version bump changing VOID semantics) surfaces
    # instead of being masked as "no TSA name".
    tsa_name = None
    try:
        tsa_field = tst_info["tsa"]
        tsa_native = tsa_field.native
        if tsa_native is not None:
            tsa_name = str(tsa_native)
    except (KeyError, ValueError, AttributeError, TypeError):
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

    IMPORTANT — scope of this check: it verifies the messageImprint HASH
    only. It does NOT verify the token's PKCS#7 SignedData signature at
    all (neither the signature itself nor the signer-cert chain). A hash
    match therefore proves the imprint corresponds to this manifest, but
    does NOT cryptographically authenticate the `gen_time`: a party who
    knows the (public) canonicalisation can craft a token with an
    arbitrary gen_time and a matching imprint. A consumer that needs a
    trustworthy time attestation must extract the token and validate its
    signature and signer chain with a dedicated RFC 3161 tool. We warn;
    we do not fail.

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
        f"(hash match only — token signature NOT independently verified, "
        f"so gen_time is not cryptographically authenticated)"
    )


# --- RFC 3161 token signature verification -----------------------------
#
# `verify_manifest_timestamp` above checks the messageImprint hash ONLY.
# That proves the token's imprint corresponds to this manifest, but not
# that a real TSA issued it: anyone who knows the (public) canonicalisation
# can mint a token with an arbitrary gen_time and a matching imprint. The
# functions below close that gap — they verify the token's PKCS#7
# SignedData signature (RFC 5652 §5.4) against the signer certificate
# carried in the token, and require the RFC 3161 §2.3 critical
# timestamping EKU.
#
# What this deliberately does NOT do (stated here, in the returned detail
# string, and in spec §4.6.4 so no caller can mistake the guarantee):
#   - Revocation (CRL/OCSP). Regula's core is zero-network by design; a
#     revocation check cannot be performed offline. Out of scope.
#   - Full RFC 5280 path validation (name constraints, policy mapping,
#     policy qualifiers). The optional trust-anchor check below is a
#     LIMITED chain check: issuer signature, CA basicConstraints, and
#     validity window at gen_time.
#
# The crypto itself is done by `cryptography` (already a `[signing]`
# dependency). We do not hand-roll any primitive.

_OID_CONTENT_TYPE = "1.2.840.113549.1.9.3"
_OID_MESSAGE_DIGEST = "1.2.840.113549.1.9.4"
_OID_TST_INFO = "1.2.840.113549.1.9.16.1.4"
_OID_EKU_TIMESTAMPING = "1.3.6.1.5.5.7.3.8"

# Digests we will accept for a signature we are willing to call verified.
# md5/sha1 are collision-broken; reporting a SHA-1 signature as verified in
# a compliance tool would overstate the guarantee, so they are refused
# rather than silently accepted.
_ACCEPTED_SIG_DIGESTS = frozenset({"sha256", "sha384", "sha512"})


def _require_cryptography():
    """Return the cryptography primitives needed, or raise TimestampUnavailable."""
    try:
        from cryptography import x509
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import ec, padding
    except ImportError as exc:
        raise TimestampUnavailable(
            "RFC 3161 signature verification requires the `cryptography` "
            "package. Install it with: pip install regula-ai[signing]"
        ) from exc
    return x509, hashes, padding, ec


def _hash_for(name: str):
    """Map an asn1crypto digest name to a cryptography hash instance."""
    _, hashes, _, _ = _require_cryptography()
    table = {
        "sha256": hashes.SHA256,
        "sha384": hashes.SHA384,
        "sha512": hashes.SHA512,
    }
    cls = table.get(name)
    return cls() if cls else None


def _find_signer_cert(signed_data, signer_info):
    """Locate the signer's certificate inside the token, or return None.

    Handles both SignerIdentifier choices (issuerAndSerialNumber and
    subjectKeyIdentifier). Comparison is on DER bytes, not `.native`, so
    equivalent-but-differently-encoded names cannot produce a false match.
    """
    sid = signer_info["sid"]
    certs = signed_data["certificates"]
    if certs is None:
        return None

    if sid.name == "issuer_and_serial_number":
        want_issuer = sid.chosen["issuer"].dump()
        want_serial = sid.chosen["serial_number"].native
        for choice in certs:
            if choice.name != "certificate":
                continue
            cert = choice.chosen
            tbs = cert["tbs_certificate"]
            if (tbs["issuer"].dump() == want_issuer
                    and tbs["serial_number"].native == want_serial):
                return cert
    elif sid.name == "subject_key_identifier":
        want_ski = sid.chosen.native
        for choice in certs:
            if choice.name != "certificate":
                continue
            cert = choice.chosen
            if cert.key_identifier == want_ski:
                return cert
    return None


def _get_signed_attr(signed_attrs, oid: str):
    """Return the values of the signed attribute with `oid`, or None."""
    for attr in signed_attrs:
        if attr["type"].dotted == oid:
            return attr["values"]
    return None


def _check_timestamping_eku(cert_der: bytes) -> Optional[str]:
    """Return an error string if the cert is not a valid TSA signer cert.

    RFC 3161 §2.3: the TSA signing certificate MUST contain an
    extendedKeyUsage extension with exactly the id-kp-timeStamping value,
    and that extension MUST be marked critical.
    """
    x509, _, _, _ = _require_cryptography()
    cert = x509.load_der_x509_certificate(cert_der)
    try:
        ext = cert.extensions.get_extension_for_class(x509.ExtendedKeyUsage)
    except x509.ExtensionNotFound:
        return ("signer certificate has no extendedKeyUsage extension "
                "(RFC 3161 §2.3 requires id-kp-timeStamping)")
    oids = [oid.dotted_string for oid in ext.value]
    if _OID_EKU_TIMESTAMPING not in oids:
        return (f"signer certificate extendedKeyUsage {oids} does not include "
                f"id-kp-timeStamping ({_OID_EKU_TIMESTAMPING})")
    if len(oids) != 1:
        return (f"signer certificate extendedKeyUsage must contain ONLY "
                f"id-kp-timeStamping (RFC 3161 §2.3), found {oids}")
    if not ext.critical:
        return ("signer certificate extendedKeyUsage is not marked critical "
                "(RFC 3161 §2.3 requires it)")
    return None


def _verify_signature(cert_der: bytes, sig_algo: str, digest_name: str,
                      signature: bytes, signed_bytes: bytes,
                      sig_params) -> Optional[tuple[str, str]]:
    """Verify `signature` over `signed_bytes`.

    Returns None on success, else a (status, message) pair where status is
    "INVALID" or "UNSUPPORTED". The two MUST NOT be collapsed: "I cannot
    evaluate this algorithm" is not evidence of tampering, and reporting it
    as INVALID would hard-fail packs from a conforming TSA whose algorithms
    this implementation simply does not cover (spec §4.6.3 item 3).
    """
    x509, hashes, padding, ec = _require_cryptography()
    cert = x509.load_der_x509_certificate(cert_der)
    public_key = cert.public_key()
    hash_obj = _hash_for(digest_name)
    if hash_obj is None:
        return "UNSUPPORTED", f"unsupported signature digest {digest_name!r}"

    from cryptography.exceptions import InvalidSignature
    try:
        if sig_algo == "rsassa_pkcs1v15":
            public_key.verify(signature, signed_bytes,
                              padding.PKCS1v15(), hash_obj)
        elif sig_algo == "rsassa_pss":
            # Salt length and MGF digest come from the algorithm parameters;
            # defaulting them would let a mismatched token verify.
            try:
                salt_len = sig_params["salt_length"].native
                mgf_hash = sig_params["mask_gen_algorithm"]["parameters"]["algorithm"].native
            except Exception as exc:
                # Declared RSASSA-PSS but the parameters are unreadable:
                # that is a malformed token, not an unimplemented algorithm.
                return "INVALID", f"cannot read RSASSA-PSS parameters: {exc}"
            mgf_hash_obj = _hash_for(mgf_hash)
            if mgf_hash_obj is None:
                return "UNSUPPORTED", f"unsupported RSASSA-PSS MGF digest {mgf_hash!r}"
            public_key.verify(
                signature, signed_bytes,
                padding.PSS(mgf=padding.MGF1(mgf_hash_obj), salt_length=salt_len),
                hash_obj,
            )
        elif sig_algo == "ecdsa":
            public_key.verify(signature, signed_bytes, ec.ECDSA(hash_obj))
        else:
            # e.g. Ed25519/Ed448/DSA — asn1crypto names them, we have not
            # implemented them. Degrade, do not allege tampering.
            return "UNSUPPORTED", (
                f"token is signed with {sig_algo!r}, which this implementation "
                f"does not verify (supported: RSA PKCS#1 v1.5, RSASSA-PSS, "
                f"ECDSA), so the signature was not evaluated"
            )
    except InvalidSignature:
        return "INVALID", "token signature does not verify against the signer certificate"
    except Exception as exc:
        return "INVALID", f"signature verification error: {exc.__class__.__name__}: {exc}"
    return None


def _limited_chain_check(cert_der: bytes, anchor_pem: bytes,
                         gen_time) -> Optional[str]:
    """LIMITED chain check: anchor signed the signer cert, and both were
    within their validity window at `gen_time`.

    This is NOT full RFC 5280 path validation. No revocation, no name
    constraints, no policy processing, and no intermediate chain building
    (the anchor must be the direct issuer). Callers must not present the
    result as full PKI validation — see spec §4.6.4.
    """
    x509, hashes, padding, ec = _require_cryptography()
    from cryptography.exceptions import InvalidSignature

    cert = x509.load_der_x509_certificate(cert_der)
    try:
        anchor = x509.load_pem_x509_certificate(anchor_pem)
    except Exception as exc:
        return f"cannot parse trust anchor PEM: {exc.__class__.__name__}: {exc}"

    if cert.issuer != anchor.subject:
        return ("trust anchor subject does not match the signer certificate's "
                "issuer (no intermediate chain building is performed)")

    try:
        basic = anchor.extensions.get_extension_for_class(x509.BasicConstraints)
        if not basic.value.ca:
            return "trust anchor is not a CA certificate (basicConstraints CA=false)"
    except x509.ExtensionNotFound:
        return "trust anchor has no basicConstraints extension"

    # Validity window must cover the asserted signing time, not "now".
    gen = gen_time
    if gen.tzinfo is None:
        gen = gen.replace(tzinfo=timezone.utc)
    for label, c in (("signer certificate", cert), ("trust anchor", anchor)):
        not_before = c.not_valid_before_utc
        not_after = c.not_valid_after_utc
        if not (not_before <= gen <= not_after):
            return (f"{label} was not valid at gen_time {gen.isoformat()} "
                    f"(valid {not_before.isoformat()} .. {not_after.isoformat()})")

    try:
        anchor_key = anchor.public_key()
        if isinstance(anchor_key, ec.EllipticCurvePublicKey):
            anchor_key.verify(cert.signature, cert.tbs_certificate_bytes,
                              ec.ECDSA(cert.signature_hash_algorithm))
        else:
            anchor_key.verify(cert.signature, cert.tbs_certificate_bytes,
                              padding.PKCS1v15(), cert.signature_hash_algorithm)
    except InvalidSignature:
        return "signer certificate was not signed by the supplied trust anchor"
    except Exception as exc:
        return f"chain check error: {exc.__class__.__name__}: {exc}"
    return None


def verify_timestamp_token_signature(
    token_bytes: bytes,
    trust_anchor_pem: Optional[bytes] = None,
) -> tuple[str, str]:
    """Verify the PKCS#7 SignedData signature of an RFC 3161 TimeStampToken.

    Returns (status, detail) where status is one of:
      - "SIGNATURE_VERIFIED" — the signature verifies against the signer
        certificate embedded in the token, the signed attributes bind that
        signature to this exact TSTInfo, and the certificate carries the
        critical id-kp-timeStamping EKU. The signer's *identity* is only as
        trustworthy as the embedded certificate: nothing anchors it yet.
      - "CHAIN_VERIFIED"     — as above, plus the signer certificate chains
        directly to the caller-supplied trust anchor and both certificates
        were valid at gen_time. Still no revocation checking.
      - "INVALID"            — the signature is provably bad, or the token
        violates RFC 3161 in a way a conforming TSA never would. Callers
        SHOULD fail on this.
      - "UNSUPPORTED"        — the token cannot be evaluated by this
        implementation (algorithm we do not support, no embedded signer
        certificate, no signed attributes, weak digest). This is NOT
        evidence of tampering, so callers should degrade to the hash-only
        verdict and say so rather than failing a previously-valid pack.
      - "UNVERIFIABLE"       — asn1crypto/cryptography not installed.

    The INVALID/UNSUPPORTED split matters: hard-failing on everything we
    cannot parse would break packs from a conforming TSA that happens to
    use an algorithm we have not implemented. We only fail when we can
    actually prove something is wrong.

    This function does not look at the messageImprint; pair it with
    `verify_manifest_timestamp`, which binds the token to the manifest.
    """
    try:
        _require_asn1crypto()
        _require_cryptography()
        from asn1crypto import cms
    except TimestampUnavailable as exc:
        return "UNVERIFIABLE", str(exc)
    except ImportError as exc:
        return "UNVERIFIABLE", f"asn1crypto is missing the cms module: {exc}"

    try:
        content_info = cms.ContentInfo.load(token_bytes)
        if content_info["content_type"].native != "signed_data":
            return "INVALID", (
                f"token is {content_info['content_type'].native!r}, "
                f"expected a PKCS#7 signed_data structure"
            )
        signed_data = content_info["content"]
        signer_infos = signed_data["signer_infos"]
    except Exception as exc:
        return "INVALID", f"cannot parse SignedData: {exc.__class__.__name__}: {exc}"

    # More than one signer makes "the" signature ambiguous — a token where
    # one of two signatures verifies must not read as verified.
    if len(signer_infos) != 1:
        return "UNSUPPORTED", (
            f"token has {len(signer_infos)} SignerInfos; exactly 1 is required "
            f"for an unambiguous verdict, so the signature was not evaluated"
        )
    signer_info = signer_infos[0]

    signer_cert = _find_signer_cert(signed_data, signer_info)
    if signer_cert is None:
        return "UNSUPPORTED", (
            "token does not embed the signer's certificate, so the signature "
            "cannot be verified from the token alone"
        )
    cert_der = signer_cert.dump()

    eku_error = _check_timestamping_eku(cert_der)
    if eku_error:
        return "INVALID", eku_error

    signed_attrs = signer_info["signed_attrs"]
    if signed_attrs is None or len(signed_attrs) == 0:
        return "UNSUPPORTED", (
            "token has no signed attributes, so there is nothing binding a "
            "signature to this TSTInfo to evaluate"
        )

    try:
        encap = signed_data["encap_content_info"]
        econtent = encap["content"]
        tst_der = econtent.contents if hasattr(econtent, "contents") else bytes(econtent)
        digest_name = signer_info["digest_algorithm"]["algorithm"].native
    except Exception as exc:
        return "INVALID", f"cannot read encapContentInfo: {exc.__class__.__name__}: {exc}"

    if digest_name not in _ACCEPTED_SIG_DIGESTS:
        return "UNSUPPORTED", (
            f"token is signed with {digest_name!r}, which is not collision "
            f"resistant; refusing to report it as verified "
            f"(accepted: {sorted(_ACCEPTED_SIG_DIGESTS)})"
        )

    # contentType signed attr must say this is a TSTInfo.
    ct_values = _get_signed_attr(signed_attrs, _OID_CONTENT_TYPE)
    if ct_values is None or len(ct_values) != 1:
        return "INVALID", "token is missing a single contentType signed attribute"
    if ct_values[0].dotted != _OID_TST_INFO:
        return "INVALID", (
            f"signed contentType is {ct_values[0].dotted}, expected id-ct-TSTInfo "
            f"({_OID_TST_INFO})"
        )

    # messageDigest signed attr must equal the digest of the encapsulated
    # TSTInfo — this is what binds the signature to the timestamp content.
    md_values = _get_signed_attr(signed_attrs, _OID_MESSAGE_DIGEST)
    if md_values is None or len(md_values) != 1:
        return "INVALID", "token is missing a single messageDigest signed attribute"
    declared_digest = md_values[0].native
    actual_digest = hashlib.new(digest_name, tst_der).digest()
    if declared_digest != actual_digest:
        return "INVALID", (
            "signed messageDigest attribute does not match the encapsulated "
            "TSTInfo — the signature does not cover this timestamp content"
        )

    # RFC 5652 §5.4: the signature is computed over the DER encoding of the
    # signed attributes as a SET OF, not over the implicit [0] tagged form
    # that appears in the message.
    try:
        signed_bytes = signed_attrs.untag().dump(force=True)
    except Exception as exc:
        return "INVALID", f"cannot re-encode signed attributes: {exc}"

    try:
        sig_algo = signer_info["signature_algorithm"].signature_algo
        sig_params = signer_info["signature_algorithm"]["parameters"]
    except Exception as exc:
        # asn1crypto raises ValueError for a signature-algorithm OID it does
        # not know. An algorithm we cannot name is one we cannot evaluate —
        # degrade rather than allege tampering. The messageImprint check is
        # independent of this and still stands.
        try:
            raw_oid = signer_info["signature_algorithm"]["algorithm"].dotted
        except Exception:
            raw_oid = "unreadable"
        return "UNSUPPORTED", (
            f"token uses signature algorithm OID {raw_oid}, which this "
            f"implementation does not recognise ({exc.__class__.__name__}), "
            f"so the signature was not evaluated"
        )
    signature = signer_info["signature"].native

    sig_problem = _verify_signature(cert_der, sig_algo, digest_name,
                                    signature, signed_bytes, sig_params)
    if sig_problem:
        return sig_problem  # (status, detail) — INVALID or UNSUPPORTED

    base_detail = (
        f"RFC 3161 token signature verified ({sig_algo}/{digest_name}) against "
        f"the embedded signer certificate; signed attributes bind it to this "
        f"TSTInfo; certificate carries the critical id-kp-timeStamping EKU"
    )

    if trust_anchor_pem is None:
        return "SIGNATURE_VERIFIED", (
            base_detail + ". No trust anchor supplied, so the signer's IDENTITY "
            "is unverified — the certificate is self-asserted by the token. "
            "Pass --tsa-trust-anchor to chain it. No revocation checking."
        )

    try:
        tsp, _, _ = _require_asn1crypto()
        tst_info = tsp.TSTInfo.load(tst_der)
        gen_time = tst_info["gen_time"].native
    except Exception as exc:
        return "INVALID", f"cannot read gen_time for the chain check: {exc}"

    chain_error = _limited_chain_check(cert_der, trust_anchor_pem, gen_time)
    if chain_error:
        return "INVALID", f"chain check failed: {chain_error}"

    return "CHAIN_VERIFIED", (
        base_detail + f"; signer certificate chains to the supplied trust anchor "
        f"and both were valid at gen_time {gen_time.isoformat()}. LIMITED chain "
        f"check only — no revocation (CRL/OCSP), no name-constraint or policy "
        f"validation, no intermediate chain building."
    )


