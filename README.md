# Regula

**EU AI Act compliance tool for code.**

[![PyPI](https://img.shields.io/pypi/v/regula-ai)](https://pypi.org/project/regula-ai/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE.txt)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![CI](https://github.com/kuzivaai/getregula/actions/workflows/ci.yaml/badge.svg)](https://github.com/kuzivaai/getregula/actions)
[![Tests](https://img.shields.io/badge/tests-947%20passing-brightgreen.svg)](#verified-numbers)

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

![Regula check demo](assets/demo/regula-check.svg)

---

## What it does

If you ship an AI product to EU users, the EU AI Act applies to you -- regardless of where you are based or how small your team is. Regula scans your codebase for risk indicators, classifies your system into one of the Act's four risk tiers, and tells you which obligations apply. It runs in your terminal, in CI/CD, or as a pre-commit hook. No external dependencies, no API calls, no data leaves your machine.

## Quick start

### Install

The recommended install is **pipx** — it works on every platform (Linux, macOS, Windows), isolates Regula from your system Python, and does not trip the `externally-managed-environment` error that Ubuntu 22.04+, Debian 12+, Fedora, Arch, and Homebrew Python raise against plain `pip`.

```bash
pipx install regula-ai
```

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

### Scan

From your project directory:

```bash
regula
```

That single command scans your code and produces a summary:

```
Regula -- yourproject
============================================================
  Files scanned:          42
  BLOCK findings:         0
  WARN findings:          1
  INFO findings:          8
  Compliance score:       97/100
  Highest risk tier:      high_risk
  Scan time:              1.4s
============================================================

  Next steps:
    1. regula check .                  Review findings in detail
    2. regula comply                   Check your obligations
    3. regula plan --project .         Prioritised remediation plan
```

For a more detailed scan:

```bash
regula check .
```

Try it against a known high-risk fixture:

```bash
regula check examples/cv-screening-app
```

See [`examples/`](examples/) for runnable reference projects covering each EU AI Act risk tier.

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
| **Prohibited** (Article 5) | Block | Social scoring, subliminal manipulation, real-time biometric ID, emotion detection in workplaces. Regula blocks these patterns and explains the specific prohibition. |
| **High-risk** (Annex III) | Warn + requirements | CV screening, credit scoring, medical diagnosis, biometrics, education assessment. Regula lists the Articles 9-15 obligations that apply if the system is confirmed high-risk. |
| **Limited-risk** (Article 50) | Transparency note | Chatbots, deepfakes, emotion recognition. Regula flags the transparency disclosure required. |
| **Minimal-risk** | Log only | Spam filters, recommendations, code completion. Logged for awareness, no action required. |

Every finding includes the relevant Article reference and explains when exceptions may apply. Regula flags patterns -- it does not make legal determinations.

## Key commands

| Command | What it does |
|---------|-------------|
| `regula` | Scan current directory, show compliance score and next steps |
| `regula check .` | Detailed risk scan with per-file findings |
| `regula comply` | EU AI Act obligation checklist with completion status |
| `regula gap --project .` | Compliance gap assessment against Articles 9-15 |
| `regula plan --project .` | Prioritised remediation plan based on gap results |
| `regula fix --project .` | Generate compliance fix scaffolds for findings |
| `regula evidence-pack --project .` | Auditor-ready evidence package |
| `regula conform --project .` | Article 43 conformity assessment evidence pack |
| `regula check --ci .` | CI mode -- exit code 1 on any WARN or BLOCK finding, SARIF output |
| `regula assess` | Interactive applicability check -- does the EU AI Act apply to you? |

Regula has 53 commands in total. Run `regula --help-all` for the full list, or see [`docs/cli-reference.md`](docs/cli-reference.md).

## Who is this for?

- **Solo founders and indie hackers** building AI products (with Claude Code, Cursor, or similar) who have EU users and need to know what the EU AI Act means for their code.
- **Small teams** who want to understand their compliance exposure before it becomes a sales blocker. Enterprise procurement is already asking for AI Act evidence.
- **Engineering teams** who want EU AI Act scanning in CI/CD to catch high-risk or prohibited patterns before they ship.

## What Regula is (and isn't)

**Regula is:**

- A development-time static analysis tool that detects AI-related code patterns and maps them to EU AI Act obligations
- A shift-left compliance scanner -- like ESLint for regulatory risk, running in your terminal or CI/CD pipeline
- A starting point for compliance awareness, not a finish line

**Regula is not:**

- A runtime monitoring system (it analyses source code, not running systems)
- A legal compliance certificate (findings are indicators, not legal determinations)
- A replacement for enterprise GRC platforms like Credo AI or Holistic AI (it complements them)
- A production fairness testing platform (`regula bias` runs benchmark probes against a local model as a starting point, but does not replace runtime fairness monitoring)
- Legal advice (consult qualified legal counsel for compliance decisions)

Regula helps development teams understand their EU AI Act exposure early. It does not replace the organisational, procedural, and legal work required for full compliance. For a detailed account of what falls outside Regula's scope, see [`docs/what-regula-does-not-do.md`](docs/what-regula-does-not-do.md).

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
- **False positives will occur.** The self-benchmark on five labelled open-source projects (257 hand-labelled findings) measured **15.2% overall precision**. The minimal-risk tier accounts for 94% of findings on general-purpose libraries and is the noisiest. Full methodology and reproduction steps: [`benchmarks/README.md`](benchmarks/README.md).
- **False negatives will occur.** Novel risk patterns not in the database will be missed.
- Article 5 prohibitions have conditions and exceptions that require human judgment.
- The audit trail is self-attesting (locally verifiable, not externally witnessed).
- This is not a substitute for legal advice or DPO review.

## Verified numbers

| What | Count |
|------|------:|
| CLI commands | 53 |
| Risk detection patterns (regexes) | 403 |
| Language families scanned | 8 (Python, JS, TS, Java, Go, Rust, C/C++, Jupyter) |
| Compliance frameworks mapped | 17 |
| Tests (all passing) | 947 |
| Required production dependencies | 0 |

## Contributing

Bug reports and pull requests are welcome.

- Run `pytest tests/ -q` before opening a PR.
- Pattern additions go in `scripts/classify_risk.py`. Each pattern should have a corresponding test.
- Regula is intentionally risk *indication*, not legal classification. New patterns should be conservative -- false positives erode trust more than false negatives for a developer tool.
- See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the full contributor guide and [`CHANGELOG.md`](CHANGELOG.md) for version history.

### Authorship

Regula is maintained by Kuziva Muzondo (solo). Commits include a `Co-Authored-By: Claude Opus 4.6` trailer where the work was paired with Anthropic's Claude. This is standard pair-programming attribution — the maintainer is accountable for every merged change, and every commit was reviewed and reasoned about by a human before landing. Said plainly so you know how the sausage is made.

## Licence

**Engine and CLI:** [MIT License](LICENSE.txt) **OR** [European Union Public Licence v. 1.2](LICENSE.EUPL) — at your option. Pick the one that fits your context:

- **MIT** is the simplest and most compatible choice for private companies, SaaS, and most commercial redistribution.
- **EUPL-1.2** is explicitly recognised inside EU institutions and public-sector procurement, is strongly-copyleft on software, and has a formal compatibility appendix (GPL v2/v3, AGPL v3, OSL, EPL, CeCILL, MPL 2.0, LGPL, CC BY-SA 3.0) for downstream projects. If you work with a European public administration, EUPL is often the required or preferred licence.

You may choose either licence for any use. You do not need to state which one you picked, but attribution (keep the copyright notice) is required under both.

**Risk patterns and regulatory data:** [Detection Rule License (DRL) 1.1](docs/LICENSE.Detection.Rules.md). You may use, modify, and redistribute the patterns freely. Attribution is required if you redistribute the patterns or use them in a product. If your tool generates match output from these patterns, the output must credit the source.

The SPDX expression for the full package is `(MIT OR EUPL-1.2) AND LicenseRef-DRL-1.1`.
