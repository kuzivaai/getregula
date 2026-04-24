---
title: "Questionnaires tell you what you said. Code scanning shows what you did."
published: false
description: "Questionnaires and code scanning cover different halves of the EU AI Act. Neither replaces the other. Together, they produce something closer to defensible compliance."
tags: euaiact, compliance, ai, devtools
canonical_url: https://getregula.com/blog/blog-code-scanning-vs-questionnaires.html
cover_image: https://getregula.com/assets/og-image.png
---

Browse any EU AI Act thread on Reddit and you will find the same split. Someone asks how to comply. Half the replies say hire a law firm. The other half recommend a governance platform: Holistic AI, Difinity, Airia, ClearAI Register. Every tool mentioned is a questionnaire, a risk register, or a policy layer.

Across nine Reddit threads I reviewed in April 2026, not one user mentioned scanning their source code. That absence is interesting, but the conclusion people tend to draw from it is wrong. The answer is not that code scanning should replace questionnaires. The answer is that questionnaires alone leave a gap, and code scanning fills a specific part of it.

## What questionnaires do well

A questionnaire captures organisational information that no scanner can reach. Does your company have a risk management system (Article 9)? A quality management system (Article 17)? A fundamental rights impact assessment process (Article 27)? A post-market monitoring plan (Article 72)?

These are human obligations. They exist in meeting rooms, policy documents, and governance structures. A regex cannot attend a board meeting. A static analyser cannot verify that your AI risk committee met last quarter. For these obligations, a structured questionnaire filled out by the responsible person in your organisation is not just acceptable. It is the correct tool.

No serious compliance programme can skip this layer. The EU AI Act is roughly 70% organisational and 30% technical. If you only scan code, you are ignoring the majority of what the regulation requires.

## What questionnaires cannot do

Questionnaire answers are self-reported. When your compliance lead ticks "yes" next to "does your AI system implement appropriate logging?", an auditor has to trust their word. There is no mechanism inside the questionnaire to verify whether that answer reflects what the code actually does.

This is not a hypothetical problem. Code changes continuously. A developer adds a face detection pipeline in March. Another integrates a resume screening model in June. A third refactors the logging module and removes the audit trail the compliance team was relying on. None of these changes trigger a questionnaire update, because questionnaires are not wired into the development workflow.

The Sopact/Sprinto research on continuous compliance monitoring puts it plainly: annual questionnaires create snapshots that miss drift between assessments. The system you assessed in January is not the system running in production in October.

u/TumbleweedPuzzled293 on Reddit described the classification burden: "the classification system is what kills most small teams." That burden gets worse when classification is a point-in-time exercise. If the only record of your risk tier is a form someone filled out six months ago, you are carrying compliance debt that compounds with every merge.

## What code scanning adds

A code scanner reads your actual source files. It does not ask you what your system does. It looks and reports.

For the technical subset of the EU AI Act, this produces evidence that questionnaires structurally cannot:

**Risk classification from code, not from memory.** When someone asks "are we high-risk?", the answer should not depend on whether the compliance lead remembers what shipped last quarter. A scanner that detects Annex III category patterns in the codebase answers the classification question from evidence, not recollection. u/stairflyer noted the confusion directly: "for now unless your AI could be considered high risk I'd recommend not stressing too much." The problem is that many teams genuinely do not know whether their system is high-risk, because nobody has checked the code against the categories.

**Continuous verification, not periodic review.** Run the scanner in CI/CD. Every pull request gets checked. If someone introduces a prohibited practice (Article 5) or a high-risk pattern (Annex III), it surfaces in the PR review, not in next year's audit cycle.

**Specific, actionable findings.** Not "your system may have transparency issues" but "`src/chatbot/handler.py`, line 47: AI-generated content served to users without disclosure. Article 50 requires marking." A developer can fix that. They cannot fix "please ensure your AI systems comply with transparency requirements."

**Evidence tied to commits.** A questionnaire answer is a claim. A scan result tied to a specific git commit is evidence. When an auditor asks how you know your system does not do social scoring, there is a difference between "our compliance lead said so" and "here is a scan of commit `a3f7b2c` showing zero Article 5 matches."

## What code scanning cannot do

Static analysis addresses roughly 30% of the EU AI Act. That is not a pessimistic estimate. It is a structural reality. We have documented the boundary in detail: see [what Regula does not do](https://github.com/kuzivaai/getregula/blob/main/docs/what-regula-does-not-do.md).

Article 9 requires a risk management system. A set of processes, approvals, and reviews that happen inside an organisation. Not a code artefact.

Article 17 requires a quality management system. Same logic, larger scope.

Article 27 requires a fundamental rights impact assessment. A structured document produced with input from affected persons.

Article 72 requires post-market monitoring. Ongoing observation of a deployed system that no pre-deployment scan can substitute.

No amount of pattern matching will verify that your organisation holds quarterly AI risk review meetings, that your board has approved an AI policy, or that affected communities were consulted. A scanner that claims to handle these obligations is lying about its coverage.

u/amrit_za raised a related point: compliance tools that "adds a lot of admin and paperwork which incentivises us to own fewer models." The criticism lands hardest against tools that overstate what they cover. If a vendor implies a scan result equals compliance, they are creating false confidence. A scan result is evidence for the parts of the regulation that have a code footprint. The rest still requires human work.

## The combination

The useful framing is not scanners versus questionnaires. It is scanners as the evidence layer that makes some questionnaire answers provable.

When your questionnaire asks "does your AI system implement appropriate logging?" and you answer "yes", that answer is a claim. When you attach a scan result showing logging calls detected around model invocations in 14 files, with file paths and line numbers, the claim becomes verifiable.

When the questionnaire asks "have you assessed your system for prohibited practices?" and you answer "yes", that is a checkbox. When you attach a scan showing zero Article 5 pattern matches across the entire codebase, signed against a specific commit, that is evidence backing the checkbox.

The questionnaire captures what your organisation says it does. The scan shows what the code actually does. Together, the two layers are stronger than either one alone. The questionnaire without the scan is unverified. The scan without the questionnaire is incomplete.

## The gap that still exists

u/balirUK observed that "GDPR was a paper tiger." The implication was that regulations without enforcement teeth get treated as box-ticking exercises. Whether the AI Act follows the same trajectory remains to be seen, but the tooling pattern is familiar: most of what exists today produces paperwork, not evidence.

This is not because questionnaire vendors are doing something wrong. They are building the right tool for the organisational layer. The gap is at the code layer. Almost nobody is building tools that read the source code and check whether it matches the claims in the policy documents.

For a defensible AI Act compliance programme, you need both layers. The organisational layer captures obligations that exist above the codebase: policies, processes, governance structures, legal review, monitoring. The code layer captures what the system actually does: risk patterns, security surfaces, oversight gaps, transparency obligations.

Neither layer alone is compliance. But a governance programme built entirely on self-reported answers is a programme that cannot prove its own claims. When market surveillance authorities start checking, "we filled out the form" is going to be a weaker answer than "here is the form, and here is the code evidence that backs it up."

---

*[Regula](https://github.com/kuzivaai/getregula) is an open-source CLI that scans codebases for EU AI Act risk patterns. It covers the code layer of compliance, which is roughly 30% of the regulation. For everything it does not cover, see [what Regula does not do](https://github.com/kuzivaai/getregula/blob/main/docs/what-regula-does-not-do.md).*
