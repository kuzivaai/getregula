"""Verify that `docs/improvement/LEDGER.md`'s claims about commits are true.

WHY THIS EXISTS
---------------
The ledger's own first rule is that "every status names the commit or the
command that establishes it". Nothing enforced it, and the rule failed on the
day the file was created.

MEASURED 2026-07-29. The ledger recorded finding N2 as "commit HELD FOR
APPROVAL, not pushed". The commit carrying that correction, `236437b`, was on
the remote:

    $ git branch -r --contains 236437b
      origin/improvement/2026-08-programme

It got there without ever being pushed as a tip. The reflog of the
remote-tracking ref shows `e48c4db` pushed at 2026-07-29 19:18:53 +0100 and
never shows `236437b` at all. A push names a tip; the remote receives that tip
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
5. Supersession between rows is DECLARED and BIDIRECTIONAL. See below.

WHY SUPERSESSION IS A MARKER AND NOT PROSE
------------------------------------------
The checks above verify claims about commits. Nothing verified that a figure is
still current, and the ledger carried a stale headline through two consecutive
sessions because of it: row N13 led with "15 findings, 6 fixable" after N15 had
established the `fixable` count was over-counted by one and N18 had re-measured
the residue at a different commit.

Supersession is a relation between two rows. No predicate can infer it from
prose, because "which rows N15 and N18 supersede" is a sentence about the file
and not a fact in it. So the relation is declared:

    the superseding row carries   SUPERSEDES:<id>
    the superseded row carries    SUPERSEDED-BY:<id>

and this module asserts every declaration has its counterpart. That is the
whole mechanism. It cannot tell you a figure is stale; it can only stop a row
from being marked stale in one direction and current in the other, which is
exactly the half-recorded state N13 was left in.

Design choices, recorded because they were mine and a later session inherits
them rather than only the result:

- Markers are UPPERCASE, matching HELD:/PUSHED:, so a machine assertion is
  visibly not prose in the rendered table.
- Ids are the row's own first cell, so no second identifier scheme is
  introduced and a marker cannot point at something that is not a row.
- Bidirectional rather than one-way. A one-way SUPERSEDES: would let a reader
  arrive at N13 from the contents page and see nothing wrong with it, which is
  the failure being fixed. The cost is that both rows must be edited together;
  that cost is the point.
- Many-to-one is allowed. N13 is superseded by two rows and carries two
  markers.
- NOT used for a figure that merely moved. This file's own rule 24 holds that
  `--diff-base` totals have no fixed point and that each is correct at its
  commit. A number that changed because the corpus changed is not superseded.
  Supersession is for a statement that was WRONG or has been RETRACTED. This
  distinction is a judgement and no test enforces it; it is written here so the
  mechanism does not decay into marking every re-measurement.

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

# `SUPERSEDES:<id>` / `SUPERSEDED-BY:<id>`. The two tokens cannot collide:
# after `SUPERSEDE` one continues with `S:` and the other with `D-BY:`.
#
# The id charset deliberately excludes `.` so that a marker ending a sentence
# parses as the id and not as the id plus a full stop. Caught by this check on
# its first real use: `SUPERSEDED-BY:N18.` was read as row `N18.`, which does
# not exist, and the pairing failed. A marker can therefore only name a
# single-token id, which every F*/N* row has; a row titled in words, such as
# `Merge-base measurement`, cannot be named by one, and that limitation is
# stated rather than worked around.
SUPERSEDES_RE = re.compile(r"\bSUPERSEDES:([A-Za-z0-9_-]+)")
SUPERSEDED_BY_RE = re.compile(r"\bSUPERSEDED-BY:([A-Za-z0-9_-]+)")


def row_id(line: str) -> str | None:
    """The row's own identifier: its first table cell, stripped of emphasis.

    Returns None for anything that is not a body row of a table, including the
    `|---|---|` separator and the header.
    """
    if not line.lstrip().startswith("|"):
        return None
    cells = line.strip().strip("|").split("|")
    if not cells:
        return None
    ident = cells[0].strip().strip("*").strip("`").strip()
    if not ident or set(ident) <= set("-: "):
        return None
    return ident


def audit_supersession(text: str) -> tuple[list[str], int]:
    """Return (problems, declarations_checked) for one ledger body.

    Pure over `text`, so a control can drive it with a fixture instead of
    editing the file on disk.
    """
    problems: list[str] = []
    rows: dict[str, str] = {}
    for line in text.splitlines():
        ident = row_id(line)
        if ident is not None:
            # First occurrence wins. A duplicate id is reported rather than
            # silently shadowing, because a marker pointing at an ambiguous
            # row checks nothing.
            if ident in rows:
                problems.append(
                    f"row id {ident!r} appears more than once, so a "
                    f"SUPERSEDES:/SUPERSEDED-BY: marker naming it is ambiguous")
            else:
                rows[ident] = line

    forward: set[tuple[str, str]] = set()      # (newer, older)
    backward: set[tuple[str, str]] = set()     # (newer, older)

    for ident, line in rows.items():
        for older in SUPERSEDES_RE.findall(line):
            forward.add((ident, older))
        for newer in SUPERSEDED_BY_RE.findall(line):
            backward.add((newer, ident))

    checked = 0
    for newer, older in sorted(forward):
        checked += 1
        if newer == older:
            problems.append(f"row {newer} declares SUPERSEDES:{older}, itself")
            continue
        if older not in rows:
            problems.append(
                f"row {newer} declares SUPERSEDES:{older}, but no row {older} "
                f"exists in the ledger")
            continue
        if (newer, older) not in backward:
            problems.append(
                f"unpaired declaration: row {newer} declares "
                f"SUPERSEDES:{older}, but row {older} does not carry "
                f"SUPERSEDED-BY:{newer}. Supersession is bidirectional so a "
                f"reader arriving at the superseded row is told it is stale.")

    for newer, older in sorted(backward):
        checked += 1
        if newer == older:
            problems.append(
                f"row {older} declares SUPERSEDED-BY:{newer}, itself")
            continue
        if newer not in rows:
            problems.append(
                f"row {older} declares SUPERSEDED-BY:{newer}, but no row "
                f"{newer} exists in the ledger")
            continue
        if (newer, older) not in forward:
            problems.append(
                f"unpaired declaration: row {older} declares "
                f"SUPERSEDED-BY:{newer}, but row {newer} does not carry "
                f"SUPERSEDES:{older}")

    return problems, checked


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

    `236437b` is on the remote. Asserting it is held must be rejected;
    asserting it is pushed must be accepted. One planted line, two polarities,
    so the check cannot pass by being inert.
    """
    ok, why = checkout_can_answer()
    if not ok:
        pytest.skip(f"cannot run the remote-state control here: {why}")
    if not commit_exists("236437b"):
        pytest.skip("236437b is not in this checkout")

    false_hold, _ = audit_status_claims("| x | HELD:236437b |")
    assert any("HELD:236437b" in p for p in false_hold), (
        "planting a false hold on a commit that is on the remote produced no "
        "complaint; the check is inert")

    true_statement, checked = audit_status_claims("| x | PUSHED:236437b |")
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
        "| N2 | ... | corrected, and the commit is PUSHED:236437b |",
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


def test_ledger_supersession_declarations_are_paired():
    """Every SUPERSEDES: in LEDGER.md has its SUPERSEDED-BY: counterpart."""
    problems, checked = audit_supersession(
        LEDGER_PATH.read_text(encoding="utf-8"))
    assert not problems, (
        "LEDGER.md has half-declared supersessions:\n"
        + "\n".join(f"  - {p}" for p in problems))
    # An absent signal is not a passing signal. If the ledger stops declaring
    # supersession at all, this test must say so rather than pass on nothing.
    assert checked > 0, (
        "no SUPERSEDES:/SUPERSEDED-BY: declarations were found in LEDGER.md. "
        "Either every superseded figure has been removed, or the markers have "
        "been dropped and stale headlines are unguarded again.")
    print(f"✓ ledger supersession: {checked} declarations paired")


def test_an_unpaired_supersedes_is_named():
    """The exact defect: N15 supersedes N13 and N13 is not told about it.

    This is the control for the real edit made in this session, run as a
    fixture so it keeps firing after the file is correct.
    """
    unpaired = (
        "| **N13** | residue is 15, 6 fixable | date | OPEN. |\n"
        "| **N15** | fixable was over-counted | date | SUPERSEDES:N13 |\n"
    )
    problems, checked = audit_supersession(unpaired)
    assert checked == 1, checked
    assert any("unpaired declaration" in p and "N13" in p and "N15" in p
               for p in problems), problems

    paired = (
        "| **N13** | residue is 15, 6 fixable | date | OPEN. SUPERSEDED-BY:N15 |\n"
        "| **N15** | fixable was over-counted | date | SUPERSEDES:N13 |\n"
    )
    ok, checked_ok = audit_supersession(paired)
    assert not ok, ok
    assert checked_ok == 2, checked_ok
    print("✓ ledger supersession control: unpaired named, paired accepted")


def test_the_reverse_direction_is_also_required():
    """A lone SUPERSEDED-BY: is as unverifiable as a lone SUPERSEDES:."""
    problems, _ = audit_supersession(
        "| **N13** | x | d | SUPERSEDED-BY:N15 |\n"
        "| **N15** | y | d | OPEN. |\n")
    assert any("does not carry SUPERSEDES:N13" in p for p in problems), problems
    print("✓ ledger supersession: reverse direction required too")


def test_a_marker_naming_a_row_that_does_not_exist_is_reported():
    problems, _ = audit_supersession(
        "| **N15** | y | d | SUPERSEDES:N99 |\n")
    assert any("no row N99 exists" in p for p in problems), problems

    self_ref, _ = audit_supersession("| **N15** | y | d | SUPERSEDES:N15 |\n")
    assert any("itself" in p for p in self_ref), self_ref
    print("✓ ledger supersession: dangling and self-referential markers caught")


def test_a_marker_ending_a_sentence_is_not_read_as_part_of_the_id():
    """Regression: `SUPERSEDED-BY:N18.` must name N18, not `N18.`.

    This defect was introduced by the very edit that added the markers and was
    caught by this check, so the case is pinned.
    """
    text = (
        "| **N13** | x | d | SUPERSEDED-BY:N18. Do not quote this row. |\n"
        "| **N18** | y | d | SUPERSEDES:N13, so the figures moved. |\n"
    )
    problems, checked = audit_supersession(text)
    assert not problems, problems
    assert checked == 2, checked
    print("✓ ledger supersession: trailing punctuation is not part of the id")


def test_many_to_one_supersession_is_allowed():
    """N13 is superseded by two rows; that must not be an error."""
    text = (
        "| **N13** | x | d | SUPERSEDED-BY:N15 SUPERSEDED-BY:N18 |\n"
        "| **N15** | y | d | SUPERSEDES:N13 |\n"
        "| **N18** | z | d | SUPERSEDES:N13 |\n"
    )
    problems, checked = audit_supersession(text)
    assert not problems, problems
    assert checked == 4, checked
    print("✓ ledger supersession: many-to-one accepted")


def test_row_id_ignores_table_furniture_and_prose():
    assert row_id("| **N13** | a | b | c |") == "N13"
    assert row_id("| F21 | a | b | c |") == "F21"
    assert row_id("| **Merge-base measurement** | a | b | c |") == \
        "Merge-base measurement"
    assert row_id("|---|---|---|---|") is None
    assert row_id("Nothing drops off because it stopped being mentioned.") \
        is None
    print("✓ row_id: only table body rows produce an id")


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
