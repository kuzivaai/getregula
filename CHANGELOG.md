# Changelog

All notable changes to Regula are documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
This project uses [Semantic Versioning](https://semver.org/).

## [1.5.0] — 2026-04-03

### Added
- EU Cyber Resilience Act (2024/2847) as 11th compliance framework mapped to Articles 9-15
- 2 vibe-coding architecture antipatterns: no_error_handling_ai_call, exposed_api_key_env
- Vibe coder quickstart guide (docs/QUICKSTART_VIBE_CODERS.md)
- `Finding` dataclass — formalises the scan finding contract (12 fields, backward-compatible)
- `compute_finding_tier()` — single source of truth for block/warn/info logic
- `get_policy(path=)` override for testability
- `__all__` on 6 key public API modules (constants, risk_types, classify_risk, report, log_event, policy_config)
- 5 new risk patterns: driverless, automated driving, vehicle control system, dialogue system, conversational model
- 28 orphaned tests added to manual runner (324 total, 748 assertions)

### Changed
- Landing page: light cream theme with hexagonal tile pattern, research-validated copy targeting both vibe coders and production developers
- VERSION moved to constants.py — breaks circular import chain (evidence_pack/gen_docs/sbom no longer import cli.py)
- report.py refactored: extracted _scan_agent_autonomy(), _scan_credentials(), _scan_ai_security(), _parse_suppression_rules()
- Removed unverifiable competitive claims ("unique", "The only") from all landing pages and docs
- Competitor landscape updated with verified data: Systima Comply, ArkForge, EuConform, ClawGuard, VerifyWise
- Risk pattern count: 130 (was 123). Command count corrected: 33 (was 34).
- _compile_custom_pattern() now catches re.error
- strip_comments() docstring corrected to match actual behaviour

### Fixed
- docs/FULL_INSPECTION.md version 1.2.0 → 1.5.0
- CRA crosswalk misattributions: Art. 13(15) → Annex II, Annex VII → Art. 13(8)
- Pattern breakdown in FULL_INSPECTION.md (32+61+21+16=130)

---

## [1.3.0] — 2026-03-28

### Fixed
- Credit scorer false negative — `train_credit_model` and similar underscore-prefixed identifiers now correctly match `essential_services` high-risk patterns. Root cause: `\b` word-boundary anchor fails when the keyword is preceded by `_` (a word character). Fixed `credit.?model`, `credit.?risk`, `credit.?predict` in `risk_patterns.py`. Adds regression test `test_fn_fix_credit_scorer_function_names`.
- Advisory directory resolution — `_load_advisories()` in `dependency_scan.py` returned empty when Python loaded the module from `__pycache__` (`.pyc`), causing `here.parent` to resolve to `scripts/__pycache__` instead of `scripts/`. Fix: step up an extra level when `here.name == "__pycache__"`, with `Path.cwd() / "references" / "advisories"` as a final fallback. Adds regression test `test_advisory_load_fallback_pyc_path`.
- `skip_dirs` absolute path bug in `code_analysis.py` and `generate_documentation.py` — both used `filepath.parts` (absolute path) to check skip directories, causing any project nested inside a directory named `tests/`, `build/`, `venv/`, etc. to have all files silently skipped. Fixed to use `filepath.relative_to(project).parts`. Adds regression test `test_docs_nested_in_tests_dir_not_blank`.
- Version string in generated documentation was `v1.1.0` in 6 places; corrected to `v1.2.0`.

### Added
- AST analysis wired into Annex IV documentation generator (`generate_documentation.py`). Section 2.1 now lists detected AI frameworks and function signatures. Section 3.3 now includes an AST-derived oversight score (0-100), specific oversight patterns with line numbers, and unreviewed automated decision paths. Section 3.4 now includes a logging coverage score (0-100), counts of logged vs unlogged AI operations, and an Article 12 gap warning when AI operations have no nearby logging. For non-Python projects the generator falls back to regex-based detection. Adds 4 new regression tests.
- `ast_analyse_project()` helper in `generate_documentation.py` — aggregates `parse_python_file`, `detect_human_oversight`, and `detect_logging_practices` across all Python source files in a project, returning AI imports, function signatures, oversight score/evidence, and logging coverage metrics.

- `parse_go_mod()` in `dependency_scan.py` — parses Go module dependencies from `go.mod` files. Handles block `require(...)` and single-line `require` statements. All go.mod versions treated as exact (Go modules have no range specifiers). 67 known AI Go modules registered including `github.com/tmc/langchaingo`, `github.com/sashabaranov/go-openai`, `github.com/ollama/ollama`, `github.com/anthropics/anthropic-sdk-go`.
- `parse_build_gradle()` in `dependency_scan.py` — parses Java/Kotlin dependencies from `build.gradle` (Groovy DSL) and `build.gradle.kts` (Kotlin DSL). Handles string-style (`'group:artifact:version'`) and named-arg style (`group: 'g', name: 'a', version: 'v'`). 40+ known AI Java/Kotlin artifacts registered including `dev.langchain4j:langchain4j`, `ai.djl:api`, `org.deeplearning4j:deeplearning4j-core`, `org.tensorflow:tensorflow-core-platform`. Both parsers wired into `scan_dependencies()`.

### Tests
- 435 tests, 1,044 assertions (was 348 at v1.2.0 release)

---

## [1.2.0] — 2026-03-28

### Added
- `regula status --show <name>` — detailed view of one registered system with libraries, findings, risk trend
- `regula status --format csv` — CSV export of registry for spreadsheet analysis
- `regula status --format json` — structured JSON export of registry
- `regula discover --sync` — re-scan all previously registered projects, update timestamps and risk levels
- `regula docs --format model-card` — generates HuggingFace-compatible model card with auto-detected architecture, data sources, and EU AI Act compliance section
- Auto-populated Annex IV sections: model architecture (from imports), data sources (CSV/DB/API/S3), human oversight patterns, logging infrastructure, risk register with OWASP mappings
- `scripts/code_analysis.py` — detection helpers for architecture (12 frameworks), data sources (10 types), oversight (4 categories), logging (4 types)
- `tests/test_documentation.py` — 10 test functions / 22 assertions for documentation generation
- MCP server permission analysis — parses `mcpServers` config, assesses risk per server against OWASP Agentic Top 10
- MCP credential detection in both env vars (MEDIUM) and hardcoded args (HIGH)
- Known MCP server risk profiles (filesystem, postgres, github, slack, puppeteer, fetch, everything)
- Autonomous action detection — flags AI output flowing to subprocess/HTTP/database without human gate
- OWASP Agentic Top 10 mapping (#1 Excessive Agency, #2 Uncontrolled Tool Use, #5 Identity Gaps, #6 Unmonitored Actions, #7 Data Exfiltration, #8 Supply Chain)
- `tests/test_agent_governance.py` — 10 test functions / 13 assertions for agent governance
- `tests/test_reliability.py` — 12 test functions / 17 assertions for edge cases (unicode, null bytes, binary files, concurrent writes, nested JSON, network timeout)
- Narrowed 16 `except Exception` blocks across 8 files to specific exception types (OSError, ValueError, SyntaxError, subprocess.SubprocessError). 3 intentional catch-alls remain with comments explaining why.
- Risk trend tracking — `previous_highest_risk` stored when risk tier changes between scans
- `tests/test_registry.py` — 8 test functions / 21 assertions for registry features
- `--ci` flag for check command — implies `--strict`, exits 1 on any WARN or BLOCK finding
- Generic exception handler in CLI — non-RegulaError exceptions produce a clean message with bug report link instead of raw tracebacks
- Smoke tests for CLI subcommands (previously only 5 were tested)
- Tests for `--ci` flag behaviour (5 tests: compliant, warn-tier, error, global position, info-tier)
- Tests for generic exception handler and `--framework` removal
- 3 hook resilience tests: empty stdin, large payload (500KB), binary content edge cases
- `scripts/__main__.py` — enables `python -m scripts` invocation
- `INFO` status level in `regula doctor` for setup-specific items (not problems)
- Pytest compatibility — tests run via both `python3 tests/test_*.py` and `pytest tests/`
- 2 new test fixtures: `sample_prohibited` (Article 5), `sample_mixed_tier` (employment + chatbot)
- Benchmark manifest at `tests/fixtures/benchmark_manifest.json`

- `--skip-tests` flag for `check` — excludes test files entirely from scan results (removes ~27% noise on typical AI codebases)
- `--min-tier` flag for `check` — filters output to a minimum risk tier (`prohibited`, `high_risk`, `limited_risk`, `minimal_risk`); combined with `--skip-tests` reduces LangChain's 2,108 raw findings to 19 actionable ones
- Agent autonomy detection wired into `check` — `detect_autonomous_actions()` now runs on all code files, not just via `agent` subcommand
- Contextual agent path detection — files in `agent/`, `tool/`, `middleware/`, `plugin/`, `executor/`, `sandbox/` paths are flagged for subprocess/exec even without AI imports (OWASP Agentic ASI02/ASI04)
- `agent_autonomy` tier in SARIF output and text report
- `_is_test_file()` extended to catch suffix patterns (`standard-tests/`, `langchain_tests/`)
- `test_security_hardening.py` — security hardening assertions (no eval/exec in source, no os.system, self-scan clean)

### Changed
- Refactored 5 CLI commands (report, audit, install, docs, discover) from sys.argv manipulation to direct function calls
- Split classify_risk.py (844 lines) into 4 focused modules:
  - `risk_types.py` (63 lines) — RiskTier enum and Classification dataclass
  - `risk_patterns.py` (321 lines) — all EU AI Act pattern definitions
  - `policy_config.py` (132 lines) — policy loading, caching, and accessors
  - `classify_risk.py` (377 lines) — classification logic, security checks, CLI
- All existing imports (`from classify_risk import X`) continue to work via re-exports
- `datetime.utcnow()` replaced with `datetime.now(timezone.utc)` — removes Python 3.12+ deprecation warnings
- Doctor output distinguishes INFO (setup needed) from WARN (potential issue)
- Doctor .gitignore check recognises `.regula/` as covering audit subdirectory
- Removed false "world-readable policy file" warning from doctor (policy contains no secrets)
- README: removed stale `--framework` CLI examples, added `--ci` flag documentation
- `sample_warn_tier` fixture docstring corrected to document test-path deprioritisation

### Removed
- Unused `--framework` global flag (was declared but never consumed by any command)

### Fixed
- `--ci` flag now works after subcommand (`regula check --ci`) not just before it
- `regula audit query` now correctly passes `--after` and `--before` date filters (were silently dropped)
- `regula docs` now correctly supports `--format json` output (was silently defaulting to markdown)
- `regula discover` now correctly supports `--format json` in all code paths
- False positive regex patterns tightened with word boundaries:
  - `predictive.?polic` → `predictive.?policing`
  - `face.?scrap` → `\bface.?scrap`
  - `race.?detect` → `\brace.?detect(?!.*(?:condition|thread|concurrent))`
  - `face.?recogn` → `\bface.?recogn`
  - `voice.?recogn` → `\bvoice.?recogn`
  - `support.?bot` → `support.?bot\b`
  - `age.?estimat` → `\bage.?estimat`

## [1.0.0] - 2026-03-11

### Added
- Initial release
- EU AI Act Article 5 prohibited practice detection (8 categories, 24 patterns)
- Annex III high-risk classification (10 categories)
- Limited-risk and minimal-risk classification
- Confidence scoring (0-100 with BLOCK/WARN/INFO tiers)
- Credential detection (API keys, private keys, connection strings)
- SARIF output for CI/CD integration
- HTML report generation
- Audit trail with hash-chain verification
- AI system discovery and registry
- Compliance status management with workflow transitions
- Gap assessment (Articles 9-15)
- Questionnaire-based risk assessment
- Session-level risk aggregation
- Baseline save/compare for incremental compliance
- Documentation scaffolding (Annex IV, QMS)
- EU AI Act enforcement timeline
- Hook system (pre_tool_use, post_tool_use, stop_hook)
- Installation for Claude Code, Copilot CLI, Windsurf, pre-commit, git-hooks
- Custom exception hierarchy (RegulaError, PathError, ConfigError, ParseError, DependencyError)
- Exit code convention (0=success, 1=findings, 2=error, 130=interrupt)
- AI security patterns (LLM05 unsafe deserialization, prompt injection, eval-on-output)
- SBOM generation (CycloneDX 1.6 format)
- Agentic AI governance monitoring (`agent` subcommand)
- Dependency supply chain analysis (`deps` subcommand)
- Multi-framework compliance mapping (8 frameworks)
- Policy thresholds configuration (block_above, warn_above)
- Diff scanning mode (`check --diff REF`)
- Remediation engine with inline fix suggestions
- Article 6(3) exemption assessment
- Model card validation
- Tree-sitter JS/TS AST analysis
- Rust, C, C++, Java, Go language support in AST engine
