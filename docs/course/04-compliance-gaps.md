# regula-ignore
# Module 4: Compliance Gap Assessment

## What You'll Learn

- Assess compliance gaps for EU AI Act Articles 9-15
- Understand what evidence Regula looks for
- Interpret per-article compliance scores

## Run a Gap Assessment

```bash
python3 scripts/cli.py gap --project /tmp/anthropic-cookbook
```

## What Each Article Checks

| Article | What Regula Looks For |
|---------|---------------------|
| **Art 9** (Risk Management) | Risk assessment docs, risk registers, mitigation plans |
| **Art 10** (Data Governance) | Data documentation, bias checking libraries, data validation |
| **Art 11** (Technical Docs) | Annex IV documentation, model cards, system descriptions |
| **Art 12** (Record-Keeping) | Logging frameworks, AI operation logging, structured audit logs |
| **Art 13** (Transparency) | Capability/limitation docs, user-facing AI disclosures |
| **Art 14** (Human Oversight) | Review/approve functions, human-in-the-loop patterns, override mechanisms |
| **Art 15** (Security) | Test suites, security configs, dependency pinning, credential management |

Each article gets a score from 0-100% with specific evidence (file paths where evidence was found) and gaps (what's missing).

## Model Card Validation

If a model card exists (model_card.md, MODEL_CARD.md), Regula checks it for 5 required sections:
1. Intended use/purpose
2. Limitations and known issues
3. Training data description
4. Performance metrics
5. Ethical considerations

## Exercise

1. Run `python3 scripts/cli.py gap --project /tmp/anthropic-cookbook --article 14` — what's the Article 14 (Human Oversight) score?
2. Create a simple project with NO documentation and scan it — what's the overall score?
3. Add a model_card.md with just "# Model Card" and rescan — does the score change?

## Article 6(3) Exemption Assessment

If you believe your system qualifies for an exemption:

```bash
python3 scripts/cli.py questionnaire --exemption
```

This generates the 4 exemption questions from Article 6(3)(a)-(d) and produces documentation that can support an exemption claim.

---

**Next:** [Module 5: Dependency Security](05-dependency-security.md)
