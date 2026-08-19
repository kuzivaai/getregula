# regula-ignore
"""Hostile-fixture sweep: every path-taking command against a malicious tree.

This is a BEHAVIOURAL check, deliberately run through the CLI as a
subprocess rather than against the walker functions in-process.

Why it exists
  The July 2026 security review fixed the same class of defect five times
  and each fix was verified against the *unit*. The commands kept failing:
  `sbom` had four guarded walkers and still leaked through a delegated
  call, and a commit claiming the FIFO denial-of-service was fixed was
  wrong when written because 15+ commands still hung. Grep-and-patch found
  instances; running every command against a hostile tree found the class.

  It also disproved a false finding. `benchmark` was reported as hanging on
  a FIFO, inferred from reading its bare read_text calls. It does not hang:
  those reads only ever receive paths that the guarded scan already
  approved. Measuring beat inferring in both directions.

What a failure here means
  HANG    a command blocked on a named pipe. A single FIFO committed to a
          repository is then a denial of service against any CI job that
          scans untrusted code.
  ESCAPE  content from outside the scan root reached the output. The tree
          under test can name any file on the host via a symlink.
  SKIPDIR a command walked into a directory in SKIP_DIRS. `.git` holds
          credentials and history; it is not scannable material.

The command list is DERIVED from the argument parser, never hardcoded. A
hardcoded list would have missed `handoff` — whose path argument is its
second positional, not its first — and `handoff` was the one command in
this sweep with a real, reproduced defect. Any command whose shape this
cannot construct fails the test rather than being quietly dropped.
"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

# Distinct markers so a failure says WHICH property broke.
CANARY_OUT_OF_ROOT = "RegulaCanaryOutOfRoot9f3a2b"
CANARY_SKIPDIR = "RegulaCanarySkipDir4c7e1d"

# A pattern the scanners actually look for, so a file that gets read has a
# chance of surfacing in output. A canary in a file nothing matches on
# would make this sweep pass for the wrong reason.
_BAIT = "import anthropic\nanthropic.messages.create(model='m', messages=[])\n"

_PATH_DESTS = {"path", "project", "project_path_positional"}

# Commands excluded from the sweep, each with a reason. Excluding a command
# is a decision that has to be written down: the test below asserts that
# every path-taking command is either swept or named here, so a new command
# cannot land in neither set.
EXCLUDED = {
    "install": "installs hooks into the user's environment, not the fixture",
    "init": "writes config and can prompt; mutates the fixture mid-sweep",
    "fix": "rewrites source files in place; makes the sweep order-dependent",
    "register": "writes to a registry outside the scan root",
    "attest": "requires signing keys; covered by test_signing.py",
    "quickstart": "interactive walkthrough, not a scanner",
    # `badge` was excluded here on the stated ground that it "renders a badge
    # from a prior scan; performs no walk". The implementation contradicts that:
    # `cli_report.cmd_badge` calls `scan_files(project)`, which walks the tree.
    # A path-taking command that walks was therefore exempt from the hostile
    # sweep on a false premise, so the FIFO, symlink-escape and skip-dir bait in
    # this fixture never reached it. Removed 2026-08-17 so it is swept. Found by
    # reading the implementation against the exclusion's own justification, not
    # by the sweep, which had no way to notice its own blind spot.
}

# Per-command timeout. The fixture is tiny, so anything approaching this is
# a block, not slow work.
TIMEOUT_SECONDS = 30


def _build_hostile_tree(root: Path) -> bool:
    """Create the malicious fixture. Returns False if the platform cannot
    host it (no FIFO / no symlinks), in which case callers return early —
    an early return keeps the suite's "collected == passing, 0 skipped"
    invariant, which pytest.skip would break.
    """
    outside = root / "outside"
    tree = root / "project"
    (tree / "sub").mkdir(parents=True)
    outside.mkdir()

    # Legitimate content, so the scanners have something real to report and
    # a clean run is distinguishable from a run that found nothing at all.
    (tree / "model.py").write_text(_BAIT, encoding="utf-8")

    # Out-of-root secret, reachable only by following the symlink below.
    (outside / "secret.py").write_text(
        f"# {CANARY_OUT_OF_ROOT}\n{_BAIT}", encoding="utf-8")

    # Content inside a SKIP_DIRS directory.
    (tree / ".git").mkdir()
    (tree / ".git" / "config.py").write_text(
        f"# {CANARY_SKIPDIR}\n{_BAIT}", encoding="utf-8")

    try:
        os.mkfifo(tree / "pipe.py")
        # A FIFO named regula-policy.yaml. The scanner reads a scanned
        # project's own policy file for system.domain; before scan_safety
        # reached that read (policy_config/domain_scoring/engagement), this
        # FIFO hung every path-taking command forever — the same DoS class
        # pipe.py guards, recurring on the policy path.
        os.mkfifo(tree / "regula-policy.yaml")
        # The cwd-relative members of the same class: when Regula runs FROM
        # inside a hostile tree (`cd repo && regula check .` is the
        # documented usage), policy_config loads ./regula-policy.yaml at
        # import time, config-validate discovers and reads it, and doctor
        # reads ./.gitignore. Each was a bare read; each hang was
        # reproduced per-vector against the unguarded code (2026-07-24).
        # regula-rules.yaml is different: auto-discovery calls is_file(),
        # which is False for a FIFO, so cwd discovery never hung — only an
        # explicit `--rules` path reached the bare read. The FIFO below
        # exercises that path and pins the discovery behaviour so a
        # refactor that drops is_file() cannot silently reintroduce the
        # hang.
        os.mkfifo(tree / "regula-rules.yaml")
        os.mkfifo(tree / ".gitignore")
    except (AttributeError, OSError):
        return False
    try:
        # A symlinked FILE escaping the root, and a symlinked DIRECTORY.
        (tree / "escape.py").symlink_to(outside / "secret.py")
        (tree / "sub" / "escapedir").symlink_to(outside, target_is_directory=True)
    except (AttributeError, OSError, NotImplementedError):
        return False
    return True


def _path_taking_commands():
    """Every subcommand that accepts a project path, derived from the parser.

    Returns {name: argv_tail_builder} where the builder takes the tree path
    and returns the argv after the program name, or None when the shape is
    not understood.
    """
    import argparse
    import cli

    parser = argparse.ArgumentParser(prog="regula")
    subs = parser.add_subparsers(dest="command")
    cli._build_subparsers(subs)

    found = {}
    for name, sub in subs.choices.items():
        opts, positionals = set(), []
        for action in sub._actions:
            if action.option_strings:
                opts.update(action.option_strings)
            elif action.dest != "command":
                positionals.append(action)

        if "-p" in opts or "--project" in opts:
            found[name] = lambda tree, n=name: [n, "-p", str(tree)]
            continue

        if not any(a.dest in _PATH_DESTS for a in positionals):
            continue

        # Build the positional run, filling anything that comes BEFORE the
        # path argument. `handoff` needs this: `handoff <tool> <project>`.
        argv_tail, understood = [name], True
        for action in positionals:
            if action.dest in _PATH_DESTS:
                argv_tail.append(None)  # placeholder for the tree
            elif action.choices:
                argv_tail.append(str(list(action.choices)[0]))
            elif action.nargs in ("?", "*"):
                continue
            else:
                understood = False  # required positional of unknown meaning
                break
        if understood:
            found[name] = (
                lambda tree, t=tuple(argv_tail):
                [str(tree) if x is None else x for x in t]
            )
    return found


def test_every_path_taking_command_is_swept_or_excluded():
    """No command may fall out of the sweep silently.

    Guards against the failure mode this whole file exists for: a check
    whose coverage is narrower than the reality it claims to cover.
    """
    commands = _path_taking_commands()
    stale = sorted(set(EXCLUDED) - set(commands))
    assert not stale, (
        f"EXCLUDED names commands that no longer take a path: {stale}. "
        "Remove them so the exclusion list cannot rot."
    )
    # handoff is the regression canary for the derivation itself.
    assert "handoff" in commands, (
        "handoff dropped out of the derived command list. Its path is its "
        "SECOND positional; a derivation that only inspects the first will "
        "miss it, and handoff is the command this sweep caught a real "
        "FIFO hang and out-of-root read in."
    )


def test_the_hostile_fixture_is_actually_hostile():
    """Prove the bait is live before trusting a clean sweep.

    The ESCAPE and SKIPDIR checks cannot be mutation-tested the way HANG
    and CRASH were, so they are only meaningful if the fixture genuinely
    reaches outside the root. If a symlink silently failed to create, the
    sweep would report clean because nothing was ever bait — the same
    "instrument that cannot return a negative" failure that produced a
    false Sentry-rotation report in July 2026.
    """
    with tempfile.TemporaryDirectory() as td:
        root = Path(td).resolve()
        if not _build_hostile_tree(root):
            return
        tree = root / "project"

        escape = tree / "escape.py"
        assert escape.is_symlink(), "escape.py is not a symlink — no bait"
        target = escape.resolve()
        assert not str(target).startswith(str(tree)), (
            f"escape.py resolves INSIDE the tree ({target}); it cannot test "
            "containment"
        )
        assert CANARY_OUT_OF_ROOT in target.read_text(encoding="utf-8"), (
            "the out-of-root file does not contain the canary"
        )

        skipped = tree / ".git" / "config.py"
        assert CANARY_SKIPDIR in skipped.read_text(encoding="utf-8")

        import stat as _stat
        assert _stat.S_ISFIFO(os.stat(tree / "pipe.py").st_mode), (
            "pipe.py is not a FIFO — the hang check cannot fire"
        )
        assert _stat.S_ISFIFO(os.stat(tree / "regula-policy.yaml").st_mode), (
            "regula-policy.yaml is not a FIFO — the policy-read hang check "
            "cannot fire"
        )
        assert _stat.S_ISFIFO(os.stat(tree / "regula-rules.yaml").st_mode), (
            "regula-rules.yaml is not a FIFO — the custom-rules hang check "
            "cannot fire"
        )
        assert _stat.S_ISFIFO(os.stat(tree / ".gitignore").st_mode), (
            ".gitignore is not a FIFO — the doctor hang check cannot fire"
        )

        # The other policy-read vector: a symlinked regula-policy.yaml that
        # escapes the scan root must not be followed. domain_scoring reads it
        # for system.domain; before the guard, this leaked an out-of-tree
        # file's parsed contents. It must now come back empty.
        sys.path.insert(0, str(REPO_ROOT / "scripts"))
        from domain_scoring import project_declared_domains
        sym_root = root / "sym_project"
        sym_root.mkdir()
        (root / "outside_policy.yaml").write_text(
            "system:\n  domain: employment\n", encoding="utf-8")
        (sym_root / "regula-policy.yaml").symlink_to(root / "outside_policy.yaml")
        assert project_declared_domains(str(sym_root)) == set(), (
            "a symlinked regula-policy.yaml escaping the project root was "
            "followed — scan_safety containment is not applied to the policy "
            "read"
        )


def test_no_command_hangs_or_escapes_on_a_hostile_tree():
    """The sweep. Collects every failure before asserting, so one broken
    command does not hide the others."""
    commands = _path_taking_commands()

    with tempfile.TemporaryDirectory() as td:
        root = Path(td).resolve()
        if not _build_hostile_tree(root):
            return  # platform cannot host a FIFO or symlinks
        tree = root / "project"

        # Snapshot the fixture's own files. Only files that appear AFTER a
        # command runs count as its output — otherwise the sweep reads the
        # planted .git/config.py back and reports every command as leaking,
        # which is a failure of the instrument, not of the commands.
        planted = {p for p in tree.rglob("*")}

        failures = []
        exit_codes = {}
        for name in sorted(commands):
            if name in EXCLUDED:
                continue
            argv = commands[name](tree)
            try:
                proc = subprocess.run(
                    [sys.executable, "-m", "scripts.cli", *argv],
                    cwd=str(REPO_ROOT),
                    capture_output=True,
                    text=True,
                    timeout=TIMEOUT_SECONDS,
                )
            except subprocess.TimeoutExpired:
                failures.append(
                    f"{name}: HANG — no return in {TIMEOUT_SECONDS}s. A FIFO "
                    f"in the scanned tree blocks it forever."
                )
                continue

            exit_codes[name] = proc.returncode
            blob = (proc.stdout or "") + (proc.stderr or "")
            # Anything the command NEWLY wrote into the tree counts as its
            # output. Symlinks are skipped: reading the bait through
            # escape.py is the breach itself, not evidence of one.
            for produced in tree.rglob("*"):
                if produced in planted:
                    continue
                if produced.is_symlink() or not produced.is_file():
                    continue
                try:
                    blob += produced.read_text(encoding="utf-8", errors="ignore")
                except OSError:
                    continue

            # A crash is a sweep failure in its own right, and it MUST be
            # checked: a command that dies early never reaches the FIFO or
            # the symlink, so a crash silently masks both other checks.
            # Verified — the buggy handoff crashed on relative_to() before
            # reaching the pipe, and this sweep reported it clean until
            # this check existed.
            crashed = (
                "Traceback (most recent call last)" in (proc.stderr or "")
                or "Internal error" in blob
            )
            if crashed:
                first = next(
                    (ln for ln in blob.splitlines()
                     if "error" in ln.lower()), "no error line found")
                failures.append(
                    f"{name}: CRASH — died on a hostile tree ({first.strip()[:90]}). "
                    f"A crash also hides the hang and escape checks below."
                )

            if CANARY_OUT_OF_ROOT in blob:
                failures.append(
                    f"{name}: ESCAPE — content from outside the scan root "
                    f"reached the output via a symlink."
                )
            if CANARY_SKIPDIR in blob:
                failures.append(
                    f"{name}: SKIPDIR — walked into .git, which is in "
                    f"SKIP_DIRS and holds credentials and history."
                )

        # Substantive findings are asserted FIRST. The controls below guard
        # against a vacuous pass, but they must not pre-empt real failures:
        # when every command hung, exit_codes was empty and the control
        # "no commands were swept" fired, hiding all 30 hang reports.
        assert not failures, "\n".join(["hostile sweep failures:", *failures])

        # Controls. With no failures reported, prove the sweep was capable
        # of reporting one — a run in which every command died on its
        # arguments would look identical to a clean run.
        assert exit_codes, "no commands were swept at all"
        argparse_errors = sorted(n for n, rc in exit_codes.items() if rc == 2)
        assert len(argparse_errors) <= len(exit_codes) // 4, (
            f"{len(argparse_errors)}/{len(exit_codes)} commands were rejected "
            f"by argparse, so the sweep exercised almost nothing: "
            f"{argparse_errors}"
        )


def test_no_command_hangs_when_cwd_is_hostile():
    """Run Regula FROM INSIDE the hostile tree, not just against it.

    The main sweep passes the hostile tree as an argument with cwd at the
    repo root, which never exercises the cwd-relative reads: policy_config
    loads ./regula-policy.yaml at module import, classify_risk loads
    ./regula-rules.yaml, doctor reads ./.gitignore, and config-validate
    auto-discovers ./regula-policy.yaml. Every one was a bare read_text,
    so a FIFO by any of those names hung the command before the scan-path
    guards could matter. `cd repo && regula check .` is the documented
    quickstart, so cwd-is-the-untrusted-tree is the NORMAL case, not an
    edge case.
    """
    with tempfile.TemporaryDirectory() as td:
        root = Path(td).resolve()
        if not _build_hostile_tree(root):
            return  # platform cannot host a FIFO or symlinks
        tree = root / "project"

        env = {**os.environ, "PYTHONPATH": str(REPO_ROOT)}
        env.pop("REGULA_POLICY", None)  # isolate discovery to the fixture

        # One command per cwd-read vector: import-time policy load fires
        # for all of them; doctor adds the .gitignore read; config validate
        # adds the validator's own discovery+read; check adds the in-tree
        # scan; check-rules adds the explicit --rules read, which is the
        # one path that reaches custom_rules with an attacker-shaped file
        # (auto-discovery filters FIFOs via is_file(), verified 2026-07-24).
        sweep = {
            "doctor": ["doctor"],
            "config-validate": ["config", "validate"],
            "check": ["check", "."],
            "check-rules": ["check", ".", "--rules", "regula-rules.yaml"],
        }

        failures = []
        for name, argv in sorted(sweep.items()):
            try:
                proc = subprocess.run(
                    [sys.executable, "-m", "scripts.cli", *argv],
                    cwd=str(tree),
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=TIMEOUT_SECONDS,
                )
            except subprocess.TimeoutExpired:
                failures.append(
                    f"{name}: HANG — no return in {TIMEOUT_SECONDS}s with a "
                    f"FIFO regula-policy.yaml/regula-rules.yaml/.gitignore "
                    f"in the working directory."
                )
                continue
            blob = (proc.stdout or "") + (proc.stderr or "")
            if "Traceback (most recent call last)" in (proc.stderr or ""):
                first = next(
                    (ln for ln in blob.splitlines()
                     if "error" in ln.lower()), "no error line found")
                failures.append(
                    f"{name}: CRASH from a hostile cwd "
                    f"({first.strip()[:90]})."
                )
            # Control: an argparse rejection returns fast without touching
            # any FIFO, which would make this sweep pass vacuously. Exit
            # codes cannot distinguish it (config validate exits 2 on an
            # invalid config), but argparse always prints a usage block.
            if "usage:" in (proc.stderr or ""):
                failures.append(
                    f"{name}: argparse rejected the invocation, so the "
                    f"command exercised nothing."
                )

        assert not failures, "\n".join(["hostile-cwd sweep failures:", *failures])


if __name__ == "__main__":
    test_every_path_taking_command_is_swept_or_excluded()
    print("PASS: every path-taking command is swept or explicitly excluded")
    test_the_hostile_fixture_is_actually_hostile()
    print("PASS: the hostile fixture genuinely reaches outside the scan root")
    test_no_command_hangs_or_escapes_on_a_hostile_tree()
    print("PASS: no command hangs or escapes on a hostile tree")
    test_no_command_hangs_when_cwd_is_hostile()
    print("PASS: no command hangs when the working directory is hostile")
