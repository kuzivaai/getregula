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

- **Phase 1 exhaustive code review.** Done so far: the FP taxonomy
  (`docs/improvement/fp_taxonomy.json`, commit `1356f97`) — all 24
  high-risk false positives traced to causal patterns and classified.
  Remaining Phase 1 sections: architecture/call-graph map, per-language
  regex-quality audit, crosswalk audit, evidence-output spec validation,
  test-suite audit, corpus audit, security pass, repo hygiene.
- Phase 0 coverage measurement (background run, still in flight).

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

## NEXT

1. Record coverage in BASELINE §9 when the run lands.
2. Finish Phase 1 sections listed above -> `CODE_REVIEW.md`.
3. Phase 2 research validation (cards inherit the completed 27 Jul
   primary-source verification where applicable, and say so).

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
