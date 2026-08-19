#!/usr/bin/env node
// test_scanner_js.js — Tests for site/assess/scanner.js (648 detection patterns)
// Verifies Python↔browser parity across the complete canonical benchmark corpus.
// Run: node tests/test_scanner_js.js

'use strict';

const fs = require('fs');
const path = require('path');
const { spawnSync } = require('child_process');

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
const manifestPath = path.join(__dirname, '..', 'benchmarks', 'synthetic', 'manifest.json');
const repoRoot = path.join(__dirname, '..');

function loadFixture(name) {
  return fs.readFileSync(path.join(fixturesDir, name), 'utf-8');
}

// =====================================================================
// 1. Complete-corpus parity and label-fidelity measurement
// =====================================================================

console.log('\n── Complete benchmark parity (manifest-derived) ──\n');

const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf-8'));
const expectations = manifest.expectations;
const fixtureNames = Object.keys(expectations).sort();
const filesOnDisk = fs.readdirSync(fixturesDir).filter(name => name.endsWith('.py')).sort();

assertEq(fixtureNames.length, 38, 'canonical corpus size');
assertEq(fixtureNames.filter(name => expectations[name] === 'high_risk').length, 30, 'high-risk corpus size');
assertEq(fixtureNames.filter(name => expectations[name] === 'prohibited').length, 5, 'prohibited corpus size');
assertEq(fixtureNames.filter(name => expectations[name] === 'not_high').length, 3, 'negative corpus size');
assertEq(JSON.stringify(filesOnDisk), JSON.stringify(fixtureNames), 'manifest and fixture directory enumerate the same corpus');

const pythonProbe = String.raw`
import json
import sys
from pathlib import Path

root = Path.cwd()
sys.path.insert(0, str(root / "scripts"))
from classify_risk import classify

manifest = json.loads((root / "benchmarks/synthetic/manifest.json").read_text(encoding="utf-8"))
fixtures = root / "benchmarks/synthetic/fixtures"
out = {}
for name in sorted(manifest["expectations"]):
    result = classify((fixtures / name).read_text(encoding="utf-8"), "python")
    out[name] = {
        "tier": result.tier.value,
        "indicators": sorted(result.indicators_matched),
    }
print(json.dumps(out, sort_keys=True))
`;
const pythonRun = spawnSync('python3', ['-c', pythonProbe], {
  cwd: repoRoot,
  encoding: 'utf-8',
  env: { ...process.env, REGULA_POLICY: path.join(repoRoot, 'configs', 'regula-policy.yaml') },
});
assertEq(pythonRun.status, 0, `Python parity probe exits successfully${pythonRun.stderr ? ` (${pythonRun.stderr.trim()})` : ''}`);
let pythonResults = {};
try {
  pythonResults = JSON.parse(pythonRun.stdout);
} catch (error) {
  assert(false, `Python parity probe emitted valid JSON: ${error.message}`);
}

const pythonTierToDetector = {
  prohibited: 'article_5_pattern',
  high_risk: 'annex_iii_pattern',
  limited_risk: 'article_50_pattern',
  minimal_risk: 'no_elevated_pattern',
  not_ai: 'no_ai_pattern',
};
const labelExpectedClass = {
  prohibited: 'article_5_pattern',
  high_risk: 'annex_iii_pattern',
};
const labelStats = {
  prohibited: { exact: 0, total: 0 },
  high_risk: { exact: 0, total: 0, article5: 0, noAi: 0, other: 0 },
  not_high: { correct: 0, total: 0 },
};

for (const fixture of fixtureNames) {
  const expectedLabel = expectations[fixture];
  const result = classifyCode(loadFixture(fixture), 'python');
  const python = pythonResults[fixture];
  const expectedDetector = pythonTierToDetector[python.tier];
  const jsIndicators = [...result.indicators_matched].sort();

  assertEq(result.detector_class, expectedDetector, `${fixture} Python↔JavaScript detector class`);
  assertEq(JSON.stringify(jsIndicators), JSON.stringify(python.indicators), `${fixture} Python↔JavaScript indicators`);

  if (expectedLabel === 'not_high') {
    labelStats.not_high.total++;
    const correct = !['article_5_pattern', 'annex_iii_pattern'].includes(result.detector_class);
    if (correct) labelStats.not_high.correct++;
    assert(correct, `${fixture} negative fixture has no elevated detector class`);
  } else {
    const stats = labelStats[expectedLabel];
    stats.total++;
    if (result.detector_class === labelExpectedClass[expectedLabel]) stats.exact++;
    if (expectedLabel === 'high_risk' && result.detector_class !== 'annex_iii_pattern') {
      if (result.detector_class === 'article_5_pattern') stats.article5++;
      else if (result.detector_class === 'no_ai_pattern') stats.noAi++;
      else stats.other++;
    }
  }
  console.log(`  PARITY  ${fixture}: label=${expectedLabel}, detector=${result.detector_class}`);
}

// This is a non-regression floor, not an accuracy claim. The corpus is small,
// synthetic, and maintained by this project. Improvements may raise the count;
// a representative independently-labelled corpus is still required.
assert(labelStats.high_risk.exact >= 18, 'high-risk label fidelity has not regressed below the measured 18/30 synthetic baseline');
assertEq(labelStats.prohibited.exact, labelStats.prohibited.total, 'all prohibited labels retain exact detector agreement');

console.log('\n  Runtime parity: 38/38 fixtures compared, including all 30 high-risk fixtures');
console.log(`  Label fidelity (not real-world accuracy): prohibited ${labelStats.prohibited.exact}/${labelStats.prohibited.total}; high-risk ${labelStats.high_risk.exact}/${labelStats.high_risk.total}; negatives ${labelStats.not_high.correct}/${labelStats.not_high.total}`);
console.log(`  High-risk disagreements: ${labelStats.high_risk.article5} article_5_pattern; ${labelStats.high_risk.noAi} no_ai_pattern; ${labelStats.high_risk.other} other`);

// =====================================================================
// 2. scanCode() integration tests
// =====================================================================

console.log('\n── scanCode() integration tests ──\n');

{
  const code = loadFixture('prohibited_art5_1c.py');
  const result = scanCode(code, 'scoring.py');
  assertEq(result.classification.detector_class, 'article_5_pattern', 'scanCode article_5_pattern returns correct tier');
  assert(Array.isArray(result.security), 'scanCode returns security array');
  assert(typeof result.is_training === 'boolean', 'scanCode returns is_training boolean');
  assert(typeof result.language === 'string', 'scanCode returns language string');
  console.log('  PASS  scanCode() returns complete result structure');
}

{
  const code = loadFixture('highrisk_biometrics.py');
  const result = scanCode(code, 'biometrics.py');
  assertEq(result.classification.detector_class, 'annex_iii_pattern', 'scanCode high-risk returns correct tier');
  assert(Array.isArray(result.observations), 'scanCode high-risk includes observations');
  assert(Array.isArray(result.bias), 'scanCode high-risk includes bias');
  console.log('  PASS  scanCode() high-risk includes observations + bias');
}

{
  const code = loadFixture('negative_pure_utility.py');
  const result = scanCode(code, 'utils.py');
  assertIn(result.classification.detector_class, ['no_ai_pattern', 'no_elevated_pattern'], 'scanCode utility returns no_ai_pattern/minimal');
  assert(result.classification.detector_class !== 'article_5_pattern', 'scanCode utility not article_5_pattern');
  assert(result.classification.detector_class !== 'annex_iii_pattern', 'scanCode utility not annex_iii_pattern');
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
  assertEq(result.detector_class, 'no_ai_pattern', 'empty string → no_ai_pattern');
  assertEq(result.detector_priority, 0, 'empty input detector priority is zero');
  assert(!Object.prototype.hasOwnProperty.call(result, 'tier'), 'empty input emits no tier');
  assert(!Object.prototype.hasOwnProperty.call(result, 'confidence'), 'empty input emits no confidence label');
  assert(!Object.prototype.hasOwnProperty.call(result, 'confidence_score'), 'empty input emits no confidence score');
  console.log('  PASS  empty input returns no_ai_pattern');
}

{
  const result = classifyCode('import torch\nmodel.predict(candidate)', 'python');
  assert(typeof result.detector_priority === 'number', 'detector priority is numeric');
  assert(!Object.prototype.hasOwnProperty.call(result, 'tier'), 'detector emits no legal tier field');
  assert(!Object.prototype.hasOwnProperty.call(result, 'applicable_articles'), 'detector emits suggestions, not applicable articles');
  assert(Array.isArray(result.suggested_provisions), 'detector provides provisions for review');
}

{
  const result = classifyCode('# just a comment\n# nothing here', 'python');
  assertEq(result.detector_class, 'no_ai_pattern', 'comments-only → no_ai_pattern');
  console.log('  PASS  comments-only input returns no_ai_pattern');
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
  assertEq(result.detector_class, 'annex_iii_pattern', 'JS employment screening → annex_iii_pattern');
  console.log(`  ${result.detector_class === 'annex_iii_pattern' ? 'PASS' : 'FAIL'}  JavaScript employment screening → ${result.detector_class}`);
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
  assertIn(result.detector_class, ['article_50_pattern', 'no_elevated_pattern'], 'Go chatbot → limited/minimal');
  console.log(`  ${['article_50_pattern', 'no_elevated_pattern'].includes(result.detector_class) ? 'PASS' : 'FAIL'}  Go chatbot → ${result.detector_class}`);
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
