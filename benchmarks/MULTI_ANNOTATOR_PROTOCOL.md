# Independent annotation and detector-evaluation protocol

Protocol version 2.0 — 25 August 2026

This is a preregistration template, not a benchmark result. It defines the
minimum evidence needed before Regula describes performance on real projects.
Regula detects code-observable indicators for review; the annotation target is
whether a reported indicator is supported by the available code and project
context. It is not a legal classification or compliance judgment.

## Evidence behind the design

- PrimeVul, published at ICSE 2025, reports that weak labels, duplication and
  non-chronological evaluation can materially overstate vulnerability-detector
  performance. It uses de-duplication and chronological splitting:
  <https://doi.org/10.1109/ICSE55347.2025.00038>.
- Risse, Liu and Böhme, published at ISSTA 2025, found that a function-level
  binary vulnerability decision usually cannot be made without surrounding
  context. Regula therefore supplies project and call-site context and permits
  `not_assessable`: <https://doi.org/10.1145/3728887>.
- Zapf and colleagues' peer-reviewed simulation study recommends nominal
  Krippendorff alpha with bootstrap confidence intervals when ratings may be
  missing: <https://doi.org/10.1186/s12874-016-0200-9>.
- VICBench is a useful August 2026 preprint example of exact-version,
  multi-language, independently checked benchmark construction. It has not
  completed peer review, so it informs candidate practice rather than acting
  as validation of Regula: <https://arxiv.org/abs/2608.12246>.
- NIST's TEVV-Athlon initial public draft calls for a structured,
  context-specific evaluation design. It is a draft open for comment through
  6 October 2026, not a final standard:
  <https://doi.org/10.6028/NIST.AI.200-2.ipd>.

## 1. Freeze the measurement target

Before labels are collected, record:

- Regula version, Git commit, rule-set digest and configuration digest;
- corpus manifest digest, licences, acquisition dates and exact repository
  commits;
- the unit of analysis: one emitted finding at one source location, with a
  stable rule ID and sufficient code/project context;
- primary and secondary outcomes, exclusions, subgroup analyses and stop
  conditions;
- a threat model covering label leakage, duplicate code, unavailable context,
  generated fixtures and conflicts of interest.

Changing any frozen item creates a new evaluation version. Results from
different versions must not be silently pooled.

## 2. Construct the corpus before running the detector

1. Define the target population and sampling frame. Convenience samples and
   hand-picked repositories are reported as such.
2. Keep all material from one repository on one side of a split. Use a
   chronological, project-held-out test set where dates are available.
3. De-duplicate before splitting: exact source identity, normalised snippet
   hash, and manually reviewed cross-project near-duplicate candidates.
4. Preserve negatives. A detector-only sample can estimate precision but
   cannot estimate recall, specificity, F1 or MCC.
5. Separate synthetic, seeded, historical and naturally occurring cases.
   Synthetic runtime parity is not real-world detector validity.
6. Record every exclusion and acquisition failure. Do not replace failed
   samples after seeing tool output without recording the deviation.

`benchmarks/dedup_check.py` and `benchmarks/temporal_split.py` implement only
parts of these controls and state their data limitations in their output.

## 3. Independent, blinded annotation

- Use at least three suitably qualified human raters for the common reliability
  subset. Record qualifications, training, conflicts and recusals using
  non-identifying public rater IDs.
- Raters work independently and do not see Regula's score, another rater's
  label, or an adjudicated answer.
- Present the rule description, source location, surrounding control/data-flow
  context and the public project purpose. Do not reduce a context-dependent
  task to an isolated function.
- Allowed labels are `tp`, `fp`, `uncertain` and `not_assessable`. A rationale
  and context-sufficiency field are required. `not_assessable` is missing for
  TP/FP agreement and performance calculations, not a negative label.
- Preserve every original rating. Adjudication creates a separate record with
  its own rationale and source evidence; it never overwrites independent
  ratings.

## 4. Agreement and adjudication

Report nominal Krippendorff alpha, an item-bootstrap 95% confidence interval,
the number of raters and pairable items, rating coverage, label prevalence,
raw agreement and the disagreement table. `benchmarks/annotation_stats.py`
computes alpha with a deterministic seed and retains Fleiss kappa as a
complete-case compatibility view.

No universal alpha threshold proves that a corpus is publishable. The interval,
prevalence, missingness, task consequences and disagreement reasons determine
whether the labels support the intended claim. Revise an ambiguous codebook on
a separate training sample; do not tune it on the held-out result and then
report the same result as confirmatory.

Adjudication is done after the agreement snapshot is frozen. The public record
contains original labels, adjudicated label, evidence consulted, adjudicator
ID, date and whether the codebook changed.

## 5. Performance and abstention

For every population and subgroup, report integer confusion counts before
derived metrics. Report precision, recall/sensitivity, specificity, F1 and MCC
only when their required denominators exist. Add binomial confidence intervals
for proportions and identify the interval method.

Regula's current 0–100 detector priority is heuristic and must not be treated as
a correctness probability. Calibration or risk-control claims require an
independent representative calibration set and a held-out evaluation. Until
that evidence exists, missing deployment context produces an explicit review
requirement or abstention, not a confident legal conclusion.

When abstention is evaluated, report:

- coverage: the fraction receiving a non-abstaining result;
- selective risk/error among covered items;
- error and class composition among abstained items;
- results across predeclared thresholds, without selecting a threshold on the
  final test set.

## 6. Repetition and reporting

- Run the frozen evaluator at least twice in clean environments and compare
  content hashes, case IDs, results and completion manifests.
- Report hardware, operating system, Python version, duration, peak resources,
  skipped files and parser/fallback mode by language.
- Report micro and macro results and predeclared language/domain/rule subgroups;
  do not hide small or poor-performing strata inside one aggregate.
- Publish the protocol, codebook, schema, manifests, evaluator and deviations
  with the result. Private source code or personal rater data remains outside
  the public repository.

## Current evidence boundary

The repository still contains maintainer-labelled and synthetic corpora useful
for regression testing and hypothesis generation. They do not establish
independent real-world accuracy. A performance claim remains blocked until this
protocol is executed on a licence-compatible, independently labelled,
project-held-out corpus.
