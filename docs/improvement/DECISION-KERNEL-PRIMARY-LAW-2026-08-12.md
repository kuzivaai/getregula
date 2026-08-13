# Decision kernel primary-law basis, 2026-08-12

## Status and method

This record is the Phase A4 basis for decision model `2026-08-12.4`. It is
not legal advice. Sources were retrieved on 2026-08-12. The canonical and
recipient-visible edges are enumerated by:

```text
python3 scripts/enumerate_decision_surface.py
```

That predicate reported 60 canonical regulatory edges, itemised as 26
indications and 34 obligations. The jurisdiction itemisation was Colorado 7,
EU 34, and Korea 19, and each subtotal reconciled with its list. The complete
machine-readable conditions, including every fact edge, are in
`references/decision_model.v1.json`. This document explains their basis and
records what remains unresolved.

Claim labels used below:

- **Demonstrated** means the official text was retrieved and read.
- **Interpreted** means the stated model condition is an implementation
  interpretation of that text. The assumption is named.
- **Unresolved** means the primary text delegates a necessary condition and
  the delegated instrument was not established here.

## Official sources

- [Regulation (EU) 2024/1689](https://eur-lex.europa.eu/eli/reg/2024/1689/oj)
- [Regulation (EU) 2026/1744, Digital Omnibus on AI](https://eur-lex.europa.eu/eli/reg/2026/1744/oj)
- [Korea Framework Act on AI, Act No. 20676](https://law.go.kr/lsInfoP.do?lsiSeq=268543&urlMode=engLsInfoR&viewCls=engLsInfoR)
- [Colorado SB26-189 signed act](https://leg.colorado.gov/bill_files/116489/download)
- [Colorado General Assembly bill record](https://leg.colorado.gov/bills/SB26-189)

## European Union

### Scope and high-risk classification

**Demonstrated.** Article 2 establishes territorial and operator scope and
Article 3(1) defines an AI system. Article 6(1), as amended, requires a product
or safety component covered by Annex I and a third-party conformity assessment
for the product. New Article 6(1a) to (1c) narrows the safety-component and
third-party-assessment conditions. Article 6(2) applies Annex III. Article
6(3) excludes listed narrow uses from high-risk classification unless profiling
is performed, while Article 6(2) and Annex III still require the listed intended
purpose. Model rules `eu_high_risk_annex_i_section_a`,
`eu_high_risk_annex_i_section_b_limited`, and `eu_high_risk_annex_iii` encode
those necessary conditions.

**Demonstrated.** Amended Article 2(2) says that for Article 6(1) systems tied
to Annex I Section B products, only Article 6(1), Article 60a, and Articles 102
to 112 apply, subject to its further sentence. The Section B rule can therefore
produce a high-risk candidate indication but is deliberately absent from every
Article 9 to 17 and Article 26 obligation edge.

**Interpreted.** `eu_significant_risk` represents the Article 6(3) material-
influence/significant-risk limb as one sourced fact. This assumes a competent
reviewer can attest the combined legal conclusion. Splitting health, safety,
fundamental-rights, and material-influence subfacts would produce a more
granular trace and would overturn this design if reviewers cannot source the
combined fact reliably.

### Article 5 prohibitions

**Demonstrated.** Model rules `eu_prohibited_5_1_a` through
`eu_prohibited_5_1_h` reproduce the necessary conjunctive conditions and the
express exceptions in Article 5(1)(a) to (h): manipulative or deceptive
techniques plus distorted decision and significant harm; vulnerability plus
those effects; social evaluation plus the specified detriment; criminal-risk
prediction based solely on profiling or personality traits; untargeted facial-
image scraping; workplace or education emotion inference without the medical
or safety purpose; sensitive biometric categorisation without the listed
filtering or law-enforcement exception; and real-time remote biometric
identification for law enforcement without a fully authorised exception.

**Demonstrated.** Regulation 2026/1744 inserts Article 5(1)(ba), 5(1)(bb),
5(1a), and 5(1b). Rules `eu_prohibited_5_1_ba` and
`eu_prohibited_5_1_bb` separately encode identifiable non-consensual intimate
material and child sexual abuse material, the provider intended-purpose or
reasonably-foreseeable-use limb, the deployer purpose limb, explicit consent,
and the without-right defence. They carry the amended application date of
2026-12-02 rather than the base Act date.

### High-risk operator duties

**Demonstrated.** Articles 9 to 15 are system requirements. Article 16(a)
requires a provider to ensure that its high-risk system complies with Section
2, and Article 17 separately requires a provider quality-management system.
Article 26 assigns deployers their own duties. Consequently, model version
`2026-08-12.3`, which attached Articles 9 to 15 without resolving the operator
role, was falsified and replaced.

**Interpreted.** Obligation edges `eu_requirement_9` through
`eu_requirement_15` require both a resolved Annex I Section A or Annex III
high-risk rule and `role_provider=yes`; `eu_provider_qms_17` has the same
provider condition. Deployer edges attach Article 26(1) to (2), Article 26(5),
and Article 26(12) only when the same high-risk predicate and
`role_deployer=yes` resolve. The model does not yet encode Article 25 role
conversion. A distributor, importer, deployer, or third party that becomes the
provider under Article 25 must currently be represented by a sourced
`role_provider=yes` value. A dedicated Article 25 predicate would be required
if the product must derive that role rather than accept it as a fact.

**Demonstrated.** Regulation 2026/1744 changes the detailed text of Articles
10 and 11 and changes Article 113. Chapter III Sections 1 to 3 apply from
2027-12-02 for Article 6(2)/Annex III systems and 2028-08-02 for Article
6(1)/Annex I systems. The model stores those dates per matched rule and emits
them as `applicable_from`; it does not describe a future date as present
readiness.

### Article 50 transparency

**Demonstrated.** Article 50(1) covers provider interaction disclosure, subject
to obviousness and the authorised criminal-law exception. Article 50(2) covers
provider machine-readable marking of synthetic output, subject to the standard
editing and authorised criminal-law exceptions. Article 50(3) covers deployer
notice for emotion recognition or biometric categorisation. Article 50(4)
covers deployer disclosure for deep fakes and public-interest text, with a
human-review/editorial-responsibility exception for the text limb. Rules and
obligations `eu_transparency_*`, `eu_notice_50_*`, `eu_marking_50_2`, and
`eu_disclosure_50_4_*` reproduce those conditions.

**Unresolved.** `eu_artistic_or_fictional_work` is defined but is not on an
applicability edge. Article 50(4) still requires disclosure for artistic,
creative, satirical, fictional, or analogous work, but changes how and where it
may be displayed. The current tagged result cannot express a conditional
performance variant within one obligation. A sub-obligation or obligation-
variant field would settle this. Until then the fact is not used to remove the
duty and the output does not prescribe the manner of disclosure.

**Demonstrated.** The Article 50 duties apply from 2026-08-02. Amended Article
111(4) separately gives providers of synthetic-content systems placed on the
market before that date until 2026-12-02 for Article 50(2). The model records
that transition as a note because the placement date is not yet a modeled fact.

## Republic of Korea

### Scope and definitions

**Demonstrated.** Article 2 defines AI, an AI system, high-impact AI,
generative AI, AI developers, and AI-using business operators. Article 4
extends the Act to foreign conduct affecting the domestic market or users and
excludes defence or national-security AI prescribed by Presidential Decree.
The common scope facts and `kr_ai_business_operator` represent these gates.

### Articles 31 to 36

**Demonstrated.** Article 31(1) requires advance AI-operation notice for a
product or service using high-impact or generative AI. Article 31(2) requires
generative-output labelling. Article 31(3) requires recognisable notice or
labelling for realistic virtual sound, image, or video and permits a less
disruptive manner for artistic or creative work. Rules
`kr_transparency_high_impact`, `kr_transparency_generative`, and
`kr_transparency_virtual_media`, with obligations `kr_notice_31_1`,
`kr_label_31_2`, and `kr_label_31_3`, encode those applicability conditions.

**Demonstrated.** Article 32 applies only when cumulative training computation
meets a Presidential-Decree threshold. It then requires lifecycle risk
identification, assessment and mitigation, a safety-incident risk-management
system, and submission of implementation results. Rule `kr_high_compute` and
obligations `kr_safety_32_1` and `kr_submit_32_2` require an explicit sourced
threshold result.

**Demonstrated.** Article 33(1) requires an AI business operator providing AI
or an AI product or service to review high-impact status in advance. The
request to the Minister is optional. Rule `kr_advance_review` and obligation
`kr_review_33` therefore do not require the system actually to be high-impact.

**Demonstrated.** Article 34(1) applies when an operator provides high-impact
AI or a product or service using it. Its five modeled measures are risk
management, an explanation plan, user protection, human management and
oversight, and retained verification documents. Rule `kr_high_impact` requires
both a listed or decree-prescribed area and likely significant impact or risk
to life, physical safety, or fundamental rights. Obligations
`kr_risk_management_34` through `kr_records_34` attach only through that rule.

**Demonstrated.** Article 36 requires an operator without a Korean address or
office to designate and report a Korean agent only when the decree-prescribed
user, sales, or other scale threshold is met. Rule `kr_domestic_agent` and
obligation `kr_agent_36` require both facts.

**Unresolved.** This research did not establish the numeric Article 32 compute
threshold, the Article 36 user/sales threshold, the Article 4 defence
exclusion detail, or the detailed Article 31 method and exceptions from the
Presidential Decree and ministerial notices. The kernel does not fabricate
them. A dated official English or Korean decree and applicable public notices
would settle each value. Until then a user must supply a sourced yes, no,
unknown, or not-applicable fact, and unknown cannot produce the affected duty.

## Colorado

**Demonstrated.** The signed SB26-189 repeals and reenacts Part 17 for covered
automated decision-making technology. Section 6-1-1701 defines covered ADMT
through personal-data processing, computational output, material influence on
a consequential decision, the listed consequential domains, and detailed
technology and entity/activity exclusions. Rule `co_covered_admt` represents
those necessary conditions. `co_excluded_technology` and
`co_other_law_exemption` are separate because statutory exclusion and
conditional compliance with another law are different evidence claims.

**Demonstrated.** Section 6-1-1702 requires developer information and update
disclosures for covered ADMT and, in subsection (4), developer record
retention. `co_developer_docs_1702` and `co_developer_records_1702_4` require
covered ADMT and `role_provider=yes`. Section 6-1-1703 requires deployer record
retention; `co_deployer_records_1703` requires covered ADMT and
`role_deployer=yes`.

**Demonstrated.** Section 6-1-1704 requires deployer notices concerning the
use of covered ADMT in consequential decisions and additional disclosures
after an adverse outcome. `co_notice_1704` requires the covered-ADMT and
deployer predicates; `co_adverse_disclosure_1704` additionally requires
`co_adverse_outcome=yes`. Section 6-1-1705 gives a consumer experiencing such
an adverse outcome correction instructions and, to the extent commercially
reasonable, meaningful human review and reconsideration.
`co_consumer_rights_1705` requires the same adverse-outcome edge.

**Demonstrated.** The Colorado General Assembly bill record identifies the
signed act and its effective date. The model records 2027-01-01 as the default
application date. Outputs expose that date rather than describing a future
duty as current readiness.

**Interpreted.** The model combines the Act's numerous enumerated exclusions
into two sourced booleans. This is reversible and fail-closed, but it places the
burden of correctly resolving the list on the evidence provider. Separate
named predicates for each exclusion would be required if legal reviewers find
that a combined attestation is not auditable enough.

## Design conclusions and rejected alternatives

**Demonstrated.** Necessary legal conditions can be represented by nested
`all`, `any`, fact, and named-rule expressions for the currently emitted
classification and obligation edges. No procedural escape hatch was needed.
The artistic-disclosure manner variant and Article 25 role conversion are
limitations, not hidden procedural code.

**Interpreted.** One JSON model can serve Python and browser runtimes because
the browser model is generated locally by a stdlib-only script and scan-time
execution has no network or build dependency. Hand-copying locale engines was
rejected because it cannot make semantic equality executable.

The model deliberately does not convert code-detector matches into legal
facts, average contradictory values, treat absence as no, or attach an
obligation from an unresolved edge. Those alternatives recreate the defect
this kernel exists to close.
