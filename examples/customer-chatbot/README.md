# customer-chatbot — limited-risk fixture (Article 50)

A minimal reference project that triggers an EU AI Act limited-risk
classification (Article 50 transparency obligation) when scanned with Regula.

## Run the scan

```
regula check examples/customer-chatbot --scope all
```

(`--scope all` includes example-provenance findings, which the default
production scope deliberately excludes — see `examples/README.md`.)

Expected output (captured against Regula v1.7.6 on 2026-07-20):

```
Regula Scan: examples/customer-chatbot
============================================================

  Verdict: LIMITED-RISK
  Your project has indicators of limited-risk AI components (Article 50 transparency).
  If confirmed, Article 50 requires disclosing AI usage to users.
  Files scanned:      1
  Prohibited:         0
  Credentials:        0
  High-risk:          0
  Agent autonomy:     0
  Limited-risk:       1
  Suppressed:         0
  BLOCK tier:         0
  WARN tier:          0
  INFO tier:          2
  Lifecycle:          deploy: 1, develop: 2

  LIMITED-RISK (Article 50):
    [INFO] [ 20] app.py:29 — Chatbots and conversational AI [develop]

  Questions for human review (2):
    ? app.py:66 — AI Security (LLM06)
      AI API call detected — verify error handling is in place (confidence: 40%)
    ? app.py:29 — Limited Risk (Article 50)
      Chatbots and conversational AI (confidence: 20%)
============================================================
```

## Why Regula flags this

Article 50(1) of the EU AI Act requires that providers of AI systems intended
to interact directly with natural persons design and develop those systems such
that the persons concerned are informed that they are interacting with an AI
system. A customer-facing assistant is the textbook case.

## What the fixture does

`app.py` assembles a prompt for an LLM call and returns a stub reply. The
system prompt at the top contains the Article 50 disclosure clause — a small
example of how you satisfy the obligation in code.

## What Regula does NOT tell you

Whether your disclosure text is *sufficient* under Article 50 — that is a
product and legal question, not a pattern-match question. Regula tells you the
obligation exists; the wording is yours.
