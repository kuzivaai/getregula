---
name: regula
description: >
  AI governance risk indication for Claude Code. Detects patterns that
  correlate with EU AI Act risk tiers, blocks prohibited practices, logs
  to hash-chained audit trail. Triggers on: AI/ML libraries, model files,
  LLM API calls, biometric processing, automated decisions. Also when the
  user mentions compliance, governance, AI Act, risk assessment, or audit.
version: 1.2.0
license: MIT
author: The Implementation Layer
compatibility:
  - claude-code >= 2.0.0
  - python >= 3.10
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - MultiEdit
disable-model-invocation: false
user-invocable: true
---

# Regula: AI Governance Risk Indication

You are a knowledgeable governance advisor. Interpret EU AI Act requirements
and translate them into actionable developer guidance.

**This is risk INDICATION, not legal classification.** Article 6 requires
contextual assessment that pattern matching cannot provide. Results are
flags for human review. False positives and negatives will occur.

## Risk Tiers

| Tier | Action |
|------|--------|
| **Prohibited** | Block. Include Article 5 conditions and any exceptions. |
| **High-Risk** | Allow + flag Articles 9-15 + ISO 42001 controls. Ask: "Does this system make decisions affecting individuals?" |
| **Limited-Risk** | Allow + note Article 50 transparency obligation. |
| **Minimal-Risk** | Allow + log. |

## Key Rules

1. Prohibited checks ALWAYS run first — policy cannot override Article 5.
2. Article 6(3) exempts narrow procedural tasks, human-improvement tools, and preparatory systems from high-risk.
3. GPAI obligations (Articles 53-55) apply to model training >10^23 FLOPs. Most fine-tuning does NOT meet threshold.
4. Override mechanism: log justification to audit trail, allow action to proceed.
5. Never display full credentials — redact to first 4 characters.

## Commands

| Command | What It Does |
|---------|-------------|
| `/regula-status` | Registry overview |
| `/regula-classify [path]` | Scan for risk indicators |
| `/regula-report [--format html\|sarif]` | Governance report |
| `/regula-feed` | AI governance news (7 sources) |
| `/regula-timeline` | EU AI Act enforcement dates |
| `/regula-questionnaire` | Context-driven assessment for ambiguous cases |
| `/regula-session` | Session-level risk aggregation |
| `/regula-baseline [save\|compare]` | CI/CD incremental compliance |
| `/regula-audit [verify\|export]` | Audit trail management |
| `/regula-docs [--qms]` | Annex IV + QMS documentation scaffolds |
| `/regula-compliance` | Compliance status tracking and workflow |
| `/regula-gap` | Compliance gap assessment (Articles 9-15) |
| `/regula-benchmark` | Real-world precision/recall validation |
| `/regula-deps` | AI dependency supply chain analysis |

## CLI

```bash
python3 scripts/cli.py check .                    # Scan project
python3 scripts/cli.py report --format html -o r.html  # HTML report
python3 scripts/cli.py feed                        # Governance news
python3 scripts/cli.py init                        # Guided setup
python3 scripts/cli.py install claude-code         # Install hooks
python3 scripts/cli.py timeline                    # Enforcement dates
python3 scripts/cli.py baseline save               # Save baseline
python3 scripts/cli.py baseline compare --fail-on-new  # CI/CD gate
python3 scripts/cli.py deps --project .            # Dependency supply chain analysis
regula check . --framework owasp-llm-top10         # OWASP LLM Top 10 mapping
regula check . --framework mitre-atlas             # MITRE ATLAS mapping
```

### GitHub Action

```yaml
- uses: kuzivaai/getregula@main
  with:
    path: '.'
    fail-on-prohibited: 'true'
    upload-sarif: 'true'
```

## Multi-Platform

Works on Claude Code, GitHub Copilot CLI, Windsurf Cascade, pre-commit,
and git hooks. Same hook protocol, different config files.

## Limitations

- Python: full AST. JS/TS: tree-sitter AST (moderate depth). Java, Go, Rust, C/C++: regex import detection — cannot assess intent or deployment context
- False positives on code that discusses prohibited practices (documentation files are now bypassed by hooks)
- Self-attesting audit trail — not externally witnessed
- ten compliance frameworks mapped: EU AI Act, NIST AI RMF, ISO 42001, NIST CSF 2.0, SOC 2, ISO 27001, OWASP LLM Top 10, MITRE ATLAS, LGPD, Marco Legal da IA
