# Regula Benchmark Suite

Precision measurement for Regula's risk detection across two corpora:
a **library corpus** (AI SDKs/frameworks) and an **application corpus**
(real-world AI applications spanning EU AI Act risk categories).

## Methodology

See [LABELLING_CRITERIA.md](LABELLING_CRITERIA.md) for the full labelling
protocol, TP/FP definitions, and metrics computation.

### Key points

- All scans use `--depth=1` shallow clones
- Findings are labelled as **TP** (true positive — genuinely risky code)
  or **FP** (false positive — pattern matched but not a real risk)
- Precision = TP / (TP + FP)
- Labels reflect one reviewer's judgement (no peer validation yet — P2)
- Recall is measured separately via synthetic fixtures only

## Corpora

### Library Corpus (baseline)

AI frameworks and SDKs. These contain mostly infrastructure code, so
precision is expected to be lower than on application code.

| Project | GitHub | Description |
|---------|--------|-------------|
| instructor | github.com/jxnl/instructor | Structured LLM output library |
| pydantic-ai | github.com/pydantic/pydantic-ai | Agent framework built on Pydantic |
| langchain | github.com/langchain-ai/langchain | LLM application framework (monorepo) |
| scikit-learn | github.com/scikit-learn/scikit-learn | ML library (Python/Cython) |
| openai-python | github.com/openai/openai-python | OpenAI API client |

### Application Corpus

Real-world AI applications across EU AI Act risk categories. These
contain application-level code where risk patterns are more likely to be
genuine, so precision is expected to be higher.

| Project | GitHub | EU AI Act Category |
|---------|--------|--------------------|
| app_aider | github.com/Aider-AI/aider | Agent Autonomy — AI coding assistant |
| app_crewai | github.com/crewAIInc/crewAI | Agent Autonomy — multi-agent framework |
| app_openadapt | github.com/OpenAdaptAI/OpenAdapt | Annex III 4(b) — worker monitoring/RPA |
| app_privategpt | github.com/zylon-ai/private-gpt | Limited Risk — RAG/document QA |
| app_quivr | github.com/QuivrHQ/quivr | Limited Risk — knowledge management |
| app_resume_matcher | github.com/srbhr/Resume-Matcher | Annex III 6(a) — recruitment/candidate ranking |
| app_monai | github.com/Project-MONAI/MONAI | Annex III 5(c) — medical imaging/diagnosis |
| app_deepface | github.com/serengil/deepface | Article 5 / Annex III — facial recognition |
| app_rasa | github.com/RasaHQ/rasa | Article 50 — conversational AI/chatbot |
| app_frigate | github.com/blakeblackshear/frigate | Annex III — real-time CV/surveillance |
| app_toad | github.com/amphibian-dev/toad | Annex III 5(b) — credit scorecard |
| app_proctoring | github.com/vardanagarwal/Proctoring-AI | Annex III 3(a) — exam proctoring |

## Precision — Library Corpus

Labels from 2026-04-01, re-validated 2026-04-07 (257 hand-labelled findings).

> **Re-validation note.** Pattern files changed six times since labelling.
> A full rescan on 2026-04-07 found 252 of 257 labels (98%) still match
> current output. Precision on the matched subset is 15.1% — within 0.1pp
> of the published 15.2%.
>
> **Coverage caveat.** The rescan produced 3,927 unlabelled findings.
> Published precision covers ~6% of current scanner output on these repos.

| Cut | TP | FP | Precision |
|---|---:|---:|---:|
| **Overall** (all tiers) | 39 | 218 | **15.2%** |
| `agent_autonomy` | 2 | 3 | 40.0% |
| `limited_risk` | 1 | 2 | 33.3% |
| `minimal_risk` (94% of findings) | 36 | 205 | 14.9% |
| `ai_security` | 0 | 6 | 0.0% |
| `credential_exposure` | 0 | 2 | 0.0% |

The `minimal_risk` tier dominates and is noisy on library code — these
projects are AI libraries where every file imports AI modules, but most
files are infrastructure (serialisation, API marshalling, config) rather
than risk-bearing application code.

No `prohibited` or `high_risk` findings were generated because library
code does not typically trigger domain-specific patterns (hiring,
credit scoring, biometrics, etc.).

## Precision — Random Corpus, Blind-Labelled (81.4%)

**This is the headline number.** 50 randomly selected Python AI repos
(from a pool of 276, seed=42), scanned with Regula v1.7.0, 201 findings
stratified-sampled and blind-labelled (labeller saw only file path, code
context, and finding description — no project name, README, or purpose).

Precision is measured on **production code only** (default `--skip-tests`
settings), which is what users actually see.

| Tier | TP | FP | Precision |
|---|---:|---:|---:|
| `minimal_risk` | 11 | 0 | 100.0% |
| `limited_risk` | 7 | 1 | 87.5% |
| `ai_security` | 41 | 7 | 85.4% |
| `agent_autonomy` | 34 | 7 | 82.9% |
| `credential_exposure` | 1 | 0 | 100.0% |
| `high_risk` | 2 | 7 | 22.2% |
| **Overall** | **96** | **22** | **81.4% (N=118)** |

**Improvement from v1.7.0:** Production precision improved from 70.0% to
81.4% (+11.4pp) via three changes: (1) domain-gated high-risk findings
(16 FP removed, 0 TP lost), (2) LLM import gating for OWASP findings
(4 FP removed, 3 borderline TP lost), (3) pattern fixes (pipeline/ControlNet
separation, worker exclusion).

**What this means:** About 8 in 10 of Regula's findings on production
code in a random AI project are genuine risk indicators. The `high_risk`
tier (22%) remains weakest — 6 domain keyword subcategories now require
`--domain` declaration or import fingerprinting to fire. The structural
tiers (`ai_security`, `agent_autonomy`, `limited_risk`, `minimal_risk`)
are all above 80% because they match on code patterns (deserialization,
subprocess calls, API calls, model files) rather than keywords.

**Including test code** (what users see with `--no-skip-tests`), overall
precision is 59.5% (N=168, was 51.2%).

**Methodology details:** `benchmarks/results/random_corpus/METHODOLOGY.json`
contains the exact GitHub API queries, random seed, and selected repos.
`benchmarks/results/random_corpus/BLIND_LABELS.json` contains all 201
labels with notes. Fully reproducible.

## Precision — Development Corpora (internal reference)

These corpora were used during development to tune patterns. They are
**not** published as headline numbers because the corpus selection was
non-random (hand-picked to match specific risk categories).

| Corpus | Labelled | TP | FP | Precision | Note |
|--------|----------|---:|---:|---:|------|
| Hand-picked apps (12 projects) | 189 | 125 | 64 | 66.1% | Cherry-picked to match Annex III categories |
| Library code (5 projects) | 257 | 39 | 218 | 15.2% | AI SDKs — mostly infrastructure code |

## Scan Summary — Application Corpus

| Project | Findings | Tiers |
|---------|----------|-------|
| app_crewai | 115 | agent_autonomy:86, ai_security:15, high_risk:10, credential_exposure:3, limited_risk:1 |
| app_deepface | 32 | high_risk:30, ai_security:2 |
| app_frigate | 22 | high_risk:19, agent_autonomy:3 |
| app_monai | 20 | high_risk:12, ai_security:6, limited_risk:2 |
| app_aider | 18 | agent_autonomy:14, ai_security:3, credential_exposure:1 |
| app_openadapt | 8 | ai_security:7, high_risk:1 |
| app_privategpt | 8 | ai_security:6, limited_risk:1, minimal_risk:1 |
| app_resume_matcher | 4 | high_risk:3, minimal_risk:1 |
| app_proctoring | 2 | ai_security:1, minimal_risk:1 |
| app_toad | 2 | ai_security:1, high_risk:1 |
| app_rasa | 2 | ai_security:1, credential_exposure:1 |
| app_quivr | 1 | limited_risk:1 |
| **Total** | **234** | |

## Metrics

| Metric | Status |
|--------|--------|
| Precision | **81.4%** on random corpus production code (blind-labelled, N=118) |
| Recall | Measured on synthetic fixtures only (`benchmarks/synthetic/run.py`) |
| F1 Score | Not computable (requires recall on same corpus as precision) |
| Youden Index (J) | Not computable (requires TN count — OWASP standard) |
| MCC | Not computable (requires TN and FN counts) |

**Why recall-dependent metrics are absent.** Precision measures "of the
findings Regula emits, how many are genuine?" Recall measures "of the
genuine risks in the code, how many does Regula find?" Computing recall
requires a corpus with exhaustively known ground truth (all risks
catalogued). The synthetic fixtures provide controlled recall measurement,
but combining synthetic recall with real-world precision into a single F1
would conflate two different corpora and is methodologically unsound.

## Limitations

1. **Sample size.** 257 library labels + 234 app findings is small by
   SAST benchmark standards (OWASP uses 2,740 test cases).
2. **Single reviewer.** All labels are from one reviewer. No inter-rater
   agreement measurement exists (target: P2).
3. **Python only.** All benchmarked projects are Python. Regula supports
   8 language families but precision is unmeasured for non-Python code.
4. **No prohibited-tier apps.** No open-source project explicitly
   implements Article 5 prohibited practices, so prohibited-tier
   precision cannot be measured from real-world code.
5. **Snapshot in time.** Labels are tied to specific pattern and project
   versions. Pattern changes can move precision in either direction.

## CI Integration

The `benchmark.yml` workflow runs on every PR that touches pattern files
(`risk_patterns.py`, `classify_risk.py`, `report.py`). It:

1. Scores the current labels and reports precision
2. Compares with the baseline PRECISION.json
3. Uploads the precision report as an artifact
4. Runs synthetic recall tests

No hard failure threshold is set yet — the workflow makes precision
visible on every pattern change PR.

## Reproduce

```bash
# Rescan all projects (library + app)
python3 benchmarks/run_benchmark.py

# Rescan only libraries / only apps
python3 benchmarks/run_benchmark.py --corpus lib
python3 benchmarks/run_benchmark.py --corpus app

# Sample findings for labelling
python3 benchmarks/label.py sample                    # all
python3 benchmarks/label.py sample --corpus app       # apps only

# Score precision
python3 benchmarks/label.py score                     # all labels
python3 benchmarks/label.py score --corpus app        # app corpus only
python3 benchmarks/label.py score --breakdown         # add category/language tables

# Compare with a baseline
python3 benchmarks/label.py compare path/to/old/PRECISION.json

# Synthetic recall
python3 benchmarks/synthetic/run.py
```
