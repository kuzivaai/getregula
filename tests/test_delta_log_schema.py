# regula-ignore
"""The delta log's JSON Schema had no gate, and an entry was violating it.

`content/regulations/delta-log/schema.json` has existed alongside the
entries since the delta log was built, and `build_delta_log.py` reads the
entries without validating them against it. Nothing else did either.

MEASURED 2026-07-29, the first time anything checked. Of the 10 entries
already tracked, `2026-04-29-trilogue-failed.json` carried a `summary` of
**1058 characters against the schema's `maxLength` of 1000**, and had
done since it was committed. Both entries added the same day failed too,
because `impact_on_regula_patterns` is an array of objects with a
`pattern_id` and an enumerated `change`, not the free prose it looks
like. So on first contact the schema rejected 3 of 12.

A schema that nothing runs is documentation, not a gate. This file is the
gate. Finding F31.

**Why this test hard-fails instead of skipping when `jsonschema` is
missing.** The recorded defect in this repo is a schema test that
degrades silently when its validator is absent, so it reports green while
checking nothing. `jsonschema` is installed (4.26.0) but appears in no
dependency list. A `pytest.importorskip` here would rebuild exactly the
blank gate this file exists to close, so an absent validator is a
failure, with a message that says how to fix it.

The delta log is the regulatory-currency asset. Entries in it are the
provenance for published regulatory claims, so an entry that silently
drifts out of schema is a claim whose structure nobody checked.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
DELTA_DIR = REPO_ROOT / "content" / "regulations" / "delta-log"
SCHEMA_PATH = DELTA_DIR / "schema.json"
ENTRIES_DIR = DELTA_DIR / "entries"


def _validator():
    """Import jsonschema, failing loudly rather than skipping."""
    try:
        import jsonschema
    except ImportError as exc:  # pragma: no cover - environment defect
        pytest.fail(
            "jsonschema is not importable, so the delta-log schema gate "
            "cannot run. This is a FAILURE, not a skip: a schema test that "
            "quietly does nothing is the blank gate this file exists to "
            f"close. Install it with `pip install jsonschema`. ({exc})"
        )
    return jsonschema


def _entries() -> list[Path]:
    return sorted(ENTRIES_DIR.glob("*.json"))


def test_schema_and_entries_exist() -> None:
    """Guard against the whole suite passing because nothing was found."""
    assert SCHEMA_PATH.is_file(), f"missing schema: {SCHEMA_PATH}"
    found = _entries()
    assert found, f"no delta-log entries found under {ENTRIES_DIR}"
    # A count floor. If a glob change or a move empties this directory, the
    # per-entry test below would pass vacuously with zero iterations.
    assert len(found) >= 12, (
        f"expected at least 12 delta-log entries, found {len(found)}. "
        "If entries were deliberately removed, lower this floor in the "
        "same commit and say why."
    )


@pytest.mark.parametrize("entry_path", _entries(), ids=lambda p: p.stem)
def test_entry_validates_against_schema(entry_path: Path) -> None:
    """Every tracked entry must satisfy the delta log's own schema."""
    jsonschema = _validator()
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    entry = json.loads(entry_path.read_text(encoding="utf-8"))
    try:
        jsonschema.validate(entry, schema)
    except jsonschema.ValidationError as exc:
        field = ".".join(str(p) for p in exc.absolute_path) or "<root>"
        pytest.fail(
            f"{entry_path.name} violates schema.json at '{field}': "
            f"{exc.validator}={exc.validator_value}. {exc.message[:300]}"
        )


def test_control_an_invalid_entry_is_rejected() -> None:
    """The control. If this does not fail, the gate above proves nothing.

    Measurement rule 4: an absent signal is not a passing signal. This
    plants each of the two defects actually found on 2026-07-29 and
    asserts the same code path rejects them.
    """
    jsonschema = _validator()
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    good = json.loads((ENTRIES_DIR / "2026-07-24-oj-publication.json")
                      .read_text(encoding="utf-8"))
    jsonschema.validate(good, schema)  # the fixture itself must be valid

    over_length = dict(good, summary="x" * 1001)
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(over_length, schema)

    prose_impact = dict(good, impact_on_regula_patterns="free prose, not a list")
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(prose_impact, schema)

    missing_required = {k: v for k, v in good.items() if k != "confidence"}
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(missing_required, schema)
