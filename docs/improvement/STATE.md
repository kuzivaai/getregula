# Improvement Programme — STATE

> **HANDOVER POINTER.** The fuller narrative handover is
> `docs/improvement/HANDOVER.md`. **It is now tracked** (relocated from
> `.claude/regula-handover.md` on 28 Jul 2026, owner decision 1), so the
> old warning that it would not survive a `git clean` no longer applies.
> **This file remains the resume file and the tracked source of truth for
> programme state**; the handover carries the narrative. Also now tracked
> alongside them: `PHASE0_VERIFICATION.md`, `OWNER_ACTIONS.md`,
> `COMMIT_ERRATA.md`, and `docs/dpvcg-contribution-draft.md`.

Resume file. A fresh session reads PROGRAMME.md then this, and continues
from "NEXT". Checkpointed after every phase and every ~20 significant
actions.

- **Branch:** `improvement/2026-08-programme` (created from `main`, 27 Jul 2026)
- **Programme started:** 27 July 2026
- **Last checkpoint:** 27 July 2026 — session 1, Phase 0 starting

## Session-protocol findings (session 1)

- `docs/improvement/STATE.md` did not exist -> first session. PROGRAMME.md
  written verbatim; branch created; prior uncommitted work carried onto
  the branch and committed so BASELINE anchors to a SHA.
- **There is no repo-root `CLAUDE.md`.** Project rules live in
  `.claude/rules/` (python-scripts, quality-standards, regulatory-content,
  site-html, tests) and are injected automatically. Read and in force.
- **Commands** (`.claude/commands/`): add-command, add-pattern, verify.
- **Skills** (`.claude/skills/`): discovering-test-gaps, gsc,
  hoisting-regex-compiles, regula, regulatory-context, releasing-regula.
- **`docs/research/` does NOT exist.** Per Phase 2 this is stated, not
  guessed. The seed corpus exists elsewhere and is richer than the
  prompt assumes. **Locations updated 28 Jul 2026 after the relocation:**
  the owner sweep is now `getregula-internal/research-sweep-2026-07.md`,
  held **outside the repository** because it is commercial strategy and
  this repo is public (see HANDOVER §12); its primary-source verification
  is now tracked at `docs/improvement/PHASE0_VERIFICATION.md`, with only
  its competitive-intelligence section redacted. Phase 2 will build
  validation cards on top of the already-verified set rather than
  re-verifying from zero, and will state which cards inherit prior
  verification vs which are new. **Note for Phase 2: the RESEARCH
  VALIDATOR subagent gets the cards only, so the internal sweep's location
  does not obstruct it.**

## DONE

- Session protocol executed (checks above).
- `docs/improvement/PROGRAMME.md` written verbatim.
- Branch `improvement/2026-08-programme` created from `main`.
- Prior 27 Jul moat work committed at **`d4180e3`** — BASELINE anchors to
  this SHA.
- **Phase 0 BASELINE written** (`docs/improvement/BASELINE.md`), all
  sections measured except coverage (§9, run still in flight).
- EUR-Lex re-verification closed out (see below) — this removes an item
  that was previously on the owner's manual list.

## PHASE 0 HEADLINE FINDINGS

1. **`doctor` misdirects users to a foreign PyPI package.** It prints
   `pip install regula[ast]`; the distribution is `regula-ai`, and
   `regula` is a real unrelated package (Tkinter wrapper, v0.1.2,
   VERIFIED 2026-07-27 via the PyPI JSON API). 18 occurrences repo-wide.
   HIGH severity, Trust dimension.
2. **Silent AST-to-regex downgrade for JS/TS on a default install.**
   tree-sitter is an optional extra; without it JS/TS analysis falls back
   to regex with no disclosure in scan output, while `docs/TRUST.md`
   claims "Python and JS/TS have full AST". HIGH, Detection + Trust.
3. **Precision corpus is Python-only.** Every seed query is
   `language:python`; the 83.5% headline generalises to none of the other
   seven supported languages. Recall is not measured at all.
4. **Superlinear scan performance.** 44 ms/file at 13 files vs 299 ms/file
   at 222 files. Largest real-world UX risk; cause undiagnosed.
5. **Version-attribution contradiction.** `PRECISION.json` says v1.7.0;
   `README.md:246` says v1.7.4 for the same measurement.
6. **Claim-auditor coverage** is 16 files for number drift; `docs/*.md`
   (58 files) is swept by no gate.

Provisional re-scored aggregate **54.4** vs the programme's 57, driven by
Detection 42 -> 38 and Trust 92 -> 84. Full arithmetic in BASELINE §11.

> **SUPERSEDED, flagged 28 Jul 2026. Do not quote 54.4 or 84.** Those were
> the figures at the point Phase 0 first wrote this section. Trust was
> subsequently lowered again to **72** on three legs (inflated count
> enforced as canonical, percentages undetectable, coordinate drift),
> giving an aggregate of **52.3**. `BASELINE.md` §11 is authoritative and
> already carries 72 and 52.3; this paragraph had not been updated to
> match, so the resume file and the baseline disagreed on the headline
> score.
>
> **Both are WORKING NUMBERS.** The Phase 7 independent scorer arbitrates,
> including over our own 92 -> 72 movement. Leg three (F7) has since been
> corrected downward from "wrong by hundreds of lines" to a 1-3 line drift
> with no misquote, so the **direction is intact but the level is
> deliberately not recomputed**. Do not recompute it here either.

## EUR-LEX RE-VERIFICATION (closed, no longer an owner task)

Two independent retrievals of Regulation (EU) 2026/1744 (the ELI
`/eli/reg/2026/1744/oj/eng` record and the CELEX `32026R1744` text),
27 Jul 2026, both agree:

- **No agentic-AI category or definition exists.** The research sweep's
  claim is contradicted by two independent fetches. Nothing in Regula
  asserts one; nothing may be added.
- **The Omnibus does not amend Article 111(2) and sets no 2 August 2030
  date.** The "2030 public-authority deadline" reported by secondaries is
  therefore NOT an Omnibus provision. MEASURED: Regula makes no such
  claim anywhere (the only `2030` strings in the repo are the Colorado
  cure-provision sunset, which is correct). No fix required; the item is
  closed as "claim never adopted".
- The new Article 5 points (ba)/(bb) exist; their specific application
  date is still not visible in the retrieved text, so the "2 December
  2026" date remains **REPORTED-UNVERIFIED** and is not asserted by
  Regula.

## IN PROGRESS

**Phase 1 exhaustive code review** — `docs/improvement/CODE_REVIEW.md`.

Sections COMPLETE (committed):
- §1 FP taxonomy + `fp_taxonomy.json` (`1356f97`)
- §2 Evidence-output spec validation (`81ffab8`)
- §3 Methodology note (instrument error)
- §4 Crosswalk audit (`088aded`)
- §5 Detection-layer reach + `measure_pattern_reach.py` (`6dfc1a9`)
- §6 Security pass (`ed83760`)
- Phase 0 §9 coverage recorded (`0d8424c`)

- §7 Architecture + repo hygiene (`46156ea`)
- §8 Test-suite audit (`46156ea`), §8.5.1 auditor line-attribution
  defect found by dogfooding (`f2f2fa6`)
- BASELINE corrections after independent verification (`e7df31a`)

**PHASE 1 IS COMPLETE.** Both audit subagents returned; every load-bearing
claim was re-verified before recording, and claims carried on the
subagents' evidence are tagged REPORTED per the project rule that
subagent output is not verified by default.

### Phase 1 findings so far (cumulative)

### Phase 1 findings so far

- **Corpus scope confusion resolved.** `PRECISION.json` high_risk n=6
  (tp=2, fp=4) is the post-domain-gating PRODUCTION subset of N=115. The
  full 201-entry labelled set contains **24** high-risk false positives
  and 98 FPs overall. The programme's "trace >=10 high-risk FPs" is
  therefore satisfiable; it would not have been from the N=115 subset
  alone. Both figures must always carry their scope.
- **The high-risk FPs are semantic, not lexical.** Five classes:
  generative-model infra read as critical infrastructure (7),
  non-production paths (6), domain-word collision (4), compute-vs-human
  homonyms (4), modality confusion (3). The firing patterns use genuine
  Annex III vocabulary (for example "task allocation", which is Annex III
  4(b) language) that carries an unrelated ordinary meaning in ML code.
  **Consequence for Phase 3:** regex tightening cannot fix this class
  without destroying recall; the fix space is context (package-level
  domain classification, co-occurrence requirements, path scoping, or an
  optional semantic verification tier). This is direct evidence for
  Phase 3 item 3 and against a naive "improve the regexes" plan.
- **HIGH: CycloneDX ML-BOM fails official schema validation.**
  `sbom.py:550` emits `modelCard.modelParameters.owner`; that object sets
  `additionalProperties: false` and permits only approach,
  architectureFamily, datasets, inputs, modelArchitecture, outputs, task.
  Never valid in 1.6 either, so it is a long-standing defect not a
  migration regression. SARIF, the pack manifest, pack tamper detection
  and all vocabulary IRIs pass. **No test validates any generated
  artefact against a published schema** — the structural reason this
  survived.
- **HIGH: 183 of 391 tier regexes (46.8%) are exercised by no test
  input.** They are unguarded rather than broken (the Article 5 NCII
  pattern is among them and works on a live scan), so a typo would ship
  with all 2,849 tests passing. Worst-exposed are the newest, highest-
  stakes prohibitions. Pattern *quality* is good (no compile failures, no
  catastrophic backtracking), which again points away from "better
  regexes" as the detection lever.
- **MEDIUM: crosswalk is 108 days old and does not consume the
  delta-log.** `article_11` still omits the Omnibus simplified-
  documentation route; `owasp_agentic` is missing from articles 11 and
  12; five reference files carry no verification stamp.
- **Security pass: no defects found.** No `shell=True`, no `eval`/`exec`,
  HTML filename escaping proven correct by live control.
- **Two instrument errors made and recorded** (piped exit code; filename
  tests that never created their file). Both were absent signals nearly
  read as clean results. Countermeasure adopted: require positive proof
  the code path executed.

## PHASE 1.5 — INTEGRITY-APPARATUS REPAIR (in progress)

Owner-approved scope fence: F1, F6, F7 and the `eli_data` packaging
defect only. Tests first, one logical commit each, a regression test per
defect. No AST reconciliation, no ML-BOM fix, no cache fix.

### Deviation record (owner-directed, recorded honestly)

- **The 2,821 -> 2,849 count cascade was a Phase 0 deviation.** Phase 0's
  constraint is "measure everything, change nothing"; the cascade changed
  ten published surfaces plus the auditor's canonical hint. It was not
  routine maintenance. Reverted at `a9ad2e8`.
- **The ELI snapshot / delta-dataset / benchmark harnesses were
  pre-programme**, committed at `d4180e3` before the programme began, so
  they are not a Phase 0/1 deviation. The packaging defect they
  introduced (`scripts/eli_data/*.json` absent from `package-data`) is
  mine regardless of when it landed, and is in the 1.5 scope.

### Status

| Item | State |
|---|---|
| Revert | **DONE** `a9ad2e8`. Ten surfaces byte-identical to pre-session; commit documents the intentional one-commit red gate. |
| F1 AC3 (config exclusion) | **VERIFIED** `pyproject.toml:92` declares `python_functions = ["test_*"]`; `_runner_test_*` cannot match. Asserted in the regression test so widening the config fails loudly. |
| F1 tests-first | **VERIFIED** `tests/test_collection_integrity.py` failed pre-fix with exactly 527 duplicates. |
| F1 AC1 (collection) | **2,325** = 2,322 corrected baseline + 3 new guard tests. |
| F1 AC2 (runner 1386/963) | **PENDING** — first post-fix run gave 1,380 passed / **1 failed** / 963 functions. Function discovery is intact (963 unchanged); one test fails. Not yet diagnosed; re-run in flight. **F1 will not land until this is green or shown unrelated.** |
| F1 AC4 (site_facts) | Pending AC2. |
| F6 | Regex candidate validated in isolation (catches `83.5%`, `40%`, `100% of`; ignores `version 1.7`, `Article 5`). Backlog re-measured — see below. |
| F7 | Consumer grep **DONE**: four invocations (`ci.yaml:113,115,122`, `.pre-commit-config.yaml:15`) all use default text output and consume only the exit code. **No `--format json` invocation exists anywhere; nothing parses line numbers.** Consumer-safe. |
| eli_data | Not started. |

### F6 — the approved backlog number was wrong, and the plan needs a decision

MEASURED through the auditor's own pipeline (patched copy, tracked files
untouched), over the 56 site HTML pages `site_integrity` actually sweeps:

| | claims | unsourced |
|---|---|---|
| current auditor | 182 | **0** |
| with percentage detection | 411 | **185** |

So the real quarantine backlog is **185 unsourced findings**, not the 341
I reported. 341 was a raw-text count across surfaces the gate does not
sweep, and it included CSS.

**The design problem:** of 294 raw percentage occurrences in site HTML,
**78 (27%) sit in CSS/layout contexts** (`style="width:100%"`,
gradients, transforms). Quarantining those as "UNVERIFIED BACKLOG,
NOT ENDORSED" would be a false label — they are not claims — and leaving
them detectable permanently saddles the gate with 78 standing false
positives, which degrades exactly the instrument this phase is repairing.

Recommendation: pair the regex fix with noise-stripping for inline
`style=` attributes so the surfaced set is genuinely claims, then
quarantine the real remainder. This is making the fix correct rather than
widening scope, but it changes the approved commit contents, so it is
flagged rather than assumed.

### Answers to two owner queries (closed)

- **The tenth surface.** "Nine" was inherited from the test-suite audit's
  own phrase — "nine surfaces (README, SECURITY.md, TRUST.md,
  MODEL_CARD.md, six site pages)" — which itself enumerates to ten. I
  repeated the label without summing its components. **The definitive
  list, from the revert diff `a9ad2e8`, is ten published surfaces:**
  `README.md`, `SECURITY.md`, `docs/TRUST.md`, `docs/MODEL_CARD.md`,
  `site/index.html`, `site/about.html`, `site/llms-full.txt`,
  `site/regions/uae.html`, `site/locales/de.html`,
  `site/locales/pt-br.html`. Two further files carried the number without
  being published surfaces: `scripts/claim_auditor.py` (canonical hint)
  and `data/site_facts.json` (generated artefact) — hence twelve files in
  the revert. This is the list F6's reconciliation and the eventual
  correction commit sweep.
- **`# regula-ignore` in the new fixtures: pre-existing convention, not
  introduced by me.** It first appears in commit `c83c07b` and is carried
  by 139 files at `main`, including test files I did not write
  (`tests/test_dpv_export.py` opens with it). It is a **scanner** pragma
  parsed by `scripts/risk_decisions.py` to suppress Regula's own
  false-positive findings on its own source; **the claim auditor does not
  honour it at all** (the sole occurrence in `claim_auditor.py` is the
  pragma on its own line 2). So it narrows no gate touched by this phase,
  and following the file convention introduced no bypass.

### Score-file annotation (owner-directed, 28 Jul)

The Trust movement 92 -> 72 rested on three legs. Leg three (F7
coordinates) has since been **corrected downward** from "wrong by
hundreds of lines, snippets misquoted" to a 1-3 line cumulative drift
with no misquote. Legs one (inflated count enforced as canonical) and two
(percentages undetectable) stand. **Direction intact; level NOT
recomputed.** Both score files now mark 72 as a WORKING NUMBER for the
Phase 7 independent scorer to arbitrate, including over my own movement.

### UNIT DEFINITIONS, and a correction to the F6 commit message

**Units (both occurrence-level, not deduplicated):**

- **claims** = every regex match the auditor records, counted once per
  occurrence. `report.claims += len(para_claims)`.
- **unsourced** = every claim that survived paragraph-sourcing, the
  allowlist and (now) quarantine, counted once per occurrence. One
  `Finding` per unsourced claim.

Under these definitions **unsourced is a strict subset of claims**, and
the current state satisfies it: 370 claims, 0 unsourced, 42 quarantined
entries (the quarantine deduplicates to unique `(file, claim)` pairs, so
42 unique pairs correspond to **45** occurrences — the only place a
deduplicated unit appears, and it is labelled as such in the quarantine
header).

**CORRECTED 28 Jul 2026: this paragraph said 55 occurrences.** It was
wrong, and it contradicted the 45 in the RECONCILED CHAIN section further
down this same file, and the 45 in `_reconciliation` in the quarantine
file whose `_units` field sat directly above it saying 55. Three
statements of the same quantity, two of them right. Re-measured in place
(real `scripts/claim_auditor.py`, correct `REPO_ROOT`, the same 56 pages
`site_integrity.py` sweeps, tallying `is_quarantined` hits without
patching the auditor): **370 claims, 0 unsourced, 45 suppressed
occurrences across 42 unique pairs.** 45 is correct and is now in both
places. The measurement also showed **0 quarantine entries matching
nothing**, so there is no stale entry padding the count and the
shrink-only ratchet is measuring something real.

**CORRECTION — the reconciliation table in commit `35fc763` is not
reliable.** It reported that the CSS fence removed "41 claims and 140
would-be findings, all of them layout values". Re-measured on a single
consistent code state (current code, quarantine disabled, fence toggled):

| state | claims | unsourced |
|---|---|---|
| fence OFF | 411 | 185 |
| fence ON | 370 | **168** |

So the fence removes 41 claims and **17** findings, not 140. The
intermediate figures in that commit were taken across *differing* code
states — the F7 coordinate fix landed between two of the measurements,
and correcting line attribution changes which line the allowlist is
tested against, which changes how many claims get exempted. I attributed
the whole movement to the fence without controlling for that.

The commit is landed and history is immutable, so the correction lives
here. **What remains true and independently verified:** percentages are
now detectable, CSS values are fenced out with per-attribute proof that
prose attributes are not, the gate is green for new claims, and the
backlog is 42 unique pairs under quarantine. **What was wrong:** the
attribution of the drop between the fence and the coordinate fix.

Method lesson, third instance this phase: measure one variable at a time,
on one code state. The 341 -> 185 -> 45 sequence improved because the
instrument improved; this error is the opposite failure — comparing
across instruments and crediting the change to whichever one I had just
edited.

### 1.5b batch — triage prepared (execution pending F1 + count correction)

> **SUPERSEDED AND WRONG. Do not act on the next paragraph.** It is kept
> because deleting a wrong call hides that it was made. The substantive
> per-occurrence audit is in "83.5% — per-occurrence audit" below, and it
> **overturns this**: provenance fails at **five of eight** locations,
> including a bare number on a public page. Read that section instead.
>
> **The error class, because it will recur.** The paragraph below checks
> the wrong thing. "Not in the quarantine" is the *auditor's* criterion
> (an annotation exists somewhere). The *bar the owner set* is honest
> provenance at the point of use. A claim can satisfy the first and fail
> the second at every location, which is exactly what happened. **Passing
> a gate is not evidence of meeting a standard when the gate tests
> something narrower than the standard.**

**The priority item is already clean.** The 83.5% precision claim is
**not in the quarantine** — its occurrences are already sourced or
allowlisted, so the bar set for it ("N=115, single labeller, visible or
one link away") has nothing to act on in this batch. That is worth
re-checking during Phase 8's every-number sweep rather than assumed
permanently settled, but no 1.5b disposition is owed for it.

**The 42 pairs reduce to 19 distinct claim texts in three classes:**

1. **Round percentages in landing/locale UI (about 30 of 42 pairs).**
   `0/20/30/40/50/60/70/80%` in `index.html`, `about.html`, both locale
   files and `assess/*`. Context sampled: they are values in an ASCII
   progress-bar widget (`&#9617;&#9617;… 30%` beside "Article 14 Human
   Oversight"). **These are rendered prose, correctly in scope** — a
   coverage percentage beside an article name reads as a claim about
   Regula's coverage of that article, whatever the surrounding markup.
   Likely disposition: **corrected** (state what the figure describes, or
   drop the numeral from an illustrative widget). Not "verified": no
   underlying measurement is cited today.
2. **Empirical statistics in blog posts (about 9 pairs).** For example
   "Agent autonomy dominated at 56.6% of findings" across 8,659 source
   files (`blog-scanning-10-ai-apps.html`), plus 41/57/65/72% in
   `blog-scanning-5-frameworks.html`. These are real study results.
   Likely disposition: **verified-with-source** if the post's own
   methodology section supports them, else corrected.
3. **Hypothetical illustrations (about 3 pairs).** For example "A model
   with 95% accuracy overall but 70%…" in a healthcare guide — a worked
   example, not a claim about Regula or the world. Likely disposition:
   **corrected** by framing so the hypothetical is unambiguous, since a
   bare figure in prose reads as factual.

Every class-1 and class-3 item is a public-surface edit and therefore
goes into the single batched approval, with the full per-item disposition
list, before any of it lands.

### PHASE 1.5 COMPLETE — all four items landed

| Item | Commit | Evidence |
|---|---|---|
| F7 coordinates | `59ac25b` | fixture suite + line-count invariant |
| F6 percentages + fence + quarantine | `35fc763` | 3-case fence fixture + shrink-only ratchet |
| eli_data packaging | `7383f33` | verified against a real wheel build |
| **F1 count** | **`fd212fb`** | **10/10 captured runs at 1386/0/963** |

Published count corrected **2,821 -> 2,349**, produced by collection.
`--verify-facts` rc=0, `site_integrity` OK, 27 Phase 1.5 guard tests pass.

**F1 watch item (open, not closed):** an early post-fix run reported
1,380 passed / 1 failed, function count intact at 963. Did not reproduce
across ten runs; failure text never captured. Unreproduced transient, not
a diagnosis. Repro `timeout 2400 python3 tests/test_classification.py`;
captures at `<scratchpad>/runner_runs/`.

**Two `git add -A` deviations, disclosed in `fd212fb`:** the manifest and
its test landed in `140e7fb` instead of the count-correction commit; and
the F1 code landed in `8a5888d`, whose message says F1 was NOT landed.
Both messages are now inaccurate about their own contents.

**NEXT: 1.5b batch pack** (owner approval required before any public
surface changes), then Phase 2.

### RECONCILED CHAIN — closed, and 185 was never real

All four stages re-measured **in place**, on the real file, with the real
`REPO_ROOT`, over the same 56 site pages. Units are occurrence-level for
both columns.

| stage | claims | unsourced |
|---|---|---|
| S1 pre-F6, as landed at `59ac25b` | 182 | 0 |
| S2 + percent detection, no fence | 411 | **61** |
| S3 + CSS fence | 370 | **45** |
| S4 + quarantine (current) | 370 | 0 |

`unsourced <= claims` holds at every stage. Deltas: percent detection
surfaces +229 claims and +61 findings; the fence removes 41 claims and
**16** findings; quarantine holds the remaining 45.

**Why the chain looked broken.** The 185 and 168 figures were produced by
running *patched copies of the auditor from the scratchpad directory*.
`REPO_ROOT` is derived from the module's own location, so those runs
resolved repo-file citations against the scratchpad — every
`paragraph_has_source()` check that depends on a file reference existing
failed, and paragraphs that are genuinely sourced were counted unsourced.
**185 was an artefact of the measuring rig, not a state the repo was ever
in.** The earlier "17" correction was drawn from the same bad pair and is
also wrong; the true fence delta is 16.

**THE ~123 GAP, CLOSED EXPLICITLY.** This was the specific loose thread,
so here is the arithmetic rather than a narrative. The old bogus pair was
fence OFF 185, fence ON 168, implying the fence removed 17. The quarantine
holds 45. That left `168 - 45 = 123` findings with no account of where
they went. A 17-finding fence correction cannot explain 123 findings, and
that mismatch was the correct thing to refuse to sign off.

**The gap never existed.** It was manufactured entirely by the broken rig,
at both ends of the subtraction. On the corrected in-place chain the same
arithmetic closes to zero:

| quantity | bogus rig | measured in place |
|---|---|---|
| unsourced, fence OFF | 185 | **61** |
| unsourced, fence ON | 168 | **45** |
| fence delta | 17 | **16** |
| held by quarantine | 45 | **45** |
| **unaccounted for** | **123** | **0** |

`45 - 45 = 0`. Every finding the fence does not remove is held by the
quarantine, and the quarantine holds nothing else: the in-place
measurement of 28 Jul found 45 suppressed occurrences across 42 unique
pairs with **zero entries matching nothing**. Nothing is unexplained and
nothing is padding the count. Thread closed.

Fourth instrument error of this phase, and the same root as the others:
the rig was not identical to the thing being measured. The rule that
would have caught all four: **measure in place, one variable at a time,
and never trust a number produced by a copy.**

### 83.5% — per-occurrence audit (owner-ordered, deferral overruled)

**Auditor status: NOT allowlisted.** It is artefact-verified — 83.5 is in
`known_precision_values()`, derived live from
`benchmarks/results/random_corpus/PRECISION.json`. There is no excused
flagship claim.

**Provenance-at-point-of-use status: FAILS at three locations.** The bar
is N=115 and single-labeller visible or one link away.

Single-labeller is disclosed in exactly one place repo-wide:
`benchmarks/README.md:198` ("Single reviewer. All labels are from one
reviewer. No inter-rater...").

| # | Location | N at point of use | Single-labeller reachable | Verdict |
|---|---|---|---|---|
| 1 | `README.md:246` | yes | yes — links `benchmarks/README.md`, which carries it at :198 | PASS |
| 2 | `benchmarks/README.md` (:87,:105,:108,:132,:140,:180) | yes | yes — same file | PASS |
| 3 | `docs/MODEL_CARD.md:75,:79` | via :143 same page | see #4 | PASS on N |
| 4 | `docs/MODEL_CARD.md:143` | yes | **NO** — links `METHODOLOGY.json`, which contains corpus construction only (description, date, pool, sample, seed, queries, filters, repos) and no labeller field | **FAIL** |
| 5 | `docs/TRUST.md:157` | yes | **NO** — no route to the labeller disclosure | **FAIL** |
| 6 | `docs/examples/exec-summary-sample.html:89` | yes | **NO** — links TRUST.md, which per #5 does not carry it | **FAIL** |
| 7 | `scripts/exec_summary.py:225` (generates #6) | yes | **NO** — same chain | **FAIL** |
| 8 | **`site/about.html:132`** | **NO** | **NO** | **FAIL — bare "Published precision on a random corpus: 83.5%." with no N, no labeller, no link, on a public page** |

**Also surfaced:** the version attribution splits across surfaces —
`README.md` and `TRUST.md` say measured on v1.7.4; the exec summaries and
`PRECISION.json` say v1.7.0. This is finding F20, previously logged, now
confirmed to affect the flagship number's provenance directly.

**Conclusion: the deferral was wrong.** The auditor's criterion (an
annotation exists) and the bar (honest provenance at point of use) are
different checks, and the second fails at five of eight locations —
including a bare flagship number on `site/about.html`. Dispositioned
first in the 1.5b batch as originally ordered.

### F7 must precede the F6 burn-down (evidence, not preference)

While triaging the percentage findings above, the auditor reported a
finding at `L423`; the actual content at that line was unrelated markup.
The wrong-coordinates defect **actively blocked triage** and forced a
grep-based workaround. Burning down 185 items against wrong line numbers
would multiply that cost 185 times. F7 lands before 1.5b starts.

## NEXT (start of next session)

1. **1.5b batch pack** — build it, do not land it. Scope restated in the
   checkpoint at the end of this file. **Nothing touches a public surface
   before the owner approves the pack.**
2. **Phase 2** research acquisition + validation. Note: `docs/research/`
   does not exist; the seed corpus lives at
   `getregula-internal/research-sweep-2026-07.md` (outside the repo, see
   HANDOVER §12) with a completed primary-source verification tracked at
   `docs/improvement/PHASE0_VERIFICATION.md`. Cards inherit that
   verification where applicable and must say so; the RESEARCH VALIDATOR
   subagent gets the cards only.
3. Then Phase 3 (instruments first), Phase 4 (plan + HOSTILE REVIEWER +
   human gate).

## PHASE 1 FINAL FINDING LIST (severity-ordered, for the Phase 4 plan)

| # | Finding | Sev | Dimension | Verified |
|---|---|---|---|---|
| F1 | Published test count double-counts 18.5% (2,849 node IDs vs 2,322 unique); enforced as canonical by the auditor; published on 9 surfaces | CRITICAL | Trust, Craft | [V] me |
| F2 | `doctor` tells users `pip install regula[ast]`; `regula` is a real unrelated PyPI package | HIGH | Trust | [V] me |
| F3 | Default install silently downgrades JS/TS from AST to regex; docs claim full AST | HIGH | Detection, Trust | [V] me |
| F4 | CycloneDX ML-BOM fails official schema (`modelParameters.owner`), never valid in 1.6 either | HIGH | Trust, Altitude | [V] me |
| F5 | 183/391 tier regexes (46.8%) exercised by no test input, incl. the new Article 5 NCII prohibition | HIGH | Detection, Craft | [V] me |
| F6 | Claim auditor cannot match a bare `%` at all (trailing `\b` at `:69`) | HIGH | Trust | REPORTED, mechanism traced |
| F7 | Auditor reports wrong line numbers and wrong snippets | HIGH | Trust | [V] me |
| F8 | `regula check` never uses the AST engine; two unreconciled detectors | HIGH | Detection, Trust | REPORTED |
| F9 | Scan cache keys lack a project root; provenance replays across projects, defeating `--scope` | HIGH if reproduced | Detection, Trust | REPORTED — reproduce first |
| F10 | No test validates any generated artefact against a published schema | HIGH | Trust | [V] me |
| F11 | Precision corpus is Python-only; recall never measured | HIGH | Detection | [V] me |
| F12 | `verify_facts()` and `main()` — the auditor's CI entry points — untested | HIGH | Trust | REPORTED |
| F13 | `eli_data` and `dashboard/` missing from the wheel (F13a is my own defect) | MEDIUM | Craft, Trust | [V] me |
| F14 | Crosswalk 108 days stale, does not consume the delta-log; `owasp_agentic` missing from 2 articles | MEDIUM | Currency | [V] me |
| F15 | `test_questionnaire_scoring.js` is a full data copy, already drifted, never executed | MEDIUM | Craft | REPORTED |
| F16 | Superlinear scan performance (44 ms/file at 13 files, 299 ms/file at 222) | MEDIUM | Craft, UX | [V] me |
| F17 | README mismatches: `--ci` gives no SARIF; `demo` does not need the clone; jurisdiction crosswalk is EU-only | MEDIUM | Trust | REPORTED |
| F18 | Zero SPDX headers despite a composite licence | LOW | Craft | REPORTED |
| F19 | `ci_heal.py` (588 lines) and three other modules are dead | LOW | Craft | REPORTED |
| F20 | Version attribution contradiction: PRECISION.json v1.7.0 vs README v1.7.4 | LOW | Trust | [V] me |
| **F21** | **A page's own canonical URL satisfies `paragraph_has_source()`, so every `<meta>` description number is auto-sourced and can never be flagged** | **HIGH** | **Trust** | **[V] me, MEASURED 28 Jul** |

### F21 — the meta-description gap (OWNER_ACTIONS item 8, answered)

The question was whether `claim_auditor` sweeps `<meta>` content. **It
does** — the tags are not blanked by `strip_noise`, and the auditor
extracts **27 claims** from numeric `<meta>` description lines across the
56 site pages. So the feared gap ("meta is invisible to the gate") is not
the real one.

**The real gap is worse, because the gate looks green.** All 27 of those
claims are suppressed with reason `url`. The `<head>` block parses as one
paragraph, and it contains `<link rel="canonical"
href="https://getregula.com/...">`. `paragraph_has_source()` returns True
on its first check, `URL_RE.search(paragraph)`. **The page's own address
is accepted as the source for every number in its own `<head>`.**

MEASURED 28 Jul 2026, in place, real module, real `REPO_ROOT`, counting
with `scan_file` semantics so the total reconciles to the gate's own 370:

| source reason | claims |
|---|---|
| NOT sourced (then allowlist + quarantine) | 167 |
| `url` | 92 |
| `citation-word` | 88 |
| `html-link` | 22 |
| `file-ref:README.md` | 1 |
| **total** | **370** (gate reports 370) |

**16** of those claims sit in a paragraph whose URL context includes a
self-canonical link. Real examples of numbers currently riding this:
`site/blog/blog-scanning-5-frameworks.html:24` "562 findings",
`site/blog/blog-article-5-prohibited-practices.html:29` "35M" and "7%".

**Consequence.** The originating worry was a stale search-index snippet
showing "398 risk patterns, 12 frameworks" against the canonical 419/13.
If that drift existed in a `<meta>` description, **the gate would not
catch it.** Every meta number is permanently pre-sourced.

**Error class: the same one as 83.5%.** The gate tests "is there a URL in
this paragraph", the standard is "does this number trace to something
that supports it". A self-referential link satisfies the first and is
worthless against the second. Now rule 5 in `.claude/rules/measurement.md`.

**Scope discipline:** logged, not fixed. The disposition belongs in the
1.5b pack because it is the same instrument. Note the fix is NOT "stop
sweeping meta": the sweep is correct and should stay. The fix is that a
self-referential URL must not count as provenance.

Sequencing note for Phase 3/4: F1, F6 and F7 are all defects **in the
integrity apparatus itself**. They should be fixed before any work that
adds new public numbers, or the new numbers inherit a broken gate.

## OPEN QUESTIONS

- None blocking.

## ESCALATIONS

- None yet.

## DRIFT CHECK

Is the current activity the highest-value path to the rubric? **Yes, with
one correction already applied.** Phase 0 measurement is the precondition
for Principle 2. Correction logged this session: the previous session's
recommendation that the head-to-head benchmark be gated on human
annotator recruitment was **over-strict**. A synthetic-corpus run has
ground truth true by construction and needs no annotators; it can and
should run in Phase 3 as pre-registered, with the human-labelled
real-world run added later. Gating everything on the slowest human
dependency was self-inflicted drift.

---

# CHECKPOINT — 28 July 2026, end of session 2

Phase 1.5 accepted as complete by the owner. Ten of ten captured greens
satisfied the gate; 2,349 checks out as 2,322 + 27 Phase 1.5 guards; the
MODEL_CARD "unique test IDs" fix was ratified as within the correction's
scope, being the same conflation the correction exists to remove.

**Phase 1.5b is NEXT and not started.** Next session opens on this file
per the session protocol and builds the approval pack. **Nothing touches a
public surface before the owner approves the pack.**

## Owner decisions executed this session

| Decision | Outcome |
|---|---|
| 1. `.claude/` | **Relocate, do not track wholesale.** DONE, with a sensitivity carve-out (below). |
| 2. Premature commits | **Disclosure stands, no history rewrite.** `COMMIT_ERRATA.md` added; `.claude/rules/git.md` added and tracked. DONE. |
| 3. Reconciled table | **Confirmed landed**, and a contradiction inside it was found and fixed. DONE. |
| 4. 83.5% | Per-occurrence table required in the pack, covering passing and failing locations. Carried into the scope below. |

### Decision 1, and where it was not followed literally

The sensitivity check the owner ordered found that this repository is
**public** (`gh repo view kuzivaai/getregula`: `isPrivate: false`,
verified 28 Jul 2026) and that some relocation candidates are competitive
and commercial strategy, a class this repo's own `.gitignore` already
declares not-public.

Tracked, as ordered: `HANDOVER.md`, `PHASE0_VERIFICATION.md`,
`OWNER_ACTIONS.md`, `docs/dpvcg-contribution-draft.md`, plus
`.claude/rules/` and `.claude/commands/` un-ignored by subpath.

**Held outside the repository at `getregula-internal/`, contrary to the
literal instruction and flagged for the owner:**
`research-sweep-2026-07.md`, `moat-programme-2026-07.md`, and a
`competitive-intelligence-2026-07.md` extracted from section E of the
Phase 0 verification and section 6 of the owner-actions list. Two owner
personal-data items were redacted from the handover's section 10.

Calibration, so this is not over-applied later: **competitor names were
NOT redacted**, because the repo already names its comparison set publicly
in `benchmarks/headtohead/PREREGISTRATION.md` and `adapters.py`. What was
held back is positioning work: pricing, star counts, Regula's absence from
a competitor comparison page, and the ranked commercial strategy.

This trades the `git clean` risk for a no-backup risk, since
`getregula-internal/` has no version control. Logged as open owner
decision 4 in HANDOVER §11.

### Decision 3, confirmed and corrected

The reconciled table **had** landed, in the STATE.md "RECONCILED CHAIN"
section and in the quarantine's `_reconciliation` field. Reading them
together surfaced a defect: the quarantine's `_units` field said the 42
entries were **55** occurrences while `_reconciliation`, in the same file,
said **45**. STATE.md carried both figures too.

Re-measured in place, importing the real `scripts/claim_auditor.py` so
`REPO_ROOT` is correct, tallying `is_quarantined` hits over the same 56
pages `site_integrity.py` sweeps, without patching the auditor:

```
pages 56 | claims 370 | unsourced 0 | entries 42
suppressed occurrences 45 | unique (file,claim) 42
quarantine entries matching nothing: 0
```

**45 is correct; 55 was stale.** Fixed in both places. The ~123 gap is now
closed with explicit arithmetic in the RECONCILED CHAIN section: it never
existed, both ends of the subtraction came from the broken scratchpad rig,
and on the corrected chain `45 - 45 = 0`. Zero stale quarantine entries
means nothing is padding the ratchet.

## 1.5b PACK SCOPE (build next session, do not land)

One batch, 42 unique pairs / 45 occurrences. Owner approval required
before ANY public surface change.

1. **Five 83.5% provenance fixes.** `docs/MODEL_CARD.md:143`,
   `docs/TRUST.md:157`, `docs/examples/exec-summary-sample.html:89`,
   `scripts/exec_summary.py:225`, and `site/about.html:132`, the worst,
   a bare "Published precision on a random corpus: 83.5%" with no N, no
   labeller and no link on a public page. **The pack must present a
   per-occurrence table covering every location, passing and failing, so
   approval happens on full evidence.** Bar: N=115 and single-labeller
   provenance visible or one link away at every point of use.
   Single-labeller is disclosed in exactly one place repo-wide,
   `benchmarks/README.md:198`. **Do not strip the number**; its successor
   is Phase 3's corpus. Fold in F20, the v1.7.4 vs v1.7.0 attribution
   split.
2. **Class 1, progress-bar percentages (~30 pairs): DERIVE OR REMOVE.**
   A citation on an unmeasured number is not a correction. A percentage
   stays only with a defined numerator and denominator generated from
   measured data (site_facts pattern, test-backed). "30% of Article 14"
   has no honest denominator. Options: derived counts ("4 of 7
   requirements mapped", computed from crosswalk data), qualitative
   tiers, or removal. **The pack must show the proposed replacement as it
   would render**, because this changes the landing page's face.
3. **Class 2, blog statistics (~9 pairs): reproducible or externally
   cited.** Methodology plus data or scripts sufficient to reproduce, or
   an external primary source. **A post asserting its own number is not a
   source for that number.** Where the artefacts do not exist, the honest
   disposition is an annotation saying so, or a correction.
4. **Class 3, hypotheticals (~3 pairs): rewrite so the framing is explicit
   in the sentence itself.** Any exemption must be **typed
   (`ILLUSTRATIVE`)**, constrained to framed sentences, carry a **control
   proving a factual claim cannot ride it**, and stay **distinct from the
   shrink-only quarantine**. The constraint is non-negotiable; the design
   is ours to propose in the pack.

Also log "unmeasured coverage percentages on the most public surfaces" in
the severity list: it predates the programme, and the repaired gate now
catches the class. Phase 7 evidence both ways.

The quarantine must be **empty before Phase 6/8 publishes anything**.
Quarantined items would fail the every-number-traces sweep regardless.

## Still open, carried forward

- **F1 watch item: OPEN, accepted as recorded.** Unreproduced transient,
  capture armed. Not a diagnosis. Do not close it without a reproduction.
  Repro: `timeout 2400 python3 tests/test_classification.py > run.txt 2>&1`
  (redirect to a file; a pipe loses the failure line, which is how it was
  lost the first time).
- **Full `pytest tests/ -q`: DONE AND GREEN, 28 Jul 2026.** `2349 passed`
  in 1406.51s (23:26), pytest's own exit code 0, zero `FAILED` or `ERROR`
  lines in the log. The executed count **equals** the collect-only count
  (2,349 = 2,349), which is the thing that needed confirming: the
  corrected collection is not just counted correctly, it executes clean
  end to end after the F1 rebind. This closes the carried-over re-run
  item. Re-run it before any release, not every session.
  **This does NOT bear on the F1 watch item.** That transient was in the
  **custom runner** (`tests/test_classification.py`, 1386/0/963), a
  different harness with different discovery. A green pytest run is not
  evidence about it either way.
- Owner decisions 3 (1.5b pack) and 4 (backup for `getregula-internal/`).
- `OWNER_ACTIONS.md` items 1, 2, 3, 5, 7 and the new 8. Item 4 is closed.
- **New, from the relocation:** does `claim_auditor` sweep `<meta>`
  descriptions? Untested. `OWNER_ACTIONS.md` item 8.

---

# CHECKPOINT — 28 July 2026, end of session 3 (Phase 4 gate attempt)

**Read `docs/improvement/GATE-REVIEW.md` first.** It consolidates both
decisions.

## Headline: both independent subagents returned FAIL, and both were right.

| Charter | Verdict | Loop | Status |
|---|---|---|---|
| RESEARCH VALIDATOR (Phase 2) | **FAIL** | 1 of 3 | 2 of 4 pass criteria unmet |
| HOSTILE REVIEWER (Phase 4) | **FAIL** | 1 of 3 | 16 MAJOR, all accepted |

**Neither Phase 2 nor Phase 4 has passed. The Phase 4 plan must not be
executed.** Loop 2 has not run for either. Dispositions are written up in
`HOSTILE-REVIEW-DISPOSITIONS.md` and inline in `RESEARCH-CARDS.md`, per
principle 7.

## New artefacts

`PACK-1.5b.md` (built, held, **nothing applied**) · `RESEARCH-CARDS.md` ·
`PLAN-PHASE4.md` · `HOSTILE-REVIEW-DISPOSITIONS.md` · `GATE-REVIEW.md` ·
`benchmarks/headtohead/RESULTS-synthetic-2026-07-28.md` + raw JSON ·
`.claude/rules/measurement.md` · `.claude/rules/git.md` ·
`COMMIT_ERRATA.md`.

## Three defects of mine, in already-committed documents

1. **A falsified research claim** ("ICSE 2026 ran a single-annotator first
   pass") published to `RESEARCH-CARDS.md` from a retrieval subagent
   without verification. It was the load-bearing leg of a recommendation to
   relax the programme's own annotator bar. **Struck.** κ ≥ 0.6 floor
   restored; three annotators retained.
2. **P8's acceptance criterion was gameable.** MEASURED:
   `measure_pattern_reach.py:85` counts a pattern guarded if its string
   appears anywhere in the corpus tree, so the criterion needed no
   assertion. My anti-gaming note policed plausibility, not assertions.
3. **Craft anchor carried at 90 from PROGRAMME.md** instead of the measured
   88. Caught by me and independently by the reviewer.

## New findings

- **F21 (HIGH):** a page's own canonical URL satisfies
  `paragraph_has_source()`, so all 27 `<meta>` description claims pass
  permanently. Disposition in PACK-1.5b §2.
- **NEW, Tier 0:** `docs/architecture.md:53` (tracked) publishes
  `1,223 tests`; canonical is **2,349**; the file is outside the auditor's
  list; `--verify-facts` returns rc=0. Live claim-integrity defect.
- **NEW, detection:** `highrisk_employment.py` classifies `ai_security`
  only, not high risk. First measured high-risk recall: **4/5**.
- **BASELINE §11 contradicts itself:** craft row says "Hold at 90", its
  arithmetic uses 88 → aggregate is **52.3 or 52.6**. Unresolved by design;
  Phase 7 arbitrates. Its craft evidence also cites the stale 2,849.

## Projected movement

Mine (corrected): 53.7-57.2. **Reviewer's counter: 52.9-54.5, +0.6 to
+2.2. I accept the counter as more defensible.**

## NEXT

1. **Owner decisions** — 1.5b pack; the `blog-scanning-10-ai-apps`
   discrepancy (OWNER-INPUT); private remote.
2. **Phase 4 loop 2**: revise the plan against the 24 accepted objections,
   re-run HOSTILE REVIEWER fresh. Reprioritise per its ruling — Tier 0 is
   right, **Tier 2 is where the disproportion is**; cut P8 to 17 prohibited
   patterns; promote the `docs/*.md` gate gap, version attribution,
   `.gitignore` scan handling, the 16 `_sha256` sites, and F9's repro.
3. **Phase 2 loop 2**: add per-item domain-shift notes (B3, C1, C2, C3,
   C4), then re-run RESEARCH VALIDATOR fresh.
4. F1 watch item stays open. The green pytest run is not evidence about it.

**Nothing public changed. `main` untouched. Tree clean.**
