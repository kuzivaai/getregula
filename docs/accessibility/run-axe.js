// A11Y_NODE_MODULES allows a clean, exact-version tool install outside the
// repository without changing the product's zero-dependency runtime.
const moduleRoot = process.env.A11Y_NODE_MODULES;
const { chromium } = require(moduleRoot ? pathJoin(moduleRoot, 'playwright') : 'playwright');
const { AxeBuilder } = require(moduleRoot ? pathJoin(moduleRoot, '@axe-core/playwright') : '@axe-core/playwright');
const fs = require('fs');
const path = require('path');

function pathJoin(...parts) {
  return parts.join('/');
}

const SITE = path.resolve(__dirname, '../../site');
const REDIRECT_STUBS = new Set([
  'de.html', 'pt-br.html', 'uae.html', 'uk-ai-regulation.html',
  'south-africa-ai-policy.html', 'south-korea-ai-regulation.html',
  'colorado-ai-regulation.html', 'regulations.html',
  'blog-does-ai-act-apply.html', 'blog-omnibus-delay.html',
  'blog-risk-tiers-in-code.html', 'writing.html',
]);

function htmlFiles(directory) {
  return fs.readdirSync(directory, { withFileTypes: true }).flatMap(entry => {
    const target = path.join(directory, entry.name);
    return entry.isDirectory() ? htmlFiles(target) :
      (entry.isFile() && entry.name.endsWith('.html') ? [target] : []);
  });
}

function pageUrl(file) {
  const relative = path.relative(SITE, file).split(path.sep).join('/');
  if (relative === 'index.html') return '/';
  if (relative.endsWith('/index.html')) return '/' + relative.slice(0, -10);
  return '/' + relative;
}

// Discover the shipped canonical surface on every run. Redirect-only stubs
// and verbatim generated report examples are deliberately out of scope.
const PAGES = htmlFiles(SITE)
  .map(file => path.relative(SITE, file).split(path.sep).join('/'))
  .filter(relative => !REDIRECT_STUBS.has(relative))
  .filter(relative => !relative.startsWith('examples/'))
  .map(relative => pageUrl(path.join(SITE, relative)))
  .sort();

// Every page is audited at BOTH a desktop and a mobile viewport.
//
// It used to run at 1400x900 only, and that single width is why a real
// WCAG 2.1.1 failure shipped: a scrollable table wrapper on
// blog-aicdi-governance-gaps.html has no focusable content and no tabindex,
// and it only overflows once the viewport is narrow enough. Measured across
// 1400, 1200, 800 and 390, it appears at 390 and nowhere else, so the audit
// reported zero violations while a keyboard user on a phone could not reach
// the table. The site's own breakpoint is 900px (site.css), so testing only
// above it exercises one side of every responsive rule the site has.
//
// 390x844 is a current small-phone viewport. Findings are reported per
// viewport so a regression names the width it appears at.
const VIEWPORTS = [
  { name: 'desktop', width: 1400, height: 900 },
  { name: 'mobile', width: 390, height: 844 },
];

(async () => {
  const browser = await chromium.launch();
  const results = [];
  for (const vp of VIEWPORTS) {
  for (const p of PAGES) {
    const ctx = await browser.newContext({ viewport: { width: vp.width, height: vp.height } });
    await ctx.route('**/*plausible*', route => route.abort());
    // The audit evaluates the shipped DOM, styles and local interaction code.
    // Do not let the optional third-party newsletter enhancement make page
    // loading depend on registry/CDN availability in the audit environment.
    await ctx.route('https://unpkg.com/**', route => route.abort());
    const page = await ctx.newPage();
    try {
      console.error(`Testing ${p} @${vp.name}`);
      await page.goto('http://127.0.0.1:8790' + p, { waitUntil: 'load', timeout: 30000 });
      // Wait for the media="print" → "all" swap AND stylesheet fully parsed
      await page.waitForFunction(() => {
        const sheets = Array.from(document.styleSheets).filter(s => s.href && (s.href.includes('site.css') || s.href.includes('site.min.css')));
        // The assessment tool intentionally uses a self-contained stylesheet.
        // For other pages, wait until the deferred shared stylesheet is parsed.
        return sheets.length === 0 || sheets.every(s =>
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
        viewport: vp.name,
        violations: axe.violations.length,
        violationRules: axe.violations.map(v => ({ id: v.id, impact: v.impact, description: v.description, nodes: v.nodes.length, sampleTargets: v.nodes.slice(0,2).map(n=>n.target.join(' ')) })),
        passes: axe.passes.length,
        incomplete: axe.incomplete.length,
      });
    } catch (e) { results.push({ page: p, viewport: vp.name, error: e.message }); }
    await ctx.close();
  }
  }
  const report = JSON.stringify(results, null, 2);
  console.log(report);
  if (process.env.AXE_REPORT) fs.writeFileSync(process.env.AXE_REPORT, report + '\n');
  const failures = results.filter(result => result.error || result.violations > 0);
  const pageCount = new Set(results.map(r => r.page)).size;
  console.error(`Audited ${pageCount} canonical pages at ${VIEWPORTS.length} viewport(s) `
    + `(${results.length} runs); ${failures.length} failed.`);
  if (failures.length) process.exitCode = 1;
  await browser.close();
})();
