# synthetic-test-fixture
"""Synthetic fixture: Annex III Category 7 — migration and border control.
Expected: high_risk."""


def border_control_traveller_risk(passenger_manifest):
    """Flags arriving travellers for secondary inspection."""
    return [p for p in passenger_manifest if _risk(p) > 0.7]
