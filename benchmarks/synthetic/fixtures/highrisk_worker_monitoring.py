# synthetic-test-fixture
"""Synthetic fixture: Annex III Category 4(b) — worker management.
Expected: high_risk."""


def employee_monitoring_productivity(keystroke_log, screenshots):
    """Scores warehouse staff productivity; low scores trigger review."""
    return _score(keystroke_log, screenshots)


def flag_for_termination(scores, threshold=0.3):
    return [e for e, s in scores.items() if s < threshold]
