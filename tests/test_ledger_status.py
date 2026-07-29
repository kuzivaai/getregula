"""Verify that `docs/improvement/LEDGER.md`'s claims about commits are true.

WHY THIS EXISTS
---------------
The ledger's own first rule is that "every status names the commit or the
command that establishes it". Nothing enforced it, and the rule failed on the
day the file was created.

MEASURED 2026-07-29. The ledger recorded finding N2 as "commit HELD FOR
APPROVAL, not pushed". The commit carrying that correction, `7b78f2e`, was on
the remote:

    $ git branch -r --contains 7b78f2e
      origin/improvement/2026-08-programme

It got there without ever being pushed as a tip. The reflog of the
remote-tracking ref shows `f286562` pushed at 2026-07-29 19:18:53 +0100 and
never shows `7b78f2e` at all. A push names a tip; the remote receives that tip
and every one of its ancestors. A hold on a commit is therefore broken by
pushing anything descended from it, which is what happened.

The instance is a wrong sentence in a document. The class is that the ledger is
written mid-session and then overtaken by the same session's later actions,
with no mechanical check on any of it.

WHAT THIS CHECKS
----------------
1. Every commit-shaped token written in backticks names a commit that exists.
2. `HELD:<sha>` asserts the commit is absent from the remote. Verified.
3. `PUSHED:<sha>` asserts the commit is present on the remote. Verified.
4. A ledger table row that discusses a commit's remote state in prose must
   carry one of those markers, so the prose-only claim that failed here cannot
   be made again without something checking it.

RESOLVING "ON THE REMOTE" WITHOUT THE NETWORK
---------------------------------------------
The remote question is answered from local remote-tracking refs
(`refs/remotes/**`) via `git merge-base --is-ancestor`, never by contacting a
server, so the test gives the same answer offline, in CI and in a clean
checkout.

That has a real limitation and the limitation is reported rather than hidden:
a remote-tracking ref that has not been fetched is stale, and a shallow clone
does not contain the objects the ledger names. When the checkout cannot answer
the question, this test says so and skips instead of passing quietly. A silent
pass on an unverifiable claim is the failure mode this file exists to prevent.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

LEDGER_PATH = REPO_ROOT / "docs" / "improvement" / "LEDGER.md"

# `HELD:<sha>` / `PUSHED:<sha>`. Uppercase so the marker is visibly a machine
# assertion in the rendered table and not mistaken for prose.
MARKER_RE = re.compile(r"\b(HELD|PUSHED):([0-9a-f]{7,40})\b")

# The ledger writes commits in backticks throughout. Restricting the existence
# check to that form keeps ordinary seven-digit numbers out of the match set.
BACKTICK_SHA_RE = re.compile(r"`([0-9a-f]{7,40})`")

# Prose that asserts something about where a commit is. A row using any of
# these has to carry a marker, or nothing can check it.
REMOTE_STATE_CUES = (
    "held for approval",
    "not pushed",
    "unpushed",
    "absent from the remote",
    "on the remote",
)


def _git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=REPO_ROOT,
                          capture_output=True, text=True)


def commit_exists(sha: str) -> bool:
    r = _git("cat-file", "-t", sha)
    return r.returncode == 0 and r.stdout.strip() == "commit"


def remote_tracking_refs() -> list[str]:
    r = _git("for-each-ref", "--format=%(refname)", "refs/remotes/")
    return [line for line in r.stdout.splitlines() if line.strip()]


def is_on_remote(sha: str) -> bool:
    """Is `sha` reachable from any remote-tracking ref in this checkout?

    `merge-base --is-ancestor` exits 0 for yes and 1 for no. A commit is its
    own ancestor, so a ref pointing straight at `sha` also answers yes.
    """
    for ref in remote_tracking_refs():
        if _git("merge-base", "--is-ancestor", sha, ref).returncode == 0:
            return True
    return False


def checkout_can_answer() -> tuple[bool, str]:
    """Can this checkout resolve the ledger's commit claims at all?"""
    if _git("rev-parse", "--is-shallow-repository").stdout.strip() == "true":
        return False, ("shallow clone: the objects the ledger names are not "
                       "present, so no claim about them can be verified")
    if not remote_tracking_refs():
        return False, ("no remote-tracking refs in refs/remotes/: the remote "
                       "state of a commit cannot be resolved without them")
    return True, ""


def audit_status_claims(text: str,
                        exists=commit_exists,
                        on_remote=is_on_remote) -> tuple[list[str], int]:
    """Return (problems, claims_checked) for one ledger body.

    Pure over `text`, and the two git resolvers are injectable, so a control
    can plant a claim and drive this without writing to the file on disk or
    to the repository.
    """
    problems: list[str] = []
    checked = 0

    for sha in sorted(set(BACKTICK_SHA_RE.findall(text))):
        if exists(sha):
            checked += 1
        else:
            problems.append(
                f"`{sha}` is written in the commit form but no such commit "
                f"exists in this repository")

    for kind, sha in MARKER_RE.findall(text):
        if not exists(sha):
            problems.append(f"{kind}:{sha} names a commit that does not exist")
            continue
        checked += 1
        present = on_remote(sha)
        if kind == "HELD" and present:
            problems.append(
                f"HELD:{sha} claims the commit is off the remote, but it is "
                f"reachable from a remote-tracking ref. A hold is broken by "
                f"pushing any descendant.")
        if kind == "PUSHED" and not present:
            problems.append(
                f"PUSHED:{sha} claims the commit is on the remote, but no "
                f"remote-tracking ref reaches it")

    for line in text.splitlines():
        if not line.lstrip().startswith("|"):
            continue
        lowered = line.lower()
        if any(cue in lowered for cue in REMOTE_STATE_CUES) and \
                not MARKER_RE.search(line):
            problems.append(
                "a table row states a commit's remote state in prose with no "
                "HELD:/PUSHED: marker, so nothing can check it: "
                + line.strip()[:140])

    return problems, checked


def test_ledger_commit_claims_are_verified():
    """Every claim LEDGER.md makes about a commit holds in this repository."""
    ok, why = checkout_can_answer()
    if not ok:
        pytest.skip(f"cannot verify ledger commit claims here: {why}")

    problems, checked = audit_status_claims(
        LEDGER_PATH.read_text(encoding="utf-8"))

    assert not problems, (
        "LEDGER.md makes claims about commits that do not hold:\n"
        + "\n".join(f"  - {p}" for p in problems))
    # A parser that silently matches nothing would pass the assertion above
    # while checking nothing at all. That is the blank-gate failure this
    # programme keeps paying for, so require positive proof it ran.
    assert checked > 0, (
        "no commit claims were found in LEDGER.md. Either the ledger stopped "
        "naming commits, which breaks its own first rule, or the parser has "
        "drifted from the file's conventions.")
    print(f"✓ ledger status: {checked} commit claims verified")


def test_audit_discriminates_a_false_hold_from_a_true_statement():
    """Control, against real git state, in both directions.

    `7b78f2e` is on the remote. Asserting it is held must be rejected;
    asserting it is pushed must be accepted. One planted line, two polarities,
    so the check cannot pass by being inert.
    """
    ok, why = checkout_can_answer()
    if not ok:
        pytest.skip(f"cannot run the remote-state control here: {why}")
    if not commit_exists("7b78f2e"):
        pytest.skip("7b78f2e is not in this checkout")

    false_hold, _ = audit_status_claims("| x | HELD:7b78f2e |")
    assert any("HELD:7b78f2e" in p for p in false_hold), (
        "planting a false hold on a commit that is on the remote produced no "
        "complaint; the check is inert")

    true_statement, checked = audit_status_claims("| x | PUSHED:7b78f2e |")
    assert not true_statement, (
        "the true form was rejected: " + "; ".join(true_statement))
    assert checked == 1
    print("✓ ledger status control: false hold rejected, true statement kept")


def test_prose_only_remote_claim_is_rejected():
    """The exact defect: a status asserting a hold with nothing to check it."""
    problems, _ = audit_status_claims(
        "| N2 | ... | **CORRECTED, commit HELD FOR APPROVAL, not pushed.** |")
    assert any("prose" in p for p in problems), (
        "a prose-only hold claim was accepted; that is the N2 defect intact")

    def exists(_sha):
        return True

    def present(_sha):
        return True

    accepted, _ = audit_status_claims(
        "| N2 | ... | corrected, and the commit is PUSHED:7b78f2e |",
        exists, present)
    assert not accepted, "; ".join(accepted)
    print("✓ ledger status: prose-only remote claims rejected")


def test_a_backticked_non_commit_is_reported():
    """An invented commit hash must not pass as a citation."""
    problems, _ = audit_status_claims(
        "text citing `abcdef1234567` as though it were a commit")
    assert any("no such commit exists" in p for p in problems), (
        "an invented commit hash was accepted")
    print("✓ ledger status: invented commit hashes rejected")


def test_marker_polarity_is_decided_by_the_resolver_not_the_word():
    """Logic control with stub resolvers: both markers, both answers.

    Drives the four combinations without git, so a change to the resolvers
    cannot quietly invert the meaning of a marker.
    """
    def always_exists(_sha):
        return True

    def on(_sha):
        return True

    def off(_sha):
        return False

    held_but_pushed, _ = audit_status_claims("| HELD:aaaaaaa |",
                                             always_exists, on)
    held_and_absent, _ = audit_status_claims("| HELD:aaaaaaa |",
                                             always_exists, off)
    pushed_and_present, _ = audit_status_claims("| PUSHED:aaaaaaa |",
                                                always_exists, on)
    pushed_but_absent, _ = audit_status_claims("| PUSHED:aaaaaaa |",
                                               always_exists, off)

    assert held_but_pushed and not held_and_absent
    assert pushed_but_absent and not pushed_and_present
    print("✓ ledger status: marker polarity follows the resolver")
