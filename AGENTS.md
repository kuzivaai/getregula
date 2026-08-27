# Regula — Agent Instructions

Start with `docs/ENGINEERING_ROADMAP.md`, then verify mutable GitHub, deployment and
registry observations directly. Public repository content must be limited to
product code, reusable engineering evidence and user-facing documentation.

EU AI Act compliance CLI for code. Python 3.10+ stdlib-only core.

GitHub: kuzivaai/getregula | Distribution: source-only while PyPI is unavailable | CLI: `regula`

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
- **Privacy-guard awareness**: repository operations are scanned for credential and private-data patterns. Use char-code construction for sensitive-shape test fixtures.
- **Public-repository privacy**: never commit handovers, session logs, private
  plans, pricing experiments, outreach records, personal names or contact
  details, immigration/employment context, local usernames, hostnames or
  machine-specific absolute paths. Use `/home/USER`, `/mnt/c/Users/USER` and
  `LOCAL-MACHINE` in public examples.

## Quality Checkpoints

- After code changes: run the verify command (all 4 steps)
- After writing tests: wire into `test_classification.py` via alias import + globals binding
- After regulatory content: verify claims against primary legislation before committing
- Before releases: bump `scripts/constants.py:VERSION` and every current-version declaration. The enforced set is enumerated by `tests/test_source_of_truth.py` (CITATION.cff, mcp-server.json, server.json, site/llms.txt, references/annex_iv_template.md, docs/MODEL_CARD.md, plus schema.org softwareVersion on the site pages) and fails on drift; CLAUDE.md's version line is manual. pyproject.toml is dynamic and must NOT carry a literal version (same test enforces this).
- After site changes: confirm DE and PT-BR locales updated

## Architecture

- Entry point: `scripts/cli.py` (monolith)
- Risk patterns: `scripts/risk_patterns.py`
- Framework crosswalk: `references/framework_crosswalk.yaml`
- Tests: `tests/test_classification.py` (custom runner) + `tests/test_*.py` (pytest)
- Site: `site/` (GitHub Pages, 3 locales: EN, DE, PT-BR)
- Version source of truth: `scripts/constants.py:VERSION` (must match `pyproject.toml`)
- **Web scanner**: `site/assess/scanner.js` — client-side port of the Python detection rules. Regenerate it when patterns change and verify it with `benchmarks/synthetic/fixtures/`. **`tests/test_scanner_js.js` executes all 38 canonical fixtures, including all 30 high-risk fixtures.** Runtime parity is not detector validity or real-world accuracy; read the emitted label-fidelity summary and `docs/ENGINEERING_ROADMAP.md`.
- **Assess tool**: `site/assess/` — EN (`index.html`), DE (`de.html`), PT-BR (`pt-br.html`). All share `scanner.js`. Locale pages duplicate the JS scoring engine with translated strings — changes to scoring logic must be applied to all 3 files.
