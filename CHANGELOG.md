# Changelog

All notable changes to Regula are documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
This project uses [Semantic Versioning](https://semver.org/).

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
- Smoke tests for all 21 CLI subcommands (previously only 5 of 21 were tested)
- Tests for `--ci` flag behaviour (5 tests: compliant, warn-tier, error, global position, info-tier)
- Tests for generic exception handler and `--framework` removal
- 3 hook resilience tests: empty stdin, large payload (500KB), binary content edge cases
- `scripts/__main__.py` — enables `python -m scripts` invocation
- `INFO` status level in `regula doctor` for setup-specific items (not problems)
- Pytest compatibility — tests run via both `python3 tests/test_*.py` and `pytest tests/`
- 2 new test fixtures: `sample_prohibited` (Article 5), `sample_mixed_tier` (employment + chatbot)
- Benchmark manifest at `tests/fixtures/benchmark_manifest.json`

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
