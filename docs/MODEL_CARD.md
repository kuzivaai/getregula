# Model Card — Regula Detection Engine

Regula's detection engine is a static analysis system that reports source-code indicators associated with EU AI Act risk categories. It does not determine legal classification. This document treats it as an AI system and documents its capabilities, limitations, and biases. To generate a model card scaffold for your own project, run `regula model-card --project /path/to/project`.

---

## System Overview

| Field | Value |
|---|---|
| Name | Regula Detection Engine |
| Version | 2.0.0 (this doc updated 2026-08-19) |
| Type | Rule-based detector plus a separate evidence-gated legal decision kernel |
| Training data | None — not a machine learning model |
| Detection patterns | 419 tiered risk regexes across 57 categories (10 prohibited + 18 high-risk + 4 limited-risk + 17 AI security + 2 bias + 6 governance observations) + 17 GPAI training regexes. Includes housing (Colorado SB 26-189), transportation (Korea AI Basic Act Art 33), and emotion inference split categories. Regenerate with `python3 scripts/site_facts.py`. |
| Languages supported | Python, JavaScript, TypeScript, Java, Go, Rust, C, C++ |
| Compliance frameworks | 13 with full crosswalk data (EU AI Act, NIST AI RMF, ISO 42001, NIST CSF, SOC 2, ISO 27001, OWASP LLM Top 10, OWASP Agentic (ASI), MITRE ATLAS, EU CRA, LGPD, Marco Legal IA, UK ICO) |
| Dependencies | Zero runtime (Python 3.10+ stdlib only); `regula[signing]` extra adds `cryptography` + `asn1crypto` for optional Ed25519 + RFC 3161 manifest signing. |

---

## Intended Use

**Primary use case:** Find code patterns that merit regulatory review, then
evaluate separately sourced deployment and operator facts through the decision
kernel for the EU AI Act, South Korea AI Basic Act, and Colorado SB26-189.
Generated compliance documents are unverified scaffolds until the kernel has a
resolved evidence path for the relevant obligation.

**Intended users:**

- Developers building AI-powered applications that may be deployed in or affect the EU market
- Small teams (1-20 people) who cannot afford enterprise governance SaaS
- Compliance officers who need a technical evidence base for governance programmes
- Auditors who need a starting point for code-level compliance assessment

**Deployment context:** Local CLI tool. Core scan paths are designed for local execution without an account or API key. Optional timestamping, configured telemetry, update/feed paths, and other explicitly network-enabled features are outside that boundary.

---

## Known Limitations

### Decision meaning and evidence contract

Decision model `2026-08-19.1` is stored in
`references/decision_model.v1.json`. A decision-critical fact has one or more
sourced values, each with `yes`, `no`, `unknown`, or `not_applicable` state,
provenance, jurisdiction, and timestamp. Absence, explicit unknown, no, and
not applicable remain distinct. Conflicting sourced values remain
contradictory rather than being averaged.

The kernel emits a tagged result:

- `indication` means every necessary classification predicate has a sourced
  satisfied path. An obligation is attached only when its own role and rule
  edges are also resolved.
- `insufficient_information` lists the unresolved facts, the predicates each
  fact would resolve, and their provisions. The list is ordered by resolution
  count.
- `outside_scope_candidate` requires a resolved false scope path or resolved
  false paths through all applicable named rules. Missing facts cannot create
  this result.

`evidence_completeness` and `rule_resolution` report different properties.
Detector priority is a ranking of findings, not a probability that a legal
classification is correct. No correctness probability is emitted because the
project has no representative labelled legal-outcome corpus with which to
calibrate one.

The Python and browser runtimes consume the same declarative model. A generated
conformance corpus exercises Python, REST, browser, MCP, and editor adapters.
Mutation controls alter each predicate and obligation edge and require a
semantic vector to fail.

The machine-readable predicates, applicability dates and unresolved conditions
are recorded in `references/decision_model.v1.json`; the conformance manifest is
`references/decision_conformance.v1.json`, with integrity-bound cases in the
adjacent `references/decision_conformance.v1/` shards. Sharding keeps every
generated file within the repository privacy gate's complete-scan bound. These
are implementation records, not authoritative legal interpretation.

Current limitations of the decision model are material:

- code-detector matches are observations and are never promoted to legal facts;
- the Article 50(4) artistic-work fact changes disclosure manner, which the
  current obligation schema does not yet express;
- EU Article 25 role conversion must currently arrive as sourced
  `role_provider=yes`, rather than being derived by a dedicated predicate;
- Korea Article 32 and Article 36 decree thresholds remain sourced input facts
  because this review did not establish their numeric values from the official
  delegated instruments;
- combined Colorado exclusion facts place the enumeration burden on the fact
  provider; and
- application dates are reported on indications and obligations, but the
  kernel does not claim implementation readiness or calculate a deadline.

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

Published benchmark against 50 randomly selected Python AI repos (from 276 candidates, random seed 42), **N=115**, blind-labelled by a **single reviewer** with no inter-rater agreement measurement (labeller saw only file path, code context, and finding description; see [`benchmarks/README.md`](../benchmarks/README.md)). Production code only (default `--skip-tests` settings):

| Tier | TP | FP | Precision |
|---|---:|---:|---:|
| `minimal_risk` | 11 | 0 | 100.0% |
| `limited_risk` | 7 | 1 | 87.5% |
| `ai_security` | 41 | 7 | 85.4% |
| `agent_autonomy` | 34 | 7 | 82.9% |
| `high_risk` | 2 | 4 | 33.3% |
| **Overall** | **96** | **19** | **83.5%** |
Source: [`benchmarks/README.md`](../benchmarks/README.md). N=115, single reviewer, no inter-rater agreement measurement.

**Improvement from v1.7.4:** Domain-gated high-risk findings, LLM import
gating, and justice opt-in reduced FP from 42 to 19 on the same labelled
corpus, improving production precision from 70.0% to 83.5%. 3 borderline
ai_security TPs were lost (LLM02 findings in files without LLM library imports).
Both figures are from the same N=115 corpus recorded in [`benchmarks/README.md`](../benchmarks/README.md).

The `high_risk` tier (33%) remains weakest — 6 subcategories (`critical_infrastructure`,
`safety_components`, `worker_management`, `democratic_processes`, `justice`,
`essential_services`) now require `--domain` declaration or import fingerprinting to fire. Including test
code drops overall precision to 60.6%. Both figures are recorded in [`benchmarks/README.md`](../benchmarks/README.md); note that 33% rests on N=6 and is not statistically meaningful at that sample size.

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

38 hand-crafted Python files (`benchmarks/synthetic/manifest.json`, version 2.0):
- 5 Article 5 prohibited practices (social scoring, subliminal manipulation, real-time biometric identification, emotion inference in workplaces, vulnerability exploitation)
- 30 Annex III high-risk categories
- 3 negative cases (non-AI code that should not be flagged)

**Recall depends on the code path and the gate condition, so a bare fraction is not a measurement.** Every figure below is regenerated from `benchmarks/synthetic/RECALL.json` by `tests/test_recall_artefact.py`, and a fixture counts as recalled when the highest tier detected equals the tier the manifest expects.

| Path and gate condition | High-risk | Prohibited |
|---|---:|---:|
| scanner, default scan, no flags | 10/30 = 33.3% | 5/5 |
| scanner, all eight domains declared | 16/30 = 53.3% | 5/5 |
| scanner, domains declared + AI-library import present | 23/30 = 76.7% | 5/5 |
| classifier (`report.scan_files`), all domains declared | 16/30 = 53.3% | 5/5 |
Source: `benchmarks/synthetic/RECALL.json`, produced from an actual run by `scripts/build_recall_artefact.py`.

**Corrected 29 July 2026.** This section previously described a 13-file corpus and reported **100% precision, 100% recall**. The corpus was expanded to 38 fixtures (high-risk 5 to 30) and the claim was never re-measured against it. The withdrawn figures are recorded here rather than deleted; the measured replacements are in the table above, from `benchmarks/synthetic/RECALL.json`. **Corrected again 29 July 2026.** The decomposition published here until today read "13 suppressed by opt-in domain gating, 4 by the AI-indicator gate, and 3 are genuine pattern gaps, so 17 of 20 misses are gate behaviour". Every component of that was wrong, and it understated the pattern-side weakness by more than double. It was carried over from an earlier recall table whose two lower rows are marked NOT REPRODUCIBLE in `benchmarks/headtohead/RESULTS-synthetic-v2-2026-07-28.md`. Derived from the per-fixture `missed` lists in `benchmarks/synthetic/RECALL.json` by set difference across the three scanner conditions: of the 20 high-risk fixtures missed on a default scan, **6 are recovered by declaring the opt-in domains, a further 7 by also having an AI-library import present, and 7 are never recovered under any measured condition**. So **13 of 20 misses are gate behaviour and 7 are pattern-side exposure**. Regenerated and asserted by `tests/test_recall_decomposition.py`, which recomputes the three numbers from the artefact and fails if this paragraph disagrees.

### Curated library corpus (development baseline)

257 findings hand-labelled across 5 mature open-source AI libraries (instructor, pydantic-ai, langchain, scikit-learn, openai-python). Each finding manually classified as TP or FP. Labels committed at `benchmarks/labels.json`. This corpus was used during development to tune patterns and is **not** the headline precision number — library code is mostly infrastructure, producing 15.2% precision at the `minimal_risk` tier.

### Random corpus (headline precision measurement)

50 randomly selected Python AI repos (from 276 candidates, seed=42), scanned with Regula v1.7.0. 201 findings stratified-sampled and blind-labelled by a **single reviewer** (labeller saw only file path, code context, and finding description — no project name, README, or purpose, see `benchmarks/labels.json`).

**Result:** 83.5% precision on production code (N=115, measured on Regula v1.7.0). **Labelled by one reviewer; no inter-rater agreement measurement exists.** Previous baseline was 70.0% before domain gating and LLM import gating. Figures re-measured per release where corpus permits; v1.7.1+ additions not yet reflected. Full methodology: `benchmarks/results/random_corpus/METHODOLOGY.json`; labelling limits: [`benchmarks/README.md`](../benchmarks/README.md) (the only repo-wide disclosure of the single-reviewer basis).

### Continuous validation

- 2,897 pytest-collected tests, produced by collection rather than
  hand-maintained (measured 2026-08-25). See
  [`data/published_count_manifest.json`](../data/published_count_manifest.json).
- 48 CLI integration tests (`tests/test_cli_integration.py`), enumerated by
  `data/site_facts.json`.
- 6 self-test assertions (`regula self-test`)
- 12 health checks (`regula doctor`)
- CI runs on every push across Python 3.10, 3.11, 3.12, 3.13

---

## Versioning

This model card describes Regula v2.0.0. If the detection patterns, classification logic, or evaluation methodology change, this document should be updated in the same commit.

---

*Last updated: 12 August 2026.*
