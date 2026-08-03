# Blog scan data — "I scanned 10 open-source AI apps for EU AI Act compliance"

Regula v1.7.0 scan output for the 10 projects analysed in
[the blog post](https://getregula.com/blog/blog-scanning-10-ai-apps.html).

Scanned: 23 April 2026 against shallow clones of each project's default branch.

## Reproduce

```bash
pipx install regula-ai
git clone --depth 1 https://github.com/<owner>/<repo>.git
regula check <repo> --format json > <repo>.json
```

## Results summary (v1.7.0, 23 April 2026)

| Project | Findings |
|---|---|
| LiteLLM | 397 |
| ChatGPT-on-WeChat | 105 |
| gptme | 86 |
| Khoj | 23 |
| Kirara AI | 17 |
| LangBot | 14 |
| Local Deep Research | 13 |
| Claude Engineer | 5 |
| Aider | 4 |
| Open Computer Use | 1 |
| **Total** | **665** |

The original blog post reports 553 findings using Regula v1.6.1 (10 April 2026).
The difference is primarily due to expanded AI security detection patterns in v1.7.0
(387 tier regexes vs 330 in v1.6.1).

> **CORRECTED 28 July 2026.** This said **409** and the blog post said
> **389**. Neither is derivable. MEASURED: 387 tier regexes, counted at commit c6aa67a (23 April 2026, VERSION 1.7.0, the tree the scan actually ran) by two independent methods: that tree's own scripts/site_facts.py, and a direct sum over risk_patterns.py. Every pattern unit
> available at that tree is 52 / 387 / 182 / 17 / 38 / 10 / 4 / 4 / 18 /
> 660 / 447 — **neither 389 nor 409 appears under any unit**, so this was
> not a units mismatch, it was two wrong numbers. The v1.7.0 tag
> (16 April) gives 386; the 23 April tree gives 387. The `409` that
> appears in the v1.7.0 tree is a false match inside `arXiv:2409.11363`.
>
> **Still open:** the **330** figure for v1.6.1 is not settleable from a
> tag, because no `v1.6.1` tag exists (only v1.6.0 and v1.6.2). It is
> left as published and flagged.

## Category breakdown

| Category | Count | % |
|---|---|---|
| AI security | 241 | 36.2% |
| Agent autonomy | 216 | 32.5% |
| Limited risk | 155 | 23.3% |
| High risk | 35 | 5.3% |
| Credential exposure | 14 | 2.1% |
| Prohibited | 4 | 0.6% |
