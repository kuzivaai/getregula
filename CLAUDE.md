# Regula — Project Instructions

## Identity

Regula v1.2.0 — EU AI Act compliance CLI for code. Python 3.10+ stdlib-only core. 29 CLI commands, 121 risk patterns, 8 languages, 10 compliance frameworks. Zero production dependencies.

GitHub: kuzivaai/getregula | PyPI: regula-ai | CLI command: regula

## Commands

```bash
# Primary test runner (custom — tests must be in the manual list at bottom of file)
python3 tests/test_classification.py

# Secondary (pytest — discovers test_ functions automatically)
python3 -m pytest tests/ -q

# Verification
python3 -m scripts.cli self-test    # 6 built-in assertions
python3 -m scripts.cli doctor       # 10 health checks

# Run all three sequentially before claiming anything is "done"
python3 tests/test_classification.py && python3 -m scripts.cli self-test && python3 -m scripts.cli doctor
```

## Import Convention — DO NOT CHANGE

All `scripts/*.py` files use **bare imports**:
```python
# CORRECT
from errors import RegulaError
from classify_risk import classify

# WRONG — do NOT use these
from scripts.errors import RegulaError
from .errors import RegulaError
```

This works because every file has `sys.path.insert(0, str(Path(__file__).parent))` near the top. Do NOT remove these lines. Do NOT convert to relative imports.

## Test Convention

1. Define the test function in `tests/test_classification.py`
2. Add it to the **manual list** at the bottom of the file (inside `if __name__ == "__main__":`)
3. Both steps are required — the custom runner only executes functions in that list

## Version

Source of truth: `scripts/cli.py:VERSION`

Must match:
- `pyproject.toml` `[project] version`
- Landing page eyebrow in `index.html`, `de.html`, `pt-br.html`

## Package

- PyPI name: `regula-ai`
- CLI command after install: `regula`
- Entry point: `scripts.cli:main` (defined in pyproject.toml)

## CLI Pattern

To add a new command:
1. Add `cmd_X(args)` function in `scripts/cli.py`
2. Add subparser in `main()`: `p_x = subparsers.add_parser("x", help="...")`
3. Wire: `p_x.set_defaults(func=cmd_X)`
4. Add `--format` arg if the command supports JSON output
5. Use `json_output("x", data)` for consistent JSON envelope

## Hook Awareness

`hooks/pre_tool_use.py` runs on ALL Bash/Write/Edit/MultiEdit operations. It scans for credential patterns (AWS keys, GitHub tokens, etc.).

Test fixtures that contain synthetic credentials use char-code construction to avoid triggering:
```python
test_key = ''.join(chr(c) for c in [65, 75, 73, 65, ...])
```

If a hook blocks your command, do NOT bypass it. Construct test values the same way.

## What NOT to Change

- Do not refactor cli.py's monolith structure unless explicitly asked
- Do not convert bare imports to relative imports
- Do not remove `sys.path.insert` lines from any file
- Do not delete the manual test list at the bottom of test_classification.py
- Do not change the `json_output()` envelope format (format_version, regula_version, command, timestamp, exit_code, data)
