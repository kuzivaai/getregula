# customer-chatbot — limited-risk fixture (Article 50)

A minimal reference project that triggers an EU AI Act limited-risk
classification (Article 50 transparency obligation) when scanned with Regula.

## Run the scan

```
regula check examples/customer-chatbot
```

Expected output (captured against Regula v1.7.0 on 2026-04-16):

```
Regula Scan: /home/mkuziva/getregula/examples/customer-chatbot
============================================================
  Files scanned:      1
  Prohibited:         0
  Credentials:        0
  High-risk:          0
  Agent autonomy:     0
  Limited-risk:       1
  Suppressed:         0
  BLOCK tier:         0
  WARN tier:          0
  INFO tier:          1

  LIMITED-RISK (Article 50):
    [INFO] [ 45] app.py:1 — Chatbots and conversational AI
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
