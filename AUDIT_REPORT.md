# Regula Audit Report — 14 April 2026

## Summary

| Severity | Count |
|----------|-------|
| CRITICAL | 0 |
| HIGH | 8 (52 oversized functions, not 30) |
| MEDIUM | 10 (13 silent exceptions, not 7) |
| LOW | 5 (1 retracted) |

---

## CRITICAL — None

---

## HIGH

### H1. `cli.py` monolith — 3,246 lines, 52 commands
`scripts/cli.py` — 52 `cmd_*` functions, a 544-line `_build_subparsers`, and a 251-line `cmd_check`. Logical groupings exist (scanning, reporting, compliance, governance, utilities) but are not separated into modules.

### H2. 52 functions over 100 lines
Top offenders:
- `generate_documentation.py:241` `generate_annex_iv` — 590 lines
- `cli.py:2593` `_build_subparsers` — 547 lines
- `ast_engine.py:217` `_tree_sitter_parse` — 503 lines
- `report.py:715` `generate_html_report` — 377 lines
- `conform.py:251` `generate_conformity_pack` — 323 lines
- `report.py:276` `scan_files` — 311 lines

### H3. 68/78 script modules have no dedicated test file
`test_classification.py` (6,811 lines, 431 tests) tests almost everything via 57 imports. No structured per-module coverage. Only 10 modules have dedicated test files: `bias_bbq`, `bias_report`, `bias_stats`, `build_regulations`, `gpai_check`, `mcp_server`, `register`, `scan_cache`, `session`, `telemetry`. Key untested modules: `report.py`, `compliance_check.py`, `evidence_pack.py`, `remediation.py`, `dependency_scan.py`.

### H4. `test_classification.py` is a 6,700-line monolith
Simultaneously the custom test runner entry point, the primary test file, and the wiring harness for 4 external test modules. 431 of 928 tests live here.

### H5. Command count 53 on landing pages — should be 52
- `README.md:265`, `index.html:102,489`, `de.html:99,304`, `pt-br.html:99,305` — all say 53
- CLAUDE.md correctly says 52. `regula --help` confirms 52.

### H6. CycloneDX version conflict — marketing says 1.7, code says 1.6
- `README.md:85`, `index.html:459,500`, `de.html:313` — "CycloneDX 1.7"
- `cli.py:1977,2966`, `conform.py:463` — "CycloneDX 1.6"

### H7. 130 weak `len > 0` / `len >= 1` assertions
Tests that assert "at least one result" but never verify the result is correct. 130 instances across the test suite. Highest density in:
- `test_ai_codegen.py` — 12 instances
- `test_classification.py` — 11+ instances
- `test_build_regulations.py` — 1 instance
- `test_gpai_check.py` — 1 instance
- Remainder spread across other test files

### H8. 1 zero-assertion test remaining
- `test_classification.py:2782` `test_ai_security_no_false_positive_safe_torch` — calls code, asserts nothing

---

## MEDIUM

### M1. 13 `except Exception:` blocks with silent fallbacks (not bare `pass`, but no logging)
- `bias_bbq.py:144`
- `bias_eval.py:178,212,287`
- `cli.py:107,549,768,942,1373,3233`
- `feed.py:141`
- `site_facts.py:140,149`

### M2. 78 public functions with no return type hints
All 52 `cmd_*` functions plus 26 others including `json_output`.

### M3. Circular import smell: `cli.py` ↔ `bias_report.py`
Both guard with runtime imports. Root cause: `VERSION` should live in `constants.py` (it already does — `bias_report.py` should import from there instead of `cli`).

### M4. `site_facts.json` stale
- `total_functions: 809` — actual is 831 (grep) / 928 (pytest)
- `tier_regexes: 358` — should be 403 (missing governance + GPAI)
- Per-file counts incomplete (3 bias test files missing, `test_classification.py` count stale)

### M5. CHANGELOG dual unreleased headers
Lines 9-12 say "v1.7.0 (unreleased)", lines 14+ say "[Unreleased]" — unclear if same release.

### M6. CHANGELOG "926 tests" stale
Lines 22 and 184 — should reflect current 928 (pytest).

### M7. `cmd_feedback` wired to 4 subparsers
`cli.py:3036,3043,3048,3050` — running `regula feedback` with no sub-subcommand defaults to `false-positive`, likely unintentional.

### M8. Art 15 gap semantics
`regula gap` reports Art 15 score=100 but gaps=33 — contradictory display.

### M9. 3 manual JSON envelopes still bypass `json_output()` for file output
`cli.py:594` (report file), `cli.py:905` (feed file), `cli.py:1951` (benchmark file). Stdout paths were fixed, but file-write paths still build envelopes manually.

### M10. Duplicated assert helpers across 14 test files
Every file redefines `assert_eq`, `assert_true`, etc. from scratch. Should be a shared `tests/helpers.py`.

---

## LOW

### ~~L1. RETRACTED~~ — `format_mapping_text` at `cli.py:189` is NOT unused (used in `framework_mapper.py:314`, `pdf_export.py:580,584`)
### L2. Dead functions: `term_style.py:54` `bold`, `term_style.py:62` `dim`
### L3. Redundant `cmd_config` wiring (parent + subparser both set `func=cmd_config`)
### L4. 4 `# type: ignore` comments (2 acceptable, 1 real type mismatch in `log_event.py:37`)
### L5. 79 `Path(...).resolve()` calls — repeated pattern, not a bug
### L6. 1 SystemExit caught without checking exit code (`test_register.py:373`)
