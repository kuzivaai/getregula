# Regula Roadmap

Last updated: 2026-04-07

Items are prioritised by competitive gap severity and implementation feasibility.
Status: Backlog → In Progress → Done.

Source: 57-tool competitive analysis, April 2026.

---

## Priority: High

### Publish precision/recall benchmarks
- **Gap:** No published accuracy metrics. Quethos Sentinel claims 99.8% precision.
- **What:** Run benchmark suite against labelled open-source projects, publish precision/recall numbers in README and on the website.
- **Feasibility:** Low effort — `regula benchmark` already exists. Need labelled test data.

### Publish scan time benchmarks
- **Gap:** Systima claims 8-second scans on 20k-star repos. Regula has no published scan time.
- **What:** Time `regula check` against well-known repos (langchain, transformers, openai-python). Publish results.
- **Feasibility:** Low effort — `time` command. Add to README.

### PR inline comments for CI/CD
- **Gap:** Systima Comply and Sentinel post findings as PR comments. Regula only outputs SARIF/JSON.
- **What:** GitHub Action enhancement that posts findings as inline PR review comments on changed files.
- **Feasibility:** Low effort — GitHub API, findings already have file:line data.

### Jupyter notebook scanning (.ipynb)
- **Gap:** Quethos Sentinel scans Jupyter notebooks. Regula does not — `.ipynb` is not in `CODE_EXTENSIONS`.
- **What:** Add notebook parser that extracts code cells and feeds them through existing classification pipeline.
- **Feasibility:** Medium — JSON parsing of .ipynb format. ML/data science is a major Regula audience.

---

## Priority: Medium

### Domain-based severity adjustment
- **Gap:** Systima lets users declare their system domain (healthcare, finance) to adjust risk severity. Regula treats all code the same.
- **What:** Add `--domain` flag or `regula-policy.yaml` config that adjusts confidence scores based on declared domain.
- **Feasibility:** Low effort — config file addition, score multiplier in classify.

### Conformity assessment for LGPD / Marco Legal da IA
- **Gap:** `regula conform` generates EU AI Act evidence only. Gap command supports LGPD/Marco Legal but conform pack doesn't.
- **What:** Extend `conform.py` to include LGPD article cross-references when `--framework` flag is set.
- **Feasibility:** Medium — framework mapper data exists, needs integration.

### JS/TS AST analysis depth
- **Gap:** Systima uses TypeScript Compiler API + tree-sitter WASM for deep AST analysis. Regula uses regex for JS/TS.
- **What:** Use existing tree-sitter optional dep for JS/TS pattern matching. Degrade gracefully when not installed.
- **Feasibility:** Medium — tree-sitter is already optional dep.

### MCP server documentation and discovery
- **Gap:** ark-forge and SonnyLabs MCP servers are documented for Claude/Cursor/Windsurf. Regula has `mcp-server` but it's not documented.
- **What:** Document MCP server usage in README and landing page. Add example configs for Claude Code, Cursor, Windsurf.
- **Feasibility:** Low effort — feature exists, just needs docs.

### R language support
- **Gap:** Quethos Sentinel scans R. Regula doesn't.
- **What:** Add `.R` and `.r` to `CODE_EXTENSIONS`. R-specific patterns for tidymodels, caret, mlr3.
- **Feasibility:** Medium — pattern research needed. R is significant in academic/statistical AI.

### CE Marking workflow
- **Gap:** Modulos has explicit CE Marking workflow for high-risk systems. Regula's conform pack stops at evidence generation.
- **What:** Add `regula ce-mark` command that generates the EU declaration of conformity in the format required for CE marking.
- **Feasibility:** Low — declaration template already exists in conform pack. Needs format compliance check.

### Triage tickets (not just plans)
- **Gap:** Quethos generates triage tickets. Regula generates remediation plans but not tickets.
- **What:** Add `--export jira|github|linear` flag to `regula plan` that creates issues directly.
- **Feasibility:** Low — plan output already structured. Just needs API integrations.

### Slack/Teams webhook integration
- **Gap:** tibet-audit posts to webhooks. Regula has no notification channels.
- **What:** Add `--webhook URL` flag to `regula check --ci` that posts summary to Slack/Teams on findings.
- **Feasibility:** Low — single HTTP POST.

### Multi-jurisdiction frameworks (Asian, African, Americas)
- **Gap:** tibet-audit covers PIPA (Korea), APPI (Japan), PDPA (Singapore), Gulf PDPL, NDPR (Nigeria). Centraleyes CAIF covers California/Colorado/China AI laws. Regula has 12 frameworks but mostly EU/Brazil.
- **What:** Add framework mappings for: California AI law (SB 1047), Colorado AI Act, South Korea AI Act, China AI regulations, Japan APPI, Singapore PDPA.
- **Feasibility:** High effort — requires legal research per jurisdiction. Phase by region.

### Multi-EU-regulation coverage
- **Gap:** EuroComply covers AI Act + NIS2 + GDPR + CRA + Data Act + VdS 10000. Regula covers AI Act + CRA only.
- **What:** Extend Regula to detect NIS2 and GDPR-relevant patterns for AI systems processing personal data.
- **Feasibility:** Medium — new pattern set, but framework_mapper architecture supports it.

### Self-attesting audit chain → externally witnessed
- **Gap:** Sentinel has immutable evidence ledger. Regula's SHA-256 manifest is self-attesting (a local user can rewrite it).
- **What:** Optional integration with external timestamping (already have RFC 3161 in `timestamp.py`). Document as best practice.
- **Feasibility:** Low — code exists, needs integration with conform pack output.

---

## Priority: Low (different tool category — not planned)

These are capabilities of fundamentally different tools. Documented for awareness, not planned for Regula.

- **Runtime monitoring** (Holistic AI, OneTrust, IBM watsonx, MS AGT)
- **Bias/fairness model testing** (EuConform CrowS-Pairs, Holistic AI) — would require executing models
- **AI red-teaming / LLM output testing** (Promptfoo) — Regula is static, not behavioural
- **PII redaction at runtime** (AgentGuard) — Regula detects credentials but doesn't intercept
- **Content watermarking** (SonnyLabs) — runtime concern, not static
- **Deepfake labelling generation** (SonnyLabs) — different problem
- **Offline LLM-assisted classification** (EuConform with Ollama) — Regula is pure static analysis
- **SSO/RBAC/multi-user** (all enterprise platforms) — not relevant for CLI
- **Executive dashboards** (all enterprise platforms) — not relevant for CLI
- **Approval workflows** (all enterprise platforms) — not relevant for CLI
- **Model lifecycle management** (ValidMind, IBM) — different category
- **Vendor AI risk management** (Trustible, Monitaur) — different category
- **Web UI / dashboard for non-CLI users** — Regula is CLI-first by design

---

## Honest comparison gaps

These are things we cannot answer until we measure:

- **How does Regula compare to ValidMind's "60% documentation automation"?** — needs side-by-side test
- **How does Regula compare to Modulos's "90% time reduction"?** — needs side-by-side test
- **Is Regula more or less precise than Quethos Sentinel's claimed 99.8%?** — needs benchmark comparison
- **Is Regula faster than Systima's 8-second scan?** — needs benchmark comparison

---

## Done (2026-04-06 session)

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
- [x] CI fix: updated YAML hook test for security-hardened bypass
