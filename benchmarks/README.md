# Regula Benchmark Suite

First calibration run against real-world OSS AI projects. All scans performed on 2026-03-31 using `--depth=1` clones.

## Projects Scanned

| Project | GitHub | Description |
|---------|--------|-------------|
| instructor | https://github.com/jxnl/instructor | Structured LLM output library |
| pydantic-ai | https://github.com/pydantic/pydantic-ai | Agent framework built on Pydantic |
| langchain | https://github.com/langchain-ai/langchain | LLM application framework (monorepo) |
| scikit-learn | https://github.com/scikit-learn/scikit-learn | ML library (Python/Cython) |
| openai-python | https://github.com/openai/openai-python | OpenAI API client |

## Results

| Project | Total | minimal_risk | limited_risk | agent_autonomy | ai_security | credential_exposure | Scan time |
|---------|-------|-------------|-------------|----------------|-------------|--------------------:|-----------|
| instructor | 288 | 285 | 2 | 1 | 0 | 0 | 2.8s |
| pydantic-ai | 353 | 337 | 5 | 4 | 3 | 4 | 9.3s |
| langchain | 2112 | 2069 | 4 | 37 | 1 | 1 | 13.6s |
| scikit-learn | 962 | 894 | 0 | 5 | 63 | 0 | 15.2s |
| openai-python | 401 | 396 | 0 | 4 | 1 | 0 | 3.7s |
| **Totals** | **4116** | **3981** | **11** | **51** | **68** | **5** | **44.7s** |

## Observations

- The vast majority of findings (97%) are `minimal_risk`. This is expected for general-purpose libraries.
- scikit-learn has 63 `ai_security` findings, likely from model serialisation patterns (pickle/joblib).
- langchain has the most `agent_autonomy` findings (37), consistent with its agent orchestration focus.
- `credential_exposure` findings are rare (5 total), mostly in pydantic-ai.
- Scan performance is reasonable: under 16 seconds per project, even for large monorepos.

## Next Steps

These findings need manual labelling as true positive (TP) or false positive (FP) to calculate precision. This is a human task -- the raw JSON files in `results/` contain full finding details for review.

### Labelling Protocol

1. Open `results/<project>.json`
2. For each finding, assess whether the flagged code genuinely represents the identified risk tier
3. Mark as TP (true positive) or FP (false positive)
4. Calculate precision = TP / (TP + FP) per tier
