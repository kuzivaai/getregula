# Existing readiness-pack reuse audit

This audit reuses the committed validation-readiness pack. It does not rewrite
its abandoned insurer-specific protocol or treat templates as approved controls.

| Component | Existing file | Disposition | Reason/action |
|---|---|---|---|
| Participant information | `templates/PARTICIPANT-INFORMATION.md` | NEEDS_NARROW_CORRECTION | Populate transaction-first purpose, controller, storage and retention after decisions |
| Participation consent | `templates/CONSENT.md` | READY_WITHOUT_CHANGE | Correctly separates participation permission from lawful basis |
| Confidentiality | `templates/CONFIDENTIALITY.md` | PROFESSIONAL_REVIEW_REQUIRED | Stage A avoids confidential information; retain for later only |
| No-recording pathway | `templates/RECORDING-CONSENT.md` | READY_WITHOUT_CHANGE | Default is already no recording |
| Privacy information | participant information plus `03-CONSENT-AND-DATA-HANDLING.md` | OWNER_INPUT_REQUIRED | Controller, basis, storage, recipients and retention unresolved |
| Withdrawal handling | `templates/WITHDRAWAL-AND-DELETION.md` and `RIGHTS-REQUEST.md` | PROFESSIONAL_REVIEW_REQUIRED | Useful drafts; controller procedure and legal exceptions unresolved |
| Data receipt controls | `templates/DATA-RECEIPT-REGISTER.md` | NOT_NEEDED for Stage A | Documents and repositories prohibited; retain for a later separately authorised stage |
| Interview screener | `templates/RECRUITMENT-SPECIFICATION.md` | NEEDS_NARROW_CORRECTION | Existing placeholder is not executable; use transaction screener in `02` |
| Supplier guide | none specific | NEEDS_NARROW_CORRECTION | Added in `02` |
| Buyer guide | none specific | NEEDS_NARROW_CORRECTION | Added in `02` |
| Note schema | no transaction-first schema | NEEDS_NARROW_CORRECTION | Synthetic pseudonymised-form schema only; real schema remains unfrozen |
| Event and negative-case fields | partial in old discovery protocol | NEEDS_NARROW_CORRECTION | Old fields are bound to abandoned H1 |
| Owner permissions | `06-ADVICE-PERMISSIONS-AND-COST-REGISTER.md` | READY_WITHOUT_CHANGE | All external actions default not authorised |
| Go/hold/stop gate | `07-GO-HOLD-STOP-GATE.md` | NEEDS_NARROW_CORRECTION | New gate narrows Stage A; later baseline/labelling gates remain valid |
| Validator | `scripts/validate_validation_readiness.py` | READY_WITHOUT_CHANGE for the original 29-file pack | Tests preparation controls, not future corpus or legal readiness |
| Machine-readable readiness | `readiness.json` | READY_WITHOUT_CHANGE as historical readiness state | Does not authorise this launch gate or encode owner decisions |

The old `02-DISCOVERY-PROTOCOL.md` remains a historical preregistration for H1
and is not reused as the new population. H1 stays abandoned under N67/N68.
The irreducible decisions are isolated in `05-OWNER-AND-PROFESSIONAL-DECISIONS.md`.
