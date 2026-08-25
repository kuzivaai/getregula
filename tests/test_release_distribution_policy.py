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
EXPERIMENTS = ROOT / "data" / "distribution_experiments.json"
RESEARCH_GATE = ROOT / "data" / "research_execution_gate.json"


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

    directory_action = next(
        action for action in policy["actions"]
        if action["action_id"] == "mcp-so-directory-submission-2026-08-25"
    )
    assert directory_action["decision"] == "EXECUTED_PENDING_EXTERNAL_REVIEW"
    assert directory_action["executed_at"] == "2026-08-25T08:00:17Z"
    assert "RECEIPT_5407302795_VERIFIED" in directory_action["result"]
    assert "NOT_LISTED_OR_ACCEPTED_YET" in directory_action["result"]

    glama_action = next(
        action for action in policy["actions"]
        if action["action_id"] == "glama-directory-submission-2026-08-25"
    )
    assert glama_action["decision"] == "EXTERNAL_EXECUTION_BLOCKED"
    assert glama_action["executed_at"] is None
    assert glama_action["owner_fact_required"] is True
    assert "0_OAUTH_GRANTS" in glama_action["result"]
    assert "0_SUBMISSIONS" in glama_action["result"]


def test_hard_stop_states_cannot_be_mistaken_for_authorisation():
    states = _policy()["effective_states"]
    assert states["PERSONAL_DATA_WEB_FORM"] == "DISABLED_UNTIL_PRIVACY_GATE"
    assert states["PAYMENT_GATE"] == "NOT_ACTIVE"
    assert states["CONSULTANT_BOOKING"] == "NOT_AVAILABLE"
    assert states["CUSTOMER_SOURCE_UPLOAD"] == "NOT_ACCEPTED"


def test_distribution_experiments_are_preregistered_with_complete_fields():
    register = json.loads(EXPERIMENTS.read_text(encoding="utf-8"))
    required = {
        "experiment_id", "target_segment", "decision_question", "hypothesis",
        "counter_hypothesis", "channel", "asset", "baseline",
        "primary_metric", "guardrail", "denominator", "minimum_observation",
        "cost_cap", "owner_effort_cap", "result", "uncertainty", "decision",
        "stop_condition",
    }
    ids = []
    for experiment in register["experiments"]:
        assert set(experiment) == required, experiment.get("experiment_id")
        assert experiment["result"] is None
        ids.append(experiment["experiment_id"])
    assert len(ids) == len(set(ids))

    directory_experiment = next(
        experiment for experiment in register["experiments"]
        if experiment["experiment_id"] == "DIST-007-MCP-DIRECTORY-DISCOVERY"
    )
    assert directory_experiment["decision"] == "SUBMITTED_PENDING_EXTERNAL_REVIEW"
    assert directory_experiment["result"] is None
    assert "Do not duplicate" in directory_experiment["stop_condition"]

    glama_experiment = next(
        experiment for experiment in register["experiments"]
        if experiment["experiment_id"] == "DIST-008-GLAMA-MCP-DISCOVERY"
    )
    assert glama_experiment["decision"] == "HOLD_EXTERNAL_ACCOUNT_TERMS_AND_AUTH"
    assert glama_experiment["result"] is None
    assert "Do not create an account" in glama_experiment["stop_condition"]

    submissions = (ROOT / "docs" / "distribution" / "SUBMISSIONS.md").read_text(
        encoding="utf-8"
    )
    assert "issuecomment-5407302795" in submissions
    assert "f3d0d525f1ae91f375c7dddccdbccee1f6cca3174c4812890cfd1bd908340be0" in submissions
    assert "submitted only, not listed or accepted" in submissions
    assert "0 accounts, 0 OAuth grants, 0 submissions, 0 listings" in submissions


def test_research_action_agrees_with_the_fail_closed_gate():
    gate = json.loads(RESEARCH_GATE.read_text(encoding="utf-8"))
    action = next(
        item for item in _policy()["actions"]
        if item["action_id"] == "moderated-founder-research-readiness-2026-08-25"
    )
    assert gate["execution_state"] == "BLOCKED"
    assert gate["external_research"] == "DISABLED"
    assert gate["participants_contacted"] == 0
    assert gate["sessions_completed"] == 0
    assert len(gate["unresolved_facts"]) == 19
    assert action["decision"] == "EXTERNAL_EXECUTION_BLOCKED"
    assert action["executed_at"] is None
    assert action["result"].endswith("19_LAUNCH_FACTS_UNRESOLVED")


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


def test_github_release_reuses_verified_artifacts_after_pypi_smoke_tests():
    source = (
        ROOT / ".github" / "workflows" / "release.yml"
    ).read_text(encoding="utf-8")
    release_job = source.split("\n  github-release:\n", 1)[1]

    assert release_job.startswith("    needs: verify\n")
    assert "permissions:\n      contents: write" in release_job
    assert (
        "actions/download-artifact@"
        "3e5f45b2cfb9172054b4087a40e8e0b5a5461e7c"
    ) in release_job
    assert "name: dist" in release_job
    assert "sha256sum regula_ai-*.whl regula_ai-*.tar.gz > SHA256SUMS" in release_job
    assert 'gh release create "$RELEASE_TAG"' in release_job
    assert "--verify-tag" in release_job
