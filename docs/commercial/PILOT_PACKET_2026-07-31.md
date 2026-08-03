# Pilot packet — evidence-validation only

## Status and boundary

Regula is **not approved for a customer product pilot** by commercial_v1. This
packet is immediately usable only for a no-claim discovery and independent
validation engagement. It must not be sold as compliance certification,
autonomous high-risk classification, legal advice or demonstrated accuracy.

## Provisional customer and job

Provisional ICP: an EU AI-governance consultancy or regulated-software
engineering team able to provide a representative, non-sensitive repository
and independent reviewers. User: software assurance engineer or consultant.
Buyer: governance lead, engineering director or consulting partner. Job:
produce a reviewable inventory/evidence scaffold while preserving exact source
provenance and explicit uncertainty. Present workaround: dependency manifests,
repository search, questionnaires and manually assembled evidence folders.

Measurable problem hypothesis: qualified reviewers spend material time finding
AI dependencies and assembling provenance, and an accurate local tool could
reduce elapsed review time without increasing missed items or false-alert
burden. This is UNVALIDATED.

## Proposed validation scope

- 30 or more prospectively sampled buyer-relevant repositories, sized by a
  recorded power analysis; no proprietary code enters the public repository.
- Two independent human raters, blinded tool outputs, adjudication and raw
  disagreements.
- Frozen Regula, transparent baseline and source-event schema.
- Deliverables: annotation guide, hashed manifest, raw outputs, adjudicated
  labels, per-repository metrics, uncertainty, failure classes and go/stop memo.
- Exclusions: legal certification, autonomous Article 6 decisions, production
  deployment, personal data, paid APIs, detector tuning after holdout results,
  and any public performance claim before review.

Customer evidence required: repository access under an agreed data boundary,
dependency/build manifests, intended-purpose statement, deployment context,
known AI integrations and two qualified raters. Customer effort assumption:
two raters plus an adjudicator, repository owner support and a security review
of local execution. This effort has not been measured.

## Acceptance and failure criteria

Technical acceptance reuses the frozen Candidate A gate: precision and recall
Wilson 95% lower bounds each at least 0.90, identical normalised clean reruns,
complete manifest accounting, verified evidence manifests, no concealed weak
stratum, and meaningful advantage over the transparent baseline. Commercial
success additionally requires at least three qualified organisations to
confirm the same costly workflow, two to provide representative data, and one
signed paid validation. Failure occurs on any accuracy gate miss, irreducible
legal ambiguity presented as fact, manual review burden no better than the
baseline, data-boundary rejection, or absence of willingness evidence.

## Five falsifiable demand hypotheses

1. At least 3/5 qualified interviewees report the inventory/provenance task at
   least monthly and can quantify its current time cost.
2. At least 2/5 will provide a representative repository and independent
   raters under the stated boundary.
3. At least 3/5 prefer local, inspectable evidence over a cloud-only workflow.
4. At least 2/5 say a manifest-verifiable scaffold changes a procurement or
   assurance decision, not merely presentation quality.
5. At least 1/5 signs a paid validation after seeing the measured limitations.

## Neutral interview guide and disqualifiers

Ask: “Walk me through the last repository-level AI inventory or evidence
review.” “What triggered it?” “What artefacts did you trust?” “Where were
errors found?” “How much reviewer time was used?” “What happens if an item is
missed?” “Which data may leave your environment?” “What would make a local
tool unusable?” “Who approves budget?” “What evidence would justify a trial?”

Disqualify evidence from respondents without the workflow, hypothetical-only
answers, vendor partners unable to criticise the product, data that cannot be
lawfully used, or engagements demanding autonomous legal certification.

## Offers and pricing tests

Design-partner offer: customer supplies representative repositories and
raters; owner supplies a frozen, local, transparent validation and returns all
raw evidence; no performance promise. Paid-validation offer: fixed-scope
independent benchmark and evidence pack with an explicit stop conclusion
allowed.

Pricing anchors are tests, not market prices: £1,500 for one repository and a
methods memo (assumes one review day); £5,000 for up to five repositories and
adjudicated findings (assumes four delivery days); £15,000 for an organisation
validation pack with governance workshop (assumes ten days). Reject the anchor
if delivery time, buyer value or procurement evidence contradicts its
assumption.

Kill the effort if no qualified organisation supplies data after ten
interviews, no paid validation follows two completed design-partner studies,
the transparent baseline remains non-inferior, or regulatory maintenance cost
exceeds measured recurring revenue.

## Future evidence table

| Date | Organisation/role | Qualified? | Last real workflow | Time/cost evidence | Repository offered? | Boundary accepted? | Commitment | Price reaction | Disconfirming evidence | Follow-up |
|---|---|---|---|---|---|---|---|---|---|---|
| | | | | | | | | | | |
