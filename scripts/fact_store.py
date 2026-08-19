#!/usr/bin/env python3
"""A project-local store for facts a person has declared about their system.

Why this exists
---------------

Ledger N149. `regula check` reported `insufficient_information` and named
exactly two facts. `regula assess` asked questions that answer exactly those two
facts, printed a result, and its own Next steps said to run `regula check .`.
Nothing was written anywhere. Running `check` again returned the identical block
naming the identical two facts. Demonstrated in both directions on a third-party
repository, and the enumeration across `scripts/cli.py` and
`scripts/decision_adapters.py` found no `--fact`, `declared_facts`, `facts_file`
or `sourced_facts` route of any kind.

The result is that the honest core of the product, a decision that declines to
be made until someone supplies the facts code cannot show, had no way to receive
those facts. This module is that way.

What it is NOT
--------------

It is not a source of facts. **Regula establishes no fact in this store.**
Every value here is something a person asserted, and the provenance records who
asserted it, through which command, in answer to which question, and when. That
distinction is the whole product, so it is carried in the data rather than in a
docstring.

A resolved fact may move a decision from `insufficient_information` to an
`indication`. It may never produce a risk tier, a compliance score, a readiness
percentage or an effort estimate: this module hands facts to the kernel and the
kernel's own output is what a reader sees.

Where it lives, and why there
-----------------------------

`<project>/.regula/facts.json`.

Project-local rather than `~/.regula`, because a fact is about the system being
assessed and not about the person or the machine. Two projects on one laptop
have different answers, and a home-directory store would carry one project's
declaration into another's assessment silently. That is the shape of defect
N112/N113 recorded for the scan cache, where a key that ignored context served
one scan's entry to another, and it is not worth repeating in a store whose
contents are legal assertions.

`.regula/` is the directory this tool already writes project-local output into
(the registry, `plan-status.json`, the audit trail), so no new convention is
invented.

Schema, and what migrates
-------------------------

The value shape is the decision kernel's own `FactValue` contract, verbatim, and
every value is validated by `FactValue.from_dict` on the way in and on the way
out. Restating the contract in a second place is the divergence N81 recorded for
copied decision engines; there is one contract and this file uses it.

    {
      "schema_version": "1.0",
      "model_version": "<the model the declarations were made against>",
      "facts": {"<fact_id>": {"values": [<FactValue>, ...]}}
    }

The `facts` object is exactly the `facts` half of a kernel request, so a store
can be handed to the kernel without translation.

**Nothing migrates.** This file did not exist before 2026-08-17: no code wrote
it and no code read it, so there is no prior shape and no user's disk carries
one. An existing `.regula/` directory is unaffected, because this is a new file
beside the ones already there and nothing else reads it.

Two failure modes are handled by refusing rather than guessing:

* an unknown `schema_version` is refused, because a store written by a later
  version may mean something different by the same field;
* a fact id the current model does not define is refused, because the id is the
  only thing that binds a declaration to a legal predicate.

A `model_version` that differs from the running kernel's is **not** refused. It
is reported, on every run, naming both versions, because the declarations remain
the user's and stranding them would leave re-answering as the only remedy. The
notice travels into the JSON output as well as the text output.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping

sys.path.insert(0, str(Path(__file__).parent))

from decision_kernel import DecisionInputError, FactState, FactValue  # noqa: E402
from errors import UsageError  # noqa: E402

SCHEMA_VERSION = "1.0"
STORE_RELATIVE_PATH = ".regula/facts.json"

# Source types. `user_attestation` is a person answering a question in their own
# words; `user_declaration` is a person answering one of this tool's questions.
# Neither is `tool_observation`, and no writer in this repository emits one,
# which is checked by tests rather than promised here.
SOURCE_USER_ATTESTATION = "user_attestation"
SOURCE_USER_DECLARATION = "user_declaration"


class FactStoreError(UsageError):
    """The store could not be read, written or understood.

    A `UsageError` and not a bare exception, so the CLI exits 2 and says the
    request cannot be satisfied. Reporting a malformed declaration as an
    internal bug, or worse as a success, is the N119 class: `plan --done`
    printed "Marked <id> as completed" and exited 0 for a task no plan
    contained.
    """


def store_path(project: str | Path) -> Path:
    return Path(project) / STORE_RELATIVE_PATH


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_fact_argument(raw: str) -> tuple[str, str]:
    """Parse one `--fact id=state` argument.

    `unknown` is a legal state and is preserved as `unknown`. It is never
    normalised to `no`: absence, explicit unknown and an explicit negative are
    three different answers and the kernel treats them as three (N94).
    """
    if not isinstance(raw, str) or "=" not in raw:
        raise FactStoreError(
            f"--fact expects id=state, got {raw!r}. States: "
            + ", ".join(s.value for s in FactState))
    fact_id, _, state = raw.partition("=")
    fact_id = fact_id.strip()
    state = state.strip().lower()
    if not fact_id:
        raise FactStoreError(f"--fact {raw!r} has an empty fact id")
    try:
        FactState(state)
    except ValueError as exc:
        raise FactStoreError(
            f"--fact {raw!r}: {state!r} is not a fact state. Use one of: "
            + ", ".join(s.value for s in FactState)) from exc
    return fact_id, state


def build_value(state: str, jurisdiction: str, source_ref: str,
                source_type: str = SOURCE_USER_ATTESTATION,
                timestamp: str | None = None, **provenance: Any) -> dict:
    """One canonical fact value, validated by the kernel's own constructor.

    Validating here rather than only at evaluation time means a store can never
    contain a value the kernel would refuse, so a file on disk cannot become an
    unreadable record of somebody's answers.
    """
    value = {
        "state": state,
        "provenance": {
            "source_type": source_type,
            "source_ref": source_ref,
            **{k: v for k, v in provenance.items() if v is not None},
        },
        "jurisdiction": jurisdiction,
        "timestamp": timestamp or now_iso(),
    }
    FactValue.from_dict(value, "<new>")     # raises DecisionInputError if invalid
    return value


def known_fact_ids(model: Mapping[str, Any]) -> set:
    definitions = model.get("fact_definitions") or {}
    return set(definitions)


def load(path: Path, model: Mapping[str, Any]) -> dict:
    """Read a store and return `{facts, model_version, path, notices}`.

    Fails closed. An unreadable, malformed, unknown-schema or unknown-fact-id
    store raises rather than returning an empty fact map, because an empty fact
    map is indistinguishable from "the user declared nothing" and would silently
    discard the answers this module exists to keep (measurement rule 4).
    """
    try:
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
    except OSError as exc:
        raise FactStoreError(f"{path}: cannot read fact store ({exc})") from exc
    except json.JSONDecodeError as exc:
        raise FactStoreError(f"{path}: fact store is not valid JSON ({exc})") from exc

    if not isinstance(raw, Mapping):
        raise FactStoreError(f"{path}: fact store must be a JSON object")
    schema = raw.get("schema_version")
    if schema != SCHEMA_VERSION:
        raise FactStoreError(
            f"{path}: fact store schema_version is {schema!r}; this build reads "
            f"{SCHEMA_VERSION!r} only. Refusing rather than guessing what a "
            f"different schema means by the same field.")
    facts = raw.get("facts")
    if not isinstance(facts, Mapping):
        raise FactStoreError(f"{path}: fact store has no `facts` object")

    known = known_fact_ids(model)
    notices = []
    cleaned: dict[str, dict] = {}
    for fact_id, entry in facts.items():
        if fact_id not in known:
            raise FactStoreError(
                f"{path}: fact id {fact_id!r} is not defined by decision model "
                f"{model.get('model_version')!r}. The id is what binds a "
                f"declaration to a legal predicate, so an unknown one is refused.")
        if not isinstance(entry, Mapping) or not isinstance(entry.get("values"), list):
            raise FactStoreError(f"{path}: fact {fact_id!r} must be an object with `values`")
        if not entry["values"]:
            raise FactStoreError(f"{path}: fact {fact_id!r} has no values")
        for value in entry["values"]:
            try:
                FactValue.from_dict(value, fact_id)
            except DecisionInputError as exc:
                raise FactStoreError(f"{path}: {exc}") from exc
        cleaned[fact_id] = {"values": [dict(v) for v in entry["values"]]}

    stored_model = raw.get("model_version")
    running_model = model.get("model_version")
    if stored_model and running_model and stored_model != running_model:
        notices.append(
            f"the declarations in {path} were made against decision model "
            f"{stored_model}; this build runs {running_model}. Every fact id in "
            f"the store is still defined, so they are applied, but a fact may "
            f"have been re-specified between the two models. Re-declare if the "
            f"assessment matters.")

    return {"facts": cleaned, "model_version": stored_model,
            "path": str(path), "notices": notices}


def save(path: Path, facts: Mapping[str, Any], model_version: str) -> Path:
    """Write a store, creating `.regula/` if needed. Overwrites by design.

    Merging silently would leave a user unable to correct an answer without
    editing JSON by hand, and a store whose history is invisible is worse for
    evidence than one that records the current declaration with its timestamp.
    Callers that want to keep earlier values read first and pass the merge.
    """
    path = Path(path)
    for fact_id, entry in facts.items():
        for value in entry.get("values", []):
            FactValue.from_dict(value, fact_id)
    payload = {
        "schema_version": SCHEMA_VERSION,
        "model_version": model_version,
        "written_at": now_iso(),
        "_note": (
            "Facts a person declared about this project. Regula establishes none "
            "of them; every value records who asserted it and in answer to what. "
            "A declared fact can move a decision from insufficient_information to "
            "an indication. It does not produce a risk tier, a compliance score, "
            "a readiness percentage or an effort estimate."
        ),
        "facts": {k: {"values": [dict(v) for v in e["values"]]} for k, e in facts.items()},
    }
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    except OSError as exc:
        raise FactStoreError(f"{path}: cannot write fact store ({exc})") from exc
    return path


def merge(*sources: Mapping[str, Any]) -> dict:
    """Later sources win per fact id; earlier values are replaced, not appended.

    Appending would let a stale `yes` and a fresh `no` sit in one fact, and the
    kernel would report a contradiction that the user never made.
    """
    merged: dict[str, dict] = {}
    for source in sources:
        for fact_id, entry in (source or {}).items():
            merged[fact_id] = {"values": [dict(v) for v in entry["values"]]}
    return merged


def describe(facts: Mapping[str, Any]) -> list[str]:
    """Human-readable provenance for every declared fact, one line each.

    This is the honesty half of the loop. A decision that moved because somebody
    said so must show that somebody said so, at the point the decision is shown.
    """
    lines = []
    for fact_id in sorted(facts):
        for value in facts[fact_id]["values"]:
            provenance = value.get("provenance", {})
            asked = provenance.get("question")
            lines.append(
                f"  - {fact_id} = {value['state']}"
                f"  [{provenance.get('source_type', '?')}"
                f" via {provenance.get('source_ref', '?')}"
                f" at {value.get('timestamp', '?')}]"
                + (f"\n      asked: {asked}" if asked else "")
            )
    return lines


def source_types(facts: Mapping[str, Any]) -> set:
    return {v.get("provenance", {}).get("source_type")
            for e in facts.values() for v in e["values"]}


def collect_cli_facts(raw_args: Iterable[str], jurisdiction: str,
                      model: Mapping[str, Any],
                      source_ref: str = "cli:check --fact") -> dict:
    """Turn `--fact id=state` arguments into a canonical fact map."""
    known = known_fact_ids(model)
    facts: dict[str, dict] = {}
    for raw in raw_args or ():
        fact_id, state = parse_fact_argument(raw)
        if fact_id not in known:
            catalogue_command = (
                "comply" if source_ref.startswith("cli:comply") else "check"
            )
            raise FactStoreError(
                f"--fact {fact_id!r} is not defined by decision model "
                f"{model.get('model_version')!r}. "
                f"Run `regula {catalogue_command} --list-facts` to see the ids "
                "this model uses.")
        facts[fact_id] = {"values": [build_value(
            state, jurisdiction, source_ref,
            source_type=SOURCE_USER_ATTESTATION,
            question=(model["fact_definitions"][fact_id].get("question")),
        )]}
    return facts


__all__ = [
    "FactStoreError",
    "SCHEMA_VERSION",
    "SOURCE_USER_ATTESTATION",
    "SOURCE_USER_DECLARATION",
    "STORE_RELATIVE_PATH",
    "build_value",
    "collect_cli_facts",
    "describe",
    "known_fact_ids",
    "load",
    "merge",
    "parse_fact_argument",
    "save",
    "source_types",
    "store_path",
]
