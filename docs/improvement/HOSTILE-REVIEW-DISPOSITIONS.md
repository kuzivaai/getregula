# HOSTILE REVIEWER — verdict and written dispositions

**Verdict returned: FAIL. 16 MAJOR, 8 MINOR.** Loop 1 of 3.

PROGRAMME.md principle 7: the implementing agent may not overrule a
subagent verdict without a written disposition recorded in STATE.md. Every
objection is dispositioned below: **ACCEPTED** (plan changes) or
**REJECTED** (reason recorded). No objection is left unanswered.

**The verdict stands. Phase 4 has NOT passed its gate.** See §D.

Charter compliance: inputs were PLAN-PHASE4.md, CODE_REVIEW.md and
BASELINE.md only; the reviewer declared what it could not check.

---

## §A. FIRST, WHERE THE REVIEWER IS WRONG

Verified before accepting anything, per the standing rule that subagent
output is not verified by default.

### A1. Objection 2's factual core is wrong on this machine. Its structural point stands.

The reviewer states jsonschema "is installed nowhere" and therefore
`tests/test_evidence_format_v1.py`'s real branch "never runs and it passes
on a stub".

**MEASURED: `jsonschema` is installed, version 4.26.0.** The real branch
does run here. The claim that the test validates nothing today is false.

**But the reviewer's structural point survives and is accepted.** MEASURED:
there are **no `requirements*.txt` files at all**, and `jsonschema` appears
in neither `pyproject.toml` nor any workflow. So the test's behaviour
depends on whether the machine happens to have it. On a clean checkout it
degrades silently to the stub. That is a conditionally-degrading gate,
which is measurement rule 4, and it is a real defect.

**Disposition: ACCEPTED on substance, corrected on fact.** P2 gains: declare
the dependency, and make the test **hard-fail** when it is absent rather
than fall back.

### A2. Objection 11 is half-right, and the half that is right is serious.

- `docs/FULL_REVIEW.md` (the "~2,390 tests" source): **UNTRACKED**,
  gitignored at `.gitignore:104`. It is not a published surface. The
  reviewer treated it as in-repo. **That half is rejected.**
- `docs/architecture.md:53`: **TRACKED**, and says
  `# 45 test files, 1,223 tests (pytest --collect-only)`.

**MEASURED at HEAD:** canonical count **2,349**; `architecture.md` is
**not** in the auditor's `check_files`; `--verify-facts` returns **rc=0**,
"all published numbers match canonical counts — OK".

**So a tracked document publishes a wrong test count, attributes it to a
command, and the drift gate is green.** That is a live claim-integrity
defect with no plan item. **ACCEPTED, and promoted.**

### A3. The arithmetic objection was already fixed before the review landed.

The reviewer read the pre-correction plan and independently derived the
same error I had caught minutes earlier: craft carried at 90 from the
PROGRAMME anchor instead of the measured 88, gain overstated by 0.3 at both
ends, corrected range **1.4 to 4.9**. Fixed in `51ee8ad`, which also logged
BASELINE's own 90-vs-88 self-contradiction.

**Two independent routes to the same defect is the strongest signal in this
review.** Noted, not claimed as a pre-emption.

---

## §B. ACCEPTED — MAJOR

| # | Objection | Disposition |
|---|---|---|
| 1 | P4's "18 occurrences" is wrong and the grep test would go red on the finding record itself | **ACCEPTED.** Re-derive against the product surface with an explicit exclusion for `docs/improvement/`. A gate that fails on its own defect record is a gate that will be deleted. |
| 2 | jsonschema undeclared; test degrades silently | **ACCEPTED on substance** (see A1). Declare as a test-only dev dependency; make absence a hard failure. Stdlib-only is a **runtime core** constraint, not a CI constraint. |
| 3 | P2 says schemas are "fetched"; offline-by-default says vendor them | **ACCEPTED.** Vendor snapshots with source URL, licence and fetch date, mirroring `scripts/dpv_data/` and `scripts/eli_data/`. My licence note was wrong. |
| 4 | **P8's acceptance requires zero assertions** | **ACCEPTED, and this is the most damaging finding against my own work.** MEASURED: `measure_pattern_reach.py:85` is `rx.search(blob)` over concatenated corpus text, so "guarded" means the string exists somewhere. P8 was satisfiable by pasting strings into one file. My anti-gaming note policed fixture *plausibility* while the criterion required no *assertion*. **The control was decorative.** P8's criterion is replaced by an assertion-based one. |
| 5 | P8 drops 3 of 4 properties CODE_REVIEW §5.1 specified | **ACCEPTED.** Restore: near-miss negative assertion; generation from the pattern dictionaries so it cannot drift; failure when a new pattern lands without fixtures. Without the last, the fixtures buy no regression protection, which was P8's only claimed benefit. |
| 6 | P8 is wrong scale and cements a layer due for rework | **ACCEPTED.** Cut to the **17 prohibited** patterns. CODE_REVIEW §1.2 says the high-risk failure space is context, not pattern; pinning 117 high-risk fixtures makes the context rework harder. I quoted §1.2 to defer P12 and failed to apply it to P8. Also corrected: the tier scope is 134, not 183. |
| 7 | Baseline stale against HEAD; gain double-counts landed work | **ACCEPTED.** Trust=72 rests on legs already fixed by `35fc763` (percentages detectable) and `fd212fb` (count corrected). Re-derive Trust at HEAD before using it as a projection base. This is measurement rule 3 turned against my own plan. |
| 8 | Trust 78-84 indefensible at the high end | **ACCEPTED.** Of six legs, the plan touches one, two are fixed, three are untouched. Revised to **74-77**. |
| 9 | Detection 40-46 contradicts the plan's own reasoning | **ACCEPTED.** I wrote "guarding is not improving" and then projected +2 to +8. Revised to **39-41**. |
| 10 | P5 installs a subtler false claim by preceding P10 | **ACCEPTED.** If `regula check` reaches no AST engine at all, "JS/TS is regex-only" implies Python is not. Scope P5's docs change to the install-path fact only; the per-command mechanism claim waits for P10. Also widen the disclosure to all 5 always-regex languages, not just JS/TS. |
| 11 | Three test counts, gate green, no plan item | **ACCEPTED, promoted to Tier 0** (see A2 for the correction). New item **P0**. |
| 12 | P1 fixes 1 of 3 loopholes; acceptance permits quarantining all 16 | **ACCEPTED.** Fix `see`, `ref` and self-referential URL together per the whole-class standard. Cap quarantine additions and require a per-entry reason. |
| 13 | P13's staleness ceiling is a gameable gate | **ACCEPTED.** A calendar-triggered failing test has one available response when it goes red mid-task. Convert to a `doctor` warning or a scheduled issue-opener. Also: five reference files carry no stamp, so the ceiling would be vacuous on exactly those. |
| 14 | P9 commits the population-transfer error P12 prohibits | **ACCEPTED, and it is the sharpest catch in the review.** I prohibited transferring 88.6%/94-98%/43.7% and then transferred Li et al.'s 12.7%/70.9%/90.5% onto a different tool class as "external evidence". Demoted to context, not evidence. The 12.7 + 70.9 = 83.6 gap is flagged for resolution before citing. |
| 15 | CODE_REVIEW §7.3 has no plan item, incl. a live correctness defect | **ACCEPTED.** `_CONFIDENCE_BASE` shadowing, three `scan_files` defaults behind the published 136-vs-222 discrepancy, no `.gitignore` handling in the scan path, domain gating implemented twice. New item **P15**. |
| 16 | §8.3 weak-test census has no item; P8 adds volume to it | **ACCEPTED.** 16 assertion sites re-implement `_sha256` as their own expected value in a product whose differentiator is evidence integrity. Fix those before adding fixtures. New item **P16**. |

## §C. ACCEPTED — MINOR (condensed)

17 (P7's "still 5/5" is self-contradictory against a measured 4/5 —
restate as 4/5 → 5/5), 18 (widen the wheel assertion, not just F13b),
19 (promote F18/SPDX ahead of vendoring), 20 (rewrite P9's licence note
when a corpus source is named; add provenance for "the AdaTaint
principle"), 21 (attempt F9's repro in Tier 0 — gating is not deferring,
and it is two directories and two runs), 22 (version attribution is a
third false public claim, and precision was never re-measured on 1.9.0),
23 (derive `count_languages()` rather than hardcoding 8), 24 (widen P2 to
`site_integrity.py`, 0% covered and wired as a merge gate).

**All eight ACCEPTED.** None rejected.

## §D. WHAT THIS MEANS FOR THE GATE

**Phase 4 has NOT passed.** Sixteen MAJOR objections, all accepted, four of
them blocking: P2 infeasible as written, P8's criterion assertion-free, P5
ordered before P10, and a stale baseline that inflates the projected gain.

**This is loop 1 of the 3 permitted.** The revised plan requires a **loop 2
hostile review**, which has **not been run**. Under PROGRAMME.md principle
8 the honest position is that the plan is not approved and must not be
executed.

**I am not iterating to a PASS in this session.** Producing a revised plan
and declaring it passed without re-review would be exactly the silent
bar-lowering the loop cap exists to prevent. Recorded as an escalation.

**The reviewer's own summary judgement, recorded because it is the most
useful sentence in the review:** Tier 0 is the right place to spend a solo
maintainer's time; **Tier 2 is where the disproportion is** — 134 fixtures
against a layer due for rearchitecting, plus a recall measurement whose
load-bearing half is blocked on recruiting humans for a tool with four
users. Its recommended promotions: the `docs/*.md` gate gap, version
attribution, `.gitignore` handling in the scan path, the 16 hash assertion
sites, and F9's reproduction attempt.

**I agree with that reprioritisation** and it is the single largest change
to the plan.
