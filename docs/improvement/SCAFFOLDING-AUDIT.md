# Phase 1.7 — Scaffolding and guardrail audit

Written 30 July 2026 under DIRECTIVE-v3 section 5. Every item below answers
four questions: is it loaded, is it obeyed, has it prevented a recorded
failure, and is there a recorded instance where it should have and did not.
Every change made in this phase names the recorded failure it prevents. No
change ships without one.

Corpus audited: `.claude/rules/` (7 files, tracked), `.claude/commands/`
(3 files, tracked), `.claude/skills/` (6 directories, untracked),
`.claude/agents/` (1 charter, untracked). Tracked status established by
`git ls-files .claude/`, per measurement rule 4b.

---

## 1. Rules (`.claude/rules/`, all tracked, all loaded per session)

| File | Loaded | Obeyed | Prevented a recorded failure | Missed instance |
|---|---|---|---|---|
| `git.md` | Yes | Yes: recent commits stage by path and name every file | The two COMMIT_ERRATA entries predate it; none since | None recorded since adoption |
| `measurement.md` | Yes | Largely | Rule 4e held in STATE.md 9.4 (the suppressed-finding non-defect); rule 4b caught the 58-vs-34 scope error | F26 and F28: the HANDOVER verification block itself violated rule 4 (collect count as passing suite; cached canonical as canonical) for six commits. The rule existed; the block did not obey it. Both fixed in session 4. |
| `tests.md` | Yes (paths: tests/**) | Yes | Custom-runner wiring has stayed consistent | None recorded |
| `python-scripts.md` | Yes | Yes | self-test and doctor run after changes | None recorded |
| `quality-standards.md` | Yes | Yes | Its worked example (`getNextSteps` / `getScanNextSteps`) verified to still exist at `site/assess/index.html:1347` | None recorded |
| `regulatory-content.md` | Yes | **The rule itself was stale** | n/a | **FIXED THIS PHASE.** It required noting the Omnibus as a "provisional agreement ... pending formal adoption". The Omnibus was published in the OJ on 24 July 2026 and `scripts/omnibus.py:29` has carried `OMNIBUS_OJ_DATE = "2026-07-24"` since. A rule loaded every session was injecting a superseded legal status into every session. |
| `site-html.md` | Yes (paths: site/**) | Yes | None specific | None recorded |

### Changes made to rules

**1a. `regulatory-content.md`: Omnibus status corrected to enacted.**
Prevents: the stale-status class recorded on 27 July 2026, when released CLIs
printed "pending OJ publication" for a regulation already in force and a
30-file sweep was needed. The rule now states the enacted position and names
`scripts/omnibus.py` as the single source of truth, so the rule can never
again disagree with the code it governs. Deferred dates in the rule now match
`DEADLINE_OMNIBUS_ANNEX_III = "2027-12-02"` in `scripts/omnibus.py`.

**1b. `measurement.md`: the opening line no longer hand-counts its own rules.**
The file opened "Five rules." while containing nine headed entries (1, 2, 3,
4, 4b, 4c, 4d, 4e, 5); `docs/improvement/HANDOVER.md` section 12 calls it
nine. Prevents: rule 4c's own class (a hand-maintained count drifting as the
file grows), in the file that defines that class.

**1c. Em-dash rule scoped and the verbatim-record exemption encoded
(`CLAUDE.md`; note that file is deliberately gitignored at `.gitignore:35`,
so like the skills it is local scaffolding, not a published surface, and
this change cannot be committed).** Queued explicitly in STATE.md's session
5d NEXT block. The
blanket "no em dashes anywhere" wording misdescribes the tree: measured
30 July 2026, `git ls-files | xargs grep -l "&mdash;"` returns **40** tracked
files and `git ls-files site/ scripts/ | xargs grep -l "—"` returns **167**.
The rule as written was therefore violated by the repository's own generators
(`scripts/build_regulations.py:173`, `scripts/pdf_export.py:642`) and by
`scripts/verify_seo.py:25`, which expects `&mdash;` in titles. The scoped
rule: **no em dashes in NEW prose**, including entity forms; verbatim records
(quoted command output, quoted directives, quoted external text) are
reproduced exactly, because altering them falsifies the record. Prevents: the
DIRECTIVE-v3 logged deviation, where the blanket rule collided with the
verbatim-record requirement and had to be deviated from ad hoc.
**The existing 40-and-167-file footprint is recorded, not swept.** Rewriting
existing copy en masse is content churn on public surfaces behind a gate that
is still being repaired, and dated records must not be rewritten. Disposition:
deferred to the Phase 7-8 public-surface work with this measurement as its
baseline; not silently dropped.

## 2. Commands (`.claude/commands/`, tracked)

**2a. `verify.md` claimed "This sequence mirrors the CI workflow in
`.github/workflows/ci.yaml` exactly. If /verify is green locally, CI should
be green too." Measured false.** CI additionally runs: the security
self-check, the lint job, the html-wellformed job, and the claim-audit job
(`claim_auditor.py --diff-base`, site_facts freshness, `--verify-facts`).
The claim gate is precisely the gate `docs/improvement/LEDGER.md` section 6
records as red on this branch and set to fire on first PR. So /verify's claim
failed measurement rule 5 (a gate narrower than the standard it implies) in
the scaffolding itself, in the direction that matters. Fixed: the claim is
corrected and the six fast gates are added to the sequence.

**2b. `add-command.md` instructed writing new command functions into
`scripts/cli.py`.** The command implementations live in the `cli_*.py`
modules (11 files, `ls scripts/cli*.py`); `cli.py` retains `main()` and the
subparser wiring. Fixed to describe the real layout. Prevents: the
stale-instruction class (a scaffold that contradicts the tree produces wrong
edits), the same class as 3b below.

**2c. `add-pattern.md` audited, one addition.** Its four tier-dict names
verified present in `scripts/risk_patterns.py` (lines 20, 145, 584, 621).
One gap: it did not say that adding a pattern moves the published tier-regex
count, which requires `scripts/site_facts.py` then
`scripts/cascade_count.py --apply` in the same commit. That is the lesson
commit `5f4ae76` paid for (a red intermediate commit where the fast gates
disagreed with the tree). Added as step 3.

## 3. Skills (`.claude/skills/`, untracked, loaded by trigger)

**3a. `regulatory-context/SKILL.md` was stale in the way this project treats
as its worst failure mode.** Updated 17 July 2026, it stated the Omnibus was
"ADOPTED — pending Official Journal publication ... expected second half of
July 2026". The OJ publication happened 24 July 2026 (Regulation (EU)
2026/1744, in force 27 July 2026; `scripts/omnibus.py:29`). This skill
triggers on "regulatory, compliance, deadline, omnibus, AI Act", which in
this project is effectively every session: a stale legal status was being
injected as context into exactly the sessions that write regulatory copy.
Fixed: status flipped to enacted, dates aligned to `scripts/omnibus.py`, a
code-outranks-prose line added at the top, and the Colorado and agentic
AIH 0401 positions aligned to the primary-verified records
(`content/regulations/colorado.py`; LEDGER owner decision 6). Prevents: the
same stale-status class as 1a.

**3b. `releasing-regula/SKILL.md` contained four instructions that are wrong
or forbidden against the current tree.** (i) It said to update a
`version = "X.Y.Z"` line in `pyproject.toml`; the file uses
`dynamic = ["version"]` resolved from `scripts.constants.VERSION`, there is
no static line. (ii) It said to update a version on `CLAUDE.md` line 3; no
version appears there. (iii) Its release-commit step instructed
`git add -A`, which `.claude/rules/git.md` forbids without exception; both
recorded COMMIT_ERRATA entries came from bulk staging. (iv) Its publish step
was a manual twine upload; the release path is `release.yml` via Trusted
Publishing on tag push. Rewritten: bump `scripts/constants.py`, let
`tests/test_source_of_truth.py` (8 tests) enumerate what else must move,
stage explicitly, never blind-replace version digits (measurement rule 4d,
the lockfile near-miss), build-and-clean-install before tagging (the v1.7.6
packaging lesson), and publish through the workflow. Prevents: the recorded
failures behind git.md and rule 4d, replayed through a skill.

**3c. `regula/SKILL.md` frontmatter carries `version: 1.7.1` while
`scripts/constants.py:16` is `1.9.0`.** Ambiguous whether that field is the
skill's own version or the product's; it matched the product version at the
skill's creation. Recorded, not changed: renumbering a field whose meaning is
undetermined would be guessing.

**3d. `gsc/SKILL.md`**: functional, but the underlying token is expired
(`invalid_grant`, an owner action item). No change; the skill is not the
defect.

**3e. `discovering-test-gaps`, `hoisting-regex-compiles`**: audited, current,
no change. The latter is correctly cross-referenced from `/verify`.

## 4. Agent charters (`.claude/agents/`, untracked)

**4a. `claim-auditor.md` predated two auditor behaviours and misstated one
acceptance criterion.** It accepted "a file reference that exists in the
repo"; finding N1 (fixed in `bebe255`, guarded by
`tests/test_tracked_citation.py`) established that existence on disk is not
provenance, the reference must be git-tracked, because a gitignored file
counts locally and vanishes in CI. The charter also predated the quarantine
mechanism (`.claim-quarantine.json`) entirely. Fixed: tracked-not-present
wording at both sites, a new guardrail 7 describing the quarantine as
shrink-only and not the agent's to grow, and pointers to the ledger's open
F25/F30 findings so the agent does not treat a citation-word or
allowlist-shadowed pass as provenance. Prevents: N1's recorded failure,
replayed through an agent that enforces the superseded criterion.

## 5. Self-verification literature (DIRECTIVE-v3 section 5, second bullet)

Citations verified at source, 30 July 2026. The recency window is
deliberately wider than two months because these are the foundational papers
behind the directive's load-bearing claim, stated as such:

- **Huang et al., "Large Language Models Cannot Self-Correct Reasoning
  Yet", arXiv:2310.01798, ICLR 2024 (accepted).** Abstract, quoted exactly:
  "LLMs struggle to self-correct their responses without external feedback,
  and at times, their performance even degrades after self-correction."
- **Stechly, Valmeekam and Kambhampati, "On the Self-Verification
  Limitations of Large Language Models on Reasoning and Planning Tasks",
  arXiv:2402.08115, preprint (not shown as peer-reviewed at source).**
  Abstract, quoted exactly: "We observe significant performance collapse
  with self-critique and significant performance gains with sound external
  verification."
- **Panickssery, Bowman and Feng, "LLM Evaluators Recognize and Favor Their
  Own Generations", arXiv:2404.13076, preprint (not shown as peer-reviewed
  at source).** Documents self-preference bias and, quoted exactly, "a
  linear correlation between self-recognition capability and the strength
  of self-preference bias."

Application, encoded structurally rather than as advice:

- **Gates external to the thing being gated** is already this programme's
  design (tests regenerate artefacts; controls fail on purpose), and the
  literature is the theoretical account of every recorded instance where
  self-checking failed: the 8-of-14 hand-built table, the false blog
  discrepancy (measurement rule 4e), the guard narrower than its own
  standard (F21), the collect count standing in for a passing suite (F26).
- **Independent critics never see their own prior justifications**: any
  review loop (hostile review, gate review, closure verification) must give
  the reviewer the artefact and the standard, never the author's reasoning.
  This is now stated in the charter file (section 4a), and it is why
  DIRECTIVE-v3 already requires loop 3 to run in a fresh session.

## 6. Context-compaction survival (DIRECTIVE-v3 section 5, third bullet)

Verified against this setup's observed behaviour rather than against vendor
claims: project rules under `.claude/rules/` and `CLAUDE.md`-level
instructions are re-injected at session start and after context resets; the
conversation itself is summarised. `measurement.md`'s own header states the
mechanism: "They are loaded every session so they survive a context reset,
which a promise does not." Constraint-pinning is therefore already adopted
here, and this phase strengthens it by making the pinned files true (1a, 3a).
What does NOT survive is session prose: the stale-sentinel hazard lived only
in conversation until 30 July 2026, when it was written into
`docs/improvement/LEDGER.md`. Standing rule confirmed: any constraint worth
keeping goes in a loaded file, not a promise; any hazard discovered goes in
the ledger the same session.

## 7. What this audit did NOT do, stated per the no-silent-deprioritisation rule

- No sweep of the 40 entity-form and 167 literal em-dash files (1c above):
  deferred with reason and baseline measurement.
- No change to `.claim-allowlist` or `.claim-quarantine.json`: F25 and F30
  scoping is owner decision 3 and is not this phase's to take.
- No change to the `regula` skill version field (3c): meaning undetermined.
- Subagent charters beyond `claim-auditor.md` do not exist in this repo;
  the loop-3 closure-verification brief is queued work, not scaffolding.
