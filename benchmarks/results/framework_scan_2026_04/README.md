# Framework scan data — "We scanned 5 AI frameworks for EU AI Act compliance"

Regula v1.7.0 scan output for the 5 frameworks analysed in
[the blog post](https://getregula.com/blog/blog-scanning-5-frameworks.html).

Scanned: 25 April 2026 against shallow clones of each framework's default branch.

## Reproduce

```bash
pipx install regula-ai
git clone --depth 1 https://github.com/<owner>/<repo>.git
regula check <repo> --format json > <repo>.json
```

## Results summary (v1.7.0, 25 April 2026)

| Framework | Stars | Source files | Findings |
|---|---|---|---|
| HuggingFace Transformers | 159,867 | 4,255 | 175 |
| LlamaIndex | 48,882 | 4,594 | 163 |
| CrewAI | 49,778 | 1,104 | 78 |
| LangChain | 134,779 | 2,463 | 53 |
| PyTorch | 99,411 | 7,010 | 93 |
| **Total** | **492,717** | **19,426** | **562** |

## Category breakdown

| Category | Count | % |
|---|---|---|
| AI security | 304 | 54.1% |
| Agent autonomy | 104 | 18.5% |
| High risk | 80 | 14.2% |
| Limited risk | 57 | 10.1% |
| Credential exposure | 17 | 3.0% |
| Prohibited | 0 | 0% |
