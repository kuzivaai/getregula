# Dataset-paper skeleton (target: MSR data/tool track, else ICSE/FSE dataset track)

Working title: "A Multi-Annotator Benchmark for Static AI-Regulation Risk
Indication in Source Code"

Status: SKELETON. Nothing here is written prose yet; every number in the
final paper must be measured at write-time and pass the repo's
claim-auditing discipline. Citations restricted to the verified set in
`.claude/phase0-verification-2026-07.md`.

## Why this paper can exist (verified white space)

Falsification pass (27 Jul 2026) found NO peer-reviewed study of static
code scanning for AI-regulation compliance properties; adjacent work is
document-level compliance checking (Springer Discover AI, Apr 2026) and
Semantic-Web risk documentation (CLSR S2212473X26000568) — cite both as
related work, scoped honestly as not-code-scanning. First published,
multi-annotator corpus in this niche defines the citable record.

## Outline

1. Introduction: risk INDICATION vs legal classification; why labels here
   are judgment calls (project purpose, deployment context).
2. Related work: PrimeVul; Risse et al.; SecVulEval; Li et al. FSE 2023;
   CASTLE; the two adjacent non-code-scanning papers above; delta-log
   dataset (companion artefact).
3. Corpus construction: random-corpus methodology (50 repos, seeded
   selection, documented queries/filters), targeted corpus, labelling
   criteria (tier-specific), blinding.
4. Annotation study: >= 3 raters, Fleiss' kappa, adjudication procedure,
   disagreement dossier as qualitative data.
5. De-duplication and temporal split: methods + what they changed.
6. Baseline results: Regula's published per-tier precision on the final
   corpus (re-measured), with the FP-penalising scoring discussed in the
   head-to-head harness (benchmarks/headtohead/).
7. Threats to validity: single-tool corpus origin (findings sampled from
   Regula's own detections — selection bias stated, mitigation: report it,
   do not claim tool-independence), small high-risk N, English-repo bias.
8. Data availability: repo + (owner decision) Zenodo DOI; CITATION.cff.

## Hard gates before submission

- Fleiss' kappa computed on >= 3 real raters (never simulated).
- Dedup + temporal split executed and reported.
- Every number re-measured on the frozen corpus commit.
- /research-eval pass on the full draft.
