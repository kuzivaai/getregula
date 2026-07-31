# Regula Handover

## CURRENT RESUME POINT

This file is a historical narrative from session 4 and is not the current
state record. The single durable record of open and closed work is
`docs/improvement/LEDGER.md`; its section 6 records the measured current state.
Read the ledger before selecting work, then use the newest checkpoints at the
end of `docs/improvement/STATE.md` for chronological evidence.

Do not use the historical Git state or verification figures below as current
facts. Re-measure the tree before relying on any mutable count. This notice is
guarded by `tests/test_handover_continuity.py` so a future session cannot again
present the old instructions as the current entry point without a failing
test.

## HISTORICAL SESSION 4 HANDOVER

Rewritten 28 July 2026, end of session 4. Supersedes all earlier versions of
this file. Tracked (owner decision 1); `.claude/handover.md` is superseded
history and remains untracked.

**Read this sceptically.** This programme has a documented history of
confident-but-wrong statements, and every session so far has produced more
of them. All are recorded rather than deleted. **Any number you did not
personally measure is unverified.** Do not repeat a figure from prose;
re-measure it.

**The single most important lesson from session 4:** two of the three
"green" gates in the previous version of this block were not measuring what
a reader assumed. A collect count is not a passing suite, and a cached
canonical is not a canonical. Both were fixed, and the block below is
corrected accordingly.

---

## 1. START HERE

**Branch `improvement/2026-08-programme`. NOT pushed** (no upstream; absent
from `git ls-remote --heads origin`). **`main` untouched** at `b5ac95c8`,
identical to `origin/main`. Nothing is public. Tree clean.

Re-measure before trusting anything. **Run the suite, not just collection:**

```
git log --oneline main..HEAD | wc -l           # 51 at time of writing
git status --porcelain                          # expect empty
python3 -m pytest tests/ -q                     # 2,416 passed, ~13 min
python3 tests/test_classification.py            # 1386 passed, rc=0
python3 scripts/claim_auditor.py --verify-facts # rc=0
python3 scripts/site_integrity.py               # rc=0
python3 scripts/cascade_count.py --check        # rc=0
python3 scripts/build_recall_artefact.py --check # rc=0
python3 scripts/build_gap_demo.py --check       # rc=0
python3 scripts/check_selfref_sourcing.py --control-only  # rc=0
```

**`--collect-only` is NOT in this list on purpose.** The previous version of
this block used it, and the suite was red for six commits underneath it. A
collect count proves tests exist. It does not prove they pass. See F26.

A fresh session must, in order:

1. Read `docs/improvement/PROGRAMME.md`, the commissioning contract,
   verbatim. It is the specification this work is judged against.
2. Read `docs/improvement/STATE.md`, the resume file. Read the LAST two
   checkpoints (session 4) first; they are the current position.
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
| Phase 1.5b claim provenance | DONE, partial (residuals annotated, §7) |
| **Phase 1.5c** | **DONE.** Three defects, three regression pairs, §4 |
| **Class 1 landing-page derivation** | **DONE.** §5 |
| Phase 2 | **FAILED validation, loop 1 of 3** |
| Phase 4 | **FAILED hostile review, loop 2 of 3** |
| Phases 5-8 | NOT STARTED |

**Neither Phase 2 nor Phase 4 has passed its gate. The Phase 4 plan must not
be executed.** Both stopped deliberately with loops remaining.

## 3. THE QUEUE (owner-confirmed, do not reorder)

Items 1 and 2 are DONE. The next session starts at item 3.

1. ~~1.5c, three defects~~ **DONE** (`93d81bf`, `6f3ef07`, `e9aacc8`, `07fd0c0`).
2. ~~Class 1 landing-page derivation~~ **DONE** (`8ae2f70`, `31388c1`).
3. **NEXT: re-derivations at HEAD** under one written rule (Trust and
   Detection), plus resolving the BASELINE §11 craft contradiction. No
   projection published until this lands.
4. **The traces**, path-labelled. **The target list has changed; read §6
   before starting.**
5. **Plan revision** against `HOSTILE-REVIEW-LOOP2.md` §F and both loops'
   dispositions.
6. **Loop 3** in a fresh session with the closure-verification brief.

**P0 (docs/*.md gate coverage) is now UNPARKED**, 1.5c has landed, which was
its precondition. It belongs to the Phase 4 plan, not to a side quest. Do
not start it outside that plan.

## 4. PHASE 1.5c: WHAT LANDED

| Defect | Repair | Guard |
|---|---|---|
| **F21** self-citation | `paragraph_has_source()` no longer accepts a page's own address, machine-metadata URLs, fragment anchors, or a document citing its own filename. `page_identity()` collects the page's addresses once per file; `scan_file` passes them in. | `tests/test_selfref_sourcing.py`, 17 tests |
| **F22** the 0.5 floor | Deleted. Replaced by `STALE_CHECK_EXEMPTIONS`, named per-file per-phrase data with a stated reason, plus `stale_number_verdict()`. Magnitude decides nothing. | `tests/test_stale_number_floor.py`, 12 tests |
| **F24** recall underivability | `benchmarks/synthetic/RECALL.json`, produced by `scripts/build_recall_artefact.py` from an actual run. `check_recall_claims()` requires every published fraction to exist in it AND to name path and gate condition. | `tests/test_recall_artefact.py`, 13 tests |

**`STALE_CHECK_EXEMPTIONS` is empty, and keeping it empty was the work.**
Removing the floor surfaced four suppressed matches. None was a legitimate
sub-count. Three were `python3 tests/...` read as "3 tests" (the lookbehind
was `(?<!\d)`, which excludes a preceding digit but not a preceding letter);
one was "963 test functions" swept up by a singular `tests?`. Both fixed at
the pattern; see tests/test_stale_number_floor.py . **An exemption records that a number means something else. It
does not excuse a regex that cannot tell a filename from a count.**

**The quarantine ratchet was extended, +2, and this is discretionary.**
A repair that increases sensitivity uncovers claims that were always there.
`.claim-quarantine.json` now carries `_sensitivity_admissions`: tranches,
each naming the finding, the instrument change, the base size before, and
**the exact entries admitted**. Two new tests require every admitted entry
to be itemised and every tranche to state its cause. Anything not itemised
is still forbidden. Quarantine is **44** entries. **FOR OWNER RATIFICATION.**

## 5. CLASS 1: WHAT LANDED, AND WHAT DID NOT

**Class 1 was three unrelated things, not one class of ~30 pairs.** Only the
first was actioned:

| Item | Where | Status |
|---|---|---|
| Terminal mock-up: invented `regula gap` / `regula comply` output behind a `$` prompt | `site/index.html`, `site/locales/de.html`, `site/locales/pt-br.html` | **DERIVED** from real output |
| "roughly 30% / 70% of the EU AI Act", a substantive modelling claim, not a progress bar | `site/about.html`, `blog-code-scanning-vs-questionnaires.html` | **NOT DONE.** Belongs with class 2 |
| `0%` in the assess widget, live UI state, `<span id="progressPct">0%</span>` | `site/assess/{index,de,pt-br}.html` | **NOT A CLAIM.** Nothing to do |

**Do not report class 1 as closed on the strength of the commit.** Two of
the three items remain.

`data/gap_demo.json` is produced by `scripts/build_gap_demo.py` from real
runs against `tests/fixtures/sample_high_risk`. `tests/test_gap_demo.py`
binds every locale panel in both directions: every artefact percentage must
appear, **and no other percentage may appear**. The second half is what
catches drift.

What changed on the page: 20/40/60/80/0/30/50 became 0/0/25/0/0/45/0/0 and
42/100 became 9/100; the **NOTE** the mock-up omitted is now published, and
that NOTE is the denominator disclosure whose absence was the actual defect;
eight article rows, not seven; and `regula comply` needed `--all`, because
without it the command prints no article table for this fixture. The old
panel was not stale output, it was output the command does not produce.

**The F14 stale-crosswalk guard was NOT applied, and the premise was
checked.** MEASURED: `scripts/compliance_check.py` and
`scripts/cli_compliance.py` contain **zero** crosswalk references;
`assess_compliance()` scores through per-article checkers that match
filename patterns and document headings. Crosswalk staleness cannot reach
these numbers. Blanking Articles 11 and 12 would have meant publishing
**altered command output**, which is this task's own defect in reverse.
**DEVIATION FROM A LITERAL INSTRUCTION, FOR OWNER RATIFICATION.** If the
owner still wants those rows blanked, the fix is to stop showing verbatim
output and show a table instead.

**Locales:** the block is English command output in all three files, so
mirroring it is numeric and structural and has landed. **The English
provenance sentence for the DE and PT-BR panels is HELD** for
competent-speaker sign-off; the exact proposed text is in STATE.md. The
locale panels carry a language-neutral reference line instead.

## 6. RECALL: WHAT REPRODUCES, AND WHAT F27 CHANGES

`benchmarks/synthetic/RECALL.json`, four conditions, all from actual runs:

| Condition (path, gates) | High-risk | Prohibited |
|---|---|---|
| scanner, default scan, no flags | **10/30 = 33.3%** | 5/5 |
| scanner, all eight domains declared | **16/30 = 53.3%** | 5/5 |
| scanner, domains declared + `import torch` injected | **23/30 = 76.7%** | 5/5 |
| classifier (`report.scan_files`), all domains | **16/30 = 53.3%** | 5/5 |
| Source: benchmarks/synthetic/RECALL.json , re-derived by tests/test_recall_artefact.py | | |

**10/30 and 16/30 reproduce exactly. 14/30 and 19/30 are WITHDRAWN as NOT
REPRODUCIBLE** on both surfaces that published them. The conditions behind
them were never committed: "`--domain <matched>`" implies a per-fixture
domain mapping that does not exist in `manifest.json`, and "an AI-library
import present" names neither the import nor the fixtures. The reproducible
neighbours are **different conditions** and are labelled as such rather than
substituted.

**F27: F8 does not survive a like-for-like comparison.** Under the SAME gate
condition the scanner and classifier paths miss the **identical 14
fixtures**, the same set, symmetric difference zero. The recorded
six-fixture divergence compared `scanner/default` against
`classifier/all-domains`, changing two paths and two gate conditions at
once. The six fixtures it named are exactly the ones the domain gate
unlocks. **This changes what the traces in queue item 4 are for: the
scanner/classifier divergence is not there to be explained.**

**The trace target list is 7 named fixtures, not 8**, and they come from the
artefact rather than prose: `highrisk_benefits_eligibility`,
`highrisk_border_screening`, `highrisk_crime_forecast`,
`highrisk_energy_grid`, `highrisk_exam_proctor`, `highrisk_recidivism`,
`highrisk_voter_targeting`.

**The diagnosis is still the durable output.** Of 20 default-scan misses:
13 opt-in domain suppression, 4 AI-indicator gate, 3 genuine pattern gaps.
**17 of 20 are gates, not patterns.** Pattern work addresses 3 of 20.

**The projection remains WITHDRAWN.** No movement figure until Trust and
Detection are re-derived at HEAD under one written rule. **BASELINE §11 still
contradicts itself:** craft row says "Hold at 90", arithmetic uses 88, so the
baseline is **52.3 or 52.6**. Phase 7 arbitrates; queue item 3 resolves it.

## 7. OPEN FINDINGS: F25 TO F30

Session 4 produced six. Three are fixed, three are escalated unfixed.

### F25: `CITATION_WORDS` accepts ordinary prose. HIGH, Trust. NOT FIXED.

MEASURED: 94 paragraphs carrying numeric claims are sourced only by a
citation-word. Enumerating all 46 where that word is "source" shows almost
none are citations: "source files", "source code", "open source", "a
significant source of their profits", "Version source of truth". **11
paragraphs across 7 tracked files are sourced by the phrase "open source"
alone**, including `site/index.html`, both locale pages,
`site/regions/uae.html`, `docs/MODEL_CARD.md`, `docs/AI_GOVERNANCE.md` and
`benchmarks/README.md`.

**Consequence, stated plainly: F21 is closed for the URL mechanism, and the
landing page's `<meta>` "13 frameworks" claim still passes anyway**, now via
"Open Source" in its own `<title>`. Measurement rule 5 in live form.

Not fixed because tightening `CITATION_WORDS` would reclassify roughly 90
paragraphs repo-wide, an auditor behaviour change beyond the 1.5c fence.
**ESCALATED for owner scoping.**

### F26: the branch was red for six commits. MAJOR. FIXED.

MEASURED by worktree bisect on the single test: `e30de41` **passed**,
`a941321` **failed**, `eacc2b6` **failed**. `a941321` expanded the high-risk
corpus 5 to 30 and measured recall at 16/30 without touching a test
asserting `recall == 1.0`. Six further commits landed on it, against
programme Principle 6.

It survived because the previous verification block ran `--collect-only`.
The test now reads its expectation from `RECALL.json` and is renamed
`test_synthetic_fixture_precision_recall_matches_artefact`. **The
verification block in §1 has been corrected.**

### F27: F8 not supported by a like-for-like comparison. MAJOR. See §6.

### F28: `cascade_count --check` was a blank gate. HIGH, Trust. FIXED.

MEASURED: `data/site_facts.json` recorded 2,363 collected tests while the
suite collected 2,404. `canonical_count()` read only that cache, so
`--check` compared every surface against a stale canonical, found them all
in agreement, and **exited 0**. The previous version of §1 listed this
command as evidence the tree was trustworthy.

`canonical_count()` now cross-checks against a live `site_facts.compute()`
and raises `RefusedError` on disagreement. Control fired both ways.
**Correct sequence when adding tests: `python3 scripts/site_facts.py` first,
then `cascade_count.py --apply`.**

### F29: 387 does not reproduce; 386 does. MAJOR. NOT FIXED. ESCALATED.

STATE.md and the previous §7.5 record R2 as settled at **387** by two
independent methods. MEASURED at the `v1.7.0` tag by two methods, both give
**386**: that version's own `site_facts.py`, and the current one run against
the same tree. `blog-scanning-10-ai-apps.html` also says **389** further down
while saying 387 above; those cannot both be right.

**Annotated on the page, not corrected**, because the 387 on record came
from two methods that have not been re-run. **Owner ruling needed.**

### F30: allowlist entries suppress whole paragraphs. HIGH. NOT FIXED.

`scan_file` tests each allowlist regex against the claim's line, the claim's
text, **and the entire paragraph**, so one entry intended for one line
exempts every claim beside it. MEASURED: `\bArticles?\s+\d+.*\d+%`, written
for per-article percentages, was suppressing a `9%` overall score and a
`100%` in the same panel.

Repo-wide: **240 claims are allowlist-suppressed, 63 of them ONLY by the
whole-paragraph arm**, across ~20 files, led by
`references/tree_sitter_implementation_guide.md` (17) and
`docs/benchmarks/PRECISION_RECALL_2026_04.md` (9). Line-scoping would
surface all 63 at once. **ESCALATED.**

Note this one interacts with §8: paragraphs got larger when `<pre>` blocks
became atomic, so the over-reach reaches further than it did.

## 8. SMALLER REPAIRS WORTH KNOWING ABOUT

- **A `<pre>` block is now ONE paragraph.** `split_paragraphs` broke on blank
  lines, cutting a terminal transcript into stanzas and demanding a source
  for each, and there is nowhere to put a citation inside verbatim output
  without falsifying it. Blank lines inside a `<pre>` get a **zero-width
  space**: line counts are untouched so coordinates still map. A plain space
  does NOT work, because `line.strip() == ""` is true for it.
- **`scripts/check_selfref_sourcing.py` was a blank gate and is now a
  control.** Its detection was subsumed by the F21 repair, so it reported
  CLEAN on every input including its own known offender. It now plants a
  self-referential-only paragraph and asserts rejection, plants a sourced one
  and asserts acceptance, and **exits 2 if the control does not fire**.
- **`ATTRIBUTED_CLAIM` no longer fires inside HTML tags.** Inside a tag the
  quote characters are attribute syntax, so
  `<meta content="... Reports | Regula">` read as an attribution verb
  followed by quoted text. Numeric claims inside tags still count: a meta
  description is published prose.

## 9. MY OWN ERRORS THIS SESSION: all five

Recorded because the honesty requirement outranks how the record reads.
None reached a commit; all were caught by a control or by checking before
asserting, which is the point.

**9.1 A test that passed for the wrong reason.** My F24 "compliant fraction
passes" test used the word "recalls", and `RECALL_CONTEXT` matched only
`\brecall\b`, so the paragraph was never inspected and the empty result
meant nothing. Found because an adjacent test failed for the same reason.
Fixed the regex, and added an inline control that strips the labels from the
same sentence and asserts it then fails.

**9.2 A join that did not join.** I replaced blank lines inside `<pre>`
blocks with a single space to stop them splitting. `line.strip() == ""` is
true for a space, so nothing changed. The gate still failed; re-running is
what surfaced it.

**9.3 Provenance lines on the wrong panels.** My locale script added the
reference line to all four terminal panels per page, not the two demo
panels. Two of them would have pointed at a fixture and test that do not
produce their output. Caught by counting the insertions.

**9.4 A defect I nearly reported that does not exist.** `regula gap` says
"Highest risk tier: not_ai" for a fixture named `sample_prohibited`, while
`regula check --format json` returns a prohibited finding. I was one step
from filing it. The fixture carries `# regula-ignore` on line 1; the finding
is `suppressed: True`; `check`'s human output says "NO AI DETECTED,
Suppressed: 1". They agree. Measurement rule 4e held.

**9.5 A gate that passed for the wrong reason.** The class 1 pre-landing
check went green on all three locale pages while the panels were **not
sourced**, an allowlist entry was matching elsewhere in the same paragraph
and suppressing everything in it. Found by asking why it passed rather than
accepting that it did. That question is what produced F30. The panels now
carry a resolvable file reference and are sourced on their own merits,
**proven by stripping citation words and re-running**: all three return
`file-ref:tests/test_gap_demo.py`.

## 10. WHAT IS NOT GREEN

**`claim_auditor.py --diff-base` is red on `docs/TRUST.md` (14 findings) and
`docs/MODEL_CARD.md` (12) for pre-existing unsourced percentages.** MEASURED
like-for-like in a HEAD worktree: those documents plus the synthetic results
gave **67 claims / 36 unsourced** before session 4 and **72 / 34** after, so
the session reduced it.

The CI claim gate scans whole files, so **any commit touching those two
documents is red, including every cascade commit that has ever run**. The
branch is unpushed, so CI has never executed. This is P0 territory.

Whole-repo, all 170 tracked scanned files: **1,287 claims, 359 findings,
0 in `site/`.** Reproduce with scripts/claim_auditor.py over `git ls-files`.

## 11. STANDING RULES (owner-set, non-negotiable)

- **Never suppress or dismiss a security alert.** Leave false positives open
  and explain them.
- **No owner personal information in the repo, of any kind.**
- **No em dashes** in repo copy, commits, docs or replies. Verbatim command
  output is reproduced exactly, including any em dash the tool prints;
  altering it would falsify the output.
- **All three locales in the same change**; new DE/PT-BR prose needs
  competent-speaker sign-off.
- **Region pages `site/regions/*.html` are GENERATED** from
  `content/regulations/*.py`. `uae.html` and `regulations.html` are
  hand-maintained exceptions.
- **Run the control before reporting a result.** A blank gate is not a green
  gate; use `PIPESTATUS` or redirect to a file. **A collect count is not a
  passing suite. A cached canonical is not a canonical.**
- **Stdlib-only core, offline by default, no telemetry.** A **runtime-core**
  constraint, not a CI constraint.
- **Never commit to `main`; no force-push; no history rewrite.**
- **Stage explicitly; no `git add -A`** (`.claude/rules/git.md`).
- **Count propagation uses `scripts/cascade_count.py` only**, and
  `scripts/site_facts.py` runs first.
- **Numbers on public surfaces come from an artefact a test regenerates**,
  never from prose. Three exist now: data/site_facts.json ,
  benchmarks/synthetic/RECALL.json and data/gap_demo.json .
- **Mid-landing expansion** is permitted only when (a) it applies an
  already-approved disposition class to newly discovered instances, or (b)
  leaving it would publish a known-false claim through the same commit
  window. Flag every expansion in the commit body and the report; anything
  involving discretionary framing goes for ratification.
- Owner deliverables go to the Downloads folder on the Windows side of the
  WSL mount.

## 12. LOADED RULES: read these, they are the compressed lessons

`.claude/rules/measurement.md` is the highest-value file in the repo for a
new session. Nine rules, each paid for by a wrong number:

1. Measure in place. 2. One variable at a time. 3. Never trust a number
produced by a copy, including your own earlier one. 4. Require positive proof
the code path executed. **4b.** Verify a file is tracked before calling it a
published surface. **4c.** Any completeness claim must be produced by
enumeration. **4d.** Enumeration picks the files; it does not license a blind
replace. **4e.** Before asserting two artefacts contradict, read both in
full. 5. Passing a gate is not evidence of meeting a standard when the gate
tests something narrower.

Session 4 exercised 4b (the 100% dogfood score computed over gitignored
directories, see scripts/build_gap_demo.py ), 4e (§9.4) and 5 (F25)
directly.

Also `.claude/rules/git.md`, `tests.md`, `quality-standards.md`,
`python-scripts.md`, `site-html.md`, `regulatory-content.md`.

## 13. OPEN OWNER ITEMS

**Decisions this session is waiting on:**

1. **Ratify or reject the quarantine admissions mechanism** (+2 entries,
   §4).
2. **Ratify or reject the F14 deviation** on Articles 11 and 12 (§5).
3. **Scope F25 and F30** (§7). Both are auditor behaviour changes larger
   than the 1.5c fence. F25 in particular means the landing page's meta
   claim is still falsely sourced.
4. **Rule on F29** (§7): is 387 or 386 correct, and does the blog's 389 get
   corrected?
5. **Sign off the English provenance sentence** for the DE and PT-BR panels
   (§5). Exact text in STATE.md.

**Standing items, unchanged:**

6. **R1 and the 330 figure are annotated, not corrected.** R1: the v1.6.1
   raw output is not committed though the post says both versions are.
   **330 is UNSETTLEABLE**, no `v1.6.1` tag and **no 1.6.1 release on PyPI**
   (releases run 1.5.0, 1.5.1, 1.6.0, **1.6.2**, 1.7.0 onward; the sdist
   derivation was attempted once). Bracketing the tags that exist with the
   current script gives v1.6.0 = 219 and v1.6.2 = 386, so 330 is consistent
   but unconfirmed. **The unit is not fixed either:** on the same v1.6.2
   tree, that version's own script gives 358 and the current one gives 386.
7. **Private remote for `getregula-internal/`** (`OWNER_ACTIONS.md` item 9).
   Local-only git repo with a `pre-push` hook; history but one disk.
8. `OWNER_ACTIONS.md` items 1, 2, 3, 5, 7 unstarted (DPVCG post, rater
   recruitment, Zenodo/DOI, BSI ART/1, GSC re-auth). Item 4 closed; item 8
   answered as F21.
9. **Rater recruitment** remains the binding constraint on the corpus, and
   the validator's ruling means it **cannot** be relaxed to two raters on the
   evidence offered.

## 14. WHERE THINGS ARE

**Tracked, `docs/improvement/`:** `PROGRAMME.md` (contract) · `STATE.md`
(resume) · `BASELINE.md` · `CODE_REVIEW.md` · **`HANDOVER.md`** (this) ·
`PHASE0_VERIFICATION.md` · `OWNER_ACTIONS.md` · `COMMIT_ERRATA.md` ·
`PACK-1.5b.md` · `RESEARCH-CARDS.md` · `PLAN-PHASE4.md` ·
`PLAN-PHASE4-v2.md` · `HOSTILE-REVIEW-DISPOSITIONS.md` ·
`HOSTILE-REVIEW-LOOP2.md` · `GATE-REVIEW.md` · `fp_taxonomy.json` ·
`measure_pattern_reach.py`.

**Artefacts that back published numbers** (each regenerated by a test):
`data/site_facts.json` · **`benchmarks/synthetic/RECALL.json`** ·
**`data/gap_demo.json`**.

**Producers:** `scripts/site_facts.py` · `scripts/cascade_count.py` ·
**`scripts/build_recall_artefact.py`** · **`scripts/build_gap_demo.py`** ·
`scripts/check_selfref_sourcing.py` (control + pre-landing gate).

**Guards:** `tests/test_precision_provenance.py` · `test_cascade_count.py` ·
`test_collection_integrity.py` · `test_claim_auditor_coords.py` ·
`test_claim_auditor_percent.py` · `test_claim_quarantine.py` ·
`test_packaged_data.py` · `test_published_count_manifest.py` ·
**`test_selfref_sourcing.py`** · **`test_stale_number_floor.py`** ·
**`test_recall_artefact.py`** · **`test_gap_demo.py`**.

**Outside the repo, deliberately, `getregula-internal/`** (local-only git
repo, no remote, `pre-push` hook refuses): `research-sweep-2026-07.md` ·
`moat-programme-2026-07.md` · `competitive-intelligence-2026-07.md` ·
`moat-research.md` · `originals-pre-redaction/` · `README.md`.
**Why:** the repo is public; these are competitive and commercial strategy.
**Calibration: competitor names were NOT redacted**, the repo already names
its comparison set publicly. What is held back is positioning work.

## 15. THE ONE THING TO UNDERSTAND

Session 3's version of this file said the programme was further from the
Phase 4 gate than it looked, and that this was the checks working. Session 4
found that **two of the checks in its own verification block were not
checking**: a collect count stood in for a passing suite while the suite was
red for six commits, and a cached number stood in for a canonical while the
published counts drifted.

Neither was found by running the checks. Both were found by doing work that
happened to cross them.

**So: run the control, and when a gate goes green, ask what it actually
measured.** Twice this session a gate passed for the wrong reason, and both
times the answer to that question was a real finding.
