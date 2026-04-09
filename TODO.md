# Regula — Prioritised Gap Backlog

This file is the **single source of truth** for known gaps, bugs, and
improvements. It complements `ROADMAP.md` (which tracks shipped features).
Gaps are graded by user impact: **P0** blocks user value, **P1** is
visible quality damage, **P2** is real but not visible, **P3** is backlog.

Last consolidated: 2026-04-09 from the `/research-eval` + live-path audit.

---

## P0 — Ship next (blocks user value)

### 1. Verify the AICDI 2,972 / 2.7% figures against the primary PDF
- **Where:** `scripts/timeline.py:73`, `docs/landscape.md:3`,
  `writing.html:143`, `README.md:143`
- **Issue:** "2,972 companies" and "2.7% have a formal AI model registry"
  appear consistently in Regula's own files but are not surfaced in any
  publicly indexable secondary source I could find. Press releases round
  to "3,000". One secondary source says "more than 1,000". The granular
  percentages (10%, 12%, 11%, 7%, 2.7%, 2.3%) appear nowhere except in
  Regula.
- **Action:** find the AICDI PDF in your local research folder, confirm
  the numbers against page-and-paragraph, add it to `references/`, cite
  the PDF page numbers in the `timeline.py` source comment.
- **Effort:** 30 min (assuming you have the PDF)
- **Risk if not done:** unverified statistic in user-facing copy is a
  blocking issue per `CLAUDE.md` Research Integrity rule 2.

### 2. Recall expansion for the 5 remaining Annex III categories
- **Where:** `scripts/risk_patterns.py` HIGH_RISK_PATTERNS dict
- **Issue:** v1.6.0 expanded employment, education, essential_services,
  and law_enforcement. The 5 still on the original 3–4 keyword baseline:
  - `biometrics` (4 patterns)
  - `critical_infrastructure` (4 patterns)
  - `migration` (4 patterns)
  - `justice` (4 patterns)
  - `medical_devices` (4 patterns)
  - `safety_components` (7 patterns)
- **Action:** for each, add 8–15 real-world phrasings + prompt-string
  templates + a regression test fixture, following the pattern from
  `test_recall_realistic_employment_code`.
- **Effort:** ~2 hours per category. Can be done as 6 small commits.
- **Owner:** unassigned.

### 3. Sentry DSN — decide & ship
- **Where:** `scripts/telemetry.py`
- **Issue:** `regula doctor` warns "Consent is enabled but Sentry DSN is
  not set — crashes will not be reported." You currently have **zero
  visibility** into real-world failures. Either set the DSN with a clear
  consent flow or remove the warning.
- **Action:** decide one of three:
  - (A) Set DSN, default `_consent = False`, opt-in via `regula telemetry enable`
  - (B) Remove the warning entirely (accept zero crash visibility)
  - (C) Move to a different provider (Plausible, self-hosted Glitchtip)
- **Effort:** 2 hours
- **Recommendation:** A. Crash data will close P1 #5 below faster than
  any audit can.

---

## P1 — This week (visible quality damage)

### 4. Self-benchmark precision is 15.2% on labelled OSS
- **Where:** `README.md:224`, `tests/test_classification.py` (precision test)
- **Issue:** ~5 in 6 findings on mature OSS are false positives at the
  tier tested. README discloses this honestly (good), but it bites on
  every first-run.
- **Action:** audit `_compute_context_penalty`, `_has_mock_patterns`,
  `_is_example_file`, `_is_init_file`, and the domain-boost interaction.
  False-positive root cause is likely under-tuned context penalties + the
  combination of multiple weak indicators producing a high confidence_score.
- **Effort:** 4–8 hours of measurement-driven work. Use `regula benchmark`
  + the labelled OSS corpus.
- **Acceptance:** precision >= 30% with no recall regression on the
  prohibited / high-risk synthetic fixtures (currently 100/100).

### 5. JS/TS data-flow is single-file only
- **Where:** `scripts/ast_engine.py:215-788` (JS/TS path) vs
  `scripts/cross_file_flow.py` (Python only)
- **Issue:** A user with a TypeScript project that calls OpenAI in
  `client.ts` and uses the result in `routes/chat.ts` won't get the same
  oversight detection as Python users.
- **Action:** add JS/TS analogue of `cross_file_flow.py`. Tree-sitter
  already gives us the import map; need to walk it across files and
  resolve `import { x } from './client'` chains.
- **Effort:** 1–2 days

### 6. Java / Go / Rust / C / C++ are regex-only
- **Where:** `scripts/ast_engine.py` `_analyse_java_regex` etc.
- **Issue:** Imports detected, no AST, no data flow, no oversight detection.
  Documented honestly in `docs/architecture.md` but it's a real ceiling.
- **Action:** tree-sitter has grammars for all of these. Same pattern as
  the existing JS/TS implementation.
- **Effort:** ~1 week per language with tests.
- **Priority order if doing one:** Go (highest customer interest signal
  from the `regula deps` Go module support already shipped) → Java
  (Spring Boot enterprise) → Rust → C++ → C.

### 7. CHANGELOG.md and TODO.md need to be linked from README
- **Where:** `README.md`
- **Issue:** these files exist after this commit but aren't surfaced
  anywhere users can find them.
- **Action:** add "Releases" and "Roadmap & Known Issues" links to the
  README footer.
- **Effort:** 5 min

### 8. Pre-commit hook is too aggressive on legitimate dev fixtures
- **Where:** `hooks/pre_tool_use.py`
- **Issue:** the hook blocked **8+** of my own Edit/Write/Bash operations
  this session because I was writing test fixtures and pattern definitions
  that literally contain the prohibited keywords. Workaround was to embed
  `# regula-ignore` in the new content, which works but is friction.
- **Action:** widen `_is_documentation_write` to include
  `tests/test_*.py` and `scripts/risk_patterns.py` automatically, OR
  detect when the new content is **inside a test file or pattern
  definition file** and downgrade to INFO with a one-line warning instead
  of a block.
- **Effort:** 2 hours
- **Risk:** if too permissive, real prohibited code in tests slips
  through. Mitigate with a deny-list of file paths that still get full
  classification.

### 9. Clean stale test artefacts on every release
- **Where:** `dist/`, `~/.regula/cache/scan_cache.json`, `docs/tmp*.md`
- **Issue:** I deleted 45 untracked `docs/tmp*_annex_iv.md` files this
  session. They were generated by test runs but not gitignored at the
  test level (only at the repo level). The conform/docs generators
  should write to a tempdir, not into `docs/`.
- **Action:** audit every command that writes a file, default the output
  path to `tempfile.mkdtemp()` unless `--output` is given.
- **Effort:** 4 hours

---

## P2 — Real but not yet user-visible

### 10. Regulatory state is hard-coded in Python
- **Where:** `scripts/timeline.py`, `references/*.yaml`,
  `content/regulations/*.py`
- **Issue:** When the Omnibus passes, you'll need to edit code, ship a
  release, and wait for users to upgrade. A `regula update --regulatory`
  that fetches a signed JSON manifest would dramatically increase
  confidence and reduce time-to-correct on regulatory changes.
- **Effort:** 1 day (manifest format + signing + fetcher + cache)
- **Risk:** opens a network surface — needs design consideration for the
  zero-deps / offline-first promise.

### 11. No competitive landscape audit on file
- **Issue:** You asked for this earlier. I have not done it. Without it,
  positioning copy is anchored on whatever you remember from past
  research, not on the current state of the market.
- **Action:** parallel WebSearch sweep — Credo AI, Holistic AI, Fairly AI,
  Trustible, Snyk AI-BOM, Semgrep AI patterns, Datadog AI, ObvioTech,
  ArkForge, Systima, MyNARA, Plus any AICDI-listed tools — check each
  against Regula's positioning surface (CLI vs SaaS, free vs paid,
  EU AI Act vs generic) and update README accordingly.
- **Effort:** 2 hours
- **Acceptance:** a `docs/competitive-landscape.md` with one row per
  competitor, last-verified date, and the dimension on which Regula
  differentiates (or does not).

### 12. No documented user validation
- **Where:** `docs/user-validation/` (currently only templates)
- **Issue:** No case studies, no testimonials, no documented user calls.
  You can't prioritise P3 / future features without a real signal.
- **Action:** document at least 2–3 real user calls with named pain
  points using the existing `user-template.md`. Anonymise if needed.
- **Effort:** founder work, not technical.

### 13. No telemetry baseline
- **Where:** doesn't exist
- **Issue:** you don't know how many people are running `regula check`
  per day, which subcommands are most used, or which fail.
- **Action:** opt-in, anonymous, count-only telemetry. <100 LOC. Posts
  to a self-hosted endpoint or Plausible.
- **Effort:** 3 hours
- **Tied to:** #3 (Sentry DSN decision)

### 14. `regula check` is single-threaded
- **Where:** `scripts/report.py:scan_files`
- **Issue:** I saw `93 files in 0.024s` on Regula's own codebase.
  On a 5,000-file monorepo it'll be 1–2 minutes.
- **Action:** add `--workers N` flag using `concurrent.futures`. Cache
  is already content-addressed so concurrent workers won't conflict.
- **Effort:** 4 hours

### 15. Doctor doesn't check for stale build artefacts
- **Where:** `scripts/doctor.py`
- **Issue:** `dist/` had both 1.5.1 and 1.6.0 wheels until I cleaned them
  this session. A future release run could re-create the same state.
- **Action:** doctor warns if `dist/` contains more than one version's
  artefacts.
- **Effort:** 1 hour

### 16. No end-to-end smoke test for the published wheel
- **Where:** doesn't exist
- **Issue:** I manually verified `dist/regula_ai-1.6.0-py3-none-any.whl`
  in a clean venv this session. There's no automated equivalent that
  runs on every release.
- **Action:** GitHub Action that, on tag push, creates a clean venv,
  installs the wheel, and runs `self-test + doctor + assess --answers
  + classify --text`.
- **Effort:** 2 hours

### 17. Audit trail has no remote anchor
- **Where:** `scripts/audit.py`, `~/.regula/audit/*.jsonl`
- **Issue:** The audit chain is SHA-256 tamper-evident locally, but a
  contested enforcement action would ask "how do we know you didn't edit
  the file after the fact?". A periodic anchor to a third-party timestamp
  service (RFC 3161) or git tag would address this.
- **Effort:** 1 day
- **Priority:** depends on whether any user is in a position where they
  need this. Probably not yet.

---

## P3 — Backlog (the original v1.3 candidates)

### 18. AVID vulnerability database mapping
- **Issue:** Useful as metadata enrichment on findings (`avid_tag` field
  in SARIF / JSON envelope) but doesn't change detection.
- **Effort:** 2 days (taxonomy file + per-pattern mapping + CLI subcommand
  for lookup)

### 19. Typosquat detection on AI dep names
- **Issue:** Cheap and visibly valuable in `regula deps`. Detect imports
  of `openai` lookalikes (`openal`, `oepnai`, `0penai`) using
  Damerau-Levenshtein distance against a target list.
- **Effort:** 4 hours
- **Out of scope but considered:** typosquat detection on package names
  (PyPI mirror) would require a network call and breaks zero-deps.

### 20. DPO dashboard / Slack alerts / model card generation
- **Issue:** Listed in README as "not planned — needs validation". Stay
  parked until #12 (user validation) produces a signal.

---

## Closed in v1.6.0 (for reference)

- ~~Stale PyPI version (1.5.1 vs 1.6.0)~~ — wheel built and twine-checked.
  Awaiting user `twine upload` (their token).
- ~~`Files scanned: 0` lying~~ — fixed in commit `35c89a9`.
- ~~Scan cache stale on upgrade~~ — fixed in commit `35c89a9`.
- ~~`regula assess` non-TTY crash~~ — fixed in commit `35c89a9`.
- ~~Recall gap on `classify_resume`-style employment code~~ — fixed in
  commit `35c89a9` and extended to education/essential_services/law_enforcement
  in commit (this session's recall expansion commit).
- ~~5 factual errors on README regulatory section~~ — fixed in commit
  `7faf679`.
- ~~"10 Annex III categories" mislabel~~ — fixed in commit `7faf679`.
- ~~45 untracked `docs/tmp*_annex_iv.md` bloat files~~ — deleted this
  session.
- ~~JS/TS tree-sitter data flow listed as "candidate"~~ — already shipped,
  README corrected.
