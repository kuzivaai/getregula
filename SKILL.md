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
version: 1.1.0
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

## Regulatory Context

The EU AI Act (Regulation 2024/1689) entered into force on 1 August 2024:
- **2 February 2025:** Prohibited AI practices (Article 5) now apply
- **2 August 2025:** General-purpose AI model rules apply
- **2 August 2026:** High-risk AI system requirements (Articles 9-15) apply
  *(Digital Omnibus proposes December 2027 — not yet enacted)*

Run `python3 scripts/timeline.py` for current enforcement dates.

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
python3 scripts/cli.py classify --input "$TOOL_INPUT" --format json
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
   *Exception: With prior judicial authorisation for specific scenarios*

**Override mechanism:** If the user provides written justification (narrow
exception applies, research context, false positive), log the override with
full justification to the audit trail and allow the action to proceed.

### 3. High-Risk Indicators (Articles 9-15)

**Important context (Article 6):** Matching an Annex III area does NOT
automatically mean a system is high-risk. Article 6(3) exempts systems that:
- Perform narrow procedural tasks
- Improve the result of a previously completed human activity
- Detect decision-making patterns without replacing human assessment

**After presenting high-risk indicators, always ask:**
> "Does this system make or materially influence decisions affecting
> individuals? If so, Articles 9-15 likely apply. Shall I proceed with
> a compliant implementation?"

### 4. Questionnaire Mode (Ambiguous Classifications)

When pattern-based classification is ambiguous (low confidence score or
conflicting indicators), offer to run a context-driven questionnaire:

```bash
python3 scripts/questionnaire.py --generate
python3 scripts/questionnaire.py --evaluate '{"autonomous_decisions":"yes",...}'
```

8 questions derived from Article 6 criteria. Combines pattern-based signals
with context about intended purpose. Both questions and answers are logged.

### 5. Audit Trail

Hash-chained, append-only, file-locked event log:
```bash
python3 scripts/cli.py audit verify              # Check chain integrity
python3 scripts/cli.py audit export --format csv  # Export as CSV
```

### 6. Documentation Generation

Generate Annex IV documentation scaffolds (not complete compliance docs):
```bash
python3 scripts/cli.py report --format html --output report.html --include-audit
python3 scripts/generate_documentation.py --project "." --output "docs/"
```

### 7. System Discovery and Registry

Discover AI components and maintain a persistent inventory:
```bash
python3 scripts/cli.py discover --project "." --register
python3 scripts/cli.py status
```

### 8. Governance News Feed

Curated AI governance news from 7 reputable sources (IAPP, NIST, Stanford
HAI, ICO, EU AI Act, Brookings, Help Net Security):
```bash
python3 scripts/cli.py feed                          # CLI text
python3 scripts/cli.py feed --format html -o feed.html  # HTML digest
python3 scripts/cli.py feed --sources                # List sources
```

### 9. Session Risk Aggregation

Aggregate individual tool classifications into a session-level risk profile:
```bash
python3 scripts/cli.py session              # Current session profile
python3 scripts/cli.py session --hours 24   # Last 24 hours
```

### 10. CI/CD Baseline Comparison

Save compliance baseline and report only net-new findings:
```bash
python3 scripts/cli.py baseline save           # Save current state
python3 scripts/cli.py baseline compare        # Show changes
python3 scripts/cli.py baseline compare --fail-on-new  # Fail CI on new findings
```

### 11. EU AI Act Timeline

Current enforcement dates with Digital Omnibus status:
```bash
python3 scripts/cli.py timeline
```

### 12. ISO 42001 Cross-Mapping

Risk classifications include ISO 42001 control references alongside EU AI
Act articles. See `references/iso_42001_mapping.yaml` for the full mapping
(24 controls, ~90% coverage).

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

### /regula-classify [path]
Scan path for AI systems. Report risk indicators found.

### /regula-audit [verify|export]
View/export audit trail. Verify hash chain integrity.

### /regula-docs [--output path]
Generate Annex IV documentation scaffolds.

### /regula-report [--format html|sarif|json]
Generate governance reports. HTML for stakeholders, SARIF for CI/CD.

### /regula-feed
AI governance news from curated sources.

### /regula-timeline
Current EU AI Act enforcement dates with Digital Omnibus status.

### /regula-questionnaire
Context-driven risk assessment for ambiguous classifications.

### /regula-session
Session-level risk aggregation across tool calls.

### /regula-baseline [save|compare]
CI/CD baseline comparison for incremental compliance.

### /regula-policy [validate|apply|test]
Manage governance policies.

## Multi-Platform Support

Regula works across AI coding platforms that share the same hook protocol:
```bash
python3 scripts/cli.py install claude-code   # Claude Code
python3 scripts/cli.py install copilot-cli   # GitHub Copilot CLI
python3 scripts/cli.py install windsurf      # Windsurf Cascade
python3 scripts/cli.py install pre-commit    # pre-commit framework
python3 scripts/cli.py install git-hooks     # Direct git hooks
```

## Limitations

- **Not legal advice.** Risk indication, not legal classification.
- **Pattern matching only.** Cannot assess intended purpose or deployment context.
- **False positives occur.** Code discussing prohibited practices will trigger.
- **False negatives occur.** Novel patterns not in the database will be missed.
- **Self-attesting audit.** Locally verifiable, not externally witnessed.
