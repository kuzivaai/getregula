#!/usr/bin/env node
// test_questionnaire_scoring.js — Tests for /assess/ questionnaire calculateResults()
// Validates scoring logic, tier classification, and gap assessment.
// Run: node tests/test_questionnaire_scoring.js

'use strict';

// =====================================================================
// Extract scoring logic from index.html (inline JS)
// We reproduce the QUESTIONS and calculateResults() here since they
// are embedded in HTML, not a separate module.
// =====================================================================

const QUESTIONS = [
  { id: "deployment_eu", text: "EU deployment?", weight: { yes: 10, no: -10, unsure: 5 }, signal: "jurisdiction" },
  { id: "affected_domain", text: "Annex III domain?", weight: { yes: 25, no: -15, unsure: 10 }, signal: "high_risk" },
  { id: "autonomous_decisions", text: "Autonomous decisions?", weight: { yes: 30, no: -20, unsure: 10 }, signal: "high_risk" },
  { id: "significant_harm", text: "Significant harm?", weight: { yes: 25, no: -15, unsure: 10 }, signal: "high_risk" },
  { id: "biometric_data", text: "Biometric data?", weight: { yes: 20, no: -5, unsure: 10 }, signal: "high_risk" },
  { id: "social_scoring", text: "Evaluate individuals?", weight: { yes: 35, no: -5, unsure: 10 }, signal: "prohibited" },
  { id: "emotion_recognition", text: "Emotion recognition?", weight: { yes: 35, no: -5, unsure: 10 }, signal: "prohibited" },
  { id: "public_facing", text: "AI undisclosed?", weight: { yes: 15, no: -5, unsure: 5 }, signal: "transparency" },
  { id: "narrow_procedural", text: "Narrow procedural?", weight: { yes: -25, no: 10, unsure: 0 }, signal: "exemption" },
  { id: "improves_human_activity", text: "Improves human activity?", weight: { yes: -20, no: 5, unsure: 0 }, signal: "exemption" },
  { id: "pattern_detection", text: "Pattern detection for review?", weight: { yes: -20, no: 5, unsure: 0 }, signal: "exemption" },
  { id: "preparatory_task", text: "Preparatory task?", weight: { yes: -20, no: 5, unsure: 0 }, signal: "exemption" },
  { id: "risk_documentation", text: "Risk register?", weight: { yes: -5, no: 5, unsure: 0 }, signal: "gap_assessment" },
  { id: "logging_active", text: "Logging active?", weight: { yes: -5, no: 5, unsure: 0 }, signal: "gap_assessment" },
];

function calculateResults(answers) {
  let adjustment = 0;
  let prohibitedSignals = [];
  let highRiskSignals = [];
  let transparencySignals = [];
  let exemptionSignals = [];
  let gapSignals = {};

  for (const q of QUESTIONS) {
    const a = answers[q.id] || "unsure";
    adjustment += q.weight[a] || 0;

    if (q.signal === "prohibited" && a === "yes") prohibitedSignals.push(q.id);
    if (q.signal === "high_risk" && a === "yes") highRiskSignals.push(q.id);
    if (q.signal === "transparency" && a === "yes") transparencySignals.push(q.id);
    if (q.signal === "exemption" && a === "yes") exemptionSignals.push(q.id);
    if (q.signal === "gap_assessment") gapSignals[q.id] = a;
  }

  const score = Math.max(0, Math.min(100, 50 + Math.round(adjustment * 0.55)));

  let tier;
  if (prohibitedSignals.length > 0) {
    tier = "prohibited";
  } else if (score >= 65 && exemptionSignals.length === 0) {
    tier = "high_risk";
  } else if (score >= 65 && exemptionSignals.length > 0) {
    tier = "high_risk_exempt";
  } else if (score >= 35 || transparencySignals.length > 0) {
    tier = "limited_risk";
  } else {
    tier = "minimal_risk";
  }

  const gapScores = {
    9: gapSignals.risk_documentation === "yes" ? 60 : (gapSignals.risk_documentation === "unsure" ? 30 : 10),
    10: 20,
    11: 15,
    12: gapSignals.logging_active === "yes" ? 65 : (gapSignals.logging_active === "unsure" ? 30 : 10),
    13: answers.public_facing === "no" ? 50 : 15,
    14: answers.autonomous_decisions === "no" ? 70 : 25,
    15: 30,
  };

  return { tier, score, prohibitedSignals, highRiskSignals, exemptionSignals, transparencySignals, gapScores };
}

// =====================================================================
// Test harness
// =====================================================================

let passed = 0;
let failed = 0;
const failures = [];

function assertEq(actual, expected, msg) {
  if (actual === expected) { passed++; }
  else { failed++; failures.push(`${msg}: expected '${expected}', got '${actual}'`); }
}

function assert(condition, msg) {
  if (condition) { passed++; }
  else { failed++; failures.push(msg); }
}

// =====================================================================
// 1. Tier classification tests
// =====================================================================

console.log('\n── Tier classification tests ──\n');

// All "no" → minimal_risk (reversed polarity: public_facing=no means AI IS disclosed)
{
  const answers = {};
  QUESTIONS.forEach(q => answers[q.id] = 'no');
  const r = calculateResults(answers);
  assertEq(r.tier, 'minimal_risk', 'all no → minimal_risk');
  assert(r.score < 35, 'all no → score < 35');
  assertEq(r.transparencySignals.length, 0, 'all no → no transparency signal');
  console.log(`  PASS  all no → ${r.tier} (score: ${r.score})`);
}

// Prohibited: answering yes to evaluation question
{
  const answers = {};
  QUESTIONS.forEach(q => answers[q.id] = 'no');
  answers.social_scoring = 'yes';
  const r = calculateResults(answers);
  assertEq(r.tier, 'prohibited', 'prohibited signal → prohibited tier');
  assert(r.prohibitedSignals.length > 0, 'prohibited signals populated');
  console.log(`  PASS  prohibited signal → ${r.tier}`);
}

// Prohibited: emotion recognition
{
  const answers = {};
  QUESTIONS.forEach(q => answers[q.id] = 'no');
  answers.emotion_recognition = 'yes';
  const r = calculateResults(answers);
  assertEq(r.tier, 'prohibited', 'emotion recognition → prohibited');
  console.log(`  PASS  emotion recognition → ${r.tier}`);
}

// High-risk: EU deployment + Annex III domain + autonomous + significant harm
{
  const answers = {};
  QUESTIONS.forEach(q => answers[q.id] = 'no');
  answers.deployment_eu = 'yes';
  answers.affected_domain = 'yes';
  answers.autonomous_decisions = 'yes';
  answers.significant_harm = 'yes';
  const r = calculateResults(answers);
  assertEq(r.tier, 'high_risk', 'high-risk combination → high_risk');
  assert(r.score >= 65, 'high-risk score >= 65');
  console.log(`  PASS  high-risk combination → ${r.tier} (score: ${r.score})`);
}

// High-risk exempt: same as above but narrow procedural = yes
{
  const answers = {};
  QUESTIONS.forEach(q => answers[q.id] = 'no');
  answers.deployment_eu = 'yes';
  answers.affected_domain = 'yes';
  answers.autonomous_decisions = 'yes';
  answers.significant_harm = 'yes';
  answers.narrow_procedural = 'yes';
  const r = calculateResults(answers);
  assertEq(r.tier, 'high_risk_exempt', 'with exemption → high_risk_exempt');
  assert(r.exemptionSignals.length > 0, 'exemption signals populated');
  console.log(`  PASS  with exemption → ${r.tier}`);
}

// Limited risk: transparency signal (AI not disclosed — public_facing=yes means undisclosed)
{
  const answers = {};
  QUESTIONS.forEach(q => answers[q.id] = 'no');
  answers.deployment_eu = 'yes';
  answers.public_facing = 'yes';  // "Could interact without knowing" = yes → transparency signal
  const r = calculateResults(answers);
  assertEq(r.tier, 'limited_risk', 'transparency signal → limited_risk');
  assert(r.transparencySignals.length > 0, 'transparency signals populated');
  console.log(`  PASS  transparency signal → ${r.tier}`);
}

// All unsure → limited risk (cautious default)
{
  const answers = {};
  QUESTIONS.forEach(q => answers[q.id] = 'unsure');
  const r = calculateResults(answers);
  assertIn_tier(r.tier, ['limited_risk', 'high_risk'], 'all unsure → limited/high (cautious)');
  assert(r.score >= 35, 'all unsure → score >= 35 (cautious scoring)');
  console.log(`  PASS  all unsure → ${r.tier} (score: ${r.score})`);
}

function assertIn_tier(actual, list, msg) {
  if (list.includes(actual)) { passed++; }
  else { failed++; failures.push(`${msg}: '${actual}' not in [${list.join(', ')}]`); }
}

// =====================================================================
// 2. Score boundary tests
// =====================================================================

console.log('\n── Score boundary tests ──\n');

{
  const answers = {};
  QUESTIONS.forEach(q => answers[q.id] = 'no');
  const r = calculateResults(answers);
  assert(r.score >= 0 && r.score <= 100, 'all-no score in 0-100 range');
  console.log(`  PASS  all-no score: ${r.score} (valid range)`);
}

{
  const answers = {};
  QUESTIONS.forEach(q => answers[q.id] = 'yes');
  const r = calculateResults(answers);
  assert(r.score >= 0 && r.score <= 100, 'all-yes score in 0-100 range');
  console.log(`  PASS  all-yes score: ${r.score} (valid range)`);
}

// Prohibited takes precedence over score
{
  const answers = {};
  QUESTIONS.forEach(q => answers[q.id] = 'no');
  answers.social_scoring = 'yes';
  const r = calculateResults(answers);
  assertEq(r.tier, 'prohibited', 'prohibited overrides low score');
  console.log(`  PASS  prohibited overrides score (score: ${r.score}, tier: ${r.tier})`);
}

// =====================================================================
// 3. Gap assessment tests
// =====================================================================

console.log('\n── Gap assessment tests ──\n');

// Risk documentation: yes → 60
{
  const answers = {};
  QUESTIONS.forEach(q => answers[q.id] = 'no');
  answers.risk_documentation = 'yes';
  const r = calculateResults(answers);
  assertEq(r.gapScores[9], 60, 'risk_documentation yes → Art 9 gap 60');
  console.log(`  PASS  risk documentation yes → gap score ${r.gapScores[9]}`);
}

// Risk documentation: no → 10
{
  const answers = {};
  QUESTIONS.forEach(q => answers[q.id] = 'no');
  answers.risk_documentation = 'no';
  const r = calculateResults(answers);
  assertEq(r.gapScores[9], 10, 'risk_documentation no → Art 9 gap 10');
  console.log(`  PASS  risk documentation no → gap score ${r.gapScores[9]}`);
}

// Logging: yes → 65
{
  const answers = {};
  QUESTIONS.forEach(q => answers[q.id] = 'no');
  answers.logging_active = 'yes';
  const r = calculateResults(answers);
  assertEq(r.gapScores[12], 65, 'logging yes → Art 12 gap 65');
  console.log(`  PASS  logging yes → gap score ${r.gapScores[12]}`);
}

// Logging: no → 10
{
  const answers = {};
  QUESTIONS.forEach(q => answers[q.id] = 'no');
  answers.logging_active = 'no';
  const r = calculateResults(answers);
  assertEq(r.gapScores[12], 10, 'logging no → Art 12 gap 10');
  console.log(`  PASS  logging no → gap score ${r.gapScores[12]}`);
}

// Human oversight: autonomous=no → Art 14 gap 70
{
  const answers = {};
  QUESTIONS.forEach(q => answers[q.id] = 'no');
  answers.autonomous_decisions = 'no';
  const r = calculateResults(answers);
  assertEq(r.gapScores[14], 70, 'autonomous no → Art 14 gap 70');
  console.log(`  PASS  autonomous decisions no → Art 14 gap ${r.gapScores[14]}`);
}

// Human oversight: autonomous=yes → Art 14 gap 25
{
  const answers = {};
  QUESTIONS.forEach(q => answers[q.id] = 'no');
  answers.autonomous_decisions = 'yes';
  const r = calculateResults(answers);
  assertEq(r.gapScores[14], 25, 'autonomous yes → Art 14 gap 25');
  console.log(`  PASS  autonomous decisions yes → Art 14 gap ${r.gapScores[14]}`);
}

// Static gap scores (not assessable from questionnaire)
{
  const answers = {};
  QUESTIONS.forEach(q => answers[q.id] = 'no');
  const r = calculateResults(answers);
  assertEq(r.gapScores[10], 20, 'data governance static gap 20');
  assertEq(r.gapScores[11], 15, 'technical docs static gap 15');
  assertEq(r.gapScores[15], 30, 'robustness static gap 30');
  console.log(`  PASS  static gap scores correct (Art 10: 20, Art 11: 15, Art 15: 30)`);
}

// =====================================================================
// 4. Signal accumulation tests
// =====================================================================

console.log('\n── Signal accumulation tests ──\n');

// Multiple high-risk signals
{
  const answers = {};
  QUESTIONS.forEach(q => answers[q.id] = 'no');
  answers.affected_domain = 'yes';
  answers.autonomous_decisions = 'yes';
  answers.biometric_data = 'yes';
  const r = calculateResults(answers);
  assertEq(r.highRiskSignals.length, 3, '3 high-risk signals');
  console.log(`  PASS  3 high-risk signals accumulated (${r.highRiskSignals.join(', ')})`);
}

// Both prohibited signals
{
  const answers = {};
  QUESTIONS.forEach(q => answers[q.id] = 'no');
  answers.social_scoring = 'yes';
  answers.emotion_recognition = 'yes';
  const r = calculateResults(answers);
  assertEq(r.prohibitedSignals.length, 2, '2 prohibited signals');
  assertEq(r.tier, 'prohibited', 'multiple prohibited → prohibited');
  console.log(`  PASS  2 prohibited signals → ${r.tier}`);
}

// Missing answers default to unsure
{
  const r = calculateResults({});
  assert(r.score > 0, 'empty answers still produces valid score');
  assert(typeof r.tier === 'string', 'empty answers produces valid tier');
  console.log(`  PASS  empty answers → ${r.tier} (score: ${r.score})`);
}

// =====================================================================
// 5. Question count and structure
// =====================================================================

console.log('\n── Structure tests ──\n');

{
  assertEq(QUESTIONS.length, 14, 'exactly 14 questions');
  const signals = new Set(QUESTIONS.map(q => q.signal));
  assert(signals.has('jurisdiction'), 'has jurisdiction signal');
  assert(signals.has('high_risk'), 'has high_risk signal');
  assert(signals.has('prohibited'), 'has prohibited signal');
  assert(signals.has('transparency'), 'has transparency signal');
  assert(signals.has('exemption'), 'has exemption signal');
  assert(signals.has('gap_assessment'), 'has gap_assessment signal');
  console.log(`  PASS  14 questions across ${signals.size} signal types`);
}

{
  for (const q of QUESTIONS) {
    assert(typeof q.weight.yes === 'number', `${q.id} has numeric yes weight`);
    assert(typeof q.weight.no === 'number', `${q.id} has numeric no weight`);
    assert(typeof q.weight.unsure === 'number', `${q.id} has numeric unsure weight`);
  }
  console.log(`  PASS  all questions have valid weight structures`);
}

// =====================================================================
// Summary
// =====================================================================

console.log(`\n${'─'.repeat(50)}`);
console.log(`${passed + failed} tests: ${passed} passed, ${failed} failed`);

if (failures.length > 0) {
  console.log('\nFailures:');
  for (const f of failures) console.log(`  ✗ ${f}`);
  process.exit(1);
} else {
  console.log('');
  process.exit(0);
}
