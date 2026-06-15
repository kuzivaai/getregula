# Session 12: Value-Prioritisation Synthesis

**Date:** 14 June 2026
**Type:** Decision document. No implementation.

---

## Current State (One Honest Paragraph)

Regula is the most capable, honest, and regulatory-current open-source EU AI Act code scanner. It rates 4–5 on detection breadth, honesty/credibility, regulatory currency, and evidence/auditability — ahead of every open-source competitor on each axis (Session 11, A3, VERIFIED via GitHub API, PyPI API, and codebase audit). The "static scanner for code" niche has exactly four occupants: Regula, AIR Blackbox (17 stars, 958 downloads/month, Python-only, 51 checks), aibom-scanner (20 stars, SDK detection), and InfraRails (5 stars, Terraform-only). Regula leads on breadth (398 patterns, 8 languages, 12 frameworks) and evidence capability (Ed25519 signing, RFC 3161 timestamps, conformity packs) and publishes precision figures on a blind-labelled corpus of production code (AIR Blackbox also publishes precision, but on synthetic fixtures). Against these strengths: discoverability is 1/5 (4 stars, 117 downloads/month, zero third-party mentions, absent from all MCP registries and buyer guides), and value-legibility to a non-technical buyer is 3/5 (the site speaks to developers, not the person who signs the purchase order). The product is strong. The distribution is near-zero. This finding is unchanged across Sessions 9, 10, and 11.

---

## Candidate Next Steps

### Category A: Founder Manual Actions (Already Prepared)

| # | Action | Effort | Prepared? | Evidence It Matters |
|---|--------|--------|-----------|---------------------|
| F1 | **Commit Session 11 + push to origin** | 10 min | Yes (all verified, tests green) | Deploys: 25 AI crawlers in robots.txt, llms.txt covering 15 posts, llms-full.txt, BreadcrumbList on 26 pages, WebSite schema on 3 pages, OG/Twitter/canonical on 3 previously missing posts. None of this has value until live. VERIFIED — all changes validated. |
| F2 | **MCP registry submissions (D4)** | 30 min | Yes (mcp-server.json committed, HUMAN_ACTIONS §6) | Regula has an MCP server but 0 registry listings. ArkForge (8 stars, direct competitor) IS listed on PulseMCP. Every MCP registry is a discovery path for Claude Code/Cursor/Windsurf users searching for "EU AI Act." VERIFIED — GitHub API, PulseMCP check. |
| F3 | **Send IAPP email (D5)** | 5 min | Yes (draft in HUMAN_ACTIONS §7) | The IAPP AI Governance Vendor Report is a significant discovery channel for compliance buyers (CTOs, DPOs, compliance leads). Regula is not listed. REPORTED — IAPP report reviewed in Phase 0; characterisation as "significant" is plausible but unquantified. |
| F4 | **Bing Webmaster Tools (D7)** | 15 min | Yes (steps in HUMAN_ACTIONS §1) | Bing Webmaster submission improves discoverability in Bing Chat and Microsoft Copilot, and may supplement ChatGPT's indexing (ChatGPT's OAI-SearchBot crawls independently, but Bing feeds Copilot). VERIFIED — robots.txt allows OAI-SearchBot; Bing/Copilot relationship documented. |
| F5 | **Label 39 targeted findings + 50 blind subset (A2/A3)** | 2.5 hr | Yes (infrastructure built: targeted_corpus/candidates.json, rater2_blind_subset.json, compute_kappa.py) | Unblocks the entire benchmark credibility chain: kappa computation → updated precision figures → HN launch → external credibility. Currently high_risk precision is unmeasurable (N=6). VERIFIED — PRECISION.json, benchmarks/. |
| F6 | **Recruit Rater 2** | 10 min to send, weeks latency | Yes (protocol documented) | Unblocks publishable kappa (inter-rater reliability). Without Rater 2, precision figures remain single-rater and are a known HN attack vector (Strategic Plan §1.3). VERIFIED — benchmark docs. |
| F7 | **LinkedIn content (D11)** | 4 posts over 4 weeks | Not drafted | Founder-written thought-leadership. No product promotion. Direct visibility to the compliance/AI governance audience. REPORTED — LinkedIn engagement data not available; effectiveness is an assumption. |
| F8 | **Lobste.rs invite request** | 10 min | Yes (noted in HUMAN_ACTIONS §3) | Starts a 70-day clock. Enables a future submission. Low-cost optionality. VERIFIED — Lobste.rs policy. |

### Category B: Buildable Product/Site Work (Claude Code)

| # | Action | Effort | Blocked? | Evidence It Matters |
|---|--------|--------|----------|---------------------|
| B1 | **B3 — Domain fingerprinting for remaining subcategories** | M | No blockers | Expands DOMAIN_FINGERPRINTS to all 15 high_risk categories. Improves detection quality. But: improvement is unmeasurable until A3 labelling produces enough high_risk findings. Building blind. VERIFIED — risk_patterns.py, backlog B3. |
| B2 | **C5 — Watermarking timeline logic (PARTIAL)** | S | No blockers | `regula conform` doesn't distinguish new vs existing system deadlines (Aug 2026 vs Dec 2026). Niche; most buyers won't encounter this. VERIFIED — CLI output. |
| B3 | **F1 — Answer-first blog restructuring** | M | No blockers | GEO-SFE research suggests 17.3% citation improvement from structural optimisation. But: the research is REPORTED (arXiv, not independently verified), and Session 11's audit found the existing content structure is already good ("excellent" on key pages). Marginal returns. |
| B4 | **F2 — Value-legibility copy drafting** | M | Founder-gated | Session 11 rated value-legibility 3/5. The hero speaks to developers, not the compliance buyer. Drafting alternative copy for founder review is possible. But: every sentence is a potential claim, and the founder must review line-by-line. Cannot be auto-accepted. VERIFIED — landing page review. |
| B5 | **F4 — Credibility signals audit** | M | No blockers | Research-only. Compare landing page against EuroComply, Credo AI, Vanta for trust signal gaps. Value is informational, not direct. |
| B6 | **B2 — Tune employment/credit/medical patterns** | M | Blocked on A3 labelling | Needs labelled high_risk data to know which patterns to tune. Building without data is guessing. VERIFIED — backlog B2. |
| B7 | **A4 — Confidence calibration curve** | M | Blocked on A3 labelling | Needs labelled corpus. VERIFIED — backlog A4. |
| B8 | **A6 — Publish corpus on HuggingFace/Zenodo** | M | Blocked on A2/A3 | Needs completed labelling + kappa. VERIFIED — backlog A6. |
| B9 | **E2/E3 — Self-assessment web flow / hosted viewer** | M | No blockers, P2 | Research-only. Addresses the "no non-technical surface" pre-mortem (Strategic Plan §1.2). But: the pre-mortem rates this #2, behind invisibility. Building a surface nobody can find is the wrong ordering. |

### Category C: New Opportunities from Session 11 Research

| # | Action | Effort | Evidence It Matters |
|---|--------|--------|---------------------|
| C1 | **Cite academic papers in content** | S | Three arXiv papers validate the product category. Citing them in blog/docs adds authority. Low effort, low risk. But: marginal value — no buyer reads Regula because arXiv papers endorse the approach. REPORTED — arXiv IDs verified, content claims not independently confirmed. |
| C2 | **MCP 2026-07-28 spec tracking** | S (now), M (later) | New MCP spec publishes 28 July. Regula's MCP server may need updates. Tracking now, building after publication. VERIFIED — MCP blog. |

---

## Value-Per-Effort Scoring

| # | Candidate | Value to Buyer (1–5) | Effort | Who | Risk | Unblocks | Score Basis |
|---|-----------|---------------------|--------|-----|------|----------|-------------|
| **F1** | Push to origin | 3 | S (10 min) | Founder | Low | Everything GEO | VERIFIED — all changes tested |
| **F2** | MCP registries | 4 | S (30 min) | Founder | Low | IDE agent discovery | VERIFIED — 0 listings |
| **F3** | IAPP email | 4 | S (5 min) | Founder | Low | Compliance buyer visibility | VERIFIED — draft ready |
| **F4** | Bing Webmaster | 3 | S (15 min) | Founder | Low | ChatGPT search | VERIFIED — steps ready |
| **F5** | Label findings | 3 | M (2.5 hr) | Founder | Low | HN launch chain, credibility | VERIFIED — infrastructure built |
| **F6** | Recruit Rater 2 | 3 | S + weeks | Founder | Low | Publishable kappa | VERIFIED — protocol ready |
| **F8** | Lobste.rs invite | 1 | S (10 min) | Founder | Low | Future submission | VERIFIED |
| B1 | Domain fingerprints | 2 | M | Claude Code | Low | Nothing (unmeasurable without labels) | VERIFIED — building blind |
| B2 | Watermarking logic | 1 | S | Claude Code | Low | Niche feature | VERIFIED |
| B3 | Blog restructuring | 2 | M | Claude Code | Low | Marginal GEO | REPORTED — 17.3% figure unverified |
| B4 | Copy drafting | 4 | M | Both | Medium | Buyer conversion (if approved) | VERIFIED, but gated |
| C1 | Cite papers | 1 | S | Claude Code | Low | Nothing | REPORTED |

**Value/effort ranking (effort-adjusted):**

1. **F3: Send IAPP email** — 5 min, high value, direct access to buyer persona
2. **F1: Push to origin** — 10 min, deploys all Session 11 GEO work
3. **F2: MCP registries** — 30 min, fills the 0-listing gap
4. **F4: Bing Webmaster** — 15 min, enables ChatGPT discovery
5. **F5: Label findings** — 2.5 hr, unblocks the HN launch chain
6. **F6: Recruit Rater 2** — 10 min now + weeks latency, unblocks publishable kappa
7. **B4: Value-legibility copy drafting** — first Claude Code task that clears, but founder-gated
8. **F8: Lobste.rs invite** — 10 min, starts clock
9. **B1: Domain fingerprints** — buildable but unmeasurable
10. **B3: Blog restructuring** — marginal improvement on good content

---

## Confronting the Inconvenient Finding

The top 6 items are all founder actions. The highest-value Claude Code task (#7, value-legibility copy drafting) ranks 7th and is founder-gated — it cannot proceed without the founder deciding the framing, and it cannot be auto-accepted because every sentence is a potential claim.

This is the same finding from Sessions 9, 10, and 11. The evidence has converged three times:

- **Session 9** (audit close-out): "The remaining automatable work all requires labelled data as input. The build pause is correct."
- **Session 11** (competitive/GEO): "The critical problem is not capability — it is that almost nobody can find it. Discoverability is 1/5."
- **Session 12** (this document): The top 6 next steps by value-per-effort are founder manual actions totalling ~70 minutes + 2.5 hours of labelling. The highest-value Claude Code task is 7th and gated.

The honest conclusion: **building more is not the constraint. Distribution and labelling are.** A Claude Code session that manufactures build work to justify itself, when the data says the bottleneck is 70 minutes of externals the founder hasn't done yet, would be the bias this analysis exists to avoid.

---

## Ranked Next-3

### #1: The 70-Minute External Blitz (Founder, ~70 min)

**What:** Push to origin, send IAPP email, submit to 4 MCP registries, submit sitemap to Bing Webmaster Tools.

**Why it's #1:** These are the four highest value-per-effort items. They are all S-effort, all prepared (drafts written, manifests committed, steps documented), and each opens a distinct discovery channel. Combined, they move Regula from "absent from all buyer guides and registries" to "listed in 5+ discovery channels." No Claude Code session can substitute for this.

**Definition of done:** IAPP email sent (confirmation received or bounced). Regula listed on ≥3 MCP registries (visible in search). Bing Webmaster Tools verified and sitemap accepted. Site pushed with Session 11 GEO changes live.

**How value is measured:** Within 60 days: check MCP registry listing visibility (search "EU AI Act" on each registry), check Bing indexing status, check IAPP report inclusion (next edition, timing uncertain). These are influence signals — citation and download impact is months out. No promise of specific numbers.

### #2: Label the Targeted Findings and Blind Subset (Founder, ~2.5 hr)

**What:** Open `benchmarks/targeted_corpus/candidates.json` and label 39 findings as tp/fp. Copy `rater2_blind_subset.json` to `rater1_blind_subset.json` and label 50 entries independently.

**Why it's #2:** This unblocks the most valuable Claude Code session available — the one that computes kappa, publishes updated precision figures (especially high_risk on N>6), and fires the HN launch package against defensible numbers instead of "unmeasurable." Without labels, B2 (pattern tuning), A4 (calibration), A6 (corpus publication), and D8 (HN launch) are all blocked. This is the single founder action with the largest downstream unblock.

**Definition of done:** `candidates.json` has `"label": "tp"` or `"fp"` on all 39 entries. `rater1_blind_subset.json` exists with 50 labelled entries.

**How value is measured:** kappa computation (immediate, automated). If kappa ≥ 0.60: publishable precision figures follow. If kappa < 0.60: labelling criteria need refinement before publication.

### #3: Recruit Rater 2 (Founder, 10 min to send + weeks latency)

**What:** Email academic contacts in AI auditing/fairness. Offer co-authorship on the published benchmark. Request ~3 hours of labelling time on ~89 entries.

**Why it's #3:** Without Rater 2, precision figures remain single-rater and are the known attack vector for HN credibility (Strategic Plan §1.3). This has weeks of latency, so starting it now is highest-leverage. The 10 minutes to send the email is trivially cheap relative to the chain it unblocks.

**Definition of done:** Email sent to ≥1 academic contact with the labelling task description, timeline, and co-authorship offer.

**How value is measured:** Rater 2 commitment (yes/no/timeline). If yes: labels arrive → kappa → publication → HN launch. If no: re-recruit.

---

## What NOT To Do Next

| Candidate | Why Not |
|-----------|---------|
| **B3 — Domain fingerprinting** | Building detection quality improvements without labelled data to measure them is guessing. Do this AFTER labelling (F5) produces high_risk findings to test against. |
| **F1 — Answer-first blog restructuring** | The content structure is already good (Session 11 audit). The 17.3% GEO-SFE improvement figure is REPORTED, not VERIFIED. Marginal returns on an already-decent baseline. |
| **E2/E3 — Web flow / hosted viewer** | Addresses pre-mortem #2 (no non-technical surface) but pre-mortem #1 (invisibility) is the binding constraint. Building a surface nobody can find is the wrong ordering. Do this after distribution channels are open. |
| **A4 — Calibration curve** | Blocked on labelling. Cannot execute. |
| **A6 — Corpus publication** | Blocked on labelling + kappa. Cannot execute. |
| **Another Claude Code build session** | The data says the bottleneck is not the product. The four highest-value actions are founder manual tasks totalling ~70 minutes. Running a build session to avoid doing them is the bias pattern this analysis exists to catch. |

---

## Research-Eval on This Ranking

**Self-adversarial check, assuming the ranking is biased toward action that justifies NOT having a session (the inverse bias):**

1. **Is B4 (copy drafting) underranked?** Value-legibility is 3/5, and improving it addresses the conversion gap once buyers DO find Regula. If F1-F4 drive traffic, value-legibility becomes the next binding constraint. Counter: it's founder-gated, so it cannot proceed without the founder's editorial decisions regardless of ranking. It sits at #7 correctly — not because it lacks value, but because it's blocked on the same person the top 6 depend on.

2. **Is "building blind" (B1) unfairly dismissed?** Domain fingerprinting (B3) has no data dependency per the backlog. Counter: the backlog says "no blockers" but the SESSION11_RESEARCH.md analysis (A3) notes that high_risk precision is unmeasurable at N=6. Improving fingerprinting without being able to measure whether it helps is investing effort with no feedback loop. The dismissal is warranted.

3. **Could a Claude Code session draft F2 copy for founder review, making it ready when the founder is ready?** Yes — but the prompt instruction says "the burden of proof is on the build, given two prior sessions found otherwise." The value of pre-drafting copy the founder may reject entirely is speculative. The cost is low (Claude Code time is cheap), but the signal sent is "let's find something to build" rather than "do the thing the data says matters." If the founder wants copy drafts, they can ask for them. The ranking does not propose it unprompted.

4. **Does ranking all founder actions at the top constitute telling the founder what to do?** The prompt explicitly requires this: "If the analysis shows the top-ranked items are founder actions rather than builds, say so plainly." The ranking follows the instruction and the evidence.

**Verdict:** No bias detected in the ranking toward artificially suppressing build work. The ranking would flip if the founder had already completed items F1–F4 — at that point, B4 (copy drafting) would become #1. The ranking is conditional on the current state, not a permanent position.

---

## Plain Statement

**The top recommendation is a founder action, not a Claude Code task.**

The three highest-value next steps are: (1) the 70-minute external blitz (push, IAPP, MCP registries, Bing), (2) label the targeted findings and blind subset (2.5 hours), and (3) recruit Rater 2 (10 minutes to send). Combined, they take ~3.5 hours of founder time and unblock every remaining high-value action in the project.

The highest-value Claude Code task available — value-legibility copy drafting — ranks 7th and is founder-gated. It becomes #1 after the founder completes F1–F4.

No build session should be manufactured to avoid doing the human queue. The data has said this three times. Act on it.
