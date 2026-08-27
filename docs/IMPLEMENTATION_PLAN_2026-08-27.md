# Regula recovery, release and validity implementation plan

Date: 27 August 2026

Evidence baseline: commit `d89de32117611c80de7c876c4b60e6a96e5de345`,
tree `06b3b313e544e14c803479263423c7373a90d0f6`.

Regula reports code-observable indicators for human review. It does not decide
legal applicability, legal classification, conformity or compliance. A clean
result is not clearance.

## Evidence established on 27 August 2026

- [Observed] `getregula.com` resolved to GitHub Pages and returned GitHub's
  site-not-found response. The repository Pages API also returned 404.
- [Observed] `getregula.netlify.app` and the latest reviewed Netlify deploy
  preview returned the expected site. The repository has a Netlify publish
  configuration, while its Pages workflow is manual-only.
- [Inferred] The outage is a split-host configuration defect: DNS points to a
  Pages service that is not enabled while the Netlify deployment works.
- [Observed] the PyPI JSON endpoint for `regula-ai` returned 404, while its
  simple-index endpoint returned an active but empty project record.
- [Unverified] Public endpoints do not establish which authenticated account
  controls the PyPI project.
- [Observed] GitHub has no public tag or release. A stale local-only `v2.0.0`
  tag points outside the current sanitised public lineage and must never enter
  a tag push.
- [Observed] public remote `main` is a five-commit sanitised lineage with one
  protected branch and no public tags.
- [Observed] GitHub advertises 66 historical pull-request head refs. An
  isolated scan found 2,444 commits outside sanitised `main`, 9,935 unique
  path/blob pairs and 486 unique privacy-rule/path combinations. At least one
  affected historical commit is reachable from 64 of the 66 pull-request refs.
- [Inferred] Some credential-shaped results are deliberately hostile test
  fixtures, but the personal-identity, machine-path and private-record results
  establish a material privacy exposure independently of those fixtures.
- [Unverified] Other clones, forks and external archives remain outside this
  enumeration.
- [Observed] default scanning of the committed synthetic corpus detects 4 of
  30 high-risk-labelled fixtures and 5 of 5 prohibited-labelled fixtures.
  The movement from 10 of 30 is attributable to default opt-in gates for
  biometric and financial categories, not to a corpus change.
- [Observed] the complete local verification chain passed at the baseline:
  1,453 custom assertions passed with 8 skips; pytest reported 2,884 passed and
  38 skipped; self-test passed 6 of 6; doctor reported 9 passes and 3
  informational notices.

Synthetic label fidelity is a regression diagnostic. It is not real-world
precision, recall, legal validity or efficacy.

## Implementation record at the candidate working tree

- [Observed] the current release workflow now rejects lightweight,
  GitHub-unverified and non-current-main tags before build. A separately tested
  publication-status gate blocks release while naming, PyPI control and
  historical-ref conditions remain false.
- [Observed] a fresh reachable-ref auditor reproduced the historical exposure
  without printing matched values. It remains a finding, not a completed
  remediation.
- [Observed] the locked all-extras audit found one advisory,
  `PYSEC-2026-3412`, in WeasyPrint 68.1 and no fixed release. The affected
  option is not passed, HTML fallback remains available and nothing is
  suppressed.
- [Observed] the decision-model mutation control reconciled 136 mutants: 136
  killed, 0 survived, 0 invalid and 0 timed out. Equivalent mutants were not
  assessed. This is assertion-sensitivity evidence for two declared operators,
  not detector-validity evidence.
- [Observed] the unchanged pinned external corpus reran across 13 repositories,
  18 variants and 36 isolated repetitions. All 18 variants were byte-repeatable
  and 11 of 13 preregistered assertions passed. The same two adverse probes
  remain.
- [Observed] the canonical facts generator and sanctioned cascade report every
  declared test, test-file, custom-runner and command-count surface in sync.
  Exact current values remain single-sourced in `data/site_facts.json`.
- [Observed] local real-browser checks exercised successful and unanswered
  questionnaire paths at 390 × 844 and 1440 × 1000. The result moves focus to
  its heading; the error moves focus to the first unanswered radio group.
  Representative human comprehension and assistive-technology evidence remain
  absent.
- [Observed] the owner-gated, reversible Netlify recovery procedure is now
  recorded in `docs/operations/WEBSITE_RECOVERY_RUNBOOK.md`. No DNS, hosting or
  deployment state was changed by this implementation.

## Workstream 1: evidence and privacy preflight

Objective: maintain a public-safe register and prove which Git references are
reachable before any restoration or release.

1. Reconcile every historical open or partial identifier into
   `docs/OPEN_ITEMS_2026-08-27.md` using current evidence.
2. Enumerate live GitHub branches, tags, releases and pull-request refs.
3. Run `scripts/public_repo_guard.py` over the current tracked tree and every
   proposed public file.
4. Use a fresh clone of remote `main` for release preparation. Fetch and push
   named refs only. Never use `git push --tags`.
5. Do not attempt another ordinary force-push rewrite: the affected refs are
   GitHub-managed pull-request refs. Prepare a GitHub Support request that
   enumerates the affected refs and rule classes without reproducing matched
   values. Ask for removal of cached views and affected pull-request refs under
   GitHub's sensitive-data process.
6. Rotate any live credential whose value is confirmed as real during a
   restricted review. Credential-shaped synthetic fixtures are not evidence of
   a live credential and must be classified separately.

Completion evidence: zero current-tree privacy findings, an enumerated live-ref
record, GitHub Support confirmation for affected pull-request refs and a fresh
release workspace with no stale local tag.

## Workstream 2: restore the website through Netlify

Objective: end the outage using the already functioning deployment without
publishing a package or widening product claims.

Human approval and authenticated platform access are required. Before changing
DNS, confirm the exact Netlify project, deployment identifier, custom-domain
ownership and project-specific DNS values. Record existing DNS so it can be
restored. Then configure the apex and `www`, HTTPS and the canonical redirect.

Verify with two DNS resolvers and public HTTP requests. In a real browser,
exercise the home page, assessment, trust and installation pages, all three
locales, an invalid route, keyboard operation and representative mobile and
desktop layouts. No page may imply that PyPI installation currently works.

Rollback is restoration of the recorded DNS values or publication of the
previous successful atomic Netlify deployment.

## Workstream 3: review the three local commits

Objective: put the audit changes through protected remote review at the exact
commit that will be merged.

Push only the named audit branch. Require privacy, complete CI, site-integrity,
accessibility, security and release-preflight checks. The pull request must
state the synthetic default movement from 10 of 30 to 4 of 30 and its cause.
Human approval is required for merge. Repeat the mandatory local chain after
any conflict resolution.

## Workstream 4: decide the durable name

Objective: settle product and package identity before creating an immutable
tag or package release.

Website restoration under the existing domain may proceed first. A concise
decision record must compare retaining Regula and `regula-ai` with a complete
rename, including CLI compatibility, redirects and package migration. Missing
Search Console evidence must be recorded as uncertainty, not used to delay the
decision indefinitely. A signed decision is required before Workstream 5.

## Workstream 5: controlled 2.0.0 release

Objective: publish only artefacts built once from an exact reviewed commit.

This workstream is blocked until GitHub confirms disposition of the affected
historical pull-request refs. The current source tree can be built and tested,
but renewed public package distribution would amplify a repository whose
historical privacy incident remains reachable.

1. Confirm authenticated control of `regula-ai`. If it is absent, stop and use
   the PyPI support process.
2. Configure one minimal PyPI Trusted Publisher for a dedicated release
   workflow and a protected `pypi` environment with manual approval.
3. Require remote CI at the release commit. Build wheel and source archive
   once, inspect their contents, run the distribution privacy guard and install
   each into a fresh environment for verification.
4. Create a fresh signed `v2.0.0` tag at that commit. Never reuse or push the
   stale local tag.
5. Publish through short-lived OIDC credentials. Retain PyPI's distribution
   attestations, checksums and provenance.
6. Run public installation, metadata, CLI, documentation-link and website
   smoke tests.

A defective immutable package version is yanked and replaced by a higher
version. It is not deleted and reused.

## Workstream 6: independent validity and human evidence

Objective: test whether Regula's observations are useful for their stated
review purpose before widening any performance claim.

1. Freeze a licence-compatible, project-held-out corpus, codebook, ruleset,
   configuration, primary outcomes and exclusions before scanning.
2. Use at least three blinded qualified raters for the shared reliability set.
   Retain `uncertain` and `not_assessable`, every original rating and a separate
   adjudication record.
3. Report integer confusion counts before metrics, confidence intervals,
   agreement, missingness, language and rule-family strata, abstention coverage
   and all deviations.
4. Only after the frozen baseline, improve biometric, financial, TypeScript and
   other error families on training data and evaluate once on held-out data.
5. Run moderated comprehension sessions covering clean, severe, unknown,
   incomplete and error journeys with representative developers and governance
   reviewers.
6. Complete the manual WCAG 2.2 AA matrix with proficient assistive-technology
   users. Automated axe output remains mechanical evidence only.

No accuracy, recall, certification or legal-correctness claim may widen before
independent evidence supports its exact wording.

## Workstream 7: engineering and UX debt

- Keep two-worker xdist over the unchanged complete collection on supported
  Python versions and retain one sequential order/shared-state audit. Required
  gates must not use change-based test selection.
- Re-run the locked all-extras dependency audit. If the WeasyPrint advisory
  still lacks a fixed release and the affected feature remains unused, retain
  HTML fallback, document the exposure and monitor upstream without
  suppression.
- Update the Article 6 guidance record only from a final primary Commission
  publication. Otherwise retain the dated draft-status caveat.
- Treat 4 of 30 as a product-policy and validity question. Do not reverse gates
  merely to improve the synthetic fraction.
- Generate the three assessment locale engines from one tested decision model
  after validity work stabilises scoring. Preserve translated presentation and
  test parity for EN, DE and PT-BR.
- [Observed] the fresh complete axe run covered 54 canonical pages at two
  viewports: 108 runs, zero detected violations, 71 incomplete colour-contrast
  results and 516 retained nodes. Complete manual review rather than
  allowlisting those incomplete nodes.
- Delete public artefacts only when an enumerating predicate proves they are
  superseded, unreferenced and unnecessary. Age alone is not a deletion rule.

## Final verification

Before declaring an implementation complete, run:

```bash
python3 tests/test_classification.py
python3 -m pytest tests/ -q
python3 -m scripts.cli self-test
python3 -m scripts.cli doctor
```

Record every exit code and the exact commit and tree. Verify the public tree and
built distributions with the privacy guards. Inspect important site states in
a real browser at mobile and desktop sizes. Human usability and assistive-
technology validation remain outstanding until representative people complete
them.
