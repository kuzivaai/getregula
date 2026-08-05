# Manual evidence-readiness baseline

STATUS: PREPARATION ONLY
EXTERNAL ACTION: DISABLED
VENTURE DECISION: STOP
PRODUCT PILOT: NOT APPROVED

Protocol status: `PREREGISTERED_NOT_EXECUTED`.

## Input and unit

Future input is one real permissioned buyer diligence request, one named supplier
product and deployment context, one permissioned evidence set and one trained
human reviewer. Regula output is hidden from the reviewer and supplier during the
baseline and remains non-decision-bearing.

The provisional unit is one buyer question-to-response decision, because that is
the smallest buyer-visible task joining request, claim, evidence and escalation.
If a real questionnaire combines multiple decisions in one question, the unit
must be decomposed before review using a written rule: separate each independently
answerable obligation, evidence request or decision. Compound wording remains one
unit only where the buyer accepts one inseparable decision. Freeze the decomposition
and denominator before review. Changing either after outcomes are visible is a
protocol deviation.

## Status codebook

`DIRECTLY_EVIDENCED`, `SUPPLIER_ASSERTED`, `PARTIALLY_EVIDENCED`, `MISSING`,
`STALE`, `CONTRADICTORY`, `NOT_TECHNICALLY_ASSESSABLE`,
`REQUIRES_LEGAL_DECISION`, `REQUIRES_BUYER_DECISION`, and
`REQUIRES_INDEPENDENT_REVIEW`. Every status needs an evidence pointer, reason,
reviewer, timestamp and version. Each unit receives one evidence state plus zero
or more escalation states; escalation never replaces evidence state. Precedence
for the primary numerator is `CONTRADICTORY`, `STALE`, `MISSING`,
`PARTIALLY_EVIDENCED`, then `DIRECTLY_EVIDENCED`. Silence is not `MISSING`; it is
unreviewed and excluded with a reported reason.

## Procedure

1. Freeze request, context, evidence manifest and atomic units.
2. Train reviewer on the codebook using material outside the study.
3. Start timers. Record active reviewer and supplier time separately.
4. For each unit, record status, evidence pointer, confidence, correction and
   escalation without seeing Regula output.
5. Freeze the baseline record and hash it before any tool output is opened.
6. Freeze questions needing clarification before any response. Obtain buyer
   clarification only through the permissioned route, retain pre-clarification
   status, and record response time and post-clarification status separately.

Primary outcome: directly evidenced units divided by all frozen reviewed units;
report partially evidenced units separately and never add them to the numerator.
Safety outcomes: unsupported-assertion rate, missed contradiction and missed stale
or missing evidence, measured against independently frozen reference labels rather
than reviewer self-assessment. Secondary outcomes: active reviewer/supplier time, corrections,
unanswered units, escalations, clarification requests, traceability and exact
reproduction by a second independently trained reviewer from the frozen input,
with raw disagreements and adjudication retained. Evidence reuse is
exploratory and never presumed lawful.

No effect size or variance estimate exists. The first study is exploratory;
inferential, representative and market-wide claims are prohibited. It supplies
variance, clustering and burden information for a later power analysis. The
manual method must remain useful if Regula is abandoned.
