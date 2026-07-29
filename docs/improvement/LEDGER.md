# Open-items ledger

**The single durable record of what is open.** Created 29 July 2026.

Before this file existed, the only good ledger lived in a consolidated handover
on the Windows filesystem, outside the repository, and was deleted when it was
superseded. `OWNER_ACTIONS.md` carries owner-facing detail but uses its own
numbering, which does not correspond to the decision numbers used in session
records. This file is the continuity baseline. Reproduce it verbatim in every
consolidated session record.

**Rules for this file.**

- Nothing drops off because it stopped being mentioned. An item leaves only
  when it is closed with evidence, and the evidence is named here.
- Every status names the commit or the command that establishes it.
- Every figure states the commit **and the tree** it was measured in. Finding
  N1 established that `--diff-base` figures were tree-dependent; they are not
  any more, but the habit of stating the tree stays.
- No relative day counts. "Four days from now" rots the moment the file is
  read again. State the date.
- No figure whose apparatus is gone. If a number cannot be re-derived by a
  committed command, either re-derive it or replace it with the command.

---

## 1. Findings

| ID | What it is | First raised | Status |
|---|---|---|---|
| **F25** | `CITATION_WORDS` accepts ordinary prose (`source`, `see`, `ref`, `reference`) as provenance. Tested at `claim_auditor.py:490`, before the `file-ref` arm at `:499`, and first match wins, so a real file citation is masked by the word next to it. | 2026-07-28 16:09 (`0e1f509`) | **OPEN.** Complete table exists. The exposure figure **22 / 46** does not reproduce: the script that produced it was never committed and an independent re-measurement on the same corpus at the same commit gave 29 / 53. Owner decision 3 is posed against the unreproducible number. Sharpest public instance: the words "Open Source" in `<title>` of `site/index.html` source that page's `13 frameworks` claim. Demonstrated a second time on 2026-07-29 when the first draft of `tests/test_tracked_citation.py` used "See ..." in a fixture sentence and passed for that wrong reason. |
| **F29** | 387 does not reproduce, 386 does; the blog also says 389. | 2026-07-28 17:01 (`431a7d3`) | **OPEN. Unacted across four sessions.** Deferred to Session B each time, never begun. Nothing in this session touched it. |
| **F30** | Allowlist entries suppress the whole paragraph, not the matched claim. `scan_file` tests each allowlist pattern against `claim_line`, `claim.snippet` **and `para`**, so one match exempts every claim in the paragraph. | 2026-07-28 17:01 (`431a7d3`) | **OPEN. Unacted across four sessions.** Measured instance 2026-07-29: on `site/regions/uae.html` the pattern `\bregula[- ]ai\b` matches the product name inside a terminal demo block and thereby exempts the whole `<pre>`. This remains the strongest continuity finding in the ledger. |
| F31 | Delta-log JSON Schema existed but nothing validated entries against it. | 2026-07-29 11:18 | **CLOSED** in `0990441`. Verified 2026-07-29: `tests/test_delta_log_schema.py` 14 passed, control plants the two real defects. |
| F32 | `strip_noise` blanked command citations, so the gate erased the evidence form it recommends. | 2026-07-29 12:38 | **CLOSED** in `e2b238c`, regression pair hardened in `4aa0f8d`. Verified 2026-07-29 by reverting the hunk in a worktree: 3 failed / 6 passed reverted, 9 passed with the fix. |
| **N1** | A citation resolved against the **working tree** (`(REPO_ROOT / ref).exists()`), so a gitignored file counted as provenance locally and vanished in CI. Commit `4aa0f8d` scored **276** unsourced in the main tree and **277** in a clean worktree. | 2026-07-29 (review) | **CLOSED** in `bebe255`. One predicate `ref_is_tracked()` serves all three call sites. Both trees report **281** at `3939949` (`python3 scripts/claim_auditor.py --diff-base main`, run in the main tree and in a clean worktree). Covered by `tests/test_tracked_citation.py`, 13 tests; two-way control, 5 fail with the fix reverted. |
| **N2** | `docs/MODEL_CARD.md:145` publishes "13 domain-gated, 4 AI-gated, 3 pattern gaps, so 17 of 20 misses are gate behaviour", citing `benchmarks/synthetic/RECALL.json`. That artefact shows 6 recovered by domains, 7 by AI-import, **7 never recovered** against 3 claimed pattern gaps. `STATE.md:892` says 8 remain unexplained. The published number understates pattern-side exposure. | 2026-07-29 (review) | **OPEN. NOT STARTED.** Queued as the lead item of the next scope. Published surface, so the fix is prepared and held for approval rather than pushed. |
| **N3** | No open-items ledger existed in the repository. | 2026-07-29 (review) | **CLOSED** by this file, `8c8f44c`. |
| **N4** | A session record stated the 30 July standards enquiry window "has now passed" when it closed the following day. | 2026-07-29 (review) | **CLOSED as a record defect**; the repo copy in `OWNER_ACTIONS.md` 5a was always correct. **The underlying owner action remains open**: `prEN 18228` and `prEN 18282` closed **30 July 2026**. Whether it was met is unrecorded. |
| **N5** | Withdrawn recall rows `14/30 = 47%` and `19/30 = 63%` sit unflagged at `STATE.md:884` while `benchmarks/headtohead/RESULTS-synthetic-v2-2026-07-28.md:38-39` marks them `[NOT REPRODUCIBLE]` and `:189` marks 63% WITHDRAWN. They are the basis of N2's wrong split. | 2026-07-29 (review) | **OPEN. NOT STARTED.** Goes with N2. |
| **N6** | `site/llms-full.txt` is on the published-surface manifest (`data/published_count_manifest.json`) yet the claim auditor never scans it: `.txt` is outside `SCANNED_SUFFIXES = {".md", ".markdown", ".html", ".htm"}`. A designated published surface is invisible to the gate that exists to police published surfaces. | 2026-07-29 | **OPEN.** Measurement rule 5: the gate tests something narrower than the standard. Belongs to the gate-scope repair. |
| **N7** | `SHORT_DURATION` (`claim_auditor.py:111`) exempts any bare `N seconds/minutes/ms` as "UX copy, not statistical claims", and therefore exempts genuine published performance claims. Measured instances: `site/regions/uae.html:416` publishes "From pip install to a categorised, article-cited finding in under 10 seconds"; `docs/QUICKSTART.md:7` publishes "Regula tells you where you stand in 10 seconds". Neither is measured anywhere in the repo. | 2026-07-29 | **OPEN, owner ruling needed.** Is a published performance claim UX copy? Deliberately not patched: changing the exemption is a gate-scope decision. |
| **N8** | Regulatory currency movement partly unapplied. `OMNIBUS_OJ_DATE` was correctly flipped to `2026-07-24` and `OMNIBUS_IN_FORCE_DATE` derives `2026-07-27`, but tracked files still carry the phrase "pending OJ publication". **14 tracked files contain it; 13 once `CHANGELOG.md` and `content/regulations/delta-log/` are excluded**, both of which legitimately record what was true on a past date. Count produced by the predicate: `git ls-files -z \| xargs -0 grep -ln "pending OJ publication" \| grep -vE "CHANGELOG\|delta-log" \| wc -l`. | 2026-07-29 | **OPEN, needs triage.** The script and test occurrences are conditional else-branches and are correct to keep. The reference data, the committed benchmark artefacts and the user-facing example are stale output and are not. A regulatory content sweep, not apparatus. |
| **N9** | **Article 50 transparency duties for new systems apply from 2 August 2026**, unchanged by the Omnibus (`content/regulations/delta-log/entries/2026-07-24-oj-publication.json`, quoting the OJ text). No session in this programme surfaced this until 29 July 2026. | 2026-07-29 | **OPEN, live deadline: 2 August 2026.** Stated as a date, not a countdown, because a countdown rots. A day-count defect in the 29 July consolidated record said "three days" from 29 July; the correct interval is four days, and `git ls-files -z \| xargs -0 grep -n "three days"` confirms **no tracked file carries the wrong count** (the seven tracked hits all describe the genuine three-day OJ-to-in-force gap, 24 to 27 July). |
| **N10** | `NUMERIC_CLAIM` does not match unseparated numbers of four or more digits. MEASURED 2026-07-29: `"The suite collects 2452 tests."` yields no match; `"2,452 tests"` yields one; `"12345 tests"` yields none. A published count written without a thousands separator is invisible to the gate. | **2026-07-29 (this session)** | **OPEN.** Found by the fixture precondition in `tests/test_claim_diff.py`, not by looking for it. No tracked published surface currently relies on it (`git ls-files -z \| xargs -0 grep -nE "[^,0-9][0-9]{4} (tests\|commands\|patterns\|files\|findings)"` returns only CHANGELOG and script comments). Widening the regex is a gate-scope change, so not done here. |
| **N11** | The custom runner wiring rule in `.claude/rules/tests.md` says new test files must be wired into `tests/test_classification.py`. MEASURED 2026-07-29: **89 test files on disk, 22 wired, 67 not**, including `test_command_citation.py`, `test_delta_log_schema.py`, `test_tracked_citation.py` and `test_claim_diff.py`. The rule has not been followed for some time. | **2026-07-29 (this session)** | **OPEN.** Not fixed here: the existing filter excludes only pytest fixtures, so binding a parametrized test such as `test_bucket_predicate` would break the runner. Wiring the backlog needs the filter extended to parametrized tests, which is shared test infrastructure and a scope of its own. |
| **Merge-base measurement** | For each finding `--diff-base main` reports at HEAD, does the same claim exist at the merge base? Decides whether an introduced-claim condition alone can unblock the merge. | 2026-07-29 (review) | **CLOSED, this session.** `python3 scripts/claim_diff.py --base main`, main tree. At `b310821`: 278 findings, 55 at merge base, 223 introduced. At `3939949`, the commit that landed this work: **281 findings, 55 at merge base, 226 introduced.** Buckets at `3939949`, total / at-base / introduced: `docs/improvement/` 203 / 0 / 203; `benchmarks/ + docs/benchmarks/` 67 / 55 / 12; `.claude/rules/` 8 / 0 / 8; `everything else` 3 / 0 / 3. **Answer: an introduced-claim condition alone would NOT unblock the merge.** It removes 55 and leaves 226. **The `everything else` 3 are `docs/adr/0001-claim-identity.md`** (two illustrative figures at L34, one superlative at L101). Writing the ADR about claim identity added three claims to the corpus that measures claims. That is the self-referential loop again, recorded rather than fixed: the bucket predicate was deliberately NOT amended to reclassify `docs/adr/` as a working document, because changing a predicate so that a file the author just created stops counting is the move this programme exists to catch. |
| **Gate scope repair** | `--diff-base` scans whole files rather than introduced claims. | 2026-07-28 | **OPEN. Not started in four consecutive sessions, but its design is now decided by measurement rather than argument.** Bucket figures re-derived at `3939949` in the main tree by `python3 scripts/claim_diff.py --base main`, produced by the same predicate that enumerates the set: **203 of 281 findings are `docs/improvement/`**, 67 are `benchmarks/ + docs/benchmarks/`, 8 are `.claude/rules/`, 3 are `docs/adr/`. The previous "201 of 277" mixed a bucket count taken at 276 in the pre-N1 main tree with a post-fix total, and is withdrawn. **What each candidate condition achieves, from the same run at `3939949`:** introduced-claim alone, 281 to **226** (removes 55, 19.6%); published-surface alone, 281 to **70**; both together, 281 to **15**. At `b310821` the same three figures were 223, 67 and 12; the difference is the three ADR findings. **Recommendation: implement both, and treat the published-surface condition as the load-bearing one.** The introduced-claim condition is worth having because it is what stops a one-line edit inheriting a document's whole backlog, but on this branch it is nearly inert, because the branch created the documents. |
| F21 | Self-citation via canonical URL. | 2026-07-28 09:48 | CLOSED (`b954ecf`). Not independently re-verified. |
| F22 | The 0.5 magnitude floor. | 2026-07-28 16:09 | CLOSED (`0e1f509`). Not independently re-verified. |
| F24 | Recall underivability. | 2026-07-28 16:09 | CLOSED (`0e1f509`). Not independently re-verified. |
| F26 | Branch red for six commits under a collect count. | 2026-07-28 16:09 | CLOSED (`0e1f509`). Not independently re-verified. |
| F27 | F8 not supported by a like-for-like comparison. | 2026-07-28 16:09 | CLOSED (`0e1f509`). Not independently re-verified. |
| F28 | `cascade_count --check` was a blank gate. | 2026-07-28 16:09 | CLOSED (`0e1f509`). Not independently re-verified. |

---

## 2. Owner decisions

"Ruled but unapplied" is called out explicitly: the owner has already answered
these and the answer has not been encoded.

| # | Decision | Raised | Status |
|---|---|---|---|
| 1 | Ratify or reject the quarantine sensitivity-admissions mechanism | 2026-07-28 | **RULED, UNAPPLIED, four sessions.** Owner ratified with three conditions to encode as tests. Not encoded. Nothing in this session touched it. |
| 2 | Ratify or reject the F14 deviation on Articles 11 and 12 | 2026-07-28 | **RULED, UNAPPLIED, four sessions.** Owner gave a split ruling: reject for the `article_11` Omnibus route, ratify for `owasp_agentic`. Not applied. Nothing in this session touched it. |
| 3 | Scope F25 and F30 | 2026-07-28 | **OPEN, and currently unanswerable.** Posed against 22 / 46, which does not reproduce. Re-measure with a committed script first, the way `scripts/claim_diff.py` was committed for the merge-base question. |
| 4 | Rule on F29: 387 or 386, and does the blog's 389 get corrected | 2026-07-28 | **OPEN.** Deferred to Session B four times. |
| 5 | Sign off the English provenance sentence for the DE and PT-BR panels | 2026-07-28 | **OPEN.** Untouched. |
| 6 | Approve or reject the agentic AI draft before publication | 2026-07-29 | **OPEN.** `content/blog/article-agentic-ai-annex-xiv.md`, tracked, `published: false`, never human-reviewed. Its description asserts that "agentic" appears exactly once in Regulation (EU) 2026/1744, corroborated by a direct-quote extraction but never counted literally. |
| 7 | Whether `docs/improvement/` belongs in the CI claim gate | 2026-07-29 | **WITHDRAWN by the owner, and the merge-base measurement now forces it back open.** It was withdrawn on the grounds that the gate repair's design would answer it. The measurement says the design cannot avoid it: 203 of 281 findings are `docs/improvement/` and every one is branch-introduced, so no introduced-claim condition excludes them. Only a scope condition does, and that condition is decision 7 restated. **Recommend reopening.** |
| 8 | How CI should ever run on this branch | 2026-07-29 | **OPEN, and now understood.** `.github/workflows/ci.yaml` triggers only on push and pull request to `main` and has no `workflow_dispatch`. The rationale for not adding one, supplied by the owner 29 July: GitHub requires a `workflow_dispatch` workflow to be present **on the default branch** before the event can be triggered, so adding the trigger on this branch cannot enable dispatch, and the earlier HTTP 422 was the API reading main's copy. Getting it onto main requires a pull request, which is an owner decision. **No further engineering attempts should be made from this branch.** |

---

## 3. Standing owner items

DPVCG contribution post; recruit raters 2 and 3; Zenodo account and DOI
decision; BSI ART/1 route; GSC re-auth (`invalid_grant`); private remote for
`getregula-internal/`; the Phase 1.5b residuals; the **20 August 2026**
`prEN 18229-1` enquiry window; **Article 50 for new systems, 2 August 2026**
(N9).

---

## 4. Deferred sessions

- **Session B**. F29 unit reconciliation; agentic draft humanising and
  validation. Deferred on the grounds that both are content corrections better
  verified by the repaired gate than the current one.
- **Session C**. Repository restructure to public-repo standard. Deferred as
  the largest diff, and because it moves the paths every recorded measurement
  is keyed to.

---

## 5. Programme phase status

| Phase | Status |
|---|---|
| Phase 0 baseline | DONE |
| Phase 1 code review | DONE |
| Phase 1.5 apparatus repair | DONE |
| Phase 1.5b claim provenance | DONE, partial |
| Phase 1.5c | DONE |
| Class 1 landing-page derivation | DONE, 1 of 3 items, two residuals |
| Phase 2 | **FAILED validation, loop 1 of 3** |
| Phase 4 | **FAILED hostile review, loop 2 of 3** |
| Phase 1.7 | NOT STARTED |
| Phases 5 to 8 | NOT STARTED |

Neither Phase 2 nor Phase 4 has passed its gate. The Phase 4 plan must not be
executed. `BASELINE.md` section 11 reportedly still contradicts itself (52.3 or
52.6); not re-checked.
