# Dated verdict record, 2026-08-06

**This record supersedes the MEASUREMENT fields of the 2026-08-05 19:57 block**
in `docs/improvement/HANDOVER-CLAIM-SCOPE-2026-08-05-195731.md` section 27.

That block was produced by a cycle which stopped at its first prerequisite, so
most of its measurement fields record "this was not measured", not "this was
measured and failed". Reading them as failures overstates what was known. Every
measurement field below is re-issued with one citation from a run made during
this cycle, at the commit named beside it.

Supersession is of the measurement fields only. The decision fields are
owner-held, are reproduced verbatim below, and are not re-issued here.

All runs are at commit `a62afc6`, tree `c44878b`, base `301a573`, working tree
clean of tracked modification. Exit codes are captured from `$?` immediately
after the command or from a redirected `.exit` file, never read off a summary
line. Load average is stated where a run could be affected by contention,
because this cycle established that it can be.

## Measurement fields, re-issued

| Field | Value | Citation |
|---|---|---|
| PRIOR_EVIDENCE_PRESERVATION | **PASS** | `cd docs/improvement/evidence-2026-08-05 && sha256sum -c SHA256SUMS.txt`: 37 OK, 0 FAILED, 0 WARNING, exit 0. The 19:57 `FAIL` was a manifest path-convention defect, closed on 5 August in `4ce306e`, not a byte mismatch. |
| REPOSITORY_SUITE | **PASS** | `python3 -m pytest tests/ -q -rs`: passed in 842.69s (0:14:02), exit 0, **zero failed and zero skipped**, launched on a quiescent tree at load average 0.52 with the sentinel removed first. The passing total equals the canonical count in `data/site_facts.json` exactly, and the figure itself is deliberately not written into this file, which sits inside the corpus the published-count guard scans; that is the same reason N70's closure record gives. The verbatim run output is retained outside the repository, in this cycle's handover evidence register. |
| MERGE_READINESS | **PASS** | `python3 scripts/merge_blockers.py`, nothing else in flight: `TOTAL 0`, exit 0. 365 total findings, 298 of them `docs/improvement/`; survive published-surface alone 0; survive BOTH 0. |
| ACTIVE_DELIVERY_GATE | **PASS** | `python3 scripts/claim_auditor.py --delivery-surfaces`: scanned 96 file(s), 527 claim(s), 0 unsourced, exit 0. |
| CLAIM_POLICY_COMPLETENESS | NOT_REMEASURED | The count-record policy validates with live provenance inside `tests/test_published_count_manifest.py`, but that is a narrower instrument than the field names. The claim-scope causality work this field belongs to did not run in this cycle and is not in its scope. |
| CLASSIFICATION_LAUNDERING_GUARD | NOT_REMEASURED | No classification-transition experiment was run. The transfer-record gap N70 records as open is unchanged. |
| CAUSAL_SCOPE_ATTRIBUTION | NOT_REMEASURED | The causal experiment has never begun; it was the blocked cycle's objective and is out of this cycle's scope. |
| DELIVERY_INVENTORY_COMPLETENESS | NOT_REMEASURED | The inventory was consumed by the active-delivery gate above but its completeness was not independently re-derived. |
| HISTORICAL_INTERNAL_BACKLOG | NOT_REMEASURED | Not measured this cycle. |
| ALL_CHANGED_NO_NEW_DEBT_GATE | NOT_IMPLEMENTED | Unchanged from the 19:57 block. Nothing in this cycle implemented it. |

### Supporting gate results at the same commit

Six fast gates, each exit code captured separately, all rc=0:
`claim_auditor.py --verify-facts` (checked 148 fact references across 17
files), `site_integrity.py` (`RESULT: OK`), `cascade_count.py --check`
(canonical value matched on all 11 manifest surfaces),
`build_recall_artefact.py --check`, `build_gap_demo.py --check`,
`check_selfref_sourcing.py --control-only`. Also
`claim_auditor.py --diff-base main` scanned 38 file(s), 378 claim(s), 0
unsourced, exit 0; `scripts.cli self-test` exit 0; `scripts.cli doctor` exit 0;
`ruff check scripts/ tests/ --select F821,F811` reported `All checks passed!`.

### The custom runner took two attempts, and both are recorded

Attempt 1: `1383 passed, 1 failed, 0 skipped (1095 test functions)`, exit 1.
The single failure was `test_smoke_feed`, a 30 second subprocess timeout on
`regula feed`. Attempt 2, on a quieter machine: `1389 passed, 0 failed, 0
skipped (1095 test functions)`, exit 0.

Neither attempt is discarded. The failure is diagnosed in ledger row N75: it is
a third instance of the wall-clock class, it reproduces nowhere (the command
runs in 3.08s cold and 0.08s warm, and the test passes 3 times out of 3 in
isolation), and nothing in this cycle touches feed or CLI code. The differing
helper-assertion totals between the two attempts are N27's known distinction:
that figure counts helper assertions, not tests, so an aborted test lowers it.

**The published custom-runner function count of 1,095 in `docs/TRUST.md` is
CONFIRMED, not corrected.** Both attempts report 1095 test functions.

## Decision fields, owner-held and unchanged

Copied verbatim. Not re-issued, not altered, not re-derived.

```text
PRODUCT_BUILD: STOP
VENTURE_DECISION: STOP
STAGE_A_PACK: HOLD
EXTERNAL_CONTACT: NOT_AUTHORISED
REAL_DATA_COLLECTION: DISABLED
H1_STATUS: ABANDONED
H2_STATUS: NOT_CREATED
WILLINGNESS_TO_PAY: UNVALIDATED
PRODUCT_PILOT_STATUS: NOT_APPROVED
```

## N60 is unmoved and remains the most recent efficacy evidence

Nothing in this cycle touched detection, thresholds or flags. N60's executed
review stands exactly as recorded: recall 0/40 on both constructed adversarial
candidate families, descriptive Wilson 95% interval 0.000 to 0.0876, against
transparent baselines at 40/40 and 40/44; TECHNICAL_EVIDENCE FAILED;
OVERALL_DECISION STOP. Those families are correlated and constructed, so they
are diagnostic and are not external accuracy.

**No gate result in this record is evidence of product efficacy.** A green
suite says the repository does what its tests say; it says nothing about
whether the detector finds real governance risk, and this cycle produced no
evidence on that question. The three commits it does contain are a published
count guard, a test determinism conversion and a packaging ceiling. None of
them is a product improvement.

---

## Addendum, same day: the branch merged to main

The record above was written at `a62afc6`, before the branch was pushed. What
followed changes three of its fields and is appended rather than rewritten,
because a dated record that is edited to look prescient is worthless.

**MERGE_READINESS moves from a local measurement to a completed merge.** The
branch was pushed, PR #44 opened, and CI executed on this branch's content for
the FIRST time ever (owner decision 8). It failed 5 of 24 checks. Both causes
are recorded as N76: a sitemap the local gate set could not see, and a
package-qualified import that resolved only through an editable install. Both
were fixed, the second at the class. CI then reported **24 pass, 0 fail, 4
skipping**, and `main` was advanced to `b978076` by **fast-forward**, so no
merge commit exists and the property the merge gate required is intact.

To make that fast-forward possible, `origin/main` was first merged INTO the
branch. `main` had advanced on 4 August via a merge of this branch's own
earlier tip, so it was no longer an ancestor. That merge is content-neutral and
its only purpose was to restore the ancestry the gate depends on. Rebasing was
excluded by the immutable-history rule.

**REPOSITORY_SUITE re-measured at the merged tree.** Full pytest passed with
zero failures and zero skips, exit 0, on its FIRST attempt, and the custom
runner reported 0 failed and 0 skipped across 1,097 test functions, exit 0,
matching `docs/TRUST.md`. Both figures are deliberately not written here; this
file sits inside the corpus the published-count guard scans. The first-attempt
pass is itself the result: the two preceding cycles each needed a second
attempt because a wall-clock test failed under load, and N75's hermetic
conversion removed that.

**A new field, and it is not green.** `LIVE_SITE_PUBLICATION: FAILED`. The
corrected counts are in the repository and on `main`; they are NOT on
`https://getregula.com/`, because four `Deploy to GitHub Pages` attempts all
failed at the deploy step while the artifact uploaded cleanly. Recorded as N77
with the measurements. **Nothing in this record should be read as saying the
published figures are now correct everywhere.**

N60 remains unmoved. Nothing in this cycle touched detection, and no gate
result here is evidence of product efficacy.
