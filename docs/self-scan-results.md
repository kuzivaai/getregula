# Regula Self-Scan Results

**Date:** 10 April 2026
**Version:** 1.6.1
**Command:** `regula check . --no-skip-tests`
**Commit:** 9fbf524 (main)

---

## Summary

| Metric | Value |
|---|---|
| Files scanned | 103 |
| Prohibited findings | 0 |
| Credential findings | 0 |
| High-risk findings | 2 |
| Agent autonomy findings | 3 |
| Limited-risk findings | 0 |
| Suppressed findings | 165 |
| BLOCK tier | 0 |
| WARN tier | 1 |
| INFO tier | 6 |

---

## Findings

### High-Risk Indicators

| Tier | Score | File | Category | Detail |
|---|---|---|---|---|
| WARN | 60 | `tests/fixtures/sample_warn_tier/hiring_system.py` | Employment and workers management | Add human oversight before automated hiring/employment decisions |
| INFO | 48 | `tests/fixtures/sample_high_risk/app.py` | Employment and workers management | — |

**Assessment:** Both findings are in test fixtures, not production code. `hiring_system.py` is a deliberately constructed test case for the WARN tier. `app.py` is a sample high-risk fixture used by the benchmark. These are true positives — the fixtures are designed to trigger these patterns.

### Agent Autonomy (OWASP Agentic ASI02/ASI04)

| Tier | Score | File | Detail |
|---|---|---|---|
| INFO | 30 | `tests/test_scan_cache.py:22` | AI output may flow to file system modification — no human gate detected |
| INFO | 30 | `tests/test_scan_cache.py:36` | AI output may flow to file system modification — no human gate detected |
| INFO | 30 | `tests/test_scan_cache.py:53` | AI output may flow to file system modification — no human gate detected |

**Assessment:** These are test file operations (writing to temporary cache files). The pattern matches `open(..., 'w')` in a file that also imports AI-related modules. These are false positives — the file writes are test cache operations, not AI-driven autonomous actions. This is a known limitation of regex-based detection: it cannot distinguish test infrastructure from production agent behaviour.

### Suppressed Findings

165 findings are suppressed via `# regula-ignore` comments. These are in:
- Test fixtures designed to contain patterns without triggering scan noise
- Scripts that handle file paths or configuration (legitimate file operations)
- The detection engine itself (which necessarily contains the patterns it scans for)

---

## Interpretation

Regula scanning its own codebase produces:
- **0 prohibited findings** — the tool does not implement any Article 5 practices
- **0 credential exposures** — no hardcoded API keys or secrets in production code
- **0 BLOCK-tier findings** — nothing that would fail a CI gate
- **1 WARN-tier finding** — a deliberate test fixture
- **6 INFO-tier findings** — 2 test fixtures (true positives by design) + 3 test infrastructure (false positives)

The self-scan demonstrates both the tool's capabilities and its known limitation: regex pattern matching will produce false positives on test infrastructure that happens to contain patterns similar to production AI code.

---

*This scan is re-run periodically and committed to the repository as a transparency artefact. If the results change materially, this file is updated with the new findings and an explanation of what changed.*
