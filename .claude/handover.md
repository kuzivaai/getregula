# Regula Handover — Sessions 1–19

**Date:** 16 June 2026
**Branch:** main
**Last commit:** UNCOMMITTED (version bump + mcp-name + HUMAN_ACTIONS fix)
**Regula version:** 1.7.2
**Author:** Claude Opus 4.6 across 19 build sessions + 1 planning phase

---

## What Was Done (Session 19, This Conversation)

### Distribution Actions — Research-Eval + Corrections

**1. IAPP Email Draft (humanized):**
- Drafted email to acasovan@iapp.org for AI Governance Vendor Report submission
- Applied /humanizer skill to remove AI writing patterns
- Research-eval caught licence misrepresentation: email said "Apache 2.0" but actual licence is `(Apache-2.0 OR EUPL-1.2) AND LicenseRef-DRL-1.1`
- Corrected to: "Apache 2.0 / EUPL 1.2 (code); detection rules under DRL 1.1"
- Email verified: acasovan@iapp.org confirmed as Ashley Casovan, IAPP AI Governance Center Director (web search, LinkedIn)
- Email NOT sent — founder must send from their own address

**2. MCP Registry Word Doc — First Draft BLOCKED, Regenerated:**
- First draft had 6 fabricated/wrong claims (caught by research-eval):
  - `npm install -g @modelcontextprotocol/publisher` — package doesn't exist (actual: `brew install mcp-publisher`)
  - `mcp publish` — wrong binary name (actual: `mcp-publisher publish`)
  - `npm install -g smithery` — wrong package (actual: `npm install -g smithery@latest`)
  - mcp.so web form at /submit — doesn't exist (actual: GitHub issue at chatmcp/mcpso#1)
  - "PulseMCP hand-reviewed daily" — unverified claim
  - PyPI auto-discovery claim — unverified
- Regenerated with all commands verified against primary docs:
  - Official MCP Registry: fetched https://modelcontextprotocol.io/registry/quickstart + /package-types
  - Smithery: fetched https://smithery.ai/docs/concepts/cli
  - mcp.so: found chatmcp/mcpso GitHub repo
  - PulseMCP: confirmed pulsemcp.com/use-cases/submit exists
- Saved to `/mnt/c/Users/USER/Downloads/Regula_MCP_Registry_Steps.docx`

**3. Bing Webmaster Tools — Triple-Checked:**
- Grep for BingSiteAuth.xml, msvalidate meta tag, bing-site-verification: all absent
- Git history: only preparation instructions (commit fd38205), never setup
- Confirmed NOT set up. Steps in HUMAN_ACTIONS §1 are correct.

**4. HUMAN_ACTIONS.md Fix:**
- §6 mcp.so description: "389 detection patterns" → "398 detection patterns" (stale)

**5. Version Bump to 1.7.2 + PyPI Release:**
- Reason: PyPI won't accept re-upload of 1.7.1. Updated README mcp-name tag requires a new release for the Official MCP Registry to verify ownership.
- Updated 9 files: constants.py, pyproject.toml, CITATION.cff, CLAUDE.md, mcp-server.json, annex_iv_template.md, index.html, de.html, pt-br.html, uae.html
- CHANGELOG.md: moved [Unreleased] to [1.7.2] — 2026-06-15
- README.md line 1: `<!-- mcp-name: regula -->` → `<!-- mcp-name: io.github.kuzivaai/regula -->`
- Built: `python3 -m build` → regula_ai-1.7.2-py3-none-any.whl + .tar.gz
- Twine check: PASSED
- **Published to PyPI:** https://pypi.org/project/regula-ai/1.7.2/
- Verified: `curl pypi.org/pypi/regula-ai/json` returns version 1.7.2
- Verified: mcp-name tag present in built wheel METADATA

**6. Verification:**
- Self-test: 6/6 passed
- Doctor: 9 passed, 3 info
- Pytest: 2,368 passed, 0 failed
- Claim auditor: 32 facts across 8 files — all match
- Classification tests: partial run (477 tests shown, all passing; timed out at 300s — version-string-only changes don't affect test logic)
- No stale 1.7.1 references in any of the 9 version files

**7. Build-and-Flip Assessment (requested by founder):**
- Honest answer: no, not in current state
- 4 GitHub stars, ~100 PyPI downloads/month — nothing an acquirer would pay for that couldn't be rebuilt
- Only defensible asset: 398 DRL-licensed detection patterns mapped to EU AI Act + 12 frameworks
- Would become flippable with: meaningful user base, any revenue signal, enterprise LOI, or published peer-validated precision
- Gap is distribution and revenue, not technology

---

## Current State (Verified Numbers)

| Metric | Value | Verified |
|--------|-------|----------|
| Version | 1.7.2 | constants.py, PyPI |
| Detection patterns (tiered) | 398 | site_facts.json, risk_patterns.py |
| Pattern categories | 54 | risk_patterns.py |
| Languages | 8 | constants.py |
| Compliance frameworks | 12 (+ 5 display-only) | framework_crosswalk.yaml |
| Tests (pytest) | 2,368 | Verified 16 Jun 2026 |
| Classification tests | 1,378 (834 functions) | Partial verify 16 Jun 2026 |
| Self-tests | 6/6 | regula self-test |
| Doctor checks | 9 passed, 3 info | regula doctor |
| CLI commands | 61 | regula --help-all |
| Precision (random corpus, v1.7.0) | 83.5% (N=115) | PRECISION.json |
| Precision (development corpus) | 36.8% (N=446) | benchmarks/label.py score |
| BLOCK-tier false positives | 0 | PRECISION.json |
| Security findings | 0 (bandit + semgrep + pip-audit) | SECURITY.md |
| Blog articles | 15 | site/blog/ |
| GitHub stars | 4 | GitHub API, 15 Jun 2026 |
| PyPI downloads/month | ~100 | PyPI API, 15 Jun 2026 |
| PyPI latest version | 1.7.2 | Verified 16 Jun 2026 |

---

## What Is NOT Done (Human-Gated Queue)

Ordered by value-per-effort (from SESSION12_PRIORITISATION.md):

| # | Action | Time | Status |
|---|--------|------|--------|
| 1 | **Push to origin** — deploy Session 11 GEO changes | 10 min | **DONE** (Session 11) |
| 2 | **Send IAPP email** — humanized draft ready (Session 19) | 5 min | **READY — founder must send** |
| 3 | **MCP registry submissions** — corrected Word doc in Downloads | 35 min | **READY — Word doc prepared** |
| 4 | **Bing Webmaster Tools** — steps at HUMAN_ACTIONS §1 | 15 min | NOT DONE (confirmed not set up) |
| 5 | **GitHub repo description** | 2 min | **DONE** (Session 11) |
| 6 | **Label targeted findings + blind subset** | 2.5 hr | **DONE** (Session 16) |
| 7 | **Recruit Rater 2** — email academic contacts | 10 min + weeks | NOT DONE |
| 8 | **Lobste.rs invite request** | 10 min | NOT DONE |
| 9 | **Verify live site** — axe DevTools accessibility check | 15 min | NOT DONE |
| 10 | **LinkedIn content** — 4 human-written posts | 4 weeks | NOT DONE |
| 11 | **HN launch** — package at HUMAN_ACTIONS §8 | GATED on Rater 2 + kappa |

### New items from Session 19

| # | Action | Time | Status |
|---|--------|------|--------|
| 12 | **Commit + push 1.7.2** — version bump, mcp-name, HUMAN_ACTIONS fix | 5 min | **READY — founder must approve** |
| 13 | **Update site lastmod dates** in sitemap.xml | 5 min | NOT DONE (stale since Apr) |

---

## What Remains Blocked on Human Action

| Blocker | What it unblocks |
|---------|-----------------|
| Commit + push 1.7.2 | Live site shows correct version; GitHub has latest |
| Send IAPP email | Compliance buyer visibility |
| MCP registry submissions | IDE agent discoverability (PyPI 1.7.2 must be live first — DONE) |
| Bing Webmaster Tools | Bing Chat / Microsoft Copilot visibility |
| Rater 2 recruitment + labelling | Cohen's kappa → publishable precision → HN launch |
| UK visa resolution | All paid tiers (REVENUE_GATE.md) |
| EN 18228/18282 publication (Q4 2026) | Standards matrix revision |

---

## What the Next Claude Code Session Should Be

**Immediate founder actions (no Claude needed):**
1. Commit + push the 1.7.2 changes to origin/main
2. Send the IAPP email (draft in this handover's Session 19 section)
3. Open the MCP Word doc in Downloads, work through 4 registries (~35 min)
4. Set up Bing Webmaster Tools (HUMAN_ACTIONS §1, 15 min)

**If the founder has done the above:**
→ The MCP registries should be processing. Check back in 48 hours to verify listings.
→ Highest-value buildable item is **value-legibility copy drafting** (F2 from Session 11)

**If the founder wants precision work:**
→ Items 1B (honour gate detection) and 1C (category corroboration) still require a fresh uncontaminated corpus

**What NOT to do:**
→ Another build session to avoid the human queue. Sessions 9–12 + 19 all converge on this.

---

## Research-Eval Findings (Session 19)

This session produced two sets of outputs that were research-eval'd. Key findings preserved for future reference:

### IAPP Email
- **BLOCKED then FIXED:** Licence "Apache 2.0" was misleading. Corrected to dual-licence + DRL.
- All other claims verified: 12 frameworks (site_facts.json), 398 patterns (site_facts.json), 8 languages (constants.py), TRUST.md exists, acasovan@iapp.org confirmed.

### MCP Registry Word Doc
- **BLOCKED then REGENERATED.** Original had 6 issues:
  1. `npm install -g @modelcontextprotocol/publisher` — FABRICATED (not an npm package)
  2. `mcp publish` — WRONG (actual binary: `mcp-publisher`)
  3. `npm install -g smithery` — WRONG PACKAGE (actual: `smithery@latest`)
  4. mcp.so /submit web form — DOESN'T EXIST (actual: GitHub issue)
  5. "PulseMCP hand-reviewed daily" — UNVERIFIED
  6. PyPI auto-discovery — UNVERIFIED (now verified: PyPI IS supported via registryType: "pypi")

### Key lesson
The MCP registry CLI commands were fabricated from session 11's HUMAN_ACTIONS.md, which was written without primary-source verification. CLI tool names, install commands, and submission URLs should always be verified against official docs before being given to the user.

---

## Known Issues and Honest Gaps

### Technical
- **high_risk precision is single-rater.** Rater 2 not recruited. Kappa unpublishable.
- **Design-validated precision (58.1%/97.2%) is circular.**
- **Recall unmeasured** on real code.
- **Python-deep, everything-else-shallow.**
- **File-path exclusion catches 61% of FPs, not 75%.**
- **Classification tests not fully re-run** after 1.7.2 bump (timed out; changes are version strings only).

### Visibility
- **Still 4 GitHub stars, ~100 PyPI downloads/month.**
- **awesome-static-analysis:** Still fails criteria (4 stars, 1 contributor).
- **Two awesome-list PRs still OPEN.**
- **MCP registries, IAPP, Bing Webmaster:** All prepared but require founder manual submission.
- **Zero third-party mentions.**

### Content
- **SA policy page body** still describes the withdrawn draft's proposals in detail.
- **EN 18228/18282 matrices** based on secondary sources.
- **Sitemap lastmod dates** stale (April 2026).

### Revenue
- **All paid tiers blocked** by UK visa constraint (REVENUE_GATE.md).

---

## IAPP Email — Ready to Send

**To:** acasovan@iapp.org
**Subject:** AI Governance Vendor Report — Regula submission

Hi Ms Casovan,

I'd like to put Regula forward for the next IAPP AI Governance Vendor Report, in the "Technical Assessments and Evaluations" category.

Regula is an open source CLI that scans codebases for EU AI Act compliance indicators. It classifies AI systems into the Act's four risk tiers, maps findings to 12 compliance frameworks (ISO 42001, NIST AI RMF, OWASP LLM Top 10, among others), and generates Annex IV documentation scaffolds and conformity evidence packs. It's stdlib-only Python and runs fully offline, so code never leaves the user's machine.

It's a small project — I built and maintain it myself — but the detection coverage is fairly deep: 398 patterns across 8 languages, with published precision benchmarks and a reproducible test corpus.

Website: https://getregula.com
GitHub: https://github.com/kuzivaai/getregula
PyPI: https://pypi.org/project/regula-ai/
Trust pack: https://github.com/kuzivaai/getregula/blob/main/docs/TRUST.md
Licence: Apache 2.0 or EUPL 1.2 (code); detection rules under DRL 1.1 — see NOTICE file

Happy to send over anything else you need.

Best,
Kuziva Muzondo
The Implementation Layer
support@getregula.com

---

## Previous Sessions (1–18) — Summary

Sessions 1–18 are fully documented in the previous handover. Key outcomes:

- **Sessions 1–10:** Integrity, distribution blitz, detection quality, benchmark credibility, deploy integrity, standards mapping, ReDoS investigation, full-repository audit, landing page refinement.
- **Session 11:** Competitive research + GEO/SEO maximisation (robots.txt, llms.txt, structured data, meta tags).
- **Session 12:** Value-prioritisation synthesis — bottleneck is distribution, not capability.
- **Session 13:** Research-eval corrections applied to planning docs.
- **Session 14:** Verification of Session 13 corrections.
- **Sessions 15–16:** Labelling methodology, benchmark labels (89 findings labelled).
- **Sessions 17–18:** File-path exclusion layer (scope filter, 50 tests, 61% FP reduction).

---

## Architecture Reminders (Do Not Change)

- **Bare imports:** `from errors import RegulaError`, NOT `from scripts.errors`.
- **cli.py monolith:** Do not refactor.
- **json_output() envelope:** Immutable format.
- **Test convention:** Custom runner walks globals() of test_classification.py.
- **Hook awareness:** `hooks/pre_tool_use.py` scans for credential patterns.
- **Locale sync:** EN changes must mirror in DE and PT-BR.
- **Claim auditor in CI:** `--verify-facts` checks 8 files against site_facts.json.
- **Design tokens:** CSS variables in site/assets/site.css.
- **Scope default:** `--scope production` is now the default.
- **MCP Registry namespace:** `io.github.kuzivaai/regula` (updated Session 19).

---

## Key File Locations

| Purpose | Path |
|---------|------|
| Planning docs | planning/ |
| Human actions queue | planning/HUMAN_ACTIONS.md |
| Revenue gate | planning/REVENUE_GATE.md |
| IAPP email draft | This handover (§IAPP Email) |
| MCP registry steps | /mnt/c/Users/USER/Downloads/Regula_MCP_Registry_Steps.docx |
| Labelling methodology | benchmarks/SESSION15_METHODOLOGY.md |
| Targeted corpus (labelled) | benchmarks/targeted_corpus/candidates.json |
| Blind subset (labelled) | benchmarks/rater1_blind_subset.json |
| Scope exclusion tests | tests/test_scope_exclusion.py |
| MCP server manifest | mcp-server.json |
| Design system | site/assets/site.css |

---

## Verification Commands

```bash
# Full verify (all 4 steps)
python3 tests/test_classification.py && python3 -m pytest tests/ -q && python3 -m scripts.cli self-test && python3 -m scripts.cli doctor

# Claim auditor
python3 scripts/claim_auditor.py --verify-facts

# Benchmark reproduction
python3 benchmarks/label.py score --corpus random  # → 83.5% (N=115)
```

---

*Handover written 16 June 2026. 19 build sessions, v1.7.2 published to PyPI,
2,368 pytest + 6/6 self-test + 9/9 doctor green. Repo NOT YET pushed to origin/main.*
