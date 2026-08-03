#!/usr/bin/env python3
# regula-ignore
"""Reconcile stated decompositions against the totals they claim to explain.

WHY THIS EXISTS.

Two defects in the session 9 records had, at first glance, one shape: a
decomposition stated in prose sitting beside a total produced by a command,
with nothing checking that the two agreed.

    "72 passed"  ...  "That is 7 + 15 + 15 + 21 + 17 against ... before."

That sums to 75, not 72. The misattributed file was
`tests/test_claim_diff.py`, stated at 21 and actually 18.

The second defect turned out NOT to be that shape, and finding that out is
the reason this file has three rules rather than one. A handover header
declared four commits and a finish at `41feb51`. Six commits appeared in its
own itemisation. But `git rev-list --count 9e6b6de..41feb51` is 4, so the
count was internally consistent with its own declared finish. The defect was
that the **declared finish commit was stale**: `190da47` and `ef2b8de`
landed after the header was written and the header was never re-derived.
An arithmetic check would never have caught it. A reconciliation against
the repository catches it immediately.

WHAT WAS TRIED AND REJECTED, so a later session does not repeat it.

A fourth rule was prototyped and abandoned: pair any `Label: N`
declaration with any nearby itemisation by matching the label against
section headings, then compare N to the item count. Measured against the
tracked `docs/**/*.md` corpus it produced **seven findings, all seven
false**, and **zero** true positives:

    docs/benchmarks/PRECISION_RECALL_2026_04.md:305  "OSS corpus" 15 vs 8
    docs/improvement/CODE_REVIEW.md:387              "README" 161 vs 2
    docs/improvement/STATE.md:415                    "NEXT" 1 vs 2
    docs/installation.md:237                         "Files scanned" 0 vs 1

`Label: N` in this corpus is overwhelmingly not a count of an itemised set:
it is a line number, a section pointer, or pasted sample CLI output. The
pairing cannot be inferred from proximity or from heading text. It can only
be checked when the record states the anchors explicitly, which is what
rule `commit-anchors` requires and why that rule is narrow.

THE RULES.

`sum-equals`     An explicit `a + b + ... = T` must sum to T.
`fence-total`    A fenced block whose trailing summary line states a total,
                 followed within a short window by prose carrying additive
                 decompositions: at least one must equal the total. Multiple
                 decompositions on one line are common ("N against M
                 before"), so any match satisfies the rule.
`commit-anchors` A record declaring a start commit, a finish commit and a
                 commit count must satisfy count == rev-list start..finish,
                 every declared tree must be that commit's real tree, and
                 under --require-head the finish must be HEAD.

FALSE POSITIVE BASIS, measured not assumed. At the commit this file was
added, `sum-equals` finds 8 statements in tracked `docs/**/*.md` and all 8
are arithmetically correct, and `fence-total` finds 0 pairings there. So
both rules are green on the corpus rather than green because they are
inert, and the control below proves they are not inert.

Usage:
    python3 scripts/check_decompositions.py                 # tracked records
    python3 scripts/check_decompositions.py FILE [FILE ...] # named files too
    python3 scripts/check_decompositions.py --require-head FILE
    python3 scripts/check_decompositions.py --control-only

Exit 0 = control fired and nothing to report. Exit 1 = findings.
Exit 2 = the control did not fire, so the run proves nothing.

Stdlib only.
"""

import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

REPO_ROOT = Path(__file__).resolve().parent.parent

# A decomposition: two or more numbers joined by "+". Integers and decimals,
# thousands separators allowed. The lookbehind stops the match starting
# mid-number, so "222353" cannot be read as a component.
DECOMP = re.compile(
    r"(?<![\d.,])(\d[\d,]*(?:\.\d+)?(?:\s*\+\s*\d[\d,]*(?:\.\d+)?)+)"
)

# A timezone offset is not arithmetic. Mask the whole ISO timestamp before
# looking for decompositions so e.g. ``2026-08-01T14:00:06+01:00`` cannot be
# read as ``06+01``. Requiring the date, time, and offset keeps this narrower
# than ignoring arbitrary plus signs beside numbers.
ISO_TIMESTAMP = re.compile(
    r"\b\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})\b"
)


def _without_iso_timestamps(text):
    """Replace ISO timestamps with spaces while preserving match offsets."""
    return ISO_TIMESTAMP.sub(lambda match: " " * len(match.group(0)), text)

# "a + b + ... = T", tolerating markdown bold on the total.
SUM_EQUALS = re.compile(
    DECOMP.pattern + r"\s*=\s*\*{0,2}\s*(\d[\d,]*(?:\.\d+)?)"
)

# Totals this programme actually pastes out of commands. Anchored on a noun so
# that a bare number in a fence is never mistaken for the total.
TOTAL_ANCHOR = re.compile(
    r"\b(\d[\d,]*)\s+(?:passed|findings?|unsourced|claims?|patterns?"
    r"|tests?|files?|occurrences?|commits?)\b"
)

FENCE = re.compile(r"^\s*```")

# How far back inside a closing fence to look for the summary line, and how far
# forward into prose to look for the decomposition that explains it.
LOOKBACK = 8
LOOKAHEAD = 4

SHA = r"([0-9a-f]{7,40})"
STARTED_AT = re.compile(r"\*{0,2}Started at:?\*{0,2}\s*`?" + SHA, re.I)
FINISHED_AT = re.compile(r"\*{0,2}Finished at:?\*{0,2}\s*`?" + SHA, re.I)
COMMIT_COUNT = re.compile(
    r"\*{0,2}Commits (?:made )?(?:this session|in this session):?\*{0,2}\s*"
    r"\*{0,2}\s*(\d{1,3})\b",
    re.I,
)
# "tree `<40 hex>`" on the same line as a declared commit anchor.
TREE_ON_LINE = re.compile(r"tree\s*`?([0-9a-f]{40})", re.I)


def _num(text):
    """Parse a claim number: strip thousands separators, keep the decimal."""
    return float(text.replace(",", ""))


def _fmt(value):
    """Render a parsed number the way the document would have written it."""
    return f"{value:g}"


def _components(expression):
    return [_num(p) for p in re.split(r"\s*\+\s*", expression)]


def _agrees(left, right):
    """Compare two claim numbers. Tolerance covers one-decimal-place prose."""
    return abs(left - right) < 0.005


class Finding:
    """One reconciliation failure, carrying enough to name the gap."""

    def __init__(self, path, line, rule, message):
        self.path = path
        self.line = line
        self.rule = rule
        self.message = message

    def __str__(self):
        return f"{self.path}:{self.line} [{self.rule}] {self.message}"


def check_sum_equals(path, lines):
    """Rule sum-equals: an explicit a + b + ... = T must sum to T."""
    findings = []
    for index, line in enumerate(lines, 1):
        for match in SUM_EQUALS.finditer(_without_iso_timestamps(line)):
            parts = _components(match.group(1))
            stated = _num(match.group(2))
            if not _agrees(sum(parts), stated):
                findings.append(
                    Finding(
                        path,
                        index,
                        "sum-equals",
                        f"'{match.group(1)}' sums to {_fmt(sum(parts))}, "
                        f"stated total is {_fmt(stated)}, "
                        f"gap {_fmt(sum(parts) - stated)}",
                    )
                )
    return findings


def check_fence_total(path, lines):
    """Rule fence-total: a pasted total must be explained by prose beside it."""
    findings = []
    in_fence = False
    for index, line in enumerate(lines):
        if not FENCE.match(line):
            continue
        in_fence = not in_fence
        if in_fence:
            continue

        # The fence just closed. Find the total it reported, if any.
        total = None
        for back in range(index - 1, max(-1, index - 1 - LOOKBACK), -1):
            match = TOTAL_ANCHOR.search(lines[back])
            if match:
                total = _num(match.group(1))
                break
        if total is None:
            continue

        # Look at the prose immediately after it for a decomposition.
        for forward in range(index + 1, min(len(lines), index + 1 + LOOKAHEAD)):
            if FENCE.match(lines[forward]):
                break
            matches = list(
                DECOMP.finditer(_without_iso_timestamps(lines[forward]))
            )
            if not matches:
                continue
            sums = [(m.group(1), sum(_components(m.group(1)))) for m in matches]
            if any(_agrees(value, total) for _, value in sums):
                break
            detail = ", ".join(
                f"'{expr}' sums to {_fmt(value)}" for expr, value in sums
            )
            findings.append(
                Finding(
                    path,
                    forward + 1,
                    "fence-total",
                    f"pasted total is {_fmt(total)} but no decomposition "
                    f"beside it agrees: {detail}",
                )
            )
            break
    return findings


def _git(*args):
    """Run git in the repo. Returns stripped stdout, or None if it failed."""
    result = subprocess.run(
        ["git", "-C", str(REPO_ROOT), *args],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def check_commit_anchors(path, lines, require_head=False):
    """Rule commit-anchors: reconcile a record's commit claims against git.

    This is the rule that catches a stale header. It is deliberately narrow:
    it fires only where the record states its anchors, because inferring the
    pairing was measured to be all false positives. See the module docstring.
    """
    findings = []
    start = finish = count = None
    start_line = finish_line = count_line = None

    for index, line in enumerate(lines, 1):
        match = STARTED_AT.search(line)
        if match and start is None:
            start, start_line = match.group(1), index
        match = FINISHED_AT.search(line)
        if match and finish is None:
            finish, finish_line = match.group(1), index
        match = COMMIT_COUNT.search(line)
        if match and count is None:
            count, count_line = int(match.group(1)), index

        # Any line declaring a commit and a tree must state that commit's
        # real tree. This is how a copied-forward tree hash gets caught.
        anchor = STARTED_AT.search(line) or FINISHED_AT.search(line)
        tree = TREE_ON_LINE.search(line)
        if anchor and tree:
            real = _git("rev-parse", f"{anchor.group(1)}^{{tree}}")
            if real is None:
                findings.append(
                    Finding(
                        path,
                        index,
                        "commit-anchors",
                        f"declared commit {anchor.group(1)} does not resolve "
                        f"in this repository",
                    )
                )
            elif not real.startswith(tree.group(1)) and not tree.group(
                1
            ).startswith(real):
                findings.append(
                    Finding(
                        path,
                        index,
                        "commit-anchors",
                        f"commit {anchor.group(1)} declares tree "
                        f"{tree.group(1)[:7]} but its real tree is "
                        f"{real[:7]}",
                    )
                )

    if start and finish and count is not None:
        measured = _git("rev-list", "--count", f"{start}..{finish}")
        if measured is None:
            findings.append(
                Finding(
                    path,
                    count_line,
                    "commit-anchors",
                    f"cannot reconcile: {start}..{finish} does not resolve",
                )
            )
        elif int(measured) != count:
            findings.append(
                Finding(
                    path,
                    count_line,
                    "commit-anchors",
                    f"declares {count} commit(s) but "
                    f"git rev-list --count {start}..{finish} is {measured}",
                )
            )

    if require_head and finish:
        head = _git("rev-parse", "HEAD")
        if head and not head.startswith(finish):
            findings.append(
                Finding(
                    path,
                    finish_line,
                    "commit-anchors",
                    f"declares finish {finish} but HEAD is {head[:7]}: the "
                    f"header was not re-derived at the end of the session",
                )
            )
    return findings


def check_file(path, require_head=False):
    """Run every rule over one file. `path` is used verbatim in findings."""
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    return (
        check_sum_equals(path, lines)
        + check_fence_total(path, lines)
        + check_commit_anchors(path, lines, require_head=require_head)
    )


def tracked_records():
    """Enumerate the tracked markdown records, by predicate not by hand.

    `.claude/rules/measurement.md` rule 4b: untracked files are not surfaces.
    Rule 4c: a set behind a completeness claim comes from git ls-files.
    """
    output = _git("ls-files", "docs")
    if output is None:
        return []
    return sorted(
        str(REPO_ROOT / line)
        for line in output.splitlines()
        if line.endswith(".md")
    )


CONTROL_BAD = """# Control

```
$ python3 -m pytest -q
72 passed in 9.09s
```

That is 7 + 15 + 15 + 21 + 17 against 0 + 15 + 14 + 16 + 17 before.

The split is 2 + 2 = 5 overall.
"""

CONTROL_GOOD = """# Control

```
$ python3 -m pytest -q
72 passed in 9.09s
```

That is 7 + 15 + 15 + 18 + 17 against 0 + 15 + 14 + 16 + 17 before.

The split is 2 + 3 = 5 overall.
"""


def run_control(tmp_dir):
    """Prove both arithmetic rules can fire, and can also stay silent.

    An absent signal is not a passing signal, so this plants the real session
    9 defect and requires it to be reported, then repairs it and requires
    silence. Returns (ok, detail).
    """
    bad = tmp_dir / "control_bad.md"
    good = tmp_dir / "control_good.md"
    bad.write_text(CONTROL_BAD, encoding="utf-8")
    good.write_text(CONTROL_GOOD, encoding="utf-8")

    fired = check_file(str(bad))
    rules_fired = {f.rule for f in fired}
    if "fence-total" not in rules_fired:
        return False, "control: fence-total did not fire on a planted mismatch"
    if "sum-equals" not in rules_fired:
        return False, "control: sum-equals did not fire on a planted mismatch"

    silent = check_file(str(good))
    if silent:
        detail = "; ".join(str(f) for f in silent)
        return False, f"control: repaired file still reported: {detail}"
    return True, f"control: fired {len(fired)} finding(s), then silent"


def main(argv):
    require_head = "--require-head" in argv
    control_only = "--control-only" in argv
    paths = [a for a in argv if not a.startswith("--")]

    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        ok, detail = run_control(Path(tmp))
    print(detail)
    if not ok:
        print("check-decompositions: CONTROL FAILED, this run proves nothing")
        return 2
    if control_only:
        return 0

    targets = paths if paths else tracked_records()
    findings = []
    for target in targets:
        if not Path(target).is_file():
            print(f"check-decompositions: no such file: {target}")
            return 2
        findings.extend(check_file(target, require_head=require_head))

    print(
        f"check-decompositions: scanned {len(targets)} record(s), "
        f"{len(findings)} finding(s)"
    )
    for finding in findings:
        print(f"  {finding}")
    if findings:
        print(
            "\nFix: re-derive the decomposition from the command that produced "
            "the total, and correct whichever side is wrong. Do not adjust the "
            "total to match the prose."
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
