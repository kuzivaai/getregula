# Independent remediation validation

Date: 30 August 2026

## Conclusion

The candidate materially improves the product boundary, cache correctness, share-state preservation and local trust boundaries. It does not establish detector validity, legal accuracy, accessibility conformance, public-release integrity or production readiness.

## Major dispositions

### Public review schema 2.0: CONFIRMED

OBSERVED: `scripts/decision_adapters.py` defines public schema 2.0 and emits observations, declared facts, missing facts, contradictions, references, reviewer questions, suggested steps, limitations and an empty human-decision field.

REPRODUCED: decision conformance passed 160 of 160 vectors. Product-boundary tests reach CLI, REST, MCP, report and scaffold adapters.

Limitation: downstream consumers of legacy public fields need migration.

### Removal of legacy public outcome fields: PARTIALLY CONFIRMED

REPRODUCED: supported-output tests reject `result_type`, `rule_resolution`, `indications`, `obligations`, `outside_scope_basis` and `decision_trace` in public schema 2.0 records.

OBSERVED: some names remain inside older internal decision machinery and historical material. Their continued containment depends on the adapter boundary and inventory.

### Generated-output product boundary: CONFIRMED within the inventoried surfaces

REPRODUCED: the determination guard scanned 539 tracked files of 762 with zero findings. Its bidirectional control detected 39 planted prohibited examples and accepted 22 legitimate qualified examples. Installed artefacts passed the same claim scan.

Limitation: a semantic guard is regression evidence, not qualified legal review.

### Cache schema v8: CONFIRMED

REPRODUCED: cold A/B, warm A then B, warm B then A, policy, threshold, domain, parser, path-context, corruption, concurrent writer, eviction and disabled-persistence tests pass. Mutating a behaviour-changing key input changes identity.

Limitation: native Windows concurrency and filesystem semantics were not executed.

### Assessment-sharing schema 4: CONFIRMED at the JavaScript contract layer

REPRODUCED: complete, partial, missing, explicitly unsure, contradiction, early-exit, locale, legacy, malformed, unsupported-version and round-trip cases pass within the 255-assertion questionnaire suite. Extra-answer smuggling is rejected.

BLOCKED: browser-rendered recovery and assistive-technology announcements could not be exercised.

### MCP workspace containment: PARTIALLY CONFIRMED

REPRODUCED: explicit root, resolved containment, traversal, symlink escape, sensitive-path, oversized-input, file-count, byte-count, temporary-workspace and audit-privacy tests pass.

BLOCKED: native Windows execution.

### REST network acknowledgement: PARTIALLY CONFIRMED

REPRODUCED: loopback defaults, accidental non-loopback refusal, explicit unsafe acknowledgement, limits, nesting, path containment, concurrency bounds and error disclosure tests pass.

BLOCKED: the session cannot open a loopback socket for the final RFC 3161/browser chain. The REST server remains experimental and unauthenticated.

### Feedback preview and consent: CONFIRMED in bounded tests

REPRODUCED: exact outbound preview precedes action; local paths, bearer tokens, assignment-shaped secrets, email-shaped identifiers and private-key material are minimised or redacted; cancellation performs no external action.

No browser or network action was triggered during validation.

### Weekly-digest authority and data flow: CONFIRMED

OBSERVED: workflow permissions are read-only, checkout credentials are not persisted, issue text is treated as untrusted data, output is schema-bound and only a review summary is produced.

REPRODUCED: tests prevent commit, push, publication and issue-writing authority.

Limitation: model endpoint privacy and output quality require separate approval and review.

### Rating-packet schema: CONFIRMED for tooling readiness

REPRODUCED: both agreement utilities accept rating packet schema 1.0; missing second ratings produce an explicit incomplete result; no rating is manufactured.

BLOCKED: two representative independent ratings and adjudication do not exist.

### Locked CI: CONFIRMED as repository configuration

OBSERVED: CI installs uv 0.11.0 and uses `uv sync --locked --extra test` across Python 3.10 to 3.13, plus a sequential Python 3.12 lane.

UNVERIFIED: remote GitHub Actions did not run in this session.

### Website generation: CONFIRMED statically

REPRODUCED: five regional generator round trips match, 1,609 internal references have zero dead links, all checked claims are sourced, 108 cross-language links are labelled, and the site integrity check passes with two declared exemptions.

BLOCKED: real-browser review and axe automation.

### Claim controls: CONFIRMED within declared scope

REPRODUCED: 269 public fact references across 17 files match canonical counts. Published transcript checks reproduce 39 CLI anchors and eight benchmark contracts across 11 surfaces.

### Installation provenance: CONFIRMED locally

REPRODUCED: exact wheel and source-distribution hashes are recorded and both clean offline installations pass installed-product verification with zero findings across eight checks.

EXTERNALLY VERIFIED: PyPI currently serves `regula-ai` 1.9.0; GitHub displays no public releases and no public tags. The candidate is not publicly distributed.

### Representative detector validity: BLOCKED

REPRODUCED: runtime parity covers 38 of 38 canonical fixtures, but high-risk label fidelity is 18 of 30. This is synthetic label fidelity, not precision, recall or real-world accuracy.

No validity result may be reported until the frozen representative protocol has two independent ratings and completed calculations.

## Adversarial challenge summary

- Staff engineering: the shared schema is bounded and has current callers. Moving weekly digest tooling out of the package removed an unnecessary authority and packaging surface.
- Product boundary: active generated outputs were scanned by structure and by semantic guard. The challenge pass removed a remaining Annex VIII path that converted detector labels into `registration_required` or legal non-applicability. Historical and internal decision names remain a maintenance risk.
- Security and privacy: least-privilege tests pass for changed boundaries. Native Windows, external model privacy and intrusive testing remain outside scope.
- Website and UX: source-level hierarchy and state contracts improved, but visual and assistive-technology conclusions are blocked.
- Testing: planted determination controls, cache-key mutations, legacy-field rejection and direct installed-product execution prevent the principal new tests from passing vacuously.
- Scope: no new jurisdiction, dashboard, autonomous agent, compliance badge or speculative commercial feature was added.
