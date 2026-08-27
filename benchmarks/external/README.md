# External diagnostic corpus

This corpus asks a bounded question: on exact, licence-declared public project
snapshots, what code-observable indicators does Regula emit and does it do so
repeatably? It does **not** provide legal ground truth or an accuracy estimate.

The manifest was frozen before execution. Its repositories form a purposive
diagnostic sample spanning horizontal infrastructure, general AI applications,
and projects that document employment, credit, education, health or biometric
capabilities. Repository popularity is not a label. A README description is
evidence of a documented project capability, not evidence that any law applies.

## Reproduce safely

```bash
python3 benchmarks/run_external_corpus.py \
  --manifest benchmarks/external/manifest.v1.json \
  --output /tmp/regula-external-results.json
```

The runner validates every URL, commit, licence, domain and expectation before
network access. It initialises an empty repository, fetches only the pinned
commit, verifies `HEAD`, and never imports, builds, installs or executes target
code. Each repetition uses an isolated scan cache and audit directory. Output
contains counts and finding metadata, not third-party source excerpts.

## Interpretation gates

- A passed negative-control assertion means no predeclared elevated detector
  class appeared in this snapshot/configuration. It does not establish
  specificity.
- A passed capability probe means at least one requested review class appeared.
  It does not establish that each finding is correct or that the project is in
  legal scope.
- A failed probe is a diagnostic lead. It becomes a false positive or false
  negative only after context-complete, independent human annotation.
- Recall, precision, F1, MCC and calibration remain unavailable from this
  corpus because it has no exhaustive independently adjudicated ground truth.
- The sample is not random or representative. Do not generalise rates from it
  to GitHub or production code.

The independent-labelling gate remains
[`MULTI_ANNOTATOR_PROTOCOL.md`](../MULTI_ANNOTATOR_PROTOCOL.md). The wider
evaluation preregistration remains
[`evaluation_protocol.v1.json`](../evaluation_protocol.v1.json).
The dated observed result and its claim boundary are recorded in
[`docs/EXTERNAL_DIAGNOSTIC_2026-08-26.md`](../../docs/EXTERNAL_DIAGNOSTIC_2026-08-26.md).

## Method basis

The design uses project-held-out, context-preserving and exact-version controls
described in the benchmark protocol. It also follows NIST's distinction between
verification (specified behaviour) and validation (fitness for an intended use),
and NIST AITE's use of sequestered evaluation to reduce contamination. The NIST
TEVV-Athlon document cited by the protocol is an initial public draft, not a
final standard. Those sources inform the method; they do not validate Regula.
