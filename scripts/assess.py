# regula-ignore
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
- Digital Omnibus: Annex III deadline proposed Dec 2027, not yet law
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


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


def format_result(tier: str, non_eu_provider: bool) -> str:
    lines = [_header()]

    if tier == TIER_NOT_IN_SCOPE:
        lines += [
            "  Result: NOT IN SCOPE\n",
            "  Your product does not use AI or ML, so the EU AI Act does",
            "  not apply. If that changes, run this check again.",
            "",
        ]
        return "\n".join(lines)

    if tier == TIER_NOT_IN_SCOPE_EU:
        lines += [
            "  Result: NOT CURRENTLY IN SCOPE (EU market)\n",
            "  Your product uses AI but you are not currently marketing to",
            "  EU customers. The Act applies from the point you first have",
            "  EU users. Run `regula check .` now so you are ready.",
            "",
        ]
        return "\n".join(lines)

    if tier == TIER_PROHIBITED:
        lines += [
            "  Result: PROHIBITED PRACTICE DETECTED\n",
            "  One or more practices you described are prohibited under",
            "  Article 5 of the EU AI Act. These prohibitions have been",
            "  in force since 2 February 2025 and apply regardless of",
            "  where you are based.",
            "",
            "  What this means:",
            "  - These practices cannot be made compliant. They must stop.",
            "  - Penalties: up to EUR 35 million or 7% of global turnover.",
            "  - Applies now, not in 2026.",
            "",
            "  Next step: Run `regula check .` to find prohibited patterns",
            "  in your code. Seek qualified legal advice.",
            "",
        ]

    elif tier == TIER_HIGH:
        lines += [
            "  Result: HIGH-RISK AI SYSTEM (Annex III)\n",
            "  Your product falls into a high-risk category under Annex III.",
            "  Articles 9-15 apply -- a substantial compliance obligation.",
            "",
            "  Your obligations:",
            "  Art. 9  -- Risk management system",
            "  Art. 10 -- Training data documentation and data governance",
            "  Art. 11 -- Annex IV technical documentation",
            "  Art. 12 -- Operational logs and audit trail",
            "  Art. 13 -- Transparency with deployers on capabilities/limits",
            "  Art. 14 -- Human oversight mechanisms",
            "  Art. 15 -- Accuracy, robustness, and cybersecurity",
            "",
            "  Deadlines:",
            "  - Legally binding: 2 August 2026.",
            "  - The EU Digital Omnibus proposes extending this to",
            "    2 December 2027 for Annex III systems. This is under",
            "    active negotiation and is NOT yet law. Do not plan",
            "    around it as certain.",
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
            "  Result: LIMITED-RISK (Article 50 transparency obligation)\n",
            "  Your product is in scope, but the obligation is lightweight:",
            "  inform users they are interacting with AI or consuming",
            "  AI-generated content.",
            "",
            "  What Article 50 requires:",
            "  - Chatbots / voice: disclose that the user is talking to AI",
            "    (unless the human is clearly already aware).",
            "  - AI-generated content: label it as AI-generated in a",
            "    machine-readable format.",
            "  - Biometric categorisation: inform affected persons.",
            "",
            "  Deadline: 2 August 2026.",
            "  This deadline is NOT proposed for delay by the Digital Omnibus.",
            "",
            "  Next steps:",
            "  1. regula disclose .    -- generate compliant disclosure text",
            "  2. regula check .       -- confirm no high-risk patterns",
            "",
        ]

    elif tier == TIER_MINIMAL:
        lines += [
            "  Result: MINIMAL-RISK\n",
            "  Your product uses AI but falls into the minimal-risk tier.",
            "  There are no mandatory compliance requirements under the",
            "  EU AI Act for minimal-risk systems.",
            "",
            "  What this means:",
            "  - No documentation, audit trail, or conformity assessment",
            "    required.",
            "  - No transparency disclosure obligation.",
            "  - Article 5 prohibitions still apply -- if you answered no",
            "    to the prohibited practices question, you are clear.",
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


def run_assess(output_format: str = "text") -> int:
    """Main entry point. Returns exit code (1 if prohibited, else 0)."""
    if not sys.stdin.isatty():
        print("Error: `regula assess` requires an interactive terminal.", file=sys.stderr)
        print("Use `regula questionnaire` for non-interactive use.", file=sys.stderr)
        return 1

    try:
        result = run_interactive()
    except KeyboardInterrupt:
        print("\n\n  Assessment cancelled.", file=sys.stderr)
        return 1

    tier = result["tier"]
    non_eu = result["non_eu_provider"]

    if output_format == "json":
        import json
        print(json.dumps(result, indent=2))
        return 1 if tier == TIER_PROHIBITED else 0

    print(format_result(tier, non_eu))
    return 1 if tier == TIER_PROHIBITED else 0
