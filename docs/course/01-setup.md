# regula-ignore
# Module 1: Setup

## What You'll Learn

- Install Regula
- Run your first scan
- Understand the output format

## Install

```bash
git clone https://github.com/kuzivaai/getregula.git
cd getregula
```

Regula has zero required dependencies — it runs on Python's standard library. Optional: install `pyyaml` for full YAML support in framework mapping and advisory features.

```bash
pip install pyyaml  # optional but recommended
```

## Verify Installation

```bash
python3 scripts/cli.py --help
```

You should see 20 commands listed:

```
agent, audit, baseline, benchmark, check, classify, compliance,
deps, discover, docs, feed, gap, init, install, questionnaire,
report, sbom, session, status, timeline
```

## Run Your First Scan

Scan Regula's own codebase:

```bash
python3 scripts/cli.py check .
```

You should see output showing files scanned, findings by tier, and any high-risk indicators detected. The test fixture file (`tests/fixtures/sample_high_risk/app.py`) contains a deliberately created employment screening example and will appear as a high-risk finding. This is expected behaviour.

## Understanding the Output

Regula classifies findings into tiers based on the EU AI Act:

| Tier | What It Means | Action |
|------|--------------|--------|
| **Prohibited** | Matches an Article 5 banned practice | Blocked — cannot proceed |
| **High-Risk** | Matches an Annex III category (e.g., credit AI, hiring AI) | Warning with Article 9-15 requirements |
| **Limited-Risk** | Transparency obligation (e.g., chatbots, deepfakes) | Note — inform users they interact with AI |
| **Minimal-Risk** | AI code detected, no specific regulatory concern | Logged only |
| **AI Security** | Code-level vulnerability (e.g., unsafe deserialization) | Warning with OWASP LLM reference |
| **Credential** | Hardcoded API key or secret detected | Blocked or warned |

Each finding gets a **confidence score** (0-100) mapped to a **finding tier**:
- **BLOCK** (score >= 80): High confidence — CI should fail
- **WARN** (score 50-79): Medium confidence — needs human review
- **INFO** (score < 50): Low confidence — shown only with `--verbose`

Findings in test files are automatically deprioritised (-40 confidence) to reduce noise.

## Exercise

1. Run `python3 scripts/cli.py check . --verbose` — how many INFO-tier findings appear?
2. Run `python3 scripts/cli.py check . --format json | python3 -m json.tool | head -30` — examine the JSON structure
3. Run `python3 scripts/cli.py classify --input "import openai; credit_risk_model(data)"` — what tier does it return?

## Verification

If `classify` returned HIGH-RISK with Annex III Category 5 (essential services), you're set up correctly.

---

**Next:** [Module 2: Risk Classification](02-risk-classification.md)
