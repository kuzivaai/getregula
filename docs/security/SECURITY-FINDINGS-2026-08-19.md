# Security findings inventory — 19 August 2026

This is a dated, ref-specific inventory. It does not claim that Regula has no
vulnerabilities. Counts from different tools are kept separate because they
measure different things.

## Scope and refs

- Starting branch: `feat/engagement-fixes`
- Audited starting head: `edeeb32a8e340a877041e528ba09b3e2105ea90d`
- Security reconciliation implementation commit: `9782a47`
- Default-branch CodeQL analysis commit:
  `65eb5b9421ab6ab75a13c47bbf6c3aee1e6209dc`
- PR 55 merge-ref CodeQL analysis commit:
  `dbefebfaee3403145d6736c42b6c809c795f69d6`
- PR merge-ref analysis id: `1641039245`, completed
  `2026-08-19T13:10:58Z`

## Executive disposition

| Evidence source | Before this change | Current branch result | Residual |
|---|---:|---:|---|
| Bandit, `scripts/ hooks/` with project config | 14 findings: 3 low, 11 medium, 0 high | 0 findings | Project-level exclusions and narrow, documented false-positive annotations remain part of the result |
| `pip-audit`, locked all-extras export | 5 advisories in 2 packages | 1 advisory in 1 package | WeasyPrint 68.1, CVE-2026-49452 / GHSA-jhhc-3hcp-qhm5, has no fixed release in the advisory data |
| CodeQL, default branch | 43 open alerts | Still open on that ref | Must not be called closed before a fresh default-branch analysis |
| CodeQL, exact PR 55 merge ref | n/a | 0 results | Must be re-run after the security commit and again after merge |
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

| Path | Alert ids | Disposition |
|---|---|---|
| `scripts/policy_config.py` | 69, 70 | Default-branch-only pending fresh analysis; review containment tests before closure |
| `scripts/domain_scoring.py` | 68 | Same |
| `scripts/report.py` | 40, 41, 45, 60, 61, 62, 65, 66 | Same |
| `scripts/project_fingerprint.py` | 32, 33, 59, 64 | Same |
| `scripts/compliance_check.py` | 23, 24, 25, 57, 58, 63 | Same |
| `scripts/cross_file_flow.py` | 28, 29, 53, 54, 55, 56 | Same |
| `scripts/scan_safety.py` | 49, 50, 51, 52 | Same |
| `scripts/api_server.py` | 14, 15, 16, 17, 18, 19 | Same |

The scanner intentionally accepts a user-selected project root. Containment is
implemented by the safe walker, symlink/special-file rejection and API root
checks, but a green PR merge-ref alone does not prove every dataflow safe. The
alerts remain `DEFAULT_BRANCH_ONLY_PENDING_REANALYSIS`, not dismissed.

### Other rules — 6 alerts

| Alert | Rule and path | Disposition |
|---:|---|---|
| 71 | `py/redos`, `tests/test_security_hardening.py` | Test-only hostile-pattern fixture |
| 67 | `py/bad-tag-filter`, `scripts/claim_auditor.py` | Defect fixed on PR branch; pending default-branch reanalysis |
| 13 | `py/clear-text-logging-sensitive-data`, `tests/helpers.py` | Synthetic, char-code-constructed credential in a test helper |
| 11 | `py/polynomial-redos`, `scripts/classify_risk.py` | User custom-rule path; length and nested-quantifier guards exist and are tested; retained as mitigated residual |
| 10 | `py/redos`, `tests/test_classification.py` | Test that exercises ReDoS protection |
| 9 | `py/incomplete-url-substring-sanitization`, `tests/test_build_regulations.py` | HTML-output assertion, not a URL security boundary |

## Required closure evidence

Before merge or release:

1. run the full project gate from `AGENTS.md`;
2. rerun Bandit and the locked all-extras dependency audit;
3. push the exact commit and require CodeQL to complete on the new PR merge ref;
4. after merge, require a terminal default-branch CodeQL run and recount open
   alerts through the GitHub API; and
5. publish the residual WeasyPrint advisory with the release rather than using
   an unqualified zero-vulnerability badge or sentence.
