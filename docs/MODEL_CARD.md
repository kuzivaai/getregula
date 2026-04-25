# Model Card — Regula Detection Engine

Regula's detection engine is a static analysis system that classifies source code against EU AI Act risk tiers. This document treats it as an AI system and documents its capabilities, limitations, and biases. To generate a model card scaffold for your own project, run `regula model-card --project /path/to/project`.

---

## System Overview

| Field | Value |
|---|---|
| Name | Regula Detection Engine |
| Version | 1.7.0 (this doc generated 2026-04-16) |
| Type | Rule-based static analysis (regex + AST pattern matching) |
| Training data | None — not a machine learning model |
| Detection patterns | 389 tiered risk regexes across 52 categories (8 prohibited + 15 high-risk + 4 limited-risk + 17 AI security + 2 bias + 6 governance observations) + 17 GPAI training regexes. Regenerate with `python3 scripts/site_facts.py`. |
| Languages supported | Python, JavaScript, TypeScript, Java, Go, Rust, C, C++ |
| Compliance frameworks | 12 with full crosswalk data (EU AI Act, NIST AI RMF, ISO 42001, NIST CSF, SOC 2, ISO 27001, OWASP LLM Top 10, MITRE ATLAS, EU CRA, LGPD, Marco Legal IA, UK ICO) |
| Dependencies | Zero runtime (Python 3.10+ stdlib only); `regula[signing]` extra adds `cryptography` + `asn1crypto` for optional Ed25519 + RFC 3161 manifest signing. |

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

Published benchmark against 50 randomly selected Python AI repos (from 276 candidates, random seed 42), blind-labelled (labeller saw only file path, code context, and finding description). Production code only (default `--skip-tests` settings):

| Tier | TP | FP | Precision |
|---|---:|---:|---:|
| `minimal_risk` | 11 | 0 | 100.0% |
| `limited_risk` | 7 | 1 | 87.5% |
| `ai_security` | 41 | 7 | 85.4% |
| `agent_autonomy` | 34 | 7 | 82.9% |
| `high_risk` | 2 | 4 | 33.3% |
| **Overall** | **96** | **19** | **83.5%** |

**Improvement from v1.7.0:** Domain-gated high-risk findings, LLM import
gating, and justice opt-in reduced FP from 42 to 19 on the same labelled
corpus, improving production precision from 70.0% to 83.5%. 3 borderline
ai_security TPs were lost (LLM02 findings in files without LLM library imports).

The `high_risk` tier (33%) remains weakest — 6 subcategories (`critical_infrastructure`,
`safety_components`, `worker_management`, `democratic_processes`, `justice`,
`essential_services`) now require `--domain` declaration or import fingerprinting to fire. Including test
code drops overall precision to 60.6%.

Full methodology and reproduction steps: `benchmarks/README.md`

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

**Result:** 83.5% precision on production code from random corpus (blind-labelled, N=115); 0 false positives at BLOCK tier. Previous baseline was 70.0% before domain gating and LLM import gating.

### Continuous validation

- 1232 pytest-collected tests (1111 `def test_*` functions; delta is pytest parametrisation)
- 11 CLI integration tests
- 6 self-test assertions (`regula self-test`)
- 10 health checks (`regula doctor`)
- CI runs on every push across Python 3.10, 3.11, 3.12, 3.13

---

## Versioning

This model card describes Regula v1.7.0. If the detection patterns, classification logic, or evaluation methodology change, this document should be updated in the same commit.

---

*Last updated: 10 April 2026.*
