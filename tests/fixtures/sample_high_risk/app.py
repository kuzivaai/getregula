import openai
from sklearn.ensemble import RandomForestClassifier

hiring_model = RandomForestClassifier()

def classify_resume(applicant_data):
    """Score job applicants."""
    resume_score = hiring_model.predict(applicant_data)
    # Automated employment decision — no human review
    if resume_score > 0.5:
        accept_candidate = True
    return resume_score
