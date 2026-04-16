# regula-ignore
# Module 10: Building Your Own Patterns

## What You'll Learn

- Add custom risk detection patterns
- Use the policy file for force-classification
- Extend the framework crosswalk

## Custom Patterns via Policy

The simplest way to add detection is via `regula-policy.yaml`:

```yaml
rules:
  risk_classification:
    force_high_risk:
      - "fraud_detection"    # Always classify as high-risk
      - "insurance_pricing"
    exempt:
      - "spam_filter"        # Confirmed low-risk after review
```

Note: `force_high_risk` cannot override Article 5 prohibited detections. Prohibited always takes priority.

## Adding Regex Patterns

To add new detection patterns, edit `scripts/classify_risk.py`:

1. Find the appropriate dict (PROHIBITED_PATTERNS, HIGH_RISK_PATTERNS, or LIMITED_RISK_PATTERNS)
2. Add a new entry following the existing format:

```python
"your_category": {
    "patterns": [r"your_pattern", r"another_pattern"],
    "articles": ["9", "10", "11", "12", "13", "14", "15"],
    "category": "Your Category Name",
    "description": "What this detects",
},
```

3. Add a test in `tests/test_classification.py`
4. Run the test suite: `python3 tests/test_classification.py`

## Pattern Quality Rules

Based on the audit findings, follow these rules when writing patterns:

1. **Use word boundaries** (`\b`) to prevent substring matches
2. **Require context** for common words — don't match "sentence" alone, match "sentencing recommendation"
3. **Skip comments** — the AI security checker skips `#` comments and docstrings
4. **Test against real code** — scan an actual project to check for false positives
5. **Target <10% false positive rate** — Google's Tricorder removes checks above this threshold

## Adding AI Security Patterns

Edit `AI_SECURITY_PATTERNS` in `scripts/classify_risk.py`:

```python
"your_pattern": {
    "patterns": [r"regex_here"],
    "owasp": "LLM01",  # Which OWASP LLM item
    "description": "What vulnerability this detects",
    "severity": "high",  # critical, high, medium, low
    "remediation": "Specific fix instruction",
},
```

## Exercise

1. Add a pattern to detect `requests.get()` calls without timeout (a reliability concern)
2. Write a test for it
3. Run the test suite to verify nothing breaks

## Verification

Run `python3 tests/test_classification.py` — if all tests pass plus your new test, you've successfully extended Regula.

---

## Course Complete

You've learned to:
- Scan codebases for EU AI Act risk patterns
- Interpret findings and distinguish true positives from false positives
- Assess compliance gaps for Articles 9-15
- Check AI dependency supply chain security
- Detect AI-specific security vulnerabilities
- Integrate into CI/CD pipelines
- Generate compliance documentation
- Map findings across 17 frameworks (see `references/framework_crosswalk.yaml`)
- Build custom detection patterns

**What's next:**
- Run the benchmark against your own projects
- Contribute patterns for your domain to the GitHub repo
- Join the conversation at [The Implementation Layer](https://theimplementationlayer.substack.com)
