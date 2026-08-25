# Regula founder usability research gate and protocol

**Prepared:** 25 August 2026

**Status:** PREPARATION ONLY

**External research:** DISABLED

**Decision:** HOLD_RESEARCH_PRIVACY_GATE

No participant has been contacted and no research session has been run under
this protocol. This document does not approve recruitment, establish a lawful
basis, appoint a controller, approve a storage provider or replace qualified
privacy review. The machine-readable state is
`data/research_execution_gate.json`; `python3 -m scripts.research_gate --status`
must continue to fail closed while any blocker remains.

## 1. Decision this study is allowed to inform

The study may identify comprehension and task-completion failures in two current
Regula journeys:

1. a technical founder or AI product owner uses the founder-first homepage to
   decide whether Regula is relevant and what to do next;
2. an AI-governance, audit or advisory professional inspects a
   reviewer-completable evidence pack and explains what it can and cannot prove.

It cannot establish market demand, conversion rate, legal correctness,
compliance, scanner accuracy, representative population preference or
willingness to pay. Those require different evidence.

## 2. Preregistered questions and counterevidence

### Founder journey

Primary question: after completing the homepage journey without coaching, can
the participant correctly explain both what Regula observed and what it did not
decide?

Evidence against the design includes:

- describing Regula as legal advice, certification or a compliance decision;
- believing source code alone settles jurisdiction, intended purpose, operator
  role or legal risk tier;
- being unable to find or understand an appropriate next action;
- mistaking an unavailable human-service hypothesis for a bookable service;
- abandoning because the language, hierarchy or interaction is unclear.

### Evidence-pack journey

Primary question: can a governance professional locate an observation, its
source, an unresolved fact and the human-completion boundary without extensive
facilitator explanation?

Evidence against the design includes unsupported assurance, inability to trace
an observation, confusion between a scaffold and substantive evidence, or more
review work than the artefact saves.

## 3. Formative sample and reporting boundary

The first round is five participants per journey. This is a design-management
minimum for finding task failures, not a power calculation and not a
representative sample. Report integer counts with the denominator and
de-identified failure themes. Do not publish percentages without the underlying
counts. Do not claim saturation, market prevalence or population conversion.

Recruit participants who actually match the relevant role. Friends, project
contributors and compliance specialists cannot be silently substituted for
non-technical founders. Record conflicts and prior familiarity outside Git in
the approved private system.

## 4. Session tasks

### Founder task, 30 minutes maximum

1. Open the production homepage from a clean browser context.
2. Without an introduction to the product, explain what the page appears to
   offer and who it is for.
3. Complete the five-question qualifier using a neutral fictional scenario
   supplied by the facilitator. Do not enter real company or personal data.
4. Explain the result, including what the product observed, what remains
   unresolved and what the product did not decide.
5. Choose the next action that would be appropriate for the fictional scenario.
6. Locate the limitations and explain one material limitation.

### Evidence-pack task, 45 minutes maximum

1. Use only the committed fictional sample pack.
2. Locate one code observation and its evidence pointer.
3. Locate one unresolved deployment fact.
4. Explain which fields require human completion.
5. Explain whether the pack proves compliance and why.
6. Identify the next reviewer or evidence source needed.

The facilitator may ask “what are you thinking?” or “what would you do next?”
but must not explain Regula, correct terminology or point to a control until the
task has been scored.

## 5. Scoring fixed before recruitment

For every participant, record each task as `COMPLETED_UNASSISTED`,
`COMPLETED_AFTER_PROMPT`, `FAILED` or `NOT_ASSESSABLE`.

The founder comprehension outcome passes only when the participant, without
correction, states both:

- Regula reports code-observable indicators or evidence; and
- Regula does not determine legal applicability, risk tier, obligations or
  compliance from source code alone.

Also record abandonment, wrong next action, unavailable-control confusion,
critical accessibility barriers, confidence in their explanation and the exact
facilitator prompts used. Confidence is descriptive and never overrides task
performance.

## 6. Privacy and safety defaults

Until the gate is separately cleared:

- do not recruit or contact anyone;
- do not create a waitlist or transmitting web form;
- do not record audio, video, screens or verbatim transcripts;
- do not receive customer code, repositories, documents, contracts, security
  findings or confidential scenarios;
- do not collect special-category or criminal-offence data;
- do not store names, contact details, employer names or session notes in Git;
- do not use tracking pixels or individual analytics to link a session to site
  activity;
- do not combine research participation with sales, service delivery or a legal
  assessment.

When authorised, use a random participant token that is not derived from name,
email, employer or date. Keep the identity/contact register separate from
pseudonymous analytical notes. Pseudonymised does not mean anonymous.

Participation permission is an ethical and operational control; it is not
automatically the controller's data-protection lawful basis. Use the existing
participant-information, participation-permission and withdrawal templates only
after the named controller has completed them, storage and rights handling have
been tested, and required review has been recorded.

## 7. Launch gate

External recruitment remains prohibited until every field in
`required_launch_facts` is populated with real, reviewable evidence outside this
public repository where appropriate, including:

- controller identity and contact;
- research lead and applicable jurisdictions;
- lawful basis and its review evidence;
- approved participant-notice version and approval evidence;
- storage system, region, access roles, processors and transfers;
- retention period, withdrawal, rights-request and incident routes;
- participant source, approved sender and incentive policy.

The current protocol is `NO_RECORDING`. Changing that choice requires a new
privacy and consent assessment, not a field edit.

After the factual fields are complete, an authenticated owner must still issue a
separate dated launch authorisation. The validator intentionally cannot turn
repository fields into permission to contact people.

## 8. Stop and incident rules

Stop the session immediately if a participant starts disclosing confidential
material, personal data about another person, source code, credentials, security
findings or information outside the approved scope. Do not inspect unsolicited
files or links. Quarantine and escalate through the approved incident route.

Stop the study if the notice, storage, access, deletion or withdrawal process
does not operate as described; if a participant objects; or if the research is
being used as a sales or legal-advice pathway. Resolve the issue before any
further contact.

## 9. Result record

The research result must preserve:

- invitation, acceptance, attendance and completion counts;
- role-fit and exclusion counts;
- task outcomes and all facilitator prompts;
- counterevidence before favourable themes;
- deviations, incidents, withdrawals and deletions;
- exact product version, page commit and sample-pack hash;
- limitations and the decision taken.

No receipt, private consent record and approved analytical record means no
completed-session claim. Raw personal data and the identity map never belong in
the public repository.

## 10. Current method and privacy foundations

Rechecked against the primary pages on 25 August 2026:

- the [ICO lawful-basis guide](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/lawful-basis/a-guide-to-lawful-basis/)
  says a valid basis under UK GDPR Article 6 must be selected and documented
  before personal information is processed, and that the appropriate basis
  depends on the purpose and relationship;
- the [ICO research grounds guidance](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/the-research-provisions/principles-and-grounds-for-processing/)
  distinguishes consent to participate in research from consent used as the
  data-protection lawful basis;
- the [ESRC/UKRI consent guidance](https://www.ukri.org/councils/esrc/guidance-for-applicants/research-ethics-guidance/consent/)
  supports informed and voluntary participation, question refusal, withdrawal
  boundaries and clear data-management information; and
- the [MRS qualitative-research guidance](https://www.mrs.org.uk/standards/guidelines-for-qualitative-research)
  separates research from sales and treats participant privacy and honest,
  non-intrusive practice as core controls. Its rules bind MRS members and
  Company Partners; here it is used as a professional benchmark, not as evidence
  of membership or legal approval.

These sources support the controls, not the application of law to Regula's
future study. Controller, purpose, jurisdictions, lawful basis and review remain
unresolved facts.
