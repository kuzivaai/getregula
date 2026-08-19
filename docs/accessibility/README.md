# Accessibility and human-centred quality

**Target:** WCAG 2.2 Level AA<br>
**Conformance status:** not claimed<br>
**Last completed automated audit:** 15 August 2026, 48 canonical pages, zero axe
violations, on the working tree of `feat/engagement-fixes` (unpushed)<br>
**Previous:** 4 August 2026, 42 canonical pages, zero axe violations<br>
**Audit tools:** Playwright 1.62.1 and axe-core 4.12.1

**The 15 August run found two violations before it found none.** Both were
`scrollable-region-focusable`, impact serious: a horizontally scrolling `<pre>`
that a keyboard user cannot scroll, on `/guides/article-9-risk-management.html`
and `/guides/eu-ai-act-healthcare.html`. That is WCAG 2.1.1 Keyboard, a Level A
criterion, on a site whose target is AA.

They were a regression on this branch, established by measurement rather than
inference: the audit was re-run in a worktree at `688d1a7`, where both pages
were in scope and both returned zero. Commit `4de7541`, the N108 correction
that replaced published CLI transcripts with real command output, took the
longest line inside those `<pre>` blocks from 68 and 74 characters to 121. At
the runner's fixed 1400px viewport that is the width at which the block starts
to scroll.

**Why nothing caught it.** `.github/workflows/accessibility.yml` triggers on
`pull_request` for `site/**`. The branch carrying the regression has never been
pushed, so the job had never run against it. The gate is correct and it is
wired to the right paths; it is blind to work that stays local. Run it locally
before relying on it (see below).

The fix completes a pattern the site already used inconsistently: 22 of 73
`<pre>` elements carried `tabindex="0"` and 51 did not. All 73 now do, so the
next transcript that grows past the container is focusable before anyone
notices it scrolls. An accessible name was deliberately not added: `role` plus
`aria-label` on 73 code blocks would add 73 landmarks and make screen-reader
navigation worse, and the axe rule asks for focusability.

**Thirteen pages return `incomplete` results**, which axe reports when it
cannot decide and a human must. Those are not counted as passes here, and
automated checks reach only part of WCAG in any case. Zero violations means
zero violations of the rules this tool can evaluate. It is not conformance,
and nothing in this file should be read as claiming it.

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

The current audit on 4 August 2026 covered all 42 discovered canonical pages
and reported zero axe violations for the `wcag2a`, `wcag2aa`, `wcag21a`,
`wcag21aa`, and `wcag22aa` tags. Axe also returned 16 incomplete checks across
13 pages. Those require human review and are not counted as passes.

The audit runner now discovers every canonical HTML page under `site/` on each
run. It excludes only redirect stubs and verbatim generated report examples.
It exits unsuccessfully for page-load errors or detected violations, preventing
a partial audit from appearing green.

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
| Axe audit, 4 August 2026 | 42 canonical pages, zero detected violations; 16 incomplete checks on 13 pages | Current automated rules on the discovered canonical surface | Manual criteria or WCAG conformance |
| Dynamic axe discovery | Implemented and exercised | Canonical-page selection and failing exit status | Manual criteria or user experience |
| Keyboard browser review | Pending | Operability and visible state on tested paths | Screen-reader experience |
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
