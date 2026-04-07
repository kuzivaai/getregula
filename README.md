# Regula

**AI Governance Risk Indication for Code**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE.txt)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![EU AI Act](https://img.shields.io/badge/EU%20AI%20Act-Risk%20Indication-blue.svg)](#regulatory-coverage)
[![CI](https://github.com/kuzivaai/getregula/actions/workflows/ci.yaml/badge.svg)](https://github.com/kuzivaai/getregula/actions)

If you ship an AI product to EU users, the EU AI Act applies to you — regardless of where you are based or how small your team is. Article 2 is extraterritorial: it covers any provider whose system is used in the EU.

Regula scans your code for risk indicators, tells you which tier your system falls into, and flags what you need to do before the August 2026 deadline. Most solo founders building chatbots or productivity tools will land in the limited-risk tier — meaning lightweight transparency obligations under Article 50, not the full Annex III high-risk requirements. Regula tells you that clearly, rather than leaving you guessing.

## Who Is This For?

- **Solo founders and indie hackers** building AI products (with Claude Code, Cursor, Lovable, Bolt, or similar) who have EU users and are not sure what the EU AI Act means for them
- **Small teams** who want to understand their compliance exposure before it becomes a sales blocker — enterprise procurement is already asking for AI Act evidence
- **Engineering teams** who want to add EU AI Act scanning to CI/CD and catch high-risk or prohibited patterns before they ship

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
pip install -e .

# First: find out if and how the EU AI Act applies to your product
# A few yes/no questions, no code required
regula assess

# Then: scan your codebase for risk indicators
regula check /path/to/project

# Generate an HTML report for your DPO or enterprise customer
regula report --format html --output report.html --include-audit
```

Or clone and run without installing:
```bash
# Guided setup (detects platform, installs hooks, runs first scan)
python3 scripts/cli.py init

# Install hooks for your editor
python3 scripts/cli.py install claude-code     # Claude Code
python3 scripts/cli.py install copilot-cli     # GitHub Copilot CLI
python3 scripts/cli.py install windsurf        # Windsurf Cascade
```

Run tests: `pytest tests/ -q`

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
10. **Produces** conformity assessment evidence packs (Article 43) with per-article readiness scoring
11. **Traces** AI model outputs across files to detect human oversight gaps (Article 14)
12. **Creates** AI Bills of Materials with model provenance and GPAI tier annotations (CycloneDX 1.6)

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

## Why Regula?

Several EU AI Act tools exist. Here is an honest comparison with the closest ones.

| | Regula | [Systima Comply](https://dev.to/systima/open-source-eu-ai-act-compliance-scanning-for-cicd-4ogj) | [AIR Blackbox](https://github.com/airblackbox) | [EuConform](https://github.com/Hiepler/EuConform) | [ark-forge MCP](https://github.com/ark-forge/mcp-eu-ai-act) |
|---|---|---|---|---|---|
| **Type** | CLI + pre-commit/git hooks | npm CLI + GitHub Action | MCP server | Web app (browser) | MCP server |
| **Python analysis** | Full AST (data flow, oversight) | Unknown | Runtime tracing | None | Regex only |
| **JS/TS analysis** | Moderate (tree-sitter) | **AST + 37 frameworks + call-chain** | LangChain/OpenAI focus | None | Regex only |
| **Hook integration** | Claude Code, Copilot CLI, Windsurf | CI/CD only | Cursor, Claude Desktop | None | Cursor, Claude Desktop |
| **Offline / no deps** | Yes (stdlib only) | Requires npm | Requires MCP client | Browser + Ollama | Single dep (mcp) |
| **Gap assessment** | Articles 9-15 scored 0-100 | Unknown | 22 controls (SOC 2/ISO 27001) | Articles 5-15 classification | Doc file existence only |
| **Audit trail** | Hash-chained, file-locked | Unknown | Deterministic replay | None | Unknown |
| **Bias testing** | CrowS-Pairs (`regula bias`) | None | None | **CrowS-Pairs** | None |
| **Fix generation** | None | None | **Yes** | None | None |
| **License** | MIT | Apache 2.0 | Unknown | Unknown | Unknown |

**Where Regula leads:** pre-commit hook integration, Python AST depth, compliance gap assessment (Articles 9-15), dependency pinning analysis, offline zero-dependency operation.

**Where Regula falls short:** JS/TS analysis (Systima is deeper), fix code generation (AIR Blackbox has it, Regula doesn't).

If your primary stack is TypeScript and you need CI/CD integration, Systima Comply is worth evaluating alongside Regula. If you need runtime interception and automated fix suggestions, AIR Blackbox serves a different need.

---

## Regulatory Context

The EU AI Act (Regulation 2024/1689) is now in force:

| Date | Requirement |
|------|-------------|
| **2 February 2025** | Prohibited AI practices (Article 5) apply |
| **2 August 2025** | General-purpose AI model rules apply |
| **2 August 2026** | High-risk system requirements (Articles 9-15) fully apply |

Penalties: up to EUR 35 million or 7% of global annual turnover.

**Digital Omnibus:** The European Commission proposed in December 2025 to delay the Annex III high-risk obligations to December 2027 for certain providers. This is not yet law — it remains in trilogue as of April 2026. The August 2026 deadline remains in effect until and unless the Omnibus is formally adopted. Do not plan around the extension without monitoring its legislative progress.

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
| **Claude Code** | Supported | `python3 scripts/cli.py install claude-code` |
| **GitHub Copilot CLI** | Supported | `python3 scripts/cli.py install copilot-cli` |
| **Windsurf Cascade** | Supported | `python3 scripts/cli.py install windsurf` |
| **pre-commit** | Supported | `python3 scripts/cli.py install pre-commit` |
| **Git hooks** | Supported | `python3 scripts/cli.py install git-hooks` |
| **CI/CD (GitHub Actions, GitLab)** | Via SARIF | `regula check --format sarif` |

Claude Code, Copilot CLI, and Windsurf use the same hook protocol. Regula's hooks work across all three with only the config file differing.

## CI/CD Integration

Add EU AI Act scanning to your GitHub Actions workflow:

```yaml
name: AI Governance Check
on: [push, pull_request]

jobs:
  regula:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: kuzivaai/getregula@v1
        with:
          path: '.'
          upload-sarif: 'true'
          fail-on-prohibited: 'true'
```

Findings appear in your repository's Security tab alongside CodeQL and Dependabot.

## CLI Usage

```bash
# Find out if the EU AI Act applies to your product (a few yes/no questions, no code required)
python3 scripts/cli.py assess

# Scan a project for risk indicators
python3 scripts/cli.py check .
python3 scripts/cli.py check . --format json
python3 scripts/cli.py check . --format sarif    # For CI/CD integration
python3 scripts/cli.py check . --ci              # Exit 1 on any WARN or BLOCK finding
python3 scripts/cli.py check . --strict          # Exit 1 on WARN-tier findings
python3 scripts/cli.py check . --skip-tests      # Exclude test files from results
python3 scripts/cli.py check . --min-tier limited_risk  # Filter out minimal_risk noise

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

# Conformity assessment evidence pack (Article 43)
python3 scripts/cli.py conform --project .
python3 scripts/cli.py conform --project . --format json

# Cross-file Article 14 human oversight analysis
python3 scripts/cli.py oversight --project .

# AI Bill of Materials (CycloneDX 1.6 with GPAI tier annotations)
python3 scripts/cli.py sbom --project .
python3 scripts/cli.py sbom --project . --ai-bom    # Include model provenance + datasets

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

### Conformity Assessment Evidence Pack

Generates a structured evidence folder for Article 43 internal conformity assessment (Annex VI, Module A). Each sub-folder maps to a specific EU AI Act article with auto-generated evidence and a coverage file that clearly states what was auto-detected vs what requires human input.

```bash
regula conform --project .                    # Generate evidence pack
regula conform --project . --format json      # Machine-readable summary
```

Output: 26 files across 12 folders, including Annex IV draft, audit trail, SBOM, remediation plan, Article 14 oversight analysis, and an Article 47 declaration of conformity template. All files SHA-256 hashed in a manifest for tamper detection.

**Important:** This is a compliance evidence scaffold, not a legal determination. The `00-assessment-summary.json` file lists what Regula auto-generated and what requires human input (intended purpose, FRIA, training data provenance, etc.).

### Cross-File Human Oversight Analysis (Article 14)

Traces AI model outputs across Python files to check whether each path from an AI call to a user-facing endpoint passes through a human review gate.

```bash
regula oversight --project .                  # Text output
regula oversight --project . --format json    # Machine-readable
```

Reports per-path confidence (high/medium/low) and always discloses five limitations: dynamic imports not analysed, decorator-wrapped routes not resolved, third-party library internals not traced, cross-service calls not detected, and that detecting a code path does not verify oversight is meaningfully exercised (per ICO ADM guidance).

### AI Bill of Materials

Extends the CycloneDX 1.6 SBOM with AI-specific metadata: model provenance extracted from code (which models are loaded, from which providers), GPAI tier annotations per EU AI Act Articles 51-55, and detected training dataset references.

```bash
regula sbom --project .                       # Standard SBOM
regula sbom --project . --ai-bom              # With AI-specific metadata
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

Regula maps findings to 12 compliance frameworks internally: EU AI Act, NIST AI RMF 1.0, ISO 42001:2023, NIST CSF 2.0, SOC 2, ISO 27001:2022, OWASP Top 10 for LLMs, MITRE ATLAS, LGPD (Brazil), Marco Legal da IA (Brazil), EU Cyber Resilience Act, and UK ICO AI Guidance. Framework mappings appear in check findings and gap assessments automatically.

### Real-World Validation Benchmark

Measure Regula's precision and recall against real codebases. Outputs CSV for manual labelling, then calculates metrics from labelled data.

```bash
regula benchmark --project /path/to/project                    # Scan
regula benchmark --project /path/to/project -f csv -o out.csv  # CSV for labelling
regula benchmark --metrics labelled.csv                        # Precision/recall
```

### Scan Time Benchmark

Reproducible scan-time numbers against public repositories. Shallow-clones each repo, runs `regula check`, and prints a markdown table with wall-clock time, file count, and finding count. Designed to be re-run on your own hardware.

```bash
python3 scripts/scan_benchmarks.py                  # default repo list
python3 scripts/scan_benchmarks.py --self           # this repo only
python3 scripts/scan_benchmarks.py --json           # machine-readable
```

Sample run on `Linux-6.6.87.2-microsoft-standard-WSL2-x86_64` (Python 3.12.3, Regula 1.5.1):

| Target | Commit | Files scanned | Findings | Wall time | Files/sec |
|---|---|---:|---:|---:|---:|
| [psf/requests](https://github.com/psf/requests) | `ef439eb779c1` | 36 | 2 | 0.35s | 103.2 |
| [openai/openai-python](https://github.com/openai/openai-python) | `58184ad545ee` | 1,218 | 404 | 5.76s | 211.5 |
| [encode/httpx](https://github.com/encode/httpx) | `b5addb64f016` | 60 | 8 | 0.57s | 105.1 |

Numbers are from a single run on one machine. Re-run the script on your own hardware before citing them. No precision/recall claims are made — see the validation benchmark above for accuracy measurement.

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
| `comment-on-pr` | `true` | Post a single rolled-up summary comment on PRs |
| `inline-pr-comments` | `false` | Post per-finding inline review comments anchored to changed lines |
| `inline-comment-max` | `20` | Cap on inline review comments per PR (anti-spam) |
| `inline-comment-min-tier` | `high_risk` | Minimum tier eligible for inline comments |

**Outputs:** `findings-count`, `prohibited-count`, `high-risk-count`, `pinning-score`, `sarif-file`

**Inline review comments.** When `inline-pr-comments: true`, the action fetches the PR's diff via the GitHub API, builds a set of changed line numbers per file, and posts a single review (`event: COMMENT`) containing one inline comment per finding whose `file:line` falls inside the diff. Findings outside the diff are silently dropped — no spam on unchanged code. The default minimum tier is `high_risk`; set `inline-comment-min-tier: minimal_risk` to comment on everything. The default cap of 20 prevents large PRs from generating hundreds of comments.

**Status: defined, not yet validated end-to-end in a production PR workflow.** The action definition is correct and the SARIF + summary-comment paths are exercised by `.github/workflows/regula-scan.yaml`, but the inline-review-comment path was added in this revision and has not yet been observed against a real GitHub PR. The first run on a real PR is the verification. Treat the inline-comment feature as experimental until that confirmation.

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

### MCP Server (use Regula from Claude Code, Cursor, Windsurf)

Regula ships an MCP (Model Context Protocol) server that exposes
`regula_check`, `regula_classify`, and `regula_gap` as tools an AI coding
assistant can call directly. The server uses stdio transport and JSON-RPC
2.0; no network exposure, no authentication needed (the parent process
controls access).

```bash
regula mcp-server                          # Start MCP server (stdio)
```

**Claude Code** — recommended method is the CLI:

```bash
claude mcp add regula -- python3 /absolute/path/to/getregula/scripts/mcp_server.py

# Or, if you installed Regula via `pip install regula-ai`:
claude mcp add regula -- regula mcp-server
```

This writes to `~/.claude.json` (user scope) or `.mcp.json` in your project
root (project scope, checked into source control). If you prefer to edit
the JSON directly, the schema is:

```json
{
  "mcpServers": {
    "regula": {
      "type": "stdio",
      "command": "regula",
      "args": ["mcp-server"]
    }
  }
}
```

See the [Claude Code MCP docs](https://code.claude.com/docs/en/mcp) for
the full scope hierarchy.

**Cursor** (`~/.cursor/mcp.json`) and **Windsurf**
(`~/.codeium/windsurf/mcp_config.json`) use the same `mcpServers` schema:

```json
{
  "mcpServers": {
    "regula": {
      "command": "regula",
      "args": ["mcp-server"]
    }
  }
}
```

Replace `regula` / `["mcp-server"]` with `python3` and the absolute path
to `scripts/mcp_server.py` if you have not installed via pip.

After restarting your client, the assistant gains three tools:

- `regula_check` — scan a project directory; returns findings with tier,
  confidence, and remediation guidance.
- `regula_classify` — classify a code snippet against EU AI Act risk tiers.
- `regula_gap` — assess Articles 9–15 compliance gaps with per-article scores.

**Security note.** The MCP server is stdio-only and inherits the
permissions of the parent process. Do not expose it over TCP/HTTP without
adding authentication first.

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
│   ├── framework_mapper.py        # Cross-framework compliance mapping (11 frameworks)
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
│   ├── test_classification.py     # Core classification tests
│   ├── test_agent_governance.py   # Agent autonomy detection
│   ├── test_coverage_critical.py  # Critical path coverage
│   ├── test_documentation.py      # Documentation generation
│   ├── test_hooks_audit.py        # Hook and audit trail
│   ├── test_registry.py           # AI system registry
│   ├── test_reliability.py        # Edge cases and resilience
│   └── test_security_hardening.py # Security hardening checks
│   # 525 tests
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
- **Multi-framework mapping.** 12 frameworks (EU AI Act, NIST AI RMF, ISO 42001, NIST CSF 2.0, SOC 2, ISO 27001, OWASP LLM Top 10, MITRE ATLAS, LGPD, Marco Legal da IA, EU CRA, UK ICO) mapped via a single crosswalk data file.

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

# Domain-aware severity adjustment
system:
  name: "Lending Risk Engine"
  domain: creditworthiness    # See list below
  risk_level: high_risk       # Or "" for auto-detect
```

### Domain-aware severity

Regula adjusts confidence scores based on the declared system domain. The same finding (e.g. an OpenAI call combined with credit-scoring keywords) becomes a higher-confidence finding in a fintech project than in a demo. This is implemented in `scripts/domain_scoring.py` and applied in `scripts/report.py` during scanning.

Set `system.domain` in `regula-policy.yaml` to one of:

- **Regulated** (Annex III categories — boost applied): `creditworthiness`, `employment`, `insurance`, `education`, `legal`, `law_enforcement`, `migration`, `biometric`, `medical`
- **Informational** (no boost): `customer_support`, `internal_tooling`, `content_generation`, `general_purpose`

Findings that received a domain boost include a `domain_boost` field in JSON output:

```json
{
  "file": "credit.py",
  "tier": "high_risk",
  "confidence_score": 95,
  "domain_boost": {
    "boost": 15,
    "domains_matched": ["finance"],
    "detail": "Domain keywords detected: finance + automated decision logic"
  }
}
```

If `system.domain` is unset, Regula falls back to keyword-based detection (employment, finance, medical, education, law_enforcement, biometrics, infrastructure, migration). The boost is only applied when AI indicators are also present — a file with employment keywords but no AI code gets zero boost.

Policy exemptions **cannot override** Article 5 prohibited practice detection. Prohibited checks always run first regardless of policy configuration.

For full YAML support, install pyyaml: `pip install pyyaml`. Without it, a minimal YAML subset parser is used. Alternatively, use `regula-policy.json`.

## Testing

```bash
pytest tests/ -q
```

525 tests covering:
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

- **v1.2:** ~~Production readiness~~ — shipped 2026-03-28. Agent autonomy detection, `--skip-tests`, `--min-tier`, bias testing, 10-framework mapping, 525 tests.
- **v1.3 (candidates):** JS/TS tree-sitter data flow, AVID vulnerability database integration, typosquatting detection, GitHub Action validated in real PR workflow.
- **Not planned yet:** DPO dashboard, Slack/Teams alerting, model card generation, bias testing. These require validation that there are users who want them first.

## Contributing

Bug reports and pull requests are welcome. A few things to know:

- Tests are in `tests/`. Run `pytest tests/ -q` before opening a PR.
- Pattern additions go in `scripts/classify_risk.py`. Each pattern should have a test.
- The tool is intentionally risk *indication*, not legal classification. New patterns should be conservative — false positives erode trust more than false negatives for a developer tool.
- See [CHANGELOG.md](CHANGELOG.md) for what has changed between versions.

## License

MIT License. See [LICENSE.txt](LICENSE.txt).

## Author

Built by [The Implementation Layer](https://theimplementationlayer.substack.com) — AI governance from the practitioner side.
