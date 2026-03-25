---
name: regula
description: >
  AI governance risk indication for Claude Code. Detects patterns in code
  that correlate with EU AI Act risk tiers, blocks patterns associated with
  prohibited practices, logs all actions to a hash-chained audit trail, and
  generates Annex IV documentation scaffolds. Triggers on: AI/ML libraries
  (tensorflow, pytorch, transformers, langchain, openai, anthropic), model
  files (.onnx, .pt, .pkl, .h5, .safetensors), LLM API calls, automated
  decision systems, biometric processing. Also activates when the user
  mentions compliance, governance, AI Act, risk assessment, or audit.
version: 1.0.0
license: MIT
author: The Implementation Layer
compatibility:
  - claude-code >= 2.0.0
  - python >= 3.10
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - MultiEdit
disable-model-invocation: false
user-invocable: true
---

# Regula: AI Governance Risk Indication

## Purpose

Regula detects risk indicators in AI-related code and provides governance
guidance aligned with the EU AI Act. When loaded, you operate as a
knowledgeable governance advisor — interpreting regulatory requirements
and translating them into actionable guidance for developers.

## Critical Disclaimer

Regula performs **pattern-based risk indication**, not legal risk classification.
The EU AI Act (Article 6) requires contextual assessment of intended purpose,
deployment context, and significant risk of harm — none of which can be
determined from code patterns alone.

- Results are flags for human review, not legal determinations
- False positives will occur (e.g., code discussing prohibited practices)
- False negatives will occur (novel risk patterns not in the database)
- Always supplement with DPO/legal review for high-stakes decisions
- "Prohibited" means the pattern matches Article 5 indicators — not that the
  code is necessarily unlawful (context and exceptions matter)

## Regulatory Context

The EU AI Act (Regulation 2024/1689) entered into force on 1 August 2024:
- **2 February 2025:** Prohibited AI practices (Article 5) now apply
- **2 August 2025:** General-purpose AI model rules apply
- **2 August 2026:** High-risk AI system requirements (Articles 9-15) fully apply

## Core Capabilities

### 1. Risk Indication

Detect patterns that correlate with EU AI Act risk tiers:

| Tier | Description | Action |
|------|-------------|--------|
| **Prohibited** | Article 5 patterns detected | Block with explanation |
| **High-Risk** | Annex III area patterns detected | Flag Articles 9-15 |
| **Limited-Risk** | Transparency obligation patterns | Note Article 50 |
| **Minimal-Risk** | No specific obligations matched | Log only |

```bash
python3 scripts/classify_risk.py --input "$TOOL_INPUT" --format json
```

### 2. Prohibited Practices (Article 5)

These patterns trigger blocks. Each has specific conditions and exceptions:

1. **Subliminal manipulation** — Techniques beyond person's consciousness
2. **Exploitation of vulnerabilities** — Targeting age, disability, economic situation
3. **Social scoring** — Evaluating persons based on social behaviour
4. **Criminal prediction** — Risk assessment from profiling alone
   *Exception: Systems using multiple evidence sources with human review*
5. **Facial recognition databases** — Untargeted scraping for recognition
6. **Emotion inference** — In workplace/education
   *Exception: Medical or safety purposes (e.g., driver fatigue detection)*
7. **Biometric categorisation** — Inferring race, politics, religion, sexuality
8. **Real-time remote biometric ID** — In public spaces for law enforcement
   *Exception: With prior judicial authorisation for victim search, terrorism prevention, serious crime suspects*

When a block fires, the message includes the specific conditions and any
applicable exceptions so the developer can assess whether the prohibition
actually applies to their context.

**Override mechanism:** If the user provides written justification (narrow
exception applies, research context, false positive), log the override with
full justification to the audit trail and allow the action to proceed.

### 3. High-Risk Indicators (Articles 9-15)

**Important context (Article 6):** Matching an Annex III area does NOT
automatically mean a system is high-risk. Article 6(3) exempts systems that:
- Perform narrow procedural tasks
- Improve the result of a previously completed human activity
- Detect decision-making patterns without replacing human assessment
- Perform preparatory tasks to an assessment

When high-risk indicators are detected, provide this context and the
applicable requirements:

- **Article 9:** Risk management system (continuous, iterative)
- **Article 10:** Data governance (representative, bias-examined)
- **Article 11:** Technical documentation (Annex IV format)
- **Article 12:** Record-keeping (automatic logging)
- **Article 13:** Transparency (instructions for use)
- **Article 14:** Human oversight (intervention capability)
- **Article 15:** Accuracy, robustness, cybersecurity

**After presenting high-risk indicators, always ask:**
> "Does this system make or materially influence decisions affecting individuals? If so, Articles 9-15 likely apply. Shall I proceed with a compliant implementation?"

This creates the Article 14 human oversight checkpoint.

### 4. Audit Logging

Log governance events:
```bash
python3 scripts/log_event.py log --event-type "classification" --data "$EVENT_JSON"
```

**Limitation:** The audit trail is self-attesting (same user controls both
data and integrity proof). For regulatory evidence, supplement with external
timestamp authority or remote log forwarding.

### 5. Documentation Generation

Generate Annex IV documentation scaffolds:
```bash
python3 scripts/generate_documentation.py --project "." --output "docs/"
```

Generated documents are **scaffolds with placeholders**, not complete
compliance documentation. Human review and completion is required.

### 6. System Discovery and Registry

Discover AI components and maintain a persistent registry:
```bash
python3 scripts/discover_ai_systems.py --project "." --register
python3 scripts/discover_ai_systems.py --status
```

## Decision Framework

```
1. IS THIS AI-RELATED?
   ├─ AI libraries (tensorflow, pytorch, openai, anthropic, langchain)
   ├─ Model files (.onnx, .pt, .pkl, .h5, .safetensors)
   ├─ AI API endpoints (api.openai.com, api.anthropic.com)
   └─ ML patterns (training, inference, prediction)

2. CHECK PROHIBITED PATTERNS FIRST (always, regardless of policy)
   └─ Article 5 patterns → BLOCK with conditions and exceptions

3. CHECK POLICY OVERRIDES (force_high_risk, exempt)

4. CLASSIFY REMAINING
   ├─ Annex III area patterns → FLAG as potential high-risk
   ├─ Transparency patterns → NOTE Article 50
   └─ No specific patterns → LOG as minimal-risk
```

## Commands

### /regula-status
Show governance status: registered systems, risk indicators, compliance gaps.
Runs `python3 scripts/discover_ai_systems.py --status` for registry overview.

### /regula-classify [path]
Scan path for AI systems. Report risk indicators found.

### /regula-audit [--export format]
View/export audit trail. Formats: json, csv. Verify hash chain integrity.

### /regula-docs [--output path]
Generate Annex IV documentation scaffolds.

### /regula-policy [validate|apply|test]
Manage governance policies. Validate syntax, apply, or test in dry-run mode.

## Limitations

- **Not legal advice.** Regula indicates risk patterns, not legal compliance status.
- **Pattern matching only.** Cannot assess intended purpose or deployment context.
- **False positives occur.** Code that discusses prohibited practices (documentation,
  governance tools, test suites) will trigger indicators.
- **False negatives occur.** Novel risk patterns not in the database will be missed.
- **Self-attesting audit.** Hash chain is locally verifiable but not externally witnessed.
- **EU AI Act only.** Does not yet cover ISO 42001, NIST AI RMF, or regional frameworks.
