# synthetic-test-fixture
"""Synthetic fixture: Annex III Category 3 — education.
Expected: high_risk."""


def admission_decision_rank(applications):
    """Ranks university applicants; the top N receive offers automatically."""
    scored = [(a, _model.score(a)) for a in applications]
    return sorted(scored, key=lambda p: -p[1])


def issue_offers(ranked, seats):
    return [a for a, _ in ranked[:seats]]
