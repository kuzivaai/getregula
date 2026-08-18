# Users, journeys and information architecture

**Written:** 2026-08-18. **Branch:** `feat/engagement-fixes`.
**Scope:** the public website under `site/`, all three shipped locales.

This document exists because the information architecture did not serve the
audience the owner is aiming at. It states who the users are, what each one
arrives to do, where the current site fails them, and what follows for the
structure. It is written before the refactor and the refactor is built from it.

Every claim below carries one of five labels, using this repository's existing
vocabulary from `docs/venture/research-2026-08/README.md`:

- **Primary** retrieved from the body that produced it.
- **Verified** checked in this repository against a named primary source, with
  the anchor identifier from `docs/venture/gtm-2026-08-14/MARKET-SIZING-2026-08-14.md`.
- **Measured here** computed from an artefact on this machine, with the command.
- **Owner-stated** asserted by the owner. Not evidence, and not treated as any.
- **Reasoned, not evidenced** no source found. The reasoning, its assumptions and
  the observation that would overturn it are stated.

---

## 0. The honest state of the evidence, stated before any persona

**No persona in this document is evidenced by observation of this site's users,
because no such observation exists.**

| Fact | Value | Status |
|---|---|---|
| User interviews ever run | 0 | Measured here: no interview artefact exists in the tree. `git ls-files docs/user-validation` is empty; the directory does not exist. |
| Comprehension, usability or trust tests ever run on any surface | 0 | Verified against `docs/improvement/MERGE-READINESS-2026-08.md` section 0, item 5, which states it as a standing gap. |
| Visitors, 91 days to 2026-08-13 | 188, mean 2.07/day, 15 zero-days | Measured, `docs/venture/research-2026-08/b-stickiness-and-sample-size.md`, from the Plausible export of 2026-08-14. Not re-derived here: the export is a snapshot and cannot be refreshed from this machine. |
| Homepage `/` | 109 visitors, 85% bounce, 23 s on page, 29% scroll depth | Same source, same limitation. |
| Completions of the existing browser assessment in that window | 1 | Same source. |
| Direct/None share of visitors | 147 of 188 (78.2%), 86% bounce, 19 s mean duration | Same source. Composition consistent with an automated residue; **Interpreted, not Demonstrated**, and the residue cannot be sized from the export because the export is already post-filter. |

Two consequences follow and neither is optional.

**First, this work is a precondition, not an intervention.** At 188 visitors over
91 days a full year of split testing could not detect a change smaller than about
1.7-fold (`b-stickiness-and-sample-size.md`). No before-and-after claim about this
site is establishable. Nothing in this document, and nothing built from it, may
ever be credited with a measured lift.

**Second, the honest form of a persona here is a role and a task, not a person.**
There are no interviews to draw a biography from, so inventing one would be
fabrication dressed as research. Each user below is therefore defined by the
regulatory role they occupy and the question they arrive with. Those are anchored
on things that can be checked: the Act's own definitions, the verified market
anchors, and this site's measured behaviour.

### The archetype the owner named, and the hole in it

The owner states the target as **solo founders, non-technical founders, and small
teams that have a small technical function**. That is **Owner-stated**. It is the
premise of this work and it is not evidence.

It also has a hole worth naming rather than papering over. The verified
AI-adoption anchor is Eurostat `isoc_eb_ai` (anchor A3): **20.0% of EU enterprises
with 10 or more persons employed used AI in 2025; small firms of 10 to 49 employees
17.00%, medium firms of 50 to 249 employees 30.36%** [Verified, A3, VERIFIED-direct
2026-08-14]. That series has a floor of 10 employees. **Solo founders and
micro-enterprises sit below it, so the largest part of the named archetype is
precisely the part for which no adoption figure exists in the verified anchor set.**

There is a second tension. The GTM plan's primary earlyvangelist profile E1 is a
founder or CTO of a non-EU B2B SaaS with **5 to 100 staff** that already pays
between roughly EUR 420 and EUR 6,000 a year for a GDPR Article 27 representative
[anchors A12, A13, A14, all in
`docs/venture/gtm-2026-08-14/MARKET-SIZING-2026-08-14.md`]. Of the three
earlyvangelist profiles recorded there, E1 is the one with a *demonstrated*
budget for this class of obligation. The solo founder in the
owner's archetype has no budget anchor at all. **The design must therefore not
push the paid route at everybody**, because for a large part of the named
audience the paid route is speculative and pushing it would be selling ahead of
the evidence.

---

## 1. The users

Four users. Named by role and task. All four are **Reasoned, not evidenced** as
personas; what differs is what each one's reasoning is anchored on, which is
stated per user.

### U1. The non-technical founder who has been asked a question

**Arrives with:** a question somebody else asked. A customer's procurement form, an
investor's diligence list, a co-founder, or a headline.

**Their task:** find out whether this is a real obligation for them, this week.

**Context:** no legal training, no compliance function, may not write code at all.
Uses AI through somebody else's API or through a no-code tool that added it.

**Vocabulary they do not have, and this is the load-bearing fact about them:**
provider, deployer, placing on the market, putting into service, intended purpose,
Annex III, GPAI, conformity assessment. These are the terms the law is written in
[Primary: Regulation (EU) 2024/1689 Articles 2, 3(1), 3(3), 3(4), 6, Annex III].
A page written in them is not readable by this user, and a questionnaire whose
first question uses them is not answerable by this user.

**Likely failure points:**

1. The first view is a terminal command. It is not a thing they can execute, and
   not a thing they can evaluate. **Measured here:** at the commit this work
   started from, the first interactive element in the homepage hero after the
   headline is a button that copies `pipx install regula-ai && regula`, and the
   right half of the hero is a four-tab terminal.
2. The existing browser assessment's second question asks whether the subject
   "meets the EU AI Act definition of an AI system" and quotes Article 3(1) in
   full. **That is the question this user came to have answered.** Asking it back
   is the single clearest instance of the architecture not serving the archetype.
   [Measured here: `site/assess/index.html`, `QUESTIONS[1]`, id `is_ai_system`.]
3. They cannot tell whether `insufficient_information` means the tool failed or
   means the answer is genuinely open. The project's own ledger reaches the same
   conclusion from the other direction at N149: the tool "asks two questions,
   ships a command that answers them, and discards the answers, which is what
   makes an insufficient-information result read as a failure rather than as
   rigour."

**Consequence of failure:** they conclude that nothing applies and stop, or they
buy something they do not need. The first is worse and it is the one the measured
numbers are consistent with: 85% bounce, 23 seconds, 29% scroll, all measured
in `docs/venture/research-2026-08/b-stickiness-and-sample-size.md` from the
Plausible export of 2026-08-14.

**Anchored on:** the Act's own definitions (Primary), and this site's measured
behaviour.

### U2. The founder or technical lead who does write code

**Arrives with:** the same question, and the ability to answer part of it themselves.

**Their task:** establish in a few minutes whether this is real, and if so what to
do first. Comfortable with a terminal; will run a one-line install to find out.

**Likely failure points, and each is a defect this repository has already
recorded against itself:**

1. A scan that reads part of the tree and does not say so. Ledger N146 in
   `docs/improvement/LEDGER.md`: on a face-recognition library the default
   command read 6 of 30 Python files and reported 3 findings where the same
   tool reports 14 across the same tree. Fixed; the scan now discloses what it
   skipped.
2. A result that says `insufficient_information` with no path onward. Ledger N149
   and N155; the fact loop now closes.
3. Being talked down to. This user can falsify a claim in one command, which
   makes overstatement expensive here in a way it is not elsewhere.

**Consequence of failure:** dismisses the tool as marketing and does not return.

**Anchored on:** the Act's definitions, and the repository's own recorded defects.

### U3. The small team with a small technical function

**Arrives as two people, not one.** A business owner of the question and a
technical owner of the code. Roughly the 10 to 49 employee band.

**Their task:** produce one artefact that is legible to both of them and to
whoever asked.

**Anchored on two verified figures:**

- **17.00% of EU enterprises with 10 to 49 employees used AI in 2025**
  [Verified, anchor A3, Eurostat `isoc_eb_ai`, VERIFIED-direct 2026-08-14].
- Of 106 enterprise AI systems classified in the appliedAI study of March 2023,
  **18% were high-risk, 42% low-risk and 40% unclear** [Verified, anchor A5,
  VERIFIED-agent. **Caveat that travels with it:** a convenience sample of a
  public database, explicitly not representative].

That 40% figure, recorded at anchor A5 in
`docs/venture/gtm-2026-08-14/MARKET-SIZING-2026-08-14.md`, does the design work
here and it is used narrowly. It does not say that 40% of anyone's systems are
unclear. It says that when specialists classified a non-representative sample of
106 systems, two in five could not be placed. **If trained assessors cannot place
two in five, then forcing a founder to answer yes or no is asking them to
fabricate.** That is the argument for making "not sure" a first-class answer,
and this document uses the figure for nothing else.

**Likely failure point:** the hand-off. The business owner cannot run the CLI; the
developer will not fill in a browser questionnaire about intended purpose. The
site already has the right instinct in the wrong place: a "copy link to send to
your developer" button exists, at a scroll position below the measured median
reader.

**Consequence of failure:** neither completes. Measured: one assessment completion
in 91 days.

### U4. The independent consultant

**Arrives to evaluate**, not to be sold to. GTM profile E2: a fractional DPO or
privacy consultant adding AI Act scoping to an existing practice, serving 5 to 50
SME clients [Reasoned, not evidenced, inherited from
`MARKET-SIZING-2026-08-14.md` section 5, where it is labelled REASONED].

**Their task:** decide whether this tool is safe to put in front of a client.

**Likely failure point:** any page that overstates. One badge asserting a
compliance state disqualifies the tool for this reader permanently, and this
project has shipped exactly that: ledger N125, N129 and N144 record eleven sites
across eight files stating a compliance determination, and N144 records that the
**published package on PyPI still does**, printing a compliance score out of a
hundred, a verdict line and a risk tier, all of which this branch removed.

**Consequence of failure:** loss of the multiplier.

**Deliberately not served.** Two readers are out of scope and the site should say
so rather than serve them badly:

- The enterprise compliance function. Excluded by the market model itself
  (`MARKET-SIZING-2026-08-14.md` section 2: enterprise platforms of the
  Vanta/OneTrust class are excluded from the addressable market).
- **Anyone who wants a certificate.** E1's own stated disqualifier. This is not a
  marketing preference. Conformity is determined by regulators and notified
  bodies, not by a scanner, and the correct treatment is referral out.

---

## 2. Journeys

One structural finding governs all four: **every user arrives with the same first
question, and it is not "do I want to scan some code".** It is "does this apply to
me". The divergence between U1, U2, U3 and U4 happens *after* that question, not
before it. So the first view is the same for all four, and the routing is what
differs.

That is why the qualifier is the front door rather than one of two named entry
points. It supersedes, for the front door specifically, the direction reached in
`docs/venture/research-2026-08/e-dual-audience-architecture.md` section "What
follows for a design decision", item 2, which proposed two named entry points
because a named route requires no inference about the reader. **The reason for
departing:** two named entry points still require the reader to know which one
they are, and U1's defining characteristic is that they do not know. The named
entry points survive, one layer down, inside the result.

### J1. U1, the non-technical founder

| | |
|---|---|
| Entry | Search, or a link somebody sent them |
| The opening seconds must deliver | That this page will tell them whether the rules reach them, in words they already own. The abandonment hazard is front-loaded: see `docs/venture/research-2026-08/a-above-the-fold.md` |
| Path | Five plain-language questions on one card, each with a one-sentence explanation of what it means. "Not sure" is an answer. |
| Result | A named list of what their answers point at, and a named list of what is still unsettled. Never a tier, never a score, never a compliance state. |
| Onward | Free: the fuller browser assessment, or a guide. Paid: a written starter assessment. Consultant: registered interest, honestly labelled as not yet bookable. |
| Honest end state | "Here is what you still have to find out, and here is who can settle it." |

### J2. U2, the technical founder or lead

Identical entry, identical first view. **The divergence is a single line inside the
result**, offering the one-line scan to a reader who has just demonstrated, by
their own answers, that they have something worth scanning. It is offered, not
imposed, and it is phrased as a capability rather than as a qualification test.

### J3. U3, the small team

Identical entry. The result must be **forwardable**: a link that carries the
answers, so the business owner can send the technical owner the same page in the
same state, and so the same page can be sent to whoever asked the original
question. This is the hand-off failure named in U3, addressed at the point where
it occurs rather than below the 29% median scroll depth recorded in
`docs/venture/research-2026-08/b-stickiness-and-sample-size.md`.

### J4. U4, the consultant

Identical entry, and they will read the result adversarially. **What they are
looking for is the refusal.** The result must visibly decline to determine, name
the facts it cannot settle, and link the limits. The design instruction is that
the limits are not a disclaimer in the footer; they are part of the answer.

### What each journey must never do

Common to all four, and taken from `CLAUDE.md` and `AGENTS.md` rather than
invented here: never present a scan or an answer as a compliance determination,
certification or conformity assessment; never present "not flagged" as
"compliant"; never present "not excluded" as "admissible"; never present a paid
report as a determination or a consultant as a certification.

---

## 3. Information architecture

### What the homepage was

Measured here at `1518213` from `site/index.html`, in document order: hero with
install command and four-tab terminal; who is this for; what Regula tells you;
current timeline; how it works; what it does; runs where you work; where Regula
fits in the market; what Regula does not do; guides and analysis; common
questions; closing call to action.

Two properties of that order matter. The first interactive thing is a terminal
command, which serves U2 and excludes U1 and most of U3. And "what Regula does not
do", which is the section U4 is looking for and the one that makes the tool
trustworthy to U1, sits ninth.

### What it becomes

1. **The qualifier.** Five plain-language questions, one card, and the answer.
2. **What happens next**, the three routes named honestly: free, paid, consultant.
3. **What Regula is and is not.** Moved up from ninth. This is the credibility
   signal available to a product with no customers, and it is available precisely
   because the honesty rules already require it.
4. **If you are comfortable with a terminal.** The developer entry, with the real
   transcript that was previously the front door.
5. Everything else, in its existing order.

### Why this order, and how strong each reason is

| Decision | Basis | Status |
|---|---|---|
| Qualifier first, code later | All four users share the first question; U1 and most of U3 cannot act on a terminal command | Reasoned, not evidenced |
| One card, all five questions visible, **no progress indicator** | Conrad et al. 2010, below | Evidenced |
| The hardest question last | Conrad et al. 2010 and, in its own literature review, Crawford et al. 2001 | Evidenced |
| "Not sure" as a first-class answer | Anchor A5 in `docs/venture/gtm-2026-08-14/MARKET-SIZING-2026-08-14.md`: 40% of 106 specialist-classified systems were unclear | Verified anchor, narrow use |
| Limits moved up to third | Stanford Guidelines for Web Credibility, and the fact that the honesty rules and the credibility literature point the same way | Reasoned, with a dated source |
| No claim of improvement | 1.7-fold detection floor at this traffic | Measured |

**Conrad, F. G., Couper, M. P., Tourangeau, R., and Peytchev, A. (2010). "The
impact of progress indicators on task completion." *Interacting with Computers*
22(5), 417-427. DOI 10.1016/j.intcom.2010.03.001.**

From DOI 10.1016/j.intcom.2010.03.001, as recorded in
`docs/venture/research-2026-08/c-multi-step-form-completion.md`: Experiment 1,
3,179 users, overall breakoff 14.4%, with Slow-to-Fast indicator 21.8%,
Constant speed 14.4%, **no indicator at all 12.7%** and Fast-to-Slow 11.3%;
chi-squared(3) = 31.57, p < .001. Experiment 2 replicated it at 14.3, 14.4, 19.9
and 11.3 percent for None, Constant Speed, Slow-to-Fast and Fast-to-Slow;
chi-squared(3) = 27.92, p < .001.

The asymmetry is the design instruction. A badly calibrated indicator reliably
increased abandonment against showing none; a well calibrated one did not
reliably reduce it. **Showing no indicator is a legitimate choice, and in both
experiments it outperformed the badly calibrated one** (same source, DOI
10.1016/j.intcom.2010.03.001, quoted in
`docs/venture/research-2026-08/c-multi-step-form-completion.md`). A single card
with five short questions makes the remaining effort visible and finite at a
glance, which is the encouraging first frame obtained without an indicator at
all.

**Provenance warning, repeated at the point of use rather than left in the
source document.** The publisher record could not be opened from this machine:
ScienceDirect, the ACM Digital Library and Hogrefe each returned HTTP 403 and
PubMed Central returned a CAPTCHA on 2026-08-17. The figures are quoted from the
accepted manuscript's Results section as surfaced by a search index. The paper's
identity is corroborated across four independent listings; **the figures are one
retrieval short of the standard the rest of this document holds, and anyone
acting further on them should open the PDF first.**

**The assumption behind the card was tested here, and it failed.**
`c-multi-step-form-completion.md` reasoned for a single card on the stated
assumption "that five questions fit above the fold on a 320px viewport, which is
testable rather than arguable". It was tested, by serving the page and reading
each question block's bounding rectangle against the viewport height:

| viewport | questions fully visible |
|---|---|
| 1400x900 | 3 |
| 1280x720 | 2 |
| 390x844 | 1 |
| 320x568 | 0 |

The fallback stated in
`docs/venture/research-2026-08/c-multi-step-form-completion.md` was one question
per screen with a 1-of-5 counter. **It was not taken**, and the reason is not
convenience. What the evidence supports is an
*encouraging first frame* rather than a creeping percentage, and the static
`1/5` numeral on each question delivers that without depending on the fold at
all; one question per screen would also hide the shape of what is being asked
from a reader whose defining problem is not knowing what they are being asked.
The assumption is recorded as falsified rather than quietly dropped, and the
same measurement is recorded in ledger N168 in `docs/improvement/LEDGER.md`.
What did change is that the options wrap instead of stacking on narrow screens,
which cut the card's height by 26% at 320px, from 2,651 CSS pixels to 1,964,
measured before and after with the page served locally; the rule that does it is
in `site/assets/site.css` and carries the same note.

**The Stanford source and its age.** The Stanford Guidelines for Web Credibility,
verified at https://credibility.stanford.edu and recorded at ledger N132 in
`docs/improvement/LEDGER.md`, are "based on
three years of research that included over 4,500 people" and their sixth
guideline is to design a site so it looks professional. The work is early-2000s
vintage and **its age travels with it**; it is used here only to corroborate a
direction the honesty rules already require, never as the reason for it.

### What no evidence was found for

Stated as empty searches rather than filled in, because this programme has a
recorded history of accepting confident synthesis over vendor content
(ledger N132, where all three supplied statistics failed at source, one of them
attributed to a firm that had wound down before its stated publication year).

- **Outcome-led against category-led headlines.** No controlled comparison found
  for developer tools or professional services.
  [`a-above-the-fold.md`]
- **One question per screen against a single card, at five questions.** No source
  settles it. The card is chosen on the reasoning above.
  [`c-multi-step-form-completion.md`]
- **Serving a technical and a non-technical audience from one page.** The search
  returned vendor content, an encyclopaedia entry, two papers about algorithmic
  transparency rather than page architecture, a practitioner blog post and a
  diagramming convention. None is evidence. [`e-dual-audience-architecture.md`]
- **Form completion benchmarks.** Deliberately not quoted. Self-reported by form
  vendors over self-selected customer bases with no stated methodology, and this
  site could not use one anyway: one visitor completed the existing assessment in
  91 days, so there is nothing to compare a benchmark against.

### The one test that would overturn most of this

Show the page to two representative readers, one developer and one non-technical
founder, and ask them what the product does and what it just told them. **This
project has never run that test.** Every design conclusion in this document is
weaker than that one test would be, and this sentence is the deliverable's
statement of what human validation remains outstanding.

---

## 4. Design screening

Screened against the list the brief supplied. Findings and dispositions.

Screened across every tracked page, enumerated with `git ls-files` rather than
by reading, per measurement rule 4c. Two items in this table were present on
pages that are **not** among the three refactored here, and an eyeball screening
of the pages being changed would have reported both as absent.

| Item | Present at `1518213`? | Disposition |
|---|---|---|
| Radial orbs | **Yes.** `.hero-glow`, a 700px `radial-gradient(circle, ...)`; `.final-glow`, an 800x600 `radial-gradient(ellipse, ...)`, plus per-page inline overrides of the second on three pages. | **Removed**, with their rules and their inline overrides. Both were decoration with no informational content. Removing them had a consequence nobody would predict: four entries in `.claim-quarantine.json` recorded percentages inside those gradients as suppressed-but-present, and they are now absent, which is a different disposition. Corrected; see ledger N175. |
| Decorative terminal windows | **Partly.** The transcript is real output, bound to a command re-run on every check (N135 to N142). The window chrome around it was three coloured dots imitating a desktop operating system. | **Split.** Real output kept and promoted; the imitation window chrome removed. |
| Gradient stripe band | **Yes, on 18 pages.** `#progress-bar`, a fixed 2px `linear-gradient(90deg, accent, purple)`. Enumerated with `git ls-files`, not read: it was **not** on the three pages refactored here, which is why an eyeball screening of those three would have missed it entirely. | **Removed sitewide**, with its rule, its four different driver scripts, and its declaration in `content/regulations/_template.html`. It is also the progress-indicator failure mode from Conrad et al. rendered as decoration: a bar that creeps from 0%. |
| Purple and black | **Partly.** `--purple: #7c3aed` on `--bg: #070711`. | **Reduced.** Purple retained only where it already carries meaning in existing components; it is not used anywhere in the new work. |
| Three feature cards in a row | Yes, in several places. | **Kept where the three things are genuinely distinct** and not tiers of one thing. Named in the deliberate-keep list below. |
| Three pricing tiers | Yes. | **Kept, and justified.** These are not good/better/best. They are a free tool, a fixed-scope engagement and a time-based engagement, and the free one is the visually emphasised card, which is the opposite of an upsell ladder. |
| Checkmark bullet lists | No. Lists use default markers. | No action. |
| Emojis | No. | No action. |
| Em dashes | Guarded. `scripts/` carries an em-dash guard covering the literal character and its entity forms. | No action; new prose written without them. |
| Inter / Geist / Space Grotesk as the default choice | No. DM Sans, Fraunces and JetBrains Mono, self-hosted. | **Kept and now documented as deliberate**: a grotesque for interface text, a serif with real optical sizing for editorial headings, a monospace reserved for command output. |
| Uniform soft corner radius | No. Five radius tokens exist and are used differently. | No action. |
| Pure white background | No, dark. | No action. |
| Rainbow colour | Partly: the risk tiers use red, amber, green and blue. | **Kept.** These encode severity, they are not decoration, and they are never the only channel: every tier also carries a text label. |
| Neon colour | No. | No action. |
| Default pastel palettes | No. | No action. |
| Bento grids | No. | No action. |
| Dot grids | No. | No action. |
| Sparkle icons | No. | No action. |
| Blue-tinted side icons | No icon set is used. | No action. |
| Drop shadow on everything | One shadow token, used sparingly. | No action. |
| Hover animation on everything | Present on cards and links. | **Reduced in the new work**, and every animation is already inside a `prefers-reduced-motion` guard. |
| Animated arrows | No. | No action. |
| Fake testimonials | No, and none may ever be added: there are no users to quote. | No action. |
| "It's not X, it's Y" copy | No. The limitation sentences are statements of scope, not a rhetorical device. | No action. |
| No real product demo | **Inverted, and satisfied.** Real transcript bound to a re-run command. | Kept and promoted. |
| Missing terms of service | **Inverted, and satisfied.** `site/terms.html`, `site/terms-de.html`, `site/terms-pt-br.html`. | Verified linked from the footer of every refactored page. |
| Missing privacy policy | **Inverted, and satisfied.** `site/privacy.html` and both locale versions. | Same. |
| Missing skeleton loaders | **Inverted, and deliberately not built.** | **Justified non-fix.** The qualifier does no asynchronous work: it is a pure client-side computation over five radio groups and completes within a frame. A skeleton would simulate latency that does not exist, which is fabricating work to look busy. The states that do exist here are designed and exercised instead: initial, incomplete-with-error, answered, cleared, and no-JavaScript. |

**Three feature cards kept, and why.** The audience cards describe three different
readers, the routes describe three different commercial relationships, and the
pricing cards describe three different engagements. In each case the three are
mutually exclusive and jointly meaningful, which is the condition under which a
row of three is an information structure rather than a layout habit.

---

## 5. What this work does not fix

Recorded so it is not mistaken for complete.

1. **The browser assessment's own question wording is unchanged.** `site/assess/`
   still opens on the Article 3(1) definition. The qualifier now stands in front
   of it and translates, but the deeper questionnaire remains written in the
   law's vocabulary. Rewriting 17 EU questions plus the Korea and Colorado sets,
   in three locales, with their URL-stable ordering and their shared scoring
   engine, is a larger change than this one and is not attempted here.
2. **No human has read any of it.** See section 3.
3. **The consultant is not named.** The pricing page states that the named
   consultant, the duration and the full terms will be published before booking
   opens. Until then the consultant route is described as what it is, which is an
   email, and never as a bookable service.
4. **The pricing direction remains Reasoned, not evidenced**, per ledger N132.
   All three statistics offered for it failed at source.
