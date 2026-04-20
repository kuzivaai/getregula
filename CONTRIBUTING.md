# Contributing to Regula

Thanks for your interest in improving EU AI Act compliance tooling. This guide covers everything you need to get started.

## Quick Start

```bash
# Clone your fork
git clone https://github.com/<your-username>/getregula.git
cd getregula

# No install needed for core — it's pure Python 3.10+
regula --help

# Optional dependencies (for YAML config and AST analysis)
pip install pyyaml tree-sitter

# Run the test suite
pytest tests/ -q
# Must output: "X passed"
```

## Project Structure

```
scripts/
├── cli.py                 # CLI entry point and argument parsing
├── classify_risk.py       # Risk classification engine
├── report.py              # Code scanner and reporting
├── risk_patterns.py       # Pattern definitions for risk detection
├── risk_types.py          # Risk category types and constants
├── framework_mapper.py    # Crosswalk mappings (NIST, ISO, etc.)
├── ast_engine.py          # AST-based analysis (tree-sitter)
├── compliance_check.py    # Compliance checking logic
├── remediation.py         # Fix suggestions
└── ...                    # See scripts/ for full list
tests/
├── test_classification.py     # Core classification tests (main test file)
└── ...                        # 44 test files total — see tests/ for full list
```

## How to Add a Risk Pattern

Risk patterns live in `scripts/risk_patterns.py`. Each pattern is a regex or keyword set that maps to a risk category.

1. Open `scripts/risk_patterns.py` and find the relevant pattern group.
2. Add your pattern following the existing format.
3. Write a failing test first (see Testing below).
4. Run tests to confirm it passes.

Example: if you want to flag a new biometric library:

```python
# In risk_patterns.py, add to the relevant pattern list
"new_biometric_lib",
```

## How to Add a Framework Mapping

Framework mappings live in `scripts/framework_mapper.py`. These map EU AI Act articles to controls in other frameworks (NIST AI RMF, ISO 42001, etc.).

1. Open `scripts/framework_mapper.py`.
2. Find or create the mapping dictionary for your target framework.
3. Add entries linking AI Act articles to the corresponding controls.
4. Write a test to verify the mapping resolves correctly.

## How to Add Language Support

Regula scans source code for AI-related patterns. To add support for a new programming language:

1. Add file extension handling in `scripts/report.py` (the scanner).
2. Add any language-specific patterns to `scripts/risk_patterns.py`.
3. If using AST analysis, add a tree-sitter grammar in `scripts/ast_engine.py`.
4. Write tests with sample code in the new language.

## Testing

Tests are spread across 44 files in `tests/`. The main classification tests live in `tests/test_classification.py`; other test files cover agent governance, documentation, hooks, registry, reliability, security hardening, and critical path coverage. Run all tests with `pytest tests/ -q`.

The test pattern is:

1. Define a test function that exercises the behaviour you want to verify.
2. Add it to the appropriate test file (or `test_classification.py` for classification logic).
3. Run with `pytest tests/ -q`.

```python
def test_my_new_pattern():
    """Verify that XYZ pattern is classified as high risk."""
    result = classify_something(...)
    assert result.risk_level == "high", f"Expected high, got {result.risk_level}"

# Add to the tests list:
tests = [
    # ... existing tests ...
    test_my_new_pattern,
]
```

**Write failing tests first.** This is not optional. The workflow is:

1. Write a test that demonstrates the expected behaviour.
2. Run it — confirm it fails.
3. Implement the change.
4. Run it again — confirm it passes.
5. Run the full suite — confirm no regressions.

## Making a Pull Request

### Workflow

1. Fork the repository.
2. Create a feature branch: `git checkout -b my-feature`.
3. Write a failing test for your change.
4. Implement the change.
5. Run `pytest tests/ -q` — all tests must pass.
6. Commit with a clear message: `feat: add detection for XYZ library`.
7. Push and open a PR against `main`.

### PR Checklist

Before submitting, verify:

- [ ] `pytest tests/ -q` shows "X passed"
- [ ] New behaviour has at least one test
- [ ] No new external dependencies added to core (discuss first if needed)
- [ ] Commit messages follow conventional format (`feat:`, `fix:`, `docs:`, etc.)
- [ ] User-facing copy uses British English
- [ ] No secrets, API keys, or credentials in the diff
- [ ] PR description explains *why*, not just *what*

### Commit Message Format

```
type: short description

Longer explanation if needed.
```

Types: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`

## Code Style

- Follow existing patterns in the codebase. Consistency matters more than any style guide.
- Python 3.10+ features are fine (match statements, union types with `|`, etc.).
- No type stubs needed — the codebase doesn't use them.
- British English in all user-facing strings and documentation.
- Keep functions focused. If a function does two things, split it.

## Reporting Issues

- **Bugs**: Use the bug report template.
- **Pattern requests**: Use the pattern request form.
- **False positives**: Use the false positive template — these are particularly valuable for improving accuracy.

## Code of Conduct

- Be respectful and constructive.
- Assume good intent.
- Be inclusive — this tool serves a global community.
- Focus on the work, not the person.
- If something is unclear, ask rather than assume.

That's it. No lengthy governance documents. If you're unsure about anything, open an issue and ask.
