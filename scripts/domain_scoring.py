# regula-ignore
"""
Domain-Aware Confidence Scoring for Regula.

Boosts or reduces confidence based on co-occurrence of AI operations with
regulatory domain keywords. A file that imports an AI library AND contains
employment/credit/medical terminology scores higher than one that just
imports the library.

This is a domain-specific heuristic for EU AI Act risk classification,
not a general-purpose SAST technique. No precision claims are made —
measure with benchmarks/label.py after deployment.
"""

import re
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent))


# ---------------------------------------------------------------------------
# Regulatory domain keyword groups
#
# Each group corresponds to an Annex III high-risk category or Article 5
# prohibited practice. Keywords are chosen to be specific enough to avoid
# matching general programming terms.
# ---------------------------------------------------------------------------

DOMAIN_KEYWORDS = {
    "employment": {
        "keywords": [
            r"\bhir(?:e|ing)\b", r"\brecruit", r"\bresume", r"\bcv\b", r"\bcandidate",
            r"\bapplicant", r"\binterview", r"\bjob.?application",
            r"\bperformance.?review", r"\btermination", r"\bpromotion.?decision",
        ],
        "category": "Annex III, Category 4",
        "boost": 15,
    },
    "finance": {
        "keywords": [
            r"\bcredit.?scor", r"\bcreditworth", r"\bloan", r"\binsurance.?pric",
            r"\bunderwriting", r"\bdefault.?risk", r"\bdebt.?collect",
            r"\bmortgage", r"\bfinancial.?decision",
            r"\bcredit.?risk", r"\bcredit.?assess", r"\bassess.?credit",
            r"\bcredit.?model", r"\bcredit.?predict", r"\bcredit.?decision",
        ],
        "category": "Annex III, Category 5",
        "boost": 15,
    },
    "medical": {
        "keywords": [
            r"\bdiagnos(?:e|is|tic)\b", r"\bpatient", r"\bclinical",
            r"\btreatment", r"\btriage", r"\bmedical", r"\bhealthcare",
            r"\bsymptom", r"\bprescri(?:be|ption)",
        ],
        "category": "Medical Devices",
        "boost": 15,
    },
    "education": {
        "keywords": [
            r"\badmission", r"\bstudent", r"\bexam", r"\bgrade\b", r"\bschool",
            r"\buniversity", r"\benrollment", r"\bscholarship",
        ],
        "category": "Annex III, Category 3",
        "boost": 12,
    },
    "law_enforcement": {
        "keywords": [
            r"\bpolice", r"\blaw.?enforcement", r"\bcriminal", r"\bsuspect",
            r"\bevidence", r"\bsentenc", r"\binvestigation", r"\bsurveillance",
        ],
        "category": "Annex III, Category 6",
        "boost": 15,
    },
    "biometrics": {
        "keywords": [
            r"\bbiometric", r"\bfacial", r"\bface.?recogn", r"\bfingerprint",
            r"\bvoice.?recogn", r"\biris.?scan",
        ],
        "category": "Annex III, Category 1",
        "boost": 15,
    },
    "infrastructure": {
        "keywords": [
            r"\benergy.?grid", r"\bwater.?supply", r"\bpower.?plant",
            r"\btraffic.?control", r"\bscada\b",
        ],
        "category": "Annex III, Category 2",
        "boost": 12,
    },
    "migration": {
        "keywords": [
            r"\basylum", r"\bvisa", r"\bborder.?control", r"\bimmigration",
            r"\brefugee", r"\bdeportation",
        ],
        "category": "Annex III, Category 7",
        "boost": 15,
    },
}

# Pre-compile all domain patterns
_DOMAIN_COMPILED = {
    domain: {
        "patterns": [re.compile(p, re.IGNORECASE) for p in cfg["keywords"]],
        "category": cfg["category"],
        "boost": cfg["boost"],
    }
    for domain, cfg in DOMAIN_KEYWORDS.items()
}


# ---------------------------------------------------------------------------
# Decision function indicators
#
# These suggest the code makes automated decisions (not just predictions).
# Co-occurrence with AI operations → higher regulatory relevance.
# ---------------------------------------------------------------------------

_DECISION_PATTERNS = [
    re.compile(p, re.IGNORECASE) for p in [
        r"\bif\b.*\bpredict", r"\bif\b.*\bscore\b", r"\bif\b.*\bthreshold",
        r"\baccept\b.*\bif\b", r"\breject\b.*\bif\b", r"\bapprove\b.*\bif\b",
        r"\bdeny\b.*\bif\b", r"\bfilter\b.*\bscore\b",
        r"\breturn\b.*\bTrue\b.*\bscore\b", r"\breturn\b.*\bFalse\b.*\bscore\b",
    ]
]


def compute_domain_boost(text: str, has_ai_indicator: bool) -> dict:
    """Compute confidence boost from domain keyword co-occurrence.

    Only applies when AI indicators are present. A file with employment
    keywords but no AI code gets zero boost.

    Returns:
        {
            "boost": int (0-15),
            "domains_matched": [list of matched domain names],
            "has_decision_logic": bool,
            "detail": str (human-readable explanation)
        }
    """
    if not has_ai_indicator:
        return {"boost": 0, "domains_matched": [], "has_decision_logic": False, "detail": ""}

    text_lower = text.lower()
    matched_domains = []
    max_boost = 0

    for domain, cfg in _DOMAIN_COMPILED.items():
        for rx in cfg["patterns"]:
            if rx.search(text_lower):
                matched_domains.append(domain)
                max_boost = max(max_boost, cfg["boost"])
                break  # one match per domain is enough

    # Decision logic detection
    has_decision = any(rx.search(text_lower) for rx in _DECISION_PATTERNS)

    # Boost logic:
    #   0 domains → 0 boost
    #   1 domain → domain boost (12-15)
    #   1+ domains + decision logic → domain boost + 5
    boost = 0
    detail = ""

    if matched_domains:
        boost = max_boost
        detail = f"Domain keywords detected: {', '.join(matched_domains)}"

        if has_decision:
            boost = min(boost + 5, 20)
            detail += " + automated decision logic"

    return {
        "boost": boost,
        "domains_matched": matched_domains,
        "has_decision_logic": has_decision,
        "detail": detail,
    }
