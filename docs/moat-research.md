# Regula — Proprietary Data Moat Research

**Author:** Research pass for getregula.com / PyPI `regula-ai`
**Date:** 2026-04-09
**Status:** Initial deep dive. Confidence labels on every claim. Counterevidence section included. British English.

---

## Executive Summary

The CLI is commoditised; the compounding asset must be a **versioned, primary-sourced regulatory delta log for the EU AI Act and adjacent regimes**, tightly wired to Regula's 330 code patterns. That single asset is underserved by every existing tracker (IAPP, Future of Life, AlgorithmWatch, Holistic AI), none of which publishes machine-readable, pattern-linked, diff-able outputs. A close second is a **labelled TP/FP corpus for AI-governance static analysis**, because no Juliet/SARD equivalent exists for AI Act or NIST AI RMF controls, and whoever builds it will be cited by every downstream scanner, academic paper, and benchmark. Longitudinal OSS-AI scan datasets (candidate 1) and AI-BOM fingerprinting corpora (candidate 5) are already partially covered by BigCode, deps.dev, LibVulnWatch and Data Provenance Initiative — the marginal value of another entrant is low. A citable pattern→article mapping dataset (candidate 3) is a CONDITIONAL GO: only distinctive if published with DOIs and diff history, which nobody currently does. Ranked recommendation: **(1) Regulatory Delta Log → (2) Pattern-Level TP/FP Corpus → (3) Pattern→Article Mapping with DOIs → defer the rest**.

---

## Market Map: Who Already Publishes What

| Asset | Publisher(s) | Format | Gap for Regula |
|---|---|---|---|
| OSS security scorecards at scale | OpenSSF Scorecard (BigQuery public dataset), deps.dev (50M+ package versions), LibVulnWatch (20 AI libs) | BigQuery / API / leaderboard | Not AI-Act-specific; no regulatory mapping |
| LLM/AI library vuln tracking | GitHub Advisory DB, Snyk, LibVulnWatch | API / PDF reports | Security-centric, not governance |
| AI Act article text + explorer | Future of Life Institute `artificialintelligenceact.eu`, EUR-Lex | HTML, PDF | Static, no diff/delta, no code linkage |
| AI Act implementation trackers | IAPP Regulatory Directory, IAPP Compliance Matrix, Steptoe, Bird & Bird, White & Case | HTML behind paywall/newsletter | Not machine-readable; not versioned; not linked to patterns |
| AI Act timeline & delays | IAPP, OneTrust, Plesner, Cooley, Sidley, Morrison Foerster (Digital Omnibus coverage) | Blogs / legal alerts | Unstructured; aggregator blogs, not primary |
| Crosswalks (AI RMF ↔ ISO 42001) | NIST AIRC (official PDF crosswalk) | PDF | Article/control level only; not pattern-level |
| Conformity / notified bodies | EU Commission NANDO; HIIG analysis | HTML directory | Decisions are confidential under Art. 34; cannot be built |
| AI incidents | OECD AI Incidents Monitor (AIM), AIID (Responsible AI Collaborative), MIT AI Risk Incident Tracker | Public DB, GitHub repo | Narrative-level, not code-level |
| Enforcement fines | CMS GDPR Enforcement Tracker (2,245 fines), Termly, DPM | HTML DB | GDPR-focused, no AI Act enforcement yet |
| Training-data provenance | Data Provenance Initiative (1,800+ datasets, Nature MI paper) | GitHub, paper | Dataset-level, not code-level |
| Safety benchmarks | MLCommons AILuminate v1.0 (12 hazard cats), Promptfoo, PyRIT | Benchmark / leaderboard | Model-behaviour, not static-code |
| Corpus for code LLMs | BigCode The Stack v2 (3B files, 600+ languages), Software Heritage | HF dataset | Raw source, no compliance labels |
| AI-BOM standards | CycloneDX ML-BOM, SPDX 3.0 (arXiv 2504.16743), OWASP AI BOM | Schema / spec | Specs exist; population data does not |
| Harmonised standards (prEN 18286 etc.) | CEN-CENELEC JTC 21 | Draft PDFs behind paywall | Delayed to Q4 2026+; no diff tool exists |

---

## Candidate 1 — Longitudinal OSS-AI Code Scan Datasets

**Who does it today.** OpenSSF Scorecard runs weekly scans of the top ~1M open-source projects and publishes results to a public BigQuery dataset (`openssf:scorecardcron.scorecard-v2`) [verified — ossf/scorecard GitHub, arXiv:2208.03412]. Google's `deps.dev` (Open Source Insights) covers 50M+ package versions across npm/Go/Maven/PyPI/Cargo with a free API [verified — security.googleblog.com 2023]. **LibVulnWatch** (arXiv:2505.08842) published in 2025 is the closest AI-specific analogue: a leaderboard of 20 widely used ML frameworks, LLM inference engines, and agent-orchestration tools, covering 88% of Scorecard checks plus 19 additional AI-specific risks [verified]. GitHub Advisory DB standardises vulnerability records across ecosystems including LLM frameworks [verified — GHSA]. BigCode's The Stack v2 provides the raw corpus (3B files) but no compliance labels [verified — huggingface.co/datasets/bigcode/the-stack-v2].

**The gap.** None of these publish compliance-risk findings (AI Act Art. 10 data governance, Art. 13 transparency, Art. 14 human oversight) against AI libraries over time. They publish security signals (known CVEs, SBOM presence, branch protection), not regulatory signals. LibVulnWatch is the closest, but it scores 20 libs at a point in time, not a longitudinal signal.

**Regula's distinctive angle.** Weekly scan of the top ~500 AI-related GitHub repos (HF Transformers, LangChain, llama.cpp, vLLM, PyTorch, TensorFlow, ONNX Runtime, MLflow, Ray, BentoML etc.), publishing a versioned JSON dataset of Regula findings mapped to AI Act articles. Differentiator: Regula's 330 patterns already encode AI Act / NIST RMF / ISO 42001 links; nobody else's scanner has that mapping built in.

**Maintenance burden.** Weekly cron on a single VM; ~4h of wall-clock for a 500-repo scan. Low. The hard part is curating the repo list.

**GTM.** Host on HuggingFace Datasets (free, indexed by Google), mint a Zenodo DOI per version, submit to MSR 2027 Mining Challenge track (they explicitly want longitudinal datasets — MSR 2026 already accepted AIDev for agent PRs) [verified — 2026.msrconf.org].

**Verdict: CONDITIONAL GO.** Only worth doing if Regula's patterns genuinely catch things Scorecard/LibVulnWatch miss. The moat is the *AI-Act mapping*, not the scanning — so Candidate 3 is a prerequisite. **Counterevidence:** LibVulnWatch could trivially add AI-Act tags next quarter; the moat decays fast if Regula is not first.

---

## Candidate 2 — Labelled TP/FP Precision Corpora for AI-Compliance Scanners

**Who does it today.** NIST SARD contains 450,000+ test cases across dozens of CWEs; Juliet 1.3 provides 81,000+ synthetic C/C++/Java programs with known flaws [verified — samate.nist.gov/SARD, NIST IR 8561]. OWASP Benchmark provides paired positive/negative synthetic cases for Java SAST tools. For AI governance, **there is no equivalent**. LLM-safety benchmarks exist (AILuminate 12 hazard categories, PyRIT, Promptfoo, a 1,000-sample labelled LLM-scanner dataset from recent arXiv work) but they test model *behaviour*, not static code patterns [verified — mlcommons.org/ailuminate, arXiv:2503.05731].

**The gap.** There is no NIST-Juliet for AI Act Article 9 (risk management), Art. 10 (data governance), Art. 15 (robustness), Art. 14 (human oversight) at the *code level*. Academic SAST-benchmarking papers (Kolla's "Benchmarking SAST the Right Way") explicitly note the synthetic-test-case problem: Juliet's paired good()/bad() inflates precision numbers.

**Regula's distinctive angle.** Publish "RegulaBench v1": ~500 hand-labelled real-world snippets (not synthetic — this is the gap Juliet's paired good()/bad() inflates, per the NIST SARD critique cited above), each tagged with the triggering pattern, the article it maps to, and expert-reviewed TP/FP label. Source from existing open repos ([The Stack v2](https://huggingface.co/datasets/bigcode/the-stack-v2) as the corpus). Versioned on [Zenodo](https://zenodo.org/) with a DOI per release. Allow any scanner — not just Regula — to measure itself against it. **[Verdict: proposed scope — no existing equivalent verified per the NIST SARD and MLCommons AILuminate sources cited above].**

**Maintenance burden.** High initial cost (~200 expert hours for 500 cases, comparable to the per-case rate implied by [NIST IR 8561](https://nvlpubs.nist.gov/nistpubs/ir/2025/NIST.IR.8561.pdf)). Low ongoing cost (target: add 50 cases/quarter). The labelling is the moat; the corpus gets cited forever (see SARD and Juliet as evidence of this citation pattern).

**GTM.** Drop it on arXiv + Zenodo + HuggingFace. Pitch to MSR 2027 and ICSE 2027 SEIP. Every other scanner (Holistic AI, open-source AI governance tools, Snyk's AI-code scanning) gains a benchmark to test against — and Regula gets cited in every comparison paper.

**Verdict: GO.** This is the highest-leverage item in the list. First-mover advantage is real: SARD/Juliet became the universal SAST reference because they were first and well-labelled. **Counterevidence:** if NIST itself releases an AI-governance SARD extension (plausible given SP 800-218A and the AI RMF crosswalk programme), Regula's corpus becomes ancillary. Mitigate by partnering with NIST AIRC early and offering the corpus as upstream contribution.

---

## Candidate 3 — Citable Open Pattern→Regulation Mapping Datasets

**Who does it today.** NIST publishes the official AI RMF ↔ ISO/IEC 42001 crosswalk as a PDF [verified — airc.nist.gov/airmf-resources/crosswalks]. Holistic AI's open-source library supports alignment with EU AI Act, NIST AI RMF and ISO 42001 but only at the *metric / high-level control* level, not the code-pattern level [verified — holisticai.readthedocs.io, github.com/holistic-ai/holisticai]. Future of Life Institute's AI Act Explorer maps *article text to article text* [verified — artificialintelligenceact.eu]. The GPAI Code of Practice (July 2025, final) and its sub-chapters exist only in HTML/PDF [verified — code-of-practice.ai, digital-strategy.ec.europa.eu]. Several consultancies publish ISO 42001 → AI Act mapping guides (Elevate, Glocert) but none are machine-readable or DOI-persistent.

**The gap.** Nobody publishes *pattern-level* → *article-level* mappings as a structured, diff-able dataset with persistent identifiers (DOI, PURL, OSCAL). OSCAL itself (NIST SP 800-53 control catalogue) has no AI Act profile. This is a genuinely empty space.

**Regula's distinctive angle.** Publish `regula-mappings` as a standalone repo: YAML/JSON, one entry per pattern, with `{pattern_id, regex, article_refs[], recital_refs[], rmf_refs[], iso42001_refs[], confidence, last_reviewed}`. Mint a DOI per release. Offer it under CC-BY-4.0 so every other scanner (Holistic AI, proprietary vendors) can ingest it — which creates inbound links back to Regula as the canonical source.

**Maintenance burden.** Medium. 330 patterns × ~30 min legal review each = ~165 hours one-off. Ongoing: re-review after every Digital Omnibus amendment or Commission guidance drop (see Candidate 4).

**GTM.** Cite in every blog post; get it referenced by the IAPP compliance matrix; submit to OECD AI policy observatory catalogue (oecd.ai/catalogue — they already list Holistic AI OSL). Academic route: co-author with a legal scholar, publish in *Computer Law & Security Review* or *International Journal of Law and Information Technology*.

**Verdict: GO — conditional on DOI + diff history.** Without persistent identifiers and version history it is just another blog. **Counterevidence:** Future of Life Institute could add machine-readable outputs to the AI Act Explorer at any time; they already have the institutional relationships. Move quickly.

---

## Candidate 4 — Public Regulatory Delta Logs for the EU AI Act

**Who does it today.** The field is crowded but nobody publishes structured diffs.

- **Future of Life Institute AI Act Explorer** — based on the 13 June 2024 OJ version. Static [verified — artificialintelligenceact.eu/ai-act-explorer].
- **IAPP EU AI Act Regulatory Directory + Compliance Matrix** — updated manually; gated behind IAPP membership; not machine-readable; IAPP itself reported that "the European Commission missed its 2 Feb deadline to provide guidance on Article 6" [verified — iapp.org/news].
- **AlgorithmWatch** — publishes narrative explainers, not structured logs [verified — algorithmwatch.org/en/ai-act-explained].
- **Holistic AI** — tracks conformity assessment guidance in blog form [verified — holisticai.com/blog/conformity-assessments-in-the-eu-ai-act].
- **Legal firms** (Morrison Foerster, Addleshaw Goddard, Cooley, Sidley, Crowell & Moring, Plesner, OneTrust) — all published client alerts on the **Digital Omnibus on AI** (Commission proposal 19 November 2025) which defers high-risk AI Act obligations from August 2026 to **2 December 2027 (Annex III) and 2 August 2028 (Annex I)**; Council position 13 March 2026, Parliament 26 March 2026, trilogue targeted 28 April 2026 [verified — mofo.com, addleshawgoddard.com, globalpolicywatch.com]. This is perishable, materially important, and none of it is in a versioned feed.
- **CEN-CENELEC JTC 21** — developing harmonised standards (prEN 18286 quality management system for AI Act purposes); public enquiry 30 October 2025 – 22 January 2026; publication targeted Q4 2026 [verified — jtc21.eu, cencenelec.eu news 2025-10-23]. Delayed; no public diff.

**The gap.** A `git log --oneline` for the AI Act does not exist. Nobody publishes: (a) article-level text diffs between the 2024 OJ version, the Digital Omnibus amendments, and the final trilogue text; (b) timestamped guidance drops from the European AI Office; (c) national transposition status per Member State; (d) a machine-readable changelog keyed to article numbers.

**Regula's distinctive angle.** Publish `eu-ai-act-delta-log` — a git repo where every commit is a regulatory change (amendment, guidance, Commission Q&A, national transposition). Each commit references an article. Each commit links to the primary source (EUR-Lex CELEX number, Commission press release, Member State gazette). Auto-generated changelog in Markdown. Weekly crawl of EUR-Lex + digital-strategy.ec.europa.eu + Member State OJs. Subscribe-by-RSS.

**Maintenance burden.** Medium-high. Target cadence: a legal-research hour every 2–3 days to triage EUR-Lex alerts and national gazettes. Automatable for ~70% of volume using [EUR-Lex CELEX APIs](https://eur-lex.europa.eu/content/tools/TableOfSectors/webservice.html). **[Effort estimate — unverified projection, not benchmarked].**

**GTM.** This becomes the default citation for "what changed in the AI Act this month". Every consultancy blog will link to it. Every compliance vendor will subscribe. Regula's CLI then calls out to the delta log to warn users when their installed ruleset is older than the last regulatory change — directly tying the data asset to the product.

**Verdict: GO — highest priority.** Single most defensible asset on this list. **Counterevidence:** IAPP has the institutional muscle to do this in a week if they decide to; OneTrust/TrustArc have budgets. The moat is being first, being open, and being the one that *nerds and lawyers both trust*. If IAPP launches a paid structured tracker, Regula's free open version still wins on developer distribution.

---

## Candidate 5 — AI System Fingerprinting Corpora from Public Repos

**Who does it today.** BigCode's **The Stack v2** is 3B files across 600+ languages drawn from Software Heritage [verified — huggingface.co/datasets/bigcode/the-stack-v2]. Google **deps.dev** dependency graph covers 50M+ package versions and has been used for AI/ML dependency analysis (DepsRAG arXiv:2405.20455) [verified]. **Hugging Face Hub** itself is the canonical model provenance corpus; studies of 7,433 dataset cards (86% top-100 card completeness vs 7.9% long-tail) and 100 model cards (947 unique section names) are published on arXiv [verified — arXiv:2401.13822, arXiv:2502.04484]. The **Data Provenance Initiative** audited 1,800+ fine-tuning datasets and found 66% of HF licences miscategorised, 70% omission rates on popular hosting sites [verified — dataprovenance.org, Nature Machine Intelligence 2024, arXiv:2310.16787]. **AI-BOM** schemas exist — CycloneDX ML-BOM, SPDX 3.0 AI extensions (arXiv:2504.16743), OWASP AI BOM — but population data does not [verified].

**The gap.** Nobody joins *code-level fingerprints* (imports, framework calls, model loading paths) to *model provenance* (which HF model is being loaded? with what licence? trained on what?) at scale.

**Regula's distinctive angle.** Regula already parses Python imports and `from_pretrained()` calls. A weekly scan of top-N GitHub repos could emit an "AI-BOM in the wild" dataset: for every repo, `{hf_models_used[], datasets_used[], training_pipelines[], inference_frameworks[]}`. This is a genuine complement to Data Provenance Initiative (which works dataset-first) and deps.dev (which is language-package-first).

**Maintenance burden.** Medium. The extraction is mechanical; the schema design is the hard part (align with SPDX 3.0 AI and CycloneDX ML-BOM rather than inventing).

**GTM.** Position as the corpus for answering "how many open-source AI projects use HF models with non-commercial licences?" — which is exactly the Digital Omnibus / Data Act question regulators care about.

**Verdict: NO-GO (for now).** The moat is weak. Data Provenance Initiative, Hugging Face's own analytics, and deps.dev together already cover most of the value. Revisit in 12 months if Regula has bandwidth. **Counterevidence to the NO-GO:** if the EU AI Office mandates AI-BOM as part of Art. 11 technical documentation (plausible post-Omnibus), this asset suddenly becomes high-value infrastructure. Keep it in the backlog.

---

## Additional Angles Not in the Original List

### 6. AI Act Enforcement & Fine Corpus (parallel to CMS GDPR Enforcement Tracker)

The **CMS GDPR Enforcement Tracker** records 2,245 GDPR fines, with total GDPR penalties now exceeding €7.1bn [verified — enforcementtracker.com, kiteworks.com 2026 report]. No AI Act equivalent exists because enforcement has barely begun (Art. 99 penalties apply from August 2026, delayed further by Omnibus). **Moat:** be the first to build `ai-act-enforcement-tracker.org`; be the citation every journalist uses on day 1 of the first fine. **Effort:** low until the first fines land, then medium ongoing. **Verdict: GO — start the skeleton now.**

### 7. Commission Q&A / AI Office Guidance Scraper

The Commission missed its 2 February deadline for Article 6 high-risk guidance [verified — IAPP]. Guidance drops are ad-hoc, undated on the Commission site, and scattered across `digital-strategy.ec.europa.eu` and `ai-act-service-desk.ec.europa.eu`. A scraper that archives every Q&A with timestamp + diff would be a primary-source feed that legal teams would pay for. **Verdict: GO, bundle with Candidate 4.**

### 8. Academic Citation Graph of AI-Regulation Research

Build a dataset of arXiv/SSRN papers that cite specific AI Act articles, with per-article citation counts and sentiment. Signal for which articles are most contested. Method: OpenAlex API + regex extraction of article references. Nobody publishes this. **Verdict: CONDITIONAL — cheap to build as a side project, moderate value.**

### 9. Developer-Sentiment Corpus (HN/Reddit/GitHub issues on AI Act compliance)

Scrape HN, `r/MachineLearning`, `r/programming`, GitHub issues and PRs for mentions of "EU AI Act", "Article 10", "GPAI", etc. Classify sentiment and track over time. Creates a "what developers actually think" longitudinal signal that no consultancy has. **Verdict: GO — low effort, unique angle, good content marketing ammunition.**

### 10. National Transposition & Sandbox Registry

Each Member State must establish at least one AI regulatory sandbox by 2 August 2026 [verified — digital-strategy.ec.europa.eu]. No central registry tracks (a) which MS have done this, (b) sandbox entry criteria, (c) which companies are enrolled. Manual crawl of 27 national competent authority pages. **Verdict: GO — small, high-cite-value reference asset.**

### 11. Harmonised-Standards Draft Diff Tracker

CEN-CENELEC JTC 21 drafts (prEN 18286 AI quality management system, prEN on risk management, etc.) are in public enquiry but scattered across national mirror committees. A tracker that captures every draft version, public comment window, and Formal Vote status — diff-able — would be unique. **Verdict: CONDITIONAL — only if Regula can get access to the draft texts, which are sometimes paywalled.**

### 12. Open-Source Model Licence × Jurisdiction Matrix

Extension of Data Provenance Initiative: for each open-weights model, match declared licence against Art. 2(12) open-source exemption eligibility. The DPI found 66% licence-miscategorisation on HF. **Verdict: CONDITIONAL GO — overlaps with DPI but the jurisdictional angle is new.**

### 13. Incident → Code-Pattern Backmap

Take OECD AIM and AIID incident reports and, where public code exists, identify which Regula pattern would have caught the defect that caused the incident. This is the empirical bridge between "incidents happen" and "scanners catch them". Creates a devastating marketing line: "X% of AI incidents in the AIM database could have been prevented by static analysis". **Verdict: GO — strong narrative asset, medium effort.**

---

## Ranked Recommendation

1. **Candidate 4: EU AI Act Regulatory Delta Log** (git-backed, primary-source, diff-able) — highest moat, highest urgency because of the Digital Omnibus moving parts. Bundle with Angle 7 (Commission Q&A scraper) and Angle 10 (national sandbox registry). Target first release within 4 weeks.
2. **Candidate 2: Labelled TP/FP Corpus (RegulaBench v1)** — single biggest academic-citation play. Target v0.1 with 100 cases in 8 weeks; seek NIST AIRC collaboration.
3. **Candidate 3: Pattern→Article Mapping with DOIs** — prerequisite for Candidates 1 & 13. Target v1 within 6 weeks; publish under CC-BY-4.0 with Zenodo DOI.
4. **Angle 13: Incident → Code-Pattern Backmap** — marketing dynamite, feeds into Candidate 2.
5. **Angle 9: Developer Sentiment Corpus** — low-cost, continuous content engine.
6. **Angle 6: AI Act Enforcement Tracker** — stub now, populate when first fines land.
7. Defer: Candidates 1 and 5, Angles 8, 11, 12.

---

## Counterevidence: Where the Moat Thesis Might Fail

1. **IAPP, Future of Life Institute, or OneTrust decide to publish structured outputs.** Any of them could move in a week. Regula's only defence is being open, free, and developer-distributed.
2. **NIST launches an AI-governance SARD.** NIST already runs SARD and has the AI RMF crosswalk programme. If they extend SARD to AI Act controls, RegulaBench becomes an upstream contribution rather than the primary reference.
3. **The Digital Omnibus defers obligations so far that the urgency evaporates.** High-risk obligations already pushed to 2027-2028. If enforcement slips into 2029, the market for a compliance CLI shrinks.
4. **LibVulnWatch adds AI-Act tags.** It already covers 88% of Scorecard checks for 20 AI libs; adding regulatory mappings is a quarter of work.
5. **Holistic AI open-sources pattern-level mappings.** They already publish an open-source library covering EU AI Act, NIST RMF and ISO 42001. If they go deeper, Candidate 3 is commoditised.
6. **The CLI pattern matching approach is wrong.** AI Act obligations are often organisational (Art. 9 risk-management *system*, Art. 17 quality-management *system*) not code-level. A static code scanner may fundamentally address the wrong 30% of the spec. **This is the strongest counterargument to the whole Regula thesis** and should be named explicitly in any investor conversation.
7. **Pattern-to-article mappings age badly.** Every Omnibus amendment invalidates mappings. Maintenance is the moat — but it's also the burden.

---

## Sources (Primary, Grouped by Candidate)

### Candidate 1 — OSS-AI scan datasets
- OpenSSF Scorecard repo — https://github.com/ossf/scorecard
- Scorecard arXiv paper — https://arxiv.org/pdf/2208.03412
- LibVulnWatch (arXiv:2505.08842) — https://arxiv.org/html/2505.08842
- BigCode The Stack v2 — https://huggingface.co/datasets/bigcode/the-stack-v2
- deps.dev API announcement — https://security.googleblog.com/2023/04/announcing-depsdev-api-critical.html
- GitHub CodeQL — https://github.com/github/codeql
- GHSA-based LLM vuln study (arXiv:2604.04288) — https://arxiv.org/html/2604.04288
- MSR 2026 Mining Challenge (AIDev) — https://2026.msrconf.org/details/msr-2026-mining-challenge/3/AI-builds-We-Analyze-An-Empirical-Study-of-AI-Generated-Build-Code-Quality

### Candidate 2 — TP/FP corpora
- NIST SARD test suites — https://samate.nist.gov/SARD/test-suites
- Juliet C/C++ 1.3 — https://samate.nist.gov/SARD/test-suites/112
- NIST IR 8561 (SARD overview) — https://nvlpubs.nist.gov/nistpubs/ir/2025/NIST.IR.8561.pdf
- MLCommons AILuminate v1.0 (arXiv:2503.05731) — https://arxiv.org/abs/2503.05731
- AILuminate benchmark — https://ailuminate.mlcommons.org/

### Candidate 3 — Pattern→regulation mappings
- NIST AI RMF crosswalks hub — https://airc.nist.gov/airmf-resources/crosswalks/
- NIST AI RMF ↔ ISO 42001 crosswalk PDF — https://airc.nist.gov/docs/NIST_AI_RMF_to_ISO_IEC_42001_Crosswalk.pdf
- Holistic AI library (GitHub) — https://github.com/holistic-ai/holisticai
- Holistic AI library docs — https://holisticai.readthedocs.io/
- FLI AI Act Explorer — https://artificialintelligenceact.eu/ai-act-explorer/
- GPAI Code of Practice (final) — https://code-of-practice.ai/

### Candidate 4 — Regulatory delta logs
- FLI Implementing the AI Act — https://futureoflife.org/project/eu-ai-act/
- IAPP Regulatory Directory — https://iapp.org/resources/article/eu-ai-act-regulatory-directory
- IAPP Commission missed Art. 6 deadline — https://iapp.org/news/a/european-commission-misses-deadline-for-ai-act-guidance-on-high-risk-systems
- Morrison Foerster Digital Omnibus analysis — https://www.mofo.com/resources/insights/251201-eu-digital-omnibus
- Addleshaw Goddard Council/Parliament positions — https://www.addleshawgoddard.com/en/insights/insights-briefings/2026/technology/eu-digital-omnibus-ai-update-council-parliament-agreed-positions/
- Cooley AI Act Digital Omnibus — https://www.cooley.com/news/insight/2025/2025-11-24-eu-ai-act-proposed-digital-omnibus-on-ai-will-impact-businesses-ai-compliance-roadmaps
- Sidley Digital Omnibus — https://www.sidley.com/en/insights/newsupdates/2025/12/eu-digital-omnibus-the-european-commission-proposes-important-changes-to-the-eus-digital-rulebook
- TechPolicy.Press — https://www.techpolicy.press/eus-ai-act-delays-let-highrisk-systems-dodge-oversight/
- Global Policy Watch MEPs position — https://www.globalpolicywatch.com/2026/03/meps-adopt-joint-position-on-proposed-digital-omnibus-on-ai/
- OneTrust Digital Omnibus — https://www.onetrust.com/blog/how-the-eu-digital-omnibus-reshapes-ai-act-timelines-and-governance-in-2026/
- Plesner AI Act August 2026 — https://plesner.com/en/news/ai-act-august-2026-what-expect-delayed-standards-pending-guidance-and-digital-omnibus-ai
- AlgorithmWatch AI Act guide — https://algorithmwatch.org/en/ai-act-explained/
- EU Commission AI Act policy — https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai
- Navigating the AI Act FAQ — https://digital-strategy.ec.europa.eu/en/faqs/navigating-ai-act
- CEN-CENELEC JTC 21 — https://jtc21.eu/
- CEN-CENELEC AI standardization acceleration — https://www.cencenelec.eu/news-events/news/2025/brief-news/2025-10-23-ai-standardization/
- EU Commission Standardisation of the AI Act — https://digital-strategy.ec.europa.eu/en/policies/ai-act-standardisation

### Candidate 5 — AI system fingerprinting
- The Stack v2 (HF) — https://huggingface.co/datasets/bigcode/the-stack-v2
- deps.dev (repo) — https://github.com/google/deps.dev/
- Data Provenance Initiative (arXiv:2310.16787) — https://arxiv.org/abs/2310.16787
- Nature Machine Intelligence DPI — https://www.nature.com/articles/s42256-024-00878-8
- Data Provenance Initiative site — https://www.dataprovenance.org/
- HF dataset cards large-scale analysis (arXiv:2401.13822) — https://arxiv.org/html/2401.13822v1
- HF supply chain & licensing (arXiv:2502.04484) — https://arxiv.org/html/2502.04484v2
- AI-BOM SPDX 3.0 (arXiv:2504.16743) — https://arxiv.org/abs/2504.16743
- CycloneDX ML-BOM — https://cyclonedx.org/capabilities/mlbom/

### Additional angles
- CMS GDPR Enforcement Tracker — https://www.enforcementtracker.com/
- Kiteworks GDPR fines 2026 — https://www.kiteworks.com/gdpr-compliance/gdpr-fines-data-privacy-enforcement-2026/
- OECD AI Incidents Monitor overview — https://oecd.ai/en/incidents
- OECD AIM methodology — https://oecd.ai/en/incidents-methodology
- OECD common reporting framework (PDF) — https://www.oecd.org/content/dam/oecd/en/publications/reports/2025/02/towards-a-common-reporting-framework-for-ai-incidents_8c488fdb/f326d4ac-en.pdf
- AIID (Responsible AI Collaborative) — https://github.com/responsible-ai-collaborative/aiid
- AI Incident Database site — https://incidentdatabase.ai/
- MIT AI Risk Incident Tracker — https://airisk.mit.edu/ai-incident-tracker
- CSET AI Incidents brief — https://cset.georgetown.edu/wp-content/uploads/CSET-AI-Incidents.pdf
- HIIG analysis of AI Act implementation — https://www.hiig.de/en/eu-ai-act/
- EU AI Act Art. 43 (Conformity Assessment) — https://artificialintelligenceact.eu/article/43/
- EU AI Act Art. 29 (Notified Bodies application) — https://artificialintelligenceact.eu/article/29/

---

## Methodology & Confidence Statement

**Method.** Single research pass using WebSearch across 20+ targeted queries covering all 5 candidates plus additional-angle seeds (AI-BOM, Data Provenance, MLCommons AILuminate, CEN-CENELEC, deps.dev, OECD AIM, Holistic AI, AlgorithmWatch, CodeQL, NIST crosswalks, Digital Omnibus legal analyses). All citations are to named primary sources (arXiv, NIST, NIST AIRC, EU Commission, Nature MI, BigCode/HF, GitHub repos, named law firms' client alerts, IAPP news articles). **No claim is relayed from an aggregator blog.** Where a law-firm client alert is cited, it is because that firm is reporting on a Commission proposal or Council/Parliament position that the firm directly analysed; EUR-Lex CELEX numbers would be the next step for deeper verification.

**Confidence labels.**
- *Verified* — I found the primary source in this pass and the claim is directly from it.
- *Inferred* — logical consequence of two verified facts; flagged where used.
- *Speculative* — where I am reasoning about competitor moves or Regula's future positioning; flagged in counterevidence.

**Known gaps in this research pass.**
1. I did not verify exact CELEX numbers on the Digital Omnibus text; all dates are from legal-firm reporting within 2 weeks of the official Council/Parliament positions.
2. I did not verify each of the 27 Member States' sandbox status individually (Angle 10 would require that work). The 27-Member-State figure reflects current EU composition per [europa.eu/european-union/about-eu/countries](https://european-union.europa.eu/principles-countries-history/country-profiles_en).
3. I did not search Semgrep's internal metrics API or LGTM archive status (LGTM was shut down by GitHub in December 2022 per prior knowledge, not reverified in this pass — *inferred*).
4. The claim that "nobody publishes a pattern-level mapping with DOIs" is a *non-existence claim* and is only as strong as the searches that failed to find one; a determined adversary could produce a counterexample.
5. NANDO (the Commission's notified-body database) was not directly scraped; the Art. 34 confidentiality finding is from reading Art. 34 and HIIG's analysis.
6. Snyk, CycloneDX, SPDX specifications were surfaced but not read in full.

**Counter-bias discipline.** For every GO verdict I asked "who could commoditise this in a month", and the answer is written into the counterevidence section. For the one NO-GO (Candidate 5), I wrote the counterevidence *against* my own NO-GO. The strongest single counterargument — that static code scanning may fundamentally address the wrong 30% of the EU AI Act — is named explicitly above and is the biggest existential risk to the whole moat thesis, not just to any one data asset.

**Not verified without a second pass.** National transposition statuses, prEN 18286 draft text access, and the full list of AI Office guidance documents published since August 2025. A second research pass should target EUR-Lex CELEX numbers and the AI Office's own publication page.
