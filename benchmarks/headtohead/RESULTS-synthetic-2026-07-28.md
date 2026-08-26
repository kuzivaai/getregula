# Synthetic-corpus baseline — Regula only, 28 July 2026

## READ THIS FIRST: this is NOT the head-to-head

The pre-registered head-to-head **did not run and could not run.** What ran
is a single-tool baseline for Regula against the synthetic ground-truth
fixture set. Calling it a head-to-head would be false.

**Why the comparative run is still blocked**, MEASURED 28 Jul 2026:

1. **All three competitor adapters raise by design.** `adapters.py` defines
   `run_air_blackbox`, `run_systima` and `run_ark_forge` as calls to
   `_not_yet(...)`, which raises `NotImplementedError`. This is the
   deliberate refuse-to-guess design: mappings must be written against each
   tool's CURRENT output format at run time, per PREREGISTRATION rule 3.
2. **None of the competitor tools is installed.** `air_blackbox` is not
   importable; `systima` is not on PATH.

So blocker 2 in PREREGISTRATION.md ("adapter implementation for the three
competitor tools") stands, untouched. Only blocker 1, the ground-truth
gate, was addressed by the owner's authorisation.

## Deviation from the pre-registration, declared

PREREGISTRATION commitment 5 defines the corpus as the random-corpus
repositories **plus** the synthetic fixture set. **This run used the
synthetic fixture set only.**

**Justification, per the requirement that any deviation carry one in
writing:** commitment 6 gates scoring on the multi-annotator corpus
reaching two independent raters, because scoring against single-rater
labels would import the exact weakness the corpus upgrade exists to fix.
Rater 2 is not recruited. The synthetic subset is not affected by that gate
because its ground truth is true by construction, not by annotation: each
fixture is hand-built to contain one unambiguous example of its labelled
tier. The random-corpus half remains gated and was not run.

This deviation was authorised by the owner before the run, on that
reasoning, and is recorded here rather than in a commit message alone.

**No corpus was added or removed.** No metric was chosen after seeing
results. The manifest (`benchmarks/synthetic/manifest.json`, version 1.0)
was fixed before the run.

## What ran

- Tool: Regula at branch tip `improvement/2026-08-programme`
- Invocation: `python3 -m scripts.cli check <fixture> --format json`, via
  the committed `adapters.run_regula`, unmodified
- Corpus: `benchmarks/synthetic/fixtures/`, 13 fixtures
- Raw output committed at
  `benchmarks/headtohead/results/regula-synthetic-2026-07-28.json`

## Results (MEASURED)

| Class | Fixtures | Recall | False positives on other classes |
|---|---|---|---|
| Prohibited (Art. 5) | 5 | **5/5 = 100%** | 0 |
| High risk (Annex III) | 5 | **4/5 = 80%** | 0 |
| Negative controls | 3 | n/a | **0** high-risk firings |
Derived from the committed raw output at benchmarks/headtohead/results/regula-synthetic-2026-07-28.json, which carries one record per fixture: of the 5 prohibited fixtures, 5 report tier prohibited; of the 5 high-risk fixtures, 4 report tier high_risk, the miss being highrisk_employment.py, which reports ai_security only; and none of the 3 negative controls reports high_risk.

Per fixture:

| Fixture | Expected | Tiers found |
|---|---|---|
| `prohibited_art5_1a.py` | prohibited | prohibited |
| `prohibited_art5_1b.py` | prohibited | prohibited |
| `prohibited_art5_1c.py` | prohibited | prohibited |
| `prohibited_art5_1d.py` | prohibited | prohibited |
| `prohibited_art5_1e.py` | prohibited | prohibited |
| `highrisk_biometrics.py` | high_risk | high_risk |
| `highrisk_credit.py` | high_risk | high_risk |
| `highrisk_medical.py` | high_risk | ai_security, high_risk |
| `highrisk_migration.py` | high_risk | high_risk |
| **`highrisk_employment.py`** | **high_risk** | **ai_security only** |
| `negative_chatbot.py` | not_high | ai_security |
| `negative_minimal_ai.py` | not_high | ai_security |
| `negative_pure_utility.py` | not_high | (none) |

## The negative result, stated plainly

**`highrisk_employment.py` is a MISS.** The fixture is hand-built as an
unambiguous Annex III employment case. Regula fired `ai_security` on it and
**did not classify it high risk**. On a corpus whose ground truth is true
by construction, that is a recall failure, not a labelling dispute.

This is worth more than the three passing tiers, because it is the first
measured recall number this project has for the high-risk tier at all.
F11 records that recall has never been measured; this measures it on five
constructed cases and finds 80%.

**Do not generalise it.** Five fixtures is not a recall estimate for real
code. It is an existence proof that at least one constructed Annex III
category does not classify, and it should be traced to its cause before any
Phase 5 work touches the detection layer.

## What this does and does not license saying

**Supported:** on a 13-fixture synthetic corpus with constructed ground
truth, Regula detected 5 of 5 prohibited cases and 4 of 5 high-risk cases,
with zero high-risk false positives on three negative controls.

**NOT supported:** any comparison to any other tool; any recall figure for
real-world code; any claim that the high-risk tier is 80% accurate. The
sample is 13 hand-built files.

**Nothing here goes on a public surface** without going through the
approval gate. It is recorded so Phase 6 can re-run it unchanged and
compare.
