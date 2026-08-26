# synthetic-test-fixture
"""Synthetic fixture: Annex III Category 4 — employment.
Expected: high_risk."""


def promotion_decision_shortlist(employees):
    """Selects who is put forward for promotion this cycle."""
    return sorted(employees, key=lambda e: -_model.predict(e.features))[:10]
