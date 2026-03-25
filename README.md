# Regula

**AI Governance Risk Indication for Claude Code**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE.txt)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![EU AI Act](https://img.shields.io/badge/EU%20AI%20Act-Risk%20Indication-blue.svg)](#regulatory-coverage)
[![CI](https://github.com/kuzivaai/getregula/actions/workflows/ci.yaml/badge.svg)](https://github.com/kuzivaai/getregula/actions)

Regula is a Claude Code skill that detects AI governance risk indicators in real-time. It flags patterns associated with EU AI Act risk tiers, blocks patterns matching prohibited practices, and maintains a hash-chained audit trail.

## Quick Start

```bash
git clone https://github.com/kuzivaai/getregula.git
cd getregula

# Install for your platform (pick one):
python3 scripts/install.py claude-code     # Claude Code
python3 scripts/install.py copilot-cli     # GitHub Copilot CLI
python3 scripts/install.py windsurf        # Windsurf Cascade
python3 scripts/install.py pre-commit      # pre-commit framework
python3 scripts/install.py git-hooks       # Direct git hooks

# Scan a project
python3 scripts/cli.py check /path/to/project

# Generate an HTML report for your DPO
python3 scripts/cli.py report --format html --output report.html --include-audit
```

Run tests: `python3 tests/test_classification.py`

## What It Does

When you write AI-related code, Regula:

1. **Detects** AI indicators (libraries, model files, API calls, ML patterns)
2. **Flags** patterns associated with EU AI Act risk tiers
3. **Blocks** patterns matching Article 5 prohibited practices (with conditions and exceptions)
4. **Warns** about patterns in Annex III high-risk areas (with Article 6 context)
5. **Logs** everything to a hash-chained audit trail

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

All three major AI coding agents (Claude Code, Copilot CLI, Windsurf) use the same hook protocol. Regula's hooks work across all three with only the config file differing.

## CLI Usage

```bash
# Scan a project for risk indicators
python3 scripts/cli.py check .
python3 scripts/cli.py check . --format json
python3 scripts/cli.py check . --format sarif    # For CI/CD integration

# Classify a text input
python3 scripts/cli.py classify --input "import tensorflow; cv screening model"

# Generate reports
python3 scripts/cli.py report --format html -o report.html --include-audit
python3 scripts/cli.py report --format sarif -o results.sarif.json

# Discover AI systems and register them
python3 scripts/cli.py discover --project . --register
python3 scripts/cli.py status

# Audit trail management
python3 scripts/cli.py audit verify
python3 scripts/cli.py audit export --format csv -o audit.csv

# Install hooks for a platform
python3 scripts/cli.py install claude-code
python3 scripts/cli.py install copilot-cli
python3 scripts/cli.py install list
```

### Inline Suppression

Add `# regula-ignore` to any file to suppress all findings for that file, or `# regula-ignore: RULE_ID` to suppress a specific rule. Suppressions are tracked and visible in reports.

```python
# regula-ignore: employment
import sklearn
# This CV screening tool is a research prototype, not deployed
```

### Governance News Feed

Curated AI governance news from 7 reputable sources (IAPP, NIST, Stanford HAI, ICO, EU AI Act, Brookings, Help Net Security). Keyword-filtered, deduplicated, cached.

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
│   ├── generate_documentation.py  # Annex IV scaffold generator
│   └── discover_ai_systems.py     # AI system discovery and registry
├── hooks/
│   ├── pre_tool_use.py            # PreToolUse hook (CC/Copilot/Windsurf)
│   ├── post_tool_use.py           # PostToolUse logging hook
│   └── stop_hook.py               # Session summary hook
├── references/                    # Regulatory reference documents
├── tests/
│   └── test_classification.py     # 59 tests, 177 assertions
├── docs/
│   └── research-synthesis.md      # Research findings informing roadmap
├── regula-policy.yaml             # Policy configuration template
└── .github/workflows/ci.yaml     # CI/CD
```

### Design Principles

- **Core engine + thin adapters.** One classification engine, multiple platform integrations.
- **Same hook protocol.** Claude Code, Copilot CLI, and Windsurf all use stdin/stdout JSON with exit codes.
- **Confidence scores, not binary labels.** 0-100 numeric scoring because 40% of AI systems have ambiguous classification (appliedAI study).
- **Inline suppression with audit trail.** `# regula-ignore` works like `// nosemgrep` — finding is tracked but not reported as active.
- **SARIF for CI/CD.** Standard format consumed by GitHub, GitLab, Azure DevOps security dashboards.

## Configuration

Copy `regula-policy.yaml` to your project root and customise:

```yaml
version: "1.0"
organisation: "Your Organisation"

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

59 test functions, 177+ assertions covering:
- AI detection (libraries, model files, API endpoints, ML patterns)
- All 8 prohibited practices
- All 10+ high-risk categories
- Limited-risk and minimal-risk scenarios
- Edge cases (empty input, case insensitivity, priority ordering)
- Policy engine (force_high_risk, exempt, prohibited override safety)
- Audit trail (hash chain integrity, CSV export)
- Confidence scoring (numeric scores, tier ordering, multi-indicator bonus)
- Reports (SARIF structure, HTML disclaimer, inline suppression)
- Questionnaire (generation, high-risk evaluation, minimal-risk evaluation)
- Session aggregation, baseline comparison, timeline data accuracy

## Constraints

- **No required external dependencies** — stdlib only (pyyaml optional)
- **Python 3.10+**
- **Works offline** — no API calls required
- **Append-only audit** — no deletion capability
- **File-locked writes** — safe under concurrent hook execution

## Roadmap

- **v1.1:** ISO 42001 control mapping, NIST AI RMF integration
- **v1.2:** DPO dashboard, Slack/Teams alerting, external timestamp authority
- **v2.0:** Model card generation, bias testing integration

## License

MIT License. See [LICENSE.txt](LICENSE.txt).

## Author

Built by [The Implementation Layer](https://theimplementationlayer.substack.com) — AI governance from the practitioner side.
