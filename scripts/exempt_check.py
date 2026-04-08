# regula-ignore
#!/usr/bin/env python3
"""
Regula Exempt — Article 6(3) self-assessment decision tree

Helps a provider determine whether an AI system in an Annex III area is
NOT high-risk under Article 6(3) of the EU AI Act, on the basis that it
does not pose significant risk of harm to the health, safety, or
fundamental rights of natural persons.

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

Status disclosure (verified 2026-04-08):
  The European Commission MISSED its 2 February 2026 deadline for
  publishing guidelines on Article 6 (Article 6(5)). A draft was
  promised end-February 2026 and has not been finalised. Self-assessment
  under Article 6(3) is currently unguided — providers should err on
  the side of treating systems as high-risk, document the rationale
  thoroughly, and re-evaluate when guidelines publish.

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
    "  If YES, the system is high-risk regardless of the other conditions."
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
        "  Regula - Article 6(3) Exemption Self-Assessment\n"
        "================================================================\n"
    )


def _guidelines_status_block() -> list[str]:
    return [
        f"  {_LINE}",
        "  REGULATORY STATUS (verified 2026-04-08):",
        "  The European Commission missed its 2 February 2026 deadline",
        "  for publishing guidelines on Article 6 classification (Art 6(5)).",
        "  A draft was promised by end-February 2026 and has not been",
        "  finalised. Self-assessment under Article 6(3) is currently",
        "  UNGUIDED. Re-evaluate when the guidelines publish.",
        f"  {_LINE}",
    ]


def format_result(result: dict) -> str:
    tier = result["result"]
    answers = result["answers"]
    conditions_met = result.get("conditions_met", [])

    lines = [_header()]

    if tier == RESULT_NOT_IN_ANNEX_III:
        lines += [
            "  Result: NOT IN ANNEX III",
            "",
            "  Your system is not in any of the Annex III high-risk areas.",
            "  Article 6(3) does not apply because the system is not",
            "  high-risk in the first place.",
            "",
            "  Your system may still have transparency obligations under",
            "  Article 50, GPAI obligations under Articles 53-55, or",
            "  general product safety obligations. Run `regula assess`",
            "  for the full applicability check.",
            "",
        ]

    elif tier == RESULT_NOT_EXEMPT and answers.get("profiling") == "yes":
        lines += [
            "  Result: NOT EXEMPT - profiling triggers high-risk",
            "",
            "  Article 6(3) second subparagraph: a system that performs",
            "  profiling of natural persons (GDPR Art 4(4)) IS high-risk",
            "  regardless of conditions (a)-(d).",
            "",
            "  Articles 9-15 obligations apply to your system. Run:",
            "    regula gap          - Articles 9-15 gap assessment",
            "    regula conform      - generate the Annex IV evidence pack",
            "    regula register     - generate the Annex VIII registration",
            "",
        ]
        lines += _guidelines_status_block()

    elif tier == RESULT_NOT_EXEMPT:
        lines += [
            "  Result: NOT EXEMPT under Article 6(3)",
            "",
            "  None of the four exemption conditions (a)-(d) applies.",
            "  Your system remains classified as high-risk under Article",
            "  6(2) + Annex III.",
            "",
            "  Articles 9-15 obligations apply to your system. Run:",
            "    regula gap          - Articles 9-15 gap assessment",
            "    regula conform      - generate the Annex IV evidence pack",
            "    regula register     - generate the Annex VIII registration",
            "",
        ]
        lines += _guidelines_status_block()

    elif tier == RESULT_EXEMPT:
        cond_text = ", ".join(f"({c})" for c in conditions_met)
        lines += [
            "  Result: POTENTIALLY EXEMPT under Article 6(3)",
            "",
            f"  Conditions met: {cond_text}",
            "",
            "  Your self-assessment indicates the system meets at least",
            "  one of the four Article 6(3) conditions and does not perform",
            "  profiling. This is a self-assessment, NOT a legal determination.",
            "",
            "  Article 6(4) requires you to:",
            "  1. Document the rationale for the exemption.",
            "  2. Keep the documentation for 10 years (Article 18).",
            "  3. Register the self-assessment in the EU database",
            "     (Article 49(2)) BEFORE placing the system on the market.",
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
            "  before relying on the exemption. Until the Commission",
            "  guidelines publish, the exemption is the user's risk.",
            "",
        ]

    elif tier == RESULT_NEEDS_REVIEW:
        lines += [
            "  Result: NEEDS LEGAL REVIEW",
            "",
            "  Your answers indicate ambiguity that this self-assessment",
            "  cannot resolve. Consult qualified legal counsel before",
            "  classifying the system.",
            "",
        ]
        lines += _guidelines_status_block()

    lines += [
        f"  {_LINE}",
        "  This output is a documented self-assessment, not legal advice.",
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
    print("  6 questions. Decision tree for the Article 6(3) exemption.")
    print("  Tells you whether your Annex III system can be self-assessed")
    print("  as not-high-risk and what to document if it can.")
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
    Exit code: 0 for any classification (it is informational), 2 for usage
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
        print(json.dumps(result, indent=2))
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
