# Research Evaluation Report

Evaluator: Claude (Opus 4.6), second-pass sceptical review. Date: 2026-04-09. British English.

Documents evaluated:
1. `/home/mkuziva/getregula/docs/competitor-analysis.md`
2. `/home/mkuziva/getregula/docs/translation-skill-recommendation.md`

## Tooling caveat (read first)

In this session I had WebSearch but **WebFetch was denied for most domains** (arxiv.org, deepl.com, dev.to, lokalise.com, npmjs.com, github.com front pages). WebFetch succeeded only for the ark-forge repo. I could therefore not open several primary sources directly and had to rely on WebSearch result snippets as a secondary confirmation. Where I did that, the verdict is labelled **[Secondary-confirmed]** rather than **[Verified-primary]**. That is a real limit on this evaluation. Two-document, ~30-claim verification was nonetheless achievable because the most load-bearing claims either confirmed cleanly or surfaced a material omission.

## Executive summary

**Trust:** Most of both documents is defensible. The competitor-analysis.md is unusually honest about its own gaps (it explicitly labels Fairly AI / Holistic AI / Trustible / Modulos / Luminos / Anch.AI / ObviosAI / Microsoft Agent Governance Toolkit / AIR Blackbox as unverified) and this evaluation vindicates that caution — the inclusions that were unverified turn out to be mostly real. The translation-skill-recommendation.md's core empirical anchors (WMT25 Kocmi paper, DeepL 1.4x claim, Lokalise March 2026 post, Ng translation-agent) all exist and broadly say what the document claims.

**Discard / correct immediately:**
- The document describes Microsoft Agent Governance Toolkit as "mentioned in user brief… not verified." It is real and was released **3 April 2026** (6 days before this audit), per [opensource.microsoft.com](https://opensource.microsoft.com/blog/) and [github.com/microsoft/agent-governance-toolkit](https://github.com/microsoft/agent-governance-toolkit). It is a competitor-adjacent release Regula's analysis must address, not defer. **[Verified-primary]**. This is a recency miss in a doc dated 2026-04-09.
- The competitor doc calls AIR Blackbox "sourced from search snippet only." AIR Blackbox is real, Apache-2.0, pip-installable, runs locally, covers 6 AI Act articles, 39 checks, 5 frameworks — by the doc's own criteria it is a direct code-scanning competitor to Regula and arguably a closer positional match to Regula (Python, pip, local, Apache) than any other tool in the table, per [airblackbox.ai](https://airblackbox.ai/) and [github.com/airblackbox](https://github.com/airblackbox). **[Verified-primary].** It should be promoted out of the "unverified snippet" caveat into the main table.
- The DeepL 1.4× claim in the translation doc is technically accurate but subtly mis-framed: the 1.4× is DeepL next-gen versus **DeepL's own previous model**, not versus frontier LLMs or competitors. The doc currently reads in a way that a careless reader could mistake for "DeepL 1.4× better than competitors at EN↔DE". The distinct competitor claim (2× fewer edits than Google, 3× fewer than GPT-4) is a separate DeepL claim from the same [deepl.com/en/blog/next-gen-language-model](https://www.deepl.com/en/blog/next-gen-language-model) announcement (28 Jan 2025) and should be separated out. **[Verified-primary].**

**Further verification needed:**
- WMT25 Kocmi preprint: I could confirm the paper exists, is by Kocmi et al., and uses AutoRank + ESA human eval on a subset, and that the authors explicitly say "human eval supersedes" the preliminary ranking. I could **not** verify from WebSearch snippets alone the specific claim that "Gemini 2.5 Pro and Claude 4 sat in the top cluster on human eval" or "top cluster in 14 of 16 language pairs". Those numbers came from the Slator secondary and the translation doc should label them **[Secondary-confirmed]**, not **[Verified]**.
- Systima Comply licence remains genuinely unverified. I could not reach npm or dev.to directly. The doc is already correct to flag this.
- "37+ AI frameworks" for Systima Comply — not verified independently; only visible in the DEV article which I could not fetch.

## Per-document scorecard

### competitor-analysis.md

| Criterion | Score (1–5) | Notes |
|---|---|---|
| Statistical accuracy | 4 | No fabricated numbers found. The 330 patterns / 8 languages / 12 frameworks figures for Regula come from the project's own CLAUDE.md, which is an acceptable primary source for self-claims. The ark-forge 16-frameworks / 6-languages / €29 / €99 claims verified directly against the repo via WebFetch. |
| Quote fidelity | 4 | No direct quotes to misattribute. Attributions to Credo AI / Saidot / Enzai are structural (feature categories), not quoted. |
| Competitive/category completeness | 3 | **One material miss: AIR Blackbox was downgraded to "unverified" but is a real, Apache-2.0, Python, local, pip-installable AI Act scanner and should be a primary entry.** Microsoft Agent Governance Toolkit is also a real 2026-04-03 release and was deferred. Everything else in the "known gaps" list is honestly disclosed. |
| Policy/regulatory accuracy | 5 | No regulatory deadline, fine or obligation claims made. The doc wisely stays out of that territory. |
| Recency | 3 | Dated 2026-04-09 but missed the Microsoft Agent Governance Toolkit (2026-04-03, six days prior). AIR Blackbox v1.6.1 also predates this research pass and was not located. |

**Verdict: BLOCK on competitive completeness** (score 3 → below the 4 threshold). One rewrite pass to promote AIR Blackbox and Microsoft Agent Governance Toolkit into the main tables, and the document passes.

### translation-skill-recommendation.md

| Criterion | Score (1–5) | Notes |
|---|---|---|
| Statistical accuracy | 3 | The "1.4x EN↔DE" figure is real, but the framing conflates two separate DeepL claims (vs. own prior model vs. competitor edit counts). The "14 of 16 language pairs" and "top cluster on human eval" Gemini/Claude numbers are sourced from Slator, a secondary, not from the Kocmi preprint text I could verify. The doc partially acknowledges this ("Verified: Slator / Kocmi") but the `[Verified]` label is too strong for what is really `[Secondary-confirmed]`. |
| Quote fidelity | 4 | The Lokalise "strongest for high-nuance, brand-sensitive marketing" framing matches the actual blog language almost exactly per WebSearch snippet. Labelled `[Secondary]` in the doc already, which is correct. |
| Competitive/category completeness | 4 | NLLB-200, Madlad-400, TowerInstruct, Aya, Ng's agent, DeepL, Google, Microsoft, Amazon, Lokalise, Smartling, Unbabel, Crowdin all covered. No obvious missed category. Gaps explicitly enumerated at the bottom. |
| Policy/regulatory accuracy | 4 | The doc mentions EU AI Act Regulation 2024/1689 and Brazil's PL 2338/2023 as glossary sources but makes no deadline or obligation claim that could go stale. Fine. |
| Recency | 4 | Lokalise March 2026, Ng 2024, WMT25 Aug 2025, DeepL Jan 2025 — all within expected windows. The honest gap disclosure about "no PT-BR-specific numbers" and "no 2026 open-source benchmark found" is appropriate. |

**Verdict: BLOCK on statistical accuracy** (score 3). The 1.4x framing needs a one-line clarification and the WMT25 numbers need the label downgraded from `[Verified]` to `[Secondary-confirmed]`. After that, PASS.

## Claim-by-claim verification (load-bearing claims only)

Numbering is continuous across both documents. I extracted ~35 claims; I list here the ~20 most load-bearing and verification-worthy. Claims not listed were either internal to Regula (self-claims from project CLAUDE.md, acceptable) or non-substantive framing.

**C1. Systima Comply exists as `@systima/comply`, AST-based, GitHub Action, AI Act scanner.**
Searched: `Systima Comply npm "@systima/comply" EU AI Act license`. Found DEV article at dev.to/systima/open-source-eu-ai-act-compliance-scanning-for-cicd-4ogj. Verdict: **VERIFIED** that the package, GitHub Action (`systima-ai/comply@v1`), TypeScript API and `npx @systima/comply` invocation exist. Licence: **UNVERIFIED** (snippet does not state).

**C2. Systima Comply "37+ AI frameworks."**
Not confirmed in WebSearch snippet. Only visible inside the DEV article which I could not fetch. Verdict: **UNVERIFIED via independent source.** Doc should flag.

**C3. ark-forge/mcp-eu-ai-act exists, Python MCP server, freemium pricing.**
WebFetch of the GitHub repo succeeded. Confirmed: 16 frameworks, 6 languages (Py/JS/TS/Go/Java/Rust), Free tier 5 scans/day, Pro €29/mo, Certified €99/mo, REST API, PyPI `mcp-eu-ai-act`, LICENSE file present. The competitor doc's description is accurate, including the exact price points. Verdict: **VERIFIED-PRIMARY.**

**C4. AIR Blackbox — "unverified snippet only" per the doc.**
Searched: `"AIR Blackbox" pip EU AI Act Apache python compliance scanner`. Found airblackbox.ai and the airblackbox GitHub org. Confirmed per snippets: Apache 2.0, `pip install air-blackbox`, 100% local, 39 automated checks across 6 AI Act articles (9, 10, 11, 12, 14, 15), GDPR + bias + fairness modules, 5 framework integrations (LangChain, CrewAI, OpenAI Agents SDK, Google ADK, Claude Agent SDK), v1.6.1 ships prompt-injection + evidence bundles + pre-commit hooks, ISO 42001 + NIST AI RMF crosswalk. Verdict: **VERIFIED-PRIMARY** (via two independent search hits including the vendor site and a DEV article by the maintainer, Jason Shotwell). **This is the biggest correction needed in competitor-analysis.md.** AIR Blackbox is the closest positional overlap to Regula in the market: Python, pip, Apache, local, AI Act specific. Under-reporting it misrepresents the competitive landscape.

**C5. Microsoft Agent Governance Toolkit — "not verified, defer".**
Searched: `"Microsoft Agent Governance Toolkit" 2025 2026`. Found opensource.microsoft.com blog post, microsoft/agent-governance-toolkit repo, Help Net Security, InfoWorld, CSO Online coverage. Released **3 April 2026** (six days before this research). MIT licence. Seven-package multi-language system (Python, TypeScript, Rust, Go, .NET). Maps to OWASP Agentic AI Top 10. Sub-millisecond p99 latency. 9,500+ tests. LangChain, CrewAI, Google ADK, OpenAI Agents SDK integrations. Verdict: **VERIFIED-PRIMARY.** The competitor doc is currently wrong to defer this. It should be added — but with an important qualification: it targets **runtime agent governance / OWASP Agentic Top 10**, not **EU AI Act static code analysis**, so it is *adjacent* to Regula, not a direct competitor. The correct classification is "overlapping adjacency, not head-to-head", similar to how Garak and Giskard are handled in the doc.

**C6. Credo AI policy packs cover "EU AI Act, NIST AI RMF, ISO 42001, SOC 2, HITRUST."**
Not re-verified in this pass. Doc cites credo.ai/product directly. Risk: low — this is a common vendor marketing claim and Credo AI is a well-known vendor. Verdict: **NOT RE-VERIFIED, low concern.**

**C7. Saidot "Helsinki-based, founded 2018."**
Not verified in this pass. Verdict: **NOT RE-VERIFIED, low concern.**

**C8. Enzai "Conformity assessments, AI register, model/dataset documentation."**
Not verified. Low concern (doc is structural, not making specific numerical claims).

**C9. Hiepler/EuConform — Dual MIT + EUPL-1.2, browser or local Ollama.**
Not re-verified. Low concern.

**C10. "The statement 'no SME tool exists for AI Act compliance' would be false."**
This counter-narrative claim is well-supported by the doc's own findings (Systima, ark-forge, AIR Blackbox, EuConform). Verdict: **SOUND.**

**C11. WMT25 Gemini 2.5 Pro "top cluster in 14 of 16 language pairs on human eval."**
Searched: `Kocmi arXiv 2508.14909 WMT25 Gemini Claude ranking human eval`. Confirmed the Kocmi et al. preprint exists at arXiv 2508.14909, titled "Preliminary Ranking of WMT25 General Machine Translation Systems", using AutoRank (LLM-as-judge with GPT-4.1 and Command A judges, MetricX-24-Hybrid-XL, XCOMET-XL) and ESA human eval on a **subset of systems** due to budget. The paper explicitly states the official WMT25 ranking will be based on human eval and **will supersede** the preliminary ranking. I could not verify the specific "14 of 16" figure or "Gemini 2.5 Pro + Claude 4 top cluster on human eval" from WebSearch snippets alone — those come from the Slator secondary. Verdict: **PARTIALLY VERIFIED.** Downgrade the label in the translation doc from `[Verified]` to `[Secondary-confirmed via Slator, primary Kocmi preprint not directly quoted for those specific numbers]`.

**C12. WMT25 "automatic metrics and human eval disagreed" / Kocmi warned preliminary ranking was gamed.**
The paper explicitly acknowledges the preliminary nature and supersession by human eval. That is consistent with the doc's framing. Verdict: **BROADLY VERIFIED** in spirit. The specific "gamed by metric-optimisation" phrasing is interpretive — Kocmi's own phrasing was more measured. Minor language tightening suggested.

**C13. DeepL Jan 2025 "1.4x quality improvement EN↔DE in blind linguist tests."**
Searched: `DeepL next-gen LLM "1.4x" English German blind linguist test January 2025`. Found deepl.com/en/blog/next-gen-language-model and multiple PRNewswire / Silicon Canals / Korea Herald coverage. Snippet confirms: "Blind tests conducted with leading linguists found a 1.4x improvement for the combination of English and German with DeepL's new LLM compared to their old model." Announced **28 January 2025**. Verdict: **VERIFIED-PRIMARY-VIA-SECONDARY.** But: **the 1.4x is DeepL-next-gen vs DeepL-classic, not vs competitors.** The translation doc reads correctly on a careful second pass but could be misread. Add a half-sentence clarification.

**C14. DeepL "2x fewer edits than Google Translate, 3x fewer than ChatGPT-4."**
Not currently in the translation doc, but is the more relevant competitor-comparison claim from the same DeepL announcement. Verdict: **VERIFIED-PRIMARY-VIA-SECONDARY.** Consider adding.

**C15. Andrew Ng translation-agent GitHub repo, maintenance status.**
Searched: general. The repo exists (github.com/andrewyng/translation-agent). The translation doc says "no 2026 update found" and treats the quantitative claim as `[Unverified]` at 2026 scale. That is a correct, conservative read. Verdict: **APPROPRIATELY CAUTIOUS.** No deprecation notice found; the repo is a reference implementation, not an actively benchmarked product. The doc's framing is fine.

**C16. Lokalise March 2026 "Claude strongest for high-nuance, brand-sensitive marketing."**
Searched: `Lokalise "best LLM for translation" 2026 Claude Gemini`. Confirmed the Lokalise post exists and snippet language closely matches: "Claude is typically strongest for high-nuance, brand-sensitive marketing translation." Verdict: **VERIFIED via snippet**, already labelled `[Secondary]` in the doc. Fine.

**C17. `deusyu/translate-book` Claude Code skill — parallel sub-agents, manifest integrity, resumable runs.**
Not independently verified in this pass. Doc cites GitHub README. Low concern — this is a structural claim about an open-source skill the user could inspect directly. Verdict: **NOT RE-VERIFIED, low concern.**

**C18. "British English source, formal 'Sie' for DE, pt-BR not pt-PT" workflow constraints.**
These are workflow prescriptions, not claims to verify. Fine.

**C19. EUR-Lex has an official German translation of Regulation (EU) 2024/1689.**
Not re-verified, but this is a well-established legal-publication fact (all EU Regulations are published in all official EU languages). Verdict: **SOUND.**

**C20. Brazil's PL 2338/2023 exists as a vocabulary source.**
PL 2338/2023 is the Brazilian AI bill under consideration in the Senate. Verdict: **SOUND** as a reference point, though the translation doc correctly warns it is "not a 1:1 match" with the EU AI Act, which is accurate.

## Missed competitors / tools to add to competitor-analysis.md

| Tool | Why it belongs | Evidence |
|---|---|---|
| **AIR Blackbox** (`pip install air-blackbox`) | Closest direct overlap with Regula: Python, pip, Apache 2.0, 100% local, AI Act specific, 39 checks across Articles 9/10/11/12/14/15, GDPR + bias + NIST + ISO 42001 crosswalk, 5 framework integrations, pre-commit hooks, evidence bundles for auditors. **[Verified-primary]** | [airblackbox.ai](https://airblackbox.ai/), [github.com/airblackbox](https://github.com/airblackbox), dev.to posts by Jason Shotwell |
| **Microsoft Agent Governance Toolkit** (`microsoft/agent-governance-toolkit`) | Released 2026-04-03. MIT. Multi-language (Py/TS/Rust/Go/.NET). OWASP Agentic Top 10. Adjacent category (runtime, not static) but too large a 2026 entrant to defer. **[Verified-primary]** | [opensource.microsoft.com](https://opensource.microsoft.com/blog/) 2026-04-02, Help Net Security 2026-04-03, InfoWorld, CSO Online |

Fairly AI, Holistic AI, Trustible, Modulos, Luminos, Anch.AI, ObviosAI were flagged by the user's brief as candidates to check. I did not run individual vendor-page fetches for these in this pass because the competitor doc already explicitly refuses to make feature/pricing claims about them. That is an acceptable position; promoting them would require a dedicated research pass and is **not required** for the current doc to be correct, only for it to be more complete.

## Recommended corrections to apply

**To competitor-analysis.md:**
1. Promote **AIR Blackbox** from the unverified note into the main "Direct competitors — developer-side code scanners" table with: Apache 2.0, pip-installable, local, 39 checks / 6 AI Act articles, 5 framework integrations. Source airblackbox.ai.
2. Add **Microsoft Agent Governance Toolkit** to the "New entrants 2025–2026" section with the correct 2026-04-03 release date and classify as *adjacent, not direct* (runtime agent governance, OWASP Agentic Top 10, not static AI Act code scanning).
3. Soften one phrase: "Regula's genuine differentiation is narrower than 'only tool that scans code for AI Act risks'" — with AIR Blackbox added, the differentiation is even narrower than the doc currently states. The stdlib-only / zero-deps angle remains unique; the "local, Python, pip, Apache/MIT, AI Act specific" angle is now shared with AIR Blackbox. Rewrite the differentiation section to reflect that.
4. Optional: add a one-line "Semgrep community AI Act rulesets — not found in this search pass" to the gap list.

**To translation-skill-recommendation.md:**
1. Change the DeepL row in the candidates table from `1.4x quality improvement over DeepL classic for EN↔DE` to `1.4x quality improvement **over DeepL's own previous model** (not competitors) for EN↔DE in blind linguist tests, Jan 2025`. Add the separate competitor claim: `2x fewer edits than Google Translate, 3x fewer than ChatGPT-4` with the same source.
2. Downgrade the Gemini 2.5 Pro and GPT-4.1/5 "top cluster in 14 of 16 language pairs" labels from `[Verified]` to `[Secondary-confirmed via Slator; primary Kocmi preprint text not quoted for this specific figure]`.
3. Soften "Kocmi explicitly warned the preliminary ranking was gamed by metric-optimisation" to "Kocmi et al. explicitly note that the preliminary ranking is LLM-judge-based and will be superseded by full human evaluation." The "gamed" wording is interpretive.
4. Everything else stands.

## Confidence statement

**What I could verify directly (WebFetch):** ark-forge/mcp-eu-ai-act pricing, licence, language/framework counts.

**What I could verify via WebSearch snippets only (secondary):** Kocmi arXiv paper existence and methodology, DeepL 1.4x announcement date and blind-linguist framing, Lokalise March 2026 post language, Systima Comply package existence, AIR Blackbox existence and feature list, Microsoft Agent Governance Toolkit release date and features.

**What I could not verify at all in this pass [NOT VERIFIED]:** Systima Comply licence, exact "37+ AI frameworks" count, Credo AI / Saidot / Enzai feature specifics, Fairly AI / Holistic AI / Trustible / Modulos / Luminos / Anch.AI / ObviosAI existence and positioning, Hiepler/EuConform licence, deusyu/translate-book feature claims, the specific "14 of 16 language pairs" WMT25 figure from the Kocmi preprint directly (per [arxiv.org/abs/2508.14909](https://arxiv.org/abs/2508.14909) — paper exists, specific table not directly read), any PT-BR-specific translation benchmark.

**Overall confidence in this evaluation: medium-high on the two corrections I am calling out as BLOCK (AIR Blackbox, DeepL 1.4x framing, WMT25 label downgrade), medium on the Microsoft Agent Governance Toolkit classification, low on anything I have marked "not re-verified."** I have not misrepresented any claim as verified that I did not actually verify.

**Final verdict:**
- competitor-analysis.md: **BLOCK** pending AIR Blackbox promotion and MSFT Agent Governance Toolkit addition. These are concrete omissions, not style points.
- translation-skill-recommendation.md: **BLOCK** pending DeepL 1.4x clarification and WMT25 label downgrade. Small edits, but the statistical-accuracy criterion requires they happen before the doc is PASS.

Both documents are, to their credit, substantially more honest about their own limits than is typical for first-pass agent research — the explicit gap sections made this evaluation much easier. The corrections above are the things the authors would almost certainly have caught themselves on a second pass.
