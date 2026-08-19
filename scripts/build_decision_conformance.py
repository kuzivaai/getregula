#!/usr/bin/env python3
"""Build the checked-in cross-runtime decision conformance corpus."""

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from decision_kernel import DecisionInputError, DecisionKernel, fact, load_model
from run_decision_mutations import (
    NOW,
    _assign,
    _fact_leaves,
    _leaf_witness,
    _obligation_assignments,
    _rule_edges,
)


ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = ROOT / "references" / "decision_model.v1.json"
TARGET = ROOT / "references" / "decision_conformance.v1.json"


def _relevant_facts(model, jurisdiction, state="no"):
    return {
        fact_id: fact(state, "conformance-default", jurisdiction, NOW)
        for fact_id, definition in model["fact_definitions"].items()
        if definition["jurisdiction"] in {"common", jurisdiction}
    }


def _request(model, jurisdiction, assignments=None, facts=None):
    if facts is None:
        facts = _relevant_facts(model, jurisdiction)
        for fact_id, state in (assignments or {}).items():
            facts[fact_id] = fact(
                state, "conformance-witness", jurisdiction, NOW
            )
    return {
        "model_version": model["model_version"],
        "jurisdiction": jurisdiction,
        "facts": facts,
    }


def _expected(kernel, request):
    try:
        return {"result": kernel.evaluate(request)}
    except DecisionInputError:
        return {"error": "DecisionInputError"}


def _add(vectors, kernel, vector_id, category, request):
    vectors.append({
        "id": vector_id,
        "category": category,
        "request": request,
        "expected": _expected(kernel, request),
    })


def build_corpus():
    model = load_model()
    kernel = DecisionKernel(model)
    vectors = []
    for jurisdiction, config in model["jurisdictions"].items():
        scope_true = _assign(config["scope"], True)
        _add(vectors, kernel, f"{jurisdiction}:empty", "empty",
             _request(model, jurisdiction, facts={}))
        unknown_facts = {
            fact_id: fact("unknown", "conformance-unknown", jurisdiction, NOW)
            for fact_id in _relevant_facts(model, jurisdiction)
        }
        _add(vectors, kernel, f"{jurisdiction}:all_unknown", "all_unknown",
             _request(model, jurisdiction, facts=unknown_facts))
        outside = _relevant_facts(model, jurisdiction)
        outside["jurisdiction_in_scope"] = fact(
            "no", "conformance-outside", jurisdiction, NOW
        )
        _add(vectors, kernel, f"{jurisdiction}:outside", "outside_scope",
             _request(model, jurisdiction, facts=outside))
        not_applicable = _relevant_facts(model, jurisdiction, "not_applicable")
        _add(vectors, kernel, f"{jurisdiction}:not_applicable", "not_applicable",
             _request(model, jurisdiction, facts=not_applicable))
        partial = {
            "jurisdiction_in_scope": fact(
                "yes", "conformance-partial", jurisdiction, NOW
            )
        }
        _add(vectors, kernel, f"{jurisdiction}:partial", "partial",
             _request(model, jurisdiction, facts=partial))
        contradictory = {
            "jurisdiction_in_scope": {
                "values": [
                    fact("yes", "conformance-a", jurisdiction, NOW)["values"][0],
                    fact("no", "conformance-b", jurisdiction, NOW)["values"][0],
                ]
            },
            "is_ai_system": fact(
                "yes", "conformance-ai", jurisdiction, NOW
            ),
        }
        _add(vectors, kernel, f"{jurisdiction}:contradictory", "contradictory",
             _request(model, jurisdiction, facts=contradictory))
        _add(vectors, kernel, f"{jurisdiction}:resolved_no_match", "no_rule_match",
             _request(model, jurisdiction, assignments=scope_true))

        for rule in config["rules"]:
            for path, leaf in _fact_leaves(rule):
                assignments = dict(scope_true)
                assignments.update(_leaf_witness(rule, path))
                path_text = ".".join(map(str, path)) or "root"
                _add(
                    vectors,
                    kernel,
                    f"{jurisdiction}:predicate:{rule['id']}:{leaf['fact']}:{path_text}",
                    "predicate_branch",
                    _request(model, jurisdiction, assignments=assignments),
                )

        rules_by_id = {rule["id"]: rule for rule in config["rules"]}
        for obligation in config["obligations"]:
            for path, target_rule in _rule_edges(obligation):
                assignments = dict(scope_true)
                assignments.update(_assign(rules_by_id[target_rule], True))
                assignments.update(_obligation_assignments(obligation))
                _add(
                    vectors,
                    kernel,
                    f"{jurisdiction}:edge:{obligation['id']}:{target_rule}",
                    "obligation_edge",
                    _request(model, jurisdiction, assignments=assignments),
                )

        invalid = _request(model, jurisdiction, facts={
            "jurisdiction_in_scope": fact(
                "yes", "conformance-invalid", jurisdiction, NOW
            )
        })
        invalid["facts"]["jurisdiction_in_scope"]["values"][0]["state"] = "perhaps"
        _add(vectors, kernel, f"{jurisdiction}:invalid_state", "invalid", invalid)

    categories = {}
    jurisdictions = {}
    for vector in vectors:
        categories[vector["category"]] = categories.get(vector["category"], 0) + 1
        jurisdiction = vector["request"].get("jurisdiction", "invalid")
        jurisdictions[jurisdiction] = jurisdictions.get(jurisdiction, 0) + 1
    source_bytes = MODEL_PATH.read_bytes()
    return {
        "schema_version": "1.0",
        "model_version": model["model_version"],
        "model_sha256": hashlib.sha256(source_bytes).hexdigest(),
        "generated_by": "scripts/build_decision_conformance.py",
        "counts": {
            "total": len(vectors),
            "by_category": dict(sorted(categories.items())),
            "by_jurisdiction": dict(sorted(jurisdictions.items())),
            "reconciled_by_category": sum(categories.values()) == len(vectors),
            "reconciled_by_jurisdiction": sum(jurisdictions.values()) == len(vectors),
        },
        "vectors": vectors,
    }


def render():
    return json.dumps(build_corpus(), indent=2, sort_keys=True) + "\n"


def main():
    TARGET.write_text(render(), encoding="utf-8")
    corpus = json.loads(TARGET.read_text(encoding="utf-8"))
    print(json.dumps(corpus["counts"], indent=2, sort_keys=True))
    print(f"wrote {TARGET.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
