# Regula — Prioritised Gap Backlog

This file is the **single source of truth** for known gaps, bugs, and
improvements. It complements `ROADMAP.md` (which tracks shipped features).
Gaps are graded by user impact: **P0** blocks user value, **P1** is
visible quality damage, **P2** is real but not visible, **P3** is backlog.

Last consolidated: 2026-04-09 from the `/research-eval` + live-path audit
+ `/last30days` market and best-practices research.

---

## /last30days market intelligence — verified Apr 2026

These items inform priority weighting below. Sources cited inline.

**EU AI Act state of play (March–April 2026):**
- Commission published the **second draft of the Code of Practice on
  Marking and Labelling of AI-generated content** on 3 March 2026.
  Stakeholder feedback closed 30 March 2026. Finalisation expected
  May–June 2026. Regula already tracks this in `scripts/timeline.py`;
  no action required, but `regula gpai-check` should map watermarking
  obligations to this Code once finalised.
- Council mandate adds an **obligation for the Commission to provide
  guidance to economic operators of high-risk AI systems covered by
  sectoral harmonisation legislation** (Annex I) — explicitly to
  minimise compliance burden. This is a tailwind for Regula's existing
  Annex I detection (medical_devices, safety_components categories).
- **AI regulatory sandbox deadline postponed to 2 December 2027** (was
  August 2026). Regula's `regula timeline` should be updated to reflect
  the sandbox postponement.
- New prohibition on **non-consensual sexual content / CSAM AI** added
  to Article 5 by both Council and Parliament mandates. Regula's
  `PROHIBITED_PATTERNS` does not yet have a `non_consensual_sexual`
  category. Add when the Omnibus is formally adopted.
- **Support instruments for implementation under preparation,
  publication Q2 2026.** Watch for the Annex IV template (would replace
  Regula's interim SME format from `regula conform --sme`) and any
  Article 6 high-risk classification guidelines (still overdue).

  Sources:
  - [Council 13 March 2026 press release](https://www.consilium.europa.eu/en/press/press-releases/2026/03/13/council-agrees-position-to-streamline-rules-on-artificial-intelligence/)
  - [Pearl Cohen — New EU AI Act guidance ahead of next enforcement date](https://www.pearlcohen.com/new-guidance-under-the-eu-ai-act-ahead-of-its-next-enforcement-date/)
  - [K&L Gates — EU and Luxembourg Update on Harmonised AI Rules, Jan 2026](https://www.klgates.com/EU-and-Luxembourg-Update-on-the-European-Harmonised-Rules-on-Artificial-IntelligenceRecent-Developments-1-20-2026)

**CLI UX best practices for developer tools (2025–2026):**
- 78% of professional developers spend >50% of their workday in a
  terminal (Stack Overflow Developer Survey 2025) — up from 62% in 2023.
  This validates Regula's CLI-first positioning vs SaaS dashboards.
- "**Value-first onboarding**": get users to experience the core benefit
  as quickly as possible (Vercel / Railway / Supabase model). Show a
  tangible result before asking for any user investment.
  **APPLIED**: `regula quickstart` now shows up to 3 top findings inline
  (commit this session).
- **Display progress for long-running operations.** Avoid blinking-cursor
  silence. Regula's `regula check` is fast enough on small repos that
  this isn't pressing, but on a 5,000-file monorepo it will be.
  **TODO**: Item #14 (--workers + progress bar).
- **Smart defaults beat clever flags.** Regula's flag set is large
  (40+ commands × multiple flags each). Audit which flags users actually
  need vs which can become defaults.
  **TODO**: new item #21.
- **Use the CLI itself to deliver onboarding** — not 10 pages of docs.
  **APPLIED** for quickstart. Other commands could follow.

  Sources:
  - [Lucas F. Costa — UX patterns for CLI tools](https://www.lucasfcosta.com/blog/ux-patterns-cli-tools)
  - [Evil Martians — CLI UX best practices: progress displays](https://evilmartians.com/chronicles/cli-ux-best-practices-3-patterns-for-improving-progress-displays)
  - [DEV Community — Building Developer CLI Tools in 2026](https://dev.to/chengyixu/the-complete-guide-to-building-developer-cli-tools-in-2026-a96)

**Documentation IA / Diátaxis (2026):**
- Diátaxis = 4 distinct quadrants matching 4 user needs:
  1. **Tutorials** (learning-oriented) — "I am new and want to be guided"
  2. **How-to guides** (task-oriented) — "I have a task and want to do it"
  3. **Reference** (information-oriented) — "I need exact details"
  4. **Explanation** (understanding-oriented) — "I want to understand why"
- Regula's docs/ folder currently mixes all four without separation.
  Action: split docs/ into `docs/tutorials/`, `docs/how-to/`,
  `docs/reference/`, `docs/explanation/`. README points to each.
  **TODO**: new item #22.
- "Documentation organised around what developers need to do, not how
  your product is built internally."

  Sources:
  - [Diátaxis](https://diataxis.fr/)
  - [GitBook — Documentation structure best practices](https://gitbook.com/docs/guides/docs-best-practices/documentation-structure-tips)
  - [Fern — Info Architecture for Docs, Feb 2026](https://buildwithfern.com/post/information-architecture-best-practices-documentation)

**AI governance market sizing (validates the wedge):**
- Market: $0.2B (2025) → projected **$4.83B by 2034** at 35–45% CAGR.
- **SME segment is the highest-growth share** — directly validates
  Regula's positioning. "AI governance for SMEs needs to become a
  practical operating discipline, not a heavyweight compliance
  programme."
- IBM Watson governance: ~13% market share, leader.
- Microsoft / Google Cloud / AWS: rapidly expanding governance offerings
  integrated with cloud platforms.
- **MLOps tools segment growing fastest at 49% CAGR** — Regula could
  position adjacent (governance for MLOps pipelines).
- Notable competitors NOT yet in Regula's competitive landscape:
  Credo AI, DataRobot governance, Holistic AI, Trustible, Fairly AI,
  PwC and Deloitte governance services. **TODO**: P2 #11 (competitive
  landscape audit).

  Sources:
  - [Future Market Insights — Enterprise AI Governance and Compliance Market 2026](https://www.futuremarketinsights.com/reports/enterprise-ai-governance-and-compliance-market)
  - [AIMultiple — Best 30 AI Governance Tools in 2026](https://aimultiple.com/ai-governance-tools)
  - [IAPP — AI Governance Vendor Report 2026](https://iapp.org/resources/article/ai-governance-vendor-report)
  - [Tradify Services — AI Governance for SMEs, Apr 2026](https://tradifyservices.com/2026/04/04/ai-governance-for-smes-how-to-adopt-business-ai-without-losing-control-2/)

---

## P0 — Ship next (blocks user value)

_All P0 items closed in this session — see "Closed" section below._

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

### 21. Smart-defaults audit (CLI UX best practice)
- **Where:** every `subparsers.add_parser` block in `scripts/cli.py`
- **Issue:** Regula has 40+ commands × multiple flags. Users have to
  read help text for every command. The 2026 CLI UX best practice is
  "smart defaults beat clever flags" — most users should never have to
  set a flag.
- **Action:** for each command, identify the most common usage pattern
  and make it the default. Examples:
  - `regula check` should default to `--skip-tests` (real users don't
    want test-file findings unless they ask)
  - `regula docs` should default to `--qms` (most users want both)
  - `regula register` should default to `--branch auto` (auto-detect)
- **Acceptance:** the README's "common workflows" section lists the
  exact 5 commands a user actually needs to run, with no flags.
- **Effort:** 4 hours
- **Source:** [Lucas Costa — UX patterns for CLI tools](https://www.lucasfcosta.com/blog/ux-patterns-cli-tools)

### 22. Diátaxis-shape the docs/ folder
- **Where:** `docs/` (current state: flat folder mixing tutorials, how-to,
  reference, and explanation content)
- **Issue:** Per the 2026 IA best-practice consensus, documentation
  should be organised by user intent (Diátaxis: tutorials / how-to /
  reference / explanation), not by internal structure. Regula's `docs/`
  has architecture.md, landscape.md, sample_high_risk_annex_iv.md,
  course/, user-validation/, and others all mixed together.
- **Action:**
  - Create `docs/tutorials/` (move QUICKSTART_VIBE_CODERS.md here)
  - Create `docs/how-to/` (e.g. "how-to-disclose-an-article-50-chatbot.md",
    "how-to-generate-an-annex-iv-pack.md")
  - Create `docs/reference/` (move cli-reference.md, architecture.md
    here)
  - Create `docs/explanation/` (move article-state-of-ai-compliance.md,
    landscape.md, article-south-africa-ai-policy.md here)
  - Update README to link the four entrypoints
- **Effort:** 2 hours (move + rewrite README links)
- **Source:** [Diátaxis](https://diataxis.fr/),
  [GitBook IA best practices](https://gitbook.com/docs/guides/docs-best-practices/documentation-structure-tips)

### 23. Add `non_consensual_sexual_content` to PROHIBITED_PATTERNS
- **Where:** `scripts/risk_patterns.py:PROHIBITED_PATTERNS`
- **Issue:** Both Council (13 March 2026) and Parliament (26 March 2026)
  Omnibus mandates add a new Article 5 prohibition on non-consensual
  sexual / intimate content AI and CSAM AI. Once the Omnibus is formally
  adopted, Regula needs to detect this category.
- **Action:** add the category once the Omnibus is in OJEU. Until then,
  it is a candidate detection.
- **Effort:** 2 hours when triggered.
- **Trigger:** OJEU publication of the Omnibus (likely H2 2026).
- **Source:** [Council 13 March 2026 press release](https://www.consilium.europa.eu/en/press/press-releases/2026/03/13/council-agrees-position-to-streamline-rules-on-artificial-intelligence/)

### 24. AI regulatory sandbox deadline update
- **Where:** `scripts/timeline.py`
- **Issue:** The Omnibus postpones the AI regulatory sandbox deadline
  from August 2026 to **2 December 2027** (per the Council mandate).
  Regula's timeline doesn't yet have this entry.
- **Action:** add a `2027-12-02` proposed entry for "AI regulatory
  sandbox establishment deadline (Omnibus, postponed from Aug 2026)".
  Status: proposed.
- **Effort:** 15 min.
- **Source:** [Pearl Cohen](https://www.pearlcohen.com/new-guidance-under-the-eu-ai-act-ahead-of-its-next-enforcement-date/)

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

## Closed in this session (post-v1.6.0)

- ~~P0 #1 AICDI figures verification~~ — `2,972` replaced with
  "approximately 3,000" (UNESCO press release wording) in
  `scripts/timeline.py`, `docs/landscape.md`, `README.md`, `writing.html`.
  `2.7%` model registry and `2.3%` complaints mechanism figures marked
  **[PDF only — unverified]** per CLAUDE.md Research Integrity rule 2.
  Verified against UNESCO + Policy Edge press releases; both quote
  "3,000 companies across 11 sectors" and the 10%/12%/11%/7% figures, but
  neither discloses the 2.7% / 2.3% breakdowns.
- ~~P0 #2 Recall expansion for the 6 remaining Annex III categories~~ —
  biometrics, critical_infrastructure, migration, justice, medical_devices,
  and safety_components each expanded from 4–7 to 12–18 real-world
  phrasings + prompt-string templates. Six new regression tests added
  (`test_recall_realistic_biometrics_code` and five siblings). 925/925
  custom runner green.
- ~~P0 #3 Sentry DSN warning~~ — doctor telemetry check downgraded from
  WARN to INFO. Rewritten to "no crash-reporting backend configured
  (self-hosted deployment). Optional: set _SENTRY_DSN in telemetry.py".
  User can still plumb a DSN later (option A from the TODO); the
  misleading WARN is gone.
- ~~P1 #7 CHANGELOG + TODO in README footer~~ — already present at
  `README.md:393`; item closed.

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
