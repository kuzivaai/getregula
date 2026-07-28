# Phase 4 — implementation plan

Written 28 July 2026. **Not approved. Phase 4 ends at a stop-and-ask gate
and this plan does not authorise any Phase 5 work.**

Per PROGRAMME.md: each item carries measurable acceptance criteria,
tests-to-add-first, rollback path, claim-auditor impact, docs impact, and a
licence-provenance note where research code is adapted.

**Ordering principle:** the integrity apparatus is fixed before anything
that adds or changes a public number, because new numbers otherwise inherit
a broken gate. This is the same sequencing that justified Phase 1.5, and
F21 shows the apparatus is still not sound.

---

## TIER 0 — the instrument (must land before any item that touches a number)

### P1. F21 — a self-referential URL must not count as provenance
- **Acceptance (MEASURED):** a numeric claim in a `<meta name="description">`
  on a page whose only URL context is its own canonical link **is flagged**;
  the same claim with a genuine citation in scope **is not**. Auditor total
  over 56 pages recomputed and recorded; the ~16 newly surfaced findings
  each get a disposition or a quarantine entry **in the same commit**.
- **Tests first:** `tests/test_claim_auditor_selfref.py` with **both** cases.
  The negative case is the control; without it the test proves nothing.
- **Rollback:** single function change in `paragraph_has_source()`; revert
  the commit.
- **Claim-auditor impact:** this *is* the auditor. Expect the finding count
  to rise. **A rising count here is the gate working and must not be used
  as an argument against the change.**
- **Docs impact:** STATE.md finding table; quarantine header note.
- **Licence:** none, original work.

### P2. F10 + F12 — validate generated artefacts, and test the gate's own entry points
- **Acceptance:** at least one test validates each generated artefact
  (CycloneDX ML-BOM, SARIF, DPV-AIAct JSON-LD) against its **published
  schema**, and `verify_facts()` and `main()` each have a test that fails
  when the function misbehaves. Proven by mutation: break each on purpose,
  confirm red, restore.
- **Tests first:** yes, by definition.
- **Note:** F12 is tagged REPORTED. **Confirm the entry points are untested
  before writing anything** — do not act on the tag.
- **Licence:** schemas are fetched specifications, not adapted code. Record
  each schema's source URL and licence in the test file.

### P3. F4 — CycloneDX ML-BOM fails official schema validation
- **Acceptance:** `scripts/sbom.py:550` no longer emits
  `modelCard.modelParameters.owner`; output validates against the official
  CycloneDX 1.7 schema in the P2 test; the owner datum is relocated to a
  permitted field or dropped with a note.
- **Rollback:** revert; the field is additive.
- **Docs impact:** if any doc claims schema-valid ML-BOM, that claim was
  false and its correction is a **public-surface change** needing approval.
- **Depends on P2** — do not "fix" it without a test that would have caught it.

---

## TIER 1 — user-facing trust defects

### P4. F2 — `doctor` sends users to a stranger's PyPI package
- **Acceptance:** zero occurrences of `pip install regula[` in the repo
  (currently 18); every install instruction names `regula-ai`; a test
  asserts no doc or command emits the bare `regula` distribution name.
- **Tests first:** repo-wide grep assertion test.
- **Claim-auditor impact:** none directly; add the grep test as a gate.
- **Docs impact:** README, docs, CLI output. **Public surface → approval.**
- **Severity note:** this is the highest *user-harm* item in the plan.
  Following the tool's own advice installs an unrelated package.

### P5. F3 — silent AST-to-regex downgrade
- **Acceptance:** on a default install, `regula check` **discloses in scan
  output** that JS/TS analysis is regex-only; `docs/TRUST.md` states what a
  default install actually does. MEASURED: on a default install 7 of 8
  languages are regex-only.
- **Tests first:** a test asserting the disclosure appears when tree-sitter
  is absent, and does not when present.
- **Docs impact:** TRUST.md currently claims full AST for Python and JS/TS.
  **That is a false public claim → approval required.**

### P6. F20 + the 83.5% provenance fixes
- **Deferred to PACK-1.5b approval.** Listed here so the plan is complete.
  Adds a claim-auditor rule binding `83.5` to `N=115` plus a labeller route.

---

## TIER 2 — detection

### P7. The `highrisk_employment` miss (NEW, 28 Jul)
- **Origin:** the synthetic baseline. A hand-built, unambiguous Annex III
  employment fixture classified `ai_security` only, **not** high risk.
- **Acceptance:** the fixture classifies `high_risk`, **and** the synthetic
  run still shows 5/5 prohibited, 5/5 high-risk, 0 high-risk firings on the
  three negatives. Any change that fixes this by widening a pattern until
  the negatives fire is rejected.
- **Tests first:** the fixture already exists and already fails. **Trace the
  cause before changing anything** — this may be a missing Annex III 4(a)
  pattern, a tier-precedence bug where `ai_security` masks `high_risk`, or
  a domain-gating exclusion. The three have different fixes.
- **Rollback:** revert the pattern or precedence change.
- **This is the only item in the plan with a currently-failing measurement
  to satisfy**, which makes it the best-specified.

### P8. F5 — 183 of 391 tier regexes exercised by no test input
- **Acceptance:** `measure_pattern_reach.py` reports **0 unguarded patterns
  in the prohibited and high-risk tiers**; overall unguarded count strictly
  decreases and is recorded. Lower tiers may remain, tracked.
- **Tests first:** one minimal positive fixture per unguarded pattern.
- **Anti-gaming (PROGRAMME.md 3):** a fixture that merely re-states the
  regex is a tautological test. Each must be a **plausible code snippet**,
  and the anti-gaming audit in Phase 6 lists any that are not.
- **Effort warning, honest:** 183 patterns is the largest item here. It is
  mechanical but not small, and should be **split across commits by tier**,
  prohibited and high-risk first.

### P9. F11 — recall, and the corpus language monoculture
- **Acceptance:** recall measured and published **with its N and its
  construction method**; corpus extended beyond Python OR the Python-only
  limit stated at every point of use.
- **Research framing (RESEARCH-CARDS C6, Li et al. FSE 2023,
  peer-reviewed):** seven SAST tools detected 12.7% of real-world
  vulnerabilities; 70.9% went undetected; tools overstated detection by
  90.5%. **External evidence that unmeasured recall is likely the weak
  number, not precision.** Cite it when publishing any recall figure.
- **Blocked on:** rater recruitment for the real-world half. The synthetic
  half is not blocked and is already measured (4/5 high-risk).
- **Licence:** no code adapted; methodology only (dedup, chronological
  split), which is not copyrightable and is cited.

### P10. F8 — `regula check` never uses the AST engine
- **Tagged REPORTED.** **Reproduce before planning a fix.** If reproduced,
  two unreconciled detectors over the same code is an architecture item,
  not a patch, and it should return to Phase 3 rather than be fixed inline.

---

## TIER 3 — gated and deferred

### P11. F9 — cache keys lack a project root
- **ENTERS ONLY BEHIND ITS REPRODUCTION GATE**, per standing owner
  instruction. Required first: a **minimal failing case** showing provenance
  replaying across two projects and defeating `--scope`.
- **If it does not reproduce, it is downgraded and recorded as such**, not
  quietly fixed. No fix may be written before the repro exists.

### P12. The optional semantic verification tier
- **Do not build in Phase 5.** Per RESEARCH-CARDS B-CROSS: **none of the six
  FP-reduction papers addresses the actual measured failure**, because all
  operate where a hard oracle exists and regulatory classification has none.
  Five of six require a network call at scan time.
- **Gate:** build only after the multi-annotator corpus exists, so
  before/after is measurable. Building it now produces unmeasurable claims.
- **If built:** optional extra, off by default, graceful absence, its own
  ADR (constraint 4), and the AdaTaint principle — the LLM proposes, it
  never adjudicates finally.
- **Acceptance if built:** removes ≥50% of the 24 measured high-risk FPs
  while losing 0 of 5 synthetic prohibited and ≤1 of 5 high-risk.
- **No acceptance criterion may be written in terms of 88.6%, 94-98% or
  43.7%.** Those are population transfers, not predictions.

### P13. F14 — crosswalk stale, does not consume the delta-log
- **Acceptance:** crosswalk consumes `content/regulations/delta-log/`;
  `owasp_agentic` present in articles 11 and 12; staleness measured in days
  and asserted by a test with a ceiling.

### P14. Remaining MEDIUM/LOW
F13b (dashboard missing from wheel), F15 (JS test is a drifted data copy —
per the standing rule it must import or verify against source, not copy),
F16 (superlinear scan: **diagnose before optimising**), F17 (README
mismatches), F18 (SPDX headers), F19 (dead `ci_heal.py`, 588 lines).

---

## PROJECTED RUBRIC MOVEMENT, with arithmetic

Ranges, not points. Assumptions stated. **These are JUDGEMENT, not
measurement**, and the Phase 7 independent scorer arbitrates.

Baseline (BASELINE.md §11): **52.3**, with a caveat I introduced an error
over and then caught.

> **SELF-CORRECTION, recorded rather than quietly fixed.** My first draft of
> this table carried Engineering craft at **90**, taken from the
> PROGRAMME.md rubric anchor. That is wrong: Phase 0 re-measured, and
> BASELINE's own aggregate arithmetic uses a craft contribution of **13.2**,
> which is a score of **88**. Carrying the embedded anchor instead of the
> measured value is precisely the measured-over-embedded error (principle 2)
> this programme exists to catch. Corrected below.
>
> Checking that also surfaced a defect in BASELINE itself: its craft row
> says "Hold at 90" while its arithmetic uses 88, so the baseline aggregate
> is **52.3 or 52.6** depending on which you read. Logged in BASELINE §11;
> **not resolved here**; Phase 7 arbitrates. The projections below use
> **88**, the value BASELINE's arithmetic actually uses.

| Dimension | Weight | Now | Projected | Basis |
|---|---|---|---|---|
| Detection efficacy | 25% | 38 | 40-46 | P7 fixes a constructed miss; P8 guards 183 patterns (**guarding is not improving** — it prevents silent regression, it does not raise precision); P9 measures recall for the first time. **Measuring a number does not improve it.** |
| Problem altitude | 20% | 40 | 40-42 | P13 only. No new governance gap addressed; P12 deferred. |
| Engineering craft | 15% | **88** | 88-90 | P2, P14 cleanups; offset by P8's volume of new fixtures. |
| Trust & integrity | 15% | 72 (working) | 78-84 | P1 closes a gate defect; P3 makes artefacts schema-valid; P4 and P5 remove two false public claims. **The largest honest movement in the plan.** |
| Regulatory currency | 10% | 85 | 85-88 | P13. |
| Delivered-value | 10% | 8 | **8** | **Unchanged. Principle 11: this moves only on artefacts that verifiably exist.** No in-repo work can move it. |
| Durability | 5% | 30 | 30-32 | Bus factor unchanged. |

**Arithmetic, low end:** 0.25(40) + 0.20(40) + 0.15(88) + 0.15(78) +
0.10(85) + 0.10(8) + 0.05(30) = 10.0 + 8.0 + 13.2 + 11.7 + 8.5 + 0.8 + 1.5
= **53.7**

**Arithmetic, high end:** 0.25(46) + 0.20(42) + 0.15(90) + 0.15(84) +
0.10(88) + 0.10(8) + 0.05(32) = 11.5 + 8.4 + 13.5 + 12.6 + 8.8 + 0.8 + 1.6
= **57.2**

**Projected 53.7 to 57.2, from 52.3.** A gain of **1.4 to 4.9 points** for
substantial work, and that is the honest shape: **most of this plan removes
false claims and unguarded surfaces rather than adding capability.** The
programme's own honest ceiling is ~70-72 and is gated on human actions no
in-repo work can perform.

Both lines recomputed after the craft correction; if you recompute and get
54.0/57.5 you are reading the pre-correction draft.

**Anyone reading a bigger number out of this plan has made an arithmetic
error.** Projection above ~72 is defined as a signal to re-check.

---

## WHAT THIS PLAN DELIBERATELY DOES NOT DO

- **No LLM tier in Phase 5** (P12), on the evidence, not on preference.
- **No F9 fix without a reproduction** (P11).
- **No F8 inline fix** (P10) — if reproduced it returns to Phase 3.
- **No public-surface change without approval** — P4, P5, P6 and P3's docs
  all need it, and PACK-1.5b is the vehicle.
- **No claim that guarding 183 patterns improves detection.** It prevents
  silent regression. Saying otherwise would be metric gaming.
