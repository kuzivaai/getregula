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

Regula's design choices, stated on their own terms:

- **CLI-first.** A single executable that runs in CI, in pre-commit hooks, and from a developer's terminal. No browser, no SaaS account, no model service.
- **Stdlib-only core.** The base scanner has zero required production dependencies. PyYAML, tree-sitter, WeasyPrint, and Sentry are all optional and gated behind explicit feature flags.
- **Static analysis only.** Regula reads source files. It does not run code, call models, or send data anywhere. Air-gapped environments are a first-class use case.
- **EU AI Act-shaped.** Risk tiers, finding categories, and the conformity evidence pack are aligned to the regulation's structure (Article 5 prohibited practices, Annex III high-risk categories, Articles 9–15 obligations) rather than to a generic SAST taxonomy.
- **Honest about its own precision.** The benchmark in `benchmarks/` measures Regula against five labelled OSS projects and publishes the actual number — see *Real-World Validation Benchmark* below.

### How Regula maps to the AICDI corporate AI governance gaps

The 2026 [UNESCO + Thomson Reuters Foundation AI Company Data Initiative report](https://www.unesco.org/en/articles/pioneering-report-thomson-reuters-foundation-and-unesco-sheds-light-way-3000-companies-approach-ai) measured 2,972 global companies and found large gaps between AI adoption and AI governance. Regula addresses some of those gaps directly, others partially, and many not at all.

For an honest, gap-by-gap mapping with citations and explicit out-of-scope items, see [`docs/landscape.md`](docs/landscape.md). Headline:

- **Yes, addressed by Regula:** technical AI model registry (closes the 2.7% gap), Article 14 human-oversight verification (partial — closes part of the 12% gap), Article 9–15 conformity evidence pack, GPAI Code of Practice signatory annotation on detected vendors.
- **No, not addressed by Regula:** AI strategy adoption (44%), board oversight (40%), worker protection policies (14%), AI training programmes (31%), environmental impact assessments (11%), ethical impact assessments (5%), complaints mechanisms (2.3%). These are organisational and human-process gaps that no static code scanner can fix.

---

## Regulatory Context

The EU AI Act (Regulation 2024/1689) is now in force:

| Date | Requirement |
|------|-------------|
| **2 February 2025** | Prohibited AI practices (Article 5) apply |
| **2 August 2025** | General-purpose AI model rules apply |
| **2 August 2026** | High-risk system requirements (Articles 9-15) fully apply |

Penalties: up to EUR 35 million or 7% of global annual turnover.

**Digital Omnibus:** The European Commission proposed in December 2025 to delay the Annex III high-risk obligations to 2 December 2027 (Annex I systems to 2 August 2028). The European Parliament adopted its joint position in plenary on 26 March 2026 (569–45), the Council agreed its negotiating mandate on 13 March 2026, the first trilogue completed in late March 2026, and the second (expected to be final) trilogue is scheduled for 28 April 2026. The Cypriot Presidency is targeting agreement in May 2026. Until the Omnibus is formally adopted and published in the OJEU, the **2 August 2026 Annex III deadline remains legally binding**. Do not plan around the extension without monitoring its legislative progress — `regula timeline` shows both the current statutory date and the proposed replacement.

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

## Precision

Regula publishes its own measured precision rather than vendor-marketing claims. Two benchmarks:

**Self-benchmark on labelled OSS findings (labels 2026-04-01, re-validated 2026-04-07).** Hand-labelled 257 findings sampled across `instructor`, `pydantic-ai`, `langchain`, `scikit-learn`, and `openai-python`:

| Cut | TP | FP | Precision |
|---|---:|---:|---:|
| **Overall** | 39 | 218 | **15.2%** |
| `agent_autonomy` | 2 | 3 | 40.0% |
| `limited_risk` | 1 | 2 | 33.3% |
| `minimal_risk` (94% of findings) | 36 | 205 | 14.9% |
| `ai_security` | 0 | 6 | 0.0% |
| `credential_exposure` | 0 | 2 | 0.0% |

The minimal_risk tier dominates the sample on general-purpose libraries and is noisy — that's the next pattern-tuning target. None of the five repos triggered `prohibited` or `high_risk` findings, so those tiers cannot be measured against this corpus and need a separate fixture (see below).

**Synthetic fixture for the legally significant tiers.** A hand-crafted corpus in [`benchmarks/synthetic/`](benchmarks/synthetic/) with 5 prohibited examples (Article 5 categories a–e), 5 high-risk examples (Annex III categories), and 3 negative examples. Recall is computable here because every fixture is labelled at the file level. Current measurement:

| Tier | Precision | Recall | F1 |
|---|---:|---:|---:|
| `prohibited` (Article 5) | 100% | 100% | 100% |
| `high_risk` (Annex III) | 100% | 100% | 100% |

Reproduce with `python3 benchmarks/label.py score` (OSS labels) and `python3 benchmarks/synthetic/run.py` (synthetic). Methodology, limitations, and the 3,946 unlabelled findings still requiring human review: [`benchmarks/README.md`](benchmarks/README.md).

**No "99%" claim is being made and none should be.** The 15.2% number is honest on the labelled subset of one snapshot. The 100% on the synthetic fixture is honest on a small (13-file) hand-crafted corpus designed to exercise the prohibited/high-risk paths the OSS benchmark cannot cover.

## CLI Usage

Regula has 39 CLI subcommands. The full reference (with examples for each) lives in [`docs/cli-reference.md`](docs/cli-reference.md). Top-level summary:

```bash
regula --help                              # list all subcommands
regula assess                              # interactive applicability check
regula check .                             # scan for risk indicators
regula classify --input "some code..."    # classify a snippet
regula gap                                 # Articles 9-15 compliance gap assessment
regula exempt                              # Article 6(3) self-assessment decision tree
regula gpai-check                          # GPAI Code of Practice chapter mapping (Art 53 + Art 55)
regula conform                             # generate Annex IV evidence pack
regula register                            # generate Annex VIII Section A/B/C packet (Article 49)
regula sbom --ai-bom                       # AI Bill of Materials (CycloneDX)
regula report --format html                # HTML report
regula doctor                              # health checks
regula self-test                           # built-in correctness assertions
regula timeline                            # EU AI Act enforcement dates
regula benchmark --project /path           # precision benchmark
regula mcp-server                          # start the stdio MCP server
```

See also:
- [`docs/cli-reference.md`](docs/cli-reference.md) — full command reference
- [`docs/architecture.md`](docs/architecture.md) — internal layout, modules, design principles, language support
- [`docs/article-south-africa-ai-policy.md`](docs/article-south-africa-ai-policy.md) — South Africa's National AI Policy Framework, what is verified, what isn't, and what it means for code

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

- **v1.2:** ~~Production readiness~~ — shipped 2026-03-28. Agent autonomy detection, `--skip-tests`, `--min-tier`, bias testing (`regula bias`, CrowS-Pairs), 8-framework mapping, 525 tests.
- **v1.3:** GPAI Code of Practice chapter-level obligation mapping (`regula gpai-check`, three chapters: Transparency / Copyright / Safety & Security) — **shipped**. Colorado AI Act + South Korea AI Basic Act Tier-3 pages — **shipped**. Harmonised-standards plumbing ready for Q4 2026 CEN-CENELEC publication — **shipped (stub)**. Prompt-injection detector (OWASP LLM01:2025 — direct, indirect, and tool-output vectors) — **shipped**. Article 6(3) self-assessment decision tree (`regula exempt`, with the missed-Commission-deadline disclosure surfaced in `regula gap`) — **shipped**. SME-simplified Annex IV under Article 11(1) (`regula conform --sme`) — **shipped (interim format pending Commission template)**. Still in candidate list: JS/TS tree-sitter data flow, AVID vulnerability database integration, typosquatting detection.
- **Not planned yet:** DPO dashboard, Slack/Teams alerting, model card generation. These require validation that there are users who want them first.

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
