# regula-ignore — Article 6(3) decision tree describes the high-risk use cases it screens for
#!/usr/bin/env python3
"""
Regula Exempt — Article 6(3) context-review decision tree

Records answers relevant to an accountable review of Article 6(3). It does not
determine whether a system is high-risk or exempt.

Article 6(3) lists four conditions, of which at least one must apply:
    (a) narrow procedural task
    (b) intended to improve the result of a previously completed human activity
    (c) intended to detect decision-making patterns or deviations from
        prior decision-making patterns and not meant to replace or
        influence the previously completed human assessment without
        proper human review
    (d) intended to perform a preparatory task to an assessment relevant
        for the purposes of the use cases listed in Annex III

Hard carve-out (Article 6(3) second subparagraph): a system that performs
profiling of natural persons IS high-risk regardless of (a)-(d).

If a provider self-assesses as exempt, Article 6(4) requires them to:
  - document the rationale
  - keep the documentation for 10 years (Article 18)
  - register the self-assessment in the EU database (Article 49(2))
    before placing the system on the market

Status disclosure (verified 2026-07-23):
  The European Commission MISSED its 2 February 2026 deadline for
  publishing guidelines on Article 6 (Article 6(5)). It published DRAFT
  guidelines on 19 May 2026 (targeted consultation to 23 July 2026) that
  are not yet finalised. Self-assessment under Article 6(3) can follow the
  draft, which may change before adoption; providers should still err on
  the side of treating systems as high-risk and document the rationale.

This module is a structured walkthrough that produces a documented
self-assessment record. It is NOT a legal determination. Providers
should consult qualified counsel before placing exempt-classified
systems on the market.
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

# Self-protect the sibling-import path: _guidelines_status_block() imports
# ARTICLE_6_GUIDELINES_STATUS from compliance_check (the single source of
# truth), so this module must seed sys.path like every other script that
# bare-imports a sibling (enforced by test_source_of_truth).
sys.path.insert(0, str(Path(__file__).parent))

# ---------------------------------------------------------------------------
# Result tiers
# ---------------------------------------------------------------------------

RESULT_NOT_IN_ANNEX_III = "not_in_annex_iii"
RESULT_EXEMPT = "exempt"
RESULT_NOT_EXEMPT = "not_exempt"
RESULT_NEEDS_REVIEW = "needs_legal_review"


# ---------------------------------------------------------------------------
# Question text (plain language to avoid self-flagging)
# ---------------------------------------------------------------------------

Q_ANNEX_III = (
    "Does your AI system fall into one of the Annex III categories?\n"
    "  (Biometric identification or categorisation, critical infrastructure,\n"
    "   education, employment / hiring / worker management, access to\n"
    "   essential private or public services, law enforcement, migration\n"
    "   and border control, administration of justice and democratic\n"
    "   processes.)"
)

Q_PROFILING = (
    "Does your system perform profiling of natural persons?\n"
    "  (Profiling per GDPR Article 4(4): any form of automated processing\n"
    "   to evaluate personal aspects, in particular to analyse or predict\n"
    "   performance at work, economic situation, health, preferences,\n"
    "   reliability, behaviour, location, or movements.)\n"
    "  A YES answer makes Article 6(3)'s second subparagraph relevant; a\n"
    "  reviewer must confirm the definition, context, conditions, and exceptions."
)

Q_NARROW_PROCEDURAL = (
    "Condition (a): Is the system intended to perform a narrow procedural\n"
    "  task only?\n"
    "  (Examples from Recital 53: turning unstructured data into structured\n"
    "   data; classifying incoming documents into categories; detecting\n"
    "   duplicates among large numbers of applications. Anything that does\n"
    "   not affect the substance of the human decision.)"
)

Q_IMPROVE_HUMAN = (
    "Condition (b): Is the system intended to improve the result of a\n"
    "  previously completed human activity?\n"
    "  (Example from Recital 53: improving the language used in previously\n"
    "   drafted documents — proofreading, formatting, translation polish.\n"
    "   The human did the substantive work first; the AI refines it.)"
)

Q_DETECT_PATTERNS = (
    "Condition (c): Is the system intended to detect decision-making\n"
    "  patterns or deviations from prior decision-making patterns, and is\n"
    "  it NOT meant to replace or influence the previously completed human\n"
    "  assessment without proper human review?\n"
    "  (Example from Recital 53: flagging potential inconsistencies for a\n"
    "   human reviewer to verify, where the human still makes the call.)"
)

Q_PREPARATORY = (
    "Condition (d): Is the system intended to perform a preparatory task\n"
    "  to an assessment relevant for the purposes of an Annex III use case?\n"
    "  (Example from Recital 53: file handling, translation of input\n"
    "   documents, smart search and retrieval — work that prepares material\n"
    "   for a human assessor without itself producing the assessment.)"
)


# ---------------------------------------------------------------------------
# Result formatting
# ---------------------------------------------------------------------------

_LINE = "-" * 60


def _header() -> str:
    return (
        "\n"
        "================================================================\n"
        "  Regula - Article 6(3) Context Review\n"
        "================================================================\n"
    )


def _guidelines_status_block() -> list[str]:
    # Rendered from the single source of truth (compliance_check.
    # ARTICLE_6_GUIDELINES_STATUS) so this block cannot drift from the gap
    # report / JSON when the Commission publishes the guidelines. Function-local
    # import keeps exempt_check loadable standalone and avoids any import cycle.
    from compliance_check import ARTICLE_6_GUIDELINES_STATUS as s, _uk_date
    lines = [
        f"  {_LINE}",
        f"  REGULATORY STATUS (verified {s['verified_on']}):",
    ]
    if s.get("missed") and s.get("current_status") != "finalised":
        lines += [
            f"  The European Commission missed its {_uk_date(s['deadline'])} deadline",
            "  for publishing guidelines on Article 6 classification (Art 6(5)).",
        ]
        draft_pub = s.get("draft_published_on")
        if draft_pub:
            consult = s.get("consultation_until")
            consult_clause = (
                f" (consultation to {_uk_date(consult)})" if consult else ""
            )
            lines += [
                f"  DRAFT guidelines were published on {_uk_date(draft_pub)}"
                f"{consult_clause}",
                "  but are not yet finalised. Self-assessment under Article 6(3)",
                "  can follow the draft, which may change before adoption.",
            ]
        else:
            promised = s.get("draft_promised_by")
            lines += [
                (f"  A draft was promised by {_uk_date(promised)} and has not been"
                 if promised else "  A draft was promised and has not been"),
                "  finalised. Self-assessment under Article 6(3) is currently",
                "  UNGUIDED. Re-evaluate when the guidelines publish.",
            ]
    else:
        lines += [
            "  The European Commission has PUBLISHED its Article 6(5) guidelines",
            f"  on high-risk classification (deadline was {_uk_date(s['deadline'])}).",
            "  Self-assessment under Article 6(3) can now follow that guidance.",
        ]
    lines.append(f"  {_LINE}")
    return lines


def format_result(result: dict) -> str:
    tier = result["result"]
    answers = result["answers"]
    conditions_met = result.get("conditions_met", [])

    lines = [_header()]

    if tier == RESULT_NOT_IN_ANNEX_III:
        lines += [
            "  Review status: ANNEX III ANSWER RECORDED",
            "",
            "  You answered that the system is not in an Annex III area.",
            "  This declaration does not establish legal non-applicability.",
            "  Confirm intended purpose, actual use and Article 6 conditions",
            "  with an accountable reviewer.",
            "",
            "  Article 50, Articles 53 to 55 and product-safety provisions",
            "  may still be relevant. Run `regula assess` to record more",
            "  context, not to obtain an applicability decision.",
            "",
        ]

    elif tier == RESULT_NOT_EXEMPT and answers.get("profiling") == "yes":
        lines += [
            "  Review status: PROFILING ANSWER REQUIRES ARTICLE 6 REVIEW",
            "",
            "  You declared profiling of natural persons. Article 6(3)'s",
            "  second subparagraph is potentially relevant. A reviewer must",
            "  confirm the profiling definition and the system context.",
            "",
            "  If a reviewer confirms the required predicates, consider:",
            "    regula gap          - Articles 9-15 gap assessment",
            "    regula conform      - generate the Annex IV evidence pack",
            "    regula register     - generate the Annex VIII registration",
            "",
        ]
        lines += _guidelines_status_block()

    elif tier == RESULT_NOT_EXEMPT:
        lines += [
            "  Review status: NO ARTICLE 6(3) CONDITION DECLARED",
            "",
            "  You answered no to each of the four Article 6(3) conditions.",
            "  That is declared context, not a legal classification. A reviewer",
            "  must confirm intended purpose, Annex III context and the answers.",
            "",
            "  If a reviewer confirms the required predicates, consider:",
            "    regula gap          - Articles 9-15 gap assessment",
            "    regula conform      - generate the Annex IV evidence pack",
            "    regula register     - generate the Annex VIII registration",
            "",
        ]
        lines += _guidelines_status_block()

    elif tier == RESULT_EXEMPT:
        cond_text = ", ".join(f"({c})" for c in conditions_met)
        lines += [
            "  Review status: ARTICLE 6(3) CONDITION INDICATORS DECLARED",
            "",
            f"  Conditions answered yes: {cond_text}",
            "",
            "  Your answers mark at least one condition yes and profiling no.",
            "  They do not establish that a condition is legally satisfied or",
            "  that the system is exempt.",
            "",
            "  If an accountable review confirms Article 6(3) treatment,",
            "  review Article 6(4), Article 18 and Article 49(2), including",
            "  rationale, retention and registration conditions.",
            "",
            "  Generate the Annex VIII registration packet with the",
            "  exemption flag set:",
            "    regula register --art-6-3-exempted",
            "",
        ]
        lines += _guidelines_status_block()
        lines += [
            "",
            "  STRONG RECOMMENDATION: consult qualified legal counsel",
            "  before recording any exemption decision. The tool leaves the",
            "  human decision empty.",
            "",
        ]

    elif tier == RESULT_NEEDS_REVIEW:
        lines += [
            "  Review status: INCOMPLETE CONTEXT",
            "",
            "  Your answers indicate ambiguity that this self-assessment",
            "  cannot resolve. Consult qualified legal counsel before",
            "  recording a legal decision.",
            "",
        ]
        lines += _guidelines_status_block()

    lines += [
        f"  {_LINE}",
        "  This output records declared context, not legal advice or a decision.",
        "  Article 6(3) requires contextual judgement; the Commission",
        "  guidelines that would standardise that judgement are overdue.",
        f"  {_LINE}",
        "",
    ]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------

def evaluate(answers: dict) -> dict:
    """Pure function: takes a normalised answers dict and returns a result.

    Answers keys (each "yes" or "no"):
        annex_iii, profiling, narrow_procedural, improve_human,
        detect_patterns, preparatory.

    Returns dict with keys: result, conditions_met, answers, assessed_at.
    """
    out: dict[str, Any] = {
        "result": RESULT_NEEDS_REVIEW,
        "conditions_met": [],
        "answers": dict(answers),
        "assessed_at": date.today().isoformat(),
    }

    if answers.get("annex_iii") != "yes":
        out["result"] = RESULT_NOT_IN_ANNEX_III
        return out

    if answers.get("profiling") == "yes":
        out["result"] = RESULT_NOT_EXEMPT
        return out

    conditions = []
    if answers.get("narrow_procedural") == "yes":
        conditions.append("a")
    if answers.get("improve_human") == "yes":
        conditions.append("b")
    if answers.get("detect_patterns") == "yes":
        conditions.append("c")
    if answers.get("preparatory") == "yes":
        conditions.append("d")

    if conditions:
        out["result"] = RESULT_EXEMPT
        out["conditions_met"] = conditions
    else:
        out["result"] = RESULT_NOT_EXEMPT

    return out


def public_review_record(result: dict) -> dict:
    """Expose declared answers without the internal decision-tree branch."""
    answers = result.get("answers", {})
    expected = {
        "annex_iii", "profiling", "narrow_procedural", "improve_human",
        "detect_patterns", "preparatory",
    }
    return {
        "schema_version": "2.0",
        "record_type": "article_6_3_context_review",
        "review_status": "human_review_required",
        "declared_context": [
            {
                "fact_id": key,
                "state": value,
                "provenance": {
                    "source_type": "user_declaration",
                    "source_ref": f"exempt:{key}",
                },
            }
            for key, value in sorted(answers.items())
        ],
        "missing_context": [
            {"fact_id": key, "reason": "not_asked_or_unanswered"}
            for key in sorted(expected - set(answers))
        ],
        "contradictory_context": [],
        "condition_observations": [
            {"condition": item, "status": "declared_yes_requires_review"}
            for item in result.get("conditions_met", [])
        ],
        "potentially_relevant_provisions": [
            {
                "reference": "Article 6(3)",
                "status": "potentially_relevant",
                "source_version": None,
                "source_date": None,
            }
        ],
        "reviewer_questions": [
            "Does evidence support the declared Annex III use and intended purpose?",
            "Does the actual processing meet the profiling definition?",
            "Does evidence support each declared Article 6(3) condition?",
        ],
        "suggested_human_review_steps": [
            "Validate each answer against design and deployment evidence.",
            "Review Article 6 conditions and exceptions with qualified expertise.",
            "Record the accountable reviewer's decision separately.",
        ],
        "explicit_limitations": [
            "This record does not determine high-risk status, exemption, duties, compliance, or non-applicability."
        ],
        "human_decision": None,
    }


# ---------------------------------------------------------------------------
# Interactive runner
# ---------------------------------------------------------------------------

def _ask(prompt_text: str) -> str:
    print(f"\n  {prompt_text}")
    while True:
        try:
            raw = input("  y/n: ").strip().lower()
        except EOFError:
            return "no"
        if raw in ("y", "yes"):
            return "yes"
        if raw in ("n", "no"):
            return "no"
        print("  Please answer y or n.")


def run_interactive() -> dict:
    print(_header())
    print("  6 questions that preserve context relevant to Article 6(3).")
    print("  The result identifies review questions and does not decide")
    print("  high-risk status, exemption, duties, or compliance.")
    print()

    answers: dict[str, str] = {}

    answers["annex_iii"] = _ask(Q_ANNEX_III)
    if answers["annex_iii"] == "no":
        return evaluate(answers)

    answers["profiling"] = _ask(Q_PROFILING)
    if answers["profiling"] == "yes":
        return evaluate(answers)

    answers["narrow_procedural"] = _ask(Q_NARROW_PROCEDURAL)
    answers["improve_human"] = _ask(Q_IMPROVE_HUMAN)
    answers["detect_patterns"] = _ask(Q_DETECT_PATTERNS)
    answers["preparatory"] = _ask(Q_PREPARATORY)

    return evaluate(answers)


def run_exempt(output_format: str = "text",
               answers: dict | None = None) -> int:
    """Main entry point.

    If `answers` is provided (non-interactive mode), evaluate it directly.
    Otherwise require an interactive terminal.
    Exit code: 0 for any review path (it is informational), 2 for usage
    errors.
    """
    if answers is not None:
        result = evaluate(answers)
    else:
        if not sys.stdin.isatty():
            print(
                "Error: `regula exempt` requires an interactive terminal,\n"
                "or pass --answers as a comma-separated list of yes/no values\n"
                "in order: annex_iii,profiling,narrow_procedural,improve_human,\n"
                "detect_patterns,preparatory.",
                file=sys.stderr,
            )
            return 2
        try:
            result = run_interactive()
        except KeyboardInterrupt:
            print("\n\n  Self-assessment cancelled.", file=sys.stderr)
            return 1

    if output_format == "json":
        print(json.dumps(public_review_record(result), indent=2))
    else:
        print(format_result(result))
    return 0


def parse_answers_csv(csv: str) -> dict | None:
    """Parse a comma-separated answers string for non-interactive use.

    Order: annex_iii, profiling, narrow_procedural, improve_human,
    detect_patterns, preparatory. Each must be 'y'/'yes' or 'n'/'no'.
    Returns a normalised answers dict, or None if the input is malformed.
    """
    keys = [
        "annex_iii", "profiling", "narrow_procedural",
        "improve_human", "detect_patterns", "preparatory",
    ]
    parts = [p.strip().lower() for p in csv.split(",")]
    if len(parts) != len(keys):
        return None
    out = {}
    for k, v in zip(keys, parts):
        if v in ("y", "yes"):
            out[k] = "yes"
        elif v in ("n", "no"):
            out[k] = "no"
        else:
            return None
    return out
