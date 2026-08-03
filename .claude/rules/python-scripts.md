---
globs:
  - "scripts/**/*.py"
---

# Python Script Rules

- Use **bare imports**: `from errors import RegulaError`, NOT `from scripts.errors` or `.errors`
- Every file must have `sys.path.insert(0, str(Path(__file__).parent))` near the top
- Do NOT add external dependencies — stdlib-only core is a hard constraint
- Do NOT refactor `cli.py` monolith unless explicitly asked
- Do NOT change the `json_output()` envelope format
- Run `python3 -m scripts.cli self-test && python3 -m scripts.cli doctor` after any change to verify
