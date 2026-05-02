# Regula v1.8+ Enhancement Design Spec

**Date:** 2026-04-18
**Status:** Draft — pending user review
**Research basis:** 14 parallel research agents, 5 verification passes, 30+ primary sources verified

---

## Executive Summary

Competitive analysis of 12 EU AI Act compliance tools (VerifyWise, EuConform, AIR Blackbox, ArkForge MCP, COMPL-AI, Practical AI Act, Trusera ai-bom, and others) validated against Regula's codebase reveals:

- **Regula has the deepest code-level scanning in this space** (389 patterns / 46 categories / 8 languages / 12 framework crosswalks). No competitor matches this.
- **Direct competitors are tiny**: ArkForge (4 stars, 1,293 PyPI/month), AIR Blackbox (13 stars, 1,642/month), EuConform (110 stars, single contributor). Window is open.
- **Several competitor claims are inflated**: AIR Blackbox's "ML-DSA-65 quantum-safe signing" is not implemented. ArkForge's "Trust Layer" proxies through httpbin.org. AIR Blackbox's bias scanner and AI-BOM generator are stubs.
- **Regula's downloads are 192/week (459/month)** — 6.6x higher than the stale 29/week figure.

The plan adds features across three phases, each delivering standalone value:

1. **Sharpen the Output** — precision improvement, evidence bundles, doc scoring, open questions
2. **Widen the Moat** — GDPR dual-compliance, AI BOM, compliance roadmap, lifecycle tagging
3. **Build the Ecosystem** — VS Code extension, community rules, REST API

---

## Competitive Ground Truth (Verified 2026-04-18)

### GitHub Stats (all verified via `gh api`)

| Tool | Stars | Forks | Contributors | License | Created |
|------|-------|-------|-------------|---------|---------|
| VerifyWise | 259 | 101 | 30 | BSL 1.1 (not OSS) | 2024-08-18 |
| EuConform | 110 | 5 | 2 (1 human) | MIT + EUPL-1.2 | 2025-12-16 |
| COMPL-AI | 187 | 32 | 10 | Apache-2.0 | 2024-10-07 |
| Practical AI Act | 20 | 0 | 5 | Apache-2.0 | 2025-01-02 |
| AIR Blackbox | 13 | 2 | 3 | Apache-2.0 | 2026-02-14 |
| ArkForge MCP | 4 | 1 | 1 | MIT | 2026-02-16 |

### PyPI Downloads (verified via pypistats.org)

| Package | Monthly | Weekly |
|---------|---------|--------|
| regula-ai | 459 | 192 |
| air-blackbox (v1.12.0) | 1,642 | 605 |
| eu-ai-act-scanner (v2.0.15) | 1,293 | 878 |
| ai-bom (Trusera, v3.6.0) | 12,570 (unverified) | 3,663 |
| asqav (v0.2.15) | 1,047 | 707 |

### Competitor Code Reality (verified against actual repos)

| Claim | Verdict | Evidence |
|-------|---------|----------|
| AIR Blackbox ML-DSA-65 quantum-safe signing | **NOT IMPLEMENTED** | Zero quantum code/deps in repo. Only HMAC-SHA256 + Ed25519 exist. |
| AIR Blackbox bias scanner | **EMPTY STUB** | `scan_for_bias()` returns `[]` with "Placeholder" comment |
| AIR Blackbox AI-BOM generator | **MANUAL ONLY** | Has add/validate/report methods but no automated scanning |
| AIR Blackbox HMAC-SHA256 chains | **REAL** | Full impl in Python + Go |
| ArkForge Trust Layer | **PROXIES THROUGH httpbin.org** | Line 2987: `"url": "https://httpbin.org/post"` |
| ArkForge code scanning | **PARTIAL** | Scans imports for 16+ frameworks; compliance assessment is doc-existence based |
| ArkForge email harvesting | **VERIFIED** | MCP instructions: "MANDATORY POST-SCAN FLOW" with email funnel |
| EuConform evidence format | **VERIFIED** | 4 JSON schemas (aibom, bundle, ci, report) |
| EuConform single contributor | **VERIFIED** | 1 human (52 commits) + 1 bot |

---

## What Regula Has That No Competitor Matches

Verified against codebase:

- **389 regexes across 46 risk pattern categories** (vs EuConform ~30, AIR Blackbox ~13, ArkForge 0)
- **8 language families with AST for Python/JS/TS** (vs EuConform JS/TS only, AIR Blackbox Python only)
- **12 compliance framework crosswalks** (vs AIR Blackbox 4, VerifyWise 4, ArkForge 0)
- **CrowS-Pairs + BBQ bias benchmarks with Wilson CIs** (vs AIR Blackbox stub, ArkForge none)
- **Zero production dependencies** (vs AIR Blackbox 4+, ArkForge 1, VerifyWise PostgreSQL+Redis+Node)
- **Ed25519 signing already implemented** (`scripts/signing.py`, optional via `regula[signing]`)
- **CycloneDX 1.7 SBOM already implemented** (`scripts/sbom.py`)
- **1,055 tests all passing** (vs AIR Blackbox ~40, ArkForge ~15)
- **Published precision baseline** (15.2% on OSS, 100% on synthetic — honest, not inflated)

---

## Phase 1: Sharpen the Output

### 1.1 Precision Improvement

**Goal:** Improve real-world precision from 15.2% toward 40%+.

**Features:**
- **File provenance classification**: Classify files as production/test/example/generated/documentation/tooling. Production files get full confidence; test/example/generated get reduced confidence or are filtered.
- **`--scope production` flag**: Filter to production files only (inspired by EuConform's `--scope production`).
- **Pattern confidence tuning**: Suppress low-confidence findings by default. Show only with `--verbose` or `--min-confidence 0`.
- **Open questions**: Findings with confidence < 60% tagged as `open_question: true`. Displayed in separate "Questions for Human Review" section. In SARIF: `"level": "note"` instead of `"warning"`.

**Validation:** Every DevSecOps study confirms false positive fatigue is the #1 reason developers abandon scanners (sources: Semgrep blog, Snyk user feedback, 202-developer adoption study). Regula's 15.2% precision means ~5/6 findings are FPs.

**Effort:** Low-medium. File classification heuristics + plumbing through scan pipeline.

### 1.2 Self-Verifying Evidence Bundle

**What:** Package existing evidence pack into a `.regula-evidence.zip` with embedded `verify.py`.

**How:**
- Wraps existing 7-file evidence pack in `zipfile` (stdlib)
- Includes standalone `verify.py` (~50 lines, stdlib-only) that checks all SHA-256 hashes
- If `regula[signing]` installed: includes Ed25519 signature in manifest
- Metadata: Regula version, scan timestamp, target path, git commit hash
- CLI: `regula evidence-pack --bundle`

**Standards alignment:** ISO 42001 expects documented evidence of controls operating. NIST AI RMF Govern function calls for embedding governance in SDLC. Evidence bundles serve both.

**Competitive gap:** EuConform has bundle verification (JS/TS only). AIR Blackbox has `.air-evidence` ZIPs (13 regex checks). ArkForge's evidence is behind €99/month paywall. Regula: deep scanning + self-verifying bundles + Ed25519 signing, free.

**Effort:** Low.

### 1.3 Document Quality Scoring (`regula doc-audit`)

**What:** Score compliance documents 0-100 based on coverage, depth, and structure per EU AI Act article.

**Scoring model (inspired by DoXpert's validated three-score approach):**
- **Coverage (0-40):** Required sections present for the applicable article
- **Depth (0-40):** Word count per section, specific terms, standards references
- **Structure (0-20):** Headings, version/date, author/owner

**Article-specific section checklists (from Annex IV requirements):**
- Art. 9 (risk management): hazard identification, residual risk log, testing strategy, mitigation measures
- Art. 10 (data governance): training data description, data quality measures, bias examination
- Art. 11 (technical documentation): system description, design specifications, development process
- Art. 12 (record-keeping): logging capability, data retention policy, audit trail
- Art. 13 (transparency): user instructions, capability limitations, human oversight instructions
- Art. 14 (human oversight): oversight measures, human-machine interface, intervention capability
- Art. 15 (robustness): accuracy metrics, error handling, cybersecurity measures

**Output:** Table showing doc name, article, score (0-100), specific gaps. Supports `--format json`.

**Validation:** Springer EMSE paper (Sovrano et al., 2025) validated that documentation depth scoring has "moderate and statistically significant correlation" with expert legal judgments. Stanford AILCCP (April 2026) expects "evidence artefacts and measurable metrics" at each lifecycle phase.

**Honest limitation:** This scores structural completeness and keyword presence, not semantic adequacy. A doc with the right headings but nonsense content would score well. This should be clearly documented.

**Effort:** Medium.

---

## Phase 2: Widen the Moat

### 2.1 GDPR Dual-Compliance Patterns

**Articles covered (revised after GDPR verification):**
- Art. 5(1)(c) — data minimisation (excessive data collection to AI models)
- Art. 5(1)(f) — integrity/confidentiality (unencrypted PII, plaintext logging)
- Art. 7 — consent (user data to ML training without consent gate)
- Art. 9 — special category data (biometric, health, racial data in AI features)
- Art. 13/14 — transparency (absence of privacy notice/AI disclosure in user-facing code)
- Art. 17 — right to erasure (user data in vector stores without deletion capability)
- Art. 22 — automated decision-making (AI output driving decisions without human review) — **observation-level confidence only**
- Art. 25 — privacy by design (PII handling without validation/sanitisation)
- Art. 32 — security of processing (missing encryption, unvalidated inputs)
- Art. 35 — DPIA triggers (high-risk processing patterns)
- Art. 44-49 — cross-border transfers (data to non-EU API endpoints) — **low-confidence observation with caveats about env vars, SDK abstractions, adequacy decisions**

**Removed:** Art. 6 (lawful basis is organisational, not code-detectable).

**Dual-compliance hotspots (validated by IAPP, EDPB, DLA Piper):**
1. GDPR Art. 35 DPIA + AI Act Art. 27 FRIA — impact assessment overlap
2. GDPR Art. 22 automated decisions + AI Act Art. 14 human oversight
3. GDPR Art. 9 special categories + AI Act Art. 10 data governance

**All GDPR patterns framed as "indicators that GDPR obligations may apply"** — not violations. Consistent with existing EU AI Act approach. Validated by CNIL developer guide, EDPB Guidelines 4/2019, and IAPP analysis.

**Pattern count:** ~18-25 patterns.

**CLI:** `regula check --include-gdpr` flag + standalone `regula gdpr` command.

**Effort:** Medium.

### 2.2 AI BOM Generation (`regula aibom`)

**Honest positioning:** AI BOM auto-generation from code scanning is NOT novel — Cisco aibom (Feb 2026), Trusera ai-bom, SafeDep xbom, Snyk AI-BOM, and saasvista aibom-scanner all do this. **Regula's differentiator: combining AI BOM + EU AI Act risk classification in one pass.** No other tool does both.

**Component taxonomy (custom, documented as `regula:ai:kind` in CycloneDX properties):**
- inference-provider, ai-framework, vector-store, embedding, orchestration, model-file, runtime
- agent, mcp-server, prompt-template, guardrail, dataset-reference (expanded per Cisco's 24-type taxonomy)

**Output formats:**
- JSON (machine-readable, Regula envelope)
- Markdown (human-readable)
- **CycloneDX v1.6** BOM with ML-BOM components (not v1.7 — v1.6 is the ecosystem standard; every competitor outputs v1.6)

**EU AI Act framing:** The Act does NOT use the term "AI BOM." It requires technical documentation (Annex IV, XI) that an AI BOM helps produce. Framed as "documentation supporting Annex IV/XI requirements," not "required by the EU AI Act."

**Leverages existing code:** `dependency_scan.py` (180+ AI library detection) + `classify_risk.py` findings. The detection foundation already exists.

**Effort:** Medium.

### 2.3 Compliance Roadmap (`regula roadmap`)

**What:** Deadline-aware, effort-weighted, week-by-week action plan from gap analysis.

**Methodology:** Action Priority Matrix (established PMI/MindTools methodology) — `criticality × (1/effort)`, quick wins first.

**Deadlines (verified against EU AI Act Art. 113 + Omnibus status):**

| Obligation | Current legal baseline | Omnibus proposal (not yet law) |
|------------|----------------------|-------------------------------|
| Art. 5 prohibited practices | 2 Feb 2025 (in effect) | Unchanged |
| Art. 4 AI literacy | 2 Feb 2025 (in effect) | Shift to Commission/Member States |
| GPAI obligations (Art. 51-56) | 2 Aug 2025 (in effect) | Unchanged |
| GPAI enforcement powers | 2 Aug 2026 | Unchanged |
| Annex III standalone high-risk | 2 Aug 2026 | 2 Dec 2027 |
| Annex I product-embedded high-risk | 2 Aug 2027 | 2 Aug 2028 |

**Default `--target-date`:** 2 Aug 2026 (legal baseline). Omnibus caveat in output but does not change default.

**4 phases (validated against ISO 42001 implementation methodology):**
1. Quick wins (weeks 1-2): transparency disclosures, AI disclosure in README
2. Documentation (weeks 3-6): risk management, data governance, model cards
3. Technical implementation (weeks 7-10): human oversight gates, logging, monitoring
4. Validation and conformity (weeks 11+): testing, conformity prep

**Existing code:** `remediation_plan.py` already has prioritised tasks, effort estimates (correctly disclaimed as heuristics), deadline awareness. Needs: calendar scheduling, phase bucketing, `--target-date` parameter.

**Competitive gap confirmed:** No free tool generates a week-by-week code-level compliance roadmap. ArkForge's is behind €29/month paywall.

**Effort:** Medium (60% already exists in `remediation_plan.py`).

### 2.4 Lifecycle-Phase Tagging

**Phases (expanded to 6, aligned with ISO 22989 / ISO 5338 / Algoritmekader):**
1. **Plan/Assess** — risk classification, applicability assessment, prohibited practice detection
2. **Design** — architecture decisions, privacy-by-design patterns
3. **Develop** — code patterns, bias testing, documentation gaps
4. **Deploy** — credential exposure, dependency pinning, conformity readiness
5. **Operate & Monitor** — logging, audit trails, human oversight, post-market readiness
6. **Retire** (optional) — data retention, model decommissioning

**Multi-phase tagging:** `lifecycle_phases: ["develop", "deploy"]` list field — ~15-20% of patterns span multiple phases. Single-phase-per-finding would be inaccurate.

**Primary dimension stays article-based:** Lifecycle is additive metadata for context. Auditors work by requirement/article (verified against Annex IV and Annex VII conformity assessment structure). Lifecycle adds value for demonstrating continuous risk management (Art. 9's "throughout the entire lifecycle" requirement).

**Novel:** No existing scanner tags findings by lifecycle phase. Differentiation opportunity.

**Effort:** Low (metadata annotation on existing pattern categories + report grouping).

### 2.5 CEN/CENELEC Harmonised Standards Tracking

**Gap identified during verification.** CEN/CENELEC JTC 21 is developing harmonised standards for the AI Act, including prEN 18286 (quality management system for AI Act regulatory purposes). First publications expected Q4 2026.

**Action:** Add monitoring task. When standards publish, map Regula's patterns and evidence output to them. Any tool claiming AI Act compliance alignment will need this mapping.

**Effort:** Low (tracking only until Q4 2026).

---

## Phase 3: Build the Ecosystem

### 3.1 VS Code Extension

**Architecture:** Thin TypeScript wrapper calling installed `regula` CLI. No bundled Python runtime.

**Features:**
- Diagnostics mapped from tier (prohibited → Error, high-risk → Warning, limited → Info, observation → Hint)
- Hover: EU AI Act article, confidence, one-line remediation
- Code Actions: suppress (`# regula-ignore`), accept risk (`# regula-accept`), view article
- Status bar: scan summary
- Config: `regula.scanOnSave`, `regula.minTier`, `regula.scope`

**Validated by:** DevSecOps research ("IDE integration is a prerequisite for adoption" — Checkmarx). No EU AI Act tool currently has a VS Code extension.

**Effort:** High (TypeScript/VS Code extension development, marketplace publishing).

### 3.2 Community Rule Registry

**Rule format:** YAML with pattern definition, metadata, and mandatory test cases (at least 1 true positive + 1 true negative per pattern, following Semgrep's model).

**Infrastructure:** GitHub repo with CI validation. Not a SaaS platform.

**Design constraint:** Community rules are additive. Regula ships complete out of the box.

**Rule language:** YAML + regex (not Rego — learning curve, not Python — security concerns with arbitrary code execution). Accessible to developers who don't know Regula's internals.

**Effort:** Medium-high (YAML loader, test runner, registry infrastructure).

### 3.3 REST API (`regula serve`)

**Architecture:** stdlib `http.server`, stateless request/response, optional `--token` auth.

**Endpoints:** `POST /check`, `POST /classify`, `POST /gap`, `GET /health`.

**Build when:** An enterprise user or integration partner explicitly asks for it.

**Effort:** Medium.

---

## Standards Alignment Summary

| Standard/Framework | How plan aligns | Verified against |
|---|---|---|
| ISO 42001 | Evidence bundles (controls evidence), lifecycle tagging (ongoing), doc scoring (documentation requirements) | ISO 42001 Annex A, Deloitte/KPMG guides |
| NIST AI RMF | 12-framework crosswalk (already), roadmap (Govern function), lifecycle (Map function) | NIST AI RMF 1.0, COSAiS concept note |
| Stanford AILCCP (Apr 2026) | Lifecycle-phase tagging maps to their 10-phase model, evidence artefacts requirement | Stanford CodeX publication |
| Partnership on AI (2026) | Documentation templates, agent governance (existing `regula agent`), interoperable reporting | PAI 6 priorities |
| OECD Due Diligence (Feb 2026) | Risk assessment evidence, lifecycle tracking, adverse impact identification | OECD RBC guidance PDF |
| CycloneDX ML-BOM | AI BOM output in v1.6 format | cyclonedx.org, OWASP AIBOM |
| CNIL Developer Guide | GDPR code-level patterns validated against 18-sheet guide | lincnil.github.io |
| EDPB Guidelines 4/2019 | Art. 25 privacy-by-design technical measures | EDPB publication |
| CEN/CENELEC JTC 21 | Tracking task (standards expected Q4 2026) | cencenelec.eu, ai-act-standards.com |

---

## What This Plan Does NOT Include (Deliberate Scope)

- **LLM-based compliance checking**: Conflicts with stdlib-only, offline-first positioning. Watched but not adopted.
- **Web dashboard/platform**: VerifyWise's territory. Regula is CLI-first.
- **Runtime monitoring/proxy**: AIR Blackbox's territory. Regula is static analysis.
- **Model evaluation/benchmarking**: COMPL-AI's territory. Regula scans code, not models.
- **Full ML pipeline reference implementation**: Practical AI Act's territory.
- **Formal verification**: Amazon Bedrock Automated Reasoning approach. Watched for Phase 4+.

---

## Metrics for Success

| Metric | Current | Phase 1 target | Phase 2 target |
|--------|---------|----------------|----------------|
| OSS precision | 15.2% | 40%+ | 50%+ |
| PyPI weekly downloads | 192 | 500+ | 1,000+ |
| GitHub stars | ~0 | 50+ | 200+ |
| Compliance frameworks | 12 | 12 | 13+ (GDPR) |
| Pattern categories | 46 | 46 | 56+ (GDPR) |
| CLI commands | 55 | 58 | 62 |
| Tests passing | 1,055 | 1,100+ | 1,200+ |

---

## Research Methodology

This spec was produced through:
- **14 parallel research agents** covering: Regula codebase audit, VerifyWise, EuConform, AIR Blackbox, ArkForge MCP, COMPL-AI, Practical AI Act, academic tools, latest trends, DevSecOps success patterns, user-centricity, distribution strategy, industry alignment
- **5 verification passes** covering: GitHub stats (8 repos), PyPI downloads (5 packages), regulatory claims (10 claims), DevSecOps revenue/funding (10 claims), competitor code-level claims (10 claims)
- **4 design validation agents** covering: GDPR article selection, AI BOM standards, compliance roadmap dates/methodology, lifecycle-phase alignment
- **3 critical review agents** covering: user-centricity, distribution strategy, industry standards alignment
- **30+ primary sources verified** including EP press releases, NIST publications, ISO standards, OECD guidance, CycloneDX specifications, academic papers

All claims marked with confidence levels. Corrections applied where verification found discrepancies.
