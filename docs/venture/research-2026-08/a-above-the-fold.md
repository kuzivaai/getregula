# (a) Above the fold: value proposition clarity and credibility at zero users

## What the literature actually supports

**Secondary, with its primary named**, retrieved 2026-08-17: Jakob Nielsen,
"How Long Do Users Stay on Web Pages?", Nielsen Norman Group, published
**11 September 2011**. It reports an analysis by Chao Liu and colleagues at
Microsoft Research over **205,873 web pages**, more than 10,000 visits per page,
and **over 2 billion dwell times**.

Quoted findings:

> "The average page visit lasts a little less than a minute."
> "Users often leave Web pages in 10-20 seconds, but pages with a clear value
> proposition can hold people's attention for much longer."
> "the time users spend on a web page follows a Weibull distribution"
> "99% of web pages have a negative aging effect"
> "the first 10 seconds of the page visit are critical"
> "Only after people have stayed on a page for about 30 seconds does the curve
> become relatively flat."

"Negative aging" is the load-bearing concept: the longer someone has already
stayed, the less likely they are to leave in the next instant. The abandonment
hazard is front-loaded, so the first seconds are not merely important, they are
where nearly all the risk sits.

**The age of this is a real problem and is stated rather than buried.** It is
from 2011, which predates mobile-majority browsing. The project's own rules
require preferring sources from the last two months for fast-moving topics and
saying so explicitly when widening; nothing of comparable scale and methodology
was found from the last two months, or the last two years, and this is a
fifteen-year-old finding being used because the alternative is a vendor blog. The
same caveat the ledger attached to the Stanford web-credibility guidelines at
N132 applies here with more force.

## Why it is worth quoting anyway: this site's own numbers land inside it

**Measured here**, from the 91-day Plausible export (2026-05-15 to 2026-08-13):

| Homepage, `/` | value |
|---|---|
| visitors | 109 |
| bounce rate | 85% |
| time on page | **23 seconds** |
| scroll depth | **29%** |

23 seconds sits just past the 10-20 second abandonment band and short of the
30-second point at which the hazard curve flattens. 29% scroll depth means the
median visitor never reaches the lower two thirds of the page, **including the
four-tab terminal showing real `insufficient_information` output**, which is the
strongest honest asset the site has.

That is the finding this section exists to produce, and it does not depend on the
2011 paper being current: whatever the general population does, **this page is
losing its readers before the evidence on it is reached.** The external source
supplies a mechanism; the internal measurement supplies the instance.

## Outcome-led versus category-led headlines

**No usable evidence was found, and this is reported as an empty search rather
than filled in.** Searched for controlled comparisons of outcome-framed against
category-framed headlines for developer tools and for professional services. What
came back was agency and SaaS content marketing, none of it stating a sample, a
population or a method. The project's ledger records at N132 that all three
statistics previously supplied for a comparable decision failed at source, one of
them attributed to a firm that had wound down before the report could exist. No
figure is offered here rather than repeat that.

**Reasoned, not evidenced.** For this product the choice is partly made by facts
outside the design question. The current headline is category-led and hedged, and
the hedging is not optional: the hard rule forbids promising an outcome the tool
does not deliver, so "know your risk tier in 60 seconds" is unavailable whatever
it might do for conversion. What remains available is an outcome-led framing of
the outcome the tool *does* produce, which is a named list of what a person still
has to settle. **Assumption:** that a reader values "here is what you have to
find out" as an outcome. **Overturned by:** comprehension testing with
representative readers showing they read it as an evasion rather than as an
answer. That test has not been run and this project has never run one.

## Honest credibility signals available at zero users

The constraint is real: no logos, no testimonials, no user count, no funding, no
legal entity, and no professional indemnity cover, which the pricing page already
discloses. What remains are signals whose evidence is *inside the artefact*
rather than in a customer base.

**Reasoned, not evidenced**, and enumerated from what this repository can already
prove rather than from a list of best practices:

1. **Reproducible output.** A published transcript bound to a command a reader can
   run, verified on every build. As of this session the README carries exactly
   that, gated by `scripts/verify_transcripts.py`. This is the strongest available
   signal because the reader can falsify it in one command.
2. **Stated limits.** "What Regula is (and isn't)" and "Important limitations"
   already exist. The literature this project already verified at N132 (the
   Stanford Web Credibility Guidelines, early-2000s, "based on three years of
   research that included over 4,500 people") lists showing expertise and
   avoiding over-promotion among its ten; six of the ten are things this
   project's honesty rules already require. That is a coincidence worth noticing:
   the compliance-driven constraints and the credibility-driven ones point the
   same way.
3. **Open source under a named licence**, which lets a reader check the claim
   rather than trust it.
4. **A tamper-evident audit chain a reader can verify** (`regula audit verify`).
5. **Published methodology including its failures.** The benchmark README already
   states what is and is not reproducible.

**What must not be used**, and this is a live risk rather than a hypothetical:
the download figure. Ledger N109 retracted a "1,282-2,177/week" figure that was a
cumulative total under a weekly label, overstating by 88.4 times; the real figure
is 25 a week excluding mirrors. A user count is the most conventional
zero-to-one credibility signal and it is the one this project has already got
wrong once.
