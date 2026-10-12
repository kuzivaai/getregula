# Candidate integration and provenance

Date: 30 August 2026

## Finding

OBSERVED: Regula now has a coherent local candidate commit, but the original working tree remains materially dirty and the complete pytest chain is BLOCKED by this session's loopback-socket restriction. The candidate is suitable for local code review. It is not a release or production artefact.

## Source and starting state

- Repository root: `/home/USER/getregula`
- Starting branch: `feat/site-ux-redesign-2026-08-27`
- Starting HEAD: `fbed8f3baf81f0c5f0860ebaf56a2845b632b547`
- Starting tracked state: 150 modified files, zero staged files, zero tracked deletions, and 33 untracked files.
- Starting tracked diff: 5,613 insertions and 2,397 deletions.
- Remotes: GitHub fetch remote; deliberately disabled `no-push` push remote.
- Relevant local tag: `v2.0.0` resolves to `0b2b1642cf5b7e8786a1a5dcba93f7b75e170ccd`, not the candidate.

REPRODUCED: before integration, the dirty tree was preserved as:

- `getregula-pre-candidate-2026-08-30.patch`, SHA-256 `7394ce642a981dd3297abca5db632f6b7fca1807c4c36a21fed5fb20de09a16e`.
- `getregula-pre-candidate-new-files-2026-08-30.tar.gz`, SHA-256 `bb216611560ef4be7fc624fe1f563f6cd6e2d1e05767e473dd3371c79d890a32`.

No pre-existing file was discarded, stashed or reset.

At final read-back, the original repository still had the same 150 tracked
modifications and the same tracked diff statistics, 5,613 insertions and 2,397
deletions, with no staged change. The untracked-file count was 48 rather than
the starting 33 because this validation package added 15 untracked artefacts.
The candidate clone itself was clean at the final commit.

## Candidate identity

- Branch: `candidate/remediation-2026-08-30`
- Commit: `3b6ca1f7e483ff35838a814c043e6b0361a2d55a`
- Commit scope relative to the starting HEAD: 235 files, 8,693 insertions and 3,055 deletions.
- Local clone: ignored `output/candidate-remediation-2026-08-30/` in the original repository.
- Recoverable bundle: `regula-candidate-3b6ca1f7-2026-08-30.bundle`.
- Bundle SHA-256: `3292e366e909e74a259b0a7636ad91f8abde5f25b0696e7eeb1a57af0eb43660`.

BLOCKED: the original repository's `.git` directory was read-only in this session, including after approval, so the candidate branch could not be registered directly there. The ignored clone and verified complete-history bundle preserve the same commit without touching the dirty working tree.

## Built artefacts

- Source distribution: `regula_ai-2.0.0.tar.gz`, SHA-256 `d272eeda38cba7ce179e663b860add30fe2be96c5224c0605b094dde158f133c`.
- Wheel: `regula_ai-2.0.0-py3-none-any.whl`, SHA-256 `4862f4653c287429dfdad522b8ab3886e1915b0010769f7d64c8bb0a33040741`.
- Build backend: setuptools 83.0.0 from a local cached wheel.
- Build dependency floor corrected from setuptools 68 to 77 because authoritative setuptools documentation states that SPDX licence strings and `project.license-files` require version 77 or later.

REPRODUCED: each artefact installed with `--no-index --no-deps` into a separate clean Python 3.12 environment. The source distribution used local setuptools 83.0.0 through `--no-build-isolation`; no package was downloaded. The installed-artefact verifier reconciled 181 RECORD files, 100 modules, 15 required data files, eight conformance items, 179 scanned files and four executed CLI transcripts with zero findings for each installation.

## Five reported implementation files

### `benchmarks/rating_packet.py`

- Purpose: one versioned rating-packet schema and canonical item identifier for evaluation utilities.
- Callers: `benchmarks/annotation_stats.py` and `benchmarks/compute_kappa.py`.
- Packaging: deliberately excluded because benchmarks are not installed product code.
- Production path: evaluation tooling only; integration tests exercise both consumers.
- Duplication decision: retained because it replaces separate packet parsing and identifier conventions.

### `scripts/evidence_review.py`

- Purpose: central evidence record for observations, provenance, unknowns, contradictions, reviewer questions and an empty human-decision field.
- Callers: decision adapters and report/evidence generators.
- Packaging: included because installed CLI paths import it.
- Production path: reached through CLI, report, REST and MCP contract tests.
- Duplication decision: retained as the smallest shared semantic boundary rather than extending a legal-decision model.

### `tools/weekly_digest.py`

- Purpose: validate and render a review-only digest from untrusted issue data.
- Callers: `.github/workflows/weekly-digest.yaml` and `tests/test_weekly_digest.py`.
- Packaging: deliberately excluded. The original reported `scripts/weekly_digest.py` location would have shipped workflow-only model tooling in the product wheel, so it was moved to `tools/`.
- Production path: the workflow's exact helper and main path are tested.
- Duplication decision: retained because no existing bounded schema renderer handled this trust boundary.

### `tests/test_product_boundary_contract.py`

- Purpose: cross-renderer regression contract for CLI, JSON, HTML, PDF fallback, SARIF, evidence and scaffold outputs.
- Caller: pytest and the custom test runner through the repository's required binding.
- Packaging: tests are excluded from the wheel.
- Production path: assertions invoke real adapters and generators rather than copied strings.
- Duplication decision: retained because per-renderer tests did not prove semantic agreement.

### `tests/test_weekly_digest.py`

- Purpose: negative tests for schema rejection, untrusted input, least privilege and absence of commit, push, publication or issue-writing authority.
- Caller: pytest and custom-runner binding.
- Packaging: excluded from the wheel.
- Production path: invokes `tools/weekly_digest.py` and inspects the active workflow.
- Duplication decision: retained because no prior test reached this model boundary.

## Public schema versions

- Public review schema: 2.0.
- Evidence record schema: 1.0.
- Assessment share schema: 4.
- Rating packet schema: 1.0.
- Cache schema: v8 plus Regula version and scanner fingerprint.
- Supported-surface manifest schema: 1.

## Preserved limitations

- The candidate does not prove representative detector validity.
- Native Windows workspace containment was not executed.
- Browser, keyboard, screen-reader, zoom, reflow and print review were blocked by the environment.
- Fluent and qualified review of consequential German and Brazilian Portuguese wording remains external.
- No push, tag move, release, publication or deployment occurred.
