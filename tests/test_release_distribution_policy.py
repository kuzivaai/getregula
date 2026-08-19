"""Machine checks for the owner directive and the new I/O boundaries."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from safe_io import (  # noqa: E402
    UnsafeUrlError,
    UnsafeXmlError,
    parse_xml_text,
    validate_https_url,
)
from svg_text import SvgTextError, rendered_lines  # noqa: E402


POLICY = ROOT / "data" / "distribution_execution_policy.json"


def _policy() -> dict:
    return json.loads(POLICY.read_text(encoding="utf-8"))


def _raises(error_type, fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except error_type:
        return
    raise AssertionError(f"expected {error_type.__name__}")


def test_distribution_policy_records_the_owner_source_by_hash():
    policy = _policy()
    assert policy["effective_date"] == "2026-08-19"
    assert len(policy["owner_authorisation"]["sha256"]) == 64
    assert policy["repository"]["expected_pull_request"] == 55


def test_every_distribution_action_is_a_complete_evidence_manifest():
    policy = _policy()
    required = set(policy["manifest_required_fields"])
    assert required
    for action in policy["actions"]:
        assert required == set(action), action["action_id"]
        assert action["risk_class"] in policy["action_classes"]


def test_hard_stop_states_cannot_be_mistaken_for_authorisation():
    states = _policy()["effective_states"]
    assert states["PERSONAL_DATA_WEB_FORM"] == "DISABLED_UNTIL_PRIVACY_GATE"
    assert states["PAYMENT_GATE"] == "NOT_ACTIVE"
    assert states["CONSULTANT_BOOKING"] == "NOT_AVAILABLE"
    assert states["CUSTOMER_SOURCE_UPLOAD"] == "NOT_ACCEPTED"


def test_https_validator_accepts_only_the_exact_allowlisted_host():
    assert validate_https_url(
        "https://api.github.com/repos/kuzivaai/getregula",
        frozenset({"api.github.com"}),
    ).startswith("https://")
    _raises(
        UnsafeUrlError,
        validate_https_url,
        "https://api.github.com.attacker.example/",
        frozenset({"api.github.com"}),
    )


def test_https_validator_refuses_scheme_credentials_and_nondefault_port():
    allowed = frozenset({"example.com"})
    _raises(UnsafeUrlError, validate_https_url, "file:///etc/passwd", allowed)
    _raises(
        UnsafeUrlError,
        validate_https_url,
        "https://example.com@attacker.example/",
        allowed,
    )
    _raises(
        UnsafeUrlError,
        validate_https_url,
        "https://example.com:444/",
        allowed,
    )


def test_xml_parser_refuses_dtd_and_entity_declarations():
    payload = '<!DOCTYPE x [<!ENTITY y "boom">]><x>&y;</x>'
    _raises(UnsafeXmlError, parse_xml_text, payload)


def test_xml_parser_enforces_the_byte_limit_before_parsing():
    _raises(UnsafeXmlError, parse_xml_text, "<x>12345</x>", max_bytes=5)


def test_svg_reader_fails_closed_on_refused_xml_declarations():
    payload = '<!DOCTYPE svg [<!ENTITY y "boom">]><svg>&y;</svg>'
    _raises(SvgTextError, rendered_lines, payload)


def test_pdf_export_does_not_enable_vulnerable_presentational_hints():
    source = (ROOT / "scripts" / "pdf_export.py").read_text(encoding="utf-8")
    assert "presentational_hints=True" not in source


def test_ci_signing_dependency_cannot_fall_below_the_audited_floor():
    workflows = (
        ROOT / ".github" / "workflows" / "ci.yaml",
        ROOT / ".github" / "workflows" / "test-parallel-experiment.yml",
    )
    for workflow in workflows:
        source = workflow.read_text(encoding="utf-8")
        assert "cryptography>=41,<51" not in source
        assert "cryptography>=50.0.0,<51" in source
