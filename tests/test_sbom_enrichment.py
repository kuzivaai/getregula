"""Tests for AI-BOM enrichment and NIST AI RMF YAML deepening."""

import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import helpers
from helpers import assert_eq, assert_true, assert_none


# ── GPAI tier detection tests ───────────────────────────────────

def test_gpai_tier_openai():
    from sbom import _detect_gpai_tier
    result = _detect_gpai_tier("openai")
    assert_true(result is not None, "openai should be detected")
    assert_eq(result["provider"], "OpenAI", "openai provider")
    assert_eq(result["tier"], "systemic", "openai tier")
    assert_eq(result["obligations"], "Art 53, Art 55", "openai obligations")


def test_gpai_tier_anthropic():
    from sbom import _detect_gpai_tier
    result = _detect_gpai_tier("anthropic")
    assert_true(result is not None, "anthropic should be detected")
    assert_eq(result["provider"], "Anthropic", "anthropic provider")
    assert_eq(result["tier"], "systemic", "anthropic tier")


def test_gpai_tier_google():
    from sbom import _detect_gpai_tier
    result = _detect_gpai_tier("google-generativeai")
    assert_true(result is not None, "google-generativeai should be detected")
    assert_eq(result["provider"], "Google DeepMind", "google provider")
    assert_eq(result["tier"], "systemic", "google tier")


def test_gpai_tier_mistral():
    from sbom import _detect_gpai_tier
    result = _detect_gpai_tier("mistralai")
    assert_true(result is not None, "mistralai should be detected")
    assert_eq(result["provider"], "Mistral AI", "mistral provider")
    assert_eq(result["tier"], "systemic", "mistral tier")


def test_gpai_tier_transformers():
    from sbom import _detect_gpai_tier
    result = _detect_gpai_tier("transformers")
    assert_true(result is not None, "transformers should be detected")
    assert_eq(result["provider"], "Hugging Face", "transformers provider")
    assert_eq(result["tier"], "general", "transformers tier")
    assert_eq(result["obligations"], "Art 53", "transformers obligations")


def test_gpai_tier_torch():
    from sbom import _detect_gpai_tier
    result = _detect_gpai_tier("torch")
    assert_true(result is not None, "torch should be detected")
    assert_eq(result["tier"], "general", "torch tier")


def test_gpai_tier_ollama():
    from sbom import _detect_gpai_tier
    result = _detect_gpai_tier("ollama")
    assert_true(result is not None, "ollama should be detected")
    assert_eq(result["tier"], "local", "ollama tier")
    assert_eq(result["obligations"], "None (local deployment)", "ollama obligations")


def test_gpai_tier_llama_cpp():
    from sbom import _detect_gpai_tier
    result = _detect_gpai_tier("llama-cpp-python")
    assert_true(result is not None, "llama-cpp-python should be detected")
    assert_eq(result["tier"], "local", "llama-cpp-python tier")


def test_gpai_tier_unknown():
    from sbom import _detect_gpai_tier
    result = _detect_gpai_tier("requests")
    assert_none(result, "requests should not be a GPAI provider")


def test_gpai_tier_unknown_flask():
    from sbom import _detect_gpai_tier
    result = _detect_gpai_tier("flask")
    assert_none(result, "flask should not be a GPAI provider")


def test_gpai_tier_normalisation():
    from sbom import _detect_gpai_tier
    result = _detect_gpai_tier("llama_cpp_python")
    assert_true(result is not None, "underscore variant should normalise")
    assert_eq(result["tier"], "local", "normalised tier")


# ── Dataset file detection tests ────────────────────────────────

def test_detect_dataset_files_csv():
    from sbom import _detect_dataset_files
    with tempfile.TemporaryDirectory() as tmpdir:
        train_dir = Path(tmpdir) / "data" / "train"
        train_dir.mkdir(parents=True)
        (train_dir / "features.csv").write_text("a,b,c\n1,2,3\n")
        results = _detect_dataset_files(tmpdir)
        assert_eq(len(results), 1, "should find 1 csv")
        assert_eq(results[0]["format"], "csv", "format should be csv")
        assert_eq(results[0]["purpose_hint"], "train", "purpose from dir name")


def test_detect_dataset_files_multiple():
    from sbom import _detect_dataset_files
    with tempfile.TemporaryDirectory() as tmpdir:
        (Path(tmpdir) / "data.jsonl").write_text('{"a":1}\n')
        (Path(tmpdir) / "data.parquet").write_bytes(b"\x00" * 10)
        results = _detect_dataset_files(tmpdir)
        assert_eq(len(results), 2, "should find 2 dataset files")
        formats = {r["format"] for r in results}
        assert_true("jsonl" in formats, "jsonl found")
        assert_true("parquet" in formats, "parquet found")


def test_detect_dataset_files_empty_project():
    from sbom import _detect_dataset_files
    with tempfile.TemporaryDirectory() as tmpdir:
        results = _detect_dataset_files(tmpdir)
        assert_eq(len(results), 0, "empty project has no datasets")


# ── Model metadata extraction tests ─────────────────────────────

def test_extract_model_metadata_config_json():
    from sbom import _extract_model_metadata
    with tempfile.TemporaryDirectory() as tmpdir:
        config = {"model_type": "bert", "hidden_size": 768}
        (Path(tmpdir) / "config.json").write_text(json.dumps(config))
        results = _extract_model_metadata(tmpdir)
        assert_eq(len(results), 1, "should find config.json")
        assert_eq(results[0]["format"], "json", "format is json")
        assert_true("model_type" in results[0]["fields_found"], "fields extracted")


def test_extract_model_metadata_binary():
    from sbom import _extract_model_metadata
    with tempfile.TemporaryDirectory() as tmpdir:
        (Path(tmpdir) / "model.safetensors").write_bytes(b"\x00" * 10)
        results = _extract_model_metadata(tmpdir)
        assert_eq(len(results), 1, "should find safetensors file")
        assert_eq(results[0]["format"], "binary", "format is binary")


def test_extract_model_metadata_empty():
    from sbom import _extract_model_metadata
    with tempfile.TemporaryDirectory() as tmpdir:
        (Path(tmpdir) / "app.py").write_text("print('hello')")
        results = _extract_model_metadata(tmpdir)
        assert_eq(len(results), 0, "no model metadata in plain project")


# ── NIST framework mapping tests ────────────────────────────────

def test_nist_mapping_loads():
    from framework_mapper import map_to_frameworks
    result = map_to_frameworks(["9", "10", "11", "12", "13", "14", "15"], ["nist-ai-rmf"])
    for art in ["9", "10", "11", "12", "13", "14", "15"]:
        assert_true(art in result, f"article {art} in result")
        nist = result[art].get("nist_ai_rmf", {})
        assert_true(len(nist.get("subcategories", [])) > 0, f"article {art} has NIST subcategories")


def test_nist_article_9_comprehensive():
    from framework_mapper import map_to_frameworks
    result = map_to_frameworks(["9"], ["nist-ai-rmf"])
    subcats = result["9"]["nist_ai_rmf"]["subcategories"]
    # Should have GOVERN, MAP, and MANAGE subcategories
    has_govern = any("GOVERN" in s for s in subcats)
    has_map = any("MAP" in s for s in subcats)
    has_manage = any("MANAGE" in s for s in subcats)
    assert_true(has_govern, "Art 9 has GOVERN subcategories")
    assert_true(has_map, "Art 9 has MAP subcategories")
    assert_true(has_manage, "Art 9 has MANAGE subcategories")
    assert_true(len(subcats) >= 10, f"Art 9 should have >= 10 subcategories, got {len(subcats)}")


def test_nist_article_15_measure_focus():
    from framework_mapper import map_to_frameworks
    result = map_to_frameworks(["15"], ["nist-ai-rmf"])
    subcats = result["15"]["nist_ai_rmf"]["subcategories"]
    measure_count = sum(1 for s in subcats if "MEASURE" in s)
    assert_true(measure_count >= 6, f"Art 15 should have >= 6 MEASURE subcategories, got {measure_count}")


def test_nist_article_12_record_keeping():
    from framework_mapper import map_to_frameworks
    result = map_to_frameworks(["12"], ["nist-ai-rmf"])
    subcats = result["12"]["nist_ai_rmf"]["subcategories"]
    assert_true(len(subcats) >= 5, f"Art 12 should have >= 5 subcategories, got {len(subcats)}")
    has_govern = any("GOVERN 6" in s for s in subcats)
    assert_true(has_govern, "Art 12 should have GOVERN 6.x subcategories")


def test_nist_article_13_transparency():
    from framework_mapper import map_to_frameworks
    result = map_to_frameworks(["13"], ["nist-ai-rmf"])
    subcats = result["13"]["nist_ai_rmf"]["subcategories"]
    has_govern5 = any("GOVERN 5" in s for s in subcats)
    assert_true(has_govern5, "Art 13 should have GOVERN 5.x subcategories")


def test_nist_article_14_human_oversight():
    from framework_mapper import map_to_frameworks
    result = map_to_frameworks(["14"], ["nist-ai-rmf"])
    subcats = result["14"]["nist_ai_rmf"]["subcategories"]
    has_map4 = any("MAP 4" in s for s in subcats)
    has_manage4 = any("MANAGE 4" in s for s in subcats)
    assert_true(has_map4, "Art 14 should have MAP 4.x subcategories")
    assert_true(has_manage4, "Art 14 should have MANAGE 4.x subcategories")


# ── AI-BOM properties in SBOM test ──────────────────────────────

def test_ai_bom_properties_added():
    from sbom import generate_sbom
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a minimal project with a requirements.txt containing an AI dep
        (Path(tmpdir) / "requirements.txt").write_text("openai==1.0.0\n")
        (Path(tmpdir) / "app.py").write_text("import openai\n")
        sbom = generate_sbom(tmpdir, ai_bom=True)
        meta_props = sbom.get("metadata", {}).get("properties", [])
        prop_names = [p["name"] for p in meta_props]
        assert_true("regula:ai-bom" in prop_names, "ai-bom flag in metadata")
        assert_true("regula:transitive-ai-deps" in prop_names, "transitive-ai-deps in metadata")
        assert_true("regula:has-upstream-sbom" in prop_names, "has-upstream-sbom in metadata")
        assert_true("regula:article-9-applicable" in prop_names, "article-9-applicable in metadata")
        assert_true("regula:article-10-applicable" in prop_names, "article-10-applicable in metadata")
        assert_true("regula:article-11-applicable" in prop_names, "article-11-applicable in metadata")


def test_ai_bom_not_added_when_false():
    from sbom import generate_sbom
    with tempfile.TemporaryDirectory() as tmpdir:
        (Path(tmpdir) / "app.py").write_text("print('hello')\n")
        sbom = generate_sbom(tmpdir, ai_bom=False)
        meta_props = sbom.get("metadata", {}).get("properties", [])
        prop_names = [p["name"] for p in meta_props]
        assert_true("regula:ai-bom" not in prop_names, "ai-bom flag not in metadata when False")


# ── Runner ──────────────────────────────────────────────────────

if __name__ == "__main__":
    test_funcs = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in test_funcs:
        fn()
    total = helpers.passed + helpers.failed
    print(f"\n{helpers.passed}/{total} passed, {helpers.failed} failed")
    sys.exit(1 if helpers.failed else 0)
