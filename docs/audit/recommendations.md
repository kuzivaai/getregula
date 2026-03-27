# Regula v1.2 — Prioritised Improvement Roadmap

**Based on:** Technical audit, real-world benchmark, competitive gap analysis, reference skill patterns
**Date:** 2026-03-27

---

## P0: Fix Now (Bugs That Undermine Credibility)

| # | Issue | File | Fix | Effort |
|---|-------|------|-----|--------|
| 1 | `import fcntl` unconditional in classify_risk.py crashes Windows | `classify_risk.py:16` | Remove unused import (fcntl is not used in this file) | 5 min |
| 2 | SARIF version hardcoded as "1.0.0" | `report.py:595` | Change to "1.1.0" | 5 min |
| 3 | `sentenc` regex in justice pattern causes false positives | `classify_risk.py` HIGH_RISK_PATTERNS["justice"] | Change `r"sentenc"` to `r"sentenc\w*\W{0,5}(court|judge|judicial|legal|verdict|criminal)"` | 15 min |
| 4 | README says "105+ tests" — actual count is 109 | `README.md` | Update to "109 tests" | 2 min |
| 5 | Roadmap says "v2.0: AST-based analysis" but AST is already shipped | `README.md` | Remove from roadmap, it's done | 2 min |

## P1: Fix Soon (Technical Debt That Limits Growth)

| # | Issue | Fix | Effort |
|---|-------|-----|--------|
| 6 | tree-sitter integration is a stub that always raises ImportError | Implement `_tree_sitter_parse()` in ast_engine.py to actually use tree-sitter when installed | 2-3 days |
| 7 | ast_engine.py bare import breaks when used as package | Add `sys.path.insert(0, ...)` like other modules | 5 min |
| 8 | requirements.txt `-r` includes not followed | Add recursive include parsing to `parse_requirements_txt()` | 2 hours |
| 9 | pyproject.toml optional-dependencies parser has dead code | Fix regex to actually extract optional deps | 1 hour |
| 10 | No file size guard — OOM on large files | Add max file size check (e.g., skip files >1MB) | 30 min |
| 11 | Advisory version matching is exact-string only | Add semver-aware version range checking | 2 hours |
| 12 | Confidence threshold not configurable in policy | Add `min_confidence` to policy thresholds | 30 min |

## P2: Build Next (Competitive Gap Closers — High Value)

| # | Feature | Competitive Gap | Effort | Value |
|---|---------|----------------|--------|-------|
| 13 | Complete tree-sitter JS/TS with data flow tracing | Systima Comply parity | 3-5 days | High — many AI apps are Node.js |
| 14 | Add Java + Go import detection (regex) | ArkForge parity (partial) | 1-2 days | Medium — enterprise AI is often Java |
| 15 | Add OWASP LLM Top 10 + MITRE ATLAS mapping | Agent-BOM parity (partial) | 2-3 days | High — OWASP is the security standard |
| 16 | Two-stage filtering: regex then LLM for high-risk/prohibited | Reference skill pattern (claude-code-security-review) | 3-5 days | High — dramatically reduces false positives |
| 17 | GitHub Action wrapper | Every competitor has one | 1 day | Critical — CI/CD is the adoption path |
| 18 | Recommend pip-audit/osv-scanner in output | Close the "50K advisories" perception gap | 1 hour | Important — honest positioning |

## P3: Build Later (Nice-to-Have, Differentiation)

| # | Feature | Effort |
|---|---------|--------|
| 19 | Cross-file data flow tracing (import graph resolution) | 5-8 days |
| 20 | Slash command markdown files (claude-bug-bounty pattern) | 2 days |
| 21 | NIST CSF 2.0, SOC 2, ISO 27001 framework mappings | 2-3 days |
| 22 | pom.xml, go.mod, Cargo.toml dependency parsing | 1-2 days |
| 23 | Rust, C, C++ regex import detection | 1 day |
| 24 | Multi-language obfuscation resistance | Research-level problem |
| 25 | Migrate to pytest | 1-2 days |

## Skip (Not Worth Building)

| # | What | Why |
|---|------|-----|
| — | General CVE/vulnerability database | pip-audit/osv-scanner already do this with 50K+ entries |
| — | Enterprise sales team | Business problem, not code problem |
| — | Analyst recognition (Gartner/Forrester) | Requires revenue, customers, maturity — years away |
| — | Runtime LLM call interception | Different product category (AIR Blackbox does this) |

---

## Execution Order

**Week 1: Fix credibility issues (P0 + P1)**
- Items 1-5 (30 minutes total)
- Items 6-12 (1-2 days)
- Run benchmark again to measure false positive reduction

**Week 2: GitHub Action + two-stage filtering**
- Item 17 (GitHub Action — critical for adoption)
- Item 16 (LLM-assisted false positive filtering — biggest quality improvement)

**Week 3-4: Language expansion + framework mapping**
- Item 13 (tree-sitter JS/TS)
- Item 14 (Java + Go)
- Item 15 (OWASP + MITRE ATLAS)

**After that:** P3 items based on user feedback and adoption data.
