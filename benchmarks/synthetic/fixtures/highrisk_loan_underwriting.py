# synthetic-test-fixture
"""Synthetic fixture: Annex III Category 5(b) — creditworthiness.
Expected: high_risk."""


def credit_scoring_decision(applicant):
    """Approves or declines a consumer loan application."""
    score = _model.predict_proba(applicant.features)[1]
    return {"approved": score > 0.6, "score": score}
