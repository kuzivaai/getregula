# Regula — Agent Instructions

EU AI Act compliance CLI for code. Python 3.10+ stdlib-only core.

GitHub: kuzivaai/getregula | PyPI: regula-ai | CLI: `regula`

## Build & Test

```bash
# Verify (run all before claiming done)
python3 tests/test_classification.py && python3 -m pytest tests/ -q && python3 -m scripts.cli self-test && python3 -m scripts.cli doctor
```

## Key Constraints

- **IMPORTANT: Bare imports only**: `from errors import RegulaError`, NOT `from scripts.errors` or `.errors`. Every `scripts/*.py` file uses `sys.path.insert(0, str(Path(__file__).parent))` at the top. Do NOT remove or convert to relative imports.
- **Zero external dependencies**: stdlib-only core, do not add packages
- **Do not refactor** cli.py monolith unless explicitly asked
- **Do not change** `json_output()` envelope format: `{format_version, regula_version, command, timestamp, exit_code, data}`
- **Do not delete** manual test list at bottom of `tests/test_classification.py`
- **Locale sync**: changes to EN site content must also update DE and PT-BR versions
- **Regulatory claims**: cite specific article numbers; include Omnibus caveat for EU AI Act deadlines; see `regulatory-context` skill for current status
- **Hook awareness**: `hooks/pre_tool_use.py` scans all ops for credential patterns. Use char-code construction for test fixtures.

## Quality Checkpoints

- After code changes: run the verify command (all 4 steps)
- After writing tests: wire into `test_classification.py` via alias import + globals binding
- After regulatory content: verify claims against primary legislation before committing
- Before releases: update version in all 9 files (constants.py, pyproject.toml, CITATION.cff, CLAUDE.md, annex_iv_template.md, index.html, de.html, pt-br.html, uae.html)
- After site changes: confirm DE and PT-BR locales updated

## Architecture

- Entry point: `scripts/cli.py` (monolith)
- Risk patterns: `scripts/risk_patterns.py`
- Framework crosswalk: `references/framework_crosswalk.yaml`
- Tests: `tests/test_classification.py` (custom runner) + `tests/test_*.py` (pytest)
- Site: `site/` (GitHub Pages, 3 locales: EN, DE, PT-BR)
- Version source of truth: `scripts/constants.py:VERSION` (must match `pyproject.toml`)
- **Web scanner**: `site/assess/scanner.js` — client-side port of 627 patterns from `risk_patterns.py`. Must be regenerated when patterns change (see `.claude/handover.md`). Verify with `benchmarks/synthetic/fixtures/` (13 fixtures must match CLI tier).
- **Assess tool**: `site/assess/` — EN (`index.html`), DE (`de.html`), PT-BR (`pt-br.html`). All share `scanner.js`. Locale pages duplicate the JS scoring engine with translated strings — changes to scoring logic must be applied to all 3 files.
