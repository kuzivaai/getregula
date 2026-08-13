# Paid consultant gate: product boundary and activation plan

**Date:** 2026-08-13

**Status:** DESIGN READY; PAYMENT AND BOOKING NOT ACTIVE

## Decision

Regula's free experience should continue to provide the questions, observed
code indicators, unresolved facts, evidence paths, and product limitations. The
first paid offer should sell human work: contextual fact review, evidence-quality
review, interpretation within a stated professional scope, prioritisation, a
live walkthrough, and a written action brief.

This is a more defensible boundary than withholding basic findings or safety
information. It makes the paid value costly to deliver and difficult to copy
without creating a dark pattern in which uncertainty or risk is used to force a
purchase.

No checkout or booking control is active. The website now states this visibly
and uses non-actionable, disabled labels for planned services.

## Proposed service ladder

### Free self-assessment — available

- Browser questions and the canonical unresolved-facts path.
- Local code-indicator scan.
- Transparent rule, evidence, and limitation output.
- Reviewer-completable evidence and documentation scaffolds.
- No legal determination and no professional advice.

### Consultant review — proposed first paid service

- One named AI-governance consultant.
- One pre-defined live session.
- Pre-session fact and scope intake.
- Review of Regula's observations, matched evidence, contradictions, and
  unresolved predicates.
- Prioritised action brief with owners, evidence gaps, and questions requiring a
  qualified specialist.
- Explicit boundary: not legal advice unless the named consultant is separately
  qualified and retained for that purpose.

### Organisation review — proposed scoped engagement

- Multiple systems or teams.
- Evidence and decision-register workshop.
- Governance ownership and remediation planning.
- Re-scan and review cadence.
- Separately scoped price, statement of work, data handling, and delivery terms.

## Root-cause analysis: why a payment gate cannot honestly be enabled today

### Direct cause

There is no confirmed live payment-and-fulfillment system. The repository has
no verified payment link, paid scheduling event, webhook, order record,
consultant roster, availability calendar, service price, or completed booking
path.

### Contributing causes

1. **The service is not fully specified.** Duration, preparation burden,
   deliverable format, turnaround, rescheduling, cancellation, refund, no-show,
   and escalation boundaries are unset.
2. **The provider is not identified.** A visitor cannot yet see the named legal
   seller, named consultant, credentials, jurisdiction, or complaint route.
3. **Professional scope is unresolved.** “Consultant support” must not imply
   legal advice, certification, conformity assessment, or regulator approval.
4. **Data handling is unresolved.** Intake may contain personal data,
   confidential business facts, source extracts, or security findings. The
   controller, processors, lawful basis, privacy notice, minimisation, retention,
   deletion, access, transfer, and breach routes are not approved.
5. **Tax and consumer terms are unresolved.** Currency, tax treatment, invoicing,
   pre-contract information, cancellation rights, refund handling, and the
   treatment of immediate service commencement require owner/accountant/legal
   confirmation for the actual seller and customer type.
6. **Fulfillment evidence is absent.** Payment success must create or unlock a
   real booking, send confirmation, create an internal delivery record, and
   support reconciliation and refund. None has been tested end to end.
7. **Demand and capacity are unmeasured.** A price should not be published as
   settled until delivery effort, consultant capacity, willingness to pay, and
   support load are measured without conflating user confusion with demand.

Current UK primary guidance reinforces these blockers. GOV.UK says distance
sellers must provide clear pre-order information including the total price,
cancellation conditions, and other contract information in a form the customer
can save. The ICO's Article 5 guidance requires lawfulness, transparency,
purpose limitation, data minimisation, storage limitation, and security for
personal data. HMRC's current VAT registration guidance sets a GBP 90,000
taxable-turnover threshold while also identifying cases where registration can
apply regardless of turnover; the actual seller and customer geography must be
resolved rather than inferred from that headline threshold.

Primary references:

- [GOV.UK: Online and distance selling](https://www.gov.uk/online-and-distance-selling-for-businesses)
- [ICO: Data protection principles](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/data-protection-principles/a-guide-to-the-data-protection-principles/)
- [GOV.UK: Register for VAT](https://www.gov.uk/vat-registration/when-to-register)

### Why not add a dead button now?

An actionable-looking control whose payment or booking path is unavailable
would violate the project's UX rules and destroy trust. An unvalidated checkout
could also collect money for a service that cannot be fulfilled. The safe
interim state is an explicit offer boundary with a clear unavailable status.

## Recommended technical route

### Preferred first implementation: paid scheduling event

Use a hosted scheduling product with Stripe connected to a single consultant
event type and require payment to book. Calendly's current official guidance
states that Stripe can be connected to an event type, payment can be required
upfront, amount/currency and terms can be set, and refunds remain the account
holder's manual responsibility. This is lower implementation risk than building
custom checkout, webhooks, calendar locking, receipts, and refund administration
for the first transaction.

Reference: [Calendly + Stripe](https://help.calendly.com/hc/en-us/articles/14077985848215).

### Alternative: Stripe Payment Link plus controlled fulfillment

Stripe Payment Links provide a hosted no-code checkout, reusable links, dynamic
payment methods, receipts, refunds, and post-payment redirects. A plain redirect
to an unprotected booking page is not sufficient proof of payment. If this route
is used, fulfillment must validate payment state through Stripe or a trusted
integration before offering a paid appointment.

References:

- [Stripe Payment Links](https://docs.stripe.com/payment-links)
- [Create Payment Links](https://docs.stripe.com/no-code/payment-links)
- [After a Payment Link payment](https://docs.stripe.com/payment-links/post-payment)

## Activation checklist

Payment remains disabled until every P0 item is evidenced.

### P0 — provider, service, and professional boundary

- [ ] Identify the legal seller and customer contact route.
- [ ] Name the consultant and verify actual availability.
- [ ] Publish the consultant's relevant credentials without exaggeration.
- [ ] Define duration, preparation, deliverable, turnaround, and support limits.
- [ ] State that the service is AI-governance support, not legal advice, unless a
      separately qualified legal professional is engaged.
- [ ] Define referral triggers for legal, security, accessibility, employment,
      privacy, or sector-specific advice.

### P0 — commercial and consumer terms

- [ ] Set and validate price, currency, customer type, and tax treatment.
- [ ] Publish pre-contract service information and total price.
- [ ] Define rescheduling, cancellation, refund, no-show, and provider-cancellation
      terms.
- [ ] Confirm how any consumer cancellation period and request for early service
      commencement apply to the actual service.
- [ ] Define invoice/receipt and complaint handling.

### P0 — privacy and evidence handling

- [ ] Approve controller, processors, purposes, lawful basis, and privacy notice.
- [ ] Minimise intake; prohibit source-code upload by default.
- [ ] Define permitted evidence types and a secure transfer route.
- [ ] Set access, retention, deletion, backup, transfer, and breach procedures.
- [ ] Prevent payment metadata from being treated as permission to use consulting
      content for product research or marketing.

### P0 — end-to-end fulfillment

- [ ] Create a live-mode paid booking event or a verified Payment Link flow.
- [ ] Test success, declined, abandoned, duplicate, refunded, cancelled,
      rescheduled, no-show, and provider-unavailable states.
- [ ] Confirm a successful payment produces one appointment and one internal
      delivery record.
- [ ] Confirm no booking is possible without payment unless an explicit authorised
      coupon or manual exception is used.
- [ ] Confirm accessibility, mobile reflow, keyboard flow, receipts, time zones,
      calendar conflicts, and customer support.

### P1 — measurement without dark patterns

- [ ] Measure assessment completion separately from paid-interest clicks.
- [ ] Measure checkout start, payment success, booking completion, attendance,
      refund, and delivery effort as separate events.
- [ ] Do not use scary results, urgency, countdowns, or hidden limitations to
      increase conversion.
- [ ] Conduct representative comprehension and willingness-to-pay interviews
      under an approved research/data process.

## Initial commercial hypotheses to test

These are hypotheses, not prices or promises.

1. A fixed-duration consultant review is easier to understand and fulfill than a
   paid evidence-pack download.
2. The strongest buyer value is confidence in scope, evidence quality, and next
   actions, not a synthetic compliance score.
3. A free question-and-indicator layer increases trust and qualifies the paid
   conversation without giving away the consultant's contextual work.
4. Organisation reviews should be quoted only after system count, jurisdictions,
   evidence condition, attendees, and expected deliverables are known.
5. The paid offer will fail if the free result is confusing; conversion cannot be
   used as a substitute for usability and comprehension evidence.

## Acceptance criteria for launch

The payment gate is launchable only when a representative user can:

1. understand what remains free;
2. understand exactly what the paid service includes and excludes;
3. see the named provider, consultant, price, duration, cancellation/refund, and
   privacy terms before committing;
4. pay and book once with visible success state;
5. recover from decline, abandonment, scheduling conflict, cancellation, and
   refund;
6. receive the promised service and artifact within the stated time;
7. obtain support without exposing source code or confidential evidence through
   an unapproved channel.

Until these are demonstrated, `PAYMENT_GATE: NOT_ACTIVE` and
`CONSULTANT_BOOKING: NOT_AVAILABLE` are the only supportable public states.
