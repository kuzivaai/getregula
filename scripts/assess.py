# regula-ignore — applicability questionnaire prose describes Annex III use cases to ask the user about
#!/usr/bin/env python3
"""
Regula Assess -- EU AI Act Applicability Check

A standalone, no-code applicability check for founders and developers who
want to know whether the EU AI Act applies to their product and what their
actual obligations are.

This is distinct from the questionnaire (which operates on scan results)
and from classify (which classifies text input). This is a front-door check
for someone who has not scanned code yet.

Regulatory basis:
- Article 2: territorial scope (extraterritorial -- applies to non-EU providers)
- Article 5: prohibited practices (in force Feb 2025)
- Article 6 + Annex III: high-risk classification
- Article 50: transparency obligations (Aug 2026)
- Digital Omnibus: Annex III deadline Dec 2027; enactment status derives
  from scripts/omnibus.py (the single source of truth for the OJ flip)
"""

import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent))

from omnibus import ANNEX_III_PROSE, ADOPTION_HISTORY, BINDING_NOTE, OMNIBUS_ENACTED, OMNIBUS_IN_FORCE_DATE, OMNIBUS_OJ_DATE, ORIGINAL_PROSE


# ---------------------------------------------------------------------------
# Risk tiers
# ---------------------------------------------------------------------------

TIER_NOT_IN_SCOPE = "not_in_scope"
TIER_NOT_IN_SCOPE_EU = "not_in_scope_eu"
TIER_MINIMAL = "minimal_risk"
TIER_LIMITED = "limited_risk"
TIER_HIGH = "high_risk"
TIER_PROHIBITED = "prohibited"


# ---------------------------------------------------------------------------
# Question text
# Note: Article 5 descriptions use plain language that avoids triggering
# Regula's own prohibited-practice pattern detection (false positives on
# documentation text). The regulatory meaning is preserved.
# ---------------------------------------------------------------------------

Q_USES_AI = (
    "Does your product use AI, machine learning, or an AI API?\n"
    "  (Examples: OpenAI, Anthropic, Google AI, Hugging Face, a fine-tuned\n"
    "   model, an ML pipeline, or any system that predicts or decides from data.)"
)

Q_EU_USERS = (
    "Do any users interact with your product from within the EU,\n"
    "  or do you plan to market or sell it to EU customers?"
)

# Article 5 prohibited practices -- plain language descriptions
Q_PROHIBITED = (
    "Does your product do any of the following?\n"
    "  a) Score or rank people's social behaviour for government decision-making\n"
    "  b) Influence user decisions through methods that operate outside their awareness\n"
    "  c) Target and exploit vulnerabilities of specific groups (age, disability)\n"
    "  d) Identify individuals in real-time via cameras or sensors in public spaces\n"
    "  e) Assess the mood or mental state of staff or pupils from expressions/behaviour\n"
    "  f) Infer race, religion, political views or orientation from biometric data\n"
    "  g) Predict criminal behaviour based solely on personal profiling\n\n"
    "  Answer yes if any of the above apply:"
)

# Annex III high-risk domains
Q_HIGH_RISK = (
    "Does your product do any of the following?\n"
    "  a) Screen, rank, or filter job candidates or CVs\n"
    "  b) Make or influence credit, loan, or insurance decisions\n"
    "  c) Assess students or control access to educational programmes\n"
    "  d) Process biometric data (face, fingerprint, voice, gait)\n"
    "  e) Provide outputs used directly by law enforcement\n"
    "  f) Assist healthcare diagnosis or treatment decisions\n"
    "  g) Operate within critical infrastructure (energy, water, transport)\n"
    "  h) Used in migration, asylum, or border control processes\n"
    "  i) Used in administration of justice or legal proceedings\n\n"
    "  Answer yes if any of the above apply:"
)

# Article 50 transparency triggers
Q_TRANSPARENCY = (
    "Does your product do any of the following?\n"
    "  a) Interact with users via chat, conversation, or voice (e.g. a chatbot)\n"
    "  b) Generate text, images, audio, or video users might think is human-made\n"
    "  c) Categorise individuals by detected physical or behavioural traits\n\n"
    "  Answer yes if any of the above apply:"
)

Q_NON_EU = (
    "Are you based outside the EU?\n"
    "  (e.g. in the US, UK, Africa, Asia, or anywhere other than an EU member state)"
)


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------

_SEP = "=" * 64
_LINE = "-" * 60


def _header() -> str:
    return f"\n{_SEP}\n  Regula -- EU AI Act Applicability Check\n{_SEP}\n"


def _omnibus_deadline_lines() -> list:
    """High-risk deadline copy, derived from omnibus.py so the OJ flip
    is a one-line change there rather than a hand-edit here."""
    if OMNIBUS_ENACTED:
        return [
            # "in force from <date>" is truthful before, on and after the
            # entry-into-force date; a flat "is in force" overstates legal
            # status during the 3 days between OJ publication and effect.
            f"  - The Digital Omnibus is in force from {OMNIBUS_IN_FORCE_DATE} "
            f"(OJ {OMNIBUS_OJ_DATE}).",
            f"    Annex III obligations apply from {ANNEX_III_PROSE}.",
        ]
    return [
        f"  - Legally binding: {ORIGINAL_PROSE}.",
        f"  - The EU Digital Omnibus ({ADOPTION_HISTORY})",
        f"    defers Annex III to {ANNEX_III_PROSE}.",
        f"    {BINDING_NOTE}",
    ]


def format_result(tier: str, non_eu_provider: bool) -> str:
    lines = [_header()]

    if tier == TIER_NOT_IN_SCOPE:
        lines += [
            "  Result: NO AI USE DECLARED\n",
            "  Based on your answers, you did not declare AI or ML use.",
            "  This questionnaire therefore found no AI Act indicator. If",
            "  the product or your answer changes, run this check again.",
            "",
        ]
        return "\n".join(lines)

    if tier == TIER_NOT_IN_SCOPE_EU:
        lines += [
            "  Result: NO CURRENT EU-SCOPE INDICATOR DECLARED\n",
            "  Based on your answers, the product uses AI but is not currently",
            "  placed on the EU market and its output is not used in the EU.",
            "  Reassess before that context changes. Run `regula check .` now",
            "  if you want to review code-observable indicators.",
            "",
        ]
        return "\n".join(lines)

    if tier == TIER_PROHIBITED:
        lines += [
            "  Result: POSSIBLE ARTICLE 5 INDICATORS\n",
            "  Your answers describe one or more practices that may fall under",
            "  Article 5 prohibitions. A qualified review must confirm the facts,",
            "  legal scope, and any applicable exception. Article 5 prohibitions",
            "  have applied since 2 February 2025.",
            "",
            "  What this could mean if confirmed:",
            "  - A confirmed prohibited practice cannot be deployed or used as",
            "    described and requires immediate legal and product review.",
            "  - Article 99 sets maximum fines of EUR 35 million or 7% of global",
            "    turnover, with separate limits for SMEs and case-specific enforcement.",
            "",
            "  Next step: Do not rely on this questionnaire as the determination.",
            "  Preserve the answers, seek qualified legal advice, and run",
            "  `regula check .` to review related code indicators.",
            "",
        ]

    elif tier == TIER_HIGH:
        lines += [
            "  Result: CANDIDATE HIGH-RISK INDICATORS (Annex III)\n",
            "  Your answers place the product in an Annex III use area.",
            "  Confirming high-risk status requires intended-purpose and",
            "  Article 6 assessment, including any applicable exclusion.",
            "",
            "  If high-risk status is confirmed, review:",
            "  Art. 9  -- Risk management system",
            "  Art. 10 -- Training data documentation and data governance",
            "  Art. 11 -- Annex IV technical documentation",
            "  Art. 12 -- Operational logs and audit trail",
            "  Art. 13 -- Transparency with deployers on capabilities/limits",
            "  Art. 14 -- Human oversight mechanisms",
            "  Art. 15 -- Accuracy, robustness, and cybersecurity",
            "",
            "  Deadlines:",
        ] + _omnibus_deadline_lines() + [
            "",
        ]
        if non_eu_provider:
            lines += [
                "  You are outside the EU -- additional requirement:",
                "  Article 22 requires non-EU providers of high-risk systems",
                "  to appoint an EU-based Authorised Representative before",
                "  placing the product on the EU market. This is a legal",
                "  prerequisite, not optional. Typical cost: EUR 2-10K/year.",
                "",
            ]
        lines += [
            "  Next steps:",
            "  1. regula check .       -- code-level risk scan",
            "  2. regula gap .         -- Articles 9-15 gap assessment",
            "  3. regula docs .        -- generate Annex IV scaffold",
            "  4. regula plan .        -- prioritised remediation tasks",
            "",
        ]

    elif tier == TIER_LIMITED:
        lines += [
            "  Result: CANDIDATE ARTICLE 50 INDICATORS\n",
            "  Your answers indicate a use that may trigger Article 50",
            "  transparency duties. Confirm the exact system and deployment",
            "  context before treating a listed duty as applicable.",
            "",
            "  What Article 50 requires:",
            "  - Chatbots / voice: disclose that the user is talking to AI",
            "    (unless the human is clearly already aware).",
            "  - AI-generated content: label it as AI-generated in a",
            "    machine-readable format.",
            "  - Biometric categorisation: inform affected persons.",
            "",
            f"  Deadline: {ORIGINAL_PROSE}.",
            "  This deadline is unchanged by the Digital Omnibus.",
            "",
            "  Next steps:",
            # This step used to describe the generated disclosure text as
            # carrying a compliance state, which asserts that an artefact the
            # tool produces satisfies the law. That is the determination this
            # project forbids, and it sat seven lines above the TIER_MINIMAL
            # passage that gets the register exactly right. LEDGER N125 carries
            # the verbatim old wording. The command drafts text for review.
            "  1. regula disclose .    -- draft disclosure text to review",
            "  2. regula check .       -- look for high-risk patterns in code",
            "",
        ]

    elif tier == TIER_MINIMAL:
        lines += [
            "  Result: NO SPECIFIC RISK-TIER INDICATOR FROM THESE ANSWERS\n",
            "  Your answers did not trigger the prohibited, Annex III, or",
            "  Article 50 paths in this questionnaire. That is not a legal",
            "  classification and does not test every AI Act obligation.",
            "",
            "  What this means:",
            "  - Reassess when intended purpose, users, or deployment changes.",
            "  - Article 4 AI-literacy and Article 5 prohibitions may still matter.",
            "  - Use qualified review for unresolved or high-consequence contexts.",
            "",
            "  Good practice (not mandatory):",
            "  Run `regula check .` periodically. If your product evolves",
            "  into a new use case, your classification may change.",
            "",
        ]

    lines += [
        f"  {_LINE}",
        "  Findings are indicators for human review, not legal determinations.",
        "  The EU AI Act requires contextual assessment this tool cannot",
        "  provide. For high-risk systems, seek qualified legal advice.",
        f"  {_LINE}",
        "",
    ]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Interactive flow
# ---------------------------------------------------------------------------

def _ask(prompt_text: str) -> str:
    """Prompt yes/no. Returns 'yes' or 'no'."""
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
    """Run the interactive assess flow. Returns result dict."""
    print(_header())
    print("  5 questions. No code required. Takes under 2 minutes.")
    print("  Tells you whether the EU AI Act applies to your product")
    print("  and exactly what you need to do.")
    print()

    answers: dict = {}

    answers["uses_ai"] = _ask(Q_USES_AI)
    if answers["uses_ai"] == "no":
        return {"tier": TIER_NOT_IN_SCOPE, "non_eu_provider": False, "answers": answers}

    answers["eu_users"] = _ask(Q_EU_USERS)
    if answers["eu_users"] == "no":
        return {"tier": TIER_NOT_IN_SCOPE_EU, "non_eu_provider": False, "answers": answers}

    answers["prohibited"] = _ask(Q_PROHIBITED)
    if answers["prohibited"] == "yes":
        return {"tier": TIER_PROHIBITED, "non_eu_provider": False, "answers": answers}

    answers["high_risk_domain"] = _ask(Q_HIGH_RISK)
    if answers["high_risk_domain"] == "yes":
        answers["non_eu_provider"] = _ask(Q_NON_EU)
        non_eu = answers["non_eu_provider"] == "yes"
        return {"tier": TIER_HIGH, "non_eu_provider": non_eu, "answers": answers}

    answers["transparency_trigger"] = _ask(Q_TRANSPARENCY)
    tier = TIER_LIMITED if answers["transparency_trigger"] == "yes" else TIER_MINIMAL
    return {"tier": tier, "non_eu_provider": False, "answers": answers}


def run_from_answers(answers_csv: str) -> dict:
    """Run the assess flow from a comma-separated answers list.

    Order (same as the interactive flow): uses_ai, eu_users, prohibited,
    high_risk_domain, non_eu_provider, transparency_trigger.

    Short-circuit rules match run_interactive():
      - uses_ai=no        -> TIER_NOT_IN_SCOPE
      - eu_users=no       -> TIER_NOT_IN_SCOPE_EU
      - prohibited=yes    -> TIER_PROHIBITED
      - high_risk=yes     -> TIER_HIGH (consumes non_eu_provider)
      - otherwise         -> TIER_LIMITED / TIER_MINIMAL by transparency
    """
    def _norm(v: str) -> str:
        v = (v or "").strip().lower()
        if v in ("y", "yes", "true", "1"):
            return "yes"
        if v in ("n", "no", "false", "0"):
            return "no"
        raise ValueError(f"invalid answer {v!r} — expected yes/no")

    raw = [a for a in (answers_csv or "").split(",") if a.strip()]
    if not raw:
        raise ValueError("--answers is empty")
    answers: dict = {}
    # uses_ai
    answers["uses_ai"] = _norm(raw[0])
    if answers["uses_ai"] == "no":
        return {"tier": TIER_NOT_IN_SCOPE, "non_eu_provider": False, "answers": answers}
    if len(raw) < 2:
        raise ValueError("missing eu_users answer")
    answers["eu_users"] = _norm(raw[1])
    if answers["eu_users"] == "no":
        return {"tier": TIER_NOT_IN_SCOPE_EU, "non_eu_provider": False, "answers": answers}
    if len(raw) < 3:
        raise ValueError("missing prohibited answer")
    answers["prohibited"] = _norm(raw[2])
    if answers["prohibited"] == "yes":
        return {"tier": TIER_PROHIBITED, "non_eu_provider": False, "answers": answers}
    if len(raw) < 4:
        raise ValueError("missing high_risk_domain answer")
    answers["high_risk_domain"] = _norm(raw[3])
    if answers["high_risk_domain"] == "yes":
        if len(raw) < 5:
            raise ValueError("missing non_eu_provider answer (required when high_risk=yes)")
        answers["non_eu_provider"] = _norm(raw[4])
        return {"tier": TIER_HIGH, "non_eu_provider": answers["non_eu_provider"] == "yes", "answers": answers}
    if len(raw) < 5:
        raise ValueError("missing transparency_trigger answer")
    # When high_risk=no, the 5th slot is transparency_trigger.
    answers["transparency_trigger"] = _norm(raw[4])
    tier = TIER_LIMITED if answers["transparency_trigger"] == "yes" else TIER_MINIMAL
    return {"tier": tier, "non_eu_provider": False, "answers": answers}


# Which assess answers correspond EXACTLY to one fact in the decision model, and
# which do not. The unmapped ones are listed with their reason rather than
# omitted, because an answer that silently goes nowhere is what N149 is about.
#
# The test is correspondence, not similarity. `prohibited` and
# `transparency_trigger` each ask one yes/no question covering seven and three
# distinct kernel facts respectively, so a `yes` does not say WHICH, and writing
# it against any single fact id would be Regula inventing a fact. The honest
# answer is that this questionnaire cannot resolve them, said out loud.
ANSWER_TO_FACT = {
    "uses_ai": ("is_ai_system", Q_USES_AI),
    "eu_users": ("jurisdiction_in_scope", Q_EU_USERS),
    "high_risk_domain": ("eu_annex_iii_use", Q_HIGH_RISK),
}

ANSWER_NOT_MAPPED = {
    "prohibited": (
        "one yes/no over seven separate Article 5 practices; the model has a "
        "distinct fact for each and a single yes does not say which"),
    "transparency_trigger": (
        "one yes/no over direct interaction, synthetic content and biometric "
        "categorisation; the model has a distinct fact for each"),
    "non_eu_provider": (
        "the model has no fact for where the provider is established; "
        "jurisdiction_in_scope and role_provider are different questions"),
}


def facts_from_answers(answers: dict, jurisdiction: str = "eu") -> tuple:
    """Map assess answers onto canonical facts. Returns (facts, unmapped).

    Every value is `user_declaration`: a person answered a question this tool
    asked, and the question asked is recorded in the provenance so a later
    reader can judge the correspondence rather than take it on trust. The assess
    wording is broader than the legal definition in at least one place
    (`uses_ai` asks about using an AI API; `is_ai_system` asks whether the
    subject meets the Act's definition), which is exactly why the question
    travels with the answer.
    """
    import fact_store as fs

    facts = {}
    for answer_key, (fact_id, question) in ANSWER_TO_FACT.items():
        if answer_key not in answers:
            continue
        state = answers[answer_key]
        if state not in ("yes", "no"):
            continue
        facts[fact_id] = {"values": [fs.build_value(
            state, jurisdiction, "cli:assess",
            source_type=fs.SOURCE_USER_DECLARATION,
            # The WHOLE question, not its first line. `high_risk_domain` opens
            # with "Does your product do any of the following?" and everything
            # that makes the answer mean anything is in the nine bullets under
            # it. An evidence record that stored only the opening line would
            # record that somebody said yes to nothing in particular.
            question=" ".join(question.split()),
            derived_from=f"assess:{answer_key}",
        )]}
    unmapped = {k: v for k, v in ANSWER_NOT_MAPPED.items() if k in answers}
    return facts, unmapped


def save_declared_facts(result: dict, project: str, jurisdiction: str = "eu") -> dict:
    """Write the mappable answers to <project>/.regula/facts.json.

    Merges over an existing store rather than replacing it, so answering the
    questionnaire a second time does not silently discard a fact declared with
    `check --fact`.
    """
    import fact_store as fs
    from decision_kernel import DecisionKernel

    kernel = DecisionKernel()
    facts, unmapped = facts_from_answers(result.get("answers", {}), jurisdiction)
    path = fs.store_path(project)
    existing = {}
    if path.is_file():
        existing = fs.load(path, kernel.model)["facts"]
    merged = fs.merge(existing, facts)
    fs.save(path, merged, kernel.model_version)
    return {"path": str(path), "written": facts, "unmapped": unmapped,
            "total_in_store": len(merged)}


def run_assess(output_format: str = "text", answers: Optional[str] = None,
               save_facts: Optional[str] = None) -> int:
    """Main entry point. Returns exit code (1 if prohibited, else 0)."""
    if answers is not None:
        try:
            result = run_from_answers(answers)
        except ValueError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            print(
                "  --answers order: uses_ai,eu_users,prohibited,"
                "high_risk_domain,non_eu_provider|transparency_trigger",
                file=sys.stderr,
            )
            return 2
    else:
        if not sys.stdin.isatty():
            print("Error: `regula assess` requires an interactive terminal,", file=sys.stderr)
            print(
                "or pass --answers as a comma-separated list of yes/no values in order:",
                file=sys.stderr,
            )
            print(
                "  uses_ai,eu_users,prohibited,high_risk_domain,"
                "non_eu_provider|transparency_trigger",
                file=sys.stderr,
            )
            print("Or use `regula questionnaire` for the richer non-interactive flow.", file=sys.stderr)
            return 1

        try:
            result = run_interactive()
        except KeyboardInterrupt:
            print("\n\n  Assessment cancelled.", file=sys.stderr)
            return 1

    tier = result["tier"]
    non_eu = result["non_eu_provider"]

    exit_code = 1 if tier == TIER_PROHIBITED else 0

    saved = None
    if save_facts is not None:
        try:
            saved = save_declared_facts(result, save_facts)
        except Exception as exc:                                # noqa: BLE001
            print(f"Error: could not write declared facts: {exc}", file=sys.stderr)
            return 2
        result = dict(result, declared_facts=saved)

    if output_format == "json":
        import json
        from envelope import build_envelope
        print(json.dumps(build_envelope("assess", result, exit_code),
                         indent=2, sort_keys=True, default=str))
        return exit_code

    print(format_result(tier, non_eu))
    if saved is not None:
        print()
        print(f"  Declared facts written to {saved['path']}")
        print(f"  {len(saved['written'])} of your answers map to a fact the "
              f"decision model uses; {saved['total_in_store']} fact(s) now in the store:")
        for fact_id in sorted(saved["written"]):
            print(f"    - {fact_id} = {saved['written'][fact_id]['values'][0]['state']}")
        if saved["unmapped"]:
            print(f"  {len(saved['unmapped'])} answer(s) were NOT written, and why:")
            for key, reason in sorted(saved["unmapped"].items()):
                print(f"    - {key}: {reason}")
        print("  These are your declarations. Regula establishes none of them.")
        print("  Next: regula check .   (it now reads them)")
    return exit_code
