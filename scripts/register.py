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


# Annex III point → (target, article, fields_excluded) for providers.
# Point 1 = biometrics, 2 = critical infra, 3 = education, 4 = employment,
# 5 = essential services, 6 = law enforcement, 7 = migration/asylum/border, 8 = justice/democracy.
# See spec §4.2 and primary sources at references/annex_viii_sections.json.

_PROVIDER_NON_PUBLIC_POINTS = {1, 6, 7}      # Art 49(4) — non-public EU section
_PROVIDER_NATIONAL_POINTS = {2}              # Art 49(5) — national-level registration
_NON_PUBLIC_EXCLUDED_FIELDS = [6, 8, 9]      # Section A points excluded under Art 49(4)


def detect_section_and_target(role: str, annex_iii_point: int | None,
                              deployer_type: str, art_6_3_exempted: bool) -> dict:
    """Determine which Annex VIII section and submission target apply.

    Args:
        role: "provider", "deployer", or "unclear" (from explain.detect_provider_deployer)
        annex_iii_point: 1-8 if a high-risk Annex III area was detected, else None
        deployer_type: "public_authority" or "none"
        art_6_3_exempted: True if the provider has self-assessed as non-high-risk under Art 6(3)

    Returns:
        {"section", "target", "article", "fields_excluded", "kind"}

        "kind" is one of: "registration_required", "not_applicable",
        "no_registration_required".
    """
    # Provider self-exemption (Art 6(3)) — Section B regardless of Annex III point
    if role == "provider" and art_6_3_exempted:
        return {
            "section": "B",
            "target": "eu_database_public",
            "article": "49(2)",
            "fields_excluded": [],
            "kind": "registration_required",
        }

    if role == "provider" and annex_iii_point is not None:
        if annex_iii_point in _PROVIDER_NATIONAL_POINTS:
            return {
                "section": "A",
                "target": "national_authority",
                "article": "49(5)",
                "fields_excluded": [],
                "kind": "registration_required",
            }
        if annex_iii_point in _PROVIDER_NON_PUBLIC_POINTS:
            return {
                "section": "A",
                "target": "eu_database_non_public",
                "article": "49(4)",
                "fields_excluded": list(_NON_PUBLIC_EXCLUDED_FIELDS),
                "kind": "registration_required",
            }
        return {
            "section": "A",
            "target": "eu_database_public",
            "article": "49(1)",
            "fields_excluded": [],
            "kind": "registration_required",
        }

    # Deployer / fallback branches handled in Task 3 — placeholder for now
    return {
        "section": None,
        "target": None,
        "article": None,
        "fields_excluded": [],
        "kind": "not_applicable",
    }
