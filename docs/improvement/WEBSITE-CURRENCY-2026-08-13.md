# Website currency and rendered-experience record

**Measured:** 2026-08-13

**Public origin:** `https://getregula.com`

**Local source:** `/home/mkuziva/getregula/site`

## Verdict

The published website is not up to date with the repository's repaired decision
kernel. This is demonstrated across the English, German, and Brazilian
Portuguese landing pages and on the deployed browser assessment. The local site
source contains the new canonical insufficient-information behavior, but it has
not been published by this work.

This record is not a deployment authorization and no push, release, or
publication was performed.

## Method

The public pages were retrieved through the generic web reader and exercised in
a real Chromium browser. The local site was served from the working tree and
exercised at representative mobile widths. Source inspection alone is not used
as evidence that a deployed page behaves correctly.

The comparison used observable contract markers:

- published test count;
- presence or absence of the canonical `insufficient_information` result;
- presence of legacy tier, percentage, readiness, and effort outputs;
- assessment behavior when every legal-fact answer is `Not sure`;
- mobile navigation state and focus after Escape;
- horizontal reflow at 320 and 375 CSS pixels;
- focus placement after an assessment result is rendered.

## Published landing pages

The live EN, DE, and PT-BR pages all showed the older `2,722`/`2.722` test
count. They did not contain the canonical `Decision:
insufficient_information` example. Their published demonstrations still
contained `Highest risk tier: not_ai` and `Overall score: 6%`.

Those claims are stale relative to the local source, which carries the current
`2,781` collected-test manifest and the repaired decision contract. The live
pages are therefore not merely missing cosmetic changes; they demonstrate the
pre-kernel output semantics that this work was intended to retire.

Measured URLs:

- [English landing page](https://getregula.com/)
- [German landing page](https://getregula.com/locales/de.html)
- [Brazilian Portuguese landing page](https://getregula.com/locales/pt-br.html)

## Published assessment

On the live English assessment, every question was answered `Not sure`. The
deployed browser engine nevertheless rendered a `QUESTIONNAIRE INDICATION`,
`Candidate high-risk indicators`, a `Questionnaire signal score: 91/100`,
readiness percentages, effort estimates, and provisions.

Runtime inspection found neither the local shared `RegulaDecisionAdapters` nor
`RegulaDecisionUI` object. The public assessment was still executing its older
inline decision engine. This is the highest-impact currency defect because an
unknown fact set was converted into decision-like numeric output.

Measured URL: [public assessment](https://getregula.com/assess/).

The browser also recorded Plausible analytics requests rejected by CORS. That
is a secondary telemetry defect; it does not explain the stale decision engine.

## Local assessment behavior

The local EN, DE, and PT-BR assessment pages use the shared generated model,
kernel, adapter, and decision UI. With every answer unresolved they rendered
the locale-equivalent of `More facts required`, emitted no obligation, tier,
score, readiness, or effort conclusion, and retained two unresolved facts.

After rendering, focus now moves to the result status (`role="status"`,
`aria-live="polite"`, `tabindex="-1"`) so keyboard and screen-reader users do
not lose their place when the question card is hidden.

## Local responsive and keyboard findings

An initial 320-by-800 browser pass reproduced two accessibility defects:

1. Escape left the non-modal mobile navigation dialog open and did not restore
   focus to its toggle.
2. Long German statistic and tier labels widened the document beyond the
   viewport.

The local source now explicitly closes the dialog on Escape, synchronizes
`aria-expanded`, and returns focus to the toggle across the six EN, DE, and
PT-BR landing/assessment entry points. Flexible grid and tier children now use
`min-width: 0` and long labels use `overflow-wrap: anywhere`.

Fresh-browser verification at 320 CSS pixels measured a 305-pixel document
content width on all checked pages, with no horizontal overflow. The same
assessment-result check passed at 375 CSS pixels. Escape left the dialog closed,
`aria-expanded="false"`, and focus on the toggle across all six pages.

These are mechanical and rendered-browser checks. Representative human
usability, comprehension, confidence, zoom, assistive-technology, and broader
device testing remain outstanding; the interface must not be called
user-validated on this evidence alone.

## Regulatory currency boundary

The local site reflects the decision-kernel and public-copy work documented in
the repository's primary-law and ledger records. It is not evidence that every
regulatory condition is resolved. Korean delegated numeric thresholds and two
EU model variants remain explicitly unresolved from primary text. Omnibus
timing caveats remain required wherever EU AI Act deadlines are described.

The correct statement is therefore:

- local source: current with the repaired implementation and its stated
  uncertainty boundary;
- deployed public site: stale and unsafe to describe as current;
- regulatory model: materially improved but not complete;
- human usability: not yet validated with representative users.

## Required next publication step

After the implementation commit is fully verified and an owner authorizes
publication:

1. publish the exact verified site artifact rather than rebuilding from an
   unrecorded tree;
2. probe the live EN, DE, and PT-BR landing pages for the expected build/count
   marker;
3. exercise the live assessment with all facts unresolved and require the
   canonical insufficient-information result with no decision-like percentage;
4. repeat the mobile Escape, focus, and reflow checks against the public origin;
5. record the deployed commit and browser evidence in the ledger.

Until all five are demonstrated, source currency and deployment currency must
remain separate claims.
