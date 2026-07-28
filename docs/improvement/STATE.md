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
- Prior 27 Jul moat work committed at **`d0c08a4`** — BASELINE anchors to
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
- §1 FP taxonomy + `fp_taxonomy.json` (`7a0e1c0`)
- §2 Evidence-output spec validation (`5871bb2`)
- §3 Methodology note (instrument error)
- §4 Crosswalk audit (`2cd62a7`)
- §5 Detection-layer reach + `measure_pattern_reach.py` (`204dbcf`)
- §6 Security pass (`e1175e5`)
- Phase 0 §9 coverage recorded (`88decee`)

- §7 Architecture + repo hygiene (`a6f7001`)
- §8 Test-suite audit (`a6f7001`), §8.5.1 auditor line-attribution
  defect found by dogfooding (`c82a51b`)
- BASELINE corrections after independent verification (`40f26ae`)

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
  routine maintenance. Reverted at `f476af7`.
- **The ELI snapshot / delta-dataset / benchmark harnesses were
  pre-programme**, committed at `d0c08a4` before the programme began, so
  they are not a Phase 0/1 deviation. The packaging defect they
  introduced (`scripts/eli_data/*.json` absent from `package-data`) is
  mine regardless of when it landed, and is in the 1.5 scope.

### Status

| Item | State |
|---|---|
| Revert | **DONE** `f476af7`. Ten surfaces byte-identical to pre-session; commit documents the intentional one-commit red gate. |
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
