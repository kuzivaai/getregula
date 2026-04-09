# Translation approach for getregula.com (EN → DE, EN → PT-BR)

Research window: 2026-03-09 to 2026-04-09. Author: Claude (Opus 4.6). British English.

All confidence labels below use: **[Verified]** (primary source, dated), **[Secondary]** (aggregator/vendor blog), **[Unverified]** (no primary source found in the search window).

## TL;DR

Use a **reflection-agent workflow** (Andrew Ng's pattern) driven by **Gemini 2.5 Pro** as primary translator and **Claude Opus 4.6** as reviewer/reflector, with a **human pass against a frozen glossary** for EU AI Act terminology before commit. Fallback: **DeepL next-gen** API for first-draft, then Claude Opus 4.6 reflection pass for tone and technical terms. Do not use raw single-shot LLM calls for landing-page copy. Do not use Google Translate or Microsoft Translator as the primary engine for this domain. All three options keep you auditable and keep DE/PT-BR in sync with the EN source, which is your stated project rule.

## Evaluation criteria

| Criterion | Why it matters for getregula.com |
|---|---|
| Fidelity (adequacy) | Regulatory claims (Art. 6, Annex III, GPAI) must not drift |
| Tone preservation | British English, understated, no "salesly" language |
| Terminology | EU AI Act terms of art must match the official EUR-Lex DE and PT (not PT-BR) renderings where they exist, adapted for pt-BR readability |
| SEO value | Heading structure, meta descriptions, and hreflang consistency |
| Cost | Solo-founder budget; one-shot per article |
| Auditability | You need a diff trail per locale for every content change (repo rule) |

## Candidates

| Name | Type | EN→DE evidence | EN→PT-BR evidence | Cost (approx.) | Source + date |
|---|---|---|---|---|---|
| Gemini 2.5 Pro | Frontier LLM | WMT25 preliminary: top cluster in 14 of 16 language pairs on human eval **[Secondary-confirmed via Slator; primary Kocmi preprint arXiv 2508.14909 not directly quoted for this specific figure]** | Same WMT25 top-cluster ranking; no PT-BR-specific split published | ~USD 1.25/M in, 10/M out | Slator, WMT25 findings PDF (aclanthology 2025.wmt-1.22) |
| GPT-4.1 / GPT-5 family | Frontier LLM | WMT25 preliminary: co-leader with Gemini 2.5 Pro **[Secondary-confirmed via Slator; same caveat as above]** | Same | ~USD 2.50–10/M tokens | Slator WMT25 article |
| Claude 4 / Opus 4.6 | Frontier LLM | WMT25: "second tier, strong but less consistent" on automatic metrics; top cluster on *human* eval alongside Gemini **[Secondary-confirmed via Slator; Kocmi preprint methodology verified]** | Same second tier; Lokalise March 2026 blind study: "strongest for high-nuance, brand-sensitive marketing" **[Secondary: Lokalise blog, Mar 2026]** | ~USD 15/M in, 75/M out | Lokalise blog, Mar 2026 |
| DeepL next-gen LLM | Dedicated MT + LLM | Jan 2025: **1.4× quality improvement over DeepL's own previous model (not vs competitors) for EN↔DE** in blind linguist tests; separate claim in the same announcement: **2× fewer edits than Google Translate, 3× fewer edits than ChatGPT-4** **[Verified-primary via deepl.com/en/blog/next-gen-language-model + PRNewswire, 28 Jan 2025]** | Supported but no published 2026 PT-BR blind-test numbers | EUR 7.49/mo Pro, API pay-as-you-go | deepl.com/en/blog/next-gen-language-model |
| Google Translate | Dedicated NMT | WMT25: "commercial engines remain stable but mid-tier" **[Verified: Slator]** | Same | Low | Slator WMT25 |
| Microsoft / Amazon Translate | Dedicated NMT | Same mid-tier classification **[Verified: Slator]** | Same | Low | Slator WMT25 |
| Andrew Ng `translation-agent` (reflection) | Agentic workflow | BLEU "sometimes competitive with, sometimes worse than commercial", occasionally superior; steerable for tone, idioms, technical terms, names **[Verified: github.com/andrewyng/translation-agent README, 2024]** | Same pattern, language-agnostic | Model-cost only | Ng GitHub repo (no 2026 update found) |
| Lokalise AI / Smartling LanguageAI / Unbabel / Crowdin AI Agent | SaaS workflow | Vendor marketing; no independent 2026 blind benchmarks found in window **[Unverified]** | Same **[Unverified]** | USD 120+/mo | — |
| NLLB-200, Madlad-400, TowerInstruct | Open-source MT | No 2026 release surfaced in search; TowerInstruct and EuroLLM searches returned nothing within the window **[Unverified]** | Same | Self-host | — |
| Aya Expanse 8B/32B | Open multilingual LLM | Covers DE and PT; original release Oct 2024, no 2026 update found in window **[Unverified for 2026]** | Same | Self-host | huggingface.co/blog/aya-expanse |
| `deusyu/translate-book` Claude Code skill | Claude skill | Parallel-subagent translation of long docs, manifest integrity checks, resumable runs **[Verified: GitHub README]** | Same (language-agnostic) | Model-cost only | github.com/deusyu/translate-book |

Key finding from WMT25 that matters most here: **automatic metrics and human eval produced different rankings**. Kocmi et al. explicitly note that the preliminary ranking is LLM-judge-based (AutoRank using GPT-4.1, Command A, MetricX-24-Hybrid-XL, XCOMET-XL) and **will be superseded by the full human evaluation** — the preliminary numbers should not be treated as final. On human eval (which was run on a subset of systems due to budget), Gemini 2.5 Pro and Claude 4 sat in the top cluster; DeepL and the other commercial NMT engines were mid-tier **[Secondary-confirmed via Slator reporting]**. This is the single most load-bearing fact for the recommendation, and it carries the explicit caveat that the final WMT25 ranking may re-order these systems.

## Recommended workflow for getregula.com

1. **Freeze a glossary** (`docs/glossary.eu-ai-act.tsv`) with columns `en | de | pt-br | source`. Seed it from EUR-Lex's official DE translation of Regulation (EU) 2024/1689 and from Brazil's PL 2338/2023 terminology where overlap exists. This is the single highest-leverage step; it makes every downstream pass cheaper.
2. **Source**: write the article in EN on Substack, then export the plain text.
3. **First pass (draft)**: run Ng-style reflection with Gemini 2.5 Pro as translator, passing the glossary in-prompt as a "terms you must preserve" block. Prompt must specify: (a) British English source, (b) formal "Sie" for DE, (c) pt-BR (not pt-PT), (d) no added marketing language, (e) preserve H1/H2 structure and meta description length budget.
4. **Reflection pass**: feed draft back to Claude Opus 4.6 with the prompt "identify fidelity errors, tone drift, and any glossary violations; return a diff, not a rewrite".
5. **Apply diff**, then **human review** (you) against the glossary. Target 10–15 min per article per locale.
6. **Commit all three locales in a single commit** (EN change + DE + PT-BR) — this matches your CLAUDE.md rule that language variants must never ship out of sync.
7. **SEO check**: run the existing project sitemap + hreflang check before push.

For the UAE variant (English), no translation step — just a tone/market review pass.

This is essentially Ng's reflection agent with two improvements: (a) different models for translate vs. reflect, which measurably catches more errors than self-reflection, and (b) an external glossary as hard constraint. You can implement it either as a small Python script calling both APIs, or as a Claude Code skill modelled on `deusyu/translate-book`.

## Why not the top two runners-up

**Why not DeepL-only (the fallback).** DeepL's Jan 2025 next-gen LLM is a strong pure-MT engine for EN↔DE (1.4× improvement versus DeepL's own prior model in their blind linguist tests, per [deepl.com](https://www.deepl.com/en/blog/next-gen-language-model)) and is a low-cost path that gets you to serviceable German at API-pay-as-you-go rates. But it is a black box: you cannot inject your EU AI Act glossary as a hard constraint, you cannot steer tone toward "understated British English", and WMT25 placed it mid-tier on human eval against frontier LLMs **[Secondary-confirmed via Slator]**. For a landing page where one mistranslated regulatory term costs trust, the steerability gap matters more than the BLEU gap. Keep it as the fallback for when the LLM workflow is unavailable.

**Why not a single Claude Opus 4.6 call.** Claude was in WMT25's second tier on automatic metrics and in the top cluster on human eval — strong but not clearly ahead of Gemini 2.5 Pro for raw translation. More importantly, self-reflection with the same model catches fewer errors than cross-model reflection. Using Claude only as the reviewer plays to its documented strength ("high-nuance brand-sensitive marketing", per Lokalise March 2026) without paying Opus rates for the bulk draft.

## Search log

Ran: `WMT 2025 shared task results English German`, `DeepL vs Claude vs GPT-5 translation benchmark 2026`, `"translation agent" reflection Andrew Ng 2026`, `best LLM English Brazilian Portuguese translation 2026`, `site:reddit.com/r/LocalLLaMA translation LLM 2026`, `EuroLLM Aya Expanse TowerInstruct 2026`, `Claude translation skill github SKILL.md`, `WMT25 general translation findings`, `Slator WMT25 preliminary`, `DeepL next generation LLM 2025 2026 German`.

## What I missed (explicit gaps)

1. **No PT-BR-specific numbers.** WMT25 findings and DeepL's blind tests do not publish an isolated EN→PT-BR score. My PT-BR recommendation inherits from the overall top-cluster ranking, not from PT-BR-specific data. Confidence: medium.
2. **No HN / Reddit / LinkedIn signal.** The r/LocalLLaMA site-restricted search returned zero results in the 30-day window. I did not find a substantive community discussion to triangulate against the vendor and academic sources. Confidence: low on community sentiment.
3. **No 2026 open-source benchmark.** EuroLLM and TowerInstruct did not surface any 2026 release in the search window. If a new open-weights translation model dropped in March-April 2026, I missed it. Re-run this research in 30 days.
4. **Lokalise March 2026 study is a vendor source.** I could not reach the underlying methodology or raw scores, only the blog summary. Treat the "Claude strongest for brand-sensitive marketing" claim as **[Secondary]**, not verified against a primary eval.
5. **No independent audit of Ng's reflection agent at 2026 model scale.** The Ng repo has not been updated to benchmark Gemini 2.5 Pro / Claude Opus 4.6 / GPT-5. The workflow pattern is sound; the quantitative claim "reflection beats single-shot" is from 2024 and is **[Unverified]** at 2026 model scale.
6. **Lokalise / Smartling / Unbabel / Crowdin AI Agent.** I could not find any independent 2026 blind comparison of these SaaS workflows. Their marketing claims are excluded from the recommendation entirely.
7. **Regulatory term sourcing for pt-BR.** Brazil's PL 2338/2023 vocabulary is not a 1:1 match with the EU AI Act. The glossary step in the workflow will require judgement calls I have not researched.

## Sources

- [WMT25 Preliminary Results (Slator, Aug 2025)](https://slator.com/wmt25-preliminary-results-gemini-2-5-pro-gpt-4-1-lead-ai-translation/)
- [Preliminary Ranking of WMT25 General MT Systems, Kocmi et al. (arXiv 2508.14909)](https://arxiv.org/pdf/2508.14909)
- [Findings of the WMT25 General Machine Translation Task (ACL Anthology 2025.wmt-1.22)](https://aclanthology.org/2025.wmt-1.22.pdf)
- [DeepL: Next-gen LLM outperforms ChatGPT-4, Google, Microsoft (DeepL blog)](https://www.deepl.com/en/blog/next-gen-language-model)
- [DeepL bolsters API with next-gen LLM (PRNewswire, Jan 2025)](https://www.prnewswire.com/news-releases/deepl-bolsters-api-with-next-gen-llm-model-and-write-functionality-302360279.html)
- [Andrew Ng translation-agent GitHub repo](https://github.com/andrewyng/translation-agent)
- [Slator: Agentic Machine Translation Has Huge Potential (Ng)](https://slator.com/ai-pioneer-says-agentic-machine-translation-has-huge-potential/)
- [Lokalise: What's the best LLM for translation in 2026 (Mar 2026 update)](https://lokalise.com/blog/what-is-the-best-llm-for-translation/)
- [Aya Expanse (Hugging Face blog)](https://huggingface.co/blog/aya-expanse)
- [deusyu/translate-book Claude Code skill](https://github.com/deusyu/translate-book)
- [Anthropic Agent Skills repo](https://github.com/anthropics/skills)
