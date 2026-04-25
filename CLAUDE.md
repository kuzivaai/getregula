# Regula — Project Instructions

Regula v1.7.0 — EU AI Act compliance CLI for code. Python 3.10+ stdlib-only core.

GitHub: kuzivaai/getregula | PyPI: regula-ai | CLI: `regula`

## Quick Reference

- **61 commands** | **52 pattern categories, 389 regexes** | **8 language families** | **12 compliance frameworks**
- **1,111 unique tests** (pytest collects 1,232; 121 duplicated via globals() binding)
- **Zero production dependencies** (stdlib-only)
- Positioned as the **code layer** of AI governance, not the whole programme — see `docs/what-regula-does-not-do.md`

## Commands

```bash
# Full verification — run all four before claiming anything is done
python3 tests/test_classification.py && python3 -m pytest tests/ -q && python3 -m scripts.cli self-test && python3 -m scripts.cli doctor
```

## Architecture — DO NOT CHANGE

**Bare imports:** All `scripts/*.py` use `from errors import RegulaError`, not `from scripts.errors` or `.errors`. This works via `sys.path.insert(0, str(Path(__file__).parent))` at the top of each file. Do NOT remove these lines or convert to relative imports.

**Test convention:** Custom runner walks `globals()` of `tests/test_classification.py`. Separate test files are wired in via alias imports + globals binding. Pytest discovers `tests/test_*.py` natively.

**Version source of truth:** `scripts/constants.py:VERSION`. Must match `pyproject.toml` version and landing page eyebrow in `index.html`, `de.html`, `pt-br.html`.

**JSON envelope:** `json_output()` format is `{format_version, regula_version, command, timestamp, exit_code, data}`. Do not change.

**cli.py monolith:** Do not refactor unless explicitly asked.

## Regulatory Context

**Omnibus status (April 2026):** EU Digital Omnibus proposes delaying Annex III high-risk deadlines from 2 Aug 2026 to 2 Dec 2027. EP voted 569-45-23 on 26 March 2026. Trilogue ongoing; Cypriot Presidency targeting 28 April 2026 agreement. **Not yet law.** Keep Aug 2026 as baseline but always add Omnibus caveat nearby.

**Brazil:** PL 2338/2023 (Marco Legal da IA) passed Senate 10 Dec 2024, in Chamber Special Commission. Not yet law. LGPD Art. 20 (automated decisions) already in force. `regula gap --framework lgpd` and `--framework marco-legal-ia` both work.

## Hook Awareness

`hooks/pre_tool_use.py` scans ALL Bash/Write/Edit ops for credential patterns. Test fixtures use char-code construction to avoid triggering:
```python
test_key = ''.join(chr(c) for c in [65, 75, 73, 65, ...])
```
If blocked, construct values the same way. Do NOT bypass hooks.

## Project Conventions

- Update ALL locale versions (EN, PT-BR, DE) in the same pass
- Use `h3` not `h4` for card headings in site HTML
- Use `var(--text-dim)` not `#707090` for muted inline text
- Add `class="cmp-table"` to comparison tables for sticky first column

## What NOT to Change

- cli.py monolith structure
- Bare import convention or `sys.path.insert` lines
- Manual test list at bottom of test_classification.py
- `json_output()` envelope format

## Thoroughness

- Fix ALL issues an audit finds, not just the easy ones
- `grep -ri` the entire repo before claiming a text change is complete
- Use available tools (Playwright, EU regulations MCP, /research-eval) — never say "I can't verify"
- Default to honest framing: "code scanning and questionnaires are complementary" not "code scanning beats questionnaires"
