# Tech Debt Audit Report — Regula

**Date:** 2026-04-01
**Scope:** Full codebase tech debt assessment
**Trigger:** /audit /tech-debt

## Summary

| Severity | Count |
|----------|-------|
| CRITICAL | 0 |
| HIGH | 2 |
| MEDIUM | 5 |
| LOW | 4 |
| **Total** | **11** |

All tests pass: 639/639, self-test 6/6, doctor 8/8.

---

## HIGH

### H-1: DE and PT-BR landing pages are stale

`de.html` and `pt-br.html` still reference:
- "29" commands (now 30)
- "August 2026" as a fact (EN version now hedges for Omnibus)
- Old hero copy, old feature grid, old framework list
- No cost positioning, no `--explain` demo, no provider/deployer section

These pages will contradict the EN version when published.

**Fix:** Rewrite DE/PT-BR to match EN, or add a note that they're outdated.

### H-2: FULL_INSPECTION.md references stale counts

`docs/FULL_INSPECTION.md` references "29 subcommands" in 6 places, "1,421 LOC" for cli.py (now ~1,490), and "438 tests" (now 639 assertions across 259 functions). This is the "single source of truth" document per the handover, so stale numbers here propagate.

**Fix:** Update the 6 occurrences, or add a caveat that it's a point-in-time snapshot.

---

## MEDIUM

### M-1: test_classification.py is 4,950 lines (monolith)

Single test file with 259 test functions and a manual test list of ~170 entries. Adding tests requires both writing the function AND adding it to the manual list — easy to forget one. The manual list pattern is fragile; pytest discovers tests automatically.

**Debt:** Not blocking, but every new feature adds ~50 lines. At current growth rate this file hits 6K+ lines within months.

**Fix (future):** Split into test_prohibited.py, test_high_risk.py, test_explain.py, test_docs.py, etc. Keep the manual runner as a thin wrapper that imports from submodules. Not urgent — the file works.

### M-2: cli.py is 1,489 lines (monolith)

All 30 commands in one file. CLAUDE.md explicitly says "Do not refactor cli.py's monolith structure unless explicitly asked." Respected. But this is tech debt by design.

**Debt:** Each new command adds ~40-60 lines. Adding `--explain` and `--completion` added ~40 lines of inline logic that could live in their respective modules.

### M-3: docs/getregula_annex_iv.md is generated output checked into docs/

The `regula docs` command regenerated this file during the session. It contains machine-specific paths (`/home/mkuziva/getregula`) and timestamps. It should either be .gitignored or generated on demand, not committed.

**Fix:** Add `docs/getregula_annex_iv.md` to .gitignore, or don't commit it.

### M-4: 12 uncommitted files from this session

8 modified + 4 untracked files. This is a full v2.0 feature set without a single commit. Risk of losing work if the session ends.

**Fix:** Commit the work.

### M-5: Effort estimates in article_obligations.yaml are unsourced

The YAML header now correctly disclaims these as "indicative ranges... NOT sourced from a specific study." But users consuming the `--explain` output see "40-60h" without this caveat. The CLI output presents these as authoritative.

**Debt:** Could mislead users into thinking these are industry-standard figures. They're reasonable estimates but unverifiable.

**Fix:** Add a one-line caveat in the `format_explanation()` output near the effort totals, e.g., "Effort estimates are indicative — actual hours vary by system complexity."

---

## LOW

### L-1: No TODOs or FIXMEs in codebase

Zero grep hits. This is good hygiene, not a finding. Noted for completeness.

### L-2: `main()` function exists in 21 scripts

Each script has its own `main()` for standalone execution. Not a problem — standard Python pattern. But it means 21 entry points that need to stay working.

### L-3: `visit_*` methods duplicated in ast_analysis.py

`visit_FunctionDef`, `visit_Call`, `visit_AsyncFunctionDef` appear multiple times because they're defined in separate AST visitor classes. This is correct OOP — different visitors for different analysis phases. Not real duplication.

### L-4: Version string hardcoded in generate_documentation.py

`generate_documentation.py` line ~214 hardcodes "Regula v1.2.0" in the Annex IV output. Should import VERSION from cli.py instead.

---

## Not Debt (Verified Clean)

- Zero orphaned scripts (every module is imported by something)
- Zero dependencies in pyproject.toml (only optional-dependencies)
- Version consistent across cli.py, pyproject.toml, index.html (all v1.2.0)
- No hardcoded paths or debug breakpoints in scripts/
- sbom.py properly delegates to dependency_scan.py (not real duplication)
- Print statements are all in CLI output paths (not debug prints)
