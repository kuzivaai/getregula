# synthetic-test-fixture
"""Synthetic fixture: Annex III Category 8 — democratic processes.
Expected: high_risk."""


def voter_targeting_persuasion(electoral_roll, message_variants):
    """Selects which voters receive which campaign message."""
    return {v: _uplift_model.best(v, message_variants) for v in electoral_roll}
