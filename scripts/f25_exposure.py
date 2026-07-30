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

`reconcile()` is imported from `scripts/merge_blockers.py` rather than
reimplemented. That module built the single door every total in this programme
passes through; a second copy of the same check is the duplication this
repository exists to catch.

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
from merge_blockers import (             # noqa: E402
    ARM_OFF as NEVER,
    TotalMismatch,
    is_published_surface,
    reconcile,
)

REPO_ROOT = ca.REPO_ROOT

# The two figures on record that this script exists to test.
RECORDED_FIGURES = {
    "22 / 46": (22, 46),
    "29 / 53": (29, 53),
}

# `NEVER` is `merge_blockers.ARM_OFF`, imported above rather than redefined: a
# pattern that cannot match, used to switch the citation-word arm off without
# editing claim_auditor.py. Both this module and `merge_blockers` switch the
# same arm off, and two copies of an off-switch drift. A drifted off-switch
# reports LESS exposure, which reads as good news, so it is the copy that would
# not get caught.

MANIFEST_PATH = REPO_ROOT / "data" / "published_count_manifest.json"

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
    """Classify every citation-word-sourced paragraph in `paths`.

    Returns per-file and per-paragraph detail so every total printed has an
    itemisation to be reconciled against.
    """
    real_words = ca.CITATION_WORDS
    rows: list[dict] = []
    paragraphs = sourced = 0

    for rel in paths:
        path = REPO_ROOT / rel
        try:
            raw = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        suffix = path.suffix.lower()
        cleaned = ca.strip_noise(raw, suffix)
        identity = ca.page_identity(raw, rel)

        for start, end, para in ca.split_paragraphs(cleaned):
            paragraphs += 1
            has_src, reason = ca.paragraph_has_source(para, identity)
            if has_src:
                sourced += 1
            if not has_src or reason != "citation-word":
                continue

            # Pass 2. One variable: the citation-word arm, switched off on the
            # real function. Restored in a finally so an exception cannot leave
            # the module patched for a later caller.
            try:
                ca.CITATION_WORDS = NEVER
                still_sourced, other_reason = ca.paragraph_has_source(
                    para, identity)
            finally:
                ca.CITATION_WORDS = real_words

            words = sorted({m.group(0).strip(":. ").lower()
                            for m in real_words.finditer(para)})
            rows.append({
                "file": rel,
                "paragraph_start": start,
                "paragraph_end": end,
                "exposed": not still_sourced,
                "otherwise_sourced_by": None if not still_sourced
                else other_reason,
                "words": words,
            })

    return {
        "paths": len(paths),
        "paragraphs": paragraphs,
        "sourced_paragraphs": sourced,
        "rows": rows,
    }


class UnjoinedFinding(RuntimeError):
    """A revealed finding did not join to a citation-word paragraph.

    Not a total mismatch: the arithmetic is fine and the join is broken, which
    means the two passes disagree about where a paragraph starts. Separated so
    the message says which of the two went wrong.
    """


def _findings(paths: list[str]) -> list[dict]:
    """Findings the REAL gate reports over `paths`, one record per OCCURRENCE.

    `scan_file` is the gate. Calling it is the only way to count claim
    occurrences the way the gate counts them, because every exemption that
    stands between a regex match and a finding lives inside it: the
    exempt-number list, the structural-reference ranges, the tag ranges for
    attributed claims, the allowlist, and the quarantine.

    THE ORDINAL IS NOT DECORATION. Keyed on (file, line, kind, snippet) alone,
    this set had 267 members where the gate reported 273 over the same 59
    files, because six claims repeat identically on one line: `15 files` twice
    on `.claude/rules/quality-standards.md:22`, `41%` and `43%` and `29%` in
    `docs/improvement/PACK-1.5b.md`, and two in
    `docs/benchmarks/PRECISION_RECALL_2026_04.md`. A set that silently merges
    duplicates reports a total six below the gate's, and a headline that
    disagrees with the instrument by six is exactly what this programme keeps
    paying for. Appending an occurrence index makes the set size equal the list
    length while keeping the set difference well defined.

    Records rather than bare keys, because a count with no itemisation behind it
    is the defect that made owner decision 3 unanswerable for five sessions.
    The paragraph coordinates travel with each record so the enumeration can be
    joined back to the paragraph that sourced it without re-deriving anything.
    """
    allow = ca.load_allowlist()
    out: list[dict] = []
    seen: dict[tuple[str, int, str, str], int] = {}
    for rel in paths:
        report = ca.scan_file(REPO_ROOT / rel, allow)
        for f in report.findings:
            base = (report.path, f.claim.line, f.claim.kind, f.claim.snippet)
            ordinal = seen.get(base, 0)
            seen[base] = ordinal + 1
            out.append({
                "file": report.path,
                "line": f.claim.line,
                "kind": f.claim.kind,
                "snippet": f.claim.snippet,
                "occurrence": ordinal,
                "paragraph_start": f.claim.paragraph_start,
                "paragraph_end": f.claim.paragraph_end,
            })
    return out


def finding_key(f: dict) -> tuple[str, int, str, str, int]:
    """The identity of one finding OCCURRENCE. See `_findings`."""
    return (f["file"], f["line"], f["kind"], f["snippet"], f["occurrence"])


def gate_delta(paths: list[str]) -> dict:
    """What the gate would report with the citation-word arm switched off.

    THE DECISION-RELEVANT NUMBER, and the reason the earlier hand-rolled claim
    count in this file was deleted rather than corrected. That version applied
    the auditor's four claim regexes to a paragraph itself and therefore
    counted matches the gate exempts, overstating the claim unit. Re-derived
    here by running the real `scan_file` twice over one code state with one
    variable toggled, so the delta is exactly the set of findings the arm is
    currently suppressing.
    """
    real_words = ca.CITATION_WORDS
    before = _findings(paths)
    try:
        ca.CITATION_WORDS = NEVER
        after = _findings(paths)
    finally:
        ca.CITATION_WORDS = real_words
    before_keys = {finding_key(f) for f in before}
    after_by_key = {finding_key(f): f for f in after}
    revealed = [after_by_key[k] for k in sorted(set(after_by_key) - before_keys)]
    lost = sorted(before_keys - set(after_by_key))
    return {
        "findings_now": len(before),
        "findings_with_arm_off": len(after),
        "revealed": revealed,
        "no_longer_reported": [list(k) for k in lost],
    }


def enumerate_revealed(result: dict, delta: dict) -> list[dict]:
    """One record per revealed finding: file, line, claim text, citation word.

    WHY THIS EXISTS. The counts alone turned F25 into an apparatus finding: 26
    findings on the live site were suppressed by an ordinary English word and
    nobody could say WHICH claims they were without building a throwaway
    script. A figure whose apparatus is gone is the defect that made owner
    decision 3 unanswerable for five sessions, so the enumeration is produced by
    the SAME predicate that produces the counts and is re-derivable by a
    committed command.

    THE JOIN IS ON EXACT PARAGRAPH COORDINATES, never on containment. Both
    sides come from `ca.split_paragraphs(ca.strip_noise(...))` over the same
    file at the same code state, and `Claim` carries the paragraph it was found
    in, so `(file, paragraph_start, paragraph_end)` identifies the same
    paragraph on both sides or nothing does.

    EVERY revealed finding must join. Switching the citation-word arm off can
    only change the verdict of a paragraph whose winning reason WAS
    `citation-word`, because the arms before it are untouched and the arms after
    it are only ever reached more often; `scan_paragraphs` records every such
    paragraph. A revealed finding with no matching row means the two passes
    disagree about what a paragraph is, and the enumeration must not print.
    """
    rows = {(r["file"], r["paragraph_start"], r["paragraph_end"]): r
            for r in result["rows"]}
    out: list[dict] = []
    unjoined: list[tuple] = []
    for f in delta["revealed"]:
        row = rows.get((f["file"], f["paragraph_start"], f["paragraph_end"]))
        if row is None:
            unjoined.append(finding_key(f))
            continue
        out.append({**f,
                    "citation_words": row["words"],
                    "exposed": row["exposed"],
                    "otherwise_sourced_by": row["otherwise_sourced_by"]})
    if unjoined:
        raise UnjoinedFinding(
            f"{len(unjoined)} of {len(delta['revealed'])} revealed finding(s) "
            f"do not sit in any paragraph this run recorded as sourced by the "
            f"citation-word arm: {unjoined}. The two passes disagree about "
            f"paragraph boundaries, so neither the enumeration nor the counts "
            f"may be published.")
    # Reconciled against the DIFFERENCE OF THE TWO GATE TOTALS, not against
    # `len(delta["revealed"])`. The latter is the same object this list was
    # built from, so checking against it could never fail and would be a blank
    # gate. The two totals are counted independently of the set difference, so
    # this fires if the toggle lost a finding as well as if the join dropped
    # one.
    reconcile("revealed findings, enumerated one per line",
              delta["findings_with_arm_off"] - delta["findings_now"],
              [(f["file"], 1) for f in out])
    return out


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
    if args.enumerate_findings:
        report_enumeration(measurements)
    if args.recover:
        report_recovery(measurements)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
