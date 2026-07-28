# synthetic-test-fixture
"""Synthetic fixture: housing (Colorado SB 26-189) — tenant screening.
Expected: high_risk."""


def tenant_screening_decision(rental_application):
    """Approves or rejects a prospective tenant."""
    return _model.predict(rental_application) > 0.5
