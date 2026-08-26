#!/usr/bin/env python3
"""Deterministic mutation controls for every decision-model rule and edge."""

import copy
import json
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from decision_kernel import (  # noqa: E402
    DecisionKernel,
    ExpressionResult,
    PredicateState,
    fact,
    load_model,
)


NOW = "2026-08-12T12:00:00+00:00"


@dataclass(frozen=True)
class MutationOutcome:
    mutation_id: str
    kind: str
    killed: bool
    canonical_state: str
    mutant_state: str

    def to_dict(self):
        return {
            "mutation_id": self.mutation_id,
            "kind": self.kind,
            "killed": self.killed,
            "canonical_state": self.canonical_state,
            "mutant_state": self.mutant_state,
        }


def _fact_leaves(expression, path=()):
    if "fact" in expression:
        yield path, expression
    for operator in ("all", "any"):
        for index, child in enumerate(expression.get(operator, [])):
            yield from _fact_leaves(child, path + (operator, index))


def _rule_edges(expression, path=()):
    for key in ("rule_any", "when_rule_any"):
        for index, rule_id in enumerate(expression.get(key, [])):
            yield path + (key, index), rule_id
    for operator in ("all", "any"):
        for index, child in enumerate(expression.get(operator, [])):
            yield from _rule_edges(child, path + (operator, index))


def _opposite(state):
    return "no" if state == "yes" else "yes"


def _merge(target, additions):
    for fact_id, state in additions.items():
        existing = target.get(fact_id)
        if existing is not None and existing != state:
            raise AssertionError(
                f"cannot synthesize witness: {fact_id} needs {existing} and {state}"
            )
        target[fact_id] = state


def _assign(expression, desired):
    if "fact" in expression:
        expected = expression["is"]
        return {expression["fact"]: expected if desired else _opposite(expected)}
    if "all" in expression:
        if desired:
            result = {}
            for child in expression["all"]:
                _merge(result, _assign(child, True))
            return result
        return _assign(expression["all"][0], False)
    if "any" in expression:
        if desired:
            return _assign(expression["any"][0], True)
        result = {}
        for child in expression["any"]:
            _merge(result, _assign(child, False))
        return result
    if "rule_any" in expression or "when_rule_any" in expression:
        return {}
    raise AssertionError("unsupported expression in witness generator")


def _leaf_witness(expression, target_path):
    if not target_path:
        return _assign(expression, True)
    operator, index, *rest = target_path
    result = _leaf_witness(expression[operator][index], tuple(rest))
    for sibling_index, sibling in enumerate(expression[operator]):
        if sibling_index == index:
            continue
        _merge(result, _assign(sibling, operator == "all"))
    return result


def _expression_at(expression, path):
    current = expression
    for offset in range(0, len(path), 2):
        current = current[path[offset]][path[offset + 1]]
    return current


def _resolutions(kernel, jurisdiction, assignments):
    request = {
        "model_version": kernel.model_version,
        "jurisdiction": jurisdiction,
        "facts": {
            fact_id: fact(state, "mutation-witness", jurisdiction, NOW)
            for fact_id, state in assignments.items()
        },
    }
    return kernel._parse_request(request)[1]


def _rule_result(kernel, jurisdiction, expression, assignments):
    resolutions = _resolutions(kernel, jurisdiction, assignments)
    return kernel._evaluate_expression(expression, resolutions, {})


def _predicate_mutations(model):
    outcomes = []
    for jurisdiction, config in model["jurisdictions"].items():
        canonical_kernel = DecisionKernel(model)
        for rule in config["rules"]:
            for path, leaf in _fact_leaves(rule):
                assignments = _leaf_witness(rule, path)
                canonical = _rule_result(
                    canonical_kernel, jurisdiction, rule, assignments
                )
                mutant_rule = copy.deepcopy(rule)
                mutant_leaf = _expression_at(mutant_rule, path)
                mutant_leaf["is"] = _opposite(mutant_leaf["is"])
                mutant = _rule_result(
                    canonical_kernel, jurisdiction, mutant_rule, assignments
                )
                mutation_id = (
                    f"{jurisdiction}:{rule['id']}:"
                    f"{leaf['fact']}:{'/'.join(map(str, path)) or 'root'}"
                )
                outcomes.append(MutationOutcome(
                    mutation_id,
                    "predicate_fact_comparison",
                    canonical.state == PredicateState.TRUE
                    and mutant.state != PredicateState.TRUE,
                    canonical.state.value,
                    mutant.state.value,
                ))
    return outcomes


def _fake_rule_results(config, target_rule):
    return {
        rule["id"]: ExpressionResult(
            PredicateState.TRUE if rule["id"] == target_rule else PredicateState.FALSE,
            {"rule": rule["id"]},
            frozenset(),
            frozenset(),
        )
        for rule in config["rules"]
    }


def _obligation_assignments(expression):
    if "fact" in expression:
        return {expression["fact"]: expression["is"]}
    result = {}
    for operator in ("all", "any"):
        for child in expression.get(operator, []):
            if "rule_any" in child or "when_rule_any" in child:
                continue
            _merge(result, _obligation_assignments(child))
    return result


def _remove_edge(expression, path):
    current = expression
    for offset in range(0, len(path) - 2, 2):
        current = current[path[offset]][path[offset + 1]]
    key, index = path[-2:]
    current[key].pop(index)


def _obligation_edge_mutations(model):
    outcomes = []
    for jurisdiction, config in model["jurisdictions"].items():
        canonical_kernel = DecisionKernel(model)
        for obligation in config["obligations"]:
            assignments = _obligation_assignments(obligation)
            resolutions = _resolutions(canonical_kernel, jurisdiction, assignments)
            for path, target_rule in _rule_edges(obligation):
                rule_results = _fake_rule_results(config, target_rule)
                canonical = canonical_kernel._evaluate_expression(
                    obligation, resolutions, rule_results
                )
                mutant_obligation = copy.deepcopy(obligation)
                _remove_edge(mutant_obligation, path)
                try:
                    mutant = canonical_kernel._evaluate_expression(
                        mutant_obligation, resolutions, rule_results
                    )
                    mutant_state = mutant.state.value
                except Exception as exc:
                    mutant_state = f"rejected:{type(exc).__name__}"
                mutation_id = (
                    f"{jurisdiction}:{obligation['id']}:{target_rule}:"
                    f"{'/'.join(map(str, path))}"
                )
                outcomes.append(MutationOutcome(
                    mutation_id,
                    "obligation_rule_edge",
                    canonical.state == PredicateState.TRUE
                    and mutant_state != PredicateState.TRUE.value,
                    canonical.state.value,
                    mutant_state,
                ))
    return outcomes


def run_mutations():
    model = load_model()
    outcomes = [*_predicate_mutations(model), *_obligation_edge_mutations(model)]
    survivors = [outcome for outcome in outcomes if not outcome.killed]
    itemisation = [outcome.to_dict() for outcome in outcomes]
    summary = {
        "model_version": model["model_version"],
        "predicate_mutants": sum(
            outcome.kind == "predicate_fact_comparison" for outcome in outcomes
        ),
        "obligation_edge_mutants": sum(
            outcome.kind == "obligation_rule_edge" for outcome in outcomes
        ),
        "total_mutants": len(outcomes),
        "killed_mutants": sum(outcome.killed for outcome in outcomes),
        "surviving_mutants": len(survivors),
        "reconciled": len(itemisation) == len(outcomes),
        "itemisation": itemisation,
    }
    return summary


def main():
    summary = run_mutations()
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 1 if summary["surviving_mutants"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
