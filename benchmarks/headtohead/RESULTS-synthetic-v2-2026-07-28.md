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

> **PATH CORRECTION, 28 Jul 2026.** Every figure below is the **scanner**
> path (`regula check`, via the committed `adapters.run_regula`) — what a
> user actually runs. The **classifier** path (`classify()`, what
> `benchmarks/synthetic/run.py` measures) gives **16/30 = 53%** on the same
> corpus. **The two disagree by 6 fixtures.** My first writeup gave 33%
> without stating which path produced it, which is the same
> provenance-free-number defect this batch exists to fix. The divergence
> is finding **F8** (two unreconciled detectors over the same code), now
> quantified for the first time.

| Condition (scanner path) | High-risk recall |
|---|---|
| **Default scan** | **10/30 = 33%** |
| Domain declared (`--domain <matched>`) | **14/30 = 47%** [NOT REPRODUCIBLE] |
| Domain declared **and** an AI-library import present | **19/30 = 63%** [NOT REPRODUCIBLE] |

Prohibited recall on the scanner path, default scan: **5/5**. High-risk
firings on the 3 negative controls: **0**.

> **1.5c CORRECTION, 28 Jul 2026 — two of these four figures are WITHDRAWN
> as NOT REPRODUCIBLE.** F24 committed
> `benchmarks/synthetic/RECALL.json`, produced by
> `scripts/build_recall_artefact.py` from an actual run. Re-measuring
> reproduced **10/30 default** and **16/30 classifier** exactly. It could
> not reproduce **14/30** or **19/30**, because the conditions that
> produced them were never committed: "`--domain <matched>`" implies a
> per-fixture domain mapping that does not exist in `manifest.json`, and
> "an AI-library import present" does not say which import or which
> fixtures received it.
>
> The reproducible neighbours, both from the committed artefact, are
> **different conditions and are labelled as such** rather than
> substituted for the withdrawn ones:
>
> | Condition (path, gates) | High-risk recall |
> |---|---|
> | scanner path, default scan, no flags | **10/30 = 33.3%** |
> | scanner path, all eight opt-in domains declared | **16/30 = 53.3%** |
> | scanner path, domains declared and `import torch` injected into every fixture | **23/30 = 76.7%** |
> | classifier path (`report.scan_files`), all domains declared | **16/30 = 53.3%** |
>
> All four give prohibited **5/5**.

### F8 does not survive a like-for-like comparison

**MEASURED 2026-07-28 from `RECALL.json`.** Under the SAME gate condition
(all eight domains declared) the scanner path and the classifier path miss
**the identical 14 fixtures**. Not the same count with different members:
the same set, symmetric difference zero.

The "six-fixture divergence" recorded above and in the handover compared
`scanner/default` against `classifier/all-domains` — **two paths and two
gate conditions changed at once**. The six fixtures it identified
(`highrisk_employment`, `highrisk_judicial_support`,
`highrisk_promotion_ranking`, `highrisk_traffic_control`,
`highrisk_visa_triage`, `highrisk_water_supply`) are exactly the ones the
domain gate unlocks. They are the domain gate, not two unreconciled
detectors.

This is `.claude/rules/measurement.md` rule 2 — one variable at a time —
failing in the document that was written to establish the recall baseline.
**F8 as stated is not supported by this measurement.** Whether some
narrower divergence exists is open; the trace work in Task C should start
from the artefact rather than from the withdrawn claim.

### The fixtures that miss with both gates satisfied

Seven, not eight, under the reproducible condition (domains declared plus
an injected AI import), named here because a trace has to start somewhere:
`highrisk_benefits_eligibility`, `highrisk_border_screening`,
`highrisk_crime_forecast`, `highrisk_energy_grid`, `highrisk_exam_proctor`,
`highrisk_recidivism`, `highrisk_voter_targeting`. The handover's figure of
eight came from the unreproducible condition and is not comparable.

**The n=5 figure was 80%. On 30 fixtures it is 33%.** The first number was
not wrong; it was underpowered, and it happened to sample the categories
that survive the gates.
The 80% is the high-risk row of
benchmarks/headtohead/results/regula-synthetic-2026-07-28.json, 4 of 5. The 33%
is the scanner default-scan condition in benchmarks/synthetic/RECALL.json,
10 of 30.

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
for 134 patterns) is the wrong work at the wrong scale. The scope figure is
recorded at docs/improvement/HOSTILE-REVIEW-DISPOSITIONS.md, objection 6, which
cut the tier scope to 134 from the 183 in docs/improvement/PLAN-PHASE4.md and
gives 134 as 17 prohibited plus 117 high-risk patterns.

## What this does and does not license saying

**Supported:** on a 30-fixture hand-built corpus with constructed ground
truth, scanner-path default-scan high-risk recall is 33%, rising to 76.7%
with all domains declared and an AI import injected; scanner-path
default-scan prohibited recall is 5/5; zero false high-risk on 3 negatives.
The 63% figure is WITHDRAWN as NOT REPRODUCIBLE — see the 1.5c correction
above. Every figure here traces to `benchmarks/synthetic/RECALL.json`.

**NOT supported:** any real-world recall estimate; any comparison to
another tool; any claim that 63% is "the" recall. Thirty hand-built files
are a diagnostic instrument, not a sample of the world.

**Nothing here goes on a public surface** without the approval gate. Raw
output: `results/regula-synthetic-v2-2026-07-28.json`.
