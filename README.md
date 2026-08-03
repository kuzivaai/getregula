<!-- mcp-name: io.github.kuzivaai/regula -->
# Regula

**AI governance risk indication for code — EU AI Act, South Korea AI Basic Act, Colorado SB 26-189. Combines code scanning with governance questionnaires.**

[![PyPI](https://img.shields.io/pypi/v/regula-ai)](https://pypi.org/project/regula-ai/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE.txt)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![CI](https://github.com/kuzivaai/getregula/actions/workflows/ci.yaml/badge.svg)](https://github.com/kuzivaai/getregula/actions)
[![Tests](https://img.shields.io/badge/tests-2679%20collected-blue.svg)](#verified-numbers)
[![WCAG 2.2 AA](https://img.shields.io/badge/WCAG%202.2-AA-success.svg)](docs/accessibility/README.md)

---

## Table of contents

- [What it does](#what-it-does)
- [Quick start](#quick-start)
- [What Regula tells you](#what-regula-tells-you)
- [Key commands](#key-commands)
- [Who is this for?](#who-is-this-for)
- [What Regula is (and isn't)](#what-regula-is-and-isnt)
- [Bias evaluation — methodology and ethics](#bias-evaluation--methodology-and-ethics)
- [Important limitations](#important-limitations)
- [Verified numbers](#verified-numbers)
- [Contributing](#contributing)
- [Licence](#licence)

---

![Regula check demo](site/assets/demo/regula-check.svg)

---

## What it does

Regula combines local code scanning with governance questionnaires. It reports code-observable AI-governance indicators, candidate risk categories, and potentially relevant provisions for contextual human review. It does not determine legal classification, compliance, or the obligations applicable to a real deployment. Multi-jurisdiction reference material covers the EU AI Act, South Korea's AI Basic Act (Act No. 20676), and Colorado SB 26-189. The core install has no required third-party runtime dependencies; optional extras add dependencies and some optional commands or configured features can contact external services. Assess the territorial scope and data-processing duties for your deployment independently.

## Quick start

```bash
pipx install regula-ai      # or: pip install regula-ai / uv pip install regula-ai
```

**Not sure if the AI Act applies?** No code needed:
```bash
regula assess               # record declared context for human review
```

**Want to scan your code?**
```bash
regula check .              # 419 tier patterns, 8 language families; runtime varies
regula check . --jurisdictions eu,korea,colorado  # all 3 jurisdictions
```

**Need documentation for auditors?**
```bash
regula evidence-pack --project .   # Annex IV docs + evidence pack
regula conform --sign --timestamp  # signed + timestamped (requires regula[signing])
```

**Just want to see it work?** (requires the cloned repo — `examples/` is not bundled in the pip package)
```bash
git clone https://github.com/kuzivaai/getregula && cd getregula
regula demo                 # scan a bundled example project
```

### Install details

The recommended install is **pipx** — it isolates Regula from your system Python and avoids the `externally-managed-environment` error on Ubuntu 22.04+, Debian 12+, Fedora, Arch, and Homebrew Python.

If you don't have pipx yet, install it first (one-time):

| Platform | Install pipx |
|---|---|
| macOS | `brew install pipx && pipx ensurepath` |
| Debian / Ubuntu | `sudo apt install pipx && pipx ensurepath` |
| Fedora | `sudo dnf install pipx && pipx ensurepath` |
| Arch | `sudo pacman -S python-pipx && pipx ensurepath` |
| Windows | `python -m pip install --user pipx && python -m pipx ensurepath` |

**Already using uv?** `uvx --from regula-ai regula` runs it with no install step (the `--from` flag is required because the PyPI package name `regula-ai` differs from the CLI name `regula`). Or install it permanently with `uv tool install regula-ai`.

**Running inside a venv or conda env?** `pip install regula-ai` works fine there — the PEP 668 restriction only applies to system Python.

See [`docs/installation.md`](docs/installation.md) for troubleshooting (`externally-managed-environment`, `command not found: regula` after install, PATH setup per shell).

### Try it against a known high-risk fixture:

```bash
regula check examples/cv-screening-app --scope all
```

The `--scope all` flag is needed because Regula's default scope (`production`) skips example directories. This fixture intentionally triggers an Annex III Category 4 (Employment) high-risk classification.

See [`examples/`](examples/) for runnable reference projects covering each EU AI Act risk tier, or walk through the full 10-minute evaluation journey in [`examples/cv-screening-app/`](examples/cv-screening-app/) — install, scan, plan, gap, conform, verify, handoff to red-team tooling.

For a deeper first-time-user walk-through (policy tuning, CI integration, baselining) see [`docs/QUICKSTART.md`](docs/QUICKSTART.md). The full documentation is indexed by type (tutorials / how-to / reference / explanation) in [`docs/README.md`](docs/README.md).

### CI/CD

```yaml
# .github/workflows/regula.yaml
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

## What Regula tells you

The EU AI Act defines four risk tiers. Regula maps code patterns to each:

| Tier | Action | What it means |
|------|--------|---------------|
| **Potentially prohibited** (Article 5) | Block indicator | Reports code patterns associated with listed practices for urgent contextual review. |
| **Potentially high-risk** (Article 6 and Annex III) | Warn + review map | Reports candidate use categories and maps provisions that may be relevant if a reviewer confirms the legal classification. |
| **Potential transparency duty** (Article 50) | Transparency indicator | Reports chatbot, synthetic-content and related implementation signals; the applicable paragraph and exceptions require review. |
| **No elevated code indicator** | Log only | Means the scanner did not observe a configured elevated indicator. It does not establish minimal-risk status or absence of legal duties. |

Every finding includes the relevant Article reference and explains when exceptions may apply. Regula flags patterns -- it does not make legal determinations.

**Multi-jurisdiction support.** Beyond the EU AI Act, Regula maps risk patterns to South Korea's AI Basic Act (Act No. 20676, in force 22 January 2026) and Colorado SB 26-189 (disclosure-focused, plus consumer correction and human-review rights, duties from 1 January 2027). Use `--jurisdictions eu,korea,colorado` on `regula check` or `--jurisdiction korea` on `regula assess` to apply the relevant framework. Each jurisdiction has its own YAML config (`references/jurisdictions/`) and tailored web questionnaire.

**Developer guides** on getregula.com:
[Python](https://getregula.com/guides/eu-ai-act-python.html) |
[JavaScript](https://getregula.com/guides/eu-ai-act-javascript.html) |
[Healthcare](https://getregula.com/guides/eu-ai-act-healthcare.html) |
[Recruitment](https://getregula.com/guides/eu-ai-act-recruitment-hiring.html) |
[Article 5](https://getregula.com/guides/article-5-prohibited-practices.html) |
[Article 9](https://getregula.com/guides/article-9-risk-management.html) |
[Article 14](https://getregula.com/guides/article-14-human-oversight.html) |
[Article 50](https://getregula.com/guides/article-50-transparency.html)

## Key commands

| Command | What it does |
|---------|-------------|
| `regula` | Scan current directory, show compliance score and next steps |
| `regula check .` | Detailed risk scan with per-file findings |
| `regula comply` | EU AI Act obligation checklist with completion status |
| `regula gap --project .` | Compliance gap assessment against Articles 9-15 |
| `regula plan --project .` | Prioritised remediation plan based on gap results |
| `regula fix --project .` | Generate compliance fix scaffolds for findings |
| `regula evidence-pack --project .` | Reviewer-completable evidence scaffold with integrity metadata |
| `regula conform --project .` | Article 43 conformity assessment evidence pack |
| `regula dpv --project .` | Export the risk indication as DPV-AIAct JSON-LD (aligned to the DPVCG EU-AIAct vocabulary) for RDF/GRC tooling |
| `regula check --ci .` | CI mode -- exit code 1 on any WARN or BLOCK finding, SARIF output |
| `regula assess` | Structured declared-context questionnaire for applicability and risk review |
| `regula demo` | Scan a bundled example project -- zero-commitment trial |
| `regula api-server` | Start the REST API (localhost:8487) with web dashboard |
| `regula conform --organisational` | Governance self-assessment for Articles 9/17/27/72 |
| `regula questionnaire` | Context-driven risk assessment questionnaire (also via REST API) |
| `regula exempt` | Article 6(3) high-risk exemption decision tree |
| `regula oversight .` | Article 14 human oversight analysis (cross-file flow tracing) |
| `regula guardrails .` | Article 15 guardrail implementation coverage detection |
| `regula owasp-agentic` | OWASP Top 10 for Agentic Applications assessment |
| `regula monitor` | Runtime monitoring for AI applications (Article 12) |
| `regula gdpr` | GDPR cross-reference scan ([14 focused checks](scripts/gdpr_scan.py), 4 AI Act/GDPR hotspots) |
| `regula bias` | CrowS-Pairs bias evaluation (1,508 sentence pairs) with optional BBQ benchmark. Aligned with Digital Omnibus bias-testing safeguards (Article 4a, COM(2025)836). |
| `regula mcp-server` | MCP server (JSON-RPC stdio) exposing three tools — `regula_check`, `regula_classify`, `regula_gap` — for Claude Code, Cursor, and other MCP clients |
| `regula install <platform>` | Set up pre-commit hooks, git hooks, or Claude Code/Copilot/Windsurf integration |

Regula has 62 commands in total. Run `regula --help-all` for the full list, or see [`docs/cli-reference.md`](docs/cli-reference.md).

### REST API and web dashboard

For GRC integration or non-terminal users:

```bash
python3 scripts/api_server.py --port 8487
# Open http://localhost:8487/v1/dashboard
```

Seven endpoints: `/health`, `/v1/check`, `/v1/classify`, `/v1/gap`, `/v1/questionnaire`, `/v1/questionnaire/evaluate`, `/v1/dashboard`. All return the same JSON envelope as the CLI. No auth -- run behind a reverse proxy for remote access.

## Who is this for?

- **Solo founders and indie hackers** building AI products who need an initial inventory of code-observable governance indicators before contextual and legal review.
- **Small teams** who want to understand their compliance exposure before it becomes a sales blocker. Enterprise procurement is already asking for AI Act evidence.
- **Engineering teams** who want EU AI Act scanning in CI/CD to catch high-risk or prohibited patterns before they ship.
- **AI governance consultants and advisors** — run Regula on a client's codebase to produce code-observation reports, gap-review scaffolds, and hash-manifested documentation for completion and review within a broader governance engagement. Selected generated facts have repository checks; limitations and reproduction commands are recorded in the trust pack. Deliverables can carry engagement metadata (client, preparer, reference) via the `engagement:` policy section or `--client`/`--prepared-by`/`--engagement-ref` flags. See the [consultant guide](docs/consultant-guide.md) for the workflow and its boundaries.

## What Regula is (and isn't)

**Regula is:**

- A development-time compliance tool that combines static code analysis with governance questionnaires, mapping both to obligations across 3 jurisdictions (EU AI Act, South Korea AI Basic Act, Colorado SB 26-189)
- A shift-left code-indicator scanner -- like ESLint for governance review, running in your terminal or CI/CD pipeline
- A questionnaire-based assessment tool for organisational obligations that code patterns cannot verify (Articles 9, 17, 27, 72)
- Pattern-based risk indication across 3 jurisdictions, not a legal compliance certificate
- A starting point for compliance awareness, not a finish line

**Regula is not:**

- A runtime monitoring system (it analyses source code, not running systems)
- A legal compliance certificate (findings are indicators, not legal determinations)
- A replacement for enterprise GRC platforms like Credo AI or Holistic AI (it complements them)
- A production fairness testing platform (`regula bias` runs benchmark probes against a local model as a starting point, but does not replace runtime fairness monitoring)
- Legal advice (consult qualified legal counsel for compliance decisions)

Regula helps development teams understand their EU AI Act exposure early. It does not replace the organisational, procedural, and legal work required for full compliance. For a detailed account of what falls outside Regula's scope, see [`docs/what-regula-does-not-do.md`](docs/what-regula-does-not-do.md), and for Regula's own model card (intended use, training data, evaluation, known failure modes) see [`docs/MODEL_CARD.md`](docs/MODEL_CARD.md).

## Bias evaluation — methodology and ethics

`regula bias` runs two social-bias benchmarks against a locally-hosted
language model (Ollama, `llama3.2`/`mistral`/`qwen` variants supported)
as evidence for EU AI Act Article 10 data-governance documentation.

| Benchmark | Paper | Method | What it measures |
|---|---|---|---|
| CrowS-Pairs | Nangia et al., 2020 | Log-probability difference between stereotypical and anti-stereotypical sentence pairs | Intrinsic bias in masked/causal LM output |
| BBQ | Parrish et al., 2022 | Question-answering on ambiguous-context prompts | Bias surfacing in downstream QA behaviour |

Both include Wilson confidence intervals for small-sample reliability and
bootstrap CIs for distribution estimates. Full methodology lives in
[`scripts/bias_eval.py`](scripts/bias_eval.py) and
[`docs/benchmarks/PRECISION_RECALL_2026_04.md`](docs/benchmarks/PRECISION_RECALL_2026_04.md).

**Ethics statement.** CrowS-Pairs and BBQ stereotype pairs are used
**solely for scientific evaluation** of model behaviour under controlled
conditions. Regula does **not display individual stereotype pairs** in
terminal output or reports — only aggregated scores, confidence
intervals, and benchmark-level verdicts. The pairs are distributed under
the dataset's own licence (CC BY-SA 4.0 for CrowS-Pairs) and are not
redistributed or modified by Regula. Opinions encoded in the stereotype
pairs do not reflect the views of the maintainer, Regula contributors,
or any user running the tool; their presence is instrumental, not
endorsing. `regula bias` is a development-time starting point for bias
documentation, not a production fairness monitor — see "What Regula is
(and isn't)" above.

## Important limitations

Regula performs **pattern-based risk indication**, not legal risk classification.

- The EU AI Act classifies risk based on intended purpose and deployment context (Article 6), not code patterns. Regula's findings are indicators that warrant human review.
- **False positives will occur.** Blind-labelled benchmark on 50 randomly selected Python AI repos measured **83.5% precision on production code** (N=115, measured on v1.7.0, labelled by a single reviewer with no inter-rater agreement measurement). Per-tier: `ai_security` (85%), `agent_autonomy` (83%), `limited_risk` (88%), `minimal_risk` (100%). The `high_risk` tier (33%, N=6) is statistically unmeasurable at this sample size. Full methodology, corpus selection, and reproduction steps: [`benchmarks/README.md`](benchmarks/README.md).
- **TypeScript findings are advisory:** 0% precision on the current benchmark (6 FP, 0 TP). Language-specific AST gating is not yet implemented for TypeScript.
- **False negatives will occur.** Novel risk patterns not in the database will be missed.
- Article 5 prohibitions have conditions and exceptions that require human judgment.
- The audit trail is self-attesting (locally verifiable, not externally witnessed).
- This is not a substitute for legal advice or DPO review.

## Verified numbers

| What | Count |
|------|------:|
| CLI commands | 62 |
| Risk detection patterns (regexes) | 419 |
| Language families scanned | 8 (Python, JS, TS, Java, Go, Rust, C/C++, Jupyter) |
| Compliance frameworks mapped | 13 |
| Tests (pytest --collect-only, all passing) | 2,681 |
| Required production dependencies | 0 |

For reproduction commands, version-bounded benchmarks, known exceptions, security posture, and audit-trail design, see [`docs/TRUST.md`](docs/TRUST.md). What version numbers promise, the public API they cover, and the deprecation policy: [`docs/VERSIONING.md`](docs/VERSIONING.md).

## Privacy and data handling

Regula runs entirely on your machine. No code, findings, or metadata are transmitted to any external service. There is no account system, no API key, no telemetry by default (crash reporting requires both `regula telemetry enable` **and** an endpoint you configure yourself via `REGULA_SENTRY_DSN`; published builds ship none, and `DO_NOT_TRACK` suppresses it regardless). The tool reads your source files, analyses them locally, and writes output to your local filesystem. Network access is only used when you explicitly request it (RFC 3161 timestamps via `--timestamp`). See [`SECURITY.md`](SECURITY.md) for the full security posture.

## Contributing

Bug reports and pull requests are welcome.

- Run `pytest tests/ -q` before opening a PR.
- Pattern additions go in `scripts/risk_patterns.py`. Each pattern should have a corresponding test.
- Regula is intentionally risk *indication*, not legal classification. New patterns should be conservative -- false positives erode trust more than false negatives for a developer tool.
- See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the full contributor guide and [`CHANGELOG.md`](CHANGELOG.md) for version history.

### Authorship

Regula is maintained by Kuziva Muzondo (solo). Commits include a `Co-Authored-By: Claude Opus 4.6` trailer where the work was paired with Anthropic's Claude. This is standard pair-programming attribution — the maintainer is accountable for every merged change, and every commit was reviewed and reasoned about by a human before landing. Said plainly so you know how the sausage is made.

## Licence

**Engine and CLI:** [Apache License 2.0](LICENSE.txt) **OR** [European Union Public Licence v. 1.2](LICENSE.EUPL) — at your option. Pick the one that fits your context:

- **Apache 2.0** includes an explicit patent grant, making it the preferred choice for enterprise adoption, commercial redistribution, and any context where patent clarity matters.
- **EUPL-1.2** is explicitly recognised inside EU institutions and public-sector procurement, is strongly-copyleft on software, and has a formal compatibility appendix (GPL v2/v3, AGPL v3, OSL, EPL, CeCILL, MPL 2.0, LGPL, CC BY-SA 3.0) for downstream projects. If you work with a European public administration, EUPL is often the required or preferred licence.

You may choose either licence for any use. You do not need to state which one you picked, but attribution (keep the copyright notice and NOTICE file) is required under both.

**Risk patterns and regulatory data:** [Detection Rule License (DRL) 1.1](docs/LICENSE.Detection.Rules.md). You may use, modify, and redistribute the patterns freely. Attribution is required if you redistribute the patterns or use them in a product. If your tool generates match output from these patterns, the output must credit the source.

The SPDX expression for the full package is `(Apache-2.0 OR EUPL-1.2) AND LicenseRef-DRL-1.1`.
