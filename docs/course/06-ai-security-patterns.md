# regula-ignore
# Module 6: AI Security Patterns

## What You'll Learn

- Detect AI-specific security vulnerabilities in code
- Understand OWASP LLM Top 10 mapping
- Fix common AI security antipatterns

## What Regula Detects

Regula checks for 6 AI-specific security vulnerability categories (14 patterns):

| Pattern | OWASP | Severity | What It Catches |
|---------|-------|----------|-----------------|
| Unsafe deserialization | LLM05 | High | pickle.load, torch.load, joblib.load |
| Prompt injection risk | LLM01 | High | User input concatenated into prompts |
| No output validation | LLM02 | Critical | eval() or exec() on AI model output |
| Hardcoded model path | LLM03 | Medium | Loading models from URLs or temp dirs |
| Unbounded tokens | LLM10 | Medium | max_tokens set to None or very high |
| High temperature | LLM09 | Low | temperature >= 1.0 in production |

These are checked on actual code lines, skipping comments and docstrings to reduce false positives.

## Real Example

The anthropic-cookbook scan found 3 genuine unsafe deserialization findings:
```
[BLOCK] vectordb.py:80 — pickle.load(file)
```

This is a real security risk: pickle.load can execute arbitrary code. The fix is to use safetensors format or add `weights_only=True` to torch.load.

## Exercise

Create a file `test_security.py`:
```python
import pickle
with open('model.pkl', 'rb') as f:
    model = pickle.load(f)
```

Scan it:
```bash
python3 scripts/cli.py check . --format json | python3 -c "
import json, sys
for f in json.load(sys.stdin):
    if f['tier'] == 'ai_security':
        print(f'{f["file"]}:{f.get("line","?")} — {f["description"]}')"
```

## Remediation

Every AI security finding includes a specific fix. The inline remediation engine provides code snippets:

```bash
python3 scripts/cli.py check .
# Output includes:
#   Fix: Use safetensors format or torch.load(path, weights_only=True)
```

---

**Next:** [Module 7: CI/CD Integration](07-cicd-integration.md)
