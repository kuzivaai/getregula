---
title: "Agentic AI appears once in EU law. It is a filing code."
published: false
description: "Regulation (EU) 2026/1744 mentions agentic AI exactly once, in a table that tells notified bodies what they are competent to assess. No definition, no risk tier, no obligation."
tags: euaiact, agenticai, compliance, ai
canonical_url: https://getregula.com/blog/blog-agentic-ai-annex-xiv.html
cover_image: https://getregula.com/assets/og-image.png
---

<!--
DRAFT. Held for owner approval before publication (DIRECTIVE-v3 section 2b).
Every quotation below was taken from a full-text retrieval of
eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=OJ:L_202601744 on
29 July 2026, HTTP 200. Re-verify before shipping: Annex XIV is amendable
by delegated act, so this article has a shelf life by design.
-->

The Digital Omnibus on AI, Regulation (EU) 2026/1744, entered into force on 27 July 2026. Within days, "agentic AI is now regulated in the EU" began circulating.

The term does appear in the regulation. It appears exactly once. It is worth knowing where, because the location determines what it means.

## Where it actually appears

Regulation (EU) 2026/1744 inserts Annex XIV into the AI Act. Annex XIV is a list of codes used to describe what a conformity assessment body is qualified to assess. It has three categories: AIP codes for AI in products covered by other Union product legislation, AIB codes for the biometric systems in Annex III, and AIH codes, which are horizontal and describe the underlying technology.

There are eight AIH codes. The last one reads:

> AI systems based on other emerging AI technologies not covered by other codes, including Agentic AI

That is Annex XIV, Section 3, point (d). Code AIH 0401. Search the [full text of Regulation (EU) 2026/1744](https://eur-lex.europa.eu/eli/reg/2026/1744/oj/eng) for "agentic" and this is the single hit.

The code immediately above it matters too, because the two are defined against each other:

> AI systems that learn from their environment, excluding AI systems covered under AIH 0401

That is AIH 0205. Reinforcement-learning-style systems sit there, and whatever falls under AIH 0401 is carved out of it.

## What the codes are for

Recital 43 says why the list exists. The codes scope the designation of notified bodies, so that those bodies "are fully competent in regard to the AI systems they are required to assess".

That is the whole function. When a conformity assessment body applies to be designated, the codes describe what it is qualified to handle. A body competent in image processing is not automatically competent in agentic systems. The list is how a regulator writes that distinction down.

## What does not follow

No obligation attaches to AIH 0401.

There is no article defining an AI agent. There is no risk tier keyed to autonomy. There is no duty that scales with how many steps a system takes without a human in the loop. Nothing in the operative text treats an agentic system differently from any other system in the same risk category. If your agent performs a task listed in Annex III, it is high risk because of the task, exactly as it was before this regulation, and on the same timetable.

A filing code is not a legal definition. It tells you which assessor is qualified to look at your system. It does not tell you what your system must do.

## Why the summaries disagree

Two widely read explainers describe AIH 0401 differently. One reports it as the agentic AI code. The other reports it as the code for other emerging technologies.

Both are reading the same line, and each has half of it. The label is a residual category, "other emerging AI technologies not covered by other codes", with agentic AI named as an example inside it. Reading only the first half makes it sound like the EU has created an agentic AI category. Reading only the second half loses the fact that the word appears in binding law at all.

The practical consequence of the first reading is the more expensive one. Nobody should be scoping a compliance programme around a category that does not carry duties.

## What would change this

This analysis has an expiry date built into the regulation itself.

Article 1(16) of Regulation (EU) 2026/1744 amends Article 30(2) of the AI Act so that notification is scoped by reference to Annex XIV. Recital 45 delegates power to the Commission to amend the annex. AIH 0401 is therefore precisely where agentic obligations would first attach, if they ever do.

Two things would reopen the question:

1. A delegated act amending Annex XIV.
2. Guidance from the AI Office or the Commission that references AIH 0401 or attaches substantive requirements to it.

Neither has happened. Until one does, the honest statement is the narrow one: European law now has a filing code that names agentic AI, and that is all it has.

## Checking this yourself

The regulation is free to read. Open the Official Journal text of Regulation (EU) 2026/1744, search for "agentic", and count the hits. One result, in a table about assessor competence, is the entire basis for every claim above.

That is a five-minute check, and it is worth more than any summary, including this one.
