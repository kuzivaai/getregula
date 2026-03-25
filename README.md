# Regula

**AI Governance Enforcement for Claude Code**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE.txt)
[![EU AI Act](https://img.shields.io/badge/EU%20AI%20Act-Compliant-green.svg)](#regulatory-coverage)

Regula is a Claude Code skill that enforces AI governance at the point of code creation. It automatically classifies AI systems against EU AI Act risk tiers, blocks prohibited practices, and maintains an immutable audit trail.

## Why Regula?

The EU AI Act (Regulation 2024/1689) is now in force:

- **2 February 2025:** Prohibited AI practices (Article 5) apply
- **2 August 2026:** High-risk system requirements (Articles 9-15) fully apply

Penalties reach up to **€35 million or 7% of global turnover**.

## What It Does

| Feature | Description |
|---------|-------------|
| **Risk Classification** | Automatically classifies code against EU AI Act risk tiers |
| **Real-time Blocking** | Blocks prohibited AI practices immediately |
| **Compliance Guidance** | Provides Article 9-15 requirements for high-risk systems |
| **Audit Trail** | Maintains immutable, hash-chained logs |
| **Documentation** | Generates Annex IV compliant technical documentation |

## Installation

```bash
# Clone the repository
git clone https://github.com/kuzivaai/getregula.git

# Copy to your Claude Code skills directory
cp -r getregula ~/.claude/skills/regula
```

## Usage

Once installed, Regula activates automatically when you work with AI-related code:

```
User: "Build a CV screening function that auto-filters candidates"

Claude: ⚠️ HIGH-RISK AI SYSTEM DETECTED

This operation involves automated CV screening, classified as HIGH-RISK
under EU AI Act Annex III, Category 4 (Employment).

Applicable Requirements:
• Article 9: Risk management system
• Article 10: Bias-examined training data
• Article 14: Human oversight mechanism
...
```

## Regulatory Coverage

| Risk Tier | Action | Coverage |
|-----------|--------|----------|
| **Prohibited** | Block | Social scoring, emotion inference in workplace, real-time biometric ID |
| **High-Risk** | Warn + Requirements | Employment, credit scoring, education, biometrics, critical infrastructure |
| **Limited-Risk** | Transparency reminder | Chatbots, emotion recognition, synthetic content |
| **Minimal-Risk** | Log only | Spam filters, recommendations, games |

## Testing

```bash
python3 tests/test_classification.py
```

## License

MIT License. See [LICENSE.txt](LICENSE.txt).

## Author

Built by [The Implementation Layer](https://theimplementationlayer.substack.com)
