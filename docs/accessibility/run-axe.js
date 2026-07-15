const { chromium } = require('playwright');
const { AxeBuilder } = require('@axe-core/playwright');

const PAGES = [
  '/', '/locales/de.html', '/locales/pt-br.html',
  '/regions/uae.html', '/regions/regulations.html',
  '/regions/colorado-ai-regulation.html', '/regions/south-africa-ai-policy.html',
  '/regions/south-korea-ai-regulation.html', '/regions/uk-ai-regulation.html',
  '/regions/brazil-ai-regulation.html',
  '/blog/writing.html', '/blog/blog-does-ai-act-apply.html',
  '/blog/blog-omnibus-delay.html', '/blog/blog-risk-tiers-in-code.html',
  '/blog/blog-omnibus-trilogue-failed.html', '/blog/blog-omnibus-decision-framework.html',
  '/blog/blog-startups-ignoring-ai-act.html', '/blog/blog-code-scanning-vs-questionnaires.html',
  '/blog/blog-article-5-prohibited-practices.html', '/blog/blog-scanning-10-ai-apps.html',
  '/blog/blog-scanning-5-frameworks.html', '/blog/blog-classify-ai-system.html',
  '/blog/blog-static-analysis-ai-compliance.html', '/blog/blog-en-standards-mapping.html',
  '/blog/blog-art50-code-of-practice.html', '/blog/blog-aicdi-governance-gaps.html',
  '/pricing.html',
  '/assess/', '/assess/de.html', '/assess/pt-br.html',
  '/guides/article-5-prohibited-practices.html',
  '/guides/article-50-transparency.html',
  '/guides/eu-ai-act-healthcare.html',
  '/guides/eu-ai-act-javascript.html',
  '/404.html',
];

(async () => {
  const browser = await chromium.launch();
  const results = [];
  for (const p of PAGES) {
    const ctx = await browser.newContext({ viewport: { width: 1400, height: 900 } });
    await ctx.route('**/*plausible*', route => route.abort());
    const page = await ctx.newPage();
    try {
      console.error(`Testing ${p}`);
      await page.goto('http://127.0.0.1:8790' + p, { waitUntil: 'load', timeout: 30000 });
      // Wait for the media="print" → "all" swap AND stylesheet fully parsed
      await page.waitForFunction(() => {
        const sheets = Array.from(document.styleSheets).filter(s => s.href && (s.href.includes('site.css') || s.href.includes('site.min.css')));
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
