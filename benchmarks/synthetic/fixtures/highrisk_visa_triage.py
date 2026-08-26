# synthetic-test-fixture
"""Synthetic fixture: Annex III Category 7 — migration and border control.
Expected: high_risk."""


def asylum_application_triage(case_file):
    """Prioritises and pre-assesses asylum applications."""
    return {"track": _model.route(case_file), "risk": _model.risk(case_file)}
