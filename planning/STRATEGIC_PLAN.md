# Regula Phase 2 Strategic Plan

**Created:** 11 June 2026
**Status:** Active
**Author:** Kuziva Muzondo
**Scope:** Post-audit prioritisation and execution plan

---

## Table of Contents

1. [Pre-Mortem](#1-pre-mortem)
2. [Honest Current-State Assessment](#2-honest-current-state-assessment)
3. [Workstreams](#3-workstreams)
4. [Kill List](#4-kill-list)
5. [Trade-Off Register](#5-trade-off-register)
6. [Sequencing and Dependencies](#6-sequencing-and-dependencies)

---

## 1. Pre-Mortem

_It is June 2027 and Regula failed to matter. The five most plausible causes, ranked by likelihood._

### 1.1 Invisibility (Most Likely)

Regula never escaped the zero-visibility trap. It is not listed on awesome-lists, MCP registries, the IAPP AI Governance Vendor Report, or any buyer guide. Three Hacker News posts scored 1–2 points. AIR Blackbox's comparison article did not mention it. ComplianceRadar and ActReady captured the SME market by being visible first. The tool was good but nobody knew it existed.

**Why this is #1:** Distribution is the binding constraint for a solo-maintained open-source tool. Technical quality is necessary but not sufficient. Every week of invisibility is a week where a competitor with worse technology but better distribution captures a buyer who will never switch.

### 1.2 No Non-Technical Surface

Engineers found Regula useful but could not sell it internally. Founders comparing compliance tools saw SaaS dashboards and PDF reports, not a CLI. EuroComply (EUR 149/month) won the SME buyer because it had a browser flow and downloadable artefacts. Regula's output stayed in terminals.

**Why this is #2:** The person who evaluates compliance tools is rarely the person who uses the terminal. A CLI-only tool is invisible to the budget holder.

### 1.3 Benchmark Credibility Collapsed

A competitor or Hacker News commenter ran `benchmarks/label.py score`, got 36.8% instead of the published 83.5%, and posted "Regula's precision claims are misleading." Single-rater labelling, no inter-rater kappa, N=6 for the high_risk tier — all legitimate attack vectors. Trust evaporated.

**Why this is #3:** Open-source credibility is binary. A single reproduced discrepancy, even if it stems from a misunderstanding (different benchmark file, different command), destroys trust permanently. The benchmark is honest but fragile.

### 1.4 Regulatory Staleness

The Omnibus was formally adopted in July 2026 but `timeline.py` still said "trilogue expected mid-May." Blog posts still referenced "August 2026 deadline." A compliance officer evaluating the tool found stale dates and moved on. Competitors (ComplianceRadar, ActReady) had Omnibus-correct content from day one.

**Why this is #4:** Compliance buyers are hyper-sensitive to accuracy. A single stale date signals the entire tool may be unmaintained. Regulatory staleness is not just a content problem — it is a credibility problem.

### 1.5 Competition Intensified Faster Than Expected

AIR Blackbox shipped 7 framework trust layers. Microsoft AGT hit 10K stars. ArkForge's MCP-first approach captured the AI coding assistant market. Giskard Guards became the default runtime layer. Regula's technical advantages (8 languages, zero-dep, offline-first) were real but not visible enough to matter against better-distributed competitors.

**Why this is #5:** Regula's differentiators (offline, zero-dep, multi-language, static analysis) are genuine. But differentiators that nobody sees are not differentiators. This cause compounds with #1 — competition only matters relative to visibility.

---

## 2. Honest Current-State Assessment

_Where the Phase 0 state dossier was wrong or inflated._

### 2.1 Pattern Count Inflation

The dossier's pattern tier table summed to 780. The actual marketing number — 389 tiered detection regexes — is correct and reproducible via `site_facts.py`. The dossier conflated detection regexes with metadata lists (keyword arrays, string constants, etc. that are not themselves patterns). The 780 figure must not appear anywhere. All references should use the verified 389 number.

**Action:** Grep codebase and documentation for "780" and replace or remove.

### 2.2 Colorado Is Not an Opportunity

Colorado was listed as a regulatory opportunity. SB 205 has been gutted and replaced by disclosure-only SB 189. There is no substantive compliance requirement that Regula can address. Colorado is not an opportunity and should be removed from the site or marked with a prominent notice.

**Action:** Update or remove `site/regions/colorado` content. Do not promote Colorado compliance as a feature.

### 2.3 Zero Visibility Is the Binding Constraint

"Zero third-party visibility" was stated in the dossier but undersold. To be explicit about the scope of the problem, Regula is absent from:

- The AIR Blackbox comparison article
- Every buyer guide searched (KLA Digital, Prediction Guard, Augment Code, AI Journal)
- Both awesome-eu-ai-act GitHub lists
- awesome-static-analysis
- All MCP registries (official, mcp.so, Smithery, PulseMCP, Glama)
- The IAPP AI Governance Vendor Report

This is not a weakness to be addressed alongside other priorities. It is the single binding constraint. All other improvements are wasted if nobody can find the tool.

### 2.4 Benchmark: Honest but Fragile

The 83.5% headline precision is real and reproducible — but only from a separate benchmark file, not from the default `benchmarks/label.py score` command. The per-tier breakdown reveals the fragility:

- **high_risk:** 33.3% precision on N=6 (statistically void)
- **limited_risk:** adequate sample size, reasonable precision
- **minimal_risk:** adequate sample size, high precision
- **BLOCK tier (CI default):** 0% false positives (strongest claim)

Additionally:
- Single-rater labelling with no inter-rater reliability metric
- No real-world recall measurement
- No confidence calibration
- Headline number requires qualification that undermines its marketing value

### 2.5 The Non-Technical Buyer Does Not Exist in the Current Product

There is no web surface. There is no PDF export that works without WeasyPrint. There is no self-assessment flow. There is no downloadable artefact a non-technical person can attach to a procurement questionnaire.

The product is a CLI for engineers. This is fine for the OSS community, but it is invisible to the people who make purchasing decisions for compliance tooling.

---

## 3. Workstreams

_Prioritised by impact on pre-mortem causes. Ordered by execution sequence._

### Workstream A: Claim and Benchmark Integrity

| | |
|---|---|
| **Objective** | Make every published number adversary-proof |
| **Pre-mortem cause** | #3 — Benchmark credibility collapse |
| **Priority** | P0 — Foundation for all other work |
| **Dependencies** | None (can start immediately) |

**Why this comes first:** Every other workstream builds on trust. If the benchmark is attacked before claims are hardened, all distribution work is wasted. This is the foundation.

**Tasks:**

1. **Fix benchmark reproducibility.** `benchmarks/label.py score` must produce the headline number, OR documentation must specify the exact command that does. A sceptical third party following TRUST.md instructions must reproduce every published number on first attempt.

2. **Add second-rater protocol.** Recruit one independent rater for 10%+ of the corpus. Calculate inter-rater kappa. Publish the methodology and the kappa score in TRUST.md.

3. **Expand high_risk corpus to N>=30.** Current N=6 is statistically void. Source additional high_risk findings from open-source projects using employment, credit, medical, and biometric patterns.

4. **Publish corpus on HuggingFace or Zenodo.** The corpus should be independently downloadable and auditable. This is a credibility signal and a research contribution.

5. **Implement confidence calibration curve.** For each risk tier, measure calibration (predicted probability vs observed accuracy). Publish the curve in the benchmark documentation.

**Definition of done:** A sceptical third party following TRUST.md instructions reproduces every published number on first attempt. Inter-rater kappa is published. high_risk corpus has N>=30.

**Risks:**
- Second-rater recruitment may be slow (mitigation: start with academic contacts, offer co-authorship on benchmark paper)
- Expanded corpus may reveal lower precision (mitigation: this is a feature, not a bug — honest numbers build trust)

---

### Workstream B: Detection Quality — high_risk Tier

| | |
|---|---|
| **Objective** | Achieve >=70% precision on high_risk tier with N>=30 |
| **Pre-mortem cause** | Core technical weakness affecting product credibility |
| **Priority** | P0 |
| **Dependencies** | Workstream A (benchmark must be credible before measuring improvement) |

**Why this matters:** 33.3% precision on N=6 is statistically void for the tier that names the product. "High risk" is the category that matters most to EU AI Act buyers. If Regula cannot reliably identify high-risk systems, the core value proposition is undermined.

**Tasks:**

1. **Re-benchmark with domain gating active.** Domain fingerprinting may already improve high_risk precision by filtering false positives from non-AI contexts. Measure the delta.

2. **Expand high_risk test corpus.** Source findings from:
   - Open-source HR/recruitment tools
   - Credit scoring libraries
   - Medical/clinical decision support code
   - Biometric processing projects
   - Law enforcement and border control tools (Annex III subcategories)

3. **Tune employment/credit/medical patterns.** Review false positives from current patterns. Add domain-specific context requirements (e.g., "salary" alone is not high_risk, but "salary" + "candidate_score" + "hiring_decision" is).

4. **Add domain fingerprinting for remaining Annex III subcategories.** Current fingerprinting covers employment and credit. Extend to medical, biometric, law enforcement, education, and critical infrastructure.

**Definition of done:** high_risk precision >=70% on N>=30 blind-labelled findings, with domain gating active.

**Risks:**
- Achieving 70% on a larger corpus may require significant pattern rewriting
- Some Annex III subcategories (e.g., border control) have very few open-source examples

---

### Workstream C: Regulatory Currency

| | |
|---|---|
| **Objective** | Every date, deadline, and article reference in the codebase is correct |
| **Pre-mortem cause** | #4 — Regulatory staleness |
| **Priority** | P0 |
| **Dependencies** | None (can start immediately) |

**Why this is P0:** Stale regulatory content is an instant disqualifier for compliance buyers. It also blocks Workstream D — there is no point promoting content that contains incorrect dates.

**Tasks:**

1. **Rewrite `timeline.py` for Omnibus.** The entire file needs updating. Currently user-facing via `regula timeline` and shows "trilogue expected mid-May 2026." Must reflect the Omnibus agreement (EP vote 569–45, trilogue 7 May 2026) and current adoption status.

2. **Update UAE page.** Verify all dates and references against current UAE AI Office publications.

3. **Add editor's notes to blog posts.** Three posts reference "follow-up trilogue expected mid-May" when the agreement was reached 7 May. Add editor's notes with correct dates and context.

4. **Add Art 5 NCII/CSAM patterns.** These are prohibited practices under the AI Act. Detection patterns should be added with synthetic test coverage.

5. **Update watermarking timeline logic.** Verify against the current Omnibus timeline for Art 50 transparency obligations.

6. **Prepare "formal adoption" update batch.** When the Official Journal publishes the Omnibus, all timeline references need a coordinated update. Prepare the batch now so it can be executed quickly.

**Definition of done:** Zero stale regulatory references anywhere in the codebase, site, or documentation. New Art 5 patterns passing synthetic tests.

**Risks:**
- Omnibus formal adoption date is uncertain (mitigation: prepare update batch, execute when OJ publishes)
- Art 5 patterns may require legal review for accuracy (mitigation: cite specific article text in pattern comments)

---

### Workstream D: Distribution (THE BINDING CONSTRAINT)

| | |
|---|---|
| **Objective** | Regula appears in the top 10 results when someone searches "EU AI Act compliance tool" |
| **Pre-mortem cause** | #1 — Invisibility |
| **Priority** | P0 — This is the single most important workstream |
| **Dependencies** | Workstream C must complete first (do not promote stale content) |

**Why this is the binding constraint:** Every other improvement is wasted if nobody can find the tool. The product could have 100% precision, perfect regulatory accuracy, and a beautiful web interface — and it would still fail if it remains invisible. Distribution is not a nice-to-have. It is the bottleneck.

**Tasks:**

#### D.1 Directory and Registry Submissions

Submit Regula to the following directories and registries:

- **awesome-static-analysis** — Regula fits the "security/compliance" category
- **awesome-eu-ai-act** (both lists) — primary audience match
- **awesome-devsecops** — compliance-as-code angle
- **awesome-grc-ai** — governance, risk, compliance for AI
- **awesome-compliance** — broader compliance tooling list
- **MCP registries:** official registry, mcp.so, Smithery, PulseMCP, Glama

Each submission should be a well-crafted PR with a one-line description that positions Regula clearly.

#### D.2 IAPP Vendor Report Inclusion

Email IAPP (acasovan@iapp.org) requesting inclusion in the AI Governance Vendor Report. Include:
- One-paragraph product description
- Link to GitHub and getregula.com
- Key differentiators (offline, zero-dep, 8 languages, open-source)
- Benchmark methodology link (TRUST.md)

#### D.3 Search Engine Visibility

- **Update `robots.txt`:** Add `OAI-SearchBot`, `Claude-SearchBot`, `Claude-User`. Remove deprecated crawlers. This enables GEO (Generative Engine Optimisation) — AI search engines must be able to crawl the site.
- **Submit sitemap to Bing Webmaster Tools.** Google Search Console is already connected; Bing is not.
- **Verify Perplexity and ChatGPT citation** by testing "EU AI Act compliance tool" queries after robots.txt update.

#### D.4 Hacker News Re-Launch

Previous HN submissions scored 1–2 points. A re-launch requires:
- **Technical framing:** Not "I built a compliance tool" but a specific technical insight (e.g., "What 8 languages of production code reveal about AI Act high-risk classification")
- **Timing:** Monday 00:00 UTC (optimal for EU/US overlap)
- **Maker comment ready:** Technical details, benchmark methodology, what the tool does not do (honest framing)
- **Prerequisite:** Workstream C complete, Workstream A at minimum benchmark reproducibility

#### D.5 Content Marketing

- **Publish comparison article:** Validated SEO topic. Honest comparison of EU AI Act compliance tools including Regula's weaknesses.
- **Publish risk classification guide:** Educational content targeting "EU AI Act risk classification" searches.
- **LinkedIn:** Human-written posts about Omnibus implications, not product promotion. The audience is compliance professionals, not developers. Value-first, tool-mention-last.

**Definition of done:** Listed on >=5 directories. MCP registries updated. IAPP vendor report inclusion confirmed or in pipeline. >=1 third-party article or buyer guide mentions Regula.

**Risks:**
- Awesome-list PRs may be rejected (mitigation: follow contribution guidelines precisely, one PR per list)
- IAPP may not respond (mitigation: follow up at 2-week intervals, attend IAPP events if possible)
- HN re-launch may score low again (mitigation: this is one channel among many, not a single point of failure)

---

### Workstream E: Non-Technical Buyer Surface

| | |
|---|---|
| **Objective** | A non-technical person can use Regula's output without a terminal |
| **Pre-mortem cause** | #2 — No non-technical surface |
| **Priority** | P1 |
| **Dependencies** | Research complete (from Phase 1 PMF findings) |

**Why P1 not P0:** Distribution (D) and credibility (A, B, C) come first. There is no point building a non-technical surface for a tool nobody can find. But this workstream must follow closely because the non-technical buyer is the path to revenue.

**Options under consideration:**

| Option | Effort | Impact | Notes |
|--------|--------|--------|-------|
| (a) Hosted read-only report viewer | Medium | High | Shareable URL, no install required |
| (b) Executive summary PDF output | Low | Medium | Downloadable artefact for procurement |
| (c) Web-based self-assessment flow | High | High | EuroComply pattern, but heavy to build |
| (d) Branded compliance report template | Low | Low | Static template, limited value |

**Minimum viable artefact:** One downloadable output that a founder can attach to a procurement questionnaire. This is option (b) — a PDF report that summarises findings, risk classification, and recommended actions, branded and professional.

**Tasks:**

1. **Research phase:** Evaluate options (a)–(d) against effort, impact, and solo-maintainer constraints.
2. **Build minimum artefact:** PDF or HTML report output that works without WeasyPrint (use stdlib or lightweight templating).
3. **Test with target persona:** Share with 2–3 non-technical founders and collect feedback on whether they would attach it to a compliance questionnaire.
4. **Iterate based on feedback.**

**Definition of done:** One non-CLI artefact exists that a non-technical person can use and share. At least one target user confirms it is useful for procurement.

**Risks:**
- PDF generation without external dependencies is limited (mitigation: HTML report with print-to-PDF instruction may suffice)
- Scope creep toward full SaaS (mitigation: hard boundary — one artefact, not a platform)

---

### Workstream F: Website Elevation

| | |
|---|---|
| **Objective** | getregula.com reads as authoritative compliance tooling, not a developer side project |
| **Pre-mortem cause** | Trust and credibility (compounds with #1 and #2) |
| **Priority** | P1 |
| **Dependencies** | Workstream C (regulatory currency must be correct first) |

**Why this matters:** Non-technical buyers evaluate the website before the tool. Template aesthetics and thin content signal "side project." Compliance buyers need credibility signals: named authors, data residency statements, professional presentation, accurate regulatory content.

**Tasks:**

1. **Fix GEO gaps:**
   - Update `robots.txt` with AI search engine crawlers (also in Workstream D)
   - Restructure blog posts for answer-first format (AI search engines extract the first paragraph)
   - Submit to Bing Webmaster Tools

2. **Add credibility signals:**
   - Data residency statement (where data is processed — answer: locally, never transmitted)
   - Named author attribution on all content
   - "Last verified" dates on regulatory content
   - Clear methodology links from any published numbers

3. **Blog post accuracy:**
   - Add editor's notes to all posts with stale Omnibus references (also in Workstream C)
   - Ensure all blog posts have a "Last updated" date

4. **Competitive credibility review:**
   - Review EuroComply, Credo AI, and ComplianceRadar websites for credibility signals Regula is missing
   - Identify and implement the highest-impact gaps

**Definition of done:** Site passes a compliance buyer's 30-second credibility check. GEO improvements measurable via Perplexity/ChatGPT citation testing within 60 days.

**Risks:**
- Design improvements may require skills outside the founder's core competency (mitigation: focus on content and structure, not visual redesign)
- GEO results take weeks to materialise (mitigation: measure baseline before changes, track monthly)

---

### Workstream G: Multi-Regime Expansion

| | |
|---|---|
| **Objective** | Decide which regulatory regimes beyond the EU AI Act justify investment |
| **Pre-mortem cause** | Scope sprawl vs missed opportunities |
| **Priority** | P2 (decisions now, execution later) |
| **Dependencies** | Standards publication (Q4 2026) |

**Why P2:** Spreading thin kills a solo project. The EU AI Act is the primary investment until the December 2027 high-risk deadline. Other regimes are evaluated for bounded, high-value additions only.

**Regime Decisions:**

| Regime | Decision | Rationale |
|--------|----------|-----------|
| EU AI Act high-risk (Annex III) | **YES — primary investment** | December 2027 deadline. This is the core product. |
| EN 18228 / EN 18282 mapping | **YES — begin now** | Category-level mapping can start before standards publish. Refine after publication in Q4 2026. High value for Annex IV documentation. |
| Art 50 transparency obligations | **YES — quick win** | Code of Practice just published. Transparency detection patterns are bounded and implementable. |
| Colorado SB 205 | **NO — remove** | Replaced by disclosure-only SB 189. Not an opportunity. Remove references from site. |
| Brazil AI regulation | **NO — wait** | Not yet law. Monitor but do not invest. |
| South Korea AI Basic Act | **NO** | Localised enforcement, no Korean language support. Not investable. |
| UK AI regulation | **WATCH** | ICO AI code not published yet. Monitor and prepare when published. |

**Tasks:**

1. Begin EN 18228/18282 category-level mapping based on available drafts
2. Implement Art 50 transparency detection patterns
3. Remove Colorado SB 205 references from site (also in Kill List)
4. Set calendar reminders for UK ICO code publication and Brazil legislative progress

**Definition of done:** EN 18228/18282 category-level mapping delivered when standards publish. Colorado references removed. Art 50 patterns implemented and tested.

---

### Workstream H: Business Model

| | |
|---|---|
| **Objective** | Define revenue model for when commercial activity becomes possible |
| **Priority** | P2 (gated on external constraint) |
| **Dependencies** | HARD GATE — see below |

#### Hard Gate: Visa Constraint

Revenue activation (EUR 49/149 evidence packs or any commercial activity) is **BLOCKED** pending resolution of the founder's UK visa constraints on independent commercial activity. This gate is lifted only by the founder, on professional immigration advice.

**This is not a soft constraint.** No commercial activity should be planned, promised, or implied until this gate is explicitly lifted.

#### Revenue-Independent Work This Quarter

All of Workstreams A–G are revenue-independent. Open-source improvements, visibility, credibility, and content do not require revenue and do not trigger visa constraints. This quarter's work is entirely within bounds.

#### When Gate Lifts

Priority order for revenue activation:

1. **Starter tier (EUR 49 one-time):** Evidence pack generation for SME self-assessment. Lowest friction, immediate value.
2. **Snort-model time-delayed pattern access:** New detection patterns available to paying users first, open-sourced after 90 days. Proven model from security tooling.
3. **AGPL dual licensing:** Detection Rule License (DRL) is already in place. Explore AGPL dual licensing for the detection rule database if commercial demand warrants it.

**Definition of done:** Revenue model documented and ready to execute when gate lifts. No premature commercial activity.

---

## 4. Kill List

_Items to remove, de-emphasise, or rewrite. Each is a credibility liability in its current form._

### 4.1 Colorado SB 205 References

**Problem:** `site/regions/colorado` page presents SB 205 as an active compliance requirement. SB 205 has been gutted and replaced by disclosure-only SB 189.

**Action:** Remove the Colorado page or add a prominent notice that SB 205 was replaced by SB 189 (disclosure-only). Current content is misleading.

**Owner:** Workstream G
**Urgency:** High — misleading content is a credibility risk.

### 4.2 "780 Patterns" in Any Context

**Problem:** The number 780 conflates detection regexes with metadata lists. The correct, reproducible number is 389.

**Action:** Grep the entire codebase and documentation for "780" and remove or replace. The number should never appear in any user-facing or internal context.

**Owner:** Workstream A
**Urgency:** High — inflated numbers are the fastest way to lose trust.

### 4.3 timeline.py Stale Content

**Problem:** The entire `timeline.py` file needs a rewrite. Currently user-facing via `regula timeline` and shows "trilogue expected mid-May 2026" when the trilogue agreement was reached 7 May 2026.

**Action:** Rewrite with Omnibus-correct dates and adoption status.

**Owner:** Workstream C
**Urgency:** Critical — user-facing stale regulatory content.

### 4.4 Blog Post "Update (1 May 2026)" Sections

**Problem:** Three blog posts reference "follow-up trilogue expected mid-May" when the agreement was reached 7 May 2026.

**Action:** Add editor's notes with correct dates. Do not delete original text — add a dated correction above it.

**Owner:** Workstream C
**Urgency:** High — blog posts are indexed by search engines and AI search tools.

### 4.5 TRUST.md Doctor Output Claim

**Problem:** TRUST.md says doctor output is "9 passed, 2 info" but actual output is "9 passed, 3 info."

**Action:** Update TRUST.md to match actual output.

**Owner:** Workstream A
**Urgency:** Medium — minor but undermines the trust document's own credibility.

### 4.6 SonnyLabs as a Key Competitor

**Problem:** SonnyLabs was last updated December 2025 and is likely abandoned.

**Action:** De-emphasise in competitive analysis. Move to "inactive/unverified" section if one exists, or add a note about last-known activity date.

**Owner:** Workstream D (competitive positioning)
**Urgency:** Low — internal analysis only, not user-facing.

---

## 5. Trade-Off Register

_Decisions that require explicit trade-off analysis. Some require founder decision; others are resolved by available evidence._

### 5.1 LLM-Assisted Analysis vs Zero-Dep Identity

| | |
|---|---|
| **Tension** | Field consensus supports LLM-assisted compliance triage, but Regula's identity is zero-dependency, offline-first |
| **Option A** | Stay pure regex/AST — maintain zero-dep identity, accept ceiling on analysis depth |
| **Option B** | Optional `regula[llm]` extra for triage/explanation — core stays stdlib-only, optional extra adds LLM capabilities |
| **Recommendation** | **(B)** — KCode architecture maps directly to this pattern. Field consensus supports hybrid approaches. Core remains stdlib-only; the extra is opt-in. This preserves the identity whilst unlocking deeper analysis for users who want it. |
| **Founder decision required?** | **Yes** — this is an architectural direction decision |

### 5.2 Breadth of Regimes vs Depth on EU

| | |
|---|---|
| **Tension** | Multiple regimes increase addressable market but spread a solo project thin |
| **Option A** | Add 3+ regimes now — broader appeal, thinner coverage |
| **Option B** | EU-only until December 2027 deadline — maximum depth, narrow scope |
| **Option C** | EU primary + EN standards mapping — bounded expansion with high value |
| **Recommendation** | **(C)** — EU primary with EN 18228/18282 standards mapping is bounded and high-value. Other regimes are not investable until the EU foundation is solid. Colorado is removed. Brazil and South Korea are not yet law. UK is watch-only. |
| **Founder decision required?** | **No** — the evidence is clear |

### 5.3 Engineer UX vs Non-Technical Surface

| | |
|---|---|
| **Tension** | CLI is the product's strength but invisible to budget holders |
| **Option A** | CLI-only — maintain focus, accept limited market |
| **Option B** | Web dashboard — full SaaS, heavy investment |
| **Option C** | PDF/report output — downloadable artefact, moderate investment |
| **Option D** | Hosted report viewer — shareable URL, moderate-to-high investment |
| **Recommendation** | **(C) as minimum, then (D) if resources allow.** Web-based flow is the EuroComply pattern and the long-term goal. PDF is the minimum viable artefact — it gives the non-technical buyer something to attach to a procurement questionnaire. |
| **Founder decision required?** | **Yes** — scope and investment level |

### 5.4 Benchmark Honesty vs Marketing

| | |
|---|---|
| **Tension** | 83.5% precision is real but requires qualifications that undermine its marketing value |
| **Option A** | Publish 83.5% prominently — strong headline, requires asterisks |
| **Option B** | Lead with per-tier breakdown — more honest, less punchy |
| **Option C** | Lead with BLOCK-tier 0% false positives — strongest defensible claim |
| **Recommendation** | **(C)** — "Zero false positives at CI default threshold" is the strongest, most defensible claim. It is true without qualification. It addresses the buyer's primary concern (will this break my CI pipeline with false alarms?). 83.5% can appear in detailed documentation with proper context. |
| **Founder decision required?** | **No** — (C) is clearly the correct choice |

### 5.5 Open-Source Purity vs Revenue

| | |
|---|---|
| **Tension** | Full open-source maximises adoption; revenue is needed for sustainability |
| **Option A** | Fully open forever — maximum adoption, zero revenue |
| **Option B** | Detection Rule License (current) — patterns are viewable but not redistributable commercially |
| **Option C** | AGPL dual licensing — AGPL for open-source, commercial licence for enterprise |
| **Option D** | Time-delayed rule access — new patterns to paying users first, open-sourced after 90 days |
| **Recommendation** | **Maintain (B) with option to explore (D) when visa gate lifts.** The Detection Rule License is already in place and defensible. Time-delayed access (the Snort model) is proven in security tooling and aligns with the open-source ethos. |
| **Founder decision required?** | **Yes** — licensing strategy |

### 5.6 Solo Project vs Community

| | |
|---|---|
| **Tension** | Bus factor of 1 is a legitimate risk, but quality control is hard with contributors |
| **Option A** | Stay solo — maximum quality control, bus factor 1 |
| **Option B** | Actively recruit contributors — reduce bus factor, increase maintenance burden |
| **Option C** | Accept PRs but do not recruit — organic growth, lower maintenance |
| **Recommendation** | **Start with (C), graduate to (B) if traction warrants.** Write a clear CONTRIBUTING.md with quality expectations. Accept PRs that meet the bar. Do not recruit until there is enough traction to justify the coordination overhead. |
| **Founder decision required?** | **Yes** — community strategy |

---

## 6. Sequencing and Dependencies

### Phase 2a: Foundation (Weeks 1–4)

Execute in parallel:

```
Workstream A (Benchmark Integrity)  ─────────────────────►
Workstream C (Regulatory Currency)  ─────────────────────►
Kill List items 4.1–4.5            ─────────────────────►
```

**Rationale:** A and C have no dependencies and are prerequisites for D. Kill List items are quick fixes that remove credibility liabilities.

### Phase 2b: Quality + Distribution Prep (Weeks 3–8)

```
Workstream B (high_risk Quality)   ──────── depends on A ─►
Workstream D.1–D.3 (Directories)   ──────── depends on C ─►
Workstream F (Website Elevation)   ──────── depends on C ─►
```

**Rationale:** B depends on A's benchmark infrastructure. D and F depend on C's regulatory corrections. D.1–D.3 (directory submissions, IAPP, SEO) can begin as soon as content is accurate.

### Phase 2c: Distribution Push (Weeks 6–12)

```
Workstream D.4 (HN Re-Launch)     ──────── depends on A+C ►
Workstream D.5 (Content Marketing) ──────── depends on C+F ►
Workstream E (Non-Technical Surface)────── research begins ►
```

**Rationale:** HN re-launch requires both benchmark credibility (A) and regulatory accuracy (C). Content marketing requires accurate content (C) and a credible website (F). Non-technical surface research can begin in parallel.

### Phase 2d: Expansion (Weeks 10+)

```
Workstream G (Multi-Regime)        ──────── depends on C ──►
Workstream E (Build phase)         ──────── depends on research►
Workstream H (Business Model)      ──────── GATED ─────────►
```

**Rationale:** G requires regulatory currency as a foundation. E moves from research to build based on Phase 2c findings. H remains gated on the visa constraint.

### Dependency Graph (Summary)

```
A (Benchmark) ──► B (high_risk Quality)
                  D.4 (HN Re-Launch)

C (Regulatory) ──► D (Distribution)
                   F (Website)
                   G (Multi-Regime)

D + F ──► D.5 (Content Marketing)

E: Research independent, build depends on research findings

H: GATED (external constraint)
```

---

## Appendix: Success Metrics

| Metric | Current | Target (12 weeks) | Target (6 months) |
|--------|---------|-------------------|-------------------|
| Third-party directory listings | 0 | >=5 | >=10 |
| IAPP vendor report | Not listed | Submitted | Listed |
| high_risk precision (N>=30) | 33.3% (N=6) | >=60% (N>=30) | >=70% (N>=30) |
| Benchmark inter-rater kappa | None | Published | >=0.7 |
| Stale regulatory references | Multiple | 0 | 0 |
| Non-CLI artefact | None | Research complete | 1 shipped |
| "EU AI Act compliance tool" search rank | Not in top 50 | Measurable improvement | Top 20 |
| HN post score | 1–2 | >=10 | N/A (one-shot) |
| GitHub stars | Current | +50 | +200 |

---

_This plan is a living document. It will be updated as workstreams progress, decisions are made, and external events (Omnibus OJ publication, standards release, visa resolution) change the landscape._
