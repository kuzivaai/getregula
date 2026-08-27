# Model Card — Regula Detection Engine

Regula's detection engine is a static analysis system that reports source-code
indicators associated with AI-governance review. A separate decision kernel
evaluates explicitly declared facts for three implemented jurisdictions. It
does not determine legal classification or compliance. This document treats
the detector and kernel as an automated decision-support system and documents
their capabilities, limitations, and biases. To generate a model card scaffold
for your own project, run `regula model-card --project /path/to/project`.

---

## System Overview

| Field | Value |
|---|---|
| Name | Regula Detection Engine |
| Version | 2.0.0 (this doc updated 2026-08-26) |
| Type | Rule-based detector plus a separate evidence-gated legal decision kernel |
| Training data | None — not a machine learning model |
| Detection patterns | 423 tiered risk regexes across 57 categories (10 prohibited + 18 high-risk + 4 limited-risk + 17 AI security + 2 bias + 6 governance observations) + 17 GPAI training regexes. Includes housing (Colorado SB 26-189), transportation (Korea AI Basic Act Art 33), and emotion inference split categories. Regenerate with `python3 scripts/site_facts.py`. |
| Languages supported | Python, JavaScript, TypeScript, Java, Go, Rust, C, C++ |
| Framework references | 13 identifiers with selected crosswalk data (EU AI Act, NIST AI RMF, ISO 42001, NIST CSF, SOC 2, ISO 27001, OWASP LLM Top 10, OWASP Agentic (ASI), MITRE ATLAS, EU CRA, LGPD, pending Marco Legal IA, UK ICO/DSIT). A mapping does not test applicability, control implementation, equivalence, or conformity. |
| Dependencies | Zero runtime (Python 3.10+ stdlib only); `regula[signing]` extra adds `cryptography` + `asn1crypto` for optional Ed25519 + RFC 3161 manifest signing. |

---

## Intended Use

**Primary use case:** Find code patterns that merit regulatory review, then
evaluate separately sourced deployment and operator facts through the decision
kernel for the EU AI Act, South Korea AI Basic Act, and Colorado SB26-189.
Generated compliance documents are unverified scaffolds until the kernel has a
resolved evidence path for the relevant obligation.

**Intended users and tasks:**

- Builders and maintainers locating source-code signals that warrant review.
- Governance and assurance reviewers combining observations with sourced
  deployment and operator facts while preserving unknowns and contradictions.
- Evaluators testing Regula on a representative local sample before adoption
  or CI enforcement.
- Qualified legal, data-protection, security, accessibility, and domain
  reviewers using Regula artefacts as inputs, not as Regula-authored opinions.

The task journeys, failure paths, and three capability levels are defined in
[`PRODUCT_COVERAGE_AND_JOURNEYS.md`](PRODUCT_COVERAGE_AND_JOURNEYS.md).

**Deployment context:** Local CLI tool. Core scan paths are designed for local execution without an account or API key. Optional timestamping, configured telemetry, update/feed paths, and other explicitly network-enabled features are outside that boundary.

---

## Known Limitations

### Decision meaning and evidence contract

Decision model `2026-08-26.1` is stored in
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
- Korea Article 32's three conjunctive Decree Article 24 criteria and Article
  36's four disjunctive Decree Article 29 scale criteria are separate sourced
  input facts; Regula does not infer current frontier status, revenue, user
  counts, or enforcement history from code;
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
| Python | Most developed | Most rules and the available labelled development records are Python-focused; current real-world recall is unknown. |
| JavaScript/TypeScript | Intermediate | Recognises common frameworks and has an optional syntax-aware path; current real-world precision and recall are unknown. |
| Java | Limited | Recognises selected framework imports and patterns; detector validity is unmeasured. |
| Go | Limited | Recognises selected library imports and patterns; detector validity is unmeasured. |
| Rust | Limited | Recognises selected library imports and patterns; detector validity is unmeasured. |
| C/C++ | Limited | Recognises selected library imports and patterns; detector validity is unmeasured. |

A Python project will receive more granular findings than an equivalent Rust project. This is a known bias in the pattern set, not a language limitation.

### Retired v1.7.0 precision record

Regula has no current independent real-world precision estimate. The table
below preserves a dated v1.7.0 record rather than presenting it as a baseline
for v2.0.0. It used 50 randomly selected Python AI repositories (from 276
candidates, seed 42), an N=115 production subset, and one blind reviewer with
no inter-rater agreement measurement. The measured subset and pinned source
snapshots were not preserved, so the result cannot be re-derived from a clean
checkout. See [`benchmarks/README.md`](../benchmarks/README.md).

| Tier | TP | FP | Precision |
|---|---:|---:|---:|
| `minimal_risk` | 11 | 0 | 100.0% |
| `limited_risk` | 7 | 1 | 87.5% |
| `ai_security` | 41 | 7 | 85.4% |
| `agent_autonomy` | 34 | 7 | 82.9% |
| `high_risk` | 2 | 4 | 33.3% |
| **Overall** | **96** | **19** | **83.5%** |
Source: [`benchmarks/README.md`](../benchmarks/README.md). N=115, single reviewer, no inter-rater agreement measurement.

Within that v1.7.0 analysis, domain-gated high-risk findings, LLM import
gating, and justice opt-in changed the recorded false-positive count from 42
to 19 and lost three borderline `ai_security` true-positive labels. This is a
historical within-corpus comparison, not evidence about v2.0.0.

The `high_risk` tier (33%) remains weakest — 6 subcategories (`critical_infrastructure`,
`safety_components`, `worker_management`, `democratic_processes`, `justice`,
`essential_services`) now require `--domain` declaration or import fingerprinting to fire. Including test
code drops overall precision to 60.6%. Both figures are recorded in [`benchmarks/README.md`](../benchmarks/README.md); note that 33% rests on N=6 and is not statistically meaningful at that sample size.

Available methodology and the reproducibility gap: `benchmarks/README.md`.
The 26 August pinned external diagnostic, including all retained failures and
the no-accuracy-claim boundary, is
[`EXTERNAL_DIAGNOSTIC_2026-08-26.md`](EXTERNAL_DIAGNOSTIC_2026-08-26.md).

---

## Bias Risks

### Systematic over-flagging

- **AI library and infrastructure code:** Imports, prompts, tool execution, and
  security terminology can appear in libraries and developer infrastructure
  without implementing the regulated intended purpose suggested by a pattern.
  The pinned external corpus exercises this failure mode, but its diagnostic
  assertions are not independently adjudicated false-positive labels.
- **Employment-related keywords:** Patterns for Annex III Category 4 (employment) match on keywords like `hiring`, `applicant`, `candidate`. HR software that is not an AI system may be flagged.

### Systematic under-flagging

- **Non-English code:** Pattern matching is English-centric. Variable names, comments, and identifiers in other languages will not match patterns expecting English keywords like `face_recognition` or `credit_score`.
- **Abstracted architectures:** Code that wraps AI operations behind generic interfaces (e.g., `service.process(request)`) will not be detected. The patterns expect explicit AI library usage.
- **Uncommon languages:** Go, Rust, C, and C++ have fewer patterns than Python. AI applications in these languages will systematically receive fewer findings.

Calling systematic over-flagging “by design” would not make it harmless. Even
when a broad signal is intentional, the review burden and misleading
implication must be measured and reduced without hiding relevant observations.

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

### Synthetic corpus (path-specific label fidelity)

38 hand-crafted Python files (`benchmarks/synthetic/manifest.json`, version 2.0):
- 5 Article 5 prohibited practices (social scoring, subliminal manipulation, real-time biometric identification, emotion inference in workplaces, vulnerability exploitation)
- 30 Annex III high-risk categories
- 3 negative cases (non-AI code that should not be flagged)

**Recall depends on the code path and the gate condition, so a bare fraction is not a measurement.** Every figure below is regenerated from `benchmarks/synthetic/RECALL.json` by `tests/test_recall_artefact.py`, and a fixture counts as recalled when the highest tier detected equals the tier the manifest expects.

| Path and gate condition | High-risk | Prohibited |
|---|---:|---:|
| context-free core classifier, no project/domain gates (Python and browser JavaScript) | 18/30 = 60.0% | 5/5 |
| scanner, default scan, no flags | 4/30 = 13.3% | 5/5 |
| scanner, all eight domains declared | 16/30 = 53.3% | 5/5 |
| scanner, domains declared + AI-library import present | 23/30 = 76.7% | 5/5 |
| classifier (`report.scan_files`), all domains declared | 16/30 = 53.3% | 5/5 |
Source: `benchmarks/synthetic/RECALL.json`, produced from an actual run by `scripts/build_recall_artefact.py`.

**Corrected 29 July 2026.** This section previously described a 13-file corpus and reported **100% precision, 100% recall**. The corpus was expanded to 38 fixtures (high-risk 5 to 30) and the claim was never re-measured against it. The withdrawn figures are recorded here rather than deleted; the measured replacements are in the table above, from `benchmarks/synthetic/RECALL.json`. **Corrected again 29 July 2026.** The decomposition then published as “17 of 20 misses are gate behaviour” was not supported by the per-fixture artefact and was withdrawn. **Re-measured 26 August 2026 after the finance subcategories were brought under their intended opt-in domain gate and broad biometric matches were narrowed:** of the 26 high-risk fixtures missed by the default CLI, **12 are recovered by declaring the opt-in domains, a further 7 by also having an AI-library import present, and 7 are never recovered under any measured condition**. Thus **19 of 26 misses are gate behaviour and 7 are pattern-side exposure**. The context-free Python/browser classifier is reported separately because it has no project-policy, fingerprint or domain-gating layer. `tests/test_recall_decomposition.py` recomputes the three scanner-path numbers and fails if this paragraph disagrees.

### Curated library corpus (development baseline)

257 findings hand-labelled across 5 mature open-source AI libraries (instructor, pydantic-ai, langchain, scikit-learn, openai-python). Each finding manually classified as TP or FP. Labels committed at `benchmarks/labels.json`. This corpus was used during development to tune patterns and is **not** the headline precision number — library code is mostly infrastructure, producing 15.2% precision at the `minimal_risk` tier.

### Random corpus (retired dated measurement)

50 randomly selected Python AI repos (from 276 candidates, seed=42), scanned with Regula v1.7.0. 201 findings stratified-sampled and blind-labelled by a **single reviewer** (labeller saw only file path, code context, and finding description — no project name, README, or purpose, see `benchmarks/labels.json`).

**Recorded result:** 83.5% precision on the N=115 production subset for
Regula v1.7.0. One reviewer supplied the labels and no inter-rater agreement
measurement exists. The subset membership and pinned repository snapshots are
not tracked, so this is neither re-runnable nor evidence of current detector
accuracy. Full available methodology:
`benchmarks/results/random_corpus/METHODOLOGY.json`; limitations:
[`benchmarks/README.md`](../benchmarks/README.md).

### Continuous validation

- 2,922 pytest-collected tests, produced by collection rather than
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

*Last updated: 26 August 2026.*
