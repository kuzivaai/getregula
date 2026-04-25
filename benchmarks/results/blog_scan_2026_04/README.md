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
(389 patterns vs 330 in v1.6.1).

## Category breakdown

| Category | Count | % |
|---|---|---|
| AI security | 241 | 36.2% |
| Agent autonomy | 216 | 32.5% |
| Limited risk | 155 | 23.3% |
| High risk | 35 | 5.3% |
| Credential exposure | 14 | 2.1% |
| Prohibited | 4 | 0.6% |
