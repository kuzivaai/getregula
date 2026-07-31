#!/usr/bin/env python3
# regula-ignore
"""The ONLY sanctioned mechanism for propagating the published test count.

Two incidents share one cause: count propagation performed as a manual bulk
edit. The Phase 0 cascade deviation, and a near-miss on 28 July 2026 where a
global `2353` -> `2354` replace rewrote a package download URL hash path and
an integrity `size = 222353` field inside `uv.lock`. That lockfile would have
failed installs and integrity verification. `git diff` caught it; nothing
else would have.

**From 28 July 2026 a manual bulk numeric edit for count propagation is a
rule violation, not a risk.** See `.claude/rules/measurement.md` 4c and 4d.

Design, and why each part is load-bearing:

  - The surface list comes from `data/published_count_manifest.json`, which
    is committed data. Nothing outside it is ever opened for writing.
  - **Refusal is by construction, not by filter.** The script iterates the
    manifest. A file that is not in the manifest is never a candidate, so a
    lockfile cannot be reached even by an unlucky pattern. Extension denial
    is a second belt, not the mechanism.
  - The new value comes from the canonical source, never from an argument,
    so a typo cannot become the published number.
  - Replacement is context-bound: the old value must appear with a known
    surrounding shape (a separator, a word boundary, a JSON key). A bare
    digit run is not sufficient to trigger a write.

Usage:
    python3 scripts/cascade_count.py --check    # report drift, write nothing
    python3 scripts/cascade_count.py --apply    # propagate

Stdlib only.
"""

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

REPO = Path(__file__).resolve().parent.parent
MANIFEST = REPO / "data/published_count_manifest.json"
CANONICAL = REPO / "data/site_facts.json"

# Second belt only. The mechanism is manifest iteration; this exists so that
# a manifest edit cannot quietly add a lockfile.
DENY_SUFFIXES = {".lock", ".sum", ".sha256", ".sha512", ".whl", ".tar",
                 ".gz", ".zip", ".sig", ".asc", ".pem", ".der"}
DENY_NAMES = {"uv.lock", "poetry.lock", "package-lock.json", "Cargo.lock",
              "yarn.lock", "Pipfile.lock", "go.sum", "requirements.lock"}


# EXPLICIT TEMPLATES, not heuristics.
#
# Two heuristic designs were tried and both rewrote years. A +/-20% band
# around 2,354 spans 1883-2824 and contains 2026; adding a "must sit near
# count vocabulary" window did not help, because in a document about a test
# suite almost every number is within 90 characters of the word "test".
#
# So the tool does not guess which number is a count. It replaces only these
# exact shapes. A year never appears inside "N passing" or "N
# pytest-collected", so the class of error is eliminated rather than reduced.
#
# {n} is the count, with or without a thousands separator (comma or full
# stop; de-DE and pt-BR group with a full stop).
#
# {g} is the gap between the number and its unit word. It is NOT `\s+`.
#
# MEASURED 2026-07-31. Every template below used to join with `\s+`. The
# landing page publishes the count as
#     <strong style="color:var(--text);">2,354</strong> tests
# and `</strong> ` is not whitespace, so no template matched, `_stale_values`
# nominated nothing, and `--check` printed "all manifest surfaces already
# carry the canonical value" and exited 0 while site/index.html was 258
# short. It stayed that way across cascades to 2,595, 2,608 and 2,612.
#
# The gap tolerates whitespace and complete HTML tags, and nothing else. It
# deliberately does NOT tolerate arbitrary text: the unit word must still be
# the next thing after the number, because the unit word is the whole reason
# a year is safe here. Widening this to "somewhere near the word tests" is
# the heuristic the header above records as tried and abandoned twice.
GAP = r"(?:\s|</?[a-zA-Z][^>]*>)+"

COUNT_TEMPLATES = [
    r"tests-{n}%20passing",
    r"{n}{g}passing",
    r"{n}{g}pytest-collected",
    r"{n}{g}unique tests",
    r"{n}{g}\[unique\]",
    # Plural only: matches "2,354 tests", German "2.612 Tests" and pt-BR
    # "2.612 testes", but NOT "963 test functions", which is a different
    # quantity that docs/TRUST.md publishes three lines away.
    r"{n}{g}test(?:s|es)\b",
    # NOT a bare "{n} passed": the custom runner publishes "1386 passed",
    # a different quantity. Caught by this module's own sync test.
    r"Expected:\s*{n}\s+passed",
    r"{n}\s+pytest\b",
    r'"total_collected"\s*:\s*{n}',
    r"total_collected\s*=\s*{n}",
    r"\|\s*{n}\s*\|",
    r"\({n}\s+pytest-collected\)",
]


class RefusedError(RuntimeError):
    """Raised when a target is outside what this tool may ever touch."""


def canonical_count() -> int:
    """The published count, from committed data, verified against reality.

    `data/site_facts.json` is a CACHE. Reading it alone made `--check` a
    blank gate: add tests without regenerating it and the tool compares
    every surface against a stale canonical, finds them all in agreement,
    and exits 0. MEASURED 2026-07-28 - the file said 2,363 while the suite
    collected 2,404, and `--check` reported "all manifest surfaces already
    carry the canonical value".

    That matters beyond this tool. `docs/improvement/HANDOVER.md` lists
    `cascade_count.py --check` in the block a fresh session runs to
    establish that the tree is trustworthy, and rc=0 was being read as
    proof the published counts were current.

    The canonical value still comes from committed data, never from an
    argument, so a typo cannot become the published number. It is now
    cross-checked against a live computation, and a disagreement is a
    refusal rather than a silent pass.
    """
    facts = json.loads(CANONICAL.read_text(encoding="utf-8"))
    cached = int(facts["counts"]["tests"]["total_collected"])

    import site_facts
    live = int(site_facts.compute()["counts"]["tests"]["total_collected"])
    if cached != live:
        raise RefusedError(
            f"data/site_facts.json is stale: it records {cached:,} collected "
            f"tests, the suite currently collects {live:,}. Regenerate it "
            f"with `python3 scripts/site_facts.py` and re-run. Refusing to "
            f"cascade a cached number, and refusing to report a clean check "
            f"against one."
        )
    return cached


def manifest_surfaces() -> list[str]:
    doc = json.loads(MANIFEST.read_text(encoding="utf-8"))
    out = []
    for entry in doc.get("published_surfaces", []):
        if isinstance(entry, str):
            out.append(entry)
        elif isinstance(entry, dict):
            for key in ("file", "path", "surface"):
                if key in entry:
                    out.append(entry[key])
                    break
    return out


def assert_permitted(rel: str) -> None:
    """Refuse anything that must never be rewritten, even if manifested."""
    p = Path(rel)
    if p.name in DENY_NAMES or p.suffix.lower() in DENY_SUFFIXES:
        raise RefusedError(
            f"REFUSED: {rel} is a lockfile/checksum class file. Count "
            f"propagation may never rewrite these. A digit run inside a hash "
            f"or a size field is not a claim.")
    if p.is_absolute() or ".." in p.parts:
        raise RefusedError(f"REFUSED: {rel} escapes the repository root.")


def _patterns(old: int):
    """Context-bound matches only. A bare digit run never qualifies."""
    plain, comma = str(old), f"{old:,}"
    for lit in (comma, plain):
        esc = re.escape(lit)
        # \w not \d: "ee2353d8330" must NOT match. Excluding only digits
        # let a hash path through, which is exactly the 28 July near-miss.
        yield re.compile(rf"(?<![\w,.]){esc}(?![\w,.])")


def _dotted(value: int) -> str:
    """de-DE / pt-BR thousands grouping: 2612 -> '2.612'."""
    return f"{value:,}".replace(",", ".")


def _swap(fragment: str, old: int, new: int) -> str:
    """Replace old with new inside a matched count fragment, keeping the
    thousands-separator style the surface already uses.

    The dotted form is handled FIRST and explicitly. Writing `2,612` into
    a German or Brazilian page would correct the number and corrupt the
    language, which is a different published defect, not a fix.
    """
    return (fragment.replace(_dotted(old), _dotted(new))
                    .replace(f"{old:,}", f"{new:,}")
                    .replace(str(old), str(new)))


def propagate(new: int, apply: bool) -> int:
    changed, drift = 0, []
    for rel in manifest_surfaces():
        assert_permitted(rel)
        p = REPO / rel
        if not p.exists():
            print(f"  MISSING  {rel}")
            continue
        text = p.read_text(encoding="utf-8")
        updated = text
        for old in _stale_values(text, new):
            for rx in _count_regexes(old):
                updated = rx.sub(
                    lambda m: _swap(m.group(0), old, new), updated)
        if updated != text:
            drift.append(rel)
            if apply:
                p.write_text(updated, encoding="utf-8")
                changed += 1
    if drift:
        verb = "updated" if apply else "would update"
        print(f"  {verb}: {len(drift)} surface(s)")
        for rel in drift:
            print(f"    {rel}")
    else:
        print("  all manifest surfaces already carry the canonical value")
    return changed if apply else len(drift)


def _count_regexes(value: int):
    """Compiled regexes for every sanctioned shape of `value`.

    Three renderings of the same number are sanctioned: bare (`2612`),
    comma-grouped (`2,612`) and dot-grouped (`2.612`). The third exists
    because site/locales/de.html and site/locales/pt-br.html are manifest
    surfaces and both group thousands with a full stop.
    """
    plain, comma, dot = str(value), f"{value:,}", _dotted(value)
    alt = "(?:{})".format(
        "|".join(re.escape(s) for s in (comma, dot, plain)))
    for tpl in COUNT_TEMPLATES:
        yield re.compile(
            tpl.replace("{n}", alt).replace("{g}", GAP), re.IGNORECASE)


def _stale_values(text: str, new: int) -> set:
    """Values appearing in a sanctioned count shape but differing from
    canonical. Nothing outside COUNT_TEMPLATES is ever a candidate.

    The candidate scanner accepts a full stop as a thousands separator as
    well as a comma. Without that, `2.349` on the German and Brazilian
    landing pages was not merely unmatched by the templates, it was never
    nominated as a candidate at all, so both blindnesses had to be closed
    to make either page reachable.
    """
    out = set()
    lo, hi = int(new * 0.5), int(new * 2)
    for m in re.finditer(
            r"(?<![\w,.])(\d{1,3}[.,]\d{3}|\d{4})(?![\w,.])", text):
        val = int(m.group(1).replace(",", "").replace(".", ""))
        if val == new or not (lo <= val <= hi):
            continue
        for rx in _count_regexes(val):
            if rx.search(text):
                out.add(val)
                break
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--check", action="store_true")
    g.add_argument("--apply", action="store_true")
    args = ap.parse_args(argv)

    new = canonical_count()
    print(f"canonical count (data/site_facts.json): {new:,}")
    print(f"manifest surfaces: {len(manifest_surfaces())}")
    n = propagate(new, apply=args.apply)
    if args.check and n:
        print("\nDRIFT. Run with --apply.")
        return 1
    return 0


if __name__ == "__main__":
    from tree_guard import stamp
    stamp()
    raise SystemExit(main())
