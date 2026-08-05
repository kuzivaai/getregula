# Regula Stage A activation-readiness session

Date: 2026-08-05
Time: 143401
Repository: /home/mkuziva/getregula

Objectives:
1. Close the count-literal collision defect class.
2. Correct the pseudonymisation and transaction-linkage architecture.
3. Issue an owner GO/HOLD decision without external contact.

VENTURE_DECISION: STOP
PRODUCT_PILOT_STATUS: NOT_APPROVED
EXTERNAL_CONTACT: NOT_AUTHORISED
REAL_DATA_COLLECTION: DISABLED
PRODUCT_BUILD: STOP

## Authority and initial state

- Session opened: `2026-08-05T14:34:01+01:00`.
- Workspace: `/home/mkuziva/getregula`; workspace-write sandbox; restricted
  network; unrestricted local verification available by approval.
- Exact escalated `.git` probe: `git_dir_writable=yes`, exit 0.
- Initial HEAD: `ac9e01be50fa589fa136875897643c9cd9557d0f`.
- Initial tree: `de4cd0fc15213d3f49327b80c872e6645681316c`.
- Initial worktree: clean. Concurrent-writer risk was checked; no other Regula
  writer was identified. Two read-only adversarial reviewers were available.

## Unsettled-claim reproduction

- `c11a831^{commit}` existed; its tree was reproduced from Git.
- The focused published-count test failed at both pre-implementation HEAD
  `ac9e01b` and untouched starting commit `ba673b2`. In both cases the decisive
  collision was
  `docs/venture/validation-readiness-2026-08-05/08-EVIDENCE-RECONCILIATION.md`.
- The prior launch-pack commit did not introduce that collision.
- The readiness validator reported all 29 required files present and consistent.
- The direct-transaction schema held two synthetic examples and no real record.
- Repository searches found no later H1 reopening, H2 creation, contact
  authorisation, or real participant/contact/transaction data.

## Count-record controls

Fail-before command:

```console
$ python3 -m pytest tests/test_published_count_manifest.py -q
ERROR collecting tests/test_published_count_manifest.py
ModuleNotFoundError: No module named 'count_record_policy'
[exit 2]
```

The first class implementation committed as `bd189da`. Adversarial review then
identified suffix-only discovery, unverified Git provenance, silent read errors,
decoded-text hashing and a separate vacuity oracle. The corrected implementation:

- scans every tracked readable text file, independent of suffix;
- fails on Git discovery and tracked-file read errors;
- hashes raw bytes;
- permits only centrally registered exact-path `dated_evidence` records;
- requires the capture date in the path;
- verifies commit existence, path-at-commit and historical blob hash;
- rejects current/generated surfaces as historical;
- retains broad-exclusion, rename, missing-file, stale-current and Git-failure
  negative controls.

Corrected focused result: 21 passed, exit 0. Revert control changed the broad
exclusion rejection to a no-op; the intended test failed, exit 1; the fix was
restored and the focused result returned to exit 0.

Implementation commit: `95caef48fa486167632276bf5e910f24988ecb14`.
Implementation tree: `552752881d4417a616bee70595ee6f72049c9ea7`.

## Research data architecture

Future Stage A records are `PSEUDONYMISED`, not anonymous. The design separates:

1. contact and participation register, never in Git;
2. separately permissioned transaction-linkage register with random tokens;
3. pseudonymised analytical corpus, with no identity/contact mapping.

The threat model covers singling out, rare combinations, deterministic-hash
attacks, insider access, Git/log/backup leakage, linkage-table disclosure,
false matches, counterpart inference, small cells, quotations, cross-session
inference and linked withdrawal. The current JSON schema is synthetic-only; a
future real schema must constrain bands/free text and small-cell output before
collection. The H2 corpus validator remains deliberately deferred.

Owner-approved Stage A defaults are GBP 0 and prohibitions on recording,
transcription, confidential documents, private repositories, code, security
findings, special-category data, incentives, Regula demonstration, sales,
publication and real data in Git. Controller, purpose, research lead, storage,
processors, access, retention/deletion, privacy ownership, lawful basis, work
permission and separate contact authorisation remain blocking.

## Adversarial reviews

Reviewer A initially found the five count-policy defects described above. After
correction it reported no remaining material implementation defect; focused
result 21 passed, exit 0. Residual scope: NUL/non-UTF-8 files are treated as
binary and are not semantically scanned.

Reviewer B initially found transcript-dependent retention wording despite the
Stage A transcription prohibition, and prose-only future schema constraints.
After correction it reported no remaining material defect. Retention,
aggregation boundary and storage remain owner/professional gates.

Reviewer A final finding (verbatim):

> No remaining material implementation defect. The corrected focused test
> passes: `21 passed`, exit 0. N70 must remain open because the corrections are
> uncommitted and the exact committed full suite has not yet passed. Therefore
> the public “2,702 all passing/all green” claim remains unverified for now.

Reviewer B final finding (verbatim):

> No remaining material defect. The transcript-dependent triggers now use
> note-review or participation-close events, and the future-schema limitations
> are explicitly acknowledged and gated before real collection. Remaining
> retention, aggregation, and storage decisions are correctly left for owner
> and professional review.

## Exact final verification

The custom runner on the clean detached implementation tree completed with
1,378 passed, 0 failed, 4 skipped, exit 0. Full output is retained in the
committed compressed evidence attachment named in the handover.

The first restricted pytest attempt was interrupted at 77 percent by an
orchestration-cell loss and is not evidence. A clean restricted rerun completed
with 2 failures, 2,663 passes, 34 skips and 8 errors: localhost mock TSA sockets
were denied and MCP fixture paths in the detached `/tmp` worktree were rejected.
An unrestricted detached rerun removed all socket errors but retained the two
canonical-root MCP path rejections: 2 failures, 2,671 passes, 34 skips.

The controlling unrestricted run used the canonical repository path at the
same exact commit/tree. It completed with two thousand seven hundred seven
passes, no failures or skips, exit 0, in 24 minutes 6 seconds. Pre/post status
contained only this session log as untracked; no tracked file changed.

Additional commands and outcomes:

- `python3 -m scripts.cli self-test`: 6/6 passed, exit 0.
- `python3 -m scripts.cli doctor`: 8 passed, 4 informational, exit 0.
- configured Ruff command from CI: passed, exit 0.
- intentionally over-broad Ruff sweep: 53 undefined names in synthetic
  fixtures; abandoned because CI explicitly excludes those fixtures.
- CI HTML parser: 56 files, 0 failures, exit 0.
- security self-check: 19 known acceptable, 0 unexpected, exit 0.
- claim facts, site integrity, count cascade, recall artefact, gap demo and
  self-reference controls: each exit 0.
- merge blocker: zero active-delivery findings, exit 0; historical tree-guard
  debt remains printed and was not suppressed.

Compressed raw evidence SHA-256:

```text
72db89c40dd493cb4655a1d192be66efd5304f3ca98428cfdef7d831d408d0ef  custom-runner.log.gz
2d2ad3ffdfc974104b908b744c169a17af6c2ddd1e1834cbfed949f1b19efad4  pytest-canonical-unrestricted.log.gz
622d61d3f1b6cfc3ff422f3381943860f116b248eddd29b5cdf04cbb567e211f  pytest-detached-unrestricted.log.gz
174fa82d18dba74e3c6720371ec4e34ee8c59c10929a99974694e24c873371d2  pytest-restricted.log.gz
```

## Final decision

The count collision class is closed and the repository suite is green at the
implementation commit. The research data architecture is honestly classified
and designed, but Stage A remains `HOLD`: controller, storage, lawful basis and
interviewer work-permission decisions are unresolved. External contact remains
not authorised and real-data collection remains disabled.

## Authority and environment

Start time: `2026-08-05T14:34:01+01:00`.

Working directory and workspace root: `/home/mkuziva/getregula`. Sandbox: workspace-write with restricted network. Git and repository writes are authorised for this unit; the exact escalated probe returned `git_dir_writable=yes`. Subagent review is available. No active test or repository-writing process was identified; existing detached worktrees are treated as read-only concurrent-state risk. Initial HEAD: `ac9e01be50fa589fa136875897643c9cd9557d0f`; tree: `de4cd0fc15213d3f49327b80c872e6645681316c`; branch: `audit/regulatory-current-2026-08-04`; 15 commits ahead of `origin/main`; initial tree clean.
