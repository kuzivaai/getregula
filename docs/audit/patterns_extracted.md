# Patterns Extracted from Reference Security/Governance Skills

**Date:** 2026-03-27
**Repos studied:**
- `shuvonsec/claude-bug-bounty` (1.2k stars, MIT) — AI-powered bug bounty hunting harness
- `anthropics/claude-code-security-review` (4k+ stars, MIT) — GitHub Action for PR security review

**Regula version analysed:** 1.1.0

---

## 1. Architectural Patterns Worth Adopting

### 1.1 Layered Agent Specialisation (claude-bug-bounty)

The bug bounty repo uses **7 specialised agents** (`agents/*.md`), each with a single responsibility: `recon-agent.md`, `validator.md`, `report-writer.md`, `chain-builder.md`, `autopilot.md`, `recon-ranker.md`, `web3-auditor.md`. Each agent file is a self-contained prompt document with its own decision logic, not a monolithic instruction set.

**What Regula lacks:** Regula puts all governance logic into `classify_risk.py` and `pre_tool_use.py`. There is no concept of specialised agent roles — the same code path handles prohibited practice detection, high-risk flagging, credential checking, and GPAI awareness. Splitting into composable agent definitions (e.g., `agents/prohibited-checker.md`, `agents/article-assessor.md`, `agents/gpai-evaluator.md`) would make each concern independently testable and allow users to enable/disable specific governance checks.

**Concrete pattern:**
```
agents/
  prohibited-checker.md   # Article 5 only — hard block
  risk-assessor.md        # Articles 6-15 — classification + guidance
  gpai-evaluator.md       # Articles 53-55 — training activity awareness
  credential-guardian.md  # Secret detection
  compliance-auditor.md   # Gap analysis orchestration
```

### 1.2 Two-Stage Filtering Pipeline (claude-code-security-review)

`claudecode/findings_filter.py` implements a two-stage approach:
1. **Hard exclusion rules** — regex-based pattern matching via `HardExclusionRules` class, with pre-compiled patterns across 7 categories (DoS, rate limiting, resource management, open redirects, regex injection, memory safety, SSRF). These are fast and deterministic.
2. **Claude API analysis** — remaining findings pass through `ClaudeAPIClient.analyze_single_finding()` for contextual false-positive filtering with confidence scoring.

**What Regula lacks:** Regula's `classify_risk.py` does only stage 1 (regex patterns). There is no second-pass contextual analysis. For governance, this means regex matches like "social_scoring" or "biometric" trigger without any contextual understanding of whether the code actually implements a prohibited practice or merely discusses one. Adding a lightweight LLM-based second pass for high-risk and prohibited findings would dramatically reduce false positives.

**Key implementation detail from the reference:** The filter gracefully degrades — if the Claude API is unavailable, findings are preserved with default confidence scores rather than lost. Regula should adopt this same resilience pattern.

### 1.3 Structured Command Interface with Slash Commands (claude-bug-bounty)

13 slash commands in `commands/*.md`, each a standalone markdown file that defines:
- Input parameters
- Execution phases
- Decision logic
- Output format
- Stop conditions

Commands reference each other (e.g., `/hunt` tells you to run `/validate` before reporting). This creates a discoverable workflow graph.

**What Regula has:** 14 slash commands defined in `SKILL.md` as a table. The actual logic lives in `scripts/cli.py` as Python functions. The commands are not self-documenting markdown files — they are code paths behind argparse. This means users cannot read the command definition to understand what it will do before running it.

**Recommendation:** Create `commands/*.md` files for each `/regula-*` command. These serve as both documentation and prompt context when the skill is loaded. The bug bounty pattern of having each command file describe its own phases, decision gates, and output format is superior for user trust in governance tooling.

### 1.4 Confidence Scoring with Thresholds (claude-code-security-review)

`claudecode/prompts.py` enforces a confidence range of 0.7-1.0 for reported findings. Anything below 0.7 is suppressed. Each finding carries: file path, line number, severity, vulnerability category, description, exploit scenario, recommendations, and confidence score.

**What Regula has:** A `confidence_score` field (0-100 integer) on `Classification` objects, but it is underutilised. The CLI displays it in brackets `[score]` but there is no configurable threshold to suppress low-confidence findings. The `regula-policy.yaml` has `thresholds` for blocking but no `min_confidence` setting.

**Recommendation:** Add `min_confidence_score` to `regula-policy.yaml` thresholds. Default to 40 (equivalent to 0.4). Allow users to tune this to reduce noise in projects that trigger many pattern matches.

### 1.5 File-Type-Aware Filtering (claude-code-security-review)

`findings_filter.py` excludes memory safety findings from non-C/C++ files and SSRF findings from HTML files. This prevents nonsensical cross-language false positives.

**What Regula lacks:** Risk classification in `classify_risk.py` does not consider file type. A Python file importing `torch` and a markdown file discussing torch training both trigger the same indicators. Adding file-extension awareness to the pattern matching would be a low-effort, high-impact improvement.

---

## 2. Validation/Filtering Approaches Missing from Regula

### 2.1 The 7-Question Gate (claude-bug-bounty)

`agents/validator.md` and `commands/validate.md` implement a sequential validation gate. Seven questions are asked in order; the first "NO" terminates evaluation:

1. Can you reproduce this immediately?
2. Is this bug class in scope?
3. Is the asset in scope?
4. Does it require unobtainable access?
5. Has it been previously disclosed?
6. Can you show actual harm?
7. Does it fall under never-submit categories?

Four verdicts result: **PASS**, **KILL**, **DOWNGRADE**, **CHAIN REQUIRED**.

**Regula equivalent needed:** A governance validation gate for findings before they reach reports or CI/CD pipelines:

1. Is this file actually part of a deployed AI system (vs. test/docs/example)?
2. Does the code implement the flagged behaviour (vs. merely importing a library)?
3. Is there evidence of the specific prohibited/high-risk use case (vs. a general-purpose library)?
4. Does the deployment context match a regulated scenario?
5. Has this finding been previously reviewed and accepted/suppressed?

This would live as a `/regula-validate` command or as a filtering stage in `report.py`.

### 2.2 Never-Submit / Always-Reject Categories (claude-bug-bounty)

`rules/hunting.md` and `rules/reporting.md` define explicit categories that are always rejected unless chained with stronger evidence:
- Open redirects alone
- CORS misconfiguration without data theft proof
- SSRF without data exfiltration
- Missing security headers without functional exploitation
- GraphQL introspection alone

**Regula equivalent:** Define explicit "always-suppress" categories for governance findings that are reliably false positives:
- `import torch` / `import tensorflow` in test files
- AI library mentions in `requirements.txt` / `package.json` without corresponding code
- Discussion of prohibited practices in documentation or comments
- Model files in `.gitignore`-d directories

These could be codified in `regula-policy.yaml` under a new `always_suppress` section, separate from the path-based `exclusions`.

### 2.3 Hard Exclusion Rules with Statistics (claude-code-security-review)

`findings_filter.py` tracks comprehensive filtering statistics: exclusion breakdowns by category, confidence score distributions, and runtime performance. This lets users understand why findings were filtered and tune their configuration.

**What Regula lacks:** When findings are suppressed (via `# regula-ignore` or path exclusions), no statistics are reported. The CLI shows `Suppressed: N` but not why. Adding a `--verbose` flag that shows exclusion reasons per finding would build user trust.

---

## 3. CLI/UX Patterns

### 3.1 Phased Workflow with Clear Stop Signals (claude-bug-bounty)

`commands/hunt.md` defines 5 phases with explicit stop signals:
- Phase 1: Scope reading (stop if scope unclear)
- Phase 2: Tech stack detection (stop if nothing interesting after 5 minutes)
- Phase 3: Targeted testing
- Phase 4: Signal chaining
- Phase 5: Documentation

The 5-minute rule and 20-minute rotation rule prevent rabbit-holing.

**Regula equivalent:** The `/regula-classify` and `/regula-gap` commands run to completion with no intermediate feedback. For large projects, adding phase-based output (e.g., "Phase 1: Scanning 847 files... Phase 2: Classifying 23 AI-related files... Phase 3: Assessing 4 high-risk candidates...") would improve UX and allow early termination.

### 3.2 Resume/Remember Pattern for Persistent Sessions (claude-bug-bounty)

`/resume target.com` loads previous hunt state: session count, tested endpoints, untested endpoints, and pattern-based suggestions from `memory/pattern_db.py`.

`/remember` saves findings to `journal.jsonl` (always) and `patterns.jsonl` (conditionally) with schema validation.

**What Regula lacks:** Each `regula check` run is stateless. There is no concept of "resume where you left off" or "remember this finding for next time." The audit log (`log_event.py`) records events but is not queryable for resumption. Adding a `/regula-resume` that loads the last scan results and shows what changed would be valuable for iterative compliance work.

### 3.3 Report Title Formula (claude-bug-bounty)

`rules/reporting.md` mandates: `[Bug Class] in [Endpoint] allows [role] to [impact]`.

**Regula equivalent for findings:** Currently findings are described as free-text strings. Adopting a structured format like `[Risk Tier] in [file:line] — [indicator] may indicate [article] obligation` would make findings more scannable in reports and CI output.

### 3.4 Exit Code Convention (claude-code-security-review)

`github_action_audit.py` uses specific exit codes: configuration errors, general failures, and high-severity findings each get distinct codes.

**What Regula has:** `cli.py` uses exit code 2 for prohibited, 1 for high-risk (with `--strict`), 0 otherwise. This is good but not documented. The CI workflow (`ci.yaml`) only runs tests — it does not use Regula's own exit codes as a gate. Regula should eat its own dog food: the CI pipeline should run `regula check` on the Regula codebase itself.

---

## 4. Memory/State Management

### 4.1 JSONL Append-Only Logs with File Locking (claude-bug-bounty)

`memory/hunt_journal.py` and `memory/pattern_db.py` both use:
- JSONL format (one JSON object per line)
- `fcntl.flock()` for thread-safe concurrent writes
- Schema validation before writing (via `memory/schemas.py`)
- Graceful corruption handling (skip bad lines with warning, don't crash)
- Query methods with AND-logic filtering

**What Regula has:** `log_event.py` uses a similar JSONL append-only pattern with `fcntl.flock()` and hash chaining. However, it lacks:
- Schema validation on write (entries are free-form dicts)
- Graceful corruption recovery (unverified — needs testing)
- Rich query methods (the audit log has `query` but it is basic)

**Recommendation:** Add schema validation to `log_event.py` entries using a `schemas.py` module. Define entry types: `classification`, `blocked`, `secret_detected`, `tool_use`, `scan_result`, `compliance_update`. This makes the audit trail queryable and verifiable by external auditors.

### 4.2 Four Distinct Entry Types with Schemas (claude-bug-bounty)

`memory/schemas.py` defines four entry types, each with required and optional fields, type validation, enum validation, and ISO 8601 timestamp enforcement:
- Journal entries (hunting actions)
- Pattern entries (successful techniques)
- Target profiles (per-target state)
- Audit entries (HTTP requests)

Helper functions (`make_journal_entry()`, `make_pattern_entry()`, `make_audit_entry()`) auto-populate timestamps and validate.

**What Regula should adopt:** Define governance-specific entry types:
- `finding_entry` — risk indicator detection with file, line, tier, confidence, indicators
- `decision_entry` — human override of a finding (accept, suppress, escalate)
- `compliance_entry` — status change for a registered system
- `scan_entry` — metadata for a scan run (files scanned, duration, counts)
- `review_entry` — external review sign-off

### 4.3 Pattern Learning Across Targets (claude-bug-bounty)

`memory/pattern_db.py` stores successful techniques and matches them against new targets by vulnerability class and technology stack overlap. Results are ranked by "highest payout first, then most recent."

**Regula equivalent:** Store which indicators were confirmed as true positives vs. false positives across projects. When scanning a new project with a similar tech stack, adjust confidence scores based on historical accuracy. This is a medium-term feature but architecturally, the JSONL + schema pattern makes it feasible.

### 4.4 Rate Limiting and Circuit Breaker (claude-bug-bounty)

`memory/audit_log.py` includes `RateLimiter` and `CircuitBreaker` classes:
- Per-host request throttling (10 req/s for recon, 1 req/s for vuln testing)
- Circuit breaker that trips after 5 consecutive failures, with 60s cooldown

**Regula relevance:** Not directly applicable to governance scanning, but relevant if Regula adds features that call external APIs (e.g., vulnerability database lookups for dependency scanning, or LLM-based contextual analysis). The pattern is worth noting for future architecture.

---

## 5. GitHub Action Integration

### 5.1 How claude-code-security-review Does It

**`action.yml`** defines:
- Required input: `claude-api-key`
- Optional inputs: `comment-pr`, `upload-results`, `exclude-directories`, `claude-model`, `claudecode-timeout`, `run-every-commit`, `false-positive-filtering-instructions`, `custom-security-scan-instructions`
- Outputs: `findings-count`, `results-file`
- Permissions needed: `pull-requests: write`, `contents: read`

**`github_action_audit.py`** orchestrates:
1. Retrieve PR metadata and file changes via GitHub API
2. Filter excluded directories and auto-generated files (protobuf, OpenAPI markers)
3. Build security audit prompt from `prompts.py` with PR context and diffs
4. Execute Claude Code with retry logic (3 attempts, exponential backoff to 15s)
5. Handle "prompt too long" by re-running without diff content
6. Parse JSON findings from Claude response
7. Apply two-stage false positive filtering
8. Post findings as PR review comments on specific lines
9. Upload results as artifacts
10. Return exit codes

**Key design decisions:**
- Caching to avoid re-analysing the same code on PRs with many commits
- Race-condition prevention through marker-based reservations
- Graceful degradation when API calls fail
- Custom instructions via external file paths (not inline YAML)

### 5.2 What Regula Should Build

Regula's current CI integration is minimal: `ci.yaml` runs `python tests/test_classification.py` on push/PR. There is no GitHub Action that users can install in their own repos.

**Recommended `action.yml` for Regula:**

```yaml
name: "Regula AI Governance Check"
description: "Scan PRs for EU AI Act risk indicators"
inputs:
  policy-file:
    description: "Path to regula-policy.yaml"
    default: "regula-policy.yaml"
  fail-on-prohibited:
    description: "Fail the check if prohibited indicators found"
    default: "true"
  fail-on-high-risk:
    description: "Fail the check if high-risk indicators found"
    default: "false"
  min-confidence:
    description: "Minimum confidence score to report (0-100)"
    default: "40"
  comment-pr:
    description: "Post findings as PR comments"
    default: "true"
  format:
    description: "Output format (sarif, json, text)"
    default: "sarif"
  exclude-directories:
    description: "Comma-separated directories to skip"
    default: "tests,docs,examples"
outputs:
  findings-count:
    description: "Total findings count"
  prohibited-count:
    description: "Prohibited indicator count"
  results-file:
    description: "Path to results file"
```

**Implementation steps:**
1. Copy the retry + fallback pattern from `github_action_audit.py`
2. Use `regula check --format sarif` output for GitHub Code Scanning integration (SARIF upload)
3. Use `regula check --format json` for PR comment generation
4. Add incremental scanning: compare against baseline from the base branch, only report new findings
5. Upload SARIF to GitHub Code Scanning API for native security tab integration

**SARIF integration is the highest-value action item.** Regula already generates SARIF output (`cli.py` supports `--format sarif`). Wiring this into a GitHub Action that uploads to the Code Scanning API would give Regula native GitHub security tab presence with zero additional UI work.

### 5.3 Self-Hosted vs. API-Based

The security review action requires a Claude API key because it uses LLM analysis. Regula's pattern-based approach needs no API key — it can run entirely locally. This is a significant advantage: no secrets management, no API costs, faster execution.

For the optional LLM-based second-pass filtering (section 1.2), follow the security review pattern: accept an optional `claude-api-key` input, gracefully degrade if not provided.

---

## Summary: Priority Adoption List

| Priority | Pattern | Source | Effort | Impact |
|----------|---------|--------|--------|--------|
| 1 | GitHub Action with SARIF upload | security-review | Medium | High — native GH integration |
| 2 | Confidence threshold in policy | security-review | Low | High — reduces false positive noise |
| 3 | File-type-aware pattern matching | security-review | Low | Medium — fewer nonsensical matches |
| 4 | Validation gate for findings | bug-bounty | Medium | High — trust in governance output |
| 5 | Schema-validated audit entries | bug-bounty | Medium | Medium — auditability |
| 6 | Command markdown files | bug-bounty | Low | Medium — discoverability |
| 7 | Two-stage filtering (regex + LLM) | security-review | High | High — dramatic FP reduction |
| 8 | Always-suppress categories in policy | bug-bounty | Low | Medium — configurable noise reduction |
| 9 | Phased CLI output | bug-bounty | Low | Low — better UX |
| 10 | Pattern learning across scans | bug-bounty | High | Medium — long-term accuracy |
