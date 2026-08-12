#!/usr/bin/env python3
"""Versioned, evidence-aware regulatory decision kernel.

The kernel is deliberately independent of presentation adapters. It accepts
sourced facts, preserves conflicting values, evaluates named legal predicates,
and emits one of three semantic result variants. It does not emit confidence
probabilities, readiness percentages, or effort estimates.
"""

import json
import sys
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Set, Tuple

sys.path.insert(0, str(Path(__file__).parent))


MODEL_PATH = Path(__file__).parent.parent / "references" / "decision_model.v1.json"


class DecisionInputError(ValueError):
    """Raised when a decision request violates the input contract."""


class FactState(str, Enum):
    YES = "yes"
    NO = "no"
    UNKNOWN = "unknown"
    NOT_APPLICABLE = "not_applicable"


class PredicateState(str, Enum):
    TRUE = "true"
    FALSE = "false"
    UNRESOLVED = "unresolved"


@dataclass(frozen=True)
class FactValue:
    state: FactState
    provenance: Mapping[str, Any]
    jurisdiction: str
    timestamp: str

    @classmethod
    def from_dict(cls, value: Mapping[str, Any], fact_id: str) -> "FactValue":
        if not isinstance(value, Mapping):
            raise DecisionInputError(f"fact {fact_id!r} value must be an object")
        try:
            state = FactState(value.get("state"))
        except (TypeError, ValueError) as exc:
            allowed = ", ".join(item.value for item in FactState)
            raise DecisionInputError(
                f"fact {fact_id!r} state must be one of: {allowed}"
            ) from exc
        provenance = value.get("provenance")
        if not isinstance(provenance, Mapping) or not provenance:
            raise DecisionInputError(
                f"fact {fact_id!r} provenance must be a non-empty object"
            )
        source_type = provenance.get("source_type")
        source_ref = provenance.get("source_ref")
        if not isinstance(source_type, str) or not source_type.strip():
            raise DecisionInputError(
                f"fact {fact_id!r} provenance.source_type must be non-empty"
            )
        if not isinstance(source_ref, str) or not source_ref.strip():
            raise DecisionInputError(
                f"fact {fact_id!r} provenance.source_ref must be non-empty"
            )
        jurisdiction = value.get("jurisdiction")
        if not isinstance(jurisdiction, str) or not jurisdiction:
            raise DecisionInputError(
                f"fact {fact_id!r} jurisdiction must be non-empty"
            )
        timestamp = value.get("timestamp")
        if not isinstance(timestamp, str):
            raise DecisionInputError(f"fact {fact_id!r} timestamp must be a string")
        try:
            parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except ValueError as exc:
            raise DecisionInputError(
                f"fact {fact_id!r} timestamp must be ISO 8601"
            ) from exc
        if parsed.tzinfo is None:
            raise DecisionInputError(
                f"fact {fact_id!r} timestamp must include a UTC offset"
            )
        return cls(state, dict(provenance), jurisdiction, timestamp)

    def to_dict(self) -> dict:
        return {
            "state": self.state.value,
            "provenance": dict(self.provenance),
            "jurisdiction": self.jurisdiction,
            "timestamp": self.timestamp,
        }


@dataclass(frozen=True)
class FactResolution:
    fact_id: str
    status: str
    state: Optional[FactState]
    values: Tuple[FactValue, ...]

    def to_dict(self) -> dict:
        return {
            "fact_id": self.fact_id,
            "status": self.status,
            "state": self.state.value if self.state else None,
            "values": [value.to_dict() for value in self.values],
        }


@dataclass(frozen=True)
class ExpressionResult:
    state: PredicateState
    trace: Mapping[str, Any]
    fact_ids: frozenset
    unresolved: frozenset


def load_model(path: Path = MODEL_PATH) -> dict:
    try:
        model = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise DecisionInputError(f"cannot load decision model: {exc}") from exc
    _validate_model(model)
    return model


def _validate_model(model: Mapping[str, Any]) -> None:
    if model.get("schema_version") != "1.0":
        raise DecisionInputError("unsupported decision model schema_version")
    if not isinstance(model.get("model_version"), str):
        raise DecisionInputError("decision model has no model_version")
    facts = model.get("fact_definitions")
    jurisdictions = model.get("jurisdictions")
    if not isinstance(facts, Mapping) or not isinstance(jurisdictions, Mapping):
        raise DecisionInputError("decision model facts and jurisdictions must be objects")
    for jurisdiction, config in jurisdictions.items():
        if not isinstance(config, Mapping):
            raise DecisionInputError(f"jurisdiction {jurisdiction!r} must be an object")
        rules = config.get("rules")
        obligations = config.get("obligations")
        if not isinstance(rules, list) or not isinstance(obligations, list):
            raise DecisionInputError(
                f"jurisdiction {jurisdiction!r} rules and obligations must be arrays"
            )
        rule_ids = {rule.get("id") for rule in rules if isinstance(rule, Mapping)}
        if len(rule_ids) != len(rules) or None in rule_ids:
            raise DecisionInputError(
                f"jurisdiction {jurisdiction!r} has missing or duplicate rule ids"
            )
        for expression in [config.get("scope"), *rules, *obligations]:
            _validate_expression_references(expression, facts, rule_ids)


def _validate_expression_references(expression, fact_definitions, rule_ids):
    if not isinstance(expression, Mapping):
        raise DecisionInputError("predicate expression must be an object")
    if "fact" in expression:
        if expression["fact"] not in fact_definitions:
            raise DecisionInputError(f"unknown model fact {expression['fact']!r}")
        if expression.get("is") not in {item.value for item in FactState}:
            raise DecisionInputError(
                f"fact predicate {expression['fact']!r} has invalid expected state"
            )
    for operator in ("all", "any"):
        if operator in expression:
            children = expression[operator]
            if not isinstance(children, list) or not children:
                raise DecisionInputError(f"predicate operator {operator!r} must be non-empty")
            for child in children:
                _validate_expression_references(child, fact_definitions, rule_ids)
    for key in ("rule_any", "when_rule_any"):
        if key in expression:
            referenced = expression[key]
            if not isinstance(referenced, list) or not referenced:
                raise DecisionInputError(f"{key} must be a non-empty array")
            unknown = set(referenced) - set(rule_ids)
            if unknown:
                raise DecisionInputError(f"unknown rule references: {sorted(unknown)}")


class DecisionKernel:
    def __init__(self, model: Optional[Mapping[str, Any]] = None):
        self.model = dict(model) if model is not None else load_model()
        _validate_model(self.model)

    @property
    def model_version(self) -> str:
        return self.model["model_version"]

    def evaluate(self, request: Mapping[str, Any]) -> dict:
        jurisdiction, resolutions = self._parse_request(request)
        config = self.model["jurisdictions"][jurisdiction]

        scope = self._evaluate_expression(config["scope"], resolutions, {})
        scope_trace = self._named_trace(config["scope"], scope)
        if scope.state == PredicateState.FALSE:
            return self._base_result(
                "outside_scope_candidate",
                jurisdiction,
                resolutions,
                rule_resolution="resolved",
                decision_trace=[scope_trace],
                matched_evidence=self._matched_evidence(scope.fact_ids, resolutions),
                outside_scope_basis={
                    "predicate_id": config["scope"]["id"],
                    "provision": config["scope"]["provision"],
                    "satisfied_false_path": scope.trace,
                },
            )
        if scope.state == PredicateState.UNRESOLVED:
            return self._insufficient_result(
                jurisdiction,
                resolutions,
                [scope_trace],
                [(fact_id, config["scope"]["id"], config["scope"]["provision"])
                 for fact_id in scope.unresolved],
            )

        rule_results = {}
        rule_traces = []
        for rule in config["rules"]:
            result = self._evaluate_expression(rule, resolutions, rule_results)
            rule_results[rule["id"]] = result
            rule_traces.append(self._named_trace(rule, result))

        matched_rules = [
            rule for rule in config["rules"]
            if rule_results[rule["id"]].state == PredicateState.TRUE
        ]
        if not matched_rules:
            unresolved = []
            for rule in config["rules"]:
                result = rule_results[rule["id"]]
                for fact_id in result.unresolved:
                    unresolved.append((fact_id, rule["id"], rule["provision"]))
            if unresolved:
                return self._insufficient_result(
                    jurisdiction,
                    resolutions,
                    [scope_trace, *rule_traces],
                    unresolved,
                )
            all_fact_ids = set(scope.fact_ids)
            for result in rule_results.values():
                all_fact_ids.update(result.fact_ids)
            return self._base_result(
                "outside_scope_candidate",
                jurisdiction,
                resolutions,
                rule_resolution="resolved",
                decision_trace=[scope_trace, *rule_traces],
                matched_evidence=self._matched_evidence(all_fact_ids, resolutions),
                outside_scope_basis={
                    "predicate_id": "no_traced_rule_matched",
                    "provision": "All named predicates for the selected jurisdiction",
                    "satisfied_false_path": [
                        trace for trace in rule_traces
                        if trace["state"] == PredicateState.FALSE.value
                    ],
                },
            )

        obligation_results = []
        obligations = []
        unresolved = []
        for rule in config["rules"]:
            result = rule_results[rule["id"]]
            if result.state == PredicateState.UNRESOLVED:
                for fact_id in result.unresolved:
                    unresolved.append((fact_id, rule["id"], rule["provision"]))
        for obligation in config["obligations"]:
            result = self._evaluate_expression(obligation, resolutions, rule_results)
            trace = self._named_trace(obligation, result)
            obligation_results.append(trace)
            if result.state == PredicateState.TRUE:
                applicability_by_rule = {
                    rule_id: date
                    for rule_id, date in obligation.get(
                        "applicability_by_rule", {}
                    ).items()
                    if rule_results[rule_id].state == PredicateState.TRUE
                }
                matched_dates = sorted(set(applicability_by_rule.values()))
                applicable_from = obligation.get("applicable_from")
                if applicable_from is None and len(matched_dates) == 1:
                    applicable_from = matched_dates[0]
                if applicable_from is None and not applicability_by_rule:
                    applicable_from = config.get("default_applicable_from")
                obligations.append({
                    "obligation_id": obligation["id"],
                    "name": obligation["name"],
                    "provision": obligation["provision"],
                    "applicable_from": applicable_from,
                    "applicability_by_rule": applicability_by_rule,
                    "applicability_note": obligation.get("applicability_note"),
                    "satisfied_predicate_path": result.trace,
                    "evidence_path": self._matched_evidence(
                        result.fact_ids, resolutions),
                })
            elif result.state == PredicateState.UNRESOLVED:
                for fact_id in result.unresolved:
                    unresolved.append(
                        (fact_id, obligation["id"], obligation["provision"])
                    )

        matched_fact_ids = set(scope.fact_ids)
        for rule in matched_rules:
            matched_fact_ids.update(rule_results[rule["id"]].fact_ids)
        indications = [{
            "predicate_id": rule["id"],
            "classification": rule["classification"],
            "provision": rule["provision"],
            "applicable_from": rule.get(
                "applicable_from", config.get("default_applicable_from")
            ),
            "applicability_note": rule.get("applicability_note"),
            "satisfied_predicate_path": rule_results[rule["id"]].trace,
        } for rule in matched_rules]
        return self._base_result(
            "indication",
            jurisdiction,
            resolutions,
            rule_resolution="partial" if unresolved else "resolved",
            decision_trace=[scope_trace, *rule_traces, *obligation_results],
            matched_evidence=self._matched_evidence(matched_fact_ids, resolutions),
            indications=indications,
            obligations=obligations,
            unresolved_predicates=self._rank_unresolved(unresolved, resolutions),
        )

    def _parse_request(self, request):
        if not isinstance(request, Mapping):
            raise DecisionInputError("decision request must be an object")
        version = request.get("model_version")
        if version != self.model_version:
            raise DecisionInputError(
                f"model_version must be {self.model_version!r}, got {version!r}"
            )
        jurisdiction = request.get("jurisdiction")
        if jurisdiction not in self.model["jurisdictions"]:
            allowed = ", ".join(sorted(self.model["jurisdictions"]))
            raise DecisionInputError(f"jurisdiction must be one of: {allowed}")
        supplied = request.get("facts")
        if not isinstance(supplied, Mapping):
            raise DecisionInputError("facts must be an object keyed by fact id")
        unknown = set(supplied) - set(self.model["fact_definitions"])
        if unknown:
            raise DecisionInputError(f"unknown fact ids: {sorted(unknown)}")

        resolutions = {}
        for fact_id in self.model["fact_definitions"]:
            raw = supplied.get(fact_id)
            if raw is None:
                resolutions[fact_id] = FactResolution(
                    fact_id, "absent", None, tuple())
                continue
            if not isinstance(raw, Mapping) or not isinstance(raw.get("values"), list):
                raise DecisionInputError(
                    f"fact {fact_id!r} must be an object with a values array"
                )
            if not raw["values"]:
                raise DecisionInputError(f"fact {fact_id!r} values must not be empty")
            values = tuple(
                FactValue.from_dict(item, fact_id) for item in raw["values"]
            )
            for value in values:
                definition_jurisdiction = self.model["fact_definitions"][fact_id][
                    "jurisdiction"
                ]
                allowed_jurisdictions = {"common", jurisdiction}
                if definition_jurisdiction not in allowed_jurisdictions:
                    raise DecisionInputError(
                        f"fact {fact_id!r} does not belong to jurisdiction {jurisdiction!r}"
                    )
                if value.jurisdiction not in allowed_jurisdictions:
                    raise DecisionInputError(
                        f"fact {fact_id!r} value jurisdiction {value.jurisdiction!r} "
                        f"does not match request {jurisdiction!r}"
                    )
            resolutions[fact_id] = self._resolve_fact(fact_id, values)
        return jurisdiction, resolutions

    @staticmethod
    def _resolve_fact(fact_id, values):
        decisive = {value.state for value in values if value.state != FactState.UNKNOWN}
        if len(decisive) > 1:
            return FactResolution(fact_id, "contradictory", None, values)
        if not decisive:
            return FactResolution(fact_id, "explicit_unknown", None, values)
        return FactResolution(fact_id, "resolved", next(iter(decisive)), values)

    def _evaluate_expression(self, expression, resolutions, rule_results):
        if "fact" in expression:
            fact_id = expression["fact"]
            resolution = resolutions[fact_id]
            expected = FactState(expression["is"])
            if resolution.state is None:
                state = PredicateState.UNRESOLVED
                unresolved = frozenset({fact_id})
            else:
                state = (PredicateState.TRUE if resolution.state == expected
                         else PredicateState.FALSE)
                unresolved = frozenset()
            return ExpressionResult(
                state,
                {
                    "fact": fact_id,
                    "expected": expected.value,
                    "actual": resolution.state.value if resolution.state else None,
                    "fact_status": resolution.status,
                    "state": state.value,
                },
                frozenset({fact_id}),
                unresolved,
            )
        for key in ("rule_any", "when_rule_any"):
            if key in expression:
                children = []
                for rule_id in expression[key]:
                    result = rule_results[rule_id]
                    children.append(ExpressionResult(
                        result.state,
                        {"rule": rule_id, "state": result.state.value},
                        result.fact_ids,
                        result.unresolved,
                    ))
                return self._combine("any", children)
        for operator in ("all", "any"):
            if operator in expression:
                children = [
                    self._evaluate_expression(child, resolutions, rule_results)
                    for child in expression[operator]
                ]
                return self._combine(operator, children)
        raise DecisionInputError("predicate expression has no supported operator")

    @staticmethod
    def _combine(operator, children):
        if operator == "all":
            if any(child.state == PredicateState.FALSE for child in children):
                state = PredicateState.FALSE
            elif any(child.state == PredicateState.UNRESOLVED for child in children):
                state = PredicateState.UNRESOLVED
            else:
                state = PredicateState.TRUE
        else:
            if any(child.state == PredicateState.TRUE for child in children):
                state = PredicateState.TRUE
            elif any(child.state == PredicateState.UNRESOLVED for child in children):
                state = PredicateState.UNRESOLVED
            else:
                state = PredicateState.FALSE
        fact_ids = frozenset().union(*(child.fact_ids for child in children))
        unresolved = frozenset().union(*(child.unresolved for child in children))
        return ExpressionResult(
            state,
            {
                "operator": operator,
                "state": state.value,
                "children": [child.trace for child in children],
            },
            fact_ids,
            unresolved if state == PredicateState.UNRESOLVED else frozenset(),
        )

    @staticmethod
    def _named_trace(config, result):
        return {
            "predicate_id": config["id"],
            "provision": config["provision"],
            "state": result.state.value,
            "trace": result.trace,
        }

    def _base_result(
            self, result_type, jurisdiction, resolutions, rule_resolution,
            decision_trace, matched_evidence, **payload):
        considered_fact_ids = set()
        for trace in decision_trace:
            considered_fact_ids.update(_trace_fact_ids(trace))
        considered = [resolutions[fact_id] for fact_id in considered_fact_ids]
        resolved = sum(1 for item in considered if item.state is not None)
        explicit_unknown = sum(
            1 for item in considered if item.status == "explicit_unknown")
        contradictory = sum(
            1 for item in considered if item.status == "contradictory")
        absent = sum(1 for item in considered if item.status == "absent")
        result = {
            "result_type": result_type,
            "schema_version": "1.0",
            "model_version": self.model_version,
            "jurisdiction": jurisdiction,
            "evidence_completeness": {
                "considered_fact_count": len(considered),
                "resolved_fact_count": resolved,
                "explicit_unknown_fact_count": explicit_unknown,
                "contradictory_fact_count": contradictory,
                "absent_fact_count": absent,
            },
            "rule_resolution": rule_resolution,
            "matched_evidence": matched_evidence,
            "decision_trace": decision_trace,
            "probability_calibration": {
                "available": False,
                "condition": (
                    "Representative labelled outcomes are required before a "
                    "correctness probability can be calibrated."
                ),
            },
        }
        result.update(payload)
        return result

    def _insufficient_result(self, jurisdiction, resolutions, traces, unresolved):
        fact_ids = set()
        for trace in traces:
            fact_ids.update(_trace_fact_ids(trace))
        return self._base_result(
            "insufficient_information",
            jurisdiction,
            resolutions,
            rule_resolution="unresolved",
            decision_trace=traces,
            matched_evidence=self._matched_evidence(fact_ids, resolutions),
            unresolved_predicates=self._rank_unresolved(unresolved, resolutions),
        )

    def _rank_unresolved(self, unresolved, resolutions):
        impacts: Dict[str, Set[Tuple[str, str]]] = {}
        for fact_id, predicate_id, provision in unresolved:
            impacts.setdefault(fact_id, set()).add((predicate_id, provision))
        rows = []
        for fact_id, affected in impacts.items():
            definition = self.model["fact_definitions"][fact_id]
            resolution = resolutions[fact_id]
            rows.append({
                "fact_id": fact_id,
                "reason": resolution.status,
                "question": definition["question"],
                "would_resolve": [
                    {"predicate_id": predicate, "provision": provision}
                    for predicate, provision in sorted(affected)
                ],
                "resolution_count": len(affected),
                "observed_values": [value.to_dict() for value in resolution.values],
            })
        rows.sort(key=lambda item: (-item["resolution_count"], item["fact_id"]))
        return rows

    @staticmethod
    def _matched_evidence(fact_ids: Iterable[str], resolutions):
        rows = []
        for fact_id in sorted(set(fact_ids)):
            resolution = resolutions[fact_id]
            if resolution.state is not None:
                rows.append(resolution.to_dict())
        return rows


def _trace_fact_ids(value):
    result = set()
    if isinstance(value, Mapping):
        if isinstance(value.get("fact"), str):
            result.add(value["fact"])
        for child in value.values():
            result.update(_trace_fact_ids(child))
    elif isinstance(value, list):
        for child in value:
            result.update(_trace_fact_ids(child))
    return result


def fact(
        state: str, source_ref: str, jurisdiction: str, timestamp: str,
        source_type: str = "user_attestation", **provenance) -> dict:
    """Build one fact value using the public request shape."""
    source = {
        "source_type": source_type,
        "source_ref": source_ref,
        **provenance,
    }
    return {
        "values": [{
            "state": state,
            "provenance": source,
            "jurisdiction": jurisdiction,
            "timestamp": timestamp,
        }]
    }


def evaluate_decision(request: Mapping[str, Any]) -> dict:
    """Evaluate a request with the repository's canonical model."""
    return DecisionKernel().evaluate(request)


__all__ = [
    "DecisionInputError",
    "DecisionKernel",
    "FactState",
    "PredicateState",
    "evaluate_decision",
    "fact",
    "load_model",
]
