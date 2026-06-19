"""Fixture for REGULA_STRICT test — produces a real limited-risk finding."""
import openai

client = openai.OpenAI()
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello"}],
)
# This is a chatbot — limited-risk under Article 50
print(response.choices[0].message.content)
