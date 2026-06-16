# Regula — Project Instructions

@AGENTS.md

Regula v1.7.2 — EU AI Act compliance CLI for code. Python 3.10+ stdlib-only core.

GitHub: kuzivaai/getregula | PyPI: regula-ai | CLI: `regula`

## Commands

```bash
# Full verification — run all four before claiming anything is done
python3 tests/test_classification.py && python3 -m pytest tests/ -q && python3 -m scripts.cli self-test && python3 -m scripts.cli doctor
```

## What NOT to Change

- cli.py monolith structure
- Bare import convention or `sys.path.insert` lines
- Manual test list at bottom of test_classification.py
- `json_output()` envelope format

## Architecture — DO NOT CHANGE

**IMPORTANT: Bare imports.** All `scripts/*.py` use `from errors import RegulaError`, not `from scripts.errors` or `.errors`. This works via `sys.path.insert(0, str(Path(__file__).parent))` at the top of each file. Do NOT remove these lines or convert to relative imports.

**Test convention:** Custom runner walks `globals()` of `tests/test_classification.py`. Separate test files are wired in via alias imports + globals binding. Pytest discovers `tests/test_*.py` natively.

**Version source of truth:** `scripts/constants.py:VERSION`. Must match `pyproject.toml` version and landing page eyebrow in `index.html`, `de.html`, `pt-br.html`.

**JSON envelope:** `json_output()` format is `{format_version, regula_version, command, timestamp, exit_code, data}`. Do not change.

**cli.py monolith:** Do not refactor unless explicitly asked.

## IMPORTANT: Hook Awareness

`hooks/pre_tool_use.py` scans ALL Bash/Write/Edit ops for credential patterns. Test fixtures use char-code construction to avoid triggering:
```python
test_key = ''.join(chr(c) for c in [65, 75, 73, 65, ...])
```
If blocked, construct values the same way. Do NOT bypass hooks.

## Locale Sync

Update ALL locale versions (EN, PT-BR, DE) in the same pass. Site-specific conventions are in `.claude/rules/site-html.md`.

## Regulatory Context

For current EU AI Act timeline, Omnibus status, and international regulation context, see the `regulatory-context` skill. It loads automatically when regulatory topics arise.

## Quality Checkpoints

**After writing or modifying code:**
1. Run `/verify` — all four steps must pass before claiming done
2. If you touched `scripts/*.py`, check for `re.compile()` inside functions — use `hoisting-regex-compiles` skill if found

**After writing tests:**
- Wire new test files into `test_classification.py` via alias import + globals binding
- Use `discovering-test-gaps` skill to check what else is untested

**Before any release or version bump:**
- Use `/releasing-regula X.Y.Z` — it lists all 9 files that need updating

**After writing regulatory content (site, docs, README):**
- Run `/research-eval` on any regulatory claim before committing
- The `regulatory-context` skill has the current Omnibus status — check it first

**After completing a significant feature or audit:**
- Run `/code-review` for security, performance, and correctness review
- Run `/research-eval` if the work involved any statistics, competitor claims, or regulatory references

## Compaction

When compacting, always preserve: bare import convention, "What NOT to Change" list, hook awareness, verification command, quality checkpoints, and locale sync requirement.

## Thoroughness

Default to honest framing: "code scanning and questionnaires are complementary" not "code scanning beats questionnaires."
