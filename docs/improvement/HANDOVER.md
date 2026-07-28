# Regula Handover

Written 28 July 2026, at the end of a long session that completed Phase
1.5 of the improvement programme. Supersedes all earlier versions.
`.claude/handover.md` is older, superseded history.

**Read this sceptically.** This project has a documented history of
confident-but-wrong statements, and this programme produced **four of
them from me** in a single phase. All were caught; all are recorded in
§6 rather than deleted. **Any number you did not personally measure is
unverified.** Do not repeat a figure from prose; re-measure it.

> **RELOCATED AND NOW TRACKED, 28 July 2026.** This file was
> `.claude/regula-handover.md`. The warning that used to sit here was that
> `.gitignore` excluded the whole `.claude/` directory, so one
> `git clean -xdf` would destroy this handover with no history. The owner
> resolved that (open decision 1, now closed): **relocate, do not track
> `.claude/` wholesale.** This file is now
> `docs/improvement/HANDOVER.md` and is under version control.
> `docs/improvement/STATE.md` remains the resume file; this remains the
> narrative.
>
> **Two redactions were made on relocation**, because
> `github.com/kuzivaai/getregula` is a **public** repository and this file
> carried two pieces of owner personal data. Both are in §10 and both are
> marked in place. Nothing else in this document was altered. See §12 for
> where every relocated file now lives, and what was held back from the
> public repo and why.

---

## 1. START HERE

**Branch: `improvement/2026-08-programme`. `main` is untouched** and still
represents released v1.9.0. Everything below is **unreleased**. The branch
is **not pushed**: it has no upstream and does not appear in
`git ls-remote --heads origin` (checked 28 Jul 2026), so nothing here is
public yet. The commit count was 25 when this file was first written and
26 after the relocation commit; **that number goes stale every commit, so
re-measure it rather than quoting this line**:
`git log --oneline main..HEAD | wc -l`. Phase state is tracked in
`docs/improvement/STATE.md`.

A fresh session must, in order:

1. Read `docs/improvement/PROGRAMME.md` — the commissioning contract,
   committed verbatim. It is the specification this work is judged
   against.
2. Read `docs/improvement/STATE.md` — the resume file, with the full
   finding table, triage and open decisions.
3. Re-measure before trusting anything: `git log --oneline main..HEAD |
   wc -l`, `git status`, and the gate commands in §9.

Do not start Phase 2 without doing the above. Do not commit to `main`.

## 2. PROGRAMME STATUS

| Phase | Status |
|---|---|
| Session protocol | DONE |
| Phase 0 — baseline | DONE (`docs/improvement/BASELINE.md`) |
| Phase 1 — exhaustive code review | DONE (`CODE_REVIEW.md`, `fp_taxonomy.json`) |
| **Phase 1.5 — integrity-apparatus repair** | **DONE — all four items landed** |
| **Phase 1.5b — quarantine burn-down** | **NEXT. Not started. Triage prepared.** |
| Phases 2-8 | NOT STARTED |

Phase 1.5 was inserted by the owner after Phase 1 found that the tools
guarding Regula's published claims were themselves defective. Fixing the
gate had to precede publishing anything new through it.

## 3. WHAT PHASE 1.5 FIXED

| Item | Commit | Evidence |
|---|---|---|
| **F7** auditor coordinate drift | `59ac25b` | fixture suite + line-count invariant |
| **F6** percentage blindness, CSS fence, quarantine | `35fc763` | 3-case fence fixture + shrink-only ratchet |
| **eli_data** packaging | `7383f33` | verified against a real wheel build |
| **F1** test-count double-count | `fd212fb` | **10/10 captured runs at 1386/0/963** |

**F1 — the headline.** `tests/test_classification.py` rebinds
fixture-less tests from 22 sibling modules into its own namespace so the
custom runner (which discovers by walking `globals()`) can execute them.
pytest also collects module-level `test_*` names, so every rebound
function was collected **twice**. The published count was overstated by
18.5%: `2,821` and briefly `2,849` both double-counted the **same 527
functions**. Fixed by binding aliases under `RUNNER_ALIAS_PREFIX =
"_runner_test_"`, which pytest's configured `python_functions =
["test_*"]` cannot match. **No manual registry** — one was deliberately
removed as tech debt because it drifted silently.
**Published count corrected 2,821 -> 2,349, produced by collection, never
hand-maintained.**

**F7.** `strip_noise` blanked inline-code spans with spaces, but
`` `[^`]*` `` matches across line breaks, so a span wrapping a line lost
its newline and every later coordinate shifted up by one, cumulatively.

**F6.** `NUMERIC_CLAIM` ended its unit alternation in `\b`; `%` is not a
word character, so percentage claims were invisible while the docstring
listed them first. Percent is now a unit. Paired with a narrow fence:
inline `style=` **values** are blanked (CSS lengths are not claims) while
`alt`, `title`, `aria-label` stay in scope as user-visible prose.
`.claim-quarantine.json` holds the pre-existing backlog (**42 unique
(file, claim) pairs = 45 occurrences**), labelled UNVERIFIED BACKLOG /
QUARANTINED / NOT ENDORSED, keyed on file + normalised claim text, never
line numbers. A malformed quarantine **raises** rather than becoming
silently empty, because an empty quarantine is indistinguishable from a
healthy gate.

**eli_data.** `pyproject.toml` declared `bias_data` and `dpv_data` but
not `eli_data`, so the wheel omitted the ELI snapshot.
**This defect was mine** (introduced 27 Jul, pre-programme commit).

## 4. THE IMMEDIATE NEXT TASK — 1.5b batch pack

**One batch, 42 pairs. Owner approval required before ANY public surface
changes.** Full triage is in STATE.md. Owner-set disposition bars:

- **83.5% precision — first, and it FAILS the bar at five of eight
  locations.** The auditor is clean (not allowlisted; artefact-verified
  from `PRECISION.json`), but the bar is that **N=115 and single-labeller
  provenance are visible or one link away at every point of use**.
  Single-labeller is disclosed in exactly **one** place repo-wide:
  `benchmarks/README.md:198`.
  PASS: `README.md:246`, `benchmarks/README.md`.
  **FAIL:** `docs/MODEL_CARD.md:143` (links `METHODOLOGY.json`, which has
  no labeller field), `docs/TRUST.md:157`,
  `docs/examples/exec-summary-sample.html:89`,
  `scripts/exec_summary.py:225`, and worst — **`site/about.html:132`, a
  bare "Published precision on a random corpus: 83.5%" with no N, no
  labeller, no link, on a public page.**
  **Do not strip the number**; its successor is Phase 3's corpus.
  Also: version attribution splits, v1.7.4 on README/TRUST vs v1.7.0 on
  the artefact and both exec summaries (finding F20).
- **Class 1, progress-bar percentages (~30 pairs): DERIVE OR REMOVE.**
  "Corrected" may **not** mean decorating an unmeasured number with a
  citation. A percentage stays only with a defined numerator and
  denominator generated from measured data (site_facts pattern,
  test-backed). "30% of Article 14" has no honest denominator. Options:
  derived counts ("4 of 7 requirements mapped", computed from crosswalk
  data), qualitative tiers, or removal. **The approval pack must show the
  proposed replacement rendering — this changes the landing page's face.**
  Separately, log "unmeasured coverage percentages on the most public
  surfaces" in the severity list: predates the programme, and the
  repaired gate now catches the class (Phase 7 evidence both ways).
- **Class 2, blog statistics (~9 pairs): verified = reproducible or
  externally cited.** Methodology plus data or scripts sufficient to
  reproduce, or an external primary source. **A post asserting its own
  number is not a source for that number.** Where artefacts do not exist,
  the honest disposition is an annotation saying so, or a correction.
- **Class 3, hypotheticals (~3 pairs): rewrite so the framing is explicit
  in the sentence itself.** If an exemption is still needed it must be
  **typed (`ILLUSTRATIVE`)**, constrained to framed sentences, carry a
  control proving a factual claim cannot ride it, and stay **distinct
  from the shrink-only quarantine**. The constraint is non-negotiable;
  the design is yours to propose in the pack.

The quarantine must be **empty before Phase 6/8 publishes anything** —
quarantined items would fail the every-number-traces sweep regardless.

## 5. PHASE 1 FINDINGS (F1-F20)

Full detail in `CODE_REVIEW.md`; severity table in `STATE.md`.
**[V]** = I verified personally. **REPORTED** = carried on a subagent's
evidence and **NOT independently verified** — verify before acting.

**Resolved in 1.5:** F1 [V], F6, F7 [V], F13a `eli_data` [V].

**Still open, HIGH:**
- **F2** `doctor` prints `pip install regula[ast]`; the distribution is
  `regula-ai`, and **`regula` is a real unrelated PyPI package** (Tkinter
  wrapper, v0.1.2). Following Regula's own advice installs a stranger's
  package. 18 occurrences repo-wide. [V]
- **F3** Default install silently downgrades JS/TS from AST to regex
  (tree-sitter is an optional extra) while `docs/TRUST.md` claims full
  AST. On a default install **7 of 8 languages are regex-only**. [V]
- **F4** CycloneDX ML-BOM **fails official schema validation** —
  `modelCard.modelParameters.owner` is not permitted, and was never valid
  in 1.6 either. `scripts/sbom.py:550`. [V]
- **F5** **183 of 391 tier regexes (46.8%) are exercised by no test
  input** — unguarded, not broken. Includes the new Article 5 NCII
  prohibition. Re-measure with
  `python3 docs/improvement/measure_pattern_reach.py`. [V]
- **F8** `regula check` never uses the AST engine; two unreconciled
  detectors over the same code. [REPORTED]
- **F9** Scan cache keys lack a project root, so provenance may replay
  across projects and defeat `--scope`. **[REPORTED — reproduce before
  fixing; owner instruction: minimal failing case or downgrade.]**
- **F10** No test validates any generated artefact against a published
  schema. [V]
- **F11** Precision corpus is **Python-only**; recall never measured. [V]
- **F12** The auditor's own CI entry points (`verify_facts`, `main`) are
  untested. [REPORTED]

**Still open, MEDIUM/LOW:** F13b `scripts/dashboard/` missing from the
wheel so `api-server` has no dashboard [V] · F14 crosswalk 108 days
stale, does not consume the delta-log, `owasp_agentic` missing from
articles 11 and 12 [V] · F15 `test_questionnaire_scoring.js` is a full
data copy, already drifted, never executed [REPORTED] · F16 superlinear
scan performance, 44ms/file at 13 files vs 299ms/file at 222 [V] · F17
README mismatches: `--ci` gives no SARIF, `demo` does not need the clone,
jurisdiction crosswalk is EU-only [REPORTED] · F18 zero SPDX headers
despite a composite licence [REPORTED] · F19 `ci_heal.py` (588 lines)
dead [REPORTED] · F20 version-attribution contradiction [V].

**THE CENTRAL STRATEGIC FINDING.** All 24 high-risk false positives are
**semantic, not lexical**. The firing patterns use the statute's own
words — "task allocation" is Annex III 4(b) language that means compute
scheduling in ML code. **Regex tightening cannot fix this class without
destroying recall.** Any plan whose detection lever is "better regexes"
should be rejected at Phase 4. The fix space is context: package-level
domain classification, co-occurrence requirements, path scoping, or an
optional semantic verification tier.

## 6. MY OWN ERRORS — all four, with the rule that came out of them

Recorded because the honesty requirement outranks how the record reads,
and because Phase 6 requires an anti-gaming audit.

1. **F7 overstated by two orders of magnitude.** I published a 237-line
   coordinate error with a misquoted snippet. Real drift is **1-3 lines**
   and nothing was misquoted. Cause: read multi-file auditor output and
   attributed one file's finding to another. Caught by building the
   fixture the fix required. Severity revised HIGH -> MEDIUM.
2. **Claimed `verify_seo` gated CI.** It is untracked, in `.gitignore`,
   and in no workflow. I trusted the prior handover's prose instead of
   grepping `.github/`.
3. **Cascaded the test count during Phase 0**, whose constraint is
   "change nothing", and called it routine maintenance. Reverted at
   `a9ad2e8`; logged as a deviation.
4. **Measured the reconciliation chain on a broken rig.** Reported 185
   and 168 unsourced findings from patched **copies** run out of the
   scratchpad; `REPO_ROOT` derives from module location, so repo-file
   citations failed and sourced paragraphs counted as unsourced.
   **185 was never a state the repo was in.** A later "17" correction
   drew on the same bad pair and is also wrong.

**Common root:** the measuring rig was not identical to the thing
measured. **Rule now in force: measure in place, one variable at a time,
and never trust a number produced by a copy.**

**Two process deviations, both from `git add -A`:**
- The count manifest and its test landed in `140e7fb` instead of the
  count-correction commit; that message does not mention them.
- **The F1 code landed in `8a5888d`, a checkpoint commit whose message
  states F1 was NOT landed** — the message contradicts its own contents.

History is immutable; both are disclosed in `fd212fb` and STATE.md.
**Do not use `git add -A` in this programme.** Stage explicitly.

## 7. THE RECONCILED CHAIN (correct figures)

Measured in place, real file, real `REPO_ROOT`, 56 site pages,
occurrence-level in both columns:

| stage | claims | unsourced |
|---|---|---|
| S1 pre-F6 (`59ac25b`) | 182 | 0 |
| S2 + percent detection | 411 | 61 |
| S3 + CSS fence | 370 | 45 |
| S4 + quarantine (current) | 370 | 0 |

`unsourced` is a subset of `claims` at every stage. Percent detection
surfaces 61 findings; the fence removes 41 claims and **16** findings;
quarantine holds 45 occurrences = 42 unique pairs.

## 8. SCORING — working numbers only

Phase 0 re-measured the rubric anchors (measured-over-embedded).
**Provisional aggregate 52.3 against the programme's assumed 57**, driven
by Detection 42 -> 38 and Trust 92 -> 72.

**All mid-programme movements are WORKING NUMBERS.** The Phase 7
independent scorer arbitrates, **including over my own 92 -> 72
movement**. That movement rested on three legs; leg three (F7) has since
been corrected downward, so direction is intact but **the level is
deliberately not recomputed**. Annotated in both score locations.

## 9. VERIFICATION STATE (measured at branch tip, 28 Jul)

| Gate | Result |
|---|---|
| `python3 -m pytest tests/ -q --collect-only` | **2,349 collected** |
| Custom runner `python3 tests/test_classification.py` | **1386 / 0 / 963**, ten consecutive captured runs |
| `python3 scripts/claim_auditor.py --verify-facts` | **rc=0**, 137 refs across 16 files |
| Auditor over 56 site pages | 370 claims, **0 unsourced** (45 quarantined) |
| `python3 scripts/site_integrity.py` | OK |
| `python3 -m scripts.cli self-test` | rc=0, 6/6 |
| Phase 1.5 guard suites (27 tests) | all pass |
| ruff F821/F811 on `scripts/`, `tests/` | clean |

Notes: `verify_seo.py` passes but is **untracked and gates nothing**. The
21 ruff findings in `benchmarks/synthetic/fixtures/` are intentional and
pre-existing. A full `pytest tests/ -q` run takes ~15 min and was last
green before the F1 rebind; **re-run it early next session** to confirm
the corrected collection executes clean end to end.

**F1 WATCH ITEM, OPEN.** An early post-fix run reported `1,380 passed, 1
failed` with function count intact at 963. Did not reproduce across ten
runs; **failure text never captured** (scrolled through a pipe), so the
failing test is **unknown**. Classified as an unreproduced transient,
**not a diagnosis**.
Repro: `timeout 2400 python3 tests/test_classification.py > run.txt 2>&1`
(redirect to a file; do not pipe, or the failure line is lost again).

## 10. STANDING RULES (owner-set, non-negotiable)

- **Never suppress or dismiss a security alert.** Leave false positives
  open and explain them. The red PR CodeQL check is accepted.
- **No owner personal information in the repo, of any kind.** (REDACTED
  ON RELOCATION, 28 Jul 2026. This rule was previously written naming one
  specific personal category. Naming it put that detail into a public
  repository, which is the thing the rule exists to prevent. The general
  form above is the rule and is strictly stronger.)
- **No em dashes** in repo copy, commits, docs or replies.
- **All three locales (EN/DE/PT-BR) in the same change.** New DE/PT-BR
  prose needs competent-speaker sign-off.
- **Region pages `site/regions/*.html` are GENERATED** from
  `content/regulations/*.py`; never hand-edit (`uae.html` and
  `regulations.html` are hand-maintained exceptions).
- **Run the control before reporting a result.** A blank gate is not a
  green gate; a piped exit code is not an exit code (use PIPESTATUS).
- **Stdlib-only core, offline by default, no telemetry.** Optional
  networked features are extras, off by default, with an ADR.
- **Never commit to `main`; no force-push; no history rewrite.**
- **Stage explicitly; no `git add -A`** (see §6).
- Owner deliverables go to the Downloads folder on the Windows side of
  the WSL mount. (REDACTED ON RELOCATION, 28 Jul 2026: the literal path
  was recorded here and contains a personal Windows username.)
- Programme principles (evidence tags, loop caps of 3, stop-and-ask
  gates, no metric gaming) are in `PROGRAMME.md` and bind all work.

## 11. OWNER DECISIONS

**1. Should `.claude/` be tracked? CLOSED 28 Jul 2026: relocate, do not
track wholesale.** Executed. Programme documents moved to
`docs/improvement/`, the DPVCG draft to `docs/`, and `.claude/rules/` and
`.claude/commands/` un-ignored by specific subpath while
`settings.local.json`, `skills/`, `agents/` and all session scratch stay
ignored. See §12.
**The sensitivity carve-out was RATIFIED by the owner on 28 Jul 2026.**
The three strategy documents stay at `getregula-internal/`, and the
calibration (competitor names public, positioning private) is accepted as
recorded. The deviation from the literal instruction is closed as
approved, not merely disclosed.

**2. Do the two `git add -A` deviations need more than disclosure? CLOSED
28 Jul 2026: disclosure stands, plus two additions.** No history rewrite.
`docs/improvement/COMMIT_ERRATA.md` now carries both entries where a
bisecting reader will look, and `.claude/rules/git.md` makes the staging
rule structural rather than a promise that dies at the next context reset.

**3. 1.5b batch pack. STILL OPEN.** Must be approved before any public
surface changes, including the landing-page rendering replacements.

**4. Backup for internal-only material. STOPGAP AUTHORISED and executed
28 Jul 2026.** `getregula-internal/` is now a **local-only git
repository**: `git init`, initial commit `756fb43`, nine files tracked,
**no remote and never to have one**. A `pre-push` hook in
`.git/hooks/pre-push` refuses every push as a hard guard; do not remove
it. `docs/moat-research.md` (32,911 bytes, previously gitignored and
historyless) was moved into it. Grep before the move found only two
references, both incidental (the `.gitignore` line excluding it, and a
mention in §12 of this file as an example of the not-public class), so
nothing broke and no pointer stub was needed.
**The private-remote decision remains open and stays on
`OWNER_ACTIONS.md`.** A local repo gives history but still lives on one
disk. This is a stopgap, not the answer.

Also open from `docs/improvement/OWNER_ACTIONS.md`, none started: post the
DPVCG comment (recommendation: include concrete concepts first); recruit
annotators 2 and 3 (**the binding constraint on the corpus asset** — a
multi-week social task, not reducible to one day); Zenodo account and
dataset licence; BSI ART/1 enquiry (costs UNVERIFIED — ask BSI); GSC
re-auth (`invalid_grant`). **Closed:** the EUR-Lex check — two
independent retrievals confirmed Regulation (EU) 2026/1744 contains **no
agentic-AI category and no 2030 date**, and Regula asserts neither.

## 12. WHERE THINGS ARE (rewritten 28 Jul 2026 after the relocation)

**Tracked programme documents** in `docs/improvement/`:
`PROGRAMME.md` (contract, verbatim) · `STATE.md` (**resume file**) ·
`BASELINE.md` · `CODE_REVIEW.md` · **`HANDOVER.md` (this file)** ·
**`PHASE0_VERIFICATION.md`** (§E redacted) ·
**`OWNER_ACTIONS.md`** (§6 redacted) · **`COMMIT_ERRATA.md`** ·
`fp_taxonomy.json` · `measure_pattern_reach.py`.

**Tracked elsewhere:** `docs/dpvcg-contribution-draft.md` (moved from
`.claude/`, unredacted) · `.claim-quarantine.json` ·
`data/published_count_manifest.json` · `docs/UX-REVIEW-2026-07.md` ·
`.claude/rules/*.md` (five, plus the new `git.md`) ·
`.claude/commands/*.md` (three) ·
Phase 1.5 guards: `tests/test_collection_integrity.py`,
`test_claim_auditor_coords.py`, `test_claim_auditor_percent.py`,
`test_claim_quarantine.py`, `test_packaged_data.py`,
`test_published_count_manifest.py`.

**Held OUTSIDE the repository, deliberately, at `getregula-internal/`:**
`research-sweep-2026-07.md` · `moat-programme-2026-07.md` ·
`competitive-intelligence-2026-07.md` (extracted from the two redacted
files above) · `README.md` explaining the split.
**Why:** `github.com/kuzivaai/getregula` is **public** (verified 28 Jul
2026), these documents are competitive and commercial strategy, and the
repo's own `.gitignore` already declares that class not-public
(`docs/competitor-analysis.md`, `docs/moat-research.md`, `analysis/`,
`planning/`). Note the calibration: competitor **names** were NOT
redacted anywhere, because the repo already names its comparison set
publicly in `benchmarks/headtohead/PREREGISTRATION.md` and `adapters.py`.
What was held back is positioning work: pricing intel, star counts,
Regula's absence from a competitor's comparison page, and the ranked
commercial strategy. This directory has no version control and no backup
(open decision 4, §11).

**Still in `.claude/` and still ignored:** `handover.md` (old, superseded
by this file) · `settings.local.json` · `skills/` · `agents/` ·
`worktrees/` · pre-programme planning documents from June 2026. These
remain one `git clean` from gone. That is a deliberate scope boundary,
not an oversight: the owner's decision covered the programme's documents,
and the June material is superseded. Flag if any of it should be kept.

**Already delivered to the owner** (Downloads folder, Windows side):
`Regula-Phase0-Verification-2026-07-27.docx`,
`Regula-Moat-Programme-Session-Report-2026-07-27.docx`,
`Regula-Business-Dossier-2026-07-27.docx`. These are gitignored by
`*.docx` and are not in the repo.
