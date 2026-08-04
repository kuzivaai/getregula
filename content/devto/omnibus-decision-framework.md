---
title: "The EU AI Act after Regulation (EU) 2026/1744: the dates developers need"
published: true
description: "The enacted EU AI Act timeline after Regulation (EU) 2026/1744, including Article 5, Article 50 and the two Article 6 high-risk paths."
tags: euaiact, compliance, ai, opensource
canonical_url: https://getregula.com/blog/blog-omnibus-decision-framework.html
cover_image: https://getregula.com/assets/og-image.png
---

The timing uncertainty discussed in the original version of this article is over. Regulation (EU) 2026/1744 was published in the Official Journal on 24 July 2026 and entered into force on 27 July 2026. It amended Regulation (EU) 2024/1689; it did more than move deadlines.

Primary texts: [Regulation (EU) 2024/1689](https://eur-lex.europa.eu/eli/reg/2024/1689/oj) and [Regulation (EU) 2026/1744](https://eur-lex.europa.eu/eli/reg/2026/1744/oj).

## The enacted timeline

| Provision or path | Application date | Qualification |
|---|---:|---|
| Original Article 5 prohibitions | 2 February 2025 | Each prohibition has its own conditions and exceptions. |
| New Article 5(1)(ba) and (bb) | 2 December 2026 | Added by Regulation (EU) 2026/1744, with conditions in Article 5(1a) and (1b). |
| Most Article 50 transparency duties | 2 August 2026 | Scope differs by paragraph. |
| Pre-existing Article 50(2) systems | 2 December 2026 | Specific transition for systems placed on the market before 2 August 2026. |
| Annex III high-risk path under Article 6(2) | 2 December 2027 | Classification still requires the full Article 6 test. |
| Annex I product-safety path under Article 6(1) | 2 August 2028 | Both conditions in Article 6(1) must be met. |

These dates come from the enacted amendments to Article 113. A date alone does not establish that a system is prohibited, high-risk, or subject to a particular transparency duty.

## Article 5: do not classify from a code match

The original Article 5 prohibitions have applied since 2 February 2025. Regulation (EU) 2026/1744 adds prohibitions concerning non-consensual intimate content and child sexual abuse material, applicable from 2 December 2026. The amended text also adds intended-purpose, reasonably foreseeable use, provider-safeguard and deployer-use conditions, plus a stated exclusion for specified law-enforcement manipulation of non-consensual intimate content. Read the complete provision before reaching a legal conclusion.

Article 99 permits administrative fines of up to EUR 35 million or, for undertakings, up to 7% of total worldwide annual turnover for the preceding financial year for non-compliance with Article 5, subject to the Regulation's detailed rules. That maximum is not a prediction of the sanction in an individual case.

## Article 50: generally live, with a specific transition

Article 50 includes different duties for providers and deployers. It addresses, among other things, certain direct interactions with natural persons, synthetic content, emotion-recognition or biometric-categorisation systems, deepfakes, and AI-generated or manipulated public-interest text. The paragraph, role, exceptions and context matter.

Regulation (EU) 2026/1744 did not generally defer Article 50. It gives providers of systems covered by Article 50(2) that were already on the market before 2 August 2026 until 2 December 2026 to comply.

## Article 6: two high-risk paths

The Annex III route under Article 6(2) applies from 2 December 2027. The Annex I route under Article 6(1) applies from 2 August 2028. Annex membership or a library name alone is insufficient: Article 6 contains the legal tests, and Article 6(3) contains conditions relevant to some Annex III systems.

Regulation (EU) 2026/1744 also amended provisions beyond the dates, including definitions, prohibited practices, high-risk classification and documentation, conformity assessment, post-market monitoring, sandboxes, governance, penalties and transition rules. Describing it as only a deadline delay is incomplete.

## What engineering teams can do now

1. Inventory systems, roles, intended purposes and deployment contexts.
2. Treat static scanner output as review indicators, not legal classification.
3. Map evidence to the provision that may apply, including its conditions and exceptions.
4. Record uncertainty and obtain qualified legal review where the legal outcome matters.
5. Build reusable risk-management, data-governance, logging, documentation and human-oversight evidence where applicable. Cross-framework mappings can identify related controls, but they do not make standards or laws equivalent.

`regula check .` identifies code patterns for review. It cannot determine intended purpose, reasonably foreseeable misuse, organisational role, jurisdiction, exceptions or the complete facts required for a legal classification.

```bash
pipx install regula-ai
regula check .
```

**Not legal advice.** Regula's output is evidence for human review, not a definitive compliance determination.

---

*Originally published at [getregula.com](https://getregula.com/blog/blog-omnibus-decision-framework.html). This copy was updated on 4 August 2026 to replace the pre-enactment version.*
