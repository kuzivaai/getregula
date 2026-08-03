# regula-ignore
"""Guard `scripts/check_decompositions.py`, the decomposition reconciler.

WHY THIS EXISTS
---------------
Session 9 landed two record defects with, apparently, one shape: a
decomposition stated in prose beside a total produced by a command, with
nothing checking they agreed. `72 passed` sat above
`7 + 15 + 15 + 21 + 17`, which is 75. The overstated file was
`tests/test_claim_diff.py`, prose 21 against a measured 18.

The second defect looked like the same class and was not, which is why this
file pins three rules rather than one. A handover header declared four
commits and a finish at `8c2fccb` while its own itemisation listed six.
`git rev-list --count 2c1f080..8c2fccb` is 4, so the arithmetic was
internally consistent; the **declared finish was stale**, because `4a442f2`
and `e9c1e03` landed after the header was written. No arithmetic check
catches that. Reconciling the header against the repository does.

WHAT IS PINNED
--------------
- `sum-equals` fires when `a + b + ... = T` does not sum to T, and names the
  gap rather than only reporting a failure
- `fence-total` fires when a pasted total has no decomposition beside it that
  agrees, and stays silent when any one of several decompositions on the line
  does agree ("N against M before" is the common prose shape)
- `commit-anchors` reconciles a declared commit count against
  `git rev-list --count`, and under `--require-head` catches a stale finish
- the tracked-record enumeration comes from `git ls-files`, not from a list
- the module's own control fires on a planted defect and then goes silent,
  so a green run is positive proof the code path executed rather than an
  absent signal
- the real session 9 defects are reproduced as fixtures, so a regression that
  stops detecting them fails here

WHAT WAS MEASURED AND REJECTED
------------------------------
A fourth rule, pairing any `Label: N` with a nearby itemisation by matching
the label against section headings, produced seven findings on the tracked
corpus and all seven were false. That negative result is recorded in the
module docstring and in `docs/improvement/LEDGER.md`; the test below pins
that the rule set does NOT contain it, so a later session does not add it
back without re-measuring.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import check_decompositions as cd   # noqa: E402

SCRIPT = REPO_ROOT / "scripts" / "check_decompositions.py"

# The real defect, reproduced verbatim from the session 9 handover at line 922.
SESSION9_FENCE_DEFECT = """# Record

```
$ python3 -m pytest tests/test_gate_probe.py -q
72 passed in 22.86s
```

That is 7 + 15 + 15 + 21 + 17 against 0 + 15 + 14 + 16 + 17 before.
"""

# The same passage after re-deriving each file's own total by running it.
SESSION9_FENCE_REPAIRED = """# Record

```
$ python3 -m pytest tests/test_gate_probe.py -q
72 passed in 22.86s
```

That is 7 + 15 + 15 + 18 + 17 against 0 + 15 + 14 + 16 + 17 before.
"""


def _write(tmp_path, name, text):
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return str(path)


def _rules(findings):
    return sorted(f.rule for f in findings)


# --------------------------------------------------------------------------
# sum-equals
# --------------------------------------------------------------------------

def test_sum_equals_fires_and_names_the_gap(tmp_path):
    """A failure that does not say BY HOW MUCH sends the reader back to it."""
    path = _write(tmp_path, "a.md", "The split is 7 + 15 + 21 = 40 overall.\n")
    findings = cd.check_file(path)
    assert _rules(findings) == ["sum-equals"], findings
    message = findings[0].message
    assert "sums to 43" in message, message
    assert "stated total is 40" in message, message
    assert "gap 3" in message, message
    print("✓ sum-equals fires on a non-summing decomposition and names the gap")


def test_sum_equals_silent_when_the_arithmetic_holds(tmp_path):
    """Every explicit form in the tracked corpus is correct; none may fire."""
    path = _write(tmp_path, "a.md", "The split is 7 + 15 + 18 = 40 overall.\n")
    assert cd.check_file(path) == []
    print("✓ sum-equals stays silent on correct arithmetic")


def test_sum_equals_handles_decimals_and_thousands(tmp_path):
    """The programme's records carry both `9.5 + 8.0` and `2,322 + 27`."""
    good = _write(
        tmp_path, "g.md",
        "= 9.5 + 8.0 + 13.2 + 10.8 + 8.5 + 0.8 + 1.5 = **52.3**\n"
        "and 2,322 + 27 = 2,349 checks out.\n",
    )
    assert cd.check_file(good) == []
    bad = _write(tmp_path, "b.md", "and 2,322 + 27 = 2,350 checks out.\n")
    findings = cd.check_file(bad)
    assert _rules(findings) == ["sum-equals"], findings
    assert "gap -1" in findings[0].message, findings[0].message
    print("✓ decimals and thousands separators parse, and still reconcile")


def test_a_digit_run_inside_a_longer_number_is_not_a_component(tmp_path):
    """Rule 4d: a digit sequence is not a claim. `222353` is not `22 + 2353`."""
    path = _write(tmp_path, "a.md", 'size = 222353\nhash = 22+2353\n')
    findings = cd.check_file(path)
    assert findings == [], findings
    print("✓ a digit run inside a longer number is never read as a component")


# --------------------------------------------------------------------------
# fence-total
# --------------------------------------------------------------------------

def test_fence_total_reproduces_the_real_session9_defect(tmp_path):
    """If this stops failing, the reconciler stopped detecting the defect."""
    path = _write(tmp_path, "h.md", SESSION9_FENCE_DEFECT)
    findings = cd.check_file(path)
    assert _rules(findings) == ["fence-total"], findings
    message = findings[0].message
    assert "pasted total is 72" in message, message
    assert "'7 + 15 + 15 + 21 + 17' sums to 75" in message, message
    assert "'0 + 15 + 14 + 16 + 17' sums to 62" in message, message
    assert findings[0].line == 8, findings[0].line
    print("✓ fence-total reproduces the session 9 defect and names both sums")


def test_fence_total_silent_once_the_defect_is_repaired(tmp_path):
    """Control the other way: the repaired passage must report nothing."""
    path = _write(tmp_path, "h.md", SESSION9_FENCE_REPAIRED)
    assert cd.check_file(path) == []
    print("✓ fence-total goes silent on the repaired passage")


def test_fence_total_accepts_any_agreeing_decomposition_on_the_line(tmp_path):
    """`N against M before` is the house prose shape; one match is enough."""
    path = _write(
        tmp_path, "h.md",
        "```\n72 passed in 9.09s\n```\n"
        "That is 40 + 32 against 8 + 9 before.\n",
    )
    assert cd.check_file(path) == []
    print("✓ one agreeing decomposition on the line satisfies the rule")


def test_fence_total_needs_an_anchor_noun_for_the_total(tmp_path):
    """A bare number in a fence is not a total, so it must not be paired."""
    path = _write(
        tmp_path, "h.md",
        "```\n$ echo 72\n72\n```\n"
        "That is 7 + 15 + 15 + 21 + 17 in total.\n",
    )
    assert cd.check_file(path) == [], "a bare fence number was read as a total"
    print("✓ an unanchored number in a fence is never treated as the total")


def test_fence_total_does_not_read_iso_timezone_as_arithmetic(tmp_path):
    """An ISO offset such as 06+01 is timestamp syntax, not a decomposition."""
    path = _write(
        tmp_path, "h.md",
        "```\n244 files changed\n```\n"
        "Ended: 2026-08-01T14:00:06+01:00\n",
    )
    assert cd.check_file(path) == []
    print("✓ an ISO timezone offset is never treated as arithmetic")


def test_fence_total_ignores_prose_beyond_the_window(tmp_path):
    """Distant prose is not a decomposition OF the total, so it is not paired."""
    path = _write(
        tmp_path, "h.md",
        "```\n72 passed in 9.09s\n```\n"
        + "\n".join(["Unrelated line."] * 6)
        + "\nThe unrelated split is 7 + 15 + 21 in total.\n",
    )
    assert cd.check_file(path) == []
    print("✓ prose beyond the lookahead window is not paired with the total")


# --------------------------------------------------------------------------
# commit-anchors
# --------------------------------------------------------------------------

def test_commit_anchors_reconciles_the_count_against_git(tmp_path):
    """The count is measured with rev-list, never taken from the prose."""
    real = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "rev-list", "--count", "2c1f080..8c2fccb"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    assert real == "4", f"fixture assumption changed: {real}"

    ok = _write(
        tmp_path, "ok.md",
        "**Started at:** `2c1f080`\n"
        "**Finished at:** `8c2fccb`\n"
        "**Commits made this session:** 4\n",
    )
    assert cd.check_file(ok) == []

    bad = _write(
        tmp_path, "bad.md",
        "**Started at:** `2c1f080`\n"
        "**Finished at:** `8c2fccb`\n"
        "**Commits made this session:** 6\n",
    )
    findings = cd.check_file(bad)
    assert _rules(findings) == ["commit-anchors"], findings
    assert "declares 6 commit(s)" in findings[0].message, findings[0].message
    assert "is 4" in findings[0].message, findings[0].message
    print("✓ a declared commit count is reconciled against git rev-list")


def test_require_head_catches_the_real_stale_finish(tmp_path):
    """The session 9 defect: a header written early and never re-derived."""
    path = _write(
        tmp_path, "h.md",
        "**Started at:** `2c1f080`\n"
        "**Finished at:** `8c2fccb`\n"
        "**Commits made this session:** 4\n",
    )
    assert cd.check_file(path, require_head=False) == []
    findings = cd.check_file(path, require_head=True)
    assert _rules(findings) == ["commit-anchors"], findings
    assert "was not re-derived" in findings[0].message, findings[0].message
    print("✓ --require-head catches a stale finish an arithmetic check cannot")


def test_commit_anchors_checks_a_declared_tree_against_the_real_tree(tmp_path):
    """A tree hash copied forward from the previous session is caught here."""
    ok = _write(
        tmp_path, "ok.md",
        "**Finished at:** `8c2fccb`, tree "
        "`e85452ceb0d648a391b16a366b7696ef8c913afd`\n",
    )
    assert cd.check_file(ok) == []
    bad = _write(
        tmp_path, "bad.md",
        "**Finished at:** `8c2fccb`, tree "
        "`8e9e48370d0cc43bd904835eb688b76ee3f1d1c9`\n",
    )
    findings = cd.check_file(bad)
    assert _rules(findings) == ["commit-anchors"], findings
    assert "its real tree is e85452c" in findings[0].message, findings[0].message
    print("✓ a declared tree is checked against the commit's real tree")


def test_commit_anchors_reports_an_unresolvable_commit(tmp_path):
    """A record naming a commit this repo does not have is a defect, not a pass."""
    path = _write(
        tmp_path, "h.md",
        "**Finished at:** `deadbee`, tree "
        "`0000000000000000000000000000000000000000`\n",
    )
    findings = cd.check_file(path)
    assert _rules(findings) == ["commit-anchors"], findings
    assert "does not resolve" in findings[0].message, findings[0].message
    print("✓ an unresolvable declared commit is reported")


# --------------------------------------------------------------------------
# the instrument itself
# --------------------------------------------------------------------------

def test_the_modules_own_control_fires_then_goes_silent():
    """Rule 4: an absent signal is not a passing signal."""
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        ok, detail = cd.run_control(Path(tmp))
    assert ok, detail
    assert "fired 2 finding(s), then silent" in detail, detail
    print("✓ the module control fires on a planted defect, then goes silent")


def test_a_broken_rule_makes_the_control_fail_rather_than_pass(monkeypatch):
    """If a rule is disabled, the run must exit 2, not report a clean tree."""
    monkeypatch.setattr(cd, "check_fence_total", lambda path, lines: [])
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        ok, detail = cd.run_control(Path(tmp))
    assert not ok, "a disabled rule still reported a firing control"
    assert "fence-total did not fire" in detail, detail
    print("✓ disabling a rule fails the control instead of greening the run")


def test_tracked_records_come_from_git_ls_files():
    """Rule 4b and 4c: the set is enumerated, never assembled by hand."""
    records = cd.tracked_records()
    listed = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "ls-files", "docs"],
        capture_output=True, text=True, check=True,
    ).stdout.split()
    expected = {str(REPO_ROOT / p) for p in listed if p.endswith(".md")}
    assert set(records) == expected
    assert records, "the enumeration returned nothing, so the gate is blank"
    for record in records:
        assert Path(record).is_file(), record
    print(f"✓ {len(records)} tracked records, enumerated by git ls-files")


def test_the_rule_set_does_not_include_the_rejected_heuristic():
    """The Label:N pairing was 7/7 false positives. Do not add it back blind."""
    source = SCRIPT.read_text(encoding="utf-8")
    rules = {"sum-equals", "fence-total", "commit-anchors"}
    for rule in rules:
        assert f'"{rule}"' in source, rule
    assert "stated-count" not in source, (
        "a stated-count rule reappeared; it measured 7 false positives and 0 "
        "true positives on the tracked corpus, so re-measure before adding it"
    )
    print("✓ the rejected heuristic has not been reintroduced")


def test_the_tracked_corpus_is_clean_at_this_commit():
    """The gate is green on real records, and green because they reconcile."""
    findings = []
    for record in cd.tracked_records():
        findings.extend(cd.check_file(record))
    assert findings == [], "\n".join(str(f) for f in findings)
    print("✓ every tracked record reconciles at this commit")


def test_decomposition_cli_exit_codes(tmp_path):
    """Exit codes are the contract: 0 clean, 1 findings, 2 control failed.

    Named for this module rather than `test_cli_exit_codes`, which
    `tests/test_classification.py` already defines at its line 3231. Two
    same-named functions in two modules are not a double-count, but
    `tests/test_collection_integrity.py` cannot tell that from a runner
    rebind when one of the two modules is `test_classification.py`, and it
    failed here for exactly that reason. The name is the cheaper thing to
    change.
    """
    clean = _write(tmp_path, "clean.md", "The split is 7 + 15 + 18 = 40.\n")
    dirty = _write(tmp_path, "dirty.md", "The split is 7 + 15 + 21 = 40.\n")

    for path, expected in ((clean, 0), (dirty, 1)):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), path],
            capture_output=True, text=True,
        )
        assert result.returncode == expected, (
            f"{path} gave rc={result.returncode}, wanted {expected}\n"
            f"{result.stdout}{result.stderr}"
        )
        assert "control: fired 2 finding(s), then silent" in result.stdout

    missing = subprocess.run(
        [sys.executable, str(SCRIPT), str(tmp_path / "nope.md")],
        capture_output=True, text=True,
    )
    assert missing.returncode == 2, missing.stdout
    print("✓ rc=0 clean, rc=1 findings, rc=2 unusable input")


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
