# Support Service Level Agreement

> **Document version:** 1.0
> **Last reviewed:** 2026-04-24
> **Regula version:** 1.7.0
> **Maintainer:** Kuziva AI Ltd

Regula is an open-source EU AI Act compliance CLI tool maintained by a
small team. This document describes three tiers of support available to
deployers, providers, and governance teams using Regula as part of their
AI risk management systems. The commitments below are sustainable ones,
not marketing aspirations — every response target reflects capacity the
team can actually deliver.

For security vulnerabilities, do not use the channels below. Follow the
separate reporting process in [`SECURITY.md`](../SECURITY.md).

---

## Contents

1. [Severity definitions](#1-severity-definitions)
2. [Support tiers](#2-support-tiers)
3. [Escalation procedures](#3-escalation-procedures)
4. [Exclusions](#4-exclusions)
5. [Measurement and reporting](#5-measurement-and-reporting)
6. [Honest caveats](#6-honest-caveats)

---

## 1. Severity definitions

All tiers use the same four-level severity classification. The
priority level is determined by impact to the deployer's compliance
posture, not by subjective urgency.

| Priority | Name | Criteria | Examples |
|---|---|---|---|
| **P1** | Production blocker | Regula is inoperable or produces materially incorrect compliance output that could lead to a false sense of conformity. No workaround available. | Scanner crashes on all input; findings mapped to wrong EU AI Act articles; `regula conform` generates structurally invalid Annex IV documentation. |
| **P2** | Major degradation | Core functionality is impaired but a workaround exists, or a significant subset of scans produces incorrect results. | One risk category fails to detect known patterns; JSON output envelope breaks downstream tooling; `regula sbom` omits GPAI annotations. |
| **P3** | Minor issue | Non-critical defect, cosmetic error, or documentation inaccuracy that does not affect compliance output correctness. | Typo in CLI help text; minor formatting issue in evidence pack; incorrect cross-reference in framework crosswalk for a non-applicable framework. |
| **P4** | General enquiry | Feature request, usage question, integration guidance, or general feedback. | "How do I integrate Regula into our CI/CD pipeline?"; "Can Regula map findings to our internal risk taxonomy?"; "When will Sigstore signing ship?" |

The maintainer reserves the right to re-classify severity after initial
triage if the reported impact does not match the criteria above. The
reporter will be notified of any reclassification with an explanation.

---

## 2. Support tiers

### 2.1 Community (free / open source)

Available to all users. No contractual guarantee.

| Attribute | Detail |
|---|---|
| **Channels** | [GitHub Issues](https://github.com/kuzivaai/getregula/issues) and [GitHub Discussions](https://github.com/kuzivaai/getregula/discussions) |
| **Response time** | Best-effort, typically within 5 business days |
| **Coverage** | Business hours (UTC), weekdays |
| **Scope** | Bug reports, feature requests, documentation questions |
| **SLA guarantee** | None — best-effort only |

Community support is provided in public. All issues and discussions are
visible to other users, which means your question may also help others.
Regula's maintainer triages community issues regularly but cannot
guarantee response times.

### 2.2 Professional

For organisations that need predictable response times and direct
support for compliance mapping and integration work.

| Attribute | Detail |
|---|---|
| **Channels** | Email (`support@getregula.com`) + priority-labelled GitHub Issues |
| **Coverage** | Business hours (09:00–18:00 CET), weekdays |
| **Scope** | Everything in Community, plus: configuration assistance, compliance mapping questions, integration support, framework crosswalk guidance |
| **Includes** | Monthly regulatory update digest (EU AI Act developments, Omnibus status, relevant enforcement actions) |
| **Pricing** | Contact `support@getregula.com` |

**Response targets:**

| Priority | Initial response | Update cadence |
|---|---|---|
| P1 — Production blocker | 48 hours | Every 24 hours until resolved or mitigated |
| P2 — Major degradation | 3 business days | Every 3 business days |
| P3 — Minor issue | 5 business days | As progress is made |
| P4 — General enquiry | 7 business days | Single response unless follow-up needed |

"Initial response" means a substantive acknowledgement that includes
triage, severity confirmation, and either a resolution path or a
request for further information. An auto-reply does not count.

### 2.3 Enterprise

For organisations deploying Regula as a component of a formal AI risk
management system under Article 9 of the EU AI Act, or integrating
Regula into internal conformity assessment workflows.

| Attribute | Detail |
|---|---|
| **Channels** | Dedicated email address + optional shared Slack channel |
| **Coverage** | 24/7 for P1; extended business hours (08:00–20:00 CET, weekdays) for P2–P4 |
| **Scope** | Everything in Professional, plus: custom pattern development, private deployment assistance, regulatory advisory referral, named account contact |
| **Includes** | Quarterly compliance review call, early access to new features and pre-release builds |
| **Pricing** | Annual contract — contact `support@getregula.com` |

**Response targets:**

| Priority | Initial response | Update cadence |
|---|---|---|
| P1 — Production blocker | 4 hours (24/7) | Every 2 hours until resolved or mitigated |
| P2 — Major degradation | 8 business hours | Every business day |
| P3 — Minor issue | 2 business days | Every 3 business days |
| P4 — General enquiry | 3 business days | Single response unless follow-up needed |

Enterprise customers receive a named account contact and a private
issue tracker. Custom pattern development is scoped and scheduled
during the quarterly review call.

---

## 3. Escalation procedures

### 3.1 Standard escalation

If a response target is missed or you are dissatisfied with the
resolution path:

1. **Reply to the existing support thread** stating that you wish to
   escalate, with a brief explanation of why.
2. The escalation will be reviewed by the project lead within
   **one business day** (Professional) or **4 hours** (Enterprise).
3. If the escalation is not resolved within a further business day,
   email `support@getregula.com` with the subject line
   `[ESCALATION] <ticket reference>`.

### 3.2 Severity upgrade

If a previously classified P2/P3/P4 issue is found to have a greater
impact than initially assessed:

1. Provide evidence of the increased impact (e.g., incorrect
   compliance output affecting production systems, newly discovered
   scope of the defect).
2. The maintainer will re-triage within 4 business hours (Enterprise)
   or 1 business day (Professional).
3. If reclassified upward, the new response targets apply from the
   point of reclassification.

### 3.3 Security issues

Security vulnerabilities follow a separate process. Do not report
them through support channels. See [`SECURITY.md`](../SECURITY.md)
for the disclosure procedure and response timelines.

---

## 4. Exclusions

The following are **not covered** under any support tier:

| Exclusion | Rationale |
|---|---|
| **Legal advice or legal opinions** | Regula is a technical scanning tool, not a law firm. Interpreting whether your system falls under Article 6(2) or qualifies for an Article 6(3) exemption is a legal determination, not a technical one. |
| **Conformity assessments** | Regula generates scaffolding for Annex IV technical documentation and Annex VIII registration. It does not perform conformity assessments under Article 43, and its output is not a substitute for one. |
| **Organisational governance obligations** | Articles 9 (risk management system), 17 (quality management system), and 27 (fundamental rights impact assessment) are organisational obligations. Regula cannot verify that your organisation has implemented them. See [`what-regula-does-not-do.md`](what-regula-does-not-do.md). |
| **Third-party tool integrations** | Issues arising in Claude Code, Cursor, Windsurf, IDE plugins, or other tools that invoke Regula should be reported to the upstream tool maintainer. |
| **Custom fork support** | Modified versions of Regula, including patched or vendored copies, are not covered. Support applies to official releases published on [PyPI](https://pypi.org/project/regula-ai/). |
| **Infrastructure and hosting** | Regula is a local CLI tool with zero runtime dependencies. We do not provide support for the deployer's CI/CD infrastructure, Python environment, or operating system. |
| **Unsupported versions** | See the supported versions table in [`SECURITY.md`](../SECURITY.md). Issues reported against unsupported versions will receive a recommendation to upgrade. |

---

## 5. Measurement and reporting

### 5.1 How response times are measured

- **Clock starts** when the support request is received via the
  designated channel (email timestamp or GitHub issue creation time).
- **Clock stops** when the first substantive response is sent.
  Auto-acknowledgements and out-of-office replies do not stop the clock.
- **Business hours** are 09:00–18:00 CET, Monday to Friday, excluding
  public holidays in the maintainer's jurisdiction. P1 Enterprise
  coverage is 24/7 calendar hours.
- **Business days** are weekdays (Monday–Friday) within business hours.

### 5.2 Reporting (Professional and Enterprise)

- **Professional** customers receive a quarterly summary of support
  interactions, including response times achieved against targets.
- **Enterprise** customers receive a monthly support report, including:
  response time metrics, open issue status, and trend analysis.

### 5.3 SLA breach

If a response target under the Professional or Enterprise tier is not
met, the maintainer will:

1. Acknowledge the breach in the next communication.
2. Provide a root-cause explanation (e.g., capacity constraint,
   complexity of triage).
3. Document any process change made to prevent recurrence.

There are no financial penalties or service credits at this time.
Regula is maintained by a small team and these SLAs are commitments
of good faith, not contractual indemnities.

---

## 6. Honest caveats

This section exists because compliance officers deserve to know what
they are getting.

- **Small team.** Regula is maintained by a small team.
  The response targets above reflect what we can sustainably deliver.
  They are not padded for marketing and they are not aspirational.
  If capacity changes, this document will be updated before the
  targets change.

- **Open source, not zero-cost.** The Community tier is genuinely
  free and will remain so. The Professional and Enterprise tiers
  exist to fund sustainable maintenance of the project — including
  keeping the pattern library current as delegated acts, implementing
  acts, and guidance documents are published under the EU AI Act.

- **Tool, not programme.** Regula is one layer of an AI governance
  programme. It addresses the code-inspection layer. It does not
  replace your risk management system, your quality management
  system, your legal counsel, or your notified body. Support
  conversations that cross into those domains will be redirected
  to the appropriate function within your organisation.

- **Regulatory landscape is moving.** The EU AI Act is still being
  amended. The Omnibus proposal, delegated acts, and
  harmonised standards are still being finalised. Regula tracks
  these developments and updates its pattern library accordingly,
  but support responses reflect the regulatory state at the time
  of response, not a guarantee of future regulatory interpretation.

---

## Contact

| Purpose | Channel |
|---|---|
| Community support | [GitHub Issues](https://github.com/kuzivaai/getregula/issues) / [Discussions](https://github.com/kuzivaai/getregula/discussions) |
| Professional / Enterprise support | `support@getregula.com` |
| Security vulnerabilities | See [`SECURITY.md`](../SECURITY.md) |
| General enquiries | `support@getregula.com` |

---

*This document is reviewed quarterly. The next scheduled review is
July 2026.*
