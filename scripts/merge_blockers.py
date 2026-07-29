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

USAGE
  python3 scripts/merge_blockers.py                 # the residue, enumerated
  python3 scripts/merge_blockers.py --main-only     # would main go red?
  python3 scripts/merge_blockers.py --json
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import claim_auditor as ca      # noqa: E402
import claim_diff               # noqa: E402

REPO_ROOT = ca.REPO_ROOT

# A surface ships to a reader unless it is a programme working document or
# agent configuration. Deliberately NOT claim_diff's reporting buckets; see
# the module docstring for the error that distinction cost.
WORKING_PREFIXES = ("docs/improvement/", ".claude/")


def is_published_surface(path: str) -> bool:
    return not path.startswith(WORKING_PREFIXES)


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
    }


def main_only_findings() -> dict:
    """Run the published-surface predicate against a clean checkout of main.

    The published-surface condition does not consult a diff, so on main's own
    push trigger it scans main's tracked corpus. If that is non-empty, adding
    the condition turns the default branch red on the next push to it. This
    scans main ALONE, with no reference to the branch.
    """
    tmp = Path(tempfile.mkdtemp(prefix="merge-blockers-"))
    wt = tmp / "main"
    try:
        subprocess.run(["git", "worktree", "add", "--detach", str(wt), "main"],
                       cwd=REPO_ROOT, capture_output=True, text=True,
                       check=True)
        # One instrument, two specimens: HEAD's auditor against main's content,
        # so a difference cannot be the detector changing. Same reasoning as
        # scripts/claim_diff.py; REPO_ROOT is asserted below.
        shutil.copy2(REPO_ROOT / "scripts" / "claim_auditor.py",
                     wt / "scripts" / "claim_auditor.py")
        mod = claim_diff.load_base_module(wt)
        if Path(mod.REPO_ROOT).resolve() != wt.resolve():
            raise RuntimeError(
                f"REPO_ROOT is {mod.REPO_ROOT}, expected {wt}")
        corpus = _git("ls-files", "*.md", "*.html", cwd=wt).split()
        allow = mod.load_allowlist()
        hits = []
        for rel in corpus:
            if not is_published_surface(rel):
                continue
            rep = mod.scan_file(wt / rel, allow)
            for f in rep.findings:
                hits.append({
                    "file": rep.path, "line": f.claim.line,
                    "kind": f.claim.kind, "snippet": f.claim.snippet,
                    "reason": f.reason,
                })
        return {
            "main_sha": _git("rev-parse", "main", cwd=REPO_ROOT).strip(),
            "corpus": len(corpus),
            "published_surface_findings_on_main": len(hits),
            "files": sorted({h["file"] for h in hits}),
            "findings": hits,
        }
    finally:
        subprocess.run(["git", "worktree", "remove", "--force", str(wt)],
                       cwd=REPO_ROOT, capture_output=True, text=True,
                       check=False)
        shutil.rmtree(tmp, ignore_errors=True)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--base", default="main")
    ap.add_argument("--main-only", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.main_only:
        r = main_only_findings()
        if args.json:
            print(json.dumps(r, indent=2))
            return 0
        print(f"main {r['main_sha'][:7]}, clean worktree, "
              f"{r['corpus']} tracked md/html")
        print(f"published-surface findings ON MAIN: "
              f"{r['published_surface_findings_on_main']}")
        for rel in r["files"]:
            n = sum(1 for h in r["findings"] if h["file"] == rel)
            print(f"  {n:4d}  {rel}")
        if r["published_surface_findings_on_main"]:
            print("\nA published-surface condition that ignores the diff would "
                  "fail on main's own push trigger.")
        return 0

    r = residue(args.base)
    for f in r["residue"]:
        f["disposition"], f["why"] = disposition(f)
    from collections import Counter
    r["by_disposition"] = dict(Counter(f["disposition"] for f in r["residue"]))
    if args.json:
        print(json.dumps(r, indent=2))
        return 0
    print(f"HEAD {r['head'][:7]}  base {r['base_sha'][:7]}  tree {r['tree']}")
    print(f"total findings                    : {r['total']}")
    print(f"  survive introduced-claim alone  : {r['introduced_only']}")
    print(f"  survive published-surface alone : {r['published_only']}")
    print(f"  survive BOTH                    : {r['both']}")
    print()
    for f in sorted(r["residue"], key=lambda x: (x["file"], x["line"])):
        print(f"  [{f['disposition'].upper():9s}] {f['file']}:{f['line']} "
              f"{f['snippet']!r}")
    print()
    for k, v in sorted(r["by_disposition"].items()):
        print(f"  {k:10s} {v}")
    print(f"  {'TOTAL':10s} {r['both']}")
    print()
    for k in sorted(r["by_disposition"]):
        ex = next(f for f in r["residue"] if f["disposition"] == k)
        print(f"  {k}: {ex['why']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
