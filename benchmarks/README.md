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
> Evidence: [`benchmarks/labels.json`](labels.json) and the reproducible scorer in [`benchmarks/label.py`](label.py).

| Cut | TP | FP | Precision |
|---|---:|---:|---:|
| **Overall** (all tiers) | 39 | 218 | **15.2%** |
| `agent_autonomy` | 2 | 3 | 40.0% |
| `limited_risk` | 1 | 2 | 33.3% |
| `minimal_risk` (94% of findings) | 36 | 205 | 14.9% |
| `ai_security` | 0 | 6 | 0.0% |
| `credential_exposure` | 0 | 2 | 0.0% |
Source: [`benchmarks/labels.json`](labels.json), reproduced with [`benchmarks/label.py`](label.py) `score`.

The `minimal_risk` tier dominates and is noisy on library code — these
projects are AI libraries where every file imports AI modules, but most
files are infrastructure (serialisation, API marshalling, config) rather
than risk-bearing application code.

No `prohibited` or `high_risk` findings were generated because library
code does not typically trigger domain-specific patterns (hiring,
credit scoring, biometrics, etc.).

## Precision — Random Corpus, Blind-Labelled

**N=115, labelled by a single reviewer; no inter-rater agreement
measurement exists** (see "Limitations" below).

The measured corpus uses 50 randomly selected Python AI repos
(from a pool of 276, seed=42), scanned with Regula v1.7.0; 201 findings were
stratified-sampled and blind-labelled (labeller saw only file path, code
context, and finding description — no project name, README, or purpose).
Source: [`METHODOLOGY.json`](results/random_corpus/METHODOLOGY.json).

Precision is measured on **production code only** (default `--skip-tests`
settings), which is what users actually see.

| Tier | TP | FP | Precision |
|---|---:|---:|---:|
| `minimal_risk` | 11 | 0 | 100.0% |
| `limited_risk` | 7 | 1 | 87.5% |
| `ai_security` | 41 | 7 | 85.4% |
| `agent_autonomy` | 34 | 7 | 82.9% |
| `credential_exposure` | 1 | 0 | 100.0% |
| `high_risk` | 2 | 4 | 33.3% |
| **Overall** | **96** | **19** | **83.5% (N=115)** |
Source: [`benchmarks/results/random_corpus/BLIND_LABELS.json`](results/random_corpus/BLIND_LABELS.json) and [`METHODOLOGY.json`](results/random_corpus/METHODOLOGY.json).

**Measured v1.7.0 comparison:** production precision changed from 70.0% to
83.5% (+13.5pp) after domain gating, import gating, and pattern changes.
The underlying labels and methodology are in
[`benchmarks/results/random_corpus/`](results/random_corpus/).

**Interpretation:** the measured production subset was 83.5% precise. The
`high_risk` tier result rests on N=6 and is too small for a reliable tier-level
conclusion. See [`METHODOLOGY.json`](results/random_corpus/METHODOLOGY.json).

**Including test code**, the measured precision is 60.6% (N=165).
Source: [`METHODOLOGY.json`](results/random_corpus/METHODOLOGY.json).

**Pattern improvements after the measured version (not yet re-benchmarked against the random corpus):**

Three SUPPRESS_FINGERPRINTS groups added (medical_imaging, experiment_tracking,
database_migration), sensitive_info_disclosure pattern narrowed to require PII
context, employment domain excludes threading/joblib/concurrent.futures. These
changes should reduce false positives but have NOT been measured against the
random corpus because re-scanning requires cloning the 50 repos and re-labelling
new findings. The last verified measurement is the v1.7.0 result recorded in
[`METHODOLOGY.json`](results/random_corpus/METHODOLOGY.json).

**B1 status (June 2026):** The random corpus result reflects domain-gated
scanning (v1.7.0). The high-risk slice is N=6 and does not support a reliable
tier-level conclusion. See [`METHODOLOGY.json`](results/random_corpus/METHODOLOGY.json).
A full rescan of the random corpus with current patterns is needed to verify
whether the post-v1.7.0 improvements affect the 83.5% headline.

**Methodology details and reproducibility, stated exactly.**
`benchmarks/results/random_corpus/METHODOLOGY.json` contains the exact
GitHub API queries, random seed and selected repos, and
`benchmarks/results/random_corpus/BLIND_LABELS.json` contains all 201
blind labels with notes. Those artefacts are tracked, and the arithmetic
inside `PRECISION.json` re-derives from its own tier table. **The 83.5%
figure itself is a dated measurement, not a re-runnable benchmark.** The
per-repository scan outputs that determined which 115 of the 201
labelled findings form the production subset are deliberately untracked
(they embed third-party code excerpts), and `rescan_corpus.py` clones
each repository's current head rather than a pinned commit, so
re-running it scans today's corpus state, not the 25 April 2026 state
the labels were made against. Neither the subset membership nor the
corpus snapshot is reconstructible from a clone. The tracked labels
alone do not reproduce the figure: computed 6 August 2026 from
`BLIND_LABELS.json`, precision over all 201 labels is 51.2% and over a
path-heuristic production subset (139 entries) is 69.8%; both use
different denominators from the published 115 and are stated to show the
subset is not derivable, not as competing headlines. Any future
re-measurement should pin corpus commits and record subset membership in
tracked content so this paragraph can be retired.

## Precision — Development Corpora (internal reference)

These corpora were used during development to tune patterns. They are
**not** published as headline numbers because the corpus selection was
non-random (hand-picked to match specific risk categories).

| Corpus | Labelled | TP | FP | Precision | Note |
|--------|----------|---:|---:|---:|------|
| Hand-picked apps (12 projects) | 189 | 125 | 64 | 66.1% | Cherry-picked to match Annex III categories |
| Library code (5 projects) | 257 | 39 | 218 | 15.2% | AI SDKs — mostly infrastructure code |
Source: [`benchmarks/labels.json`](labels.json) and development-corpus records under [`benchmarks/results/`](results/).

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
| Precision | **83.5%** on random corpus production code (blind-labelled, N=115, single reviewer, no inter-rater agreement — see "Limitations") |
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

1. **Sample size.** The checked-in corpus is too small for dependable
   conclusions about every tier, language, and project type.
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
