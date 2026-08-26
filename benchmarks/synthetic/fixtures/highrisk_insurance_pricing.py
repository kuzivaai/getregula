# synthetic-test-fixture
"""Synthetic fixture: Annex III Category 5(c) — life and health insurance.
Expected: high_risk."""


def insurance_scoring_premium(policyholder):
    """Sets the health insurance premium for an individual."""
    return base_rate * _risk_model.predict(policyholder.health_features)
