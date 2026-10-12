# Final verification log

Date: 30 August 2026

Candidate commit: `3b6ca1f7e483ff35838a814c043e6b0361a2d55a`

Environment: WSL2 Linux 6.6.87.2, Python 3.12.3, Node 24.3.0, Git 2.43.0. The candidate clone was clean after the final commit. No source file changed between the complete Python and JavaScript runs and the commit. Package build and installed-artefact checks ran after the commit.

## Controlling result

BLOCKED: the complete pytest command did not pass because this managed session refused creation of an IPv4 loopback socket for eight RFC 3161 fixture setups. The result was 2,956 passed, 38 skipped, and 8 setup errors in 399.74 seconds. Every error originated at `HTTPServer(("127.0.0.1", 0), ...)` with `PermissionError: [Errno 1] Operation not permitted` in `tests/test_manifest_timestamp.py`.

No assertion failed in that run. This is an environment block, not a pass and not evidence that the eight behaviours work.

## Complete and focused checks

- `python3 tests/test_classification.py`: PASS, 1,465 passed, 0 failed, 8 skipped, 1,349 runner functions.
- `python3 -m pytest tests/ -q`: BLOCKED, 2,956 passed, 38 skipped, 8 loopback setup errors.
- Focused product-boundary, registry, register, gap and documentation run: PASS, 139 tests.
- Affected integration, site, locale and transcript run: PASS, 357 tests.
- `node tests/test_scanner_js.js`: PASS, 130 of 130. Runtime parity 38 of 38 fixtures. Label fidelity was prohibited 5 of 5, high-risk 18 of 30, negatives 3 of 3. This is synthetic label fidelity, not representative validity.
- `node tests/test_questionnaire_scoring.js`: PASS, 255 of 255 assertions.
- `node tests/test_decision_conformance.js`: PASS, 160 of 160 reconciled vectors.
- `python3 -m scripts.cli self-test`: PASS, 6 of 6.
- `REGULA_AUDIT_DIR=<writable temporary directory> python3 -m scripts.cli doctor`: PASS, 9 passed and 3 information items.
- Default doctor path: environment failure because `/home/USER/.regula/audit` was not writable in this managed session.

## Product, site and source controls

- `python3 scripts/determination_guard.py --control`: PASS, 39 prohibited examples detected and 22 qualified examples accepted.
- `python3 scripts/determination_guard.py --check`: PASS, 539 tracked files of 762 scanned, 0 findings.
- `python3 scripts/claim_auditor.py --verify-facts`: PASS, 269 fact references across 17 files.
- `python3 scripts/site_integrity.py`: PASS with two declared exemptions, five generator round trips, 1,609 internal references and zero dead links.
- `python3 scripts/build_llms_full.py --check`: PASS.
- `python3 scripts/cascade_count.py --check`: PASS, 3,002 pytest-collected tests, 1,349 runner functions, 120 test files and 62 commands on 12 manifest surfaces.
- `git diff --check`: PASS before commit.
- Changed-file Ruff check with the repository's E402 convention: PASS.
- Unfiltered Ruff over scripts and tests: FAIL on two intentional constructs in `tests/fixtures/sample_high_risk/app.py`, one unused import and one unused assignment.
- `python3 -m compileall -q scripts benchmarks`: PASS.
- Bandit high-severity threshold: PASS.
- Unfiltered Bandit: 97 low-severity findings, zero medium and zero high. Findings primarily concern subprocess use and non-cryptographic randomness. No finding was suppressed to obtain the controlling result.

## Release and publication controls

- `python3 scripts/release_gate.py`: PASS. Previous release v1.9.0; target 2.0.0; required and actual bump both major.
- `python3 scripts/publication_gate.py`: BLOCKED as designed. Unmet conditions: durable name decision, fresh reachable privacy audit, historical pull-request reference remediation, and verified PyPI control.
- Locked dependency export: PASS.
- Current vulnerability lookup: BLOCKED by DNS, including after approved escalation.

## Package build and clean installation

Build command used local setuptools 83.0.0 and no network:

`python -m build --no-isolation`

- Source distribution: `regula_ai-2.0.0.tar.gz`, 1,658,422 bytes, SHA-256 `d272eeda38cba7ce179e663b860add30fe2be96c5224c0605b094dde158f133c`.
- Wheel: `regula_ai-2.0.0-py3-none-any.whl`, 1,270,076 bytes, SHA-256 `4862f4653c287429dfdad522b8ab3886e1915b0010769f7d64c8bb0a33040741`.
- Wheel installation: PASS with `--no-index --no-deps` in a new virtual environment.
- Source-distribution installation: PASS with `--no-index --no-deps --no-build-isolation` in a separate new virtual environment, using the already installed local build backend.
- Installed wheel verifier: PASS, zero findings across 181 RECORD files, 100 modules, 15 required data files, 8 conformance items, 179 claim-scanned files, 1 console script and 4 command transcripts.
- Installed source-distribution verifier: PASS with the same reconciled counts.

## Candidate recovery artefacts

- Complete-history bundle: `regula-candidate-3b6ca1f7-2026-08-30.bundle`.
- Bundle SHA-256: `3292e366e909e74a259b0a7636ad91f8abde5f25b0696e7eeb1a57af0eb43660`.
- `git bundle verify`: PASS, complete history and candidate branch recorded.

Post-commit read-back in the durable clone reran the 61-case determination
control, tracked-tree determination scan, public fact audit, site integrity,
release gate, CLI self-test and doctor against the exact candidate SHA. All
seven commands passed within their declared scope, and the clone remained
clean.

## Checks not completed

- Browser rendering, keyboard traversal, zoom, reflow, print and accessibility automation: BLOCKED by socket and Chromium sandbox restrictions.
- LibreOffice PDF rendering of the consolidated DOCX: BLOCKED. The wrapper and the documented isolated-profile fallback both exited without producing a PDF. DOCX ZIP integrity and Pandoc full-text read-back passed, so the file is structurally verified but not visually verified in this environment.
- Native Windows MCP path, junction and case-folding tests: not run.
- Remote CI, CodeQL, branch protection and registry ownership checks: not run.
- Representative human rating and adjudication: not run.
