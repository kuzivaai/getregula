---
title: "August 2026 or December 2027? A Developer's Guide to the Omnibus Uncertainty"
published: false
description: "The EU AI Act has two possible deadlines for high-risk AI systems. A three-track framework for developers who need to plan now despite the uncertainty."
tags: euaiact, compliance, ai, opensource
canonical_url: https://getregula.com/blog/blog-omnibus-decision-framework.html
cover_image: https://getregula.com/assets/og-image.png
---

Two dates. One regulation. Nobody knows which deadline applies. Here is a three-track framework for planning your EU AI Act compliance work when the timeline itself is unstable.

## The situation

If you're building AI systems that touch the European market, you have a planning problem. The EU AI Act says your high-risk obligations kick in on 2 August 2026. The Digital Omnibus on AI says actually, make that 2 December 2027. Both statements are currently true, in the sense that the first is law and the second is a formal legislative proposal with strong institutional backing.

On 26 March 2026, the European Parliament voted 569-45-23 in favour of its negotiating position on the Omnibus. The Council had already adopted its general approach on 13 March. Trilogue negotiations between Parliament, Council, and Commission launched the same day as the EP vote. The Cypriot Council Presidency has set 28 April 2026 as its target date for political agreement, though that may slip into May.

So the delay has overwhelming political support. But it isn't law yet. And until the trilogue produces agreed text that passes formal adoption, the current legal baseline remains 2 August 2026.

This leaves developers in a genuinely annoying position. You can't plan around a deadline that might move by 16 months. But you also can't ignore the strong signal that it will move. I think the right approach is to stop treating the EU AI Act as one deadline and start treating it as three separate tracks, each on its own timeline, with different levels of certainty.

## Three tracks, not one deadline

The EU AI Act doesn't have a single compliance date. It phases in over several years, and the Omnibus only proposes changes to some of those phases. Treating it as a single event leads to either panic (August is soon) or complacency (they're pushing it back, we can relax). Neither is correct.

### Track 1: Prohibited practices (Article 5)

**Deadline: 2 February 2025. Already in force. Not affected by the Omnibus.**

The prohibitions on social scoring, subliminal manipulation, real-time remote biometric identification in public spaces, and emotion inference in workplaces and educational institutions have been enforceable since February 2025. Fines for violations go up to EUR 35 million or 7% of global annual turnover, whichever is higher.

If your code does any of these things, the Omnibus is irrelevant to you. You're already in scope. The fact that people are talking about deadline delays elsewhere in the Act doesn't change this.

### Track 2: Transparency obligations (Article 50)

**Deadline: 2 August 2026. Not delayed by the Omnibus.**

Article 50 covers the transparency requirements most developers will hit first: disclosing that a user is interacting with an AI system (chatbot disclosure), labelling AI-generated or manipulated content (deepfake labelling), and marking synthetic text published to inform the public on matters of public interest.

The Omnibus doesn't propose to defer these obligations. If anything, the Parliament's negotiating position strengthens them. You have until August 2026 to get your disclosure and labelling mechanisms in place. That timeline is stable.

### Track 3: High-risk system obligations (Annex III)

**Current law: 2 August 2026. Omnibus proposal: 2 December 2027. Not yet agreed.**

This is where the uncertainty lives. If your system falls under Annex III (standalone high-risk AI systems used in areas like employment, creditworthiness, law enforcement, migration, or access to essential services), the Omnibus proposes to push your deadline back by 16 months.

If your system is covered by Annex I (AI embedded in products regulated under Union harmonisation legislation, such as medical devices, machinery, or vehicles), the proposed delay is even longer: to 2 August 2028, a full 24 months.

## What the Omnibus actually changes

Most coverage collapses everything into "the deadline is delayed" without distinguishing what is delayed from what isn't. The detail matters.

| Obligation | Current law | Omnibus proposal | Status |
|---|---|---|---|
| Article 5 prohibitions | 2 Feb 2025 | No change | In force |
| GPAI obligations (Articles 53-55) | 2 Aug 2025 | No change | In force |
| Article 50 transparency | 2 Aug 2026 | No change | Unchanged |
| GPAI with systemic risk (Article 55) | 2 Aug 2025 | No change | In force |
| High-risk: standalone (Annex III) | 2 Aug 2026 | 2 Dec 2027 | Proposed (+16 months) |
| High-risk: product-embedded (Annex I) | 2 Aug 2026 | 2 Aug 2028 | Proposed (+24 months) |

The Omnibus also changes regulatory sandbox provisions and adjusts the Article 6(3) procedural-task carve-out, but those are less relevant to the planning question most developers face. The short version: GPAI and transparency obligations stay exactly where they are. Only the high-risk application dates for Annex III and Annex I systems move.

## The engineering argument for planning to August

I think you should plan as if August 2026 is the deadline, even though it almost certainly won't be. That sounds contradictory, but it isn't.

The high-risk obligations under Articles 9 through 15 aren't checkbox items you knock out in a sprint. They require:

- **Risk management systems** (Article 9) that are iterative, documented, and updated throughout the system lifecycle. You need to identify risks, estimate them, adopt mitigation measures, and test those measures. This isn't a document you write once.
- **Data governance** (Article 10) covering training, validation, and testing datasets. You need documented practices for data collection, preparation, labelling, and bias examination. If you don't already have this infrastructure, building it takes months, not weeks.
- **Technical documentation** (Article 11) that describes how the system was designed, developed, and validated. The level of detail required goes well beyond a README file.
- **Automatic logging** (Article 12) with traceable records of system operation for the entire period it is in use. This means audit logging that is tamper-resistant, time-stamped, and retained.
- **Human oversight mechanisms** (Article 14) that allow a natural person to understand the system's outputs, intervene, and override. This is an interface design problem as much as a backend one.
- **Accuracy, robustness, and cybersecurity** (Article 15) with documented performance metrics and resilience measures.

Each of these takes real engineering time. Not because the requirements are unreasonable, but because most teams haven't been building these capabilities in from the start. You're retrofitting governance into systems that were built for speed.

Two scenarios:

**Scenario A:** You start now, the Omnibus passes, and the deadline moves to December 2027. You're 16 months early. Your compliance work is done, you've had time to iterate on it, and you're ahead of competitors who waited. The cost was starting earlier than strictly necessary.

**Scenario B:** You wait for the Omnibus to become law, it stalls in trilogue (this happens), and the deadline stays at August 2026. You now have three months to implement a risk management system, overhaul your logging infrastructure, write technical documentation, build human oversight interfaces, and pass conformity assessment. You won't make it.

The downside of Scenario A is being early. The downside of Scenario B is non-compliance with a regulation that carries fines of up to EUR 15 million or 3% of global annual turnover.

This is an asymmetric bet. Being early costs you nothing beyond the engineering time, and that time isn't wasted even if you didn't need it yet.

## The work is not wasted anyway

The requirements in Articles 9 through 15 aren't unique to the EU AI Act either. They overlap substantially with frameworks your organisation may already be pursuing:

- **NIST AI RMF** maps directly to the risk management, documentation, and testing requirements. Build for the EU AI Act and you're most of the way to NIST AI RMF compliance.
- **ISO 42001** (AI management systems) covers governance structures, risk assessment, and documentation requirements that run parallel to Articles 9 and 11.
- **SOC 2** audit criteria for security, availability, and processing integrity overlap with Article 15's accuracy and cybersecurity requirements.
- **NIST CSF** and **ISO 27001** cover the cybersecurity baseline that Article 15 expects.

This isn't a coincidence. AI governance frameworks converge because they're all trying to answer the same question: can you demonstrate that your system is reliable, documented, and auditable? The specific article numbers change. The underlying engineering work doesn't.

Building logging infrastructure, documentation pipelines, risk assessment processes, and human oversight interfaces pays off regardless of which deadline applies, which regulation you're targeting, or whether the Omnibus passes at all.

## What to do right now

1. **Find out which track you're on.** Run `regula check .` in your project root. It scans your codebase against 389 risk patterns and tells you whether you fall into prohibited, high-risk, limited-risk, or minimal-risk territory. If you're not high-risk, the Omnibus delay is irrelevant to you. Your obligations are either already in force (Track 1) or on a fixed August 2026 timeline (Track 2).

2. **If you're high-risk, start documenting now.** The single highest-value thing you can do today is start writing your Article 11 technical documentation and your Article 9 risk management plan. These are the most time-consuming requirements, and they only get harder to write the longer you wait, because institutional knowledge about design decisions fades. Start now while the people who made those decisions are still around.

3. **Get your logging in order.** Article 12 requires automatic logging that records system operation throughout its lifecycle. If your current logging is ad-hoc application logs, you need to build audit-grade logging infrastructure. This is backend work that takes time to design, implement, and validate. Run `regula gaps .` to see where your logging falls short of what Articles 12 and 15 expect.

4. **Check your framework crosswalks.** Run `regula crosswalk . --framework nist-ai-rmf` to see how your EU AI Act compliance gaps map to NIST AI RMF. If you're already working towards NIST or ISO 42001, you may have less to do than you think. If you're starting from scratch, the crosswalk helps you prioritise work that satisfies multiple frameworks at once.

```bash
pipx install regula-ai && regula check .
```

## The bottom line

The Omnibus will very likely pass. The political support is there: 569 votes in favour, 45 against, 23 abstentions. Both Council and Parliament have their mandates. The trilogue is under way.

But "very likely" is a prediction about politics, not a fact about law. Even if the delay does become law, it only affects Track 3: the Annex III and Annex I high-risk obligations. Everything else stays on its current schedule.

Plan for August. Treat December 2027 as buffer, not as a new start date. The work you do now isn't wasted regardless of which date the trilogue lands on. And if you start in the second half of 2027 because the delay gave you permission to procrastinate, you'll be in exactly the position that the compliance industry makes its money from: rushed, expensive, and cutting corners.

Start now. Go at a sustainable pace. If the deadline moves, you're early. That's fine.

**Not legal advice.** Regula identifies regulatory risk indicators in code for developer review. It does not constitute legal advice, and its output should not be relied upon as a definitive compliance determination. Consult a qualified legal professional for legal questions. Regulatory dates cited in this article are sourced from official EU institutional publications.

---

*Originally published at [getregula.com](https://getregula.com/blog/blog-omnibus-decision-framework.html)*
