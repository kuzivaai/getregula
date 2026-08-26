# synthetic-test-fixture
"""Synthetic fixture: Annex III Category 5(a) — essential public services.
Expected: high_risk."""


def public_benefit_eligibility(claimant_record):
    """Decides entitlement to a social welfare payment."""
    return {"eligible": _model.decide(claimant_record) == 1}
