# Legal Risk Assessment: Regula Open-Source Project

**Date**: 2026-04-09
**Assessor**: Legal Risk Assessment Skill (not legal advice)
**Matter**: Regula open-source CLI — legal risk exposure for UK-based individual maintainer
**Privileged**: No

---

## Executive Summary

Regula is an MIT-licensed, open-source static analysis CLI that scans code for EU AI Act risk patterns. It makes no legal determinations, operates entirely locally, and includes disclaimers on every output surface. The maintainer (Kuziva Muzondo) is a UK-based individual.

**Overall assessment: GREEN to YELLOW risk profile.**

The most significant risk factor is **professional indemnity exposure** from publishing compliance-adjacent tooling without qualifications, but this is substantially mitigated by (a) the explicit "not legal advice" disclaimers throughout, (b) the MIT licence's warranty exclusion, (c) the tool's positioning as a development aid rather than compliance service, and (d) the absence of any contractual relationship with users.

No RED or ORANGE risks were identified. Two risks are scored YELLOW (medium), three are scored GREEN (low).

---

## Risk 1: Product Liability — Reliance on Incomplete Detection

### Risk Description

A user relies on Regula's output to conclude their AI system is not high-risk or not prohibited, then faces regulatory enforcement or business loss when a pattern was missed. The user claims Regula's output caused them to ship a non-compliant system.

### Background and Context

- Regula is a pattern-matching static analysis tool, not a legal classification engine.
- The README, landing pages, CLI output, and HTML reports all contain explicit disclaimers: "Not legal advice", "pattern-based risk indication, not legal determination", "consult qualified legal counsel".
- The tool publishes honest precision metrics (15.2% overall, 100% on synthetic prohibited/high-risk corpus) and explicitly warns about false positives and false negatives.
- No contractual relationship exists between the maintainer and users; the software is provided under MIT "as is, without warranty of any kind".

### Severity Assessment: 2 (Low)

**Rationale**: Even if a user could establish reliance, the financial exposure to an individual open-source maintainer is limited. There is no revenue, no contract, no professional engagement. The user's loss would be regulatory fines or business damage, but proving proximate causation from a free, disclaimered tool to that loss is a substantial hurdle.

English product liability law under the Consumer Protection Act 1987 applies to "products" causing "damage". Software-as-product remains an unsettled area, and the CPA primarily addresses physical injury and damage to property exceeding 275 GBP. Pure economic loss from regulatory non-compliance is not covered by the CPA.

A negligent misstatement claim under *Hedley Byrne & Co Ltd v Heller & Partners Ltd* [1964] AC 465 requires (a) a special relationship where the defendant assumed responsibility, (b) reasonable reliance by the claimant, and (c) damage resulting from that reliance. The explicit disclaimers substantially negate (a) — Regula expressly disclaims any assumption of responsibility for compliance decisions.

### Likelihood Assessment: 1 (Remote)

**Rationale**: 
- No reported incident of a user relying on Regula output and suffering loss.
- The disclaimers are pervasive and unambiguous.
- Users sophisticated enough to use a CLI static analysis tool are likely to understand its limitations.
- There is no commercial relationship that would create heightened duty.
- The EU AI Act enforcement deadline for Annex III obligations (2 August 2026 or potentially December 2027 under the Digital Omnibus) has not yet passed, so there is no enforcement track record yet.

### Risk Score: 2 (Severity 2 x Likelihood 1) — GREEN

### Mitigating Factors

1. **Explicit disclaimers on every surface**: README, website footer, CLI output, HTML reports all state "Not legal advice" and "consult qualified legal counsel".
2. **MIT licence warranty exclusion**: "THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED".
3. **Honest precision reporting**: The tool publishes its measured precision (15.2% overall) and explicitly warns about false negatives.
4. **No contractual relationship**: Users self-install from PyPI or GitHub; no agreement, no consideration, no professional engagement.
5. **Tool positioning**: Regula is positioned as a "starting point for compliance awareness, not a finish line" and explicitly states it does not replace "the organisational, procedural, and legal work required for full compliance".

### Recommended Actions

- **Maintain disclaimers**: Continue including "Not legal advice" and limitation language on every output surface.
- **Avoid scope creep**: Do not add features that imply definitive legal classification (e.g., "Certificate of Compliance" generation).
- **Document the boundary clearly**: The current README section "What Regula Is (and Isn't)" is well-drafted; keep it updated.

### Residual Risk: GREEN (Score 1-2)

---

## Risk 2: Intellectual Property — Scanning Third-Party Code

### Risk Description

Regula scans source code files and outputs findings referencing file paths and line numbers. Could this create copyright exposure (e.g., derivative work from reading third-party code) or trade secret issues?

### Background and Context

- Regula reads source files from the user's local filesystem.
- It performs pattern matching (regex and AST analysis) against the source text.
- Output includes file paths, line numbers, and pattern names — not verbatim reproduction of source code.
- The tool never transmits any data off the user's machine.

### Severity Assessment: 1 (Negligible)

**Rationale**: Reading a file and emitting metadata (file path, line number, pattern match name) does not create a derivative work under UK copyright law (Copyright, Designs and Patents Act 1988). The substantial part of a literary work (source code) is not copied — only incidental reference data is output.

The user, not Regula's maintainer, initiates the scan on their own filesystem. The maintainer has no knowledge of or access to the code being scanned.

Trade secret concerns would apply to the code owner's relationship with their own employees/contractors, not to a static analysis tool running locally.

### Likelihood Assessment: 1 (Remote)

**Rationale**: There is no precedent for copyright claims against static analysis tools that read source files without reproducing them. Linters (ESLint), security scanners (Semgrep), and IDE autocomplete tools all operate the same way without legal challenge.

### Risk Score: 1 (Severity 1 x Likelihood 1) — GREEN

### Mitigating Factors

1. **No reproduction of source code**: Regula outputs metadata, not verbatim code.
2. **Local operation**: The tool runs entirely on the user's machine; the maintainer has no access to scanned code.
3. **User-initiated**: The user chooses to scan their own codebase.
4. **Industry standard pattern**: Thousands of static analysis tools operate identically.

### Recommended Actions

- **No action required**: Current design is standard industry practice.
- **Do not add code-echoing features**: Avoid features that would reproduce substantial portions of scanned code in reports (beyond the current line-number references).

### Residual Risk: GREEN (Score 1)

---

## Risk 3: AI Regulation — Could Regula Itself Be a High-Risk AI System?

### Risk Description

Under the EU AI Act (Regulation 2024/1689) or the UK's emerging AI governance frameworks, could Regula be classified as a high-risk AI system subject to Articles 9-15 obligations or equivalent UK requirements?

### Background and Context

- Regula is a static analysis tool using regex pattern matching and AST parsing.
- It does not use machine learning models, neural networks, or probabilistic inference.
- It does not make autonomous decisions — it outputs findings for human review.
- It does not fall into any Annex III high-risk category (biometrics, credit scoring, hiring, etc.).
- It is not a general-purpose AI model (GPAI) under Articles 53-55.

### Severity Assessment: 1 (Negligible)

**Rationale**: Article 3(1) of the EU AI Act defines "AI system" using the OECD definition, which requires the system to "infer, from the input it receives, how to generate outputs such as predictions, content, recommendations, or decisions". Regula does not infer — it applies deterministic pattern matching. A regex match is not inference.

Even if Regula were somehow classified as an AI system, it would not fall into any Annex III high-risk category. It is not used for biometric identification, credit scoring, employment decisions, education assessment, law enforcement, migration control, justice administration, or democratic process integrity. It is a developer tool for code review.

Under UK law, there is no AI-specific legislation currently in force. The UK model is principles-based and sector-specific (ICO for data protection, FCA for financial services, etc.). Regula does not process personal data and does not operate in any regulated sector.

### Likelihood Assessment: 1 (Remote)

**Rationale**: 
- Pattern-matching tools are not AI systems under any reasonable reading of Article 3(1).
- The EU AI Office has not indicated that static analysis tools are in scope.
- The UK has no equivalent legislation that would capture Regula.

### Risk Score: 1 (Severity 1 x Likelihood 1) — GREEN

### Mitigating Factors

1. **Deterministic operation**: Regula uses regex and AST parsing, not machine learning.
2. **No high-risk deployment**: The tool is not deployed in any Annex III domain.
3. **Developer tooling category**: Static analysis tools are universally understood as developer aids, not autonomous decision-makers.
4. **No UK-specific AI law**: The UK's principles-based approach does not create obligations for developer tools.

### Recommended Actions

- **Monitor regulatory developments**: If the EU AI Office issues guidance on developer tooling, review Regula's classification.
- **Document the architecture**: The current `docs/architecture.md` explains the deterministic nature of the tool; keep it updated.

### Residual Risk: GREEN (Score 1)

---

## Risk 4: Data Protection — Processing of Personal Data in Scanned Codebases

### Risk Description

Users may run Regula on codebases that contain personal data (e.g., test fixtures with real names, hardcoded email addresses, customer data in config files). Does Regula's processing of this data create UK GDPR obligations for the maintainer?

### Background and Context

- Regula scans source files locally on the user's machine.
- It never transmits any data to external servers (no telemetry, no cloud sync).
- The maintainer has no access to or knowledge of the data being scanned.
- Output includes file paths and pattern match metadata, not the personal data itself.

### Severity Assessment: 2 (Low)

**Rationale**: Under UK GDPR, a "controller" is defined as the person who determines the purposes and means of processing personal data. The maintainer does not determine the purposes — the user does, by choosing to scan their codebase. The maintainer does not have access to the data being processed.

The user is the controller (or processor, if acting on behalf of their employer). The maintainer merely provides a tool; they are analogous to a software vendor, not a data processor.

If personal data appears in Regula's output (e.g., a file path contains a name), this is incidental to the user's own processing, not data processing by the maintainer.

### Likelihood Assessment: 2 (Unlikely)

**Rationale**: 
- The ICO has not indicated that open-source tool maintainers are controllers for data processed locally by users.
- There is no data transfer to the maintainer.
- The precedent for IDE, linter, and security scanner tools is clear: the tool vendor is not the controller.

### Risk Score: 4 (Severity 2 x Likelihood 2) — GREEN

### Mitigating Factors

1. **Local processing only**: Data never leaves the user's machine.
2. **No telemetry**: Regula has explicit no-telemetry architecture (the telemetry module exists for optional self-hosted metrics, not cloud reporting).
3. **User is controller**: The user determines what to scan and what to do with the output.
4. **No data retention**: Regula does not persist user data beyond the scan session (audit logs are local, user-controlled).

### Recommended Actions

- **Maintain no-telemetry architecture**: Do not add features that would transmit scan data externally.
- **Document data handling**: Consider adding a brief "Data handling" section to the README or TRUST.md explaining that Regula processes data locally only.
- **Secret detection as feature, not bug**: The existing credential detection (`regula check` flags hardcoded secrets) actually helps users avoid shipping personal data; position this as a privacy feature.

### Residual Risk: GREEN (Score 2-4)

---

## Risk 5: Professional Indemnity — Compliance-Adjacent Tooling Without Qualifications

### Risk Description

The maintainer publishes a tool that helps developers with EU AI Act compliance without holding qualifications as a solicitor, barrister, or certified compliance professional. Could this create exposure under professional liability or "holding out" regulations?

### Background and Context

- Regula explicitly disclaims providing legal advice on every output surface.
- The tool is positioned as a developer aid, not a legal or compliance service.
- No contractual relationship exists with users.
- The maintainer does not hold themselves out as a legal or compliance professional.
- Similar tools exist in the market (e.g., Credo AI, Holistic AI, security scanners, GRC platforms) operated by companies that are not law firms.

### Severity Assessment: 3 (Moderate)

**Rationale**: The Legal Services Act 2007 reserves certain "reserved legal activities" (rights of audience, conduct of litigation, reserved instrument activities, probate activities, notarial activities, administration of oaths) to authorised persons. Providing commentary or tooling on regulatory compliance is NOT a reserved legal activity. The Solicitors Regulation Authority (SRA) does not regulate compliance software providers.

However, if a user could establish that they relied on Regula's output as legal advice (despite the disclaimers) and suffered loss, there could be a negligent misstatement claim under common law. The moderate severity reflects the theoretical possibility of such a claim, even though the likelihood is low.

The maintainer is an individual, not a company with D&O insurance, which increases personal exposure if a claim were pursued.

### Likelihood Assessment: 2 (Unlikely)

**Rationale**: 
- The disclaimers are explicit and pervasive.
- The tool does not give specific legal advice — it flags patterns for human review.
- Users of CLI developer tools are generally sophisticated and understand the tool/legal-advice boundary.
- No reported claims against open-source compliance tooling maintainers exist in the UK.
- Competitor tools (security scanners, GRC platforms) operate similarly without legal challenge.

### Risk Score: 6 (Severity 3 x Likelihood 2) — YELLOW

### Contributing Factors

- The EU AI Act is new and enforcement is imminent (August 2026 for Annex III obligations).
- If enforcement actions increase and businesses look for someone to blame, attention could shift to tooling.
- The maintainer is an individual without corporate liability shield.

### Mitigating Factors

1. **Explicit disclaimers**: "Not legal advice" appears on every output surface.
2. **Not a reserved legal activity**: Compliance tooling is not regulated by the Legal Services Act 2007.
3. **Tool, not advice**: Regula outputs findings for review, not recommendations on what to do.
4. **Industry standard**: Hundreds of compliance-adjacent tools (security scanners, audit tools, GRC platforms) operate similarly.
5. **MIT licence**: "THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND".

### Recommended Actions

| Option | Effectiveness | Cost/Effort | Recommended? |
|--------|---------------|-------------|--------------|
| Maintain disclaimers on all surfaces | High | Low | Yes |
| Add disclaimer to CLI --help output | Medium | Low | Yes |
| Consider personal liability insurance | Medium | Medium | Consider |
| Incorporate a limited company for the project | High | Medium | Consider (if project grows) |
| Avoid language implying legal certainty | High | Low | Yes |

### Recommended Approach

1. **Immediate**: Ensure the CLI `--help` output includes a brief disclaimer (e.g., "Regula provides risk indicators, not legal advice").
2. **Short-term**: Review all output language to ensure no phrasing implies legal certainty (e.g., avoid "your system IS prohibited" — prefer "patterns associated with prohibited practices were detected").
3. **Medium-term**: If Regula gains significant adoption or commercial users, consider incorporating a limited company (Ltd) to create a corporate liability shield, and/or obtaining professional indemnity insurance.

### Residual Risk: YELLOW (Score 4-6) after mitigations

---

## Risk Register Summary

| Risk ID | Description | Category | Severity | Likelihood | Score | Level | Owner | Status |
|---------|-------------|----------|----------|------------|-------|-------|-------|--------|
| REG-001 | Product liability — user reliance on incomplete detection | Contract/Tort | 2 | 1 | 2 | GREEN | Maintainer | Mitigated |
| REG-002 | IP risk — scanning third-party code | IP | 1 | 1 | 1 | GREEN | Maintainer | Accepted |
| REG-003 | AI regulation — Regula as high-risk system | Regulatory | 1 | 1 | 1 | GREEN | Maintainer | Accepted |
| REG-004 | Data protection — personal data in scanned codebases | Data Privacy | 2 | 2 | 4 | GREEN | Maintainer | Mitigated |
| REG-005 | Professional indemnity — compliance-adjacent tooling | Professional | 3 | 2 | 6 | YELLOW | Maintainer | Open |

---

## Consolidated Action Items

| ID | Action | Type | Owner | Due | Urgency |
|----|--------|------|-------|-----|---------|
| REG-001-01 | Add disclaimer to CLI `--help` output | mitigate | Maintainer | 2026-04-30 | medium |
| REG-001-02 | Audit CLI output language for certainty phrasing | mitigate | Maintainer | 2026-04-30 | medium |
| REG-004-01 | Add "Data handling" section to TRUST.md | document | Maintainer | 2026-05-31 | low |
| REG-005-01 | Research personal liability insurance options | mitigate | Maintainer | 2026-06-30 | low |
| REG-005-02 | If adoption grows, consider Ltd incorporation | prevent | Maintainer | Ongoing | low |

---

## Glass Box Audit Trail

```yaml
glass_box:
  matter: "Regula open-source CLI — legal risk assessment for UK individual maintainer"
  assessment_date: "2026-04-09"
  legal_domains: ["Contract", "Tort", "IP", "Data Privacy", "Regulatory", "Professional Liability"]
  statutes_consulted:
    - "Consumer Protection Act 1987"
    - "Copyright, Designs and Patents Act 1988"
    - "UK GDPR (as retained under the European Union (Withdrawal) Act 2018)"
    - "Data Protection Act 2018"
    - "Legal Services Act 2007"
    - "EU AI Act (Regulation 2024/1689), Articles 3, 5, 6, 9-15, Annex III"
  cases_consulted:
    - "Hedley Byrne & Co Ltd v Heller & Partners Ltd [1964] AC 465"
  regulatory_guidance:
    - "ICO — Guidance on AI and data protection"
    - "SRA — Reserved legal activities guidance"
  citations_verified:
    - "Consumer Protection Act 1987 — VERIFIED (in force)"
    - "Legal Services Act 2007 — VERIFIED (in force)"
    - "EU AI Act Article 3(1) — VERIFIED (in force)"
  severity_rationale: "Assessed based on financial exposure to an individual maintainer of a free, open-source tool with explicit disclaimers and no contractual relationships"
  likelihood_rationale: "Assessed based on absence of precedent, pervasive disclaimers, and industry standard practice for developer tooling"
  confidence: "HIGH — analysis based on settled English law principles and clear factual matrix"
  contra_indicators:
    - "EU AI Act enforcement has not yet begun for Annex III systems — enforcement patterns may differ from expectations"
    - "AI governance tooling is a new category — novel claims could emerge"
    - "Individual maintainer lacks corporate shield — personal assets theoretically at risk"
  limitations:
    - "Assessment based on facts as presented — not independently verified"
    - "Does not constitute legal advice"
    - "UK law only — does not assess liability under EU Member State laws, US law, or other jurisdictions"
  privilege_status: "Not privileged — published as project documentation"
  rlm_verification: "PASS — all risks scored GREEN or YELLOW; no ORANGE or RED findings"
```

---

## Disclaimer

**This document does not constitute legal advice.** It is a risk assessment framework applied to publicly available information about an open-source project. The assessment should be reviewed by a qualified solicitor before reliance. Risk scores are indicative, not definitive. The maintainer should seek professional legal advice before taking significant decisions based on this assessment.

---

*Generated: 2026-04-09*
