# regula-ignore
#!/usr/bin/env python3
"""
Regula Risk Indication Engine

Detects patterns in code that correlate with EU AI Act risk tiers.

IMPORTANT: This engine performs pattern-based risk INDICATION, not legal
risk CLASSIFICATION. The EU AI Act Article 6 requires a contextual
assessment of intended purpose and deployment context that automated
pattern matching cannot provide. Results should be treated as flags
for human review, not as legal determinations.
"""

import argparse
import fcntl
import json
import os
import re
import sys
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Optional


class RiskTier(Enum):
    PROHIBITED = "prohibited"
    HIGH_RISK = "high_risk"
    LIMITED_RISK = "limited_risk"
    MINIMAL_RISK = "minimal_risk"
    NOT_AI = "not_ai"


@dataclass
class Classification:
    tier: RiskTier
    confidence: str
    indicators_matched: list = field(default_factory=list)
    applicable_articles: list = field(default_factory=list)
    category: Optional[str] = None
    description: Optional[str] = None
    action: str = "allow"
    message: Optional[str] = None
    exceptions: Optional[str] = None
    confidence_score: int = 0  # 0-100 numeric confidence

    def to_dict(self) -> dict:
        result = asdict(self)
        result["tier"] = self.tier.value
        return result

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


# ---------------------------------------------------------------------------
# Article 5 prohibited patterns
#
# Each entry includes the specific conditions under which the prohibition
# applies and any narrow exceptions from the Act, so that messages to the
# developer are legally accurate rather than categorical.
# ---------------------------------------------------------------------------

PROHIBITED_PATTERNS = {
    "subliminal_manipulation": {
        "patterns": [r"subliminal", r"beyond.?consciousness", r"subconscious.?influence"],
        "article": "5(1)(a)",
        "description": "AI deploying subliminal techniques beyond a person's consciousness",
        "conditions": "Prohibited when the technique materially distorts behaviour and causes or is likely to cause significant harm.",
        "exceptions": None,
    },
    "exploitation_vulnerabilities": {
        "patterns": [r"target.?elderly", r"exploit.?disabil", r"vulnerable.?group.?target"],
        "article": "5(1)(b)",
        "description": "Exploiting vulnerabilities of specific groups (age, disability, economic situation)",
        "conditions": "Prohibited when exploiting vulnerabilities to materially distort behaviour causing significant harm.",
        "exceptions": None,
    },
    "social_scoring": {
        "patterns": [r"social.?scor", r"social.?credit", r"citizen.?score", r"behaviour.?scor"],
        "article": "5(1)(c)",
        "description": "Social scoring by public authorities or on their behalf",
        "conditions": "Prohibited when evaluating or classifying persons based on social behaviour or personal traits, leading to detrimental treatment disproportionate to context.",
        "exceptions": None,
    },
    "criminal_prediction": {
        "patterns": [r"crime.?predict", r"criminal.?risk.?assess", r"predictive.?polic", r"recidivism"],
        "article": "5(1)(d)",
        "description": "Criminal risk prediction based solely on profiling or personality traits",
        "conditions": "Prohibited ONLY when based solely on profiling or personality traits. Systems using multiple evidence sources (case facts, prior convictions with human review) may be lawful.",
        "exceptions": "AI systems that support human assessment based on objective, verifiable facts directly linked to criminal activity are NOT prohibited.",
    },
    "facial_recognition_scraping": {
        "patterns": [r"face.?scrap", r"facial.?database.?untarget", r"mass.?facial.?collect"],
        "article": "5(1)(e)",
        "description": "Creating facial recognition databases through untargeted scraping",
        "conditions": "Prohibited when scraping facial images from the internet or CCTV to build or expand recognition databases.",
        "exceptions": None,
    },
    "emotion_inference_restricted": {
        "patterns": [r"emotion.{0,20}workplace", r"emotion.{0,20}school", r"sentiment.{0,20}employee",
                     r"workplace.{0,20}emotion", r"employee.{0,20}emotion"],
        "article": "5(1)(f)",
        "description": "Emotion inference in workplace or educational settings",
        "conditions": "Prohibited in workplace and educational institutions.",
        "exceptions": "EXEMPT when used for medical or safety purposes (e.g., detecting driver fatigue, monitoring patient wellbeing in clinical settings).",
    },
    "biometric_categorisation_sensitive": {
        "patterns": [r"race.?detect", r"ethnicity.?infer", r"political.?opinion.?biometric",
                     r"religion.?detect", r"sexual.?orientation.?infer"],
        "article": "5(1)(g)",
        "description": "Biometric categorisation inferring sensitive attributes (race, politics, religion, sexuality)",
        "conditions": "Prohibited when using biometric data to categorise persons by race, political opinions, trade union membership, religious beliefs, sex life, or sexual orientation.",
        "exceptions": "Labelling or filtering of lawfully acquired biometric datasets (e.g., photo sorting) may be exempt where no categorisation of individuals occurs.",
    },
    "realtime_biometric_public": {
        "patterns": [r"real.?time.?facial.?recogn", r"live.?biometric.?public",
                     r"public.?space.?biometric", r"mass.?surveillance.?biometric"],
        "article": "5(1)(h)",
        "description": "Real-time remote biometric identification in publicly accessible spaces for law enforcement",
        "conditions": "Prohibited for law enforcement in publicly accessible spaces in real-time.",
        "exceptions": "Narrow exceptions exist with PRIOR judicial authorisation for: (i) targeted search for victims of abduction/trafficking/sexual exploitation, (ii) prevention of specific imminent terrorist threat, (iii) identification of suspects of serious criminal offences (as defined in Annex II).",
    },
}


# ---------------------------------------------------------------------------
# Annex III high-risk patterns
#
# NOTE: The EU AI Act Article 6 requires a two-step test:
#   1. The system falls within an Annex III area, AND
#   2. It poses a significant risk of harm.
# Article 6(3) explicitly exempts systems that perform narrow procedural
# tasks, improve previously completed human activities, detect patterns
# without replacing human assessment, or perform preparatory tasks.
#
# Pattern matches here indicate the system MAY be high-risk and should
# be reviewed — not that it IS high-risk.
# ---------------------------------------------------------------------------

HIGH_RISK_PATTERNS = {
    "biometrics": {
        "patterns": [r"biometric.?ident", r"face.?recogn", r"fingerprint.?recogn", r"voice.?recogn"],
        "articles": ["9", "10", "11", "12", "13", "14", "15"],
        "category": "Annex III, Category 1",
        "description": "Biometric identification and categorisation",
    },
    "critical_infrastructure": {
        "patterns": [r"energy.?grid", r"water.?supply", r"traffic.?control", r"electricity.?manage"],
        "articles": ["9", "10", "11", "12", "13", "14", "15"],
        "category": "Annex III, Category 2",
        "description": "Critical infrastructure management",
    },
    "education": {
        "patterns": [r"admission.?decision", r"student.?assess", r"exam.?scor", r"procto"],
        "articles": ["9", "10", "11", "12", "13", "14", "15"],
        "category": "Annex III, Category 3",
        "description": "Education and vocational training",
    },
    "employment": {
        "patterns": [r"cv.?screen", r"resume.?filt", r"hiring.?decision", r"recruit\w*\W{0,3}automat",
                     r"automat\w*\W{0,3}recruit", r"candidate.?rank", r"promotion.?decision",
                     r"termination.?decision", r"performance.?review.{0,10}(ai|automat|model|predict)"],
        "articles": ["9", "10", "11", "12", "13", "14", "15"],
        "category": "Annex III, Category 4",
        "description": "Employment and workers management",
    },
    "essential_services": {
        "patterns": [r"credit.?scor", r"creditworth", r"loan.?decision", r"insurance.?pric",
                     r"benefit.?eligib", r"emergency.?dispatch"],
        "articles": ["9", "10", "11", "12", "13", "14", "15"],
        "category": "Annex III, Category 5",
        "description": "Access to essential services",
    },
    "law_enforcement": {
        "patterns": [r"polygraph", r"lie.?detect", r"evidence.?reliab", r"criminal.?investigat"],
        "articles": ["9", "10", "11", "12", "13", "14", "15"],
        "category": "Annex III, Category 6",
        "description": "Law enforcement",
    },
    "migration": {
        "patterns": [r"border.?control", r"visa.?application", r"asylum.?application", r"immigration.?decision"],
        "articles": ["9", "10", "11", "12", "13", "14", "15"],
        "category": "Annex III, Category 7",
        "description": "Migration, asylum, and border control",
    },
    "justice": {
        "patterns": [r"judicial.?decision", r"court.?rul", r"sentenc", r"election.?influence"],
        "articles": ["9", "10", "11", "12", "13", "14", "15"],
        "category": "Annex III, Category 8",
        "description": "Justice and democratic processes",
    },
    "medical_devices": {
        "patterns": [r"medical.?diagnos", r"clinical.?decision", r"treatment.?recommend", r"patient.?triage"],
        "articles": ["9", "10", "11", "12", "13", "14", "15"],
        "category": "Medical Devices",
        "description": "AI components of medical devices",
    },
    "safety_components": {
        "patterns": [r"autonomous.?vehicle", r"self.?driv", r"aviation.?safety", r"machinery.?safety"],
        "articles": ["9", "10", "11", "12", "13", "14", "15"],
        "category": "Safety Components",
        "description": "Safety components under Union harmonisation legislation",
    },
}

LIMITED_RISK_PATTERNS = {
    "chatbots": {
        "patterns": [r"chatbot", r"conversational.?ai", r"virtual.?assist", r"support.?bot"],
        "article": "50",
        "description": "Chatbots and conversational AI",
    },
    "emotion_recognition": {
        "patterns": [r"emotion.?recogn", r"sentiment.?analy", r"affect.?detect", r"mood.?analy"],
        "article": "50",
        "description": "Emotion recognition systems",
    },
    "biometric_categorisation": {
        "patterns": [r"age.?estimat", r"gender.?detect", r"demographic.?analy"],
        "article": "50",
        "description": "Biometric categorisation (non-sensitive)",
    },
    "synthetic_content": {
        "patterns": [r"deepfake", r"synthetic.?media", r"face.?swap", r"voice.?clon",
                     r"ai.{0,5}generat\w*.{0,5}image", r"text.?to.?image"],
        "article": "50",
        "description": "Synthetic content generation",
    },
}

AI_INDICATORS = {
    "libraries": [r"tensorflow", r"torch", r"pytorch", r"transformers", r"langchain",
                  r"openai", r"anthropic", r"sklearn", r"scikit.?learn", r"keras",
                  r"xgboost", r"lightgbm", r"huggingface", r"spacy", r"nltk",
                  r"onnx", r"onnxruntime", r"brain\.js", r"@tensorflow/tfjs",
                  r"@anthropic-ai/sdk", r"@langchain", r"transformers\.js"],
    "model_files": [r"\.onnx", r"\.pt\b", r"\.pth\b", r"\.pkl\b", r"\.joblib\b",
                    r"\.h5\b", r"\.hdf5\b", r"\.safetensors", r"\.gguf\b", r"\.ggml\b"],
    "api_endpoints": [r"api\.openai\.com", r"api\.anthropic\.com",
                      r"generativelanguage\.googleapis\.com",
                      r"api\.cohere\.ai", r"api\.mistral\.ai"],
    "ml_patterns": [r"model\.fit", r"model\.train", r"model\.predict", r"embedding",
                    r"vectorstore", r"llm\.invoke", r"chat\.completions",
                    r"messages\.create", r"from_pretrained", r"fine.?tune",
                    r"neural.?network", r"deep.?learning", r"machine.?learning"],
}

# Patterns that indicate model TRAINING (not just inference) — may trigger
# GPAI obligations if building a general-purpose model (>10^23 FLOPs)
GPAI_TRAINING_PATTERNS = [
    r"model\.fit\b", r"model\.train\b", r"\.train\(\)", r"trainer\.train",
    r"fine.?tun", r"from_pretrained.{0,30}train", r"training_args",
    r"TrainingArguments", r"Trainer\(", r"SFTTrainer",
    r"\.compile\(.{0,30}optimizer", r"backpropagat",
    r"torch\.optim", r"tf\.keras\.optimizers",
    r"lora", r"qlora", r"peft",
]


def is_training_activity(text: str) -> bool:
    """Detect whether code involves model training/fine-tuning (not just inference)."""
    return any(re.search(p, text, re.IGNORECASE) for p in GPAI_TRAINING_PATTERNS)


# ---------------------------------------------------------------------------
# Policy loading
# ---------------------------------------------------------------------------

def _load_policy() -> dict:
    """Load policy configuration. Tries YAML (via pyyaml) then JSON fallback."""
    candidates = []
    env_path = os.environ.get("REGULA_POLICY")
    if env_path:
        candidates.append(Path(env_path))
    candidates.append(Path.cwd() / "regula-policy.yaml")
    candidates.append(Path.cwd() / "regula-policy.json")
    candidates.append(Path.home() / ".regula" / "regula-policy.yaml")
    candidates.append(Path.home() / ".regula" / "regula-policy.json")

    for path in candidates:
        if not path.exists():
            continue
        try:
            content = path.read_text(encoding="utf-8")
            if path.suffix == ".json":
                return json.loads(content)
            # YAML: try pyyaml first, then safe fallback
            try:
                import yaml
                return yaml.safe_load(content) or {}
            except ImportError:
                return _parse_yaml_fallback(content)
        except Exception:
            continue
    return {}


def _parse_yaml_fallback(text: str) -> dict:
    """
    Minimal YAML-subset parser used ONLY when pyyaml is not installed.
    Handles the specific structure of regula-policy.yaml: scalar values,
    inline lists, and up to 3 levels of nesting.

    This is NOT a general YAML parser. Install pyyaml for full support.
    """
    result = {}
    stack = [result]  # stack of current dict context
    indent_stack = [-1]  # indentation levels

    for line in text.split("\n"):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        indent = len(line) - len(line.lstrip())

        # Pop stack to correct level
        while len(indent_stack) > 1 and indent <= indent_stack[-1]:
            indent_stack.pop()
            stack.pop()

        current = stack[-1]

        # List item
        if stripped.startswith("- "):
            item = stripped[2:].strip().strip('"').strip("'")
            if isinstance(current, list):
                current.append(item)
            continue

        # Key-value
        if ":" in stripped:
            key, _, val = stripped.partition(":")
            key = key.strip()
            val = val.strip()

            if not val:
                # New dict section
                new_dict = {}
                if isinstance(current, dict):
                    current[key] = new_dict
                    stack.append(new_dict)
                    indent_stack.append(indent)
            elif val.startswith("["):
                # Inline list
                items = re.findall(r'["\']?([^"\',\[\]]+)["\']?', val)
                if isinstance(current, dict):
                    current[key] = [i.strip() for i in items if i.strip()]
            else:
                # Scalar value
                val = val.strip('"').strip("'")
                if val.lower() == "true":
                    val = True
                elif val.lower() == "false":
                    val = False
                elif val.isdigit():
                    val = int(val)
                if isinstance(current, dict):
                    current[key] = val

    return result


_POLICY = _load_policy()


def get_policy() -> dict:
    return _POLICY


# ---------------------------------------------------------------------------
# Detection functions
# ---------------------------------------------------------------------------

# Compact ISO 42001 mapping for high-risk classification output.
# Full mapping in references/iso_42001_mapping.yaml.
ISO_42001_MAP = {
    "9":  "ISO 42001: 6.1 (Risk assessment), A.5.3 (AI risk management)",
    "10": "ISO 42001: A.6.6 (Data for AI systems), A.7.4 (Documentation of data)",
    "11": "ISO 42001: A.6.4 (AI system documentation), 7.5 (Documented information)",
    "12": "ISO 42001: A.6.10 (Logging and monitoring)",
    "13": "ISO 42001: A.6.8 (Transparency and explainability)",
    "14": "ISO 42001: A.6.3 (Human oversight of AI systems)",
    "15": "ISO 42001: A.6.9 (Performance and monitoring)",
}


# Pattern-to-Article observations: when specific code patterns co-occur
# with high-risk indicators, generate Article-specific governance notes.
GOVERNANCE_OBSERVATIONS = {
    "training_data": {
        "patterns": [r"\.fit\(", r"\.train\(", r"training_data", r"train_test_split",
                     r"\.csv", r"read_csv", r"load_data"],
        "article": "10",
        "observation": "Training data detected — Article 10 requires data to be relevant, representative, and examined for biases.",
    },
    "prediction_without_review": {
        "patterns": [r"\.predict\(", r"\.predict_proba\("],
        "article": "14",
        "observation": "Model predictions detected — Article 14 requires human oversight with ability to override or reverse AI outputs.",
    },
    "automated_decision_function": {
        "patterns": [r"def\s+\w*(screen|filter|rank|score|decide|reject|accept|approve|deny)\w*\s*\("],
        "article": "13",
        "observation": "Automated decision function detected — Article 13 requires transparency to deployers about capabilities and limitations.",
    },
    "no_logging": {
        "patterns": [r"logging", r"\.log\(", r"audit", r"logger"],
        "article": "12",
        "observation": None,  # Only flag ABSENCE — see check below
        "absence_observation": "No logging detected — Article 12 requires automatic recording of events for traceability.",
    },
}


def generate_observations(text: str) -> list:
    """Generate Article-specific governance observations from code patterns.

    Returns a list of dicts with 'article' and 'observation' keys.
    Only runs on text already classified as high-risk.
    """
    observations = []
    text_lower = text.lower()

    for name, config in GOVERNANCE_OBSERVATIONS.items():
        found = any(re.search(p, text_lower) for p in config["patterns"])

        if name == "no_logging":
            # Flag absence of logging, not presence
            if not found:
                observations.append({
                    "article": config["article"],
                    "observation": config["absence_observation"],
                })
        elif found and config.get("observation"):
            observations.append({
                "article": config["article"],
                "observation": config["observation"],
            })

    return observations


def _compute_confidence_score(tier: str, num_matches: int, has_ai_indicator: bool) -> int:
    """Compute a 0-100 confidence score based on tier, match count, and context."""
    base = {"prohibited": 75, "high_risk": 55, "limited_risk": 40, "minimal_risk": 15}.get(tier, 10)
    match_bonus = min(num_matches * 8, 15)
    ai_bonus = 10 if has_ai_indicator else 0
    return min(base + match_bonus + ai_bonus, 100)


def is_ai_related(text: str) -> bool:
    text_lower = text.lower()
    for category in AI_INDICATORS.values():
        for pattern in category:
            if re.search(pattern, text_lower):
                return True
    return False


def check_prohibited(text: str) -> Optional[Classification]:
    text_lower = text.lower()
    matches = []
    for name, config in PROHIBITED_PATTERNS.items():
        for pattern in config["patterns"]:
            if re.search(pattern, text_lower):
                matches.append(config | {"indicator": name})
                break

    if matches:
        primary = matches[0]
        has_ai = is_ai_related(text)
        return Classification(
            tier=RiskTier.PROHIBITED,
            confidence="high" if len(matches) >= 2 else "medium",
            indicators_matched=[m["indicator"] for m in matches],
            applicable_articles=[primary["article"]],
            category="Prohibited (Article 5)",
            description=primary["description"],
            action="block",
            message=f"PROHIBITED: {primary['description']}",
            exceptions=primary.get("exceptions"),
            confidence_score=_compute_confidence_score("prohibited", len(matches), has_ai),
        )
    return None


def check_high_risk(text: str) -> Optional[Classification]:
    text_lower = text.lower()
    matches = []
    for name, config in HIGH_RISK_PATTERNS.items():
        for pattern in config["patterns"]:
            if re.search(pattern, text_lower):
                matches.append(config | {"indicator": name})
                break

    if matches:
        all_articles = set()
        for m in matches:
            all_articles.update(m["articles"])
        primary = matches[0]
        return Classification(
            tier=RiskTier.HIGH_RISK,
            confidence="high" if len(matches) >= 2 else "medium",
            indicators_matched=[m["indicator"] for m in matches],
            applicable_articles=sorted(all_articles, key=int),
            category=primary["category"],
            description=primary["description"],
            action="allow_with_requirements",
            message=f"HIGH-RISK: {primary['description']} - Articles {', '.join(sorted(all_articles, key=int))}",
            confidence_score=_compute_confidence_score("high_risk", len(matches), True),
        )
    return None


def check_limited_risk(text: str) -> Optional[Classification]:
    text_lower = text.lower()
    matches = []
    for name, config in LIMITED_RISK_PATTERNS.items():
        for pattern in config["patterns"]:
            if re.search(pattern, text_lower):
                matches.append(config | {"indicator": name})
                break

    if matches:
        primary = matches[0]
        return Classification(
            tier=RiskTier.LIMITED_RISK,
            confidence="high" if len(matches) >= 2 else "medium",
            indicators_matched=[m["indicator"] for m in matches],
            applicable_articles=["50"],
            category="Limited Risk (Article 50)",
            description=primary["description"],
            action="allow_with_transparency",
            message=f"LIMITED-RISK: {primary['description']}",
            confidence_score=_compute_confidence_score("limited_risk", len(matches), True),
        )
    return None


def _check_policy_overrides(text: str) -> Optional[Classification]:
    """Check policy-defined force_high_risk and exempt lists.

    NOTE: This is only called for non-prohibited classifications.
    Prohibited practices CANNOT be exempted by policy — see classify().
    """
    policy = get_policy()
    rules = policy.get("rules", {})
    if not isinstance(rules, dict):
        return None
    risk_rules = rules.get("risk_classification", {})
    if not isinstance(risk_rules, dict):
        return None

    text_lower = text.lower()

    # Check exempt list
    exempt = risk_rules.get("exempt", [])
    if isinstance(exempt, list):
        for pattern in exempt:
            if isinstance(pattern, str) and pattern.lower() in text_lower:
                return Classification(
                    tier=RiskTier.MINIMAL_RISK, confidence="high",
                    indicators_matched=[], applicable_articles=[],
                    category="Policy Exempt",
                    description=f"Exempt per policy: {pattern}",
                    action="allow",
                    message=f"EXEMPT: '{pattern}' is exempt per regula-policy.yaml",
                )

    # Check force_high_risk list
    force_high = risk_rules.get("force_high_risk", [])
    if isinstance(force_high, list):
        for pattern in force_high:
            if not isinstance(pattern, str):
                continue
            normalised = pattern.lower().replace("_", " ")
            if normalised in text_lower or pattern.lower() in text_lower:
                return Classification(
                    tier=RiskTier.HIGH_RISK, confidence="high",
                    indicators_matched=[pattern],
                    applicable_articles=["9", "10", "11", "12", "13", "14", "15"],
                    category="Policy Override",
                    description=f"Forced high-risk per policy: {pattern}",
                    action="allow_with_requirements",
                    message=f"HIGH-RISK (policy override): '{pattern}' is force-classified as high-risk",
                )

    return None


def classify(text: str) -> Classification:
    """Classify text against EU AI Act risk tiers.

    Priority order (safety-first):
      1. Prohibited practices — ALWAYS checked, CANNOT be overridden by policy
      2. Policy overrides (force_high_risk, exempt)
      3. Pattern-based classification (high-risk, limited-risk, minimal-risk)
    """
    # 1. ALWAYS check prohibited first — policy cannot override Article 5
    prohibited = check_prohibited(text)
    if prohibited:
        return prohibited

    # 2. Policy overrides (only for non-prohibited classifications)
    policy_result = _check_policy_overrides(text)
    if policy_result:
        return policy_result

    # 3. Standard classification
    if not is_ai_related(text):
        return Classification(
            tier=RiskTier.NOT_AI, confidence="high",
            action="allow", message="No AI indicators detected.",
        )

    high_risk = check_high_risk(text)
    if high_risk:
        return high_risk

    limited_risk = check_limited_risk(text)
    if limited_risk:
        return limited_risk

    return Classification(
        tier=RiskTier.MINIMAL_RISK, confidence="medium", action="allow",
        message="Minimal-risk AI system. No specific EU AI Act requirements.",
    )


def main():
    parser = argparse.ArgumentParser(
        description="Detect EU AI Act risk indicators in AI operations"
    )
    parser.add_argument("--input", "-i", help="Text to classify")
    parser.add_argument("--file", "-f", help="File to classify")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()

    if args.file:
        text = Path(args.file).read_text(encoding="utf-8", errors="ignore")
    elif args.input:
        text = args.input
    else:
        parser.print_help()
        sys.exit(1)

    result = classify(text)
    print(result.to_json() if args.format == "json" else result.message)
    sys.exit(2 if result.tier == RiskTier.PROHIBITED else 0)


if __name__ == "__main__":
    main()
