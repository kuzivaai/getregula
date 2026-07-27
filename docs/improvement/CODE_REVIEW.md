# Phase 1 — Exhaustive Code Review

Branch `improvement/2026-08-programme`, baseline commit `d0c08a4`.
Phase 1 changes no product code. Every finding carries a severity and the
rubric dimension it bears on.

Severity: **HIGH** (ships incorrect behaviour or a false claim to users) /
**MEDIUM** (real defect, contained blast radius) / **LOW** (hygiene).

Evidence tags: **MEASURED** / **VERIFIED** / **JUDGEMENT**.

---

## 1. Classification layer — false-positive taxonomy

Full structured output: `docs/improvement/fp_taxonomy.json` (commit
`7a0e1c0`). Derived from `benchmarks/results/random_corpus/BLIND_LABELS.json`.

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

## 4. Crosswalk audit

**Storage.** `references/framework_crosswalk.yaml`, schema_version 2.3.
Structure is `mappings[article_N][framework_key]` — keyed by AI Act
article (articles 9-15, seven entries), with all framework keys nested
inside each article. Twelve further reference YAMLs hold framework-specific
detail (`iso_42001_mapping`, `owasp_llm_top10`, `mitre_atlas`,
`owasp_agentic_top10`, `en18228_mapping`, `en18282_mapping`, and others).

**Completeness against the 13 cited frameworks (MEASURED):**

| Coverage | Frameworks |
|---|---|
| 7/7 articles | cra, eu_ai_act, ico_ai, iso_27001, iso_42001, lgpd, marco_legal_ia, mitre_atlas, nist_ai_rmf, nist_csf, owasp_llm_top10, soc2 (12 of 13) |
| **5/7 articles** | **owasp_agentic** — absent from `article_11` and `article_12` |

`owasp_agentic` was the 13th framework added on 23 Jul 2026 and its
crosswalk rows for Articles 11 (technical documentation) and 12
(record-keeping) were never written. The count claim of "13 frameworks"
is true at the `_FRAMEWORK_KEYS` level (13 unique values, MEASURED) but
the underlying data is not uniformly populated. **Severity: MEDIUM.
Dimension: Problem altitude, Trust.**

**Staleness (MEASURED):**

| File | Stamp | Age at 28 Jul 2026 |
|---|---|---|
| `framework_crosswalk.yaml` | `last_updated: 2026-04-11` | **108 days** |
| gpai_code_of_practice, gpai_signatories, harmonised_standards, mitre_atlas, owasp_llm_top10 | 2026-07-22 | 6 days |
| en18228_mapping, en18282_mapping | 2026-06-11 | 47 days |
| article_obligations, risk_indicators, iso_42001_mapping, owasp_agentic_top10, framework_crosswalk (per-entry) | **no `verified_on` stamp at all** | unknown |

Two concrete staleness risks follow:

1. **The crosswalk predates the Digital Omnibus by three months.**
   Regulation (EU) 2026/1744 amended Article 11(1) to permit SMEs and
   small mid-caps to supply Annex IV technical documentation in
   simplified form (VERIFIED against the EUR-Lex text, 27 Jul 2026). The
   crosswalk's `article_11.eu_ai_act` entry still reads only "Technical
   documentation shall be drawn up before the system is placed on the
   market", with no simplified-documentation route. The delta-log
   correctly records the amendment; **the crosswalk does not consume the
   delta-log**, so the two can diverge silently. **Severity: MEDIUM.
   Dimension: Regulatory currency.**
2. **Five reference files carry no verification stamp**, so the
   re-verification cadence recorded in the handover cannot be enforced
   for them by any automated check.

**Design observation (JUDGEMENT).** The delta-log now knows, in
machine-readable form, that Article 11 changed on 2026-07-24. The
crosswalk records what Article 11 requires. Nothing connects them. Wiring
the delta-log so that a change to article N flags every crosswalk row for
article N is the concrete, cheap form of the "temporally aware classifier"
idea the programme asks to be assessed in Phase 3 item 6 — and this audit
is the evidence that the gap is real rather than hypothetical.

## 5. Detection layer — regex quality and test reach

### 5.1 HIGH — 46.8% of tier regexes are exercised by no test input

MEASURED. Method: every regex in `PROHIBITED_PATTERNS`,
`HIGH_RISK_PATTERNS`, `LIMITED_RISK_PATTERNS`, `AI_SECURITY_PATTERNS` and
`BIAS_RISK_PATTERNS` was compiled and searched against the concatenated
text of every file the test suite can feed the engine (103 files across
`tests/` and `benchmarks/synthetic/fixtures/`, 1,534,257 characters).

| Result | Count |
|---|---|
| Total tier regexes | 391 |
| Fail to compile | **0** (good) |
| **Never matched by any test input** | **183 (46.8%)** |

By tier variable: HIGH_RISK 117, AI_SECURITY 35, PROHIBITED 17,
LIMITED_RISK 8, BIAS_RISK 6. Full list:
`scratchpad/unexercised.json` (regenerate with the snippet in §5.3).

**The framing that matters: these patterns are not broken, they are
unguarded.** Verified behaviourally — the Article 5 NCII pattern
(`\bnudif`) is among the 183, and a live scan of a file containing
`def nudify_image(...)` correctly returns `tier: prohibited, "AI systems
generating non-consensual intimate imagery of identifiable…"`. The
detection works. What does not exist is any test that would notice if it
stopped working. A typo in that regex would ship, and all 2,849 tests
would still pass.

This is the sharpest available illustration of the Phase 0 point that
test *count* is not test *reach*: 2,849 passing tests coexist with nearly
half the detection surface having no behavioural guard.

The exposure is worst exactly where the stakes are highest. Among the 183
unexercised are the newest and most serious prohibitions:
`ncii_generation` (`\bnudif`, `\bundress…`) — the Article 5 prohibition
added by Regulation (EU) 2026/1744 — plus `social_scoring`
(`\bscore.{0,5}citizen`), `criminal_prediction`,
`emotion_inference_workplace`, `emotion_inference_education`,
`biometric_categorisation_sensitive` and `realtime_biometric_public`.

**Severity: HIGH. Dimension: Detection efficacy, Engineering craft.**

**Fix shape (for Phase 4, not done here):** a generated table-driven test
that, for every regex in the tier dictionaries, asserts at least one
positive fixture string matches and at least one near-miss does not. It
must be generated *from* the pattern dictionaries so it cannot drift, and
it must fail when a new pattern is added without fixtures — otherwise it
becomes exactly the kind of count-inflating test the programme forbids.

### 5.2 Anchoring quality (JUDGEMENT, sampled)

The patterns are better engineered than the false-positive rate suggests.
Sampled groups use `\b` word boundaries, bounded gaps (`.{0,40}`) rather
than unbounded `.*`, and non-capturing alternation — for example
`\b(?:employee|worker|staff)[_\W]?(?:monitor|surveil|track|rank|…)`.
Zero regexes fail to compile, and no catastrophic-backtracking construct
(nested unbounded quantifiers) was found in the sampled set.

This corroborates §1.2: the false positives are **not** caused by sloppy
regex authorship. They are caused by the statute's vocabulary colliding
with ordinary engineering vocabulary. Any plan that proposes "improve the
regexes" as its detection-efficacy lever is mis-targeted and should be
rejected at Phase 4.

### 5.3 Reproduction

The measurement in §5.1 is reproducible from the repo root; the script is
committed alongside this review as the basis for the Phase 4 generated
test, so the figure can be re-measured rather than trusted.

## 6. Sections pending

Architecture / call-graph map, per-language regex-quality audit,
crosswalk audit, test-suite audit, security pass and repo hygiene are in
progress (two audit subagents dispatched; results appended on return).
