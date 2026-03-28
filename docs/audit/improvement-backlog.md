# Regula — Improvement Backlog

**Based on:** False positive audit, AST depth audit, compliance evidence audit, dependency security audit, CI/CD audit, competitive positioning audit.
**Last updated:** 2026-03-28 (v1.2.0)

## ✓ Completed in v1.2.0

| Item | Notes |
|------|-------|
| Priority 1: Fix 4 high-FP regex patterns | `face.?recogn`, `voice.?recogn`, `age.?estimat`, `support.?bot` — word boundaries added. Also `race.?detect`, `face.?scrap`, `predictive.?policing`. |
| Priority 5: Systematic word boundary audit | Applied across prohibted + limited-risk patterns |
| Priority 6: Qualify language support claims | README has honest depth table with "Full AST / Moderate / Import detection" |
| Priority 7: Qualify dependency security claims | README says "pinning hygiene checker, not vulnerability scanner" + pip-audit recommendation |
| P0 #1 (recommendations.md): Remove fcntl from classify_risk.py | Already absent — not present in current file |
| P0 #2: Fix SARIF version | Already 2.1.0 |
| P0 #3: Tighten `sentenc` regex | Done in v1.2.0 |
| P0 #4/#5: README test count + roadmap | Updated 2026-03-28 |
| Agent autonomy detection wired into check | New in v1.2.0 — contextual path detection (OWASP ASI02/ASI04) |
| --skip-tests / --min-tier flags | New in v1.2.0 |
| Priority 2: Fix credit scorer false negative | `train_credit_model` → HIGH-RISK. Removed `\b` from `credit.?model`, `credit.?risk`, `credit.?predict`. 1 regression test added. |
| Priority 3: Wire AST into documentation generator | Sections 2.1, 3.3, 3.4 now populated from AST. `ast_analyse_project()` added. 4 regression tests. |
| Priority 4: Fix advisory directory resolution | `__pycache__` path step-up + `Path.cwd()` fallback. 1 regression test added. |
| Skip-dirs absolute path bug | `filepath.parts` → `filepath.relative_to(project).parts` in `code_analysis.py` and `generate_documentation.py`. 1 regression test added. |
| Version string v1.1.0 → v1.2.0 | 6 occurrences corrected in `generate_documentation.py`. 1 regression test added. |
| Priority 8: go.mod + build.gradle parsing | `parse_go_mod()` and `parse_build_gradle()` added to `dependency_scan.py`, wired into `scan_dependencies()`. 6 regression tests. |

---

## [PRIORITY 1] Fix 4 High-FP Regex Patterns
**Impact:** Every user scanning real code. False positives destroy trust in the first 2 weeks.
**Effort:** 1 hour
**Evidence:** Audit identified 4 patterns with HIGH false positive risk on real codebases.
**Implementation:**

| Pattern | Current | Fix | File |
|---------|---------|-----|------|
| `face.?recogn` | Matches `typeface_recognition`, `surface_recognition` | `\bface.?recogn` (add word boundary) | `classify_risk.py:143` |
| `voice.?recogn` | Matches `invoice_recognition`, `invoice_recognizer` | `\bvoice.?recogn` (add word boundary) | `classify_risk.py:143` |
| `age.?estimat` | Matches `page_estimation` | `\bage.?estimat` (add word boundary) | `classify_risk.py:219` |
| `support.?bot` | Matches `support_bottom` (CSS) | `support.?bot\b` (add trailing word boundary) | `classify_risk.py:209` |

Also tighten 2 MEDIUM-risk prohibited patterns:
- `social.?scor` → `\bsocial.?scor(?:e|ing)\b` (exclude social media scoring without AI context)
- `social.?credit` → `social.?credit.?(?:scor|system|rating)` (exclude credit card contexts)

---

## [PRIORITY 2] Fix Credit Scorer False Negative
**Impact:** Any user building credit/lending AI. This is a real-world compliance gap.
**Effort:** 2 hours
**Evidence:** Credit scoring fixture (`train_credit_model` + `score_applicant`) classified as minimal_risk. Should be high_risk (Annex III Category 5). Pattern `credit.?scor` requires compound phrase; separate identifiers miss.
**Implementation:**
- Add token co-occurrence detection to `classify_risk.py`: if BOTH `credit` AND `scor` (or `predict`/`model`/`classify`) appear within the same file AND the file is AI-related, flag as high-risk
- Add patterns: `credit.?worthi`, `credit.?risk`, `loan.?approv`, `lending.?decision`, `credit.?model`, `credit.?predict`
- Add test with the credit scorer fixture

---

## [PRIORITY 3] Wire AST Results into Documentation Generator
**Impact:** DPOs and compliance consultants — the primary audience for generated docs. Currently Annex IV docs are ~80% blank placeholders despite AST analysis producing rich data.
**Effort:** 1 day
**Evidence:** AST audit found that `generate_documentation.py` does NOT use ast_analysis results. Data flow traces, oversight scores, logging assessments are computed but never appear in the generated Annex IV documentation.
**Implementation:**
- In `generate_documentation.py`, import and run `ast_engine.analyse_project()`
- Populate Annex IV sections with AST-derived evidence:
  - Section 2 (Development): List AI libraries detected, model files found
  - Section 3 (Monitoring): Insert logging scores per file
  - Section 3.3 (Human Oversight): Insert oversight scores, list review functions found
  - Section 5 (Compliance): Auto-fill Article 12/14 status from AST scores
- Add data flow diagrams to the documentation (text-based, showing AI output destinations)

---

## [PRIORITY 4] Fix Advisory Directory Resolution
**Impact:** Anyone using the compromised package detection feature. Works locally with pyyaml but the CI audit found the advisory loader returns empty on some paths.
**Effort:** 30 minutes
**Evidence:** The advisory file exists at `references/advisories/pypi/litellm/x_REGULA-2026-001.yaml` but `_load_advisories()` uses `Path(__file__).resolve().parent.parent` which can fail depending on how the module is imported. Need to add fallback paths.
**Implementation:**
- Add `Path.cwd() / "references" / "advisories"` as a fallback path in `_load_advisories()`
- Add a test that verifies advisory loading from the correct path regardless of import method
- Document that pyyaml is REQUIRED for advisory and framework features (not optional)

---

## [PRIORITY 5] Add Word Boundary to All Single-Word High-Risk Patterns
**Impact:** Reduces FP rate across all high-risk patterns systematically.
**Effort:** 1 hour
**Evidence:** The FP audit found that single-word patterns without word boundaries are the root cause of most false positives. All patterns should use `\b` prefix.
**Implementation:**
- Audit every pattern in HIGH_RISK_PATTERNS
- Add `\b` prefix to any pattern that starts with a plain word (not already using `\b`)
- Preserve patterns that intentionally match substrings (e.g., `credit.?scor` should match `credit_scoring`)
- Run the full test suite after each change to catch regressions

---

## [PRIORITY 6] Qualify Language Support Claims in Documentation
**Impact:** Credibility with technical evaluators. Overclaiming undermines trust.
**Effort:** 30 minutes
**Evidence:** Competitive audit found that saying "8 languages" without qualification is misleading. Only Python has full AST, JS/TS has moderate tree-sitter, 5 others are regex-only.
**Implementation:**
- README: Change "8 languages" to "8 languages (Python: full AST, JS/TS: AST with tree-sitter, Java/Go/Rust/C/C++: import detection)"
- SKILL.md: Same qualification
- Add honest capability levels to the architecture section

---

## [PRIORITY 7] Qualify Dependency Security Claims
**Impact:** Credibility. Claiming dependency security with 1 advisory entry vs pip-audit's 4000+ is misleading.
**Effort:** 30 minutes
**Evidence:** Competitive audit confirmed the advisory database has 1 entry. The value-add is pinning quality analysis, not vulnerability scanning.
**Implementation:**
- README: Change "dependency supply chain security" to "AI dependency pinning analysis"
- Add explicit recommendation: "For vulnerability scanning, complement with pip-audit or osv-scanner"
- Remove or qualify "known compromised versions" claim unless more advisories are added
- In CLI output: add a line "Tip: Run pip-audit for comprehensive vulnerability scanning"

---

## [PRIORITY 8] Add go.mod and build.gradle Dependency Parsing
**Impact:** Enterprise users with Go and Java projects. These are missing from the 7 parsers.
**Effort:** 2 hours
**Evidence:** dependency_scan.py parses 7 formats but misses go.mod (Go) and build.gradle/pom.xml (Java) — the dependency files for 2 of the 8 supported languages.
**Implementation:**
- `parse_go_mod(content)`: Extract `require` blocks, match against GO_AI_LIBRARIES
- `parse_build_gradle(content)`: Extract `implementation`/`compile` dependencies
- Add to `scan_dependencies()` file scanning

---

## [PRIORITY 9] Add Typosquatting Detection (Basic)
**Impact:** Supply chain security. Typosquatting is the #1 attack vector.
**Effort:** 1 day
**Evidence:** `is_ai_dependency()` is exact-match only. `openaii`, `langchian`, `open-ai` all return False. Even basic edit-distance detection would catch common typosquats.
**Implementation:**
- Add Levenshtein distance check (stdlib-friendly: implement in ~20 lines)
- For any unrecognised dependency with edit distance ≤2 from a known AI library: flag as potential typosquat
- Severity: WARNING (not BLOCKING — may have false positives)

---

## [PRIORITY 10] Improve JS/TS Tree-Sitter Depth
**Impact:** Users scanning Node.js AI applications. Currently misses automated_action detection in if-conditions.
**Effort:** 2-3 days
**Evidence:** AST audit confirmed JS/TS tree-sitter misses: automated_action (if-condition detection), api_response (res.json/res.send classification), display (React rendering). Python AST catches all of these.
**Implementation:**
- In `_tree_sitter_parse()`, add if_statement visitor that checks if AI-tracked variables appear in conditions
- Add destination classification for Express/Next.js response patterns
- Add React JSX return detection
- Port `_classify_call()` logic from Python's `_FlowTracer` to tree-sitter

---

## NOT RECOMMENDED

| Item | Why Not |
|------|---------|
| Web dashboard | Different product. Multi-week React project. Build after CLI is stable with users. |
| General CVE database | pip-audit/osv-scanner do this with 50K+ entries. Recommend them as complement. |
| Cross-file data flow | 5-8 days effort, complex import graph resolution. Deferred until single-file is production-validated. |
| Marketing/GTM | Technical audit, not business audit. |
| Migrate to pytest | Nice-to-have but doesn't add user value. Current test framework works. |

---

## Execution Order

**Day 1:** Priority 1 (FP patterns) + Priority 2 (credit scorer) + Priority 4 (advisory path) + Priority 5 (word boundaries) + Priority 6 (docs qualification) + Priority 7 (deps qualification) = all quick fixes done

**Day 2-3:** Priority 3 (wire AST into docs) + Priority 8 (go.mod/gradle)

**Day 4:** Priority 9 (typosquatting)

**Week 2:** Priority 10 (JS/TS depth)
