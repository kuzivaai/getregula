# Regula venture source register

Research cut-off: 2026-08-04 23:59 Europe/London

Retrieval date: 2026-08-05


Live vendor pages retrieved after the cut-off establish only a current vendor
claim unless a dated release or help page fixes the state by the cut-off.

## Repository and product evidence

| ID | Source | Date/version | Class and use | Limit |
|---|---|---|---|---|
| R01 | `README.md`, `SECURITY.md`, `docs/TRUST.md`, `docs/MODEL_CARD.md`, `docs/architecture.md` | checkout `6ac32de`, tree `8cd9697` | `REPOSITORY_MEASURED`: product boundary, architecture, security and language depth | Later than frozen commercial product commit; internal evidence only |
| R02 | `data/site_facts.json` and `python3 scripts/cascade_count.py --check` | generated 2026-08-04 | `REPOSITORY_MEASURED`: 62 commands, 419 tier regexes, 722 broad patterns, 13 frameworks, 8 language families, 2,690 collected tests | Counts use different definitions and do not show efficacy |
| R03 | `benchmarks/commercial_v1/results/summary.json` and raw score | frozen product `140bdac`; protocol commit `f77473d`; session 2026-07-31 | `REPRODUCED`: A/B local 0/40; baselines 40/40; zero labelled repositories; STOP | Constructed correlated transformations; version-bound; no external accuracy |
| R04 | `docs/commercial/COMMERCIAL_DEFENSIBILITY_REVIEW_2026-07-31.md` | 2026-07-31, erratum 2026-08-01 | Current controlling commercial verdict fields | Internal decision record, not external validation |
| R05 | `docs/commercial/PILOT_PACKET_2026-07-31.md` | 2026-07-31 | Prior validation design and price anchors | No engagement or payment occurred |
| R06 | `site/pricing.html` | checkout `6ac32de` | Paid tiers marked coming soon; no payment accepted | Public claim, not demand evidence |

## Customer, buyer and market sources

| ID | Source | Publication/effective date | Class and decision use | Limit |
|---|---|---|---|---|
| M01 | [Bank of England and FCA, Artificial intelligence in UK financial services 2024](https://www.bankofengland.co.uk/report/2024/artificial-intelligence-in-uk-financial-services-2024) | 2024-11-21 | `PRIMARY_SOURCE_VERIFIED`: 75% of 118 respondents used AI; one third of use cases third-party; 64% third-party in risk/compliance; incomplete understanding linked to third parties | Anonymised self-report; no supplier cost, rejection or payment data |
| M02 | [PRA SS1/23, Model risk management principles](https://www.bankofengland.co.uk/prudential-regulation/publication/2023/may/model-risk-management-principles-for-banks-ss) | current version published/effective 2026-04-23 | `PRIMARY_SOURCE_VERIFIED`: applies to external/vendor models; governance, validation and monitoring remain with firm | Scope is specified PRA firms, not every financial buyer |
| M03 | [PRA SS2/21, Outsourcing and third-party risk](https://www.bankofengland.co.uk/prudential-regulation/publication/2021/march/outsourcing-and-third-party-risk-management-ss) | applicable version 2024-11-15, effective 2024-12-31 | `PRIMARY_SOURCE_VERIFIED`: due diligence, written agreements, security, audit, continuity and exit workflow | Proportionate; not AI-specific and not every purchase is material |
| M04 | [PRA CP17/24](https://www.bankofengland.co.uk/prudential-regulation/publication/2024/december/operational-incident-and-outsourcing-and-third-party-reporting-consultation-paper) | 2024-12 | `PRIMARY_SOURCE_VERIFIED`: inconsistent third-party records and potential omission of material AI models | Consultation at cut-off; not final rule or supplier demand evidence |
| M05 | [Commission Delegated Regulation (EU) 2024/1773](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1773) | adopted 2024-03-13; applicable 2025-01-17 | `PRIMARY_SOURCE_VERIFIED`: DORA due diligence evidence for qualifying critical/important ICT services | Applicability depends on entity, geography and service; not AI-specific |
| M06 | [EBA DORA register preparation](https://www.eba.europa.eu/activities/direct-supervision-and-oversight/digital-operational-resilience-act/preparation-dora-application) | applicable 2025-01-17 | `PRIMARY_SOURCE_VERIFIED`: comprehensive contractual-arrangement registers | Buyer obligation, not supplier willingness to pay |
| M07 | [PRA Business Plan 2026/27](https://www.bankofengland.co.uk/prudential-regulation/publication/2026/april/pra-business-plan-2026-27) | 2026-04 | `PRIMARY_SOURCE_VERIFIED`: 568 supervised insurers at January 2026, used only as TAM-like ceiling | Includes unsuitable firm types; not an ICP count |
| M08 | [UK Guidelines for AI procurement](https://www.gov.uk/government/publications/guidelines-for-ai-procurement/guidelines-for-ai-procurement) | 2020-06-08 | `PRIMARY_SOURCE_VERIFIED`: lifecycle evidence, multidisciplinary evaluation, supplier communication | Old and public-sector-specific |
| M09 | [Responsible AI in Recruitment](https://www.gov.uk/government/publications/responsible-ai-in-recruitment-guide/responsible-ai-in-recruitment) | 2024-03-25 | `PRIMARY_SOURCE_VERIFIED`: concrete supplier evidence questions and bias-audit example | Recruitment guidance, not insurer practice |
| M10 | [EU AI model contractual clauses](https://public-buyers-community.ec.europa.eu/communities/procurement-ai/resources/updated-eu-ai-model-contractual-clauses) | updated after AI Act adoption, available before cut-off | `PRIMARY_SOURCE_VERIFIED`: full/light buyer clauses and commentary | Public procurement, voluntary/customisable; not a full contract |
| M11 | [UK AI sector study 2024](https://www.gov.uk/government/publications/artificial-intelligence-sector-study-2024/artificial-intelligence-sector-study-2024) | 2025-09-03, data for 2024 | `PRIMARY_SOURCE_VERIFIED`: 5,862 UK AI firms; 95% SMEs | TAM-like ceiling; does not identify enterprise-selling suppliers or demand |
| M12 | [DSIT, Assuring a Responsible Future for AI](https://www.gov.uk/government/publications/assuring-a-responsible-future-for-ai/assuring-a-responsible-future-for-ai) | 2024 research, available before cut-off | `PRIMARY_SOURCE_VERIFIED`: 524 assurance suppliers, 84 specialised; 1,347-leader survey; barriers include demand understanding, model access and interoperability | Government-commissioned estimates and projections do not validate Regula revenue |
| M13 | [CSA AI Controls Matrix v1.1](https://cloudsecurityalliance.org/artifacts/ai-controls-matrix-v1-1) | released 2026-06-22 | `PRIMARY_SOURCE_VERIFIED`: 247 controls and AI-CAIQ mapping | Framework existence, not buyer adoption or Regula demand |
| M14 | [CSA CAIQ v4.1](https://cloudsecurityalliance.org/artifacts/star-level-1-security-questionnaire-caiq-v4-1) | 2026 | `PRIMARY_SOURCE_VERIFIED`: reusable standard cloud questionnaire substitute | Cloud controls are not complete AI assurance |
| M15 | [Shared Assessments SIG](https://sharedassessments.org/about-sig/) and [pricing](https://sharedassessments.org/sig/) | live pages by cut-off; exact update unresolved | `VENDOR_CLAIMED`: repeatable supplier questionnaire and $7,000 corporate licence | Adoption/exchange counts and cut-off page state not reproduced |
| M16 | [HN security-questionnaire discussion](https://news.ycombinator.com/item?id=25793230) | 2021-01-14 | `USER_REPORTED`: redundancy and disproportionate burden on smaller contracts | Anecdotal; not AI or insurer-specific |
| M17 | [HN Stacksi launch discussion](https://news.ycombinator.com/item?id=26513040) | 2021-03-18 | `USER_REPORTED`: repeated questionnaires across formats require expert input | Vendor launch bias |
| M18 | [Reddit enterprise questionnaire thread](https://www.reddit.com/r/SaaS/comments/1ux1jwa/founders_who_sell_to_enterprise_how_are_you/) | 2026-07 | `USER_REPORTED`: answer libraries need owner, date, source and reuse boundaries | Small thread; may be vendor-seeded; no payment proof |
| M19 | [G2 Conveyor reviews](https://www.g2.com/products/conveyor-conveyor/reviews) | reviews through cut-off | `USER_REPORTED`: time saving alongside correction/customisation complaints | Aggregator and invited-review bias; no independent efficacy |

## Competitors and substitutes

| ID | Source | Cut-off treatment | Class and use |
|---|---|---|---|
| C01 | [ValidMind documentation overview](https://docs.validmind.com/about/overview.html) | dated 2026-07-14 | `OFFICIALLY_DOCUMENTED`: financial model-risk validation, documentation, SaaS/on-prem/customer-managed |
| C02 | [Credo AI](https://www.credo.ai/product) | undated live page; exact cut-off state unresolved | `VENDOR_CLAIMED`: enterprise inventory, policy, workflow, monitoring and integrations |
| C03 | [Saidot](https://www.saidot.ai/product) | undated live page | `VENDOR_CLAIMED`: graph inventory, evidence reuse, approvals and integrations |
| C04 | [ModelOp inventory](https://www.modelop.com/ai-governance-software/inventory) | undated live page | `VENDOR_CLAIMED`: enterprise AI system of record and lifecycle evidence |
| C05 | [Monitaur platform](https://www.monitaur.ai/platform) | undated live page | `VENDOR_CLAIMED`: insurer focus, policy-to-proof, vendor governance and services |
| C06 | [Holistic AI](https://www.holisticai.com/) | live page; dated Azure release 2024-09-25 | `VENDOR_CLAIMED`: discovery, testing, runtime control and evidence; performance claims unverified |
| C07 | [ServiceNow AI Control Tower](https://www.servicenow.com/uk/products/ai-control-tower.html) | live page; 2026 docs exist | `OFFICIALLY_DOCUMENTED`: installed workflow/CMDB distribution; documented cloud-transfer boundary |
| C08 | [Vanta pricing](https://www.vanta.com/pricing) and [Trust Center help](https://help.vanta.com/en/articles/11345469-vanta-trust-center) | help dated 2026-05-18 | `OFFICIALLY_DOCUMENTED`: evidence, trust centre and questionnaire allowances; money not public |
| C09 | [Drata questionnaire automation](https://drata.com/products/assurance/security-questionnaire-automation) | live page | `VENDOR_CLAIMED`: approved-source answers and approval workflow |
| C10 | [Conveyor pricing](https://www.conveyor.com/pricing) and [questionnaire product](https://www.conveyor.com/products/security-questionnaire-automation) | public by cut-off | `OFFICIALLY_DOCUMENTED`: Business from $9,600/year; workflow. Accuracy/time claims remain `VENDOR_CLAIMED` |
| C11 | [Whistic pricing](https://www.whistic.com/pricing) | live page | `VENDOR_CLAIMED`: buyer and supplier exchange/catalog model; quote pricing |
| C12 | [AIR Blackbox](https://airblackbox.ai/) | available by cut-off | `OFFICIALLY_DOCUMENTED`: open-source local scanner/flight recorder/AI-BOM, no certification guarantee |
| C13 | [Armilla Verified in government portfolio](https://www.gov.uk/ai-assurance-techniques/armilla-verified-third-party-ai-product-verification) | 2023 | `PRIMARY_SOURCE_VERIFIED` listing of an assurance technique, not government certification |

## Technology, standards and regulation

| ID | Source | Date/version | Class and venture effect |
|---|---|---|---|
| T01 | [SPDX specification 3.0.1](https://spdx.dev/wp-content/uploads/sites/31/2024/12/SPDX-3.0.1-1.pdf) | 3.0.1 | `PRIMARY_SOURCE_VERIFIED`: AI and dataset profiles make portable component provenance an interoperability option, not a moat |
| T02 | [W3C Verifiable Credentials Data Model 2.0](https://www.w3.org/standards/history/vc-data-model-2.0/) | Recommendation 2025-05-15 | `PRIMARY_SOURCE_VERIFIED`: issuer-holder-verifier claims and data minimisation; ecosystem trust/adoption still required |
| T03 | [IETF SCITT working group](https://datatracker.ietf.org/group/scitt/) | architecture in RFC Editor queue; APIs under IESG in 2026 | `PRIMARY_SOURCE_VERIFIED`: promising transparency receipts but not a mature Regula distribution advantage |
| T04 | [OMG SACM 2.3](https://www.omg.org/spec/SACM) | 2.3, 2023-10 | `PRIMARY_SOURCE_VERIFIED`: standard assurance claim/evidence/counterclaim structure |
| T05 | [NIST AI Agent Standards Initiative](https://www.nist.gov/artificial-intelligence/ai-agent-standards-initiative) | created 2026-02-17; updated 2026-04-20 | `PRIMARY_SOURCE_VERIFIED`: agent identity/security/interoperability is emerging; deliverables remain developing |
| T06 | [MCP authorization specification](https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization) | 2025-11-25 | `PRIMARY_SOURCE_VERIFIED`: optional HTTP authorization based on OAuth-related standards; not full agent governance |
| T07 | [Commission Article 50 guidelines](https://digital-strategy.ec.europa.eu/en/library/guidelines-transparency-obligations-providers-and-deployers-ai-systems) | published 2026-07-20; applies 2026-08-02 | `PRIMARY_SOURCE_VERIFIED`: marking, interaction and deployer disclosure scope |
| T08 | [Article 50 Code of Practice](https://digital-strategy.ec.europa.eu/en/policies/code-practice-ai-generated-content) | final published 2026-06-10 | `PRIMARY_SOURCE_VERIFIED`: voluntary marking/labelling implementation route |
| T09 | [Commission technical marking studies](https://digital-strategy.ec.europa.eu/en/library/three-studies-technical-solutions-mark-and-detect-ai-generated-content) | 2026-05-08 | `PRIMARY_SOURCE_VERIFIED`: modality-specific limitations make a generic code-only pack weak |
| T10 | [NIST AI 800-5 agent-security RFI analysis](https://www.nist.gov/publications/summary-analysis-responses-request-information-regarding-security-considerations-ai) | 2026-05-18 | `PRIMARY_SOURCE_VERIFIED` report of respondent consensus that agent security is an adoption barrier; RFI evidence, not measured market demand |
| T11 | [CycloneDX v1.7 specification](https://cyclonedx.org/specification/overview/) | 1.7, released 2025-10-21 | `PRIMARY_SOURCE_VERIFIED`: attestations and AI/ML component representation; useful only where a recipient consumes the format |
| T12 | [SLSA specification](https://slsa.dev/spec/) and [in-toto specification](https://github.com/in-toto/docs/blob/v1.0/in-toto-spec.md) | versioned official specifications available by cut-off | `PRIMARY_SOURCE_VERIFIED`: build provenance and supply-chain integrity; do not establish truth of governance claims |
| T13 | [Sigstore documentation](https://docs.sigstore.dev/) and [DSSE protocol](https://github.com/secure-systems-lab/dsse/blob/master/protocol.md) | official documentation available by cut-off | `PRIMARY_SOURCE_VERIFIED`: signing envelopes and identity-linked verification; integrity and attribution are not evidence accuracy |
| T14 | [NIST OSCAL](https://pages.nist.gov/OSCAL/) | 1.1.3 current by cut-off | `PRIMARY_SOURCE_VERIFIED`: machine-readable control, assessment and plan models; adoption by a named buyer is unresolved |
| T15 | [W3C PROV-O](https://www.w3.org/TR/prov-o/) and [SHACL](https://www.w3.org/TR/shacl/) | W3C Recommendations | `PRIMARY_SOURCE_VERIFIED`: provenance and graph validation primitives; implementation choices, not product differentiation |
| T16 | [OpenTelemetry generative AI semantic conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/) | development status at cut-off | `PRIMARY_SOURCE_VERIFIED`: emerging telemetry vocabulary; stability and buyer use must not be assumed |
| T17 | [C2PA technical specification](https://spec.c2pa.org/specifications/specifications/2.2/specs/C2PA_Specification.html) | 2.2 | `PRIMARY_SOURCE_VERIFIED`: content provenance assertions and manifests; does not by itself satisfy every Article 50 duty or prove content truth |
| T18 | [OPA documentation](https://www.openpolicyagent.org/docs/latest/) and [Cedar specification](https://docs.cedarpolicy.com/) | official documentation available by cut-off | `PRIMARY_SOURCE_VERIFIED`: policy evaluation and authorisation mechanisms; require a valid policy and runtime integration |
| T19 | [OpenLineage specification](https://openlineage.io/docs/spec/) | official specification available by cut-off | `PRIMARY_SOURCE_VERIFIED`: job, run and dataset lineage events; not an AI assurance verdict |

## Theory used because it changes the decision

| ID | Source | Mechanism and decision effect | Where analogy breaks |
|---|---|---|---|
| H01 | [Williamson, transaction-cost approach](https://doi.org/10.1086/227496) | Repeated uncertain, expert-dependent transactions should first be governed through a service/hybrid; automate only stable repeated elements | Does not establish that this specific transaction is budgeted |
| H02 | Akerlof, *The Market for Lemons*, 1970 | Self-asserted supplier quality is easy for poor suppliers to imitate; independent evidence and reviewer acceptance matter more than report generation | Enterprise procurement has contracts, reputation and audits that partly mitigate asymmetry |
| H03 | Spence, *Job Market Signaling*, 1973 | A signal is useful when buyers recognise it and imitation is costly; Regula-generated self-attestation is not automatically credible | Education signalling is not supplier assurance; buyer recognition must be tested |
| H04 | [OMG SACM 2.3](https://www.omg.org/spec/SACM) | Explicit claims, evidence, counterclaims and inference make uncertainty reviewable; choose an assurance-case structure over a compliance score | A structure does not make evidence true or accepted |

## Founder and immigration rules

| ID | Source | Date | Class and use |
|---|---|---|---|
| F01 | [Immigration Rules Appendix Innovator Founder](https://www.gov.uk/guidance/immigration-rules/immigration-rules-appendix-innovator-founder) | updated 2026-07-01 | `PRIMARY_SOURCE_VERIFIED_RULE`: significant contribution to plan, day-to-day role, sole founder or instrumental founding-team member, endorsed innovative/viable/scalable venture |
| F02 | [Innovator Founder overview](https://www.gov.uk/innovator-founder-visa) | live at cut-off | `PRIMARY_SOURCE_VERIFIED_RULE`: endorsement and new/innovative/viable/scalable description |
| F03 | [Authorised endorsing bodies](https://www.gov.uk/government/publications/endorsing-bodies-innovator-founder-and-scale-up-visas/innovator-founder-and-scale-up-visas-endorsing-bodies) | updated 2026-04-20 | `PRIMARY_SOURCE_VERIFIED_RULE`: only listed bodies can issue new endorsements; official fees |
