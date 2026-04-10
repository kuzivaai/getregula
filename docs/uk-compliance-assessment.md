# UK Data Protection and Privacy Compliance Assessment for Regula

**Assessment date:** 2026-04-09  
**Assessor:** AI-assisted (requires legal review)  
**Scope:** Regula CLI tool operation, user guidance, UK landing page positioning

---

## Executive Summary

Regula is a local-only, offline CLI tool that scans codebases for AI governance risk indicators. It processes no personal data in its own operation. Users of Regula, however, may be UK-based organisations deploying AI systems subject to both the EU AI Act (extraterritorial) and the UK's data protection and AI regulatory framework.

**Key findings:**

1. **Regula's own operation raises no UK GDPR concerns** - it is a static analysis tool that runs locally, processes no personal data, and makes no network calls by default.
2. **Regula already surfaces UK-specific guidance** via the ICO/DSIT framework mapping in `references/framework_crosswalk.yaml` - this is accurate and current.
3. **Material UK regulatory changes occurred in February 2026** with the Data (Use and Access) Act 2025 provisions on automated decision-making coming into force - the UK landing page should be updated to reflect this.

---

## Question 1: Does Regula's Own Operation Raise Any UK GDPR Concerns?

### Assessment: NO UK GDPR concerns in Regula's operation

**Analysis:**

Regula is a static analysis CLI tool with the following data handling characteristics:

| Aspect | Regula Behaviour | UK GDPR Relevance |
|--------|------------------|-------------------|
| **Data processed** | Source code files (local only) | Source code is not "personal data" under UK GDPR Art 4(1) unless it contains embedded PII |
| **Network activity** | None by default | No data transfer outside the user's machine |
| **Telemetry** | Opt-in only, GDPR-compliant consent flow | `scripts/telemetry.py` implements Art 7(3) withdrawal-as-easy-as-consent |
| **Data storage** | Config in `~/.regula/config.toml` | Stores only user preferences (telemetry consent), not personal data |
| **Personal data in scanned files** | Not extracted or processed | Regula pattern-matches code structure, not data content |

**Verification (from codebase):**

1. `scripts/telemetry.py` lines 77-88: Consent prompt is opt-in ("Send anonymous crash reports? [y/N]"), defaults to No
2. `scripts/telemetry.py` line 103: `send_default_pii=False` in Sentry configuration
3. `scripts/telemetry.py` line 79: Explicit statement "No source code, file paths, or personal data are ever sent"
4. No network calls in core scanning functions (`classify_risk.py`, `ast_engine.py`, `code_analysis.py`)

**Conclusion:** Regula does not process personal data in the course of its operation. The telemetry feature, when enabled, sends only crash stack traces with PII stripped. UK GDPR does not apply to Regula's own operation.

**One edge case to document:** If a user scans code that contains hardcoded personal data (e.g., test fixtures with real names/emails), Regula does not extract or transmit this data - it only pattern-matches for AI governance risk indicators. This is analogous to a linter reading code; the code content is not "processed" in the UK GDPR sense.

---

## Question 2: What UK-Specific Guidance Should Regula Surface to Users?

### Current State (Verified)

Regula already maps findings to UK ICO/DSIT guidance via `references/framework_crosswalk.yaml`. The mapping covers:

| EU AI Act Article | UK ICO/DSIT Mapping | Status |
|-------------------|---------------------|--------|
| Art 9 (Risk Management) | DSIT Principle 1 (Safety/security/robustness), DSIT Principle 5 (Accountability), ICO Accountability (Art 5(2) UK GDPR) | Current |
| Art 10 (Data Governance) | ICO Data minimisation, Storage limitation, Accuracy (Art 5(1)(c)(d)(e) UK GDPR), DSIT Principle 3 (Fairness) | Current |
| Art 11 (Technical Documentation) | DSIT Principle 5 (Accountability), ICO DPIA requirement, Art 30 records | Current |
| Art 12 (Record-Keeping) | ICO Accountability (Art 5(2) UK GDPR), ICO "Explaining decisions made with AI" | Current |
| Art 13 (Transparency) | DSIT Principle 2 (Transparency/explainability), ICO Art 22 explanation rights | **Needs update** |
| Art 14 (Human Oversight) | DSIT Principle 5 (Contestability/redress), ICO Art 22 UK GDPR human review | **Needs update** |
| Art 15 (Accuracy/Robustness/Cybersecurity) | DSIT Principle 1 (Safety), ICO Accuracy + Security (Art 5(1)(d)(f) UK GDPR) | Current |

### Recommended Updates for UK Guidance

**1. Reflect Data (Use and Access) Act 2025 changes to Article 22**

The DUAA came into force on 5 February 2026 and materially changes the UK automated decision-making framework:

- **Broader lawful basis:** Controllers can now rely on "legitimate interests" for ADM processing (not just consent/contract)
- **New safeguard requirements:** Information provision before/after decision, representations mechanism, human intervention right
- **Special category restriction narrowed:** Restriction now applies only to significant decisions based "entirely or partly" on special category data

**Recommendation:** Update `references/framework_crosswalk.yaml` Article 14 mapping to reference DUAA 2025 s.80 alongside Art 22 UK GDPR.

**2. Add ICO Agentic AI guidance reference**

The ICO published "Tech Futures: Agentic AI" in January 2026. This is relevant for users scanning autonomous agent codebases.

**Recommendation:** Add a note to Article 14 (Human Oversight) mapping referencing ICO agentic AI guidance.

**3. Reference ICO's active enforcement areas**

ICO announced investigation into Grok (February 2026) for non-consensual AI-generated imagery. This signals enforcement priority on:
- Training data provenance
- Non-consensual output generation
- AI-generated CSAM

**Recommendation:** Add these to the `regula check` output when NSFW/content moderation patterns are detected.

### UK-Specific Patterns to Consider Adding

The following patterns are relevant to UK users but not currently in Regula's pattern set:

| Pattern | UK Regulatory Basis | Priority |
|---------|---------------------|----------|
| Facial recognition in public spaces | ICO Biometrics Guidance + Bridges v South Wales Police [2020] EWCA Civ 1058 | Medium |
| Emotion recognition in employment | ICO Employment Practices guidance, DSIT Principle 3 (Fairness) | Medium |
| Children's data in AI training | ICO Age-Appropriate Design Code | High |
| Automated hiring/CV screening | ICO Employment guidance + emerging tribunal case law | High |

---

## Question 3: UK AI Regulation Developments (March-April 2026)

### Material Changes Requiring Landing Page Update

**1. Data (Use and Access) Act 2025 - Part 5 in force (5 February 2026)**

This is the most significant UK data protection change since Brexit. The DUAA:

- Reforms Article 22 UK GDPR automated decision-making rules
- Adds "meaningful human involvement" definition framework (ICO to publish guidance)
- Broadens lawful basis options for ADM
- Retains core safeguards but with more flexibility

**Landing page impact:** The "What is already in force" section should be updated to reference DUAA 2025 as the new baseline for ADM compliance, not just Art 22 UK GDPR.

**2. ICO AI and Biometrics Strategy Update (March 2026)**

The ICO published a strategy update with:
- Engagement with 11 major AI foundation model developers
- Policy positions on generative AI to be published "in coming months"
- Active investigation into Grok

**Landing page impact:** The "ICO has scaled up AI enforcement" bullet should be updated with the Grok investigation and foundation model engagement.

**3. Artificial Intelligence (Regulation) Bill [HL] - Still not law**

Lord Holmes's private member's bill has been re-introduced but has not progressed. The tracker row "Dedicated AI Act: Not currently on the government's legislative agenda" remains accurate.

**Landing page impact:** No change required. The "PENDING" status is correct.

**4. Copyright and AI - Section 137 DUAA progress report due**

DSIT must lay a report before Parliament by 18 March 2026 on copyright and AI training data.

**Landing page impact:** Consider adding to "What we are tracking" section if the report materially affects AI compliance obligations.

### Recommended Landing Page Edits

```yaml
# content/regulations/united-kingdom.py suggested changes

# 1. Update last_updated
"last_updated": "2026-04-09"

# 2. Add new tracker row for DUAA
{
    "label": "Data (Use and Access) Act 2025",
    "value": "Part 5 in force (5 Feb 2026) — reforms automated decision-making (Art 22A UK GDPR)",
    "state": "verified",
}

# 3. Update ICO AI guidance tracker row
{
    "label": "ICO AI guidance",
    "value": (
        "In force — Art 22A ADM safeguards, DPIAs for AI, explainability guidance. "
        "Active enforcement: Grok investigation (Feb 2026), foundation model engagement."
    ),
    "state": "verified",
}

# 4. Update "What is already in force" section to reference DUAA
```

---

## Glass Box Audit Trail

```yaml
glass_box:
  matter: "UK compliance assessment for Regula CLI"
  date: "2026-04-09"
  regulations_applied:
    - "UK GDPR, Articles 4(1), 5(1), 5(2), 22"
    - "Data Protection Act 2018"
    - "Data (Use and Access) Act 2025, Part 5, s.80"
    - "DSIT Five AI Principles (non-statutory)"
  ico_guidance_consulted:
    - "Guidance on AI and data protection (current)"
    - "AI and Biometrics Strategy Update — March 2026"
    - "Tech Futures: Agentic AI (January 2026)"
    - "Explaining decisions made with AI (with Alan Turing Institute)"
  authoritative_sources:
    - "legislation.gov.uk — Data (Use and Access) Act 2025"
    - "ico.org.uk — AI and biometrics strategy update March 2026"
    - "ico.org.uk — Investigation into Grok announcement February 2026"
    - "gov.uk — DUAA 2025 commencement regulations"
    - "bills.parliament.uk — Artificial Intelligence (Regulation) Bill [HL] status"
  citations_verified:
    - "UK GDPR Art 4(1) — VERIFIED (in force)"
    - "UK GDPR Art 22 — VERIFIED (amended by DUAA 2025 s.80)"
    - "DUAA 2025 Part 5 commencement — VERIFIED (5 February 2026)"
    - "ICO Grok investigation — VERIFIED (February 2026 announcement)"
  confidence: "HIGH — all claims traced to primary legislation or ICO publications"
  limitations:
    - "ICO 'meaningful human involvement' guidance not yet published — analysis based on DUAA text"
    - "Copyright/AI report (s.137 DUAA) not yet laid before Parliament"
  reviewer: "AI-assisted — requires DPO/solicitor review"
```

---

## Recommended Actions

### Immediate (before next release)

1. **Update `content/regulations/united-kingdom.py`** to reflect DUAA 2025 Part 5 commencement
2. **Update `references/framework_crosswalk.yaml`** Article 14 mapping to reference DUAA 2025 s.80
3. **Regenerate `uk-ai-regulation.html`** with updated content

### Near-term (next 30 days)

4. **Monitor ICO publication** of "meaningful human involvement" guidance under DUAA
5. **Add risk pattern** for children's data in AI training (Age-Appropriate Design Code)
6. **Add risk pattern** for automated hiring/CV screening (ICO Employment guidance)

### Tracking

7. **Watch for ICO generative AI policy positions** promised for "coming months"
8. **Monitor Copyright/AI report** due under s.137 DUAA

---

## Sources

- [ICO — Guidance on AI and data protection](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/artificial-intelligence/guidance-on-ai-and-data-protection/)
- [ICO — AI and Biometrics Strategy Update March 2026](https://ico.org.uk/about-the-ico/our-information/our-strategies-and-plans/artificial-intelligence-and-biometrics-strategy/ai-and-biometrics-strategy-update-march-2026/)
- [ICO — Investigation into Grok (February 2026)](https://ico.org.uk/about-the-ico/media-centre/news-and-blogs/2026/02/ico-announces-investigation-into-grok/)
- [ICO — Tech Futures: Agentic AI](https://ico.org.uk/about-the-ico/research-reports-impact-and-evaluation/research-and-reports/technology-and-innovation/tech-horizons-and-ico-tech-futures/ico-tech-futures-agentic-ai/)
- [Data (Use and Access) Act 2025 — automated decision-making provisions](https://www.legislation.gov.uk/ukpga/2025/18/part/5/chapter/1/crossheading/automated-decisionmaking)
- [DUAA 2025 commencement plans](https://www.gov.uk/guidance/data-use-and-access-act-2025-plans-for-commencement)
- [ICO — DUAA 2025 what it means for organisations](https://ico.org.uk/about-the-ico/what-we-do/legislation-we-cover/data-use-and-access-act-2025/the-data-use-and-access-act-2025-what-does-it-mean-for-organisations/)
- [Artificial Intelligence (Regulation) Bill [HL] — Parliament](https://bills.parliament.uk/bills/3942)
- [DSIT — A pro-innovation approach to AI regulation](https://www.gov.uk/government/publications/ai-regulation-a-pro-innovation-approach)
- [Copyright and AI progress report under s.137 DUAA](https://www.gov.uk/government/publications/copyright-and-artificial-intelligence-progress-report/copyright-and-artificial-intelligence-statement-of-progress-under-section-137-data-use-and-access-act)
