# Regula in the AI Governance Landscape

This page maps Regula's actual capabilities against the gaps documented in the [UNESCO + Thomson Reuters Foundation AI Company Data Initiative (AICDI) 2025 Global Insights Report](https://www.unesco.org/en/articles/pioneering-report-thomson-reuters-foundation-and-unesco-sheds-light-way-3000-companies-approach-ai), published April 2026. The UNESCO press release describes the dataset as "almost 3,000 companies" / "approximately 3,000 companies". Data was collected between July and November 2025.

The point of this page is honesty. Regula is a static code scanner. It addresses some of the gaps the report measures. It does not address others — and we are explicit about which is which. The previous version of this section (in the README) listed competitor names without primary sources and was removed in commit `e013b9a`. This page replaces it with a per-gap mapping anchored to a published external study.

## Honest scoring legend

- **Yes** — Regula directly addresses this gap with shipped functionality. File and command listed.
- **Partial** — Regula addresses one component of a multi-part gap. The rest needs human or organisational work.
- **No** — Regula does not address this gap. It is not in scope for a static code scanner. We document it here so it is clear we are not selling functionality we do not have.

## Mapping

Percentages below are quoted **only** where they appear verbatim in the UNESCO press release or the Policy Edge / Eco-Business / Digital Watch / Economy Middle East coverage. Figures not published in the press (e.g. model-registry %, complaints-mechanism %, board-oversight %) are shown as `—`.

The full AICDI report PDF is referenced at [`unesdoc.unesco.org/ark:/48223/pf0000397817_eng`](https://unesdoc.unesco.org/ark:/48223/pf0000397817_eng) (title: *Responsible AI in practice: 2025 global insights from the AI Company Data Initiative*, powered by Thomson Reuters Foundation and grounded in the UNESCO Recommendation on the Ethics of AI). The `unesdoc.unesco.org` portal is gated behind Cloudflare Bot Protection and cannot be retrieved programmatically — it must be downloaded in a browser. When that is done, the `—` rows in the table below can be restored against page references.

| AICDI gap | % of companies | Regula coverage | How |
|---|---:|---|---|
| Has an AI strategy | 44% | **No** | Regula is a code scanner, not a strategy framework. |
| Publicly commits to a named governance framework | 10% | **Indirect** | Regula maps findings to 13 frameworks (EU AI Act, ISO 42001, NIST AI RMF, NIST AI 600-1 GenAI Profile, NIST CSF 2.0, SOC 2 TSC, ISO 27001, OWASP LLM Top 10, MITRE ATLAS, CRA, ICO/DSIT, LGPD, Marco Legal IA). Adopting Regula doesn't make a company "publicly committed" — that's a board statement. But it operationalises adherence in code. See `references/framework_crosswalk.yaml`. |
| Board / committee-level AI oversight | — | **No** | Governance structure, not a code property. |
| Dedicated AI governance team | — | **No** | Org structure. |
| Has policy ensuring human oversight of AI systems | 12% | **Partial** | `regula oversight` does cross-file Article 14 detection — traces AI model outputs through the codebase and flags whether a human-review function gates the output. This is *verification* of oversight in code. The *policy* itself is a written document. See `scripts/cross_file_flow.py`. |
| Has a formal AI model registry | — | **Yes (narrow)** | `regula sbom --ai-bom` produces a CycloneDX 1.7 ML-BOM (`scripts/sbom.py`) with: detected ML model files, AI dependencies, GPAI tier annotations, and (since April 2026) GPAI Code of Practice signatory status for each detected vendor. This is a **technical** registry. Separately, `regula register` (added 2026-04-07, see `scripts/register.py`) generates Annex VIII Section A/B/C registration packets locally with auto-fill from existing scan artifacts and an explicit gap list — the EU database (Art. 71) is not user-writable, so a local artifact + dual-deadline annotation (2026-08-02 / 2027-12-02 Omnibus pending) is the credible CLI-side workflow. |
| Has worker protection policies for AI | — | **No** | Organisational policy, not a code property. |
| Offers AI training to employees | 30% offer any; 12% offer structured coverage | **No** | Training program, not a code scanner. |
| Evaluates environmental impact | 11% | **No** | Regula has zero environmental scanning. Not in scope. The NIST AI 600-1 GenAI Profile flags this as a known cross-framework gap — see `references/framework_crosswalk.yaml`. |
| Evaluates human rights impact | 7% | **Partial (narrow)** | `regula bias` checks for protected-class features in ML training data per Article 10(5) of the EU AI Act. That is one component of an HRIA. The wider HRIA (worker impact, downstream uses, vulnerable groups) is not in code. |
| Conducts ethical impact assessments | — | **No** | Not in scope. |
| Has a complaints mechanism for AI issues | — | **No** | Operational mechanism, not a code property. |
| Conducts AI privacy / DPIA | fewer than 1 in 5 | **Partial** | `regula gap` scores DPIA-adjacent evidence under Article 10 data governance. |
| Has policies on data-sharing with 3rd-party AI vendors | ~1 in 5 | **No** | Org policy. |
| Has checked training data quality | ~25% have any evidence | **No** | Regula detects training data pipelines but does not audit their quality. |

## What Regula adds beyond the AICDI gaps

Things Regula does that the AICDI report does not specifically measure but that are objectively useful for a developer-facing compliance baseline:

- **Article 5 prohibited practice detection** — pattern-based detection of subliminal manipulation, social scoring, criminal-prediction-by-profiling, untargeted facial scraping, and 4 other Article 5 categories. Fires regardless of whether the file imports an AI library (fixed in commit `999ffac`). Synthetic-fixture precision and recall are 100/100 against a hand-crafted ground-truth corpus.
- **EU AI Act high-risk classification** — pattern-based classification across all 8 Annex III areas (Regulation (EU) 2024/1689 Annex III points 1–8: biometrics, critical infrastructure, education, employment, essential services, law enforcement, migration, justice + democratic processes) plus 2 Annex I categories referenced by Article 6(1) (medical devices, machinery safety components) — 10 high-risk pattern categories in total.
- **Articles 9–15 gap assessment** — `regula gap` produces per-article 0–100 scores against the EU AI Act risk-management lifecycle.
- **Annex IV conformity evidence pack** — `regula conform` generates structured per-article evidence packs with SHA-256 manifest, ready for an audit.
- **Annex VIII registration packet** — `regula register` builds Sections A/B/C packets, branches by provider/deployer role and Annex III area (incl. Art. 49(4) non-public for biometrics/law enforcement/migration and Art. 49(5) national-level routing for critical infrastructure), auto-fills from existing scan data, lists gaps, and dual-annotates the 2026-08-02 vs Omnibus-proposed 2027-12-02 deadlines. Three-source-verified schema in `references/annex_viii_sections.json`.
- **Cross-file Article 14 oversight detection** — `regula oversight` traces AI model outputs through call chains to detect missing human-in-the-loop gates.
- **AI Bill of Materials (CycloneDX 1.7 ML-BOM)** — see model registry row above.
- **Audit trail with hash chain** — `regula audit` maintains a tamper-evident log of compliance scans.
- **Pre-commit hook for prohibited patterns** — `hooks/pre_tool_use.py` blocks Bash/Write/Edit operations that touch Article 5 prohibited patterns. Prevention layer that complements detection.
- **MCP server** — `regula mcp-server` exposes `regula_check`, `regula_classify`, and `regula_gap` as tools an AI coding assistant can call directly. Documented for Claude Code, Cursor, and Windsurf.

## Honest baselines (measured, reproducible)

- **OSS benchmark precision**: 15.2% on 257 hand-labelled findings sampled from 5 OSS projects (instructor, pydantic-ai, langchain, scikit-learn, openai-python). Re-validated against current patterns 2026-04-07: 252 of 257 labels still match (98%). See `benchmarks/labels.json` and reproduce with `python3 benchmarks/label.py score`.
- **Synthetic benchmark precision and recall**: 100% / 100% on 13 hand-crafted fixtures covering 5 prohibited (Article 5 categories a–e), 5 high-risk (Annex III categories), and 3 negative cases. Reproduce with `python3 benchmarks/synthetic/run.py`.
- **Scan time**: see [`benchmarks/results/SUMMARY.json`](../benchmarks/results/SUMMARY.json) for current numbers across all five OSS projects.

## Things we are explicit about NOT building

These come up when people ask "can you make Regula do X?" The answer is no, and here is why each is out of scope rather than a future feature:

- **AI governance maturity scoring from a code scan.** The AICDI report measures organisational signals that are not in code (board oversight, training programmes, complaints mechanisms). Pretending to score those from static analysis would be inflation, not measurement.
- **Environmental impact estimator.** Out of scope. Would require runtime telemetry and electricity-grid data we don't have.
- **AI ethics rating.** Not measurable from static code. Behavioural tools (e.g. red-teaming) are different products.
- **Policy generator that writes governance policies for companies.** Anyone using such a tool to satisfy a regulator would fail an audit. Form-letter output is worse than no policy.
- **Public commitment to a framework.** That's a board statement, not a code property. Regula can show the *technical* implementation matches a framework's expectations; it cannot make the public commitment for you.
- **Vendor SaaS audit.** Regula detects that your code calls a vendor and surfaces the vendor's published GPAI Code of Practice signing status. It does not audit the vendor's actual practices.

## Sources

- [UNESCO press release on the AICDI 2025 report](https://www.unesco.org/en/articles/pioneering-report-thomson-reuters-foundation-and-unesco-sheds-light-way-3000-companies-approach-ai)
- [Digital Watch Observatory coverage of the AICDI report](https://dig.watch/updates/unesco-responsible-ai-practice-report)
- [The Policy Edge: AICDI accountability gap analysis](https://www.policyedge.in/p/the-accountability-gap-unesco-findings-reveal-lag-in-corporate-ai-governance)
- [EU AI Act Annex VIII (registration)](https://artificialintelligenceact.eu/annex/8/)
- [EU AI Act Article 71 (EU database for high-risk AI)](https://artificialintelligenceact.eu/article/71/)
- [General-Purpose AI Code of Practice (European Commission)](https://digital-strategy.ec.europa.eu/en/policies/contents-code-gpai)
- [Nemko: OpenAI and Anthropic sign EU AI Code (July 2025)](https://digital.nemko.com/news/openai-anthropic-signs-eu-ai-code)
- [NIST AI 600-1: AI RMF Generative AI Profile (July 2024)](https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence)
- [CycloneDX ML-BOM v1.7](https://cyclonedx.org/capabilities/mlbom/)
- [OneTrust: Digital Omnibus delay analysis](https://www.onetrust.com/blog/eu-digital-omnibus-proposes-delay-of-ai-compliance-deadlines/)

## Last updated

2026-04-07. Re-verify gap percentages against the AICDI report's published methodology before each Regula release.
