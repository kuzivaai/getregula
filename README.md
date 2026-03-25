# Regula

**AI Governance Enforcement at the Point of Code Creation**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE.txt)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![EU AI Act](https://img.shields.io/badge/EU%20AI%20Act-Compliant-green.svg)](#regulatory-coverage)
[![CI](https://github.com/kuzivaai/getregula/actions/workflows/ci.yaml/badge.svg)](https://github.com/kuzivaai/getregula/actions)

Regula is a Claude Code skill that enforces AI governance compliance in real-time. It intercepts AI-related code as developers write it, classifies operations against EU AI Act risk tiers, blocks prohibited practices, provides compliance guidance for high-risk systems, and maintains an immutable audit trail.

## The Problem

The EU AI Act (Regulation 2024/1689) is now in force:

| Date | Requirement |
|------|-------------|
| **2 February 2025** | Prohibited AI practices (Article 5) apply — **live now** |
| **2 August 2025** | General-purpose AI model rules apply |
| **2 August 2026** | High-risk system requirements (Articles 9-15) fully apply |

**Penalties:** Up to **€35 million** or **7% of global annual turnover**.

Current AI governance tools cost $50K-500K+/year, require 6-12 month implementations, and operate post-deployment. Nothing exists at the code creation layer — until now.

## How It Works

Regula operates as a three-layer defence:

```
┌─────────────────────────────────────────────────────────┐
│  SKILL LAYER — Expert auditor persona & guidance        │
├─────────────────────────────────────────────────────────┤
│  HOOK LAYER — Deterministic enforcement (block/allow)   │
├─────────────────────────────────────────────────────────┤
│  AUDIT LAYER — Immutable, hash-chained event log        │
└─────────────────────────────────────────────────────────┘
```

When a developer writes AI-related code, Regula:

1. **Detects** AI indicators (libraries, model files, API calls, ML patterns)
2. **Classifies** the operation against EU AI Act risk tiers
3. **Blocks** prohibited practices immediately (exit code 2)
4. **Warns** about high-risk system requirements (Articles 9-15)
5. **Logs** everything to a tamper-evident audit trail

## What It Does

| Feature | Description |
|---------|-------------|
| **Risk Classification** | Classifies code against 4 EU AI Act risk tiers |
| **Real-time Blocking** | Blocks all 8 Article 5 prohibited practices |
| **Compliance Guidance** | Flags Articles 9-15 requirements for high-risk systems |
| **Audit Trail** | SHA-256 hash-chained, append-only event log |
| **Documentation** | Generates Annex IV compliant technical documentation |

## Installation

```bash
# Clone the repository
git clone https://github.com/kuzivaai/getregula.git

# Copy to your Claude Code skills directory
cp -r getregula ~/.claude/skills/regula
```

### Configure Hooks

Add to your Claude Code `settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": ".*",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ~/.claude/skills/regula/hooks/pre_tool_use.py"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": ".*",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ~/.claude/skills/regula/hooks/post_tool_use.py"
          }
        ]
      }
    ],
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ~/.claude/skills/regula/hooks/stop_hook.py"
          }
        ]
      }
    ]
  }
}
```

## Usage

### Automatic Enforcement

Once installed, Regula activates automatically when you work with AI-related code:

```
User: "Build a CV screening function that auto-filters candidates"

Claude: ⚠️ HIGH-RISK AI SYSTEM DETECTED

Category: Annex III, Category 4 — Employment and workers management
Indicators: cv_screen, hiring_decision

Applicable Requirements (effective 2 August 2026):
• Article 9: Implement risk management system
• Article 10: Ensure training data is representative and bias-examined
• Article 11: Maintain technical documentation (Annex IV)
• Article 12: Enable automatic logging of decisions
• Article 13: Provide transparency to affected persons
• Article 14: Implement human oversight mechanism
• Article 15: Validate accuracy and implement security measures
```

### Prohibited Practice Blocking

```
User: "Build a social credit scoring system"

🛑 PROHIBITED AI PRACTICE — ACTION BLOCKED

Specific prohibition: Article 5(1)(c)
Description: Social scoring systems evaluating persons based on social behaviour
Indicator detected: social_scoring

This action CANNOT proceed. Penalties: up to €35M or 7% global turnover.
```

### CLI Usage

```bash
# Classify a text input
python3 scripts/classify_risk.py --input "import tensorflow; cv screening model" --format json

# Classify a file
python3 scripts/classify_risk.py --file model.py --format json

# Generate Annex IV documentation
python3 scripts/generate_documentation.py --project . --output docs/

# Query audit trail
python3 scripts/log_event.py query --event-type classification --limit 50

# Verify audit chain integrity
python3 scripts/log_event.py verify
```

### Skill Commands

| Command | Description |
|---------|-------------|
| `/regula-status` | Show governance status and compliance gaps |
| `/regula-classify [path]` | Classify AI systems in a path |
| `/regula-audit [--export format]` | View/export audit trail |
| `/regula-docs [--output path]` | Generate Annex IV documentation |
| `/regula-policy [validate\|apply\|test]` | Manage governance policies |

## Regulatory Coverage

### Risk Tiers

| Tier | Action | Examples |
|------|--------|----------|
| **Prohibited** | Block | Social scoring, emotion in workplace, real-time biometric ID, race detection |
| **High-Risk** | Warn + Requirements | CV screening, credit scoring, medical diagnosis, biometrics, education |
| **Limited-Risk** | Transparency note | Chatbots, deepfakes, age estimation, emotion recognition |
| **Minimal-Risk** | Log only | Spam filters, recommendations, code completion |

### Prohibited Practices (Article 5)

All 8 prohibited practices are detected and blocked:

1. Subliminal manipulation beyond consciousness
2. Exploitation of vulnerabilities (age, disability, economic situation)
3. Social scoring by public authorities
4. Criminal risk prediction based solely on profiling
5. Untargeted facial recognition database scraping
6. Emotion inference in workplace/education
7. Biometric categorisation inferring sensitive attributes (race, politics, religion, sexuality)
8. Real-time remote biometric ID in public spaces

### High-Risk Categories (Annex III)

All 10 Annex III categories are detected:

1. Biometrics (identification, categorisation)
2. Critical infrastructure (energy, water, traffic)
3. Education (admissions, assessments, proctoring)
4. Employment (CV screening, hiring, promotions, terminations)
5. Essential services (credit scoring, insurance, benefits)
6. Law enforcement (polygraphs, evidence analysis)
7. Migration (visa, asylum, border control)
8. Justice and democracy (judicial decisions, elections)
9. Medical devices (diagnosis, clinical decisions, treatment)
10. Safety components (autonomous vehicles, aviation)

## Architecture

```
regula/
├── SKILL.md                       # Core skill file
├── scripts/
│   ├── classify_risk.py           # Risk classification engine
│   ├── log_event.py               # Audit trail management
│   └── generate_documentation.py  # Annex IV doc generator
├── hooks/
│   ├── pre_tool_use.py            # PreToolUse enforcement hook
│   ├── post_tool_use.py           # PostToolUse logging hook
│   └── stop_hook.py               # Session summary hook
├── references/
│   ├── risk_indicators.yaml       # Classification patterns
│   ├── eu_ai_act_articles_9_15.md # Full article text
│   └── annex_iv_template.md       # Documentation template
├── tests/
│   └── test_classification.py     # 40 test functions, 130+ assertions
├── regula-policy.yaml             # Policy configuration template
├── README.md
├── LICENSE.txt                    # MIT
└── .github/workflows/ci.yaml     # CI/CD
```

## Testing

```bash
python3 tests/test_classification.py
```

The test suite includes 40 test functions covering:
- AI detection (Python libraries, model files, API endpoints, ML patterns)
- All 8 prohibited practices
- All 10 high-risk categories
- Limited-risk scenarios
- Minimal-risk scenarios
- Edge cases (empty input, case insensitivity, priority ordering, serialisation)

## Configuration

Copy `regula-policy.yaml` to your project root and customise:

```yaml
version: "1.0"
organisation: "Your Organisation"

frameworks:
  - eu_ai_act

rules:
  risk_classification:
    force_high_risk: []       # Systems to always treat as high-risk
    exempt: []                # Systems confirmed as low-risk

  approvals:
    high_risk:
      required: true
      approvers: ["dpo@company.com"]

  logging:
    retention_years: 10
    pii_redaction: true
```

## Audit Trail

Events are stored in `~/.regula/audit/` as JSONL files with SHA-256 hash chaining:

```json
{
  "event_id": "uuid",
  "timestamp": "ISO8601",
  "event_type": "classification",
  "data": {
    "tier": "high_risk",
    "indicators_matched": ["employment", "cv_screen"],
    "applicable_articles": ["9", "10", "11", "12", "13", "14", "15"]
  },
  "previous_hash": "sha256...",
  "current_hash": "sha256..."
}
```

Verify integrity: `python3 scripts/log_event.py verify`

## Constraints

- **No external dependencies** — stdlib only
- **Python 3.10+**
- **Works offline** — no API calls required
- **Append-only audit** — no deletion capability
- **Tamper-evident** — SHA-256 hash chain verification

## Limitations

Regula provides governance guidance but:
- Is not a substitute for legal advice
- Cannot guarantee regulatory compliance
- Uses pattern matching that may miss novel risks
- Should be supplemented with DPO/legal review for high-stakes decisions

## Roadmap

- **v1.1:** ISO 42001 control mapping, NIST AI RMF integration
- **v1.2:** DPO dashboard, Slack/Teams alerting
- **v2.0:** Model card generation, bias testing integration, continuous monitoring

## License

MIT License. See [LICENSE.txt](LICENSE.txt).

## Author

Built by [The Implementation Layer](https://theimplementationlayer.substack.com) — AI governance from the practitioner side.
