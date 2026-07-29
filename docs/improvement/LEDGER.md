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

---

## 1. Findings

| ID | What it is | First raised | Status |
|---|---|---|---|
| **F25** | `CITATION_WORDS` accepts ordinary prose (`source`, `see`, `ref`, `reference`) as provenance. Tested at `claim_auditor.py:490`, before the `file-ref` arm at `:499`, and first match wins, so a real file citation is masked by the word next to it. | 2026-07-28 16:09 (`0e1f509`) | **OPEN.** Complete table exists. The exposure figure **22 / 46** does not reproduce: the script that produced it was never committed and an independent re-measurement on the same corpus at the same commit gave 29 / 53. Owner decision 3 is posed against the unreproducible number. Sharpest public instance: the words "Open Source" in `<title>` of `site/index.html` source that page's `13 frameworks` claim. Demonstrated again on 2026-07-29 when the first draft of `tests/test_tracked_citation.py` used "See ..." in a fixture sentence and passed for that wrong reason. |
| **F29** | 387 does not reproduce, 386 does; the blog also says 389. | 2026-07-28 17:01 (`431a7d3`) | **OPEN. Passed over in silence for three sessions.** Deferred to Session B each time. |
| **F30** | Allowlist entries suppress the whole paragraph, not the matched claim. `scan_file` tests each allowlist pattern against `claim_line`, `claim.snippet` **and `para`**, so one match exempts every claim in the paragraph. | 2026-07-28 17:01 (`431a7d3`) | **OPEN. Raised three times, unaddressed three times.** Measured instance 2026-07-29: on `site/regions/uae.html` the pattern `\bregula[- ]ai\b` matches the product name inside a terminal demo block and thereby exempts the whole `<pre>`. This is the strongest continuity finding in the ledger. |
| F31 | Delta-log JSON Schema existed but nothing validated entries against it. | 2026-07-29 11:18 | **CLOSED** in `0990441`. Independently verified 2026-07-29: `tests/test_delta_log_schema.py` 14 passed, control plants the two real defects. |
| F32 | `strip_noise` blanked command citations, so the gate erased the evidence form it recommends. | 2026-07-29 12:38 | **CLOSED** in `e2b238c`, regression pair hardened in `4aa0f8d`. Independently verified 2026-07-29 by reverting the hunk in a worktree: 3 failed / 6 passed reverted, 9 passed with the fix. |
| **N1** | A citation resolved against the **working tree** (`(REPO_ROOT / ref).exists()`), so a gitignored file counted as provenance locally and vanished in CI. The same commit `4aa0f8d` scored **276** unsourced in the main tree and **277** in a clean worktree. | 2026-07-29 (review) | **CLOSED, this session.** One predicate `ref_is_tracked()` now serves all three call sites (`claim_auditor.py:358`, `:374`, `:548`). Both trees now report **277** at `4aa0f8d`, claims unchanged at 906. Cost was **+1 finding**, exactly as predicted; the +1 is `docs/improvement/PLAN-PHASE4-v2.md` 18 to 19, and it is the finding CI would already have reported. Covered by `tests/test_tracked_citation.py` (13 tests); two-way control run, 5 fail with the fix reverted. |
| **N2** | `docs/MODEL_CARD.md:145` publishes "13 domain-gated, 4 AI-gated, 3 pattern gaps, so 17 of 20 misses are gate behaviour", citing `benchmarks/synthetic/RECALL.json`. That artefact shows 6 recovered by domains, 7 by AI-import, **7 never recovered** against 3 claimed pattern gaps. `STATE.md:892` says 8 remain unexplained. The published number understates pattern-side exposure. | 2026-07-29 (review) | **OPEN. NOT STARTED.** Scope Item 2, not reached this session. Published surface. |
| **N3** | No open-items ledger existed in the repository. | 2026-07-29 (review) | **CLOSED** by this file. |
| **N4** | A session record stated the 30 July standards enquiry window "has now passed" when it closed the following day. | 2026-07-29 (review) | **CLOSED as a record defect** (the repo copy in `OWNER_ACTIONS.md` 5a was always correct and flags it time-critical). **The underlying owner action remains open**: `prEN 18228` and `prEN 18282` closed **30 July 2026**. Whether it was met is unrecorded. |
| **N5** | Withdrawn recall rows `14/30 = 47%` and `19/30 = 63%` sit unflagged at `STATE.md:884` while `benchmarks/headtohead/RESULTS-synthetic-v2-2026-07-28.md:38-39` marks them `[NOT REPRODUCIBLE]` and `:189` marks 63% WITHDRAWN. They are the basis of N2's wrong split. | 2026-07-29 (review) | **OPEN. NOT STARTED.** Scope Item 2, not reached. |
| **N6** | `site/llms-full.txt` is on the published-surface manifest (`data/published_count_manifest.json`) yet the claim auditor never scans it: `.txt` is outside `SCANNED_SUFFIXES = {".md", ".markdown", ".html", ".htm"}`. A designated published surface is invisible to the gate that exists to police published surfaces. | **2026-07-29 (this session)** | **OPEN.** Measurement rule 5: the gate tests something narrower than the standard. Belongs to the deferred gate-scope repair, not to a one-file patch. |
| **N7** | `SHORT_DURATION` (`claim_auditor.py:111`) exempts any bare `N seconds/minutes/ms` as "UX copy, not statistical claims". It therefore exempts genuine published performance claims. Measured instance: `site/regions/uae.html:416` publishes "From pip install to a categorised, article-cited finding in under 10 seconds", and `docs/QUICKSTART.md:7` publishes "Regula tells you where you stand in 10 seconds". Neither is measured anywhere in the repo; both are exempt by design. | **2026-07-29 (this session)** | **OPEN, owner ruling needed.** Is a performance claim UX copy? Deliberately not patched: changing the exemption is a gate-scope decision. |
| **N8** | Regulatory currency movement partly unapplied. `OMNIBUS_OJ_DATE` was correctly flipped to `2026-07-24` and `OMNIBUS_IN_FORCE_DATE` derives `2026-07-27`, but tracked files still carry the phrase "pending OJ publication". **14 tracked files contain it; 13 once `CHANGELOG.md` and `content/regulations/delta-log/` are excluded**, both of which legitimately record what was true on a past date. Counts produced by the predicate, not read off a listing: `git ls-files -z \| xargs -0 grep -ln "pending OJ publication" \| grep -vE "CHANGELOG\|delta-log" \| wc -l`. The 13 are `benchmarks/results/{instructor,langchain,pydantic-ai}.json`, `examples/cv-screening-app/README.md`, `references/{article_obligations.yaml,eu_ai_act_articles_9_15.md,jurisdictions/eu_ai_act.yaml}`, `scripts/{explain.py,explain_articles.py,omnibus.py,report.py,timeline.py}`, `tests/test_omnibus_status.py`. | **2026-07-29 (this session)** | **OPEN, needs triage.** The script and test occurrences are conditional else-branches, which are correct to keep. The reference data, the committed benchmark artefacts and the user-facing example are stale output and are not. Not fixed here: it is a regulatory content sweep, not apparatus, and mixing the two would put a content change inside an apparatus commit. |
| **N9** | **Article 50 transparency duties for new systems apply from 2 August 2026, unchanged by the Omnibus** (`content/regulations/delta-log/entries/2026-07-24-oj-publication.json`, quoting the OJ text). That is four days after this ledger was written. No session in this programme has tracked it. | **2026-07-29 (this session, prompted by owner)** | **OPEN, live deadline.** Not a repo defect; a regulatory date the product speaks to and the programme has not surfaced. |
| **Parallel-path guard** | No mechanism asserts that a figure published on one surface agrees with the same figure on every other surface. Six instances of a published figure disagreeing with its own source have now been recorded. | 2026-07-28 | **OPEN. NOT STARTED.** Scope Item 2 asked for a manifest-sourced agreement guard with a planted-disagreement control. Not reached this session. |
| **Merge-base measurement** | For each of the 277 findings, does the same claim exist at the merge base with `main`? Decides whether an introduced-claim condition alone can unblock the merge, or whether only a published-surface condition can, which would reopen owner decision 7. | 2026-07-29 (review) | **OPEN. NOT STARTED.** Scope Item 3, not reached this session. This is the measurement that decides the gate-scope repair's design. |
| **Gate scope repair** | `--diff-base` scans whole files rather than introduced claims. 201 of 277 findings are the programme's own working documents. | 2026-07-28 | **OPEN. Not started in four consecutive sessions.** Deliberately out of scope until the merge-base measurement above answers its design question. |
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
| 1 | Ratify or reject the quarantine sensitivity-admissions mechanism | 2026-07-28 | **RULED, UNAPPLIED, three sessions.** Owner ratified with three conditions to encode as tests. Not encoded. |
| 2 | Ratify or reject the F14 deviation on Articles 11 and 12 | 2026-07-28 | **RULED, UNAPPLIED, three sessions.** Owner gave a split ruling: reject for the `article_11` Omnibus route, ratify for `owasp_agentic`. Not applied. |
| 3 | Scope F25 and F30 | 2026-07-28 | **OPEN, and currently unanswerable.** Posed against 22 / 46, which does not reproduce. Re-measure first. |
| 4 | Rule on F29: 387 or 386, and does the blog's 389 get corrected | 2026-07-28 | **OPEN.** Deferred to Session B three times. |
| 5 | Sign off the English provenance sentence for the DE and PT-BR panels | 2026-07-28 | **OPEN.** Untouched. |
| 6 | Approve or reject the agentic AI draft before publication | 2026-07-29 | **OPEN.** `content/blog/article-agentic-ai-annex-xiv.md`, tracked, `published: false`, never human-reviewed. Its description asserts that "agentic" appears exactly once in Regulation (EU) 2026/1744, which is corroborated by a direct-quote extraction but has never been counted literally. |
| 7 | Whether `docs/improvement/` belongs in the CI claim gate | 2026-07-29 | **WITHDRAWN by the owner; withdrawal still unapplied.** No corresponding entry exists in `OWNER_ACTIONS.md`. **Likely to reopen**: if the merge-base measurement shows the 201 working-document findings are branch-introduced, only a published-surface condition unblocks the merge, and that condition is decision 7 by another name. |
| 8 | How CI should ever run on this branch | 2026-07-29 | **OPEN.** `.github/workflows/ci.yaml` triggers only on push and pull request to `main`, and has no `workflow_dispatch`. The full 3.10 to 3.13 matrix has never executed against this branch. Adding `workflow_dispatch` was explicitly prohibited by the 29 July scope; the reason given was "see the note at the end", and no such note was present. **The prohibition is being honoured and its rationale is unrecorded.** |

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
