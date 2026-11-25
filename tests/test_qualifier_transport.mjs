// Contract test, not a browser test: run the actual engine against the values and
// copy of each shipped page, then capture an actual loopback HTTP request.
// No credentials, external services, submitted data or browser dependencies.
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createServer } from 'node:http';
import { runInNewContext } from 'node:vm';

const engine = readFileSync('site/assets/qualifier.js', 'utf8');
const examples = ['yes', 'yes', 'built', 'yes', 'unsure'];

// Only the DOM primitives the qualifier uses for rendering and dispatch.
function visit(html, url) {
  const controls = new Map();
  const nodes = new Map();
  let shareButton, clipboard;
  const element = () => ({
    textContent: '', hidden: false, classList: { remove() {} },
    getAttribute(key) { return this[key]; },
    setAttribute(key, value) { this[key] = value; },
    focus() {}, appendChild() {},
    addEventListener(name, callback) { this[name] = callback; },
    querySelector(selector) {
      const match = selector.match(/name="(q[1-5])"(?:\]\[value="([^"]+)")?/);
      if (!match) return null;
      if (match[2]) return controls.get(match[1] + ':' + match[2]) ?? null;
      return [...controls.values()].find(input => input.name === match[1] && input.checked) ?? null;
    },
  });
  for (const [, name, value] of html.matchAll(/name="(q[1-5])" value="([^"]+)"/g)) {
    controls.set(name + ':' + value, { name, value, checked: false });
  }
  const document = {
    readyState: 'complete',
    getElementById(id) {
      if (!nodes.has(id)) {
        const node = element();
        if (id === 'qual-copy') node.textContent = html.match(/id="qual-copy">([\s\S]*?)<\/script>/)[1];
        if (id === 'qual-result') node.hidden = true;
        nodes.set(id, node);
      }
      return nodes.get(id);
    },
    createElement(tag) {
      const node = element();
      if (tag === 'button') shareButton = node;
      return node;
    },
  };
  runInNewContext(engine, {
    document, window: { location: new URL(url) }, URLSearchParams, CSS: { escape: value => value },
    navigator: { clipboard: { async writeText(value) { clipboard = value; } } },
  });
  return {
    restored: () => [...controls.values()].filter(input => input.checked).map(input => input.value),
    hasResult: () => document.getElementById('qual-result').hidden === false,
    share() {
      examples.forEach((value, i) => { controls.get('q' + (i + 1) + ':' + value).checked = true; });
      document.getElementById('qual-form').submit({ preventDefault() {} });
      shareButton.click();
      return clipboard;
    },
  };
}

const requests = [];
const server = createServer((request, response) => { requests.push(request.url); response.end('OK'); });
await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
try {
  for (const page of ['site/index.html', 'site/locales/de.html', 'site/locales/pt-br.html']) {
    const html = readFileSync(page, 'utf8');
    const endpoint = 'http://127.0.0.1:' + server.address().port + '/' + page.replace(/^site\//, '');
    const link = visit(html, endpoint).share();
    const target = new URL(link);
    assert.equal(target.origin + target.pathname, endpoint);
    assert.equal(target.search, '', 'generated link must not put answers in the query');
    requests.length = 0;
    await (await fetch(link)).text();
    assert.deepEqual(requests, [target.pathname], 'HTTP receiver must see only the path');
    for (const validLink of [link, link.replace('#qual=', '?qual=')]) {
      const reader = visit(html, validLink);
      assert(reader.hasResult());
      assert.deepEqual(reader.restored(), examples);
    }
    const empty = visit(html, endpoint); assert(!empty.hasResult()); assert.deepEqual(empty.restored(), []);
    console.log(page + ': new link stays out of HTTP; new and legacy links restore choices.');
  }
} finally {
  server.close();
}
