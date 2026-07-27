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
standards-conformant, auditable evidence, generated by
[`scripts/sbom.py`](../../scripts/sbom.py). An ML-BOM that fails the
official schema (https://github.com/CycloneDX/specification) is the one
defect class the product cannot afford.
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

## 6. Security pass

MEASURED, with live controls rather than code reading alone.

| Surface | Result |
|---|---|
| `shell=True` anywhere in `scripts/` | **None.** No shell-interpolation command-injection surface |
| `os.system` / `eval(` / `exec(` | **None in executable code.** The single grep hit (`scripts/remediation.py:460`) is *advice text* warning users against `eval`/`exec` on model output |
| HTML report escaping, user-controlled **filename** | **Correctly escaped.** Control: a file literally named `evil"><img src=x onerror=alert(1)>.py` was scanned and reported; the raw payload appears **0** times in the HTML, escaped forms appear 4 times, and the filename is present, proving the path was exercised rather than dropped |
| HTML report echoing **source text** | Source content is not echoed into the report at all — finding descriptions come from the pattern catalogue, not the matched line. Removes that vector by design |
| PDF export escaping | `scripts/pdf_export.py` applies `html.escape` at lines 84, 127 and throughout the header block |
| Path traversal / hostile trees | Already covered by `scripts/scan_safety.py` (87.9% coverage) and `tests/test_hostile_sweep.py`, which guards both tree-as-argument and cwd-inside-tree; no new gap found this pass |

**No security defects found in this pass.** That is a genuine, if
unglamorous, result: the areas most likely to be weak in a report-generating
tool are sound.

### 6.1 Two instrument errors, recorded not deleted

Both would have produced false conclusions and were caught by insisting a
control prove the code path ran:

1. **False positive risk.** I first measured `verify` as returning exit
   code 0 on a tampered pack (a HIGH finding). Wrong: the command was
   piped into `tail`, so `$?` was `tail`'s status. Unpiped, it returns
   **1**, correctly.
2. **False negative risk.** My first two filename-XSS attempts silently
   never created the file — first shell quoting, then a payload
   containing `/` inside `</script>`, which cannot exist in a Linux
   filename. Both runs "found no vulnerability" while testing nothing.
   Only the third attempt, which asserted the filename was actually
   present in the output, was evidence of anything.

The pattern in both: an absent signal was nearly read as a clean result.
The countermeasure that worked was requiring positive proof the path
executed — the escaped-form count and the `'evil' in html` assertion.
Phase 6's anti-gaming audit inherits this: **a blank gate is not a green
gate**.

## 7. Architecture — the call graph is not what the module names suggest

Source: dedicated audit subagent, fresh context, read-only. Claims below
marked **[V]** were re-verified by me directly; the rest are the
subagent's with file:line evidence and are tagged REPORTED accordingly
(project rule: subagent output is not verified by default).

### 7.1 HIGH — two independent detection engines that never reconcile

`regula check` does **not** use the AST engine. Its path is
`cli.py:948 → cli_scan.cmd_check:252 → report.scan_files:519 →
classify_risk.classify:687`, which is pure regex matching over
`risk_patterns`. From `ast_engine.py` (1,915 lines) it imports exactly
one function, `detect_language` (`report.py:32`, used `report.py:937`);
`ast_analysis.py` is not reached by `check` at all. The AST engine serves
*other* commands — `gap`/`comply` (`compliance_check.py:69,72`),
`oversight` (`cross_file_flow.py:28,32`), `aibom`/`sbom` (`sbom.py:32`).

So Regula ships two detectors with different mechanisms over the same
code, and nothing reconciles their verdicts. This reframes the
documentation problem found in Phase 0 §4: "Python and JS/TS have full
AST" is true of `gap`, not of `check` — the command the quickstart leads
with. **Severity: HIGH. Dimension: Detection efficacy, Trust.**

### 7.2 HIGH — the scan cache leaks provenance across projects (REPORTED, high-confidence)

`ScanCache` (`scan_cache.py:48`) lives at `~/.regula/cache` and keys
entries on `{relative_path}:{schema}:{context}:{sha256(content)}`
(`scan_cache.py:69,73`) — **with no project root in the key**. Provenance
(`example` / `test` / `production`) is computed from the *absolute* path
(`report.py:182`) but is baked into the cached finding, so an identical
`app.py` in a different project replays the other project's provenance.

Observed effect: `check examples/cv-screening-app` returns 0 findings on
a cold cache (as [`README.md`](../../README.md) line 91 documents) but **1 high-risk finding labelled
`provenance: "production"`** on a warm one. This silently defeats
`--scope production` and is a cross-project information-flow issue in a
tool that promises nothing leaves the machine boundary it was scanned in.

I have not personally reproduced the warm-cache case (it requires the
specific cache state); the mechanism is legible in the source and the
reasoning is sound. **Marked REPORTED — reproduce before fixing.
Severity: HIGH if confirmed. Dimension: Detection efficacy, Trust.**

### 7.3 Other duplicate paths (REPORTED, file:line given)

- **Confidence bases defined twice with different values.**
  `classify_risk._CONFIDENCE_BASE` (`:118`) is 75/55/40/15;
  `report.py:985` overwrites it with 85/65/45/20. The first is dead in
  the `check` path.
- **Three callers of `scan_files` with three different defaults** —
  `cmd_check` (`skip_tests=True, min_tier=limited_risk, scope=production`),
  `cmd_report` (`skip_tests=False, min_tier="", scope=all`), and
  `_run_bare_scan` (all defaults). **This explains the Phase 0 §8 anomaly**
  where bare `regula` reported 136 files and `report.scan_files('.')`
  reported 222 for the same directory: they are different scans, not a
  measurement error. [V — consistent with my own measurement]
- **Two HTML report generators** (`pdf_export.generate_compliance_html_report`
  vs `report.generate_html_report`) with different layouts and inputs.
- **Domain gating implemented twice** — inline for fresh findings
  (`report.py:1120-1135`), `_check_domain_gated()` for cached
  (`report.py:504`).
- **No `.gitignore` handling exists in the scan path** at all; directory
  exclusion is `SKIP_DIRS`-only.

### 7.4 Packaging defects [V — verified directly against the built wheel]

- **`scripts/eli_data/eli_ontology_terms.json` is missing from the wheel.**
  `pyproject.toml:87` lists `bias_data/*.json` and `dpv_data/*.json` but
  not `eli_data/*.json`. `scripts/build_delta_dataset.py:59` reads it, so
  that script cannot work from an installed package. **This is my own
  defect, introduced on 27 Jul when I added the ELI snapshot without a
  packaging entry.** Severity: MEDIUM (dev tooling, not the scan path).
- **`scripts/dashboard/index.html` is missing from the wheel**, so
  `regula api-server` on a pip install serves no dashboard and falls back
  to a JSON stub (`api_server.py:418`) — while README:161 advertises
  "with web dashboard". Severity: MEDIUM. Dimension: Trust.
- The release workflow's wheel check asserts only 5 paths and would not
  have caught either.

### 7.5 README claims that do not match behaviour (REPORTED)

- `README.md:156` says `--ci` gives "SARIF output". It does not; `--ci`
  only forces strict mode (`cli_scan.py:370`) and format still defaults
  to text.
- `README.md:62` says `regula demo` "requires the cloned repo". It does
  not — `scripts/demos/` is bundled and release CI smoke-tests it from
  PyPI.
- `README.md:131` implies article-level jurisdiction mapping for Korea
  and Colorado. Domain-level obligations are produced, but the
  article-level crosswalk returns EU only, because `framework_mapper`
  deliberately removed those keys while `cli.JURISDICTION_MAP` still
  points at them — failing silently to `{}`.

### 7.6 Licence-header gap (REPORTED)

`pyproject.toml:13` declares a composite licence
(`(Apache-2.0 OR EUPL-1.2) AND LicenseRef-DRL-1.1`), but **0 of 119**
files carry an SPDX identifier or copyright notice; exactly one file
(`risk_patterns.py:7`) states its licence in prose. A downstream consumer
of any single file cannot tell which of the three terms applies. Relevant
to Principle 5 (licence hygiene) before any research code is adapted.

### 7.7 Dead code (REPORTED, with inbound-reference evidence)

`scripts/ci_heal.py` (588 lines) is the highest-confidence dead module:
its only repo reference is a CHANGELOG line pairing it with
`.github/workflows/self-heal.yaml`, which was deleted in `baec7c0`. Also
orphaned: `update_sitemap.py`, `demo_screenshots.py`, `make_og_uae.py`.

---

## 8. Test-suite audit — the suite is bimodal

Source: dedicated audit subagent, fresh context. Headline re-verified by
me directly.

### 8.1 CRITICAL — the published test count double-counts by 18.5% [V]

Independently MEASURED by me:

```
total collected node IDs                       2849
inside tests/test_classification.py             963
...duplicating a function in another module     527
=> unique test functions                       2322
```

Mechanism confirmed at `tests/test_classification.py:47-61`: every
fixture-less `test_*` from 22 modules is rebound into that module's
`globals()` so the custom runner's `globals()` walk finds them. pytest
collects those names again, so each is counted twice.

The figure is published on nine surfaces and enforced as canonical by
`claim_auditor.py:689`. **The drift-protection apparatus is defending an
over-statement.** Full disposition and my own contribution to it are
recorded in `BASELINE.md` §1. **Severity: CRITICAL for a project whose
differentiator is measurement honesty. Dimension: Trust, Engineering craft.**

### 8.2 The strong half is genuinely strong (REPORTED, and it matters)

`test_source_of_truth.py`, `test_hostile_sweep.py`, `test_scan_safety.py`,
`test_delta_dataset.py` and `test_dpv_export.py` derive expectations from
source rather than restating them, and several carry **vacuity controls** —
tests whose job is to prove the sibling test can fail
(`test_scan_safety.py:314` asserts the *old* insecure pattern still leaks;
`test_hostile_sweep.py:204` proves the hostile fixture is actually
hostile). That is rarer and more valuable than coverage percentage, and
any remediation must not damage it.

### 8.3 Weak-test census (REPORTED, with method stated)

Of 2,322 unique functions: **2** have no behavioural assertion
(`test_evidence_pack_unit.py:470`, `test_telemetry.py:33` — the latter's
correct form exists 190 lines below it at `:226`); **270 (11.6%)** assert
only membership / `len>0` / `isinstance` / `is not None`; **16 assertion
sites** re-implement `_sha256` as their own expected value, so switching
the hash to MD5 would leave them green; **0** parametrised tests exist.
Two are pure tautologies (`test_audit_scoping.py:93` compares a pure
function to itself).

### 8.4 Data-copy drift, already drifted (REPORTED, serious)

`tests/test_questionnaire_scoring.js` contains a **full copy** of all 15
questionnaire questions and a re-implementation of `calculateResultsEU()`,
against a source embedded in `site/assess/index.html:723,1100` (plus two
locale copies). It has **already drifted**: question order differs at
positions 8-14 and `text` fields are abbreviated. It has **no sync check**
and **is never executed** — there is no `package.json`, and pytest does
not collect `.js`. This violates the project's own quality rule directly.

Also: `test_classification.py:2274` is named `test_framework_mapper_all_8_frameworks`,
lists 9 keys, and the source has 13 — so dropping `lgpd`/`cra`/`ico_ai`
would pass.

### 8.5 HIGH — the claim auditor cannot see percentages [REPORTED, mechanism traced]

`NUMERIC_CLAIM` (`claim_auditor.py:62-72`) ends the unit alternation with
`\b`. Because `%` is a non-word character, `"40%"`, `"83.5% precision"`
and `"99.9% uptime"` never match — only the spelled-out `"40 percent"`
does. The module docstring at `:6` lists percentages **first** among what
it detects. Other blind spots traced: unit words outside the hardcoded
list (`rules`, `checks`, `jurisdictions`), unseparated 4+ digit numbers
(`250000`), superlatives outside the vocabulary (`unparalleled`,
`gold standard`, `#1`), and — in `--verify-facts` — a **50% floor**
(`:781`) that silently skips any stale value below half the canonical one,
plus the fact that **deleting a claim entirely passes**.

Additionally, `paragraph_has_source()` accepts the bare words **`see`**
and **`ref`**, or any URL however irrelevant, as sourcing for every claim
in the paragraph.

**The single highest-leverage one-line fix available in the repo:**
removing the trailing `\b` at `claim_auditor.py:69` would make every
percentage claim visible to the gate for the first time. It must be done
with care — it will surface a backlog of currently-invisible claims, which
is the point.

### 8.6 The gates' own CI entry points are untested (REPORTED)

`claim_auditor.py`'s uncovered 42% is precisely `verify_facts()` (the
function CI runs on every PR), `main()` and the exit-code contract, the
git file-selection helpers behind `--diff-base`, and `backtest()`. A
`git diff` returning an empty list would make the gate pass on every PR
while checking nothing.

---

## 9. Sections pending

Architecture / call-graph map, per-language regex-quality audit,
crosswalk audit, test-suite audit, security pass and repo hygiene are in
progress (two audit subagents dispatched; results appended on return).
