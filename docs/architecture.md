# Architecture

Internal layout of the `scripts/` package, design principles, and language support.

## Architecture

```
regula/
├── .claude/skills/regula/SKILL.md  # Core skill file (Claude Code)
├── scripts/
│   ├── cli.py                     # Unified CLI entry point
│   ├── classify_risk.py           # Risk indication engine (confidence scoring)
│   ├── log_event.py               # Audit trail (hash-chained, file-locked)
│   ├── report.py                  # HTML + SARIF report generator
│   ├── install.py                 # Multi-platform hook installer
│   ├── feed.py                    # Governance news aggregator (7 sources)
│   ├── questionnaire.py           # Context-driven risk assessment
│   ├── session.py                 # Session-level risk aggregation
│   ├── baseline.py                # CI/CD baseline comparison
│   ├── timeline.py                # EU AI Act enforcement dates
│   ├── generate_documentation.py  # Annex IV + QMS scaffold generator
│   ├── discover_ai_systems.py     # AI system discovery, registry, compliance tracking
│   ├── credential_check.py        # Secret detection (18 patterns: 10 high + 8 medium confidence)
│   ├── ast_analysis.py            # AST-based Python analysis (data flow, oversight, logging)
│   ├── ast_engine.py              # Multi-language AST engine (Python + JS/TS tree-sitter + Java/Go/Rust/C/C++ regex)
│   ├── compliance_check.py        # Compliance gap assessment (Articles 9-15)
│   ├── dependency_scan.py         # AI dependency supply chain security
│   ├── framework_mapper.py        # Cross-framework compliance mapping (13 frameworks)
│   ├── remediation.py             # Inline fix suggestions per Annex III category
│   ├── agent_monitor.py           # Agentic AI governance (autonomy scoring, MCP config)
│   ├── sbom.py                    # CycloneDX 1.7 AI SBOM generation
│   ├── benchmark.py               # Real-world precision/recall validation
│   ├── aibom.py                   # AI Bill of Materials generator (CycloneDX 1.7)
│   ├── gdpr_patterns.py           # GDPR pattern definitions (14 patterns, 4 hotspots)
│   ├── gdpr_scan.py               # GDPR code pattern scanner
│   ├── roadmap.py                 # Compliance roadmap generator
│   ├── doc_audit.py               # Document quality scoring engine
│   ├── evidence_pack.py           # Self-verifying evidence bundle
│   ├── risk_decisions.py          # Annotation parser (regula-ignore / regula-accept)
│   ├── findings_view.py           # Finding view separation (active/suppressed/accepted)
│   ├── signing.py                 # Ed25519 manifest signing
│   ├── timestamp.py               # RFC 3161 timestamping
│   ├── adoption_pulse.py          # Passive PyPI + GitHub signal tracker
│   ├── monitor.py                 # Article 12 runtime monitoring SDK (MonitorSession, Trace)
│   └── cli_monitor.py             # CLI: regula monitor status|report|verify|prune|export
├── hooks/
│   ├── pre_tool_use.py            # PreToolUse hook (CC/Copilot/Windsurf)
│   ├── post_tool_use.py           # PostToolUse logging hook
│   └── stop_hook.py               # Session summary hook
├── references/                    # Regulatory reference documents
│   ├── owasp_llm_top10.yaml       # OWASP Top 10 for LLMs → EU AI Act mapping
│   └── mitre_atlas.yaml           # MITRE ATLAS → EU AI Act mapping
├── tests/                         # 127 test files, 3,096 tests (pytest --collect-only)
│   ├── test_classification.py     # Core classification tests (main test file)
│   └── ...                        # See tests/ for full list
├── docs/
│   └── course/                    # Interactive 10-module governance course
├── regula-policy.yaml             # Policy configuration template
└── .github/workflows/ci.yaml     # CI/CD
```

### Language Support

| Language | Analysis Depth | What It Detects |
|----------|---------------|-----------------|
| **Python** | Full AST | Data flow tracing, human oversight detection, logging practices, function/class extraction |
| **JavaScript/TypeScript** | Moderate (tree-sitter) | Import extraction, data flow tracing, oversight detection, logging. Tree-sitter optional — falls back to regex. |
| **Java** | Import detection (regex) | 13 AI libraries (Google AI Platform, LangChain4j, DJL, etc.) |
| **Go** | Import detection (regex) | 9 AI libraries (go-openai, langchaingo, etc.) |
| **Rust** | Import detection (regex) | 39 AI crates (candle, burn, tch, async-openai, etc.) + Cargo.toml parsing |
| **C/C++** | Include detection (regex) | 43 AI headers (LibTorch, TensorFlow, ONNX Runtime, llama.cpp, etc.) + CMake/vcpkg parsing |

**Honest note:** Only Python has deep AST analysis with data flow tracing. JS/TS with tree-sitter is moderate depth. Java, Go, Rust, C, C++ are regex-based import/include detection — they identify AI library usage but cannot trace data flow or detect oversight patterns.

### Design Principles

- **Core engine + thin adapters.** One classification engine, multiple platform integrations.
- **Same hook protocol.** Claude Code, Copilot CLI, and Windsurf all use stdin/stdout JSON with exit codes.
- **Detector priority, not binary labels.** 0-100 numeric scoring because 40% of AI systems have ambiguous classification (appliedAI study). The number counts how many code patterns matched; it is not a confidence and not a probability that the finding is correct.
- **Inline suppression with audit trail.** `# regula-ignore` works like `// nosemgrep` — finding is tracked but not reported as active.
- **SARIF for CI/CD.** Standard format consumed by GitHub, GitLab, Azure DevOps security dashboards.
- **Named governance contacts.** The policy file supports optional AI Officer and DPO fields. These fields do not represent an Article 4 requirement; AI-literacy measures and ISO/IEC 42001 role controls must be assessed separately.
- **Compliance workflow.** Tracked status progression with audit trail and transition history.
- **AST over regex where it matters.** Python `ast` module provides structure-aware analysis: real imports vs string mentions, data flow tracing, human oversight detection. Regex remains for cross-language pattern matching.
- **Compliance gap assessment, not just risk flagging.** Checks whether Articles 9-15 compliance infrastructure actually exists in the codebase.
- **AI-specific supply chain security.** Dependency pinning checks focus on AI libraries, not general packages.
- **Cross-platform.** Unix/macOS (`fcntl`) and Windows (`msvcrt`) file locking. No platform restrictions.
- **Multi-framework mapping.** 13 frameworks with full crosswalk data (EU AI Act, NIST AI RMF, ISO 42001, NIST CSF, SOC 2, ISO 27001, OWASP LLM Top 10, OWASP Top 10 for Agentic Applications, MITRE ATLAS, EU CRA, LGPD, Marco Legal IA, UK ICO) mapped via [references/framework_crosswalk.yaml](../references/framework_crosswalk.yaml). 5 additional frameworks have display handlers but no crosswalk data and no filter keys (Colorado SB-205, Canada AIDA, Singapore AI, OECD AI, South Korea AI) — filter keys removed in commit 7d93fed to prevent silent empty results.


## Site integrity guard

Region pages under `site/regions/` are generated from `content/regulations/*.py`
by `scripts/build_regulations.py`. Hand-editing the shipped HTML is what caused
the July 2026 Colorado drift — never do it; edit the source and rebuild.

`python3 scripts/site_integrity.py` enforces this:

- **regen** — re-renders every sourced page in memory and compares with the
  shipped file. Identical → OK; drift matching a reviewed fingerprint in
  `KNOWN_DRIFT` → WARN (ticketed); any other drift → FAIL.
- **sources** — every `site/regions/*.html` needs a content source or an
  explicit `EXEMPT_NO_SOURCE` entry.
- **links** — every internal href/src across `site/**/*.html` resolves.
- **claims** — `scripts/claim_auditor.py` over all site pages.

`--root DIR` runs against a copy (sandbox testing), `--fingerprint` prints
drift fingerprints when reviewing a known drift, `--check` selects subsets.
CI: `.github/workflows/site-integrity.yml` (inert until pushed).
