# Website and accessibility review

Date: 30 August 2026

## Finding

The candidate has a more coherent and honest source-level public experience, but rendered browser and assistive-technology verification is BLOCKED. No WCAG conformance claim is supported.

## Primary journey

Repository evidence supports a primary user who wants to understand Regula's bounded role, inspect an example, keep source local, try an exact reviewed version, and interpret results without mistaking them for legal advice or a compliance verdict.

The candidate now presents this sequence:

1. Declared facts.
2. Code observations.
3. Unknown or contradictory context.
4. Reviewer questions and potentially relevant references.
5. An empty human-decision field.
6. Accountable review outside Regula.

## Source-level improvements observed

- Homepage, README, CLI and examples use the same local source-code observation and review-evidence position.
- Installation calls to action use an exact reviewed `COMMIT_SHA` placeholder. They do not present the stale local tag, moving main branch, PyPI 1.9.0, or a non-existent GitHub release as the candidate.
- The sample report's dominant heading no longer calls scan output a terminal verdict.
- Article 5, Annex III and Article 50 pages describe observed indicators, relevant conditions, unresolved context and human review.
- A recruitment guide and structured metadata no longer say code patterns trigger a legal classification.
- A risk-tier article was recast around code-observable indicators and removed an unrepresentative precision claim from current product copy.
- EN, DE and PT-BR evidence-gap labels describe documentation evidence coverage rather than compliance scoring.
- Consequential structured metadata was included in the semantic guard and claim checks.

## Static verification

REPRODUCED:

- Five regional generated pages match their generators.
- 1,609 internal references have zero dead links.
- 269 fact references across 17 files match canonical counts.
- 108 cross-language links carry language labelling in the locale audit.
- The aggregate `llms-full.txt` file matches its generator.
- The determination guard scans active HTML, JSON-LD, metadata and documentation with zero findings after passing 61 bidirectional controls.
- Share and browser-decision JavaScript contracts pass 255 and 160 assertions respectively.

## Rendered review status

BLOCKED:

- Python could not bind a local HTTP server because socket creation returned `PermissionError: [Errno 1]`.
- The available Chromium executable terminated under the environment's socket and sandbox restrictions.
- The Playwright daemon could not remain available after writable cache paths were supplied.

Consequently, no after screenshot is presented as browser evidence. Desktop, tablet and mobile rendering, keyboard focus order, visible focus, zoom, reflow, contrast, target sizing, reduced motion, screen-reader structure, live-status announcements and print output remain unverified.

## Locale status

The automated semantic comparison and locale-link audit pass within their declared scope. Fluent and qualified review remains required for consequential German and Brazilian Portuguese legal-language choices, particularly evidence-gap headings, Article 50 qualifications, exception wording and calls to human review.

## Decision

- Local source and content review: GO.
- Bounded browser evaluation in a loopback-capable environment: CONDITIONAL GO.
- Public website update: BLOCKED until rendered journeys, accessibility checks, fluent language review and publication controls are completed.
- Accessibility conformance claim: NO-GO.

