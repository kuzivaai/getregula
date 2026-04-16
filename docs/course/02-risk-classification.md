# regula-ignore
# Module 2: Risk Classification

## What You'll Learn

- How the EU AI Act classifies AI systems into risk tiers
- What patterns Regula detects for each tier
- How confidence scoring works

## The EU AI Act Risk Pyramid

The EU AI Act (Regulation 2024/1689) classifies AI systems into four tiers. From highest to lowest severity:

**Prohibited (Article 5):** 8 categories of banned AI practices. Regula blocks these with exit code 2.

**High-Risk (Annex III):** 10 categories of sensitive AI domains (employment, credit, education, biometrics, medical, law enforcement, migration, justice, critical infrastructure, safety components). Regula warns with specific Article 9-15 requirements.

**Limited-Risk (Article 50):** 4 categories requiring transparency (chatbots, emotion recognition, biometric categorisation, synthetic content). Users must be informed they're interacting with AI.

**Minimal-Risk:** No specific requirements. Regula logs detection only.

## Important Caveat

Matching an Annex III category does NOT automatically make a system high-risk. Article 6(3) exempts systems that:
- Perform only narrow procedural tasks
- Improve previously completed human activities
- Detect patterns without replacing human assessment
- Perform preparatory tasks for assessments

## Confidence Scoring

Each finding gets a confidence score (0-100). Scores determine finding tiers:
- BLOCK (>= 80): CI should fail
- WARN (50-79): needs human review
- INFO (< 50): shown only with --verbose

Thresholds are configurable in regula-policy.yaml.

## Exercise

```bash
regula classify --input "import sklearn; hiring_decision = model.predict(candidates)"
regula classify --input "import openai; summary = generate_text(prompt)"
regula classify --input "def add(a, b): return a + b"
```

Expected: HIGH-RISK, MINIMAL-RISK, NOT_AI.

---

**Next:** [Module 3: Scanning Real Code](03-scanning-real-code.md)
