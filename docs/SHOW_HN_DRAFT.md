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

- `regula check .` — classifies your project against 130 risk patterns across 4 tiers
- `regula gap .` — scores you on Articles 9-15 (risk management, logging, human oversight, etc.)
- `regula docs .` — generates Annex IV technical documentation from your actual code
- `regula plan .` — prioritised remediation tasks with effort estimates
- `regula evidence-pack .` — bundles everything for an auditor

It's Python, zero dependencies for core features, MIT licensed. Supports Python, JS, TS, Java, Go, Rust, C, C++. Cross-maps to 11 frameworks including ISO 42001, NIST AI RMF, OWASP LLM Top 10, and the EU Cyber Resilience Act.

What it doesn't do: it doesn't catch general security vulnerabilities (use Semgrep/Bandit for that), it doesn't assess code quality, and it doesn't make you compliant. Findings are indicators for human review, not legal determinations.

GitHub: https://github.com/kuzivaai/getregula
PyPI: pip install regula-ai

Happy to answer questions about the EU AI Act, the detection approach, or the false positive rate (~67% precision on our benchmark corpus).

---

## Predictable questions + prepared answers

### "How is this different from Semgrep?"

Semgrep is a general static analysis tool — you write custom rules for security bugs, code patterns, etc. Regula is specifically for EU AI Act risk classification. It maps your code to the regulation's risk tiers, articles, and annexes. Semgrep could do some of this if you wrote the rules, but Regula ships with 130 patterns pre-mapped to specific EU AI Act articles and generates the compliance documentation the law requires.

### "What about false positives?"

We benchmarked on a labelled corpus and measured ~67% precision — meaning about 1 in 3 findings is a false positive. The main source is pattern matching without full semantic context (e.g., a comment mentioning "credit scoring" triggers the same as actual credit scoring code). We mitigate this with confidence scoring (0-100), context penalties for test/example files, and regula-ignore inline suppression. It's better to flag something for human review than to miss a prohibited practice.

### "Why not just read the regulation?"

You should. Regula doesn't replace understanding the law — it surfaces the parts of the law that are relevant to your specific codebase. The EU AI Act is 144 pages. Annex III alone has 8 high-risk categories. Most developers don't know which articles apply to them until they've read the whole thing. Regula does that triage.

### "Is this useful for non-Python projects?"

Yes. It scans Python, JavaScript, TypeScript, Java, Go, Rust, C, and C++. Python gets the deepest analysis (AST-level data flow tracing), while other languages use tree-sitter AST parsing (JS/TS) or regex-based pattern matching.

### "What about the Digital Omnibus / deadline extension?"

The European Parliament voted 569-45 in March 2026 to potentially push high-risk Annex III obligations from August 2026 to December 2027. It still needs trilogue agreement. Either way, the requirements don't change — only the enforcement date. Starting now means you're ahead rather than scrambling.

### "This looks like it could generate a lot of noise on real codebases"

It can. Use `--skip-tests` to exclude test files (removes ~27% of findings) and `--min-tier high_risk` to focus on actionable items. On a 20K-star LangChain fork, this reduced 2,108 raw findings to 19 actionable ones.

---

## Posting checklist

- [ ] PyPI package published and working
- [ ] Landing page live at getregula.com
- [ ] Post Tuesday-Thursday, 8-10am ET (peak HN engagement per Markepear)
- [ ] Be online for 6+ hours after posting to answer comments
- [ ] Link to GitHub repo, not landing page (HN prefers repos)
- [ ] No superlatives in title (no "fastest", "best", "first")
- [ ] Ready to acknowledge limitations honestly when asked
