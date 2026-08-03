---
globs:
  - "**/*"
---

# Quality Standards

These rules override any default behaviour that trades quality for speed. They apply to every file, every change, every session.

## No quick fixes or partial work

- Never apply a fix to one path (e.g. questionnaire) without checking whether the same logic exists in parallel paths (e.g. scanner). If the same pattern appears in `getNextSteps()` and `getScanNextSteps()`, both must be updated.
- Never copy data structures (questions, scoring logic, pattern arrays) into test files. Tests must import from, parse, or verify against the source of truth. A manually-maintained copy WILL drift silently. If the source cannot be imported directly, write a sync check that compares the test's copy against the source at test time.
- Never change the semantics of a stateless encoding (URL parameters, JSON exports) without versioning. If a field's meaning changes, old encodings must be decoded correctly. Add a version marker and migration path.
- When adding a feature to one locale (EN), apply it to ALL locales (DE, PT-BR) in the same change. Do not commit locale-incomplete work.

## Always choose the best approach

- Default to the approach that solves the root cause, not the symptom.
- If there are multiple credible approaches, research them, weigh trade-offs explicitly, and choose based on this project's constraints. Document why in a comment if non-obvious.
- Do not optimise for token usage, context window, or time spent. Optimise for correctness, completeness, and maintainability.
- If a fix requires touching 15 files across 3 locales, touch all 15 files. Partial application is worse than no fix.

## Verification is not optional

- Every change must be verified with evidence (test output, grep result, rendered page). "I believe this works" is not verification.
- After fixing something, re-run ALL relevant test suites, not just the one for the changed file.
- Use `playwright-cli` to verify browser rendering when changes affect HTML/CSS/JS in site pages.
- Run `python3 scripts/claim_auditor.py` on any page where numeric claims appear.
- Cross-locale changes must be verified with a parity check (grep for the changed logic across all locale files).

## Audit before commit

- Before claiming work is done, run a sceptical self-audit: assume something is broken and try to find it.
- Check for: parallel paths that weren't updated, data copies that drifted, URL/export format backward compatibility, CLI commands shown to non-technical users, locale parity, test coverage gaps.
