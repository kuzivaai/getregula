# Session 16: Precision Improvement Research

**Date:** 15 June 2026
**Scope:** Identify data-backed, evidence-grounded methods to improve Regula's precision
**Constraint:** stdlib-only Python, fully offline, zero runtime dependencies

---

## Current State (Measured, Not Assumed)

| Corpus | TP | FP | Precision | N |
|--------|----|----|-----------|---|
| Targeted high_risk repos | 35 | 4 | 89.7% | 39 |
| Blind subset (mixed tiers) | 18 | 32 | 36.0% | 50 |
| Random production code (existing) | — | — | 83.5% | 115 |
| AI library source code (existing) | — | — | 15.2% | 257 |

---

## Root Cause Analysis: Where Do False Positives Come From?

### Blind Subset (32 FPs, the diagnostically rich corpus)

| Root Cause | Count | % of FPs | Fixable? |
|------------|-------|----------|----------|
| **Test files** flagged as production findings | 13 | 41% | YES — file-path heuristic |
| **Type defs / package __init__** flagged as AI logic | 6 | 19% | YES — file-path + AST heuristic |
| **Utility / infrastructure code** (logging, plumbing) | 4 | 12% | PARTIALLY — file-path heuristic |
| **Wrong Annex III category** (MONAI→law enforcement, CrewAI→biometrics) | 2 | 6% | YES — category-specific signals |
| **Gate-mitigated autonomy** (gate detected but still flagged) | 2 | 6% | YES — honour own gate detection |
| **Vocabulary/context mismatch** (package install ≠ agent autonomy, etc.) | 5 | 16% | PARTIALLY — requires deeper context |

### Targeted Corpus (4 FPs)

All 4 are infrastructure files: 2× setup.py, 1× docs/conf.py, 1× weight_utils.py. All fixable by file-path exclusion.

### The Key Insight

**75% of all FPs (23/32 blind + 4/4 targeted) are detectable by file path alone** — test files, type definitions, utility/infrastructure modules, setup.py, __init__.py, docs/. No new analysis technique needed. A file-path exclusion layer applied BEFORE pattern matching would eliminate them. Independently verified: zero TPs would be wrongly suppressed by this filter.

---

## Precision Improvement Methods — Ranked by Value-Per-Effort

### Tier 1: High Impact, Low Effort, Zero Dependencies (Buildable Now)

#### 1A. File-Path Exclusion Layer
**What:** Before running any pattern, check if the file matches known non-production paths: `*/tests/*`, `test_*.py`, `*_test.py`, `conftest.py`, `setup.py`, `setup.cfg`, `docs/conf.py`, `*/__init__.py` (for minimal_risk only), `*/types/*` or `*_types*.py` (for minimal_risk only).

**Evidence:** 13/32 blind-subset FPs (41%) are test files; 6 are type defs/__init__; 4 are utility/infrastructure. 4/4 targeted FPs are setup/docs/utility files. SonarQube achieves 3.2% FP rate partly through "rules that only trigger when the tool has enough context to be confident" — file-path filtering is the simplest form of this. VERIFIED as vendor self-report — SonarQube blog, Feb 2026 (not independently audited).

**Impact estimate:** Eliminates 27/36 total FPs across both corpora. Precision improvement: blind subset 36.0% → 66.7% (calculated: 18 TP, 9 FP remaining), targeted 89.7% → 100% (calculated: 35 TP, 0 FP remaining). Independently verified: zero TPs suppressed.

**Effort:** S. Pure Python path matching. No new dependencies.

**Risk:** May suppress genuine findings in test files (rare but possible — e.g. hardcoded credentials in tests). Mitigate by exempting credential_exposure tier from test-file suppression.

**Identity compatible:** YES. stdlib-only, offline, deterministic.

#### 1B. Honour Own Gate Detection
**What:** When Regula's agent_autonomy scanner detects "human gate pattern detected nearby," downgrade the finding's confidence or suppress it rather than reporting it at the same severity as ungated autonomy.

**Evidence:** 2/32 blind-subset FPs were cases where Regula itself detected a gate but still flagged the finding. The tool already knows the mitigation exists.

**Impact estimate:** Eliminates 2 FPs. Small count but high-quality improvement — it removes self-contradictory findings.

**Effort:** S. Logic change in the autonomy scanner.

**Identity compatible:** YES.

#### 1C. Category-Specific Signal Strengthening
**What:** For high_risk Annex III findings, require at least 2 corroborating signals before flagging. Currently, a single vocabulary match (e.g. "biometrics" keyword in a vector search tool) can trigger a high_risk finding at low confidence. Require: keyword match + either (a) domain fingerprint match, (b) import of a domain-specific library, or (c) file-path evidence.

**Evidence:** 2/32 blind-subset FPs were wrong-category assignments (MONAI flagged as law_enforcement, CrewAI vector search flagged as biometrics). Both had low confidence (23–60) and no corroborating signal.

**Impact estimate:** Eliminates category-mismatch FPs without reducing TP (true high_risk findings have multiple signals).

**Effort:** M. Requires modifying the high_risk classification logic to require corroboration.

**Identity compatible:** YES.

### Tier 2: Medium Impact, Medium Effort, Still Zero Dependencies

#### 2A. Confidence-Based Suppression Threshold
**What:** Introduce a minimum confidence threshold (e.g. 30) below which findings are reported as "informational" rather than actionable. Currently, findings at confidence 5–23 inflate the FP count.

**Evidence:** In the blind subset, several FPs had confidence scores of 5, 10, 20, 23. The lowest-confidence findings are disproportionately FP. The targeted corpus's FPs all had confidence ≥63 (setup.py/docs/conf.py — file-path issue, not confidence issue), so this primarily helps the mixed-tier corpus.

**Impact estimate:** Would need to measure the confidence→FP correlation across the full 446-entry corpus to set the threshold accurately. Estimated 3–5 additional FP eliminations.

**Effort:** S. Configuration parameter.

**Risk:** May suppress low-confidence TPs. Needs calibration against labelled data.

**Identity compatible:** YES.

#### 2B. Expand Python AST Analysis to Resolve Ambiguity
**What:** For Python files that match a regex pattern, use the existing AST engine (ast_engine.py) to verify the match semantically. Example: if a regex matches `subprocess.run(...)` in an agent autonomy context, the AST can check whether the arguments come from an AI model's output or are hardcoded strings.

**Evidence:** 5/32 blind-subset FPs were vocabulary/context mismatches where the regex matched syntactically but the semantic context was benign (e.g. `subprocess.run(["uv", "add", "oxylabs"])` is package installation, not AI-to-shell flow).

**Impact estimate:** 3–5 FP eliminations for Python files. No impact on other languages (AST is Python-only).

**Effort:** M–L. AST already exists but would need new verification passes per pattern type.

**Identity compatible:** YES. AST engine is stdlib-only (uses Python's built-in `ast` module).

### Tier 3: High Impact, High Effort, or Identity-Challenging

#### 3A. Hybrid LLM Post-Filter (Offline, Optional)
**What:** After Regula produces findings, offer an optional `--verify` flag that runs each finding through a local LLM (Ollama) to classify it as TP/FP with reasoning. The ICSE 2026 paper (arXiv:2601.18844) showed hybrid LLM+static analysis eliminates 94–98% of FPs while maintaining recall, at 2.1–109.5 seconds per alarm.

**Evidence:** VERIFIED — Du et al., "Reducing False Positives in Static Bug Detection with LLMs," ICSE 2026 SEIP. Tested on 433 industrial alarms (328 FP, 105 TP) from Tencent's BkCheck. Hybrid techniques achieve near-perfect FP elimination.

**Impact estimate:** Potentially transformative — could reduce FP rate to <5% on all corpora.

**Effort:** L. Requires Ollama integration, prompt engineering for each tier, and testing.

**Risk:** Violates the "zero runtime dependencies" identity if made mandatory. Mitigated if offered as an optional flag (offline, local LLM). Users who want maximum precision opt in; the default remains deterministic regex.

**Identity compatible:** PARTIALLY. Acceptable as opt-in. Not acceptable as default. The identity constraint is "zero runtime dependencies for the core scanner" — an optional post-filter doesn't violate this if the core works without it.

#### 3B. Cross-File Data Flow Analysis
**What:** Build a lightweight call graph for the scanned project. Check whether flagged functions are actually called from regulated code paths, or are dead/test/utility code.

**Evidence:** Semgrep's taint mode and SonarQube's cross-file analysis are the industry gold standard for FP reduction. Semgrep documents that "taint mode gives better precision than pattern matching." SonarQube builds control flow graphs and data flow graphs. VERIFIED — Semgrep docs, SonarQube blog.

**Impact estimate:** High — would eliminate most context-mismatch FPs. But the engineering cost is substantial.

**Effort:** L–XL. Building a cross-file call graph in stdlib-only Python is a major engineering project.

**Identity compatible:** YES (if built in stdlib Python). But effort is disproportionate for a solo project.

#### 3C. Tree-Sitter Multi-Language AST
**What:** Replace regex with tree-sitter AST queries for all 8 languages. This is what Systima Comply does (tree-sitter WASM).

**Evidence:** Tree-sitter provides structural understanding that regex cannot — community consensus is that AST-based analysis gives the real dependency graph rather than approximations. REPORTED — DEV Community and practitioner consensus, not a single citable source.

**Impact estimate:** Would eliminate nearly all vocabulary-mismatch FPs. But fundamentally changes the architecture.

**Effort:** XL. Requires adding tree-sitter as a dependency (compiled C extension). 

**Identity compatible:** NO. Violates stdlib-only constraint. Would require a policy decision to relax the constraint.

---

## Recommended Sequence

| Priority | Action | Estimated Impact | Effort | Dependencies |
|----------|--------|-----------------|--------|-------------|
| **1** | 1A: File-path exclusion layer | 27 FPs eliminated (75% of all FPs) | S | None |
| **2** | 1B: Honour own gate detection | 2 FPs eliminated | S | None |
| **3** | 1C: Category corroboration requirement | 2+ FPs eliminated | M | None |
| **4** | 2A: Confidence threshold | 3–5 FPs eliminated | S | Needs calibration data |
| **5** | 2B: AST verification for Python | 3–5 FPs eliminated | M–L | Existing AST engine |
| **6** | 3A: Optional LLM post-filter | Near-complete FP elimination | L | Ollama, opt-in only |

**Item 1A alone** addresses 27/36 FPs (75%) with S effort and zero new dependencies. Items 1B and 1C address an additional 4 FPs from the remaining 9. Combined: 31/36 FPs (86%) addressed with S–M effort.

**The honest constraint:** Items 1–5 are refinements within the current architecture. Item 1A alone lifts precision from 36% to 67% on the blind subset and 90% to 100% on targeted, by eliminating 75% of all FPs via file-path filtering. Items 1B+1C push further to address 86% of FPs. To reach SonarQube-level precision (<5% FP rate, vendor self-report), you'd need either 3A (LLM post-filter) or 3B+3C (cross-file analysis + AST), both of which change the tool's character. The stdlib-only, deterministic, offline identity caps the achievable precision ceiling — and that's a trade-off the founder has already accepted.

---

## Session 17 Implementation Results

**Implemented:** File-path exclusion layer (item 1A) with tier-aware scope filter.
Default `--scope` changed from `all` to `production`.

**Predicted vs achieved:**
- Session 16 predicted 75% of FPs file-path-detectable → **achieved 61% (22/36)**
- Gap cause: 14% of FPs are semantically non-production but have production-looking
  file paths (dataset loaders, vocabulary mismatches, wrong Annex III categories).
  These require items 1B/1C/2B, not file-path heuristics.

**Design-validation results (NOT publishable precision — see circularity note):**

| Corpus | Before | After | FPs Excluded | TPs Suppressed |
|--------|--------|-------|-------------|----------------|
| Blind subset (50) | 36.0% | 58.1% | 19/32 | 0 |
| Targeted (39) | 89.7% | 97.2% | 3/4 | 0 |
| Combined (89) | 59.6% | 72.6% | 22/36 | 0 |

**CIRCULARITY WARNING:** These figures are design validation, derived from the
corpora the exclusion rules were tuned on. They confirm the rules do what they
were designed to do. They are NOT independent precision measurements and MUST
NOT be published as updated precision figures. An uncontaminated corpus is
required before any precision headline moves. The published 83.5% (random
production corpus, v1.7.0) is measured on a different benchmark and is
unaffected by this change.

---

## What This Does NOT Cover

- **Recall improvement** — unmeasured, requires planted corpus. Different problem.
- **New patterns** — adding more patterns increases breadth but doesn't improve precision (may decrease it).
- **Non-Python language depth** — Java/Go/Rust/C are regex-only. No AST available. Precision improvement there requires tree-sitter (3C) or LLM (3A).

---

## Evidence Tags

| Finding | Tag | Source |
|---------|-----|--------|
| SonarQube 3.2% FP rate via context-aware rules | VERIFIED (vendor self-report, not independently audited) | SonarQube blog, Feb 2026 |
| Hybrid LLM+SA eliminates 94–98% FPs | VERIFIED | Du et al., arXiv:2601.18844, ICSE 2026 |
| Semgrep taint mode > pattern matching for precision | VERIFIED | Semgrep docs |
| Tree-sitter AST > regex for structural analysis | REPORTED | DEV Community, practitioner consensus (no single citable source) |
| LLaMA-3.1 8B achieves F1 0.9852 on secret detection | VERIFIED | arXiv:2504.18784 |
| Root cause: 41% of FPs are test files | VERIFIED | This session's labelling data |
| Root cause: 75% of FPs detectable by file path (27/36) | VERIFIED | This session's labelling data, independently recounted by research-eval |
