# Starting state manifest

Captured: 30 August 2026

## Repository identity

- Repository root: `/home/USER/getregula`
- Branch: `feat/site-ux-redesign-2026-08-27`
- HEAD: `fbed8f3baf81f0c5f0860ebaf56a2845b632b547`
- Fetch remote: `https://github.com/kuzivaai/getregula.git`
- Push remote: `no-push://history-reset-required`
- Staged entries: 0
- Tracked changed files: 65
- Untracked files: 13
- Deleted worktree files: 0
- Tracked diff stat: 65 files, 1,806 insertions, 778 deletions
- Audit and assurance directory:
  `docs/audit/project-intelligence-2026-08-30/`

OBSERVED: the worktree is materially dirty. Provenance for every entry below
is unknown unless a later evidence record establishes it.

## Pre-existing tracked changes

| Path | Classification |
|---|---|
| `data/qualifier_copy/de.json` | website redesign |
| `data/qualifier_copy/en.json` | website redesign |
| `data/qualifier_copy/pt-br.json` | website redesign |
| `docs/PRODUCT_COVERAGE_AND_JOURNEYS.md` | documentation |
| `docs/accessibility/README.md` | documentation |
| `scripts/build_qualifier.py` | website generator |
| `site/404.html` | website redesign |
| `site/about.html` | website redesign |
| `site/assess/de.html` | website redesign |
| `site/assess/index.html` | website redesign |
| `site/assess/pt-br.html` | website redesign |
| `site/assets/qualifier.js` | generated website output |
| `site/assets/site.css` | website redesign |
| `site/assets/site.min.css` | generated website output |
| `site/blog/blog-aicdi-governance-gaps.html` | website redesign |
| `site/blog/blog-art50-code-of-practice.html` | website redesign |
| `site/blog/blog-article-5-prohibited-practices.html` | website redesign |
| `site/blog/blog-classify-ai-system.html` | website redesign |
| `site/blog/blog-code-scanning-vs-questionnaires.html` | website redesign |
| `site/blog/blog-does-ai-act-apply.html` | website redesign |
| `site/blog/blog-en-standards-mapping.html` | website redesign |
| `site/blog/blog-omnibus-decision-framework.html` | website redesign |
| `site/blog/blog-omnibus-delay.html` | website redesign |
| `site/blog/blog-omnibus-trilogue-failed.html` | website redesign |
| `site/blog/blog-risk-tiers-in-code.html` | website redesign |
| `site/blog/blog-scanning-10-ai-apps.html` | website redesign |
| `site/blog/blog-scanning-5-frameworks.html` | website redesign |
| `site/blog/blog-startups-ignoring-ai-act.html` | website redesign |
| `site/blog/blog-static-analysis-ai-compliance.html` | website redesign |
| `site/blog/writing.html` | website redesign |
| `site/coverage-de.html` | website redesign |
| `site/coverage-pt-br.html` | website redesign |
| `site/coverage.html` | website redesign |
| `site/guides/article-14-human-oversight.html` | website redesign |
| `site/guides/article-5-prohibited-practices.html` | website redesign |
| `site/guides/article-50-transparency.html` | website redesign |
| `site/guides/article-9-risk-management.html` | website redesign |
| `site/guides/eu-ai-act-healthcare.html` | website redesign |
| `site/guides/eu-ai-act-javascript.html` | website redesign |
| `site/guides/eu-ai-act-python.html` | website redesign |
| `site/guides/eu-ai-act-recruitment-hiring.html` | website redesign |
| `site/guides/index.html` | website redesign |
| `site/index.html` | website redesign |
| `site/locales/de.html` | website redesign |
| `site/locales/pt-br.html` | website redesign |
| `site/pricing.html` | website redesign |
| `site/privacy-de.html` | website redesign |
| `site/privacy-pt-br.html` | website redesign |
| `site/privacy.html` | website redesign |
| `site/product-de.html` | website redesign |
| `site/product-pt-br.html` | website redesign |
| `site/product.html` | website redesign |
| `site/regions/brazil-ai-regulation.html` | generated website output |
| `site/regions/colorado-ai-regulation.html` | generated website output |
| `site/regions/regulations.html` | generated website output |
| `site/regions/south-africa-ai-policy.html` | generated website output |
| `site/regions/south-korea-ai-regulation.html` | generated website output |
| `site/regions/uae.html` | website redesign |
| `site/regions/uk-ai-regulation.html` | generated website output |
| `site/sample-report.html` | website redesign |
| `site/terms-de.html` | website redesign |
| `site/terms-pt-br.html` | website redesign |
| `site/terms.html` | website redesign |
| `tests/test_public_claim_integrity.py` | test |
| `tests/test_site_critical_css.py` | test |

## Pre-existing untracked files

| Path | Classification |
|---|---|
| `AGENTS.proposed.md` | instruction proposal, do not edit without approval |
| `docs/UX_ARCHETYPES_AND_JOURNEYS_2026-08-27.md` | documentation |
| `docs/learnings.md` | documentation |
| `marketing/blog-what-a-scanner-cannot-see.md` | public content draft |
| `output/playwright/article50-scan-error-mobile.png` | audit artefact |
| `output/playwright/deploy-preview-55-mobile.png` | audit artefact |
| `output/playwright/dossier-continuation-2026-08-19/aicdi-desktop.png` | audit artefact |
| `output/playwright/dossier-continuation-2026-08-19/aicdi-mobile.png` | audit artefact |
| `output/playwright/dossier-continuation-2026-08-19/home-desktop.png` | audit artefact |
| `output/playwright/founder-home-audit/founder-local-desktop.png` | audit artefact |
| `output/playwright/live-desktop-start-2026-08-27.png` | audit artefact |
| `output/playwright/live-desktop-top-2026-08-27.png` | audit artefact |
| `output/playwright/live-mobile-result-2026-08-27.png` | audit artefact |

## Relevant ignored state

Ignored state includes agent configuration directories, a private handover,
local deployment state, browser logs, test and lint caches, a virtual
environment, generated root governance and model-card files, generated
conformity and evidence-pack directories, private planning directories, build
outputs, package metadata and Python bytecode. These paths are excluded from
product edits. Private or credential-bearing ignored files will not be read.

The ignored audit directory is the source dossier. Its contents are treated as
ASSERTED until reproduced or directly matched to current implementation.

## Provenance rule for later diffs

The final report will separate the 65 tracked and 13 untracked entries above
from remediation changes. A file already listed here remains pre-existing even
if the remediation adds a compatible incremental change to the same file.
