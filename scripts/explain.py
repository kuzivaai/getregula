# regula-ignore
"""
Regula Explainable Classification Engine

Produces human-readable explanations for risk classifications:
- WHY a pattern matched (file:line, legal basis, false positive guidance)
- Obligation roadmap with effort estimates
- Provider vs deployer determination
"""

import re
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from risk_types import RiskTier, Classification
from risk_patterns import (
    PROHIBITED_PATTERNS, HIGH_RISK_PATTERNS, LIMITED_RISK_PATTERNS,
    AI_INDICATORS,
)
from classify_risk import strip_comments


# ---------------------------------------------------------------------------
# Article obligations (loaded once from YAML, with pure-Python fallback)
# ---------------------------------------------------------------------------

_OBLIGATIONS = None


def _reset_obligations_cache():
    """Clear the obligations cache (used by tests)."""
    global _OBLIGATIONS
    _OBLIGATIONS = None


def _load_obligations() -> dict:
    """Load article obligations from YAML reference file.

    Uses a simple line-by-line YAML parser (no PyYAML dependency).
    Falls back to a built-in minimal set if the file is missing.
    """
    global _OBLIGATIONS
    if _OBLIGATIONS is not None:
        return _OBLIGATIONS

    yaml_path = Path(__file__).parent.parent / "references" / "article_obligations.yaml"
    if yaml_path.exists():
        from policy_config import _parse_yaml_fallback
        try:
            data = _parse_yaml_fallback(yaml_path.read_text(encoding="utf-8"))
            _OBLIGATIONS = data
            return _OBLIGATIONS
        except Exception:
            pass  # YAML parse failure — fall through to built-in defaults

    # Built-in fallback — minimal obligation data
    _OBLIGATIONS = {"articles": {
        "9":  {"title": "Risk Management System", "short": "Risk management",
               "effort_hours": [40, 60], "priority": "HIGH"},
        "10": {"title": "Data and Data Governance", "short": "Data governance",
               "effort_hours": [24, 80], "priority": "HIGH"},
        "11": {"title": "Technical Documentation", "short": "Technical docs",
               "effort_hours": [40, 80], "priority": "MED"},
        "12": {"title": "Record-Keeping", "short": "Logging",
               "effort_hours": [8, 16], "priority": "HIGH"},
        "13": {"title": "Transparency and Information to Deployers", "short": "Transparency",
               "effort_hours": [16, 24], "priority": "MED"},
        "14": {"title": "Human Oversight", "short": "Human oversight",
               "effort_hours": [16, 24], "priority": "HIGH"},
        "15": {"title": "Accuracy, Robustness, and Cybersecurity", "short": "Accuracy & security",
               "effort_hours": [16, 40], "priority": "HIGH"},
    }}
    return _OBLIGATIONS


# ---------------------------------------------------------------------------
# Line-level pattern matching
# ---------------------------------------------------------------------------

def find_pattern_matches(text: str, language: str = "python") -> list:
    """Find all risk pattern matches with line numbers and context.

    Returns a list of dicts:
        pattern_name, category, line, matched_text, legal_basis,
        false_positive_if, description
    """
    stripped = strip_comments(text, language)
    stripped_lower = stripped.lower()
    lines = stripped.split("\n")
    matches = []

    # Check prohibited patterns (one match per pattern name)
    for name, cfg in PROHIBITED_PATTERNS.items():
        found = False
        for pattern in cfg["patterns"]:
            if found:
                break
            rx = re.compile(pattern)
            for i, line in enumerate(lines, 1):
                if rx.search(line.lower()):
                    matches.append({
                        "pattern_name": name,
                        "tier": "prohibited",
                        "category": "Prohibited (Article 5)",
                        "line": i,
                        "matched_text": line.strip()[:120],
                        "legal_basis": f"Article {cfg['article']}",
                        "description": cfg["description"],
                        "conditions": cfg.get("conditions", ""),
                        "false_positive_if": cfg.get("exceptions") or "Pattern appears in comments or documentation, not in executable code",
                    })
                    found = True
                    break

    # Check high-risk patterns (one match per pattern name)
    for name, cfg in HIGH_RISK_PATTERNS.items():
        found = False
        for pattern in cfg["patterns"]:
            if found:
                break
            rx = re.compile(pattern)
            for i, line in enumerate(lines, 1):
                if rx.search(line.lower()):
                    _fp_guidance = _high_risk_false_positive_guidance(name)
                    matches.append({
                        "pattern_name": name,
                        "tier": "high_risk",
                        "category": cfg["category"],
                        "line": i,
                        "matched_text": line.strip()[:120],
                        "legal_basis": f"Annex III — Articles {', '.join(cfg['articles'])}",
                        "description": cfg["description"],
                        "conditions": "",
                        "false_positive_if": _fp_guidance,
                    })
                    found = True
                    break

    # Check limited-risk patterns (one match per pattern name)
    for name, cfg in LIMITED_RISK_PATTERNS.items():
        found = False
        for pattern in cfg["patterns"]:
            if found:
                break
            rx = re.compile(pattern)
            for i, line in enumerate(lines, 1):
                if rx.search(line.lower()):
                    matches.append({
                        "pattern_name": name,
                        "tier": "limited_risk",
                        "category": "Limited Risk (Article 50)",
                        "line": i,
                        "matched_text": line.strip()[:120],
                        "legal_basis": f"Article {cfg['article']}",
                        "description": cfg["description"],
                        "conditions": "",
                        "false_positive_if": "System does not interact with end users or generate content presented as human-made",
                    })
                    found = True
                    break

    return matches


def _high_risk_false_positive_guidance(pattern_name: str) -> str:
    """Return false-positive guidance for a high-risk pattern."""
    guidance = {
        "employment": "Function does not influence hiring, promotion, or termination decisions",
        "essential_services": "Function does not determine access to credit, insurance, or benefits",
        "education": "Function does not determine admissions, grades, or exam outcomes",
        "biometrics": "Function does not identify or categorise natural persons by biometric data",
        "critical_infrastructure": "Function does not manage energy, water, or traffic systems",
        "law_enforcement": "Function does not assist in criminal investigations or evidence assessment",
        "migration": "Function does not process visa, asylum, or border control decisions",
        "justice": "Function does not influence judicial decisions or democratic processes",
        "medical_devices": "Function does not provide clinical decisions or patient triage",
        "safety_components": "Function does not control safety-critical vehicle or machinery behaviour",
    }
    default = "Pattern appears in documentation or test code, not in a decision-making pipeline"
    return guidance.get(pattern_name, default)


# ---------------------------------------------------------------------------
# Provider vs deployer detection
# ---------------------------------------------------------------------------

_PROVIDER_PATTERNS = [
    (r"\bmodel\.fit\b", "model training (model.fit)"),
    (r"\bmodel\.train\b", "model training (model.train)"),
    (r"\bTrainer\s*\(", "HuggingFace Trainer"),
    (r"\bfine.?tun", "fine-tuning"),
    (r"\bpeft\b|\blora\b|\bLoraConfig\b", "parameter-efficient fine-tuning (PEFT/LoRA)"),
    (r"\bnn\.Module\b", "custom PyTorch model definition"),
    (r"\btf\.keras\.Model\b|\bkeras\.Model\b", "custom Keras model definition"),
    (r"\bDataLoader\b.*train", "training DataLoader"),
    (r"\bsave_pretrained\b", "model export (save_pretrained)"),
    (r"\btorch\.save\b", "model serialisation (torch.save)"),
    (r"\boptuna\b|\bray\.tune\b|\bgrid_search\b", "hyperparameter tuning"),
    (r"\bwandb\.init\b|\bmlflow\.start_run\b", "experiment tracking"),
]

_DEPLOYER_PATTERNS = [
    (r"(?:from\s+openai|import\s+openai|OpenAI\s*\()", "OpenAI API usage"),
    (r"chat\.completions\.create", "OpenAI chat completions API"),
    (r"(?:from\s+anthropic|import\s+anthropic|Anthropic\s*\()", "Anthropic API usage"),
    (r"messages\.create", "Anthropic messages API"),
    (r"litellm\.completion", "LiteLLM API wrapper"),
    (r"langchain", "LangChain framework (typically deployer)"),
    (r"\bpipeline\s*\(\s*['\"]", "HuggingFace pipeline (inference)"),
    (r"from_pretrained\b(?!.*\.train)", "pre-trained model loading"),
    (r"model\.predict\b", "inference-only usage (model.predict)"),
    (r"model\.generate\b", "inference-only usage (model.generate)"),
]

_PROVIDER_COMPILED = [(re.compile(p, re.IGNORECASE), desc) for p, desc in _PROVIDER_PATTERNS]
_DEPLOYER_COMPILED = [(re.compile(p, re.IGNORECASE), desc) for p, desc in _DEPLOYER_PATTERNS]


def detect_provider_deployer(text: str) -> dict:
    """Detect whether the code is from a PROVIDER or DEPLOYER of the AI system.

    Returns:
        {
            "role": "provider" | "deployer" | "unclear",
            "confidence": "high" | "medium" | "low",
            "evidence": [list of matched indicators],
            "note": str
        }
    """
    provider_evidence = []
    deployer_evidence = []

    for rx, desc in _PROVIDER_COMPILED:
        if rx.search(text):
            provider_evidence.append(desc)

    for rx, desc in _DEPLOYER_COMPILED:
        if rx.search(text):
            deployer_evidence.append(desc)

    p_count = len(provider_evidence)
    d_count = len(deployer_evidence)

    if p_count > 0 and d_count == 0:
        return {
            "role": "provider",
            "confidence": "high" if p_count >= 2 else "medium",
            "evidence": provider_evidence,
            "note": "Full provider obligations apply (Articles 9-15, conformity assessment, registration).",
        }
    elif d_count > 0 and p_count == 0:
        return {
            "role": "deployer",
            "confidence": "high" if d_count >= 2 else "medium",
            "evidence": deployer_evidence,
            "note": "Deployer obligations apply (Article 26: use per instructions, human oversight, monitoring, logging; Article 27: fundamental rights impact assessment).",
        }
    elif p_count > 0 and d_count > 0:
        if p_count > d_count:
            return {
                "role": "provider",
                "confidence": "low",
                "evidence": provider_evidence + deployer_evidence,
                "note": "Mixed signals — training AND inference code detected. Likely provider. Review manually.",
            }
        else:
            return {
                "role": "unclear",
                "confidence": "low",
                "evidence": provider_evidence + deployer_evidence,
                "note": "Both provider and deployer indicators detected. Review whether you are training a model or using a third-party API.",
            }
    else:
        return {
            "role": "unclear",
            "confidence": "low",
            "evidence": [],
            "note": "Insufficient evidence to determine provider/deployer role. Check whether you train models or consume APIs.",
        }


# ---------------------------------------------------------------------------
# Obligation roadmap
# ---------------------------------------------------------------------------

def generate_obligation_roadmap(classification: Classification, text: str) -> list:
    """Generate an obligation roadmap for a classified AI system.

    Returns a list of obligation dicts sorted by priority:
        article, title, priority, status, effort_hours, note
    """
    if classification.tier not in (RiskTier.HIGH_RISK, RiskTier.PROHIBITED):
        return []

    obligations_data = _load_obligations()
    articles = obligations_data.get("articles", {})
    roadmap = []

    for art_num in classification.applicable_articles:
        art_str = str(art_num)
        if art_str not in articles:
            continue

        art = articles[art_str]
        status = _detect_compliance_status(art_str, text)

        # Parse effort hours (fallback YAML parser returns strings)
        raw_effort = art.get("effort_hours", [0, 0])
        if isinstance(raw_effort, list) and len(raw_effort) >= 2:
            effort = [int(raw_effort[0]), int(raw_effort[1])]
        else:
            effort = [0, 0]

        roadmap.append({
            "article": art_str,
            "title": f"Art. {art_str} {art.get('short', art.get('title', ''))}",
            "priority": art.get("priority", "MED"),
            "status": status,
            "effort_hours": effort,
            "description": art.get("description", ""),
        })

    # Sort: HIGH priority first, then by article number
    priority_order = {"HIGH": 0, "MED": 1, "LOW": 2}
    roadmap.sort(key=lambda x: (priority_order.get(x["priority"], 9), int(x["article"])))

    return roadmap


def _detect_compliance_status(article: str, text: str) -> str:
    """Detect rough compliance status for an article from code patterns.

    Returns: 'detected', 'partial', or 'not_detected'
    """
    text_lower = text.lower()

    checks = {
        "9": [r"risk.?manag", r"risk.?assess", r"risk.?register", r"risk.?matrix"],
        "10": [r"data.?governance", r"data.?quality", r"bias.?detect", r"fairlearn", r"aif360",
               r"data.?validation", r"training.?data.*doc"],
        "11": [r"annex.?iv", r"technical.?document", r"model.?card", r"system.?description"],
        "12": [r"\blogging\b", r"\.log\(", r"logger\.", r"audit.?trail", r"structlog",
               r"loguru", r"record.?keeping"],
        "13": [r"readme", r"instructions.?for.?use", r"api.?doc", r"user.?guide",
               r"model.?card", r"system.?card"],
        "14": [r"human.?review", r"human.?oversight", r"approval.?gate", r"manual.?review",
               r"confirm.?before", r"human.?in.?the.?loop", r"override"],
        "15": [r"test.?accuracy", r"assert", r"eval.?metric", r"precision\b", r"recall\b",
               r"f1.?score", r"input.?valid", r"sanitiz", r"adversarial.?test"],
    }

    patterns = checks.get(article, [])
    if not patterns:
        return "not_detected"

    match_count = sum(1 for p in patterns if re.search(p, text_lower))
    if match_count >= 2:
        return "detected"
    elif match_count == 1:
        return "partial"
    return "not_detected"


# ---------------------------------------------------------------------------
# Full explanation output
# ---------------------------------------------------------------------------

def explain_classification(text: str, filepath: str = "<stdin>",
                           language: str = "python") -> dict:
    """Produce a full explainable classification for a piece of code.

    Returns:
        {
            "classification": Classification,
            "pattern_matches": [list of line-level matches],
            "provider_deployer": {role, confidence, evidence, note},
            "obligation_roadmap": [list of obligations],
            "total_effort_hours": [min, max],
            "timeline": {current_law, omnibus_proposed}
        }
    """
    from classify_risk import classify

    classification = classify(text, language=language)
    pattern_matches = find_pattern_matches(text, language=language)
    provider_deployer = detect_provider_deployer(text)
    roadmap = generate_obligation_roadmap(classification, text)

    # Calculate total effort
    total_min = sum(o["effort_hours"][0] for o in roadmap)
    total_max = sum(o["effort_hours"][1] for o in roadmap)

    # Timeline from obligations data
    obligations_data = _load_obligations()
    timeline = obligations_data.get("timeline", {
        "current_law": "2 August 2026",
        "omnibus_proposed": {"annex_iii": "2 December 2027", "annex_i": "2 August 2028"},
        "guidance": "Plan for August 2026 until Omnibus is formally enacted",
    })

    return {
        "classification": classification,
        "pattern_matches": pattern_matches,
        "provider_deployer": provider_deployer,
        "obligation_roadmap": roadmap,
        "total_effort_hours": [total_min, total_max],
        "timeline": timeline,
    }


def format_explanation(result: dict, filepath: str = "<stdin>") -> str:
    """Format an explanation result as human-readable text."""
    cls = result["classification"]
    lines = []

    # Header
    tier_label = cls.tier.value.upper().replace("_", "-")
    category = cls.category or ""
    lines.append(f"Classification: {tier_label}")
    if category:
        lines.append(f"  {category}")
    lines.append("")

    # Pattern matches — WHY
    matches = result["pattern_matches"]
    if matches:
        lines.append("WHY:")
        for m in matches:
            lines.append(f"  {filepath}:{m['line']} — {m['pattern_name']}")
            lines.append(f"    Code: {m['matched_text']}")
            lines.append(f"    Legal basis: {m['legal_basis']}")
            if m.get("conditions"):
                lines.append(f"    Conditions: {m['conditions']}")
            lines.append(f"    False positive if: {m['false_positive_if']}")
            lines.append("")
    elif cls.tier == RiskTier.MINIMAL_RISK:
        lines.append("WHY: No high-risk or prohibited patterns detected in code.")
        lines.append("")
    elif cls.tier == RiskTier.NOT_AI:
        lines.append("WHY: No AI indicators detected in this file.")
        lines.append("")

    # Provider / Deployer
    pd = result["provider_deployer"]
    role_label = pd["role"].upper()
    lines.append(f"ROLE: {role_label} (confidence: {pd['confidence']})")
    if pd["evidence"]:
        for ev in pd["evidence"][:3]:
            lines.append(f"  - {ev}")
    lines.append(f"  {pd['note']}")
    lines.append("")

    # Obligation roadmap
    roadmap = result["obligation_roadmap"]
    if roadmap:
        lines.append("OBLIGATIONS:")
        for o in roadmap:
            status_icon = {
                "detected": "+",
                "partial": "~",
                "not_detected": "-",
            }.get(o["status"], "?")
            effort = f"{o['effort_hours'][0]}-{o['effort_hours'][1]}h"
            lines.append(f"  [{o['priority']:4s}] {o['title']} [{status_icon}] {o['status']} — {effort}")
        lines.append("")

        # Total effort
        total = result["total_effort_hours"]
        lines.append(f"  Total: {total[0]}-{total[1]} hours (indicative — varies by system complexity)")

        # Timeline
        timeline = result.get("timeline", {})
        current = timeline.get("current_law", "2 August 2026")
        omnibus = timeline.get("omnibus_proposed", {})
        annex_iii = omnibus.get("annex_iii", "2 December 2027") if isinstance(omnibus, dict) else "2 December 2027"
        lines.append(f"  Deadline: {current} (or {annex_iii} if Omnibus passes)")
        lines.append("")

    # Disclaimer
    lines.append("NOTE: This is a risk INDICATION, not a legal determination.")
    lines.append("The EU AI Act Article 6 requires contextual assessment of intended")
    lines.append("purpose and deployment context that automated scanning cannot provide.")

    return "\n".join(lines)
