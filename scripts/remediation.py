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
    # nosec B105 — these are env VAR NAMES (not secret values) that Regula
    # recommends users switch TO when it detects hardcoded credentials.
    # Bandit pattern-matches on "*_TOKEN" / "*_KEY" string literals and
    # false-positives on this entire dict.
    "openai_api_key": "OPENAI_API_KEY",         # nosec B105
    "anthropic_api_key": "ANTHROPIC_API_KEY",    # nosec B105
    "aws_access_key": "AWS_ACCESS_KEY_ID",       # nosec B105
    "google_api_key": "GOOGLE_API_KEY",          # nosec B105
    "github_token": "GITHUB_TOKEN",              # nosec B105
    "azure_api_key": "AZURE_API_KEY",            # nosec B105
    "huggingface_token": "HUGGINGFACE_TOKEN",    # nosec B105
    "cohere_api_key": "COHERE_API_KEY",          # nosec B105
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
# AI Security pattern remediations (OWASP LLM Top 10)
# ---------------------------------------------------------------------------

_AI_SECURITY_REMEDIATIONS = {
    "prompt_injection_vulnerable": {
        "summary": "Sanitise user input before including in LLM prompts",
        "article": "Article 15 (Cybersecurity) + OWASP LLM01",
        "fix_code": (
            "# Suggested fix: Sanitise user input before including in prompts\n"
            "import re\n"
            "\n"
            "MAX_INPUT_LENGTH = 2000\n"
            "\n"
            "def sanitise_prompt_input(user_input: str) -> str:\n"
            "    \"\"\"Strip injection markers and enforce length limit.\"\"\"\n"
            "    # Remove common injection patterns\n"
            "    cleaned = re.sub(\n"
            "        r'(?i)(ignore\\s+(?:previous|above|all)\\s+instructions|'  # instruction override\n"
            "        r'you\\s+are\\s+now|act\\s+as|pretend\\s+to|'              # role hijacking\n"
            "        r'system\\s*:\\s*|\\[INST\\]|<\\|im_start\\|>)',            # format markers\n"
            "        '', user_input\n"
            "    )\n"
            "    return cleaned[:MAX_INPUT_LENGTH]\n"
            "\n"
            "# Use structured prompt templates instead of string concatenation:\n"
            "# BAD:  prompt = f\"Analyse this: {user_input}\"\n"
            "# GOOD: prompt = template.format(content=sanitise_prompt_input(user_input))"
        ),
        "fix_command": "",
        "explanation": (
            "Article 15 requires cybersecurity measures for AI systems. "
            "Direct string concatenation of user input into LLM prompts enables "
            "prompt injection attacks (OWASP LLM01:2025). Use structured prompt "
            "templates with input sanitisation."
        ),
    },
    "prompt_injection_indirect": {
        "summary": "Validate external content before passing to LLM",
        "article": "Article 15 (Cybersecurity) + OWASP LLM01",
        "fix_code": (
            "# Suggested fix: Validate external content before LLM ingestion\n"
            "def sanitise_external_content(content: str, source: str) -> str:\n"
            "    \"\"\"Strip potential injection payloads from fetched content.\"\"\"\n"
            "    import re\n"
            "    # Remove hidden text / zero-width chars used for indirect injection\n"
            "    cleaned = re.sub(r'[\\u200b-\\u200f\\u2028-\\u202f\\ufeff]', '', content)\n"
            "    # Truncate to prevent context flooding\n"
            "    MAX_EXTERNAL_LENGTH = 4000\n"
            "    return cleaned[:MAX_EXTERNAL_LENGTH]"
        ),
        "fix_command": "",
        "explanation": (
            "Fetching external content (web pages, files, tool output) and passing it "
            "directly to an LLM enables indirect prompt injection. Validate and truncate "
            "external content before inclusion. OWASP LLM01:2025."
        ),
    },
    "prompt_injection_agentic": {
        "summary": "Treat tool/agent output as untrusted input",
        "article": "Article 15 (Cybersecurity) + OWASP LLM01 / ASI04",
        "fix_code": (
            "# Suggested fix: Validate tool output before returning to LLM\n"
            "import json\n"
            "\n"
            "def validate_tool_output(output, expected_schema: dict) -> dict:\n"
            "    \"\"\"Validate tool output structure before feeding back to LLM.\"\"\"\n"
            "    if isinstance(output, str):\n"
            "        try:\n"
            "            output = json.loads(output)\n"
            "        except json.JSONDecodeError:\n"
            "            return {\"error\": \"Invalid tool output format\", \"raw_truncated\": output[:500]}\n"
            "    # Strip any instruction-like content from string values\n"
            "    for key, val in output.items():\n"
            "        if isinstance(val, str) and len(val) > 5000:\n"
            "            output[key] = val[:5000]\n"
            "    return output"
        ),
        "fix_command": "",
        "explanation": (
            "Tool and agent outputs can contain adversarial content that hijacks "
            "the LLM control flow (OWASP ASI04). Validate structure and truncate "
            "outputs before returning them to the model."
        ),
    },
    "no_output_validation": {
        "summary": "Validate AI model output before use — never eval/exec",
        "article": "Article 15 (Cybersecurity) + OWASP LLM02",
        "fix_code": (
            "# Suggested fix: Validate AI model output before use\n"
            "import ast\n"
            "\n"
            "MAX_OUTPUT_LENGTH = 10000\n"
            "\n"
            "def validate_ai_output(response):\n"
            "    \"\"\"Validate and sanitise AI model output before use.\"\"\"\n"
            "    if not response or not isinstance(response, str):\n"
            "        raise ValueError(\"Empty or invalid AI response\")\n"
            "    if len(response) > MAX_OUTPUT_LENGTH:\n"
            "        response = response[:MAX_OUTPUT_LENGTH]\n"
            "    return response\n"
            "\n"
            "# If you need to parse AI-generated code, use ast.literal_eval (not eval):\n"
            "# BAD:  result = eval(ai_response)\n"
            "# GOOD: result = ast.literal_eval(ai_response)  # only parses literals"
        ),
        "fix_command": "",
        "explanation": (
            "Using eval() or exec() on AI model output enables arbitrary code execution. "
            "Article 15 requires cybersecurity measures. Validate output type, length, "
            "and structure before use. Use ast.literal_eval() for safe parsing of "
            "literal expressions. OWASP LLM02:2025."
        ),
    },
    "unsafe_model_deserialization": {
        "summary": "Use safe model loading — never unpickle untrusted files",
        "article": "Article 15 (Cybersecurity) + OWASP LLM05",
        "fix_code": (
            "# Suggested fix: Use safe model loading\n"
            "# BAD:  model = torch.load('model.pt')\n"
            "# GOOD: model = torch.load('model.pt', weights_only=True)\n"
            "# BEST: Use safetensors format\n"
            "from safetensors.torch import load_file\n"
            "model_weights = load_file('model.safetensors')"
        ),
        "fix_command": "pip install safetensors",
        "explanation": (
            "Pickle-based model files can execute arbitrary code on load. "
            "Use safetensors format or torch.load(weights_only=True). "
            "OWASP LLM05:2025."
        ),
    },
    "unbounded_token_generation": {
        "summary": "Set explicit token limits on LLM API calls",
        "article": "Article 15 (Cybersecurity) + OWASP LLM10",
        "fix_code": (
            "# Suggested fix: Set reasonable token limits\n"
            "response = client.chat.completions.create(\n"
            "    model=model_name,\n"
            "    messages=messages,\n"
            "    max_tokens=4096,  # Set an appropriate limit for your use case\n"
            ")"
        ),
        "fix_command": "",
        "explanation": (
            "Unbounded token generation enables denial-of-service and excessive "
            "resource consumption. Set max_tokens to a reasonable limit. OWASP LLM10:2025."
        ),
    },
    "no_error_handling_ai_call": {
        "summary": "Add error handling around AI API calls",
        "article": "Article 15 (Cybersecurity) + OWASP LLM06",
        "fix_code": (
            "# Suggested fix: Wrap AI API calls in error handling\n"
            "import logging\n"
            "\n"
            "logger = logging.getLogger(__name__)\n"
            "\n"
            "try:\n"
            "    response = client.chat.completions.create(\n"
            "        model=model_name,\n"
            "        messages=messages,\n"
            "        max_tokens=4096,\n"
            "        timeout=30,\n"
            "    )\n"
            "except (TimeoutError, ConnectionError) as e:\n"
            "    logger.error(\"AI API call failed: %s\", e)\n"
            "    response = None  # Handle gracefully\n"
            "except Exception as e:\n"
            "    logger.exception(\"Unexpected error in AI API call\")\n"
            "    raise"
        ),
        "fix_command": "",
        "explanation": (
            "Unhandled AI API errors can cause cascading failures and expose "
            "internal state. Add try/except with logging. OWASP LLM06:2025."
        ),
    },
    "exposed_api_key_env": {
        "summary": "Remove hardcoded API key — use environment variables",
        "article": "Article 15 (Cybersecurity) + OWASP LLM06",
        "fix_code": (
            "# Suggested fix: Use environment variables for API keys\n"
            "import os\n"
            "\n"
            "api_key = os.environ[\"OPENAI_API_KEY\"]  # Set in .env, never commit\n"
            "client = OpenAI(api_key=api_key)"
        ),
        "fix_command": "",
        "explanation": (
            "Hardcoded API keys in source code are a supply chain risk. "
            "Use environment variables and .env files (excluded from version control)."
        ),
    },
    "excessive_agent_autonomy": {
        "summary": "Add human approval gate for agent actions",
        "article": "Article 14 (Human oversight) + OWASP LLM06",
        "fix_code": (
            "# Suggested fix: Add human-in-the-loop for agent tool use\n"
            "def execute_tool(tool_name: str, tool_args: dict, auto_approve: bool = False):\n"
            "    \"\"\"Article 14: Require approval for high-impact agent actions.\"\"\"\n"
            "    HIGH_IMPACT_TOOLS = {\"write_file\", \"delete\", \"execute\", \"send_email\"}\n"
            "    if tool_name in HIGH_IMPACT_TOOLS and not auto_approve:\n"
            "        print(f\"Agent wants to run: {tool_name}({tool_args})\")\n"
            "        if input(\"Approve? [y/N] \").lower() != 'y':\n"
            "            return {\"status\": \"denied_by_human\"}\n"
            "    return run_tool(tool_name, tool_args)"
        ),
        "fix_command": "",
        "explanation": (
            "Auto-executing agent actions without human review violates Article 14 "
            "human oversight requirements. Add approval gates for high-impact operations."
        ),
    },
    "hardcoded_model_path": {
        "summary": "Use model registries with integrity verification",
        "article": "Article 15 (Cybersecurity) + OWASP LLM03",
        "fix_code": (
            "# Suggested fix: Use model registry with pinned revision\n"
            "import os\n"
            "\n"
            "MODEL_NAME = os.environ.get('MODEL_NAME', 'your-org/your-model')\n"
            "MODEL_REVISION = os.environ.get('MODEL_REVISION', 'main')\n"
            "\n"
            "model = AutoModel.from_pretrained(\n"
            "    MODEL_NAME,\n"
            "    revision=MODEL_REVISION,  # Pin to specific commit\n"
            ")"
        ),
        "fix_command": "",
        "explanation": (
            "Loading models from hardcoded URLs or temp paths is a supply chain risk. "
            "Use model registries (HuggingFace Hub, MLflow) and pin revisions. OWASP LLM03:2025."
        ),
    },
}

# ---------------------------------------------------------------------------
# Governance observation remediations (absence-based findings)
# ---------------------------------------------------------------------------

_OBSERVATION_REMEDIATIONS = {
    "no_logging": {
        "summary": "Add audit logging around AI model calls",
        "article": "Article 12 (Record-keeping)",
        "fix_code": (
            "# Suggested fix: Add logging around AI model calls\n"
            "import logging\n"
            "from datetime import datetime, timezone\n"
            "\n"
            "logger = logging.getLogger(\"ai_audit\")\n"
            "\n"
            "def log_ai_inference(model_name: str, input_summary: str, output_summary: str):\n"
            "    \"\"\"Article 12: Record AI system events for traceability.\"\"\"\n"
            "    logger.info(\n"
            "        \"AI inference\",\n"
            "        extra={\n"
            "            \"model\": model_name,\n"
            "            \"timestamp\": datetime.now(timezone.utc).isoformat(),\n"
            "            \"input_hash\": hash(input_summary),\n"
            "            \"output_length\": len(output_summary),\n"
            "        },\n"
            "    )\n"
            "\n"
            "# Configure structured logging for audit trail:\n"
            "logging.basicConfig(\n"
            "    level=logging.INFO,\n"
            "    format='%(asctime)s %(name)s %(levelname)s %(message)s',\n"
            ")"
        ),
        "fix_command": "",
        "explanation": (
            "Article 12 requires high-risk AI systems to have automatic recording "
            "of events (logging) to ensure traceability. Log model inputs, outputs, "
            "timestamps, and version identifiers."
        ),
    },
    "missing_fairness_evaluation": {
        "summary": "Add fairness evaluation before deployment",
        "article": "Article 10(5) (Data governance — bias examination)",
        "fix_code": (
            "# Suggested fix: Add fairness evaluation before deployment\n"
            "# Option 1: Use fairlearn (pip install fairlearn)\n"
            "from fairlearn.metrics import MetricFrame, selection_rate\n"
            "\n"
            "def evaluate_fairness(y_true, y_pred, sensitive_features):\n"
            "    \"\"\"Article 10(5): Examine training data for biases.\"\"\"\n"
            "    metric_frame = MetricFrame(\n"
            "        metrics=selection_rate,\n"
            "        y_true=y_true,\n"
            "        y_pred=y_pred,\n"
            "        sensitive_features=sensitive_features,\n"
            "    )\n"
            "    print(\"Selection rate by group:\")\n"
            "    print(metric_frame.by_group)\n"
            "    print(f\"Ratio: {metric_frame.ratio()}\")\n"
            "    return metric_frame\n"
            "\n"
            "# Option 2: Manual disparate impact check\n"
            "def disparate_impact_ratio(y_pred, protected_attr):\n"
            "    \"\"\"Check if selection rate ratio exceeds 80% threshold.\"\"\"\n"
            "    groups = set(protected_attr)\n"
            "    rates = {}\n"
            "    for g in groups:\n"
            "        mask = [a == g for a in protected_attr]\n"
            "        rates[g] = sum(p for p, m in zip(y_pred, mask) if m) / sum(mask)\n"
            "    min_rate = min(rates.values())\n"
            "    max_rate = max(rates.values())\n"
            "    return min_rate / max_rate if max_rate > 0 else 0.0"
        ),
        "fix_command": "pip install fairlearn  # or: pip install aif360",
        "explanation": (
            "Article 10(5) requires training data to be examined for possible biases "
            "that could lead to prohibited discrimination. Protected class attributes "
            "were detected as model features without fairness evaluation. Use fairlearn, "
            "AIF360, or manual disparate impact analysis."
        ),
    },
    "automated_decision": {
        "summary": "Add transparency documentation for automated decisions",
        "article": "Article 13 (Transparency)",
        "fix_code": (
            "# Suggested fix: Document automated decision capabilities\n"
            "DECISION_TRANSPARENCY = {\n"
            "    \"system_description\": \"[Describe what this AI system does]\",\n"
            "    \"capabilities\": \"[List what it can and cannot do]\",\n"
            "    \"limitations\": \"[Known limitations and failure modes]\",\n"
            "    \"human_oversight\": \"[How a human can review/override decisions]\",\n"
            "}"
        ),
        "fix_command": "regula model-card --project .",
        "explanation": (
            "Article 13 requires transparency to deployers about AI system capabilities "
            "and limitations. Document what the system does, its known limitations, "
            "and how human oversight is exercised."
        ),
    },
}


def _remediate_ai_security(category, indicators):
    """Remediation for AI security findings (OWASP LLM Top 10)."""
    # Try to match by indicator name first
    for ind in (indicators or []):
        if ind in _AI_SECURITY_REMEDIATIONS:
            return dict(_AI_SECURITY_REMEDIATIONS[ind])

    # Generic security remediation
    return {
        "summary": "Review and remediate AI security antipattern",
        "article": "Article 15 (Cybersecurity)",
        "fix_code": "",
        "fix_command": "",
        "explanation": (
            "Article 15 requires appropriate cybersecurity measures for AI systems. "
            "Review the flagged pattern and apply the remediation from the OWASP LLM "
            "Top 10 guidance."
        ),
    }


def remediate_observation(observation_key):
    """Remediation for governance observations (absence-based findings).

    Returns a remediation dict or None if no specific remediation exists.
    """
    return dict(_OBSERVATION_REMEDIATIONS[observation_key]) if observation_key in _OBSERVATION_REMEDIATIONS else None


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
    elif tier == "ai_security":
        return _remediate_ai_security(category, indicators)
    elif tier == "credential_exposure":
        return _remediate_credential(indicators, description)
    elif tier == "limited_risk":
        return _remediate_limited_risk(category, indicators)
    else:
        return _remediate_minimal(category)
