#!/usr/bin/env node
// Browser questionnaire contract tests. No decision logic is reproduced here.
"use strict";

const fs = require("fs");
const path = require("path");
const root = path.resolve(__dirname, "..");
const model = require(path.join(root, "site", "assess", "decision-model.js"));
globalThis.RegulaDecisionModel = model;
globalThis.RegulaDecisionKernel = require(
  path.join(root, "site", "assess", "decision-kernel.js"));
const adapters = require(path.join(root, "site", "assess", "decision-adapters.js"));

const NOW = "2026-08-12T12:00:00+00:00";
let passed = 0;
const failures = [];

function check(condition, message) {
  if (condition) passed += 1;
  else failures.push(message);
}

function equal(actual, expected, message) {
  check(actual === expected, `${message}: expected ${expected}, got ${actual}`);
}

for (const generatedDataFile of ["decision-model.js", "decision-adapters.js"]) {
  const source = fs.readFileSync(path.join(root, "site", "assess", generatedDataFile), "utf8");
  check(source.startsWith("// regula-ignore: * -- "),
    `${generatedDataFile} carries a reasoned self-scan suppression`);
}
const decisionUiSource = fs.readFileSync(
  path.join(root, "site", "assess", "decision-ui.js"), "utf8");
check(decisionUiSource.includes("human_decision"),
  "browser result visibly preserves the empty human decision field");
check(decisionUiSource.includes("potentially_relevant_provisions"),
  "browser result visibly presents provisions as review questions");

function obligationIds(result) {
  return new Set((result.obligations || []).map(item => item.obligation_id));
}

function evaluateInternal(jurisdiction, answers) {
  return globalThis.RegulaDecisionKernel.evaluateDecision(
    model, adapters.buildQuestionnaireRequest(jurisdiction, answers, NOW));
}

const ALL_QUESTION_IDS = {
  eu: ["deployment_eu", "is_ai_system", "role_provider", "role_deployer",
    "affected_domain", "significant_harm", "profiling", "narrow_procedural",
    "improves_human_activity", "pattern_detection", "preparatory_task",
    "social_scoring", "emotion_recognition", "public_facing", "biometric_data",
    "risk_documentation", "logging_active", "autonomous_decisions"],
  kr: ["kr_scope", "kr_is_ai_system", "kr_operator", "kr_provides",
    "kr_high_impact_domain", "kr_significant_impact", "kr_training_compute",
    "kr_frontier_technology", "kr_widespread_impact",
    "kr_transparency", "kr_generative", "kr_virtual_media", "kr_explanation",
    "kr_risk_management", "kr_human_oversight", "kr_foreign_operator",
    "kr_total_revenue", "kr_ai_services_revenue", "kr_domestic_users",
    "kr_admin_fine", "kr_representative"],
  co: ["co_scope", "co_is_ai_system", "co_doing_business", "co_personal_data",
    "co_decisions", "co_domain", "co_material", "co_excluded",
    "co_other_law_exemption", "co_role", "co_pre_notice", "co_adverse",
    "co_adverse_outcome", "co_consumer_rights"],
};

for (const jurisdiction of ["eu", "kr", "co"]) {
  const missing = adapters.evaluateQuestionnaireDecision(jurisdiction, {}, NOW);
  equal(missing.review_status, "insufficient_information",
    `${jurisdiction} missing answers remain unresolved`);
  check(missing.missing_context.every(item => item.reason === "absent"),
    `${jurisdiction} missing answers are absent, not defaulted`);
  check(missing.human_decision === null,
    `${jurisdiction} missing answers leave the human decision empty`);
  check(!Object.prototype.hasOwnProperty.call(missing, "result_type") &&
    !Object.prototype.hasOwnProperty.call(missing, "obligations"),
  `${jurisdiction} public result exposes no legal outcome fields`);

  const unsureAnswers = Object.fromEntries(
    ALL_QUESTION_IDS[jurisdiction].map(questionId => [questionId, "unsure"]));
  const unsure = adapters.evaluateQuestionnaireDecision(
    jurisdiction, unsureAnswers, NOW);
  equal(unsure.review_status, "insufficient_information",
    `${jurisdiction} all unsure cannot create a tier`);
  check(unsure.missing_context.every(
    item => ["explicit_unknown", "absent"].includes(item.reason)),
    `${jurisdiction} unsure remains explicit unknown where mapped`);
  check(!Object.prototype.hasOwnProperty.call(unsure, "confidence_score"),
    `${jurisdiction} has no numeric correctness probability`);
}

for (const jurisdiction of ["eu", "kr", "co"]) {
  const questions = ALL_QUESTION_IDS[jurisdiction].map(id => ({ id }));
  const answers = Object.fromEntries(questions.map((question, index) => [
    question.id,
    ["yes", "no", "unsure", "not_applicable"][index % 4],
  ]));
  const encoded = adapters.encodeAnswers(jurisdiction, answers, questions);
  check(encoded.startsWith("4."), `${jurisdiction} uses version 4 share encoding`);
  check(JSON.stringify(adapters.decodeAnswers(jurisdiction, encoded, questions)) ===
    JSON.stringify(answers), `${jurisdiction} version 4 share link round-trips all states`);
  const fullDecoded = adapters.decodeShare(jurisdiction, encoded, questions);
  check(JSON.stringify(fullDecoded.states) === JSON.stringify(answers),
    `${jurisdiction} complete evidence states round-trip exactly`);

  const partial = { [questions[0].id]: "yes", [questions[2].id]: "unsure" };
  const partialDecoded = adapters.decodeShare(
    jurisdiction, adapters.encodeAnswers(jurisdiction, partial, questions), questions);
  check(partialDecoded.ok, `${jurisdiction} partial share payload decodes`);
  check(JSON.stringify(partialDecoded.answers) === JSON.stringify(partial),
    `${jurisdiction} missing answers remain absent after round trip`);
  equal(partialDecoded.states[questions[1].id], "unanswered",
    `${jurisdiction} unanswered is distinct from explicit unsure`);
  equal(partialDecoded.states[questions[2].id], "unsure",
    `${jurisdiction} explicit unsure remains explicit unsure`);
  equal(partialDecoded.schema_version, 4,
    `${jurisdiction} decoded evidence records its schema version`);
  equal(partialDecoded.provenance.jurisdiction, jurisdiction,
    `${jurisdiction} decoded evidence records jurisdiction provenance`);

  const scopeOnly = { [questions[0].id]: "no" };
  const earlyExitDecoded = adapters.decodeShare(
    jurisdiction, adapters.encodeAnswers(jurisdiction, scopeOnly, questions), questions);
  check(JSON.stringify(earlyExitDecoded.answers) === JSON.stringify(scopeOnly),
    `${jurisdiction} early-exit evidence remains partial after round trip`);
}

const euQuestions = ALL_QUESTION_IDS.eu.map(id => ({ id }));
const contradictoryPayload = adapters.encodeAnswers("eu", {
  deployment_eu: "contradictory",
}, euQuestions);
const contradictoryDecoded = adapters.decodeShare("eu", contradictoryPayload, euQuestions);
equal(contradictoryDecoded.states.deployment_eu, "contradictory",
  "contradictory evidence is preserved by the versioned codec");
check(contradictoryDecoded.requires_manual_recovery,
  "contradictory shared evidence cannot be auto-evaluated");

const malformedV4 = adapters.decodeShare("eu", "4.not-base64!", euQuestions);
check(!malformedV4.ok && malformedV4.error === "malformed_payload",
  "malformed version 4 payload is rejected explicitly");
const unsupported = adapters.decodeShare("eu", "9.future", euQuestions);
check(!unsupported.ok && unsupported.error === "unsupported_version",
  "unsupported share version is rejected explicitly");
const wrongJurisdiction = adapters.decodeShare(
  "kr", adapters.encodeAnswers("eu", { deployment_eu: "yes" }, euQuestions),
  ALL_QUESTION_IDS.kr.map(id => ({ id })));
check(!wrongJurisdiction.ok && wrongJurisdiction.error === "jurisdiction_mismatch",
  "share evidence cannot be decoded under a different jurisdiction");

check(adapters.decodeShare("eu", "2yn", ALL_QUESTION_IDS.eu.map(id => ({ id }))).legacy,
  "legacy EU version 2 link is labelled as legacy");
check(adapters.decodeAnswers("eu", "2yn", ALL_QUESTION_IDS.eu.map(id => ({ id }))).deployment_eu === "yes",
  "legacy EU version 2 link decodes with legacy order");
check(adapters.decodeAnswers("kr", "yn", ALL_QUESTION_IDS.kr.map(id => ({ id }))).kr_high_impact_domain === "no",
  "legacy Korea link decodes with legacy order");
check(adapters.decodeAnswers("co", "yn", ALL_QUESTION_IDS.co.map(id => ({ id }))).co_decisions === "no",
  "legacy Colorado link decodes with legacy order");

const euAnswers = {
  deployment_eu: "yes",
  is_ai_system: "yes",
  role_provider: "yes",
  role_deployer: "no",
  affected_domain: "yes",
  significant_harm: "yes",
  profiling: "no",
  narrow_procedural: "no",
  improves_human_activity: "no",
  pattern_detection: "no",
  preparatory_task: "no",
  social_scoring: "no",
  emotion_recognition: "no",
};
const eu = evaluateInternal("eu", euAnswers);
equal(eu.result_type, "indication", "internal EU Article 6 facts indicate");
check(eu.indications.some(item => item.predicate_id === "eu_high_risk_annex_iii"),
  "EU result cites the satisfied Article 6 path");
check(obligationIds(eu).has("eu_requirement_9"),
  "EU result attaches Article 9 through a satisfied edge");
const euPublic = adapters.evaluateQuestionnaireDecision("eu", euAnswers, NOW);
equal(euPublic.review_status, "human_review_required",
  "public EU result requires accountable review");
check(euPublic.human_decision === null && euPublic.potentially_relevant_provisions.length > 0,
  "public EU result preserves provisions but no completed decision");
check(!Object.prototype.hasOwnProperty.call(euPublic, "indications") &&
  !Object.prototype.hasOwnProperty.call(euPublic, "obligations"),
  "internal EU legal outcomes do not escape the browser adapter");

const krAnswers = {
  kr_scope: "yes",
  kr_is_ai_system: "yes",
  kr_operator: "yes",
  kr_provides: "yes",
  kr_high_impact_domain: "yes",
  kr_significant_impact: "yes",
  kr_training_compute: "no",
  kr_frontier_technology: "no",
  kr_widespread_impact: "no",
  kr_generative: "no",
  kr_virtual_media: "no",
  kr_foreign_operator: "no",
  kr_total_revenue: "no",
  kr_ai_services_revenue: "no",
  kr_domestic_users: "no",
  kr_admin_fine: "no",
};
const kr = evaluateInternal("kr", krAnswers);
equal(kr.result_type, "indication", "resolved Korea facts indicate");
check(obligationIds(kr).has("kr_review_33"),
  "Korea result includes advance Article 33 review");
check(obligationIds(kr).has("kr_risk_management_34"),
  "Korea result includes resolved Article 34 duty");

const krSafety = evaluateInternal("kr", {
  kr_scope: "yes",
  kr_is_ai_system: "yes",
  kr_operator: "yes",
  kr_provides: "yes",
  kr_training_compute: "yes",
  kr_frontier_technology: "yes",
  kr_widespread_impact: "yes",
});
check(obligationIds(krSafety).has("kr_safety_32_1"),
  "Korea adapter requires and maps all three Decree Article 24 criteria");

const krAgent = evaluateInternal("kr", {
  kr_scope: "yes",
  kr_is_ai_system: "yes",
  kr_operator: "yes",
  kr_foreign_operator: "yes",
  kr_domestic_users: "yes",
});
check(obligationIds(krAgent).has("kr_agent_36"),
  "Korea adapter maps each Decree Article 29 alternative independently");

const co = evaluateInternal("co", {
  co_scope: "yes",
  co_is_ai_system: "yes",
  co_doing_business: "yes",
  co_personal_data: "yes",
  co_decisions: "yes",
  co_domain: "yes",
  co_material: "yes",
  co_excluded: "no",
  co_other_law_exemption: "no",
  co_role: "no",
  co_adverse_outcome: "no",
});
equal(co.result_type, "indication", "resolved Colorado facts indicate");
check(obligationIds(co).has("co_notice_1704"),
  "Colorado deployer result includes point-of-interaction notice");
check(!obligationIds(co).has("co_adverse_disclosure_1704"),
  "Colorado result does not attach adverse-outcome duty when adverse outcome is no");

const outside = adapters.evaluateQuestionnaireDecision("eu", {
  deployment_eu: "yes",
  is_ai_system: "no",
}, NOW);
equal(outside.review_status, "human_review_required",
  "a negative self-report still requires accountable scope review");
check(outside.human_decision === null,
  "negative self-report cannot complete a non-applicability decision");
check(!Object.prototype.hasOwnProperty.call(outside, "outside_scope_basis") &&
  !Object.prototype.hasOwnProperty.call(outside, "obligations"),
  "outside-scope and duty outcomes do not escape the browser adapter");

// The question ids below are a copy of what the pages declare. A copy drifts:
// this list was missing autonomous_decisions while all three pages shipped it,
// and nothing caught that because no runner executed this file. The sync check
// compares the copy against the pages on every run so it cannot drift silently.
const QUESTION_ID_PATTERN = /\bid:\s*"([a-z0-9_]+)"/g;
const localeQuestionIds = {};
for (const localeFile of ["index.html", "de.html", "pt-br.html"]) {
  const html = fs.readFileSync(path.join(root, "site", "assess", localeFile), "utf8");
  localeQuestionIds[localeFile] = [...html.matchAll(QUESTION_ID_PATTERN)].map(m => m[1]);
}
const declaredIds = new Set(Object.values(ALL_QUESTION_IDS).flat());
const shippedIds = new Set(localeQuestionIds["index.html"]);
for (const id of shippedIds) {
  check(declaredIds.has(id), `test list covers shipped question id ${id}`);
}
for (const id of declaredIds) {
  check(shippedIds.has(id), `test list has no stale question id ${id}`);
}
// Locale parity: the same questions in the same order in all three pages.
for (const localeFile of ["de.html", "pt-br.html"]) {
  check(localeQuestionIds[localeFile].join(",") === localeQuestionIds["index.html"].join(","),
    `${localeFile} declares the same question ids in the same order as index.html`);
}

for (const localeFile of ["index.html", "de.html", "pt-br.html"]) {
  const html = fs.readFileSync(path.join(root, "site", "assess", localeFile), "utf8");
  // Flow control is shared. A page that re-declares it has forked again.
  for (const forked of ["function renderQuestion(", "function nextQuestion(",
    "function showResults(", "function saveProgress("]) {
    check(!html.includes(forked),
      `${localeFile} does not re-declare ${forked.slice(9, -1)} (shared in assess-flow.js)`);
  }
  for (const script of ["decision-model.js", "decision-kernel.js",
    "decision-adapters.js", "decision-ui.js", "assess-flow.js"]) {
    check(html.includes(`<script src="${script}"></script>`),
      `${localeFile} loads ${script}`);
  }
  check(!html.includes("function calculateResultsEU"),
    `${localeFile} has no copied EU engine`);
  check(!html.includes("function calculateResultsKR"),
    `${localeFile} has no copied Korea engine`);
  check(!html.includes("function calculateResultsCO"),
    `${localeFile} has no copied Colorado engine`);
  check(!html.includes("Questionnaire signal score"),
    `${localeFile} does not render a decision score`);
  for (const recoveryKey of ["legacy", "malformed_payload", "unsupported_version",
    "jurisdiction_mismatch", "question_set_mismatch", "contradictory"]) {
    check(html.includes(`${recoveryKey}:`),
      `${localeFile} provides localised recovery copy for ${recoveryKey}`);
  }
}

function makeFlowDom(search) {
  const elements = {};
  function element(id) {
    const item = {
      id,
      style: {},
      attributes: {},
      children: [],
      firstChild: null,
      classList: {
        values: new Set(),
        add(value) { this.values.add(value); },
        remove(value) { this.values.delete(value); },
        contains(value) { return this.values.has(value); },
      },
      setAttribute(name, value) { this.attributes[name] = String(value); },
      getAttribute(name) { return this.attributes[name]; },
      focus() { this.focused = true; },
      remove() { this.removed = true; },
      insertBefore(child) {
        this.children.unshift(child);
        this.firstChild = child;
        if (child.id) elements[child.id] = child;
      },
    };
    elements[id] = item;
    return item;
  }
  for (const id of ["jur-eu", "jur-kr", "jur-co", "jurisdictionInfo",
    "heroSection", "questionnaireSection", "resultsSection", "tierResult",
    "obligationsList", "nextStepsSection"]) element(id);
  const location = { search, pathname: "/assess/", origin: "https://example.test" };
  const history = { replaceState() {} };
  const document = {
    documentElement: { lang: "en" },
    getElementById(id) { return elements[id] || null; },
    querySelectorAll(selector) {
      return selector === ".jurisdiction-btn"
        ? [elements["jur-eu"], elements["jur-kr"], elements["jur-co"]] : [];
    },
    createElement() { return element(""); },
    addEventListener() {},
  };
  return { document, elements, history, location };
}

function installFlow(search, exportedAnswers) {
  const dom = makeFlowDom(search);
  global.document = dom.document;
  global.history = dom.history;
  global.location = dom.location;
  global.sessionStorage = { getItem() { return null; }, setItem() {}, removeItem() {} };
  global.window = {
    document: dom.document,
    history: dom.history,
    location: dom.location,
    scrollTo() {},
    RegulaDecisionAdapters: adapters,
    RegulaDecisionUI: {
      renderQuestionnaireResult() { dom.rendered = true; },
      exportResult(result, options) { exportedAnswers.value = options.answers; },
    },
  };
  const flow = require("../site/assess/assess-flow.js");
  flow.install({
    questions: Object.fromEntries(Object.entries(ALL_QUESTION_IDS).map(
      ([jurisdiction, ids]) => [jurisdiction, ids.map(id => ({ id }))])),
    jurisdictionInfo: {
      eu: { law: "EU", status: "current" },
      kr: { law: "KR", status: "current" },
      co: { law: "CO", status: "current" },
    },
    scopeQuestionId: { eu: "deployment_eu", kr: "kr_scope", co: "co_scope" },
    copy: {
      jurisdictionMeta: () => "meta",
      shareRecovery: {
        legacy: "legacy warning",
        malformed_payload: "malformed warning",
        unsupported_version: "unsupported warning",
        jurisdiction_mismatch: "jurisdiction warning",
        question_set_mismatch: "question warning",
        contradictory: "contradictory warning",
      },
    },
  });
  return dom;
}

const invalidFlowExport = { value: null };
const invalidFlow = installFlow("?r=4.not-base64!", invalidFlowExport);
equal(invalidFlow.elements.shareRecoveryMessage.textContent, "malformed warning",
  "malformed shared link produces a visible recovery message");
equal(invalidFlow.elements.shareRecoveryMessage.attributes.role, "alert",
  "malformed shared link recovery is announced as an alert");
check(!invalidFlow.rendered, "malformed shared link does not manufacture a result");

const partialForFlow = { deployment_eu: "no", is_ai_system: "unsure" };
const partialCodeForFlow = adapters.encodeAnswers("eu", partialForFlow, euQuestions);
const partialFlowExport = { value: null };
const partialFlow = installFlow(`?r=${partialCodeForFlow}`, partialFlowExport);
check(partialFlow.rendered, "valid partial shared evidence renders a result");
global.window.exportJSON();
check(JSON.stringify(partialFlowExport.value) === JSON.stringify(partialForFlow),
  "production flow exports the same partial answer object that was shared");

const legacyFlowExport = { value: null };
const legacyFlow = installFlow("?r=2yn", legacyFlowExport);
check(legacyFlow.rendered, "legacy shared evidence is decoded through compatibility path");
equal(legacyFlow.elements.shareRecoveryMessage.textContent, "legacy warning",
  "legacy shared evidence displays its lossy-format warning");
equal(legacyFlow.elements.shareRecoveryMessage.attributes.role, "status",
  "legacy warning is announced without presenting a malformed-link error");

console.log(JSON.stringify({
  model_version: model.model_version,
  assertions: passed + failures.length,
  passed,
  failed: failures.length,
}, null, 2));
for (const failure of failures) console.error(failure);
process.exit(failures.length ? 1 : 0);
