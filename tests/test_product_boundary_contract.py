"""Cross-renderer contract for Regula's evidence-preparation boundary."""

from __future__ import annotations

import sys
import tempfile
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))


def _finding(tier: str = "high_risk") -> dict:
    return {
        "file": "app.py",
        "line": 7,
        "tier": tier,
        "category": "employment_decision",
        "description": "A hiring-related code pattern was found",
        "articles": ["6", "Annex III(4)"],
        "confidence_score": 80,
        "suppressed": False,
        "observations": [],
        "indicators": ["employment"],
    }


def test_review_record_preserves_unknowns_and_empty_human_decision():
    from evidence_review import review_record_from_finding

    record = review_record_from_finding(_finding())

    assert record["schema_version"] == "1.0"
    assert record["record_type"] == "reviewable_evidence"
    assert record["observation"] == "A hiring-related code pattern was found"
    assert record["source_location"] == {"path": "app.py", "line": 7}
    assert record["indicator"] == "employment_decision"
    assert record["declared_context"] == []
    assert record["contradictory_context"] == []
    assert record["missing_context"]
    assert record["reviewer_questions"]
    assert record["suggested_human_review_steps"]
    assert record["explicit_limitations"]
    assert record["human_decision"] is None
    assert all(
        reference["status"] == "potentially_relevant"
        for reference in record["source_references"]
    )


def test_public_context_evaluation_never_emits_a_legal_decision():
    from decision_adapters import evaluate_payload
    from decision_kernel import DecisionKernel, fact

    kernel = DecisionKernel()
    timestamp = "2026-08-30T12:00:00+00:00"
    relevant = {
        fact_id
        for fact_id, definition in kernel.model["fact_definitions"].items()
        if definition["jurisdiction"] in {"common", "eu"}
    }
    facts = {
        fact_id: fact("no", "test:declared-context", "eu", timestamp)
        for fact_id in relevant
    }
    for fact_id in (
        "jurisdiction_in_scope",
        "is_ai_system",
        "role_provider",
        "eu_annex_iii_use",
        "eu_significant_risk",
    ):
        facts[fact_id] = fact(
            "yes", "test:declared-context", "eu", timestamp
        )

    result = evaluate_payload({"jurisdiction": "eu", "facts": facts})

    assert result["schema_version"] == "2.0"
    assert result["review_status"] == "human_review_required"
    assert result["human_decision"] is None
    assert result["potentially_relevant_provisions"]
    assert result["declared_context"]
    assert result["explicit_limitations"]
    assert not ({
        "result_type",
        "obligations",
        "indications",
        "outside_scope_basis",
        "decision_trace",
        "rule_resolution",
    } & set(result))


def test_html_report_is_evidence_preparation_not_a_legal_result():
    from report import generate_html_report

    html = generate_html_report([_finding()], "test-project")

    assert "Regula Evidence-Preparation Report" in html
    assert "Human review required" in html
    assert "Code-observable indicator" in html
    assert "will be subject to mandatory obligations" not in html
    assert "EU AI Act Compliance Report" not in html
    assert "HIGH-RISK AI SYSTEM" not in html


def test_pdf_html_report_uses_the_same_product_boundary():
    from pdf_export import generate_compliance_html_report

    html = generate_compliance_html_report([_finding()], "test-project")

    assert "Regula Evidence-Preparation Report" in html
    assert "Human review required" in html
    assert "Potentially relevant provision" in html
    assert "EU AI Act Compliance Report" not in html
    assert "HIGH-RISK AI SYSTEM" not in html
    assert "Full obligations under Articles" not in html


def test_generated_model_and_governance_scaffolds_do_not_classify():
    from generate_documentation import generate_ai_governance, generate_model_card

    findings = {
        "highest_risk": "high_risk",
        "classifications": [{"indicators": ["employment"]}],
        "ai_files": ["app.py"],
        "model_files": [],
    }
    with tempfile.TemporaryDirectory() as project:
        Path(project, "app.py").write_text("def review_candidate(): pass\n", encoding="utf-8")
        model_card = generate_model_card(findings, "test-project", project)
        governance = generate_ai_governance(findings, "test-project", project)

    combined = model_card + governance
    assert "Code-observation class" in combined
    assert "Human review required" in combined
    assert "EU AI Act Risk Classification" not in combined
    assert "**Risk Classification:**" not in combined
    assert "Articles 9-15 apply" not in combined
    assert "Article 50 transparency requirements apply" not in combined


def test_sarif_and_shareable_summary_are_review_evidence_not_compliance_results():
    from report import generate_sales_report, generate_sarif

    sarif = generate_sarif([_finding()], "test-project")
    serialised = json.dumps(sarif)
    summary = generate_sales_report([_finding()], "test-project")

    assert "Transparency obligation applies" not in serialised
    assert '"compliance"' not in serialised
    assert sarif["runs"][0]["results"][0]["properties"][
        "reviewable_evidence"
    ]["human_decision"] is None
    assert "Evidence-Preparation Summary" in summary
    assert "Human review required" in summary
    assert "Compliance Summary" not in summary
    assert "Transparency Obligations Apply" not in summary


def test_questionnaire_output_preserves_answers_without_a_legal_result():
    from questionnaire import evaluate_questionnaire

    result = evaluate_questionnaire({
        "deployment_eu": "yes",
        "is_ai_system": "yes",
    })

    assert result["schema_version"] == "2.0"
    assert result["review_status"] == "insufficient_information"
    assert result["human_decision"] is None
    assert result["declared_context"]
    assert result["missing_context"]
    assert "result_type" not in result
    assert "obligations" not in result


def test_assess_and_exemption_json_records_hide_internal_legal_branches():
    from assess import public_review_record as assess_record, run_from_answers
    from exempt_check import evaluate, public_review_record as exemption_record

    assess = assess_record(run_from_answers("yes,yes,yes"))
    exemption = exemption_record(evaluate({
        "annex_iii": "yes",
        "profiling": "no",
        "narrow_procedural": "yes",
        "improve_human": "no",
        "detect_patterns": "no",
        "preparatory": "no",
    }))

    for record in (assess, exemption):
        assert record["schema_version"] == "2.0"
        assert record["review_status"] == "human_review_required"
        assert record["human_decision"] is None
        assert "tier" not in record
        assert "result" not in record
    assert assess["potentially_relevant_provisions"][0]["reference"] == "Article 5"
    assert exemption["condition_observations"] == [
        {"condition": "a", "status": "declared_yes_requires_review"}
    ]


def test_declared_context_cannot_unlock_an_automated_conformity_pack():
    from conform import generate_conformity_pack
    from decision_kernel import DecisionKernel, fact

    kernel = DecisionKernel()
    timestamp = "2026-08-30T12:00:00+00:00"
    facts = {
        fact_id: fact("no", "test:declared-context", "eu", timestamp)
        for fact_id, definition in kernel.model["fact_definitions"].items()
        if definition["jurisdiction"] in {"common", "eu"}
    }
    for fact_id in (
        "jurisdiction_in_scope",
        "is_ai_system",
        "role_provider",
        "eu_annex_iii_use",
        "eu_significant_risk",
    ):
        facts[fact_id] = fact(
            "yes", "test:declared-context", "eu", timestamp
        )
    request = {
        "model_version": kernel.model_version,
        "jurisdiction": "eu",
        "facts": facts,
    }

    with tempfile.TemporaryDirectory() as root:
        project = Path(root, "project")
        project.mkdir()
        Path(project, "app.py").write_text(
            "def review_candidate(): pass\n", encoding="utf-8"
        )
        result = generate_conformity_pack(
            str(project),
            output_dir=str(Path(root, "output")),
            decision_request=request,
        )
        pack = Path(result["pack_path"])

        assert result["summary"]["decision"]["human_decision"] is None
        assert result["summary"]["article_duties_attached"] == []
        assert result["summary"]["readiness_assessment"] is None
        assert "overall_readiness" not in result["summary"]
        declaration = (
            pack / "10-declaration-of-conformity" / "declaration-template.md"
        ).read_text(encoding="utf-8")
        assert "**Human conformity decision:** [NOT RECORDED]" in declaration
        assert "Automated readiness score" not in declaration
