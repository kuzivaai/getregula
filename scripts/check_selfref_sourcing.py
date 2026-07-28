#!/usr/bin/env python3
# regula-ignore
"""Pre-landing gate for claim batches, and the live control for F21.

HISTORY, because it explains the shape of this file.

Before 1.5c this script re-implemented the F21 detection outside the
auditor: it looked for paragraphs where `paragraph_has_source()` returned
reason "url" and the only URLs present were the page's own canonical,
og:url or alternate. That was the right shape for a pre-landing gate while
the auditor itself was still broken.

1.5c moved the mechanism into `claim_auditor.paragraph_has_source()`. The
old detection then became unreachable by construction: a self-referential
URL can no longer produce reason "url", so the script reported CLEAN on
every input including its own known offender. **A permanently green check
is a blank gate**, which is precisely what `.claude/rules/measurement.md`
rule 4 exists to stop. So it was rewritten rather than left in place.

What it does now, in order:

1. **Control.** Plants a paragraph whose only source is its own canonical
   URL and asserts the auditor rejects it, and plants a properly sourced
   paragraph and asserts the auditor accepts it. If the control does not
   fire, the script exits 2 and reports nothing else: an instrument that
   cannot be shown to work reports nothing worth reading.
2. **Gate.** Reports every paragraph in the named files that carries a
   numeric claim and has no source, with the reason. This is what a
   pre-landing check on a claim batch actually needs.

Usage:
    python3 scripts/check_selfref_sourcing.py FILE [FILE ...]
    python3 scripts/check_selfref_sourcing.py --pack   # files named in PACK-1.5b.md
    python3 scripts/check_selfref_sourcing.py --control-only

Exit 0 = control fired and no unsourced claims. Exit 1 = unsourced claims
present. Exit 2 = the control failed, so the run proves nothing.

Stdlib only.
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import claim_auditor as ca  # noqa: E402

SELFREF_ONLY = (
    '<link rel="canonical" href="https://getregula.com/control.html">\n'
    '<meta name="description" content="Regula ships 419 patterns.">'
)
PROPERLY_SOURCED = (
    'Regula ships 419 patterns, counted by scripts/site_facts.py.'
)


def control() -> bool:
    """Positive proof that the F21 mechanism is live in this working tree."""
    rejected, reason = ca.paragraph_has_source(SELFREF_ONLY)
    accepted, _ = ca.paragraph_has_source(PROPERLY_SOURCED)
    ok = (rejected is False) and (accepted is True)
    print("control:")
    print(f"  self-referential-only paragraph -> "
          f"{'REJECTED (correct)' if not rejected else f'ACCEPTED as {reason!r} (WRONG)'}")
    print(f"  properly sourced paragraph      -> "
          f"{'ACCEPTED (correct)' if accepted else 'REJECTED (WRONG)'}")
    if not ok:
        print("\nCONTROL FAILED. The F21 repair is not active in this tree, "
              "so nothing this script reports can be trusted.\n"
              "See tests/test_selfref_sourcing.py.", file=sys.stderr)
    return ok


def audit(paths: list[Path]) -> int:
    """Report paragraphs carrying a numeric claim with no source."""
    offenders = []
    checked = 0
    allowlist = ca.load_allowlist()

    for p in paths:
        if not p.exists():
            print(f"  SKIP (missing): {p}")
            continue
        raw = p.read_text(encoding="utf-8", errors="replace")
        rel = str(p.relative_to(ca.REPO_ROOT) if p.is_absolute() else p)
        identity = ca.page_identity(raw, rel)
        cleaned = ca.strip_noise(raw, p.suffix.lower())

        for start, end, para in ca.split_paragraphs(cleaned):
            claims = [c.group(0).strip()
                      for c in ca.NUMERIC_CLAIM.finditer(para)
                      if not ca.is_exempt_number(c.group(0).strip())]
            if not claims:
                continue
            checked += 1
            has_src, reason = ca.paragraph_has_source(para, identity)
            if has_src:
                continue
            live = [c for c in claims
                    if not ca.is_quarantined(rel, c)
                    and not any(a.search(c) or a.search(para)
                                for a in allowlist)]
            if live:
                offenders.append((rel, start, end, live[:4], reason))

    print(f"\nparagraphs with numeric claims checked: {checked}")
    if not offenders:
        print("RESULT: CLEAN. Every numeric claim is sourced, quarantined "
              "or allowlisted.")
        return 0

    print(f"RESULT: {len(offenders)} PARAGRAPH(S) CARRY AN UNSOURCED CLAIM\n")
    for rel, start, end, claims, reason in offenders:
        print(f"  {rel}:{start}-{end}  ({reason})")
        print(f"      claims : {claims}")
    print("\nSource each properly within the batch, correct it, or hold it.")
    return 1


def _pack_files() -> list[Path]:
    """Files named in PACK-1.5b.md, so the gate follows the pack."""
    pack = ca.REPO_ROOT / "docs/improvement/PACK-1.5b.md"
    if not pack.exists():
        print("PACK-1.5b.md not found", file=sys.stderr)
        raise SystemExit(2)
    text = pack.read_text(encoding="utf-8")
    found = set()
    for m in re.finditer(r'`?((?:site|docs|scripts|benchmarks)/[\w./-]+'
                         r'\.(?:html|md|py|txt))', text):
        found.add(m.group(1))
    return sorted(ca.REPO_ROOT / f for f in found)


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        raise SystemExit(2)
    if not control():
        raise SystemExit(2)
    if args[0] == "--control-only":
        raise SystemExit(0)
    if args[0] == "--pack":
        targets = _pack_files()
        print(f"\nauditing {len(targets)} file(s) named in PACK-1.5b.md")
    else:
        targets = [Path(a) for a in args]
    raise SystemExit(audit(targets))
