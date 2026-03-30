# Regula Competitive Gaps — Design Spec
**Date:** 2026-03-30
**Status:** Approved

## Overview

Four features that close the remaining honest gaps in Regula relative to competing tools — model inventory, expanded framework detection, multi-framework cross-referencing wired into check output, and a self-contained HTML report for non-developer audiences.

These features compose: `regula check --format html --framework nist-ai-rmf` produces a single file containing findings, NIST cross-refs, and a model inventory.

---

## Feature 1 — `regula inventory`

### Purpose

Currently Regula detects that a project uses OpenAI (import-level). It does not detect *which* model is being used. This matters for EU AI Act compliance: GPAI obligations under Article 51 apply to frontier models (GPT-4o, Claude 3.5, Gemini 1.5 Pro); Article 53(1) provides exemptions for open-weight models below the compute threshold.

### New File

`scripts/model_inventory.py`

### Detection Strategy

Scan Python, JS/TS, YAML, JSON, `.env`, and config files for:

1. **Model name strings** — regex match against a known-models catalogue (see below)
2. **`from_pretrained("model-name")` calls** — extract model identifier from argument
3. **SDK instantiation with model param** — e.g. `OpenAI()` + `model="gpt-4o"` in same file
4. **API key patterns** — confirm live usage (not just import)

### Known-Models Catalogue

Hardcoded in `model_inventory.py`. Each entry has:
- `provider`: OpenAI / Anthropic / Meta / Mistral / Google / Cohere / etc.
- `model_id`: the string to match (e.g. `"gpt-4o"`, `"gpt-4o-mini"`)
- `gpai_tier`: `"frontier"` | `"open-weight"` | `"unknown"`
- `eu_note`: short annotation for the report

Frontier examples: `gpt-4o`, `gpt-4-turbo`, `claude-3-5-sonnet`, `claude-3-opus`, `gemini-1.5-pro`, `gemini-2.0-flash`, `mistral-large`, `command-r-plus`

Open-weight examples: `llama-3.1-8b`, `llama-3.1-70b`, `llama-3.1-405b`, `mistral-7b`, `mixtral-8x7b`, `phi-3`, `gemma-2`, `qwen-2.5`, `deepseek-r1`, `falcon-40b`

### Output Schema

```json
{
  "models": [
    {
      "provider": "OpenAI",
      "model_id": "gpt-4o",
      "gpai_tier": "frontier",
      "eu_note": "GPAI obligations may apply (Article 51)",
      "occurrences": [
        {"file": "app/chat.py", "line": 14}
      ]
    }
  ],
  "summary": {
    "total": 2,
    "frontier": 1,
    "open_weight": 1,
    "unknown": 0
  }
}
```

### CLI

```
regula inventory [PATH] [--format table|json]
```

Default format: table. `--format json` for machine consumption or HTML report integration.

### EU AI Act Annotations (static, honest)

| GPAI tier | Note |
|-----------|------|
| frontier | GPAI obligations may apply (Article 51) — verify systemic risk threshold |
| open-weight | GPAI exemption likely (Article 53(1)) — verify compute threshold |
| unknown | Model not in catalogue — classify manually |

These are flags for human review, not legal conclusions.

### Tests

- `test_model_inventory_detects_gpt4o` — fixture with `model="gpt-4o"` string
- `test_model_inventory_detects_from_pretrained` — fixture with `from_pretrained("llama-3.1-8b")`
- `test_model_inventory_json_schema` — output matches schema above
- `test_model_inventory_empty_project` — returns empty models list, not an error
- `test_model_inventory_cli_table` — CLI exits 0, produces tabular output

---

## Feature 2 — Framework Coverage Expansion

### Purpose

`code_analysis.py` currently detects 12 AI architectures. The gap matters because `regula docs` auto-populates Annex IV documentation fields — a project using CrewAI or Haystack gets "Unknown architecture" when it should get "Multi-agent orchestration (CrewAI)."

### Changes

**File**: `scripts/code_analysis.py` — `ARCHITECTURE_PATTERNS` dict

**Additions** (16 new entries, 12 → 28):

| Framework | Import pattern | Description |
|-----------|---------------|-------------|
| AutoGen | `from autogen`, `import autogen`, `pyautogen` | Multi-agent conversation (Microsoft) |
| CrewAI | `from crewai`, `import crewai` | Role-based multi-agent orchestration |
| Haystack | `from haystack`, `import haystack` | RAG / document pipeline (deepset) |
| DSPy | `from dspy`, `import dspy` | Programmatic LM pipelines (Stanford) |
| Groq SDK | `from groq`, `import groq` | Groq inference API |
| AWS Bedrock | `import boto3` + `bedrock`, `from botocore.*bedrock` | AWS managed model API |
| Google Vertex AI | `from vertexai`, `import vertexai`, `google.cloud.aiplatform` | Google Cloud model API |
| LiteLLM | `from litellm`, `import litellm` | Multi-provider LLM proxy |
| Semantic Kernel | `from semantic_kernel`, `import semantic_kernel` | Microsoft SK (Python) |
| Instructor | `from instructor`, `import instructor` | Structured outputs from LLMs |
| PydanticAI | `from pydantic_ai`, `import pydantic_ai` | Type-safe agent framework |
| SmolAgents | `from smolagents`, `import smolagents` | HuggingFace agent library |
| Together AI | `from together`, `import together` | Together AI inference API |
| Replicate | `import replicate`, `from replicate` | Replicate model hosting API |
| Mistral SDK | `from mistralai`, `import mistralai` | Mistral AI Python SDK |
| Google Generative AI | `import google.generativeai`, `from google.generativeai` | Gemini API (non-Vertex) |
| Ollama | `import ollama`, `from ollama` | Local model inference |

Also expand `risk_patterns.py` `AI_INDICATORS["libraries"]` to match.

### Tests

- `test_framework_detection_autogen` — fixture with `from autogen import AssistantAgent`
- `test_framework_detection_crewai` — fixture with `from crewai import Agent`
- One test per new framework (16 tests) — all use the existing fixture pattern in `test_classification.py`

---

## Feature 3 — Multi-Framework Wired into Check Output

### Purpose

`framework_mapper.py` already maps all EU AI Act articles to NIST AI RMF, ISO 42001, NIST CSF, SOC 2, ISO 27001, OWASP LLM Top 10, and MITRE ATLAS. This data is not surfaced in `regula check` output, so users don't know it exists.

### Changes

**File**: `scripts/compliance_check.py`

Add optional `frameworks` parameter to the main check function. When provided, each finding's output includes a `frameworks` block containing the cross-references for that finding's article.

**File**: `scripts/cli.py`

Add `--framework` flag to the `compliance` (and `check`) subcommand:

```
--framework eu-ai-act|nist-ai-rmf|iso-42001|nist-csf|soc2|iso-27001|owasp-llm-top10|mitre-atlas|all
```

Accepts comma-separated list. Default: not set (no cross-refs, backward compatible).

### Output (JSON, with `--framework nist-ai-rmf`):

```json
{
  "article": "10",
  "finding": "...",
  "frameworks": {
    "nist_ai_rmf": {
      "functions": ["MAP", "MEASURE"],
      "subcategories": ["MAP 2.1: ...", "MEASURE 2.6: ..."]
    }
  }
}
```

### Text Output (with `--framework nist-ai-rmf`):

```
[HIGH-RISK] Article 10 — Data Governance
  Finding: No dataset documentation detected
  NIST AI RMF: MAP 2.1, MEASURE 2.6
```

### Tests

- `test_compliance_check_framework_nist` — check output includes `frameworks.nist_ai_rmf` when flag set
- `test_compliance_check_no_framework_flag` — output unchanged when flag absent
- `test_compliance_check_framework_all` — all 7 frameworks present in output

---

## Feature 4 — HTML Report

### Purpose

DPOs, legal teams, and auditors cannot run `regula check`. They need something they can open in a browser, read, and store as audit evidence. The HTML report is the zero-friction path.

### Invocation

```
regula check --format html [PATH] > report.html
regula check --format html [PATH] -o report.html
```

The `-o` flag (output file) is added alongside `--format html` support.

### File

`scripts/pdf_export.py` already has HTML generation for Annex IV. The HTML report is a separate, more comprehensive template added to `pdf_export.py` as `generate_html_report(results: dict) -> bytes`.

### Structure

```
┌─────────────────────────────────────────┐
│  HEADER                                 │
│  Project name · Scan date · Risk tier   │
│  (risk tier: large, dominant badge)     │
├─────────────────────────────────────────┤
│  EXECUTIVE SUMMARY                      │
│  Finding counts by tier                 │
│  Models detected · Frameworks coverage  │
├─────────────────────────────────────────┤
│  FINDINGS                               │
│  Grouped by tier (PROHIBITED first)     │
│  Each: article · description · file:ln  │
│  Expandable: framework cross-refs       │
├─────────────────────────────────────────┤
│  MODEL INVENTORY                        │
│  Table: Provider · Model · Tier · Note  │
├─────────────────────────────────────────┤
│  FRAMEWORK MAPPING                      │
│  Collapsible: NIST / ISO / OWASP refs   │
├─────────────────────────────────────────┤
│  METHODOLOGY                            │
│  What was checked · What wasn't         │
│  Honest about static analysis limits    │
└─────────────────────────────────────────┘
```

### Aesthetic Direction

**Editorial/Institutional** — built for auditors and DPOs, not developers.

- **Background**: `#FAFAF8` (warm off-white) with `#1B2A4A` (deep navy) as primary text/accent
- **Risk tier colours**: `#C0392B` (scarlet, PROHIBITED) / `#D35400` (amber, HIGH-RISK) / `#1A7A6E` (teal, LIMITED) / `#27AE60` (green, MINIMAL)
- **Typography**: `DM Serif Display` (headings, via Google Fonts) + `DM Mono` (code, file references) + `Georgia` (body fallback)
- **Layout**: Single-column, max-width 860px, centred, generous vertical rhythm
- **Risk badge**: Full-width coloured band at top — dominant, unambiguous
- **Interactivity**: Pure CSS `<details>` for collapsible sections (no JS required for core function); optional JS for copy-to-clipboard on code references
- **Print styles**: `@media print` — colours preserved, no collapsibles (all expanded), page-break hints on sections
- **Self-contained**: Google Fonts loaded via `@import` in `<style>` block; no external JS

### Tests

- `test_html_report_structure` — output contains all 6 sections (header, summary, findings, inventory, frameworks, methodology)
- `test_html_report_risk_badge_prohibited` — PROHIBITED projects get scarlet badge
- `test_html_report_self_contained` — no `<script src=` or `<link href=` pointing to external resources (only Google Fonts `@import` exception)
- `test_html_report_cli_integration` — `regula check --format html` exits 0 and produces valid HTML

---

## Composition

All four features feed the HTML report:

```
regula check --format html --framework nist-ai-rmf .
```

1. Classification runs → findings with article refs
2. `framework_mapper` adds NIST cross-refs to each finding
3. `model_inventory` scans and appends model list
4. `generate_html_report()` renders everything into one file

Each feature is independently usable (CLI flags are optional). The HTML report degrades gracefully if inventory or framework data is absent.

---

## Files Changed

| File | Change |
|------|--------|
| `scripts/model_inventory.py` | New — model detection engine + CLI |
| `scripts/code_analysis.py` | Expand ARCHITECTURE_PATTERNS 12 → 28 |
| `scripts/risk_patterns.py` | Expand AI_INDICATORS.libraries |
| `scripts/compliance_check.py` | Add optional `frameworks` param, wire framework_mapper |
| `scripts/cli.py` | Add `inventory` subcommand, `--framework` flag, `-o` flag, `--format html` |
| `scripts/pdf_export.py` | Add `generate_html_report()` |
| `tests/test_classification.py` | Tests for all four features |

---

## What This Does Not Do

- **Call-chain tracing**: Regula still detects patterns, not data flow. It cannot trace how an AI output variable propagates through function calls.
- **Live model registry**: The model inventory is static analysis. It does not know if a model is actually deployed or what version is in production.
- **Multi-user dashboard**: The HTML report is a static file. No auth, no persistence, no team collaboration.
- **Runtime monitoring**: All analysis is at scan time. No hooks into running systems.

These are honest limits, stated in the report's Methodology section.
