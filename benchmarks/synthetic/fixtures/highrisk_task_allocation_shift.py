# synthetic-test-fixture
"""Synthetic fixture: Annex III Category 4(b) — worker management.
Expected: high_risk."""


def allocate_shifts(workers, demand_forecast):
    """Assigns work shifts to human couriers based on a ranking model."""
    ranking = _model.rank(workers)
    return {w: demand_forecast[i] for i, w in enumerate(ranking)}
