/* Regula qualifier engine.
 *
 * ONE engine, THREE string tables. This file contains no user-facing prose in
 * any language: every string is read from the <script type="application/json"
 * id="qual-copy"> block in the page that loads it. That is deliberate and it is
 * the project's own rule (.claude/rules/quality-standards.md): a copy of the
 * logic in each locale page WILL drift silently, so there is one copy of the
 * logic and the locale pages carry only what differs, which is words.
 *
 * tests/test_qualifier.py enforces the consequences of that split: the three
 * string tables must have identical key structure, the form markup must expose
 * identical question ids and option values, and no regulatory date may be
 * hand-authored in prose. Dates arrive as ISO strings, are checked against
 * scripts/omnibus.py (the repository's single source of truth for them) and are
 * rendered here, so a deadline cannot drift between languages.
 *
 * WHAT THIS DOES NOT DO, and must never be changed to do. It does not classify,
 * score, rank or determine anything. It reports which parts of the law the
 * reader's own answers point at, and which facts remain unsettled. There is no
 * tier, no percentage and no compliance state anywhere in this file, because a
 * scanner and five questions cannot establish any of them.
 */
(function () {
  'use strict';

  var QIDS = ['q1', 'q2', 'q3', 'q4', 'q5'];

  /* The stateless encoding is versioned. If the meaning of any position or any
   * value changes, bump this and add a decoder for the old version; do not
   * reinterpret an old link under new rules. */
  var ENCODING_VERSION = 'v1';

  var form, resultBox, errorBox, copy, resetBtn;

  function byId(id) { return document.getElementById(id); }

  function answers() {
    var out = {};
    QIDS.forEach(function (q) {
      var picked = form.querySelector('input[name="' + q + '"]:checked');
      out[q] = picked ? picked.value : null;
    });
    return out;
  }

  function missing(a) {
    return QIDS.filter(function (q) { return !a[q]; });
  }

  function fmtDate(iso) {
    var parts = String(iso).split('-');
    var day = String(parseInt(parts[2], 10));
    var month = copy.months[parseInt(parts[1], 10) - 1];
    return copy.dateFormat
      .replace('{d}', day)
      .replace('{month}', month)
      .replace('{y}', parts[0]);
  }

  function fill(text) {
    return String(text).replace(/\{(\w+)\}/g, function (whole, key) {
      return Object.prototype.hasOwnProperty.call(copy.dates, key)
        ? fmtDate(copy.dates[key])
        : whole;
    });
  }

  function el(tag, className, text) {
    var node = document.createElement(tag);
    if (className) { node.className = className; }
    if (text !== undefined && text !== null) { node.textContent = fill(text); }
    return node;
  }

  /* Which pointers the answers raise. Deterministic, and deliberately generous:
   * "not sure" raises a pointer rather than clearing it, because the reader who
   * does not know is the reader this page is for, and silently treating an
   * unknown as a negative would be the tool answering a question it was just
   * told nobody can answer. */
  function pointerKeys(a) {
    var euReached = (a.q1 === 'yes' || a.q1 === 'unsure');
    var usesAi = (a.q2 === 'yes' || a.q2 === 'unsure');
    var keys = [];

    if (!euReached) { keys.push('noEu'); }
    else if (a.q1 === 'unsure') { keys.push('scopeUnsure'); }
    else { keys.push('scope'); }

    if (!usesAi) {
      keys.push('noAi');
      return keys;
    }

    keys.push('definition');

    if (a.q3 === 'built') { keys.push('roleProvider'); }
    else if (a.q3 === 'using') { keys.push('roleDeployer'); }
    else if (a.q3 === 'both') { keys.push('roleBoth'); }
    else { keys.push('roleUnsure'); }

    if (a.q4 === 'yes' || a.q4 === 'unsure') { keys.push('transparency'); }
    if (a.q5 === 'yes' || a.q5 === 'unsure') { keys.push('decisions'); }
    keys.push('prohibited');
    return keys;
  }

  function ledeKey(a) {
    if (a.q1 === 'no') { return 'ledeNoEu'; }
    if (a.q2 === 'no') { return 'ledeNoAi'; }
    return 'ledeIn';
  }

  /* Reasoned, not evidenced: the consultant route is given extra prominence
   * only where an answer names a use the law treats most strictly, or where the
   * reader builds the system and cannot say. Documented in
   * docs/ux/USERS-JOURNEYS-IA-2026-08.md section 2. */
  function consultantWarranted(a) {
    return a.q5 === 'yes' || (a.q3 === 'built' && a.q5 === 'unsure');
  }

  /* Every page the qualifier links to is English. A reader on the German or
   * Brazilian page following one lands on a page they may not be able to read,
   * so the link declares the change of language. The visible cue is in the
   * copy table beside the link text; this adds the machine-readable half.
   * scripts/locale_link_audit.py enforces it across the whole site. */
  function markLanguage(anchor) {
    if (copy.lang !== 'en' && anchor.getAttribute('href').charAt(0) === '/') {
      anchor.setAttribute('hreflang', 'en');
    }
  }

  function buildPoint(key) {
    var p = copy.points[key];
    var item = el('li', 'qual-point');
    item.appendChild(el('h4', null, p.title));
    item.appendChild(el('p', null, p.body));
    if (p.href) {
      var a = el('a', 'qual-point-link', p.linkText);
      a.href = p.href;
      markLanguage(a);
      item.appendChild(a);
    }
    if (p.cite) { item.appendChild(el('span', 'qual-cite', p.cite)); }
    return item;
  }

  function buildRoute(key, open) {
    var r = copy.routes[key];
    var card = el('div', 'qual-route' + (open ? ' is-open' : ''));
    card.appendChild(el('h4', null, r.title));
    card.appendChild(el('p', 'qual-price', r.price));
    card.appendChild(el('p', null, r.body));
    if (r.cmd) { card.appendChild(el('code', null, r.cmd)); }
    var cta = el('a', 'qual-route-cta', r.cta);
    cta.href = r.href;
    markLanguage(cta);
    card.appendChild(cta);
    return card;
  }

  function render(a, recordCompletion) {
    resultBox.textContent = '';

    var h2 = el('h2', null, copy.resultHeading);
    h2.id = 'qual-result-h';
    resultBox.appendChild(h2);
    resultBox.setAttribute('aria-labelledby', 'qual-result-h');
    resultBox.appendChild(el('p', 'qual-lede', copy[ledeKey(a)]));

    resultBox.appendChild(el('h3', null, copy.pointsHeading));
    var list = el('ul', 'qual-points');
    pointerKeys(a).forEach(function (key) { list.appendChild(buildPoint(key)); });
    resultBox.appendChild(list);

    resultBox.appendChild(el('h3', null, copy.unsettledHeading));
    var unsettled = el('ul', 'qual-unsettled');
    copy.unsettled.forEach(function (line) { unsettled.appendChild(el('li', null, line)); });
    resultBox.appendChild(unsettled);

    resultBox.appendChild(el('h3', null, copy.routesHeading));
    var warranted = consultantWarranted(a);
    /* Answers that point nowhere get one route and a sentence saying so. Laying
     * three commercial options in front of a reader who has just been told the
     * rules may not reach them would contradict the sentence above them, and
     * the project's own market model has no budget anchor for that reader
     * anyway. docs/ux/USERS-JOURNEYS-IA-2026-08.md, section 0. */
    var nothingToBuy = (a.q1 === 'no' && a.q2 === 'no');
    if (warranted) { resultBox.appendChild(el('p', 'qual-lede', copy.consultantWarranted)); }
    if (nothingToBuy) { resultBox.appendChild(el('p', 'qual-lede', copy.nothingToBuy)); }
    var routes = el('div', 'qual-routes');
    routes.appendChild(buildRoute('free', true));
    if (!nothingToBuy) {
      routes.appendChild(buildRoute('paid', false));
      routes.appendChild(buildRoute('consultant', warranted));
    }
    resultBox.appendChild(routes);

    var limits = el('div', 'qual-limits');
    limits.setAttribute('role', 'note');
    copy.limits.forEach(function (line) { limits.appendChild(el('p', null, line)); });
    resultBox.appendChild(limits);

    var share = el('div', 'qual-share');
    var shareBtn = el('button', 'qual-quiet', copy.shareLabel);
    shareBtn.type = 'button';
    shareBtn.addEventListener('click', function () { copyLink(a, shareBtn); });
    share.appendChild(shareBtn);
    resultBox.appendChild(share);

    resultBox.hidden = false;
    h2.setAttribute('tabindex', '-1');
    h2.focus();
    /* Record completion without any answer or result property. A shared-link
     * render is deliberately excluded: it is a view of someone else's saved
     * state, not a completion by this visitor. */
    if (recordCompletion && window.RegulaAnalytics) {
      window.RegulaAnalytics.track('Qualifier Complete');
    }
  }

  function encode(a) {
    return ENCODING_VERSION + '.' + QIDS.map(function (q) { return a[q]; }).join('-');
  }

  function decode(raw) {
    if (!raw) { return null; }
    var bits = String(raw).split('.');
    if (bits[0] !== ENCODING_VERSION) { return null; }
    var values = bits[1] ? bits[1].split('-') : [];
    if (values.length !== QIDS.length) { return null; }
    var out = {};
    for (var i = 0; i < QIDS.length; i += 1) {
      var input = form.querySelector('input[name="' + QIDS[i] + '"][value="' + CSS.escape(values[i]) + '"]');
      if (!input) { return null; }
      out[QIDS[i]] = values[i];
    }
    return out;
  }

  function copyLink(a, button) {
    var url = window.location.origin + window.location.pathname + '?qual=' + encodeURIComponent(encode(a));
    var done = function () { button.textContent = fill(copy.shareDone); };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(url).then(done, function () { window.prompt(fill(copy.shareLabel), url); });
    } else {
      window.prompt(fill(copy.shareLabel), url);
    }
  }

  function showError(gaps) {
    /* Nothing answered is not five mistakes, it is a page nobody has started,
     * so it gets its own message and no red marking. Marking every question at
     * once reads as an accusation and is the state a first-time reader is most
     * likely to hit. Only a partial answer set marks the specific gaps. */
    var untouched = gaps.length === QIDS.length;
    var template = untouched ? copy.errorNone
                 : (gaps.length === 1 ? copy.errorOne : copy.errorMany);
    errorBox.textContent = fill(template).replace('{n}', String(gaps.length));
    /* Set explicitly rather than assumed: reset() restyles this element to
     * carry the neutral cleared-answers notice, and a submit straight after a
     * reset would otherwise show an error in the notice's colours. */
    errorBox.className = 'qual-err';
    errorBox.hidden = false;
    QIDS.forEach(function (q) {
      var block = byId('qual-' + q);
      if (block) { block.classList.toggle('is-missing', !untouched && gaps.indexOf(q) !== -1); }
    });

    /* The radio itself is clipped to a single pixel, so focusing it does not
     * reliably bring its question into view for a sighted keyboard user. Scroll
     * the question block first, then focus the real control so the role, the
     * name and the checked state still come from the native radio. */
    var block = byId('qual-' + gaps[0]);
    if (block && block.scrollIntoView) {
      var still = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
      block.scrollIntoView({ block: 'center', behavior: still ? 'instant' : 'smooth' });
    }
    var first = form.querySelector('input[name="' + gaps[0] + '"]');
    if (first) { first.focus({ preventScroll: true }); }
  }

  function clearError() {
    errorBox.hidden = true;
    errorBox.textContent = '';
    QIDS.forEach(function (q) {
      var block = byId('qual-' + q);
      if (block) { block.classList.remove('is-missing'); }
    });
  }

  function submit(event) {
    if (event) { event.preventDefault(); }
    var a = answers();
    var gaps = missing(a);
    if (gaps.length) {
      resultBox.hidden = true;
      showError(gaps);
      return;
    }
    clearError();
    render(a, true);
    if (resetBtn) { resetBtn.disabled = false; }
  }

  function reset() {
    form.reset();
    clearError();
    resultBox.hidden = true;
    resultBox.textContent = '';
    errorBox.textContent = fill(copy.clearedNotice);
    errorBox.hidden = false;
    errorBox.className = 'qual-nojs';
    if (resetBtn) { resetBtn.disabled = true; }
    var first = form.querySelector('input[name="q1"]');
    if (first) { first.focus(); }
  }

  function start() {
    form = byId('qual-form');
    resultBox = byId('qual-result');
    errorBox = byId('qual-error');
    resetBtn = byId('qual-reset');
    var copyNode = byId('qual-copy');
    if (!form || !resultBox || !errorBox || !copyNode) { return; }

    try { copy = JSON.parse(copyNode.textContent); }
    catch (err) { return; }

    /* The questions are server-rendered and readable without this file. Only
     * the computation is progressive enhancement, so the no-JavaScript notice
     * is removed here rather than being absent and added by script. */
    var nojs = byId('qual-nojs');
    if (nojs) { nojs.hidden = true; }

    form.addEventListener('submit', submit);
    if (resetBtn) {
      resetBtn.disabled = true;
      resetBtn.addEventListener('click', reset);
    }
    form.addEventListener('change', function () {
      clearError();
      errorBox.className = 'qual-err';
      if (resetBtn) { resetBtn.disabled = false; }
      if (window.RegulaAnalytics) {
        window.RegulaAnalytics.track('Qualifier Start');
      }
    });

    var shared = decode(new URLSearchParams(window.location.search).get('qual'));
    if (shared) {
      QIDS.forEach(function (q) {
        var input = form.querySelector('input[name="' + q + '"][value="' + CSS.escape(shared[q]) + '"]');
        if (input) { input.checked = true; }
      });
      render(shared, false);
      if (resetBtn) { resetBtn.disabled = false; }
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start);
  } else {
    start();
  }
}());
