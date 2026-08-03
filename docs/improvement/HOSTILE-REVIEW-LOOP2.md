# HOSTILE REVIEWER loop 2 — verdict, dispositions, and the escalation

**Verdict: FAIL.** Loop **2 of 3**. Closure tally on loop 1's 24
objections: **9 CLOSED, 12 PARTIALLY CLOSED, 3 COSMETIC**, plus **18 new
MAJOR** and 9 new MINOR.

Charter per the owner's amendment: inputs were the revised plan, loop 1's
objection list with per-objection dispositions, CODE_REVIEW and BASELINE;
added task was to verify each accepted objection is actually closed and to
raise cosmetic closures as new MAJOR. It did exactly that.

---

## §A. VERIFIED BEFORE ACCEPTING

Three load-bearing claims re-measured personally. **All three hold
exactly.**

| Claim | Measured at HEAD | Verdict |
|---|---|---|
| `claim_auditor.py:850` skips any stale number below 50% of canonical | `if found_val < int(actual_str) * 0.5: continue` | **CONFIRMED** |
| "58 docs files" is wrong | 70 on disk, 48 tracked, **34 tracked outside `docs/improvement/`** | **CONFIRMED** |
| `CHANGELOG.md` omitted from P4's list | 3 occurrences: `regula[all]` ×2, `regula[signing]` ×1 | **CONFIRMED** |

The reviewer also reproduced the projection arithmetic exactly (52.85 and
54.5) and located the error in the **inputs**, not the multiplication.

---

## §B. THE THREE COSMETIC CLOSURES — all accepted

I pre-flagged three closures as likely cosmetic and told the reviewer not
to let the flag earn them a pass. **All three failed on merit.**
Self-flagging is not self-correcting, and it was right to say so.

1. **P0's `docs/improvement/*` exclusion.** Blanket, permanent and
   unscoped, in a directory that **is** tracked and published and that
   carries 7 live instances of the harmful `pip install regula[` string.
   The per-instance mechanism I mandate for every other file
   (`load_quarantine()` / `is_quarantined()`, already built) is exactly
   what should be used here. **Accepted: sweep the directory, quarantine
   the historical-quote instances with per-entry reasons.**
2. **P7's Gate 1 "disclosure".** Recall stays at 33%; only awareness
   changes. I justified leaving 9 of 17 domains suppressed as
   "precision-protecting" and cited no measurement. The only measurement
   in the record cuts the other way: BASELINE §6 records high-risk
   precision of **0.333 (tp=2, fp=4, n=6)** on the **post-gating** subset —
   the suppression is already applied there and precision is still 33%.
   **Accepted: measure the precision cost of un-suppressing on both
   corpora, then decide. The harness exists.**
3. **P9 dropping the real-world recall half.** Closes no objection —
   neither 14 nor 20 asked for it. It is an independent scope cut
   presented under their heading. **Accepted.**

---

## §C. THE MOST SERIOUS NEW FINDINGS

**N10 — extending the gate's reach before its sensitivity.** The 50% floor
means P0 would propagate a known blind spot across 34 more files. My own
control clears the floor by a 2% margin: had `architecture.md` said 1,100
rather than 1,223, P0 would have shipped and the gate would still have
passed it. **This is measurement rule 5 applied to my own plan, and it
demotes P0 from "lead Tier 0 item" to "blocked until the floor is fixed".**

**N1 — the third wrong number for the same quantity.** I asserted 21,
enumerated a list summing to 20, and the measured figure is 23. Objection
1's whole point was that the number was unverified. **The count must be
produced by the test, not asserted in prose.** That is now the criterion.

**N11 + n4 — the projection was computed from a number I forbade using**,
quoted the favourable end of a range I had acknowledged, and silently
resolved a baseline I was calling indeterminate. **The projection is
withdrawn.** No movement figure is published until Trust and Detection are
both re-derived at HEAD under one rule.

**N15 — a dependency running backwards through my own tiers.** P16's text
requires it to land *before* P8; P16 is Tier 3 and P8 is Tier 2. Two of the
five promotions I wrote "I agree with" were not made.

**N2 — P2 would red CI as written.** jsonschema is in no dependency list;
CI installs a hardcoded inline list; my acceptance was hard-fail only.

**N19, N20, n5-n8 — missing items**, each traced to a CODE_REVIEW or
BASELINE section: the never-executed drifted `test_questionnaire_scoring.js`
(§8.4), three false README claims (§7.5) sitting outside a Tier 1 whose
stated purpose is user-facing trust, `owasp_agentic` absent from two
articles while "13 frameworks" is enforced as canonical (§4), and the
n=6-vs-n=24 high-risk FP scope (§1.1).

**N17 — the plan is not reviewable against its own charter.** Eleven
findings referenced by bare F-number and one item deferred to an external
document, none of which are in the four permitted inputs. The reviewer
could not verify Tier 1 or Tier 3 coverage at all. **That is my defect, not
its.**

---

## §D. WHAT I CORRECTED IMMEDIATELY

In `PLAN-PHASE4-v2.md`, the verified factual errors only:

- P0's scope: **58 → 34**, with the tracked/untracked conflation named.
- P0: the 50% floor added as a **blocking precondition**.
- P4: product surface **21 → 23**, `CHANGELOG.md` added, and the count
  moved from prose into the acceptance criterion.
- The **projection withdrawn** entirely, with all four reasons recorded.

**I did not attempt a full loop-3 revision.** See below.

---

## §E. ESCALATION — the loop cap, and why I am stopping at 2

PROGRAMME.md principle 8 caps review cycles at 3. **This is loop 2 and it
failed.** One loop remains.

**I am not spending it in this session.** The defects loop 2 found are
substantive design errors — a gate extended before its sensitivity is
fixed, an acceptance that breaks CI, a dependency inverted through the tier
order, a projection derived from a disallowed input. Fixing those properly
is real work. Revising under context pressure and immediately re-reviewing
is how the errors in loops 1 and 2 were introduced in the first place: in
both rounds I produced a wrong number for a quantity I had just been told
was wrong.

**Burning the last loop on a rushed revision would convert a real quality
gate into a formality.** The honest position is that the plan needs
substantive rework, then loop 3.

**Phase 4 remains NOT PASSED. The plan must not be executed.**

## §F. WHAT LOOP 3 MUST START FROM

1. Fix `claim_auditor.py`'s 50% floor and the delete-a-claim-passes hole
   **before** P0 widens scope.
2. Re-derive Trust and Detection at HEAD, then republish a projection.
3. Resolve the baseline: craft at 88 forces 52.3. Say so or leave craft
   open in the table.
4. Give P2 three separate acceptance criteria and name where the jsonschema
   declaration lands plus the two CI install lines.
5. Reorder Tier 0 explicitly (P-SPDX → P2 → P3; P-REPRO day one) and move
   P16 ahead of P8.
6. Inline a one-line description per F-number, or amend the reviewer's
   input list. The plan must be reviewable from its stated inputs.
7. Add items for §8.4, §7.5, §4 and §1.1.
