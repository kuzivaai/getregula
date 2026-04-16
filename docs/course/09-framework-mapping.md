# regula-ignore
# Module 9: Framework Mapping

## What You'll Learn

- Map findings to 10 compliance frameworks simultaneously
- Understand the crosswalk between EU AI Act and other standards

## Supported Frameworks

| Framework | What It Covers |
|-----------|---------------|
| EU AI Act | Articles 5, 9-15, 50 — the primary regulatory framework |
| NIST AI RMF 1.0 | GOVERN, MAP, MEASURE, MANAGE functions |
| ISO 42001:2023 | AI management system controls (Annex A) |
| NIST CSF 2.0 | GOVERN, IDENTIFY, PROTECT, DETECT, RESPOND, RECOVER |
| SOC 2 | Trust Services Criteria |
| ISO 27001:2022 | Information security controls (Annex A) |
| OWASP LLM Top 10 | 10 LLM-specific vulnerability categories |
| MITRE ATLAS | Adversarial threat techniques for AI systems |
| LGPD | Brazil's General Data Protection Law |
| Marco Legal da IA | Brazil's AI legal framework |

## Using Framework Mapping

```bash
# All frameworks
regula check . --framework all

# Specific framework
regula check . --framework nist-ai-rmf
regula check . --framework owasp-llm-top10
regula check . --framework mitre-atlas
```

## How the Crosswalk Works

The mapping data lives in `references/framework_crosswalk.yaml`. For each EU AI Act article (9-15), it maps to specific controls/subcategories in each framework.

Example for Article 14 (Human Oversight):
- **NIST AI RMF:** GOVERN 1.3, MANAGE 2.2
- **ISO 42001:** A.6.3 (Human oversight of AI systems)
- **NIST CSF 2.0:** GV.RR-01, RS.MA-01
- **SOC 2:** CC1.1, CC1.3
- **ISO 27001:** 5.3, A.5.8
- **OWASP LLM:** LLM05 (Improper Output Handling), LLM06 (Excessive Agency)

## Exercise

1. Run a check with `--framework all` and examine the output
2. Open `references/framework_crosswalk.yaml` and read the Article 15 mapping

---

**Next:** [Module 10: Building Your Own Patterns](10-custom-patterns.md)
