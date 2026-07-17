# regula-ignore — domain gating keyword lists ARE the employment, justice, and other domain vocabulary being gated
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
            r"\bhir(?:e|ing)\b", r"\brecruit", r"\bresume", r"\bcv\b",
            r"\bapplicant", r"\binterview", r"\bjob.?application",
            r"\bperformance.?review", r"\bpromotion.?decision",
        ],
        # Suppress employment domain when file is clearly compute/ML context
        "exclude_if": [
            r"\bimport\s+(?:multiprocessing|subprocess|celery|ray|dask|threading|joblib)",
            r"\bfrom\s+(?:multiprocessing|subprocess|celery|ray|dask|threading|concurrent\.futures|joblib)\b",
            r"\bProcessPoolExecutor\b", r"\bThreadPoolExecutor\b",
            r"\bmp\.Process\b", r"\bworker_process\b",
            r"\bthreading\.Thread\b", r"\bconcurrent\.futures\b",
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
        # Suppress finance domain when file is a quantitative/backtesting library
        "exclude_if": [
            r"\b(?:backtrader|zipline|quantlib|ta[\-_]lib|pyalgotrading)\b",
            r"\b(?:yfinance|alpha_vantage|polygon_io)\b",
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
        # Suppress medical domain when file is a medical-imaging or computational-biology library
        "exclude_if": [
            r"\b(?:monai|nibabel|simpleitk|torchio|medpy|pydicom)\b",
            r"\b(?:biopython|rdkit|openbabel)\b",
        ],
        "category": "Medical Devices",
        "boost": 15,
    },
    "education": {
        "keywords": [
            r"\badmission", r"\bstudent", r"\bexam", r"\bgrade\b", r"\bschool",
            r"\buniversity", r"\benrollment", r"\bscholarship",
        ],
        # Suppress education domain when file is a tutorial/notebook context
        "exclude_if": [
            r"\b(?:jupyter|nbformat|notebook|tutorial_?\w+)\b",
        ],
        "category": "Annex III, Category 3",
        "boost": 12,
    },
    "law_enforcement": {
        "keywords": [
            r"\bpolice", r"\blaw.?enforcement", r"\bcriminal", r"\bsuspect",
            r"\bevidence", r"\bsentenc", r"\binvestigation", r"\bsurveillance",
        ],
        # Suppress law_enforcement domain when file is a gaming/fiction context
        "exclude_if": [
            r"\b(?:pygame|unity|godot|unreal|game_engine)\b",
        ],
        "category": "Annex III, Category 6",
        "boost": 15,
    },
    "biometrics": {
        "keywords": [
            r"\bbiometric", r"\bfacial", r"\bface.?recogn", r"\bfingerprint",
            r"\bvoice.?recogn", r"\biris.?scan",
        ],
        # Suppress biometrics domain when file is a speech/audio processing library
        "exclude_if": [
            r"\b(?:lhotse|speechbrain|espnet|librosa|pyaudioanalysis)\b",
        ],
        "category": "Annex III, Category 1",
        "boost": 15,
    },
    "infrastructure": {
        "keywords": [
            r"\benergy.?grid", r"\bwater.?supply", r"\bpower.?plant",
            r"\btraffic.?control", r"\bscada\b",
        ],
        # Suppress infrastructure domain when file is infra-as-code/DevOps tooling
        "exclude_if": [
            r"\b(?:terraform|ansible|puppet|chef|kubernetes|docker|podman)\b",
        ],
        "category": "Annex III, Category 2",
        "boost": 12,
    },
    "migration": {
        "keywords": [
            r"\basylum", r"\bvisa", r"\bborder.?control", r"\bimmigration",
            r"\brefugee", r"\bdeportation",
        ],
        # Suppress migration domain when file is a database migration tool
        "exclude_if": [
            r"\b(?:alembic|django\.db|flask_migrate|flyway|liquibase)\b",
        ],
        "category": "Annex III, Category 7",
        "boost": 15,
    },
}

# Pre-compile all domain patterns
_DOMAIN_COMPILED = {
    domain: {
        "patterns": [re.compile(p, re.IGNORECASE) for p in cfg["keywords"]],
        "excludes": [re.compile(p, re.IGNORECASE) for p in cfg.get("exclude_if", [])],
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


# Regulated domains where findings become critical
REGULATED_DOMAINS = {
    "creditworthiness", "employment", "insurance", "education", "legal",
    "law_enforcement", "migration", "biometric", "medical",
}

# Non-regulated domains where findings are informational
INFORMATIONAL_DOMAINS = {
    "customer_support", "internal_tooling", "content_generation", "general_purpose",
}


def project_declared_domains(project_dir) -> set:
    """system.domain declared in the TARGET project's own policy file.

    Reads regula-policy.yaml/.json inside project_dir explicitly — not
    the CWD-based policy cache — so scanning another directory sees that
    project's declaration. This is what makes `system.domain` activate
    domain-gated patterns everywhere a project is scanned: doctor and
    the consultant guide have documented that behaviour, but until
    16 Jul 2026 only the `--domain` flag actually activated anything
    (the policy declaration fed the confidence boost path only).
    """
    from pathlib import Path as _Path
    try:
        from policy_config import get_policy
        for name in ("regula-policy.yaml", "regula-policy.json"):
            p = _Path(project_dir) / name
            if p.exists():
                system = get_policy(str(p)).get("system", {})
                if isinstance(system, dict) and system.get("domain"):
                    return {str(system["domain"]).strip().lower()}
                break
    except Exception:
        pass
    return set()


def get_declared_domain() -> dict:
    """Read domain declaration from regula-policy.yaml.

    Returns: {"domain": str, "risk_level": str, "name": str, "is_regulated": bool}
    """
    try:
        from policy_config import get_policy
        policy = get_policy()
        system = policy.get("system", {})
        if not isinstance(system, dict):
            return {"domain": "general_purpose", "risk_level": "", "name": "", "is_regulated": False}
        domain = system.get("domain", "general_purpose") or "general_purpose"
        return {
            "domain": domain,
            "risk_level": system.get("risk_level", "") or "",
            "name": system.get("name", "") or "",
            "is_regulated": domain in REGULATED_DOMAINS,
        }
    except Exception:
        return {"domain": "general_purpose", "risk_level": "", "name": "", "is_regulated": False}


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

    # Check declared domain from policy — overrides keyword detection
    declared = get_declared_domain()
    if declared["is_regulated"] and declared["domain"]:
        # Map declared domain to our internal domain names
        domain_map = {
            "creditworthiness": "finance", "employment": "employment",
            "insurance": "finance", "education": "education",
            "legal": "law_enforcement", "law_enforcement": "law_enforcement",
            "migration": "migration", "biometric": "biometrics",
            "medical": "medical",
        }
        mapped = domain_map.get(declared["domain"])
        if mapped and mapped in _DOMAIN_COMPILED:
            cfg = _DOMAIN_COMPILED[mapped]
            return {
                "boost": cfg["boost"],
                "domains_matched": [mapped],
                "has_decision_logic": False,
                "detail": f"Declared domain: {declared['domain']} (from regula-policy.yaml)",
            }

    text_lower = text.lower()
    matched_domains = []
    max_boost = 0

    for domain, cfg in _DOMAIN_COMPILED.items():
        # Check exclusion patterns first — if any exclude pattern matches,
        # skip this domain entirely. This prevents compute "worker" contexts
        # from triggering employment domain.
        excluded = any(rx.search(text_lower) for rx in cfg.get("excludes", []))
        if excluded:
            continue
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
