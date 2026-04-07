# synthetic-test-fixture
"""Synthetic fixture: Annex III Category 4 — employment.
Expected: classifier should return 'high_risk'."""

import openai

def cv_screen_pipeline(resume_text):
    """Hiring decision support — screens CVs and ranks candidates."""
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": f"Score this candidate: {resume_text}"}],
    )
    return rank_candidate(response)


def resume_screen_batch(resumes):
    """Filter resumes by AI score."""
    return [r for r in resumes if cv_screen_pipeline(r)["score"] > 0.7]
