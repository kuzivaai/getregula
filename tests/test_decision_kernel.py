# regula-ignore
"""Contract tests for the versioned epistemic decision kernel."""

import copy
import random
import sys
from datetime import datetime
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from decision_kernel import (  # noqa: E402
    DecisionInputError,
    DecisionKernel,
    FactState,
    fact,
)
from run_decision_mutations import run_mutations  # noqa: E402


NOW = "2026-08-12T12:00:00+00:00"


def _value(state, jurisdiction, source_ref="test-observation"):
    return fact(state, source_ref, jurisdiction, NOW)


def _request(kernel, jurisdiction, facts):
    return {
        "model_version": kernel.model_version,
        "jurisdiction": jurisdiction,
        "facts": facts,
    }


def _relevant_fact_ids(kernel, jurisdiction):
    return [
        fact_id
        for fact_id, definition in kernel.model["fact_definitions"].items()
        if definition["jurisdiction"] in {"common", jurisdiction}
    ]


def _resolved_map(kernel, jurisdiction, default="no"):
    return {
        fact_id: _value(default, jurisdiction)
        for fact_id in _relevant_fact_ids(kernel, jurisdiction)
    }


def _eu_annex_iii_indication(kernel):
    facts = _resolved_map(kernel, "eu")
    facts.update({
        "jurisdiction_in_scope": _value("yes", "eu"),
        "is_ai_system": _value("yes", "eu"),
        "role_provider": _value("yes", "eu"),
        "eu_annex_iii_use": _value("yes", "eu"),
        "eu_significant_risk": _value("yes", "eu"),
    })
    return facts


def _obligation_ids(result):
    return {item["obligation_id"] for item in result.get("obligations", [])}


def _determinacy(result):
    return 0 if result["result_type"] == "insufficient_information" else 1


def test_fact_state_contract_and_model_version_are_explicit():
    kernel = DecisionKernel()
    assert {state.value for state in FactState} == {
        "yes", "no", "unknown", "not_applicable"
    }
    assert kernel.model["schema_version"] == "1.0"
    assert kernel.model_version == "2026-08-26.1"


@pytest.mark.parametrize("jurisdiction", ["eu", "kr", "co"])
def test_empty_input_is_insufficient_in_every_jurisdiction(jurisdiction):
    kernel = DecisionKernel()
    result = kernel.evaluate(_request(kernel, jurisdiction, {}))
    assert result["result_type"] == "insufficient_information"
    assert result["unresolved_predicates"]
    assert result["evidence_completeness"]["absent_fact_count"] > 0
    assert "indications" not in result
    assert "obligations" not in result


@pytest.mark.parametrize("jurisdiction", ["eu", "kr", "co"])
def test_all_explicit_unknown_is_distinct_from_absence(jurisdiction):
    kernel = DecisionKernel()
    facts = {
        fact_id: _value("unknown", jurisdiction)
        for fact_id in _relevant_fact_ids(kernel, jurisdiction)
    }
    result = kernel.evaluate(_request(kernel, jurisdiction, facts))
    completeness = result["evidence_completeness"]
    assert result["result_type"] == "insufficient_information"
    assert completeness["explicit_unknown_fact_count"] > 0
    assert completeness["absent_fact_count"] == 0
    assert all(item["reason"] == "explicit_unknown"
               for item in result["unresolved_predicates"])


@pytest.mark.parametrize("jurisdiction", ["eu", "kr", "co"])
def test_partial_input_lists_actionable_resolvable_facts_in_rank_order(jurisdiction):
    kernel = DecisionKernel()
    facts = {"jurisdiction_in_scope": _value("yes", jurisdiction)}
    result = kernel.evaluate(_request(kernel, jurisdiction, facts))
    assert result["result_type"] == "insufficient_information"
    rows = result["unresolved_predicates"]
    assert [(row["resolution_count"], row["fact_id"]) for row in rows] == sorted(
        ((row["resolution_count"], row["fact_id"]) for row in rows),
        key=lambda item: (-item[0], item[1]),
    )
    row = next(item for item in rows if item["fact_id"] == "is_ai_system")
    assert row["question"]
    assert row["would_resolve"] == [{
        "predicate_id": f"{jurisdiction}_scope",
        "provision": kernel.model["jurisdictions"][jurisdiction]["scope"]["provision"],
    }]


@pytest.mark.parametrize("jurisdiction", ["eu", "kr", "co"])
def test_contradictory_values_are_preserved_and_block_decision(jurisdiction):
    kernel = DecisionKernel()
    contradictory = _value("yes", jurisdiction, "source-a")
    contradictory["values"].extend(
        _value("no", jurisdiction, "source-b")["values"]
    )
    facts = {
        "jurisdiction_in_scope": contradictory,
        "is_ai_system": _value("yes", jurisdiction),
    }
    result = kernel.evaluate(_request(kernel, jurisdiction, facts))
    row = next(item for item in result["unresolved_predicates"]
               if item["fact_id"] == "jurisdiction_in_scope")
    assert result["result_type"] == "insufficient_information"
    assert row["reason"] == "contradictory"
    assert {item["state"] for item in row["observed_values"]} == {"yes", "no"}
    assert {item["provenance"]["source_ref"] for item in row["observed_values"]} == {
        "source-a", "source-b"
    }


@pytest.mark.parametrize(
    ("jurisdiction", "scope_fact_count"),
    [("eu", 2), ("kr", 3), ("co", 3)],
)
def test_not_applicable_is_resolved_but_does_not_mean_no(
        jurisdiction, scope_fact_count):
    kernel = DecisionKernel()
    facts = _resolved_map(kernel, jurisdiction, "not_applicable")
    result = kernel.evaluate(_request(kernel, jurisdiction, facts))
    assert result["result_type"] == "outside_scope_candidate"
    assert result["evidence_completeness"]["resolved_fact_count"] == scope_fact_count
    actual = result["outside_scope_basis"]["satisfied_false_path"]["children"][0]
    assert actual["actual"] == "not_applicable"
    assert actual["expected"] == "yes"


@pytest.mark.parametrize("jurisdiction", ["eu", "kr", "co"])
def test_resolved_outside_jurisdiction_scope_has_evidence(jurisdiction):
    kernel = DecisionKernel()
    facts = {
        "jurisdiction_in_scope": _value("no", jurisdiction),
        "is_ai_system": _value("yes", jurisdiction),
    }
    result = kernel.evaluate(_request(kernel, jurisdiction, facts))
    assert result["result_type"] == "outside_scope_candidate"
    assert result["rule_resolution"] == "resolved"
    assert result["outside_scope_basis"]["predicate_id"].endswith("_scope")
    assert result["matched_evidence"]


def test_not_ai_cannot_receive_eu_article_9_to_17_obligations():
    kernel = DecisionKernel()
    facts = _eu_annex_iii_indication(kernel)
    facts["is_ai_system"] = _value("no", "eu")
    result = kernel.evaluate(_request(kernel, "eu", facts))
    assert result["result_type"] == "outside_scope_candidate"
    assert "obligations" not in result


def test_eu_annex_iii_indication_has_trace_and_no_decision_probability():
    kernel = DecisionKernel()
    result = kernel.evaluate(
        _request(kernel, "eu", _eu_annex_iii_indication(kernel))
    )
    assert result["result_type"] == "indication"
    assert any(item["predicate_id"] == "eu_high_risk_annex_iii"
               for item in result["indications"])
    assert {f"eu_requirement_{article}" for article in range(9, 16)}.issubset(
        _obligation_ids(result)
    )
    assert "eu_provider_qms_17" in _obligation_ids(result)
    assert result["probability_calibration"]["available"] is False
    assert "confidence" not in result
    assert "confidence_score" not in result
    assert "readiness" not in result
    assert "effort" not in result
    for obligation in result["obligations"]:
        assert obligation["provision"]
        assert obligation["satisfied_predicate_path"]["state"] == "true"
        assert obligation["evidence_path"]
        assert obligation["applicable_from"] == "2027-12-02"


def test_eu_deployer_gets_article_26_not_provider_requirements():
    kernel = DecisionKernel()
    facts = _eu_annex_iii_indication(kernel)
    facts["role_provider"] = _value("no", "eu")
    facts["role_deployer"] = _value("yes", "eu")
    result = kernel.evaluate(_request(kernel, "eu", facts))
    obligation_ids = _obligation_ids(result)
    assert result["result_type"] == "indication"
    assert {
        "eu_deployer_use_and_oversight_26",
        "eu_deployer_monitor_26",
        "eu_deployer_cooperate_26",
    }.issubset(obligation_ids)
    assert not ({f"eu_requirement_{article}" for article in range(9, 16)}
                | {"eu_provider_qms_17"}) & obligation_ids


def test_article_50_1_public_crime_reporting_carve_back_is_modelled():
    kernel = DecisionKernel()
    facts = _resolved_map(kernel, "eu")
    facts.update({
        "jurisdiction_in_scope": _value("yes", "eu"),
        "is_ai_system": _value("yes", "eu"),
        "role_provider": _value("yes", "eu"),
        "eu_direct_interaction": _value("yes", "eu"),
        "eu_interaction_obvious": _value("no", "eu"),
        "eu_50_1_criminal_law_exception": _value("yes", "eu"),
        "eu_50_1_public_crime_reporting": _value("yes", "eu"),
    })
    result = kernel.evaluate(_request(kernel, "eu", facts))
    assert "eu_transparency_direct_interaction" in {
        item["predicate_id"] for item in result["indications"]
    }
    assert "eu_notice_50_1" in _obligation_ids(result)


def test_article_50_1_criminal_exception_excludes_non_public_system():
    kernel = DecisionKernel()
    facts = _resolved_map(kernel, "eu")
    facts.update({
        "jurisdiction_in_scope": _value("yes", "eu"),
        "is_ai_system": _value("yes", "eu"),
        "role_provider": _value("yes", "eu"),
        "eu_direct_interaction": _value("yes", "eu"),
        "eu_interaction_obvious": _value("no", "eu"),
        "eu_50_1_criminal_law_exception": _value("yes", "eu"),
        "eu_50_1_public_crime_reporting": _value("no", "eu"),
    })
    result = kernel.evaluate(_request(kernel, "eu", facts))
    assert "eu_transparency_direct_interaction" not in {
        item["predicate_id"] for item in result.get("indications", [])
    }
    assert "eu_notice_50_1" not in _obligation_ids(result)


@pytest.mark.parametrize(
    ("assignments", "excluded_obligation"),
    [
        ({
            "role_provider": "yes",
            "eu_generates_synthetic_content": "yes",
            "eu_standard_editing_assistance_only": "no",
            "eu_50_2_criminal_law_exception": "yes",
        }, "eu_marking_50_2"),
        ({
            "role_deployer": "yes",
            "eu_emotion_recognition": "yes",
            "eu_50_3_persons_exposed": "no",
            "eu_50_3_criminal_law_exception": "no",
        }, "eu_notice_50_3"),
        ({
            "role_deployer": "yes",
            "eu_biometric_categorisation": "yes",
            "eu_50_3_persons_exposed": "yes",
            "eu_50_3_criminal_law_exception": "yes",
        }, "eu_notice_50_3"),
        ({
            "role_deployer": "yes",
            "eu_deepfake_content": "yes",
            "eu_50_4_criminal_law_exception": "yes",
        }, "eu_disclosure_50_4_deepfake"),
        ({
            "role_deployer": "yes",
            "eu_public_interest_text": "yes",
            "eu_human_review_or_editorial_control": "no",
            "eu_50_4_criminal_law_exception": "yes",
        }, "eu_disclosure_50_4_text"),
    ],
)
def test_article_50_paragraph_specific_exclusions_are_modelled(
        assignments, excluded_obligation):
    kernel = DecisionKernel()
    facts = _resolved_map(kernel, "eu")
    facts.update({
        "jurisdiction_in_scope": _value("yes", "eu"),
        "is_ai_system": _value("yes", "eu"),
    })
    facts.update({
        fact_id: _value(state, "eu")
        for fact_id, state in assignments.items()
    })
    result = kernel.evaluate(_request(kernel, "eu", facts))
    assert excluded_obligation not in _obligation_ids(result)


@pytest.mark.parametrize(
    ("assignments", "expected_obligation"),
    [
        ({
            "role_provider": "yes",
            "eu_generates_synthetic_content": "yes",
            "eu_standard_editing_assistance_only": "no",
            "eu_50_2_criminal_law_exception": "no",
        }, "eu_marking_50_2"),
        ({
            "role_deployer": "yes",
            "eu_emotion_recognition": "yes",
            "eu_50_3_persons_exposed": "yes",
            "eu_50_3_criminal_law_exception": "no",
        }, "eu_notice_50_3"),
        ({
            "role_deployer": "yes",
            "eu_deepfake_content": "yes",
            "eu_50_4_criminal_law_exception": "no",
        }, "eu_disclosure_50_4_deepfake"),
        ({
            "role_deployer": "yes",
            "eu_public_interest_text": "yes",
            "eu_human_review_or_editorial_control": "no",
            "eu_50_4_criminal_law_exception": "no",
        }, "eu_disclosure_50_4_text"),
    ],
)
def test_article_50_positive_paths_emit_the_expected_obligation(
        assignments, expected_obligation):
    kernel = DecisionKernel()
    facts = _resolved_map(kernel, "eu")
    facts.update({
        "jurisdiction_in_scope": _value("yes", "eu"),
        "is_ai_system": _value("yes", "eu"),
    })
    facts.update({
        fact_id: _value(state, "eu")
        for fact_id, state in assignments.items()
    })
    result = kernel.evaluate(_request(kernel, "eu", facts))
    assert expected_obligation in _obligation_ids(result)


def test_korea_high_impact_indication_and_article_33_review():
    kernel = DecisionKernel()
    facts = _resolved_map(kernel, "kr")
    facts.update({
        "jurisdiction_in_scope": _value("yes", "kr"),
        "is_ai_system": _value("yes", "kr"),
        "kr_ai_business_operator": _value("yes", "kr"),
        "kr_provides_ai_product_or_service": _value("yes", "kr"),
        "kr_high_impact_area": _value("yes", "kr"),
        "kr_significant_impact_or_risk": _value("yes", "kr"),
    })
    result = kernel.evaluate(_request(kernel, "kr", facts))
    assert result["result_type"] == "indication"
    assert {"kr_advance_review", "kr_high_impact"}.issubset(
        {item["predicate_id"] for item in result["indications"]}
    )
    assert {"kr_review_33", "kr_risk_management_34"}.issubset(
        _obligation_ids(result)
    )
    assert all(item["applicable_from"] == "2026-01-22"
               for item in result["obligations"])


def test_korea_article_32_requires_all_three_decree_criteria():
    kernel = DecisionKernel()
    facts = _resolved_map(kernel, "kr")
    facts.update({
        "jurisdiction_in_scope": _value("yes", "kr"),
        "is_ai_system": _value("yes", "kr"),
        "kr_ai_business_operator": _value("yes", "kr"),
        "kr_provides_ai_product_or_service": _value("yes", "kr"),
        "kr_training_compute_threshold_met": _value("yes", "kr"),
    })
    without_other_criteria = kernel.evaluate(_request(kernel, "kr", facts))
    assert "kr_high_compute" not in {
        item["predicate_id"] for item in without_other_criteria["indications"]
    }

    facts.update({
        "kr_frontier_technology_configuration": _value("yes", "kr"),
        "kr_widespread_significant_impact_risk": _value("yes", "kr"),
    })
    with_all_criteria = kernel.evaluate(_request(kernel, "kr", facts))
    assert "kr_high_compute" in {
        item["predicate_id"] for item in with_all_criteria["indications"]
    }
    assert {"kr_safety_32_1", "kr_submit_32_2"}.issubset(
        _obligation_ids(with_all_criteria)
    )


@pytest.mark.parametrize("threshold_fact", [
    "kr_total_revenue_at_least_1trn_krw",
    "kr_ai_services_revenue_at_least_10bn_krw",
    "kr_average_daily_domestic_users_at_least_1m",
    "kr_article_43_1_3_administrative_fine",
])
def test_korea_domestic_agent_accepts_any_one_decree_threshold(threshold_fact):
    kernel = DecisionKernel()
    facts = _resolved_map(kernel, "kr")
    facts.update({
        "jurisdiction_in_scope": _value("yes", "kr"),
        "is_ai_system": _value("yes", "kr"),
        "kr_ai_business_operator": _value("yes", "kr"),
        "kr_foreign_operator": _value("yes", "kr"),
        threshold_fact: _value("yes", "kr"),
    })
    result = kernel.evaluate(_request(kernel, "kr", facts))
    assert "kr_domestic_agent" in {
        item["predicate_id"] for item in result["indications"]
    }
    assert "kr_agent_36" in _obligation_ids(result)


def test_colorado_covered_admt_indication_and_future_applicability():
    kernel = DecisionKernel()
    facts = _resolved_map(kernel, "co")
    facts.update({
        "jurisdiction_in_scope": _value("yes", "co"),
        "is_ai_system": _value("yes", "co"),
        "role_deployer": _value("yes", "co"),
        "co_doing_business": _value("yes", "co"),
        "co_processes_personal_data": _value("yes", "co"),
        "co_computational_output": _value("yes", "co"),
        "co_substantial_factor": _value("yes", "co"),
        "co_consequential_domain": _value("yes", "co"),
    })
    result = kernel.evaluate(_request(kernel, "co", facts))
    assert result["result_type"] == "indication"
    assert [item["predicate_id"] for item in result["indications"]] == [
        "co_covered_admt"
    ]
    assert {"co_deployer_records_1703", "co_notice_1704"}.issubset(
        _obligation_ids(result)
    )
    assert all(item["applicable_from"] == "2027-01-01"
               for item in result["obligations"])


def test_annex_i_section_b_does_not_inherit_articles_9_to_17():
    kernel = DecisionKernel()
    facts = _resolved_map(kernel, "eu")
    facts.update({
        "jurisdiction_in_scope": _value("yes", "eu"),
        "is_ai_system": _value("yes", "eu"),
        "role_provider": _value("yes", "eu"),
        "eu_annex_i_section_b_product": _value("yes", "eu"),
        "eu_safety_component": _value("yes", "eu"),
        "eu_third_party_assessment_required": _value("yes", "eu"),
    })
    result = kernel.evaluate(_request(kernel, "eu", facts))
    assert result["result_type"] == "indication"
    assert any(item["predicate_id"] == "eu_high_risk_annex_i_section_b_limited"
               for item in result["indications"])
    assert not ({f"eu_requirement_{article}" for article in range(9, 16)}
                | {"eu_provider_qms_17"}) & _obligation_ids(result)


def test_evidence_completeness_counts_only_considered_decision_facts():
    kernel = DecisionKernel()
    result = kernel.evaluate(_request(kernel, "eu", {}))
    assert result["evidence_completeness"] == {
        "considered_fact_count": 2,
        "resolved_fact_count": 0,
        "explicit_unknown_fact_count": 0,
        "contradictory_fact_count": 0,
        "absent_fact_count": 2,
    }


@pytest.mark.parametrize("jurisdiction", ["eu", "kr", "co"])
def test_generated_unknown_substitution_never_increases_determinacy_or_duties(
        jurisdiction):
    kernel = DecisionKernel()
    generator = random.Random(f"decision-kernel-{jurisdiction}-2026-08-12")
    fact_ids = _relevant_fact_ids(kernel, jurisdiction)
    for vector_number in range(256):
        facts = {
            fact_id: _value(generator.choice(("yes", "no", "not_applicable")),
                            jurisdiction, f"generated-{vector_number}")
            for fact_id in fact_ids
        }
        before = kernel.evaluate(_request(kernel, jurisdiction, facts))
        selected = generator.choice(fact_ids)
        substituted = copy.deepcopy(facts)
        substituted[selected] = _value(
            "unknown", jurisdiction, f"unknown-substitution-{vector_number}"
        )
        after = kernel.evaluate(_request(kernel, jurisdiction, substituted))
        assert _determinacy(after) <= _determinacy(before)
        assert _obligation_ids(after) <= _obligation_ids(before)


@pytest.mark.parametrize("jurisdiction", ["eu", "kr", "co"])
def test_invalid_input_is_rejected_in_every_jurisdiction(jurisdiction):
    kernel = DecisionKernel()
    invalid_requests = [
        {},
        {"model_version": kernel.model_version, "jurisdiction": jurisdiction,
         "facts": []},
        _request(kernel, jurisdiction, {"invented_fact": _value("yes", jurisdiction)}),
        _request(kernel, jurisdiction, {
            "jurisdiction_in_scope": _value("perhaps", jurisdiction)
        }),
        _request(kernel, jurisdiction, {
            "jurisdiction_in_scope": _value("yes", "wrong-jurisdiction")
        }),
    ]
    for request in invalid_requests:
        with pytest.raises(DecisionInputError):
            kernel.evaluate(request)


def test_timestamp_and_provenance_are_mandatory():
    kernel = DecisionKernel()
    valid = _value("yes", "eu")
    for field in ("timestamp", "provenance"):
        broken = copy.deepcopy(valid)
        del broken["values"][0][field]
        with pytest.raises(DecisionInputError):
            kernel.evaluate(_request(kernel, "eu", {
                "jurisdiction_in_scope": broken
            }))
    malformed = _value("yes", "eu")
    malformed["values"][0]["timestamp"] = "not-a-timestamp"
    with pytest.raises(DecisionInputError):
        kernel.evaluate(_request(kernel, "eu", {
            "jurisdiction_in_scope": malformed
        }))


def test_fact_timestamp_fixture_is_timezone_aware():
    assert datetime.fromisoformat(NOW).tzinfo is not None


def test_every_predicate_and_obligation_edge_mutant_is_killed():
    summary = run_mutations()
    assert summary["total_mutants"] == (
        summary["predicate_mutants"] + summary["obligation_edge_mutants"]
    )
    assert summary["reconciled"] is True
    assert summary["operator_set"] == [
        "invert each fact-state comparison",
        "remove each rule-to-obligation edge",
    ]
    assert summary["invalid_mutants"] == 0
    assert summary["timed_out_mutants"] == 0
    assert summary["equivalent_mutants"] == "not_assessed"
    assert summary["surviving_mutants"] == 0, summary["itemisation"]
    assert summary["killed_mutants"] == summary["total_mutants"]
