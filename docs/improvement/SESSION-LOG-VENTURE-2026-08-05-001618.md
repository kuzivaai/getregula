# Regula venture research session, 2026-08-05 001618

Repository: `/home/mkuziva/getregula`

Research cut-off: 2026-08-04 23:59 Europe/London

Objective: determine whether Regula has a genuinely innovative, viable and
scalable venture path, without manufacturing positive evidence.

## Authority gate

Started: `2026-08-05T00:12:00+01:00` (approximate, before substantive research)

- Working directory: `/home/mkuziva/getregula`
- Workspace root: `/home/mkuziva/getregula`
- Filesystem: restricted workspace-write; repository content writable; `.git`
  read-only in the default sandbox.
- Approval: managed, with explicit escalation available.
- Network: web research connector available; unrestricted shell network is not
  assumed.
- Delegation: available. Only read-only research delegation is authorised.
- Concurrent writers: no other writer is intentionally delegated by this
  session; the shared workspace means another external process could write, so
  Git state must be checked before each commit.
- Applicable rule discovery: `find .. -name AGENTS.md -print` and the requested
  `.claude/rules` search returned no filesystem results. The user-supplied
  `AGENTS.md` in the conversation remains applicable.

The default-sandbox Git probe failed with exit 73:

```console
git_dir_writable=no
/bin/bash: line 3: .git/.codex-venture-research-probe-2: Read-only file system
```

The same scoped probe was rerun with user-approved unrestricted execution and
returned:

```console
git_dir_writable=yes
```

This resolved the mandated authority blocker. No substantive research occurred
before resolution.

## Work package 1 interim classification

Classification made after repository reads and corrected standalone mechanical
verification. It is version-bounded to checkout `a62e8aa` unless stated.

| Prior proposition | Classification | Basis |
|---|---|---|
| Regula is a local, open-source AI-governance indicator tool | CURRENT | README, security policy, trust pack, architecture and package metadata agree on the bounded core; optional network features remain separate. |
| Regula does not determine legal classification, compliance or applicable obligations | CURRENT in corrected repository and site copy | README and current site use the indicator and human-review boundary. The retained PyPI/public-package wording is contradictory and is recorded in the claim register. |
| TECHNICAL_EVIDENCE FAILED | CURRENT controlling commercial verdict, VERSION_BOUND measurement | The verdict remains in current state. Underlying evaluation is bound to frozen product commit `94efa9e`; it is not a measurement of later changes. |
| COMPARATIVE_ADVANTAGE NOT_DEMONSTRATED | CURRENT | No equivalent independently labelled real-repository comparison exists. |
| DEMAND_EVIDENCE UNVALIDATED | CURRENT | No human or paid evidence was added in the inspected repository records. |
| OVERALL_DECISION STOP | CURRENT | Current state, ledger, commercial review and summary agree. Reasoning alone cannot change it. |
| PRODUCT_PILOT_STATUS NOT_APPROVED | CURRENT | Current ledger and improvement records agree. |
| Local Candidate A and B each detected 0/40 positives | REPRODUCED from retained result data, VERSION_BOUND | Recalculated from `summary.json`: each has TP 0, FN 40, recall 0, Wilson 95% `[0, 0.08762160119728664]`. |
| Transparent baselines detected 40/40 for A and B | REPRODUCED from retained result data, VERSION_BOUND | A: precision 40/44 = 0.9091, recall 40/40 = 1.0. B: precision 40/40 = 1.0, recall 40/40 = 1.0. Recall Wilson 95% is approximately `[0.9123784, 1]`. Transformations are correlated and do not establish external accuracy. |
| Independently human-labelled real repositories exist | CONTRADICTED | Result summary records `human_labelled: 0`; comparator accuracy is explicitly UNTESTABLE. |
| Paid tiers and scalable delivery are validated | CONTRADICTED | Pricing page marks paid tiers coming soon; commercial records contain no paid validation. |
| Evidence-readiness for small AI suppliers is the strongest current hypothesis | CURRENT as a hypothesis only | It appears in the pilot packet and Phuluso working documents, but has no human or paid validation. |
| Technical depth is equal across languages | CONTRADICTED | Architecture records deep Python AST, moderate optional JS/TS analysis, and regex/import-level analysis for Java, Go, Rust, C and C++. |
| Passing tests proves customer value or legal accuracy | CONTRADICTED | Repository trust and commercial records explicitly reject that inference. |
| Public claim-integrity work is complete | UNVERIFIED and likely stale as a repository-wide statement | The active branch contains a claim-correction commit, but is ahead of `main`; ledger N65 says exact final verification remained pending. No repository-wide conclusion is justified here. |
| Current counts | REPOSITORY_MEASURED | `site_facts.json`: 62 commands, 419 tier regexes, 722 broad grand-total patterns, 13 framework crosswalks, 8 language families, 2,690 pytest-collected tests. Counts answer different questions and are not interchangeable. |

### Failed verification path

The first commercial-result checker assumed both local and baseline JSON rows
used the key `wilson95`. Baseline rows use `recall_wilson95`. The checker raised
`KeyError` after Candidate A. A semicolon-separated logging command later exited
zero because a subsequent `rg` succeeded, masking the intermediate failure.
The checker was corrected to accept the two documented schemas, compare values
with a tight absolute tolerance, and was rerun alone through the logger. The
standalone run exited zero and is retained above. This failure changes no
product result but demonstrates why material verification commands must not be
masked by later shell segments.

## Complete improvement ledger

Started: `2026-08-05T00:16:55+01:00`

Command:

```console
$ bash -lc 'cat docs/improvement/LEDGER.md'
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
- **The `--diff-base` total has no fixed point and chasing it is the bug.**
  This file and `docs/improvement/STATE.md` are inside the corpus the gate
  measures, so every edit to them moves the number they record. Observed on
  2026-07-29 across four commits: 278 at `b310821`, 281 at `3939949` after an
  ADR landed, 278 again at `7b78f2e` after a STATE.md edit added file
  references that sourced paragraphs. Each is correct at its commit. State the
  commit, do not reconcile them, and do not re-edit the ledger to make the
  latest figure match.
- **Supersession is declared, not written in prose.** When a row establishes
  that an earlier row's statement was wrong or retracted, the newer row carries
  `SUPERSEDES:<id>` and the older row carries `SUPERSEDED-BY:<id>`, both ways,
  and `tests/test_ledger_status.py` fails on any unpaired declaration. A
  sentence like "which rows N15 and N18 supersede" is a statement about this
  file and nothing can check it; that is how N13 carried a stale headline
  through two sessions. **This marker is NOT for a figure that merely moved.**
  Under the rule immediately above, a number that changed because the corpus
  changed is correct at its own commit and is not superseded. Reserve the
  marker for a statement that was WRONG or has been WITHDRAWN.
- **A status may not name a commit that cannot establish it.** A docs-only
  commit does not close a code defect. Six rows in section 1 named the commit
  that RECORDED a finding as the commit that FIXED it; corrected 2026-07-30
  against `git log -S`, see N22. No test enforces this, and why not is stated
  in N22.

---

## 1. Findings

| ID | What it is | First raised | Status |
|---|---|---|---|
| **F25** | `CITATION_WORDS` accepts ordinary prose (`source`, `see`, `ref`, `reference`) as provenance. Tested before the `file-ref` arm, and first match wins, so a real file citation is masked by the word next to it. **The ordering is the claim; the line numbers are not.** Recorded as 490/499, then as 544/553, and at 2026-07-30 they are 543 and 548. `scripts/f25_exposure.py` re-derives them from the source on every run so the record cannot go stale a third time. **SUPERSEDED-BY:N26** on its exposure figure. | 2026-07-28 16:09 (`0e1f509`) | **OPEN, and no longer unmeasured. See N26 for the figures and `scripts/f25_exposure.py --recover` for the apparatus.** The exposure figure **22 / 46** does not reproduce, and neither does the 29 / 53 offered against it; both are WITHDRAWN as unreproducible. The real exposure on the gate's own corpus is **91 suppressed findings** and **215 of 279 citation-word paragraphs with no other provenance**. Sharpest public instance: the words "Open Source" in `<title>` of `site/index.html` source that page's `13 frameworks` claim. Demonstrated a second time on 2026-07-29 when the first draft of `tests/test_tracked_citation.py` used "See ..." in a fixture sentence and passed for that wrong reason. |
| **F29** | 387 does not reproduce, 386 does; the blog also says 389. | 2026-07-28 17:01 (`431a7d3`) | **SETTLED 2026-07-30 ON THE MEASUREMENT, after SEVEN deferrals, in PUSHED:4335831. BOTH FIGURES ARE CORRECT AND THE DISPUTE WAS NEVER ABOUT UNITS.** The unit is **tier regexes**: the sum of the `patterns` lists across the tier dictionaries in `scripts/risk_patterns.py`. Two trees both call themselves v1.7.0. The **`v1.7.0` tag is `7fa2088`, 16 April 2026, and counts 386.** **Commit `c6aa67a`, 23 April 2026, still carries version 1.7.0 and counts 387**, and it is the tree the 10-app re-scan actually ran on, per `benchmarks/results/blog_scan_2026_04/README.md`. So 387 never failed to reproduce; it was being sought in the wrong tree. **Measured at each tree by TWO INDEPENDENT METHODS that agree**, in detached worktrees removed afterwards: that tree's own `scripts/site_facts.py`, and a direct sum over the tier dictionaries that does not use `site_facts` at all. Full unit set at the tag: **52 / 386 / 182 / 17 / 38 / 10 / 4 / 4 / 18 / 659 / 446**. At 23 April: **52 / 387 / 182 / 17 / 38 / 10 / 4 / 4 / 18 / 660 / 447**. **389 is wrong and appears under NO unit at either tree**, so it was never a units mismatch. `409` likewise; its apparent presence in the v1.7.0 tree is a false match inside `arXiv:2409.11363`. **Reader-facing correction in PUSHED:4335831.** `site/blog/blog-scanning-10-ai-apps.html` said 387 at line 165 and 389 at line 408, contradicting itself on one page; 408 is corrected to 387, determinate because that page's own scan is attributed to `c6aa67a` by its benchmark README, and the stale open-question note at line 171 is replaced by the settled answer with both unit sets stated. **STILL OPEN, and deliberately not guessed at: the 5-frameworks post.** `site/blog/blog-scanning-5-frameworks.html` (154, 155, 242, 363) and `content/devto/scanning-5-frameworks.md` (3, 32, 93, 97) also publish 389, and its artefacts in `benchmarks/results/framework_scan_2026_04/` record `regula_version: 1.7.0` with **no date**, so they do not say which tree ran. 389 is wrong under both, but whether the replacement is 386 or 387 is not derivable from any committed artefact, and substituting either would be inventing a figure. **What would settle it:** any artefact recording the scan date or commit for the framework scan. **Cheapest if none exists:** state the version without a pattern count, true under both trees, as the 70% remediation did for a claim it could not source. Owner decision 4 is now answerable on the measurement and still needs a ruling on that last surface. |
| **F30** | Allowlist entries suppress the whole paragraph, not the matched claim. `scan_file` tests each allowlist pattern against `claim_line`, `claim.snippet` **and `para`**, so one match exempts every claim in the paragraph. | 2026-07-28 17:01 (`431a7d3`) | **OPEN. Unacted across NINE sessions (the count as stated by the owner directive of 30 July; carried, not enumerable by command, the same limit recorded on decision 4), and with three measured instances.** 2026-07-29, on `site/regions/uae.html` the pattern `\bregula[- ]ai\b` matches the product name inside a terminal demo block and thereby exempts the whole `<pre>`. **2026-07-30, found while measuring N23: four quarantine entries fire on nothing because an allowlist pattern matched their whole paragraph first** (`0%` on `site/index.html`, `site/locales/de.html`, `site/locales/pt-br.html`, and `29%` on `site/guides/article-9-risk-management.html`). The allowlist is tested BEFORE the quarantine in `scan_file`, so paragraph-wide allowlisting silently shadows a narrower mechanism as well as the claims it was written for. This remains the strongest continuity finding in the ledger. |
| F31 | Delta-log JSON Schema existed but nothing validated entries against it. | 2026-07-29 11:18 | **CLOSED** in `0990441`. Verified 2026-07-29: `tests/test_delta_log_schema.py` 14 passed, control plants the two real defects. |
| F32 | `strip_noise` blanked command citations, so the gate erased the evidence form it recommends. | 2026-07-29 12:38 | **CLOSED** in `e2b238c`, regression pair hardened in `4aa0f8d`. Verified 2026-07-29 by reverting the hunk in a worktree: 3 failed / 6 passed reverted, 9 passed with the fix. |
| **N1** | A citation resolved against the **working tree** (`(REPO_ROOT / ref).exists()`), so a gitignored file counted as provenance locally and vanished in CI. Commit `4aa0f8d` scored **276** unsourced in the main tree and **277** in a clean worktree. | 2026-07-29 (review) | **CLOSED** in `bebe255`. One predicate `ref_is_tracked()` serves all three call sites. Both trees report **281** at `3939949` (`python3 scripts/claim_auditor.py --diff-base main`, run in the main tree and in a clean worktree). Covered by `tests/test_tracked_citation.py`, 13 tests; two-way control, 5 fail with the fix reverted. |
| **N2** | `docs/MODEL_CARD.md` published "13 domain-gated, 4 AI-gated, 3 pattern gaps, so 17 of 20 misses are gate behaviour", citing `benchmarks/synthetic/RECALL.json`. | 2026-07-29 (review) | **CONTENT CORRECTED 2026-07-29 in PUSHED:7b78f2e. THE STATUS THIS ENTRY USED TO CARRY WAS FALSE.** It read "commit HELD FOR APPROVAL, not pushed". `7b78f2e` is on the remote. It reached it as an ancestor of `f286562`, pushed at 2026-07-29 19:18:53 +0100, and `git reflog show --date=iso refs/remotes/origin/improvement/2026-08-programme` never lists `7b78f2e` as a tip, so it was never sent directly. **A push names a tip, not a set. The remote receives that tip and every one of its ancestors, so a hold is broken by pushing anything descended from the held commit, and an explicit refspec does not narrow that.** Established offline by `git merge-base --is-ancestor 7b78f2e refs/remotes/origin/improvement/2026-08-programme` (exit 0) and `git branch -r --contains 7b78f2e` (`origin/improvement/2026-08-programme`). Enforced from 2026-07-29 by `tests/test_ledger_status.py`, which rejects a prose-only remote-state claim and resolves every HELD:/PUSHED: marker against local remote-tracking refs. **The content correction itself stands, and is restated here unchanged:** the artefact carries per-fixture `missed` lists, so the split is derivable by set difference across the three scanner conditions rather than by subtracting fractions. Derived: **6 recovered by declaring domains, 7 more by an AI-library import, 7 never recovered**, so **13 of 20 are gate behaviour and 7 are pattern-side exposure, not 3**. Every component of the published split was wrong and it understated pattern-side weakness by more than double. `docs/MODEL_CARD.md` now states the derived figures and names its derivation; `tests/test_recall_decomposition.py` recomputes them from the artefact and fails if the prose disagrees. Control: restoring the old wording fails 3 of 5 tests. |
| **N3** | No open-items ledger existed in the repository. | 2026-07-29 (review) | **CLOSED** by this file, `8c8f44c`. |
| **N4** | A session record stated the 30 July standards enquiry window "has now passed" when it closed the following day. | 2026-07-29 (review) | **CLOSED as a record defect**; the repo copy in `OWNER_ACTIONS.md` 5a was always correct. **The underlying owner action remains open**: `prEN 18228` and `prEN 18282` closed **30 July 2026**. Whether it was met is unrecorded. |
| **N5** | Withdrawn recall rows `14/30 = 47%` and `19/30 = 63%` sat unflagged at `STATE.md:884`. | 2026-07-29 (review) | **CLOSED 2026-07-29.** Both rows now carry `[NOT REPRODUCIBLE, see above]` and `[WITHDRAWN, see above]` inline, under a blockquote naming `benchmarks/headtohead/RESULTS-synthetic-v2-2026-07-28.md:38-39` and `:189` and giving the reproducible figures. The decomposition beneath, which N2 inherited, is marked WITHDRAWN with the true split beside it. Rows kept rather than deleted because a superseded figure is part of the record. |
| **N6** | `site/llms-full.txt` is on the published-surface manifest (`data/published_count_manifest.json`) yet the claim auditor never scans it: `.txt` is outside `SCANNED_SUFFIXES = {".md", ".markdown", ".html", ".htm"}`. A designated published surface is invisible to the gate that exists to police published surfaces. | 2026-07-29 | **OPEN.** Measurement rule 5: the gate tests something narrower than the standard. Belongs to the gate-scope repair. **Now surfaced by an instrument rather than only recorded here:** `scripts/f25_exposure.py` reports its manifest corpus as 9 files of 10 and names the tenth with the reason, and `tests/test_f25_exposure.py` fails if that notice disappears. A corpus that quietly loses a member reports less exposure and reads as better news. |
| **N7** | `SHORT_DURATION` (`claim_auditor.py:111`) exempts any bare `N seconds/minutes/ms` as "UX copy, not statistical claims", and therefore exempts genuine published performance claims. Measured instances: `site/regions/uae.html:416` publishes "From pip install to a categorised, article-cited finding in under 10 seconds"; `docs/QUICKSTART.md:7` publishes "Regula tells you where you stand in 10 seconds". Neither is measured anywhere in the repo. | 2026-07-29 | **OPEN, owner ruling needed.** Is a published performance claim UX copy? Deliberately not patched: changing the exemption is a gate-scope decision. |
| **N8** | Regulatory currency movement partly unapplied. `OMNIBUS_OJ_DATE` was correctly flipped to `2026-07-24` and `OMNIBUS_IN_FORCE_DATE` derives `2026-07-27`, but tracked files still carry the phrase "pending OJ publication". **14 tracked files contain it; 13 once `CHANGELOG.md` and `content/regulations/delta-log/` are excluded**, both of which legitimately record what was true on a past date. Count produced by the predicate: `git ls-files -z \| xargs -0 grep -ln "pending OJ publication" \| grep -vE "CHANGELOG\|delta-log" \| wc -l`. | 2026-07-29 | **OPEN, needs triage.** The script and test occurrences are conditional else-branches and are correct to keep. The reference data, the committed benchmark artefacts and the user-facing example are stale output and are not. A regulatory content sweep, not apparatus. |
| **N9** | **Article 50 transparency duties for new systems apply from 2 August 2026**, unchanged by the Omnibus (`content/regulations/delta-log/entries/2026-07-24-oj-publication.json`, quoting the OJ text). No session in this programme surfaced this until 29 July 2026. | 2026-07-29 | **OPEN, live deadline: 2 August 2026.** Stated as a date, not a countdown, because a countdown rots. A day-count defect in the 29 July consolidated record said "three days" from 29 July; the correct interval is four days, and `git ls-files -z \| xargs -0 grep -n "three days"` confirms **no tracked file carries the wrong count** (the seven tracked hits all describe the genuine three-day OJ-to-in-force gap, 24 to 27 July). |
| **N10** | `NUMERIC_CLAIM` misses published numeric claims. Originally recorded as a four-digit gap; **MEASURED 2026-07-29 to be broader than that**. The regex requires the unit word to be ADJACENT to the number, so `465 unique tests` is invisible exactly as `2465 tests` is, and digit count is not the cause. | 2026-07-29 | **OPEN, and worse than first recorded.** `ca.NUMERIC_CLAIM.findall('Expected: 2465 passed.')` returns `[]`. **All six occurrences of the canonical test count on `docs/TRUST.md`, a manifest published surface, are invisible to the gate**, including the comma-separated `2,465 unique tests`. Across the ten manifest surfaces a number-near-unit heuristic finds **37 phrases the gate does not detect on 9 of 10 surfaces**, including `419 risk patterns`, `13 compliance frameworks`, `257 hand-labelled findings` and `8 programming languages`; some entries in that list are artefacts of the heuristic rather than real claims, and the full list is in the 29 July consolidated record so a reader can judge. Widening the regex is gate-scope work and was not done. |
| **N11** | The custom runner wiring rule in `.claude/rules/tests.md` says new test files must be wired into `tests/test_classification.py`. MEASURED 2026-07-29: **89 test files on disk, 22 wired, 67 not**, including `test_command_citation.py`, `test_delta_log_schema.py`, `test_tracked_citation.py` and `test_claim_diff.py`. The rule has not been followed for some time. | **2026-07-29 (this session)** | **OPEN.** Not fixed here: the existing filter excludes only pytest fixtures, so binding a parametrized test such as `test_bucket_predicate` would break the runner. Wiring the backlog needs the filter extended to parametrized tests, which is shared test infrastructure and a scope of its own. |
| **Merge-base measurement** | For each finding `--diff-base main` reports at HEAD, does the same claim exist at the merge base? Decides whether an introduced-claim condition alone can unblock the merge. | 2026-07-29 (review) | **CLOSED, this session.** `python3 scripts/claim_diff.py --base main`, main tree. At `b310821`: 278 findings, 55 at merge base, 223 introduced. At `3939949`, the commit that landed this work: **281 findings, 55 at merge base, 226 introduced.** Buckets at `3939949`, total / at-base / introduced: `docs/improvement/` 203 / 0 / 203; `benchmarks/ + docs/benchmarks/` 67 / 55 / 12; `.claude/rules/` 8 / 0 / 8; `everything else` 3 / 0 / 3. **Answer: an introduced-claim condition alone would NOT unblock the merge.** It removes 55 and leaves 226. **The `everything else` 3 are `docs/adr/0001-claim-identity.md`** (two illustrative figures at L34, one superlative at L101). Writing the ADR about claim identity added three claims to the corpus that measures claims. That is the self-referential loop again, recorded rather than fixed: the bucket predicate was deliberately NOT amended to reclassify `docs/adr/` as a working document, because changing a predicate so that a file the author just created stops counting is the move this programme exists to catch. |
| **N12** | **A published-surface gate condition would turn `main` red.** The condition ignores the diff by design, so on main's own push trigger it scans main's whole tracked corpus, not the branch diff. **SUPERSEDED-BY:N16** on its file count: this row originally said "in 29 files", which has no apparatus and does not reproduce. | **2026-07-29** | **OPEN, owner ruling needed, and it blocks owner decision 7.** MEASURED by `python3 scripts/merge_blockers.py --main-only` against a clean worktree of `main` at `6daacd2`: **168 published-surface findings across 138 tracked md/html files**, in **33 files** (corrected from 29, see N16), largest being `benchmarks/README.md` 28, `docs/benchmarks/PRECISION_RECALL_2026_04.md` 19, `docs/TRUST.md` 14, `benchmarks/CLEAR_CASE_CLUSTERS.md` 14, `references/tree_sitter_implementation_guide.md` 12, `docs/MODEL_CARD.md` 12. **Options, not chosen:** fix the 168 before enabling; scope the condition to the diff, which reopens the hole it exists to close; enable it warn-only on main and blocking on pull requests; or accept the 168 as a recorded baseline and fail only on increase. The owner rules. |
| **N13** | **The residue under both gate conditions is 15 and is not all fixable.** **SUPERSEDED-BY:N15 SUPERSEDED-BY:N18. Do not quote this row's disposition figures.** The `6 fixable` below was over-counted by one (N15) and the residue has since been burned down and re-measured (N18). The `15` itself is not superseded: it is correct at `931dfa4` and moved because the corpus moved. | **2026-07-29** | **OPEN.** Enumerated by `python3 scripts/merge_blockers.py` at `931dfa4`, main tree: 281 total, 226 survive introduced-claim alone, 70 survive published-surface alone, **15 survive both**. Disposition produced by predicates in that script, not by hand: **6 fixable, 7 contested, 2 inherited** [SUPERSEDED, see N15 and N18]. The 2 inherited are N5's withdrawn rows, which must not be sourced. The 7 contested are gate limitations: five are the document disclaiming a figure (`NOT supported: any claim that ... 80% accurate`), one is `nothing else` inside "changing nothing else" in a controlled-experiment description, and three are illustrative figures inside `docs/adr/0001-claim-identity.md`. **A mergeable state is therefore NOT reachable by sourcing alone**: 6 of 15 can be fixed by adding provenance, and the other 9 need either a gate change or a ruling. |
| **Gate scope repair** | `--diff-base` scans whole files rather than introduced claims. | 2026-07-28 | **OPEN. Not started in four consecutive sessions, but its design is now decided by measurement rather than argument.** Bucket figures re-derived at `3939949` in the main tree by `python3 scripts/claim_diff.py --base main`, produced by the same predicate that enumerates the set: **203 of 281 findings are `docs/improvement/`**, 67 are `benchmarks/ + docs/benchmarks/`, 8 are `.claude/rules/`, 3 are `docs/adr/`. The previous "201 of 277" mixed a bucket count taken at 276 in the pre-N1 main tree with a post-fix total, and is withdrawn. **What each candidate condition achieves, from the same run at `3939949`:** introduced-claim alone, 281 to **226** (removes 55, 19.6%); published-surface alone, 281 to **70**; both together, 281 to **15**. At `b310821` the same three figures were 223, 67 and 12; the difference is the three ADR findings. **Recommendation: implement both, and treat the published-surface condition as the load-bearing one.** The introduced-claim condition is worth having because it is what stops a one-line edit inheriting a document's whole backlog, but on this branch it is nearly inert, because the branch created the documents. |
| **N14** | **The 168 is a statement about the product, not only about a gate.** `main` is the shipped, public state of this repository: it is what `origin/main` serves, what a reader clones, and what the website is built from. **168 numeric and superlative claims on its published surfaces carry no in-paragraph provenance.** MEASURED at f286562 in the main tree by `python3 scripts/merge_blockers.py --main-only`, against a clean worktree of `main` at `6daacd2`: 168 findings over 138 tracked md/html files, in 33 files, the itemisation reconciled against the total by the script. Concentration: `benchmarks/README.md` 28, `docs/benchmarks/PRECISION_RECALL_2026_04.md` 19, `docs/TRUST.md` 14, `benchmarks/CLEAR_CASE_CLUSTERS.md` 14, `docs/MODEL_CARD.md` 12, `references/tree_sitter_implementation_guide.md` 12; those six are **99 of 168**, and the four named in the session brief are **73 of 168**. | **2026-07-29 (this session)** | **OPEN, recorded so the ruling is made against the fact and not against a gate-configuration question.** No fix attempted and no plan proposed: the disposition is the owner's. Note what this figure is NOT. It is not a count of false claims; an unsourced claim may be perfectly true. It is a count of claims a reader cannot check from where they are standing. It also predates this branch entirely, so no work here caused it and no work here removes it. |
| **N15** | **The residue disposition classified per finding while the remedy operates per paragraph, so `fixable` was over-counted.** `paragraph_has_source()` is evaluated once per paragraph and every claim inside inherits the verdict, so a citation cannot be aimed at one line. **SUPERSEDES:N13**, whose `6 fixable` is one too many. | **2026-07-29** | **CLOSED as a measurement defect, and the underlying document issue is OPEN.** MEASURED at f286562: `benchmarks/headtohead/RESULTS-synthetic-v2-2026-07-28.md:37` (`33%`, reproducible, backed by `benchmarks/synthetic/RECALL.json`) shares paragraph 35-39 with `:38` and `:39`, both marked `[NOT REPRODUCIBLE]` and both classed `inherited`. Sourcing `:37` would therefore cite two withdrawn figures. Reclassified `blocked` by predicate in `scripts/merge_blockers.py`, not by hand, and guarded by `tests/test_merge_blockers.py` (content-addressed, so editing the document does not silently retarget the assertion; control: 1 test fails with the predicate disabled). **What remains open is the document:** the reproducible row can only be sourced once the withdrawn rows sit in a paragraph of their own, which is a presentation change and the owner's call. Found by attempting the fix, not by reading. |
| **N16** | `scripts/merge_blockers.py` printed totals that nothing checked against the breakdowns printed beneath them. **SUPERSEDES:N12** on the "29 files" figure. | **2026-07-29** | **CLOSED** by `reconcile()`, which every printed total now passes through, checked against the same itemisation the reader is shown, including the `--json` path. Covered by `tests/test_merge_blockers.py`, **13 tests** at 2026-07-30 (10 when this row was written); control run both ways: 6 fail with the check neutered, all pass restored. **How many totals and how many reconciliations: see N21.** **The discrepancy that prompted it does not exist.** `--main-only` reports 168 and itemises 33 files summing to 168, at f286562 AND at `ec484b7`, the commit that introduced the script and recorded the figure. The "29 files" in N12 was recorded without an apparatus and cannot be re-derived, which is this file's own rule about figures whose apparatus is gone. Corrected against the tree. |
| **N17** | **A second published test count existed that no gate covered.** `docs/TRUST.md` publishes how many functions the legacy `tests/test_classification.py` runner executes; `scripts/cascade_count.py` propagates only the pytest-collected count. **SUPERSEDED-BY:N27** on its closing note about the `N passed` figure: that figure is not a test count at all, so "not machine-checked" understated it. | **2026-07-29** | **CLOSED, and it was self-inflicted.** Wiring two new test files into the custom runner, which `.claude/rules/tests.md` requires, moved the runner from 963 functions to 978 while `docs/TRUST.md` carried 963 in **two** places (line 95 inside a reproduction instruction, line 381 in the summary table). Both corrected; verified by an actual run: `Running 978 tests... Results: 1386 passed, 0 failed, 0 skipped (978 test functions)`, rc=0. Guarded by `tests/test_published_count_manifest.py`, which recomputes both figures and covers both locations. Locations produced by `git ls-files \| xargs grep -n 963`, not by reading: the other tracked hits are `CHANGELOG.md`, `docs/improvement/*` and two code comments, all legitimately recording a past date, plus hash coincidences in `uv.lock` that must never be text-replaced. **The `N passed` figure is still not machine-checked**, because deriving it costs a twenty-minute run; it is re-derived by hand and that limitation is stated in the test. |
| **N18** | **Item 2 result: the six fixable residue items, attempted.** **SUPERSEDES:N13** on the disposition: after this burn-down the residue is 10 with **0 fixable**. | **2026-07-29** | **FIVE SOURCED, ONE RECLASSIFIED, and the work is PUSHED:969f3a8.** That commit is off the remote and must stay off it; anything pushed with it as an ancestor publishes it, which is how the N2 hold failed. Sourced, all through the `file-ref` arm rather than `citation-word`: `RESULTS-synthetic-2026-07-28.md:58,59` to `benchmarks/headtohead/results/regula-synthetic-2026-07-28.json`, re-derived from that artefact before citing it; `RESULTS-synthetic-v2-2026-07-28.md:99` twice, to the same artefact and to `benchmarks/synthetic/RECALL.json`; `v2:181` to `docs/improvement/HOSTILE-REVIEW-DISPOSITIONS.md` objection 6, which sources the **attribution** only, since whether 134 is re-derivable from `measure_pattern_reach.py` was not checked and is not claimed. Reclassified `blocked`: `v2:37`, see N15. The two `inherited` rows were deliberately not sourced. **Residue MEASURED at 969f3a8 in the main tree by `python3 scripts/merge_blockers.py`: total 273, introduced-claim alone 218, published-surface alone 65, BOTH 10** (0 fixable, 1 blocked, 7 contested, 2 inherited), down from 15 at f286562. **A mergeable state is still not reachable by sourcing alone:** of the 10 remaining, 1 needs a presentation change and 9 need a gate change or a ruling. |
| **N23** | **The quarantine holds 44 entries of which 21 suppress anything, and its own `_units` field had gone stale for the second time.** `_units` read "42 entries" and "45 suppressed occurrences over 42 unique pairs" while `_count` in the same file said 44, in a field whose own text records a previous correction of exactly this kind. **SUPERSEDED-BY:N31** on its 44-entry figure, which the category-A burn-down took to 29. **SUPERSEDED-BY:N32** on its per-entry cause split: the four entries this row calls allowlist-pre-empted do not reproduce as such. | **2026-07-30 (this session)** | **`_units` FIXED at root; the 23 silent entries are OPEN and the disposition is the owner's.** Re-measured in place, wrapping the real `is_quarantined` and delegating, over the 56 tracked `site/*.html` pages: **380 claims, 0 unsourced, 26 suppressed occurrences over 21 unique pairs**. So 23 of 44 entries fire on nothing. **Cause of each of the 23, reconciled against the total by predicate:** 15 the claim text is gone from the page entirely (the `20%`/`30%`/`40%`/`60%`/`80%` rows on `site/index.html`, `site/locales/de.html`, `site/locales/pt-br.html`); 3 present but blanked by `strip_noise` (`50%` on the same three pages); 4 pre-empted by an allowlist pattern matching the whole paragraph, **which is F30 measured on live data** (`0%` on the same three pages plus `29%` on `site/guides/article-9-risk-management.html`); 1 whose paragraph has since gained a source (`43%` on `site/sample-report.html`). **Removing all 23 is gate-neutral, verified rather than assumed:** with them removed, `python3 scripts/claim_auditor.py --diff-base main` produced byte-identical output and `site_integrity.py` stayed rc=0. **NOT DONE HERE.** Burn-down requires a per-item disposition, the file states its own priority order, and jumping it is not this session's call. `_units` no longer carries figures at all: it names `tests/test_claim_quarantine.py::test_quarantine_liveness_is_recomputed_not_asserted`, which recomputes both units on every run and asserts only the invariants. Deliberately NOT asserted there: that every entry fires, which would force the burn-down above, and that the site corpus is free of unsourced claims, which would be a new gate condition and out of scope. |
| **N24** | **Owner decision 1 encoded.** The quarantine sensitivity-admissions mechanism was ratified with three conditions on 2026-07-28 and went unapplied for five sessions. | **2026-07-30 (this session)** | **CLOSED. Three conditions, three tests, three controls, each run both ways.** (1) *Every admission names the finding ID.* The old check accepted any non-empty `finding` field, which "the auditor got stricter" satisfies; it now must match `^[FN]\d+$` **and resolve to a row in this file**. Control: prose cause planted in the real data, test fails naming it. (2) *Admissions only for claims that pre-date the increase.* Each tranche now declares `instrument_commit` and every admitted claim must be present in its file at that commit's PARENT. `instrument_commit` is **`c7c0ae9`**, the commit that changed the instrument, NOT `b954ecf`, which only logged F21; naming the docs commit would have resolved pre-dating against the wrong tree, and that is N22 biting inside another mechanism. Control: a third admission whose text is new prose, with the ceiling and itemisation adjusted so only condition 2 could fire, fails naming the claim. (3) *The ceiling re-bases once, visibly, with the reason recorded, and shrinks from the new ceiling.* Each tranche declares one `rebase` object with `from`, `to` and `reason`; the chain must start at the base ceiling, step by exactly that tranche's live admission count, stay contiguous, and end at the ceiling the code allows. Control: ceiling raised 44 to 45 with the data untouched, test fails with "a ceiling that grows with no recorded re-base is not permitted". **A latent defect was fixed to make condition 3 satisfiable:** the old itemisation test required EVERY admission to be in `entries`, so burning one down failed the suite. An admission is now in `entries` if and only if it has not been burned down, and a `burned_down` object lowers the ceiling automatically. |
| **N25** | **Owner decision 2 encoded, and the repo's own OJ record disagreed with itself.** The split ruling on Articles 11 and 12 went unapplied for five sessions. | **2026-07-30 (this session)** | **CLOSED, both halves, and a third defect found while doing it.** **Reject half, verified against the primary text before encoding:** Regulation (EU) 2026/1744 Article 1, point (10) reads "in Article 11(1), the second subparagraph is replaced by the following", and the replacement lets SMEs, start-ups and SMCs supply the Annex IV elements in a simplified manner, obliges the Commission to establish a simplified technical-documentation form, and requires notified bodies to accept it. Encoded on `references/framework_crosswalk.yaml` as `amended_by`, `amendment`, `amendment_source`, `amendment_verified`, and surfaced in `regula map-frameworks` text output through a generic amendment branch in `scripts/framework_mapper.py`, because data the formatter ignores still shows a reader the pre-Omnibus duty. **Ratify half:** `owasp_agentic` stays unmapped on Articles 11 and 12, with the reason now in the crosswalk rather than only here. **Article 12 is not amended at all**, established by enumerating the amending article's numbered points against the primary text: **40 points, 1 to 40 with none missing, of which 37 amend an existing article of Regulation (EU) 2024/1689 and 3 insert new ones** (point 6 inserts Article 4a, point 25 Article 60a, point 32 Article 75a and following). None touches Article 12; the sequence runs Article 10 at point (9), Article 11 at point (10), Article 17 at point (11). The first pass of that enumeration matched only the 37 and would have supported a bare "40 amending points" that was true by luck; the three inserting points were found by asking which numbers the pattern had missed. **Third defect:** `content/regulations/delta-log/entries/2026-07-24-oj-publication.json` listed `affected_articles` as 5, 6, 50, 113 while its own `verified_by` field named the amended Article 11(1). Corrected to include 11 and the four generated outputs regenerated by their committed scripts. Guarded by `tests/test_crosswalk_omnibus.py`, 10 tests; three controls run: removing the amendment fields fails 4 tests, adding an OWASP Agentic item fails naming the reversed ruling, reverting the formatter fails the reader-visibility test. |
| **N26** | **F25 re-measured by a committed script. Neither figure on record reproduces, and the exposure is far larger than either.** **SUPERSEDES:F25** on its exposure figure. | **2026-07-30 (this session)** | **MEASURED. Owner decision 3 is now answerable.** `scripts/f25_exposure.py`, committed, with its six corpus definitions written down inside it and every total reconciled against its own itemisation. Exposure is decided by toggling ONE variable on the REAL function: `CITATION_WORDS` swapped for a pattern that cannot match, nothing else changed. **On the gate's own corpus (`diff-base`, 59 files) at `e8b5986` in the main working tree: 279 paragraphs are sourced by the citation-word arm, and for 215 of them the word is the ONLY provenance. In the gate's own unit, findings go from 273 to 364 with the arm off, so 91 findings across 20 files are currently suppressed by an ordinary English word.** Across all tracked scannable files: 512 citation-word paragraphs, 427 exposed, and 133 findings suppressed. **Neither 22 / 46 nor 29 / 53 is recoverable**, and no corpus matches EITHER SIDE of either figure; the twelve candidates are printed by `--recover`. Establishing that both prior figures are unreproducible is the result, and no third figure is offered as their successor. **F25 is NOT fixed:** re-ordering the arms is a gate-scope change and out of scope. Two defects were found in the apparatus while building it and both are recorded in the module: a first draft counted claim occurrences by applying the auditor's claim regexes to a paragraph directly, which counts matches the gate exempts, and was deleted rather than corrected in favour of running the real gate twice; and a finding key of (file, line, kind, snippet) reported **267** where the auditor's own list reported **273** over the same 59 files, because six claims repeat identically on one line. Guarded by `tests/test_f25_exposure.py`, 12 tests; controls: moving the citation-word arm after the file-ref arm fails the ordering test, and removing the occurrence ordinal reproduces the 267-versus-273 undercount. |
| **N27** | **SUPERSEDES:N17** on its `N passed` note. **A figure published on `docs/TRUST.md` that looks like a test count is not one, and is invariant to adding tests.** The custom runner prints `Results: N passed, ...` where `N` is `helpers.passed`, incremented only by the `assert_true` / `assert_eq` / `assert_false` helpers in `tests/helpers.py`. A test written with a bare `assert` executes, passes, and contributes **nothing** to it. | **2026-07-30 (this session)** | **ANNOTATED on the surface, mechanism OPEN.** Found by predicting that the figure would move and watching it not. **Positive proof, three runs:** `Running 978 tests... Results: 1386 passed, 0 failed, 0 skipped (978 test functions)` on 2026-07-29, then `1010 test functions` and then `1011 test functions` on 2026-07-30, **`1386 passed` every time**, rc=0 every time. **33 functions were added across those runs and the figure did not change by one.** Cause confirmed by enumeration rather than inference: the five test files touched or added this session contain **0** calls to those helpers (`grep -cE "assert_true\(\|assert_eq\(\|assert_false\("` per file). `docs/TRUST.md` line 95 now states in the surface itself that `1386 passed` counts helper assertions and that the number to read is the function count in brackets. **Not fixed:** making the counter count tests means changing `tests/helpers.py` and the runner's summary, which alters a published figure's definition and is shared test infrastructure; it belongs with the N11 runner-wiring work, not to a session encoding owner decisions. This also explains, and partly supersedes, N17's note that the figure "is not machine-checked": the deeper problem is that it is not a test count, so checking it would have certified the wrong thing. |
| **N28** | **The full suite is not deterministic: `tests/test_security_hardening.py::test_redos_ast_patterns` asserts on WALL CLOCK.** It times `pattern.search(input)` for eight compiled regexes against pathological inputs and fails any that exceeds **1.0 second**. A wall-clock threshold inside a sixteen-minute suite measures machine contention, not the regex. | **2026-07-30 (this session)** | **OPEN, not touched, and the reason for not touching it is the point.** OBSERVED: the suite ran `1 failed, 2527 passed in 956.70s`, rc=1, on `AssertionError: ReDoS in ast_engine: ['_RE_JAVA_METHOD_DEF: 1.64s on len=10008']`. **Diagnosed, not assumed.** The test passes in isolation in 0.13s and 5 consecutive isolated runs all exit 0. Measured directly, `_RE_JAVA_METHOD_DEF.search()` on both 10,008-character inputs in that set runs at a **median of 0.0095s and 0.0103s, roughly 100x inside the threshold**. A 1.64s reading is therefore a **~170x** wall-clock excursion under scheduling contention, not a regex on the edge of catastrophic backtracking, and nothing in this session touches `scripts/ast_engine.py` or any detection pattern. **Deliberately NOT fixed by raising the threshold, marking it flaky, or skipping it.** Every one of those is suppression to make a check pass, and this repository's own `docs/TRUST.md` already warns that "wall-clock is machine-dependent and is NOT a claim; it has varied by a factor of two on one laptop in a single day". Here it varied by two orders of magnitude. The durable fix is to assert on a deterministic proxy for backtracking, such as a step or comparison budget, rather than on elapsed time, and that is a change to a security test and its published meaning. **Consequence a reviewer must weigh: `full suite green` is a statement about one run, on one machine, at one load.** |
| F21 | Self-citation via canonical URL. | 2026-07-28 09:48 | CLOSED in `c7c0ae9`, which added `page_identity`, `SELFREF_TAG` and `_is_self_url` to `scripts/claim_auditor.py`. **Attribution corrected 2026-07-30, see N22:** this row said `b954ecf`, a docs-only commit that RECORDED the finding. Not independently re-verified. |
| F22 | The 0.5 magnitude floor. | 2026-07-28 16:09 | CLOSED in `c7c0ae9` (floor replaced by `STALE_CHECK_EXEMPTIONS`) with the regression pair in `88d45f7`. **Attribution corrected 2026-07-30, see N22:** this row said `0e1f509`, a docs-only commit. Not independently re-verified. |
| F24 | Recall underivability. | 2026-07-28 16:09 | CLOSED in `bb98261`, which added `scripts/build_recall_artefact.py`, `benchmarks/synthetic/RECALL.json` and `tests/test_recall_artefact.py`. **Attribution corrected 2026-07-30, see N22.** Not independently re-verified. |
| F26 | Branch red for six commits under a collect count. | 2026-07-28 16:09 | CLOSED in `bb98261`, which renamed the assertion to `test_synthetic_fixture_precision_recall_matches_artefact` and made it read its expectation from the artefact. **Attribution corrected 2026-07-30, see N22.** Not independently re-verified. |
| F27 | F8 not supported by a like-for-like comparison. | 2026-07-28 16:09 | CLOSED in `bb98261`, which withdrew the two unreproducible figures in `benchmarks/headtohead/RESULTS-synthetic-v2-2026-07-28.md`. **Attribution corrected 2026-07-30, see N22.** Not independently re-verified. |
| F28 | `cascade_count --check` was a blank gate. | 2026-07-28 16:09 | CLOSED in `f51af33`. **Attribution corrected 2026-07-30, see N22:** this row said `0e1f509`, a docs-only commit. Not independently re-verified. |
| **N19** | **A current-state record said "Failing: nothing" while the merge blocker was red.** `python3 scripts/claim_auditor.py --diff-base main` exits **rc=1** and is not one of the six fast gates, so its red never appears in a gates block and a reader with no terminal cannot see it. | **2026-07-30 (this session)** | **CLOSED as a record defect; the underlying gate is still red and is recorded in section 6 of this file.** The 29 July consolidated record listed six fast gates rc=0, full suite green and "Failing: nothing" on the same page as a merge blocker exiting 1. Section 6 below now carries the failing gate with its figure, commit and tree, and is the place any future current-state statement belongs. |
| **N20** | **Supersession between ledger rows was prose-only, so nothing could check that a figure was still current.** `tests/test_ledger_status.py` verified claims about commits and nothing verified currency. | **2026-07-30 (this session)** | **CLOSED.** Declared and bidirectional: the newer row carries `SUPERSEDES:<id>`, the older carries `SUPERSEDED-BY:<id>`, and `audit_supersession()` in `tests/test_ledger_status.py` fails on any unpaired declaration, any marker naming a row that does not exist, any self-reference and any duplicate row id. Six tests. **Control run both ways against the real file**, both directions, and against fixtures for the dangling, self-referential and many-to-one cases. Design reasoning, including why the marker is deliberately NOT applied to a figure that merely moved, is in the module docstring so a later session inherits the basis and not only the conclusion. |
| **N21** | **Two record sections disagreed about `scripts/merge_blockers.py`: five printed totals versus eight reconciliations.** Neither said what it was counting, so the two read as a contradiction. | **2026-07-30 (this session)** | **CLOSED, and both figures are right about different things.** Derived from the code by `tests/test_merge_blockers.py`, not from either prose figure: **5 `reconcile()` call sites**, in 3 functions, read from the module's syntax tree (`report_main_only` 1, `reconcile_residue` 3 of which one is in a loop, `main` 1); **5 distinct totals printed to a reader**, parsed from the text the report functions emit (`total findings`, `survive introduced-claim alone`, `survive published-surface alone`, `survive BOTH`, `published-surface findings ON MAIN`); and **8 reconciliations executed across the module**, counted by wrapping the real `reconcile` and delegating to it: 6 on the residue path, 1 on the main-only path, 1 more on the `--main-only --json` branch. The gap between 5 and 8 is that `survive BOTH` is printed once and reconciled three ways, and that the JSON branch reconciles its total a second time. **The load-bearing assertion is neither count: it is that every total printed to a reader was reconciled.** Control: an extra unreconciled total planted in `report_residue` fails that assertion by name. |
| **N29** | **`main`'s published-surface debt was measured with the citation-word arm ACTIVE, so 168 is a floor and not the debt.** A ratchet baselined on 168 would be baselined on a number the gate-scope repair is going to move, because narrowing `CITATION_WORDS` is part of that repair. This is the missing input to owner decision 7. | **2026-07-30 (this session)** | **MEASURED. `python3 scripts/merge_blockers.py --main-only --arm-delta`, a clean detached worktree of `main` at `6daacd2` (tree `b95876d`), scanned by HEAD's `scripts/claim_auditor.py` which was unmodified at `13ffc00`. ONE worktree, ONE auditor module, TWO scans, ONE variable toggled. Over the same 138 tracked md/html files: arm ON **168**, arm OFF **238**, **70 revealed**, and **0 findings stop being reported**, which is the direction check. Every one of those four totals is reconciled against its own by-file itemisation by the script before it prints. The arm-ON pass reproduces the pre-existing `--main-only` instrument exactly: 168 over 33 files. Prediction written before the run: 168 arm-on (right), 61 revealed (WRONG, the actual is 70; 61 is the figure for the BRANCH's published corpus, which is a different corpus). **What the four options in N12 imply at 238 rather than 168** is set out in section 7 below. Concentration of the 70: `site/blog/blog-scanning-10-ai-apps.html` 15, `site/blog/blog-scanning-5-frameworks.html` 14, `content/devto/scanning-5-frameworks.md` 8, `docs/TRUST.md` 6, `benchmarks/LABELLING_CRITERIA.md` 4, `docs/self-scan-results.md` 4. **Note what makes main's figure larger than the branch's for the same pages:** `main` has no `.claim-quarantine.json` at all (`git ls-tree main -- .claim-quarantine.json` is empty), so nothing on main is quarantined, and 15 tracked files under `site/` differ between `main` and this branch. |
| **N30** | **The 26 findings the citation-word arm holds green on the site corpus had never been looked at, because the apparatus reported counts and not claims.** | **2026-07-30 (this session)** | **ENUMERATED AND CLASSIFIED. F25 is now a product finding, not only an apparatus one.** `python3 scripts/f25_exposure.py --corpus site --enumerate` at `13ffc00`, working tree carrying uncommitted edits to `scripts/f25_exposure.py` and `scripts/merge_blockers.py` only; `scripts/claim_auditor.py` and every scanned page were identical to `13ffc00`. **26 findings in 10 paragraphs across 7 files**, the enumeration produced by the same predicate that produces the count and joined to its paragraph on exact coordinates, never by containment. **Classification: 24 real claims needing provenance, 2 false positives of the claim regexes.** The two false positives are `site/sample-report.html:122`, a conditional sentence inside a terminal-output demo (`If confirmed high-risk (Article 6)`), and `site/blog/blog-aicdi-governance-gaps.html:244`, where `ATTRIBUTED_CLAIM` read the tool name `Write` in "blocks Bash/Write/Edit operations" as an attribution verb. **Nothing on a published surface was changed: that is content work and needs approval.** Three things the enumeration surfaced that a count could not. **(1)** The single most substantive is `site/blog/blog-static-analysis-ai-compliance.html:189`, "the roughly 70% of the EU AI Act that has no source-code footprint". It is the only occurrence of that figure on the page, the page has no methodology note, and it is held green by the word `source` inside "source-code footprint". **(2)** On `site/blog/blog-article-5-prohibited-practices.html:270` the arm matched `ref` inside the CSS class name `article-ref`, because `_citable_text` blanks only `link/meta/img/source/iframe/base/track/area/use` tags and a `<div>`'s attributes survive. A CSS class name is sourcing published prose. **(3)** On `site/regions/south-africa-ai-policy.html` the whole 37-line FAQ section is ONE paragraph, because the `<details>` blocks carry no blank lines between them, so `verified against` in the fourth answer sources the first, second and ninth as well; and the sentence it comes from says the claim "will be verified against the gazetted text when it publishes", which is a promise of FUTURE verification being read as provenance. **On the same corpus at `main`, `site/` carries 38 revealed findings over 8 files, not 26 over 7**, for the two reasons in N29. |
| **N31** | **The burn-down protocol lowered the ceiling automatically only for sensitivity ADMISSIONS. For an ordinary backlog entry it did nothing, so fifteen entries could be removed and the ceiling would stay at 44, leaving fifteen slots a new entry could occupy without the ratchet firing.** **SUPERSEDES:N23** on its 44-entry figure. | **2026-07-30 (this session)** | **FOUND BY EXERCISING THE PROTOCOL, AND FIXED AT THE CLASS.** The brief asked for the fifteen category-A entries to be burned down "through the protocol condition 3 established, with its `burned_down` objects lowering the ceiling automatically", and to say plainly if the protocol did not behave as designed. **It did not.** `_burn_down_protocol` lived inside the F21 tranche and its instruction was "Lower `QUARANTINE_ADMITTED` in tests/test_claim_quarantine.py in the same commit", which is a manual edit and applies only to the two admitted entries. Neither `.claim-quarantine.json` nor `tests/test_claim_quarantine.py` had any mechanism for a base entry. **Extended rather than worked around:** the quarantine now carries a top-level `burned_down` list and a `_burn_down` protocol for base entries, and `quarantine_ceiling()` derives the ceiling as `QUARANTINE_BASE_CEILING + QUARANTINE_ADMITTED - len(burned_down)`. `QUARANTINE_BASE_CEILING` stays at 42 deliberately: it is what the declared re-base chain is anchored to, and rewriting it would falsify the historical record condition 3 checks. **Result: 44 entries to 29, ceiling 44 to 29, and the ratchet is now tight rather than carrying fifteen slots of slack.** Gate-neutrality verified rather than assumed: `python3 scripts/claim_auditor.py --diff-base main` produced BYTE-IDENTICAL output before and after (`diff` of the two captures is empty; `scanned 59 file(s), 978 claim(s), 274 unsourced`, rc=1 both times) and `python3 scripts/site_integrity.py` stayed rc=0. Four controls run, each restored after: adding one new entry fails the ratchet at 30 against 29; a burn-down record for text still on its page fails by name; stripping `silent_because` fails by name; a `silent_because` that measurement contradicts fails by name. |
| **N32** | **`LEDGER.md` N23 attributed four silences to an allowlist match. The tree says the operative cause is that the paragraph is sourced, and the allowlist is a second blocker that never gets consulted.** **SUPERSEDES:N23** on its cause split. | **2026-07-30 (this session)** | **RE-MEASURED, AND THE DISAGREEMENT IS NOW RECORDED IN DATA RATHER THAN PROSE.** `scan_file` runs `if has_src: continue` BEFORE the allowlist loop, so a sourced paragraph short-circuits and the allowlist is never reached. Measured by `python3 scripts/quarantine_liveness.py`, which runs the REAL gate over the pages the quarantine names with one thing toggled at a time and never forks `scan_file`. **N23's split was 15 text-gone / 3 blanked / 4 allowlist-pre-empted / 1 paragraph-sourced. The measured split at `13ffc00` is 15 text-absent / 3 blanked-by-strip-noise / 5 paragraph-sourced / 0 allowlist-pre-empted.** Both records agree that 23 of 44 were silent and that 26 occurrences were suppressed over 21 unique pairs; they disagree only on which of two simultaneous blockers is operative. **Both statements about the data are true and the attribution was not:** all four of those paragraphs are BOTH sourced AND allowlist-matched, which is why the entries now carry `silent_because` (the blocker reached first) AND `also_blocked_by` (what stands behind it), both re-measured on every test run. My own prediction before running was N23's split, and it was wrong. **Two further facts fall out.** `site/index.html`'s `0%` is sourced by `citation-word` while `site/locales/de.html` and `site/locales/pt-br.html` reach the same verdict through `file-ref:tests/test_gap_demo.py`, so the three locale pages are not parity copies as far as provenance goes. And because `site/index.html`'s `0%` rests on a citation word, the F25 gate-scope repair could make that quarantine entry live again; F30 is not the only finding entangled with the quarantine. |
| **N38** | **The "roughly 70% of the EU AI Act" claim has no source and no derivation, and it is on four reader-facing surfaces rather than one.** It is the premise of the product's positioning, not a figure inside a scan report. | **2026-07-30 (this session)** | **INVESTIGATED, CONCLUDED, AND NOT EDITED. Full record in `docs/adr/0002-the-seventy-percent-claim.md`.** Searched the repository (every `70%` occurrence, `docs/what-regula-does-not-do.md`, `references/article_obligations.yaml`, the crosswalk, and `git log -S` across all refs) and externally (four searches, including an exact-phrase search that returned **zero results**). The claim entered at `001b6c5` **with no source attached at introduction**; nothing was ever removed. The nearest repository basis is qualitative and covers seven articles. The nearest external work, Cappelli et al. on ScienceDirect, counts roughly 729 provisions and 862 obligations but does not apportion them between code-detectable and organisational. **Conclusion: no source or derivation exists.** Recommendation, labelled reasoned and not evidenced: weaken to the qualitative claim the repository can already support, with the case against recorded in the ADR. **Circularity risk, not hypothetical: Regula's own page already ranks on the first page for the query a person would use to check this claim**, so if the figure propagates Regula becomes its own citation. **This was already known and deferred:** `docs/improvement/STATE.md:1242` and `docs/improvement/HANDOVER.md:126` both record it as "a substantive modelling claim about the regulation's composition", assigned to "class 2" and marked NOT DONE. This row supersedes that deferral with an actual investigation. |
| **N33** | **This branch added five findings to the merge blocker and nothing named them.** The blocker read 274 at `13ffc00` and 279 at `9e6b6de`. A session that adds to the blocker without naming what it added is the accounting failure this file exists to prevent, and until 2026-07-30 no committed command could answer it. | **2026-07-30 (this session)** | **NAMED, and the command is committed.** `python3 scripts/claim_diff.py --blocker-delta 13ffc00 9e6b6de`, which scans `--diff-base main` inside a clean detached worktree of each commit and diffs the two finding sets. It reproduces both totals exactly: 274 at `13ffc00` tree `9fd730a`, 279 at `9e6b6de` tree `8e9e483`, 59 scanned files at each. **All five are in `docs/improvement/LEDGER.md` and all five are mine, from the section 7 written last session: `70 findings` (L316), `6 files` (L326), `42%` (L327), `the only` (L336), `cheapest` (L337). Nothing was removed; the net is +5.** The `42%` is a rounding of 41.67%, the exact rise from 168 to 238. **Attribution is exact for four and declared ambiguous for one:** `the only` occurred once at `13ffc00` (L5) and twice at `9e6b6de` (L5 and L336), and identical claim text repeated in one file cannot be told apart across two commits without reading diff hunks, so the tool prints both sides rather than picking one and looking certain. **Control, run and agreeing:** `--carry-instrument` copies this tree's auditor, quarantine and allowlist into both worktrees, so the only variable is the scanned content. It returns the same five. The quarantine burn-down of 44 entries to 29 therefore contributed **0** to the movement, measured rather than assumed, and `git diff --stat 13ffc00 9e6b6de -- scripts/claim_auditor.py` is empty, so the detector never moved either. **This session will itself add findings by writing this row; that figure is in section 6.** |
| **N34** | **`main`'s revealed site findings had never been enumerated, and the branch's enumeration could not reach them.** `f25_exposure.py` resolves every corpus against this branch's working tree; `merge_blockers.py` owns the clean worktree of `main`. Answering the same question in both places needed one predicate, not two. | **2026-07-30 (this session)** | **ENUMERATED, CLASSIFIED, AND THE APPARATUS IS NOW SHARED.** `scripts/gate_probe.py` is a new leaf module holding `reconcile`, `TotalMismatch`, the off-switch, the occurrence-keyed finding records, the paragraph classification and the per-finding enumeration. Everything in it takes the auditor MODULE and its ROOT as arguments and hardcodes neither, so `f25_exposure` passes `claim_auditor` and `REPO_ROOT` while `merge_blockers` passes the module loaded out of a worktree of `main`. `f25_exposure`, `merge_blockers` and `claim_diff` all import from it and re-export under their old names; `python3 -c "import ..."` confirms all three hold the SAME objects, not equal copies. **`python3 scripts/merge_blockers.py --main-only --arm-delta` at `main` `6daacd2`: 168 with the arm on, 238 with it off, 70 revealed, 0 lost, of which 38 are under `site/` over 8 files.** The refactor is behaviour-preserving: the branch's 26-line enumeration is byte-identical to the pre-refactor capture, and 168/238/70/0 are unchanged. **Classification, 36 real and 2 false positives**, on the standard the branch set (a false positive is revealed text that is not an assertion about the world): `site/sample-report.html:122`, a conditional sentence in a terminal demo, and `site/blog/blog-aicdi-governance-gaps.html:244`, where `ATTRIBUTED_CLAIM` read the tool name `Write` as an attribution verb. The classification is judgement and is labelled as such; the completeness of the set is machine-produced. **26 of the 38 also appear on the branch and 12 do not, computed as a multiset difference on content signature, and ALL TWELVE are claims the branch quarantine lists** (`27.8%` x2, `553 findings` x3, `56.6%` x2, `7.4%` x2 on `blog-scanning-10-ai-apps.html`, `562 findings` on `blog-scanning-5-frameworks.html`, `43%` on `eu-ai-act-recruitment-hiring.html` and on `sample-report.html`). `main` has no `.claim-quarantine.json` at all, so the branch's extra suppression is the whole of the difference. **Nothing on a published surface was changed.** |
| **N35** | **A CSS class name sources published prose.** `_citable_text` blanks only the void tags in `NONCITATION_TAG` (`link\|meta\|img\|source\|iframe\|base\|track\|area\|use`), so a `<div class="article-ref">`'s attributes survive into the text the source test reads and `ref` matches. Same family as F21, where a page's own canonical URL sourced its claims. Demonstrated 2026-07-30 inside N30's status field rather than as a row of its own, which is one edit from being lost. | **2026-07-30 (this session, promoted from N30's status)** | **OPEN, FROZEN pending owner decision 7, and now MEASURED.** `python3 scripts/f25_exposure.py --corpus site --shape` at `9e6b6de`: **18 of the site corpus's 105 citation-word paragraphs are sourced ONLY by a citation word occurring inside an HTML attribute**, over 4 files, meaning nothing a reader can see supplied the provenance. Concentration: `site/blog/blog-risk-tiers-in-code.html` 10 and `site/blog/blog-article-5-prohibited-practices.html` 6, both `ref` from `class="article-ref"`, plus `source` on `site/assess/index.html` and `see` on `site/index.html:355-459`. **That last one matters beyond this row:** it is the paragraph whose source keeps the `0%` quarantine entry silent, so an attribute-only citation word is currently holding a quarantine entry down. Not fixed: narrowing what `_citable_text` blanks is gate-scope work. |
| **N36** | **An HTML section with no blank lines is one paragraph.** `split_paragraphs` splits on blank lines, and `paragraph_has_source` is evaluated once per paragraph with every claim inside inheriting the verdict. A 37-line FAQ with nine answers is therefore a single unit of provenance, and one citation word in the fourth answer sources all nine. Demonstrated 2026-07-30 inside N30's status field rather than as a row of its own. | **2026-07-30 (this session, promoted from N30's status)** | **OPEN, FROZEN pending owner decision 7, and now MEASURED.** Same command as N35. Distribution over the site corpus's **1,906 paragraphs** at `9e6b6de`: median **2** lines, p90 **16**, p99 **43**, **max 105**. **305 paragraphs exceed 10 lines and 40 exceed 30 lines.** Thresholds are declared in `f25_exposure.PARAGRAPH_LENGTH_THRESHOLDS` rather than buried in a format string: 10 lines is the point past which a paragraph is no longer a unit a reader would recognise as one piece of prose, and 30 is the scale of a whole HTML section, which is the shape this finding is about. **Of the 26 findings the arm holds green on the branch's site corpus, 14 sit in a paragraph longer than 10 lines and 13 in one longer than 30.** So half the site's suppressed findings are being sourced by a word that may be a hundred lines away from them. Not fixed: changing how paragraphs are split changes every coordinate in the programme. |
| **N37** | **A key that served two different questions produced a right count and a wrong attribution.** A first draft of `gate_probe` dropped the line number from the finding key so one key could serve both same-tree and cross-commit comparisons. | **2026-07-30 (this session)** | **CAUGHT BY THE JOIN GUARD BEFORE ANY FIGURE WAS PUBLISHED, and fixed.** Dropping the line makes the occurrence ordinal POSITIONALLY UNSTABLE: when the arm-off pass adds a finding EARLIER in a file, every later identical snippet shifts ordinal and the set difference returns the tail of the list rather than the findings actually revealed. MEASURED on `site/guides/eu-ai-act-recruitment-hiring.html` at `main`: `43%` yields one finding with the arm on (line 213) and two with it off (lines 210 and 213); the keyless difference resolved to line **213**, an unsourced paragraph, while the finding actually revealed is line **210**. `enumerate_revealed` raised `UnjoinedFinding` on 4 of 70 revealed findings and refused to print. **The count stayed right at 70 throughout and only the attribution was wrong**, which is why a count-only check would never have caught it. Fixed by giving the two questions two keys: `finding_key` includes the line and is for same-tree comparisons only, `content_signature` carries no coordinates and is the multiset element for cross-commit ones. Both are pinned by `tests/test_gate_probe.py`. |
| **N22** | **Six ledger rows named the commit that RECORDED a finding as the commit that FIXED it.** F21 was attributed to `b954ecf` and F22, F24, F26, F27, F28 to `0e1f509`. Both are docs-only commits: `b954ecf` touches four files under `.claude/rules/` and `docs/improvement/`, `0e1f509` touches `docs/improvement/STATE.md` alone. A docs-only commit cannot close a code defect. | **2026-07-30 (this session)** | **CORRECTED above, by `git log -S` per finding, not by reading.** True commits: F21 and F22 `c7c0ae9` (F22's regression pair `88d45f7`), F24, F26 and F27 `bb98261`, F28 `f51af33`. **"Six" is produced by enumeration, not by reading.** Every row of section 1 whose status contains CLOSED was scanned for backticked commits and each commit's `git show --name-only` classified; at `e8b5986` that gives **55 table rows scanned and 7 rows naming a docs-only commit**: the six above, plus **N3**, whose closure commit `8c8f44c` touches only `docs/improvement/LEDGER.md` and `docs/improvement/OWNER_ACTIONS.md` and is CORRECT, because N3 is the finding that no ledger existed and creating this file closed it. **No mechanical check was added, and that seventh hit is why rather than a guess:** a predicate of the form "a closure commit must touch a non-docs path" fires correctly on six and wrongly on one, and telling a record-defect closure from a code-defect closure is a judgement no predicate makes. Adding a third marker family in the same session that introduces the supersession markers is also more apparatus than one review can absorb. **The 6-versus-1 split is measured; the decision not to build the predicate is reasoned, not evidenced.** The observation that would overturn it is a rule that separates the two kinds of closure without a false positive. Cheapest reversal: the corrections are prose and revert in one edit. |
| **N39** | **Two arithmetic defects in the session 9 record, each contradicting evidence pasted beside it.** (a) The consolidated handover's header declared **4** commits and a finish at `41feb51`, while its own section 12.3 itemised **six** and its section 12.2 prose said six; its own pasted `git rev-parse` output showed `ef2b8de`. (b) A five-file test decomposition read `7 + 15 + 15 + 21 + 17` beside a pasted `72 passed`, which sums to **75**. | **2026-07-30 (this session)** | **BOTH DIAGNOSED AND RE-DERIVED FROM COMMANDS, and they are NOT the same defect.** (b) is arithmetic: running each file alone gives `test_gate_probe.py` 7, `test_f25_exposure.py` 15, `test_merge_blockers.py` 15, **`test_claim_diff.py` 18**, `test_claim_quarantine.py` 17, summing to 72 and matching the combined run. **The misattributed file is `tests/test_claim_diff.py`, published at 21 against a measured 18.** (a) is NOT arithmetic, and finding that out changed the fix: `git rev-list --count 9e6b6de..41feb51` is **4**, so the header was internally consistent with its own declared finish. **The declared finish was stale** because `190da47` and `ef2b8de` landed after the header was written and it was never re-derived; `git rev-list --count 9e6b6de..ef2b8de` is 6. An arithmetic check could never have caught (a). The two undocumented commits now have the per-commit diffstat every other commit received: **`190da47`, tree `9f16497`, `docs/adr/0002-the-seventy-percent-claim.md` only, 1 file changed, 6 insertions, 2 deletions**; **`ef2b8de`, tree `f9b12b6`, `docs/improvement/LEDGER.md` only, 1 file changed, 20 insertions, 9 deletions**. Both are docs-only and neither touches code. **(c) A THIRD defect was found while writing this row, and it was found by being caught: the session 9 handover published `ef2b8de`'s tree as f9b1262 (written here WITHOUT backticks, see below) at its line 1542, and `git rev-parse` on it returns `fatal: ambiguous argument`. It names no object in this repository.** The real short tree is `f9b12b6`; the published figure is a transposition of it. It was quoted forward into three places in this file before `tests/test_ledger_status.py::test_ledger_commit_claims_are_verified` refused it with "is written in the object form but names no commit or tree in this repository", and all three were corrected. **The bad string is deliberately written as plain text rather than in backticks, and that is not a dodge around the guard.** The guard's invariant is that a backticked hash in this file names a real object, so a reader can trust every one of them. A string being reported AS invalid is not a claim that it exists, and writing it in the object form would assert the opposite of what the sentence says. Nothing was allowlisted, excluded or weakened to accommodate it; the guard still checks every backticked hash in this file, and it is the reason defect (c) is in this row at all. **This is measurement rule 3 landing on the session that was auditing measurement rule 3:** a figure was copied from a record instead of re-derived, and the only reason it did not survive is that an existing guard tested the claim rather than the prose. It is also outside `check_decompositions.py`'s reach, because the handover's commit table states a tree without the word "tree" on the line, so the `commit-anchors` rule does not see it; the two instruments are complementary and neither is sufficient. **The handover carrying all three defects lives on the Windows filesystem and is not tracked**, so `git grep` for its figures returns nothing and rule 4b applies: it was never a repository surface. That is precisely why this row exists, and why the class is closed by an instrument that can be pointed at an untracked file before it ships. See N40. |
| **N40** | **Nothing checked that a decomposition stated in prose agreed with the total pasted beside it.** Both N39 defects sat next to their own contradicting evidence through a full session and a review. | **2026-07-30 (this session)** | **CLOSED for the arithmetic shape by `scripts/check_decompositions.py`, with the negative result on the third shape recorded rather than retried.** Three rules, each measured against the real corpus before being kept: `sum-equals` finds **8** explicit `a + b + ... = T` statements in tracked `docs/**/*.md` and **all 8 are arithmetically correct**, so the rule is green on content rather than green because it is inert; `fence-total` finds **0** pairings in tracked docs and **fires on the real N39(b) defect**, naming both sums (`'7 + 15 + 15 + 21 + 17' sums to 75, '0 + 15 + 14 + 16 + 17' sums to 62` against a pasted total of 72); `commit-anchors` reconciles a declared commit count against `git rev-list --count` and, under `--require-head`, catches the stale finish that is N39(a). Pointed at the real session 9 handover the instrument reports **exactly the two N39 defects and nothing else**, rc=1. Control run both ways on a real tracked record, not a fixture: planting `= 260` as `= 261` at `docs/improvement/STATE.md:1892` gives `sum-equals ... sums to 260, stated total is 261, gap -1` with rc=1 and fails `test_the_tracked_corpus_is_clean_at_this_commit`; `git checkout --` restores it and both go green. The module carries its own control and exits **2** rather than 0 if a rule stops firing, because a permanently green check is a blank gate. `tests/test_check_decompositions.py`, 19 tests. **THE RECORDED NEGATIVE RESULT:** a fourth rule was prototyped that paired any `Label: N` declaration with a nearby itemisation by matching the label against section headings. Measured on the tracked corpus it produced **7 findings, all 7 false** (`"OSS corpus" 15 vs 8`, `"README" 161 vs 2` where 161 is a line number, `"NEXT" 1 vs 2`, `"Files scanned" 0 vs 1` which is pasted sample CLI output) and **0 true positives**: it did not even fire on N39(a). `Label: N` in this corpus is overwhelmingly not a count of an itemised set, and the pairing cannot be inferred from proximity or heading text. **Reasoned, not evidenced, on the general question:** the class is closeable only where the record states its anchors explicitly, which is why `commit-anchors` is narrow rather than general. Assumption it rests on: that records keep declaring start, finish and count, which is this programme's stable handover schema. The observation that would overturn it is a pairing rule that separates a count-of-a-set from a line number without a false positive on this corpus. Cheapest reversal: the rejected rule is absent, and `test_the_rule_set_does_not_include_the_rejected_heuristic` fails if it returns, so re-adding it forces a re-measurement rather than a silent regression. |
| **N41** | **The N37 ordinal defect was fixed where it fired, and nothing had checked whether any other comparison in the programme had the same shape.** N37: a finding key that dropped the line produced a correct total of 70 with a wrong attribution, the difference resolving to line 213 while the finding revealed was at line 210. | **2026-07-30 (this session)** | **AUDITED BY PREDICATE, ONE MORE SITE FOUND DEFECTIVE AND FIXED, AND THE AUDIT IS NOW SELF-RENEWING.** Enumerated by AST walk over the scripts that import the claim apparatus, not by grep and not by memory: **8 apparatus scripts, 42 operation sites, 29 distinct (file, function, kind), 7 cross-state comparisons of finding/claim/fired sets, 1 defective.** Reconciled by `tests/test_setop_inventory.py::test_the_audit_reconciles_against_its_own_enumeration`, which computes every one of those figures rather than reading them. **The defective site is `claim_diff.classify_findings`.** Its key `claim_key` is `(file, normalised snippet)` with no line and no ordinal, so it CAN collide within one file, and it compared a **set**, which loses multiplicity rather than position. On the 210-versus-213 shape, base holding a claim once and head holding it twice, it reported **0 introduced where the truth is 1**: the occurrence the branch added was classified as inherited and vanished from the bucket the merge gate reads. Same root cause as N37, a key too coarse for the question, different symptom. **On the real tree the under-count is 0**, measured at `da728db` by re-deriving the base side as a multiset with the real extractor's own predicate: 280 findings, 209 distinct head keys, 49 keys with duplicates, 71 surplus occurrences, and **zero** keys where base > 0 and head > base. The prediction written before that measurement was 5 to 20 and it was **wrong**; the 49 duplicated keys all sit in files whose base has the claim zero times, so the shipped set test happened to be right. **The defect was LATENT, not active, and is fixed on the strength of being reachable.** `extract_claims` now returns a `Counter`; `classify_findings` takes a multiset and **refuses a set with a TypeError** rather than coercing it, because treating a set as one-of-each would be a different wrong answer. Where base > 0 and head > base the surplus is introduced, the tie-break is the tail in document order and is DECLARED rather than measured, and every finding in such a group carries `present_at_base_ambiguous: True`, matching the standard `blocker_delta` already set by refusing to pick. **Figures unchanged after the fix**, which is the point: `claim_diff --base main` at `da728db` gives 280 total, 55 at base, 225 introduced, itemised 206 + 7 + 8 + 4 = 225 and 206 + 62 + 8 + 4 = 280. **The six safe sites carry their reason in the code**, not in this row: `gate_probe.arm_delta` (line-bearing key, same-tree, cannot collide), `blocker_delta`'s union and multiset difference (coordinate-free key, cross-commit, collides by design and counts rather than picks), `quarantine_liveness.cause_of` and `also_blocked_by` (fired sets keyed identically to the quarantine entries, so the key IS the unit and there is no occurrence to misattribute; checked rather than inherited), and `f25_exposure._manifest_surfaces` (file paths, no multiplicity). **A count-only check cannot catch this class, so none was added:** the seven new tests in `tests/test_claim_diff.py` assert attribution and which occurrence carries it. Control: reverting `classify_findings` to the set-membership body fails 4 of them, including the 210/213 one; restored and all 25 pass. **The audit renews itself.** `tests/test_setop_inventory.py` re-runs the AST enumeration every test run and fails on any comparison site with no classification, so a new set difference cannot land unclassified; a planted site is detected, and a stale entry naming a site that no longer exists also fails. |
| **N42** | **The 70% remediation had to be drafted on every surface, and TWO premises it rested on were wrong.** | **2026-07-30 (this session)** | **DRAFTED AND COMMITTED AS PUSHED:197eb99, CONDITIONAL ON A DECISION NOT YET CONFIRMED. See ADR 0002.** Options 1 (derive a figure) and 3 (remove the sentence) remain open; if either is chosen `PUSHED:197eb99` is discarded, costing one commit and no published change. **Premise 1 that was wrong: the surface count.** ADR 0002 and the session brief both said FOUR reader-facing surfaces. Re-derived before editing, the answer is **ten locations across six files**. The original predicate was produced by command, which is the rule, but was chosen by hand and matched only phrasings containing **70%**; the identical claim is also published as its complement, `roughly 30% of the EU AI Act`, at six locations the pattern never looked at. A predicate does not make an enumeration complete, a predicate that COVERS THE CLAIM does, and this is measurement rule 4c failing one step BEFORE the command. **Two of the six newly found are `docs/what-regula-does-not-do.md:6` and its verbatim mirror `site/llms-full.txt:291`, which is the sharpest finding here:** the document ADR 0002 names as the QUALITATIVE BASIS for removing an unsourced proportional figure was itself publishing one, `static code scanning may fundamentally address only about 30% of the EU AI Act`. The ADR's argument was circular and nobody had noticed. The ADR further asserted that `site/llms-full.txt` carried the qualitative statement **but not the figure**; it carried the figure. **Premise 2 that was wrong: the replacement wording.** The brief directed `a substantial majority of the Act's obligations are organisational`, citing that same table. Derived by parsing it: **10 articles Regula can address, 9 it cannot, 19 rows, and 8 of the 10 addressable are scaffold-only, reference-only or medium, leaving 2 of 19 as high-confidence code coverage.** Nine of nineteen is not a substantial majority of the table's own rows, and a 19-article coverage map cannot support a statement about the SHARE of a 113-article regulation whatever quantifier is chosen. Publishing it would have replaced an unsourced proportional claim with an unsourced proportional claim, which is the ADR's own argument against option 1. **Raised as a boundary before anything was written; the owner ruled to drop the proportion entirely and claim the KIND of obligation rather than its share.** **No locale variant carries the claim**, all six locale surfaces checked individually, and `site/locales/de.html:586` and `site/locales/pt-br.html:603` already carried the qualitative framing with no percentage, so the English pages were the outliers. **Consequence handled in the same commit:** removing both `30%` and `70%` from two pages orphaned **four LIVE quarantine entries** (`quarantine_liveness.py` at `da728db`: 29 entries, 21 live, 8 silent). Burned down through the file's own `_burn_down` protocol with disposition `corrected`; entries 29 to 25, `_count` 29 to 25, `burned_down` 15 to 19, ceiling falls by four automatically, and `tests/test_claim_quarantine.py` re-measures every record so a burn-down on a false premise fails the suite (17 passed). Removing an entry whose claim no longer exists makes the gate strictly stricter, so this is cleanup and not suppression. `site/guides/eu-ai-act-healthcare.html '70%'` untouched: an unrelated model-accuracy example. **KNOWN AND NOT FIXED:** `site/blog/blog-static-analysis-ai-compliance.html:189` is N30(1), held green by the word `source` inside `source-code footprint`, and the replacement keeps that phrase, so it stays held green by the same word. Gate-scope work, out of this session's scope. **The ADR's `15 files` figure was stated with no commit**; the tracked total is **16 at `da728db`**, and it moves because the records discussing the claim are inside the corpus, which is rule 24 above. Corrected to state the commit. |
| **N43** | **The published gap-demo figures are not reproducible from the repository.** `data/gap_demo.json` (generated 2026-07-28T15:16:46Z, main tree) and the site panels `tests/test_gap_demo.py` binds to it publish overall **9** with Article 11 at **25**; every clean checkout reproduces **6** and **0**. | 2026-07-30 (directive session, item 2) | **DIAGNOSED WITH A ONE-VARIABLE CONTROL BOTH WAYS; READER-FACING CORRECTION OWNER-GATED.** `build_gap_demo.py --check` is rc=1 in clean detached worktrees at `7b154f8` (tree `689898bd`), `969f3a8` and `e8b5986`, and rc=0 in the main tree at `839b031`. Cause: the main tree's tracked fixture contains gitignored state, `tests/fixtures/sample_high_risk/.regula/registry/7093442f77de75f5.json` (dir dated 11 April) plus `garak.regula.yaml` (16 April, ignored BY NAME at `.gitignore:66`), and `scripts/compliance_check.py` credits any `.regula/*` match as the `regula_docs` component, one of four, 25 points. First hypothesis (the garak file) REFUTED by its own control: copied into a clean worktree, rc stayed 1. Second proven both ways in the `e8b5986` worktree via `cp -r`/`mv`, nothing deleted: **WITH `.regula/`: rc=0; WITHOUT: rc=1.** So the artefact the Class 1 remediation built embeds an input that exists only on this machine, the exact class its own docstring rejected the repo-self-scan for (rule 4b). NOT a regression at the held commits: the contamination predates them by months. **Not fixed here because the honest repair changes published percentages (9 to 6, 25 to 0) on reader-facing pages, excluded by this session's scope; boundary raised.** Durable fix when sanctioned: make `build_gap_demo.py` refuse untracked or ignored inputs inside the fixture it scans, remove or track the contaminating files, regenerate artefact and panels in the same change. Interim detection: both paths are in the tree-guard baseline (N45), so any further mutation of them is named at the next measurement. |
| **N44** | **The twelve modified files of 30 July are ATTRIBUTED; cross-context sessions are the operating environment, not an anomaly.** | 2026-07-30 (directive session, item 1a) | **CLOSED on the second incident; the FIRST (the silent revert) remains untested.** The files were written by Claude session 70177dfc-58cd-4c7b-8c30-8f1d0522abf1 (a session id, not a git object, so deliberately not backticked; see N39c) running from the HOME-workspace project context (`~/.claude/projects/-home-mkuziva/`), 13:41:42Z to 17:48:31Z: 41 tool calls on the twelve files in the window, Edit timestamps matching file mtimes to the second (`references/annex_iv_template.md` edited 16:47:41Z, mtime 17:47:41.845 +0100), last session event matching the repo-root `.handover.md` stamp 18:48:31 to the second. The transcript parser was CONTROLLED first against this session's own transcript (4 known hits found). That session ran the suite three times; its leftover result file reads `2581 passed, 6 subtests passed in 774.86s (0:12:54)`; the "6 subtests" phrasing is the repo's gitignored `.venv` (pytest 9.1.1, matching CI's pin) against system pytest 8.4.2, whose summary prints no subtest clause. Its records live outside this repo because programme records key off the directory a session starts in; that is the mechanism, and another home-workspace session was OBSERVED LIVE during the directive session (transcript mtime 22:18). **The silent-revert incident's primary record was NOT FOUND**: searched the reflog (no operations in the window), LEDGER/STATE phrasings, the session 70177dfc transcript (44 watcher/inotify lines, all unrelated hook documentation), and every home transcript for "byte-identical to HEAD / reverted to HEAD / identical to the committed" (one hit, 18:25:42Z, StreetSignal's deliberate Cape-Town-Dash restore). Cause untested from inside this session; what would test it is the incident's source record or time window. The cross-context mechanism explaining it is **reasoned, not evidenced**. |
| **N46** | **`7b154f8` and `969f3a8` are FULL-SUITE VERIFIED for the first time, seven sessions after landing.** Both were previously verified only by targeted tests and the six gates. | 2026-07-30 (directive session, item 2) | **VERIFIED IN CLEAN DETACHED WORKTREES, AND THE EVIDENCE SUPPORTS APPROVING `969f3a8`.** At `7b154f8`, tree `689898bd`: `1 failed, 2455 passed, 34 skipped in 1207.42s`; custom runner `1375 passed, 0 failed, 4 skipped (978 test functions)` rc=0; five of six fast gates rc=0. At `969f3a8`, tree `795977e6`: `1 failed, 2455 passed, 34 skipped in 1164.94s`; custom runner `1375 passed, 0 failed, 4 skipped (978 test functions)` rc=0; five of six fast gates rc=0. **The single failure is identical at both commits, `tests/test_gap_demo.py::TestArtefactIsProducedNotWritten::test_artefact_matches_a_fresh_run`, and it is N43**, the contamination that predates both by months; the held commit therefore changes NO test outcome relative to its own parent, which is the like-for-like comparison the approval needs. The sixth gate red at both is the same N43 cause. **The 34 skips are explained, not assumed:** re-run with `-rs`, 30 of them report `hooks/ not present (local dev file, not tracked in git)` across `test_hooks_audit.py` (27), `test_audit_scoping.py` (2) and `test_audit_surface_conformance.py` (1), which is a by-design absence in any clean worktree; the main tree, which has the untracked `hooks/`, reports 0 skipped. **Caveat carried into the approval:** approving `969f3a8` is orthogonal to N43, but N43's repair will later move the published gap-demo figures (9 to 6, Article 11 25 to 0), so approval is given knowing that correction is pending. |
| **N47** | **My own stamp integration broke a rule the repository enforces, and the six fast gates could not see it.** `c812ceb` added `from tree_guard import stamp` to nine scripts; `build_gap_demo.py` and `site_facts.py` had no `sys.path.insert` because until then they imported no sibling. | 2026-07-30 (directive session) | **FIXED AT ROOT in `f4e98d7`; `c812ceb` IS A RED INTERMEDIATE COMMIT AND IS RECORDED AS SUCH.** Caught only by the full suite at HEAD `9224a42` (`1 failed, 2594 passed in 1475.56s`): `tests/test_source_of_truth.py::test_sibling_importers_have_path_insert` reported `Modules bare-import siblings without sys.path.insert self-protection: ['build_gap_demo.py', 'site_facts.py']`. All six fast gates were rc=0 across that same window, so this is measurement rule 5 in live form: the fast gates test something narrower than the rule set, and a green gates block is not a green tree. The rule broken is `.claude/rules/python-scripts.md`, which exists because `import classify_risk` from a clean interpreter failed until July 2026. Fixed by adding the self-protection to both files with the reason inline, not by exempting them. Controls: fail-before is the suite line above, pass-after is `8 passed` on `tests/test_source_of_truth.py`, and the behaviour the rule is actually about is proven by running both scripts from a foreign cwd (`cd /tmp && python3 /home/mkuziva/getregula/scripts/build_gap_demo.py --check` rc=0). **Lesson for the class, not the instance:** a change that touches every measurement script at once needs the full suite before it is called done, because the gates it stamps are exactly the instruments that cannot see it. |
| **N48** | **The session's closing verification took three attempts, and the second was made worthless by my own mid-run commit.** | 2026-07-30 (directive session, close) | **CLEAN AT `346a494`, third attempt; the two earlier attempts are recorded rather than discarded.** Attempt 1, at `9224a42`: `1 failed, 2594 passed in 1475.56s`, the failure being N47. Attempt 2, launched at `f4e98d7` and CONTAMINATED when my commit `346a494` landed mid-run: suite `2595 passed in 1646.65s` rc=0 and runner `1386 passed, 0 failed, 0 skipped (1043 test functions)` rc=0, both green but describing a tree that changed underneath them, which under this programme's own rule describes no single commit. **Attempt 3, quiescent, commit and tree captured to a file BEFORE launch and nothing else touching the tree: `346a494`, tree `e246dadc3cb88ef2d843d61ad4e16523c6d99007`, `2595 passed in 1302.35s`, rc=0 from `$?` after redirection, zero `FAILED` lines, tree confirmed still `346a494` and clean afterwards.** Six fast gates rc=0 each at the same commit; `self-test` rc=0; `doctor` rc=0. **The mid-run mutation is N45's lesson recurring inside the session that recorded it, by the same author, roughly forty minutes later**, which is this row's real content: the rule was written, published, and then broken, so knowledge is demonstrably not the countermeasure. What would prevent it is a launch-time refusal to start a long run on a dirty tree and to commit while one is in flight, which is harness behaviour and runs into the same boundary as `tree_guard`'s WHO-half (N45). **Reasoned, not evidenced:** a repository-side approximation exists (a lockfile written by the runner, checked by a pre-commit hook) and is cheap to reverse, but building a mechanism at the close of a session to catch that session's own mistake is how unproven scaffolding enters a codebase, so it is deferred with the reasoning recorded. The observation that would overturn the deferral is a third occurrence. |
| **N49** | **The N43 class is closed at the point of creation: a generator can no longer build a published artefact from inputs a clone does not have.** The instance (the wrong published figures) remains owner-gated and unchanged. | 2026-07-31 | **CLOSED FOR THE CLASS in PUSHED:30fd6e8, after an adversarial review falsified the first attempt.** `tree_guard.untracked_inputs(path, root=None)` returns every path under a target whose porcelain code is `??` or `!!`, using `--ignored=matching` (the load-bearing flag: a plain porcelain call reports NOTHING for a gitignored file, which is how a `.regula/registry/` directory fed the published gap-demo figures unnoticed) and `-z` (so names with spaces or non-ASCII bytes survive unescaped). `assert_inputs_tracked` raises `UntrackedInputError` naming them; both directory-scanning generators refuse on the write path and warn on `--check`. **Measured by enumeration over every tracked fixture-bearing directory, not by sampling: 3 contaminated paths across 2 directories.** `tests/fixtures/sample_high_risk/.regula/` and `.../garak.regula.yaml` are LIVE (scanned by `build_gap_demo.py`, reach the published figures); `tests/fixtures/sample_compliant/.regula-baseline.json` is LATENT (`grep -rn sample_compliant scripts/*.py` returns nothing). `benchmarks/synthetic/fixtures` is CLEAN, 38 tracked files. **The first version of this work was falsified by the adversarial reviewer and the falsification is the reason to trust the second.** Its wiring test asserted only that the string `assert_inputs_tracked` appeared in the generator source; the reviewer moved the guard to AFTER the write and every test stayed green while the contaminated artefact was rewritten. Replaced by a behavioural test that clones the repo, overlays the working-tree modules, plants the real contamination shape, runs the real entry point, and asserts rc!=0 AND that the artefact bytes are unchanged, paired with a clean-clone test so an unconditional refusal cannot pass both. The reviewer's mutation was re-applied afterwards and the new test caught it (`1 failed, 12 passed`; restored, `13 passed`). **Also fixed from that review:** the predicate wrongly reported modified, deleted and renamed TRACKED files, so an ordinary uncommitted edit blocked regeneration while advising "track it"; a nonexistent target returned `[]` instead of raising, which made a typo'd path a permanent pass (measurement rule 4); and the advisory git call could break the shipped package outside a git checkout. **The `--check` path WARNS rather than refusing, and that is a stated limit, not a suppression.** `--check` asks "does the committed artefact match a fresh run", and in a tree carrying this contamination the honest answer to THAT question is yes, because both sides are contaminated identically. Strengthening it would turn the gate red until the figures move, which is the owner decision. **The phrase "impossible to miss" is withdrawn:** the reviewer established that no CI job runs `--check` at all and that `tests/test_gap_demo.py` captures output while asserting only the return code, so the warning has no automated consumer. **What would close the instance:** owner sanction to remove the two contaminating paths, regenerate, and cascade 9 to 6 and Article 11 25 to 0 across `site/index.html` and both locale pages; the `--check` warning then becomes a refusal and this row closes. |
| **N51** | **The same class is OPEN on the most-published number in the repository, the 83.5% precision figure, and closing it is an owner decision rather than a code change.** | 2026-07-31 (adversarial review) | **OPEN, ESCALATED, NOT ACTED ON.** `benchmarks/results/random_corpus/PRECISION.json` holds `overall_precision: 0.835`, published on README, `docs/TRUST.md`, `docs/MODEL_CARD.md` and the site. Its corpus is gitignored BY DESIGN: `.gitignore:130` excludes `benchmarks/results/random_corpus/*.json` and `:138` excludes `benchmarks/results/app_*.json`; 54 JSON files exist there against 4 tracked, and 19 against 7 tracked at `benchmarks/results/`. `benchmarks/label.py:86` globs that directory to write the tracked `benchmarks/results/PRECISION.json`, and `claim_auditor.py:886-887` reads both as the authority for which precision percentages may be published. So the statement this session's work rests on, "an artefact that backs a published number must be derivable from tracked content alone", is NOT true of the repository's headline figure. **Why it was not fixed here:** tracking that corpus means committing third-party source code with its own licence positions, and the `.gitignore` comment says it is regenerable via `rescan_corpus.py`, which may be a deliberate and defensible design. Both readings are open and only the owner can rule. **Also recorded here, same class, theoretical:** a tracked symlink pointing outside the repository defeats any git-based guard; none exists in either guarded fixture today. |
| **N52** | **`site_facts.py` enumerates by working-tree glob while four sibling instruments enumerate by `git ls-files`, so an untracked test file is counted into every published test-count surface.** | 2026-07-31 (adversarial review) | **CLOSED 2026-07-31 (session B) in PUSHED:290e926, at the invariant rather than at the enumeration.** The fix is NOT to switch `site_facts` to `git ls-files`: the legitimate workflow is to add a test file, regenerate, cascade and commit all of it together, and an enumeration that ignored untracked files would silently publish a count that disagreed with the very suite the developer just ran. Instead the invariant is stated and enforced: **every key in `counts.tests.per_file` must name a file git tracks**, because `per_file` records exactly which files contributed. `site_facts.untracked_test_contributors(per_file, tracked=None)` is the predicate; `count_tests` WARNS at generation naming each stray file (a refusal there would block the legitimate workflow); and `tests/test_site_facts.py` enforces it AT REST, so a contaminated artefact cannot be committed. **Controls both ways, end to end, not on a fixture:** planting a real untracked `tests/test_planted_untracked_probe.py` produced the warning naming it and `untracked_test_contributors -> ['test_planted_untracked_probe.py']`; regenerating from that tree and running the at-rest test gave `FAILED ... test_untracked_contributors_defaults_to_asking_git`; removing the probe and restoring the artefact gave `10 passed` with `data/site_facts.json` byte-identical. **Four tests written before the implementation, all four failing with `AttributeError` beforehand.** Incidental repair: `subprocess` was imported inside `count_tests` and is now a module-level import, which is what the two functions that need it require. **What this does NOT close:** `total_collected` still comes from a working-tree `pytest --collect-only`, so a MODIFIED tracked test file changes the count without tripping this guard. That is a narrower hole (the content is in the repository, and the cascade gates compare published surfaces against the canonical), and it is recorded here rather than left implicit. **Three further holes in this guard, all found by the adversarial review of the closing diff and all OPEN, are recorded as N55 rather than hidden in this cell.** *Superseded original statement of the finding, retained because the row must show what was believed when it was raised, and marked so it cannot be read as current:* ~~"`scripts/site_facts.py:238` uses `tests_dir.glob(...)` and `:221` runs `pytest --collect-only` over the working tree ... Inert at every commit in practice ... Recorded rather than fixed because switching `site_facts` to `git ls-files` deserves its own measurement and its own commit."~~ Three corrections to that text: the line citations moved to `:268` and `:251` when the predicate was inserted above them; "inert at every commit in practice" is **wrong**, because the class fired on 2026-07-31 when a still-untracked `tests/test_tracked_inputs.py` was counted into the canonical artefact and cascaded to nine surfaces (correct only because the file happened to land in the same commit); and the closing sentence describes a fix that was deliberately NOT taken, for the reason given at the head of this cell. The sibling comparison stands: `claim_auditor.py`, `f25_exposure.py`, `merge_blockers.py` and `check_decompositions.py` all enumerate with `git ls-files`. So does the consequence the reviewer demonstrated: with the new test file absent, a tracked-content-only checkout does not merely count differently, it fails to collect (`2159 tests collected, 1 error`, `ModuleNotFoundError: No module named 'test_tracked_inputs'`), because tracked `tests/test_classification.py` imports it. |
| **N53** | **A gitignored root policy file shadows the tracked one for both artefact generators, and no git-based guard on the fixture can see it.** | 2026-07-31 (adversarial review) | **OPEN, MEASURED INERT TODAY, RECORDED.** Both generators run the CLI with `cwd=REPO_ROOT`, and `scripts/policy_config.py:42-53` resolves `$REGULA_POLICY`, then `./regula-policy.yaml`, then `./configs/regula-policy.*`, then `$HOME/.regula/regula-policy.*`. A gitignored `regula-policy.yaml` exists at the repository root on this machine (`.gitignore:59`, confirmed by `git check-ignore -v`) and shadows the tracked `configs/regula-policy.yaml`. `assert_inputs_tracked(FIXTURE)` inspects only the fixture subtree and cannot see it. **One-variable control by the reviewer: parking the root policy and re-running both commands produced identical output apart from the assessment timestamp**, so this is a structural gap and NOT a live wrong number. `$HOME/.regula/` can never be covered by a git-based guard at all. The durable fix is to run artefact generators with an explicit pinned policy path rather than resolution-by-search, which is a design change beyond the unit this session closed. |
| **N50** | **The mid-run editing defect occurred a THIRD time, in the session that recorded the second, and N48's own overturning criterion is therefore met.** | 2026-07-31 | **RECORDED, DEFERRAL OVERTURNED, GUARD NOT YET BUILT, AND THE REASON IS STATED.** The full suite launched at 01:19 at `cd6ff3c` was still running when `tests/test_tracked_inputs.py` was created, moving collection 2595 to 2603 underneath it; the run was stopped rather than allowed to finish, because a result describing a tree that changed underneath it describes no commit. It happened a FOURTH time in the same session, deliberately this time: a second clean run was stopped early once the adversarial review returned findings that required editing the tree, on the grounds that finishing a run whose result would be superseded is worse than stopping it. **N48 stated in advance: "The observation that would overturn the deferral is a third occurrence."** It has occurred, so the deferral is overturned by the criterion the ledger set rather than by a later opinion, and the next session inherits a decided question. **Deliberately not built here.** The obvious mechanism, a pre-commit refusal keyed on a runner lockfile, has a flaw a rushed implementation would ship: an orphaned lockfile from a killed run blocks every subsequent commit, which is worse and more confusing than the failure it prevents. It needs a PID-liveness check and an explicit override. Building that at the close of a session, to catch that session's own mistake, is the pattern N48 itself warns produces unproven scaffolding. **Reasoned, not evidenced:** a PID-liveness lockfile is the cheapest correct form and is trivially reversible (delete the file, drop the hook). The observation that would overturn THAT judgement is a further occurrence before the guard lands. |
| **N54** | **The mid-run editing defect has now occurred FIVE times, and the fifth exposes it as structural rather than careless.** | 2026-07-31 (session B) | **RECORDED; the guard N50 defers is now the single highest-value process fix, and the cheaper mitigation is stated.** The step-1 baseline suite was still running when editing began, so it was stopped. **Why this one is not simple forgetfulness:** the operating directive requires a full-suite run during step-1 state re-establishment AND work in step 3, the suite takes 15 to 25 minutes, so a session following both literally must either idle for that duration or overlap them. **Reasoned, not evidenced:** the step-1 baseline suite carries little decision value in a session that will modify the tree, because the claim that matters is the FINAL suite on the committed state, which must run regardless; the decisive cheap step-1 check is the six fast gates plus the linter, which run in seconds. Assumption: no defect exists that the full suite catches while all six gates AND the final suite miss it. The observation that would overturn it is a session where the step-1 suite fails but the gates and the final suite pass. Cheapest reversal: reinstate the step-1 suite, since nothing depends on its absence. **This does not retire N50**; a lockfile guard with a PID-liveness check would have refused the edit and forced the choice explicitly, which is better than relying on either discipline or this reasoning. |
| **N55** | **The N52 guard has three holes of its own, and one of them lets its enforcement test pass without ever consulting git.** | 2026-07-31 (session C, adversarial review of the N52 diff) | **OPEN, ALL THREE MEASURED, NONE FIXED IN THE COMMIT THAT RAISED THEM.** (a) **Vacuous pass, the serious one.** `untracked_test_contributors` swallows `OSError`/`CalledProcessError` and returns `[]`, which is the PASS value, so the at-rest test `test_untracked_contributors_defaults_to_asking_git` cannot distinguish "git says every contributor is tracked" from "git never ran". Measured in place with `REPO` repointed at a non-git directory: `REAL -> []`, `NON-GIT -> []`, `NON-GIT + BOGUS CONTRIBUTOR -> []` (silent), `IN REPO + BOGUS CONTRIBUTOR -> ['test_this_file_never_existed.py']`. This is measurement rule 4 ("a blank gate is not a green gate") violated by the single test carrying the entire guarantee. The swallow is justified in the docstring for the WARNING path, where `scripts/` ships as a PyPI package outside any checkout; that justification does not transfer to the ENFORCEMENT path. (b) **Non-recursive glob against a recursive collector.** `per_file` is built from `tests_dir.glob("test_*.py")` (`:268`, top level only) while `total_collected` comes from `pytest --collect-only tests/` (`:251`, recursive). Demonstrated on a scratch tree under this repo's own `python_files = ["test_*.py"]`: 3 collected, `per_file` sees `['test_top.py']`. So an untracked `tests/<subdir>/test_*.py` (or an untracked `tests/<subdir>/conftest.py`) inflates `total_collected`, cascades to the README badge, and produces NO `per_file` key, so the predicate cannot see it and the at-rest test stays green. (c) **One-directional.** The predicate iterates `per_file` keys, so a tracked test file DELETED from the working tree without `git rm` drops its key, lowers the count, and reports `[]`. "Every key names a tracked file" does not imply "every tracked file is a key", and only the second direction catches under-counting. **Also recorded, lower consequence:** the row's phrase "a contaminated artefact cannot be committed" is an overstatement and is withdrawn, because no git hook enforces it (`.git/hooks/` holds only samples) and CI runs pytest on `main` only (`.github/workflows/ci.yaml:2-6`), so nothing runs it on this branch; the three pre-existing tests that fake `subprocess.run` now also feed that fake to the new predicate, which parses `"2678 tests collected"` as a `git ls-files` result and declares all 101 tracked files untracked without failing anything; `claim_auditor.py --verify-facts` derives its canonical from a working-tree `sf.compute()`, the same limitation N49 recorded for `build_gap_demo --check`; the basename comparison is unsound by construction (a tracked `tests/fixtures/**/test_x.py` would mask an untracked top-level `test_x.py`), measured inert today because no tracked `test_*.py` exists outside the top level; and `claim_auditor.py:1197` carried a `"2354"` canonical hint key, 258 out of date. **That last sub-item is CLOSED in PUSHED:7dba517**, which replaced the literal with `str(facts["counts"]["tests"]["total_collected"])`; it is recorded here rather than left reading "still carries", because an adversarial review found that the closing commit mentioned it in neither its message nor N56, which is how an open item silently disappears. (a), (b) and (c) above remain OPEN: PUSHED:7dba517 did not touch `scripts/site_facts.py`. |
| **N56** | **The landing page published a test count 258 short for three days while BOTH gates that exist to catch that reported green, and a second surface was 1,395 short and covered by no gate at all.** | 2026-07-31 (session C) | **CLOSED FOR THE CLASS in PUSHED:7dba517; every instance corrected.** `site/index.html` published `<strong ...>2,354</strong> tests` since `bb52488` (2026-07-28) through cascades to 2,595, 2,608 and 2,612; `site/locales/de.html` and `site/locales/pt-br.html` published `2.349`. All three are manifest surfaces. **Two INDEPENDENT blindnesses, either alone sufficient.** (1) Every `COUNT_TEMPLATES` entry joined number to unit word with `\s+`, and `</strong> ` is not whitespace, so nothing matched and `_stale_values` nominated nothing. (2) The candidate scanner `(?<![\w,.])(\d{1,3},\d{3}|\d{4})(?![\w,.])` cannot see dot-grouped `2.349` at all, so the two locale pages were unreachable by a second route; and `_swap` wrote `f"{new:,}"`, so even once detected a German page would have received an English-formatted number. **`claim_auditor --verify-facts` shared blindness (1)** through `(?:\s*|%20)`, while its own comment asserted it "matches the shape list scripts/cascade_count.py already uses ... so the two instruments agree". It now IMPORTS `cascade_count.GAP` and a test asserts identity, because repairing one instrument silently falsifies that comment otherwise. **The fix is a template widening, NOT a heuristic:** the gap accepts whitespace or complete HTML tags and nothing else, the unit word is still mandatory, and the two pre-existing controls (an unrelated number in the same sentence; years behind markup) pass before and after. **Control both ways on the real files:** re-planting `2,354</strong> tests` gives `--verify-facts` rc=1 naming `site/index.html:L346 ... (context: '2,354</strong> tests')` and `--check` rc=1 naming the surface; both were rc=0 on that identical state beforehand. **The larger instance was found by enumeration, not by reading (rule 4c):** `docs/architecture.md:53` published "45 test files, 1,223 tests", short by 1,395, absent from the manifest AND from `claim_auditor.VERIFY_FACTS_FILES` where `claim_auditor.py:1109-1114` had recorded it as a known gap parked behind 1.5c. Corrected to 101 / 2,622, both re-derived. `docs/CONTINUITY.md`'s "2,600+ tests" is left alone: it is still true and hard-coding a number into it would create maintenance where none is needed. **What actually closes the class is that the at-rest test no longer trusts either the tool or the manifest.** `TestEveryPublishedSurfaceCarriesTheCanonicalCount` enumerates tracked `.md/.html/.txt` via `git ls-files`, uses its own matcher rather than `COUNT_TEMPLATES`, names its exemptions (ledger, changelog, rules files and other verbatim records that must keep historically-true numbers), and is paired with a test asserting the enumeration actually reaches README, index.html, TRUST.md, de.html and architecture.md, so an exemption typo cannot make it pass by scanning nothing. **Widening reach surfaced two false positives and they were fixed, not allowlisted:** architecture.md's per-module "18 patterns" and "14 patterns" (both verified correct against `credential_check.SECRET_PATTERNS` and `gdpr_patterns.GDPR_PATTERNS`) were read as failed attempts at the repo-wide 419. `VERIFY_FACTS_FILES` entries may now be `(path, {facts})`; architecture.md is scoped to `{"tests"}`, held honest by a test requiring a scoped entry to still flag a planted stale value for a fact it declares and to ignore one it does not. **Withdrawn as a result of this row:** `docs/TRUST.md`'s standing sentence that every published number is reproducible from a checkout was, for three days, false of the landing page itself, and `test_repo_is_currently_in_sync` is now documented as insufficient on its own because it asks the tool whether the tool found drift. |
| **N57** | **The adversarial review of N56 found eleven items; six were fixed in the same session, five are open and recorded here rather than absorbed.** | 2026-07-31 (session C, adversarial review) | **PARTIALLY CLOSED in PUSHED:d0ba6f0; five OPEN.** *Fixed and tested:* the entity/comment gap, the block-boundary crossing, `_swap`'s multi-substitution, the `(path, {facts})` scoping silently dropping `frameworks` coverage on `docs/architecture.md` (which publishes "13 frameworks" at :28 and :88, both matching the gate's own pattern, and is now scoped `{"tests", "frameworks"}`), the at-rest matcher's case-sensitivity and its blindness to the badge form `tests-NNNN%20passing`, and `claim_auditor._GAP_SOURCE`, which makes a failed import observable where value-equality alone could not distinguish "imported" from "fell back to an identical copy". *Also fixed, found by the repair itself rather than by the reviewer:* `tests/test_published_count_manifest.py` used a `(?<!\d)` lookbehind, so at one canonical value it failed naming `scripts/report.py` where every hit was the hex colour `#dc` plus four digits. That is the SAME defect `cascade_count._patterns` already carries a comment about; it is now `(?<!\w)`, with a both-ways control asserting a hex colour and a hash path do not match while a real published claim still does. **OPEN, 1:** `_stale_values` has an undisclosed 50% magnitude floor (`lo = int(new * 0.5)`), so the cascade tool structurally could not have seen `docs/architecture.md`'s 1,223 against a canonical of 2,618; that file was corrected by hand and is caught by the at-rest test and by claim_auditor, neither of which has a floor, so the class is not open, but the claim that manifesting the file brought it under the cascade tool is withdrawn. **OPEN, 2:** `.claim-allowlist` lines 36-40 are RANGES, not values (`\b2[,.]?3\d{2}\s+tests?` matches both `2,354 tests` and `2.349 tests`; `\b1[,.]?2\d{2}\s+tests?` matches `1,223 tests`), so a third instrument was silent on those exact strings by allowlist. It feeds the sourcing scan rather than `--verify-facts`, so it did not cause N56, but N56's phrase "both gates" undercounts the instruments involved. **OPEN, 3:** `claim_auditor --verify-facts` derives its canonical from a working-tree `sf.compute()`, so locally it compares a contaminated published number against an identically contaminated canonical; same limitation N49 recorded for `build_gap_demo --check`. **OPEN, 4:** the at-rest enumeration exempts `scripts/`, which swallows one real HTML file, `scripts/dashboard/index.html`; measured to carry no count-shaped claim today. **OPEN, 5:** `wrong_pat` in `claim_auditor` leaves a dotted literal unreplaced, so a stale dotted count is reported as "found 349" rather than "found 2,349". The gate fires correctly; only the message is wrong. |
| **N58** | **The tracked handover still presented session 4 as “START HERE” after 62 later commits had landed.** `docs/improvement/HANDOVER.md` had not changed since `79debb9` on 2026-07-28, while the actual tip before this repair was `1f3da84` on 2026-07-31. Its opening Git state and verification figures were historical but unlabelled as such. | 2026-07-31 (continuity audit) | **CLOSED as a continuity defect.** The first screen now names this ledger as the single durable current record, directs chronological readers to the newest `STATE.md` checkpoints, and marks the remaining narrative as historical before its old “START HERE” section. `python3 -m pytest tests/test_handover_continuity.py -q` is the guard; the control failed before the notice because both required section markers were absent, then passed after it. The mutable historical counts were deliberately not rewritten: the ledger's fixed-point rule explains why copying them forward creates another stale snapshot. The new test is wired into the custom runner and the canonical published test count moved from 2,627 to 2,628 through `site_facts.py` followed by `cascade_count.py --apply`, including EN, DE and PT-BR surfaces. |
| **N59** | **The optional governance-feed cache was fatal on a read-only filesystem.** `fetch_governance_news()` always called `_save_cache()`, including after all network sources failed, and `_save_cache()` let `OSError` escape. The required custom runner reproduced it in `test_smoke_feed`: the CLI returned exit 2 with `[Errno 30]` instead of a JSON envelope. | 2026-07-31 (continuity audit verification) | **CLOSED for cache filesystem errors.** `_load_cache()` now treats an unreadable cache like a miss and `_save_cache()` treats an unwritable cache as disabled; neither changes the feed result. The existing smoke test now plants a cache directory whose `mkdir()` raises `OSError`, so the filesystem branch executes on writable development machines too. `python3 -m pytest tests/test_classification.py -q -k smoke_feed` and `python3 -m pytest tests/test_reliability.py -q` pass, 1 and 11 tests respectively. The pre-fix full custom runner remains honestly red: 1,380 helper assertions passed, 3 failures, and 1,060 functions; the chained pytest, self-test and doctor commands did not run after that failure. |
| **N60** | **The commercial-defensibility gate exposed a gap between a large green suite and claim-ready evidence.** Current PyPI is 1.7.4 while local source is 1.9.0; restricted verification fails one Git-worktree control, eight localhost timestamp tests and the home audit-path doctor check, while exact unrestricted controls pass; the merge blocker remains red; active public surfaces contradict the product's own legal limitations, regulatory status and security record. The first protocol draft also had tautological discovery, correlated samples presented as independent, unreachable comparators, non-equivalent outcome adapters and subjective gates. | 2026-07-31 to 2026-08-01 (commercial-defensibility session) | **EXECUTED; RESULT `STOP`.** Preregistered in `5bd2112`; pre-results verifier repair `84e0118`; post-result acquisition-blocker correction `056bcf2`, with the frozen exit-1 control retained. The corrected acquirer obtained 12/12 exact repositories and 12/12 licence records. Two fresh runs per synthetic tool were byte-identical after normalisation. Local 1.9.0: Candidate A TP 0, FP 0, FN 40, TN 40, recall **0/40**, descriptive Wilson 95% interval 0.000–0.0876; Candidate B identical. Transparent baseline A: TP 40, FP 4, FN 0, TN 36, precision **40/44**, recall **40/40**; baseline B: TP 40, FP 0, FN 0, TN 40, precision and recall **40/40**. These correlated constructed families are diagnostic, not external accuracy. Twelve-repository operations retained every outcome: local and public Regula each exited 0 on 9/12 and 1 on 3/12; their second-run stdout/stderr and exits matched 12/12. Two executable competitors exited 0 operationally on 12/12, but accuracy is UNTESTABLE without equivalent adapters or human repository labels. Candidate C remains MODEL-PROVISIONAL with 0/30 independently human-labelled scenarios. Local evidence-pack strict verification passed; public 1.7.4 strict verification failed exit 2 on its legacy manifest. Network behaviour remains UNVERIFIED because namespace denial was unavailable and the socket control broke `ssl` import before execution. Verdict: TECHNICAL_EVIDENCE FAILED; COMPARATIVE_ADVANTAGE NOT_DEMONSTRATED; PUBLIC_CLAIM_INTEGRITY FAIL; REGULATORY_CURRENCY PARTIAL; OPERATIONAL_READINESS FAIL; DEMAND_EVIDENCE UNVALIDATED; OVERALL_DECISION STOP. Final verification: custom runner 1,386/1,386 exit 0; pytest **2,633 passed, 6 failed, exit 1** because the 11 harness tests move live collection to 2,639 while public canonical claims remain 2,628; two of six fast gates fail on that mismatch, four pass; merge blocker remains exit 1; unrestricted doctor and self-test pass. The public-claim cascade is explicitly prohibited this session and no test was hidden to manufacture green. Results: `docs/commercial/COMMERCIAL_DEFENSIBILITY_REVIEW_2026-07-31.md` and `benchmarks/commercial_v1/results/summary.json`. Existing items **F25, F30, N35, N43, N50, N54, N53, N55, N57, N6, N7, N10, N11 and N12 were not closed by this bounded session and remain OPEN or PARTIALLY CLOSED exactly as their own rows state**; no absence from the review supersedes them. N43 and public-claim debt were independently corroborated. Exact next unit: correct the high-consequence public/PyPI claim classes in the dated register without changing benchmark results or detector rules, then independently label a future repository study before reconsidering a pilot. |
| **N45** | **Working-tree drift is now detectable at every measurement point.** Built because of N44's mechanism and proven necessary twice in one evening. | 2026-07-30 (directive session, item 1b) | **BUILT, CONTROLLED BOTH WAYS, INTEGRATED in PUSHED:c812ceb.** `scripts/tree_guard.py`: `--record` baselines to gitignored `.claude/tree-state.json` (recording cannot dirty the measured tree; the baseline file is the one excluded path, a self-reference bug found on the real repo and fixed with the control re-run); `--check` exits 3 naming every drifted path; `stamp()` prints one stderr line from the nine measurement CLIs (claim_auditor, site_integrity, cascade_count, build_recall_artefact, build_gap_demo, check_selfref_sourcing, merge_blockers, f25_exposure, site_facts), silent with no baseline, never touching exit codes. Ignored files are content-hashed; ignored dirs hashed to a stated 200-file budget, presence-plus-count above (the `.venv` class), because N43 proved plain porcelain blind to the live class. `tests/test_tree_guard.py`, 10 tests in throwaway repos including the planted-change control both ways and the silent-revert-to-HEAD class; wired into the custom runner, selection 1,033 to 1,043 functions, cascade 2,585 to 2,595 in the same commit. **Its build caused, then named, a real incident**: creating the test file mid-run made the item-0 HEAD suite at `839b031` fail `test_stale_number_floor.py::TestEndToEndThroughVerifyFacts::test_the_real_repo_still_passes` (`1 failed, 2584 passed in 1291.04s`; live collection 2,595 against canonical 2,585, failure naming `site/llms-full.txt:L16`), which is the overlap rule firing through a second mechanism: a NEW file changes live collection even though running processes never re-read it. Diagnosed by running the single test on the quiescent tree, remediated by the cascade in PUSHED:c812ceb, single test and all six gates then green. First live catch on record: `site_facts` stamped `content changed again since record: evidence-pack-project-2026-07-30/manifest.json` during the cascade. **Limit stated plainly: it detects THAT and WHAT, never WHO; actor attribution needs a harness-level watcher, out of repository reach** (the stale-sentinel precedent). Residual hole carried from N39/N40, not new: `check_decompositions.py`'s `commit-anchors` rule only parses records whose schema states trees with the word "tree" on the line, so a schema-drifted record escapes it. |

---

## 2. Owner decisions

"Ruled but unapplied" is called out explicitly: the owner has already answered
these and the answer has not been encoded.

| # | Decision | Raised | Status |
|---|---|---|---|
| 1 | Ratify or reject the quarantine sensitivity-admissions mechanism | 2026-07-28 | **RULED AND NOW ENCODED, 2026-07-30.** All three conditions exist as tests in `tests/test_claim_quarantine.py`, each with a control run both ways. See N24. Nothing in the ruling turned out to be underdetermined. |
| 2 | Ratify or reject the F14 deviation on Articles 11 and 12 | 2026-07-28 | **RULED AND NOW ENCODED, 2026-07-30.** Reject half: the Article 11(1) Omnibus route verified against the primary text at EUR-Lex and added to `references/framework_crosswalk.yaml`. Ratify half: the `owasp_agentic` reason recorded in the crosswalk itself. See N25. |
| 3 | Scope F25 and F30 | 2026-07-28 | **ANSWERABLE FOR THE FIRST TIME, and still OPEN because the scoping is the owner's.** The apparatus now exists and is committed: `python3 scripts/f25_exposure.py --recover`. **The number the ruling should use: 91 findings on the gate's own corpus are currently held green by an ordinary English word, and 215 of 279 citation-word-sourced paragraphs have no other provenance** (`e8b5986`, main working tree; see N26). **Neither 22 / 46 nor 29 / 53 reproduces under any of six corpus definitions in either of two units, and neither side of either figure matches.** Both are withdrawn as unreproducible. F30's half of this decision is untouched and F30 remains open; N23 now supplies a measured F30 instance on live data. **2026-07-30: the decision is no longer only about an instrument.** `--enumerate` now lists every revealed finding with the word that sourced it, and 24 of the 26 on the site corpus are real claims a reader cannot check. See N30. F25 is a product finding as well as a gate finding, and the scoping ruling changes what ships, not only what the gate counts. |
| 4 | Rule on F29: 387 or 386, and does the blog's 389 get corrected | 2026-07-28 | **THE MEASUREMENT IS SETTLED 2026-07-30; ONE SURFACE STILL NEEDS A RULING.** 387 and 386 are BOTH correct, at two trees that both call themselves v1.7.0 (`7fa2088` 16 April gives 386, `c6aa67a` 23 April gives 387), so the question as posed had a false premise: it was never 387 OR 386. 389 is wrong under every unit at both trees. See F29 above and `PUSHED:4335831`. **What still needs the owner:** the 5-frameworks post publishes 389 and its artefacts do not record which tree ran, so the replacement is not derivable and nothing was changed there. **Previously recorded as deferred SEVEN times, not four.** This cell read "four times" while the F29 row in section 1 read "SEVEN sessions", so the file disagreed with itself about the same item; corrected 2026-07-30 to the F29 row's figure. **The figure is carried, not enumerated, and that is a real limit:** a session is not a git object, so no predicate can count deferrals the way `git ls-files` counts surfaces. It is the one count in this file that no command can re-derive. What would fix it: a deferral marker in this file incremented when an item is carried, which a test could then reconcile against the row's prose. Not built this session. |
| 5 | Sign off the English provenance sentence for the DE and PT-BR panels | 2026-07-28 | **OPEN.** Untouched. |
| 6 | Approve or reject the agentic AI draft before publication | 2026-07-29 | **OPEN, and one of its two obstacles is gone.** `content/blog/article-agentic-ai-annex-xiv.md`, tracked, `published: false`, still never human-reviewed, which is the part only the owner can clear. **The count has now been done literally, 2026-07-30:** the regulation was retrieved in full from `eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=OJ:L_202601744`, tags stripped and the text searched case-insensitively; the string `agentic` occurs **exactly once**, in the Annex XIV code table at AIH 0401, and the sentence immediately after that table puts the codes to work scoping conformity-assessment-body designation. **Two summarising fetches of the same URL reported that the word does not appear at all**, because both truncated before the annexes; one stopped mid-sentence in Article 63. A truncated retrieval is not evidence of absence, which is why the count was redone with the whole document in hand. |
| 7 | Whether `docs/improvement/` belongs in the CI claim gate | 2026-07-29 | **WITHDRAWN by the owner, and the merge-base measurement now forces it back open.** It was withdrawn on the grounds that the gate repair's design would answer it. The measurement says the design cannot avoid it: 203 of 281 findings are `docs/improvement/` and every one is branch-introduced, so no introduced-claim condition excludes them. Only a scope condition does, and that condition is decision 7 restated. **Recommend reopening.** **2026-07-30: the missing input is now measured.** Main's published-surface debt is 168 with the citation-word arm on and **238 with it off**; see N29 and section 7 below for what each of N12's four options implies at 238. |
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

- **Session B**. **F29's unit reconciliation is DONE, 2026-07-30, and is no
  longer Session B's**; see F29 in section 1 and `PUSHED:4335831`. What remains
  of F29 is one reader-facing surface whose correct figure is not derivable
  from any committed artefact, which is an owner ruling and not a session's
  work. Still Session B's: the agentic draft humanising and validation,
  deferred on the grounds that it is a content correction better verified by
  the repaired gate than the current one.
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
| Phase 1.7 | **DONE 2026-07-30** in PUSHED:4ee37b2 (deliverable `docs/improvement/SCAFFOLDING-AUDIT.md`; residuals listed in its section 7). Untracked scaffolding (CLAUDE.md, two skills, one charter) corrected in place; gitignored files cannot carry a commit hash and the audit records them. |
| Phases 5 to 8 | NOT STARTED |

Neither Phase 2 nor Phase 4 has passed its gate. The Phase 4 plan must not be
executed.

**`BASELINE.md` section 11: READ 2026-07-30, after five sessions of not being
read.** The contradiction is real and it is narrower than "the file contradicts
itself". Four statements bear on the Engineering-craft score and three of them
say 88:

- the table row says **"Hold at 90"** — the outlier;
- the aggregate arithmetic on line 322 uses **13.2**, and 0.15 x 88 = 13.2;
- the closing sentence on line 344 says **"Engineering craft moves 90 to 88"**,
  and gives its reason;
- `docs/improvement/PLAN-PHASE4-v2.md:291` and
  `docs/improvement/HOSTILE-REVIEW-LOOP2.md:138` both fix craft at 88.

Both readings are arithmetically sound, re-derived rather than quoted:
craft 88 gives `9.5 + 8.0 + 13.2 + 10.8 + 8.5 + 0.8 + 1.5 = 52.3`, craft 90
gives `... 13.5 ... = 52.6`. **Nothing in `BASELINE.md` was changed.** Section
11 states in its own correction note that the discrepancy is "not silently
resolved" and that the Phase 7 independent scorer arbitrates; resolving it here
would override a recorded decision, which is not this session's to make. What
is now on record is which statement is the outlier and by what weight.

Two further facts about that row, both of which cut against quoting the
aggregate at all: the craft row's evidence is **"2,849 tests MEASURED"**, a
figure withdrawn by finding F1 as double-counted, and the current
pytest-collected count is different again. **The aggregate rests on a withdrawn
measurement whichever reading is taken.** Enumerated exposure:
`git ls-files -z | xargs -0 grep -n "52\.3\|52\.6"` finds the figures in
**eight tracked files, all under `docs/improvement/`**. No published surface
quotes an aggregate, so there is no public exposure to correct.

---

## 6. Current state

**This section exists because a current-state record said "Failing: nothing"
on the same page as a merge blocker exiting 1.** See N19. Anything that fails
belongs here with its figure, its commit and the tree it was measured in, and a
gate that is not one of the six fast gates is not thereby a gate that passes.

### Failing

| What | Command | Result |
|---|---|---|
| **The merge blocker.** Unsourced numeric and superlative claims on the branch diff. | `python3 scripts/claim_auditor.py --diff-base main` | **rc=1, at six commits.** At `e8b5986`, main working tree: `scanned 59 file(s), 945 claim(s), 273 unsourced`. At `60fa775`, tree `46b7c3d`: `scanned 59 file(s), 976 claim(s), 274 unsourced`. At `13ffc00`, tree `9fd730a`, clean: `scanned 59 file(s), 978 claim(s), 274 unsourced`. At `057c009`, tree `218b4a1`, **with this file's edits still uncommitted in the working tree**: `scanned 59 file(s), 996 claim(s), 279 unsourced`. At `ef2b8de`, tree `f9b12b6`, clean: `scanned 60 file(s), 1016 claim(s), 280 unsourced`. At `197eb99`, tree `5147def`, **with this file's N42 edit uncommitted in the working tree**: `scanned 64 file(s), 1051 claim(s), 282 unsourced`. `--diff-base` selects files from the diff and reads their WORKING TREE contents, so a figure taken on a dirty tree measures the dirty tree, and that is stated rather than smoothed over. This is NOT one of the six fast gates, so its red does not appear in a gates block. |
| **The residue under both candidate gate conditions.** | `python3 scripts/merge_blockers.py` | **10 survive both at every commit measured.** At `e8b5986`: 273 total, 218 introduced-claim alone, 65 published-surface alone. At `60fa775`: 274 / 219 / 65. At `057c009` with this file uncommitted: **279 total, 224 introduced-claim alone, 65 published-surface alone**. Disposition by predicate, unchanged throughout: 1 blocked, 7 contested, 2 inherited, **0 fixable**. |
| **F30 now has a third measured instance.** The allowlist exempts the whole paragraph, and `site/index.html`'s `0%` quarantine entry is held silent by a paragraph whose only citation word sits inside an HTML attribute. | `python3 scripts/f25_exposure.py --corpus site --shape` | **18 of 105 citation-word paragraphs on the site corpus are sourced ONLY from inside an HTML attribute**, at `9e6b6de`. See N35. rc=0: a measurement, not a gate. |
| **`main`'s published-surface debt is larger than the gate can see.** | `python3 scripts/merge_blockers.py --main-only --arm-delta` | **168 with the citation-word arm on, 238 with it off, 70 revealed, 0 lost**, at `main` `6daacd2`, tree `b95876d`, clean detached worktree, HEAD's auditor unmodified at `13ffc00`. rc=0: this is a measurement, not a gate. See N29 and section 7. |

**What the 2026-07-30 apparatus session added to the blocker, named.** Produced
by `python3 scripts/claim_diff.py --blocker-delta 9e6b6de 190da47`, whose
apparatus is `scripts/claim_diff.py`: **1 finding, in
`docs/adr/0002-the-seventy-percent-claim.md` at line 130, the snippet `70%`.**
The code and the count cascade added **0**, measured separately as
`--blocker-delta 9e6b6de fc27823`. It is the ADR naming the very figure it
exists to investigate, which is the self-referential loop this file already
records for `docs/adr/`: writing the analysis of a claim adds claims to the
corpus that measures claims. Recorded rather than engineered away, per rule 24
in `docs/improvement/LEDGER.md` above.

**It was 3 before the ADR was corrected, and the correction was forced by a
test.** At `4e1a33f` the ADR also carried `the only` and the bare precision
figure; `tests/test_precision_provenance.py` failed the full suite because that
figure was published on a surface not listed in its `KNOWN_SURFACES`, without
N and the single-reviewer basis at the point of use. The fix at `190da47`
removed the figure from the sentence rather than adding `docs/adr/` to that
test's exclusions, because excluding a surface to make a check pass is
prohibited outright. Removing it also took `the only` out of the blocker, since
the rewritten paragraph now cites `tests/test_precision_provenance.py` and is
sourced through the file-reference arm.

**On 282 to 280, and why the total moved without the corpus growing.** The last
stated total was **282** at `41feb51`, tree `e85452c`. The tip figure is **280**
at `ef2b8de`, tree `f9b12b6`, on a clean tree. The difference is the two
findings `190da47` removed from `docs/adr/0002-the-seventy-percent-claim.md`,
the bare precision figure and `the only`, so the movement is fully attributed
and neither figure is quoted forward from the other; each was re-derived from
the command. **This is the first record of the tip figure at `ef2b8de`**, which
had been measured nowhere: the prior sessions recorded 282 and then landed two
commits without re-running the gate.

**On the two figures 273.** The most recent prior record measured 273 at
`969f3a8` (N18). `e8b5986` added one line to this file, which is inside the
measured corpus, so the number was expected to move and **it did not**. The
prediction was written down before the measurement and was wrong. The reason is
mechanical and worth keeping: the line added was the N18 table row, which cites
four tracked repository files, so every claim inside it is sourced through the
`file-ref` arm and it contributed to `claim(s)` without contributing to
`unsourced`. Both 273s are correct at their own commits and neither is quoted
forward from the other; each was re-derived from the command.

**On 273 to 274, and what the one added claim is.** `60fa775` added 152 lines
to this file and moved `claim(s)` from 945 to 976 while `unsourced` moved by
exactly one. Attributed by predicate, not by reading: `merge_blockers.py` puts
the `docs/improvement/` bucket at 200 then 201, and scanning this file alone at
each commit with the real auditor, the older version in a detached worktree with
HEAD's auditor copied in, gives 1 finding then 2, with a single snippet added:
**`2,849 tests`**. That is the withdrawn craft-row figure quoted in the
`BASELINE.md` section 11 diagnosis above. **It is deliberately not sourced.**
F1 withdrew 2,849 as double-counted, so a citation next to it would cite a
withdrawn number, which is the `blocked` class N15 established. Writing the
diagnosis of a withdrawn figure added a claim to the corpus that measures
claims; that is the same self-referential loop the merge-base row recorded for
`docs/adr/`, and it is recorded rather than engineered away, because engineering
it away is chasing the number and rule 24 above forbids it.

### 2026-07-30, evening session: the held tree landed, and Phase 1.7

The 12 files the previous session left modified-but-uncommitted were
verified and committed as six units: PUSHED:820562c (shared exit-code
derivation, CLI and API), PUSHED:2d0cea6 (MCP shared path denylist plus the
repair of regula_gap, which imported a function that does not exist),
PUSHED:3f1a797 (bias endpoint scheme guard), PUSHED:7317689 (jsonschema test
dependency declared), PUSHED:0b74db0 (indicator language on generated
surfaces; the hardcoded 419 pattern-count fallback removed), PUSHED:82266e9
(four regression tests plus the cascade 2,581 to 2,585 in the same
commit). Fail-before controls ran in a detached worktree at `e14fdbe`
OUTSIDE /tmp: 5 discriminating tests failed there, 104 passed in the fixed
tree. A first control run inside /tmp was discarded, /tmp is itself in the
MCP denylist, which confounded one test (measurement rule 2: two variables
had changed).

Full `pytest tests/ -q` at `e14fdbe` with the 12 files in the working
tree: **2581 passed in 1036.31s**, rc=0 from `$?` after redirection, the
sentinel file removed before launch. The published expectation is now
2,585; the post-change full-suite and custom-runner runs are recorded
below when they complete, per the standing caveat that verification runs
post-date the commit they verify.

Phase 1.7 landed in PUSHED:4ee37b2 (see section 5). Its audit found and
fixed: a rules file and a skill still describing the Omnibus as pending
publication against `scripts/omnibus.py:29`; /verify's false
mirrors-CI-exactly claim (measurement rule 5 in the scaffolding itself);
add-command.md naming the wrong module for command bodies; the
releasing-regula skill instructing `git add -A` (forbidden by
`.claude/rules/git.md`) and a static pyproject version line that does not
exist. The em-dash rule was scoped to new prose with the verbatim-record
exemption encoded; the measured footprint of existing em dashes (40
tracked files with the entity form, 167 under site/ and scripts/ with the
literal) is recorded in the audit, deferred, not swept.

**Correction, directive session:** the phrase this entry first used here,
"made self-verifiable", mischaracterised the header fix. `git show 4ee37b2`
shows the hand counts ("7 files", "3 files") were the two findings; the
amendment in `839b031` REMOVED those numeric claims and replaced them with
the enumerated file names. No provenance was attached; there is no numeric
claim left for the gate to see. That is rule 4c's remedy (the enumeration
is the number's source), and the record should say removal-and-itemisation,
not sourcing. At PUSHED:4ee37b2 with that amendment:
`claim_auditor.py --diff-base main` rc=1, scanned 66 file(s), 1057
claim(s), **282 unsourced**, of which SCAFFOLDING-AUDIT.md contributes 0;
the residue is the pre-existing programme-document debt this file already
records. Six fast gates rc=0 at PUSHED:82266e9 and again at PUSHED:4ee37b2.

### Passing

Six fast gates, each rc captured rather than read off a summary line, at
`e8b5986`, again at `60fa775`, and again at `057c009`:
`claim_auditor.py --verify-facts`, `site_integrity.py`,
`cascade_count.py --check`, `build_recall_artefact.py --check`,
`build_gap_demo.py --check`, `check_selfref_sourcing.py --control-only`. Also
at `60fa775` and at `057c009`: `python3 -m scripts.cli self-test` 6/6 rc=0 and
`python3 -m scripts.cli doctor` 8 passed / 4 info rc=0.

**2026-07-30, later session: all six rc=0 at `f536dd0`, again at `99c7ef7` and
again at `197eb99`**, each captured from `$?` after redirection rather than
read off a summary line. **No commit in that session leaves a fast gate red**,
because each of the two count cascades went in the SAME commit as the tests
that moved the count. That is the lesson `5f4ae76` paid for; see section 6's
"Not measured" list.

**Two of the six went red during the 2026-07-30 session and were repaired at
root rather than suppressed.** Adding seven tests moved the pytest-collected
count from 2,529 to 2,536, which turned `claim_auditor.py --verify-facts`
red with ten mismatches and made `cascade_count.py --check` refuse with
`RefusedError: data/site_facts.json is stale`. The fix was to regenerate
`data/site_facts.json` with `scripts/site_facts.py` and propagate with
`scripts/cascade_count.py --apply`, then read the diff of all seven surfaces
line by line, per measurement rule 4d. No threshold was raised and no check
was skipped. `docs/TRUST.md` also carries the custom runner's own function
count, which `cascade_count` does not propagate; it moved 1,011 to 1,015 and
`tests/test_published_count_manifest.py` is what caught it.

### Verification runs necessarily post-date the commit they verify

A full-suite or full-runner result cannot be written into the commit it
describes. Both are recorded in the consolidated session record for
**2026-07-30**, with the command, the summary line and the captured exit code.
What belongs here is the standing caveat, which N28 establishes: the suite
contains a **wall-clock** assertion, so "full suite green" is a statement about
one run on one machine at one load, not a property of the tree.

### Not measured, and stated as such

- Whether `134` is re-derivable from `docs/improvement/measure_pattern_reach.py`.
- CI has never executed on this branch and still cannot; see owner decision 8.
- F21, F22, F24, F26, F27, F28 remain closed and have never been independently
  re-verified. Their closure commits were wrong until 2026-07-30 (N22).
- **A long test run and a live editing session must not overlap, and on
  2026-07-30 they did.** The custom runner was started at 08:44 and took
  roughly 25 minutes; `docs/improvement/LEDGER.md` was edited while it ran.
  `test_ledger_supersession_declarations_are_paired` read the file in the
  window between the edit that added `SUPERSEDED-BY:N31` to N23 and the edit
  that created row N31, and reported `1 failed`:
  `EXCEPTION in test_ledger_supersession_declarations_are_paired: LEDGER.md
  has half-declared supersessions`. **The failure is real output and it is not
  a defect in the tree**; the same test passes in isolation before and after,
  and the runner was re-run to completion on the quiescent committed tree. It
  is recorded because "the suite was green" and "the suite was green on a tree
  nobody was editing" are different claims, and only the second one means
  anything.
- **Commits `7b154f8` and `969f3a8` have never been full-suite verified.**
  Carried forward from the 29 July session, which verified them by targeted
  tests and all six gates and ran the full suite only at `f286562` and
  `e8b5986`. Still true on 2026-07-30: this session did not run the suite at
  either of them either. It matters more here than it would elsewhere, because
  F26 recorded this branch running red for six commits under a collect count.
  The changes between `7b154f8` and `e8b5986` are document prose plus one
  ledger line, which is a reason the risk is low and not a reason it is zero.
- The custom runner's `N passed` figure on `docs/TRUST.md` line 95 is not
  machine-checked; only its function count is. Deriving it costs a full runner
  execution, and it is re-derived by hand each time the runner is run to
  completion.
- **The stale-sentinel hazard, which until 2026-07-30 had no durable home
  anywhere and survived only in session prose.** A long run is launched with
  its result redirected to a file, and the exit code is read from that file
  afterwards. If the file already existed from an earlier run, the reader gets
  the earlier run's verdict and cannot tell. This is measurement rule 4 in its
  sharpest form: an exit code read from a pre-existing file is not this run's
  exit code. **A near-miss on exactly this occurred in the 2026-07-30 apparatus
  session** and is recorded in that session's record as its most important
  entry. The standing mitigation, which is procedure rather than apparatus:
  `rm -f` the target before launching the run that writes it, and capture the
  code from `$?` immediately after the redirection rather than from a summary
  line or a file listing. **No mechanical check enforces this**, because the
  hazard lives in the shell invocation and not in the tree, and nothing in the
  repository can observe a command a session chose to run. Stated as a gap
  rather than as a solved problem.
- **`5f4ae76` is a red intermediate commit and remains one.** It landed the
  shared probe, two commands and thirteen tests, which moved the pytest-collected
  count and thereby turned `claim_auditor.py --verify-facts` and
  `cascade_count.py --check` red at that commit. The cascade that repaired both
  landed separately at `fc27823`. **A bisect that lands on `5f4ae76` sees two
  fast gates red for a reason unrelated to whatever it is bisecting for.** It is
  recorded rather than rewritten because history is immutable on this branch.
  The lesson taken forward from 2026-07-30 onward: when adding tests moves the
  published count, the cascade goes in the SAME commit as the tests, so no
  commit exists in which the gates disagree with the tree.
- `BASELINE.md` section 11 was READ this session; see section 5 above. The
  52.3-versus-52.6 arbitration remains Phase 7's and is not a measurement gap.

---

## 7. Owner decision 7: the ratchet baseline at the corrected figure

**The figure is 238.** MEASURED at `main` `6daacd2`, tree `b95876d`, in a clean
detached worktree scanned by HEAD's auditor unmodified at `13ffc00`, by
`python3 scripts/merge_blockers.py --main-only --arm-delta`: 168 published-
surface findings with the citation-word arm as shipped, **238 with it off**, 70
revealed, 0 lost. See N29.

**Why 238 and not 168, stated as reasoning rather than as a preference.** A
ratchet is a promise that the number can only fall. The gate-scope repair is
already scheduled to narrow `CITATION_WORDS`, and narrowing it can only raise
what the gate reports. A baseline of 168 therefore fails on the day the repair
lands, with no claim added and no content changed, and the only ways out of
that failure are to raise the baseline (which destroys the ratchet's meaning)
or to delay the repair (which is the gate protecting itself). A baseline of 238
is invariant to any narrowing of that arm, because 238 is what the gate reports
with the arm gone entirely.

**The cost of 238, stated plainly.** It is deliberately loose today by up to 70.
Until the arm is narrowed, 70 findings could be introduced on main's published
surfaces without the ratchet firing. That is the price of a baseline that does
not have to be renegotiated, and it is a real cost, not a rounding error.

**What each of N12's four options implies at 238.** Not a choice among them; the
owner rules.

| Option, as recorded in N12 | What it means at 238 rather than 168 |
|---|---|
| Fix the findings before enabling | The remediation is 238 items, not 168. Fixing only the 168 the gate shows today leaves 70 that go red the moment the arm narrows, so the work would be done twice. |
| Scope the condition to the diff | Unchanged in principle: the arm question is orthogonal to whether the diff is consulted. In practice the 70 are concentrated in 6 files, two of which are the scan blog posts, so any future edit to those files inherits them. |
| Warn-only on main, blocking on pull requests | The warning reads 168 today and 238 after the repair. A 42% rise with no content change will read as a regression to anyone who does not know why, so if this option is taken the warning must state which arm state produced it. |
| Accept as a recorded baseline, fail only on increase | This is the option the figure matters most for, and it is the one 168 breaks. At 238 the ratchet survives the repair; at 168 it does not. |

**What would overturn this.** If the gate-scope repair narrows
`CITATION_WORDS` rather than removing it, the true post-repair figure is
somewhere in 168 to 238 and 238 is loose by the difference. Re-running
`--main-only --arm-delta` with the narrowed pattern substituted for `ARM_OFF`
gives the exact number, and that is a one-line change to `merge_blockers.ARM_OFF`
once the repair's pattern is decided. The recommendation to baseline at 238
holds until then because it is the only figure that cannot be invalidated by
the repair, and it is the cheapest to reverse: lowering a recorded baseline
after a measurement is a one-line edit, whereas raising one after it has been
published is the move this programme exists to catch.

---

## N61 — Commercial review used stale current-release identity

**First raised:** 2026-08-01. **Status:** partially addressed.

PyPI no-cache JSON, pip index, downloaded wheel METADATA, and tag mapping identify
1.9.0 as current on 2026-08-01, contradicting commercial_v1's description of
1.7.4 as current. Dated errata preserve the 1.7.4 frozen result as VERSION_BOUND.
The structural prevention criterion remains open: release identity must be
mechanically queried and retained in future protocols rather than inherited.

## 2026-08-01 bounded claim-correction carry-forward

F25, F30, N35, N43, N50, N54, N53, N55, N57, N6, N10, N11, N12 and N60 remain
open or retain their previous recorded verdict; none was closed by weakening
public wording. N7 was not examined as an independent acceptance unit. N61 is
partially addressed as above. Public source correction is not evidence that
detectors, benchmark reproducibility, merge policy, CI, or pilot readiness
improved. commercial_v1 remains STOP and the product remains not approved for
a customer pilot.

## N62 — Delivery-derived public-surface inventory

**First raised:** 2026-08-01. **Status:** implemented; discovered residual claim
classes corrected, exact final verification pending.

The former 22-path hand-curated contract could pass while tracked Pages routes,
Action descriptors, registered CLI help, MCP `tools/list` descriptors, package
metadata and README-reachable documents were absent. The authoritative
inventory is now derived from the two GitHub Pages workflows, tracked `site/`
artifact contents, `pyproject.toml`, README-relative link reachability,
`action.yml`, the constructed `argparse` registry and the actual MCP `TOOLS`
registry. `data/public_claim_surfaces.json` and the human report are generated;
`data/public_surface_policy.json` contains only narrow, reasoned dispositions.
Mutation controls cover new routes and outputs, linked docs, CLI, MCP, Action,
package metadata, renames, policy integrity, Git/build failures and legitimate
negatives. The resulting active-surface residual list is now empty after
capability wording was narrowed to code-observable indicators, human review,
variable runtime and scoped local-processing statements. F25, F30, N35, N43,
N50/N54, N53, N55, N57, N6, N7, N10, N11, N12, N60 and N61 retain their prior
status. commercial_v1 remains STOP and `PRODUCT_PILOT_STATUS` remains
NOT_APPROVED.

## N63 — Decision labels were downstream of three reproducibility defects

**First raised:** 2026-08-01. **Status:** implementation complete; independent
exact-commit verification pending.

The decision labels were not themselves the defect. Three evidence mechanisms
were: an ISO-8601 timezone offset was parsed as arithmetic; five numeric claims
introduced by the evidence-only records lacked same-paragraph sources; and the
gap-demo builder scanned ignored local files while claiming clone
reproducibility. The decomposition parser now masks complete ISO timestamps and
retains positive arithmetic controls. The evidence records link their durable
sources and the claim-auditor count returned from 314 to the pre-existing 309.
The gap-demo builder now materialises exactly `git ls-files` into a temporary
snapshot and fails closed on Git, copy, command or parse failure. Mutation
controls prove ignored input is absent and Git failure is not swallowed. The
generated result is 6% overall with Article 11 at 0%, synchronized across EN,
DE and PT-BR. N43 is deliberately carried forward unchanged until the required
detached-worktree verification reproduces the repair. All previously named open
items remain open. These corrections do not create human-labelled accuracy,
competitor equivalence, demand or pilot evidence, so commercial_v1 remains STOP
and `PRODUCT_PILOT_STATUS` remains NOT_APPROVED.

## N64 — Active-delivery claim enforcement and readiness decision

**First raised:** 2026-08-03. **Status:** partially addressed; release remains
blocked.

The discovery inventory exposed a second-order enforcement defect: the normal
diff audit could be green while claim-capable, actively delivered surfaces
that were unchanged in the current diff still contained unsourced or stale
claims. The auditor now consumes the generated delivery inventory and
`--delivery-surfaces` fails closed on an unreadable or empty inventory. The
full active delivery scan covers 96 text surfaces and currently reports 538
claim candidates with no unsourced candidates; fact verification checks 148
references across 17 files. Mutation tests cover the inventory hand-off and
prevent a policy entry from turning an entire paragraph into an exemption.

This does not make the repository release-ready. The independent merge-blocker
analysis still reports 42 findings that survive both enforcement arms: 1
blocked, 21 contested, 18 fixable and 2 inherited. Exact final full-suite and
detached-worktree verification remain required. No deployment is authorised by
this item. F25, F30, N35, N43, N50/N54, N53, N55, N57, N6, N7, N10, N11, N12,
N60 and N61 retain their prior status. commercial_v1 remains STOP and
`PRODUCT_PILOT_STATUS` remains NOT_APPROVED.

## N65 — Merge blocker used tracked-renderable as a publication proxy

**First raised:** 2026-08-03. **Status:** implementation complete; exact final
verification pending.

The independent merge analysis continued to classify almost every tracked
document outside `.claude/` and `docs/improvement/` as a published product
surface after N62 introduced the authoritative delivery-derived inventory.
That proxy mixed active product promises with retained benchmarks, ADRs and
commercial evidence. The reported 42-item residue therefore comprised two
different populations and could not support a single merge decision.

`merge_blockers.is_published_surface` now derives its file set from generated
records classified `active_product` and `claim_capable`, and fails closed when
the inventory is missing, malformed or empty. The current run reports 474
total claim findings, 463 introduced-only findings, zero active-delivery
findings and zero surviving both conditions. The 42 previously reported items
remain in retained evidence; they were not deleted, sourced indiscriminately
or allowlisted. Focused gate, set-operation and mutation coverage reports 45
passing tests. This changes the active claim-blocker measurement, not the
commercial evidence: commercial_v1 remains STOP and
`PRODUCT_PILOT_STATUS` remains NOT_APPROVED. Repository merge readiness remains
pending until the complete test matrix and detached-worktree checks pass.
[exit 0]
```

Ended: `2026-08-05T00:16:55+01:00`

## Latest improvement state

Started: `2026-08-05T00:16:55+01:00`

Command:

```console
$ bash -lc 'tail -n 900 docs/improvement/STATE.md'
**10/30 and 16/30 reproduce exactly.** **14/30 and 19/30 do not, and are
WITHDRAWN as NOT REPRODUCIBLE** on both surfaces that published them
(`docs/TRUST.md`, `RESULTS-synthetic-v2-2026-07-28.md`). The conditions
behind them were never committed: "`--domain <matched>`" implies a
per-fixture domain mapping that does not exist in `manifest.json`, and "an
AI-library import present" names neither the import nor the fixtures.

The reproducible neighbours are **different conditions** and are labelled
as such rather than substituted for the withdrawn figures. Inventing the
mapping now would be a new measurement wearing an old label.

**The "8 fixtures that miss with both gates satisfied" is 7** under the
reproducible condition, and they are named in the artefact:
`highrisk_benefits_eligibility`, `highrisk_border_screening`,
`highrisk_crime_forecast`, `highrisk_energy_grid`, `highrisk_exam_proctor`,
`highrisk_recidivism`, `highrisk_voter_targeting`. The figure of 8 came
from the unreproducible condition and is not comparable.

## Also repaired, flagged as mid-landing expansion

- **`scripts/check_selfref_sourcing.py` had become a blank gate.** Its
  detection was subsumed by the F21 repair, so it reported CLEAN on every
  input including its own known offender. Rewritten: it now runs a control
  first (plants a self-referential-only paragraph, asserts rejection;
  plants a sourced one, asserts acceptance) and exits 2 if the control does
  not fire, then reports unsourced claims. Justification: rule 4, a blank
  gate is not a green gate.
- **Two `ATTRIBUTED_CLAIM` false positives on `site/pricing.html`**,
  surfaced by the F21 repair. `<meta ... content="... Reports | Regula">`
  read as an attribution verb followed by quoted text, because inside a
  tag the quote characters are attribute syntax. Attribution matches
  inside tags are now skipped; numeric claims inside tags still count,
  since a meta description is published prose.
- **Four `verify_facts` false positives**, surfaced by removing the F22
  floor and fixed at the pattern rather than exempted: `(?<!\d)` became
  `(?<!\w)` so `python3 tests/...` stops reading as "3 tests" (three
  surfaces), and `tests?` became `tests` so "963 test functions" is no
  longer swept up. This aligns the auditor with the shape list
  `scripts/cascade_count.py` already uses. **`STALE_CHECK_EXEMPTIONS` is
  empty, and that is the point.**

## What is NOT green, stated rather than buried

**`claim_auditor.py --diff-base` is red on `docs/TRUST.md` (14) and
`docs/MODEL_CARD.md` (12) for pre-existing unsourced percentages.**
MEASURED like-for-like in a HEAD worktree: those same three documents gave
**67 claims / 36 unsourced at HEAD** and **72 claims / 34 unsourced now**,
so this batch reduced it. The CI claim gate scans whole files, so any
commit touching those two documents is red, including every cascade commit
that has ever run. The branch is unpushed, so CI has never executed.

**This is P0 territory and P0 stays parked.** Recorded here so nobody
reports this batch as "all gates green" when one of them is not.

## NEXT

1. **Task B** — class 1 under the stale-crosswalk guard, plus the R1 and
   330 residuals. Not started; it is the seam this session stops at.
2. **Owner ratification** — the quarantine admissions mechanism (F21
   tranche, +2), and scoping for **F25**.
3. **Task C** — re-derivations, then traces. The trace target list is now
   7 named fixtures from a committed artefact rather than 8 from prose.
   **F27 changes what the traces are for:** the scanner/classifier
   divergence is not there to be explained.
4. Loop 3 in its own fresh session, unchanged.

---

# CHECKPOINT — 28 July 2026, session 4: TASK B (CLASS 1) LANDED

## Class 1 was three different things, not one class of ~30 pairs

PACK-1.5b §3 grouped "~30 progress-bar percentage pairs" across 8 files.
Reading the files shows three unrelated items:

| Item | Where | What it actually is |
|---|---|---|
| **Terminal mock-up** | `site/index.html`, `site/locales/de.html`, `site/locales/pt-br.html` | Invented `regula gap` and `regula comply` output behind a `$` prompt. **The real class 1 defect.** DERIVED this session. |
| **"roughly 30% / 70% of the EU AI Act"** | `site/about.html`, `site/blog/blog-code-scanning-vs-questionnaires.html` | Not a progress bar. A substantive modelling claim about the regulation's composition. Already quarantined. Belongs with class 2, not here. |
| **`0%` in the assess widget** | `site/assess/{index,de,pt-br}.html` | Live UI state (`<span id="progressPct">0%</span>`), initialised at zero. Not a claim at all. |

Only the first was actioned. The other two are named here so nobody
reports class 1 as closed on the strength of this commit.

## The terminal mock-up, derived

`data/gap_demo.json` is produced by `scripts/build_gap_demo.py` from real
runs against the committed fixture `tests/fixtures/sample_high_risk`.
`tests/test_gap_demo.py` (10 tests) re-runs both commands, and binds every
locale panel to the artefact in both directions: every artefact percentage
must appear, and **no other percentage may appear**. The second half is
the one that catches drift.

What the real output changed on the page:

- **20/40/60/80/0/30/50 became 0/0/25/0/0/45/0/0**, and the headline
  **42/100 became 9/100**. The mock-up flattered.
- **The NOTE the mock-up omitted is now on the page.** It says the score
  measures presence of documentation and cannot offset scan findings.
  That NOTE is the denominator disclosure, and its absence was the defect.
- **Eight article rows, not seven.** The real output includes Article 17.
- **`regula comply` needed `--all`.** Without it the command prints no
  article table for this fixture, because the project classifies as
  `not_ai`. The old panel did not depict stale output; it depicted output
  the command does not produce.

### Fixture choice, criterion fixed before any score was seen

The criterion: committed, and scanned exactly as the page depicts it, no
flags. Two candidates were rejected for reasons independent of their
scores:

- **`regula gap .` on the Regula repo scores 100%**, and that number is
  computed partly over `conformity-evidence-project-*` directories which
  are **untracked and gitignored**. No clone reproduces it. Measurement
  rule 4b, caught before publishing.
- **A purpose-built fixture** would be the shop window chosen by its
  author. PROGRAMME.md principle 3.

`sample_high_risk` scores 9%. That is not why it was chosen and is not a
reason to change it.

### The F14 stale-crosswalk guard: premise checked, does not apply

The directive required Articles 11 and 12 to get tier-or-removal rather
than a derived count, because F14 found the crosswalk 108 days stale.

**MEASURED: the gap assessment never reads the crosswalk.**
`scripts/compliance_check.py` and `scripts/cli_compliance.py` contain
**zero** references to it. `assess_compliance()` scores each article
through `ARTICLE_CHECKERS`, per-article functions that match filename
patterns and document headings in the scanned project. Crosswalk staleness
cannot reach these numbers.

All eight rows are therefore derived. **Blanking rows 11 and 12 would have
meant publishing altered command output**, which is the defect this task
exists to remove, in the opposite direction.

**This is a deviation from a literal instruction and goes for owner
ratification.** The evidence is above; if the owner still wants those rows
blanked, the fix is to stop showing verbatim output and show a table
instead.

### Locale handling

The terminal block is English command output in all three files, so
mirroring it is a numeric and structural change and lands now. **New
DE/PT-BR prose is HELD.** The provenance line under each locale panel is
deliberately not prose: `→ tests/test_gap_demo.py · tests/fixtures/sample_high_risk`.
The English explanatory sentence, proposed for sign-off, is:

> Real output, not a mock-up. Reproduce it from a clone with the command
> shown; the fixture is committed at tests/fixtures/sample_high_risk and
> this page is diffed against a fresh run by tests/test_gap_demo.py.

## The two residuals, annotated not corrected

**R1 — the v1.6.1 raw output is not committed.** CONFIRMED: 11 files in
`benchmarks/results/blog_scan_2026_04`, none from v1.6.1, and its README
describes the v1.7.0 scan only. The post's closing note says output for
both versions is available. Annotated on the page.

**The 330 figure — UNSETTLEABLE, and the attempt is recorded.**

- No `v1.6.1` git tag (v1.6.0 and v1.6.2 exist).
- **No 1.6.1 release on PyPI either.** MEASURED via the PyPI JSON API:
  releases run 1.5.0, 1.5.1, 1.6.0, **1.6.2**, 1.7.0 onward. The sdist
  derivation the directive asked for was attempted once; there is nothing
  to derive from.
- Bracketing at the tags that do exist, current counting script:
  **v1.6.0 = 219**, **v1.6.2 = 386**. 330 sits between them, which is
  consistency, not confirmation.
- **The unit is not fixed either.** On the same v1.6.2 tree, that
  version's own script gives **358** and the current one gives **386**. A
  28-count gap on identical code means a bracket cannot settle a figure
  whose definition moved.

## NEW FINDING F29 — 387 does not reproduce; 386 does. MAJOR.

STATE.md and HANDOVER §7.5 record R2 as settled at **387** by two
independent methods. MEASURED at the `v1.7.0` tag by two methods, both
give **386**: that version's own `site_facts.py`, and the current one run
against the same tree.

The blog page also carries **389** further down while saying 387 above.
Those cannot both be right.

**Annotated, not corrected.** The 387 on record came from two methods that
have not been re-run, and replacing one unreproducible number with another
is not a correction. **ESCALATED.**

## NEW FINDING F30 — allowlist entries suppress whole paragraphs. HIGH.

`scan_file` tests each allowlist regex against the claim's line, the
claim's text, **and the entire paragraph**. One entry intended for one
line therefore exempts every claim beside it. MEASURED: `\bArticles?\s+\d+.*\d+%`,
written for per-article percentages, was suppressing the `9%` overall
score and the NOTE's `100%` in the same panel.

Repo-wide: **240 claims are allowlist-suppressed, and 63 of them ONLY by
the whole-paragraph arm** across ~20 files, led by
`references/tree_sitter_implementation_guide.md` (17) and
`docs/benchmarks/PRECISION_RECALL_2026_04.md` (9).

Line-scoping the allowlist would surface those 63 at once, which is an
auditor behaviour change beyond this fence. **NOT FIXED. ESCALATED.**

Consequence stated plainly: the class 1 panels initially passed the
pre-landing gate through this over-reach. They now carry a resolvable
file reference and are sourced on their own merits, **proven by stripping
citation words and re-running**: all three return
`file-ref:tests/test_gap_demo.py`.

## Also repaired

**A `<pre>` block is one verbatim unit.** `split_paragraphs` broke on
blank lines, cutting a terminal transcript into stanzas and demanding a
source for each. There is nowhere to put a citation inside verbatim
command output without falsifying it. Blank lines inside a `<pre>` now
get a zero-width space: line counts are untouched so coordinates still
map, but the block no longer splits. A plain space does **not** work,
because `line.strip() == ""` is true for it, and the control caught that
one step later.

## Gates

pytest and the legacy runner both green; `verify-facts`, `site_integrity`,
`cascade_count --check`, `build_recall_artefact --check`,
`build_gap_demo --check` and the F21 pre-landing gate with its control all
rc=0. Count cascaded 2,406 to 2,416 through `cascade_count.py --apply`.

`claim_auditor --diff-base` remains red on `docs/TRUST.md` and
`docs/MODEL_CARD.md` for pre-existing unsourced percentages. Unchanged by
this task, still P0, still parked.

## NEXT — the seam. Task B is done; this session stops here.

Task C (re-derivations, then traces) runs next session. Task D follows.
Loop 3 in its own fresh session. **F25, F29 and F30 are open escalations.**

---

# CHECKPOINT — 29 July 2026, session 5: DIRECTIVE v3 RECORDED

## v3 extends PROGRAMME.md; it does not replace it

Recorded verbatim at `docs/improvement/DIRECTIVE-v3.md` per its own section 0,
with a seven-row conflict and extension log. **No irreconcilable conflict was
found.** Every divergence is an extension or a sequencing change; none lowers a
bar or discards a prior finding. PROGRAMME.md remains the contract.

One logged deviation: the directive body contains em dashes, which the standing
rule forbids in repo copy. The verbatim-record requirement wins, for the same
reason verbatim command output wins in `.claude/rules/measurement.md`. Altering
a contract document to satisfy a style rule would falsify the record.

## Gates re-measured before trusting any prose. All eight green.

`pytest tests/ -q` **2416 passed rc=0** (1336.52s). `tests/test_classification.py`
**1386 passed, 0 failed, 0 skipped**, 963 test functions, rc=0 (19m53s).
`--verify-facts` rc=0 (145 refs / 16 files). `site_integrity` rc=0.
`cascade_count --check` rc=0, canonical **2,416**. `build_recall_artefact --check`
rc=0. `build_gap_demo --check` rc=0. `check_selfref_sourcing --control-only`
rc=0, control fires both ways. Tree clean, 52 commits `main..HEAD`, `main` =
`origin/main` = `6daacd2d`, branch absent from `git ls-remote`.

**`--collect-only` was not used.** F26 is why.

## Three HANDOVER.md prose figures do not reproduce at HEAD

Not defects in code or in any gate. All three understate rather than overstate.

| Figure | HANDOVER.md says | MEASURED |
|---|---|---|
| Whole-repo auditor, section 10 | 1,287 claims / 359 findings | HEAD **1,301 / 355**; parent `431a7d3` **1,287 / 360**. Both deterministic over repeated runs. |
| F25 blast radius | 94 paragraphs, 46 by "source" | HEAD **105 / 49**; parent **100 / 47** (allowlist and quarantine off, like for like) |
| F30 suppression | 240 suppressed, 63 para-only | HEAD **289 / 61**. Per-file leaders reproduce exactly. |

**The section 10 pair is a mixed-state figure**: its claims half matches the
parent commit, its findings half matches neither state. Cause is self-reference.
`HANDOVER.md` is inside the corpus it measures, and went from 7 claims / 4
findings at the parent to 21 claims / 0 findings at HEAD, so its own rewrite
changed the number it publishes about itself. **This is a live instance of the
failure that measurement rule 3 exists to prevent, committed by the document
that states the rule.** It is also the worked example directive section 8 wants
written up.

**New, and not recorded anywhere before:** `CITATION_WORDS` also contains a bare
`see` and `ref` / `reference`. At HEAD the word **see alone sources 26**
numeric-claim paragraphs. F25 discusses only "source" and scopes its remediation
on that basis, so **the F25 fix is larger than F25 states** and owner decision 3
is currently posed against an incomplete picture.

**My own error, recorded in place.** My first F25 figure was **218** and was
wrong: it counted paragraphs unsourced for any reason, not only those sourced by
a citation word. Corrected method gives 65 with gates on, 105 with gates off.
Caught before it reached the owner, by asking why it diverged so far from the
record rather than assuming the record was wrong.

## AGENTIC AI: item RE-OPENED per directive section 4, and now SETTLED

**Primary source retrieved from EUR-Lex, HTTP 200, 29 July 2026.** Regulation
(EU) 2026/1744, Annex XIV, Section 3:

- **AIH 0401** = "AI systems based on other emerging AI technologies not covered
  by other codes, including Agentic AI"
- **AIH 0205** = "AI systems that learn from their environment, excluding AI
  systems covered under AIH 0401"

**The word "Agentic" appears exactly once in the whole regulation**, at Annex
XIV Section 3(d). Not in any article, not in any recital, no definition, no risk
tier, no obligation. Recital 43 states the AIH codes exist to scope the
designation of conformity assessment bodies so notified bodies "are fully
competent in regard to the AI systems they are required to assess". Recital 45
empowers delegated acts to amend Annex XIV.

**Disposition. The prior STATE.md closure was half right and half wrong, and the
directive was right to re-open it.**

- WRONG on existence: a category label does exist and it names Agentic AI.
- RIGHT on substance: it is a nomenclature code for notified-body competence.
  No definition, no obligations.

**Both careful secondaries were imprecise.** HAQQ ("AIH 0401 = agentic AI") and
NicFab ("AIH 0401 = emerging technologies") each reported half the label. The
actual label is both, in one sentence. Neither is quotable as written.

**Ruling on the OWASP Agentic crosswalk: NO legitimate obligations hook.** A
code that scopes assessor competence is not a source of duties. Regula may
state that the AI Act's notified-body taxonomy names Agentic AI at AIH 0401 and
attaches no obligations to it. It may not present AIH 0401 as a compliance
requirement. **Any surface that mentions it must carry the no-obligations
qualifier**, per the directive's own instruction.

## Standards comment window: flagged, PARTIALLY verified, owner action

`prEN 18228` and `prEN 18282` public enquiry reported closing **30 July 2026**;
`prEN 18229-1` **20 August 2026**.

**Verification status: NOT confirmed against a primary source.** CEN-CENELEC's
own AI page carries no enquiry dates. The JTC 21 tracker is a June 2026 snapshot
with no closing dates and tells the reader to check the live work programme. The
two JTC 21 participant posts announcing the ballots are paywalled, but are dated
**7 and 8 May 2026**, and a standard 12-week CEN enquiry from that start lands
on approximately 31 July, which is consistent. The BSI project page for
`BS EN 18228` (`projects/2025-01990`) exists but would not render.

**Corroborated and consistent, not verified. The owner must confirm with BSI
before relying on it.** Flagged same-day because the window is reported to close
tomorrow and the cost of checking is minutes.

## F25: THE COMPLETE PICTURE, for owner decision 3

MEASURED 29 July 2026 at HEAD over all tracked `.md` and `.html`. Method:
wrap the real `paragraph_has_source`, force `citation-word` to stop sourcing,
one variable, everything else untouched. Counts are **paragraphs carrying at
least one numeric claim** whose only source is a citation word. A paragraph
can contain more than one word, so per-word columns overlap and the union is
the honest total.

| Scope | Gates | union | source | see | ref | reference | other words | multi-word |
|---|---|---|---|---|---|---|---|---|
| Whole repo | ON | **65** | 30 | 20 | 2 | 4 | verdict 9, citation 8, verified-primary 3, primary source 2, verified against 1 | 10 |
| Whole repo | OFF | **108** | 54 | 31 | 5 | 10 | verdict 14, citation 9, verified-primary 4, verified against 3, primary source 2, verified via 1 | 19 |
| `docs/improvement/` only | ON | 35 | 14 | 10 | 1 | 3 | verdict 8, citation 7, others 2 | 7 |
| `docs/improvement/` only | OFF | 50 | 22 | 12 | 1 | 8 | verdict 10, citation 8, others 6 | 12 |
| **Everything else** | ON | **30** | 16 | 10 | 1 | 1 | verified-primary 2, others 4 | 3 |
| **Everything else** | OFF | **58** | 32 | 19 | 4 | 2 | verdict 4, verified-primary 2, others 4 | 7 |

"Gates ON" means the allowlist and quarantine are active, so it is what the
auditor would surface today. "Gates OFF" is the full population the mechanism
touches, and is the number a `CITATION_WORDS` tightening would have to triage.

**Answering the question as posed: the union is NOT materially larger than
105.** It is **108** whole-repo gates-off. `ref` and `reference`, which were
unquantified anywhere, are **5 and 10** whole-repo, and only **4 and 2** on
the surfaces outside this programme's own documents. They are the small arms.
`see` is the large one at **31**, and it was named but never counted.

**The finding that should shape decision 3.** Nearly half the population is
`docs/improvement/`, this programme's own working documents: **50 of 108**
gates-off, **35 of 65** gates-on. Those are not published surfaces in any
meaningful sense. **The decision-relevant figure is the "everything else" row:
58 paragraphs gates-off, 30 gates-on.** Scoping a `CITATION_WORDS` tightening
against 108 overstates the work by about 46%.

**The union figure is unstable by construction, and that is a finding not a
caveat.** It measured 105, then 107, then 108 across three runs on the same
day. Nothing about the auditor changed. What changed is that I wrote a STATE.md
checkpoint and a DIRECTIVE-v3.md, both inside the corpus being measured. **The
instrument's corpus contains the instrument's own output.** This is the second
independent instance today, after the section 10 pair, and it is the worked
example directive section 8 asks to be written up. Any F25 figure must carry
the commit it was taken at.

## SECTION 4 CORRECTION LAYER: what landed, and two corrections to the directive

### Colorado: ALREADY CORRECT. The sweep would have caused a regression.

`content/regulations/colorado.py` already carried SB 26-189 signed 14 May 2026,
duties from 1 Jan 2027, repeal-and-reenactment of SB 24-205, and the 27 April
2026 xAI v. Weiser suspension, verified against `leg.colorado.gov` on
2026-07-16 with docket detail added 07-27. **Re-verified at the primary source
2026-07-29:** the bill history line reads `05/14/2026 | Governor | Governor
Signed`, and the summary says the act "repeals and reenacts those provisions".

**The 29 July sweep downgraded this from settled fact to "conflicting
accounts". Applying that framing would have degraded correct, primary-verified
data.** This is the source-hierarchy rule earning its place on its first use.

Two further statutes added to the fact block, verified at leg.colorado.gov:
**HB 26-1263**, Conversational AI Service Operator Requirements, Governor
Signed `05/29/2026`, act effective 12 Aug 2026 with operator duties from
1 Jan 2027. A 2026 health-care AI statute covering payers and utilisation
review, **bill number reported as HB 26-1139 by a secondary source and NOT
verified**, recorded as unconfirmed.

**Crosswalk decisions, reasons recorded both ways.** HB 26-1263 is IN SCOPE for
a future hook: its AI-interaction disclosure duty is statically detectable by
the same mechanism already used for Article 50, and its audience is Regula's
audience. Not implemented here, because new detection scope belongs in the
Phase 4 plan and not in a factual-correction commit. The health-care statute is
OUT OF SCOPE: its duties fall on insurers and utilisation reviewers, not on
builders of AI systems, and they are organisational rather than detectable in
code.

### CORRECTION TO THE DIRECTIVE 1: the AG enforcement claim is unverified

The directive states "AG will not enforce either statute pending rulemaking".
**The Colorado AG's own AI page (`coag.gov/ai/`) does not say that.** Checked
2026-07-29: it names SB 26-189 and HB 26-1263, records that pre-rulemaking
comment closed 13 July 2026, and says formal rulemaking detail follows once
that process begins. It is silent on enforcement timing. Recorded in
`colorado.py` as UNVERIFIED and **not asserted**. The verified enforcement fact
remains the 27 April 2026 suspension, whose reach to SB 26-189 is still
publicly unresolved.

(The same AG page gives HB 26-1263 as "signed into law July 1, 2026", which the
legislature's own bill history contradicts. Primary beat the agency page.)

### CORRECTION TO THE DIRECTIVE 2: ISO/IEC TR 42106 is not published

The directive lists it as "under publication 2026-04". `iso.org` returned
**HTTP 403** to an automated fetch, so this is NOT primary-verified. The ISO
catalogue entry surfaced in search is titled **ISO/IEC DTR 42106**, and DTR is
the draft stage. Recorded as **draft, unverified**; it does bear on the
benchmark work and should be re-checked by hand before being cited.

### EN 18286: landed, with the load-bearing distinction preserved

Approved 12 July 2026, published as EN 18286:2026, **not yet OJ-cited**, so it
does NOT confer the Article 40 presumption. Three false statements corrected:
`references/harmonised_standards.yaml` (status, published_ref, published_date,
with `oj_reference` deliberately still null and `confers_presumption` still
false); `site/blog/blog-omnibus-delay.html`, which said the standards were "not
expected before Q4 2026 at the earliest"; and
`scripts/generate_documentation.py`, which was wrong twice in one table row,
saying "Awaiting publication" and giving the enquiry as closing October 2026
when it closed January 2026. **That row is emitted into user-facing generated
documentation.**

Confidence is `verified-secondary`, not primary: SGS, a named JTC 21
participant, and the CSA research note agree, but no CEN-CENELEC primary page
carries standard-level status. **The OJ-citation negative is an
absence-of-evidence finding, not a positive confirmation.**

### The 2 August 2030 date

Attributed to Regulation (EU) 2024/1689 **Article 111(2)**, unchanged by the
Omnibus; recital 39 of 2026/1744 clarifies the grace period's scope without
altering the date. The earlier STATE.md closure ("not an Omnibus provision")
was **correct but partial**, and reads that way now rather than as an error.

## NEW FINDING F31: the delta log had a schema and no gate. FIXED.

`content/regulations/delta-log/schema.json` has existed since the delta log was
built. **Nothing validated entries against it.** `build_delta_log.py` reads the
entries and writes the index, feed and summary without checking them, and no
test covered it.

MEASURED 2026-07-29, the first time anything checked: of the 12 tracked
entries, **`2026-04-29-trilogue-failed.json` carried a `summary` of 1058
characters against a `maxLength` of 1000**, and had done since it was
committed. Both entries I added the same day also failed, because
`impact_on_regula_patterns` is an array of objects with a `pattern_id` and an
enumerated `change`, not the free prose it resembles.

`tests/test_delta_log_schema.py` closes it: 14 tests, every entry validated,
a count floor so an empty glob cannot pass vacuously, and **a control that
plants both real defects and asserts rejection**. Control fired both ways
(deliberately corrupted an entry, saw 2 failures; restored, saw 14 pass). The
over-length summary was trimmed to 999 characters with every fact and the
original tense preserved.

**It hard-fails rather than skips when `jsonschema` is missing.** A
`pytest.importorskip` would rebuild the exact blank-gate defect already on
record in this repo.

**Count cascade:** 2,416 to **2,430** via `site_facts.py` then
`cascade_count.py --apply`, in that order, 7 surfaces updated. Every changed
line was read: all are test-count claims, no lockfile, hash or URL touched
(rule 4d). The cascade also propagated a number into a sentence claiming
`12m35s ... verified 2026-07-28`, a runtime never measured at 2,430; that
attribution was corrected rather than left.

## DRAFTED, HELD FOR APPROVAL

`content/blog/article-agentic-ai-annex-xiv.md`, `published: false`. Quotes
Annex XIV Section 3 exactly, states the AIH 0205 exclusion, states plainly that
no obligations attach, and names both trigger conditions. Corrects the two
secondary readings on substance without naming either outlet. **It makes no
uniqueness claim**, because "nobody else published this correctly" cannot be
exhaustively verified. Auditor clean at rc=0 after one real finding of its own
(an unsourced "the only") was fixed with a primary-source link rather than an
allowlist entry.

---

# CHECKPOINT — 29 July 2026, session 5c: DIFF-BASE CLEARED, BRANCH PUSHED

## TASK 1 DIAGNOSIS: both the apparatus and the content were defective

The question nobody had asked was whether the red was the files or the check.
It was both, and they separate cleanly.

**The base selection is NOT defective.** `files_diff_base()` runs
`git diff --name-only --diff-filter=ACMR {base}...HEAD`. Three-dot notation
means merge-base(base, HEAD) to HEAD, which is exactly "what this branch
changed". That is correct and was never the problem.

**The scope IS worth naming.** The function returns file paths and `scan_file`
then audits the WHOLE FILE. The module docstring says the tool exists to
"block commits that introduce unverified factual claims", but it blocks on
every unverified claim in a touched file. That is why a one-line count cascade
into `docs/TRUST.md` inherited 14 findings it did not introduce, and why
the handover could say every cascade commit that has ever run was red.

**One variable at a time settled where the findings came from:**

| Instrument | Content | Claims | Unsourced |
|---|---|---|---|
| `main`'s auditor | `main`'s files | 13 | **0** |
| **HEAD's auditor** | **`main`'s files** | 53 | **30** |
| HEAD's auditor | HEAD's files | 50 | 26 |

Identical bytes, 13 claims detected against 53. **The branch's own repairs
(F21 self-citation, F22 floor removal, the `<pre>` change) made the instrument
roughly four times more sensitive, and it then met pre-existing content.** The
branch did not introduce these claims; it built the thing that can see them.
HEAD's files also score better than main's under the same instrument, 26
against 30, so the branch had already improved these two documents.

### F32, apparatus: the gate blanked the remedy it recommends

`strip_noise()` removes inline code spans, keeping only a span that
**fullmatches** a resolvable repo path. MEASURED on `docs/TRUST.md` L226:
`FILE_REF_RE` matches `benchmarks/label.py` on the raw line and matches
**nothing** after `strip_noise`, because the span is
`benchmarks/label.py score --breakdown`. So citing a file counted and citing
the command that produced the number did not, while PROGRAMME.md Principle 1
lists **MEASURED (command + output)** as an accepted evidence tag and the
auditor's own failure text tells the reader to add "a reference to an existing
file".

Repaired: the span survives when ANY token in it resolves under `REPO_ROOT`.
Repo-wide, one variable, all tracked Markdown and HTML: findings **360 to
355**, total claims **unchanged at 1329**. Five real findings resolved and no
claims hidden. `tests/test_command_citation.py`, 9 tests, is the regression
pair: 3 must pass, 3 must still fail (including a command naming a
nonexistent file, the anti-gaming half), 1 asserts a documented boundary, 2
hold the named documents at zero. **Control run: reverting the repair fails
exactly the two PASS tests.**

The boundary test exists because my first version of it was wrong.
`pytest tests/ --collect-only` names a directory, and `FILE_REF_RE` requires a
file extension, so it does not source its paragraph. The expectation was
wrong, not the code, and the limitation is now asserted so it cannot drift.

### Content: 26 genuine findings, fixed at source

Percentages sat in paragraphs with no in-paragraph source. The markdown tables
could not inherit their captions because a blank line separates them. Fixed by
putting provenance in the paragraph: a source line directly beneath each table
and a reference in each prose paragraph. **Nothing was allowlisted,
quarantined or suppressed.**

### A stale claim, withdrawn rather than annotated

`docs/MODEL_CARD.md` published "13 hand-crafted Python files ... **100%
precision, 100% recall**". The corpus is **38 fixtures** (manifest v2.0:
5 prohibited, 30 high-risk, 3 negative) and `RECALL.json` measures high-risk
recall between **33.3% and 76.7%** by path and gate condition. Replaced with
the four measured conditions, each naming its path and gate per the artefact's
own publication rule.

**`docs/TRUST.md` section 3.4 had already been corrected on 28 July.
MODEL_CARD.md was never updated to match.** Parallel-path drift between two
published surfaces, the exact class `quality-standards.md` warns about.

**Result: `docs/TRUST.md` and `docs/MODEL_CARD.md` are 61 claims, 0 unsourced,
rc=0.** `--diff-base main` falls from **297 to 266** unsourced and neither
document appears in it. Suite **2439 passed in 1028.09s, rc=0**. Six fast
gates rc=0.

## TASK 2: CI DID NOT RUN, AND CANNOT RUN ON THIS BRANCH

Branch pushed. `git ls-remote --heads origin` shows
`improvement/2026-08-programme` at `e2b238c`. `main` unchanged at `6daacd2d`,
still equal to `origin/main`. No PR opened.

**MEASURED: `total_count: 0` runs for the pushed SHA.** Not a failure to
observe, an absence of any run.

**Cause, from the workflow files themselves.** `ci.yaml` declares:

```
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
```

**CI does not trigger on pushes to feature branches.** The same is true of
`codeql.yml` and `regula-scan.yaml`. `ci.yaml` has **no `workflow_dispatch`**,
so it cannot be started by hand either. Verbatim:

```
could not create workflow dispatch event: HTTP 422: Workflow does not have
'workflow_dispatch' trigger
```

**Triage of this result: CI configuration, not a defect and not
environment-specific.** The full matrix (Python 3.10, 3.11, 3.12, 3.13) has
never executed against this branch and cannot without either opening a PR,
which is out of scope this session, or adding a trigger, which is a repair
beyond Task 1.

**What could be run, was run.** Two workflows carry `workflow_dispatch` and
were dispatched against the branch ref:

| Run | Workflow | Result | Wall clock |
|---|---|---|---|
| [30448143491](https://github.com/kuzivaai/getregula/actions/runs/30448143491) | Site Integrity | **completed / success** | 10s |
| [30448145329](https://github.com/kuzivaai/getregula/actions/runs/30448145329) | Test Regula Action | **completed / success** | 1m13s |

Site Integrity executed `python3 scripts/site_integrity.py` on a hosted
ubuntu-24.04 runner against the branch and passed. **This is real remote
evidence, and it is NOT the claim gate and NOT the matrix.** Do not report it
as CI passing.

**The claim gate's push path is dead code in practice.** The
`--diff-base HEAD~1` branch of the conditional only ever executes on a push to
`main`, because pushes elsewhere do not trigger the workflow at all. Every
real invocation on a feature branch goes through the PR path,
`--diff-base origin/main`.

## THE NEXT BINDING CONSTRAINT

**Not the two documents. The 266.**

The moment a PR is opened into `main`, CI runs
`claim_auditor.py --diff-base origin/main`, which scans **57 files** and
reports **266 unsourced across 20 files**. That gate fails on the first PR.
The distribution:

- `docs/improvement/` — **191** across 10 files, led by `PACK-1.5b.md` (50),
  `STATE.md` (38), `BASELINE.md` (26), `PLAN-PHASE4.md` (20)
- `benchmarks/` and `docs/benchmarks/` — **59** across 5 files, led by
  `benchmarks/README.md` (28) and `PRECISION_RECALL_2026_04.md` (21)
- `.claude/rules/` — 8, and `docs/improvement/DIRECTIVE-v3.md` — 2

**Roughly 72% of the blocker is the programme's own working documents**, which
are internal logs rather than published claim surfaces. Whether they belong in
the CI claim gate at all is a scoping decision for the owner, and it is not one
to settle by allowlisting. Recorded, not actioned.

## F25 RE-MEASURED AT A FIXED COMMIT, SELF-REFERENCE REMOVED

Per instruction, measured in a **detached worktree at commit `e2b238c`** with
`docs/improvement/` excluded from the corpus. Corpus: **156 tracked Markdown
and HTML files**, 16 excluded of 172.

| Gates | union | source | see | ref | reference | multi-word |
|---|---|---|---|---|---|---|
| ON | **33** | 19 | 10 | 1 | 1 | 3 |
| OFF | **61** | 35 | 19 | 4 | 2 | 7 |

**This figure is stable and reproducible**, because the corpus no longer
contains the documents that record it and the commit is pinned. The unstable
series it replaces (105, 107, 108 in one day) moved only because checkpoints
were being written into the measured corpus. **Quote this as
"33 / 61 at `e2b238c`", never as a bare number.**

---

# CHECKPOINT, 29 July 2026, session 5d: ITEM 0, THREE GAPS SETTLED

Verification first, all at `ae56f42`: `git log --oneline main..HEAD | wc -l` = **58**;
`git status --porcelain` **empty**; `git rev-parse main origin/main` both
**6daacd2d**; `pytest tests/ -q` **2439 passed rc=0** (932.48s);
`claim_auditor.py --diff-base main` **270 unsourced**. The three load-bearing
items agree, so nothing is public and nothing is on main.

## 0a. THE DISTRIBUTION DOES SUM. THE MASTER RECORD HAD TWO ERRORS.

Produced by enumeration over the full JSON output, not sampling. At
`ae56f42`, 57 files scanned, 899 claims, **270 unsourced across exactly 20
files**, summing to 270 with **no unattributed remainder**.

| Bucket | Findings |
|---|---|
| `docs/improvement/` | **195** |
| `benchmarks/` + `docs/benchmarks/` | **67** |
| `.claude/rules/` | **8** |
| anything else | **0** |

Only `docs/improvement/STATE.md` differs between `e2b238c` and `ae56f42`
(MEASURED: `git diff --name-only e2b238c ae56f42` returns that one path), and
it moved 38 to 42 findings. So at `e2b238c` the buckets were **191 / 67 / 8 =
266**, which matches the total the master record stated.

**The two errors were in the decomposition, not the total:**

1. The `benchmarks/` bucket was stated as **59**. It is **67**, understated by 8.
2. `docs/improvement/DIRECTIVE-v3.md` was listed as a separate "+2" when it is
   **already inside** the 191. Double counted.

191 + 59 + 8 + 2 = 260 against a correct 191 + 67 + 8 = 266. The two errors
partly cancel, which is why the gap looked like six missing findings rather
than two mistakes. **There are no unattributed findings.**

**Root cause: the bucket table was hand-built from grep output.** That is
measurement rule 4c failing for the third time in this programme. The table
above came from `--format json` and a summation.

## 0b. ONE TEST WAS ASSERTING CURRENT BEHAVIOUR. NAMED AND FIXED.

MEASURED by reverting the F32 repair in a scratch worktree at `ae56f42` and
running the pair. Before the fix below, exactly two tests failed:
`test_command_citation_naming_a_real_file_is_a_source` and
`test_interpreter_prefixed_command_is_a_source`.

**The offender was `test_command_naming_a_NONEXISTENT_file_is_not_a_source`.**
It guards the anti-gaming half of the new behaviour, and it **passed with the
repair reverted**, because before the repair every non-fullmatch span was
blanked, so a nonexistent path was rejected for an entirely different reason.
It could not distinguish "the existence check works" from "the repair is not
installed".

An anti-gaming assertion cannot be fail-before-pass-after on its own, because
before the repair the outcome is identical. Renamed to
`test_existence_check_discriminates_real_from_invented_paths` and rewritten to
assert the **contrast**: the same construction with a real file must source,
with an invented file must not. The positive half fails when the repair is
reverted, so the test is now fail-before and pass-after, while the negative
half still guards the existence check against later removal.

**Control re-run: 3 tests now fail with the repair reverted, 9 pass with it
present.** The other four that pass both ways are legitimate: two are the
FAIL half (must hold in both states), one is a deliberate no-regression test
of pre-existing behaviour, one is a documented boundary.

The master record's "three must pass" and "reverting fails exactly the two
PASS tests" were both true but the pairing was ambiguous, because one of the
three was a no-regression test rather than a new-behaviour test.

## 0c. THE PLUS THREE IS MINE, AND IT EXPOSES A CHECK-ORDER DEFECT

**MEASURED: `paragraph_has_source` tests `citation-word` at line 490 and
`file-ref` at line 499.** The weak signal is checked before the strong one and
returns first.

The three paragraphs are the three source lines `e2b238c` added:
`docs/TRUST.md` L230-238 (precision table), `docs/TRUST.md` L242 (by
language), `docs/MODEL_CARD.md` L137-143 (recall table). Each carries a
resolvable repo file reference AND begins `Source:`, so each reports reason
**citation-word** rather than **file-ref**. **My F25-adjacent content fix
increased the F25 population by exactly three.**

**F25's remedy and F32's remedy pull against each other, and whoever disposes
of F25 inherits this constraint.** The instruction "cite the file that
produced the number" is satisfied by writing `Source: path`, and the word
`Source` then masks the file reference that actually does the work.

### The decision-relevant consequence, quantified

For every numeric-claim paragraph currently sourced only by a citation word,
one variable removed (`CITATION_WORDS` disabled), asking what would source it
instead. Corpus excludes `docs/improvement/`, 156 tracked files, at `ae56f42`:

| Gates | union | already sourced by a file-ref, masked by check order | genuinely exposed |
|---|---|---|---|
| ON | 33 | **11** | **22** |
| OFF | 61 | **15** | **46** |

**Roughly a third of F25's population is already properly sourced and merely
mis-attributed.** The real exposure on non-programme surfaces is **22 gates-on
/ 46 gates-off**, not 33 / 61. **Owner decision 3 should be posed against
22 / 46.**

**A cheap structural repair is implied and is NOT done here:** reordering
`paragraph_has_source` to test `file-ref` before `citation-word` would
reclassify those 11 to 15 paragraphs without weakening anything, because
file-ref is the stronger signal and already requires the path to resolve. It
is a behaviour change to the auditor and belongs with the F25 disposition, not
in a verification item. **Recorded, not actioned.**

### An error of mine, in this measurement

My first masking run reported 29 / 58 where the recorded figure is 33 / 61.
Nothing outside `docs/improvement/` had changed, so the two could not both be
right. Cause: my script left `CITATION_WORDS` patched to a never-matching
regex across `scan_file` calls, so later files were scanned with the weak
signal already disabled. Rewritten to capture the originals once and restore
before every call; it then reproduced 33 / 61 exactly. **Caught by noticing
the disagreement, not by the script failing.**

## NEXT

Phase 1.7 scaffolding audit (directive section 5), including the two additions:
scope the em-dash rule to new prose rather than all prose, and encode the
verbatim-record exemption as a rule. **Then** section 6: re-derive Trust and
Detection at HEAD under one written rule, then the traces.
**F25, F29, F30 remain open escalations.** F25 now has its complete table
above, and decision 3 should be posed against the 58/30 row, not the 108/65.

---

# CHECKPOINT, 30 July 2026, session 6: THE HELD TREE LANDED, PHASE 1.7 DONE

Verification first: `pytest tests/ -q` at `e14fdbe` with the previous
session's 12 modified files in the working tree gave **2581 passed in
1036.31s, rc=0** (exit code from `$?` after redirection, sentinel removed
before launch); ruff F821/F811 clean; six fast gates rc=0; self-test 6/6;
doctor 8 passed / 4 info. The handover's "plus 6 subtests" did not appear in
the pytest summary; the likely referent is the self-test's six assertions,
recorded here as interpretation, not fact.

**The 12 held files were verified and committed as six units**
(`820562c`, `2d0cea6`, `3f1a797`, `7317689`, `0b74db0`, `82266e9`); the
ledger's 2026-07-30 evening entry carries the detail, including the
fail-before controls (5 discriminating failures at `e14fdbe` in a worktree
outside /tmp, 104 passed after) and the discarded /tmp-confounded first
control. Four regression tests were added for the three repairs that
arrived without one; cascade 2,581 to 2,585 in the same commit as the
tests. NOT pushed: everything on this branch beyond `f286562` is local.

**Phase 1.7 is DONE** (`4ee37b2`): `docs/improvement/SCAFFOLDING-AUDIT.md`
is the deliverable and the ledger's phase table points at it. The two
STATE 5d additions landed: the em-dash rule is scoped to new prose with the
verbatim-record exemption encoded in CLAUDE.md (untracked, recorded in the
audit), and the stale-status class was fixed at its two live instances
(regulatory-content.md rule, regulatory-context skill).

## NEXT

Unchanged from 5d, minus what landed: **queue item 3, re-derive Trust and
Detection at HEAD under one written rule** (DIRECTIVE-v3 section 6), then
the traces (7 fixtures, per F27), then the Phase 4 plan revision, then
loop 3 in a fresh session. F25, F29 (one surface), F30 remain open owner
escalations; owner decisions 3, 4 (last surface), 5, 6, 7 and 8 unchanged.

---

# CHECKPOINT, 31 July–1 August 2026: COMMERCIAL DEFENSIBILITY GATE

The evaluation froze product commit `94efa9e` and preregistered at `5bd2112`
before result execution. Two protocol deviations are explicit: `84e0118`
separated protocol and product trees before results, and `056bcf2` supplied a
case-insensitive runtime licence acquirer after retaining the frozen
lowercase-licence failure. No detector rule, threshold, corpus label or public
claim was changed.

The result is adverse. Local 1.9.0 detected **0/40** constructed Candidate A
positives and **0/40** Candidate B positives. Transparent baselines detected
**40/40** for both; A produced 4/40 negative false alerts and B 0/40. Two
fresh runs per tool normalised identically. Twelve exact public repositories
were acquired; no independent repository labels exist, so comparator accuracy
is UNTESTABLE. Local and public Regula each exited zero for 9/12 repository
runs and non-zero for 3/12, identically on repeat. Candidate C has 0/30
independently human-labelled scenarios and remains MODEL-PROVISIONAL.

Operationally, local 1.9.0 generated and strictly verified an evidence pack;
public 1.7.4 generated a legacy pack whose strict verification exited 2. Both
versions emitted empty finding lists for the active OpenAI first-use control.
Network behaviour remains UNVERIFIED: `unshare -n` is unavailable and the
frozen Python socket-denial probe invalidates `ssl` import before the scanner
runs.

Verdict: **TECHNICAL_EVIDENCE FAILED; COMPARATIVE_ADVANTAGE NOT_DEMONSTRATED;
PUBLIC_CLAIM_INTEGRITY FAIL; REGULATORY_CURRENCY PARTIAL; OPERATIONAL_READINESS
FAIL; DEMAND_EVIDENCE UNVALIDATED; OVERALL_DECISION STOP.** The detailed
review, claim register, validation-only pilot packet and compact result are in
`docs/commercial/` and `benchmarks/commercial_v1/results/summary.json`.

F25, F30, N35, N43, N50/N54, N53, N55, N57, N6, N7, N10, N11 and N12 remain
open or partially closed exactly as the ledger records. The next bounded unit
is high-consequence public/PyPI claim correction; it must not tune the frozen
benchmark or imply a customer pilot.
[exit 0]
```

Ended: `2026-08-05T00:16:55+01:00`

## Current Git state

Started: `2026-08-05T00:16:55+01:00`

Command:

```console
$ bash -lc 'git status --short --branch; git log -12 --oneline --decorate; git rev-parse HEAD HEAD^{tree} main origin/main; git rev-list --left-right --count origin/main...HEAD; git remote -v; git diff --check'
## audit/regulatory-current-2026-08-04...origin/audit/regulatory-current-2026-08-04
?? docs/improvement/SESSION-LOG-VENTURE-2026-08-05-001618.md
a62e8aa (HEAD -> audit/regulatory-current-2026-08-04, origin/audit/regulatory-current-2026-08-04) Update regulatory claims and assessment safeguards
301a573 (origin/main, main) Fix regulatory currentness and risk messaging (#42)
fabe417 Improve standards evidence and test quality (#41)
1ffbdca Merge pull request #40 from kuzivaai/fix/plain-language-public-entrypoints
be9afdd fix(site): refresh sitemap modification dates
a8301e2 fix(site): clarify public entry journeys
c5508d8 Merge pull request #39 from kuzivaai/fix/public-homepage-gate
3fe88a5 docs(trust): sync docs/TRUST.md custom runner count
9ac770b fix(site): refresh site/sitemap.xml modification dates
09b3192 fix(site): remove internal gate from public homepages
06ac7c7 Merge pull request #38 from kuzivaai/fix/main-empty-diff-base
3c0bf64 (origin/fix/main-empty-diff-base, fix/main-empty-diff-base) test(ci): validate empty claim diff by suffix
a62e8aa6af99e77a49793c7bea398d8c1da171d4
8cd969777ce1a28c43997facd149e882efafbe9b
301a5732b7635c7440ad9179f846c992800b6120
301a5732b7635c7440ad9179f846c992800b6120
0	1
origin	https://github.com/kuzivaai/getregula.git (fetch)
origin	https://github.com/kuzivaai/getregula.git (push)
[exit 0]
```

Ended: `2026-08-05T00:16:55+01:00`

## Current test and generated facts

Started: `2026-08-05T00:16:55+01:00`

Command:

```console
$ bash -lc 'cat data/site_facts.json; python3 scripts/cascade_count.py --check'
{
  "generated_at": "2026-08-04T06:54:50.133712+00:00",
  "source_of_truth": {
    "commands": "scripts/cli*.py (grep '^def cmd_' across all topic modules)",
    "patterns": "scripts/risk_patterns.py + scripts/code_analysis.py + scripts/credential_check.py",
    "frameworks": "references/framework_crosswalk.yaml (unique keys + EU AI Act)",
    "languages": "scripts/ast_engine.py + README",
    "tests": "tests/test_classification.py (grep '^def test_')"
  },
  "counts": {
    "commands": 62,
    "patterns": {
      "tier_groups": 57,
      "tier_regexes": 419,
      "ai_indicators": 212,
      "gpai_training": 17,
      "architecture": 38,
      "data_source": 10,
      "logging": 4,
      "oversight": 4,
      "credential": 18,
      "agentic_categories": 10,
      "grand_total": 722,
      "composite_tier_cred_agentic": 447,
      "historical_330_bucket": 479
    },
    "frameworks": 13,
    "languages": 8,
    "tests": {
      "total_collected": 2690,
      "total_functions": 1964,
      "per_file": {
        "test_agent_governance.py": 28,
        "test_ai_codegen.py": 0,
        "test_aibom.py": 32,
        "test_analysis_manifest.py": 12,
        "test_annotation_stats.py": 0,
        "test_api_server.py": 77,
        "test_audit_scoping.py": 4,
        "test_audit_surface_conformance.py": 0,
        "test_bias_bbq.py": 7,
        "test_bias_report.py": 4,
        "test_bias_stats.py": 9,
        "test_build_regulations.py": 14,
        "test_cascade_count.py": 0,
        "test_check_decompositions.py": 20,
        "test_claim_auditor.py": 41,
        "test_claim_auditor_coords.py": 0,
        "test_claim_auditor_percent.py": 0,
        "test_claim_diff.py": 20,
        "test_claim_quarantine.py": 0,
        "test_classification.py": 440,
        "test_classify_risk.py": 0,
        "test_cli_integration.py": 46,
        "test_collection_integrity.py": 0,
        "test_command_citation.py": 8,
        "test_commercial_benchmark.py": 11,
        "test_compliance_check.py": 64,
        "test_conform.py": 0,
        "test_coverage_critical.py": 46,
        "test_cross_file_flow.py": 103,
        "test_crosswalk_omnibus.py": 10,
        "test_delta_dataset.py": 0,
        "test_delta_log_schema.py": 3,
        "test_dependency_compromised_text.py": 9,
        "test_dependency_pinning.py": 14,
        "test_dependency_scan_safety.py": 5,
        "test_doc_audit.py": 10,
        "test_documentation.py": 16,
        "test_domain_scoring.py": 52,
        "test_dpv_export.py": 19,
        "test_engagement.py": 19,
        "test_evidence_bundle.py": 4,
        "test_evidence_format_v1.py": 14,
        "test_evidence_pack_unit.py": 0,
        "test_exec_summary.py": 10,
        "test_f25_exposure.py": 15,
        "test_file_provenance.py": 9,
        "test_first_run.py": 4,
        "test_gap_demo.py": 2,
        "test_gate_probe.py": 7,
        "test_gdpr_patterns.py": 32,
        "test_gpai_check.py": 27,
        "test_guardrails.py": 24,
        "test_handover_continuity.py": 1,
        "test_headtohead_scoring.py": 0,
        "test_hooks_audit.py": 50,
        "test_hostile_sweep.py": 4,
        "test_ledger_status.py": 13,
        "test_lifecycle_phases.py": 13,
        "test_lifecycle_visibility.py": 5,
        "test_manifest_timestamp.py": 23,
        "test_mcp_server.py": 8,
        "test_merge_blockers.py": 17,
        "test_monitor.py": 24,
        "test_multi_jurisdiction.py": 35,
        "test_new_commands.py": 14,
        "test_omnibus_status.py": 13,
        "test_open_questions.py": 5,
        "test_owasp_agentic.py": 24,
        "test_packaged_data.py": 0,
        "test_pattern_sync.py": 1,
        "test_policy_config.py": 5,
        "test_precision_provenance.py": 0,
        "test_project_fingerprint.py": 79,
        "test_public_claim_integrity.py": 10,
        "test_public_surface_inventory.py": 17,
        "test_published_count_manifest.py": 0,
        "test_recall_artefact.py": 0,
        "test_recall_decomposition.py": 5,
        "test_redteam_coverage.py": 19,
        "test_register.py": 22,
        "test_registry.py": 8,
        "test_release_gate.py": 15,
        "test_reliability.py": 11,
        "test_report.py": 0,
        "test_risk_decisions.py": 17,
        "test_roadmap.py": 16,
        "test_sbom_enrichment.py": 25,
        "test_scan_cache.py": 6,
        "test_scan_safety.py": 26,
        "test_scan_security.py": 8,
        "test_scope_exclusion.py": 1,
        "test_security_hardening.py": 12,
        "test_selfref_sourcing.py": 0,
        "test_session.py": 12,
        "test_setop_inventory.py": 6,
        "test_signing.py": 21,
        "test_site_critical_css.py": 6,
        "test_site_facts.py": 10,
        "test_source_of_truth.py": 8,
        "test_stale_number_floor.py": 0,
        "test_surface_agreement.py": 4,
        "test_telemetry.py": 18,
        "test_tracked_citation.py": 13,
        "test_tracked_inputs.py": 13,
        "test_tree_guard.py": 10
      }
    }
  },
  "notes": {
    "pattern_count_methodology": "Regula's landing pages cite 'tier_regexes risk patterns'. That figure is the total individual regexes in risk_patterns.py across all tiered groups (prohibited, high-risk, limited-risk, AI security, bias, governance, GPAI training). The `historical_330_bucket` adds architecture, credential, and oversight patterns from code_analysis.py. The `grand_total` also includes AI_INDICATORS.",
    "frameworks_vs_claim": "Regula's landing pages cite '13 compliance frameworks'. All 13 are in _FRAMEWORK_KEYS with crosswalk data (OWASP ASI added 2026-07). Colorado SB-189, Canada AIDA, Singapore AI, OECD AI and South Korea AI have display handlers only (no filter keys, no crosswalk)."
  }
}
tree-guard: TREE CHANGED since baseline 2026-07-30T22:45:18.947267+00:00:
tree-guard:   HEAD moved fcc24ff -> a62e8aa
tree-guard:   no longer modified (committed, restored or deleted): .playwright-cli/console-2026-07-10T12-14-07-388Z.log
tree-guard:   no longer modified (committed, restored or deleted): .playwright-cli/console-2026-07-10T12-14-48-086Z.log
tree-guard:   no longer modified (committed, restored or deleted): .playwright-cli/console-2026-07-10T12-15-36-779Z.log
tree-guard:   no longer modified (committed, restored or deleted): .playwright-cli/console-2026-07-16T07-54-43-100Z.log
tree-guard:   no longer modified (committed, restored or deleted): .playwright-cli/console-2026-07-16T07-54-43-551Z.log
tree-guard:   no longer modified (committed, restored or deleted): .playwright-cli/console-2026-07-16T07-54-45-201Z.log
tree-guard:   no longer modified (committed, restored or deleted): .playwright-cli/console-2026-07-16T07-54-45-553Z.log
tree-guard:   no longer modified (committed, restored or deleted): .playwright-cli/console-2026-07-16T07-54-46-722Z.log
tree-guard:   no longer modified (committed, restored or deleted): .playwright-cli/console-2026-07-16T07-54-47-009Z.log
tree-guard:   no longer modified (committed, restored or deleted): .playwright-cli/console-2026-07-16T07-55-14-885Z.log
tree-guard:   no longer modified (committed, restored or deleted): .playwright-cli/console-2026-07-16T07-55-28-858Z.log
tree-guard:   no longer modified (committed, restored or deleted): .playwright-cli/console-2026-07-16T08-19-20-524Z.log
tree-guard:   no longer modified (committed, restored or deleted): .playwright-cli/console-2026-07-16T08-19-23-201Z.log
tree-guard:   no longer modified (committed, restored or deleted): .playwright-cli/console-2026-07-17T06-18-00-765Z.log
tree-guard:   no longer modified (committed, restored or deleted): .playwright-cli/console-2026-07-17T06-18-01-000Z.log
tree-guard:   no longer modified (committed, restored or deleted): .playwright-cli/console-2026-07-17T06-18-30-465Z.log
tree-guard:   no longer modified (committed, restored or deleted): .playwright-cli/console-2026-07-17T06-18-32-763Z.log
tree-guard:   no longer modified (committed, restored or deleted): .playwright-cli/console-2026-07-17T06-18-33-920Z.log
tree-guard:   no longer modified (committed, restored or deleted): .playwright-cli/console-2026-07-18T22-20-12-118Z.log
tree-guard:   no longer modified (committed, restored or deleted): .playwright-cli/console-2026-07-18T22-20-12-641Z.log
tree-guard:   no longer modified (committed, restored or deleted): .playwright-cli/console-2026-07-18T22-21-35-699Z.log
tree-guard:   no longer modified (committed, restored or deleted): .playwright-cli/console-2026-07-18T22-40-46-287Z.log
tree-guard:   no longer modified (committed, restored or deleted): .playwright-cli/console-2026-07-18T22-46-21-258Z.log
tree-guard:   no longer modified (committed, restored or deleted): .playwright-cli/console-2026-07-18T22-46-24-872Z.log
tree-guard:   no longer modified (committed, restored or deleted): .playwright-cli/console-2026-07-20T06-24-19-896Z.log
tree-guard:   no longer modified (committed, restored or deleted): .playwright-cli/console-2026-07-20T06-24-20-260Z.log
tree-guard:   no longer modified (committed, restored or deleted): .playwright-cli/console-2026-07-20T06-24-30-572Z.log
tree-guard:   no longer modified (committed, restored or deleted): .playwright-cli/console-2026-07-20T06-25-03-822Z.log
tree-guard:   no longer modified (committed, restored or deleted): .playwright-cli/console-2026-07-20T06-25-04-106Z.log
tree-guard:   no longer modified (committed, restored or deleted): .playwright-cli/console-2026-07-20T06-25-04-289Z.log
tree-guard:   no longer modified (committed, restored or deleted): .playwright-cli/console-2026-07-20T06-25-05-552Z.log
tree-guard:   no longer modified (committed, restored or deleted): .playwright-cli/console-2026-07-20T06-47-16-954Z.log
tree-guard:   no longer modified (committed, restored or deleted): .playwright-cli/console-2026-07-20T06-49-04-182Z.log
tree-guard:   no longer modified (committed, restored or deleted): .playwright-cli/console-2026-07-20T06-49-08-597Z.log
tree-guard:   no longer modified (committed, restored or deleted): .playwright-cli/console-2026-07-20T06-50-17-020Z.log
tree-guard:   no longer modified (committed, restored or deleted): .playwright-cli/page-2026-07-10T12-13-02-722Z.yml
tree-guard:   no longer modified (committed, restored or deleted): .playwright-cli/page-2026-07-10T12-13-02-797Z.yml
tree-guard:   no longer modified (committed, restored or deleted): .playwright-cli/page-2026-07-10T12-13-37-323Z.yml
tree-guard:   no longer modified (committed, restored or deleted): .playwright-cli/page-2026-07-10T12-13-44-497Z.yml
tree-guard:   no longer modified (committed, restored or deleted): .playwright-cli/page-2026-07-10T12-13-46-628Z.yml
tree-guard:   no longer modified (committed, restored or deleted): .playwright-cli/page-2026-07-10T12-14-08-003Z.yml
tree-guard:   no longer modified (committed, restored or deleted): .playwright-cli/page-2026-07-10T12-14-08-163Z.yml
tree-guard:   no longer modified (committed, restored or deleted): .playwright-cli/page-2026-07-10T12-14-22-188Z.yml
tree-guard:   no longer modified (committed, restored or deleted): .playwright-cli/page-2026-07-10T12-14-22-280Z.yml
tree-guard:   no longer modified (committed, restored or deleted): .playwright-cli/page-2026-07-10T12-14-48-701Z.yml
tree-guard:   no longer modified (committed, restored or deleted): .playwright-cli/page-2026-07-10T12-14-48-822Z.yml
tree-guard:   no longer modified (committed, restored or deleted): .playwright-cli/page-2026-07-10T12-15-20-350Z.yml
tree-guard:   no longer modified (committed, restored or deleted): .playwright-cli/page-2026-07-10T12-15-22-463Z.yml
tree-guard:   no longer modified (committed, restored or deleted): .playwright-cli/page-2026-07-10T12-15-39-082Z.yml
tree-guard:   no longer modified (committed, restored or deleted): .playwright-cli/page-2026-07-10T12-15-39-336Z.yml
tree-guard:   no longer modified (committed, restored or deleted): .playwright-cli/page-2026-07-10T12-15-56-537Z.yml
tree-guard:   no longer modified (committed, restored or deleted): .playwright-cli/page-2026-07-10T12-15-56-670Z.yml
tree-guard:   no longer modified (committed, restored or deleted): .playwright-cli/page-2026-07-10T12-16-19-481Z.yml
tree-guard:   no longer modified (committed, restored or deleted): .playwright-cli/page-2026-07-10T12-16-22-532Z.yml
tree-guard:   no longer modified (committed, restored or deleted): .playwright-cli/page-2026-07-10T12-17-25-976Z.yml
tree-guard:   no longer modified (committed, restored or deleted): .playwright-cli/page-2026-07-16T07-54-43-486Z.yml
tree-guard:   no longer modified (committed, restored or deleted): .playwright-cli/page-2026-07-16T07-54-45-487Z.yml
tree-guard:   no longer modified (committed, restored or deleted): .playwright-cli/page-2026-07-16T07-54-46-949Z.yml
tree-guard:   no longer modified (committed, restored or deleted): .playwright-cli/page-2026-07-16T07-55-15-146Z.yml
tree-guard:   no longer modified (committed, restored or deleted): .playwright-cli/page-2026-07-16T07-55-29-084Z.yml
tree-guard:   no longer modified (committed, restored or deleted): .playwright-cli/page-2026-07-16T08-19-20-785Z.yml
tree-guard:   no longer modified (committed, restored or deleted): .playwright-cli/page-2026-07-16T08-19-23-464Z.yml
tree-guard:   no longer modified (committed, restored or deleted): .playwright-cli/page-2026-07-17T06-18-00-965Z.yml
tree-guard:   no longer modified (committed, restored or deleted): .playwright-cli/page-2026-07-17T06-18-30-565Z.yml
tree-guard:   no longer modified (committed, restored or deleted): .playwright-cli/page-2026-07-17T06-18-31-686Z.yml
tree-guard:   no longer modified (committed, restored or deleted): .playwright-cli/page-2026-07-17T06-18-32-841Z.yml
tree-guard:   no longer modified (committed, restored or deleted): .playwright-cli/page-2026-07-18T22-20-12-305Z.yml
tree-guard:   no longer modified (committed, restored or deleted): .playwright-cli/page-2026-07-18T22-21-35-888Z.yml
tree-guard:   no longer modified (committed, restored or deleted): .playwright-cli/page-2026-07-18T22-40-46-626Z.yml
tree-guard:   no longer modified (committed, restored or deleted): .playwright-cli/page-2026-07-18T22-46-21-399Z.yml
tree-guard:   no longer modified (committed, restored or deleted): .playwright-cli/page-2026-07-20T06-24-20-200Z.yml
tree-guard:   no longer modified (committed, restored or deleted): .playwright-cli/page-2026-07-20T06-25-04-053Z.yml
tree-guard:   no longer modified (committed, restored or deleted): .playwright-cli/page-2026-07-20T06-25-04-242Z.yml
tree-guard:   no longer modified (committed, restored or deleted): .playwright-cli/page-2026-07-20T06-25-04-434Z.yml
tree-guard:   no longer modified (committed, restored or deleted): .playwright-cli/page-2026-07-20T06-25-05-658Z.yml
tree-guard:   no longer modified (committed, restored or deleted): .playwright-cli/page-2026-07-20T06-47-17-530Z.yml
tree-guard:   no longer modified (committed, restored or deleted): .playwright-cli/page-2026-07-20T06-47-37-735Z.yml
tree-guard:   no longer modified (committed, restored or deleted): .playwright-cli/page-2026-07-20T06-48-24-980Z.yml
tree-guard:   no longer modified (committed, restored or deleted): .playwright-cli/page-2026-07-20T06-49-04-312Z.yml
tree-guard:   no longer modified (committed, restored or deleted): .playwright-cli/page-2026-07-20T06-49-08-684Z.yml
tree-guard:   no longer modified (committed, restored or deleted): .playwright-cli/page-2026-07-20T06-50-17-584Z.yml
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/10060530066913676843
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/10288967754928098818
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/1062959321936563370
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/10682181070463058704
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/10975585647256133724
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/11248352602224924173
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/1141437365791308822
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/11535127536693357146
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/11627417047363554554
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/11656578670900320949
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/1177916081738019672
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/12117695073368083818
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/12157329268326334863
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/12185616074612056005
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/12327869989846289908
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/12509413967127385282
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/12678664956100010584
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/12680368827053363219
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/12721647714237491997
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/12887264394569640538
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/12998679185779951236
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/13359478430938736963
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/13374316855513984473
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/13402565982592032791
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/13484584576669405868
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/13934329905766932625
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/14119146789961193007
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/14236911508772218206
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/14242818881845187756
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/14312863034831352441
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/14445803355040041070
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/14456024132233837155
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/14524215636481096941
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/14598430838779402040
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/14742171529521460699
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/1475420656038811049
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/14822436699309884481
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/15073101386765111732
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/15109502327779083974
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/15118110071901061939
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/15455021840237970527
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/15821951049318055345
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/15857467540530299390
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/15965316490206987096
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/16374213220153077883
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/16495709892262913540
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/16515286662469573153
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/16556721652630733948
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/16759996890714964480
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/16851900890884870201
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/17351095329733857431
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/17498189843125760543
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/17569817446572468085
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/17782022611696870821
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/17937576021711127322
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/17966397915973335548
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/18057661873868753599
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/18244623185857116438
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/1932783278862069705
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/1938674062034232501
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/2062826022172623335
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/2365246935310357698
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/2737602287794513763
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/2916096708638692640
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/2992974549050601250
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/3155727760561208347
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/339817266268791649
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/3614020819875675325
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/3846944800769298756
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/4245798094273911952
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/4285149414886197758
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/4798616508748937009
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/5020900684261911019
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/5105287937893990553
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/5346726449490190912
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/5361434495073173672
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/5473761695116906488
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/5704246755681146481
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/5939274859232502563
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/6019243210323724210
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/6061531345416435896
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/6129123475089029028
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/622055815074279103
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/6309026210631202743
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/6744457395501996450
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/6750397649425066874
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/6851488678233090709
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/6870706806841642915
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/6877058894746434361
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/6938854268439649072
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/7286780586613459894
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/7684695631548650602
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/7773430148698074079
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/7814232156828563520
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/8071206663921278552
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/8309477949188516385
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/8458847643990882456
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/8614344456978418839
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/8890319054942393369
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/8958513815527453212
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/9054647964243579189
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/9226984356755708620
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/9604961994856187666
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/9675118094967931783
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/9695373623381316487
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/9769007785485964783
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/985326426925707105
tree-guard:   no longer modified (committed, restored or deleted): .ruff_cache/0.15.10/9958882783994011779
tree-guard:   no longer modified (committed, restored or deleted): build/lib/references/FETCH.md
tree-guard:   no longer modified (committed, restored or deleted): build/lib/references/__init__.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/references/advisories/pypi/litellm/x_REGULA-2026-001.yaml
tree-guard:   no longer modified (committed, restored or deleted): build/lib/references/annex_iv_template.md
tree-guard:   no longer modified (committed, restored or deleted): build/lib/references/annex_viii_sections.json
tree-guard:   no longer modified (committed, restored or deleted): build/lib/references/article_obligations.yaml
tree-guard:   no longer modified (committed, restored or deleted): build/lib/references/en18228_mapping.yaml
tree-guard:   no longer modified (committed, restored or deleted): build/lib/references/en18282_mapping.yaml
tree-guard:   no longer modified (committed, restored or deleted): build/lib/references/eu_ai_act_articles_9_15.md
tree-guard:   no longer modified (committed, restored or deleted): build/lib/references/framework_crosswalk.yaml
tree-guard:   no longer modified (committed, restored or deleted): build/lib/references/gpai_code_of_practice.yaml
tree-guard:   no longer modified (committed, restored or deleted): build/lib/references/gpai_obligations.md
tree-guard:   no longer modified (committed, restored or deleted): build/lib/references/gpai_signatories.yaml
tree-guard:   no longer modified (committed, restored or deleted): build/lib/references/harmonised_standards.yaml
tree-guard:   no longer modified (committed, restored or deleted): build/lib/references/iso_42001_mapping.yaml
tree-guard:   no longer modified (committed, restored or deleted): build/lib/references/jurisdictions/colorado.yaml
tree-guard:   no longer modified (committed, restored or deleted): build/lib/references/jurisdictions/eu_ai_act.yaml
tree-guard:   no longer modified (committed, restored or deleted): build/lib/references/jurisdictions/south_korea.yaml
tree-guard:   no longer modified (committed, restored or deleted): build/lib/references/mitre_atlas.yaml
tree-guard:   no longer modified (committed, restored or deleted): build/lib/references/owasp_agentic_top10.yaml
tree-guard:   no longer modified (committed, restored or deleted): build/lib/references/owasp_llm_top10.yaml
tree-guard:   no longer modified (committed, restored or deleted): build/lib/references/risk_indicators.yaml
tree-guard:   no longer modified (committed, restored or deleted): build/lib/references/tree_sitter_implementation_guide.md
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/__init__.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/__main__.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/adoption_pulse.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/agent_monitor.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/ai_code_governance.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/aibom.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/api_server.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/assess.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/ast_analysis.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/ast_context.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/ast_engine.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/baseline.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/benchmark.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/bias_bbq.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/bias_data/bbq_sample.json
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/bias_eval.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/bias_report.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/bias_stats.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/build_delta_dataset.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/build_delta_log.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/build_regulations.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/ci_heal.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/claim_auditor.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/classify_risk.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/cli.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/cli_admin.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/cli_analysis.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/cli_compliance.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/cli_evidence.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/cli_governance.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/cli_infra.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/cli_monitor.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/cli_report.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/cli_scan.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/cli_util.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/code_analysis.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/compliance_check.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/config_validator.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/conform.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/constants.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/credential_check.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/cross_file_flow.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/custom_rules.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/degradation.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/demo_screenshots.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/demos/__init__.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/demos/cv_screening_app.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/dependency_scan.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/dev_sentiment.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/discover_ai_systems.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/doc_audit.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/doctor.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/domain_scoring.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/dpv_data/dpv_aiact_terms.json
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/dpv_export.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/eli_data/eli_ontology_terms.json
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/engagement.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/envelope.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/errors.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/evidence_pack.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/exec_summary.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/exempt_check.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/explain.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/explain_articles.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/extract_patterns.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/feed.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/findings_view.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/framework_mapper.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/gdpr_patterns.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/gdpr_scan.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/generate_documentation.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/gpai_check.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/gsc_fetch.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/guardrail_scanner.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/handoff.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/i18n.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/indexnow.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/init_wizard.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/install.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/log_event.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/make_og_uae.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/mcp_server.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/metrics.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/minify_css.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/model_inventory.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/monitor.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/notebook.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/omnibus.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/pdf_export.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/planning_consistency.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/policy_config.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/project_fingerprint.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/questionnaire.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/quickstart.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/refresh_dpv_vocab.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/refresh_eli_vocab.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/register.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/regulation_map.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/regwatch.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/release_gate.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/remediation.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/remediation_plan.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/report.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/risk_decisions.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/risk_patterns.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/risk_types.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/roadmap.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/sbom.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/scan_benchmarks.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/scan_cache.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/scan_safety.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/security_self_check.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/self_test.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/session.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/signing.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/site_facts.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/site_integrity.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/telemetry.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/term_style.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/timeline.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/timestamp.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/transparency.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/update_sitemap.py
tree-guard:   no longer modified (committed, restored or deleted): build/lib/scripts/verify_seo.py
tree-guard:   no longer modified (committed, restored or deleted): dist/regula_ai-1.9.0-py3-none-any.whl
tree-guard:   no longer modified (committed, restored or deleted): dist/regula_ai-1.9.0.tar.gz
tree-guard:   no longer modified (committed, restored or deleted): regula_ai.egg-info/PKG-INFO
tree-guard:   no longer modified (committed, restored or deleted): regula_ai.egg-info/SOURCES.txt
tree-guard:   no longer modified (committed, restored or deleted): regula_ai.egg-info/dependency_links.txt
tree-guard:   no longer modified (committed, restored or deleted): regula_ai.egg-info/entry_points.txt
tree-guard:   no longer modified (committed, restored or deleted): regula_ai.egg-info/requires.txt
tree-guard:   no longer modified (committed, restored or deleted): regula_ai.egg-info/top_level.txt
tree-guard:   no longer modified (committed, restored or deleted): vscode-extension/node_modules/
tree-guard:   no longer modified (committed, restored or deleted): vscode-extension/out/extension.js
tree-guard:   no longer modified (committed, restored or deleted): vscode-extension/regula-ai-act-0.1.0.vsix
tree-guard:   newly changed since record: .playwright-cli/console-2026-08-03T19-42-13-454Z.log
tree-guard:   newly changed since record: .playwright-cli/console-2026-08-03T22-32-35-815Z.log
tree-guard:   newly changed since record: .playwright-cli/console-2026-08-03T22-34-25-833Z.log
tree-guard:   newly changed since record: .playwright-cli/console-2026-08-03T22-35-53-989Z.log
tree-guard:   newly changed since record: .playwright-cli/console-2026-08-04T06-44-06-549Z.log
tree-guard:   newly changed since record: .playwright-cli/console-2026-08-04T10-38-06-569Z.log
tree-guard:   newly changed since record: .playwright-cli/console-2026-08-04T13-29-41-259Z.log
tree-guard:   newly changed since record: .playwright-cli/console-2026-08-04T13-30-27-385Z.log
tree-guard:   newly changed since record: .playwright-cli/console-2026-08-04T15-43-21-019Z.log
tree-guard:   newly changed since record: .playwright-cli/console-2026-08-04T15-49-47-206Z.log
tree-guard:   newly changed since record: .playwright-cli/console-2026-08-04T15-50-54-507Z.log
tree-guard:   newly changed since record: .playwright-cli/console-2026-08-04T15-51-21-437Z.log
tree-guard:   newly changed since record: .playwright-cli/page-2026-08-03T19-16-41-244Z.yml
tree-guard:   newly changed since record: .playwright-cli/page-2026-08-03T19-42-14-041Z.yml
tree-guard:   newly changed since record: .playwright-cli/page-2026-08-03T20-44-44-042Z.yml
tree-guard:   newly changed since record: .playwright-cli/page-2026-08-03T20-52-15-025Z.yml
tree-guard:   newly changed since record: .playwright-cli/page-2026-08-03T20-52-21-926Z.yml
tree-guard:   newly changed since record: .playwright-cli/page-2026-08-03T22-32-36-581Z.yml
tree-guard:   newly changed since record: .playwright-cli/page-2026-08-03T22-34-25-953Z.yml
tree-guard:   newly changed since record: .playwright-cli/page-2026-08-03T22-34-33-912Z.yml
tree-guard:   newly changed since record: .playwright-cli/page-2026-08-03T22-35-54-139Z.yml
tree-guard:   newly changed since record: .playwright-cli/page-2026-08-03T22-35-57-380Z.yml
tree-guard:   newly changed since record: .playwright-cli/page-2026-08-03T22-36-01-630Z.yml
tree-guard:   newly changed since record: .playwright-cli/page-2026-08-03T22-36-03-813Z.yml
tree-guard:   newly changed since record: .playwright-cli/page-2026-08-04T00-25-20-314Z.yml
tree-guard:   newly changed since record: .playwright-cli/page-2026-08-04T00-25-29-436Z.yml
tree-guard:   newly changed since record: .playwright-cli/page-2026-08-04T00-25-32-587Z.yml
tree-guard:   newly changed since record: .playwright-cli/page-2026-08-04T00-25-44-585Z.yml
tree-guard:   newly changed since record: .playwright-cli/page-2026-08-04T00-25-46-707Z.yml
tree-guard:   newly changed since record: .playwright-cli/page-2026-08-04T00-36-48-567Z.yml
tree-guard:   newly changed since record: .playwright-cli/page-2026-08-04T00-36-53-448Z.yml
tree-guard:   newly changed since record: .playwright-cli/page-2026-08-04T06-44-06-746Z.yml
tree-guard:   newly changed since record: .playwright-cli/page-2026-08-04T06-44-16-177Z.yml
tree-guard:   newly changed since record: .playwright-cli/page-2026-08-04T10-38-06-696Z.yml
tree-guard:   newly changed since record: .playwright-cli/page-2026-08-04T10-38-45-085Z.yml
tree-guard:   newly changed since record: .playwright-cli/page-2026-08-04T10-46-24-204Z.yml
tree-guard:   newly changed since record: .playwright-cli/page-2026-08-04T10-46-35-655Z.yml
tree-guard:   newly changed since record: .playwright-cli/page-2026-08-04T12-46-35-694Z.yml
tree-guard:   newly changed since record: .playwright-cli/page-2026-08-04T12-47-03-487Z.yml
tree-guard:   newly changed since record: .playwright-cli/page-2026-08-04T13-29-41-561Z.yml
tree-guard:   newly changed since record: .playwright-cli/page-2026-08-04T13-29-45-852Z.png
tree-guard:   newly changed since record: .playwright-cli/page-2026-08-04T13-30-17-398Z.yml
tree-guard:   newly changed since record: .playwright-cli/page-2026-08-04T13-30-19-871Z.png
tree-guard:   newly changed since record: .playwright-cli/page-2026-08-04T13-30-27-464Z.yml
tree-guard:   newly changed since record: .playwright-cli/page-2026-08-04T13-30-37-948Z.yml
tree-guard:   newly changed since record: .playwright-cli/page-2026-08-04T13-30-56-512Z.yml
tree-guard:   newly changed since record: .playwright-cli/page-2026-08-04T15-43-21-177Z.yml
tree-guard:   newly changed since record: .playwright-cli/page-2026-08-04T15-43-32-063Z.yml
tree-guard:   newly changed since record: .playwright-cli/page-2026-08-04T15-47-17-423Z.yml
tree-guard:   newly changed since record: .playwright-cli/page-2026-08-04T15-47-26-974Z.yml
tree-guard:   newly changed since record: .playwright-cli/page-2026-08-04T15-49-19-357Z.yml
tree-guard:   newly changed since record: .playwright-cli/page-2026-08-04T15-49-47-311Z.yml
tree-guard:   newly changed since record: .playwright-cli/page-2026-08-04T15-49-56-645Z.yml
tree-guard:   newly changed since record: .playwright-cli/page-2026-08-04T15-50-06-399Z.yml
tree-guard:   newly changed since record: .playwright-cli/page-2026-08-04T15-50-22-250Z.yml
tree-guard:   newly changed since record: .playwright-cli/page-2026-08-04T15-50-54-666Z.yml
tree-guard:   newly changed since record: .playwright-cli/page-2026-08-04T15-51-16-023Z.yml
tree-guard:   newly changed since record: .playwright-cli/page-2026-08-04T15-51-21-535Z.yml
tree-guard:   newly changed since record: .playwright-cli/page-2026-08-04T19-41-56-918Z.yml
tree-guard:   newly changed since record: .playwright-cli/page-2026-08-04T19-42-06-077Z.yml
tree-guard:   newly changed since record: .playwright-cli/page-2026-08-04T19-42-19-842Z.yml
tree-guard:   newly changed since record: .playwright-cli/page-2026-08-04T19-42-28-445Z.yml
tree-guard:   newly changed since record: .playwright-cli/page-2026-08-04T19-42-35-113Z.yml
tree-guard:   newly changed since record: benchmarks/commercial_v1/__pycache__/acquire.cpython-312.pyc
tree-guard:   newly changed since record: benchmarks/commercial_v1/__pycache__/build_annotation_pack.cpython-312.pyc
tree-guard:   newly changed since record: benchmarks/commercial_v1/__pycache__/build_corpus.cpython-312.pyc
tree-guard:   newly changed since record: benchmarks/commercial_v1/__pycache__/gate.cpython-312.pyc
tree-guard:   newly changed since record: benchmarks/commercial_v1/__pycache__/install_tools.cpython-312.pyc
tree-guard:   newly changed since record: benchmarks/commercial_v1/__pycache__/network_probe.cpython-312.pyc
tree-guard:   newly changed since record: benchmarks/commercial_v1/__pycache__/normalise.cpython-312.pyc
tree-guard:   newly changed since record: benchmarks/commercial_v1/__pycache__/operations.cpython-312.pyc
tree-guard:   newly changed since record: benchmarks/commercial_v1/__pycache__/run.cpython-312.pyc
tree-guard:   newly changed since record: benchmarks/commercial_v1/__pycache__/score.cpython-312.pyc
tree-guard:   newly changed since record: benchmarks/commercial_v1/__pycache__/select_repositories.cpython-312.pyc
tree-guard:   newly changed since record: benchmarks/commercial_v1/__pycache__/verify.cpython-312.pyc
tree-guard:   newly changed since record: conformity-evidence-project-2026-07-31/00-assessment-summary.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-07-31/01-risk-classification/coverage.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-07-31/01-risk-classification/findings.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-07-31/02-risk-management-art9/coverage.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-07-31/02-risk-management-art9/evidence.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-07-31/03-data-governance-art10/coverage.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-07-31/03-data-governance-art10/evidence.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-07-31/04-technical-documentation-art11/annex-iv-draft.md
tree-guard:   newly changed since record: conformity-evidence-project-2026-07-31/04-technical-documentation-art11/coverage.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-07-31/04-technical-documentation-art11/evidence.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-07-31/05-record-keeping-art12/audit-trail.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-07-31/05-record-keeping-art12/coverage.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-07-31/05-record-keeping-art12/evidence.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-07-31/06-transparency-art13/coverage.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-07-31/06-transparency-art13/evidence.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-07-31/07-human-oversight-art14/coverage.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-07-31/07-human-oversight-art14/evidence.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-07-31/07-human-oversight-art14/oversight-analysis.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-07-31/08-accuracy-robustness-art15/coverage.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-07-31/08-accuracy-robustness-art15/evidence.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-07-31/08-accuracy-robustness-art15/sbom.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-07-31/09-supply-chain/dependency-report.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-07-31/09-supply-chain/sbom.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-07-31/10-declaration-of-conformity/declaration-template.md
tree-guard:   newly changed since record: conformity-evidence-project-2026-07-31/11-remediation/remediation-plan.md
tree-guard:   newly changed since record: conformity-evidence-project-2026-07-31/README.md
tree-guard:   newly changed since record: conformity-evidence-project-2026-07-31/manifest.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-08-01/00-assessment-summary.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-08-01/01-risk-classification/coverage.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-08-01/01-risk-classification/findings.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-08-01/02-risk-management-art9/coverage.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-08-01/02-risk-management-art9/evidence.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-08-01/03-data-governance-art10/coverage.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-08-01/03-data-governance-art10/evidence.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-08-01/04-technical-documentation-art11/annex-iv-draft.md
tree-guard:   newly changed since record: conformity-evidence-project-2026-08-01/04-technical-documentation-art11/coverage.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-08-01/04-technical-documentation-art11/evidence.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-08-01/05-record-keeping-art12/audit-trail.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-08-01/05-record-keeping-art12/coverage.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-08-01/05-record-keeping-art12/evidence.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-08-01/06-transparency-art13/coverage.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-08-01/06-transparency-art13/evidence.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-08-01/07-human-oversight-art14/coverage.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-08-01/07-human-oversight-art14/evidence.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-08-01/07-human-oversight-art14/oversight-analysis.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-08-01/08-accuracy-robustness-art15/coverage.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-08-01/08-accuracy-robustness-art15/evidence.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-08-01/08-accuracy-robustness-art15/sbom.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-08-01/09-supply-chain/dependency-report.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-08-01/09-supply-chain/sbom.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-08-01/10-declaration-of-conformity/declaration-template.md
tree-guard:   newly changed since record: conformity-evidence-project-2026-08-01/11-remediation/remediation-plan.md
tree-guard:   newly changed since record: conformity-evidence-project-2026-08-01/README.md
tree-guard:   newly changed since record: conformity-evidence-project-2026-08-01/manifest.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-08-03/00-assessment-summary.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-08-03/01-risk-classification/coverage.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-08-03/01-risk-classification/findings.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-08-03/02-risk-management-art9/coverage.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-08-03/02-risk-management-art9/evidence.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-08-03/03-data-governance-art10/coverage.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-08-03/03-data-governance-art10/evidence.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-08-03/04-technical-documentation-art11/annex-iv-draft.md
tree-guard:   newly changed since record: conformity-evidence-project-2026-08-03/04-technical-documentation-art11/coverage.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-08-03/04-technical-documentation-art11/evidence.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-08-03/05-record-keeping-art12/audit-trail.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-08-03/05-record-keeping-art12/coverage.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-08-03/05-record-keeping-art12/evidence.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-08-03/06-transparency-art13/coverage.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-08-03/06-transparency-art13/evidence.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-08-03/07-human-oversight-art14/coverage.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-08-03/07-human-oversight-art14/evidence.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-08-03/07-human-oversight-art14/oversight-analysis.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-08-03/08-accuracy-robustness-art15/coverage.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-08-03/08-accuracy-robustness-art15/evidence.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-08-03/08-accuracy-robustness-art15/sbom.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-08-03/09-supply-chain/dependency-report.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-08-03/09-supply-chain/sbom.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-08-03/10-declaration-of-conformity/declaration-template.md
tree-guard:   newly changed since record: conformity-evidence-project-2026-08-03/11-remediation/remediation-plan.md
tree-guard:   newly changed since record: conformity-evidence-project-2026-08-03/README.md
tree-guard:   newly changed since record: conformity-evidence-project-2026-08-03/manifest.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-08-04/00-assessment-summary.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-08-04/01-risk-classification/coverage.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-08-04/01-risk-classification/findings.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-08-04/02-risk-management-art9/coverage.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-08-04/02-risk-management-art9/evidence.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-08-04/03-data-governance-art10/coverage.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-08-04/03-data-governance-art10/evidence.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-08-04/04-technical-documentation-art11/annex-iv-draft.md
tree-guard:   newly changed since record: conformity-evidence-project-2026-08-04/04-technical-documentation-art11/coverage.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-08-04/04-technical-documentation-art11/evidence.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-08-04/05-record-keeping-art12/audit-trail.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-08-04/05-record-keeping-art12/coverage.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-08-04/05-record-keeping-art12/evidence.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-08-04/06-transparency-art13/coverage.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-08-04/06-transparency-art13/evidence.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-08-04/07-human-oversight-art14/coverage.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-08-04/07-human-oversight-art14/evidence.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-08-04/07-human-oversight-art14/oversight-analysis.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-08-04/08-accuracy-robustness-art15/coverage.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-08-04/08-accuracy-robustness-art15/evidence.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-08-04/08-accuracy-robustness-art15/sbom.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-08-04/09-supply-chain/dependency-report.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-08-04/09-supply-chain/sbom.json
tree-guard:   newly changed since record: conformity-evidence-project-2026-08-04/10-declaration-of-conformity/declaration-template.md
tree-guard:   newly changed since record: conformity-evidence-project-2026-08-04/11-remediation/remediation-plan.md
tree-guard:   newly changed since record: conformity-evidence-project-2026-08-04/README.md
tree-guard:   newly changed since record: conformity-evidence-project-2026-08-04/manifest.json
tree-guard:   newly changed since record: docs/improvement/SESSION-LOG-VENTURE-2026-08-05-001618.md
tree-guard:   newly changed since record: evidence-pack-project-2026-07-31/00-summary.md
tree-guard:   newly changed since record: evidence-pack-project-2026-07-31/01-scan-results.json
tree-guard:   newly changed since record: evidence-pack-project-2026-07-31/02-gap-assessment.json
tree-guard:   newly changed since record: evidence-pack-project-2026-07-31/03-annex-iv-draft.md
tree-guard:   newly changed since record: evidence-pack-project-2026-07-31/04-dependency-report.json
tree-guard:   newly changed since record: evidence-pack-project-2026-07-31/05-audit-trail.json
tree-guard:   newly changed since record: evidence-pack-project-2026-07-31/06-remediation-plan.md
tree-guard:   newly changed since record: evidence-pack-project-2026-07-31/07-risk-decisions.json
tree-guard:   newly changed since record: evidence-pack-project-2026-07-31/README.md
tree-guard:   newly changed since record: evidence-pack-project-2026-07-31/manifest.json
tree-guard:   newly changed since record: evidence-pack-project-2026-08-01/00-summary.md
tree-guard:   newly changed since record: evidence-pack-project-2026-08-01/01-scan-results.json
tree-guard:   newly changed since record: evidence-pack-project-2026-08-01/02-gap-assessment.json
tree-guard:   newly changed since record: evidence-pack-project-2026-08-01/03-annex-iv-draft.md
tree-guard:   newly changed since record: evidence-pack-project-2026-08-01/04-dependency-report.json
tree-guard:   newly changed since record: evidence-pack-project-2026-08-01/05-audit-trail.json
tree-guard:   newly changed since record: evidence-pack-project-2026-08-01/06-remediation-plan.md
tree-guard:   newly changed since record: evidence-pack-project-2026-08-01/07-risk-decisions.json
tree-guard:   newly changed since record: evidence-pack-project-2026-08-01/README.md
tree-guard:   newly changed since record: evidence-pack-project-2026-08-01/manifest.json
tree-guard:   newly changed since record: evidence-pack-project-2026-08-03/00-summary.md
tree-guard:   newly changed since record: evidence-pack-project-2026-08-03/01-scan-results.json
tree-guard:   newly changed since record: evidence-pack-project-2026-08-03/02-gap-assessment.json
tree-guard:   newly changed since record: evidence-pack-project-2026-08-03/03-annex-iv-draft.md
tree-guard:   newly changed since record: evidence-pack-project-2026-08-03/04-dependency-report.json
tree-guard:   newly changed since record: evidence-pack-project-2026-08-03/05-audit-trail.json
tree-guard:   newly changed since record: evidence-pack-project-2026-08-03/06-remediation-plan.md
tree-guard:   newly changed since record: evidence-pack-project-2026-08-03/07-risk-decisions.json
tree-guard:   newly changed since record: evidence-pack-project-2026-08-03/README.md
tree-guard:   newly changed since record: evidence-pack-project-2026-08-03/manifest.json
tree-guard:   newly changed since record: evidence-pack-project-2026-08-04/00-summary.md
tree-guard:   newly changed since record: evidence-pack-project-2026-08-04/01-scan-results.json
tree-guard:   newly changed since record: evidence-pack-project-2026-08-04/02-gap-assessment.json
tree-guard:   newly changed since record: evidence-pack-project-2026-08-04/03-annex-iv-draft.md
tree-guard:   newly changed since record: evidence-pack-project-2026-08-04/04-dependency-report.json
tree-guard:   newly changed since record: evidence-pack-project-2026-08-04/05-audit-trail.json
tree-guard:   newly changed since record: evidence-pack-project-2026-08-04/06-remediation-plan.md
tree-guard:   newly changed since record: evidence-pack-project-2026-08-04/07-risk-decisions.json
tree-guard:   newly changed since record: evidence-pack-project-2026-08-04/README.md
tree-guard:   newly changed since record: evidence-pack-project-2026-08-04/manifest.json
tree-guard:   newly changed since record: scripts/__pycache__/build_gap_demo.cpython-312.pyc
tree-guard:   newly changed since record: scripts/__pycache__/build_recall_artefact.cpython-312.pyc
tree-guard:   newly changed since record: scripts/__pycache__/commercial_acquire_runtime.cpython-312.pyc
tree-guard:   newly changed since record: scripts/__pycache__/public_surface_inventory.cpython-312.pyc
tree-guard:   content changed again since record: .handover.md
tree-guard:   content changed again since record: .pytest_cache/v/cache/lastfailed
tree-guard:   content changed again since record: .pytest_cache/v/cache/nodeids
tree-guard:   content changed again since record: .ruff_cache/0.15.10/15312485216152109148
tree-guard:   content changed again since record: AI_GOVERNANCE.md
tree-guard:   content changed again since record: MODEL_CARD.md
tree-guard:   content changed again since record: benchmarks/__pycache__/annotation_stats.cpython-312.pyc
tree-guard:   content changed again since record: benchmarks/__pycache__/dedup_check.cpython-312.pyc
tree-guard:   content changed again since record: benchmarks/__pycache__/temporal_split.cpython-312.pyc
tree-guard:   content changed again since record: benchmarks/headtohead/__pycache__/adapters.cpython-312.pyc
tree-guard:   content changed again since record: benchmarks/headtohead/__pycache__/scoring.cpython-312.pyc
tree-guard:   content changed again since record: conformity-evidence-project-2026-07-30/00-assessment-summary.json
tree-guard:   content changed again since record: conformity-evidence-project-2026-07-30/04-technical-documentation-art11/annex-iv-draft.md
tree-guard:   content changed again since record: conformity-evidence-project-2026-07-30/05-record-keeping-art12/audit-trail.json
tree-guard:   content changed again since record: conformity-evidence-project-2026-07-30/08-accuracy-robustness-art15/sbom.json
tree-guard:   content changed again since record: conformity-evidence-project-2026-07-30/09-supply-chain/dependency-report.json
tree-guard:   content changed again since record: conformity-evidence-project-2026-07-30/09-supply-chain/sbom.json
tree-guard:   content changed again since record: conformity-evidence-project-2026-07-30/11-remediation/remediation-plan.md
tree-guard:   content changed again since record: conformity-evidence-project-2026-07-30/manifest.json
tree-guard:   content changed again since record: content/regulations/__pycache__/brazil.cpython-312.pyc
tree-guard:   content changed again since record: content/regulations/__pycache__/colorado.cpython-312.pyc
tree-guard:   content changed again since record: content/regulations/__pycache__/south-africa.cpython-312.pyc
tree-guard:   content changed again since record: content/regulations/__pycache__/south-korea.cpython-312.pyc
tree-guard:   content changed again since record: content/regulations/__pycache__/united-kingdom.cpython-312.pyc
tree-guard:   content changed again since record: evidence-pack-project-2026-07-30/00-summary.md
tree-guard:   content changed again since record: evidence-pack-project-2026-07-30/02-gap-assessment.json
tree-guard:   content changed again since record: evidence-pack-project-2026-07-30/03-annex-iv-draft.md
tree-guard:   content changed again since record: evidence-pack-project-2026-07-30/04-dependency-report.json
tree-guard:   content changed again since record: evidence-pack-project-2026-07-30/05-audit-trail.json
tree-guard:   content changed again since record: evidence-pack-project-2026-07-30/06-remediation-plan.md
tree-guard:   content changed again since record: evidence-pack-project-2026-07-30/07-risk-decisions.json
tree-guard:   content changed again since record: evidence-pack-project-2026-07-30/manifest.json
tree-guard:   content changed again since record: scripts/__pycache__/api_server.cpython-312.pyc
tree-guard:   content changed again since record: scripts/__pycache__/assess.cpython-312.pyc
tree-guard:   content changed again since record: scripts/__pycache__/build_delta_dataset.cpython-312.pyc
tree-guard:   content changed again since record: scripts/__pycache__/cascade_count.cpython-312.pyc
tree-guard:   content changed again since record: scripts/__pycache__/check_decompositions.cpython-312.pyc
tree-guard:   content changed again since record: scripts/__pycache__/claim_auditor.cpython-312.pyc
tree-guard:   content changed again since record: scripts/__pycache__/claim_diff.cpython-312.pyc
tree-guard:   content changed again since record: scripts/__pycache__/classify_risk.cpython-312.pyc
tree-guard:   content changed again since record: scripts/__pycache__/cli.cpython-312.pyc
tree-guard:   content changed again since record: scripts/__pycache__/cli_analysis.cpython-312.pyc
tree-guard:   content changed again since record: scripts/__pycache__/cli_compliance.cpython-312.pyc
tree-guard:   content changed again since record: scripts/__pycache__/cli_scan.cpython-312.pyc
tree-guard:   content changed again since record: scripts/__pycache__/config_validator.cpython-312.pyc
tree-guard:   content changed again since record: scripts/__pycache__/dpv_export.cpython-312.pyc
tree-guard:   content changed again since record: scripts/__pycache__/exec_summary.cpython-312.pyc
tree-guard:   content changed again since record: scripts/__pycache__/explain_articles.cpython-312.pyc
tree-guard:   content changed again since record: scripts/__pycache__/f25_exposure.cpython-312.pyc
tree-guard:   content changed again since record: scripts/__pycache__/feed.cpython-312.pyc
tree-guard:   content changed again since record: scripts/__pycache__/findings_view.cpython-312.pyc
tree-guard:   content changed again since record: scripts/__pycache__/framework_mapper.cpython-312.pyc
tree-guard:   content changed again since record: scripts/__pycache__/gate_probe.cpython-312.pyc
tree-guard:   content changed again since record: scripts/__pycache__/generate_documentation.cpython-312.pyc
tree-guard:   content changed again since record: scripts/__pycache__/mcp_server.cpython-312.pyc
tree-guard:   content changed again since record: scripts/__pycache__/merge_blockers.cpython-312.pyc
tree-guard:   content changed again since record: scripts/__pycache__/pdf_export.cpython-312.pyc
tree-guard:   content changed again since record: scripts/__pycache__/quarantine_liveness.cpython-312.pyc
tree-guard:   content changed again since record: scripts/__pycache__/register.cpython-312.pyc
tree-guard:   content changed again since record: scripts/__pycache__/remediation.cpython-312.pyc
tree-guard:   content changed again since record: scripts/__pycache__/report.cpython-312.pyc
tree-guard:   content changed again since record: scripts/__pycache__/risk_patterns.cpython-312.pyc
tree-guard:   content changed again since record: scripts/__pycache__/site_facts.cpython-312.pyc
tree-guard:   content changed again since record: scripts/__pycache__/telemetry.cpython-312.pyc
tree-guard:   content changed again since record: scripts/__pycache__/timeline.cpython-312.pyc
tree-guard:   content changed again since record: scripts/__pycache__/tree_guard.cpython-312.pyc
tree-guard:   content changed again since record: scripts/__pycache__/update_sitemap.cpython-312.pyc
tree-guard:   content changed again since record: tests/__pycache__/
canonical count (data/site_facts.json): 2,690
manifest surfaces: 11
  all manifest surfaces already carry the canonical value
[exit 0]
```

Ended: `2026-08-05T00:16:58+01:00`

## Current commercial evidence

Started: `2026-08-05T00:17:17+01:00`

Command:

```console
$ bash -lc 'cat docs/commercial/COMMERCIAL_DEFENSIBILITY_REVIEW_2026-07-31.md; printf '"'"'\n===== CLAIM REGISTER =====\n'"'"'; cat docs/commercial/PUBLIC_CLAIM_REGISTER_2026-07-31.md; printf '"'"'\n===== PILOT PACKET =====\n'"'"'; cat docs/commercial/PILOT_PACKET_2026-07-31.md'
# Commercial defensibility review — 2026-07-31

## Erratum — 2026-08-01: public release identity

**CONTRADICTED:** the review below described `regula-ai==1.7.4` as the current
public package. A no-cache PyPI JSON response retrieved 2026-08-01 at
09:16:26 UTC, `pip index versions regula-ai`, the downloaded
`regula_ai-1.9.0-py3-none-any.whl`, and local tag `v1.9.0` all identify 1.9.0
as current. The downloaded wheel SHA-256 is
`01cde674270adcf08acedf1b79e003c6f083c464944cf158582a14afde93cff3` and its
METADATA says `Version: 1.9.0`; tag `v1.9.0` resolves to
`96497430917cfdbe243cd942bb9e0f9448111607`.

The commercial_v1 public-package operational findings remain **VERSION_BOUND**
to the wheel actually tested, 1.7.4. commercial_v1 did not establish the
operational readiness of published 1.9.0. The 1.9.0 wheel still carries the
disputed classification, network, DPA, runtime, and auditor-completeness copy
quoted in the claim register. Frozen corpora, results, hashes, local 1.9.0
Candidate A/B results, and the STOP decision are unchanged.

## Executive decision

`OVERALL_DECISION: STOP`. No evaluated capability justifies a customer pilot.
The frozen local product missed 40/40 constructed Candidate A positives and
40/40 Candidate B positives, while transparent baselines found 40/40 in both.
Candidate C lacks human ground truth. Public claims materially exceed the
measured boundary. A future result can overturn this decision, but present
evidence cannot.

## Verdict fields

| Field | Verdict |
|---|---|
| TECHNICAL_EVIDENCE | **FAILED** |
| COMPARATIVE_ADVANTAGE | **NOT_DEMONSTRATED** |
| PUBLIC_CLAIM_INTEGRITY | **FAIL** |
| REGULATORY_CURRENCY | **PARTIAL** |
| OPERATIONAL_READINESS | **FAIL** |
| DEMAND_EVIDENCE | **UNVALIDATED** |
| OVERALL_DECISION | **STOP** |

These are internal decision labels, not legal or scientific standards.

## Scope and frozen identities

MEASURED against local product commit
`94efa9e6ad9173fb888822543c247195078b0220`, Regula 1.9.0, Python 3.12.3,
Linux 6.6.87.2-microsoft-standard-WSL2. Preregistration commit: `5bd2112`.
Protocol SHA-256:
`58c935903b5832eb7b8232116f6dc182b97708a89b5d3070f8b856ec9272d8c4`.
Public package: `regula-ai==1.7.4`, wheel SHA-256
`36e4a6b3b91dd2989a9163310fed1e35559e6fc0697c93a6bd042e6514ab3940`.
Local wheel: 1.9.0, SHA-256
`1282b69e64c863989346fbaf9e5c8c72fdcf5a0357f6e3b75b3bad8c02a36cd6`.

The 12 exact repository commits and acquisition hashes are in
`manifest.json` and the retained external `acquisition.json`. They comprise
microsoft/markitdown, open-webui/open-webui, browser-use/browser-use,
modelcontextprotocol/python-sdk, pallets/click, pallets/itsdangerous,
python-attrs/attrs, astral-sh/ruff, prettier/prettier, axios/axios,
sindresorhus/ky and vitest-dev/vitest. This is a purposive convenience frame,
not a representative sample.

## Deviations and integrity

Before results, `84e0118` fixed the verifier's conflation of the mutable
protocol tree with the detached product tree. After the frozen acquisition
failed on `sindresorhus/ky`'s lowercase root `license`, the before-fix exit 1
was retained and `056bcf2` added a class-wide case-insensitive runtime
acquirer outside the frozen input set. Frozen product rules, corpus, labels,
thresholds and `acquire.py` were not changed. The corrected acquisition found
12/12 repositories and 12/12 licence records.

## Results

The unit is one constructed observable decision. Labels are truth by
construction, not human judgements. Forty positives and forty negatives were
run per candidate and tool, twice from fresh output directories. Results were
identical after normalisation. Transformation families are correlated, so the
Wilson intervals below are descriptive and cannot establish external
accuracy.

| Tool/job | TP | FP | FN | TN | Precision (95% Wilson) | Recall (95% Wilson) |
|---|---:|---:|---:|---:|---|---|
| local 1.9.0 / A | 0 | 0 | 40 | 40 | undefined, 0/0 | 0/40 = 0.000 (0.000–0.0876) |
| naive imports / A | 40 | 4 | 0 | 36 | 40/44 = 0.909 (0.788–0.964) | 40/40 = 1.000 (0.912–1.000) |
| local 1.9.0 / B | 0 | 0 | 40 | 40 | undefined, 0/0 | 0/40 = 0.000 (0.000–0.0876) |
| naive markup / B | 40 | 0 | 0 | 40 | 40/40 = 1.000 (0.912–1.000) | 40/40 = 1.000 (0.912–1.000) |

Exact reproduction:

```bash
python3 benchmarks/commercial_v1/run.py --manifest benchmarks/commercial_v1/manifest.json --corpus benchmarks/commercial_v1/corpus.json --output OUT --tool naive
python3 benchmarks/commercial_v1/run.py --manifest benchmarks/commercial_v1/manifest.json --corpus benchmarks/commercial_v1/corpus.json --output OUT --tool local_head --executable python3
python3 benchmarks/commercial_v1/normalise.py --input OUT/results.json --output OUT/normalised.json
python3 benchmarks/commercial_v1/score.py --labels benchmarks/commercial_v1/labels.json --output SCORE --result OUT1/results.json --result OUT2/results.json --result OUT3/results.json --result OUT4/results.json
```

Raw-output root: `/tmp/regula-commercial-20260731.Inq4k2`; the score and
repository-operation records needed for the stated fractions are committed in
`benchmarks/commercial_v1/results/raw/`, with the compact result at
`benchmarks/commercial_v1/results/summary.json`. The full score output SHA-256 is
`bd8191a1ec9f19bfc408fc770fd40409da091b6a218308ae0014200a6df20a3e`.

Repository operational execution retained 12/12 outcomes per tool. Local
1.9.0 and public 1.7.4 each returned exit 0 for 9/12 and exit 1 for 3/12
(open-webui, python-sdk and prettier). Their second runs repeated every exit,
stdout hash and stderr hash for 12/12; wall time differed. compliance-agent
0.5.0 default and configured modes and AIR Blackbox 1.13.2 returned exit 0 for
12/12. This proves reachability only: no equivalent source-event adapter or
independent repository labels exist, so competitor accuracy is UNTESTABLE.
Complior's executable identity remained unresolved and was not replaced.

The documented journey on one active `openai` import/use fixture and one
negative arithmetic fixture returned empty data for both local and public
versions: observed positive findings 0/1 and negative false alerts 0/1.
Unicode/space paths exited 0 for both. Local 1.9.0 generated a nine-file
manifest and strict verification exited 0. Public 1.7.4 generated a legacy
manifest, non-strict verification exited 0, and strict verification exited 2
because the manifest did not declare `format=regula.evidence.v1`.

Network behaviour is UNVERIFIED. `unshare -n` failed with “Operation not
permitted”. The frozen Python socket-denial control replaced `socket.socket`
too early and caused `ssl` import to fail, so it did not execute the scanner.
Source inspection and ordinary offline success do not prove zero calls. Peak
memory is NOT_MEASURED because the available value is cumulative child RSS.

## Failure classes

After execution, the 80 local synthetic false negatives were classified as a
source-event adapter/product-output mismatch: the default `check` path emitted
no source-linked findings satisfying the frozen buyer-job definition. The
active OpenAI control reproduced the absence outside generated cases. Three
repository non-zero exits per Regula version are operational failures retained
in raw stderr. Candidate C is non-observable without declared context and
independent human annotation, not a measured classifier failure.

## Legal and regulatory boundary

PRIMARY-SOURCE VERIFIED on 2026-07-31: Regulation (EU) 2026/1744 entered into
force on 27 July 2026. Its transition moves relevant Annex III rules to
2 December 2027 and Annex I product-system rules to 2 August 2028; the legacy
Article 50(2) transition is 2 December 2026. Article 6 depends on intended
purpose and context. Article 50 source-code absence is not proof of violation.
Exact official sources and limitations are in the research register.

prEN 18228, prEN 18229-1 and prEN 18282 were observed in draft/enquiry stages;
EN 18286 was at formal vote in reviewed material. ISO/IEC 42005 and 42006 are
published international standards, but that does not create Article 40
presumption of conformity. No exact Official Journal citation for these
standards was established; any harmonisation claim remains UNVERIFIED.

## Commercial interpretation

The strongest proposed wedge was local AI inventory plus reproducible
evidence. Its strongest supporting fact is that 1.9.0 can generate and
strictly verify a local evidence manifest. The stronger contrary evidence is
that the same journey put zero observed findings into the pack and missed
40/40 constructed inventory positives; a small transparent import baseline
found 40/40. Evidence packaging without reliable evidence discovery is not a
defensible capability.

Demand is UNVALIDATED: no interviews, representative customer repositories,
design-partner commitments or payments were produced. Competitor availability
and regulatory workload are problem signals at most, not willingness to pay.
The maintenance burden includes regulatory currency, multilingual claims,
package/release divergence, comparator evolution and evidence-format support.

Economic reasoning is assumption-bound. At any price, a pilot that requires a
consultant to reconstruct missed inventory manually has negative product
leverage unless the tool saves more review time than it creates. No measured
customer time or cost exists, so no market price or ROI is claimed.

The decision would be falsified by a prospectively sampled, independently labelled
repository study in which a frozen Regula version clears the preregistered
lower bounds, beats the transparent baseline without a material regression,
reproduces its evidence packs, and has corrected public claims. The next
bounded unit is not a feature build: correct high-consequence public and PyPI
claims, publish no new accuracy claim, and design an owner-approved independent
annotation study before reconsidering a pilot.

## Successor prompt

> Work only on the bounded claim-integrity unit derived from commercial_v1.
> Recompute state; read the ledger and 2026-07-31 commercial review. Correct
> every active high-consequence README, TRUST, SECURITY, package-description
> and translated-site claim identified in the public claim register. Preserve
> the distinction between code-observable evidence and legal determination;
> remove zero-network, universal reproducibility and unqualified
> classification claims unless new mechanical evidence supports them. Do not
> change detector rules, benchmark labels or commercial_v1 results. Add
> exact-surface tests, run all repository gates, update the ledger, and stop
> before push, publication or deployment.

## Final adversarial review

An independent read-only reviewer received only the complete diff, protocol,
raw summary, test output, claim register and ledger. The reviewer found one
HIGH, two MEDIUM and two LOW defects. Reproduction confirmed all five. The
HIGH correction removes an invalid inference from A/B misses to the separate
legal-classification claim. One MEDIUM is closed by committing the raw score
and repository records and adding a summary-to-raw regression check. The other
MEDIUM remains a limitation: `gate.py` evaluates a supplied external-evidence
record and its conjunction test cannot prove those booleans were derived from
raw artefacts. No claim-ready verdict relies on that path here; both candidates
fail their measured recall gate. The LOW fixes rename hash equality accurately
and classify the observed >30-second runs as contradiction of the unqualified
bound. The open-alert wording now distinguishes alerts from confirmed
vulnerabilities. No arithmetic error, silent ledger closure, suppressed failed
run or hidden human-label substitution was found.

## Final verification state

MEASURED on the quiescent working tree after review disposition. The custom
runner exited 0: `1386 passed, 0 failed, 0 skipped (1071 test functions)`.
Full pytest exited 1 after 2,011.63 seconds: `6 failed, 2633 passed`; all six
failures independently report the same count-integrity condition, live
collection 2,639 versus public canonical 2,628. The session contract forbids
editing public website claims, so `site_facts.py` and
`cascade_count.py --apply` were not used to make those surfaces green. An
attempt to consolidate the 11 new checks into an existing test was fully
reverted because it would conceal the denominator change.

Fast gates: `site_integrity`, `build_recall_artefact --check`,
`build_gap_demo --check` and `check_selfref_sourcing --control-only` exited 0.
`claim_auditor --verify-facts` and `cascade_count --check` exited 1 on the same
2,628/2,639 count mismatch. The separately required merge blocker remained
exit 1. Commercial integrity exited 0 with 20 repository inputs verified.
Self-test exited 0 (6/6). Restricted doctor exited 1 solely because the sandbox
made `/home/mkuziva/.regula/audit` unwritable; the exact unrestricted control
exited 0 with 8 passed and 4 info. These are separate environment-specific
results, not one green run.

Because required gates are red, the results commit is evidence-complete but
not release-ready. Resolving the count mismatch requires an owner-authorised
public-claim cascade or a separately justified removal of tests; neither is
within this session's permitted scope.

===== CLAIM REGISTER =====
# Public claim register — 2026-07-31

## Erratum — 2026-08-01: published package

The register's references to PyPI 1.7.4 as the current release are
**CONTRADICTED**. Primary package-registry evidence retrieved 2026-08-01 and
downloaded wheel metadata identify `regula-ai==1.9.0` as current; wheel
SHA-256 `01cde674270adcf08acedf1b79e003c6f083c464944cf158582a14afde93cff3`.
The 1.7.4 findings remain VERSION_BOUND to 1.7.4, while 1.9.0 operational
readiness is UNTESTED by commercial_v1. The published 1.9.0 METADATA contains
the same disputed high-consequence claim classes. Frozen benchmark data and
the local 1.9.0 Candidate A/B results are not altered by this correction.

This register is version-aware. The sentence originally recorded that no public
wording was edited in the 2026-07-31 benchmark session; the separate 2026-08-01
claim-correction session did edit local public-source wording but did not release
or deploy it.

| Exact claim | Active surfaces/version | Disposition and evidence | Exact proposed replacement | Consequence |
|---|---|---|---|---|
| “classifies your system into one of the Act's four risk tiers, and tells you which obligations apply” | README and PyPI 1.7.4 description; related site copy | **LEGAL_REVIEW_REQUIRED and UNTESTED.** Article 6 requires intended purpose/context. Candidate C, the only commercial_v1 job addressing contextual high-risk review, has no independent human labels and was not executed as an accuracy study. Candidate A/B misses do not test this claim. | “Reports code-observable risk indicators and links them to provisions for human review; it does not determine legal classification or which obligations apply.” | release- and pilot-blocking |
| “No external dependencies, no API calls, no data leaves your machine” and “zero network calls during scanning — no DPA required” | README/PyPI 1.7.4; TRUST | **UNTESTABLE and legally overbroad.** Namespace denial unavailable; socket probe invalid. Optional extras exist in wheel metadata. A tool cannot decide whether a DPA is required. | “The stdlib core is designed to scan local files. Network behaviour has not yet been mechanically verified across every command and environment. Optional features add dependencies and may use network services.” | release- and pilot-blocking |
| “Auditor-ready evidence package” | README, CLI help, guides | **VERSION_BOUND / CONTRADICTED in broad form.** Local 1.9.0 strict verification passed, but the tested pack contained 0 observed scan findings; public 1.7.4 strict verification failed. | “Hash-manifested evidence scaffold for reviewer completion; output completeness and legal sufficiency require independent review. Strict v1 verification is available in 1.9.0.” | pilot-blocking |
| “Every metric is CI-enforced and generated from source … independently verified” | README consultant paragraph | **CONTRADICTED.** Merge blocker exits 1; N43 records timing disclaimer gaps; public release counts are stale. | “Selected generated facts have repository checks. Review the versioned evidence register and known failing gates before relying on a number.” | release-blocking |
| “under 30 seconds” / “30 seconds” | README and TRUST | **CONTRADICTED as an unqualified universal bound.** The frozen local `ruff` repository runs took 68.885 and 122.778 seconds; three Regula repository runs also returned non-zero. No frozen hardware, repository-size or command boundary accompanies the public wording. | “Runtime depends on repository size, language mix and environment; no universal runtime bound is claimed.” | material |
| “0 known security findings” | TRUST | **CONTRADICTED as an inventory statement, not proof of vulnerabilities.** SECURITY discloses 42 open high-severity CodeQL alerts, says they are triaged and explains why many are believed false positives. An alert is not automatically a confirmed vulnerability, but the zero wording hides the disclosed open-alert inventory. | “See SECURITY.md for the current, versioned open-alert inventory and disposition; open alerts are not equivalent to confirmed vulnerabilities.” | release-blocking |
| “100% recall” residue and derived precision/recall claims | TRUST, benchmark/history surfaces | **STALE / VERSION_BOUND.** Historical fixture results do not establish current buyer-job performance; commercial_v1 local recall was 0/40 for A and 0/40 for B. | “Historical fixture result; not a current external accuracy estimate. commercial_v1 results are reported separately with corpus, fractions and intervals.” | pilot-blocking |
| current test, pattern and command counts (including a stale PyPI passing-count badge) | README, badges, PyPI 1.7.4, site/generated facts | **STALE / VERSION_BOUND.** Initial HEAD collected 2,628 pytest cases; the custom runner reported 1,060 functions and 1,386 cases. Counts changed again with this harness. | “Version-specific counts only, generated from the named release artefact and command; do not reuse local-HEAD counts for 1.7.4.” | material |
| “independently verifiable” evidence signing/timestamping | TRUST and evidence guide | **VERSION_BOUND.** Local unsigned hash-manifest strict verification passed; no signed or timestamped commercial_v1 pack was tested. | “Unsigned manifest integrity was reproduced for 1.9.0. Signature identity and timestamp trust require the documented keys, dependencies and trust-anchor checks and were not tested here.” | material |
| draft standards are “published” or provide harmonised-standard presumption | standards/blog surfaces | **CONTRADICTED / UNVERIFIED.** Draft/enquiry/formal-vote stages are not OJ citation; no OJ citation was established. | “Draft or voting-stage work item; no Article 40 presumption of conformity is claimed unless and until the exact standard is cited in the Official Journal.” | release-blocking |
| Article 50 and high-risk application dates stated without 2026/1744 transition | README/docs/site/blog and translations where present | **STALE where old dates remain.** PRIMARY-SOURCE VERIFIED transition dates are in the research register. | “Dates reflect Regulation (EU) 2026/1744: identify the exact provision and transition; include the Digital Omnibus caveat and retrieval date.” | release-blocking |

“Not found in reviewed official material” never means a competitor feature or
standard does not exist. Main, local HEAD, PyPI 1.7.4, current README, TRUST,
SECURITY, MODEL_CARD, site source, regional pages, translated pages, generated
facts, badges, CLI help and wheel metadata were in scope. Exact exhaustive
line-by-line disposition remains a successor claim-correction unit; this
register identifies every high-consequence class found in the bounded session.

===== PILOT PACKET =====
# Pilot packet — evidence-validation only

## Status and boundary

Regula is **not approved for a customer product pilot** by commercial_v1. This
packet is immediately usable only for a no-claim discovery and independent
validation engagement. It must not be sold as compliance certification,
autonomous high-risk classification, legal advice or demonstrated accuracy.

## Provisional customer and job

Provisional ICP: an EU AI-governance consultancy or regulated-software
engineering team able to provide a representative, non-sensitive repository
and independent reviewers. User: software assurance engineer or consultant.
Buyer: governance lead, engineering director or consulting partner. Job:
produce a reviewable inventory/evidence scaffold while preserving exact source
provenance and explicit uncertainty. Present workaround: dependency manifests,
repository search, questionnaires and manually assembled evidence folders.

Measurable problem hypothesis: qualified reviewers spend material time finding
AI dependencies and assembling provenance, and an accurate local tool could
reduce elapsed review time without increasing missed items or false-alert
burden. This is UNVALIDATED.

## Proposed validation scope

- 30 or more prospectively sampled buyer-relevant repositories, sized by a
  recorded power analysis; no proprietary code enters the public repository.
- Two independent human raters, blinded tool outputs, adjudication and raw
  disagreements.
- Frozen Regula, transparent baseline and source-event schema.
- Deliverables: annotation guide, hashed manifest, raw outputs, adjudicated
  labels, per-repository metrics, uncertainty, failure classes and go/stop memo.
- Exclusions: legal certification, autonomous Article 6 decisions, production
  deployment, personal data, paid APIs, detector tuning after holdout results,
  and any public performance claim before review.

Customer evidence required: repository access under an agreed data boundary,
dependency/build manifests, intended-purpose statement, deployment context,
known AI integrations and two qualified raters. Customer effort assumption:
two raters plus an adjudicator, repository owner support and a security review
of local execution. This effort has not been measured.

## Acceptance and failure criteria

Technical acceptance reuses the frozen Candidate A gate: precision and recall
Wilson 95% lower bounds each at least 0.90, identical normalised clean reruns,
complete manifest accounting, verified evidence manifests, no concealed weak
stratum, and meaningful advantage over the transparent baseline. Commercial
success additionally requires at least three qualified organisations to
confirm the same costly workflow, two to provide representative data, and one
signed paid validation. Failure occurs on any accuracy gate miss, irreducible
legal ambiguity presented as fact, manual review burden no better than the
baseline, data-boundary rejection, or absence of willingness evidence.

## Five falsifiable demand hypotheses

1. At least 3/5 qualified interviewees report the inventory/provenance task at
   least monthly and can quantify its current time cost.
2. At least 2/5 will provide a representative repository and independent
   raters under the stated boundary.
3. At least 3/5 prefer local, inspectable evidence over a cloud-only workflow.
4. At least 2/5 say a manifest-verifiable scaffold changes a procurement or
   assurance decision, not merely presentation quality.
5. At least 1/5 signs a paid validation after seeing the measured limitations.

## Neutral interview guide and disqualifiers

Ask: “Walk me through the last repository-level AI inventory or evidence
review.” “What triggered it?” “What artefacts did you trust?” “Where were
errors found?” “How much reviewer time was used?” “What happens if an item is
missed?” “Which data may leave your environment?” “What would make a local
tool unusable?” “Who approves budget?” “What evidence would justify a trial?”

Disqualify evidence from respondents without the workflow, hypothetical-only
answers, vendor partners unable to criticise the product, data that cannot be
lawfully used, or engagements demanding autonomous legal certification.

## Offers and pricing tests

Design-partner offer: customer supplies representative repositories and
raters; owner supplies a frozen, local, transparent validation and returns all
raw evidence; no performance promise. Paid-validation offer: fixed-scope
independent benchmark and evidence pack with an explicit stop conclusion
allowed.

Pricing anchors are tests, not market prices: £1,500 for one repository and a
methods memo (assumes one review day); £5,000 for up to five repositories and
adjudicated findings (assumes four delivery days); £15,000 for an organisation
validation pack with governance workshop (assumes ten days). Reject the anchor
if delivery time, buyer value or procurement evidence contradicts its
assumption.

Kill the effort if no qualified organisation supplies data after ten
interviews, no paid validation follows two completed design-partner studies,
the transparent baseline remains non-inferior, or regulatory maintenance cost
exceeds measured recurring revenue.

## Future evidence table

| Date | Organisation/role | Qualified? | Last real workflow | Time/cost evidence | Repository offered? | Boundary accepted? | Commitment | Price reaction | Disconfirming evidence | Follow-up |
|---|---|---|---|---|---|---|---|---|---|---|
| | | | | | | | | | | |
[exit 0]
```

Ended: `2026-08-05T00:17:17+01:00`

## Contributor, licence and governance documents

Started: `2026-08-05T00:17:17+01:00`

Command:

```console
$ bash -lc 'cat CONTRIBUTING.md; printf '"'"'\n===== LICENSE =====\n'"'"'; cat LICENSE.txt; printf '"'"'\n===== EUPL =====\n'"'"'; cat LICENSE.EUPL; printf '"'"'\n===== DRL =====\n'"'"'; cat docs/LICENSE.Detection.Rules.md; printf '"'"'\n===== NOTICE =====\n'"'"'; cat NOTICE; find . -maxdepth 3 -type f \( -iname '"'"'*governance*'"'"' -o -iname '"'"'*code*conduct*'"'"' \) -print'
# Contributing to Regula

Thanks for your interest in improving EU AI Act compliance tooling. This guide covers everything you need to get started.

## Quick Start

```bash
# Clone your fork
git clone https://github.com/<your-username>/getregula.git
cd getregula

# No install needed for core — it's pure Python 3.10+
regula --help

# Optional dependencies (for YAML config and AST analysis)
pip install pyyaml tree-sitter

# Run the test suite
pytest tests/ -q
# Must output: "X passed"
```

## Import convention (important)

Every file in `scripts/` uses **bare imports** — `from errors import RegulaError`, NOT `from scripts.errors import RegulaError` or `from .errors import RegulaError`. This works because every `scripts/*.py` file has `sys.path.insert(0, str(Path(__file__).parent))` near the top. Do NOT remove these lines or switch to relative imports.

## Project Structure

```
scripts/
├── cli.py                 # CLI entry point and argument parsing
├── classify_risk.py       # Risk classification engine
├── report.py              # Code scanner and reporting
├── risk_patterns.py       # Pattern definitions for risk detection
├── risk_types.py          # Risk category types and constants
├── framework_mapper.py    # Crosswalk mappings (NIST, ISO, etc.)
├── ast_engine.py          # AST-based analysis (tree-sitter)
├── compliance_check.py    # Compliance checking logic
├── remediation.py         # Fix suggestions
└── ...                    # See scripts/ for full list
tests/
├── test_classification.py     # Core classification tests (custom runner)
└── ...                        # 56 test files — see tests/ for full list
```

## How to Add a Risk Pattern

Risk patterns live in `scripts/risk_patterns.py`. Each pattern is a regex or keyword set that maps to a risk category.

1. Open `scripts/risk_patterns.py` and find the relevant pattern group.
2. Add your pattern following the existing format.
3. Write a failing test first (see Testing below).
4. Run tests to confirm it passes.

Example: if you want to flag a new biometric library:

```python
# In risk_patterns.py, add to the relevant pattern list
"new_biometric_lib",
```

## How to Add a Framework Mapping

Framework mappings live in `scripts/framework_mapper.py`. These map EU AI Act articles to controls in other frameworks (NIST AI RMF, ISO 42001, etc.).

1. Open `scripts/framework_mapper.py`.
2. Find or create the mapping dictionary for your target framework.
3. Add entries linking AI Act articles to the corresponding controls.
4. Write a test to verify the mapping resolves correctly.

## How to Add Language Support

Regula scans source code for AI-related patterns. To add support for a new programming language:

1. Add file extension handling in `scripts/report.py` (the scanner).
2. Add any language-specific patterns to `scripts/risk_patterns.py`.
3. If using AST analysis, add a tree-sitter grammar in `scripts/ast_engine.py`.
4. Write tests with sample code in the new language.

## Testing

Tests are spread across 58 files in `tests/`. The main classification tests live in `tests/test_classification.py` (a custom runner with 437 test functions); the rest are pytest-native. Run the full verification before any PR:

The test pattern is:

1. Define a test function that exercises the behaviour you want to verify.
2. Add it to the appropriate test file (or `test_classification.py` for classification logic).
3. Run with `pytest tests/ -q`.

```python
def test_my_new_pattern():
    """Verify that XYZ pattern is classified as high risk."""
    result = classify_something(...)
    assert result.risk_level == "high", f"Expected high, got {result.risk_level}"

# Add to the tests list:
tests = [
    # ... existing tests ...
    test_my_new_pattern,
]
```

**Write failing tests first.** This is not optional. The workflow is:

1. Write a test that demonstrates the expected behaviour.
2. Run it — confirm it fails.
3. Implement the change.
4. Run it again — confirm it passes.
5. Run the full suite — confirm no regressions.

## Making a Pull Request

### Workflow

1. Fork the repository.
2. Create a feature branch: `git checkout -b my-feature`.
3. Write a failing test for your change.
4. Implement the change.
5. Run `pytest tests/ -q` — all tests must pass.
6. Commit with a clear message: `feat: add detection for XYZ library`.
7. Push and open a PR against `main`.

### PR Checklist

Before submitting, verify:

- [ ] Full verify passes: `python3 tests/test_classification.py && python3 -m pytest tests/ -q && python3 -m scripts.cli self-test && python3 -m scripts.cli doctor`
- [ ] New behaviour has at least one test
- [ ] No new external dependencies added to core (discuss first if needed)
- [ ] Commit messages follow conventional format (`feat:`, `fix:`, `docs:`, etc.)
- [ ] User-facing copy uses British English
- [ ] No secrets, API keys, or credentials in the diff
- [ ] PR description explains *why*, not just *what*

### Commit Message Format

```
type: short description

Longer explanation if needed.
```

Types: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`

## Code Style

- Follow existing patterns in the codebase. Consistency matters more than any style guide.
- Python 3.10+ features are fine (match statements, union types with `|`, etc.).
- No type stubs needed — the codebase doesn't use them.
- British English in all user-facing strings and documentation.
- Keep functions focused. If a function does two things, split it.

## Reporting Issues

- **Bugs**: Use the bug report template.
- **Pattern requests**: Use the pattern request form.
- **False positives**: Use the false positive template — these are particularly valuable for improving accuracy.

## Code of Conduct

- Be respectful and constructive.
- Assume good intent.
- Be inclusive — this tool serves a global community.
- Focus on the work, not the person.
- If something is unclear, ask rather than assume.

That's it. No lengthy governance documents. If you're unsure about anything, open an issue and ask.

===== LICENSE =====

                                 Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

   TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

   1. Definitions.

      "License" shall mean the terms and conditions for use, reproduction,
      and distribution as defined by Sections 1 through 9 of this document.

      "Licensor" shall mean the copyright owner or entity authorized by
      the copyright owner that is granting the License.

      "Legal Entity" shall mean the union of the acting entity and all
      other entities that control, are controlled by, or are under common
      control with that entity. For the purposes of this definition,
      "control" means (i) the power, direct or indirect, to cause the
      direction or management of such entity, whether by contract or
      otherwise, or (ii) ownership of fifty percent (50%) or more of the
      outstanding shares, or (iii) beneficial ownership of such entity.

      "You" (or "Your") shall mean an individual or Legal Entity
      exercising permissions granted by this License.

      "Source" form shall mean the preferred form for making modifications,
      including but not limited to software source code, documentation
      source, and configuration files.

      "Object" form shall mean any form resulting from mechanical
      transformation or translation of a Source form, including but
      not limited to compiled object code, generated documentation,
      and conversions to other media types.

      "Work" shall mean the work of authorship, whether in Source or
      Object form, made available under the License, as indicated by a
      copyright notice that is included in or attached to the work
      (an example is provided in the Appendix below).

      "Derivative Works" shall mean any work, whether in Source or Object
      form, that is based on (or derived from) the Work and for which the
      editorial revisions, annotations, elaborations, or other modifications
      represent, as a whole, an original work of authorship. For the purposes
      of this License, Derivative Works shall not include works that remain
      separable from, or merely link (or bind by name) to the interfaces of,
      the Work and Derivative Works thereof.

      "Contribution" shall mean any work of authorship, including
      the original version of the Work and any modifications or additions
      to that Work or Derivative Works thereof, that is intentionally
      submitted to the Licensor for inclusion in the Work by the copyright owner
      or by an individual or Legal Entity authorized to submit on behalf of
      the copyright owner. For the purposes of this definition, "submitted"
      means any form of electronic, verbal, or written communication sent
      to the Licensor or its representatives, including but not limited to
      communication on electronic mailing lists, source code control systems,
      and issue tracking systems that are managed by, or on behalf of, the
      Licensor for the purpose of discussing and improving the Work, but
      excluding communication that is conspicuously marked or otherwise
      designated in writing by the copyright owner as "Not a Contribution."

      "Contributor" shall mean Licensor and any individual or Legal Entity
      on behalf of whom a Contribution has been received by the Licensor and
      subsequently incorporated within the Work.

   2. Grant of Copyright License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      copyright license to reproduce, prepare Derivative Works of,
      publicly display, publicly perform, sublicense, and distribute the
      Work and such Derivative Works in Source or Object form.

   3. Grant of Patent License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      (except as stated in this section) patent license to make, have made,
      use, offer to sell, sell, import, and otherwise transfer the Work,
      where such license applies only to those patent claims licensable
      by such Contributor that are necessarily infringed by their
      Contribution(s) alone or by combination of their Contribution(s)
      with the Work to which such Contribution(s) was submitted. If You
      institute patent litigation against any entity (including a
      cross-claim or counterclaim in a lawsuit) alleging that the Work
      or a Contribution incorporated within the Work constitutes direct
      or contributory patent infringement, then any patent licenses
      granted to You under this License for that Work shall terminate
      as of the date such litigation is filed.

   4. Redistribution. You may reproduce and distribute copies of the
      Work or Derivative Works thereof in any medium, with or without
      modifications, and in Source or Object form, provided that You
      meet the following conditions:

      (a) You must give any other recipients of the Work or
          Derivative Works a copy of this License; and

      (b) You must cause any modified files to carry prominent notices
          stating that You changed the files; and

      (c) You must retain, in the Source form of any Derivative Works
          that You distribute, all copyright, patent, trademark, and
          attribution notices from the Source form of the Work,
          excluding those notices that do not pertain to any part of
          the Derivative Works; and

      (d) If the Work includes a "NOTICE" text file as part of its
          distribution, then any Derivative Works that You distribute must
          include a readable copy of the attribution notices contained
          within such NOTICE file, excluding any notices that do not
          pertain to any part of the Derivative Works, in at least one
          of the following places: within a NOTICE text file distributed
          as part of the Derivative Works; within the Source form or
          documentation, if provided along with the Derivative Works; or,
          within a display generated by the Derivative Works, if and
          wherever such third-party notices normally appear. The contents
          of the NOTICE file are for informational purposes only and
          do not modify the License. You may add Your own attribution
          notices within Derivative Works that You distribute, alongside
          or as an addendum to the NOTICE text from the Work, provided
          that such additional attribution notices cannot be construed
          as modifying the License.

      You may add Your own copyright statement to Your modifications and
      may provide additional or different license terms and conditions
      for use, reproduction, or distribution of Your modifications, or
      for any such Derivative Works as a whole, provided Your use,
      reproduction, and distribution of the Work otherwise complies with
      the conditions stated in this License.

   5. Submission of Contributions. Unless You explicitly state otherwise,
      any Contribution intentionally submitted for inclusion in the Work
      by You to the Licensor shall be under the terms and conditions of
      this License, without any additional terms or conditions.
      Notwithstanding the above, nothing herein shall supersede or modify
      the terms of any separate license agreement you may have executed
      with Licensor regarding such Contributions.

   6. Trademarks. This License does not grant permission to use the trade
      names, trademarks, service marks, or product names of the Licensor,
      except as required for reasonable and customary use in describing the
      origin of the Work and reproducing the content of the NOTICE file.

   7. Disclaimer of Warranty. Unless required by applicable law or
      agreed to in writing, Licensor provides the Work (and each
      Contributor provides its Contributions) on an "AS IS" BASIS,
      WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
      implied, including, without limitation, any warranties or conditions
      of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
      PARTICULAR PURPOSE. You are solely responsible for determining the
      appropriateness of using or redistributing the Work and assume any
      risks associated with Your exercise of permissions under this License.

   8. Limitation of Liability. In no event and under no legal theory,
      whether in tort (including negligence), contract, or otherwise,
      unless required by applicable law (such as deliberate and grossly
      negligent acts) or agreed to in writing, shall any Contributor be
      liable to You for damages, including any direct, indirect, special,
      incidental, or consequential damages of any character arising as a
      result of this License or out of the use or inability to use the
      Work (including but not limited to damages for loss of goodwill,
      work stoppage, computer failure or malfunction, or any and all
      other commercial damages or losses), even if such Contributor
      has been advised of the possibility of such damages.

   9. Accepting Warranty or Additional Liability. While redistributing
      the Work or Derivative Works thereof, You may choose to offer,
      and charge a fee for, acceptance of support, warranty, indemnity,
      or other liability obligations and/or rights consistent with this
      License. However, in accepting such obligations, You may act only
      on Your own behalf and on Your sole responsibility, not on behalf
      of any other Contributor, and only if You agree to indemnify,
      defend, and hold each Contributor harmless for any liability
      incurred by, or claims asserted against, such Contributor by reason
      of your accepting any such warranty or additional liability.

   END OF TERMS AND CONDITIONS

   APPENDIX: How to apply the Apache License to your work.

      To apply the Apache License to your work, attach the following
      boilerplate notice, with the fields enclosed by brackets "[]"
      replaced with your own identifying information. (Don't include
      the brackets!)  The text should be enclosed in the appropriate
      comment syntax for the file format. Please also get an in-the-know
      person to verify that the account information is correct.

   Copyright 2026 The Implementation Layer

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

===== EUPL =====
                      EUROPEAN UNION PUBLIC LICENCE v. 1.2
                      EUPL © the European Union 2007, 2016

This European Union Public Licence (the ‘EUPL’) applies to the Work (as defined
below) which is provided under the terms of this Licence. Any use of the Work,
other than as authorised under this Licence is prohibited (to the extent such
use is covered by a right of the copyright holder of the Work).

The Work is provided under the terms of this Licence when the Licensor (as
defined below) has placed the following notice immediately following the
copyright notice for the Work:

        Licensed under the EUPL

or has expressed by any other means his willingness to license under the EUPL.

1. Definitions

In this Licence, the following terms have the following meaning:

- ‘The Licence’: this Licence.

- ‘The Original Work’: the work or software distributed or communicated by the
  Licensor under this Licence, available as Source Code and also as Executable
  Code as the case may be.

- ‘Derivative Works’: the works or software that could be created by the
  Licensee, based upon the Original Work or modifications thereof. This Licence
  does not define the extent of modification or dependence on the Original Work
  required in order to classify a work as a Derivative Work; this extent is
  determined by copyright law applicable in the country mentioned in Article 15.

- ‘The Work’: the Original Work or its Derivative Works.

- ‘The Source Code’: the human-readable form of the Work which is the most
  convenient for people to study and modify.

- ‘The Executable Code’: any code which has generally been compiled and which is
  meant to be interpreted by a computer as a program.

- ‘The Licensor’: the natural or legal person that distributes or communicates
  the Work under the Licence.

- ‘Contributor(s)’: any natural or legal person who modifies the Work under the
  Licence, or otherwise contributes to the creation of a Derivative Work.

- ‘The Licensee’ or ‘You’: any natural or legal person who makes any usage of
  the Work under the terms of the Licence.

- ‘Distribution’ or ‘Communication’: any act of selling, giving, lending,
  renting, distributing, communicating, transmitting, or otherwise making
  available, online or offline, copies of the Work or providing access to its
  essential functionalities at the disposal of any other natural or legal
  person.

2. Scope of the rights granted by the Licence

The Licensor hereby grants You a worldwide, royalty-free, non-exclusive,
sublicensable licence to do the following, for the duration of copyright vested
in the Original Work:

- use the Work in any circumstance and for all usage,
- reproduce the Work,
- modify the Work, and make Derivative Works based upon the Work,
- communicate to the public, including the right to make available or display
  the Work or copies thereof to the public and perform publicly, as the case may
  be, the Work,
- distribute the Work or copies thereof,
- lend and rent the Work or copies thereof,
- sublicense rights in the Work or copies thereof.

Those rights can be exercised on any media, supports and formats, whether now
known or later invented, as far as the applicable law permits so.

In the countries where moral rights apply, the Licensor waives his right to
exercise his moral right to the extent allowed by law in order to make effective
the licence of the economic rights here above listed.

The Licensor grants to the Licensee royalty-free, non-exclusive usage rights to
any patents held by the Licensor, to the extent necessary to make use of the
rights granted on the Work under this Licence.

3. Communication of the Source Code

The Licensor may provide the Work either in its Source Code form, or as
Executable Code. If the Work is provided as Executable Code, the Licensor
provides in addition a machine-readable copy of the Source Code of the Work
along with each copy of the Work that the Licensor distributes or indicates, in
a notice following the copyright notice attached to the Work, a repository where
the Source Code is easily and freely accessible for as long as the Licensor
continues to distribute or communicate the Work.

4. Limitations on copyright

Nothing in this Licence is intended to deprive the Licensee of the benefits from
any exception or limitation to the exclusive rights of the rights owners in the
Work, of the exhaustion of those rights or of other applicable limitations
thereto.

5. Obligations of the Licensee

The grant of the rights mentioned above is subject to some restrictions and
obligations imposed on the Licensee. Those obligations are the following:

Attribution right: The Licensee shall keep intact all copyright, patent or
trademarks notices and all notices that refer to the Licence and to the
disclaimer of warranties. The Licensee must include a copy of such notices and a
copy of the Licence with every copy of the Work he/she distributes or
communicates. The Licensee must cause any Derivative Work to carry prominent
notices stating that the Work has been modified and the date of modification.

Copyleft clause: If the Licensee distributes or communicates copies of the
Original Works or Derivative Works, this Distribution or Communication will be
done under the terms of this Licence or of a later version of this Licence
unless the Original Work is expressly distributed only under this version of the
Licence — for example by communicating ‘EUPL v. 1.2 only’. The Licensee
(becoming Licensor) cannot offer or impose any additional terms or conditions on
the Work or Derivative Work that alter or restrict the terms of the Licence.

Compatibility clause: If the Licensee Distributes or Communicates Derivative
Works or copies thereof based upon both the Work and another work licensed under
a Compatible Licence, this Distribution or Communication can be done under the
terms of this Compatible Licence. For the sake of this clause, ‘Compatible
Licence’ refers to the licences listed in the appendix attached to this Licence.
Should the Licensee's obligations under the Compatible Licence conflict with
his/her obligations under this Licence, the obligations of the Compatible
Licence shall prevail.

Provision of Source Code: When distributing or communicating copies of the Work,
the Licensee will provide a machine-readable copy of the Source Code or indicate
a repository where this Source will be easily and freely available for as long
as the Licensee continues to distribute or communicate the Work.

Legal Protection: This Licence does not grant permission to use the trade names,
trademarks, service marks, or names of the Licensor, except as required for
reasonable and customary use in describing the origin of the Work and
reproducing the content of the copyright notice.

6. Chain of Authorship

The original Licensor warrants that the copyright in the Original Work granted
hereunder is owned by him/her or licensed to him/her and that he/she has the
power and authority to grant the Licence.

Each Contributor warrants that the copyright in the modifications he/she brings
to the Work are owned by him/her or licensed to him/her and that he/she has the
power and authority to grant the Licence.

Each time You accept the Licence, the original Licensor and subsequent
Contributors grant You a licence to their contributions to the Work, under the
terms of this Licence.

7. Disclaimer of Warranty

The Work is a work in progress, which is continuously improved by numerous
Contributors. It is not a finished work and may therefore contain defects or
‘bugs’ inherent to this type of development.

For the above reason, the Work is provided under the Licence on an ‘as is’ basis
and without warranties of any kind concerning the Work, including without
limitation merchantability, fitness for a particular purpose, absence of defects
or errors, accuracy, non-infringement of intellectual property rights other than
copyright as stated in Article 6 of this Licence.

This disclaimer of warranty is an essential part of the Licence and a condition
for the grant of any rights to the Work.

8. Disclaimer of Liability

Except in the cases of wilful misconduct or damages directly caused to natural
persons, the Licensor will in no event be liable for any direct or indirect,
material or moral, damages of any kind, arising out of the Licence or of the use
of the Work, including without limitation, damages for loss of goodwill, work
stoppage, computer failure or malfunction, loss of data or any commercial
damage, even if the Licensor has been advised of the possibility of such damage.
However, the Licensor will be liable under statutory product liability laws as
far such laws apply to the Work.

9. Additional agreements

While distributing the Work, You may choose to conclude an additional agreement,
defining obligations or services consistent with this Licence. However, if
accepting obligations, You may act only on your own behalf and on your sole
responsibility, not on behalf of the original Licensor or any other Contributor,
and only if You agree to indemnify, defend, and hold each Contributor harmless
for any liability incurred by, or claims asserted against such Contributor by
the fact You have accepted any warranty or additional liability.

10. Acceptance of the Licence

The provisions of this Licence can be accepted by clicking on an icon ‘I agree’
placed under the bottom of a window displaying the text of this Licence or by
affirming consent in any other similar way, in accordance with the rules of
applicable law. Clicking on that icon indicates your clear and irrevocable
acceptance of this Licence and all of its terms and conditions.

Similarly, you irrevocably accept this Licence and all of its terms and
conditions by exercising any rights granted to You by Article 2 of this Licence,
such as the use of the Work, the creation by You of a Derivative Work or the
Distribution or Communication by You of the Work or copies thereof.

11. Information to the public

In case of any Distribution or Communication of the Work by means of electronic
communication by You (for example, by offering to download the Work from a
remote location) the distribution channel or media (for example, a website) must
at least provide to the public the information requested by the applicable law
regarding the Licensor, the Licence and the way it may be accessible, concluded,
stored and reproduced by the Licensee.

12. Termination of the Licence

The Licence and the rights granted hereunder will terminate automatically upon
any breach by the Licensee of the terms of the Licence.

Such a termination will not terminate the licences of any person who has
received the Work from the Licensee under the Licence, provided such persons
remain in full compliance with the Licence.

13. Miscellaneous

Without prejudice of Article 9 above, the Licence represents the complete
agreement between the Parties as to the Work.

If any provision of the Licence is invalid or unenforceable under applicable
law, this will not affect the validity or enforceability of the Licence as a
whole. Such provision will be construed or reformed so as necessary to make it
valid and enforceable.

The European Commission may publish other linguistic versions or new versions of
this Licence or updated versions of the Appendix, so far this is required and
reasonable, without reducing the scope of the rights granted by the Licence. New
versions of the Licence will be published with a unique version number.

All linguistic versions of this Licence, approved by the European Commission,
have identical value. Parties can take advantage of the linguistic version of
their choice.

14. Jurisdiction

Without prejudice to specific agreement between parties,

- any litigation resulting from the interpretation of this License, arising
  between the European Union institutions, bodies, offices or agencies, as a
  Licensor, and any Licensee, will be subject to the jurisdiction of the Court
  of Justice of the European Union, as laid down in article 272 of the Treaty on
  the Functioning of the European Union,

- any litigation arising between other parties and resulting from the
  interpretation of this License, will be subject to the exclusive jurisdiction
  of the competent court where the Licensor resides or conducts its primary
  business.

15. Applicable Law

Without prejudice to specific agreement between parties,

- this Licence shall be governed by the law of the European Union Member State
  where the Licensor has his seat, resides or has his registered office,

- this licence shall be governed by Belgian law if the Licensor has no seat,
  residence or registered office inside a European Union Member State.

Appendix

‘Compatible Licences’ according to Article 5 EUPL are:

- GNU General Public License (GPL) v. 2, v. 3
- GNU Affero General Public License (AGPL) v. 3
- Open Software License (OSL) v. 2.1, v. 3.0
- Eclipse Public License (EPL) v. 1.0
- CeCILL v. 2.0, v. 2.1
- Mozilla Public Licence (MPL) v. 2
- GNU Lesser General Public Licence (LGPL) v. 2.1, v. 3
- Creative Commons Attribution-ShareAlike v. 3.0 Unported (CC BY-SA 3.0) for
  works other than software
- European Union Public Licence (EUPL) v. 1.1, v. 1.2
- Québec Free and Open-Source Licence — Reciprocity (LiLiQ-R) or Strong
  Reciprocity (LiLiQ-R+).

The European Commission may update this Appendix to later versions of the above
licences without producing a new version of the EUPL, as long as they provide
the rights granted in Article 2 of this Licence and protect the covered Source
Code from exclusive appropriation.

All other changes or additions to this Appendix require the production of a new
EUPL version.

===== DRL =====
# Detection Rule License (DRL) 1.1

Applies to: all files under `scripts/risk_patterns.py`, `data/patterns/`, and
`content/regulations/delta-log/` in this repository. The scanning engine and CLI
remain under the Apache License 2.0 (`LICENSE.txt`).

---

Permission is hereby granted, free of charge, to any person obtaining a copy of
this rule set and associated documentation files (the "Rules"), to deal in the
Rules without restriction, including without limitation the rights to use, copy,
modify, merge, publish, distribute, sublicense, and/or sell copies of the Rules,
and to permit persons to whom the Rules are furnished to do so, subject to the
following conditions:

If you share the Rules (including in modified form), you must retain the
following if it is supplied within the Rules:

1. identification of the authors(s) ("author" field) of the Rule and any others
   designated to receive attribution, in any reasonable manner requested by the
   Rule author (including by pseudonym if designated).

2. a URI or hyperlink to the Rule set or explicit Rule to the extent reasonably
   practicable

3. indicate the Rules are licensed under this Detection Rule License, and
   include the text of, or the URI or hyperlink to, this Detection Rule License
   to the extent reasonably practicable

If you use the Rules (including in modified form) on data, messages based on
matches with the Rules must retain the following if it is supplied within the
Rules:

1. identification of the authors(s) ("author" field) of the Rule and any others
   designated to receive attribution, in any reasonable manner requested by the
   Rule author (including by pseudonym if designated).

THE RULES ARE PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN
AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE RULES OR THE USE OR OTHER DEALINGS IN THE RULES.

===== NOTICE =====
Regula
Copyright 2026 The Implementation Layer

This product includes software developed by
The Implementation Layer (https://getregula.com).

Detection rules are separately licensed under
the Detection Rule License v1.1 (DRL-1.1).
See LICENSE.Detection.Rules.md for details.
./scripts/ai_code_governance.py
./scripts/cli_governance.py
./scripts/__pycache__/cli_governance.cpython-312.pyc
./scripts/__pycache__/ai_code_governance.cpython-312.pyc
./AI_GOVERNANCE.md
./docs/AI_GOVERNANCE.md
./tests/test_agent_governance.py
./tests/__pycache__/test_agent_governance.cpython-312-pytest-9.1.1.pyc
./tests/__pycache__/test_agent_governance.cpython-312-pytest-9.0.2.pyc
./tests/__pycache__/test_agent_governance.cpython-312.pyc
./tests/__pycache__/test_agent_governance.cpython-312-pytest-8.4.2.pyc
./CODE_OF_CONDUCT.md
./GOVERNANCE.md
./site/blog/blog-aicdi-governance-gaps.html
[exit 0]
```

Ended: `2026-08-05T00:17:17+01:00`

## Pricing, proposition and public inventory

Started: `2026-08-05T00:17:17+01:00`

Command:

```console
$ bash -lc 'cat site/pricing.html; printf '"'"'\n===== SITE INDEX =====\n'"'"'; cat site/index.html; printf '"'"'\n===== PUBLIC INVENTORY =====\n'"'"'; cat data/public_surface_inventory.json 2>/dev/null || true; find . -iname '"'"'*public*surface*'"'"' -o -iname '"'"'*research*register*'"'"' -print'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <!-- Critical inline CSS + non-render-blocking stylesheets — same pattern as
         blog posts. Inline critical CSS establishes dark theme immediately;
         color-scheme: dark hints the canvas colour; stylesheets load via
         media="print" + onload swap so they don't block first paint. -->
    <style>
      :root { color-scheme: dark }
      html, body {
        background: #070711;
        color: #e2e2f0;
        margin: 0;
        font-family: 'DM Sans', system-ui, -apple-system, sans-serif;
        line-height: 1.65;
        -webkit-font-smoothing: antialiased;
      }
    </style>
    <meta name="theme-color" content="#070711">
    <meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' 'unsafe-inline' https://plausible.io; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self' https://plausible.io; font-src 'self'; frame-src 'none'; base-uri 'self'; form-action 'self'">
    <meta http-equiv="X-Content-Type-Options" content="nosniff">
    <meta name="referrer" content="strict-origin-when-cross-origin">
    <title>Evidence Packs &mdash; Signed AI Act Reports | Regula</title>
    <meta name="description" content="Signed, timestamped compliance reports you can hand to an auditor. The Regula CLI is free forever; paid evidence-pack tiers are planned and not yet purchasable.">
    <meta property="og:type" content="website">
    <meta property="og:url" content="https://getregula.com/pricing.html">
    <meta property="og:title" content="Evidence Packs — Signed EU AI Act Compliance Reports | Regula">
    <meta property="og:description" content="Signed, timestamped compliance reports you can hand to an auditor. The CLI is free forever; paid tiers are planned and not yet purchasable.">
    <meta property="og:image" content="https://getregula.com/assets/og-image.png">
    <meta property="og:image:alt" content="Regula — EU AI Act compliance tool for code">
    <meta property="og:locale" content="en_GB">
    <meta property="og:site_name" content="Regula">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="Evidence Packs — Signed EU AI Act Compliance Reports | Regula">
    <meta name="twitter:description" content="Signed, timestamped compliance reports you can hand to an auditor. The CLI is free forever; paid tiers are planned and not yet purchasable.">
    <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@type": "WebPage",
      "name": "Evidence Packs — Signed EU AI Act Compliance Reports",
      "url": "https://getregula.com/pricing.html",
      "description": "Signed, timestamped compliance reports you can hand to an auditor. The Regula CLI is free forever; paid evidence-pack tiers are planned and not yet purchasable.",
      "isPartOf": {"@type": "WebSite", "name": "Regula", "url": "https://getregula.com/"},
      "breadcrumb": {
        "@type": "BreadcrumbList",
        "itemListElement": [
          {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://getregula.com/"},
          {"@type": "ListItem", "position": 2, "name": "Evidence Packs", "item": "https://getregula.com/pricing.html"}
        ]
      }
    }
    </script>
    <meta name="robots" content="index, follow, max-image-preview:large">
    <link rel="canonical" href="https://getregula.com/pricing.html">
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect width='100' height='100' rx='16' fill='%233b82f6'/><text x='50' y='72' font-family='system-ui' font-size='64' font-weight='700' fill='white' text-anchor='middle'>R</text></svg>">
    <link rel="stylesheet" href="/assets/fonts.min.css" media="print" onload="this.media='all';this.onload=null">
    <link rel="preload" href="/assets/fonts/dm-sans-latin.woff2" as="font" type="font/woff2" fetchpriority="high" crossorigin>
    <link rel="preload" href="/assets/fonts/fraunces-latin.woff2" as="font" type="font/woff2" fetchpriority="high" crossorigin>
    <link rel="stylesheet" href="/assets/site.min.css" media="print" onload="this.media='all';this.onload=null">
    <noscript>
        <link rel="stylesheet" href="/assets/fonts.min.css">
        <link rel="stylesheet" href="/assets/site.min.css">
    </noscript>
    <style>
        /* Pricing page styles */
        .pricing-hero {
            max-width: 720px;
            margin: var(--s12) auto var(--s10);
            padding: 0 var(--s6);
            text-align: center;
        }
        .pricing-hero h1 {
            font-family: var(--font-serif);
            font-size: clamp(28px, 5vw, 42px);
            font-weight: 700;
            line-height: 1.15;
            letter-spacing: -0.02em;
            margin-bottom: var(--s5);
        }
        .pricing-hero .subtitle {
            font-size: 16px;
            color: var(--text-2);
            max-width: 560px;
            margin: 0 auto;
            line-height: 1.7;
        }

        .pricing-cards {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: var(--s6);
            max-width: 960px;
            margin: 0 auto var(--s12);
            padding: 0 var(--s6);
        }

        .pricing-card {
            background: var(--bg-elev);
            border: 1px solid var(--border);
            border-radius: var(--r-lg);
            padding: var(--s7) var(--s6);
            display: flex;
            flex-direction: column;
        }
        .pricing-card.featured {
            border-color: var(--accent);
            background: var(--bg-elev-2);
            position: relative;
        }
        .pricing-card.featured::before {
            content: "Most useful";
            position: absolute;
            top: calc(-1 * var(--s3));
            left: 50%;
            transform: translateX(-50%);
            background: var(--accent);
            color: #fff;
            font-family: var(--font-mono);
            font-size: 11px;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            padding: var(--s1) var(--s4);
            border-radius: var(--r-pill);
        }

        .pricing-card h3 {
            font-family: var(--font-serif);
            font-size: 22px;
            font-weight: 700;
            margin-bottom: var(--s2);
        }
        .pricing-card .price {
            font-family: var(--font-serif);
            font-size: 36px;
            font-weight: 700;
            margin-bottom: var(--s2);
        }
        .pricing-card .price-note {
            font-size: 13px;
            color: var(--text-dim);
            margin-bottom: var(--s6);
        }

        .pricing-card ul {
            list-style: none;
            padding: 0;
            margin: 0 0 var(--s7);
            flex: 1;
        }
        .pricing-card ul li {
            padding: var(--s2) 0;
            font-size: 14px;
            color: var(--text-2);
            border-bottom: 1px solid var(--border);
            line-height: 1.55;
        }
        .pricing-card ul li:last-child { border-bottom: none; }
        .pricing-card ul li::before {
            content: "\2713\00a0";
            color: var(--success);
            font-weight: 700;
        }

        .pricing-card .cta-btn {
            display: block;
            text-align: center;
            padding: var(--s3) var(--s5);
            border-radius: var(--r-md);
            font-family: var(--font-mono);
            font-size: 13px;
            font-weight: 500;
            text-decoration: none;
            min-height: 44px;
            line-height: 44px;
            padding: 0 var(--s5);
            cursor: default;
        }
        .pricing-card .cta-btn.free {
            background: var(--accent-soft);
            color: #bae6fd;
            border: 1px solid rgba(59,130,246,0.2);
        }
        .pricing-card .cta-btn.coming {
            background: var(--bg-elev);
            color: var(--text-dim);
            border: 1px solid var(--border-strong);
        }
        .pricing-card.featured .cta-btn.coming {
            background: rgba(59,130,246,0.1);
            color: #bae6fd;
            border: 1px solid rgba(59,130,246,0.3);
        }

        .pricing-card code {
            font-family: var(--font-mono);
            font-size: 12px;
            color: var(--text-dim);
            background: rgba(255,255,255,0.04);
            padding: 2px 6px;
            border-radius: var(--r-sm);
        }

        .trust-note {
            max-width: 640px;
            margin: 0 auto var(--s12);
            padding: 0 var(--s6);
            text-align: center;
        }
        .trust-note p {
            font-size: 14px;
            color: var(--text-dim);
            line-height: 1.7;
        }
        .trust-note strong {
            color: var(--text-2);
        }

        .pricing-faq {
            max-width: 640px;
            margin: 0 auto var(--s12);
            padding: 0 var(--s6);
        }
        .pricing-faq h2 {
            font-family: var(--font-serif);
            font-size: 24px;
            margin-bottom: var(--s6);
            text-align: center;
        }
        .pricing-faq details {
            border-bottom: 1px solid var(--border);
            padding: var(--s5) 0;
        }
        .pricing-faq summary {
            font-size: 15px;
            font-weight: 500;
            color: var(--text);
            cursor: pointer;
            min-height: 44px;
            display: flex;
            align-items: center;
        }
        .pricing-faq summary:focus-visible {
            outline: 2px solid var(--accent);
            outline-offset: 3px;
            border-radius: var(--r-sm);
        }
        .pricing-faq details p {
            font-size: 14px;
            color: var(--text-2);
            margin-top: var(--s3);
            line-height: 1.7;
        }

        @media (max-width: 768px) {
            .pricing-cards {
                grid-template-columns: 1fr;
                max-width: 400px;
            }
            .pricing-hero {
                margin: var(--s10) auto var(--s8);
            }
        }
    </style>
    <!-- Privacy-friendly analytics by Plausible -->
    <script async src="https://plausible.io/js/pa-_TnuxaU2TjRgMK9Cc1btN.js"></script>
    <script>
      window.plausible=window.plausible||function(){(plausible.q=plausible.q||[]).push(arguments)},plausible.init=plausible.init||function(i){plausible.o=i||{}};
      plausible.init()
    </script>
</head>
<body>

<a href="#main" class="skip-link">Skip to content</a>

<nav class="nav" id="nav" aria-label="Main navigation">
    <a href="/" class="nav-brand">Regula</a>
    <button type="button" class="nav-toggle" onclick="const d=document.getElementById('nav-menu');if(d.open){d.close();this.setAttribute('aria-expanded','false')}else{d.showModal();this.setAttribute('aria-expanded','true')}" aria-label="Menu" aria-expanded="false">&#9776;</button>
    <dialog id="nav-menu" class="nav-right" aria-label="Site navigation" onclick="if(event.target===this)this.close()" onclose="document.querySelector('#nav .nav-toggle').setAttribute('aria-expanded','false')">
        <a href="/assess/" title="Free EU AI Act risk assessment">Assess</a>
        <a href="/guides/">Guides</a>
        <a href="https://github.com/kuzivaai/getregula">GitHub</a>
        <a href="https://github.com/kuzivaai/getregula/blob/main/docs/course/README.md">Docs</a>
        <a href="/regions/regulations.html" title="Global AI regulation tracker">Regulations</a>
        <a href="/blog/writing.html" title="Research notes on AI governance">Blog</a>
        <a href="/about.html">About</a>
        <a href="/">EN</a>
        <a href="/locales/de.html">DE</a>
        <a href="/locales/pt-br.html">BR</a>
    </dialog>
</nav>

<main id="main">

<div class="pricing-hero">
    <h1>Evidence packs for your auditor</h1>
    <p class="subtitle">Regula is free. The CLI stays free forever. Evidence packs are signed, timestamped compliance reports you can hand to an auditor, a customer, or a regulator.</p>
</div>

<div class="pricing-cards">

    <!-- Free tier -->
    <div class="pricing-card">
        <h3>Free</h3>
        <div class="price">EUR 0</div>
        <div class="price-note">Free forever</div>
        <ul>
            <li>Risk classification across 419 patterns</li>
            <li>Gap analysis against EU AI Act articles</li>
            <li>Remediation plan with effort estimates</li>
            <li>JSON and text output</li>
            <li>Annex IV documentation scaffold</li>
        </ul>
        <code style="margin-bottom: var(--s5); display: block;">regula check . && regula gap .</code>
        <span class="cta-btn free">Current behaviour</span>
    </div>

    <!-- Starter tier -->
    <div class="pricing-card featured">
        <h3>Starter</h3>
        <div class="price">EUR 49</div>
        <div class="price-note">One-time per evidence pack</div>
        <ul>
            <li>Everything in Free</li>
            <li>Ed25519-signed evidence pack</li>
            <li>SHA-256 integrity manifest</li>
            <li>Annex IV documentation scaffold</li>
            <li>Compliance score with per-article breakdown</li>
            <li>Reviewer-completable PDF-printable scaffold</li>
        </ul>
        <code style="margin-bottom: var(--s5); display: block;">regula conform --sign .</code>
        <span class="cta-btn coming">Coming soon</span>
    </div>

    <!-- Professional tier -->
    <div class="pricing-card">
        <h3>Professional</h3>
        <div class="price">EUR 149</div>
        <div class="price-note">One-time per evidence pack</div>
        <ul>
            <li>Everything in Starter</li>
            <li>Conformity assessment pack</li>
            <li>Declaration of Conformity template</li>
            <li>Prioritised remediation plan</li>
            <li>CycloneDX AI SBOM</li>
            <li>RFC 3161 timestamp</li>
        </ul>
        <code style="margin-bottom: var(--s5); display: block;">regula conform --sign --timestamp .</code>
        <span class="cta-btn coming">Coming soon</span>
    </div>

</div>

<div class="trust-note" style="background:rgba(245,158,11,0.08);border-left:3px solid #f59e0b;padding:16px 20px;margin:0 0 24px;border-radius:0 8px 8px 0;">
    <p><strong>Paid tiers are not yet available.</strong> No payment is currently processed and no purchase is possible. The pricing shown is indicative of the planned model. The free CLI and all its commands remain fully available.</p>
</div>
<div class="trust-note">
    <p><strong>The core scanner processes files locally and does not upload them.</strong> Evidence packs are generated locally. Optional integrations and the platform running Regula may have their own data handling, which you should review separately.</p>
</div>

<div class="pricing-faq">
    <h2>Questions</h2>

    <details>
        <summary>Will the free tier ever become paid?</summary>
        <p>No. The CLI is the distribution channel. Every command that exists today stays free forever. Evidence packs are a paid deliverable on top of the free tool.</p>
    </details>

    <details>
        <summary>What do I actually get?</summary>
        <p>A ZIP bundle containing JSON scan results, gap analysis, Annex IV documentation, remediation plan, and a SHA-256 integrity manifest. Starter packs are Ed25519-signed. Professional packs add a conformity assessment pack, Declaration of Conformity template, and a CycloneDX SBOM.</p>
    </details>

    <details>
        <summary>Is this a subscription?</summary>
        <p>No. Each payment generates one evidence pack for one project at a point in time. Run it again next quarter if your codebase has changed.</p>
    </details>

    <details>
        <summary>Can my auditor verify the pack?</summary>
        <p>Yes. Each bundle includes a standalone <code>verify.py</code> script that checks SHA-256 hashes of every file against the manifest. Signed packs also include an Ed25519 signature your auditor can verify independently.</p>
    </details>
</div>

</main>

<footer>
    <div class="foot-inner">
        <div class="foot-left">
            <div class="foot-brand">Regula</div>
            <div class="foot-links">
                <a href="/assess/">Assess</a>
                <a href="/guides/">Guides</a>
                <a href="https://github.com/kuzivaai/getregula">GitHub</a>
                <a href="https://pypi.org/project/regula-ai/">PyPI</a>
                <a href="/blog/writing.html">Blog</a>
                <a href="/regions/regulations.html">Regulations</a>
                <a href="/about.html">About</a>
            </div>
            <div class="foot-copy">Open source &middot; Apache 2.0 / EUPL 1.2 &middot; &copy; 2026 Regula</div>
        </div>
        <div class="foot-right">
            <div class="foot-legal">
                <strong>Not legal advice.</strong> Regula identifies regulatory risk indicators in code for developer review. It does not constitute legal advice. Consult a qualified legal professional for legal questions.
            </div>
        </div>
    </div>
</footer>

<script>
    // Nav scroll
    function updateNav() {
        document.getElementById('nav').classList.toggle('scrolled', window.scrollY > 20);
    }
    window.addEventListener('scroll', updateNav, { passive: true });
</script>

</body>
</html>

===== SITE INDEX =====
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <!-- Critical inline CSS + non-render-blocking stylesheet loading.
         Why: /assets/site.min.css is render-blocking, so Chrome shows a WHITE canvas
         (the browser default) for the entire duration of the CSS fetch on cold
         loads :  measured at ~600ms on simulated 3G, worse on real slow networks.
         That white→dark snap is what users reported as "the demo flashing": the
         hero terminal sits at the top of the fold and takes the full brunt of it.
         The earlier attempt (27cfba4) targeted panel opacity and font preload,
         neither of which is the actual cause :  the cause is that the browser
         cannot paint at all until the external stylesheet arrives.

         Fix: establish the brand background + basic tokens inline so first paint
         is already dark, then load site.css asynchronously via the media="print"
         + onload swap trick (well-documented pattern). A <noscript> fallback
         preserves styling for JS-disabled clients. -->
    <style>
      :root { color-scheme: dark }
      html, body {
        background: #070711;
        color: #e2e2f0;
        margin: 0;
        font-family: 'DM Sans', system-ui, -apple-system, sans-serif;
        line-height: 1.65;
        -webkit-font-smoothing: antialiased;
      }
      /* Pre-external-CSS state for the hero terminal panels so the initial paint
         shows the active panel at opacity 1 and hides the rest, matching the
         post-CSS visual. Prevents a vertical stack of all four panels flashing
         briefly before site.css loads. */
      .term-panel { opacity: 0; position: absolute; top: 0; left: 0; right: 0 }
      .term-panel.active { opacity: 1; position: relative }
      .term-body { position: relative; min-height: 340px }
    </style>
    <meta name="theme-color" content="#070711">
    <!-- CSP: GitHub Pages cannot set server headers; meta tag is the only option.
         'unsafe-inline' is required (inline scripts/styles throughout).
         frame-ancestors is ignored in meta CSP per spec :  clickjacking protection
         requires a server header or CDN proxy (e.g. Cloudflare). -->
    <meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' 'unsafe-inline' https://plausible.io https://unpkg.com; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self' https://formspree.io https://plausible.io; font-src 'self'; frame-src 'none'; base-uri 'self'; form-action 'self' https://formspree.io">
    <meta http-equiv="X-Content-Type-Options" content="nosniff">
    <meta name="referrer" content="strict-origin-when-cross-origin">
    <link rel="preconnect" href="https://plausible.io" crossorigin>
    <link rel="preconnect" href="https://unpkg.com" crossorigin>
    <title>Regula: EU AI Act Code-Indicator Scanner (Open Source)</title>
    <meta name="description" content="Open-source tool that flags AI governance risks in source code for human review. It does not determine legal classification or compliance.">
    <meta name="robots" content="index, follow, max-image-preview:large">
    <meta property="og:title" content="Regula: EU AI Act Code-Indicator Scanner (Open Source)">
    <meta property="og:description" content="Open-source tool that flags AI governance risks in source code for human review. It does not determine legal classification or compliance.">
    <meta property="og:type" content="website">
    <meta property="og:url" content="https://getregula.com/">
    <meta property="og:site_name" content="Regula">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:site" content="@kuzivaai">
    <meta property="og:locale" content="en_GB">
    <meta name="twitter:title" content="Regula: EU AI Act Code-Indicator Scanner (Open Source)">
    <meta name="twitter:description" content="Open-source tool that flags AI governance risks in source code for human review. It does not determine legal classification or compliance.">
    <meta property="og:image" content="https://getregula.com/assets/og-image.png">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="630">
    <meta property="og:image:alt" content="Regula :  EU AI Act code-indicator scanner">
    <meta name="twitter:image" content="https://getregula.com/assets/og-image.png">
    <meta name="twitter:image:alt" content="Regula :  EU AI Act code-indicator scanner">
    <meta name="author" content="Regula">
    <link rel="canonical" href="https://getregula.com/">
    <script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": "Regula",
        "description": "Open-source EU AI Act compliance CLI combining code scanning and governance questionnaires. 419 risk patterns, 13 compliance frameworks, structured self-assessments.",
        "url": "https://getregula.com",
        "applicationCategory": "DeveloperApplication",
        "operatingSystem": "Linux, macOS, Windows",
        "license": "https://www.apache.org/licenses/LICENSE-2.0",
        "offers": {
            "@type": "Offer",
            "price": "0",
            "priceCurrency": "USD"
        },
        "softwareVersion": "1.9.0",
        "programmingLanguage": "Python",
        "codeRepository": "https://github.com/kuzivaai/getregula"
    }
    </script>
    <script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": "Regula",
        "alternateName": "Regula EU AI Act CLI",
        "url": "https://getregula.com",
        "logo": "https://getregula.com/assets/regula-logo.png",
        "sameAs": [
            "https://github.com/kuzivaai/getregula",
            "https://pypi.org/project/regula-ai/"
        ],
        "description": "Open-source EU AI Act compliance CLI for developers.",
        "disambiguatingDescription": "Open-source command-line tool for EU AI Act compliance scanning. Not affiliated with Regula Forensics (identity verification).",
        "contactPoint": {
            "@type": "ContactPoint",
            "email": "support@getregula.com",
            "contactType": "customer support"
        }
    }
    </script>
    <script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Regula"}
        ]
    }
    </script>
    <script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": "Regula",
        "url": "https://getregula.com",
        "potentialAction": {
            "@type": "SearchAction",
            "target": {
                "@type": "EntryPoint",
                "urlTemplate": "https://github.com/kuzivaai/getregula/search?q={search_term_string}"
            },
            "query-input": "required name=search_term_string"
        }
    }
    </script>
    <script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": "Is my AI app prohibited under the EU AI Act?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "Article 5 prohibits specified practices, including certain forms of social scoring, manipulation, biometric identification, and emotion inference. The exact scope, conditions, and exceptions matter. Regula flags related code patterns for review; it does not determine that a prohibited practice exists."
                }
            },
            {
                "@type": "Question",
                "name": "Does the EU AI Act apply to my company if I'm outside the EU?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "Potentially. Article 2(1)(c) covers providers and deployers established outside the EU where an AI system's output is used in the Union, subject to the Act's roles, exclusions, and other scope conditions. Location alone does not decide applicability."
                }
            },
            {
                "@type": "Question",
                "name": "What makes an AI system high-risk under the EU AI Act?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "Article 6 contains the classification routes and Annex III lists specified intended uses across eight areas. Conditions, exceptions, intended purpose, and deployment context matter. Regula reports related code indicators but does not determine high-risk status."
                }
            },
            {
                "@type": "Question",
                "name": "When does the EU AI Act start being enforced?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "The original Article 5 prohibitions have applied since 2 February 2025. GPAI provisions began applying on 2 August 2025, subject to transition rules. Regulation (EU) 2026/1744 sets 2 December 2027 for Annex III high-risk provisions and 2 August 2028 for the Annex I product path. Article 50 generally has applied since 2 August 2026, with a specific 2 December 2026 transition for providers of Article 50(2) systems already on the market."
                }
            },
            {
                "@type": "Question",
                "name": "Is Regula free?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "Yes. Regula is open-source under the Apache 2.0 or EUPL 1.2 licence (your choice). Detection rule patterns carry a separate Detection Rule Licence (DRL 1.1) requiring attribution on redistribution :  see the NOTICE file. No account, no API key, no sales call. Install with pipx install regula-ai (see docs/installation.md for uv and pip alternatives) and run it locally on your codebase. The full CLI, all 62 commands (including `regula handoff` for Garak/Giskard/Promptfoo scoping and `regula regwatch` for delta-log drift warnings), all 419 risk patterns, and all 13 compliance framework mappings are free."
                }
            },
            {
                "@type": "Question",
                "name": "What are the fines under the EU AI Act?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "Prohibited AI practices (Article 5) carry fines up to €35 million or 7% of global annual turnover, whichever is higher. High-risk violations carry fines up to €15 million or 3% of turnover. Non-compliance with information requirements carries fines up to €7.5 million or 1% of turnover."
                }
            },
            {
                "@type": "Question",
                "name": "Can Regula test AI models for bias?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "Regula includes an optional bias evaluation command (regula bias) that runs CrowS-Pairs and BBQ stereotype benchmarks against a local Ollama model, with statistical confidence intervals. It is a development-time starting point for Article 10 bias documentation, not a production fairness testing tool. For production bias measurement, use dedicated platforms like IBM watsonx.governance or Fiddler AI."
                }
            },
            {
                "@type": "Question",
                "name": "Does the EU AI Act overlap with GDPR, DORA, or NIS2?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "Yes, significantly. High-risk AI systems that process personal data must also comply with GDPR, and other regulations like DORA and NIS2 may apply depending on your sector. Regula cross-maps each AI Act article to ISO 42001, NIST AI RMF, NIST CSF, SOC 2, ISO 27001, OWASP LLM Top 10, MITRE ATLAS, and other framework obligations in a single scan. Run regula gap --project . to see where your obligations overlap across all 13 mapped frameworks."
                }
            },
            {
                "@type": "Question",
                "name": "Does Regula work with AI-generated code from Cursor, Claude Code, or Lovable?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "Yes. Regula scans source code files regardless of who or what wrote them. Authorship alone does not determine whether the EU AI Act applies: Article 2 scope, the actor's role, intended purpose, deployment context, and applicable exclusions still require review. Run regula check . for code-observable indicators and regula assess to record context."
                }
            },
            {
                "@type": "Question",
                "name": "What should I do right now to prepare for the EU AI Act?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "Install Regula, run the declared-context questionnaire, then scan for code-observable indicators. Findings require human review and do not determine legal classification or compliance. Runtime varies by repository and environment."
                }
            }
        ]
    }
    </script>
    <link rel="alternate" hreflang="en" href="https://getregula.com/">
    <link rel="alternate" hreflang="de" href="https://getregula.com/locales/de.html">
    <link rel="alternate" hreflang="pt-BR" href="https://getregula.com/locales/pt-br.html">
    <link rel="alternate" hreflang="x-default" href="https://getregula.com/">
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect width='100' height='100' rx='16' fill='%233b82f6'/><text x='50' y='72' font-family='system-ui' font-size='64' font-weight='700' fill='white' text-anchor='middle'>R</text></svg>">
    <link rel="alternate" type="text/markdown" title="LLM-friendly version" href="/llms.txt">
    <!-- Stylesheets loaded via media="print" + onload swap so they don't block
         first paint. The inline critical CSS above already establishes the dark
         theme; these sheets layer on the full design system once they arrive.
         <noscript> fallback ensures JS-disabled clients still get full styling. -->
    <!-- CSP note: these inline onload handlers require 'unsafe-inline' in script-src.
         If adding a Content Security Policy, migrate to a hashed <script> block. -->
    <link rel="stylesheet" href="/assets/fonts.min.css" media="print" onload="this.media='all';this.onload=null">
    <link rel="stylesheet" href="/assets/site.min.css" media="print" onload="this.media='all';this.onload=null">
    <noscript>
        <link rel="stylesheet" href="/assets/fonts.min.css">
        <link rel="stylesheet" href="/assets/site.min.css">
    </noscript>
    <link rel="preload" href="/assets/fonts/dm-sans-latin.woff2" as="font" type="font/woff2" fetchpriority="high" crossorigin>
    <link rel="preload" href="/assets/fonts/fraunces-latin.woff2" as="font" type="font/woff2" fetchpriority="high" crossorigin>
    <!-- JetBrains Mono is used only inside the hero terminal demo. Preload
         eliminates the font-swap reflow that otherwise reads as a flash
         when the woff2 arrives late. -->
    <link rel="preload" href="/assets/fonts/jetbrains-mono-latin.woff2" as="font" type="font/woff2" fetchpriority="high" crossorigin>
    <style>
        /* index.html overrides :  values that intentionally differ from site.css */
        body { line-height: 1.6; }
        .nav { height: 52px; }
        .badge { gap: 6px; padding: 4px 12px; }
        .badge-dot { width: 5px; height: 5px; }
        .hero h1 { font-size: 60px; line-height: 1.1; letter-spacing: -0.04em; }
        .hero .sub { font-size: 16px; color: var(--text-dim); }
        .term-bar { background: #080813; border-bottom-color: rgba(255,255,255,0.06); }
        .td-r { background: var(--danger); } .td-y { background: #eab308; } .td-g { background: #22c55e; }
        .sec { padding: 80px 32px 0; }
        .sec-head { font-size: 28px; letter-spacing: -0.03em; line-height: 1.2; }
        .sec-sub { margin-bottom: 32px; max-width: none; }
        .sep { margin: 80px auto 0; height: 1px; background: rgba(255,255,255,0.06); border-top: none; }
        .art-grid { gap: 10px; }
        .cm { align-items: baseline; }
        .cm code { background: none; padding: 0; border-radius: 0; }
        .final-wrap { margin-top: 80px; border-color: rgba(255,255,255,0.06); }
        .final-glow { top: -50%; bottom: auto; width: 600px; background: radial-gradient(circle, rgba(59,130,246,0.1) 0%, transparent 65%); }
        .final { max-width: 640px; padding: 80px 32px; }
        .final h2 { font-size: 36px; margin-bottom: 10px; }
        .final p { font-size: 15px; margin-bottom: 28px; line-height: 1.6; }
        .final .install-box { margin: 0 auto 24px; }
        .foot { max-width: 1200px; margin: 0 auto; padding: 28px 32px; border-top: 1px solid rgba(255,255,255,0.06); }
        .foot-brand { font-size: 14px; }
        .foot-links { margin-bottom: 8px; }
        .foot-copy { font-size: 12px; margin-top: 8px; }
        .foot-legal { border-color: rgba(255,255,255,0.05); }
        .skip-link { text-decoration: none; }
        @media (max-width: 768px) {
            dialog.nav-right { top: 52px; }
        }
        @media (max-width: 900px) {
            .hero { gap: 36px; padding: 48px 20px 32px; }
            .hero h1 { font-size: 36px; }
            .art-grid { grid-template-columns: 1fr; }
            .scroll-hint { display: block !important; }
        }
        @media (max-width: 640px) {
            .nav { padding: 0 16px; }
            .hero { padding: 36px 16px 24px; }
            .sec { padding: 56px 16px 0; }
            .sep { margin: 56px auto 0; }
            .final { padding: 56px 16px; }
        }
    </style>
    <!-- Privacy-friendly analytics by Plausible -->
    <script async src="https://plausible.io/js/pa-_TnuxaU2TjRgMK9Cc1btN.js"></script>
    <script>
      window.plausible=window.plausible||function(){(plausible.q=plausible.q||[]).push(arguments)},plausible.init=plausible.init||function(i){plausible.o=i||{}};
      plausible.init()
    </script>
    <noscript><style>.reveal { opacity: 1; transform: none; }</style></noscript>
</head>
<body>

<a href="#main" class="skip-link">Skip to content</a>
<!-- NAV -->
<nav class="nav" id="nav" aria-label="Main navigation">
    <a href="/" class="nav-brand">Regula</a>
    <button type="button" class="nav-toggle" onclick="const d=document.getElementById('nav-menu');if(d.open){d.close();this.setAttribute('aria-expanded','false')}else{d.show();this.setAttribute('aria-expanded','true')}" aria-label="Menu" aria-expanded="false">&#9776;</button>
    <dialog id="nav-menu" class="nav-right" aria-label="Site navigation" onclick="if(event.target===this)this.close()" onclose="document.querySelector('#nav .nav-toggle').setAttribute('aria-expanded','false')">
        <a href="/assess/" title="Free EU AI Act risk assessment">Assess</a>
        <a href="/guides/">Guides</a>
        <a href="https://github.com/kuzivaai/getregula">GitHub</a>
        <a href="/regions/regulations.html" title="Global AI regulation tracker">Regulations</a>
        <a href="/blog/writing.html" title="Research notes on AI governance">Blog</a>
        <a href="/about.html">About</a>
        <span class="active">EN</span>
        <a href="/locales/de.html">DE</a>
        <a href="/locales/pt-br.html">BR</a>
    </dialog>
</nav>

<!-- HERO -->
<main id="main">
<div class="hero-wrap">
    <div class="hero-glow"></div>
    <div class="hero">
        <div class="hero-text">
            <div class="badge"><span class="badge-dot"></span> Open-source CLI &middot; v1.9.0 &middot; Apache 2.0</div>
            <h1>Find <span class="hl">AI governance indicators</span> in your code</h1>
            <p class="sub">Scan a source-code folder to find patterns that may need AI governance review. Regula explains why each pattern matters and links to relevant rules. It does not decide whether your system is legally compliant.</p>

            <button type="button" class="cta-pill" id="install-pill" aria-live="polite" onclick="if(window.plausible)plausible('CTA Click',{props:{type:'install'}});copyPill(this, 'pipx install regula-ai \u0026\u0026 regula')">
                <span>&#9654;</span>
                Try the local scanner
            </button>

            <div style="margin-top:14px;">
                <a href="/assess/" style="color:var(--accent);font-size:0.9rem;text-decoration:underline;text-underline-offset:3px;" onclick="if(window.plausible)plausible('CTA Click',{props:{type:'assess-hero'}})">Prefer no terminal? Assess in your browser &rarr;</a>
            </div>

            <div class="cta-secondary">
                no account or API key for core scanning &middot; scanned files stay local in the core workflow &middot;
        <a href="/guides/">Guides</a>
                <a href="https://github.com/kuzivaai/getregula" style="color:#8888aa;font-size:12px;font-family:'JetBrains Mono',monospace;">GitHub &#8599;</a>
            </div>
            <div class="social-proof">
                <strong style="color:var(--text);">2,690</strong> tests
                <span class="sp-sep" aria-hidden="true">&middot;</span> <strong style="color:var(--text);">0</strong> unexpected security findings
                <span class="sp-sep" aria-hidden="true">&middot;</span> zero dependencies
                <span class="sp-sep" aria-hidden="true">&middot;</span> the local core does not upload scanned files
                <span class="sp-sep" aria-hidden="true">&middot;</span> <a href="https://github.com/kuzivaai/getregula/blob/main/docs/TRUST.md" style="color:#8888aa;">trust pack</a>
            </div>
        </div>

        <!-- TERMINAL -->
        <div class="term-wrap" role="region" aria-label="Interactive Regula CLI demo. Switch tabs to see example output of regula check, plan, gap, and comply commands">
            <div class="term-bar" aria-hidden="true">
                <div class="term-dot td-r"></div>
                <div class="term-dot td-y"></div>
                <div class="term-dot td-g"></div>
            </div>
            <div class="term-tabs" role="tablist" aria-label="Regula command examples">
                <div class="term-tab active" role="tab" id="tab-check-label" tabindex="0" aria-selected="true" aria-controls="tab-check" onclick="switchTab('check', this)" onkeydown="handleTabKey(event, this)">check</div>
                <div class="term-tab" role="tab" id="tab-plan-label" tabindex="-1" aria-selected="false" aria-controls="tab-plan" onclick="switchTab('plan', this)" onkeydown="handleTabKey(event, this)">plan</div>
                <div class="term-tab" role="tab" id="tab-gap-label" tabindex="-1" aria-selected="false" aria-controls="tab-gap" onclick="switchTab('gap', this)" onkeydown="handleTabKey(event, this)">gap</div>
                <div class="term-tab" role="tab" id="tab-comply-label" tabindex="-1" aria-selected="false" aria-controls="tab-comply" onclick="switchTab('comply', this)" onkeydown="handleTabKey(event, this)">comply</div>
            </div>
            <div class="term-body">
                <div class="term-panel active" id="tab-check" role="tabpanel" aria-labelledby="tab-check-label">
                    <pre tabindex="0"><span class="t-p">$</span> <span class="t-c">regula check . --explain</span>

<span class="t-h">Classification: HIGH-RISK</span>
  Annex III, Category 5

<span class="t-y">WHY:</span>
  scoring.py:23 : essential_services
    <span class="t-m">Code: score = model.predict(applicant)</span>
    Legal basis: Annex III : Articles 9-15
    False positive if: not a credit decision

<span class="t-h">ROLE:</span> DEPLOYER (confidence: high)
  <span class="t-m">- OpenAI API usage detected</span>

<span class="t-y">OBLIGATIONS:</span>
  <span class="t-c">[HIGH]</span> Art. 9  Risk management   : 40-60h
  <span class="t-c">[HIGH]</span> Art. 14 Human oversight  : 16-24h
  Total: 160-324h | Deadline: <span class="t-y">Dec 2027</span>
  <span class="t-m">&#9888; Omnibus agreed 7 May 2026, EP approved 16 Jun 2026, Council approved 29 Jun 2026; published in OJ 2026-07-24, in force from 2026-07-27</span></pre>
                </div>
                <div class="term-panel" id="tab-plan" role="tabpanel" aria-labelledby="tab-plan-label">
                    <pre tabindex="0"><span class="t-p">$</span> <span class="t-c">regula plan .</span>

<span class="t-h">COMPLIANCE PLAN  &middot;  HIGH-RISK (Annex III, Category 5)</span>

Priority 1 : Risk Management System (Art. 9)
  Effort: 40&ndash;60h
  <span class="t-r">&times;</span> No risk assessment file found
  <span class="t-r">&times;</span> No model evaluation documented

Priority 2 : Human Oversight (Art. 14)
  Effort: 16&ndash;24h
  <span class="t-r">&times;</span> No review-before-action pattern detected
  <span class="t-r">&times;</span> No override mechanism found

Priority 3 : Technical Documentation (Art. 11)
  Effort: 8&ndash;12h
  <span class="t-g">&#10003;</span> Annex IV template: regula docs .

Total: 64&ndash;96h estimated effort</pre>
                </div>
                <div class="term-panel" id="tab-gap" role="tabpanel" aria-labelledby="tab-gap-label">
                    <pre tabindex="0"><span class="t-p">$</span> <span class="t-c">regula gap tests/fixtures/sample_high_risk</span>

<span class="t-h">EU AI Act Compliance Gap Assessment: sample_high_risk</span>
Highest risk tier: not_ai
Overall score:     6%

  NOTE: This score measures the PRESENCE of compliance
  documentation and infrastructure : it does not assess code
  risk and cannot offset scan findings. A project can score
  100% here and still fail `regula check` on prohibited or
  high-risk patterns. Run both; they answer different questions.

Article 9   Risk Management                     [<span class="t-r">  0%</span>] <span class="t-r">NOT FOUND</span>
Article 10  Data Governance                     [<span class="t-r">  0%</span>] <span class="t-r">NOT FOUND</span>
Article 11  Technical Documentation             [<span class="t-r">  0%</span>] <span class="t-r">NOT FOUND</span>
Article 12  Record-Keeping                      [<span class="t-r">  0%</span>] <span class="t-r">NOT FOUND</span>
Article 13  Transparency                        [<span class="t-r">  0%</span>] <span class="t-r">NOT FOUND</span>
Article 14  Human Oversight                     [<span class="t-y"> 45%</span>] <span class="t-y">PARTIAL</span>
Article 15  Accuracy, Robustness, Cybersecurity [<span class="t-r">  0%</span>] <span class="t-r">NOT FOUND</span>
Article 17  Quality Management System           [<span class="t-r">  0%</span>] <span class="t-r">NOT FOUND</span>

Run: <span class="t-b">regula plan tests/fixtures/sample_high_risk</span> for a prioritised fix list</pre>
                    <p class="term-provenance">Real output, not a mock-up. Reproduce it from a clone with the command shown; the fixture is committed at tests/fixtures/sample_high_risk and this page is diffed against a fresh run by tests/test_gap_demo.py .</p>
                </div>
                <div class="term-panel" id="tab-comply" role="tabpanel" aria-labelledby="tab-comply-label">
                    <pre tabindex="0"><span class="t-p">$</span> <span class="t-c">regula comply tests/fixtures/sample_high_risk --all</span>

<span class="t-h">EU AI Act Compliance Checklist: sample_high_risk</span>
  Overall compliance score: 6/100
  Highest risk tier:        not_ai (showing all articles per --all flag)

  [<span class="t-r">&times;</span>] Article 9   Risk Management                       <span class="t-r">0%</span> <span class="t-r">NOT FOUND</span>
  [<span class="t-r">&times;</span>] Article 10  Data Governance                       <span class="t-r">0%</span> <span class="t-r">NOT FOUND</span>
  [<span class="t-r">&times;</span>] Article 11  Technical Documentation               <span class="t-r">0%</span> <span class="t-r">NOT FOUND</span>
  [<span class="t-r">&times;</span>] Article 12  Record-Keeping                        <span class="t-r">0%</span> <span class="t-r">NOT FOUND</span>
  [<span class="t-r">&times;</span>] Article 13  Transparency                          <span class="t-r">0%</span> <span class="t-r">NOT FOUND</span>
  [<span class="t-r">&times;</span>] Article 14  Human Oversight                      <span class="t-y">45%</span> <span class="t-y">NEEDS WORK</span>
  [<span class="t-r">&times;</span>] Article 15  Accuracy, Robustness, Cybersecurity   <span class="t-r">0%</span> <span class="t-r">NOT FOUND</span>
  [<span class="t-r">&times;</span>] Article 17  Quality Management System             <span class="t-r">0%</span> <span class="t-r">NOT FOUND</span>

  0/8 high-risk obligations have strong evidence

Run: <span class="t-b">regula comply --article 9</span> for deep-dive</pre>
                    <p class="term-provenance">Real output, not a mock-up. <code>--all</code> is required here: without it the command prints no article table for this fixture, because the project classifies as not_ai. Bound to tests/test_gap_demo.py .</p>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
  // Flip panel transitions on AFTER the first paint so the terminal does
  // not play its 0→1 opacity fade on page load. Uses requestAnimationFrame
  // rather than DOMContentLoaded so the class lands just after the browser
  // has committed initial styles :  guaranteed no flash.
  requestAnimationFrame(function () {
      requestAnimationFrame(function () {
          document.body.classList.add('term-panels-ready');
      });
  });
</script>

<!-- WHO IS THIS FOR -->
<div class="sec reveal">
    <h2 class="sec-head">Who is this for?</h2>
    <p class="sec-sub">Developers shipping AI products, and the businesses that use them.</p>
    <div class="audience-grid">
        <div class="audience-card audience-biz">
            <div class="audience-label">If you run the business</div>
            <h3>Start with deployment context</h3>
            <p>If your team builds or uses AI, jurisdiction, intended purpose, role and deployment context determine which rules may apply. Record that context in <code>regula assess</code>, then have the result reviewed by the appropriate technical and legal owners.</p>
            <button type="button" class="audience-fwd" onclick="copyPageUrl(this)">
                <span class="fwd-icon">&#8599;</span>
                <span class="fwd-txt">Copy link to send to your developer</span>
            </button>
            <a class="audience-fwd" href="/assess/" onclick="if(window.plausible)plausible('CTA Click',{props:{type:'assess-biz'}})">
                <span class="fwd-icon">&#8594;</span>
                <span class="fwd-txt">Assess in your browser (no install, no terminal)</span>
            </a>
        </div>
        <div class="audience-card audience-dev">
            <div class="audience-label">If you write the code</div>
            <h3>Review patterns found in the code</h3>
            <p>Article 2 includes circumstances in which the Act applies outside the EU, but applicability and risk classification cannot be settled from source code alone. Use the scan to locate evidence and questions for contextual review.</p>
            <ul>
                <li>Works on AI-generated code (Cursor, Lovable, Bolt, Claude Code)</li>
                <li>Generates Annex IV documentation from your actual code</li>
                <li>CI/CD integration &middot; JSON &middot; SARIF &middot; 13 compliance frameworks</li>
            </ul>
            <span class="step-cmd" style="margin-top:18px;">regula check .</span>
        </div>
        <div class="audience-card audience-audit">
            <div class="audience-label">If you audit compliance</div>
            <h3>Reviewable evidence scaffolds</h3>
            <p>Regula can generate evidence-pack scaffolds with SHA-256 manifests; optional commands can add signatures or timestamps when their prerequisites are configured. Packs require human completion and do not establish legal sufficiency. <a href="/sample-report.html" onclick="if(window.plausible)plausible('CTA Click',{props:{type:'sample-report'}})">See a sample report &rarr;</a> &middot; <a href="/pricing.html">Evidence pack tiers &rarr;</a></p>
            <button type="button" class="audience-fwd" aria-live="polite" onclick="copyPill(this, 'pipx install regula-ai &amp;&amp; regula conform --sign .')">
                <span class="fwd-icon">&#9654;</span>
                <span class="fwd-txt">regula conform --sign .</span>
            </button>
        </div>
    </div>
</div>

<div class="sep"></div>

<!-- WHAT REGULA TELLS YOU -->
<div class="sec reveal" id="tiers">
    <h2 class="sec-head">What Regula tells you</h2>
    <p class="sec-sub">The EU AI Act uses risk-based rules whose application depends on intended purpose and deployment context. Regula reports candidate indicators and related provisions for human review; it does not decide the legal tier.</p>
    <div class="tiers">
        <div class="tier tier-r">
            <div class="tier-badge">Prohibited</div>
            <div class="tier-examples">Social scoring &middot; Emotion inference &middot; Real-time biometrics &middot; Subliminal manipulation</div>
            <div class="tier-hint">Article 5 prohibited-practice indicator &rarr;</div>
        </div>
        <div class="tier tier-a">
            <div class="tier-badge">High-Risk</div>
            <div class="tier-examples">Credit scoring &middot; Hiring &middot; Healthcare services &middot; Education &middot; Law enforcement</div>
            <div class="tier-hint">Related Articles 9&ndash;15 &rarr;</div>
        </div>
        <div class="tier tier-y">
            <div class="tier-badge">Limited Risk</div>
            <div class="tier-examples">Chatbots &middot; Synthetic content &middot; Emotion recognition &middot; Deep fakes</div>
            <div class="tier-hint">Transparency rules &rarr;</div>
        </div>
        <div class="tier tier-g">
            <div class="tier-badge">No elevated indicator</div>
            <div class="tier-examples">No Article 5, Annex III, or Article 50 pattern detected</div>
            <div class="tier-hint">No AI-Act duty inferred from code alone &rarr;</div>
        </div>
    </div>
    <p class="tier-cta">Regula shows which code evidence triggered a candidate indicator and what context a reviewer still needs.</p>
</div>

<div class="urgency">
    <div class="urgency-box" role="note">
        <div class="date">2026&ndash;27</div>
        <div class="body"><strong>Current enacted timeline:</strong> Regulation (EU) 2026/1744 entered into force on 27 July 2026. Annex III high-risk rules apply from 2 December 2027 and Annex I product-embedded high-risk rules from 2 August 2028. Other provisions have different dates and conditions; review the amended legislation for the system in question.</div>
    </div>
</div>

<div class="sep"></div>

<!-- HOW IT WORKS -->
<div class="sec reveal" id="how">
    <h2 class="sec-head">How it works</h2>
    <p class="sec-sub">Three steps. Core scanning requires no account or API key; optional network-enabled features have separate boundaries.</p>
    <div class="art-grid">
        <div class="card-base art-card" style="text-align:center;">
            <div class="tag tag-blue">Step 1</div>
            <h3>Install</h3>
            <p><code>pipx install regula-ai</code><br>Requires Python 3.10 or later; see the tested installation paths. <a href="https://github.com/kuzivaai/getregula/blob/main/docs/installation.md" style="color:#8888aa;">Installation guide &#8599;</a></p>
        </div>
        <div class="card-base art-card" style="text-align:center;">
            <div class="tag tag-blue">Step 2</div>
            <h3>Scan</h3>
            <p><code>regula</code><br>Indicator summary, findings, and suggested next steps.</p>
        </div>
        <div class="card-base art-card" style="text-align:center;">
            <div class="tag tag-blue">Step 3</div>
            <h3>Act</h3>
            <p><code>regula comply</code><br>Checklist of documentation and controls found for each article.</p>
        </div>
    </div>
</div>

<!-- STATS BAR -->
<div class="stats-bar reveal">
    <div class="stats-inner">
        <div class="stat-item">
            <div class="stat-num">419</div>
            <div class="stat-label">risk patterns <a href="https://github.com/kuzivaai/getregula/blob/main/scripts/risk_patterns.py" class="stat-source">(source)</a></div>
        </div>
        <div class="stat-item">
            <div class="stat-num">8</div>
            <div class="stat-label">programming languages</div>
        </div>
        <div class="stat-item">
            <div class="stat-num">13</div>
            <div class="stat-label">compliance frameworks <a href="https://github.com/kuzivaai/getregula/blob/main/references/framework_crosswalk.yaml" class="stat-source">(source)</a></div>
        </div>
        <div class="stat-item">
            <div class="stat-num">0</div>
            <div class="stat-label">runtime dependencies</div>
        </div>
    </div>
</div>

<div class="sep"></div>

<!-- FEATURES (moved before competitive comparison per UX research: users should understand capabilities before seeing how they compare) -->
<div class="sec reveal" id="features">
    <h2 class="sec-head">What it does</h2>
    <p class="sec-sub">Regula combines code scanning with governance questionnaires. It reads your code for risk patterns, and provides structured self-assessments for the organisational obligations code cannot verify. It generates artefacts an auditor can review, not just findings.</p>

    <div class="feature-category">Assess</div>
    <div class="art-grid">
        <div class="card-base art-card">
            <div class="tag tag-blue">Gaps</div>
            <h3>What's missing?</h3>
            <p>Risk management, data governance, logging, transparency, human oversight, accuracy. Scored per article with effort estimates.</p>
            <code style="font-size:11px;color:#9898b4;">regula gap .</code>
        </div>
        <div class="card-base art-card">
            <div class="tag tag-purple">Security</div>
            <h3>Is your AI code secure?</h3>
            <p>Prompt injection, unsafe model loading, unvalidated AI output, hardcoded keys, and other AI-specific vulnerabilities.</p>
            <code style="font-size:11px;color:#9898b4;">regula check . &middot; regula guardrails .</code>
        </div>
        <div class="card-base art-card">
            <div class="tag tag-blue">Oversight</div>
            <h3>Human review analysis</h3>
            <p>Traces AI outputs across files. Checks whether each path to a user-facing endpoint passes through a human review gate.</p>
            <code style="font-size:11px;color:#9898b4;">regula oversight .</code>
        </div>
    </div>

    <div class="feature-category">Evidence</div>
    <div class="art-grid">
        <div class="card-base art-card">
            <div class="tag tag-blue">Documentation</div>
            <h3>Need evidence for review?</h3>
            <p>Annex IV technical documentation generated from your actual code. Functions, dependencies, and logging coverage pre-populated.</p>
            <code style="font-size:11px;color:#9898b4;">regula docs . &middot; regula conform .</code>
        </div>
        <div class="card-base art-card">
            <div class="tag tag-purple">Evidence</div>
            <h3>Conformity assessment pack</h3>
            <p>Article 43 evidence pack mapped to Articles 9&ndash;15, with per-article readiness scores and SHA-256 integrity hashes. <a href="https://github.com/kuzivaai/getregula/blob/main/docs/evidence-pack-guide.md">Evidence-pack specification</a>.</p>
            <code style="font-size:11px;color:#9898b4;">regula conform . &middot; regula evidence-pack .</code>
        </div>
        <div class="card-base art-card">
            <div class="tag tag-purple">Integrity</div>
            <h3>Integrity checks and optional signatures</h3>
            <p>SHA-256 manifests, Ed25519 signatures, and RFC 3161 timestamps can help reviewers check when an assessment was produced and whether files changed afterward.</p>
            <code style="font-size:11px;color:#9898b4;">regula conform --sign --timestamp .</code>
        </div>
    </div>

    <div class="feature-category">Integrate</div>
    <div class="art-grid">
        <div class="card-base art-card">
            <div class="tag tag-blue">Multi-jurisdiction</div>
            <h3>3 jurisdictions, one scan</h3>
            <p>Beyond the EU AI Act: the same scan maps findings to South Korea's AI Basic Act (Act No. 20676, in force 22 January 2026) and Colorado SB 26-189 (disclosure-focused, duties from 1 January 2027), each with its own domain-to-obligation mapping and questionnaire.</p>
            <code style="font-size:11px;color:#9898b4;">regula check . --jurisdictions eu,korea,colorado</code>
        </div>
        <div class="card-base art-card">
            <div class="tag tag-blue">Cross-regulation</div>
            <h3>13 framework mappings</h3>
            <p>Each AI Act article is mapped to ISO 42001, NIST AI RMF, SOC 2, OWASP, and 8 other framework obligations. One scan surfaces requirements across all 13 frameworks.</p>
            <code style="font-size:11px;color:#9898b4;">regula gap .</code>
        </div>
    </div>

    <p style="font-size:12px;color:#9898b4;margin-top:24px;font-family:'JetBrains Mono',monospace;text-align:center;">
        62 commands total &middot; Python, JS, TS, Java, Go, Rust, C, C++ &middot; Cross-maps to ISO 42001, NIST AI RMF, OWASP LLM Top 10, EU CRA, and 9 other frameworks.
        <a href="https://github.com/kuzivaai/getregula/blob/main/docs/cli-reference.md" style="color:#8888aa;margin-left:4px;">Full CLI reference &rarr;</a>
    </p>
</div>

<div class="sep"></div>

<!-- RUNS WHERE YOU WORK -->
<div class="sec reveal" id="integrations">
    <h2 class="sec-head">Runs where you work</h2>
    <p class="sec-sub">Terminal, CI/CD, editor, pre-commit. One tool, every workflow.</p>
    <div class="art-grid">
        <div class="card-base art-card">
            <h3>Terminal</h3>
            <p><code>pipx install regula-ai &amp;&amp; regula check .</code></p>
        </div>
        <div class="card-base art-card">
            <h3>CI/CD</h3>
            <p>GitHub Action: <code>kuzivaai/getregula@v1</code> with SARIF upload</p>
        </div>
        <div class="card-base art-card">
            <h3>VS Code</h3>
            <p>Inline WARN/BLOCK decorators. Scan on save.</p>
        </div>
        <div class="card-base art-card">
            <h3>Claude Code / Cursor</h3>
            <p>MCP server: <code>regula mcp-server</code></p>
        </div>
        <div class="card-base art-card">
            <h3>Pre-commit</h3>
            <p><code>regula install pre-commit</code></p>
        </div>
        <div class="card-base art-card">
            <h3>GDPR dual-compliance</h3>
            <p><code>regula gdpr</code> : GDPR-related code indicators and AI Act/GDPR hotspots. <a href="https://github.com/kuzivaai/getregula/blob/main/scripts/risk_patterns.py">Pattern source</a>.</p>
        </div>
    </div>
</div>

<div class="sep"></div>

<!-- WHERE REGULA FITS -->
<details class="sec-disclose">
    <summary><h2 class="sec-head">Where Regula fits in the market</h2></summary>
    <div class="sec-disclose-body">
    <p class="sec-sub">Code scanning plus governance questionnaires. One of several tools in the EU AI Act ecosystem. Each solves a different part of the problem.</p>
    <div class="pricing-grid">
        <div class="price-card">
            <div class="price-tier">Governance SaaS</div>
            <div class="price-amount">Contact sales</div>
            <p class="price-desc">Credo AI, Saidot, Enzai, IBM watsonx.governance, Microsoft Purview. Evidence workflows, control libraries, continuous monitoring, legal-expert policy updates. Built for compliance departments, not developers. No published pricing.</p>
        </div>
        <div class="price-card">
            <div class="price-tier">Runtime testing</div>
            <div class="price-amount">Open source</div>
            <p class="price-desc">Garak, Giskard, Promptfoo. Prompt-injection, jailbreak and bias red-teaming against running models. Complementary to Regula, not overlapping. They test behaviour; Regula reads code.</p>
        </div>
        <div class="price-card featured">
            <div class="price-tier price-featured-tier">Regula</div>
            <div class="price-amount price-featured-amount">Free &amp; open source</div>
            <p class="price-desc">Code scanning plus governance questionnaires. The stdlib-only core scans local files without uploading them; optional features have separate dependency and network boundaries. <code>pipx install regula-ai</code>, inspect the indicators, then complete contextual human review. Apache 2.0 / EUPL 1.2; detection rules under DRL 1.1.</p>
        </div>
    </div>
    <div role="region" aria-label="Competitive comparison of EU AI Act compliance tools" style="overflow-x:auto;margin-top:32px;-webkit-overflow-scrolling:touch;">
    <p class="scroll-hint" style="display:none;font-size:11px;color:var(--text-dim);margin-bottom:8px;text-align:right;">Scroll &rarr;</p>
    <table class="cmp-table" style="width:100%;border-collapse:collapse;font-size:13px;color:#b0b0cc;">
        <caption class="sr-only">Feature comparison of EU AI Act compliance tools: Regula, AIR Blackbox, Systima Comply, EuConform, and Enterprise SaaS</caption>
        <thead>
            <tr style="border-bottom:1px solid #23234a;text-align:left;">
                <th scope="col" style="padding:8px 12px;"><span class="sr-only">Feature</span></th>
                <th scope="col" style="padding:8px 12px;">Regula</th>
                <th scope="col" style="padding:8px 12px;">AIR Blackbox</th>
                <th scope="col" style="padding:8px 12px;">Systima Comply</th>
                <th scope="col" style="padding:8px 12px;">EuConform</th>
                <th scope="col" style="padding:8px 12px;">Enterprise SaaS</th>
            </tr>
        </thead>
        <tbody>
            <tr><th scope="row" style="padding:6px 12px;color:#e0e0f0;font-weight:400;text-align:left;">Approach</th><td>Static code scan</td><td>Scan + runtime trust layers</td><td>AST-based scan</td><td>Questionnaire + bias eval</td><td>Platform / dashboard</td></tr>
            <tr style="background:#0d0d1a;"><th scope="row" style="padding:6px 12px;color:#e0e0f0;font-weight:400;text-align:left;">Languages</th><td>8 families</td><td>Python</td><td>JS/TS/Python</td><td>Not a code scanner</td><td>Not a code scanner</td></tr>
            <tr><th scope="row" style="padding:6px 12px;color:#e0e0f0;font-weight:400;text-align:left;">Detection patterns</th><td>419</td><td>51 checks</td><td>37+ frameworks</td><td>Questionnaire</td><td>Varies</td></tr>
            <tr style="background:#0d0d1a;"><th scope="row" style="padding:6px 12px;color:#e0e0f0;font-weight:400;text-align:left;">Dependencies</th><td>Zero (stdlib)</td><td>Multiple</td><td>npm</td><td>Next.js + Ollama</td><td>SaaS</td></tr>
            <tr><th scope="row" style="padding:6px 12px;color:#e0e0f0;font-weight:400;text-align:left;">Data path</th><td>Local core; optional features vary</td><td>Local</td><td>Local</td><td>Local + Ollama</td><td>Cloud</td></tr>
            <tr style="background:#0d0d1a;"><th scope="row" style="padding:6px 12px;color:#e0e0f0;font-weight:400;text-align:left;">Evidence signing</th><td>Ed25519 + RFC 3161</td><td>Ed25519 (opt-in)</td><td>:</td><td>:</td><td>Varies</td></tr>
            <tr><th scope="row" style="padding:6px 12px;color:#e0e0f0;font-weight:400;text-align:left;">Framework mappings</th><td>13</td><td>3</td><td>EU AI Act</td><td>EU AI Act</td><td>Multiple</td></tr>
            <tr style="background:#0d0d1a;"><th scope="row" style="padding:6px 12px;color:#e0e0f0;font-weight:400;text-align:left;">CI/CD integration</th><td>GitHub Action + SARIF</td><td>GitHub Action</td><td>GitHub Action</td><td>:</td><td>Native</td></tr>
            <tr><th scope="row" style="padding:6px 12px;color:#e0e0f0;font-weight:400;text-align:left;">Annex IV docs</th><td>Free</td><td>:</td><td>:</td><td>PDF reports</td><td>Built-in</td></tr>
            <tr style="background:#0d0d1a;"><th scope="row" style="padding:6px 12px;color:#e0e0f0;font-weight:400;text-align:left;">Price</th><td>Free (Apache 2.0 / EUPL 1.2)</td><td>Free (Apache 2.0)</td><td>Free (Apache 2.0)</td><td>Free (MIT)</td><td>Typically unpublished</td></tr>
        </tbody>
    </table>
    </div>
    <p style="font-size:12px;color:var(--text-dim);margin-top:12px;">Pick the tool whose language coverage and trade-offs fit your stack. Regula covers the most languages and framework mappings among the open-source options listed above. For <em>runtime</em> agent governance, see <a href="https://github.com/microsoft/agent-governance-toolkit" rel="noopener" style="color:var(--text-dim);">Microsoft&rsquo;s Agent Governance Toolkit</a>. <!-- Comparison table last verified: 13 June 2026. AIR Blackbox: github.com/airblackbox/airblackbox (51+ checks, 17 stars, Apache-2.0, last push 11 Jun 2026). Systima: github.com/systima-ai/comply (JS/TS/Python, 0 stars, last push 25 May 2026). EuConform: github.com/Hiepler/EuConform (MIT, 119 stars, last push 27 Apr 2026). All verified via GitHub API. --></p>
</div>
</details>

<div class="sep"></div>

<!-- HONESTY :  WHAT REGULA DOES AND DOESN'T DO -->
<div class="sec reveal">
    <h2 class="sec-head">What Regula does not do</h2>
    <p class="sec-sub">A compliance tool that overstates its capabilities is worse than no tool at all. Here is what Regula actually is, and what it isn't.</p>
    <div class="art-grid">
        <div class="card-base art-card">
            <h3>Not legal advice</h3>
            <p>Regula identifies risk indicators in code for developer review. It does not determine compliance. A qualified legal professional should review any classification before you act on it.</p>
        </div>
        <div class="card-base art-card">
            <h3>Pattern matching, not understanding</h3>
            <p>83.5% precision on production code (blind-labelled random corpus, N=115, Python only, measured on v1.7.0, labelled by a single reviewer with no inter-rater agreement measurement). 15.2% on AI library source code :  the hardest corpus, since those libraries implement AI rather than using it for regulated decisions. <a href="https://github.com/kuzivaai/getregula/blob/main/docs/benchmarks/PRECISION_RECALL_2026_04.md" style="color:#8888aa;">Published benchmark &rarr;</a></p>
        </div>
        <div class="card-base art-card">
            <h3>Scaffolds, not substance</h3>
            <p>Annex IV docs, evidence packs, and governance frameworks are pre-filled scaffolds. A human must complete them with substantive content. Regula cannot verify that a risk management system actually operates.</p>
        </div>
    </div>
    <p class="sec-sub" style="margin-top:24px;font-size:13px;"><a href="https://github.com/kuzivaai/getregula/blob/main/docs/what-regula-does-not-do.md" style="color:#8888aa;">Full limitations disclosure &rarr;</a></p>
</div>

<div class="sep"></div>

<!-- BLOG -->
<div class="sec reveal">
    <h2 class="sec-head">Guides &amp; analysis</h2>
    <p class="sec-sub">Technical guides for developers and analysis of AI regulation.</p>
    <div class="art-grid" style="margin-bottom:32px;">
        <a href="/guides/eu-ai-act-python.html" class="card-base art-card">
            <div class="tag tag-blue">Guide</div>
            <h3>EU AI Act for Python Developers</h3>
            <p>Scan Python AI code for risk patterns. PyTorch, TensorFlow, scikit-learn, LangChain.</p>
        </a>
        <a href="/guides/article-9-risk-management.html" class="card-base art-card">
            <div class="tag tag-blue">Guide</div>
            <h3>Article 9: Risk Management System</h3>
            <p>What the regulation requires, what code scanning can detect, and what needs human review.</p>
        </a>
        <a href="/guides/eu-ai-act-healthcare.html" class="card-base art-card">
            <div class="tag tag-blue">Guide</div>
            <h3>EU AI Act for Healthcare AI</h3>
            <p>Medical devices, clinical decision support, and the MDR/IVDR intersection.</p>
        </a>
        <a href="/guides/article-5-prohibited-practices.html" class="card-base art-card">
            <div class="tag tag-blue">Guide</div>
            <h3>Article 5: Prohibited Practices</h3>
            <p>The 10 practices banned under Article 5, including the Omnibus additions.</p>
        </a>
    </div>
    <p style="text-align:center;margin-bottom:32px;font-size:13px;"><a href="/blog/writing.html" style="color:#8888aa;">All 8 guides &amp; 14 articles &rarr;</a></p>
    <div class="art-grid">
        <a href="/blog/blog-omnibus-trilogue-failed.html" class="card-base art-card">
            <div class="tag tag-purple">Trilogue</div>
            <h3>The Omnibus Trilogue Failed (April 2026): A Post-Mortem</h3>
            <p>The first political trilogue ended without agreement on 28 April after 12 hours. The follow-up trilogue succeeded on 7 May; Parliament and Council approved the December 2027 deferral in June 2026.</p>
        </a>
        <a href="/blog/blog-code-scanning-vs-questionnaires.html" class="card-base art-card">
            <div class="tag tag-purple">Analysis</div>
            <h3>Questionnaires vs Code Scanning</h3>
            <p>Questionnaires capture what you said. Code scanning shows what you did. Neither replaces the other.</p>
        </a>
        <a href="/blog/blog-does-ai-act-apply.html" class="card-base art-card">
            <div class="tag tag-blue">Applicability</div>
            <h3>Does the EU AI Act Apply to Your AI App?</h3>
            <p>Five questions to check whether your product falls under EU AI Act scope.</p>
        </a>
        <a href="/blog/blog-risk-tiers-in-code.html" class="card-base art-card">
            <div class="tag tag-purple">Code</div>
            <h3>EU AI Act Risk Tiers in Actual Code</h3>
            <p>What prohibited, high-risk, and limited-risk indicators look like in real code.</p>
        </a>
        <a href="/blog/blog-startups-ignoring-ai-act.html" class="card-base art-card">
            <div class="tag tag-blue">Adoption</div>
            <h3>Most Startups Are Ignoring the AI Act</h3>
            <p>Why that's rational today, three triggers for when it stops being rational, and what preparing actually means.</p>
        </a>
    </div>
</div>

<!-- FAQ (visible :  content mirrors the FAQPage schema for GEO extractability) -->
<div class="sep"></div>
<div class="sec reveal" id="faq">
    <h2 class="sec-head">Common questions</h2>
    <p class="sec-sub">Answers grounded in the regulation. Every claim cites a specific Article.</p>
    <div class="faq" style="max-width:760px;margin:0 auto;">
        <details>
            <summary>Does the EU AI Act apply to my company if I'm outside the EU?</summary>
            <p>Potentially. Article 2(1)(c) covers providers and deployers established outside the EU where an AI system's output is used in the Union, subject to the Act's roles, exclusions, and other scope conditions. Location alone does not decide applicability.</p>
        </details>
        <details>
            <summary>Is my AI app prohibited under the EU AI Act?</summary>
            <p>Article 5 prohibits specified practices, including certain forms of social scoring, manipulation, biometric identification, and emotion inference. The exact scope, conditions, and exceptions matter. Regula flags related code patterns for review; it does not determine that a prohibited practice exists.</p>
        </details>
        <details>
            <summary>What makes an AI system high-risk?</summary>
            <p>Article 6 contains the classification routes and Annex III lists specified intended uses across eight areas. Conditions, exceptions, intended purpose, and deployment context matter. Regula reports related code indicators but does not determine high-risk status.</p>
        </details>
        <details>
            <summary>When does the EU AI Act start being enforced?</summary>
            <p>The original Article 5 prohibitions have applied since 2 February 2025. GPAI provisions began applying on 2 August 2025, subject to transition rules. Regulation (EU) 2026/1744 sets 2 December 2027 for Annex III and 2 August 2028 for the Annex I product path. Article 50 generally has applied since 2 August 2026, with a specific transition for providers of Article 50(2) systems already on the market.</p>
        </details>
        <details>
            <summary>What are the fines under the EU AI Act?</summary>
            <p>Article 99 provides for fines up to &euro;35 million or 7% of global annual turnover for prohibited-practice infringements; up to &euro;15 million or 3% for certain other infringements; and up to &euro;7.5 million or 1% for supplying incorrect, incomplete, or misleading information. <a href="https://eur-lex.europa.eu/eli/reg/2024/1689/oj" rel="noopener">Read Article 99 in the primary legislation</a>.</p>
        </details>
        <details>
            <summary>Is Regula free?</summary>
            <p>Yes. Regula is open-source under the Apache 2.0 or EUPL 1.2 licence. No account or API key is required for local use. Install with <code>pipx install regula-ai</code> and run it locally. <a href="https://github.com/kuzivaai/getregula/blob/main/docs/cli-reference.md">The CLI reference</a> and <a href="https://github.com/kuzivaai/getregula/blob/main/references/framework_crosswalk.yaml">framework crosswalk</a> document the shipped surface.</p>
        </details>
        <details>
            <summary>Does the EU AI Act overlap with GDPR, DORA, or NIS2?</summary>
            <p>Yes, significantly. High-risk AI systems that process personal data must also comply with GDPR, and other regulations like DORA and NIS2 may apply depending on your sector. Regula cross-maps AI Act obligations to ISO 42001, NIST AI RMF, SOC 2, OWASP, and 9 other frameworks in a single scan.</p>
        </details>
        <details>
            <summary>Does Regula work with AI-generated code?</summary>
            <p>Yes. Regula scans source files regardless of who or what wrote them. Authorship alone does not determine whether the EU AI Act applies: Article 2 scope, the actor's role, intended purpose, deployment context, and applicable exclusions still require review. Run <code>regula check .</code> for code-observable indicators and <code>regula assess</code> to record context.</p>
        </details>
        <details>
            <summary>What should I do right now to prepare?</summary>
            <p>Install with <code>pipx install regula-ai</code>, use <code>regula assess</code> to record declared context, then run <code>regula check .</code> for code-observable indicators. Human review is required; these outputs do not determine legal classification or compliance.</p>
        </details>
    </div>
</div>

<div class="sep"></div>

<!-- FINAL CTA -->
<div class="final-wrap">
    <div class="final-glow"></div>
    <div class="final reveal">
        <h2>Find out where you stand</h2>
        <p>One command; runtime varies by repository and environment. No account is needed for core scanning.</p>
        <button type="button" class="install-box" id="install-btn-2" onclick="copyInstall(this)" style="display:inline-flex;">
            <span class="dollar">$</span>
            <span class="cmd">pipx install regula-ai</span>
            <span class="cp" aria-live="polite">copy</span>
        </button>
        <p style="font-size:13px;color:var(--text-dim);margin:24px 0 12px;">Not ready to install? Get notified when deadlines change.</p>
        <div data-fs-success style="display:none;font-size:13px;color:#10b981;margin-bottom:8px;">You're on the list. Major releases only.</div>
        <div data-fs-error style="display:none;font-size:13px;color:#ef4444;margin-bottom:8px;"></div>
        <form id="notify-form" class="notify">
            <input type="email" id="notify-email" name="email" placeholder="your@email.com" aria-label="Email for updates" data-fs-field required>
            <span data-fs-error="email" style="font-size:11px;color:#ef4444;"></span>
            <button type="submit" data-fs-submit-btn>Get updates</button>
        </form>
        <p class="notify-msg">No spam. Major releases and EU AI Act deadline reminders only.</p>
    </div>
</div>

</main>

<!-- FOOTER -->
<footer>
    <div class="foot">
        <div class="foot-inner">
            <div class="foot-left">
                <div class="foot-brand">Regula</div>
                <div class="foot-links">
        <a href="/guides/">Guides</a>
                    <a href="https://github.com/kuzivaai/getregula">GitHub</a>
                    <a href="https://pypi.org/project/regula-ai/">PyPI</a>
                    <a href="https://github.com/kuzivaai/getregula/blob/main/docs/TRUST.md">Trust pack</a>
                    <a href="/pricing.html">Evidence packs</a>
                    <a href="https://github.com/kuzivaai/getregula/blob/main/docs/SUPPORT_SLA.md">Support policy</a>
                    <a href="https://github.com/kuzivaai/getregula/blob/main/docs/benchmarks/PRECISION_RECALL_2026_04.md">Benchmarks</a>
                    <a href="https://github.com/kuzivaai/getregula/blob/main/SECURITY.md">Security</a>
                    <a href="https://github.com/kuzivaai/getregula/blob/main/CONTRIBUTING.md">Contributing</a>
                    <a href="/regions/uae.html">UAE &amp; GCC</a>
                    <a href="/regions/brazil-ai-regulation.html">Brazil : LGPD &amp; Marco Legal</a>
                    <a href="mailto:support@getregula.com">support@getregula.com</a>
                </div>
                <div class="foot-copy">Open source &middot; Apache 2.0 / EUPL 1.2 (code); <a href="https://github.com/kuzivaai/getregula/blob/main/NOTICE" class="foot-muted-link">detection rules under DRL 1.1</a> &middot; &copy; 2026 Regula &middot; <a href="mailto:support@getregula.com" class="foot-muted-link">support@getregula.com</a></div>
            </div>
            <div class="foot-middle">
                <div class="foot-col-head">Reading</div>
                <div class="foot-col-links">
                    <a href="/blog/blog-static-analysis-ai-compliance.html">Code scanning vs questionnaires <span class="muted">Why you need both for EU AI Act compliance</span></a>
                    <a href="/blog/blog-classify-ai-system.html">How to review your AI system context <span class="muted">Article 6 routes, candidate risk categories, and limits</span></a>
                    <a href="/blog/blog-art50-code-of-practice.html">Art 50 Code of Practice mapping <span class="muted">What the 10 June 2026 final code means for your codebase</span></a>
                    <a href="/blog/blog-aicdi-governance-gaps.html">AICDI corporate governance gaps <span class="muted">How Regula maps to the 2026 UNESCO/TRF report</span></a>
                    <a href="/guides/eu-ai-act-python.html">EU AI Act for Python developers <span class="muted">Scan Python AI code for risk patterns</span></a>
                    <a href="/guides/eu-ai-act-javascript.html">EU AI Act for JavaScript developers <span class="muted">Node.js, browser, TypeScript</span></a>
                    <a href="/guides/eu-ai-act-recruitment-hiring.html">EU AI Act for recruitment AI <span class="muted">Annex III Category 4 hiring obligations</span></a>
                </div>
            </div>
            <div class="foot-right">
                <div class="foot-legal">
                    <strong>Not legal advice.</strong> Regula identifies regulatory risk indicators in code for developer review. It does not constitute legal advice, and its output should not be relied upon as a definitive compliance determination. Consult a qualified legal professional for legal questions.
                </div>
            </div>
        </div>
    </div>
</footer>

<script>
    // ===== NAV SCROLL =====
    function updateNav() {
        document.getElementById('nav').classList.toggle('scrolled', window.scrollY > 20);
    }

    window.addEventListener('scroll', () => {
        updateNav();
    }, { passive: true });

    // ===== TERMINAL TABS =====
    // Swap the currently-active tab and panel directly, rather than first
    // deactivating ALL of them. The old approach briefly left zero panels
    // with `.active`, so the outgoing panel started its opacity-fade to 0
    // *before* the incoming one started fading in :  visible as a flash.
    function switchTab(name, el) {
        const currentTab = document.querySelector('.term-tab.active');
        const currentPanel = document.querySelector('.term-panel.active');
        const nextPanel = document.getElementById('tab-' + name);
        if (!nextPanel || currentPanel === nextPanel) return;
        if (currentTab && currentTab !== el) {
            currentTab.classList.remove('active');
            currentTab.setAttribute('aria-selected', 'false');
            currentTab.setAttribute('tabindex', '-1');
        }
        if (currentPanel) currentPanel.classList.remove('active');
        el.classList.add('active');
        el.setAttribute('aria-selected', 'true');
        el.setAttribute('tabindex', '0');
        el.focus();
        nextPanel.classList.add('active');
    }

    function handleTabKey(e, el) {
        const tabs = Array.from(document.querySelectorAll('.term-tab'));
        const i = tabs.indexOf(el);
        if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {
            e.preventDefault();
            const next = tabs[(i + 1) % tabs.length];
            switchTab(next.textContent, next);
        } else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
            e.preventDefault();
            const prev = tabs[(i - 1 + tabs.length) % tabs.length];
            switchTab(prev.textContent, prev);
        } else if (e.key === 'Home') {
            e.preventDefault();
            switchTab(tabs[0].textContent, tabs[0]);
        } else if (e.key === 'End') {
            e.preventDefault();
            switchTab(tabs[tabs.length - 1].textContent, tabs[tabs.length - 1]);
        } else if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            switchTab(el.textContent, el);
        }
    }

    // ===== COPY BUTTON =====
    function copyInstall(el) {
        const cp = el.querySelector('.cp');
        navigator.clipboard.writeText('pipx install regula-ai').then(() => {
            el.classList.add('copied');
            cp.innerHTML = '&#10003;&nbsp;copied';
            setTimeout(() => {
                el.classList.remove('copied');
                cp.textContent = 'copy';
            }, 2000);
        }).catch(() => {
            cp.textContent = 'copy failed';
            setTimeout(() => { cp.textContent = 'copy'; }, 2000);
        });
    }

    // ===== COPY ARBITRARY COMMAND =====
    // ===== PILL BUTTON COPY =====
    function copyPill(el, cmd) {
        const original = el.innerHTML;
        navigator.clipboard.writeText(cmd).then(() => {
            el.classList.add('copied');
            el.innerHTML = '<span>&#10003;</span> Copied! Paste it in your terminal';
            setTimeout(() => {
                el.classList.remove('copied');
                el.innerHTML = original;
            }, 2500);
        }).catch(() => {
            el.innerHTML = '<span>&#9888;</span> Copy failed. Type:' + cmd;
            setTimeout(() => { el.innerHTML = original; }, 2500);
        });
    }

    // ===== COPY PAGE URL (for business owner CTA) =====
    function copyPageUrl(el) {
        navigator.clipboard.writeText('https://getregula.com').then(() => {
            const txt = el.querySelector('.fwd-txt');
            txt.textContent = '✓ Link copied! Send it to your developer';
            setTimeout(() => { txt.textContent = 'Copy link to send to your developer'; }, 3000);
        });
    }

    // ===== SCROLL REVEAL =====
    const revealObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                // Don't unobserve :  keep visible
            }
        });
    }, { threshold: 0.08 });

    document.querySelectorAll('.reveal, .sec, .step, .art-card').forEach(el => {
        // Only add reveal class if not already set
        if (!el.classList.contains('reveal')) {
            el.classList.add('reveal');
        }
        revealObserver.observe(el);
    });
</script>

<script>
    window.formspree = window.formspree || function () { (formspree.q = formspree.q || []).push(arguments); };
    formspree('initForm', { formElement: '#notify-form', formId: 'xjgppkkn' });
    document.getElementById('notify-form').addEventListener('submit', function() {
        if (window.plausible) plausible('CTA Click', { props: { type: 'notify' } });
    });
</script>
<script src="https://unpkg.com/@formspree/ajax@1" defer></script>
</body>
</html>

===== PUBLIC INVENTORY =====
./docs/commercial/RESEARCH_REGISTER_2026-07-31.md
[exit 0]
```

Ended: `2026-08-05T00:17:17+01:00`

## Commercial benchmark protocol and results

Started: `2026-08-05T00:17:17+01:00`

Command:

```console
$ bash -lc 'cat benchmarks/commercial_v1/PROTOCOL.md; printf '"'"'\n===== MANIFEST =====\n'"'"'; cat benchmarks/commercial_v1/manifest.json; printf '"'"'\n===== LABELS =====\n'"'"'; cat benchmarks/commercial_v1/labels.json; printf '"'"'\n===== SUMMARY =====\n'"'"'; cat benchmarks/commercial_v1/results/summary.json; printf '"'"'\n===== RAW SCORE =====\n'"'"'; cat benchmarks/commercial_v1/results/raw/synthetic-score.json'
# Regula commercial_v1 preregistration

Status: frozen before any `commercial_v1` tool execution. Session date:
2026-07-31 Europe/London. Product detection rules, classifiers, gates,
thresholds, and public positioning are frozen at commit
`94efa9e6ad9173fb888822543c247195078b0220`.

This evaluates whether one narrow Regula capability merits a bounded pilot.
It is not an EU AI Act compliance certification and is not designed to make
Regula look favourable. Failed installs, non-zero exits, timeouts, missing
repositories, and underpowered strata remain results.

## Evidence boundary and candidate jobs

Candidate A asks whether a buyer can use Regula for local AI inventory and a
reproducible evidence scaffold. A positive fact is an observable imported AI
library or service; comments, quoted examples, and near-name modules are
negative controls. A tool prediction requires a source-linked finding carrying
the case filename, integer line and non-empty indicator list. Ungrounded global
metadata is rejected. Real-repository inventory labels are not inferred by a
model.

Candidate B asks whether Regula can identify code-observable Article 50
implementation evidence. The unit is rendered affirmative disclosure or
machine-readable marking evidence. Corpus truth is limited to that observable
feature, not legal sufficiency. Tool output predicts the feature only when a
source-linked `limited_risk` finding identifies the case. The naive baseline
uses a stdlib HTML parser to exclude comments, scripts, styles and templates
and recognise visible affirmative text or an `ai-generated` meta marker.
Comments, dormant templates, developer notes, irrelevant attributes, and
negated text are negatives. A miss means
only that implementation evidence was not observed in the reviewed artefact.
It is never scored as a legal violation.

Candidate C asks whether declared intended purpose and deployment context can
support high-risk review. It cannot exceed `MODEL_PROVISIONAL` in this session:
two independent human raters and adjudication are unavailable. No code-only
result may clear Candidate C.

## Corpus and leakage controls

Layer 1 is 160 truth-by-construction decisions in `corpus.json`: 40 positive
and 40 negative decisions for each of A and B. Python and HTML are separate
language strata. Transformations are frozen before execution. Expected labels
are held in `labels.json`; `run.py` does not open that file. Labels are opened
only by `score.py` after every frozen run finishes.

Layer 2 is a disclosed purposive convenience frame of 12 public repositories
listed in `manifest.json`, pinned to commits obtained from `git ls-remote` on
2026-07-31. It is not random or confirmatory. The set includes Python and
TypeScript, AI and non-AI software, and small and materially larger projects.
Four previously benchmarked repositories are disclosed as exclusions rather
than silently removed. Repository identity, commit and licence are factual
metadata. Capability labels require blinded human review; without it, this
layer can support installation, runtime, alert-burden and evidence-reproduction
observations but not precision, recall, or external accuracy support. No
candidate can become `CLAIM_READY` from this convenience frame.

Layer 3 is a blinded scenario-pack requirement covering intended purpose,
roles, affected people, deployment context, consequence, oversight, code
evidence, decision rules, two independent labels and adjudication. It remains
unexecuted and `MODEL_PROVISIONAL` until independent humans supply those
fields.

No existing Regula development fixture is a headline holdout. No expected
holdout label may be exposed to a scanner command. After execution, internal
inspection may classify failures but may not tune product rules or corpus.

## Prospective sample size and power

The commercial gates concern lower confidence bounds, not convenient point
estimates. For 40/40 successes, a two-sided Wilson 95% lower bound is about
0.912, so a perfect applicable stratum can clear a 0.90 lower-bound policy.
With 39/40, the lower bound is about 0.871 and does not clear it. Forty actual
positives and forty negatives per synthetic candidate therefore make the gate
falsifiable while exceeding the 30-decision minimum.

This calculation does not grant independent trials or external validity. The
160 decisions repeat only three positive and five negative transformation
families per job. Transformation family, not generated file, is the inferential
unit; family-level results are diagnostic and cannot independently clear a
claim gate. Repository decisions are clustered. Twelve purposively chosen
clusters are exploratory and no repository-level accuracy labels exist, so
comparative inference is `INSUFFICIENT`. Forty predicted and actual positives
remain the minimum for descriptive Wilson intervals, which are reported with
an explicit correlated-case caveat rather than used as confirmatory coverage.

## Tools and comparator fairness

`tools.lock.json` freezes the latest official-registry Regula release found
(1.7.4), local HEAD, a transparent naive baseline, two registry-resolved
competitors, and one unresolved CLI lead. Each install uses a fresh external
virtual environment. The documented default runs first. At most one frozen
best-reasonable configuration may follow. A comparator that cannot install or
produce valid output is operationally unavailable and is not replaced.

Candidate A naive baseline matches ten explicit AI package/service names only
in active Python import statements. Candidate B naive baseline matches five
exact affirmative phrases in rendered markup and excludes five transparent
near-miss forms. These are intentionally inspectable, not optimised after
results.

Every synthetic CLI invocation has a 120-second limit and every repository
invocation a 900-second limit, retained stdout, stderr, command, working
directory, version, configuration, start/finish time, exit status, timeout,
input hash, output hashes and duration. In-process naive timing and cold CLI
timing are reported separately and never used for superiority. The available
`resource` high-water mark is cumulative child RSS, not per-invocation peak;
memory is therefore `NOT_MEASURED` for comparative purposes. Network behaviour
uses an attempted namespace denial plus a Python socket-construction denial.
The latter cannot see non-Python syscalls and cannot prove zero calls. Source
inspection alone cannot prove zero network calls.

## Execution sequence

1. Verify all frozen hashes in the committed protocol tree, independently
   verify that the detached product worktree is exactly the frozen product
   commit, that Git actually succeeds, every repository
   input is tracked and not ignored, every listed input exists, and recursive
   discovery agrees with the manifest in both directions.
2. Acquire each pinned public repository into the external artefact directory;
   verify HEAD, source hash and licence. Missing acquisition is an error.
3. `install_tools.py` creates fresh environments for every registry-resolved
   package and retains installs; the unresolved Complior identity remains an
   availability result, not a product execution failure.
4. `run.py` executes naive and local-HEAD synthetic cells. Public Regula and
   competitor schemas are not coerced into synthetic accuracy decisions
   without a source-event adapter. `operations.py` nevertheless reaches and
   executes every installed documented default, and the one frozen configured
   compliance-agent path, on all 12 repositories. This is an availability and
   operations audit, not an accuracy comparison.
5. Repeat deterministic paths from a fresh output directory without output or
   fixture reuse. Compare normalised output hashes.
6. Only after both runs end, open `labels.json`, score, and classify failures.

`run.py` refuses an existing output directory. `verify.py` independently uses
`git ls-files`, checks HEAD against the manifest, and rejects missing,
untracked, ignored, changed, duplicate, extra or omitted inputs/results. It
retains adverse records but refuses to mark them successful. `normalise.py`
removes declared timing and harness-path fields and canonicalises case/Python
paths while retaining semantic configuration. `score.py` requires exact unique
enumeration, reports language/transform strata, retains fractions and Wilson
intervals, and hard-codes headline eligibility false until the external gate
engine evaluates every conjunct.

## Metrics and analysis

Where logically valid, report TP, FP, FN, TN, precision, recall, F1, MCC,
Wilson 95% intervals, false alerts per repository and per 1,000 relevant lines,
misses per repository, category/language breakdown, default/configured paths,
execution-path disagreement, install success, time to first valid result,
runtime, peak memory, determinism, observed network behaviour, evidence-pack
completeness, clean-checkout reproduction, manifest/signature verification and
exit-code usability.

Paired binary decisions may use exact McNemar diagnostically, but repeated
transformation families make item-level inference non-confirmatory. A future
confirmatory repository study must define an external population and adequate
independent repository clusters before using a paired repository bootstrap.
Report effect sizes and uncertainty, not p-values alone. Do not pool away a
weak job, language, transformation or category. No pseudo-probabilities or
calibration analysis are permitted unless a tool emits real confidence scores.
Sensitivity analysis reports false-positive to false-negative cost ratios of
1:1, 2:1, 1:2, 5:1 and 1:5; no single ratio is buyer truth.

## Preregistered gates

Candidate A is `CLAIM_READY` only if Wilson lower bounds are at least 0.90 for
both precision and recall, real repositories support the result, clean evidence
reproduction passes, no material hidden-network contradiction exists, and a
meaningful advantage over the naive baseline or executable competitor is
demonstrated. In this session, “real repositories support” requires independent
labels on at least 30 repositories sampled from a prospectively enumerated
buyer-relevant population. That condition is known unavailable, so A cannot
become `CLAIM_READY`; synthetic results can support only `PILOT` or `FAILED`.

Candidate B is `CLAIM_READY` only if the precision lower bound is at least
0.90 and recall lower bound at least 0.80, evidence observations are separated
from legal compliance, source absence never becomes a definitive violation,
and advantage over exact markup matching or an executable competitor is
demonstrated. “Meaningful advantage” means a paired difference whose 95%
interval excludes zero and whose absolute recall or precision improvement is
at least 0.05 without degrading the other metric by more than 0.02, or a
documented operational capability absent from the baseline with no accuracy
regression. No source-linked competitor adapter exists at freeze, so B also
cannot become `CLAIM_READY` in this session.

Candidate C requires two independent human raters, adjudication, context
inputs, raw disagreements and an appropriate agreement statistic, plus Wilson
lower bounds of 0.80 precision and 0.70 recall and no un-escalated definitive
legal error. Without those humans its ceiling is `MODEL_PROVISIONAL`.

All candidates additionally require two clean identical normalised runs,
verified evidence manifests, complete accounting, visible failures, a working
public-release first-use journey, no contradicted active high-consequence claim,
and no concealed category/language. A “material hidden-network contradiction”
means an observed socket attempt on a command actively described as offline or
zero-network. Public-claim integrity fails if any active unqualified legal
classification, universal reproducibility, or zero-network claim is
contradicted. A point estimate that passes while its
interval fails is `PILOT`, never `CLAIM_READY`.

Verdict fields and decision rules are exactly those in the session directive:
technical evidence, comparative advantage, public-claim integrity, regulatory
currency, operational readiness, demand evidence and overall decision are
reported separately. Research cannot raise demand above `UNVALIDATED`.

## Known preregistration limitations

- Layer 1 is generated from a small set of repeated transformation families;
  it tests metamorphic consistency, not independent Bernoulli performance.
- Real-repository precision and recall cannot be scored without independent
  labels. Twelve repository clusters are weak for uncertainty estimation.
- No human raters are available for Candidate C.
- Comparator schemas may not map cleanly to the same unit. A non-equivalent
  output is reported operationally, not coerced into an accuracy result.
- The current public PyPI description is stale relative to local HEAD and
  contains high-consequence claims; the claim audit may itself block every
  capability regardless of synthetic accuracy.
- Demand remains unvalidated without interviews, representative buyer data,
  design-partner commitments or payment.

These limitations cannot be changed after benchmark output is visible.

===== MANIFEST =====
{
  "protocol_version": "commercial_v1",
  "regula_commit": "94efa9e6ad9173fb888822543c247195078b0220",
  "selection_seed": "identity provenance only; repository frame is a disclosed purposive census, not a random sample",
  "ground_truth": {
    "layer_1": "truth-by-construction",
    "layer_2": "repository identity and code are factual; capability labels require blinded human review and are unavailable",
    "layer_3": "MODEL-PROVISIONAL because independent human raters and adjudication are unavailable"
  },
  "repository_inputs": [
    {"path": "benchmarks/commercial_v1/PROTOCOL.md", "sha256": "58c935903b5832eb7b8232116f6dc182b97708a89b5d3070f8b856ec9272d8c4"},
    {"path": "benchmarks/commercial_v1/REDTEAM_PREREGISTRATION.md", "sha256": "82ffaea70cba9e325a8354dbca48fb948cc4bc68abd0e31cc48e9377b6a16c03"},
    {"path": "benchmarks/commercial_v1/acquire.py", "sha256": "d2cc1d48cfa8c05eb37791e0987cea483e5d668f5c8c3fbdec7a0260dd49d43a"},
    {"path": "benchmarks/commercial_v1/annotation_pack.json", "sha256": "5e4edf71cb03c89331f642ea70a6ef6d1e1501fcbd094afcbed694cd22ee0eb8"},
    {"path": "benchmarks/commercial_v1/build_annotation_pack.py", "sha256": "20cd491ac6b04518333f743a3e865b1ba3b6aad1654a61d25d2e75fbd7907c4e"},
    {"path": "benchmarks/commercial_v1/build_corpus.py", "sha256": "41779ababa2b13479c39edff12bb28c05e1b3e63f950f1559dcb450a62257aec"},
    {"path": "benchmarks/commercial_v1/corpus.json", "sha256": "9c726626ce8ff34d94fb070c0d732fe25a6a243e3401618fa12ae63673f763af"},
    {"path": "benchmarks/commercial_v1/gate.py", "sha256": "0b059050c024cc3208f3cc96f60ff1052b34309d5e9b006f92f0d76c0ccacfdc"},
    {"path": "benchmarks/commercial_v1/install_tools.py", "sha256": "04abc48c26bb488578d2fef9ba87572713751b0d048c0c75b75133a00bbb10c3"},
    {"path": "benchmarks/commercial_v1/labels.json", "sha256": "feea31edb0316ad8606c8d995b2164b4704b46e0223e7ad4df29a94154217e28"},
    {"path": "benchmarks/commercial_v1/network_probe.py", "sha256": "f46928064729f65798439d41d5798dea5986739cae8979909622a7cf0c4ecc78"},
    {"path": "benchmarks/commercial_v1/normalise.py", "sha256": "53a6321117fc8ec6bb348e6ee0b36f0589f59df14fe5b9dddd9f2a87f28f3478"},
    {"path": "benchmarks/commercial_v1/operations.py", "sha256": "d5a652874ecaa25d2e008f2d914bf5cb23b79960bf1cd1c49b40c95b98717723"},
    {"path": "benchmarks/commercial_v1/repository_candidates.json", "sha256": "efd0ae2ab51b6a7ed6e63cd9b5e72f81c1b030510ca9b159d255dce24f9f0859"},
    {"path": "benchmarks/commercial_v1/research_questions.json", "sha256": "d8dab648777b301a11d5255b59d7be6a8b09f5daeef49eb09818f7ce158ba172"},
    {"path": "benchmarks/commercial_v1/run.py", "sha256": "f04d002d1a93363b33b10692a43b3d8f33909e9f41299b8dae837c5cfade25e7"},
    {"path": "benchmarks/commercial_v1/score.py", "sha256": "fc020c842d360c62b6bcfbb6a2718ba3fb4870aaeeae92b757bba62516a2cb08"},
    {"path": "benchmarks/commercial_v1/select_repositories.py", "sha256": "5bc876796c4f3f334deabce12732d5195397a146a2a9310dadd6ed1c3856df5b"},
    {"path": "benchmarks/commercial_v1/tools.lock.json", "sha256": "f933ba1c4107bea1f2a46f32b59f60f239c51eef3a0718d7fd1464905a23bd77"},
    {"path": "benchmarks/commercial_v1/verify.py", "sha256": "2c8ebd6723eb7e0e12ba711625d60eb2e96b24604a105b68a84f3878f7fd84da"}
  ],
  "layers": {
    "truth_by_construction": {
      "corpus_file": "benchmarks/commercial_v1/corpus.json",
      "labels_file": "benchmarks/commercial_v1/labels.json",
      "decisions": 160,
      "strata": {
        "A_positive": 40,
        "A_negative": 40,
        "B_positive": 40,
        "B_negative": 40
      }
    },
    "public_repositories": [
      {"id": "microsoft/markitdown", "commit": "fd239d5d2be43d9b68329730206b9312c7d5a388", "language": "Python", "ai_mix": "AI", "license_expected": "MIT"},
      {"id": "open-webui/open-webui", "commit": "01f4282f1ffe0d6212f58d3afbeae21fffd0c4be", "language": "Python/TypeScript", "ai_mix": "AI", "license_expected": "repository licence to verify"},
      {"id": "browser-use/browser-use", "commit": "f0aa3a8bb03779c71a5aa262d389e3bfe6b77cdc", "language": "Python", "ai_mix": "AI", "license_expected": "MIT"},
      {"id": "modelcontextprotocol/python-sdk", "commit": "a4f4ccd091138771535e17191123f20b30fda68e", "language": "Python", "ai_mix": "AI infrastructure", "license_expected": "MIT"},
      {"id": "pallets/click", "commit": "00e592cea702e0b2caa0dee42489fdb1c22cd845", "language": "Python", "ai_mix": "non-AI", "license_expected": "BSD-3-Clause"},
      {"id": "pallets/itsdangerous", "commit": "672971d66a2ef9f85151e53283113f33d642dabd", "language": "Python", "ai_mix": "non-AI", "license_expected": "BSD-3-Clause"},
      {"id": "python-attrs/attrs", "commit": "97f8d175656bc03c373a1c9038048a4d312c307c", "language": "Python", "ai_mix": "non-AI", "license_expected": "MIT"},
      {"id": "astral-sh/ruff", "commit": "2272478c067945096c34350b20d0bfc41d356d3c", "language": "Rust/Python", "ai_mix": "non-AI", "license_expected": "MIT"},
      {"id": "prettier/prettier", "commit": "60f03eae59ddf0dff496073d88b0263507c99a5a", "language": "TypeScript/JavaScript", "ai_mix": "non-AI", "license_expected": "MIT"},
      {"id": "axios/axios", "commit": "c3f553c740ebf3dff5e22dae24e9caaafafddd2d", "language": "JavaScript", "ai_mix": "non-AI", "license_expected": "MIT"},
      {"id": "sindresorhus/ky", "commit": "3419113b48e034fdcf8fa6bd3be3da7b3d0d758f", "language": "TypeScript", "ai_mix": "non-AI", "license_expected": "MIT"},
      {"id": "vitest-dev/vitest", "commit": "ec367cf2a6c955da8304e8cea935d1f3dc034a98", "language": "TypeScript", "ai_mix": "non-AI", "license_expected": "MIT"}
    ],
    "legal_context_scenarios": {
      "status": "annotation pack required but not claim-eligible without two independent human raters and adjudication",
      "headline_allowed": false
    }
  }
}

===== LABELS =====
[
  {
    "decision_id": "a-positive-01",
    "candidate": "A",
    "expected": true,
    "basis": "truth-by-construction import"
  },
  {
    "decision_id": "a-positive-02",
    "candidate": "A",
    "expected": true,
    "basis": "truth-by-construction import"
  },
  {
    "decision_id": "a-positive-03",
    "candidate": "A",
    "expected": true,
    "basis": "truth-by-construction import"
  },
  {
    "decision_id": "a-positive-04",
    "candidate": "A",
    "expected": true,
    "basis": "truth-by-construction import"
  },
  {
    "decision_id": "a-positive-05",
    "candidate": "A",
    "expected": true,
    "basis": "truth-by-construction import"
  },
  {
    "decision_id": "a-positive-06",
    "candidate": "A",
    "expected": true,
    "basis": "truth-by-construction import"
  },
  {
    "decision_id": "a-positive-07",
    "candidate": "A",
    "expected": true,
    "basis": "truth-by-construction import"
  },
  {
    "decision_id": "a-positive-08",
    "candidate": "A",
    "expected": true,
    "basis": "truth-by-construction import"
  },
  {
    "decision_id": "a-positive-09",
    "candidate": "A",
    "expected": true,
    "basis": "truth-by-construction import"
  },
  {
    "decision_id": "a-positive-10",
    "candidate": "A",
    "expected": true,
    "basis": "truth-by-construction import"
  },
  {
    "decision_id": "a-positive-11",
    "candidate": "A",
    "expected": true,
    "basis": "truth-by-construction import"
  },
  {
    "decision_id": "a-positive-12",
    "candidate": "A",
    "expected": true,
    "basis": "truth-by-construction import"
  },
  {
    "decision_id": "a-positive-13",
    "candidate": "A",
    "expected": true,
    "basis": "truth-by-construction import"
  },
  {
    "decision_id": "a-positive-14",
    "candidate": "A",
    "expected": true,
    "basis": "truth-by-construction import"
  },
  {
    "decision_id": "a-positive-15",
    "candidate": "A",
    "expected": true,
    "basis": "truth-by-construction import"
  },
  {
    "decision_id": "a-positive-16",
    "candidate": "A",
    "expected": true,
    "basis": "truth-by-construction import"
  },
  {
    "decision_id": "a-positive-17",
    "candidate": "A",
    "expected": true,
    "basis": "truth-by-construction import"
  },
  {
    "decision_id": "a-positive-18",
    "candidate": "A",
    "expected": true,
    "basis": "truth-by-construction import"
  },
  {
    "decision_id": "a-positive-19",
    "candidate": "A",
    "expected": true,
    "basis": "truth-by-construction import"
  },
  {
    "decision_id": "a-positive-20",
    "candidate": "A",
    "expected": true,
    "basis": "truth-by-construction import"
  },
  {
    "decision_id": "a-positive-21",
    "candidate": "A",
    "expected": true,
    "basis": "truth-by-construction import"
  },
  {
    "decision_id": "a-positive-22",
    "candidate": "A",
    "expected": true,
    "basis": "truth-by-construction import"
  },
  {
    "decision_id": "a-positive-23",
    "candidate": "A",
    "expected": true,
    "basis": "truth-by-construction import"
  },
  {
    "decision_id": "a-positive-24",
    "candidate": "A",
    "expected": true,
    "basis": "truth-by-construction import"
  },
  {
    "decision_id": "a-positive-25",
    "candidate": "A",
    "expected": true,
    "basis": "truth-by-construction import"
  },
  {
    "decision_id": "a-positive-26",
    "candidate": "A",
    "expected": true,
    "basis": "truth-by-construction import"
  },
  {
    "decision_id": "a-positive-27",
    "candidate": "A",
    "expected": true,
    "basis": "truth-by-construction import"
  },
  {
    "decision_id": "a-positive-28",
    "candidate": "A",
    "expected": true,
    "basis": "truth-by-construction import"
  },
  {
    "decision_id": "a-positive-29",
    "candidate": "A",
    "expected": true,
    "basis": "truth-by-construction import"
  },
  {
    "decision_id": "a-positive-30",
    "candidate": "A",
    "expected": true,
    "basis": "truth-by-construction import"
  },
  {
    "decision_id": "a-positive-31",
    "candidate": "A",
    "expected": true,
    "basis": "truth-by-construction import"
  },
  {
    "decision_id": "a-positive-32",
    "candidate": "A",
    "expected": true,
    "basis": "truth-by-construction import"
  },
  {
    "decision_id": "a-positive-33",
    "candidate": "A",
    "expected": true,
    "basis": "truth-by-construction import"
  },
  {
    "decision_id": "a-positive-34",
    "candidate": "A",
    "expected": true,
    "basis": "truth-by-construction import"
  },
  {
    "decision_id": "a-positive-35",
    "candidate": "A",
    "expected": true,
    "basis": "truth-by-construction import"
  },
  {
    "decision_id": "a-positive-36",
    "candidate": "A",
    "expected": true,
    "basis": "truth-by-construction import"
  },
  {
    "decision_id": "a-positive-37",
    "candidate": "A",
    "expected": true,
    "basis": "truth-by-construction import"
  },
  {
    "decision_id": "a-positive-38",
    "candidate": "A",
    "expected": true,
    "basis": "truth-by-construction import"
  },
  {
    "decision_id": "a-positive-39",
    "candidate": "A",
    "expected": true,
    "basis": "truth-by-construction import"
  },
  {
    "decision_id": "a-positive-40",
    "candidate": "A",
    "expected": true,
    "basis": "truth-by-construction import"
  },
  {
    "decision_id": "a-negative-01",
    "candidate": "A",
    "expected": false,
    "basis": "truth-by-construction near miss"
  },
  {
    "decision_id": "a-negative-02",
    "candidate": "A",
    "expected": false,
    "basis": "truth-by-construction near miss"
  },
  {
    "decision_id": "a-negative-03",
    "candidate": "A",
    "expected": false,
    "basis": "truth-by-construction near miss"
  },
  {
    "decision_id": "a-negative-04",
    "candidate": "A",
    "expected": false,
    "basis": "truth-by-construction near miss"
  },
  {
    "decision_id": "a-negative-05",
    "candidate": "A",
    "expected": false,
    "basis": "truth-by-construction near miss"
  },
  {
    "decision_id": "a-negative-06",
    "candidate": "A",
    "expected": false,
    "basis": "truth-by-construction near miss"
  },
  {
    "decision_id": "a-negative-07",
    "candidate": "A",
    "expected": false,
    "basis": "truth-by-construction near miss"
  },
  {
    "decision_id": "a-negative-08",
    "candidate": "A",
    "expected": false,
    "basis": "truth-by-construction near miss"
  },
  {
    "decision_id": "a-negative-09",
    "candidate": "A",
    "expected": false,
    "basis": "truth-by-construction near miss"
  },
  {
    "decision_id": "a-negative-10",
    "candidate": "A",
    "expected": false,
    "basis": "truth-by-construction near miss"
  },
  {
    "decision_id": "a-negative-11",
    "candidate": "A",
    "expected": false,
    "basis": "truth-by-construction near miss"
  },
  {
    "decision_id": "a-negative-12",
    "candidate": "A",
    "expected": false,
    "basis": "truth-by-construction near miss"
  },
  {
    "decision_id": "a-negative-13",
    "candidate": "A",
    "expected": false,
    "basis": "truth-by-construction near miss"
  },
  {
    "decision_id": "a-negative-14",
    "candidate": "A",
    "expected": false,
    "basis": "truth-by-construction near miss"
  },
  {
    "decision_id": "a-negative-15",
    "candidate": "A",
    "expected": false,
    "basis": "truth-by-construction near miss"
  },
  {
    "decision_id": "a-negative-16",
    "candidate": "A",
    "expected": false,
    "basis": "truth-by-construction near miss"
  },
  {
    "decision_id": "a-negative-17",
    "candidate": "A",
    "expected": false,
    "basis": "truth-by-construction near miss"
  },
  {
    "decision_id": "a-negative-18",
    "candidate": "A",
    "expected": false,
    "basis": "truth-by-construction near miss"
  },
  {
    "decision_id": "a-negative-19",
    "candidate": "A",
    "expected": false,
    "basis": "truth-by-construction near miss"
  },
  {
    "decision_id": "a-negative-20",
    "candidate": "A",
    "expected": false,
    "basis": "truth-by-construction near miss"
  },
  {
    "decision_id": "a-negative-21",
    "candidate": "A",
    "expected": false,
    "basis": "truth-by-construction near miss"
  },
  {
    "decision_id": "a-negative-22",
    "candidate": "A",
    "expected": false,
    "basis": "truth-by-construction near miss"
  },
  {
    "decision_id": "a-negative-23",
    "candidate": "A",
    "expected": false,
    "basis": "truth-by-construction near miss"
  },
  {
    "decision_id": "a-negative-24",
    "candidate": "A",
    "expected": false,
    "basis": "truth-by-construction near miss"
  },
  {
    "decision_id": "a-negative-25",
    "candidate": "A",
    "expected": false,
    "basis": "truth-by-construction near miss"
  },
  {
    "decision_id": "a-negative-26",
    "candidate": "A",
    "expected": false,
    "basis": "truth-by-construction near miss"
  },
  {
    "decision_id": "a-negative-27",
    "candidate": "A",
    "expected": false,
    "basis": "truth-by-construction near miss"
  },
  {
    "decision_id": "a-negative-28",
    "candidate": "A",
    "expected": false,
    "basis": "truth-by-construction near miss"
  },
  {
    "decision_id": "a-negative-29",
    "candidate": "A",
    "expected": false,
    "basis": "truth-by-construction near miss"
  },
  {
    "decision_id": "a-negative-30",
    "candidate": "A",
    "expected": false,
    "basis": "truth-by-construction near miss"
  },
  {
    "decision_id": "a-negative-31",
    "candidate": "A",
    "expected": false,
    "basis": "truth-by-construction near miss"
  },
  {
    "decision_id": "a-negative-32",
    "candidate": "A",
    "expected": false,
    "basis": "truth-by-construction near miss"
  },
  {
    "decision_id": "a-negative-33",
    "candidate": "A",
    "expected": false,
    "basis": "truth-by-construction near miss"
  },
  {
    "decision_id": "a-negative-34",
    "candidate": "A",
    "expected": false,
    "basis": "truth-by-construction near miss"
  },
  {
    "decision_id": "a-negative-35",
    "candidate": "A",
    "expected": false,
    "basis": "truth-by-construction near miss"
  },
  {
    "decision_id": "a-negative-36",
    "candidate": "A",
    "expected": false,
    "basis": "truth-by-construction near miss"
  },
  {
    "decision_id": "a-negative-37",
    "candidate": "A",
    "expected": false,
    "basis": "truth-by-construction near miss"
  },
  {
    "decision_id": "a-negative-38",
    "candidate": "A",
    "expected": false,
    "basis": "truth-by-construction near miss"
  },
  {
    "decision_id": "a-negative-39",
    "candidate": "A",
    "expected": false,
    "basis": "truth-by-construction near miss"
  },
  {
    "decision_id": "a-negative-40",
    "candidate": "A",
    "expected": false,
    "basis": "truth-by-construction near miss"
  },
  {
    "decision_id": "b-positive-01",
    "candidate": "B",
    "expected": true,
    "basis": "truth-by-construction chatbot_notice"
  },
  {
    "decision_id": "b-positive-02",
    "candidate": "B",
    "expected": true,
    "basis": "truth-by-construction synthetic_marker"
  },
  {
    "decision_id": "b-positive-03",
    "candidate": "B",
    "expected": true,
    "basis": "truth-by-construction deepfake_notice"
  },
  {
    "decision_id": "b-positive-04",
    "candidate": "B",
    "expected": true,
    "basis": "truth-by-construction emotion_notice"
  },
  {
    "decision_id": "b-positive-05",
    "candidate": "B",
    "expected": true,
    "basis": "truth-by-construction biometric_notice"
  },
  {
    "decision_id": "b-positive-06",
    "candidate": "B",
    "expected": true,
    "basis": "truth-by-construction chatbot_notice"
  },
  {
    "decision_id": "b-positive-07",
    "candidate": "B",
    "expected": true,
    "basis": "truth-by-construction synthetic_marker"
  },
  {
    "decision_id": "b-positive-08",
    "candidate": "B",
    "expected": true,
    "basis": "truth-by-construction deepfake_notice"
  },
  {
    "decision_id": "b-positive-09",
    "candidate": "B",
    "expected": true,
    "basis": "truth-by-construction emotion_notice"
  },
  {
    "decision_id": "b-positive-10",
    "candidate": "B",
    "expected": true,
    "basis": "truth-by-construction biometric_notice"
  },
  {
    "decision_id": "b-positive-11",
    "candidate": "B",
    "expected": true,
    "basis": "truth-by-construction chatbot_notice"
  },
  {
    "decision_id": "b-positive-12",
    "candidate": "B",
    "expected": true,
    "basis": "truth-by-construction synthetic_marker"
  },
  {
    "decision_id": "b-positive-13",
    "candidate": "B",
    "expected": true,
    "basis": "truth-by-construction deepfake_notice"
  },
  {
    "decision_id": "b-positive-14",
    "candidate": "B",
    "expected": true,
    "basis": "truth-by-construction emotion_notice"
  },
  {
    "decision_id": "b-positive-15",
    "candidate": "B",
    "expected": true,
    "basis": "truth-by-construction biometric_notice"
  },
  {
    "decision_id": "b-positive-16",
    "candidate": "B",
    "expected": true,
    "basis": "truth-by-construction chatbot_notice"
  },
  {
    "decision_id": "b-positive-17",
    "candidate": "B",
    "expected": true,
    "basis": "truth-by-construction synthetic_marker"
  },
  {
    "decision_id": "b-positive-18",
    "candidate": "B",
    "expected": true,
    "basis": "truth-by-construction deepfake_notice"
  },
  {
    "decision_id": "b-positive-19",
    "candidate": "B",
    "expected": true,
    "basis": "truth-by-construction emotion_notice"
  },
  {
    "decision_id": "b-positive-20",
    "candidate": "B",
    "expected": true,
    "basis": "truth-by-construction biometric_notice"
  },
  {
    "decision_id": "b-positive-21",
    "candidate": "B",
    "expected": true,
    "basis": "truth-by-construction chatbot_notice"
  },
  {
    "decision_id": "b-positive-22",
    "candidate": "B",
    "expected": true,
    "basis": "truth-by-construction synthetic_marker"
  },
  {
    "decision_id": "b-positive-23",
    "candidate": "B",
    "expected": true,
    "basis": "truth-by-construction deepfake_notice"
  },
  {
    "decision_id": "b-positive-24",
    "candidate": "B",
    "expected": true,
    "basis": "truth-by-construction emotion_notice"
  },
  {
    "decision_id": "b-positive-25",
    "candidate": "B",
    "expected": true,
    "basis": "truth-by-construction biometric_notice"
  },
  {
    "decision_id": "b-positive-26",
    "candidate": "B",
    "expected": true,
    "basis": "truth-by-construction chatbot_notice"
  },
  {
    "decision_id": "b-positive-27",
    "candidate": "B",
    "expected": true,
    "basis": "truth-by-construction synthetic_marker"
  },
  {
    "decision_id": "b-positive-28",
    "candidate": "B",
    "expected": true,
    "basis": "truth-by-construction deepfake_notice"
  },
  {
    "decision_id": "b-positive-29",
    "candidate": "B",
    "expected": true,
    "basis": "truth-by-construction emotion_notice"
  },
  {
    "decision_id": "b-positive-30",
    "candidate": "B",
    "expected": true,
    "basis": "truth-by-construction biometric_notice"
  },
  {
    "decision_id": "b-positive-31",
    "candidate": "B",
    "expected": true,
    "basis": "truth-by-construction chatbot_notice"
  },
  {
    "decision_id": "b-positive-32",
    "candidate": "B",
    "expected": true,
    "basis": "truth-by-construction synthetic_marker"
  },
  {
    "decision_id": "b-positive-33",
    "candidate": "B",
    "expected": true,
    "basis": "truth-by-construction deepfake_notice"
  },
  {
    "decision_id": "b-positive-34",
    "candidate": "B",
    "expected": true,
    "basis": "truth-by-construction emotion_notice"
  },
  {
    "decision_id": "b-positive-35",
    "candidate": "B",
    "expected": true,
    "basis": "truth-by-construction biometric_notice"
  },
  {
    "decision_id": "b-positive-36",
    "candidate": "B",
    "expected": true,
    "basis": "truth-by-construction chatbot_notice"
  },
  {
    "decision_id": "b-positive-37",
    "candidate": "B",
    "expected": true,
    "basis": "truth-by-construction synthetic_marker"
  },
  {
    "decision_id": "b-positive-38",
    "candidate": "B",
    "expected": true,
    "basis": "truth-by-construction deepfake_notice"
  },
  {
    "decision_id": "b-positive-39",
    "candidate": "B",
    "expected": true,
    "basis": "truth-by-construction emotion_notice"
  },
  {
    "decision_id": "b-positive-40",
    "candidate": "B",
    "expected": true,
    "basis": "truth-by-construction biometric_notice"
  },
  {
    "decision_id": "b-negative-01",
    "candidate": "B",
    "expected": false,
    "basis": "truth-by-construction near miss"
  },
  {
    "decision_id": "b-negative-02",
    "candidate": "B",
    "expected": false,
    "basis": "truth-by-construction near miss"
  },
  {
    "decision_id": "b-negative-03",
    "candidate": "B",
    "expected": false,
    "basis": "truth-by-construction near miss"
  },
  {
    "decision_id": "b-negative-04",
    "candidate": "B",
    "expected": false,
    "basis": "truth-by-construction near miss"
  },
  {
    "decision_id": "b-negative-05",
    "candidate": "B",
    "expected": false,
    "basis": "truth-by-construction near miss"
  },
  {
    "decision_id": "b-negative-06",
    "candidate": "B",
    "expected": false,
    "basis": "truth-by-construction near miss"
  },
  {
    "decision_id": "b-negative-07",
    "candidate": "B",
    "expected": false,
    "basis": "truth-by-construction near miss"
  },
  {
    "decision_id": "b-negative-08",
    "candidate": "B",
    "expected": false,
    "basis": "truth-by-construction near miss"
  },
  {
    "decision_id": "b-negative-09",
    "candidate": "B",
    "expected": false,
    "basis": "truth-by-construction near miss"
  },
  {
    "decision_id": "b-negative-10",
    "candidate": "B",
    "expected": false,
    "basis": "truth-by-construction near miss"
  },
  {
    "decision_id": "b-negative-11",
    "candidate": "B",
    "expected": false,
    "basis": "truth-by-construction near miss"
  },
  {
    "decision_id": "b-negative-12",
    "candidate": "B",
    "expected": false,
    "basis": "truth-by-construction near miss"
  },
  {
    "decision_id": "b-negative-13",
    "candidate": "B",
    "expected": false,
    "basis": "truth-by-construction near miss"
  },
  {
    "decision_id": "b-negative-14",
    "candidate": "B",
    "expected": false,
    "basis": "truth-by-construction near miss"
  },
  {
    "decision_id": "b-negative-15",
    "candidate": "B",
    "expected": false,
    "basis": "truth-by-construction near miss"
  },
  {
    "decision_id": "b-negative-16",
    "candidate": "B",
    "expected": false,
    "basis": "truth-by-construction near miss"
  },
  {
    "decision_id": "b-negative-17",
    "candidate": "B",
    "expected": false,
    "basis": "truth-by-construction near miss"
  },
  {
    "decision_id": "b-negative-18",
    "candidate": "B",
    "expected": false,
    "basis": "truth-by-construction near miss"
  },
  {
    "decision_id": "b-negative-19",
    "candidate": "B",
    "expected": false,
    "basis": "truth-by-construction near miss"
  },
  {
    "decision_id": "b-negative-20",
    "candidate": "B",
    "expected": false,
    "basis": "truth-by-construction near miss"
  },
  {
    "decision_id": "b-negative-21",
    "candidate": "B",
    "expected": false,
    "basis": "truth-by-construction near miss"
  },
  {
    "decision_id": "b-negative-22",
    "candidate": "B",
    "expected": false,
    "basis": "truth-by-construction near miss"
  },
  {
    "decision_id": "b-negative-23",
    "candidate": "B",
    "expected": false,
    "basis": "truth-by-construction near miss"
  },
  {
    "decision_id": "b-negative-24",
    "candidate": "B",
    "expected": false,
    "basis": "truth-by-construction near miss"
  },
  {
    "decision_id": "b-negative-25",
    "candidate": "B",
    "expected": false,
    "basis": "truth-by-construction near miss"
  },
  {
    "decision_id": "b-negative-26",
    "candidate": "B",
    "expected": false,
    "basis": "truth-by-construction near miss"
  },
  {
    "decision_id": "b-negative-27",
    "candidate": "B",
    "expected": false,
    "basis": "truth-by-construction near miss"
  },
  {
    "decision_id": "b-negative-28",
    "candidate": "B",
    "expected": false,
    "basis": "truth-by-construction near miss"
  },
  {
    "decision_id": "b-negative-29",
    "candidate": "B",
    "expected": false,
    "basis": "truth-by-construction near miss"
  },
  {
    "decision_id": "b-negative-30",
    "candidate": "B",
    "expected": false,
    "basis": "truth-by-construction near miss"
  },
  {
    "decision_id": "b-negative-31",
    "candidate": "B",
    "expected": false,
    "basis": "truth-by-construction near miss"
  },
  {
    "decision_id": "b-negative-32",
    "candidate": "B",
    "expected": false,
    "basis": "truth-by-construction near miss"
  },
  {
    "decision_id": "b-negative-33",
    "candidate": "B",
    "expected": false,
    "basis": "truth-by-construction near miss"
  },
  {
    "decision_id": "b-negative-34",
    "candidate": "B",
    "expected": false,
    "basis": "truth-by-construction near miss"
  },
  {
    "decision_id": "b-negative-35",
    "candidate": "B",
    "expected": false,
    "basis": "truth-by-construction near miss"
  },
  {
    "decision_id": "b-negative-36",
    "candidate": "B",
    "expected": false,
    "basis": "truth-by-construction near miss"
  },
  {
    "decision_id": "b-negative-37",
    "candidate": "B",
    "expected": false,
    "basis": "truth-by-construction near miss"
  },
  {
    "decision_id": "b-negative-38",
    "candidate": "B",
    "expected": false,
    "basis": "truth-by-construction near miss"
  },
  {
    "decision_id": "b-negative-39",
    "candidate": "B",
    "expected": false,
    "basis": "truth-by-construction near miss"
  },
  {
    "decision_id": "b-negative-40",
    "candidate": "B",
    "expected": false,
    "basis": "truth-by-construction near miss"
  }
]

===== SUMMARY =====
{
  "schema_version": "commercial_v1.result-summary.1",
  "session_date": "2026-07-31",
  "frozen_product_commit": "94efa9e6ad9173fb888822543c247195078b0220",
  "preregistration_commit": "5bd2112",
  "protocol_sha256": "58c935903b5832eb7b8232116f6dc182b97708a89b5d3070f8b856ec9272d8c4",
  "raw_score_sha256": "bd8191a1ec9f19bfc408fc770fd40409da091b6a218308ae0014200a6df20a3e",
  "protocol_deviations": [
    "84e0118 separated protocol-tree hashes from the frozen product tree before result execution",
    "056bcf2 added a non-frozen acquisition runner for case-insensitive root licence filenames after the retained frozen-run failure"
  ],
  "synthetic": {
    "decisions_per_run": 160,
    "runs_per_tool": 2,
    "local_normalised_sha256": "d3e891c9453a53acc6ba1c2905c2102f835ff39366be8be37e0101b86b3eb485",
    "naive_normalised_sha256": "8ddf6b690861f3e361a9375dff1e3d8615a457784fad3e9fa49a974b5b337e83",
    "local": {
      "A": {"tp": 0, "fp": 0, "fn": 40, "tn": 40, "recall": "0/40", "wilson95": [0.0, 0.08762160119728664]},
      "B": {"tp": 0, "fp": 0, "fn": 40, "tn": 40, "recall": "0/40", "wilson95": [0.0, 0.08762160119728664]}
    },
    "naive": {
      "A": {"tp": 40, "fp": 4, "fn": 0, "tn": 36, "precision": "40/44", "recall": "40/40", "precision_wilson95": [0.7884076083340138, 0.9640778067726837], "recall_wilson95": [0.9123783988027135, 1.0]},
      "B": {"tp": 40, "fp": 0, "fn": 0, "tn": 40, "precision": "40/40", "recall": "40/40", "precision_wilson95": [0.9123783988027135, 1.0], "recall_wilson95": [0.9123783988027135, 1.0]}
    },
    "ground_truth": "truth by construction; correlated transformation families; diagnostic, not external accuracy ground truth"
  },
  "repositories": {
    "pinned": 12,
    "acquired": 12,
    "human_labelled": 0,
    "local_head": {"successful_exits": "9/12", "nonzero_exits": "3/12", "exit_stdout_stderr_hash_repeat_match": "12/12"},
    "public_1_7_4": {"successful_exits": "9/12", "nonzero_exits": "3/12", "exit_stdout_stderr_hash_repeat_match": "12/12"},
    "compliance_agent_0_5_0_default": {"successful_exits": "12/12"},
    "compliance_agent_0_5_0_configured": {"successful_exits": "12/12"},
    "air_blackbox_1_13_2": {"successful_exits": "12/12"},
    "accuracy_comparison": "UNTESTABLE: no independent repository labels or equivalent source-event adapters"
  },
  "operational": {
    "active_openai_fixture_local_findings": "0/1",
    "active_openai_fixture_public_findings": "0/1",
    "unicode_path_local": "exit 0",
    "unicode_path_public": "exit 0",
    "local_pack_generation": "exit 0",
    "local_strict_pack_verification": "exit 0",
    "public_pack_generation": "exit 0 after documented --project syntax",
    "public_strict_pack_verification": "exit 2: legacy manifest lacks regula.evidence.v1 format declaration",
    "public_nonstrict_pack_verification": "exit 0",
    "network": "UNVERIFIED: namespace denial unavailable and frozen socket-denial probe breaks ssl import before command execution"
  },
  "verdict": {
    "TECHNICAL_EVIDENCE": "FAILED",
    "COMPARATIVE_ADVANTAGE": "NOT_DEMONSTRATED",
    "PUBLIC_CLAIM_INTEGRITY": "FAIL",
    "REGULATORY_CURRENCY": "PARTIAL",
    "OPERATIONAL_READINESS": "FAIL",
    "DEMAND_EVIDENCE": "UNVALIDATED",
    "OVERALL_DECISION": "STOP"
  }
}

===== RAW SCORE =====
{
  "schema_version": "commercial_v1.score.1",
  "labels_sha256": "feea31edb0316ad8606c8d995b2164b4704b46e0223e7ad4df29a94154217e28",
  "reports": [
    {
      "result_path": "/tmp/regula-commercial-20260731.Inq4k2/synthetic-naive-1/results.json",
      "tool": "naive",
      "result_sha256": "6125eb9518cb93d985095fd4919b179de04a62984feb7ba7c48d56087d3d5a1a",
      "enumeration_complete": true,
      "missing_ids": [],
      "extra_ids": [],
      "duplicate_ids": [],
      "failed_ids": [],
      "candidates": {
        "A": {
          "complete": true,
          "applicable_decisions": 80,
          "valid_decisions": 80,
          "failed_decision_ids": [],
          "metrics": {
            "counts": {
              "tp": 40,
              "fp": 4,
              "fn": 0,
              "tn": 36,
              "decisions": 80
            },
            "precision": {
              "numerator": 40,
              "denominator": 44,
              "value": 0.9090909090909091,
              "wilson95": {
                "low": 0.7884076083340138,
                "high": 0.9640778067726837
              }
            },
            "recall": {
              "numerator": 40,
              "denominator": 40,
              "value": 1.0,
              "wilson95": {
                "low": 0.9123783988027135,
                "high": 1.0
              }
            },
            "f1": {
              "numerator": 80,
              "denominator": 84,
              "value": 0.9523809523809523
            },
            "mcc": 0.9045340337332909
          },
          "strata": {
            "language:python": {
              "counts": {
                "tp": 40,
                "fp": 4,
                "fn": 0,
                "tn": 36,
                "decisions": 80
              },
              "precision": {
                "numerator": 40,
                "denominator": 44,
                "value": 0.9090909090909091,
                "wilson95": {
                  "low": 0.7884076083340138,
                  "high": 0.9640778067726837
                }
              },
              "recall": {
                "numerator": 40,
                "denominator": 40,
                "value": 1.0,
                "wilson95": {
                  "low": 0.9123783988027135,
                  "high": 1.0
                }
              },
              "f1": {
                "numerator": 80,
                "denominator": 84,
                "value": 0.9523809523809523
              },
              "mcc": 0.9045340337332909
            },
            "transform:alias_import": {
              "counts": {
                "tp": 13,
                "fp": 0,
                "fn": 0,
                "tn": 0,
                "decisions": 13
              },
              "precision": {
                "numerator": 13,
                "denominator": 13,
                "value": 1.0,
                "wilson95": {
                  "low": 0.7719046276458016,
                  "high": 0.9999999999999999
                }
              },
              "recall": {
                "numerator": 13,
                "denominator": 13,
                "value": 1.0,
                "wilson95": {
                  "low": 0.7719046276458016,
                  "high": 0.9999999999999999
                }
              },
              "f1": {
                "numerator": 26,
                "denominator": 26,
                "value": 1.0
              },
              "mcc": null
            },
            "transform:comment": {
              "counts": {
                "tp": 0,
                "fp": 0,
                "fn": 0,
                "tn": 8,
                "decisions": 8
              },
              "precision": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "recall": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "f1": {
                "numerator": 0,
                "denominator": 0,
                "value": null
              },
              "mcc": null
            },
            "transform:dead_comment": {
              "counts": {
                "tp": 0,
                "fp": 0,
                "fn": 0,
                "tn": 8,
                "decisions": 8
              },
              "precision": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "recall": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "f1": {
                "numerator": 0,
                "denominator": 0,
                "value": null
              },
              "mcc": null
            },
            "transform:direct_import": {
              "counts": {
                "tp": 14,
                "fp": 0,
                "fn": 0,
                "tn": 0,
                "decisions": 14
              },
              "precision": {
                "numerator": 14,
                "denominator": 14,
                "value": 1.0,
                "wilson95": {
                  "low": 0.7846891972623643,
                  "high": 1.0
                }
              },
              "recall": {
                "numerator": 14,
                "denominator": 14,
                "value": 1.0,
                "wilson95": {
                  "low": 0.7846891972623643,
                  "high": 1.0
                }
              },
              "f1": {
                "numerator": 28,
                "denominator": 28,
                "value": 1.0
              },
              "mcc": null
            },
            "transform:documentation": {
              "counts": {
                "tp": 0,
                "fp": 0,
                "fn": 0,
                "tn": 8,
                "decisions": 8
              },
              "precision": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "recall": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "f1": {
                "numerator": 0,
                "denominator": 0,
                "value": null
              },
              "mcc": null
            },
            "transform:from_import": {
              "counts": {
                "tp": 13,
                "fp": 0,
                "fn": 0,
                "tn": 0,
                "decisions": 13
              },
              "precision": {
                "numerator": 13,
                "denominator": 13,
                "value": 1.0,
                "wilson95": {
                  "low": 0.7719046276458016,
                  "high": 0.9999999999999999
                }
              },
              "recall": {
                "numerator": 13,
                "denominator": 13,
                "value": 1.0,
                "wilson95": {
                  "low": 0.7719046276458016,
                  "high": 0.9999999999999999
                }
              },
              "f1": {
                "numerator": 26,
                "denominator": 26,
                "value": 1.0
              },
              "mcc": null
            },
            "transform:near_name": {
              "counts": {
                "tp": 0,
                "fp": 4,
                "fn": 0,
                "tn": 4,
                "decisions": 8
              },
              "precision": {
                "numerator": 0,
                "denominator": 4,
                "value": 0.0,
                "wilson95": {
                  "low": 0.0,
                  "high": 0.4898908364545973
                }
              },
              "recall": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "f1": {
                "numerator": 0,
                "denominator": 4,
                "value": 0.0
              },
              "mcc": null
            },
            "transform:string_literal": {
              "counts": {
                "tp": 0,
                "fp": 0,
                "fn": 0,
                "tn": 8,
                "decisions": 8
              },
              "precision": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "recall": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "f1": {
                "numerator": 0,
                "denominator": 0,
                "value": null
              },
              "mcc": null
            }
          },
          "synthetic_metric_eligible": true,
          "headline_eligible": false,
          "headline_blockers": [
            "synthetic transformations are correlated families",
            "real-repository labelled accuracy unavailable",
            "comparative, determinism, network, public-claim and demand gates are evaluated outside this score file"
          ]
        },
        "B": {
          "complete": true,
          "applicable_decisions": 80,
          "valid_decisions": 80,
          "failed_decision_ids": [],
          "metrics": {
            "counts": {
              "tp": 40,
              "fp": 0,
              "fn": 0,
              "tn": 40,
              "decisions": 80
            },
            "precision": {
              "numerator": 40,
              "denominator": 40,
              "value": 1.0,
              "wilson95": {
                "low": 0.9123783988027135,
                "high": 1.0
              }
            },
            "recall": {
              "numerator": 40,
              "denominator": 40,
              "value": 1.0,
              "wilson95": {
                "low": 0.9123783988027135,
                "high": 1.0
              }
            },
            "f1": {
              "numerator": 80,
              "denominator": 80,
              "value": 1.0
            },
            "mcc": 1.0
          },
          "strata": {
            "language:html": {
              "counts": {
                "tp": 40,
                "fp": 0,
                "fn": 0,
                "tn": 40,
                "decisions": 80
              },
              "precision": {
                "numerator": 40,
                "denominator": 40,
                "value": 1.0,
                "wilson95": {
                  "low": 0.9123783988027135,
                  "high": 1.0
                }
              },
              "recall": {
                "numerator": 40,
                "denominator": 40,
                "value": 1.0,
                "wilson95": {
                  "low": 0.9123783988027135,
                  "high": 1.0
                }
              },
              "f1": {
                "numerator": 80,
                "denominator": 80,
                "value": 1.0
              },
              "mcc": 1.0
            },
            "transform:biometric_notice:language_attribute": {
              "counts": {
                "tp": 2,
                "fp": 0,
                "fn": 0,
                "tn": 0,
                "decisions": 2
              },
              "precision": {
                "numerator": 2,
                "denominator": 2,
                "value": 1.0,
                "wilson95": {
                  "low": 0.34238022750665303,
                  "high": 1.0
                }
              },
              "recall": {
                "numerator": 2,
                "denominator": 2,
                "value": 1.0,
                "wilson95": {
                  "low": 0.34238022750665303,
                  "high": 1.0
                }
              },
              "f1": {
                "numerator": 4,
                "denominator": 4,
                "value": 1.0
              },
              "mcc": null
            },
            "transform:biometric_notice:nested_template": {
              "counts": {
                "tp": 3,
                "fp": 0,
                "fn": 0,
                "tn": 0,
                "decisions": 3
              },
              "precision": {
                "numerator": 3,
                "denominator": 3,
                "value": 1.0,
                "wilson95": {
                  "low": 0.4385029682449546,
                  "high": 1.0
                }
              },
              "recall": {
                "numerator": 3,
                "denominator": 3,
                "value": 1.0,
                "wilson95": {
                  "low": 0.4385029682449546,
                  "high": 1.0
                }
              },
              "f1": {
                "numerator": 6,
                "denominator": 6,
                "value": 1.0
              },
              "mcc": null
            },
            "transform:biometric_notice:rendered_body": {
              "counts": {
                "tp": 3,
                "fp": 0,
                "fn": 0,
                "tn": 0,
                "decisions": 3
              },
              "precision": {
                "numerator": 3,
                "denominator": 3,
                "value": 1.0,
                "wilson95": {
                  "low": 0.4385029682449546,
                  "high": 1.0
                }
              },
              "recall": {
                "numerator": 3,
                "denominator": 3,
                "value": 1.0,
                "wilson95": {
                  "low": 0.4385029682449546,
                  "high": 1.0
                }
              },
              "f1": {
                "numerator": 6,
                "denominator": 6,
                "value": 1.0
              },
              "mcc": null
            },
            "transform:chatbot_notice:language_attribute": {
              "counts": {
                "tp": 3,
                "fp": 0,
                "fn": 0,
                "tn": 0,
                "decisions": 3
              },
              "precision": {
                "numerator": 3,
                "denominator": 3,
                "value": 1.0,
                "wilson95": {
                  "low": 0.4385029682449546,
                  "high": 1.0
                }
              },
              "recall": {
                "numerator": 3,
                "denominator": 3,
                "value": 1.0,
                "wilson95": {
                  "low": 0.4385029682449546,
                  "high": 1.0
                }
              },
              "f1": {
                "numerator": 6,
                "denominator": 6,
                "value": 1.0
              },
              "mcc": null
            },
            "transform:chatbot_notice:nested_template": {
              "counts": {
                "tp": 2,
                "fp": 0,
                "fn": 0,
                "tn": 0,
                "decisions": 2
              },
              "precision": {
                "numerator": 2,
                "denominator": 2,
                "value": 1.0,
                "wilson95": {
                  "low": 0.34238022750665303,
                  "high": 1.0
                }
              },
              "recall": {
                "numerator": 2,
                "denominator": 2,
                "value": 1.0,
                "wilson95": {
                  "low": 0.34238022750665303,
                  "high": 1.0
                }
              },
              "f1": {
                "numerator": 4,
                "denominator": 4,
                "value": 1.0
              },
              "mcc": null
            },
            "transform:chatbot_notice:rendered_body": {
              "counts": {
                "tp": 3,
                "fp": 0,
                "fn": 0,
                "tn": 0,
                "decisions": 3
              },
              "precision": {
                "numerator": 3,
                "denominator": 3,
                "value": 1.0,
                "wilson95": {
                  "low": 0.4385029682449546,
                  "high": 1.0
                }
              },
              "recall": {
                "numerator": 3,
                "denominator": 3,
                "value": 1.0,
                "wilson95": {
                  "low": 0.4385029682449546,
                  "high": 1.0
                }
              },
              "f1": {
                "numerator": 6,
                "denominator": 6,
                "value": 1.0
              },
              "mcc": null
            },
            "transform:deepfake_notice:language_attribute": {
              "counts": {
                "tp": 3,
                "fp": 0,
                "fn": 0,
                "tn": 0,
                "decisions": 3
              },
              "precision": {
                "numerator": 3,
                "denominator": 3,
                "value": 1.0,
                "wilson95": {
                  "low": 0.4385029682449546,
                  "high": 1.0
                }
              },
              "recall": {
                "numerator": 3,
                "denominator": 3,
                "value": 1.0,
                "wilson95": {
                  "low": 0.4385029682449546,
                  "high": 1.0
                }
              },
              "f1": {
                "numerator": 6,
                "denominator": 6,
                "value": 1.0
              },
              "mcc": null
            },
            "transform:deepfake_notice:nested_template": {
              "counts": {
                "tp": 3,
                "fp": 0,
                "fn": 0,
                "tn": 0,
                "decisions": 3
              },
              "precision": {
                "numerator": 3,
                "denominator": 3,
                "value": 1.0,
                "wilson95": {
                  "low": 0.4385029682449546,
                  "high": 1.0
                }
              },
              "recall": {
                "numerator": 3,
                "denominator": 3,
                "value": 1.0,
                "wilson95": {
                  "low": 0.4385029682449546,
                  "high": 1.0
                }
              },
              "f1": {
                "numerator": 6,
                "denominator": 6,
                "value": 1.0
              },
              "mcc": null
            },
            "transform:deepfake_notice:rendered_body": {
              "counts": {
                "tp": 2,
                "fp": 0,
                "fn": 0,
                "tn": 0,
                "decisions": 2
              },
              "precision": {
                "numerator": 2,
                "denominator": 2,
                "value": 1.0,
                "wilson95": {
                  "low": 0.34238022750665303,
                  "high": 1.0
                }
              },
              "recall": {
                "numerator": 2,
                "denominator": 2,
                "value": 1.0,
                "wilson95": {
                  "low": 0.34238022750665303,
                  "high": 1.0
                }
              },
              "f1": {
                "numerator": 4,
                "denominator": 4,
                "value": 1.0
              },
              "mcc": null
            },
            "transform:developer_note": {
              "counts": {
                "tp": 0,
                "fp": 0,
                "fn": 0,
                "tn": 8,
                "decisions": 8
              },
              "precision": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "recall": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "f1": {
                "numerator": 0,
                "denominator": 0,
                "value": null
              },
              "mcc": null
            },
            "transform:emotion_notice:language_attribute": {
              "counts": {
                "tp": 3,
                "fp": 0,
                "fn": 0,
                "tn": 0,
                "decisions": 3
              },
              "precision": {
                "numerator": 3,
                "denominator": 3,
                "value": 1.0,
                "wilson95": {
                  "low": 0.4385029682449546,
                  "high": 1.0
                }
              },
              "recall": {
                "numerator": 3,
                "denominator": 3,
                "value": 1.0,
                "wilson95": {
                  "low": 0.4385029682449546,
                  "high": 1.0
                }
              },
              "f1": {
                "numerator": 6,
                "denominator": 6,
                "value": 1.0
              },
              "mcc": null
            },
            "transform:emotion_notice:nested_template": {
              "counts": {
                "tp": 2,
                "fp": 0,
                "fn": 0,
                "tn": 0,
                "decisions": 2
              },
              "precision": {
                "numerator": 2,
                "denominator": 2,
                "value": 1.0,
                "wilson95": {
                  "low": 0.34238022750665303,
                  "high": 1.0
                }
              },
              "recall": {
                "numerator": 2,
                "denominator": 2,
                "value": 1.0,
                "wilson95": {
                  "low": 0.34238022750665303,
                  "high": 1.0
                }
              },
              "f1": {
                "numerator": 4,
                "denominator": 4,
                "value": 1.0
              },
              "mcc": null
            },
            "transform:emotion_notice:rendered_body": {
              "counts": {
                "tp": 3,
                "fp": 0,
                "fn": 0,
                "tn": 0,
                "decisions": 3
              },
              "precision": {
                "numerator": 3,
                "denominator": 3,
                "value": 1.0,
                "wilson95": {
                  "low": 0.4385029682449546,
                  "high": 1.0
                }
              },
              "recall": {
                "numerator": 3,
                "denominator": 3,
                "value": 1.0,
                "wilson95": {
                  "low": 0.4385029682449546,
                  "high": 1.0
                }
              },
              "f1": {
                "numerator": 6,
                "denominator": 6,
                "value": 1.0
              },
              "mcc": null
            },
            "transform:html_comment": {
              "counts": {
                "tp": 0,
                "fp": 0,
                "fn": 0,
                "tn": 8,
                "decisions": 8
              },
              "precision": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "recall": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "f1": {
                "numerator": 0,
                "denominator": 0,
                "value": null
              },
              "mcc": null
            },
            "transform:irrelevant_attribute": {
              "counts": {
                "tp": 0,
                "fp": 0,
                "fn": 0,
                "tn": 8,
                "decisions": 8
              },
              "precision": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "recall": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "f1": {
                "numerator": 0,
                "denominator": 0,
                "value": null
              },
              "mcc": null
            },
            "transform:negated_copy": {
              "counts": {
                "tp": 0,
                "fp": 0,
                "fn": 0,
                "tn": 8,
                "decisions": 8
              },
              "precision": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "recall": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "f1": {
                "numerator": 0,
                "denominator": 0,
                "value": null
              },
              "mcc": null
            },
            "transform:non_rendered_template": {
              "counts": {
                "tp": 0,
                "fp": 0,
                "fn": 0,
                "tn": 8,
                "decisions": 8
              },
              "precision": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "recall": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "f1": {
                "numerator": 0,
                "denominator": 0,
                "value": null
              },
              "mcc": null
            },
            "transform:synthetic_marker:language_attribute": {
              "counts": {
                "tp": 2,
                "fp": 0,
                "fn": 0,
                "tn": 0,
                "decisions": 2
              },
              "precision": {
                "numerator": 2,
                "denominator": 2,
                "value": 1.0,
                "wilson95": {
                  "low": 0.34238022750665303,
                  "high": 1.0
                }
              },
              "recall": {
                "numerator": 2,
                "denominator": 2,
                "value": 1.0,
                "wilson95": {
                  "low": 0.34238022750665303,
                  "high": 1.0
                }
              },
              "f1": {
                "numerator": 4,
                "denominator": 4,
                "value": 1.0
              },
              "mcc": null
            },
            "transform:synthetic_marker:nested_template": {
              "counts": {
                "tp": 3,
                "fp": 0,
                "fn": 0,
                "tn": 0,
                "decisions": 3
              },
              "precision": {
                "numerator": 3,
                "denominator": 3,
                "value": 1.0,
                "wilson95": {
                  "low": 0.4385029682449546,
                  "high": 1.0
                }
              },
              "recall": {
                "numerator": 3,
                "denominator": 3,
                "value": 1.0,
                "wilson95": {
                  "low": 0.4385029682449546,
                  "high": 1.0
                }
              },
              "f1": {
                "numerator": 6,
                "denominator": 6,
                "value": 1.0
              },
              "mcc": null
            },
            "transform:synthetic_marker:rendered_body": {
              "counts": {
                "tp": 3,
                "fp": 0,
                "fn": 0,
                "tn": 0,
                "decisions": 3
              },
              "precision": {
                "numerator": 3,
                "denominator": 3,
                "value": 1.0,
                "wilson95": {
                  "low": 0.4385029682449546,
                  "high": 1.0
                }
              },
              "recall": {
                "numerator": 3,
                "denominator": 3,
                "value": 1.0,
                "wilson95": {
                  "low": 0.4385029682449546,
                  "high": 1.0
                }
              },
              "f1": {
                "numerator": 6,
                "denominator": 6,
                "value": 1.0
              },
              "mcc": null
            }
          },
          "synthetic_metric_eligible": true,
          "headline_eligible": false,
          "headline_blockers": [
            "synthetic transformations are correlated families",
            "real-repository labelled accuracy unavailable",
            "comparative, determinism, network, public-claim and demand gates are evaluated outside this score file"
          ]
        }
      }
    },
    {
      "result_path": "/tmp/regula-commercial-20260731.Inq4k2/synthetic-naive-2/results.json",
      "tool": "naive",
      "result_sha256": "29077cf8ed190561bf7dc3b96410d514767bdc9437feb50cbf483c63a50edb24",
      "enumeration_complete": true,
      "missing_ids": [],
      "extra_ids": [],
      "duplicate_ids": [],
      "failed_ids": [],
      "candidates": {
        "A": {
          "complete": true,
          "applicable_decisions": 80,
          "valid_decisions": 80,
          "failed_decision_ids": [],
          "metrics": {
            "counts": {
              "tp": 40,
              "fp": 4,
              "fn": 0,
              "tn": 36,
              "decisions": 80
            },
            "precision": {
              "numerator": 40,
              "denominator": 44,
              "value": 0.9090909090909091,
              "wilson95": {
                "low": 0.7884076083340138,
                "high": 0.9640778067726837
              }
            },
            "recall": {
              "numerator": 40,
              "denominator": 40,
              "value": 1.0,
              "wilson95": {
                "low": 0.9123783988027135,
                "high": 1.0
              }
            },
            "f1": {
              "numerator": 80,
              "denominator": 84,
              "value": 0.9523809523809523
            },
            "mcc": 0.9045340337332909
          },
          "strata": {
            "language:python": {
              "counts": {
                "tp": 40,
                "fp": 4,
                "fn": 0,
                "tn": 36,
                "decisions": 80
              },
              "precision": {
                "numerator": 40,
                "denominator": 44,
                "value": 0.9090909090909091,
                "wilson95": {
                  "low": 0.7884076083340138,
                  "high": 0.9640778067726837
                }
              },
              "recall": {
                "numerator": 40,
                "denominator": 40,
                "value": 1.0,
                "wilson95": {
                  "low": 0.9123783988027135,
                  "high": 1.0
                }
              },
              "f1": {
                "numerator": 80,
                "denominator": 84,
                "value": 0.9523809523809523
              },
              "mcc": 0.9045340337332909
            },
            "transform:alias_import": {
              "counts": {
                "tp": 13,
                "fp": 0,
                "fn": 0,
                "tn": 0,
                "decisions": 13
              },
              "precision": {
                "numerator": 13,
                "denominator": 13,
                "value": 1.0,
                "wilson95": {
                  "low": 0.7719046276458016,
                  "high": 0.9999999999999999
                }
              },
              "recall": {
                "numerator": 13,
                "denominator": 13,
                "value": 1.0,
                "wilson95": {
                  "low": 0.7719046276458016,
                  "high": 0.9999999999999999
                }
              },
              "f1": {
                "numerator": 26,
                "denominator": 26,
                "value": 1.0
              },
              "mcc": null
            },
            "transform:comment": {
              "counts": {
                "tp": 0,
                "fp": 0,
                "fn": 0,
                "tn": 8,
                "decisions": 8
              },
              "precision": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "recall": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "f1": {
                "numerator": 0,
                "denominator": 0,
                "value": null
              },
              "mcc": null
            },
            "transform:dead_comment": {
              "counts": {
                "tp": 0,
                "fp": 0,
                "fn": 0,
                "tn": 8,
                "decisions": 8
              },
              "precision": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "recall": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "f1": {
                "numerator": 0,
                "denominator": 0,
                "value": null
              },
              "mcc": null
            },
            "transform:direct_import": {
              "counts": {
                "tp": 14,
                "fp": 0,
                "fn": 0,
                "tn": 0,
                "decisions": 14
              },
              "precision": {
                "numerator": 14,
                "denominator": 14,
                "value": 1.0,
                "wilson95": {
                  "low": 0.7846891972623643,
                  "high": 1.0
                }
              },
              "recall": {
                "numerator": 14,
                "denominator": 14,
                "value": 1.0,
                "wilson95": {
                  "low": 0.7846891972623643,
                  "high": 1.0
                }
              },
              "f1": {
                "numerator": 28,
                "denominator": 28,
                "value": 1.0
              },
              "mcc": null
            },
            "transform:documentation": {
              "counts": {
                "tp": 0,
                "fp": 0,
                "fn": 0,
                "tn": 8,
                "decisions": 8
              },
              "precision": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "recall": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "f1": {
                "numerator": 0,
                "denominator": 0,
                "value": null
              },
              "mcc": null
            },
            "transform:from_import": {
              "counts": {
                "tp": 13,
                "fp": 0,
                "fn": 0,
                "tn": 0,
                "decisions": 13
              },
              "precision": {
                "numerator": 13,
                "denominator": 13,
                "value": 1.0,
                "wilson95": {
                  "low": 0.7719046276458016,
                  "high": 0.9999999999999999
                }
              },
              "recall": {
                "numerator": 13,
                "denominator": 13,
                "value": 1.0,
                "wilson95": {
                  "low": 0.7719046276458016,
                  "high": 0.9999999999999999
                }
              },
              "f1": {
                "numerator": 26,
                "denominator": 26,
                "value": 1.0
              },
              "mcc": null
            },
            "transform:near_name": {
              "counts": {
                "tp": 0,
                "fp": 4,
                "fn": 0,
                "tn": 4,
                "decisions": 8
              },
              "precision": {
                "numerator": 0,
                "denominator": 4,
                "value": 0.0,
                "wilson95": {
                  "low": 0.0,
                  "high": 0.4898908364545973
                }
              },
              "recall": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "f1": {
                "numerator": 0,
                "denominator": 4,
                "value": 0.0
              },
              "mcc": null
            },
            "transform:string_literal": {
              "counts": {
                "tp": 0,
                "fp": 0,
                "fn": 0,
                "tn": 8,
                "decisions": 8
              },
              "precision": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "recall": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "f1": {
                "numerator": 0,
                "denominator": 0,
                "value": null
              },
              "mcc": null
            }
          },
          "synthetic_metric_eligible": true,
          "headline_eligible": false,
          "headline_blockers": [
            "synthetic transformations are correlated families",
            "real-repository labelled accuracy unavailable",
            "comparative, determinism, network, public-claim and demand gates are evaluated outside this score file"
          ]
        },
        "B": {
          "complete": true,
          "applicable_decisions": 80,
          "valid_decisions": 80,
          "failed_decision_ids": [],
          "metrics": {
            "counts": {
              "tp": 40,
              "fp": 0,
              "fn": 0,
              "tn": 40,
              "decisions": 80
            },
            "precision": {
              "numerator": 40,
              "denominator": 40,
              "value": 1.0,
              "wilson95": {
                "low": 0.9123783988027135,
                "high": 1.0
              }
            },
            "recall": {
              "numerator": 40,
              "denominator": 40,
              "value": 1.0,
              "wilson95": {
                "low": 0.9123783988027135,
                "high": 1.0
              }
            },
            "f1": {
              "numerator": 80,
              "denominator": 80,
              "value": 1.0
            },
            "mcc": 1.0
          },
          "strata": {
            "language:html": {
              "counts": {
                "tp": 40,
                "fp": 0,
                "fn": 0,
                "tn": 40,
                "decisions": 80
              },
              "precision": {
                "numerator": 40,
                "denominator": 40,
                "value": 1.0,
                "wilson95": {
                  "low": 0.9123783988027135,
                  "high": 1.0
                }
              },
              "recall": {
                "numerator": 40,
                "denominator": 40,
                "value": 1.0,
                "wilson95": {
                  "low": 0.9123783988027135,
                  "high": 1.0
                }
              },
              "f1": {
                "numerator": 80,
                "denominator": 80,
                "value": 1.0
              },
              "mcc": 1.0
            },
            "transform:biometric_notice:language_attribute": {
              "counts": {
                "tp": 2,
                "fp": 0,
                "fn": 0,
                "tn": 0,
                "decisions": 2
              },
              "precision": {
                "numerator": 2,
                "denominator": 2,
                "value": 1.0,
                "wilson95": {
                  "low": 0.34238022750665303,
                  "high": 1.0
                }
              },
              "recall": {
                "numerator": 2,
                "denominator": 2,
                "value": 1.0,
                "wilson95": {
                  "low": 0.34238022750665303,
                  "high": 1.0
                }
              },
              "f1": {
                "numerator": 4,
                "denominator": 4,
                "value": 1.0
              },
              "mcc": null
            },
            "transform:biometric_notice:nested_template": {
              "counts": {
                "tp": 3,
                "fp": 0,
                "fn": 0,
                "tn": 0,
                "decisions": 3
              },
              "precision": {
                "numerator": 3,
                "denominator": 3,
                "value": 1.0,
                "wilson95": {
                  "low": 0.4385029682449546,
                  "high": 1.0
                }
              },
              "recall": {
                "numerator": 3,
                "denominator": 3,
                "value": 1.0,
                "wilson95": {
                  "low": 0.4385029682449546,
                  "high": 1.0
                }
              },
              "f1": {
                "numerator": 6,
                "denominator": 6,
                "value": 1.0
              },
              "mcc": null
            },
            "transform:biometric_notice:rendered_body": {
              "counts": {
                "tp": 3,
                "fp": 0,
                "fn": 0,
                "tn": 0,
                "decisions": 3
              },
              "precision": {
                "numerator": 3,
                "denominator": 3,
                "value": 1.0,
                "wilson95": {
                  "low": 0.4385029682449546,
                  "high": 1.0
                }
              },
              "recall": {
                "numerator": 3,
                "denominator": 3,
                "value": 1.0,
                "wilson95": {
                  "low": 0.4385029682449546,
                  "high": 1.0
                }
              },
              "f1": {
                "numerator": 6,
                "denominator": 6,
                "value": 1.0
              },
              "mcc": null
            },
            "transform:chatbot_notice:language_attribute": {
              "counts": {
                "tp": 3,
                "fp": 0,
                "fn": 0,
                "tn": 0,
                "decisions": 3
              },
              "precision": {
                "numerator": 3,
                "denominator": 3,
                "value": 1.0,
                "wilson95": {
                  "low": 0.4385029682449546,
                  "high": 1.0
                }
              },
              "recall": {
                "numerator": 3,
                "denominator": 3,
                "value": 1.0,
                "wilson95": {
                  "low": 0.4385029682449546,
                  "high": 1.0
                }
              },
              "f1": {
                "numerator": 6,
                "denominator": 6,
                "value": 1.0
              },
              "mcc": null
            },
            "transform:chatbot_notice:nested_template": {
              "counts": {
                "tp": 2,
                "fp": 0,
                "fn": 0,
                "tn": 0,
                "decisions": 2
              },
              "precision": {
                "numerator": 2,
                "denominator": 2,
                "value": 1.0,
                "wilson95": {
                  "low": 0.34238022750665303,
                  "high": 1.0
                }
              },
              "recall": {
                "numerator": 2,
                "denominator": 2,
                "value": 1.0,
                "wilson95": {
                  "low": 0.34238022750665303,
                  "high": 1.0
                }
              },
              "f1": {
                "numerator": 4,
                "denominator": 4,
                "value": 1.0
              },
              "mcc": null
            },
            "transform:chatbot_notice:rendered_body": {
              "counts": {
                "tp": 3,
                "fp": 0,
                "fn": 0,
                "tn": 0,
                "decisions": 3
              },
              "precision": {
                "numerator": 3,
                "denominator": 3,
                "value": 1.0,
                "wilson95": {
                  "low": 0.4385029682449546,
                  "high": 1.0
                }
              },
              "recall": {
                "numerator": 3,
                "denominator": 3,
                "value": 1.0,
                "wilson95": {
                  "low": 0.4385029682449546,
                  "high": 1.0
                }
              },
              "f1": {
                "numerator": 6,
                "denominator": 6,
                "value": 1.0
              },
              "mcc": null
            },
            "transform:deepfake_notice:language_attribute": {
              "counts": {
                "tp": 3,
                "fp": 0,
                "fn": 0,
                "tn": 0,
                "decisions": 3
              },
              "precision": {
                "numerator": 3,
                "denominator": 3,
                "value": 1.0,
                "wilson95": {
                  "low": 0.4385029682449546,
                  "high": 1.0
                }
              },
              "recall": {
                "numerator": 3,
                "denominator": 3,
                "value": 1.0,
                "wilson95": {
                  "low": 0.4385029682449546,
                  "high": 1.0
                }
              },
              "f1": {
                "numerator": 6,
                "denominator": 6,
                "value": 1.0
              },
              "mcc": null
            },
            "transform:deepfake_notice:nested_template": {
              "counts": {
                "tp": 3,
                "fp": 0,
                "fn": 0,
                "tn": 0,
                "decisions": 3
              },
              "precision": {
                "numerator": 3,
                "denominator": 3,
                "value": 1.0,
                "wilson95": {
                  "low": 0.4385029682449546,
                  "high": 1.0
                }
              },
              "recall": {
                "numerator": 3,
                "denominator": 3,
                "value": 1.0,
                "wilson95": {
                  "low": 0.4385029682449546,
                  "high": 1.0
                }
              },
              "f1": {
                "numerator": 6,
                "denominator": 6,
                "value": 1.0
              },
              "mcc": null
            },
            "transform:deepfake_notice:rendered_body": {
              "counts": {
                "tp": 2,
                "fp": 0,
                "fn": 0,
                "tn": 0,
                "decisions": 2
              },
              "precision": {
                "numerator": 2,
                "denominator": 2,
                "value": 1.0,
                "wilson95": {
                  "low": 0.34238022750665303,
                  "high": 1.0
                }
              },
              "recall": {
                "numerator": 2,
                "denominator": 2,
                "value": 1.0,
                "wilson95": {
                  "low": 0.34238022750665303,
                  "high": 1.0
                }
              },
              "f1": {
                "numerator": 4,
                "denominator": 4,
                "value": 1.0
              },
              "mcc": null
            },
            "transform:developer_note": {
              "counts": {
                "tp": 0,
                "fp": 0,
                "fn": 0,
                "tn": 8,
                "decisions": 8
              },
              "precision": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "recall": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "f1": {
                "numerator": 0,
                "denominator": 0,
                "value": null
              },
              "mcc": null
            },
            "transform:emotion_notice:language_attribute": {
              "counts": {
                "tp": 3,
                "fp": 0,
                "fn": 0,
                "tn": 0,
                "decisions": 3
              },
              "precision": {
                "numerator": 3,
                "denominator": 3,
                "value": 1.0,
                "wilson95": {
                  "low": 0.4385029682449546,
                  "high": 1.0
                }
              },
              "recall": {
                "numerator": 3,
                "denominator": 3,
                "value": 1.0,
                "wilson95": {
                  "low": 0.4385029682449546,
                  "high": 1.0
                }
              },
              "f1": {
                "numerator": 6,
                "denominator": 6,
                "value": 1.0
              },
              "mcc": null
            },
            "transform:emotion_notice:nested_template": {
              "counts": {
                "tp": 2,
                "fp": 0,
                "fn": 0,
                "tn": 0,
                "decisions": 2
              },
              "precision": {
                "numerator": 2,
                "denominator": 2,
                "value": 1.0,
                "wilson95": {
                  "low": 0.34238022750665303,
                  "high": 1.0
                }
              },
              "recall": {
                "numerator": 2,
                "denominator": 2,
                "value": 1.0,
                "wilson95": {
                  "low": 0.34238022750665303,
                  "high": 1.0
                }
              },
              "f1": {
                "numerator": 4,
                "denominator": 4,
                "value": 1.0
              },
              "mcc": null
            },
            "transform:emotion_notice:rendered_body": {
              "counts": {
                "tp": 3,
                "fp": 0,
                "fn": 0,
                "tn": 0,
                "decisions": 3
              },
              "precision": {
                "numerator": 3,
                "denominator": 3,
                "value": 1.0,
                "wilson95": {
                  "low": 0.4385029682449546,
                  "high": 1.0
                }
              },
              "recall": {
                "numerator": 3,
                "denominator": 3,
                "value": 1.0,
                "wilson95": {
                  "low": 0.4385029682449546,
                  "high": 1.0
                }
              },
              "f1": {
                "numerator": 6,
                "denominator": 6,
                "value": 1.0
              },
              "mcc": null
            },
            "transform:html_comment": {
              "counts": {
                "tp": 0,
                "fp": 0,
                "fn": 0,
                "tn": 8,
                "decisions": 8
              },
              "precision": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "recall": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "f1": {
                "numerator": 0,
                "denominator": 0,
                "value": null
              },
              "mcc": null
            },
            "transform:irrelevant_attribute": {
              "counts": {
                "tp": 0,
                "fp": 0,
                "fn": 0,
                "tn": 8,
                "decisions": 8
              },
              "precision": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "recall": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "f1": {
                "numerator": 0,
                "denominator": 0,
                "value": null
              },
              "mcc": null
            },
            "transform:negated_copy": {
              "counts": {
                "tp": 0,
                "fp": 0,
                "fn": 0,
                "tn": 8,
                "decisions": 8
              },
              "precision": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "recall": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "f1": {
                "numerator": 0,
                "denominator": 0,
                "value": null
              },
              "mcc": null
            },
            "transform:non_rendered_template": {
              "counts": {
                "tp": 0,
                "fp": 0,
                "fn": 0,
                "tn": 8,
                "decisions": 8
              },
              "precision": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "recall": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "f1": {
                "numerator": 0,
                "denominator": 0,
                "value": null
              },
              "mcc": null
            },
            "transform:synthetic_marker:language_attribute": {
              "counts": {
                "tp": 2,
                "fp": 0,
                "fn": 0,
                "tn": 0,
                "decisions": 2
              },
              "precision": {
                "numerator": 2,
                "denominator": 2,
                "value": 1.0,
                "wilson95": {
                  "low": 0.34238022750665303,
                  "high": 1.0
                }
              },
              "recall": {
                "numerator": 2,
                "denominator": 2,
                "value": 1.0,
                "wilson95": {
                  "low": 0.34238022750665303,
                  "high": 1.0
                }
              },
              "f1": {
                "numerator": 4,
                "denominator": 4,
                "value": 1.0
              },
              "mcc": null
            },
            "transform:synthetic_marker:nested_template": {
              "counts": {
                "tp": 3,
                "fp": 0,
                "fn": 0,
                "tn": 0,
                "decisions": 3
              },
              "precision": {
                "numerator": 3,
                "denominator": 3,
                "value": 1.0,
                "wilson95": {
                  "low": 0.4385029682449546,
                  "high": 1.0
                }
              },
              "recall": {
                "numerator": 3,
                "denominator": 3,
                "value": 1.0,
                "wilson95": {
                  "low": 0.4385029682449546,
                  "high": 1.0
                }
              },
              "f1": {
                "numerator": 6,
                "denominator": 6,
                "value": 1.0
              },
              "mcc": null
            },
            "transform:synthetic_marker:rendered_body": {
              "counts": {
                "tp": 3,
                "fp": 0,
                "fn": 0,
                "tn": 0,
                "decisions": 3
              },
              "precision": {
                "numerator": 3,
                "denominator": 3,
                "value": 1.0,
                "wilson95": {
                  "low": 0.4385029682449546,
                  "high": 1.0
                }
              },
              "recall": {
                "numerator": 3,
                "denominator": 3,
                "value": 1.0,
                "wilson95": {
                  "low": 0.4385029682449546,
                  "high": 1.0
                }
              },
              "f1": {
                "numerator": 6,
                "denominator": 6,
                "value": 1.0
              },
              "mcc": null
            }
          },
          "synthetic_metric_eligible": true,
          "headline_eligible": false,
          "headline_blockers": [
            "synthetic transformations are correlated families",
            "real-repository labelled accuracy unavailable",
            "comparative, determinism, network, public-claim and demand gates are evaluated outside this score file"
          ]
        }
      }
    },
    {
      "result_path": "/tmp/regula-commercial-20260731.Inq4k2/synthetic-local-1/results.json",
      "tool": "local_head",
      "result_sha256": "8041bbb547ef56b9a586e457d95c7e641045a027d33c9933fcaaa7d3b70c26b6",
      "enumeration_complete": true,
      "missing_ids": [],
      "extra_ids": [],
      "duplicate_ids": [],
      "failed_ids": [],
      "candidates": {
        "A": {
          "complete": true,
          "applicable_decisions": 80,
          "valid_decisions": 80,
          "failed_decision_ids": [],
          "metrics": {
            "counts": {
              "tp": 0,
              "fp": 0,
              "fn": 40,
              "tn": 40,
              "decisions": 80
            },
            "precision": {
              "numerator": 0,
              "denominator": 0,
              "value": null,
              "wilson95": {
                "low": null,
                "high": null
              }
            },
            "recall": {
              "numerator": 0,
              "denominator": 40,
              "value": 0.0,
              "wilson95": {
                "low": 0.0,
                "high": 0.08762160119728664
              }
            },
            "f1": {
              "numerator": 0,
              "denominator": 40,
              "value": 0.0
            },
            "mcc": null
          },
          "strata": {
            "language:python": {
              "counts": {
                "tp": 0,
                "fp": 0,
                "fn": 40,
                "tn": 40,
                "decisions": 80
              },
              "precision": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "recall": {
                "numerator": 0,
                "denominator": 40,
                "value": 0.0,
                "wilson95": {
                  "low": 0.0,
                  "high": 0.08762160119728664
                }
              },
              "f1": {
                "numerator": 0,
                "denominator": 40,
                "value": 0.0
              },
              "mcc": null
            },
            "transform:alias_import": {
              "counts": {
                "tp": 0,
                "fp": 0,
                "fn": 13,
                "tn": 0,
                "decisions": 13
              },
              "precision": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "recall": {
                "numerator": 0,
                "denominator": 13,
                "value": 0.0,
                "wilson95": {
                  "low": 0.0,
                  "high": 0.22809537235419838
                }
              },
              "f1": {
                "numerator": 0,
                "denominator": 13,
                "value": 0.0
              },
              "mcc": null
            },
            "transform:comment": {
              "counts": {
                "tp": 0,
                "fp": 0,
                "fn": 0,
                "tn": 8,
                "decisions": 8
              },
              "precision": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "recall": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "f1": {
                "numerator": 0,
                "denominator": 0,
                "value": null
              },
              "mcc": null
            },
            "transform:dead_comment": {
              "counts": {
                "tp": 0,
                "fp": 0,
                "fn": 0,
                "tn": 8,
                "decisions": 8
              },
              "precision": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "recall": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "f1": {
                "numerator": 0,
                "denominator": 0,
                "value": null
              },
              "mcc": null
            },
            "transform:direct_import": {
              "counts": {
                "tp": 0,
                "fp": 0,
                "fn": 14,
                "tn": 0,
                "decisions": 14
              },
              "precision": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "recall": {
                "numerator": 0,
                "denominator": 14,
                "value": 0.0,
                "wilson95": {
                  "low": 1.3877787807814457e-17,
                  "high": 0.2153108027376358
                }
              },
              "f1": {
                "numerator": 0,
                "denominator": 14,
                "value": 0.0
              },
              "mcc": null
            },
            "transform:documentation": {
              "counts": {
                "tp": 0,
                "fp": 0,
                "fn": 0,
                "tn": 8,
                "decisions": 8
              },
              "precision": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "recall": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "f1": {
                "numerator": 0,
                "denominator": 0,
                "value": null
              },
              "mcc": null
            },
            "transform:from_import": {
              "counts": {
                "tp": 0,
                "fp": 0,
                "fn": 13,
                "tn": 0,
                "decisions": 13
              },
              "precision": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "recall": {
                "numerator": 0,
                "denominator": 13,
                "value": 0.0,
                "wilson95": {
                  "low": 0.0,
                  "high": 0.22809537235419838
                }
              },
              "f1": {
                "numerator": 0,
                "denominator": 13,
                "value": 0.0
              },
              "mcc": null
            },
            "transform:near_name": {
              "counts": {
                "tp": 0,
                "fp": 0,
                "fn": 0,
                "tn": 8,
                "decisions": 8
              },
              "precision": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "recall": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "f1": {
                "numerator": 0,
                "denominator": 0,
                "value": null
              },
              "mcc": null
            },
            "transform:string_literal": {
              "counts": {
                "tp": 0,
                "fp": 0,
                "fn": 0,
                "tn": 8,
                "decisions": 8
              },
              "precision": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "recall": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "f1": {
                "numerator": 0,
                "denominator": 0,
                "value": null
              },
              "mcc": null
            }
          },
          "synthetic_metric_eligible": true,
          "headline_eligible": false,
          "headline_blockers": [
            "synthetic transformations are correlated families",
            "real-repository labelled accuracy unavailable",
            "comparative, determinism, network, public-claim and demand gates are evaluated outside this score file"
          ]
        },
        "B": {
          "complete": true,
          "applicable_decisions": 80,
          "valid_decisions": 80,
          "failed_decision_ids": [],
          "metrics": {
            "counts": {
              "tp": 0,
              "fp": 0,
              "fn": 40,
              "tn": 40,
              "decisions": 80
            },
            "precision": {
              "numerator": 0,
              "denominator": 0,
              "value": null,
              "wilson95": {
                "low": null,
                "high": null
              }
            },
            "recall": {
              "numerator": 0,
              "denominator": 40,
              "value": 0.0,
              "wilson95": {
                "low": 0.0,
                "high": 0.08762160119728664
              }
            },
            "f1": {
              "numerator": 0,
              "denominator": 40,
              "value": 0.0
            },
            "mcc": null
          },
          "strata": {
            "language:html": {
              "counts": {
                "tp": 0,
                "fp": 0,
                "fn": 40,
                "tn": 40,
                "decisions": 80
              },
              "precision": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "recall": {
                "numerator": 0,
                "denominator": 40,
                "value": 0.0,
                "wilson95": {
                  "low": 0.0,
                  "high": 0.08762160119728664
                }
              },
              "f1": {
                "numerator": 0,
                "denominator": 40,
                "value": 0.0
              },
              "mcc": null
            },
            "transform:biometric_notice:language_attribute": {
              "counts": {
                "tp": 0,
                "fp": 0,
                "fn": 2,
                "tn": 0,
                "decisions": 2
              },
              "precision": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "recall": {
                "numerator": 0,
                "denominator": 2,
                "value": 0.0,
                "wilson95": {
                  "low": 0.0,
                  "high": 0.6576197724933469
                }
              },
              "f1": {
                "numerator": 0,
                "denominator": 2,
                "value": 0.0
              },
              "mcc": null
            },
            "transform:biometric_notice:nested_template": {
              "counts": {
                "tp": 0,
                "fp": 0,
                "fn": 3,
                "tn": 0,
                "decisions": 3
              },
              "precision": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "recall": {
                "numerator": 0,
                "denominator": 3,
                "value": 0.0,
                "wilson95": {
                  "low": 5.551115123125783e-17,
                  "high": 0.5614970317550454
                }
              },
              "f1": {
                "numerator": 0,
                "denominator": 3,
                "value": 0.0
              },
              "mcc": null
            },
            "transform:biometric_notice:rendered_body": {
              "counts": {
                "tp": 0,
                "fp": 0,
                "fn": 3,
                "tn": 0,
                "decisions": 3
              },
              "precision": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "recall": {
                "numerator": 0,
                "denominator": 3,
                "value": 0.0,
                "wilson95": {
                  "low": 5.551115123125783e-17,
                  "high": 0.5614970317550454
                }
              },
              "f1": {
                "numerator": 0,
                "denominator": 3,
                "value": 0.0
              },
              "mcc": null
            },
            "transform:chatbot_notice:language_attribute": {
              "counts": {
                "tp": 0,
                "fp": 0,
                "fn": 3,
                "tn": 0,
                "decisions": 3
              },
              "precision": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "recall": {
                "numerator": 0,
                "denominator": 3,
                "value": 0.0,
                "wilson95": {
                  "low": 5.551115123125783e-17,
                  "high": 0.5614970317550454
                }
              },
              "f1": {
                "numerator": 0,
                "denominator": 3,
                "value": 0.0
              },
              "mcc": null
            },
            "transform:chatbot_notice:nested_template": {
              "counts": {
                "tp": 0,
                "fp": 0,
                "fn": 2,
                "tn": 0,
                "decisions": 2
              },
              "precision": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "recall": {
                "numerator": 0,
                "denominator": 2,
                "value": 0.0,
                "wilson95": {
                  "low": 0.0,
                  "high": 0.6576197724933469
                }
              },
              "f1": {
                "numerator": 0,
                "denominator": 2,
                "value": 0.0
              },
              "mcc": null
            },
            "transform:chatbot_notice:rendered_body": {
              "counts": {
                "tp": 0,
                "fp": 0,
                "fn": 3,
                "tn": 0,
                "decisions": 3
              },
              "precision": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "recall": {
                "numerator": 0,
                "denominator": 3,
                "value": 0.0,
                "wilson95": {
                  "low": 5.551115123125783e-17,
                  "high": 0.5614970317550454
                }
              },
              "f1": {
                "numerator": 0,
                "denominator": 3,
                "value": 0.0
              },
              "mcc": null
            },
            "transform:deepfake_notice:language_attribute": {
              "counts": {
                "tp": 0,
                "fp": 0,
                "fn": 3,
                "tn": 0,
                "decisions": 3
              },
              "precision": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "recall": {
                "numerator": 0,
                "denominator": 3,
                "value": 0.0,
                "wilson95": {
                  "low": 5.551115123125783e-17,
                  "high": 0.5614970317550454
                }
              },
              "f1": {
                "numerator": 0,
                "denominator": 3,
                "value": 0.0
              },
              "mcc": null
            },
            "transform:deepfake_notice:nested_template": {
              "counts": {
                "tp": 0,
                "fp": 0,
                "fn": 3,
                "tn": 0,
                "decisions": 3
              },
              "precision": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "recall": {
                "numerator": 0,
                "denominator": 3,
                "value": 0.0,
                "wilson95": {
                  "low": 5.551115123125783e-17,
                  "high": 0.5614970317550454
                }
              },
              "f1": {
                "numerator": 0,
                "denominator": 3,
                "value": 0.0
              },
              "mcc": null
            },
            "transform:deepfake_notice:rendered_body": {
              "counts": {
                "tp": 0,
                "fp": 0,
                "fn": 2,
                "tn": 0,
                "decisions": 2
              },
              "precision": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "recall": {
                "numerator": 0,
                "denominator": 2,
                "value": 0.0,
                "wilson95": {
                  "low": 0.0,
                  "high": 0.6576197724933469
                }
              },
              "f1": {
                "numerator": 0,
                "denominator": 2,
                "value": 0.0
              },
              "mcc": null
            },
            "transform:developer_note": {
              "counts": {
                "tp": 0,
                "fp": 0,
                "fn": 0,
                "tn": 8,
                "decisions": 8
              },
              "precision": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "recall": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "f1": {
                "numerator": 0,
                "denominator": 0,
                "value": null
              },
              "mcc": null
            },
            "transform:emotion_notice:language_attribute": {
              "counts": {
                "tp": 0,
                "fp": 0,
                "fn": 3,
                "tn": 0,
                "decisions": 3
              },
              "precision": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "recall": {
                "numerator": 0,
                "denominator": 3,
                "value": 0.0,
                "wilson95": {
                  "low": 5.551115123125783e-17,
                  "high": 0.5614970317550454
                }
              },
              "f1": {
                "numerator": 0,
                "denominator": 3,
                "value": 0.0
              },
              "mcc": null
            },
            "transform:emotion_notice:nested_template": {
              "counts": {
                "tp": 0,
                "fp": 0,
                "fn": 2,
                "tn": 0,
                "decisions": 2
              },
              "precision": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "recall": {
                "numerator": 0,
                "denominator": 2,
                "value": 0.0,
                "wilson95": {
                  "low": 0.0,
                  "high": 0.6576197724933469
                }
              },
              "f1": {
                "numerator": 0,
                "denominator": 2,
                "value": 0.0
              },
              "mcc": null
            },
            "transform:emotion_notice:rendered_body": {
              "counts": {
                "tp": 0,
                "fp": 0,
                "fn": 3,
                "tn": 0,
                "decisions": 3
              },
              "precision": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "recall": {
                "numerator": 0,
                "denominator": 3,
                "value": 0.0,
                "wilson95": {
                  "low": 5.551115123125783e-17,
                  "high": 0.5614970317550454
                }
              },
              "f1": {
                "numerator": 0,
                "denominator": 3,
                "value": 0.0
              },
              "mcc": null
            },
            "transform:html_comment": {
              "counts": {
                "tp": 0,
                "fp": 0,
                "fn": 0,
                "tn": 8,
                "decisions": 8
              },
              "precision": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "recall": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "f1": {
                "numerator": 0,
                "denominator": 0,
                "value": null
              },
              "mcc": null
            },
            "transform:irrelevant_attribute": {
              "counts": {
                "tp": 0,
                "fp": 0,
                "fn": 0,
                "tn": 8,
                "decisions": 8
              },
              "precision": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "recall": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "f1": {
                "numerator": 0,
                "denominator": 0,
                "value": null
              },
              "mcc": null
            },
            "transform:negated_copy": {
              "counts": {
                "tp": 0,
                "fp": 0,
                "fn": 0,
                "tn": 8,
                "decisions": 8
              },
              "precision": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "recall": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "f1": {
                "numerator": 0,
                "denominator": 0,
                "value": null
              },
              "mcc": null
            },
            "transform:non_rendered_template": {
              "counts": {
                "tp": 0,
                "fp": 0,
                "fn": 0,
                "tn": 8,
                "decisions": 8
              },
              "precision": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "recall": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "f1": {
                "numerator": 0,
                "denominator": 0,
                "value": null
              },
              "mcc": null
            },
            "transform:synthetic_marker:language_attribute": {
              "counts": {
                "tp": 0,
                "fp": 0,
                "fn": 2,
                "tn": 0,
                "decisions": 2
              },
              "precision": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "recall": {
                "numerator": 0,
                "denominator": 2,
                "value": 0.0,
                "wilson95": {
                  "low": 0.0,
                  "high": 0.6576197724933469
                }
              },
              "f1": {
                "numerator": 0,
                "denominator": 2,
                "value": 0.0
              },
              "mcc": null
            },
            "transform:synthetic_marker:nested_template": {
              "counts": {
                "tp": 0,
                "fp": 0,
                "fn": 3,
                "tn": 0,
                "decisions": 3
              },
              "precision": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "recall": {
                "numerator": 0,
                "denominator": 3,
                "value": 0.0,
                "wilson95": {
                  "low": 5.551115123125783e-17,
                  "high": 0.5614970317550454
                }
              },
              "f1": {
                "numerator": 0,
                "denominator": 3,
                "value": 0.0
              },
              "mcc": null
            },
            "transform:synthetic_marker:rendered_body": {
              "counts": {
                "tp": 0,
                "fp": 0,
                "fn": 3,
                "tn": 0,
                "decisions": 3
              },
              "precision": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "recall": {
                "numerator": 0,
                "denominator": 3,
                "value": 0.0,
                "wilson95": {
                  "low": 5.551115123125783e-17,
                  "high": 0.5614970317550454
                }
              },
              "f1": {
                "numerator": 0,
                "denominator": 3,
                "value": 0.0
              },
              "mcc": null
            }
          },
          "synthetic_metric_eligible": true,
          "headline_eligible": false,
          "headline_blockers": [
            "synthetic transformations are correlated families",
            "real-repository labelled accuracy unavailable",
            "comparative, determinism, network, public-claim and demand gates are evaluated outside this score file"
          ]
        }
      }
    },
    {
      "result_path": "/tmp/regula-commercial-20260731.Inq4k2/synthetic-local-2/results.json",
      "tool": "local_head",
      "result_sha256": "54110a8672f39c58eb4762646091669c0bd15194d082b9840c0f53ed856d4add",
      "enumeration_complete": true,
      "missing_ids": [],
      "extra_ids": [],
      "duplicate_ids": [],
      "failed_ids": [],
      "candidates": {
        "A": {
          "complete": true,
          "applicable_decisions": 80,
          "valid_decisions": 80,
          "failed_decision_ids": [],
          "metrics": {
            "counts": {
              "tp": 0,
              "fp": 0,
              "fn": 40,
              "tn": 40,
              "decisions": 80
            },
            "precision": {
              "numerator": 0,
              "denominator": 0,
              "value": null,
              "wilson95": {
                "low": null,
                "high": null
              }
            },
            "recall": {
              "numerator": 0,
              "denominator": 40,
              "value": 0.0,
              "wilson95": {
                "low": 0.0,
                "high": 0.08762160119728664
              }
            },
            "f1": {
              "numerator": 0,
              "denominator": 40,
              "value": 0.0
            },
            "mcc": null
          },
          "strata": {
            "language:python": {
              "counts": {
                "tp": 0,
                "fp": 0,
                "fn": 40,
                "tn": 40,
                "decisions": 80
              },
              "precision": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "recall": {
                "numerator": 0,
                "denominator": 40,
                "value": 0.0,
                "wilson95": {
                  "low": 0.0,
                  "high": 0.08762160119728664
                }
              },
              "f1": {
                "numerator": 0,
                "denominator": 40,
                "value": 0.0
              },
              "mcc": null
            },
            "transform:alias_import": {
              "counts": {
                "tp": 0,
                "fp": 0,
                "fn": 13,
                "tn": 0,
                "decisions": 13
              },
              "precision": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "recall": {
                "numerator": 0,
                "denominator": 13,
                "value": 0.0,
                "wilson95": {
                  "low": 0.0,
                  "high": 0.22809537235419838
                }
              },
              "f1": {
                "numerator": 0,
                "denominator": 13,
                "value": 0.0
              },
              "mcc": null
            },
            "transform:comment": {
              "counts": {
                "tp": 0,
                "fp": 0,
                "fn": 0,
                "tn": 8,
                "decisions": 8
              },
              "precision": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "recall": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "f1": {
                "numerator": 0,
                "denominator": 0,
                "value": null
              },
              "mcc": null
            },
            "transform:dead_comment": {
              "counts": {
                "tp": 0,
                "fp": 0,
                "fn": 0,
                "tn": 8,
                "decisions": 8
              },
              "precision": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "recall": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "f1": {
                "numerator": 0,
                "denominator": 0,
                "value": null
              },
              "mcc": null
            },
            "transform:direct_import": {
              "counts": {
                "tp": 0,
                "fp": 0,
                "fn": 14,
                "tn": 0,
                "decisions": 14
              },
              "precision": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "recall": {
                "numerator": 0,
                "denominator": 14,
                "value": 0.0,
                "wilson95": {
                  "low": 1.3877787807814457e-17,
                  "high": 0.2153108027376358
                }
              },
              "f1": {
                "numerator": 0,
                "denominator": 14,
                "value": 0.0
              },
              "mcc": null
            },
            "transform:documentation": {
              "counts": {
                "tp": 0,
                "fp": 0,
                "fn": 0,
                "tn": 8,
                "decisions": 8
              },
              "precision": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "recall": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "f1": {
                "numerator": 0,
                "denominator": 0,
                "value": null
              },
              "mcc": null
            },
            "transform:from_import": {
              "counts": {
                "tp": 0,
                "fp": 0,
                "fn": 13,
                "tn": 0,
                "decisions": 13
              },
              "precision": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "recall": {
                "numerator": 0,
                "denominator": 13,
                "value": 0.0,
                "wilson95": {
                  "low": 0.0,
                  "high": 0.22809537235419838
                }
              },
              "f1": {
                "numerator": 0,
                "denominator": 13,
                "value": 0.0
              },
              "mcc": null
            },
            "transform:near_name": {
              "counts": {
                "tp": 0,
                "fp": 0,
                "fn": 0,
                "tn": 8,
                "decisions": 8
              },
              "precision": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "recall": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "f1": {
                "numerator": 0,
                "denominator": 0,
                "value": null
              },
              "mcc": null
            },
            "transform:string_literal": {
              "counts": {
                "tp": 0,
                "fp": 0,
                "fn": 0,
                "tn": 8,
                "decisions": 8
              },
              "precision": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "recall": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "f1": {
                "numerator": 0,
                "denominator": 0,
                "value": null
              },
              "mcc": null
            }
          },
          "synthetic_metric_eligible": true,
          "headline_eligible": false,
          "headline_blockers": [
            "synthetic transformations are correlated families",
            "real-repository labelled accuracy unavailable",
            "comparative, determinism, network, public-claim and demand gates are evaluated outside this score file"
          ]
        },
        "B": {
          "complete": true,
          "applicable_decisions": 80,
          "valid_decisions": 80,
          "failed_decision_ids": [],
          "metrics": {
            "counts": {
              "tp": 0,
              "fp": 0,
              "fn": 40,
              "tn": 40,
              "decisions": 80
            },
            "precision": {
              "numerator": 0,
              "denominator": 0,
              "value": null,
              "wilson95": {
                "low": null,
                "high": null
              }
            },
            "recall": {
              "numerator": 0,
              "denominator": 40,
              "value": 0.0,
              "wilson95": {
                "low": 0.0,
                "high": 0.08762160119728664
              }
            },
            "f1": {
              "numerator": 0,
              "denominator": 40,
              "value": 0.0
            },
            "mcc": null
          },
          "strata": {
            "language:html": {
              "counts": {
                "tp": 0,
                "fp": 0,
                "fn": 40,
                "tn": 40,
                "decisions": 80
              },
              "precision": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "recall": {
                "numerator": 0,
                "denominator": 40,
                "value": 0.0,
                "wilson95": {
                  "low": 0.0,
                  "high": 0.08762160119728664
                }
              },
              "f1": {
                "numerator": 0,
                "denominator": 40,
                "value": 0.0
              },
              "mcc": null
            },
            "transform:biometric_notice:language_attribute": {
              "counts": {
                "tp": 0,
                "fp": 0,
                "fn": 2,
                "tn": 0,
                "decisions": 2
              },
              "precision": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "recall": {
                "numerator": 0,
                "denominator": 2,
                "value": 0.0,
                "wilson95": {
                  "low": 0.0,
                  "high": 0.6576197724933469
                }
              },
              "f1": {
                "numerator": 0,
                "denominator": 2,
                "value": 0.0
              },
              "mcc": null
            },
            "transform:biometric_notice:nested_template": {
              "counts": {
                "tp": 0,
                "fp": 0,
                "fn": 3,
                "tn": 0,
                "decisions": 3
              },
              "precision": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "recall": {
                "numerator": 0,
                "denominator": 3,
                "value": 0.0,
                "wilson95": {
                  "low": 5.551115123125783e-17,
                  "high": 0.5614970317550454
                }
              },
              "f1": {
                "numerator": 0,
                "denominator": 3,
                "value": 0.0
              },
              "mcc": null
            },
            "transform:biometric_notice:rendered_body": {
              "counts": {
                "tp": 0,
                "fp": 0,
                "fn": 3,
                "tn": 0,
                "decisions": 3
              },
              "precision": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "recall": {
                "numerator": 0,
                "denominator": 3,
                "value": 0.0,
                "wilson95": {
                  "low": 5.551115123125783e-17,
                  "high": 0.5614970317550454
                }
              },
              "f1": {
                "numerator": 0,
                "denominator": 3,
                "value": 0.0
              },
              "mcc": null
            },
            "transform:chatbot_notice:language_attribute": {
              "counts": {
                "tp": 0,
                "fp": 0,
                "fn": 3,
                "tn": 0,
                "decisions": 3
              },
              "precision": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "recall": {
                "numerator": 0,
                "denominator": 3,
                "value": 0.0,
                "wilson95": {
                  "low": 5.551115123125783e-17,
                  "high": 0.5614970317550454
                }
              },
              "f1": {
                "numerator": 0,
                "denominator": 3,
                "value": 0.0
              },
              "mcc": null
            },
            "transform:chatbot_notice:nested_template": {
              "counts": {
                "tp": 0,
                "fp": 0,
                "fn": 2,
                "tn": 0,
                "decisions": 2
              },
              "precision": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "recall": {
                "numerator": 0,
                "denominator": 2,
                "value": 0.0,
                "wilson95": {
                  "low": 0.0,
                  "high": 0.6576197724933469
                }
              },
              "f1": {
                "numerator": 0,
                "denominator": 2,
                "value": 0.0
              },
              "mcc": null
            },
            "transform:chatbot_notice:rendered_body": {
              "counts": {
                "tp": 0,
                "fp": 0,
                "fn": 3,
                "tn": 0,
                "decisions": 3
              },
              "precision": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "recall": {
                "numerator": 0,
                "denominator": 3,
                "value": 0.0,
                "wilson95": {
                  "low": 5.551115123125783e-17,
                  "high": 0.5614970317550454
                }
              },
              "f1": {
                "numerator": 0,
                "denominator": 3,
                "value": 0.0
              },
              "mcc": null
            },
            "transform:deepfake_notice:language_attribute": {
              "counts": {
                "tp": 0,
                "fp": 0,
                "fn": 3,
                "tn": 0,
                "decisions": 3
              },
              "precision": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "recall": {
                "numerator": 0,
                "denominator": 3,
                "value": 0.0,
                "wilson95": {
                  "low": 5.551115123125783e-17,
                  "high": 0.5614970317550454
                }
              },
              "f1": {
                "numerator": 0,
                "denominator": 3,
                "value": 0.0
              },
              "mcc": null
            },
            "transform:deepfake_notice:nested_template": {
              "counts": {
                "tp": 0,
                "fp": 0,
                "fn": 3,
                "tn": 0,
                "decisions": 3
              },
              "precision": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "recall": {
                "numerator": 0,
                "denominator": 3,
                "value": 0.0,
                "wilson95": {
                  "low": 5.551115123125783e-17,
                  "high": 0.5614970317550454
                }
              },
              "f1": {
                "numerator": 0,
                "denominator": 3,
                "value": 0.0
              },
              "mcc": null
            },
            "transform:deepfake_notice:rendered_body": {
              "counts": {
                "tp": 0,
                "fp": 0,
                "fn": 2,
                "tn": 0,
                "decisions": 2
              },
              "precision": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "recall": {
                "numerator": 0,
                "denominator": 2,
                "value": 0.0,
                "wilson95": {
                  "low": 0.0,
                  "high": 0.6576197724933469
                }
              },
              "f1": {
                "numerator": 0,
                "denominator": 2,
                "value": 0.0
              },
              "mcc": null
            },
            "transform:developer_note": {
              "counts": {
                "tp": 0,
                "fp": 0,
                "fn": 0,
                "tn": 8,
                "decisions": 8
              },
              "precision": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "recall": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "f1": {
                "numerator": 0,
                "denominator": 0,
                "value": null
              },
              "mcc": null
            },
            "transform:emotion_notice:language_attribute": {
              "counts": {
                "tp": 0,
                "fp": 0,
                "fn": 3,
                "tn": 0,
                "decisions": 3
              },
              "precision": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "recall": {
                "numerator": 0,
                "denominator": 3,
                "value": 0.0,
                "wilson95": {
                  "low": 5.551115123125783e-17,
                  "high": 0.5614970317550454
                }
              },
              "f1": {
                "numerator": 0,
                "denominator": 3,
                "value": 0.0
              },
              "mcc": null
            },
            "transform:emotion_notice:nested_template": {
              "counts": {
                "tp": 0,
                "fp": 0,
                "fn": 2,
                "tn": 0,
                "decisions": 2
              },
              "precision": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "recall": {
                "numerator": 0,
                "denominator": 2,
                "value": 0.0,
                "wilson95": {
                  "low": 0.0,
                  "high": 0.6576197724933469
                }
              },
              "f1": {
                "numerator": 0,
                "denominator": 2,
                "value": 0.0
              },
              "mcc": null
            },
            "transform:emotion_notice:rendered_body": {
              "counts": {
                "tp": 0,
                "fp": 0,
                "fn": 3,
                "tn": 0,
                "decisions": 3
              },
              "precision": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "recall": {
                "numerator": 0,
                "denominator": 3,
                "value": 0.0,
                "wilson95": {
                  "low": 5.551115123125783e-17,
                  "high": 0.5614970317550454
                }
              },
              "f1": {
                "numerator": 0,
                "denominator": 3,
                "value": 0.0
              },
              "mcc": null
            },
            "transform:html_comment": {
              "counts": {
                "tp": 0,
                "fp": 0,
                "fn": 0,
                "tn": 8,
                "decisions": 8
              },
              "precision": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "recall": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "f1": {
                "numerator": 0,
                "denominator": 0,
                "value": null
              },
              "mcc": null
            },
            "transform:irrelevant_attribute": {
              "counts": {
                "tp": 0,
                "fp": 0,
                "fn": 0,
                "tn": 8,
                "decisions": 8
              },
              "precision": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "recall": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "f1": {
                "numerator": 0,
                "denominator": 0,
                "value": null
              },
              "mcc": null
            },
            "transform:negated_copy": {
              "counts": {
                "tp": 0,
                "fp": 0,
                "fn": 0,
                "tn": 8,
                "decisions": 8
              },
              "precision": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "recall": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "f1": {
                "numerator": 0,
                "denominator": 0,
                "value": null
              },
              "mcc": null
            },
            "transform:non_rendered_template": {
              "counts": {
                "tp": 0,
                "fp": 0,
                "fn": 0,
                "tn": 8,
                "decisions": 8
              },
              "precision": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "recall": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "f1": {
                "numerator": 0,
                "denominator": 0,
                "value": null
              },
              "mcc": null
            },
            "transform:synthetic_marker:language_attribute": {
              "counts": {
                "tp": 0,
                "fp": 0,
                "fn": 2,
                "tn": 0,
                "decisions": 2
              },
              "precision": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "recall": {
                "numerator": 0,
                "denominator": 2,
                "value": 0.0,
                "wilson95": {
                  "low": 0.0,
                  "high": 0.6576197724933469
                }
              },
              "f1": {
                "numerator": 0,
                "denominator": 2,
                "value": 0.0
              },
              "mcc": null
            },
            "transform:synthetic_marker:nested_template": {
              "counts": {
                "tp": 0,
                "fp": 0,
                "fn": 3,
                "tn": 0,
                "decisions": 3
              },
              "precision": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "recall": {
                "numerator": 0,
                "denominator": 3,
                "value": 0.0,
                "wilson95": {
                  "low": 5.551115123125783e-17,
                  "high": 0.5614970317550454
                }
              },
              "f1": {
                "numerator": 0,
                "denominator": 3,
                "value": 0.0
              },
              "mcc": null
            },
            "transform:synthetic_marker:rendered_body": {
              "counts": {
                "tp": 0,
                "fp": 0,
                "fn": 3,
                "tn": 0,
                "decisions": 3
              },
              "precision": {
                "numerator": 0,
                "denominator": 0,
                "value": null,
                "wilson95": {
                  "low": null,
                  "high": null
                }
              },
              "recall": {
                "numerator": 0,
                "denominator": 3,
                "value": 0.0,
                "wilson95": {
                  "low": 5.551115123125783e-17,
                  "high": 0.5614970317550454
                }
              },
              "f1": {
                "numerator": 0,
                "denominator": 3,
                "value": 0.0
              },
              "mcc": null
            }
          },
          "synthetic_metric_eligible": true,
          "headline_eligible": false,
          "headline_blockers": [
            "synthetic transformations are correlated families",
            "real-repository labelled accuracy unavailable",
            "comparative, determinism, network, public-claim and demand gates are evaluated outside this score file"
          ]
        }
      }
    }
  ]
}
[exit 0]
```

Ended: `2026-08-05T00:17:17+01:00`

## Core product and trust documents

Started: `2026-08-05T00:17:17+01:00`

Command:

```console
$ bash -lc 'cat README.md; printf '"'"'\n===== SECURITY =====\n'"'"'; cat SECURITY.md; printf '"'"'\n===== TRUST =====\n'"'"'; cat docs/TRUST.md; printf '"'"'\n===== MODEL CARD =====\n'"'"'; cat docs/MODEL_CARD.md; printf '"'"'\n===== ARCHITECTURE =====\n'"'"'; cat docs/architecture.md; printf '"'"'\n===== VERSIONING =====\n'"'"'; cat docs/VERSIONING.md'
<!-- mcp-name: io.github.kuzivaai/regula -->
# Regula

**Find AI governance risks that may be visible in source code. Covers the EU AI Act, South Korea AI Basic Act, and Colorado SB 26-189, with questionnaires for context that code cannot show.**

[![PyPI](https://img.shields.io/pypi/v/regula-ai)](https://pypi.org/project/regula-ai/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE.txt)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![CI](https://github.com/kuzivaai/getregula/actions/workflows/ci.yaml/badge.svg)](https://github.com/kuzivaai/getregula/actions)
[![Tests](https://img.shields.io/badge/tests-2683%20collected-blue.svg)](#verified-numbers)
[![Accessibility target: WCAG 2.2 AA](https://img.shields.io/badge/accessibility%20target-WCAG%202.2%20AA-blue.svg)](docs/accessibility/README.md)

---

## Table of contents

- [What it does](#what-it-does)
- [Choose how to start](#choose-how-to-start)
- [Quick start](#quick-start)
- [What Regula tells you](#what-regula-tells-you)
- [Key commands](#key-commands)
- [Who is this for?](#who-is-this-for)
- [What Regula is (and isn't)](#what-regula-is-and-isnt)
- [Bias evaluation: methodology and ethics](#bias-evaluation-methodology-and-ethics)
- [Important limitations](#important-limitations)
- [Verified numbers](#verified-numbers)
- [Contributing](#contributing)
- [Licence](#licence)

---

![Regula check demo](site/assets/demo/regula-check.svg)

---

## What it does

Regula scans a local source-code folder for patterns that may need AI governance review. A questionnaire records facts that code cannot show, such as where and how a system will be used. Results identify candidate risk categories and link to provisions that may be relevant. Regula does not determine legal classification, compliance, or the obligations that apply to a real deployment.

Reference material covers the EU AI Act, South Korea's AI Basic Act (Act No. 20676), and Colorado SB 26-189. The core install has no required third-party runtime dependencies. Optional extras add dependencies, and some optional commands or configured features can contact external services. Assess territorial scope and data-processing duties independently.

In plain English: give Regula a source-code folder and answer questions about how the system will be used. It returns possible issues and a review trail so a developer, governance lead, or adviser can decide what to investigate next. A scan with no findings does not prove that a system is compliant or low risk.

## Choose how to start

| If you want to… | Start here |
|---|---|
| Explore the questions without installing anything | Use the [browser assessment](https://getregula.com/assess/). It records declared context for review; it does not inspect your code or make a legal determination. |
| Check a local codebase | Follow the [Quick start](#quick-start), then run `regula check .`. |
| Evaluate Regula before adopting it | Follow the [10-minute example journey](examples/cv-screening-app/) and read the [documented limitations and verification evidence](docs/TRUST.md). |
| Add a repeatable team check | Use the [CI/CD example](#cicd) and review the exit-code policy before making it blocking. |
| Prepare material for a human reviewer | Generate a reviewer-completable evidence scaffold, then complete and validate its contextual fields. |

## Quick start

```bash
pipx install regula-ai      # or: pip install regula-ai / uv pip install regula-ai
```

**Not sure if the AI Act applies?** No code needed:
```bash
regula assess               # record declared context for human review
```

**Want to scan your code?**
```bash
regula check .              # 419 tier patterns, 8 language families; runtime varies
regula check . --jurisdictions eu,korea,colorado  # all 3 jurisdictions
```

**Need a review pack?**
```bash
regula evidence-pack --project .   # reviewer-completable evidence scaffold
regula conform --sign --timestamp  # integrity metadata (requires regula[signing])
```

Generated files are inputs to human review, not an audit opinion, certification, or proof of compliance.

**Just want to see it work?** (requires the cloned repo :  `examples/` is not bundled in the pip package)
```bash
git clone https://github.com/kuzivaai/getregula && cd getregula
regula demo                 # scan a bundled example project
```

### Install details

The recommended install is **pipx** :  it isolates Regula from your system Python and avoids the `externally-managed-environment` error on Ubuntu 22.04+, Debian 12+, Fedora, Arch, and Homebrew Python.

If you don't have pipx yet, install it first (one-time):

| Platform | Install pipx |
|---|---|
| macOS | `brew install pipx && pipx ensurepath` |
| Debian / Ubuntu | `sudo apt install pipx && pipx ensurepath` |
| Fedora | `sudo dnf install pipx && pipx ensurepath` |
| Arch | `sudo pacman -S python-pipx && pipx ensurepath` |
| Windows | `python -m pip install --user pipx && python -m pipx ensurepath` |

**Already using uv?** `uvx --from regula-ai regula` runs it with no install step (the `--from` flag is required because the PyPI package name `regula-ai` differs from the CLI name `regula`). Or install it permanently with `uv tool install regula-ai`.

**Running inside a venv or conda env?** `pip install regula-ai` works fine there :  the PEP 668 restriction only applies to system Python.

See [`docs/installation.md`](docs/installation.md) for troubleshooting (`externally-managed-environment`, `command not found: regula` after install, PATH setup per shell).

### Try it against a known high-risk fixture:

```bash
regula check examples/cv-screening-app --scope all
```

The `--scope all` flag is needed because Regula's default scope (`production`) skips example directories. This fixture intentionally triggers an Annex III Category 4 (Employment) high-risk classification.

See [`examples/`](examples/) for runnable reference projects covering each EU AI Act risk tier, or walk through the full 10-minute evaluation journey in [`examples/cv-screening-app/`](examples/cv-screening-app/) :  install, scan, plan, gap, conform, verify, handoff to red-team tooling.

For a deeper first-time-user walk-through (policy tuning, CI integration, baselining) see [`docs/QUICKSTART.md`](docs/QUICKSTART.md). The full documentation is indexed by type (tutorials / how-to / reference / explanation) in [`docs/README.md`](docs/README.md).

### CI/CD

```yaml
# .github/workflows/regula.yaml
name: AI Governance Check
on: [push, pull_request]
jobs:
  regula:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: kuzivaai/getregula@v1
        with:
          path: '.'
          upload-sarif: 'true'
          fail-on-prohibited: 'true'
```

## What Regula tells you

The EU AI Act defines four risk tiers. Regula maps code patterns to each:

| Tier | Action | What it means |
|------|--------|---------------|
| **Potentially prohibited** (Article 5) | Block indicator | Reports code patterns associated with listed practices for urgent contextual review. |
| **Potentially high-risk** (Article 6 and Annex III) | Warn + review map | Reports candidate use categories and maps provisions that may be relevant if a reviewer confirms the legal classification. |
| **Potential transparency duty** (Article 50) | Transparency indicator | Reports chatbot, synthetic-content and related implementation signals; the applicable paragraph and exceptions require review. |
| **No elevated code indicator** | Log only | Means the scanner did not observe a configured elevated indicator. It does not establish minimal-risk status or absence of legal duties. |

Every finding includes the relevant Article reference and explains when exceptions may apply. Regula flags patterns -- it does not make legal determinations.

**Multi-jurisdiction support.** Beyond the EU AI Act, Regula maps risk patterns to South Korea's AI Basic Act (Act No. 20676, in force 22 January 2026) and Colorado SB 26-189 (disclosure-focused, plus consumer correction and human-review rights, duties from 1 January 2027). Use `--jurisdictions eu,korea,colorado` on `regula check` or `--jurisdiction korea` on `regula assess` to apply the relevant framework. Each jurisdiction has its own YAML config (`references/jurisdictions/`) and tailored web questionnaire.

**Developer guides** on getregula.com:
[Python](https://getregula.com/guides/eu-ai-act-python.html) |
[JavaScript](https://getregula.com/guides/eu-ai-act-javascript.html) |
[Healthcare](https://getregula.com/guides/eu-ai-act-healthcare.html) |
[Recruitment](https://getregula.com/guides/eu-ai-act-recruitment-hiring.html) |
[Article 5](https://getregula.com/guides/article-5-prohibited-practices.html) |
[Article 9](https://getregula.com/guides/article-9-risk-management.html) |
[Article 14](https://getregula.com/guides/article-14-human-oversight.html) |
[Article 50](https://getregula.com/guides/article-50-transparency.html)

## Key commands

| Command | What it does |
|---------|-------------|
| `regula` | Scan the current directory, show an indicator summary and next steps |
| `regula check .` | Detailed risk scan with per-file findings |
| `regula comply` | EU AI Act obligation checklist with completion status |
| `regula gap --project .` | Compliance gap assessment against Articles 9-15 |
| `regula plan --project .` | Prioritised remediation plan based on gap results |
| `regula fix --project .` | Generate compliance fix scaffolds for findings |
| `regula evidence-pack --project .` | Reviewer-completable evidence scaffold with integrity metadata |
| `regula conform --project .` | Article 43 conformity assessment evidence pack |
| `regula dpv --project .` | Export the risk indication as DPV-AIAct JSON-LD (aligned to the DPVCG EU-AIAct vocabulary) for RDF/GRC tooling |
| `regula check --ci .` | CI mode -- exit code 1 on any WARN or BLOCK finding, SARIF output |
| `regula assess` | Structured declared-context questionnaire for applicability and risk review |
| `regula demo` | Scan a bundled example project -- zero-commitment trial |
| `regula api-server` | Start the REST API (localhost:8487) with web dashboard |
| `regula conform --organisational` | Governance self-assessment for Articles 9/17/27/72 |
| `regula questionnaire` | Context-driven risk assessment questionnaire (also via REST API) |
| `regula exempt` | Article 6(3) high-risk exemption decision tree |
| `regula oversight .` | Article 14 human oversight analysis (cross-file flow tracing) |
| `regula guardrails .` | Article 15 guardrail implementation coverage detection |
| `regula owasp-agentic` | OWASP Top 10 for Agentic Applications assessment |
| `regula monitor` | Runtime monitoring for AI applications (Article 12) |
| `regula gdpr` | GDPR cross-reference scan ([14 focused checks](scripts/gdpr_scan.py), 4 AI Act/GDPR hotspots) |
| `regula bias` | CrowS-Pairs bias evaluation (1,508 sentence pairs) with optional BBQ benchmark. Aligned with Digital Omnibus bias-testing safeguards (Article 4a, COM(2025)836). |
| `regula mcp-server` | MCP server (JSON-RPC stdio) exposing three tools :  `regula_check`, `regula_classify`, `regula_gap` :  for Claude Code, Cursor, and other MCP clients |
| `regula install <platform>` | Set up pre-commit hooks, git hooks, or Claude Code/Copilot/Windsurf integration |

Regula has 62 commands in total. Run `regula --help-all` for the full list, or see [`docs/cli-reference.md`](docs/cli-reference.md).

### REST API and web dashboard

For GRC integration or non-terminal users:

```bash
python3 scripts/api_server.py --port 8487
# Open http://localhost:8487/v1/dashboard
```

Seven endpoints: `/health`, `/v1/check`, `/v1/classify`, `/v1/gap`, `/v1/questionnaire`, `/v1/questionnaire/evaluate`, `/v1/dashboard`. All return the same JSON envelope as the CLI. No auth -- run behind a reverse proxy for remote access.

## Who is this for?

- **Solo founders and indie hackers** building AI products who need an initial list of code patterns to investigate before contextual and legal review.
- **Small teams** who want to understand their compliance exposure before it becomes a sales blocker. Enterprise procurement is already asking for AI Act evidence.
- **Engineering teams** who want EU AI Act scanning in CI/CD to catch high-risk or prohibited patterns before they ship.
- **AI governance consultants and advisors** :  run Regula on a client's codebase to produce code-observation reports, gap-review scaffolds, and hash-manifested documentation for completion and review within a broader governance engagement. Selected generated facts have repository checks; limitations and reproduction commands are recorded in the trust pack. Deliverables can carry engagement metadata (client, preparer, reference) via the `engagement:` policy section or `--client`/`--prepared-by`/`--engagement-ref` flags. See the [consultant guide](docs/consultant-guide.md) for the workflow and its boundaries.

## What Regula is (and isn't)

**Regula is:**

- A development-time compliance tool that combines static code analysis with governance questionnaires, mapping both to obligations across 3 jurisdictions (EU AI Act, South Korea AI Basic Act, Colorado SB 26-189)
- A shift-left code-indicator scanner -- like ESLint for governance review, running in your terminal or CI/CD pipeline
- A questionnaire-based assessment tool for organisational obligations that code patterns cannot verify (Articles 9, 17, 27, 72)
- Pattern-based risk indication across 3 jurisdictions, not a legal compliance certificate
- A starting point for compliance awareness, not a finish line

**Regula is not:**

- A runtime monitoring system (it analyses source code, not running systems)
- A legal compliance certificate (findings are indicators, not legal determinations)
- A replacement for enterprise GRC platforms like Credo AI or Holistic AI (it complements them)
- A production fairness testing platform (`regula bias` runs benchmark probes against a local model as a starting point, but does not replace runtime fairness monitoring)
- Legal advice (consult qualified legal counsel for compliance decisions)

Regula helps development teams understand their EU AI Act exposure early. It does not replace the organisational, procedural, and legal work required for full compliance. For a detailed account of what falls outside Regula's scope, see [`docs/what-regula-does-not-do.md`](docs/what-regula-does-not-do.md), and for Regula's own model card (intended use, training data, evaluation, known failure modes) see [`docs/MODEL_CARD.md`](docs/MODEL_CARD.md).

## Bias evaluation: methodology and ethics

`regula bias` runs two social-bias benchmarks against a locally-hosted
language model (Ollama, `llama3.2`/`mistral`/`qwen` variants supported)
as evidence for EU AI Act Article 10 data-governance documentation.

| Benchmark | Paper | Method | What it measures |
|---|---|---|---|
| CrowS-Pairs | Nangia et al., 2020 | Log-probability difference between stereotypical and anti-stereotypical sentence pairs | Intrinsic bias in masked/causal LM output |
| BBQ | Parrish et al., 2022 | Question-answering on ambiguous-context prompts | Bias surfacing in downstream QA behaviour |

Both include Wilson confidence intervals for small-sample reliability and
bootstrap CIs for distribution estimates. Full methodology lives in
[`scripts/bias_eval.py`](scripts/bias_eval.py) and
[`docs/benchmarks/PRECISION_RECALL_2026_04.md`](docs/benchmarks/PRECISION_RECALL_2026_04.md).

**Ethics statement.** CrowS-Pairs and BBQ stereotype pairs are used
**solely for scientific evaluation** of model behaviour under controlled
conditions. Regula does **not display individual stereotype pairs** in
terminal output or reports :  only aggregated scores, confidence
intervals, and benchmark-level verdicts. The pairs are distributed under
the dataset's own licence (CC BY-SA 4.0 for CrowS-Pairs) and are not
redistributed or modified by Regula. Opinions encoded in the stereotype
pairs do not reflect the views of the maintainer, Regula contributors,
or any user running the tool; their presence is instrumental, not
endorsing. `regula bias` is a development-time starting point for bias
documentation, not a production fairness monitor :  see "What Regula is
(and isn't)" above.

## Important limitations

Regula performs **pattern-based risk indication**, not legal risk classification.

- The EU AI Act classifies risk based on intended purpose and deployment context (Article 6), not code patterns. Regula's findings are indicators that warrant human review.
- **False positives will occur.** Blind-labelled benchmark on 50 randomly selected Python AI repos measured **83.5% precision on production code** (N=115, measured on v1.7.0, labelled by a single reviewer with no inter-rater agreement measurement). Per-tier: `ai_security` (85%), `agent_autonomy` (83%), `limited_risk` (88%), `minimal_risk` (100%). The `high_risk` tier (33%, N=6) is statistically unmeasurable at this sample size. Full methodology, corpus selection, and reproduction steps: [`benchmarks/README.md`](benchmarks/README.md).
- **TypeScript findings are advisory:** 0% precision on the current benchmark (6 FP, 0 TP). Language-specific AST gating is not yet implemented for TypeScript.
- **False negatives will occur.** Novel risk patterns not in the database will be missed.
- Article 5 prohibitions have conditions and exceptions that require human judgment.
- The audit trail is self-attesting (locally verifiable, not externally witnessed).
- This is not a substitute for legal advice or DPO review.

## Verified numbers

| What | Count |
|------|------:|
| CLI commands | 62 |
| Risk detection patterns (regexes) | 419 |
| Language families scanned | 8 (Python, JS, TS, Java, Go, Rust, C/C++, Jupyter) |
| Compliance frameworks mapped | 13 |
| Tests (pytest --collect-only, all passing) | 2,690 |
| Required production dependencies | 0 |

For reproduction commands, version-bounded benchmarks, known exceptions, security posture, and audit-trail design, see [`docs/TRUST.md`](docs/TRUST.md). What version numbers promise, the public API they cover, and the deprecation policy: [`docs/VERSIONING.md`](docs/VERSIONING.md).

## Privacy and data handling

Regula runs entirely on your machine. No code, findings, or metadata are transmitted to any external service. There is no account system, no API key, no telemetry by default (crash reporting requires both `regula telemetry enable` **and** an endpoint you configure yourself via `REGULA_SENTRY_DSN`; published builds ship none, and `DO_NOT_TRACK` suppresses it regardless). The tool reads your source files, analyses them locally, and writes output to your local filesystem. Network access is only used when you explicitly request it (RFC 3161 timestamps via `--timestamp`). See [`SECURITY.md`](SECURITY.md) for the full security posture.

## Contributing

Bug reports and pull requests are welcome.

- Run `pytest tests/ -q` before opening a PR.
- Pattern additions go in `scripts/risk_patterns.py`. Each pattern should have a corresponding test.
- Regula is intentionally risk *indication*, not legal classification. New patterns should be conservative -- false positives erode trust more than false negatives for a developer tool.
- See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the full contributor guide and [`CHANGELOG.md`](CHANGELOG.md) for version history.

### Authorship

Regula is maintained by Kuziva Muzondo. Where commits identify a co-author, that attribution records the tools or collaborators involved. The maintainer remains accountable for reviewing and accepting every merged change.

## Licence

**Engine and CLI:** [Apache License 2.0](LICENSE.txt) **OR** [European Union Public Licence v. 1.2](LICENSE.EUPL) :  at your option. Pick the one that fits your context:

- **Apache 2.0** includes an explicit patent grant, making it the preferred choice for enterprise adoption, commercial redistribution, and any context where patent clarity matters.
- **EUPL-1.2** is explicitly recognised inside EU institutions and public-sector procurement, is strongly-copyleft on software, and has a formal compatibility appendix (GPL v2/v3, AGPL v3, OSL, EPL, CeCILL, MPL 2.0, LGPL, CC BY-SA 3.0) for downstream projects. If you work with a European public administration, EUPL is often the required or preferred licence.

You may choose either licence for any use. You do not need to state which one you picked, but attribution (keep the copyright notice and NOTICE file) is required under both.

**Risk patterns and regulatory data:** [Detection Rule License (DRL) 1.1](docs/LICENSE.Detection.Rules.md). You may use, modify, and redistribute the patterns freely. Attribution is required if you redistribute the patterns or use them in a product. If your tool generates match output from these patterns, the output must credit the source.

The SPDX expression for the full package is `(Apache-2.0 OR EUPL-1.2) AND LicenseRef-DRL-1.1`.

===== SECURITY =====
# Security Policy

> Regula is an open-source CLI tool that combines code scanning with
> governance questionnaires, running entirely on the user's local
> machine. It has zero runtime dependencies and makes no network calls
> in its core operations. The attack surface is therefore narrow, but it
> is not nil — see this document for the full posture and how to
> report issues.

## Supported versions

| Version | Supported |
|---|---|
| 1.9.x | ✅ Receives security fixes |
| 1.7.x | ⚠️ Critical security fixes only; upgrade — 1.9.0 is a drop-in replacement (see `docs/VERSIONING.md`: the jump is a version realignment, not a breaking change) |
| < 1.7 | ❌ Unsupported — please upgrade |

The latest release is on PyPI at <https://pypi.org/project/regula-ai/>.

## Reporting a vulnerability

**Please report vulnerabilities privately, not via public GitHub issues.**

Two channels:

1. **GitHub Security Advisory (preferred)** —
   <https://github.com/kuzivaai/getregula/security/advisories/new>
2. **Email** — `support@getregula.com` with the subject line
   `[SECURITY] <short description>`

Include in your report:

- A clear description of the issue
- Steps to reproduce (a minimal repro is ideal)
- The Regula version and Python version you tested against
- Your suggested severity (critical / high / medium / low)
- Whether you intend to publish your own write-up after disclosure

## What to expect

| Stage | Target |
|---|---|
| Acknowledgement | within 72 hours |
| Initial triage and severity confirmation | within 7 days |
| Fix or mitigation in `main` | within 30 days for high/critical |
| Coordinated disclosure | within 90 days from initial report |

If a fix takes longer, you will be told why and given an updated
estimate. The maintainer will not silently ignore a reported issue.

We follow a 90-day coordinated disclosure timeline by default — if you
need a different timeline (regulatory deadlines, embargoed industry
disclosure, etc.), include that in your initial report.

## What is in scope

- The `regula` CLI commands and the `scripts/` package
- The `hooks/` package (pre/post tool-use, stop hooks)
- The `references/` data files when consumed by the scanner
- The benchmark runner (`benchmarks/label.py`, `benchmarks/synthetic/run.py`)
- The MCP server (`scripts/mcp_server.py`)

## What is out of scope

- Issues in third-party tools that integrate with Regula (Claude Code,
  Cursor, Windsurf, IDE plugins) — please report those upstream
- Issues in optional dependencies (`pyyaml`, `tree-sitter`,
  `weasyprint`, `sentry-sdk`) — please report those to the upstream
  package maintainers
- The landing page (`index.html`, `uae.html`, `de.html`,
  `pt-br.html`) is hosted statically and has no server-side code; web
  vulnerabilities there are out of scope
- Attacks that require an attacker to already control the user's
  shell, filesystem, or Python interpreter — Regula cannot defend
  against a compromised host

## Current security posture

| Check | Last verified | Status |
|---|---|---|
| `bandit -c pyproject.toml -r scripts/ hooks/` | Each release | 0 low / 0 medium / 0 high |
| `semgrep --config p/security-audit --config p/python` | Each release | 0 findings on 200 rules / 129 files |
| `pip-audit` | Each release | 0 vulnerabilities (zero runtime deps) |
| `regula self-test` | Each commit | 6 / 6 |
| Custom regression suite | Each commit | 2,690 pytest-collected tests |
| PyPI provenance attestation (PEP 740, Trusted Publishing) | Each release | ✅ attached to wheel + sdist, Sigstore-backed |
| CodeQL static analysis | Each push | workflow green; open alerts triaged below, never suppressed |
Source: reproducible commands and evidence are documented in [`docs/TRUST.md`](docs/TRUST.md); live workflow state is available in [GitHub Actions](https://github.com/kuzivaai/getregula/actions).

The full posture is in [`docs/TRUST.md`](docs/TRUST.md), Section 7.

## Known unhardened areas

Honest list, also recorded in `docs/TRUST.md`:

- **No SOC 2 Type II.** Regula is a local CLI, not a hosted service —
  there is no infrastructure to audit. The equivalent is the open-source
  code itself.
- **No third-party penetration test.** The attack surface is the user's
  local machine + opt-in network calls. Open for review at
  <https://github.com/kuzivaai/getregula>.
- **No formal CVE program (yet).** The next public CVE we receive will
  also be the moment we register as a CNA. Until then, GitHub Security
  Advisory + email.

## CodeQL static-analysis alerts (open, triaged, not suppressed)

CodeQL runs on every push. The dated snapshot recorded **42 open high-severity
alerts**; use the [live code-scanning list](https://github.com/kuzivaai/getregula/security/code-scanning) for current state.
They are listed here in full, with the reasoning for each, and left open in the
GitHub Security tab. We do not dismiss or suppress security alerts:
a compliance tool that clears its own dashboard by waving alerts away is not one
you should trust. The CodeQL *workflow* passes; these alerts do not gate it.

**37 × `py/path-injection` (across 8 files).** A code scanner's job is to read
files from a folder the user points it at, so its file-reading paths are tainted
by design. Every scanning command routes through `walk_project_files()` /
`is_safe_to_scan()`, which reject named pipes, out-of-root symlinks and `.git`;
the optional REST API (`api_server.py`) additionally rejects any path outside the
current working directory (`Path.resolve().relative_to(cwd)`) and caps request
bodies at 1 MB. CodeQL does not model these containment checks as sanitisers, so
the taint path is reported even though the guard is present. `tests/test_hostile_sweep.py`
exercises this whole class against a deliberately hostile directory tree.

**5 × other rules, each reviewed individually:**

| Alert | Location | Assessment |
|---|---|---|
| `py/polynomial-redos` | `classify_risk.py` | Reachable only via *user-supplied* custom-rule patterns, which already pass `_compile_custom_pattern` (rejects nested quantifiers and patterns over 500 chars; unit-tested). Polynomial, not exponential; self-inflicted. Low risk, mitigated. |
| `py/bad-tag-filter` | `claim_auditor.py` | A genuine minor robustness gap in an internal docs-audit tool — **fixed**: the `<script>` / `<style>` blanking regex now tolerates whitespace and attributes in the closing tag. |
| `py/clear-text-logging-sensitive-data` | `tests/helpers.py` | Test helper that prints an assertion failure; the "secret" is a synthetic, char-code-constructed test credential. Test-only false positive. |
| `py/redos` | `tests/test_classification.py` | A regex inside the test that *asserts* ReDoS protection works. Test-only. |
| `py/incomplete-url-substring-sanitization` | `tests/test_build_regulations.py` | A test asserting rendered HTML contains a URL substring, not a security check. Test-only false positive. |

If you are evaluating Regula: its own scanner is held to the same standard it
applies to your code. Every alert is visible, triaged in public, and either
explained or fixed — never silenced.

## How to verify a release independently

```bash
# Verify the wheel matches the published commit
git clone https://github.com/kuzivaai/getregula.git
cd getregula
git checkout v1.7.3
python3 -m build
sha256sum dist/regula_ai-1.7.3-py3-none-any.whl

# Compare against the wheel served by PyPI
pip download --no-deps -d /tmp/verify regula-ai==1.7.3
sha256sum /tmp/verify/regula_ai-1.7.3-py3-none-any.whl

# Verify PyPI provenance attestations (PEP 740, Sigstore-backed)
python3 -m pip install pypi-attestation-models
python3 -m pypi_attestations verify /tmp/verify/regula_ai-1.7.3-py3-none-any.whl
```

The two SHA-256 hashes should match. If they do not, **stop and report
to `support@getregula.com` immediately** — that would indicate either a
PyPI compromise or a non-reproducible build, both of which we want to
investigate.

## Acknowledgements

Researchers who have responsibly disclosed issues will be credited
here, with their consent. The list is currently empty — be the first.

===== TRUST =====
# Trust Pack — Regula

> The 2026 B2B buyer's playbook is "Evidence Pack first, pitch deck never."
> This document is Regula's Trust Pack: a single source of truth for the
> questions a sceptical buyer, auditor, or compliance officer asks before
> they will consider running it on their codebase.
>
> Every claim below is paired with the **exact shell command** anyone can
> run to verify it independently. If a claim is not verifiable, it is not
> in this document.

---

## Contents

1. [Who built it and what is it](#1-who-built-it-and-what-is-it)
2. [What Regula does (and does not) claim](#2-what-regula-does-and-does-not-claim)
3. [Reproducibility — verify every published number](#3-reproducibility)
4. [Tamper-evidence — verify the audit trail](#4-tamper-evidence)
5. [Transparency — verify every finding](#5-transparency)
6. [Independent verification — read the source](#6-independent-verification)
7. [Security posture — what is hardened, what is not](#7-security-posture)
8. [Privacy posture — what data Regula collects](#8-privacy-posture)
9. [Vendor evaluation answers](#9-vendor-evaluation-answers)
10. [Trust centre summary](#10-trust-centre-summary)

---

## 1. Who built it and what is it

Regula is an **open-source command-line tool** that combines code scanning
with governance questionnaires for EU AI Act compliance at the point of
creation. It is licensed
under the Apache License 2.0. The full source is on GitHub at
[github.com/kuzivaai/getregula](https://github.com/kuzivaai/getregula).
PyPI package: [`regula-ai`](https://pypi.org/project/regula-ai/).

It is **not a SaaS, not a hosted service, not an API**. It runs entirely
on the developer's machine. No code, no findings, no telemetry leave the
machine unless the user explicitly opts in to anonymous crash reporting.

It is **not a legal opinion**, not a substitute for a Data Protection
Impact Assessment, not a guarantee of Article 6(3) exemption, and not a
vendor audit. Regula tells you what your code looks like under the EU
AI Act's published rules. The legal interpretation of those signals is
your lawyer's job, not Regula's.

---

## 2. What Regula does (and does not) claim

| Claim | Evidence |
|---|---|
| Detects 8 prohibited AI practices (Article 5 of Regulation (EU) 2024/1689) | `regula classify --text "predictive policing system"` |
| Detects 10 high-risk categories (Annex III + 2 Annex I categories cross-referenced by Article 6(1)) | `regula classify --text "classify_resume function"` |
| Maps every finding to specific articles of the EU AI Act | `regula classify --text "credit scoring model" --format json` |
| Maps every finding to ISO 42001, NIST AI RMF, NIST AI 600-1, NIST CSF 2.0, SOC 2 TSC, ISO 27001, OWASP LLM Top 10, MITRE ATLAS, CRA, ICO/DSIT, LGPD, Marco Legal IA | `cat references/framework_crosswalk.yaml` |
| Generates Annex IV conformity evidence packs | `regula conform .` |
| Generates Annex VIII registration packets | `regula register` |
| Cross-file Article 14 human-oversight detection (Python) | `regula oversight` |
| CycloneDX 1.7 ML-BOM with GPAI signatory annotations | `regula sbom --ai-bom` |
| Machine-readable risk indication as JSON-LD, *aligned to* (not certified against) the DPVCG EU-AIAct vocabulary — a W3C Community Group report, **not a ratified W3C Standard** | `regula dpv .` |
| SHA-256 hash-chained tamper-evident audit log | `regula audit verify` |
| 2,690 unique tests (2,690 pytest-collected), 6 self-tests; versioned open-alert inventory retained | see [§3](#3-reproducibility) and [SECURITY.md](../SECURITY.md) |

| Claim Regula does **NOT** make | Why |
|---|---|
| "Compliant with the EU AI Act" | Compliance is a legal determination. Regula cannot make it. |
| "100% precision" | Regula is intentionally tuned for recall on Annex III/Article 5. False positives at the INFO tier are documented and quantified — see [the precision/recall report](benchmarks/PRECISION_RECALL_2026_04.md). |
| "Audits your AI vendor" | Regula sees your code, not the vendor's. It surfaces vendor names and their published GPAI Code of Practice signatory status, nothing more. |
| "Replaces a DPIA / FRIA / HRIA" | These are organisational processes that involve people, policy, and stakeholder consultation. `regula conform --organisational` provides a structured self-assessment questionnaire for Articles 9/17/27/72, but the output is a self-reported evidence document, not a compliance certificate. A qualified assessor must verify the answers. |
| "Works on every language" | Python and JS/TS have full AST + cross-file flow. Java/Go/Rust/C/C++ are regex-only. This is documented in [`docs/architecture.md`](architecture.md). |

---

## 3. Reproducibility

> This document provides reproduction commands for selected, version-bounded
> facts. Runtime is environment-dependent, and known exceptions are retained.
>
> **One documented exception, stated here rather than discovered later.** The
> landing page's `regula gap` / `regula comply` demo panel (9% overall,
> Article 11 at 25%) does NOT currently reproduce from a clean checkout: it
> was generated on a machine whose copy of the scanned fixture held a
> gitignored `.regula/` directory, which the Article 11 checker credits. A
> clean clone yields 6% and 0%. The generator now refuses to build from
> untracked inputs, so this cannot recur; correcting the published figures
> is pending and tracked as ledger row N43 in
> [`docs/improvement/LEDGER.md`](improvement/LEDGER.md).

### 3.1 Internal test suite — 2,690 [unique](../tests/) / 2,690 pytest-collected, all green

```bash
git clone https://github.com/kuzivaai/getregula.git
cd getregula
python3 -m pytest tests/ -q
# Expected: 2690 passed. Wall-clock is machine-dependent and is NOT a claim;
# it has varied by a factor of two on one laptop in a single day. Quote the
# count, never the duration.
# 2,690 unique tests (sort -u of test IDs equals collected count).
```

Regula also ships a legacy auto-discovery runner for the classification
suite — run `python3 tests/test_classification.py` for its current output.
The runner currently discovers 1,088 functions, a count machine-checked by
`tests/test_published_count_manifest.py`). **Read that line carefully:
`1386 passed` is not a count of tests.** The runner's counter is incremented by
the `assert_true` / `assert_eq` / `assert_false` helpers in `tests/helpers.py`,
so it counts helper assertions, and a test written with a bare `assert`
contributes nothing to it. The figure was **also 1386 when the runner executed
978, 1010, 1011, 1015, 1023, 1033, 1043, 1051, 1056, 1059 and 1060 functions**: 82 functions were added across those
runs and not one of them uses the helpers. **The number to read is the function count
in brackets.** It walks `globals()` of `tests/test_classification.py`,
finds every `test_*` function, and executes it; 437 of those functions
are defined in the file itself, the rest are aliased in from other test
modules. The pytest total above covers this suite
plus all dedicated test files (signing, timestamping, evidence format
v1, dependency pinning, and others).

### 3.2 Self-tests — 6 / 6

```bash
python3 -m scripts.cli self-test
# Expected: 6/6 passed
```

Six round-trip assertions covering: prohibited practice detection,
high-risk classification, minimal-risk classification, credential
detection, framework mapping, limited-risk classification.

### 3.3 Doctor — environment health

```bash
python3 -m scripts.cli doctor
# Expected on a fresh install (inside a git repo): 8 passed, 4 info, 0 warn
# Expected on a fresh install (outside a git repo): 8 passed, 4 info, 1 warn
#   The 4 info messages cover: no hooks installed, no ai_officer in policy,
#   telemetry not configured, and no domain declared. The 1 warn (outside
#   git) is ".gitignore not found". Telemetry moves from INFO to PASS only
#   if you both opt in and set REGULA_SENTRY_DSN; 12 checks run either way.
```

Lists every optional dependency, hook installation status, audit
directory writability, and policy file presence. INFO entries for
optional features are not warnings — they are reminders that
`pipx install "regula-ai[yaml,ast]"` would unlock more features.

### 3.4 Synthetic precision and recall: classifier path, all domains declared, prohibited 5/5, high-risk 16/30

```bash
python3 benchmarks/synthetic/run.py
# Expected (corpus v2.0, measured 2026-07-28):
#   prohibited   tp=5   fp=0  fn=0
#   high_risk    tp=16  fp=0  fn=14
# The command prints these as percentages. Prohibited recall is 5/5.
# High-risk recall is 16 of 30 on the classifier path.
```

**38 hand-crafted fixtures** covering 5 Article 5 prohibited practices,
**30** Annex III high-risk categories, and 3 negative cases. Ground truth
is the human-authored fixture set in `benchmarks/synthetic/fixtures/`.

> **This section previously claimed "100 / 100" against a 13-fixture
> corpus (5 high-risk).** The high-risk set was expanded to 30 on
> 28 July 2026 and recall fell to **16 of 30**. The old figure was not a
> misstatement at the time; it was **underpowered** — 5 fixtures happened
> to sample categories that pass. Corrected here rather than left
> unreproducible.
>
> **Gate conditions change this number more than anything else does.** The
> 53% above is the **classifier** path (`report.scan_files`, what `run.py`
> measures) with all eight opt-in domains declared. The **scanner** path
> (`regula check`, what a user actually runs) with **no flags** gives
> **10 of 30** on the same corpus, because opt-in domain suppression and an
> AI-library-indicator requirement gate findings the classifier assigns.
>
> Every figure below is reproducible from `benchmarks/synthetic/RECALL.json`,
> which `scripts/build_recall_artefact.py` produces from an actual run:
> **scanner path, default scan 10/30**; **scanner path, all domains declared
> 16/30**; **scanner path, domains declared with an AI import injected
> 23/30**; **classifier path, all domains declared 16/30**. Prohibited
> recall is **5/5** on every one of them.
>
> **No recall figure may be quoted without naming its path and its gate
> condition** — `claim_auditor --verify-facts` now rejects one that is not.
> The earlier "14/30 domain-declared" and "19/30 with both gates" figures
> are WITHDRAWN as NOT REPRODUCIBLE: the conditions behind them were never
> committed. Full decomposition, including the 17-vs-3
> gates-vs-patterns split, is in
> `benchmarks/headtohead/RESULTS-synthetic-v2-2026-07-28.md`.
>
> **Finding F8 (scanner and classifier disagree) is not supported by the
> artefact.** Under the same gate condition the two paths miss the
> identical 14 fixtures. The divergence previously recorded compared two
> different gate conditions as well as two paths.

### 3.5 OSS precision benchmark — published, sliced, reproducible

The full report is at
[`docs/benchmarks/PRECISION_RECALL_2026_04.md`](benchmarks/PRECISION_RECALL_2026_04.md).

```bash
# Headline precision (blind-labelled random corpus, production code only):
python3 benchmarks/label.py score --corpus random
# Expected: 83.5% precision (N=115)
# Labelled by a single reviewer; no inter-rater agreement measurement
# exists. See benchmarks/README.md.

# Full development corpus (library + application projects, all code):
python3 benchmarks/label.py score
# Expected: 36.8% precision (N=446)
```

**Two corpora, two numbers — both honest, different scopes.** The
headline precision is **83.5%** (N=115, **measured on Regula v1.7.0**,
labelled by a **single reviewer** with no inter-rater agreement
measurement, see [`benchmarks/README.md`](../benchmarks/README.md)),
on production code from a random corpus of 50 Python AI repos selected
via GitHub API (pool of 276, random seed 42) and blind-labelled
(labeller saw only file path, code context, and finding description —
no project name, README, or purpose). This measures what users see
with default `--skip-tests` and domain-gating settings.

> **Version note:** Precision figures are re-measured per release where
> the corpus permits. Pattern additions in v1.7.1+ (including Article
> 5(1)(ba)/(bb) NCII/CSAM detection) are not yet reflected in benchmark
> numbers. Figures cite the Regula version they were measured on. Per-tier:
`ai_security` (85%), `agent_autonomy` (83%), `limited_risk` (88%),
`minimal_risk` (100%). The `high_risk` tier (33%, N=6) remains weakest and is
**statistically unmeasurable** at this sample size — corpus expansion
to N>=30 is required before any meaningful conclusion about high_risk
precision. Six subcategories now require `--domain` declaration or
import fingerprinting to fire. All per-tier figures in this note are the
rounded values from the N=115 published benchmark recorded in
[`benchmarks/README.md`](../benchmarks/README.md).

The development corpus (`python3 benchmarks/label.py score`, no flags)
scores **36.8%** on 446 entries across 5 AI library projects and 12
application projects. The library subset (scikit-learn, langchain,
pydantic-ai, instructor, openai-python) alone is 15.2% — AI framework
infrastructure code is the hardest corpus, analogous to running an SQL
injection scanner on psycopg2 itself. Discovering this 36.8% figure is
not a contradiction of the 83.5% headline (N=115, single reviewer, see
[`benchmarks/README.md`](../benchmarks/README.md)) — it is a different corpus
measuring a different thing.

**Development corpus per-tier precision (v1.7.3, `benchmarks/label.py score --breakdown`):**

| Tier | TP | FP | Precision |
|------|-----|-----|-----------|
| ai_security | 33 | 11 | 75.0% |
| agent_autonomy | 47 | 20 | 70.1% |
| limited_risk | 5 | 3 | 62.5% |
| high_risk | 38 | 38 | 50.0% |
| credential_exposure | 2 | 5 | 28.6% |
| minimal_risk | 39 | 205 | 16.0% |
Source: `benchmarks/results/random_corpus/METHODOLOGY.json`, regenerated by `benchmarks/label.py score --breakdown` on the 446-entry development corpus.

**By corpus type:** application code 66.1% (125 TP, 64 FP); library source code 15.2% (39 TP, 218 FP). Source: [`benchmarks/results/random_corpus/METHODOLOGY.json`](../benchmarks/results/random_corpus/METHODOLOGY.json).

**By language:** Python 36.7% (160 TP, 276 FP); TypeScript 0.0% (0 TP, 6 FP); Jupyter/YAML/PKL 100% (3 TP, 0 FP; N too small for significance). Source: `benchmarks/results/random_corpus/METHODOLOGY.json`.

Full methodology: `benchmarks/results/random_corpus/METHODOLOGY.json`.

### 3.5 Known limitations

- **TypeScript precision is 0% on the current benchmark** (0 TP, 6 FP). All six TypeScript false positives are domain-keyword matches in code where no AI inference occurs. Regula has no TypeScript-specific AST gating, so TypeScript findings should be treated as advisory. Source: [`benchmarks/results/random_corpus/METHODOLOGY.json`](../benchmarks/results/random_corpus/METHODOLOGY.json).
- **Library source code** has 15.2% precision on the measured library corpus, compared with 66.1% for measured application code. AI frameworks implement APIs that the patterns flag, so use `--scope production` and `--skip-tests` to focus on application code. Source: [`benchmarks/results/random_corpus/METHODOLOGY.json`](../benchmarks/results/random_corpus/METHODOLOGY.json).

### 3.6 Security posture — bandit, semgrep, pip-audit

```bash
# Bandit and pip-audit are lightweight:
pip install bandit pip-audit
bandit -c pyproject.toml -r scripts/ hooks/
# Expected: 0 low / 0 medium / 0 high
pip-audit
# Expected: 0 vulnerabilities (zero runtime deps)

# Semgrep is heavier (~150 MB) and optional. Skip if you only have
# capacity for the quick pass:
pip install semgrep
semgrep --config p/security-audit --config p/python scripts/ hooks/
# Expected: 0 findings (200 rules, 129 files)
```

Per the [comparative SAST research](https://semgrep.dev/blog/2021/python-static-analysis-comparison-bandit-semgrep/),
running both bandit and semgrep is the standard hardened-Python audit.
Regula passes both at the published version. Bandit's project config
is in `pyproject.toml [tool.bandit]` with every project-level skip
documented and rationalised.

Bandit project config in `pyproject.toml [tool.bandit]` documents every
project-level skip with rationale. Hard checks (B101 assert, B102 exec,
B301 pickle, B501–B507 ssl/tls, B601–B602 shell injection, B608 sql
injection) remain enabled.

---

## 4. Tamper-evidence

Regula maintains a SHA-256 hash-chained audit log of every scan it runs
on a developer's machine. This is the same construction used by
RFC 6962 Certificate Transparency.

```bash
regula audit show           # human-readable view
regula audit show --format json
regula audit verify         # walks the chain, recomputes every hash
# Expected: "Audit chain verified (N entries, no tampering detected)"
```

If a single byte of any past entry has been altered, `regula audit verify`
will report the exact entry where the chain breaks. The user can verify
this themselves by editing one character of `~/.regula/audit/*.jsonl` and
re-running the verify command.

### Project scoping

Audit events are attributed to the project they were recorded in and
stored in per-project chains (`~/.regula/audit/projects/<slug>/`).
Deliverables — evidence packs, conformity packs, HTML reports — embed
only the scanned project's own chain, never events from other projects
on the same machine. `regula audit verify --project <path>` verifies a
single project's chain; without `--project` it verifies the machine
store and every project chain.

Two honesty notes. First, log files rotate monthly, and versions before
v1.7.5 started each new monthly file from the genesis hash instead of
continuing the chain. Verification therefore reports a genesis seed at
the start of a file as a "legacy restart" rather than failing; the
consequence is that truncating a *legacy* store exactly at a month
boundary is not detectable by the chain alone. Chains written by
current versions are continuous across files, so this forgiveness does
not extend to new data. Second, events recorded by versions without
project scoping live unattributed in the machine-wide store; they are
excluded from deliverables and each deliverable's audit section says so.

### Optional: third-party RFC 3161 timestamping

```bash
regula audit anchor --tsa https://freetsa.org/tsr
```

This sends a SHA-256 of the current audit log head to a public RFC 3161
Time Stamp Authority and stores the signed timestamp token. Anyone with
the token can later prove the audit log existed in its current form at
that time. Regula does not require trust in any specific TSA — the user
sets `REGULA_TSA_URL` to the authority of their choice.

---

## 5. Transparency

Every Regula finding is paired with:

1. The article of the EU AI Act it maps to (e.g. Article 9, Article 14)
2. The ISO 42001 control it relates to (e.g. A.6.3, A.6.6)
3. The NIST AI RMF function (e.g. GOVERN, MAP, MEASURE, MANAGE)
4. The exact pattern in `scripts/risk_patterns.py` that fired
5. The exact `file:line` in the user's code

```bash
regula classify --text "classify_resume function" --format json
# Returns the full structured envelope with all five fields above
```

There are no opaque ML scores. There are no "trust the model" outputs.
Every finding is traceable to a specific regular expression in a
specific file in the open-source repo. A reviewer can read the pattern
and decide for themselves whether it is too broad or too narrow.

### Regulatory currency

Deadline and status copy is not hand-maintained per page: it derives
from a single source (`scripts/omnibus.py`) consumed by every CLI
output, registration packet, and report, and a test
(`tests/test_source_of_truth.py`) fails the build if any consumer
drifts. This mechanism exists because the manual approach failed us:
when the Digital Omnibus changed the EU AI Act's status in June 2026,
the correction had to be hand-edited into six files and two were
missed. The prose now lives in one constant, and the next status
change (Official Journal publication) is a one-line flip that the
test suite propagates and checks. Changes to the regulatory record
are tracked in a public delta log (`content/regulations/delta-log/`).

---

## 6. Independent verification

| Resource | Where |
|---|---|
| Source code | <https://github.com/kuzivaai/getregula> |
| PyPI package | <https://pypi.org/project/regula-ai/> |
| Direct contact | `support@getregula.com` |
| Issue tracker | <https://github.com/kuzivaai/getregula/issues> |
| Security disclosures | <https://github.com/kuzivaai/getregula/security/advisories/new> or `support@getregula.com` |
| Test suite | `tests/` (2,690 unique tests, 2,690 pytest-collected; the legacy `tests/test_classification.py` runner executes 1,088 functions, 440 defined in-file) |
| Pattern definitions | `scripts/risk_patterns.py` |
| Framework mapping | `references/framework_crosswalk.yaml` |
| Pre-commit hook source | `hooks/pre_tool_use.py` |
| MCP server source | `scripts/mcp_server.py` |
| Benchmark corpus | `benchmarks/labels.json` |
| Self-scan (Regula run on its own repo) | [`docs/self-scan-results.md`](self-scan-results.md) |
| Primary research citations | `references/FETCH.md` |
| Changelog | `CHANGELOG.md` |
| Known gaps and limitations | `docs/what-regula-does-not-do.md` |

The repository is intentionally legible. There are no compiled binaries,
no obfuscated bytecode, no generated code committed without the
generator. A reviewer can read every line of every file Regula will run
on their machine.

### 6.1 Verify an evidence pack without installing Regula

A Regula evidence pack is designed so that the party *receiving* it — a
client's auditor, counsel, or security team — can verify it without
trusting or installing Regula. Two independent tiers, both specified in
[Evidence Format v1](spec/regula-evidence-format-v1.md):

**Tier 1 — file integrity (Python standard library only).** Every pack
file's SHA-256 is recorded in `manifest.json`:

```python
import hashlib, json, sys
from pathlib import Path

pack = Path(sys.argv[1])
manifest = json.loads((pack / "manifest.json").read_text(encoding="utf-8"))
for entry in manifest["files"]:
    digest = hashlib.sha256((pack / entry["filename"]).read_bytes()).hexdigest()
    assert digest == entry["sha256"], f"TAMPERED: {entry['filename']}"
print(f"{len(manifest['files'])} file hashes match the manifest")
```

**Tier 2 — signature (needs only `pip install cryptography`).** Signed
packs embed an Ed25519 signature over the canonical manifest
(spec §4.5), with the public key in the pack:

```python
import base64, json
from cryptography.hazmat.primitives.serialization import load_pem_public_key

sig = manifest["signing"]
stripped = {k: v for k, v in manifest.items()
            if k not in ("signing", "timestamp_authority")}
canonical = json.dumps(stripped, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=False).encode("utf-8")
pub = load_pem_public_key(base64.b64decode(sig["public_key"]))
pub.verify(base64.b64decode(sig["signature"]), canonical)  # raises if invalid
print("Ed25519 signature VERIFIED")
```

Both walkthroughs were executed against a pack generated by the
released `regula-ai` 1.7.5 on 16 July 2026: 9/9 hashes matched, the
signature verified, and a deliberately flipped byte in one pack file
was caught by tier 1 (then restored).

Why this design matters: Ed25519 is an asymmetric scheme, so the
verifying party never holds signing capability — anyone with the pack
can check it, and nobody who can check it can forge it. A symmetric
scheme (e.g. an HMAC chain) cannot offer that separation: verification
requires the same secret that creates the records, so any party able
to verify is also able to forge, and third-party verification without
key disclosure is impossible. The distribution pipeline carries the
same property end-to-end — the PyPI release is published via OIDC
trusted publishing with PEP 740 attestations, so the package itself
is provenance-verifiable before you run it.

---

## 7. Security posture

### 7.1 What is hardened

- **Zero runtime dependencies.** Regula's core only uses Python's
  standard library. Optional features (YAML parsing, AST analysis, PDF
  export) are explicit opt-ins via `pipx install "regula-ai[yaml,ast,pdf]"`.
  Verify with `pip show regula-ai`.
- **Deterministic output.** Same input + same policy file produces
  byte-identical JSON output. Verify by running `regula check --format
  json` twice and `diff`-ing the results.
- **Schema-versioned JSON envelope.** Every JSON command output includes
  `format_version`, `regula_version`, `command`, `timestamp`, and
  `exit_code` so machine consumers can detect schema drift.
- **Hooks run in subprocess isolation.** The pre-commit hook is a
  separate Python script and cannot affect the parent process state.
- **No network calls in the core scanner.** `regula check` is fully
  offline. Network calls are scoped to opt-in commands: `regula feed`
  (governance news), `regula audit anchor` (RFC 3161 TSA), and
  `regula bias` (CrowS-Pairs dataset download, when network is available).
- **All `urllib.urlopen` call sites enforce `http(s)` only.** The
  `_require_http_url()` guard rejects `file://`, `ftp://`, `data://`
  schemes before any network call. Verified by semgrep
  `dynamic-urllib-use-detected` rule.
- **XML feed parsing prefers `defusedxml`** when available, falls back
  to `xml.etree` with a 10 MiB size cap to defuse XML-bomb vectors.
- **Credential detection has tested heuristics.** See `tests/`
  `test_classification.py::test_credentials_*` for the regression set.

### 7.2 What is NOT hardened

Honest list of things a buyer should ask about and what Regula's answer
currently is:

| Question | Answer |
|---|---|
| Do you have a SOC 2 Type II report? | No. Regula is an open-source CLI tool, not a hosted service. There is no Regula infrastructure to audit. The equivalent is the open-source code itself plus the bandit/semgrep/pip-audit clean state. |
| Have you had a third-party penetration test? | No. The attack surface is the user's local machine + opt-in network calls listed above. The code is open for review. |
| Do you have a CVE program? | Yes — [`SECURITY.md`](../SECURITY.md) defines the disclosure flow, supported versions, and target response times. Private disclosure via GitHub Security Advisory or `support@getregula.com`. The next public CVE we receive will also be the moment we register as a CNA. |
| Do you sign releases with Sigstore? | Not yet. Releases are reproducible from source via `python3 -m build`. |
| Do you have an SBOM for your own releases? | Yes — Regula generates one of itself: `regula sbom --ai-bom` from a checkout. |

### 7.3 Supply chain security

Regula's supply chain attack surface is intentionally minimal.

- **Zero runtime dependencies.** The core scanner uses only the Python
  standard library. Verify with `pip show regula-ai` — the `Requires`
  field is empty. This eliminates transitive dependency compromise as
  an attack vector.
- **Reproducible builds from source.** Anyone can rebuild the wheel from
  a tagged commit and compare the SHA-256 against the PyPI artefact.
  See [`SECURITY.md`](../SECURITY.md) "How to verify a release
  independently" for the exact steps.
- **No compiled binaries or obfuscated bytecode.** Every file in the
  repository is human-readable source. There is no `.so`, `.dll`,
  `.pyc`, or minified code committed.
- **Optional dependencies are explicit opt-ins.** `pyyaml`,
  `tree-sitter`, `weasyprint`, and `sentry-sdk` are declared as extras
  in `pyproject.toml` (e.g. `pipx install "regula-ai[yaml,ast,pdf]"`).
  They are never pulled in by a bare `pip install regula-ai`.
- **SBOM self-generation.** Regula can generate a CycloneDX 1.7 ML-BOM
  of itself from any checkout: `regula sbom --ai-bom`. This includes
  component hashes and dependency declarations.
- **OpenSSF Scorecard.** Adopting the OpenSSF Scorecard
  (<https://scorecard.dev>) for automated supply chain hygiene checks
  is on the roadmap. It is not yet run in CI — do not treat it as a
  current achievement.

### 7.4 Incident response

The formal vulnerability disclosure process is defined in
[`SECURITY.md`](../SECURITY.md). The key commitments are:

| Stage | Target |
|---|---|
| Acknowledgement of report | within 72 hours |
| Initial triage and severity confirmation | within 7 days |
| Fix or mitigation merged to `main` | within 30 days for high/critical |
| Coordinated disclosure | within 90 days from initial report |

If a fix takes longer than the target, the reporter will receive a
written explanation and an updated estimate. Reports are never
silently ignored.

The 90-day coordinated disclosure timeline is the default. Reporters
who require a different timeline (e.g. regulatory deadlines or
embargoed industry disclosure) should state this in the initial report.

Report privately via:
1. **GitHub Security Advisory** —
   <https://github.com/kuzivaai/getregula/security/advisories/new>
2. **Email** — `support@getregula.com` with subject `[SECURITY] <short
   description>`

### 7.5 Reported vulnerabilities

None as of the published version. Report security issues privately by
opening a GitHub Security Advisory at
<https://github.com/kuzivaai/getregula/security/advisories/new>.

---

## 8. Privacy posture

### 8.1 What Regula collects from a user's machine

**By default: nothing.** No telemetry, no usage stats, no error reports.

`regula doctor` will report `Telemetry — disabled` on a fresh install.

### 8.2 What Regula collects if telemetry is opted in

Crash reporting requires **both** of the following. Neither is the default:

1. the user runs `regula telemetry enable`, and
2. a Sentry endpoint is configured, via the `REGULA_SENTRY_DSN`
   environment variable.

The published PyPI build ships `_SENTRY_DSN = ""` (empty) and reads the
endpoint from the environment, so **even if the user opts in, nothing is
sent unless they point Regula at a Sentry instance themselves.** This is
by design: Regula is a tool for compliance teams, many of whom cannot
legally exfiltrate any data to a third party.

Verify with:

```bash
grep -n "^_SENTRY_DSN" $(pip show regula-ai | grep Location | cut -d: -f2)/scripts/telemetry.py
# Expected: _SENTRY_DSN = ""
```

When an endpoint *is* configured and consent given, an uncaught exception
sends: the exception type and message, a stack trace through Regula's own
code, and the Regula, OS and Python versions. Stack-frame local variables
are explicitly disabled (`include_local_variables=False`) because Regula's
scan frames hold whole scanned files in memory, and the auto-detected
hostname is replaced with `redacted`. One residual caveat, stated because
it cannot be fully prevented: an exception *message* can itself contain a
file path (for example a permission error naming the file).

Sending is suppressed regardless of stored consent when any of
`DO_NOT_TRACK`, `REGULA_NO_TELEMETRY`, or `CI` is set to a value other
than `0`/`false`/`no`. `DO_NOT_TRACK` follows the cross-tool CLI
convention (<https://consoledonottrack.com>).

> **Correction (21 Jul 2026).** Between commit `43da24c` (10 Apr 2026) and
> this change, `_SENTRY_DSN` was hardcoded to a live endpoint while this
> section continued to state it was empty — so the claim above was false
> for releases in that window, including v1.7.7 on PyPI. Reaching the
> endpoint still required the optional `sentry-sdk` extra to be installed
> *and* explicit opt-in, so the default-install posture was unaffected.
> The DSN is now read from the environment and defaults to empty, which
> restores the documented behaviour.

### 8.3 What Regula sends over the network

Only when the user explicitly invokes the relevant command:

| Command | Endpoint | Data sent |
|---|---|---|
| `regula feed` | curated RSS/Atom feed URLs in `scripts/feed.py` (IAPP, EDPB, ICO, etc.) | HTTP GET only — no user data sent |
| `regula audit anchor` | user-configured RFC 3161 TSA (default `freetsa.org`) | A SHA-256 hash of the local audit log head. The hash itself reveals nothing about the user's code. |
| `regula bias` | `raw.githubusercontent.com/nyu-mll/crows-pairs/master/...` | HTTP GET only. Falls back to bundled 20-pair sample if network unavailable. |

Core scan paths are designed for local execution. This repository has not
completed operating-system-level network observation for every command and
environment. Optional timestamping, configured telemetry, update/feed paths,
and other explicitly network-enabled features are excluded from any local-only
statement.

---

## 9. Vendor evaluation answers

The questions a 2026 procurement team will ask, with copy-pasteable
answers.

**Q: What is the deployment model?**
A: Local-only command-line tool. Installs via `pipx install regula-ai`.
No accounts, no servers, no SaaS tier exists.

**Q: Where is data stored?**
A: Core scan output, audit logs, and generated scaffolds are written to
the user's local filesystem under `~/.regula/` and the project directory.
Optional network-enabled features have separate boundaries and must be assessed.

**Q: What is the licensing model?**
A: Apache License 2.0 (with EUPL-1.2 dual-licence option). Commercial
use, redistribution, and modification are permitted. There is no paid
tier. The maintainer accepts sponsorships but does not gate features
behind payment.

**Q: How do you handle GDPR / DPA / SCCs?**
A: Core scan paths are designed to process source locally. Whether a controller-
processor relationship, DPA, SCCs, or other privacy measure is required depends
on the actual deployment, data, roles, and optional features; Regula does not
make that legal determination.

**Q: What is the support model?**
A: Best-effort via `support@getregula.com` and GitHub Issues. Response
time is not contractually guaranteed. For enterprises that need a
paid SLA, email `support@getregula.com` to discuss a separate support
agreement.

**Q: How do we verify Regula's claims independently?**
A: Run the commands in section 3 above. Read the patterns in
`scripts/risk_patterns.py`. Read the framework mappings in
`references/framework_crosswalk.yaml`. Read the test suite. Read the
benchmark report. Cite the published methodology in your own internal
audit.

**Q: Who maintains the regulatory mapping?**
A: A single maintainer at present. Every regulatory claim is paired
with an article reference and a primary-source citation. The AICDI
2025 figures are page-cited against the
published PDF (ISBN 978-92-3-100863-4, DOI 10.54678/YJWP8855); the
`references/FETCH.md` file records the SHA-256 of the canonical PDF.

**Q: What happens if you stop maintaining Regula?**
A: The repository is open source under Apache 2.0. Anyone can fork it. The
test suite is comprehensive enough that a competent maintainer can
verify a fork. The pattern definitions are flat data files that
anyone can update without touching the engine.

---

## Reading order for evaluators

If you have **15 minutes**, run the commands in [§3](#3-reproducibility)
and read [§2](#2-what-regula-does-and-does-not-claim).

If you have **1 hour**, also read
[`docs/benchmarks/PRECISION_RECALL_2026_04.md`](benchmarks/PRECISION_RECALL_2026_04.md)
(the precision/recall report) and
[`docs/what-regula-does-not-do.md`](what-regula-does-not-do.md)
(the scope statement).

If you have **half a day**, also read
[`scripts/risk_patterns.py`](../scripts/risk_patterns.py),
[`references/framework_crosswalk.yaml`](../references/framework_crosswalk.yaml),
and [`docs/architecture.md`](architecture.md).

If anything in this document is unclear, ambiguous, or unverifiable,
that is a bug. Open an issue.

---

## 10. Trust centre summary

Quick-reference table of all security and compliance evidence available
in this repository. Every row links to a verifiable artefact.

| Evidence | Location | What it covers |
|---|---|---|
| Vulnerability disclosure policy | [`SECURITY.md`](../SECURITY.md) | Supported versions, reporting channels, response timelines, scope |
| Trust pack (this document) | [`docs/TRUST.md`](TRUST.md) | Reproducibility, tamper-evidence, transparency, security and privacy posture, vendor evaluation Q&A |
| Licence | [`LICENSE.txt`](../LICENSE.txt) | Apache License 2.0 (with EUPL-1.2 dual-licence option) |
| Third-party notices | [`NOTICE`](../NOTICE) | Attribution for bundled data and referenced standards |
| Architecture overview | [`docs/architecture.md`](architecture.md) | Module map, data flow, scan pipeline, AST vs regex coverage |
| Scope and limitations | [`docs/what-regula-does-not-do.md`](what-regula-does-not-do.md) | Explicit list of what Regula is not and cannot do |
| Precision and recall benchmark | [`docs/benchmarks/PRECISION_RECALL_2026_04.md`](benchmarks/PRECISION_RECALL_2026_04.md) | Labelled corpus, methodology, per-tier and per-project breakdown |
| Framework crosswalk data | [`references/framework_crosswalk.yaml`](../references/framework_crosswalk.yaml) | EU AI Act ↔ ISO 42001 / NIST AI RMF / SOC 2 / etc. mappings |
| Pattern definitions | [`scripts/risk_patterns.py`](../scripts/risk_patterns.py) | All detection regexes, grouped by risk tier and category |
| Test suite | `tests/` | 2,690 unique tests (2,690 pytest-collected) |
| Self-test | `regula self-test` | 6 round-trip assertions |
| Environment health | `regula doctor` | 12 checks (pass/info split varies by environment) |
| SBOM | `regula sbom --ai-bom` | CycloneDX 1.7 ML-BOM from any checkout |
| Changelog | [`CHANGELOG.md`](../CHANGELOG.md) | Version history and breaking changes |

**Machine-readable security metadata.** A `security.txt` file
(per [RFC 9116](https://www.rfc-editor.org/rfc/rfc9116)) is on the
roadmap but not yet published. Until it is in place, the canonical
security contact is `support@getregula.com` and the disclosure process
is defined in [`SECURITY.md`](../SECURITY.md).

===== MODEL CARD =====
# Model Card — Regula Detection Engine

Regula's detection engine is a static analysis system that reports source-code indicators associated with EU AI Act risk categories. It does not determine legal classification. This document treats it as an AI system and documents its capabilities, limitations, and biases. To generate a model card scaffold for your own project, run `regula model-card --project /path/to/project`.

---

## System Overview

| Field | Value |
|---|---|
| Name | Regula Detection Engine |
| Version | 1.9.0 (this doc updated 2026-07-27) |
| Type | Rule-based static analysis (regex + AST pattern matching) |
| Training data | None — not a machine learning model |
| Detection patterns | 419 tiered risk regexes across 57 categories (10 prohibited + 18 high-risk + 4 limited-risk + 17 AI security + 2 bias + 6 governance observations) + 17 GPAI training regexes. Includes housing (Colorado SB 26-189), transportation (Korea AI Basic Act Art 33), and emotion inference split categories. Regenerate with `python3 scripts/site_facts.py`. |
| Languages supported | Python, JavaScript, TypeScript, Java, Go, Rust, C, C++ |
| Compliance frameworks | 13 with full crosswalk data (EU AI Act, NIST AI RMF, ISO 42001, NIST CSF, SOC 2, ISO 27001, OWASP LLM Top 10, OWASP Agentic (ASI), MITRE ATLAS, EU CRA, LGPD, Marco Legal IA, UK ICO) |
| Dependencies | Zero runtime (Python 3.10+ stdlib only); `regula[signing]` extra adds `cryptography` + `asn1crypto` for optional Ed25519 + RFC 3161 manifest signing. |

---

## Intended Use

**Primary use case:** Combine code scanning with governance questionnaires to assess compliance across 3 jurisdictions: EU AI Act (Regulation (EU) 2024/1689), South Korea AI Basic Act (Act No. 20676), and Colorado SB 26-189. Scan source code for risk patterns, run structured self-assessments for organisational obligations code cannot verify (Articles 9, 17, 27, 72), and generate compliance documentation scaffolds.

**Intended users:**

- Developers building AI-powered applications that may be deployed in or affect the EU market
- Small teams (1-20 people) who cannot afford enterprise governance SaaS
- Compliance officers who need a technical evidence base for governance programmes
- Auditors who need a starting point for code-level compliance assessment

**Deployment context:** Local CLI tool. Core scan paths are designed for local execution without an account or API key. Optional timestamping, configured telemetry, update/feed paths, and other explicitly network-enabled features are outside that boundary.

---

## Known Limitations

### Detection methodology

Regula uses regex pattern matching and lightweight AST analysis. It does not use machine learning, semantic understanding, or data flow analysis beyond import/call tracing.

**What this means in practice:**

- **Regex-only recall:** Regula detects patterns by matching code against regular expressions. If a developer implements a regulated behaviour using non-standard naming or architecture, Regula will not detect it. The system catches common patterns, not novel implementations.
- **No semantic understanding:** Regula cannot determine whether `model.predict(applicant)` is actually making a credit decision or is a test mock. Deployment context determines risk classification — code patterns alone cannot.
- **No cross-file data flow:** While `regula oversight` traces AI output to endpoints across files, the core `regula check` command analyses files independently. A prohibited practice split across multiple files may not be detected.

### Language depth disparity

Not all 8 supported languages are equally well-covered:

| Language | Pattern depth | Notes |
|---|---|---|
| Python | Deep | Most patterns were developed against Python codebases. Highest recall. |
| JavaScript/TypeScript | Moderate | Good coverage for common AI frameworks (TensorFlow.js, OpenAI SDK). |
| Java | Moderate | Covers Spring AI, DL4J, and common ML library imports. |
| Go | Basic | Covers common Go AI library imports. Fewer domain-specific patterns. |
| Rust | Basic | Covers tch-rs, candle, burn. Limited ecosystem coverage. |
| C/C++ | Basic | Covers TensorFlow C API, ONNX Runtime. Limited pattern set. |

A Python project will receive more granular findings than an equivalent Rust project. This is a known bias in the pattern set, not a language limitation.

### Precision baseline

Published benchmark against 50 randomly selected Python AI repos (from 276 candidates, random seed 42), **N=115**, blind-labelled by a **single reviewer** with no inter-rater agreement measurement (labeller saw only file path, code context, and finding description; see [`benchmarks/README.md`](../benchmarks/README.md)). Production code only (default `--skip-tests` settings):

| Tier | TP | FP | Precision |
|---|---:|---:|---:|
| `minimal_risk` | 11 | 0 | 100.0% |
| `limited_risk` | 7 | 1 | 87.5% |
| `ai_security` | 41 | 7 | 85.4% |
| `agent_autonomy` | 34 | 7 | 82.9% |
| `high_risk` | 2 | 4 | 33.3% |
| **Overall** | **96** | **19** | **83.5%** |
Source: [`benchmarks/README.md`](../benchmarks/README.md). N=115, single reviewer, no inter-rater agreement measurement.

**Improvement from v1.7.4:** Domain-gated high-risk findings, LLM import
gating, and justice opt-in reduced FP from 42 to 19 on the same labelled
corpus, improving production precision from 70.0% to 83.5%. 3 borderline
ai_security TPs were lost (LLM02 findings in files without LLM library imports).
Both figures are from the same N=115 corpus recorded in [`benchmarks/README.md`](../benchmarks/README.md).

The `high_risk` tier (33%) remains weakest — 6 subcategories (`critical_infrastructure`,
`safety_components`, `worker_management`, `democratic_processes`, `justice`,
`essential_services`) now require `--domain` declaration or import fingerprinting to fire. Including test
code drops overall precision to 60.6%. Both figures are recorded in [`benchmarks/README.md`](../benchmarks/README.md); note that 33% rests on N=6 and is not statistically meaningful at that sample size.

Full methodology and reproduction steps: `benchmarks/README.md`

---

## Bias Risks

### Systematic over-flagging

- **AI library imports:** Projects that import AI frameworks (PyTorch, TensorFlow, OpenAI SDK) will receive findings even if they are building developer tools, not regulated AI systems. The OSS benchmark deliberately measures this: 5 AI libraries produced 218 false positives at INFO tier.
- **Employment-related keywords:** Patterns for Annex III Category 4 (employment) match on keywords like `hiring`, `applicant`, `candidate`. HR software that is not an AI system may be flagged.

### Systematic under-flagging

- **Non-English code:** Pattern matching is English-centric. Variable names, comments, and identifiers in other languages will not match patterns expecting English keywords like `face_recognition` or `credit_score`.
- **Abstracted architectures:** Code that wraps AI operations behind generic interfaces (e.g., `service.process(request)`) will not be detected. The patterns expect explicit AI library usage.
- **Uncommon languages:** Go, Rust, C, and C++ have fewer patterns than Python. AI applications in these languages will systematically receive fewer findings.

### What is NOT a bias

- **High false positive rate on AI libraries** is by design. Regula's OSS benchmark corpus consists of AI frameworks, not AI applications. Flagging `import openai` in the OpenAI SDK itself is expected. The tool is designed for application code, not library code.

---

## Out-of-Scope Uses

Regula is explicitly **NOT** intended for:

| Use | Why it's out of scope |
|---|---|
| Legal advice | Regula identifies code patterns, not legal obligations. Deployment context determines classification. Consult a qualified legal professional. |
| Definitive compliance determination | A clean scan does not mean a system is compliant. Compliance requires deployment-context assessment, documentation, and ongoing governance. |
| Runtime monitoring | Regula performs static analysis on source code. It does not intercept, monitor, or evaluate running AI systems. |
| Replacing human review | Every finding requires human judgement about deployment context. Automated pass/fail decisions based solely on Regula output are inappropriate. |
| Auditor certification | Regula generates evidence artefacts (Annex IV docs, conformity packs). These are scaffolds for human review, not certified audit outputs. |

---

## Evaluation Methodology

### Synthetic corpus (recall measurement)

38 hand-crafted Python files (`benchmarks/synthetic/manifest.json`, version 2.0):
- 5 Article 5 prohibited practices (social scoring, subliminal manipulation, real-time biometric identification, emotion inference in workplaces, vulnerability exploitation)
- 30 Annex III high-risk categories
- 3 negative cases (non-AI code that should not be flagged)

**Recall depends on the code path and the gate condition, so a bare fraction is not a measurement.** Every figure below is regenerated from `benchmarks/synthetic/RECALL.json` by `tests/test_recall_artefact.py`, and a fixture counts as recalled when the highest tier detected equals the tier the manifest expects.

| Path and gate condition | High-risk | Prohibited |
|---|---:|---:|
| scanner, default scan, no flags | 10/30 = 33.3% | 5/5 |
| scanner, all eight domains declared | 16/30 = 53.3% | 5/5 |
| scanner, domains declared + AI-library import present | 23/30 = 76.7% | 5/5 |
| classifier (`report.scan_files`), all domains declared | 16/30 = 53.3% | 5/5 |
Source: `benchmarks/synthetic/RECALL.json`, produced from an actual run by `scripts/build_recall_artefact.py`.

**Corrected 29 July 2026.** This section previously described a 13-file corpus and reported **100% precision, 100% recall**. The corpus was expanded to 38 fixtures (high-risk 5 to 30) and the claim was never re-measured against it. The withdrawn figures are recorded here rather than deleted; the measured replacements are in the table above, from `benchmarks/synthetic/RECALL.json`. **Corrected again 29 July 2026.** The decomposition published here until today read "13 suppressed by opt-in domain gating, 4 by the AI-indicator gate, and 3 are genuine pattern gaps, so 17 of 20 misses are gate behaviour". Every component of that was wrong, and it understated the pattern-side weakness by more than double. It was carried over from an earlier recall table whose two lower rows are marked NOT REPRODUCIBLE in `benchmarks/headtohead/RESULTS-synthetic-v2-2026-07-28.md`. Derived from the per-fixture `missed` lists in `benchmarks/synthetic/RECALL.json` by set difference across the three scanner conditions: of the 20 high-risk fixtures missed on a default scan, **6 are recovered by declaring the opt-in domains, a further 7 by also having an AI-library import present, and 7 are never recovered under any measured condition**. So **13 of 20 misses are gate behaviour and 7 are pattern-side exposure**. Regenerated and asserted by `tests/test_recall_decomposition.py`, which recomputes the three numbers from the artefact and fails if this paragraph disagrees.

### Curated library corpus (development baseline)

257 findings hand-labelled across 5 mature open-source AI libraries (instructor, pydantic-ai, langchain, scikit-learn, openai-python). Each finding manually classified as TP or FP. Labels committed at `benchmarks/labels.json`. This corpus was used during development to tune patterns and is **not** the headline precision number — library code is mostly infrastructure, producing 15.2% precision at the `minimal_risk` tier.

### Random corpus (headline precision measurement)

50 randomly selected Python AI repos (from 276 candidates, seed=42), scanned with Regula v1.7.0. 201 findings stratified-sampled and blind-labelled by a **single reviewer** (labeller saw only file path, code context, and finding description — no project name, README, or purpose, see `benchmarks/labels.json`).

**Result:** 83.5% precision on production code (N=115, measured on Regula v1.7.0). **Labelled by one reviewer; no inter-rater agreement measurement exists.** Previous baseline was 70.0% before domain gating and LLM import gating. Figures re-measured per release where corpus permits; v1.7.1+ additions not yet reflected. Full methodology: `benchmarks/results/random_corpus/METHODOLOGY.json`; labelling limits: [`benchmarks/README.md`](../benchmarks/README.md) (the only repo-wide disclosure of the single-reviewer basis).

### Continuous validation

- 2,690 pytest-collected tests, produced by collection rather than
  hand-maintained (measured 2026-07-30). See
  [`data/published_count_manifest.json`](../data/published_count_manifest.json).
- 45 CLI integration tests (`tests/test_cli_integration.py`)
- 6 self-test assertions (`regula self-test`)
- 12 health checks (`regula doctor`)
- CI runs on every push across Python 3.10, 3.11, 3.12, 3.13

---

## Versioning

This model card describes Regula v1.9.0. If the detection patterns, classification logic, or evaluation methodology change, this document should be updated in the same commit.

---

*Last updated: 22 July 2026.*

===== ARCHITECTURE =====
# Architecture

Internal layout of the `scripts/` package, design principles, and language support.

## Architecture

```
regula/
├── .claude/skills/regula/SKILL.md  # Core skill file (Claude Code)
├── scripts/
│   ├── cli.py                     # Unified CLI entry point
│   ├── classify_risk.py           # Risk indication engine (confidence scoring)
│   ├── log_event.py               # Audit trail (hash-chained, file-locked)
│   ├── report.py                  # HTML + SARIF report generator
│   ├── install.py                 # Multi-platform hook installer
│   ├── feed.py                    # Governance news aggregator (7 sources)
│   ├── questionnaire.py           # Context-driven risk assessment
│   ├── session.py                 # Session-level risk aggregation
│   ├── baseline.py                # CI/CD baseline comparison
│   ├── timeline.py                # EU AI Act enforcement dates
│   ├── generate_documentation.py  # Annex IV + QMS scaffold generator
│   ├── discover_ai_systems.py     # AI system discovery, registry, compliance tracking
│   ├── credential_check.py        # Secret detection (18 patterns: 10 high + 8 medium confidence)
│   ├── ast_analysis.py            # AST-based Python analysis (data flow, oversight, logging)
│   ├── ast_engine.py              # Multi-language AST engine (Python + JS/TS tree-sitter + Java/Go/Rust/C/C++ regex)
│   ├── compliance_check.py        # Compliance gap assessment (Articles 9-15)
│   ├── dependency_scan.py         # AI dependency supply chain security
│   ├── framework_mapper.py        # Cross-framework compliance mapping (13 frameworks)
│   ├── remediation.py             # Inline fix suggestions per Annex III category
│   ├── agent_monitor.py           # Agentic AI governance (autonomy scoring, MCP config)
│   ├── sbom.py                    # CycloneDX 1.7 AI SBOM generation
│   ├── benchmark.py               # Real-world precision/recall validation
│   ├── aibom.py                   # AI Bill of Materials generator (CycloneDX 1.7)
│   ├── gdpr_patterns.py           # GDPR pattern definitions (14 patterns, 4 hotspots)
│   ├── gdpr_scan.py               # GDPR code pattern scanner
│   ├── roadmap.py                 # Compliance roadmap generator
│   ├── doc_audit.py               # Document quality scoring engine
│   ├── evidence_pack.py           # Self-verifying evidence bundle
│   ├── risk_decisions.py          # Annotation parser (regula-ignore / regula-accept)
│   ├── findings_view.py           # Finding view separation (active/suppressed/accepted)
│   ├── signing.py                 # Ed25519 manifest signing
│   ├── timestamp.py               # RFC 3161 timestamping
│   ├── adoption_pulse.py          # Passive PyPI + GitHub signal tracker
│   ├── monitor.py                 # Article 12 runtime monitoring SDK (MonitorSession, Trace)
│   └── cli_monitor.py             # CLI: regula monitor status|report|verify|prune|export
├── hooks/
│   ├── pre_tool_use.py            # PreToolUse hook (CC/Copilot/Windsurf)
│   ├── post_tool_use.py           # PostToolUse logging hook
│   └── stop_hook.py               # Session summary hook
├── references/                    # Regulatory reference documents
│   ├── owasp_llm_top10.yaml       # OWASP Top 10 for LLMs → EU AI Act mapping
│   └── mitre_atlas.yaml           # MITRE ATLAS → EU AI Act mapping
├── tests/                         # 101 test files, 2,690 tests (pytest --collect-only)
│   ├── test_classification.py     # Core classification tests (main test file)
│   └── ...                        # See tests/ for full list
├── docs/
│   └── course/                    # Interactive 10-module governance course
├── regula-policy.yaml             # Policy configuration template
└── .github/workflows/ci.yaml     # CI/CD
```

### Language Support

| Language | Analysis Depth | What It Detects |
|----------|---------------|-----------------|
| **Python** | Full AST | Data flow tracing, human oversight detection, logging practices, function/class extraction |
| **JavaScript/TypeScript** | Moderate (tree-sitter) | Import extraction, data flow tracing, oversight detection, logging. Tree-sitter optional — falls back to regex. |
| **Java** | Import detection (regex) | 13 AI libraries (Google AI Platform, LangChain4j, DJL, etc.) |
| **Go** | Import detection (regex) | 9 AI libraries (go-openai, langchaingo, etc.) |
| **Rust** | Import detection (regex) | 39 AI crates (candle, burn, tch, async-openai, etc.) + Cargo.toml parsing |
| **C/C++** | Include detection (regex) | 43 AI headers (LibTorch, TensorFlow, ONNX Runtime, llama.cpp, etc.) + CMake/vcpkg parsing |

**Honest note:** Only Python has deep AST analysis with data flow tracing. JS/TS with tree-sitter is moderate depth. Java, Go, Rust, C, C++ are regex-based import/include detection — they identify AI library usage but cannot trace data flow or detect oversight patterns.

### Design Principles

- **Core engine + thin adapters.** One classification engine, multiple platform integrations.
- **Same hook protocol.** Claude Code, Copilot CLI, and Windsurf all use stdin/stdout JSON with exit codes.
- **Confidence scores, not binary labels.** 0-100 numeric scoring because 40% of AI systems have ambiguous classification (appliedAI study).
- **Inline suppression with audit trail.** `# regula-ignore` works like `// nosemgrep` — finding is tracked but not reported as active.
- **SARIF for CI/CD.** Standard format consumed by GitHub, GitLab, Azure DevOps security dashboards.
- **Named governance contacts.** The policy file supports optional AI Officer and DPO fields. These fields do not represent an Article 4 requirement; AI-literacy measures and ISO/IEC 42001 role controls must be assessed separately.
- **Compliance workflow.** Tracked status progression with audit trail and transition history.
- **AST over regex where it matters.** Python `ast` module provides structure-aware analysis: real imports vs string mentions, data flow tracing, human oversight detection. Regex remains for cross-language pattern matching.
- **Compliance gap assessment, not just risk flagging.** Checks whether Articles 9-15 compliance infrastructure actually exists in the codebase.
- **AI-specific supply chain security.** Dependency pinning checks focus on AI libraries, not general packages.
- **Cross-platform.** Unix/macOS (`fcntl`) and Windows (`msvcrt`) file locking. No platform restrictions.
- **Multi-framework mapping.** 13 frameworks with full crosswalk data (EU AI Act, NIST AI RMF, ISO 42001, NIST CSF, SOC 2, ISO 27001, OWASP LLM Top 10, OWASP Top 10 for Agentic Applications, MITRE ATLAS, EU CRA, LGPD, Marco Legal IA, UK ICO) mapped via [references/framework_crosswalk.yaml](../references/framework_crosswalk.yaml). 5 additional frameworks have display handlers but no crosswalk data and no filter keys (Colorado SB-205, Canada AIDA, Singapore AI, OECD AI, South Korea AI) — filter keys removed in commit 7d93fed to prevent silent empty results.


## Site integrity guard

Region pages under `site/regions/` are generated from `content/regulations/*.py`
by `scripts/build_regulations.py`. Hand-editing the shipped HTML is what caused
the July 2026 Colorado drift — never do it; edit the source and rebuild.

`python3 scripts/site_integrity.py` enforces this:

- **regen** — re-renders every sourced page in memory and compares with the
  shipped file. Identical → OK; drift matching a reviewed fingerprint in
  `KNOWN_DRIFT` → WARN (ticketed); any other drift → FAIL.
- **sources** — every `site/regions/*.html` needs a content source or an
  explicit `EXEMPT_NO_SOURCE` entry.
- **links** — every internal href/src across `site/**/*.html` resolves.
- **claims** — `scripts/claim_auditor.py` over all site pages.

`--root DIR` runs against a copy (sandbox testing), `--fingerprint` prints
drift fingerprints when reviewing a known drift, `--check` selects subsets.
CI: `.github/workflows/site-integrity.yml` (inert until pushed).

===== VERSIONING =====
# Versioning and Deprecation Policy

> **Scheme:** Semantic Versioning 2.0.0, expressed within PEP 440.
> **Adopted:** 27 July 2026, with the 1.9.0 realignment release.
> **Enforced by:** `scripts/release_gate.py`, run by `release.yml` before
> every build; a release whose version bump understates its content does
> not publish.

## 1. Why this document exists

[`CHANGELOG.md`](../CHANGELOG.md) has claimed Semantic Versioning in its
header since 1.0.0, but the 1.7.x line shipped new functionality in
PATCH releases six times (its 1.7.2, 1.7.3, 1.7.5, 1.7.6, 1.7.8 and
1.7.10 sections all carry "Added" entries or feat content). SemVer 2.0.0 item 7 requires a MINOR increment for new
backward-compatible functionality, so those numbers understated what the
releases contained. Nothing checked the bump against the content, so the
drift went unnoticed until a user asked why the version was still 1.7.

SemVer's own remediation rule applies: released versions are immutable;
you correct a versioning mistake by releasing a new, correctly numbered
version, never by renaming or republishing old ones. **1.9.0 is that
corrective release.** Sections 5 and 6 record the decision in full.

## 2. The public API

SemVer item 1 requires a declared public API. Regula's public API, for
versioning purposes, is exactly this list:

| Surface | Covered |
|---|---|
| CLI commands and subcommands | Names and documented behaviour of every command in `regula --help-all` |
| Documented flags | Name, accepted values and documented semantics |
| Exit codes | The documented meanings (0 success, 1 findings/CI failure, 2 usage error) |
| JSON output envelope | The `json_output()` envelope structure (frozen) and documented field semantics |
| SARIF output | The structure consumed by GitHub code scanning |
| Evidence Format | `docs/spec/regula-evidence-format-v1.md` |
| Config file contracts | `regula-policy.yaml` / `regula-policy.json` and `regula-rules.yaml` accepted structure |
| Delta-log schema | `content/regulations/delta-log/schema.json` |

Explicitly **not** public API:

- Python import paths (`scripts/*`): Regula is a CLI, not a library.
  Importing its internals is unsupported and may break in any release.
- Detection pattern internals, tier regex counts and precision figures:
  these are quality characteristics, not interface contracts.
- The website, documentation prose and example artefacts.

## 3. Bump rules

| Change | Bump | Notes |
|---|---|---|
| Backward-incompatible change to any Section 2 surface | **MAJOR** | Includes removing or renaming a command or flag, renumbering exit codes, envelope changes, an incompatible Evidence Format revision |
| New command, flag, output field, framework mapping or jurisdiction | **MINOR** | New backward-compatible functionality |
| Deprecating any public API element | **MINOR** | SemVer item 7 makes deprecation a MINOR event |
| Bug fix, security fix with unchanged interface, pattern tuning, docs, site, CI | **PATCH** | |
| New detection patterns within existing commands | **MINOR** if they add a documented capability (a new category, tier or check), **PATCH** if they tune recall/precision of an existing one | Judgement call; the release gate takes the stricter of commit-type and changelog signals |

## 4. Deprecation policy

- A deprecation is announced in the CHANGELOG under `### Deprecated` and
  emits a runtime warning naming the replacement.
- Deprecated elements keep working for **at least one MINOR release and
  at least 90 days**, whichever is longer, before removal. The 90-day
  floor matches the common public-API norm (Kubernetes and Salesforce
  hold longer windows; 30 days is the minimum seen in major-vendor
  policies; 90 is a deliberate middle).
- Removal happens only in a **MAJOR** release.

## 5. The 1.7.x correction record

Releases whose numbers understated their content, from the CHANGELOG:

| Released as | Contained | SemVer-correct bump |
|---|---|---|
| 1.7.2 | Added | minor |
| 1.7.3 | Added | minor |
| 1.7.5 | Added (multiple) | minor |
| 1.7.6 | Added (DPV-AIAct export, a new command) | minor |
| 1.7.8 | Added | minor |
| 1.7.10 | feat commits (13th framework, MITRE ATLAS additions, enacted-Omnibus behaviour) | minor |

A strict reconstruction would place the project near 1.13.0, but that
number depends on judgement calls about each "Added" entry made months
later, so it is not recoverable with confidence. The realignment
therefore does not claim to compute the true number; it picks a clearly
documented reset point and enforces correctness from there.

## 6. Why 1.9.0, and why not the alternatives

- **Not 2.0.0:** SemVer reserves MAJOR for backward-incompatible
  changes. Nothing shipped or planned breaks the Section 2 API; a 2.0.0
  would tell users to expect breakage that does not exist.
- **Not 1.10.0 or higher:** PEP 440 orders release segments numerically,
  so 1.9.0 < 1.10.0 < 1.90.0; but humans routinely misread 1.10 as
  older than 1.9, and a compliance tool should not spend trust
  explaining its own version string. 1.9.0 is unambiguous.
- **Not 1.8.0:** equally legal, but the drift spans six releases, and
  the smallest possible bump reads as routine rather than corrective.
  1.9.0 marks the reset visibly while staying inside the 1.x line.
- **Not CalVer:** pip and black use calendar versioning because their
  releases are time-driven and compatibility signalling matters less.
  Regula's users pin it in CI and read the version as a compatibility
  promise; discarding SemVer's signal would remove exactly the
  information a compliance tool's version exists to carry.
- **Skipping 1.8.0 is precedented and legal:** SemVer only requires
  monotonic increase; React jumped 0.14 to 15 and PHP jumped 5 to 7,
  both with documented rationale. The rationale here is this document.

## 7. Enforcement

`scripts/release_gate.py` runs in `release.yml` before build and
publish. It derives the minimum required bump from two independent
signals: conventional-commit subjects since the previous release tag
(feat requires minor; `!` or BREAKING CHANGE requires major) and the
target version's CHANGELOG section (Added/Deprecated require minor;
Removed requires major). The actual bump must be at least the stricter
signal; over-bumping is always allowed, under-bumping fails the release
before anything is built. Unit tests in `tests/test_release_gate.py`
pin the logic, including a regression test proving the gate would have
failed the misnumbered v1.7.10.

## 8. Criteria for a future 2.0.0

A MAJOR release happens only when a Section 2 surface breaks:
an Evidence Format revision without backward compatibility, removal of
a deprecated command or flag after its Section 4 window, an envelope
change, or exit-code renumbering. Feature accumulation alone never
justifies a MAJOR bump.

## Sources

- [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html):
  items 1 and 6-8, and the FAQ remediation rule for misnumbered releases.
- [PEP 440 / Version specifiers](https://packaging.python.org/specifications/version-specifiers/):
  numeric per-segment ordering.
- [Python Packaging User Guide, Versioning discussion](https://packaging.python.org/en/latest/discussions/versioning/):
  scheme choice is the maintainer's; SemVer vs CalVer trade-offs.
- [React versioning policy](https://react.dev/community/versioning-policy) and the
  [0.14 to 15 jump](https://www.infoq.com/news/2016/02/react-version-bumped-to-15);
  [PHP's missing 6](https://ma.ttias.be/php6-missing-version-number/): version-jump precedents.
- [Conventional Commits](https://www.conventionalcommits.org/en/about/):
  the commit-type to bump-level mapping the gate implements.
- [Kubernetes deprecation policy](https://kubernetes.io/docs/reference/using-api/deprecation-policy/) and
  [Salesforce CLI deprecation policy](https://developer.salesforce.com/docs/platform/salesforce-cli-reference/guide/cli_reference_deprecation.html):
  deprecation-window norms behind Section 4.
[exit 0]
```

Ended: `2026-08-05T00:17:17+01:00`

## Current project governance files

Started: `2026-08-05T00:18:44+01:00`

Command:

```console
$ bash -lc 'cat GOVERNANCE.md; printf '"'"'\n===== CODE OF CONDUCT =====\n'"'"'; cat CODE_OF_CONDUCT.md; printf '"'"'\n===== AI GOVERNANCE =====\n'"'"'; cat docs/AI_GOVERNANCE.md'
# Governance

This document exists because enterprise buyers and security reviewers ask
these questions before adopting a tool, and the honest answers are short.
It satisfies OSPS Baseline OSPS-GV-01.01 and OSPS-GV-01.02 (a documented
list of members with access to sensitive resources, and their roles).

## Who maintains Regula

**One person.** Kuziva Muzondo (`@kuzivaai`) is the sole maintainer and
holds every sensitive credential. This is verifiable rather than asserted:
every non-bot commit in the repository's history is his, which the
[contributor list](https://github.com/kuzivaai/getregula/graphs/contributors)
and `git log --format='%ae' | sort -u` both show.

| Resource | Holder | Notes |
|---|---|---|
| GitHub repository admin | `@kuzivaai` | Sole admin |
| PyPI project `regula-ai` | `@kuzivaai` | Published via GitHub Actions Trusted Publishing (OIDC), not a stored API token |
| Domain `getregula.com` | `@kuzivaai` | |
| Crash-reporting endpoint | none shipped | Published builds contain no endpoint; see `SECURITY.md` |

There are no other maintainers, no organisation, and no foundation — see
the [contributor list](https://github.com/kuzivaai/getregula/graphs/contributors)
above. Automated accounts (`dependabot`, `github-actions`) appear there but
hold no credentials and cannot approve or release.

## What that means for you — stated plainly

**Bus factor is one.** If the maintainer stops, releases stop. We are not
going to dress this up: it is the single largest adoption risk, and it is
the reason for the mitigations below rather than a reason to ignore it.

What limits the damage:

- **The code is open** under Apache-2.0 OR EUPL-1.2. Anyone can fork and
  continue. Detection rules are separately licensed
  (`LicenseRef-DRL-1.1`) — see `docs/LICENSE.Detection.Rules.md`.
- **Your data is local.** Regula runs on your machine and makes no network
  calls in its core scan. If the project were abandoned tomorrow, an
  installed copy keeps working, and nothing you scanned was ever held by
  us. There is no service to shut down and no account to lose.
- **Releases are verifiable without trusting us.** Published artefacts
  carry PyPI attestations (SLSA v1.0 Build Level 2) tying each file to the
  GitHub Actions workflow that built it.

What we cannot claim:

- **We are OSPS Baseline Level 1**, and structurally cannot reach Level 2,
  which requires at least two maintainers. Stated here so it is not
  discovered later.
- No third-party security audit or penetration test has been performed.
- There is no funded support contract or response-time guarantee. The
  security disclosure SLA in `SECURITY.md` is a good-faith commitment by
  one person, not an underwritten obligation.

## Decision-making

Decisions are made by the maintainer. Where a change affects a published
claim, the standard applied is in `.claude/rules/quality-standards.md` and
`docs/TRUST.md`: every number must be reproducible by a command a reader
can run, and a claim that cannot be verified is removed rather than
softened.

Two rules constrain the maintainer as much as contributors:

1. **Security alerts are never dismissed or suppressed** — not through the
   GitHub UI, not with inline suppression comments, not via scanner
   configuration, and not by rewriting correct code until a scanner goes
   quiet. If a finding is a false positive, it stays open with the
   reasoning recorded publicly.
2. **Corrections are published, not quietly patched.** When a claim in
   `docs/TRUST.md` or the README turns out to be wrong, it is corrected
   with a dated notice. See §8.2 of `docs/TRUST.md` for a worked example.

## Contributing

See `CONTRIBUTING.md`. Contributions are welcome and reviewed by the
maintainer. Because there is one maintainer, a contribution cannot receive
independent review by a second person — a limitation OSPS Baseline Level 3
would require us to fix, and which we cannot fix alone.

Non-code contribution is genuinely valuable here: regulatory content
currency, jurisdiction coverage, implementation guidance, and
documentation are the areas where the project is most constrained.

## Succession

There is no formal succession plan. If you depend on Regula commercially
and this matters to you, open an issue — a documented handover
arrangement is worth building with someone who needs it rather than
inventing in the abstract.

## Reporting security issues

See `SECURITY.md` in the repository root. Do not use public issues for
vulnerability reports.

===== CODE OF CONDUCT =====
# Code of Conduct

Regula is a small project. The rules are short.

## In short

Be honest. Be technical. Be kind. Disagreement is welcome; contempt is not.

## What is acceptable

- Constructive criticism of code, claims, benchmark methodology, or
  documentation. Pointing out a mistake is helpful — including pointing
  out a mistake by the maintainer.
- Asking questions even if they feel obvious. Compliance is hard and
  the people who need this tool are often not security or AI experts.
- Disagreeing with a design decision, with reasoning.
- Contributing patterns, framework mappings, or test cases for
  jurisdictions, languages, or domains the maintainer does not know
  well.

## What is not acceptable

- Personal attacks, harassment, or discrimination on any basis.
- Posting security vulnerabilities publicly without first using the
  private channels in [`SECURITY.md`](SECURITY.md). Coordinated
  disclosure protects users.
- Misrepresenting Regula's capabilities to a third party — e.g.
  claiming Regula provides legal compliance certification when it
  does not.
- Submitting AI-generated code or documentation without review and
  attribution. We are an EU AI Act tool; we hold ourselves to the
  same Article 14 transparency standard we ask others to.

## Reporting a problem

If something happens that should not have happened, email
`support@getregula.com` with `[CONDUCT]` in the subject line. The
maintainer will respond within 72 hours and will not retaliate against
the reporter. For issues involving the maintainer themselves, use the
GitHub Security Advisory channel and we will route it to a neutral
third party for review.

## Enforcement

The maintainer may, at their discretion:

- Edit, hide, or delete contributions that violate this code
- Block accounts that repeatedly violate it
- Refuse to merge a contribution from someone with an unresolved report

Severe or repeated violations result in a permanent ban from the
project's GitHub spaces.

## Attribution

This code of conduct is intentionally short. It draws on the
[Contributor Covenant](https://www.contributor-covenant.org/) and the
[Recurse Center social rules](https://www.recurse.com/manual#sub-sec-social-rules)
without copying either verbatim.

===== AI GOVERNANCE =====
# AI Governance — Regula Development Practices

This document describes how AI is used in the development of Regula, what oversight processes exist, and where AI-generated outputs carry risk.

Regula is a compliance tool combining code scanning with governance questionnaires. It should demonstrate the governance practices it advocates. To generate a governance scaffold for your own project, run `regula governance --project /path/to/project`.

---

## AI's Role in Development

Regula is maintained by a small team, at times one developer, with substantial AI assistance.

**What Claude generates:**

- Code — CLI commands, detection logic, test files, HTML/CSS for the website
- Detection patterns — regex patterns mapped to EU AI Act articles, reviewed and validated by the developer before merge
- Compliance framework cross-mappings — article-to-framework mappings in `references/framework_crosswalk.yaml`
- Documentation — README sections, blog posts, technical docs, this document
- Test cases — both unit tests and integration tests

**What Claude does not do:**

- Make final decisions about what ships — every commit is reviewed by the developer
- Access production systems or user data — Regula runs locally, there is no production backend
- Determine regulatory interpretation — article mappings reflect the regulation text, not Claude's legal opinion
- Replace the developer's judgement on risk classification accuracy

---

## Human Oversight Process

Every AI-generated output goes through the following before reaching `main`:

1. **Code review** — The developer reads every diff before committing. AI-generated code is not auto-merged.
2. **Test verification** — The repository verification commands run before a claim of completion; the current collected count is generated by `scripts/site_facts.py`.
3. **Claim auditor** — A CI pipeline (`scripts/claim_auditor.py`) scans all modified Markdown and HTML files for unverified numeric claims, superlatives, and competitive assertions. Unsourced claims fail the build.
4. **Site facts verification** — `scripts/site_facts.py` computes every numeric claim on the landing pages from the actual codebase. If a page claim drifts from the computed value, the discrepancy is visible.
5. **Benchmark validation** — Detection changes are tested against checked-in labelled and synthetic corpora. Results and limitations are published in [`docs/benchmarks/PRECISION_RECALL_2026_04.md`](benchmarks/PRECISION_RECALL_2026_04.md).

---

## Accountability

The human maintainer is responsible for approved project outputs, including AI-generated code, documentation, detection patterns, and compliance mappings.

"AI-assisted" does not mean "AI-decided." Every pattern classification, every article mapping, and every compliance claim was reviewed by a human before publication. If something is wrong, the responsibility lies with the developer who approved it, not with the model that generated it.

---

## Risk Assessment

AI-generated outputs in Regula carry specific risks. These are documented honestly, not minimised.

### Where AI-generated errors could cause harm

| Component | Risk if wrong | Mitigation |
|---|---|---|
| **Risk indication** | False confidence: a user treats a code indicator as a legal classification | Publish measured benchmark limitations; require deployment-context and human review. See [`benchmarks/README.md`](../benchmarks/README.md). |
| **Article mappings** (pattern → EU AI Act article) | Incorrect obligations: a user implements the wrong compliance measures | Cross-referenced against regulation text; framework crosswalk reviewed against primary sources (ISO 42001, NIST AI RMF, etc.) |
| **Effort estimates** (hours per article) | Under-estimation leads to missed deadlines or under-resourcing | Estimates are ranges, not point values; clearly labelled as indicative |
| **Prohibited-practice indicators** | False negative: relevant behavior is not flagged | Publish the current synthetic recall artefact and its limitations; do not generalize fixture results to real systems. See [`benchmarks/synthetic/RECALL.json`](../benchmarks/synthetic/RECALL.json). |
| **Documentation generation** (Annex IV) | Generated documentation accepted as-is without review, creating a false compliance record | Output clearly marks sections as "auto-generated — requires human review"; never claims to be complete |

### What Regula explicitly does NOT do

- Provide legal advice (disclaimed on every page and in CLI output)
- Determine whether a system IS high-risk (that depends on deployment context, not code alone)
- Replace a human compliance review
- Monitor running systems (static analysis only)
- Guarantee compliance (it identifies risk indicators for human review)

---

## Detection Pattern Curation Methodology

### How the initial pattern set was selected

The original curation covered 330 patterns — the `historical_330_bucket` computation in `scripts/site_facts.py` at the time: tiered risk regexes (279) + architecture detectors (38) + credential detectors (9) + oversight detectors (4). The same bucket computes 479 on the current codebase (419 + 38 + 18 + 4); regenerate with `python3 scripts/site_facts.py`. The selection methodology below applies to every pattern added since.

Pattern sources:

1. **EU AI Act regulation text** — Each prohibited and high-risk pattern maps to a specific article and paragraph. The mapping is documented in `scripts/risk_patterns.py` alongside each pattern group.
2. **OWASP Top 10 for LLMs** and **OWASP Agentic Security** — AI security patterns (prompt injection, unsafe deserialisation, unbounded token generation) map to published OWASP categories.
3. **Common coding patterns** — Patterns were derived from how developers actually implement the regulated behaviours (e.g., `model.predict(applicant)` for credit scoring, `face_recognition` imports for biometric processing).

### How patterns are validated

- **Synthetic corpus:** tests whether current fixtures are detected; it does not estimate real-world recall. Current results: [`benchmarks/synthetic/RECALL.json`](../benchmarks/synthetic/RECALL.json).
- **OSS corpus:** measures precision on checked-in labelled findings. Results and scope: [`benchmarks/README.md`](../benchmarks/README.md).

### How to interpret the library-corpus precision

The measured library-corpus result and its numerator, denominator, labelling limits, and reproduction steps are recorded in [`benchmarks/README.md`](../benchmarks/README.md).

This is honest but requires context:

- The low library-corpus result is dominated by INFO findings and does not establish performance on other corpora.
- The labelled library corpus does not provide a usable BLOCK-tier precision estimate.
- Tier slices are small and must not be generalized.
- **The OSS corpus is deliberately adversarial** — these are mature AI libraries, not AI applications. They import AI frameworks extensively but are not themselves regulated AI systems. High false-positive rates on these projects are expected.

The benchmark methodology and reproduction steps are published in `docs/benchmarks/PRECISION_RECALL_2026_04.md`. Every number can be independently verified by running `regula benchmark` against the labelled corpus checked into the repository.

---

## Transparency

This document is part of the project's public repository. It is versioned alongside the code it describes. If the development practices change, this document should be updated in the same commit.

The project's `CLAUDE.md` file contains operational instructions for Claude Code sessions, including honesty requirements, verification standards, and the rule that no statistic may be fabricated.

---

*Last updated: 10 April 2026. Commit: see git log.*
[exit 0]
```

Ended: `2026-08-05T00:18:44+01:00`

## Current inventories and research registers

Started: `2026-08-05T00:18:44+01:00`

Command:

```console
$ bash -lc 'rg --files | rg '"'"'PUBLIC|public.surface|RESEARCH_REGISTER|research.register|inventory'"'"' | sort; for f in docs/commercial/RESEARCH_REGISTER_2026-07-31.md data/public_surface_inventory.json docs/improvement/PUBLIC-SURFACE-DISCOVERY.md; do if test -f ""; then printf '"'"'\n===== %s =====\n'"'"' ""; cat ""; fi; done'
data/public_surface_policy.json
docs/commercial/PUBLIC_CLAIM_REGISTER_2026-07-31.md
docs/commercial/RESEARCH_REGISTER_2026-07-31.md
docs/improvement/PUBLIC-SURFACE-DISCOVERY.md
scripts/model_inventory.py
scripts/public_surface_inventory.py
tests/test_public_surface_inventory.py
tests/test_setop_inventory.py
[exit 0]
```

Ended: `2026-08-05T00:18:44+01:00`

## Mechanical commercial result verification

Started: `2026-08-05T00:18:44+01:00`

Command:

```console
$ bash -lc 'python3 /tmp/verify_regula_commercial.py; git cat-file -t 94efa9e6ad9173fb888822543c247195078b0220; git cat-file -t 5bd2112; sha256sum benchmarks/commercial_v1/PROTOCOL.md benchmarks/commercial_v1/results/raw/synthetic-score.json; rg -n '"'"'OVERALL_DECISION|PRODUCT_PILOT_STATUS|TECHNICAL_EVIDENCE|DEMAND_EVIDENCE'"'"' docs benchmarks data'
summary_sha256 fe985431a8dd9092f8c809aa1bd396dcf5e87c710b564cf691d54a72d49c7ba8
frozen_product_commit 94efa9e6ad9173fb888822543c247195078b0220
preregistration_commit 5bd2112
local A TP 0 FP 0 FN 40 TN 40 precision None recall 0.0 recall_wilson95 [0.0, 0.08762160119728664] precision_wilson95 None
local B TP 0 FP 0 FN 40 TN 40 precision None recall 0.0 recall_wilson95 [0.0, 0.08762160119728664] precision_wilson95 None
naive A TP 40 FP 4 FN 0 TN 36 precision 0.9090909090909091 recall 1.0 recall_wilson95 [0.9123783988027135, 1.0000000000000002] precision_wilson95 [0.7884076083340138, 0.9640778067726837]
Traceback (most recent call last):
  File "/tmp/verify_regula_commercial.py", line 30, in <module>
    assert row['wilson95'] == wilson(tp, tp + fn)
           ~~~^^^^^^^^^^^^
KeyError: 'wilson95'
commit
commit
58c935903b5832eb7b8232116f6dc182b97708a89b5d3070f8b856ec9272d8c4  benchmarks/commercial_v1/PROTOCOL.md
bd8191a1ec9f19bfc408fc770fd40409da091b6a218308ae0014200a6df20a3e  benchmarks/commercial_v1/results/raw/synthetic-score.json
docs/improvement/SESSION-LOG-2026-08-01-190000.md:70:`PRODUCT_PILOT_STATUS` remains NOT_APPROVED.
docs/improvement/HANDOVER-2026-08-01-203000.md:21:- `COMMERCIAL_V1_OVERALL_DECISION: STOP`
docs/improvement/HANDOVER-2026-08-01-203000.md:22:- `PRODUCT_PILOT_STATUS: NOT_APPROVED`
docs/improvement/HANDOVER.md:12:review. It records `OVERALL_DECISION: STOP`, not a pilot recommendation. Read
docs/improvement/HANDOVER-2026-08-01-120000.md:22:The latest implementation commits are `509eb52` (release identity erratum) and `4963152` (claim corrections). The commercial STOP decision and `PRODUCT_PILOT_STATUS: NOT_APPROVED` remain unchanged.
docs/commercial/RESEARCH_REGISTER_2026-07-31.md:40:| Is inventory/governance a real workflow? | [Public Contracts Scotland AI Register & Governance award notice](https://www.publiccontractsscotland.gov.uk/search/show/search_view.aspx?ID=JUL559622); [European Commission AI@EC](https://commission.europa.eu/publications/artificial-intelligence-european-commission-aiec-communication_en); [GOV.UK Holistic AI assurance case study](https://www.gov.uk/ai-assurance-techniques/holistic-ai-governance-risk-and-compliance-platform) | Official procurement/workflow material provides a `PROBLEM_SIGNAL`, not Regula fit, repeat demand or willingness to pay. Vendor-supplied case-study content is not independent effectiveness evidence. | Candidate A is the strongest workflow hypothesis, but `DEMAND_EVIDENCE` stays `UNVALIDATED`. |
docs/commercial/CLAIM_INTEGRITY_CORRECTION_2026-08-01.md:69:STOP and PRODUCT_PILOT_STATUS remains NOT_APPROVED.
docs/improvement/STATE.md:2054:Verdict: **TECHNICAL_EVIDENCE FAILED; COMPARATIVE_ADVANTAGE NOT_DEMONSTRATED;
docs/improvement/STATE.md:2056:FAIL; DEMAND_EVIDENCE UNVALIDATED; OVERALL_DECISION STOP.** The detailed
docs/commercial/COMMERCIAL_DEFENSIBILITY_REVIEW_2026-07-31.md:23:`OVERALL_DECISION: STOP`. No evaluated capability justifies a customer pilot.
docs/commercial/COMMERCIAL_DEFENSIBILITY_REVIEW_2026-07-31.md:34:| TECHNICAL_EVIDENCE | **FAILED** |
docs/commercial/COMMERCIAL_DEFENSIBILITY_REVIEW_2026-07-31.md:39:| DEMAND_EVIDENCE | **UNVALIDATED** |
docs/commercial/COMMERCIAL_DEFENSIBILITY_REVIEW_2026-07-31.md:40:| OVERALL_DECISION | **STOP** |
docs/improvement/SESSION-LOG-2026-08-01-120000.md:48:Candidate E (commercial validation): the repository still records commercial_v1 STOP and `PRODUCT_PILOT_STATUS: NOT_APPROVED`; no independent human labels, buyer interviews, design-partner access, or paid validation were added. Candidate E is the commercial binding constraint and cannot be closed by repository-only work.
docs/improvement/LEDGER.md:125:| **N60** | **The commercial-defensibility gate exposed a gap between a large green suite and claim-ready evidence.** Current PyPI is 1.7.4 while local source is 1.9.0; restricted verification fails one Git-worktree control, eight localhost timestamp tests and the home audit-path doctor check, while exact unrestricted controls pass; the merge blocker remains red; active public surfaces contradict the product's own legal limitations, regulatory status and security record. The first protocol draft also had tautological discovery, correlated samples presented as independent, unreachable comparators, non-equivalent outcome adapters and subjective gates. | 2026-07-31 to 2026-08-01 (commercial-defensibility session) | **EXECUTED; RESULT `STOP`.** Preregistered in `5bd2112`; pre-results verifier repair `84e0118`; post-result acquisition-blocker correction `056bcf2`, with the frozen exit-1 control retained. The corrected acquirer obtained 12/12 exact repositories and 12/12 licence records. Two fresh runs per synthetic tool were byte-identical after normalisation. Local 1.9.0: Candidate A TP 0, FP 0, FN 40, TN 40, recall **0/40**, descriptive Wilson 95% interval 0.000–0.0876; Candidate B identical. Transparent baseline A: TP 40, FP 4, FN 0, TN 36, precision **40/44**, recall **40/40**; baseline B: TP 40, FP 0, FN 0, TN 40, precision and recall **40/40**. These correlated constructed families are diagnostic, not external accuracy. Twelve-repository operations retained every outcome: local and public Regula each exited 0 on 9/12 and 1 on 3/12; their second-run stdout/stderr and exits matched 12/12. Two executable competitors exited 0 operationally on 12/12, but accuracy is UNTESTABLE without equivalent adapters or human repository labels. Candidate C remains MODEL-PROVISIONAL with 0/30 independently human-labelled scenarios. Local evidence-pack strict verification passed; public 1.7.4 strict verification failed exit 2 on its legacy manifest. Network behaviour remains UNVERIFIED because namespace denial was unavailable and the socket control broke `ssl` import before execution. Verdict: TECHNICAL_EVIDENCE FAILED; COMPARATIVE_ADVANTAGE NOT_DEMONSTRATED; PUBLIC_CLAIM_INTEGRITY FAIL; REGULATORY_CURRENCY PARTIAL; OPERATIONAL_READINESS FAIL; DEMAND_EVIDENCE UNVALIDATED; OVERALL_DECISION STOP. Final verification: custom runner 1,386/1,386 exit 0; pytest **2,633 passed, 6 failed, exit 1** because the 11 harness tests move live collection to 2,639 while public canonical claims remain 2,628; two of six fast gates fail on that mismatch, four pass; merge blocker remains exit 1; unrestricted doctor and self-test pass. The public-claim cascade is explicitly prohibited this session and no test was hidden to manufacture green. Results: `docs/commercial/COMMERCIAL_DEFENSIBILITY_REVIEW_2026-07-31.md` and `benchmarks/commercial_v1/results/summary.json`. Existing items **F25, F30, N35, N43, N50, N54, N53, N55, N57, N6, N7, N10, N11 and N12 were not closed by this bounded session and remain OPEN or PARTIALLY CLOSED exactly as their own rows state**; no absence from the review supersedes them. N43 and public-claim debt were independently corroborated. Exact next unit: correct the high-consequence public/PyPI claim classes in the dated register without changing benchmark results or detector rules, then independently label a future repository study before reconsidering a pilot. |
docs/improvement/LEDGER.md:527:status. commercial_v1 remains STOP and `PRODUCT_PILOT_STATUS` remains
docs/improvement/LEDGER.md:550:and `PRODUCT_PILOT_STATUS` remains NOT_APPROVED.
docs/improvement/LEDGER.md:573:`PRODUCT_PILOT_STATUS` remains NOT_APPROVED.
docs/improvement/LEDGER.md:596:`PRODUCT_PILOT_STATUS` remains NOT_APPROVED. Repository merge readiness remains
docs/improvement/HANDOVER-2026-08-01-190000.md:28:- `COMMERCIAL_V1_OVERALL_DECISION: STOP`
docs/improvement/HANDOVER-2026-08-01-190000.md:29:- `PRODUCT_PILOT_STATUS: NOT_APPROVED`
docs/improvement/SESSION-LOG-2026-08-01-203000.md:52:`COMMERCIAL_V1_OVERALL_DECISION: STOP`
docs/improvement/SESSION-LOG-2026-08-01-203000.md:54:`PRODUCT_PILOT_STATUS: NOT_APPROVED`
docs/improvement/SESSION-LOG-2026-08-03-110106.md:53:- `COMMERCIAL_V1_OVERALL_DECISION: STOP`
docs/improvement/SESSION-LOG-2026-08-03-110106.md:54:- `PRODUCT_PILOT_STATUS: NOT_APPROVED`
docs/improvement/HANDOVER-2026-08-03-110106.md:58:- `COMMERCIAL_V1_OVERALL_DECISION: STOP`
docs/improvement/HANDOVER-2026-08-03-110106.md:59:- `PRODUCT_PILOT_STATUS: NOT_APPROVED`
benchmarks/commercial_v1/results/summary.json:51:    "TECHNICAL_EVIDENCE": "FAILED",
benchmarks/commercial_v1/results/summary.json:56:    "DEMAND_EVIDENCE": "UNVALIDATED",
benchmarks/commercial_v1/results/summary.json:57:    "OVERALL_DECISION": "STOP"
docs/improvement/SESSION-LOG-VENTURE-2026-08-05-001618.md:178:| **N60** | **The commercial-defensibility gate exposed a gap between a large green suite and claim-ready evidence.** Current PyPI is 1.7.4 while local source is 1.9.0; restricted verification fails one Git-worktree control, eight localhost timestamp tests and the home audit-path doctor check, while exact unrestricted controls pass; the merge blocker remains red; active public surfaces contradict the product's own legal limitations, regulatory status and security record. The first protocol draft also had tautological discovery, correlated samples presented as independent, unreachable comparators, non-equivalent outcome adapters and subjective gates. | 2026-07-31 to 2026-08-01 (commercial-defensibility session) | **EXECUTED; RESULT `STOP`.** Preregistered in `5bd2112`; pre-results verifier repair `84e0118`; post-result acquisition-blocker correction `056bcf2`, with the frozen exit-1 control retained. The corrected acquirer obtained 12/12 exact repositories and 12/12 licence records. Two fresh runs per synthetic tool were byte-identical after normalisation. Local 1.9.0: Candidate A TP 0, FP 0, FN 40, TN 40, recall **0/40**, descriptive Wilson 95% interval 0.000–0.0876; Candidate B identical. Transparent baseline A: TP 40, FP 4, FN 0, TN 36, precision **40/44**, recall **40/40**; baseline B: TP 40, FP 0, FN 0, TN 40, precision and recall **40/40**. These correlated constructed families are diagnostic, not external accuracy. Twelve-repository operations retained every outcome: local and public Regula each exited 0 on 9/12 and 1 on 3/12; their second-run stdout/stderr and exits matched 12/12. Two executable competitors exited 0 operationally on 12/12, but accuracy is UNTESTABLE without equivalent adapters or human repository labels. Candidate C remains MODEL-PROVISIONAL with 0/30 independently human-labelled scenarios. Local evidence-pack strict verification passed; public 1.7.4 strict verification failed exit 2 on its legacy manifest. Network behaviour remains UNVERIFIED because namespace denial was unavailable and the socket control broke `ssl` import before execution. Verdict: TECHNICAL_EVIDENCE FAILED; COMPARATIVE_ADVANTAGE NOT_DEMONSTRATED; PUBLIC_CLAIM_INTEGRITY FAIL; REGULATORY_CURRENCY PARTIAL; OPERATIONAL_READINESS FAIL; DEMAND_EVIDENCE UNVALIDATED; OVERALL_DECISION STOP. Final verification: custom runner 1,386/1,386 exit 0; pytest **2,633 passed, 6 failed, exit 1** because the 11 harness tests move live collection to 2,639 while public canonical claims remain 2,628; two of six fast gates fail on that mismatch, four pass; merge blocker remains exit 1; unrestricted doctor and self-test pass. The public-claim cascade is explicitly prohibited this session and no test was hidden to manufacture green. Results: `docs/commercial/COMMERCIAL_DEFENSIBILITY_REVIEW_2026-07-31.md` and `benchmarks/commercial_v1/results/summary.json`. Existing items **F25, F30, N35, N43, N50, N54, N53, N55, N57, N6, N7, N10, N11 and N12 were not closed by this bounded session and remain OPEN or PARTIALLY CLOSED exactly as their own rows state**; no absence from the review supersedes them. N43 and public-claim debt were independently corroborated. Exact next unit: correct the high-consequence public/PyPI claim classes in the dated register without changing benchmark results or detector rules, then independently label a future repository study before reconsidering a pilot. |
docs/improvement/SESSION-LOG-VENTURE-2026-08-05-001618.md:580:status. commercial_v1 remains STOP and `PRODUCT_PILOT_STATUS` remains
docs/improvement/SESSION-LOG-VENTURE-2026-08-05-001618.md:603:and `PRODUCT_PILOT_STATUS` remains NOT_APPROVED.
docs/improvement/SESSION-LOG-VENTURE-2026-08-05-001618.md:626:`PRODUCT_PILOT_STATUS` remains NOT_APPROVED.
docs/improvement/SESSION-LOG-VENTURE-2026-08-05-001618.md:649:`PRODUCT_PILOT_STATUS` remains NOT_APPROVED. Repository merge readiness remains
docs/improvement/SESSION-LOG-VENTURE-2026-08-05-001618.md:1554:Verdict: **TECHNICAL_EVIDENCE FAILED; COMPARATIVE_ADVANTAGE NOT_DEMONSTRATED;
docs/improvement/SESSION-LOG-VENTURE-2026-08-05-001618.md:1556:FAIL; DEMAND_EVIDENCE UNVALIDATED; OVERALL_DECISION STOP.** The detailed
docs/improvement/SESSION-LOG-VENTURE-2026-08-05-001618.md:2439:`OVERALL_DECISION: STOP`. No evaluated capability justifies a customer pilot.
docs/improvement/SESSION-LOG-VENTURE-2026-08-05-001618.md:2450:| TECHNICAL_EVIDENCE | **FAILED** |
docs/improvement/SESSION-LOG-VENTURE-2026-08-05-001618.md:2455:| DEMAND_EVIDENCE | **UNVALIDATED** |
docs/improvement/SESSION-LOG-VENTURE-2026-08-05-001618.md:2456:| OVERALL_DECISION | **STOP** |
docs/improvement/SESSION-LOG-VENTURE-2026-08-05-001618.md:6380:    "TECHNICAL_EVIDENCE": "FAILED",
docs/improvement/SESSION-LOG-VENTURE-2026-08-05-001618.md:6385:    "DEMAND_EVIDENCE": "UNVALIDATED",
docs/improvement/SESSION-LOG-VENTURE-2026-08-05-001618.md:6386:    "OVERALL_DECISION": "STOP"
[exit 0]
```

Ended: `2026-08-05T00:18:45+01:00`

## Delivered Phuluso documents inspection

Started: `2026-08-05T00:18:44+01:00`

Command:

```console
$ bash -lc 'python3 - <<'"'"'PY'"'"'
from pathlib import Path
from docx import Document
base=Path('"'"'/mnt/c/Users/mkuzi/Downloads'"'"')
for name in ('"'"'Regula-Technical-and-Commercial-Dossier-for-Phuluso-2026-08-04-FINAL.docx'"'"','"'"'Regula-Responses-to-Phuluso-Questions-2026-08-04-FINAL.docx'"'"'):
 p=base/name
 print('"'"'FILE'"'"',p,'"'"'exists'"'"',p.exists(),'"'"'bytes'"'"',p.stat().st_size if p.exists() else None)
 if p.exists():
  d=Document(p)
  text='"'"'\n'"'"'.join(x.text for x in d.paragraphs)+'"'"'\n'"'"'+'"'"'\n'"'"'.join(c.text for t in d.tables for row in t.rows for c in row.cells)
  print(text)
PY'
FILE /mnt/c/Users/mkuzi/Downloads/Regula-Technical-and-Commercial-Dossier-for-Phuluso-2026-08-04-FINAL.docx exists True bytes 50602
REGULA
Technical and Commercial Dossier
A clear, evidence-bounded guide to the product, its limits and the proposed business


How to use this dossier
This is a working briefing, not a sales brochure. It is designed to let you explain Regula confidently without pretending the product or business has reached a stage it has not reached. Each section distinguishes what exists now, what the evidence shows, what is proposed, and what still needs human or market validation.

1. Executive briefing
What exists today
A published Regula 1.9.0 Python package and open-source repository.
A local command-line interface with 62 documented commands.
Code scanning across eight language families, with materially different analysis depth by language.
419 tiered risk-detection regular expressions on the public site. The broader internal inventory counts 722 patterns when other indicator, architecture, data-source, logging, oversight, credential and agentic categories are included. These counts answer different questions and must not be mixed.
Thirteen framework crosswalks, including the EU AI Act, NIST AI RMF, ISO/IEC 42001, ISO/IEC 27001, NIST CSF, SOC 2, OWASP and MITRE mappings.
Local reports, gap assessments, prioritised remediation suggestions, questionnaires, evidence scaffolds, audit records and CI-oriented formats such as SARIF.
A static public website and browser assessment interface. The web assessment runs in the browser. The CLI runs on the user’s machine.
A stdlib-only core, meaning the core Python package has no required third-party runtime dependencies. Optional features can add dependencies and network access.
What does not yet exist as a validated business
Paid tiers are not available. The public pricing page labels Starter and Professional as coming soon and says no payment is processed.
There is no demonstrated product-market fit, paid demand, completed design-partner study or independently validated enterprise buying case in the reviewed evidence.
The repository’s 31 July 2026 commercial review records OVERALL_DECISION: STOP and PRODUCT_PILOT_STATUS: NOT_APPROVED.
There is no SOC 2 Type II report and no third-party penetration test.
There is no basis to say the tool makes a product compliant, safe, scalable or acceptable to a bank, insurer or asset manager.
The proposed advisory layer, Pro tier and Business tier are hypotheses that need customer discovery, service design, delivery controls and evidence.

2. What problem Regula is trying to solve
AI regulation and enterprise governance create a translation problem. Developers work in code, tickets and build pipelines. Legal, risk and procurement teams work in duties, policies, evidence and approvals. A codebase can reveal some technical signals, such as an AI library, biometric processing, credit scoring logic, missing logging or credential exposure. It cannot reveal the full intended purpose, affected population, deployment setting, contractual allocation of responsibility or the truth of an organisation’s governance processes.
Regula’s proposed role is to make the first review more structured. It identifies code-observable indicators, asks for context that code cannot show, links the resulting evidence to relevant frameworks, and produces material that a competent human can review. Its value is not an automated legal verdict. Its value, if validated, is reducing the distance between technical facts and governance decisions.
3. How Regula works
A developer installs the regula-ai package or uses the repository version.
They point Regula at a local project folder, for example by running regula check .
The scanner reads eligible project files and looks for code-observable indicators.
The user can answer contextual questions about intended purpose, deployment and governance.
Regula groups and scores indicators, links them to provisions that may be relevant, and produces findings for review.
Other commands can produce gap assessments, remediation suggestions, inventories, documentation scaffolds, evidence packs and CI output.
A qualified person must confirm scope, classification, applicable duties, evidence quality and remediation decisions.
Analysis depth matters
Python receives the deepest analysis, including abstract syntax tree analysis and some cross-file data-flow and oversight checks. JavaScript and TypeScript can use optional tree-sitter support and otherwise fall back to shallower matching. Java, Go, Rust, C and C++ primarily use regular expressions and import or include detection. A claim that Regula analyses all eight language families equally would be false.
4. What Regula can and cannot tell a customer
5. Data handling and security
Does Regula store or upload a customer’s code?
The core CLI reads the selected source files locally and writes its outputs to the local filesystem. It does not require a Regula account or API key, and the documented core scan does not upload scanned files to a Regula service. That does not mean nothing is ever written. Reports, configuration, caches, audit logs or evidence packs requested by the user can be stored locally. Their retention is controlled by the user and the environment in which Regula runs.
Optional behaviour must be assessed separately. RFC 3161 timestamping contacts a timestamp authority. Bias tooling may download a dataset and talk to a locally hosted Ollama model. Telemetry requires explicit enablement and a configured Sentry endpoint. Update, feed and other integrations can use a network. GitHub Actions can upload SARIF to GitHub. The host platform, IDE, CI provider and optional dependencies have their own data-handling terms.
Does open source expose customer code?
No, not by itself. Open source means Regula’s own source code and detection logic are available for inspection under their licences. It does not publish the private code that a customer scans. A customer could still expose code through an unsafe CI configuration, public logs, an uploaded report, a compromised machine, a malicious package or fork, or a separately enabled integration. Open source improves inspectability but does not create a guarantee of security.
Security evidence and limits
The core has no required third-party runtime dependencies, which narrows one class of supply-chain risk but does not remove all security risk.
The project documents Bandit, Semgrep, pip-audit, CodeQL, regression tests and PyPI provenance attestations.
The security policy retains 42 dated open high-severity CodeQL alerts and explains their triage. A green workflow is not the same as zero alerts.
There is no third-party penetration test and no SOC 2 Type II report.
A compromised host, Python interpreter, package source, CI runner or privileged user remains outside what Regula can defend against.
An enterprise evaluation should pin a version and hash, verify package provenance, review optional network paths, inspect generated files and logs, use least privilege, and test in an isolated copy before scanning sensitive repositories.

6. Evidence quality and the hard commercial limit
The repository contains extensive automated tests. The site-facts record generated on 4 August 2026 lists 2,690 pytest-collected tests. Test volume is evidence of exercised behaviours, not proof that the product detects real-world regulatory issues accurately or creates customer value.
The most important contrary evidence is the commercial defensibility review dated 31 July 2026. In its frozen constructed evaluation, the local product missed 40 of 40 Candidate A positives and 40 of 40 Candidate B positives, while simple transparent baselines found 40 of 40 in each set. The review says the failure arose from a source-event adapter and product-output mismatch. The generated cases were correlated and were not a representative external accuracy sample, so the result does not prove that Regula always has zero recall. It does prove that the tested buyer-oriented jobs failed and prevents an honest claim of commercial readiness.
That same review had no independently human-labelled repositories, could not compare competitor accuracy, did not verify network behaviour at operating-system level, and found no demand evidence. Its controlling verdict remains STOP. Newer repository corrections and passing CI do not automatically overturn that separate commercial verdict.
Public wording is not fully consistent
The current PyPI page for regula-ai still contains stronger legacy wording. It says Regula classifies a system into one of four risk tiers, tells the user which obligations apply, and creates “no DPA required” and “no vendor data breach risk.” Those statements exceed the evidence boundary used in this dossier and conflict with the repository’s own commercial claim register. They should not be used as an approved sales script. The safer position is that Regula reports code-observable indicators and links them to provisions for contextual human and legal review. Data-processing and security duties must be assessed for the actual environment and optional features.

7. The credible commercial opportunity
The strongest proposed position is not “software that makes you compliant.” It is “a structured technical and advisory workflow that helps a small AI supplier prepare evidence, decisions and remediation work for enterprise diligence.” This remains a hypothesis until customers and buyers validate it.
Potential target customer
A plausible early customer is a small AI company with limited governance capacity that wants to sell into a regulated or risk-sensitive enterprise. The trigger could be a bank, insurer, asset manager or large corporate asking for security, privacy, model-risk, governance and regulatory evidence. The pain is not only understanding a regulation. It is knowing what evidence to prepare, who must own each action, what technical work is missing and how to respond consistently during procurement.
Why Phuluso’s consulting background could matter
Customer discovery with founders, technical leads, risk teams, procurement and regulated-industry buyers.
Translation of regulatory duties into operating-model questions, control owners, evidence requests and decision points.
Design of founder-friendly roadmaps that separate urgent fixes, evidence collection, legal decisions and longer-term governance.
Mapping requirements to governance processes, roles, committees, escalation paths and existing enterprise controls.
Improving content and UX so outputs tell a user what was observed, what is uncertain, who should review it and what the next action is.
Maintaining regulation and framework research through documented primary sources, review dates and change control.
Building partnerships and an interview programme without overstating what interview evidence proves.
Coding experience is not required for all of this. Technical changes, integrations and scanner rules still require engineering implementation and review. Regulatory interpretation requires competence and may require qualified legal advice. Phuluso should not be described as legal counsel unless she has the relevant professional qualification and engagement scope.
8. Product and service model, stated honestly
The current public pricing page shows Free, Starter and Professional, with Starter and Professional marked “Coming soon.” It explicitly says paid tiers are unavailable and no payment is processed. The Apple Notes labels “Pro” and “Business” should therefore be treated as workshop language, not current product names.
What “Monday morning” could mean in practice
A useful paid review would turn the scan and the team’s answers into a short working plan. For example:
09:00: confirm what the AI system does, who uses it, where it will operate and what decision it affects.
10:00: review each Regula finding with the technical lead. Mark it relevant, not relevant or unresolved, and record the reason.
11:00: list the evidence already available, such as model documentation, test results, logging records, data provenance, human-oversight procedures and supplier information.
12:00: identify missing evidence and decisions that need a lawyer, security reviewer, data-protection specialist, buyer or product owner.
14:00: assign an owner and due date to each agreed action. Separate launch blockers from improvements and open questions.
15:00: compare the evidence list with the specific enterprise buyer’s questionnaire or diligence request.
16:00: issue a short record of findings, rejected flags, unresolved questions, owners, dates and the next review point.
That is an example service workflow, not something the scanner completes automatically and not a guarantee of compliance, safety or buyer approval.
Copy that should be changed before external use
9. Contribution and governance model
More contributors can improve review quality, language coverage, maintenance capacity and resilience if contributions are governed. Contributor count alone does not create enterprise credibility. Poorly reviewed contributions can increase defects, regulatory drift and security risk.
A suitable contribution path for Phuluso
Own a customer and buyer interview protocol. Separate founder assumptions from direct evidence.
Maintain a source register for selected regulations and frameworks, using primary sources, effective dates and named reviewers.
Draft plain-language implementation guidance with a clear boundary between information and legal advice.
Create operating-model maps linking obligations to roles, processes, decisions and evidence.
Review reports and the website for comprehension, actionability, accessibility and consistency.
Run moderated usability sessions with representative users and record task success, errors, confusion and confidence.
Propose rule or product changes through issues and acceptance criteria. Engineering implements and tests technical changes.
Publish corrections and limitations with the same visibility as positive results.
Controls needed before multiple contributors
A written maintainer and decision-rights model.
Contributor licence and intellectual-property review, including the separate Detection Rule Licence.
Required peer review and CI checks for code, content and regulatory changes.
Primary-source citation, effective-date and locale-sync requirements.
Security reporting, release signing, versioning and rollback procedures.
Clear ownership of customer data, interview consent, confidentiality and research records.
No public contributor count or logos used as implied customer endorsement.
10. Ownership and working roles
A possible structure is for Phuluso to own and lead the company, commercial proposition, customer discovery, partnerships, operating model and advisory work, with Kuziva providing technical delivery as a contractor or CTO. The exact ownership, authority, payment and working arrangement should be written down clearly.
Ownership transfer checklist
Ownership transfer due diligence
Identify who currently owns copyright in every material code and content contribution.
Review the Apache 2.0, EUPL 1.2 and Detection Rule Licence structure and what can actually be assigned.
Inventory the GitHub organisation or repository, PyPI publisher access, domain, website hosting, email, trademarks, social accounts, signing keys and customer or research data.
Use a written assignment or licence, founder agreement, share terms, contractor agreement, confidentiality terms and decision rights prepared or reviewed professionally.
Record pre-existing intellectual property, licence obligations and future contribution ownership.
Agree how each person’s past and future contribution will be described in company, customer and application materials.
Innovator Founder route
The UK route is called the Innovator Founder visa. The current rules require an endorsed business plan, a day-to-day role and an innovative, viable and scalable venture. Phuluso’s proposed role could include ownership, commercial leadership, customer research, service design and operational development. A regulated immigration adviser should advise on the application and each person’s permitted work. This dossier does not assess visa eligibility.
11. A responsible 90-day validation plan
Days 1 to 15: establish truth and boundaries
Agree the proposed ownership, decision rights and working roles, then have the legal and immigration details reviewed professionally.
Create an intellectual-property and account inventory.
Agree an honest one-sentence proposition and a prohibited-claims list.
Select one customer segment and one buyer use case. Do not begin with banks, insurers and asset managers as if they were identical.
Create an interview protocol, consent wording and evidence register.
Days 16 to 45: discovery, not selling certainty
Interview at least 10 relevant AI suppliers and at least 5 people involved in enterprise buying or assurance. These are discovery targets, not statistical proof.
Ask for recent evidence requests, rejected deals, review delays, documents requested and who made the decision.
Test a real report workflow with representative users. Measure task completion and comprehension, not whether they say the idea sounds good.
Have technical and legal reviewers inspect outputs from known projects and record false positives, false negatives and unsafe interpretations.
Resolve or re-evaluate the commercial benchmark failures before offering a customer pilot.
Days 46 to 90: bounded service prototype
Design one manual, bounded “enterprise evidence readiness” service around a named buyer process.
State deliverables, exclusions, data handling, reviewer roles and acceptance criteria.
Run an unpaid or paid design-partner study only after the internal pilot gate is approved. Do not call ordinary feedback a successful pilot.
Measure time to complete, findings accepted or rejected by reviewers, missing evidence identified, remediation completed and buyer feedback.
Decide whether the repeatable value belongs in software, consulting, templates, training or a combination. Do not assume a SaaS platform is necessary.
Evidence needed before stronger claims
Independent human labels on representative repositories and use cases.
Version-bounded precision and recall for the exact jobs being sold.
Resolved source-event and output mismatch demonstrated in the commercial review.
Representative usability evidence, including accessibility and failure-path testing.
Security review for the actual delivery architecture, especially if any hosted service is introduced.
Buyer interviews and design-partner evidence showing the problem, workflow and willingness to pay.
A delivery process that another trained person can repeat with consistent evidence boundaries.
Professional review of contracts, data protection, professional liability and regulatory claims.
12. Conversation guide for Phuluso
A 30-second introduction
“Regula is an open-source tool that helps teams inspect code for AI governance indicators and organise the evidence a human reviewer needs. It runs locally for the core scan, so the scanned source files are not uploaded to a Regula service. It does not certify compliance or replace legal review. We are exploring whether a guided evidence-readiness service can help smaller AI suppliers respond to enterprise due diligence more clearly and efficiently.”
Questions to ask a founder
Tell me about the last enterprise security or governance questionnaire you received.
Which questions took longest, and which evidence did you not already have?
Who inside your team owned the answers?
Did the buyer reject, delay or condition the deal? What reason did they give?
Which part would you trust software to prepare, and which part needs a human reviewer?
What would make an evidence pack credible to you and to the buyer?
What information could never leave your environment?
What outcome would justify paying, and who controls that budget?
Questions to ask an enterprise buyer
What evidence do you request from a small AI supplier before technical evaluation or procurement?
Which evidence is mandatory, risk-based or negotiable?
Who can accept residual risk and what triggers escalation?
Which failures most often delay or stop a purchase?
Would a machine-generated report help, and what independent verification would you require?
How do requirements change by use case, data type, geography and materiality?
What would make this output unusable or unsafe?
Statements to refuse
“Regula guarantees compliance.”
“The scan proves your EU AI Act risk class.”
“Your code can never be exposed.”
“It is enterprise-ready because it is open source.”
“It will get an Innovator Founder endorsement.”
“The paid product already exists.”
“Banks require exactly this pack.”
“Passing 2,690 tests proves real-world accuracy.”
13. Glossary
Primary and repository sources
URLs are written out so they remain usable when this file is copied, printed or converted to PDF.
Regula repository README: https://github.com/kuzivaai/getregula/blob/main/README.md
Regula security policy: https://github.com/kuzivaai/getregula/blob/main/SECURITY.md
Regula trust pack: https://github.com/kuzivaai/getregula/blob/main/docs/TRUST.md
Regula architecture: https://github.com/kuzivaai/getregula/blob/main/docs/architecture.md
Regula commercial defensibility review, 31 July 2026: https://github.com/kuzivaai/getregula/blob/main/docs/commercial/COMMERCIAL_DEFENSIBILITY_REVIEW_2026-07-31.md
Regula pricing page: https://getregula.com/pricing.html
UK Immigration Rules, Appendix Innovator Founder: https://www.gov.uk/guidance/immigration-rules/immigration-rules-appendix-innovator-founder
GOV.UK Innovator Founder overview: https://www.gov.uk/innovator-founder-visa
GOV.UK Innovator Founder eligibility: https://www.gov.uk/innovator-founder-visa/eligibility
Authorised endorsing bodies, updated 20 April 2026: https://www.gov.uk/government/publications/endorsing-bodies-innovator-founder-and-scale-up-visas/innovator-founder-and-scale-up-visas-endorsing-bodies
Prepared for
Phuluso (PK)
Evidence date
4 August 2026
Product version reviewed
Regula 1.9.0, repository commit a62e8aa6af99e77a49793c7bea398d8c1da171d4
Purpose
Understanding, discussion and customer discovery. Not legal, security, investment or immigration advice.
The shortest accurate description
Regula is a free, open-source command-line tool that scans source code locally for technical indicators that may require AI governance review. It combines those findings with questions about the system context, maps them to potentially relevant regulatory and governance provisions, and generates evidence scaffolds for a human reviewer. It does not determine legal classification, prove compliance, replace a lawyer or auditor, or guarantee that a system is safe or enterprise-ready.
Bottom line
There is enough real product here to support serious discovery conversations. There is not enough evidence to sell certainty. The honest opportunity is to turn a technically useful open-source tool into a well-governed evidence and advisory workflow, then test whether buyers will pay for it.
Technical meaning
Plain-language meaning
Static code analysis
The tool reads files without running the product and looks for structures or patterns that may matter.
Risk indicator
A clue that deserves review. It is not proof that the law applies or that something is wrong.
Governance questionnaire
Questions a person answers about purpose, users, deployment and controls because those facts are not reliably visible in code.
Framework crosswalk
A map showing how one finding may relate to several standards or regulatory provisions. A map is not certification.
Evidence scaffold
A structured starting document with fields for evidence and reviewer decisions. It is not completed evidence merely because the file exists.
SARIF
A standard file format that lets code-scanning results appear in development tools such as GitHub security views.
CLI
A command-line interface. A developer types commands in a terminal instead of clicking through a hosted application.
Local processing
The core scan happens on the user’s own computer or build environment rather than uploading source code to a Regula cloud service.
Reasonable claim
Why it is bounded
Claim to avoid
It can surface technical indicators for human review.
Indicators can be false positives or miss relevant behaviour.
It finds every AI risk.
It can map findings to provisions that may be relevant.
Applicability depends on role, purpose, context and legal interpretation.
It tells you exactly which laws and obligations apply.
It can generate a remediation plan.
The plan is generated from observed findings and templates. It needs prioritisation by the organisation.
It tells you everything to do on Monday morning.
It can create evidence scaffolds.
Blank or self-reported fields are not verified evidence.
It produces an audit-ready compliance pack automatically.
It can support enterprise preparation.
Each buyer has its own diligence, security, privacy, model-risk and procurement requirements.
It makes a product enterprise-safe or guarantees a sale.
It can help teams start structured governance work.
Human review, legal analysis and operational controls remain necessary.
It certifies EU AI Act or WCAG compliance.
Safe answer to a customer
The core scanner is designed to run locally without uploading scanned source files. It can create local outputs, and optional features or the surrounding platform may use a network. Open source does not make the customer’s code public, but it also does not make the tool risk-free. We should complete the customer’s security review for the exact version, configuration and environment.
What passing tests prove
They prove that the tested implementation behaves as the tests specify in the tested environments. They do not prove legal accuracy, external validity, security certification, product-market fit, usability, enterprise acceptance or successful customer outcomes.
Layer
Honest user question
Possible offer
Current status
Free
What technical and governance indicators should we review?
Local scan, contextual questionnaire, mappings and evidence scaffolds.
Exists. Free CLI is available.
Guided review
What do these findings mean in our actual context, and what should we verify next?
Facilitated review, evidence inventory and prioritised action workshop.
Proposed service. Not validated or publicly purchasable.
Enterprise readiness
What evidence and remediation work should we prepare for this buyer’s diligence?
Buyer-specific readiness assessment, owners, dependencies and decision log.
Commercial hypothesis. Requires discovery, legal boundaries and delivery method.
Portfolio governance
How do we track review status and evidence across products and teams?
Inventory, control ownership, review cadence, evidence status and reporting.
Product hypothesis. No validated Business platform is evidenced.
Overbroad wording
Evidence-bounded alternative
Avoid: “Can I build this safely?”
Use: “What technical and governance indicators should I review while building?”
Avoid: “Can I launch this confidently?”
Use: “What known issues, missing evidence and decisions should I address before launch?”
Avoid: “Can I sell this to enterprise customers?”
Use: “What evidence and remediation work should I prepare for enterprise diligence?”
Avoid: “What makes my product enterprise-safe?”
Use: “What does this specific buyer require, what evidence do we have, and what gaps remain?”
Avoid: “Compliance roadmap” as a guaranteed outcome
Use: “Evidence and implementation roadmap for human and legal review.”
Term
Plain-language definition
AI governance
The roles, rules, evidence and decisions used to develop and operate AI responsibly.
Enterprise diligence
The checks a larger organisation performs before buying or approving a product.
False positive
The tool flags something that a reviewer decides is not relevant.
False negative
The tool misses something that should have been surfaced.
Precision
Of the items flagged, the proportion that are truly relevant under the chosen definition.
Recall
Of all relevant items in the test set, the proportion the tool found.
Provenance
Evidence of where software, data or a document came from and whether it was altered.
Static site
A website served as files without a server application processing customer data behind each page.
Product-market fit
Evidence that a defined group repeatedly values and pays for a product. It is not established by an idea or a small number of compliments.
Pilot
A controlled real-world evaluation with agreed users, scope, success criteria and evidence. It is not merely a demo.
FILE /mnt/c/Users/mkuzi/Downloads/Regula-Responses-to-Phuluso-Questions-2026-08-04-FINAL.docx exists True bytes 44431
REGULA
Responses to Phuluso’s Questions
Copy-ready answers in Kuziva’s direct, evidence-bounded tone


PK, I have answered each point directly below. I have separated what Regula actually does today from what I think we could build around it. I do not want to sell you a story that the evidence does not support.
1. Does it store my code or any data that I share?
Short answer: the core scan reads the code locally and does not upload the scanned files to a Regula service. It does write outputs locally when you ask it to, such as reports, configuration, audit logs or evidence packs. Those files stay in the environment where you run it unless you or another tool move them elsewhere.

I need to qualify that answer. Some optional features can use a network. Timestamping contacts a timestamp authority. Bias tooling can download a dataset and communicate with a local Ollama model. Telemetry only works if somebody explicitly enables it and configures an endpoint. GitHub Actions can upload SARIF results to GitHub. The laptop, cloud development environment, CI provider, IDE and optional integrations also have their own data policies.

So the accurate answer is not “Regula never stores or transmits any data.” It is: “The core scanner processes selected files locally and does not upload them to Regula. It can create local outputs, and optional features or the surrounding platform need their own data review.”
2. Is it secure? If it is open source, can somebody steal my code?
Open source means Regula’s own code and detection rules can be inspected. It does not mean the private code being scanned becomes public. Running an open-source scanner locally does not give other contributors access to the customer’s repository.

I still would not answer “yes, it is secure” without qualification. No software is risk-free. Code could be exposed through a compromised laptop, a malicious package or fork, unsafe CI logs, a report uploaded to the wrong place, excessive filesystem permissions, or an optional integration. Regula reduces some risk because the core has no required third-party runtime dependencies and does not need a hosted Regula account, but that is not a security guarantee.

The project publishes a security policy, automated security checks and package provenance information. It also records that there has been no third-party penetration test, no SOC 2 Type II audit, and a dated inventory of 42 open high-severity CodeQL alerts. Before an enterprise runs it on sensitive code, we should review the exact version, package hash, configuration, environment, permissions, outputs and network-enabled options.
3. Is the idea to get other contributors to increase enterprise credibility?
Partly, but contributor count is not the objective and it would be misleading to use it as a credibility badge. Good contributors can improve review quality, language coverage, regulatory maintenance, documentation and resilience if the work is governed properly. More unmanaged contributors can also create defects, inconsistent interpretations and security risk.

Enterprise credibility would come from transparent governance, named maintainers, primary-source regulatory work, peer review, reproducible tests, package provenance, an honest security posture, independent evaluation and evidence from real buyer workflows. Ten contributors with weak controls would be less credible than two accountable contributors with strong review and evidence.

So I would say the goal is to build a competent, governed contributor base. Increased credibility should be an outcome of the quality of that work, not the number of names on GitHub.
4. As a second contributor with no coding experience, where could I add value?
I think your strongest value is in the second group you listed: translating obligations into practical guidance, designing founder-friendly roadmaps, mapping requirements to governance processes and operating models, and improving the UX so the output is actionable. That fits your management consulting background and addresses a real gap between technical findings and organisational decisions.

You could also lead structured research on new regulations, frameworks, language needs and industry-specific requirements. The important boundary is that regulatory content needs primary sources, dates, review and, where necessary, legal input. Integrations and scanner rules need an engineer to implement and test them. Language support needs a fluent reviewer and technical parity checks, not just translation.

Your role could include ownership of the company and commercial proposition, customer discovery, buyer interviews, service design, operating-model mapping, evidence requirements, content design, usability testing, partnership development and regulatory change governance. I could support the technical product and implementation as the CTO or contractor, subject to the agreed structure and working permissions.
5. Could the target be small AI start-ups that want to sell to enterprise clients?
Yes, that is a plausible customer hypothesis. It is not yet a validated target market. A small AI supplier can be delayed by security, privacy, model-risk, governance and procurement questions from a larger buyer. There may be value in helping that supplier organise evidence, assign owners and close gaps before or during diligence.

Banks, insurers and asset managers are not one buyer type with one standard checklist. Requirements vary by jurisdiction, use case, data, materiality, outsourcing model, buyer policy and the people approving the risk. Your expertise could be valuable in finding out what a specific buyer actually expects and translating that into a practical operating plan.

Before we claim this is the market, we need interviews with both sides: small AI suppliers and the people who assess them. We need examples of real questionnaires, delayed deals, rejected evidence and purchasing decisions. Compliments about the idea are not enough. We need evidence of a repeated problem and willingness to pay.
6. Could the scan be free and the paid service be a compliance roadmap?
That is a sensible model to test, with one wording change. I would not sell a “compliance roadmap” if that suggests we have decided the law applies or guaranteed compliance. I would call it an evidence and implementation roadmap for human and legal review.

The free CLI already scans code, asks contextual questions and creates reports and scaffolds. The paid value would need to be more than reformatting free output. It could be a facilitated review that explains what was observed, what cannot be determined from code, what evidence is missing, who should own each action, which decisions require legal or buyer input, and what sequence is practical.

A Monday-morning output could say:

09:00: confirm the system’s purpose, users, deployment and affected decisions.
10:00: review every scanner finding with the technical lead and mark it relevant, not relevant or unresolved.
11:00: collect the evidence already held, including model documentation, test results, logs, data provenance, human-oversight procedures and supplier information.
12:00: list missing evidence and questions requiring legal, security, privacy, buyer or product-owner input.
14:00: assign an owner and due date to each action, separating blockers from improvements and open questions.
15:00: compare the evidence against the actual enterprise buyer’s diligence request.
16:00: issue a short record of decisions, owners, dates and the next review point.

That would be a facilitated service workflow. The scanner does not complete all of those steps itself, and the resulting plan would not guarantee compliance, safety or buyer approval.
7. Does this create a natural upgrade path?
Potentially, but the paid layers are proposals, not products we can say are available or proven. The current public page says the paid Starter and Professional tiers are coming soon and that no payment is processed. The repository’s commercial review also records STOP and says a customer pilot is not approved. I do not want us to skip over that.

I would reframe the pathway like this:

Free: “What technical and governance indicators should we review?”
Guided review: “What do these findings mean in our context, and what evidence or decisions are missing?”
Enterprise readiness: “What evidence and remediation work should we prepare for this specific buyer’s diligence?”
Portfolio governance: “How do we track evidence, owners, review status and change across products and teams?”

That sequence moves from observation to interpretation, preparation and ongoing governance. It is more defensible than “Can I build safely?”, “Can I launch confidently?” or “Can I sell to enterprise?”, because the tool cannot guarantee safety, confidence or a sale. We would validate each layer before naming, pricing or building it.
8. What is the honest current commercial position?
Regula is a real open-source product with a published package, a substantial command surface, local scanning, governance workflows and extensive automated tests. That gives us something concrete to put in front of people.

It is not yet an approved commercial pilot or a validated paid business. The most relevant repository review found serious failures in two constructed buyer-oriented detection jobs, no independent human-labelled repository evaluation, no reliable competitor accuracy comparison and no demand evidence. Its verdict was STOP. Passing engineering tests and updating the website do not automatically overturn that verdict.

There is also a public wording inconsistency we should not hide. The current PyPI description still says Regula classifies a system into a legal risk tier, tells the user which obligations apply, and creates “no DPA required” and “no vendor data breach risk.” The repository’s own claim register treats that boundary as untested or legally reviewable. I would not repeat those PyPI statements. The safer explanation is that Regula surfaces indicators and links them to provisions for contextual human and legal review.

My honest position is that we can start disciplined customer discovery and improve the product against real evidence. We should not yet present paid tiers as operational, imply enterprise acceptance, or use the visa objective as evidence that the business is innovative or viable.
9. Could Regula support an Innovator Founder visa application?
It could form part of the business case. The correct route is the UK Innovator Founder visa. The proposal would be for you to own and lead the company, commercial direction, customer research, partnerships, advisory model and operating development. I would support the technical product and implementation as CTO or contractor.

The application would still need an approved endorsing body to assess the business plan and whether the venture is innovative, viable and scalable. We should have an immigration adviser confirm how the ownership transfer, your role and my working arrangement should be documented. The application itself should be prepared around the actual company structure, responsibilities and work carried out.
10. What would I propose we do next?
First, we agree the ownership, decision rights and working roles. Second, we document the intellectual property, licences and accounts needed for the transfer. Third, we choose one narrow customer and buyer use case. Fourth, you lead the interviews, commercial proposition and operating-model work while I support the technical explanation and product implementation. Fifth, we test the output with real users and qualified reviewers, including the known failure paths. We can then decide whether there is enough evidence for a bounded pilot.

An immigration adviser and solicitor can deal with the application wording, transfer documents and working permissions alongside that work.
Copy-ready short answers
Primary and repository sources
URLs are written out so they remain usable when this file is copied, printed or converted to PDF.
Regula repository README: https://github.com/kuzivaai/getregula/blob/main/README.md
Regula security policy: https://github.com/kuzivaai/getregula/blob/main/SECURITY.md
Regula trust pack: https://github.com/kuzivaai/getregula/blob/main/docs/TRUST.md
Regula architecture: https://github.com/kuzivaai/getregula/blob/main/docs/architecture.md
Regula commercial defensibility review, 31 July 2026: https://github.com/kuzivaai/getregula/blob/main/docs/commercial/COMMERCIAL_DEFENSIBILITY_REVIEW_2026-07-31.md
Regula pricing page: https://getregula.com/pricing.html
UK Immigration Rules, Appendix Innovator Founder: https://www.gov.uk/guidance/immigration-rules/immigration-rules-appendix-innovator-founder
GOV.UK Innovator Founder overview: https://www.gov.uk/innovator-founder-visa
GOV.UK Innovator Founder eligibility: https://www.gov.uk/innovator-founder-visa/eligibility
Authorised endorsing bodies, updated 20 April 2026: https://www.gov.uk/government/publications/endorsing-bodies-innovator-founder-and-scale-up-visas/innovator-founder-and-scale-up-visas-endorsing-bodies
Prepared for
Kuziva Muzondo
Evidence date
4 August 2026
Product version reviewed
Regula 1.9.0, repository commit a62e8aa6af99e77a49793c7bea398d8c1da171d4
Purpose
Understanding, discussion and customer discovery. Not legal, security, investment or immigration advice.
Question
Short answer
Does it upload code?
The core scanner processes selected files locally and does not upload them to Regula. It can create local outputs, and optional features or the surrounding platform need separate review.
Is it secure?
It has a relatively narrow core attack surface and transparent controls, but no software is risk-free. It has not had a third-party penetration test or SOC 2 Type II audit.
Does open source expose customer code?
No. Open source exposes Regula’s code, not the private repository being scanned. Operational mistakes or compromised environments can still expose data.
Can it prove compliance?
No. It surfaces indicators and organises evidence for qualified human review.
Are paid tiers live?
No. The current pricing page marks them as coming soon and no payments are processed.
Is there validated demand?
Not yet. The repository records demand as unvalidated and the pilot as not approved.
Can it support a visa case?
It may be part of a genuine venture, but only an authorised endorsing body and the Home Office process can determine the route requirements. Ownership alone is insufficient.
[exit 0]
```

Ended: `2026-08-05T00:18:45+01:00`

## Corrected standalone commercial result verification

Started: `2026-08-05T00:19:10+01:00`

Command:

```console
$ python3 /tmp/verify_regula_commercial.py
summary_sha256 fe985431a8dd9092f8c809aa1bd396dcf5e87c710b564cf691d54a72d49c7ba8
frozen_product_commit 94efa9e6ad9173fb888822543c247195078b0220
preregistration_commit 5bd2112
local A TP 0 FP 0 FN 40 TN 40 precision None recall 0.0 recall_wilson95 [0.0, 0.08762160119728664] precision_wilson95 None
local B TP 0 FP 0 FN 40 TN 40 precision None recall 0.0 recall_wilson95 [0.0, 0.08762160119728664] precision_wilson95 None
naive A TP 40 FP 4 FN 0 TN 36 precision 0.9090909090909091 recall 1.0 recall_wilson95 [0.9123783988027135, 1.0000000000000002] precision_wilson95 [0.7884076083340138, 0.9640778067726837]
naive B TP 40 FP 0 FN 0 TN 40 precision 1.0 recall 1.0 recall_wilson95 [0.9123783988027135, 1.0000000000000002] precision_wilson95 [0.9123783988027135, 1.0000000000000002]
human_labelled_repositories 0
accuracy_comparison UNTESTABLE: no independent repository labels or equivalent source-event adapters
network UNVERIFIED: namespace denial unavailable and frozen socket-denial probe breaks ssl import before command execution
verdict {"COMPARATIVE_ADVANTAGE": "NOT_DEMONSTRATED", "DEMAND_EVIDENCE": "UNVALIDATED", "OPERATIONAL_READINESS": "FAIL", "OVERALL_DECISION": "STOP", "PUBLIC_CLAIM_INTEGRITY": "FAIL", "REGULATORY_CURRENCY": "PARTIAL", "TECHNICAL_EVIDENCE": "FAILED"}
[exit 0]
```

Ended: `2026-08-05T00:19:10+01:00`
## Work package 2 and 3 retained synthesis

Completed: 2026-08-05 Europe/London.

Three read-only research tracks examined market and buyer workflows, competitors
and substitutes, and technology, standards, theory and official Innovator
Founder rules. Evidence was normalised into
`docs/venture/REGULA_VENTURE_SOURCE_REGISTER_2026-08-04.md` and 23 claims in
`docs/venture/REGULA_VENTURE_EVIDENCE_MATRIX_2026-08-04.json`.

The first draft selected `SERVICE_FIRST` as a validation vehicle. Independent
commercial falsification showed that this confused a research method with a
supported venture model, selected an unsupported and over-broad insurer
beachhead, understated reviewer dependency, used inconsistent delivery economics
and sequenced assisted delivery before technical validation. The technology
review found overstatement of what signing establishes and mixed primary
specification facts with reasoned defensibility conclusions.

All material findings were accepted. The decision changed to `STOP`. There is no
recommended paid offer and no commercially selected beachhead. One narrow
claims-triage insurer-onboarding transaction remains only a discovery hypothesis.
Gross-margin percentages were removed. Founder roles were made voluntary,
prospective and conditional on work actually performed. Regula output must remain
blinded and non-decision-bearing in any manual study until technical and pilot
gates pass.

Final verdict fields:

```text
CUSTOMER_PROBLEM_EVIDENCE: MODERATE
WILLINGNESS_TO_PAY: UNVALIDATED
TECHNICAL_FIT: FAILED
DIFFERENTIATION: NOT_DEMONSTRATED
VIABILITY: WEAK
SCALABILITY: WEAK
INNOVATOR_FOUNDER_EVIDENCE: CURRENTLY_WEAK
VENTURE_DECISION: STOP
```

No product, detector, scanner, benchmark, threshold, public claim, package
version, website, pricing, founder record, legal document or release
configuration was changed. No external contact, spending, publication,
deployment or submission occurred.
