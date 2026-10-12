# UX archetypes, journeys and redesign basis

Status: implemented design contract and research plan, 27 August 2026.

## Evidence status

The four archetypes below are **provisional, evidence-backed hypotheses**. They
come from implemented Regula workflows, support questions, failure modes and
the product contract in `docs/PRODUCT_COVERAGE_AND_JOURNEYS.md`. They have not
been confirmed by representative moderated research. Automated tests, browser
exercises and an expert review can show that a path is operable. They cannot
show that representative people understand it, trust it appropriately or can
use it confidently in their own setting.

The website must not describe these archetypes as validated until the study in
the final section has been completed. This distinction prevents a redesigned
interface from turning an untested audience assumption into a product claim.

## Provisional archetypes and jobs

| Archetype | Situation and job | Needs from Regula | Costly failure | Homepage route |
|---|---|---|---|---|
| Founder or product lead | Needs to work out which deployment and operator facts matter before choosing a deeper review path | Plain language, a short browser route, explicit unknown states and a practical hand-off | Treating a five-question indication as a legal classification | Scope a system |
| Builder or maintainer | Needs to inspect a codebase before release without uploading proprietary source | Local execution, exact source locations, scan-completion facts, reasons and configuration routes | Treating a match as a legal fact or a clean scan as low risk | Inspect source code |
| Governance or assurance reviewer | Needs to combine declared context with technical observations and prepare reviewable material | Provenance, contradictions, unresolved facts, source references and clearly labelled scaffolds | Treating self-attested or generated material as verified evidence | Prepare review material |
| Evaluator or adopter | Needs to decide whether Regula is suitable for a specific codebase and operating process | Reproducible methods, coverage levels, external diagnostics, performance data, limitations, security and accessibility evidence | Generalising synthetic performance to real-world validity | Evaluate the tool |

A qualified contextual reviewer, such as counsel, a DPO, a security or
accessibility specialist, consumes Regula artefacts. This person is not a sales
persona. The interface must preserve the evidence and uncertainty they need
instead of implying that Regula replaces their judgement.

## Journey 1: scope a system

| Stage | Person's question | Interface responsibility | Required exit state |
|---|---|---|---|
| Orient | What can this tool actually tell me? | State that Regula indicates possible relevance and unresolved facts, not compliance | Person can choose the browser assessment or leave for methods and limits |
| Select context | Which jurisdiction and role describe this use? | Explain the choice, keep `unknown` available and never default uncertainty to No | Selected jurisdiction and declared source remain visible |
| Answer | What facts does the next decision depend on? | Ask one related question at a time, show progress, permit Back, preserve native controls and explain unfamiliar terms | Answer is recorded or explicitly unknown or not applicable |
| Review | What do my answers point at? | Separate declared facts, possible provisions and facts the questionnaire cannot establish | Results include limitations and open questions |
| Continue | What should I do now? | Offer a local scan, evidence preparation or qualified review with each route's limits | Person chooses a reversible next step or exports a reviewable record |

## Journey 2: inspect source code

| Stage | Person's question | Interface responsibility | Required exit state |
|---|---|---|---|
| Evaluate privacy | Will my source leave my machine? | Say where processing occurs before asking for code | Local browser or CLI route is chosen intentionally |
| Run | Is the scan complete? | Show discovered, eligible, scanned, skipped, unsupported and failed files | Complete, partial, no eligible files or recoverable failure is explicit |
| Understand | Why was this line reported? | Show the matching observation, location, rule and analysis limits | Person can inspect, configure or reject the observation |
| Add context | What can code not show? | Ask for intended purpose, role, domain and deployment facts without converting missing facts to No | Missing and contradictory facts remain visible |
| Hand off | What can another reviewer reproduce? | Preserve version, configuration, integrity metadata and unresolved fields | Artefact is labelled as an observation or scaffold, never a verdict |

## Journey 3: prepare review material

| Stage | Person's question | Interface responsibility | Required exit state |
|---|---|---|---|
| Establish provenance | Where did every fact and observation come from? | Distinguish user declarations, code observations, references and reviewer conclusions | Every material item has source and time metadata |
| Resolve uncertainty | Which facts block the next decision? | Group missing, contradictory and unavailable facts without hiding them | Open questions have an owner or remain explicitly unresolved |
| Build evidence | What can be prepared automatically? | Generate reviewer-completable scaffolds and mark self-attested content | Generated material is distinguishable from verified evidence |
| Review | Who decides what this means? | Keep confirmation, rejection and request-for-evidence as human actions | Accountable decision and rationale can be recorded outside the detector |

## Journey 4: evaluate Regula

| Stage | Person's question | Interface responsibility | Required exit state |
|---|---|---|---|
| Claims | What does Regula claim and refuse to claim? | Present the claim boundary before feature and coverage lists | Evaluator can explain the boundary in their own words |
| Evidence | What has actually been measured? | Separate conformance, repeatability, diagnostic validity and human usability evidence | Caveats travel with every figure |
| Reproduce | Can I run the same checks? | Pin versions, commands, corpora and expected outputs | Result is reproducible or the difference is recorded |
| Trial | Does it work in my context? | Recommend a sequestered local sample and non-blocking adoption path | Local review burden and missed material issues are measured |
| Decide | What is the exit path if evidence is inadequate? | Keep installation reversible and output contracts inspectable | Adopt, restrict, defer or reject with a recorded basis |

## Information architecture implemented in this redesign

The homepage now answers these questions in sequence:

1. What can Regula show, and where does human judgement begin?
2. How do declared facts, code observations, open questions and a human
   decision relate?
3. Which route matches the person's current responsibility?
4. Can a founder complete a short orientation without installing anything?
5. Can a technical or evaluating reader inspect the actual product, coverage,
   methods and limitations?

The top-level labels remain task-based: Assess scope, Scan code, Coverage, and
Methods and limits. The homepage adds explicit entry cards for review material
and evaluation without claiming features that the linked pages do not expose.

## Research and design decisions

Sources were retrieved on 27 August 2026. Primary guidance informed the
interaction decisions. Competitor pages were used only to identify common
presentation patterns and failure modes, not as evidence that those patterns
are effective.

| Source | Observed guidance or pattern | Design response |
|---|---|---|
| [GOV.UK, Structuring forms](https://www.gov.uk/service-manual/design/form-structure) | Start from a question protocol, try one thing per page first, branch common scenarios, and use research to decide grouping | The homepage qualifier progressively shows one question while retaining an all-questions no-JavaScript fallback |
| [GOV.UK Design System, Question pages](https://design-system.service.gov.uk/patterns/question-pages/) | Provide Back and Continue, allow a genuine not-sure response, and keep progress simple | The enhanced qualifier has Back, Continue, a five-step indicator and no automatic advance after selection |
| [USWDS, Establish trust](https://designsystem.digital.gov/patterns/complete-a-complex-form/establish-trust/) | Explain purpose, effort and data handling, use progressive disclosure, and support no-blame recovery | Calls to action state approximate effort and where processing occurs; error copy preserves uncertainty |
| [W3C WAI, Multi-page forms](https://www.w3.org/WAI/tutorials/forms/multi-page/) | Use logical groups, informative headings and progress, and avoid time limits | Native fieldsets remain, the active question is announced as a step, and no timer is introduced |
| [WCAG 2.2](https://www.w3.org/TR/WCAG22/) | Perceivable, operable, understandable and robust interfaces require more than visual polish | Keyboard, focus, reflow, zoom, reduced-motion, name and state checks remain release evidence rather than design assumptions |
| [web.dev, Core Web Vitals thresholds](https://web.dev/articles/defining-core-web-vitals-thresholds) | Good p75 thresholds are LCP at most 2.5 seconds, INP at most 200 milliseconds and CLS at most 0.1 | The redesign remains static, dependency-free and progressively enhanced; production field data is still required |
| [Credo AI](https://www.credo.ai/), [VerifyWise](https://verifywise.ai/), [Saidot](https://www.saidot.ai/product), and [Modulos](https://www.modulos.ai/modulos-ai-governance-platform/) | Current product pages commonly use a concise task promise, generous spacing, workflow visualisation and role-oriented entry points. Some also use intrusive overlays or broad compliance language | Regula adopts task clarity and workflow visualisation while retaining no tracking overlay, no forced account and a narrower claims boundary |

The ISO usability standard page could not be retrieved during the research
session because the source returned HTTP 403. No claim from that page is used
as an evidence basis here.

## Human confirmation study still required

Recruit people who currently perform each of the four jobs above. Include
fluent German and Brazilian Portuguese participants for those experiences and
proficient assistive-technology users for the relevant tasks. Do not recruit
only existing maintainers or people already familiar with the claims boundary.

Use realistic, non-leading scenarios and observe whether participants can:

- choose the appropriate entry route without explanation;
- complete the assessment and recover from an uncertain answer;
- explain that a finding is an observation rather than a compliance verdict;
- identify at least one fact that code cannot establish;
- find methods, limitations, privacy and source information;
- complete the same primary task with keyboard and relevant assistive
  technology;
- recognise partial, unsupported, empty and failure states.

Record task completion, critical errors, assistance, time on task, a
post-task ease rating, confidence and the participant's own explanation of the
result. Run a second formative round after fixing severe blockers. Evidence can
support an archetype only when recruited participants in that role recognise
the job, attempt the expected route and can act on the result without adopting
the prohibited compliance interpretation. Report contrary evidence and do not
average severe failures away.

