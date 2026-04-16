# regula-ignore
# Module 5: AI Dependency Security

## What You'll Learn

- Check AI dependency pinning quality
- Understand why unpinned AI dependencies are dangerous
- Detect lockfile presence

## Background: The LiteLLM Incident

In March 2026, the LiteLLM Python package was compromised via a CI/CD pipeline attack. Malicious versions (1.82.7 and 1.82.8) harvested API keys, SSH keys, and cloud credentials. The attack worked because developers running `pip install litellm` without version pinning received the compromised version.

## Run a Dependency Scan

```bash
regula deps --project /tmp/anthropic-cookbook
```

## Pinning Quality Levels

| Level | Example | Score |
|-------|---------|-------|
| Hash-pinned | `openai==1.52.0 --hash=sha256:abc...` | 100 |
| Exact | `openai==1.52.0` | 80 |
| Compatible | `openai~=1.52` | 60 |
| Range | `openai>=1.0,<2.0` | 30 |
| Unpinned | `openai` | 0 |

AI dependencies are weighted 3x in the score calculation because they handle sensitive data and model operations.

## Lockfile Detection

Regula checks for 10 lockfile formats:
Pipfile.lock, poetry.lock, uv.lock, package-lock.json, yarn.lock, pnpm-lock.yaml, bun.lockb, Cargo.lock, .conda-lock.yml, conda-lock.yml

A lockfile present adds +20 to the pinning score (capped at 100).

## Dependency File Parsers

Regula parses 7 dependency file formats:
requirements.txt, pyproject.toml, package.json, Pipfile, Cargo.toml, CMakeLists.txt, vcpkg.json

## Important Limitation

Regula checks pinning quality, NOT vulnerabilities. For vulnerability scanning, use pip-audit or osv-scanner as a complement:

```bash
pip install pip-audit
pip-audit -r requirements.txt
```

## Exercise

1. Create a `requirements.txt` with: `openai` (unpinned), `torch==2.4.1` (exact), `langchain>=0.1` (range)
2. Run `regula deps --project .` on it
3. What's the pinning score? Why?

---

**Next:** [Module 6: AI Security Patterns](06-ai-security-patterns.md)
