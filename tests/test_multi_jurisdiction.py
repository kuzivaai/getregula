# regula-ignore
"""Tests for multi-jurisdiction regulation mapping.

Covers: regulation_map.py, detect_domains(), jurisdiction YAML loading,
domain-to-obligation mapping, and YAML fallback parser compatibility.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from classify_risk import classify, detect_domains
from regulation_map import (
    load_jurisdiction, list_jurisdictions,
    map_domains_to_obligations, get_jurisdiction_summary,
    _JURISDICTION_CACHE,
)
from risk_patterns import HIGH_RISK_PATTERNS, PROHIBITED_PATTERNS


# ---------------------------------------------------------------------------
# Phase 1: domain fields on all patterns
# ---------------------------------------------------------------------------

def test_all_high_risk_patterns_have_domain():
    for key, cfg in HIGH_RISK_PATTERNS.items():
        assert "domain" in cfg, f"HIGH_RISK_PATTERNS['{key}'] missing 'domain' field"

def test_all_prohibited_patterns_have_domain():
    for key, cfg in PROHIBITED_PATTERNS.items():
        assert "domain" in cfg, f"PROHIBITED_PATTERNS['{key}'] missing 'domain' field"

def test_domain_values_are_strings():
    for key, cfg in HIGH_RISK_PATTERNS.items():
        assert isinstance(cfg["domain"], str), f"HIGH_RISK_PATTERNS['{key}']['domain'] is not a string"
    for key, cfg in PROHIBITED_PATTERNS.items():
        assert isinstance(cfg["domain"], str), f"PROHIBITED_PATTERNS['{key}']['domain'] is not a string"


# ---------------------------------------------------------------------------
# Phase 2: jurisdiction YAML loading
# ---------------------------------------------------------------------------

def test_list_jurisdictions_returns_three():
    jurs = list_jurisdictions()
    assert len(jurs) == 3, f"Expected 3 jurisdictions, got {len(jurs)}: {jurs}"
    assert "eu_ai_act" in jurs
    assert "south_korea" in jurs
    assert "colorado" in jurs

def test_load_jurisdiction_eu():
    _JURISDICTION_CACHE.clear()
    config = load_jurisdiction("eu_ai_act")
    assert config["jurisdiction_id"] == "eu_ai_act"
    assert config["name"] == "EU AI Act"
    dm = config.get("domain_mappings", {})
    assert len(dm) == 12, f"EU should have 12 domains, got {len(dm)}"

def test_load_jurisdiction_korea():
    _JURISDICTION_CACHE.clear()
    config = load_jurisdiction("south_korea")
    assert config["jurisdiction_id"] == "south_korea"
    dm = config.get("domain_mappings", {})
    assert "transportation" in dm, "Korea should have transportation domain"
    assert len(dm) == 9, f"Korea should have 9 domains, got {len(dm)}"

def test_load_jurisdiction_colorado():
    _JURISDICTION_CACHE.clear()
    config = load_jurisdiction("colorado")
    assert config["jurisdiction_id"] == "colorado"
    dm = config.get("domain_mappings", {})
    assert "housing" in dm, "Colorado should have housing domain"
    assert len(dm) == 7, f"Colorado should have 7 domains, got {len(dm)}"

def test_load_invalid_jurisdiction_raises():
    try:
        load_jurisdiction("narnia")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass

def test_jurisdiction_summary():
    _JURISDICTION_CACHE.clear()
    info = get_jurisdiction_summary("eu_ai_act")
    assert info["name"] == "EU AI Act"
    assert "2024/1689" in info["law"]
    assert isinstance(info["risk_tiers"], list)
    assert len(info["risk_tiers"]) == 5


# ---------------------------------------------------------------------------
# Phase 2: obligation mapping
# ---------------------------------------------------------------------------

def test_map_employment_across_jurisdictions():
    _JURISDICTION_CACHE.clear()
    for jid in ["eu_ai_act", "south_korea", "colorado"]:
        results = map_domains_to_obligations(["employment"], jid)
        assert len(results) == 1, f"employment should be covered by {jid}"
        assert results[0]["covered"] is True
        assert len(results[0]["obligations"]) > 0

def test_map_migration_eu_only():
    _JURISDICTION_CACHE.clear()
    eu = map_domains_to_obligations(["migration"], "eu_ai_act")
    kr = map_domains_to_obligations(["migration"], "south_korea")
    co = map_domains_to_obligations(["migration"], "colorado")
    assert len(eu) == 1, "migration should be covered by EU"
    assert len(kr) == 0, "migration should NOT be covered by Korea"
    assert len(co) == 0, "migration should NOT be covered by Colorado"

def test_map_housing_colorado_only():
    _JURISDICTION_CACHE.clear()
    eu = map_domains_to_obligations(["housing"], "eu_ai_act")
    kr = map_domains_to_obligations(["housing"], "south_korea")
    co = map_domains_to_obligations(["housing"], "colorado")
    assert len(eu) == 0, "housing should NOT be covered by EU"
    assert len(kr) == 0, "housing should NOT be covered by Korea"
    assert len(co) == 1, "housing should be covered by Colorado"

def test_map_transportation_korea():
    _JURISDICTION_CACHE.clear()
    kr = map_domains_to_obligations(["transportation"], "south_korea")
    assert len(kr) == 1, "transportation should be covered by Korea"
    assert kr[0]["risk_level"] == "high_impact"

def test_map_multiple_domains():
    _JURISDICTION_CACHE.clear()
    results = map_domains_to_obligations(["employment", "credit", "biometrics"], "eu_ai_act")
    assert len(results) == 3, f"All 3 domains should be covered by EU, got {len(results)}"

def test_map_uncovered_domain_returns_empty():
    _JURISDICTION_CACHE.clear()
    results = map_domains_to_obligations(["manipulation"], "colorado")
    assert len(results) == 0

def test_obligations_have_article_and_name():
    _JURISDICTION_CACHE.clear()
    results = map_domains_to_obligations(["employment"], "eu_ai_act")
    for obl in results[0]["obligations"]:
        assert "article" in obl, f"obligation missing 'article': {obl}"
        assert "name" in obl, f"obligation missing 'name': {obl}"


# ---------------------------------------------------------------------------
# Phase 3: detect_domains in classify_risk.py
# ---------------------------------------------------------------------------

def test_detect_domains_employment():
    text = "import sklearn\ndef screen_candidates(resumes):\n    model = sklearn.ensemble.RandomForestClassifier()\n"
    domains = detect_domains(text)
    assert "employment" in domains, f"Expected 'employment' in {domains}"

def test_detect_domains_credit():
    text = "import tensorflow\ndef credit_score_model(features):\n    pass\n"
    domains = detect_domains(text)
    assert "credit" in domains or "essential_services" in domains, f"Expected credit domain in {domains}"

def test_detect_domains_housing():
    text = "import sklearn\ndef screen_tenants(apps):\n    pass\n"
    domains = detect_domains(text)
    assert "housing" in domains, f"Expected 'housing' in {domains}"

def test_detect_domains_empty_for_no_ai():
    text = "print('hello world')\n"
    domains = detect_domains(text)
    assert len(domains) == 0, f"Expected empty domains, got {domains}"

def test_classify_includes_detected_domains():
    text = "import sklearn\ndef cv_screen(resumes):\n    return sklearn.tree.DecisionTreeClassifier().predict(resumes)\n"
    result = classify(text)
    assert hasattr(result, "detected_domains"), "Classification missing detected_domains field"
    assert isinstance(result.detected_domains, list)

def test_classify_serialises_detected_domains():
    text = "import sklearn\ndef hiring_decision(x):\n    return sklearn.svm.SVC().predict(x)\n"
    result = classify(text)
    d = result.to_dict()
    assert "detected_domains" in d, "to_dict() missing detected_domains"


# ---------------------------------------------------------------------------
# Phase 2: YAML fallback parser compatibility
# ---------------------------------------------------------------------------

def test_yaml_fallback_parses_jurisdiction_files():
    from policy_config import _parse_yaml_fallback
    for fname in ["eu_ai_act", "south_korea", "colorado"]:
        path = Path(__file__).parent.parent / "references" / "jurisdictions" / f"{fname}.yaml"
        text = path.read_text(encoding="utf-8")
        result = _parse_yaml_fallback(text)
        assert isinstance(result, dict), f"Fallback failed for {fname}"
        dm = result.get("domain_mappings", {})
        assert isinstance(dm, dict), f"domain_mappings not a dict for {fname}"
        assert len(dm) > 0, f"domain_mappings empty for {fname}"
        # Check obligations are lists of dicts
        for domain, mapping in dm.items():
            obs = mapping.get("obligations", [])
            assert isinstance(obs, list), f"{fname}/{domain}/obligations not a list"
            if obs:
                assert isinstance(obs[0], dict), f"{fname}/{domain}/obligations[0] not a dict"

def test_yaml_fallback_parses_risk_tiers_as_list():
    from policy_config import _parse_yaml_fallback
    for fname in ["eu_ai_act", "south_korea", "colorado"]:
        path = Path(__file__).parent.parent / "references" / "jurisdictions" / f"{fname}.yaml"
        text = path.read_text(encoding="utf-8")
        result = _parse_yaml_fallback(text)
        tiers = result.get("risk_tiers", [])
        assert isinstance(tiers, list), f"risk_tiers not a list for {fname}: {type(tiers)}"
        assert len(tiers) >= 2, f"risk_tiers too short for {fname}: {tiers}"

def test_yaml_fallback_obligation_articles_are_strings():
    """Flow mapping article values must stay as strings, not coerced to int."""
    from policy_config import _parse_yaml_fallback
    for fname in ["eu_ai_act", "south_korea", "colorado"]:
        path = Path(__file__).parent.parent / "references" / "jurisdictions" / f"{fname}.yaml"
        text = path.read_text(encoding="utf-8")
        result = _parse_yaml_fallback(text)
        for domain, mapping in result.get("domain_mappings", {}).items():
            for obl in mapping.get("obligations", []):
                art = obl.get("article")
                assert isinstance(art, str), (
                    f"{fname}/{domain}: obligation article {art!r} is {type(art).__name__}, expected str"
                )

def test_yaml_fallback_korea_flops_is_float():
    """Korea high_performance_threshold.flops must parse as float."""
    from policy_config import _parse_yaml_fallback
    path = Path(__file__).parent.parent / "references" / "jurisdictions" / "south_korea.yaml"
    result = _parse_yaml_fallback(path.read_text(encoding="utf-8"))
    flops = result.get("high_performance_threshold", {}).get("flops")
    assert isinstance(flops, float), f"flops is {type(flops).__name__}={flops!r}, expected float"
    assert flops == 1e26, f"flops is {flops}, expected 1e26"


# ---------------------------------------------------------------------------
# Detect domains with stripped text (false positive filtering)
# ---------------------------------------------------------------------------

def test_detect_domains_filters_comments():
    """Domain keywords in comments should not produce false positives."""
    from classify_risk import strip_comments
    text = '# This comment mentions hiring_decision and cv_screen\nprint("hello")\n'
    stripped = strip_comments(text, "python")
    domains = detect_domains(text, stripped_text=stripped)
    assert "employment" not in domains, f"Comment-only employment should be filtered, got {domains}"

def test_detect_domains_empty_string():
    domains = detect_domains("")
    assert domains == [], f"Empty string should produce empty domains, got {domains}"

def test_detect_domains_stripped_text_used():
    """When stripped_text is provided, it should be used instead of raw text."""
    raw = '# hiring_decision in a comment\nimport sklearn\ndef predict(x): pass\n'
    stripped = 'import sklearn\ndef predict(x): pass\n'
    domains = detect_domains(raw, stripped_text=stripped)
    assert "employment" not in domains, f"Stripped text should filter comment domain, got {domains}"


# ---------------------------------------------------------------------------
# Path traversal containment
# ---------------------------------------------------------------------------

def test_load_jurisdiction_blocks_path_traversal():
    _JURISDICTION_CACHE.clear()
    traversal_ids = [
        "../etc/passwd",
        "eu_ai_act/../../etc/passwd",
        "..%2Fetc%2Fpasswd",
    ]
    for tid in traversal_ids:
        try:
            load_jurisdiction(tid)
            assert False, f"Should have raised ValueError for {tid!r}"
        except ValueError:
            pass

def test_load_jurisdiction_blocks_absolute_path():
    _JURISDICTION_CACHE.clear()
    try:
        load_jurisdiction("/etc/passwd")
        assert False, "Should have raised ValueError for absolute path"
    except ValueError:
        pass


# ---------------------------------------------------------------------------
# Korea Article 29 removal (research-eval fix)
# ---------------------------------------------------------------------------

def test_korea_no_article_29_obligations():
    """Article 29 was incorrectly mapped as 'right to explanation'. Verify removed."""
    _JURISDICTION_CACHE.clear()
    config = load_jurisdiction("south_korea")
    for domain, mapping in config.get("domain_mappings", {}).items():
        for obl in mapping.get("obligations", []):
            art = str(obl.get("article", ""))
            assert art != "29", (
                f"Korea/{domain} still has Article 29 obligation: {obl}"
            )

def test_eu_insurance_category_is_5c():
    """Insurance is Annex III Category 5(c), not 5(d)."""
    _JURISDICTION_CACHE.clear()
    config = load_jurisdiction("eu_ai_act")
    insurance = config["domain_mappings"].get("insurance", {})
    assert "5(c)" in insurance.get("category", ""), (
        f"EU insurance category should be 5(c), got: {insurance.get('category')}"
    )


# ---------------------------------------------------------------------------
# CLI jurisdiction aliases (web assess uses kr/co; CLI canonical is korea/colorado)
# ---------------------------------------------------------------------------

def test_jurisdiction_aliases_resolve_to_canonical():
    from cli import JURISDICTION_ALIASES, JURISDICTION_MAP, _resolve_jurisdictions
    # Every alias must point at a canonical short name that actually exists
    for alias, canonical in JURISDICTION_ALIASES.items():
        assert canonical in JURISDICTION_MAP, (
            f"Alias '{alias}' points at unknown jurisdiction '{canonical}'"
        )
    resolved = _resolve_jurisdictions("kr,co")
    assert ("korea", JURISDICTION_MAP["korea"]) in resolved
    assert ("colorado", JURISDICTION_MAP["colorado"]) in resolved

def test_jurisdiction_alias_normaliser():
    from cli import _normalise_jurisdiction
    assert _normalise_jurisdiction("kr") == "korea"
    assert _normalise_jurisdiction("CO") == "colorado"
    assert _normalise_jurisdiction(" korea ") == "korea"
    assert _normalise_jurisdiction("eu") == "eu"
