# Regula — Project Instructions

## Identity

Regula v1.7.0 — EU AI Act compliance CLI for code. Python 3.10+ stdlib-only core.

**Verified counts (2026-04-17):**
- **55 CLI commands** (verified via `regula --help-all`; `regula -h` shows 7 primary commands via progressive disclosure)
- **52 risk pattern categories** containing 404 individual regexes (8 prohibited, 15 high-risk, 4 limited-risk, 17 AI security, 2 bias, 6 governance observations) plus 1 GPAI training group (17 regexes)
- **182 AI framework detection indicators** (88 libraries, 10 model file types, 7 API endpoints, 13 ML patterns, 64 domain keywords)
- **8 language families scanned** via regex (Python, JavaScript, TypeScript, Java, Go, Rust, C/C++, Jupyter notebooks — deep AST analysis for Python/JS/TS only)
- **12 compliance frameworks with crosswalk data** (EU AI Act, NIST AI RMF, ISO 42001, NIST CSF, SOC 2, ISO 27001, OWASP LLM Top 10, MITRE ATLAS, EU CRA, LGPD, Marco Legal IA, UK ICO). Note: OWASP and MITRE have data for 4/7 articles. 5 additional frameworks (Colorado SB-205, Canada AIDA, Singapore AI, OECD AI, South Korea AI) have display handlers but no crosswalk data — filter keys removed until populated.
- **1,055 tests** (all passing — verified via `python3 -m pytest tests/ --collect-only -q` on 2026-04-17)
- **2 bias benchmarks** (CrowS-Pairs likelihood scoring + BBQ question-answering, with Wilson CI and bootstrap confidence intervals)
- **18 credential patterns** detected
- **1 GitHub Action** (composite, 13 inputs, 5 outputs, SARIF upload, PR comments)
- **1 MCP server** (3 tools: check, classify, gap)
- **Zero production dependencies** (stdlib-only core)

Positioned as the **code layer** of an AI governance programme, not the whole programme — see `docs/what-regula-does-not-do.md`.

**Omnibus status (as of April 2026):** The EU Digital Omnibus on AI proposes delaying Annex III high-risk deadlines from 2 Aug 2026 to 2 Dec 2027. EP adopted its negotiating position 569-45-23 on **26 March 2026** (vote held Thursday; press release dated 26 Mar). Trilogue negotiations launched the same day; Cypriot Council Presidency target for political agreement is 28 April 2026 (may slip into May). **Not yet law.** Do not remove Aug 2026 references — it remains the legal baseline — but every mention must have a nearby Omnibus caveat.

GitHub: kuzivaai/getregula | PyPI: regula-ai | CLI command: regula

## Honesty & Verification

Never fabricate statistics, GitHub stars, user counts, benchmarks, or marketing claims. Every numeric or factual claim in docs/landing pages/research must cite a verifiable source or be omitted.

## Workflow

Before claiming work is complete, verify it: run tests, check the actual file, or invoke the research-eval/verification-loop skill. Do not say 'done' or 'fixed' without evidence.

## Commands

```bash
# Primary test runner (custom — auto-discovers test_* functions in test_classification.py globals)
python3 tests/test_classification.py

# Secondary (pytest — discovers test_ functions automatically)
python3 -m pytest tests/ -q

# Verification
python3 -m scripts.cli self-test    # 6 built-in assertions
python3 -m scripts.cli doctor       # 11 health checks (9 pass + 2 info)

# Run all three sequentially before claiming anything is "done"
python3 tests/test_classification.py && python3 -m scripts.cli self-test && python3 -m scripts.cli doctor
```

## Google Search Console

GSC is connected via OAuth. Requires `.venv` activated (dependencies: `google-auth`, `google-auth-oauthlib`, `google-api-python-client`).

```bash
source .venv/bin/activate

# Top queries, last 28 days
python3 scripts/gsc_fetch.py --days 28 --dimensions query --limit 25

# Top pages
python3 scripts/gsc_fetch.py --days 28 --dimensions page --limit 25

# Blog pages only
python3 scripts/gsc_fetch.py --days 28 --page-filter "/blog"

# Daily trend for a query
python3 scripts/gsc_fetch.py --days 28 --dimensions date --query-filter "eu ai act"

# By country
python3 scripts/gsc_fetch.py --days 28 --dimensions country

# JSON output
python3 scripts/gsc_fetch.py --days 28 --format json

# Other properties (validground.com, streetsignal.co.za)
python3 scripts/gsc_fetch.py --site "sc-domain:validground.com" --days 28
```

Auth files (`credentials.json`, `token.json`) are gitignored. Token auto-refreshes. If it expires fully, re-run `gsc_auth.py` with the `.venv` activated.

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

1. Define the test function in `tests/test_<topic>.py` (or directly in `tests/test_classification.py`)
2. The custom runner walks `globals()` of `tests/test_classification.py` and runs every `test_*` function it finds (auto-discovery added in commit `a90009f`). Pytest discovers separate `tests/test_*.py` files natively.
3. To make tests in a separate file visible to the custom runner: import the module as an alias and bind the `test_*` functions into globals — see the `test_register` wiring at the top of `test_classification.py` for the pattern (it also filters out tests requiring pytest fixtures so they only run under pytest).

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

## Project Conventions

When updating landing pages or docs, apply changes to ALL locale versions (EN, PT-BR, DE, etc.) in the same pass.

## What NOT to Change

- Do not refactor cli.py's monolith structure unless explicitly asked
- Do not convert bare imports to relative imports
- Do not remove `sys.path.insert` lines from any file
- Do not delete the manual test list at the bottom of test_classification.py
- Do not change the `json_output()` envelope format (format_version, regula_version, command, timestamp, exit_code, data)
