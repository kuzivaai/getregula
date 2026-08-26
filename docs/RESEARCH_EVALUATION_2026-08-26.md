# Research quality evaluation — 26 August 2026

## Verdict

**Pass for the bounded claims made in the accompanying documents.** The
research is sufficiently current, attributable and source-appropriate to
justify the implemented engineering changes and the deliberately narrow
product description. It does **not** establish that Regula is legally correct,
accurate on a representative population, or independently validated.

This evaluation covers
[`RESEARCH_BASIS_2026-08-25.md`](RESEARCH_BASIS_2026-08-25.md), the dated
jurisdiction trackers, the external-corpus protocol and results, and the
research-dependent claims in the model card and coverage pages. Sources were
rechecked on 25–26 August 2026. “Latest” means latest located through the
documented searches, not proof that every repository, paper, bill or standard
was found.

## Claim-and-evidence review

| Claim used by Regula | Best evidence used | Fitness and disposition |
|---|---|---|
| EU AI Act timing may change under the Digital Omnibus proposal | European Commission proposal and legislative observatory; enacted Regulation (EU) 2024/1689 remains the legal baseline | Primary sources. All deadline text carries the proposal/trilogue caveat instead of presenting a proposal as law. |
| South Korea's high-impact threshold requires all three Article 24 conditions; Article 29 business thresholds are alternatives | Official translated AI Basic Act and Enforcement Decree in the Korean Law Information Center, plus MSIT material | Primary law corrected the previous compressed question. The executable model now represents three `all` conditions and four `any` alternatives, with conformance tests. Translation and legal interpretation still require qualified review. |
| Colorado's amended AI duties begin in 2027 | Colorado General Assembly bill text and status for SB 26-189 | Primary legislative source. Tracker distinguishes enacted text and dates from commentary. |
| Static source scanning cannot by itself establish legal applicability, intended purpose, deployment context or operated controls | Statutory decision factors; NIST AI RMF Measure Playbook and AI Technology Evaluation guidance | Appropriate primary/authoritative evidence. Product wording was narrowed to observations, selected cross-references and decision support. |
| Evaluation should separate verification, validation, repeatability, completion and real-world validity | NIST AI RMF/TEVV material; peer-reviewed PrimeVul and context-aware static-analysis studies | Strong methodological support. The external experiment reports integer denominators and retained failures and makes no accuracy claim. |
| Modern OSS evaluation tools provide useful patterns but are not drop-in validators of Regula | Official repositories/docs for Inspect AI, OpenAI Evals, garak, AI Verify, Fairlearn, Semgrep, CodeQL, Joern and Tree-sitter | First-party implementation sources. Concepts were adopted selectively: exact pins, explicit codebooks, task separation, result provenance, adversarial/negative probes and cross-language analysis as future work. No dependency was added to the stdlib-only core. |
| VerifyWise is open source | Repository licence terms show a Business Source Licence transition rather than an unqualified OSI licence | Earlier wording was corrected to **source-available**. It is not used as evidence of an open-source implementation. |
| The pinned corpus exposed concrete regressions and retained blind spots | Exact 40-character commits, manifest digest, two isolated repetitions per variant and generated result JSON | Direct experimental evidence for this scanner version. 18/18 variants repeated and 11/13 heterogeneous assertions passed; neither fraction is precision, recall, efficacy or legal validity. |
| The site meets automated WCAG checks | Local axe-core results at desktop and mobile sizes | Only mechanical evidence. Automated violations and incomplete/manual rules are reported separately; human usability and proficient assistive-technology testing remain outstanding. |

No unattributed quotation is relied on. Legal conclusions are not inferred from
vendor blogs, repository READMEs or search-result snippets. Repository READMEs
are used only to establish purposive corpus selection, not ground truth.

## Corrections made because of this review

- Replaced the opaque South Korea threshold questions with the explicit legal
  criteria and made the `all`/`any` logic executable and testable.
- Reclassified VerifyWise from “open source” to “source-available”.
- Removed statements that a green test suite validates detector efficacy.
- Separated implemented decision rules, selected framework cross-references
  and regulatory trackers throughout the site and documentation.
- Published the two failed corpus probes and completion-with-skips denominator
  rather than presenting 11/13 as a product score.
- Preserved Brazil, Colorado, South Korea, South Africa, UK and UAE tracker
  uncertainty instead of implying a single EU-only compliance surface.

## Quality rubric

The five-point values below assess the **research record**, not Regula's
accuracy, jurisdictions, policies or third-party projects.

| Criterion | Score | Reason |
|---|---:|---|
| Statistical integrity | 5 | Raw integer denominators, repetition count, retained failures and non-representative sampling limits are explicit. No derived accuracy metric is claimed. |
| Quote accuracy | 5 | No material claim depends on an unattributed or unverifiable quotation. |
| Source completeness | 4 | Primary legal and first-party technical sources cover each implemented change; exhaustive discovery and independent legal review remain impossible to claim. |
| Method/policy compliance | 4 | Exact pins, licences, safe no-execution scanning and provenance are documented; the public diagnostic corpus is not sequestered or independently adjudicated. |
| Recency | 5 | Volatile legal, repository and tool observations were rechecked on 25–26 August 2026. |
| Chronology | 4 | Enacted law, proposals and observed dates are separated; future changes after the cutoff remain possible. |

**Overall: 4/5 — pass, with explicit limitations.** The remaining gap is not
more confident prose. It is independent, project-held-out, multi-annotator
validation; moderated research with representative users; qualified legal
review; and proficient screen-reader testing.

## Reproducibility boundary

The external result records the manifest, evaluator, protocol, configuration,
ruleset, codebook and complete scanner/reference source digests. The exact
public inputs can therefore be rerun, but network availability, repository
hosting and platform differences may still affect acquisition or timing. The
working tree was intentionally marked dirty during the final run because it
measured the not-yet-committed candidate implementation; the recorded source
digest identifies that implementation independently of the commit identifier.
