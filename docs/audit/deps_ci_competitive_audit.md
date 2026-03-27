# Regula Audit: Dependency Security, CI/CD Integration, and Competitive Positioning

**Date:** 2026-03-27
**Auditor:** Code audit (automated analysis of source files)

---

## Part 1: Dependency Scanner Capabilities and Limitations

### AI Library Registry

**Exact count: 100 unique entries** in `AI_LIBRARIES` (file: `scripts/dependency_scan.py`, lines 18-74).

Breakdown by ecosystem:
- Python ML/DL frameworks: 6 (tensorflow, torch, pytorch, keras, jax, flax)
- Transformers ecosystem: 10 (transformers, sentence-transformers, peft, trl, accelerate, datasets, diffusers, safetensors, huggingface-hub, tokenizers)
- LLM providers/wrappers: 9 (openai, anthropic, cohere, litellm, vllm, replicate, together, mistralai, groq)
- LangChain ecosystem: 6 (langchain, langchain-core, langchain-community, langchain-openai, langchain-anthropic, langchain-google-genai)
- LlamaIndex: 2 (llama-index, llama-index-core)
- Classical ML: 5 (sklearn, scikit-learn, xgboost, lightgbm, catboost)
- NLP: 3 (spacy, nltk, gensim)
- Local inference: 2 (llama-cpp-python, ctransformers)
- Structured generation/agents: 8 (instructor, outlines, dspy-ai, guidance, semantic-kernel, autogen, crewai, phidata)
- Vector databases: 5 (chromadb, pinecone-client, weaviate-client, qdrant-client, milvus)
- Document processing: 1 (unstructured)
- Model serving/UI: 3 (gradio, streamlit, bentoml)
- MLOps: 5 (mlflow, wandb, optuna, sagemaker, ray)
- ONNX: 2 (onnx, onnxruntime)
- Haystack: 1 (haystack-ai)
- JavaScript/TypeScript (npm): 10 (@anthropic-ai/sdk, @tensorflow/tfjs, @langchain/core, brain.js, @xenova/transformers, @huggingface/inference, @pinecone-database/pinecone, @qdrant/js-client-rest, weaviate-ts-client, ai)
- Rust crates: 21 raw entries, 17 unique after deduplication (candle-core, candle-nn, candle-transformers, burn, burn-core, burn-tch, burn-ndarray, tch, ort, rust-bert, async-openai, misanthropic, langchain-rust, llm-chain, hf-hub, linfa, smartcore)
- C++ packages: 5 (libtorch, tensorflow-lite, mlpack, dlib, faiss)

Note: 4 entries are duplicated across ecosystems (anthropic, tokenizers, safetensors, qdrant-client) and are deduplicated by the Python `set`.

### Alias handling

`_AI_ALIASES` maps 2 aliases:
- `pytorch` -> `torch`
- `sklearn` -> `scikit-learn`

### How `is_ai_dependency()` works

The function normalises the input name (lowercase, replace `[-_.]` with `-`) and checks against a pre-computed normalised set of all `AI_LIBRARIES` plus alias keys. This is an **exact-match lookup only**.

### Typosquatting detection: NOT SUPPORTED

The scanner has **zero typosquatting detection**. Analysis of the code confirms:
- `openaii` -> **False** (would miss a typosquat of `openai`)
- `open-ai` -> **False** (would miss a hyphenated variant of `openai`)
- `langchian` -> **False** (would miss a transposition typosquat of `langchain`)
- `pytorch` -> **True** (only because it is explicitly listed as an alias)
- `torch` -> **True** (directly in the set)

This is a significant gap. Typosquatting is one of the most common supply chain attack vectors. The scanner detects only exact matches from its registry. It does not use edit distance, phonetic matching, or any fuzzy matching.

### How `check_compromised()` works

1. Calls `_load_advisories()` which recursively reads `*.yaml` files from `references/advisories/`.
2. For each dependency with a name and version, iterates over all advisory entries.
3. Matches by normalised package name against the advisory's `affected[].package.name`.
4. Checks if the dependency's exact version string appears in the advisory's `affected[].versions` list.
5. Returns findings with advisory_id, description, remediation, and severity (hardcoded to "critical").

**Limitations:**
- **No version range matching.** Only checks for exact version strings in the `versions` list. If an advisory specifies ranges (e.g., `>=1.0,<1.5`), these are not evaluated. OSV format commonly uses `ranges` with `type: SEMVER` or `type: ECOSYSTEM`, which are completely ignored.
- **No `references/advisories/` directory exists.** The glob search found zero files. The compromised-package database is empty, meaning `check_compromised()` always returns an empty list in the current state.
- **No integration with OSV.dev, pip-audit, or any external vulnerability database.**

### How `calculate_pinning_score()` works

Algorithm:
1. Each dependency gets a weight: **3x for AI dependencies**, 1x for non-AI.
2. Each pinning level has a score: hash=100, exact=80, compatible=60, range=30, unpinned=0.
3. Weighted average: `sum(weight * pinning_score) / sum(weights)`, rounded.
4. If a lockfile is present, adds +20 (capped at 100).
5. If no dependencies found, base score is 100.

This is a reasonable scoring algorithm with appropriate AI-dependency weighting.

### Dependency files parsed

The scanner parses **7 dependency file types**:
1. `requirements.txt` — Python pip
2. `pyproject.toml` — Python (PEP 621)
3. `package.json` — JavaScript/TypeScript npm
4. `Pipfile` — Python Pipenv
5. `Cargo.toml` — Rust
6. `CMakeLists.txt` — C/C++ (find_package and target_link_libraries)
7. `vcpkg.json` — C/C++ vcpkg

**Not parsed:** `go.mod` (Go), `build.gradle` / `pom.xml` (Java/Kotlin), `Gemfile` (Ruby), `Package.swift` (Swift), `conanfile.txt`/`conanfile.py` (C++ Conan), `poetry.lock`, `setup.py`, `setup.cfg`.

### Recommendation: pip-audit complement

The `references/advisories/` directory does not exist, meaning the compromised-package database has **zero entries**. pip-audit (backed by the OSV database with 4000+ Python advisories) or `osv-scanner` (multi-ecosystem) should be **strongly recommended as a complement**, not replaced by Regula's scanner. Regula should not try to be standalone for vulnerability detection. Its value-add is the AI-specific pinning analysis and governance framing, not CVE coverage.

---

## Part 2: SARIF Validation Results

### SARIF generation analysis (static code review)

The SARIF output is generated by `generate_sarif()` in `scripts/report.py` (line 501).

**Conformance to SARIF v2.1.0:**
- `$schema`: Present, points to the correct OASIS SARIF 2.1.0 schema URL.
- `version`: Set to `"2.1.0"` — correct.
- `runs`: Single run with `tool.driver` containing `name`, `version`, `informationUri`, and `rules`.
- `rules`: Defined from pattern dictionaries (PROHIBITED_PATTERNS, HIGH_RISK_PATTERNS, SECRET_PATTERNS, LIMITED_RISK_PATTERNS). Each rule has `id`, `name`, `shortDescription`, `fullDescription`, `defaultConfiguration.level`, and `helpUri`.
- `results`: Each has `ruleId`, `level`, `message.text`, `locations[].physicalLocation.artifactLocation.uri`, `locations[].physicalLocation.region.startLine`, and `properties.confidence_score`.

**Issues found:**
1. **Potential ruleId mismatch:** Results use the first indicator from `f["indicators"][0]` as the rule suffix (e.g., `regula/prohibited/social_scoring`). This builds a rule ID dynamically. If a finding's primary indicator does not have a corresponding pre-defined pattern, the ruleId in the result will not match any entry in the `rules` array. This is a SARIF spec violation (each result's ruleId SHOULD reference a defined rule).
2. **No `invocations` array:** SARIF best practice is to include `invocations` with `executionSuccessful` to indicate whether the tool completed successfully. Not a hard requirement but recommended.
3. **`properties.confidence_score` is non-standard:** This is allowed by SARIF (properties bag is extensible) but consumers may not use it.
4. **No `automationDetails`:** Recommended for CI/CD to identify unique analysis runs.

**Overall SARIF assessment: MODERATE quality.** The output is structurally valid SARIF 2.1.0 and will work with GitHub Code Scanning, but could be improved with invocations and automation details.

---

## Part 3: GitHub Action Assessment

### action.yml review (file: `/home/mkuziva/getregula/action.yml`)

**Composite action structure:** Correct use of `runs: using: composite`.

**Inputs (7 defined):**
- `path` (default: ".") — project path
- `format` (default: "sarif") — output format
- `framework` (default: "eu-ai-act") — compliance framework
- `fail-on-prohibited` (default: "true") — exit 2 on prohibited findings
- `fail-on-high-risk` (default: "false") — exit 1 on high-risk findings
- `min-dependency-score` (default: "0") — minimum pinning score threshold
- `upload-sarif` (default: "true") — upload to Code Scanning

All inputs have defaults and descriptions. This is correct.

**Outputs (5 defined):**
- `findings-count`, `prohibited-count`, `high-risk-count`, `pinning-score`, `sarif-file`

All reference appropriate step outputs. This is correct.

**Issues found:**

1. **Silent failure in step "Run regula check":** The `|| true` at the end of the CLI invocation means the step never fails, even if regula crashes. If the SARIF file is not created, a fallback run is attempted. If that also fails, a minimal stub JSON is written. This masks real errors. The action will appear to succeed with zero findings when the tool itself is broken.

2. **Python installation with `pip install -e`:** The step runs `pip install --quiet -e "${{ github.action_path }}" 2>/dev/null || true`. Errors are suppressed. If installation fails, subsequent Python imports will fail silently (hidden by `|| true`).

3. **No pinning of `actions/setup-python@v5` or `github/codeql-action/upload-sarif@v3`:** These use major version tags rather than commit SHAs. For a security tool, this is a supply chain risk in itself. Best practice is to pin to a full commit SHA.

4. **Environment variable passing:** The `SARIF_FILE` env var in the "Count findings" step is set correctly via the `env` block. However, the "Run regula check" step constructs the path inline rather than using an env var, creating a potential inconsistency if the path template changes.

5. **Exit code handling is well-designed:** Exit code 2 for prohibited findings (hard block), exit code 1 for high-risk/low-pinning (soft fail), exit code 0 for pass. The priority order (prohibited overrides high-risk) is correct.

6. **Step summary formatting:** The heredoc in "Write GitHub Step Summary" has leading whitespace (4 spaces of indentation). This will render as a code block in markdown rather than a table. The table will likely not render correctly.

7. **The `continue-on-error: true` on SARIF upload** is appropriate — upload failures should not block the workflow. The `if: always()` condition ensures it runs even if previous steps fail.

**Overall action.yml assessment: MODERATE quality.** The structure is sound and follows composite action conventions. The main concerns are error suppression masking failures, unpinned action references, and the step summary formatting issue.

---

## Part 4: Corrected Competitive Matrix

### Regula's actual capabilities (verified from source)

| Capability | Honest Level | Evidence |
|---|---|---|
| Languages scanned | 8 languages (EXTENSION_MAP) | python, javascript, typescript, java, go, rust, c, cpp |
| Python AST analysis | FULL | Dedicated `ast_analysis.py` with `parse_python_file`, `classify_context`, `trace_ai_data_flow`, `detect_human_oversight`, `detect_logging_practices` |
| JS/TS analysis | MODERATE | Tree-sitter optional, regex fallback. Import detection and basic pattern matching. No deep data flow. |
| Java/Go/Rust/C/C++ analysis | BASIC | Regex-only pattern matching for imports and AI library usage. No AST, no data flow. |
| AI library detection | MODERATE | 100 unique libraries across 5 ecosystems. No typosquatting detection. Exact-match only. |
| Dependency pinning analysis | MODERATE | 7 dependency file formats parsed. Weighted scoring algorithm. No vulnerability database (advisories dir is empty). |
| Vulnerability detection | NONE (effectively) | Advisory loading code exists but `references/advisories/` directory has zero files. No integration with OSV, NVD, or pip-audit. |
| SARIF output | MODERATE | Valid SARIF 2.1.0 structure. Minor spec compliance gaps (no invocations, potential ruleId mismatches). |
| EU AI Act mapping | FULL | Articles 5, 9-15, 50 mapped. Prohibited, high-risk, limited-risk tiers. Cross-framework mapping to 8 frameworks. |
| CI/CD integration | MODERATE | GitHub Action with proper inputs/outputs/exit codes. Error suppression masks failures. Unpinned action deps. |
| Compliance frameworks | 8 frameworks mapped | eu-ai-act, nist-ai-rmf, iso-42001, nist-csf, soc2, iso-27001, owasp-llm-top10, mitre-atlas |
| CLI commands | 19 commands | init, check, classify, report, audit, discover, install, status, feed, questionnaire, session, baseline, docs, compliance, gap, benchmark, timeline, deps, sbom |

### Competitor comparison (honest assessment)

**Note:** Competitor capabilities below are based on their publicly documented features as of March 2026. Where specific capabilities cannot be verified from public sources, "UNVERIFIED" is noted.

| Capability | Regula | Semgrep | Snyk | Systima Comply | ArkForge | Agent-BOM |
|---|---|---|---|---|---|---|
| **EU AI Act classification** | FULL (Articles 5, 9-15, 50; prohibited/high-risk/limited tiers) | NONE (security-focused, no regulatory mapping) | NONE (security/license-focused) | UNVERIFIED (claims regulatory focus) | UNVERIFIED (claims compliance) | NONE (SBOM-focused) |
| **Static analysis depth** | FULL for Python, BASIC-MODERATE for 7 others | FULL for 30+ languages (mature AST engine with taint tracking) | MODERATE (primarily dependency-focused, some SAST) | UNVERIFIED | UNVERIFIED | NONE (inventory only) |
| **Vulnerability database** | NONE (empty advisory dir) | FULL (Semgrep rules registry, community rules) | FULL (Snyk Vulnerability DB, 4M+ entries) | UNVERIFIED | UNVERIFIED | NONE |
| **Dependency scanning** | MODERATE (7 file formats, pinning analysis, no vuln DB) | MODERATE (Semgrep Supply Chain, reachability analysis) | FULL (industry-leading dep scanning, license compliance) | UNVERIFIED | UNVERIFIED | MODERATE (SBOM generation) |
| **SARIF output** | MODERATE | FULL | FULL | UNVERIFIED | UNVERIFIED | NONE |
| **CI/CD integration** | MODERATE (GitHub Action) | FULL (GitHub, GitLab, Bitbucket, IDE plugins) | FULL (all major CI/CD, IDE plugins, CLI) | UNVERIFIED | UNVERIFIED | BASIC |
| **AI-specific governance** | FULL (AI library detection, data flow, human oversight, credential checks) | NONE (general-purpose) | NONE (general-purpose) | UNVERIFIED (claims AI governance) | UNVERIFIED (claims AI compliance) | MODERATE (AI SBOM focus) |
| **Multi-framework mapping** | FULL (8 frameworks cross-mapped) | NONE | NONE | UNVERIFIED | UNVERIFIED | NONE |
| **Typosquatting detection** | NONE | NONE (not a primary feature) | MODERATE (some detection via advisories) | UNVERIFIED | UNVERIFIED | NONE |
| **Maturity / Community** | Early-stage, single-developer | Mature, large community, VC-funded | Mature, enterprise-grade, public company | Early-stage | Early-stage | Early-stage |

### Key honest takeaways

1. **Regula's differentiator is genuine:** No established SAST tool (Semgrep, Snyk) provides EU AI Act regulatory classification and cross-framework mapping. This is a real gap Regula fills.

2. **Regula should not claim to be a vulnerability scanner.** The advisory database is empty. It should position itself as complementary to Snyk/pip-audit/osv-scanner, not a replacement.

3. **Language support claims need qualification.** Saying "8 languages" without noting that only Python has full AST analysis is misleading. 5 of those 8 are regex-only with no data flow analysis.

4. **The "100 AI libraries" claim is accurate** but should be contextualised. It is an exact-match list, not a fuzzy or heuristic detection system. Novel or typosquatted packages are invisible.

5. **Competitor claims about Systima Comply and ArkForge cannot be verified** from public sources. Making competitive claims against unverifiable competitors is risky. Recommend removing specific competitor comparisons unless they can be substantiated with public documentation links.

---

## Recommendations

### High priority
1. **Integrate pip-audit or osv-scanner** as an optional dependency scan complement. Do not try to maintain a bespoke advisory database.
2. **Add typosquatting detection** using edit-distance checks (Levenshtein distance <= 2) against known AI library names.
3. **Pin GitHub Action dependencies** to full commit SHAs in `action.yml`.
4. **Fix error suppression** in the GitHub Action — log warnings instead of silently swallowing failures.

### Medium priority
5. **Add `invocations` and `automationDetails`** to SARIF output for better CI/CD integration.
6. **Add version range matching** in `check_compromised()` for proper OSV advisory evaluation.
7. **Fix step summary indentation** in `action.yml` to render the markdown table correctly.

### Low priority
8. Add `go.mod` and `build.gradle`/`pom.xml` parsers for Go and Java dependency scanning.
9. Consider adding `setup.py` and `setup.cfg` parsers for legacy Python projects.
