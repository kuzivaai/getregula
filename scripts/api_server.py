#!/usr/bin/env python3
"""
Regula REST API Server

Exposes Regula's check, classify, gap analysis, and questionnaire
functionality over HTTP using Python's stdlib http.server.

SECURITY: This server has no authentication. Do NOT expose over public
networks without adding auth (e.g. reverse proxy with API key validation).

Endpoints:
    GET  /health                     Health check
    POST /v1/check                   Scan files for risk indicators
    POST /v1/classify                Classify text against EU AI Act tiers
    POST /v1/gap                     Compliance gap analysis
    GET  /v1/questionnaire           Governance self-assessment questionnaire
    POST /v1/questionnaire/evaluate  Evaluate questionnaire answers
    GET  /v1/dashboard               Static dashboard (or JSON status)

Usage:
    python3 -m scripts.api_server --port 8487 --host localhost
    python3 scripts/api_server.py --port 8487 --host 0.0.0.0
"""

import argparse
import json
import sys
import traceback
from datetime import datetime, timezone
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse

# Ensure scripts directory is importable
sys.path.insert(0, str(Path(__file__).parent))

from constants import VERSION

# Maximum request body size: 10 MB
MAX_REQUEST_SIZE = 10 * 1024 * 1024


# ---------------------------------------------------------------------------
# JSON envelope — mirrors cli.py _build_envelope / json_output
# ---------------------------------------------------------------------------

def _build_envelope(command: str, data, exit_code: int = 0) -> dict:
    """Build the standard JSON envelope dict."""
    return {
        "format_version": "1.0",
        "regula_version": VERSION,
        "command": command,
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "exit_code": exit_code,
        "data": data,
    }


def _json_bytes(obj: dict) -> bytes:
    """Serialise a dict to UTF-8 JSON bytes."""
    return json.dumps(obj, indent=2, sort_keys=True, default=str).encode("utf-8")


# ---------------------------------------------------------------------------
# Request handler
# ---------------------------------------------------------------------------

class RegulaHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the Regula REST API."""

    # Silence default stderr logging per request — we do our own logging
    def log_message(self, fmt, *args):
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        sys.stderr.write(f"[{ts}] {fmt % args}\n")

    # ---- CORS ----

    def _set_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_response(200)
        self._set_cors_headers()
        self.send_header("Content-Length", "0")
        self.end_headers()

    # ---- Helpers ----

    def _send_json(self, status: int, body: dict):
        """Send a JSON response with the given HTTP status code."""
        payload = _json_bytes(body)
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self._set_cors_headers()
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _send_error(self, status: int, message: str):
        """Send a JSON error response."""
        body = {
            "error": message,
            "status": status,
        }
        self._send_json(status, body)

    def _read_json_body(self) -> dict:
        """Read and parse the JSON request body.

        Returns the parsed dict, or raises ValueError on failure.
        """
        content_type = self.headers.get("Content-Type", "")
        if "application/json" not in content_type:
            raise ValueError(
                f"Content-Type must be application/json, got: {content_type!r}"
            )

        length_str = self.headers.get("Content-Length", "0")
        try:
            length = int(length_str)
        except (ValueError, TypeError):
            raise ValueError(f"Invalid Content-Length: {length_str!r}")

        if length < 0:
            raise ValueError(f"Invalid Content-Length: {length_str!r}")

        if length > MAX_REQUEST_SIZE:
            raise ValueError(
                f"Request body too large: {length} bytes (max {MAX_REQUEST_SIZE})"
            )

        raw = self.rfile.read(length)
        if not raw:
            raise ValueError("Empty request body")

        return json.loads(raw.decode("utf-8"))

    # ---- Routing ----

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"

        if path == "/health":
            self._handle_health()
        elif path == "/v1/questionnaire":
            self._handle_get_questionnaire()
        elif path == "/v1/dashboard":
            self._handle_dashboard()
        else:
            self._send_error(404, f"Not found: {path}")

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"

        if path == "/v1/check":
            self._handle_check()
        elif path == "/v1/classify":
            self._handle_classify()
        elif path == "/v1/gap":
            self._handle_gap()
        elif path == "/v1/questionnaire/evaluate":
            self._handle_questionnaire_evaluate()
        else:
            self._send_error(404, f"Not found: {path}")

    # ---- Endpoint handlers ----

    def _handle_health(self):
        """GET /health — liveness check."""
        self._send_json(200, {"status": "ok", "version": VERSION})

    def _handle_check(self):
        """POST /v1/check — scan files for risk indicators."""
        try:
            body = self._read_json_body()
        except ValueError as e:
            self._send_error(400, str(e))
            return

        path = body.get("path")
        if not path:
            self._send_error(400, "Missing required field: path")
            return

        target = Path(path).resolve()
        if not target.exists():
            self._send_error(400, f"Path does not exist: {path}")
            return
        if not target.is_dir() and not target.is_file():
            self._send_error(400, f"Path is not a file or directory: {path}")
            return

        # Security: reject paths outside the working directory to prevent
        # scanning arbitrary filesystem locations via the API.
        cwd = Path.cwd().resolve()
        try:
            target.relative_to(cwd)
        except ValueError:
            self._send_error(403, "Path must be within the current working directory")
            return

        min_tier = body.get("min_tier", "")
        valid_tiers = {"", "prohibited", "high_risk", "limited_risk", "minimal_risk"}
        if min_tier not in valid_tiers:
            self._send_error(400, f"Invalid min_tier: {min_tier!r}")
            return
        skip_tests = bool(body.get("skip_tests", False))

        try:
            from report import scan_files
            findings = scan_files(
                str(target),
                respect_ignores=True,
                skip_tests=skip_tests,
                min_tier=min_tier,
            )
            # Sort findings for deterministic output
            findings.sort(
                key=lambda f: (f.get("file", ""), f.get("line", 0), f.get("pattern", ""))
            )
            envelope = _build_envelope("check", findings)
            self._send_json(200, envelope)
        except Exception as e:
            sys.stderr.write(f"Error in /v1/check: {traceback.format_exc()}\n")
            self._send_error(500, "Scan failed. Check server logs for details.")

    def _handle_classify(self):
        """POST /v1/classify — classify text against EU AI Act risk tiers."""
        try:
            body = self._read_json_body()
        except ValueError as e:
            self._send_error(400, str(e))
            return

        text = body.get("input")
        if not text:
            self._send_error(400, "Missing required field: input")
            return

        if not isinstance(text, str):
            self._send_error(400, "Field 'input' must be a string")
            return

        # Limit input size to prevent regex backtracking DoS
        if len(text) > 1_048_576:  # 1 MB
            self._send_error(400, "Field 'input' too large (max 1 MB)")
            return

        try:
            from classify_risk import classify
            result = classify(text)
            envelope = _build_envelope("classify", result.to_dict())
            self._send_json(200, envelope)
        except Exception as e:
            sys.stderr.write(f"Error in /v1/classify: {traceback.format_exc()}\n")
            self._send_error(500, "Classification failed. Check server logs for details.")

    def _handle_gap(self):
        """POST /v1/gap — compliance gap analysis."""
        try:
            body = self._read_json_body()
        except ValueError as e:
            self._send_error(400, str(e))
            return

        path = body.get("path")
        if not path:
            self._send_error(400, "Missing required field: path")
            return

        target = Path(path).resolve()
        if not target.is_dir():
            self._send_error(400, f"Path is not a directory: {path}")
            return

        # Security: reject paths outside the working directory
        cwd = Path.cwd().resolve()
        try:
            target.relative_to(cwd)
        except ValueError:
            self._send_error(403, "Path must be within the current working directory")
            return

        articles = body.get("articles")
        if articles is not None:
            if not isinstance(articles, list):
                self._send_error(400, "Field 'articles' must be a list of article numbers")
                return
            if not all(isinstance(a, (str, int)) for a in articles):
                self._send_error(400, "Each article must be a string or integer")
                return

        try:
            from compliance_check import assess_compliance
            assessment = assess_compliance(str(target), articles=articles)
            envelope = _build_envelope("gap", assessment)
            self._send_json(200, envelope)
        except Exception as e:
            sys.stderr.write(f"Error in /v1/gap: {traceback.format_exc()}\n")
            self._send_error(500, "Gap analysis failed. Check server logs for details.")

    def _handle_get_questionnaire(self):
        """GET /v1/questionnaire — return the governance self-assessment questionnaire."""
        try:
            from questionnaire import generate_questionnaire
            questionnaire = generate_questionnaire()
            envelope = _build_envelope("questionnaire", questionnaire)
            self._send_json(200, envelope)
        except Exception as e:
            sys.stderr.write(f"Error in /v1/questionnaire: {traceback.format_exc()}\n")
            self._send_error(500, "Questionnaire generation failed. Check server logs for details.")

    def _handle_questionnaire_evaluate(self):
        """POST /v1/questionnaire/evaluate — evaluate questionnaire answers."""
        try:
            body = self._read_json_body()
        except ValueError as e:
            self._send_error(400, str(e))
            return

        answers = body.get("answers")
        if not answers or not isinstance(answers, dict):
            self._send_error(400, "Missing or invalid field: answers (must be a dict of question_id -> yes/no/unsure)")
            return

        # Validate answer values
        valid_answers = {"yes", "no", "unsure"}
        for qid, answer in answers.items():
            if answer not in valid_answers:
                self._send_error(400, f"Invalid answer for '{qid}': {answer!r} (must be yes/no/unsure)")
                return

        try:
            from questionnaire import evaluate_questionnaire
            result = evaluate_questionnaire(answers)
            envelope = _build_envelope("questionnaire/evaluate", result.to_dict())
            self._send_json(200, envelope)
        except Exception as e:
            sys.stderr.write(f"Error in /v1/questionnaire/evaluate: {traceback.format_exc()}\n")
            self._send_error(500, "Questionnaire evaluation failed. Check server logs for details.")

    def _handle_dashboard(self):
        """GET /v1/dashboard — serve static dashboard or JSON status."""
        dashboard_dir = Path(__file__).parent / "dashboard"
        index_file = dashboard_dir / "index.html"

        if index_file.is_file():
            try:
                html = index_file.read_text(encoding="utf-8")
                payload = html.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self._set_cors_headers()
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
            except (OSError, PermissionError) as e:
                sys.stderr.write(f"Error reading dashboard: {e}\n")
                self._send_error(500, "Failed to read dashboard. Check server logs for details.")
        else:
            # Fallback: JSON status
            self._send_json(200, _build_envelope("dashboard", {
                "status": "ok",
                "version": VERSION,
                "message": "No dashboard files found. Place index.html in scripts/dashboard/ to enable.",
            }))


# ---------------------------------------------------------------------------
# Server startup
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Regula REST API server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--host",
        default="localhost",
        help="Bind address (default: localhost)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8487,
        help="Listen port (default: 8487)",
    )
    args = parser.parse_args()

    server = HTTPServer((args.host, args.port), RegulaHandler)
    sys.stderr.write(
        f"Regula API v{VERSION} listening on http://{args.host}:{args.port}\n"
        f"Security: No authentication — do NOT expose on public networks.\n"
        f"Endpoints:\n"
        f"  GET  /health\n"
        f"  POST /v1/check\n"
        f"  POST /v1/classify\n"
        f"  POST /v1/gap\n"
        f"  GET  /v1/questionnaire\n"
        f"  POST /v1/questionnaire/evaluate\n"
        f"  GET  /v1/dashboard\n"
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        sys.stderr.write("\nShutting down.\n")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
