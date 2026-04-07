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

## Precision (measured 2026-04-01)

After hand-labelling 257 findings sampled across the five projects above
(see `labels.json`), the measured precision is in `results/PRECISION.json`.
Headline:

| Cut | TP | FP | Precision |
|---|---:|---:|---:|
| **Overall** (all tiers) | 39 | 218 | **15.2%** |
| `agent_autonomy` | 2 | 3 | 40.0% |
| `limited_risk` | 1 | 2 | 33.3% |
| `minimal_risk` (94% of findings) | 36 | 205 | 14.9% |
| `ai_security` | 0 | 6 | 0.0% |
| `credential_exposure` | 0 | 2 | 0.0% |

This is the honest current state. The minimal_risk tier dominates the
sample and is noisy on general-purpose libraries — that is the next
pattern-tuning target. The labelled sample contains no `prohibited` or
`high_risk` findings because none of the five OSS libraries scanned
actually trigger those tiers, so precision for those tiers cannot be
estimated from this benchmark.

**Limitations of this benchmark.** N=257 hand-labelled findings is small.
Recall is not estimable from labelled findings alone (we don't know what
the scanner missed). Labels reflect one reviewer's judgement and are not
peer-validated. Numbers are tied to Regula's pattern set as of
2026-04-01 and may move as patterns evolve. **No "99%" claim is being
made and none should be.**

## Reproduce

```bash
python3 benchmarks/run_benchmark.py        # rescan all five projects (shallow clones)
python3 benchmarks/label.py sample         # sample new findings for labelling
python3 benchmarks/label.py score          # recompute precision from labels.json
```

The first command shallow-clones each repo, runs `regula check`, and
writes per-project JSON to `results/`. `label.py score` reads
`labels.json` and recomputes the table above. The labels in
`labels.json` are keyed by project + file + line so you can re-import
them after a rescan without re-labelling from scratch.
