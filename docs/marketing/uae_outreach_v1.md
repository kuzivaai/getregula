# UAE outreach — cold message templates v1

> 50-message distribution test for the `/uae` landing page launch.
> Targets: DIFC, ADGM, Hub71, Dubai Internet City portfolio CTOs and
> heads of engineering at companies with **AI features in production**
> AND **EU customers**.
>
> Goal of the test: measure reply rate (target: ≥4% = 2 conversations
> from 50 messages) and book ≥1 30-min walk-through Zoom that becomes
> Phase 2's first POC report.
>
> **Do NOT mass-send.** Personalise each one. The templates below are
> starting points, not boilerplate.

---

## Targeting checklist

Before sending any message, verify the recipient meets all four:

- [ ] Company is licensed by DIFC, ADGM, Hub71, Dubai Internet City, or NEOM
- [ ] Company has at least one product surface that uses AI/ML (LLM call,
      classifier, ranker, or generative output) — verify via their docs
      or marketing site
- [ ] Company has EU customers, EU office, or markets in EU explicitly
      (check the footer / "where we operate" page)
- [ ] You are messaging an actual technical decision maker — CTO, head
      of engineering, head of platform, principal engineer with hiring
      authority. **Not** sales, marketing, or HR.

If any box is unchecked, skip the lead.

---

## LinkedIn DM template — fintech CTO

> Subject: 30-second EU AI Act check for your team
>
> Hi {Name} —
>
> Saw {Company}'s {specific feature, e.g. "credit-decisioning model"
> mentioned in your last product update / blog post / TechCrunch
> piece}. Quick heads-up that under EU AI Act Article 2(1)(c), if
> {Company} ships that model's outputs to EU customers, you're a
> "provider" — and from 2 August 2026, the rules in Articles 9–15
> apply regardless of where you're licensed.
>
> I built Regula — an open-source CLI that flags this in one command,
> against your actual codebase, locally. No SaaS, no consultants, no
> data leaves your machine. Free, MIT licence.
>
> Two minutes:
>
> ```
> pip install regula-ai && regula quickstart
> ```
>
> If you'd rather see it run live on a representative file, I'm happy
> to do a 20-min walk-through whenever suits — calendar:
> {your calendar link}
>
> The trust pack is at github.com/kuzivaai/getregula/blob/main/docs/TRUST.md
> if your security team wants to vet it before you run anything.
>
> — Kuziva

**Notes:**
- Lead with their specific product, not the tool.
- Cite the article number — UAE compliance teams already use this
  vocabulary from PDPL/GDPR work.
- Make the install command literally copy-pasteable in the message body.
- Offer the calendar link without pushing.
- Include the Trust Pack link unprompted to defuse the security objection.

---

## LinkedIn DM template — health-tech / clinical AI

> Hi {Name} —
>
> {Company}'s {clinical decision support / radiology classifier /
> diagnostic AI feature} caught my eye — congrats on {recent ADGM
> Hub71 graduation / funding round / regulatory milestone}.
>
> Article 6(1) of the EU AI Act cross-references Annex I Section A
> (medical devices under MDR 2017/745) — which means any AI component
> of your system that's CE-marked under MDR is automatically a
> "high-risk AI system" under the AI Act, and the Articles 9–15
> obligations stack on top of MDR. From 2 August 2026.
>
> Built Regula, an open-source CLI that audits the codebase locally
> in one command and tells you which Annex I/III categories you hit
> and which articles apply. Free, MIT, runs offline.
>
> ```
> pip install regula-ai && regula quickstart
> ```
>
> Happy to walk through what it surfaces against a representative
> module — 20 minutes. {calendar link}
>
> Trust pack: github.com/kuzivaai/getregula/blob/main/docs/TRUST.md
>
> — Kuziva

---

## LinkedIn DM template — HR-tech / recruitment SaaS

> Hi {Name} —
>
> {Company}'s {CV-screening / candidate-ranking / HR copilot} ships
> to EU customers, which puts it squarely in Annex III Category 4
> under the EU AI Act — employment and workers management is one of
> the eight high-risk areas, and the Articles 9–15 obligations apply
> from 2 August 2026 regardless of where you're licensed.
>
> Built Regula, an open-source CLI that scans the codebase in one
> command, locally, and flags exactly which functions trigger Cat 4
> (with line numbers) and which articles you need evidence against.
> Free, MIT, no data leaves your machine.
>
> ```
> pip install regula-ai && regula quickstart
> ```
>
> The motivating example I built it against is a literal `def
> classify_resume()` calling OpenAI — exact same shape as a lot of
> 2025-vintage HR-tech code. 20-min walk-through if it'd be useful.
> {calendar link}
>
> Trust pack: github.com/kuzivaai/getregula/blob/main/docs/TRUST.md
>
> — Kuziva

---

## Email template — fallback (when LinkedIn doesn't connect)

> Subject: EU AI Act exposure on {Company}'s {feature}
>
> {Name},
>
> Apologies for the cold email. I built an open-source tool called
> Regula that audits codebases for EU AI Act compliance, and your
> {feature} looked like an exact fit for one of the headline
> categories — {Annex III Cat X | Article 6(1) + Annex I}.
>
> Three things you should know if {Company} hasn't already done the
> work:
>
> 1. The Act applies extraterritorially. UAE licensing doesn't
>    matter; what matters is whether the model's output reaches EU
>    customers.
> 2. The provider carries the liability under Article 16, not the
>    distributor.
> 3. Fines are up to €35M or 7% of global turnover under Article 99.
>
> Regula is free, MIT-licensed, and runs locally — no SaaS, no
> account, no data exfiltration. Full source at
> github.com/kuzivaai/getregula. The Trust Pack
> (github.com/kuzivaai/getregula/blob/main/docs/TRUST.md) covers the
> security questions your team will ask.
>
> If you'd like a 20-min walk-through of what it surfaces against
> {Company}'s codebase, my calendar is at {link}.
>
> Best,
> Kuziva
> Maintainer, Regula

---

## What to track per send

Spreadsheet columns (one row per recipient):

| Column | Notes |
|---|---|
| Date sent | YYYY-MM-DD |
| Channel | LinkedIn / email |
| Recipient name | |
| Recipient role | CTO / Head of Eng / etc |
| Company | |
| License jurisdiction | DIFC / ADGM / Hub71 / Dubai Internet City / NEOM / other |
| Specific product/feature cited | |
| Reply (Y/N) | |
| Reply sentiment | Interested / Polite no / Auto / Hostile / No reply |
| Booked call (Y/N) | |
| Call date | |
| Outcome | POC scheduled / Not interested / Loop |

**Stop conditions for the test:**

- 50 sent → tally results, write up `docs/marketing/uae_outreach_v1_results.md`
- OR 5 calls booked → switch to call-fulfilment mode and pause sending

**What success looks like:**

- ≥2 replies (4% reply rate is the cold-DM baseline for this segment)
- ≥1 booked call
- ≥1 documented finding-against-real-code from a call → becomes the
  Phase 2 POC report

If reply rate < 2%, the targeting is wrong. Re-segment.
If reply rate ≥ 2% but no calls book, the message body is wrong.
Iterate the script before sending more.

---

## Things NOT to say in any message

- "We're the only..." — unverified competitive claim, banned by global
  CLAUDE.md research integrity rules
- "GDPR-style fines" — incorrect; the EU AI Act fines are higher and
  scoped differently. Use the actual numbers.
- "Compliant with the EU AI Act" — Regula does not make this claim and
  neither should the outreach. Compliance is a legal determination.
- "Replace your DPO / lawyer / consultancy" — Regula complements these
  roles, not replaces.
- Anything that promises specific dollar savings without a baseline.
  Quote ROI only after a real POC produces it.

---

## Compliance footnote

These templates do not collect personal data beyond what is publicly
listed on LinkedIn or company websites. Recipients can opt out of
follow-up by simply not replying. No automated scraping, no purchased
lists, no third-party enrichment beyond manual research. UAE PDPL and
EU GDPR apply to any reply that includes personal data — handle replies
with the same care as customer support.
