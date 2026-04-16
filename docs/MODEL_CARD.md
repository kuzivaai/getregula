# Model Card — Regula Detection Engine

Regula's detection engine is a static analysis system that classifies source code against EU AI Act risk tiers. This document treats it as an AI system and documents its capabilities, limitations, and biases. To generate a model card scaffold for your own project, run `regula model-card --project /path/to/project`.

---

## System Overview

| Field | Value |
|---|---|
| Name | Regula Detection Engine |
| Version | 1.6.1 |
| Type | Rule-based static analysis (regex + AST pattern matching) |
| Training data | None — not a machine learning model |
| Detection patterns | 330 (historical bucket); 502 (grand total inclusive) |
| Languages supported | Python, JavaScript, TypeScript, Java, Go, Rust, C, C++ |
| Compliance frameworks | 12 (EU AI Act + 11 cross-mapped frameworks) |
| Dependencies | Zero (Python 3.10+ stdlib only) |

---

## Intended Use

**Primary use case:** Scan source code to identify patterns that map to EU AI Act risk classifications. Surface findings for human review. Generate compliance documentation scaffolds.

**Intended users:**

- Developers building AI-powered applications that may be deployed in or affect the EU market
- Small teams (1-20 people) who cannot afford enterprise governance SaaS
- Compliance officers who need a technical evidence base for governance programmes
- Auditors who need a starting point for code-level compliance assessment

**Deployment context:** Local CLI tool. Runs on the developer's machine. No data leaves the machine. No network access required. No account or API key needed.

---

## Known Limitations

### Detection methodology

Regula uses regex pattern matching and lightweight AST analysis. It does not use machine learning, semantic understanding, or data flow analysis beyond import/call tracing.

**What this means in practice:**

- **Regex-only recall:** Regula detects patterns by matching code against regular expressions. If a developer implements a regulated behaviour using non-standard naming or architecture, Regula will not detect it. The system catches common patterns, not novel implementations.
- **No semantic understanding:** Regula cannot determine whether `model.predict(applicant)` is actually making a credit decision or is a test mock. Deployment context determines risk classification — code patterns alone cannot.
- **No cross-file data flow:** While `regula oversight` traces AI output to endpoints across files, the core `regula check` command analyses files independently. A prohibited practice split across multiple files may not be detected.

### Language depth disparity

Not all 8 supported languages are equally well-covered:

| Language | Pattern depth | Notes |
|---|---|---|
| Python | Deep | Most patterns were developed against Python codebases. Highest recall. |
| JavaScript/TypeScript | Moderate | Good coverage for common AI frameworks (TensorFlow.js, OpenAI SDK). |
| Java | Moderate | Covers Spring AI, DL4J, and common ML library imports. |
| Go | Basic | Covers common Go AI library imports. Fewer domain-specific patterns. |
| Rust | Basic | Covers tch-rs, candle, burn. Limited ecosystem coverage. |
| C/C++ | Basic | Covers TensorFlow C API, ONNX Runtime. Limited pattern set. |

A Python project will receive more granular findings than an equivalent Rust project. This is a known bias in the pattern set, not a language limitation.

### Precision baseline

Published benchmark against 5 labelled open-source projects (257 hand-labelled findings):

| Tier | True Positives | False Positives | Precision |
|---|---|---|---|
| BLOCK (>=80) | 0 | 0 | N/A (no findings) |
| WARN (50-79) | 2 | 6 | 25.0% |
| INFO (<50) | 37 | 212 | 14.9% |
| **Overall** | **39** | **218** | **15.2%** |

**Critical context:** The BLOCK tier — the only tier that fails CI builds by default — produced zero false positives. The 15.2% figure applies to INFO-tier findings, which are surfaced for manual review only.

Full methodology and reproduction steps: `docs/benchmarks/PRECISION_RECALL_2026_04.md`

---

## Bias Risks

### Systematic over-flagging

- **AI library imports:** Projects that import AI frameworks (PyTorch, TensorFlow, OpenAI SDK) will receive findings even if they are building developer tools, not regulated AI systems. The OSS benchmark deliberately measures this: 5 AI libraries produced 218 false positives at INFO tier.
- **Employment-related keywords:** Patterns for Annex III Category 4 (employment) match on keywords like `hiring`, `applicant`, `candidate`. HR software that is not an AI system may be flagged.

### Systematic under-flagging

- **Non-English code:** Pattern matching is English-centric. Variable names, comments, and identifiers in other languages will not match patterns expecting English keywords like `face_recognition` or `credit_score`.
- **Abstracted architectures:** Code that wraps AI operations behind generic interfaces (e.g., `service.process(request)`) will not be detected. The patterns expect explicit AI library usage.
- **Uncommon languages:** Go, Rust, C, and C++ have fewer patterns than Python. AI applications in these languages will systematically receive fewer findings.

### What is NOT a bias

- **High false positive rate on AI libraries** is by design. Regula's OSS benchmark corpus consists of AI frameworks, not AI applications. Flagging `import openai` in the OpenAI SDK itself is expected. The tool is designed for application code, not library code.

---

## Out-of-Scope Uses

Regula is explicitly **NOT** intended for:

| Use | Why it's out of scope |
|---|---|
| Legal advice | Regula identifies code patterns, not legal obligations. Deployment context determines classification. Consult a qualified legal professional. |
| Definitive compliance determination | A clean scan does not mean a system is compliant. Compliance requires deployment-context assessment, documentation, and ongoing governance. |
| Runtime monitoring | Regula performs static analysis on source code. It does not intercept, monitor, or evaluate running AI systems. |
| Replacing human review | Every finding requires human judgement about deployment context. Automated pass/fail decisions based solely on Regula output are inappropriate. |
| Auditor certification | Regula generates evidence artefacts (Annex IV docs, conformity packs). These are scaffolds for human review, not certified audit outputs. |

---

## Evaluation Methodology

### Synthetic corpus (recall measurement)

13 hand-crafted Python files covering:
- 5 Article 5 prohibited practices (social scoring, subliminal manipulation, real-time biometric identification, emotion inference in workplaces, vulnerability exploitation)
- 5 Annex III high-risk categories (employment, credit scoring, education, law enforcement, essential services)
- 3 negative cases (non-AI code that should not be flagged)

**Result:** 100% precision, 100% recall. All prohibited and high-risk patterns detected. Zero false positives on negative cases.

### OSS corpus (precision measurement)

257 findings hand-labelled across 5 mature open-source AI projects:
- instructor (structured LLM outputs)
- pydantic-ai (type-safe AI agents)
- langchain (LLM orchestration)
- scikit-learn (classical ML)
- openai-python (OpenAI API client)

Each finding was manually classified as true positive or false positive by the developer. Labels are committed to the repository at `benchmarks/labels.json` and can be independently verified.

**Result:** 15.2% overall precision; 0 false positives at BLOCK tier.

### Continuous validation

- 751 pytest tests
- 11 CLI integration tests
- 6 self-test assertions (`regula self-test`)
- 10 health checks (`regula doctor`)
- CI runs on every push across Python 3.10, 3.11, 3.12, 3.13

---

## Versioning

This model card describes Regula v1.6.1. If the detection patterns, classification logic, or evaluation methodology change, this document should be updated in the same commit.

---

*Last updated: 10 April 2026.*
