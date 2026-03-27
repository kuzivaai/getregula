# Regula Real-World Benchmark Results

**Date:** 2026-03-27
**Test target:** anthropic-cookbook (Anthropic's official cookbook, 81 Python files)
**Regula version:** 1.1.0

---

## anthropic-cookbook

- **Files scanned:** 29 (AI-related files out of 81 total Python files)
- **Scan time:** 0.137s (137ms)
- **Total findings:** 29
- **By tier:** prohibited=0, high_risk=2, limited_risk=0, minimal_risk=27, credential_exposure=0
- **Dependency pinning score:** 50/100 (anthropic >=0.71.0, lockfile present: uv.lock)
- **Compliance gap score:** 79%

### Manual Review of High-Risk Findings (2 findings)

| Finding | File | Trigger | Actual Code | Verdict |
|---------|------|---------|-------------|---------|
| 1 | `third_party/ElevenLabs/stream_voice_assistant_websocket.py` | `sentenc` pattern matched (justice category) | Comment: "No **sentence** buffering required" | **FALSE POSITIVE** |
| 2 | `capabilities/summarization/evaluation/custom_evals/bleu_eval.py` | `sentenc` pattern matched (justice category) | `from nltk.translate.bleu_score import **sentence**_bleu` | **FALSE POSITIVE** |

### Precision: 0% for high-risk findings (0/2 true positives)

Both high-risk findings are false positives caused by the `sentenc` regex in `HIGH_RISK_PATTERNS["justice"]` matching the English word "sentence" in non-judicial contexts (NLP sentence tokenisation, audio sentence buffering).

### Minimal-Risk Findings (27 findings)

All 27 minimal-risk findings correctly identify files that import AI libraries (`anthropic`, `openai`, etc.). These are true positives — the files genuinely contain AI code. However, "minimal_risk: AI-related code with no specific risk indicators" provides little actionable value to a DPO.

### Dependency Analysis

Correctly identified `anthropic>=0.71.0` as a range-pinned AI dependency. Correctly detected `uv.lock` as a lockfile. Score of 50/100 is reasonable — the project uses ranges, not exact pins, but has a lockfile.

### Compliance Gap Assessment

79% overall score. Notable:
- Article 9 (Risk Management): 100% — correctly found risk management content in financial model docs
- Article 13 (Transparency): 100% — correctly found capability/limitation docs and AI disclosure notices
- Article 11 (Technical Documentation): 25% — correctly identified missing Annex IV and model cards
- Article 10 (Data Governance): 65% — correctly noted missing bias detection libraries

The gap assessment produces genuinely useful output for this project.

---

## Overall Assessment

- **Scan speed:** Excellent (137ms for 81 files). Viable for CI/CD.
- **High-risk precision:** 0% (2/2 false positives). The `sentenc` regex is a critical pattern quality issue.
- **Minimal-risk accuracy:** 100% (27/27 true positives). But low actionable value.
- **Dependency scan:** Accurate and useful.
- **Gap assessment:** Accurate and useful. The most valuable output for a DPO.
- **Would a governance professional find this useful?** The gap assessment and dependency scan: yes. The risk classification: not yet — false positive rate on high-risk findings is too high for production use.

### Root Cause of False Positives

The `justice` category in `HIGH_RISK_PATTERNS` contains `r"sentenc"` which matches:
- `sentence_bleu` (BLEU score computation)
- "sentence buffering" (audio streaming)
- "sentence tokenization" (NLP)
- Any use of the English word "sentence"

This pattern needs to be more specific: `r"sentenc\w*\W{0,3}(court|judge|judicial|legal|criminal|verdict)"` or similar context-requiring pattern.

### Key Finding

The compliance gap assessment (`regula gap`) and dependency scan (`regula deps`) are production-ready and produce genuinely useful output. The risk classification (`regula check`) has pattern quality issues that generate false positives on real codebases. The AST engine helps for Python but the regex patterns need refinement.
