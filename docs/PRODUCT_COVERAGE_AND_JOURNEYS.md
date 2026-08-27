# Product coverage, users, journeys, and information architecture

Status: product contract, reviewed 26 August 2026.

This document defines what Regula exposes, who each path serves, and which
claims the interface may make. It is deliberately narrower than a feature
inventory. A command or reference file existing does not establish that Regula
can determine compliance with a law or framework.

## Coverage is a level, not a badge

| Level | Meaning | Current coverage | Permitted claim |
|---|---|---|---|
| **Decision support implemented** | A versioned questionnaire and evidence-gated decision model can evaluate declared facts. Detector matches remain observations, never legal facts. | EU AI Act; South Korea AI Basic Act; Colorado SB 26-189 | “Records facts and produces a reviewable indication for …” |
| **Detector or framework crosswalk** | Findings link to selected provisions or control families. This does not evaluate applicability, implementation, or conformity. | NIST AI RMF, ISO/IEC 42001, NIST CSF, SOC 2, ISO/IEC 27001, OWASP LLM Top 10, OWASP Agentic, MITRE ATLAS, EU CRA, LGPD, proposed Brazilian AI framework, UK ICO/DSIT principles | “Maps findings to selected references in …” |
| **Regulatory tracker** | A dated, sourced page summarises the current public position. It may inform scoping but is not executable legal logic. | Brazil, United Kingdom, South Africa, United Arab Emirates, and other region pages | “Tracks public developments in …” |

The levels are not a quality ranking. They describe different implemented
capabilities. No level means “certifies compliance”, “covers every applicable
rule”, or “replaces qualified legal, regulatory, accessibility, security, or
domain review”. Region pages must state their review date and distinguish law,
proposal, policy, guidance, standard, and Regula functionality.

## People and the tasks they are trying to complete

### Builder or maintainer

**Task:** identify source-code signals worth investigating before release,
without uploading proprietary code.

**Needs:** a quick local start, visible scan scope and completion, precise file
references, reasons for findings, useful suppression/configuration paths, and
an honest clean-scan message.

**Likely failures:** treating a pattern as a legal conclusion; assuming skipped
or unsupported files were checked; blocking CI before measuring local false
positives; missing intended-purpose facts that are not present in code.

### Governance or assurance reviewer

**Task:** combine technical observations with sourced deployment and operator
facts, preserve uncertainty, and prepare material for accountable review.

**Needs:** provenance, jurisdiction and role context, unresolved facts,
contradictions, applicable provisions, reproducible artefacts, and a clear
boundary between generated scaffolds and verified evidence.

**Likely failures:** reading self-attested evidence as independently verified;
using an outdated legal summary; allowing `unknown` or missing facts to become
`no`; mistaking a framework crosswalk for a control assessment.

### Evaluator or adopter

**Task:** decide whether Regula is suitable for a particular codebase and
workflow before depending on it.

**Needs:** version-pinned tests, a representative local sample, known failure
modes by language/domain, timing and completeness data, stable output
contracts, accessibility evidence, and an exit path if validity is inadequate.

**Likely failures:** generalising from synthetic fixtures; treating diagnostic
open-source examples as precision/recall; accepting repeatability as validity;
or applying a single CI threshold across unlike projects.

### Qualified contextual reviewer

Legal counsel, a DPO, regulator-facing assurance staff, a domain specialist,
or an accessibility/security professional may consume Regula artefacts. Regula
does not replace their judgment and must not present generated material as
their opinion, approval, or certification.

## Primary journeys and required states

### 1. Assess a project

1. **Choose scope:** jurisdiction, deployment, role, intended purpose, domain,
   and source tree.
2. **Declare facts:** record source, actor, time, and `yes`, `no`, `unknown`, or
   `not_applicable`; preserve contradictions.
3. **Scan locally:** show discovered, eligible, scanned, skipped, unsupported,
   and failed files. Never equate “no finding” with “low risk”.
4. **Review observations:** explain the matched signal, confidence boundary,
   relevant provision or crosswalk, and suppression/configuration route.
5. **Resolve context:** show which facts block the next decision and why.
6. **Prepare evidence:** generate labelled, reviewer-completable scaffolds with
   integrity metadata and unresolved fields intact.
7. **Human decision:** an accountable reviewer confirms, rejects, or requests
   evidence outside Regula.

Required interface states: first-use guidance; running/progress; complete;
complete-with-skips; no eligible files; no indicators; indicators found;
insufficient information; contradictory facts; invalid configuration; partial
output; and recoverable failure. A control whose path is unavailable must be
disabled with an explanation or removed.

### 2. Evaluate Regula before adoption

1. Read the claim boundary and model card.
2. Reproduce the synthetic conformance tests.
3. Run the pinned external diagnostic corpus without executing target code.
4. Create a sequestered, representative local sample with an independently
   authored codebook and at least two qualified annotators.
5. Resolve disagreements, report inter-rater reliability, precision/recall by
   domain and language, abstentions, completion, and uncertainty intervals.
6. Test the intended CI policy on a non-blocking branch and measure review
   burden and missed material issues.
7. Conduct representative user research and assistive-technology testing for
   the actual workflow before calling it user-ready.

Repeatability, runtime parity, and a green test suite are necessary engineering
evidence. They do not establish detector validity or legal correctness.

## Website information architecture

The public site should answer four questions in this order:

1. **What task can I complete?** Assess scope, scan code, review evidence, or
   track a regulatory development.
2. **What does the result mean?** Indicator, declared fact, unresolved fact,
   scaffold, or dated reference—not a compliance verdict.
3. **What coverage exists?** Show the three coverage levels above before the
   list of jurisdictions and frameworks.
4. **Can I trust it for my context?** Link directly to methods, pinned results,
   limitations, security/privacy, accessibility evidence, and human-validation
   gaps.

Recommended top-level destinations are task labels rather than internal
feature names: **Assess scope**, **Scan code**, **Review evidence**,
**Coverage**, and **Methods & limits**. Region pages belong beneath Coverage;
installation and command reference belong beneath Scan code; model card,
external evaluation, accessibility, security, and research basis belong beneath
Methods & limits.

## Acceptance evidence still required

- Independent, multi-annotator validation on representative production
  applications is not complete.
- Representative moderated usability research is not complete.
- Manual screen-reader testing by proficient users is not complete.
- Legal interpretations require continuing review against primary sources and
  qualified local counsel.
- The non-English assessment pages need comprehension testing with fluent
  German and Brazilian Portuguese users; translation parity tests do not
  establish comprehension.

These are evidence gaps, not items that automated tests may mark complete.
