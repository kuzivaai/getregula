# regula-ignore
"""AI Bill of Materials generator.

Generates a structured inventory of AI components in a project,
classified by kind (inference-provider, ai-framework, vector-store, etc.).

Distinct from `regula sbom` which generates CycloneDX for ALL dependencies.
The AI BOM inventories only AI *capabilities* with compliance metadata.

Supports Annex IV/XI documentation but is not a regulatory requirement.
"""

import os
import re
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from constants import VERSION, MODEL_EXTENSIONS, SKIP_DIRS, CODE_EXTENSIONS
from dependency_scan import scan_dependencies, AI_LIBRARIES

# ── Component Kind Taxonomy ──────────────────────────────────────

COMPONENT_KIND_MAP: dict[str, str] = {
    # inference-provider
    "openai": "inference-provider",
    "anthropic": "inference-provider",
    "cohere": "inference-provider",
    "mistralai": "inference-provider",
    "groq": "inference-provider",
    "replicate": "inference-provider",
    "together": "inference-provider",
    "litellm": "inference-provider",
    # ai-framework
    "tensorflow": "ai-framework",
    "torch": "ai-framework",
    "pytorch": "ai-framework",
    "jax": "ai-framework",
    "flax": "ai-framework",
    "keras": "ai-framework",
    "sklearn": "ai-framework",
    "scikit-learn": "ai-framework",
    "xgboost": "ai-framework",
    "lightgbm": "ai-framework",
    "catboost": "ai-framework",
    "transformers": "ai-framework",
    # vector-store
    "chromadb": "vector-store",
    "pinecone": "vector-store",
    "pinecone-client": "vector-store",
    "weaviate": "vector-store",
    "weaviate-client": "vector-store",
    "qdrant": "vector-store",
    "qdrant-client": "vector-store",
    "milvus": "vector-store",
    "faiss": "vector-store",
    # embedding
    "sentence-transformers": "embedding",
    # orchestration
    "langchain": "orchestration",
    "langchain-core": "orchestration",
    "langchain-community": "orchestration",
    "langchain-openai": "orchestration",
    "langchain-anthropic": "orchestration",
    "langchain-google-genai": "orchestration",
    "llama-index": "orchestration",
    "llama-index-core": "orchestration",
    "dspy": "orchestration",
    "dspy-ai": "orchestration",
    "semantic-kernel": "orchestration",
    "haystack": "orchestration",
    "haystack-ai": "orchestration",
    # runtime
    "ollama": "runtime",
    "vllm": "runtime",
    "bentoml": "runtime",
    "gradio": "runtime",
    "streamlit": "runtime",
    "llama-cpp-python": "runtime",
    "ctransformers": "runtime",
    # agent
    "crewai": "agent",
    "autogen": "agent",
    "instructor": "agent",
    "phidata": "agent",
    # guardrail
    "guardrails-ai": "guardrail",
    "nemoguardrails": "guardrail",
    # mlops
    "mlflow": "mlops",
    "wandb": "mlops",
    "optuna": "mlops",
    "ray": "mlops",
    "sagemaker": "mlops",
    # dataset-reference
    "datasets": "dataset-reference",
    "dvc": "dataset-reference",
    # NLP
    "spacy": "ai-framework",
    "nltk": "ai-framework",
    "gensim": "ai-framework",
    # ONNX
    "onnx": "ai-framework",
    "onnxruntime": "runtime",
    # JS/TS AI libs
    "@anthropic-ai/sdk": "inference-provider",
    "@tensorflow/tfjs": "ai-framework",
    "@langchain/core": "orchestration",
    "brain-js": "ai-framework",
    "@xenova/transformers": "ai-framework",
    "@huggingface/inference": "inference-provider",
    "@pinecone-database/pinecone": "vector-store",
    "@qdrant/js-client-rest": "vector-store",
    "weaviate-ts-client": "vector-store",
    # Rust crates
    "candle-core": "ai-framework",
    "candle-nn": "ai-framework",
    "candle-transformers": "ai-framework",
    "burn": "ai-framework",
    "burn-core": "ai-framework",
    "burn-tch": "ai-framework",
    "burn-ndarray": "ai-framework",
    "tch": "ai-framework",
    "ort": "runtime",
    "rust-bert": "ai-framework",
    "async-openai": "inference-provider",
    "misanthropic": "inference-provider",
    "langchain-rust": "orchestration",
    "llm-chain": "orchestration",
    "linfa": "ai-framework",
    "smartcore": "ai-framework",
    # C/C++ packages
    "libtorch": "ai-framework",
    "tensorflow-lite": "ai-framework",
    "mlpack": "ai-framework",
    "dlib": "ai-framework",
    # Transformers ecosystem
    "peft": "ai-framework",
    "trl": "ai-framework",
    "accelerate": "ai-framework",
    "diffusers": "ai-framework",
    "safetensors": "ai-framework",
    "huggingface-hub": "inference-provider",
    "tokenizers": "ai-framework",
    "hf-hub": "inference-provider",
    # Go modules (short names for matching)
    "langchaingo": "orchestration",
    "go-openai": "inference-provider",
    "generative-ai-go": "inference-provider",
    "anthropic-sdk-go": "inference-provider",
    # Java artifacts (group:artifact)
    "dev.langchain4j:langchain4j": "orchestration",
    "ai.djl:api": "ai-framework",
    "org.deeplearning4j:deeplearning4j-core": "ai-framework",
    "org.tensorflow:tensorflow-core-platform": "ai-framework",
    # Model serving
    "guidance": "orchestration",
    "outlines": "orchestration",
    # Unstructured
    "unstructured": "dataset-reference",
    # Vercel AI SDK (bare "ai" removed — false-positives on ai-* packages)
    "ai-sdk": "inference-provider",
    "@vercel/ai": "inference-provider",
}

# All valid kind values
VALID_KINDS = {
    "inference-provider", "ai-framework", "vector-store", "embedding",
    "orchestration", "model-file", "runtime", "agent", "mcp-server",
    "guardrail", "dataset-reference", "mlops",
}


def _normalize_name(name: str) -> str:
    """Normalise a package name for kind lookup.

    Lowercases and replaces underscores with hyphens to match
    COMPONENT_KIND_MAP keys.
    """
    return re.sub(r"[-_.]+", "-", name.strip().lower())


def _classify_kind(name: str) -> str:
    """Classify a dependency by its AI component kind.

    Tries exact match first, then prefix matching for namespaced
    packages (e.g. langchain-openai -> orchestration).
    """
    norm = _normalize_name(name)

    # Exact match
    if norm in COMPONENT_KIND_MAP:
        return COMPONENT_KIND_MAP[norm]

    # Also try the raw name (for Go modules with full paths, Java artifacts)
    if name in COMPONENT_KIND_MAP:
        return COMPONENT_KIND_MAP[name]

    # Prefix matching for namespaced packages
    for prefix, kind in COMPONENT_KIND_MAP.items():
        if norm.startswith(prefix + "-") or norm.startswith(prefix + "/"):
            return kind

    # Last-resort: check if the short name after the last slash matches
    # (useful for Go module paths like github.com/sashabaranov/go-openai)
    short = norm.rsplit("/", 1)[-1] if "/" in norm else norm
    if short in COMPONENT_KIND_MAP:
        return COMPONENT_KIND_MAP[short]

    return "ai-framework"  # default for unrecognised AI deps


def _scan_model_files(project_path: str) -> list[dict]:
    """Find model files in a project directory."""
    model_files: list[dict] = []
    root = Path(project_path)

    for dirpath, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for filename in files:
            filepath = Path(dirpath) / filename
            if filepath.suffix.lower() in MODEL_EXTENSIONS:
                rel_path = str(filepath.relative_to(root))
                try:
                    size_bytes = filepath.stat().st_size
                except OSError:
                    size_bytes = 0
                model_files.append({
                    "name": filename,
                    "path": rel_path,
                    "extension": filepath.suffix.lower(),
                    "size_bytes": size_bytes,
                })

    return model_files


def generate_aibom(project_path: str) -> dict:
    """Generate an AI Bill of Materials for a project.

    Returns dict with components list, summary, and metadata.
    Each component has: name, version, kind, files, risk_tier, articles.
    """
    root = Path(project_path).resolve()
    project_path_str = str(root)

    # Get AI dependencies from the existing scanner
    scan_result = scan_dependencies(project_path_str)
    ai_deps = scan_result.get("ai_dependencies", [])

    # Build components from AI dependencies
    components: list[dict] = []
    seen_names: set[str] = set()

    for dep in ai_deps:
        name = dep.get("name", "")
        if not name:
            continue
        norm = _normalize_name(name)
        if norm in seen_names:
            continue
        seen_names.add(norm)

        kind = _classify_kind(name)
        component = {
            "name": name,
            "version": dep.get("version") or "unknown",
            "kind": kind,
            "files": [dep.get("file", "manifest")],
            "source_line": dep.get("line", 0),
            "pinning": dep.get("pinning", "unknown"),
        }
        components.append(component)

    # Fallback: scan source code imports when no manifest deps found
    if not components:
        _AI_IMPORT_RE = re.compile(
            r"^\s*(?:from|import)\s+([\w.]+)", re.MULTILINE
        )
        _normalised_ai = {lib.replace("-", "_").lower() for lib in AI_LIBRARIES}
        for dirpath, dirs, files in os.walk(root):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            for filename in files:
                filepath = Path(dirpath) / filename
                if filepath.suffix.lower() not in CODE_EXTENSIONS:
                    continue
                try:
                    content = filepath.read_text(encoding="utf-8", errors="ignore")
                except OSError:
                    continue
                for match in _AI_IMPORT_RE.finditer(content):
                    module = match.group(1).split(".")[0].lower().replace("-", "_")
                    if module in _normalised_ai and module not in seen_names:
                        seen_names.add(module)
                        # Map back to canonical name for kind lookup
                        canonical = module.replace("_", "-")
                        kind = _classify_kind(canonical)
                        components.append({
                            "name": canonical,
                            "version": "unknown (from import)",
                            "kind": kind,
                            "files": [str(filepath.relative_to(root))],
                            "source_line": 0,
                            "pinning": "n/a",
                        })

    # Scan for model files
    model_files = _scan_model_files(project_path_str)
    for mf in model_files:
        mf_key = mf.get("path", mf["name"])
        if mf_key not in seen_names:
            seen_names.add(mf_key)
            components.append({
                "name": mf["name"],
                "version": "n/a",
                "kind": "model-file",
                "files": [mf["path"]],
                "pinning": "n/a",
                "size_bytes": mf.get("size_bytes", 0),
            })

    # Sort: inference providers first, then frameworks, then alphabetical
    _kind_order = {
        "inference-provider": 0, "ai-framework": 1, "orchestration": 2,
        "agent": 3, "vector-store": 4, "embedding": 5, "runtime": 6,
        "guardrail": 7, "mlops": 8, "dataset-reference": 9,
        "model-file": 10, "mcp-server": 11,
    }
    components.sort(key=lambda c: (_kind_order.get(c["kind"], 99), c["name"]))

    # Build summary
    kinds_found: dict[str, int] = {}
    for c in components:
        kinds_found[c["kind"]] = kinds_found.get(c["kind"], 0) + 1

    return {
        "project": project_path_str,
        "regula_version": VERSION,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "components": components,
        "summary": {
            "total_components": len(components),
            "kinds": kinds_found,
        },
    }


def format_cyclonedx(aibom: dict) -> dict:
    """Format AI BOM as CycloneDX v1.7 JSON.

    Uses the regula:ai:kind custom property to tag each component
    with its AI taxonomy classification.
    """
    components = []
    for comp in aibom["components"]:
        cdx_comp: dict = {
            "type": "library",
            "name": comp["name"],
            "version": comp.get("version", "unknown"),
            "properties": [
                {"name": "regula:ai:kind", "value": comp["kind"]},
            ],
        }
        if comp["kind"] == "ai-framework":
            cdx_comp["type"] = "framework"
        elif comp["kind"] == "model-file":
            cdx_comp["type"] = "machine-learning-model"
        components.append(cdx_comp)

    return {
        "bomFormat": "CycloneDX",
        "specVersion": "1.7",
        "serialNumber": f"urn:uuid:{uuid.uuid4()}",
        "version": 1,
        "metadata": {
            "timestamp": aibom["generated_at"],
            "tools": {
                "components": [{
                    "type": "application",
                    "name": "regula",
                    "version": aibom["regula_version"],
                }],
            },
        },
        "components": components,
    }


def format_aibom_markdown(aibom: dict) -> str:
    """Format AI BOM as a Markdown table."""
    lines: list[str] = []
    lines.append("# AI Bill of Materials")
    lines.append("")
    lines.append(f"**Project:** {aibom['project']}")
    lines.append(f"**Generated:** {aibom['generated_at']}")
    lines.append(f"**Regula version:** {aibom['regula_version']}")
    lines.append("")

    components = aibom["components"]
    if not components:
        lines.append("No AI components detected.")
        return "\n".join(lines)

    lines.append("| Component | Kind | Version | Files |")
    lines.append("|-----------|------|---------|-------|")
    for c in components:
        files_str = ", ".join(c["files"][:3])
        if len(c["files"]) > 3:
            files_str += f" (+{len(c['files']) - 3} more)"
        lines.append(f"| {c['name']} | {c['kind']} | {c.get('version', '?')} | {files_str} |")

    lines.append("")
    summary = aibom["summary"]
    lines.append(f"**Total:** {summary['total_components']} AI component(s) "
                 f"across {len(summary['kinds'])} kind(s)")
    lines.append("")
    lines.append("*Note: AI BOM supports Annex IV/XI documentation "
                 "-- it is not a regulatory requirement.*")

    return "\n".join(lines)
