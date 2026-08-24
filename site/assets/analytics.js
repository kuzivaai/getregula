(function (root) {
  'use strict';

  var EVENT_PROPERTIES = {
    'Qualifier Start': [],
    'Qualifier Complete': [],
    'Assessment Start': [],
    'Assessment Complete': [],
    'Scanner Start': [],
    'Scanner Complete': [],
    'Scanner Error': [],
    'Install Command Copy': [],
    'GitHub Action Click': ['location'],
    'MCP Click': ['location'],
    'PyPI Click': ['location'],
    'GitHub Click': ['location'],
    'Sample Report View': ['asset'],
    'Pricing View': [],
    'Pricing FAQ Open': ['item'],
    'Contact Intent': ['route'],
    'Enquiry Prepared': [],
    'Documentation Search': []
  };

  var PROPERTY_VALUES = {
    location: ['homepage', 'product', 'assessment', 'footer', 'readme', 'sample'],
    asset: ['html-report', 'executive-summary'],
    item: ['scope', 'deliverable', 'price', 'data', 'limitations', 'availability'],
    route: ['starter', 'consultant', 'organisation', 'support', 'general']
  };

  var CAMPAIGNS = {
    campaign_source: ['github', 'pypi', 'mcp-registry', 'github-marketplace',
      'console-dev', 'ai-governance-library', 'python-bytes', 'talk-python',
      'changelog', 'iapp', 'corporate-outreach'],
    campaign_medium: ['repository', 'registry', 'marketplace', 'editorial',
      'community', 'email'],
    campaign_name: ['release-2-0', 'founder-qualifier', 'browser-scanner',
      'editorial-2026q3', 'b2b-pilot-2026q3']
  };

  var UTM_TO_PROPERTY = {
    utm_source: 'campaign_source',
    utm_medium: 'campaign_medium',
    utm_campaign: 'campaign_name'
  };
  var STORAGE_KEY = 'regula_campaign_v1';
  var fired = Object.create(null);

  function allowedValue(property, value) {
    return typeof value === 'string' &&
      PROPERTY_VALUES[property] &&
      PROPERTY_VALUES[property].indexOf(value) !== -1;
  }

  function readCampaign() {
    var safe = {};
    try {
      var params = new URLSearchParams(root.location.search || '');
      Object.keys(UTM_TO_PROPERTY).forEach(function (utm) {
        var property = UTM_TO_PROPERTY[utm];
        var value = params.get(utm);
        if (value && CAMPAIGNS[property].indexOf(value) !== -1) {
          safe[property] = value;
        }
      });
      if (Object.keys(safe).length) {
        root.sessionStorage.setItem(STORAGE_KEY, JSON.stringify(safe));
        return safe;
      }
      var stored = JSON.parse(root.sessionStorage.getItem(STORAGE_KEY) || '{}');
      Object.keys(CAMPAIGNS).forEach(function (property) {
        if (CAMPAIGNS[property].indexOf(stored[property]) !== -1) {
          safe[property] = stored[property];
        }
      });
    } catch (ignore) {
      return {};
    }
    return safe;
  }

  function sanitise(name, properties) {
    if (!Object.prototype.hasOwnProperty.call(EVENT_PROPERTIES, name)) {
      return null;
    }
    var safe = readCampaign();
    var allowed = EVENT_PROPERTIES[name];
    properties = properties || {};
    allowed.forEach(function (property) {
      if (allowedValue(property, properties[property])) {
        safe[property] = properties[property];
      }
    });
    return safe;
  }

  function track(name, properties, options) {
    var safe = sanitise(name, properties);
    if (safe === null) return false;
    options = options || {};
    var key = options.onceKey || name;
    if (options.once !== false && fired[key]) return false;
    fired[key] = true;
    if (typeof root.plausible === 'function') {
      root.plausible(name, { props: safe });
    }
    return true;
  }

  function pageLocation() {
    var path = (root.location && root.location.pathname) || '';
    if (path.indexOf('/assess') === 0) return 'assessment';
    if (path.indexOf('/product') === 0) return 'product';
    if (path.indexOf('/sample-report') === 0) return 'sample';
    if (path === '/' || path.indexOf('/locales/') === 0) return 'homepage';
    return 'footer';
  }

  function bindLinks(doc) {
    if (!doc || !doc.addEventListener) return;
    doc.addEventListener('click', function (event) {
      var link = event.target && event.target.closest ? event.target.closest('a[href]') : null;
      if (!link) return;
      var explicit = link.getAttribute('data-regula-event');
      if (explicit) {
        var property = link.getAttribute('data-regula-property');
        var value = link.getAttribute('data-regula-value');
        var props = {};
        if (property && value) props[property] = value;
        track(explicit, props, { onceKey: explicit + ':' + (value || pageLocation()) });
        return;
      }
      var href;
      try { href = new URL(link.href, root.location.href); } catch (ignore) { return; }
      if (href.hostname === 'pypi.org' && href.pathname.indexOf('/project/regula-ai') === 0) {
        track('PyPI Click', { location: pageLocation() });
      } else if (href.hostname === 'github.com' && href.pathname.indexOf('/kuzivaai/getregula') === 0) {
        track('GitHub Click', { location: pageLocation() });
      } else if (href.protocol === 'mailto:' && href.pathname === 'support@getregula.com') {
        var route = link.getAttribute('data-contact-route') || 'general';
        track('Contact Intent', { route: route }, { onceKey: 'Contact Intent:' + route });
      }
    });
  }

  var api = {
    eventProperties: EVENT_PROPERTIES,
    campaignAllowlists: CAMPAIGNS,
    sanitise: sanitise,
    track: track,
    bindLinks: bindLinks,
    _resetForTest: function () { fired = Object.create(null); }
  };
  root.RegulaAnalytics = api;
  if (root.document) bindLinks(root.document);
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
}(typeof window !== 'undefined' ? window : globalThis));
