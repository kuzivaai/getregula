# CLAIMS AUDIT — Regula v1.7.1

**Auditor:** Claude Opus 4.6 (automated, single-pass)
**Date:** 11 June 2026
**External research:** Live (web search available)
**Evidence standard:** VERIFIED = checked code/file directly (path cited). SOURCED = external reference (URL + date). FLAGGED = could not verify.

---

## 1. Pattern Inventory Reconciliation

### The Discrepancy

The state dossier claims "389 tiered regexes" as the marketing headline but its own tier table sums to 780. These are not contradictory — they count different things.

### How 389 Is Computed

`scripts/site_facts.py` iterates over 6 pattern dictionaries in `scripts/risk_patterns.py`. Each dictionary maps category names to dicts containing multiple keys. The function counts **only the `"patterns"` key** — the actual regex strings used for detection. It ignores metadata keys (`articles`, `description`, `confidence`, `conditions`, etc.).

**Verified breakdown (389):**

| Tier | Categories | Pattern Regexes | Article Reference |
|------|-----------|----------------|-------------------|
| PROHIBITED_PATTERNS | 8 | 33 | Article 5 |
| HIGH_RISK_PATTERNS | 15 | 242 | Annex III + Art 6(1) |
| LIMITED_RISK_PATTERNS | 4 | 23 | Article 50 |
| AI_SECURITY_PATTERNS | 17 | 51 | Art 15 + OWASP |
| BIAS_RISK_PATTERNS | 2 | 12 | Art 10(2-5) |
| GOVERNANCE_OBSERVATIONS | 6 | 28 | General |
| **TOTAL** | **52** | **389** | |

**Status:** VERIFIED. `python3 scripts/site_facts.py` produces `tier_regexes: 389`.

### How 780 Was Reached (Dossier Error)

The dossier's tier table used `sum(len(v) for v in dict.values())` on each pattern dictionary, which counts **all list-type values** — including `articles` lists, `conditions` lists, etc. — not just detection regexes. This inflated every tier:

- PROHIBITED: 89 (all lists) vs 33 (patterns only)
- HIGH_RISK: 422 (all lists) vs 242 (patterns only)

**The dossier's tier table is wrong.** The 780 figure has no meaningful interpretation and should not be published anywhere.

### What the Marketing Headline Should Be

**389** is the correct, reproducible number. It counts the regex strings that the scanner actually uses for detection.

**Reproducibility command:**
```bash
python3 -c "
import sys; sys.path.insert(0, 'scripts'); import site_facts
facts = site_facts.compute()
print(f'tier_regexes: {facts[\"tier_regexes\"]}')
"
```

### Additional Pattern Sources (Not Included in 389)

| Source | Count | Purpose |
|--------|-------|---------|
| AI indicators (code_analysis.py) | 212 | Library/framework detection |
| GPAI training patterns | 17 | GPAI systemic risk |
| Credential patterns | 18 | Secret detection |
| Architecture patterns | 38 | Code structure |
| Data source patterns | 10 | Data pipeline |
| Logging/oversight | 8 | Article 12/14 |
| Agentic categories | 30 | Agent governance |
| **Grand total (all sources)** | **692** | |

If a broader number is ever used, 692 is defensible as "grand total patterns across all detection modules." But it requires explanation and should not replace the 389 headline without context.

---

## 2. Test Count Reconciliation

### The Four Circulating Figures

| Figure | Meaning | Verified |
|--------|---------|----------|
| **2,309** | `pytest --collect-only` total | YES (2,309 collected in 0.60s) |
| **1,911** | 2,309 minus 398 globals() duplicates | YES (arithmetic) |
| **1,466** | Unique `def test_` function definitions (grep) | YES |
| **1,378** | Custom runner pass count | YES (Results: 1378 passed) |
| **834** | Custom runner function count | YES (834 test functions) |

### Why 1,911 != 1,466

- **1,466** counts unique function *definitions* across all test files
- **1,911** counts unique test *cases* collected by pytest (some functions produce multiple cases via parametrisation or dynamic generation)
- 1,911 + 398 (duplicates from globals() binding) = 2,309

Both numbers are correct but measure different things. TRUST.md says "1,911 unique tests" — this means unique test cases, not unique function definitions.

### The Honest Number to Publish

**2,309 pytest-collected** is the externally reproducible number. Anyone can run `pytest --collect-only -q` and confirm it.

The "1,911 unique" figure requires understanding the globals() binding mechanism — a third party would not naturally arrive at this number. It is honest but requires explanation. The current TRUST.md explanation (lines 87-88) is adequate.

The "1,466 unique functions" figure is never published and does not need to be.

### Parameterisation Padding Assessment

The difference between 1,466 functions and 1,911 test cases (445 extra) comes from pytest collecting the same function multiple times when it's imported via globals(). This is **not** parametrisation padding — it's an architectural choice for the custom runner. The 398 duplicates are legitimate: the same test runs under both pytest (native discovery) and the custom runner (globals() walk).

**Recommendation:** Continue publishing 2,309 as the headline. It is the one a sceptic can reproduce in one command.

---

## 3. Benchmark Integrity Audit

### 3.1 The 83.5% Headline Precision

**Claim:** 83.5% precision on production code (N=115, blind-labelled)
**Source:** benchmarks/results/random_corpus/BLIND_LABELS.json
**Methodology:** 50 Python AI repos (276 pool, seed=42), 201 findings, filtered to 115 production-code findings via --skip-tests

| Tier | TP | FP | Precision |
|------|---:|---:|----------:|
| minimal_risk | 11 | 0 | 100.0% |
| limited_risk | 7 | 1 | 87.5% |
| ai_security | 41 | 7 | 85.4% |
| agent_autonomy | 34 | 7 | 82.9% |
| credential_exposure | 1 | 0 | 100.0% |
| high_risk | 2 | 4 | 33.3% |
| **Overall** | **96** | **19** | **83.5%** |

**Status:** VERIFIED against the labelled data. The figure is real.

**Critical qualification:** Running `python3 benchmarks/label.py score` does NOT reproduce 83.5%. That command scores the full development corpus (446 entries, 36.8% precision). The 83.5% figure requires running against a separate file in benchmarks/results/random_corpus/. TRUST.md implies the main command reproduces it — this is MISLEADING.

### 3.2 The high_risk Tier (33.3%, N=6)

**Confirmed:** 2 TP, 4 FP on N=6 findings in the random corpus. This is statistically meaningless — the confidence interval on 33.3% with N=6 is roughly 4% to 78% (Wilson). Publishing "33.3% precision" for the tier that gives the product its name is the single worst technical fact in the project. Domain gating (introduced post-benchmark) should improve this, but no re-benchmark has been run.

### 3.3 Recall Measurement

**On real code: NOT MEASURED.** Explicitly documented in PRECISION_RECALL_2026_04.md (lines 229-234): "The OSS corpus is a sample of Regula's existing findings, labelled TP/FP. It does not measure false negatives."

**On synthetic fixtures: 100%.** 13 hand-crafted files (5 prohibited, 5 high-risk, 3 negative). These were authored by the same person who wrote the patterns — circular validation.

**F1 score: Cannot be computed.** Precision without recall gives no F1. This is correctly disclosed.

### 3.4 Labelling Integrity

- **Single rater.** No labeller field in the 446 corpus entries. No inter-rater reliability measured. No Cohen's kappa. LABELLING_CRITERIA.md line 122 says second-rater is "P2 not yet implemented."
- **No independent fixtures.** Synthetic corpus authored by pattern author. AVID-sourced fixtures noted as roadmap item.
- **Confidence scores uncalibrated.** A score of 80 does not mean 80% true-positive probability. Not validated against labelled data.
- **Python-only.** All benchmarked projects are Python. JS/TS/Java/Go/Rust/C precision is unmeasured.

### 3.5 What an Adversarial Reviewer Could Legitimately Attack

| Attack | Severity | Current Defence | Cost to Fix |
|--------|----------|----------------|-------------|
| "83.5% is on 115 findings from 50 repos — that's tiny" | HIGH | Disclosed but undersold | Expand corpus to 200+ findings from 100+ repos |
| "high_risk is 33% on N=6 — statistically void" | CRITICAL | Domain gating helps but not re-measured | Re-benchmark with domain gating; require N>=30 per tier |
| "Single rater — how do we know labels are correct?" | HIGH | Notes field has rationale | Add second rater on 10%+; publish inter-rater kappa |
| "Recall unmeasured — you could miss 90% of violations" | HIGH | Synthetic 100% recall cited | Build planted-issue corpus; measure real recall |
| "Only Python benchmarked — you claim 8 languages" | MEDIUM | Language depth documented | Benchmark at least JS/TS separately |
| "Synthetic fixtures written by pattern author — circular" | MEDIUM | Disclosed as limitation | Source fixtures from AVID or external contributors |
| "benchmarks/label.py score doesn't give 83.5%" | HIGH | Not documented clearly | Fix the command or document the exact command that reproduces 83.5% |

---

## 4. Claim-by-Claim Sweep

### TRUST.md

| Claim | Value | Status | Notes |
|-------|-------|--------|-------|
| 8 prohibited practices | 8 categories | VERIFIED | risk_patterns.py |
| 10 high-risk categories | 10 base (15 impl) | VERIFIED | Legislation: 8 Annex III + 2 Art 6(1) |
| 12 compliance frameworks | 12 | VERIFIED | framework_crosswalk.yaml |
| 1,911 unique tests | 1,911 test cases | VERIFIED | 2,309 - 398 duplicates |
| 2,309 pytest-collected | 2,309 | VERIFIED | pytest --collect-only |
| 6 self-tests | 6/6 | VERIFIED | regula self-test |
| 0 security findings | 0 | VERIFIED | bandit + semgrep + pip-audit |
| 83.5% precision (N=115) | 83.5% | VERIFIED | Random corpus BLIND_LABELS.json |
| 9 passed, 2 info (doctor) | 9 passed, 3 info | STALE | Third info message added since doc written |
| 932 passed, 495 functions (custom runner) | 1,378 passed, 834 functions | STALE | Updated in working tree but TRUST.md line 93 still shows old number |

Wait — let me re-check. The earlier session updated TRUST.md. Let me verify the current state.

**TRUST.md line 93 currently reads:** "Results: 1378 passed, 0 failed (834 test functions)" — VERIFIED as correct.

**TRUST.md line 113-114 (doctor):** Claims "9 passed, 2 info, 0 warn" — actual is "9 passed, 3 info". **STALE.**

### README.md

| Claim | Value | Status |
|-------|-------|--------|
| tests-N passing (badge) | 2,318 | STALE — was 2,309, updated Session 9 |
| 398 patterns, 8 languages, 30 seconds | 398, 8 | STALE — was 389, updated Session 9 |
| Tests (pytest --collect-only) = 2,318 | 2,318 | STALE — was 2,309, updated Session 9 |
| 61 CLI commands | 61 | VERIFIED |
| 12 compliance frameworks | 12 | VERIFIED |
| 0 required production dependencies | 0 | VERIFIED |

### Landing Page (site/index.html)

| Claim | Value | Status |
|-------|-------|--------|
| 398 risk patterns | 398 | STALE — was 389, updated Session 9 |
| 8 programming languages | 8 | VERIFIED |
| 12 compliance frameworks | 12 | VERIFIED |
| 0 external dependencies | 0 | VERIFIED |
| 2,318 tests | 2,318 | STALE — was 2,309, updated Session 9 |
| 0 security findings | 0 | VERIFIED |
| 83.5% precision (honesty section) | 83.5% | VERIFIED |
| 15.2% on AI library source code | 15.2% | VERIFIED (library subset) |
| 0 false positives at BLOCK tier | 0 | VERIFIED |

### MODEL_CARD.md

| Claim | Value | Status |
|-------|-------|--------|
| 398 tiered risk regexes | 398 | STALE — was 389, updated Session 9 |
| 54 categories | 54 | STALE — was 52, updated Session 9 |
| 2,318 pytest-collected | 2,318 | STALE — was 2,309, updated Session 9 |
| 1,920 unique | Recalculated Session 9 | STALE — was 1,911 |
| 8 languages | 8 | VERIFIED |
| 12 frameworks | 12 | VERIFIED |

### Claim Auditor Coverage Gap

The CI claim auditor (`scripts/claim_auditor.py`) checks for **source citations** (URLs, file references, verification labels) but does **not validate the accuracy of numbers**. It verifies that "389 patterns" has a citation to `scripts/risk_patterns.py` but never opens that file to confirm the count is 389.

**What it would need:** A semantic validation mode that loads `data/site_facts.json` and cross-references every numeric claim in markdown/HTML against the canonical counts. When `risk_patterns.py` grows, the auditor should flag that the published number may be stale.

---

## 5. Regulatory Currency Audit

### Correctly Updated (7 May 2026 Standard)

- site/index.html: Omnibus FAQ, deadline messaging — CORRECT
- site/locales/de.html, pt-br.html: Locale-synced — CORRECT
- references/article_obligations.yaml: Deadlines updated — CORRECT
- benchmarks/labels.json: 11 entries updated — CORRECT
- .claude/skills/regulatory-context/SKILL.md: Updated 11 Jun 2026 — CORRECT
- .claude/rules/regulatory-content.md: Caveat rule present — CORRECT

### STALE — Requires Update

| File | Line(s) | Issue |
|------|---------|-------|
| `scripts/timeline.py` | 7, 83-88, 115 | Last updated 5 April 2026. Says "trilogue failed 28 April" and "next trilogue expected mid-May 2026". The 7 May agreement is not reflected. **Entire file needs rewrite.** |
| `site/regions/uae.html` | 329 | Says "currently in trilogue". Should say "provisional agreement reached 7 May 2026, pending formal adoption." |
| `site/blog/blog-omnibus-delay.html` | 223+ | Update dated 1 May 2026 says "follow-up trilogue expected mid-May". Needs editor's note about 7 May agreement. |
| `site/blog/blog-omnibus-decision-framework.html` | 247+ | Same "1 May 2026" update, same stale language. |
| `site/blog/blog-omnibus-trilogue-failed.html` | 203, 217, 246-247 | Multiple references to "mid-May trilogue". Needs post-agreement editor's note. |
| `docs/TRUST.md` | 114 | Doctor output claims "9 passed, 2 info" — actual is "9 passed, 3 info". Minor. |

### Will Become Stale on Formal Adoption

When the Omnibus is published in the Official Journal (expected July 2026), every reference to "pending formal adoption" and "original deadlines remain legally binding" will need updating to "adopted [date], published OJ [date], new deadlines legally binding."

**Affected locations (at minimum):**
- site/index.html (urgency box)
- site/locales/de.html, pt-br.html (corresponding sections)
- site/regions/uae.html
- references/article_obligations.yaml
- benchmarks/labels.json (all deadline_note fields)
- .claude/skills/regulatory-context/SKILL.md
- scripts/timeline.py (after rewrite)

---

## 6. Coverage Gap Against New Law

### New Article 5 CSAM/NCII Prohibition

**Question:** Do detection patterns exist for the new Article 5 prohibition on AI systems that generate child sexual abuse material or non-consensual intimate imagery?

**Answer: NO.**

```
grep -rn 'csam\|ncii\|child.*sexual\|intimate.*image\|non.consensual.*intimate' scripts/risk_patterns.py
```
Returns: 0 results.

The `regulatory-context` skill correctly notes this prohibition (deadline 2 Dec 2026). `references/article_obligations.yaml` includes it. `scripts/timeline.py` line 73 references "non-consensual intimate deepfakes" in the Parliament's position. But **no detection patterns exist** in `risk_patterns.py` to flag code that might generate such content.

**Impact:** Regula cannot currently detect the newest prohibited practice. Given the 2 December 2026 enforcement date, this is a gap that should be addressed.

### Revised Article 50 Watermarking Timeline

**Question:** Does the scanner's logic account for the split watermarking deadline (new systems: 2 Aug 2026 unchanged; existing systems on market: 2 Dec 2026)?

**Answer: PARTIAL.** The `limited_risk` patterns in `risk_patterns.py` include `synthetic_content` patterns that detect AI-generated content without disclosure. But the timeline logic in `scripts/timeline.py` (which is stale — see Section 5) does not distinguish between new and existing systems for watermarking deadlines. The conformity evidence pack (`scripts/conform.py`) does not generate separate timelines for the two categories.

---

## Summary of Deal-Breakers

1. **Benchmark reproducibility gap:** `python3 benchmarks/label.py score` does not reproduce the 83.5% headline. A sceptic following TRUST.md instructions will get 36.8% instead.
2. **high_risk precision is 33.3% on N=6.** Statistically void for the tier that names the product.
3. **No real-world recall measurement.** Precision alone is insufficient for a compliance tool.
4. **Single-rater labelling with no inter-rater protocol.** Cannot quantify labelling bias.
5. **5 files with stale regulatory content**, including `scripts/timeline.py` (used by `regula timeline` command — user-facing).
6. **No CSAM/NCII detection patterns** for the newest Article 5 prohibition (effective Dec 2026).
