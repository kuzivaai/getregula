# GATE REVIEW — two decisions, one sitting

28 July 2026. Branch `improvement/2026-08-programme`, not pushed, `main`
untouched, tree clean, nothing on a public surface.

> **HEADLINE, STATED FIRST BECAUSE IT IS THE POINT.**
> **Both independent subagents returned FAIL.** The RESEARCH VALIDATOR
> failed Phase 2. The HOSTILE REVIEWER failed the Phase 4 plan. Both were
> right. **Neither Phase 2 nor Phase 4 has passed its gate, and the Phase 4
> plan must not be executed.**
>
> Only **one** of the two decisions below is actually ready for you.

---

## DECISION 1 — the 1.5b pack. READY.

`docs/improvement/PACK-1.5b.md`. Built, held, **nothing applied**.

**What approval authorises:** correcting 5 of 8 locations of the 83.5%
claim (worst: a bare number on `site/about.html:132`) plus the F20 version
split; fixing F21 in the auditor; replacing the landing-page mock-up with
real derived output across EN/DE/PT-BR; reframing the healthcare
hypothetical.

**What it explicitly does NOT authorise, and why:**

- **`blog-scanning-10-ai-apps.html`, 4 pairs.** The post publishes 553
  findings with AI security at 7.4%. The repo's own tracked scan data, and
  that data's own tracked README, say **665** and **33.8%**. I did not
  determine the cause and did not guess. **OWNER-INPUT: was that post
  written from a scan other than `blog_scan_2026_04`?** Until answered,
  those pairs stay quarantined. A "verified-with-source" label must not go
  on numbers that contradict the source.
- The `41%` claim in the other post (unverified), and 4 pairs in §4.3 not
  yet individually traced.

**Two things you must see before approving §3**, because they change the
landing page's face: the real numbers are **worse** (headline 42/100
becomes 9%), and the real command emits a NOTE saying the score measures
presence of documentation and cannot offset scan findings — **the site
omits that entirely, and it is the denominator disclosure.**

**OWNER-INPUT on §3:** which fixture to feature, and DE/PT-BR sign-off. Any
fixture is acceptable **except one chosen because it scores well.**

---

## DECISION 2 — the Phase 4 plan. NOT READY. Do not approve.

`docs/improvement/PLAN-PHASE4.md`, with
`docs/improvement/HOSTILE-REVIEW-DISPOSITIONS.md`.

**HOSTILE REVIEWER verdict: FAIL. 16 MAJOR, 8 MINOR. All 24 accepted, none
rejected.** Loop **1 of 3**. The revised plan requires a loop-2 review that
**has not been run**.

**The four blocking objections:**

1. **P2 is infeasible as written**, and the repo already contains the
   silently-degrading test it would reproduce.
2. **P8's acceptance criterion requires zero assertions.** MEASURED:
   `measure_pattern_reach.py:85` counts a pattern "guarded" if its string
   appears anywhere in `tests/` or the fixture tree. My criterion was
   satisfiable by pasting 134 strings into one file. **My stated
   anti-gaming control was decorative** — it policed fixture plausibility
   while the criterion required no assertion.
3. **P5 removes one false claim and installs a subtler one** by being
   ordered before P10.
4. **The baseline is stale against HEAD**, so the projected gain
   double-counts work already landed.

**Plus one live defect the plan had no item for.** MEASURED at HEAD:
`docs/architecture.md:53` (tracked) publishes `1,223 tests (pytest
--collect-only)`; the canonical count is **2,349**; `architecture.md` is
not in the auditor's file list; `--verify-facts` returns **rc=0, "all
published numbers match"**. A wrong number, attributed to a command, on a
tracked surface, with the drift gate green. Promoted to Tier 0.

*(One correction to the reviewer: it also cited `docs/FULL_REVIEW.md`, which
is gitignored and untracked, so that half is not a published surface. And
its jsonschema claim was factually wrong — it is installed, 4.26.0 — though
its structural point stands, since the package is in no dependency list and
the test degrades silently without it.)*

---

## PHASE 2 — also failed. RESEARCH VALIDATOR verdict: FAIL.

Two of four conjunctive pass criteria not met. Loop **1 of 3**.

**The citation layer passed and passed well:** all 11 arXiv IDs and 4 DOIs
resolve to the claimed works, every peer-review status is correct, and all
**twelve** numbers the validator spot-checked are verbatim-accurate. The
three flagged corrections all hold, one stronger than claimed.

**The failure is in inference, and one item is serious.**

> **I published a falsified claim.** My cards asserted that the ICSE 2026
> paper "ran its initial full pass with a single annotator", and used it to
> argue a cheaper path to credibility that would partially unblock rater
> recruitment. **Neither ICSE 2026 paper did that.** It came from a
> retrieval subagent and I published it without verifying it — the exact
> failure the standing rule on subagent output exists to prevent. **It was
> the load-bearing leg of a recommendation to relax this programme's own
> quality bar.** Struck.

Also accepted: I miscounted "two of four" kappa values below 0.7 (it is
**three of four**, and that error ran *against* my own recommendation); the
3→2 annotator reduction was contradicted by **C1 in my own document**,
which records PrimeVul using three; and I committed an unflagged
population transfer of exactly the type I police elsewhere.

**Corrected position now in the cards:** dropping the Fleiss κ ≥ 0.7
*threshold* is earned. **A κ ≥ 0.6 floor is restored. Three annotators are
retained.** Any later reduction must be recorded as a resource decision,
not a measured one.

A **fourth** citation-identity defect was found in my own document by the
validator: card C1 is headed "PrimeVul", but that is the benchmark; the
paper is "Vulnerability Detection with Code Language Models: How Far Are
We?". Same defect at B3, B4, B5.

---

## WHAT DID PASS, AND IS BANKED

| Item | Evidence |
|---|---|
| Full suite green after the F1 rebind | **2,349 passed**, rc=0, 23m26s; executed count equals collect-only count |
| Owner decisions 1, 2, 4 executed | carve-out ratified; `getregula-internal/` a local-only repo (no remote, `pre-push` guard); `measurement.md` loaded |
| **F21 found and measured** | auditor sweeps `<meta>`; all 27 claims pass because a page's own canonical URL satisfies `paragraph_has_source()`; 370 total reconciles to the gate |
| **Synthetic baseline run** | prohibited 5/5, high-risk **4/5**, 0 high-risk firings on 3 negatives; raw output committed |
| Two BASELINE defects found | craft row says "Hold at 90" while its arithmetic uses 88 (52.3 **or** 52.6); craft evidence cites the stale 2,849 |

**The synthetic run's negative result is the most valuable single output of
this session.** `highrisk_employment.py`, hand-built as an unambiguous
Annex III case, classifies as `ai_security` only. On a corpus whose ground
truth is true by construction, that is a recall failure. F11 records that
recall had never been measured; this is the first number, and it is a miss.

**It must not be generalised.** Five fixtures is not a recall estimate.

---

## PROJECTED MOVEMENT, with arithmetic and the reviewer's counter

Baseline: **52.3** (or 52.6 — BASELINE contradicts itself; unresolved,
Phase 7 arbitrates).

| | My plan (corrected) | Reviewer's counter |
|---|---|---|
| Low | **53.7** | **52.9** |
| High | **57.2** | **54.5** |
| Gain | +1.4 to +4.9 | **+0.6 to +2.2** |

**I accept the reviewer's counter as the more defensible range.** Its two
reductions are both arguments I made myself and then failed to apply:
Detection cannot move +8 when I wrote "guarding is not improving" in the
same row, and Trust cannot move +12 when the plan touches one of the six
legs under it, two are already fixed, and three are untouched.

**Delivered-value stays at 8 in every version.** Principle 11: it moves
only on artefacts that verifiably exist, and no in-repo work can move it.

---

## ESCALATIONS

1. **Phase 4 failed hostile review at loop 1 of 3. Loop 2 has not run.**
   I am **not** iterating to a PASS in this session. Producing a revised
   plan and declaring it passed without re-review is precisely the silent
   bar-lowering the loop cap exists to prevent.
2. **Phase 2 failed validation at loop 1 of 3.** Five specific repairs are
   named; four are applied to the cards, the fifth (per-item domain-shift
   notes for B3, C1, C2, C3, C4) is not.
3. **A falsified research claim was published to a tracked document and
   survived until an independent agent caught it.** The retrieval-agent
   verification discipline needs strengthening beyond spot-checking two
   items, which is what I did.
4. **`blog-scanning-10-ai-apps.html` contradicts the repo's own tracked
   evidence.** Owner input required.

## DEVIATIONS

- **The head-to-head did not run and could not.** All three competitor
  adapters raise by design; none of the tools is installed. What ran is a
  Regula-only synthetic baseline, declared as a corpus deviation with
  written justification. Blocker 2 of the pre-registration is untouched.
- **The sensitivity carve-out** (ratified this session) remains a deviation
  from the literal relocation instruction, now closed as approved.

## STANDING OPEN ITEMS

- **F1 watch item: OPEN.** Unreproduced transient in the custom runner. The
  green pytest run is **not** evidence about it — different harness.
- **Owner decisions:** 1.5b pack (§Decision 1); private remote for
  `getregula-internal/` (OWNER_ACTIONS 9).
- **OWNER_ACTIONS** 1, 2, 3, 5, 7 unstarted. Item 4 closed, item 8 answered
  as F21.
- **Rater recruitment** remains the binding constraint on the corpus, and
  the validator's ruling means it **cannot** be relaxed to two raters on
  the evidence I offered.

---

## THE HONEST SUMMARY

This session produced one deliverable ready for decision (the 1.5b pack),
one measured negative result worth more than most positives (the high-risk
miss), one new HIGH finding (F21), and **two independent FAIL verdicts on
my own work, both of which I accept.**

Three of the defects found this session were **mine, in documents I had
already committed**: a falsified research precedent, a gameable acceptance
criterion whose stated control was decorative, and a rubric anchor carried
from the programme text instead of the measurement. Two were caught by
independent agents; one I caught myself.

**The honesty of this review outranks the flattery of the result.** The
result is that the programme is further from the Phase 4 gate than it
looked at the start of the session, and the reason is that the checks
worked.
