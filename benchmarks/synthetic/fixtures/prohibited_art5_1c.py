# synthetic-test-fixture
"""Synthetic fixture: prohibited social scoring (Article 5(1)(c)).
Expected: classifier should return 'prohibited'."""

def compute_citizen_score(citizen_id, behaviour_log):
    """Aggregate social credit score from behaviour observations."""
    base = lookup_social_credit_rating(citizen_id)
    return base + score_behaviour_log(behaviour_log)


def update_social_score(citizen_id, delta):
    """Apply social scoring delta to citizen record."""
    persist_social_credit_system(citizen_id, delta)
