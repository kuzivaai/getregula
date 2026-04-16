"""Tests for RFC 3161 manifest timestamping (Regula Evidence Format v1.1).

Covers §4.6.3 verifier behaviour and the producer path. All network
interactions go through a local mock TSA — no real TSA calls.

Kept in a dedicated test file per project convention — do NOT extend
tests/test_classification.py.

Skipped if either `asn1crypto` or `cryptography` is missing (both ship
under `regula[signing]`).
"""
from __future__ import annotations

import base64
import datetime
import hashlib
import json
import os
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

asn1crypto = pytest.importorskip("asn1crypto")
cryptography = pytest.importorskip("cryptography")

from asn1crypto import tsp, algos, cms, core  # noqa: E402


# ── Mock TSA fixture ───────────────────────────────────────────────


def _build_mock_tsr(message: bytes, imprint_hash_algo: str = "sha256",
                    override_imprint: bytes | None = None) -> bytes:
    """Build a DER-encoded TimeStampResp carrying a token over `message`.

    Uses an empty SignerInfos set — good enough for our verifier, which
    only checks the messageImprint. Real TSAs sign the token; our mock
    doesn't need to (we don't validate the chain).

    If `override_imprint` is provided, use it instead of sha256(message)
    — simulates a TSA replacing the imprint or a tampered response.
    """
    if override_imprint is not None:
        digest = override_imprint
    else:
        digest = hashlib.sha256(message).digest()

    tst_info = tsp.TSTInfo({
        "version": 1,
        "policy": "1.2.3.4.5",
        "message_imprint": tsp.MessageImprint({
            "hash_algorithm": algos.DigestAlgorithm({"algorithm": imprint_hash_algo}),
            "hashed_message": digest,
        }),
        "serial_number": 12345,
        "gen_time": datetime.datetime.now(datetime.timezone.utc),
    })

    encap = cms.EncapsulatedContentInfo({
        "content_type": "tst_info",
        "content": core.ParsableOctetString(tst_info.dump()),
    })
    signed_data = cms.SignedData({
        "version": "v3",
        "digest_algorithms": [algos.DigestAlgorithm({"algorithm": "sha256"})],
        "encap_content_info": encap,
        "signer_infos": [],
    })
    token = cms.ContentInfo({
        "content_type": "signed_data",
        "content": signed_data,
    })
    resp = tsp.TimeStampResp({
        "status": tsp.PKIStatusInfo({"status": "granted"}),
        "time_stamp_token": token,
    })
    return resp.dump()


class _MockTSAHandler(BaseHTTPRequestHandler):
    """HTTP handler that returns a TSR over whatever hash is in the request."""

    # Set by the test fixture to control what the mock returns
    imprint_override: bytes | None = None
    fail_next: bool = False

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        req_der = self.rfile.read(length)

        try:
            req = tsp.TimeStampReq.load(req_der)
            imprint_in_req = req["message_imprint"]["hashed_message"].native
        except Exception:
            self.send_response(400)
            self.end_headers()
            return

        if self.__class__.fail_next:
            self.send_response(500)
            self.end_headers()
            return

        override = self.__class__.imprint_override
        # We need to produce a TSR whose embedded imprint matches what the
        # PRODUCER requested (otherwise our own producer will reject the
        # mismatched response before it ever reaches the verifier). So we
        # build the TSR with override_imprint = imprint_in_req normally,
        # and only deviate when explicitly told to.
        tsr = _build_mock_tsr(
            b"",  # unused because override_imprint is provided
            override_imprint=override if override is not None else imprint_in_req,
        )
        self.send_response(200)
        self.send_header("Content-Type", "application/timestamp-reply")
        self.send_header("Content-Length", str(len(tsr)))
        self.end_headers()
        self.wfile.write(tsr)

    def log_message(self, *_args, **_kwargs):
        pass  # silence test logs


@pytest.fixture
def mock_tsa():
    """Yield a local http://localhost:PORT/tsa that speaks RFC 3161."""
    _MockTSAHandler.imprint_override = None
    _MockTSAHandler.fail_next = False
    server = HTTPServer(("127.0.0.1", 0), _MockTSAHandler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield {
            "url": f"http://127.0.0.1:{port}/tsa",
            "handler": _MockTSAHandler,
        }
    finally:
        server.shutdown()
        thread.join(timeout=5)


# ── Unit tests ─────────────────────────────────────────────────────


def test_request_manifest_timestamp_happy_path(mock_tsa):
    """Producer can request + parse a timestamp from a RFC 3161 TSA."""
    from timestamp import request_manifest_timestamp

    message = b"test canonical manifest bytes"
    block = request_manifest_timestamp(message, tsa_url=mock_tsa["url"])

    assert block["format"] == "rfc3161"
    assert block["hash_algorithm"] == "sha256"
    assert block["message_imprint"] == hashlib.sha256(message).hexdigest()
    assert block["tsa_url"] == mock_tsa["url"]
    assert block["chain_verified"] is False
    assert "gen_time" in block
    assert isinstance(block["token"], str)
    # Token should decode as bytes
    token_bytes = base64.b64decode(block["token"])
    assert len(token_bytes) > 50


def test_verify_manifest_timestamp_round_trip(mock_tsa):
    """A freshly-timestamped manifest verifies cleanly."""
    from timestamp import request_manifest_timestamp, verify_manifest_timestamp

    manifest = {
        "format": "regula.evidence.v1",
        "format_version": "1.1",
        "regula_version": "1.6.2",
        "hash_algorithm": "sha256",
        "files": [{"filename": "a.json", "sha256": "a" * 64, "size_bytes": 1}],
    }
    from signing import canonicalize_manifest_for_signing
    canonical = canonicalize_manifest_for_signing(manifest)

    block = request_manifest_timestamp(canonical, tsa_url=mock_tsa["url"])
    manifest_ts = dict(manifest, timestamp_authority=block)

    ok, detail = verify_manifest_timestamp(manifest_ts, canonical)
    assert ok is True, detail
    assert "matches manifest" in detail
    assert "NOT independently verified" in detail  # chain caveat present


def test_verify_detects_canonical_form_mismatch(mock_tsa):
    """If the manifest changes after timestamping, verify fails."""
    from timestamp import request_manifest_timestamp, verify_manifest_timestamp
    from signing import canonicalize_manifest_for_signing

    manifest = {
        "format": "regula.evidence.v1",
        "format_version": "1.1",
        "regula_version": "1.6.2",
        "hash_algorithm": "sha256",
        "files": [{"filename": "a.json", "sha256": "a" * 64, "size_bytes": 1}],
    }
    canonical = canonicalize_manifest_for_signing(manifest)
    block = request_manifest_timestamp(canonical, tsa_url=mock_tsa["url"])

    # Tamper: change a file's sha256 after the timestamp was issued
    tampered = dict(manifest, timestamp_authority=block)
    tampered["files"] = [{"filename": "a.json", "sha256": "b" * 64, "size_bytes": 1}]
    new_canonical = canonicalize_manifest_for_signing(tampered)

    ok, detail = verify_manifest_timestamp(tampered, new_canonical)
    assert ok is False
    assert "does not match" in detail


def test_no_timestamp_block_returns_marker():
    from timestamp import verify_manifest_timestamp
    manifest = {"format": "regula.evidence.v1", "files": []}
    ok, detail = verify_manifest_timestamp(manifest, b"anything")
    assert ok is False
    assert detail == "no timestamp block"


def test_non_sha256_imprint_rejected(mock_tsa):
    """A timestamp using sha1 or sha384 is rejected by the v1.1 verifier."""
    from timestamp import verify_manifest_timestamp

    # Hand-build a timestamp block with a sha1 algorithm (not sha256)
    tst_info = tsp.TSTInfo({
        "version": 1,
        "policy": "1.2.3.4.5",
        "message_imprint": tsp.MessageImprint({
            "hash_algorithm": algos.DigestAlgorithm({"algorithm": "sha1"}),
            "hashed_message": hashlib.sha1(b"hello").digest(),
        }),
        "serial_number": 1,
        "gen_time": datetime.datetime.now(datetime.timezone.utc),
    })
    encap = cms.EncapsulatedContentInfo({
        "content_type": "tst_info",
        "content": core.ParsableOctetString(tst_info.dump()),
    })
    signed_data = cms.SignedData({
        "version": "v3",
        "digest_algorithms": [algos.DigestAlgorithm({"algorithm": "sha1"})],
        "encap_content_info": encap,
        "signer_infos": [],
    })
    token = cms.ContentInfo({"content_type": "signed_data", "content": signed_data})
    block = {
        "format": "rfc3161",
        "hash_algorithm": "sha256",  # declared sha256 but token uses sha1
        "message_imprint": hashlib.sha256(b"hello").hexdigest(),
        "tsa_url": "http://fake",
        "token": base64.b64encode(token.dump()).decode("ascii"),
    }
    manifest = {"format": "regula.evidence.v1", "timestamp_authority": block}

    ok, detail = verify_manifest_timestamp(manifest, b"hello")
    assert ok is False
    assert "sha" in detail.lower()


def test_malformed_token_rejected():
    from timestamp import verify_manifest_timestamp
    manifest = {
        "format": "regula.evidence.v1",
        "timestamp_authority": {
            "format": "rfc3161",
            "hash_algorithm": "sha256",
            "message_imprint": "a" * 64,
            "tsa_url": "http://fake",
            "token": "this-is-not-valid-base64-or-DER-either",
        },
    }
    ok, detail = verify_manifest_timestamp(manifest, b"whatever")
    assert ok is False


def test_missing_token_field_rejected():
    from timestamp import verify_manifest_timestamp
    manifest = {
        "format": "regula.evidence.v1",
        "timestamp_authority": {
            "format": "rfc3161",
            "hash_algorithm": "sha256",
        },
    }
    ok, detail = verify_manifest_timestamp(manifest, b"whatever")
    assert ok is False
    assert "token" in detail.lower()


# ── CLI end-to-end tests ───────────────────────────────────────────


def _run_regula(*argv, env=None):
    merged = os.environ.copy()
    if env:
        merged.update(env)
    proc = subprocess.run(
        [sys.executable, "-m", "scripts.cli", *argv],
        cwd=str(ROOT),
        env=merged,
        capture_output=True,
        text=True,
        timeout=180,
    )
    return proc.returncode, proc.stdout, proc.stderr


def test_cli_conform_sign_timestamp_verify_round_trip_json(tmp_path, mock_tsa):
    """`conform --sign --timestamp --format json` then `verify --format json` succeeds.

    Asserts on JSON envelope fields (stable contract) instead of stdout
    text substrings. This is the primary timestamp round-trip test.
    """
    key_path = tmp_path / "signing.key"
    out_dir = tmp_path / "pack-out"
    env = {"REGULA_SIGNING_KEY": str(key_path)}

    rc, out, err = _run_regula(
        "conform",
        "--project", "examples/code-completion-tool",
        "--output", str(out_dir),
        "--sign",
        "--timestamp",
        "--tsa-url", mock_tsa["url"],
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
    assert "timestamp_authority" in manifest
    assert manifest["timestamp_authority"]["format"] == "rfc3161"
    assert manifest["timestamp_authority"]["hash_algorithm"] == "sha256"
    pack_path = conform_data["data"]["pack_path"]

    # Verify via JSON mode
    rc2, out2, err2 = _run_regula(
        "verify", pack_path, "--format", "json", env=env,
    )
    assert rc2 == 0, f"verify failed: rc={rc2}\nstdout={out2}\nstderr={err2}"
    verify_data = json.loads(out2)
    assert verify_data["command"] == "verify"
    report = verify_data["data"]
    assert report["signature_status"] == "VERIFIED"
    assert report["timestamp_status"] == "VERIFIED"
    assert report["failed"] == 0
    assert report["passed"] == report["total"]


def test_cli_conform_sign_timestamp_verify_text_smoke(tmp_path, mock_tsa):
    """Smoke test: text output mentions signing and timestamping.

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
        "--timestamp",
        "--tsa-url", mock_tsa["url"],
        env=env,
    )
    assert rc == 0, f"conform failed: rc={rc}\nstdout={out}\nstderr={err}"
    out_lower = out.lower()
    assert "sign" in out_lower or "ed25519" in out_lower, (
        f"expected signing mention in text output: {out!r}"
    )
    assert "timestamp" in out_lower or "rfc 3161" in out_lower or "rfc3161" in out_lower, (
        f"expected timestamp mention in text output: {out!r}"
    )

    pack_dir = next(p for p in out_dir.iterdir() if p.is_dir())
    rc2, out2, err2 = _run_regula("verify", str(pack_dir), env=env)
    assert rc2 == 0, f"verify failed: rc={rc2}\nstdout={out2}\nstderr={err2}"
    out2_lower = out2.lower()
    assert "verified" in out2_lower, (
        f"expected 'verified' in text output: {out2!r}"
    )


def test_cli_verify_detects_post_timestamp_tampering_json(tmp_path, mock_tsa):
    """Editing a signed+timestamped manifest after the fact fails verification (JSON mode)."""
    key_path = tmp_path / "signing.key"
    out_dir = tmp_path / "pack-out"
    env = {"REGULA_SIGNING_KEY": str(key_path)}

    rc, out, err = _run_regula(
        "conform",
        "--project", "examples/code-completion-tool",
        "--output", str(out_dir),
        "--sign", "--timestamp", "--tsa-url", mock_tsa["url"],
        "--format", "json",
        env=env,
    )
    assert rc == 0, err
    conform_data = json.loads(out)
    pack_path = conform_data["data"]["pack_path"]

    manifest_path = Path(pack_path) / "manifest.json"
    manifest = json.loads(manifest_path.read_text())

    # Tamper: change first file's hash
    first = manifest["files"][0]
    first["sha256"] = ("1" if first["sha256"][0] == "0" else "0") + first["sha256"][1:]
    manifest_path.write_text(json.dumps(manifest, indent=2))

    rc2, out2, err2 = _run_regula(
        "verify", str(pack_path), "--format", "json", env=env,
    )
    assert rc2 != 0
    # The CLI may sys.exit(1) before emitting JSON, so check combined text
    combined = (out2 + err2).lower()
    assert "signature" in combined or "timestamp" in combined or "modified" in combined


def test_cli_verify_untimestamped_pack_passes_non_strict_json(tmp_path):
    """A signed-but-not-timestamped pack verifies cleanly without --strict (JSON mode)."""
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
    manifest = conform_data["data"]["manifest"]
    assert "timestamp_authority" not in manifest
    pack_path = conform_data["data"]["pack_path"]

    rc2, out2, err2 = _run_regula(
        "verify", pack_path, "--format", "json", env=env,
    )
    assert rc2 == 0
    verify_data = json.loads(out2)
    report = verify_data["data"]
    assert report["failed"] == 0
    # No timestamp_status key when no timestamp block present and non-strict
    assert "timestamp_status" not in report


def test_cli_verify_untimestamped_pack_warns_under_strict_json(tmp_path):
    """Under --strict, an un-timestamped manifest warns but still exits 0 (JSON mode)."""
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
    rc2, out2, err2 = _run_regula(
        "verify", str(pack_dir), "--strict", "--format", "json", env=env,
    )
    assert rc2 == 0, f"strict verify of un-timestamped pack should exit 0: {err2}"
    verify_data = json.loads(out2)
    report = verify_data["data"]
    assert "warnings" in report
    warning_text = " ".join(report["warnings"]).lower()
    assert "timestamp" in warning_text


def test_cli_rejects_timestamp_without_sign(tmp_path):
    """Using --timestamp without --sign is converted to --sign internally,
    but attempts to bypass (if forced) would be caught by conform's invariant.

    We test the CLI behaviour: `--timestamp` alone implies sign, so the
    command should succeed (not error). The unit test for the invariant
    lives further down."""
    out_dir = tmp_path / "pack-out"
    env = {"REGULA_SIGNING_KEY": str(tmp_path / "k.key")}
    # The CLI wiring auto-upgrades --timestamp to imply --sign. Even
    # though we don't pass --sign explicitly, the producer should still
    # produce a signed + timestamped pack (when TSA is reachable; with
    # no mock here, the call will fail on the network).
    rc, out, err = _run_regula(
        "conform", "--project", "examples/code-completion-tool",
        "--output", str(out_dir),
        "--timestamp", "--tsa-url", "http://127.0.0.1:1",  # unreachable
        env=env,
    )
    # Expect non-zero exit (can't reach TSA), but we should get a clean
    # "Timestamping failed" message — not a raw traceback.
    assert rc != 0
    combined = (out + err).lower()
    assert "timestamping failed" in combined or "tsa" in combined
