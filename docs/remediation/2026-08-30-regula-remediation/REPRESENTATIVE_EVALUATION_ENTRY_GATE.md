# Representative evaluation entry gate

Date: 30 August 2026

## Decision

BLOCKED. Regula does not pass the representative-evaluation entry gate.

## What is ready

- OBSERVED: one schema, version 1.0, is consumed by both evaluation utilities.
- OBSERVED: the canonical identifier scheme is
  `corpus-project-file-line-v1`.
- REPRODUCED: 15 integration tests cover the real packet shape, blinded fields,
  complete synthetic pairs and incomplete real packets.
- REPRODUCED: rater 1 contributes 50 labels, rater 2 contributes 0, overlap is
  0, and agreement is reported as incomplete rather than calculated.

## Entry conditions still unmet

- BLOCKED: no representative corpus has received the required independent
  evaluation.
- BLOCKED: no second independent rating exists.
- BLOCKED: no agreement statistic can be calculated from zero overlap.
- UNVERIFIED: detector validity, false-positive and false-negative rates on a
  representative corpus.
- UNVERIFIED: protocol execution by independent raters and adjudicators.

Synthetic fixtures and self-tests are retained as implementation controls. They
are not evidence that the later human evaluation workflow has succeeded.
