# Stage A data architecture and re-identification threat model

STATUS: PREPARATION ONLY
EXTERNAL CONTACT: NOT AUTHORISED
REAL DATA COLLECTION: DISABLED
REAL DATA IN GIT: PROHIBITED

## Classification and boundary

Future interview records are `PSEUDONYMISED`, not anonymous by default. Removing
names does not prevent singling out or linkage from rare roles, dates, sectors or
events. The current repository contains an empty schema and two synthetic
examples only. It is not an approved real-data store.

ICO anonymisation guidance published 28 March 2025 is under review following the
Data (Use and Access) Act 2025. The architecture therefore uses the stricter
reversible boundary: minimise, separate identity/linkage/content, restrict
access and retain the possibility that the analytical corpus remains personal
data. This is a design decision, not a lawful-basis conclusion.

## Three separated layers

| Layer | Permitted future content | Separation and access | Deletion/linkage |
|---|---|---|---|
| 1. Contact and participation register | Minimum identity/contact, invitation/permission status, random participant token | Approved business system only, never Git; research lead only; no interview content; token generated randomly, never from identity | Controller-approved retention; deletion owner propagates withdrawal to Layers 2 and 3 |
| 2. Transaction-linkage register | Random participant/account tokens mapped to random transaction tokens, linkage permission, creation/deletion audit | Separate approved system and access role; no analytical content; no token derived from name, domain, date or event facts; never disclose counterpart participation | Link only with explicit scoped permission; false-match/duplicate review; withdrawal removes mappings and flags linked analytical records |
| 3. Analytical transaction corpus | Pseudonymised transaction/account facts, bands, evidence states, contradictions and uncertainty | No contacts, names, employer-identifying free text, customer/product names, contracts, repositories, code, security findings or special-category data; independent analyst need not access Layers 1 or 2 | Random transaction token may group permissioned accounts; small-cell review before reporting; withdrawal propagated unless a professionally reviewed irreversible aggregation boundary applies |

No real layer is created in this unit. Approved storage, controller, access
roles, processors, jurisdiction, retention and deletion procedure remain gates.

## Threat model

Qualitative likelihood labels describe plausible routes, not measured
probabilities.

| Threat and asset | Adversary and route | Likelihood | Consequence | Mitigation and residual risk | Decision/review |
|---|---|---|---|---|---|
| Singling out a participant | Reader combines rare role, sector, buyer band and outcome | PLAUSIBLE | Identity or employer inferred | Coarsen bands, suppress rare combinations, prohibit identifying prose; residual inference remains | Controller sets reporting rule; professional review |
| Event linkage | Reader combines date, product category, buyer type and public announcement | PLAUSIBLE | Transaction/counterparty inferred | Recency bands, no names/exact dates, small-cell review; retain pseudonymised classification | Owner and data-protection review |
| Dictionary attack | Insider hashes likely names/domains against deterministic IDs | PLAUSIBLE if deterministic | Identity recovered | Cryptographically random tokens; no deterministic identity/event hashes | Technical design gate |
| Insider access | Over-privileged researcher joins all layers | PLAUSIBLE | Full re-identification | Separate systems/roles, least privilege, access audit; research lead alone handles Layer 1 | Owner assigns roles; professional review |
| Accidental Git inclusion | Operator stages export, logs or contact file | PLAUSIBLE | Durable replication and disclosure | Real data in Git prohibited; approved storage outside repo; pre-commit/path controls before activation | Owner storage decision; future operational test |
| Logs and backups | Provider or application logs tokens/content beyond retention | PLAUSIBLE | Persistence after deletion | Map logs/backups/processors, minimise diagnostics, verify deletion limits | Processor/storage review |
| Linkage-table disclosure | Layer 2 export or error reveals paired participants | PLAUSIBLE | Counterpart participation disclosed | Separate restricted register, no counterpart disclosure, safe error messages, audited access | Linkage permission and security review |
| False match or duplicate | Similar accounts incorrectly joined | PLAUSIBLE | Wrong corroboration or double counting | Random transaction token assigned only after reviewed evidence; duplicate queue; retain uncertainty | Research lead plus independent review |
| Counterpart inference | Interview wording reveals the other side participated | PLAUSIBLE | Confidential participation revealed | Never disclose or confirm counterpart participation; link asynchronously in Layer 2 | Interviewer training |
| Quoted free text | Distinctive phrase is searchable | PLAUSIBLE | Speaker/organisation inferred | No verbatim free text in analytical corpus; paraphrase and review | Data-minimisation gate |
| Cross-session inference | Repeated role/band combinations connect records | PLAUSIBLE | Longitudinal identity inference | Random session-independent tokens only where linkage is permitted; otherwise rotate tokens and suppress combinations | Purpose/linkage decision |
| Withdrawal across a dyad | One side withdraws after linked analysis | PLAUSIBLE | Residual contribution or counterpart disclosure | Layer 2 deletion audit identifies affected Layer 3 records without notifying counterpart; quarantine/reanalyse; record exceptions | Professionally reviewed procedure |

## Data flow and failure handling

An authorised organisation route may lead to a Layer 1 contact entry only after
separate contact authorisation. The interviewer records minimised notes into
Layer 3 under a random account token. Layer 2 is created only where separate
linkage permission exists. Identity never flows into Layer 3. Analytical output
flows outward only after small-cell, quotation and inference review.

If prohibited data is disclosed, stop the discussion, do not copy it, quarantine
any affected note in approved storage, notify the deletion/incident owner and do
not write details to Git or general logs. Error output may contain random record
tokens and control status only, never identities or interview content.

## Deferred H2 corpus control

The cross-record H2 validator is not built. It is required after Stage A and
before H2 generation, against a frozen real-record schema. Its future contract
must enforce uniqueness, range consistency, permissioned event linkage,
negative-case status, substitute basis, generating-versus-holdout separation
and analyst independence. Before real collection, the frozen schema and
operating control must also constrain band vocabularies, review all free text,
test rare combinations and apply small-cell suppression. The current object
schema enforces synthetic structure only; its prose description does not
mechanically prevent identifying text. Synthetic examples cannot establish
real-corpus fitness.
