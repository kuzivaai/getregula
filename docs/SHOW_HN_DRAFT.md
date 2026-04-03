# Show HN Draft

## Title (pick one)

**Option A:** Show HN: Regula — free CLI that checks if your AI code is high-risk under the EU AI Act

**Option B:** Show HN: I built a free CLI to check EU AI Act compliance from your codebase

**Option C:** Show HN: Regula — scan your AI project for EU AI Act risk in 10 seconds

---

## Post body

Regula is an open-source CLI that scans your codebase for EU AI Act risk indicators. It tells you which risk tier you're in (prohibited, high-risk, limited-risk, or minimal), points to the exact line of code that triggered the classification, and estimates the compliance effort per article.

I built it because the EU AI Act takes effect in August 2026 (high-risk Annex III obligations), and most teams building AI haven't checked where they stand. Enterprise compliance platforms cost $50K+/year. Lawyers cost $500/hour. I wanted something a developer could run in 10 seconds for free.

What it does:

- `regula check .` — classifies your project against 53 risk pattern groups across 4 tiers
- `regula gap .` — scores you on Articles 9-15 (risk management, logging, human oversight, etc.)
- `regula docs .` — generates Annex IV technical documentation from your actual code
- `regula plan .` — prioritised remediation tasks with effort estimates
- `regula evidence-pack .` — bundles everything for an auditor

It's Python, zero dependencies for core features, MIT licensed. Supports Python, JS, TS, Java, Go, Rust, C, C++. Cross-maps to 11 frameworks including ISO 42001, NIST AI RMF, OWASP LLM Top 10, and the EU Cyber Resilience Act.

What it doesn't do: it doesn't catch general security vulnerabilities (use Semgrep/Bandit for that), it doesn't assess code quality, and it doesn't make you compliant. Findings are indicators for human review, not legal determinations.

GitHub: https://github.com/kuzivaai/getregula
PyPI: pip install regula-ai

Happy to answer questions about the EU AI Act, the detection approach, or the false positive rate. The built-in self-test covers 6 fixture cases (prohibited, high-risk, limited-risk, mixed-tier, compliant, and warn-tier) and passes on every install. On self-scan (137 findings on our own codebase, which discusses AI patterns without being an AI system), raw false-positive rate is high without filters — but with the default filters (skip-tests, min-tier, regula-ignore), all false positives are suppressed. The honest answer is: precision depends heavily on your codebase and filter settings. We'd welcome real-world data if you run it.

---

## Predictable questions + prepared answers

### "How is this different from Semgrep?"

Semgrep is a general static analysis tool — you write custom rules for security bugs, code patterns, etc. Regula is specifically for EU AI Act risk classification. It maps your code to the regulation's risk tiers, articles, and annexes. Semgrep could do some of this if you wrote the rules, but Regula ships with 49 named detection patterns pre-mapped to specific EU AI Act articles and generates the compliance documentation the law requires.

### "What about false positives?"

It depends on the codebase. On code that clearly implements AI features (chatbots, screening tools, recommendation engines), precision is high — our 6 built-in fixture cases all classify correctly. On code that *discusses* AI patterns without implementing them (like our own scanner codebase), raw false-positive rate is high because regex patterns match keywords in comments, variable names, and documentation. The default filters handle this: `--skip-tests` removes test file noise, `--min-tier limited_risk` filters low-confidence findings, and `# regula-ignore` suppresses known false positives. With defaults on, our own codebase shows 0 false positives. We use comment stripping, confidence scoring (0-100), and context penalties for test/example files. It's designed to over-report rather than miss something — you can always suppress, but you can't unsee a missed prohibited practice.

### "Why not just read the regulation?"

You should. Regula doesn't replace understanding the law — it surfaces the parts of the law that are relevant to your specific codebase. The EU AI Act is 144 pages. Annex III alone has 8 high-risk categories. Most developers don't know which articles apply to them until they've read the whole thing. Regula does that triage.

### "Is this useful for non-Python projects?"

Yes. It scans Python, JavaScript, TypeScript, Java, Go, Rust, C, and C++. Python gets the deepest analysis (AST-level data flow tracing), while other languages use tree-sitter AST parsing (JS/TS) or regex-based pattern matching.

### "What about the Digital Omnibus / deadline extension?"

The European Parliament voted 569-45 in March 2026 to potentially push high-risk Annex III obligations from August 2026 to December 2027. It still needs trilogue agreement. Either way, the requirements don't change — only the enforcement date. Starting now means you're ahead rather than scrambling.

### "This looks like it could generate a lot of noise on real codebases"

It can. Use `--skip-tests` to exclude test files (removes the majority of findings on codebases that discuss AI patterns in tests) and `--min-tier high_risk` to focus on actionable items. 

---

## Posting checklist

- [ ] PyPI package published and working
- [ ] Landing page live at getregula.com
- [ ] Post when you can commit to answering comments for several hours (morning ET on weekdays is commonly cited but 2025 data shows weekends may perform better for Show HN)
- [ ] Link to GitHub repo, not landing page (HN prefers repos)
- [ ] No superlatives in title (no "fastest", "best", "first")
- [ ] Ready to acknowledge limitations honestly when asked — especially the precision numbers

## Distribution channels (ranked by audience fit)

### Phase 1: Launch week (developer-focused)
- [ ] **Show HN** — primary launch. Link to GitHub repo.
- [ ] **DEV.to article** — "I scanned 5 open-source AI projects for EU AI Act compliance." Show real output.
- [ ] **awesome-claude-code** — submit PR to list Regula (has Claude Code hooks)
- [ ] **MCP server directories** — list the Regula MCP server where Claude/Cursor users discover tools

### Phase 2: Compliance ecosystem (where your actual audience is)
- [ ] **artificialintelligenceact.eu** — the main EU AI Act community hub (400K+ visitors). Explore getting listed or contributing content.
- [ ] **IAPP** (International Association of Privacy Professionals) — their AI Act compliance matrix is the reference for DPOs. Contribute or get listed.
- [ ] **European DIGITAL SME Alliance** — targets SMEs with AI Act tools. They maintain a directory.
- [ ] **AI Act Service Desk** (EC official) — EU's own support channel highlights tools for startups/SMEs.
- [ ] **LinkedIn** — short posts about what the law requires + "here's a free tool." Target DPO and CTO audience.

### Phase 3: Developer communities (be a member first)
- [ ] **r/python, r/programming, r/artificial** — participate in relevant threads first. Reddit's 80/20 rule: 80% genuine participation, 20% self-promotion. Frame as results, not marketing.
- [ ] **Product Hunt** — second wave after HN. Good for broader visibility.
