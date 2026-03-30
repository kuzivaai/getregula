# regula-ignore
"""Code analysis helpers for documentation auto-population.

Detects model architecture, data sources, human oversight, and logging
patterns from source code. All detections are heuristic and must be
marked as [AUTO-DETECTED — VERIFY] in generated documentation.
"""

import re
from pathlib import Path


# Architecture detection: import patterns → architecture description
ARCHITECTURE_PATTERNS = {
    "PyTorch (neural network)": [
        r"import\s+torch", r"from\s+torch", r"torch\.nn",
    ],
    "Transformer (HuggingFace)": [
        r"from\s+transformers\s+import", r"AutoModel", r"AutoTokenizer",
        r"from_pretrained",
    ],
    "TensorFlow / Keras": [
        r"import\s+tensorflow", r"from\s+tensorflow", r"import\s+keras",
        r"tf\.keras",
    ],
    "scikit-learn (traditional ML)": [
        r"from\s+sklearn", r"import\s+sklearn",
    ],
    "XGBoost": [r"import\s+xgboost", r"from\s+xgboost"],
    "LightGBM": [r"import\s+lightgbm", r"from\s+lightgbm"],
    "LangChain (RAG / agent)": [
        r"from\s+langchain", r"import\s+langchain",
    ],
    "LlamaIndex (RAG)": [
        r"from\s+llama_index", r"import\s+llama_index",
    ],
    "OpenAI API": [r"import\s+openai", r"from\s+openai"],
    "Anthropic API": [r"import\s+anthropic", r"from\s+anthropic"],
    "spaCy (NLP)": [r"import\s+spacy", r"from\s+spacy"],
    "ONNX Runtime": [r"import\s+onnxruntime", r"from\s+onnxruntime"],
    "LiteLLM (multi-provider proxy)": [
        r"from\s+litellm", r"import\s+litellm",
    ],
    "CrewAI (multi-agent orchestration)": [
        r"from\s+crewai", r"import\s+crewai",
    ],
    "AutoGen (multi-agent conversation)": [
        r"from\s+autogen", r"import\s+autogen", r"import\s+pyautogen", r"from\s+pyautogen",
    ],
    "Haystack (RAG / document pipeline)": [
        r"from\s+haystack", r"import\s+haystack",
    ],
    "smolagents (HuggingFace lightweight agents)": [
        r"from\s+smolagents", r"import\s+smolagents",
    ],
    "Ollama (local model inference)": [
        r"import\s+ollama", r"from\s+ollama",
    ],
    "Google Generative AI (Gemini API)": [
        r"import\s+google\.generativeai", r"from\s+google\.generativeai",
        r"import\s+google_generativeai",
    ],
    "Mistral AI SDK": [
        r"from\s+mistralai", r"import\s+mistralai",
    ],
    "Groq SDK": [
        r"from\s+groq\s+import", r"import\s+groq\b",
    ],
    "DSPy (programmatic LM pipelines)": [
        r"import\s+dspy\b", r"from\s+dspy",
    ],
    "AWS Bedrock": [
        r"bedrock(?:_runtime|_agent)?",
        r"boto3.*bedrock", r"botocore.*bedrock",
    ],
    "Google Vertex AI": [
        r"from\s+vertexai", r"import\s+vertexai",
        r"google\.cloud\.aiplatform",
    ],
    "Semantic Kernel (Microsoft)": [
        r"from\s+semantic_kernel", r"import\s+semantic_kernel",
    ],
    "Instructor (structured LLM output)": [
        r"from\s+instructor", r"import\s+instructor\b",
    ],
    "PydanticAI (type-safe agents)": [
        r"from\s+pydantic_ai", r"import\s+pydantic_ai",
    ],
    "Together AI": [
        r"from\s+together\s+import", r"import\s+together\b",
    ],
    "Replicate": [
        r"import\s+replicate\b", r"from\s+replicate",
    ],
}

# Data source detection: code patterns → data source description
DATA_SOURCE_PATTERNS = {
    "CSV files": [
        r"pd\.read_csv", r"csv\.reader", r"csv\.DictReader",
        r"read_csv\(", r"\.csv['\"]",
    ],
    "Database (SQLAlchemy)": [
        r"from\s+sqlalchemy", r"import\s+sqlalchemy", r"create_engine\(",
    ],
    "Database (psycopg2 / PostgreSQL)": [
        r"import\s+psycopg2", r"from\s+psycopg2",
    ],
    "Database (pymysql / MySQL)": [
        r"import\s+pymysql", r"from\s+pymysql",
    ],
    "Database (sqlite3)": [
        r"import\s+sqlite3", r"sqlite3\.connect",
    ],
    "HTTP API": [
        r"requests\.get\(", r"requests\.post\(", r"httpx\.",
        r"aiohttp\.ClientSession",
    ],
    "AWS S3": [
        r"boto3\.client\(['\"]s3", r"boto3\.resource\(['\"]s3",
    ],
    "JSON files": [
        r"json\.load\(", r"\.json['\"]",
    ],
    "Parquet files": [
        r"read_parquet\(", r"\.parquet['\"]",
    ],
    "HuggingFace datasets": [
        r"from\s+datasets\s+import", r"load_dataset\(",
    ],
}

# Human oversight patterns
OVERSIGHT_PATTERNS = {
    "Human review gate": [
        r"human_review", r"human_in_the_loop", r"hitl",
        r"manual_review", r"manual_check",
    ],
    "Approval mechanism": [
        r"approval_required", r"send_for_approval", r"queue_for_review",
        r"flag_for_review", r"if\s+approved",
    ],
    "Override capability": [
        r"override", r"escalat", r"supervisor",
    ],
    "Confirmation prompt": [
        r"input\(['\"].*(?:proceed|confirm|approve)",
        r"click\.confirm", r"if\s+confirmed",
    ],
}

# Logging patterns
LOGGING_PATTERNS = {
    "Python logging module": [
        r"import\s+logging", r"logging\.getLogger",
        r"logger\.info", r"logger\.warning", r"logger\.error",
    ],
    "Structured logging (structlog)": [
        r"import\s+structlog", r"from\s+structlog",
    ],
    "Audit logging": [
        r"audit_log", r"log_event", r"audit_trail",
    ],
    "Print-based logging": [
        r"print\(.*log", r"print\(.*debug",
    ],
}


def detect_architectures(text: str) -> list:
    """Detect AI model architectures from code.

    Returns list of architecture description strings.
    """
    found = []
    for arch, patterns in ARCHITECTURE_PATTERNS.items():
        if any(re.search(p, text, re.IGNORECASE) for p in patterns):
            found.append(arch)
    return found


def detect_data_sources(text: str) -> list:
    """Detect data source patterns in code.

    Returns list of data source description strings.
    """
    found = []
    for source, patterns in DATA_SOURCE_PATTERNS.items():
        if any(re.search(p, text) for p in patterns):
            found.append(source)
    return found


def detect_oversight(text: str) -> list:
    """Detect human oversight patterns in code.

    Returns list of oversight mechanism description strings.
    """
    found = []
    for mechanism, patterns in OVERSIGHT_PATTERNS.items():
        if any(re.search(p, text, re.IGNORECASE) for p in patterns):
            found.append(mechanism)
    return found


def detect_logging(text: str) -> list:
    """Detect logging patterns in code.

    Returns list of logging mechanism description strings.
    """
    found = []
    for mechanism, patterns in LOGGING_PATTERNS.items():
        if any(re.search(p, text, re.IGNORECASE) for p in patterns):
            found.append(mechanism)
    return found


def analyse_project_code(project_path: str) -> dict:
    """Run all detection across all code files in a project.

    Returns aggregated results with deduplicated findings.
    """
    project = Path(project_path).resolve()
    skip_dirs = {".git", "node_modules", "__pycache__", "venv", ".venv",
                 "dist", "build", ".next", ".tox", "tests"}
    code_extensions = {".py", ".js", ".ts", ".jsx", ".tsx"}

    all_architectures = set()
    all_data_sources = set()
    all_oversight = set()
    all_logging = set()

    for filepath in project.rglob("*"):
        if any(d in filepath.parts for d in skip_dirs):
            continue
        if filepath.suffix not in code_extensions:
            continue
        try:
            text = filepath.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue

        all_architectures.update(detect_architectures(text))
        all_data_sources.update(detect_data_sources(text))
        all_oversight.update(detect_oversight(text))
        all_logging.update(detect_logging(text))

    return {
        "architectures": sorted(all_architectures),
        "data_sources": sorted(all_data_sources),
        "oversight": sorted(all_oversight),
        "logging": sorted(all_logging),
    }
