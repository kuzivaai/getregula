#!/usr/bin/env python3
# regula-ignore
"""How much provenance rests on an ordinary English word. Finding F25.

WHY THIS EXISTS
---------------
`paragraph_has_source()` tries its arms in order and the first match wins.
`CITATION_WORDS` is tried BEFORE the file-reference arm, and it matches bare
prose: `source`, `see`, `ref`, `reference`, `cf.`, `verdict:`. So a paragraph
that says "see the table below" is recorded as sourced, and a paragraph that
carries a real, tracked file citation next to the word "see" is recorded as
sourced BY THE WORD, with the real citation never reached.

Owner decision 3 asks how far that reaches. It has been unanswerable for five
sessions for one reason: the recorded exposure figure **22 / 46** cannot be
re-derived, because the script that produced it was never committed. An
independent pass on what was believed to be the same corpus at the same commit
gave **29 / 53**. Two figures, no apparatus, no way to tell which unit either
was counting.

`LEDGER.md`'s own rule is that a figure whose apparatus is gone must be
re-derived or replaced by the command. This file is the command. It is
committed for the same reason `scripts/claim_diff.py` and
`scripts/merge_blockers.py` were: a decision input with no reproducible
apparatus is not a decision input.

THIS SCRIPT DOES NOT FIX F25
----------------------------
Re-ordering the arms, or narrowing `CITATION_WORDS`, is a gate-scope change and
is out of scope. This measures, so the ruling can be made against a number that
reproduces.

HOW EXPOSURE IS DECIDED
-----------------------
By toggling ONE variable on the REAL function, per measurement rule 2. For each
paragraph:

  pass 1  `paragraph_has_source()` as shipped. Record the winning reason.
  pass 2  the same real function, with `CITATION_WORDS` swapped for a pattern
          that matches nothing, and nothing else changed.

A paragraph whose pass-1 reason is `citation-word` is then one of:

  EXPOSED   pass 2 finds no source at all. The word was the only provenance.
            This is the finding: the paragraph is unsourced in substance and
            green to the gate.
  MASKED    pass 2 finds a source anyway. A real citation was present and the
            word reached the verdict first. Harmless to the gate today, but it
            is why the reason string cannot be trusted as evidence of what
            actually sourced a paragraph.

The auditor is never forked. `claim_auditor` is imported from its real location
so `REPO_ROOT` resolves to this repository, which is the mistake that produced
the figures 185 and 168 in an earlier session.

THE PROBE ITSELF LIVES IN `scripts/gate_probe.py`
-------------------------------------------------
`reconcile()`, the off-switch, the occurrence-keyed finding records, the
paragraph classification and the per-finding enumeration are all imported from
that leaf module and re-exported here under the names this file has always
used. They moved out on 2026-07-30 because `scripts/merge_blockers.py` asks the
identical questions of a clean worktree of `main`, and this module cannot reach
that worktree: every corpus here resolves against `REPO_ROOT`. Keeping a second
implementation there would have produced two answers to one question, which is
precisely how 22/46 and 29/53 came to disagree. Everything in `gate_probe`
takes the auditor module and its root as arguments and hardcodes neither.

CORPUS DEFINITIONS
------------------
Written down here, in the file, so a figure can always be attributed to one.
Every definition is produced by `git ls-files` plus a pattern, executed, never
by reading a listing (measurement rule 4c). Untracked files are excluded
everywhere: rule 4b, an untracked file is not a surface.

  all-tracked   every tracked file with a suffix the auditor scans
  diff-base     exactly what `--diff-base main` scans: tracked files that
                differ from the merge base with main
  published     all-tracked minus programme working documents
                (`docs/improvement/`) and agent configuration (`.claude/`),
                the same predicate `merge_blockers.is_published_surface` uses
  site          tracked pages under `site/`
  manifest      the ten surfaces named in
                `data/published_count_manifest.json`
  docs          tracked Markdown under `docs/`, excluding `docs/improvement/`

UNITS
-----
Both are reported for every corpus, because conflating them is how "55
occurrences" came to sit five lines above "45 occurrences" in one file.

  paragraph   a paragraph whose winning source reason is `citation-word`,
              split into EXPOSED and MASKED as above
  gate        findings the real gate reports, before and after the arm is
              switched off. The difference is what the word is suppressing,
              with every downstream exemption already applied: the
              exempt-number list, structural references, tag ranges, the
              allowlist and the quarantine

The gate unit is the one a ruling should use. An earlier draft of this file
counted claim occurrences by applying the auditor's four claim regexes to a
paragraph directly, which counted matches the gate exempts and overstated the
number. It was deleted rather than corrected: the gate is the instrument, so
the gate is what gets run twice.

PER-FINDING ENUMERATION
-----------------------
The counts say how much provenance rests on an ordinary English word. They do
not say WHICH claims, and for the 26 findings the arm holds green on the live
site that is the question a reader has. `--enumerate` prints file, line, claim
text and the citation word that sourced each, produced by the same predicate
that produces the counts, joined to its paragraph on exact coordinates. Built
into this module rather than as a throwaway script for the reason this module
exists at all: a figure whose apparatus is gone is not a decision input.

USAGE
  python3 scripts/f25_exposure.py                    # every corpus, both units
  python3 scripts/f25_exposure.py --corpus published
  python3 scripts/f25_exposure.py --corpus site --enumerate
  python3 scripts/f25_exposure.py --json
  python3 scripts/f25_exposure.py --recover          # can 22/46 or 29/53 be
                                                     # reproduced by any of
                                                     # these definitions?
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import claim_auditor as ca              # noqa: E402
from merge_blockers import is_published_surface   # noqa: E402
# The probe itself. Imported from the leaf module rather than from
# `merge_blockers`, so this module does not depend on a consumer of the same
# machinery, and re-exported under the names this module has always used so
# existing callers and tests keep working.
from gate_probe import (                 # noqa: E402,F401
    ARM_OFF as NEVER,
    paragraph_shape,
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

# The two figures on record that this script exists to test.
RECORDED_FIGURES = {
    "22 / 46": (22, 46),
    "29 / 53": (29, 53),
}

# `NEVER` is `gate_probe.ARM_OFF`, imported above rather than redefined: a
# pattern that cannot match, used to switch the citation-word arm off without
# editing claim_auditor.py. Every caller switches the SAME arm off through the
# SAME object, because two copies of an off-switch drift and a drifted one
# reports LESS exposure, which reads as good news and is therefore the copy
# nobody catches.

MANIFEST_PATH = REPO_ROOT / "data" / "published_count_manifest.json"

# Reported thresholds for the paragraph-length measurement, finding N37. Stated
# here rather than chosen inside the report so the number a reader sees is
# attributable to a declared cut, not to a magic constant in a format string.
# 10 lines is the point past which a "paragraph" is no longer a unit a reader
# would recognise as one piece of prose; 30 is the scale of a whole HTML
# section, which is the shape the finding is about.
PARAGRAPH_LENGTH_THRESHOLDS = (10, 30)

# Paths a corpus definition names but cannot include, with the reason. Reported,
# never dropped in silence: a corpus that quietly loses a member reports a
# smaller exposure and looks like better news. Populated as corpora are built.
DROPPED: dict[str, list[str]] = {}


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=REPO_ROOT, capture_output=True,
                          text=True, check=True).stdout


def _tracked_scannable() -> list[str]:
    """Every tracked path whose suffix the auditor scans."""
    out = _git("ls-files", "-z").split("\0")
    return sorted(p for p in out
                  if p and Path(p).suffix.lower() in ca.SCANNED_SUFFIXES)


def _manifest_surfaces() -> list[str]:
    doc = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    named = doc["published_surfaces"]
    if not named:
        raise RuntimeError(
            "data/published_count_manifest.json lists no published surfaces. "
            "An empty corpus would report zero exposure, which is the "
            "blank-gate failure this programme keeps paying for.")
    paths = [p for p in named if isinstance(p, str)]
    tracked = set(_tracked_scannable())
    kept = sorted(p for p in paths if p in tracked)
    # A designated published surface the auditor cannot scan is finding N6, not
    # a rounding error. `site/llms-full.txt` is on this manifest and `.txt` is
    # outside SCANNED_SUFFIXES, so the corpus is 9 of 10 and the tenth is named.
    # This set difference cannot carry the N37 ordinal defect, checked
    # 2026-07-30. Its elements are FILE PATHS from a manifest, not findings: a
    # path occurs at most once, so there is no multiplicity to collapse and no
    # occurrence to attribute to. Contrast `claim_diff.classify_findings`,
    # where the elements were claim keys standing in for several occurrences.
    DROPPED["manifest"] = [
        f"{p} (suffix {Path(p).suffix or 'none'} is outside "
        f"claim_auditor.SCANNED_SUFFIXES; finding N6)"
        for p in sorted(set(paths) - set(kept))
    ]
    return kept


def _diff_base(base: str) -> list[str]:
    """The corpus `--diff-base` scans: tracked, changed against the merge base.

    Resolved through the same merge-base semantics the auditor uses, so this
    definition and the gate's cannot drift apart without one of them failing.
    """
    merge_base = _git("merge-base", "HEAD", base).strip()
    changed = _git("diff", "--name-only", merge_base, "HEAD").split("\n")
    tracked = set(_tracked_scannable())
    return sorted(p for p in changed if p in tracked)


CORPORA = {
    "all-tracked": lambda: _tracked_scannable(),
    "diff-base": lambda: _diff_base("main"),
    "published": lambda: [p for p in _tracked_scannable()
                          if is_published_surface(p)],
    "site": lambda: [p for p in _tracked_scannable()
                     if p.startswith("site/")],
    "manifest": _manifest_surfaces,
    "docs": lambda: [p for p in _tracked_scannable()
                     if p.startswith("docs/")
                     and not p.startswith("docs/improvement/")
                     and p.endswith(".md")],
}


def arm_order() -> list[tuple[str, int]]:
    """Where each source arm sits in `paragraph_has_source`, from the source.

    F25 was recorded with line numbers that had already moved by the time it
    was next read. Re-derived on every run so the record cannot go stale.
    """
    src = (REPO_ROOT / "scripts" / "claim_auditor.py").read_text(
        encoding="utf-8").splitlines()
    start = next(i for i, ln in enumerate(src)
                 if ln.startswith("def paragraph_has_source("))
    arms = [
        ("url", "for m in URL_RE.finditer"),
        ("md-link", "for m in MD_LINK_RE.finditer"),
        ("html-link", "for m in ANCHOR_HREF.finditer"),
        ("citation-word", "if CITATION_WORDS.search"),
        ("verification-label", "if VERIFICATION_LABEL.search"),
        ("file-ref", "for m in FILE_REF_RE.finditer"),
    ]
    found = []
    for name, needle in arms:
        for i in range(start, len(src)):
            if needle in src[i]:
                found.append((name, i + 1))
                break
    return found


def scan_paragraphs(paths: list[str]) -> dict:
    """Every citation-word-sourced paragraph in `paths`, under this tree.

    A thin binding of `gate_probe.citation_word_rows` to this repository's own
    auditor and root. The logic lives in the shared probe because
    `scripts/merge_blockers.py` asks the identical question of a clean worktree
    of `main`, and two implementations of one question is how 22/46 and 29/53
    came to disagree.
    """
    return citation_word_rows(ca, REPO_ROOT, paths)


def _findings(paths: list[str]) -> list[dict]:
    """Findings the real gate reports over `paths`, under this tree."""
    return findings_over(ca, REPO_ROOT, paths)


def gate_delta(paths: list[str]) -> dict:
    """What the gate would report here with the citation-word arm off."""
    return arm_delta(ca, REPO_ROOT, paths)


def totals(result: dict, delta: dict) -> dict:
    """Both units, exposed and masked, each reconciled against its itemisation."""
    rows = result["rows"]
    exposed = [r for r in rows if r["exposed"]]
    masked = [r for r in rows if not r["exposed"]]

    by_file = sorted({r["file"] for r in rows})
    reconcile("citation-word paragraphs", len(rows),
              [(f, sum(1 for r in rows if r["file"] == f)) for f in by_file])
    reconcile("citation-word paragraphs, by verdict", len(rows),
              [("exposed", len(exposed)), ("masked", len(masked))])

    revealed_by_file = sorted({r["file"] for r in delta["revealed"]})
    reconcile("findings revealed with the arm off", len(delta["revealed"]),
              [(f, sum(1 for r in delta["revealed"] if r["file"] == f))
               for f in revealed_by_file])
    # Switching an arm OFF can only remove provenance, so the gate's finding
    # set can only grow. If anything disappeared, the toggle did something
    # other than what this script claims and the figures must not be published.
    reconcile("findings the arm off would stop reporting",
              len(delta["no_longer_reported"]), [])

    return {
        "paragraph_unit": {
            "citation_word_sourced": len(rows),
            "exposed": len(exposed),
            "masked": len(masked),
        },
        "claim_unit": {
            "findings_now": delta["findings_now"],
            "findings_with_arm_off": delta["findings_with_arm_off"],
            "revealed": len(delta["revealed"]),
        },
        "files": len(by_file),
        "revealed_files": len(revealed_by_file),
    }


def measure(name: str) -> dict:
    paths = CORPORA[name]()
    result = scan_paragraphs(paths)
    delta = gate_delta(paths)
    return {"corpus": name, "paths": result["paths"],
            "paragraphs": result["paragraphs"],
            "sourced_paragraphs": result["sourced_paragraphs"],
            "dropped_from_corpus": DROPPED.get(name, []),
            **totals(result, delta), "rows": result["rows"],
            "revealed_findings": enumerate_revealed(result, delta)}


def head_and_tree() -> tuple[str, str, str]:
    return (_git("rev-parse", "HEAD").strip(),
            _git("rev-parse", "HEAD^{tree}").strip(),
            str(REPO_ROOT))


def report(measurements: list[dict], out=print) -> None:
    head, tree, root = head_and_tree()
    out(f"HEAD {head[:7]}  tree {tree[:7]}  working tree {root}")
    out("")
    out("arm order in paragraph_has_source, re-derived from the source:")
    for name, line in arm_order():
        flag = "   <-- F25: matches bare prose, and wins first" \
            if name == "citation-word" else ""
        out(f"  claim_auditor.py:{line:<5d} {name}{flag}")
    out("")
    for m in measurements:
        p, c = m["paragraph_unit"], m["claim_unit"]
        out(f"corpus {m['corpus']}: {m['paths']} file(s), "
            f"{m['paragraphs']} paragraph(s), "
            f"{m['sourced_paragraphs']} sourced")
        for note in m["dropped_from_corpus"]:
            out(f"  NOT SCANNED: {note}")
        out(f"  paragraph unit: {p['citation_word_sourced']} sourced by "
            f"citation-word  ->  {p['exposed']} EXPOSED, "
            f"{p['masked']} masked, over {m['files']} file(s)")
        out(f"  reconciled: exposed + masked = "
            f"{p['exposed'] + p['masked']} paragraphs")
        out(f"  gate unit:      {c['findings_now']} finding(s) now, "
            f"{c['findings_with_arm_off']} with the arm off  ->  "
            f"{c['revealed']} REVEALED over {m['revealed_files']} file(s)")
        out("")


def report_shape(names: list[str], out=print) -> None:
    """The two orphaned gate mechanisms, measured. Findings N36 and N37.

    Neither is fixed here: both belong to the gate-scope repair, which is
    frozen pending owner decision 7. The deliverable is a number and a command
    that reproduces it.
    """
    for name in names:
        paths = CORPORA[name]()
        shape = paragraph_shape(ca, REPO_ROOT, paths)
        delta = gate_delta(paths)
        rows, lengths = shape["rows"], shape["lengths"]
        attr = shape["attribute_only"]

        by_file = sorted({r["file"] for r in attr})
        reconcile("citation-word paragraphs sourced ONLY inside an HTML "
                  "attribute", len(attr),
                  [(f, sum(1 for r in attr if r["file"] == f))
                   for f in by_file])

        out(f"corpus {name}: {shape['paths']} file(s), "
            f"{shape['paragraphs']} paragraph(s)")
        out(f"  citation-word sourced: {len(rows)}")
        out(f"  sourced ONLY by a citation word inside an HTML attribute: "
            f"{len(attr)} over {len(by_file)} file(s)")
        for r in sorted(attr, key=lambda x: (x["file"], x["paragraph_start"])):
            out(f"      {r['file']}:{r['paragraph_start']}-"
                f"{r['paragraph_end']}  words={r['words']}")

        # Paragraph length. The threshold is stated, not implied.
        lengths_sorted = sorted(lengths)
        n = len(lengths_sorted)
        def pct(p):
            return lengths_sorted[min(n - 1, int(n * p))] if n else 0
        out(f"  paragraph length in lines: median {pct(0.5)}, "
            f"p90 {pct(0.9)}, p99 {pct(0.99)}, max {max(lengths) if lengths else 0}")
        for t in PARAGRAPH_LENGTH_THRESHOLDS:
            over = [r for r in delta["revealed"]
                    if r["paragraph_end"] - r["paragraph_start"] + 1 > t]
            big = sum(1 for x in lengths if x > t)
            out(f"  paragraphs longer than {t} line(s): {big} of "
                f"{shape['paragraphs']}; revealed findings sitting in one: "
                f"{len(over)} of {len(delta['revealed'])}")
        out("")


def report_enumeration(measurements: list[dict], out=print) -> None:
    """Every revealed finding, one line each, with the word that sourced it.

    The counts above say how much provenance rests on an ordinary English word.
    This says which claims they are, which is what turns F25 from a statement
    about an instrument into a statement about the product.
    """
    for m in measurements:
        listed = m["revealed_findings"]
        out(f"corpus {m['corpus']}: {len(listed)} revealed finding(s), "
            f"enumerated")
        for f in sorted(listed, key=lambda x: (x["file"], x["line"],
                                               x["snippet"])):
            out(f"  {f['file']}:{f['line']}  [{f['kind']}] {f['snippet']!r}  "
                f"sourced by: {', '.join(f['citation_words'])}")
        out("")


def candidate_figures(measurements: list[dict]) -> list[tuple[str, str, int, int]]:
    """Every (corpus, unit) pair this script can produce, as exposed/total."""
    out = []
    for m in measurements:
        p, c = m["paragraph_unit"], m["claim_unit"]
        out.append((m["corpus"], "paragraph",
                    p["exposed"], p["citation_word_sourced"]))
        # The gate unit as a ratio: revealed out of what the gate would report
        # once the arm is off. Included so a recorded "N / M" of either shape
        # gets a fair chance of matching.
        out.append((m["corpus"], "gate",
                    c["revealed"], c["findings_with_arm_off"]))
    return out


def report_recovery(measurements: list[dict], out=print) -> bool:
    """Is either recorded figure reproducible under any stated definition?

    Returns True if any is. Establishing that neither reproduces is a result,
    and a better one than publishing a third unreproducible number.
    """
    candidates = candidate_figures(measurements)
    out("candidate figures, every corpus x every unit:")
    for corpus, unit, exposed, total in candidates:
        out(f"  {corpus:12s} {unit:9s} {exposed:4d} / {total:<4d}")
    out("")
    any_hit = False
    for label, (want_exposed, want_total) in RECORDED_FIGURES.items():
        hits = [(c, u) for c, u, e, t in candidates
                if e == want_exposed and t == want_total]
        near = [(c, u, e, t) for c, u, e, t in candidates
                if t == want_total or e == want_exposed]
        if hits:
            any_hit = True
            out(f"RECOVERED {label}: {hits}")
        else:
            out(f"NOT RECOVERABLE {label}: no corpus and unit in this script "
                f"produces it.")
            if near:
                out("  partial matches on one side only: "
                    + ", ".join(f"{c}/{u} {e}/{t}" for c, u, e, t in near))
            else:
                out("  no corpus matches either side of it.")
    return any_hit


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--corpus", choices=sorted(CORPORA), action="append",
                    help="restrict to one corpus; repeatable")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--recover", action="store_true",
                    help="test whether 22/46 or 29/53 reproduces")
    ap.add_argument("--shape", action="store_true",
                    help="measure where citation words sit and how long the "
                         "paragraphs they source are (findings N36 and N37)")
    ap.add_argument("--enumerate", dest="enumerate_findings",
                    action="store_true",
                    help="list every revealed finding with the citation word "
                         "that sourced it")
    args = ap.parse_args()

    names = args.corpus or sorted(CORPORA)
    try:
        measurements = [measure(n) for n in names]
    except (TotalMismatch, UnjoinedFinding) as exc:
        print(f"f25-exposure: {exc}", file=sys.stderr)
        return 2

    if args.json:
        head, tree, root = head_and_tree()
        print(json.dumps({"head": head, "tree": tree, "working_tree": root,
                          "arms": arm_order(),
                          "measurements": measurements}, indent=2))
        return 0

    report(measurements)
    if args.shape:
        report_shape(names)
    if args.enumerate_findings:
        report_enumeration(measurements)
    if args.recover:
        report_recovery(measurements)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
