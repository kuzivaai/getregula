# Labelling Criteria for Regula Benchmark

Version 1.0 — 2026-04-25

## Purpose

This document defines the criteria for labelling Regula scan findings as
**True Positive (TP)** or **False Positive (FP)**. Consistent application
of these criteria is required for precision measurements to be meaningful
and reproducible.

## Definitions

- **True Positive (TP):** Regula correctly identified a genuine risk
  indicator — the flagged code genuinely performs or enables the behaviour
  described by the finding's tier and category.
- **False Positive (FP):** Regula flagged code that does not perform or
  enable the described behaviour. The pattern matched syntactically but
  the semantic intent does not match.

## Decision Framework

For each finding, answer this question:

> **Does this code, in its production context, genuinely perform or enable
> the behaviour described in the finding's `description` and `category`?**

If YES → **TP**. If NO → **FP**.

### Tier-Specific Criteria

#### Prohibited (Article 5)

| TP if... | FP if... |
|----------|----------|
| Code implements social scoring, real-time biometric identification, emotion inference in workplace/education, or other Article 5 prohibited practices | Pattern matched on keyword but code serves a different purpose (e.g., "score" in a game, "emotion" in a sentiment analysis library not deployed in workplace) |
| Code has no meaningful guardrails against prohibited use | Code includes explicit scope limitations or is clearly non-deployed research |

#### High-Risk (Annex III)

| TP if... | FP if... |
|----------|----------|
| Code makes or influences decisions in Annex III domains: employment, credit, education, law enforcement, migration, critical infrastructure, healthcare | Code uses similar ML techniques but not in an Annex III domain |
| Code processes biometric data for identification or categorisation | Code processes images/audio for non-biometric purposes |
| The AI system's output materially affects natural persons | Code is internal tooling with no external impact |

#### Limited Risk (Article 50)

| TP if... | FP if... |
|----------|----------|
| Code generates synthetic text, images, audio, or video that could be mistaken for human-created content | Code generates structured data (JSON, CSV) that nobody would mistake for human content |
| Code operates a chatbot or conversational interface without disclosure | Code is a CLI tool or API that clearly identifies itself as software |
| Deepfake generation or manipulation capability | Image processing that is clearly not generative (resize, crop, format conversion) |

#### Agent Autonomy

| TP if... | FP if... |
|----------|----------|
| AI-generated output flows to system commands, HTTP mutations, file writes, or database changes without a human approval gate | Code executes commands but the input is hardcoded or user-initiated (not AI-generated) |
| Agent can autonomously call tools, APIs, or external services | Code imports an agent library but only for non-agentic use (e.g., structured output parsing) |

#### AI Security (OWASP LLM Top 10)

| TP if... | FP if... |
|----------|----------|
| User input flows to LLM prompts without sanitisation (LLM01: Prompt Injection) | Input is validated, escaped, or from a trusted source |
| Model outputs are rendered as HTML/JS without escaping (LLM02: Output Handling) | Outputs are logged or stored as plain text |
| API keys, tokens, or credentials are hardcoded or logged (LLM06: Sensitive Data) | Test fixtures using dummy values or environment variables |
| Model files loaded via pickle/joblib without integrity checks (LLM05: Supply Chain) | Model loading with hash verification or from trusted registry |

#### Credential Exposure

| TP if... | FP if... |
|----------|----------|
| Real API keys, tokens, or secrets in source code | Test/example placeholder values (e.g., `sk-test-...`, `your-api-key-here`) |
| Credentials logged, printed, or sent to external services | Credentials read from env vars or secret managers (secure pattern) |

#### Minimal Risk

| TP if... | FP if... |
|----------|----------|
| Code genuinely uses AI/ML for inference, training, or prediction | Code imports an AI library but only uses utility functions (data formatting, validation) |
| The file contains meaningful AI application logic | The file is pure infrastructure (config, routing, serialisation) that happens to be in an AI project |

### Context Rules

1. **Example/demo code**: Label based on what the code does, not where it
   lives. If `examples/chat.py` implements a real chatbot with no
   disclosure, that IS a limited-risk finding (the example teaches users
   to build non-compliant systems).

2. **Test code**: Generally FP unless the test itself contains hardcoded
   credentials or demonstrates a genuinely risky pattern.

3. **Library vs application**: Library infrastructure code (serialisation,
   API marshalling, type definitions) is typically FP for tier-specific
   findings. Application code that uses libraries to make decisions
   affecting people is typically TP.

4. **Confidence score**: The confidence score does NOT determine TP/FP.
   A low-confidence finding can be TP; a high-confidence finding can be
   FP. Label based on what the code does, not what the score says.

5. **Dual-use code**: If code could be used for both risky and benign
   purposes, label based on the **primary documented purpose** of the
   project. A face detection library intended for photo organisation is
   different from one intended for surveillance.

## Labelling Process

1. Open the finding's source file at the indicated line number
2. Read surrounding context (±20 lines minimum)
3. Consider the project's stated purpose (README, documentation)
4. Apply the tier-specific criteria above
5. Set `"label": "tp"` or `"label": "fp"`
6. Add a brief `"notes"` explaining the rationale (required for auditability)

## Quality Controls

- **Single reviewer minimum**: One person labels all findings for consistency
- **Spot-check target**: At least 10% of labels should be independently
  verified by a second reviewer (not yet implemented — tracked as P2)
- **Conflict resolution**: If two reviewers disagree, the finding is
  discussed and the agreed label is documented with both perspectives
- **Re-validation**: After pattern changes, re-scan and check whether
  existing labels still match the current output (key = project + file + line)

## Metrics Computed from Labels

| Metric | Formula | Purpose |
|--------|---------|---------|
| Precision | TP / (TP + FP) | What fraction of findings are genuine? |
| Recall | TP / (TP + FN) | What fraction of real issues are found? (requires planted corpus) |
| F1 Score | 2 × (P × R) / (P + R) | Harmonic mean of precision and recall |
| Youden Index (J) | Sensitivity + Specificity − 1 | OWASP Benchmark standard; requires TNs |
| MCC | (TP×TN − FP×FN) / √((TP+FP)(TP+FN)(TN+FP)(TN+FN)) | Balanced measure even with class imbalance |

**Current limitation:** Only precision is measurable from labelled scan
output. Recall, F1, Youden, and MCC require a corpus with known ground
truth (planted issues or exhaustively audited code) to establish FN and
TN counts.

## Corpus Types

| Corpus | Purpose | Status |
|--------|---------|--------|
| **Random corpus** | Precision on 50 randomly selected AI repos (blind-labelled) | 201 labels, 51.2% precision |
| **Library corpus** | Precision on OSS AI libraries (development reference) | 257 labels, 15.2% precision |
| **App corpus** | Precision on hand-picked AI apps (development reference) | 189 labels, 66.1% precision |
| **Synthetic corpus** | Recall on controlled fixtures with known issues | 13 fixtures in `benchmarks/synthetic/` |
| **Planted corpus** | Recall on real code with seeded issues | Not yet built |
