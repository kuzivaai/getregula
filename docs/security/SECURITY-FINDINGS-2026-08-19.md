# Security findings inventory — 19 August 2026

This is a dated, ref-specific inventory. It does not claim that Regula has no
vulnerabilities. Counts from different tools are kept separate because they
measure different things.

## Scope and refs

- Starting branch: `feat/engagement-fixes`
- Audited starting head: `edeeb32a8e340a877041e528ba09b3e2105ea90d`
- Security reconciliation implementation commit: `9782a47`
- Default-branch CodeQL analysis commit:
  `2ab71d85929a8bccea8b152cbf5b5b86d14f9b49`
- Default-branch analysis id: `1643330145`, completed
  `2026-08-19T19:49:29Z`
- PR 55 merge-ref CodeQL analysis commit:
  `dbefebfaee3403145d6736c42b6c809c795f69d6`
- PR merge-ref analysis id: `1641039245`, completed
  `2026-08-19T13:10:58Z`

## Executive disposition

| Evidence source | Before this change | Current branch result | Residual |
|---|---:|---:|---|
| Bandit, `scripts/ hooks/` with project config | 14 findings: 3 low, 11 medium, 0 high | 0 findings | Project-level exclusions and narrow, documented false-positive annotations remain part of the result |
| `pip-audit`, locked all-extras export | 5 advisories in 2 packages | 1 advisory in 1 package | WeasyPrint 68.1, CVE-2026-49452 / GHSA-jhhc-3hcp-qhm5, has no fixed release in the advisory data |
| CodeQL, default branch | 43 open alerts | 43 open at merge commit `2ab71d8` | PR results are baseline-relative and did not mean the repository inventory was empty |
| CodeQL, exact PR 55 merge ref | n/a | 0 results | Means no alerts introduced relative to the base; it was incorrectly treated as a zero-inventory result before the post-merge check |
| Regula's own PR scan | 1 high-risk indicator | 1 indicator | Biometrics product-governance observation in `scripts/cli_scan.py`; not a software vulnerability |

No independent penetration test was performed. Semgrep was not re-run in this
audit, so this record makes no current Semgrep pass claim.

## Bandit inventory and remediation

The pre-change command was:

```bash
bandit -c pyproject.toml -r scripts/ hooks/ -f json
```

It reported B310 at the network fetchers in `adoption_pulse.py`,
`dev_sentiment.py`, `indexnow.py`, `refresh_dpv_vocab.py`,
`refresh_eli_vocab.py` and `verify_quotations.py`; B405/B314 in XML consumers;
and two B108 reports on denylist literals in `cli.py` and `mcp_server.py`. The
[audited starting tree](https://github.com/kuzivaai/getregula/tree/edeeb32a8e340a877041e528ba09b3e2105ea90d)
preserves those call sites, while the replacement boundaries are exercised by
[`tests/test_release_distribution_policy.py`](../../tests/test_release_distribution_policy.py).

The branch adds `scripts/safe_io.py`, which permits only exact HTTPS hosts,
rejects credentials and non-default ports, and revalidates every redirect.
XML downloads are capped at 2 MiB and DTD/entity declarations are rejected
before the standard-library parser is invoked. B108 annotations are limited to
the two path strings that are denylist values, not write destinations. The
same command then reports zero findings. This is a Bandit result, not a
penetration-test result.

## Dependency inventory

The audit exported the complete lock with every optional extra. The earlier
lock selected `cryptography==46.0.7` and `weasyprint==68.1`.

The `cryptography` floor is now 50.0.0 and the lock selects 50.0.0, removing:

- PYSEC-2026-3552 (fixed in 50.0.0);
- PYSEC-2026-3553 (fixed in 49.0.0);
- PYSEC-2026-3554 (fixed in 49.0.0); and
- GHSA-537c-gmf6-5ccf (fixed in 48.0.1).

The remaining WeasyPrint advisory concerns rendering with
`presentational_hints=True`. Regula does not enable that option, and a
regression test preserves that condition. This reduces reachability; it does
not erase the advisory. The core package still declares no required
third-party dependency, but that fact must never be used to describe the
optional all-extras environment.

## Default-branch CodeQL inventory

The GitHub API returned the following 43 open alert identifiers.

### `py/path-injection` — 37 alerts

Every current alert id is enumerated below. Rows share a disposition only where
the source, reachable input, control and residual risk are the same.

| Path | Current alert ids | PR/release-head change | Reachable input and existing boundary | Disposition | Test / residual risk |
|---|---|---|---|---|---|
| `scripts/policy_config.py` | 69, 70 | No relevant sink change | Project policy selected by the user; content reads use `read_text_if_safe` with the project root for untrusted policy | `FALSE_POSITIVE_WITH_PROOF` | Hostile-tree tests cover FIFO, size and escaping symlink refusal; a deliberately selected external `--rules`/policy path remains operator-controlled |
| `scripts/domain_scoring.py` | 68 | No relevant sink change | Joins fixed policy filenames to the selected project root; the downstream read passes that root to the shared guard | `FALSE_POSITIVE_WITH_PROOF` | Hostile policy-symlink test; project-root choice remains visible and intentional |
| `scripts/report.py` | 40, 41, 45, 60, 61, 65, 66, 84 | Alert 84 is the post-merge fingerprint replacing fixed alert 62; no new file-read primitive | The scan root is the CLI user's target or an API target already contained to the launch directory; files are opened via the descriptor-safe scan guard with size and file-type caps | `FALSE_POSITIVE_WITH_PROOF` | `tests/test_scan_safety.py`, `tests/test_hostile_sweep.py`, cache/scope regressions; Windows lacks POSIX `O_NOFOLLOW`/`fwalk`, a documented platform residual |
| `scripts/project_fingerprint.py` | 32, 33, 59, 64 | No relevant sink change | Reads fixed manifest filenames below the selected root through guarded helpers | `FALSE_POSITIVE_WITH_PROOF` | Hostile-sweep and project-fingerprint tests; user-selected root remains intentional |
| `scripts/compliance_check.py` | 23, 24, 25, 57, 58, 63 | No relevant sink change | Walks the selected project; file content is captured through `os.fwalk` descriptors and `read_text_if_safe` | `FALSE_POSITIVE_WITH_PROOF` | Compliance hostile-tree/cache tests; documented Windows ancestor-race degradation remains |
| `scripts/cross_file_flow.py` | 28, 29, 53, 54, 55, 56 | No relevant sink change | Walks the selected project; Python/JS files are read while the parent descriptor is live | `FALSE_POSITIVE_WITH_PROOF` | Cross-file hostile-tree tests; unsupported-language analysis is a product limit, not a path-boundary defect |
| `scripts/scan_safety.py` | 49, 50, 51, 52 | No relevant sink change | These are the guard's own `resolve`, `stat`, `os.open` and descriptor operations; it rejects out-of-root symlinks, non-regular files and files over the configured cap | `FALSE_POSITIVE_WITH_PROOF` | Dedicated symlink, FIFO, TOCTOU and ancestor-swap tests; documented Windows degradation remains |
| `scripts/api_server.py` | 14, 15, 16, 17, 18, 19 | Yes: `_resolve_request_target` now applies a lexical root check before `exists`/type probes, then resolves symlinks and checks again | JSON `path` is attacker-controlled on the unauthenticated local server; launch directory is the authority boundary | `FIXED_ON_RELEASE_HEAD` | New tests prove outside paths are rejected before `exists`/`is_dir`/`is_file`, non-strings fail, symlink escapes fail; running the server from a broad root deliberately grants broad scope |

Alert 62 is not silently omitted: GitHub marked it fixed at the PR 55 merge and
opened alert 84 for the post-merge flow at `scripts/report.py`. The current
population therefore remains 37 path alerts, not 38.

### Other rules — 6 alerts

| Alert | Rule and path | Disposition |
|---:|---|---|
| 71 | `py/redos`, `tests/test_security_hardening.py` | `FALSE_POSITIVE_WITH_PROOF`: deliberately executes a catastrophic regex under a CPU-time meter to prove the detector can observe the failure mode; test-only |
| 67 | `py/bad-tag-filter`, `scripts/claim_auditor.py` | `FIXED_ON_RELEASE_HEAD`: script/style closing-tag blanking now handles browser-tolerated whitespace/trailing text and preserves line count; regression added |
| 13 | `py/clear-text-logging-sensitive-data`, `tests/helpers.py` | `FALSE_POSITIVE_WITH_PROOF`: assertion helper prints a synthetic credential value assembled by character code for the credential-detector fixture; test-only, no production secret source |
| 11 | `py/polynomial-redos`, `scripts/classify_risk.py` | `FIXED_ON_RELEASE_HEAD`: repository-local regexes now require explicit `--rules`; custom regexes reject unbounded repeats, lookarounds, backreferences, quantified groups, excessive bounds and multiple variable repeats; invalid rules warn once |
| 10 | `py/redos`, `tests/test_classification.py` | `FALSE_POSITIVE_WITH_PROOF`: literal hostile pattern passed to `_compile_custom_pattern` to assert rejection; it is not compiled by the application path |
| 9 | `py/incomplete-url-substring-sanitization`, `tests/test_build_regulations.py` | `FALSE_POSITIVE_WITH_PROOF`: equality/containment assertion on generated HTML output, not URL validation or sanitisation |

## Required closure evidence

Before release:

1. run the full project gate from `AGENTS.md`;
2. rerun Bandit and the locked all-extras dependency audit;
3. push the exact release commit and require CodeQL to complete on the new PR
   merge ref;
4. after merge, require a terminal default-branch CodeQL run, recount alerts
   through the GitHub API, then use per-alert platform dispositions rather than
   a query-wide suppression; and
5. publish the residual WeasyPrint advisory with the release rather than using
   an unqualified zero-vulnerability badge or sentence.
