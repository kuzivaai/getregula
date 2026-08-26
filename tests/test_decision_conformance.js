#!/usr/bin/env node
"use strict";

const fs = require("fs");
const crypto = require("crypto");
const path = require("path");
const util = require("util");
const root = path.resolve(__dirname, "..");
const model = require(path.join(root, "site", "assess", "decision-model.js"));
const { DecisionInputError, evaluateDecision } = require(
  path.join(root, "site", "assess", "decision-kernel.js"));
const manifest = JSON.parse(fs.readFileSync(
  path.join(root, "references", "decision_conformance.v1.json"), "utf8"));
const vectors = manifest.shards.flatMap((entry, index) => {
  const raw = fs.readFileSync(path.join(root, "references", entry.file));
  if (raw.length !== entry.bytes) {
    throw new Error(`${entry.file}: byte count differs from manifest`);
  }
  const sha256 = crypto.createHash("sha256").update(raw).digest("hex");
  if (sha256 !== entry.sha256) {
    throw new Error(`${entry.file}: SHA-256 differs from manifest`);
  }
  const shard = JSON.parse(raw.toString("utf8"));
  if (shard.shard_index !== index ||
      shard.model_version !== manifest.model_version ||
      shard.vectors.length !== entry.vector_count) {
    throw new Error(`${entry.file}: shard metadata differs from manifest`);
  }
  return shard.vectors;
});
const corpus = {...manifest, vectors};

let passed = 0;
const failures = [];
for (const vector of corpus.vectors) {
  try {
    const actual = evaluateDecision(model, vector.request);
    if (vector.expected.error) {
      failures.push(`${vector.id}: expected ${vector.expected.error}, returned a result`);
    } else if (!util.isDeepStrictEqual(actual, vector.expected.result)) {
      failures.push(`${vector.id}: semantic result differs from corpus`);
    } else {
      passed += 1;
    }
  } catch (error) {
    if (vector.expected.error && error instanceof DecisionInputError &&
        error.constructor.name === vector.expected.error) {
      passed += 1;
    } else {
      failures.push(`${vector.id}: unexpected ${error.stack || error}`);
    }
  }
}

console.log(JSON.stringify({
  model_version: corpus.model_version,
  vectors: corpus.vectors.length,
  passed,
  failed: failures.length,
  reconciled: passed + failures.length === corpus.vectors.length,
}, null, 2));
if (failures.length) {
  failures.forEach(failure => console.error(failure));
  process.exit(1);
}
