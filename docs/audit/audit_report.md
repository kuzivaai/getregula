# Regula Technical Audit Report

**Date:** 2026-03-27
**Auditor:** Automated code audit (Claude Opus 4.6)
**Version audited:** 1.1.0
**Commit:** HEAD of `/home/mkuziva/getregula/`

---

## Executive Summary

Regula is a genuinely functional EU AI Act risk indication tool with real classification logic, working audit trails, and broad feature coverage across 20 Python modules and 109 tests. However, it has one crash-on-import bug (unconditional `import fcntl` in classify_risk.py breaks Windows), a SARIF version mismatch (reports "1.0.0" while pyproject.toml says "1.1.0"), a stale roadmap that lists AST analysis as "v2.0 planned" when it already exists, and the test suite uses a custom test harness instead of unittest/pytest, which means failures are silent in CI unless the exit code is checked. The tool is honest about its limitations (pattern-matching, not legal classification) but the README's "105+ tests" claim is now 109 tests, and several edge cases in dependency parsing and JS/TS analysis are unhandled.

---

## Phase 1: Baseline Inventory

### Lines of Code

| File | Lines | Purpose |
|------|-------|---------|
| `scripts/compliance_check.py` | 1,026 | Compliance gap assessment (Articles 9-15) |
| `scripts/ast_analysis.py` | 870 | Python AST-based code analysis |
| `scripts/benchmark.py` | 777 | Precision/recall validation |
| `scripts/classify_risk.py` | 673 | Risk indication engine |
| `scripts/report.py` | 657 | HTML + SARIF report generator |
| `scripts/dependency_scan.py` | 618 | Supply chain security scanner |
| `scripts/cli.py` | 611 | Unified CLI |
| `scripts/ast_engine.py` | 535 | Multi-language AST engine |
| `scripts/generate_documentation.py` | 512 | Annex IV + QMS scaffold |
| `scripts/feed.py` | 460 | Governance news feed |
| `scripts/discover_ai_systems.py` | 407 | AI system discovery + registry |
| `scripts/install.py` | 300 | Multi-platform hook installer |
| `scripts/questionnaire.py` | 274 | Context-driven risk questionnaire |
| `scripts/log_event.py` | 288 | Audit trail (hash-chained) |
| `scripts/init_wizard.py` | 203 | Guided setup |
| `scripts/framework_mapper.py` | 202 | Cross-framework mapping |
| `scripts/credential_check.py` | 197 | Secret detection |
| `scripts/session.py` | 188 | Session risk aggregation |
| `scripts/baseline.py` | 174 | CI/CD baseline comparison |
| `scripts/timeline.py` | 164 | EU AI Act enforcement dates |
| **Total scripts/** | **~8,136** | |
| `hooks/pre_tool_use.py` | 248 | PreToolUse hook |
| `hooks/post_tool_use.py` | 63 | PostToolUse hook |
| `hooks/stop_hook.py` | 98 | Session summary hook |
| **Total hooks/** | **~409** | |
| `tests/test_classification.py` | 1,749 | Test suite |
| **Grand total Python** | **~10,294** | |

### Test Count

- **109 test functions** (grep `def test_` count)
- README claims "105+ tests" -- accurate but stale (should be 109)
- Custom test harness (manual `passed`/`failed` counters) -- not unittest or pytest
- CI runs on Python 3.10, 3.11, 3.12 via GitHub Actions

### File Count

- 20 Python scripts in `scripts/`
- 3 Python hooks in `hooks/`
- 1 test file
- 2 test fixtures (sample projects)
- 5 YAML reference files
- 1 CI config

---

## Phase 2: Per-Module Assessment

### 2.1 Risk Classification (`scripts/classify_risk.py` -- 673 lines)

**1. Does it actually classify?**
YES. The `classify()` function is fully implemented with a priority chain: prohibited -> policy overrides -> AI detection -> high-risk -> limited-risk -> minimal-risk. This is not a stub.

**2. Are all 8 Article 5 prohibited patterns implemented?**
YES. All 8 are present with correct Article references:
- 5(1)(a) Subliminal manipulation -- 3 regex patterns
- 5(1)(b) Exploitation of vulnerabilities -- 3 patterns
- 5(1)(c) Social scoring -- 4 patterns
- 5(1)(d) Criminal prediction -- 4 patterns
- 5(1)(e) Facial recognition scraping -- 3 patterns
- 5(1)(f) Emotion inference restricted (workplace/school) -- 5 patterns
- 5(1)(g) Biometric categorisation (sensitive) -- 5 patterns
- 5(1)(h) Real-time biometric public -- 4 patterns

Each includes conditions, exceptions, and Article references. The conditions text is legally nuanced (e.g., criminal prediction notes the "solely based on profiling" requirement). This is well done.

**3. Are all Annex III high-risk categories covered?**
YES. 10 categories counted:
1. Biometrics (Category 1)
2. Critical infrastructure (Category 2)
3. Education (Category 3)
4. Employment (Category 4)
5. Essential services (Category 5)
6. Law enforcement (Category 6)
7. Migration (Category 7)
8. Justice (Category 8)
9. Medical devices
10. Safety components

This exceeds the 8 explicit Annex III categories by including medical devices and safety components (which are covered under other Union harmonisation legislation, referenced in Article 6). Appropriate.

**4. Confidence scoring algorithm?**
Reasonable but simple. Base score by tier (prohibited=75, high_risk=55, limited_risk=40, minimal=15) + match bonus (8 per match, capped at 15) + AI indicator bonus (10 if AI-related). Max 100. This is sensible and documented.

**5. Performance on 10,000-file codebase?**
The `classify()` function runs regex on a single text string -- fast. The file scanner in `report.py` uses `os.walk` with directory skipping and only reads code files with AI indicators. For 10,000 files, performance would be acceptable but not optimised (no parallelism, no streaming).

**6. What would break it?**
- **CRITICAL BUG: `import fcntl` on line 16 of classify_risk.py.** This is unconditional and will crash on Windows with `ModuleNotFoundError`. fcntl is not used in this file at all -- it is a leftover import. The log_event.py file handles cross-platform correctly; classify_risk.py does not.
- Binary files: reads with `errors="ignore"`, which silently produces garbage. Not a crash but useless results.
- Unicode: regex patterns use `re.IGNORECASE` inconsistently -- some patterns use it, the `check_prohibited` etc. functions lowercase the text first. This works but is redundant.
- Very large files: reads entire file into memory. No size guard.

### 2.2 AST Engine (`scripts/ast_engine.py` -- 535 lines)

**1. Does Python AST delegation work?**
YES, but with a CRITICAL IMPORT ISSUE. Line 22 uses `from ast_analysis import (...)` without a relative import prefix or sys.path manipulation. This will ONLY work if the script is run from the `scripts/` directory or if `scripts/` is on `sys.path`. Running `ast_engine.py` directly from the project root or as an installed package will fail with `ModuleNotFoundError: No module named 'ast_analysis'`.

The CLI (`cli.py`) works around this by inserting `sys.path` at line 23, but `ast_engine.py` itself does not do this.

**2. Does JS/TS regex fallback parse real-world JavaScript?**
PARTIALLY. Testing the import regex `_RE_IMPORT_FROM` against `import { ChatOpenAI } from '@langchain/openai'`:
- The regex pattern `import\s+(?:.*?\s+from\s+)?['"]([^'"]+)['"]` would match this because `.*?` is non-greedy and `\s+from\s+` will match.
- It correctly extracts `@langchain/openai`.
- However, it would NOT handle: dynamic imports (`import()`), re-exports (`export { x } from 'y'`), or side-effect imports without quotes.
- Arrow function regex misses methods in object literals (common JS pattern).
- Class regex misses TypeScript abstract classes and decorators.

**3. Does tree-sitter integration exist?**
NO. It is a stub. Line 117: `raise ImportError("tree-sitter parsing not yet implemented")`. Even if tree-sitter is installed, it will always fall back to regex. The pyproject.toml lists tree-sitter as an optional dependency, but it cannot actually be used.

**4. What's missing vs. Systima Comply's call-chain tracing?**
The AST engine does single-file data flow tracing within Python (via `ast_analysis.py`), which is genuine and non-trivial. However, it does NOT do:
- Cross-file call chain tracing
- Module-level dependency graphs
- Type inference
- Inter-function data flow
- Any of this for JS/TS (regex only)

### 2.3 Dependency Scanner (`scripts/dependency_scan.py` -- 618 lines)

**1. Does requirements.txt parsing handle all pip formats?**
PARTIALLY.
- Handles: basic `package==1.0`, extras `package[extra]`, comments, continuation lines, hash pinning, inline comments
- DOES NOT handle: `-r` include directives (references to other requirements files), git URLs (`git+https://...`), `--index-url`, `--extra-index-url`, environment markers (`; python_version >= '3.8'`)
- Line 165 skips lines starting with `-`, which catches `-r` but silently ignores the referenced files instead of following them.

**2. Does pyproject.toml parsing work without tomllib?**
YES, via regex. The regex approach is fragile (line 222: `re.finditer(r'dependencies\s*=\s*\[([^\]]*)\]', content, re.DOTALL)`) but will work for the common case. It would FAIL on:
- Dependencies split across multiple TOML tables
- Poetry-style `[tool.poetry.dependencies]`
- Nested TOML with brackets in string values

The optional-dependencies parser (lines 235-258) has dead code: the first loop body is `pass`, and the second pattern only matches `[project.optional-dependencies]` as a single section, not the per-group format.

**3. Does package.json parsing handle workspaces, peerDependencies?**
NO. It only checks `dependencies` and `devDependencies` (line 286). `peerDependencies`, `optionalDependencies`, and workspace configurations are ignored.

**4. How many AI libraries in the detection list?**
Exactly **69 unique entries** in `AI_LIBRARIES` (counted from the set literal, lines 18-62). This is a solid list covering Python ML/DL, LLM providers, LangChain ecosystem, LlamaIndex, classical ML, NLP, local inference, agents, vector databases, MLOps, and some npm packages.

**5. Does compromised package check load advisory YAML?**
YES. `_load_advisories()` (line 425) loads from `references/advisories/` recursively, tries pyyaml first, falls back to the classify_risk YAML parser. Currently one advisory exists (LiteLLM REGULA-2026-001). The version matching is exact-string only (line 506: `dep_version in versions`), so it would miss semantic version ranges.

### 2.4 Compliance Gap Assessment (`scripts/compliance_check.py` -- 1,026 lines)

**1. What does each Article check for?**

| Article | Checks | Method |
|---------|--------|--------|
| **9** (Risk Management) | Files named `risk_*`, content mentioning "risk assessment/register/mitigation", AI-specific risk docs, structured mitigations with status/owner/deadline | File glob + content regex |
| **10** (Data Governance) | Data dictionary/catalog files, data governance content, bias libraries (fairlearn, aequitas, aif360), data validation frameworks (great_expectations, pandera, pydantic) | File glob + code grep |
| **11** (Technical Documentation) | Annex IV files, model cards, system descriptions, Annex IV section headings (needs 3+ of 8), Regula-generated docs | File glob + heading detection |
| **12** (Record-Keeping) | Logging imports (Python logging, winston, pino), monitoring libraries (prometheus, datadog, sentry), AI-specific logging, structured logging patterns, AST logging detection | Code grep + AST analysis |
| **13** (Transparency) | Model cards, capability/limitation docs (needs 2+ of 8 topics), AI disclosure notices in code | File glob + content analysis |
| **14** (Human Oversight) | Oversight docs (human_in_the_loop, approval_workflow, etc.), code oversight patterns (require_approval, review_gate), review-before-action patterns, AST oversight detection | Docs + code grep + AST |
| **15** (Accuracy/Robustness) | Test files/dirs, security configs (.snyk, .bandit), monitoring, performance evaluation, credential management, hardcoded secrets, dependency pinning | Files + code + dep scan |

**2. Are the checks meaningful or superficial?**
MOSTLY MEANINGFUL with some superficiality:
- Article 9: Checking for structured mitigations (status, owner, deadline) is a real quality signal. Good.
- Article 10: Checking for actual bias libraries (fairlearn, aif360) rather than just the word "bias" is solid.
- Article 12: AST integration for logging is genuinely deeper than grep. Good.
- Article 14: The review-before-action regex (`(review|approv|confirm).{0,30}(before|prior)`) is a reasonable heuristic. AST detection of human oversight patterns in Python adds real value.
- Article 13: Could be superficial. Checking for `ai-generated` or `ai-powered` strings in code is a weak signal -- these could be comments, variable names, or actual disclosure notices.
- Article 15: Most comprehensive checker with 5 components. The dependency pinning integration is a genuinely useful addition.

**3. Does AST integration actually work?**
YES, for Python files. Lines 476-494 and 619-636 use `detect_logging_practices` and `detect_human_oversight` from ast_analysis.py. These are wrapped in try/except and fall back gracefully if the module is unavailable. The AST functions are real (verified in ast_analysis.py -- they use actual `ast.NodeVisitor` classes).

### 2.5 Audit Trail (`scripts/log_event.py` -- 288 lines)

**1. Is the hash chain tamper-evident?**
YES, with a documented limitation. `compute_hash()` (line 80) creates a SHA-256 hash of all event fields (excluding current_hash) concatenated with the previous hash. This is a proper hash chain. The code itself acknowledges (line 9) this is "self-attesting" and recommends RFC 3161 timestamping for regulatory evidence.

**2. What happens if file is corrupted mid-write?**
PARTIAL PROTECTION. The write is append-only with file locking (line 121: `open(audit_file, "a")`). If the process crashes mid-write, the last line will be incomplete JSON. The `_read_last_hash` function (line 86) reads line-by-line and would skip an incomplete line IF it fails JSON parsing. But the chain verification (`verify_chain`) would report the broken line as "Invalid JSON". Recovery would require manual removal of the incomplete line.

**3. Can the chain be verified independently?**
YES. `verify_chain()` (line 174) walks all audit files in order, checking: (a) previous_hash matches the last event's current_hash, (b) recomputing the hash matches the stored current_hash. This is independently verifiable by any tool that can parse JSONL and compute SHA-256.

**4. Cross-platform locking?**
YES, correctly implemented. Lines 27-49 use `msvcrt.locking` on Windows and `fcntl.flock` on Unix/macOS with proper conditional imports.

BUT: `classify_risk.py` imports `fcntl` unconditionally on line 16, which WOULD crash on Windows. This is a real bug even though `log_event.py` handles it correctly.

### 2.6 Secret Detection (`scripts/credential_check.py` -- 197 lines)

**1. How many patterns?**
**9 patterns total:**

HIGH confidence (6):
1. `openai_api_key` -- `sk-` prefix, 20+ chars (excludes `sk-ant-`)
2. `anthropic_api_key` -- `sk-ant-` prefix, 20+ chars
3. `aws_access_key` -- `AKIA` + 16 uppercase alphanumeric
4. `google_api_key` -- `AIza` + 35 mixed chars
5. `github_token` -- `gh[ps]_` + 36+ chars
6. `private_key` -- PEM header

MEDIUM confidence (3):
7. `generic_api_key` -- `api_key = "..."` pattern
8. `connection_string` -- `mongodb://`, `postgres://`, etc.
9. `aws_secret_key` -- `aws` near `secret/key` near 40 base64 chars

**2. False positive rate?**
- `sk-` prefix matching for OpenAI is well-designed: excludes `sk-ant-` (Anthropic) and requires 20+ chars.
- `AKIA` is very specific to AWS -- low false positive.
- `generic_api_key` medium-confidence pattern WILL false-positive on test code, config examples, and documentation that contains `api_key = "test_key_for_development_purposes"`.
- `connection_string` medium-confidence is reasonable -- will match legitimate connection strings in config files, which IS a finding.

**3. Comparison to gitleaks/TruffleHog?**
This is explicitly NOT a competitor. The docstring (line 19) states: "This module covers tool inputs only, not general file scanning (use gitleaks/truffleHog/detect-secrets for file-level scanning)." With 9 patterns vs. gitleaks' 150+ or TruffleHog's 800+, this is a focused subset for AI-related credentials. This is an honest scope limitation.

### 2.7 Framework Mapper (`scripts/framework_mapper.py` -- 202 lines)

**1. Does it load the crosswalk YAML?**
YES. `_load_crosswalk()` loads `references/framework_crosswalk.yaml` with pyyaml or the fallback parser. Caches after first load. The crosswalk file exists and contains mappings for all 7 articles (9-15).

**2. Are NIST AI RMF mappings accurate?**
MOSTLY ACCURATE but with caveats:
- Article 9 (Risk Management) -> GOVERN 1.1, MAP 1.1, MAP 5.1, MANAGE 1.1, MANAGE 2.1: These are reasonable mappings. NIST AI RMF's GOVERN and MAP functions do cover risk identification and assessment.
- Article 14 (Human Oversight) -> GOVERN 1.3, MANAGE 2.2: GOVERN 1.3 is described as "Processes for human oversight are defined" -- this is a reasonable mapping but the actual NIST subcategory text may differ slightly from what's in the YAML. The YAML appears to paraphrase rather than quote the official NIST text.
- The YAML notes "Sources: EU AI Act text, NIST AI 100-1, ISO/IEC 42001:2023 Annex A" which is the correct reference document.

**3. Are ISO 42001 mappings accurate?**
PLAUSIBLE. The control IDs used (6.1, A.5.3, A.6.3, A.6.4, A.6.6, A.6.8, A.6.9, A.6.10) are consistent with ISO 42001's Annex A structure. The `iso_42001_mapping.yaml` reference file provides 24 mapped controls with overlap ratings. Cannot verify exact control text without the ISO standard document, but the structure and IDs are consistent with publicly available summaries.

### 2.8 Report Generator (`scripts/report.py` -- 657 lines)

**1. Does HTML render correctly?**
YES, structurally. The HTML is well-formed with:
- Proper DOCTYPE, charset, viewport meta tags
- Inline CSS (single-file, portable)
- All tags properly closed (verified by reading the template strings)
- The HTML uses `escape()` from `html` module on user-controlled content (file names, descriptions)
- Responsive grid layout for summary cards

**2. Does SARIF validate against 2.1.0 schema?**
MOSTLY. The SARIF output includes:
- Correct `$schema` URI pointing to SARIF 2.1.0
- Correct `version: "2.1.0"`
- Proper `runs[].tool.driver.rules` and `runs[].results` structure
- **BUG: SARIF `driver.version` is hardcoded to "1.0.0" (line 595) while pyproject.toml says version "1.1.0"**. This is a version mismatch that should be fixed.

**3. Are dependency and framework sections functional?**
YES. The `generate_html_report` function accepts `dependency_results` and `framework_mappings` parameters and renders them as HTML tables. The dependency section shows pinning score, AI dependency table with status badges, and compromised package alerts.

### 2.9 CLI (`scripts/cli.py` -- 611 lines)

**1. How many commands?**
**17 commands:**
1. `init` -- Guided setup wizard
2. `check` -- Scan files for risk indicators
3. `classify` -- Classify text input
4. `report` -- Generate reports (HTML, SARIF, JSON)
5. `audit` -- Manage audit trail (verify, export, query)
6. `discover` -- Discover AI systems
7. `install` -- Install platform hooks
8. `status` -- Show registry status
9. `feed` -- AI governance news feed
10. `questionnaire` -- Context-driven risk assessment
11. `session` -- Session risk aggregation
12. `baseline` -- CI/CD baseline comparison
13. `docs` -- Documentation scaffold generation
14. `compliance` -- Compliance status management
15. `gap` -- Compliance gap assessment
16. `benchmark` -- Precision/recall validation
17. `timeline` -- EU AI Act enforcement dates
18. `deps` -- Dependency supply chain analysis

(18 total -- I miscounted the subparser registrations.)

**2. Are all commands functional?**
Cannot execute (Bash denied), but from code inspection:
- All commands import their dependencies lazily (inside the function), which is good for startup time
- Several commands delegate by manipulating `sys.argv` and calling the module's `main()` function (lines 125-138 for `report`, 143-156 for `audit`, 159-168 for `discover`). This is hacky but functional.
- The `cmd_report` function replaces `sys.argv` globally (line 125), which means if called programmatically, it would have side effects. Not ideal.

**3. Is help text consistent?**
YES. The epilog (lines 426-452) provides comprehensive examples for all major commands. Each subparser has a `help` string.

**4. Error paths?**
- `cmd_classify` handles missing input gracefully (line 107: checks stdin, file, input)
- `cmd_check` uses `Path.resolve()` which will fail with a clear error on non-existent paths
- Exit codes are documented: 0=pass, 1=high-risk (strict), 2=prohibited/compromised

---

## Phase 3: README vs Reality Gaps

| README Claim | Reality | Verdict |
|-------------|---------|---------|
| "105+ tests" | 109 test functions | STALE -- should say 109 |
| "All 8 Article 5 categories are detected" | 8 categories present in PROHIBITED_PATTERNS | ACCURATE |
| "All 10 Annex III categories are detected" | 10 categories (including medical devices and safety components) | ACCURATE |
| "No required external dependencies -- stdlib only" | `import fcntl` unconditionally in classify_risk.py | BUG -- breaks on Windows |
| "Cross-platform -- Unix, macOS, and Windows supported" | log_event.py: correct. classify_risk.py: crashes on Windows | PARTIALLY FALSE |
| "v2.0: AST-based analysis" listed in Roadmap | AST analysis already exists in ast_analysis.py (870 lines) | STALE ROADMAP -- AST is shipped |
| "tree-sitter optional for JS/TS AST" | tree-sitter is a stub that always raises ImportError | MISLEADING -- it's listed as optional but doesn't work |
| "6 providers" for credential check | 6 high-confidence patterns + 3 medium-confidence | ACCURATE (6 high-confidence providers) |
| "Hash-chained audit trail" | SHA-256 hash chain, independently verifiable | ACCURATE |
| "File-locked writes -- safe under concurrent hook execution" | fcntl/msvcrt locking in log_event.py | ACCURATE |
| "Regula v1.1.0" in HTML report | SARIF output hardcodes "1.0.0" | VERSION MISMATCH in SARIF |
| "SARIF for CI/CD" | SARIF 2.1.0 schema, proper structure | ACCURATE (minus version bug) |
| "Same hook protocol" for Claude Code, Copilot, Windsurf | Hooks use stdin/stdout JSON with exit codes | ACCURATE |
| "Confidence scores, not binary labels" | 0-100 scoring with sensible algorithm | ACCURATE |
| "AST-powered compliance gap analysis" | compliance_check.py uses AST for Articles 12 and 14 | ACCURATE |
| "AI-specific dependency pinning" | 69 AI libraries in detection list | ACCURATE |

---

## Critical Bugs and Issues

### P0 (Crash)

1. **`import fcntl` in classify_risk.py line 16.** Unconditional import of Unix-only module. Will crash with `ModuleNotFoundError` on Windows. The `fcntl` import is not used anywhere in this file -- it appears to be a leftover from development. `log_event.py` handles cross-platform correctly; this file does not.

### P1 (Incorrect behaviour)

2. **SARIF version mismatch.** `report.py` line 595 hardcodes `"version": "1.0.0"` in the SARIF tool driver, but `pyproject.toml` declares version `1.1.0`. Auditors comparing SARIF output to the installed version will see a discrepancy.

3. **ast_engine.py bare import.** `from ast_analysis import (...)` on line 22 uses a bare import without sys.path manipulation. This file will fail with `ModuleNotFoundError` when imported as a package (`from scripts.ast_engine import analyse_file`) because it expects `ast_analysis` to be directly importable.

4. **tree-sitter is a documented stub.** `_tree_sitter_parse()` always raises `ImportError("tree-sitter parsing not yet implemented")` even when tree-sitter IS installed. The optional dependency in pyproject.toml is misleading.

### P2 (Missing functionality)

5. **requirements.txt `-r` includes not followed.** Lines starting with `-r` (recursive includes) are silently skipped. A project with `requirements.txt` containing `-r requirements-ai.txt` will miss all AI dependencies in the included file.

6. **package.json peerDependencies/workspaces ignored.** Only `dependencies` and `devDependencies` are parsed. Monorepo workspaces and peer dependencies are invisible.

7. **pyproject.toml optional-dependencies dead code.** The first `for m in re.finditer(...)` loop at lines 235-241 has a body of just `pass` -- this is dead code.

8. **Advisory version matching is exact-string only.** `check_compromised()` compares `dep_version in versions` (line 506). If a project pins `litellm==1.82.7.post1` or uses a compatible release specifier, it would NOT match the advisory's `"1.82.7"`.

### P3 (Quality/maintenance)

9. **Custom test harness instead of unittest/pytest.** Tests use manual `passed`/`failed` counters with `assert_eq`/`assert_true`. CI only checks exit code. A test failure does NOT stop the test run -- all tests execute regardless of failures, and the exit code is based on `failed > 0`. This is fragile. Using pytest would provide better failure reporting, fixture management, and IDE integration.

10. **`is_ai_dependency` defined twice.** In dependency_scan.py, lines 89-101 define `is_ai_dependency`, then lines 115-117 redefine it (with `# noqa: F811`). The first implementation is dead code.

11. **No file size guard.** Both `classify_risk.py` (via `main()`) and `report.py` (`scan_files()`) read entire files into memory. A 500MB generated file would cause OOM.

---

## What a Hostile Code Reviewer Would Flag

1. **"You claim cross-platform but crash on Windows."** The unconditional `import fcntl` in classify_risk.py is an instant disqualification for the "cross-platform" claim. Fix: remove the unused import.

2. **"Your test suite doesn't use any testing framework."** A custom `assert_eq` function with manual counters is something you'd see in a beginner tutorial. For a compliance tool that claims 109 tests, this is unprofessional. A single flaky assert won't halt the suite. Fix: migrate to pytest.

3. **"Your tree-sitter integration is vapourware."** You list it as an optional dependency in pyproject.toml, but `_tree_sitter_parse` always raises an error. Either implement it or remove the dependency. Don't ship a stub and call it "optional."

4. **"Your YAML fallback parser is a liability."** The `_parse_yaml_fallback` in classify_risk.py handles "up to 3 levels of nesting" and doesn't support YAML lists as values under nested keys. Any non-trivial policy file will break silently. The parser doesn't handle multiline strings, anchors, aliases, or any real YAML feature. Fix: make pyyaml a required dependency.

5. **"Version numbers are inconsistent."** pyproject.toml says 1.1.0, SARIF output says 1.0.0. This is the kind of sloppiness that undermines trust in a compliance tool.

6. **"Pattern matching as risk indication is fundamentally limited."** The tool will flag a file containing the string "social credit scoring" in a research paper, a docstring, or a code comment. There is no semantic understanding of whether the matched text represents actual system behaviour or merely discusses it. This is acknowledged in the README but remains the core limitation.

7. **"The dependency scanner follows no external advisory database."** Only one advisory (LiteLLM) exists. There is no mechanism to update advisories, no integration with OSV, CVE, or any real vulnerability database. For a "supply chain security" feature, this is minimal.

8. **"The compliance gap assessment gives points for the wrong reasons."** If a project has a file named `risk_assessment.md` that contains the word "risk mitigation" but describes a business risk (not AI risk), it still gets Article 9 points. The AI-specificity check (lines 222-224) helps but is easily gamed.

9. **"No integration tests that actually run the CLI."** While there are test functions with "integration" in the name, they test individual functions, not the actual CLI entry points. There's no test that pipes JSON to stdin and checks hook output.

10. **"Prohibited pattern matching is regex-based and trivially evadable."** Writing "s0cial cr3dit sc0ring" or "Sozialkredit" (German) bypasses all 8 prohibited patterns. The tool only works in English and only with exact substring matches. Obfuscation defeats it entirely.

---

## Summary of Findings

### What's Good
- Genuinely functional risk classification with all 8 Article 5 and 10 Annex III categories
- Honest about limitations (pattern-based indication, not legal classification)
- Real hash-chained audit trail with independent verification
- AST-based Python analysis is substantial (870 lines, actual data flow tracing)
- 109 tests covering core functionality
- Zero required external dependencies (stdlib only)
- Comprehensive CLI with 18 commands
- Compliance gap assessment is genuinely useful for Articles 9-15
- Dependency scanner with 69 AI libraries is a solid registry
- Cross-framework mapping (EU AI Act, NIST, ISO 42001) uses real reference data

### What Needs Fixing
- P0: Remove unused `import fcntl` from classify_risk.py (breaks Windows)
- P1: Fix SARIF version to match pyproject.toml (1.1.0)
- P1: Fix ast_engine.py bare import
- P1: Either implement tree-sitter or remove the stub
- P2: Handle `-r` includes in requirements.txt
- P2: Add peerDependencies/workspaces to package.json parser
- P3: Migrate tests to pytest
- P3: Update README roadmap (AST is shipped, not "v2.0 planned")
- P3: Update test count from "105+" to actual count
