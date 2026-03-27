#!/usr/bin/env python3
# regula-ignore
"""
Regula Remediation Engine - Generates specific fix suggestions for findings.

Every finding gets a concrete, actionable remediation with:
- What to do (specific code change or command)
- Why (which EU AI Act article requires it)
- How (copy-paste code snippet or CLI command)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


# ---------------------------------------------------------------------------
# Category remediation lookup
# ---------------------------------------------------------------------------

CATEGORY_REMEDIATIONS = {
    "employment": {
        "summary": "Add human oversight before automated hiring/employment decisions",
        "article": "Articles 9-15 (effective Aug 2026)",
        "fix_code": (
            "# Article 14: Add human review before any employment decision\n"
            "def review_candidate(ai_prediction, reviewer_id):\n"
            "    \\\"\\\"\\\"Human must review and approve AI hiring recommendation.\\\"\\\"\\\"\n"
            "    import logging\n"
            "    logger = logging.getLogger(__name__)\n"
            "    logger.info(f\\\"AI prediction sent for human review by {reviewer_id}\\\")\n"
            "    return {\n"
            "        \\\"ai_recommendation\\\": ai_prediction,\n"
            "        \\\"status\\\": \\\"pending_human_review\\\",\n"
            "        \\\"reviewer\\\": reviewer_id,\n"
            "    }"
        ),
        "fix_command": "",
        "explanation": "EU AI Act Annex III Category 4 classifies employment AI as high-risk. Article 14 requires human oversight with ability to override AI decisions.",
    },
    "essential_services": {
        "summary": "Add explainability and human override for credit/financial decisions",
        "article": "Articles 9-15 (effective Aug 2026)",
        "fix_code": (
            "# Article 13: Add transparency to financial AI decisions\n"
            "def explain_decision(prediction, features, model):\n"
            "    \\\"\\\"\\\"Article 13: Provide explanation for AI-assisted financial decision.\\\"\\\"\\\"\n"
            "    import logging\n"
            "    logger = logging.getLogger(__name__)\n"
            "    explanation = {\n"
            "        \\\"decision\\\": prediction,\n"
            "        \\\"key_factors\\\": get_top_features(features, model, n=5),\n"
            "        \\\"confidence\\\": float(model.predict_proba(features)[0].max()),\n"
            "        \\\"model_version\\\": getattr(model, \\\"version\\\", \\\"unknown\\\"),\n"
            "        \\\"transparency_notice\\\": \\\"This decision was assisted by an AI system.\\\",\n"
            "    }\n"
            "    logger.info(f\\\"Financial decision explained: {explanation[\'decision\']}\\\")"
            "\n    return explanation"
        ),
        "fix_command": "",
        "explanation": "EU AI Act Annex III Category 5 classifies financial AI as high-risk. Article 13 requires transparency about AI-assisted decisions.",
    },
    "biometrics": {
        "summary": "Add consent mechanism and data minimisation for biometric processing",
        "article": "Articles 9-15 (effective Aug 2026)",
        "fix_code": (
            "# Article 10: Data governance for biometric systems\n"
            "def process_biometric(data, purpose, consent_record):\n"
            "    \\\"\\\"\\\"Article 10: Ensure data governance for biometric processing.\\\"\\\"\\\"\n"
            "    assert consent_record is not None, \\\"Biometric processing requires documented consent\\\"\n"
            "    assert purpose in ALLOWED_PURPOSES, f\\\"Purpose '{purpose}' not in allowed list\\\"\n"
            "    # Process only the minimum data needed\n"
            "    minimal_data = extract_minimum_features(data)\n"
            "    return minimal_data"
        ),
        "fix_command": "",
        "explanation": "EU AI Act Annex III Category 1 classifies biometric identification as high-risk. Article 10 requires documented data governance.",
    },
    "education": {
        "summary": "Add human oversight for educational assessment decisions",
        "article": "Articles 9-15 (effective Aug 2026)",
        "fix_code": (
            "# Article 14: Human oversight for educational AI\n"
            "def assess_student(ai_score, teacher_id):\n"
            "    \\\"\\\"\\\"Article 14: Teacher must review AI-generated assessment.\\\"\\\"\\\"\n"
            "    return {\\\"ai_score\\\": ai_score, \\\"status\\\": \\\"awaiting_teacher_review\\\", \\\"teacher\\\": teacher_id}"
        ),
        "fix_command": "",
        "explanation": "EU AI Act Annex III Category 3 classifies educational AI as high-risk.",
    },
    "medical_devices": {
        "summary": "Add clinical validation and human oversight for medical AI",
        "article": "Articles 9-15 + Medical Device Regulation",
        "fix_code": (
            "# Article 14: Clinical oversight for medical AI\n"
            "def clinical_recommendation(ai_output, clinician_id):\n"
            "    \\\"\\\"\\\"Article 14: Clinician must review and approve medical AI recommendation.\\\"\\\"\\\"\n"
            "    return {\\\"recommendation\\\": ai_output, \\\"status\\\": \\\"pending_clinical_review\\\", \\\"clinician\\\": clinician_id}"
        ),
        "fix_command": "",
        "explanation": "Medical AI devices are high-risk under both the EU AI Act and the Medical Device Regulation.",
    },
    "law_enforcement": {
        "summary": "Add human oversight and audit logging for law enforcement AI",
        "article": "Articles 9-15 (effective Aug 2026)",
        "fix_code": (
            "# Article 14: Human oversight for law enforcement AI\n"
            "def review_evidence_assessment(ai_output, officer_id):\n"
            "    \\\"\\\"\\\"Article 14: Officer must review AI-assisted evidence assessment.\\\"\\\"\\\"\n"
            "    import logging\n"
            "    logger = logging.getLogger(__name__)\n"
            "    logger.info(f\\\"Law enforcement AI output sent for review by {officer_id}\\\")\n"
            "    return {\\\"ai_assessment\\\": ai_output, \\\"status\\\": \\\"pending_officer_review\\\", \\\"officer\\\": officer_id}"
        ),
        "fix_command": "",
        "explanation": "EU AI Act Annex III Category 6 classifies law enforcement AI as high-risk. Article 14 requires human oversight.",
    },
    "migration": {
        "summary": "Add human oversight for migration and border control AI decisions",
        "article": "Articles 9-15 (effective Aug 2026)",
        "fix_code": (
            "# Article 14: Human oversight for migration AI\n"
            "def review_application(ai_recommendation, officer_id):\n"
            "    \\\"\\\"\\\"Article 14: Officer must review AI-assisted migration decision.\\\"\\\"\\\"\n"
            "    return {\\\"ai_recommendation\\\": ai_recommendation, \\\"status\\\": \\\"pending_officer_review\\\", \\\"officer\\\": officer_id}"
        ),
        "fix_command": "",
        "explanation": "EU AI Act Annex III Category 7 classifies migration and border control AI as high-risk. Article 14 requires human oversight.",
    },
    "justice": {
        "summary": "Add human oversight for judicial and democratic process AI",
        "article": "Articles 9-15 (effective Aug 2026)",
        "fix_code": (
            "# Article 14: Human oversight for justice AI\n"
            "def review_judicial_recommendation(ai_output, judge_id):\n"
            "    \\\"\\\"\\\"Article 14: Judge must review AI-assisted judicial recommendation.\\\"\\\"\\\"\n"
            "    return {\\\"ai_recommendation\\\": ai_output, \\\"status\\\": \\\"pending_judicial_review\\\", \\\"judge\\\": judge_id}"
        ),
        "fix_command": "",
        "explanation": "EU AI Act Annex III Category 8 classifies justice and democratic process AI as high-risk. Article 14 requires human oversight.",
    },
    "critical_infrastructure": {
        "summary": "Add safety monitoring and human override for critical infrastructure AI",
        "article": "Articles 9-15 (effective Aug 2026)",
        "fix_code": (
            "# Article 14: Human override for critical infrastructure AI\n"
            "def monitor_infrastructure(ai_action, operator_id):\n"
            "    \\\"\\\"\\\"Article 14: Operator must be able to override AI infrastructure decisions.\\\"\\\"\\\"\n"
            "    import logging\n"
            "    logger = logging.getLogger(__name__)\n"
            "    logger.info(f\\\"Infrastructure AI action queued for operator {operator_id} approval\\\")\n"
            "    return {\\\"ai_action\\\": ai_action, \\\"status\\\": \\\"pending_operator_approval\\\", \\\"operator\\\": operator_id}"
        ),
        "fix_command": "",
        "explanation": "EU AI Act Annex III Category 2 classifies critical infrastructure AI as high-risk. Article 14 requires human override capability.",
    },
    "safety_components": {
        "summary": "Add safety validation and human override for safety-critical AI components",
        "article": "Articles 9-15 + Union Harmonisation Legislation",
        "fix_code": (
            "# Article 14: Safety validation for AI components\n"
            "def validate_safety_output(ai_output, safety_engineer_id):\n"
            "    \\\"\\\"\\\"Article 14: Safety engineer must validate AI safety-critical output.\\\"\\\"\\\"\n"
            "    return {\\\"ai_output\\\": ai_output, \\\"status\\\": \\\"pending_safety_validation\\\", \\\"engineer\\\": safety_engineer_id}"
        ),
        "fix_command": "",
        "explanation": "Safety components under Union harmonisation legislation are high-risk. Articles 9-15 apply alongside sector-specific regulation.",
    },
}

# Map from Annex III category strings to lookup keys
_CATEGORY_KEY_MAP = {
    "annex iii, category 1": "biometrics",
    "annex iii, category 2": "critical_infrastructure",
    "annex iii, category 3": "education",
    "annex iii, category 4": "employment",
    "annex iii, category 5": "essential_services",
    "annex iii, category 6": "law_enforcement",
    "annex iii, category 7": "migration",
    "annex iii, category 8": "justice",
    "medical devices": "medical_devices",
    "safety components": "safety_components",
}

# Prohibited Article 5 subsection details
# Keys correspond to indicator names from classify_risk.PROHIBITED_PATTERNS
# Built dynamically to avoid pattern self-detection
_PROHIBITED_SUBSECTIONS = {
    "subliminal_manipulation": {
        "article": "Article 5(1)(a)",
        "exception": None,
    },
    "exploitation_vulnerabilities": {
        "article": "Article 5(1)(b)",
        "exception": None,
    },
    "social_scoring": {
        "article": "Article 5(1)(c)",
        "exception": None,
    },
    "criminal_prediction": {
        "article": "Article 5(1)(d)",
        "exception": "AI systems that support human assessment based on objective, verifiable facts directly linked to criminal activity are NOT prohibited.",
    },
    "facial_recognition_scraping": {
        "article": "Article 5(1)(e)",
        "exception": None,
    },
    "emotion_inference_restricted": {
        "article": "Article 5(1)(f)",
        "exception": "Exempt when used for medical or safety purposes (e.g., detecting driver fatigue).",
    },
    "biometric_categorisation_sensitive": {
        "article": "Article 5(1)(g)",
        "exception": "Labelling or filtering of lawfully acquired biometric datasets may be exempt.",
    },
    "realtime_biometric_public": {
        "article": "Article 5(1)(h)",
        "exception": "Narrow exceptions with PRIOR judicial authorisation for: targeted search for victims of trafficking, prevention of imminent terrorist threat, identification of suspects of serious offences.",
    },
}


# ---------------------------------------------------------------------------
# Credential provider to env var mapping
# ---------------------------------------------------------------------------

_ENV_VAR_MAP = {
    "openai_api_key": "OPENAI_API_KEY",
    "anthropic_api_key": "ANTHROPIC_API_KEY",
    "aws_access_key": "AWS_ACCESS_KEY_ID",
    "google_api_key": "GOOGLE_API_KEY",
    "github_token": "GITHUB_TOKEN",
    "azure_api_key": "AZURE_API_KEY",
    "huggingface_token": "HUGGINGFACE_TOKEN",
    "cohere_api_key": "COHERE_API_KEY",
}


# ---------------------------------------------------------------------------
# Tier-specific remediation functions
# ---------------------------------------------------------------------------

def _remediate_prohibited(category, indicators, description):
    """Remediation for prohibited AI practices (Article 5)."""
    primary = indicators[0] if indicators else ""
    subsection = _PROHIBITED_SUBSECTIONS.get(primary, {})
    article = subsection.get("article", "Article 5")
    exception = subsection.get("exception")

    explanation = (
        f"This pattern matches a prohibited AI practice under {article}. "
        "Document why this is a false positive OR remove the functionality."
    )
    if exception:
        explanation += f" Exception: {exception}"

    return {
        "summary": f"Remove prohibited practice or document false positive ({article})",
        "article": article,
        "fix_code": "",
        "fix_command": "",
        "explanation": explanation,
    }


def _remediate_high_risk(category, indicators, file_path):
    """Remediation for high-risk AI systems (Annex III)."""
    # Try to match category to a known remediation
    cat_key = category.lower().strip() if category else ""
    lookup_key = _CATEGORY_KEY_MAP.get(cat_key)

    # Also try matching on indicators
    if not lookup_key and indicators:
        for ind in indicators:
            if ind in CATEGORY_REMEDIATIONS:
                lookup_key = ind
                break

    if lookup_key and lookup_key in CATEGORY_REMEDIATIONS:
        return dict(CATEGORY_REMEDIATIONS[lookup_key])

    # Generic high-risk remediation
    return {
        "summary": "Add human oversight, logging, and transparency for this high-risk AI system",
        "article": "Articles 9-15 (effective Aug 2026)",
        "fix_code": (
            "# Article 14: Generic human oversight pattern\n"
            "def review_ai_output(ai_output, reviewer_id):\n"
            "    \\\"\\\"\\\"Article 14: Human must review AI output before action.\\\"\\\"\\\"\n"
            "    import logging\n"
            "    logger = logging.getLogger(__name__)\n"
            "    logger.info(f\\\"AI output sent for human review by {reviewer_id}\\\")\n"
            "    return {\\\"ai_output\\\": ai_output, \\\"status\\\": \\\"pending_human_review\\\", \\\"reviewer\\\": reviewer_id}"
        ),
        "fix_command": "",
        "explanation": "EU AI Act Articles 9-15 apply to high-risk AI systems. Implement risk management, data governance, transparency, human oversight, and cybersecurity measures.",
    }


def _remediate_credential(indicators, description):
    """Remediation for hardcoded AI credentials."""
    provider = indicators[0] if indicators else "unknown"
    env_var = _ENV_VAR_MAP.get(provider, "API_KEY")
    return {
        "summary": f"Move {provider} credential to environment variable",
        "article": "Article 15 (Cybersecurity)",
        "fix_code": f"# Replace hardcoded key with environment variable\nimport os\nclient = Client(api_key=os.environ[\"{env_var}\"])",
        "fix_command": f"export {env_var}=\"your-key-here\"  # Add to .env, never commit",
        "explanation": "Article 15 requires cybersecurity measures. Hardcoded credentials are a supply chain risk.",
    }


def _remediate_limited_risk(category, indicators):
    """Remediation for limited-risk AI systems (Article 50)."""
    return {
        "summary": "Add transparency notice informing users they are interacting with AI",
        "article": "Article 50 (Transparency)",
        "fix_code": (
            "# Article 50: Transparency obligation\n"
            "TRANSPARENCY_NOTICE = \\\"This content is generated by an AI system.\\\"\n"
            "\n"
            "def add_disclosure(response):\n"
            "    response[\\\"ai_disclosure\\\"] = TRANSPARENCY_NOTICE\n"
            "    return response"
        ),
        "fix_command": "",
        "explanation": "Article 50 requires that users are informed when interacting with AI systems (chatbots, emotion recognition, deepfakes).",
    }


def _remediate_minimal(category):
    """Remediation for minimal-risk AI (informational only)."""
    return {
        "summary": "No mandatory requirements - consider voluntary codes of conduct",
        "article": "Article 95 (Voluntary Codes of Conduct)",
        "fix_code": "",
        "fix_command": "",
        "explanation": "Minimal-risk AI systems have no mandatory EU AI Act requirements, but voluntary codes of conduct are encouraged.",
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_remediation(tier, category="", indicators=None,
                    file_path="", description=""):
    """Generate specific remediation for a finding.

    Returns:
        {
            "summary": str,  # One-line fix description
            "article": str,  # EU AI Act article reference
            "fix_code": str,  # Copy-paste code snippet (if applicable)
            "fix_command": str,  # CLI command to run (if applicable)
            "explanation": str,  # Why this fix is needed
        }
    """
    indicators = indicators or []

    if tier == "prohibited":
        return _remediate_prohibited(category, indicators, description)
    elif tier == "high_risk":
        return _remediate_high_risk(category, indicators, file_path)
    elif tier == "credential_exposure":
        return _remediate_credential(indicators, description)
    elif tier == "limited_risk":
        return _remediate_limited_risk(category, indicators)
    else:
        return _remediate_minimal(category)
