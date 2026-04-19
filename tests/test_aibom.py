"""Tests for the AI Bill of Materials generator (scripts/aibom.py)."""

import json
import os
import sys
import tempfile
from pathlib import Path

# Ensure scripts directory is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from aibom import (
    COMPONENT_KIND_MAP,
    VALID_KINDS,
    generate_aibom,
    format_cyclonedx,
    format_aibom_markdown,
    _classify_kind,
    _normalize_name,
    _scan_model_files,
)


# ── COMPONENT_KIND_MAP coverage ──────────────────────────────────


def test_all_kind_values_are_valid():
    """Every value in COMPONENT_KIND_MAP must be a member of VALID_KINDS."""
    for lib, kind in COMPONENT_KIND_MAP.items():
        assert kind in VALID_KINDS, f"{lib} mapped to unknown kind '{kind}'"


def test_kind_map_covers_core_inference_providers():
    """Core inference provider libraries must be mapped."""
    for lib in ("openai", "anthropic", "cohere", "mistralai", "groq", "replicate"):
        assert COMPONENT_KIND_MAP.get(lib) == "inference-provider", f"{lib} not mapped to inference-provider"


def test_kind_map_covers_core_frameworks():
    """Core AI framework libraries must be mapped."""
    for lib in ("tensorflow", "torch", "jax", "keras", "sklearn", "scikit-learn"):
        assert COMPONENT_KIND_MAP.get(lib) == "ai-framework", f"{lib} not mapped to ai-framework"


def test_kind_map_covers_vector_stores():
    """Vector store libraries must be mapped."""
    for lib in ("chromadb", "pinecone-client", "weaviate-client", "qdrant-client", "milvus", "faiss"):
        assert COMPONENT_KIND_MAP.get(lib) == "vector-store", f"{lib} not mapped to vector-store"


def test_kind_map_covers_orchestration():
    """Orchestration libraries must be mapped."""
    for lib in ("langchain", "langchain-core", "llama-index", "dspy-ai", "haystack-ai"):
        assert COMPONENT_KIND_MAP.get(lib) == "orchestration", f"{lib} not mapped to orchestration"


def test_kind_map_covers_agents():
    """Agent libraries must be mapped."""
    for lib in ("crewai", "autogen", "instructor"):
        assert COMPONENT_KIND_MAP.get(lib) == "agent", f"{lib} not mapped to agent"


def test_kind_map_covers_mlops():
    """MLOps libraries must be mapped."""
    for lib in ("mlflow", "wandb", "optuna", "ray"):
        assert COMPONENT_KIND_MAP.get(lib) == "mlops", f"{lib} not mapped to mlops"


# ── _classify_kind ───────────────────────────────────────────────


def test_classify_kind_exact_match():
    assert _classify_kind("openai") == "inference-provider"
    assert _classify_kind("torch") == "ai-framework"
    assert _classify_kind("chromadb") == "vector-store"


def test_classify_kind_normalises_underscores():
    assert _classify_kind("scikit_learn") == "ai-framework"


def test_classify_kind_case_insensitive():
    assert _classify_kind("OpenAI") == "inference-provider"
    assert _classify_kind("TensorFlow") == "ai-framework"


def test_classify_kind_prefix_match():
    """Namespaced packages should match by prefix."""
    assert _classify_kind("langchain-extra-stuff") == "orchestration"


def test_classify_kind_unknown_defaults_to_framework():
    """Unrecognised AI deps should default to ai-framework."""
    assert _classify_kind("some-unknown-ai-lib") == "ai-framework"


# ── _normalize_name ──────────────────────────────────────────────


def test_normalize_name_lowercase():
    assert _normalize_name("OpenAI") == "openai"


def test_normalize_name_underscores_to_hyphens():
    assert _normalize_name("sentence_transformers") == "sentence-transformers"


def test_normalize_name_dots_to_hyphens():
    assert _normalize_name("brain.js") == "brain-js"


# ── generate_aibom ───────────────────────────────────────────────


def test_generate_aibom_empty_project():
    """An empty project should return an empty components list."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = generate_aibom(tmpdir)
        assert isinstance(result, dict)
        assert result["components"] == []
        assert result["summary"]["total_components"] == 0
        assert result["summary"]["kinds"] == {}
        assert "project" in result
        assert "regula_version" in result
        assert "generated_at" in result


def test_generate_aibom_with_requirements():
    """Should detect AI deps from requirements.txt."""
    with tempfile.TemporaryDirectory() as tmpdir:
        req = Path(tmpdir) / "requirements.txt"
        req.write_text("openai==1.30.0\nflask==3.0.0\ntorch==2.1.0\n")
        result = generate_aibom(tmpdir)
        names = [c["name"] for c in result["components"]]
        assert "openai" in names
        assert "torch" in names
        # flask is not an AI dep, should not appear
        assert "flask" not in names


def test_generate_aibom_component_structure():
    """Each component must have required fields."""
    with tempfile.TemporaryDirectory() as tmpdir:
        req = Path(tmpdir) / "requirements.txt"
        req.write_text("langchain==0.1.0\n")
        result = generate_aibom(tmpdir)
        assert len(result["components"]) >= 1
        comp = result["components"][0]
        assert "name" in comp
        assert "kind" in comp
        assert "version" in comp
        assert "files" in comp
        assert isinstance(comp["files"], list)


def test_generate_aibom_deduplicates():
    """Same library in multiple manifest files should not appear twice."""
    with tempfile.TemporaryDirectory() as tmpdir:
        req = Path(tmpdir) / "requirements.txt"
        req.write_text("openai==1.0.0\n")
        pkg = Path(tmpdir) / "package.json"
        pkg.write_text(json.dumps({"dependencies": {"openai": "^4.0.0"}}))
        result = generate_aibom(tmpdir)
        openai_comps = [c for c in result["components"] if _normalize_name(c["name"]) == "openai"]
        assert len(openai_comps) == 1


def test_generate_aibom_model_files():
    """Model files should be classified as model-file kind."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a fake model file
        model = Path(tmpdir) / "model.pt"
        model.write_bytes(b"\x00" * 100)
        onnx = Path(tmpdir) / "encoder.onnx"
        onnx.write_bytes(b"\x00" * 50)
        result = generate_aibom(tmpdir)
        model_comps = [c for c in result["components"] if c["kind"] == "model-file"]
        assert len(model_comps) == 2
        names = {c["name"] for c in model_comps}
        assert "model.pt" in names
        assert "encoder.onnx" in names


def test_generate_aibom_summary_kinds():
    """Summary should correctly count kinds."""
    with tempfile.TemporaryDirectory() as tmpdir:
        req = Path(tmpdir) / "requirements.txt"
        req.write_text("openai==1.0.0\ntorch==2.0.0\nchromadb==0.4.0\n")
        result = generate_aibom(tmpdir)
        kinds = result["summary"]["kinds"]
        assert "inference-provider" in kinds
        assert "ai-framework" in kinds
        assert "vector-store" in kinds


def test_generate_aibom_sorts_components():
    """Components should be sorted by kind order then name."""
    with tempfile.TemporaryDirectory() as tmpdir:
        req = Path(tmpdir) / "requirements.txt"
        req.write_text("chromadb==0.4.0\nopenai==1.0.0\ntorch==2.0.0\n")
        result = generate_aibom(tmpdir)
        kinds_in_order = [c["kind"] for c in result["components"]]
        # inference-provider (0) should come before ai-framework (1)
        # which should come before vector-store (4)
        ip_idx = kinds_in_order.index("inference-provider")
        af_idx = kinds_in_order.index("ai-framework")
        vs_idx = kinds_in_order.index("vector-store")
        assert ip_idx < af_idx < vs_idx


# ── _scan_model_files ────────────────────────────────────────────


def test_scan_model_files_finds_models():
    """Should find .pt, .h5, .onnx, .safetensors, .gguf files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        for name in ("model.pt", "weights.h5", "net.onnx", "lora.safetensors", "llm.gguf"):
            (Path(tmpdir) / name).write_bytes(b"\x00" * 10)
        # Non-model file
        (Path(tmpdir) / "readme.txt").write_text("not a model")
        results = _scan_model_files(tmpdir)
        assert len(results) == 5
        names = {r["name"] for r in results}
        assert "model.pt" in names
        assert "weights.h5" in names
        assert "net.onnx" in names
        assert "lora.safetensors" in names
        assert "llm.gguf" in names


def test_scan_model_files_skips_excluded_dirs():
    """Should not scan inside SKIP_DIRS like node_modules."""
    with tempfile.TemporaryDirectory() as tmpdir:
        nm = Path(tmpdir) / "node_modules"
        nm.mkdir()
        (nm / "model.pt").write_bytes(b"\x00" * 10)
        results = _scan_model_files(tmpdir)
        assert len(results) == 0


def test_scan_model_files_empty_dir():
    """Empty directory should return empty list."""
    with tempfile.TemporaryDirectory() as tmpdir:
        results = _scan_model_files(tmpdir)
        assert results == []


# ── format_cyclonedx ─────────────────────────────────────────────


def test_cyclonedx_structure():
    """CycloneDX output must have required top-level fields."""
    aibom = {
        "project": "/tmp/test",
        "regula_version": "1.7.0",
        "generated_at": "2026-04-18T00:00:00Z",
        "components": [
            {"name": "openai", "version": "1.30.0", "kind": "inference-provider",
             "files": ["requirements.txt"], "pinning": "exact"},
        ],
        "summary": {"total_components": 1, "kinds": {"inference-provider": 1}},
    }
    cdx = format_cyclonedx(aibom)
    assert cdx["bomFormat"] == "CycloneDX"
    assert cdx["specVersion"] == "1.7"
    assert cdx["version"] == 1
    assert cdx["serialNumber"].startswith("urn:uuid:")
    assert "metadata" in cdx
    assert "components" in cdx
    assert cdx["metadata"]["timestamp"] == "2026-04-18T00:00:00Z"


def test_cyclonedx_component_types():
    """CycloneDX should use correct component types based on kind."""
    aibom = {
        "project": "/tmp/test",
        "regula_version": "1.7.0",
        "generated_at": "2026-04-18T00:00:00Z",
        "components": [
            {"name": "openai", "version": "1.0", "kind": "inference-provider",
             "files": [], "pinning": "exact"},
            {"name": "torch", "version": "2.0", "kind": "ai-framework",
             "files": [], "pinning": "exact"},
            {"name": "model.pt", "version": "n/a", "kind": "model-file",
             "files": ["model.pt"], "pinning": "n/a"},
        ],
        "summary": {"total_components": 3, "kinds": {}},
    }
    cdx = format_cyclonedx(aibom)
    types = {c["name"]: c["type"] for c in cdx["components"]}
    assert types["openai"] == "library"
    assert types["torch"] == "framework"
    assert types["model.pt"] == "machine-learning-model"


def test_cyclonedx_custom_properties():
    """Each CycloneDX component should have regula:ai:kind property."""
    aibom = {
        "project": "/tmp/test",
        "regula_version": "1.7.0",
        "generated_at": "2026-04-18T00:00:00Z",
        "components": [
            {"name": "langchain", "version": "0.1.0", "kind": "orchestration",
             "files": [], "pinning": "range"},
        ],
        "summary": {"total_components": 1, "kinds": {"orchestration": 1}},
    }
    cdx = format_cyclonedx(aibom)
    comp = cdx["components"][0]
    prop_names = [p["name"] for p in comp["properties"]]
    assert "regula:ai:kind" in prop_names
    kind_prop = next(p for p in comp["properties"] if p["name"] == "regula:ai:kind")
    assert kind_prop["value"] == "orchestration"


def test_cyclonedx_tools_metadata():
    """CycloneDX metadata should include Regula tool info in v1.5+ format."""
    aibom = {
        "project": "/tmp/test",
        "regula_version": "1.7.0",
        "generated_at": "2026-04-18T00:00:00Z",
        "components": [],
        "summary": {"total_components": 0, "kinds": {}},
    }
    cdx = format_cyclonedx(aibom)
    tools = cdx["metadata"]["tools"]
    assert isinstance(tools, dict), "tools must be a dict (v1.5+ format)"
    assert "components" in tools
    assert len(tools["components"]) == 1
    assert tools["components"][0]["type"] == "application"
    assert tools["components"][0]["name"] == "regula"


# ── format_aibom_markdown ────────────────────────────────────────


def test_markdown_empty():
    """Empty project should produce 'No AI components detected' message."""
    aibom = {
        "project": "/tmp/test",
        "regula_version": "1.7.0",
        "generated_at": "2026-04-18T00:00:00Z",
        "components": [],
        "summary": {"total_components": 0, "kinds": {}},
    }
    md = format_aibom_markdown(aibom)
    assert "No AI components detected" in md


def test_markdown_table_format():
    """Markdown output should include a table header."""
    aibom = {
        "project": "/tmp/test",
        "regula_version": "1.7.0",
        "generated_at": "2026-04-18T00:00:00Z",
        "components": [
            {"name": "openai", "version": "1.30.0", "kind": "inference-provider",
             "files": ["requirements.txt"], "pinning": "exact"},
        ],
        "summary": {"total_components": 1, "kinds": {"inference-provider": 1}},
    }
    md = format_aibom_markdown(aibom)
    assert "| Component | Kind | Version | Files |" in md
    assert "openai" in md
    assert "inference-provider" in md


def test_markdown_includes_note():
    """Markdown output should include the Annex IV/XI note."""
    aibom = {
        "project": "/tmp/test",
        "regula_version": "1.7.0",
        "generated_at": "2026-04-18T00:00:00Z",
        "components": [
            {"name": "torch", "version": "2.0", "kind": "ai-framework",
             "files": [], "pinning": "exact"},
        ],
        "summary": {"total_components": 1, "kinds": {"ai-framework": 1}},
    }
    md = format_aibom_markdown(aibom)
    assert "Annex IV/XI" in md
    assert "not a regulatory requirement" in md
