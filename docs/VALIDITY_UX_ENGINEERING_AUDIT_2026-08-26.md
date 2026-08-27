# Regula validity, UX and engineering audit — 26 August 2026

## Executive conclusion

Regula **works as a local, reproducible source-code indicator and evidence
scaffolding tool**. It executes, returns stable machine envelopes, preserves
unknown and conflicting facts, cites provisions, and exposes many important
scope limits. That is useful for triage and for preparing a human review.

Regula is **not yet validated as an accurate real-world regulatory-risk
detector**, and it cannot validate compliance. The current evidence does not
support calling it a compliance classifier, legal decision-maker, conformity
assessment, or dependable clean/unsafe gate. The final default CLI path found
only 4 of 30 hand-authored high-risk synthetic fixtures. Available real-code labels were
created by one maintainer, are Python-dominated, are not exhaustive enough to
measure recall, and do not describe the current detector reliably. No
independent representative user study establishes that people understand or
successfully act on the output.

The website and assessment have strong mechanical UX and accessibility
foundations, including explicit unresolved states and usable keyboard paths.
They are not “user-ready” by evidence alone: representative task testing and
screen-reader sessions remain outstanding. Automated accessibility results are
not a WCAG conformance claim.

This mixed verdict is deliberate. Operational correctness, detector validity,
legal validity, usability and accessibility are different questions; a large
green test suite answers only part of them.

## Scope and appraisal method

The final candidate was evaluated from parent commit `ba679fc1` plus the
tracked changes listed below. It inspected the code, public claims, CI history, benchmark
artefacts, CLI behaviour, browser assessment, responsive website, dependency
environment and privacy guard. Research was refreshed on 26 August 2026.

Sources were prioritised in this order:

1. enacted law and official consolidated text;
2. standards bodies and public regulators;
3. peer-reviewed research;
4. official project documentation and executable repository evidence;
5. repository metadata and emerging preprints, clearly limited to maintenance
   or hypothesis signals.

This is a structured engineering audit, not a complete systematic literature
review, legal opinion, penetration test, or representative usability study.
Repository stars are adoption context, never a validity score. “Current” means
observed on the audit date and cannot prove that an unindexed newer source did
not exist.

The regulatory source review and detector-method research from the preceding
day remain in [`RESEARCH_BASIS_2026-08-25.md`](RESEARCH_BASIS_2026-08-25.md).

## Intended-purpose verdict

| Question | Finding | Evidence boundary |
|---|---|---|
| Does the software execute repeatably? | Yes, in the tested environments | Full automated suites, self-test, doctor, CLI/browser exercises; not every operating system or repository shape |
| Does it detect its authored rule fixtures? | Partly | Strong prohibited-fixture result; weak default high-risk coverage; synthetic fixtures are authored around known concepts |
| Is real-world precision known for the current version? | No | Available labels are dated, single-reviewer development records; the old random-corpus subset is not re-runnable |
| Is real-world recall known? | No | Labelled findings omit false negatives and therefore cannot estimate recall |
| Are scores calibrated probabilities? | No | They are priority heuristics; there is no representative calibration corpus |
| Can code observations establish legal risk tier or obligations? | No | Intended purpose, deployment, operator role, exceptions and organisational operation require externally sourced facts and qualified review |
| Does the decision kernel handle missing facts honestly? | Yes, for the exercised model | Unknown, absent, no, not-applicable and contradiction are distinct; mutation/conformance tests cover declared paths |
| Are generated documents compliance evidence? | Only as scaffolds and self-attested records | Completeness, truth, organisational operation and legal sufficiency remain human responsibilities |
| Can users complete the primary web tasks mechanically? | Yes, on the exercised desktop/mobile and keyboard paths | This is browser evidence, not representative human usability or assistive-technology evidence |

## Detector evidence reproduced

### Synthetic label fidelity

The committed 38-fixture corpus contains 5 prohibited, 30 high-risk and 3
negative fixtures. Fresh runs reproduced the committed artefact:

| Runtime and gate condition | High-risk label fidelity | Prohibited label fidelity |
|---|---:|---:|
| Context-free Python/browser classifier, no project/domain gates | 18/30 (60.0%) | 5/5 |
| CLI scanner, default scan, no flags | 4/30 (13.3%) | 5/5 |
| Scanner with all domains declared | 16/30 (53.3%) | 5/5 |
| Scanner with domains plus an injected AI import | 23/30 (76.7%) | 5/5 |
| Python classifier with all domains declared | 16/30 (53.3%) | 5/5 |

These are path-and-condition-specific label-fidelity measurements, not
real-world recall. The three negatives remained negative. Core Python and
browser JavaScript classification agree on all 38 fixtures, but the full CLI
adds project policy, fingerprinting and opt-in domain gates. Consequently,
same-file end-to-end labels differ: 12 of the CLI default misses are recovered
by declaring all domains, seven more after injecting an AI import, and seven
remain missed under the most permissive measured scanner condition. The 4/30
default result is material under-detection in this authored corpus; the 18/30
browser result is not evidence that the ungated browser is more accurate.

### Real-code development records

- Dated library labels: 39 TP and 218 FP, 15.2% arithmetic precision over 257
  labelled findings.
- Dated hand-picked application labels: 125 TP and 64 FP, 66.1% arithmetic
  precision over 189 labelled findings.
- Combined dated labels: 164 TP and 282 FP, 36.8% over 446 findings.
- The old random-corpus artefact records 83.5% over an N=115 production
  subset, but the subset membership and pinned repository snapshots were not
  preserved. It used one reviewer and Regula v1.7.0.

None is a current independent detector-accuracy estimate. The library command
can reproduce arithmetic over its label file; it cannot prove that those labels
cover the present scanner output. The old random command redisplays a tracked
score artefact rather than reconstructing its measured population.

The audit removed the old random result from the current README and generated
executive summaries. It remains in the benchmark and model-card history with
its limitations. A previous test that required the README to keep publishing
the number was reversed into a guard that prevents it being presented as a
current product claim.

### Coverage and completion

The analysis manifest now reports discovered, eligible, scanned and
unsupported counts, plus the normalised eligible suffix population. It retains
the existing scanned/skipped evidence and explicit completion status. This
closes the earlier defect where “zero skipped” could be misread as complete
coverage despite unknown discovery and language denominators. Exclusions,
unreadable inputs and pruning still need to remain explicit wherever those
paths apply; a clean finding list is never a completeness statement.

This principle appears in current open-source work such as
[saasvista/aibom-scanner](https://github.com/saasvista/aibom-scanner): observed
and inferred inventory should be separate, unreadable/unsupported inputs must
not look clean, and incomplete analysis needs a distinct status. The practice
is useful; the repository's own claims are not independent validation of
Regula.

### Pinned external diagnostic corpus

A frozen manifest now records 13 licence-declared public repositories at exact
commits, 18 scan variants and 13 predeclared diagnostic assertions. Target code
is fetched as untrusted data and is never imported, installed, built or run.
Two isolated repetitions produced byte-stable result content for all 18
variants. Of 36 repetitions, 26 completed fully and 10 completed with explicit
skips.

The unchanged manifest produced 6/13 passing assertions before error-led rule
changes and 11/13 afterwards. The comparison exposed and supported fixes for a
Go race-detector false escalation, broad identity/face/speaker vocabulary,
cross-language agent command execution, and declared employment, finance and
biometric context. The private-gpt transparency probe and education-declared
proctoring probe still fail and were retained.

The fraction is not precision, recall, legal validity or a product score. The
assertions are heterogeneous hypotheses over a purposive sample and lack
exhaustive independent labels. Exact method, projects, observed denominators
and limitations are in
[`EXTERNAL_DIAGNOSTIC_2026-08-26.md`](EXTERNAL_DIAGNOSTIC_2026-08-26.md).

## Research synthesis and decisions

### Test speed without efficacy loss

[pytest-xdist](https://github.com/pytest-dev/pytest-xdist) 3.8 was the only
reviewed mechanism adopted for the required gate because it distributes the
unchanged complete collection. Its `worksteal` scheduler fits Regula's highly
uneven durations. Controlled local runs and a four-interpreter GitHub Actions
experiment both preserved result totals and succeeded; exact results are in
[`PERF_REPORT.md`](../PERF_REPORT.md).

Required-gate test selection was rejected. The May 2026 NameRTS preprint
reports a 45.59% time reduction and 99.6% safety on its study population; that
remaining miss rate is incompatible with a sole release gate and the paper is
not yet peer reviewed ([arXiv 2605.25356](https://arxiv.org/abs/2605.25356)).
Tools such as [pytest-testmon](https://github.com/tarpas/pytest-testmon) may be
useful for optional local feedback, not as evidence that unselected tests pass.

Mutation testing was retained as a targeted future efficacy audit, not a main
CI speed technique. Both [mutmut](https://github.com/boxed/mutmut) and
[Cosmic Ray](https://github.com/sixty-north/cosmic-ray) were active when
observed. A peer-reviewed 2026 study identifies eight methodological threats
that can materially inflate predictive-mutation results, including class
imbalance, project heterogeneity and weak reproducibility
([DOI 10.1007/s10515-026-00626-9](https://doi.org/10.1007/s10515-026-00626-9)).
Any Regula pilot must publish operator set, target modules, equivalent/invalid
handling, timeouts and raw killed/survived counts.

### Detector architecture

Mature static-analysis ecosystems continue to support a staged design:
lexical candidate generation, syntax-aware confirmation, explicit local flow,
then bounded cross-file analysis for high-value rules. Regula keeps the
stdlib-only core and now includes its existing Tree-sitter adapters in the
complete contributor test environment. [Tree-sitter](https://github.com/tree-sitter/tree-sitter),
[Semgrep](https://github.com/semgrep/semgrep),
[CodeQL data-flow documentation](https://codeql.github.com/docs/writing-codeql-queries/about-data-flow-analysis/)
and [Joern's code-property graph](https://docs.joern.io/code-property-graph/)
remain reference baselines, not wholesale dependencies or evidence that
Regula inherits their accuracy.

Current AI-governance projects show useful process ideas but no repository
reviewed supplied independent validation of Regula. Examples observed on the
audit date include [VerifyWise](https://github.com/verifywise-ai/verifywise),
[EuConform](https://github.com/Hiepler/EuConform),
[airblackbox](https://github.com/airblackbox/airblackbox), and
[aibom-scanner](https://github.com/saasvista/aibom-scanner). Airblackbox's
published balanced synthetic evaluation is appropriately limited to its 72
fixtures; that is a good disclosure pattern, not evidence of arbitrary
production-code performance.

### Validity and evaluation method

The next evaluation should follow the existing
`benchmarks/MULTI_ANNOTATOR_PROTOCOL.md`: exact licensed project commits,
deduplication before split, project-held-out and chronological evaluation,
independent blinded reviewers, retained disagreements, `not_assessable`,
inter-rater reliability with intervals, and integer confusion counts before
derived metrics.

This aligns with the official [NIST AI RMF Measure
Playbook](https://airc.nist.gov/airmf-resources/playbook/measure/) emphasis on
documented test sets, representative contexts and independent assessors, and
with peer-reviewed benchmark lessons from
[PrimeVul](https://doi.org/10.1109/ICSE55347.2025.00038) and
[Top Score on the Wrong Exam](https://doi.org/10.1145/3728887). Security-code
benchmarks are analogies, not proof that Regula's regulatory construct is
valid. Legal/context labels need their own study.

## Website and interaction audit

### Browser paths exercised

The rendered site was inspected at 1400×900 and 390×844. The following paths
were exercised in Chromium rather than inferred from markup alone:

- homepage navigation, mobile menu open/close, focus entry, Escape and focus
  return;
- empty questionnaire submission, alert and focus on the first unanswered
  control;
- all-unknown questionnaire completion and its explicit unresolved result;
- full `/assess/` progress, button states, keyboard shortcut, citations,
  early result, absent/unknown fact listing and JSON export affordance;
- desktop and mobile reflow of the assessment and primary content.

The assessment uses a semantic progressbar, visible selected states, genuine
disabled Back/Next states, specific error recovery, focusable result headings
and “more facts required” rather than manufacturing an obligation. This is a
strong match to task-completion and truthfulness requirements.

### Accessibility automation and manual follow-up

Playwright 1.62.1 with axe-core 4.12.1 audited all 54 discovered canonical
pages at both viewports: 108 runs, zero automatically detected violations and
71 unresolved color-contrast reviews containing 516 nodes. Every unresolved result is retained as
incomplete, not counted as a pass. The audit runner now stores the rule, every
target, relevant HTML and axe failure summary rather than discarding the
evidence behind the count.

Manual calculation of shared translucent/gradient styles found three genuine
AA contrast defects hidden inside the incomplete set:

**Correction, re-derived 27 August 2026:** this paragraph originally said 511
nodes. A fresh complete run over the same 54 canonical pages and two viewports
enumerated 516 nodes across 71 incomplete results. Report SHA-256:
`7a94a6d0698634fa848c3c421424d439fcb6629a309e5580c5e6be81aa8007b4`.
The earlier 511 was a transcription error, not a different audit population.

- 13px blue decision-tree numbers: 4.13:1; changed to 5.97:1;
- the 11px pricing badge: white on blue at 3.68:1; changed to 5.17:1;
- the UAE action gradient: one white/blue stop at 3.68:1, with an additional
  light green state; both gradients now use stops above 4.5:1.

Shared mobile navigation, callout, tracker and audience-card combinations were
also calculated against their worst declared composite backgrounds and met the
4.5:1 normal-text threshold in the checked states. Gradient, backdrop-filter,
pseudo-element and overlapping-content cases still require manual review
because axe cannot determine their effective background reliably.

WCAG 2.2 AA remains a target, not a conformance claim. Outstanding manual work
includes 200% text size, 400% reflow, text spacing, forced colours, reduced
motion, NVDA/Firefox or Chrome, VoiceOver/Safari, TalkBack/Chrome and testing
with representative disabled users. See
[`accessibility/README.md`](accessibility/README.md) and the
[WCAG 2.2 Recommendation](https://www.w3.org/TR/WCAG22/).

### Performance evidence

The homepage's first-party encoded payload was approximately 270 KB in the
local browser audit, including HTML, CSS, JavaScript and fonts. Localhost load
timings were in milliseconds and are not field performance. No sufficient
CrUX/RUM population was established, so Regula does not claim to pass Core Web
Vitals. Current field thresholds remain p75 LCP at most 2.5 seconds, INP at
most 200 ms, and CLS at most 0.1
([web.dev](https://web.dev/articles/defining-core-web-vitals-thresholds)).

### Human validation still required

No representative moderated study was found in the repository. The browser
evidence shows operability for the exercised paths; it cannot establish
comprehension, confidence, usefulness or task success for developers,
governance reviewers or people using assistive technology. The key research
question is whether users correctly understand “indicator,” “unknown fact,”
“not assessed” and “human/legal review required,” especially after a clean or
high-severity result.

## Public-repository and privacy audit

`scripts/public_repo_guard.py` scanned 742 tracked files and reported zero
findings. Targeted term searches found legitimate regulatory detection rules
and synthetic regulatory fixtures, not private personal material. Deleting
those rule fixtures merely because a word can also appear in personal context
would reduce detector coverage. No personal records, employer details,
business plans, pricing strategy, handover/session logs, credentials or machine
identity were found in the tracked public tree during this audit.

This verifies the current tracked tree, not all Git history. The repository's
push URL remains disabled pending a separately reviewed sanitised-history
replacement. Nothing was published by this audit.

## Engineering changes made

- Added pytest-xdist to the contributor test extra and regenerated `uv.lock`.
- Made the test extra complete for YAML, JSON Schema, syntax-aware JS/TS,
  signing, timestamping and telemetry privacy paths; the installed core remains
  dependency-free.
- Distributed the complete four-version pytest matrix over two workers while
  adding a complete Python 3.12 sequential order/shared-state audit.
- Moved the alternate custom harness and product-contract audits to one
  independent job instead of repeating that harness four times.
- Disabled fail-fast for the interpreter matrix.
- Corrected contributor instructions that described a stale manual test list
  and incomplete environment.
- Removed a superseded detector-accuracy number from current product copy and
  generated summaries; strengthened the regression guard against reintroduction.
- Reframed language and article-coverage claims where the repository had used
  unsupported “high,” “medium,” “full,” or “current benchmark” language.
- Preserved complete axe incomplete-node evidence and fixed three contrast
  defects found during manual review.
- Added this audit and the root performance report.
- Added a pinned, licence-declared external diagnostic corpus with exact commits,
  predeclared hypotheses, no target-code execution, isolated repetitions,
  completion denominators and source/configuration/evaluator digests.
- Corrected external-corpus failures without editing the frozen manifest and
  added focused regressions for every adopted rule change.
- Replaced Korea's opaque delegated-threshold facts with the three conjunctive
  Enforcement Decree Article 24 criteria and four disjunctive Article 29
  domestic-agent criteria, then regenerated and retested the CLI/browser model.
- Published explicit capability levels, user archetypes, task journeys, failure
  paths and task-first information architecture in all three website locales.

## Final verification evidence

The completed post-change checks produced:

- final mandatory default-order pytest: 2,882 passed and 38 skipped across the
  complete 2,920-test collection in 515.75 seconds;
- alternate custom harness: 1,453 helper assertions passed, zero failed and 8
  optional/local-tool skips across 1,289 discovered test functions;
- built-in self-test: 6/6 passed; doctor: 9 passed and 3 informational notices;
- controlled speed experiment before the additional audit tests: the same
  2,861 passes, 38 skips and 11 subtests took 157.68 seconds under two-worker
  xdist versus 527.66 seconds in default sequential order;
- pinned external diagnostic: 13 repositories, 18 variants, 36 repetitions,
  18/18 byte-repeatable variants, 26 fully complete runs, 10
  completed-with-skips runs, and 11/13 predeclared assertions observed;
- public-repository guard: 742 tracked files and zero findings;
- workflow YAML parse, JavaScript syntax, lock consistency, claim facts,
  quotations, transcripts, questionnaire scoring and source-of-truth checks;
- final browser accessibility audit: 54 pages, two viewports, 108 runs, zero
  automatically detected violations and 71 explicitly unresolved manual
  contrast reviews.

The skip count is not presented as missing dependency coverage. The complete
test extra was installed; remaining skips are reported by the tests for their
declared platform or local-tool conditions. The custom harness recovered four
previous optional-feature skips after the syntax-aware dependencies were added.

## Defensible next work, in order

1. **Independent detector study:** execute the preregistered multi-annotator
   protocol. Until then, keep accuracy claims frozen.
2. **Error-led detector improvement:** improve high-risk default misses and
   TypeScript false-positive clusters one rule family at a time; compare on
   project-held-out data and publish regressions as well as gains.
3. **Human comprehension study:** test primary scan and assessment tasks with
   representative developers and governance reviewers; include clean,
   high-severity, unknown, incomplete and error states.
4. **Assistive-technology matrix:** complete and record the manual WCAG work,
   including representative disabled-user testing.
5. **Remote CI confirmation:** after the history/publication gate is cleared,
   run the updated workflow and compare its critical path with the measured
   baseline. Do not infer the improvement from YAML alone.
6. **Targeted mutation pilot:** completed for the pure decision model on 27
   August 2026. The two declared operators produced 136 reconciled mutants:
   136 killed, 0 survived, 0 invalid and 0 timed out. Equivalent mutants were
   not assessed. This scope does not establish detector validity or legal
   correctness.
7. **Field performance:** collect privacy-preserving real-user Core Web Vitals
   only if there is a lawful, transparent and sufficiently populated method;
   otherwise retain lab results as diagnostics.

These steps prioritise construct validity, honest completion evidence and user
comprehension over adding more rules or publishing a larger test count.
