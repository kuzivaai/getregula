# Validation-readiness evidence reconciliation

STATUS: PREPARATION ONLY
EXTERNAL ACTION: DISABLED
VENTURE DECISION: STOP
PRODUCT PILOT: NOT APPROVED

Reconciliation date: 2026-08-05. Settled implementation commit:
`f72f2f836cd3b4a5ea8c7c9cf88763a1c0fe47bb`; tree
`563876fefcfd698bd5e64d4ac8bf87c9d5172f40`.

## Material-claim reconciliation

| Claim | Verdict | Settling evidence | Correction or limitation |
|---|---|---|---|
| Implementation identity | DEMONSTRATED | `git cat-file -e`, `git show --stat`, and `git rev-parse f72f2f8^{tree}`; all exit 0 | Handover identity is correct |
| Pack contains 29 tracked files | DEMONSTRATED | `git ls-tree -r --name-only f72f2f8 docs/venture/validation-readiness-2026-08-05`; 29 enumerated | Population includes 8 main records and 21 templates/other records |
| Pack source register contains 23 sources | DEMONSTRATED | anchored row enumeration `rg '^\| S[0-9]+ '` returns 23 | This is the validation-readiness source register, not the earlier venture register |
| Fail-before returned 42 errors | DEMONSTRATED | permanent log records exact command, `FAIL (42 errors)`, exit 1, HEAD and tree | Full 42-line raw error list was not retained; its detailed composition is PARTIAL |
| Fourteen mutations failed as intended | DEMONSTRATED | source enumeration shows 12 table mutations plus missing-file and JSON-disagreement controls; exact-commit focused run: 2 passed, exit 0 | Pytest count is two test functions, not fourteen tests |
| Adversarial findings and dispositions | DEMONSTRATED | permanent log retains 8 legal and 14 experimental corrective findings plus one positive finding; `VR-DEV-01` and resulting documents retain accepted corrections | Original subagent transport envelope was not retained separately |
| Custom runner | DEMONSTRATED | exact-commit rerun: 1,378 passed, 0 failed, 4 skipped across 1,090 functions; exit 0; raw-log SHA-256 `0a9c661c18df9661432f236db14b33292fe17041a9c1ef60fea99fc68fecef3d` | Four skips all state `hooks/pre_tool_use.py` is an absent local-development file |
| Pytest | DEMONSTRATED | `python3 -m pytest tests/ -q -rs`: 2,658 passed, 34 skipped in 857.65s; exit 0; raw-log SHA-256 `953b4b3db1c341ca4c1cd520a50225fc947885630a2a8057ab6359c648c98594` | 27 `test_hooks_audit`, 4 imported classification, 2 audit-scoping and 1 audit-surface skips all concern absent untracked `hooks/` files |
| Self-test | DEMONSTRATED | exact-commit rerun: 6/6, exit 0 | Narrow built-in assertions only |
| Doctor | DEMONSTRATED | exact-commit rerun: 9 pass, 3 info, exit 0 | Information: no hooks, no crash backend, no declared domain |
| Ruff | DEMONSTRATED | exact-commit configured F821/F811 command: all checks passed, exit 0 | It is not a formatter or full style check |
| HTML parser | DEMONSTRATED | configured parser enumerated 56 HTML files, 0 bad, exit 0 | Structural parser only, not accessibility or visual evidence |
| Security self-check | DEMONSTRATED | 19 known acceptable, 0 unexpected, exit 0 | Only the tool's declared self-check scope |
| Six fast gates | DEMONSTRATED | facts 148/17; site 1,173 internal refs/0 dead with 2 documented warnings; cascade 2,692/11; recall and gap fresh-match; self-reference positive and negative controls; all exit 0 | Gate scope remains narrower than repository-wide correctness |
| Merge blocker / claim diff | DEMONSTRATED | `claim_auditor.py --diff-base main`: 38 files, 378 candidates, 0 unsourced, exit 0 | This settles the current diff claim gate, not release readiness or legal accuracy |

The earlier 96-surface/538-candidate active-delivery result, 474/463 set counts
and 45 focused-test count remain prior-record summaries because their complete
raw outputs were not retained in the validation-readiness log. They are not used
as current exact-tree verification claims in this reconciliation.

## Ledger contradiction

N64 previously retained a 42-item result from the superseded tracked-renderable
proxy and still required final verification. N65 documented the corrected
active-delivery predicate but said exact verification remained pending. The raw
exact-commit reruns now establish that N65's implementation and verification are
complete and the current claim-diff gate passes. N64 remains partially addressed
because it explicitly carries other release blockers and does not authorise a
release. No product, efficacy, commercial or public-claim item is closed.

## Unresolved evidence

The fail-before detailed error list and original subagent transport records were
not retained independently. This does not change the final pack pass, mutation
controls or current gates, but those narrower historical details remain partial.
Public transaction evidence, willingness to pay, buyer acceptance, technical
efficacy and legal conclusions remain unresolved.
