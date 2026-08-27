"""Tests for the fail-closed public release status."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import publication_gate as gate


def _ready() -> dict[str, object]:
    return {
        "schema_version": 1,
        "publication_allowed": True,
        "reviewed_on": "2026-08-27",
        "reason_code": "approved_for_release",
        "conditions": {name: True for name in gate.REQUIRED_CONDITIONS},
    }


def test_committed_publication_status_blocks_release():
    document = gate.load_status(gate.DEFAULT_STATUS)
    errors = gate.evaluate(document)
    assert "publication_allowed is false" in errors
    assert any(error.startswith("unmet conditions:") for error in errors)


def test_publication_gate_requires_every_named_condition():
    document = _ready()
    document["conditions"]["pypi_control_confirmed"] = False
    assert gate.evaluate(document) == [
        "unmet conditions: pypi_control_confirmed"
    ]


def test_publication_gate_accepts_complete_reviewed_status():
    assert gate.evaluate(_ready()) == []


def test_publication_gate_rejects_missing_or_unexpected_conditions():
    document = _ready()
    del document["conditions"]["durable_name_decision_recorded"]
    document["conditions"]["informal_override"] = True
    errors = gate.evaluate(document)
    assert "missing conditions: durable_name_decision_recorded" in errors
    assert "unexpected conditions: informal_override" in errors


def test_publication_gate_returns_two_for_unreadable_status(tmp_path: Path):
    status = tmp_path / "status.json"
    status.write_text("not json", encoding="utf-8")
    assert gate.main(["--status", str(status)]) == 2


def test_publication_status_round_trips_as_canonical_json():
    document = gate.load_status(gate.DEFAULT_STATUS)
    encoded = json.dumps(document, sort_keys=True)
    assert json.loads(encoded) == document


def test_release_workflow_enforces_publication_and_tag_identity_before_build():
    workflow = (
        Path(__file__).parent.parent / ".github" / "workflows" / "release.yml"
    ).read_text(encoding="utf-8")
    tag_check = workflow.index("Assert verified annotated tag points at current main")
    publication_check = workflow.index("python3 scripts/publication_gate.py")
    build = workflow.index("run: python3 -m build")
    publish = workflow.index("name: Publish to PyPI")
    assert tag_check < publication_check < build < publish
    assert 'git cat-file -t "$TAG_OBJECT"' in workflow
    assert 'git rev-parse "$GITHUB_REF^{commit}"' in workflow
    assert "'.verification.verified'" in workflow
