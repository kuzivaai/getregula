# Phase 4 — implementation plan, revision 2

28 July 2026. Supersedes `PLAN-PHASE4.md`, which stands as the record of
what loop 1 reviewed. **Not approved. Loop 2 of 3.**

**Every one of loop 1's 24 objections was accepted.** Dispositions are in
`HOSTILE-REVIEW-DISPOSITIONS.md`; this document is what they produced.

Two things changed the plan more than any single objection:

1. **The reviewer's reprioritisation ruling**, which I agree with: Tier 0
   is the right place to spend a solo maintainer's time; **Tier 2 is where
   the disproportion is.**
2. **The expanded recall measurement** (`RESULTS-synthetic-v2-2026-07-28.md`),
   which arrived after loop 1 and independently destroys P8's rationale.
   Default-scan high-risk recall is **33%**, and **17 of 20 misses are
   gates, not patterns.** Writing fixtures for 134 regexes would address
   **3 of 20**.

---

## TIER 0 — the instrument

### P0. NEW. `docs/*.md` is outside the drift gate (amendment 4 + objection 11)

**The instance and the class, separated.**

**Instance, MEASURED at HEAD:** `docs/architecture.md:53` is tracked and
publishes `# 45 test files, 1,223 tests (pytest --collect-only)`. Canonical
is **2,349**. The file is not in the auditor's list.
`--verify-facts` returns **rc=0, "all published numbers match"**. A wrong
number, attributed to a command, on a tracked surface, with the gate green.

**Class, and it needs an assigned home rather than floating** (Phase 0
finding 6): **58 `docs/*.md` files are swept by no gate.**

**The decision, taken here rather than deferred. EXTEND COVERAGE.**

- **Acceptance:** the auditor's file list is replaced by a rule that
  includes `docs/**/*.md`, with an explicit, commented exclusion list.
  `--verify-facts` fails on `architecture.md` before the fix and passes
  after. Newly surfaced findings each get a disposition **or** a
  quarantine entry with a reason; the count is recorded.
- **Reasoned exclusions, named now so the list is not a dumping ground:**
  `docs/improvement/*` (the programme's own finding record, which quotes
  wrong numbers *as findings* — sweeping it makes the gate fail on its own
  evidence, which is objection 1's failure mode); generated artefacts
  already gitignored.
- **Tests first:** a test asserting `architecture.md` is in scope and that
  the exclusion list is exactly the commented set.
- **Rollback:** revert; the list is data.
- **Why extend rather than exclude:** the alternative is recording that 58
  documentation files may carry any number at all. Regula's differentiator
  is that its numbers are gated. An exclusion would be honest only if
  paired with a public statement that docs are ungated, and that statement
  is worse than the work.

### P1. F21 — self-referential URLs, and the other two loopholes (objection 12)

- **Acceptance:** `paragraph_has_source()` no longer returns True on (a) a
  bare `see`, (b) a bare `ref`, or (c) a URL that is the page's own
  canonical/alternate/og:url. Control test with **both** a positive and a
  negative case. Newly surfaced findings capped at a stated number, each
  quarantine entry carrying a reason.
- **Already built:** `scripts/check_selfref_sourcing.py` implements the
  detection for the (c) case and is in use as the 1.5b pre-landing gate.
- **Expect the finding count to rise. That is the gate working.**

### P2. Schema validation, done properly (objections 2, 3, 24)

- **jsonschema is a declared test-only dev dependency.** MEASURED: it is
  installed here (4.26.0) but appears in **no** dependency list and there
  are **no `requirements*.txt` files at all**, so
  `tests/test_evidence_format_v1.py:97` degrades to a stub on a clean
  checkout. **Stdlib-only is a runtime-core constraint, not a CI
  constraint.**
- **Acceptance:** the test **hard-fails** when jsonschema is absent rather
  than falling back; schemas are **vendored snapshots** with source URL,
  licence and fetch date (mirroring `scripts/dpv_data/`, `scripts/eli_data/`),
  **not fetched at test time**, because fetching breaks offline-by-default.
- **Widened to `site_integrity.py`** (0% covered, and wired as a merge
  gate at `.github/workflows/site-integrity.yml:29`) and
  `claim_auditor.verify_facts()`/`main()`.
- **Depends on P-SPDX below**, since vendoring third-party files into a
  repo with zero SPDX headers is the wrong order.

### P3. F4 — CycloneDX ML-BOM schema failure. Unchanged, depends on P2.

### P-SPDX. F18 promoted out of the remainder bucket (objection 19)

`pyproject.toml:13` declares a composite licence; **0 of 119 files carry an
SPDX identifier.** P2 vendors Apache-2.0 and OASIS files into that tree.
**Headers land before vendoring.**

### P-REPRO. F9 reproduction attempt, moved into Tier 0 (objection 21)

**Gating is not deferring.** The repro is two directories, one identical
filename, two runs. Attempt it on day one: if it does not reproduce it is
downgraded at near-zero cost; if it does, a cross-project provenance leak
that defeats `--scope` outranks most of this plan. **No fix may be written
before the repro exists.**

---

## TIER 1 — user-facing trust

### P4. F2 — `doctor` sends users to a stranger's package (objection 1)

- **Criterion re-derived against the product surface.** MEASURED: `pip
  install regula[` returns **11**; the `regula[` form returns **30 across
  17 files**; neither is the 18 the old plan asserted. Excluding
  `docs/improvement/*`, the product surface is **21 occurrences** across
  `scripts/{doctor,pdf_export,signing,conform,timestamp,cli}.py`,
  `README.md`, `docs/MODEL_CARD.md`, `docs/evidence-pack-guide.md`,
  `site/llms-full.txt`, `.claim-allowlist`,
  `tests/test_manifest_timestamp.py`.
- **The grep test must exclude the finding record**, or it goes red on the
  documents that describe the defect and gets deleted.

### P5. F3 — scope narrowed to what is known (objection 10)

- **Docs change is limited to the install-path fact:** the `[ast]` extra is
  absent on a default install, so tree-sitter is not present.
- **The per-command mechanism claim waits for P10.** If `regula check`
  reaches no AST engine at all, "JS/TS is regex-only" implies Python is
  not, which would be a new false claim.
- **Disclosure covers all 5 always-regex languages**, not just JS/TS.

### P6. 83.5% provenance + F20 + the never-re-measured figure (objection 22)

Deferred to PACK-1.5b, plus: **F20's version split is a third false public
claim** and a one-line fix, and **the precision figure was last measured
2026-04-25 against a 1.7.x build and never re-measured on 1.9.0.** Both get
items.

---

## TIER 2 — detection. **Substantially cut.**

### P7. The high-risk recall gates (REPLACES the old P7 and P8)

**Restated per objection 17:** prohibited holds at 5/5; high-risk moves
**10/30 → higher**; negatives hold at 0/3. The old "still 5/5" was a
preservation condition for a state that was already 4/5.

**The work is the gates, not the patterns.** From the expanded measurement:

- **Gate 3 first, because it is unexplained.** Eight fixtures whose
  patterns match, with domain declared and an AI indicator present, still
  miss. **Trace before touching anything.**
- **Gate 1 is a disclosure problem, not a code problem.** 9 of 17
  high-risk domains are suppressed by default for documented,
  precision-protecting reasons. **Acceptance: `doctor` or scan output
  states which categories are inactive and how to activate them.** A user
  scanning an employment codebase currently gets silence.
- **Gate 2:** decide whether a high-risk domain match without an AI
  indicator should warn rather than vanish.
- **3 genuine pattern gaps** (public benefits, predictive policing, remote
  proctoring) get patterns. **That is the whole of the pattern work.**

### P8. CUT from 134 fixtures to 17 (objections 4, 5, 6)

**Prohibited tier only.** Rationale, now doubly supported: CODE_REVIEW §1.2
says the high-risk failure space is context not pattern, and the recall
measurement shows patterns explain 3 of 20 misses.

**Acceptance rewritten, because the old one required no assertions.**
MEASURED: `measure_pattern_reach.py:85` is `rx.search(blob)` over
concatenated corpus text, so "guarded" meant "the string exists somewhere".
**The new criterion is assertion-based and restores the three properties
CODE_REVIEW §5.1 specified and the old plan dropped:**

1. each pattern has a positive fixture **asserted** to classify;
2. each has a **near-miss** asserted **not** to classify;
3. the test is **generated from the pattern dictionaries** so it cannot
   drift, and **fails when a new pattern lands without fixtures**.

Without (3) the fixtures buy no regression protection, which was the only
benefit claimed.

### P9. Recall — synthetic only (objections 14, 20)

- **Publish the synthetic figure with its N and construction method.**
  **Drop the real-world half**: it is blocked on recruiting humans for a
  tool with four users.
- **Li et al. is demoted to context, not evidence** (objection 14). I
  prohibited population transfer in P12 and then transferred 12.7%/70.9%/
  90.5% from SAST-on-CVE onto regex-based regulatory classification. The
  12.7 + 70.9 = 83.6 gap is unresolved and must be before citing.
- **Licence note rewritten when a corpus source is named**, not before.

### P10. F8 — reproduce; if confirmed, return to Phase 3. Unchanged.

---

## TIER 3

**P11 F9** — now Tier 0 (P-REPRO). **P12 semantic tier** — unchanged: not
built in Phase 5, gated on the corpus, no criterion in terms of 88.6% /
94-98% / 43.7%. **P13 crosswalk** — staleness becomes a **`doctor` warning
or scheduled issue, not a merge-blocking assertion** (objection 13); the
five reference files with no `verified_on` stamp are fixed first, or the
ceiling is vacuous on exactly those. **P15 NEW** (objection 15):
`_CONFIDENCE_BASE` shadowing, three `scan_files` defaults behind the
published 136-vs-222 discrepancy, **no `.gitignore` handling in the scan
path**, domain gating implemented twice. **P16 NEW** (objection 16): the 16
`_sha256` assertion sites that re-implement the hash as their own expected
value, fixed **before** P8 adds volume. **P14** F13b + widened wheel
assertion (objection 18), F15, F16 (diagnose before optimising), F17, F19.
**P-LANG** (objection 23): derive `count_languages()` rather than
hardcoding 8.

---

## PROJECTED MOVEMENT

**I adopt the reviewer's counter-projection**, not my own. Its two
reductions were arguments I made and failed to apply.

Baseline **52.3 or 52.6** (BASELINE §11 contradicts itself; unresolved).

| Dimension | Weight | Now | Projected |
|---|---|---|---|
| Detection efficacy | 25% | 38 | 39-41 |
| Problem altitude | 20% | 40 | 40-41 |
| Engineering craft | 15% | 88 | 88-90 |
| Trust & integrity | 15% | 72 (stale, objection 7) | 74-77 |
| Regulatory currency | 10% | 85 | 85-87 |
| Delivered-value | 10% | 8 | **8** |
| Durability | 5% | 30 | 30 |

**Low:** 9.75 + 8.0 + 13.2 + 11.1 + 8.5 + 0.8 + 1.5 = **52.85**
**High:** 10.25 + 8.2 + 13.5 + 11.55 + 8.7 + 0.8 + 1.5 = **54.5**

**+0.6 to +2.2.** Small, and honest: this plan mostly removes false claims
and closes gate defects.

**Trust's "Now" of 72 is itself stale** (objection 7) — two of its six legs
were fixed by `30cb981` and `093b839` and never re-derived. **Re-derive
before using it.**

---

## WHAT LOOP 2 MUST VERIFY

Per the amended charter, the fresh reviewer receives this plan, loop 1's
full objection list with dispositions, CODE_REVIEW and BASELINE, and must
**check whether each accepted objection is actually closed — raising any
closure it judges cosmetic as a new MAJOR.**

The three most likely to be judged cosmetic, flagged in advance rather than
hidden:

1. **P0's exclusion of `docs/improvement/*`** could be read as excluding
   exactly the files most likely to contain wrong numbers.
2. **P7's Gate 1 acceptance is a disclosure, not a fix.** The suppression
   stays; only its visibility changes.
3. **P9 "drop the real-world half"** removes the objection by removing the
   work, which is a legitimate scope decision or an evasion depending on
   whether the synthetic figure is presented as sufficient. It is not.
