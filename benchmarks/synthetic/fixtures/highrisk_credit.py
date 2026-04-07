# synthetic-test-fixture
"""Synthetic fixture: Annex III Category 5 — access to essential services.
Expected: classifier should return 'high_risk'."""

from sklearn.linear_model import LogisticRegression

def credit_score_decision(applicant):
    """Compute creditworthiness score for loan approval."""
    model = LogisticRegression()
    features = extract_credit_features(applicant)
    score = model.predict_proba([features])[0][1]
    return loan_approval_from_score(score)


def loan_decision_pipeline(applicant_id):
    """Make a lending decision."""
    score = credit_score_decision(load_applicant(applicant_id))
    return {"approved": score > 0.6, "credit_score": score}
