# South Africa's national AI policy: what's verified, what isn't, and what it means for code

**Last updated: 7 April 2026**

South Africa is moving from AI strategy to AI governance. On 2 April 2026, Cabinet reportedly approved the draft National Artificial Intelligence Policy for public comment. As of the date of writing, the draft has **not yet been published in the Government Gazette**, and the policy text itself is not in the public domain. What *is* in the public domain is the October 2024 *National AI Policy Framework* — the precursor document that Cabinet's draft is built on. This page covers both, in that order, and is explicit about which claims rest on a primary source and which rest on secondary reporting.

## Two documents, not one

| Document | Status as of 7 April 2026 | Source |
|---|---|---|
| **National AI Policy Framework** ("Towards the Development of South Africa National Artificial Intelligence Policy") | **Published October 2024** by the Department of Communications and Digital Technologies (DCDT). Public comment closed 29 November 2024. **Primary source available.** | [DCDT October 2024 Framework PDF](https://www.dcdt.gov.za) — read end-to-end before writing this page. |
| **Draft National AI Policy** | Reportedly approved by Cabinet on 2 April 2026 for public comment. **Not yet gazetted** as of 7 April 2026. The text is not publicly available. | Secondary reporting only — see [Michalsons, "South Africa's draft national AI policy open for public comment", Nathan-Ross Adams, 3 April 2026](https://www.michalsons.com). |

Conflating the two would be a research-integrity failure. The Michalsons article describes the April 2026 draft as having "six core pillars". The October 2024 framework, which is the only document a reader can actually verify, sets out **twelve** strategic pillars. The two pillar lists overlap conceptually but they are not the same list, and we will not pretend otherwise here.

## What the October 2024 Framework actually says

This section is sourced directly from the DCDT's published PDF. Every claim below can be checked against the document.

The Framework was issued by the **Department of Communications and Digital Technologies, Republic of South Africa**, in October 2024, and opened a public comment window that closed at 17h00 on Friday 29 November 2024. Comments were directed to `dsondlo@dcdt.gov.za` and `mmashologu@dcdt.gov.za`. The Department's address is the iParioli Office Park, 1166 Jan Shoba Street, Hatfield, Pretoria.

The Framework explicitly positions itself as a *step towards* a National AI Policy, not as the policy itself. It frames the policy challenge using a "Futures Triangle" methodology (Inayatullah, 2023) — analysing the **push of the present** (technological advancement, economic necessity, social demands, policy momentum), the **pull of the future** (economic transformation, social equity, sustainable development, global leadership), and the **weight of the past** (digital divide, historical inequities, institutional inertia, regulatory frameworks not equipped to handle the pace of technological change).

It states, in section 4, that "The National AI Policy will serve as the foundational basis for creating AI regulations and potentially an AI Act in South Africa." This is the load-bearing sentence for businesses watching the regulatory direction: the Framework is signalling that an AI Act is on the table, but is not itself an Act.

### The twelve strategic pillars (verified from the Framework, sections 6.1–6.12)

1. **Talent Development / Capacity Development** — integrate AI into curricula from basic to tertiary education; specialised training; academia–industry partnerships.
2. **Digital Infrastructure** — supercomputing capacity; investment in 4G, 5G and high-capacity fibre.
3. **Research, Development, and Innovation** — dedicated AI research centres; public–private partnerships; funding and incentives for AI research and startups.
4. **Public Sector Implementation** — AI in administration to optimise state management and service delivery; ethical guidelines for government deployment.
5. **Ethical AI Guidelines Development** — alignment with human rights principles; regulatory compliance and governance.
6. **Privacy and Data Protection** — standardised data governance; strengthening of existing data protection regulations; transparency in AI data usage and storage.
7. **Safety and Security** — cybersecurity protocols for AI systems; risk management frameworks.
8. **Transparency and Explainability** — explainable AI; trust and acceptance; accountability; bias detection; public awareness campaigns.
9. **Fairness and Mitigating Bias** — methods to identify and mitigate bias; inclusive data sets representing all demographics.
10. **Human Control of Technology (Human-Centred Approach)** — human-in-the-loop systems, especially for generative AI; decision-making frameworks that prioritise human judgment.
11. **Professional Responsibility** — code of conduct for AI professionals; ethics training in AI education.
12. **Promotion of Cultural and Human Values** — value-based AI promoting well-being, equality, and environmental sustainability; stakeholder engagement.

If the April 2026 draft policy genuinely consolidates these twelve into six pillars, that is itself a substantive editorial decision — and one we cannot describe accurately until the gazette publishes the actual text.

## What the April 2026 draft policy reportedly does (unverified)

Per the Michalsons article — which we are citing as **secondary reporting**, not as a primary source — Cabinet approved publication of the draft policy on 2 April 2026, following a 24 February 2026 DCDT briefing to Parliament that confirmed clearance through the Socio-Economic Impact Assessment System and Director-General cluster concurrence. The article describes a 60-day public comment window once the gazette is published, with sector-specific regulations and guidelines targeted for the 2027/2028 financial year. The Cabinet decision was originally targeted for March 2026.

The Michalsons piece also reports that government has chosen a **sector-specific, multi-regulator model** rather than establishing a single dedicated AI regulator. AI governance would be embedded within existing supervisory frameworks across financial services, health, education, telecommunications and other sectors. We cannot verify this against primary text until the draft policy is gazetted.

**We will update this page within seven days of the gazette publication** with a side-by-side comparison of (a) the twelve-pillar Framework, (b) the actual gazetted draft policy, and (c) any divergence from the Michalsons summary.

## What this means for organisations building or deploying AI in South Africa

### The legal baseline today

South Africa already has a substantial body of law that touches AI systems even in the absence of an AI Act:

- **POPIA (Protection of Personal Information Act, 2013)** — applies to any AI system that processes personal information; Section 71 specifically addresses automated decision-making.
- **Copyright Act, 1978** (and the unsigned Copyright Amendment Bill) — relevant to training-data provenance and to AI-generated outputs.
- **Competition Act, 1998** — relevant to algorithmic pricing, market concentration in AI infrastructure, and data-driven anti-competitive conduct.
- **Patents Act, 1978** — relevant to AI-generated inventions; the *Thaler* line of decisions has been tested in South African courts.
- **King IV / King V Codes on Corporate Governance** — non-statutory but widely adopted. **King V was adopted by the Institute of Directors in South Africa (IoDSA) on 31 October 2025 and is in force for financial years commencing on or after January 2026.** It consolidates King IV's 17 principles into 13 and introduces explicit AI governance principles alongside enhanced cyber risk provisions — governing bodies are now expected to oversee AI use and AI-related risk as a board-level matter under King V's "apply and explain" regime (see IoDSA publications and the Clyde & Co analysis, November 2025).

None of these are specific to AI. The Framework's stated intent is to give regulators a unified policy direction so that sector-specific rules can be written on a consistent base.

### The practical compliance question for code

Most organisations deploying AI in South Africa today are not building general-purpose models from scratch. They are integrating large language model APIs (OpenAI, Anthropic, Google, AWS Bedrock), building employment-screening or credit-scoring features on top of existing ML libraries, or fine-tuning open-source models on local data. The Framework names exactly these use cases — healthcare, education, finance, employment — as the sectors where ethical AI guidelines, bias mitigation, and human-in-the-loop oversight will be expected.

The reasonable starting position for a South African organisation, while the draft policy is in consultation, is:

1. **Inventory your AI systems.** A list of what you have deployed, in which products, by which teams, with which third-party providers, and against which categories of personal data. POPIA already requires you to know this; the Framework will reinforce the requirement.
2. **Document your data flows.** Where training data came from, what consent or contractual basis covers it, where inference data lives, and who has access.
3. **Document human oversight.** For each high-stakes deployment (hiring, credit, healthcare triage, content moderation), name the human function that reviews or can override the system. The Framework's pillar 10 explicitly calls out human-in-the-loop as a requirement.
4. **Map your existing obligations.** POPIA Section 71, Competition Act, sector regulator guidance from the Information Regulator, the FSCA, the Council for Medical Schemes, and the Department of Higher Education and Training as applicable.
5. **Submit comments on the draft policy when it gazettes.** Industry voices will dominate the consultation if civil society and individual technologists do not participate. The Framework's October 2024 consultation received comparatively few public submissions.

### Where Regula fits

Regula is an open-source static analysis tool that scans code for AI Act-shaped risk indicators. It was built primarily against the EU AI Act (Regulation (EU) 2024/1689), but the South African Framework explicitly benchmarks against EU AI Act concepts — risk tiers, high-risk categories (employment, biometrics, education, law enforcement, migration, critical infrastructure), human oversight obligations, transparency requirements — so the patterns Regula already detects map directly onto the categories the Framework names.

For a South African team, the practically useful starting commands are:

```bash
pip install regula-ai

# Inventory what you have
regula discover .                    # AI systems present in the project
regula inventory                     # AI library / model references with GPAI tier annotations

# Risk indicators against the same categories the Framework names
regula check .                       # Scan for risk indicators
regula classify --input "..."        # Classify a code snippet
regula explain --file path/to/file   # Explain why something was classified

# Generate compliance evidence
regula gap                           # Articles 9–15-style gap assessment
regula oversight                     # Cross-file Article 14-style human oversight detection
regula conform                       # Annex IV-style conformity evidence pack
regula register .                    # Annex VIII-shaped registration packet (added 7 April 2026)

# Health and reproducibility
regula self-test
regula doctor
```

The `register` command produces an Annex VIII-shaped local artifact even though South Africa does not have an EU-style central AI database. The fields it captures — provider identity, intended purpose, data inputs, system status, conformity references, fundamental rights impact assessment, data protection impact assessment — overlap closely with what the Framework's twelve pillars are likely to demand once sector-specific guidelines are written. Treat the artifact as a structured record-keeping baseline, not as a legal filing.

Regula is open source, written in Python with **zero production dependencies**, and the entire detection ruleset is in the repository. South African teams can fork it, add SA-specific patterns (POPIA Section 71 markers, FSCA conduct standards, CMS clinical AI requirements) and contribute them back. Issues, pull requests, and substantive feedback are welcome at [github.com/kuzivaai/getregula](https://github.com/kuzivaai/getregula).

## Honest gaps in this page

Per the global research-integrity rules under which this page is written:

1. **The April 2026 draft policy text has not been verified against a primary source.** Every claim sourced from the Michalsons article is labelled as such. We will revise the page within seven days of gazette publication.
2. **The "six pillars" claim is unverified.** The October 2024 Framework has twelve. The April 2026 draft may consolidate, expand, rename, or restructure them; we do not yet know.
3. **The "sector-specific multi-regulator model" claim is unverified.** The Framework's section 4 only says the policy "will serve as the foundational basis for creating AI regulations and potentially an AI Act" — neither confirming nor ruling out a single regulator.
4. **No commentary on whether the Framework or the draft policy aligns with the AU Continental AI Strategy or the SADC digital strategies has been included** because that comparison cannot be made until the draft policy text is available.
5. **Regula was built primarily against EU AI Act categories.** Mapping its detection patterns onto the South African Framework's pillars is a directional claim — directly supported by the Framework's own benchmarking language but not equivalent to a SA-specific compliance toolkit. A SA-specific pattern set is on Regula's roadmap and contributions are welcome.

## Sources

- **National AI Policy Framework** (October 2024) — Department of Communications and Digital Technologies, Republic of South Africa. Read end-to-end as the primary source for sections 6.1–6.12 above. Comment contacts: dsondlo@dcdt.gov.za, mmashologu@dcdt.gov.za. Department: iParioli Office Park, 1166 Jan Shoba Street, Hatfield, Pretoria. Tel: +27 12 427 8000. Website: [www.dcdt.gov.za](https://www.dcdt.gov.za).
- **Inayatullah, S. (2023)** — "The Futures Triangle: Origins and Iterations." *World Futures Review*, 15(2-4), 112–121. The methodology underlying the Framework's section 5.
- **Presidential Commission on the Fourth Industrial Revolution** (2020) — The Diagnostic Report. Cited by the Framework as the historical starting point for South Africa's AI policy work.
- **Michalsons — Nathan-Ross Adams (3 April 2026)** — "South Africa's draft national AI policy open for public comment." Secondary source for the Cabinet approval, the 60-day comment window, and the sector-specific multi-regulator claim. Cited as secondary; not relied on for any claim that could not be checked elsewhere.
- **Regulation (EU) 2024/1689** — the EU AI Act, against which the South African Framework explicitly benchmarks.

If you spot an error on this page, open an issue on [github.com/kuzivaai/getregula](https://github.com/kuzivaai/getregula) or email a correction. We would rather be told than be wrong.
