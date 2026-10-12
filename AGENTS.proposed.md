<!-- DRAFT FOR MY REVIEW. Generated 26 August 2026 by the scaffolding overhaul run (see ~/agent-scaffolding/REPORT.md). Only commands marked verified were run in that session; everything else is Asserted or not run. Delete this comment when accepted. -->
# getregula (regula-ai)
Purpose: EU AI Act compliance CLI, published to PyPI as regula-ai.
Check command: `python3 tests/test_classification.py && python3 -m pytest tests/ -q && python3 -m scripts.cli self-test && python3 -m scripts.cli doctor` (Asserted from the existing AGENTS.md and ci.yaml; not run in full).
Setup: `pip install -e ".[test]"` (Asserted from pyproject; not run). Test: `python3 -m pytest tests/ -q` (run 26 Aug 2026 with the system python3: timed out at 400 s at 64 percent with 0 failures; not completed). Build: `python3 -m build` (not run).
Known failure modes: the repo's `.venv` has no pytest installed (Demonstrated 26 Aug 2026: "No module named pytest"); use the system interpreter or reinstall the test extra. CI runs the suite with `-n auto --dist worksteal`.
Boundaries: benchmark and performance figures are under a claim freeze until the repo's own claim-integrity audit clears (Asserted, frozen 1 Aug 2026); do not quote them anywhere. Public repository: no personal identifiers, employer names or expanded home paths in any committed file.
Priorities for this repo: correctness of regulatory content, then security, then UX of the CLI output.
