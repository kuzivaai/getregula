Run the full Regula verification sequence. Report pass/fail for each step. If any step fails, investigate before continuing.

```bash
# Step 1: Custom test runner (572+ assertions, 239+ test functions)
python3 tests/test_classification.py

# Step 2: Built-in self-test (6 assertions)
python3 -m scripts.cli self-test

# Step 3: Doctor health checks (10 checks)
python3 -m scripts.cli doctor
```

After all three pass, report the counts. If any fail, show the specific failure and diagnose the root cause.
