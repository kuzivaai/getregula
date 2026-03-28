# regula-ignore
# Module 3: Scanning Real Code

## What You'll Learn

- Scan open-source AI projects
- Interpret findings on real codebases
- Understand true positives vs false positives

## Setup: Clone a Real Project

```bash
cd /tmp
git clone --depth 1 https://github.com/anthropics/anthropic-cookbook.git
```

## Scan It

```bash
cd /path/to/getregula
python3 scripts/cli.py check /tmp/anthropic-cookbook
```

## What You Should See

Approximately 32 findings:
- 3 AI Security findings (BLOCK tier) — all genuine pickle.load() calls in vectordb.py files
- 29 Minimal-risk findings — correctly identifying AI-related code files

The 3 BLOCK findings are **true positives**: the vectordb.py files use `pickle.load(file)` to deserialise data, which is an arbitrary code execution risk (OWASP LLM05).

## JSON Output for Analysis

```bash
python3 scripts/cli.py check /tmp/anthropic-cookbook --format json | python3 -c "
import json, sys
findings = json.load(sys.stdin)
active = [f for f in findings if not f.get('suppressed')]
for tier in ['ai_security', 'high_risk', 'limited_risk', 'minimal_risk']:
    count = sum(1 for f in active if f['tier'] == tier)
    if count > 0:
        print(f'{tier}: {count}')
"
```

## Understanding False Positives

Not every finding is a real issue. Common false positive sources:
- Test files containing mock data or example patterns
- Documentation that discusses AI concepts
- Function names that coincidentally match patterns (e.g., `text_to_image_category_name`)

Regula mitigates these by:
- Deprioritising test file findings (-40 confidence score)
- Using word boundaries on patterns to avoid substring matches
- Skipping comments and docstrings in AI security checks

## Exercise

1. How many BLOCK-tier findings did you get?
2. Look at the actual code in the flagged files — are they true positives?
3. Run with `--verbose` to see INFO-tier findings

## Verification

If you found 3 BLOCK findings, all in vectordb.py files for pickle.load, you've correctly identified true positive security issues.

---

**Next:** [Module 4: Compliance Gaps](04-compliance-gaps.md)
