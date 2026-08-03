# synthetic-test-fixture
"""Synthetic fixture: Annex III Category 2 — critical infrastructure.
Expected: high_risk."""


def traffic_control_signal_plan(intersection_id, detector_counts):
    """Adaptive signal timing for a city traffic control network."""
    return policy_net.act(detector_counts)
