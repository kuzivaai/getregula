# regula-ignore
"""EU AI Act risk pattern definitions for Regula.

Pure configuration — no functions, no logic. Contains all regex patterns
used by the classification engine, organised by risk tier.
"""

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
        "patterns": [r"\bsocial.?scor(?:e|ing)\b", r"\bsocial.?credit.?(?:scor|system|rating)", r"\bsocial.?credit\b", r"\bcitizen.?score", r"\bbehaviour.?scor"],
        "article": "5(1)(c)",
        "description": "Social scoring by public authorities or on their behalf",
        "conditions": "Prohibited when evaluating or classifying persons based on social behaviour or personal traits, leading to detrimental treatment disproportionate to context.",
        "exceptions": None,
    },
    "criminal_prediction": {
        "patterns": [r"crime.?predict", r"criminal.?risk.?assess", r"predictive.?policing", r"recidivism"],
        "article": "5(1)(d)",
        "description": "Criminal risk prediction based solely on profiling or personality traits",
        "conditions": "Prohibited ONLY when based solely on profiling or personality traits. Systems using multiple evidence sources (case facts, prior convictions with human review) may be lawful.",
        "exceptions": "AI systems that support human assessment based on objective, verifiable facts directly linked to criminal activity are NOT prohibited.",
    },
    "facial_recognition_scraping": {
        "patterns": [r"\bface.?scrap", r"facial.?database.?untarget", r"mass.?facial.?collect"],
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
        "patterns": [r"\brace.?detect(?!.*(?:condition|thread|concurrent))", r"ethnicity.?infer", r"political.?opinion.?biometric",
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
        "patterns": [r"\bbiometric.?ident", r"\bface.?recogn", r"\bfingerprint.?recogn", r"\bvoice.?recogn"],
        "articles": ["9", "10", "11", "12", "13", "14", "15"],
        "category": "Annex III, Category 1",
        "description": "Biometric identification and categorisation",
    },
    "critical_infrastructure": {
        "patterns": [r"\benergy.?grid", r"\bwater.?supply", r"\btraffic.?control", r"\belectricity.?manage"],
        "articles": ["9", "10", "11", "12", "13", "14", "15"],
        "category": "Annex III, Category 2",
        "description": "Critical infrastructure management",
    },
    "education": {
        "patterns": [r"\badmission.?decision", r"\bstudent.?assess", r"\bexam.?scor", r"\bprocto\w*.{0,15}(exam|test|monitor|ai|automat|student|cheat)"],
        "articles": ["9", "10", "11", "12", "13", "14", "15"],
        "category": "Annex III, Category 3",
        "description": "Education and vocational training",
    },
    "employment": {
        "patterns": [r"\bcv.?screen", r"\bresume.?filt", r"\bhiring.?decision", r"\brecruit\w*\W{0,3}automat",
                     r"\bautomat\w*\W{0,3}recruit", r"\bcandidate.?rank", r"\bpromotion.?decision",
                     r"\btermination.?decision", r"\bperformance.?review.{0,10}(ai|automat|model|predict)"],
        "articles": ["9", "10", "11", "12", "13", "14", "15"],
        "category": "Annex III, Category 4",
        "description": "Employment and workers management",
    },
    "essential_services": {
        "patterns": [r"\bcredit.?scor", r"\bcreditworth", r"\bloan.?decision", r"\binsurance.?pric",
                     r"\bbenefit.?eligib", r"\bemergency.?dispatch",
                     r"\bcredit.?risk", r"\bcredit.?model", r"\bcredit.?predict",
                     r"\bloan.?approv", r"\blending.?decision"],
        "articles": ["9", "10", "11", "12", "13", "14", "15"],
        "category": "Annex III, Category 5",
        "description": "Access to essential services",
    },
    "law_enforcement": {
        "patterns": [r"\bpolygraph", r"\blie.?detect", r"\bevidence.?reliab", r"\bcriminal.?investigat"],
        "articles": ["9", "10", "11", "12", "13", "14", "15"],
        "category": "Annex III, Category 6",
        "description": "Law enforcement",
    },
    "migration": {
        "patterns": [r"\bborder.?control", r"\bvisa.?application", r"\basylum.?application", r"\bimmigration.?decision"],
        "articles": ["9", "10", "11", "12", "13", "14", "15"],
        "category": "Annex III, Category 7",
        "description": "Migration, asylum, and border control",
    },
    "justice": {
        "patterns": [r"\bjudicial.?decision", r"\bcourt.?rul", r"\bsentenc(ing|e\.?)\W{0,5}(recommend|decision|guidelines|court|judge|judicial|legal|verdict|criminal|prison|convict|parole|probation)", r"\belection.?influence"],
        "articles": ["9", "10", "11", "12", "13", "14", "15"],
        "category": "Annex III, Category 8",
        "description": "Justice and democratic processes",
    },
    "medical_devices": {
        "patterns": [r"\bmedical.?diagnos", r"\bclinical.?decision", r"\btreatment.?recommend", r"\bpatient.?triage"],
        "articles": ["9", "10", "11", "12", "13", "14", "15"],
        "category": "Medical Devices",
        "description": "AI components of medical devices",
    },
    "safety_components": {
        "patterns": [r"\bautonomous.?vehicle", r"\bself.?driv", r"\baviation.?safety", r"\bmachinery.?safety"],
        "articles": ["9", "10", "11", "12", "13", "14", "15"],
        "category": "Safety Components",
        "description": "Safety components under Union harmonisation legislation",
    },
}

LIMITED_RISK_PATTERNS = {
    "chatbots": {
        "patterns": [r"\bchatbot", r"conversational.?ai", r"virtual.?assist", r"support.?bot\b"],
        "article": "50",
        "description": "Chatbots and conversational AI",
    },
    "emotion_recognition": {
        "patterns": [r"emotion.?recogn", r"sentiment.?analy", r"affect.?detect", r"mood.?analy"],
        "article": "50",
        "description": "Emotion recognition systems",
    },
    "biometric_categorisation": {
        "patterns": [r"\bage.?estimat", r"\bgender.?detect", r"\bdemographic.?analy"],
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

# ---------------------------------------------------------------------------
# AI Security Antipatterns — Code patterns that indicate AI-specific
# vulnerabilities.  These map to OWASP LLM Top 10 and are reported as
# Article 15 (cybersecurity) findings.
# ---------------------------------------------------------------------------

AI_SECURITY_PATTERNS = {
    "unsafe_deserialization": {
        "patterns": [
            r"pickle\.load",
            r"pickle\.loads",
            r"torch\.load\s*\([^)]*\)",  # torch.load without weights_only=True
            r"joblib\.load",
            r"dill\.load",
        ],
        "owasp": "LLM05",
        "description": "Unsafe model deserialization — arbitrary code execution risk",
        "severity": "high",
        "remediation": "Use safetensors format or torch.load(path, weights_only=True). Never unpickle untrusted model files.",
    },
    "prompt_injection_vulnerable": {
        "patterns": [
            r"f['\"][^'\"]{0,500}\{[^}]{0,200}user[^}]{0,200}\}[^'\"]{0,500}['\"][^\n]{0,500}(?:messages|prompt|system)",  # f-string with user input in prompt
            r"\.format\([^)]{0,500}user[^)]{0,500}\)[^\n]{0,500}(?:messages|prompt|content)",  # .format with user input in prompt
            r"\+\s*(?:user_input|user_message|request\.body|req\.body)[^\n]{0,500}(?:messages|prompt)",  # string concat user input to prompt
        ],
        "owasp": "LLM01",
        "description": "User input directly concatenated into LLM prompt — prompt injection risk",
        "severity": "high",
        "remediation": "Use structured prompt templates with input sanitisation. Never concatenate raw user input into system prompts.",
    },
    "no_output_validation": {
        "patterns": [
            r"\beval\s*\([^\n]{0,500}(?:response|result|output|completion)",  # eval on AI output
            r"\bexec\s*\([^\n]{0,500}(?:response|result|output|completion)",  # exec on AI output
        ],
        "owasp": "LLM02",
        "description": "AI output used without validation — code injection risk",
        "severity": "critical",
        "remediation": "Never eval/exec AI model output. Validate and sanitise all AI-generated content before use.",
    },
    "hardcoded_model_path": {
        "patterns": [
            r"(?:from_pretrained|load_model|torch\.load)\s*\(\s*['\"]https?://",  # loading model from URL
            r"(?:from_pretrained|load_model|torch\.load)\s*\(\s*['\"](?:/tmp|/var|C:\\)",  # loading from temp/uncontrolled path
        ],
        "owasp": "LLM03",
        "description": "Model loaded from untrusted or hardcoded path — supply chain risk",
        "severity": "medium",
        "remediation": "Use model registries (HuggingFace Hub, MLflow) with integrity verification. Pin model revisions.",
    },
    "unbounded_token_generation": {
        "patterns": [
            r"max_tokens\s*[:=]\s*(?:None|0|-1|999999|1000000)",  # unbounded or very high token limit
        ],
        "owasp": "LLM10",
        "description": "Unbounded token generation — cost and resource exhaustion risk",
        "severity": "medium",
        "remediation": "Set explicit max_tokens limit. Add cost monitoring and rate limiting.",
    },
    "missing_temperature_control": {
        "patterns": [
            r"temperature\s*[:=]\s*(?:1\.0|2\.0|1\.5)",  # very high temperature for production
        ],
        "owasp": "LLM09",
        "description": "High temperature setting — increased hallucination risk in production",
        "severity": "low",
        "remediation": "Use temperature=0 or 0.1 for factual/production tasks. Reserve high temperature for creative tasks.",
    },
}

AI_INDICATORS = {
    "libraries": [r"tensorflow", r"torch", r"pytorch", r"transformers", r"langchain",
                  r"openai", r"anthropic", r"sklearn", r"scikit.?learn", r"keras",
                  r"xgboost", r"lightgbm", r"huggingface", r"spacy", r"nltk",
                  r"onnx", r"onnxruntime", r"brain\.js", r"@tensorflow/tfjs",
                  r"@anthropic-ai/sdk", r"@langchain", r"transformers\.js",
                  r"litellm", r"crewai", r"autogen", r"pyautogen",
                  r"haystack", r"smolagents", r"ollama",
                  r"google\.generativeai", r"mistralai", r"groq",
                  r"dspy", r"vertexai", r"semantic_kernel",
                  r"instructor", r"pydantic_ai", r"together", r"replicate"],
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
