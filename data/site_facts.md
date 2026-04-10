# Regula — site facts (auto-generated)

*Canonical source of truth for every numeric claim on the landing pages. Regenerate by running `python3 scripts/site_facts.py`.*

Generated: `2026-04-10T18:14:25.940406+00:00`

## Top-line counts

| Claim | Count | Source file |
|---|---|---|
| CLI commands | **43** | `scripts/cli.py` |
| Detection patterns (historical 330 bucket) | **330** | see breakdown below |
| Detection patterns (grand total, inclusive) | **502** | see breakdown below |
| Tiered risk pattern groups | 34 | `scripts/risk_patterns.py` |
| Compliance frameworks | **12** | `references/framework_crosswalk.yaml` + EU AI Act |
| Programming languages | 8 | `scripts/ast_engine.py` |
| Test functions (all files) | 688 | `tests/test_*.py` |

## Detection pattern breakdown

Regula ships detection patterns across three source files. The landing page claim of "330 risk patterns" corresponds to the `historical_330_bucket` figure below: tiered risk regexes plus architecture, credential, and oversight detectors. The `grand_total` figure is the inclusive upper bound, adding `AI_INDICATORS` (what Regula uses to recognise AI code at all) and `GPAI_TRAINING_PATTERNS` (training-code detectors). Both numbers are honest; the landing page figure is the historical mid-range.

| Category | Source | Count |
|---|---|---|
| Tiered risk regexes (prohibited, high-risk, limited-risk, AI security, bias) | `risk_patterns.py` | 279 |
| AI_INDICATORS (libraries, model files, API endpoints, ML patterns, domain keywords) | `risk_patterns.py` | 141 |
| GPAI training code detectors | `risk_patterns.py` | 17 |
| Architecture detectors | `code_analysis.py` | 38 |
| Data source detectors | `code_analysis.py` | 10 |
| Logging detectors | `code_analysis.py` | 4 |
| Oversight detectors | `code_analysis.py` | 4 |
| Credential detectors | `credential_check.py` | 9 |
| **Grand total (inclusive)** | across 3 files | **502** |
| **Historical 330 bucket** | tiered + arch + cred + oversight | **330** |

## Honesty notes

- If a landing page cites a different number, either the page is stale or this generator is stale. Fix whichever is wrong.
- The `historical_330_bucket` is the bucketing used when the "330 risk patterns" claim was originally authored. If the actual computed value drifts materially from 330, update the landing page claim — do not update this generator to match the page.
- "330" is a historical mid-range, not a precise count. The grand total (inclusive) is higher; the strict-tiered count is lower. Both are documented above so any auditor can verify.
