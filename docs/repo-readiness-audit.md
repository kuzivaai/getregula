# Regula — Public Launch Readiness Audit

Date: 2026-04-09
Auditor: Automated repo audit (Claude)
Scope: `/home/mkuziva/getregula` at HEAD of `main`
Target: First public release on GitHub + PyPI, zero embarrassment

---

## 1. Executive verdict

**Verdict: BLOCK — one critical honesty issue must be fixed before the repo goes public, plus two lower-order items. Everything else is cosmetic and can ship in a follow-up commit.**

The repository is, structurally, in better shape than most first-launch OSS projects. The standard OSS meta-files exist. The licence is valid MIT. The CI workflows exist. The tests run. The README is long and substantive. The .gitignore correctly excludes build artefacts, `.venv`, egg-info, and `.handover.md`. None of the "typical embarrassment" items (committed `node_modules`, committed `.env`, committed `dist/`) are present in git.

The three most important findings, in priority order:

1. **Numerical claims contradict the project's own source of truth (CRITICAL honesty issue).** `scripts/site_facts.py` and `data/site_facts.json` — which are *the* mechanism the repo uses to prevent marketing drift — report **43 commands, 279 individual regex patterns, 34 pattern groups, and 424 test functions**. The README, CLAUDE.md, CHANGELOG, `index.html`, `de.html`, `pt-br.html`, and the three JSON-LD blocks on the landing page say **39 commands, 330 risk patterns, and 525 or 926 tests**. For a tool whose entire value proposition is "honesty about its own precision", shipping this on day one is the single worst thing that could happen. Fix before public launch. See Section 6.
2. **No `.github/PULL_REQUEST_TEMPLATE.md` and no `.github/dependabot.yml`.** These are the two cheapest community-health wins in a 2025-2026 public OSS repo and are a 10-minute fix each. See Section 4.
3. **The benchmark precision headline in the README (15.2%) and the CHANGELOG headline (“0 false positives at the BLOCK CI tier”) do not yet appear on the landing page stats bar.** The stats bar instead shows the inflated "330 risk patterns". Replacing one stat with the real precision/recall number is a one-line change that turns an honesty liability into a trust asset.

Once item 1 is fixed, the repo can ship. Items 2 and 3 are recommended but not blockers.

---

## 2. File inventory

Every tracked top-level file and directory, with a one-line verdict. 289 files are tracked in git (verified with `git ls-files | wc -l`).

### Top-level files

| Path | Verdict | Note |
|---|---|---|
| `README.md` (420 lines) | REWRITE (numbers) | Content is strong; fix the count claims (lines 250, 341, 376). Otherwise ALREADY GOOD. |
| `LICENSE.txt` | ALREADY GOOD | Verified: standard MIT, (c) 2026 The Implementation Layer. |
| `CONTRIBUTING.md` | KEEP | Exists, tracked. Not reviewed line-by-line in this audit. |
| `CODE_OF_CONDUCT.md` | ALREADY GOOD | Present, 51 lines, technical tone. |
| `SECURITY.md` | ALREADY GOOD | Present, 124 lines, disclosure flow + supported versions. |
| `CHANGELOG.md` | REWRITE (one number) | Line 14 "926 tests" contradicts `site_facts.json` (424). Replace. Otherwise a well-maintained Keep-a-Changelog file. |
| `CITATION.cff` | ALREADY GOOD | Version 1.6.1, dated 2026-04-09, matches `pyproject.toml`. |
| `ROADMAP.md` | KEEP | 9k, content not audited in depth. |
| `TODO.md` | KEEP | 22k, dated 2026-04-09, active backlog. Not public-facing but harmless. |
| `SKILL.md` | CONSIDER REMOVING FROM ROOT | 87 lines of Claude Code skill definition. Not user-facing OSS content. Move to `.claude/skills/regula/SKILL.md` or similar so the root is not cluttered with agent-internal files. Non-blocking. |
| `CLAUDE.md` | KEEP | Tracked, project-specific. Standard in Claude-authored repos. Contains the discrepancy to fix (line 5). |
| `pyproject.toml` | ALREADY GOOD (minor fix) | Metadata complete. Missing `project.urls.Documentation` and `Changelog` entries — a 30-second fix (Section 7). |
| `action.yml` | KEEP | GitHub Action definition, 20k. Load-bearing for the `uses: kuzivaai/getregula@v1` example in the README. |
| `regula-policy.yaml` | KEEP | Reference config that the README refers to. |
| `sitemap.xml`, `robots.txt`, `CNAME`, `404.html`, `og-image.png`, `og-uae.png` | ALREADY GOOD | Site assets for the GitHub Pages landing page. Keep. |
| `.gitignore` | ALREADY GOOD | Correctly ignores `.venv/`, `dist/`, `*.egg-info/`, `.handover.md`, `.ci-heal/`, `.playwright-cli/`, `docs/tmp*_annex_iv.md`, `docs/FULL_INSPECTION.md`, `docs/SHOW_HN_DRAFT.md`. Verified `dist/`, `.venv/`, `regula_ai.egg-info/`, `.handover.md`, `uv.lock`'s peer directories are not tracked. |
| `.claim-allowlist` | KEEP | Used by `scripts/claim_auditor.py`. Load-bearing. |
| `.claudeignore` | KEEP | Claude-internal. Harmless. |
| `.pre-commit-config.yaml` | KEEP | Standard. |
| `uv.lock` | KEEP | Tracked. Harmless — modern Python practice. |
| `sa-tracker.json` | REVIEW | 1.7 KB, tracked, purpose-specific to the South Africa live-tracker content. Not broken, but the file is in the root rather than under `content/regulations/`. Consider moving in a later commit. |

### Landing pages (root-level HTML)

| File | Verdict |
|---|---|
| `index.html` (67 KB) | REWRITE | Fluff, numerical drift, and repetition — see Section 6. |
| `de.html` (22 KB) | REWRITE (numbers) | German mirror. Same "330" claim (line 109). |
| `pt-br.html` (22 KB) | REWRITE (numbers) | Brazilian Portuguese mirror. Same "330" claim (line 109). |
| `uae.html` (24 KB) | KEEP | Regional landing page. Recently updated. Not audited line-by-line. |
| `writing.html` (13 KB) | KEEP | Writing index. |
| `regulations.html` (19 KB) | KEEP | Global tracker. |
| `south-africa-ai-policy.html` (53 KB) | KEEP | Tracker page. |
| `colorado-ai-regulation.html`, `uk-ai-regulation.html`, `south-korea-ai-regulation.html` (36, 33, 36 KB) | KEEP | Tier-3 regional pages. Not audited line-by-line. |
| `404.html` | KEEP | Minimal stub. |

### Directories

| Path | Verdict |
|---|---|
| `scripts/` (76 modules) | ALREADY GOOD | Bare-import convention documented in `CLAUDE.md`. |
| `tests/` (17 test files + fixtures) | ALREADY GOOD | Custom auto-discovery + pytest. |
| `hooks/` (5 files) | ALREADY GOOD | Packaged with the wheel per `pyproject.toml`. |
| `references/` (19 files) | ALREADY GOOD | YAML crosswalks + articles. Packaged. |
| `data/patterns/` (35 YAML pattern files) | ALREADY GOOD | Pattern library. |
| `data/site_facts.json`, `data/site_facts.md` | ALREADY GOOD | **Source of truth** for marketing numbers — and the reason the READM and landing-page discrepancies are unambiguously wrong. |
| `benchmarks/` | ALREADY GOOD | README, labels, results, synthetic corpus — real and reproducible. |
| `content/regulations/` | KEEP | Delta-log, enforcement tracker, sandbox registry. |
| `demos/` (regula-cli.cast + .txt + README) | KEEP | Asciinema demo. |
| `docs/course/` (10 chapters + README) | KEEP | Tutorial. |
| `docs/benchmarks/PRECISION_RECALL_2026_04.md` | ALREADY GOOD | The benchmark document the README trust section points to. |
| `docs/TRUST.md` | ALREADY GOOD | Trust pack. Load-bearing. |
| `docs/what-regula-does-not-do.md` | ALREADY GOOD | Linked from CLAUDE.md. Matches the "Regula is not" section of the README. |
| `docs/landscape.md` | KEEP | AICDI mapping cited from the README. |
| `docs/architecture.md`, `docs/cli-reference.md`, `docs/competitor-analysis.md`, `docs/moat-research.md`, `docs/evidence-pack-guide.md`, `docs/article-south-africa-ai-policy.md` | KEEP | Referenced. |
| `docs/QUICKSTART_VIBE_CODERS.md` | CONSIDER RENAMING | "Vibe coders" is informal and ages poorly. Rename to `docs/QUICKSTART.md` or `docs/quickstart-solo-founders.md`. Non-blocking. |
| `docs/research-eval-report.md` | REVIEW | Internal research artefact. Is it meant to be public? If yes, keep; if no, gitignore. |
| `docs/translation-skill-recommendation.md` | REVIEW | Internal. Same question. |
| `docs/marketing/uae_outreach_v1.md` | CONSIDER GITIGNORING | An outreach template with 50 draft messages. Harmless but not a typical public-repo artefact. Moves the repo towards a "personal workspace" feel rather than a product repo. |
| `docs/tmp*_annex_iv.md` (18 files visible locally) | NOT TRACKED | Already covered by `.gitignore` line 19. No action needed. |
| `docs/sample_high_risk_annex_iv.md` | KEEP | Fixed sample, unlike the tmp files. |
| `examples/regula-rules.yaml` | KEEP | Single example file. |
| `.github/ISSUE_TEMPLATE/` (bug_report.md, false_positive.md, feature_request.md) | ALREADY GOOD | Three templates, the `false_positive` one is thoughtful and category-specific. |
| `.github/workflows/` (ci.yaml, regula-scan.yaml, self-heal.yaml, test-action.yml, triage.yaml, weekly-digest.yaml) | KEEP | All six workflows appear intentional. |
| `.ci-heal/` | NOT TRACKED | Already in `.gitignore`. |
| `.playwright-cli/` | NOT TRACKED | Already in `.gitignore`. |
| `.venv/`, `dist/`, `regula_ai.egg-info/`, `.handover.md` | NOT TRACKED (VERIFIED) | `git ls-files --error-unmatch` confirms none are in git. |
| `assets/site.css` | KEEP | Minimal. |
| `vscode-extension/` | REVIEW | Contains `package.json`, `src/`, `tsconfig.json`. Is the extension actually published? If not, this is a stub that will invite "is this real?" questions from reviewers. Either publish it or add a README stating "work in progress, not published" or remove it from the public tree. |

---

## 3. Standard OSS files scorecard (1–5)

| File | Present | Correct | Score | Notes |
|---|---|---|---|---|
| `README.md` | Yes | Mostly — three wrong numbers | 4 | Strong structure, long, well-linked. Count discrepancy drops score from 5. |
| `LICENSE.txt` | Yes | Yes (MIT verified) | 5 | — |
| `CONTRIBUTING.md` | Yes | Not audited in depth | 4 | Linked from README. |
| `CODE_OF_CONDUCT.md` | Yes | Yes | 5 | Short, technical, direct. |
| `SECURITY.md` | Yes | Yes | 5 | Disclosure flow, supported versions, contact. |
| `CHANGELOG.md` | Yes | One wrong number (line 14) | 4 | Follows Keep-a-Changelog format. |
| `CITATION.cff` | Yes | Yes | 5 | Version matches `pyproject.toml`. |
| `ROADMAP.md` | Yes | Not audited | 4 | — |
| `PULL_REQUEST_TEMPLATE.md` | **No** | — | 1 | **Missing.** Section 4. |
| `dependabot.yml` | **No** | — | 1 | **Missing.** Section 4. |
| `FUNDING.yml` | No | — | n/a | Optional. Recommend skipping at launch. |

Average of the nine applicable files: **3.8 / 5**. After fixing items in Section 4 and the count discrepancies: **4.8 / 5**.

---

## 4. GitHub community health

**Present:**
- `.github/ISSUE_TEMPLATE/bug_report.md`
- `.github/ISSUE_TEMPLATE/false_positive.md` (Regula-specific, thoughtful)
- `.github/ISSUE_TEMPLATE/feature_request.md`
- `.github/workflows/ci.yaml`
- `.github/workflows/regula-scan.yaml` (dogfoods the CLI)
- `.github/workflows/self-heal.yaml`
- `.github/workflows/test-action.yml`
- `.github/workflows/triage.yaml`
- `.github/workflows/weekly-digest.yaml`

**Missing (ordered by ROI):**

1. **`.github/PULL_REQUEST_TEMPLATE.md`** — 10 lines of text. Should include: what changed, why, link to issue, tests added, breaking-change flag, "Does this change pattern counts? If yes, update `data/site_facts.json` and re-run `python3 scripts/site_facts.py`."
2. **`.github/dependabot.yml`** — Ten-line config covering `pip` (for the optional extras) and `github-actions` (for the workflows). The README says "stdlib-only core" so this is low-volume but still useful for the optional extras declared in `pyproject.toml` (`pyyaml`, `tree-sitter`, `weasyprint`, `sentry-sdk`) and for the `actions/checkout@v4` pin in the README example.
3. **`.github/CODEOWNERS`** (optional, recommended). One line: `* @kuzivaai`. Ensures the maintainer is auto-requested on PRs.
4. **OpenSSF Scorecard workflow** (optional, recommended for a security-adjacent tool). Adds a `scorecard.yaml` that publishes a Scorecard badge. For a compliance CLI this has direct positioning value.
5. **`SECURITY.md` already exists.** No action.

**Suggested minimal `dependabot.yml`:**

```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
```

**Suggested minimal `PULL_REQUEST_TEMPLATE.md`:**

```markdown
## What this changes

<!-- One-line summary -->

## Why

<!-- Link to issue if applicable -->

## Tests

- [ ] Added or updated tests under `tests/`
- [ ] `python3 tests/test_classification.py` passes
- [ ] `python3 -m pytest tests/ -q` passes
- [ ] `python3 -m scripts.cli self-test` passes
- [ ] `python3 -m scripts.cli doctor` passes

## Count discipline

- [ ] If this adds or removes risk patterns, CLI commands, frameworks, or languages, I re-ran `python3 scripts/site_facts.py` and updated `data/site_facts.json` and every place that cites a count (README, landing pages, CLAUDE.md).

## Breaking changes

- [ ] None
- [ ] Yes (describe):
```

---

## 5. README.md review

The README is long (420 lines), welcoming without being sycophantic, and covers the essentials: what Regula is, what it isn't, quickstart, what it does, examples, limitations, why, regulatory context, platforms, CI/CD, precision, CLI usage, configuration, testing, constraints, roadmap, trust section, contributing, contact, licence, author. The structure is good. The problems are surgical, not structural.

### Specific rewrites

**Line 250, `## CLI Usage`:**

> Regula has 39 CLI subcommands.

Replace with:

> Regula has 43 CLI subcommands (verified with `grep -c '^def cmd_' scripts/cli.py`).

Justification: `data/site_facts.json` reports `commands: 43`. `grep -c '^def cmd_' scripts/cli.py` returns 43. The "39" is stale.

**Line 341, `## Testing`:**

> 525 tests covering:

Replace with:

> 424 test functions covering:

Justification: `data/site_facts.json` reports `test_functions: 424`. `grep -c '^def test_' tests/test_classification.py` returns 424 in that file alone. The "525" is stale.

**Line 376, `## Roadmap` (v1.2 entry):**

> bias testing (`regula bias`, CrowS-Pairs), 8-framework mapping, 525 tests.

Replace with:

> bias testing (`regula bias`, CrowS-Pairs), 8-framework mapping. (Test count at that release: see CHANGELOG.)

Or simply delete the trailing test count from the historical roadmap entry — historical figures that cannot be re-verified shouldn't sit in a Roadmap file.

**Section 5 — Regulatory Coverage, line 183:** The claim "for a total of 10 high-risk pattern categories" should be cross-checked against `data/patterns/high_risk__*.yaml` (which currently contains 10 files — `biometrics`, `critical_infrastructure`, `education`, `employment`, `essential_services`, `justice`, `law_enforcement`, `medical_devices`, `migration`, `safety_components`). This one is actually correct. No change needed — flagged here only so the author knows it survived verification.

**Lines 141–148 — AICDI mapping:** All headline figures ("2.7%", "12.4%", "43.7%", "13%", etc.) are presented as verbatim from the AICDI PDF. Since `references/aicdi_2025_global_insights.pdf` is *gitignored* (`.gitignore` line 24), external reviewers cannot re-verify these on their own. Either (a) cite the page numbers (already done for 2.7%, 12.4%, p.10) AND link to the UNESCO canonical URL for each (already done in the top of that paragraph) — status: adequate — or (b) move the PDF back into the repo if licensing allows. Current state is acceptable; the URL is the primary source. No change required.

**Line 411 — security contact:** `security@getregula.com` is *not* mentioned; the README uses `support@getregula.com` with a `[SECURITY]` prefix. That is fine but non-standard. Consider publishing `security@getregula.com` as a dedicated alias in a follow-up — not a launch blocker.

### Things the README is already doing well

- Clear "Regula is / Regula is not" section (lines 20–34) — directly answers the user's "what Regula does NOT do" checklist item.
- Honest precision section (lines 220–246). "15.2%" is on the page. No "99%" anywhere.
- Omnibus disclosure (line 164). This is exactly the kind of perishable regulatory claim that most similar projects get wrong.
- Links to `docs/TRUST.md`, `docs/benchmarks/PRECISION_RECALL_2026_04.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`, `CITATION.cff`.
- Maintainer contact visible (`support@getregula.com`, line 408).

---

## 6. Landing page review (`index.html`)

The page is well-designed, fast-loading, accessible (skip-link at line 978, no `<img>` tags so no alt-text gap), and has JSON-LD schema. The issues are honesty and a handful of fluff sentences.

### CRITICAL — inflated or stale numerical claims

Each of these is the *exact* line to change.

**Line 9 (`og:description`):**

> "Free, open-source scanner that tells you which EU AI Act tier you're in, why, and what to do about it. 330 risk patterns, 8 languages, zero dependencies."

Change `330 risk patterns` to `279 risk patterns`. (Source of truth: `data/site_facts.json` → `counts.regex_total: 279`.)

**Line 24 (JSON-LD SoftwareApplication description):**

> "Open-source CLI that scans code for EU AI Act compliance risk patterns. 330 risk patterns, 8 programming languages, 12 compliance frameworks."

Change `330 risk patterns` to `279 risk patterns`. Note that this is search-engine-facing structured data, so this is the one most likely to get quoted by aggregators. Fix carefully.

**Line 100 (FAQ JSON-LD answer, "Is Regula free?"):**

> "all 43 commands [...] all 330 risk patterns, and all 12 compliance framework mappings are free."

The `43` is correct. Change `330` to `279`.

**Line 1026 (hero social-proof strip):**

> `<span class="sp-sep">&middot;</span> 926 tests &middot; 0 security findings`

Change `926 tests` to `424 test functions` (and verify "0 security findings" is still true — check `bandit` output as of today). If "0 security findings" cannot be re-verified on demand, drop it.

**Line 1109 (stats bar, the most visible number on the page):**

> `<div class="stat-num">330</div>` `<div class="stat-label">risk patterns checked</div>`

Change `330` to `279`. Alternatively — and this is the higher-value move — replace this stat with the *measured* headline from the benchmark: **"100% precision on the synthetic Annex III / Article 5 corpus"** or **"0 false positives at BLOCK tier across 257 labelled findings"**. That takes you from a pattern-count stat (which competitors will also claim) to a precision stat (which almost nobody publishes).

**`de.html` line 7** (meta description): "330 EU-KI-Gesetz-Risikomuster" → change to `279`.
**`de.html` line 24** (JSON-LD): same fix.
**`de.html` line 109** (stats bar): `<div class="st-n">330</div>` → `279` (or replace with precision stat as above).
**`pt-br.html` line 7**: "330 padrões de risco" → `279`.
**`pt-br.html` line 24**: JSON-LD, same fix.
**`pt-br.html` line 109**: `<div class="st-n">330</div>` → `279`.

**`CLAUDE.md` line 5:**

> "43 CLI commands, 330 risk patterns, 38 architecture detections, 8 languages, 12 compliance frameworks"

Change `330` to `279`. The `43` is correct. `38 architecture detections` was not audited in this pass — verify it has a source-of-truth entry in `site_facts.json` before the next public reference cites it.

**Important context:** `scripts/site_facts.py` lines 132–135 already flag this exact drift as a known risk. The file says, verbatim: *"Regula's landing pages cite '330 risk patterns'. That figure counts individual regex entries across all pattern groups, not pattern groups themselves. If this number drifts materially from 330, update the landing pages and this note."* It has drifted by 51 (330 → 279). This is the note firing.

### Fluff and soft-claim copy (quoted verbatim)

**Line 1003 (hero sub):**

> "Regula tells you which EU AI Act tier you're in, exactly why, and what you need to do — free, open source, no account. Enforcement starts August 2026."

Keep as-is. This is the best sentence on the page. Not fluff.

**Line 1130 (journey headline):**

> "Three steps to knowing your obligations."

Keep. Tight.

**Line 1131:**

> "Install, scan, get a clear answer."

Keep.

**Line 1169:**

> "Four tiers. One command tells you which one."

Keep.

**Line 1295:**

> "Regula generates structured compliance artefacts from your actual code, not from questionnaires."

Keep. Load-bearing differentiator.

**Line 1320 (WHERE REGULA FITS):**

> "A developer-side static scanner. One of several tools in the EU AI Act ecosystem — each solves a different part of the problem."

Keep. Honest, explicit positioning.

**Lines 1334–1335 (Regula price card):**

> "Static code scanner. Runs on your laptop in one command. Stdlib-only Python core, zero production dependencies, fully offline. `pip install regula-ai`, scan your project, get a clear answer. MIT licence."

Keep. Fact-dense, no adjectives.

**Line 1338 (competitor list):**

> "Other open-source EU AI Act code scanners exist — notably AIR Blackbox..., Systima Comply..., and ark-forge mcp-eu-ai-act..."

Keep. This is the *opposite* of fluff — explicit acknowledgement of alternatives. Almost no OSS tool does this. It is one of the strongest trust signals on the page. Do not touch.

**Line 1359:**

> "No spam. Major releases and EU AI Act deadline reminders only."

Keep.

**Verdict on fluff:** The landing page is already remarkably free of marketing padding. The "Where Regula fits" and competitor-acknowledgement sections are best-in-class for an OSS project. The only copy edits needed are the numerical fixes above.

### SEO / structural issues

- JSON-LD blocks (lines 19–113) are well-formed. `SoftwareApplication`, `Organization`, `FAQPage` all present. Once the `330` is fixed in the SoftwareApplication description (line 24), this section is strong.
- `hreflang` tags present (lines 114–117) for `en`, `de`, `pt-BR`, `x-default`. Correct.
- `canonical` present (line 18).
- Favicon inlined as data-SVG (line 118). Acceptable.
- No `<img>` tags at all — the terminal mock-up is pure HTML/CSS, so there is no alt-text gap.

### Accessibility

- Skip link at line 978 (`<a href="#main" class="skip-link">`). Good.
- `<main id="main">` landmark at line 996. Good.
- Only one `aria-label` in the file (on the email input at line 1355). Consider adding `aria-label` to the three `switchTab` buttons (lines 1039–1041 — `check`, `plan`, `gap`) since they are clickable divs, and to the `copyPill` button. Non-blocking.
- Colour contrast of `#8888aa` on `#070711` body and `#44445a` on the same background is worth testing. `#44445a` on `#070711` will fail WCAG AA for any text that matters. Several "muted" captions use `#44445a`. The only load-bearing text in `#44445a` is the footer copyright and the countdown caveat (line 1008) — both secondary. Non-blocking, but worth a follow-up sweep.

### Broken/dead links

- All footer links (lines 1372–1389) point at `github.com/kuzivaai/getregula/...` paths that exist in the tree (verified against `git ls-files`). No dead links found.

---

## 7. `pyproject.toml` review

Metadata completeness:

| Field | Status |
|---|---|
| `name` | `regula-ai` — correct |
| `version` | `1.6.1` — matches `CITATION.cff` and landing page |
| `description` | Present, accurate |
| `readme` | `README.md` |
| `license` | `{text = "MIT"}` — correct |
| `requires-python` | `>=3.10` — matches README constraint |
| `authors` | Present |
| `keywords` | Present, 5 entries — consider adding `sast`, `static-analysis`, `annex-iv`, `gpai`, `iso-42001`, `nist-ai-rmf` to improve PyPI discoverability. Non-blocking. |
| `classifiers` | 9 entries. **Missing:** `Operating System :: OS Independent` (or individual OS classifiers), `Topic :: Software Development :: Libraries :: Python Modules`, `Typing :: Typed` (if applicable). Add `Programming Language :: Python :: 3.13` since 3.13 is GA. Non-blocking. |
| `[project.optional-dependencies]` | Present, well-factored (`yaml`, `ast`, `test`, `pdf`, `sentry`, `telemetry`, `all`). Good. |
| `[project.urls]` | Three entries: `Homepage`, `Repository`, `Issues`. **Missing:** `Documentation = "https://getregula.com"` (or to the `docs/` directory), `Changelog = "https://github.com/kuzivaai/getregula/blob/main/CHANGELOG.md"`, `Funding` (if applicable). PyPI renders these as labelled sidebar links. |
| `[project.scripts]` | `regula = "scripts.cli:main"` — correct. |
| `[tool.setuptools.packages.find]` include/exclude | Well-commented, intentional. Good. |
| `[tool.bandit]` | Extensively commented. Every skip justified. Exemplary. |

**Top fixes (all non-blocking):**

1. Add `Documentation` and `Changelog` entries under `[project.urls]`.
2. Add `Programming Language :: Python :: 3.13` to `classifiers`.
3. Add `Operating System :: OS Independent` to `classifiers`.

---

## 8. Dead or stale files

None tracked in git that are true zombies. The repo is unusually disciplined for a pre-launch product. Items worth reviewing (none are blockers):

- `SKILL.md` at the root — agent-internal, not product-facing. Consider moving to `.claude/skills/`.
- `docs/QUICKSTART_VIBE_CODERS.md` — rename for durability.
- `docs/marketing/uae_outreach_v1.md` — internal template, consider moving to a private gist or gitignoring.
- `docs/research-eval-report.md`, `docs/translation-skill-recommendation.md` — confirm these are meant to be public artefacts.
- `vscode-extension/` — confirm whether the extension is published, in-progress, or abandoned. If in-progress, add a one-line README in that directory stating so.
- 18 `docs/tmp*_annex_iv.md` files visible locally — already gitignored (`.gitignore` line 19). They clutter the working directory but will not reach GitHub. Consider `rm docs/tmp*_annex_iv.md` locally before the launch screenshot.

---

## 9. Structural improvements

1. **`tools/` directory.** `pyproject.toml` line 48 says "Internal go-to-market tooling and ad-hoc scripts must NOT be added here — put them under `tools/` (not packaged) instead." No `tools/` directory currently exists. Either create it (empty, with a README) or remove that sentence from `pyproject.toml` so it isn't aspirational.
2. **Move SKILL.md and CLAUDE.md out of the root** if you want the GitHub root listing to look product-first. Both are valid and tracked; both dilute the first-impression list of top-level files for a non-Claude reviewer. This is a taste call — fine either way.
3. **Landing pages in a `site/` subdirectory.** 11 HTML files in the root plus 6 PNG/XML/TXT assets make the root listing noisy. GitHub Pages supports a `docs/` source; moving the HTML into `site/` and pointing Pages at it would make the root much cleaner. This is a one-day project and explicitly optional — not a launch blocker.
4. **Rename `LICENSE.txt` → `LICENSE`.** GitHub auto-detects `LICENSE` without an extension and surfaces the licence badge automatically. `LICENSE.txt` works but is slightly less idiomatic. Non-blocking.
5. **`docs/adr/` directory.** An Architecture Decision Records folder is a 2025-2026 OSS best practice (one-pager per major decision: "why stdlib-only core", "why bare imports", "why site_facts.json"). Not required for launch but a strong signal for enterprise reviewers.

---

## 10. Top 10 concrete fixes before public launch (ordered by priority)

1. **Fix the pattern count everywhere.** Replace `330` with `279` in:
   - `README.md` (check for any occurrences — none found in the reviewed lines, but re-grep)
   - `index.html` lines 9, 24, 100, 1109
   - `de.html` lines 7, 24, 109
   - `pt-br.html` lines 7, 24, 109
   - `CLAUDE.md` line 5
   - Anywhere else `grep -rn "330" | grep -i pattern` turns up.
   Then either (a) update the note in `scripts/site_facts.py` lines 132–135 to reference 279, or (b) set an automated check in CI that fails if the landing pages cite a number that disagrees with `data/site_facts.json`.
2. **Fix the command count.** `README.md` line 250 says "39" — change to **43**. `CLAUDE.md` line 5 already says 43.
3. **Fix the test count.** `README.md` line 341 says "525 tests covering:" — change to **424 test functions**. `CHANGELOG.md` line 14 says "926 tests still pass" — either replace with the real number or drop the count. `index.html` line 1026 says "926 tests" — replace with `424 test functions` or with a precision number.
4. **Add `.github/PULL_REQUEST_TEMPLATE.md`** using the template in Section 4. The count-discipline checkbox is the highest-value line in it.
5. **Add `.github/dependabot.yml`** using the template in Section 4.
6. **Replace the stats-bar `330` on all three landing pages with a precision stat** — either "100% precision on synthetic Annex III / Article 5 corpus" or "0 false positives at BLOCK CI tier across 257 labelled findings". This turns a liability into a trust asset.
7. **Verify `vscode-extension/` status.** Either ship, document as WIP in-directory, or remove.
8. **Add `Documentation` and `Changelog` URLs to `pyproject.toml`** under `[project.urls]` so PyPI renders them in the sidebar.
9. **Rename `docs/QUICKSTART_VIBE_CODERS.md` → `docs/QUICKSTART.md`** and update the one reference to it (if any). "Vibe coders" in a file name ages badly.
10. **Rename `LICENSE.txt` → `LICENSE`** so GitHub auto-detects and shows the licence badge on the repo home.

---

## 11. Things that are ALREADY GOOD — do not remove

Leaving this section explicit so later cleanup doesn't accidentally delete load-bearing files or content.

- **`scripts/site_facts.py` and `data/site_facts.json`** — the mechanism that caught the discrepancy this audit is flagging. Do not delete, do not rewrite without preserving the drift-warning logic. Every CI change should re-run it.
- **`data/patterns/*.yaml`** (35 files) — the pattern library. The high_risk__* set correctly covers 10 categories; this matches the README claim.
- **`.gitignore`** — correctly excludes `.venv/`, `dist/`, `*.egg-info/`, `.handover.md`, `docs/tmp*_annex_iv.md`, `.ci-heal/`, `.playwright-cli/`, `docs/FULL_INSPECTION.md`, `docs/SHOW_HN_DRAFT.md`, `docs/audit/`. Do not relax.
- **The "Regula is / Regula is not" section** (README lines 20–34) — unusually honest, directly meets the user's "what Regula does NOT do" checklist requirement.
- **The precision section** (README lines 220–246) — publishes a 15.2% number on a real OSS corpus and does not mask it. The `benchmarks/` directory backs every number with reproducible commands.
- **The Omnibus disclosure** (README line 164) — explicit, dated, primary-source-linked. Exemplary regulatory hygiene.
- **The competitor acknowledgement on the landing page** (`index.html` line 1338) — naming AIR Blackbox, Systima Comply, and ark-forge mcp-eu-ai-act is the single strongest trust signal on the page.
- **`.github/ISSUE_TEMPLATE/false_positive.md`** — a category-specific template is a strong signal of product seriousness.
- **`scripts/cli.py` bare-import convention + `sys.path.insert` lines** — documented in `CLAUDE.md` as "DO NOT CHANGE". Load-bearing.
- **The `tools/`-exclusion comment in `pyproject.toml`** (line 44–46) — an intentional guard against scope creep into the published package. Keep even if the directory itself doesn't exist yet.
- **`CITATION.cff`** — properly versioned and dated. Academic reviewers will cite this.
- **`docs/TRUST.md`** and **`docs/benchmarks/PRECISION_RECALL_2026_04.md`** — load-bearing trust infrastructure linked from the README.
- **The manual test list at the bottom of `tests/test_classification.py`** — `CLAUDE.md` explicitly says "Do not delete". Keep.

---

## Verification commands

Every numerical claim in this audit was verified against the actual repo. Commands used (for reproducibility):

```bash
# Command count
grep -c '^def cmd_' scripts/cli.py                            # 43

# Test function count in the main test file
grep -c '^def test_' tests/test_classification.py              # 424

# Pattern files in data/
find data/patterns -type f | wc -l                             # 35

# Source-of-truth check
cat data/site_facts.json                                       # 43 / 279 / 424 / 12 / 8

# Cross-reference stale numbers
grep -nE "330|279|39 CLI|39 sub|525|424|926" index.html README.md CLAUDE.md CHANGELOG.md de.html pt-br.html

# Confirm build artefacts are not tracked
git ls-files --error-unmatch dist/ .venv/ regula_ai.egg-info/ .handover.md 2>&1

# Count tracked files
git ls-files | wc -l                                           # 289

# Community health files present
ls .github/ISSUE_TEMPLATE/ .github/workflows/ .github/dependabot.yml .github/PULL_REQUEST_TEMPLATE.md 2>&1
```

---

*End of audit. Total tracked files reviewed: 289. Files read in full: README.md, pyproject.toml, LICENSE.txt, CITATION.cff, .gitignore, index.html (heads + critical sections), data/site_facts.json. Files partially read: CHANGELOG.md, TODO.md, scripts/site_facts.py.*
