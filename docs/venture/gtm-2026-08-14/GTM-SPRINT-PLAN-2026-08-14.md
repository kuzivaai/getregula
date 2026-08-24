# Regula go-to-market sprint plan

**Date:** 2026-08-14
**Status:** ACTIVE CANONICAL PLAN. Re-planned at every sprint review. Version 3.
Version 3 records the owner's 19 August 2026 distribution directive, the
verified 2.0.0 release on 24 August, and the replacement of the older outreach
and evidence gates. Older sections remain where they preserve the audit trail;
section 11 states the current operating system where an older statement differs.

## 0-bis. Strategy baseline (adopted 14 Aug 2026 from the Sprint 1 dossier,
after verification)

- **Baseline is option (c):** a credible open-source tool with no commercial
  layer. This is the floor the venture must beat, and it is an acceptable
  outcome, not a failure state.
- **Gated upside is option (a):** a solo consultancy using the free tool as
  its credibility and inbound wedge. It activates only on the evidence
  triple below.
- **Not pursued:** a volume product business (option b) against a funded
  competitor, a free official checker, and an unproven willingness to pay;
  and an authorised-representative business (Prighter acquires that customer
  at near-zero marginal cost by upselling its existing Article 27 base;
  verified). Representative need becomes a REFERRAL output, never a Regula
  service. Overturning observation recorded: a wave of non-Prighter non-EU
  GPAI providers wanting a code-first representative would reopen this.
- **Current commercial decision rule (owner directive, 19 Aug):** (1) at least
  5 qualified target-segment conversations, with source recorded; (2) at least
  3 concrete price decisions, accepted or rejected, with reason; (3) a
  privacy-preserving signal of repeated tool use. Unsolicited qualified inbound
  is reported separately as stronger product-led evidence, but is no longer the
  only admissible conversation source. These are management rules, not claimed
  statistically optimal thresholds.
- **Evidence to stop entirely (all three):** near-zero real usage for one to
  two quarters after the full distribution push; a funded player ships deep
  code scanning; zero inbound willingness-to-pay. Then convert to (c)
  permanently or archive.

Reconciliation record: the Sprint 1 dossier was adopted EXCEPT where it
failed verification. Corrections applied: (1) its Article 50(2) marking date
of 2 February 2027 is wrong; `scripts/omnibus.py` (2 December 2026) is
correct and confirmed by post-Omnibus secondary sources; (2) its Regula
pattern count (~398-409) is wrong; canonical is 419 tier regexes
(`data/site_facts.json`); (3) its "Legalithm pricing unverified" flag is
stale; €0/€17/€47/€119 with a 40% founding discount was fetched directly on
14 Aug; (4) its competitive matrix marked Regula's MCP server and GitHub
Action "planned/partial"; both exist with tests (`scripts/mcp_server.py`,
`action.yml`); (5) its suggested CLI interest beacon and the copy line
"never sends your code anywhere" were rejected: the beacon would break the
offline wedge, and the copy matches the repo's prohibited-claim class
"universal network" (`scripts/public_surface_inventory.py`).
**Owner directive:** On 14 August 2026 the owner directed work on distribution,
marketing, service, post-sales support and acquisition, in that sequence, with
full (never partial) execution, targeting SMEs both inside and outside the EU
that cannot afford incumbent governance platforms.

The dated owner directive of 19 August 2026 supersedes the older verdicts only
where it says so. Safe implementation, release, owned distribution, eligible
registry/editorial submission, compliant corporate B2B outreach and anonymous
analytics are now authorised. Payment, booking, transmitting personal-data
forms, customer source upload, legal advice and compliance certification remain
hard stops. The machine-readable controlling record is
`data/distribution_execution_policy.json`.

## 0-ter. Second-pass verification record (14 Aug 2026, later same day)

This plan was re-verified against primary sources and against the tree. Nine of
twelve externally checkable claims held exactly. The items below did not, and
they are corrected here rather than left to be quoted forward. Two further
items are not wrong but overstate independence.

**Corrections that change what this plan says:**

1. **`Paid Interest` does not exist in any shipped file.** `grep -rn "Paid
   Interest" site/` returns nothing; the string's only occurrence in the whole
   repository is this plan. Sprint 1 item 2 and the section 8 metrics row both
   describe instrumentation that commit `e0e0709` removed by owner direction,
   replacing it with a `Contact Click` mailto route on pricing.html. The owner
   action "add Paid Interest as a goal in Plausible" would create a goal that
   nothing fires. **Superseded by:** add `Contact Click` and `CTA Click`.
2. **Article 54 has zero coverage in this repository.** The plan cites it twice
   for the GPAI authorised-representative duty. The provision exists in
   Regulation (EU) 2024/1689, but `grep -rn "Article 54" scripts/` returns
   nothing, the only file in the repo containing the string is this plan, and
   the repo pins its 2 August 2025 GPAI date to **Article 53**
   (`explain_articles.py`, `timeline.py`, `gpai_check.py`). Consequence: the
   standing sprint-start instruction to "re-verify regulatory dates against
   `scripts/omnibus.py`" **structurally cannot cover the GPAI line**, because
   that module defines no GPAI date at all. Any Sprint 2 content built on
   Article 54 needs a primary-source check first, not a repo check.
3. **`data/site_facts.json` carries no jurisdictions count.** Its `counts` keys
   are commands, patterns, frameworks, languages, tests. The 419 tier-regex
   figure is confirmed exactly; a jurisdiction figure cited as canonical from
   that file would be unsourced.
4. **Legalithm:** see the corrected side-finding in the channel register. The
   "no code scanning" characterisation is publicly refutable and the "free
   until ~April 2028" date is not published anywhere. Positioning must say
   *source-code* pattern scanning, which remains true and checkable.
5. **Console.dev gating was recorded backwards.** The free editorial review is
   open to Regula at v1.9.0; only the Betas listing excludes stable releases.
   The register's advice to skip the review and buy sponsorship rested on the
   misread and is corrected there.
6. **Sprint 1's scoping flow is mostly absent, and Sprint 2 depends on it.**
   Of the eight facts item 6 specifies, one is fully present (Annex III), one
   is half present (role: provider and deployer exist, importer and
   distributor do not), one is collapsed into a single question (EU users),
   and five are absent as resolvable facts: Article 2(1)(c) output-used-in-the-
   Union, establishment, GPAI status, the open-source exemption, and
   representative need. Sprint 2's content backlog is written as though the
   flow already answers them.

**Not wrong, but overstated as independent evidence:**

- **Prighter's A13 and A14 are one price card, not two markets.** The identical
  ladder (€79/€39/€189/€440 per month) is charged across EU GDPR, UK GDPR,
  KVKK, Swiss, DSA, Data Act and EU AI Act GPAI. Citing the GDPR figure and the
  AI Act figure as two observations double-counts one data point. The ladder is
  also non-monotonic: "Growth" (€39/mo) is cheaper than "Small" (€79/mo).
- **The Commission's 5-15% quote is verified, its page numbers are not.** The
  exact phrase appears in SWD(2021) 84 final, but EUR-Lex returned an empty
  body on three attempts and the text was read from an FLI-hosted mirror of the
  Commission PDF. Cite it without the "pp. 68-69" range until someone opens the
  EUR-Lex PDF by hand. The same page adds that precise cost estimation "is not
  possible ... since the legislator has not yet decided the list of high-risk
  applications", which supports this document's own honest headline.

**Upgraded:** Luiza's Newsletter "99,000+" is now [VERIFIED-direct]; the note
that the site blocks fetching is itself refuted (HTTP 200 with a normal user
agent). Oliver Patel's "over 8,500" verified direct, canonical URL is
`oliverpatel.substack.com`, and the cadence is fortnightly, not weekly.

**Scope correction, 24 Aug:** the three canonical GTM documents in this
directory are tracked. The untracked `marketing/` directory remains outside
this plan and is neither evidence nor an authorised draft queue.

## 0. Superseded verdicts and current gates

The August 6 block below is historical, not current authority. The 19 August
owner directive authorises controlled distribution and supersedes
`EXTERNAL_CONTACT: NOT_AUTHORISED`. It does not validate demand or activate a
paid service.

```text
OWNED_CHANNEL_DISTRIBUTION: AUTHORISED
PUBLIC_DIRECTORY_AND_REGISTRY_SUBMISSION: AUTHORISED_WITH_PLATFORM_CHECKS
CORPORATE_B2B_OUTREACH: AUTHORISED_WITH_COMPLIANCE_POLICY
EDITORIAL_SUBMISSIONS: AUTHORISED_WITH_EVIDENCE_POLICY
MODERATED_USER_RESEARCH: AUTHORISED_AFTER_RESEARCH_PRIVACY_GATE
ANONYMOUS_PRODUCT_ANALYTICS: AUTHORISED
WILLINGNESS_TO_PAY: UNVALIDATED
PAYMENT_GATE: NOT_ACTIVE
CONSULTANT_BOOKING: NOT_AVAILABLE
PERSONAL_DATA_WEB_FORM: DISABLED_UNTIL_PRIVACY_GATE
CUSTOMER_SOURCE_UPLOAD: NOT_ACCEPTED
```

What this means operationally for GTM work:

| Activity | Status | Why |
|---|---|---|
| Publishing to the public site, PyPI, GitHub | PERMITTED | Already-live public surfaces; no personal data, no outreach |
| Anonymous analytics events (Plausible) | PERMITTED | Already instrumented; no personal data collected |
| Building the free scoping flow | PERMITTED by owner directive of 2026-08-14 | Product change on the free layer; recorded here as the owner's decision |
| Email waitlist / newsletter capture | GATED | Collects personal data; controller, lawful basis, privacy notice unresolved (owner fields 1-12) |
| Editorial submissions | AUTHORISED WITH EVIDENCE POLICY | One tailored factual submission; no mass or fear-based pitching |
| Corporate B2B outreach | AUTHORISED WITH COMPLIANCE POLICY | Only after the private register, suppression, privacy and recipient controls in section 15 exist |
| User interviews, discovery calls | GATED | Authorised only after the research privacy gate; current controller, storage and retention facts are unresolved |
| Payment, booking, selling | GATED | Every P0 item in docs/commercial/PAID-CONSULTANT-GATE-2026-08-13.md |
| Publishing prices as settled | GATED | Same record: price must not be published as settled until measured |

The current honest demand tests are (a) task-led public content, (b) anonymous
funnel events under the versioned allowlist, (c) repository/package/registry
discovery, (d) editorial referral, and (e) controlled corporate B2B outreach.
Stars, traffic and contact clicks are interest signals, not willingness to pay.
An email waitlist remains unavailable until the transmitting-form privacy gate.

## 1. Sprint machinery (the dynamic, evolving part)

- **Cadence:** one-week sprints. Solo founder plus agent sessions.
- **Every sprint starts with:** (1) re-read this section 0; (2) re-verify
  regulatory dates against `scripts/omnibus.py` and one amendment search;
  (3) review last sprint's metrics against its exit criteria.
- **Every sprint ends with:** review (evidence vs exit criteria), retro (one
  process change max), re-plan (backlog re-ranked; this file updated in
  place, never forked).
- **Definition of done, globally:** verified with the project's own gates
  (pytest suite, claim auditor, site integrity, locale parity check, browser
  check at 320 px) and recorded with the command and result. "Looks done" is
  not done.
- **Re-planning triggers (standing):** a regulatory date moves; a verdict
  field changes; a metric crosses a threshold in section 8; a competitor
  ships an SME-priced scoping tool; any P0/P1 finding on the live site.
- **Anti-bias controls:** every sprint review answers "what evidence this
  sprint argued AGAINST continuing?" before "what progressed?". No metric may
  be reported without its denominator. No favourable end of a range may be
  quoted without the range.

## 2. Sprint 0 (14 Aug 2026, in progress): evidence base

**Goal:** a verified market-sizing model, earlyvangelist definition, channel
register and this plan, so every later sprint aims at a named audience with
honest numbers.

Backlog:
1. Verify TAM/SAM anchor statistics against primary sources. [DONE 14 Aug;
   two most load-bearing figures re-checked directly]
2. Verify representative-market pricing anchors on vendor sites. [DONE 14 Aug;
   Prighter re-checked directly]
3. Influencer/newsletter channel register with sourced audience sizes.
   [DONE 14 Aug: CHANNEL-REGISTER-2026-08-14.md]
4. MARKET-SIZING-2026-08-14.md with TAM/SAM/SOM as scenario ranges, every
   figure tagged VERIFIED / SECONDARY / REASONED. [DONE 14 Aug]
5. Earlyvangelist profiles with selection criteria and disqualifiers.
   [DONE 14 Aug, in the market-sizing doc]
6. This plan. [done, this file]

Sprint 0 finding that re-ranks later work: the section 9 competitor trigger
has PARTIALLY FIRED already. Legalithm (free-launch, €17-119/mo launch
prices, CLI/MCP/GitHub Action, declaration-driven) and the Commission's own
free beta Compliance Checker both target the scoping question. Consequence:
Sprint 2 gains a positioning task, and no copy may imply the scoping
questionnaire alone is unique. What the sweep found nothing else doing under
€5k/yr: code-pattern scanning combined with an epistemic kernel that refuses
to convert unknowns into scores, fully offline/local, open source,
multi-jurisdiction. Positioning stands on that combination, stated as a
combination, never as "the only".

**Exit criteria:** all three documents exist; every number in them carries a
source or an explicit REASONED tag; the "what did I miss" pass is recorded.

## 3. Sprint 1: Distribution (the free product is the distribution asset)

**Goal (revised per the adopted strategy):** lead with the one thing no
competitor does (deep offline code scanning behind an honest kernel), make
the existing distribution surfaces visible, and instrument intent without
personal data. The scoping flow moves AFTER the wedge, framed as "what the
code cannot tell you", because the scoping question alone is what the EC and
FLI give away free.

Revised order and status:
1. [DONE 14 Aug] README headline repositioned to the offline code-native
   wedge with guard-safe language (no prohibited-claim classes; telemetry
   claim matches the consent-gated module).
2. ~~[DONE 14 Aug] Paid-interest instrumentation on pricing.html: two honest
   "Register anonymous interest" controls plus FAQ-open events. Owner action:
   add "Paid Interest" and "Pricing FAQ Open" as goals in Plausible.~~
   **SUPERSEDED, see section 0-ter item 1.** Commit `e0e0709` removed those
   controls by owner direction. `Paid Interest` fires nowhere in `site/`. What
   the page actually carries now is a `mailto:support@getregula.com` button
   with `Contact Click` (props `pricing-consultant` / `pricing-organisation`)
   and a delegated `Pricing FAQ Open`. Owner action is therefore: add
   **`Contact Click`** and **`CTA Click`** as Plausible goals, not Paid
   Interest.
3. [DONE 14 Aug] PyPI keywords extended (static-analysis, offline,
   mcp-server, github-action, sarif).
4. [PREPARED; owner step] GitHub Marketplace listing: `action.yml` is
   already Marketplace-grade (branding, fail-closed manifest gate). Owner
   creates a release and ticks "Publish this Action to the GitHub
   Marketplace".
5. [PREPARED; owner confirmation] MCP registry listings: `mcp-server.json`
   exists and README carries `mcp-name: io.github.kuzivaai/regula`. Submit
   to mcp.so and Glama once the owner confirms (outward-facing publication).
6. [NEXT SESSION, dedicated change] Jurisdiction-agnostic scoping flow, as
   originally specified below, positioned after the scan. Kernel work across
   CLI/browser/three locales with conformance vectors deserves its own
   verified change, not a shared one.

Original backlog (retained for the scoping-flow specification):
1. **Jurisdiction-agnostic scoping flow** in the existing kernel, as
   declarative data, per the 13 Aug research dossier section 4: establishment,
   EU users/recipients, output used in the Union (Article 2(1)(c)), role
   (provider/deployer/importer/distributor), Annex III mapping, GPAI status
   and open-source exemption, EU establishment, therefore representative need
   (Articles 22/54). Tagged-union output preserved: `indication` /
   `insufficient_information` / `outside_scope_candidate` per jurisdiction.
   Unknown never becomes no; no scores, tiers or percentages.
2. All three locales (EN, DE, PT-BR) in the same change; conformance vectors
   and mutation tests extended; full verification chain green.
3. Browser assess flow gains the same questions from the generated decision
   model; verified at 320 px, keyboard, and with the all-Not-sure journey
   returning explicitly-listed unresolved facts.
4. **Paid-interest instrumentation:** anonymous Plausible events on
   pricing.html (`Paid Interest` with plan prop; `Pricing FAQ Open`), kept
   separate from assessment-completion events per the gate record's P1.
5. **PyPI and GitHub surface:** review classifiers/keywords/description on
   PyPI `regula-ai`; GitHub topics, About, README top section rewritten around
   the scoping question ("does the EU AI Act apply to us?") rather than the
   feature list; good-first-issue labels curated.
6. `llms.txt` deprioritised (inherited finding: majority receive zero bot
   requests; not re-verified, and not worth re-verifying yet).

**Exit criteria:** a synthetic non-EU test business completes the flow and
receives `outside_scope_candidate` or `insufficient_information` listing
exactly which EU-user facts are unresolved; suite green; locale parity greps
clean; Paid Interest events visible in Plausible from a manual test.

**Explicitly out:** any outreach, any email capture, any payment control.

## 4. Sprint 2: Marketing (GEO-aligned honest content)

**Goal:** the scoping questions our audience actually asks are answered on
getregula.com with cited, statistic-rich, quotation-backed pages that
generative engines and search can retrieve, in all three locales.

Evidence basis: Aggarwal et al., "GEO: Generative Engine Optimization"
(KDD 2024, arXiv:2311.09735) found Cite Sources, Quotation Addition and
Statistics Addition improved source visibility 30-40% relative on
Position-Adjusted Word Count; keyword stuffing scored below baseline. This
matches the project's honesty rules, which is why it is the content strategy.

Backlog:
1. Content architecture: one page per real scoping question.
   - "Does the EU AI Act apply to a company outside the EU?" (Article 2(1)(c),
     the SME fine cap in Article 99(6), the representative duty in
     Articles 22/54, all cited to the Act.)
   - "EU AI Act Article 50 transparency: what applies since 2 August 2026"
     (dates from `scripts/omnibus.py`; machine-readable marking grace to
     2 December 2026).
   - "Do I need an EU authorised representative for AI?" (Article 22 high-risk
     from 2 December 2027, Article 54 GPAI live since 2 August 2025;
     comparison table to the GDPR Article 27 market with sourced prices.)
   - "High-risk or not: Annex III scoping for small teams" (Commission 5-15%
     estimate vs appliedAI 18% / 40%-unclear findings, both cited; the
     40%-unclear band presented as exactly what `insufficient_information`
     is for).
   - DE and PT-BR parity in the same sprint, per the locale rule.
2. Every page passes `claim_auditor.py`; every date sourced from
   `omnibus.py`-derived data; British English; no em dashes; WCAG 2.2 AA
   checks as per docs/accessibility/.
3. Sample output page updated to show the scoping journey, not score-like
   output.
4. GSC baseline recorded the day pages ship (gsc tooling exists:
   `scripts/gsc_fetch.py`). BLOCKED 14 Aug: the local OAuth token returns
   invalid_grant and the GSC MCP account lacks getregula.com; owner action:
   re-authenticate before Sprint 2 ships.
4b. Competitor positioning page/section: honest comparison against the
   Commission checker (free, official, beta, questionnaire-only), Legalithm
   (free-launch, declaration-driven CLI) and FLI's checker, on the
   combination named in Sprint 0; every comparative claim sourced and dated,
   re-verified before publish.
5. **Channel enablement pack, held for authorisation:** one-paragraph tool
   description, honest claims sheet, screenshots, suggested angles per
   channel-register entry. Produced now, SENT ONLY after the owner signs
   field 14 (external contact).

**Exit criteria:** pages live in three locales, claim auditor 0 unsourced,
GSC baseline snapshot stored, enablement pack drafted and explicitly marked
NOT SENT.

## 5. Sprint 3: Service (make the paid layer fulfillable, without activating it)

**Goal:** every P0 item in PAID-CONSULTANT-GATE-2026-08-13.md is either
evidenced or reduced to a single named owner decision, so activation becomes a
decision, not a project.

Backlog:
1. Draft artefacts (agent-preparable): service specification (duration,
   preparation, deliverable, turnaround, rescheduling, cancellation, refund,
   no-show, escalation); pre-contract information sheet per the Consumer
   Contracts Regulations 2013; privacy notice draft; minimised intake form
   (source upload prohibited by default); complaint route; receipt/invoice
   template.
2. **Claims-and-limitations sheet** shipped with any consultant enablement:
   never claims to determine legal compliance; publishes scoped efficacy
   honestly (frozen figures stay frozen and scoped per the claim-freeze
   record); says "indicates possible relevance", never "certifies".
3. Consultant enablement artefacts: jurisdiction cheat sheet (dates from
   omnibus.py; triggers; representative rules); scoping playbook; objection
   handling ("isn't this just for big tech?" answered with Article 2(1)(c)
   and Article 99(6), cited); referral triggers to lawyers and notified
   bodies.
4. Owner decision register (blockers only the owner can clear), each with the
   evidence the owner needs to decide: named legal seller; named consultant
   and credentials (research dossier recommends IAPP AIGP ~US$799 exam, then
   ISO/IEC 42001 lead implementer; verify prices at purchase time);
   professional indemnity insurance; price/currency/tax with accountant;
   customer type (B2B vs consumer) and cancellation treatment.
5. Technical route decision prepared (not built): hosted paid scheduling
   (Calendly + Stripe) vs Payment Link + validated fulfilment, per the gate
   record's analysis. Build starts only after items 1-4 clear.
6. **Representative-service prerequisite file:** the Article 22/54 line
   requires an entity established in the Union (a UK entity cannot serve) and
   PI cover; recorded as a 2027-facing decision with the Dec 2027 Annex III
   date as the demand driver, GPAI providers the only live segment now.

**Exit criteria:** P0 checklist re-scored with every item either DONE-with-
evidence or OWNER-DECISION-named; zero items in "unexamined".

## 6. Sprint 4: Post-sales support (design fulfilment before selling)

**Goal:** if a first customer paid tomorrow, delivery would be boringly
reliable.

Backlog:
1. Fulfilment runbook: payment-verified booking, pre-session intake, session
   delivery, written action brief template (owners, evidence gaps, referral
   questions), follow-up boundary.
2. docs/SUPPORT_SLA.md reviewed against the actual proposed service; support
   channel defined (email route, response targets a solo operator can keep).
3. Full failure-path design: decline, abandon, duplicate, refund,
   cancellation, rescheduling, no-show, consultant-unavailable; every state
   has a designed screen/message per the project's no-dead-ends UX rule.
4. Feedback capture design (gated where it collects personal data): what is
   asked, where stored, retention; ships only with the privacy approvals.
5. Retainer/retention design: what ongoing monitoring would honestly contain
   (regulatory-date changes are already machine-tracked in this repo; that is
   the retainer's raw material), priced later, never auto-renewed silently.

**Exit criteria:** runbook walkthrough executed end-to-end as a drill with a
synthetic customer; every failure path has a designed state; gaps filed.

## 7. Sprint 5: Acquisition (funnel, pilots, and the STOP-revisit package)

**Goal:** a measured funnel from content to free flow to interest signal, and
an evidence package that lets the owner honestly revisit VENTURE STOP.

Backlog:
1. Funnel instrumentation review: content page -> assess start -> assess
   complete -> pricing view -> Paid Interest event; weekly readout with
   denominators.
2. Partnership referral channels (accountants, accelerators, dev agencies,
   privacy consultancies): register built from public information; contact
   remains gated on field 14.
3. Pilot design (NOT approved to run): recruitment criteria mirroring the
   earlyvangelist profile; consent and data handling from the Sprint 3
   privacy work; success measures separating comprehension from willingness
   to pay.
4. **STOP-revisit evidence package**, assembled when thresholds in section 8
   are met: unsolicited paid-interest count, scoping-flow usage trend,
   completed-interview findings (if authorised), one tested
   payment-to-fulfilment path. Presented neutrally with the counter-evidence
   included.

**Exit criteria:** four consecutive weekly funnel readouts exist; the package
template exists with its evidence slots named.

## 8. Metrics and thresholds (initial values are hypotheses, owner-settable)

Baseline context (from project records): assess analytics were dead before
10 Jul 2026; instrumentation now live; **PyPI downloads roughly 25 per week
excluding mirrors** (measured 2026-08-14 against the pypistats daily series and
recorded in ledger entry N109); zero third-party visibility as of the May 2026
market scan.

> **Correction, 2026-08-17.** This line previously read "PyPI downloads
> 1,282-2,177/week without mirrors (Jul-Aug 2026, per the corrected claim-freeze
> record)". That figure is the one ledger N109 **retracted on the same date this
> document was written**: `data/metrics/pypi_weekly.json` had recorded a
> whole-period cumulative total under a `"period": "last_7_days"` label every
> Monday from 2026-04-20, and the final row overstated the quantity its label
> names by **88.4 times** (2,211 recorded against an actual 7-day figure of 25).
> The attribution was the worse half: the corrected claim-freeze record says the
> opposite of what this line cited it for. Corrected here rather than deleted,
> because a document that quietly loses a wrong number teaches nothing.
>
> **Site traffic, added because this section had none and a threshold needs it.**
> Measured 2026-08-17 from the Plausible export taken 2026-08-14: **188 visitors
> over the 91 days 2026-05-15 to 2026-08-13**, a mean of 2.07 a day, median 2,
> and 15 days with no visitors at all. Over the same window **one** visitor
> started the assessment and **one** completed it. Every "initial threshold" in
> the table below should be read against those numbers, and
> `docs/venture/research-2026-08/b-stickiness-and-sample-size.md` shows that at
> this volume a full year of split-testing cannot detect a change smaller than
> about 1.7-fold, so none of these metrics can support a before-and-after claim.

| Metric | Instrument | Initial threshold (hypothesis) | Action when crossed |
|---|---|---|---|
| Assessment completions/week | Plausible `Assessment Complete` | trend, no target yet: 4-week baseline first | After baseline, set target at review |
| Non-EU jurisdiction usage share | jurisdiction prop | observed share reported weekly | Informs locale/content priority |
| ~~Paid Interest events/week~~ Contact Click events/week | Plausible `Contact Click` (the Paid Interest control was removed; see 0-ter item 1) | any nonzero unsolicited = record it | Feeds STOP-revisit package |
| Content -> assess click-through | Plausible goals | 4-week baseline first | Re-rank content backlog |
| GSC impressions on scoping queries | gsc_fetch.py | baseline day 0, review at +28 days | Re-rank queries |
| Unsolicited contact asking to pay | inbound only (no outreach) | each one logged verbatim | Strongest single STOP-revisit input |

Rule: no threshold is evidence of demand by itself; conversion must never be
optimised with urgency, fear or hidden limitations (gate record P1).

## 9. What would change this plan

- The Annex III date (2 Dec 2027) or Article 50 grace (2 Dec 2026) moves:
  re-verify everything pegged to them (standing sprint-start check).
- A verdict field changes: re-scope the affected sprints immediately.
- Evidence that the free scoping wedge is not used after Sprints 1-2 have
  been live for four weeks: revisit positioning before building more.
- A funded competitor ships SME-priced scoping: re-run the competitor pass
  and reposition on what remains distinct (never claim uniqueness without
  that pass).

## 10. Honest counterargument (recorded so it is not lost)

The strongest case against this plan: willingness to pay is UNVALIDATED; the
most recent efficacy diagnostic on the detection layer failed (N60: recall
0/40 on constructed adversarial families; diagnostic, not external accuracy,
but not evidence in favour either); the scoping question may be adequately
answered free by law-firm explainers and the Commission's own materials; and
the paid conversion of "confused visitor" into "customer" is exactly the
pattern the project's own rules prohibit exploiting. This plan proceeds
because the free layer has independent value, the costs are near zero, and
every paid step is gated on evidence, but the null hypothesis (no viable
venture here) remains live until the section 7 package says otherwise.

## 11. Current distribution operating system (version 3, 24 Aug 2026)

This section is controlling where the earlier sprint narrative differs. It is
an execution system, not evidence that distribution or demand has succeeded.

### 11.1 Verified launch state

| Surface | Evidence-backed state | Next action |
|---|---|---|
| Source | Current deployed `main` is `15b559e7e1b165e5862c426c8d4fe9574b66822e`; the immutable 2.0.0 release identity remains `ef5309a9f6485662192c6648d2deb17705edacf0` | Do not conflate the current website commit with the released package commit |
| Production | Founder-first homepage and all three locales live; desktop, 640, 390, 320, keyboard, no-JS, error, success, reset, scanner recovery and 404 paths mechanically verified | Human comprehension remains untested |
| PyPI | `regula-ai` 2.0.0 published 24 Aug; wheel and sdist hashes verified; clean wheel install passes 6/6 self-tests | Monitor install and support evidence, not download vanity alone |
| Provenance | PyPI Integrity API binds both artefact hashes to `kuzivaai/getregula`, `release.yml`, environment `pypi` | Never describe provenance as proof of safety |
| GitHub Release | `v2.0.0`, non-draft/non-prerelease, wheel, sdist and `SHA256SUMS`; floating `v2` points at the release commit and `v1` is unchanged | Use `v2` in new major-version Action examples only after compatibility review |
| Marketplace | Existing Regula listing is live; the accessible listing does not expose a version string that independently proves 2.0.0 selection | Human Marketplace UI confirmation may still be required |
| MCP Registry | Live official entry remains 1.9.0; 2.0.0 validates, but publication was rejected because the stored Registry JWT expired | Owner must complete GitHub device authentication, then re-run `mcp-publisher publish server.json` and verify `/v0.1/servers` |
| Analytics | Privacy hotfix live and production-verified 24 Aug: exactly Pageview, Qualifier Start and Qualifier Complete; path-only URLs, finite campaign properties, no automatic form event, console 0/0 | Obtain a fresh exact-window export; do not infer conversion from the stale pre-contract baseline |
| Search | Sitemap and robots return 200; canonical/hreflang checks exist | Search Console credentials/property remain unavailable, so no fresh index baseline exists |

### 11.2 Funnel and decision rules

The measurable sequence is: qualified discovery -> homepage comprehension ->
qualifier start -> qualifier completion -> assessment or scanner continuation
-> installation/integration intent -> useful result -> repeated use -> contact
intent -> qualified conversation -> concrete proposal -> accepted or rejected
price -> delivered engagement -> repeat/referral.

These stages must be reported separately for product-led inbound, editorial,
repository/package/registry discovery, community referral and direct outreach.
The website can measure only aggregate early-stage events. Conversation,
proposal, price and delivery evidence belong in a private commercial register.
No aggregate page event is upgraded into a later-stage outcome.

The management decision rule is:

1. five qualified target-segment conversations, each with source;
2. three concrete price decisions, accepted or rejected, with reason;
3. one privacy-preserving repeated-use signal;
4. unsolicited qualified inbound reported separately as stronger evidence.

## 12. Audience and message matrix

| Segment and real task | First message | Primary asset/action | Evidence boundary | Measurement | Stop condition |
|---|---|---|---|---|---|
| Technical founder or AI-product owner: decide whether investigation is justified | Answer five plain questions to see what your facts point at and what remains unresolved | Homepage qualifier -> fuller assessment or local scanner | Five answers cannot determine applicability, risk class, obligations or compliance | Qualifier Start/Complete; assessment or scanner continuation; later comprehension tasks | Stop changing copy from analytics alone; correct only demonstrated task/comprehension failures |
| Developer or platform engineer: find code evidence and integrate a repeatable check | Scan locally for review indicators; unresolved deployment facts remain separate | PyPI/CLI, Action, MCP, SARIF, reproducible sample | Pattern matching has false positives and false negatives; no scan proves compliance or low risk | Registry/repository clicks, Scanner Complete, Install Command Copy, Action/MCP intent | Stop a channel if it produces curiosity traffic without useful-result evidence |
| Governance, audit or advisory professional: organise traceable technical observations | Use reviewer-completable evidence and explicit unresolved facts, not an automated opinion | Evidence pack, fact store, framework mapping, model card and Annex IV scaffold | Scaffolds require human completion and do not establish legal sufficiency | Sample Report View; moderated task evidence after privacy gate | Stop if the artefact requires unsupported assurance or creates more review work than it saves |
| SME decision-maker: decide whether to allocate further work | Establish whether more investigation is warranted before buying anything | Founder qualifier, sample written output, service-boundary page | Human service is a hypothesis; seller, consultant, insurance and terms are unresolved; no booking/payment | Pricing View, FAQ, Contact Intent; later qualified conversations and price decisions | Do not activate service, booking or payment until every P0 is evidenced |

## 13. Distribution asset register

| Asset | Segment | State | Truth/UX check | Measurement | Owner effort / cost | Follow-up / stop |
|---|---|---|---|---|---|---|
| Founder qualifier, EN/DE/PT-BR | Founder, SME | LIVE | Browser mechanics and production event boundary pass; human comprehension absent | Qualifier Start/Complete | Weekly 30-minute review; GBP 0 | Formative research only after the separate research privacy gate |
| Browser assessment/scanner | Founder, developer | LIVE | Success, reset and induced-error recovery pass at 320px | Assessment and Scanner events | Weekly reliability review; GBP 0 | Fix demonstrated errors; do not infer legal accuracy from completion |
| PyPI 2.0.0 | Developer | LIVE VERIFIED | Hashes, provenance, clean install and self-test pass | PyPI weekly exact-window downloads, excluding mirrors where supported | 30 minutes/week; GBP 0 | Investigate support/install failure, not rank alone |
| GitHub repository and Action | Developer | LIVE | Action checks pass; Marketplace listing exists | GitHub referral, Action intent, clones/releases where available | 1 hour/release; GBP 0 | Dedicated Action repo only if monorepo causes support or eligibility failure |
| Official MCP Registry | Developer | 1.9.0 LIVE; 2.0.0 BLOCKED | 2.0.0 manifest live-valid; metadata immutable per version | Registry referral after update | One authenticated owner action; GBP 0 | Do not repeatedly publish metadata-only versions |
| Reproducible sample | Developer, governance | LIVE INSIDE MONOREPO | Real output and limitations; no dedicated minimal repo | Sample view and install intent | Up to 4 hours; GBP 0 | Build a separate repo only if the existing journey is a demonstrated blocker |
| Evidence-pack sample | Governance | LIVE | Reviewer-completable, not an opinion | Sample Report View plus moderated task evidence | 3 hours research prep | Stop assurance-style positioning immediately |
| Pricing/service boundary | SME | LIVE, SERVICE DISABLED | No checkout/booking; prices must be labelled hypotheses | Pricing View/FAQ/Contact Intent | 30 minutes/week | No paid activation before P0 gate |
| Local enquiry preparer | Founder, SME | NOT BUILT | Must submit nothing, keep answers out of URL and warn against sensitive material | Reserved events do not fire | Estimate after analytics deploy | Do not substitute it for a privacy-gated secure form |
| Editorial submission pack | Developer/governance | PREPARED IN PLAN, NOT SENT | One tailored message per channel; no unique/replacement/legal-risk claim | Allowlisted campaign plus register | 60-90 minutes/channel; GBP 0 | One follow-up maximum |
| Corporate outreach queue | Incorporated AI vendors | NOT CREATED | Private register and suppression controls required | Delivered/reply/conversation, never open rate | Manual review; max 10 new/day | Stop segment at 30 delivered without qualified reply |

## 14. Analytics, attribution and baseline

`data/analytics_event_spec.json` is the only current custom-event contract.
`site/assets/analytics.js` rejects unregistered custom event names, unknown
custom event properties and arbitrary campaign text; it retains only
allowlisted source, medium and campaign values for the browser session and
creates no identifier. Duplicate logical events are suppressed within a page
lifecycle. The contract forbids answers, code, repository URL, organisation,
email, free text, regulatory result and personal/tracking identifiers. That
custom-event boundary did not govern Plausible's own page URL or automatic
form event: production inspection on 24 August found both paths active. PR 62
strips the whole query string before every Plausible request and disables
automatic form-submission tracking. A second production capture after
deployment emitted exactly Pageview, Qualifier Start and Qualifier Complete,
all with path-only URLs and finite campaign properties; the automatic form
event was absent. This is evidence about the captured journey, not a guarantee
about future vendor or implementation changes.

`data/metrics/distribution_funnel_baseline_2026-08-14.json` is deliberately
marked stale for the contract: its exact 91-day window ends 13 August. It
records 188 as a **sum of daily visitor counts**, 217 pageviews and 192 visits;
it is not a period-unique visitor count. Because the current event names did
not yet exist, their baseline values are null rather than invented zeros.
`scripts/distribution_funnel.py` produces exact-window reports from a Plausible
export and names every aggregate denominator. A fresh export is still required
after deployment. No credential is present in this environment to obtain it.

Campaign URLs may use only the enumerated values in the event contract. The
first campaign is `release-2-0`; editorial and B2B campaigns have distinct
names. Allowlisted source, medium and campaign values are transmitted only as
finite custom properties; all query parameters, including arbitrary UTM
values, must be removed from the reported URL. Plausible's aggregate
referrer/page reporting remains the source for untagged referrals.

## 15. Editorial and corporate outreach controls

### 15.1 Editorial

One submission may be made per independently relevant channel. Each contains:
the audience's task, one factual differentiator, a live artefact, explicit
limits, why the audience would care and one direct request. No uniqueness,
inflated replacement value, fear-based deadline or compliance claim. The
channel register records primary-page verification, route, version, response,
traffic, qualified action, cost, follow-up and stop state.

### 15.2 Private corporate register schema

The schema is public; records are private and must never be committed:

```text
record_id; organisation_legal_name; incorporation_evidence_url;
organisation_type; recipient_role; corporate_email; source_url;
source_observed_at; relevance_observation; corporate_subscriber_basis;
lia_reference; privacy_notice_version; suppression_checked_at;
message_version; sent_at; delivery_state; follow_up_count;
last_follow_up_at; objection_at; suppressed_at; reply_class;
qualified_reason; conversation_at; proposal_at; price_decision;
price_decision_reason; time_minutes; campaign_source
```

The private suppression register retains the exact address needed to prevent
future contact, the objection/suppression timestamp and source. It is checked
before every send. It is not a marketing list and must not be hashed in a way
that makes suppression unreliable. Access is limited to the owner/operator.

Pre-send controls: incorporated organisation verified; no sole trader,
unincorporated partnership, personal address, regulator, political figure or
uncertain classification; data source and relevance recorded; corporate basis
and legitimate-interests assessment complete where personal business-contact
data is used; privacy information linked; identity and contact route present;
clear opt-out; no pixel or hidden open tracking; suppression clean; every
message manually reviewed. Cap 10 new recipients per business day, two
follow-ups, five business days apart. Stop immediately on objection and stop a
segment after 30 delivered first contacts without a qualified response.

Current state: schema and procedure prepared; no private store or eligible
recipient records were found in scope, no configured official sending API was
found, and zero messages have been sent.

## 16. Founder comprehension research protocol

Research is formative, not a conversion survey. Participants attempt, without
coaching, to identify the problem, decide whether to continue, answer all five
questions, explain “Not sure”, explain what Regula observed and did not decide,
distinguish indication from legal classification, find the next action,
identify what remains free, distinguish written assessment from advisory work,
and state whether data leaves the browser/local machine.

Record task completion/failure, time to first useful result, abandonment reason,
confidence calibration, accessibility needs and verbatim comprehension themes.
Do not lead with satisfaction or redesign from isolated style preferences.

Recruitment remains blocked until a named controller, participant information
notice, appropriate consent record, minimised recording fields, private storage
location, access owner, retention/deletion period and withdrawal route are
recorded. No source code, confidential company information or sensitive legal
facts may be solicited. The first round is five likely founders/operators; this
is a formative design rule, not a representative sample claim.

## 17. Paid human-service blueprint (prepared, unavailable)

| Field | Current honest state |
|---|---|
| Provider / legal seller | UNRESOLVED; no seller may be inferred from the project name |
| Customer type | Proposed corporate B2B only; not activated |
| Service | Human-led technical evidence-readiness review of one codebase and one declared product scope |
| Required inputs | Local scan output, non-confidential architecture/context statements and named unresolved facts |
| Prohibited inputs | Customer source upload to Regula, credentials, special-category data, confidential datasets, privileged legal material |
| Preparation / delivery | Hypothesis: bounded preparation, one remote walkthrough, written action brief; duration and capacity unvalidated |
| Written deliverable | Observations, unresolved facts, evidence owners, technical next actions and referral questions; not a legal opinion or certificate |
| Turnaround / support | Hypothesis only; must be reconciled with real operator capacity before sale |
| Exclusions | Legal advice, conformity assessment, certification, regulatory representation, operational-control assurance |
| Referral triggers | Any legal classification, statutory interpretation, notified-body need, representative appointment or material security incident |
| Cancellation / rescheduling / refund / complaints | UNRESOLVED P0 commercial terms |
| Privacy / insurance / tax | Controller, processing record, professional indemnity, seller tax and invoicing facts unresolved |
| Price | GBP 950 fixed-scope and GBP 650/day are test hypotheses, not validated willingness-to-pay evidence |
| Availability | NOT AVAILABLE; no payment or booking control may appear actionable |

The internal price model must include preparation, delivery, writing, QA,
support, software, payment cost, insurance, professional review, tax,
acquisition, refund/rescheduling burden, capacity and desired margin. Only
accepted or rejected concrete scoped proposals count as price decisions.

## 18. Commercial evidence register

| Evidence | Count/state at 24 Aug 2026 | What it establishes |
|---|---|---|
| Qualified target-segment conversations under current directive | 0 recorded | Nothing yet |
| Concrete accepted price decisions | 0 | No willingness-to-pay evidence |
| Concrete rejected price decisions with reason | 0 | No price-boundary evidence |
| Privacy-preserving repeated-use signal | Not available from current retained export | Repeated use unvalidated |
| Unsolicited qualified inbound | 0 recorded in the canonical register | No product-led demand evidence |
| Editorial submissions | 0 sent | No editorial response or referral evidence |
| Corporate first contacts | 0 delivered | No outreach response evidence |
| Representative founder comprehension sessions | 0 | Human comprehension unvalidated |

Absence of recorded evidence is not proof that nobody has ever used or asked
about Regula; it is the only defensible state of this register. Traffic,
downloads, stars and email-link clicks do not count as price decisions.

## 19. Rollback and incident runbook

1. **Misleading or privacy-violating event:** remove or disable the exact event
   call, deploy the revert, verify network requests in a real browser, record
   the affected window and update the privacy notice. Do not delete the record
   of what occurred.
2. **Broken production journey:** identify the first bad commit, preserve logs
   and screenshots, revert through a reviewable commit, wait for the Pages
   deployment terminal state, then re-run desktop/mobile/keyboard/error/no-JS
   paths. Never point DNS at an unverified replacement during diagnosis.
3. **Bad package release:** PyPI and GitHub release artefacts are immutable.
   Do not overwrite. Assess severity, publish a corrected version, and yank or
   deprecate only with a recorded reason and user guidance.
4. **Bad MCP metadata:** a published version is immutable and a deleted status
   remains accessible. Publish corrected metadata only under a unique version;
   use status changes for deprecation/security handling and record the residual
   visibility.
5. **Outreach objection or wrong recipient:** stop the sequence, add the exact
   address to the private suppression register immediately, confirm no further
   automation exists, and review the segment before another send. No public
   repository record may contain the address.
6. **Research privacy incident:** stop recruitment and access, preserve a
   minimal incident record, follow the recorded controller/breach route, honour
   withdrawal/deletion, and do not resume until the privacy gate is re-passed.
7. **Paid-service failure:** payment and booking are inactive, so no fulfilment
   incident path exists yet. They remain inactive until one payment can create
   one deliverable and one fulfilment record with tested decline, duplicate,
   refund, cancellation, no-show and consultant-unavailable states.
