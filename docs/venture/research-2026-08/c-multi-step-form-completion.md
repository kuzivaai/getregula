# (c) Multi-step forms and quizzes: order, progress, and completion

## Provenance warning, stated before the figures

The strongest source here is a peer-reviewed experiment, and **the publisher's
record could not be opened from this machine.** ScienceDirect, the ACM Digital
Library and Hogrefe each returned HTTP 403 and PubMed Central returned a CAPTCHA
on 2026-08-17. The numeric results below are quoted from the accepted
manuscript's own Results section as surfaced by a search index. The citation,
abstract and page range are corroborated across four independent listings
(ScienceDirect, ACM DL, PubMed and the DOI resolver), so the *identity* of the
paper is solid; the *figures* are one retrieval short of the standard the rest of
this document holds. **Anyone acting on them should open the PDF first.**

See also the near-miss recorded in this directory's README: a PMC identifier I
constructed rather than followed resolved to an unrelated paper about crime
victimisation.

## The paper

Conrad, F. G., Couper, M. P., Tourangeau, R., and Peytchev, A. (2010). "The
impact of progress indicators on task completion." *Interacting with Computers*
22(5), 417-427. DOI 10.1016/j.intcom.2010.03.001. Two experiments on online
questionnaire completion.

Abstract, quoted:

> "A near ubiquitous feature of user interfaces is feedback on task completion or
> progress indicators such as the graphical bar that grows as more of the task is
> completed. The presumed benefit is that users will be more likely to complete
> the task if they see they are making progress but it is also possible that
> feedback indicating slow progress may sometimes discourage users from
> completing the task. ... Overall, the results suggest that when progress seems
> to outpace users' expectations, feedback can improve their experience though
> not necessarily their completion rates; when progress seems to lag behind what
> users expect, feedback degrades their experience and lowers completion rates."

### Experiment 1

> "Of the 3,179 users who started the questionnaire 457 broke off, for an overall
> breakoff rate of 14.4%."

By condition:

| Progress indicator | Breakoff rate |
|---|---|
| Slow-to-Fast (early feedback discouraging) | **21.8%** |
| Constant speed | 14.4% |
| **No indicator at all** | **12.7%** |
| Fast-to-Slow (early feedback encouraging) | **11.3%** |

χ²(3) = 31.57, p < .001.

### Experiment 2, which replicated it

Breakoff rates "14.3, 14.4, 19.9 and 11.3 percent for None, Constant Speed,
Slow-to-Fast and Fast-to-Slow Progress Indicators, respectively". χ²(3) = 27.92,
p < .001.

### The finding that matters, and it is counterintuitive

**A progress indicator is not a free win.** In both experiments the
early-discouraging indicator produced *reliably more* abandonment than showing no
indicator at all (21.8% against 12.7%; 19.9% against 14.3%), while the
early-encouraging indicator did **not** reliably lower abandonment against none.
The authors' own summary: "early discouraging (Slow-to-Fast) information led to
reliably more breakoffs than did no progress indicator (p < .01) but early
encouraging (Fast-to-Slow) feedback did not reliably lower breakoffs."

The asymmetry is the design instruction. The downside of a badly-calibrated
progress indicator is large and reliable; the upside of a well-calibrated one is
small and conditional. The authors note it helps mainly when "overall breakoff
rates are high enough so that a reduction in breakoffs is noticeable".

The paper also reports that in Experiment 2, "frequency of feedback did affect
breakoffs differently for different speeds": the worst result in the whole study
was discouraging early feedback shown on **every** page, and making the same
discouraging information available **on demand** rather than always-on was
"substantially less detrimental".

### The prior literature it cites, which is mixed

Also useful, because it stops this being read as one settled finding. Quoted from
the paper's own review: Couper et al. (2001) "found no difference in completion
rates when progress indicators were used and when they were not"; Crawford et al.
(2001) "actually found a lower completion rate when progress indicators were used
than when they were not", with most abandonment on free-text questions, and a
follow-up with the open questions removed showed "a modest but reliable increase
in completion rates with a progress indicator".

So the honest state of the evidence is: **progress indicators change behaviour
substantially, and the sign of the change depends on calibration and on question
difficulty.**

### A second, directly relevant paper, cited but not opened

Yan, T., Conrad, F. G., Tourangeau, R., and Couper, M. P. (2010). "Should I Stay
or Should I Go: The Effects of Progress Feedback, Promised Task Duration, and
Length of Questionnaire on Completing Web Surveys." *International Journal of
Public Opinion Research* 23(2), 131-147. DOI 10.1093/ijpor/edq046. **Asserted:**
identified from the reference list of the paper above; not retrieved, and no
figure from it is quoted here. It is named because "promised task duration" is
exactly the variable a prequalifier promising "under a minute" is setting.

## What this supports for a five-or-six question prequalifier

Labelled by strength.

**Evidenced.**
1. If a progress indicator is shown, its early portion must not read as slow. On
   a five-question flow, question 1 of 5 is 20%, which is an encouraging first
   frame; a percentage that creeps (3%, 7%, 11%) is the Slow-to-Fast condition
   and is the one that measurably increased abandonment.
2. Showing no indicator is a legitimate option and outperformed the
   badly-calibrated one in both experiments. It is not a failure to omit one.
3. Put the hard question late. Crawford's free-text abandonment and Conrad's
   difficult-item result both point the same way, and it is the same instruction
   as "easy-first commitment" arrived at from evidence rather than from folklore.

**Reasoned, not evidenced.**
4. One question per screen versus a single card: **no source was found that
   settles this for a five-question flow.** Searched for controlled comparisons;
   what exists is vendor benchmark content with no methodology. Reasoning: the
   progress literature is about *perceived remaining effort*, and a single card
   showing all five questions makes remaining effort visible and finite at a
   glance, which is the encouraging-first-frame condition achieved without any
   indicator at all. For five short questions the card is therefore the cheaper
   way to get the same effect. **Assumption:** that five questions fit above the
   fold on a 320px viewport, which is testable rather than arguable.
   **Overturned by:** any controlled comparison at this length, or a rendering
   test showing the card does not fit, in which case per-screen with a 1-of-5
   counter is the fallback.
5. Completion *benchmarks* from vendor sources are deliberately not quoted. The
   figures available are self-reported by form vendors over self-selected
   customer bases, with no stated methodology, and this project's own history
   with such figures is recorded at ledger N132, where all three supplied
   statistics failed at source. **And this site could not use a benchmark
   anyway**: section (b) establishes that one visitor completed the existing
   assessment in 91 days, so there is nothing to compare a benchmark against.
