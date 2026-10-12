# Verification log

## Environment and provenance

| Command | Exit | Observed result | Limitation |
|---|---:|---|---|
| `pwd` | 0 | `/home/USER/getregula` | Path redacted for public record |
| `git branch --show-current` | 0 | `feat/site-ux-redesign-2026-08-27` | Local branch only |
| `git rev-parse HEAD` | 0 | `fbed8f3baf81f0c5f0860ebaf56a2845b632b547` | Does not identify dirty content |
| `git status --short --untracked-files=all` | 0 | 65 tracked changes and 13 untracked files | Ignored state recorded separately |
| `git diff --stat` | 0 | 65 files, 1,806 insertions, 778 deletions | Pre-existing dirty diff |
| `git diff --cached --stat` | 0 | No staged diff | None |
| sanitised remote inspection | 0 | Public fetch URL, disabled push URL | No remote network query |
| instruction-file discovery | 0 | Root `AGENTS.md`; no repository `CLAUDE.md`, `CODEX.md`, override or path-scoped agent file found | Ignored private config not read |
| audit-package inventory and reads | 0 | 14 text files plus one consolidated DOCX read | DOCX visual layout unverified |

## Product checks

| Command | Exit | Observed result | Limitation |
|---|---:|---|---|
| `python3 scripts/determination_guard.py --control` | 0 | 15 planted determinations detected; 13 legitimate statements silent | Original controls do not cover the reproduced renderer defects |
| `python3 scripts/determination_guard.py --check` | 0 | 519 tracked files scanned, 0 findings | Passing result was insufficient evidence of cross-surface safety |
| focused pre-change boundary suite | 0 | 119 passed, 1 skipped | Passed before the renderer defects were fixed |
| `python3 -m pytest tests/test_product_boundary_contract.py -q` before implementation | 1 | Four intended failures | Red-first reproduction |
| public adapter red test | 1 | Internal schema 1.0 and outcome fields escaped | Red-first reproduction |
| REST, MCP, evidence, conformity and CLI migration suite | 0 | 460 passed | Browser and public prose excluded |
| conformity and product-boundary suite | 0 | 132 passed | Full repository gate not yet run |
| focused SARIF and questionnaire compatibility checks | 0 | 8 passed | Only named functions exercised |

## Cache checks

| Command | Exit | Observed result | Limitation |
|---|---:|---|---|
| `python3 -m pytest tests/test_scan_cache.py -q` before implementation | 1 | 19 passed, 4 failed | Red run reproduced stale rules and policy; separate-process assertion also used a pre-migration JSON field |
| `python3 -m pytest tests/test_scan_cache.py -q` after configuration fix | 0 | 23 passed | Durability controls not yet added |
| `python3 -m pytest tests/test_scan_cache.py -q` after durability and process-lock tests | 0 | 29 passed | Windows lock path not executed |
| focused cache, classifier, policy, report and boundary slice | 0 | 255 passed | Full repository gate not yet run |
| `python3 -m py_compile` on changed cache and test modules | 0 | No output | Syntax compilation only |
| focused Ruff correctness rules | 0 | `All checks passed!` | Four changed Python files only |
| `git diff --check` on changed cache and test modules | 0 | No output | Whitespace check only |

## Assessment sharing checks

| Command | Exit | Observed result | Limitation |
|---|---:|---|---|
| `node tests/test_questionnaire_scoring.js` before implementation | 1 | `TypeError: adapters.decodeShare is not a function` | Red-first contract |
| `node tests/test_questionnaire_scoring.js` after implementation | 0 | 247 assertions passed, 0 failed | DOM harness, not a rendered browser |
| `node --check` on the shared adapter, flow and test | 0 | No output | Syntax only |
| focused site critical-CSS, locale-link and site-facts tests | 0 | 38 passed | Does not render pages |
| `git diff --check` on share and locale files | 0 | No output | Whitespace check only |
| loopback `python3 -m http.server` | 1 | `PermissionError: [Errno 1] Operation not permitted` | Same failure after approved escalation |
| Playwright CLI `file://` open | 1 | Browser daemon session path reported `EROFS` | Same failure after approved escalation |

## Security and privacy checks

| Command | Exit | Observed result | Limitation |
|---|---:|---|---|
| initial MCP security slice | 1 | 15 passed, 4 failed | Red run showed missing root and text limit; older denylist happened to refuse two hostile paths for the wrong reason |
| `python3 -m pytest tests/test_mcp_server.py tests/test_scan_cache.py tests/test_compliance_check.py -q` | 0 | 133 passed | Windows path semantics unexecuted |
| `python3 -m pytest tests/test_api_server.py tests/test_mcp_server.py -q` | 0 | 108 passed | Handler-level and startup tests, no listening socket |
| real CLI non-loopback invocation without acknowledgement | 2 | Refused `0.0.0.0` before bind and named missing authentication and `--unsafe-network` | Explicit unsafe bind not started because external network exposure was not authorised |
| `python3 -m pytest tests/test_telemetry.py -q` before feedback fix | 1 | 18 passed, 3 failed | Red run showed no preview, absolute path disclosure and no cancellation gate |
| `python3 -m pytest tests/test_telemetry.py -q` | 0 | 21 passed | Browser opening was mocked; no external URL opened |
| `python3 -m pytest tests/test_weekly_digest.py -q` before implementation | 2 | Collection failed because the bounded module did not exist | Red-first contract |
| `python3 -m pytest tests/test_weekly_digest.py tests/test_telemetry.py -q` | 0 | 28 passed | Model request and GitHub workflow were not executed |
| `python3 -m py_compile scripts/weekly_digest.py` | 0 | No output | Syntax only |
| `git diff --check` after security slice | 0 | No output | Whitespace only |

## Final source, site and release controls

| Command | Exit | Observed result | Limitation |
|---|---:|---|---|
| `git diff --check` | 0 | No output | Whitespace control only |
| `python3 scripts/build_gap_demo.py --check` | 0 | Generated gap demo current | No browser rendering |
| `python3 scripts/build_qualifier.py --check` | 0 | EN, DE and PT-BR generated pages current | Fluent review external |
| `python3 scripts/build_llms_full.py --check` | 0 | Generated text current | Source integrity only |
| `python3 scripts/public_surface_inventory.py --check` | 0 | Inventory current | Enumerated scope only |
| `python3 scripts/cascade_count.py --check` | 0 | 2,984 collected tests; 1,334 runner functions; 119 test files; 62 commands | Warns that two new tests are untracked |
| `python3 scripts/site_integrity.py` | 0 | Five generated pages match; 1,613 internal links; claims and version pass | Two declared hand-maintained exemptions |
| `python3 scripts/locale_link_audit.py` | 0 | 108 links across 12 pages; 0 detected defects | Not screen-reader evidence |
| `python3 scripts/determination_guard.py --control` | 0 | 25 prohibited controls detected; 18 qualified controls silent | Semantic support, not legal approval |
| `python3 scripts/determination_guard.py --check` | 0 | 519 tracked files of 738 scanned; 0 findings | Untracked files are outside this gate |
| `python3 scripts/claim_auditor.py --verify` | 0 | 117 surfaces and 269 fact references checked | Declared carrier exclusions remain |
| `node tests/test_questionnaire_scoring.js` | 0 | 254 passed, 0 failed | Bounded DOM harness |
| `python3 scripts/release_gate.py` | 0 | Required major; actual major | Local source evidence only |
| `python3 scripts/publication_gate.py` | 1 | BLOCKED on four named external controls | Gate intentionally preserved |

## Final repository gates

| Command | Exit | Observed result | Limitation |
|---|---:|---|---|
| `python3 tests/test_classification.py` | 1 | 1,463 passed, 1 failed, 8 skipped | Sole failure: two new test modules are not tracked because `.git/index` is read-only |
| `python3 -m pytest tests/ -q` | 1 | 2,935 passed, 38 skipped, 3 failed, 8 errors in 944.57 seconds | Run preceded the final migration of two stale schema assertions; one Git failure and eight loopback setup errors remain |
| focused evidence-pack and self-scan schema rerun | 0 | 2 passed in 41.63 seconds | Proves the two migrated failures only |
| `python3 -m scripts.cli self-test` | 0 | 6 of 6 passed | Built-in self-test scope |
| `python3 -m scripts.cli doctor` | 1 | 8 passed, 3 info, 1 failure | Default `/home/USER/.regula/audit` is read-only in this sandbox |
| doctor with `REGULA_AUDIT_DIR=/tmp/regula-audit-final` | 0 | 9 passed, 3 info | Environment-specific writable override |

The eight pytest errors are all `tests/test_manifest_timestamp.py` fixtures
that attempted to bind `127.0.0.1` and received `PermissionError: [Errno 1]
Operation not permitted`. The remaining product-independent pytest failure is
`test_untracked_contributors_defaults_to_asking_git`. The two other reported
failures were migrated to schema 2.0 assertions and then passed in the focused
rerun.

## Environment boundaries

- BLOCKED: local HTTP server and RFC 3161 mock server socket creation.
- BLOCKED: browser daemon state creation, reported as `EROFS`.
- BLOCKED: `.git/index` write, including an approved escalated `git add`.
- OBSERVED: default scan cache persistence under `/home/USER/.regula` is
  read-only; scans continued and emitted explicit warnings. Cache correctness
  and durability tests used writable temporary directories.

The documented chained verification command does not pass unconditionally.
No test, warning, assertion or publication condition was disabled, skipped or
weakened to claim success.

## Deliverable verification

| Check | Exit | Observed result |
|---|---:|---|
| Markdown remediation-package inventory | 0 | All required files present |
| private-path scan of remediation package | 1 | No match, which is the expected clean result |
| prohibited dash-character scan of remediation package | 1 | No match, which is the expected clean result |
| DOCX conversion | 0 | Main report written to `/mnt/c/Users/USER/Downloads/REGULA_REMEDIATION_REPORT_2026-08-30.docx` |
| DOCX size and type | 0 | 18,641 bytes; Microsoft Word 2007+ |
| DOCX archive test | 0 | Every member OK; no compressed-data error |
| DOCX Pandoc readback | 0 | Report headings and body recovered successfully |
