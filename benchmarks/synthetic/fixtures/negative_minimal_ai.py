# synthetic-test-fixture
"""Synthetic fixture: AI library imported but used for code review only.
Expected: classifier should return 'minimal_risk' or NOT_AI tier; NOT high_risk."""

import openai

def review_code_diff(diff_text):
    """Use an LLM to summarise a git diff for the developer."""
    return openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": f"Summarise this diff:\n{diff_text}"}],
    )
