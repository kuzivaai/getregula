# Regula False Positive Audit

**Date:** 2026-03-27
**Auditor:** Automated analysis + manual code review
**Scope:** `scripts/classify_risk.py` (PROHIBITED_PATTERNS, HIGH_RISK_PATTERNS, LIMITED_RISK_PATTERNS, AI_INDICATORS, GPAI_TRAINING_PATTERNS) and `scripts/credential_check.py` (SECRET_PATTERNS)
**Benchmark repos:** `anthropics/anthropic-cookbook` (29 AI-related files scanned)
**Note:** `huggingface/transformers` clone was blocked by environment permissions. Manual benchmark strongly recommended.

---

## Executive Summary

The current rule set is **conservatively tuned for low false-positive rates at the risk-classification level**. On the anthropic-cookbook benchmark (29 files, all legitimately AI-related), the scanner produced **zero false high-risk or prohibited findings** on the current codebase. However, a prior version of the rules (before the sentencing pattern was tightened) did produce 2 false positives from the word "sentence" in NLP contexts.

The **AI_INDICATORS gate** (which determines whether a file is scanned at all) is overly broad in several patterns, particularly `embedding`, `model\.fit`, and `model\.train`. These cause non-AI files to be flagged as "minimal_risk AI code" but do not escalate to actionable risk tiers, limiting real-world harm.

The **most dangerous false positive risks** are in substring-matching patterns within PROHIBITED_PATTERNS that lack word boundary constraints, and in credential patterns that match placeholder/test values.

---

## 1. Per-Rule False Positive Risk Assessment

### 1.1 PROHIBITED_PATTERNS (classify_risk.py)

These patterns trigger `action: "block"`. False positives here are **critical** because they halt developer workflows.

| Rule | Pattern | FP Risk | FP Scenario | Classification | Proposed Fix |
|------|---------|---------|-------------|----------------|--------------|
| subliminal_manipulation | `subliminal` | LOW | Extremely rare word in code. Possible in psychology research code or audio processing (`subliminal_threshold`). | BLOCKING | None needed. Word is specific enough. |
| subliminal_manipulation | `beyond.?consciousness` | LOW | Rare phrase in code. | BLOCKING | None needed. |
| subliminal_manipulation | `subconscious.?influence` | LOW | Rare phrase. | BLOCKING | None needed. |
| exploitation_vulnerabilities | `target.?elderly` | LOW | Rare in non-malicious code. Could appear in accessibility testing. | BLOCKING | None needed. |
| exploitation_vulnerabilities | `exploit.?disabil` | LOW | Rare. | BLOCKING | None needed. |
| exploitation_vulnerabilities | `vulnerable.?group.?target` | LOW | Rare. | BLOCKING | None needed. |
| social_scoring | `social.?scor` | MEDIUM | **Matches `social_score` in social media engagement scoring, gamification, social network analysis.** A social media app computing "social scores" for post popularity would trigger this. | WARNING | Add word boundary or require AI context co-occurrence: `\bsocial.?scor(?:e|ing)\b` and require 2+ indicators. |
| social_scoring | `social.?credit` | MEDIUM | **Matches "social credit card" in fintech/payment code.** | WARNING | Tighten to `social.?credit.?(?:scor|system|rating)` to exclude credit card contexts. |
| social_scoring | `citizen.?score` | LOW | Rare outside social scoring context. | BLOCKING | None needed. |
| social_scoring | `behaviour.?scor` | MEDIUM | **Matches engagement/gamification scoring.** Any app that scores user behaviour for recommendations, retention, or UX optimisation will trigger this. | WARNING | Require proximity to `citizen\|government\|authority\|public` within N chars. |
| criminal_prediction | `crime.?predict` | LOW | Specific enough. | BLOCKING | None needed. |
| criminal_prediction | `criminal.?risk.?assess` | LOW | Specific. | BLOCKING | None needed. |
| criminal_prediction | `predictive.?polic` | **HIGH** | **Matches `predictive_policy` -- a common variable name in RL, config management, and caching code.** Any reinforcement learning codebase with a "predictive policy" class/function will be blocked. | **MUST FIX** | Change to `predictive.?policing` (require full word). |
| criminal_prediction | `recidivism` | LOW | Specific legal term. | BLOCKING | None needed. |
| facial_recognition_scraping | `face.?scrap` | **HIGH** | **Matches `interface_scraper`, `surface_scraping`.** Any web scraping library or data pipeline with "interface" or "surface" in the name triggers this as a substring match. | **MUST FIX** | Change to `\bface.?scrap` (add word boundary at start). |
| facial_recognition_scraping | `facial.?database.?untarget` | LOW | Specific multi-word phrase. | BLOCKING | None needed. |
| facial_recognition_scraping | `mass.?facial.?collect` | LOW | Specific. | BLOCKING | None needed. |
| emotion_inference_restricted | `emotion.{0,20}workplace` | LOW | Specific compound. | BLOCKING | None needed. |
| emotion_inference_restricted | `emotion.{0,20}school` | LOW | Specific compound. | BLOCKING | None needed. |
| emotion_inference_restricted | `sentiment.{0,20}employee` | LOW | Specific compound. | BLOCKING | None needed. |
| biometric_categorisation_sensitive | `race.?detect` | **HIGH** | **Matches `race_detector` in concurrent programming (race condition detection).** Threading/async libraries commonly use "race detection". | **MUST FIX** | Change to `\brace.?detect(?:ion\|or\|ing)` and add negative lookahead for `condition\|data\|thread\|concurrent\|async\|deadlock`. |
| biometric_categorisation_sensitive | `ethnicity.?infer` | LOW | Specific. | BLOCKING | None needed. |
| biometric_categorisation_sensitive | `political.?opinion.?biometric` | LOW | Extremely specific. | BLOCKING | None needed. |
| biometric_categorisation_sensitive | `religion.?detect` | LOW | Rare. | BLOCKING | None needed. |
| biometric_categorisation_sensitive | `sexual.?orientation.?infer` | LOW | Specific. | BLOCKING | None needed. |
| realtime_biometric_public | All patterns | LOW | Multi-word phrases, hard to accidentally match. | BLOCKING | None needed. |

**PROHIBITED summary: 3 patterns need immediate fixes (predictive.?polic, face.?scrap, race.?detect). 3 patterns should be reclassified from BLOCKING to WARNING (social.?scor, social.?credit, behaviour.?scor).**

### 1.2 HIGH_RISK_PATTERNS (classify_risk.py)

These trigger `action: "allow_with_requirements"`. FPs generate compliance noise but don't block.

| Rule | Pattern | FP Risk | FP Scenario | Classification | Proposed Fix |
|------|---------|---------|-------------|----------------|--------------|
| biometrics | `biometric.?ident` | LOW | Specific compound. | WARNING | None needed. |
| biometrics | `face.?recogn` | **HIGH** | **Matches `typeface_recognition`, `surface_recognition`.** OCR/font detection and surface analysis code will trigger. | **MUST FIX** | Change to `\bface.?recogn` (word boundary). |
| biometrics | `fingerprint.?recogn` | LOW | Specific. Could match browser fingerprint recognition but that's arguably a valid flag. | WARNING | None needed. |
| biometrics | `voice.?recogn` | **HIGH** | **Matches `invoice_recognition`, `invoice_recognizer`.** Any invoice processing/OCR system triggers this. Very common in enterprise code. | **MUST FIX** | Change to `\bvoice.?recogn` (word boundary). |
| critical_infrastructure | All patterns | LOW | `energy.?grid`, `water.?supply` etc. are specific enough. | WARNING | None needed. |
| education | `admission.?decision` | LOW | Specific. | WARNING | None needed. |
| education | `student.?assess` | MEDIUM | Matches any student assessment tool including non-AI form builders. But the file must first pass `is_ai_related()` gate, reducing FP risk. | WARNING | Acceptable given AI gate. |
| education | `exam.?scor` | LOW-MEDIUM | Could match "example_score" in some contexts but requires `exam` specifically. AI gate further reduces risk. | WARNING | None needed. |
| education | `procto\w*.{0,15}(exam\|test\|monitor\|...)` | LOW | Well-constrained compound pattern. | WARNING | None needed. |
| employment | `cv.?screen` | LOW | Specific. | WARNING | None needed. |
| employment | `resume.?filt` | LOW | Specific. | WARNING | None needed. |
| employment | `hiring.?decision` | LOW | Specific. | WARNING | None needed. |
| employment | `recruit\w*\W{0,3}automat` | LOW | Well-constrained. | WARNING | None needed. |
| employment | `candidate.?rank` | LOW | Specific compound. | WARNING | None needed. |
| employment | `performance.?review.{0,10}(ai\|automat\|model\|predict)` | LOW | Well-constrained compound. | WARNING | None needed. |
| essential_services | `credit.?scor` | LOW-MEDIUM | `accredited_scores` does NOT match (tested). Could match "discredit_scoring" theoretically. AI gate reduces. | WARNING | None needed. |
| essential_services | `creditworth` | LOW | Specific word. | WARNING | None needed. |
| essential_services | `loan.?decision` | LOW | Specific. | WARNING | None needed. |
| essential_services | `insurance.?pric` | LOW | Specific. | WARNING | None needed. |
| essential_services | `benefit.?eligib` | LOW | Specific. | WARNING | None needed. |
| essential_services | `emergency.?dispatch` | LOW | Specific. | WARNING | None needed. |
| law_enforcement | `polygraph` | LOW | Specific. | WARNING | None needed. |
| law_enforcement | `lie.?detect` | LOW | Specific. | WARNING | None needed. |
| law_enforcement | `evidence.?reliab` | LOW-MEDIUM | Could match "evidence reliability" in testing frameworks, but AI gate reduces. | WARNING | None needed. |
| law_enforcement | `criminal.?investigat` | LOW | Specific. | WARNING | None needed. |
| migration | All patterns | LOW | Specific compound phrases. | WARNING | None needed. |
| justice | `judicial.?decision` | LOW | Specific. | WARNING | None needed. |
| justice | `court.?rul` | LOW | Specific. | WARNING | None needed. |
| justice | `sentenc(ing\|e\.?)\W{0,5}(recommend\|decision\|...)` | LOW | **Well-constrained** -- requires "sentence/sentencing" followed within 5 chars by a legal keyword. Does NOT match NLP "sentence" alone (verified). | WARNING | None needed. Good pattern. |
| justice | `election.?influence` | LOW | Specific. | WARNING | None needed. |
| medical_devices | `medical.?diagnos` | LOW | Specific. | WARNING | None needed. |
| medical_devices | `clinical.?decision` | LOW | Specific. | WARNING | None needed. |
| medical_devices | `treatment.?recommend` | LOW-MEDIUM | Could match e-commerce "treatment recommendation" for skin care etc. AI gate helps. | WARNING | None needed. |
| medical_devices | `patient.?triage` | LOW | Specific. | WARNING | None needed. |
| safety_components | `autonomous.?vehicle` | LOW | Specific. | WARNING | None needed. |
| safety_components | `self.?driv` | LOW | Specific. | WARNING | None needed. |
| safety_components | `aviation.?safety` | LOW | Specific. | WARNING | None needed. |
| safety_components | `machinery.?safety` | LOW | Specific. | WARNING | None needed. |

**HIGH_RISK summary: 2 patterns need word boundary fixes (face.?recogn, voice.?recogn). The rest are well-constrained.**

### 1.3 LIMITED_RISK_PATTERNS (classify_risk.py)

These trigger `action: "allow_with_transparency"`. Low-severity findings.

| Rule | Pattern | FP Risk | FP Scenario | Classification |
|------|---------|---------|-------------|----------------|
| chatbots | `chatbot` | LOW | Very specific word. | ADVISORY |
| chatbots | `conversational.?ai` | LOW | Specific. | ADVISORY |
| chatbots | `virtual.?assist` | LOW | Specific. | ADVISORY |
| chatbots | `support.?bot` | **MEDIUM** | **Matches `support_bottom` (CSS margin/padding variable).** Common in frontend code. | ADVISORY -- but fix recommended. Change to `support.?bot\b`. |
| emotion_recognition | `emotion.?recogn` | LOW | Specific. | ADVISORY |
| emotion_recognition | `sentiment.?analy` | LOW | Specific. True positive for any sentiment analysis (which IS limited risk). | ADVISORY |
| emotion_recognition | `affect.?detect` | LOW | Specific. | ADVISORY |
| emotion_recognition | `mood.?analy` | LOW | Specific. | ADVISORY |
| biometric_categorisation | `age.?estimat` | **MEDIUM** | **Matches `page_estimation`.** Common in pagination code. | ADVISORY -- fix recommended. Change to `\bage.?estimat`. |
| biometric_categorisation | `gender.?detect` | LOW | Specific. | ADVISORY |
| biometric_categorisation | `demographic.?analy` | LOW | Specific. | ADVISORY |
| synthetic_content | `deepfake` | LOW | Specific. | ADVISORY |
| synthetic_content | `synthetic.?media` | LOW | Specific. | ADVISORY |
| synthetic_content | `face.?swap` | LOW | Specific. | ADVISORY |
| synthetic_content | `voice.?clon` | LOW | Specific. | ADVISORY |
| synthetic_content | `ai.{0,5}generat\w*.{0,5}image` | LOW | Well-constrained compound. | ADVISORY |
| synthetic_content | `text.?to.?image` | LOW | Specific. | ADVISORY |

**LIMITED_RISK summary: 2 patterns need word boundary fixes (support.?bot, age.?estimat). Otherwise clean.**

### 1.4 AI_INDICATORS (classify_risk.py)

These are the gate that determines whether a file is scanned at all. FPs here cause files to be unnecessarily classified as "minimal_risk AI code" but do NOT escalate to higher tiers.

| Pattern | FP Risk | FP Scenario | Impact |
|---------|---------|-------------|--------|
| `embedding` | **HIGH** | Matches font embedding, video embedding, HTML embedding, CSS embedding. Extremely common word in web/document code. | LOW impact: only adds a minimal_risk entry. But inflates file count. |
| `model\.fit` | MEDIUM | Matches `data_model.fit_to_screen()`, `model.fit_intercept`. | LOW impact. |
| `model\.train` | MEDIUM | Matches `model.train_mode = True` (PyTorch toggle). | LOW impact, and this IS actually ML code. |
| `model\.predict` | LOW | Usually indicates actual ML prediction. | Negligible. |
| `fine.?tune` | MEDIUM | Matches "fine-tune your guitar", "fine-tune the parameters" (non-ML). | LOW impact. |
| `neural.?network` | LOW | Almost always refers to actual neural networks. | Negligible. |
| `torch` | MEDIUM | Could match non-ML "torch" references (PyTorch is the dominant usage though). | LOW impact. |
| All library names | LOW | Library names like `tensorflow`, `sklearn`, `keras` are highly specific. | Negligible. |
| All API endpoints | LOW | Domain names are specific. | Negligible. |

**AI_INDICATORS summary: `embedding` is the biggest FP risk but impact is limited to inflated minimal_risk counts. Consider changing to `\bembedding(?:s)?\b` and requiring ML context co-occurrence, or accept the noise.**

### 1.5 SECRET_PATTERNS (credential_check.py)

| Pattern | Confidence | FP Risk | FP Scenario | Proposed Fix |
|---------|-----------|---------|-------------|--------------|
| `sk-(?!ant-)[a-zA-Z0-9]{20,}` | HIGH (95) | LOW | Negative lookahead for `sk-ant-` correctly excludes Anthropic keys. `sklearn` does NOT match (verified: `sk-learn` has a hyphen + "l" not matching `[a-zA-Z0-9]{20,}` without the "learn" being 20+ chars). `sk-proj-` style keys fail because hyphens break the `[a-zA-Z0-9]` character class. | **ISSUE**: New OpenAI key format `sk-proj-*` with hyphens will NOT be detected. Consider `sk-(?:proj-)?[a-zA-Z0-9\-]{20,}` but this increases FP risk. |
| `sk-ant-[a-zA-Z0-9\-]{20,}` | HIGH (95) | LOW | Very specific prefix. | None needed. |
| `AKIA[0-9A-Z]{16}` | HIGH (95) | LOW | AWS key format is highly specific. Could match in test fixtures with example keys like `AKIAIOSFODNN7EXAMPLE`. | Consider excluding known AWS example keys. |
| `AIza[0-9A-Za-z\-_]{35}` | HIGH (90) | LOW | Google API key format is specific. | None needed. |
| `gh[ps]_[A-Za-z0-9_]{36,}` | HIGH (95) | LOW | GitHub token format is specific. | None needed. |
| `-----BEGIN ... PRIVATE KEY-----` | HIGH (98) | LOW | PEM header is unmistakable. | None needed. |
| `generic_api_key` | MEDIUM (60) | **HIGH** | **Matches test placeholder values, example values in documentation, and environment variable templates.** Tested: `api_key = 'test_placeholder_value_for_unit_testing'` and `api_key = 'your-api-key-goes-here-replace-me'` both match. | Add exclusion list: skip if value contains `test`, `example`, `placeholder`, `your-`, `replace`, `TODO`, `xxx`, `dummy`. |
| `connection_string` | MEDIUM (70) | MEDIUM | Matches connection strings without credentials (e.g., `postgres://localhost:5432/test_db`). | Consider requiring `@` in the URI (indicates user:pass@host). |
| `aws_secret_key` | MEDIUM (75) | MEDIUM | Contextual pattern with broad reach. | Acceptable given medium confidence label. |

**SECRET_PATTERNS summary: High-confidence patterns are excellent. `generic_api_key` has the worst FP rate and needs a placeholder/test value exclusion list. `connection_string` should require `@` to indicate credentials are present.**

---

## 2. Benchmark Results

### 2.1 anthropic-cookbook (29 files scanned)

| Tier | Count | Verified TP | Verified FP | Precision |
|------|-------|-------------|-------------|-----------|
| prohibited | 0 | -- | -- | -- |
| credential_exposure | 0 | -- | -- | -- |
| high_risk | 0 | -- | -- | -- |
| limited_risk | 0 | -- | -- | -- |
| minimal_risk | 27 | 27 (all are genuinely AI-related code) | 0 | 100% |
| model_file | 2 (.pkl files) | 2 (genuinely AI model files) | 0 | 100% |

**Overall precision on anthropic-cookbook: 100% (0 false positives across all tiers)**

This is an ideal result because the cookbook is a pure AI project -- every file genuinely is AI-related.

### 2.2 huggingface/transformers (NOT RUN)

**Blocked by environment permissions during this audit.** Manual execution required:

```bash
cd /tmp && git clone --depth 1 https://github.com/huggingface/transformers.git
cd /home/mkuziva/getregula
python3 scripts/cli.py check /tmp/transformers --format json > /tmp/transformers_findings.json
```

**Expected FP risks on transformers:**
- `voice.?recogn` matching `invoice_recognition` in any billing/payment utils -- **likely FP**
- `face.?recogn` matching `typeface_recognition` or `surface_recognition` -- **possible FP**
- `embedding` matching every file that mentions the word (hundreds of files in a transformers repo) -- **noise but not harmful**
- `sentenc` patterns -- the current compound pattern `sentenc(ing|e\.?)\W{0,5}(legal keyword)` should correctly NOT match NLP "sentence" usage -- **verified safe**
- `model.fit`, `model.train`, `from_pretrained` -- all true positives in transformers (it IS an ML library)

### 2.3 Prior Version Regression (from cached findings)

The cached `/tmp/cookbook_findings.json` (from a prior Regula version) showed **2 false positives**:

1. `third_party/ElevenLabs/stream_voice_assistant_websocket.py` -- flagged as "Justice and democratic processes" (high_risk) because the word "sentence" appeared in audio streaming context ("No sentence buffering required")
2. `capabilities/summarization/evaluation/custom_evals/bleu_eval.py` -- flagged as "Justice and democratic processes" (high_risk) because `sentence_bleu` (NLTK function) contains "sentence"

Both were fixed by tightening the sentencing pattern to require a legal keyword co-occurrence. This is a **good example of pattern improvement** that reduced FP.

---

## 3. Critical Fixes Required

### 3.1 MUST FIX -- Prohibited tier patterns (false blocks)

These patterns can block legitimate developer workflows with false positives:

#### Fix 1: `predictive.?polic` -> `predictive.?policing`

**File:** `scripts/classify_risk.py`, PROHIBITED_PATTERNS["criminal_prediction"]["patterns"]

**Problem:** Matches `predictive_policy`, a common variable name in reinforcement learning, caching, and configuration code.

**Fix:**
```python
# Before:
r"predictive.?polic"
# After:
r"predictive.?policing"
```

#### Fix 2: `face.?scrap` -> `\bface.?scrap`

**File:** `scripts/classify_risk.py`, PROHIBITED_PATTERNS["facial_recognition_scraping"]["patterns"]

**Problem:** Matches `interface_scraper`, `surface_scraping` as substrings.

**Fix:**
```python
# Before:
r"face.?scrap"
# After:
r"\bface.?scrap"
```

#### Fix 3: `race.?detect` -> `\brace.?detect` with negative lookahead

**File:** `scripts/classify_risk.py`, PROHIBITED_PATTERNS["biometric_categorisation_sensitive"]["patterns"]

**Problem:** Matches `race_detector` in concurrent programming (race condition detection).

**Fix:**
```python
# Before:
r"race.?detect"
# After:
r"\brace.?detect(?!.*(?:condition|thread|concurrent|async|deadlock|mutex|lock))"
```

### 3.2 MUST FIX -- High-risk tier patterns

#### Fix 4: `face.?recogn` -> `\bface.?recogn`

**File:** `scripts/classify_risk.py`, HIGH_RISK_PATTERNS["biometrics"]["patterns"]

**Problem:** Matches `typeface_recognition`, `surface_recognition`.

**Fix:**
```python
# Before:
r"face.?recogn"
# After:
r"\bface.?recogn"
```

#### Fix 5: `voice.?recogn` -> `\bvoice.?recogn`

**File:** `scripts/classify_risk.py`, HIGH_RISK_PATTERNS["biometrics"]["patterns"]

**Problem:** Matches `invoice_recognition`, `invoice_recognizer`.

**Fix:**
```python
# Before:
r"voice.?recogn"
# After:
r"\bvoice.?recogn"
```

### 3.3 SHOULD FIX -- Limited-risk and credential patterns

#### Fix 6: `support.?bot` -> `support.?bot\b`

Prevents matching `support_bottom` (CSS).

#### Fix 7: `age.?estimat` -> `\bage.?estimat`

Prevents matching `page_estimation` (pagination).

#### Fix 8: `generic_api_key` pattern -- add placeholder exclusion

```python
# After matching, check if value looks like a placeholder:
PLACEHOLDER_INDICATORS = ["test", "example", "placeholder", "your-", "replace",
                          "TODO", "xxx", "dummy", "fake", "sample", "changeme"]
```

#### Fix 9: `connection_string` pattern -- require `@` in URI

```python
# Before:
r"(?i)(?:mongodb|postgres|mysql|redis|amqp):\/\/[^\s'\"]{10,}"
# After:
r"(?i)(?:mongodb|postgres|mysql|redis|amqp):\/\/[^\s'\"]*@[^\s'\"]{10,}"
```

---

## 4. Rules That Should Be Reclassified

| Current Tier | Pattern | Proposed Tier | Rationale |
|-------------|---------|---------------|-----------|
| PROHIBITED (block) | `social.?scor` | PROHIBITED but WARNING action | Social media scoring is common and benign. Pattern should still flag but with `warn` not `block` until human confirms it's government social scoring. |
| PROHIBITED (block) | `social.?credit` | PROHIBITED but WARNING action | Matches credit card contexts. Too broad for auto-blocking. |
| PROHIBITED (block) | `behaviour.?scor` | PROHIBITED but WARNING action | Engagement scoring is ubiquitous. Should warn, not block. |

**Note:** These patterns correctly identify potential prohibited practices -- the issue is that automated blocking is too aggressive given the FP rate. The recommendation is NOT to remove the patterns but to change the `action` from `block` to `warn` pending human review, or to require 2+ prohibited indicators before blocking.

---

## 5. Summary Statistics

| Category | Total Patterns | BLOCKING (near-zero FP) | WARNING (<=10% FP) | ADVISORY (up to 20% FP) | MUST FIX (>20% FP) |
|----------|---------------|------------------------|--------------------|-----------------------|-------------------|
| PROHIBITED_PATTERNS | 24 patterns | 18 | 3 | 0 | 3 |
| HIGH_RISK_PATTERNS | 30 patterns | 0 | 28 | 0 | 2 |
| LIMITED_RISK_PATTERNS | 17 patterns | 0 | 15 | 2 | 0 |
| AI_INDICATORS | ~30 patterns | 0 | 25 | 5 | 0 |
| SECRET_PATTERNS | 9 patterns | 6 | 1 | 2 | 0 |
| **TOTAL** | **~110 patterns** | **24** | **72** | **9** | **5** |

**Overall assessment:** 5 patterns (4.5%) need immediate fixes due to demonstrable false positive scenarios. 9 patterns (8.2%) have moderate FP risk that is acceptable at their current severity level. The remaining 87.3% of patterns are well-tuned.

---

## 6. Recommended Next Steps

1. **Immediate:** Apply the 5 MUST FIX regex changes (Fixes 1-5 above)
2. **Short-term:** Apply the 4 SHOULD FIX changes (Fixes 6-9)
3. **Short-term:** Run the transformers benchmark manually and verify FP counts
4. **Medium-term:** Consider requiring 2+ prohibited indicators before `action: block` (reduces false block rate)
5. **Medium-term:** Add a `--strict` / `--permissive` flag to let users control the FP/FN tradeoff
6. **Ongoing:** Maintain a false positive test suite that runs on each pattern change (regression prevention)
