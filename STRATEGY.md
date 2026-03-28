# Regula — Strategy

**As of 2026-03-28 · v1.2.0**

---

## What It Is

A developer-facing AI governance risk indication tool. Detects EU AI Act risk patterns in code at the point of creation. Runs as a Claude Code skill, Copilot/Windsurf hook, pre-commit hook, git hook, or standalone CLI.

It is a risk *indication* tool, not a legal classifier. Article 6 risk classification requires contextual human judgment — Regula flags patterns that warrant that review.

---

## Current State

| Dimension | Status |
|-----------|--------|
| Version | 1.2.0 (shipped 2026-03-28) |
| Tests | 348 functions, 916 assertions |
| Benchmark | LangChain (2,450 files) scanned in 16s |
| Real-world validated | LangChain, anthropic-cookbook, pydantic-ai, openai-python |
| External users | 0 |
| GitHub Action | Defined, untested in real PR workflow |

**What works well:**
- Python AST analysis — data flow tracing, oversight detection, logging proximity
- Compliance gap assessment (`regula gap`) — produces accurate 0-100 scores per Article 9-15
- Prohibited practice detection — 93%+ confidence on social scoring, emotion in workplace
- Dependency pinning analysis — 7 manifest formats, AI deps weighted 3x
- Real-time hook interception — blocks prohibited patterns before file writes
- `--skip-tests` + `--min-tier` — reduces LangChain 2,108 raw findings to 19 actionable

**Known weaknesses:**
- JS/TS analysis is regex-only (tree-sitter integration incomplete)
- No cross-file data flow (all tracing is single-file)
- False positive rate on general codebases (0/2 true positives on anthropic-cookbook high-risk findings)
- 1 advisory in the supply chain advisory database

---

## Market Position

**The gap we fill:** No incumbent AI governance platform works at the code level. All major players (Credo AI, Holistic AI, IBM OpenPages, Monitaur) operate at metadata/policy/workflow level. The developer persona is underserved.

**Direct competitors (all early-stage):**

| Competitor | Their Edge | Their Weakness vs Regula |
|-----------|-----------|--------------------------|
| Systima Comply | TS Compiler API + 4-pattern call-chain tracing | Closed source, TS/JS only |
| AIR Blackbox | Runtime interception, tested on 5,754 files | Different product category |
| EuConform | Offline-first, bias evaluation, PDF output | No hook integration |
| ArkForge MCP | 8 languages | Regex-only, no data flow, no hooks |
| Agent-BOM | 11 framework mappings, SBOM | Supply chain only, not code analysis |

**Where Regula leads:**
- Python AST depth (competitors are all regex)
- Real-time hook interception (Claude Code/Copilot/Windsurf)
- Compliance gap assessment (Articles 9-15 scored)
- Dependency pinning analysis (7 formats, AI-weighted)
- Offline, no external dependencies

**Moat:** Weak today — patterns are replicable, MIT-licensed. Potential moat is community adoption as a standard (ESLint model), pattern quality, and first-mover among developer tools.

---

## Business Models (Viable)

1. **Open-core** — free scanner, paid DPO dashboard + cloud audit trail + external timestamping
2. **Consulting accelerator** — Regula as intake tool for compliance assessments (lowest friction for early revenue)
3. **Integration licensing** — sell pattern library to enterprise platforms
4. **Acquisition target** — enterprise security vendors (Checkmarx, Snyk, Veracode) wanting EU AI Act capability

**Avoid:** Trying to compete with Credo AI / Holistic AI directly. They have enterprise sales, funding, analyst recognition. Build what they can't: code-level, developer-native.

---

## What to Build Next

### Immediate (before first public launch)

| # | Item | Why | Effort |
|---|------|-----|--------|
| 1 | Fix credit scorer false negative | Real compliance gap — `train_credit_model` scores minimal_risk | 2h |
| 2 | Advisory directory resolution fallback | Advisory loading fails depending on import method | 30m |
| 3 | Wire AST into documentation generator | Annex IV docs are ~80% blank despite AST producing the data | 1 day |
| 4 | ~~go.mod + build.gradle parsing~~ | ~~Missing dependency parsers for 2 of 8 supported languages~~ | ✅ Done |

### Short-term (v1.3 scope)

| # | Item | Why | Effort |
|---|------|-----|--------|
| 5 | Complete JS/TS tree-sitter flow tracing | Many AI apps are Node.js — biggest analysis gap | 3-5 days |
| 6 | AVID integration (AI vulnerability database) | AI-specific vulnerability intelligence pip-audit doesn't have | 2-3 days |
| 7 | Typosquatting detection | #1 supply chain attack vector, currently no coverage | 1 day |
| 8 | GitHub Action tested in real PR workflow | Adoption path — CI/CD is where developers live | 1 day |

### Deferred

| # | Item | Why deferred |
|---|------|-------------|
| — | Cross-file data flow | 5-8 days, complex. Single-file already catches most patterns. |
| — | DPO dashboard / web UI | Different product. Build after CLI has users. |
| — | General CVE database | pip-audit does this with 50K+ entries. Recommend as complement. |
| — | Enterprise sales / analyst recognition | Business problem, not a code problem. Requires funding. |

---

## Launch Checklist (Before Going Public)

- [x] Fix credit scorer false negative (#1 above)
- [ ] Test GitHub Action in a real PR workflow
- [ ] Get 5 human users (even internal/friendly)
- [ ] Post to r/Python or Hacker News
- [x] Verify advisory loading works in fresh install
- [x] Wire AST output into Annex IV docs

---

## Regulatory Timeline (Key Dates)

| Date | Requirement |
|------|-------------|
| **2025-02-02** | Article 5 prohibited practices — in force |
| **2025-08-02** | GPAI model rules — in force |
| **2026-08-02** | High-risk system requirements (Articles 9-15) — in force |
| 2027-12-02 | Annex III systems deadline (Digital Omnibus — proposed) |

The August 2026 deadline is 4 months away. This is the primary urgency driver for developer adoption.
