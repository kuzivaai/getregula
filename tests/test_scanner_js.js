#!/usr/bin/env node
// test_scanner_js.js — Tests for site/assess/scanner.js (648 detection patterns)
// Verifies parity with Python CLI classifications on all 13 benchmark fixtures.
// Run: node tests/test_scanner_js.js

'use strict';

const fs = require('fs');
const path = require('path');

const scannerPath = path.join(__dirname, '..', 'site', 'assess', 'scanner.js');
const { classifyCode, scanCode, isAiRelated, detectLanguage, stripComments } = require(scannerPath);

let passed = 0;
let failed = 0;
const failures = [];

function assert(condition, msg) {
  if (condition) {
    passed++;
  } else {
    failed++;
    failures.push(msg);
  }
}

function assertEq(actual, expected, msg) {
  if (actual === expected) {
    passed++;
  } else {
    failed++;
    failures.push(`${msg}: expected '${expected}', got '${actual}'`);
  }
}

function assertIn(value, list, msg) {
  if (list.includes(value)) {
    passed++;
  } else {
    failed++;
    failures.push(`${msg}: '${value}' not in [${list.join(', ')}]`);
  }
}

// =====================================================================
// Load benchmark fixtures
// =====================================================================

const fixturesDir = path.join(__dirname, '..', 'benchmarks', 'synthetic', 'fixtures');

function loadFixture(name) {
  return fs.readFileSync(path.join(fixturesDir, name), 'utf-8');
}

// =====================================================================
// 1. Benchmark parity tests — 13 fixtures
// =====================================================================

console.log('\n── Benchmark fixture parity (13 tests) ──\n');

// Prohibited fixtures
const prohibitedFixtures = [
  'prohibited_art5_1a.py',
  'prohibited_art5_1b.py',
  'prohibited_art5_1c.py',
  'prohibited_art5_1d.py',
  'prohibited_art5_1e.py',
];

for (const fixture of prohibitedFixtures) {
  const code = loadFixture(fixture);
  const result = classifyCode(code, 'python');
  assertEq(result.tier, 'prohibited', `${fixture} → prohibited`);
  console.log(`  ${result.tier === 'prohibited' ? 'PASS' : 'FAIL'}  ${fixture} → ${result.tier}`);
}

// High-risk fixtures
const highRiskFixtures = [
  'highrisk_biometrics.py',
  'highrisk_credit.py',
  'highrisk_employment.py',
  'highrisk_medical.py',
  'highrisk_migration.py',
];

for (const fixture of highRiskFixtures) {
  const code = loadFixture(fixture);
  const result = classifyCode(code, 'python');
  assertEq(result.tier, 'high_risk', `${fixture} → high_risk`);
  console.log(`  ${result.tier === 'high_risk' ? 'PASS' : 'FAIL'}  ${fixture} → ${result.tier}`);
}

// Negative: chatbot → limited_risk
{
  const code = loadFixture('negative_chatbot.py');
  const result = classifyCode(code, 'python');
  assertEq(result.tier, 'limited_risk', 'negative_chatbot.py → limited_risk');
  console.log(`  ${result.tier === 'limited_risk' ? 'PASS' : 'FAIL'}  negative_chatbot.py → ${result.tier}`);
}

// Negative: minimal_ai → minimal_risk or limited_risk
{
  const code = loadFixture('negative_minimal_ai.py');
  const result = classifyCode(code, 'python');
  assertIn(result.tier, ['minimal_risk', 'limited_risk'], 'negative_minimal_ai.py → minimal/limited');
  console.log(`  ${['minimal_risk', 'limited_risk'].includes(result.tier) ? 'PASS' : 'FAIL'}  negative_minimal_ai.py → ${result.tier}`);
}

// Negative: pure utility → not prohibited or high_risk (fixture allows not_ai or minimal_risk)
{
  const code = loadFixture('negative_pure_utility.py');
  const result = classifyCode(code, 'python');
  assertIn(result.tier, ['not_ai', 'minimal_risk'], 'negative_pure_utility.py → not_ai/minimal');
  assert(result.tier !== 'prohibited', 'negative_pure_utility.py not prohibited');
  assert(result.tier !== 'high_risk', 'negative_pure_utility.py not high_risk');
  console.log(`  ${!['prohibited', 'high_risk'].includes(result.tier) ? 'PASS' : 'FAIL'}  negative_pure_utility.py → ${result.tier}`);
}

// =====================================================================
// 2. scanCode() integration tests
// =====================================================================

console.log('\n── scanCode() integration tests ──\n');

{
  const code = loadFixture('prohibited_art5_1c.py');
  const result = scanCode(code, 'scoring.py');
  assertEq(result.classification.tier, 'prohibited', 'scanCode prohibited returns correct tier');
  assert(Array.isArray(result.security), 'scanCode returns security array');
  assert(typeof result.is_training === 'boolean', 'scanCode returns is_training boolean');
  assert(typeof result.language === 'string', 'scanCode returns language string');
  console.log('  PASS  scanCode() returns complete result structure');
}

{
  const code = loadFixture('highrisk_biometrics.py');
  const result = scanCode(code, 'biometrics.py');
  assertEq(result.classification.tier, 'high_risk', 'scanCode high-risk returns correct tier');
  assert(Array.isArray(result.observations), 'scanCode high-risk includes observations');
  assert(Array.isArray(result.bias), 'scanCode high-risk includes bias');
  console.log('  PASS  scanCode() high-risk includes observations + bias');
}

{
  const code = loadFixture('negative_pure_utility.py');
  const result = scanCode(code, 'utils.py');
  assertIn(result.classification.tier, ['not_ai', 'minimal_risk'], 'scanCode utility returns not_ai/minimal');
  assert(result.classification.tier !== 'prohibited', 'scanCode utility not prohibited');
  assert(result.classification.tier !== 'high_risk', 'scanCode utility not high_risk');
  console.log('  PASS  scanCode() utility code returns safe tier');
}

// =====================================================================
// 3. isAiRelated() tests
// =====================================================================

console.log('\n── isAiRelated() tests ──\n');

{
  assert(isAiRelated('import torch\nmodel.predict(x)'), 'torch import is AI');
  assert(isAiRelated('from sklearn.ensemble import RandomForestClassifier'), 'sklearn is AI');
  assert(isAiRelated('import openai'), 'openai is AI');
  assert(isAiRelated('import tensorflow as tf'), 'tensorflow is AI');
  assert(isAiRelated('from transformers import pipeline'), 'transformers is AI');
  assert(!isAiRelated('def quicksort(arr):\n    return sorted(arr)'), 'quicksort is not AI');
  assert(!isAiRelated('console.log("hello world")'), 'hello world is not AI');
  assert(!isAiRelated('SELECT * FROM users WHERE id = 1'), 'SQL is not AI');
  console.log('  PASS  isAiRelated() correctly identifies AI/non-AI code');
}

// =====================================================================
// 4. detectLanguage() tests
// =====================================================================

console.log('\n── detectLanguage() tests ──\n');

{
  assertEq(detectLanguage('import os', 'app.py'), 'python', 'detect python from .py');
  assertEq(detectLanguage('const x = 1', 'app.js'), 'javascript', 'detect javascript from .js');
  assertEq(detectLanguage('const x: number = 1', 'app.ts'), 'typescript', 'detect typescript from .ts');
  assertEq(detectLanguage('public class Main {}', 'Main.java'), 'java', 'detect java from .java');
  assertEq(detectLanguage('package main', 'main.go'), 'go', 'detect go from .go');
  assertEq(detectLanguage('fn main() {}', 'main.rs'), 'rust', 'detect rust from .rs');
  console.log('  PASS  detectLanguage() handles all major extensions');
}

// =====================================================================
// 5. stripComments() tests
// =====================================================================

console.log('\n── stripComments() tests ──\n');

{
  const code = '# This is a comment\ndef foo():\n    pass  # inline comment';
  const stripped = stripComments(code, 'python');
  assert(!stripped.includes('This is a comment'), 'strips Python hash comments');
  assert(stripped.includes('def foo'), 'preserves code after stripping');
  console.log('  PASS  stripComments() handles Python comments');
}

{
  const code = '// JS comment\nconst x = 1;\n/* block comment */\nconst y = 2;';
  const stripped = stripComments(code, 'javascript');
  assert(!stripped.includes('JS comment'), 'strips JS line comments');
  assert(!stripped.includes('block comment'), 'strips JS block comments');
  assert(stripped.includes('const x'), 'preserves JS code');
  console.log('  PASS  stripComments() handles JavaScript comments');
}

// =====================================================================
// 6. Edge case tests
// =====================================================================

console.log('\n── Edge case tests ──\n');

{
  const result = classifyCode('', 'python');
  assertEq(result.tier, 'not_ai', 'empty string → not_ai');
  console.log('  PASS  empty input returns not_ai');
}

{
  const result = classifyCode('# just a comment\n# nothing here', 'python');
  assertEq(result.tier, 'not_ai', 'comments-only → not_ai');
  console.log('  PASS  comments-only input returns not_ai');
}

{
  // GPAI training detection
  const trainingCode = [
    'import torch',
    'from torch.utils.data import DataLoader',
    'model = torch.nn.Linear(10, 1)',
    'optimizer = torch.optim.Adam(model.parameters())',
    'for epoch in range(100):',
    '    for batch in DataLoader(dataset, batch_size=32):',
    '        loss = criterion(model(batch), labels)',
    '        loss.backward()',
    '        optimizer.step()',
  ].join('\n');
  const result = scanCode(trainingCode, 'train.py');
  assert(result.is_training === true, 'training code detected as training');
  console.log(`  ${result.is_training ? 'PASS' : 'FAIL'}  GPAI training detection works`);
}

{
  // Security patterns
  const insecureCode = [
    'import pickle',
    'import torch',
    '# Dangerous: loading untrusted model',
    'model = pickle.loads(user_input)',
    'data = torch.load(untrusted_file)',
  ].join('\n');
  const result = scanCode(insecureCode, 'loader.py');
  assert(result.security.length > 0, 'security findings detected in insecure code');
  console.log(`  ${result.security.length > 0 ? 'PASS' : 'FAIL'}  security patterns detected (${result.security.length} findings)`);
}

// =====================================================================
// 7. Multi-language classification tests
// =====================================================================

console.log('\n── Multi-language tests ──\n');

{
  const jsCode = [
    "const openai = require('openai');",
    'async function screenCandidate(resume) {',
    '  const result = await openai.chat.completions.create({',
    "    model: 'gpt-4',",
    "    messages: [{ role: 'user', content: 'Score this candidate: ' + resume }]",
    '  });',
    '  return rankCandidate(result);',
    '}',
    'function resumeScreen(resumes) {',
    '  return resumes.filter(r => screenCandidate(r).score > 0.7);',
    '}',
  ].join('\n');
  const result = classifyCode(jsCode, 'javascript');
  assertEq(result.tier, 'high_risk', 'JS employment screening → high_risk');
  console.log(`  ${result.tier === 'high_risk' ? 'PASS' : 'FAIL'}  JavaScript employment screening → ${result.tier}`);
}

{
  const goCode = [
    'package main',
    'import "github.com/sashabaranov/go-openai"',
    'func chatbotReply(msg string) string {',
    '    // Customer support chatbot',
    '    client := openai.NewClient("key")',
    '    resp, _ := client.CreateChatCompletion(ctx, openai.ChatCompletionRequest{',
    '        Model: "gpt-4",',
    '        Messages: []openai.ChatCompletionMessage{{Role: "user", Content: msg}},',
    '    })',
    '    return resp.Choices[0].Message.Content',
    '}',
  ].join('\n');
  const result = classifyCode(goCode, 'go');
  assertIn(result.tier, ['limited_risk', 'minimal_risk'], 'Go chatbot → limited/minimal');
  console.log(`  ${['limited_risk', 'minimal_risk'].includes(result.tier) ? 'PASS' : 'FAIL'}  Go chatbot → ${result.tier}`);
}

// =====================================================================
// Summary
// =====================================================================

console.log(`\n${'─'.repeat(50)}`);
console.log(`${passed + failed} tests: ${passed} passed, ${failed} failed`);

if (failures.length > 0) {
  console.log('\nFailures:');
  for (const f of failures) {
    console.log(`  ✗ ${f}`);
  }
  process.exit(1);
} else {
  console.log('');
  process.exit(0);
}
