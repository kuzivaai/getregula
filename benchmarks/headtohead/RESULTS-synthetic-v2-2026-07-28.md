# Synthetic recall, expanded corpus — Regula only, 28 July 2026

Supersedes the n=5 measurement in `RESULTS-synthetic-2026-07-28.md`, which
stands as the record of how the miss was first found. **Owner amendment:
n=5 supports a finding; it does not support a plan.**

Manifest **v2.0**. High-risk set expanded **5 → 30**, spanning Annex III
Categories 1-8 plus the medical-device, safety-component, transportation
and housing families the patterns claim. Still Regula only: this is **not**
a head-to-head; all three competitor adapters still raise by design.

## Fixture construction, stated because it moves the number

Each fixture is written as a developer in that domain would plausibly write
the code, **not reverse-engineered from the regex**. Where domain
vocabulary naturally collides with a pattern (a CV screener really is
called `cv_screen`) that collision is real; where it does not, the miss is
real. **The fixtures are deliberately sparse on AI-library imports, and
that turns out to matter — see gate 2.** A reader should treat the absolute
recall figure as sensitive to that choice and the *diagnosis* as the
durable output.

## Headline

| Condition | High-risk recall |
|---|---|
| **Default scan** | **10/30 = 33%** |
| Domain declared (`--domain <matched>`) | **14/30 = 47%** |
| Domain declared **and** an AI-library import present | **19/30 = 63%** |

Prohibited recall **5/5**. High-risk firings on the 3 negative controls:
**0**.

**The n=5 figure was 80%. On 30 fixtures it is 33%.** The first number was
not wrong; it was underpowered, and it happened to sample the categories
that survive the gates.

## Diagnosis — every miss, not just the first

The amendment requires the lexical-vs-semantic diagnosis to cover all 20
default-scan misses. It does, and **the dominant cause is neither**.

| Cause | Misses | Nature |
|---|---|---|
| **Opt-in domain suppression** | **13** | **Deliberate design** |
| AI-indicator gate | 4 | Design consequence |
| No pattern matches at all | 3 | Genuine lexical/semantic gap |

**17 of 20 misses are pipeline behaviour, not pattern quality.** The
high-risk pattern matches the file text; the tier is never assigned.

### Gate 1 — opt-in domain suppression (13 misses)

MEASURED: **9 of 17 high-risk domains are in `OPT_IN_CATEGORIES`**
(`scripts/constants.py:105`) and are suppressed on a default scan unless
the user declares the domain or fingerprinting activates it:
`critical_infrastructure`, `employment`, `essential_services`, `justice`,
`law_enforcement`, `migration`, `safety_components`,
`high_risk__worker_management`, `high_risk__democratic_processes`.

**The rationale is documented and defensible.** The constants file records
that these produced 0 true positives and multiple false positives on random
code, so they are gated to protect precision. This is a deliberate
precision-over-recall trade, not a defect.

**But it is a trade nobody outside the code knows about.** On a default
scan, an employment-AI codebase, a border-control system and a judicial
decision-support tool all return **nothing**. Verified by control:
`--domain employment` on `highrisk_employment.py` flips
`['ai_security']` → `['ai_security', 'high_risk']`.

### Gate 2 — the AI-indicator requirement (4 misses)

Verified by controlled single-variable test: adding `import
sklearn.ensemble` to `highrisk_admissions.py`, changing nothing else,
flips it from `(none)` to `['high_risk']`.

So a high-risk system built without a recognised AI-library import is
missed even in an always-reported category. That covers homegrown models,
raw HTTP calls to a model endpoint, and any library not on the indicator
list. **My fixtures overstate this**, because real ML code usually imports
something — but it is not zero, and API-only integrations are common.

### Gate 3 — unexplained (8 misses)

**Even with both gates satisfied, 11 fixtures still miss**, of which 3 have
no matching pattern and **8 do**: `border_screening`, `energy_grid`,
`recidivism`, `task_allocation_shift`, `traffic_control`,
`voter_targeting`, `water_supply`, `worker_monitoring`.

Pattern matches, domain declared, AI indicator present, tier still not
assigned. **Cause not determined. Not guessed.** This is the most important
open thread from this measurement and it should be traced before any Phase
5 work touches the detection layer.

### The genuine pattern gap (3 misses)

`benefits_eligibility` (Annex III 5(a), public benefits),
`crime_forecast` (predictive policing), `exam_proctor` (remote proctoring)
match **no** high-risk pattern. Two of the three also classify as
`prohibited` on the older fixtures, so there is tier-boundary work here
too.

## What this changes

**The programme's central strategic finding is about false positives and
still holds:** the 24 high-risk FPs are semantic, and regex tightening
cannot fix them without destroying recall.

**It does not describe the recall side.** On recall, 17 of 20 misses are
gates, not patterns. **Writing more or better regexes would not have moved
this number.** Any Phase 5 item proposing to improve recall by touching
patterns is aimed at 3 of 20 misses.

This is direct evidence for the hostile reviewer's ruling that P8 (fixtures
for 134 patterns) is the wrong work at the wrong scale.

## What this does and does not license saying

**Supported:** on a 30-fixture hand-built corpus with constructed ground
truth, default-scan high-risk recall is 33%, rising to 63% with domain
declared and an AI import present; prohibited recall is 5/5; zero false
high-risk on 3 negatives.

**NOT supported:** any real-world recall estimate; any comparison to
another tool; any claim that 63% is "the" recall. Thirty hand-built files
are a diagnostic instrument, not a sample of the world.

**Nothing here goes on a public surface** without the approval gate. Raw
output: `results/regula-synthetic-v2-2026-07-28.json`.
