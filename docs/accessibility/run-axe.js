const { chromium } = require('playwright');
const { AxeBuilder } = require('@axe-core/playwright');

const PAGES = [
  '/', '/locales/de.html', '/locales/pt-br.html',
  '/regions/uae.html', '/regions/regulations.html',
  '/regions/colorado-ai-regulation.html', '/regions/south-africa-ai-policy.html',
  '/regions/south-korea-ai-regulation.html', '/regions/uk-ai-regulation.html',
  '/blog/writing.html', '/blog/blog-does-ai-act-apply.html',
  '/blog/blog-omnibus-delay.html', '/blog/blog-risk-tiers-in-code.html',
  '/404.html',
];

(async () => {
  const browser = await chromium.launch();
  const results = [];
  for (const p of PAGES) {
    const ctx = await browser.newContext({ viewport: { width: 1400, height: 900 } });
    const page = await ctx.newPage();
    try {
      await page.goto('http://127.0.0.1:8790' + p, { waitUntil: 'load', timeout: 30000 });
      // Wait for the media="print" → "all" swap AND stylesheet fully parsed
      await page.waitForFunction(() => {
        const sheets = Array.from(document.styleSheets).filter(s => s.href && s.href.includes('site.css'));
        return sheets.length > 0 && sheets.every(s =>
          (s.media.mediaText === 'all' || s.media.mediaText === '')
          && s.cssRules
          && s.cssRules.length > 100
        );
      }, { timeout: 10000 });
      await page.waitForLoadState('networkidle', { timeout: 5000 }).catch(() => {});
      await page.waitForTimeout(1000);
      const axe = await new AxeBuilder({ page }).withTags(['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']).analyze();
      results.push({
        page: p,
        violations: axe.violations.length,
        violationRules: axe.violations.map(v => ({ id: v.id, impact: v.impact, description: v.description, nodes: v.nodes.length, sampleTargets: v.nodes.slice(0,2).map(n=>n.target.join(' ')) })),
        passes: axe.passes.length,
        incomplete: axe.incomplete.length,
      });
    } catch (e) { results.push({ page: p, error: e.message }); }
    await ctx.close();
  }
  console.log(JSON.stringify(results, null, 2));
  await browser.close();
})();
