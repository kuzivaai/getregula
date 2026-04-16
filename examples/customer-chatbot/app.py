"""Minimal customer-support chatbot reference app for Regula.

This example intentionally triggers an EU AI Act Article 50 (limited-risk)
classification when scanned with `regula check`. It exists so that new
Regula users have a runnable fixture to demonstrate Article 50 transparency
obligations — not as production code.

What it does
------------
Wraps an LLM call behind a tiny dialogue loop that answers customer
questions. The prompt injects a system instruction identifying the
assistant as AI, which is how you satisfy the Article 50 disclosure rule.

Why it is limited-risk under the EU AI Act
------------------------------------------
Article 50(1) requires providers of AI systems intended to interact
directly with natural persons to design and develop those systems such
that the persons concerned are informed that they are interacting with
an AI system. A customer-facing chatbot is the textbook example.

See: https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=OJ:L_202401689
(Article 50)
"""
from __future__ import annotations

import os
from dataclasses import dataclass

# Placeholder for whichever LLM SDK a real deployment would use.
# This fixture does not actually call a network service.


DISCLOSURE = (
    "You are SupportBot, an AI assistant. You must always begin your "
    "first reply in a conversation by clearly identifying yourself as "
    "an AI system, per EU AI Act Article 50."
)


@dataclass
class ChatMessage:
    role: str  # "user" or "assistant"
    content: str


def build_customer_chatbot_prompt(
    conversation: list[ChatMessage], user_question: str
) -> list[dict[str, str]]:
    """Assemble the message list the chatbot sends to the LLM."""
    messages: list[dict[str, str]] = [{"role": "system", "content": DISCLOSURE}]
    for msg in conversation:
        messages.append({"role": msg.role, "content": msg.content})
    messages.append({"role": "user", "content": user_question})
    return messages


def respond(messages: list[dict[str, str]]) -> str:
    """Return a stub reply. A real virtual assistant would call an LLM here."""
    # In production: openai.chat.completions.create(model=..., messages=messages)
    # The key Regula cares about is that this is a customer-facing chatbot
    # requiring Article 50 disclosure — not which model backs it.
    if not os.environ.get("OPENAI_API_KEY"):
        return (
            "Hi, I'm SupportBot — an AI assistant. "
            "(No API key set; returning a canned reply.)"
        )
    return "Hi, I'm SupportBot, an AI assistant. How can I help?"


if __name__ == "__main__":
    history: list[ChatMessage] = []
    question = "When does my order ship?"
    prompt = build_customer_chatbot_prompt(history, question)
    reply = respond(prompt)
    print(reply)
