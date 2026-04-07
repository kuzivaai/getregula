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
