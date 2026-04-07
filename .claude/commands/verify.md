Run the full Regula verification sequence. Report pass/fail for each step. If any step fails, investigate before continuing.

```bash
# Step 1: Custom test runner (manual list — asserts every test is registered)
python3 tests/test_classification.py

# Step 2: pytest discovery (catches anything not in the manual list,
#         including test files like tests/test_agent_governance.py
#         that the custom runner does not import)
pytest tests/ -q

# Step 3: Built-in self-test (6 assertions)
python3 -m scripts.cli self-test

# Step 4: Doctor health checks (10 checks)
python3 -m scripts.cli doctor
```

After all four pass, report the counts. If any fail, show the specific failure and diagnose the root cause.

This sequence mirrors the CI workflow in `.github/workflows/ci.yaml` exactly. If /verify is green locally, CI should be green too. If you skip step 2, you risk shipping changes that pass the custom runner but fail in CI — that exact gap shipped commit 06bf29a in this session.
