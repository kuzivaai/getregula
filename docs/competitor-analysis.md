# Regula — Competitor Analysis

Research date: 2026-04-09. Author: objective analysis, primary sources only. British English.

## Executive summary

Regula operates in a crowded but fragmented market. The EU AI Act governance space is dominated by enterprise SaaS platforms ([Credo AI](https://www.credo.ai/), [Saidot](https://www.saidot.ai/), [Enzai](https://www.enz.ai/), [IBM watsonx.governance](https://www.ibm.com/products/watsonx-governance), Microsoft Purview AI Hub, ServiceNow AI Control Tower) that target compliance, legal and risk teams with policy packs, evidence workflows, model registries and audit dashboards — not developer workstations. On the developer-tooling side, Regula has at least four directly overlapping open-source CLIs that did not exist 12 months ago: [Systima Comply](https://dev.to/systima/open-source-eu-ai-act-compliance-scanning-for-cicd-4ogj) (`@systima/comply`, TypeScript/npm), [ark-forge `mcp-eu-ai-act`](https://github.com/ark-forge/mcp-eu-ai-act) (Python, MCP server + REST, freemium), [AIR Blackbox](https://airblackbox.ai/) (`pip install air-blackbox`, Python, Apache 2.0, local, 39 checks across Articles 9/10/11/12/14/15 — the closest positional overlap to Regula in the market), and narrower academic tools such as [Hiepler/EuConform](https://github.com/Hiepler/EuConform). Regula's genuine differentiation is narrower than a category-leadership claim — it is better stated as "Python stdlib-only, zero production dependencies, fully-offline, MIT, no commercial upsell path wired into the tool". The enterprise SaaS platforms beat Regula on continuous monitoring, evidence workflows, legal expert networks and enterprise reporting; no local CLI should claim otherwise.

## Market segmentation

1. **Developer CLI / shift-left code scanners.** Run on a laptop or in CI, scan source code for AI framework usage and risk patterns. Small category, mostly new. Regula sits here.
2. **Enterprise AI GRC SaaS.** Policy packs, control libraries, evidence collection, model registries, human-in-the-loop workflows, audit dashboards. Sold to CISO / compliance / legal buyers. Contact-sales pricing.
3. **MLOps governance add-ons.** Governance features bolted onto ML platforms (watsonx.governance, Databricks Unity Catalog, Weights & Biases). Aimed at existing platform customers.
4. **LLM security / red-team scanners.** Giskard, NVIDIA Garak, Promptfoo, DeepEval. Focused on model behaviour (prompt injection, jailbreaks, toxicity), not on static code analysis against regulatory articles.
5. **Policy / consulting / checklists.** artificialintelligenceact.eu self-assessment, Linux Foundation Europe guidance, law firms. Not tools.

## Direct competitors — developer-side code scanners

| Tool | Category | Pricing | Licence | Scans code? | Local-only? | AI Act-specific? | Source (accessed 2026-04-09) |
|---|---|---|---|---|---|---|---|
| **Regula** (getregula / regula-ai) | Python CLI, stdlib-only | Free | MIT | Yes, 8 languages, 330 patterns | Yes, zero prod deps | Yes + 12 frameworks | Own repo |
| **Systima Comply** (`@systima/comply`) | Node/TS CLI + GitHub Action | Free OSS, commercial services on top | Not stated on DEV article — needs verification | Yes, AST-based import detection, 37+ AI frameworks | Yes, "no API keys required" | Yes | [DEV article](https://dev.to/systima/open-source-eu-ai-act-compliance-scanning-for-cicd-4ogj) |
| **ark-forge mcp-eu-ai-act** | Python MCP server / CLI / REST | Freemium: 5 scans/day free, Pro/Certified paid tiers via arkforge.tech | Repository has LICENSE file, exact licence unverified in fetch | Yes, 16 frameworks across Py/JS/TS/Go/Java/Rust | Hybrid — local MCP *or* SaaS REST | Yes, Articles 9–15, Annex III/IV mapping | [GitHub](https://github.com/ark-forge/mcp-eu-ai-act) |
| **desiorac/mcp-eu-ai-act** | Python MCP server | Free, licence not verified in this pass | Unverified | Yes, scans `.py`, `.js`, `.ts`, `.java`, `.go`, `.rs`, `.cpp`, `.c` plus dependency files | Local MCP | Yes | [GitHub](https://github.com/desiorac/mcp-eu-ai-act) — second, distinct MCP-server EU AI Act scanner, independent of ark-forge's. Flagged by second-pass audit. `reported-unverified`. |
| **AIR Blackbox** (`pip install air-blackbox`) | Python pip package, CLI + pre-commit hook | Free | Apache 2.0 | Yes — 39 checks across Articles 9/10/11/12/14/15; GDPR + bias + fairness modules; ISO 42001 + NIST AI RMF crosswalk | Yes, 100% local | Yes | [airblackbox.ai](https://airblackbox.ai/), [github.com/airblackbox](https://github.com/airblackbox) **[Verified-primary via vendor site + maintainer DEV posts]** |
| **Hiepler/EuConform** | Browser / local Ollama tool | Free | Dual MIT + EUPL-1.2 | Partial — guidance + risk classification, not deep code scan | Yes (browser or local Ollama) | Yes | [GitHub](https://github.com/Hiepler/EuConform) |
| **Dylan-Gallagher/ai-compliance-verifier** | Academic tool | Free | Unverified | Limited — compliance score for a given model | Yes | Yes | [GitHub](https://github.com/Dylan-Gallagher/ai-compliance-verifier) |
| **aai-institute/practical-ai-act** | Reference implementation | Free | Unverified | No — example high-risk system, not a scanner | N/A | Yes | [GitHub](https://github.com/aai-institute/practical-ai-act) |
| **niranjanxprt/eu-ai-act** | Interactive compliance checker | Free | Unverified | No — questionnaire UI | Yes | Yes | [GitHub](https://github.com/niranjanxprt/eu-ai-act) |

Honest read: Systima Comply, ark-forge mcp-eu-ai-act, and AIR Blackbox are the three tools in this table with code-scanning capability at a similar level of ambition to Regula. AIR Blackbox is the closest positional overlap — Python, pip, Apache 2.0, local, AI Act specific, 39 checks — and is arguably a more direct match to Regula's positioning than any other tool here. None of them are strict subsets of Regula and none fully overlap with it. **[Verdict: VERIFIED-PRIMARY]** per [airblackbox.ai](https://airblackbox.ai/).

## Direct competitors — Enterprise AI governance SaaS

| Vendor | Focus | Pricing | Code scan? | Local? | EU AI Act specific? | Source |
|---|---|---|---|---|---|---|
| **Credo AI** | Policy packs (EU AI Act, NIST AI RMF, ISO 42001, SOC 2, HITRUST), agentic workflows, evidence generation | Contact sales | No | No (SaaS) | Yes (policy pack) | [credo.ai/product](https://www.credo.ai/product) |
| **Saidot** | EU AI Act templates, controls, vendor inventory; Helsinki-based, founded 2018 | Contact sales | No | No (SaaS) | Yes | [saidot.ai/product](https://www.saidot.ai/product) |
| **Enzai** | Conformity assessments, AI register, model/dataset documentation | Contact sales | No | No (SaaS) | Yes (explicit AI Act framework) | [enz.ai/solutions/eu-ai-act](https://www.enz.ai/solutions/eu-ai-act) |
| **IBM watsonx.governance** | Auto-discovery, risk classification, agentic AI governance | Enterprise | No (model-level, not source code) | No | Yes | [ibm.com/products/watsonx-governance](https://www.ibm.com/products/watsonx-governance) |
| **Microsoft Purview AI Hub** | AI inventory, DLP, sensitivity labels, audit logs, 100+ frameworks | Microsoft 365 / Purview licensing | No (data/model governance, not code) | No | Partial | [Microsoft Community Hub](https://techcommunity.microsoft.com/blog/healthcareandlifesciencesblog/compliance-meets-ai-2026-microsoft-purview-in-the-age-of-ai/4475027) |
| **ServiceNow AI Control Tower** | Central register integrated with ITOM/IRM/TPRM | Enterprise | No | No | Yes (operational compliance) | Search result summary; vendor page not fetched — partially verified |
| **Fairly AI, Holistic AI, Trustible, Modulos, Luminos, Anch.AI, ObviosAI** | AI GRC platforms | Contact sales | No | No | Varies | **Unverified** — vendor pages not individually fetched in this pass. Do not cite as verified. |

Every platform in this table is a pure SaaS, contact-sales, compliance-team-facing product. None of them scan Python/TS/Go source code on a developer laptop with zero dependencies. That gap is real, but so is the corresponding gap in the opposite direction (see "Where Regula is weaker").

## Adjacent / overlapping tools

- **LLM behaviour scanners:** NVIDIA Garak, Giskard, Promptfoo, DeepEval — test running models for jailbreaks, prompt injection, toxicity, bias. Different problem from Regula: they need a live model endpoint, not a code tree. Some (Giskard, DeepEval) claim NIST AI RMF / OWASP LLM Top 10 mappings. Sources: [Garak (NVIDIA)](https://github.com/NVIDIA/garak), [Giskard OSS](https://github.com/Giskard-AI/giskard-oss).
- **Traditional SAST/SCA:** Semgrep, Snyk Code, CodeQL, SonarQube, GitGuardian. None ship AI-Act-specific rulesets out of the box, although Semgrep's custom-rule model is the closest thing to a DIY alternative to Regula for teams that already run Semgrep in CI.
- **Dataset/model lineage:** Databricks Unity Catalog, Weights & Biases Registry, MLflow. Governance features are add-ons; not comparable to Regula.
- **Reference/guidance:** Linux Foundation Europe AI Act explainer, `artificialintelligenceact.eu` compliance checker (a questionnaire), EU AI Act Service Desk. Not competitors in a tooling sense, but they are what a developer actually reads first.

## Where Regula is genuinely differentiated (with evidence)

1. **Zero production dependencies, Python stdlib-only.** Verified in `/home/mkuziva/getregula/CLAUDE.md` and `pyproject.toml`. Systima Comply is npm-based (web-tree-sitter, TS Compiler API). mcp-eu-ai-act is Python but bundles MCP server infra. For air-gapped or security-conscious environments this is a concrete advantage.
2. **Fully offline by default, no freemium API.** Regula has no remote endpoint. ark-forge mcp-eu-ai-act explicitly offers a hosted SaaS tier with rate limits; Systima Comply is local but ships a commercial services funnel. Unverified for other scanners.
3. **Language breadth.** Regula claims 8 languages and 330 risk patterns (per project CLAUDE.md). Systima Comply claims "37+ AI frameworks" but does not publish a language count in the DEV article. mcp-eu-ai-act claims 16 frameworks across 6 languages. Regula's pattern count is larger on its own numbers, though a head-to-head benchmark has not been run.
4. **12 compliance framework coverage** (per project spec) — broader than any single open-source competitor verified here. Enterprise SaaS beats this, but not on a laptop.
5. **MIT licence, no commercial upsell path wired into the tool.** Credible for open-source adopters who've been burned by "open core" bait-and-switch.

## Where Regula is weaker / honest gaps

A local Python CLI cannot do the following, and no amount of pattern coverage changes that. Paid SaaS platforms do these things and buyers pay for them:

- **Continuous monitoring and drift detection.** Regula runs when you run it. Credo AI, Enzai, watsonx.governance monitor deployed models in production.
- **Evidence collection workflows.** Auditors want timestamped evidence tied to controls, not a JSON report. Credo AI, Saidot, Enzai generate audit-ready evidence packages tied to a control library. Regula's `json_output` envelope is a building block, not a workflow.
- **Model registry / AI system inventory.** Governance SaaS maintains the list of "all AI systems we operate". Regula scans one repo at a time.
- **Legal expert network and policy updates.** Saidot and Credo AI employ lawyers who update policy packs when the Commission publishes new guidance, delegated acts, or Omnibus amendments. A CLI maintainer is not a substitute.
- **Conformity assessment workflow.** Annex IV technical documentation, post-market monitoring, serious-incident reporting — Enzai is explicitly built for this. Regula can scan for risk patterns but does not run a conformity assessment.
- **Dataset lineage and data governance.** Microsoft Purview, Databricks Unity Catalog operate at the data layer. Regula does not look at data.
- **Enterprise reporting, SSO, RBAC, SOC 2 / ISO 27001 certification.** Regula is a CLI; none of this applies.
- **Runtime model behaviour testing.** Garak, Giskard, Promptfoo cover prompt injection, jailbreaks, bias. Regula does not attempt this — it is static analysis, not red-teaming.
- **Competitor parity on code scanning specifically.** Systima Comply's AST-based import detection with flow tracing is architecturally more sophisticated than regex/pattern matching for the subset of things it does cover. Regula should avoid category-leadership framing in this space — there are now at least three other credible open-source AI Act scanners. **[Verdict: SOUND]** per the table above.

## New entrants 2025–2026

- **Systima Comply** — published open-source CLI and GitHub Action, late 2025 / early 2026 (DEV article).
- **ark-forge mcp-eu-ai-act** — positioned as an MCP server, which is itself a 2025 design pattern; arkforge.tech SaaS tier is new.
- **Credo AI agentic governance agents** — 2025/2026 release automating evidence retrieval and incident remediation (Credo AI 2025 year-in-review).
- **IBM watsonx.governance agentic AI features** — 2025/2026 addition.
- **Microsoft Agent Governance Toolkit** ([`microsoft/agent-governance-toolkit`](https://github.com/microsoft/agent-governance-toolkit)) — released 3 April 2026 per [opensource.microsoft.com](https://opensource.microsoft.com/blog/). MIT licence. Seven-package multi-language system (Python, TypeScript, Rust, Go, .NET). Maps to [OWASP Agentic AI Top 10](https://genai.owasp.org/). Integrations with LangChain, CrewAI, Google ADK, OpenAI Agents SDK. **Classification: adjacent, not direct** — this is runtime agent governance (like Garak/Giskard), not static AI Act code analysis, and it competes in a different lane from Regula. **[Verdict: VERIFIED-PRIMARY via Microsoft blog + InfoWorld + Help Net Security + CSO Online coverage].**
- **ServiceNow AI Control Tower** — verified as existing, exact GA date not confirmed here.

## Counterevidence pass

Actively looking for evidence that Regula's niche is already filled:

- Systima Comply arguably fills the "local CI scanner for EU AI Act" niche already, at least for TypeScript/JavaScript teams. If the user's ICP is JS/TS-heavy, Systima is a serious competitor, not an adjacent tool.
- mcp-eu-ai-act covers Python, JS, TS, Go, Java and Rust — the same 6 of Regula's claimed 8 languages. The marginal value of Regula over mcp-eu-ai-act, for a team that is fine with a freemium API, is narrower than "we support more languages".
- The statement "no SME tool exists for AI Act compliance" would be false. Multiple free, open-source scanners exist. Regula's pitch should be specific: stdlib-only, offline, MIT, no SaaS upsell.
- The statement "only Regula scans code for AI Act risks" would be false. **[Verdict: SOUND]** — Systima Comply, mcp-eu-ai-act and AIR Blackbox demonstrate that the space has multiple credible open-source scanners.

## Search log

Queries executed:
- `EU AI Act code scanner CLI open source static analysis`
- `"EU AI Act" compliance developer tool github`
- `Credo AI Holistic AI Fairly AI Trustible AI governance platform pricing 2026`
- `Saidot Luminos Enzai ObviosAI Anch.AI Modulos AI Act compliance`
- `Systima comply CLI EU AI Act open source license pricing`
- `"watsonx.governance" "Microsoft Purview AI Hub" "ServiceNow AI Control Tower" EU AI Act 2026`
- `Giskard Garak Promptfoo DeepEval LLM security scanner open source`
- WebFetch on `github.com/ark-forge/mcp-eu-ai-act`

### Known gaps in this research pass

- **Vendor pages not individually fetched** for Fairly AI, Holistic AI, Trustible, Modulos, Luminos, Anch.AI, ObviosAI, Fiddler, Monitaur. Inclusion in the SaaS table is based on user-supplied names only; feature/pricing claims are not made for them.
- ~~Microsoft Agent Governance Toolkit — not verified.~~ **Resolved in second pass:** verified via Microsoft open-source blog + multiple press outlets. Now in "New entrants 2025-2026" above.
- ~~AIR Blackbox — sourced from search snippet only.~~ **Resolved in second pass:** verified via [airblackbox.ai](https://airblackbox.ai/) and maintainer DEV posts. Promoted into the main competitor table.
- **Systima Comply licence** — the DEV article states the Article 12 audit logging library is MIT, but does not explicitly state the licence of `@systima/comply` itself. Needs confirmation from the npm package metadata or the systima-ai/comply GitHub repo.
- **Head-to-head benchmark** between Regula, Systima Comply and mcp-eu-ai-act on the same codebase — not performed. Pattern-count claims are vendor-stated, not measured.
- **Databricks Unity Catalog governance**, **Weights & Biases governance**, **Google Cloud Model Armor** — not searched in this pass.
- **Semgrep community AI Act rulesets** — not searched. Worth checking whether any public Semgrep ruleset targets AI Act articles, since that would be the most realistic DIY substitute for Regula.
- **Producthunt / open-source GitHub "new in 2026"** sweep — partially covered by the github search but not exhaustive.

## Sources

- https://airblackbox.ai/ (AIR Blackbox — promoted to main table in second pass)
- https://github.com/airblackbox (AIR Blackbox org)
- https://github.com/microsoft/agent-governance-toolkit (Microsoft Agent Governance Toolkit, 3 April 2026)
- https://opensource.microsoft.com/blog/ (Microsoft Agent Governance Toolkit announcement)
- https://dev.to/systima/open-source-eu-ai-act-compliance-scanning-for-cicd-4ogj
- https://systima.ai/blog/eu-ai-act-engineering-compliance-guide
- https://systima.ai/blog/open-source-article-12-audit-logging
- https://github.com/ark-forge/mcp-eu-ai-act
- https://github.com/Hiepler/EuConform
- https://github.com/niranjanxprt/eu-ai-act
- https://github.com/Dylan-Gallagher/ai-compliance-verifier
- https://github.com/aai-institute/practical-ai-act
- https://github.com/Francesco-Sovrano/AI-Act-Compliance-Technical-Documentation-Assessment-Tools
- https://github.com/ARQNXS/eu-ai-act-compliance-checker
- https://www.credo.ai/
- https://www.credo.ai/product
- https://www.credo.ai/blog/credo-ai-2025-year-in-review
- https://www.saidot.ai/
- https://www.saidot.ai/product
- https://www.enz.ai/
- https://www.enz.ai/solutions/eu-ai-act
- https://oecd.ai/en/catalogue/tools/enzai-eu-ai-act-compliance-framework
- https://oecd.ai/en/catalogue/tools/saidot
- https://www.ibm.com/products/watsonx-governance
- https://www.ibm.com/think/insights/eu-ai-act
- https://techcommunity.microsoft.com/blog/healthcareandlifesciencesblog/compliance-meets-ai-2026-microsoft-purview-in-the-age-of-ai/4475027
- https://github.com/NVIDIA/garak
- https://garak.ai/
- https://github.com/Giskard-AI/giskard-oss
- https://docs.giskard.ai/en/stable/open_source/scan/scan_llm/index.html
- https://artificialintelligenceact.eu/assessment/eu-ai-act-compliance-checker/
- https://linuxfoundation.eu/newsroom/ai-act-explainer
- https://ai-act-service-desk.ec.europa.eu/en
- https://huggingface.co/blog/yjernite/eu-act-os-guideai
