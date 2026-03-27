# Regula Competitive Gap Analysis

**Date:** 2026-03-27
**Methodology:** Code review of competitor repos, web search of docs/blogs, analysis of Regula source

---

## Gap 1: Systima Comply's Deeper AST (Cross-Assignment Call-Chain Tracing)

### What the Competitor Actually Has

Systima Comply (`npx @systima/comply`, GitHub Action `systima-ai/comply@v1`) is a TypeScript-based scanner that:

- Uses the **TypeScript Compiler API** for TypeScript/JavaScript and **web-tree-sitter WASM** for other languages
- Detects 37+ AI/ML frameworks via AST-based import detection
- **Traces AI return values through assignments and destructuring** to identify four specific patterns:
  1. Conditional branching on AI output (automated decisions)
  2. Persistence of AI output to a database
  3. Rendering AI output in a UI without disclosure
  4. Sending AI output to downstream APIs
- Checks obligations against EU AI Act Articles 5-50
- Scanned Vercel's 20k-star AI chatbot in ~8 seconds

**Key unknown:** Whether their call-chain tracing crosses file boundaries or stays within single files. Their blog post says "traces how AI outputs flow through the program" but doesn't specify cross-file resolution. The call-chain tracing approach is described as still evolving (they "welcome feedback").

**Source code status:** Not clearly open-source. Published as npm package (`@systima/comply`) and GitHub Action, but the source repository was not found on GitHub during this research. The DEV.to article and blog describe features but don't link to source.

### What Regula Already Has

Regula's `ast_analysis.py` already implements **single-file data flow tracing** for Python using stdlib `ast`:
- `_AICallCollector` identifies AI operations (predict, invoke, create, etc.)
- `_FlowTracer` traces where AI results flow: variables, returns, logging, human review, automated actions, API responses, display, persistence
- Oversight scoring based on whether AI outputs pass through human review before automated actions
- Logging proximity detection (whether AI operations have logging within 5 lines)

For JS/TS, `ast_engine.py` uses **regex-based fallback** (tree-sitter noted as "not yet implemented").

### What Regula Would Need to Build

1. **Complete the tree-sitter JS/TS integration** (currently a placeholder at line 117 of `ast_engine.py`): Parse JS/TS using tree-sitter instead of regex to get proper AST nodes. This enables the same flow-tracing approach used for Python.
2. **Port `_FlowTracer` logic to work with tree-sitter nodes** for JS/TS: Track assignments, returns, and downstream calls from AI operation results.
3. **Cross-file resolution** (if Systima actually does this): Build an import graph resolver that follows `import`/`require` statements to trace AI data across module boundaries. This is significantly harder than single-file analysis.

### Effort Estimate

- Tree-sitter JS/TS integration with flow tracing: **3-5 days** (the Python flow tracer is a solid template)
- Cross-file import graph resolution: **5-8 days** additional (requires resolving relative imports, package.json main fields, TypeScript path aliases)
- Total for parity with Systima's described features: **~1-2 weeks**

### Is It Worth Building?

**Yes, partially.** The tree-sitter JS/TS integration is high value because many AI applications are Node.js-based. Cross-file tracing is lower priority -- single-file tracing already catches the most important patterns (AI output -> automated action without human review), and most AI call + decision logic lives in the same file.

### Priority: **Important** (tree-sitter JS/TS) / **Nice-to-have** (cross-file)

---

## Gap 2: ArkForge's Broader Language Support (8 Languages)

### What the Competitor Actually Has

ArkForge's `mcp-eu-ai-act` (GitHub: `ark-forge/mcp-eu-ai-act`) scans 8 languages:
- Python (.py), JavaScript (.js), TypeScript (.ts), Java (.java), Go (.go), Rust (.rs), C++ (.cpp), C (.c)
- Plus dependency/config files: requirements.txt, package.json, pyproject.toml, setup.py, Pipfile, pom.xml, Cargo.toml, go.mod

**Detection mechanism: Regex pattern matching, not AST.** Two pattern dictionaries:
1. `AI_MODEL_PATTERNS` -- searches source code for framework usage strings
2. `CONFIG_DEPENDENCY_PATTERNS` -- matches dependency declarations in manifests

**Analysis depth: Shallow.** From their docs: "Static analysis only -- detects imports and patterns, not runtime behavior." They detect *which* AI frameworks are present but don't evaluate how they're used. No data flow tracing, no oversight detection, no logging analysis.

**One notable feature:** Optional `follow_imports=True` builds a forward dependency graph from Python AST to identify transitively-imported AI frameworks. This is import-graph-only, not data flow.

**Framework coverage:** 16 AI frameworks (OpenAI, Anthropic, Google Gemini, Mistral, Cohere, HuggingFace, TensorFlow, PyTorch, LangChain, Vertex AI, AWS Bedrock, Azure OpenAI, Ollama, LlamaIndex, Replicate, Groq).

### What Regula Already Has

- Python: Full AST analysis with data flow tracing, oversight detection, logging analysis
- JavaScript/TypeScript: Regex-based import detection (similar depth to ArkForge for these languages)
- AI library registry in `dependency_scan.py`: 60+ libraries (significantly more than ArkForge's 16)

### What Regula Would Need to Build

To match ArkForge's 8-language breadth with **regex-only import detection** for Java, Go, Rust, C, C++:

1. Add file extension mappings for `.java`, `.go`, `.rs`, `.cpp`, `.c`
2. Add regex patterns for AI imports in each language:
   - **Java:** `import com.google.cloud.aiplatform.*`, `import dev.langchain4j.*`, `import ai.djl.*`
   - **Go:** `import "github.com/sashabaranov/go-openai"`, `import "github.com/tmc/langchaingo"`
   - **Rust:** `use llm::*`, `use candle_core::*`, `use rust-bert::*`
   - **C/C++:** `#include "tensorflow/c/c_api.h"`, `#include <onnxruntime_c_api.h>`
3. Add config file parsers: `pom.xml` (Java), `go.mod` (Go), `Cargo.toml` (Rust)

### Effort Estimate

- Regex import detection for 5 additional languages: **1-2 days** (it's just pattern dictionaries)
- Config file parsers (pom.xml, go.mod, Cargo.toml): **1 day**
- Total: **2-3 days**

### Is It Worth Building?

**Partially.** Java and Go are worth adding because enterprise AI systems use them (especially Java with Spring AI / LangChain4j, and Go with LangChainGo). Rust, C, and C++ are edge cases for AI application code (they're used for model inference runtimes, not application logic that the EU AI Act targets). Adding regex-only detection for Java and Go gives "8 languages supported" marketing parity while Regula's Python analysis remains deeper than anything ArkForge offers.

**Important context:** ArkForge's breadth is a marketing advantage, not a technical one. Their analysis for all 8 languages is shallower than Regula's Python-only analysis. Regula should match the breadth *for import detection* while keeping its depth advantage for Python and JS/TS.

### Priority: **Important** (Java + Go) / **Nice-to-have** (Rust, C, C++)

---

## Gap 3: Checkmarx Enterprise Distribution

### What the Competitor Has

Checkmarx is an enterprise application security company with:
- Established sales team, channel partners, and enterprise contracts
- Integration into existing SAST/DAST/SCA workflows that enterprises already pay for
- SOC 2 compliance, enterprise SSO, audit trails, SLAs
- AI security scanning as an add-on to existing platform customers already use

### What Regula Would Need

This is a business gap, not a code problem. Requires:
- Funding for sales team and enterprise go-to-market
- SOC 2 Type II certification (~$50-100k and 6-12 months)
- Enterprise features: SSO, RBAC, audit logs, API, SLAs
- Customer success / support team

### Effort Estimate

Not applicable as a solo developer task. Requires funding and team.

### Is It Worth Building?

**Not as a direct competitor.** Regula's path is either: (a) get acquired by an enterprise security vendor who wants EU AI Act capabilities, or (b) build a developer-focused tool that complements enterprise platforms rather than competing with them.

### Priority: **Skip** (business problem, not code problem)

---

## Gap 4: Agent-BOM's Multi-Framework Compliance Mapping

### What the Competitor Actually Has

Agent-BOM (`msaad00/agent-bom`) maps findings to **11 frameworks** (not 14 as initially reported):

1. OWASP LLM Top 10 (7/10 categories)
2. OWASP MCP Top 10 (10/10 categories)
3. OWASP Agentic Top 10 (10/10 categories)
4. MITRE ATLAS (30+ techniques)
5. NIST AI RMF 1.0 (all subcategories)
6. NIST CSF 2.0 (all functions)
7. CIS Controls v8 (12 controls)
8. ISO 27001:2022 (9 controls)
9. SOC 2 TSC (all 5 criteria)
10. EU AI Act (6 articles)
11. CMMC 2.0 Level 2 (17 practices)

**Mapping depth: Tag-based, not full crosswalks.** "Every finding is tagged with applicable controls across 11 security frameworks." This is categorical tagging (a finding gets tagged "NIST CSF 2.0 > PROTECT") rather than detailed article-to-control crosswalk documentation. Policy-as-code enforcement is available via YAML/JSON expressions.

**Important context:** Agent-BOM is a **supply chain security scanner** (CVE scanning, SBOM generation, blast radius analysis for MCP servers). It is not a code analysis tool. The framework mapping applies to *security findings*, not compliance posture assessment. This is a different product category from Regula.

### What Regula Already Has

Regula's `framework_mapper.py` maps EU AI Act Articles 9-15 to:
- NIST AI RMF 1.0 (specific subcategories per article)
- ISO/IEC 42001:2023 (specific controls per article)

This is a **deeper crosswalk** than Agent-BOM's tagging for the frameworks it covers -- Regula maps specific EU AI Act articles to specific NIST subcategories and ISO controls with descriptions.

### What Regula Would Need to Build

To expand framework coverage while maintaining crosswalk depth:

**High-value additions (relevant to AI compliance):**
1. **OWASP AI Security Top 10** -- map findings to OWASP AI categories (new in 2025)
2. **MITRE ATLAS** -- map AI-specific attack techniques to Regula's findings
3. **NIST CSF 2.0** -- broader cybersecurity framework, many enterprises require it
4. **SOC 2 TSC** -- enterprises need this for vendor assessments

**Lower-value additions (not AI-specific):**
5. ISO 27001:2022 -- general infosec, not AI-specific
6. CIS Controls v8 -- operational security controls
7. CMMC 2.0 -- US defence contractor specific

Each framework addition requires:
- Research the framework's control structure
- Map relevant controls to EU AI Act articles 9-15
- Add to `references/framework_crosswalk.yaml`
- Update `framework_mapper.py` to support new framework keys

### Effort Estimate

- Per framework (proper crosswalk): **0.5-1 day** research + mapping
- 4 high-value frameworks: **2-4 days**
- All 8 additional frameworks: **4-8 days**

### Is It Worth Building?

**Yes, selectively.** Adding OWASP AI Top 10 and MITRE ATLAS is high value because they're AI-specific. NIST CSF 2.0 and SOC 2 are high value because enterprises ask for them. The rest are nice-to-have for marketing ("maps to 7 frameworks" sounds better than 3).

**Key advantage to maintain:** Regula's crosswalk depth (article-to-control with descriptions) is more useful than Agent-BOM's tag-based approach. Don't sacrifice depth for breadth.

### Priority: **Important** (OWASP AI, MITRE ATLAS, NIST CSF 2.0) / **Nice-to-have** (others)

---

## Gap 5: pip-audit/osv-scanner Vulnerability Database (50,000+ Entries)

### What the Competitors Have

- **pip-audit** / **osv-scanner**: Query the OSV database (500,000+ vulnerabilities across all ecosystems)
- **General CVE/NVD**: Millions of entries, general software vulnerabilities
- These are general-purpose vulnerability scanners, not AI-specific

### What Regula Already Has

- Curated AI-specific advisory checking (`dependency_scan.py` > `check_compromised()`)
- Currently 1 advisory (LiteLLM supply chain attack, March 2026)
- AI dependency pinning quality scoring (weighted 3x for AI libraries)
- Lockfile presence detection

### The Right Approach (Confirmed)

Regula should **NOT** replicate a general vulnerability database. This is confirmed:

1. **AI-specific vulnerability databases do exist** -- AVID (AI Vulnerability Database, `avidml.org`) is a dedicated database for AI failure modes, maintained by the AI Risk and Vulnerability Alliance (ARVA, a 501(c)(3) nonprofit). It catalogues both reports (concrete incidents) and vulnerabilities (recurring failure modes), mapped to MITRE ATLAS and CVSS scores.

2. **The CVE system is catching up** -- The CVE AI Working Group (CVEAI WG) is working to better capture AI-related vulnerabilities. NIST AI 100-2e2025 provides a taxonomy for adversarial ML attacks. But coverage is still incomplete for AI-specific failures (prompt injection, model poisoning, training data extraction, etc.).

3. **Regula's value is different:** General CVE scanning (pip-audit, osv-scanner) finds known vulnerabilities in packages. Regula finds **AI-specific compliance risks** -- unpinned AI dependencies, missing human oversight, unlogged AI operations, missing documentation. These are complementary, not competing.

### What Regula Should Build

1. **Recommend pip-audit/osv-scanner as complementary tools** in scan output and documentation
2. **Integrate with AVID** -- pull AI-specific vulnerability data from avidml.org to supplement the curated advisory list. This gives Regula AI-specific vulnerability awareness without trying to replicate OSV.
3. **Continue curating AI-specific supply chain advisories** (like the LiteLLM one) for cases where general databases are slow to flag AI-specific risks
4. **Add AVID/MITRE ATLAS mapping** to findings for AI-specific threat intelligence

### Effort Estimate

- Add recommendation text for pip-audit/osv-scanner: **2 hours**
- AVID integration (fetch and check against AVID database): **2-3 days**
- Continue curating advisories: **Ongoing, ~1 hour per advisory**

### Is It Worth Building?

**Yes for AVID integration, no for general CVE replication.** AVID integration gives Regula a unique angle -- AI-specific vulnerability intelligence that pip-audit doesn't have. General CVE scanning is a solved problem; don't reinvent it.

### Priority: **Important** (AVID integration, complementary tool recommendations) / **Skip** (general CVE database)

---

## Gap 6: Enterprise Analyst Recognition (Gartner, Forrester)

### What Enterprise Competitors Have

- Gartner Market Guide for AI Governance Platforms (published November 2025): Includes vendors like Credo AI, which scored 5/5 on 12 criteria
- Forrester Wave AI Governance Solutions Q3 2025: Evaluated vendors across 30 criteria including AI policy management, regulatory compliance audit, quality and testing workflows
- These vendors have funding, paying customers, revenue, dedicated teams

### What It Takes to Get Included

**Gartner Market Guide:**
- Typically requires: identifiable paying customers, measurable revenue, product maturity beyond MVP
- Not a ranking -- it's a market overview listing "Representative Vendors"
- Inclusion criteria not publicly documented but observed pattern: 10+ paying customers, $1M+ ARR, or significant market presence

**Forrester Wave:**
- Invitation-based: Forrester selects vendors based on market presence
- Requires: customer references, detailed questionnaire responses, product demos
- Typically 12-15 vendors evaluated per Wave
- Minimum threshold: usually established enterprise vendor with paying customers

**Realistic timeline for a solo developer:** Never, unless:
- Regula gets funding (seed/Series A) and builds a team
- Regula gets acquired by an enterprise vendor already in these reports
- Regula pivots to open-core model with an enterprise tier generating revenue

### What Regula Should Do Instead

1. **Target developer community recognition first:** GitHub stars, ProductHunt launch, Dev.to articles, conference talks
2. **Get listed in curated compilations:** `awesome-compliance` lists on GitHub (already appears in some), OECD AI Policy Observatory tools catalogue
3. **Build credibility through technical depth:** Published benchmarks, comparison pages, integration guides
4. **Position for acquisition:** If an enterprise vendor (Checkmarx, Snyk, Veracode) wants EU AI Act capabilities, Regula's technical depth makes it an attractive acquisition target

### Effort Estimate

Not a code problem. Requires business development, funding, and time.

### Is It Worth Pursuing?

**Not directly.** Focus on making the best open-source tool. Analyst recognition follows product-market fit and revenue, not the other way around.

### Priority: **Skip** (business milestone, not a development task)

---

## Summary Table

| Gap | Competitor | What They Actually Have | Effort to Close | Worth It? | Priority |
|-----|-----------|------------------------|-----------------|-----------|----------|
| 1. AST depth | Systima Comply | TS Compiler API + tree-sitter, 4-pattern call-chain tracing | 1-2 weeks | Yes (tree-sitter JS/TS) | Important |
| 2. Language breadth | ArkForge | 8 languages, regex import detection only | 2-3 days | Yes (Java + Go) | Important |
| 3. Enterprise distribution | Checkmarx | Sales team, enterprise contracts, SOC 2 | N/A (funding) | No (business gap) | Skip |
| 4. Framework mapping | Agent-BOM | 11 frameworks, tag-based (not deep crosswalk) | 2-4 days for top 4 | Yes (selectively) | Important |
| 5. Vulnerability DB | pip-audit/osv-scanner | 500k+ general CVEs | 2-3 days (AVID) | Yes (AVID, not CVE) | Important |
| 6. Analyst recognition | Enterprise vendors | Gartner/Forrester inclusion | N/A (business) | No (premature) | Skip |

## Recommended Development Sequence

1. **Week 1:** Add Java + Go regex import detection (Gap 2) -- quick win, marketing parity
2. **Week 1-2:** Add OWASP AI Top 10 + MITRE ATLAS + NIST CSF 2.0 framework mappings (Gap 4)
3. **Week 2-3:** Complete tree-sitter JS/TS integration with flow tracing (Gap 1)
4. **Week 3:** AVID integration + pip-audit/osv-scanner recommendations (Gap 5)
5. **Ongoing:** Community building, GitHub presence, developer docs (Gap 6 prerequisites)

**Total estimated effort for all code changes: ~3-4 weeks of focused development.**

---

## Sources

- [Systima Comply announcement (DEV.to)](https://dev.to/systima/open-source-eu-ai-act-compliance-scanning-for-cicd-4ogj)
- [ArkForge MCP EU AI Act (GitHub)](https://github.com/ark-forge/mcp-eu-ai-act)
- [Agent-BOM (GitHub)](https://github.com/msaad00/agent-bom)
- [AVID - AI Vulnerability Database](https://avidml.org/)
- [NIST AI 100-2e2025 Adversarial ML Taxonomy](https://csrc.nist.gov/pubs/ai/100/2/e2025/final)
- [Gartner Market Guide for AI Governance Platforms](https://www.gartner.com/en/documents/7145930)
- [Forrester Wave AI Governance Solutions Q3 2025](https://www.forrester.com/report/the-forrester-wave-tm-ai-governance-solutions-q3-2025/RES184849)
- [Credo AI Forrester Wave results](https://www.credo.ai/blog/credo-ai-named-a-leader-in-the-forrester-wave-tm-ai-governance-solutions-q3-2025)
- [CVE AI Working Group research](https://dl.acm.org/doi/10.1145/3733799.3762969)
