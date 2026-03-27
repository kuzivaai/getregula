# Regula AST Analysis & Compliance Evidence Audit

**Audit date:** 2026-03-27
**Auditor:** Automated deep-read audit (Claude Opus 4.6)
**Scope:** `scripts/ast_analysis.py`, `scripts/ast_engine.py`, `scripts/compliance_check.py`, `scripts/generate_documentation.py`, `scripts/classify_risk.py`

---

## 1. Language Capability Matrix

| Capability | Python | JS/TS (tree-sitter) | JS/TS (regex fallback) | Java | Go | Rust | C/C++ |
|---|---|---|---|---|---|---|---|
| **Parser type** | stdlib `ast` (full AST) | tree-sitter (full AST) | regex only | regex only | regex only | regex only | regex only |
| **Import detection** | Yes (Import + ImportFrom) | Yes (import/require nodes) | Yes (regex) | Yes (regex) | Yes (import blocks + single) | Yes (use statements + Cargo.toml) | Yes (#include) |
| **AI library recognition** | 60+ libraries | 20+ npm packages | Same as tree-sitter | 12 Maven packages | 9 Go modules | 30+ crates | 30+ headers/namespaces |
| **Function extraction** | Full (name, args, decorators, async) | Full (declarations, arrows, methods) | Partial (name only, no args) | Partial (name only) | Partial (name only) | Partial (name only) | Partial (name only) |
| **Class extraction** | Full (name, bases, methods) | Full (name, extends, methods) | Partial (name, extends only) | Partial (name only) | Structs only (name) | Structs only (name) | Classes/structs (name only) |
| **Data flow tracing** | Yes - full intra-function | Yes - variable assignment + usage | None (empty destinations) | None | None | None | None |
| **AI call detection** | Yes (method chain + context) | Yes (member expr flattening) | Yes (regex, no destinations) | No | No | No | No |
| **Flow destination classification** | 8 types (return, variable, log, human_review, automated_action, api_response, display, persisted) | 7 types (same minus display nuance) | None | None | None | None | None |
| **Human oversight detection (Art. 14)** | AST-based: function names, decorators, call expressions + data flow cross-ref | AST-based: function names + call expressions + if-statement analysis | Keyword grep only | Keyword grep only | Keyword grep only | Keyword grep only | Keyword grep only |
| **Logging detection (Art. 12)** | AST-based: call classification + AI-op proximity (5 lines) | AST-based: call classification + AI-op proximity (5 lines) | Regex pattern count (no proximity) | Regex (no proximity) | Regex (no proximity) | Regex (no proximity) | Regex (no proximity) |
| **Oversight scoring** | 0-100 (evidence +15 each, automated -10 each, floor at 20 if no patterns) | Same algorithm | Fixed 50 + 15/pattern, max 100 | Same as JS regex | Same | Same | Same |
| **Logging scoring** | 0-100 (ratio-based: logged_ops/total * 80 + 10 bonus) | Same algorithm | Fixed 50 or 60 | Fixed 50 or 60 | Fixed 50 or 60 | Fixed 50 or 60 | Fixed 50 or 60 |
| **Test file detection** | Function name + class name heuristics | Filename + describe/it/test call detection | Filename + regex for test frameworks | @Test annotation + class name | Function name (Test prefix) | Function name + #[cfg(test)] | Function name (test/Test prefix) |
| **Context classification** | 5 categories (implementation, test, configuration, documentation, not_python) | 4 categories (implementation, test, configuration, not_parseable) | Same as tree-sitter | 3 categories | 3 categories | 3 categories | 3 categories |
| **Namespace usage detection** | N/A | N/A | N/A | N/A | N/A | N/A | Yes (cv::, torch::, tf:: etc.) |

### Honest Capability Levels

| Language | Level | Summary |
|---|---|---|
| **Python** | **Deep** | True AST parsing with intra-function data flow tracing. Can detect AI calls, trace results through assignments/returns/conditionals, and classify destinations. |
| **JS/TS (tree-sitter)** | **Deep** | Comparable to Python. Full AST with data flow tracing, oversight detection, and automated decision flagging. Requires optional tree-sitter dependency. |
| **JS/TS (regex)** | **Shallow** | Detects imports and function names. Data flow returns empty destinations. Oversight/logging are keyword-only. No structural understanding. |
| **Java** | **Shallow** | Import matching + function/class name extraction. No data flow. No structural analysis. Oversight is keyword grep. |
| **Go** | **Shallow** | Same as Java. Import block parsing is reasonable but everything else is surface-level. |
| **Rust** | **Shallow** | Can parse both `use` statements and Cargo.toml dependencies (good). Normalises underscores to hyphens for matching. No data flow. |
| **C/C++** | **Shallow** | #include matching + namespace usage detection (cv::, torch:: etc.) is a nice addition. No data flow, no structural analysis. |

---

## 2. Python vs JS/TS Gap Analysis

### What Python Detects That JS/TS (tree-sitter) Also Detects
- AI library imports
- Function/class structure with full detail
- AI call detection via method chain analysis
- Variable assignment tracking from AI call results
- Data flow destinations (return, log, human_review, automated_action, api_response, display, persisted)
- Human oversight patterns (function names, decorators, call expressions)
- Logging proximity to AI operations (5-line window)
- Automated decision detection (AI results used in if-conditions)

### What Python Detects That JS/TS Misses (or handles differently)

1. **Decorator-based oversight detection:** Python's `_OversightVisitor` explicitly walks decorator lists for oversight keywords. JS/TS tree-sitter does not extract decorators at all (`decorators: []` is hardcoded empty for all function defs). TypeScript decorators (e.g., `@RequiresApproval`) will be missed.

2. **Annotated assignments:** Python handles `AnnAssign` (type-annotated assignments like `result: Response = model.predict(x)`). JS/TS tree-sitter only handles `variable_declarator`.

3. **Tuple unpacking:** Python's `_FlowTracer` handles tuple unpacking in assignments (`a, b = model.predict(x)` tracks both `a` and `b`). JS/TS destructuring (`const {a, b} = ...`) is not handled.

4. **Richer call classification:** Python's `_FlowTracer._classify_call()` has 8 distinct destination categories with detailed pattern matching (e.g., Streamlit-specific `st.write`/`st.markdown`). JS/TS `_classify_destination()` has fewer patterns.

5. **Documentation context:** Python can classify files as "documentation" (AI keywords only in docstrings). JS/TS regex cannot.

### What JS/TS (tree-sitter) Detects That Python Misses
- Nothing significant. Python's analysis is strictly a superset in terms of capability depth.

### What JS/TS (regex fallback) Misses vs tree-sitter
- **Data flow destinations:** Regex mode returns empty `destinations` arrays for all data flows. This is the single biggest gap -- it means the regex fallback cannot determine whether AI outputs are logged, reviewed, returned to users, or used in automated decisions.
- **Automated decision detection:** Entirely absent in regex mode.
- **Oversight call detection:** Regex mode does keyword grep on full content rather than AST-aware call detection, leading to false positives (e.g., "manual" in a comment or string literal).
- **Logging proximity:** Regex mode assigns a fixed score (50 or 60) rather than calculating AI-operation proximity.

---

## 3. What the AST Analysis Misses (All Languages)

### Critical Gaps

1. **Cross-file data flow:** All analysis is single-file only. A common pattern like:
   ```python
   # file1.py
   result = model.predict(data)
   return result

   # file2.py
   from file1 import predict
   output = predict(user_input)
   send_to_user(output)  # <-- Not traced
   ```
   The flow from `model.predict()` in file1 through to `send_to_user()` in file2 is invisible.

2. **Async/await chains:** Python's `_StructureVisitor` records `AsyncFunctionDef` but `_FlowTracer` does not understand `await` semantics. An `await model.ainvoke()` result assigned inside an async function is tracked, but chains like:
   ```python
   async def pipeline():
       task = asyncio.create_task(model.predict(data))
       result = await task  # <-- origin not traced through create_task
   ```
   are not followed.

3. **Class inheritance:** `_StructureVisitor` records base classes but `_FlowTracer` and `_AICallCollector` do not use inheritance information. If `class MyModel(BaseModel)` inherits `predict()` from `BaseModel`, calls to `my_model.predict()` will only be detected if the chain contains an AI-related name -- the inheritance chain is not resolved.

4. **Decorator-based routing:** Flask/FastAPI route decorators (`@app.route`, `@router.post`) are recorded as decorator strings but not used to understand that a function is an HTTP endpoint. This matters for oversight scoring -- a function decorated with `@app.route("/predict")` that returns AI output directly to users should be flagged more severely than an internal helper.

5. **Dynamic dispatch:** `getattr(model, method_name)(data)` and similar dynamic patterns are invisible.

6. **Configuration-driven AI:** Systems where AI behaviour is controlled by config files (e.g., `pipeline = load_config("pipeline.yaml")`) rather than direct library calls are missed entirely.

7. **Callback/closure flows:** AI results passed into callbacks (`model.predict(data, callback=process_result)`) are not tracked through the callback.

8. **Generator/iterator patterns:** `yield model.predict(item) for item in batch` -- the flow through generators is not traced.

---

## 4. Credit Scorer Test Results

### Test Fixture
```
/tmp/credit_scorer/
  app.py           - XGBoost credit scoring model (train + score)
  requirements.txt - xgboost, pandas
```

### Expected Classification Results

Based on code analysis of `classify_risk.py` and `report.py`:

**Risk Classification:** The credit scorer code contains:
- `import xgboost` -- matches `AI_LIBRARIES` (xgboost)
- `import pandas` -- matches `AI_LIBRARIES` (pandas)
- `model.predict()` and `model.predict_proba()` -- matches `AI_CALL_PATTERNS`
- `model.fit()` -- matches `AI_CALL_PATTERNS`
- `XGBClassifier` -- AI model constructor

The `classify_risk.py` HIGH_RISK_PATTERNS include `essential_services` with patterns `r"credit.?scor"`, `r"creditworth"`, `r"loan.?decision"`, etc. mapped to **Annex III, Category 5**. However, these patterns match against *content* strings in the code. The function name `train_credit_model` and `score_applicant` do NOT contain "credit_scor" as a contiguous pattern -- but "credit_model" in function name text would not match `r"credit.?scor"`.

**Important nuance:** The regex `credit.?scor` requires "credit" followed by zero or one character then "scor". The function `train_credit_model` has "credit_model" not "credit_scor". The function `score_applicant` has "score_applicant". These do NOT match the high-risk pattern. The system would need the literal string "credit scoring" or "credit_score" somewhere in the code to trigger the Annex III Category 5 match.

**Predicted `check` output:**
- Would detect AI imports (xgboost, pandas)
- Would detect AI operations (fit, predict, predict_proba)
- Would classify as **minimal_risk** or **high_risk** depending on whether content patterns match
- The essential_services patterns would likely NOT match because the code does not contain "credit scoring" as a literal string -- it has "credit_model" and "score_applicant" as separate identifiers

**This is a gap.** A credit scoring application with function names like `train_credit_model` and `score_applicant` should be flagged as Annex III Category 5, but the regex patterns require "credit" adjacent to "scor" (with at most one character between them), while the actual code separates these terms.

### Predicted `gap` Assessment

`compliance_check.py` checks Articles 9-15 by scanning for:
- Risk management files (Article 9): None present -- score 0
- Data governance docs + bias libraries (Article 10): No fairlearn/aequitas, no data dictionary -- score 0
- Technical documentation (Article 11): No annex_iv or model_card files -- score 0
- Record-keeping (Article 12): AST analysis of app.py would find no logging near AI ops -- score 0
- Transparency (Article 13): No transparency docs -- score 0
- Human oversight (Article 14): No oversight functions/calls in app.py -- score ~10-20
- Accuracy/robustness (Article 15): No test files, no monitoring -- score 0

**Overall expected score: ~5-10/100** -- nearly every article gap would be flagged.

### Predicted `deps` Output

`dependency_scan.py` would parse `requirements.txt` and flag:
- xgboost: AI/ML library (unpinned version -- supply chain concern)
- pandas: Data library (unpinned version)
- Both lack version pinning, which would lower the pinning score

### Predicted `docs` Output

`generate_documentation.py` would produce:
1. **Annex IV scaffold** with `[TO BE COMPLETED]` placeholders for most sections
2. A table listing app.py with its detected risk tier and indicators
3. Compliance requirements table for Articles 9-15 if classified as high-risk
4. QMS scaffold (if `--qms` flag used) with Article 17 structure

---

## 5. Compliance Evidence Quality Assessment

### Strengths

1. **Python AST analysis is genuinely useful.** The data flow tracing from AI calls through assignments, returns, conditionals, and API responses provides real compliance evidence. Detecting that `model.predict()` output flows directly into a `return` statement without passing through any logging or review function is materially useful for Article 14 assessment.

2. **Structured gap assessment.** The compliance_check.py module checks each Article (9-15) independently with specific file/content patterns and produces a 0-100 score per article. This gives actionable visibility into which areas need work.

3. **Honest disclaimers.** Both classify_risk.py and generate_documentation.py contain prominent disclaimers that results are "risk indication, not legal classification" and that scaffolds require human completion. This is important for avoiding over-reliance.

4. **Scoring rubrics are reasonable.** The oversight score formula (base 50, +15 per evidence, -10 per automated decision, floor at 20 if flows exist but no oversight) produces reasonable relative rankings.

### Weaknesses

1. **Generated documentation is mostly boilerplate.** The Annex IV scaffold is ~80% `[TO BE COMPLETED]` placeholders. The only substantive auto-populated sections are:
   - Section 1.2 (AI components table -- file names, tiers, indicators)
   - Section 5 (compliance requirements table)
   - Section 1.3 (model files list)

   Everything else (development methods, data requirements, model architecture, performance metrics, known limitations, human oversight procedures, risk management) is blank. This is honest but of limited value beyond providing correct headings.

2. **No integration between AST findings and documentation.** The `generate_documentation.py` module calls `classify()` but does NOT call `trace_ai_data_flow()`, `detect_human_oversight()`, or `detect_logging_practices()`. The deep AST analysis results are not incorporated into generated documentation. For example, the oversight score could pre-populate Section 3.3 (Human Oversight) with specific findings, and the data flow analysis could populate Section 3.1 with detected AI operation patterns.

3. **Credit scoring gap (detailed above).** The regex patterns for Annex III Category 5 would miss a real credit scoring application where "credit" and "score" appear in separate identifiers rather than as a contiguous phrase. The system needs semantic understanding or broader regex patterns (e.g., matching files that import xgboost AND have function names containing both "credit" and "score" separately).

4. **Regex-language oversight is essentially meaningless.** For Java/Go/Rust/C++, the oversight detection is a keyword grep on full file content. The word "manual" in a comment about "manual testing" or "confirm" in a variable name like `confirm_delete` would generate false positive oversight evidence. The fixed scores (50 or 60) provide no actual compliance insight.

5. **No cross-file analysis in gap assessment.** The compliance_check module reads files individually. If oversight is implemented in `middleware/auth.py` and the AI model runs in `services/model.py`, the gap assessment cannot connect them. This means projects with good separation of concerns may appear to have worse oversight than they actually do.

6. **Data flow tracing is intra-function only.** Even within Python, the `_FlowTracer` traces flows within function bodies but not across function calls within the same file. If `def process(data): return model.predict(data)` is called by `def handle(): result = process(input); return result`, the flow from `model.predict` through `process` to `handle`'s return is not traced.

### Recommendations

1. **Wire AST analysis into documentation generation.** The deep analysis results should populate the Annex IV scaffold with concrete findings rather than blanks.

2. **Implement cross-file flow analysis** at least for Python, using import resolution and call graph construction.

3. **Broaden high-risk pattern matching** to use token co-occurrence within a file (e.g., file contains both "credit" and "score" tokens + AI imports) rather than requiring contiguous regex patterns.

4. **Add confidence levels to regex-language results** to make clear that Java/Go/Rust/C++ analysis is surface-level import detection only.

5. **Handle TypeScript decorators** in the tree-sitter parser -- the `decorators: []` hardcoding means Angular/NestJS oversight decorators are invisible.

---

## 6. Summary

Regula's AST analysis provides genuinely deep analysis for Python and JS/TS (with tree-sitter), covering data flow tracing, oversight detection, and logging assessment. For all other languages, analysis is limited to import detection and keyword grep. The compliance gap assessment framework is well-structured but does not incorporate the deep AST results into generated documentation. The credit scorer test case reveals a pattern-matching blind spot for Annex III Category 5 when domain terms are split across identifiers rather than appearing as contiguous phrases.
