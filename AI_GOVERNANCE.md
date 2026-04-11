# AI Governance — Regula Development Practices

This document describes how AI is used in the development of Regula, what oversight processes exist, and where AI-generated outputs carry risk.

Regula is a compliance scanning tool. It should demonstrate the governance practices it advocates. To generate a governance scaffold for your own project, run `regula governance --project /path/to/project`.

---

## AI's Role in Development

Regula is developed by a sole developer (Kuziva Muzondo) with substantial assistance from Claude (Anthropic), primarily Claude Opus 4.6.

**What Claude generates:**

- Code — CLI commands, detection logic, test files, HTML/CSS for the website
- Detection patterns — regex patterns mapped to EU AI Act articles, reviewed and validated by the developer before merge
- Compliance framework cross-mappings — article-to-framework mappings in `references/framework_crosswalk.yaml`
- Documentation — README sections, blog posts, technical docs, this document
- Test cases — both unit tests and integration tests

**What Claude does not do:**

- Make final decisions about what ships — every commit is reviewed by the developer
- Access production systems or user data — Regula runs locally, there is no production backend
- Determine regulatory interpretation — article mappings reflect the regulation text, not Claude's legal opinion
- Replace the developer's judgement on risk classification accuracy

---

## Human Oversight Process

Every AI-generated output goes through the following before reaching `main`:

1. **Code review** — The developer reads every diff before committing. AI-generated code is not auto-merged.
2. **Test verification** — The project's test suite (751 pytest tests, 11 CLI integration tests, 6 self-test assertions, 10 doctor checks) runs before any claim of "done."
3. **Claim auditor** — A CI pipeline (`scripts/claim_auditor.py`) scans all modified Markdown and HTML files for unverified numeric claims, superlatives, and competitive assertions. Unsourced claims fail the build.
4. **Site facts verification** — `scripts/site_facts.py` computes every numeric claim on the landing pages from the actual codebase. If a page claim drifts from the computed value, the discrepancy is visible.
5. **Benchmark validation** — Detection pattern changes are tested against a labelled corpus of 257 hand-labelled findings from 5 open-source projects plus a 13-file synthetic corpus. Results are published in `docs/benchmarks/PRECISION_RECALL_2026_04.md`.

---

## Accountability

The sole developer (Kuziva Muzondo) is responsible for all outputs of this project, including AI-generated code, documentation, detection patterns, and compliance mappings.

"AI-assisted" does not mean "AI-decided." Every pattern classification, every article mapping, and every compliance claim was reviewed by a human before publication. If something is wrong, the responsibility lies with the developer who approved it, not with the model that generated it.

---

## Risk Assessment

AI-generated outputs in Regula carry specific risks. These are documented honestly, not minimised.

### Where AI-generated errors could cause harm

| Component | Risk if wrong | Mitigation |
|---|---|---|
| **Risk classification** (prohibited/high-risk/limited/minimal) | False confidence: a user believes their system is minimal-risk when it is actually high-risk, and skips compliance obligations | Published precision benchmark (15.2% on OSS corpus); "not legal advice" disclaimer on every page; classification requires deployment context confirmation |
| **Article mappings** (pattern → EU AI Act article) | Incorrect obligations: a user implements the wrong compliance measures | Cross-referenced against regulation text; framework crosswalk reviewed against primary sources (ISO 42001, NIST AI RMF, etc.) |
| **Effort estimates** (hours per article) | Under-estimation leads to missed deadlines or under-resourcing | Estimates are ranges, not point values; clearly labelled as indicative |
| **Prohibited practice detection** | False negative: a genuinely prohibited system passes the scan undetected | 100% recall on synthetic corpus for Article 5 patterns; 0 BLOCK findings fired on 5 OSS projects (no false alarms at enforcement tier) |
| **Documentation generation** (Annex IV) | Generated documentation accepted as-is without review, creating a false compliance record | Output clearly marks sections as "auto-generated — requires human review"; never claims to be complete |

### What Regula explicitly does NOT do

- Provide legal advice (disclaimed on every page and in CLI output)
- Determine whether a system IS high-risk (that depends on deployment context, not code alone)
- Replace a human compliance review
- Monitor running systems (static analysis only)
- Guarantee compliance (it identifies risk indicators for human review)

---

## Detection Pattern Curation Methodology

### How the 330 patterns were selected

The 330-pattern count corresponds to the `historical_330_bucket` computation in `scripts/site_facts.py`: tiered risk regexes (279) + architecture detectors (38) + credential detectors (9) + oversight detectors (4).

Pattern sources:

1. **EU AI Act regulation text** — Each prohibited and high-risk pattern maps to a specific article and paragraph. The mapping is documented in `scripts/risk_patterns.py` alongside each pattern group.
2. **OWASP Top 10 for LLMs** and **OWASP Agentic Security** — AI security patterns (prompt injection, unsafe deserialisation, unbounded token generation) map to published OWASP categories.
3. **Common coding patterns** — Patterns were derived from how developers actually implement the regulated behaviours (e.g., `model.predict(applicant)` for credit scoring, `face_recognition` imports for biometric processing).

### How patterns are validated

- **Synthetic corpus** (13 hand-crafted files): Tests recall — does Regula find what it should find? Result: 100% recall on prohibited and high-risk patterns.
- **OSS corpus** (257 hand-labelled findings from 5 projects): Tests precision — when Regula flags something, is it actually relevant? Result: 15.2% overall precision; 0 false positives at BLOCK tier.

### What 15.2% precision means

15.2% means that across 257 findings on 5 open-source AI projects (instructor, pydantic-ai, langchain, scikit-learn, openai-python), 39 were true positives and 218 were false positives.

This is honest but requires context:

- **The 15.2% applies to INFO tier** — findings surfaced for manual review, not findings that fail CI builds.
- **BLOCK tier precision is effectively 100%** — 0 false positives across the entire OSS corpus. A team using Regula in CI with default settings gets zero false alarms.
- **WARN tier precision is 25%** — 2 true positives, 6 false positives.
- **The OSS corpus is deliberately adversarial** — these are mature AI libraries, not AI applications. They import AI frameworks extensively but are not themselves regulated AI systems. High false-positive rates on these projects are expected.

The benchmark methodology and reproduction steps are published in `docs/benchmarks/PRECISION_RECALL_2026_04.md`. Every number can be independently verified by running `regula benchmark` against the labelled corpus checked into the repository.

---

## Transparency

This document is part of the project's public repository. It is versioned alongside the code it describes. If the development practices change, this document should be updated in the same commit.

The project's `CLAUDE.md` file contains operational instructions for Claude Code sessions, including honesty requirements, verification standards, and the rule that no statistic may be fabricated.

---

*Last updated: 10 April 2026. Commit: see git log.*
