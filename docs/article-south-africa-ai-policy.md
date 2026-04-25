# South Africa's draft National AI Policy: what Cabinet approved, and what it means for code

**Last updated: 7 April 2026**

On 2 April 2026, Cabinet approved South Africa's draft National Artificial Intelligence Policy for public comment. The gazette has not yet published the text, but the direction is now clear: a sector-specific AI governance regime, a 60-day public comment window, and sector-specific regulations in the 2027/2028 financial year. This is the live reference — what we know, what we don't, and what South African organisations can do today while the draft policy works through the gazette.

## What Cabinet approved on 2 April 2026

At a post-Cabinet media briefing in Pretoria, Minister in the Presidency Khumbudzo Ntshavheni announced that Cabinet had approved publication of the draft National Artificial Intelligence Policy for public comment. The draft reportedly cleared the Socio-Economic Impact Assessment System and achieved concurrence across all Director-General clusters in a 24 February 2026 DCDT briefing to Parliament.

The gazette has not yet published the text, so the policy's exact wording is not in the public domain. What the draft is **reported** to contain — pending gazette confirmation — is the following:

- **A sector-specific, multi-regulator governance model.** Rather than creating a single dedicated AI regulator, AI governance will be embedded within existing supervisory frameworks — the FSCA for financial services, the Information Regulator for data protection, the Council for Medical Schemes for health, ICASA for telecommunications, the Department of Higher Education and Training for education, and so on. Pragmatic, but creates a patchwork that is harder to navigate for smaller businesses operating across sectors.
- **Six core pillars** organised around capacity and talent development, AI for inclusive growth and job creation, responsible governance, ethical and inclusive AI, cultural preservation and international integration, and human-centred deployment.
- **A 60-day public comment window** that opens on the gazette publication date (expected April 2026).
- **Final policy** targeted for the 2026/2027 financial year.
- **Sector-specific regulations and guidelines** targeted for the 2027/2028 financial year.

All six-pillar and multi-regulator claims above are sourced from [Michalsons' 3 April 2026 analysis](https://www.michalsons.com) and will be verified against the gazetted text the moment it publishes.

**The question everyone is asking.** How will the DCDT coordinate across that many sector regulators so South African organisations don't end up complying with six different, conflicting AI rulebooks? That is the single most important question to raise during the public comment window.

## The South African legal baseline for AI today

South Africa does not have an AI Act yet, and the draft policy Cabinet approved is not itself an Act either — it is a policy that will later be translated into sector-specific regulations. But South African organisations deploying AI are already bound by a substantial body of existing law. None of these require waiting for the gazette.

- **POPIA (Protection of Personal Information Act, 2013)** — applies to any AI system that processes personal information. **Section 71** specifically addresses automated decision-making and profiling: a data subject is entitled not to be subject to a decision based solely on automated processing unless specific exceptions apply. This obligation already binds South African organisations.
- **Copyright Act, 1978** (and the unsigned Copyright Amendment Bill) — relevant to training-data provenance and to AI-generated outputs.
- **Competition Act, 1998** — relevant to algorithmic pricing, market concentration in AI infrastructure, and data-driven anti-competitive conduct.
- **Patents Act, 1978** — relevant to AI-generated inventions; the *Thaler* line of decisions has been tested in South African courts.
- **King IV / King V Codes on Corporate Governance** — non-statutory but widely adopted. **King V was adopted by the Institute of Directors in South Africa (IoDSA) on 31 October 2025 and is in force for financial years commencing on or after January 2026.** It consolidates King IV's 17 principles into 13 and introduces explicit AI governance principles alongside enhanced cyber risk provisions — governing bodies are now expected to oversee AI use and AI-related risk as a board-level matter under King V's "apply and explain" regime (see IoDSA publications and the Clyde & Co analysis, November 2025).

## What South African organisations should do now

While the draft policy works through the gazette and the 60-day comment window, five things are worth doing today. None of them require waiting for the final text.

1. **Inventory your AI systems.** A list of what you have deployed, in which products, by which teams, with which third-party providers, and against which categories of personal data. POPIA already requires you to know this, and King V now makes it a board-level oversight obligation.
2. **Document your data flows.** Where training data came from, what consent or contractual basis covers it, where inference data lives, and who has access.
3. **Document human oversight.** For each high-stakes deployment (hiring, credit scoring, healthcare triage, content moderation), name the human function that reviews or can override the system. Human oversight is central to every modern AI governance regime and will be a focal point of the draft policy's "human-centred deployment" pillar.
4. **Map your existing obligations.** POPIA Section 71 (automated decision-making), Competition Act, Copyright Act, and sector regulator guidance from the Information Regulator, the FSCA, the Council for Medical Schemes, ICASA and the Department of Higher Education and Training as applicable. Those are the regulators most likely to own AI rule-making in a sector-specific model.
5. **Submit comments during the 60-day public comment window.** Industry voices will dominate the consultation if civil society, individual technologists and smaller businesses do not participate. Early feedback is the best chance to shape how sector-specific rules are eventually written.

## Where Regula fits

Regula is an open-source compliance CLI that combines code scanning with governance questionnaires for AI Act-shaped risk assessment. It was built primarily against the EU AI Act (Regulation (EU) 2024/1689), but the risk categories it detects — employment, biometrics, education, law enforcement, migration, critical infrastructure, credit scoring, medical devices — are exactly the areas every modern AI governance regime treats as high-risk, including the sectors South Africa's draft policy will route to sector-specific regulators. If you need to know whether a deployment touches a high-risk category today, Regula will tell you.

For a South African team, the practically useful starting commands are:

```bash
pip install regula-ai

# Inventory what you have
regula discover .                    # AI systems present in the project
regula inventory                     # AI library / model references with GPAI tier annotations

# Risk indicators against the same categories the draft policy will touch
regula check .                       # Scan for risk indicators
regula classify --input "..."        # Classify a code snippet
regula explain --file path/to/file   # Explain why something was classified

# Generate compliance evidence
regula gap                           # Articles 9–15-style gap assessment
regula oversight                     # Cross-file Article 14-style human oversight detection
regula conform                       # Annex IV-style conformity evidence pack
regula register .                    # Annex VIII-shaped registration packet

# Health and reproducibility
regula self-test
regula doctor
```

The `register` command produces an Annex VIII-shaped local artifact even though South Africa does not have an EU-style central AI database. The fields it captures — provider identity, intended purpose, data inputs, system status, conformity references, fundamental rights impact assessment, data protection impact assessment — are the exact fields any sector-specific South African regulator will eventually ask for. Treat the artifact as a structured record-keeping baseline, not as a legal filing.

Regula is open source, written in Python with **zero production dependencies**, and the entire detection ruleset is in the repository. South African teams can fork it, add SA-specific patterns (POPIA Section 71 markers, FSCA conduct standards, CMS clinical AI requirements) and contribute them back. Issues, pull requests, and substantive feedback are welcome at [github.com/kuzivaai/getregula](https://github.com/kuzivaai/getregula).

## What we are tracking and what we still need to verify

We would rather publish what we know and flag what we don't than wait for certainty and let others dominate the conversation. Here is the gap list as of 7 April 2026:

1. **Exact number and naming of pillars.** Current reporting says six; the gazetted text may show a different count or structure.
2. **The sector-specific multi-regulator model.** Whether the final text confirms this approach or hedges it, and which specific regulators are named.
3. **Coordination mechanism across regulators.** How DCDT proposes to prevent conflicting sector rules — this is the single most important practical question for businesses operating across industries.
4. **High-risk category definitions.** Whether the draft policy carries an explicit Annex III-style list and how it compares to the EU AI Act's categories.
5. **Public sector obligations.** The extent to which state use of AI (welfare, policing, border control) is treated differently from private sector deployment.
6. **Alignment with the AU Continental AI Strategy and SADC digital frameworks.** Not addressable until the text is in the public domain.

The moment the gazette publishes, we update the tracker, update this list, and publish a focused breakdown of what changed between the Cabinet-approved draft and the gazetted text.

## Background

Work on a South African AI framework began in 2020 following the Presidential Commission on the Fourth Industrial Revolution (PC4IR). In October 2024 the Department of Communications and Digital Technologies published a National AI Policy Framework as a precursor document, opening a public comment window that closed on 29 November 2024. That Framework benchmarked against international approaches including the EU AI Act and set out twelve strategic pillars as input to the eventual policy. The draft policy Cabinet approved on 2 April 2026 builds on that Framework but is a separate document, and the gazette text will be what matters.

## Sources

- **Post-Cabinet media briefing (2 April 2026)** — Minister in the Presidency Khumbudzo Ntshavheni, Pretoria. Announcement of Cabinet approval of the draft National AI Policy for public comment. Confirmed via live broadcast coverage on Sowetan and Business Day.
- **Michalsons — Nathan-Ross Adams (3 April 2026)** — "South Africa's draft national AI policy open for public comment." Source for the six-pillar structure, sector-specific multi-regulator model, 60-day comment window, 24 February 2026 parliamentary briefing, SEIAS clearance and DG cluster concurrence, and the 2026/2027 and 2027/2028 targets. To be verified against the gazetted text.
- **Department of Communications and Digital Technologies** — the lead department. Web: [www.dcdt.gov.za](https://www.dcdt.gov.za). Tel: +27 12 427 8000.
- **POPIA (Protection of Personal Information Act 4 of 2013)** — Republic of South Africa. Section 71 governs automated decision-making and profiling.
- **King V Code of Corporate Governance (October 2025)** — Institute of Directors in South Africa. Adopted 31 October 2025, in force for financial years commencing on or after January 2026.
- **October 2024 DCDT National AI Policy Framework** — the precursor document published for public comment (closed 29 November 2024). Useful historical context; superseded in focus by the April 2026 draft policy.

If you spot an error on this page, open an issue on [github.com/kuzivaai/getregula](https://github.com/kuzivaai/getregula) or email a correction. We would rather be told than be wrong.
