# Regula Roadmap

Last updated: 2026-04-06

Items are prioritised by competitive gap severity and implementation feasibility.
Status: Backlog → In Progress → Done.

---

## Priority: High

### Publish precision/recall benchmarks
- **Gap:** No published accuracy metrics. Quethos Sentinel claims 99.8%.
- **What:** Run benchmark suite against labelled open-source projects, publish precision/recall numbers in README and on the website.
- **Feasibility:** Low effort — benchmark tooling already exists (`regula benchmark`). Need labelled test data.
- **Status:** Backlog

### PR inline comments for CI/CD
- **Gap:** Systima Comply and Sentinel both post findings as PR comments. Regula only outputs SARIF/JSON.
- **What:** GitHub Action enhancement that posts findings as inline PR review comments on changed files.
- **Feasibility:** Low effort — GitHub API, findings already have file:line data.
- **Status:** Backlog

---

## Priority: Medium

### Domain-based severity adjustment
- **Gap:** Systima lets users declare their system domain (healthcare, finance, etc.) to adjust risk severity. Regula treats all code the same.
- **What:** Add `--domain` flag or `regula-policy.yaml` config that adjusts confidence scores based on declared domain. A credit scoring pattern in a fintech project scores higher than in a demo app.
- **Feasibility:** Low effort — config file addition, score multiplier in `_enrich_deadlines` or `classify`.
- **Status:** Backlog

### Conformity assessment for LGPD / Marco Legal da IA
- **Gap:** `regula conform` generates EU AI Act evidence only. The gap command already maps to LGPD and Marco Legal da IA, but the conformity pack doesn't include Brazilian framework references.
- **What:** Extend `conform.py` to include LGPD article cross-references in per-article evidence when `--framework lgpd` or `--framework marco-legal-ia` is passed.
- **Feasibility:** Medium — framework mapper data exists, needs integration into conform output.
- **Status:** Backlog

### JS/TS AST analysis depth
- **Gap:** Systima uses TypeScript Compiler API + tree-sitter WASM for deep AST analysis. Regula uses regex for JS/TS (Python has stdlib `ast`).
- **What:** Evaluate whether tree-sitter (already an optional dep) can be used for JS/TS AST-level pattern matching without breaking the zero-required-deps promise.
- **Feasibility:** Medium — tree-sitter is already optional. Would need to degrade gracefully when not installed.
- **Status:** Backlog

### MCP server discovery
- **Gap:** ark-forge and SonnyLabs offer MCP server integration for AI coding assistants. Regula has an MCP server (`regula mcp-server`) but it's not widely known.
- **What:** Document MCP server usage for Claude Code, Cursor, Windsurf. Add to README and landing page.
- **Feasibility:** Low effort — the feature exists, just needs documentation.
- **Status:** Backlog

---

## Priority: Low (different tool category)

These are capabilities that enterprise GRC platforms have but are fundamentally outside the scope of a CLI tool. Tracked for awareness, not planned.

- Runtime monitoring (Holistic AI, OneTrust, IBM watsonx)
- Bias/fairness testing (EuConform CrowS-Pairs, Holistic AI)
- SSO/RBAC/multi-user access (all enterprise platforms)
- Executive dashboards (all enterprise platforms)
- Approval workflows (all enterprise platforms)
- Model lifecycle management (ValidMind, IBM)
- Integration ecosystem (Databricks, Snowflake, MLflow)

---

## Done (this session, 2026-04-06)

- [x] Conformity assessment evidence pack (`regula conform`)
- [x] AI Bill of Materials with GPAI tiers (`regula sbom --ai-bom`)
- [x] Cross-file Article 14 human oversight analysis (`regula oversight`)
- [x] Omnibus-aware deadline tagging per finding
- [x] Timeline updated to April 2026 (trilogue, Transparency CoP)
- [x] Text classification for all 10 Annex III categories
- [x] Security: YAML/JSON removed from doc bypass, MCP path validation, git ref validation
- [x] SEO: JSON-LD structured data, og:image, sitemap update
- [x] Landing page: removed 8 unverifiable claims, added new features
- [x] README: documented all new commands with honest limitations
