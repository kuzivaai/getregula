# synthetic-test-fixture
"""Synthetic fixture: customer support chatbot.
Expected: classifier should return 'limited_risk' (Article 50), NOT high_risk."""

import openai

def support_bot_reply(user_message):
    """Conversational AI for customer support — Article 50 transparency applies."""
    return openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a customer support chatbot. Disclose AI to the user."},
            {"role": "user", "content": user_message},
        ],
    )
