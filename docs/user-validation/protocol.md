# User Validation Protocol — Regula v2.0

## Purpose

Validate that `regula check . --explain` (Prompt 1) actually helps SME founders understand their EU AI Act risk classification before investing further in documentation features (Prompt 2) or website copy (Prompt 3).

**Note:** Prompts 2 and 3 were built before this validation ran. Results here may trigger rework on those features.

## Target: 5 users

### Selection criteria

- Building an AI product (not just using ChatGPT internally)
- Fewer than 50 employees
- Selling or planning to sell in the EU
- Willing to run a CLI tool on their codebase
- Has Python 3.10+ installed

### Where to find them

| Channel | Search / approach |
|---------|-------------------|
| Hacker News | "Ask HN" threads about EU AI Act, AI regulation |
| r/startups, r/SaaS, r/MachineLearning | Threads about EU compliance, AI Act |
| Indie Hackers | EU-based AI founders |
| X/Twitter | "EU AI Act" + "startup" or "compliance" or "high-risk" |
| LinkedIn | Founders at EU AI startups, filter <50 employees |
| AI meetups (Berlin, Amsterdam, London) | In-person or virtual |

### Outreach message

> I built a free, open-source EU AI Act scanner. Looking for 5 founders to test it on their actual codebases. Takes 10 minutes. I'll share what I find — no strings attached.
>
> It tells you which risk tier your code falls under, why (with the specific line and legal basis), and what obligations apply — including effort estimates.
>
> pip install regula-ai && regula check . --explain
>
> Interested? [reply / DM / link]

### Disqualify if

- Not building AI (using off-the-shelf SaaS doesn't count)
- Enterprise (>50 people) — different needs, different product
- Not EU-facing (US-only companies aren't the target)
- Won't run CLI (web-only users need a different product)

---

## Test protocol

### Before running Regula (2 minutes)

Ask these questions. Record answers verbatim.

1. "What does your AI product do, in one sentence?"
2. "What risk tier do you think your AI system falls under?" (prohibited / high-risk / limited-risk / minimal-risk / don't know)
3. "How confident are you in that assessment?" (1-10)
4. "What's your biggest uncertainty about EU AI Act compliance?"
5. "Have you used any other compliance tool?" (which one / none)

### Run Regula (3 minutes)

The user runs on their own machine:

```bash
pip install regula-ai
regula check . --explain
```

If they're uncomfortable running on production code, a staging branch or test project works. What matters is real AI code, not toy examples.

Capture: screenshot or copy-paste of the full output.

### After running Regula (5 minutes)

Ask these questions. Record answers verbatim.

1. "Did the classification match your expectation?" (yes / no / partially)
2. "Did the explanation help you understand WHY you got that classification?" (yes / no / partially)
3. "Is the false positive guidance useful? Could you tell if an indicator was wrong?"
4. "Is the obligation roadmap actionable? Could you start working from it?"
5. "What's the most useful thing in the output?"
6. "What's missing that would make this useful for your day-to-day?"
7. "Would you run this again?" (yes / no / maybe)
8. "Would you recommend this to another founder?" (yes / no / maybe)
9. "If this had a paid tier, what would make it worth paying for?"

---

## Success criteria

### Prompt 1 is VALIDATED if

- 4/5 users say the explanation helped them understand their classification
- 3/5 users say the roadmap is actionable (they could start working from it)
- 0/5 users say the output made them MORE confused than before

### Prompt 1 NEEDS ITERATION if

- Users don't understand the legal basis citations (e.g., "Annex III" means nothing to them)
- Users can't tell whether an indicator is a false positive
- Users don't know what to do next after seeing the output
- The provider/deployer distinction confuses rather than clarifies

### Prompt 2 REWORK triggers

- If users say "I don't need documentation help, I need X" — rethink Prompt 2
- If users say the Annex IV scaffolds are too technical — simplify the templates
- If users want runtime/monitoring features — that's out of scope, document it as a finding

---

## After each test

Record results in `user-N.md` using the template below. Do not summarise — preserve verbatim quotes.

After all 5 tests, write `synthesis.md` with:
- Patterns across users
- Go/no-go decision on Prompt 2
- Specific iteration needed on Prompt 1
- Unexpected findings
