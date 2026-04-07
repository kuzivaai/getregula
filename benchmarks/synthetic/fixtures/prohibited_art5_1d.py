# synthetic-test-fixture
"""Synthetic fixture: prohibited criminal prediction by profiling (Article 5(1)(d)).
Expected: classifier should return 'prohibited'."""

import sklearn
from sklearn.ensemble import RandomForestClassifier

def train_recidivism_model(profiles):
    """Predict recidivism risk from personality traits alone."""
    model = RandomForestClassifier()
    features = [extract_personality_traits(p) for p in profiles]
    model.fit(features, [p.reoffended for p in profiles])
    return model


def predictive_policing_score(suspect_profile):
    """Score a suspect using crime prediction on personality alone."""
    return _crime_predict(suspect_profile.personality)
