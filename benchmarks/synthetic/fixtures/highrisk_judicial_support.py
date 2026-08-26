# synthetic-test-fixture
"""Synthetic fixture: Annex III Category 8 — administration of justice.
Expected: high_risk."""


def judicial_decision_draft(case_bundle):
    """Drafts sentencing recommendations for a judge."""
    return _llm.generate(prompt=_render(case_bundle))
