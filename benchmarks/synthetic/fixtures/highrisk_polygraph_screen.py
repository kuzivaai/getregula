# synthetic-test-fixture
"""Synthetic fixture: Annex III Category 6 — law enforcement.
Expected: high_risk."""


def polygraph_deception_score(physiological_signals):
    """Estimates deception likelihood during suspect interview."""
    return _deception_net.forward(physiological_signals)
