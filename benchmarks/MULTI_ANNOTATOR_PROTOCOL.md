# Multi-Annotator Corpus Upgrade Protocol

Written 27 July 2026. Extends the existing Second-Rater Protocol in
`LABELLING_CRITERIA.md` from 2 raters (Cohen's kappa) to >= 3 independent
raters (Fleiss' kappa), and adds the de-duplication and temporal-split
legs. The goal is a corpus defensible enough to publish as a dataset paper
(MSR or the ICSE/FSE dataset track), which is simultaneously a
judgment-labelled data asset and a citable artefact.

## Why upgrade (verified grounding)

Every citation below was independently verified against its primary
source on 27 Jul 2026 (see `.claude/phase0-verification-2026-07.md`).
Two earlier candidate citations for "kappa precedents in the security
domain" (arXiv:2511.16123, arXiv:2604.04288) FAILED verification (wrong
paper; unconfirmed figures) and must not be cited.

- **Risse, Liu and Böhme (ISSTA 2025, arXiv:2408.12986)**: function-level
  vulnerable/not-vulnerable labels are frequently not assignable without
  calling context; single-labeller function-level tagging is exactly the
  design this critique targets. Our labelling already requires reading
  surrounding context and project purpose (LABELLING_CRITERIA.md); the
  upgrade adds independent replication of that judgment.
- **PrimeVul (ICSE 2025, arXiv:2403.18624)**: label accuracy,
  de-duplication and chronological splitting are the three legs of a
  defensible benchmark. Its abstract
  (https://arxiv.org/abs/2403.18624) reports a state-of-the-art 7B model
  scoring 68.26 percent F1 on BigVul but 3.09 percent on PrimeVul:
  undeduplicated, weakly labelled corpora inflate scores.
- **SecVulEval (AIware 2026, DOI 10.1145/3805760.3814932)**: precedent
  for candid inter-annotator-variability reporting in a security corpus.
- **Li et al. (ESEC/FSE 2023, DOI 10.1145/3611643.3616262)**: ground
  truth built by multi-round independent labelling with consensus
  adjudication; our disagreement procedure follows the same shape.

## Design

### Raters

- N >= 3 independent raters. Rater 1 is the founder (historical labels
  exist). Raters 2 and 3+ must be humans, not LLMs, with sufficient
  technical background (channels and co-authorship offer per the
  Second-Rater Protocol). RECRUITMENT IS THE BINDING CONSTRAINT and is
  owner-action; the tooling below is ready when they are.
- Blind packets per rater, generated exactly as today
  (`select_blind_subset.py` / `label.py sample`); raters never see other
  raters' labels.

### Statistic and target

- **Fleiss' kappa** across all raters on the common subset
  (`benchmarks/annotation_stats.py`, self-test included). Cohen's kappa
  (`compute_kappa.py`) remains for any pairwise view.
- Target: **kappa >= 0.7**. Bands: >= 0.7 publish as-is; 0.6 to 0.7
  publish with an ambiguity analysis; **below 0.6 is itself a publishable
  finding** about the subjectivity of AI-risk-tier labelling, and
  reframes the small-sample high-risk precision figure (33 percent, N=6,
  documented as statistically unmeasurable in `README.md`) as
  task-difficulty evidence rather than a tool defect. Either outcome is
  reportable; neither is suppressed.

### De-duplication

- Run `benchmarks/dedup_check.py` across ALL label files before any
  published count. Exact (project, file, line) duplicates are removed;
  intra-project clusters are collapsed to one representative with a
  multiplicity note; cross-project candidates need human review
  (snippet-level confirmation requires the rescan pipeline; the tool
  states this limitation).

### Temporal split

- Chronological split at PROJECT granularity via
  `benchmarks/temporal_split.py`. BLOCKED on data: per-project
  created_at/pushed_at dates are not yet captured (METHODOLOGY.json has
  only the corpus-level scan date). Capture them during the next rescan;
  the tool refuses to declare a split publishable while any project
  lacks a date.

### Adjudication and provenance

- Unchanged from the Second-Rater Protocol: disagreements are discussed
  and adjudicated, never averaged; original labels preserved; the
  adjudicated label carries `"adjudicated": true` plus notes; all rater
  identities attributed.

### What gets published

Fleiss' kappa with N, rater count, per-tier breakdown, unanimity count,
disagreement dossier, dedup report, split definition, and the full
labelling criteria. Publication venue order: MSR dataset track, then
ICSE/FSE dataset track. See `PAPER_OUTLINE.md`.

## Status (27 Jul 2026)

| Leg | State |
|---|---|
| Rater 1 labels | 50/50 blind subset + 446 corpus labels exist |
| Rater 2 | Packet generated, 0/50 labelled: awaiting recruitment (owner) |
| Rater 3 | Not yet recruited (owner) |
| Fleiss tooling | `annotation_stats.py` ready, self-test passing |
| Dedup tooling | `dedup_check.py` ready |
| Temporal split | Tool ready; per-project dates NOT captured yet |
| Paper skeleton | `PAPER_OUTLINE.md` |
