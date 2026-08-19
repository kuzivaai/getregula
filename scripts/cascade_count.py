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
# The gap tolerates horizontal whitespace, INLINE HTML tags, space entities
# and HTML comments, and nothing else. It deliberately does NOT tolerate
# arbitrary text: the unit word must still be the next thing after the
# number, because the unit word is the whole reason a year is safe here.
# Widening this to "somewhere near the word tests" is the heuristic the
# header above records as tried and abandoned twice.
#
# Three deliberate narrowings, each one paid for by an adversarial review of
# the first version of this constant on 2026-07-31:
#
# 1. INLINE TAGS ONLY, named explicitly. The first version accepted any tag,
#    `</?[a-zA-Z][^>]*>`, which let the gap cross a block boundary:
#    `<h2>Roadmap 2026</h2>\n<p>tests ...` nominated 2026, and
#    `<tr><td>2,468</td><td>Tests updated</td></tr>` nominated 2,468. A
#    number in one block and a unit word in the next are not one claim.
# 2. NO NEWLINES. `[ \t]`, not `\s`. Same reason: a blank line between a
#    number and the word "tests" is a paragraph break, not a separator.
# 3. SPACE ENTITIES AND COMMENTS ARE MARKUP TOO. `&nbsp;` appears 64 times
#    in the published site and is used exactly as an inline separator after
#    a value. A guard that saw `</strong> ` but not `&nbsp;` would repeat
#    this repository's documented entity-blindness failure, where a check
#    for the literal em dash let seven `&mdash;` entities render live.
_INLINE_TAG = (
    r"</?(?:strong|b|em|i|span|a|code|kbd|mark|small|sup|sub|abbr|u|q"
    r"|time|data|var|samp|cite|dfn|s|del|ins|wbr|bdi|bdo|font)\b[^>]*>"
)
_SPACE_ENTITY = (
    r"&(?:nbsp|ensp|emsp|thinsp|hairsp|numsp|puncsp|#160|#8194|#8195"
    r"|#8201|#8202|#x[aA]0|#x00[aA]0|#x2002|#x2003|#x2009);"
)
_HTML_COMMENT = r"<!--.*?-->"
GAP = rf"(?:[ \t]|{_INLINE_TAG}|{_SPACE_ENTITY}|{_HTML_COMMENT})+"


# Which numbers are even NOMINATED as possibly-stale. Membership in a template
# shape is the real filter; this only decides what gets offered to it.
#
# CANDIDATE_THOUSANDS is the original and stays the default: four digits, or
# three-or-fewer grouped by a comma or a full stop (both, because the German
# and Brazilian pages group with a full stop). It cannot nominate a bare
# three-digit number, so **no published count below 1,000 could ever be found
# stale**. That is how `docs/architecture.md` published "112 test files" while
# git tracked 113 on the same commit: the number was not merely unmatched, it
# was never a candidate. The docstring on _stale_values already records the
# same class of blindness being closed once for dot-grouping.
#
# CANDIDATE_ANY_INTEGER nominates two digits and up. It is NOT safe for
# COUNT_TEMPLATES, which contains a bare table-cell shape (`| {n} |`) that any
# three-digit number in any table would match. Use it only with templates
# anchored on unit words specific enough to carry the whole filter themselves.
CANDIDATE_THOUSANDS = r"(?<![\w,.])(\d{1,3}[.,]\d{3}|\d{4})(?![\w,.])"
CANDIDATE_ANY_INTEGER = r"(?<![\w,.])(\d{1,3}[.,]\d{3}|\d{2,})(?![\w,.])"

COUNT_TEMPLATES = [
    # Shields.io badge forms, one per unit word, named explicitly.
    #
    # MEASURED 2026-08-06. Only the `passing` form existed, and README.md:10
    # publishes the same quantity as `tests-2683%20collected`. Nothing matched
    # it, so `--apply` never rewrote it and `--check` reported "all manifest
    # surfaces already carry the canonical value" while README.md, manifest
    # surface number one, was 33 short on this branch and the same literal on
    # `main` was 7 short of main's own canonical. README.md:278 carries
    # `| 2,716 |` and satisfies the check, so one file both satisfied and
    # violated at once: measurement rule 5 in live form.
    #
    # The writer stays explicit and the reader goes general, deliberately.
    # A tool that WRITES must only ever match shapes someone named, which is
    # this module's founding rule. Catching an unnamed badge word is the job
    # of the at-rest check in tests/test_cascade_count.py, which reads only
    # and fails loudly telling you to add the template here.
    r"tests-{n}%20passing",
    r"tests-{n}%20collected",
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
    r"Expected:\s*{n}\s+collected",
    r"{n}\s+pytest\b",
    r'"total_collected"\s*:\s*{n}',
    r"total_collected\s*=\s*{n}",
    r"\|\s*{n}\s*\|",
    r"\({n}\s+pytest-collected\)",
]


# The SECOND published quantity: how many functions the legacy custom runner
# selects. docs/TRUST.md publishes it twice, three lines from the collected
# count, and it moves whenever a test module is wired into
# tests/test_classification.py, which .claude/rules/tests.md requires.
#
# It was deliberately excluded from COUNT_TEMPLATES above, whose comment records
# that "963 test functions" is "a different quantity that docs/TRUST.md
# publishes three lines away". That exclusion was right and stays right: these
# templates are a separate list applied in a separate pass against a separate
# canonical, so neither quantity can ever be written with the other's value.
#
# WHY IT IS HERE NOW. Leaving it uncascaded cost two full suite runs to
# discover on 2026-08-14 alone, once for the content-freshness module and once
# for the documented-transcripts module. tests/test_published_count_manifest.py
# catches the drift and names the cause, so it failed closed rather than
# publishing a wrong number, but "fails closed twice in one session" is a
# recurring manual step, which is what this module exists to remove.
#
# The shapes are anchored on the VERB, not on the unit word. "functions" alone
# would nominate "442 defined in-file", a third quantity on the same line.
RUNNER_TEMPLATES = [
    rf"discovers{GAP}{{n}}{GAP}functions",
    rf"executes{GAP}{{n}}{GAP}functions",
]


# The THIRD published quantity: how many test FILES there are.
#
# WHY IT IS HERE. `docs/architecture.md` publishes one line carrying the test
# FILE count and the collected count together. The collected half was
# cascade-managed and correct; the file half was managed by nobody and was
# already wrong by one at `ea64ffe`. It is the exact shape measurement rule 5
# warns about: half a line carries a guarantee and the whole line reads as
# though it does. (The figures are deliberately not written here. Derive them
# with `python3 scripts/cascade_count.py --check`; a canonical count written as
# a literal into a living document is what tests/test_published_count_manifest
# exists to refuse, and this comment failed that check on its first draft.)
#
# Anchored on the unit words "test files", which no other quantity in the
# corpus uses, and applied in its own pass against its own canonical so it can
# never be written with the collected or runner value.
TEST_FILE_TEMPLATES = [
    rf"{{n}}{GAP}test files",
]


# The FOURTH published quantity: how many commands the CLI registers.
#
# WHY IT IS HERE. Ledger N131 recorded it as a fourth ungated quantity and it is
# the worst of the four, for two reasons the other three do not have. It is
# published in THREE LANGUAGES, so a miss is invisible to a reader of the
# language that was updated. And `claim_auditor --verify-facts` was the only
# thing standing between a miss and a published wrong number, which makes it a
# reader rather than a writer: it can say "this is wrong" but never fix it, so
# every command added or removed meant a hand-applied edit across three locales.
#
# N131's own enumeration named five locations. Enumerated again on 2026-08-17
# the live reader-facing set is TWELVE, across five files and three languages,
# and the one N131 named that a plain adjacency grep does NOT find is
# `site/about.html`, which reads "62 CLI commands" with a qualifier between the
# number and its unit word. That is measurement rule 4c's own failure mode
# (hand enumeration under-counting, now the sixth occurrence in this programme)
# and simultaneously ledger N10's (the unit word is not always adjacent). Both
# are why the qualifier form below exists as its own template rather than being
# assumed away.
#
# CANDIDATE_ANY_INTEGER is required: the count is two digits, and
# CANDIDATE_THOUSANDS structurally cannot nominate a number below 1,000, which
# is the blindness that let "112 test files" stand while git tracked 113.
COMMAND_TEMPLATES = [
    # English, bare and with a qualifier between the number and the unit word.
    rf"{{n}}{GAP}commands",
    rf"{{n}}{GAP}CLI{GAP}commands",
    # German. The site ships de-DE and the unit word is inflected, not translated
    # word-for-word, so a pattern list written only in English is blind to it by
    # construction. This is N107's finding in a second instrument.
    rf"{{n}}{GAP}Befehle",
    # Brazilian Portuguese.
    rf"{{n}}{GAP}comandos",
    # The README's own summary table, where the number follows its unit words.
    rf"CLI commands{GAP}?\|{GAP}?{{n}}",
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


def canonical_runner_count() -> int:
    """The published runner function count, cached then cross-checked.

    Same contract as `canonical_count`: the value comes from committed data so
    a typo cannot become the published number, and a stale cache is a refusal
    rather than a silent pass. The live side calls
    `site_facts.count_runner_functions()` directly rather than `compute()`,
    because `compute()` re-runs pytest collection and this pass does not need
    it.
    """
    facts = json.loads(CANONICAL.read_text(encoding="utf-8"))
    tests = facts["counts"]["tests"]
    if "runner_functions" not in tests:
        raise RefusedError(
            "data/site_facts.json has no counts.tests.runner_functions. "
            "Regenerate it with `python3 scripts/site_facts.py`. Refusing to "
            "cascade a quantity with no canonical source.")
    cached = int(tests["runner_functions"])

    import site_facts
    live = int(site_facts.count_runner_functions())
    if cached != live:
        raise RefusedError(
            f"data/site_facts.json is stale: it records {cached:,} runner "
            f"functions, the runner currently selects {live:,}. Regenerate it "
            f"with `python3 scripts/site_facts.py` and re-run.")
    return cached


def canonical_test_file_count() -> int:
    """The published test-FILE count, cached then cross-checked.

    Same contract as the other two canonicals. The population is the keys of
    `counts.tests.per_file`, which `site_facts.count_tests` builds by the same
    recursive walk pytest collects from, and whose tracking is already policed
    (`untracked_test_contributors` warns at generation, `tests/test_site_facts`
    fails at rest). Deriving the count from that dict rather than re-walking
    means it cannot disagree with the per-file inventory it is a summary of.
    """
    facts = json.loads(CANONICAL.read_text(encoding="utf-8"))
    tests = facts["counts"]["tests"]
    if "per_file" not in tests:
        raise RefusedError(
            "data/site_facts.json has no counts.tests.per_file. Regenerate it "
            "with `python3 scripts/site_facts.py`. Refusing to cascade a "
            "quantity with no canonical source.")
    cached = len(tests["per_file"])

    import site_facts
    live = len(site_facts.count_tests()["per_file"])
    if cached != live:
        raise RefusedError(
            f"data/site_facts.json is stale: it records {cached:,} test files, "
            f"the tree currently has {live:,}. Regenerate it with "
            f"`python3 scripts/site_facts.py` and re-run.")
    return cached


def canonical_command_count() -> int:
    """The published command count, cached then cross-checked TWICE.

    Same contract as the other three canonicals: the value comes from committed
    data so a typo cannot become the published number, and a stale cache is a
    refusal rather than a silent pass.

    This one is cross-checked against two independent derivations rather than
    one, and that is deliberate. `site_facts.count_commands` counts `def cmd_*`
    definitions with a hand-written compensation for the `monitor` sub-command
    group; `site_facts.count_commands_from_registry` reads the argparse registry,
    which is the population the published claim is actually about, because "62
    commands" promises a reader what they can type. Requiring the two to agree
    turns that compensation from a coincidence into a checked invariant: a
    command registered with no handler, or a handler nothing registers, becomes
    a refusal here instead of a number that depends on which function was called.
    """
    facts = json.loads(CANONICAL.read_text(encoding="utf-8"))
    counts = facts["counts"]
    if "commands" not in counts:
        raise RefusedError(
            "data/site_facts.json has no counts.commands. Regenerate it with "
            "`python3 scripts/site_facts.py`. Refusing to cascade a quantity "
            "with no canonical source.")
    cached = int(counts["commands"])

    import site_facts
    registry = int(site_facts.count_commands_from_registry())
    handlers = int(site_facts.count_commands())
    if registry != handlers:
        raise RefusedError(
            f"the two command derivations disagree: the argparse registry "
            f"offers {registry:,} commands and {handlers:,} are derived from "
            f"`cmd_` handlers. One of them is wrong and this tool will not "
            f"pick. Either a command is registered with no handler, or a "
            f"handler exists that nothing registers.")
    if cached != registry:
        raise RefusedError(
            f"data/site_facts.json is stale: it records {cached:,} commands, "
            f"the CLI currently registers {registry:,}. Regenerate it with "
            f"`python3 scripts/site_facts.py` and re-run.")
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

    EXACTLY ONE substitution is made, and that is load-bearing. The first
    version chained three unbounded `str.replace` calls over the whole
    matched fragment. Once GAP began pulling complete tags (with their
    attributes) into the match, that rewrote digits inside attributes:

        IN   <strong>2,354</strong><a href="/c#build-2354" id="n2354"> tests</a>
        OUT  <strong>2,622</strong><a href="/c#build-2622" id="n2622"> tests</a>

    which is measurement rule 4d's own class, the uv.lock near-miss, reopened
    inside the module whose header documents it. Every count template except
    the badge puts the number first, so a form the fragment BEGINS with is
    the published number itself; the badge is handled by taking the earliest
    occurrence instead. Nothing later in the fragment is ever touched.
    """
    forms = ((_dotted(old), _dotted(new)),
             (f"{old:,}", f"{new:,}"),
             (str(old), str(new)))
    for was, now in forms:
        if fragment.startswith(was):
            return now + fragment[len(was):]
    earliest = None
    for was, now in forms:
        at = fragment.find(was)
        if at != -1 and (earliest is None or at < earliest[0]):
            earliest = (at, was, now)
    if earliest is None:
        return fragment
    at, was, now = earliest
    return fragment[:at] + now + fragment[at + len(was):]


def propagate(new: int, apply: bool, templates=None, label: str = "count",
              candidates: str = None) -> int:
    templates = templates or COUNT_TEMPLATES
    changed, drift = 0, []
    for rel in manifest_surfaces():
        assert_permitted(rel)
        p = REPO / rel
        if not p.exists():
            print(f"  MISSING  {rel}")
            continue
        text = p.read_text(encoding="utf-8")
        updated = text
        for old in _stale_values(text, new, templates, candidates):
            for rx in _count_regexes(old, templates):
                updated = rx.sub(
                    lambda m: _swap(m.group(0), old, new), updated)
        if updated != text:
            drift.append(rel)
            if apply:
                p.write_text(updated, encoding="utf-8")
                changed += 1
    if drift:
        verb = "updated" if apply else "would update"
        print(f"  {verb} ({label}): {len(drift)} surface(s)")
        for rel in drift:
            print(f"    {rel}")
    else:
        print(f"  all manifest surfaces already carry the canonical {label}")
    return changed if apply else len(drift)


def _count_regexes(value: int, templates=None):
    """Compiled regexes for every sanctioned shape of `value`.

    Three renderings of the same number are sanctioned: bare (`2612`),
    comma-grouped (`2,612`) and dot-grouped (`2.612`). The third exists
    because site/locales/de.html and site/locales/pt-br.html are manifest
    surfaces and both group thousands with a full stop.

    The alternation carries a LEFT boundary so a shorter value cannot match
    inside a longer one. Without it, `14` matches the tail of `114` and the
    tool reports permanent drift on a file it has just corrected: observed
    2026-08-15 on `docs/architecture.md` the moment two-digit values became
    nominatable. There is deliberately NO right boundary: one template is the
    JSON shape `"total_collected": {n}`, where the next character is a comma,
    and a trailing `(?![\\d.,])` would stop the tool seeing its own canonical.
    """
    templates = templates or COUNT_TEMPLATES
    plain, comma, dot = str(value), f"{value:,}", _dotted(value)
    alt = r"(?<![\d.,])(?:{})".format(
        "|".join(re.escape(s) for s in (comma, dot, plain)))
    for tpl in templates:
        yield re.compile(
            tpl.replace("{n}", alt).replace("{g}", GAP), re.IGNORECASE)


def _stale_values(text: str, new: int, templates=None,
                  candidates: str = None) -> set:
    """Values appearing in a sanctioned count shape but differing from
    canonical. Nothing outside COUNT_TEMPLATES is ever a candidate.

    The candidate scanner accepts a full stop as a thousands separator as
    well as a comma. Without that, `2.349` on the German and Brazilian
    landing pages was not merely unmatched by the templates, it was never
    nominated as a candidate at all, so both blindnesses had to be closed
    to make either page reachable.

    There is deliberately NO magnitude window. An earlier version silently
    skipped candidates outside [0.5x, 2x] of canonical, which structurally
    hid `docs/architecture.md`'s stale "1,223 tests" against a canonical of
    2,618 (ledger row N57, sub-item 1). Membership in a COUNT_TEMPLATES
    shape is the only filter: a number that renders in a sanctioned count
    shape and differs from canonical is stale whatever its magnitude, and
    a magnitude the templates never match cannot be nominated anyway.
    """
    templates = templates or COUNT_TEMPLATES
    out = set()
    for m in re.finditer(candidates or CANDIDATE_THOUSANDS, text):
        val = int(m.group(1).replace(",", "").replace(".", ""))
        if val == new:
            continue
        for rx in _count_regexes(val, templates):
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
    runner = canonical_runner_count()
    test_files = canonical_test_file_count()
    commands = canonical_command_count()
    print(f"canonical count (data/site_facts.json): {new:,}")
    print(f"canonical runner functions: {runner:,}")
    print(f"canonical test files: {test_files:,}")
    print(f"canonical commands: {commands:,}")
    print(f"manifest surfaces: {len(manifest_surfaces())}")
    n = propagate(new, apply=args.apply, templates=COUNT_TEMPLATES,
                  label="collected count")
    n += propagate(runner, apply=args.apply, templates=RUNNER_TEMPLATES,
                   label="runner functions")
    n += propagate(test_files, apply=args.apply, templates=TEST_FILE_TEMPLATES,
                   label="test files", candidates=CANDIDATE_ANY_INTEGER)
    n += propagate(commands, apply=args.apply, templates=COMMAND_TEMPLATES,
                   label="commands", candidates=CANDIDATE_ANY_INTEGER)
    if args.check and n:
        print("\nDRIFT. Run with --apply.")
        return 1
    return 0


if __name__ == "__main__":
    from tree_guard import stamp
    stamp()
    raise SystemExit(main())
