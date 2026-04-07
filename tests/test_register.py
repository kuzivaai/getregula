"""Tests for regula register (Annex VIII packet generator)."""
import sys
from pathlib import Path

# Reuse the same sys.path setup as test_classification.py
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


def test_register_schema_loads_with_correct_field_counts():
    """The Annex VIII schema file loads and reports A=13, B=9, C=5 fields."""
    from register import load_schema

    schema = load_schema()
    assert "metadata" in schema, f"missing metadata: {list(schema.keys())}"
    assert "sections" in schema, f"missing sections: {list(schema.keys())}"

    sections = schema["sections"]
    assert set(sections.keys()) == {"A", "B", "C"}, f"sections: {list(sections.keys())}"

    assert len(sections["A"]["fields"]) == 13, \
        f"Section A must have 13 fields, got {len(sections['A']['fields'])}"
    assert len(sections["B"]["fields"]) == 9, \
        f"Section B must have 9 fields, got {len(sections['B']['fields'])}"
    assert len(sections["C"]["fields"]) == 5, \
        f"Section C must have 5 fields, got {len(sections['C']['fields'])}"

    assert sections["A"]["article"] == "49(1)"
    assert sections["B"]["article"] == "49(2)"
    assert sections["C"]["article"] == "49(3)"

    md = schema["metadata"]
    assert md["regulation"] == "Regulation (EU) 2024/1689"
    assert md["verified_date"] == "2026-04-07"
    assert "verification_method" in md
    assert "sources" in md and len(md["sources"]) >= 3
    print("✓ register: schema loads with A=13, B=9, C=5")


def test_register_schema_excluded_under_49_4_flags_are_correct():
    """Section A points 6, 8, 9 are excluded under Art 49(4); all other A points and all B/C points are not."""
    from register import load_schema

    schema = load_schema()

    # Section A: every field must carry the flag, exactly points 6/8/9 are True
    a_fields = schema["sections"]["A"]["fields"]
    excluded_a_points = sorted(f["point"] for f in a_fields if f["excluded_under_49_4"])
    assert excluded_a_points == [6, 8, 9], \
        f"Section A excluded points must be [6, 8, 9], got {excluded_a_points}"
    for f in a_fields:
        assert "excluded_under_49_4" in f, \
            f"Section A point {f['point']} missing excluded_under_49_4"
        assert isinstance(f["excluded_under_49_4"], bool)

    # Sections B and C: every field must carry the flag, all values must be False
    for sec in ("B", "C"):
        for f in schema["sections"][sec]["fields"]:
            assert "excluded_under_49_4" in f, \
                f"Section {sec} point {f['point']} missing excluded_under_49_4"
            assert f["excluded_under_49_4"] is False, \
                f"Section {sec} point {f['point']} must be False, got {f['excluded_under_49_4']}"

    print("✓ register: excluded_under_49_4 flags correct (A: 6/8/9 only, B/C: all False)")


def test_register_detects_section_a_for_provider_annex3_point4_employment():
    """Provider building an Annex III point 4 (employment) system → Section A, eu_database_public, Art 49(1)."""
    from register import detect_section_and_target
    decision = detect_section_and_target(role="provider", annex_iii_point=4, deployer_type="none", art_6_3_exempted=False)
    assert decision["section"] == "A", f"section: {decision}"
    assert decision["target"] == "eu_database_public", f"target: {decision}"
    assert decision["article"] == "49(1)", f"article: {decision}"
    assert decision["fields_excluded"] == [], f"exclusions: {decision}"
    print("✓ register: provider point 4 → A / public")


def test_register_detects_critical_infra_routes_to_national():
    """Provider of Annex III point 2 (critical infrastructure) → national_authority per Art. 49(5)."""
    from register import detect_section_and_target
    decision = detect_section_and_target(role="provider", annex_iii_point=2, deployer_type="none", art_6_3_exempted=False)
    assert decision["section"] == "A"
    assert decision["target"] == "national_authority", f"target: {decision}"
    assert decision["article"] == "49(5)"
    print("✓ register: critical infra → national")


def test_register_detects_biometrics_routes_to_non_public():
    """Provider of Annex III point 1 (biometrics) → eu_database_non_public, fields 6/8/9 excluded (Art 49(4))."""
    from register import detect_section_and_target
    decision = detect_section_and_target(role="provider", annex_iii_point=1, deployer_type="none", art_6_3_exempted=False)
    assert decision["section"] == "A"
    assert decision["target"] == "eu_database_non_public", f"target: {decision}"
    assert decision["article"] == "49(4)"
    assert sorted(decision["fields_excluded"]) == [6, 8, 9], f"exclusions: {decision}"
    print("✓ register: biometrics → non_public, excludes 6,8,9")


def test_register_detects_law_enforcement_routes_to_non_public():
    """Provider of Annex III point 6 (law enforcement) → eu_database_non_public + same exclusions."""
    from register import detect_section_and_target
    decision = detect_section_and_target(role="provider", annex_iii_point=6, deployer_type="none", art_6_3_exempted=False)
    assert decision["target"] == "eu_database_non_public"
    assert decision["article"] == "49(4)"
    assert sorted(decision["fields_excluded"]) == [6, 8, 9]
    print("✓ register: law enforcement → non_public")


def test_register_detects_migration_routes_to_non_public():
    """Provider of Annex III point 7 (migration/asylum/border) → eu_database_non_public + same exclusions."""
    from register import detect_section_and_target
    decision = detect_section_and_target(role="provider", annex_iii_point=7, deployer_type="none", art_6_3_exempted=False)
    assert decision["target"] == "eu_database_non_public"
    assert decision["article"] == "49(4)"
    assert sorted(decision["fields_excluded"]) == [6, 8, 9]
    print("✓ register: migration → non_public")
