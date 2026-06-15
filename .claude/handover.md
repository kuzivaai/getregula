# Regula Handover — Sessions 1–18

**Date:** 15 June 2026
**Branch:** main
**Last commit:** d1f8a19 (pushed to origin/main)
**Regula version:** 1.7.1
**Author:** Claude Opus 4.6 across 18 build sessions + 1 planning phase

---

## What Was Done (Sessions 11–18, This Conversation)

Sessions 1–10 are documented in the previous handover (preserved below in §Previous Sessions). This section covers the current conversation only.

### Session 11: Competitive Research + GEO/SEO Maximisation

**Half A — Research (no code):**
- Competitive scan re-verified via GitHub API + PyPI API (13 Jun 2026)
- Technology/methodology scan (last 30 days): Omnibus, tree-sitter, MCP RC, GEO practice
- Objective rating on 6 axes: Regula leads on capability (4–5/5) but discoverability is 1/5
- Gap analysis: bottleneck is distribution, not capability
- GEO/SEO audit: 12→25 AI crawlers in robots.txt, 3 blog posts missing OG/Twitter/canonical, llms.txt stale (5/15 posts), no BreadcrumbList or WebSite schema
- Research-eval: 4 corrections applied (AIR Blackbox package count, missed competitor aibom-scanner, Systima framework claim, arXiv content claims downgraded)

**Half B — Implementation (approved auto-accept items):**
- robots.txt: 12 → 25 AI crawler user-agents
- llms.txt: 5/15 → 15/15 blog posts, Colorado SB-205 → SB 25-189, all regional pages
- llms-full.txt: created (57KB, 14K tokens) for IDE agents
- 3 blog posts: OG, Twitter, canonical, hreflang, enriched JSON-LD (en-standards-mapping, static-analysis, art50-code-of-practice)
- BreadcrumbList JSON-LD on all 26 indexable pages
- WebSite schema with SearchAction on EN/DE/PT-BR landing pages
- Sitemap: llms.txt lastmod updated, llms-full.txt entry added
- GitHub repo description: "389 risk patterns" → "398 risk patterns"

**Commits:** 2a4070d (GEO/SEO), 920a6cc (planning docs)

### Session 12: Value-Prioritisation Synthesis

Decision document — no implementation. Ranked all candidate next steps by value-per-effort. Finding (converged across Sessions 9–12): the bottleneck is distribution and labelling, not capability. Top-3: (1) 70-minute external blitz (push, IAPP, MCP registries, Bing), (2) label findings, (3) recruit Rater 2.

**Output:** `planning/SESSION12_PRIORITISATION.md`

### Session 13: Research-Eval Correction Closure

Applied 3 corrections from the independent research-eval of SESSION12:
1. False uniqueness claim: "only tool with published precision" → "publishes precision on blind-labelled production-code corpus (AIR Blackbox also publishes, on synthetic fixtures)"
2. Bing/ChatGPT overstatement: "absent entirely" → "improves Bing Chat/Copilot, supplements ChatGPT"
3. IAPP mistag: VERIFIED → REPORTED, "primary" → "a significant"

Repo-wide grep: no public-facing surface carried any of these claims. Planning-docs only.

**Commit:** ee1c547

### Session 14: Verification of Session 13 Corrections

Ran the verify→research→fix pipeline. Stage 1 (verify) confirmed all three correction-classes eradicated, replacement claims verified accurate from primary sources (AIR Blackbox SCANNER_EVAL.md re-fetched, robots.txt OAI-SearchBot confirmed, IAPP REPORTED tag confirmed). Stages 2–3 skipped — no defect found. Loop closed.

**No commit** — nothing changed.

### Session 15: Labelling Methodology + Decision Support

- Established methodology from standards: Cohen's kappa requires rater independence; an LLM that co-developed patterns is not a legitimate rater of record (non-independent of instrument); model pre-label is legitimate as disclosed decision support, excluded from kappa.
- Herzig et al. (ICSE 2013) citation: retracted (full text not accessed); replaced with Cristea et al. (arXiv:2208.01595, verified).
- Measured corpus: targeted is 84.6% biometrics, 12.8% credit scoring, 2.6% employment. 6/8 Annex III domains unrepresented.
- Built labelling workbenches (39 targeted + 50 blind subset) with code context, legal tests, file-type hints.
- Produced model pre-labels: targeted 35 TP / 4 FP (89.7%), blind subset 19 TP / 31 FP. Both in separate disclosed files with provenance headers.

### Session 16: Labelling + Precision Research

**Labelling (with founder as rater of record, model as disclosed assist):**
- Targeted corpus: 39/39 labelled (35 TP, 4 FP, 89.7% precision)
- Blind subset: 50/50 labelled (18 TP, 32 FP, 36.0% precision)
- All labels attributed to `kuziva-muzondo`, notes on every entry

**Precision improvement research:**
- Root cause: 41% of FPs are test files, 19% type defs/__init__, 12% utility plumbing
- Research-eval corrected: predicted 75% file-path-detectable → achieved 61% (22/36)
- Recommended: file-path exclusion layer (1A) as highest value-per-effort

**Output:** `planning/SESSION16_PRECISION_RESEARCH.md`

### Sessions 17–18: File-Path Exclusion Layer (Item 1A)

**Implementation:**
- `classify_provenance()` expanded: setup.py, setup.cfg, noxfile.py, types/ dirs, _utils/ dirs → tooling
- `_should_exclude_for_production_scope()`: tier-aware scope filter
  - prohibited / credential_exposure: NEVER excluded
  - __init__.py, types/, _utils/: excluded for minimal_risk only
  - examples: excluded for non-minimal tiers only
- `--scope` default: "all" → "production" (10 stale tests updated to pass `--scope all`)
- Observability: excluded-finding count printed to stderr
- 50 unit tests in `test_scope_exclusion.py`

**Design validation (NOT publishable — corpora shaped the rules):**

| Corpus | Before | After | FPs Excluded | TPs Suppressed |
|--------|--------|-------|-------------|----------------|
| Blind subset (50) | 36.0% | 58.1% | 19/32 | 0 |
| Targeted (39) | 89.7% | 97.2% | 3/4 | 0 |
| Combined (89) | 59.6% | 72.6% | 22/36 (61%) | 0 |

**Circularity constraint:** These figures are design validation, not publishable precision. An uncontaminated corpus is required before any precision headline moves. The published 83.5% (random production corpus, v1.7.0) is measured on a separate benchmark and is unaffected.

**Commit:** d1f8a19. Suite: 1,378 classification + 2,368 pytest = 3,746 passed, 0 failed.

---

## Current State (Verified Numbers)

| Metric | Value | Verified |
|--------|-------|----------|
| Version | 1.7.1 | constants.py |
| Detection patterns (tiered) | 398 | site_facts.json, risk_patterns.py |
| Pattern categories | 54 | risk_patterns.py |
| Languages | 8 | constants.py |
| Compliance frameworks | 12 (+ 5 display-only) | framework_crosswalk.yaml |
| Tests (pytest --collect-only) | 2,368 | Verified 15 Jun 2026 |
| Classification tests | 1,378 (834 functions) | Verified 15 Jun 2026 |
| Self-tests | 6/6 | regula self-test |
| Doctor checks | 9 passed, 3 info | regula doctor |
| CLI commands | 61 | regula --help-all |
| Precision (random corpus, v1.7.0) | 83.5% (N=115) | PRECISION.json |
| Precision (development corpus) | 36.8% (N=446) | benchmarks/label.py score |
| BLOCK-tier false positives | 0 | PRECISION.json |
| high_risk precision (targeted) | 89.7% (N=39, single-rater) | candidates.json |
| Blind subset precision | 36.0% (N=50, single-rater) | rater1_blind_subset.json |
| Design-validated precision (with scope filter) | 58.1% blind / 97.2% targeted | NOT publishable |
| Security findings | 0 (bandit + semgrep + pip-audit) | SECURITY.md |
| Blog articles | 15 | site/blog/ |
| GitHub stars | 4 | GitHub API, 15 Jun 2026 |
| PyPI downloads/month | ~100 | PyPI API, 15 Jun 2026 |
| AI crawlers in robots.txt | 25 | site/robots.txt |
| Pages with BreadcrumbList | 26/26 | All indexable pages |
| Pages with full OG+Twitter | 26/26 | All indexable pages |
| JSON-LD blocks | 75 | Across 26 HTML files |
| Backlog tasks | 42 (21 done, 8 partial, 10 not started, 1 not submitted, 2 gated) | planning/BACKLOG.md |

---

## What Is NOT Done (Human-Gated Queue)

Ordered by value-per-effort (from SESSION12_PRIORITISATION.md):

| # | Action | Time | Status |
|---|--------|------|--------|
| 1 | **Push to origin** — deploy Session 11 GEO changes | 10 min | **DONE** (Session 11) |
| 2 | **Send IAPP email** — draft at HUMAN_ACTIONS §7 | 5 min | NOT DONE |
| 3 | **MCP registry submissions** — 4 registries, steps at HUMAN_ACTIONS §6 | 30 min | NOT DONE |
| 4 | **Bing Webmaster Tools** — steps at HUMAN_ACTIONS §1 | 15 min | NOT DONE |
| 5 | **GitHub repo description** | 2 min | **DONE** (Session 11, "389"→"398") |
| 6 | **Label targeted findings + blind subset** | 2.5 hr | **DONE** (Session 16, 89 findings) |
| 7 | **Recruit Rater 2** — email academic contacts | 10 min + weeks latency | NOT DONE |
| 8 | **Lobste.rs invite request** | 10 min | NOT DONE |
| 9 | **Verify live site** — axe DevTools accessibility check | 15 min | NOT DONE |
| 10 | **LinkedIn content** — 4 human-written posts | 4 weeks | NOT DONE |
| 11 | **HN launch** — package at HUMAN_ACTIONS §8 | GATED on Rater 2 + kappa |

**The Word doc** `Regula_External_Blitz_14Jun2026.docx` was generated to the founder's Downloads folder with step-by-step instructions for items 2–4.

---

## What Remains Blocked on Human Action

| Blocker | What it unblocks |
|---------|-----------------|
| Rater 2 recruitment + labelling | Cohen's kappa → publishable precision → HN launch |
| IAPP email | Compliance buyer visibility |
| MCP registry submissions | IDE agent discoverability |
| Bing Webmaster Tools | Bing Chat / Microsoft Copilot visibility |
| UK visa resolution | All paid tiers (REVENUE_GATE.md) |
| EN 18228/18282 publication (Q4 2026) | Standards matrix revision |

---

## What the Next Claude Code Session Should Be

**If the founder has done items 2–4 (externals) and 7 (Rater 2 recruitment):**
→ Wait for Rater 2 labels. When they arrive: compute kappa, publish precision figures, update TRUST.md, fire HN launch package.

**If the founder wants to build before Rater 2 returns:**
→ The highest-value buildable item is **value-legibility copy drafting** (F2 from Session 11): rewrite the hero/CTA for non-technical buyers. Every sentence is a potential claim — founder must review line by line. This is the 3/5 value-legibility gap.

**If the founder wants to continue precision work:**
→ Items 1B (honour gate detection, S effort) and 1C (category corroboration, M effort) address the remaining 39% of FPs the path filter can't reach. But: these require calibration against a fresh corpus that doesn't yet exist. Building without measurement data repeats the pattern Session 16 exposed.

**What NOT to do:**
→ Another build session to avoid the human queue. Sessions 9–12 converged on this finding three times. The data hasn't changed.

---

## Known Issues and Honest Gaps

### Technical
- **high_risk precision is single-rater.** Rater 1 labels done (89.7% targeted, 36.0% blind). Rater 2 not recruited. Kappa unpublishable.
- **Design-validated precision (58.1%/97.2%) is circular.** The exclusion rules were derived from the corpora they improve. A fresh corpus is needed for an independent measurement.
- **Recall unmeasured.** Only synthetic fixtures (100% by construction). No real-code recall.
- **Python-deep, everything-else-shallow.** Java/Go/Rust/C are regex-only with fewer patterns.
- **File-path exclusion catches 61% of FPs, not 75%.** Session 16 predicted 75%; Session 17 implementation achieved 61%. The 14% gap is semantic mismatches (vocabulary, wrong categories) that require items 1B/1C/2B — different techniques, not more path rules.

### Visibility
- **Still 4 GitHub stars, ~100 PyPI downloads/month.** Distribution is the #1 problem, unchanged.
- **awesome-static-analysis:** Still fails criteria (4 stars, 1 contributor).
- **Two awesome-list PRs still OPEN:** morganrcu #13, awesome-grc-ai #7.
- **MCP registries, IAPP, Bing Webmaster:** All prepared but require founder manual submission.
- **Zero third-party mentions** found in Session 11 competitive scan.

### Content
- **SA policy page body** still describes the withdrawn draft's proposals in detail (hero/lede/FAQ updated).
- **EN 18228/18282 matrices** based on secondary sources — revision needed when standards publish (Q4 2026).

### Revenue
- **All paid tiers blocked** by UK visa constraint (REVENUE_GATE.md).

---

## Previous Sessions (1–10) — Summary

Sessions 1–10 are fully documented in the original handover. Key outcomes:

- **Session 1:** Integrity + regulatory currency. Benchmark reproducibility fixed, Omnibus timeline updated, claim auditor built.
- **Sessions 2–3:** Distribution blitz + detection quality. awesome-list PRs submitted, MCP manifest committed, IAPP email drafted, Art 5 NCII/CSAM patterns added (389→398), comparison article + classification guide published.
- **Session 4:** Benchmark credibility. Targeted corpus harvested (39 candidates), second-rater protocol documented, blind subset generated, compute_kappa.py built.
- **Sessions 5–6:** Deploy integrity + design system. Drift fixed, type system built, comparison table verified.
- **Session 7:** EN 18228/18282 standards mapping.
- **Session 8:** ReDoS investigation (not vulnerable), EuConform licence corrected.
- **Session 9:** Full-repository audit — 75 defects across 53 files, numeric/regulatory/locale/site fixes.
- **Session 9B:** SA tracker withdrawal, PT-BR diacritics, external link liveness (84 URLs checked).
- **Session 10:** Landing page refinement — card contrast, stats bar, grid monotony, hero density.

---

## Architecture Reminders (Do Not Change)

- **Bare imports:** `from errors import RegulaError`, NOT `from scripts.errors`. Every scripts/*.py uses `sys.path.insert(0, ...)`.
- **cli.py monolith:** Do not refactor. Command helpers split into cli_admin/analysis/evidence/infra.
- **json_output() envelope:** `{format_version, regula_version, command, timestamp, exit_code, data}` — immutable.
- **Test convention:** Custom runner walks globals() of test_classification.py. New test files wired via alias import + globals binding.
- **Hook awareness:** `hooks/pre_tool_use.py` scans all ops for credential patterns AND prohibited practice vocabulary. Test fixtures use char-code construction.
- **Locale sync:** Changes to EN must mirror in site/locales/de.html and site/locales/pt-br.html.
- **Claim auditor in CI:** `--verify-facts` checks 8 files against site_facts.json. Adding patterns without updating docs will fail CI.
- **Design tokens:** All colours, spacing, typography via CSS variables in site/assets/site.css. No new inline styles.
- **Scope default:** `--scope production` is now the default for `regula check`. Tests that need all findings must pass `--scope all`.

---

## Key File Locations

| Purpose | Path |
|---------|------|
| Planning docs | planning/ (BACKLOG, CLAIMS_AUDIT, RESEARCH_FINDINGS, STRATEGIC_PLAN) |
| Session 11 research | planning/SESSION11_RESEARCH.md |
| Session 12 prioritisation | planning/SESSION12_PRIORITISATION.md |
| Session 16 precision research | planning/SESSION16_PRECISION_RESEARCH.md |
| Human actions queue | planning/HUMAN_ACTIONS.md |
| Revenue gate | planning/REVENUE_GATE.md |
| Adoption update checklist | planning/ADOPTION_UPDATE_CHECKLIST.md |
| External blitz Word doc | /mnt/c/Users/mkuzi/Downloads/Regula_External_Blitz_14Jun2026.docx |
| Labelling methodology | benchmarks/SESSION15_METHODOLOGY.md |
| Labelling criteria | benchmarks/LABELLING_CRITERIA.md |
| Targeted corpus (labelled) | benchmarks/targeted_corpus/candidates.json |
| Blind subset (Rater 1, labelled) | benchmarks/rater1_blind_subset.json |
| Blind subset (Rater 2, unlabelled) | benchmarks/rater2_blind_subset.json |
| Model pre-labels (disclosed, not rater) | benchmarks/targeted_corpus/MODEL_PRELABEL.json, benchmarks/MODEL_PRELABEL_BLIND_SUBSET.json |
| Disagreement dossier | benchmarks/DISAGREEMENT_DOSSIER.md |
| Code context (deepface/face_rec) | benchmarks/targeted_corpus/CODE_CONTEXT.md |
| Code context (credit/employment) | benchmarks/targeted_corpus/CODE_CONTEXT_CREDIT_EMPLOYMENT.md |
| Code context (blind subset) | benchmarks/CODE_CONTEXT_BLIND_SUBSET.md |
| Scope exclusion tests | tests/test_scope_exclusion.py |
| Kappa computation | benchmarks/compute_kappa.py |
| EN 18228 mapping | references/en18228_mapping.yaml |
| EN 18282 mapping | references/en18282_mapping.yaml |
| MCP server manifest | mcp-server.json |
| Design system (CSS tokens) | site/assets/site.css |
| llms.txt | site/llms.txt |
| llms-full.txt | site/llms-full.txt |

---

## Verification Commands

```bash
# Full verify (all 4 steps)
python3 tests/test_classification.py && python3 -m pytest tests/ -q && python3 -m scripts.cli self-test && python3 -m scripts.cli doctor

# Claim auditor (semantic fact check)
python3 scripts/claim_auditor.py --verify-facts

# Planning consistency (backlog arithmetic, stale terms, blog index)
python3 scripts/planning_consistency.py

# Benchmark reproduction
python3 benchmarks/label.py score --corpus random  # → 83.5% (N=115)
python3 benchmarks/label.py score                   # → 36.8% (N=446)

# Kappa (after Rater 2 labelling)
python3 benchmarks/compute_kappa.py rater1_labels.json rater2_labels.json
```

---

*Handover written 15 June 2026. 18 build sessions, 639 total commits,
3,746 tests green (1,378 classification + 2,368 pytest), repo pushed to origin/main.*
