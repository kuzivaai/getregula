Add a new risk detection pattern to Regula for: $ARGUMENTS

## Steps

1. **Choose the tier** in `scripts/risk_patterns.py`:
   - `PROHIBITED_PATTERNS` — Article 5 banned practices
   - `HIGH_RISK_PATTERNS` — Annex III high-risk areas
   - `LIMITED_RISK_PATTERNS` — Article 50 transparency obligations
   - `AI_SECURITY_PATTERNS` — OWASP/security patterns

2. **Add the pattern dict** to the chosen tier:
   ```python
   "pattern_name": {
       "patterns": ["regex1", "regex2"],  # List of regex strings (case-insensitive)
       "article": "5(1)(a)",              # EU AI Act article reference
       "description": "What this detects",
       "conditions": "When this prohibition/requirement applies",
       "exceptions": "Any exceptions from the Act, or None",
   },
   ```

3. **Add test cases** to `tests/test_classification.py`:
   - Test that the pattern matches expected input
   - Test that it does NOT match benign input (false positive check)
   - Add both test functions to the manual list at the bottom

4. **Run verification**: `/verify`

5. **Run benchmark** to check for false positives on real projects:
   ```bash
   python3 benchmarks/run_benchmark.py  # if benchmark suite exists
   ```

## Pattern Guidelines

- Regex patterns are matched case-insensitively against full file content
- Use `\b` word boundaries to reduce false positives
- Each pattern category is a dict (key = pattern name, value = pattern config)
- Comment-only matches are filtered out by the comment stripping layer
