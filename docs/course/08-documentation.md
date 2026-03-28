# regula-ignore
# Module 8: Documentation Generation

## What You'll Learn

- Generate Annex IV technical documentation scaffolds
- Generate Quality Management System (QMS) templates
- Understand what these documents require

## Annex IV Documentation

Article 11 requires technical documentation before placing a high-risk AI system on the market. Regula generates a starting scaffold:

```bash
python3 scripts/cli.py docs --project . --output compliance-docs
```

This creates an Annex IV scaffold with:
- System identity and classification
- AI components detected (from code scan)
- Compliance requirements matrix (Articles 9-15)
- Governance contacts (from regula-policy.yaml)
- Placeholder sections for human completion

## QMS Scaffold (Article 17)

Article 17 requires a Quality Management System. Generate it:

```bash
python3 scripts/cli.py docs --project . --qms --output compliance-docs
```

The QMS scaffold covers all Article 17(1) requirements:
- Strategy and compliance objectives
- Design and development procedures
- Testing and validation techniques
- Data management systems
- Risk management system
- Post-market monitoring
- Record-keeping
- Corrective actions
- Communication with authorities
- Human oversight mechanisms
- Transparency provisions

## CycloneDX AI SBOM

Generate a Software Bill of Materials:

```bash
python3 scripts/cli.py sbom --project . --format json --output sbom.json
python3 scripts/cli.py sbom --project . --format text
```

The SBOM lists all AI components with:
- Library type classification (library, framework, ML model)
- AI library tagging via `regula:is-ai-library` property
- Pinning quality per dependency
- PURL (Package URL) per ecosystem

## Exercise

1. Generate Annex IV docs for a project
2. Generate a QMS scaffold
3. Generate an SBOM and examine the components

---

**Next:** [Module 9: Framework Mapping](09-framework-mapping.md)
