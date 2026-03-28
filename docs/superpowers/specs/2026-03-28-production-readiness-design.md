# Regula Production Readiness — Design Spec

**Date:** 2026-03-28
**Status:** Approved for implementation
**Baseline:** v1.1.0 — 152 tests, 434 assertions, 20 subcommands, 22 `except Exception` blocks, 13 JSON output paths

---

## Overview

Two-wave implementation to improve Regula's error handling, diagnostics, and output consistency. Wave 1 fixes existing bugs and establishes error handling infrastructure. Wave 2 adds 2 new commands and consolidates patterns.

### What this spec does NOT do

- Add new classification patterns
- Refactor working code for style
- Add external dependencies
- Implement telemetry that sends data anywhere

---

## Wave 1: Error Handling Foundation

### 1.1 Custom Exception Hierarchy — `scripts/errors.py`

New file. Defines:

```python
class RegulaError(Exception):
    """Base for all Regula errors. CLI catches this and prints cleanly."""
    exit_code = 1

class ConfigError(RegulaError):
    """Bad or missing configuration file."""
    exit_code = 2  # Tool error, not findings

class PathError(RegulaError):
    """Target path doesn't exist or isn't accessible."""
    exit_code = 2  # Tool error, not findings

class ParseError(RegulaError):
    """File couldn't be parsed (bad JSON, YAML, syntax)."""
    exit_code = 2  # Tool error, not findings

class DependencyError(RegulaError):
    """Optional dependency missing and needed for requested operation."""
    exit_code = 2  # Tool error, not findings
```

All inherit from `RegulaError`. Each carries an `exit_code` attribute (default 1). The CLI top-level handler catches `RegulaError` and prints to stderr without traceback.

### 1.2 Exit Code Specification

| Code | Meaning | When |
|------|---------|------|
| 0 | Success, no actionable findings | Clean scan, successful command |
| 1 | Findings detected OR scan failure | BLOCK/WARN findings, prohibited classification, strict threshold not met |
| 2 | Tool error | Bad config, missing path, parse failure, usage error |
| 130 | Interrupted | User pressed Ctrl+C |

**Rationale (research-validated 2026-03-28):** Surveyed 6 scanner/linter tools — ESLint, Semgrep, Trivy, Bandit, Checkov, Pylint. All use exit 1 for "findings detected" and exit 2 for "tool/config error." None use exit 2 for findings severity. This follows scanner convention, not general CLI convention (where exit 2 = usage error per clig.dev). Full research: `~/Documents/Regula_Production_Readiness_Research_20260328/`.

**Changes needed:**
- Line 794: `sys.exit(0)` after help → change to `sys.exit(2)` (no command = usage error)
- Existing `sys.exit(2)` for BLOCK findings → change to `sys.exit(1)` (findings, not tool error)
- `PathError.exit_code = 2` (tool error, not findings)
- `ConfigError.exit_code = 2` (tool error)
- `ParseError.exit_code = 2` (tool error)
- Document exit codes in `--help` epilog

### 1.3 CLI Top-Level Wrapper

Modify `main()` in cli.py to wrap the dispatch in:

```python
try:
    args.func(args)
except RegulaError as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(e.exit_code)
except KeyboardInterrupt:
    sys.exit(130)
except BrokenPipeError:
    sys.exit(0)
```

This eliminates raw tracebacks for all known error conditions. Unknown exceptions still traceback (they're bugs, should be visible during development).

### 1.4 Path Validation Fixes

Commands that take a path must validate it exists before processing:

| Command | Current behaviour | Fix |
|---------|-------------------|-----|
| `check <path>` | Silently succeeds with 0 findings (exit 0) | Raise `PathError` if path doesn't exist |
| `classify --file <path>` | Raw `FileNotFoundError` traceback | Raise `PathError` with clean message |
| `report --project <path>` | Generates empty HTML report, exits 0 | Validate before delegating |
| `gap --project <path>` | Raw ValueError traceback, exits 0 (not even 1) | Raise PathError |
| `discover --project <path>` | Returns empty results, exits 0 | Validate before processing |
| `deps --project <path>` | Returns "GOOD: Dependencies are well-pinned", exits 0 | Validate before processing |
| `sbom --project <path>` | Generates SBOM with empty components, exits 0 | Validate before processing |

Each fix is a 2-3 line check at the top of the command function:

```python
if not Path(args.path).exists():
    raise PathError(f"Path does not exist: {args.path}")
```

### 1.5 Existing Command Fixes

**init_wizard.py — EOFError handling (2 `input()` calls, 0 handlers):**
Wrap both `input()` calls (lines 120, 140) in try/except EOFError. When EOF received, default to non-interactive behaviour (same as if user pressed Enter).

**cli.py — Git diff fallback (line 42-44):**
Currently silent `pass`. Add `print("Note: git not available, scanning all files", file=sys.stderr)` so the user knows why diff mode didn't work.

### 1.6 Silent Exception Cleanup

Target: the 6 `except Exception` blocks in user-facing code (4 in report.py, 2 in init_wizard.py).

**report.py line 124** (`except Exception: pass` in secrets check):
- Change to `except (ValueError, KeyError, AttributeError): pass` — these are the actual exceptions that can occur during credential pattern matching

**report.py line 142** (`except Exception: pass` in security findings):
- Same treatment — narrow to specific exceptions

**report.py line 183** (`except Exception: pass` in observations):
- Same treatment

**report.py line 692** (`except Exception: pass` in audit chain):
- Change to `except (OSError, ValueError, KeyError): pass` — file I/O and JSON parsing errors

**init_wizard.py line 89** (`except Exception as e` in quick scan):
- Change to `except (OSError, ImportError) as e` — the actual failure modes

**init_wizard.py line 156** (`except Exception as e` in hook install):
- Change to `except (OSError, PermissionError, subprocess.SubprocessError) as e`

The remaining 16 `except Exception` blocks in non-user-facing code (compliance_check.py has 6, sbom.py has 2, etc.) are left as-is in this wave. They are internal fallbacks where broad catching is intentional. Can be narrowed in a future pass if needed.

---

## Wave 2: New Features

### 2.1 `scripts/doctor.py` — `regula doctor`

**Purpose:** Check installation health. Matches the established `npm doctor` / `brew doctor` pattern.

**Checks (in order):**

1. **Python version** — >= 3.10 required. PASS/FAIL.
2. **Optional: pyyaml** — importable? PASS (installed) / WARN (not installed, using fallback parser).
3. **Optional: tree-sitter** — importable? Plus tree-sitter-javascript, tree-sitter-typescript. PASS/WARN per package.
4. **Policy file** — if regula-policy.yaml exists in CWD or ~/.regula/, attempt to load it. PASS (valid) / WARN (not found) / FAIL (exists but unparseable).
5. **Audit directory** — ~/.regula/audit/ writable? PASS/FAIL. If directory doesn't exist, attempt to create it. PASS (created) / FAIL (can't create).
6. **Hook status** — check if pre_tool_use.py exists in known locations (.claude/hooks/, .cursor/, etc.). PASS (found) / WARN (not installed).
7. **Config validation** — if policy file exists, validate: governance.ai_officer present, thresholds in 0-100 range, framework names in known set, exclusion patterns are valid. PASS/WARN/FAIL per check.
8. **Security checks** — .gitignore includes audit trail patterns, audit files not world-readable (Unix only). PASS/WARN.

**Output format:**

```
Regula Doctor

  PASS  Python 3.12.3 (>= 3.10 required)
  WARN  pyyaml not installed (pip install regula[yaml])
  PASS  tree-sitter 0.23.2
  PASS  tree-sitter-javascript 0.23.1
  PASS  tree-sitter-typescript 0.23.0
  PASS  Policy file: ./regula-policy.yaml
  PASS  Audit directory: ~/.regula/audit/ (writable)
  WARN  Hooks not detected
  PASS  Config: thresholds valid
  PASS  Audit files not world-readable

8 passed, 2 warnings, 0 failures
```

**Exit codes:** 0 if no FAIL. 1 if any FAIL.

**JSON output:** `regula doctor --format json` returns structured results.

**What this subsumes from the original spec:**
- `regula config validate` → check #7 above
- `regula security-self-check` → checks #6 and #8 above

### 2.2 `scripts/self_test.py` — `regula self-test`

**Purpose:** Verify the installation works. User runs this instead of needing the test file.

**Precedent note (research-validated 2026-03-28):** No popular CLI tool has a built-in self-test command. This is a Regula-specific design choice, justified because: (1) Regula produces compliance evidence that organisations may rely on for EU AI Act obligations; (2) users in regulated environments need to verify the classification engine works before trusting its output; (3) the closest analogue is calibration checks in safety-critical measurement tools, not general CLI patterns.

**Built-in test cases (hardcoded, not imported from tests/):**

1. **Prohibited detection** — `"social_credit_scoring_system"` → tier must be `prohibited`
2. **High-risk detection** — `"import torch\nmodel = BiometricClassifier()"` → tier must be `high_risk`
3. **Clean input** — `"print('hello world')"` → tier must be `minimal_risk`
4. **Credential detection** — `"AKIAIOSFODNN7EXAMPLE"` → must flag AWS key pattern
5. **Framework mapping** — EU AI Act mapping returns expected structure
6. **Limited-risk detection** — chatbot/emotion pattern → tier must be `limited_risk`

**Output:**

```
Regula Self-Test

  PASS  Prohibited practice detection
  PASS  High-risk classification
  PASS  Minimal-risk classification
  PASS  Credential detection
  PASS  Framework mapping
  PASS  Limited-risk classification

6/6 passed in 0.3s
```

**Exit codes:** 0 if all pass. 1 if any fail.

**Target:** < 1 second. These are in-memory classifications, no file I/O.

### 2.3 `scripts/degradation.py` — Graceful Degradation Utility

**Purpose:** Replace 14 scattered `except ImportError` blocks with a consistent pattern.

```python
def check_optional(package_name: str, feature: str, install_hint: str) -> bool:
    """Check if an optional package is available. Returns True if importable.
    Prints one-line guidance to stderr on first miss (per package, per process)."""
```

Behaviour:
- Returns `True` if package is importable, `False` if not
- On first miss per package per process, prints to stderr: `"Note: {package_name} not installed — {feature} ({install_hint})"`
- Subsequent misses for same package are silent (no spam)
- Uses a module-level set to track which warnings have been shown

**Usage in existing code (example, ast_engine.py):**

```python
# Before:
try:
    import tree_sitter
except ImportError:
    tree_sitter = None

# After:
from degradation import check_optional
if check_optional("tree_sitter", "using regex fallback for JS/TS", "pip install regula[ast]"):
    import tree_sitter
else:
    tree_sitter = None
```

**Scope:** Replace the 14 `except ImportError` blocks across 7 files (sbom.py: 3, classify_risk.py: 1, discover_ai_systems.py: 1, framework_mapper.py: 1, dependency_scan.py: 2, ast_engine.py: 2, compliance_check.py: 4).

### 2.4 `regula init --dry-run`

**Purpose:** Read-only reconnaissance mode for init. Shows what `regula init` would do without creating any files or installing anything.

**Behaviour:**
- Detects project type (reuses existing `_detect_platforms`)
- Runs quick scan (reuses existing `_run_quick_scan`)
- Shows summary and recommends next steps
- Creates nothing, modifies nothing
- Works in CI (no interactive prompts)

**Output:**

```
Regula Init (dry run — no changes will be made)

  Project type: Python (requirements.txt found)
  AI files found: 12
  Risk indicators: 3 high-risk, 1 limited-risk
  Platforms detected: claude-code

  Recommended next steps:
    regula init              Set up policy and hooks
    regula check .           Full scan
    regula gap --project .   Compliance gap assessment
```

This replaces the proposed `regula quickstart` command. No new subcommand needed — it's a flag on an existing command.

### 2.5 Output Schema Consistency

**Purpose:** Wrap all `--format json` output in a consistent envelope.

**Envelope:**

```json
{
  "format_version": "1.0",
  "regula_version": "1.1.0",
  "command": "check",
  "timestamp": "2026-03-28T14:30:00Z",
  "exit_code": 0,
  "data": { ... }
}
```

**Rationale (research-validated 2026-03-28):** Terraform uses `format_version` with semantic versioning — minor bumps for additive changes, major bumps for breaking changes. Consumers should "ignore any object properties with unrecognised names" for forward compatibility. gh CLI uses no envelope (raw arrays). We follow the Terraform pattern because Regula output may be consumed by CI tools and auditors who need schema stability.

**Implementation:** A helper function in cli.py:

```python
def json_output(command: str, data, exit_code: int = 0):
    envelope = {
        "format_version": "1.0",
        "regula_version": VERSION,
        "command": command,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "exit_code": exit_code,
        "data": data,
    }
    print(json.dumps(envelope, indent=2, default=str))
```

**Backwards compatibility:** This is a breaking change for anyone parsing raw JSON output. Migration path:
- `--format json` gets the new envelope (default going forward)
- `--format json-raw` outputs the old raw format (deprecated, removed in v1.3)
- Document the change in release notes

**Scope:** Replace the 13 `json.dumps` calls in cli.py with `json_output()`. The `data` field contains the existing JSON schema unchanged — no breaking changes to the inner structure.

---

## Files Changed

### New files (4):
- `scripts/errors.py` — exception hierarchy (~30 lines)
- `scripts/doctor.py` — doctor command (~150 lines)
- `scripts/self_test.py` — self-test command (~80 lines)
- `scripts/degradation.py` — optional dependency utility (~40 lines)

### Modified files:
- `scripts/cli.py` — top-level error handler, path validation, 2 new subcommands, JSON envelope, no-args exit code, git diff warning
- `scripts/init_wizard.py` — EOFError handling, --dry-run flag
- `scripts/report.py` — narrow 4 `except Exception` blocks
- `scripts/sbom.py` — use degradation.py for 3 ImportError blocks
- `scripts/classify_risk.py` — use degradation.py for 1 ImportError block
- `scripts/discover_ai_systems.py` — use degradation.py for 1 ImportError block
- `scripts/framework_mapper.py` — use degradation.py for 1 ImportError block
- `scripts/dependency_scan.py` — use degradation.py for 2 ImportError blocks
- `scripts/ast_engine.py` — use degradation.py for 2 ImportError blocks
- `scripts/compliance_check.py` — use degradation.py for 4 ImportError blocks

### Not changed:
- Classification patterns, risk logic, audit trail, benchmarks, SBOM format, SARIF output
- The remaining 16 `except Exception` blocks in non-user-facing code

---

## Testing Plan

### New tests:
- `errors.py`: RegulaError hierarchy, exit_code attribute, subclass behaviour
- `doctor.py`: each check returns correct PASS/WARN/FAIL for mocked conditions
- `self_test.py`: all 6 built-in assertions pass
- `degradation.py`: check_optional returns correct bool, warns once per package
- Path validation: `check`, `classify --file`, `gap --project` with non-existent paths raise PathError
- CLI wrapper: RegulaError caught and printed to stderr, KeyboardInterrupt exits 130
- JSON envelope: output contains regula_version, command, timestamp, data keys
- `init --dry-run`: produces output, creates no files

### Existing tests:
- All 152 existing tests must still pass
- No changes to test infrastructure

---

## Success Criteria

- [ ] Zero Python tracebacks visible to users for known error conditions
- [ ] `regula` (no args) exits 2 (usage error), not 0
- [ ] `regula check /nonexistent` exits 2 (tool error) with "Path does not exist" message
- [ ] `regula classify --file /nonexistent.txt` exits 2 (tool error) with clean error
- [ ] `regula check .` with BLOCK findings exits 1 (findings), not 2
- [ ] `regula doctor` runs all checks, exits 0 on healthy system
- [ ] `regula self-test` passes all 6 assertions in < 1 second
- [ ] `regula init --dry-run` shows project analysis without creating files
- [ ] All `--format json` output wrapped in consistent envelope
- [ ] All 152+ existing tests pass
- [ ] 2 new subcommands (doctor, self-test) bring total to 22

---

## Verified Numbers (all from grep/wc on 2026-03-28)

- Current subcommands: 20
- `sys.exit()` in cli.py: 13
- `sys.exit()` across all scripts/: 33
- `except Exception` total: 22 (6 in user-facing code, 16 in internal)
- `except ImportError` total: 14 across 7 files
- `json.dumps` in cli.py: 13
- `input()` without EOFError in init_wizard: 2 calls, 0 handlers
- `print()` in scripts/: 282 total, 36 to stderr
- Naming precedent: `npm doctor`, `brew doctor` both verified
- No major CLI uses `quickstart` as a command (verified: git, npm, gh, kubectl)
