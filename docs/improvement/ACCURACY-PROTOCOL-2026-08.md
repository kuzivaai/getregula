# A pre-registerable protocol for the first real-world accuracy evidence

**Written 2026-08-17. NOT EXECUTED.** Labelling requires people and the owner's
authorisation. This document is the design, precise enough that someone else
could run it and that a hostile reader could believe the result.

---

## 0. The question this exists to answer

The hardest question anyone can ask about this product today has one honest
answer and it is bad:

> **Real-world accuracy is untested over 0 human-labelled repositories.** The only
> measured commercial result is **0/40** on evidence discovery against a
> transparent baseline at **40/40**, diagnostic over constructed correlated
> families, not real-world accuracy. The precision figure that exists, **83.5% on
> N=115**, is single-reviewer, dated, and its corpus is not reconstructible
> (ledger N51). The recall figures are **10/30 default, 16/30 with domains
> declared, 23/30 with domains plus an AI import**, on 30 hand-written synthetic
> fixtures.

There is no counter-evidence because none has been gathered. This protocol
gathers the smallest amount that would count.

**What it does not address, stated first so it cannot be oversold.** It does not
re-run the 0/40 benchmark and does not bear on it: that benchmark measured
evidence discovery over constructed families and this measures detector output on
real code. Anyone quoting a result from this protocol must quote the 0/40 result
beside it.

---

## 1. What is being measured, and the construct that makes it measurable

**The wrong construct, and it must be rejected explicitly.** "Is this repository a
high-risk AI system under Annex III?" is a legal determination that depends on
intended purpose, the provider's role, Article 6(3) exclusions and facts that are
not in the code. No rater can answer it from a repository, this product does not
claim to answer it, and a study that asked it would be measuring the raters'
willingness to guess.

**The construct this protocol measures** is the one the product actually claims:

> **Indication validity.** Given a code location the tool flagged and the Annex III
> use area it named, would a competent reviewer, seeing only the code, judge that
> this location plausibly relates to that use area, such that it warrants review?

That is answerable from code, it is what "risk indication, not legal advice"
means, and a tool that fails it is failing on its own terms.

**Primary endpoint: indication precision.** The proportion of sampled findings
that two blinded raters independently judge to warrant review for the use area the
finding names.

**Secondary endpoint: repository-level sensitivity.** Among repositories that
raters independently judge to contain functionality in an Annex III use area, the
proportion in which the default scan produced at least one high-risk finding.

---

## 2. Why the primary endpoint is not high-risk precision, and this is derived

The obvious primary endpoint is precision of **high-risk** findings. It is
infeasible at this scale, and the reason is a rate measured this session rather
than assumed.

Default-scan high-risk findings per real repository, measured 2026-08-17 on the
three repositories in `DEFAULTS-RECOMMENDATION-2026-08.md`:

```
face_recognition  2      open-webui  0      vercel-ai  0      mean 0.67
```

Sample sizes for a proportion, alpha 0.05 two-sided, normal approximation:

```
 assumed p  target +/-  n findings
      0.80         10pp          62
      0.80         15pp          28
      0.70         10pp          81
      0.60         10pp          93
```

```
-> 60 high-risk findings at 0.67 per repository needs ~90 repositories
-> 60 findings of ANY detector class at 16.7 per repository needs ~4
```

**Ninety repositories is not a smallest credible exercise.** So the primary
endpoint is precision over **all detector classes**, which the same sample supports
at a usable interval, and high-risk precision is reported as a pre-specified
subgroup with its own interval, which will be wide and must be published as wide.

Achieved precision of the estimate at candidate sample sizes:

```
  n= 40  +/-15.5pp worst case (p=0.5)   +/-12.4pp at p=0.8
  n= 60  +/-12.7pp worst case           +/-10.1pp at p=0.8
  n= 80  +/-11.0pp worst case           +/- 8.8pp at p=0.8
```

**Chosen: n = 60 findings.** It is the smallest n whose worst-case interval is
under 13 percentage points, and 80 is not worth a third more rater time for two
points.

---

## 3. The sampling frame, fixed before any repository is seen

Cherry-picking is the failure mode that would make this worthless, so the frame is
mechanical and is recorded before execution.

**3.1 Population.** Public GitHub repositories meeting all of:

- primary language Python, TypeScript or JavaScript (the three the product's
  measurements have ever covered);
- at least one dependency, in the manifest at the pinned commit, drawn from a
  **pre-registered list of AI/ML libraries** committed as
  `benchmarks/realworld/AI_DEPENDENCY_FRAME.json` before sampling begins;
- between 50 and 5,000 files, excluding vendored directories;
- last commit within 12 months of the sampling date;
- an OSI-approved licence permitting local analysis;
- **not** an AI library itself, determined by the pre-registered list above, so
  the corpus is applications rather than the frameworks they import.

**3.2 Draw.** Enumerate the population by the GitHub search API, record the full
result set, then select with a seeded pseudo-random draw. **The seed, the query
strings and the retrieval date are recorded in the pre-registration**, and the
complete enumerated set is committed so the draw can be replayed.

**3.3 Size.** Draw repositories until the accumulated default-scan finding count
reaches 60, then stop, then include the whole of the repository that crossed the
threshold. The number of repositories is therefore an outcome, not a choice, and is
reported. On this session's observed rate that is roughly 4 to 8 repositories.

**3.4 Pinning.** Every repository is pinned to the commit cloned and that SHA is
recorded before scanning. The corpus behind the 83.5% figure is no longer
reconstructible because `rescan_corpus.py` clones current heads with no pin
(N51). This protocol must not repeat it.

**3.5 What is committed and what is not.** The pinned SHAs, the enumerated frame,
the seed, the scan output and the labels are committed. **Third-party source is
not**, for the licence reasons N51 records; reconstruction is by clone-at-pin,
which the pin makes exact.

---

## 4. Raters, blinding and the labelling instrument

**4.1 Who.** Two independent raters, each of whom can evidence one of: a
professional qualification in law with AI or data-protection practice; two years
of applied AI governance work; or five years of software engineering plus
completed EU AI Act training. **A rater must not be the project owner and must not
have contributed to this repository.** A third rater with the same eligibility
adjudicates disagreements and does not see the first two raters' labels until
their own is recorded.

The eligibility bar is stated because "two independent blinded qualified human
raters" is already the standing requirement in the validation-readiness pack
(N66), and this protocol inherits it rather than inventing a weaker one.

**4.2 What a rater sees.** For each item: the file path, the full file, and 40
lines of context around the flagged line. **They do not see Regula's tier, its
priority score, its category label, its remediation text, or the other rater's
answers.** They see the use-area question only in the form of the fixed rubric
below, applied to a code location.

**4.3 Decoys are mandatory.** 20% of items presented to raters are **code
locations Regula did not flag**, drawn from the same repositories by the same
seeded procedure. Without them a rater sees only positives, learns that the
answer is usually yes, and the precision estimate measures acquiescence.
**Decoys are excluded from the primary endpoint** and are used only to estimate
rater acquiescence, which is reported.

**4.4 The rubric.** One question per item, answered on a fixed three-point scale.

> Looking only at this code, does it implement, configure or directly support
> functionality in the named use area, to the degree that a competent reviewer
> preparing an EU AI Act assessment would want to examine it?
>
> **2 = yes**, it clearly does.
> **1 = unclear**, it might, and I would need information not in the code.
> **0 = no**, it does not.

Plus one free-text field, mandatory when the answer is 0, naming what the code
does instead.

**The use area named to the rater is the one Regula's finding names**, supplied
without the tool's name attached, so the rater judges the pairing rather than the
tool.

**4.5 Scoring.** A finding counts as **correct** when both raters answer 2, and as
**incorrect** when both answer 0. Any other combination goes to adjudication, and
the adjudicator's 2 or 0 decides. **A finding that the adjudicator also marks 1
is scored `NOT_ASSESSABLE` and is reported as its own category, never
redistributed**, because absorbing it into either side would be choosing the
answer.

---

## 5. Inter-rater procedure, and what it must report

Raw agreement, Cohen's kappa, and **the full disagreement list**, not a summary.

At n = 60 the precision of kappa itself is limited and that is disclosed in
advance rather than discovered afterwards:

```
  n= 60  SE(kappa) ~ 0.092   95% CI half-width ~ 0.181
  n= 80  SE(kappa) ~ 0.080   95% CI half-width ~ 0.156
```

So at n = 60 a kappa of 0.70 has a confidence interval of roughly 0.52 to 0.88.
**A pre-registered minimum kappa is therefore a floor on the point estimate and
cannot be a claim about the population.** The floor is **kappa >= 0.60**. Below
it the rubric is judged to have failed and **the precision result is not
reported at all**, because a precision figure computed from labels the raters do
not agree on is a number without a referent.

**Rater training is a fixed 10 items** from repositories outside the sample,
labelled together with discussion, before blinding starts. Those 10 are discarded.

---

## 6. Pre-registered analysis and the pass criterion

**6.1 Primary.** Indication precision = correct / (correct + incorrect), with a
Wilson 95% interval. `NOT_ASSESSABLE` items are excluded from the denominator and
reported separately with their count.

**6.2 The pass criterion, chosen before the data exists.**

> **PASS if the lower bound of the Wilson 95% interval is at or above 0.60.**

**Why 0.60 and not something higher.** The claim this evidence would support is
"the locations this tool flags are worth a reviewer's time". A tool whose flagged
locations are worth reviewing three times in five is useful when the alternative
is reading the whole repository; a tool at one in five is not. **0.60 is the point
at which the majority of a reviewer's time on Regula's output is not wasted**, and
it is stated in advance so it cannot be moved afterwards. It is deliberately
lower than the existing published 83.5%: if the real-world figure lands between
0.60 and 0.835 the study passes **and simultaneously establishes that the
published figure does not generalise**, which is a result the project must be
willing to publish.

**6.3 Pre-specified subgroups**, each with its own interval and each expected to be
wide: by detector class (high_risk, limited_risk, ai_security, agent_autonomy,
credential_exposure), by language, and by repository. **No subgroup may be
reported without its interval**, and none may be promoted to the headline.

**6.4 Secondary endpoint, and it is conditional.** Repository-level sensitivity is
run only if the primary passes. Raters label each sampled repository, blinded to
the scan, for whether it contains functionality in any Annex III use area. Among
those labelled yes, the proportion where the default scan produced at least one
high-risk finding is the estimate.

Sizing, one-sided, alpha 0.05, power 0.80, against a pre-registered floor equal to
the synthetic default recall of 0.33:

```
 floor p0   true p1   n positive repositories
     0.33      0.60           25
     0.33      0.65           18
     0.33      0.70           13
```

**This is the expensive half.** Reaching 13 to 25 positively-labelled
repositories means labelling substantially more, and the sampling frame's AI
dependency requirement does not make a repository Annex III relevant. **The
protocol does not pretend Stage 2 is cheap**, and it is explicitly gated on Stage
1 rather than bundled with it.

---

## 7. What would make the result not believable, listed so it can be checked

A hostile reader should look for exactly these, and the design blocks each:

| Failure | What blocks it |
|---|---|
| Corpus chosen to flatter | Frame, query, seed and enumerated set committed before the draw |
| Corpus not reconstructible | Every repository pinned to a SHA before scanning (N51's defect) |
| Raters primed by the tool | Raters never see tier, score, category label or remediation |
| Acquiescence | 20% unflagged decoys, acquiescence reported |
| Disagreement hidden | Raw disagreements and kappa published; result withheld if kappa < 0.60 |
| Ambiguity absorbed | `NOT_ASSESSABLE` reported as its own category, never redistributed |
| Threshold moved after seeing data | Pass criterion, subgroups and analysis fixed in the pre-registration |
| Result overstated | The 0/40 benchmark result must be quoted alongside any figure from this study |
| Sample size chosen to fit a result | n derived in section 2 from a measured finding rate, shown |

**And the one it does not block, stated plainly.** Two raters and 60 findings is a
small study. It can establish that indication precision on real code is or is not
above a floor. **It cannot establish that this tool is better than any
alternative**, because no comparator is run, and it cannot establish anything
about legal correctness, which is not what the construct measures.

---

## 8. Cost, so the owner is deciding against a number

Estimated from the rubric and the item count, labelled as estimate:

- 60 findings plus 15 decoys plus 10 training items = **85 items per rater**.
- At 6 to 10 minutes an item including reading the surrounding code, **8.5 to 14
  hours per rater**, twice, plus adjudication of an expected 15 to 25 disagreements
  at 10 minutes each.
- **Total rater time: roughly 20 to 32 hours.** Plus the engineering to build the
  frame, draw, pin, scan and blind the presentation, which is repository work and
  is the cheaper half.

Stage 2, if reached, is a multiple of this and should be costed separately when
Stage 1 reports.

---

## 9. What is required before any of this may run

Not engineering questions, and none of them is answered here:

1. **Owner authorisation.** `REAL_DATA_COLLECTION` is DISABLED and
   `EXTERNAL_CONTACT` is NOT_AUTHORISED. Recruiting raters is external contact.
2. **Rater recruitment**, against the eligibility bar in 4.1. The standing owner
   item "recruit raters 2 and 3" has been open since before this protocol existed.
3. **A pre-registration written and timestamped** before the draw, containing
   sections 3 to 6 verbatim with the seed and queries filled in.
4. **A licence review** of the frame, confirming local analysis of each sampled
   repository is permitted.
5. **A decision on publication in advance**, including publication of a failing
   result. A protocol that is only published when it passes is not evidence.

---

## 10. Status

`ACCURACY_EVIDENCE: NOT_GATHERED`. `PROTOCOL: DESIGNED_NOT_PREREGISTERED`.
`EXECUTION: NOT_AUTHORISED`.

Nothing in this document changes any standing verdict. `PRODUCT_BUILD` remains
STOP, `VENTURE_DECISION` remains STOP, `TECHNICAL_EVIDENCE` remains FAILED, and
real-world accuracy remains untested over zero human-labelled repositories until
this or something better is run.
