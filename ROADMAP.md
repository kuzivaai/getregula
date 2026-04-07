# Regula Roadmap

Last updated: 2026-04-07

Items are prioritised by intrinsic value to Regula's users and implementation feasibility.
Status: Backlog → In Progress → Done.

> **Note on competitor references.** Earlier drafts of this roadmap cited specific
> vendor feature claims (e.g. "Competitor X claims 99.8% precision") as
> justification. Those claims were not backed by captured primary sources and have
> been removed. Roadmap items are now justified on their intrinsic merit to Regula's
> users. If a competitor claim is reintroduced, it must be backed by a dated
> primary-source capture in `references/competitive/<vendor>.md`.

---

## Priority: High

### ~~Jupyter notebook scanning (.ipynb)~~ — DONE 2026-04-07
- Implemented in `scripts/notebook.py` + wired into `report.py`. `.ipynb` is in `CODE_EXTENSIONS`. 3 tests cover extract/corrupt-file/end-to-end.
- Limitation: line numbers refer to position in the joined extracted source, not the original notebook cell. Cell-aware mapping is a future enhancement.

### Publish scan time benchmarks
- **Why:** Users (and prospects) ask "how fast is it on a real repo?" Regula has no published answer.
- **What:** Time `regula check` against 3–5 named public repos (chosen for size and language mix). Publish the table in README with Regula version, repo commit SHA, and machine specs.
- **Feasibility:** Low. `time` + a small script. Honest, reproducible, no fabrication risk.

### ~~Domain-based severity adjustment~~ — ALREADY IMPLEMENTED
- `scripts/domain_scoring.py` reads `system.domain` from `regula-policy.yaml` and applies confidence boosts in `report.py:440`. 5 tests in `test_classification.py`. Roadmap item was stale.

### ~~Document the existing MCP server~~ — DONE 2026-04-07 (README only)
- README now has an MCP Server section with Claude Code, Cursor, and Windsurf config snippets and a security note. Landing-page mention still TODO.

---

## Priority: Medium

### LGPD / Marco Legal da IA references in `regula conform`
- **Why:** `regula gap` already supports LGPD and Marco Legal da IA via `framework_mapper`, but the conformity evidence pack is EU-AI-Act-only. Brazilian users get half a tool.
- **What:** Extend `conform.py` so that when `--framework lgpd` or `--framework marco-legal-ia` is passed, the per-article evidence section includes the relevant LGPD / Marco Legal article cross-references already present in the framework mapper.
- **Feasibility:** Medium. Data exists; needs wiring into `conform` output and tests.

### External RFC 3161 timestamping for evidence packs
- **Why:** Regula's SHA-256 manifest is self-attesting — a local user could rewrite the evidence pack and the manifest. An external timestamp closes that loop.
- **What:** Verify that `scripts/timestamp.py` actually exists and works as the prior session claimed. If yes, integrate it as an opt-in step in `regula conform` (`--timestamp <tsa-url>`). If no, descope.
- **Feasibility:** Unknown until the existing module is verified. Treat as research-then-decide.

### Multi-EU-regulation pattern coverage (NIS2, GDPR-for-AI)
- **Why:** AI systems that process personal data have GDPR obligations on top of AI Act obligations, and AI systems that are part of essential services have NIS2 obligations. Regula's pattern set today is AI-Act-shaped.
- **What:** Add a focused pattern set for the GDPR-for-AI overlap (automated decision-making under Art. 22, DPIA triggers) and NIS2-relevant patterns where they intersect with AI systems. Wire through `framework_mapper`.
- **Feasibility:** Medium. New pattern research, but the architecture supports it.

### R language support
- **Why:** Statistical and academic AI work uses R heavily; ignoring it leaves a real audience uncovered.
- **What:** Add `.R` and `.r` to `CODE_EXTENSIONS`. Add R-specific patterns for the common ML libraries (`tidymodels`, `caret`, `mlr3`).
- **Feasibility:** Medium. Pattern research is the bulk of the work.

---

## Priority: Decide explicitly before building

These items have a values conflict with Regula's stated principles ("zero production dependencies", "offline operation", "CLI-first"). They should not be built until the trade-off is accepted explicitly.

### PR inline comments via GitHub Action
- **Trade-off:** Requires a published, maintained GitHub Action with a token model and marketplace listing. The *posting logic* is small; the *delivery vehicle* is the work.
- **Decision needed:** Are we shipping a GitHub Action as a first-class deliverable?

### Triage ticket export (`--export jira|github|linear`)
- **Trade-off:** Adds network calls and credential handling to a tool that brags about offline operation and zero deps.
- **Decision needed:** Is `regula plan` allowed to talk to external APIs, or should this stay as file output that the user pipes into their own tooling?

### Slack / Teams webhook notifications
- **Trade-off:** Same as above — network call from a CLI that runs in CI.
- **Decision needed:** Same as above.

### CE Marking declaration generator
- **Trade-off:** A Declaration of Conformity is a *legal document* with a prescribed format. Generating one from a static scan without legal review is a liability surface.
- **Decision needed:** Do we want Regula to produce legally-shaped documents, or stop at the evidence pack and let the user's lawyer assemble the declaration?

### Multi-jurisdiction frameworks (US states, APAC, Africa)
- **Trade-off:** Adding California SB 1047, Colorado AI Act, Korea AI Act, China AI regulations, Japan APPI, Singapore PDPA each requires legal sourcing per jurisdiction. This is a research project, not a coding project, and getting it wrong is worse than not having it.
- **Decision needed:** Are we partnering with legal counsel per region, or descoping until we have one?

### JS/TS AST analysis via tree-sitter
- **Trade-off:** `references/tree_sitter_implementation_guide.md` exists in the repo, suggesting prior thinking. tree-sitter grammars add complexity and a real (even if optional) dependency. Worth it only if the regex approach is genuinely producing false positives at scale.
- **Decision needed:** Measure regex precision/recall on JS/TS first. Only adopt tree-sitter if there's evidence the regex floor is too low.

---

## Blocked on prerequisites

### Publish precision / recall benchmarks
- **Status:** BLOCKED. The `regula benchmark` command exists, but there is no labelled ground-truth dataset to benchmark against. Building a credible labelled corpus is a multi-week effort and is the actual work.
- **Next step:** Treat dataset construction as its own project. Until a labelled corpus exists and is committed (or pointed to), do not publish a precision/recall number — fabricated accuracy claims would violate Regula's own honesty rules.

---

## Priority: Out of scope (different tool category)

Documented for awareness only. Not planned. Regula is a static-analysis CLI; these are different products.

- Runtime monitoring of deployed models
- Behavioural / red-team testing of model outputs
- Bias and fairness model testing (requires running models)
- PII redaction at runtime
- Content watermarking and deepfake labelling
- LLM-assisted classification (Regula is pure static analysis by design)
- SSO / RBAC / multi-user
- Executive dashboards
- Approval workflows
- Model lifecycle management
- Vendor AI risk management
- Web UI for non-CLI users

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
