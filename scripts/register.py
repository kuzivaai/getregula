"""Annex VIII registration packet generator.

Builds Annex VIII Section A/B/C registration packets for an AI project,
auto-filling fields from existing Regula scan artifacts and emitting an
explicit gap list for fields the scanner cannot derive.

No network calls. No interactive flow. See
docs/superpowers/specs/2026-04-07-regula-register-annex-viii-design.md
for the full design and primary-source verification.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

_SCHEMA_PATH = Path(__file__).resolve().parents[1] / "references" / "annex_viii_sections.json"


def load_schema() -> dict:
    """Load the Annex VIII section schema from the reference JSON file."""
    with open(_SCHEMA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)
