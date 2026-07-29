#!/usr/bin/env python3
"""Report tracked documents that cite a path the repository does not contain.

Finding N1, and what remains of it after the fix.

BEFORE the fix, `paragraph_has_source` and `strip_noise` accepted a file
reference whenever `(REPO_ROOT / ref).exists()`. That consults the working
tree, so a gitignored file counted as provenance on a developer's machine and
vanished in a clean checkout: commit fb115cb scored 276 unsourced in the main
tree and 277 in a worktree. `measurement.md` rule 4b already held that an
untracked file is not a published surface because nobody outside the machine
can read it; a citation is now held to the same bar, via `ca.ref_is_tracked`.

AFTER the fix, asking the gate "is this paragraph sourced by an untracked
reference?" always answers no, by construction. A script keyed on that would
report zero for ever, which is a tool that cannot fail rather than a tool that
passes. So this reports the CONTENT condition, which the fix does not remove:
a document pointing a reader at a file that is not in the repository.

NOT EVERY HIT IS A DEFECT. `regula-policy.yaml`, `MODEL_CARD.md` and
`AI_GOVERNANCE.md` are artefacts the tool generates for a user, so
instructional prose naming them is correct. Triage on the `claims` column:
that is what separates a paragraph merely mentioning a filename from one
leaning on it for provenance.

TWO DIFFERENT MEASUREMENTS, recorded so they are not conflated later. Against
the pre-fix gate verdict the population was 18 paragraphs. Against the content
predicate here it is 10, because this one requires the cited file to exist,
skips self-references, and records one row per paragraph rather than one per
reference. Neither number is wrong; they count different things.

Rule 4c: every count `main()` prints is produced by the predicate that built
the set, never read off the listing. A hand count of an earlier version of
this output reported "9 on published surfaces" where its own predicate gave
10. `data/published_count_manifest.json` records that the identical
off-by-one, "nine surfaces" against components summing to ten, has happened
in this repository before.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import claim_auditor as ca  # noqa: E402

REPO_ROOT = ca.REPO_ROOT

# Repo-sanctioned boundary. `data/published_count_manifest.json` lists
# `docs/improvement/` under excluded_by_design as "programme working
# documents"; `.claude/` is agent configuration. Everything else that is
# tracked ships to a reader.
WORKING_PREFIXES = ("docs/improvement/", ".claude/")


def tracked_files() -> set[str]:
    out = subprocess.run(
        ["git", "ls-files"], cwd=REPO_ROOT,
        capture_output=True, text=True, check=True).stdout
    return set(out.split())


def is_working_document(rel: str) -> bool:
    return rel.startswith(WORKING_PREFIXES)


def scan(tracked: set[str]) -> list[dict]:
    """Return one record per paragraph that CITES an untracked path.

    Deliberately does NOT ask `paragraph_has_source` whether the paragraph
    ended up sourced. Since the N1 fix that question is tautological: the
    gate never returns `file-ref:` for an untracked reference, so keying on
    its verdict would make this script permanently report zero, which is a
    tool that cannot fail rather than a tool that passes.

    What it measures instead is the content condition, which survives the
    fix: a document pointing a reader at a file the repository does not
    contain. Some hits are legitimate. `regula-policy.yaml`, `MODEL_CARD.md`
    and `AI_GOVERNANCE.md` are artefacts the tool GENERATES for a user, so
    instructional text naming them is correct and must not be "fixed". The
    `claims` field is what separates prose that merely mentions a filename
    from a claim leaning on it for provenance, so triage on that column.

    This is a report, not a gate. It exits 0 unless --check is passed.
    """
    corpus = subprocess.run(
        ["git", "ls-files", "*.md", "*.html"], cwd=REPO_ROOT,
        capture_output=True, text=True, check=True).stdout.split()
    hits: list[dict] = []
    for rel in corpus:
        raw = (REPO_ROOT / rel).read_text(encoding="utf-8", errors="replace")
        cleaned = ca.strip_noise(raw, Path(rel).suffix.lower())
        identity = ca.page_identity(raw, rel)
        for start, _end, para in ca.split_paragraphs(cleaned):
            citable = ca._citable_text(para)
            for m in ca.FILE_REF_RE.finditer(citable):
                ref = m.group(1)
                if ca._is_self_file_ref(ref, identity):
                    continue
                if os.path.normpath(ref) in tracked:
                    continue
                if not (REPO_ROOT / ref).exists():
                    # Never existed anywhere. A plain broken reference, and
                    # not the N1 class, which is about files that exist
                    # locally and vanish in CI.
                    continue
                n_claims = len([
                    c for c in
                    [mm.group(0) for mm in ca.NUMERIC_CLAIM.finditer(para)]
                    if not ca.is_exempt_number(c)
                ]) + len(list(ca.SUPERLATIVE_CLAIM.finditer(para)))
                hits.append({
                    "file": rel,
                    "ref": ref,
                    "paragraph_start": start,
                    "claims": n_claims,
                    "working": is_working_document(rel),
                })
                break   # one record per paragraph
    return hits


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if any tracked document cites a path the "
                         "repository does not contain. NOT wired into CI: "
                         "some hits are legitimate references to artefacts "
                         "the tool generates for a user. Triage first.")
    args = ap.parse_args()

    tracked = tracked_files()
    hits = scan(tracked)

    # Every count below is produced by the predicate that built `hits`.
    # None of them is read off the listing.
    published = [h for h in hits if not h["working"]]
    working = [h for h in hits if h["working"]]
    commit = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"], cwd=REPO_ROOT,
        capture_output=True, text=True, check=True).stdout.strip()

    print(f"commit {commit}, tree {REPO_ROOT}")
    for h in sorted(hits, key=lambda r: (r["working"], r["file"])):
        tag = "working-document" if h["working"] else "PUBLISHED-SURFACE"
        print(f"  {h['file']}  <- {h['ref']}  claims={h['claims']}  [{tag}]")
    print()
    print(f"paragraphs total          : {len(hits)}")
    print(f"  on published surfaces   : {len(published)}"
          f"  across {len({h['file'] for h in published})} distinct files")
    print(f"  in working documents    : {len(working)}"
          f"  across {len({h['file'] for h in working})} distinct files")
    print(f"paragraphs carrying >=1 claim: "
          f"{len([h for h in hits if h['claims']])}"
          f"  (published: {len([h for h in published if h['claims']])})")
    print(f"distinct untracked refs   : {len({h['ref'] for h in hits})}"
          f"  {sorted({h['ref'] for h in hits})}")

    if args.check and hits:
        print("\nFAIL: a citation must be tracked. See finding N1.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
