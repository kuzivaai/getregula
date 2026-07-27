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

## IN PROGRESS

- Phase 0 BASELINE.

## NEXT

1. Commit prior 27 Jul moat work on this branch (anchors BASELINE to a SHA).
2. Phase 0 measurements -> `docs/improvement/BASELINE.md`.
3. Phase 1 exhaustive code review.

## OPEN QUESTIONS

- None blocking.

## ESCALATIONS

- None yet.

## DRIFT CHECK

Is the current activity the highest-value path to the rubric? **Yes.**
Phase 0 measurement is the precondition for Principle 2 (measured beats
embedded) and for every later claim.
