# Regula Handover

Rewritten 28 July 2026, end of session 3. Supersedes all earlier versions of
this file. Tracked (owner decision 1); `.claude/handover.md` is superseded
history and remains untracked.

**Read this sceptically.** This programme has a documented history of
confident-but-wrong statements, and **session 3 produced five more of them
from me**. All were caught, all are recorded in §7 rather than deleted.
**Any number you did not personally measure is unverified.** Do not repeat a
figure from prose; re-measure it.

---

## 1. START HERE

**Branch `improvement/2026-08-programme`. NOT pushed** (no upstream; absent
from `git ls-remote --heads origin`). **`main` untouched** at `b5ac95c8`,
identical to `origin/main`. Nothing is public. Tree clean.

Re-measure before trusting anything:

```
git log --oneline main..HEAD | wc -l          # 42 at time of writing
git status --porcelain                         # expect empty
python3 -m pytest tests/ -q --collect-only     # 2,363
python3 scripts/claim_auditor.py --verify-facts # rc=0
python3 scripts/site_integrity.py              # rc=0
python3 scripts/cascade_count.py --check       # rc=0
```

A fresh session must, in order:

1. Read `docs/improvement/PROGRAMME.md` — the commissioning contract,
   verbatim. It is the specification this work is judged against.
2. Read `docs/improvement/STATE.md` — the resume file.
3. Read `docs/improvement/GATE-REVIEW.md` including its loop-2 addendum.
4. Re-measure per the block above.

**Do not commit to `main`. Do not push. Nothing reaches a public surface
without owner approval.**

## 2. WHERE THE PROGRAMME ACTUALLY IS

| Phase | Status |
|---|---|
| Phase 0 baseline | DONE (`BASELINE.md`) |
| Phase 1 code review | DONE (`CODE_REVIEW.md`, `fp_taxonomy.json`) |
| Phase 1.5 apparatus repair | DONE |
| **Phase 1.5b** | **LANDED** (`b2bb65a`, `ad1bfca`), partial — see §4 |
| **Phase 1.5c** | **NEXT. Not started.** Three defects, §5 |
| Phase 2 | **FAILED validation, loop 1 of 3** |
| Phase 4 | **FAILED hostile review, loop 2 of 3** |
| Phases 5-8 | NOT STARTED |

**Neither Phase 2 nor Phase 4 has passed its gate. The Phase 4 plan must not
be executed.** Both stopped deliberately with loops remaining; see §8.

## 3. THE QUEUE (owner-confirmed, do not reorder)

1. **1.5c** — three defects, three regression pairs, no auditor rewrite.
2. **Class 1** landing-page derivation, under the F14 guard in §6.
3. **Re-derivations at HEAD** under one written rule (Trust and Detection).
4. **The traces** — path-labelled, covering the 8 unexplained misses and the
   6-fixture divergence set.
5. **Plan revision** against `HOSTILE-REVIEW-LOOP2.md` §F and both loops'
   dispositions.
6. **Loop 3** in a fresh session with the closure-verification brief.

**P0 (docs/*.md gate coverage) stays parked behind 1.5c.** Extending a
gate's reach before repairing its sensitivity multiplies false confidence.

## 4. WHAT LANDED IN 1.5b, AND WHAT DID NOT

**Landed** (`b2bb65a`, `ad1bfca`): 83.5% provenance across **14** surfaces;
F20 version attribution corrected v1.7.4 → **v1.7.0** to match
`PRECISION.json`; the healthcare hypothetical reframed; **F23** two public
surfaces claiming 100% synthetic recall corrected; a per-location provenance
guard with two controls.

**Held, still open:**

- **§3 class 1** progress bars. Now unblocked by the owner; see §6.
- **§4.1 `41%`** unverified; **§4.3** 4 pairs untraced. Both under the
  class-2 bar: reproducible or externally cited, else annotate or correct.
- **The meta-description occurrence** on `blog-scanning-5-frameworks.html`,
  held for 1.5c by the pre-landing gate.

**The blog 4 pairs are RELEASED, VERIFIED-WITH-SOURCE.** See §7.4 — that
finding was mine and it was wrong.

## 5. PHASE 1.5c — SCOPE IS FIXED AT THREE DEFECTS

Owner: fence unchanged, three regression pairs, **no auditor rewrite**.
Lands **before P0** and before anything in Phase 5/6 publishes.

| Defect | Regression pair required |
|---|---|
| **F21** self-citation: a page's own canonical URL satisfies `paragraph_has_source()` | a claim sourced only by its own URL **must fail**; one with a genuine citation must pass |
| **F22** `claim_auditor.py:850` `if found_val < int(actual_str) * 0.5: continue` — any stale number below half canonical is silently skipped | a stale **1,100** against canonical **2,363** **must be caught** |
| **F24** the auditor derives precision from `PRECISION.json` only and cannot derive a recall figure at all | fix shape is a **committed canonical recall artefact** (fractions with path and gate condition, produced by the benchmark run) that the auditor verifies published fractions against; a compliant matching fraction passes, a bare or mismatched one fails |

`scripts/check_selfref_sourcing.py` already implements F21 detection and is
in use as the 1.5b pre-landing gate.

## 6. CLASS 1 — UNBLOCKED, WITH A GUARD

Replacement rule, **in order of preference**:

1. **Derived counts** computed from crosswalk data, site_facts pattern,
   test-backed ("4 of 7 requirements mapped").
2. **Qualitative tiers** where no honest denominator exists.
3. **Removal** where neither works.

**THE GUARD, and it is not optional.** F14 found the crosswalk **108 days
stale** with named gaps (`article_11` missing its Omnibus route;
`owasp_agentic` absent from articles 11 and 12). Therefore:

- **Any article on F14's known-stale list gets tier-or-removal, not a
  derived count**, until the crosswalk refresh lands.
- **Every derived count that publishes carries the crosswalk version and the
  date it was computed from.**
- **The derivation is scripted and test-backed** on the site_facts pattern.
  Never hand-computed.

**Locales:** changes that are purely numeric or structural, mirroring the
English disposition, land now. **Any new DE/PT-BR prose is held**, with
exact diffs presented for competent-speaker sign-off.

The real `regula gap` output is already captured in `PACK-1.5b.md` §3,
including the NOTE the site omits, which is the denominator disclosure.

## 7. MY OWN ERRORS THIS SESSION — all five

Recorded because the honesty requirement outranks how the record reads.

**7.1 The 8-of-14 table.** The pack claimed to cover *every* location of the
83.5% figure and listed **8**. The tracked total is **14**. The owner
approved a disposition on that table, so **approval was granted on
incomplete evidence** — logged as an approval-scope deviation in STATE.md.
The six missed included `site/index.html`, the landing page.

**7.2 The 58-vs-34 scope figure.** I reported 58 ungated docs files; the
tracked, publishable figure is **34**. I counted untracked local scratch —
**one section after correcting a reviewer for exactly that conflation**.

**7.3 A gate narrower than the standard, in the test written to close one.**
My provenance guard enumerated correctly but checked at file level, so a
bare figure passed if the disclosure sat far away. Upgraded to per-location;
it immediately found 4 more real gaps, plus a 5th after the first fixes.

**7.4 The blog "discrepancy" that never existed.** I reported that
`blog-scanning-10-ai-apps.html` did not reconcile with tracked scan data,
called it *the single most serious item in the pack*, and escalated it. **The
post's own methodology note discloses the 665 figure**, names both scans with
versions and dates, and explains the difference. I had not read that far into
the post. Cost: one escalation instead of a false correction to a correct
post — **because it was quarantined rather than acted on**.

**7.5 R2 closed as indeterminate too early.** I said no committed artefact
could settle 389 vs 409. The owner named two stores I had not checked. The
v1.7.0 tag and the 23 April tree both settle it: **387**, by two independent
methods. Neither published number was derivable under any unit.

**Plus a near-miss that was not a claim error but a process one:** cascading
a count by global text replace rewrote a package URL hash path and an
integrity `size` field inside `uv.lock`. Reverted before commit. `git diff`
caught it; nothing else would have.

## 8. WHY BOTH GATES ARE STOPPED, DELIBERATELY

**Phase 4, loop 2 of 3: FAIL.** 9 CLOSED, 12 PARTIALLY CLOSED, 3 COSMETIC,
18 new MAJOR. All three closures I pre-flagged as likely cosmetic **failed on
merit** — self-flagging is not self-correcting.

**Phase 2, loop 1 of 3: FAIL.** Citation layer passed well; the failure is in
inference. I published a **falsified claim** (an ICSE 2026 single-annotator
first pass that neither ICSE 2026 paper performed) as the load-bearing leg of
a recommendation to relax the programme's own annotator bar. Struck; κ ≥ 0.6
floor restored; three annotators retained.

**The last loop is not being spent under context pressure.** Revising and
immediately re-reviewing is how the loop-1 and loop-2 errors were introduced.
The cap is a ceiling, not a quota.

## 9. MEASURED FACTS WORTH CARRYING FORWARD

**Recall, and it must never be quoted bare.** Scanner path (`regula check`,
what a user runs): **10/30 default, 14/30 domain-declared, 19/30 with both
gates satisfied**. Classifier path (`classify()`, what
`benchmarks/synthetic/run.py` measures): **16/30**. **The two disagree by six
fixtures on the same corpus** — that is F8, quantified for the first time.
**Every published recall fraction labels path and gate condition.**

**The diagnosis is the durable output, not the number.** Of 20 default-scan
misses: **13 opt-in domain suppression** (9 of 17 high-risk domains are
suppressed by default), **4 AI-indicator gate**, **3 genuine pattern gaps**.
**17 of 20 are gates, not patterns.** Pattern work addresses 3 of 20.

**8 fixtures still miss with patterns matching and both gates satisfied.**
Cause not determined, not guessed. These plus the 6-fixture divergence set
are the trace targets, likely overlapping.

**The projection is WITHDRAWN.** It was computed from a Trust value the same
document forbade using, quoted the favourable end of an unresolved baseline,
and silently fixed craft at 88 while claiming indeterminacy. **No movement
figure until Trust and Detection are re-derived at HEAD under one written
rule.**

**BASELINE §11 contradicts itself:** craft row says "Hold at 90", arithmetic
uses 88, so the baseline is **52.3 or 52.6**. Unresolved by design; Phase 7
arbitrates.

## 10. STANDING RULES (owner-set, non-negotiable)

- **Never suppress or dismiss a security alert.** Leave false positives open
  and explain them.
- **No owner personal information in the repo, of any kind.**
- **No em dashes** in repo copy, commits, docs or replies.
- **All three locales in the same change**; new DE/PT-BR prose needs
  competent-speaker sign-off.
- **Region pages `site/regions/*.html` are GENERATED** from
  `content/regulations/*.py`. `uae.html` and `regulations.html` are
  hand-maintained exceptions.
- **Run the control before reporting a result.** A blank gate is not a green
  gate; use `PIPESTATUS` or redirect to a file.
- **Stdlib-only core, offline by default, no telemetry.** Optional networked
  features are extras, off by default, with an ADR. Stdlib-only is a
  **runtime-core** constraint, not a CI constraint.
- **Never commit to `main`; no force-push; no history rewrite.**
- **Stage explicitly; no `git add -A`** (`.claude/rules/git.md`).
- **Count propagation uses `scripts/cascade_count.py` only.** A manual bulk
  numeric edit is now a rule violation, not a risk.
- **Mid-landing expansion** is permitted only when (a) it applies an
  already-approved disposition class to newly discovered instances, or (b)
  leaving it would publish a known-false claim through the same commit
  window. Flag every expansion in the commit body and the report; anything
  involving discretionary framing goes for ratification.
- Owner deliverables go to the Downloads folder on the Windows side of the
  WSL mount.

## 11. LOADED RULES — read these, they are the compressed lessons

`.claude/rules/measurement.md` is the highest-value file in the repo for a
new session. Nine rules, each paid for by a wrong number:

1. Measure in place. 2. One variable at a time. 3. Never trust a number
produced by a copy, including your own earlier one. 4. Require positive proof
the code path executed. **4b.** Verify a file is tracked before calling it a
published surface. **4c.** Any completeness claim must be produced by
enumeration, never by hand. **4d.** Enumeration picks the files; it does not
license a blind replace. **4e.** Before asserting two artefacts contradict,
read both in full. 5. Passing a gate is not evidence of meeting a standard
when the gate tests something narrower.

Also `.claude/rules/git.md` (explicit staging, errata discipline) and
`.claude/rules/tests.md`, `quality-standards.md`, `python-scripts.md`,
`site-html.md`, `regulatory-content.md`.

## 12. OPEN OWNER ITEMS

1. **1.5b residuals**: R1 — the v1.6.1 raw output is not committed though the
   post says both versions are (annotation fix). **R2 sub-item still open** —
   the **330** figure for v1.6.1 cannot be settled from a tag because **no
   `v1.6.1` tag exists** (only v1.6.0 and v1.6.2).
2. **Private remote for `getregula-internal/`** (`OWNER_ACTIONS.md` item 9).
   It is a local-only git repo with a `pre-push` hook; history but one disk.
3. `OWNER_ACTIONS.md` items 1, 2, 3, 5, 7 unstarted. Item 4 closed; item 8
   answered as F21.
4. **Rater recruitment** remains the binding constraint on the corpus, and
   the validator's ruling means it **cannot** be relaxed to two raters on the
   evidence offered.

## 13. WHERE THINGS ARE

**Tracked, `docs/improvement/`:** `PROGRAMME.md` (contract) · `STATE.md`
(resume) · `BASELINE.md` · `CODE_REVIEW.md` · **`HANDOVER.md`** (this) ·
`PHASE0_VERIFICATION.md` · `OWNER_ACTIONS.md` · `COMMIT_ERRATA.md` ·
`PACK-1.5b.md` · `RESEARCH-CARDS.md` · `PLAN-PHASE4.md` ·
`PLAN-PHASE4-v2.md` · `HOSTILE-REVIEW-DISPOSITIONS.md` ·
`HOSTILE-REVIEW-LOOP2.md` · `GATE-REVIEW.md` · `fp_taxonomy.json` ·
`measure_pattern_reach.py`.

**Tracked elsewhere:** `docs/dpvcg-contribution-draft.md` ·
`benchmarks/headtohead/RESULTS-synthetic-2026-07-28.md` and
`RESULTS-synthetic-v2-2026-07-28.md` + raw JSON ·
`benchmarks/synthetic/` (manifest v2.0, 38 fixtures) ·
`scripts/cascade_count.py` · `scripts/check_selfref_sourcing.py` ·
`.claude/rules/*.md` · `.claude/commands/*.md` ·
guards: `tests/test_precision_provenance.py`, `test_cascade_count.py`,
`test_collection_integrity.py`, `test_claim_auditor_coords.py`,
`test_claim_auditor_percent.py`, `test_claim_quarantine.py`,
`test_packaged_data.py`, `test_published_count_manifest.py`.

**Outside the repo, deliberately, `getregula-internal/`** (local-only git
repo, no remote, `pre-push` hook refuses): `research-sweep-2026-07.md` ·
`moat-programme-2026-07.md` · `competitive-intelligence-2026-07.md` ·
`moat-research.md` · `originals-pre-redaction/` · `README.md`.
**Why:** the repo is public; these are competitive and commercial strategy.
**Calibration: competitor names were NOT redacted** — the repo already names
its comparison set publicly. What is held back is positioning work.

## 14. THE ONE THING TO UNDERSTAND

The programme is further from the Phase 4 gate than it looked three sessions
ago, and **that is the checks working**. Two independent subagents failed my
work; a per-location guard failed my own guard; a cascade tool failed its own
first three designs; and the single most serious finding I escalated turned
out not to exist.

Every one of those was caught by an instrument or a charter, not by
confidence. **Keep the distance honest and keep the controls in front of the
claims.**
