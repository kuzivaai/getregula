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

# Step 4: Doctor health checks
python3 -m scripts.cli doctor

# Step 5: The six fast gates (seconds each; capture each exit code)
python3 scripts/claim_auditor.py --verify-facts
python3 scripts/site_integrity.py
python3 scripts/cascade_count.py --check
python3 scripts/build_recall_artefact.py --check
python3 scripts/build_gap_demo.py --check
python3 scripts/check_selfref_sourcing.py --control-only
```

After all pass, report the counts. If any fail, show the specific failure and diagnose the root cause.

**This sequence is NOT the whole of CI.** CI additionally runs: the security
self-check, the lint job, the html-wellformed job, and the claim-audit job
(`claim_auditor.py --diff-base`, which scans every Markdown/HTML file changed
against the base ref). A local /verify can be fully green while the claim
gate is red; that is exactly the recorded state of the improvement branch
(`docs/improvement/LEDGER.md` section 6). Before any PR, also run:

```bash
python3 scripts/claim_auditor.py --diff-base origin/main
```

and treat its findings as blocking.

## Post-Verification Reminders

After verification passes, check whether any of these apply to the work just completed:

- **Wrote regulatory content?** Run `/research-eval` to verify claims against primary sources.
- **Modified `scripts/*.py`?** Check for `re.compile()` inside functions — see `hoisting-regex-compiles` skill.
- **Added new test files?** Ensure they are wired into `test_classification.py` via alias import.
- **Added or removed tests?** The collected count moves: run `python3 scripts/site_facts.py` then `python3 scripts/cascade_count.py --apply` in the SAME commit as the tests.
- **Changed version-bearing text?** `tests/test_source_of_truth.py` is the checklist — see `releasing-regula` skill.
