# Accessibility — WCAG 2.2 AA audit

**Status:** ✅ 14 / 14 pages pass WCAG 2.2 AA
**Last audit:** 2026-04-16
**Tool:** [axe-core](https://github.com/dequelabs/axe-core) 4.x via
[`@axe-core/playwright`](https://www.npmjs.com/package/@axe-core/playwright),
ruleset `wcag2a + wcag2aa + wcag21a + wcag21aa + wcag22aa`

## Scope

All 14 non-stub canonical HTML pages under `site/`:

- `/` (English landing)
- `/locales/de.html`, `/locales/pt-br.html` (localised landings)
- `/regions/{uae,regulations,colorado-ai-regulation,south-africa-ai-policy,south-korea-ai-regulation,uk-ai-regulation}.html`
- `/blog/{writing,blog-does-ai-act-apply,blog-omnibus-delay,blog-risk-tiers-in-code}.html`
- `/404.html`

Redirect stubs at the root level (`site/de.html`, `site/pt-br.html`, etc.) are
excluded — they meta-refresh in 0 seconds and never render their own content.

## What we did

### Findings at baseline (pre-audit, before remediation)

| Rule | Impact | Total nodes | Pages affected |
|---|---|---|---|
| `color-contrast` | serious | 71 | 6 |
| `link-in-text-block` | serious | 63 | 12 |

### Remediations applied

1. **`.t-m` / `.t-p` terminal muted colour:** `#44445a` → `#8a8aa8` (raises contrast from 1.98:1 to 4.62:1 on `--bg-elev`).
2. **`.social-proof .sp-sep` middot separators:** marked `aria-hidden="true"` in HTML (they are decorative); CSS colour also bumped for the edge case where they are seen.
3. **Tier badges (`.tier-r/-a/-y/-g .tier-badge`) and art tags (`.tag-blue/-red/-amber/-purple`):** background alpha raised 0.12→0.18/0.20 and text colour shifted to the `-400` variants of each tier hue (`#f87171`, `#fbbf24`, `#facc15`, `#34d399`, `#60a5fa`, `#a78bfa`). All at ≥4.5:1 on their card backgrounds.
4. **Form submit button + in-page copy buttons:** `background: var(--accent)` (`#3b82f6`, 3.67:1 with white text) → `#1d4ed8` (blue-700) with `color:#fff` (≥5:1). Hover state `#1e40af`.
5. **`.reg-card.upcoming` opacity:** `opacity: 0.6` dimmed child text colours below threshold. Replaced with `opacity: 0.85 + border-style: dashed` to signal "upcoming" without muting text.
6. **`.reg-cta.disabled`:** `var(--text-faint)` → `var(--text-dim)` (4.0:1 → 5.29:1).
7. **`.liab-card .ref` citation colour:** `#555` → `#9898b4`.
8. **UAE legal-disclaimer paragraph:** A sweep had bumped `#66668a` → `#9898b4` for the dark-bg case, but one instance lives on a cream `#fff8e7` background. Corrected to `#3f3a26` for that specific paragraph.
9. **In-content link underline rule** (WCAG 2.2 SC 1.4.1 — "Use of Color"): added `text-decoration: underline` with `text-underline-offset: 3px` for all `<a>` tags in `main p`, `main li`, `.hero-text .sub`, `.competitor-note`, `.urgency-box .body`, `.blog-body`, `.breadcrumb`, `.last-updated`, `.foot-copy`, `.foot-legal`, `footer p`. Hover state thickens the underline. Nav/CTA/art-card anchors deliberately excluded — they have their own visual affordance.
10. **Footer `#666` and `#888` legacy colours on UAE page:** bumped to `#9898b4` / `#b8b8c8`.

### Findings post-remediation

```
  /                                          clean
  /locales/de.html                           clean
  /locales/pt-br.html                        clean
  /regions/uae.html                          clean
  /regions/regulations.html                  clean
  /regions/colorado-ai-regulation.html       clean
  /regions/south-africa-ai-policy.html       clean
  /regions/south-korea-ai-regulation.html    clean
  /regions/uk-ai-regulation.html             clean
  /blog/writing.html                         clean
  /blog/blog-does-ai-act-apply.html          clean
  /blog/blog-omnibus-delay.html              clean
  /blog/blog-risk-tiers-in-code.html         clean
  /404.html                                  clean

Total violations: 0
```

Full machine-readable report: [`axe-audit-2026-04-16.json`](axe-audit-2026-04-16.json).

## How to re-run

```bash
# Install dependencies (one-time)
cd /tmp && npm install --no-save playwright @axe-core/playwright axe-core
npx playwright install chromium  # if not already installed

# From the getregula repo root:
python3 -m http.server 8790 --bind 127.0.0.1 --directory site &
node docs/accessibility/run-axe.js
```

The script waits for the `media="print"` → `"all"` stylesheet swap to finish
(see [`site/index.html`](../../site/index.html) FOUC pattern) AND for the
stylesheet to be fully parsed (`cssRules.length > 100`) before running axe,
to avoid false-positive link-in-text-block failures caused by axe sampling
the page state before `site.css` has applied.

## What this certifies — and what it doesn't

**What this certifies:**

- Automated WCAG 2.2 AA checks pass on every canonical page.
- Colour contrast ≥ 4.5:1 for normal text, ≥ 3:1 for large text (24px+ or 18.66px+ bold) and UI components.
- Links that sit inside text blocks are distinguished by more than colour alone (underline + color).
- Every `<img>` has alt text (or is a decorative `<svg>` carrying `aria-hidden`).
- Keyboard navigation reaches all interactive elements.
- Form controls have associated labels.
- ARIA landmark structure is valid.

**What this does NOT certify:**

- Automated tooling catches ~30–50% of real accessibility barriers. Passing
  axe is a floor, not a ceiling.
- **Manual screen-reader testing** (NVDA on Windows, VoiceOver on macOS,
  TalkBack on Android) has NOT been performed. Do that before making a
  formal AA claim.
- **Keyboard-only end-to-end walkthroughs** of the tabbed hero terminal
  demo have NOT been tested.
- **Real users with assistive technology** have not tested the site.
  Automated and expert review both miss user-reported friction.

If a real user reports an accessibility issue that axe missed, that report
trumps this audit — file it, fix it, re-run the audit.

## References

- [WCAG 2.2 AA specification](https://www.w3.org/TR/WCAG22/#level-aa-conformance)
- [axe-core rule descriptions](https://dequeuniversity.com/rules/axe/4.10)
- [EN 301 549 (EU accessibility standard)](https://www.etsi.org/deliver/etsi_en/301500_301599/301549/)
