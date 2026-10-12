# Security and privacy review

Date: 30 August 2026

## Finding

The candidate materially narrows MCP, REST, feedback and weekly-digest authority. The local security posture is improved, but this is not a penetration test, security certification or production approval.

## Cache

Disposition: CONFIRMED within tested Linux semantics.

REPRODUCED:

- Rules A then B and B then A are order-independent.
- Threshold, policy, domain, parser, path-context and scanner changes alter cache identity.
- Equivalent rule ordering canonicalises consistently.
- Corrupt cache input is recovered without manufacturing a hit.
- Atomic replacement, competing writers, bounded eviction and disabled persistence are exercised.
- Material write failures are reported without changing scan results.

Remaining limitation: native Windows locking and replacement semantics were not executed.

## MCP

Disposition: PARTIALLY CONFIRMED.

REPRODUCED:

- An explicit workspace root is required.
- Resolved paths must remain within that root.
- Traversal and symlink escapes are refused.
- Sensitive and out-of-scope paths are refused.
- File count, per-file bytes and total bytes are bounded.
- Audit events omit source contents and minimise path information.

BLOCKED: native Windows path, junction and case-folding behaviour was not executed.

## REST

Disposition: PARTIALLY CONFIRMED.

REPRODUCED:

- Loopback remains the default.
- Accidental non-loopback binding fails closed.
- A distinct unsafe-network acknowledgement is required for supported non-loopback binding.
- Request size, nesting, path containment, concurrency and error disclosure have negative tests.

The server has no authentication and must not be positioned as a production API. A reverse proxy would be a separate deployment requiring independent review.

BLOCKED: this session cannot open a loopback socket for the final browser and RFC 3161 chain.

## Weekly digest

Disposition: CONFIRMED for repository authority.

OBSERVED and REPRODUCED:

- Repository permission is read-only.
- Checkout credentials are not persisted.
- Issue content is bounded and treated as untrusted data.
- Model output must satisfy a strict review-summary schema.
- No helper or workflow step commits, pushes, publishes or opens issues.
- Output is a human-review job summary.

Remaining limitation: the external model service, retention policy, training policy and endpoint approval were not verified.

## Feedback

Disposition: CONFIRMED in tests.

REPRODUCED:

- The exact outbound content is shown before action.
- Local paths and likely secrets are minimised or redacted.
- Source content is not included by default.
- Affirmative confirmation is required.
- Cancellation opens no browser and performs no network action.

No external URL was opened during this review.

## Static checks

- Ruff on changed production and test files: PASS. The unfiltered all-tree run reports two intentional unused constructs in `tests/fixtures/sample_high_risk/app.py`.
- Bandit at high-severity threshold: PASS. The unfiltered run reports 97 low-severity subprocess and non-cryptographic-randomness findings, with zero medium or high findings. These were not suppressed or reclassified.
- Python bytecode compilation: PASS.
- Regula security self-check: PASS with seven known acceptable pattern-definition findings and zero unexpected findings.
- Locked all-extras dependency vulnerability lookup: BLOCKED because DNS remained unavailable even after approval. The lock export itself completed.

## Privacy and provenance

- No source, token, secret, customer record or personal record was sent externally.
- No external model was invoked.
- No GitHub object was mutated.
- No package was uploaded.
- The candidate bundle and artefact hashes permit later integrity checking.

## Required external security work

1. Re-run locked dependency audit with current vulnerability data.
2. Execute native Windows workspace-boundary tests.
3. Review any approved model endpoint and data retention before enabling weekly digest.
4. Run remote CodeQL and protected CI.
5. Conduct bounded intrusive testing before any production-network use.
