# (b) Stickiness, bot traffic, and the minimum sample size

**This is the section that decides whether the design work is an intervention or
a precondition, and the answer is precondition.**

## The traffic, measured rather than inherited

The brief describes "roughly 2.1 visitors a day". That figure survives, and it is
now measured rather than carried. Two Plausible exports for `getregula.com` were
downloaded on 2026-08-14 and sit on this machine. Reading the daily series:

```
=== 91d: 91 daily rows
  date range: 2026-05-15 .. 2026-08-13
  visitors : total=188 mean/day=2.07 median=2 max=10 zero-days=15
  pageviews: total=217 mean/day=2.38

=== 28d: 28 daily rows
  date range: 2026-07-17 .. 2026-08-13
  visitors : total=57 mean/day=2.04 median=2.0 max=6 zero-days=8
  pageviews: total=71 mean/day=2.54
```

**Measured here**, from `Plausible export getregula.com 91d.zip` and the 28d
equivalent, `visitors.csv` in each. The two windows agree at 2.07 and 2.04 per
day. **15 of 91 days had no visitors at all.**

Two limits travel with those numbers. The export is a snapshot taken on
2026-08-14, so it is four days stale as of writing and cannot be refreshed from
here. And Plausible reports only what its own filtering let through, which is the
next question.

## What Plausible does and does not filter

**Vendor claim**, retrieved 2026-08-17 from `plausible.io/most-accurate-web-analytics`.
Plausible states that it excludes traffic by four mechanisms, quoted:

> "Blocking traffic based on the User-Agent header"
> "Filtering out known referrer spam domains"
> "Blocking traffic originating from data centers"
> "Detecting and excluding unnatural traffic patterns"

and quantifies one of them:

> "Plausible also excludes ~32,000 data center IP ranges by default."

The only limitation the page states is in the opposite direction, under-counting
humans rather than over-counting bots:

> "One exception: ad blockers that make no distinction between privacy-friendly
> and invasive scripts, blocking all JavaScript tracking."

**What the page does not claim** matters as much as what it does. It makes no
claim to filter automated traffic that presents an ordinary browser User-Agent
from a residential or mobile IP range. Absence of a claim is not a stated
limitation, and it is reported here as the former.

## Is a large share of the remaining traffic automated?

The brief asserts it. The export cannot confirm it, and the reason is worth
stating: the 188 visitors are already post-filter, so any residue is by
definition traffic the four mechanisms above did not catch.

What the export does show is a composition consistent with a residue, and this is
**Interpreted, not Demonstrated**:

| Signal | 91-day value |
|---|---|
| Direct / None as a share of visitors | 147 of 188 (78.2%) |
| Bounce rate on that Direct traffic | 86% |
| Mean visit duration on that Direct traffic | 19 seconds |
| Largest single country | China, 59 of 188 (31.4%) |
| United Kingdom | 32 |
| United States | 25 |

China alone exceeds the UK and US combined (59 against 57). For a site whose
content is the EU AI Act, UK AI regulation, Colorado and South Korea, with no
Chinese-language page, that distribution has no obvious editorial explanation.

**The important point is that the conclusion below does not depend on resolving
this.** Any automated residue can only make the effective human sample smaller
than 188, so it moves every figure in the next section in the same direction:
against measurability. The bot question changes the size of the problem, never
its sign.

## The sample size a before-and-after claim would need

Derived here, not cited. Two-proportion test, two-sided alpha 0.05, power 0.80,

    n per arm = ( z(1-a/2)*sqrt(2*p̄*q̄) + z(1-b)*sqrt(p1*q1 + p2*q2) )² / (p2-p1)²

with z(0.975) = 1.9600 and z(0.80) = 0.8416, and days computed at the measured
2.066 visitors per day.

| baseline | target | relative lift | n per arm | n total | days | years |
|---|---|---|---|---|---|---|
| 0.9% | 1.8% | 100% | 2,580 | 5,160 | 2,497 | 6.8 |
| 0.9% | 2.7% | 200% | 855 | 1,710 | 828 | 2.3 |
| 0.9% | 4.5% | 400% | 317 | 634 | 307 | 0.8 |
| 5.0% | 7.5% | 50% | 1,470 | 2,941 | 1,424 | 3.9 |
| 5.0% | 10.0% | 100% | 434 | 869 | 421 | 1.2 |
| 10.0% | 15.0% | 50% | 686 | 1,371 | 664 | 1.8 |
| 10.0% | 20.0% | 100% | 199 | 398 | 193 | 0.5 |

The 0.9% baseline is not hypothetical. It is this site's own measured
assessment-start rate: 1 `Assessment Started` event against 109 homepage
visitors over the 91 days.

Turned the other way round, for the traffic that actually exists:

| window | visitors | per arm | from 0.9% detects | from 5% detects | from 10% detects |
|---|---|---|---|---|---|
| 3 months | ~189 | 94 | 10.2% (x11.3) | 17.9% (x3.6) | 25.5% (x2.5) |
| 6 months | ~377 | 189 | 6.2% (x6.9) | 13.3% (x2.7) | 20.3% (x2.0) |
| 12 months | ~755 | 377 | 4.1% (x4.5) | 10.4% (x2.1) | 17.0% (x1.7) |
| 24 months | ~1,509 | 755 | 2.9% (x3.2) | 8.6% (x1.7) | 14.7% (x1.5) |

**A full year of split-testing at this volume can detect nothing smaller than a
1.7-fold change**, and from the real assessment-start baseline, nothing smaller
than a 4.5-fold change.

## The funnel, and why it is not a rate

Over the same 91 days the conversion events were:

```
name,unique_conversions,total_conversions
Outbound Link: Click,11,12
CTA Click,2,3
Assess Question,1,17
Assessment Started,1,1
Assessment Complete,1,2
```

**One visitor started the assessment and one completed it, in 91 days.** The
`step` custom property records steps 1 through 15 with one visitor each: a single
person walked the whole flow. `/assess/` received 2 visitors in 91 days.

A completion rate cannot be computed from this. One of one is not 100%.

## Conclusion

**Demonstrated:** at the measured traffic, no before-and-after claim about a
design change to this site is establishable on any timescale a decision can wait
for. The design work is therefore a **precondition**, not an intervention: it
cannot be justified by a measured lift and must not later be credited with one.

**What this does not say.** It does not say the design work is not worth doing.
Correctness, comprehension, accessibility and honesty are all defensible grounds
and none of them requires a sample. It says only that "we changed X and
conversion rose Y%" is a sentence this site cannot support, and that instrumenting
for one would be building a measurement that cannot fire.

**The observation that would overturn it** is traffic at a different order of
magnitude. At 100 visitors a day the 12-month row becomes a 2-week row. Until
then the lever is acquisition, and the honest sequence is: fix what is wrong
because it is wrong, get traffic, then measure.
