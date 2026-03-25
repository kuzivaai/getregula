# Regula Research Synthesis — March 2026

Research conducted across three domains: AI governance tooling state of the art,
multi-platform architecture, and non-developer UX. This document captures findings
that inform the product roadmap.

---

## Finding 1: Nobody Does Code-Level Risk Classification

Every major governance platform (Credo AI, Holistic AI, IBM watsonx.governance,
ModelOp) classifies risk at the **use-case/metadata level** via questionnaires,
taxonomy mapping, and LLM-assisted recommendation. None analyses source code.

- Credo AI: questionnaire + LLM-powered risk scenario recommendation
- Holistic AI: infrastructure scanning + rule-based classification
- IBM: structured assessments + quantitative model evaluation metrics
- ModelOp: metadata-driven classification at model registration time

**Implication:** Regula's code-level approach is a genuine market gap. But it must
be honest that code patterns indicate risk, they don't determine it.

**Source:** Forrester Wave AI Governance 2025; Gartner Market Guide 2025; vendor
documentation review.

---

## Finding 2: 40% of AI Systems Can't Be Clearly Classified

The appliedAI Institute study of 106 enterprise AI systems found:
- 18% classified as high-risk
- 42% classified as low-risk
- **40% could not be clearly classified** as high or low risk

Ambiguous cases concentrated in critical infrastructure, employment, law
enforcement, and product safety — exactly where clarity matters most.

**Implication:** Any classification tool must handle ambiguity gracefully. Binary
labels are wrong; confidence scores and "review recommended" states are essential.

**Source:** appliedAI Risk Classification Study; appliedAI Risk Classification
Database.

---

## Finding 3: The State of the Art Is Hybrid (AST + LLM)

Semgrep Multimodal (launched March 2026) combines rule-based AST analysis with
LLM reasoning:
- **8x more true positives** than LLM alone
- **50% less noise** than LLM alone
- Traditional rules catch known patterns; LLMs catch business logic flaws

IRIS (ICLR 2025) validated this academically: GPT-4 + static analysis found
55 vulnerabilities vs CodeQL's 27 on the same benchmark.

**Implication:** Regula's regex approach is v1.0. The upgrade path is:
1. AST-based analysis (understand imports, data flow)
2. LLM-assisted classification (understand intent from context)
3. Hybrid combining both

---

## Finding 4: False Positive Management Is Non-Negotiable

Developer security tools all implement the same pattern:
- **Inline suppression:** `// nosemgrep`, `// noqa` equivalents
- **Confidence scoring:** Snyk uses 1-1000; Semgrep uses rule confidence levels
- **AI-assisted triage:** Semgrep Assistant has 95% user agreement rate
- **Audit trail of suppressions:** Every suppression is logged with justification

No successful developer tool simply reports findings and expects acceptance.

**Implication:** Regula needs `# regula-ignore` inline suppression, numeric
confidence scores, and a triage workflow. Without this, developers disable the tool.

**Source:** Semgrep docs; Snyk Priority Score docs; SonarQube issue management docs.

---

## Finding 5: Three AI Coding Agents Use the Same Hook Protocol

Claude Code, GitHub Copilot CLI, and Windsurf Cascade have converged on:
- JSON on stdin with tool name + arguments
- Shell script execution
- JSON on stdout with allow/deny decision
- Exit code 2 = deny

**Implication:** Regula's existing hooks work on all three platforms with only
config file generation differing. Multi-platform support is nearly free.

**Source:** Claude Code hooks docs; GitHub Copilot CLI hooks docs (Feb 2026 GA);
Windsurf Cascade hooks docs.

---

## Finding 6: LSP Is the Universal IDE Integration Layer

An LSP server that publishes diagnostics works in VS Code, Cursor, JetBrains
(2023.1+), Neovim, Emacs, and Sublime Text. Ruff is the gold standard: single
binary exposes both CLI and LSP server.

**Implication:** A `regula lsp` command would give Regula native IDE integration
across all major editors. This serves developers who don't use AI coding agents.

---

## Finding 7: Static HTML Reports Bridge CLI to Non-Developers

Trivy (security scanner) generates single-file portable HTML reports that can be
shared without a server. This is the proven pattern for CLI tools serving
non-technical stakeholders.

The UX patterns that work for compliance officers:
- RAG (Red/Amber/Green) status indicators
- Rule of Three (top 3 risks, top 3 gaps, top 3 actions)
- PDF as the universal audit artefact
- Filtered views by date, risk level, or system

**Source:** Trivy reporting docs; GRC dashboard best practices; ISACA risk
visualisation research.

---

## Finding 8: DPOs Say the Tools They Need Don't Exist

IAPP AI Governance Profession Report 2025:
- Privacy professionals are being pulled into AI governance roles
- "Organisations finding products that meet their needs are simply not available"
- Common pattern: adding AI questions to existing DPIA processes
- 23.5% say finding qualified AI governance professionals is a challenge

DPOs actually ask for:
1. Risk assessment tools integrating with existing DPIA processes
2. Consistent bias detection capabilities
3. Standardised multi-framework documentation
4. Evidence generation that doesn't require data science expertise
5. Audit-ready artefacts they can produce without developer assistance

**Source:** IAPP/Credo AI AI Governance Global Report 2025.

---

## Finding 9: EU AI Act Deadlines Are Shifting

- High-risk deadlines proposed to move to **December 2027** (from August 2026)
- Harmonised standards pushed to end of 2026 (after enforcement)
- No notified bodies ready for conformity assessment
- No governance tools are "certified" — no certification scheme exists

**Implication:** The urgency window is longer than originally assumed. There's
time to build properly rather than ship fast. But preparation demand is still
real — organisations need to start now even if deadlines shift.

**Source:** EU Parliament committees joint report (March 2026); Council position
(March 2026); IAPP coverage.

---

## Finding 10: SARIF Is the CI/CD Standard

SARIF (Static Analysis Results Interchange Format) is consumed by GitHub,
GitLab, and Azure DevOps for security scan results. Snyk, Semgrep, Trivy,
and CodeQL all output SARIF.

**Implication:** `regula check --format sarif` would integrate with every
major CI/CD platform's security dashboard natively.

---

## Architecture Recommendation

```
                    +---------------------------+
                    |      Core Engine           |
                    |  (classify, audit, policy) |
                    +---------------------------+
                           |
              +------------+------------+
              |            |            |
         CLI Interface  LSP Server  Hook Adapters
         regula check   regula lsp  (stdin/stdout JSON)
              |            |            |
     +--------+---+    +---+---+   +---+---+---+
     |   |   |    |    |   |   |   |   |   |   |
    git  CI  pre  HTML VS  JB Cur CC  CP  WS  Future
    hook     commit rpt Code         CLI
```

### Phase 1 (v1.1): Multi-platform + developer experience
- CLI wrapper (`regula check`, `regula classify`, `regula report`)
- Multi-platform hook adapters (Copilot CLI, Windsurf — config generators)
- Inline suppression (`# regula-ignore: RULE_ID`)
- Confidence scoring (numeric, not just high/medium)
- SARIF output for CI/CD
- pre-commit hook integration
- HTML report generator (Trivy model)

### Phase 2 (v1.2): Non-developer access + smarter classification
- LSP server for IDE-native diagnostics
- Questionnaire mode for ambiguous classifications
- PDF export from HTML reports
- DPO dashboard (static HTML with filtering)
- External timestamp authority option for audit chain

### Phase 3 (v2.0): Hybrid intelligence
- AST-based analysis (tree-sitter for Python/JS)
- LLM-assisted classification for context understanding
- Multi-framework support (ISO 42001, NIST AI RMF)
- Bias detection integration
