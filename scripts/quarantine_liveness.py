#!/usr/bin/env python3
# regula-ignore
"""Which quarantine entries suppress anything, and WHY the silent ones do not.

WHY THIS EXISTS
---------------
`.claim-quarantine.json` is a ratchet: a backlog of claims that pre-date the
auditor's ability to see bare percentages, which exists so the gate can go green
for NEW claims while the backlog is burned down. Finding N23 measured that 23 of
its 44 entries suppress nothing at all.

An entry that fires on nothing protects nothing. It also inflates the backlog,
and `tests/test_claim_quarantine.py` deliberately does NOT assert that every
entry fires, which is correct while a backlog exists. The gap that left is that
nothing distinguished **silent and awaiting disposition** from **silent and
forgotten**. Fifteen entries went silent and nothing noticed.

This module closes that gap by making the CAUSE of each silence a measured fact
recorded against the entry, which is a statement of fact rather than a decision
about what to do with it. What to do remains the owner's.

HOW THE CAUSE IS DECIDED
------------------------
By running the REAL gate and toggling ONE thing at a time, per measurement rules
1 and 2. `scan_file` is never forked; `is_quarantined` is wrapped and delegates,
so the tally cannot diverge from what the gate does.

Four passes over the pages the quarantine names:

  pass A  the gate exactly as shipped
  pass B  the gate with an EMPTY allowlist, nothing else changed
  pass C  pass B, plus `paragraph_has_source` forced to report no source
  pass D  the real allowlist, plus sourcing forced off. Used only to answer
          whether a SECOND blocker exists behind the operative one.

The causes then follow the gate's own order of operations inside `scan_file`,
which is: detect claims, skip the paragraph if it has a source, skip the claim if
an allowlist pattern matches, then consult the quarantine.

  live                      pass A suppressed it. The entry is doing its job.
  text-absent               the claim text is not in the raw file at all.
  blanked-by-strip-noise    in the raw file, gone after `strip_noise`. The
                            claim is inside a CSS or code fence the auditor
                            blanks before scanning.
  allowlist-preempted       fires once the allowlist is empty. An allowlist
                            pattern matched first. This is finding F30 on live
                            data: `scan_file` tests each pattern against the
                            claim line, the snippet AND the whole paragraph, so
                            one match exempts every claim in the paragraph.
  paragraph-sourced         fires once sourcing is forced off. The paragraph
                            has gained provenance since the entry was written,
                            so the claim never reaches the quarantine.
  not-detected-as-a-claim   still silent with the allowlist empty and sourcing
                            forced off. The claim regexes do not produce a claim
                            for this text: an exempt number, a structural
                            regulatory reference, or a tag range.

The precedence is the gate's, not a preference. A sourced paragraph short-
circuits before the allowlist is consulted, so `allowlist-preempted` is tested
first and only reached when the paragraph is unsourced.

TWO BLOCKERS CAN BE TRUE AT ONCE, AND THIS IS WHY THE FIELD EXISTS
------------------------------------------------------------------
`LEDGER.md` N23 recorded four entries as silent because "an allowlist pattern
matched their whole paragraph first". MEASURED here, those four paragraphs are
BOTH sourced AND allowlist-matched, and `scan_file` runs `if has_src: continue`
BEFORE the allowlist loop, so the operative cause is the source and the
allowlist never gets consulted. Both statements about the data are true; the
attribution was not.

So `cause` is the blocker the gate reaches FIRST, and `also_blocked_by` names
the ones standing behind it. A prose sentence could not have told those apart,
which is how one session recorded a cause another session cannot reproduce.

PRESENCE IS TESTED ON NORMALISED TEXT WITH A LEFT GUARD
-------------------------------------------------------
`_normalise_claim` is the quarantine's own key material, so presence is tested
on the same normalisation. A bare `re.escape` substring search would report
`20%` as present inside `120%`, so the search carries a `(?<![\\w.])` guard.
That is not a full tokeniser and the limitation is stated rather than hidden: it
distinguishes "the text is gone" from the other causes, and every other cause is
decided by running the gate rather than by matching text.

USAGE
  python3 scripts/quarantine_liveness.py
  python3 scripts/quarantine_liveness.py --json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import claim_auditor as ca              # noqa: E402
from merge_blockers import reconcile     # noqa: E402

REPO_ROOT = ca.REPO_ROOT

LIVE = "live"
TEXT_ABSENT = "text-absent"
BLANKED = "blanked-by-strip-noise"
ALLOWLIST_PREEMPTED = "allowlist-preempted"
PARAGRAPH_SOURCED = "paragraph-sourced"
NOT_A_CLAIM = "not-detected-as-a-claim"

# Every cause a silent entry may carry. `live` is not one of them: a live entry
# is not silent, and recording a cause against it would be a contradiction.
SILENT_CAUSES = (TEXT_ABSENT, BLANKED, ALLOWLIST_PREEMPTED, PARAGRAPH_SOURCED,
                 NOT_A_CLAIM)


def load_doc() -> dict:
    return json.loads(ca.QUARANTINE_PATH.read_text(encoding="utf-8"))


def entry_pairs(doc: dict) -> list[tuple[str, str]]:
    """The quarantine's entries as the auditor keys them.

    WHY THIS MODULE CANNOT CARRY THE ORDINAL DEFECT, checked 2026-07-30 rather
    than assumed. N37 is a comparison whose key is COARSER than the unit it
    resolves to: a finding key without a line, differenced to pick out one
    occurrence among several. Here the key and the unit are the SAME
    granularity. A quarantine entry is `(file, normalised claim)` and carries
    no line, so this is what the thing being classified actually is, not a
    lossy identifier for something finer. `scan_pass` builds its `fired` set on
    the identical key, and `cause_of` only ever asks whether an entry fired in
    a given pass. There is no occurrence to attribute to, so there is nothing
    to misattribute. Cardinality is not lost either: `scan_pass` keeps
    `occurrences` as a LIST beside the set, so anything needing multiplicity
    reads that rather than the set. Do not "improve" this by adding a line to
    the key; it would stop matching the quarantine file's own identity.
    """
    return [(e["file"], ca._normalise_claim(e["claim"]))
            for e in doc["entries"]]


def named_pages(doc: dict) -> list[str]:
    return sorted({e["file"] for e in doc["entries"]})


def claim_text_present(text: str, claim: str) -> bool:
    """Is this claim's text in `text`, on the quarantine's own normalisation?"""
    pattern = r"(?<![\w.])" + re.escape(ca._normalise_claim(claim))
    return re.search(pattern, ca._normalise_claim(text)) is not None


def _never_sourced(*_args, **_kwargs) -> tuple[bool, str]:
    return (False, "forced-unsourced")


def scan_pass(paths: list[str], allowlist: list, *,
              force_unsourced: bool = False) -> dict:
    """Run the real gate over `paths`, tallying what the quarantine suppressed.

    `is_quarantined` is WRAPPED and delegates to the real function, so what is
    counted is exactly what the gate did. Both patches are restored in a
    `finally`: a module left patched would corrupt every later scan in the
    process, which is the failure `tests/test_f25_exposure.py` already pins for
    `CITATION_WORDS`.
    """
    real_quarantine = ca.is_quarantined
    real_source = ca.paragraph_has_source
    fired: set[tuple[str, str]] = set()
    occurrences: list[tuple[str, str]] = []
    claims = unsourced = 0

    def tally(file_path, snippet):
        hit = real_quarantine(file_path, snippet)
        if hit:
            key = (file_path, ca._normalise_claim(snippet))
            fired.add(key)
            occurrences.append(key)
        return hit

    ca.is_quarantined = tally
    if force_unsourced:
        ca.paragraph_has_source = _never_sourced
    try:
        for rel in paths:
            report = ca.scan_file(REPO_ROOT / rel, allowlist)
            claims += report.claims
            unsourced += len(report.findings)
    finally:
        ca.is_quarantined = real_quarantine
        ca.paragraph_has_source = real_source

    return {"fired": fired, "occurrences": occurrences,
            "claims": claims, "unsourced": unsourced}


def cause_of(pair: tuple[str, str], passes: dict) -> str:
    """The measured reason this entry is silent. See the module docstring."""
    rel, claim = pair
    if pair in passes["shipped"]["fired"]:
        return LIVE
    try:
        raw = (REPO_ROOT / rel).read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        # Deliberately NOT reported as `text-absent`. An unreadable file and a
        # claim that has been edited away are different facts, and conflating
        # them would let a burn-down be justified by a missing file. The
        # quarantine's own test already asserts every named file exists, so
        # reaching here means something worse than a stale entry.
        raise RuntimeError(
            f"{rel} is named by the quarantine and cannot be read ({exc}). "
            f"Refusing to classify its entries: a file that is not there is "
            f"not evidence that a claim was removed.") from exc
    if not claim_text_present(raw, claim):
        return TEXT_ABSENT
    cleaned = ca.strip_noise(raw, Path(rel).suffix.lower())
    if not claim_text_present(cleaned, claim):
        return BLANKED
    if pair in passes["no_allowlist"]["fired"]:
        return ALLOWLIST_PREEMPTED
    if pair in passes["forced_unsourced"]["fired"]:
        return PARAGRAPH_SOURCED
    return NOT_A_CLAIM


def also_blocked_by(pair: tuple[str, str], passes: dict, cause: str) -> list[str]:
    """Blockers standing BEHIND the operative one, measured not inferred.

    Only asked where the answer is decidable. For `text-absent` and
    `blanked-by-strip-noise` there is no claim to block, and for
    `allowlist-preempted` the paragraph is already known to be unsourced,
    because that cause is only reached when the entry fires with sourcing
    unchanged.
    """
    if cause != PARAGRAPH_SOURCED:
        return []
    # It fires with the allowlist empty and sourcing off (that is what made it
    # `paragraph-sourced`). If it does NOT fire with sourcing off and the REAL
    # allowlist in place, the allowlist would have blocked it too.
    if pair in passes["allowlist_only"]["fired"]:
        return []
    return ["allowlist"]


def measure(doc: dict | None = None) -> dict:
    """Classify every quarantine entry, with the totals reconciled."""
    doc = doc if doc is not None else load_doc()
    pairs = entry_pairs(doc)
    paths = named_pages(doc)
    allow = ca.load_allowlist()

    passes = {
        "shipped": scan_pass(paths, allow),
        "no_allowlist": scan_pass(paths, []),
        "forced_unsourced": scan_pass(paths, [], force_unsourced=True),
        "allowlist_only": scan_pass(paths, allow, force_unsourced=True),
    }

    verdicts = [(rel, claim, cause_of((rel, claim), passes))
                for rel, claim in pairs]
    live = [(f, c) for f, c, v in verdicts if v == LIVE]
    silent = [{"file": f, "claim": c, "cause": v,
               "also_blocked_by": also_blocked_by((f, c), passes, v)}
              for f, c, v in verdicts if v != LIVE]

    reconcile("quarantine entries, by liveness", len(pairs),
              [(LIVE, len(live)), ("silent", len(silent))])
    reconcile("silent entries, by measured cause", len(silent),
              sorted(Counter(s["cause"] for s in silent).items()))
    reconcile("quarantine entries, by page", len(pairs),
              sorted(Counter(f for f, _ in pairs).items()))

    return {
        "head": ca.git("rev-parse", "HEAD").strip(),
        "tree": ca.git("rev-parse", "HEAD^{tree}").strip(),
        "pages": len(paths),
        "entries": len(pairs),
        "live": sorted(live),
        "silent": sorted(silent, key=lambda s: (s["file"], s["claim"])),
        "suppressed_occurrences": len(passes["shipped"]["occurrences"]),
        "claims": passes["shipped"]["claims"],
        "unsourced": passes["shipped"]["unsourced"],
        "cause_tally": dict(sorted(
            Counter(s["cause"] for s in silent).items())),
    }


def report(r: dict, out=print) -> None:
    out(f"HEAD {r['head'][:7]}  tree {r['tree'][:7]}  "
        f"working tree {REPO_ROOT}")
    out(f"quarantine entries, by liveness: {r['entries']}")
    out(f"      {len(r['live']):4d}  {LIVE}")
    out(f"      {len(r['silent']):4d}  silent")
    out(f"silent entries, by measured cause: {len(r['silent'])}")
    for cause, n in r["cause_tally"].items():
        out(f"      {n:4d}  {cause}")
    out(f"over {r['pages']} page(s): {r['claims']} claim(s), "
        f"{r['unsourced']} unsourced, "
        f"{r['suppressed_occurrences']} suppressed occurrence(s)")
    out("")
    for s in r["silent"]:
        extra = (f"  (also blocked by: {', '.join(s['also_blocked_by'])})"
                 if s["also_blocked_by"] else "")
        out(f"  SILENT  {s['file']}  {s['claim']!r}  ->  {s['cause']}{extra}")
    out("")
    for rel, claim in r["live"]:
        out(f"  LIVE    {rel}  {claim!r}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    r = measure()
    if args.json:
        print(json.dumps(r, indent=2))
        return 0
    report(r)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
