# regula-ignore
"""Fixture: Mixed-tier system with both high-risk and limited-risk patterns.

Contains employment AI (high-risk, Annex III Category 4) alongside
a chatbot interface (limited-risk, Article 50).
"""
import openai
from sklearn.ensemble import RandomForestClassifier

# High-risk: employment screening
screening_model = RandomForestClassifier()

def screen_cv_candidates(resumes):
    """Automated CV screening for hiring decisions."""
    return screening_model.predict(resumes)

# Limited-risk: chatbot interface
def chatbot_respond(user_message):
    """Virtual assistant for general queries."""
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": user_message}],
    )
    return response.choices[0].message.content
