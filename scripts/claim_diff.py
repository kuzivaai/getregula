#!/usr/bin/env python3
# regula-ignore
"""Classify each claim at HEAD as present at a base commit, or introduced.

WHY THIS EXISTS
---------------
`claim_auditor.py --diff-base main` scans whole files. Any file the diff
touches is scanned in full, so a branch that edits one line of a document
inherits every unsourced claim already in it. The proposed remedy is an
"introduced-claim condition": fail only on claims present at HEAD and absent
at the merge base. Whether that condition is sufficient is a measurement, not
an opinion, and this module is that measurement.

It is committed rather than left in a scratchpad on purpose. The F25 exposure
figure of 22/46 is unanswerable today because the script that produced it was
never committed, and an independent attempt got 29/53 on the same corpus at
the same commit. A number whose apparatus is gone is not a measurement.

CLAIM IDENTITY
--------------
A claim is keyed on **(repo-relative path, normalised claim text)**.

Normalisation lowercases, collapses runs of whitespace, and strips a trailing
full stop. It deliberately does NOT normalise digits, so 42.0% and 51% are
different claims.

The consequence, stated plainly: a paragraph edited so that its claim TEXT
changes reads as newly introduced. That is intended. See
docs/adr/0001-claim-identity.md for the argument and the rejected alternative.

Identity is on the claim snippet, not the paragraph, so editing prose around a
claim does not re-flag it. Only editing the claim itself does, and editing a
claim is re-asserting it.

HOLDING THE INSTRUMENT CONSTANT
-------------------------------
Claim DETECTION changed between b5ac95c8 and bf0c5d4: NUMERIC_CLAIM,
STRUCTURAL_REFS, is_exempt_number and strip_noise all differ. Running each
tree's own auditor would therefore change two variables at once, the content
and the detector, and measurement rule 2 forbids that. So this module runs ONE
detector, the one at HEAD, against BOTH content states.

That means copying HEAD's `claim_auditor.py` into the base worktree before
extracting. This is not the "measure with a copy" failure that rule 1 warns
about. That failure was REPO_ROOT resolving to a scratchpad, so repo-file
citations broke and sourced paragraphs counted as unsourced. Here REPO_ROOT
resolves to a complete, real checkout of the base commit, which is exactly the
tree being measured, and `_assert_repo_root` verifies it at runtime. Rule 1
says do not fork the instrument; holding one instrument against two specimens
is what rule 2 requires.

WHAT DID A COMMIT ADD TO THE MERGE BLOCKER?
-------------------------------------------
`--blocker-delta A B` answers it. The blocker read 274 unsourced at `f2de2ff`
and 279 at `2c1f080`, and nothing said which five findings appeared or why. A
session that adds to the blocker without naming what it added is the accounting
failure `docs/improvement/LEDGER.md` exists to prevent, and it could not be
answered by a committed command until this existed.

It scans `--diff-base main` inside a clean detached worktree of each commit and
diffs the two finding sets. Findings, not claims: `--base` above asks whether a
CLAIM existed at the base, which is a different question, and a claim that was
present but sourced at A and unsourced at B is a new FINDING while being an old
claim.

USAGE
  python3 scripts/claim_diff.py --base main
  python3 scripts/claim_diff.py --base main --json
  python3 scripts/claim_diff.py --blocker-delta f2de2ff 2c1f080
  python3 scripts/claim_diff.py --blocker-delta f2de2ff 2c1f080 --carry-instrument
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from contextlib import contextmanager
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import claim_auditor as ca  # noqa: E402
from gate_probe import (  # noqa: E402,F401
    TotalMismatch,
    content_signature,
    findings_over,
    reconcile,
)

REPO_ROOT = ca.REPO_ROOT

# What makes the gate's verdict, as opposed to what it reads. Copying these
# into both worktrees holds the INSTRUMENT constant so the only variable is the
# scanned content. Offered as an option rather than forced, because the honest
# reproduction of "the blocker said 274 there and 279 here" runs each commit
# with its own everything.
BLOCKER_INSTRUMENT = ("scripts/claim_auditor.py", ".claim-quarantine.json",
                      ".claim-allowlist")

# Bucket predicate. Shared so that any figure of the form "N of M are the
# programme's own working documents" is produced here rather than by hand.
# `data/published_count_manifest.json` lists docs/improvement/ under
# excluded_by_design as "programme working documents"; .claude/ is agent
# configuration.
BUCKETS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("docs/improvement/", ("docs/improvement/",)),
    ("benchmarks/ + docs/benchmarks/", ("benchmarks/", "docs/benchmarks/")),
    (".claude/rules/", (".claude/rules/",)),
)

_WS = re.compile(r"\s+")


def normalise_claim(text: str) -> str:
    """Canonical form of a claim snippet for identity purposes.

    Digits are NOT normalised. Changing 42.0% to 51% must read as a different
    claim, because it is one.
    """
    return _WS.sub(" ", text.strip().lower()).rstrip(".")


def claim_key(path: str, snippet: str) -> tuple[str, str]:
    return (path, normalise_claim(snippet))


def bucket_of(path: str) -> str:
    for label, prefixes in BUCKETS:
        if path.startswith(prefixes):
            return label
    return "everything else"


def _git(*args: str, cwd: Path) -> str:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True,
                          text=True, check=True).stdout


def _assert_repo_root(module, expected: Path) -> None:
    """Measurement rule 1. Fail loudly if the module resolved elsewhere."""
    if Path(module.REPO_ROOT).resolve() != expected.resolve():
        raise RuntimeError(
            f"{module.__name__}.REPO_ROOT is {module.REPO_ROOT}, expected "
            f"{expected}. Refusing to measure: every repo-file citation would "
            f"resolve against the wrong tree."
        )


def extract_claims(module, root: Path,
                   paths: list[str]) -> Counter[tuple[str, str]]:
    """Every claim the detector finds in `paths` under `root`, WITH COUNTS.

    Claims, not findings. The question this module answers is whether the same
    CLAIM existed at the base, regardless of whether it was sourced there.
    Sourcing is the gate's business; existence is identity's business.

    A MULTISET, not a set, and the difference is a defect this returned before
    2026-07-30. `claim_key` carries no line and no ordinal, so a set collapses
    every occurrence of one claim string in one file to a single element. Ask a
    set "was this claim at the base" and it answers yes when the base had it
    ONCE and the head has it TWICE, so the occurrence the branch actually
    introduced is classified as inherited and disappears from the introduced
    bucket. Counting instead of collapsing is the whole fix; see
    `classify_findings` for what is done with the counts, and for the one thing
    the counts still cannot decide.
    """
    _assert_repo_root(module, root)
    keys: Counter[tuple[str, str]] = Counter()
    for rel in paths:
        fp = root / rel
        if not fp.exists() or fp.suffix.lower() not in module.SCANNED_SUFFIXES:
            continue
        raw = fp.read_text(encoding="utf-8", errors="replace")
        cleaned = module.strip_noise(raw, fp.suffix.lower())
        for start, _end, para in module.split_paragraphs(cleaned):
            blocked: list[tuple[int, int]] = []
            for pat in module.STRUCTURAL_REFS:
                blocked += [(m.start(), m.end()) for m in pat.finditer(para)]
            tags = [(m.start(), m.end())
                    for m in module.HTML_TAG.finditer(para)]

            def blocked_at(pos: int) -> bool:
                return any(lo <= pos < hi for lo, hi in blocked)

            def in_tag(pos: int) -> bool:
                return any(lo <= pos < hi for lo, hi in tags)

            def add(kind: str, m) -> None:
                snip = m.group(0).strip()
                if kind == "numeric" and module.is_exempt_number(snip):
                    return
                if kind in ("numeric", "currency") and blocked_at(m.start()):
                    return
                if kind == "attributed" and in_tag(m.start()):
                    return
                keys[claim_key(rel, snip[:120])] += 1

            for m in module.NUMERIC_CLAIM.finditer(para):
                add("numeric", m)
            for m in module.CURRENCY_CLAIM.finditer(para):
                add("currency", m)
            for m in module.SUPERLATIVE_CLAIM.finditer(para):
                add("superlative", m)
            for m in module.ATTRIBUTED_CLAIM.finditer(para):
                add("attributed", m)
    return keys


def classify_findings(findings: list[dict],
                      base_counts: Counter) -> list[dict]:
    """Mark each finding present-at-base or introduced, and bucket it.

    The whole decision of this module, kept as a pure function of
    (findings, base_counts) so a test can drive it without a repository.
    Mutates in place and returns the same list for convenience.

    A MULTISET COMPARISON, and it used to be a set membership test. `claim_key`
    is `(file, normalised snippet)`: no line, no ordinal. Asking a set "is this
    key present at base" gives every occurrence of one claim string in one file
    the same answer, so a base that had the claim ONCE marks a head that has it
    TWICE as entirely inherited and the introduced occurrence vanishes. On the
    real tree at `509c997` the under-count was 0, because all 49 duplicated
    head keys sit in files the base does not have the claim in at all; the
    defect was LATENT, not active, and it is fixed on the strength of being
    reachable rather than on the strength of having bitten. This is the same
    root cause as N37, where a key that dropped the line produced a correct
    total of 70 and a wrong attribution.

    WHAT THE COUNTS STILL CANNOT DECIDE, stated rather than papered over. If a
    file had the claim twice at base and has it three times at head, exactly
    one occurrence is new and WHICH ONE cannot be decided from counts. Deciding
    it needs diff hunks, which `blocker_delta` reaches the same conclusion
    about and handles by refusing to pick. A per-finding boolean has to be
    assigned to something, so the surplus is assigned to the LAST occurrences
    in document order, and that is a DECLARED TIE-BREAK, not a measurement.
    Every finding in such a group carries `present_at_base_ambiguous: True` so
    a reader can tell a convention from a fact. Where the group is
    unambiguous, base 0 or head <= base, the flag is False.
    """
    if isinstance(base_counts, (set, frozenset)):
        # Refuse rather than coerce. Treating a set as "one of each" would
        # silently under-count the base side wherever it held a claim twice,
        # which turns this fix into a different wrong answer. A caller holding
        # a set has not re-derived it as a multiset and needs to know.
        raise TypeError(
            "classify_findings needs a multiset of base claim counts, not a "
            "set: a set collapses repeated occurrences of one claim in one "
            "file and is exactly the defect this signature was changed to "
            "prevent. Build it with extract_claims(), which returns a Counter."
        )

    by_key: dict[tuple[str, str], list[dict]] = {}
    for f in findings:
        f["bucket"] = bucket_of(f["file"])
        by_key.setdefault(claim_key(f["file"], f["snippet"]), []).append(f)

    for key, group in by_key.items():
        at_base = base_counts[key]
        introduced = max(0, len(group) - at_base)
        # Document order, so the tie-break is stable and reproducible rather
        # than dependent on dict iteration or on which pass produced the list.
        group.sort(key=lambda f: (f.get("line", 0), f.get("occurrence", 0)))
        ambiguous = at_base > 0 and introduced > 0
        for position, finding in enumerate(group):
            # The surplus is the TAIL of the group; see the docstring.
            finding["present_at_base"] = position < len(group) - introduced
            finding["present_at_base_ambiguous"] = ambiguous
    return findings


def findings_at_head(base: str) -> list[dict]:
    """The findings `--diff-base <base>` reports, as records."""
    _assert_repo_root(ca, REPO_ROOT)
    allow = ca.load_allowlist()
    out: list[dict] = []
    for fp in ca.files_diff_base(base):
        rep = ca.scan_file(fp, allow)
        for f in rep.findings:
            out.append({
                "file": rep.path,
                "line": f.claim.line,
                "kind": f.claim.kind,
                "snippet": f.claim.snippet,
                "reason": f.reason,
            })
    return out


def base_worktree(base_sha: str, tmp: Path) -> Path:
    """A clean checkout of `base_sha`, carrying HEAD's detector."""
    wt = tmp / "base"
    subprocess.run(["git", "worktree", "add", "--detach", str(wt), base_sha],
                   cwd=REPO_ROOT, capture_output=True, text=True, check=True)
    # One instrument, two specimens. See the module docstring.
    shutil.copy2(REPO_ROOT / "scripts" / "claim_auditor.py",
                 wt / "scripts" / "claim_auditor.py")
    return wt


def load_base_module(wt: Path):
    """Import the base worktree's auditor under a distinct module name.

    Registered in sys.modules BEFORE exec_module because @dataclass resolves
    its own module by name while the class body is being processed; without
    the registration it raises AttributeError on NoneType.
    """
    import importlib.util
    name = "claim_auditor_base"
    spec = importlib.util.spec_from_file_location(
        name, wt / "scripts" / "claim_auditor.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    try:
        spec.loader.exec_module(mod)
    except Exception:
        sys.modules.pop(name, None)
        raise
    return mod


def classify(base: str) -> dict:
    base_sha = _git("merge-base", base, "HEAD", cwd=REPO_ROOT).strip()
    head_sha = _git("rev-parse", "HEAD", cwd=REPO_ROOT).strip()
    findings = findings_at_head(base)
    paths = sorted({f["file"] for f in findings})

    tmp = Path(tempfile.mkdtemp(prefix="claim-diff-"))
    try:
        wt = base_worktree(base_sha, tmp)
        base_mod = load_base_module(wt)
        base_keys = extract_claims(base_mod, wt, paths)
    finally:
        subprocess.run(["git", "worktree", "remove", "--force",
                        str(tmp / "base")], cwd=REPO_ROOT,
                       capture_output=True, text=True, check=False)
        shutil.rmtree(tmp, ignore_errors=True)

    classify_findings(findings, base_keys)

    return {
        "head": head_sha,
        "base": base,
        "base_sha": base_sha,
        "tree": str(REPO_ROOT),
        "total": len(findings),
        "present_at_base": sum(1 for f in findings if f["present_at_base"]),
        "introduced": sum(1 for f in findings if not f["present_at_base"]),
        "base_claim_keys": len(base_keys),
        "findings": findings,
    }


# ---------------------------------------------------------------------------
# What did a commit add to the merge blocker?
# ---------------------------------------------------------------------------

@contextmanager
def commit_worktree(commit: str, carry: tuple[str, ...] = ()):
    """A clean detached worktree of `commit`, optionally carrying files in.

    `carry` names paths copied from THIS tree into the worktree after checkout.
    With `BLOCKER_INSTRUMENT` that holds the detector, the quarantine and the
    allowlist constant so the only variable left is the scanned content.
    """
    tmp = Path(tempfile.mkdtemp(prefix="blocker-delta-"))
    wt = tmp / "wt"
    try:
        subprocess.run(["git", "worktree", "add", "--detach", str(wt), commit],
                       cwd=REPO_ROOT, capture_output=True, text=True,
                       check=True)
        for rel in carry:
            src = REPO_ROOT / rel
            if src.exists():
                (wt / rel).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, wt / rel)
        yield wt
    finally:
        subprocess.run(["git", "worktree", "remove", "--force", str(wt)],
                       cwd=REPO_ROOT, capture_output=True, text=True,
                       check=False)
        shutil.rmtree(tmp, ignore_errors=True)


def blocker_findings(commit: str, base: str = "main",
                     carry: tuple[str, ...] = ()) -> dict:
    """The findings `--diff-base <base>` reports at `commit`.

    Run inside a detached worktree of that commit, so the corpus and the file
    contents are that commit's, not this working tree's. `--diff-base` reads
    WORKING TREE contents, so measuring a past commit from here would measure
    the present.
    """
    with commit_worktree(commit, carry) as wt:
        mod = load_base_module(wt)
        _assert_repo_root(mod, wt)
        corpus = [str(Path(p).relative_to(wt)) for p in mod.files_diff_base(base)]
        # `files_diff_base` returns every changed path; `scan_file` silently
        # skips the ones whose suffix it does not scan. Both numbers are
        # reported because the auditor's own summary line says "scanned 59
        # file(s)" and a report that only showed 159 here would look like a
        # different corpus.
        scanned = [p for p in corpus
                   if Path(p).suffix.lower() in mod.SCANNED_SUFFIXES]
        findings = findings_over(mod, wt, corpus)
        sha = _git("rev-parse", commit, cwd=REPO_ROOT).strip()
        tree = _git("rev-parse", f"{commit}^{{tree}}", cwd=REPO_ROOT).strip()
    return {"commit": sha, "tree": tree, "corpus": len(corpus),
            "scanned": len(scanned), "findings": findings}


def blocker_delta(older: str, newer: str, base: str = "main",
                  carry: tuple[str, ...] = ()) -> dict:
    """Findings the merge blocker gained and lost between two commits.

    A MULTISET DIFF on `gate_probe.content_signature`, which is
    `(file, kind, normalised snippet)` and carries no coordinates. Lines move
    between commits, so a line-keyed diff would report every finding below an
    insertion as removed and re-added. An occurrence ordinal cannot rescue that
    either: it is positionally unstable, and the measured instance of that
    defect is recorded in `gate_probe`'s docstring.

    ATTRIBUTION IS EXACT ONLY WHERE A SIGNATURE IS NEW. If a file already
    contained the same claim text and now contains it once more, which
    occurrence is the new one cannot be decided without reading diff hunks. Such
    rows carry `ambiguous: True` and list every line the signature occupies at
    the newer commit, rather than picking one and looking certain.
    """
    a = blocker_findings(older, base, carry)
    b = blocker_findings(newer, base, carry)
    a_counts = Counter(content_signature(f) for f in a["findings"])
    b_counts = Counter(content_signature(f) for f in b["findings"])
    b_lines: dict[tuple[str, str, str], list[int]] = {}
    a_lines: dict[tuple[str, str, str], list[int]] = {}
    for f in b["findings"]:
        b_lines.setdefault(content_signature(f), []).append(f["line"])
    for f in a["findings"]:
        a_lines.setdefault(content_signature(f), []).append(f["line"])

    def rows(gained: bool) -> list[dict]:
        out = []
        for sig in sorted(set(a_counts) | set(b_counts)):
            move = b_counts[sig] - a_counts[sig]
            if (move > 0) != gained or move == 0:
                continue
            file, kind, snippet = sig
            lines = sorted(b_lines.get(sig, []) if gained
                           else a_lines.get(sig, []))
            out.append({
                "file": file, "kind": kind, "snippet": snippet,
                "count": abs(move),
                "was": a_counts[sig], "now": b_counts[sig],
                "lines": lines,
                # Both sides, so an ambiguous row can be resolved by a reader
                # against the diff rather than left as a bare warning.
                "lines_older": sorted(a_lines.get(sig, [])),
                "lines_newer": sorted(b_lines.get(sig, [])),
                # Ambiguous when the signature already existed on the side it
                # is being attributed against: the occurrences are identical
                # text in one file and nothing here can tell them apart.
                "ambiguous": (a_counts[sig] if gained else b_counts[sig]) > 0,
            })
        return out

    added, removed = rows(True), rows(False)
    return {
        "older": a["commit"], "older_tree": a["tree"],
        "older_total": len(a["findings"]), "older_corpus": a["corpus"],
        "older_scanned": a["scanned"],
        "newer": b["commit"], "newer_tree": b["tree"],
        "newer_total": len(b["findings"]), "newer_corpus": b["corpus"],
        "newer_scanned": b["scanned"],
        "added": added, "removed": removed,
        "added_occurrences": sum(r["count"] for r in added),
        "removed_occurrences": sum(r["count"] for r in removed),
        "net": len(b["findings"]) - len(a["findings"]),
        "carried_instrument": list(carry),
    }


def _by_file(rows: list[dict]) -> list[tuple[str, int]]:
    tally: Counter = Counter()
    for r in rows:
        tally[r["file"]] += r["count"]
    return sorted(tally.items())


def report_blocker_delta(r: dict, out=print) -> None:
    """Print the delta. Every total reconciled against its own itemisation."""
    by_file_added = _by_file(r["added"])
    by_file_removed = _by_file(r["removed"])
    reconcile("findings added to the blocker", r["added_occurrences"],
              by_file_added)
    reconcile("findings removed from the blocker", r["removed_occurrences"],
              by_file_removed)
    # The net move has to equal added minus removed, or one of the three counts
    # is wrong. Stated as a reconciliation so it cannot be asserted in prose.
    reconcile("net movement, as added minus removed", r["net"],
              [("added", r["added_occurrences"]),
               ("removed", -r["removed_occurrences"])])

    out(f"older {r['older'][:7]}  tree {r['older_tree'][:7]}  "
        f"{r['older_corpus']} changed path(s), {r['older_scanned']} scanned  "
        f"{r['older_total']} finding(s)")
    out(f"newer {r['newer'][:7]}  tree {r['newer_tree'][:7]}  "
        f"{r['newer_corpus']} changed path(s), {r['newer_scanned']} scanned  "
        f"{r['newer_total']} finding(s)")
    out(f"instrument carried from this tree: "
        f"{r['carried_instrument'] or 'none, each commit ran its own'}")
    out("")
    for sign, label, rows_, by_file in (
            ("+", "added to", r["added"], by_file_added),
            ("-", "removed from", r["removed"], by_file_removed)):
        total = (r["added_occurrences"] if sign == "+"
                 else r["removed_occurrences"])
        out(f"findings {label} the blocker: {total}")
        for name, n in by_file:
            out(f"      {n:4d}  {name}")
        for f in sorted(rows_, key=lambda x: (x["file"], x["lines"])):
            where = ", ".join(str(n) for n in f["lines"])
            note = (f"  AMBIGUOUS: was {f['was']}x at "
                    f"{f['lines_older']}, now {f['now']}x at "
                    f"{f['lines_newer']}; which occurrence moved cannot be "
                    f"decided without reading diff hunks"
                    if f["ambiguous"] else "")
            out(f"  {sign} {f['file']}:{where}  [{f['kind']}] "
                f"{f['snippet']!r}  x{f['count']}{note}")
        out("")
    out(f"net movement, as added minus removed: {r['net']}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--base", default="main")
    ap.add_argument("--blocker-delta", nargs=2, metavar=("OLDER", "NEWER"),
                    help="findings the blocker gained and lost between two "
                         "commits")
    ap.add_argument("--carry-instrument", action="store_true",
                    help="with --blocker-delta: copy this tree's auditor, "
                         "quarantine and allowlist into both worktrees, so the "
                         "only variable is the scanned content")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.blocker_delta:
        carry = BLOCKER_INSTRUMENT if args.carry_instrument else ()
        r = blocker_delta(*args.blocker_delta, base=args.base, carry=carry)
        if args.json:
            print(json.dumps(r, indent=2))
            return 0
        report_blocker_delta(r)
        return 0

    r = classify(args.base)
    if args.json:
        print(json.dumps(r, indent=2))
        return 0

    print(f"HEAD {r['head'][:7]}  base {args.base} = {r['base_sha'][:7]}  "
          f"tree {r['tree']}")
    print(f"findings at HEAD          : {r['total']}")
    print(f"  present at merge base   : {r['present_at_base']}")
    print(f"  introduced by branch    : {r['introduced']}")
    print(f"distinct claim keys at base: {r['base_claim_keys']}")
    print()
    # Every count below comes from the predicate that built the set.
    labels = [lbl for lbl, _ in BUCKETS] + ["everything else"]
    width = max(len(x) for x in labels)
    print(f"  {'bucket'.ljust(width)}   total  at-base  introduced")
    for lbl in labels:
        rows = [f for f in r["findings"] if f["bucket"] == lbl]
        if not rows:
            continue
        at = sum(1 for f in rows if f["present_at_base"])
        print(f"  {lbl.ljust(width)}  {len(rows):6d}  {at:7d}  "
              f"{len(rows) - at:10d}")
    print(f"  {'TOTAL'.ljust(width)}  {r['total']:6d}  "
          f"{r['present_at_base']:7d}  {r['introduced']:10d}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
