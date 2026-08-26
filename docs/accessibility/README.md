# Accessibility and human-centred quality

**Target:** WCAG 2.2 Level AA<br>
**Conformance status:** not claimed<br>
**Last completed automated audit:** 26 August 2026, 54 canonical pages at
desktop and mobile widths (108 runs), zero axe violations<br>
**Incomplete automated checks:** 71 across 71 runs; these require manual review
and are not counted as passes<br>
**Audit tools:** Playwright 1.62.1 and axe-core 4.12.1

The audit covers 1400×900 and 390×844. Testing both sides of the site's 900px
breakpoint matters: horizontally scrolling content and collapsed navigation
can create keyboard failures that do not exist at desktop width. Code blocks
that may scroll are keyboard focusable without adding unnecessary landmarks.

The current run returned **71 `incomplete` results across 71 runs**: all 54
mobile runs and 17 desktop runs. Axe reports `incomplete` when it cannot decide
and a person must review the criterion. Those results are not passes, and
automated checks reach only part of WCAG. Zero violations means zero violations
of the rules this tool can evaluate; it is not a conformance claim.

Regula treats accessibility and usability as acceptance criteria. Automated
results are evidence about the rules a tool can evaluate. They are not proof
that the website conforms to WCAG or that people can complete their tasks.

## Standards baseline

- [ISO 9241-11:2018](https://www.iso.org/standard/63500.html) supplies the
  usability concepts and defines usability as an outcome of use. ISO states
  that this part does not prescribe a design or evaluation process.
- [ISO 9241-210:2019](https://www.iso.org/standard/77520.html) supplies
  requirements and recommendations for human-centred design throughout the
  life cycle. ISO confirms that Annex B contains a conformance checklist.
  Regula has not completed that proprietary checklist and does not claim ISO
  9241-210 conformance.
- [WCAG 2.2](https://www.w3.org/TR/WCAG22/) Level AA is the implementation and
  evaluation target. W3C published WCAG 2.2 as a Recommendation on 5 October
  2023. It adds nine success criteria to WCAG 2.1 and is designed to be
  backwards compatible.
- WCAG 2.2 was approved as
  [ISO/IEC 40500:2025](https://www.w3.org/press-releases/2025/wcag22-iso-pas/)
  on 21 October 2025.
- WCAG 3.0 remains a draft and is not a conformance target. The project will
  track it as research but will build and test against WCAG 2.2 AA until W3C
  publishes a stable Recommendation.

This is a voluntary engineering target. This document does not assert that a
specific accessibility law applies to Regula. UK government guidance currently
uses WCAG 2.2 AA for public-sector websites, while W3C notes that EN 301 549
currently uses WCAG 2.1 and is expected to move to WCAG 2.2.

## Performance baseline

The performance targets are the three current Core Web Vitals, evaluated at
the 75th percentile of real visits when sufficient field data exists:

| Metric | Good | Poor |
|---|---:|---:|
| Largest Contentful Paint (LCP) | at most 2.5 s | over 4.0 s |
| [Interaction to Next Paint (INP)](https://web.dev/articles/inp) | at most 200 ms | over 500 ms |
| Cumulative Layout Shift (CLS) | at most 0.1 | over 0.25 |

Source: [Google's Core Web Vitals threshold methodology](https://web.dev/articles/defining-core-web-vitals-thresholds).
INP, not FID, is the responsiveness target. CrUX field data uses a rolling
28-day window. Lighthouse and local browser measurements are diagnostic lab
evidence, not substitutes for field performance.

No claim that Regula passes Core Web Vitals is made here. Low-traffic pages may
not have sufficient CrUX data. In that case, lab results will be labelled as
approximations.

## Automated accessibility audit

The audit completed on 26 August 2026 covered all 54 discovered canonical
pages at 1400×900 and 390×844 (108 runs). It reported zero axe violations for
the `wcag2a`, `wcag2aa`, `wcag21a`, `wcag21aa`, and `wcag22aa` tags. Axe also
returned 71 incomplete checks across 71 runs. Those require human review and
are not counted as passes.

The audit runner now discovers every canonical HTML page under `site/` on each
run. It excludes only redirect stubs and verbatim generated report examples.
It exits unsuccessfully for page-load errors or detected violations, preventing
a partial audit from appearing green. For every incomplete rule it preserves
every target, the relevant HTML and axe's failure summary; an earlier report
kept only the count, which made the required manual review unauditable.

Every incomplete result was `color-contrast`. Axe could not decide because of
gradients, partially obscured or overlapping elements, pseudo-elements,
non-text symbols, or very short text. Manual contrast calculation found and
fixed three genuine AA defects that the automated result left unresolved:

- the 13px decision-tree number changed from 4.13:1 to 5.97:1;
- the 11px pricing badge changed from 3.68:1 to 5.17:1; and
- the UAE action button's failing 3.68:1 blue stop and its light-green state
  were replaced with gradient stops that exceed 4.5:1 against white.

Shared navigation, callout, tracker and audience-card colours were calculated
against their worst declared composite backgrounds and met the applicable
threshold in the checked states. The remaining overlap and effective-background
cases stay in the manual review population; zero automated violations plus
these targeted calculations is still not a WCAG conformance result.

Run it with:

```bash
cd /tmp
npm install --prefix /tmp/regula-a11y-audit \
  playwright@1.62.1 @axe-core/playwright@4.12.1 axe-core@4.12.1
/tmp/regula-a11y-audit/node_modules/.bin/playwright install chromium

cd /path/to/getregula
# Background the server, or it blocks and the audit below never runs. The
# port is hardcoded in run-axe.js, so it must be 8790.
python3 -m http.server 8790 --bind 127.0.0.1 --directory site &
server_pid=$!
trap 'kill "$server_pid"' EXIT

A11Y_NODE_MODULES=/tmp/regula-a11y-audit/node_modules \
  AXE_REPORT=/tmp/regula-axe.json node docs/accessibility/run-axe.js
echo "exit: $?"   # 0 = no violations. Read it; a blank gate is not a green gate.
```

Do NOT use `playwright install --with-deps` outside CI: it escalates to root to
install system packages and fails on a workstation without a sudo terminal.
Plain `playwright install chromium` is what the local instruction above uses,
and it is sufficient where a browser's shared libraries are already present.

## Required manual evaluation

A claim of WCAG 2.2 AA conformance requires more than the automated audit.
Before making that claim, record results for:

- keyboard-only completion of the primary assessment and installation paths
- visible focus, focus order, dialogs, tabs, error recovery and status updates
- [200% text resizing](https://www.w3.org/WAI/WCAG22/Understanding/resize-text.html) and [400% reflow](https://www.w3.org/WAI/WCAG22/Understanding/reflow.html), text spacing and representative mobile sizes
- reduced motion and high-contrast or forced-colour behavior
- NVDA with Firefox or Chrome on Windows
- VoiceOver with Safari on macOS and iOS
- TalkBack with Chrome on Android
- accessible names, descriptions, roles and state announcements
- representative disabled-user testing

Automated tools can detect some failures. They cannot establish full
conformance, comprehension, confidence, or task success.

## Human-centred research policy

Research starts with a defined user, task, context, likely failure modes and
consequences. Design changes should record the evidence used and the people
affected, including stakeholders who are not direct users.

For low-traffic decisions:

- use moderated task testing rather than underpowered A/B tests
- use ten representative participants as the default minimum for one
  formative round; smaller rounds require repetition and must not be described
  as exhaustive
- treat card sorting as input to information architecture, not as the final
  navigation structure
- report tree-test sample size and confidence intervals rather than converting
  directional findings into population claims
- use readability scores as diagnostics, not pass/fail targets
- reject the three-click rule and unsupported attention-span claims

These are project research policies, not requirements of WCAG or ISO 9241.
They do not establish usability by themselves. Representative task testing is
still required.

## Evidence register

| Evidence | Current status | What it supports | What it cannot support |
|---|---|---|---|
| Axe audit, 26 August 2026 | 54 canonical pages × 2 viewports, zero detected violations; 71 incomplete color-contrast checks on 71 runs; all 511 incomplete nodes retained | Current automated rules on the discovered canonical surface | Manual criteria or WCAG conformance |
| Dynamic axe discovery | Implemented and exercised | Canonical-page selection and failing exit status | Manual criteria or user experience |
| Limited keyboard browser review | Homepage menu/error/result and full assessment primary/unknown paths exercised at desktop and mobile widths | Operability, focus and visible state on those tested paths | Screen-reader experience, other paths or representative-user success |
| Screen-reader review | Pending | Named assistive-technology behavior | All users and configurations |
| Moderated usability testing | Pending | Task success and observed failure modes for its sample | Population-wide certainty |
| CrUX field data | Not established | Real-user Core Web Vitals when available | Low-traffic pages without sufficient data |

Accessibility problems can be reported at
[support@getregula.com](mailto:support@getregula.com) or through
[GitHub issues](https://github.com/kuzivaai/getregula/issues).

## References

- [WCAG 2.2 Recommendation](https://www.w3.org/TR/WCAG22/)
- [W3C summary of the nine WCAG 2.2 additions](https://www.w3.org/WAI/standards-guidelines/wcag/new-in-22/)
- [W3C WCAG 2 overview, including ISO and EN 301 549 status](https://www.w3.org/WAI/standards-guidelines/wcag/)
- [UK public-sector accessibility guidance](https://www.gov.uk/guidance/accessibility-requirements-for-public-sector-websites-and-apps)
- [Core Web Vitals thresholds](https://web.dev/articles/defining-core-web-vitals-thresholds)
- [CrUX methodology and 28-day field windows](https://developer.chrome.com/docs/crux/methodology/tools)
