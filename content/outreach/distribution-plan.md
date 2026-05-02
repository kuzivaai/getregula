# Distribution Plan — Regula v1.7.0

Generated: 2026-04-25
Status: Ready to execute

---

## Priority 1: Immediate (this week)

### 1a. Show HN post

**Title:** `Show HN: Regula -- Open-source CLI that scans code for EU AI Act risk patterns`

**Post body:**

```
I built Regula because I couldn't find a tool that reads your actual code and tells you which EU AI Act risk tier you're in. Every compliance tool I found was a questionnaire, a governance SaaS, or a policy layer. None of them looked at the source.

Regula is a static scanner. It reads Python, JS, TS, Java, Go, Rust, C, and C++. It checks against 389 risk patterns and tells you: prohibited, high-risk, limited-risk, or minimal. With the exact file, line, and legal basis for each finding.

What it does:
- `regula check .` — scan and classify risk tier
- `regula gap .` — article-by-article compliance gap assessment
- `regula conform .` — generate Annex IV evidence pack with SHA-256 integrity
- `regula oversight .` — trace AI outputs to check for human review gates

What it is not:
- Not legal advice. It identifies risk indicators for developer review.
- Not complete. It covers ~30% of the Act (the code-measurable part). The other ~70% is organisational.
- Not magic. 0 false positives at BLOCK tier. 15.2% precision at INFO tier on AI library source code (published benchmark: https://github.com/kuzivaai/getregula/blob/main/docs/benchmarks/PRECISION_RECALL_2026_04.md).

Zero dependencies (stdlib-only Python core). Fully offline. Apache 2.0.

Also maps to LGPD (Brazil), NIST AI RMF, ISO 42001, and 9 other frameworks.

https://github.com/kuzivaai/getregula
```

**First comment (post within 5 min):**

```
Hey HN — I'm the author. Happy to answer questions about the detection approach, false positive rates, or how the Act actually works in practice.

Some context: the EU AI Act sorts every AI system into a risk tier. The prohibited practices ban (Article 5) has been in force since Feb 2025. GPAI rules since Aug 2025. High-risk obligations start Aug 2026 (or Dec 2027 if the Omnibus delay passes trilogue — not yet law).

Most of the Act is organisational (risk management systems, quality management, fundamental rights impact assessments). You need a governance programme for that. Regula covers the code-measurable subset: does your code match the Annex III high-risk categories? Does it have logging? Does it implement human oversight gates? Is AI-generated content disclosed?

I documented everything Regula does NOT do here: https://github.com/kuzivaai/getregula/blob/main/docs/what-regula-does-not-do.md

Architecture: regex-based pattern matching + tree-sitter AST for Python/JS/TS. No LLM calls, no cloud dependency.
```

**When to post:** Tuesday-Thursday, 9-11 AM ET (14:00-16:00 UTC)

**Benchmark:** EuConform (closest comparable) got 71 points, 49 comments. Target: 50-100 points.

---

### 1b. Awesome list PRs (submit same week as Show HN)

| List | Stars | PR target section | Priority |
|------|-------|-------------------|----------|
| GenAI-Gurus/awesome-eu-ai-act | 33 | Open-Source Projects / Compliance Tools | HIGH — most relevant list |
| analysis-tools-dev/static-analysis | 14,508 | Python > Compliance | HIGH — massive audience |
| devsecops/awesome-devsecops | 5,381 | Compliance | HIGH |
| getprobo/awesome-compliance | 76 | Compliance Automation | MEDIUM |

**PR description template:**

```
## Regula — EU AI Act compliance scanner for code

- **Category:** Static analysis / Compliance
- **Language:** Python (scans Python, JS, TS, Java, Go, Rust, C, C++)
- **Licence:** Apache 2.0
- **What it does:** Scans source code for EU AI Act risk patterns. Classifies AI systems into risk tiers (prohibited, high-risk, limited-risk, minimal). Maps findings to 12 compliance frameworks including NIST AI RMF, ISO 42001, LGPD, and OWASP LLM Top 10.
- **Key differentiator:** Zero production dependencies (stdlib-only). Fully offline. 389 detection patterns. Evidence signing with SHA-256 + Ed25519.
- **Install:** `pipx install regula-ai`
- **Repo:** https://github.com/kuzivaai/getregula
```

---

### 1c. PyPI badge + download tracking

Add to README.md:
```markdown
[![PyPI Downloads](https://static.pepy.tech/badge/regula-ai)](https://pepy.tech/project/regula-ai)
```

Check current downloads:
```bash
pip install pypistats
pypistats recent regula-ai
pypistats overall regula-ai
```

---

## Priority 2: This month

### 2a. r/Python "I Made This" post

**Title:** `I built an open-source CLI that scans your code for EU AI Act risk patterns`

Follow the same content as Show HN but shorter. Lead with the problem, show the output, link to repo. Use "I Made This" flair.

**Rules:**
- Must have prior participation in r/Python (comment on 5-10 posts first)
- 90/10 rule: self-promotion should be <10% of activity
- Include a screenshot or terminal output GIF

### 2b. dev.to cross-posting

Cross-post "Questionnaires vs Code Scanning" article to dev.to with canonical URL pointing to getregula.com. Tags: `euaiact`, `compliance`, `python`, `security`.

Expected: 30-50 reactions, ~640 views. Low effort, free SEO backlink.

### 2c. LinkedIn founder posts (2-3/week)

Content types that work:
1. **Deadline countdown posts** — "High-risk obligations start Aug 2026. Here's what that means for your code."
2. **"What I learned" posts** — "I scanned 5 popular AI libraries for EU AI Act patterns. Here's what I found."
3. **Tool demo posts** — Short video/GIF of terminal output with explanation.

Post from personal account (2x higher CTR than company page).

---

## Priority 3: Next month

### 3a. Product Hunt launch

**Assessment: LOW priority.** CLI tools get 60-200 upvotes on PH. The prep effort (assets, hunter coordination, vote rally) outweighs the return vs HN. Defer until after HN results are in.

### 3b. awesome-python PR

**Requirement:** 100+ GitHub stars (currently at 1). Defer until stars grow from other distribution efforts.

### 3c. Conference talk submission

Look for CFPs:
- PyCon 2027 (CFP typically opens 6 months before)
- EuroPython 2027
- AI governance conferences (smaller, easier to get accepted)

---

## Channel performance tracking

| Metric | How to measure | Tool |
|--------|---------------|------|
| PyPI downloads | pypistats.org / pepy.tech | Weekly check |
| GitHub stars | GitHub repo page | Weekly check |
| Site traffic | Plausible dashboard | Weekly check |
| HN performance | news.ycombinator.com | Post-launch |
| Reddit engagement | Thread upvotes/comments | Post-launch |
| LinkedIn post performance | LinkedIn analytics | Per post |

---

## What NOT to do

- Don't post Reddit responses and Show HN on the same day — space them 3+ days apart
- Don't ask friends to upvote HN (against guidelines, gets flagged)
- Don't post more than once per subreddit per week
- Don't use marketing language anywhere — HN and Reddit will downvote
- Don't claim "only" or "first" without verification
- Don't post the same content to multiple platforms on the same day
