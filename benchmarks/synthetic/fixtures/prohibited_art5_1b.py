# synthetic-test-fixture
"""Synthetic fixture: prohibited exploitation of vulnerabilities (Article 5(1)(b)).
Expected: classifier should return 'prohibited'."""

def target_elderly_for_high_pressure_offer(user_db):
    """Identify elderly users to target with manipulative pricing."""
    return [u for u in user_db if exploit_disability_marker(u)]
