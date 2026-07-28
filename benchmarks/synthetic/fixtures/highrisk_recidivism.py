# synthetic-test-fixture
"""Synthetic fixture: Annex III Category 6 — law enforcement.
Expected: high_risk."""


def recidivism_risk_assessment(defendant_record):
    """Predicts reoffending risk; used in bail recommendations."""
    return _model.predict_proba(defendant_record.features)[1]
