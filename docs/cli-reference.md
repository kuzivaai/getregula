# CLI Reference

Full command-line reference for `regula`. The README's overview links here.

Verify command syntax against your installed version with `regula --help` and `regula <subcommand> --help` — this file is generated from the same source as the README CLI Usage section and may lag behind the CLI by a release.

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

### Annex VIII Registration Packet (Article 49)

Generates an Annex VIII Section A/B/C registration packet for an AI project, branching by provider/deployer role and Annex III area, auto-filling fields from existing Regula scan artifacts, and listing the gaps that require manual entry.

```bash
regula register .                              # auto-detect role + section
regula register . --section B                  # force Section B (Art 6(3) self-exemption)
regula register . --deployer-type public_authority  # force public-authority deployer (Section C)
regula register . --format json                # emit json_output envelope
regula register . --force                      # overwrite existing packet
```

Output: `.regula/registry/<system-id>.json` (canonical packet) plus `.regula/registry/<system-id>.gaps.yaml` (companion file with empty `value:` slots for fields needing human input). Both files include the dual deadline annotation (`2026-08-02` current law / `2027-12-02` Omnibus pending) and the schema provenance block listing the three sources used to verify the field schemas.

**Branching logic** (verified against Regulation (EU) 2024/1689):

| Detected role | Annex III point | Section | Submission target | Article |
|---|---|---|---|---|
| Provider | 1 (biometrics) | A subset (excl. 6, 8, 9) | `eu_database_non_public` | 49(4) |
| Provider | 2 (critical infrastructure) | A full | `national_authority` | 49(5) |
| Provider | 3, 4, 5, 8 | A full | `eu_database_public` | 49(1) |
| Provider | 6 (law enforcement) | A subset (excl. 6, 8, 9) | `eu_database_non_public` | 49(4) |
| Provider | 7 (migration/asylum/border) | A subset (excl. 6, 8, 9) | `eu_database_non_public` | 49(4) |
| Provider self-exempted via Art 6(3) | n/a | B (mandatory; field set may simplify under Omnibus) | `eu_database_public` | 49(2) |
| Public-authority deployer | any | C | varies by point | 49(3) |
| Private-sector deployer | any | n/a — out of Art 49 scope | n/a | see `regula gap` (Article 26) |
| `not_ai` / `minimal_risk` | n/a | n/a | n/a — `no_registration_required` packet | n/a |

**Important:** This is a local packet generator. The EU AI Act database (Art. 71) is not user-writable as of 2026-04-07; the packet is the credible CLI-side artifact. The schema source of truth lives at `references/annex_viii_sections.json` with `verification_method: three_independent_sources_agree_exact` and a documented EUR-Lex unreachability note.

### Cross-File Human Oversight Analysis (Article 14)

Traces AI model outputs across Python files to check whether each path from an AI call to a user-facing endpoint passes through a human review gate.

```bash
regula oversight --project .                  # Text output
regula oversight --project . --format json    # Machine-readable
```

Reports per-path confidence (high/medium/low) and always discloses five limitations: dynamic imports not analysed, decorator-wrapped routes not resolved, third-party library internals not traced, cross-service calls not detected, and that detecting a code path does not verify oversight is meaningfully exercised (per ICO ADM guidance).

### SME-Simplified Annex IV (Article 11(1) interim form)

Article 11(1) second subparagraph of the EU AI Act allows providers that are SMEs (including start-ups) to provide the elements of Annex IV in a **simplified manner**. The Commission is required to establish an official simplified technical documentation form for SMEs but had not published it as of 2026-04-08. Regula's `--sme` flag generates an interim format that covers the minimum a notified body or enterprise customer typically asks for, sourced from the same scan data as the full pack:

```bash
regula conform --sme                              # generate interim SME Annex IV
regula conform --sme --output ./compliance        # custom output directory
regula conform --sme --format json                # machine-readable manifest
regula conform                                    # full multi-folder evidence pack (Article 43)
```

The output is a **single Markdown file** rather than the full multi-folder pack, with a SHA-256 integrity hash and a manifest. Sections covered: intended purpose, AI components and dependencies, risk management summary, data governance summary, human oversight, accuracy/robustness/security, standards applied (with the JTC 21 pending status), Article 6(3) exemption pointer, and a provider declaration block. Replace with the official Commission template when published.

### Article 6(3) Exemption Self-Assessment

Structured decision tree for Article 6(3) of the EU AI Act, which lets a provider self-assess an Annex III system as **not** high-risk on one of four grounds:

- **(a)** narrow procedural task
- **(b)** intended to improve the result of a previously completed human activity
- **(c)** intended to detect decision-making patterns or deviations, with proper human review
- **(d)** intended to perform a preparatory task to a human-led assessment

A hard carve-out (Article 6(3) second subparagraph) makes any system that **performs profiling of natural persons** high-risk regardless of the four conditions.

```bash
regula exempt                                    # interactive (6 questions)
regula exempt --answers y,n,y,n,n,n              # non-interactive
regula exempt --format json                      # machine-readable record
```

The command produces a documented self-assessment with the conditions met, the rationale, and a regulatory-status disclosure that the **European Commission missed its 2 February 2026 deadline** for publishing Article 6 guidelines (Article 6(5)). The same disclosure is now embedded in `regula gap` output (key `article_6_guidelines_status` in JSON, footer block in text). If the self-assessment returns `exempt`, the command points the user at `regula register --art-6-3-exempted` for the Article 49(2) registration step required by Article 6(4).

### GPAI Code of Practice Check (Article 53 + Article 55)

Maps a GPAI provider codebase to the three chapters of the EU AI Act GPAI Code of Practice (final 10 July 2025, endorsed 1 August 2025, obligations in force since 2 August 2025, enforcement actions from 2 August 2026):

- **Chapter 1 — Transparency** (all GPAI providers, Art 53(1)(a)(b)(d)): model documentation, downstream-provider information, training-content summary
- **Chapter 2 — Copyright** (all GPAI providers, Art 53(1)(c)): written copyright policy, text-and-data mining opt-out compliance (robots.txt / TDMRep)
- **Chapter 3 — Safety & Security** (systemic-risk only, ≥10²⁵ training FLOPs, Art 55): model evaluation, serious-incident reporting, cybersecurity protection

```bash
regula gpai-check                                 # All GPAI providers (Chapters 1-2)
regula gpai-check --systemic-risk                 # + Chapter 3 (Art 55, large frontier models)
regula gpai-check --strict                        # Exit 1 on any FAIL
regula gpai-check --format json                   # Machine-readable
```

Each obligation is reported as PASS / WARN / FAIL / N/A with the relevant article anchor and concrete file evidence. Adherence to the Code provides a rebuttable presumption of conformity with Articles 53 and 55 — this command produces evidence, not a legal determination. Pattern surface and reference metadata live in `references/gpai_code_of_practice.yaml`.

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

**Self-benchmark precision (labels 2026-04-01, re-validated 2026-04-07).**

> **Re-validation result.** The labelled corpus was generated on
> 2026-04-01. Pattern files have been modified six times since. A full
> rescan on 2026-04-07 found that **252 of 257 labels (98%)** still
> match current scan output, and precision on that matched subset is
> **15.1%** — within 0.1pp of the published number. The 15.2% below
> stands as a current measurement *on the labelled findings*. Note: the
> rescan also produced 3,927 new findings that have no labels yet — the
> published number covers ~6% of what the scanner currently emits, and
> a comprehensive precision figure requires labelling that delta. That
> is the next piece of work. Reproduce both numbers with
> `python3 benchmarks/label.py score` and `python3 benchmarks/run_benchmark.py`.

Hand-labelled 257 findings sampled across five OSS AI projects (`instructor`, `pydantic-ai`, `langchain`, `scikit-learn`, `openai-python`):

| Cut | TP | FP | Precision |
|---|---:|---:|---:|
| **Overall** | 39 | 218 | **15.2%** |
| `agent_autonomy` | 2 | 3 | 40.0% |
| `limited_risk` | 1 | 2 | 33.3% |
| `minimal_risk` (94% of findings) | 36 | 205 | 14.9% |
| `ai_security` | 0 | 6 | 0.0% |
| `credential_exposure` | 0 | 2 | 0.0% |

This is the honest current state. The minimal_risk tier dominates the sample on general-purpose libraries and is noisy — that's the next pattern-tuning target. None of the five repos triggered `prohibited` or `high_risk` findings, so precision for the tiers that actually block merges cannot be estimated from this benchmark and is a separate piece of work.

Recall is not estimable from labelled findings alone and is reported as `null`. **No "99%" claim is being made and none should be.** Full methodology, per-project breakdown, and limitations: [`benchmarks/README.md`](benchmarks/README.md). Reproduce with `python3 benchmarks/label.py score`.

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

