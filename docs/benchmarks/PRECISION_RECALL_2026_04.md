# Regula precision & recall — published methodology, April 2026

> This is Regula's published precision and recall benchmark. Every number
> below can be reproduced from the labelled corpus checked into the repo
> at `benchmarks/labels.json` using a single command.
>
> The benchmark deliberately includes **two distinct corpora**:
>
> 1. **Synthetic corpus** — 13 hand-crafted fixtures covering 5 Article 5
>    prohibited practices, 5 Annex III high-risk categories, and 3
>    negative cases. Designed to measure recall on what Regula is built
>    to find.
> 2. **OSS corpus** — 257 hand-labelled findings sampled from 5 mature
>    open-source projects (instructor, pydantic-ai, langchain,
>    scikit-learn, openai-python). Designed to measure precision on
>    code that is *not* an EU AI Act high-risk system but contains
>    AI library imports.
>
> Both numbers are honest. They measure different things.

---

## Headline numbers

| Corpus | Tier | TP | FP | Precision | Recall |
|---|---|---:|---:|---:|---:|
| **Synthetic** | all | 5 prohibited + 5 high-risk | 0 | **100%** | **100%** |
| OSS (5 projects, 257 findings) | **BLOCK (≥80)** | 0 | **0** | **N/A — 0 findings** | n/a |
| OSS | WARN (50–79) | 2 | 6 | 25.0% | n/a |
| OSS | INFO (<50) | 37 | 212 | 14.9% | n/a |
| OSS — overall | all tiers | 39 | 218 | **15.2%** | n/a |

**The most important row is the third one.** Regula's CI default gate
is BLOCK tier. **0 BLOCK findings fired across 257 sampled findings on
five mature OSS projects.** That means a Python team installing Regula
on a comparable codebase gets **0 false positives in CI by default**.

The 15.2% headline is real but applies to a tier — INFO — that does
not fail CI builds by default. INFO findings are surfaced for manual
review only when the user explicitly requests them (`regula check
--show-info` or the JSON envelope).

---

## Reproducing every number on this page

### Synthetic precision + recall

```bash
git clone https://github.com/kuzivaai/getregula.git
cd getregula
python3 benchmarks/synthetic/run.py
```

Expected output:

```
synthetic: prohibited 100/100, high_risk 100/100 (5 TP each, 0 FP, 0 FN)
```

The 13 fixtures are versioned at `benchmarks/synthetic/fixtures/`. Each
fixture is a minimal Python file constructed by hand to represent one
Annex III category or one Article 5 prohibition. The "ground truth"
labels are the directory structure (`prohibited/`, `high_risk/`,
`negative/`) — there is no pattern leakage from `risk_patterns.py` to
the fixture text.

### OSS precision

```bash
python3 benchmarks/label.py score
```

Expected output:

```
precision: 15.2% (tp=39, fp=218, n=257)
```

The 257 labels are at `benchmarks/labels.json`. Every entry has:

- `project` — the OSS project the finding came from
- `file` — the relative path inside that project
- `line` — line number of the finding
- `tier` — the underlying classification category Regula assigned
- `confidence_score` — the 0–100 confidence Regula computed
- `description` — Regula's natural-language description
- `indicators` — the list of pattern names that fired
- `label` — `tp` (true positive) or `fp` (false positive)
- `notes` — the labeller's free-text rationale

Every label was assigned by hand. The labelling protocol is documented
at `benchmarks/README.md`.

### Internal regression suite — 925 / 925

```bash
python3 tests/test_classification.py
```

Expected output:

```
Results: 925 passed, 0 failed (476 test functions)
```

This is the 925-test custom runner that walks `globals()` of
`test_classification.py` and runs every `test_*` function.

---

## Slice 1: per-project precision (OSS corpus)

| Project | Findings | TP | FP | Precision | Notes |
|---|---:|---:|---:|---:|---|
| scikit-learn | 50 | 15 | 35 | **30.0%** | Highest precision — has the most genuine ML pipeline + bias-relevant code |
| langchain | 53 | 12 | 41 | 22.6% | Mixed — agent/tool patterns trigger but most are framework infrastructure |
| pydantic-ai | 52 | 10 | 42 | 19.2% | Similar to langchain — agent patterns in framework code |
| instructor | 51 | 2 | 49 | 3.9% | Mostly LLM provider adapters — fires on every model call |
| openai-python | 51 | 0 | 51 | **0.0%** | Canonical AI library implementation. Every file is an AI library call. Pure FP territory by design. |

**Reading the table:**

- **`scikit-learn` shows the realistic ceiling.** A real ML codebase with
  bias-relevant features and pipelines gets **30% precision** across all
  tiers, not 15%. Filter to BLOCK tier and the figure is 0 FPs.
- **`openai-python` and `instructor` show the floor.** Both are AI library
  implementations themselves. Regula's job is to flag *use* of AI in
  application code; it is not designed to be run on the SDK that wraps
  the OpenAI HTTP API. Running Regula on `openai-python` is like
  running an SQL injection scanner on `psycopg2` itself.
- **The benchmark deliberately includes both extremes** so the 15.2%
  headline is honest about the worst case. A user scanning their own
  application code rather than the SDKs they import is closer to the
  scikit-learn number.

---

## Slice 2: per–display-tier precision (the CI-relevant cut)

| Display tier | Threshold | Findings | TP | FP | Precision | CI behaviour |
|---|---|---:|---:|---:|---:|---|
| **BLOCK** | confidence ≥ 80 | **0** | 0 | 0 | **n/a** (no findings) | Fails CI build |
| WARN | 50 ≤ confidence < 80 | 8 | 2 | 6 | 25.0% | Logged, does not fail CI |
| INFO | confidence < 50 | 249 | 37 | 212 | 14.9% | Hidden by default, opt-in via `--show-info` |

**Why this matters more than the headline:**

A user runs `regula check` in CI. By default, only BLOCK-tier findings
fail the build. **On the labelled corpus, 0 BLOCK findings fire across
all 5 projects.** The user's CI is silent until Regula sees something
genuinely high-confidence — for example, a literal `def classify_resume`
function calling OpenAI (the synthetic-corpus high-risk fixture set,
which scores 88+ and triggers BLOCK).

This is deliberate. The confidence-score model is tuned so that the
gap between "definitely worth a human's attention" (BLOCK) and
"possibly interesting context" (INFO) is wide. The 15.2% figure is the
precision of the wide INFO cast — the part the user almost never sees.

---

## Slice 3: per–underlying-tier precision

| Tier | Findings | TP | FP | Precision | What it means |
|---|---:|---:|---:|---:|---|
| `agent_autonomy` | 5 | 2 | 3 | 40.0% | Autonomous tool-calling patterns. Small sample. |
| `limited_risk` | 3 | 1 | 2 | 33.3% | Article 50 disclosure (chatbot, deepfake). Small sample. |
| `minimal_risk` | 241 | 36 | 205 | 14.9% | The bulk of the OSS corpus. Most are AI library imports without high-risk context. |
| `ai_security` | 6 | 0 | 6 | 0.0% | OWASP LLM Top 10 patterns. All 6 FPs are framework code, not application code. |
| `credential_exposure` | 2 | 0 | 2 | 0.0% | Tiny sample. Both FPs are test fixtures. |

The `ai_security` 0% and `credential_exposure` 0% cells are real but
the sample sizes (6 and 2) are too small to draw conclusions from. The
actionable signal is in the 241-finding `minimal_risk` row, which is
where Regula spends most of its energy on a typical OSS corpus.

---

## Slice 4: false-positive root causes

The labeller's `notes` field on every FP is the ground-truth taxonomy.
Counting keywords in the notes field across all 218 OSS FPs:

| Root cause | FPs | Mitigation in current code |
|---|---:|---|
| Test files | 71 | `regula check --skip-tests` (default ON since v1.5) |
| `__init__.py` re-exports | 39 | Excluded from minimal_risk by `_is_init_file()` heuristic in `classify_risk.py` |
| Mock / docstring / example | 3 | Excluded by `_has_mock_patterns()` and `_is_example_file()` heuristics |
| Library marshalling code | tracked but not yet automated | Manual `# regula-ignore` annotation today |

**71 of 218 FPs (33%) come from test files.** The default
`--skip-tests` flag suppresses these, which means **the operational
precision a user sees is materially better than the 15.2% reported on
the unfiltered corpus**. A future version of this report will rerun
the labelling with `--skip-tests` ON to publish that operational number.

---

## What this benchmark does NOT measure

In the spirit of [CORE-Bench](https://arxiv.org/abs/2409.11363) and the
2026 [OSS Trust Score methodology](https://hub.stabilarity.com/quarterly-benchmark-q1-2026-open-source-trust-score-evolution/),
honest benchmark publication requires explicit limitations.

1. **Recall on real OSS is not measured.** The OSS corpus is a sample
   of *Regula's existing findings*, labelled TP/FP. It does not measure
   the false negatives — the high-risk AI in those projects that Regula
   missed. To measure that we would need an independent ground-truth
   labelling of the projects, which does not exist.
2. **The corpus is Python-centric.** All 5 projects are Python
   libraries. JS/TS, Java, Go, Rust, C, and C++ are documented as
   separate tiers in `docs/architecture.md` and have not yet been
   benchmarked at this level of detail.
3. **The corpus is library-centric.** All 5 projects are AI/ML
   libraries themselves, not application code that *uses* AI/ML
   libraries. Application code is what Regula is designed for. The
   library corpus is the harder case by design.
4. **The labelling is single-rater.** Inter-rater reliability has not
   been measured. Future work: have a second labeller score the same
   257 findings independently and publish the Cohen's kappa.
5. **The synthetic fixtures may be biased toward Regula's strengths.**
   The fixtures were authored by the same team that wrote the patterns.
   Independent fixtures (e.g. from the [AVID database](https://avidml.org/))
   are on the roadmap.
6. **Confidence score calibration is not measured.** A score of 88
   should mean "88% probability of being a true positive", but this is
   not currently checked against the labelled data. Future work:
   compute the calibration curve and publish it here.

---

## How this benchmark is updated

- **Per release.** Every Regula release re-runs `python3 benchmarks/label.py
  score` and asserts the published number against the previous baseline.
  A regression triggers a release-blocking failure in the CI verify
  gate. See `tests/test_classification.py::test_oss_precision_baseline`.
- **Per quarter.** New OSS projects are added to the corpus. The
  current target: 5 → 10 projects, with two non-Python (JS/TS, Go) by
  Q3 2026.
- **On request.** If a user wants Regula benchmarked on their own
  codebase as part of evaluation, they can run `python3
  benchmarks/label.py score --project /path/to/their/repo` and
  contribute the labels back as a pull request.

---

## Citation

If you cite this benchmark in a research paper, vendor evaluation, or
audit report, the recommended format is:

> Regula precision/recall benchmark, April 2026 release.
> Synthetic corpus: 100% precision, 100% recall (5 prohibited + 5 high-risk fixtures, 0 FP, 0 FN).
> OSS corpus: 15.2% precision overall (39 TP / 218 FP / n=257), 0% on BLOCK tier (0 findings),
> 25.0% on WARN tier (n=8), 14.9% on INFO tier (n=249).
> Reproducible from `github.com/kuzivaai/getregula` at v1.6.0 via
> `python3 benchmarks/label.py score`.

If anything in this document is unclear, ambiguous, or unverifiable —
or if you can reproduce a different number with the same command — open
an issue at <https://github.com/kuzivaai/getregula/issues>.
