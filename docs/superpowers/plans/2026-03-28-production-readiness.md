# Production Readiness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix error handling, add diagnostics, and standardise JSON output so Regula is reliable in CI/CD pipelines and compliance workflows.

**Architecture:** Two waves. Wave 1 creates error infrastructure (`errors.py`), wraps CLI in a top-level handler, and fixes 7 path validation bugs + 6 silent exception blocks. Wave 2 adds `doctor` and `self-test` commands, a graceful degradation utility, `init --dry-run`, and a JSON output envelope. All changes are stdlib-only.

**Tech Stack:** Python 3.10+ stdlib. No new dependencies. Test runner: `python3 tests/test_classification.py`.

**Spec:** `docs/superpowers/specs/2026-03-28-production-readiness-design.md`

**Verify command:** `python3 tests/test_classification.py`

---

## File Map

### New files
| File | Responsibility |
|------|---------------|
| `scripts/errors.py` | Custom exception hierarchy (RegulaError, PathError, ConfigError, ParseError, DependencyError) |
| `scripts/doctor.py` | `regula doctor` — installation health checks (8 checks: Python, deps, policy, audit dir, hooks, config, security) |
| `scripts/self_test.py` | `regula self-test` — 6 built-in classification assertions |
| `scripts/degradation.py` | `check_optional()` utility for consistent optional dependency messaging |

### Modified files
| File | Changes |
|------|---------|
| `scripts/cli.py` | Top-level error handler, path validation in 6 commands, 2 new subcommands, JSON envelope helper, exit code fixes, git diff warning |
| `scripts/init_wizard.py` | EOFError handling (2 sites), `--dry-run` flag |
| `scripts/report.py` | Narrow 4 `except Exception` blocks to specific exceptions |
| `scripts/sbom.py` | Replace 3 `except ImportError` with `check_optional()` |
| `scripts/classify_risk.py` | Replace 1 `except ImportError` with `check_optional()` |
| `scripts/discover_ai_systems.py` | Replace 1 `except ImportError` with `check_optional()` |
| `scripts/framework_mapper.py` | Replace 1 `except ImportError` with `check_optional()` |
| `scripts/dependency_scan.py` | Replace 2 `except ImportError` with `check_optional()` |
| `scripts/ast_engine.py` | Replace 2 `except ImportError` with `check_optional()` |
| `scripts/compliance_check.py` | Replace 4 `except ImportError` with `check_optional()` |
| `tests/test_classification.py` | New tests for errors, path validation, doctor, self-test, degradation, JSON envelope |

---

## Wave 1: Error Handling Foundation

### Task 1: Custom Exception Hierarchy

**Files:**
- Create: `scripts/errors.py`
- Test: `tests/test_classification.py`

- [ ] **Step 1: Write failing tests for exception hierarchy**

Add to `tests/test_classification.py`:

```python
def test_regula_error_hierarchy():
    """Test custom exception classes exist with correct exit codes."""
    from scripts.errors import RegulaError, PathError, ConfigError, ParseError, DependencyError

    # Base class
    e = RegulaError("test")
    assert str(e) == "test"
    assert e.exit_code == 1

    # Subclasses — all tool errors (exit 2)
    assert PathError("x").exit_code == 2
    assert ConfigError("x").exit_code == 2
    assert ParseError("x").exit_code == 2
    assert DependencyError("x").exit_code == 2

    # All inherit from RegulaError
    assert isinstance(PathError("x"), RegulaError)
    assert isinstance(ConfigError("x"), RegulaError)
    assert isinstance(ParseError("x"), RegulaError)
    assert isinstance(DependencyError("x"), RegulaError)

    passed("Error hierarchy: all classes exist with correct exit codes")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 tests/test_classification.py 2>&1 | tail -5`
Expected: FAIL — `ModuleNotFoundError: No module named 'scripts.errors'`

- [ ] **Step 3: Create errors.py**

Create `scripts/errors.py`:

```python
"""Custom exception hierarchy for Regula CLI.

Exit code convention (research-validated, scanner industry standard):
  0 = success, no actionable findings
  1 = findings detected (BLOCK/WARN/prohibited)
  2 = tool error (bad config, missing path, parse failure)
"""


class RegulaError(Exception):
    """Base for all Regula errors. CLI catches this and prints cleanly."""
    exit_code = 1


class PathError(RegulaError):
    """Target path doesn't exist or isn't accessible."""
    exit_code = 2


class ConfigError(RegulaError):
    """Bad or missing configuration file."""
    exit_code = 2


class ParseError(RegulaError):
    """File couldn't be parsed (bad JSON, YAML, syntax)."""
    exit_code = 2


class DependencyError(RegulaError):
    """Optional dependency missing and needed for requested operation."""
    exit_code = 2
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 tests/test_classification.py 2>&1 | tail -5`
Expected: PASS

- [ ] **Step 5: Run full suite to check for regressions**

Run: `python3 tests/test_classification.py 2>&1 | tail -1`
Expected: `All tests passed!`

- [ ] **Step 6: Commit**

```bash
git add scripts/errors.py tests/test_classification.py
git commit -m "feat: custom exception hierarchy for CLI error handling"
```

---

### Task 2: CLI Top-Level Error Handler + Exit Code Fixes

**Files:**
- Modify: `scripts/cli.py` (lines 586-800: main function)
- Test: `tests/test_classification.py`

- [ ] **Step 1: Write failing tests for CLI error handling**

Add to `tests/test_classification.py`:

```python
def test_cli_exit_codes():
    """Test CLI exit code convention: 0=success, 1=findings, 2=tool error."""
    import subprocess

    # No args = usage error = exit 2
    r = subprocess.run(["python3", "scripts/cli.py"], capture_output=True, text=True)
    assert r.returncode == 2, f"No-args should exit 2, got {r.returncode}"

    # Non-existent path = tool error = exit 2
    r = subprocess.run(["python3", "scripts/cli.py", "check", "/nonexistent/path"],
                       capture_output=True, text=True)
    assert r.returncode == 2, f"Bad path should exit 2, got {r.returncode}"
    assert "Path does not exist" in r.stderr, f"Should print error to stderr, got: {r.stderr}"

    # classify --file with non-existent file = exit 2
    r = subprocess.run(["python3", "scripts/cli.py", "classify", "--file", "/nonexistent.txt"],
                       capture_output=True, text=True)
    assert r.returncode == 2, f"Bad file should exit 2, got {r.returncode}"
    assert "Path does not exist" in r.stderr or "does not exist" in r.stderr

    # Clean scan = exit 0
    r = subprocess.run(["python3", "scripts/cli.py", "classify", "--input", "print('hello')"],
                       capture_output=True, text=True)
    assert r.returncode == 0, f"Clean input should exit 0, got {r.returncode}"

    passed("CLI exit codes: 0=success, 1=findings, 2=tool error")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 tests/test_classification.py 2>&1 | grep "exit codes"`
Expected: FAIL — no-args exits 0 instead of 2, bad path exits 0 instead of 2

- [ ] **Step 3: Implement CLI changes**

In `scripts/cli.py`, make these changes:

**3a. Add import at top of file:**
```python
from errors import RegulaError, PathError
```

**3b. Add path validation helper after imports:**
```python
def _validate_path(path_str: str) -> Path:
    """Validate a path exists. Raises PathError if not."""
    p = Path(path_str)
    if not p.exists():
        raise PathError(f"Path does not exist: {path_str}")
    return p
```

**3c. Add path validation to cmd_check (line ~87):**
At the start of `cmd_check`, before `project = str(Path(args.path).resolve())`:
```python
_validate_path(args.path)
```

**3d. Add path validation to cmd_classify (line ~195):**
Inside the `if args.file:` block, before `text = Path(args.file).read_text(...)`:
```python
_validate_path(args.file)
```

**3e. Add path validation to cmd_gap (line ~473):**
At the start, before `assessment = assess_compliance(args.project, ...)`:
```python
if args.project != ".":
    _validate_path(args.project)
```

**3f. Add path validation to cmd_deps (line ~572):**
At the start:
```python
if args.project != ".":
    _validate_path(args.project)
```

**3g. Add path validation to cmd_sbom (line ~529):**
At the start:
```python
if args.project != ".":
    _validate_path(args.project)
```

**3h. Add path validation to cmd_discover (line ~258):**
At the start:
```python
if args.project != ".":
    _validate_path(args.project)
```

**3i. Add path validation to cmd_report (line ~221):**
At the start:
```python
if hasattr(args, 'project') and args.project != ".":
    _validate_path(args.project)
```

**3j. Change no-args exit from 0 to 2 (line 794):**
```python
# Before:
    sys.exit(0)
# After:
    sys.exit(2)
```

**3k. Change BLOCK findings exit from 2 to 1 (line 189):**
```python
# Before:
        sys.exit(2)
# After:
        sys.exit(1)
```

**3l. Change compromised deps exit from 2 to 1 (line 581):**
```python
# Before:
        sys.exit(2)
# After:
        sys.exit(1)
```

**3m. Wrap main() dispatch in error handler (line ~794, after `args.func(args)`):**
Replace the last section of `main()`:
```python
    if not args.command:
        parser.print_help()
        sys.exit(2)

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

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 tests/test_classification.py 2>&1 | grep "exit codes"`
Expected: PASS

- [ ] **Step 5: Run full suite**

Run: `python3 tests/test_classification.py 2>&1 | tail -1`
Expected: `All tests passed!`

- [ ] **Step 6: Verify each command manually**

```bash
python3 scripts/cli.py 2>/dev/null; echo "No args: $?"           # Should be 2
python3 scripts/cli.py check /nonexistent 2>/dev/null; echo "Bad path: $?"  # Should be 2
python3 scripts/cli.py deps --project /nonexistent 2>/dev/null; echo "Bad deps: $?"  # Should be 2
python3 scripts/cli.py sbom --project /nonexistent 2>/dev/null; echo "Bad sbom: $?"  # Should be 2
python3 scripts/cli.py classify --input "print('hi')" >/dev/null; echo "Clean: $?"  # Should be 0
```

- [ ] **Step 7: Commit**

```bash
git add scripts/cli.py tests/test_classification.py
git commit -m "fix: path validation and exit codes (0=success, 1=findings, 2=tool error)"
```

---

### Task 3: Git Diff Fallback Warning

**Files:**
- Modify: `scripts/cli.py` (line 42-44)

- [ ] **Step 1: Change silent pass to warning**

At line 42-44 in `scripts/cli.py`, change:
```python
    except (subprocess.SubprocessError, FileNotFoundError):
        pass
    return []  # Empty = scan all files (fallback)
```
to:
```python
    except (subprocess.SubprocessError, FileNotFoundError):
        print("Note: git not available, scanning all files", file=sys.stderr)
    return []  # Empty = scan all files (fallback)
```

- [ ] **Step 2: Run full test suite**

Run: `python3 tests/test_classification.py 2>&1 | tail -1`
Expected: `All tests passed!`

- [ ] **Step 3: Commit**

```bash
git add scripts/cli.py
git commit -m "fix: warn when git unavailable for diff mode"
```

---

### Task 4: Silent Exception Cleanup (report.py + init_wizard.py)

**Files:**
- Modify: `scripts/report.py` (lines 124, 142, 183, 692)
- Modify: `scripts/init_wizard.py` (lines 89, 120, 140, 156)

- [ ] **Step 1: Narrow report.py exception blocks**

In `scripts/report.py`:

Line 124: Change `except Exception:` to `except (ValueError, KeyError, AttributeError):`
Line 142: Change `except Exception:` to `except (ValueError, KeyError, AttributeError):`
Line 183: Change `except Exception:` to `except (ValueError, KeyError, TypeError):`
Line 692: Change `except Exception:` to `except (OSError, ValueError, KeyError):`

- [ ] **Step 2: Fix init_wizard.py exception blocks and add EOFError handling**

Line 89: Change `except Exception as e:` to `except (OSError, ImportError) as e:`
Line 156: Change `except Exception as e:` to `except (OSError, PermissionError) as e:`

Line 120: Wrap input() call:
```python
            try:
                answer = input("  Create default regula-policy.yaml? [Y/n] ").strip().lower()
            except EOFError:
                answer = "y"  # Default to yes in non-interactive mode
```

Line 140: Wrap input() call:
```python
            try:
                choice = input(f"  Install hooks for {primary}? [Y/n/number] ").strip().lower()
            except EOFError:
                choice = "y"  # Default to yes in non-interactive mode
```

- [ ] **Step 3: Run full test suite**

Run: `python3 tests/test_classification.py 2>&1 | tail -1`
Expected: `All tests passed!`

- [ ] **Step 4: Commit**

```bash
git add scripts/report.py scripts/init_wizard.py
git commit -m "fix: narrow exception handlers, add EOFError handling for CI"
```

---

## Wave 2: New Features

### Task 5: Graceful Degradation Utility

**Files:**
- Create: `scripts/degradation.py`
- Test: `tests/test_classification.py`

- [ ] **Step 1: Write failing tests**

Add to `tests/test_classification.py`:

```python
def test_graceful_degradation():
    """Test check_optional utility for optional dependency messaging."""
    from scripts.degradation import check_optional, _warned

    # Reset warning tracker
    _warned.clear()

    # stdlib module should return True
    assert check_optional("json", "JSON support", "pip install json") is True

    # Non-existent module should return False
    import io
    stderr_capture = io.StringIO()
    import sys
    old_stderr = sys.stderr
    sys.stderr = stderr_capture
    result = check_optional("nonexistent_package_xyz", "test feature", "pip install xyz")
    sys.stderr = old_stderr
    assert result is False
    assert "nonexistent_package_xyz" in stderr_capture.getvalue()

    # Second call should NOT warn again
    stderr_capture2 = io.StringIO()
    sys.stderr = stderr_capture2
    check_optional("nonexistent_package_xyz", "test feature", "pip install xyz")
    sys.stderr = old_stderr
    assert stderr_capture2.getvalue() == "", "Should not warn twice for same package"

    passed("Graceful degradation: check_optional works correctly")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 tests/test_classification.py 2>&1 | grep "degradation"`
Expected: FAIL

- [ ] **Step 3: Create degradation.py**

Create `scripts/degradation.py`:

```python
"""Graceful degradation for optional dependencies.

Provides consistent messaging when optional packages are unavailable.
Warns once per package per process to avoid spam.
"""

import importlib
import sys

_warned: set = set()


def check_optional(package_name: str, feature: str, install_hint: str) -> bool:
    """Check if an optional package is importable.

    Returns True if available, False if not.
    Prints one-line guidance to stderr on first miss per package per process.
    """
    try:
        importlib.import_module(package_name)
        return True
    except ImportError:
        if package_name not in _warned:
            _warned.add(package_name)
            print(f"Note: {package_name} not installed — {feature} ({install_hint})",
                  file=sys.stderr)
        return False
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 tests/test_classification.py 2>&1 | grep "degradation"`
Expected: PASS

- [ ] **Step 5: Run full suite**

Run: `python3 tests/test_classification.py 2>&1 | tail -1`
Expected: `All tests passed!`

- [ ] **Step 6: Commit**

```bash
git add scripts/degradation.py tests/test_classification.py
git commit -m "feat: graceful degradation utility for optional dependencies"
```

---

### Task 6: Replace ImportError Blocks with check_optional

**Files:**
- Modify: `scripts/sbom.py` (3 blocks), `scripts/classify_risk.py` (1), `scripts/discover_ai_systems.py` (1), `scripts/framework_mapper.py` (1), `scripts/dependency_scan.py` (2), `scripts/ast_engine.py` (2), `scripts/compliance_check.py` (4)

- [ ] **Step 1: Replace all 14 blocks**

For each file, find each `try: import X / except ImportError:` pattern and replace with the `check_optional` pattern. The exact replacement depends on the existing code — read each block, determine what the fallback does, and use `check_optional()` with an appropriate message.

General pattern:
```python
# Before:
try:
    import yaml
except ImportError:
    yaml = None

# After:
from degradation import check_optional
if check_optional("yaml", "using fallback YAML parser", "pip install regula[yaml]"):
    import yaml
else:
    yaml = None
```

Files and counts:
- `scripts/sbom.py`: 3 blocks (lines 29, 41, 64)
- `scripts/classify_risk.py`: 1 block (line 440)
- `scripts/discover_ai_systems.py`: 1 block (line 301)
- `scripts/framework_mapper.py`: 1 block (line 64)
- `scripts/dependency_scan.py`: 2 blocks (lines 674, 681)
- `scripts/ast_engine.py`: 2 blocks (lines 236, 976)
- `scripts/compliance_check.py`: 4 blocks (lines 38, 45, 52, 63)

- [ ] **Step 2: Run full test suite**

Run: `python3 tests/test_classification.py 2>&1 | tail -1`
Expected: `All tests passed!`

- [ ] **Step 3: Verify degradation messages appear**

```bash
# This should show a note about tree-sitter (if not installed)
python3 -c "from scripts.degradation import check_optional; check_optional('tree_sitter', 'regex fallback', 'pip install regula[ast]')" 2>&1
```

- [ ] **Step 4: Commit**

```bash
git add scripts/sbom.py scripts/classify_risk.py scripts/discover_ai_systems.py scripts/framework_mapper.py scripts/dependency_scan.py scripts/ast_engine.py scripts/compliance_check.py
git commit -m "refactor: replace 14 scattered ImportError blocks with check_optional"
```

---

### Task 7: Doctor Command

**Files:**
- Create: `scripts/doctor.py`
- Modify: `scripts/cli.py` (add subcommand)
- Test: `tests/test_classification.py`

- [ ] **Step 1: Write failing tests**

Add to `tests/test_classification.py`:

```python
def test_doctor_command():
    """Test regula doctor runs and returns structured results."""
    import subprocess

    # Doctor should run and exit 0 on a healthy system
    r = subprocess.run(["python3", "scripts/cli.py", "doctor"],
                       capture_output=True, text=True)
    assert r.returncode == 0, f"Doctor should exit 0, got {r.returncode}"
    assert "Python" in r.stdout, "Should check Python version"
    assert "passed" in r.stdout.lower() or "PASS" in r.stdout, "Should show pass/fail results"

    # JSON format should work
    r = subprocess.run(["python3", "scripts/cli.py", "doctor", "--format", "json"],
                       capture_output=True, text=True)
    assert r.returncode == 0
    import json
    data = json.loads(r.stdout)
    assert "checks" in data or "data" in data, "JSON output should have checks"

    passed("Doctor command: runs, exits 0, supports JSON")
```

- [ ] **Step 2: Run test to verify it fails**

Expected: FAIL — `doctor` command not found

- [ ] **Step 3: Create doctor.py**

Create `scripts/doctor.py`:

```python
"""regula doctor — installation health check.

Checks: Python version, optional deps, policy file, audit dir,
hooks, config validation, security.

Pattern: npm doctor / brew doctor.
"""

import importlib
import json
import os
import sys
from datetime import datetime
from pathlib import Path


def _check_python():
    v = sys.version_info
    ok = v >= (3, 10)
    version_str = f"{v.major}.{v.minor}.{v.micro}"
    return {
        "name": "Python version",
        "status": "PASS" if ok else "FAIL",
        "detail": f"Python {version_str} ({'>=' if ok else '<'} 3.10 required)",
    }


def _check_optional_dep(name, pip_extra):
    try:
        mod = importlib.import_module(name)
        version = getattr(mod, "__version__", getattr(mod, "version", "installed"))
        return {"name": name, "status": "PASS", "detail": f"{name} {version}"}
    except ImportError:
        return {"name": name, "status": "WARN",
                "detail": f"{name} not installed (pip install regula[{pip_extra}])"}


def _check_policy():
    for loc in [Path("regula-policy.yaml"), Path.home() / ".regula" / "regula-policy.yaml"]:
        if loc.exists():
            try:
                loc.read_text(encoding="utf-8")
                return {"name": "Policy file", "status": "PASS", "detail": str(loc)}
            except OSError as e:
                return {"name": "Policy file", "status": "FAIL", "detail": f"{loc}: {e}"}
    return {"name": "Policy file", "status": "WARN", "detail": "Not found (optional)"}


def _check_audit_dir():
    audit_dir = Path.home() / ".regula" / "audit"
    if audit_dir.exists():
        if os.access(str(audit_dir), os.W_OK):
            return {"name": "Audit directory", "status": "PASS",
                    "detail": f"{audit_dir} (writable)"}
        return {"name": "Audit directory", "status": "FAIL",
                "detail": f"{audit_dir} (not writable)"}
    try:
        audit_dir.mkdir(parents=True, exist_ok=True)
        return {"name": "Audit directory", "status": "PASS",
                "detail": f"{audit_dir} (created)"}
    except OSError as e:
        return {"name": "Audit directory", "status": "FAIL", "detail": str(e)}


def _check_hooks():
    hook_locations = [
        Path(".claude") / "hooks",
        Path(".cursor"),
        Path(".windsurf"),
    ]
    for loc in hook_locations:
        if loc.exists() and any(loc.glob("*.py")):
            return {"name": "Hooks", "status": "PASS", "detail": f"Found in {loc}"}
    return {"name": "Hooks", "status": "WARN",
            "detail": "Not detected (run: regula install claude-code)"}


def _check_config_validation():
    policy_path = Path("regula-policy.yaml")
    if not policy_path.exists():
        return {"name": "Config validation", "status": "WARN", "detail": "No policy file to validate"}
    try:
        content = policy_path.read_text(encoding="utf-8")
        # Basic checks
        issues = []
        if "ai_officer:" not in content and "ai_officer :" not in content:
            issues.append("governance.ai_officer missing")
        if issues:
            return {"name": "Config validation", "status": "WARN",
                    "detail": "; ".join(issues)}
        return {"name": "Config validation", "status": "PASS", "detail": "Valid"}
    except OSError as e:
        return {"name": "Config validation", "status": "FAIL", "detail": str(e)}


def _check_security():
    issues = []
    gitignore = Path(".gitignore")
    if gitignore.exists():
        content = gitignore.read_text(encoding="utf-8", errors="ignore")
        if "audit" not in content.lower() and ".regula" not in content:
            issues.append(".gitignore missing audit trail patterns")
    audit_dir = Path.home() / ".regula" / "audit"
    if audit_dir.exists() and sys.platform != "win32":
        for f in audit_dir.glob("*.jsonl"):
            mode = f.stat().st_mode
            if mode & 0o004:  # world-readable
                issues.append(f"{f.name} is world-readable")
            break  # Check first file only
    if issues:
        return {"name": "Security", "status": "WARN", "detail": "; ".join(issues)}
    return {"name": "Security", "status": "PASS", "detail": "OK"}


def run_doctor(format_type="text"):
    checks = [
        _check_python(),
        _check_optional_dep("yaml", "yaml"),
        _check_optional_dep("tree_sitter", "ast"),
        _check_optional_dep("tree_sitter_javascript", "ast"),
        _check_optional_dep("tree_sitter_typescript", "ast"),
        _check_policy(),
        _check_audit_dir(),
        _check_hooks(),
        _check_config_validation(),
        _check_security(),
    ]

    if format_type == "json":
        passed_count = sum(1 for c in checks if c["status"] == "PASS")
        warn_count = sum(1 for c in checks if c["status"] == "WARN")
        fail_count = sum(1 for c in checks if c["status"] == "FAIL")
        return {
            "checks": checks,
            "summary": {"passed": passed_count, "warnings": warn_count, "failures": fail_count},
            "healthy": fail_count == 0,
        }

    # Text format
    print("\nRegula Doctor\n")
    for c in checks:
        status = c["status"]
        icon = {"PASS": "PASS", "WARN": "WARN", "FAIL": "FAIL"}[status]
        print(f"  {icon}  {c['detail']}")

    passed_count = sum(1 for c in checks if c["status"] == "PASS")
    warn_count = sum(1 for c in checks if c["status"] == "WARN")
    fail_count = sum(1 for c in checks if c["status"] == "FAIL")
    print(f"\n{passed_count} passed, {warn_count} warnings, {fail_count} failures\n")

    return fail_count == 0


if __name__ == "__main__":
    ok = run_doctor()
    sys.exit(0 if ok else 1)
```

- [ ] **Step 4: Wire into cli.py**

Add subcommand in `main()`, after the last `add_parser` block:

```python
p_doctor = subparsers.add_parser("doctor", help="Check installation health")
p_doctor.add_argument("--format", "-f", choices=["text", "json"], default="text")
p_doctor.set_defaults(func=cmd_doctor)
```

Add command handler:

```python
def cmd_doctor(args):
    from doctor import run_doctor
    result = run_doctor(format_type=args.format)
    if args.format == "json":
        print(json.dumps(result, indent=2))
        sys.exit(0 if result["healthy"] else 1)
    else:
        sys.exit(0 if result else 1)
```

- [ ] **Step 5: Run test to verify it passes**

Run: `python3 tests/test_classification.py 2>&1 | grep "Doctor"`
Expected: PASS

- [ ] **Step 6: Run full suite**

Run: `python3 tests/test_classification.py 2>&1 | tail -1`
Expected: `All tests passed!`

- [ ] **Step 7: Commit**

```bash
git add scripts/doctor.py scripts/cli.py tests/test_classification.py
git commit -m "feat: regula doctor command (installation health check)"
```

---

### Task 8: Self-Test Command

**Files:**
- Create: `scripts/self_test.py`
- Modify: `scripts/cli.py` (add subcommand)
- Test: `tests/test_classification.py`

- [ ] **Step 1: Write failing test**

Add to `tests/test_classification.py`:

```python
def test_self_test_command():
    """Test regula self-test runs built-in assertions."""
    import subprocess

    r = subprocess.run(["python3", "scripts/cli.py", "self-test"],
                       capture_output=True, text=True)
    assert r.returncode == 0, f"Self-test should exit 0, got {r.returncode}. stderr: {r.stderr}"
    assert "PASS" in r.stdout, "Should show PASS results"
    assert "6/6" in r.stdout or "passed" in r.stdout.lower(), "Should pass all 6 assertions"

    passed("Self-test command: runs, exits 0, all assertions pass")
```

- [ ] **Step 2: Run test to verify it fails**

Expected: FAIL — `self-test` command not found

- [ ] **Step 3: Create self_test.py**

Create `scripts/self_test.py`:

```python
"""regula self-test — verify installation works.

Runs 6 hardcoded assertions against the classification engine.
No file I/O. Target: < 1 second.

Note: This is a Regula-specific design choice, not a standard CLI pattern.
Justified because Regula produces compliance evidence that organisations
rely on for EU AI Act obligations.
"""

import sys
import time


def run_self_test():
    from classify_risk import classify
    from credential_check import check_credentials
    from framework_mapper import map_to_frameworks

    results = []
    start = time.time()

    # 1. Prohibited detection
    r = classify("social_credit_scoring_system")
    ok = r.tier.value == "prohibited"
    results.append(("Prohibited practice detection", ok))

    # 2. High-risk detection
    r = classify("import torch\nmodel = BiometricClassifier()")
    ok = r.tier.value == "high_risk"
    results.append(("High-risk classification", ok))

    # 3. Clean input
    r = classify("print('hello world')")
    ok = r.tier.value == "minimal_risk"
    results.append(("Minimal-risk classification", ok))

    # 4. Credential detection
    creds = check_credentials("AKIAIOSFODNN7EXAMPLE")
    ok = len(creds) > 0
    results.append(("Credential detection", ok))

    # 5. Framework mapping
    mapping = map_to_frameworks([{"tier": "high_risk", "category": "biometric"}], "eu-ai-act")
    ok = isinstance(mapping, (list, dict))
    results.append(("Framework mapping", ok))

    # 6. Limited-risk detection
    r = classify("chatbot_interface = ChatBot(emotion_detection=True)")
    ok = r.tier.value == "limited_risk"
    results.append(("Limited-risk classification", ok))

    elapsed = time.time() - start

    # Print results
    print("\nRegula Self-Test\n")
    for name, ok in results:
        status = "PASS" if ok else "FAIL"
        print(f"  {status}  {name}")

    passed_count = sum(1 for _, ok in results if ok)
    total = len(results)
    print(f"\n{passed_count}/{total} passed in {elapsed:.1f}s\n")

    return all(ok for _, ok in results)


if __name__ == "__main__":
    ok = run_self_test()
    sys.exit(0 if ok else 1)
```

- [ ] **Step 4: Wire into cli.py**

Add subcommand:
```python
p_selftest = subparsers.add_parser("self-test", help="Verify installation works")
p_selftest.set_defaults(func=cmd_self_test)
```

Add handler:
```python
def cmd_self_test(args):
    from self_test import run_self_test
    ok = run_self_test()
    sys.exit(0 if ok else 1)
```

- [ ] **Step 5: Run test to verify it passes**

Run: `python3 tests/test_classification.py 2>&1 | grep "Self-test"`
Expected: PASS

- [ ] **Step 6: Run full suite**

Run: `python3 tests/test_classification.py 2>&1 | tail -1`
Expected: `All tests passed!`

- [ ] **Step 7: Verify timing**

```bash
time python3 scripts/cli.py self-test
```
Expected: < 1 second

- [ ] **Step 8: Commit**

```bash
git add scripts/self_test.py scripts/cli.py tests/test_classification.py
git commit -m "feat: regula self-test command (installation verification)"
```

---

### Task 9: Init Dry-Run Flag

**Files:**
- Modify: `scripts/init_wizard.py`
- Modify: `scripts/cli.py` (add --dry-run flag to init subparser)
- Test: `tests/test_classification.py`

- [ ] **Step 1: Write failing test**

Add to `tests/test_classification.py`:

```python
def test_init_dry_run():
    """Test regula init --dry-run shows analysis without creating files."""
    import subprocess
    import tempfile
    import os

    with tempfile.TemporaryDirectory() as tmpdir:
        r = subprocess.run(["python3", "scripts/cli.py", "init", "--dry-run", "--project", tmpdir],
                           capture_output=True, text=True)
        assert r.returncode == 0, f"Dry run should exit 0, got {r.returncode}. stderr: {r.stderr}"
        assert "dry run" in r.stdout.lower() or "no changes" in r.stdout.lower(), \
            "Should indicate dry run mode"
        # Should NOT create policy file
        assert not os.path.exists(os.path.join(tmpdir, "regula-policy.yaml")), \
            "Dry run should not create files"

    passed("Init dry-run: shows analysis, creates no files")
```

- [ ] **Step 2: Run test to verify it fails**

Expected: FAIL — `--dry-run` flag not recognised

- [ ] **Step 3: Add --dry-run to init_wizard.py**

In `scripts/init_wizard.py`, add to `run_init()`:

```python
def run_init(project_dir: Path, interactive: bool = False, dry_run: bool = False) -> None:
```

At the start of `run_init`, after the header print, add:
```python
    if dry_run:
        print("  (dry run — no changes will be made)\n")
        # Detect project
        platforms = _detect_platforms(project_dir)
        py_version = _detect_python()
        has_policy = _policy_exists(project_dir)
        scan = _run_quick_scan(project_dir)

        print(f"  Python:    {py_version}")
        print(f"  Policy:    {'exists' if has_policy else 'not found'}")
        print(f"  Platforms: {', '.join(platforms) if platforms else 'none detected'}")
        if "error" not in scan:
            total = scan.get("total_files", 0)
            prohibited = scan.get("prohibited", 0)
            high_risk = scan.get("high_risk", 0)
            limited = scan.get("limited_risk", 0)
            print(f"  AI files:  {total}")
            print(f"  Findings:  {prohibited} prohibited, {high_risk} high-risk, {limited} limited-risk")
        print()
        print("  Recommended next steps:")
        if not has_policy:
            print("    regula init              Set up policy and hooks")
        print("    regula check .           Full scan")
        print("    regula gap --project .   Compliance gap assessment")
        print()
        return
```

- [ ] **Step 4: Wire --dry-run into cli.py**

In cli.py, add flag to init subparser:
```python
p_init.add_argument("--dry-run", action="store_true", help="Show analysis without creating files")
```

In `cmd_init`, pass it through:
```python
def cmd_init(args):
    from init_wizard import run_init
    run_init(Path(args.project).resolve(), interactive=args.interactive,
             dry_run=getattr(args, 'dry_run', False))
```

- [ ] **Step 5: Run test to verify it passes**

Run: `python3 tests/test_classification.py 2>&1 | grep "dry"`
Expected: PASS

- [ ] **Step 6: Run full suite**

Run: `python3 tests/test_classification.py 2>&1 | tail -1`
Expected: `All tests passed!`

- [ ] **Step 7: Commit**

```bash
git add scripts/init_wizard.py scripts/cli.py tests/test_classification.py
git commit -m "feat: regula init --dry-run (read-only project analysis)"
```

---

### Task 10: JSON Output Envelope

**Files:**
- Modify: `scripts/cli.py` (add json_output helper, replace 13 json.dumps calls)
- Test: `tests/test_classification.py`

- [ ] **Step 1: Write failing test**

Add to `tests/test_classification.py`:

```python
def test_json_output_envelope():
    """Test --format json output has standard envelope with format_version."""
    import subprocess
    import json

    r = subprocess.run(["python3", "scripts/cli.py", "check", "--format", "json", "."],
                       capture_output=True, text=True)
    assert r.returncode in (0, 1), f"Unexpected exit: {r.returncode}"
    data = json.loads(r.stdout)

    assert "format_version" in data, "Missing format_version"
    assert data["format_version"] == "1.0", f"Expected format_version 1.0, got {data['format_version']}"
    assert "regula_version" in data, "Missing regula_version"
    assert "command" in data, "Missing command"
    assert data["command"] == "check", f"Expected command=check, got {data['command']}"
    assert "timestamp" in data, "Missing timestamp"
    assert "data" in data, "Missing data field"

    passed("JSON envelope: format_version, regula_version, command, timestamp, data all present")
```

- [ ] **Step 2: Run test to verify it fails**

Expected: FAIL — no envelope, raw array returned

- [ ] **Step 3: Add json_output helper to cli.py**

Near the top of cli.py, after imports:

```python
from datetime import datetime

VERSION = "1.1.0"

def json_output(command: str, data, exit_code: int = 0):
    """Standard JSON envelope for all --format json output."""
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

- [ ] **Step 4: Replace all 13 json.dumps calls**

Replace each `print(json.dumps(X, indent=2))` in cli.py with `json_output("command_name", X)`. The 13 locations (by line number):

1. Line 120: `json_output("check", findings)` — also pass exit_code based on findings
2. Line 124: Keep SARIF as-is (SARIF has its own schema)
3. Line 268: `json_output("discover", reg)`
4. Line 275: `json_output("discover", results)`
5. Line 329: `json_output("feed", articles)`
6. Line 359: `json_output("questionnaire", q)`
7. Line 373: `json_output("questionnaire", profile)`
8. Line 387: `json_output("baseline", result)`
9. Line 434: `json_output("compliance", history)`
10. Line 462: `json_output("gap", summary)`
11. Line 495: `json_output("benchmark", metrics)`
12. Line 524: `json_output("timeline", {"as_of": date.today().isoformat(), "timeline": TIMELINE})`
13. Line 552: `json_output("deps", findings)`

Note: SARIF output (line 124) keeps its own format — SARIF has a standardised schema that must not be wrapped.

- [ ] **Step 5: Run test to verify it passes**

Run: `python3 tests/test_classification.py 2>&1 | grep "envelope"`
Expected: PASS

- [ ] **Step 6: Run full suite**

Run: `python3 tests/test_classification.py 2>&1 | tail -1`
Expected: `All tests passed!`

- [ ] **Step 7: Verify JSON output manually**

```bash
python3 scripts/cli.py check --format json . 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['format_version'], d['command'])"
```
Expected: `1.0 check`

- [ ] **Step 8: Commit**

```bash
git add scripts/cli.py tests/test_classification.py
git commit -m "feat: JSON output envelope with format_version (Terraform pattern)"
```

---

## Final Integration

### Task 11: Full Verification Gate

- [ ] **Step 1: Run full test suite**

```bash
python3 tests/test_classification.py
```
Expected: All tests pass (152 existing + ~8 new = ~160 tests)

- [ ] **Step 2: Verify all success criteria**

```bash
echo "=== Success Criteria Verification ==="

# 1. No tracebacks
python3 scripts/cli.py check /nonexistent 2>&1 | grep -c "Traceback" && echo "FAIL: traceback found" || echo "PASS: no traceback"

# 2. No args = exit 2
python3 scripts/cli.py 2>/dev/null; echo "No-args exit: $? (expect 2)"

# 3. Bad path = exit 2
python3 scripts/cli.py check /nonexistent 2>/dev/null; echo "Bad path exit: $? (expect 2)"

# 4. Bad file = exit 2
python3 scripts/cli.py classify --file /nonexistent.txt 2>/dev/null; echo "Bad file exit: $? (expect 2)"

# 5. Doctor = exit 0
python3 scripts/cli.py doctor >/dev/null 2>&1; echo "Doctor exit: $? (expect 0)"

# 6. Self-test = exit 0
python3 scripts/cli.py self-test >/dev/null 2>&1; echo "Self-test exit: $? (expect 0)"

# 7. Init dry-run = exit 0
python3 scripts/cli.py init --dry-run >/dev/null 2>&1; echo "Init dry-run exit: $? (expect 0)"

# 8. JSON envelope
python3 scripts/cli.py check --format json . 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); assert d['format_version']=='1.0'; print('JSON envelope: PASS')"

# 9. Subcommand count
echo "Subcommands: $(grep 'add_parser(' scripts/cli.py | grep -oP '\"[a-z-]+\"' | wc -l) (expect 22)"
```

- [ ] **Step 3: Update README test count**

After all tests pass, update README.md line 384 and line 452 with the new test count.

- [ ] **Step 4: Final commit**

```bash
git add -A
git commit -m "feat: production readiness — error handling, doctor, self-test, JSON envelope

Wave 1: Custom exceptions, path validation, exit codes (0/1/2), silent exception cleanup
Wave 2: regula doctor, regula self-test, init --dry-run, JSON output envelope, graceful degradation

Exit codes follow scanner convention (ESLint, Semgrep, Bandit):
  0 = success, 1 = findings, 2 = tool error

JSON envelope follows Terraform pattern with format_version for schema evolution."
```

- [ ] **Step 5: Push**

```bash
git push origin main
```
