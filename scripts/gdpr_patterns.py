#!/usr/bin/env python3
# regula-ignore
"""GDPR code pattern definitions for dual-compliance scanning.

All patterns are framed as 'indicators that GDPR obligations may apply' —
not violations. This is consistent with Regula's EU AI Act approach.

Validated against: CNIL Developer Guide, EDPB Guidelines 4/2019, IAPP analysis.
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

# Each pattern: (compiled_regex, category, gdpr_articles, description, confidence)
# confidence: "high" (70+), "medium" (50-69), "low" (30-49)

GDPR_PATTERNS = [
    # Art. 5(1)(c) — Data minimisation
    (re.compile(r"(?:user|customer|person|patient|employee|applicant)\w*\s*(?:data|info|details|record)\s*(?:=|\[|\.)", re.IGNORECASE),
     "excessive_data_collection", ["5(1)(c)"], "Personal data variable pattern — verify data minimisation", "medium"),

    # Art. 5(1)(f) — Integrity and confidentiality
    (re.compile(r"(?:password|secret|token|ssn|social_security|national_id|passport)\s*=\s*['\"]", re.IGNORECASE),
     "plaintext_sensitive_data", ["5(1)(f)", "32"], "Sensitive data in plaintext — encryption required", "high"),
    (re.compile(r"(?:log|print|logger|console\.log|puts|fmt\.Print)\s*\(.*(?:email|phone|name|address|ssn|password)", re.IGNORECASE),
     "pii_in_logs", ["5(1)(f)", "32"], "Personal data in log output — potential integrity/confidentiality breach", "high"),

    # Art. 7 — Consent
    (re.compile(r"(?:train|fine.?tune|fit|learn)\s*\(.*(?:user|customer|personal|patient)", re.IGNORECASE),
     "training_without_consent_gate", ["7"], "User data used in training — verify consent basis", "medium"),

    # Art. 9 — Special category data
    (re.compile(r"(?:race|ethnicity|ethnic|religion|religious|political|sexual_orientation|gender_identity|disability|health_status|biometric|genetic)", re.IGNORECASE),
     "special_category_data", ["9"], "Special category data processing — requires explicit consent or Art. 9(2) exception", "high"),

    # Art. 13/14 — Transparency
    (re.compile(r"(?:predict|classify|score|recommend|decide|assess)\s*\(.*(?:user|customer|applicant|patient|employee)", re.IGNORECASE),
     "automated_processing_no_disclosure", ["13", "14"], "Automated processing of personal data — verify transparency provisions", "medium"),

    # Art. 17 — Right to erasure
    (re.compile(r"(?:vector_store|vectordb|chroma|pinecone|weaviate|qdrant|milvus|faiss).*(?:add|insert|upsert|index)", re.IGNORECASE),
     "vector_store_no_deletion", ["17"], "User data stored in vector database — verify deletion capability for right to erasure", "medium"),
    (re.compile(r"(?:embedding|embed)\s*\(.*(?:user|customer|personal|patient|name|email)", re.IGNORECASE),
     "embedding_personal_data", ["17"], "Personal data converted to embeddings — erasure may be technically difficult", "medium"),

    # Art. 22 — Automated decision-making (observation-level only)
    (re.compile(r"(?:if|when|while)\s+(?:model|classifier|predictor|ai|ml)\s*[\.\(].*(?:deny|reject|decline|block|ban|suspend|terminate|approve|grant|accept)", re.IGNORECASE),
     "automated_decision_no_review", ["22"], "AI output directly driving consequential decision — verify Art. 22 compliance (human review required)", "low"),

    # Art. 25 — Privacy by design
    (re.compile(r"(?:request|req|body|form|input|params)\s*[\.\[].*(?:email|phone|name|address|dob|birth|age|gender)\b", re.IGNORECASE),
     "pii_without_validation", ["25"], "Personal data from user input without validation/sanitisation", "medium"),

    # Art. 32 — Security of processing
    (re.compile(r"http://(?!localhost|127\.0\.0\.1|0\.0\.0\.0)", re.IGNORECASE),
     "unencrypted_transport", ["32"], "Unencrypted HTTP transport for data transfer — HTTPS required", "high"),

    # Art. 35 — DPIA triggers
    (re.compile(r"(?:profil|scoring|ranking|rating|classify).*(?:user|customer|citizen|employee|applicant|patient)", re.IGNORECASE),
     "dpia_trigger_profiling", ["35"], "Profiling/scoring of individuals — DPIA likely required", "medium"),
    (re.compile(r"(?:surveillance|monitor|track|observe).*(?:user|employee|citizen|person|individual|worker)", re.IGNORECASE),
     "dpia_trigger_monitoring", ["35"], "Systematic monitoring of individuals — DPIA likely required", "medium"),

    # Art. 44-49 — Cross-border transfers (low-confidence observation)
    (re.compile(r"(?:api\.openai\.com|api\.anthropic\.com|api\.cohere\.ai|api\.mistral\.ai|generativelanguage\.googleapis\.com)", re.IGNORECASE),
     "cross_border_transfer", ["44-49"], "Data sent to non-EU API endpoint — verify transfer safeguards (adequacy decision, SCCs, or DPF). Note: this is a low-confidence indicator; endpoint routing may differ at runtime.", "low"),
]

# Dual-compliance hotspots: patterns where BOTH GDPR and EU AI Act apply.
# Validated by IAPP, EDPB, DLA Piper.
DUAL_COMPLIANCE_HOTSPOTS = {
    "automated_decision_no_review": {
        "gdpr": ["22"],
        "ai_act": ["14"],
        "description": "Automated decision-making requires human oversight under both GDPR Art. 22 and AI Act Art. 14",
    },
    "special_category_data": {
        "gdpr": ["9"],
        "ai_act": ["10"],
        "description": "Special category data in AI systems triggers both GDPR Art. 9 and AI Act Art. 10 data governance",
    },
    "dpia_trigger_profiling": {
        "gdpr": ["35"],
        "ai_act": ["27"],
        "description": "AI-based profiling triggers both GDPR Art. 35 DPIA and AI Act Art. 27 FRIA",
    },
    "dpia_trigger_monitoring": {
        "gdpr": ["35"],
        "ai_act": ["27"],
        "description": "AI-based monitoring triggers both GDPR Art. 35 DPIA and AI Act Art. 27 FRIA",
    },
}

# Lifecycle phases for GDPR patterns
GDPR_LIFECYCLE_PHASES = {
    "excessive_data_collection": ["design", "develop"],
    "plaintext_sensitive_data": ["develop", "deploy"],
    "pii_in_logs": ["develop", "operate"],
    "training_without_consent_gate": ["develop"],
    "special_category_data": ["plan", "develop"],
    "automated_processing_no_disclosure": ["develop", "deploy"],
    "vector_store_no_deletion": ["develop"],
    "embedding_personal_data": ["develop"],
    "automated_decision_no_review": ["develop", "operate"],
    "pii_without_validation": ["develop"],
    "unencrypted_transport": ["deploy"],
    "dpia_trigger_profiling": ["plan", "develop"],
    "dpia_trigger_monitoring": ["plan", "develop"],
    "cross_border_transfer": ["deploy"],
}
