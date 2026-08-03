---
paths:
  - "site/**/*.html"
  - "site/**/*.css"
---

# Site HTML/CSS Rules

- Use `h3` not `h4` for card-level headings (WCAG 1.3.1 heading hierarchy)
- Use `var(--text-dim)` not `#707090` for muted inline text (WCAG AA contrast)
- Add `class="cmp-table"` to comparison tables for sticky first column on mobile
- All interactive elements need min 44x44px touch targets (WCAG 2.5.8)
- Add `:focus-visible` rules for any custom focusable elements (divs with role/tabindex)
- Every change to EN content must also update `site/locales/de.html` and `site/locales/pt-br.html`
- Non-render-blocking CSS: use `media="print" onload="this.media='all'"` pattern with `<noscript>` fallback
- Use shared design tokens from `site/assets/site.css` — do not hardcode colours
