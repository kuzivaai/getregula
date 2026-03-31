# Regula — Project Overview

## Purpose

Regula is an open-source AI governance risk indication tool that detects EU AI Act (Regulation 2024/1689) risk patterns in code at the point of creation. It runs as a Claude Code skill, GitHub Copilot CLI hook, Windsurf Cascade hook, pre-commit hook, git hook, or standalone CLI — intercepting tool calls and scanning files for patterns that correlate with EU AI Act risk tiers. It blocks prohibited practices (Article 5), warns about high-risk systems (Annex III), flags credential leaks, and maintains a hash-chained audit trail. It is a risk *indication* tool, not a legal classifier.

---

## Tech Stack

- **Language:** Python 3.10+
- **Required dependencies:** None (stdlib only)
- **Optional dependencies:**
  - `pyyaml>=6.0` — Full YAML policy parsing (falls back to built-in parser)
  - `tree-sitter>=0.23` — JS/TS AST analysis (falls back to regex)
  - `tree-sitter-javascript>=0.23` — JS grammar for tree-sitter
  - `tree-sitter-typescript>=0.23` — TS grammar for tree-sitter
- **Build system:** setuptools (pyproject.toml)
- **Database:** None. Audit trail stored as append-only JSONL files.
- **External APIs:** None. Everything runs offline.
- **Version:** 1.2.0
- **License:** MIT
- **Python package name:** `regula`
- **CLI entry point:** `regula = "scripts.cli:main"`

---

## Build / Run

```bash
# Install from source
cd /home/mkuziva/getregula
pip install -e .                    # Editable install
pip install -e ".[all]"             # With all optional deps

# Run CLI
regula check .                      # Scan current directory
regula doctor                       # Verify installation health
regula self-test                    # Run 6 built-in classification assertions

# Run tests
pytest tests/ -q                        # 435 tests, 1,044 assertions

# Install hooks
regula install claude-code          # Claude Code hooks
regula install copilot-cli          # GitHub Copilot CLI hooks
regula install windsurf             # Windsurf Cascade hooks
regula install pre-commit           # pre-commit hook
regula install git-hooks            # git pre-commit hook
```

---

## Repo Structure

```
getregula/
├── scripts/                    # 43 Python modules
│   ├── cli.py                  # CLI dispatcher — 28 subcommands
│   ├── classify_risk.py        # Risk classification logic (377 lines) — split from monolith in v1.2.0
│   ├── risk_types.py           # RiskTier enum, Classification dataclass (63 lines)
│   ├── risk_patterns.py        # All EU AI Act pattern definitions (321 lines)
│   ├── policy_config.py        # Policy loading, caching, accessors (132 lines)
│   ├── ast_engine.py           # Multi-language AST analysis (1,725 lines, 17 functions)
│   ├── ast_analysis.py         # Python-specific AST analysis (870 lines, 45 functions)
│   ├── compliance_check.py     # Articles 9-15 gap assessment (1,104 lines, 19 functions)
│   ├── dependency_scan.py      # Supply chain analysis (866 lines, 21 functions)
│   ├── benchmark.py            # Precision/recall validation (777 lines, 17 functions)
│   ├── report.py               # HTML/SARIF/JSON reports (796 lines, 7 functions)
│   ├── discover_ai_systems.py  # AI system discovery & registry (532 lines, 14 functions)
│   ├── generate_documentation.py # Annex IV + QMS scaffolds (512 lines, 5 functions)
│   ├── sbom.py                 # CycloneDX 1.6 SBOM generation (481 lines, 13 functions)
│   ├── questionnaire.py        # Context-driven risk assessment (467 lines, 7 functions)
│   ├── feed.py                 # AI governance news feed (460 lines, 15 functions)
│   ├── remediation.py          # Inline fix suggestions (372 lines, 18 functions)
│   ├── install.py              # Hook installation (300 lines, 9 functions)
│   ├── agent_monitor.py        # Agentic AI governance, autonomy detection (563 lines)
│   ├── log_event.py            # Audit trail logging (288 lines, 15 functions)
│   ├── init_wizard.py          # Setup wizard (235 lines, 7 functions)
│   ├── framework_mapper.py     # 10-framework cross-mapping (210 lines, 5 functions)
│   ├── doctor.py               # Installation health check (208 lines, 9 functions)
│   ├── credential_check.py     # Secret detection (197 lines, 4 functions)
│   ├── session.py              # Session-level aggregation (188 lines, 3 functions)
│   ├── baseline.py             # CI/CD baseline comparison (174 lines, 6 functions)
│   ├── timeline.py             # EU AI Act enforcement dates (164 lines, 2 functions)
│   ├── self_test.py            # 6 built-in assertions (119 lines, 2 functions)
│   ├── degradation.py          # Optional dependency messaging (27 lines, 1 function)
│   ├── errors.py               # Custom exception hierarchy (32 lines, 0 functions)
│   └── __init__.py             # Package init (1 line)
│
├── hooks/                      # Real-time tool interception
│   ├── pre_tool_use.py         # Blocks prohibited patterns BEFORE execution (321 lines)
│   ├── post_tool_use.py        # Logs classifications AFTER execution
│   ├── stop_hook.py            # Session termination handler
│   └── __init__.py
│
├── tests/
│   ├── test_classification.py      # Core classification (265 tests)
│   ├── test_agent_governance.py    # Agent autonomy detection (28 tests)
│   ├── test_coverage_critical.py   # Critical path coverage (45 tests)
│   ├── test_documentation.py       # Documentation generation (16 tests)
│   ├── test_hooks_audit.py         # Hook and audit trail (50 tests)
│   ├── test_registry.py            # AI system registry (8 tests)
│   ├── test_reliability.py         # Edge cases and resilience (12 tests)
│   ├── test_security_hardening.py  # Security hardening checks (12 tests)
│   # 435 tests, 1,044 assertions total (pytest tests/)
│   └── fixtures/
│       ├── sample_high_risk/   # High-risk AI code (scores INFO tier in tests/ due to deprioritisation)
│       ├── sample_warn_tier/   # High-risk AI code (scores WARN tier when scanned outside tests/)
│       ├── sample_compliant/   # Compliant AI code example (app.py + model_card.md)
│       └── sample_unpinned/    # Unpinned dependency example (package.json)
│
├── references/                 # Static reference data
│   ├── framework_crosswalk.yaml    # 10-framework compliance mapping
│   ├── risk_indicators.yaml        # Pattern definitions
│   ├── eu_ai_act_articles_9_15.md  # High-risk requirements reference
│   ├── gpai_obligations.md         # General-purpose AI obligations
│   ├── annex_iv_template.md        # Annex IV documentation template
│   ├── iso_42001_mapping.yaml      # ISO 42001 controls mapping
│   ├── owasp_llm_top10.yaml        # OWASP LLM Top 10 mapping
│   ├── mitre_atlas.yaml            # MITRE ATLAS attack patterns
│   ├── advisories/                 # OSV-format security advisories
│   └── tree_sitter_implementation_guide.md
│
├── docs/
│   ├── course/                 # Interactive 10-module governance course
│   │   ├── 01-setup.md through 10-custom-patterns.md
│   │   └── README.md
│   ├── audit/                  # Internal audit reports (8 files)
│   │   ├── false_positive_audit.md
│   │   ├── benchmark_results.md
│   │   └── ...
│   ├── research/               # Research notes
│   └── superpowers/            # Design specs and implementation plans
│       ├── specs/2026-03-28-production-readiness-design.md
│       └── plans/2026-03-28-production-readiness.md
│
├── .github/workflows/
│   ├── ci.yaml                 # Tests on Python 3.10, 3.11, 3.12
│   └── regula-scan.yaml        # Self-scan on push/PR (SARIF upload)
│
├── .claude/                    # Claude Code configuration
│   └── settings.local.json     # Hook paths, permissions
│
├── README.md                   # User-facing documentation
├── SKILL.md                    # Claude Code skill definition
├── action.yml                  # GitHub Action definition
├── pyproject.toml              # Package metadata
├── regula-policy.yaml          # Governance policy configuration
├── LICENSE.txt                 # MIT License
├── .gitignore
└── .regula-baseline.json       # Baseline compliance state
```

---

## Entry Points

| Entry Point | File | How It's Invoked |
|---|---|---|
| CLI | `scripts/cli.py:main()` | `regula <command>` via pip-installed entry point |
| PreToolUse hook | `hooks/pre_tool_use.py` | Automatically by Claude Code/Copilot/Windsurf before each tool call |
| PostToolUse hook | `hooks/post_tool_use.py` | Automatically after each tool call |
| Session stop hook | `hooks/stop_hook.py` | On session termination |
| GitHub Action | `action.yml` | `uses: kuzivaai/getregula@main` in workflow |
| Test runner | `tests/test_classification.py` | `python3 tests/test_classification.py` |

---

## Core Business Logic

### Risk Classification Engine (`scripts/classify_risk.py`)

The central engine. Takes text input, returns a `Classification` dataclass with tier, confidence, indicators, applicable articles, and action.

**Risk tier enum:**
- `PROHIBITED` — Article 5 practices (block, exit 1)
- `HIGH_RISK` — Annex III systems (warn, Articles 9-15 apply)
- `LIMITED_RISK` — Article 50 (transparency obligation)
- `MINIMAL_RISK` — No mandatory requirements
- `NOT_AI` — No AI indicators detected

**Prohibited Patterns (8 categories, 32 regex patterns):**

| Key | Article | Patterns | Description |
|---|---|---|---|
| `subliminal_manipulation` | 5(1)(a) | 3 | AI deploying subliminal techniques beyond a person's consciousness |
| `exploitation_vulnerabilities` | 5(1)(b) | 3 | Exploiting vulnerabilities of specific groups (age, disability, economic situation) |
| `social_scoring` | 5(1)(c) | 5 | Social scoring by public authorities or on their behalf |
| `criminal_prediction` | 5(1)(d) | 4 | Criminal risk prediction based solely on profiling or personality traits |
| `facial_recognition_scraping` | 5(1)(e) | 3 | Creating facial recognition databases through untargeted scraping |
| `emotion_inference_restricted` | 5(1)(f) | 5 | Emotion inference in workplace or educational settings |
| `biometric_categorisation_sensitive` | 5(1)(g) | 5 | Biometric categorisation inferring sensitive attributes |
| `realtime_biometric_public` | 5(1)(h) | 4 | Real-time remote biometric identification in publicly accessible spaces |

**High-Risk Patterns (10 categories, 52 regex patterns):**

| Key | Patterns | Description |
|---|---|---|
| `biometrics` | 4 | Biometric identification and categorisation |
| `critical_infrastructure` | 4 | Critical infrastructure management |
| `education` | 4 | Education and vocational training |
| `employment` | 9 | Employment and workers management |
| `essential_services` | 11 | Access to essential services |
| `law_enforcement` | 4 | Law enforcement |
| `migration` | 4 | Migration, asylum, and border control |
| `justice` | 4 | Justice and democratic processes |
| `medical_devices` | 4 | AI components of medical devices |
| `safety_components` | 4 | Safety components under Union harmonisation legislation |

**Limited-Risk Patterns (4 categories, 17 regex patterns):**

| Key | Patterns | Description |
|---|---|---|
| `chatbots` | 4 | Chatbots and conversational AI |
| `emotion_recognition` | 4 | Emotion recognition systems |
| `biometric_categorisation` | 3 | Biometric categorisation (non-sensitive) |
| `synthetic_content` | 6 | Synthetic content generation |

**AI Security Patterns (6 categories, 14 regex patterns):**

| Key | OWASP | Patterns | Description |
|---|---|---|---|
| `unsafe_deserialization` | LLM05 | 5 | Unsafe model deserialization (pickle.load, torch.load) |
| `prompt_injection_vulnerable` | LLM01 | 3 | Prompt injection vulnerability |
| `no_output_validation` | LLM02 | 2 | AI output used without validation |
| `hardcoded_model_path` | LLM03 | 2 | Hardcoded model paths |
| `unbounded_token_generation` | LLM10 | 1 | Unbounded token generation |
| `missing_temperature_control` | LLM09 | 1 | Missing temperature control |

**AI Indicators (4 categories):**
- `libraries` — Known AI library imports
- `model_files` — Model file extensions (.onnx, .pt, .safetensors, etc.)
- `api_endpoints` — AI API URL patterns
- `ml_patterns` — ML-specific code patterns

**Confidence scoring:** 0-100 numeric score based on number of indicators matched, weighted by pattern specificity. Thresholds: BLOCK >=80 or prohibited, WARN 50-79, INFO <50.

### Secret Detection (`scripts/credential_check.py`)

**9 patterns (6 high confidence, 3 medium):**

| Name | Confidence | Score | Pattern |
|---|---|---|---|
| `openai_api_key` | high | 95 | `sk-(?!ant-)[a-zA-Z0-9]{20,}` |
| `anthropic_api_key` | high | 95 | `sk-ant-[a-zA-Z0-9\-]{20,}` |
| `aws_access_key` | high | 95 | `AKIA[0-9A-Z]{16}` |
| `google_api_key` | high | 90 | `AIza[0-9A-Za-z\-_]{35}` |
| `github_token` | high | 95 | `gh[ps]_[A-Za-z0-9_]{36,}` |
| `private_key` | high | 98 | `-----BEGIN (?:RSA\|DSA\|EC\|OPENSSH )?PRIVATE KEY-----` |
| `generic_api_key` | medium | 60 | `(?i)(?:api[_-]?key\|...)[:=]\s*['"][A-Za-z0-9...]{20,}['"]` |
| `connection_string` | medium | 70 | `(?i)(?:mongodb\|postgres\|...)://(?!localhost)...` |
| `aws_secret_key` | medium | 75 | `(?i)aws.{0,20}(?:secret\|key).{0,20}['"][0-9a-zA-Z/+=]{40}['"]` |

### Multi-Language AST Engine (`scripts/ast_engine.py`)

**Language support (16 file extensions → 8 languages):**

| Extension | Language | Analysis Depth |
|---|---|---|
| `.py` | Python | Full AST (ast module) |
| `.js`, `.jsx`, `.cjs`, `.mjs` | JavaScript | tree-sitter AST (moderate depth) or regex fallback |
| `.ts`, `.tsx` | TypeScript | tree-sitter AST (moderate depth) or regex fallback |
| `.java` | Java | Regex import detection |
| `.go` | Go | Regex import detection |
| `.rs` | Rust | Regex import detection |
| `.c`, `.h` | C | Regex include detection |
| `.cpp`, `.cc`, `.cxx`, `.hpp` | C++ | Regex include detection |

**AI library registries:**
- JavaScript/TypeScript: 20 libraries (@openai, @anthropic-ai/sdk, @langchain, @tensorflow/tfjs, brain.js, chromadb, etc.)
- Java: 13 libraries (com.google.cloud.aiplatform, dev.langchain4j, ai.djl, org.tensorflow, etc.)
- Go: 9 libraries (go-openai, langchaingo, gomlx, gorgonia, spago, etc.)
- Rust: 39 crates (candle-core, burn, tch, async-openai, linfa, rust-bert, ort, safetensors, etc.)
- C/C++: 43 headers (tensorflow, torch, onnxruntime, opencv, dlib, llama.h, ggml.h, faiss, etc.)

**Unified output format per file:**
```json
{
  "filename": "app.py",
  "language": "python",
  "is_test_file": false,
  "context": "implementation",
  "ai_imports": ["torch", "transformers"],
  "has_ai_code": true,
  "data_flows": [{"source": "model.predict", "source_line": 42, "destinations": ["response"]}],
  "oversight": {"has_oversight": true, "oversight_patterns": ["human_review"], "oversight_score": 75},
  "logging": {"has_logging": true, "logging_patterns": ["logging.info"]}
}
```

### Compliance Gap Assessment (`scripts/compliance_check.py`)

Checks Articles 9-15 of the EU AI Act against actual project code:

| Article | Requirement | What It Checks |
|---|---|---|
| Article 9 | Risk Management | Risk assessment files, monitoring patterns, model evaluation |
| Article 10 | Data Governance | Data validation, bias checks, data lineage documentation |
| Article 11 | Technical Documentation | README, model cards, API docs, architecture documentation |
| Article 12 | Record-Keeping | Logging patterns, audit trail, event tracking |
| Article 13 | Transparency | User-facing disclosure, explainability, documentation accessibility |
| Article 14 | Human Oversight | Human-in-the-loop patterns, review-before-action, override mechanisms |
| Article 15 | Accuracy, Robustness, Cybersecurity | Test files, security measures, monitoring, credential management |

Scoring: 0-100% per article. STRONG >=70%, MODERATE 40-69%, WEAK <40%.

### Dependency Supply Chain Analysis (`scripts/dependency_scan.py`)

**7 dependency file parsers:**
1. `requirements.txt` — handles continuation lines, hash pinning, version specs
2. `pyproject.toml` — regex-based parsing (no tomllib), optional-dependencies
3. `package.json` — JSON parsing, dependencies + devDependencies
4. `Pipfile` — INI-like parsing
5. `Cargo.toml` — section detection, inline tables
6. `CMakeLists.txt` — regex extraction of find_package(), target_link_libraries()
7. `vcpkg.json` — JSON parsing

**10 lockfile formats detected:** Pipfile.lock, poetry.lock, uv.lock, package-lock.json, yarn.lock, pnpm-lock.yaml, bun.lockb, Cargo.lock, conda-lock.yml, requirements.txt (with hashes)

**Pinning quality scoring:** hash=100, exact=80, compatible=60, range=30, unpinned=0. AI deps weighted 3x. Lockfile adds +20 points. Capped at 100.

**Advisory checking:** Loads OSV-format YAML from `references/advisories/`. Matches normalised package names against known compromised packages.

### Framework Cross-Mapping (`scripts/framework_mapper.py`)

Maps findings to 10 compliance frameworks via `references/framework_crosswalk.yaml`:

1. **EU AI Act** — Primary (Articles 5, 6, 9-15, 50)
2. **NIST AI RMF 1.0** — Map, Measure, Manage, Govern
3. **ISO 42001:2023** — AI management system controls
4. **NIST CSF 2.0** — Cybersecurity framework
5. **SOC 2** — Trust service criteria
6. **ISO 27001:2022** — Information security controls
7. **OWASP LLM Top 10** — AI-specific security
8. **MITRE ATLAS** — AI attack techniques
9. **LGPD** — Brazil's General Data Protection Law
10. **Marco Legal da IA** — Brazil's AI legal framework

### Report Generation (`scripts/report.py`)

Three output formats:
- **HTML** — Self-contained single-file report with embedded CSS. For DPOs and compliance officers.
- **SARIF** — OASIS v2.1.0 compliant. For CI/CD integration and SIEM ingestion.
- **JSON** — Wrapped in standard envelope (`format_version: "1.0"`)

### Audit Trail (`scripts/log_event.py`)

- Append-only JSONL files at `~/.regula/audit/audit_YYYY-MM.jsonl`
- SHA-256 hash chain (each event includes `previous_hash`)
- Cross-platform file locking (Unix: fcntl, Windows: msvcrt)
- Event types: `classification`, `tool_use`, `blocked`
- AuditEvent dataclass: event_id, timestamp, session_id, project, data
- Self-attesting (not externally witnessed)
- `regula audit verify` — verify chain integrity
- `regula audit export` — export to CSV

---

## Data Sources

| Source | Location | Format | Purpose |
|---|---|---|---|
| Risk patterns | `scripts/classify_risk.py` (inline dicts) | Python dicts | Prohibited, high-risk, limited-risk, AI security patterns |
| AI indicators | `scripts/classify_risk.py` (inline dict) | Python dict | Library names, model file extensions, API endpoints, ML patterns |
| Secret patterns | `scripts/credential_check.py` (inline dict) | Python dict | 9 credential detection regexes |
| AI library registries | `scripts/ast_engine.py` (inline sets) | Python sets | 124 AI libraries across 5 language ecosystems |
| Framework crosswalk | `references/framework_crosswalk.yaml` | YAML | 10-framework compliance mapping |
| Security advisories | `references/advisories/` | YAML (OSV format) | Known compromised AI packages |
| EU AI Act articles | `references/eu_ai_act_articles_9_15.md` | Markdown | Article text for gap assessment |
| News feeds | `scripts/feed.py` (inline list) | RSS/Atom URLs | 7 AI governance news sources |
| Policy config | `regula-policy.yaml` | YAML | User-configurable thresholds, exclusions, overrides |
| Audit trail | `~/.regula/audit/audit_YYYY-MM.jsonl` | JSONL | Hash-chained classification events |
| Baseline | `.regula-baseline.json` | JSON | CI/CD compliance baseline state |

**No external API calls.** All pattern matching, classification, and analysis runs offline against local data.

---

## CLI Commands (28 subcommands)

| Command | Purpose | Key Flags |
|---|---|---|
| `check <path>` | Scan files for risk indicators | `--format json\|sarif\|text`, `--strict`, `--diff`, `--skip-tests`, `--min-tier` |
| `classify` | Classify text input | `--input`, `--file`, stdin pipe |
| `report` | Generate HTML/SARIF/JSON reports | `--format html\|sarif\|json`, `--output`, `--project` |
| `audit` | Manage audit trail | `verify`, `export --format csv\|json` |
| `discover` | Discover AI systems in project | `--project`, `--org`, `--format` |
| `install` | Install hooks for platform | `claude-code\|copilot-cli\|windsurf\|pre-commit\|git-hooks` |
| `status` | Show system registry status | `--format` |
| `init` | Guided setup wizard | `--interactive`, `--dry-run`, `--project` |
| `feed` | AI governance news | `--format html\|json\|text`, `--output` |
| `questionnaire` | Context-driven risk assessment | `--evaluate`, `--exemption`, `--format` |
| `session` | Session-level risk aggregation | `--format` |
| `baseline` | CI/CD baseline comparison | `save\|compare`, `--fail-on-new` |
| `docs` | Generate documentation scaffolds | `--project`, `--qms`, `--format` |
| `compliance` | Manage compliance status | `update\|history\|workflow`, `--system`, `--status` |
| `gap` | Compliance gap assessment (Art 9-15) | `--project`, `--article`, `--strict`, `--format` |
| `benchmark` | Precision/recall validation | `--project`, `--manifest`, `--metrics` |
| `timeline` | EU AI Act enforcement dates | `--format` |
| `deps` | AI dependency supply chain analysis | `--project`, `--strict`, `--format` |
| `sbom` | CycloneDX 1.6 SBOM generation | `--project`, `--name`, `--output`, `--format` |
| `agent` | Agentic AI governance monitoring | `--check-mcp`, `--config-file`, `--format` |
| `doctor` | Installation health check | `--format json\|text` |
| `self-test` | Verify installation works | (no flags) |
| `mcp-server` | Start Regula MCP server (stdio) | (no flags) |
| `bias` | Evaluate model bias (CrowS-Pairs) | `--model`, `--format` |
| `metrics` | Show local usage statistics | `--format` |
| `security-self-check` | Verify Regula's own source is clean | (no flags) |
| `inventory` | Scan for AI model references (GPAI) | `--project`, `--format` |
| `config` | Config management (validate) | `validate` |

**Exit codes (scanner convention, research-validated):**
- `0` — Success, or findings below WARN threshold (confidence < 50 = INFO tier, non-actionable)
- `1` — BLOCK or WARN tier findings detected (confidence >= 50, or prohibited pattern)
- `2` — Tool error (bad config, missing path, parse failure, usage error)
- `130` — Interrupted (Ctrl+C)

**Threshold logic:** A finding's confidence score (0-100) determines its tier: BLOCK >= 80 or prohibited, WARN 50-79, INFO < 50. Only BLOCK and WARN trigger exit 1. INFO findings are reported but exit 0.

**JSON output envelope (all `--format json`):**
```json
{
  "format_version": "1.0",
  "regula_version": "1.2.0",
  "command": "check",
  "timestamp": "2026-03-28T14:30:00Z",
  "exit_code": 0,
  "data": { ... }
}
```

---

## Hook System

### PreToolUse Hook (`hooks/pre_tool_use.py`, 321 lines)

Intercepts Write, Edit, Bash, and MultiEdit tool calls before execution:

1. **Documentation bypass:** Files with doc extensions (.md, .txt, .rst, .html, .json, .yaml, .yml) skip classification
2. **Directory bypass:** Files in docs/, references/, course/, guides/, tutorials/ skip classification
3. **Suppression bypass:** Content containing `# regula-ignore` skips classification
4. **Secret blocking:** Checks for high-confidence credential patterns (6 providers)
5. **Prohibited blocking:** Checks for Article 5 prohibited practice patterns
6. **High-risk warning:** Flags Annex III high-risk patterns (non-blocking by default)
7. **GPAI detection:** Flags general-purpose AI training activity (Articles 53-55)
8. **Audit logging:** Logs every classification to the audit trail

**Blocking behavior:** Returns exit code 2 with structured error message for prohibited practices and high-confidence secrets. Returns exit code 0 (allow) for everything else including high-risk (configurable).

### PostToolUse Hook (`hooks/post_tool_use.py`)

Logs completed tool executions to the audit trail. Non-blocking.

### Stop Hook (`hooks/stop_hook.py`)

Writes session summary to audit trail on termination. Non-blocking.

---

## EU AI Act Timeline

| Date | Event | Status |
|---|---|---|
| 2024-08-01 | EU AI Act entered into force | Effective |
| 2025-02-02 | Article 5 prohibited practices apply | Effective |
| 2025-08-02 | General-purpose AI model rules apply | Effective |
| 2026-02-02 | Article 6 guidance deadline (MISSED) | Overdue |
| 2026-08-02 | High-risk AI system requirements (Articles 9-15) | Current law |
| 2026-10-30 | prEN 18286 (QMS) public enquiry closes | In progress |
| 2027-12-02 | Proposed: Annex III systems deadline (Digital Omnibus) | Proposed |
| 2028-08-02 | Proposed: Annex I systems deadline (Digital Omnibus) | Proposed |

---

## AI Governance News Feed Sources

| Source | URL | Focus |
|---|---|---|
| IAPP | iapp.org/rss/news.xml | Privacy and data protection |
| NIST | nist.gov/blogs/cybersecurity-insights/rss.xml | AI standards and frameworks |
| EU AI Act Updates | artificialintelligenceact.eu/feed/ | EU AI Act developments |
| MIT Technology Review | technologyreview.com/feed/ | AI technology trends |
| Future of Life Institute | futureoflife.org/feed/ | AI safety |
| Help Net Security | helpnetsecurity.com/feed/ | Cybersecurity |
| EFF | eff.org/rss/updates.xml | Digital rights |

---

## Configuration (`regula-policy.yaml`)

```yaml
version: "1.0"
organisation: "Your Organisation"

governance:
  ai_officer:                    # Natural person accountable (Article 4(1))
    name: ""
    role: ""
    email: ""
  dpo:                           # Data Protection Officer (optional)
    name: ""
    email: ""

regulatory_basis:
  eu_ai_act_version: "2024/1689"
  pattern_version: "1.1.0"
  last_reviewed: "2026-03-25"

frameworks:
  - eu_ai_act                    # Currently active

rules:
  risk_classification:
    force_high_risk: []           # Force specific patterns to high-risk
    exempt: []                    # Exempt patterns (cannot override Article 5)
  logging:
    retention_years: 10
    export_format: [json, csv]

thresholds:
  block_on_prohibited: true
  block_on_high_risk: false
  min_dependency_pinning_score: 50
  min_confidence: 0
  block_above: 80                # BLOCK tier threshold
  warn_above: 50                 # WARN tier threshold

exclusions:
  paths: ["tests/", "docs/", "examples/"]
  patterns: ["test_*.py", "*_test.py", "*.spec.ts"]
```

---

## GitHub Action (`action.yml`)

**Inputs:**
- `path` — Directory to scan (default: `.`)
- `format` — Output format: `text`, `json`, `sarif` (default: `text`)
- `framework` — Compliance framework (default: `eu-ai-act`)
- `fail-on-prohibited` — Exit 1 on prohibited findings (default: `true`)
- `fail-on-high-risk` — Exit 1 on high-risk findings (default: `false`)
- `min-dependency-score` — Minimum pinning score (default: `0`)
- `diff-mode` — Only scan changed files (default: `false`)
- `upload-sarif` — Upload SARIF to GitHub Security (default: `false`)

**Outputs:**
- `findings-count`, `prohibited-count`, `high-risk-count`, `pinning-score`, `sarif-file`

---

## Current Phase

**v1.2.0 shipped 2026-03-28.** 435 tests, 1,044 assertions. Real-world validated against LangChain (2,450 files, 16s scan). Agent autonomy detection wired into `check`. `--skip-tests` and `--min-tier` flags reduce signal-to-noise. Bias testing via CrowS-Pairs. 10-framework compliance mapping. No external users yet. GitHub Action defined but untested in a real PR workflow.

---

## Known Issues

- Zero TODO/FIXME/HACK markers in codebase
- `text_to_image` false positive on instructor library (known, documented in audit reports)
- GitHub Action untested in a real PR workflow
- Dependency pinning score of 30/100 on Regula's own optional deps
- JS/TypeScript analysis is regex-only (tree-sitter path exists but shallow vs Python AST)
- Cross-file data flow not supported — all tracing is single-file only

---

## CLAUDE.md Summary

Global rules (`~/.claude/CLAUDE.md`):
1. Never claim a fix is done without verification — run the verify command and confirm
2. Every number, count, or quantitative claim must be verified against actual source before stating (anti-inflation rule added 2026-03-28)
3. Never relay numbers from sub-agents without re-verifying
4. Test-driven bug fixing mandatory (write failing test → fix → verify)
5. Never make unverified competitive claims
6. British English in all copy
7. Severity language must match reality — no inflating 6 occurrences as "widespread"
8. When corrected on a number, acknowledge the error explicitly

---

## Skills in Use

- `SKILL.md` — Defines Regula as a Claude Code skill (risk tiers, commands, limitations)
- `hooks/pre_tool_use.py` — Real-time PreToolUse interception
- `hooks/post_tool_use.py` — PostToolUse audit logging
- `hooks/stop_hook.py` — Session termination handling

---

## User Archetypes

1. **AI developers** — Building systems that use AI libraries. Need to know if their code triggers EU AI Act obligations. Run `regula check .` during development.
2. **Compliance officers / DPOs** — Reviewing AI projects for regulatory compliance. Use `regula gap --project .` and `regula report --format html`.
3. **CI/CD pipelines** — Automated scanning on every PR. Use `regula check --format sarif .` with GitHub Action or `regula baseline compare --fail-on-new`.
4. **AI coding agent users** — Using Claude Code, Copilot, or Windsurf. Hooks intercept tool calls in real-time, blocking prohibited patterns before they're written.

---

## Key User Journeys

**1. First-time setup:**
```
regula init --dry-run          # See what init would do (read-only)
regula init                    # Create policy, install hooks
regula doctor                  # Verify installation
regula self-test               # Verify classification works
regula check .                 # First scan
```

**2. Daily development (with hooks):**
```
# Hooks run automatically on every Write/Edit/Bash in Claude Code
# Prohibited patterns → blocked with Article 5 citation
# High-risk patterns → warned (non-blocking by default)
# Credentials → blocked
# All classifications → logged to audit trail
```

**3. CI/CD integration:**
```
regula check --format sarif .              # Generate SARIF
regula baseline save                       # Save baseline
regula baseline compare --fail-on-new      # Fail on new findings
regula deps --project . --strict           # Fail if pinning < 50
```

**4. Compliance assessment:**
```
regula gap --project .                     # Full Articles 9-15 assessment
regula gap --project . --article 14        # Check specific article
regula docs --project . --qms             # Generate documentation scaffolds
regula discover --project .               # Discover AI systems
regula compliance update -s MyApp --status assessment
```

**5. Audit and reporting:**
```
regula report --format html -o report.html    # HTML report for stakeholders
regula audit verify                           # Verify audit chain integrity
regula audit export --format csv              # Export for external audit
regula sbom --project . -o sbom.json          # CycloneDX SBOM
```
