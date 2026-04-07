# synthetic-test-fixture
"""Synthetic fixture: Annex III Category 7 — migration / asylum / border control.
Expected: classifier should return 'high_risk'."""

def visa_application_score(application):
    """Score a visa application for approval recommendation."""
    return _model_predict(extract_visa_features(application))


def asylum_application_decision(case):
    """Asylum application risk classifier."""
    return immigration_decision_model(case)


def border_control_check(traveler_id):
    """Border control screening with biometric match."""
    return run_border_control_screen(traveler_id)
