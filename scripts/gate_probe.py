#!/usr/bin/env python3
# regula-ignore
"""One instrument for probing the claim gate, shared by every caller.

WHY THIS MODULE EXISTS
----------------------
Three things in this programme had started to exist in more than one place, and
each duplication is the same failure wearing a different hat.

1. **The off-switch.** `scripts/f25_exposure.py` and `scripts/merge_blockers.py`
   both replace `CITATION_WORDS` with a pattern that cannot match. Two copies
   drift, and a drifted off-switch reports LESS exposure, which reads as good
   news and is therefore the copy nobody catches.
2. **`reconcile()`.** It was defined inside `merge_blockers`, which made it
   unreachable from `claim_diff` without an import cycle, so a third consumer
   would have written its own. "The single door every total passes through" has
   to be a door, not a room inside one consumer.
3. **The per-finding enumeration.** `f25_exposure` could enumerate the findings
   the citation-word arm suppresses, but only against this branch's working
   tree, because it hardcoded `claim_auditor` and `REPO_ROOT`. Answering the
   same question for `main` needed a clean worktree, which `merge_blockers`
   owns. Writing a second enumerator there would have produced two answers to
   one question, which is exactly how 22/46 and 29/53 came to disagree.

So everything here takes the auditor **module** and its **root** as arguments
and hardcodes neither. `f25_exposure` passes `claim_auditor` and `REPO_ROOT`;
`merge_blockers` passes the module loaded out of a detached worktree of `main`
and that worktree's path. Same predicate, two specimens.

This module imports nothing from the rest of the programme. It is a leaf, so
any caller can use it without an import cycle.

FINDING IDENTITY, AND WHY THERE ARE TWO KINDS
---------------------------------------------
**Same tree**, comparing two instrument states over identical content:
`finding_key` is `(file, line, kind, normalised snippet, ordinal)`, where the
ordinal counts repeats of that exact tuple. The line belongs in the key here
because the content cannot move: both passes read the same bytes.

**The ordinal is not decoration.** Keyed on `(file, line, kind, snippet)`
alone, the set had 267 members where the gate reported 273 over the same 59
files, because six claims repeat identically on one line. A set that silently
merges duplicates undercounts, and a headline that disagrees with the
instrument by six is what this programme keeps paying for.

**THE LINE IS NOT OPTIONAL, AND REMOVING IT IS A MEASURED DEFECT.** A first
draft of this module dropped the line so one key could serve both same-tree and
cross-commit comparisons. That makes the ordinal POSITIONALLY UNSTABLE: on
`site/guides/eu-ai-act-recruitment-hiring.html` at `main`, `43%` yields one
finding with the arm on (line 213) and two with it off (lines 210 and 213). The
set difference then returns ordinal 1, which resolves to line **213**, an
unsourced paragraph, while the finding actually revealed is line **210**. The
count stays right and the attribution goes wrong. `enumerate_revealed`'s join
guard caught it, on four findings out of seventy, before any figure was
published.

**Across commits**, where lines genuinely do move, `content_signature` is
`(file, kind, normalised snippet)` and the comparison is a MULTISET diff on
counts. Identical claim text repeated in one file cannot be told apart across
two commits without reading diff hunks, so `claim_diff.blocker_delta` reports
the count change and flags attribution as ambiguous whenever a signature was
already present.
"""
from __future__ import annotations

import re
from pathlib import Path

# The off-switch for a source arm of `paragraph_has_source`: a pattern that
# cannot match anything, substituted for the real one so the REAL function is
# what gets measured rather than a fork of it.
ARM_OFF = re.compile(r"(?!x)x")

_WS = re.compile(r"\s+")


class TotalMismatch(RuntimeError):
    """A reported total disagrees with the itemisation printed beneath it."""


class UnjoinedFinding(RuntimeError):
    """A revealed finding did not join to a citation-word paragraph.

    Not a total mismatch: the arithmetic is fine and the join is broken, which
    means the two passes disagree about where a paragraph starts. Separated so
    the message says which of the two went wrong.
    """


def reconcile(label: str, total: int,
              items: list[tuple[str, int]]) -> list[tuple[str, int]]:
    """Prove `items` account for `total`, then return them for printing.

    The caller passes the SAME list it is about to print, so this cannot pass
    while the reader is shown something else. A count of a set comes from the
    predicate that enumerated it; this is the arithmetic half of that rule.
    """
    counted = sum(n for _, n in items)
    if counted != total:
        raise TotalMismatch(
            f"{label}: reported total {total}, but its itemisation of "
            f"{len(items)} entries sums to {counted} (difference "
            f"{total - counted}). One of the two is wrong, and neither may be "
            f"published until it is known which.")
    return items


def normalise_snippet(text: str) -> str:
    """Whitespace-collapsed, case-folded claim text. Digits are NOT touched."""
    return _WS.sub(" ", text.strip().lower())


def finding_key(f: dict) -> tuple[str, int, str, str, int]:
    """SAME-TREE occurrence identity. Includes the line; see the docstring.

    Only valid for comparing two instrument states over one tree. Using it
    across commits would report every finding below an insertion as removed and
    re-added, because the line moved.
    """
    return (f["file"], f["line"], f["kind"], normalise_snippet(f["snippet"]),
            f["occurrence"])


def content_signature(f: dict) -> tuple[str, str, str]:
    """CROSS-COMMIT identity of a finding's content, with no coordinates.

    Deliberately not unique per occurrence: it is the multiset element that
    `claim_diff.blocker_delta` counts on each side. See the docstring for why an
    ordinal cannot be added here without becoming positionally unstable.
    """
    return (f["file"], f["kind"], normalise_snippet(f["snippet"]))


def findings_over(module, root: Path, paths: list[str]) -> list[dict]:
    """Findings the REAL gate reports over `paths`, one record per OCCURRENCE.

    `module.scan_file` is the gate. Calling it is the only way to count claim
    occurrences the way the gate counts them, because every exemption that
    stands between a regex match and a finding lives inside it: the
    exempt-number list, the structural-reference ranges, the tag ranges for
    attributed claims, the allowlist and the quarantine.

    Records rather than bare keys, because a count with no itemisation behind
    it is the defect that made owner decision 3 unanswerable for five sessions.
    The paragraph coordinates travel with each record so the enumeration can be
    joined back to the paragraph that sourced it without re-deriving anything.
    """
    allow = module.load_allowlist()
    out: list[dict] = []
    seen: dict[tuple[str, int, str, str], int] = {}
    for rel in paths:
        report = module.scan_file(Path(root) / rel, allow)
        for f in report.findings:
            base = (report.path, f.claim.line, f.claim.kind,
                    normalise_snippet(f.claim.snippet))
            ordinal = seen.get(base, 0)
            seen[base] = ordinal + 1
            out.append({
                "file": report.path,
                "line": f.claim.line,
                "kind": f.claim.kind,
                "snippet": f.claim.snippet,
                "occurrence": ordinal,
                "reason": f.reason,
                "paragraph_start": f.claim.paragraph_start,
                "paragraph_end": f.claim.paragraph_end,
            })
    return out


def citation_word_rows(module, root: Path, paths: list[str]) -> dict:
    """Classify every citation-word-sourced paragraph in `paths`.

    For each paragraph, `paragraph_has_source` is run as shipped and then again
    with `CITATION_WORDS` swapped for `ARM_OFF` and nothing else changed. A
    paragraph whose first verdict was `citation-word` is then EXPOSED (pass two
    finds no source at all, so the word was the only provenance) or MASKED (a
    real citation was there and the word reached the verdict first).

    The real function is never forked, and `CITATION_WORDS` is restored in a
    `finally` so an exception cannot leave the module patched for a later
    caller.
    """
    real_words = module.CITATION_WORDS
    rows: list[dict] = []
    paragraphs = sourced = 0

    for rel in paths:
        path = Path(root) / rel
        try:
            raw = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        cleaned = module.strip_noise(raw, path.suffix.lower())
        identity = module.page_identity(raw, rel)

        for start, end, para in module.split_paragraphs(cleaned):
            paragraphs += 1
            has_src, reason = module.paragraph_has_source(para, identity)
            if has_src:
                sourced += 1
            if not has_src or reason != "citation-word":
                continue

            try:
                module.CITATION_WORDS = ARM_OFF
                still_sourced, other_reason = module.paragraph_has_source(
                    para, identity)
            finally:
                module.CITATION_WORDS = real_words

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


def paragraph_shape(module, root: Path, paths: list[str]) -> dict:
    """Where citation words sit, and how long the paragraphs they source are.

    Two orphaned gate mechanisms, both demonstrated and neither measured until
    2026-07-30. Both belong to the gate-scope repair, which is frozen; this only
    says how far each reaches.

    ATTRIBUTE-ONLY SOURCING. `_citable_text` blanks only the void tags in
    `NONCITATION_TAG` (`link|meta|img|source|iframe|base|track|area|use`), so a
    `<div class="article-ref">`'s attributes survive into the text the source
    test reads and `ref` matches. A paragraph is attribute-only if EVERY
    citation-word match in it falls inside an HTML tag, meaning nothing a reader
    can see supplied the provenance. Same family as F21, where a page's own
    canonical URL sourced its claims.

    PARAGRAPH LENGTH. `split_paragraphs` splits on blank lines, and HTML written
    without them makes a whole section one paragraph. `paragraph_has_source` is
    evaluated once per paragraph and every claim inside inherits the verdict, so
    a 37-line FAQ with nine answers is a single unit of provenance and one
    citation word in the fourth answer sources all nine.
    """
    real_words = module.CITATION_WORDS
    rows: list[dict] = []
    lengths: list[int] = []

    for rel in paths:
        path = Path(root) / rel
        try:
            raw = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        cleaned = module.strip_noise(raw, path.suffix.lower())
        identity = module.page_identity(raw, rel)

        for start, end, para in module.split_paragraphs(cleaned):
            lengths.append(end - start + 1)
            has_src, reason = module.paragraph_has_source(para, identity)
            if not has_src or reason != "citation-word":
                continue
            citable = module._citable_text(para)
            tags = [(m.start(), m.end())
                    for m in module.HTML_TAG.finditer(citable)]
            hits = list(real_words.finditer(citable))
            in_tag = [h for h in hits
                      if any(lo <= h.start() < hi for lo, hi in tags)]
            rows.append({
                "file": rel,
                "paragraph_start": start,
                "paragraph_end": end,
                "lines": end - start + 1,
                "citation_word_hits": len(hits),
                "hits_inside_a_tag": len(in_tag),
                # Nothing a reader can see supplied the provenance.
                "attribute_only": bool(hits) and len(in_tag) == len(hits),
                "words": sorted({m.group(0).strip(":. ").lower()
                                 for m in hits}),
            })

    return {"paths": len(paths), "paragraphs": len(lengths),
            "lengths": lengths, "rows": rows,
            "attribute_only": [r for r in rows if r["attribute_only"]]}


def arm_delta(module, root: Path, paths: list[str]) -> dict:
    """What the gate would report with the citation-word arm switched off.

    THE DECISION-RELEVANT NUMBER. Re-derived by running the real `scan_file`
    twice over one code state with one variable toggled, so the delta is
    exactly the set of findings the arm is currently suppressing.

    `findings_now` and `findings_with_arm_off` are counted independently of the
    set difference. That matters: it makes `findings_with_arm_off -
    findings_now` a total the enumeration can be reconciled against without the
    check being true by construction.
    """
    real_words = module.CITATION_WORDS
    before = findings_over(module, root, paths)
    try:
        module.CITATION_WORDS = ARM_OFF
        after = findings_over(module, root, paths)
    finally:
        module.CITATION_WORDS = real_words

    before_keys = {finding_key(f) for f in before}
    after_by_key = {finding_key(f): f for f in after}
    revealed = [after_by_key[k] for k in sorted(set(after_by_key) - before_keys)]
    lost = sorted(before_keys - set(after_by_key))
    return {
        "findings_now": len(before),
        "findings_with_arm_off": len(after),
        "findings_arm_on": before,
        "findings_arm_off": after,
        "revealed": revealed,
        "no_longer_reported": [list(k) for k in lost],
    }


def enumerate_revealed(result: dict, delta: dict) -> list[dict]:
    """One record per revealed finding: file, line, claim text, citation word.

    WHY THIS EXISTS. The counts alone made F25 an apparatus finding: N findings
    were suppressed by an ordinary English word and nobody could say WHICH
    claims they were without building a throwaway script. A figure whose
    apparatus is gone is the defect that made owner decision 3 unanswerable for
    five sessions, so the enumeration is produced by the SAME predicate that
    produces the counts.

    THE JOIN IS ON EXACT PARAGRAPH COORDINATES, never on containment. Both
    sides come from `split_paragraphs(strip_noise(...))` over the same file at
    the same code state, and the auditor's `Claim` carries the paragraph it was
    found in, so `(file, paragraph_start, paragraph_end)` identifies the same
    paragraph on both sides or nothing does.

    EVERY revealed finding must join. Switching the citation-word arm off can
    only change the verdict of a paragraph whose winning reason WAS
    `citation-word`, because the arms before it are untouched and the arms after
    it are only ever reached more often; `citation_word_rows` records every such
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
