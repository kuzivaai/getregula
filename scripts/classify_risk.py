#!/usr/bin/env python3
"""
Regula Risk Classification Engine
Classifies AI operations against EU AI Act risk tiers.
"""

import argparse
import json
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

    def to_dict(self) -> dict:
        result = asdict(self)
        result["tier"] = self.tier.value
        return result

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


PROHIBITED_PATTERNS = {
    "subliminal_manipulation": {
        "patterns": [r"subliminal", r"beyond.?consciousness", r"subconscious.?influence"],
        "article": "5(1)(a)",
        "description": "AI deploying subliminal techniques beyond a person's consciousness"
    },
    "exploitation_vulnerabilities": {
        "patterns": [r"target.?elderly", r"exploit.?disabil", r"vulnerable.?group.?target"],
        "article": "5(1)(b)",
        "description": "Exploiting vulnerabilities of specific groups"
    },
    "social_scoring": {
        "patterns": [r"social.?scor", r"social.?credit", r"citizen.?score", r"behaviour.?scor"],
        "article": "5(1)(c)",
        "description": "Social scoring systems evaluating persons based on social behaviour"
    },
    "criminal_prediction": {
        "patterns": [r"crime.?predict", r"criminal.?risk.?assess", r"predictive.?polic", r"recidivism"],
        "article": "5(1)(d)",
        "description": "Criminal risk prediction based solely on profiling"
    },
    "facial_recognition_scraping": {
        "patterns": [r"face.?scrap", r"facial.?database.?untarget", r"mass.?facial.?collect"],
        "article": "5(1)(e)",
        "description": "Creating facial recognition databases through untargeted scraping"
    },
    "emotion_inference_restricted": {
        "patterns": [r"emotion.{0,20}workplace", r"emotion.{0,20}school", r"sentiment.{0,20}employee",
                     r"workplace.{0,20}emotion", r"employee.{0,20}emotion"],
        "article": "5(1)(f)",
        "description": "Emotion inference in workplace or educational settings"
    },
    "biometric_categorisation_sensitive": {
        "patterns": [r"race.?detect", r"ethnicity.?infer", r"political.?opinion.?biometric",
                     r"religion.?detect", r"sexual.?orientation.?infer"],
        "article": "5(1)(g)",
        "description": "Biometric categorisation inferring sensitive attributes"
    },
    "realtime_biometric_public": {
        "patterns": [r"real.?time.?facial.?recogn", r"live.?biometric.?public",
                     r"public.?space.?biometric", r"mass.?surveillance.?biometric"],
        "article": "5(1)(h)",
        "description": "Real-time remote biometric identification in public spaces"
    }
}

HIGH_RISK_PATTERNS = {
    "biometrics": {
        "patterns": [r"biometric.?ident", r"face.?recogn", r"fingerprint.?recogn", r"voice.?recogn"],
        "articles": ["9", "10", "11", "12", "13", "14", "15"],
        "category": "Annex III, Category 1",
        "description": "Biometric identification and categorisation"
    },
    "critical_infrastructure": {
        "patterns": [r"energy.?grid", r"water.?supply", r"traffic.?control", r"electricity.?manage"],
        "articles": ["9", "10", "11", "12", "13", "14", "15"],
        "category": "Annex III, Category 2",
        "description": "Critical infrastructure management"
    },
    "education": {
        "patterns": [r"admission.?decision", r"student.?assess", r"exam.?scor", r"procto"],
        "articles": ["9", "10", "11", "12", "13", "14", "15"],
        "category": "Annex III, Category 3",
        "description": "Education and vocational training"
    },
    "employment": {
        "patterns": [r"cv.?screen", r"resume.?filt", r"hiring.?decision", r"recruit.?automat",
                     r"candidate.?rank", r"promotion.?decision", r"termination.?decision"],
        "articles": ["9", "10", "11", "12", "13", "14", "15"],
        "category": "Annex III, Category 4",
        "description": "Employment and workers management"
    },
    "essential_services": {
        "patterns": [r"credit.?scor", r"creditworth", r"loan.?decision", r"insurance.?pric",
                     r"benefit.?eligib", r"emergency.?dispatch"],
        "articles": ["9", "10", "11", "12", "13", "14", "15"],
        "category": "Annex III, Category 5",
        "description": "Access to essential services"
    },
    "law_enforcement": {
        "patterns": [r"polygraph", r"lie.?detect", r"evidence.?reliab", r"criminal.?investigat"],
        "articles": ["9", "10", "11", "12", "13", "14", "15"],
        "category": "Annex III, Category 6",
        "description": "Law enforcement"
    },
    "migration": {
        "patterns": [r"border.?control", r"visa.?application", r"asylum.?application", r"immigration.?decision"],
        "articles": ["9", "10", "11", "12", "13", "14", "15"],
        "category": "Annex III, Category 7",
        "description": "Migration, asylum, and border control"
    },
    "justice": {
        "patterns": [r"judicial.?decision", r"court.?rul", r"sentenc", r"election.?influence"],
        "articles": ["9", "10", "11", "12", "13", "14", "15"],
        "category": "Annex III, Category 8",
        "description": "Justice and democratic processes"
    },
    "medical_devices": {
        "patterns": [r"medical.?diagnos", r"clinical.?decision", r"treatment.?recommend", r"patient.?triage"],
        "articles": ["9", "10", "11", "12", "13", "14", "15"],
        "category": "Medical Devices",
        "description": "AI components of medical devices"
    },
    "safety_components": {
        "patterns": [r"autonomous.?vehicle", r"self.?driv", r"aviation.?safety", r"machinery.?safety"],
        "articles": ["9", "10", "11", "12", "13", "14", "15"],
        "category": "Safety Components",
        "description": "Safety components under Union harmonisation legislation"
    }
}

LIMITED_RISK_PATTERNS = {
    "chatbots": {
        "patterns": [r"chatbot", r"conversational.?ai", r"virtual.?assist", r"support.?bot"],
        "article": "50",
        "description": "Chatbots and conversational AI"
    },
    "emotion_recognition": {
        "patterns": [r"emotion.?recogn", r"sentiment.?analy", r"affect.?detect", r"mood.?analy"],
        "article": "50",
        "description": "Emotion recognition systems"
    },
    "biometric_categorisation": {
        "patterns": [r"age.?estimat", r"gender.?detect", r"demographic.?analy"],
        "article": "50",
        "description": "Biometric categorisation (non-sensitive)"
    },
    "synthetic_content": {
        "patterns": [r"deepfake", r"synthetic.?media", r"face.?swap", r"voice.?clone",
                     r"ai.?generat.?image", r"text.?to.?image"],
        "article": "50",
        "description": "Synthetic content generation"
    }
}

AI_INDICATORS = {
    "libraries": [r"tensorflow", r"torch", r"pytorch", r"transformers", r"langchain",
                  r"openai", r"anthropic", r"sklearn", r"scikit.?learn", r"keras"],
    "model_files": [r"\.onnx", r"\.pt\b", r"\.pth\b", r"\.pkl\b", r"\.h5\b", r"\.safetensors"],
    "api_endpoints": [r"api\.openai\.com", r"api\.anthropic\.com", r"generativelanguage\.googleapis\.com"],
    "ml_patterns": [r"model\.fit", r"model\.train", r"model\.predict", r"embedding",
                    r"from_pretrained", r"neural.?network", r"deep.?learning", r"machine.?learning"]
}


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
                matches.append({"indicator": name, "article": config["article"], "description": config["description"]})
                break
    if matches:
        return Classification(
            tier=RiskTier.PROHIBITED, confidence="high" if len(matches) >= 2 else "medium",
            indicators_matched=[m["indicator"] for m in matches],
            applicable_articles=[matches[0]["article"]], category="Prohibited (Article 5)",
            description=matches[0]["description"], action="block",
            message=f"PROHIBITED: {matches[0]['description']}"
        )
    return None


def check_high_risk(text: str) -> Optional[Classification]:
    text_lower = text.lower()
    matches = []
    for name, config in HIGH_RISK_PATTERNS.items():
        for pattern in config["patterns"]:
            if re.search(pattern, text_lower):
                matches.append({"indicator": name, "articles": config["articles"],
                               "category": config["category"], "description": config["description"]})
                break
    if matches:
        all_articles = set()
        for m in matches:
            all_articles.update(m["articles"])
        return Classification(
            tier=RiskTier.HIGH_RISK, confidence="high" if len(matches) >= 2 else "medium",
            indicators_matched=[m["indicator"] for m in matches],
            applicable_articles=sorted(all_articles, key=int),
            category=matches[0]["category"], description=matches[0]["description"],
            action="allow_with_requirements",
            message=f"HIGH-RISK: {matches[0]['description']} - Articles {', '.join(sorted(all_articles, key=int))}"
        )
    return None


def check_limited_risk(text: str) -> Optional[Classification]:
    text_lower = text.lower()
    matches = []
    for name, config in LIMITED_RISK_PATTERNS.items():
        for pattern in config["patterns"]:
            if re.search(pattern, text_lower):
                matches.append({"indicator": name, "article": config["article"], "description": config["description"]})
                break
    if matches:
        return Classification(
            tier=RiskTier.LIMITED_RISK, confidence="high" if len(matches) >= 2 else "medium",
            indicators_matched=[m["indicator"] for m in matches], applicable_articles=["50"],
            category="Limited Risk (Article 50)", description=matches[0]["description"],
            action="allow_with_transparency", message=f"LIMITED-RISK: {matches[0]['description']}"
        )
    return None


def classify(text: str) -> Classification:
    if not is_ai_related(text):
        prohibited = check_prohibited(text)
        if prohibited:
            return prohibited
        return Classification(tier=RiskTier.NOT_AI, confidence="high", action="allow", message="No AI indicators detected.")
    
    prohibited = check_prohibited(text)
    if prohibited:
        return prohibited
    high_risk = check_high_risk(text)
    if high_risk:
        return high_risk
    limited_risk = check_limited_risk(text)
    if limited_risk:
        return limited_risk
    return Classification(tier=RiskTier.MINIMAL_RISK, confidence="medium", action="allow",
                         message="Minimal-risk AI system. No specific EU AI Act requirements.")


def main():
    parser = argparse.ArgumentParser(description="Classify AI operations against EU AI Act risk tiers")
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
