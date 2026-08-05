# Regula direct-transaction discovery launch-gate session

Date: 2026-08-05
Time: 132655 Europe/London
Repository: /home/mkuziva/getregula

Objective: prepare the minimum owner-decidable human-discovery launch gate
without contacting anybody, collecting real data or building Regula.

VENTURE_DECISION: STOP
PRODUCT_PILOT_STATUS: NOT_APPROVED
EXTERNAL_CONTACT: NOT_AUTHORISED
REAL_DATA_COLLECTION: DISABLED
SOFTWARE_BUILD: STOP

## Authority and initial repository state

Started: `2026-08-05T13:26:55+01:00`

Working directory and writable root: `/home/mkuziva/getregula`. Sandbox: workspace-write; network restricted but read-only public retrieval authorised. Git write probe was repeated with the minimum escalation and returned `git_dir_writable=yes`. Initial HEAD was `ba673b2cb0b5ec8b3dc08f15e82e98251720cff8`, tree `ab912efbdc37d694ac52b2f0ab2e3c6b72946724`, branch `audit/regulatory-current-2026-08-04`, clean and 13 commits ahead of `origin/main`. Existing detached worktrees were read-only concurrent-state risks; no active writer was found.

## Governing-state reproduction and readiness audit

The complete ledger, current readiness pack, transaction-evidence review, handover and permanent log were inspected. N67 continues to abandon H1 with `PUBLIC_TRANSACTION_EVIDENCE: GENERAL_PROBLEM_ONLY`; N66 remains partial and points to N67. No H2 or product authorisation was found. The existing 29-file readiness pack remains a preparation-only historical control. Its validator passed, but cannot establish legal approval, participant access, transaction recurrence or future corpus integrity.

## Sources retrieved

Primary/original sources and decisive uses are retained in `docs/venture/direct-discovery-2026-08-05/SOURCES.md`: ICO research safeguards and current under-review notice; MRS Code of Conduct and interviewer guidance; Flanagan's Critical Incident Technique; Byrne and Sadeghi methodological reviews; Malterud et al. on continuous information-power appraisal; Wutich et al. on context-dependent sample guidance; SRQR; COREQ and critiques of mechanical checklist use; Morgan on dyadic interviews; Mahoney and Goertz on negative cases; and Olmos-Vega et al. on reflexivity. These sources justify methods only, not a Regula result.

## Implementation

Commit: `c11a831` (`docs(discovery): update gate, audit, method, outreach, decisions, sources, schema, examples, ledger`). Nine documentation/schema files changed. No product code, tests, website, public claim, pricing, version, benchmark, ownership or immigration record changed.

The pack now contains one irreducible owner/professional decision register; exact transaction inclusion and exclusion; neutral supplier/buyer guides; deliberate negative cases; information-power and qualitative value-of-information routing; a de-identified schema and two synthetic examples; an H2 generation gate that requires fresh holdouts and cannot change technical-fit or differentiation verdicts; and unsent outreach including withdrawal/deletion wording. H1 remains abandoned and H2 is not created.

## Adversarial reviewer A — verbatim initial review

1. HIGH — The H2 observability gate can be passed on participant assertion rather than demonstrated technical evidence. `02-DISCOVERY-METHOD.md:169-171` requires “a material subset is technically observable,” while Stage A prohibits documents and repositories and `transaction-schema.json:41` permits `corroboration_state: PARTICIPANT_REPORTED` alongside source-code/CI/runtime observability. Nothing in the gate requires corroboration stronger than participant report. Limit the gate conclusion to `OBSERVABILITY_INDICATED`, or require a later permissioned artefact check before calling it demonstrated or Regula-relevant.

2. HIGH — The H2 gate does not explicitly prevent pain/incumbent inadequacy from becoming a differentiation claim. Lines `164-173` permit H2 after burden, observable evidence and inadequate workaround, then refer to a “proposed advantage.” Those facts can justify a new hypothesis, but they do not show that Regula performs the job, beats a manual baseline, is accurate, or is differentiated. Add an explicit boundary: H2 creation is exploratory problem/transaction evidence only; `TECHNICAL_FIT` and `DIFFERENTIATION` remain unchanged until prospective comparison.

3. MODERATE — The prospective hypothesis can be tailored after observing the same cases used to satisfy its gate. `02-DISCOVERY-METHOD.md:164` says “H2 … may be preregistered only after three … transactions.” That is legitimate hypothesis generation, but it is not preregistration before discovery evidence. Require H2 to be labelled generated from these cases and tested on fresh holdout transactions; the three generating cases cannot validate H2.

4. MODERATE — Machine enforcement still depends on a future corpus check. The method itself acknowledges at `02-DISCOVERY-METHOD.md:125-131` that the object schema cannot enforce unique accounts/event groups, range ordering/null rules or supported inadequacy, and H2 cannot be gated until a corpus control exists. This is an honest stop control, but remains an execution blocker rather than a completed safeguard.

5. MODERATE — Schema permits malformed or semantically empty gate evidence. `transaction-schema.json:29` allows empty `role`, `purpose`, and `basis` in actual expenditure; requirement strings at `:41` (`requirement_id`, requester/reviewer, acceptance, observability basis, uncertainty) have no `minLength`; and JSON Schema does not enforce lower ≤ upper or the null/unit relationship at `:42`. The written corpus rule catches some, not all. The future validator should reject empty gate fields and invalid bounds.

6. MODERATE — Hypothetical-value coding is not machine-bounded. Method `:71-72` says hypothetical value must be `HYPOTHETICAL_ONLY`, but `transaction-schema.json:30` accepts any string and makes it optional. A future record could store persuasive price enthusiasm without the required label. Use a constant status plus a separate non-decision-bearing note, or omit hypothetical value entirely.

7. LOW/MODERATE — “No negative case already falsifies the proposed advantage” (`02-DISCOVERY-METHOD.md:172`) lacks a preregistered rule for which negative case falsifies which advantage. Because H2 is created after seeing the cases, this leaves room to redefine the advantage around adverse evidence. Require the generated H2 to list every retained negative case and prospectively freeze its falsifiers; do not discard a negative case merely because it falls outside a post-hoc formulation.

8. LOW — `transaction-schema.json` validates one account object, while `synthetic-examples.json` is a top-level array. This is acceptable only if the future corpus validator iterates and validates every element; direct validation of the examples file against this schema is a type mismatch.

9. POSITIVE — I found no material leading-question, Regula-naming, hypothetical-event, sample-size, one-sided, negative-case, WTP, market-size or checklist-quality defect in the written method. Specific safeguards are strong: hypothetical events are excluded (`:23-26`); the unaided account precedes analyst observability coding (`:48-55`); technical/product prompts and buy questions are prohibited (`:85-89`); negative cases are deliberately sought and retained (`:100-108`); Stage A and the 12-person cap are explicitly non-statistical (`:135-140`); buyer evidence must match two transactions (`:164-168`); three cases do not establish prevalence, recurrence, market or demand, and WTP remains unvalidated (`:172-176`).

Overall: no fatal flaw in the interview design. Before execution/H2 gating, findings 1–6 need enforcement or explicit downgrade language. The main conceptual risk is turning participant-reported technical observability and an inadequate incumbent into Regula differentiation.

## Reviewer A — verbatim final disposition

1. Participant-reported observability — RESOLVED. The gate now says `OBSERVABILITY_INDICATED` (`02-DISCOVERY-METHOD.md:169-171`), requires permissioned artefact verification before observability is “demonstrated or Regula-relevant” (`:179-183`), and the synthetic positive correctly remains `PARTICIPANT_REPORTED`.

2. Pain/incumbent inadequacy converted to differentiation — RESOLVED. Lines 183–186 explicitly preserve `TECHNICAL_FIT: FAILED_UNTIL_NEW_EVIDENCE` and `DIFFERENTIATION: NOT_DEMONSTRATED` until prospective manual-baseline comparison.

3. Generated versus tested H2 — RESOLVED. Lines 179–182 explicitly label H2 generated from discovery cases, prohibit those cases from validating it, and require fresh holdout transactions.

4. Future corpus-check dependency — REMAINS BY DESIGN, CORRECTLY DISCLOSED AS A HARD BLOCKER. Lines 125–131 state the object schema cannot establish the cross-record facts and H2 cannot be gated until the corpus control exists and passes. This is honest preparation status, not an undisclosed defect. Execution/H2 gating remains prohibited until implemented and tested.

5. Empty/malformed gate fields — SUBSTANTIALLY RESOLVED. Required role, expenditure, requirement, basis and uncertainty strings now use `minLength: 1`; substitute basis is mandatory. JSON Schema still cannot enforce `lower <= upper`, null/unit coupling, cross-record uniqueness, or semantic support for inadequacy, but these are explicitly assigned to the blocking corpus check at method lines 119–131.

6. Hypothetical-value route — RESOLVED. The unconstrained `hypothetical_value` field was removed from the schema and examples; the interview method still explicitly says hypothetical value is never WTP evidence (`:71-72`).

7. Post-hoc treatment of negative cases — RESOLVED FOR HYPOTHESIS GENERATION. Lines 179–182 require every retained negative case to be listed and the mechanism/falsifiers frozen before fresh holdout testing. Negative cases are also deliberately sought (`:105-108`) and independently reviewed (`:128-130`).

Verdict: no remaining conceptual blocker in findings 1–3 or 5–7. The only remaining blocker is the deliberately disclosed, not-yet-implemented corpus validator. The pack must remain `PREREGISTERED_NOT_EXECUTED`, and H2 cannot be gated, until that validator exists and passes.

## Adversarial reviewer B — verbatim result

Fresh Review B result (read-only; no edits): no material finding in the specified scope.

Evidence supporting that conclusion:

- Contact/data remain blocked at `00-OWNER-LAUNCH-GATE.md:40-42`, `:47-55` and `05-OWNER-AND-PROFESSIONAL-DECISIONS.md:28-29`; every prerequisite, reviewed participant information, tested storage and explicit owner authorisation are required before contact.
- Consent is not substituted for lawful basis: `01-READINESS-AUDIT.md:9`, `00...:25`, and `05...:14` say this explicitly.
- Controller, purpose, system/jurisdiction/processor, access roles, retention, deletion/objection, privacy-notice ownership and work permission remain unresolved gates at `05...:12-25`; no hidden controller/storage decision is inferred.
- Confidentiality boundaries are explicit in `04-OUTREACH-DRAFTS.md:14-16,27-30,49-59`; accidental disclosure triggers stop/omit/redact under a reviewed process, and deletion promises remain conditional.
- `03-ORGANISATION-ACCESS-MAP.md:3-4,16-18` contains named organisations only, expressly no person/contact details, and distinguishes a route candidate from actual access.
- Outreach is visibly unsent and non-sales at `04...:3,7-17,21-30`; Regula is not offered or demonstrated.
- H1 remains abandoned and H2 not created at `00...:3,13-14`; the broader transaction-first method is framed as hypothesis-generating/falsification preparation, not a validated new market. N69 preserves the same boundary.
- No founder-origin, Innovator Founder, immigration eligibility, ownership or role-assignment claim appears. The word `founder` in the complete diff is only a possible supplier-role archetype in the discovery method, not a founder narrative.
- Schema/synthetic-example work is research instrumentation, explicitly synthetic/de-identified and real-data-disabled, not product functionality.
- The validator’s `29 required files: PASS` remains bounded to the historical readiness pack. `01-READINESS-AUDIT.md:22-23` explicitly says it does not test future corpus/legal readiness or authorise this launch gate.

Current diff caveat, not a defect: `05-OWNER-AND-PROFESSIONAL-DECISIONS.md` and the current session log are untracked, but I directly inspected the former as required; the tracked/untracked state does not itself authorise any action. `git diff --check` is clean.

I found no hidden personal contact data, outreach execution, consent-as-lawful-basis, implicit external authorisation, hidden product build, founder/immigration claim, or unevidenced commercial hypothesis presented as fact.

Disposition: no material correction required within the reviewed scope. Preserve the existing HOLD, external-contact prohibition, real-data prohibition, and owner/professional prerequisites. The untracked session evidence should be included in the explicit final file-set review before commit, but its untracked state is not itself an authorisation or substantive defect.

## Verification evidence

- `python3 scripts/validate_validation_readiness.py` → exit 0; `validation-readiness pack: PASS (29 required files)`.
- Direct schema check → exit 0; 2/2 synthetic accounts accepted. Negative controls for empty blocker and invalid corroboration state were rejected.
- Six fast gates and `git diff --check` → exit 0. They emitted the repository's existing tree-guard warning that the tree differs from its 2026-07-30 baseline. This warning is disclosed and was not suppressed.
- `python3 tests/test_classification.py` → exit 0; `1389 passed, 0 failed, 0 skipped (1090 test functions)`.
- `python3 -m pytest tests/ -q -rs` → exit 1; `1 failed, 2691 passed in 852.48s`. Failure: `test_count_literal_appears_nowhere_outside_the_manifest`; the current canonical count collides with a literal in dated `08-EVIDENCE-RECONCILIATION.md`.
- The identical focused test at untouched starting commit `ba673b2` → exit 1 for the same file and collision. Therefore the failure is inherited, not introduced by this unit. It remains unresolved; no allowlist, test change or historical-record rewrite was used to force green.
- `python3 -m scripts.cli self-test` → exit 0; 6/6 passed.
- `python3 -m scripts.cli doctor` → exit 0; 8 passed, 4 informational messages.
- `git diff --check` → exit 0.

## Hostile self-review

Every implementation file was reread. Search hits for strong terms were contextual prohibitions, explicit `UNVALIDATED`/`DISABLED` states, source titles, or bounded methodological warnings. No unsupported result was retained. Diff searches found no skip, xfail, allowlist, quarantine, dependency pin, hardcoded pass, TODO, FIXME or fallback added by this unit.

## Final status

DIRECT_DISCOVERY_PACK: READY_FOR_OWNER_REVIEW
DATA_GOVERNANCE: OWNER_INPUT_REQUIRED; PROFESSIONAL_REVIEW_REQUIRED
ORGANISATION_ACCESS_MAP: READY
OUTREACH: DRAFTED_NOT_SENT
EXTERNAL_CONTACT: NOT_AUTHORISED
REAL_DATA_COLLECTION: DISABLED
H1_STATUS: ABANDONED
H2_STATUS: NOT_CREATED
WILLINGNESS_TO_PAY: UNVALIDATED
TECHNICAL_FIT: FAILED_UNTIL_NEW_EVIDENCE
DIFFERENTIATION: NOT_DEMONSTRATED
PRODUCT_BUILD: STOP
VENTURE_DECISION: STOP
PRODUCT_PILOT_STATUS: NOT_APPROVED

Unit completion: PARTIAL. The launch pack itself is ready for owner review, but the repository-wide required pytest suite is not green because of demonstrated inherited count-collision debt. The future corpus validator is also intentionally not implemented and blocks any H2 gate.

## Authority and initial state

Started `2026-08-05T13:26:55+01:00`. Initial HEAD
`ba673b2cb0b5ec8b3dc08f15e82e98251720cff8`, tree
`ab912efbdc37d694ac52b2f0ab2e3c6b72946724`, branch
`audit/regulatory-current-2026-08-04`, clean, 13 commits ahead of `origin/main`.
Repository files are writable. The exact pre-authorised unrestricted `.git`
probe returned `git_dir_writable=yes`, exit 0. Network is restricted by default
but read-only public retrieval is authorised. Read-only subagents are available.
No concurrent writer or verification process was observed beyond the current
Codex shell processes.
