#!/usr/bin/env python3
"""Validate and report the fail-closed moderated-research launch gate."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GATE = REPO_ROOT / "data" / "research_execution_gate.json"

REQUIRED_TOP_LEVEL = {
    "format_version",
    "gate_id",
    "updated_at",
    "scope",
    "execution_state",
    "external_research",
    "decision",
    "result",
    "participants_contacted",
    "sessions_completed",
    "personal_data_in_repository",
    "required_launch_facts",
    "unresolved_facts",
    "launch_authorisation",
    "prohibited_inputs",
    "required_controls",
    "artefacts",
}

REQUIRED_LAUNCH_FACTS = {
    "controller_identity",
    "controller_contact",
    "research_lead",
    "applicable_jurisdictions",
    "lawful_basis",
    "lawful_basis_review_evidence",
    "participant_notice_version",
    "participant_notice_approval_evidence",
    "approved_storage_system",
    "storage_region",
    "storage_access_roles",
    "processor_and_transfer_record",
    "retention_period",
    "withdrawal_route",
    "rights_request_route",
    "incident_route",
    "participant_contact_source",
    "approved_recruitment_sender",
    "incentive_policy",
    "recording_mode",
}

REQUIRED_AUTHORISATION_FIELDS = {
    "status",
    "authorised_by",
    "authorised_at",
    "evidence_reference",
}

EMPTY_VALUES = (None, "", "TBD", "UNRESOLVED", "UNKNOWN")


def _is_tracked(path: Path) -> bool:
    result = subprocess.run(
        ["git", "ls-files", "--error-unmatch", str(path.relative_to(REPO_ROOT))],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0


def load_gate(path: Path = DEFAULT_GATE) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def unresolved_launch_facts(record: dict) -> list[str]:
    facts = record.get("required_launch_facts", {})
    if not isinstance(facts, dict):
        return sorted(REQUIRED_LAUNCH_FACTS)
    return sorted(key for key in REQUIRED_LAUNCH_FACTS if facts.get(key) in EMPTY_VALUES)


def readiness_blockers(record: dict) -> list[str]:
    """Return blockers; repository data can never silently authorise research."""
    blockers = [f"unresolved:{key}" for key in unresolved_launch_facts(record)]
    authorisation = record.get("launch_authorisation", {})
    if not isinstance(authorisation, dict):
        authorisation = {}
    if authorisation.get("status") != "GRANTED":
        blockers.append("owner_launch_authorisation_not_granted")
    if record.get("external_research") != "ENABLED":
        blockers.append("external_research_disabled")
    blockers.append("repository_gate_cannot_authorise_external_contact")
    return blockers


def validate_record(
    record: dict,
    *,
    require_artefacts: bool = True,
    require_tracked: bool = True,
) -> list[str]:
    if not isinstance(record, dict):
        return ["research gate root must be an object"]

    errors: list[str] = []

    if set(record) != REQUIRED_TOP_LEVEL:
        missing = sorted(REQUIRED_TOP_LEVEL - set(record))
        extra = sorted(set(record) - REQUIRED_TOP_LEVEL)
        if missing:
            errors.append(f"missing top-level fields: {', '.join(missing)}")
        if extra:
            errors.append(f"unexpected top-level fields: {', '.join(extra)}")

    facts = record.get("required_launch_facts")
    if not isinstance(facts, dict) or set(facts) != REQUIRED_LAUNCH_FACTS:
        errors.append("required_launch_facts does not match the controlled schema")
    facts_for_checks = facts if isinstance(facts, dict) else {}

    authorisation = record.get("launch_authorisation")
    if not isinstance(authorisation, dict) or set(authorisation) != REQUIRED_AUTHORISATION_FIELDS:
        errors.append("launch_authorisation does not match the controlled schema")
    authorisation_for_checks = authorisation if isinstance(authorisation, dict) else {}

    if record.get("execution_state") != "BLOCKED":
        errors.append("canonical execution_state must remain BLOCKED")
    if record.get("external_research") != "DISABLED":
        errors.append("canonical external_research must remain DISABLED")
    if record.get("decision") != "HOLD_RESEARCH_PRIVACY_GATE":
        errors.append("canonical decision must remain HOLD_RESEARCH_PRIVACY_GATE")
    if record.get("participants_contacted") != 0:
        errors.append("participants_contacted must remain zero while research is disabled")
    if record.get("sessions_completed") != 0:
        errors.append("sessions_completed must remain zero while research is disabled")
    if record.get("personal_data_in_repository") is not False:
        errors.append("personal_data_in_repository must be false")
    if facts_for_checks.get("recording_mode") != "NO_RECORDING":
        errors.append("the current formative protocol must remain NO_RECORDING")

    expected_unresolved = unresolved_launch_facts(record)
    if record.get("unresolved_facts") != expected_unresolved:
        errors.append("unresolved_facts does not match the empty launch facts")

    if authorisation_for_checks.get("status") != "NOT_GRANTED":
        errors.append("canonical launch authorisation must remain NOT_GRANTED")
    for key in ("authorised_by", "authorised_at", "evidence_reference"):
        if authorisation_for_checks.get(key) is not None:
            errors.append(f"launch_authorisation.{key} must remain null")

    if not record.get("prohibited_inputs"):
        errors.append("prohibited_inputs must not be empty")
    if not record.get("required_controls"):
        errors.append("required_controls must not be empty")

    artefacts = record.get("artefacts")
    if not isinstance(artefacts, list) or not artefacts:
        errors.append("artefacts must be a non-empty list")
    elif require_artefacts:
        for relative in artefacts:
            path = REPO_ROOT / relative
            if not path.is_file() or path.stat().st_size == 0:
                errors.append(f"missing or empty artefact: {relative}")
            elif require_tracked and not _is_tracked(path):
                errors.append(f"untracked artefact: {relative}")

    return sorted(set(errors))


def validate(
    path: Path = DEFAULT_GATE,
    *,
    require_tracked: bool = True,
) -> list[str]:
    try:
        record = load_gate(path)
    except (OSError, json.JSONDecodeError) as exc:
        return [f"invalid research gate: {exc}"]
    return validate_record(record, require_tracked=require_tracked)


def status_payload(record: dict) -> dict:
    blockers = readiness_blockers(record)
    return {
        "gate_id": record.get("gate_id"),
        "execution_state": record.get("execution_state"),
        "external_research": record.get("external_research"),
        "participants_contacted": record.get("participants_contacted"),
        "sessions_completed": record.get("sessions_completed"),
        "blockers": blockers,
        "can_contact_participants": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate or report the moderated-research launch gate."
    )
    parser.add_argument("--gate", type=Path, default=DEFAULT_GATE)
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--allow-untracked", action="store_true")
    args = parser.parse_args(argv)

    errors = validate(args.gate.resolve(), require_tracked=not args.allow_untracked)
    if errors:
        print(f"research-gate: INVALID ({len(errors)} errors)")
        for error in errors:
            print(f"- {error}")
        return 1

    record = load_gate(args.gate.resolve())
    payload = status_payload(record)
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    elif args.status:
        print(
            "research-gate: BLOCKED — "
            f"{len(payload['blockers'])} launch blockers; "
            "0 participants contacted; external research disabled"
        )
        for blocker in payload["blockers"]:
            print(f"- {blocker}")
    else:
        print(
            "research-gate: VALID BLOCKED STATE — controls are internally "
            "consistent; this is not launch authorisation"
        )
    return 2 if args.status and payload["blockers"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
