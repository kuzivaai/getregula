"""Controls for the machine-readable independent evaluation protocol."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "benchmarks"))

import validate_evaluation_protocol as protocol


def committed_protocol() -> dict:
    return json.loads(protocol.DEFAULT_PROTOCOL.read_text(encoding="utf-8"))


def test_committed_evaluation_protocol_is_valid():
    assert protocol.validate(committed_protocol()) == []


def test_single_maintainer_cannot_satisfy_independence_gate():
    payload = copy.deepcopy(committed_protocol())
    payload["annotation"]["minimum_independent_human_raters"] = 1
    assert any("three independent" in error for error in protocol.validate(payload))


def test_random_function_split_cannot_replace_project_temporal_split():
    payload = copy.deepcopy(committed_protocol())
    payload["corpus"]["split_unit"] = "function"
    payload["corpus"]["split_strategy"] = "random"
    errors = protocol.validate(payload)
    assert any("split unit" in error for error in errors)
    assert any("chronological" in error for error in errors)


def test_missing_context_cannot_be_silently_counted_as_negative():
    payload = copy.deepcopy(committed_protocol())
    payload["annotation"]["not_assessable_treatment"] = "negative"
    assert any("not_assessable" in error for error in protocol.validate(payload))


def test_completion_status_must_disclose_skips():
    payload = copy.deepcopy(committed_protocol())
    payload["repeatability"]["completion_statuses"] = ["completed", "failed"]
    assert any("completion statuses" in error for error in protocol.validate(payload))
