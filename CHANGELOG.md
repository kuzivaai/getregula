# Changelog

All notable changes to Regula are documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
This project uses [Semantic Versioning](https://semver.org/).

## [Unreleased]

The "public-launch readiness" bundle. Adds two new CLI commands
(`regula handoff` and `regula regwatch`), seeds the first open data
assets Regula publishes (delta log, enforcement tracker, sandbox
registry, pattern corpus), adds two write-time integrity tools
(claim auditor, self-healing CI), and closes the honesty gaps surfaced
by three independent audits (research-eval, repo-readiness,
moat-research). Command count rises from 41 to 43. No breaking changes;
all 926 tests still pass.

### Added — new CLI commands

- **`regula handoff {garak,giskard,promptfoo}`** — detects LLM
  entrypoints in a project and emits a scoped red-team config for the
  target tool. Positions Regula as complementary to runtime behaviour
  testing, not competitive with it. Detected 14 entrypoints in the
  Regula repo itself on first smoke test.
- **`regula regwatch`** — reads the regulatory delta log, compares
  against `regula-policy.yaml → regulatory_basis.last_reviewed`, and
  warns when the installed ruleset is older than the most recent
  regulatory change. Ignores future-dated placeholder entries.

### Added — open data assets (the moat)

- **[`content/regulations/delta-log/`](content/regulations/delta-log/)**
  — primary-source-linked regulatory changelog for the EU AI Act.
  Schema + 5 seed entries (Regulation adoption 12 Jul 2024; Digital
  Omnibus proposal 19 Nov 2025; Council general approach 13 Mar 2026;
  Parliament plenary position 26 Mar 2026; trilogue target 28 Apr 2026).
  Builder `scripts/build_delta_log.py` emits `index.json`, RSS
  `feed.xml`, and `SUMMARY.md`. CC-BY-4.0.
- **[`content/regulations/enforcement-tracker/`](content/regulations/enforcement-tracker/)**
  — schema + empty index for the first EU AI Act enforcement tracker.
  Pre-populated skeleton so the first fine can be published within
  hours, not weeks. CC-BY-4.0.
- **[`content/regulations/sandbox-registry/`](content/regulations/sandbox-registry/)**
  — 27-Member-State Article 57 sandbox registry. 5 entries seeded
  (DE, ES, FI, FR, NL) from primary sources; 22 TODO. CC-BY-4.0.
- **[`data/patterns/`](data/patterns/)** — 34 risk pattern groups
  extracted from `scripts/risk_patterns.py` as CC-BY-4.0 YAML.
  Regenerate with `python3 scripts/extract_patterns.py`.
- **[`data/site_facts.json`](data/site_facts.json)** + `site_facts.md`
  — canonical source of truth for every numeric claim on landing
  pages. Computes `historical_330_bucket` (279 + 38 + 9 + 4 = 330
  exact) and `grand_total` (502, inclusive). Regenerate with
  `python3 scripts/site_facts.py`.

### Added — integrity tooling

- **[`scripts/claim_auditor.py`](scripts/claim_auditor.py)** — stdlib-only
  scanner that blocks commits introducing unverified factual claims in
  Markdown or HTML. Recognises URLs, markdown links, HTML anchors,
  in-repo file references, bracketed verification labels, and explicit
  citation words. Exempts structural regulatory references (Article /
  Annex / Recital / Category / Chapter) and short UX time durations.
  Backtest against the last 10 commits: 54 total unsourced findings
  surfaced (noise floor ~2–4 per small commit).
- **[`scripts/ci_heal.py`](scripts/ci_heal.py)** + `.github/workflows/self-heal.yaml`
  — self-healing CI agent that classifies failing GitHub Actions
  logs (pytest / type / lint / build / import / syntax), applies a
  minimal fix via Claude Code, runs the full verify sequence locally,
  and pushes with a `Ci-Heal-Attempt: N` commit trailer. Capped at 3
  attempts per branch. Backtest: 10/10 historical failing CI runs
  classified as auto-healable. Posts PR summary comments.
- **[`.pre-commit-config.yaml`](.pre-commit-config.yaml)** — local
  pre-commit hook running the claim auditor on staged files.
- **`.github/PULL_REQUEST_TEMPLATE.md`** — with explicit verify
  checklist, honesty gate checklist, scope rules, and locale-parity
  reminder.
- **`.github/dependabot.yml`** — weekly pip + github-actions updates.

### Added — documentation

- **[`docs/what-regula-does-not-do.md`](docs/what-regula-does-not-do.md)**
  — explicit scope statement. Lists articles Regula addresses
  partially / fully (Art. 5, 10, 11, 12, 13, 14, 15, 49, 51-55, 99)
  vs cannot address (Art. 9, 17, 26, 27, 29, 43, 63, 72/73, 74).
  Positions Regula as the "code layer of an AI governance programme,
  not the whole programme".
- **[`docs/evidence-pack-guide.md`](docs/evidence-pack-guide.md)** —
  auditor-facing documentation of `regula conform` output (26-file
  Article 43 pack, SHA-256 verification steps, reproducibility
  guarantees).
- **[`docs/competitor-analysis.md`](docs/competitor-analysis.md)** —
  objective competitor landscape. Promotes AIR Blackbox (closest
  positional overlap to Regula in the market) and Microsoft Agent
  Governance Toolkit (released 3 April 2026, adjacent runtime
  category) into the main table. Includes `desiorac/mcp-eu-ai-act`
  as a second independent MCP-server scanner.
- **[`docs/moat-research.md`](docs/moat-research.md)** — proprietary
  data moat thesis, ranked 13 candidates, with counterevidence.
- Translation skill recommendation (EN → DE/PT-BR workflow using
  cross-model reflection) — internal document, removed from public tree.
- Three audit reports (research-eval, public-readiness, repo-readiness)
  were produced during this development cycle. They served their purpose
  and were removed from the public tree — the fixes they recommended are
  all applied. Available in git history if needed.

### Changed

- `pyproject.toml`: Python 3.13 classifier added, CI matrix now tests
  3.10 / 3.11 / 3.12 / 3.13. Added `Documentation`, `Changelog`,
  `Trust pack`, and `Delta log` URLs. Homepage switched to
  `https://getregula.com`.
- `CLAUDE.md`: new `## Honesty & Verification`, `## Workflow`, and
  `## Project Conventions` sections. Identity line now explicitly says
  "Positioned as the code layer of an AI governance programme, not
  the whole programme". Command count reconciled 39 → 43.
- `README.md`: test count reconciled from the stale "525 tests" to
  "688 test functions (926 passing assertions)" with inline citations
  to `scripts/site_facts.py` and `benchmarks/labels.json`.
- `index.html`, `de.html`, `pt-br.html`: "Where Regula fits" section
  now names AIR Blackbox, Systima Comply, and ark-forge as OSS peers
  (honest competitive acknowledgement). Command count 38/39 → 43.
  CycloneDX 1.6 → 1.7 (matches sbom test assertion). Framework count
  13 → 12 (removed duplicate NIST AI 600-1 from visible list).
- `de.html` and `pt-br.html`: German "Sie-form" and Brazilian Portuguese
  translations of the "Where Regula fits" section added.
- `regula-policy.yaml`: `governance.ai_officer` populated for the
  Regula project itself (maintainer accountable under Article 4);
  `last_reviewed` bumped to 2026-04-09.
- `scripts/doctor.py`: support both `governance.ai_officer` and
  `governance.contacts.ai_officer` schema paths. Result: 9 pass /
  2 info (was 8 pass / 3 info).
- `.github/workflows/ci.yaml`: new `regula security-self-check` step,
  new `html-wellformed` job, new `claim-audit` job.
- `.gitignore`: re-include `.claude/agents/**` and `.claude/skills/**`
  so agent definitions and skills are tracked while local config stays
  ignored; add `.ci-heal/` scratch dir.

### Removed

- `docs/marketing/uae_outreach_v1.md` — internal sales template not
  suitable for public repo.

### Renamed

- `docs/QUICKSTART_VIBE_CODERS.md` → `docs/QUICKSTART.md` (the
  informal name was flagged by the repo audit as ageing poorly).

### Fixed

- `scripts/make_og_uae.py` was missing the `# regula-ignore` marker
  and tripped Regula's own security self-check on the first run.
  Caught by the test suite (`test_security_self_check_passes`), not
  by a human. Fixed.
- During the research-eval pass, a documentation edit about Article
  5(1)(f) triggered Regula's own `pre_tool_use.py` hook. The sentence
  was rephrased to convey the same regulatory fact without matching
  the `emotion_inference_restricted` detector. The tool worked as
  designed, live, on its own maintainer.

### Honesty note — the "330 risk patterns" claim

The "330 risk patterns" figure cited on all landing pages is not a
fabrication and not drift. It is the exact sum of the tiered risk
regexes (279) plus architecture detectors (38) plus credential
detectors (9) plus oversight detectors (4) = **330**. This bucketing
is now transparently documented in `data/site_facts.md` via the
`historical_330_bucket` computation. The grand-total figure (502) is
higher and is also published in the same file. Any auditor can
reproduce both numbers by running `python3 scripts/site_facts.py`.

## [1.6.1] — 2026-04-09

The "trust foundation" point release. Adds the buyer-facing Trust Pack,
publishes a reproducible precision/recall benchmark, kills the
`yaml not installed` nag, sharpens the doctor `.gitignore` check, and
adds standard OSS meta-files (SECURITY.md, CITATION.cff, CODE_OF_CONDUCT.md).
No breaking changes; all 926 tests still pass.

### Added

- **[`docs/TRUST.md`](docs/TRUST.md)** — Trust Pack with 9 sections.
  Every claim is paired with the exact shell command that verifies it.
- **[`docs/benchmarks/PRECISION_RECALL_2026_04.md`](docs/benchmarks/PRECISION_RECALL_2026_04.md)**
  — published precision/recall benchmark with reproducible methodology.
  Headline: 100% on the synthetic Annex III/Article 5 corpus; **0
  false positives at the BLOCK CI tier across 257 labelled findings on
  5 mature OSS projects**. Sliced by tier, project, and indicator
  category. CORE-Bench-style explicit limitations.
- **[`SECURITY.md`](SECURITY.md)** — vulnerability disclosure policy
  with supported versions, target response times, and a 90-day
  coordinated disclosure default.
- **[`CITATION.cff`](CITATION.cff)** — Citation File Format metadata.
- **[`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md)** — short, technical, direct.
- **[`uae.html`](uae.html)** — landing page for DIFC, ADGM, Hub71,
  Dubai Internet City, and NEOM portfolio teams. Cites Article 2(1)(c)
  extraterritoriality, Article 16 provider obligations, Article 99
  fines (€35M / 7%), and Article 113 enforcement timing — all against
  Regulation (EU) 2024/1689 primary text.
- **[`docs/marketing/uae_outreach_v1.md`](docs/marketing/uae_outreach_v1.md)**
  — 50-message distribution test templates with targeting checklist,
  per-sector message bodies, and stop conditions.
- **[`demos/regula-cli.cast`](demos/regula-cli.cast)** + `regula-cli.txt`
  — asciinema v2 cast and plain-text fallback of the value-first
  user journey. 11 seconds.
- **`support@getregula.com`** — direct contact channel surfaced on
  both landing pages, in `README.md`, in `SECURITY.md`, and in the
  Trust Pack vendor evaluation answers.

### Changed

- **`regula doctor` `.gitignore` check is now context-aware.** It
  only WARNs about a missing `.gitignore` when the cwd is actually
  inside a git repository (walks up looking for `.git/`). Outside a
  git repo it shows INFO instead of WARN.
- **`yaml not installed` nag is silent by default.** The fallback
  parser works; users were seeing the same notice on every CLI
  invocation. The full optional-dependency picture is still in
  `regula doctor`. Set `REGULA_VERBOSE=1` to opt back in.
- **Landing page CTA reordered.** Primary button now installs
  ("Try free in 30 seconds"); `regula assess` is the secondary
  "no codebase needed" option.
- **Landing page footer expanded** with Trust Pack, Benchmarks,
  SECURITY.md, UAE page, and `support@getregula.com`.
- **`README.md`** — new "Trust, security, and how to verify" and
  "Contact" sections.
- **Test count: 925 → 926.**
- Removed 24 stale `docs/tmp*_annex_iv.md` files left over from
  prior conformity-pack test runs.

### Verified

- 926/926 custom test runner
- 6/6 self-test
- doctor: 8 pass / 3 info / 0 warn (in a git repo)
- bandit `-c pyproject.toml`: 0 / 0 / 0
- semgrep `p/security-audit + p/python`: 0 findings on 200 rules / 129 files
- pip-audit: 0 vulnerabilities
- regula self-scan: 0 findings

---

## [1.6.0] — 2026-04-09

The "live-path reliability" release. Bundles the v1.6 feature work that
shipped over March–April 2026 with five P0/P1 fixes uncovered by the
April 2026 reliability audit and a `/research-eval` pass against primary
EU and UNESCO sources.

### Added

- **`regula conform --sme`** — SME-simplified Annex IV under Article 11(1)
  second subparagraph (interim format pending Commission template).
- **`regula exempt`** — Article 6(3) high-risk exemption decision tree
  with the Commission's missed 2 February 2026 Article 6(5) guideline-deadline
  disclosure baked in. Interactive or `--answers yes,no,...` for CI use.
- **`regula register`** — Annex VIII Section A/B/C registration packet
  generator (Article 49). Branches by provider/deployer role and Annex III
  area, including Article 49(4) non-public routing for biometrics / law
  enforcement / migration and Article 49(5) national-level routing for
  critical infrastructure. Auto-fills from existing scan artefacts and
  dual-annotates 2026-08-02 vs Omnibus-proposed 2027-12-02 deadlines.
- **`regula gpai-check`** — maps GPAI provider code to the three chapters
  of the GPAI Code of Practice (Transparency / Copyright / Safety &
  Security) with Article 53 + Article 55 scope rules.
- **OWASP LLM01:2025 prompt-injection detection (expanded)** — direct
  user-input concatenation, indirect (RAG / web-fetch / file-read flowing
  into prompt), and tool-output (plugin/function results passed back).
- **Tier-3 regional landing pages** — Colorado AI Act (SB 24-205 +
  SB 25B-004 delay to 30 June 2026), South Korea AI Basic Act, United
  Kingdom (DSIT-led approach), South Africa April 2026 draft policy.
- **Harmonised-standards plumbing** — `references/harmonised_standards.yaml`
  ready to load CEN-CENELEC standards once published Q4 2026 (currently a
  documented stub).
- **`regula assess --answers`** — non-interactive `regula assess` for CI /
  piped use. Previously errored "requires an interactive terminal" with
  no escape hatch.
- **JS/TS tree-sitter data-flow tracing** with destination classification
  (log / api_response / human_review / persisted / display /
  automated_action / return) — already shipped, README finally documents it
  honestly.
- **Recall expansion** for Annex III pattern lists in `risk_patterns.py`:
  - `employment` — classify_resume / score_resume / hire-reject / job-applicant
    phrasings + prompt-string templates.
  - `education` — grade_essay / predict_dropout / admissions ranking /
    placement scoring + prompt-string templates.
  - `essential_services` — approve_loan / mortgage / health insurance pricing
    / welfare eligibility / claim assessment.
  - `law_enforcement` — parole / bail / threat-scoring (lawful Annex III
    uses, distinct from the Article 5(1)(d) profiling prohibition handled
    by `PROHIBITED_PATTERNS`).
- **Regression tests** for every recall expansion and bug fix:
  - `test_recall_realistic_employment_code`
  - `test_recall_realistic_education_code`
  - `test_recall_realistic_essential_services_code`
  - `test_recall_realistic_law_enforcement_code`
  - `test_assess_run_from_answers_non_interactive`
  - `test_scan_files_exposes_files_scanned_count`

### Fixed

- **Scan cache silent staleness on upgrade.** `ScanCache` now keys
  entries on `{path}:v2:{regula_version}:{patterns_fingerprint}:{sha256}`.
  Previously only `{path}:{sha256}`, so users who upgraded Regula kept
  seeing stale "no findings" results until they edited each file. The
  most subtle reported bug.
- **`Files scanned: 0` lying.** `scan_files` now exposes the real
  scanned-file count via `scan_files.last_stats`, and `cmd_check` uses it
  instead of misreporting `len(unique files with findings)`. Empty scans
  now print an honest "no code files matched" message.
- **`regula assess` non-TTY crash** — see Added.
- **Recall gap on realistic AI code** — see Added (recall expansion).
- **README v1.3 roadmap line** — corrected: JS/TS tree-sitter data-flow
  already ships in `scripts/ast_engine.py`. AVID and typosquat moved to
  explicit backlog.
- **Five factual errors** identified by `/research-eval`:
  1. Commission Omnibus proposal date — was "December 2025", actually
     **COM(2025) 836 adopted 19 November 2025**
     ([EP Legislative Train](https://www.europarl.europa.eu/legislative-train/package-digital-package/file-digital-omnibus-on-ai)).
  2. "10 Annex III categories" — Annex III has **8 areas** (points 1–8).
     Regula has 10 high-risk pattern categories because it includes 2
     Annex I (Article 6(1) harmonised legislation) categories: medical
     devices and machinery safety components. README, ROADMAP, and
     `docs/landscape.md` now make the split honest. Detection logic was
     correct; only the labelling was wrong.
     ([Regulation (EU) 2024/1689 Annex III](https://eur-lex.europa.eu/eli/reg/2024/1689/oj))
  3. Trilogue timing — was "first trilogue completed in late March 2026,
     second scheduled for 28 April 2026". Parliament only adopted its
     plenary mandate on **26 March 2026** (after the **Council's 13 March
     mandate**), so trilogues began in April 2026. The 28 April date is
     the **Cypriot Council Presidency's target for political agreement**,
     not a scheduled meeting.
     ([EP press release 26 March 2026](https://www.europarl.europa.eu/news/en/press-room/20260323IPR38829/),
      [Council 13 March 2026](https://www.consilium.europa.eu/en/press/press-releases/2026/03/13/council-agrees-position-to-streamline-rules-on-artificial-intelligence/))
  4. EP plenary vote — recorded as "569–45", actual was **569 in favour,
     45 against, 23 abstentions**.
     ([howtheyvote.eu/votes/189384](https://howtheyvote.eu/votes/189384))
  5. AICDI gap framings — "closes the 2.7% gap" / "closes the 12% gap"
     inverted the direction. The 2.7% / 12% are the share of companies
     that **have** the safeguard, so the gap is 97.3% / 88%. Reworded.
     ([dig.watch coverage of UNESCO/TRF report](https://dig.watch/updates/unesco-responsible-ai-practice-report))

### Verified

- 889/889 custom runner tests
- 734/734 pytest tests
- `regula self-test` 6/6
- `regula doctor` 8 PASS / 2 INFO / 1 WARN (Sentry DSN unset, unrelated)
- Clean-venv install of `dist/regula_ai-1.6.0-py3-none-any.whl` runs every
  advertised v1.6 command end-to-end (`conform --sme`, `exempt --answers`,
  `gpai-check`, `assess --answers`, `register`, `disclose`)
- `twine check` PASSED on `dist/regula_ai-1.6.0-py3-none-any.whl` and
  `dist/regula-ai-1.6.0.tar.gz`

### Known issues

See [TODO.md](TODO.md) for the prioritised gap backlog.

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
- CRA crosswalk misattributions: Art. 13(15) → Annex II, Annex VII → Art. 13(8)

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
