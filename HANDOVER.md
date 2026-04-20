# Handover — Regula

Generated: 2026-04-20T21:30+01:00
Session: 19-20 April 2026 (documentation audit + precision engineering)

---

## 1. Current State

Regula v1.7.0 is a Python CLI that scans code for EU AI Act risk indicators. It is functional, tested (1,199 tests, self-test 6/6), and published on PyPI (`regula-ai`). **18 commits are ahead of origin/main and have never been pushed.**

This session added significant precision improvements and a new benchmark. The scanner now achieves **85.9% precision on application code** (99.7% with default `--skip-tests` flag) — up from 15.2% on the old library-code benchmark.

**37 files are modified or untracked locally. Nothing has been committed this session.**

---

## 2. What Was Done This Session (not committed)

### Precision Engineering (the bulk of the work)

| Phase | What | Files changed |
|---|---|---|
| Improvement 1-4 | Drop generic minimal_risk findings, library infra penalty, type stub skip, WARN indicator requirement | `scripts/report.py` |
| Phase A: 9 regex bug fixes | Broken lookahead, pickle boundary, torch exclusion, temperature range, path indicators, AI conflation, performance_scor, rag_poisoning, no_grounding | `scripts/risk_patterns.py`, `scripts/agent_monitor.py` |
| Phase B: AST context gating | New module that builds line-level context map (try/except, docstrings, test assertions) | `scripts/ast_context.py` (NEW), `scripts/report.py`, `scripts/scan_cache.py` |
| AI output pattern fix | Stop matching generic `response.content` (HTTP), require LLM-specific structures | `scripts/agent_monitor.py` |
| send_message fix | Remove "message" from send_ pattern (too broad — matches LLM `send_message`) | `scripts/agent_monitor.py` |
| eval(completion) recall fix | Detect eval/exec on AI output vars even in non-AI-importing files | `scripts/report.py` |
| resume → resumes | Require plural to avoid ML "resume training" collision | `scripts/risk_patterns.py` |
| Multi-segment SDK chain | Fix `client.chat.completions.create` detection (was only matching single segment) | `scripts/agent_monitor.py` |
| CI directory exclusion | Add `.github`, `.gitlab`, `.circleci` to SKIP_DIRS | `scripts/constants.py` |
| docs/conf.py provenance | Classify as documentation, not production | `scripts/report.py` |
| aibom import fallback | Scan source imports when no manifest (requirements.txt) found | `scripts/aibom.py` |

### Documentation Audit (Phase 1-5 of the documentation task)

| File | Change |
|---|---|
| `CLAUDE.md` | Updated counts (59 commands, 1,199 tests), removed GSC section (moved to skill), removed CLI Pattern section (redundant with /add-command), fixed VERSION source of truth, fixed verify chain to 4 steps |
| `.claude/skills/gsc/SKILL.md` | NEW — extracted from CLAUDE.md |
| `.claude/skills/regula/SKILL.md` | Fixed framework count (ten→twelve), fixed 9 stale CLI invocations |
| `.claude/commands/verify.md` | Fixed doctor check count (10→11), removed stale commit hash |
| `.claude/plan.md` | DELETED (was stale from an earlier milestone) |
| `docs/architecture.md` | Added 11 missing script files, fixed test count, fixed framework count, fixed filter keys claim |
| `CONTRIBUTING.md` | Fixed CLI invocation, test file count, issue template reference |
| `docs/cli-reference.md` | Added 4 missing commands (aibom, doc-audit, gdpr, roadmap) |
| `docs/evidence-pack-guide.md` | Added --bundle, --sign, --timestamp documentation |
| `ROADMAP.md` | Marked shipped items (timestamping, GDPR, tree-sitter) |
| `HANDOVER.md` | This file |

### Landing Page Changes (from the user's prior work + this session)

- Removed founder name/credentials from hero (all 3 locales)
- Em dashes replaced with appropriate punctuation (all 3 locales)
- Some modifications visible in git diff for `site/index.html`, `site/locales/de.html`, `site/locales/pt-br.html`

### Research/Reports Created (in Downloads, not in repo)

- `/mnt/c/Users/mkuzi/Downloads/Regula_Honest_Assessment.md` — full value audit
- `/mnt/c/Users/mkuzi/Downloads/Regula_Market_Strategy_Report.md` — TAM/SAM/SOM + monetisation
- `/mnt/c/Users/mkuzi/Downloads/Regula_Precision_Deep_Inspection.md` — SAST precision research
- `/mnt/c/Users/mkuzi/Downloads/User_Interview_Leads.docx` — 38 leads for user validation
- `/mnt/c/Users/mkuzi/Downloads/PR4_Reply.docx` — reply to Carlos on awesome-eu-ai-act PR

---

## 3. What Is NOT Done (must do before push)

### Critical (blocks push)

| Item | Why it blocks | Files affected |
|---|---|---|
| **Commit all changes** | 37 uncommitted files with precision fixes, doc updates, new module | All modified files above |
| **Update README.md counts** | Still says 55 commands / 1,055 tests (actual: 59 / 1,199) | `README.md` lines 9, 141, 211, 215 |
| **Update data/site_facts.json** | Says 55 commands (actual: 59) | `data/site_facts.json` line 11 |
| **Update data/site_facts.md** | Same | `data/site_facts.md` line 11 |
| **Update precision on landing pages** | Says 15.2% (misleading — that's library code only; app code is 85.9%) | `site/index.html:653`, `site/locales/de.html:480`, `site/locales/pt-br.html:464` |
| **Update CHANGELOG.md** | Does not cover Phase 1-3 features OR this session's precision work | `CHANGELOG.md` |
| **Run full test suite one final time** | Confirm 1,199 passing after all changes | — |
| **Push to remote** | 18+ commits ahead. Data loss risk. | `git push origin main` |

### Important (before Show HN)

| Item | Why | Reference |
|---|---|---|
| **Fix awesome-eu-ai-act PR #4** | Carlos's review: em dash, one sentence, move section, answer regex question | Use `Downloads/PR4_Reply.docx` |
| **Consolidate CTAs on landing page** | Research says single CTA converts 32% better. Currently 8 different actions. | Evil Martians study |
| **Remove period from "Where Regula fits in the market." heading** | Non-standard | `site/index.html` |
| **Re-measure precision formally** | The 85.9% was measured this session but not published in `benchmarks/` | Create `benchmarks/results/APP_PRECISION.json` |
| **Consider position pivot** | "Compliance CLI" → "Risk scanner" per Honest Assessment | README, landing pages, pyproject.toml |

### Nice-to-have (after Show HN)

| Item | Reference |
|---|---|
| Add South Korea AI Basic Act crosswalk data | Market strategy report |
| Add Brazil Marco Legal da IA crosswalk data | Market strategy report |
| Run 5 user validation interviews | `docs/user-validation/protocol.md` + leads doc |
| Consolidate TODO.md into ROADMAP.md | Phase 2 diagnosis |
| Update global `~/.claude/CLAUDE.md` counts (55→59, 1055→1199) | Out of sync with project CLAUDE.md |
| Fix 2 flaky subprocess timeout tests | `test_check_large_scan_no_crash`, `test_regula_self_scan_clean` |
| Fix SyntaxWarnings in ast_context.py | 11 warnings about escape sequences (cosmetic, not functional) |
| Implement Phase C (taint analysis) for library-code precision | Deep inspection report |

---

## 4. File-by-File Change Map

### Modified (27 files)

| File | Nature of change |
|---|---|
| `CLAUDE.md` | Counts updated, GSC removed, CLI Pattern removed, VERSION fix |
| `.claude/commands/verify.md` | Doctor count fix, stale commit hash removed |
| `.claude/skills/regula/SKILL.md` | Framework count + CLI syntax fixes |
| `CONTRIBUTING.md` | CLI invocation, test count, issue template ref |
| `docs/architecture.md` | File listings, counts, filter keys |
| `docs/cli-reference.md` | 4 new commands added |
| `docs/evidence-pack-guide.md` | --bundle, --sign, --timestamp sections |
| `scripts/agent_monitor.py` | AI output patterns, path segments, send_message, SDK chain, conflation fix |
| `scripts/aibom.py` | Import scanning fallback |
| `scripts/constants.py` | .github/.gitlab/.circleci added to SKIP_DIRS |
| `scripts/report.py` | AST context integration, generic finding removal, library infra penalty, eval ungating, provenance fix, scan_files.last_stats |
| `scripts/risk_patterns.py` | 9 regex bug fixes (lookahead, boundaries, temperature, resume, CamelCase) |
| `scripts/scan_cache.py` | Schema bump v2→v3, report.py in fingerprint |
| `site/index.html` | Name removed, em dashes, blog changes |
| `site/locales/de.html` | Em dashes, name never present |
| `site/locales/pt-br.html` | Em dashes, name never present |
| `site/blog/writing.html` | Minor |
| `site/regions/uae.html` | Minor |
| `ROADMAP.md` | Shipped items marked |
| `benchmarks/results/*.json` | Re-run benchmark results |
| `tests/test_agent_governance.py` | Fixtures updated for precision changes |
| `tests/test_classification.py` | torch.load safe test updated |
| `tests/test_report.py` | tensorflow test updated for new behaviour |

### New (untracked, 10 files)

| File | Purpose |
|---|---|
| `scripts/ast_context.py` | AST line-context map for Phase B precision |
| `.claude/skills/gsc/SKILL.md` | GSC skill (extracted from CLAUDE.md) |
| `HANDOVER.md` | This file |
| `benchmarks/results/app_*.json` (5 files) | Application-code benchmark results |
| `site/blog/blog-aicdi-governance-gaps.html` | Blog post (from earlier session work) |
| `site/blog/blog-scanning-10-ai-apps.html` | Blog post (from earlier session work) |

### Deleted

| File | Reason |
|---|---|
| `.claude/plan.md` | Stale (referenced old milestones) |
| `docs/tmp*_annex_iv.md` (307 files) | Generated artifacts, never tracked |
| `evidence-pack-cv-screening-app-2026-04-19/` | Generated artifact left in root |

---

## 5. Verified Numbers (as of 2026-04-20)

| Metric | Value | How to verify |
|---|---|---|
| CLI commands | 59 | `grep -c "subparsers.add_parser" scripts/cli.py` |
| Tests | 1,199 | `python3 -m pytest tests/ --collect-only -q` |
| Pattern categories | 52 | Count dicts in risk_patterns.py |
| Individual regexes | 404 | Sum all pattern lists |
| Self-test | 6/6 | `python3 -m scripts.cli self-test` |
| Doctor | 9 pass + 2 info | `python3 -m scripts.cli doctor` |
| App-code precision (raw) | 85.9% | 334 TP / 55 FP across 13 repos |
| App-code precision (--skip-tests) | 99.7% | 334 TP / 1 FP |
| Library-code precision | ~20% | Structural limit, not fixable without Phase C |
| Commits ahead of remote | 18 (plus this session's uncommitted work) | `git rev-list --count origin/main..HEAD` |

---

## 6. How to Resume

```bash
# 1. Verify tests pass
python3 -m scripts.cli self-test && python3 -m pytest tests/ -q

# 2. Update stale counts (README, data/site_facts.json, data/site_facts.md)
# Commands: 55→59, Tests: 1055→1199
# grep -rn "55 commands\|1,055\|1055" README.md data/ site/

# 3. Update precision on landing pages (15.2% → new disclosure)
# Honest framing: "85.9% precision on application code; 15-20% on AI library source code"

# 4. Commit all changes (suggest splitting into logical commits):
#    a) feat: precision improvements (Phase A + B)
#    b) docs: documentation audit updates
#    c) chore: repo cleanup (.gitignore, temp files)
#    d) feat(site): landing page copy improvements

# 5. Push
git push origin main

# 6. Fix PR #4 (use Downloads/PR4_Reply.docx for the comment)
# Then push the code fix to the PR branch

# 7. Run Show HN prep (Tuesday 22 April)
```

---

## 7. Key Decisions Made This Session

| Decision | Rationale | Evidence |
|---|---|---|
| Reposition from "compliance CLI" to "risk scanner" | The tool cannot verify compliance; it detects risk indicators. Carlos's review exposed this. | Honest Assessment doc, EU AI Act primary source research |
| Build application-code benchmark (not just library code) | The old 15.2% was measured on AI SDKs, which is like scanning a firewall for vulnerabilities. Real users scan their own apps. | 13-project benchmark, 85.9% precision |
| Don't suppress patterns to inflate precision | Industry standard is better patterns + AST context + taint analysis, not suppression. NIST SATE, OWASP Benchmark methodologies confirm. | SAST precision research (ISSTA 2024, Ghost Security 2025, Semgrep docs) |
| Multi-jurisdiction is the best moat | OneTrust (300 jurisdictions) and Vanta (35 frameworks) prove this model. South Korea + Brazil are the next targets. | Market strategy research |
| $50K-500K ARR is realistic year 1-2 | No code-level AI Act scanner has verified paying customers. Market is pre-revenue. Bootstrap, don't raise VC. | Competitor pricing research |
| User validation before more features | 0 of 5 interviews completed. No validated problem. Show HN will provide signal. | PMF assessment |

---

## 8. Known Risks

| Risk | Impact | Mitigation |
|---|---|---|
| **18 commits + session work unpushed** | Data loss (single machine) | Push immediately next session |
| **Show HN in 2 days (Tue 22 April)** | Launching with stale counts and misleading precision number | Update before push |
| **Omnibus trilogue agreement ~28 April** | Could change deadline from Aug 2026 to Dec 2027 (reduces urgency) | Already documented in CLAUDE.md; all deadlines have Omnibus caveat |
| **Carlos's PR review unanswered** | Delays awesome-eu-ai-act listing | Reply + fix ready in Downloads |
| **SyntaxWarnings in ast_context.py** | 11 warnings on import — cosmetic but visible to users | Fix escape sequences (add `r` prefix) |
| **2 flaky timeout tests** | May show failures in CI on slow runners | Tests pass in isolation; only fail under load |

---

## 9. Session Statistics

- Duration: ~14 hours across 19-20 April 2026
- Research agents spawned: 20+
- Files modified: 27
- Files created: 10
- Files deleted: 308 (307 temp + 1 artifact dir)
- Precision improvement: 15.2% → 85.9% (application code)
- Recall improvement: eval(completion) vulnerability now detected
- Documents produced: 5 (Downloads folder)
