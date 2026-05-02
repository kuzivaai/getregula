# Regula — Agent Instructions

EU AI Act compliance CLI for code. Python 3.10+ stdlib-only core.

## Build & Test

```bash
# Verify (run all before claiming done)
python3 tests/test_classification.py && python3 -m pytest tests/ -q && python3 -m scripts.cli self-test && python3 -m scripts.cli doctor
```

## Key Constraints

- **Bare imports only**: `from errors import RegulaError`, not `from scripts.errors`
- **Zero external dependencies**: stdlib-only core, do not add packages
- **Do not refactor** cli.py monolith unless explicitly asked
- **Locale sync**: changes to EN site content must also update DE and PT-BR versions
- **Regulatory claims** must cite specific article numbers and include Omnibus caveat for EU AI Act deadlines

## Architecture

- Entry point: `scripts/cli.py` (monolith, 61 commands)
- Risk patterns: `scripts/risk_patterns.py` (52 categories, 389 regexes)
- Framework crosswalk: `references/framework_crosswalk.yaml` (12 frameworks)
- Tests: `tests/test_classification.py` + `tests/test_*.py` (1,111 unique)
- Site: `site/` (GitHub Pages, 3 locales: EN, DE, PT-BR)
