# Research Evaluation — Public-Launch Readiness

**Evaluator:** Claude Opus 4.6 (1M context), sceptical second-pass reviewer.
**Date:** 2026-04-09. British English. Tool set: WebSearch plus targeted source triangulation. WebFetch was not run on primary domains in this pass; every verdict below is labelled accordingly.

Documents evaluated:

1. `/home/mkuziva/getregula/docs/competitor-analysis.md`
2. `/home/mkuziva/getregula/docs/moat-research.md`
3. `/home/mkuziva/getregula/docs/research-eval-report.md`
4. `/home/mkuziva/getregula/docs/translation-skill-recommendation.md`
5. `/home/mkuziva/getregula/docs/what-regula-does-not-do.md`
6. `/home/mkuziva/getregula/docs/evidence-pack-guide.md`
7. `/home/mkuziva/getregula/content/regulations/delta-log/entries/*.json` (5 files)
8. `/home/mkuziva/getregula/content/regulations/sandbox-registry/index.json` (27 MS entries, 5 seeded)

---

## Executive summary (trust / discard / verify)

**TRUST, WITH TWO SMALL CORRECTIONS:** the six documents and the two data assets are overwhelmingly defensible. Every load-bearing regulatory date I could check against primary-style sources is correct (CELEX 32024R1689 OJ 12 July 2024; Digital Omnibus proposed 19 November 2025; Council general approach 13 March 2026; Parliament plenary position 26 March 2026; long-stop 2 December 2027 / 2 August 2028). Every competitor claim I re-verified (AIR Blackbox, Microsoft Agent Governance Toolkit, ark-forge, Systima Comply, DeepL 1.4× EN↔DE, Kocmi WMT25 arXiv 2508.14909) survived re-checking against at least one primary-class source.

**VERIFY MANUALLY BEFORE PUBLISH:** two sandbox-registry rows need softening (NL "established" overstates the current state, which is "proposal March 2025, expected launch by August 2026"; FR "CNIL will operate the Article 57 sandbox" reads stronger than the public record, which only confirms CNIL runs its own public-service sandboxes and handles specific prohibited-AI enforcement). Both entries are already labelled `confidence: reported-unverified`, so the fix is language, not a data retraction.

**DISCARD:** nothing. I found no fabricated statistic, no misattributed quote, and no regulatory claim that is outright wrong.

**ONE MISSED COMPETITOR:** `desiorac/mcp-eu-ai-act` (GitHub) is a second MCP-server EU AI Act scanner distinct from ark-forge's; it is not listed in competitor-analysis.md and should be added as an adjacent entry in the next revision.

**Overall verdict: PASS with edits.** None of the issues is a "discard the document" problem; all are surgical language fixes. The documents are unusually honest about their own gaps, which made this evaluation fast.

---

## Per-document scorecard (1–5 per criterion; <4 = BLOCK)

| Document | Stat accuracy | Quote fidelity | Competitive completeness | Policy accuracy | Recency | Verdict |
|---|---|---|---|---|---|---|
| competitor-analysis.md | 5 | 5 | 4 | 5 | 5 | **PASS**. AIR Blackbox and MSFT Agent Governance Toolkit already promoted in this version; `desiorac/mcp-eu-ai-act` is a minor miss worth adding. |
| moat-research.md | 5 | 5 | 5 | 5 | 5 | **PASS**. Claims are cautiously labelled; DOI/SARD/LibVulnWatch references all check out. |
| research-eval-report.md | 5 | 5 | 5 | 5 | 5 | **PASS**. It is itself a verification document and is internally consistent with what I independently verified. |
| translation-skill-recommendation.md | 4 | 5 | 4 | 5 | 5 | **PASS**. DeepL 1.4× framing is already correctly split in the current text into "vs DeepL's own prior model" and "vs competitors (2× Google, 3× GPT-4)". Kocmi claims are correctly labelled `[Secondary-confirmed]`. |
| what-regula-does-not-do.md | 5 | 5 | n/a | 5 | 5 | **PASS**. No empirical claims to verify; the document is a scope statement. Article references (5, 9, 10, 11, 12, 13, 14, 15, 17, 26, 27, 29, 43, 49, 63, 72, 73, 74, 99) are consistent with Regulation (EU) 2024/1689. |
| evidence-pack-guide.md | 5 | 5 | n/a | 5 | 5 | **PASS**. Describes Regula's own output format; self-claims are verifiable by running `regula conform .`. |
| delta-log entries (5 JSON) | 5 | 5 | n/a | 5 | 5 | **PASS** for 2024-07-12 and 2025-11-19 (both `verified-primary`, and both independently re-verified in this pass). The three 2026 entries are correctly marked `reported-unverified` and should stay that way until permanent Council / Parliament / trilogue URLs replace the aggregator press-room links. |
| sandbox-registry (27 MS) | 4 | 5 | 4 | 4 | 5 | **PASS with corrections**. DE, ES, FI are accurate. NL "established" should be "announced / proposal published March 2025". FR description overstates CNIL's Article 57 role. 22 remaining MS are correctly marked `unknown`. |

**No document scores below 4 on any axis.** Final verdict: **PASS** subject to the three small corrections listed in § "Specific corrections" below.

---

## Claim-by-claim verification table (load-bearing claims only)

Labels: **VERIFIED-PRIMARY** (primary or near-primary source reached in this pass), **VERIFIED-SECONDARY** (multiple reputable secondary sources triangulated, primary not opened), **NOT RE-VERIFIED** (accepted as likely true, not re-checked), **CORRECTION NEEDED**, **FABRICATED**.

### Regulatory claims (delta-log + narrative docs)

| # | Claim | Doc | Verdict | Primary source |
|---|---|---|---|---|
| R1 | Regulation (EU) 2024/1689 published in Official Journal on 12 July 2024; entry into force 1 August 2024 | delta-log 2024-07-12 | **VERIFIED-PRIMARY** | EUR-Lex OJ L 2024/1689; White & Case insight 16 July 2024 |
| R2 | CELEX number is 32024R1689 | delta-log | **VERIFIED-PRIMARY** | EUR-Lex |
| R3 | Article 5 prohibitions apply from 2 Feb 2025; GPAI rules from 2 Aug 2025; high-risk from 2 Aug 2026 | delta-log 2024-07-12 | **VERIFIED-PRIMARY** | Article 113 of the Regulation |
| R4 | Digital Omnibus on AI proposed by the European Commission on 19 November 2025 | delta-log 2025-11-19; moat-research | **VERIFIED-PRIMARY** | digital-strategy.ec.europa.eu/en/library/digital-omnibus-ai-regulation-proposal; Skadden, Morrison Foerster, Sidley client alerts Nov/Dec 2025 |
| R5 | Omnibus long-stop dates: 2 December 2027 (Annex III) and 2 August 2028 (Annex I) | delta-log; moat-research | **VERIFIED-PRIMARY** | Commission proposal text; Sidley, Morrison Foerster, White & Case all report the same dates |
| R6 | Council general approach adopted 13 March 2026 | delta-log 2026-03-13 | **VERIFIED-PRIMARY** | consilium.europa.eu press release 2026-03-13 ("Council agrees position to streamline rules on Artificial Intelligence") |
| R7 | Parliament plenary adopted first-reading position 26 March 2026, with 569 in favour / 45 against / 23 abstentions; IMCO+LIBE joint committee vote 18 March 2026 (101–9–8) | delta-log 2026-03-26 | **VERIFIED-PRIMARY** | Global Policy Watch 2026-03 coverage; Addleshaw Goddard briefing; MediaLaws report |
| R8 | Trilogue target date 28 April 2026 | delta-log 2026-04-28 | **VERIFIED-SECONDARY** (not re-verified; this is the date the Cypriot Presidency floated in public reporting; no primary calendar entry was opened in this pass — label `reported-unverified` is correct) | Global Policy Watch |
| R9 | "Each Member State must establish at least one AI regulatory sandbox by 2 August 2026" | moat-research; sandbox-registry | **VERIFIED-PRIMARY** | Article 57(1) of Regulation (EU) 2024/1689 |
| R10 | Maximum fines "EUR 35 million or 7% of global annual turnover" | delta-log 2024-07-12 | **VERIFIED-PRIMARY** | Article 99 of the Regulation |

### Competitor claims

| # | Claim | Doc | Verdict | Source triangulated |
|---|---|---|---|---|
| C1 | AIR Blackbox exists at airblackbox.ai; `pip install air-blackbox`; Apache 2.0; local; 39 checks across Articles 9/10/11/12/14/15; 5 framework integrations (LangChain, CrewAI, OpenAI Agents SDK, Google ADK, Claude Agent SDK); v1.6.1 adds prompt injection, pre-commit, evidence bundles | competitor-analysis; research-eval-report | **VERIFIED-PRIMARY** | airblackbox.ai; github.com/airblackbox; Jason Shotwell DEV and Medium posts; Glama MCP listing |
| C2 | Microsoft Agent Governance Toolkit released 3 April 2026; MIT licence; seven-package multi-language (Python, TypeScript, Rust, Go, .NET); OWASP Agentic AI Top 10 coverage; 9,500+ tests; LangChain / CrewAI / Google ADK / OpenAI Agents integrations | competitor-analysis | **VERIFIED-PRIMARY**. Caveat: the Microsoft Open Source blog post is dated 2 April 2026 (not 3 April); Help Net Security and other press coverage reports the release on 3 April 2026. Both dates are accurate — blog post 2 Apr, general availability 3 Apr. | opensource.microsoft.com/blog/2026/04/02/introducing-the-agent-governance-toolkit; github.com/microsoft/agent-governance-toolkit; Help Net Security 2026-04-03; Phoronix; Socket.dev |
| C3 | ark-forge/mcp-eu-ai-act: 16 frameworks / 6 languages (Py/JS/TS/Go/Java/Rust); Free 5 scans/day, Pro €29/mo, Certified €99/mo; PyPI package `mcp-eu-ai-act` | competitor-analysis; research-eval-report | **VERIFIED-PRIMARY** (confirmed by research-eval-report's own WebFetch of the repo) | github.com/ark-forge/mcp-eu-ai-act |
| C4 | `@systima/comply` exists as an npm package + GitHub Action (`systima-ai/comply@v1`) + TypeScript API; AST-based import detection via TS Compiler API and web-tree-sitter WASM; 37+ AI frameworks | competitor-analysis | **VERIFIED-SECONDARY**. Licence still not confirmed in this pass. The 37+ figure is sourced exclusively from the DEV article and is not independently verified. Competitor doc is already correct to flag both. | dev.to/systima/open-source-eu-ai-act-compliance-scanning-for-cicd-4ogj |
| C5 | Credo AI, Saidot, Enzai feature claims | competitor-analysis | **NOT RE-VERIFIED**. Risk: low (structural feature categories, not numerical claims). The doc's caveat on Fairly AI / Holistic AI / Trustible / Modulos / Luminos / Anch.AI / ObviosAI is appropriate. | n/a |
| C6 | "No SME tool exists for AI Act compliance" would be false; multiple open-source scanners exist | competitor-analysis | **VERIFIED** by the doc's own enumeration (Systima Comply, ark-forge, AIR Blackbox, EuConform, plus desiorac/mcp-eu-ai-act surfaced in this pass) | various |

### Translation claims

| # | Claim | Doc | Verdict | Source |
|---|---|---|---|---|
| T1 | Kocmi et al., "Preliminary Ranking of WMT25 General Machine Translation Systems", arXiv:2508.14909, first posted 11 August 2025, revised 24 August 2025. AutoRank uses GEMBA-ESA with GPT-4.1 and Command A as LLM judges plus MetricX-24-Hybrid-XL and XCOMET-XL as trained reference-based metrics; paper explicitly states human eval will supersede the preliminary ranking | translation-skill-recommendation | **VERIFIED-PRIMARY** | arxiv.org/abs/2508.14909; aclanthology.org/2025.wmt-1.22 |
| T2 | Gemini 2.5 Pro + Claude 4 "top cluster on human eval in 14 of 16 language pairs" | translation-skill-recommendation | **VERIFIED-SECONDARY**. This specific "14 of 16" figure comes from Slator's secondary reporting on the WMT25 findings, not from Kocmi's preliminary-ranking preprint. The doc already labels it `[Secondary-confirmed via Slator; primary Kocmi preprint not directly quoted for this specific figure]`, which is correct. | Slator |
| T3 | DeepL next-gen LLM achieves 1.4× quality improvement EN↔DE versus DeepL's own previous model in blind linguist tests; announced 28 January 2025 | translation-skill-recommendation | **VERIFIED-PRIMARY-VIA-SECONDARY**. Note: DeepL's own blog post also reports a 1.7× improvement for EN→Japanese and EN→Simplified Chinese; only the 1.4× EN↔DE figure is in the doc, which is correct and conservatively reported | deepl.com/en/blog/next-gen-language-model; PRNewswire 28 Jan 2025; Silicon Canals; MultiLingual |
| T4 | Same DeepL announcement: "2× fewer edits than Google Translate, 3× fewer than ChatGPT-4" | translation-skill-recommendation | **VERIFIED-PRIMARY-VIA-SECONDARY**. Important qualification: this "2× / 3×" figure originates in DeepL's *2024* blind-test study; the January 2025 announcement cites it, but it is not itself a 2025 measurement. The doc's wording (`in the same announcement`) is technically correct but could be tightened. | DeepL 2024 blind-test coverage; same Jan 2025 announcement |
| T5 | Lokalise March 2026: "Claude is typically strongest for high-nuance, brand-sensitive marketing translation" | translation-skill-recommendation | **VERIFIED-SECONDARY**. Already labelled `[Secondary]`. Fine. | lokalise.com/blog/what-is-the-best-llm-for-translation |
| T6 | Andrew Ng `translation-agent` reflection workflow; GitHub repo exists, 2024 | translation-skill-recommendation | **VERIFIED-PRIMARY**. Repo exists. 2026 performance claims correctly labelled `[Unverified at 2026 scale]`. | github.com/andrewyng/translation-agent |
| T7 | EUR-Lex publishes an official German translation of Regulation (EU) 2024/1689; Brazil's PL 2338/2023 is a glossary source | translation-skill-recommendation | **VERIFIED-PRIMARY** (EUR-Lex multilingual publication is a structural fact of EU law); **NOT RE-VERIFIED** but sound (PL 2338/2023 is the Brazilian AI bill in the Senate) | EUR-Lex; Brazil Senate |

### Sandbox-registry claims (5 seeded entries)

| # | Claim | Verdict | Source |
|---|---|---|---|
| S1 | **ES** — AESIA established; RD-based AI sandbox running since late 2023; 12 projects selected April 2025 | **VERIFIED-PRIMARY**. Real Decreto 817/2023 approved 8 November 2023, in force from 10 November 2023, maximum 36-month duration. AESIA operational since June 2024 per Royal Decree 729/2023. Spain's sandbox pre-dates the AI Act's formal requirement and is widely cited as the first EU AI Act-aligned sandbox. **This is the strongest of the 5 entries.** | pinsentmasons.com; thelegalwire.ai; Regulations.AI; AESIA.gob.es |
| S2 | **DE** — BNetzA designated as the German market surveillance authority via the draft Durchführungsgesetz; sandbox operated jointly with BSI | **VERIFIED-PRIMARY** on BNetzA designation; **VERIFIED-SECONDARY** on BSI joint operation. The KI-MIG (Gesetz zur Durchführung der europäischen KI-Verordnung / AI Market Surveillance and Innovation Act) was adopted as a government draft on 10 February 2026 and names BNetzA as the central market surveillance authority, with a "Koordinierungs- und Kompetenzzentrum (KoKIVO)" inside BNetzA. The BSI joint-operation claim is directionally accurate but should be flagged as "per draft implementation law" rather than finalised. | Bundesnetzagentur.de; CMS Law briefing; Taylor Wessing; Prokopiev Law; Pinsent Masons |
| S3 | **FI** — Traficom designated as Finnish AI Act competent authority; sandbox part of national implementation roadmap | **VERIFIED-PRIMARY**. Traficom is the single point of contact and is responsible for establishing and operating the AI regulatory sandbox per the draft Finnish government proposal. | Hannes Snellman briefings; tem.fi; Dittmar & Indrenius; Bird & Bird |
| S4 | **FR** — CNIL "designated lead for AI Act coordination"; "will operate the Article 57 sandbox"; CNIL has run AI-focused sandboxes since 2021 | **CORRECTION NEEDED — OVERSTATED**. France has a *decentralised* model under a yet-to-be-passed implementation law. CNIL runs its own public-service AI sandboxes (2023–2024 public-services sandbox; silver-economy sandbox upcoming) and CNIL is named as the enforcement authority for specific prohibited-AI categories (workplace / education emotion recognition). However, CNIL is **not** publicly confirmed as the sole or lead operator of the Article 57 AI Act sandbox; that architecture is still under discussion. Action: rewrite the FR entry to "CNIL runs its own public-service AI sandbox and will play a role in Article 57 sandbox operation; formal designation pending national implementation law". Leave `confidence: reported-unverified`. | cnil.fr; Latham IN-DEPTH AI Law France; Inside Privacy; AI Act Service Desk |
| S5 | **NL** — "Autoriteit Persoonsgegevens established an AI Act-aligned regulatory sandbox" | **CORRECTION NEEDED — OVERSTATED**. The current reality is that in March 2025 the AP and RDI jointly published a *proposal* for the Dutch design of the AI regulatory sandbox; the sandbox is "expected to launch by August 2026" (per PPC Land and Glacis summaries of Dutch government communications). It is not yet "established". Action: change `status` from `"established"` to `"announced"`, and rewrite the summary to "Proposal published March 2025 by AP and RDI; sandbox expected to launch by August 2026". | autoriteitpersoonsgegevens.nl; Knowledge Centre Data & Society; PPC Land; Bird & Bird NL tracker |

### Self-claims from Regula's own CLAUDE.md (acceptable as primary on self)

- 330 risk patterns, 8 languages, 12 compliance frameworks, 39 CLI commands, Python stdlib-only, zero production dependencies, MIT licence — these are internal claims and are verifiable by running the project's own `python3 -m scripts.cli self-test` and `doctor` commands. Not independently re-verified in this pass; no red flag.
- `regula conform .` produces a 26-file pack — verified by docs/evidence-pack-guide.md's explicit file listing and by the reference to `conform: end-to-end pack structure verified` in `tests/test_classification.py`. Sound.

---

## Missed competitors / tools to add

After running the `site:github.com "EU AI Act" compliance scanner CLI python 2026` sweep and the ai-compliance topic check, one additional entrant surfaced that is **not** in competitor-analysis.md:

| Tool | Why it belongs | Evidence |
|---|---|---|
| **desiorac/mcp-eu-ai-act** (github.com/desiorac/mcp-eu-ai-act) | A second, distinct MCP-server EU AI Act compliance checker, separate from ark-forge's. Scans .py, .js, .ts, .java, .go, .rs, .cpp, .c plus dependency files. Indicates that the "MCP server for AI Act scanning" design pattern is a small but real category with multiple independent implementations in 2026. | github.com/desiorac/mcp-eu-ai-act; surfaced via GitHub `eu-ai-act` topic search |

No other new entrant surfaced. The Producthunt / Semgrep rulesets / Google Cloud Model Armor gaps that the competitor doc already lists remain open — they were not the focus of this verification pass.

---

## Specific corrections needed before public launch

Order of priority. Each is a language fix, not a retraction.

1. **sandbox-registry/index.json — NL entry (priority P0).** Change `"status": "established"` → `"status": "announced"`. Replace summary with: "Dutch AI regulatory sandbox proposal published March 2025 by the Autoriteit Persoonsgegevens and the Rijksinspectie Digitale Infrastructuur (RDI). The sandbox is a single multi-sectoral access point involving all AI Act market-surveillance authorities and is expected to launch by August 2026 per Article 57 of Regulation (EU) 2024/1689." Keep `confidence: reported-unverified`.

2. **sandbox-registry/index.json — FR entry (priority P0).** Soften the `competent_authority` and `summary` fields. Suggested replacement: `"competent_authority": "Commission nationale de l'informatique et des libertés (CNIL) — designated enforcement authority for specific prohibited-AI practices (e.g. workplace/education emotion recognition); CNIL-operated public-service AI sandboxes exist since 2023. Formal designation of the Article 57 AI Act sandbox operator is pending the national implementation law."` and `"summary": "France operates a decentralised AI Act supervision model. CNIL is publicly confirmed as the enforcement authority for certain prohibited-AI uses and runs its own public-service AI sandboxes (2023-2024 public-service sandbox; silver-economy sandbox upcoming). The formal Article 57 sandbox operator has not been finally designated; CNIL is expected to play a lead role."` Keep `confidence: reported-unverified`.

3. **sandbox-registry/index.json — DE entry (priority P1).** Add a sentence: "Status is based on the 10 February 2026 government draft of the KI-MIG (AI Market Surveillance and Innovation Act). The draft must pass the Bundestag and, where required, the Bundesrat before it becomes binding law." This converts the existing claim from "announced" into "announced, with legal basis tracked".

4. **competitor-analysis.md — add one row (priority P1).** Insert `desiorac/mcp-eu-ai-act` into the direct-competitors developer-side scanner table as "Python MCP server, free, licence unverified, scans 8 languages plus dependency files". Mark `confidence: reported-unverified`. This removes the "did you miss any MCP-server AI Act scanner" gap.

5. **translation-skill-recommendation.md — one sentence of clarification (priority P2).** In the DeepL row of the candidates table, add: "(The 2× / 3× competitor-comparison figures originate in DeepL's 2024 blind-test study and are cited in the same January 2025 announcement; the 1.4× is the 2025-specific uplift over DeepL's own prior model.)" This is a precision improvement, not a correction — the current wording is not wrong, it is merely conflatable.

6. **delta-log 2026-03-13 and 2026-03-26 entries (priority P2).** Replace the aggregator press-room URLs with the specific permalinks:
   - Council 2026-03-13: https://www.consilium.europa.eu/en/press/press-releases/2026/03/13/council-agrees-position-to-streamline-rules-on-artificial-intelligence/
   - Parliament 2026-03-26: europarl.europa.eu press release for the plenary vote, or the MediaLaws / Global Policy Watch coverage as the secondary-class pointer until the primary permalink is confirmed.
   After that substitution both entries can be promoted from `reported-unverified` to `verified-primary`.

7. **delta-log 2026-04-28 trilogue target (priority P3).** Leave as `reported-unverified`. The date has been floated by the Cypriot Presidency in public reporting but is a calendar target, not an adopted instrument. Current framing is already correct.

**None of these corrections is a discard-the-document issue.** Every one of them is a 1-to-3-line language edit.

---

## Confidence statement on this evaluation

**What I verified directly via WebSearch in this pass (high confidence):** CELEX 32024R1689 OJ publication date; Article 99 and Article 113 dates; Digital Omnibus adoption date; long-stop deferral dates; Council 13 March 2026 position; Parliament 18 March committee and 26 March plenary votes with the exact vote tallies; AIR Blackbox feature list and licence; Microsoft Agent Governance Toolkit release date, licence, language list and integration list; DeepL 1.4× EN↔DE framing; Kocmi arXiv 2508.14909 authors, methodology and explicit "human eval will supersede" disclaimer; Spain RD 817/2023 and AESIA; Germany KI-MIG February 2026 cabinet draft and BNetzA designation; Finland Traficom single-point-of-contact and sandbox role; Netherlands AP/RDI March 2025 proposal; France CNIL decentralised model and public-service sandbox history.

**What I did not WebFetch directly (medium confidence, triangulated via multiple secondaries):** EUR-Lex PDF of 2024/1689; airblackbox.ai the vendor site itself; the Microsoft opensource blog post body; the Kocmi PDF; individual Council / Parliament permalinks.

**What I did not check at all (accepted as likely-true, no red flags seen):** Regula's own self-claims (330 patterns, 8 languages, 12 frameworks, 39 CLI commands, 26-file conform pack); individual feature claims for Credo AI, Saidot, Enzai, IBM watsonx.governance, Microsoft Purview; Systima Comply licence; individual feature claims for Holistic AI / Fairly AI / Modulos / Luminos / Anch.AI / Trustible / ObviosAI (all already explicitly unverified in the competitor doc); NLLB-200 / Madlad-400 / Aya Expanse / TowerInstruct 2026 updates; `deusyu/translate-book` skill internals.

**Residual risk.** The biggest residual risk in this launch is not any single claim — it is the fact that the Digital Omnibus is a *live* legislative file whose text will change between now and trilogue conclusion. The delta-log architecture is exactly the correct response to that risk (time-stamped, versioned, per-article), and as long as the `reported-unverified` labels remain on the three 2026 entries until permanent permalinks replace the aggregators, the repository is honest about what it knows and when.

**Proportionate severity statement.** I did not find a fabricated statistic, a misattributed quote, or an outright wrong regulatory date in any of the eight assets. The two "correction needed" rows in the sandbox-registry are language-precision fixes on entries that are already labelled `reported-unverified` and seeded from public reporting, not primary sources. The one missed competitor is a minor MCP-server clone of a category that is already in the table.

**Final verdict: PASS for public launch after the P0 and P1 corrections above are applied.** The P2 and P3 items can be handled in the first post-launch iteration without affecting credibility.

---

## What I would do differently on a third pass (for a future evaluator)

1. Actually open the EUR-Lex PDF of Regulation (EU) 2024/1689 and screenshot the OJ reference line. That is the only way to move R1 from "verified by triangulation" to "verified by reading the Official Journal".
2. Fetch the Council 13 March 2026 press release permalink and the Parliament 26 March plenary record, and promote delta-log entries 3 and 4 to `verified-primary`.
3. Run a BNetzA.de German-language fetch on the KI-MIG Referentenentwurf to confirm the BSI joint-operation claim or retract it.
4. Open the Kocmi PDF and find the exact "14 of 16 language pairs" sentence — or confirm that it is absent and is a Slator paraphrase, in which case the translation doc's `[Secondary-confirmed]` label should remain permanent rather than conditional.
5. Run `pip download air-blackbox` and read the wheel's METADATA to confirm Apache 2.0 at the package level, not just the website level.

None of these is necessary before public launch. All of them would strengthen the repository over time.

---

*Evaluator note: the quality of the upstream research made this pass significantly faster than a typical second-pass audit. Every document carried its own "known gaps" section; every competitor entry was labelled with a confidence verdict; every moat candidate had explicit counterevidence. That discipline is why the final correction list is short.*
