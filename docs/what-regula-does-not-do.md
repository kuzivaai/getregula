# What Regula does NOT do

An explicit scope statement for the Regula project. This document exists
because the deep-research pass on the moat thesis surfaced a load-bearing
counterargument: **static code scanning may fundamentally address only
about 30% of the EU AI Act.** Articles 9 (risk management system),
Article 17 (quality management system), Article 29a (fundamental rights
impact assessment), Article 72 (post-market monitoring) and much of
Annex IV are organisational obligations, not code-level ones. A Python
CLI that reads source files cannot verify that an organisation has a
functioning risk management system, a board-approved AI policy, or a
legal team that has reviewed a conformity assessment.

This is not a weakness to hide. It is a scope boundary to state plainly.
Regula is the **code layer** of a governance programme. The human and
organisational layers are not Regula's job, and any page that implies
otherwise is wrong.

## Articles Regula can partially or fully address from code

These are the obligations where static analysis of source files
produces useful signal:

| Article | Obligation | What Regula checks | Confidence |
|---|---|---|---|
| **Art. 5** | Prohibited practices | Pattern-detects social scoring, subliminal manipulation, real-time biometric identification, emotion inference in workplaces. Human review required for intent. | High for pattern match; legal determination is human |
| **Art. 10** | Data governance | Training-data file references, dataset-loading patterns, documented data sources | Medium — detects presence/absence, not quality |
| **Art. 11 + Annex IV** | Technical documentation | Generates a pre-filled Annex IV template from scan findings and dependency graph (`regula conform`) | Scaffold only — human must complete |
| **Art. 12** | Event logging | Presence of logging calls near AI model invocations, audit-trail patterns | Medium — detects presence, not completeness |
| **Art. 13** | Transparency | User-facing AI disclosure strings, consent flows, Art. 50 markers | Medium |
| **Art. 14** | Human oversight | Cross-file flow analysis for review-before-action gates (`regula oversight`) | High for pattern match; design determination is human |
| **Art. 15** | Accuracy, robustness, cybersecurity | Error handling around model calls, input validation, known unsafe serialisation (`pickle`, `joblib`) | Medium — detects anti-patterns, not robustness |
| **Art. 49 + Annex VIII** | EU database registration | Generates a pre-filled registration packet from scan findings (`regula register`) | Scaffold only — human must submit |
| **Art. 51–55** | GPAI obligations | Detects GPAI model usage, extracts provenance into an AI-BOM (`regula sbom --ai-bom`) | Medium |
| **Art. 99** | Penalties reference | Surfaces the fine tiers in reports; does not determine liability | Reference only |

## Articles Regula cannot address at all

These are the obligations where static code analysis is structurally
the wrong tool. Regula will not pretend to verify them, and any attempt
to do so from pattern matching alone would mislead the user.

| Article | Obligation | Why Regula cannot verify it |
|---|---|---|
| **Art. 9** | **Risk management system** | A functioning RMS is a set of documented processes, meetings, approvals and reviews that happen inside an organisation. It has no source-code footprint. Regula can detect *absence* of an `docs/ai-rms.md` file or similar artefact, but cannot verify that the RMS is actually operated. |
| **Art. 17** | **Quality management system** | Same logic as Art. 9 at a larger scale. QMS is the organisation's operating rhythm for AI — not something a scanner can observe from code alone. |
| **Art. 26** | Deployer obligations (instructions for use, monitoring, logging retention) | These are operational duties of the deployer organisation. Regula scans the provider-side code; it does not see what the deployer does with the output. |
| **Art. 27** | Fundamental rights impact assessment | FRIA is a structured document produced by the deployer with input from affected persons. Not a code artefact. |
| **Art. 29** | Obligations of importers | Regulatory relationship between the importer and the provider. No code signal. |
| **Art. 43** | Conformity assessment procedure (choosing the path) | Requires a human to choose between internal control (Annex VI) and third-party assessment (Annex VII). Regula can generate the Annex IV technical file but cannot run the conformity assessment. |
| **Art. 63** | Post-market monitoring | Ongoing observation of a deployed system. Regula runs once per scan; PMM runs forever. |
| **Art. 72 / 73** | Serious incident reporting | A process triggered by real-world events. Not detectable from code. |
| **Art. 74** | Market surveillance cooperation | Between the organisation and the market surveillance authority. No code layer. |

## What the lawyer, the auditor, and the internal governance function still have to do

Even on the articles Regula addresses well, a human is on the critical
path. The scanner's job is to produce **evidence** that a lawyer, an
internal auditor, or a notified body can then rely on. The scanner's
job is **not** to produce a legal conclusion.

Specifically, Regula does not:

1. **Determine whether a system is high-risk under Article 6.** This
   requires contextual assessment of intended purpose and deployment
   context. Regula flags Annex III category matches; a human decides
   whether the narrow-procedural-task carve-out in Article 6(3) applies.
2. **Decide whether the Article 2 open-source exemption applies to
   your distribution.** Licence text parsing cannot answer that.
3. **Verify that a GPAI model meets the systemic-risk threshold.**
   Regula surfaces the GPAI usage pattern; the threshold (10^25 FLOPs)
   is a model-provider determination.
4. **Run a fundamental rights impact assessment.** FRIA is a structured
   stakeholder engagement, not a code artefact.
5. **Replace legal advice.** The tool is developer education and
   evidence production. It is not a compliance certificate.

## Where Regula's coverage is thin

Three areas where Regula has commands but the coverage is honest-to-God
shallow. We list them here so nobody overstates what these features do.

### Bias evaluation (`regula bias`)

The `bias` command runs CrowS-Pairs stereotype pairs against a local
Ollama model. This is a single English-language benchmark that tests
whether a model prefers stereotypical over anti-stereotypical sentence
completions. It does not:

- Test your actual model with your actual data
- Measure fairness metrics (demographic parity, equalised odds, etc.)
- Test for bias in languages other than English
- Evaluate bias across protected characteristics specific to your jurisdiction
- Replace the production bias testing that Article 10 data governance requires

Enterprise tools (IBM watsonx.governance, Fiddler AI, Arthur AI) do
production fairness measurement on deployed models with real data.
Regula's bias command is a starting point, not a compliance artefact.

### Documentation generation (`regula conform`, `regula docs`, `regula model-card`)

These commands generate **scaffolds** — structured templates pre-filled
with data from the scan. They are not completed documents. A scaffold
with empty sections is not technical documentation under Annex IV.

Specifically:
- `regula conform` generates an evidence pack structure, not a conformity assessment
- `regula docs --format model-card` generates a model card template, not a model card
- `regula docs --format pdf` generates a formatted shell, not a legal document
- `regula conform --organisational` generates a self-attestation questionnaire — you answer it yourself, nobody verifies your answers

The human work of filling in these scaffolds with substantive content,
reviewing them with legal counsel, and maintaining them across model
versions is the actual compliance activity. The scaffold saves time; it
does not replace the work.

### Guardrail and oversight detection (`regula guardrails`, `regula oversight`)

These commands detect the **presence** of guardrail implementations and
human oversight patterns in code. Presence is not effectiveness.

- `regula guardrails` checks whether input validation, output filtering,
  and execution controls exist in the codebase. It does not test whether
  they actually block adversarial inputs, filter harmful outputs, or
  function under load.
- `regula oversight` traces data flows to human review points. It does
  not verify that the human review is meaningful, timely, or staffed.

A codebase can pass both checks and still have ineffective guardrails
and rubber-stamp oversight. Runtime testing (red teaming, penetration
testing, user studies) is required to verify effectiveness.

## Positioning

Regula is positioned explicitly as the **code layer of a broader AI
governance programme**. The other layers — policy, legal review,
organisational risk management, post-market monitoring, incident
response, regulatory correspondence — are work that humans do, often
supported by enterprise AI governance SaaS (Credo AI, Saidot, Enzai,
IBM watsonx.governance, Microsoft Purview AI Hub). Regula does not
compete with those tools for those layers; it complements them by
doing the part of the job that is best done by reading source code.

For a production compliance programme you will need all of:

- A legal team (or outside counsel) familiar with Regulation (EU) 2024/1689
- An internal governance function with a documented AI policy
- A risk management process tied to actual ISO 42001-style clauses
- A conformity assessment workflow — either via a notified body
  (Annex VII) or internal control (Annex VI)
- Post-market monitoring and incident response procedures
- Staff training on AI Act obligations
- **And** a static code scanner that reads your actual code

Regula is only the last item on that list.

## Industry validation

McKinsey's April 2026 [AI Transformation Manifesto](https://www.mckinsey.com/capabilities/tech-and-ai/our-insights/the-ai-transformation-manifesto)
(Singla, Sukharevsky, Lamarre, Smaje & Levin) independently validates
this scope boundary:

> "Adoption often fails because adjacent upstream and downstream
> processes are left unchanged. An AI solution may predict equipment
> failures days in advance, but if maintenance still follows
> calendar-based scheduling, nothing happens." — Theme 9

This is exactly why code scanning alone does not create compliance.
Regula reads your code. Your organisation must still operate the risk
management system, quality management system, post-market monitoring,
and fundamental-rights impact assessment that the code scanning
cannot verify.

See [`docs/references/mckinsey-ai-manifesto-2026.md`](references/mckinsey-ai-manifesto-2026.md)
for the full theme-by-theme mapping (including three themes that are
honestly excluded because they don't apply to a CLI tool).

## Why this document exists

Because the first rule of this project is honesty about capability.
Saying "Regula is an AI governance platform" would be a material
misrepresentation of what a stdlib-only Python CLI can do. Saying
"Regula is a static code scanner that maps AI Act articles to code
patterns and produces evidence for the items it detects" is exactly
true and correspondingly useful.

The test of this document is simple: can an investor, a regulator, or
a compliance buyer read it and come away with an accurate mental model
of what Regula is and is not? If you think the answer is no, open an
issue and tell us which sentence is wrong.

---

*Last reviewed: 2026-04-11. Canonical version lives in the repository
at [docs/what-regula-does-not-do.md](https://github.com/kuzivaai/getregula/blob/main/docs/what-regula-does-not-do.md).*
