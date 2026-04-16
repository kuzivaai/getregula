# Regula

**EU AI Act compliance tool for code.**

[![PyPI](https://img.shields.io/pypi/v/regula-ai)](https://pypi.org/project/regula-ai/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE.txt)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![CI](https://github.com/kuzivaai/getregula/actions/workflows/ci.yaml/badge.svg)](https://github.com/kuzivaai/getregula/actions)
[![Tests](https://img.shields.io/badge/tests-935%20passing-brightgreen.svg)](#verified-numbers)

---

## Table of contents

- [What it does](#what-it-does)
- [Quick start](#quick-start)
- [What Regula tells you](#what-regula-tells-you)
- [Key commands](#key-commands)
- [Who is this for?](#who-is-this-for)
- [What Regula is (and isn't)](#what-regula-is-and-isnt)
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

```bash
pip install regula-ai
```

Then, from your project directory:

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
| Tests (all passing) | 935 |
| Required production dependencies | 0 |

## Contributing

Bug reports and pull requests are welcome.

- Run `pytest tests/ -q` before opening a PR.
- Pattern additions go in `scripts/classify_risk.py`. Each pattern should have a corresponding test.
- Regula is intentionally risk *indication*, not legal classification. New patterns should be conservative -- false positives erode trust more than false negatives for a developer tool.
- See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the full contributor guide and [`CHANGELOG.md`](CHANGELOG.md) for version history.

## Licence

**Engine and CLI:** [MIT License](LICENSE.txt).

**Risk patterns and regulatory data:** [Detection Rule License (DRL) 1.1](LICENSE.Detection.Rules.md). You may use, modify, and redistribute the patterns freely. Attribution is required if you redistribute the patterns or use them in a product. If your tool generates match output from these patterns, the output must credit the source.
