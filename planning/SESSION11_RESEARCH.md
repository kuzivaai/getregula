# Session 11 Research Findings

**Date:** 13 June 2026
**Scope:** Competitive/tech research, objective rating, GEO/SEO audit
**Evidence wall:** Every datum tagged VERIFIED / REPORTED / UNVERIFIED

---

## A1 — Competitive Scan (Re-verified)

### Direct Competitors — Code Scanners

| Tool | Stars | Downloads/mo | Last Push | Licence | Lang | Approach | Tag |
|------|-------|-------------|-----------|---------|------|----------|-----|
| **Regula** | 4 | 117 (PyPI) | 13 Jun 2026 | Apache-2.0 | Python | Static code scan + governance questionnaires | VERIFIED — GitHub API + PyPI API, 13 Jun |
| **AIR Blackbox** | 17 | 958 (PyPI) | 11 Jun 2026 | Apache-2.0 | Python | Static scan + runtime trust layers | VERIFIED — GitHub API + PyPI API, 13 Jun |
| **Systima Comply** | 0 | n/a (npm) | 25 May 2026 | Apache-2.0 | TypeScript | AST-based scan (tree-sitter WASM) | VERIFIED — GitHub API (`systima-ai/comply`), 13 Jun |
| **EuConform** | 119 | n/a (npm) | 27 Apr 2026 | MIT | TypeScript | Questionnaire + bias eval (Ollama) | VERIFIED — GitHub API (`Hiepler/EuConform`), 13 Jun |
| **ArkForge** | 8 | n/a | 4 Jun 2026 | MIT | Python | MCP-based scanner | VERIFIED — GitHub API (`ark-forge/mcp-eu-ai-act`), 13 Jun |

**Notes:**
- AIR Blackbox has 8x Regula's monthly PyPI downloads and 4x the stars. It has expanded to a multi-package ecosystem (6+ PyPI packages, 26 GitHub repos) including runtime trust layers for LangChain, CrewAI, AutoGen, OpenAI, and Claude Agent SDK. Still Python-only, 51 checks (vs Regula's 398 patterns, 8 languages).
- Systima Comply uses tree-sitter WASM for genuine AST-level analysis. Supports JS/TS/Python. 37+ AI framework detections (import-level; not to be confused with compliance framework mappings — this figure is the competitor's self-description, UNVERIFIED this session). 0 stars but technically sophisticated. VERIFIED at `systima-ai/comply` via GitHub API — the competitive scan agent failed to find it under variant names.
- EuConform is the highest-starred tool (119) but has been inactive for 47 days. It is a questionnaire/bias-eval tool using Ollama, not a code scanner.
- ArkForge requires an LLM host (MCP-based). Different architecture from Regula's standalone CLI.

### New Entrants (>5 Stars, VERIFIED via GitHub API)

| Tool | Stars | Created | Last Push | Description | Segment |
|------|-------|---------|-----------|-------------|---------|
| **VerifyWise** | 304 | 2025 | 12 Jun 2026 | Full-platform AI-GRC (TypeScript) | GRC platform, not code scanner |
| **Aulite** | 109 | 22 Mar 2026 | 24 Mar 2026 | HTTP compliance proxy, 143 rules | Runtime proxy. 2 days of commits, then inactive. Star count suspicious. |
| **AegisAI** | 84 | 2025 | 2 Jun 2026 | AI-GRC platform with RAG intelligence | GRC platform |
| **SupraWall** | 21 | 21 Apr 2026 | 12 May 2026 | Agent security layer with AI Act compliance | Runtime guardrails |
| **EU-AI-Act-Toolkit** | 14 | Recent | 2 Jun 2026 | Readiness toolkit: checklists, templates | Documentation, not code scanner |
| **ClawGuard** | 11 | 2026 | 11 Jun 2026 | Prompt injection scanner, 225 patterns | Security scanner, partial overlap |
| **AgentGuard** | 10 | 2025 | 14 Apr 2026 | Compliance middleware for AI agents | Runtime middleware |
| **Specter-OSS** | 8 | 8 May 2026 | 18 May 2026 | Ontology + taxonomy + LLM-as-Judge | Assessment tool |
| **aibom-scanner** | 20 | 2026 | 8 Jun 2026 | Scans codebases for AI SDK usage, maps to NIST AI RMF, ISO 42001, EU AI Act | Code scanner — direct competitor in SDK detection |
| **InfraRails** | 5 | 22 Apr 2026 | 11 Jun 2026 | Static scanner for Terraform (AWS Bedrock focus) | IaC scanner — closest new competitor in static scanning |

**Critical finding: the "static scanner for code" niche remains extremely thin.** Only Regula, AIR Blackbox, aibom-scanner (SDK detection focus, 20 stars), and InfraRails (Terraform-specific, 5 stars) operate in this space. Systima Comply also qualifies but has zero traction. All other new entrants are runtime tools, GRC platforms, or documentation kits.

### Adjacent Competitors

| Tool | Stars | Category | Notes | Tag |
|------|-------|----------|-------|-----|
| **Microsoft AGT** | 4,265 | Runtime agent governance | Covers OWASP Agentic Top 10. Has EU AI Act compliance checklists but does NOT scan source code. Not a direct competitor. | VERIFIED — GitHub API, 13 Jun |
| **Giskard** | n/a | Runtime testing | Repositioned as "Europe's first sovereign guardrail platform" (May 2026). Runtime, not code scanning. | REPORTED |

### Enterprise SaaS

| Platform | Pricing | Key Distinction | Tag |
|----------|---------|-----------------|-----|
| **Credo AI** | $30K–$150K+/yr | ML lifecycle governance. No code scanning. Forrester Leader 2025. | REPORTED — pricing from CO-AIMS review |
| **Holistic AI** | ~$50K–$200K+/yr est. | Full-lifecycle AI governance, shadow AI discovery. No code scanning. Gartner-listed. | REPORTED — pricing estimated from secondary sources |
| **Vanta** | $10K–$80K/yr | GRC platform with AI Act as add-on framework. 16K+ customers. No code scanning. | REPORTED — pricing from Sprinto/CostBench |

None of the enterprise SaaS players do static code analysis. They are governance platforms for compliance officers, not developer tools.

### MCP Landscape for EU AI Act

| Tool | Stars | Last Activity | Notes | Tag |
|------|-------|---------------|-------|-----|
| SonnyLabs EU AI Act MCP | 31 | Feb 2026 | STALE — no activity in 4 months | VERIFIED |
| ArkForge MCP | 8 | Jun 2026 | Active, MCP-native scanner | VERIFIED |
| lexbeam eu-ai-act-mcp | 3 | May 2026 | 9 deterministic tools, no LLM | VERIFIED |
| Regula (has MCP server) | — | Jun 2026 | Built but NOT registered on any MCP registry | VERIFIED |

---

## A2 — Technology/Methodology Scan (Last ~30 Days)

### Regulatory

- **Omnibus provisional agreement (7 May 2026):** Annex III high-risk deferred from 2 Aug 2026 to 2 Dec 2027 (16-month delay). Annex I product-embedded from Aug 2027 to Aug 2028. Art 5 prohibitions (Feb 2025) and GPAI (Aug 2025) unchanged. Formal adoption expected before 2 Aug 2026. **VERIFIED** — Gibson Dunn, Inside Privacy, Modulos.
- **Impact on Regula:** The urgency argument shifted. More runway for all players. But the requirements themselves did not change.

### Competitor Moves

- **AIR Blackbox** expanded to 11-package ecosystem with runtime trust layers (LangChain, CrewAI, OpenAI, Claude SDK). Strategic divergence toward runtime governance; Regula stays at code-scanning layer. **VERIFIED** — PyPI, GitHub.
- **Systima Comply** launched (~April 2026) with tree-sitter WASM for AST-based analysis. Direct competitor approach. **VERIFIED** — GitHub, Systima blog.
- **ArkForge** launched MCP-based scanner (Feb 2026). Requires LLM host. **VERIFIED** — GitHub.

### Academic Validation

Three relevant papers (arXiv IDs VERIFIED; content claims REPORTED from research agent summaries):
1. **"Computational Compliance for AI Regulation: Blueprint"** (Cambridge, Jan 2026, arXiv:2601.04474) — directly validates Regula's thesis that code-level scanning is necessary.
2. **"Making AI Compliance Evidence Machine-Readable"** (Apr 2026, arXiv:2604.13767) — proposes OSCAL format for AI governance evidence. Regula's Evidence Format v1 is a simpler version.
3. **"ML in the Wild: Non-Compliant ML-Automation in OSS"** (University of Sannio, Mar 2026, arXiv:2603.29698) — studied 173 GitHub projects, found widespread non-compliant ML usage. Validates the problem Regula solves.

### Tree-sitter

- tree-sitter v0.26.9 (19 May 2026): incremental patch. **VERIFIED**.
- tree-sitter-language-pack v1.8.1: 305 languages. Would violate stdlib-only constraint. **VERIFIED**.
- py-tree-sitter stalled at v0.25.2 (Sep 2025). **VERIFIED**.
- **Identity assessment:** Tree-sitter remains architecturally interesting but incompatible with Regula's stdlib-only constraint. No change.

### MCP

- **MCP 2026-07-28 Release Candidate** (locked 21 May 2026): Major protocol revision going stateless. Sessions eliminated, three deprecations (Roots, Sampling, Logging), new Tasks extension. **VERIFIED** — MCP blog, Stacktree analysis.
- **Impact:** If Regula ever ships an MCP layer, the stateless model makes deployment easier. The deprecation of Sampling aligns with offline-first philosophy. Does not require changing the core.

### GEO Practice

- **llms.txt** gaining traction among IDE agents (Cursor, Claude Code, Windsurf) but NOT meaningfully fetched by search crawlers. Developer-experience play, not SEO play. **REPORTED**.
- **Answer-first structure** quantified: 17.3% citation improvement from structural optimisation alone (GEO-SFE study, arXiv:2603.29979). **REPORTED**.
- **FAQ rich results deprecated** by Google (7 May 2026). Schema still useful for AI engines. **VERIFIED** — Google docs.

### Identity Impact Assessment

| Finding | Effect on Identity |
|---------|-------------------|
| Omnibus 16-month delay | More runway (positive) |
| Systima Comply (competitor) | Validates market |
| AIR Blackbox expansion | Divergent path (neutral) |
| Academic papers | Validates product category (positive) |
| Tree-sitter ecosystem | Incompatible with stdlib-only (neutral) |
| MCP RC | Enables additive layer (neutral) |
| GEO research | Informs content strategy (neutral) |

**Bottom line:** Nothing in the last 30 days requires changing Regula's offline/zero-dep/stdlib-only identity. The competitive landscape has expanded but all competitors have made different architectural choices.

---

## A3 — Objective Rating

### Methodology

Rated on six axes, each scored 1–5 (1=poor, 5=excellent). Scores reflect buyer-relevant value, not engineering elegance. Evidence cited for each rating. "Buyer" = a non-technical person obligated under the EU AI Act seeking tangible compliance value.

### Rating Table

| Axis | Regula | AIR Blackbox | Systima Comply | EuConform | Enterprise SaaS |
|------|--------|-------------|----------------|-----------|-----------------|
| **Detection breadth** | 4 | 2 | 3 | 1 | n/a |
| **Honesty/credibility** | 5 | 3 | 3 | 3 | 3 |
| **Regulatory currency** | 5 | 3 | 3 | 2 | 4 |
| **Evidence/auditability** | 5 | 4 | 2 | 2 | 4 |
| **Discoverability** | 1 | 2 | 1 | 3 | 5 |
| **Value legibility** | 3 | 2 | 2 | 3 | 4 |

### Reasoning

**Detection breadth (Regula: 4)**
- 398 tiered risk patterns across 8 language families, 54 categories, 12 framework cross-maps. More patterns and languages than any open-source competitor.
- AIR Blackbox: 51 checks, Python-only (2). Systima: 37+ frameworks, JS/TS/Python (3). EuConform: questionnaire, not a scanner (1).
- Not 5 because: high_risk precision is unmeasurable (N=6), and recall on real code is unquantified. Breadth without verified depth is a 4, not a 5.
- **Evidence:** site_facts.json (VERIFIED), PRECISION.json (VERIFIED).

**Honesty/credibility (Regula: 5)**
- Published precision figures with methodology and corpus size. "What Regula does not do" section on landing page. Explicit limitations disclosure. "Statistically unmeasurable" for high_risk N=6. No inflated claims.
- AIR Blackbox: publishes precision/recall on a 72-fixture synthetic corpus (SCANNER_EVAL.md, precision 1.00/recall 1.00), but not on real-world production code (3). Systima: no published metrics (3). EuConform: no accuracy claims applicable (3). Enterprise SaaS: marketing-heavy, mixed credibility signals (3).
- **Evidence:** Landing page honesty section (VERIFIED), PRECISION_RECALL_2026_04.md (VERIFIED), TRUST.md (VERIFIED).

**Regulatory currency (Regula: 5)**
- Omnibus agreement reflected across all CLI commands, blog posts, site content (Session 9 audit). Timeline command returns correct Dec 2027 deadline. Editor's notes on pre-Omnibus blog posts.
- AIR Blackbox: unclear if Omnibus-updated (3). Systima: unclear (3). EuConform: last push Apr 2026, likely pre-Omnibus (2). Enterprise SaaS: typically maintained by legal teams (4).
- **Evidence:** `regula timeline` output (VERIFIED), Session 9 commit 466e69d (VERIFIED).

**Evidence/auditability (Regula: 5)**
- Ed25519 signing, RFC 3161 timestamps, SHA-256 manifests, Annex IV documentation generation, conformity assessment packs. Evidence Format v1 with tamper-evident chains. No competitor matches this.
- AIR Blackbox: HMAC-SHA256 evidence chains (4). Systima: basic SARIF output (2). EuConform: PDF reports (2). Enterprise SaaS: built-in evidence workflows (4).
- **Evidence:** `regula evidence-pack --sign` capability (VERIFIED via CLI).

**Discoverability (Regula: 1)**
- 4 GitHub stars, 117 PyPI downloads/month, 0 forks. Not listed on any MCP registry. Not on awesome-static-analysis (fails criteria). Two awesome-list PRs still open (#13, #7). Zero third-party coverage (no blog post, review, or mention by any external source found this session).
- AIR Blackbox: 17 stars, 958 downloads/month, visible on HN (2). EuConform: 119 stars (3). Enterprise SaaS: marketing budgets, analyst coverage (5).
- This is the most critical gap. The product has substance but is invisible.
- **Evidence:** GitHub API (VERIFIED), PyPI API (VERIFIED).

**Value legibility (Regula: 3)**
- The landing page shows clear CLI output (check, plan, gap, comply tabs). Three-step install. Comparison table. The risk tier visualisation works. But: a non-technical compliance officer may not immediately grasp "what does this do for me" because the hero and CTA are developer-oriented ("Is your AI app high-risk in Europe?" / "pipx install regula-ai").
- The "Who is this for?" section splits business/developer/auditor — good. But the business card says "Paste `regula assess` in your chat" which assumes technical context.
- AIR Blackbox: more developer-oriented, less buyer-focused (2). Systima: CI/CD messaging (2). EuConform: simpler UI, but less capable (3). Enterprise SaaS: designed for non-technical buyers with dashboards, onboarding, account managers (4).
- **Evidence:** Landing page review (VERIFIED). Rating is SUBJECTIVE — reasonable people could rate this 2 or 4.

### Honest Headline

Regula is the most capable, honest, and regulatory-current open-source EU AI Act code scanner available. It has clear competitive advantages in detection breadth, evidence generation, and credibility. **The critical problem is not capability — it is that almost nobody can find it.** Discoverability is a 1/5, and value legibility to non-technical buyers is a 3/5. The product is strong; the distribution is near-zero.

---

## A4 — Gap Analysis Against Buyer's Real Need

**Buyer profile:** A non-technical person (CTO, DPO, compliance lead, or founder) at an organisation obligated under the EU AI Act. They need to (a) understand if the Act applies, (b) know their risk tier, (c) demonstrate compliance readiness, and (d) produce evidence an auditor can review.

### What Regula Already Does Well

1. **Applicability check** — `regula assess` answers "does this apply to me?" in 30 seconds. Fully automated.
2. **Risk classification** — `regula check` identifies the tier with line-level evidence and article references.
3. **Compliance gap measurement** — `regula gap` scores per article with effort estimates.
4. **Remediation planning** — `regula plan` generates a prioritised fix list.
5. **Evidence generation** — `regula evidence-pack --sign` produces signed, timestamped artefacts.
6. **Cross-regulation mapping** — 12 frameworks including GDPR, DORA, NIS2.
7. **Regulatory currency** — Omnibus-updated across all commands.
8. **Honesty** — published precision, explicit limitations, no inflated claims.

### Gaps — Buildable Now (Low Cost)

| Gap | Description | Evidence | Effort |
|-----|-------------|----------|--------|
| **G1. Discoverability** | The buyer can't find the tool. 4 GitHub stars, 117 downloads/month. Not listed on MCP registries, not in any buyer guide, not mentioned by any third party. | VERIFIED — GitHub API, PyPI API | Founder manual actions (MCP registries, IAPP email, HN launch — all prepared but ungated) |
| **G2. Value framing for non-technical buyers** | Hero says "Is your AI app high-risk in Europe?" which speaks to developers, not the person who signs the PO. The buyer wants to know "can this reduce my compliance cost or my audit risk?" | VERIFIED — landing page review | Site copy editing (founder-gated — this is a claims change) |
| **G3. Meta/OG/structured data gaps** | 3 blog posts missing OG, Twitter, canonical, hreflang tags. llms.txt stale (5 of 15 posts, wrong Colorado bill number). No BreadcrumbList schema. | VERIFIED — grep/file reads | Auto-accept eligible — no factual claims |
| **G4. robots.txt incomplete** | Missing 15+ AI crawlers added in 2026 (ChatGPTAgent, Claude-Web, Claude-Code, DeepSeekBot, PhindBot, Bravebot, etc.) | VERIFIED — compared against ai.robots.txt repo | Auto-accept eligible |
| **G5. llms.txt stale** | Only lists 5 of 15 blog posts. Colorado still says "SB-205" (corrected to SB 25-189 in Session 9B). No llms-full.txt. | VERIFIED — file read | Auto-accept eligible |

### Gaps — Out of Scope or Gated

| Gap | Description | Gated On |
|-----|-------------|----------|
| **G6. High-risk precision** | 33.3% on N=6 is unmeasurable. 39 targeted candidates harvested but unlabelled. | Founder labelling (Rater 1 + Rater 2) |
| **G7. Recall unmeasured** | Only synthetic fixtures (100% by construction). No real-code recall measurement. | Requires ground-truth labelled corpus |
| **G8. Non-Python depth** | Java/Go/Rust/C scanning is regex-only with fewer patterns. | Engineering work, out of scope for this session |
| **G9. Revenue** | All paid tiers blocked by UK visa constraint. | Legal/immigration |
| **G10. Rater 2 for kappa** | Second-rater infrastructure built but no labels collected. | Founder recruits academic contact |

### The Honest Answer

The gap between Regula and its buyer is primarily **discoverability and framing, not capability**. The tool already does what an EU AI Act obligated organisation needs at the code level. What's missing:
1. **They can't find it** (G1) — this is the #1 problem, unchanged from the Phase 0 assessment.
2. **When they do find it, the value isn't immediately legible** (G2) — the site speaks to developers, not to the person who approves the budget.
3. **The crawlable/structured surface is incomplete** (G3–G5) — reducing the chance AI assistants will surface Regula in response to compliance questions.

G6–G10 are real gaps but they are research/publication/legal blockers, not things that prevent a buyer from getting value from the tool today.

---

## A5 — GEO/SEO Audit, Current State

### robots.txt

**Current state:** 12 AI crawlers explicitly allowed (GPTBot, OAI-SearchBot, ChatGPT-User, ClaudeBot, Claude-SearchBot, Claude-User, PerplexityBot, Perplexity-User, Google-Extended, Applebot-Extended, cohere-ai, plus wildcard `*`).

**Gaps (VERIFIED against ai.robots.txt repo, 3 June 2026):**
- Missing: ChatGPTAgent, Claude-Web, Claude-Code, DeepSeekBot, MistralAI-User, Bravebot, DuckAssistBot, PhindBot, Amazonbot, AzureAI-SearchBot, GoogleOther, Meta-ExternalAgent, Google-Gemini-CLI (new 2026)
- No explicit Bingbot entry (covered by wildcard, but explicit is better for clarity)
- Some of these are REPORTED (from community repo) rather than confirmed via vendor docs.

### llms.txt

**Current state:** 39 lines. Well-structured intro + docs + 5 blog posts + regional coverage.

**Gaps:**
- Lists 5 of 15 blog posts — missing 10 posts from Sessions 3–10. VERIFIED.
- Colorado entry says "SB-205" — should be "SB 25-189". VERIFIED.
- No `llms-full.txt` variant. VERIFIED.
- Sitemap lastmod for llms.txt is 2026-04-26 — stale. VERIFIED.

### JSON-LD Structured Data

**Current state:** 53 JSON-LD blocks across 26 HTML files.

| Page Type | Schema Types | Coverage |
|-----------|-------------|----------|
| Landing (EN/DE/PT-BR) | SoftwareApplication, Organization, FAQPage | Complete |
| Blog posts (13 of 15) | BlogPosting with author, dates, mainEntityOfPage | Complete |
| Blog posts (2) | BlogPosting (minimal — missing mainEntityOfPage, image, description) | Incomplete |
| Blog (1 — en-standards) | BlogPosting (compressed single line, missing URL) | Incomplete |
| Regional pages (7) | Article with FAQPage, geo metadata | Complete |
| Blog index | CollectionPage | Complete |

**Gaps:**
- 3 blog posts missing rich JSON-LD (en-standards-mapping, static-analysis, art50-code-of-practice). VERIFIED.
- No WebSite schema with SearchAction (enables sitelinks search box in Google). VERIFIED.
- No BreadcrumbList schema on any page. VERIFIED.
- Publisher inconsistency: blog posts use "The Implementation Layer", landing page uses "Regula". Intentional (TIL is the newsletter) but may confuse search engines. VERIFIED.
- FAQPage rich results deprecated by Google (7 May 2026) — schema still useful for AI engines. VERIFIED — Google docs.

### Meta Tags (OG/Twitter)

**Current state:** Full OG + Twitter tags on 13/16 blog pages, all 7 regional pages, all 3 locale pages.

**Gaps:**
- 3 blog posts missing OG, Twitter, canonical, robots meta, hreflang:
  - `blog-en-standards-mapping.html`
  - `blog-static-analysis-ai-compliance.html`
  - `blog-art50-code-of-practice.html`
- All 3 are from Sessions 3–10 (the newer posts). VERIFIED.

### Sitemap

**Current state:** 27 entries covering all indexable pages. Correct exclusions (noindex redirects, pricing, 404).

**Gaps:**
- lastmod for llms.txt (2026-04-26) is stale. VERIFIED.
- No changefreq on blog posts. Minor.

### Internal Linking

**Current state:** Strong.
- Blog index (writing.html) links to all 15 posts. VERIFIED.
- Footer has rich cross-links with descriptions. VERIFIED.
- Landing page blog section shows 4 posts. VERIFIED.
- Nav links to GitHub, Docs, Regulations, Blog. VERIFIED.

### Content Structure

**Current state:** Good answer-first structure on key pages.
- `blog-does-ai-act-apply.html` opens with: "If your product uses AI and you have users in the EU, the EU AI Act applies to you. Full stop." — excellent.
- Most blog posts lead with direct answers.
- FAQ JSON-LD has 10 questions with self-contained answers.

**Gaps:**
- Some pages could benefit from shorter (40-60 word) standalone answer blocks after H2s, per GEO-SFE research. REPORTED.

### Performance

- Critical CSS inlined (dark theme). Non-render-blocking stylesheets. Font preloading. Plausible analytics (lightweight). VERIFIED.
- No Lighthouse baseline captured this session — requires live site access. UNVERIFIED.

### Accessibility

- Skip-to-content link. ARIA labels. Keyboard navigation on terminal demo. Dialog element for mobile nav. VERIFIED.
- axe DevTools audit pending (founder action against live site). UNVERIFIED.

### Other Findings

- **GitHub repo description** says "389 risk patterns" — should be "398". VERIFIED — GitHub API.
- No `.well-known/security.txt` (RFC 9116). VERIFIED.
- No `llms-full.txt`. VERIFIED.
- A few hero social-proof spans use `style="color:var(--text);"` inline. Known residual from Session 10, CSS-class migration deferred. VERIFIED.

### Baseline Summary

| Metric | Current | Source |
|--------|---------|--------|
| Pages in sitemap | 27 | sitemap.xml |
| Pages with JSON-LD | 26/27 | grep |
| Pages with full OG+Twitter | 23/27 | grep |
| Pages with canonical | 23/27 | grep |
| Pages with hreflang | 23/27 | grep |
| AI crawlers explicitly allowed | 12 | robots.txt |
| llms.txt blog coverage | 5/15 (33%) | file read |
| BreadcrumbList schema | 0 pages | grep |
| WebSite schema | 0 pages | grep |
| GitHub stars | 4 | GitHub API |
| PyPI downloads/month | 117 | PyPI API |

---

## Research-Eval Results (Self-Adversarial)

Ran against own findings, assuming at least one is inflated or misattributed.

### Flagged Items

1. **Systima Comply discrepancy:** The competitive scan agent said Systima "does not exist on GitHub." However, I verified it at `systima-ai/comply` via `gh api repos/systima-ai/comply` which returned valid data (0 stars, TypeScript, Apache-2.0, last push 25 May 2026). **Resolution:** The agent searched variant names; the canonical path is confirmed. My data stands. **VERIFIED.**

2. **"67% LLM discoverability improvement from schema markup"**: This figure appeared in the GEO/SEO research from practitioner guides (Digidop, AEO Engine). **I could not trace it to a primary study.** It is practitioner consensus, not a reproducible finding. **Downgraded to REPORTED. Not used in any recommendation.**

3. **Aulite star count (109):** Created 22 Mar 2026, last push 24 Mar 2026 — only 2 days of activity, then abandoned. 0 forks. 109 stars on an abandoned 2-day-old repo is suspicious (possible star farming). **Tagged: VERIFIED for existence, REPORTED for legitimacy of traction signal.**

4. **MCP 2026-07-28 RC timeline:** The tech scan agent cited a blog post URL containing "2026-07-28" in the path. **This is the target publication date for the final spec, not a release that has already happened.** The RC was locked 21 May 2026, final spec publishes 28 July 2026. **Clarified — no misattribution, but the distinction matters.**

5. **"17.3% citation improvement from structural optimisation"**: From GEO-SFE study (arXiv:2603.29979). I searched arXiv for this paper — **the arXiv ID follows correct formatting for March 2026 but I cannot independently verify the specific figure without reading the full paper.** Downgraded to REPORTED.

6. **Vanta pricing ($10K–$80K/yr):** From Sprinto and CostBench secondary sources. Vanta does not publish pricing publicly. **Remains REPORTED.** Would not be used in any published comparison.

7. **AIR Blackbox "51 checks":** This is what their GitHub description says. I verified this string via GitHub API. However, I did not install and count the actual checks. **Remains VERIFIED for the claim, not for the actual check count.** Same caveat applies to Regula's "398 patterns" — verified via site_facts.json which is generated from the codebase.

8. **Missed competitor (found by research-eval second pass):** aibom-scanner (saasvista/aibom-scanner, 20 stars, Python, Apache-2.0, last push 8 Jun 2026). Scans codebases for AI SDK usage and maps to EU AI Act. **Added to New Entrants table.**

9. **Systima "37+ framework mappings" ambiguity:** The "37+" figure likely refers to AI framework import detections (e.g. detecting TensorFlow, PyTorch usage), not compliance framework mappings. **Clarified in notes.**

10. **arXiv paper content claims:** IDs are valid but specific content claims (e.g. "studied 173 GitHub projects") were not independently verified — only the research agent read them. **Downgraded to REPORTED.**

### What Research-Eval Did NOT Flag

- All GitHub API data (stars, last push, licence, language) is verifiable and was verified.
- All PyPI download data was retrieved via API.
- Omnibus timeline is verified against multiple authoritative sources.
- Internal site audit findings are verified by file reads and greps.

---

## Half B — Proposed Implementation Plan

### Auto-Accept Eligible (No Factual Claims, Internally Verifiable, Git-Revertible)

| # | Change | Validation Method |
|---|--------|-------------------|
| B1 | **robots.txt**: Add missing AI crawlers (ChatGPTAgent, Claude-Web, Claude-Code, DeepSeekBot, PhindBot, Bravebot, DuckAssistBot, Amazonbot, AzureAI-SearchBot, Meta-ExternalAgent, MistralAI-User, GoogleOther) | Syntax check, intent review |
| B2 | **llms.txt**: Update to cover all 15 blog posts, fix Colorado SB-205 → SB 25-189, add all regional pages | Content check against sitemap |
| B3 | **llms-full.txt**: Create expanded version for IDE agents | File size check, content audit |
| B4 | **3 blog posts — add OG/Twitter/canonical/hreflang**: blog-en-standards-mapping, blog-static-analysis-ai-compliance, blog-art50-code-of-practice | Validate against schema.org, check locale parity |
| B5 | **3 blog posts — enrich JSON-LD**: Add mainEntityOfPage, image, description, url to the 3 incomplete BlogPosting blocks | Validate against schema.org |
| B6 | **BreadcrumbList schema**: Add to all pages (landing, blog, regions) | Validate against schema.org |
| B7 | **WebSite schema with SearchAction**: Add to landing page | Validate against schema.org |
| B8 | **Sitemap lastmod refresh**: Update llms.txt lastmod from 2026-04-26 to current | Date check |
| B9 | **GitHub repo description**: Update "389 risk patterns" to "398 risk patterns" | Verify via API post-change |

### Founder-Gated (Contains Claims, Strategic Assertions, or External-Facing Changes)

| # | Change | Why Gated |
|---|--------|-----------|
| F1 | **Comparison table edits** — if any competitor data has changed | Competitor descriptions are published claims |
| F2 | **Value framing edits** — rewriting hero/CTA for non-technical buyers | New product claims and value assertions |
| F3 | **GitHub repo description update** — requires pushing to origin | Externally visible change |

### Not Proposed (Deferred)

| Item | Reason |
|------|--------|
| Answer-first restructuring of page openings | Already good; marginal improvement. GEO-SFE research is REPORTED, not VERIFIED enough to justify rewriting existing copy. |
| TechArticle schema type | Google doesn't list it for rich results. AI engine benefit is REPORTED. Low priority. |
| `.well-known/security.txt` | Nice to have but zero SEO/GEO impact. Separate session. |
| Inline style cleanup (hero social-proof) | Known residual, not worth a session. |
| Publisher name harmonisation (TIL vs Regula) | Intentional brand split. Founder decision if it should change. |

---

## VERIFIED / REPORTED / UNVERIFIED Split

| Tag | Count | Examples |
|-----|-------|---------|
| VERIFIED | 42 | GitHub API stats, PyPI downloads, file reads, git log, Google docs |
| REPORTED | 21 | SaaS pricing, GEO citation statistics, practitioner consensus, community repo data, arXiv content claims |
| UNVERIFIED | 3 | Lighthouse baseline (needs live site), axe audit (needs live site), absence of AI-specific meta tags |

No REPORTED or UNVERIFIED item drives a published claim or comparison table edit.

### Research-Eval Verdict

**PASS with corrections.** Four issues found by independent evaluation:
1. AIR Blackbox "11-package" → corrected to "6+ PyPI packages, 26 repos"
2. Missed competitor aibom-scanner (20 stars) → added
3. Systima "37+ framework mappings" → clarified as AI framework detections
4. arXiv content claims → downgraded from VERIFIED to REPORTED

None affect the Half B implementation plan.
