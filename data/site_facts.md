# Regula — site facts (auto-generated)

*Canonical source of truth for every numeric claim on the landing pages. Regenerate by running `python3 scripts/site_facts.py`.*

Generated: `2026-04-16T21:04:44.660940+00:00`

## Top-line counts

| Claim | Count | Source file |
|---|---|---|
| CLI commands | **53** | `scripts/cli.py` |
| Detection patterns (historical bucket) | **446** | see breakdown below |
| Detection patterns (grand total, inclusive) | **659** | see breakdown below |
| Tiered risk pattern groups | 52 | `scripts/risk_patterns.py` |
| Compliance frameworks | **17** | `references/framework_crosswalk.yaml` + EU AI Act |
| Programming languages | 8 | `scripts/ast_engine.py` |
| Test functions (all files) | 893 | `tests/test_*.py` |

## Detection pattern breakdown

Regula ships detection patterns across three source files. The landing page claim of "403 risk patterns" corresponds to all individual regexes in risk_patterns.py. The `historical_330_bucket` adds architecture, credential, and oversight detectors from code_analysis.py. The `grand_total` also adds `AI_INDICATORS` and is the inclusive upper bound.

| Category | Source | Count |
|---|---|---|
| Tiered risk regexes (prohibited, high-risk, limited-risk, AI security, bias) | `risk_patterns.py` | 386 |
| AI_INDICATORS (libraries, model files, API endpoints, ML patterns, domain keywords) | `risk_patterns.py` | 182 |
| GPAI training code detectors | `risk_patterns.py` | 17 |
| Architecture detectors | `code_analysis.py` | 38 |
| Data source detectors | `code_analysis.py` | 10 |
| Logging detectors | `code_analysis.py` | 4 |
| Oversight detectors | `code_analysis.py` | 4 |
| Credential detectors | `credential_check.py` | 18 |
| **Grand total (inclusive)** | across 3 files | **659** |
| **Historical 330 bucket** | tiered + arch + cred + oversight | **446** |

## Honesty notes

- If a landing page cites a different number, either the page is stale or this generator is stale. Fix whichever is wrong.
- The landing page claim of "403 risk patterns" is the total individual regexes in risk_patterns.py. If the actual count drifts, update the landing page — do not update this generator to match.
- The `historical_330_bucket` includes additional detectors from code_analysis.py. Both numbers are documented above so any auditor can verify.
