# regula-ignore
"""Comprehensive unit tests for scripts/api_server.py — Regula REST API server.

Tests cover:
  - JSON envelope construction (_build_envelope, _json_bytes)
  - Request handler routing (do_GET, do_POST, do_OPTIONS)
  - Response formatting (_send_json, _send_error)
  - JSON body parsing and validation (_read_json_body)
  - Each endpoint handler's logic and error paths
  - CORS header handling
  - Configuration / argument parsing (main)
  - Security: path traversal rejection, request size limits
"""

import io
import json
import sys
import tempfile
import os
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

# Bare import convention — scripts dir on path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from api_server import (
    _build_envelope,
    _json_bytes,
    MAX_REQUEST_SIZE,
    RegulaHandler,
)
from constants import VERSION


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_handler(method="GET", path="/", body=None, headers=None):
    """Build a RegulaHandler with mocked socket/request/response streams.

    Returns (handler, response_buffer) where response_buffer is a BytesIO
    that captures everything the handler writes.
    """
    if headers is None:
        headers = {}

    # Build the raw request line + headers
    request_line = f"{method} {path} HTTP/1.1\r\n"
    header_lines = "".join(f"{k}: {v}\r\n" for k, v in headers.items())
    raw_request = (request_line + header_lines + "\r\n").encode("utf-8")

    if body is not None:
        if isinstance(body, str):
            body = body.encode("utf-8")
        raw_request += body

    rfile = io.BytesIO(raw_request)
    wfile = io.BytesIO()

    # Mock the socket so BaseHTTPRequestHandler.__init__ doesn't blow up
    mock_socket = MagicMock()
    mock_socket.makefile.return_value = rfile

    # Create the handler without calling __init__ (which tries to handle
    # a request immediately) — instead we set up internals manually.
    handler = RegulaHandler.__new__(RegulaHandler)
    handler.rfile = rfile
    handler.wfile = wfile
    handler.client_address = ("127.0.0.1", 12345)
    handler.server = MagicMock()
    handler.requestline = request_line.strip()
    handler.command = method
    handler.path = path
    handler.request_version = "HTTP/1.1"
    handler.close_connection = True

    # Parse headers using http.client
    import http.client
    rfile_for_headers = io.BytesIO(header_lines.encode("utf-8") + b"\r\n")
    handler.headers = http.client.parse_headers(rfile_for_headers)

    # Re-position rfile to the body portion for reading
    if body is not None:
        handler.rfile = io.BytesIO(body if isinstance(body, bytes) else body.encode("utf-8"))
    else:
        handler.rfile = io.BytesIO(b"")

    # Capture response
    handler._headers_buffer = []

    return handler, wfile


def _parse_response(wfile):
    """Parse the status code and JSON body from a handler's wfile output."""
    raw = wfile.getvalue()
    if not raw:
        return None, None
    text = raw.decode("utf-8", errors="replace")

    # Find JSON in the response body (after the double CRLF)
    parts = text.split("\r\n\r\n", 1)
    body_text = parts[1] if len(parts) > 1 else ""

    # Extract status code from the first line
    first_line = text.split("\r\n")[0] if text else ""
    status = None
    if "HTTP/" in first_line:
        try:
            status = int(first_line.split(" ")[1])
        except (IndexError, ValueError):
            pass

    body = None
    if body_text.strip():
        try:
            body = json.loads(body_text)
        except json.JSONDecodeError:
            body = body_text  # Return raw text (e.g. HTML)

    return status, body


def _dispatch_request(method, path, body=None, headers=None, json_body=None):
    """Create a handler, dispatch the request, and return (status, body).

    If json_body is given, it is serialised and Content-Type/Content-Length
    headers are set automatically.
    """
    if headers is None:
        headers = {}

    raw_body = None
    if json_body is not None:
        raw_body = json.dumps(json_body).encode("utf-8")
        headers.setdefault("Content-Type", "application/json")
        headers["Content-Length"] = str(len(raw_body))

    elif body is not None:
        raw_body = body if isinstance(body, bytes) else body.encode("utf-8")

    handler, wfile = _make_handler(method, path, raw_body, headers)

    if method == "GET":
        handler.do_GET()
    elif method == "POST":
        handler.do_POST()
    elif method == "OPTIONS":
        handler.do_OPTIONS()

    return _parse_response(wfile)


# ===================================================================
#  1. JSON Envelope (_build_envelope, _json_bytes)
# ===================================================================

def test_build_envelope_structure():
    """_build_envelope returns all required envelope fields."""
    env = _build_envelope("test-command", {"key": "value"})
    assert env["format_version"] == "1.0"
    assert env["regula_version"] == VERSION
    assert env["command"] == "test-command"
    assert env["exit_code"] == 0
    assert env["data"] == {"key": "value"}
    assert "timestamp" in env


def test_build_envelope_timestamp_format():
    """Timestamp ends with Z and is a valid ISO-8601 UTC string."""
    env = _build_envelope("ts-test", {})
    ts = env["timestamp"]
    assert ts.endswith("Z"), f"Timestamp should end with Z, got {ts!r}"
    assert "+00:00" not in ts, "Timestamp should use Z, not +00:00"
    # Verify it parses without error
    parsed = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    assert parsed.tzinfo is not None


def test_build_envelope_custom_exit_code():
    """_build_envelope respects a non-zero exit_code."""
    env = _build_envelope("fail", {}, exit_code=1)
    assert env["exit_code"] == 1


def test_build_envelope_data_types():
    """_build_envelope handles various data types: list, None, nested dict."""
    for data in [[], None, {"nested": {"deep": True}}, [1, 2, 3]]:
        env = _build_envelope("type-test", data)
        assert env["data"] == data


def test_json_bytes_returns_utf8():
    """_json_bytes returns bytes encoded as UTF-8 JSON."""
    result = _json_bytes({"hello": "world"})
    assert isinstance(result, bytes)
    parsed = json.loads(result.decode("utf-8"))
    assert parsed["hello"] == "world"


def test_json_bytes_sorted_keys():
    """_json_bytes sorts keys for deterministic output."""
    result = _json_bytes({"z": 1, "a": 2, "m": 3})
    text = result.decode("utf-8")
    a_pos = text.index('"a"')
    m_pos = text.index('"m"')
    z_pos = text.index('"z"')
    assert a_pos < m_pos < z_pos


def test_json_bytes_handles_non_serialisable():
    """_json_bytes uses default=str for types like datetime."""
    now = datetime.now(timezone.utc)
    result = _json_bytes({"ts": now})
    parsed = json.loads(result.decode("utf-8"))
    assert isinstance(parsed["ts"], str)


# ===================================================================
#  2. CORS and OPTIONS
# ===================================================================

def test_options_returns_200():
    """OPTIONS request returns 200 for CORS preflight."""
    status, _ = _dispatch_request("OPTIONS", "/v1/check")
    assert status == 200


def test_no_cors_headers_by_default():
    """No CORS headers by default — the server has no auth, so a wildcard
    ACAO would let any website read local scan results via fetch() to
    localhost (drive-by CSRF-via-CORS)."""
    import os
    os.environ.pop("REGULA_API_ALLOW_ORIGIN", None)
    handler, wfile = _make_handler("GET", "/health")
    handler.do_GET()
    raw = wfile.getvalue().decode("utf-8")
    assert "Access-Control-Allow-Origin" not in raw


def test_cors_headers_opt_in_via_env():
    """Setting REGULA_API_ALLOW_ORIGIN to an explicit origin enables CORS
    for that origin only; a literal * is refused."""
    import os
    os.environ["REGULA_API_ALLOW_ORIGIN"] = "http://localhost:3000"
    try:
        handler, wfile = _make_handler("GET", "/health")
        handler.do_GET()
        raw = wfile.getvalue().decode("utf-8")
        assert "Access-Control-Allow-Origin: http://localhost:3000" in raw
        assert "Access-Control-Allow-Methods" in raw
        assert "Access-Control-Allow-Headers" in raw
    finally:
        os.environ.pop("REGULA_API_ALLOW_ORIGIN", None)

    os.environ["REGULA_API_ALLOW_ORIGIN"] = "*"
    try:
        handler, wfile = _make_handler("GET", "/health")
        handler.do_GET()
        raw = wfile.getvalue().decode("utf-8")
        assert "Access-Control-Allow-Origin" not in raw
    finally:
        os.environ.pop("REGULA_API_ALLOW_ORIGIN", None)


# ===================================================================
#  3. GET Routing
# ===================================================================

def test_get_health():
    """GET /health returns status ok and version."""
    status, body = _dispatch_request("GET", "/health")
    assert status == 200
    assert body["status"] == "ok"
    assert body["version"] == VERSION


def test_get_health_trailing_slash():
    """GET /health/ (trailing slash) still routes correctly."""
    status, body = _dispatch_request("GET", "/health/")
    assert status == 200
    assert body["status"] == "ok"


def test_get_unknown_route():
    """GET on an unknown path returns 404."""
    status, body = _dispatch_request("GET", "/nonexistent")
    assert status == 404
    assert "error" in body
    assert "Not found" in body["error"]


def test_get_v1_dashboard_fallback_json():
    """GET /v1/dashboard returns JSON fallback when no index.html exists."""
    with patch("pathlib.Path.is_file", return_value=False):
        status, body = _dispatch_request("GET", "/v1/dashboard")
    assert status == 200
    assert body["data"]["status"] == "ok"
    assert body["data"]["version"] == VERSION
    assert "No dashboard files found" in body["data"]["message"]
    assert body["command"] == "dashboard"


def test_get_v1_dashboard_serves_html():
    """GET /v1/dashboard serves index.html when it exists."""
    sample_html = "<html><body>Dashboard</body></html>"
    with patch("pathlib.Path.is_file", return_value=True), \
         patch("pathlib.Path.read_text", return_value=sample_html):
        handler, wfile = _make_handler("GET", "/v1/dashboard")
        handler.do_GET()
    raw = wfile.getvalue().decode("utf-8")
    assert "200" in raw.split("\r\n")[0]
    assert "text/html" in raw
    assert "Dashboard" in raw


def test_get_v1_dashboard_read_error():
    """GET /v1/dashboard returns 500 when reading HTML fails."""
    with patch("pathlib.Path.is_file", return_value=True), \
         patch("pathlib.Path.read_text", side_effect=OSError("disk error")):
        status, body = _dispatch_request("GET", "/v1/dashboard")
    assert status == 500
    assert "error" in body


def test_get_questionnaire():
    """GET /v1/questionnaire returns the questionnaire envelope."""
    mock_questionnaire = {
        "type": "risk_assessment_questionnaire",
        "version": "1.0",
        "questions": [{"id": "q1", "text": "Is this AI?"}],
    }
    with patch("api_server.generate_questionnaire", return_value=mock_questionnaire, create=True) as mock_gen:
        # Need to patch at import time within the handler
        with patch.dict("sys.modules", {}):
            # Patch the import inside the handler
            import types
            mock_module = types.ModuleType("questionnaire")
            mock_module.generate_questionnaire = lambda: mock_questionnaire
            with patch.dict("sys.modules", {"questionnaire": mock_module}):
                status, body = _dispatch_request("GET", "/v1/questionnaire")
    assert status == 200
    assert body["command"] == "questionnaire"
    assert body["data"]["type"] == "risk_assessment_questionnaire"


def test_get_questionnaire_import_error():
    """GET /v1/questionnaire returns 500 on import/generation failure."""
    import types
    mock_module = types.ModuleType("questionnaire")
    mock_module.generate_questionnaire = MagicMock(side_effect=RuntimeError("broken"))
    with patch.dict("sys.modules", {"questionnaire": mock_module}):
        status, body = _dispatch_request("GET", "/v1/questionnaire")
    assert status == 500
    assert "error" in body


# ===================================================================
#  4. POST Routing
# ===================================================================

def test_post_unknown_route():
    """POST on an unknown path returns 404."""
    status, body = _dispatch_request("POST", "/v1/nonexistent",
                                     json_body={"input": "test"})
    assert status == 404
    assert "Not found" in body["error"]


# ===================================================================
#  5. _read_json_body validation
# ===================================================================

def test_read_json_body_wrong_content_type():
    """POST with non-JSON Content-Type returns 400."""
    status, body = _dispatch_request(
        "POST", "/v1/classify",
        body="not json",
        headers={"Content-Type": "text/plain", "Content-Length": "8"},
    )
    assert status == 400
    assert "Content-Type" in body["error"]


def test_read_json_body_invalid_content_length():
    """POST with non-numeric Content-Length returns 400."""
    status, body = _dispatch_request(
        "POST", "/v1/classify",
        body="{}",
        headers={"Content-Type": "application/json", "Content-Length": "abc"},
    )
    assert status == 400
    assert "Content-Length" in body["error"]


def test_read_json_body_negative_content_length():
    """POST with negative Content-Length returns 400."""
    status, body = _dispatch_request(
        "POST", "/v1/classify",
        body="{}",
        headers={"Content-Type": "application/json", "Content-Length": "-1"},
    )
    assert status == 400
    assert "Content-Length" in body["error"]


def test_read_json_body_too_large():
    """POST with body exceeding MAX_REQUEST_SIZE returns 400."""
    fake_length = str(MAX_REQUEST_SIZE + 1)
    status, body = _dispatch_request(
        "POST", "/v1/classify",
        body="{}",
        headers={"Content-Type": "application/json", "Content-Length": fake_length},
    )
    assert status == 400
    assert "too large" in body["error"]


def test_read_json_body_empty_body():
    """POST with Content-Length=0 returns 400 for empty body."""
    status, body = _dispatch_request(
        "POST", "/v1/classify",
        body=b"",
        headers={"Content-Type": "application/json", "Content-Length": "0"},
    )
    # Content-Length 0 means length is 0, rfile.read(0) returns b"" which is empty
    assert status == 400


def test_read_json_body_invalid_json():
    """POST with malformed JSON returns 400."""
    bad_json = b"{not valid json}"
    status, body = _dispatch_request(
        "POST", "/v1/classify",
        body=bad_json,
        headers={"Content-Type": "application/json", "Content-Length": str(len(bad_json))},
    )
    assert status == 400


# ===================================================================
#  6. POST /v1/classify
# ===================================================================

def test_classify_missing_input():
    """POST /v1/classify without 'input' field returns 400."""
    status, body = _dispatch_request("POST", "/v1/classify", json_body={})
    assert status == 400
    assert "input" in body["error"]


def test_classify_input_not_string():
    """POST /v1/classify with non-string 'input' returns 400."""
    status, body = _dispatch_request("POST", "/v1/classify",
                                     json_body={"input": 12345})
    assert status == 400
    assert "string" in body["error"]


def test_classify_input_too_large():
    """POST /v1/classify with input >1MB returns 400."""
    # Build a string just over 1MB
    big_input = "x" * (1_048_576 + 1)
    status, body = _dispatch_request("POST", "/v1/classify",
                                     json_body={"input": big_input})
    assert status == 400
    assert "too large" in body["error"]


def test_classify_success():
    """POST /v1/classify returns envelope with classification data."""
    import types

    # Create a mock Classification result
    mock_result = MagicMock()
    mock_result.to_dict.return_value = {
        "tier": "minimal_risk",
        "confidence": "medium",
        "action": "allow",
    }

    mock_module = types.ModuleType("classify_risk")
    mock_module.classify = MagicMock(return_value=mock_result)

    with patch.dict("sys.modules", {"classify_risk": mock_module}):
        status, body = _dispatch_request(
            "POST", "/v1/classify",
            json_body={"input": "import tensorflow as tf"},
        )
    assert status == 200
    assert body["command"] == "classify"
    assert body["data"]["tier"] == "minimal_risk"
    assert body["format_version"] == "1.0"
    assert body["regula_version"] == VERSION


def test_classify_internal_error():
    """POST /v1/classify returns 500 when classify() raises."""
    import types
    mock_module = types.ModuleType("classify_risk")
    mock_module.classify = MagicMock(side_effect=RuntimeError("boom"))
    with patch.dict("sys.modules", {"classify_risk": mock_module}):
        status, body = _dispatch_request(
            "POST", "/v1/classify",
            json_body={"input": "some code"},
        )
    assert status == 500
    assert "Classification failed" in body["error"]


# ===================================================================
#  7. POST /v1/check
# ===================================================================

def test_check_missing_path():
    """POST /v1/check without 'path' field returns 400."""
    status, body = _dispatch_request("POST", "/v1/check", json_body={})
    assert status == 400
    assert "path" in body["error"]


def test_check_nonexistent_path():
    """POST /v1/check with non-existent path returns 400."""
    status, body = _dispatch_request("POST", "/v1/check",
                                     json_body={"path": "/nonexistent/path/xyz"})
    assert status == 400
    assert "does not exist" in body["error"]


def test_check_path_outside_cwd():
    """POST /v1/check with path outside cwd returns 403."""
    # /tmp is almost certainly outside the cwd
    with tempfile.TemporaryDirectory() as tmpdir:
        # Ensure cwd is not a parent of tmpdir by using a different cwd
        with patch("pathlib.Path.cwd", return_value=Path("/some/other/dir")):
            with patch("pathlib.Path.exists", return_value=True), \
                 patch("pathlib.Path.is_dir", return_value=True), \
                 patch("pathlib.Path.is_file", return_value=False):
                status, body = _dispatch_request(
                    "POST", "/v1/check",
                    json_body={"path": tmpdir},
                )
    assert status == 403
    assert "working directory" in body["error"]


def test_check_invalid_min_tier():
    """POST /v1/check with invalid min_tier returns 400."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Make the path "within" cwd by patching cwd
        target = Path(tmpdir).resolve()
        with patch("pathlib.Path.cwd", return_value=target.parent):
            status, body = _dispatch_request(
                "POST", "/v1/check",
                json_body={"path": tmpdir, "min_tier": "invalid_tier"},
            )
    assert status == 400
    assert "min_tier" in body["error"]


def test_check_valid_min_tiers():
    """POST /v1/check accepts all valid min_tier values."""
    import types

    mock_module = types.ModuleType("report")
    mock_module.scan_files = MagicMock(return_value=[])

    valid_tiers = ["", "prohibited", "high_risk", "limited_risk", "minimal_risk"]
    for tier in valid_tiers:
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir).resolve()
            with patch("pathlib.Path.cwd", return_value=target.parent), \
                 patch.dict("sys.modules", {"report": mock_module}):
                status, body = _dispatch_request(
                    "POST", "/v1/check",
                    json_body={"path": tmpdir, "min_tier": tier},
                )
        assert status == 200, f"min_tier={tier!r} should be accepted, got {status}"


def test_check_success():
    """POST /v1/check returns sorted findings in an envelope."""
    import types

    mock_findings = [
        {"file": "b.py", "line": 10, "pattern": "facial_recognition"},
        {"file": "a.py", "line": 5, "pattern": "biometric"},
        {"file": "a.py", "line": 3, "pattern": "training_data"},
    ]

    mock_module = types.ModuleType("report")
    mock_module.scan_files = MagicMock(return_value=list(mock_findings))

    with tempfile.TemporaryDirectory() as tmpdir:
        target = Path(tmpdir).resolve()
        with patch("pathlib.Path.cwd", return_value=target.parent), \
             patch.dict("sys.modules", {"report": mock_module}):
            status, body = _dispatch_request(
                "POST", "/v1/check",
                json_body={"path": tmpdir},
            )

    assert status == 200
    assert body["command"] == "check"
    # Findings should be sorted by file, then line, then pattern
    data = body["data"]
    assert len(data) == 3
    assert data[0]["file"] == "a.py"
    assert data[0]["line"] == 3


def test_check_skip_tests_flag():
    """POST /v1/check passes skip_tests to scan_files."""
    import types

    mock_module = types.ModuleType("report")
    mock_module.scan_files = MagicMock(return_value=[])

    with tempfile.TemporaryDirectory() as tmpdir:
        target = Path(tmpdir).resolve()
        with patch("pathlib.Path.cwd", return_value=target.parent), \
             patch.dict("sys.modules", {"report": mock_module}):
            _dispatch_request(
                "POST", "/v1/check",
                json_body={"path": tmpdir, "skip_tests": True},
            )

    call_kwargs = mock_module.scan_files.call_args
    assert call_kwargs[1]["skip_tests"] is True


def test_check_scan_error():
    """POST /v1/check returns 500 when scan_files raises."""
    import types

    mock_module = types.ModuleType("report")
    mock_module.scan_files = MagicMock(side_effect=RuntimeError("scan broke"))

    with tempfile.TemporaryDirectory() as tmpdir:
        target = Path(tmpdir).resolve()
        with patch("pathlib.Path.cwd", return_value=target.parent), \
             patch.dict("sys.modules", {"report": mock_module}):
            status, body = _dispatch_request(
                "POST", "/v1/check",
                json_body={"path": tmpdir},
            )
    assert status == 500
    assert "Scan failed" in body["error"]


# ===================================================================
#  8. POST /v1/gap
# ===================================================================

def test_gap_missing_path():
    """POST /v1/gap without 'path' field returns 400."""
    status, body = _dispatch_request("POST", "/v1/gap", json_body={})
    assert status == 400
    assert "path" in body["error"]


def test_gap_path_not_directory():
    """POST /v1/gap with a file (not dir) returns 400."""
    with tempfile.NamedTemporaryFile(suffix=".py") as f:
        status, body = _dispatch_request("POST", "/v1/gap",
                                         json_body={"path": f.name})
    assert status == 400
    assert "not a directory" in body["error"]


def test_gap_path_outside_cwd():
    """POST /v1/gap with path outside cwd returns 403."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch("pathlib.Path.cwd", return_value=Path("/some/unrelated/dir")):
            status, body = _dispatch_request(
                "POST", "/v1/gap",
                json_body={"path": tmpdir},
            )
    assert status == 403
    assert "working directory" in body["error"]


def test_gap_articles_not_list():
    """POST /v1/gap with non-list articles returns 400."""
    with tempfile.TemporaryDirectory() as tmpdir:
        target = Path(tmpdir).resolve()
        with patch("pathlib.Path.cwd", return_value=target.parent):
            status, body = _dispatch_request(
                "POST", "/v1/gap",
                json_body={"path": tmpdir, "articles": "not-a-list"},
            )
    assert status == 400
    assert "list" in body["error"]


def test_gap_articles_invalid_types():
    """POST /v1/gap with articles containing non-str/int returns 400."""
    with tempfile.TemporaryDirectory() as tmpdir:
        target = Path(tmpdir).resolve()
        with patch("pathlib.Path.cwd", return_value=target.parent):
            status, body = _dispatch_request(
                "POST", "/v1/gap",
                json_body={"path": tmpdir, "articles": [1, "6", [7]]},
            )
    assert status == 400
    assert "string or integer" in body["error"]


def test_gap_success():
    """POST /v1/gap returns envelope with assessment data."""
    import types

    mock_assessment = {"status": "compliant", "gaps": []}
    mock_module = types.ModuleType("compliance_check")
    mock_module.assess_compliance = MagicMock(return_value=mock_assessment)

    with tempfile.TemporaryDirectory() as tmpdir:
        target = Path(tmpdir).resolve()
        with patch("pathlib.Path.cwd", return_value=target.parent), \
             patch.dict("sys.modules", {"compliance_check": mock_module}):
            status, body = _dispatch_request(
                "POST", "/v1/gap",
                json_body={"path": tmpdir, "articles": [9, "10"]},
            )
    assert status == 200
    assert body["command"] == "gap"
    assert body["data"]["status"] == "compliant"

    # Verify articles were passed through
    call_kwargs = mock_module.assess_compliance.call_args
    assert call_kwargs[1]["articles"] == [9, "10"]


def test_gap_articles_none_omitted():
    """POST /v1/gap without articles field passes None to assess_compliance."""
    import types

    mock_module = types.ModuleType("compliance_check")
    mock_module.assess_compliance = MagicMock(return_value={})

    with tempfile.TemporaryDirectory() as tmpdir:
        target = Path(tmpdir).resolve()
        with patch("pathlib.Path.cwd", return_value=target.parent), \
             patch.dict("sys.modules", {"compliance_check": mock_module}):
            _dispatch_request(
                "POST", "/v1/gap",
                json_body={"path": tmpdir},
            )
    call_kwargs = mock_module.assess_compliance.call_args
    assert call_kwargs[1]["articles"] is None


def test_gap_internal_error():
    """POST /v1/gap returns 500 when assess_compliance raises."""
    import types

    mock_module = types.ModuleType("compliance_check")
    mock_module.assess_compliance = MagicMock(side_effect=RuntimeError("fail"))

    with tempfile.TemporaryDirectory() as tmpdir:
        target = Path(tmpdir).resolve()
        with patch("pathlib.Path.cwd", return_value=target.parent), \
             patch.dict("sys.modules", {"compliance_check": mock_module}):
            status, body = _dispatch_request(
                "POST", "/v1/gap",
                json_body={"path": tmpdir},
            )
    assert status == 500
    assert "Gap analysis failed" in body["error"]


# ===================================================================
#  9. POST /v1/questionnaire/evaluate
# ===================================================================

def test_questionnaire_evaluate_missing_answers():
    """POST /v1/questionnaire/evaluate without answers returns 400."""
    status, body = _dispatch_request("POST", "/v1/questionnaire/evaluate",
                                     json_body={})
    assert status == 400
    assert "answers" in body["error"]


def test_questionnaire_evaluate_answers_not_dict():
    """POST /v1/questionnaire/evaluate with non-dict answers returns 400."""
    status, body = _dispatch_request("POST", "/v1/questionnaire/evaluate",
                                     json_body={"answers": ["yes", "no"]})
    assert status == 400
    assert "answers" in body["error"]


def test_questionnaire_evaluate_invalid_answer_value():
    """POST /v1/questionnaire/evaluate with bad answer value returns 400."""
    status, body = _dispatch_request(
        "POST", "/v1/questionnaire/evaluate",
        json_body={"answers": {"q1": "maybe"}},
    )
    assert status == 400
    assert "maybe" in body["error"]
    assert "yes/no/unsure" in body["error"]


def test_questionnaire_evaluate_valid_answers():
    """All three valid answer values (yes, no, unsure) are accepted."""
    import types

    mock_result = MagicMock()
    mock_result.to_dict.return_value = {
        "tier": "minimal_risk",
        "confidence": "medium",
    }

    mock_module = types.ModuleType("questionnaire")
    mock_module.evaluate_questionnaire = MagicMock(return_value=mock_result)

    with patch.dict("sys.modules", {"questionnaire": mock_module}):
        status, body = _dispatch_request(
            "POST", "/v1/questionnaire/evaluate",
            json_body={"answers": {"q1": "yes", "q2": "no", "q3": "unsure"}},
        )
    assert status == 200
    assert body["command"] == "questionnaire/evaluate"
    assert body["data"]["tier"] == "minimal_risk"


def test_questionnaire_evaluate_internal_error():
    """POST /v1/questionnaire/evaluate returns 500 on failure."""
    import types

    mock_module = types.ModuleType("questionnaire")
    mock_module.evaluate_questionnaire = MagicMock(side_effect=RuntimeError("fail"))

    with patch.dict("sys.modules", {"questionnaire": mock_module}):
        status, body = _dispatch_request(
            "POST", "/v1/questionnaire/evaluate",
            json_body={"answers": {"q1": "yes"}},
        )
    assert status == 500
    assert "Questionnaire evaluation failed" in body["error"]


# ===================================================================
# 10. _send_error / _send_json
# ===================================================================

def test_send_error_format():
    """_send_error produces a JSON body with error and status fields."""
    handler, wfile = _make_handler("GET", "/bad")
    handler._send_error(422, "Validation failed")
    status, body = _parse_response(wfile)
    assert status == 422
    assert body["error"] == "Validation failed"
    assert body["status"] == 422


def test_send_json_content_type():
    """_send_json sets Content-Type to application/json."""
    handler, wfile = _make_handler("GET", "/test")
    handler._send_json(200, {"ok": True})
    raw = wfile.getvalue().decode("utf-8")
    assert "application/json; charset=utf-8" in raw


def test_send_json_content_length():
    """_send_json sets Content-Length matching the actual payload."""
    handler, wfile = _make_handler("GET", "/test")
    payload = {"data": "hello"}
    handler._send_json(200, payload)
    raw = wfile.getvalue().decode("utf-8")
    # Extract Content-Length header
    for line in raw.split("\r\n"):
        if line.startswith("Content-Length:"):
            cl = int(line.split(":")[1].strip())
            # The actual body after headers
            body_bytes = wfile.getvalue().split(b"\r\n\r\n", 1)[1]
            assert cl == len(body_bytes)
            break
    else:
        raise AssertionError("Content-Length header not found")


# ===================================================================
# 11. Log message formatting
# ===================================================================

def test_log_message_format():
    """log_message writes timestamped output to stderr."""
    handler, _ = _make_handler("GET", "/")
    stderr_buf = io.StringIO()
    with patch("sys.stderr", stderr_buf):
        handler.log_message("test %s %d", "hello", 42)
    output = stderr_buf.getvalue()
    assert "test hello 42" in output
    # Should contain ISO timestamp
    assert "T" in output
    assert "Z" in output


# ===================================================================
# 12. main() argument parsing
# ===================================================================

def test_main_default_args():
    """main() uses default host=localhost and port=8487."""
    with patch("argparse.ArgumentParser.parse_args") as mock_parse, \
         patch("api_server.HTTPServer") as mock_server_cls, \
         patch("sys.stderr", io.StringIO()):

        mock_args = MagicMock()
        mock_args.host = "localhost"
        mock_args.port = 8487
        mock_parse.return_value = mock_args

        mock_server = MagicMock()
        mock_server.serve_forever.side_effect = KeyboardInterrupt()
        mock_server_cls.return_value = mock_server

        from api_server import main
        main()

        mock_server_cls.assert_called_once_with(("localhost", 8487), RegulaHandler)
        mock_server.serve_forever.assert_called_once()
        mock_server.server_close.assert_called_once()


def test_main_custom_args():
    """main() respects custom --host and --port."""
    with patch("argparse.ArgumentParser.parse_args") as mock_parse, \
         patch("api_server.HTTPServer") as mock_server_cls, \
         patch("sys.stderr", io.StringIO()):

        mock_args = MagicMock()
        mock_args.host = "0.0.0.0"
        mock_args.port = 9999
        mock_parse.return_value = mock_args

        mock_server = MagicMock()
        mock_server.serve_forever.side_effect = KeyboardInterrupt()
        mock_server_cls.return_value = mock_server

        from api_server import main
        main()

        mock_server_cls.assert_called_once_with(("0.0.0.0", 9999), RegulaHandler)


def test_main_startup_banner():
    """main() prints a startup banner with version and endpoints."""
    stderr_buf = io.StringIO()
    with patch("argparse.ArgumentParser.parse_args") as mock_parse, \
         patch("api_server.HTTPServer") as mock_server_cls, \
         patch("sys.stderr", stderr_buf):

        mock_args = MagicMock()
        mock_args.host = "localhost"
        mock_args.port = 8487
        mock_parse.return_value = mock_args

        mock_server = MagicMock()
        mock_server.serve_forever.side_effect = KeyboardInterrupt()
        mock_server_cls.return_value = mock_server

        from api_server import main
        main()

    banner = stderr_buf.getvalue()
    assert VERSION in banner
    assert "/health" in banner
    assert "/v1/check" in banner
    assert "/v1/classify" in banner
    assert "/v1/gap" in banner
    assert "/v1/questionnaire" in banner
    assert "/v1/dashboard" in banner
    assert "No authentication" in banner


# ===================================================================
# 13. MAX_REQUEST_SIZE constant
# ===================================================================

def test_max_request_size_is_10mb():
    """MAX_REQUEST_SIZE is 10 MB."""
    assert MAX_REQUEST_SIZE == 10 * 1024 * 1024


# ===================================================================
# 14. Edge cases and security
# ===================================================================

def test_check_path_traversal_blocked():
    """Path traversal attempts outside cwd are blocked.

    The handler checks target.relative_to(cwd) and returns 403 when the
    resolved path is outside the working directory. We use a real temp dir
    and patch only cwd to simulate the traversal scenario.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # The target path exists, but cwd points elsewhere
        with patch("pathlib.Path.cwd", return_value=Path("/some/completely/different/dir")):
            status, body = _dispatch_request(
                "POST", "/v1/check",
                json_body={"path": tmpdir},
            )
    assert status == 403
    assert "working directory" in body["error"]


def test_classify_empty_string_input():
    """POST /v1/classify with empty string 'input' returns 400."""
    status, body = _dispatch_request("POST", "/v1/classify",
                                     json_body={"input": ""})
    assert status == 400
    assert "input" in body["error"]


def test_questionnaire_evaluate_empty_answers_dict():
    """POST /v1/questionnaire/evaluate with empty dict answers returns 400."""
    status, body = _dispatch_request("POST", "/v1/questionnaire/evaluate",
                                     json_body={"answers": {}})
    assert status == 400
    assert "answers" in body["error"]


def test_check_path_is_file():
    """POST /v1/check accepts a file path (not just directory)."""
    import types

    mock_module = types.ModuleType("report")
    mock_module.scan_files = MagicMock(return_value=[])

    with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as f:
        f.write(b"import torch\n")
        tmpfile = f.name

    try:
        target = Path(tmpfile).resolve()
        with patch("pathlib.Path.cwd", return_value=target.parent), \
             patch.dict("sys.modules", {"report": mock_module}):
            status, body = _dispatch_request(
                "POST", "/v1/check",
                json_body={"path": tmpfile},
            )
        assert status == 200
    finally:
        os.unlink(tmpfile)


def test_get_root_returns_404():
    """GET / returns 404 — there is no root handler."""
    status, body = _dispatch_request("GET", "/")
    assert status == 404


def test_post_to_get_only_endpoint():
    """POST to a GET-only endpoint returns 404."""
    status, body = _dispatch_request("POST", "/health",
                                     json_body={"data": "test"})
    assert status == 404


def test_get_to_post_only_endpoint():
    """GET to a POST-only endpoint returns 404."""
    status, body = _dispatch_request("GET", "/v1/check")
    assert status == 404


def test_multiple_trailing_slashes():
    """Paths with multiple trailing slashes are normalised."""
    status, body = _dispatch_request("GET", "/health///")
    # rstrip("/") on "/health///" gives "/health" — should route correctly
    assert status == 200
    assert body["status"] == "ok"


def test_check_findings_sorted_deterministically():
    """Findings from /v1/check are sorted by (file, line, pattern)."""
    import types

    # Create findings in deliberately unsorted order
    mock_findings = [
        {"file": "c.py", "line": 1, "pattern": "z_pattern"},
        {"file": "a.py", "line": 5, "pattern": "b_pattern"},
        {"file": "a.py", "line": 5, "pattern": "a_pattern"},
        {"file": "a.py", "line": 1, "pattern": "x_pattern"},
        {"file": "b.py", "line": 3, "pattern": "y_pattern"},
    ]

    mock_module = types.ModuleType("report")
    mock_module.scan_files = MagicMock(return_value=list(mock_findings))

    with tempfile.TemporaryDirectory() as tmpdir:
        target = Path(tmpdir).resolve()
        with patch("pathlib.Path.cwd", return_value=target.parent), \
             patch.dict("sys.modules", {"report": mock_module}):
            status, body = _dispatch_request(
                "POST", "/v1/check",
                json_body={"path": tmpdir},
            )

    assert status == 200
    data = body["data"]
    assert len(data) == 5
    # Should be sorted: a.py:1:x, a.py:5:a, a.py:5:b, b.py:3:y, c.py:1:z
    assert data[0] == {"file": "a.py", "line": 1, "pattern": "x_pattern"}
    assert data[1] == {"file": "a.py", "line": 5, "pattern": "a_pattern"}
    assert data[2] == {"file": "a.py", "line": 5, "pattern": "b_pattern"}
    assert data[3] == {"file": "b.py", "line": 3, "pattern": "y_pattern"}
    assert data[4] == {"file": "c.py", "line": 1, "pattern": "z_pattern"}


def test_gap_valid_articles_str_and_int():
    """POST /v1/gap accepts articles as a mix of str and int."""
    import types

    mock_module = types.ModuleType("compliance_check")
    mock_module.assess_compliance = MagicMock(return_value={"gaps": []})

    with tempfile.TemporaryDirectory() as tmpdir:
        target = Path(tmpdir).resolve()
        with patch("pathlib.Path.cwd", return_value=target.parent), \
             patch.dict("sys.modules", {"compliance_check": mock_module}):
            status, body = _dispatch_request(
                "POST", "/v1/gap",
                json_body={"path": tmpdir, "articles": [6, "9", 10, "15"]},
            )
    assert status == 200


def test_envelope_fields_present_in_all_success_responses():
    """All success responses contain the full envelope: format_version, regula_version, command, timestamp, exit_code, data."""
    required_keys = {"format_version", "regula_version", "command", "timestamp", "exit_code", "data"}

    # Test /health
    _, health_body = _dispatch_request("GET", "/health")
    # /health returns a simple dict, not an envelope — that's by design
    assert "status" in health_body

    # Test /v1/classify with mock
    import types
    mock_result = MagicMock()
    mock_result.to_dict.return_value = {"tier": "minimal_risk"}
    mock_module = types.ModuleType("classify_risk")
    mock_module.classify = MagicMock(return_value=mock_result)

    with patch.dict("sys.modules", {"classify_risk": mock_module}):
        _, classify_body = _dispatch_request(
            "POST", "/v1/classify",
            json_body={"input": "test code"},
        )
    assert required_keys.issubset(classify_body.keys()), \
        f"Missing keys: {required_keys - classify_body.keys()}"
