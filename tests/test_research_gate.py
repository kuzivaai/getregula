"""Fail-closed controls for moderated founder and evidence-pack research."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from research_gate import (  # noqa: E402
    DEFAULT_GATE,
    readiness_blockers,
    status_payload,
    validate,
    validate_record,
)


def _record() -> dict:
    return json.loads(DEFAULT_GATE.read_text(encoding="utf-8"))


def test_research_gate_is_valid_and_explicitly_blocked():
    assert validate(DEFAULT_GATE, require_tracked=False) == []
    payload = status_payload(_record())
    assert payload["execution_state"] == "BLOCKED"
    assert payload["external_research"] == "DISABLED"
    assert payload["can_contact_participants"] is False
    assert payload["participants_contacted"] == 0
    assert payload["sessions_completed"] == 0


def test_research_gate_fails_if_external_research_is_enabled():
    record = _record()
    record["external_research"] = "ENABLED"
    errors = validate_record(record, require_artefacts=False)
    assert "canonical external_research must remain DISABLED" in errors


def test_research_gate_fails_if_participant_activity_is_claimed():
    record = _record()
    record["participants_contacted"] = 1
    record["sessions_completed"] = 1
    errors = validate_record(record, require_artefacts=False)
    assert "participants_contacted must remain zero while research is disabled" in errors
    assert "sessions_completed must remain zero while research is disabled" in errors


def test_research_gate_fails_if_unresolved_register_drifts():
    record = _record()
    record["unresolved_facts"].pop()
    errors = validate_record(record, require_artefacts=False)
    assert "unresolved_facts does not match the empty launch facts" in errors


def test_complete_facts_cannot_silently_replace_owner_authorisation():
    record = copy.deepcopy(_record())
    for key, value in record["required_launch_facts"].items():
        if value is None:
            record["required_launch_facts"][key] = f"evidence:{key}"
    record["unresolved_facts"] = []
    blockers = readiness_blockers(record)
    assert "owner_launch_authorisation_not_granted" in blockers
    assert "external_research_disabled" in blockers
    assert "repository_gate_cannot_authorise_external_contact" in blockers
    assert not any(item.startswith("unresolved:") for item in blockers)


def test_malformed_fact_and_authorisation_objects_fail_without_crashing():
    assert validate_record([], require_artefacts=False) == [
        "research gate root must be an object"
    ]

    record = _record()
    record["required_launch_facts"] = []
    record["launch_authorisation"] = []
    errors = validate_record(record, require_artefacts=False)
    assert "required_launch_facts does not match the controlled schema" in errors
    assert "launch_authorisation does not match the controlled schema" in errors


def test_protocol_prohibits_recruitment_and_overclaiming():
    protocol = (
        ROOT / "docs" / "research" /
        "FOUNDER-USABILITY-RESEARCH-GATE-2026-08-25.md"
    ).read_text(encoding="utf-8").replace("**", "")
    for statement in (
        "External research: DISABLED",
        "do not recruit or contact anyone",
        "does not determine legal applicability",
        "not a power calculation",
        "Pseudonymised does not mean anonymous",
    ):
        assert statement in protocol
