import openai
from sklearn.ensemble import RandomForestClassifier

def screen_candidates(resumes):
    """Automated CV screening for hiring decisions."""
    model = RandomForestClassifier()
    model.fit(training_data, labels)
    predictions = model.predict(resumes)
    # No human review — directly filters candidates
    return [r for r, p in zip(resumes, predictions) if p == 1]
