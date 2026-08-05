# Direct-transaction discovery method

STATUS: PREREGISTERED_NOT_EXECUTED
EXTERNAL_CONTACT: NOT_AUTHORISED
REAL_DATA COLLECTION: DISABLED
H1: ABANDONED
H2: NOT CREATED

## Transaction-qualified population

Include only a participant who personally took part in the previous 12 months
in an active enterprise sale, supplier onboarding or procurement review for an
AI-enabled software product involving information security, privacy, AI
governance, model risk, third-party risk, technical assurance or procurement
due diligence. This is an inclusion rule,
not a market or beachhead.

Eligible supplier roles: founder, technical founder, CTO, security/compliance
lead, sales engineer or enterprise account lead. Eligible buyer roles:
procurement, third-party risk, information security, data protection, AI
governance, model risk, legal operations or technical assurance.

Exclude hypothetical processes; advisers with no direct transaction; vendors
only marketing themselves; anyone unable to identify a recent event; anyone
whose account would require confidential or regulated disclosure; and anyone
selected because they like Regula.

## Event screener

Ask without collecting names or documents:

1. Were you personally involved in a completed or active enterprise transaction
   during the last 12 months? If no, exclude.
2. Were you on the supplier or buyer/reviewer side, and what role archetype did
   you perform? If only an observer or commentator, exclude.
3. Did the transaction concern an AI-enabled software product? If no, exclude.
4. Did it reach active sale, procurement or production-onboarding review? If no,
   exclude.
5. Which qualifying review occurred: information security, privacy, AI
   governance, model risk, third-party risk, technical assurance or procurement
   diligence? If none, exclude.
6. Can you discuss the event at a non-confidential, organisation-minimised
   level without documents, names, contract terms or security findings? If no,
   exclude from Stage A.

## Interview opening and neutrality

State: this is research, not sales; Regula is not being offered or demonstrated;
no confidential information, documents or names are requested; recording is off;
questions may be declined; participation can stop. Begin: “Please take the most
recent qualifying transaction. What happened first?” Do not name Regula during
the transaction account. Use three ordered phases: (1) an uninterrupted event
account; (2) neutral factual probes using the core questions below; (3) only
after the account is closed, analyst coding of technical observability. The
interviewer must not prompt for source-derived or Regula-compatible evidence.

If a participant begins to disclose a name, confidential fact, contract term or
security-sensitive detail, interrupt, ask them not to continue, omit or redact
the note, and apply the reviewed incident/deletion process. If safe discussion
cannot continue, stop the interview.

## Supplier guide

Core questions, in order: What triggered the review? What did the buyer ask for?
What already existed, and what was created? Who did the work? What time or
rework was actually recorded or recalled, on what basis and with what
uncertainty? Did the transaction change, pause, fail or proceed, and what reason
was actually given? What workaround, tool or adviser was actually used? Was any
money actually committed to completing the review, by which role and for what?
What could not leave the supplier? Ask for non-confidential ranges, not exact
commercial values. Do not encode hypothetical prices or enthusiasm as economic
evidence; they are never willingness-to-pay evidence.

## Buyer/reviewer guide

Core questions, in order: What triggered the review? What evidence was
requested? Which requirements, if any, were mandatory, risk-based or
negotiable? Who requested, reviewed, blocked or accepted residual risk? Did any
evidence lead to follow-up, and if so why? Did anything require independent
verification? What system or manual process was used? What made the actual
answer accepted, conditional or rejected? Ask first whether problems occurred;
do not presume weak evidence or unusable answers. Include cases where the
supplier passed quickly or the existing process worked well.

Allowed probes are “What happened next?”, “How do you know?”, “What record or
range supports that without disclosing it?”, and “Was that observed or your
interpretation?”. Prohibited prompts include naming Regula, suggesting that code
evidence should matter, asking whether the participant would buy the product,
or treating enthusiasm as commitment.

## Transaction coding and negative cases

Create one linked record for each requirement. Code its category as
`TECHNICAL_ARTEFACT`, `SUPPLIER_ATTESTATION`,
`ORGANISATIONAL`, `CONTRACTUAL`, `LEGAL_JUDGEMENT`, `BUYER_DECISION`,
`INDEPENDENT_ASSURANCE`, or `NOT_ASSESSABLE`. Evidence states are
`EXISTED`, `CREATED`, `MISSING`, `STALE`, `CONTRADICTORY`, `REJECTED`,
`ACCEPTED_WITH_CONDITIONS`, `ACCEPTED`, and `UNKNOWN`.

A negative case is transaction-qualified but shows no material burden, no
repeatable requirement, adequate incumbent handling, negligible technical
evidence, buyer/supplier disagreement, or no plausible economic consequence.
It remains in analysis and can stop the programme.

Deliberately seek, without quotas implying prevalence: a fast pass; a delayed or
rejected transaction; a buyer satisfied with the evidence; a buyer requiring
independent assurance; an adequate incumbent; immaterial code evidence; no
dedicated budget; and a supplier unwilling or unable to share technical evidence.

Burden is retained as a non-confidential range plus unit, basis, affected role
and uncertainty; “material” is not a free-standing label. Delay uses the same
rule. Each requirement links its state, requester/reviewer role, acceptance
outcome and observability basis. Observability is assessed after the interview,
per requirement, with `NOT_ASSESSABLE` available. Future account and transaction
IDs must be random tokens, not derived from identity, organisation, date or
event facts. They are pseudonyms, not proof of anonymity. Only a separately
permissioned Layer 2 linkage register may associate two accounts with one
transaction; the analytical corpus carries the random transaction ID but no
identity or contact mapping. Independence requires different transaction IDs
and no evidence that the events are the same transaction.

Both bounds must be non-negative; lower must not exceed upper; both may be null
only when the unit is `UNKNOWN` and the basis explains why. A bounded qualitative
account uses null bounds, `UNKNOWN`, and a non-empty observed basis; it cannot be
called measured. An `INADEQUATE` substitute requires a non-empty account of the
observed failure criterion and contrary evidence. Empty strings are invalid.

Before any H2 gate is evaluated, a corpus check must enforce unique account IDs,
verify that every transaction group represents one event, apply the range rules,
and reject an unsupported `INADEQUATE` result. The object schema cannot establish
these cross-record facts by itself. A second analyst must independently review
observability, contradiction and negative-case coding; disagreement is retained
and adjudicated with the basis recorded. Until that control exists and passes,
H2 cannot be gated.

## Sequential evidence plan

Stage A is an access/method test: two supplier-side and two buyer/reviewer-side
participants across at least two organisations, denominator four participants.
It is not prevalence, representativeness or market evidence. Stage B proceeds in
batches of two only after each batch updates evidence states, contradictions,
negative cases, information power and the highest-value next role. Review no
later than 12 participants; 12 is a management maximum, not proof of saturation.

Stop earlier for access failure, hypothetical accounts, no repeated transaction,
buyer/supplier non-alignment, adequate incumbents, negligible technical evidence,
or unacceptable data/liability boundaries.

After every batch, write an information-power memo recording aim specificity,
participant specificity, dialogue quality, theory contribution, analysis
strategy, new mechanisms, contradictions, negative-case coverage and buyer-
supplier divergence. Rank the next role by qualitative value of information:
decision consequence, likelihood that the role can settle it, access cost and
privacy risk. Do not fabricate probabilities. “Saturation” may be used only with
a named construct and evidence that successive batches added none of it.

Stage B must retain both sides unless a recorded information-power assessment
explains the imbalance; no organisation or role may dominate the inference.
“No repeated transaction” means that, after a completed batch, no two independent
transaction IDs share a bounded trigger, job, supplier profile, buyer type,
geography, deployment stage and evidence exchange. Non-alignment means linked
buyer/supplier accounts materially disagree on a gate fact after uncertainty is
retained; it triggers review, not forced adjudication.

## H2 gate

H2 is not created. It may be preregistered only after three independent recent
transactions share a bounded trigger, job, supplier profile, buyer type,
geography, deployment stage and evidence exchange; two suppliers are represented;
buyer-side evidence matches two of those transactions under the separately
permissioned transaction-linkage rule;
bounded qualitative or measured burden occurs
in more than one; a buyer gives acceptance/rejection criteria; a material subset
is `OBSERVABILITY_INDICATED` by the accounts; its incumbent workaround has a
retained observed inadequacy basis;
separate permission for a minimised, pseudonymised representative artefact is
feasible; and
no negative case already falsifies the proposed advantage. These are management
gates, not statistical validation. Willingness to pay remains unvalidated.
Three selected transactions do not establish prevalence, recurrence, a market
or demand. Analogue evidence may be retained as context but cannot pass a buyer
acceptance gate.

Any H2 produced is explicitly generated from these discovery cases, not
preregistered before them and not validated by them. It must list every retained
negative case, freeze the claimed mechanism and its falsifiers, and be tested on
fresh holdout transactions. A permissioned artefact check is required before
technical observability can be called demonstrated or Regula-relevant. H2
creation establishes neither Regula performance nor advantage over a transparent
manual baseline: `TECHNICAL_FIT: FAILED_UNTIL_NEW_EVIDENCE` and
`DIFFERENTIATION: NOT_DEMONSTRATED` remain unchanged until prospective comparison.
