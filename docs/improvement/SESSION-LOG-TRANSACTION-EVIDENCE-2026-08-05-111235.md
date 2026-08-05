# Regula public transaction-evidence session

Date: 2026-08-05
Time: 111235 Europe/London
Repository: /home/mkuziva/getregula

Objective: reconcile the validation-readiness evidence and falsify or retain
the exact UK general-insurer claims-triage supplier-onboarding hypothesis.

External contact: disabled.
Real data collection: disabled.
Product build: disabled.

## Authority

Working directory: `/home/mkuziva/getregula`. Workspace write root:
`/home/mkuziva/getregula`; `/tmp` is also writable. Sandbox network is
restricted. Read-only web retrieval is available. Git writes require approved
unrestricted execution. Subagents are available; concurrent repository writes
are prohibited for their review tasks.

The default exact Git probe returned `git_dir_writable=no` and exit 73 with
`.git` read-only. The minimum escalated rerun returned:

```console
git_dir_writable=yes
## audit/regulatory-current-2026-08-04...origin/audit/regulatory-current-2026-08-04 [ahead 6]
37ebbaec1979dec6dd72573ac4829f69637bdb9b
d83bf6973e34f5b0da611896884a51b0a5792da6
[exit 0]
```

No external contact, paid service, private database or credentialed source is
authorised.

## Work-package result

Initial HEAD: `37ebbaec1979dec6dd72573ac4829f69637bdb9b`.
Initial tree: `d83bf6973e34f5b0da611896884a51b0a5792da6`.
Validation-readiness implementation: `fcebd501a1034fd5139bf337d9ba848faf0b97c4`;
tree `563876fefcfd698bd5e64d4ac8bf87c9d5172f40`.

The implementation identity, 29 tracked pack files and 23-source pack register
were demonstrated. Historical fail-before detail and the original subagent
transport remain partial. N65's corrected claim predicate is verified; N64's
wider release blockers remain open.

## Exact-tree product verification used for reconciliation

Detached worktree: `/home/mkuziva/getregula-validation-fcebd50`.

- `python3 tests/test_classification.py`: exit 0; 1,378 passed, 0 failed, 4 skipped across 1,090 functions. All skips cite absent local-development `hooks/pre_tool_use.py`.
- `python3 -m pytest tests/ -q -rs`: exit 0; 2,658 passed, 34 skipped in 857.65 seconds. Skip groups: 27 hooks-audit, 4 imported classification, 2 audit-scoping and 1 audit-surface, all for absent local hook files.
- self-test: exit 0, 6/6. Doctor: exit 0, 9 pass and 3 information results.
- validator and mutation controls: exit 0; pack PASS; two pytest functions cover 14 declared mutations.
- configured ruff F821/F811, HTML parser and security self-check: exit 0.
- six fast gates and claim diff: exit 0. Fact references 148/17; site result OK with documented warnings; count 2,692/11; recall and gap matched; self-reference controls passed; claim diff scanned 38 files/378 claims/0 unsourced.

Raw custom-runner and pytest outputs follow at the end of this log. Their SHA-256
values are `0a9c661c18df9661432f236db14b33292fe17041a9c1ef60fea99fc68fecef3d`
and `953b4b3db1c341ca4c1cd520a50225fc947885630a2a8057ab6359c648c98594`.

## Public research execution

The protocol was frozen before transaction-specific searches. Thirteen rounds
screened 231 returned results and retained 17 unique sources. Exact queries,
source classes, inclusions, exclusions and limitations are in
`docs/venture/transaction-evidence-2026-08-05/SEARCH-REGISTER.md`.

Dated sources separately establish claims-AI use and general supplier
onboarding. The current Admiral policy explicitly addresses AI-supplier due
diligence, but its exact cut-off version is unresolved. No public source joined
these into H1 or established supplier burden, budget, acceptance roles or
source-code evidence materiality. Rounds 11 to 13 added no new decision category.

## Adversarial reviews

Reviewer A initially found an invalid stopping-rule claim, incorrect result
arithmetic, incomplete deduplication, inflated vendor classes, cut-off ambiguity,
unsupported replication language and incomplete audit details. Three further
rounds were run; the total was corrected to 231; 17 unique inclusions were
mapped; vendor classes and cut-off handling were corrected; replication, access
and spend wording was bounded; deviations were recorded. Final re-review: no
remaining material blocker.

Reviewer B initially found overstrong handover evidence, an N66/N67 continuity
conflict and prior metrics presented without retained raw output. Handover
evidence was downgraded to PARTIAL; N67 was added; N66 was made historical; and
the prior 96/538, 474/463 and 45-test figures were labelled prior-record
summaries. Final re-review: no remaining material blocker.

## Current sprint verification

- `git diff --check`: exit 0.
- `python3 scripts/validate_validation_readiness.py`: exit 0, 29 required files PASS.
- Initial mistyped focused command named nonexistent test files: exit 4; no tests ran. This was corrected, not hidden.
- `python3 -m pytest tests/test_validation_readiness.py tests/test_ledger_status.py -q`: exit 0, 15 passed.
- Six fast gates: all exit 0.
- `python3 scripts/claim_auditor.py --diff-base main`: exit 0, 38 files, 378 claims, 0 unsourced.
- Tree-guard emitted extensive known baseline-drift diagnostics during gates; commands still returned 0. No warning was suppressed.

## Decision

HANDOVER_EVIDENCE: PARTIAL
LEDGER_CONTINUITY: RECONCILED
PUBLIC_TRANSACTION_EVIDENCE: GENERAL_PROBLEM_ONLY
HYPOTHESIS_STATUS: ABANDON
ACCESS_FEASIBILITY: WEAK
WILLINGNESS_TO_PAY: UNVALIDATED
TECHNICAL_FIT: FAILED_UNTIL_NEW_EVIDENCE
DIFFERENTIATION: NOT_DEMONSTRATED
OWNER_SPEND_RECOMMENDATION: DO_NOT_SPEND
CONTACT_READINESS: HOLD
PRODUCT_BUILD: STOP
VENTURE_DECISION: STOP
PRODUCT_PILOT_STATUS: NOT_APPROVED

First evidence commit: `b208426`.

## Raw custom-runner output at implementation commit

```console
$ python3 tests/test_classification.py
[2026-08-05T10:17:23Z] "OPTIONS /v1/check HTTP/1.1" 200 -
[2026-08-05T10:17:24Z] "GET /health HTTP/1.1" 200 -
[2026-08-05T10:17:24Z] "GET /health HTTP/1.1" 200 -
[2026-08-05T10:17:24Z] "GET /health HTTP/1.1" 200 -
[2026-08-05T10:17:30Z] "GET /health HTTP/1.1" 200 -
[2026-08-05T10:17:30Z] "GET /health/ HTTP/1.1" 200 -
[2026-08-05T10:17:30Z] "GET /nonexistent HTTP/1.1" 404 -
[2026-08-05T10:17:30Z] "GET /v1/dashboard HTTP/1.1" 200 -
[2026-08-05T10:17:30Z] "GET /v1/dashboard HTTP/1.1" 200 -
Error reading dashboard: disk error
[2026-08-05T10:17:31Z] "GET /v1/dashboard HTTP/1.1" 500 -
[2026-08-05T10:17:31Z] "GET /v1/questionnaire HTTP/1.1" 200 -
Error in /v1/questionnaire: Traceback (most recent call last):
  File "/home/mkuziva/getregula-validation-fcebd50/scripts/api_server.py", line 379, in _handle_get_questionnaire
    questionnaire = generate_questionnaire()
                    ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/unittest/mock.py", line 1134, in __call__
    return self._mock_call(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/unittest/mock.py", line 1138, in _mock_call
    return self._execute_mock_call(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/unittest/mock.py", line 1193, in _execute_mock_call
    raise effect
RuntimeError: broken

[2026-08-05T10:17:33Z] "GET /v1/questionnaire HTTP/1.1" 500 -
[2026-08-05T10:17:33Z] "POST /v1/nonexistent HTTP/1.1" 404 -
Running 1090 tests...

✓ register: schema loads with A=13, B=9, C=5
  PASS  all 22 mapped DPV terms exist in vocabulary
✓ register: excluded_under_49_4 flags correct (A: 6/8/9 only, B/C: all False)
  PASS  vocabulary snapshot records honest status + namespace
✓ one off-switch object, shared by every caller, matching nothing
  PASS  every emitted eu-aiact IRI exists in the vocabulary
✓ the off-switch pattern matches nothing
✓ one reconciler and one TotalMismatch across all three callers
✓ register: provider point 4 → A / public
✓ reconcile: matching itemisation accepted
✓ same-tree key separates lines; cross-commit signature does not
✓ build_regulations: schema has 26 required keys
✓ reconcile: under-counted itemisation rejected, gap named
✓ register: critical infra → national
✓ build_regulations: validator rejects missing keys
✓ gate unit agrees with the auditor: 89 findings over 78 files
  PASS  _file_matches_glob basename match
  PASS  all 16 high-risk pattern categories mapped
✓ two identical claims on one line remain two findings
✓ reconcile: over-counted itemisation rejected
✓ register: biometrics → non_public, excludes 6,8,9
✓ build_regulations: validator rejects empty tracker_rows
  PASS  _file_matches_glob no match
✓ reconcile: empty itemisation cannot stand in for a nonzero total
✓ findings_over agrees with the auditor: 0 over 11 file(s)
✓ register: law enforcement → non_public
  PASS  prohibited letters ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'] handled; (ba)/(bb) are honest gaps
✓ AI detection: Python libraries
  PASS  _file_matches_glob case insensitive
✓ build_regulations: validator rejects malformed FAQ entries
✓ register: migration → non_public
  PASS  _file_matches_glob full path pattern
✓ main-only report: reconciles before printing, both directions
✓ build_regulations: tracker badge states map correctly
✓ enumeration reconciles against the gate totals and names the gap
✓ AI detection: model files
✓ register: Art 6(3) exemption → B mandatory
✓ policy_config: get_policy_parse_error() return type is correct
  PASS  specific Annex III mappings reference existing DPV concepts
  PASS  _search_content finds patterns
✓ build_regulations: sections render with id + heading
tree-guard: no baseline recorded (run --record first)
tree-guard: no baseline recorded (run --record first)
tree-guard: tree matches baseline
tree-guard: TREE CHANGED since baseline:
  newly changed since record: a.txt
tree-guard: TREE CHANGED since baseline:
  newly changed since record: a.txt
✓ AI detection: API endpoints
✓ register: public-authority deployer → C / public
  PASS  _search_content no matches
✓ an unjoinable revealed finding refuses to enumerate, and names it
  PASS  prohibited 5(1)(c) -> ProhibitedAISystem-A5-1-c
✓ an unjoinable revealed finding refuses to enumerate, and names it
✓ AI detection: ML patterns
✓ build_regulations: faq block empty when faq missing
  PASS  _search_content case insensitive
✓ register: public-authority biometrics → C / non_public
✓ arm-delta report: four totals reconciled, direction check fires
✓ build_regulations: sources render with url and note
  PASS  Article 5(1)(ba) is an explicit gap, no invented concept
✓ register: private deployer → not_applicable + correct redirects
✓ enumeration reconciles against the gate totals, and refuses a gap
  PASS  _is_in_directory positive
✓ AI detection: non-AI code ignored
✓ build_regulations: Article JSON-LD valid
  PASS  _is_in_directory negative
  PASS  Annex III area-only mapping does not over-claim a sub-point
✓ build_regulations: BreadcrumbList has 3 levels
✓ Prohibited: social scoring
  PASS  _is_in_directory nested
  PASS  specific high-risk categories map to their DPV concepts
✓ build_regulations: FAQ JSON-LD matches visible questions
  PASS  _is_in_directory file not dir
✳ Art 5 reversed/wider-gap patterns
✓ residue report: all four totals reconciled
✓ build_regulations: end-to-end render produces valid HTML
✓ totals reconcile, and the imported check still refuses a mismatch
  PASS  Korea/Colorado are out-of-scope, not forced into EU concepts
✓ register: gap list contains 10 undriveable fields
  PASS  _score_to_status not_found
✓ Prohibited: emotion in workplace
✓ residue report: per-finding and per-disposition views reconciled
  PASS  _score_to_status partial
  PASS  limited risk -> RiskLevelTransparencyRequired (Article 50)
✓ CITATION_WORDS restored after a raising measurement
  PASS  _score_to_status moderate
  PASS  operational/minimal tiers are not AI-Act risk indicators
✓ Prohibited: emotion in school
✓ Prohibited: real-time biometric in public
  PASS  _score_to_status strong
  PASS  document has honest disclaimer + vocabulary status
  PASS  _walk_project finds scannable files
✓ Prohibited: biometric sensitive attributes
✓ build_regulations: UK region loads and validates (5 sections)
✓ recovery reporting distinguishes a hit from a miss
  PASS  highestRiskLevel = most severe tier present (prohibited)
✓ Prohibited: criminal prediction
  PASS  _walk_project skips node_modules
  PASS  non-EU indicators separated as out-of-scope nodes
  PASS  dedup collapses identical concepts; suppressed findings dropped
✓ Prohibited: subliminal manipulation
  PASS  _read_file success
✓ Prohibited: facial recognition scraping
  PASS  output deterministic and valid JSON
  PASS  _read_file nonexistent
✓ 6 corpus definitions, all tracked and scannable
  PASS  empty scan -> valid document, no risk level, no indicators
✓ High-risk: employment
  PASS  validate_model_card complete
✓ the module control fires on a planted defect, then goes silent
✓ Recall: realistic classify_resume code correctly flagged employment
✓ 8 apparatus scripts, enumerated by import
  merge_blockers.py:438 in reconcile_arm_delta() label=None
  merge_blockers.py:459 in report_main_only() label='published-surface findings ON MAIN'
  merge_blockers.py:495 in reconcile_residue() label=None
  merge_blockers.py:499 in reconcile_residue() label='survive BOTH, itemised one finding per line'
  merge_blockers.py:501 in reconcile_residue() label='survive BOTH, by disposition'
  merge_blockers.py:556 in main() label='published-surface findings ON MAIN'
✓ reconcile call sites: 6 in 4 functions
  PASS  validate_model_card partial
✓ 103 tracked records, enumerated by git ls-files
✓ all 44 sites map to a classified inventory entry
  residue path reconciles: total findings
  residue path reconciles: survive introduced-claim alone
  residue path reconciles: survive published-surface alone
  residue path reconciles: survive BOTH
  residue path reconciles: survive BOTH, itemised one finding per line
  residue path reconciles: survive BOTH, by disposition
  main-only path reconciles: published-surface findings ON MAIN
  arm-delta path reconciles: published-surface findings ON MAIN, citation-word arm ON
  arm-delta path reconciles: published-surface findings ON MAIN, citation-word arm OFF
  arm-delta path reconciles: revealed by switching the citation-word arm off
  arm-delta path reconciles: findings the arm off would stop reporting
✓ reconciliations across the module: 6 residue + 1 main-only + 4 arm-delta + 1 json-only = 12
  PASS  validate_model_card empty
✓ Recall: ed-tech AI (essay grading, dropout, admissions) correctly flagged
✓ the rejected heuristic has not been reintroduced
✓ every one of the 31 entries names a live site
  PASS  _compute_regulation_overlap high_risk
✓ every tracked record reconciles at this commit
✓ ledger status: 91 commit claims verified
✓ 44 sites, 31 distinct, 7 cross-state, 1 found defective
  PASS  _compute_regulation_overlap minimal_risk
✓ Recall: fintech/insurtech/govtech AI correctly flagged essential services
  PASS  _compute_regulation_overlap not_ai
  PASS  _compute_regulation_overlap prohibited
✓ every cross-state entry states key, collision and comparison
✓ ledger status control: false hold rejected, true statement kept
  printed total: total findings
  printed total: survive introduced-claim alone
  printed total: survive published-surface alone
  printed total: survive BOTH
  printed total: published-surface findings ON MAIN
  printed total: published-surface findings ON MAIN, citation-word arm ON
  printed total: published-surface findings ON MAIN, citation-word arm OFF
  printed total: revealed by switching the citation-word arm off
  printed total: findings the arm off would stop reporting
✓ 9 printed totals, all reconciled
[2026-08-05T10:17:35Z] "POST /v1/classify HTTP/1.1" 400 -
[2026-08-05T10:17:35Z] "POST /v1/classify HTTP/1.1" 400 -
[2026-08-05T10:17:35Z] "POST /v1/classify HTTP/1.1" 400 -
[2026-08-05T10:17:35Z] "POST /v1/classify HTTP/1.1" 400 -
[2026-08-05T10:17:35Z] "POST /v1/classify HTTP/1.1" 400 -
[2026-08-05T10:17:35Z] "POST /v1/classify HTTP/1.1" 400 -
[2026-08-05T10:17:35Z] "POST /v1/classify HTTP/1.1" 400 -
[2026-08-05T10:17:35Z] "POST /v1/classify HTTP/1.1" 400 -
[2026-08-05T10:17:35Z] "POST /v1/classify HTTP/1.1" 400 -
[2026-08-05T10:17:35Z] "POST /v1/classify HTTP/1.1" 200 -
[2026-08-05T10:17:35Z] "POST /v1/classify HTTP/1.1" 200 -
[2026-08-05T10:17:35Z] "POST /v1/classify HTTP/1.1" 200 -
Error in /v1/classify: Traceback (most recent call last):
  File "/home/mkuziva/getregula-validation-fcebd50/scripts/api_server.py", line 313, in _handle_classify
    result = classify(text)
             ^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/unittest/mock.py", line 1134, in __call__
    return self._mock_call(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/unittest/mock.py", line 1138, in _mock_call
    return self._execute_mock_call(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/unittest/mock.py", line 1193, in _execute_mock_call
    raise effect
RuntimeError: boom

[2026-08-05T10:17:35Z] "POST /v1/classify HTTP/1.1" 500 -
[2026-08-05T10:17:35Z] "POST /v1/check HTTP/1.1" 400 -
[2026-08-05T10:17:35Z] "POST /v1/check HTTP/1.1" 400 -
[2026-08-05T10:17:35Z] "POST /v1/check HTTP/1.1" 403 -
[2026-08-05T10:17:35Z] "POST /v1/check HTTP/1.1" 400 -
[2026-08-05T10:17:35Z] "POST /v1/check HTTP/1.1" 200 -
[2026-08-05T10:17:35Z] "POST /v1/check HTTP/1.1" 200 -
[2026-08-05T10:17:35Z] "POST /v1/check HTTP/1.1" 200 -
[2026-08-05T10:17:35Z] "POST /v1/check HTTP/1.1" 200 -
[2026-08-05T10:17:35Z] "POST /v1/check HTTP/1.1" 200 -
[2026-08-05T10:17:35Z] "POST /v1/check HTTP/1.1" 200 -
[2026-08-05T10:17:35Z] "POST /v1/check HTTP/1.1" 200 -
[2026-08-05T10:17:35Z] "POST /v1/check HTTP/1.1" 200 -
[2026-08-05T10:17:35Z] "POST /v1/check HTTP/1.1" 200 -
[2026-08-05T10:17:35Z] "POST /v1/check HTTP/1.1" 200 -
[2026-08-05T10:17:35Z] "POST /v1/check HTTP/1.1" 200 -
Error in /v1/check: Traceback (most recent call last):
  File "/home/mkuziva/getregula-validation-fcebd50/scripts/api_server.py", line 263, in _handle_check
    findings = scan_files(
               ^^^^^^^^^^^
  File "/usr/lib/python3.12/unittest/mock.py", line 1134, in __call__
    return self._mock_call(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/unittest/mock.py", line 1138, in _mock_call
    return self._execute_mock_call(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/unittest/mock.py", line 1193, in _execute_mock_call
    raise effect
RuntimeError: scan broke

[2026-08-05T10:17:35Z] "POST /v1/check HTTP/1.1" 500 -
[2026-08-05T10:17:35Z] "POST /v1/gap HTTP/1.1" 400 -
[2026-08-05T10:17:35Z] "POST /v1/gap HTTP/1.1" 400 -
[2026-08-05T10:17:35Z] "POST /v1/gap HTTP/1.1" 403 -
[2026-08-05T10:17:35Z] "POST /v1/gap HTTP/1.1" 400 -
[2026-08-05T10:17:35Z] "POST /v1/gap HTTP/1.1" 400 -
[2026-08-05T10:17:35Z] "POST /v1/gap HTTP/1.1" 200 -
[2026-08-05T10:17:35Z] "POST /v1/gap HTTP/1.1" 200 -
[2026-08-05T10:17:35Z] "POST /v1/gap HTTP/1.1" 200 -
[2026-08-05T10:17:35Z] "POST /v1/gap HTTP/1.1" 200 -
Error in /v1/gap: Traceback (most recent call last):
  File "/home/mkuziva/getregula-validation-fcebd50/scripts/api_server.py", line 362, in _handle_gap
    assessment = assess_compliance(str(target), articles=articles)
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/unittest/mock.py", line 1134, in __call__
    return self._mock_call(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/unittest/mock.py", line 1138, in _mock_call
    return self._execute_mock_call(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/unittest/mock.py", line 1193, in _execute_mock_call
    raise effect
RuntimeError: fail

[2026-08-05T10:17:35Z] "POST /v1/gap HTTP/1.1" 500 -
[2026-08-05T10:17:35Z] "POST /v1/questionnaire/evaluate HTTP/1.1" 400 -
[2026-08-05T10:17:35Z] "POST /v1/questionnaire/evaluate HTTP/1.1" 400 -
[2026-08-05T10:17:35Z] "POST /v1/questionnaire/evaluate HTTP/1.1" 400 -
[2026-08-05T10:17:35Z] "POST /v1/questionnaire/evaluate HTTP/1.1" 200 -
Error in /v1/questionnaire/evaluate: Traceback (most recent call last):
  File "/home/mkuziva/getregula-validation-fcebd50/scripts/api_server.py", line 408, in _handle_questionnaire_evaluate
    result = evaluate_questionnaire(answers)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/unittest/mock.py", line 1134, in __call__
    return self._mock_call(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/unittest/mock.py", line 1138, in _mock_call
    return self._execute_mock_call(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/unittest/mock.py", line 1193, in _execute_mock_call
    raise effect
RuntimeError: fail

[2026-08-05T10:17:35Z] "POST /v1/questionnaire/evaluate HTTP/1.1" 500 -
[2026-08-05T10:17:35Z] "GET /bad HTTP/1.1" 422 -
[2026-08-05T10:17:35Z] "GET /test HTTP/1.1" 200 -
[2026-08-05T10:17:35Z] "GET /test HTTP/1.1" 200 -
[2026-08-05T10:17:35Z] "POST /v1/check HTTP/1.1" 403 -
[2026-08-05T10:17:35Z] "POST /v1/classify HTTP/1.1" 400 -
[2026-08-05T10:17:35Z] "POST /v1/questionnaire/evaluate HTTP/1.1" 400 -
[2026-08-05T10:17:35Z] "POST /v1/check HTTP/1.1" 200 -
[2026-08-05T10:17:35Z] "GET / HTTP/1.1" 404 -
[2026-08-05T10:17:35Z] "POST /health HTTP/1.1" 404 -
[2026-08-05T10:17:36Z] "GET /v1/check HTTP/1.1" 404 -
[2026-08-05T10:17:36Z] "GET /health/// HTTP/1.1" 200 -
[2026-08-05T10:17:36Z] "POST /v1/check HTTP/1.1" 200 -
[2026-08-05T10:17:36Z] "POST /v1/gap HTTP/1.1" 200 -
[2026-08-05T10:17:36Z] "GET /health HTTP/1.1" 200 -
[2026-08-05T10:17:36Z] "POST /v1/classify HTTP/1.1" 200 -
  PASS  Article 9: no risk docs
✓ an unclassified site is detected, so the check is not inert
✓ Recall: crime-analytics AI (parole, bail, threat) correctly flagged law enforcement
✓ ledger status: prose-only remote claims rejected
  PASS  Article 9: generic risk docs
✓ withdrawn-paragraph predicate follows the marker
  PASS  Article 9: AI-referenced risk docs
✓ ledger status: invented hashes rejected
✓ paragraph_lines: the reproducible row shares its paragraph
✓ ledger status: tree `563876f` cited, refused as a marker
✓ Recall: biometric AI (iris, gait, age-from-face) correctly flagged
✓ register: _highest_annex_iii_point reads indicators+description (regression)
  PASS  Article 9: structured mitigations
✓ disposition: reproducible row blocked, withdrawn row inherited
✓ ledger supersession: 14 declarations paired
  PASS  Article 10: no data governance
✓ Recall: critical-infrastructure AI (grid, SCADA, railway) correctly flagged
  PASS  Article 10: data docs + validation
✓ ledger supersession control: unpaired named, paired accepted
✓ Recall: migration AI (visa, asylum, border) correctly flagged
  PASS  Article 11: no tech docs
✓ ledger supersession: reverse direction required too
  PASS  Article 11: model card file
✓ ledger supersession: dangling and self-referential markers caught
✓ Recall: justice AI (verdict, case outcome, voter targeting) correctly flagged
✓ ledger supersession: trailing punctuation is not part of the id
  PASS  Article 12: no logging
✓ ledger supersession: many-to-one accepted
  PASS  Article 12: basic logging
✓ Recall: medical-device AI (radiology, sepsis, dosing) correctly flagged
✓ row_id: only table body rows produce an id
✓ ledger status: marker polarity follows the resolver
  PASS  Article 12: AI operation logging
✓ Recall: safety-component AI (ADAS, cobot, drone) correctly flagged
  PASS  Article 13: no transparency
  PASS  Article 13: with disclosure
✓ High-risk: credit scoring / essential services
  PASS  Article 14: no oversight
✓ High-risk: biometrics
✓ High-risk: medical devices
  PASS  Article 14: oversight mechanism
✓ High-risk: education
  PASS  Article 14: oversight docs
✓ High-risk: critical infrastructure
✓ High-risk: law enforcement
  PASS  Article 15: no security
✓ High-risk: migration
✓ High-risk: justice
  PASS  Article 15: with tests
✓ High-risk: safety components
✓ High-risk: all articles 9-15 present
  PASS  Article 15: SECURITY.md
✓ Limited-risk: chatbot
✓ Limited-risk: synthetic content
  PASS  Article 17: no QMS
✓ Limited-risk: biometric categorisation
  PASS  Article 17: with QMS docs
✓ Limited-risk: emotion recognition (no workplace)
✓ Minimal-risk internal tier is presented without legal clearance
  PASS  assess_compliance structure
✓ Minimal-risk: generic AI training
✓ Minimal-risk: spam filter
  PASS  assess_compliance all articles
✓ Edge case: empty input
✓ Edge case: case insensitivity
  PASS  assess_compliance single article
  PASS  assess_compliance article result keys
✓ Edge case: multiple indicators → high confidence
✓ Edge case: prohibited detected without AI indicator
✓ Edge case: prohibited overrides high-risk
✓ Edge case: high-risk overrides limited-risk
  PASS  assess_compliance invalid path
✓ Edge case: action fields correct
  PASS  assess_compliance overall score range
✓ Edge case: serialization
  PASS  format_gap_text contains key sections
✓ Edge case: JSON output
  PASS  format_gap_text status labels
✓ Policy engine: YAML fallback parser works
  PASS  format_gap_json is valid
✓ Policy engine: force_high_risk and exempt work
  PASS  ARTICLE_NUMBERS are strings
  PASS  ARTICLE_TITLES match NUMBERS
✓ Policy engine: prohibited overrides policy exempt (safety-first)
  PASS  ARTICLE_CHECKERS match NUMBERS
  PASS  ARTICLE_6_GUIDELINES_STATUS structure
✓ Prohibited: exceptions field present in classification
  PASS  MODEL_CARD_REQUIRED_SECTIONS structure
✓ High-risk: performance review
  PASS  _determine_highest_risk honours suppressions like check
✓ Audit trail: hash chain integrity
✓ Audit trail: CSV export
✓ Confidence scoring: numeric scores present
✓ Confidence scoring: tier ordering correct
✓ Confidence scoring: multiple indicators increase score
✓ Report: SARIF output structure valid
✓ Report: HTML contains disclaimer
✓ Report: HTML includes dependency analysis section
✓ Report: inline suppression works
✓ Questionnaire: generates 8 Article 6-derived questions
✓ Questionnaire: high-risk answers produce HIGH_RISK
✓ Questionnaire: low-risk answers produce MINIMAL_RISK
✓ Session: aggregation produces valid profile
✓ Baseline: save and compare work correctly
✓ Timeline: verified enforcement dates present and accurate
✓ Secrets: detects OpenAI API key
✓ Secrets: detects AWS access key
✓ Secrets: no false positives on normal code
✓ Secrets: proper redaction in output
✓ GPAI: detects training patterns
✓ GPAI: inference patterns not flagged as training
  SKIP  test_hook_prohibited_block (hooks/pre_tool_use.py not present (local dev file))
  SKIP  test_hook_high_risk_allow_with_iso (hooks/pre_tool_use.py not present (local dev file))
  SKIP  test_hook_secret_block (hooks/pre_tool_use.py not present (local dev file))
  SKIP  test_hook_clean_pass (hooks/pre_tool_use.py not present (local dev file))
✓ AI credential governance: detects credentials in AI files as Article 15 finding
✓ Registry: org scan finds AI projects
✓ Registry: CSV export works
✓ Compliance: workflow transitions are valid
✓ Compliance: status updates and records history
✓ Governance: contacts readable from policy
✓ QMS: scaffold generates with all Article 17 sections
✓ Secrets: OpenAI pattern does not false-positive on Anthropic keys
✓ AST: parse_python_file extracts imports, functions, AI detection
✓ AST: classify_context distinguishes implementation vs test
✓ AST: data flow tracing works
✓ AST: detects human oversight presence and absence
✓ AST: detects logging practices near AI operations
✓ Compliance gap: produces valid assessment structure
✓ Compliance gap: Article 15 detects test files as evidence
✓ Regulatory: basis readable from policy
✓ Cross-platform: file locking functions available
✓ AST engine: Python parse returns unified format
✓ AST engine: JS regex fallback detects openai import
✓ AST engine: TS regex fallback detects 2+ AI imports
✓ AST engine: express-only JS not flagged as AI
✓ AST engine: language detection correct for .py/.js/.ts/.tsx/.jsx/.mjs/.rb/.java/.go
✓ AST engine: Java AI detection
✓ AST engine: Go AI detection
✓ AST engine: Java non-AI correctly identified
✓ Dependency scan: parses requirements.txt pinning quality
✓ Dependency scan: AI dependency identification
✓ Dependency scan: pinning score calculation
✓ Dependency scan: lockfile detection
✓ Dependency scan: parses package.json
✓ Advisory fallback: _load_advisories works from pyc __file__ path
✓ Dependency scan: detects known compromised versions
✓ Dependency scan: go.mod basic parsing
✓ Dependency scan: go.mod AI detection
✓ Dependency scan: go.mod pinning is always exact
✓ Dependency scan: build.gradle Groovy DSL parsing
✓ Dependency scan: build.gradle.kts Kotlin DSL parsing
✓ Dependency scan: build.gradle AI detection
✓ Dependency scan: Cargo.toml parsing
✓ Dependency scan: vcpkg.json parsing
✓ Gap assessment: Article 15 includes dependency pinning
✓ Framework mapper: EU AI Act to NIST AI RMF
✓ Framework mapper: all three frameworks mapped
✓ Framework mapper: OWASP LLM Top 10 mapping
✓ Framework mapper: MITRE ATLAS mapping
✓ Framework mapper: NIST CSF 2.0 mapping
✓ Framework mapper: SOC 2 mapping
✓ Framework mapper: ISO 27001 mapping
✓ Framework mapper: core frameworks incl. OWASP Agentic mapped simultaneously
✓ Policy: thresholds readable from policy
✓ Policy: exclusions readable from policy
✓ Integration: high-risk fixture scanned correctly
✓ Integration: compliant fixture assessed correctly
✓ Integration: unpinned dependency fixture scanned correctly
✓ Integration: CLI check runs end-to-end
regula: WARNING: rules file /nonexistent/path.yaml was not read (missing, not a regular file, a symlink, or oversized). Using built-in rules only.
✓ Pattern quality: sentence_bleu not false positive
✓ Pattern quality: Embedding layer not false positive
✓ Pattern quality: generic predict not false positive
✓ Pattern quality: CV screening correctly flagged
✓ Pattern quality: credit scoring correctly flagged
✓ Confidence threshold: readable from policy
✓ Confidence tiers: prohibited = block
✓ Confidence tiers: low confidence = info
✓ Tree-sitter: JS import extraction
✓ Tree-sitter: JS data flow tracing
✓ Tree-sitter: TS oversight detection
✓ Tree-sitter: JS function/class extraction
✓ AST engine: Rust AI detection
✓ AST engine: C++ AI detection
✓ AST engine: Rust non-AI correctly identified
✓ SBOM: CycloneDX 1.7 structure valid
✓ SBOM: AI libraries marked with regula properties
✓ SBOM: ML model files detected
✓ FP fix: invoice_recognition not false positive
✓ FP fix: page_estimation not false positive
✓ FP fix: credit risk model correctly detected
✓ FN fix: train_credit_model correctly detected as high-risk
✓ FP fix: social media engagement not prohibited
✓ Exemption: narrow procedural task is likely exempt
✓ Exemption: autonomous system not exempt
✓ Model card: complete card scores high
✓ Model card: incomplete card flags missing sections
✓ Diff mode: correctly identifies changed files
✓ Remediation: employment gets specific fix
✓ Remediation: credential gets env var fix
✓ Agent monitor: handles empty session
✓ Agent monitor: MCP config credential detection
✓ AI security: detects unsafe pickle deserialization
✓ AI security: detects eval on AI output
✓ AI security: torch.load with weights_only=True correctly excluded
✓ Prompt injection (direct): request body in messages content
✓ Prompt injection (indirect): web fetch one-liner
✓ Prompt injection (indirect): file read one-liner
✓ Prompt injection (indirect): RAG chain pattern
✓ Prompt injection (tool): subprocess output
✓ Prompt injection (tool): observation pattern
✓ Prompt injection: no false positive on proper separation + sanitiser
✓ Prompt injection: remediation mentions guardrails
✓ Exempt: early-exit when not in Annex III
✓ Exempt: profiling overrides all conditions
✓ Exempt: condition (a) narrow procedural
✓ Exempt: all four conditions
✓ Exempt: none of (a)-(d) means not exempt
✓ Exempt: parse_answers_csv valid input
✓ Exempt: parse_answers_csv wrong length rejected
✓ Exempt: parse_answers_csv invalid token rejected
✓ Exempt: format_result includes guidelines disclosure
✓ Gap: Article 6 guidelines status in assessment dict
✓ SME Annex IV: generator produces non-empty markdown
✓ SME Annex IV: interim-format disclosure present
✓ SME Annex IV: references companion commands
✓ SME conform: single-file pack with correct shape
✓ SME conform: manifest carries interim-format disclosure
✓ Doctor command: runs, exits 0, supports JSON
✓ Self-test command: runs, exits 0, all assertions pass
✓ Error hierarchy: all classes exist with correct exit codes
✓ CLI exit codes: 0=success, 1=findings, 2=tool error
✓ Graceful degradation: silent default + REGULA_VERBOSE opt-in
✓ Init dry-run: shows analysis, creates no files
✓ JSON envelope: format_version, regula_version, command, timestamp, data all present
✓ Exit code 1: WARN-tier findings trigger exit 1
✓ --ci flag: compliant code exits 0
✓ --ci flag: WARN-tier findings exit 1
✓ --ci flag: error exits 2
✓ --ci flag: works before subcommand
✓ --ci flag: INFO-tier exits 0
✓ Smoke: report --format json exits 0 with output
✓ Smoke: discover exits 0 with output
✓ Smoke: install --help exits 0
✓ Smoke: status exits 0
✓ Smoke: feed --format json exits 0 with envelope
✓ Smoke: questionnaire --format json exits 0 with envelope
✓ Smoke: session --format json exits 0 with envelope
✓ Smoke: baseline --help exits 0
✓ Smoke: docs exits 0 with output
✓ Smoke: compliance exits 0
✓ Smoke: gap --format json exits 0 with envelope
✓ Smoke: benchmark --format json exits 0 with output
✓ Smoke: timeline --format json exits 0 with envelope
✓ Smoke: deps --format json exits 0 with envelope
✓ Smoke: sbom --format json exits 0 with CycloneDX envelope
✓ Smoke: agent --format json exits 0 with envelope
✓ Generic exception handler: catches non-RegulaError, exits 2
✓ --framework flag removed (unrecognized argument)
✓ GitHub Action: action.yml structure valid
✓ PDF export: HTML fallback returns HTML bytes when weasyprint absent
✓ PDF export: generate_annex_iv_html produces valid HTML
✓ MCP server: tools/list returns correct tool names
✓ MCP server: initialize returns correct protocolVersion
✓ MCP server: regula_classify returns tier
✓ Bias eval: compute_stereotype_score returns correct per-category scores with CI
✓ Bias eval: CrowS-Pairs sample loaded 100 pairs
✓ Bias eval: handles Ollama unavailability gracefully
✓ RFC 3161: _build_tsq produces valid DER
✓ RFC 3161: parse_tsr rejects invalid input
✓ RFC 3161: log_event stores tst_hex when external_timestamp=True
✓ Compliance check: JS/TS Article 14 wired correctly (score=100)
✓ Declaration of Conformity: all Annex XIII required fields present
✓ Benchmark: compute_article_pass_rates returns correct pass rates
✓ Metrics: record_scan and get_stats work correctly
✓ Metrics: reset_stats clears all data
✓ Metrics: get_stats returns zeros when no file exists
✓ Security self-check: passed (19 total, 19 known acceptable)
✓ Security self-check: result structure is correct
✓ Config validate: repo policy is valid (0 warnings)
✓ Config validate: invalid thresholds correctly rejected
✓ Config validate: nonexistent explicit path returns valid=False
✓ Quickstart: creates policy file with org name
✓ Quickstart: skips existing policy file
✓ Quickstart: result structure has all expected keys
✓ LGPD framework: Article 13 maps to 4 LGPD references
✓ Marco Legal da IA: Article 14 maps to 2 references
✓ LGPD Art. 20 (direito à revisão de decisões automatizadas) present in Article 14 mapping
✓ All 7 EU AI Act articles (9-15) have LGPD mappings
✓ Bug fix: scan_files accepts single file path (found 0 findings)
✓ Bug fix: CLI check accepts single file path (exit 0)
✓ Bug fix: metrics normalises raw tiers → {'BLOCK': 4, 'INFO': 1, 'WARN': 2}
✓ Bug fix: PROHIBITED normalised to BLOCK → {'BLOCK': 2}
✓ Bug fix: format_gap_text renders LGPD framework cross-refs
✓ Bug fix: format_gap_text renders multiple framework cross-refs
check FP reduction: comment with prohibited term not classified as prohibited
check FP reduction: comment with high-risk term not classified as high-risk
check FP reduction: actual prohibited code still correctly classified
check strip_comments: Python comments and docstrings stripped correctly
check strip_comments: JavaScript comments stripped correctly
✓ i18n: English default works
✓ i18n: Portuguese translation works
✓ i18n: fallback to key name for unknown keys
✓ i18n: German translation works
✓ Custom rules: YAML loading works correctly
✓ Custom rules: missing file returns empty structure
✓ Custom rules: custom prohibited pattern correctly detected
✓ Security: bias_eval rejects non-HTTP endpoints
✓ Bias eval: log-prob scoring uses normalised (mean per-token) comparison
✓ Bias eval: Tier 2 (eval-duration proxy) removed
✓ Bias eval: compute_stereotype_score returns CI and confidence per category
✓ Security: ReDoS protection for custom rule patterns
✓ Cross-function: AI flow traced through helper function
✓ Cross-function: oversight across function boundaries
✓ Cross-function: no false positive on non-AI code
✓ Docs integration: Annex IV output is 54309 chars
✓ Docs: auto-populated sections and guided templates present
✓ Docs: completion report shows per-section status
✓ AST: enhanced function extraction with docstring, line, return type
✓ Docs: dependency extraction finds AI libraries with versions
✓ Docs: function table included in Annex IV output
✓ Explain: high-risk code produces full explanation
✓ Explain: minimal-risk code produces no obligation roadmap
✓ Explain: provider detected from training code
✓ Explain: deployer detected from API usage
✓ Explain: unclear role when no AI indicators
✓ Explain: obligation roadmap covers required articles
✓ Explain: formatted output has all required sections
✓ Explain: line-level match reports correct line number
✓ Explain: compliance status detected for Article 12 logging
✓ Context: example directory detection works
✓ Context: __init__.py detection works
✓ Context: mock pattern detection works
✓ Context: combined penalty computation correct
✓ Cross-file: import map resolves module names to file paths
✓ Cross-file: AI data flow detected between files
✓ Cross-file: non-AI imports correctly ignored
✓ Domain scoring: employment keywords detected with AI
✓ Domain scoring: no boost without AI indicators
✓ Domain scoring: decision logic adds extra boost
✓ Domain scoring: multiple domains detected
✓ Domain scoring: generic AI code gets no boost
✓ Plan: generates tasks from findings
✓ Plan: priority ordering (prohibited first)
✓ Plan: unique task IDs
✓ Plan: text output format
✓ Plan: skips strong articles
✓ Plan: CLI integration
✓ Evidence pack: generates manifest with hashes
✓ Evidence pack: required files present
✓ Evidence pack: summary contains risk tier
✓ Evidence pack: CLI integration
✓ Evidence pack: SHA-256 integrity verified
✓ Disclose: chatbot references Article 50(1)
✓ Disclose: all 4 types generate correctly
✓ Disclose: text format output
✓ Disclose: CLI integration
✓ Annex IV: all 9 sections present
✓ Annex IV: standards from policy
✓ Annex IV: completion report covers new sections
✓ Safety: driverless variant detected
✓ Safety: automated driving variant detected
✓ Safety: vehicle control system detected
✓ Chatbot: dialogue system detected
✓ Chatbot: conversational model detected
✓ Custom pattern: invalid regex raises ValueError
✓ Shared finding tier logic works correctly
✓ Framework detection: LiteLLM
✓ Framework detection: CrewAI
✓ Framework detection: AutoGen
✓ Framework detection: Haystack
✓ Framework detection: smolagents
✓ Framework detection: Ollama
✓ Framework detection: 38 architectures in ARCHITECTURE_PATTERNS
✓ Model inventory: detects gpt-4o
✓ Model inventory: detects from_pretrained model name
✓ Model inventory: JSON schema valid
✓ Model inventory: empty project returns empty list
✓ Model inventory: GPAI tiers correct for gpt-4o (frontier) and llama-3.1-8b (open_weight)
✓ Smoke: inventory exits 0 with output
✓ Multi-framework: assess_compliance returns nist_ai_rmf block when requested
✓ Multi-framework: no frameworks key when not requested (backward compat)
✓ Smoke: gap --framework nist-ai-rmf exits 0
✓ HTML report: all 7 sections present
✓ HTML report: PROHIBITED badge present for prohibited findings
✓ HTML report: self-contained (no external script/link tags)
✓ HTML report: model inventory section renders correctly
✓ Smoke: check --format html exits and produces valid HTML
✓ Smoke: check --format html -o writes HTML file
✓ Cross-file call chain: importer linked to AI call site, test functions excluded
✓ assess: no-AI answer is reported without a legal scope ruling
✓ assess: limited-risk result includes Article 50 and correct deadline
✓ assess: high-risk EU provider result correct
✓ assess: high-risk non-EU provider includes AR requirement
✓ assess: untriggered risk paths do not become legal clearance
✓ assess: Article 5 candidate includes review, enforcement date and penalty
✓ assess: run_from_answers covers all branches + rejects bad input
✓ scan_files: exposes honest files_scanned count via last_stats
✓ text classify: facial recognition → HIGH-RISK
✓ text classify: face recognition → HIGH-RISK
✓ text classify: chatbot → LIMITED-RISK
✓ text classify: credit scoring → HIGH-RISK
✓ text classify: hiring decision → HIGH-RISK
✓ text classify: autonomous vehicle → HIGH-RISK
✓ text classify: virtual assistant → LIMITED-RISK
✓ text classify: medical diagnosis → HIGH-RISK
✓ text classify: deepfake → LIMITED-RISK
✓ text classify: border control → HIGH-RISK
✓ text classify: resume screening → HIGH-RISK
✓ text classify: loan decision → HIGH-RISK
✓ text classify: self-driving car → HIGH-RISK
✓ text classify: emotion recognition → LIMITED-RISK
✓ text classify: AI-powered generic → MINIMAL-RISK
✓ text classify: non-AI text → NOT_AI
✓ is_ai_related: domain keywords detected
✓ text classify: fingerprint recognition → HIGH-RISK
✓ text classify: voice recognition → HIGH-RISK
✓ text classify: patient triage → HIGH-RISK
✓ text classify: clinical decision → HIGH-RISK
✓ discover: respects # regula-ignore directive
✓ deadline: prohibited → 2025-02-02, no omnibus
✓ deadline: high-risk Annex III → 2027-12-02 (Omnibus enacted)
✓ deadline: safety/medical → omnibus 2028-08-02
✓ deadline: limited-risk → omnibus 2026-12-02
✓ deadline: minimal-risk → no deadline
✓ deadline: agent_autonomy → omnibus 2027-12-02
✓ deadline: present in JSON check output
✓ SARIF: ai-security rules present
✓ SARIF: agent-autonomy rules present
✓ git ref validation: safe refs accepted, injections blocked
✓ MCP: root path scan blocked
✓ timeline: Omnibus agreement and post-agreement milestones present
✓ deadline: credential_exposure → 2027-12-02, urgency note kept
✓ conform: end-to-end pack structure verified
✓ oversight: e2e — 2 paths, 1 reviewed
✓ ai-bom: 1 models, 1 datasets detected
✓ notebook: extract_code returns code cells only
✓ notebook: corrupt file returns empty string without raising
✓ notebook: scan_files found 1 findings in .ipynb
✓ self-benchmark: 261 files in 2.948s (88.5 files/s, sha=fcebd501a103)
✓ synthetic: prohibited 5/5, high_risk 16/30 (artefact-backed)
✓ precision: published number 83.5% matches random_corpus/PRECISION.json
✓ sbom: CycloneDX specVersion 1.7
✓ gpai_signatories: 8 curated vendors loaded
✓ sbom: GPAI annotation present (statuses: ['true'])
✓ nist_ai_600_1: 12 risks loaded, all mapped to EU AI Act articles
✓ findings_view: suppressed split correctly
✓ findings_view: 5 tiers grouped correctly
✓ findings_view: input list not mutated
✓ findings_view: display tier annotated (block)
✓ findings_view: empty input handled
✓ action.yml: inline PR review step present (3 inputs, 12 steps)
✓ domain: boost surfaced in finding (+15, ['employment', 'finance'])
✓ mcp: initialize + tools/list returned ['regula_check', 'regula_classify', 'regula_gap']
✓ scan_benchmarks: self-mode returned 1 files in 0.002s
  PASS  domain gating suppresses high_risk without declaration
  PASS  --domain activates high_risk findings
  PASS  fingerprint auto-activates medical domain
  PASS  fingerprint detects medical domain
  PASS  fingerprint suppresses critical_infrastructure for diffusers
  PASS  fingerprint empty project
  PASS  fingerprint: physics_sim suppresses employment
  PASS  fingerprint: library self-detection via pyproject.toml
  PASS  justice opt-in: suppressed without domain declaration

==================================================
Results: 1378 passed, 0 failed, 4 skipped (1090 test functions)
Slowest test functions:
    54.564s  __main__.test_evidence_pack_sha256_integrity
    49.027s  __main__.test_evidence_pack_cli_integration
    47.708s  __main__.test_cli_exit_codes
    46.677s  __main__.test_evidence_pack_contains_required_files
    45.650s  __main__.test_annex_iv_has_all_nine_sections
    45.289s  __main__.test_evidence_pack_generates_manifest
    45.124s  __main__.test_evidence_pack_summary_contains_risk_tier
    37.214s  __main__.test_annex_iv_standards_from_policy
    36.248s  __main__.test_annex_iv_completion_covers_new_sections
    30.935s  __main__.test_docs_auto_populated_sections
    30.722s  __main__.test_docs_completion_report
    30.355s  __main__.test_docs_include_data_flow
    13.549s  __main__.test_plan_cli_integration
    11.694s  __main__.test_smoke_check_html_output_file
    11.012s  __main__.test_smoke_check_html
     8.594s  __main__.test_smoke_inventory
     4.345s  test_hostile_sweep.test_no_command_hangs_or_escapes_on_a_hostile_tree
     3.882s  __main__.test_smoke_feed
     2.962s  __main__.test_self_scan_benchmark_runs
     2.213s  __main__.test_deadline_in_json_output
     1.925s  __main__.test_json_output_envelope
     1.724s  test_f25_exposure.test_the_gate_unit_agrees_with_the_auditors_own_total
     1.677s  test_new_commands.test_check_large_scan_no_crash
     1.345s  test_hostile_sweep.test_no_command_hangs_when_cwd_is_hostile
     1.313s  __main__.test_security_self_check_result_structure
     1.288s  __main__.test_security_self_check_passes
     1.157s  test_f25_exposure.test_the_revealed_enumeration_accounts_for_the_revealed_count
     1.057s  test_new_commands.test_deterministic_json_output
     1.021s  test_tracked_inputs.test_generator_ignores_untracked_inputs_by_construction
     0.962s  test_new_commands.test_explain_article_all_covered
     0.827s  __main__.test_ci_flag_info_tier_exits_0
     0.747s  test_scan_security.test_dense_trigger_content_is_capped_for_classification
     0.707s  __main__.test_default_scope_does_not_translate_exclusions_into_no_ai
     0.594s  __main__.test_exit_code_warn_tier
     0.590s  __main__.test_ci_flag_warn_tier_exits_1
     0.586s  __main__.test_check_cli_single_file
     0.582s  __main__.test_ci_flag_compliant_exits_0
     0.579s  __main__.test_integration_full_check_cli
     0.578s  __main__.test_ci_flag_before_subcommand
     0.566s  test_analysis_manifest.test_manifest_written_on_clean_scan
     0.566s  test_analysis_manifest.test_non_utf8_file_forces_partial_status
     0.564s  test_tracked_inputs.test_generator_writes_normally_when_inputs_are_clean
     0.559s  test_new_commands.test_env_regula_format
     0.556s  test_analysis_manifest.test_notebook_partial_cells_forces_partial_status
     0.549s  test_scan_security.test_ast_parse_memory_error_does_not_crash_entire_scan
     0.549s  test_analysis_manifest.test_json_format_also_writes_manifest
     0.549s  test_analysis_manifest.test_empty_valid_notebook_is_not_a_skip
     0.547s  test_analysis_manifest.test_annotation_only_prohibited_not_dropped
     0.546s  test_analysis_manifest.test_unknown_counts_are_null_not_fabricated
     0.545s  test_analysis_manifest.test_unreadable_file_forces_partial_status
✅ All tests passed!

[exit 0]
```

## Raw pytest output at implementation commit

```console
$ python3 -m pytest tests/ -q -rs
........................................................................ [  2%]
........................................................................ [  5%]
........................................................................ [  8%]
......ss................s............................................... [ 10%]
........................................................................ [ 13%]
........................................................................ [ 16%]
.......................................................ssss............. [ 18%]
........................................................................ [ 21%]
........................................................................ [ 24%]
........................................................................ [ 26%]
........................................................................ [ 29%]
........................................................................ [ 32%]
........................................................................ [ 34%]
........................................................................ [ 37%]
........................................................................ [ 40%]
........................................................................ [ 42%]
........................................................................ [ 45%]
........................................................................ [ 48%]
........................................................................ [ 50%]
........................................................................ [ 53%]
........................................................................ [ 56%]
........................................................................ [ 58%]
........................................................................ [ 61%]
........................................................................ [ 64%]
........................................................................ [ 66%]
........................................................................ [ 69%]
.......................sssssssssssssssssssssssssss...................... [ 72%]
........................................................................ [ 74%]
........................................................................ [ 77%]
........................................................................ [ 80%]
........................................................................ [ 82%]
........................................................................ [ 85%]
........................................................................ [ 88%]
........................................................................ [ 90%]
........................................................................ [ 93%]
........................................................................ [ 96%]
........................................................................ [ 98%]
............................                                             [100%]
=========================== short test summary info ============================
SKIPPED [2] tests/test_audit_scoping.py:464: hooks/ not present (local dev file, not tracked in git)
SKIPPED [1] tests/test_audit_surface_conformance.py:236: hooks/ not present (local dev file, not tracked in git)
SKIPPED [4] tests/test_classification.py:1295: hooks/pre_tool_use.py not present (local dev file)
SKIPPED [27] tests/test_hooks_audit.py:41: hooks/ not present (local dev file, not tracked in git)
2658 passed, 34 skipped in 857.65s (0:14:17)

[exit 0]
```
