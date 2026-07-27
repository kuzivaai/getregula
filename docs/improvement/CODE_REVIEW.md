# Phase 1 — Exhaustive Code Review

Branch `improvement/2026-08-programme`, baseline commit `d4180e3`.
Phase 1 changes no product code. Every finding carries a severity and the
rubric dimension it bears on.

Severity: **HIGH** (ships incorrect behaviour or a false claim to users) /
**MEDIUM** (real defect, contained blast radius) / **LOW** (hygiene).

Evidence tags: **MEASURED** / **VERIFIED** / **JUDGEMENT**.

---

## 1. Classification layer — false-positive taxonomy

Full structured output: `docs/improvement/fp_taxonomy.json` (commit
`1356f97`). Derived from `benchmarks/results/random_corpus/BLIND_LABELS.json`.

### 1.1 Corpus-scope correction (MEASURED)

`PRECISION.json` reports `high_risk` n=6 (tp=2, fp=4). That is the
**post-domain-gating production subset** of N=115. The full 201-entry
labelled set contains **24 high-risk false positives** and 98 false
positives across all tiers.

Both numbers are correct for their scope; quoting either without its
scope misstates the tool. The programme's requirement to trace ">=10 real
high-risk false positives" is satisfiable only from the full set — it
would have been impossible from the N=115 subset. **Severity: MEDIUM
(claim clarity). Dimension: Detection efficacy, Trust.**

### 1.2 The failures are semantic, not lexical (the central finding)

All 24 high-risk FPs classify into five causal classes:

| Class | Count | Example |
|---|---|---|
| Generative-model infra read as regulated domain | 7 | `finetrainers/models/cogview4/control_specification.py` → "Critical infrastructure management" |
| Non-production context | 6 | `tutorials/tutorial15/tutorial.ipynb`, `.dev/previous_versions/…` |
| Domain-word collision | 4 | `simpletuner/helpers/data_backend/factory.py` → "Safety components" |
| Compute-vs-human homonym | 4 | `fastdeploy/worker/worker_process.py` → "Worker monitoring and task allocation" |
| Modality confusion | 3 | `lhotse/recipes/this_american_life.py` (podcast dataset) → "Biometric identification" |

The causal patterns were traced to `risk_patterns.HIGH_RISK_PATTERNS`.
They are **well-anchored and lexically correct**. For example
`high_risk__worker_management` includes `\btask[_\W]?allocation`, and
"task allocation" is genuine Annex III 4(b) statutory language. The
failure is that the identical term means "distributing compute tasks" in
ML code. Likewise `critical_infrastructure` matches
`(?:grid|substation|…)[_\W]?(?:load|forecast|…)`, which collides with
ordinary ML "load" and "forecast" vocabulary.

**Consequence, and it constrains the whole improvement plan:** tightening
these regexes cannot fix this class without destroying recall on genuine
cases, because the tokens are the statute's own words. The fix space is
*context*, not *pattern*: package-level domain classification,
co-occurrence requirements, path scoping, or an optional semantic
verification tier. **Severity: HIGH. Dimension: Detection efficacy.**

This is direct evidence for the Phase 3 precision-stack item and direct
evidence *against* any plan whose main lever is "write better regexes".

---

## 2. Evidence outputs validated against their specs

Each output was generated from `benchmarks/synthetic/fixtures` and
validated against the authoritative published schema fetched live on
2026-07-27.

| Output | Spec | Result |
|---|---|---|
| SARIF | OASIS `sarif-schema-2.1.0.json` | **0 validation errors** (1 run, 13 results, `$schema` present) MEASURED |
| Evidence-pack manifest | `docs/spec/regula.manifest.v1.schema.json` | **0 validation errors** MEASURED |
| Evidence-pack integrity | own `verify` command | **Correct.** Clean pack: 9/9 verified, rc=0. After a one-line tamper: 8/9, "Pack integrity compromised. Do not submit to auditor.", **rc=1** MEASURED |
| DPV-AIAct vocabulary | `w3id.org/dpv/legal/eu/aiact` | resolves **HTTP 200**; canonical CG page 200; `w3id.org/dpv` 200 MEASURED |
| ELI ontology | `data.europa.eu/eli/ontology` | resolves **HTTP 200** MEASURED |
| **CycloneDX 1.7 ML-BOM** | official `bom-1.7.schema.json` | **1 validation error — FAILS** MEASURED |

### 2.1 HIGH — CycloneDX ML-BOM fails official schema validation

MEASURED. Regula emits:

```json
"modelCard": {"modelParameters": {"owner": "OpenAI"}}
```

The CycloneDX schema defines `modelCard.modelParameters` with
`additionalProperties: false` and exactly these permitted properties:
`approach, architectureFamily, datasets, inputs, modelArchitecture,
outputs, task`. **`owner` is not among them**, so a strict validator
rejects the document:

```
['components', 0, 'modelCard', 'modelParameters']
Additional properties are not allowed ('owner' was unexpected)
```

Source: `scripts/sbom.py:550` (`model_params["owner"] = provider`).

**This was never valid.** The same property set and
`additionalProperties: false` apply in CycloneDX **1.6** (VERIFIED
2026-07-27 against `bom-1.6.schema.json`), so this is a long-standing
defect, not a 1.6→1.7 migration regression. The adjacent comment at
`scripts/sbom.py:547` still reads "CycloneDX 1.6 modelCard", indicating
the block was not revisited when `specVersion` moved to 1.7.

Why it matters disproportionately: Regula's differentiator is
standards-conformant, auditable evidence. An ML-BOM that fails the
official schema is the one defect class the product cannot afford.
Provider information does have valid homes in the spec (component
`authors` / `manufacturer`, or `properties`); the fix is placement, not
removal.

**Severity: HIGH. Dimension: Trust & integrity, Problem altitude.**

### 2.2 Structural gap — nothing validates these outputs in CI

No test validates generated SARIF, ML-BOM or manifests against the
published schemas. `jsonschema` is not a dependency (correct: stdlib-only
core), which is precisely why validation belongs in a **dev/CI test**
with vendored schema snapshots, mirroring the existing checked-in
vocabulary-snapshot pattern (`scripts/dpv_data/`, `scripts/eli_data/`).
Had such a test existed, §2.1 would have been caught at authoring time.
**Severity: HIGH. Dimension: Trust & integrity.**

---

## 3. Methodology note recorded against myself

While measuring §2, I initially reported that `verify` returned exit code
0 on a tampered pack — a HIGH finding. It was wrong: I had piped the
command into `tail`, so `$?` was `tail`'s status, not the CLI's. Measured
without the pipe, `verify` correctly returns **1**.

This is the exact failure mode the project's own discipline names ("a
piped exit code is not an exit code; use PIPESTATUS"). It is recorded
here rather than quietly deleted because Phase 6 requires an anti-gaming
audit, and an instrument error that would have inflated the findings
count is precisely the kind of thing that must survive into the record.

---

## 4. Sections pending

Architecture / call-graph map, per-language regex-quality audit,
crosswalk audit, test-suite audit, security pass and repo hygiene are in
progress (two audit subagents dispatched; results appended on return).
