# Improvement Programme — STATE

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
  prompt assumes: `.claude/research-sweep-2026-07.md` (owner sweep,
  condensed) plus `.claude/phase0-verification-2026-07.md` (a completed
  primary-source verification of that sweep, 27 Jul 2026). Phase 2 will
  build validation cards on top of the already-verified set rather than
  re-verifying from zero, and will state which cards inherit prior
  verification vs which are new.

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
42 unique pairs correspond to 55 occurrences — the only place a
deduplicated unit appears, and it is labelled as such in the quarantine
header).

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

1. **Phase 2** research acquisition + validation. Note: `docs/research/`
   does not exist; the seed corpus lives at
   `.claude/research-sweep-2026-07.md` with a completed primary-source
   verification at `.claude/phase0-verification-2026-07.md`. Cards
   inherit that verification where applicable and must say so; the
   RESEARCH VALIDATOR subagent gets the cards only.
2. Then Phase 3 (instruments first), Phase 4 (plan + HOSTILE REVIEWER +
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
