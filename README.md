# Regula

**AI Governance Risk Indication for Code**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE.txt)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![EU AI Act](https://img.shields.io/badge/EU%20AI%20Act-Risk%20Indication-blue.svg)](#regulatory-coverage)
[![CI](https://github.com/kuzivaai/getregula/actions/workflows/ci.yaml/badge.svg)](https://github.com/kuzivaai/getregula/actions)

Regula is a static analysis tool that detects AI governance risk indicators in source code. It flags patterns associated with EU AI Act risk tiers, warns about patterns matching prohibited practices, and maintains a hash-chained audit trail.

## What Regula Is (and Isn't)

**Regula is:**
- A development-time static analysis tool that detects AI-related code patterns and maps them to EU AI Act obligations
- A shift-left compliance scanner — like ESLint for regulatory risk, running in your terminal or CI/CD pipeline
- A starting point for compliance awareness, not a finish line

**Regula is not:**
- A runtime monitoring system (it analyses source code, not running systems)
- A legal compliance certificate (findings are indicators, not legal determinations)
- A replacement for enterprise GRC platforms like Credo AI or Holistic AI (it complements them)
- A bias or fairness testing tool (it detects code patterns, not model behaviour)
- Legal advice (consult qualified legal counsel for compliance decisions)

Regula helps development teams understand their EU AI Act exposure early. It does not replace the organisational, procedural, and legal work required for full compliance.

## Quick Start

```bash
git clone https://github.com/kuzivaai/getregula.git
cd getregula

# Guided setup (detects platform, installs hooks, runs first scan)
python3 scripts/cli.py init

# Or install manually for your platform:
python3 scripts/cli.py install claude-code     # Claude Code
python3 scripts/cli.py install copilot-cli     # GitHub Copilot CLI
python3 scripts/cli.py install windsurf        # Windsurf Cascade

# Scan a project
python3 scripts/cli.py check /path/to/project

# Generate an HTML report for your DPO
python3 scripts/cli.py report --format html --output report.html --include-audit
```

Or install via pip:
```bash
pip install -e .
regula init
regula check .
```

Run tests: `python3 tests/test_classification.py`

## What It Does

When you write AI-related code, Regula:

1. **Detects** AI indicators (libraries, model files, API calls, ML patterns)
2. **Flags** patterns associated with EU AI Act risk tiers
3. **Blocks** patterns matching Article 5 prohibited practices (with conditions and exceptions)
4. **Warns** about patterns in Annex III high-risk areas (with Article 6 context)
5. **Blocks** hardcoded API keys in tool inputs (OpenAI, Anthropic, AWS, GitHub)
6. **Notes** GPAI transparency obligations when training patterns are detected
7. **Logs** everything to a hash-chained audit trail
8. **Generates** Annex IV technical documentation and QMS scaffolds
9. **Tracks** compliance status across registered AI systems

### Example: High-Risk Indicator

```
User: "Build a CV screening function that auto-filters candidates"

Regula: HIGH-RISK AI SYSTEM INDICATORS DETECTED

Category: Annex III, Category 4 — Employment and workers management
Patterns: cv_screen

Whether Articles 9-15 apply depends on whether the system poses a
significant risk of harm (Article 6). Systems performing narrow
procedural tasks or supporting human decisions may be exempt.

If this IS a high-risk system, these requirements apply (Aug 2026):
  Art 9:  Risk management system
  Art 10: Data governance
  Art 14: Human oversight mechanism
  ...
```

### Example: Prohibited Pattern Block

```
User: "Build a social credit scoring system"

Regula: PROHIBITED AI PRACTICE — ACTION BLOCKED

Prohibition: Social scoring by public authorities or on their behalf
Pattern detected: social_scoring

This is a pattern-based risk indication, not a legal determination.
If this is a false positive or an exception applies, document the
justification and consult your DPO.
```

## Important Limitations

Regula performs **pattern-based risk indication**, not legal risk classification.

- The EU AI Act classifies risk based on intended purpose and deployment context (Article 6), not code patterns
- False positives will occur (code that discusses prohibited practices triggers indicators)
- False negatives will occur (novel risk patterns not in the database)
- Article 5 prohibitions have conditions and exceptions that require human judgment
- The audit trail is self-attesting (locally verifiable, not externally witnessed)
- Not a substitute for legal advice or DPO review

## Regulatory Context

The EU AI Act (Regulation 2024/1689) is now in force:

| Date | Requirement |
|------|-------------|
| **2 February 2025** | Prohibited AI practices (Article 5) apply |
| **2 August 2025** | General-purpose AI model rules apply |
| **2 August 2026** | High-risk system requirements (Articles 9-15) fully apply |

Penalties: up to EUR 35 million or 7% of global annual turnover.

## Regulatory Coverage

### Risk Tiers

| Tier | Action | Examples |
|------|--------|----------|
| **Prohibited** | Block | Social scoring, emotion in workplace, real-time biometric ID, race detection |
| **High-Risk** | Warn + Requirements | CV screening, credit scoring, medical diagnosis, biometrics, education |
| **Limited-Risk** | Transparency note | Chatbots, deepfakes, age estimation, emotion recognition |
| **Minimal-Risk** | Log only | Spam filters, recommendations, code completion |

### Prohibited Practices (Article 5)

All 8 Article 5 categories are detected. Each message includes the specific conditions under which the prohibition applies and any narrow exceptions from the Act.

### High-Risk Areas (Annex III)

All 10 Annex III categories are detected. Messages include Article 6 context: matching an Annex III area does NOT automatically mean a system is high-risk. Systems performing narrow procedural tasks or supporting human decisions may be exempt (Article 6(3)).

## Supported Platforms

| Platform | Status | Install Command |
|----------|--------|----------------|
| **Claude Code** | Supported | `python3 scripts/install.py claude-code` |
| **GitHub Copilot CLI** | Supported | `python3 scripts/install.py copilot-cli` |
| **Windsurf Cascade** | Supported | `python3 scripts/install.py windsurf` |
| **pre-commit** | Supported | `python3 scripts/install.py pre-commit` |
| **Git hooks** | Supported | `python3 scripts/install.py git-hooks` |
| **CI/CD (GitHub Actions, GitLab)** | Via SARIF | `regula check --format sarif` |

Claude Code, Copilot CLI, and Windsurf use the same hook protocol. Regula's hooks work across all three with only the config file differing.

## CLI Usage

```bash
# Scan a project for risk indicators
python3 scripts/cli.py check .
python3 scripts/cli.py check . --format json
python3 scripts/cli.py check . --format sarif    # For CI/CD integration
python3 scripts/cli.py check . --ci              # Exit 1 on any WARN or BLOCK finding
python3 scripts/cli.py check . --strict          # Exit 1 on WARN-tier findings

# Classify a text input
python3 scripts/cli.py classify --input "import tensorflow; cv screening model"

# Generate reports
python3 scripts/cli.py report --format html -o report.html --include-audit
python3 scripts/cli.py report --format sarif -o results.sarif.json

# Generate documentation scaffolds
python3 scripts/cli.py docs --project .                     # Annex IV only
python3 scripts/cli.py docs --project . --qms               # Annex IV + QMS
python3 scripts/cli.py docs --project . --all -o compliance  # All types

# Discover AI systems and register them
python3 scripts/cli.py discover --project . --register
python3 scripts/cli.py status

# Compliance status tracking
python3 scripts/cli.py compliance                           # View all systems
python3 scripts/cli.py compliance workflow                  # Show workflow
python3 scripts/cli.py compliance update -s MyApp --status assessment --note "Starting review"
python3 scripts/cli.py compliance history -s MyApp          # View history

# Audit trail management
python3 scripts/cli.py audit verify
python3 scripts/cli.py audit export --format csv -o audit.csv

# Compliance gap assessment (Articles 9-15)
python3 scripts/cli.py gap --project .
python3 scripts/cli.py gap --project . --article 14   # Article 14 only

# Real-world validation benchmark
python3 scripts/cli.py benchmark --project .
python3 scripts/cli.py benchmark --project . -f csv -o findings.csv

# Install hooks for a platform
python3 scripts/cli.py install claude-code
python3 scripts/cli.py install copilot-cli
python3 scripts/cli.py install list
```

### Compliance Gap Assessment

AST-powered compliance gap analysis checks whether your project has the required compliance infrastructure for Articles 9-15. Uses Python `ast` module for structure-aware analysis — distinguishes test files from implementation, traces where AI model outputs flow, and detects human oversight mechanisms.

```bash
regula gap --project .                   # Full assessment
regula gap --project . --article 14      # Article 14 (human oversight) only
regula gap --project . --format json     # Machine-readable output
regula gap --project . --strict          # Exit 1 if score < 50 (CI/CD gate)
```

Example output:
```
Article 12  Record-Keeping       [100%] STRONG
  Evidence: Structured logging in 5/7 AI files, audit trail configured
Article 14  Human Oversight      [ 20%] WEAK
  Evidence: No review/approve functions found
  Gap: AI model output flows directly to return without human review
  Gap: AST: 3 automated decision paths with no oversight mechanism
```

### AI Dependency Pinning Analysis

Checks whether your AI dependencies are properly pinned — addressing the class of attack demonstrated by the LiteLLM supply chain incident (March 2026).

```bash
regula deps --project .                   # Full dependency analysis
regula deps --project . --format json     # Machine-readable output
regula deps --project . --strict          # Exit 1 if pinning score < 50 (CI/CD gate)
```

Checks: pinning quality (hash > exact > range > unpinned), lockfile presence, AI dependencies weighted 3x in scoring. Parses 7 dependency file formats (requirements.txt, pyproject.toml, package.json, Pipfile, Cargo.toml, CMakeLists.txt, vcpkg.json).

**Note:** This is a pinning hygiene checker, not a vulnerability scanner. For comprehensive vulnerability scanning, complement with `pip-audit` or `osv-scanner`.

### Cross-Framework Compliance Mapping

Regula maps findings to 8 compliance frameworks internally: EU AI Act, NIST AI RMF 1.0, ISO 42001:2023, NIST CSF 2.0, SOC 2, ISO 27001:2022, OWASP Top 10 for LLMs, and MITRE ATLAS. Framework mappings appear in check findings and gap assessments automatically.

### Real-World Validation Benchmark

Measure Regula's precision and recall against real codebases. Outputs CSV for manual labelling, then calculates metrics from labelled data.

```bash
regula benchmark --project /path/to/project                    # Scan
regula benchmark --project /path/to/project -f csv -o out.csv  # CSV for labelling
regula benchmark --metrics labelled.csv                        # Precision/recall
```

### Inline Suppression

Add `# regula-ignore` to any file to suppress all findings for that file, or `# regula-ignore: RULE_ID` to suppress a specific rule. Suppressions are tracked and visible in reports.

```python
# regula-ignore: employment
import sklearn
# This CV screening tool is a research prototype, not deployed
```

### Governance News Feed

Curated AI governance news from 7 sources (IAPP, NIST, EU AI Act Updates, MIT Technology Review, Future of Life Institute, Help Net Security, EFF). Keyword-filtered, deduplicated, cached.

```bash
regula feed                              # CLI text output
regula feed --format html -o feed.html   # HTML digest for stakeholders
regula feed --sources                    # List sources with authority notes
regula feed --days 30                    # Last 30 days
```

### Questionnaire Mode

When pattern-based classification is ambiguous, gather context about intended purpose and deployment via structured questions derived from Article 6 criteria.

```bash
regula questionnaire                     # Show questions
regula questionnaire --evaluate '{...}'  # Evaluate answers (JSON)
```

### Session Risk Aggregation

Aggregate individual tool classifications into a session-level risk profile for agentic AI governance.

```bash
regula session                           # Current session profile
regula session --hours 24 --format json  # Last 24 hours as JSON
```

### CI/CD Baseline Comparison

Save a compliance baseline and only report net-new findings on subsequent scans.

```bash
regula baseline save                     # Save current state
regula baseline compare --fail-on-new    # Fail CI on new findings
```

### GitHub Action

Integrate Regula into your CI/CD pipeline with one step:

```yaml
- name: Regula AI Governance Check
  uses: kuzivaai/getregula@v1
  with:
    path: "."
    fail-on-prohibited: "true"
    fail-on-high-risk: "false"
```

Results appear in the GitHub Security tab alongside CodeQL findings.

**Inputs:**

| Input | Default | Description |
|-------|---------|-------------|
| `path` | `.` | Path to the project to scan |
| `format` | `sarif` | Output format: `sarif` or `json` |
| `fail-on-prohibited` | `true` | Exit 2 if prohibited-use findings detected |
| `fail-on-high-risk` | `false` | Exit 1 if high-risk findings detected |
| `min-dependency-score` | `0` | Minimum dependency pinning score (0–100) |
| `diff-mode` | `false` | Only scan files changed in this PR |
| `upload-sarif` | `true` | Upload SARIF to GitHub Code Scanning |

**Outputs:** `findings-count`, `prohibited-count`, `high-risk-count`, `pinning-score`, `sarif-file`

### Compliance Status Tracking

Track compliance progress across registered AI systems through a defined workflow.

```bash
regula compliance                        # View all systems
regula compliance workflow               # Show status workflow
regula compliance update -s MyApp --status assessment --note "DPO review initiated"
regula compliance history -s MyApp       # View transition history
```

**Workflow:** `not_started` → `assessment` → `implementing` → `compliant` → `review_due`

All transitions are logged to the audit trail with timestamps and notes.

### Documentation Generation

Generate Annex IV technical documentation scaffolds and Quality Management System (QMS) templates per Article 17.

```bash
regula docs --project .                  # Annex IV scaffold
regula docs --project . --qms           # Annex IV + QMS scaffold
regula docs --project . --all           # All documentation types
```

QMS scaffolds cover all Article 17 requirements: governance accountability, development procedures, testing/validation, data management, risk management, post-market monitoring, human oversight, and transparency.

### EU AI Act Timeline

Current enforcement dates with Digital Omnibus status.

```bash
regula timeline                          # Display timeline
regula timeline --format json            # Machine-readable
```

## Architecture

```
regula/
├── SKILL.md                       # Core skill file (Claude Code)
├── scripts/
│   ├── cli.py                     # Unified CLI entry point
│   ├── classify_risk.py           # Risk indication engine (confidence scoring)
│   ├── log_event.py               # Audit trail (hash-chained, file-locked)
│   ├── report.py                  # HTML + SARIF report generator
│   ├── install.py                 # Multi-platform hook installer
│   ├── feed.py                    # Governance news aggregator (7 sources)
│   ├── questionnaire.py           # Context-driven risk assessment
│   ├── session.py                 # Session-level risk aggregation
│   ├── baseline.py                # CI/CD baseline comparison
│   ├── timeline.py                # EU AI Act enforcement dates
│   ├── generate_documentation.py  # Annex IV + QMS scaffold generator
│   ├── discover_ai_systems.py     # AI system discovery, registry, compliance tracking
│   ├── credential_check.py        # Secret detection (9 patterns: 6 high + 3 medium confidence)
│   ├── ast_analysis.py            # AST-based Python analysis (data flow, oversight, logging)
│   ├── ast_engine.py              # Multi-language AST engine (Python + JS/TS tree-sitter + Java/Go/Rust/C/C++ regex)
│   ├── compliance_check.py        # Compliance gap assessment (Articles 9-15)
│   ├── dependency_scan.py         # AI dependency supply chain security
│   ├── framework_mapper.py        # Cross-framework compliance mapping (8 frameworks)
│   ├── remediation.py             # Inline fix suggestions per Annex III category
│   ├── agent_monitor.py           # Agentic AI governance (autonomy scoring, MCP config)
│   ├── sbom.py                    # CycloneDX 1.6 AI SBOM generation
│   └── benchmark.py               # Real-world precision/recall validation
├── hooks/
│   ├── pre_tool_use.py            # PreToolUse hook (CC/Copilot/Windsurf)
│   ├── post_tool_use.py           # PostToolUse logging hook
│   └── stop_hook.py               # Session summary hook
├── references/                    # Regulatory reference documents
│   ├── owasp_llm_top10.yaml       # OWASP Top 10 for LLMs → EU AI Act mapping
│   └── mitre_atlas.yaml           # MITRE ATLAS → EU AI Act mapping
├── tests/
│   └── test_classification.py     # 160 tests, 472 assertions
├── docs/
│   └── course/                    # Interactive 10-module governance course
├── regula-policy.yaml             # Policy configuration template
└── .github/workflows/ci.yaml     # CI/CD
```

### Language Support

| Language | Analysis Depth | What It Detects |
|----------|---------------|-----------------|
| **Python** | Full AST | Data flow tracing, human oversight detection, logging practices, function/class extraction |
| **JavaScript/TypeScript** | Moderate (tree-sitter) | Import extraction, data flow tracing, oversight detection, logging. Tree-sitter optional — falls back to regex. |
| **Java** | Import detection (regex) | 13 AI libraries (Google AI Platform, LangChain4j, DJL, etc.) |
| **Go** | Import detection (regex) | 9 AI libraries (go-openai, langchaingo, etc.) |
| **Rust** | Import detection (regex) | 39 AI crates (candle, burn, tch, async-openai, etc.) + Cargo.toml parsing |
| **C/C++** | Include detection (regex) | 43 AI headers (LibTorch, TensorFlow, ONNX Runtime, llama.cpp, etc.) + CMake/vcpkg parsing |

**Honest note:** Only Python has deep AST analysis with data flow tracing. JS/TS with tree-sitter is moderate depth. Java, Go, Rust, C, C++ are regex-based import/include detection — they identify AI library usage but cannot trace data flow or detect oversight patterns.

### Design Principles

- **Core engine + thin adapters.** One classification engine, multiple platform integrations.
- **Same hook protocol.** Claude Code, Copilot CLI, and Windsurf all use stdin/stdout JSON with exit codes.
- **Confidence scores, not binary labels.** 0-100 numeric scoring because 40% of AI systems have ambiguous classification (appliedAI study).
- **Inline suppression with audit trail.** `# regula-ignore` works like `// nosemgrep` — finding is tracked but not reported as active.
- **SARIF for CI/CD.** Standard format consumed by GitHub, GitLab, Azure DevOps security dashboards.
- **Named accountability.** Policy file supports AI Officer and DPO fields per Article 4(1) and ISO 42001.
- **Compliance workflow.** Tracked status progression with audit trail and transition history.
- **AST over regex where it matters.** Python `ast` module provides structure-aware analysis: real imports vs string mentions, data flow tracing, human oversight detection. Regex remains for cross-language pattern matching.
- **Compliance gap assessment, not just risk flagging.** Checks whether Articles 9-15 compliance infrastructure actually exists in the codebase.
- **AI-specific supply chain security.** Dependency pinning checks focus on AI libraries, not general packages.
- **Cross-platform.** Unix/macOS (`fcntl`) and Windows (`msvcrt`) file locking. No platform restrictions.
- **Multi-framework mapping.** 8 frameworks (EU AI Act, NIST AI RMF, ISO 42001, NIST CSF 2.0, SOC 2, ISO 27001, OWASP LLM Top 10, MITRE ATLAS) mapped via a single crosswalk data file.

## Configuration

Copy `regula-policy.yaml` to your project root and customise:

```yaml
version: "1.0"
organisation: "Your Organisation"

governance:
  ai_officer:
    name: "Jane Smith"
    role: "Chief AI Ethics Officer"
    email: "jane.smith@company.com"
  dpo:
    name: "John Doe"
    email: "dpo@company.com"

rules:
  risk_classification:
    force_high_risk: []       # Always treat as high-risk
    exempt: []                # Confirmed low-risk (cannot exempt prohibited)
```

Policy exemptions **cannot override** Article 5 prohibited practice detection. Prohibited checks always run first regardless of policy configuration.

For full YAML support, install pyyaml: `pip install pyyaml`. Without it, a minimal YAML subset parser is used. Alternatively, use `regula-policy.json`.

## Testing

```bash
python3 tests/test_classification.py
```

160 tests, 472 assertions covering:
- AI detection (libraries, model files, API endpoints, ML patterns)
- All 8 prohibited practices
- All 10 high-risk categories (Annex III)
- Limited-risk and minimal-risk scenarios
- Edge cases (empty input, case insensitivity, priority ordering)
- Policy engine (force_high_risk, exempt, prohibited override safety)
- Audit trail (hash chain integrity, CSV export)
- Confidence scoring (numeric scores, tier ordering, multi-indicator bonus)
- Reports (SARIF structure, HTML disclaimer, inline suppression)
- Questionnaire (generation, high-risk evaluation, minimal-risk evaluation)
- Session aggregation, baseline comparison, timeline data accuracy
- Secret detection (OpenAI/AWS keys, no false positives, redaction)
- GPAI training detection (training vs inference distinction)
- Compliance status workflow (transitions, history, audit logging)
- QMS scaffold generation
- AST analysis (import detection, context classification, data flow tracing)
- Human oversight detection (Article 14) via AST
- Logging practice detection (Article 12) via AST
- Compliance gap assessment (Articles 9-15 evidence checks)
- Cross-platform file locking (Unix + Windows)
- Regulatory version pinning

## Constraints

- **No required external dependencies** — stdlib only (pyyaml optional; tree-sitter optional for JS/TS AST, regex fallback when not installed)
- **Language support** — Python (full AST), JavaScript/TypeScript (tree-sitter AST + regex fallback), Java (regex, 13 AI libraries), Go (regex, 9 AI libraries), Rust (regex, 39 AI crates), C/C++ (regex, 43 AI headers)
- **Python 3.10+**
- **Works offline** — no API calls required
- **Cross-platform** — Unix, macOS, and Windows supported
- **Append-only audit** — no deletion capability
- **File-locked writes** — safe under concurrent hook execution (fcntl on Unix, msvcrt on Windows)

## Roadmap

- **v1.2:** Production readiness (error handling, `regula doctor`, `regula self-test`, JSON output envelope)
- **v1.3:** DPO dashboard, Slack/Teams alerting, external timestamp authority, PDF export
- **v2.0:** Model card generation, bias testing integration

## License

MIT License. See [LICENSE.txt](LICENSE.txt).

## Author

Built by [The Implementation Layer](https://theimplementationlayer.substack.com) — AI governance from the practitioner side.
