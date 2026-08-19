# regula-ignore
"""The governance hook's degraded mode had no test at all.

`hooks/pre_tool_use.py` blocks Article 5 practices and denies secret-bearing
tool calls. When `scripts/` cannot be imported it installs stubs and FAILS
OPEN, allowing everything with one line on stderr. That trade-off is
deliberate and documented at the import site: a partial install should not
brick an entire session.

Nothing tested it. So on 2026-08-15 a legitimate dead-code deletion in
`scripts/classify_risk.py` silently turned the hook into a permit-everything
pass, and the only reason anyone noticed was that seven unrelated tests
failed. The control itself was silent.

These tests do not change the trade-off. They pin it, so that:
  - fail-open stays deliberate rather than becoming an accident,
  - the stderr warning a user relies on to know the control is off keeps
    being printed,
  - and the normal path still denies, which is the half that matters.

The third test is the one that would have caught the original break: every
name the try block imports must have a stub in the except block. Two did not
(`is_training_activity`, `generate_observations`), and fail-open worked only
because both call sites happen to sit inside a bare `except Exception: pass`.

hooks/ is gitignored local development tooling and is not distributed in the
public repository or package. These four tests therefore run only when the
local hook is present and are explicitly skipped in a clean checkout. Public
installer coverage below separately prevents the CLI from advertising that
unshipped file. See LEDGER N114.
"""
import ast
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))
HOOK = REPO_ROOT / "hooks" / "pre_tool_use.py"


class SkippedLocalHook(Exception):
    """Fallback skip signal when pytest is unavailable to the custom runner."""


def _require_local_hook():
    if HOOK.is_file():
        return
    reason = "hooks/pre_tool_use.py is local tooling and is not distributed"
    try:
        import pytest
    except ImportError:
        raise SkippedLocalHook(reason)
    pytest.skip(reason)

# The fixture is built from character codes rather than written out, following
# the convention in .claude/rules/tests.md for synthetic values that would
# otherwise trip the hook while this file is being edited. Decoded, it is a
# two-word Article 5 term the shipped detector matches.
_TRIGGER = ''.join(chr(c) for c in (
    115, 111, 99, 105, 97, 108, 32, 115, 99, 111, 114, 105, 110, 103))

PAYLOAD = {
    "tool_name": "Write",
    "tool_input": {
        "file_path": "scoring.py",
        "content": f"def rank(citizen):\n    return {_TRIGGER.replace(' ', '_')}(citizen)\n",
    },
}


def _run(hook_path, payload, env=None, cwd=None):
    return subprocess.run(
        [sys.executable, str(hook_path)],
        input=json.dumps(payload), capture_output=True, text=True,
        timeout=120, env=env, cwd=cwd)


def test_hook_denies_a_prohibited_practice_on_the_normal_path():
    """The control must work before its degraded mode is worth discussing."""
    _require_local_hook()
    proc = _run(HOOK, PAYLOAD, cwd=str(REPO_ROOT))
    assert proc.stdout.strip(), f"the hook printed nothing: {proc.stderr!r}"
    out = json.loads(proc.stdout)
    decision = out["hookSpecificOutput"].get("permissionDecision")
    assert decision == "deny", (
        "the hook allowed an Article 5 practice on the healthy path: "
        f"{proc.stdout!r} {proc.stderr!r}")
    assert proc.returncode == 2, f"expected exit 2, got {proc.returncode}"
    print("  PASS  hook denies on the normal path")


def test_hook_fails_open_and_says_so_when_scripts_cannot_be_imported():
    """The documented trade-off, pinned in both halves.

    The hook is copied alone into a temp tree with no sibling `scripts/`, and
    PYTHONPATH is cleared. That is a real partial install, not a patched hook:
    the module's own `sys.path.insert(..., parent.parent / "scripts")`
    resolves to a directory that does not exist, exactly as it would for a
    user whose install dropped the package.

    Allowing is deliberate. Allowing *silently* is not: the stderr warning is
    the only signal a user gets that the control is off, so it is part of the
    contract rather than decoration.
    """
    _require_local_hook()
    with tempfile.TemporaryDirectory() as d:
        broken = Path(d) / "hooks"
        broken.mkdir()
        shutil.copy2(HOOK, broken / "pre_tool_use.py")
        env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
        proc = _run(broken / "pre_tool_use.py", PAYLOAD, env=env, cwd=d)

    assert proc.stdout.strip(), (
        f"the hook printed nothing in degraded mode: {proc.stderr!r}")
    out = json.loads(proc.stdout)
    decision = out["hookSpecificOutput"].get("permissionDecision")
    assert decision == "allow", (
        "the fail-open path did not allow, so a partial install now bricks "
        f"the session instead: {proc.stdout!r} {proc.stderr!r}")
    assert proc.returncode == 0, (
        f"expected exit 0, got {proc.returncode}: {proc.stderr!r}")
    assert "governance checks disabled" in proc.stderr, (
        "fail-open went silent. A user cannot tell the control is off, which "
        f"is the whole reason the warning exists. stderr: {proc.stderr!r}")
    assert "fail-open" in proc.stderr, proc.stderr
    print("  PASS  hook fails open, exits 0, and warns on stderr")


def _guarded_import_block():
    tree = ast.parse(HOOK.read_text(encoding="utf-8"))
    guarded = next(
        (n for n in ast.walk(tree)
         if isinstance(n, ast.Try)
         and any(isinstance(s, ast.ImportFrom) for s in n.body)),
        None)
    assert guarded is not None, "no guarded import block found in the hook"
    imported = set()
    for stmt in guarded.body:
        if isinstance(stmt, (ast.Import, ast.ImportFrom)):
            for alias in stmt.names:
                imported.add(alias.asname or alias.name.split(".")[0])
    assert imported, "the guarded block binds no names, so this test is vacuous"
    return tree, guarded, imported


def test_every_imported_name_has_a_fail_open_stub():
    """The test that would have caught the 2026-08-15 break.

    Read the module's own source: collect the names bound by the guarded
    imports, then the names bound in the handler. A name in the first set and
    not the second is a NameError waiting for the degraded path, and whether
    it surfaces at all depends on whether its call site happens to sit inside
    a broad except.
    """
    _require_local_hook()
    _, guarded, imported = _guarded_import_block()

    stubbed = set()
    for handler in guarded.handlers:
        for stmt in ast.walk(ast.Module(body=handler.body, type_ignores=[])):
            if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef,
                                 ast.ClassDef)):
                stubbed.add(stmt.name)
            elif isinstance(stmt, ast.Assign):
                for tgt in stmt.targets:
                    if isinstance(tgt, ast.Name):
                        stubbed.add(tgt.id)

    missing = sorted(imported - stubbed)
    assert not missing, (
        f"imported under the try but not stubbed in the except: {missing}. "
        "In fail-open mode each is a NameError, and whether the hook degrades "
        "or crashes then depends on whether the call site happens to be "
        "wrapped in a broad except.")
    print(f"  PASS  all {len(imported)} guarded imports have fail-open stubs")


def test_the_hook_imports_no_name_it_never_uses():
    """An unused import is an untested dependency edge.

    One name was imported here and called nowhere. Because hooks/ is
    gitignored, a repo-wide grep read it as dead in scripts/; deleting it
    broke this import and the hook went to permit-everything. The name was
    never needed. Nothing in this file exercised it, so nothing here failed
    when it was wrong: the failure surfaced seven tests away.
    """
    _require_local_hook()
    tree, _, imported = _guarded_import_block()
    used = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    used |= {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}

    unused = sorted(imported - used)
    assert not unused, (
        f"the hook imports names it never uses: {unused}. Each is a coupling "
        "to scripts/ that nothing in this hook tests, and hooks/ is gitignored "
        "so scripts/ cannot see the consumer either. Import only what is called.")
    print(f"  PASS  all {len(imported)} guarded imports are actually used")


def test_public_installer_advertises_only_shipped_integrations():
    """Public install routes must not point to gitignored local hook files."""
    from install import PLATFORMS

    assert set(PLATFORMS) == {"pre-commit", "git-hooks"}, (
        "installer advertised an unsupported route: "
        f"{sorted(PLATFORMS)}")
    print("  PASS  public installer advertises only shipped integrations")


def test_cli_rejects_unshipped_hook_platform_without_a_traceback():
    """A removed hook route is a usage error, not a KeyError or false success."""
    proc = subprocess.run(
        [sys.executable, "-m", "scripts.cli", "install", "claude-code"],
        capture_output=True, text=True, timeout=120, cwd=str(REPO_ROOT))
    assert proc.returncode == 2, proc
    assert "invalid choice" in proc.stderr, proc.stderr
    assert "Traceback" not in proc.stderr, proc.stderr
    assert not proc.stdout.strip(), proc.stdout
    print("  PASS  unshipped hook platform is rejected as a usage error")


def test_doctor_detects_regula_content_not_editor_directories():
    """An editor directory alone is not evidence that Regula is installed."""
    from doctor import _check_hooks

    previous = Path.cwd()
    with tempfile.TemporaryDirectory() as empty_dir:
        empty = Path(empty_dir)
        (empty / ".claude" / "hooks").mkdir(parents=True)
        try:
            os.chdir(empty)
            absent = _check_hooks()
        finally:
            os.chdir(previous)
    assert absent["status"] == "INFO", absent

    with tempfile.TemporaryDirectory() as configured_dir:
        configured = Path(configured_dir)
        (configured / ".pre-commit-config.yaml").write_text(
            "repos:\n  - repo: local\n    hooks:\n      - id: regula-check\n",
            encoding="utf-8")
        try:
            os.chdir(configured)
            present = _check_hooks()
        finally:
            os.chdir(previous)
    assert present["status"] == "PASS", present
    assert "pre-commit framework" in present["detail"], present
    print("  PASS  doctor requires actual Regula integration content")


if __name__ == "__main__":
    for t in (test_hook_denies_a_prohibited_practice_on_the_normal_path,
              test_hook_fails_open_and_says_so_when_scripts_cannot_be_imported,
              test_every_imported_name_has_a_fail_open_stub,
              test_the_hook_imports_no_name_it_never_uses):
        t()
