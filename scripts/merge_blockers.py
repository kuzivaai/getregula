#!/usr/bin/env python3
# regula-ignore
"""What would still block the merge under each candidate gate condition.

WHY THIS EXISTS
---------------
`scripts/claim_diff.py` established that the introduced-claim condition alone
leaves 226 findings and does not unblock the merge, and that both conditions
together leave a much smaller set. "A much smaller set" is not a decision
input. The owner is being asked to rule on owner decision 7 without knowing
what the residue actually is, or whether a mergeable state is reachable at all.

This module answers that. It enumerates the residue item by item, and it
measures the second consequence nobody had checked: whether a
published-surface condition, which by design ignores the diff, would fire on
`main` itself and turn the default branch red.

Committed rather than left in a scratchpad for the reason owner decision 3 is
still unanswerable: the F25 exposure figure of 22/46 cannot be re-derived
because its script was never kept.

THE TWO CONDITIONS
------------------
introduced-claim
    Fail only on a claim present at HEAD and absent at the merge base.
    Implemented by `claim_diff.classify_findings`.

published-surface
    Fail on any finding on a surface that ships to a reader, irrespective of
    the diff. Implemented by `is_published_surface` below: everything tracked
    EXCEPT programme working documents (`docs/improvement/`) and agent
    configuration (`.claude/`).

    A FIRST DRAFT OF THIS MODULE GOT THIS WRONG and the error is recorded
    because it changed the answer by a factor of five. It reused
    `claim_diff.bucket_of(path) == "everything else"`, which excludes
    `benchmarks/` and `docs/benchmarks/` as well, and reported 3 findings
    surviving the published-surface condition instead of 70. Those buckets
    exist in claim_diff for REPORTING, to show where the mass sits; they are
    not a statement that benchmarks documents are unpublished. They are
    tracked, they render on GitHub, and `docs/MODEL_CARD.md` cites
    `benchmarks/README.md` as the only repo-wide disclosure of the
    single-reviewer basis for the headline precision figure. A reader follows
    that link. It is published.

    `data/published_count_manifest.json` is NOT used here either. It lists ten
    surfaces, but it governs one specific figure, the published test count,
    not the whole class of published prose. Using it would under-count:
    `docs/QUICKSTART.md` and `docs/consultant-guide.md` ship to readers and
    are not on it.

THE CITATION-WORD ARM, AND WHY IT IS TOGGLED HERE
-------------------------------------------------
The 168 below is measured with `CITATION_WORDS` active, and that arm accepts
bare English prose (`source`, `see`, `ref`) as provenance and is tried before
the file-reference arm. Finding F25. So the 168 is a floor, not the debt, and a
ratchet baselined on it would be wrong the moment the arm is narrowed by the
gate-scope repair.

`--main-only --arm-delta` measures both states in ONE clean worktree of main,
with ONE variable toggled: `CITATION_WORDS` swapped for a pattern that cannot
match, nothing else changed. Two worktrees would be two specimens; one worktree
scanned twice is one specimen and one instrument, which is measurement rule 2.

USAGE
  python3 scripts/merge_blockers.py                 # the residue, enumerated
  python3 scripts/merge_blockers.py --main-only     # would main go red?
  python3 scripts/merge_blockers.py --main-only --arm-delta
                                                    # ... and how much of that
                                                    # green rests on F25
  python3 scripts/merge_blockers.py --json
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from contextlib import contextmanager
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import claim_auditor as ca      # noqa: E402
import claim_diff               # noqa: E402
# The shared probe. `ARM_OFF`, `reconcile`, `TotalMismatch` and the
# enumeration all used to live in this module, which put them out of reach of
# `claim_diff` without an import cycle and led `f25_exposure` to hold a second
# copy of the off-switch. They now live in a leaf module both sides import.
# Re-exported here under their old names so every existing caller and test
# keeps working; `scripts/gate_probe.py` is where they are defined.
from gate_probe import (        # noqa: E402,F401
    ARM_OFF,
    TotalMismatch,
    UnjoinedFinding,
    arm_delta,
    citation_word_rows,
    enumerate_revealed,
    finding_key,
    findings_over,
    reconcile,
)

REPO_ROOT = ca.REPO_ROOT

# A surface ships to a reader unless it is a programme working document or
# agent configuration. Deliberately NOT claim_diff's reporting buckets; see
# the module docstring for the error that distinction cost.
WORKING_PREFIXES = ("docs/improvement/", ".claude/")


def is_published_surface(path: str) -> bool:
    return not path.startswith(WORKING_PREFIXES)


# ---------------------------------------------------------------------------
# Every total this script prints is reconciled against its own itemisation
# ---------------------------------------------------------------------------
# WHAT PROMPTED THIS, AND WHAT DID NOT.
#
# `LEDGER.md` N12 recorded this script as reporting 168 published-surface
# findings on `main` "in 29 files", and the discrepancy between 168 and a
# 29-file listing was raised as a defect to find. MEASURED 2026-07-29, it does
# not reproduce:
#
#   at e48c4db, main tree:  files: 33  sum: 168
#   at 30acb23, the commit that ADDED this script and recorded the figure:
#                          files: 33  sum: 168
#
# The listing has always accounted for the total. The "29" was recorded without
# an apparatus and cannot be re-derived, which is the ledger's own rule about
# figures whose apparatus is gone.
#
# The check below is built anyway. "I could not reproduce the discrepancy" is
# not "the discrepancy cannot happen", and the whole reason N12 was hard to
# audit is that nothing forced a printed total to agree with the breakdown
# printed under it. Now every total goes through one door, and the itemisation
# it is checked against is the same list the reader is shown.


def _tally(findings: list[dict], key) -> list[tuple[str, int]]:
    """Group findings by `key` into a sorted (name, count) itemisation."""
    return sorted(Counter(key(f) for f in findings).items())


def _file_of(f: dict) -> str:
    return f["file"]


def _bucket_of(f: dict) -> str:
    return f["bucket"]


def _disposition_of(f: dict) -> str:
    return f["disposition"]


# ---------------------------------------------------------------------------
# Disposition of the residue
# ---------------------------------------------------------------------------
# Classifying a finding as fixable, inherited or contested is a judgement. The
# judgement is recorded here as predicates over the finding's own context so
# the COUNTS are mechanical, per the standing rule that a count of a set comes
# from the predicate that enumerated it and never from reading a listing.

WITHDRAWN_MARKER = "[NOT REPRODUCIBLE]"
# A document that says "NOT supported: any claim that X is 80% accurate" is
# disclaiming a figure, not asserting one. The gate cannot tell the difference
# and flags the disclaimer. That is a gate limitation, not a content defect.
DISCLAIMER_CUES = ("**NOT supported:**", "any claim that", "Do not generalise")


def paragraph_lines(rel: str, line: int) -> list[str]:
    """The raw lines of the paragraph containing `line`.

    Uses the auditor's own splitter, so this predicate's idea of a paragraph is
    the same as the gate's. `strip_noise` preserves line counts by design, so
    the coordinates from the cleaned text index the raw lines correctly.
    """
    try:
        raw = (REPO_ROOT / rel).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    cleaned = ca.strip_noise(raw, Path(rel).suffix.lower())
    lines = raw.splitlines()
    for start, end, _text in ca.split_paragraphs(cleaned):
        if start <= line <= end:
            return lines[start - 1:end]
    return []


def paragraph_carries_a_withdrawn_figure(para: list[str]) -> bool:
    """Does this paragraph contain a row already marked not reproducible?"""
    return any(WITHDRAWN_MARKER in ln for ln in para)


def disposition(finding: dict) -> tuple[str, str]:
    """Return (class, why) for one residual finding."""
    rel, line = finding["file"], finding["line"]
    try:
        lines = (REPO_ROOT / rel).read_text(encoding="utf-8",
                                            errors="replace").splitlines()
    except OSError:
        return "contested", "file unreadable"
    text = lines[line - 1] if 0 < line <= len(lines) else ""
    # the paragraph-ish window the disclaimer cue may sit in
    lo, hi = max(0, line - 4), min(len(lines), line + 2)
    window = "\n".join(lines[lo:hi])

    if WITHDRAWN_MARKER in text:
        return ("inherited",
                "row already marked [NOT REPRODUCIBLE]; this is finding N5. "
                "Sourcing it would be wrong. It needs withdrawing or making "
                "machine-visible, not a citation.")
    if any(cue in window for cue in DISCLAIMER_CUES):
        return ("contested",
                "the surrounding text is disclaiming this figure, not "
                "asserting it. Flagging a disclaimer is a gate limitation.")
    # SUPERLATIVE_CLAIM matches "nothing else" wherever it appears, including
    # "changing nothing else", which is experimental method describing a
    # controlled single-variable test. That is idiomatic English, not a
    # competitive assertion, and no citation would improve it.
    if "changing nothing else" in window or "nothing else changed" in window:
        return ("contested",
                "idiomatic use inside a controlled-experiment description, "
                "not a competitive assertion. Gate limitation.")
    if rel.startswith("docs/adr/"):
        return ("contested",
                "illustrative example inside a decision record, not a claim "
                "about the product. See the docs/adr bucket question in "
                "LEDGER.md.")
    # A citation sources a PARAGRAPH, not a line. `paragraph_has_source` is
    # evaluated once per paragraph and every claim inside inherits the verdict.
    # So if the only place a citation can go also sits beside a figure that has
    # been withdrawn, sourcing this one necessarily cites the withdrawn one,
    # and citing a withdrawn figure is worse than leaving it unsourced.
    #
    # MEASURED 2026-07-29 at e48c4db: RESULTS-synthetic-v2-2026-07-28.md:37
    # (`33%`, reproducible, backed by benchmarks/synthetic/RECALL.json) shares
    # paragraph 35-39 with :38 and :39, both marked [NOT REPRODUCIBLE] and both
    # classed `inherited` by the arm above. The disposition predicate ran per
    # finding while the remedy operates per paragraph, so `fixable` was
    # over-counted by one. Found by attempting the fix, not by reading.
    if paragraph_carries_a_withdrawn_figure(paragraph_lines(rel, line)):
        return ("blocked",
                "a real figure whose paragraph also holds a row marked "
                "[NOT REPRODUCIBLE]. Sourcing is paragraph-granular, so the "
                "citation that would source this figure would also cite the "
                "withdrawn one. Not fixable by sourcing. It needs the "
                "withdrawn rows moved into a paragraph of their own, which is "
                "a presentation change and the owner's call.")
    return ("fixable",
            "a real figure on a published surface with no in-paragraph "
            "provenance. Derivable from the artefact it came from.")


def _git(*args: str, cwd: Path) -> str:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True,
                          text=True, check=True).stdout


def residue(base: str = "main") -> dict:
    """Findings surviving BOTH conditions, enumerated one by one."""
    r = claim_diff.classify(base)
    both = [f for f in r["findings"]
            if not f["present_at_base"] and is_published_surface(f["file"])]
    pub_only = [f for f in r["findings"] if is_published_surface(f["file"])]
    intro_only = [f for f in r["findings"] if not f["present_at_base"]]
    return {
        "head": r["head"], "base_sha": r["base_sha"], "tree": r["tree"],
        "total": r["total"],
        "introduced_only": len(intro_only),
        "published_only": len(pub_only),
        "both": len(both),
        "residue": both,
        # The three subsets are carried so every printed total has an
        # itemisation to be reconciled against. `total` is checked against the
        # full finding list rather than against itself, so a disagreement
        # between claim_diff's reported total and the records it returned is
        # caught here instead of being printed.
        "all_findings": r["findings"],
        "introduced": intro_only,
        "published": pub_only,
    }


@contextmanager
def main_worktree():
    """A clean, detached worktree of `main`, with HEAD's auditor copied in.

    One instrument, two specimens: HEAD's auditor against main's content, so a
    difference cannot be the detector changing. Same reasoning as
    `scripts/claim_diff.py`; `REPO_ROOT` is asserted before anything is scanned,
    because a module whose root resolved elsewhere is exactly how the figures
    185 and 168 were produced in an earlier session.

    Factored out of `main_only_findings` so the arm-delta measurement runs both
    of its passes inside ONE worktree. Two worktrees of the same commit are
    byte-identical today, but they are two specimens, and measurement rule 2 is
    one variable on one state.
    """
    tmp = Path(tempfile.mkdtemp(prefix="merge-blockers-"))
    wt = tmp / "main"
    try:
        subprocess.run(["git", "worktree", "add", "--detach", str(wt), "main"],
                       cwd=REPO_ROOT, capture_output=True, text=True,
                       check=True)
        shutil.copy2(REPO_ROOT / "scripts" / "claim_auditor.py",
                     wt / "scripts" / "claim_auditor.py")
        mod = claim_diff.load_base_module(wt)
        if Path(mod.REPO_ROOT).resolve() != wt.resolve():
            raise RuntimeError(
                f"REPO_ROOT is {mod.REPO_ROOT}, expected {wt}")
        yield wt, mod
    finally:
        subprocess.run(["git", "worktree", "remove", "--force", str(wt)],
                       cwd=REPO_ROOT, capture_output=True, text=True,
                       check=False)
        shutil.rmtree(tmp, ignore_errors=True)


def _published_paths(wt: Path) -> tuple[list[str], list[str]]:
    """(every tracked md/html path in `wt`, the published-surface subset)."""
    corpus = _git("ls-files", "*.md", "*.html", cwd=wt).split()
    return corpus, [rel for rel in corpus if is_published_surface(rel)]


def _scan_published(wt: Path, mod) -> tuple[list[str], list[dict]]:
    """(tracked md/html corpus, published-surface findings) inside `wt`.

    Delegates to `gate_probe.findings_over`, the same predicate
    `scripts/f25_exposure.py` uses against this branch's working tree. One
    question, one enumerator: a second one here would drift the way two
    off-switches would.
    """
    corpus, published = _published_paths(wt)
    return corpus, findings_over(mod, wt, published)


def main_only_findings() -> dict:
    """Run the published-surface predicate against a clean checkout of main.

    The published-surface condition does not consult a diff, so on main's own
    push trigger it scans main's tracked corpus. If that is non-empty, adding
    the condition turns the default branch red on the next push to it. This
    scans main ALONE, with no reference to the branch.
    """
    with main_worktree() as (wt, mod):
        corpus, hits = _scan_published(wt, mod)
        return {
            "main_sha": _git("rev-parse", "main", cwd=REPO_ROOT).strip(),
            "corpus": len(corpus),
            "published_surface_findings_on_main": len(hits),
            "files": sorted({h["file"] for h in hits}),
            "findings": hits,
        }


def main_only_arm_delta() -> dict:
    """main's published-surface debt with the citation-word arm on and off.

    The missing input to owner decision 7. A ratchet baselined on the arm-on
    figure is baselined on a number the gate-scope repair is going to move,
    because narrowing `CITATION_WORDS` is part of that repair.

    ONE worktree, ONE auditor module, TWO scans, ONE variable: `CITATION_WORDS`
    replaced by `ARM_OFF` and restored in a `finally` so an exception cannot
    leave the module patched. Switching an arm OFF can only remove provenance,
    so the finding set can only grow; if anything disappeared the toggle did
    something other than what this function claims, and `reconcile_arm_delta`
    refuses to print the figures.
    """
    with main_worktree() as (wt, mod):
        corpus, published = _published_paths(wt)
        delta = arm_delta(mod, wt, published)
        rows = citation_word_rows(mod, wt, published)
        # The per-finding enumeration, from the SAME predicate that answers the
        # question for the branch. Raises `UnjoinedFinding` if a revealed
        # finding does not sit in a paragraph this run recorded as sourced by
        # the citation-word arm, and reconciles its own length against the
        # difference of the two independently counted gate totals.
        listed = enumerate_revealed(rows, delta)
        main_sha = _git("rev-parse", "main", cwd=REPO_ROOT).strip()

    return {
        "main_sha": main_sha,
        "corpus": len(corpus),
        "published_corpus": len(published),
        "arm_on": delta["findings_now"],
        "arm_off": delta["findings_with_arm_off"],
        "revealed": len(delta["revealed"]),
        "findings_arm_on": delta["findings_arm_on"],
        "findings_arm_off": delta["findings_arm_off"],
        "revealed_findings": listed,
        "no_longer_reported": delta["no_longer_reported"],
        "paragraphs": rows["paragraphs"],
        "sourced_paragraphs": rows["sourced_paragraphs"],
        "citation_word_paragraphs": len(rows["rows"]),
        "citation_word_exposed": sum(1 for r in rows["rows"] if r["exposed"]),
    }


def reconcile_arm_delta(r: dict) -> list[tuple[str, int, list[tuple[str, int]]]]:
    """Every total the arm-delta report prints, each with its itemisation.

    Returned rather than printed, so the reconciliation and the output cannot
    drift apart: the caller prints exactly what was checked.
    """
    rows = [
        ("published-surface findings ON MAIN, citation-word arm ON",
         r["arm_on"], _tally(r["findings_arm_on"], _file_of)),
        ("published-surface findings ON MAIN, citation-word arm OFF",
         r["arm_off"], _tally(r["findings_arm_off"], _file_of)),
        ("revealed by switching the citation-word arm off",
         r["revealed"], _tally(r["revealed_findings"], _file_of)),
        # Direction check. An arm that is switched off cannot ADD provenance,
        # so this itemisation must be empty and the total must be zero. If it
        # is not, the toggle changed something else and none of the three
        # figures above may be published.
        ("findings the arm off would stop reporting",
         len(r["no_longer_reported"]), []),
    ]
    for label, total, items in rows:
        reconcile(label, total, items)
    return rows


def report_arm_delta(r: dict, out=print) -> None:
    rows = reconcile_arm_delta(r)
    out(f"main {r['main_sha'][:7]}, clean worktree, "
        f"{r['corpus']} tracked md/html")
    for label, total, items in rows:
        out(f"{label}: {total}")
        for name, n in items:
            out(f"      {n:4d}  {name}")
    out("")
    for f in sorted(r["revealed_findings"],
                    key=lambda x: (x["file"], x["line"], x["snippet"])):
        out(f"  {f['file']}:{f['line']}  [{f['kind']}] {f['snippet']!r}  "
            f"sourced by: {', '.join(f['citation_words'])}")


def report_main_only(r: dict, out=print) -> None:
    """Print the main-only result. Reconciles before emitting a single line."""
    breakdown = reconcile("published-surface findings ON MAIN",
                          r["published_surface_findings_on_main"],
                          _tally(r["findings"], _file_of))
    out(f"main {r['main_sha'][:7]}, clean worktree, "
        f"{r['corpus']} tracked md/html")
    out(f"published-surface findings ON MAIN: "
        f"{r['published_surface_findings_on_main']}")
    for rel, n in breakdown:
        out(f"  {n:4d}  {rel}")
    # Deliberately NOT formatted as "<spaces><count>  <name>". A line-based sum
    # over this output treats any such line as an item, so a summary line in
    # that shape would be added to the very total it reports. Observed while
    # building this: the awk one-liner used to audit the figure read 34 files
    # summing to 201 because it counted the summary as a 33-finding file.
    out(f"reconciled: {len(breakdown)} files account for "
        f"{r['published_surface_findings_on_main']} findings")
    if r["published_surface_findings_on_main"]:
        out("\nA published-surface condition that ignores the diff would "
            "fail on main's own push trigger.")


def reconcile_residue(r: dict) -> list[tuple[str, int, list[tuple[str, int]]]]:
    """Every total the residue report prints, each with its itemisation.

    Returned rather than printed so the reconciliation and the output cannot
    drift apart: the caller prints exactly what was checked.
    """
    rows = [
        ("total findings", r["total"], _tally(r["all_findings"], _bucket_of)),
        ("survive introduced-claim alone", r["introduced_only"],
         _tally(r["introduced"], _bucket_of)),
        ("survive published-surface alone", r["published_only"],
         _tally(r["published"], _bucket_of)),
        ("survive BOTH", r["both"], _tally(r["residue"], _file_of)),
    ]
    for label, total, items in rows:
        reconcile(label, total, items)
    # `survive BOTH` is printed three times over: as a number, as one line per
    # finding, and as a disposition tally. All three are itemisations of the
    # same total, so all three are checked.
    reconcile("survive BOTH, itemised one finding per line",
              r["both"], [(f["file"], 1) for f in r["residue"]])
    reconcile("survive BOTH, by disposition",
              r["both"], _tally(r["residue"], _disposition_of))
    return rows


def report_residue(r: dict, out=print) -> None:
    rows = reconcile_residue(r)
    out(f"HEAD {r['head'][:7]}  base {r['base_sha'][:7]}  tree {r['tree']}")
    for label, total, items in rows:
        out(f"{label:34s}: {total}")
        for name, n in items:
            out(f"      {n:4d}  {name}")
    out("")
    for f in sorted(r["residue"], key=lambda x: (x["file"], x["line"])):
        out(f"  [{f['disposition'].upper():9s}] {f['file']}:{f['line']} "
            f"{f['snippet']!r}")
    out("")
    for k, v in sorted(_tally(r["residue"], _disposition_of)):
        out(f"  {k:10s} {v}")
    out(f"  {'TOTAL':10s} {r['both']}")
    out("")
    for k, _v in sorted(_tally(r["residue"], _disposition_of)):
        ex = next(f for f in r["residue"] if f["disposition"] == k)
        out(f"  {k}: {ex['why']}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--base", default="main")
    ap.add_argument("--main-only", action="store_true")
    ap.add_argument("--arm-delta", action="store_true",
                    help="with --main-only: measure the same corpus twice, "
                         "with the F25 citation-word arm on and off")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.arm_delta and not args.main_only:
        print("merge-blockers: --arm-delta is only defined with --main-only",
              file=sys.stderr)
        return 2

    if args.main_only and args.arm_delta:
        r = main_only_arm_delta()
        if args.json:
            reconcile_arm_delta(r)
            print(json.dumps(r, indent=2))
            return 0
        report_arm_delta(r)
        return 0

    if args.main_only:
        r = main_only_findings()
        if args.json:
            # Reconciled before serialising too: a JSON consumer gets the same
            # guarantee as a human reader, not a weaker one.
            reconcile("published-surface findings ON MAIN",
                      r["published_surface_findings_on_main"],
                      _tally(r["findings"], _file_of))
            print(json.dumps(r, indent=2))
            return 0
        report_main_only(r)
        return 0

    r = residue(args.base)
    for f in r["residue"]:
        f["disposition"], f["why"] = disposition(f)
    r["by_disposition"] = dict(_tally(r["residue"], _disposition_of))
    if args.json:
        reconcile_residue(r)
        serialisable = {k: v for k, v in r.items()
                        if k not in ("all_findings", "introduced", "published")}
        print(json.dumps(serialisable, indent=2))
        return 0
    report_residue(r)
    return 0


if __name__ == "__main__":
    from tree_guard import stamp
    stamp()
    raise SystemExit(main())
