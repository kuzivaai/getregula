# customer-chatbot — limited-risk fixture (Article 50)

A minimal reference project that triggers an EU AI Act limited-risk
classification (Article 50 transparency obligation) when scanned with Regula.

## Run the scan

```
regula check examples/customer-chatbot --scope all
```

(`--scope all` includes example-provenance findings, which the default
production scope deliberately excludes — see `examples/README.md`.)

Expected output (captured against Regula v1.9.0 on 2026-08-14):

```
Regula Scan: examples/customer-chatbot
============================================================

Decision: insufficient_information
Jurisdiction: eu
Rule resolution: unresolved
Facts needed to resolve the next decision: 2
  - is_ai_system: Does the subject meet the governing law's definition of an AI system or regulated automated technology?
  - jurisdiction_in_scope: Does this jurisdiction's territorial and operator scope apply?

Detector observations (not legal facts):

  Detector summary: ARTICLE 50 PATTERNS
  The scanner found patterns relevant to Article 50 review.
  Resolve the facts listed above before attaching a transparency duty.
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
      AI API call detected — verify error handling is in place (detector priority: 40)
    ? app.py:29 — Limited Risk (Article 50)
      Chatbots and conversational AI (detector priority: 20)
============================================================
```

The bracketed numbers are detector priorities, not probabilities. Earlier
versions of this file labelled them as a confidence percentage, which invited
reading a pattern count as a likelihood. The tool no longer emits that wording.

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
