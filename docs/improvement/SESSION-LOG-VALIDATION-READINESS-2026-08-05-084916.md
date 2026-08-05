# Regula validation-readiness session

Date: 2026-08-05

Time: 084916 Europe/London

Repository: `/home/mkuziva/getregula`

Objective: prepare an owner-decidable validation-readiness pack without external
action and without changing Regula's commercial STOP or pilot status.

## Authority gate

Started: `2026-08-05T08:49:16+01:00`

The default sandbox probe failed with exit 73 because `.git` was mounted
read-only. The owner then explicitly authorised the minimum necessary
unrestricted Git execution for this session. The exact probe was rerun under that
approval and returned:

```console
git_dir_writable=yes
head=5256c33bdbf91a7c2a2326d9e662172ec573ccd1
tree=6ed66c1cc1f48dc195014994c9d94eb58bca5c84
## audit/regulatory-current-2026-08-04...origin/audit/regulatory-current-2026-08-04 [ahead 2]
[exit 0]
```

This matched the blocked response. The working tree was clean. Repository writes
are restricted to the requested preparation work. External contact, spending,
real-data collection, public action, ownership changes and immigration action
remain prohibited.

## Fail-before control

Command completed in under one second against HEAD `5256c33` and tree
`6ed66c1`:

```console
$ python3 scripts/validate_validation_readiness.py --allow-untracked
validation-readiness pack: FAIL (42 errors)
[exit 1]
```

The complete error set comprised the 27 absent required files, exact hypothesis
and unverified-status absence, and absent substantive controls including
abstention, adjudication, data-protection review, founder history, independent
raters, legal review, manual blinding, `NOT_ASSESSABLE`, prospective-role
classification, raw disagreements, real-data disablement and technical-label
blinding. This was a genuine missing-pack failure.

## Work package 1 reconstruction

The authoritative ledger and venture records were read completely. At HEAD
`5256c33`, their measured sizes and hashes were:

```text
LEDGER.md: 597 lines, 156173 bytes, sha256 552ff7b8c6f15e06827e0ca4e3393fe3c8c9a0654af5e46bba122f1e2d6ae747
venture dossier: 397 lines, 42575 bytes, sha256 0b07edc65101801b51b29ba2d5bfc12228a306a6118a63060697a5eb646c52a1
source register: 103 lines, 18096 bytes, sha256 4667b74f0a022f74997913554b00c825ce261049c25bc99bf646e2493f8ddc76
research protocol: 179 lines, 8376 bytes, sha256 3e7f47b3e6d035df9895e3de0355accac2fe05e64e81de09df05250446ba2682
evidence matrix: 353 lines, 25344 bytes, sha256 3612e2c2349e3faac12952a8b1fa93e8feeb3844ace7b6a12fb2ad9853ae5d3d
```

The commercial summary reproduced frozen product commit `94efa9e6`, protocol
commit `5bd2112`, Candidate A and B at 0/40 recall, transparent baselines at
40/40, and zero independently human-labelled repositories. Its verdict remains
`TECHNICAL_EVIDENCE: FAILED`, `DEMAND_EVIDENCE: UNVALIDATED` and
`OVERALL_DECISION: STOP`. The dossier retains
`PRODUCT_PILOT_STATUS: NOT_APPROVED`.

The ledger scan found 29 lines containing `OPEN` or `PARTIAL`; this is a string
match, not a count of unique live items, because some rows quote earlier statuses.
No item was closed. The prior handover omitted the ledger body and linked it
instead. This session must embed the complete current open and partial content in
the final handover.

## Primary-source pass

Current official and peer-reviewed sources were retrieved and recorded in the
pack source register. They cover ICO lawful basis, research safeguards,
international transfers and DPIAs; UKRI/ESRC ethics; the current MRS Code;
empirical-software-engineering and static-analysis evaluation methods; GitHub and
PyPI control documentation; Companies House fees; Innovator Founder rules and
endorsing bodies; and official adviser registers. Shell network remained
restricted; the read-only web connector supplied the retained sources. No model
memory was substituted for a failed retrieval.

## Adversarial review A: research, consent and legal boundary

The read-only reviewer returned these findings:

1. `MATERIAL`: retention, withdrawal-token mapping and irreversible aggregation
   cut-off were inconsistent; define the cut-off, transcript-check window and
   token-map lifetime.
2. `MATERIAL`: pre-receipt handling for confidential or unsolicited material was
   missing; require no-click/no-clone quarantine and authorised triage covering
   privilege, logs, caches, backups, return and destruction.
3. `MATERIAL`: a UK GDPR rights-request procedure was missing and must remain
   distinct from voluntary research withdrawal.
4. `MODERATE`: operational metadata, processor logs and backups were absent from
   the data categories.
5. `MODERATE`: sender disclosure authority was not a deterministic receipt gate.
6. `MODERATE`: the proposed six-year consent retention lacked support.
7. `MODERATE`: recording/transcription controls omitted human versus AI access,
   training use, diarisation, temporary copies and backups.
8. `LOW`: “UK encrypted system” described an aspiration, not an implemented
   owner storage decision.

The reviewer also confirmed that the pack separated consent from lawful basis,
did not call templates approved, preserved founder history and did not imply
immigration eligibility. All eight findings were accepted and corrected before
implementation commit; storage, lawful basis and professional review remain open.

## Adversarial review B: experimental and commercial boundary

The read-only reviewer returned these findings:

1. `HIGH`: inability to access participants is a feasibility failure, not
   falsification of customer pain.
2. `HIGH`: two-pair saturation and five-account falsification thresholds were
   arbitrary and order-sensitive; use a coverage matrix and adverse evidence.
3. `MODERATE`: “small” and the 18-month window needed operational definitions and
   limitations.
4. `MODERATE`: asking specifically about Regula output primed participants.
5. `MODERATE`: discovery cannot produce `PAID_VALIDATED`.
6. `HIGH`: the manual unit and status model needed atomic decomposition,
   precedence and fixed numerator/denominator rules.
7. `HIGH`: missed-safety outcomes require independent reference labels.
8. `MODERATE`: second-reviewer reproduction needed independence and retained
   disagreement.
9. `MODERATE`: clarification timing needed frozen pre/post states.
10. `HIGH`: `ABSENT_AFTER_REVIEW` overstated exhaustive search; use
    `NOT_FOUND_IN_FROZEN_REVIEW_SCOPE`.
11. `HIGH`: lexical and manual comparators must be separate.
12. `MODERATE`: repository representativeness was overstated; use a purposive
    exploratory population and report the approach flow.
13. `MODERATE`: the primary metric needs a frozen selection rule.
14. `MODERATE`: buyer acceptance was circular; use a non-decision-bearing artefact
    review with predeclared criteria.
15. `POSITIVE`: no platform build, demand substitution or efficacy substitution
    was hidden in the pack.

All fourteen corrective findings were accepted. The positive observation required
no change. The protocols were revised before any external action, input or result;
the revision is recorded as `VR-DEV-01` and does not change `STOP`, `NOT APPROVED`
or `HOLD`.

## Pack pass and negative controls before tracking gate

```console
$ python3 scripts/validate_validation_readiness.py --allow-untracked
validation-readiness pack: PASS (29 required files)
[exit 0]
$ python3 -m pytest tests/test_validation_readiness.py -q
2 passed in 0.71s
[exit 0]
$ python3 -m json.tool docs/venture/validation-readiness-2026-08-05/readiness.json
[exit 0]
$ git diff --check
[exit 0]
```

The mutation test covers fourteen required negative controls. Each mutation must
produce its intended validator error; the clean pack must pass. The test-count
cascade is 2,692 tests. Its check passed with existing tree-guard debt reported;
it warned, correctly, that the new test was untracked before the implementation
commit.

## Implementation commits and corrective rerun

The complete pack was frozen at `ddbea5535153462728ad09aef125f5d706dd28cd`
(tree `83255a09a0a4abd8c07d471add711248a7a2a983`). Its first full pytest run
reported 2,654 passed, 4 failed and 34 skipped. Two failures were path-specific:
MCP correctly refused fixture projects under the `/tmp` worktree. Two were real
count-cascade regressions: the live legacy-runner count remained 1,088 instead of
1,090, and a dated 2,690 measurement was incorrectly treated as a live count.

The dated measurement was preserved. The cascade coverage now explicitly treats
that named dated dossier as historical, while `docs/TRUST.md` carries the current
1,090 function count. Focused controls passed 2/2. The correction commit is
`fcebd501a1034fd5139bf337d9ba848faf0b97c4`, tree
`563876fefcfd698bd5e64d4ac8bf87c9d5172f40`. This required a third implementation
commit, exhausting the stated three-commit ceiling before the evidence-only
handover commit. Rewriting earlier commits was prohibited, so the conflict is
reported rather than hidden.

## Exact final verification

All final results below apply to commit `fcebd501a1034fd5139bf337d9ba848faf0b97c4`
and tree `563876fefcfd698bd5e64d4ac8bf87c9d5172f40` in clean detached worktree
`/home/mkuziva/getregula-validation-fcebd50`.

```text
validation-readiness validator: PASS, 29 required files
mutation/focused tests: 2 passed, 14 intended negative controls exercised
custom runner: 1,378 passed, 0 failed, 4 skipped; 1,090 functions; exit 0
pytest: 2,658 passed, 34 skipped; exit 0; 1,605.20 seconds
self-test: 6/6 passed; exit 0
doctor: 9 passed, 3 info; exit 0
ruff F821/F811: all checks passed; exit 0
HTML well-formedness: all site HTML passed; exit 0
security self-check: 19 known acceptable, 0 unexpected; exit 0
claim auditor --verify-facts: 148 references, 17 files, pass
site integrity: pass; 1,173 internal references, 0 dead; two documented warnings
cascade count: 2,692 across 11 manifest surfaces, pass
recall artefact: fresh-run match, pass
gap demo: fresh-run match, pass
self-reference control: negative and positive controls pass
claim auditor --diff-base main: 38 files, 378 claims, 0 unsourced; pass
```

The first restricted custom-runner attempt made progress but stalled and was
interrupted with exit 130. The unrestricted rerun passed. The first `/tmp`
detached-worktree pytest result was 2,654 passed, 4 failed and 34 skipped; two
failures were fixed count regressions and two were the documented MCP `/tmp`
path rejection. The final permitted-path detached run passed. No implementation
edit followed the final suite.

No formatter or type checker is configured. The repository CI config requires
the ruff check and HTML parser recorded above. A release build was not run because
this session prohibits a release and the normal CI workflow has no package-build
job; release workflow build steps are release-only.
