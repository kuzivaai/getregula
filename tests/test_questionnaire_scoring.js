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
check(decisionUiSource.includes("indication.applicability_note"),
  "browser result cards visibly preserve rule applicability notes");
check(decisionUiSource.includes("obligation.applicability_note"),
  "browser obligation cards visibly preserve transition and applicability notes");

function obligationIds(result) {
  return new Set((result.obligations || []).map(item => item.obligation_id));
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
  equal(missing.result_type, "insufficient_information",
    `${jurisdiction} missing answers remain unresolved`);
  check(missing.unresolved_predicates.every(item => item.reason === "absent"),
    `${jurisdiction} missing answers are absent, not defaulted`);
  check(!Object.prototype.hasOwnProperty.call(missing, "obligations"),
    `${jurisdiction} missing answers emit no obligations`);

  const unsureAnswers = Object.fromEntries(
    ALL_QUESTION_IDS[jurisdiction].map(questionId => [questionId, "unsure"]));
  const unsure = adapters.evaluateQuestionnaireDecision(
    jurisdiction, unsureAnswers, NOW);
  equal(unsure.result_type, "insufficient_information",
    `${jurisdiction} all unsure cannot create a tier`);
  check(unsure.unresolved_predicates.every(
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
  check(encoded.startsWith("3"), `${jurisdiction} uses version 3 share encoding`);
  check(JSON.stringify(adapters.decodeAnswers(jurisdiction, encoded, questions)) ===
    JSON.stringify(answers), `${jurisdiction} version 3 share link round-trips all states`);
}

check(adapters.decodeAnswers("eu", "2yn", ALL_QUESTION_IDS.eu.map(id => ({ id }))).deployment_eu === "yes",
  "legacy EU version 2 link decodes with legacy order");
check(adapters.decodeAnswers("kr", "yn", ALL_QUESTION_IDS.kr.map(id => ({ id }))).kr_high_impact_domain === "no",
  "legacy Korea link decodes with legacy order");
check(adapters.decodeAnswers("co", "yn", ALL_QUESTION_IDS.co.map(id => ({ id }))).co_decisions === "no",
  "legacy Colorado link decodes with legacy order");

const eu = adapters.evaluateQuestionnaireDecision("eu", {
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
}, NOW);
equal(eu.result_type, "indication", "resolved EU Article 6 facts indicate");
check(eu.indications.some(item => item.predicate_id === "eu_high_risk_annex_iii"),
  "EU result cites the satisfied Article 6 path");
check(obligationIds(eu).has("eu_requirement_9"),
  "EU result attaches Article 9 through a satisfied edge");

const kr = adapters.evaluateQuestionnaireDecision("kr", {
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
}, NOW);
equal(kr.result_type, "indication", "resolved Korea facts indicate");
check(obligationIds(kr).has("kr_review_33"),
  "Korea result includes advance Article 33 review");
check(obligationIds(kr).has("kr_risk_management_34"),
  "Korea result includes resolved Article 34 duty");

const krSafety = adapters.evaluateQuestionnaireDecision("kr", {
  kr_scope: "yes",
  kr_is_ai_system: "yes",
  kr_operator: "yes",
  kr_provides: "yes",
  kr_training_compute: "yes",
  kr_frontier_technology: "yes",
  kr_widespread_impact: "yes",
}, NOW);
check(obligationIds(krSafety).has("kr_safety_32_1"),
  "Korea adapter requires and maps all three Decree Article 24 criteria");

const krAgent = adapters.evaluateQuestionnaireDecision("kr", {
  kr_scope: "yes",
  kr_is_ai_system: "yes",
  kr_operator: "yes",
  kr_foreign_operator: "yes",
  kr_domestic_users: "yes",
}, NOW);
check(obligationIds(krAgent).has("kr_agent_36"),
  "Korea adapter maps each Decree Article 29 alternative independently");

const co = adapters.evaluateQuestionnaireDecision("co", {
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
}, NOW);
equal(co.result_type, "indication", "resolved Colorado facts indicate");
check(obligationIds(co).has("co_notice_1704"),
  "Colorado deployer result includes point-of-interaction notice");
check(!obligationIds(co).has("co_adverse_disclosure_1704"),
  "Colorado result does not attach adverse-outcome duty when adverse outcome is no");

const outside = adapters.evaluateQuestionnaireDecision("eu", {
  deployment_eu: "yes",
  is_ai_system: "no",
}, NOW);
equal(outside.result_type, "outside_scope_candidate",
  "not an AI system resolves outside EU scope");
check(!Object.prototype.hasOwnProperty.call(outside, "obligations"),
  "not an AI system receives no Article 9 to 17 obligations");

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
}

console.log(JSON.stringify({
  model_version: model.model_version,
  assertions: passed + failures.length,
  passed,
  failed: failures.length,
}, null, 2));
for (const failure of failures) console.error(failure);
process.exit(failures.length ? 1 : 0);
