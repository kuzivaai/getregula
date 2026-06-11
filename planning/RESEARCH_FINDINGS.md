# Phase 1 Research Findings

**Regula — Strategic Research (June 2026)**
Last updated: 11 June 2026

---

## 1. Regulatory Landscape (June 2026 Forward)

### 1.1 EU AI Act — Omnibus Amendment

The Omnibus Simplification Package reached **provisional agreement on 7 May 2026** between the European Parliament and Council. This is NOT yet formally adopted.

- **Council press release (7 May 2026):** Confirmed provisional agreement on simplification of the AI Act ([source](https://www.consilium.europa.eu/en/press/press-releases/2026/05/07/artificial-intelligence-act-council-and-parliament-reach-agreement-on-simplification/)).
- **Formal adoption path:** EP plenary vote expected June 2026, followed by formal Council adoption, then publication in the Official Journal (OJ) expected **July 2026**.
- **Gibson Dunn analysis (May 2026):** Detailed breakdown of deadline shifts and scope changes ([source](https://www.gibsondunn.com/eu-ai-act-omnibus-simplification-provisional-agreement/)).
- **Latham & Watkins (May 2026):** Confirmed the Omnibus does NOT reopen substantive obligations — it shifts timelines and narrows scope of certain categories ([source](https://www.lw.com/en/insights/2026/05/eu-ai-act-omnibus-agreement)).

**Key deadline changes under the Omnibus:**

| Obligation | Original deadline | Omnibus deadline | Delta |
|---|---|---|---|
| Annex III high-risk (standalone) | 2 Aug 2026 | **2 Dec 2027** | +16 months |
| Annex I high-risk (EU product legislation) | 2 Aug 2027 | **2 Aug 2028** | +12 months |
| Art 5 CSAM/NCII (new prohibited practice) | N/A | **2 Dec 2026** | New |
| Art 50 watermarking (existing systems) | 2 Aug 2026 | **2 Dec 2026** | +4 months |
| AI regulatory sandboxes | 2 Aug 2026 | **2 Aug 2027** | +12 months |

**Implication for Regula:** The 16-month extension for Annex III standalone high-risk systems is the most material change. It moves the hard compliance cliff from August 2026 to December 2027, giving deployers and providers significantly more runway. This does NOT reduce the market — it extends the sales window and shifts urgency from "panic now" to "plan now, comply by 2027."

### 1.2 AI Office Guidelines and Codes of Practice

**Code of Practice on AI Content Marking:**
- **FINAL version published 10 June 2026** by the AI Office.
- Voluntary adherence. Covers Article 50(2) marking obligations (provider-side technical marking) and Article 50(4) labelling obligations (deployer-side disclosure).
- Source: [AI Office Code of Practice on AI Content Marking — Final](https://digital-strategy.ec.europa.eu/en/library/code-practice-ai-content-marking) (10 Jun 2026).

**Article 50 Transparency Guidelines:**
- Still in **DRAFT** form. Public consultation closed **3 June 2026**.
- Final version expected before August 2026 (the Art 50 general transparency deadline).
- Source: [AI Office consultation on Art 50 guidelines](https://digital-strategy.ec.europa.eu/en/consultations/consultation-draft-guidelines-transparency-obligations-ai-act).

**Article 6 High-Risk Classification Guidelines:**
- **DRAFT** published for consultation. Consultation **open until 23 June 2026**.
- These guidelines clarify how to determine whether an AI system falls under Annex III high-risk classification, including the "significant risk" threshold.
- Critical for Regula's `classify` command accuracy.
- Source: [AI Office consultation on Art 6 guidelines](https://digital-strategy.ec.europa.eu/en/consultations/consultation-draft-guidelines-high-risk-classification).

### 1.3 Harmonised Standards — EN 18228 and EN 18282

Two CEN/CENELEC harmonised standards are progressing through the Public Enquiry phase, with **Q4 2026 publication targets**.

**prEN 18228 — AI Risk Management (maps to Art 9):**
- Structured around hazard identification, risk scenarios, and a Risk Management File.
- Directly relevant to code scanning: tools can evidence risk identification steps, logging configurations, monitoring infrastructure, and human oversight mechanisms.
- **Cannot address** organisational risk processes, governance structures, or documentation completeness — these remain outside code-scanning scope.
- Source: Adam Leon Smith substack, "AI Standards Watch" series ([source](https://adamleonsmith.substack.com/)); AI Assurance Institute commentary on EN 18228 alignment with ISO 23894.

**prEN 18282 — Cybersecurity for AI (maps to Art 15):**
- Five outcome categories: Prevent, Detect, Respond, Resolve, Control.
- Code tools can detect: input validation gaps, dependency vulnerabilities, hardcoded credentials, insecure model loading, missing encryption at rest/transit.
- Source: White & Case analysis of AI Act cybersecurity requirements ([source](https://www.whitecase.com/insight-alert/eu-ai-act-cybersecurity-requirements)); Bird & Bird standards tracker ([source](https://www.twobirds.com/en/insights/2026/eu-ai-act-harmonised-standards-tracker)).

**What "mapping" means for Regula:**
A traceability matrix from Regula finding categories → standard clauses → AI Act articles. This is bounded and tractable scope. Work can begin now at the category level (e.g., "logging finding" → EN 18228 §X.Y → Art 9(4)), with refinement after final publication. This is NOT about implementing the full standard — it is about demonstrating that code-level findings provide evidence towards standard compliance.

**OJEU citation timeline:** Estimated H1 2027 for official citation in the Official Journal, which triggers the presumption of conformity. Until citation, the standards are voluntary but carry significant persuasive weight. Exact date unverified.

### 1.4 International Regulatory Watch

**Brazil — PL 2338/2023:**
- Awaiting Chamber of Deputies plenary vote. Was scheduled for **27 May 2026** but outcome is **unconfirmed** as of this writing.
- Window effectively closes **August 2026** due to municipal elections consuming legislative bandwidth.
- **Recommendation:** Watch only. Do not invest engineering effort until the bill passes and implementing regulations clarify technical requirements.
- Source: Inside Privacy coverage of Brazil AI regulation ([source](https://www.insideprivacy.com/artificial-intelligence/brazil-ai-regulation-update-2026/)).

**Colorado — SB 205 → SB 189:**
- SB 205 (the original algorithmic discrimination prevention bill) was **gutted** during the 2026 session.
- Replaced by **SB 189**, a disclosure-only measure. **Signed 14 May 2026**, effective **1 January 2027**.
- SB 189 requires disclosure of AI use in "consequential decisions" but imposes no technical obligations — no risk assessment, no bias testing, no code-level requirements.
- **Recommendation:** No code-scanning value. Deprioritise entirely.
- Source: Holland & Knight legislative update ([source](https://www.hklaw.com/en/insights/publications/2026/05/colorado-ai-legislation-2026-session-update)).

**South Korea — AI Basic Act:**
- In force since **22 January 2026**, with a grace period extending to approximately **January 2027**.
- Localised market requiring Korean language support. No English-language compliance tooling demand identified.
- **Recommendation:** Not addressable for Regula given current capabilities and market position.
- Source: Library of Congress report on South Korea AI Basic Act ([source](https://www.loc.gov/item/global-legal-monitor/2026-01-28/south-korea-ai-basic-act-enters-into-force/)).

**United Kingdom:**
- No AI-specific primary legislation equivalent to the EU AI Act.
- **Data (Use and Access) Act (DUAA):** Section 80 Automated Decision-Making provisions in force since **5 February 2026**. These strengthen individual rights regarding automated decisions but do not create a code-scanning compliance market.
- **ICO statutory code on AI:** In development, not yet published. Will provide sector-specific guidance but is expected to be principles-based rather than prescriptive.
- **Recommendation:** Watch only.
- Source: Bratby Law analysis of DUAA S.80 implications ([source](https://www.bratbylaw.com/duaa-section-80-adm-provisions/)).

### 1.5 Investment Recommendation

| Priority | Area | Action | Rationale |
|---|---|---|---|
| **Primary** | EU AI Act high-risk (Art 6-15) | Active development | Core market. Omnibus extends timeline but does not reduce obligation scope. |
| **Begin now** | EN 18228/18282 mapping | Category-level traceability matrix | Standards in Public Enquiry — structure is stable enough to begin mapping. Refine post-publication. |
| **Quick win** | Art 50 transparency | Detect missing watermarking, disclosure patterns | Code of Practice now final. Low engineering effort, high signalling value. |
| **Watch** | Brazil PL 2338 | Monitor only | Unconfirmed vote, elections block window. |
| **No-go** | Colorado SB 189 | Ignore | Disclosure-only, no code-scanning value. |
| **No-go** | South Korea | Ignore | Localised market, language barrier. |
| **Watch** | UK ICO code | Monitor only | No prescriptive requirements yet. |

---

## 2. Detection Technology and Methodology

### 2.1 Tree-Sitter as a Parsing Foundation

**Maturity and compatibility:**
- Tree-sitter grammars are mature for Java (v0.23.5), Go, Rust, Python, C/C++, JavaScript/TypeScript, and many others.
- The Kreuzberg language pack provides **305+ languages** with pre-compiled grammars.
- Tree-sitter is implemented as a C library with bindings for Python, Rust, Node.js, and others. The C extension is **vendorable**, making it compatible with Regula's zero-dependency constraint (stdlib-only Python core, but C extensions that ship with the tool are acceptable as they do not add PyPI dependencies).
- Source: [tree-sitter.github.io](https://tree-sitter.github.io/tree-sitter/); Kreuzberg project documentation.

**Capability boundaries:**
- Tree-sitter produces a **Concrete Syntax Tree (CST)**, not a Control Flow Graph (CFG) or dataflow graph.
- It excels at structural pattern matching: finding function calls, class definitions, decorator patterns, import statements, configuration values.
- It does NOT provide: inter-procedural dataflow, taint analysis, alias analysis, or call-graph construction.
- **Tree Climber** (academic project) builds CFGs on top of tree-sitter output, but only for C.
- **Tree-Sitter Analyzer** extracts structural intelligence (complexity metrics, dependency graphs) for 13 languages.

**Implication for Regula:** Tree-sitter is the right foundation for structural pattern detection (which is what Regula's 389 patterns currently do via regex). It would improve precision by eliminating false positives from comments, strings, and dead code. It does NOT unlock dataflow analysis — that requires a fundamentally different architecture.

### 2.2 Dataflow Analysis Platforms

**Joern:**
- Most mature open-source Code Property Graph (CPG) and dataflow platform.
- Supports C/C++, Java, JavaScript, Python, Kotlin.
- **JVM dependency** — violates Regula's zero-dependency constraint.
- Source: [joern.io](https://joern.io/).

**CodeQL:**
- GitHub's mature static analysis platform with strong Python dataflow support.
- Requires the GitHub toolchain (CodeQL CLI + database creation).
- **Violates zero-dependency constraint** and requires network access for database schema updates.
- Published precision: **0.938** on enterprise codebases (per GitHub Advanced Security benchmarks).
- Source: [codeql.github.com](https://codeql.github.com/).

**Implication for Regula:** Neither Joern nor CodeQL is viable as a bundled dependency. However, Regula could optionally consume their output (e.g., reading a SARIF file from a CodeQL run) as an integration path rather than a core dependency.

### 2.3 Article 14 Human Oversight — Open Research Gap

- **No published work** exists on detecting Article 14 human oversight compliance via static analysis.
- This is an **open research gap** and a genuine Regula differentiator.
- Human oversight patterns that ARE detectable in code: approval gates before model predictions are actioned, human-in-the-loop callback mechanisms, override interfaces, kill switches, escalation paths, confidence threshold routing.
- These are structural patterns (function signatures, API call sequences, configuration values) that tree-sitter or regex can match.
- This remains the strongest technical moat: Regula is the only tool attempting to map code patterns to Art 14 compliance requirements.

### 2.4 LLM-Assisted Static Analysis

The field consensus is converging on **hybrid architectures**: deterministic core + LLM reasoning layer.

**Key research findings:**
- **IRIS (2025):** LLM-assisted vulnerability detection found **35% more vulnerabilities** than CodeQL alone on the same codebase. Deterministic analysis provided the scaffolding; LLM identified semantic patterns that rules missed.
- **MoCQ (2026):** Generated **46 new detection patterns** via LLM analysis of vulnerability databases, with human review as quality gate.
- **ZeroFalse (2025):** Achieved **F1 score of 0.912** on vulnerability classification by using LLM to filter false positives from deterministic scanners.
- **KCode (2026):** Demonstrated **local LLM inference on consumer GPU** (RTX 3060-class) for code analysis, eliminating cloud dependency.

**Counter-narrative:** LLMs produce **inconsistent results** — measured at **23% classification variance** across repeated runs on identical inputs (per academic benchmarks). This means LLM results are not reproducible, which undermines audit and compliance use cases.

**Implication for Regula:** Regula's zero-dependency, fully offline, deterministic position is **strengthened** by this research. The deterministic core is the right architectural base for compliance (where reproducibility is non-negotiable). An optional LLM tier (following the KCode local-inference architecture) could add semantic reasoning without compromising the core differentiator. This would be a premium feature, not a replacement for the pattern engine.

### 2.5 Industry Benchmarks and False Positive Baselines

**False positive rates:**
- Untuned SAST tools: **60-90% false positive rate** (industry consensus).
- Tuned commercial SAST (Snyk Code, Checkmarx SAST 2.0): **10-20%** after configuration and suppression.
- Bandit (Python-specific): approximately **25%** FP rate on typical codebases.
- CodeQL enterprise: published precision **0.938** (i.e., ~6.2% FP rate).

**Benchmark corpus norms:**
- **NIST SARD/Juliet:** 64,000+ test programs across multiple languages and CWE categories. The standard academic benchmark corpus.
- **CASTLE:** 250 C programs with known vulnerabilities. Smaller but more curated.
- **SastBench (2026):** 2,737 samples with a realistic **8:1 false positive to true positive ratio**, making it the first benchmark to model real-world class imbalance.
- **Inter-rater agreement:** Kappa >= 0.75 is the threshold for credible benchmark results. Below this, the ground truth labels are too noisy to draw conclusions.

**Publication norms for credible benchmarks:**
1. Published corpus (not proprietary test suite)
2. Realistic class imbalance (not 50/50 TP/FP)
3. Second rater or adjudication process for ground truth
4. Per-CWE/per-category granularity (not just aggregate metrics)
5. Default configuration (no custom tuning for the benchmark)
6. Version-locked reproducibility (tool version, corpus version, date)

**What Regula needs to publish credible benchmarks:**
1. A published test corpus (could be derived from NIST SARD adapted for AI Act categories, or a bespoke corpus with CC-BY licence)
2. Realistic class imbalance reflecting actual codebases
3. A second human rater for ground truth validation
4. Per-category precision/recall reporting (not just aggregate)
5. A comparison baseline (e.g., Bandit, Semgrep, or manual review)

---

## 3. Competitive Refresh (June 2026)

### 3.1 Direct Competitors — Code Scanners

**AIR Blackbox (v1.13.0, 5 June 2026):**
- 51 checks covering Articles 9-15
- 7 framework trust layers
- 11 PyPI packages (significant dependency footprint)
- HMAC-SHA256 evidence chains (cryptographic integrity for audit trails)
- Visible on Hacker News
- **Python-only** language support
- Published a comparison article on AI Act compliance tools that does **NOT mention Regula** — indicating either unawareness or deliberate exclusion.
- Source: AIR Blackbox GitHub repository and PyPI listings.

**ArkForge:**
- MCP-first architecture with 10 tools and 16 framework mappings
- GDPR + AI Act dual scan capability
- Free tier + EUR 29/month paid tier
- Listed on PulseMCP registry
- Key competitive feature: "Trust Layer" with cryptographic certification
- Source: ArkForge documentation and PulseMCP listing.

**Systima Comply:**
- Uses **tree-sitter AST** for genuine structural analysis (not regex)
- 37+ framework mappings
- TypeScript/JavaScript and Python support
- GitHub Action native integration
- This is the most technically sophisticated code-scanning competitor.
- Source: Systima Comply GitHub repository.

### 3.2 Adjacent Competitors

**Microsoft AutoGen Team (AGT):**
- **3,300+ GitHub stars** in 2 months (massive visibility)
- MIT licence, 7 packages, 60+ contributors, 9,500+ tests
- **Runtime-only** — no static analysis capability
- Not a direct competitor, but occupies mindshare in "AI governance tooling"
- Source: [github.com/microsoft/autogen](https://github.com/microsoft/autogen).

**Giskard (v3 + Giskard Guards, May 2026):**
- Repositioned as "Europe's first independent sovereign guardrail platform"
- Runtime testing and guardrails, not code scanning
- Significant brand authority in the EU AI governance space
- Source: Giskard blog, May 2026 announcement.

**VerifyWise:**
- BSL 1.1 licence (source-available, not truly open-source)
- 16+ governance modules, 24+ framework mappings
- Published an Omnibus-responsive blog post
- Governance platform (questionnaires, documentation management), NOT a code scanner
- Source: VerifyWise documentation.

**SonnyLabs:**
- **STALE** — last update December 2025. MCP tool likely abandoned.
- Deprioritise from competitive monitoring.

### 3.3 Enterprise SaaS Platforms

- **Credo AI:** $30K-$150K/year. Governance and risk platform. No code scanning.
- **Holistic AI:** Enterprise governance and auditing. No code scanning.
- **Vanta:** Added AI Act compliance module. GRC platform, no code scanning.
- None of these enterprise players do static code analysis. They occupy a fundamentally different market segment (governance platforms for compliance officers) vs. Regula's segment (developer tools for engineers).

### 3.4 New Entrants (Identified June 2026)

| Entrant | Approach | Threat Level | Notes |
|---|---|---|---|
| **CompliPilot** | 200+ checks, free scan entry point | Medium | Closest to code-scanning but unverified depth |
| **ComplianceRadar** | URL-based scanning, claims Omnibus-updated rules | Low | Not code scanning — analyses public-facing properties |
| **AgentBouncr** | MIT licence, runtime governance for AI agents | Low | Runtime only, different segment |
| **Fronterio** | Deployer-focused compliance tool | Low | Questionnaire/documentation, not code |
| **ActReady** | SMB-focused, 6-question risk classifier | Low | Simplified self-assessment, not code |

### 3.5 Competitive Intelligence Summary

**No code scanner has verifiably shipped Omnibus-updated scanning rules.** ComplianceRadar claims Omnibus updates but operates on URL-based scanning, not code analysis. Blog posts about the Omnibus (VerifyWise, others) are marketing, not product updates.

**MCP integration is table stakes** for discoverability in the AI tooling ecosystem. Regula HAS an MCP server but is **NOT listed on any registry** (official MCP registry, mcp.so, Smithery, PulseMCP). This is a critical visibility gap.

**Market segmentation:**
1. **Code scanners:** Regula, AIR Blackbox, ArkForge, Systima Comply, CompliPilot
2. **Runtime governance:** Microsoft AGT, Giskard Guards, AgentBouncr
3. **Governance platforms:** Credo AI, Holistic AI, Vanta, VerifyWise
4. **Questionnaire/template tools:** Fronterio, ActReady, free EU Commission checker

Regula competes in segment 1 only. Cross-segment comparisons are misleading.

**Regula's confirmed unique advantages:**
- **8 programming languages** (vs Python-only for AIR, TS/JS/Python for Systima)
- **389 detection patterns** (highest published count in the code-scanner segment)
- **Zero external dependencies** (no other tool claims this)
- **Fully offline operation** (critical for air-gapped and sovereign environments)
- **Evidence packs** (structured, exportable compliance artefacts)

---

## 4. Distribution and Discovery

### 4.1 Curated Lists

**awesome-static-analysis:**
- Maintained YAML file at `data/tools/`. PRs are the submission mechanism.
- Acceptance rate is high for well-formatted, relevant tools.
- Regula qualifies under the "security" or "compliance" category.
- Source: [github.com/analysis-tools-dev/static-analysis](https://github.com/analysis-tools-dev/static-analysis).

**awesome-eu-ai-act:**
- Two active lists: GenAI-Gurus and morganrcu. Both accept PRs.
- Source: GitHub search for "awesome-eu-ai-act".

### 4.2 MCP Registries

| Registry | Size | Submission method | Notes |
|---|---|---|---|
| **Official MCP registry** | Growing | `server.json` manifest + CLI publish | Requires manifest file in repo |
| **mcp.so** | 20,000+ servers | GitHub issue submission | Largest directory |
| **Smithery** | 7,000+ servers | CLI publish | Developer-focused |
| **PulseMCP** | Smaller | Direct submission | ArkForge is listed here |

**Action required:** Regula's MCP server exists but is unlisted. Listing on at least the official registry, mcp.so, and Smithery would address the discoverability gap identified in Section 3.5.

### 4.3 Hacker News Analysis

**Baseline expectations:**
- Median Show HN score: **2 points** (i.e., most posts get almost no engagement)
- Volume: approximately **200 posts per day**
- Conversion: each upvote correlates with approximately **1.4 GitHub stars**
- Half-life of a front-page post: approximately **24 hours**
- Optimal posting slot: **Monday 00:00 UTC** (Sunday evening US time)
- Front page requires approximately **30-50 upvotes in the first hour**

**Regula's HN history:**
- 3 posts, scoring 1-2 points each
- This is the **median outcome**, not a failure — most Show HN posts receive minimal engagement
- However, title framing and timing likely contributed to underperformance
- **Technical framing beats compliance framing** on HN. "Static analysis for AI Act" is less compelling than "We detect human oversight gaps in ML pipelines using AST patterns"

### 4.4 Generative Engine Optimisation (GEO)

AI citation patterns are **diverging from traditional Google rankings**. Key findings:

- AI systems (ChatGPT, Perplexity, Claude) cite sources differently from Google's PageRank algorithm.
- **Key tactics that improve AI citations:**
  1. Allow AI crawlers in robots.txt — Regula does this (partially; see gaps below)
  2. Answer-first content structure (lead with the conclusion, not the preamble)
  3. HTML tables for structured data (improves extraction)
  4. FAQ schema markup — Regula has this on the landing page
  5. Submit sitemap to Bing Webmaster Tools (Bing powers multiple AI search backends)

**robots.txt gaps identified:**
- **Missing:** `OAI-SearchBot`, `Claude-SearchBot`, `Claude-User`, `Perplexity-User`
- **Deprecated entry still present:** `claude-web` (superseded by `Claude-SearchBot` and `Claude-User`)
- These gaps mean some AI search crawlers may not be indexing getregula.com content.

### 4.5 Industry Channels

**IAPP AI Governance Vendor Report:**
- This is **THE channel** for reaching compliance buyers. The IAPP Vendor Report is consulted by compliance officers, DPOs, and legal teams when evaluating tools.
- Contact: acasovan@iapp.org to request inclusion.
- Source: [iapp.org/resources/article/ai-governance-vendor-report/](https://iapp.org/resources/article/ai-governance-vendor-report/).

**Conferences:**
- **Responsible AI Summit** (September 2026) — primary EU AI governance event
- **4th AI Legal Brussels** — legal/compliance focused, good for credibility-building

**LinkedIn:**
- Text-only posts perform best (no images, no carousels)
- AI-generated content receives **47% less reach** per algorithm updates
- Human-sounding, specific regulatory insight posts outperform generic "AI compliance" content
- Effective formula: specific article number + practical implication + one actionable takeaway

### 4.6 Bing Webmaster Tools

- Whether Bing Webmaster Tools has getregula.com sitemap indexed is **unverified**. This should be checked and resolved — Bing powers AI search results for Copilot, DuckDuckGo, and several AI assistants.

---

## 5. Product-Market Fit and the Non-Technical Buyer

### 5.1 Who Is Actually Buying

The primary buyer at an SME is the **founder or CTO reacting to a procurement questionnaire**, not a dedicated compliance officer.

- They receive a questionnaire from a larger customer asking "How do you comply with the AI Act?"
- They want an **answer** (a one-shot evidence pack), not a platform to learn and operate.
- They are not looking for a CLI tool — they are looking for a problem solved.
- The evidence pack IS the product for this buyer. The CLI is the delivery mechanism.

### 5.2 How Non-Technical Buyers Currently Solve This

Non-technical buyers compare:
1. **SaaS governance platforms** (Credo AI at $30K+, Holistic AI, Vanta)
2. **Consulting firms** ($500-$2,000/day for AI Act gap analysis)
3. **Template packs** ($49-$997 for Word/Excel compliance documentation kits)
4. **Free self-assessment tools** (EU Commission AI Act compliance checker, VerifyWise, ArkForge free tier)

They do **NOT** compare CLI tools. "Install Python, run a command, read JSON output" is not in their consideration set.

### 5.3 Minimum Viable Surface for Non-Technical Buyers

A **browser-based self-assessment flow** leading to a **downloadable PDF report** is the minimum viable surface to reach this buyer segment.

**Pattern demonstrated by:**
- **EuroComply:** Web form → AI Act risk classification → downloadable compliance checklist
- **EU Commission checker:** 6 questions → risk classification → guidance document
- **ActReady:** 6-question classifier → SMB-appropriate action plan

**Key elements:**
1. No installation required
2. Answers 3-5 questions
3. Receives a branded, professional PDF report
4. Clear next step (full scan, evidence pack, or consulting referral)

### 5.4 Website Credibility Signals

Compliance buyers specifically look for:
- **Compliance badges near CTAs** (ISO references, framework logos, regulatory article citations)
- **Outcome-focused case studies** ("Company X generated their Art 11 documentation in 4 hours" — even if anonymised)
- **Data residency statements** (where does data go? For Regula: nowhere — fully offline)
- **Regulatory specificity** (cite article numbers, not vague "AI Act compliance")
- **Free entry point** (free tier, free assessment, free report — lowers trust barrier)

**Exemplars:**
- **Credo AI:** Enterprise credibility through advisory board, SOC 2 badge, named customers
- **Vanta:** Trust centre, compliance badge ecosystem, free trial
- **EuroComply:** Simple entry point, immediate value delivery
- **Holistic AI:** Published research, regulatory body partnerships

---

## 6. Business Model Evidence

### 6.1 Pricing Benchmarks

**Template/documentation tier ($49-$997):**
- Established market for AI Act compliance documentation kits
- EUR 49-149 one-time pricing for Regula evidence packs is viable within this tier
- Differentiation must be in **artefact quality**: code-backed evidence is something Word templates cannot produce
- The "code-backed" claim only holds if the evidence pack clearly traces findings to specific code locations with verifiable timestamps

**Free alternatives:**
- EU Commission self-assessment checker (free)
- VerifyWise (free, BSL 1.1)
- ArkForge free tier
- Free entry point is table stakes. Regula's free tier must be genuinely useful, not a crippled demo.

### 6.2 Open-Source Monetisation Precedents

**Snort (time-delayed rule access):**
- Paid subscribers: immediate access to new detection rules
- Free users: 30-day delay on rule updates
- Pricing: $29.99/year (home), $300/year (commercial)
- **Directly applicable** to Regula: new pattern rules for emerging AI Act requirements could follow this model.
- Source: [snort.org/faq/what-is-the-community-ruleset](https://snort.org/faq/what-is-the-community-ruleset).

**ClamAV (open engine, paid signatures):**
- Open-source scanning engine, freely available
- Premium signature sets (Cisco Talos) for enterprise
- Applicable pattern: open pattern engine, premium regulatory intelligence layer

**Dual licensing (AGPL open core):**
- Proven model in developer tools
- One reported case of **$350K annual revenue** from AGPL open core (unverified source, commonly cited in open-source business discussions)
- AGPL ensures that hosted/SaaS derivatives must open-source their changes, driving commercial licence purchases

### 6.3 Monetisable Assets

**Framework crosswalks:**
- Mapping between regulatory frameworks (AI Act ↔ NIST AI RMF ↔ ISO 42001 ↔ GDPR) is a standalone sellable asset
- **Hyperproof** and **Apptega** demonstrate demand for compliance framework mapping tools
- Regula's `references/framework_crosswalk.yaml` is a foundation but would need significant expansion

**ArkForge's Trust Layer precedent:**
- Cryptographic certification of compliance state
- This is a certification-adjacent service — not just scanning, but attesting
- Demonstrates market willingness to pay for verifiable compliance artefacts (not just reports)

### 6.4 Pricing Recommendation Framework

| Tier | Price | What the buyer gets |
|---|---|---|
| **Free/Open** | $0 | CLI scanner, basic patterns, community rules (30-day delay) |
| **Pro** | EUR 49-149 one-time | Full pattern set, evidence pack generation, PDF reports |
| **Team** | EUR 29-49/month | CI/CD integration, priority rules, framework crosswalks |
| **Enterprise** | Custom | Dedicated pattern development, on-prem support, audit trail integration |

This is a framework, not a recommendation. Pricing requires validation against actual buyer willingness-to-pay.

---

## 7. Open Research Questions

The following items could not be verified during this research phase:

1. **Brazil PL 2338 vote result:** Plenary vote was scheduled for 27 May 2026. Outcome unconfirmed. Multiple searches returned no post-vote reporting.

2. **EP plenary vote date for Omnibus formal adoption:** Expected June 2026 per Council press release, but exact date not confirmed in any source found.

3. **prEN 18228/18282 exact Enquiry close dates:** Public Enquiry phase confirmed, but the precise close dates for national body comments were not found in publicly accessible CEN/CENELEC documents.

4. **OJEU citation timeline for harmonised standards:** Estimated H1 2027 based on typical harmonisation timelines. No official AI Office or Commission statement on expected citation date found.

5. **Bing Webmaster Tools indexing status:** Whether getregula.com sitemap is submitted and indexed in Bing Webmaster Tools requires account access to verify. This affects AI search visibility (Copilot, DuckDuckGo, etc.).

6. **Exact GitHub star counts for competitors:** AIR Blackbox, ArkForge, and Systima Comply star counts were not retrievable via web search alone. Manual verification against GitHub required.

7. **Competitor rule updates vs. marketing:** Whether any competitor has actually updated their scanning rules (code changes, not just blog posts) to reflect Omnibus changes. Would require inspecting their repositories' commit history. No evidence of shipped Omnibus-updated rules found for any competitor.

---

## Sources Index

### Regulatory
- Council of the EU press release, 7 May 2026 — Omnibus provisional agreement
- Gibson Dunn — EU AI Act Omnibus analysis (May 2026)
- Latham & Watkins — EU AI Act Omnibus overview (May 2026)
- White & Case — AI Act cybersecurity requirements
- Bird & Bird — Harmonised standards tracker
- AI Office — Code of Practice on AI Content Marking, Final (10 Jun 2026)
- AI Office — Art 50 transparency guidelines consultation (closed 3 Jun 2026)
- AI Office — Art 6 high-risk classification guidelines consultation (open until 23 Jun 2026)
- Adam Leon Smith substack — AI Standards Watch series
- AI Assurance Institute — EN 18228 commentary
- Inside Privacy — Brazil AI regulation update
- Holland & Knight — Colorado AI legislation 2026 session
- Library of Congress — South Korea AI Basic Act
- Bratby Law — DUAA S.80 ADM provisions

### Technology
- tree-sitter.github.io — Official documentation
- Kreuzberg language pack — 305+ grammar compilation
- Joern (joern.io) — Code Property Graph platform
- CodeQL (codeql.github.com) — GitHub static analysis
- IRIS (2025) — LLM-assisted vulnerability detection
- MoCQ (2026) — LLM-generated detection patterns
- ZeroFalse (2025) — LLM false positive filtering
- KCode (2026) — Local LLM code analysis
- NIST SARD/Juliet — 64K test program corpus
- SastBench (2026) — Realistic class imbalance benchmark

### Competitive
- AIR Blackbox — GitHub, PyPI (v1.13.0, 5 Jun 2026)
- ArkForge — PulseMCP listing, documentation
- Systima Comply — GitHub repository
- Microsoft AutoGen Team — github.com/microsoft/autogen
- Giskard — v3 + Guards announcement (May 2026)
- VerifyWise — Documentation, Omnibus blog
- CompliPilot, ComplianceRadar, AgentBouncr, Fronterio, ActReady — Various (Jun 2026)

### Distribution
- awesome-static-analysis — github.com/analysis-tools-dev/static-analysis
- MCP registries — Official, mcp.so, Smithery, PulseMCP
- IAPP AI Governance Vendor Report — iapp.org
- Snort community ruleset — snort.org
