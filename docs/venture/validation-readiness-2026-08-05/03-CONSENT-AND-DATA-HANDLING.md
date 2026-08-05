# Consent and data-handling protocol

STATUS: PREPARATION ONLY
EXTERNAL ACTION: DISABLED
VENTURE DECISION: STOP
PRODUCT PILOT: NOT APPROVED

LEGAL REVIEW: REQUIRED
DATA-PROTECTION REVIEW: REQUIRED
REAL DATA COLLECTION: DISABLED

Participation permission is not treated as the UK GDPR lawful basis. Candidate
bases include legitimate interests for a private research controller or consent
where genuinely appropriate, but the decision is `ADVISER_INPUT_REQUIRED`.
Controller identity, processor contracts, DPIA need, transfer status and ethics
review route are unresolved.

## Data minimisation register

### Stage A controlling override

Owner-approved Stage A defaults prohibit recording, transcription, confidential
documents, private repositories, source code, security findings,
special-category data, incentives, Regula demonstration, sales, publication and
real data in Git. Broader categories below are future risk planning only and do
not authorise receipt. Any later change requires a separate owner decision,
professional review where applicable and updated participant information.

Stage A data remains `PSEUDONYMISED`, not anonymous by default. Contact,
transaction-linkage and analytical records must occupy the three separated
layers in `../direct-discovery-2026-08-05/06-DATA-ARCHITECTURE-AND-THREAT-MODEL.md`.

| Category | Need and minimum | Access/storage expectation | Retention/deletion proposal | Risk and review |
|---|---|---|---|---|
| Participant identity/contact | Scheduling and withdrawal token; name, work role, business email only | Named researcher; approved encrypted system selected by owner | Stage A proposal: delete 30 days after the participant's note-summary review closes or participation closes if no review is offered; final dated period remains owner/professional-gated | Personal data; lawful basis and privacy notice review |
| Consent and permissions | Prove scoped permission; signed choices and version | Research lead plus audit accessor | `ADVISER_INPUT_REQUIRED`; no default period selected | Do not bundle recording, documents or reuse |
| Audio/video | PROHIBITED in Stage A; later use requires a new gate | No Stage A storage | Not collected | Voice and transcription risks require separate future review |
| Notes | Transaction facts; no verbatim transcript; remove names and irrelevant personal detail | Pseudonymised approved encrypted workspace | Participant note-summary review if offered; review at 90 days and proposed deletion after decision unless separately authorised | Withdrawal possible until professionally reviewed irreversible-aggregation cut-off |
| Questionnaire/buyer document | PROHIBITED in Stage A | No Stage A storage | Not collected | Later receipt requires a separate confidential-material gate |
| Source repository/code | PROHIBITED in Stage A | No Stage A storage | Not collected | Later access requires separate permission, security and rights review |
| Contracts/security/model/regulatory evidence | Avoid unless essential; redacted minimum | Qualified reviewer only | Document-specific expiry | High confidentiality; legal/security escalation before receipt |
| Annotation and derived data | Label, evidence pointer, rater ID pseudonym and uncertainty | Study team | Retain only under granted reuse rights | Re-identification and IP risk; no publication right assumed |
| Incentive/payment record | Only if later authorised; amount and required accounting fields | Finance role separated from research content | Statutory/accounting period requires advice | Spending currently prohibited |
| Special-category/criminal data | Not needed | Must not be collected | Delete and incident-escalate if received unexpectedly | Additional Article 9/10 condition required; adviser gate |
| Operational metadata and backups | Access, audit, deletion and incident evidence; minimum event, actor, object and time | Same access boundary as the underlying record | Must follow the underlying record or a separately justified security period | Cloud logs, caches, exports and backups must be included in search and deletion design |

International access includes remote access. Default is UK-only storage and no
subprocessor. Encryption means contemporary authenticated encryption at rest and
TLS in transit, with separate access credentials and least privilege. Exact
provider, controller and retention remain owner decisions recorded before use;
“UK encrypted workspace” is not an implemented control. Pseudonymisation is
not anonymisation. Publication and benchmark reuse require separate permission.

## Rights, withdrawal and incidents

Participants may decline questions and request research withdrawal using their
token until the disclosed irreversible aggregation cut-off. That cut-off must be
set before collection and cannot precede the participant note-summary review
window, where offered, or the disclosed participation-close date.
The token map is retained until the later of that cut-off or resolution of an
open request. The researcher verifies identity without
collecting excess data, records scope, quarantines the record, and completes or
explains the request under reviewed procedures. Deletion cannot be promised where
law requires retention; that boundary needs advice. A suspected loss, unauthorised
access, secret, special-category data or contractual breach stops processing,
revokes access where possible, preserves minimal incident evidence and escalates
to the owner/data-protection adviser. Regulatory notification is not decided by
this template. UK GDPR rights requests are separate from voluntary research
withdrawal and follow `templates/RIGHTS-REQUEST.md`.

## Pre-receipt confidential-material gate

No link, repository or attachment is opened, cloned, downloaded or indexed until
the sender's authority, scope, confidentiality restrictions, privilege risk,
retention and return/destruction terms are recorded. Unsolicited material is
quarantined without substantive review and escalated to an authorised owner.
Triage covers embedded secrets, logs, caches, backups and processor copies.

No real participant personal data appears in this pack. All templates are drafts,
not legally approved.
