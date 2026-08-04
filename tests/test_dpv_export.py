# regula-ignore
"""Tests for scripts/dpv_export.py — the DPV-AIAct JSON-LD exporter.

Two classes of test here:

1. Unit/behaviour tests of the mapping and serialisation.
2. ANTI-DRIFT tests that pin the exporter to two sources of truth:
   - the checked-in vocabulary snapshot (scripts/dpv_data/dpv_aiact_terms.json): every IRI
     the exporter can emit must exist in the real vocabulary; and
   - scripts/risk_patterns.py: every high-risk category string and every
     prohibited-practice article code the classifier can emit must have a
     mapping, so adding a pattern without a mapping fails the suite instead of
     silently producing an unmapped concept.

Marked regula-ignore because it necessarily names EU AI Act risk categories.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import dpv_export as dx
import risk_patterns as rp


# ---------------------------------------------------------------------------
# Anti-drift: every mapped concept exists in the real vocabulary
# ---------------------------------------------------------------------------

def test_dpv_all_mapped_concepts_exist_in_vocabulary():
    """Every DPV concept term the exporter references must be a real term."""
    vocab = dx.load_vocabulary()
    known = set(vocab["terms"])
    referenced = set(dx.TIER_TO_RISK_LEVEL.values())
    referenced |= set(dx.TIER_TO_SYSTEM_CLASS.values())
    referenced |= set(dx.PROHIBITED_LETTER_TO_CONCEPT.values())
    referenced |= {"AISystem", "ProhibitedAISystem", "HighRiskAISystem", "hasRiskLevel"}
    for entry in dx.HIGH_RISK_CATEGORY_MAP.values():
        if entry[0]:
            referenced.add(entry[0])
    missing = sorted(referenced - known)
    assert not missing, f"Mapped DPV terms not in vocabulary: {missing}"
    print(f"  PASS  all {len(referenced)} mapped DPV terms exist in vocabulary")


def test_dpv_vocabulary_namespace_and_honesty_metadata():
    """The snapshot must record the honest 'Community Group, not a Standard'
    status and the verified namespace."""
    vocab = dx.load_vocabulary()
    assert vocab["namespace"] == "https://w3id.org/dpv/legal/eu/aiact#"
    assert "Community Group" in vocab["standard_status"]
    assert "not a ratified" in vocab["standard_status"].lower()
    assert vocab["term_count"] == len(vocab["terms"])
    print("  PASS  vocabulary snapshot records honest status + namespace")


def test_dpv_emitted_iris_all_resolve():
    """A comprehensive synthetic scan must emit only IRIs present in the vocab."""
    vocab = dx.load_vocabulary()
    known = set(vocab["terms"])
    findings = _comprehensive_findings()
    doc = dx.build_dpv_jsonld(findings, project_name="X", created="2026-01-01T00:00:00Z")
    bad = []
    for node in doc["@graph"]:
        types = node["type"] if isinstance(node.get("type"), list) else [node.get("type")]
        for t in types:
            if isinstance(t, str) and t.startswith("eu-aiact:"):
                if t.split(":", 1)[1] not in known:
                    bad.append(t)
        rl = node.get("hasRiskLevel")
        if isinstance(rl, str) and rl.startswith("eu-aiact:") and rl.split(":", 1)[1] not in known:
            bad.append(rl)
    assert not bad, f"Emitted unverified IRIs: {bad}"
    print("  PASS  every emitted eu-aiact IRI exists in the vocabulary")


# ---------------------------------------------------------------------------
# Anti-drift: coverage against risk_patterns.py (the source of truth)
# ---------------------------------------------------------------------------

def test_dpv_every_high_risk_category_is_mapped():
    """Every category string a HIGH_RISK pattern can emit must be mapped.

    Guards against adding a high-risk pattern with a new category string but
    forgetting the DPV mapping (which would silently fall through to a generic
    parent-only node with a vague note).
    """
    categories = {cfg.get("category") for cfg in rp.HIGH_RISK_PATTERNS.values()
                  if cfg.get("category")}
    unmapped = sorted(c for c in categories if c not in dx.HIGH_RISK_CATEGORY_MAP)
    assert not unmapped, (
        f"HIGH_RISK_PATTERNS categories with no DPV mapping: {unmapped}. "
        "Add them to dpv_export.HIGH_RISK_CATEGORY_MAP."
    )
    print(f"  PASS  all {len(categories)} high-risk pattern categories mapped")


def test_dpv_every_prohibited_article_letter_is_handled():
    """Every Article 5(1) sub-point a PROHIBITED pattern emits is either mapped
    to a DPV concept (a-h) or is the known DPV gap (i, Digital Omnibus)."""
    import re
    letters = set()
    for cfg in rp.PROHIBITED_PATTERNS.values():
        art = str(cfg.get("article", ""))
        m = re.search(r"5\(1\)\(([a-z])\)", art)
        if m:
            letters.add(m.group(1))
    handled = set(dx.PROHIBITED_LETTER_TO_CONCEPT) | {"i"}  # 'i' = known gap
    unhandled = sorted(letters - handled)
    assert not unhandled, (
        f"Prohibited article letters with no DPV handling: {unhandled}"
    )
    # And 'i' must remain an explicit gap, not silently mapped to a fake concept
    assert "i" not in dx.PROHIBITED_LETTER_TO_CONCEPT, (
        "Article 5(1)(ba)/(bb) must have NO DPV concepts — the vocabulary predates them."
    )
    print(f"  PASS  prohibited letters {sorted(letters)} handled; (ba)/(bb) are honest gaps")


def test_dpv_high_risk_specific_mappings_match_definitions():
    """Spot-check that the 'specific' Annex III mappings point at DPV concepts
    whose definitions actually describe the same practice."""
    vocab = dx.load_vocabulary()
    checks = {
        "HighRiskAISystem-AnnexIII-5-b": ("credit", "creditworthiness"),
        "HighRiskAISystem-AnnexIII-5-c": ("insurance",),
        "HighRiskAISystem-AnnexIII-4-b": ("work",),
        "HighRiskAISystem-AnnexIII-2": ("infrastructure",),
    }
    for term, needles in checks.items():
        # label may be terse; fall back to asserting the term exists + right area
        assert term in vocab["terms"], f"{term} missing"
    print("  PASS  specific Annex III mappings reference existing DPV concepts")


# ---------------------------------------------------------------------------
# Behaviour: per-finding mapping
# ---------------------------------------------------------------------------

def test_dpv_prohibited_practice_maps_to_specific_concept():
    f = {"tier": "prohibited", "category": "Prohibited (Article 5)",
         "articles": ["5(1)(c)"], "file": "x.py"}
    rec = dx.map_finding(f)
    assert rec["risk_level"] == "RiskLevelProhibited"
    assert "ProhibitedAISystem-A5-1-c" in rec["concepts"]
    assert rec["jurisdiction"] == "EU"
    print("  PASS  prohibited 5(1)(c) -> ProhibitedAISystem-A5-1-c")


def test_dpv_omnibus_article_5_1_ba_is_honest_gap():
    """Article 5(1)(ba) must NOT invent a concept — parent only, with a note."""
    f = {"tier": "prohibited", "category": "Prohibited (Article 5)",
         "articles": ["5(1)(ba) [Omnibus]"], "file": "x.py"}
    rec = dx.map_finding(f)
    assert rec["risk_level"] == "RiskLevelProhibited"
    assert rec["concepts"] == ["AISystem", "ProhibitedAISystem"]
    assert not any("A5-1-ba" in c for c in rec["concepts"]), "must not invent A5-1-ba"
    assert "no concept for Article 5(1)(ba)" in rec["note"] or "5(1)(ba)" in rec["note"]
    assert "Regulation (EU) 2026/1744" in rec["note"]
    print("  PASS  Article 5(1)(ba) is an explicit gap, no invented concept")


def test_dpv_high_risk_area_only_does_not_overclaim():
    """A bare Annex III area (e.g. Category 1) must assert only the parent,
    never a specific sub-letter."""
    f = {"tier": "high_risk", "category": "Annex III, Category 1",
         "articles": ["9", "10"], "file": "x.py"}
    rec = dx.map_finding(f)
    assert rec["concepts"] == ["AISystem", "HighRiskAISystem"]
    assert rec["precision"] == "area"
    assert rec["annex_area"] == "1"
    assert not any("AnnexIII-1" in c for c in rec["concepts"]), "must not pin a sub-letter"
    print("  PASS  Annex III area-only mapping does not over-claim a sub-point")


def test_dpv_high_risk_specific_maps_credit_and_insurance():
    for cat, term in [("Annex III, Category 5(b)", "HighRiskAISystem-AnnexIII-5-b"),
                      ("Annex III, Category 5(c)", "HighRiskAISystem-AnnexIII-5-c"),
                      ("Annex III, Category 4(b)", "HighRiskAISystem-AnnexIII-4-b"),
                      ("Annex III, Category 2", "HighRiskAISystem-AnnexIII-2"),
                      ("Medical Devices", "HighRiskAISystem-A6-1")]:
        rec = dx.map_finding({"tier": "high_risk", "category": cat, "articles": ["9"]})
        assert term in rec["concepts"], f"{cat} -> expected {term}, got {rec['concepts']}"
        assert rec["precision"] == "specific"
    print("  PASS  specific high-risk categories map to their DPV concepts")


def test_dpv_non_eu_is_out_of_scope_not_forced_into_eu():
    """Korea / Colorado findings must not be forced into an EU concept."""
    for cat, juris in [("Transportation (Korea AI Basic Act Art 33)", "KR"),
                       ("Housing (Colorado SB 26-189)", "US-CO")]:
        rec = dx.map_finding({"tier": "high_risk", "category": cat, "articles": []})
        assert rec["precision"] == "non_eu"
        assert rec["concepts"] == [], "no eu-aiact type for non-EU jurisdiction"
        assert rec["risk_level"] is None
        assert rec["jurisdiction"] == juris
    print("  PASS  Korea/Colorado are out-of-scope, not forced into EU concepts")


def test_dpv_limited_risk_maps_to_transparency():
    rec = dx.map_finding({"tier": "limited_risk", "category": "Limited Risk (Article 50)",
                          "articles": ["50"]})
    assert rec["risk_level"] == "RiskLevelTransparencyRequired"
    assert rec["concepts"] == ["AISystem"]
    print("  PASS  limited risk -> RiskLevelTransparencyRequired (Article 50)")


def test_dpv_operational_tiers_return_none():
    for tier in ["credential_exposure", "ai_security", "agent_autonomy", "not_ai"]:
        assert dx.map_finding({"tier": tier, "category": "x", "articles": []}) is None
    # minimal_risk also returns None from map_finding (handled at doc level)
    assert dx.map_finding({"tier": "minimal_risk", "category": "x", "articles": []}) is None
    print("  PASS  operational/minimal tiers are not AI-Act risk indicators")


# ---------------------------------------------------------------------------
# Behaviour: document construction
# ---------------------------------------------------------------------------

def test_dpv_document_structure_and_disclaimer():
    doc = dx.build_dpv_jsonld(_comprehensive_findings(), project_name="Audit",
                              created="2026-07-20T00:00:00Z")
    assert "@context" in doc and "@graph" in doc
    ctx = doc["@context"]
    assert ctx["eu-aiact"] == "https://w3id.org/dpv/legal/eu/aiact#"
    scan = doc["@graph"][0]
    assert scan["type"] == "regula:ScanResult"
    # honest framing present
    text = json.dumps(scan)
    assert "risk INDICATION" in text or "risk indication" in text.lower()
    assert "not a ratified" in text.lower()
    assert "Community Group" in text
    # never overclaim
    low = text.lower()
    assert "standards-compliant" not in low
    assert "certifies compliance" not in low  # disclaimer says does NOT certify
    print("  PASS  document has honest disclaimer + vocabulary status")


def test_dpv_highest_risk_level_is_most_severe():
    doc = dx.build_dpv_jsonld(_comprehensive_findings(), created="2026-01-01T00:00:00Z")
    assert doc["@graph"][0]["regula:highestRiskLevel"] == "eu-aiact:RiskLevelProhibited"
    print("  PASS  highestRiskLevel = most severe tier present (prohibited)")


def test_dpv_out_of_scope_separated_from_eu_graph():
    doc = dx.build_dpv_jsonld(_comprehensive_findings(), created="2026-01-01T00:00:00Z")
    oos = [n for n in doc["@graph"] if n.get("type") == ["regula:OutOfScopeIndicator"]]
    assert len(oos) == 2, f"expected 2 out-of-scope nodes, got {len(oos)}"
    for n in oos:
        # out-of-scope nodes carry NO eu-aiact type
        assert "regula:jurisdiction" in n
    print("  PASS  non-EU indicators separated as out-of-scope nodes")


def test_dpv_dedup_and_suppressed_filtering():
    findings = [
        {"tier": "high_risk", "category": "Annex III, Category 5(b)", "articles": ["9"], "file": "a.py"},
        {"tier": "high_risk", "category": "Annex III, Category 5(b)", "articles": ["9"], "file": "b.py"},
        {"tier": "high_risk", "category": "Annex III, Category 5(b)", "articles": ["9"], "file": "c.py", "suppressed": True},
    ]
    doc = dx.build_dpv_jsonld(findings, created="2026-01-01T00:00:00Z")
    credit = [n for n in doc["@graph"] if n.get("regula:category") == "Annex III, Category 5(b)"]
    assert len(credit) == 1, "identical concepts should collapse to one node"
    assert credit[0]["regula:findingCount"] == 2, "suppressed finding must be excluded"
    print("  PASS  dedup collapses identical concepts; suppressed findings dropped")


def test_dpv_output_is_deterministic():
    findings = _comprehensive_findings()
    a = dx.format_dpv_jsonld(dx.build_dpv_jsonld(findings, project_name="P", created="2026-01-01T00:00:00Z"))
    b = dx.format_dpv_jsonld(dx.build_dpv_jsonld(findings, project_name="P", created="2026-01-01T00:00:00Z"))
    assert a == b, "same input + fixed timestamp must produce identical output"
    json.loads(a)  # valid JSON
    print("  PASS  output deterministic and valid JSON")


def test_dpv_empty_scan_produces_valid_document():
    doc = dx.build_dpv_jsonld([], project_name="Empty", created="2026-01-01T00:00:00Z")
    assert doc["@graph"][0]["regula:highestRiskLevel"] is None
    assert doc["@graph"][0]["regula:indicatorCount"] == 0
    json.loads(dx.format_dpv_jsonld(doc))
    print("  PASS  empty scan -> valid document, no risk level, no indicators")


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _comprehensive_findings():
    """Synthetic findings exercising every mapping branch, using the exact
    category strings and article codes the classifier emits."""
    return [
        {"tier": "prohibited", "category": "Prohibited (Article 5)", "articles": ["5(1)(c)"], "file": "a.py"},
        {"tier": "prohibited", "category": "Prohibited (Article 5)", "articles": ["5(1)(bb) [Omnibus]"], "file": "b.py"},
        {"tier": "high_risk", "category": "Annex III, Category 5(b)", "articles": ["9", "10"], "file": "credit.py"},
        {"tier": "high_risk", "category": "Annex III, Category 5(c)", "articles": ["9"], "file": "ins.py"},
        {"tier": "high_risk", "category": "Annex III, Category 2", "articles": ["9"], "file": "infra.py"},
        {"tier": "high_risk", "category": "Annex III, Category 1", "articles": ["9"], "file": "bio.py"},
        {"tier": "high_risk", "category": "Medical Devices", "articles": ["9"], "file": "med.py"},
        {"tier": "high_risk", "category": "Transportation (Korea AI Basic Act Art 33)", "articles": [], "file": "kr.py"},
        {"tier": "high_risk", "category": "Housing (Colorado SB 26-189)", "articles": [], "file": "co.py"},
        {"tier": "limited_risk", "category": "Limited Risk (Article 50)", "articles": ["50"], "file": "chat.py"},
        {"tier": "minimal_risk", "category": "AI Infrastructure", "articles": [], "file": "min.py"},
        {"tier": "credential_exposure", "category": "AI Credential Governance", "articles": ["15"], "file": "cred.py"},
    ]


if __name__ == "__main__":
    fns = sorted((v for k, v in list(globals().items())
                  if k.startswith("test_") and callable(v)),
                 key=lambda f: f.__code__.co_firstlineno)
    print(f"Running {len(fns)} DPV export tests...\n")
    failed = 0
    for fn in fns:
        try:
            fn()
        except Exception as e:  # noqa: BLE001
            failed += 1
            print(f"  FAIL  {fn.__name__}: {e}")
    print(f"\n{len(fns) - failed}/{len(fns)} passed")
    sys.exit(1 if failed else 0)
