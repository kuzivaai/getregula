"""Every command and flag `docs/DEMO.md` shows must exist in the real registry.

The demonstration page is the one document written to be executed live in front
of somebody. A renamed flag in it is not a documentation defect, it is a
consultant typing a command that errors while a prospect watches.

What this can and cannot cover is stated on the page itself and repeated here.
It CAN check, on every test run, that each `regula` invocation names a
registered command and that each `--flag` is one that command accepts, read from
the argparse registry rather than from help text. It CANNOT check the timings or
the third-party output, because those depend on a clone this repository does not
contain. That limit is printed on the page rather than left for a reader to
discover, which is the N138 remedy: declare the gap at the point of use.

Module-level functions so the custom runner's `dir(module)` walk binds them
(N134).
"""
import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

DEMO = REPO / "docs" / "DEMO.md"

# Flags argparse supplies for every parser.
_UNIVERSAL = {"-h", "--help"}


def _real_parser():
    """Build the shipped parser and capture it, without running a command."""
    import cli

    class _Captured(Exception):
        def __init__(self, parser):
            self.parser = parser

    real = argparse.ArgumentParser.parse_args

    def spy(self, args=None, namespace=None):
        raise _Captured(self)

    argparse.ArgumentParser.parse_args = spy
    try:
        cli.main([])
    except _Captured as captured:
        return captured.parser
    finally:
        argparse.ArgumentParser.parse_args = real
    raise AssertionError("the parser was never constructed")


def _subparsers(parser):
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            return action.choices
    raise AssertionError("no subparsers on the root parser")


def _invocations(text):
    """Every `regula ...` line in a fenced block, as (command, flags)."""
    found = []
    for block in re.findall(r"```(?:bash|console|sh)?\n(.*?)```", text, re.S):
        for line in block.splitlines():
            line = line.strip().lstrip("$ ").strip()
            if not line.startswith("regula "):
                continue
            line = line.split("#", 1)[0].strip().rstrip("\\").strip()
            parts = line.split()[1:]
            if not parts:
                continue
            command = parts[0] if not parts[0].startswith("-") else None
            flags = [p.split("=")[0] for p in parts if p.startswith("-")]
            found.append((command, flags, line))
    return found


def test_the_demo_page_exists_and_names_commands():
    assert DEMO.is_file(), f"{DEMO} is missing"
    invocations = _invocations(DEMO.read_text(encoding="utf-8"))
    assert len(invocations) >= 8, (
        f"only {len(invocations)} regula invocation(s) found; the extractor has "
        f"probably stopped matching the page's fenced blocks, which would make "
        f"this whole module pass by scanning nothing")


def test_every_command_the_demo_shows_is_registered():
    parser = _real_parser()
    choices = _subparsers(parser)
    unknown = []
    for command, _flags, line in _invocations(DEMO.read_text(encoding="utf-8")):
        if command is None:
            continue                     # a bare `regula --version` style call
        if command not in choices:
            unknown.append((command, line))
    assert unknown == [], f"docs/DEMO.md shows unregistered command(s): {unknown}"


def test_every_flag_the_demo_shows_is_accepted_by_its_command():
    parser = _real_parser()
    choices = _subparsers(parser)
    root_flags = {s for a in parser._actions for s in a.option_strings} | _UNIVERSAL
    bad = []
    for command, flags, line in _invocations(DEMO.read_text(encoding="utf-8")):
        if command is None:
            accepted = root_flags
        else:
            sub = choices[command]
            accepted = {s for a in sub._actions for s in a.option_strings}
            accepted |= root_flags
        for flag in flags:
            if flag not in accepted:
                bad.append((command, flag, line))
    assert bad == [], f"docs/DEMO.md shows flag(s) the command does not accept: {bad}"


def test_the_demo_states_the_accuracy_position_rather_than_leaving_it_to_be_asked():
    """A demonstration page that omits the numbers is a sales page.

    Each string here is a figure the session brief requires to travel unrounded
    with its caveat. If one is removed from the page this fails by name.
    """
    text = DEMO.read_text(encoding="utf-8")
    for needle in ("10/30", "5/5", "83.5%", "N=115", "0/40", "40/40",
                   "0 human-labelled repositories", "not\n  reconstructible"):
        assert needle in text, f"docs/DEMO.md no longer states {needle!r}"


def test_the_demo_makes_no_determination_claim():
    """The page must not say the tool determines, certifies or verifies
    compliance, and must not present a clean scan as compliant."""
    import determination_guard as dg
    findings = dg.scan_file("docs/DEMO.md")
    assert findings == [], findings


def test_the_third_party_commit_is_pinned():
    """An unpinned clone measures whatever the default branch is today, which is
    the defect N51 records against this project's own precision corpus."""
    text = DEMO.read_text(encoding="utf-8")
    assert re.search(r"git checkout [0-9a-f]{40}", text), (
        "docs/DEMO.md must pin the third-party repository to a full SHA")
    assert "names a commit in **that** repository" in text, (
        "the page must say whose repository the SHA belongs to (N39c)")


def test_the_demo_declares_what_no_guard_covers():
    text = DEMO.read_text(encoding="utf-8")
    assert "What no guard on this page can cover" in text
    assert "Nothing checks that the timings still hold" in text


if __name__ == "__main__":                                     # pragma: no cover
    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"PASS {name}")
            except Exception as exc:                           # noqa: BLE001
                failures += 1
                print(f"FAIL {name}: {exc}")
    print(f"{failures} failure(s)")
    raise SystemExit(1 if failures else 0)
