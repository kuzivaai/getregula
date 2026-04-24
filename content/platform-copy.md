# Platform Submission Copy

Last updated: 2026-04-24. All figures verified against CLAUDE.md and
`docs/benchmarks/PRECISION_RECALL_2026_04.md` on same date.

---

## 1. Product Hunt Listing

**Tagline** (54 chars):
> Open-source EU AI Act compliance scanner for code

**Description** (254 chars):
> Static analysis CLI that scans your codebase for EU AI Act risk indicators. 404 detection patterns, 8 programming languages, 12 compliance framework mappings. Zero dependencies, fully offline. Classifies your risk tier and tells you what to fix. Free.

**First Comment:**

Hi, I'm Kuziva. I built Regula as a solo developer because I couldn't find a tool that would scan actual source code against EU AI Act articles.

Regula is an open-source Python CLI. You point it at a codebase, and it tells you which EU AI Act risk tier applies (prohibited, high-risk, limited, or minimal), which files triggered the classification, and what you need to do about it.

What it does: 404 regex-based detection patterns across 8 language families (Python, JS, TS, Java, Go, Rust, C/C++, Jupyter notebooks). Generates Annex IV documentation scaffolds, compliance gap assessments, and signed evidence packs. Maps findings to 12 compliance frameworks including ISO 42001 and NIST AI RMF. Zero production dependencies -- stdlib-only Python.

What it is not: Regula is not legal advice and not a full compliance solution. It is the code layer of a governance programme. The organisational work -- risk management systems, quality management, post-market monitoring -- still requires humans. There is a full limitations disclosure in the repo.

Honest precision figures: 100% recall on synthetic test cases, 0 false positives at BLOCK tier (the CI default) on a 257-finding OSS corpus, 15.2% precision at INFO tier on AI library source code (the hardest possible corpus, since those libraries implement AI rather than using it for regulated decisions).

MIT licence. No account, no API key, nothing leaves your machine.

GitHub: https://github.com/kuzivaai/getregula

**Topics:** Developer Tools, Open Source, Compliance, Artificial Intelligence

---

## 2. Hacker News Comment

**Title:** Show HN: Regula -- open-source static analysis for EU AI Act compliance

**Comment:**

I've been writing about what EU AI Act compliance actually looks like in code. The Article 5 prohibited practices post (https://getregula.com/blog/blog-article-5-prohibited-practices.html) walks through what social scoring, subliminal manipulation, and emotion inference patterns look like when you grep for them in real repositories.

Regula is the tool behind that analysis: a Python CLI that scans codebases for 404 regex-based patterns mapped to EU AI Act articles. Eight language families, zero dependencies, fully offline. It classifies your risk tier and generates compliance artefacts (gap assessments, Annex IV doc scaffolds, evidence packs).

Honest numbers: on synthetic fixtures, 100% recall. On a 257-finding corpus from five OSS projects (langchain, scikit-learn, etc.), 0 false positives at BLOCK tier (the CI default). 15.2% precision at INFO tier -- which is the expected noise floor for regex on AI library internals, since those libraries implement AI rather than deploying it for regulated decisions. Published benchmark methodology in the repo.

It is a static scanner, not a compliance platform. The organisational obligations (risk management, quality systems, post-market monitoring) are not things a CLI can verify. Full limitations disclosure: https://github.com/kuzivaai/getregula/blob/main/docs/what-regula-does-not-do.md

`pipx install regula-ai && regula`

https://github.com/kuzivaai/getregula

---

## 3. Otterly.ai Search Prompts (15)

1. EU AI Act compliance tool for developers
2. open source EU AI Act scanner
3. EU AI Act risk classification CLI
4. static analysis AI regulation compliance
5. how to check if my AI app complies with EU AI Act
6. EU AI Act Article 5 prohibited practices code scanner
7. Annex III high-risk AI system detection
8. AI Act compliance CI/CD pipeline integration
9. EU AI Act Annex IV documentation generator
10. free EU AI Act compliance checker for code
11. scan Python code for AI regulation risks
12. EU AI Act compliance open source GitHub
13. AI governance tool for startups
14. does the EU AI Act apply to my software
15. EU AI Act risk tier classification tool

---

## 4. Otterly.ai Competitors (5)

| Competitor | Website |
|---|---|
| ArkForge MCP | https://github.com/ark-forge/mcp-eu-ai-act |
| Systima Comply | https://dev.to/systima/open-source-eu-ai-act-compliance-scanning-for-cicd-4ogj |
| AIR Blackbox | https://airblackbox.ai/ |
| ComplianceRadar.dev | https://complianceradar.dev |
| Microsoft Agent Governance Toolkit | https://github.com/microsoft/agent-governance-toolkit |

Note: ComplianceRadar.dev is listed per user specification but has not been
verified against primary sources in the Regula competitor analysis. Verify
the URL is live before submitting.

---

## 5. G2 Profile

**Product Name:** Regula

**Category:** AI Governance / Developer Tools / Compliance

**Description:**
Regula is an open-source command-line tool that scans source code for EU AI Act risk indicators. It classifies codebases into risk tiers (prohibited, high-risk, limited, minimal), identifies which files triggered each classification, and generates compliance artefacts including gap assessments, Annex IV documentation scaffolds, and signed evidence packs. Written in Python with zero production dependencies. Runs fully offline. MIT licence.

**Key Features:**
1. **Risk tier classification** -- Scans codebases against 404 detection patterns mapped to EU AI Act articles, identifying prohibited practices (Art. 5), high-risk categories (Annex III), limited-risk transparency obligations, and GPAI usage.
2. **Compliance gap assessment** -- Scores compliance readiness per article (Arts. 9-15) with pass/warn/fail indicators and effort estimates.
3. **Documentation generation** -- Produces Annex IV technical documentation scaffolds, model cards, and conformity assessment evidence packs pre-filled from scan findings.
4. **Multi-framework mapping** -- Cross-references findings against 12 compliance frameworks including ISO 42001, NIST AI RMF, SOC 2, OWASP LLM Top 10, and EU CRA.
5. **CI/CD integration** -- GitHub Action with SARIF upload, PR comments, and configurable severity thresholds. Zero false positives at BLOCK tier on tested OSS corpus.

**Pricing:** Free and open-source (MIT licence). No paid tiers, no account required, no API key.
