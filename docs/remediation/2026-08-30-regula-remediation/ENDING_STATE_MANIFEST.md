# Ending state manifest

Captured: 30 August 2026

## Repository identity

- Repository root: `/home/USER/getregula`
- Branch: `feat/site-ux-redesign-2026-08-27`
- HEAD: `fbed8f3baf81f0c5f0860ebaf56a2845b632b547`
- Staged entries: 0
- Tracked changed files: 150
- Untracked files: 33
- Deleted worktree files: 0
- Tracked diff stat: 150 files, 5,613 insertions, 2,397 deletions

OBSERVED: the worktree remains materially dirty. The starting 65 tracked and
13 untracked entries are preserved. This list is the exact ending status, not
an attribution of every line to this session. For starting provenance, see
`STARTING_STATE_MANIFEST.md`.

## Exact ending status

```text
 M .github/workflows/ci.yaml
 M .github/workflows/triage.yaml
 M .github/workflows/weekly-digest.yaml
 M PERF_REPORT.md
 M README.md
 M SECURITY.md
 M benchmarks/annotation_stats.py
 M benchmarks/compute_kappa.py
 M benchmarks/rater1_blind_subset.json
 M benchmarks/rater2_blind_subset.json
 M content/devto/article-5-prohibited-practices.md
 M content/regulations/_template.html
 M content/regulations/brazil.py
 M content/regulations/colorado.py
 M content/regulations/south-africa.py
 M content/regulations/south-korea.py
 M content/regulations/united-kingdom.py
 M data/documented_transcripts.json
 M data/gap_demo.json
 M data/public_claim_surfaces.json
 M data/qualifier_copy/de.json
 M data/qualifier_copy/en.json
 M data/qualifier_copy/pt-br.json
 M data/site_facts.json
 M data/site_facts.md
 M docs/DEMO.md
 M docs/MODEL_CARD.md
 M docs/PRODUCT_COVERAGE_AND_JOURNEYS.md
 M docs/QUICKSTART.md
 M docs/TRUST.md
 M docs/accessibility/README.md
 M docs/architecture.md
 M docs/cli-reference.md
 M docs/installation.md
 M examples/cv-screening-app/README.md
 M mcp-server.json
 M scripts/api_server.py
 M scripts/assess.py
 M scripts/build_gap_demo.py
 M scripts/build_qualifier.py
 M scripts/cli.py
 M scripts/cli_admin.py
 M scripts/cli_compliance.py
 M scripts/cli_governance.py
 M scripts/compliance_check.py
 M scripts/conform.py
 M scripts/decision_adapters.py
 M scripts/determination_guard.py
 M scripts/evidence_pack.py
 M scripts/exec_summary.py
 M scripts/exempt_check.py
 M scripts/explain.py
 M scripts/generate_documentation.py
 M scripts/mcp_server.py
 M scripts/pdf_export.py
 M scripts/questionnaire.py
 M scripts/remediation.py
 M scripts/report.py
 M scripts/scan_cache.py
 M scripts/telemetry.py
 M scripts/verify_transcripts.py
 M site/404.html
 M site/about.html
 M site/assess/assess-flow.js
 M site/assess/de.html
 M site/assess/decision-adapters.js
 M site/assess/decision-ui.js
 M site/assess/index.html
 M site/assess/pt-br.html
 M site/assets/qualifier.js
 M site/assets/site.css
 M site/assets/site.min.css
 M site/blog/blog-aicdi-governance-gaps.html
 M site/blog/blog-art50-code-of-practice.html
 M site/blog/blog-article-5-prohibited-practices.html
 M site/blog/blog-classify-ai-system.html
 M site/blog/blog-code-scanning-vs-questionnaires.html
 M site/blog/blog-does-ai-act-apply.html
 M site/blog/blog-en-standards-mapping.html
 M site/blog/blog-omnibus-decision-framework.html
 M site/blog/blog-omnibus-delay.html
 M site/blog/blog-omnibus-trilogue-failed.html
 M site/blog/blog-risk-tiers-in-code.html
 M site/blog/blog-scanning-10-ai-apps.html
 M site/blog/blog-scanning-5-frameworks.html
 M site/blog/blog-startups-ignoring-ai-act.html
 M site/blog/blog-static-analysis-ai-compliance.html
 M site/blog/writing.html
 M site/coverage-de.html
 M site/coverage-pt-br.html
 M site/coverage.html
 M site/guides/article-14-human-oversight.html
 M site/guides/article-5-prohibited-practices.html
 M site/guides/article-50-transparency.html
 M site/guides/article-9-risk-management.html
 M site/guides/eu-ai-act-healthcare.html
 M site/guides/eu-ai-act-javascript.html
 M site/guides/eu-ai-act-python.html
 M site/guides/eu-ai-act-recruitment-hiring.html
 M site/guides/index.html
 M site/index.html
 M site/llms-full.txt
 M site/llms.txt
 M site/locales/de.html
 M site/locales/pt-br.html
 M site/pricing.html
 M site/privacy-de.html
 M site/privacy-pt-br.html
 M site/privacy.html
 M site/product-de.html
 M site/product-pt-br.html
 M site/product.html
 M site/regions/brazil-ai-regulation.html
 M site/regions/colorado-ai-regulation.html
 M site/regions/regulations.html
 M site/regions/south-africa-ai-policy.html
 M site/regions/south-korea-ai-regulation.html
 M site/regions/uae.html
 M site/regions/uk-ai-regulation.html
 M site/sample-report.html
 M site/terms-de.html
 M site/terms-pt-br.html
 M site/terms.html
 M tests/test_annotation_stats.py
 M tests/test_api_server.py
 M tests/test_bare_scan_decision.py
 M tests/test_classification.py
 M tests/test_cli_integration.py
 M tests/test_compliance_check.py
 M tests/test_conform.py
 M tests/test_decision_conformance.py
 M tests/test_determination_guard.py
 M tests/test_evidence_pack_unit.py
 M tests/test_exec_summary.py
 M tests/test_fact_loop.py
 M tests/test_first_run.py
 M tests/test_gap_demo.py
 M tests/test_installed_artefact.py
 M tests/test_lifecycle_visibility.py
 M tests/test_locale_link_language.py
 M tests/test_mcp_server.py
 M tests/test_public_claim_integrity.py
 M tests/test_questionnaire_scoring.js
 M tests/test_release_gate.py
 M tests/test_scan_cache.py
 M tests/test_scan_security.py
 M tests/test_security_hardening.py
 M tests/test_site_critical_css.py
 M tests/test_telemetry.py
 M tests/test_tracked_inputs.py
?? AGENTS.proposed.md
?? benchmarks/rating_packet.py
?? docs/UX_ARCHETYPES_AND_JOURNEYS_2026-08-27.md
?? docs/learnings.md
?? docs/remediation/2026-08-30-regula-remediation/DECISION_LOG.md
?? docs/remediation/2026-08-30-regula-remediation/ENDING_STATE_MANIFEST.md
?? docs/remediation/2026-08-30-regula-remediation/FINDING_DISPOSITION_REGISTER.csv
?? docs/remediation/2026-08-30-regula-remediation/FINDING_DISPOSITION_REGISTER.md
?? docs/remediation/2026-08-30-regula-remediation/IMPLEMENTATION_LEARNING_LOG.md
?? docs/remediation/2026-08-30-regula-remediation/IMPLEMENTATION_LOG.md
?? docs/remediation/2026-08-30-regula-remediation/NEXT_SESSION_PROMPT.md
?? docs/remediation/2026-08-30-regula-remediation/REGULA_REMEDIATION_REPORT_2026-08-30.md
?? docs/remediation/2026-08-30-regula-remediation/REMAINING_EXTERNAL_ASSURANCE.md
?? docs/remediation/2026-08-30-regula-remediation/REMEDIATION_CHARTER.md
?? docs/remediation/2026-08-30-regula-remediation/REMEDIATION_EXECUTIVE_BRIEF_2026-08-30.md
?? docs/remediation/2026-08-30-regula-remediation/REPRESENTATIVE_EVALUATION_ENTRY_GATE.md
?? docs/remediation/2026-08-30-regula-remediation/STARTING_STATE_MANIFEST.md
?? docs/remediation/2026-08-30-regula-remediation/VERIFICATION_LOG.md
?? docs/remediation/2026-08-30-regula-remediation/WEBSITE_BEFORE_AFTER_REVIEW.md
?? marketing/blog-what-a-scanner-cannot-see.md
?? output/playwright/article50-scan-error-mobile.png
?? output/playwright/deploy-preview-55-mobile.png
?? output/playwright/dossier-continuation-2026-08-19/aicdi-desktop.png
?? output/playwright/dossier-continuation-2026-08-19/aicdi-mobile.png
?? output/playwright/dossier-continuation-2026-08-19/home-desktop.png
?? output/playwright/founder-home-audit/founder-local-desktop.png
?? output/playwright/live-desktop-start-2026-08-27.png
?? output/playwright/live-desktop-top-2026-08-27.png
?? output/playwright/live-mobile-result-2026-08-27.png
?? scripts/evidence_review.py
?? scripts/weekly_digest.py
?? tests/test_product_boundary_contract.py
?? tests/test_weekly_digest.py
```

## Exact tracked diff stat

```text
 .github/workflows/ci.yaml                          |  25 +-
 .github/workflows/triage.yaml                      |   2 +-
 .github/workflows/weekly-digest.yaml               | 106 +----
 PERF_REPORT.md                                     |   2 +-
 README.md                                          |  23 +-
 SECURITY.md                                        |   2 +-
 benchmarks/annotation_stats.py                     |  43 +-
 benchmarks/compute_kappa.py                        |  29 +-
 benchmarks/rater1_blind_subset.json                |   4 +-
 benchmarks/rater2_blind_subset.json                |   4 +-
 content/devto/article-5-prohibited-practices.md    |  42 +-
 content/regulations/_template.html                 |  14 +-
 content/regulations/brazil.py                      |   2 +-
 content/regulations/colorado.py                    |   2 +-
 content/regulations/south-africa.py                |   2 +-
 content/regulations/south-korea.py                 |   2 +-
 content/regulations/united-kingdom.py              |   2 +-
 data/documented_transcripts.json                   |  12 +-
 data/gap_demo.json                                 |  10 +-
 data/public_claim_surfaces.json                    |  32 +-
 data/qualifier_copy/de.json                        |  68 ++-
 data/qualifier_copy/en.json                        | 124 ++++-
 data/qualifier_copy/pt-br.json                     |  68 ++-
 data/site_facts.json                               |  26 +-
 data/site_facts.md                                 |   4 +-
 docs/DEMO.md                                       |   2 +-
 docs/MODEL_CARD.md                                 |   2 +-
 docs/PRODUCT_COVERAGE_AND_JOURNEYS.md              |   4 +-
 docs/QUICKSTART.md                                 |   4 +-
 docs/TRUST.md                                      |  18 +-
 docs/accessibility/README.md                       | 100 +++-
 docs/architecture.md                               |   7 +-
 docs/cli-reference.md                              |   2 +-
 docs/installation.md                               |  18 +-
 examples/cv-screening-app/README.md                |  20 +-
 mcp-server.json                                    |   8 +-
 scripts/api_server.py                              |  43 +-
 scripts/assess.py                                  | 113 ++++-
 scripts/build_gap_demo.py                          |  10 +-
 scripts/build_qualifier.py                         | 111 ++++-
 scripts/cli.py                                     |   8 +
 scripts/cli_admin.py                               |   4 +-
 scripts/cli_compliance.py                          |  56 +--
 scripts/cli_governance.py                          |  28 +-
 scripts/compliance_check.py                        |  34 +-
 scripts/conform.py                                 |  96 ++--
 scripts/decision_adapters.py                       | 194 ++++++--
 scripts/determination_guard.py                     |  98 +++-
 scripts/evidence_pack.py                           |  20 +-
 scripts/exec_summary.py                            |  21 +-
 scripts/exempt_check.py                            | 143 ++++--
 scripts/explain.py                                 |  89 +---
 scripts/generate_documentation.py                  |  61 +--
 scripts/mcp_server.py                              | 232 ++++++++--
 scripts/pdf_export.py                              |  57 +--
 scripts/questionnaire.py                           |  29 +-
 scripts/remediation.py                             |  22 +-
 scripts/report.py                                  | 266 +++++++----
 scripts/scan_cache.py                              | 229 +++++++++-
 scripts/telemetry.py                               |  63 ++-
 scripts/verify_transcripts.py                      |   6 +-
 site/404.html                                      |  14 +-
 site/about.html                                    |  10 +-
 site/assess/assess-flow.js                         |  57 ++-
 site/assess/de.html                                | 162 ++++---
 site/assess/decision-adapters.js                   | 267 ++++++++++-
 site/assess/decision-ui.js                         | 341 ++++++--------
 site/assess/index.html                             | 162 ++++---
 site/assess/pt-br.html                             | 162 ++++---
 site/assets/qualifier.js                           | 128 +++++-
 site/assets/site.css                               | 502 +++++++++++++++++----
 site/assets/site.min.css                           |   2 +-
 site/blog/blog-aicdi-governance-gaps.html          |  33 +-
 site/blog/blog-art50-code-of-practice.html         |  24 +-
 site/blog/blog-article-5-prohibited-practices.html |  24 +-
 site/blog/blog-classify-ai-system.html             |  16 +-
 .../blog/blog-code-scanning-vs-questionnaires.html |  16 +-
 site/blog/blog-does-ai-act-apply.html              |  32 +-
 site/blog/blog-en-standards-mapping.html           |  16 +-
 site/blog/blog-omnibus-decision-framework.html     |  22 +-
 site/blog/blog-omnibus-delay.html                  |  22 +-
 site/blog/blog-omnibus-trilogue-failed.html        |  20 +-
 site/blog/blog-risk-tiers-in-code.html             |  50 +-
 site/blog/blog-scanning-10-ai-apps.html            |  22 +-
 site/blog/blog-scanning-5-frameworks.html          |  18 +-
 site/blog/blog-startups-ignoring-ai-act.html       |  18 +-
 site/blog/blog-static-analysis-ai-compliance.html  |  14 +-
 site/blog/writing.html                             |  14 +-
 site/coverage-de.html                              |   9 +-
 site/coverage-pt-br.html                           |   9 +-
 site/coverage.html                                 |   9 +-
 site/guides/article-14-human-oversight.html        |  12 +-
 site/guides/article-5-prohibited-practices.html    |  12 +-
 site/guides/article-50-transparency.html           |  12 +-
 site/guides/article-9-risk-management.html         |  12 +-
 site/guides/eu-ai-act-healthcare.html              |  14 +-
 site/guides/eu-ai-act-javascript.html              |  20 +-
 site/guides/eu-ai-act-python.html                  |  20 +-
 site/guides/eu-ai-act-recruitment-hiring.html      |  30 +-
 site/guides/index.html                             |  60 +--
 site/index.html                                    | 192 +++++---
 site/llms-full.txt                                 |  45 +-
 site/llms.txt                                      |   2 +-
 site/locales/de.html                               | 190 ++++++--
 site/locales/pt-br.html                            | 220 ++++++---
 site/pricing.html                                  |  34 +-
 site/privacy-de.html                               |  10 +-
 site/privacy-pt-br.html                            |  10 +-
 site/privacy.html                                  |  10 +-
 site/product-de.html                               |  54 +--
 site/product-pt-br.html                            | 106 ++---
 site/product.html                                  |  52 +--
 site/regions/brazil-ai-regulation.html             |  16 +-
 site/regions/colorado-ai-regulation.html           |  16 +-
 site/regions/regulations.html                      |  14 +-
 site/regions/south-africa-ai-policy.html           |  16 +-
 site/regions/south-korea-ai-regulation.html        |  16 +-
 site/regions/uae.html                              |  98 ++--
 site/regions/uk-ai-regulation.html                 |  16 +-
 site/sample-report.html                            |  38 +-
 site/terms-de.html                                 |  10 +-
 site/terms-pt-br.html                              |  10 +-
 site/terms.html                                    |  10 +-
 tests/test_annotation_stats.py                     |  54 +++
 tests/test_api_server.py                           |  60 ++-
 tests/test_bare_scan_decision.py                   |   5 +-
 tests/test_classification.py                       | 144 ++++--
 tests/test_cli_integration.py                      |  41 +-
 tests/test_compliance_check.py                     |  18 +-
 tests/test_conform.py                              | 109 +++--
 tests/test_decision_conformance.py                 |  16 +-
 tests/test_determination_guard.py                  |  11 +
 tests/test_evidence_pack_unit.py                   |  34 +-
 tests/test_exec_summary.py                         |  14 +-
 tests/test_fact_loop.py                            |  14 +-
 tests/test_first_run.py                            |   8 +-
 tests/test_gap_demo.py                             |   2 +-
 tests/test_installed_artefact.py                   |   2 +-
 tests/test_lifecycle_visibility.py                 |  15 +-
 tests/test_locale_link_language.py                 |  21 +
 tests/test_mcp_server.py                           | 214 ++++++++-
 tests/test_public_claim_integrity.py               |  27 +-
 tests/test_questionnaire_scoring.js                | 241 ++++++++--
 tests/test_release_gate.py                         |  12 +
 tests/test_scan_cache.py                           | 404 ++++++++++++++++-
 tests/test_scan_security.py                        |   5 +-
 tests/test_security_hardening.py                   |   8 +-
 tests/test_site_critical_css.py                    |  12 +-
 tests/test_telemetry.py                            |  64 +++
 tests/test_tracked_inputs.py                       |  15 +-
 150 files changed, 5613 insertions(+), 2397 deletions(-)
```
