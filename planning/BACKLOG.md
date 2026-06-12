# Regula Phase 2 — Backlog

> Decomposed from the Phase 2 plan into discrete, independently shippable tasks.
> Each task has acceptance criteria, dependencies, and effort estimates.
> Ready to drive subsequent build sessions.

---

## Workstream Key

| Tag | Workstream |
|-----|------------|
| A   | Claim and Benchmark Integrity |
| B   | Detection Quality — high_risk Tier |
| C   | Regulatory Currency |
| D   | Distribution |
| E   | Non-Technical Buyer Surface |
| F   | Website Elevation |
| G   | Multi-Regime Expansion |
| H   | Business Model (GATED) |

## Effort Key

| Size | Time |
|------|------|
| S    | < 2 hours |
| M    | 2–8 hours |
| L    | > 8 hours |

## Priority Key

| Priority | Meaning |
|----------|---------|
| P0       | Do first — foundation work and integrity fixes |
| P1       | This quarter |
| P2       | Next quarter |

---

## Workstream A: Claim and Benchmark Integrity

### A1 — Fix benchmark reproducibility command
**Priority:** P0 | **Effort:** S | **Dependencies:** None
**Status:** DONE — Session 1 (commit 0b1afcb et seq.)

`benchmarks/label.py score` must either (a) output the 83.5% headline when run without args, or (b) TRUST.md must specify the exact command that reproduces 83.5% (pointing to `benchmarks/results/random_corpus/`). A third party must be able to reproduce the headline number on first attempt by following the documentation.

**Acceptance criteria:**
- A third party following TRUST.md reproduces the headline number on first attempt
- The exact command is documented, including any required arguments or data paths
- Running the command produces output that unambiguously matches the published figure

---

### A2 — Add second-rater protocol
**Priority:** P1 | **Effort:** L | **Dependencies:** None
**Status:** PARTIAL — Session 4 (commits 8b22058, 48f4fd9, c10975a). Protocol documented, blind subset generated, compute_kappa.py built. Labelling itself is human-gated (HUMAN_ACTIONS §9).

Define an inter-rater protocol in LABELLING_CRITERIA.md. Recruit or self-perform second-rater review on >= 50 entries (10%+ of 446). Compute Cohen's kappa. Publish the result.

**Acceptance criteria:**
- Inter-rater protocol documented in LABELLING_CRITERIA.md
- >= 50 entries (10%+ of corpus) reviewed by a second rater
- Cohen's kappa computed and published
- Kappa >= 0.75 on reviewed subset, or honest disclosure of actual kappa with explanation

---

### A3 — Expand high_risk benchmark corpus to N >= 30
**Priority:** P1 | **Effort:** L | **Dependencies:** A2
**Status:** PARTIAL — Session 4 (commit cf945b6). 39 candidates harvested from 7 repos. Labelling is human-gated (HUMAN_ACTIONS §9).

Source additional high-risk AI application repos. Label findings using the second-rater protocol. Ensure at least 30 high_risk findings are labelled.

**Acceptance criteria:**
- high_risk tier has >= 30 labelled findings
- All new entries labelled with inter-rater agreement per A2 protocol
- Sources documented (repo URLs or dataset references)

---

### A4 — Implement confidence calibration curve
**Priority:** P2 | **Effort:** M | **Dependencies:** A3
**Status:** NOT STARTED — blocked on A3 labelling.

Plot actual precision against published confidence scores. Publish the calibration curve in benchmark documentation.

**Acceptance criteria:**
- Calibration plot published in benchmark docs
- BLOCK tier (>= 80 confidence) confirmed to have > 80% precision, or gap documented honestly
- Methodology for generating the curve is reproducible

---

### A5 — Add labeller field to benchmark corpus
**Priority:** P1 | **Effort:** S | **Dependencies:** None
**Status:** DONE — Session 2 (handover §Session 2).

Retroactively add labeller identification to all 446 entries in labels.json. Enforce the field for new entries.

**Acceptance criteria:**
- Every entry in labels.json has a `labeller` field
- New entries require the `labeller` field (validation or documentation enforces this)
- Existing entries attributed to the original labeller

---

### A6 — Publish benchmark corpus on HuggingFace + Zenodo
**Priority:** P2 | **Effort:** M | **Dependencies:** A2, A3
**Status:** NOT STARTED — blocked on A2/A3 labelling.

Package labels.json, methodology documentation, and reproduction scripts. Publish with a DOI on Zenodo and as a HuggingFace dataset.

**Acceptance criteria:**
- DOI assigned via Zenodo
- Dataset downloadable from both HuggingFace and Zenodo
- README explains methodology, labelling criteria, and reproduction steps
- Licence specified (consistent with project licence)

---

## Workstream B: Detection Quality — high_risk Tier

### B1 — Re-benchmark with domain gating active
**Priority:** P0 | **Effort:** M | **Dependencies:** A1
**Status:** DONE — Session 3. Random corpus PRECISION.json reflects v1.7.0 domain gating. high_risk N=6 explicitly documented as statistically unmeasurable.

Run the existing benchmark corpus with domain gating enabled. Report updated precision figures for all tiers. Quantify the improvement (or regression) in the high_risk tier.

**Acceptance criteria:**
- Updated precision numbers published for all tiers (prohibited, high_risk, limited_risk, minimal_risk)
- high_risk improvement (or regression) quantified with before/after comparison
- Domain gating configuration documented

---

### B2 — Tune employment/credit/medical patterns
**Priority:** P1 | **Effort:** M | **Dependencies:** B1
**Status:** NOT STARTED — needs labelled high_risk data from A3.

Review the top false-positive sources in the high_risk tier. Tighten patterns, add exclusions, and improve domain fingerprinting for employment, credit, and medical subcategories.

**Acceptance criteria:**
- high_risk precision improves by >= 15 percentage points on re-benchmark
- Changes documented (which patterns tightened, which exclusions added)
- No regression in other tiers beyond 2pp

---

### B3 — Add domain fingerprinting for remaining subcategories
**Priority:** P1 | **Effort:** M | **Dependencies:** None
**Status:** NOT STARTED — no blockers.

Expand DOMAIN_FINGERPRINTS to cover justice, democratic_processes, essential_services, and all other high_risk subcategories not yet fingerprinted.

**Acceptance criteria:**
- All 15 high_risk categories have corresponding fingerprint entries in DOMAIN_FINGERPRINTS
- Each fingerprint has at least 3 signals
- Synthetic tests pass for each new fingerprint

---

## Workstream C: Regulatory Currency

### C1 — Rewrite scripts/timeline.py for Omnibus
**Priority:** P0 | **Effort:** M | **Dependencies:** None
**Status:** DONE — Session 1.

Update all dates in timeline logic. Remove stale "trilogue" references. Add the 7 May 2026 provisional agreement. Correct all deadlines to reflect the Omnibus outcome.

**Acceptance criteria:**
- `regula timeline` outputs a correct, Omnibus-aware timeline
- No stale references to "trilogue" or pre-agreement dates
- 7 May 2026 agreement referenced with correct status ("provisional agreement, pending formal adoption")
- All downstream deadlines updated accordingly

---

### C2 — Update site/regions/uae.html
**Priority:** P0 | **Effort:** S | **Dependencies:** None
**Status:** DONE — Session 1.

Replace "currently in trilogue" with "provisional agreement reached 7 May 2026, pending formal adoption" on the UAE regional page.

**Acceptance criteria:**
- No stale regulatory claims on the UAE page
- Status accurately reflects "provisional agreement reached 7 May 2026, pending formal adoption"
- No broken links or formatting issues introduced

---

### C3 — Add editor's notes to 3 blog posts
**Priority:** P0 | **Effort:** S | **Dependencies:** None
**Status:** DONE — Session 1.

Add visible editor's notes to: `blog-omnibus-delay.html`, `blog-omnibus-decision-framework.html`, `blog-omnibus-trilogue-failed.html`.

**Acceptance criteria:**
- Each post has a visible editor's note dated June 2026
- Each note references the 7 May 2026 provisional agreement
- Notes are styled consistently and appear near the top of the article
- Notes link to the relevant source or updated content where appropriate

---

### C4 — Add Art 5 NCII/CSAM detection patterns
**Priority:** P1 | **Effort:** M | **Dependencies:** None
**Status:** DONE — Session 3. 9 patterns (5 CSAM + 4 NCII), 2 new prohibited categories. 6/6 TP, 7/7 benign FP-clean. Pattern count 389→398.

Add patterns to PROHIBITED_PATTERNS for AI systems generating CSAM or non-consensual intimate imagery, per Art 5 prohibitions.

**Acceptance criteria:**
- Patterns added to PROHIBITED_PATTERNS covering CSAM and NCII generation
- Synthetic tests pass and are wired into test_classification.py
- Test fixtures use char-code construction to avoid hook triggers
- No false positives on benign image-processing code in re-benchmark

---

### C5 — Update watermarking timeline logic
**Priority:** P1 | **Effort:** S | **Dependencies:** None
**Status:** PARTIAL — Session 1 (C1 timeline rewrite). `regula timeline` correctly shows new systems (2 Aug 2026) and existing systems (2 Dec 2026). `regula conform` does not yet distinguish new vs existing — it checks for marking code presence only.

Distinguish between new systems (2 Aug 2026) and existing systems (2 Dec 2026) in timeline and conform outputs for watermarking obligations.

**Acceptance criteria:**
- `regula timeline` shows both watermarking deadlines correctly
- `regula conform` distinguishes new vs existing systems where applicable
- Dates verified against the Omnibus text

---

### C6 — Prepare formal adoption update batch
**Priority:** P1 | **Effort:** S | **Dependencies:** None
**Status:** DONE — Session 1. Checklist at planning/ADOPTION_UPDATE_CHECKLIST.md.

Create a checklist of every location in the codebase and site that says "pending formal adoption" and will need updating when the Official Journal publishes.

**Acceptance criteria:**
- Checklist exists in `planning/`
- Covers all site pages, docs, timeline logic, and CLI output
- Can be executed in < 2 hours when formal adoption happens
- Includes the specific text to search for and the replacement text template

---

### C7 — Remove/update Colorado SB 205 content
**Priority:** P0 | **Effort:** S | **Dependencies:** None
**Status:** DONE — Session 1. Colorado page updated for SB 189.

Update the Colorado regional page with a prominent notice that SB 205 was replaced by SB 189 (disclosure-only, effective 1 Jan 2027). Remove Colorado from any active compliance target lists that reference SB 205.

**Acceptance criteria:**
- Colorado page accurately reflects SB 189 (disclosure-only, 1 Jan 2027)
- No references to SB 205 as active legislation remain anywhere in the codebase
- Prominent notice explains the legislative change

---

### C8 — Fix TRUST.md doctor output claim
**Priority:** P0 | **Effort:** S | **Dependencies:** None
**Status:** DONE — Session 1.

Update the claim in TRUST.md from "9 passed, 2 info" to "9 passed, 3 info" to match actual `regula doctor` output.

**Acceptance criteria:**
- TRUST.md claim matches actual `regula doctor` output
- Verified by running `regula doctor` and comparing

---

## Workstream D: Distribution

### D1 — Submit to awesome-static-analysis
**Priority:** P0 | **Effort:** S | **Dependencies:** None
**Status:** NOT SUBMITTED — Session 2 determined Regula fails 2/3 criteria (4 stars, 1 contributor). Needs ≥20 stars + ≥1 external contributor.

Create a YAML entry and submit a PR to `analysis-tools-dev/static-analysis`.

**Acceptance criteria:**
- PR submitted to analysis-tools-dev/static-analysis
- Entry follows the repository's CONTRIBUTING.md format
- Description is accurate and understated

---

### D2 — Submit to awesome-eu-ai-act lists
**Priority:** P0 | **Effort:** S | **Dependencies:** None
**Status:** PARTIAL — Session 2. PR submitted to morganrcu #13 (OPEN, no maintainer response). Already listed on GenAI-Gurus (discovered during Session 2).

Submit PRs to both `GenAI-Gurus/awesome-eu-ai-act` and `morganrcu/awesome-eu-ai-act`.

**Acceptance criteria:**
- Both PRs submitted
- Entries follow each repository's contribution guidelines
- Descriptions are factual (no inflated claims)

---

### D3 — Submit to awesome-devsecops + awesome-grc-ai
**Priority:** P0 | **Effort:** S | **Dependencies:** None
**Status:** PARTIAL — Session 2. PR submitted to awesome-grc-ai #7 (OPEN, no maintainer response). awesome-devsecops has no relevant category — not submitted.

Submit PRs to `devsecops/awesome-devsecops` and `ethanolivertroy/awesome-grc-ai`.

**Acceptance criteria:**
- Both PRs submitted
- Entries follow each repository's contribution guidelines

---

### D4 — Register MCP server on registries
**Priority:** P0 | **Effort:** M | **Dependencies:** None
**Status:** PARTIAL — Session 2. mcp-server.json committed, README annotated. Registry submissions require founder manual action (HUMAN_ACTIONS §6).

Create a `server.json` manifest. Register on the official MCP registry, mcp.so, Smithery, and PulseMCP.

**Acceptance criteria:**
- Listed on >= 3 MCP registries
- server.json manifest created and committed to the repo
- Each listing links back to the GitHub repo and PyPI page

---

### D5 — Email IAPP for vendor report inclusion
**Priority:** P0 | **Effort:** S | **Dependencies:** None
**Status:** PARTIAL — Session 2. Email drafted in HUMAN_ACTIONS §7. Sending is founder action.

Email acasovan@iapp.org with Regula details for inclusion in the IAPP AI Governance Vendor Report v1.4.

**Acceptance criteria:**
- Email sent with: tool description, category (Technical Assessments), public URL (getregula.com), and GitHub link
- Description is factual and proportionate

---

### D6 — Update robots.txt for 2026 AI crawlers
**Priority:** P0 | **Effort:** S | **Dependencies:** None
**Status:** DONE — Session 1.

Add OAI-SearchBot, Claude-SearchBot, Claude-User, Perplexity-User to the allow list. Remove deprecated `claude-web`.

**Acceptance criteria:**
- robots.txt allows all current AI search crawlers (OAI-SearchBot, Claude-SearchBot, Claude-User, Perplexity-User)
- Deprecated `claude-web` entry removed
- Standard crawlers (Googlebot, Bingbot) unaffected

---

### D7 — Submit sitemap to Bing Webmaster Tools
**Priority:** P0 | **Effort:** S | **Dependencies:** None
**Status:** NOT STARTED — founder manual action (HUMAN_ACTIONS §1).

Verify getregula.com is registered in Bing Webmaster Tools. Submit sitemap.xml.

**Acceptance criteria:**
- getregula.com verified in Bing Webmaster Tools
- sitemap.xml submitted and accepted
- No crawl errors reported

---

### D8 — Prepare and execute HN re-launch
**Priority:** P1 | **Effort:** M | **Dependencies:** C1, C2, C3, A2, A3 (labels + kappa must be published first)
**Status:** PARTIAL — Session 2. Package prepared (HUMAN_ACTIONS §8: title, body, maker comment, engagement protocol). GATED on benchmark labelling pipeline (items 7–13 in human queue): launch with single-rater 33% high_risk on N=6 is a credibility risk.

Write a Show HN post with a technical framing (static analysis angle, not compliance angle). Prepare a maker comment. Schedule for Monday 00:00 UTC. Have 5–10 people ready to engage.

**Acceptance criteria:**
- Post published with technical framing
- Maker comment posted within 5 minutes of submission
- Responses to all comments within 15 minutes for the first hour
- No stale content on the site at time of launch (C1, C2, C3 complete)

---

### D9 — Publish comparison article
**Priority:** P1 | **Effort:** L | **Dependencies:** A1, B1
**Status:** DONE — Session 3. blog-static-analysis-ai-compliance.html published.

"Static Analysis for AI Compliance: Why Code Scanning Complements Questionnaires" — an evidence-based article that cites benchmarks honestly and positions code scanning as complementary to (not a replacement for) questionnaires.

**Acceptance criteria:**
- Published on getregula.com/blog
- Factual, evidence-based, cites benchmarks with honest framing
- Answer-first structure under all major headings
- No inflated claims about Regula's capabilities

---

### D10 — Publish risk classification guide
**Priority:** P1 | **Effort:** L | **Dependencies:** None
**Status:** DONE — Session 3. blog-classify-ai-system.html published.

"How to Classify Your AI System Under the EU AI Act" — targeting the highest-volume search intent in the EU AI Act compliance space.

**Acceptance criteria:**
- Published on getregula.com/blog
- Answer-first structure throughout
- FAQ schema markup included
- Cites specific EU AI Act articles (Art 6, Annex III, etc.)
- Accurate post-Omnibus content

---

### D11 — LinkedIn content programme
**Priority:** P1 | **Effort:** M | **Dependencies:** None
**Status:** NOT STARTED — founder action (human-written posts).

Four human-written text posts about: Omnibus implications, Art 50 Code of Practice, practical compliance tips. No product promotion. No AI-generated content.

**Acceptance criteria:**
- 4 posts published over 4 weeks
- Each post is original, human-written, and substantive
- No direct product promotion (educational/thought-leadership framing only)
- Content is accurate and post-Omnibus

---

## Workstream E: Non-Technical Buyer Surface

### E1 — Design executive summary PDF output
**Priority:** P1 | **Effort:** M | **Dependencies:** Research complete (PMF findings)
**Status:** DONE — Session 4 (commit db1e905). `regula report --format exec-summary` produces print-optimised HTML. Art 6 disclaimer and non-conformity footer included.

Add `regula report --format pdf-summary` that produces a 2-page executive summary suitable for forwarding to legal counsel or a board.

**Acceptance criteria:**
- PDF renders without WeasyPrint (HTML-to-PDF via browser print, or stdlib-only approach)
- Contains: risk tier, top findings, compliance score, recommended actions, Regula version/timestamp
- Layout is clean and professional
- Works on all three major OS platforms

---

### E2 — Design self-assessment web flow (research only)
**Priority:** P2 | **Effort:** M | **Dependencies:** None
**Status:** NOT STARTED.

Research and prototype a browser-based flow wrapping `regula assess` (5 questions). No build commitment — research deliverable only.

**Acceptance criteria:**
- Design document with wireframes
- Tech stack options evaluated (static site vs hosted)
- Effort estimate for implementation
- Privacy implications documented

---

### E3 — Design hosted report viewer (research only)
**Priority:** P2 | **Effort:** M | **Dependencies:** None
**Status:** NOT STARTED.

Research options for a read-only web view of `regula check` output. Evaluate static HTML bundle vs hosted service approaches.

**Acceptance criteria:**
- Design document with trade-offs
- Privacy implications documented (data residency, who sees the report)
- Effort estimate for each approach
- Decision deferred to founder

---

## Workstream F: Website Elevation

### F1 — Fix answer-first blog structure
**Priority:** P1 | **Effort:** M | **Dependencies:** None
**Status:** NOT STARTED.

Audit all 11 blog posts. Ensure the first 1–2 sentences under each H2 are standalone, quotable answers suitable for featured snippets.

**Acceptance criteria:**
- All blog posts audited
- All major headings (H2) have answer-first sentences immediately following
- Sentences are standalone and quotable (no "As we discussed above..." openers)

---

### F2 — Add data residency and sovereignty statement
**Priority:** P1 | **Effort:** S | **Dependencies:** None
**Status:** DONE — Session 3. Statement added near CTA in all 3 locales.

Add a visible statement to the landing page: "Your code never leaves your machine. Regula runs entirely locally. No data transmitted. UK-registered organisation."

**Acceptance criteria:**
- Statement visible on landing page near the CTA
- Updated in all three locale variants (EN, DE, PT-BR)
- Wording is factual and verifiable

---

### F3 — Add named author attribution
**Priority:** P1 | **Effort:** S | **Dependencies:** None
**Status:** DONE — Session 3. Author attribution added to blog posts missing it.

All blog posts and documentation pages should have visible author attribution (Kuziva Muzondo / The Implementation Layer) for E-E-A-T signals.

**Acceptance criteria:**
- Author name visible on all content pages
- Consistent styling across blog posts and docs
- E-E-A-T signal present (name, not just "Regula team")

---

### F4 — Review site against EuroComply/Credo AI credibility signals
**Priority:** P2 | **Effort:** M | **Dependencies:** None
**Status:** NOT STARTED.

Comparative audit of the landing page against EuroComply, Credo AI, and Vanta for credibility gaps (social proof, trust signals, design quality).

**Acceptance criteria:**
- Audit document with specific improvements identified
- Gaps prioritised by impact and effort
- No action required — research deliverable only

---

## Workstream G: Multi-Regime Expansion

### G1 — Begin EN 18228 category-level mapping
**Priority:** P1 | **Effort:** L | **Dependencies:** EN 18228 Enquiry text available (already public via AI Assurance Institute)
**Status:** DONE — Session 7 (commit 9c43370). 12 clauses mapped, 7 with indicator/evidence coverage. Based on secondary sources (caveat documented). Revision needed when standards publish (Q4 2026).

Map Regula finding categories to EN 18228 clause structure (risk identification, risk controls, monitoring).

**Acceptance criteria:**
- Traceability matrix draft: Regula category -> EN 18228 clause -> AI Act article
- Coverage gaps identified
- Matrix stored in `references/` or `docs/`

---

### G2 — Begin EN 18282 category-level mapping
**Priority:** P1 | **Effort:** L | **Dependencies:** EN 18282 Enquiry text available
**Status:** DONE — Session 7 (commit 9c43370). 7 clause groups, 16/17 AI_SECURITY categories mapped. Based on secondary sources (caveat documented). Revision needed when standards publish (Q4 2026).

Map AI_SECURITY_PATTERNS to EN 18282 clause structure (five outcome categories).

**Acceptance criteria:**
- Traceability matrix draft: AI_SECURITY category -> EN 18282 clause -> AI Act Art 15
- Coverage gaps identified
- Matrix stored in `references/` or `docs/`

---

### G3 — Remove Colorado from active targets
**Priority:** P0 | **Effort:** S | **Dependencies:** None
**Status:** DONE — Session 1 (same scope as C7).

Same scope as C7. Cross-referenced here for workstream tracking. See C7 for acceptance criteria.

---

### G4 — Art 50 Code of Practice quick-win
**Priority:** P0 | **Effort:** M | **Dependencies:** None
**Status:** DONE — Session 2. blog-art50-code-of-practice.html published with can/cannot evidence mapping.

Review the final Code of Practice (published 10 June 2026). Identify which provisions Regula can evidence. Publish a blog post or site update explaining the implications.

**Acceptance criteria:**
- Blog post or docs page published
- Identifies which Code of Practice provisions Regula can evidence
- Any new detection patterns or timeline references added to the codebase
- Content is factual and cites the Code of Practice directly

---

## Workstream H: Business Model (GATED)

### H1 — Document visa gate and revenue-independent sequencing
**Priority:** P0 | **Effort:** S | **Dependencies:** None
**Status:** DONE — Session 1. planning/REVENUE_GATE.md created.

Record in `planning/` that all revenue-generating work is blocked pending UK visa resolution. Ensure all P0/P1 tasks are revenue-independent.

**Acceptance criteria:**
- Gate documented in `planning/`
- All P0 and P1 tasks verified as revenue-independent
- Clear criteria for when the gate lifts

---

### H2 — Design Snort-model time-delayed pattern access (research only)
**Priority:** P2 | **Effort:** S | **Dependencies:** None (gated — execute only after visa gate lifts)
**Status:** GATED — visa gate (REVENUE_GATE.md).

Assess a time-delayed access model for detection rules (current rules free, N-day delay on new rules for free tier).

**Acceptance criteria:**
- Design document with pricing tiers and delay window options
- Implementation approach outlined
- Decision deferred to founder

---

### H3 — Design AGPL dual licensing option (research only)
**Priority:** P2 | **Effort:** S | **Dependencies:** None (gated — execute only after visa gate lifts)
**Status:** GATED — visa gate (REVENUE_GATE.md).

Assess whether AGPL for the detection rule database (separate from the Apache-licensed engine) creates a viable commercial licence path.

**Acceptance criteria:**
- Legal considerations documented
- Comparison with similar dual-licensing models (e.g., Elastic, MongoDB)
- Decision deferred to founder

---

## Execution Order (Recommended for Next 3 Build Sessions)

### Session 1: Integrity + Currency (Foundation)

| Task | Workstream | Title | Effort |
|------|------------|-------|--------|
| A1   | A | Fix benchmark reproducibility command | S |
| C1   | C | Rewrite scripts/timeline.py for Omnibus | M |
| C2   | C | Update site/regions/uae.html | S |
| C3   | C | Add editor's notes to 3 blog posts | S |
| C7   | C | Remove/update Colorado SB 205 content | S |
| C8   | C | Fix TRUST.md doctor output claim | S |
| D6   | D | Update robots.txt for 2026 AI crawlers | S |
| D7   | D | Submit sitemap to Bing Webmaster Tools | S |
| H1   | H | Document visa gate and revenue-independent sequencing | S |

**Goal:** Fix all integrity issues and stale regulatory content. No stale claims remain after this session.

### Session 2: Distribution Blitz

| Task | Workstream | Title | Effort |
|------|------------|-------|--------|
| D1   | D | Submit to awesome-static-analysis | S |
| D2   | D | Submit to awesome-eu-ai-act lists | S |
| D3   | D | Submit to awesome-devsecops + awesome-grc-ai | S |
| D4   | D | Register MCP server on registries | M |
| D5   | D | Email IAPP for vendor report inclusion | S |
| G4   | G | Art 50 Code of Practice quick-win | M |
| A5   | A | Add labeller field to benchmark corpus | S |

**Goal:** Maximum external visibility with minimum code changes. All low-effort distribution tasks cleared.

### Session 3: Detection + Content

| Task | Workstream | Title | Effort |
|------|------------|-------|--------|
| B1   | B | Re-benchmark with domain gating active | M |
| C4   | C | Add Art 5 NCII/CSAM detection patterns | M |
| C5   | C | Update watermarking timeline logic | S |
| D9   | D | Publish comparison article | L |
| D10  | D | Publish risk classification guide | L |
| F2   | F | Add data residency and sovereignty statement | S |
| F3   | F | Add named author attribution | S |

**Goal:** Improve detection quality, add missing patterns, and publish the two highest-value content pieces.

---

## Summary Statistics

*Recomputed from status lines above on 12 June 2026. 42 task headings
(G3 shares scope with C7 — both counted). Original file claimed 43; that
was always wrong.*

| Status | Count | Tasks |
|--------|-------|-------|
| DONE | 21 | A1, A5, B1, C1, C2, C3, C4, C6, C7, C8, D6, D9, D10, E1, F2, F3, G1, G2, G3, G4, H1 |
| PARTIAL | 8 | A2, A3, C5, D2, D3, D4, D5, D8 |
| NOT STARTED | 10 | A4, A6, B2, B3, D7, D11, E2, E3, F1, F4 |
| NOT SUBMITTED | 1 | D1 (fails awesome-static-analysis criteria) |
| GATED | 2 | H2, H3 (visa) |
| **Total** | **42** | |

| Workstream | Done | Partial | Not Started | Other |
|------------|------|---------|-------------|-------|
| A — Benchmark Integrity | 2 (A1, A5) | 2 (A2, A3) | 2 (A4, A6) | — |
| B — Detection Quality | 1 (B1) | 0 | 2 (B2, B3) | — |
| C — Regulatory Currency | 7 (C1–C4, C6–C8) | 1 (C5) | 0 | — |
| D — Distribution | 3 (D6, D9, D10) | 5 (D2–D5, D8) | 2 (D7, D11) | 1 not submitted (D1) |
| E — Buyer Surface | 1 (E1) | 0 | 2 (E2, E3) | — |
| F — Website Elevation | 2 (F2, F3) | 0 | 2 (F1, F4) | — |
| G — Multi-Regime Expansion | 4 (G1–G4) | 0 | 0 | — |
| H — Business Model | 1 (H1) | 0 | 0 | 2 gated (H2, H3) |
