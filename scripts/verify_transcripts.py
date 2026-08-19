#!/usr/bin/env python3
# regula-ignore
"""Every executable result this project publishes must reproduce.

A transcript is a promise that running the command shown produces the output
shown. Three ways that promise was broken, all measured on 2026-08-14 against
tracked pages:

  1. **Superseded format.** `site/guides/article-9-risk-management.html` and
     `site/guides/eu-ai-act-recruitment-hiring.html` publish
     `EU AI Act Compliance Gap Assessment` with `Overall score: 29%`. No CLI
     command emits either string any more; `format_gap_text` survives only in
     `compliance_check.py`'s own `__main__` block and as an unused import in
     `cli_compliance.py`. `regula gap` now prints the decision-kernel text,
     which reports `insufficient_information` and the facts still needed. The
     published form is also the compliance-score framing the project's hard
     rule forbids, so this was a claim defect as well as a staleness defect.

  2. **Retired wording for a varying number.** Several pages wrote a detector
     priority as `confidence: 43%`. The tool emits `detector priority: 43`,
     because a count of matched patterns is not a likelihood and labelling it
     one invites the reader to treat it as a probability of being correct.

  3. **A dated provenance line that no longer held.**
     `examples/cv-screening-app/README.md` said "verified against Regula
     v1.7.6 on 2026-07-20" above a block containing the retired verdict.
     A stale provenance line is worse than none: it invites trust in the
     transcript beneath it.

The checker runs **the command the page tells the reader to run**, taken from
the manifest, rather than a command chosen to make the anchors match. A page
whose command no longer demonstrates its own output fails here, which a
golden-file comparison against a curated invocation would not catch. That
matters concretely: the bundled fixtures live under `examples/`, which the
default production scope excludes, so a page that omits `--scope all` shows a
reader `NO ACTIVE PRODUCTION-SCOPE PATTERNS` and nothing else.

**The non-reproducible reading this docstring used to call unexplained is
explained, and the explanation reversed its conclusion.** While this checker was
being written, one checkout of HEAD returned `[INFO] [ 43]` / `INFO tier: 1` for
the cv-screening fixture while others returned `[WARN] [ 63]`, and this text
concluded that the pages publishing 43 were stale. Both halves were wrong.
`_is_example_file` (`scripts/report.py`) inspects the resolved path for an
`examples` segment and a match subtracts a flat 20, so 43 is the correct value
for the in-repo fixture path the documented command actually uses; and the
readings that disagreed did so because the scan cache keyed on the path RELATIVE
to the scan root while provenance was derived from the FULL path, so whichever
scan ran first decided what the other read. The pages were corrected TO 43, the
cache key gained a path-context component, and both are settled. Kept here
rather than deleted because a checker that once drew the opposite conclusion
should show its own wrong turn; `data/documented_transcripts.json`'s
`_anchor_choice` field carries the same record.

Anchors are still confirmed across multiple checkouts, and `run_command` still
isolates the cache per invocation, for the reason that episode established: a
single reading in any one location is not enough to publish.

**Carriers, not suffixes.** A transcript is a transcript whatever file holds it.
On 2026-08-17 `site/assets/demo/regula-check.svg` was a terminal recording whose
entire content sat in SVG `<text>` nodes, and `README.md:32` rendered it as the
first visual on the project's front page; this checker could not read it, because
it filtered on a suffix list naming the three carriers anyone had thought of, and
what it was publishing was `Confidence scores: 0-100`, the framing retired across
nine surfaces. `.svg` is now read through `svg_text`, which reconstructs rendered
lines rather than treating the file as opaque, and `.yaml`/`.yml` are scanned for
retired markers because a tracked reference file describing the tool's output in
retired terms is the same defect on a different suffix.

Widening the scan named four defects on shipped content before anything was
changed, with no false positives: the recording, `docs/architecture.md`, and both
`references/en1822*_mapping.yaml` files. Those three recordings have since been
removed and the README embed replaced by a fenced transcript bound to a
re-runnable command, so `.svg` currently matches nothing here. That is the
correct state and not a reason to narrow the scan: the scope has to outlive the
files that motivated it.

Each CLI transcript anchor is checked in both directions:

  - it must appear in the surface file, so the manifest cannot assert a line
    the page does not contain and drift into fiction; and
  - it must appear in the real command output.

Benchmark instructions are discovered from the active, claim-capable delivery
surfaces in ``data/public_claim_surfaces.json``. A prose block that tells the
reader to reproduce a percentage with a local ``python3 benchmarks/...``
command is a contract: the command is run in an isolated copy of the tracked
checkout and its primary result must contain that percentage. The primary
result distinction matters. ``benchmarks/label.py score`` without a corpus
flag prints the library percentage in a secondary breakdown, even when its
headline result is for a different corpus. A substring check would therefore
approve the exact wrong-command defect this gate exists to catch.

Only local benchmark scripts are executable through this path. Shell syntax,
absolute paths and parent traversal are refused; commands are passed directly
to ``subprocess`` without a shell. The isolated copy prevents a benchmark that
writes a result file from modifying the working tree. Stdlib only. The verifier
itself makes no network requests; it runs only local, allowlisted commands from
the tracked checkout.

Usage:
    python3 scripts/verify_transcripts.py          # verify, exit 1 on drift
    python3 scripts/verify_transcripts.py --list   # show what is covered
"""
from __future__ import annotations

import argparse
import html
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

sys.path.insert(0, str(Path(__file__).parent))

from svg_text import SvgTextError, text_of  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
MANIFEST = REPO / "data/documented_transcripts.json"
PUBLIC_SURFACE_INVENTORY = REPO / "data/public_claim_surfaces.json"
TAG_RE = re.compile(r"<[^>]+>")
PERCENT_RE = re.compile(r"(?<![\w.])(\d+(?:\.\d+)?%)")
BENCHMARK_SURFACE_SUFFIXES = {".html", ".md", ".txt"}


@dataclass(frozen=True)
class BenchmarkContract:
    """One published percentage bound to the command offered to reproduce it."""

    surface: str
    command: tuple[str, ...]
    figure: str
    context: str

# Output vocabulary the CLI once emitted and no longer does. Every one was
# replaced by wording that does not assert a legal conclusion, which is why a
# page still showing it is a claim defect and not only a staleness defect.
#
# This list is not taken on trust. `retired_markers_are_unreachable()` runs the
# real commands and fails if any marker turns up in live output, so an entry
# that stops being retired cannot sit here quietly forbidding current wording.
RETIRED_MARKERS = {
    "Verdict: HIGH-RISK": "replaced by the decision block; asserted a tier the tool does not determine",
    "Verdict: PROHIBITED": "replaced by the decision block; asserted an Article 5 conclusion",
    "Verdict: LIMITED-RISK": "replaced by the decision block; asserted an Article 50 conclusion",
    "Your project is classified as": "a legal classification, which Regula does not make",
    "You must comply with Articles": "an obligation statement, which Regula does not make",
    "Your project contains AI practices prohibited": "an Article 5 determination",
    "EU AI Act Compliance Gap Assessment": "the gap command no longer produces this report",
    "Overall score:": "a compliance score; the concept was removed, not just the wording",
    "Confidence scores": "the 0-100 framing retired across nine surfaces; a count of "
                         "matched patterns is not a confidence, and the tool now writes "
                         "`Detector priority: 0-100 ... not a correctness probability`",
}

# Retired output whose number varies, so it cannot be a literal. The tool now
# writes `detector priority: 43`; `confidence: 43%` presented a pattern count
# as a likelihood, which is why it was replaced rather than reworded.
RETIRED_MARKER_PATTERNS = {
    r"confidence:\s*\d+%": "a detector priority is not a probability; "
                           "the tool emits `detector priority: N`",
}

# Output that is CURRENT and TRUE, and becomes a determination the moment it is
# published without the sentence the tool prints beside it.
#
# A retired-marker list can never catch this, and that is the point of having a
# second mechanism rather than a longer list. `regula classify --file app.py`
# really does print
#
#     Detector observation (not a legal classification):
#     HIGH-RISK: Employment and workers management - Articles 9, 10, ... 15
#
# beneath a full `Decision: insufficient_information` block. Four tracked
# surfaces published the last line ALONE. Every one of them was quoting the tool
# accurately and every one of them read as a legal classification attributed to
# the tool, which is the one thing this project's hard rule forbids. Adding the
# line to RETIRED_MARKERS would be false, and `retired_markers_are_unreachable`
# would correctly refuse it, because the tool does emit it.
#
# `qualified_output_is_really_emitted()` runs the command and requires the
# pattern AND its qualifier to appear together in real output, so a rule here
# describes what the tool prints rather than what an author would prefer.
QUALIFIED_OUTPUT = {
    "classification line": {
        # A tier followed by a prose category name. `[A-Z][a-z]` after the
        # colon is what separates the tool's output from a YAML mapping key
        # whose value is a template expression: `action.yml` carries
        # `PROHIBITED: ${{ steps.count-findings.outputs.prohibited_count }}`
        # twice, which is a variable name and not a claim about anybody.
        "pattern": re.compile(r"\b(?:PROHIBITED|HIGH-RISK|LIMITED-RISK|MINIMAL-RISK):\s+[A-Z][a-z]"),
        "qualifiers": (
            "Detector observation (not a legal classification)",
            "Detector observations (not legal facts)",
            "not a legal classification",
            "Decision: insufficient_information",
        ),
        "window": 400,
        "why": ("a bare tier line reads as a legal classification made by the tool; "
                "the CLI prints it under a qualifier and a decision block, and a "
                "transcript that drops those is quoting the tool into a claim it "
                "does not make"),
        "proof_command": ["classify", "--file", "examples/cv-screening-app/app.py"],
    },
}

# Historical records are reproduced as they were and must not be edited to suit
# a later state; scripts/ holds the retired formatter itself and the i18n
# strings it used; tests/ holds the controls that plant these markers on purpose.
MARKER_SCAN_EXCLUDED_PREFIXES = ("tests/", "scripts/", "docs/improvement/")

# Carriers a published transcript can sit on. `.svg` is here because a
# terminal-recorder SVG is entirely text; `.yaml`/`.yml` because tracked
# reference files describe the tool's output in prose and can describe it in
# retired terms. Measured before widening, on the tracked corpus at
# `bc36b66`: adding `.svg` surfaced one real defect and adding `.yaml`/`.yml`
# surfaced two, with zero false positives. The sweep proves what it found, not
# that no other carrier shape exists.
SURFACE_SUFFIXES = (".md", ".html", ".txt", ".svg", ".yaml", ".yml")

# Carriers whose text is not the bytes of the file.
STRUCTURED_TEXT_SUFFIXES = {".svg"}


def normalise(text: str) -> str:
    """Compare on content, not on column alignment.

    Output pads its labels into columns, and HTML wraps and escapes them.
    Collapsing whitespace lets a column width change pass while a changed
    number, tier or label still fails. Case is preserved: `WARN` and `INFO`
    are the distinction this checker exists to notice.

    Space before punctuation is closed up as well. Replacing a tag with a
    space turns `<span>Verdict</span>: PROHIBITED` into `Verdict : PROHIBITED`,
    which does not contain `Verdict: PROHIBITED`. The blog page wrapped exactly
    that line in markup, so without this the guard would have missed a marked-up
    verdict while catching a plain one. A control test pins it.
    """
    flattened = re.sub(r"\s+", " ", html.unescape(TAG_RE.sub(" ", text)))
    return re.sub(r"\s+([:;,.])", r"\1", flattened).strip()


def surface_text(path: Path) -> str:
    """The text a reader of this surface sees, normalised for comparison.

    A carrier whose text is not its bytes is decoded first. An SVG that cannot
    be parsed raises rather than returning an empty string: empty is the PASS
    value for every caller here, so swallowing the failure would turn an
    unreadable carrier into a clean one (measurement rule 4).
    """
    raw = path.read_text(encoding="utf-8", errors="replace")
    if path.suffix.lower() in STRUCTURED_TEXT_SUFFIXES:
        return normalise(text_of(raw))
    return normalise(raw)


def load_manifest() -> list[dict]:
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    return payload["transcripts"]


# The command prefix that invokes the CLI under test. The default is this
# working tree, run as a module. It is a parameter rather than a constant
# because the tree is not what anyone installs: N144 recorded that the strings
# RETIRED_MARKERS asserts are unreachable were reachable in the product on
# PyPI, and this guard could not have found that, because it could only ever
# run the tree. `scripts/verify_installed_artefact.py` passes the console
# script of a built, installed artefact here.
TREE_CLI: list[str] = [sys.executable, "-m", "scripts.cli"]


def run_command(argv: list[str], cli: list[str] | None = None,
                cwd: str | Path | None = None) -> tuple[str, int]:
    """Run the documented command exactly as a reader would, on a cold cache.

    `cli` is the executable prefix; `cwd` is the directory the command runs in,
    which decides how the fixture paths in `argv` resolve and, through
    `_is_example_file`, what the finding scores (N110). Both default to this
    tree so every existing caller is unchanged.

    The cache directory is redirected to a fresh temporary directory for every
    invocation. Without that, this check is not a measurement of the page: it
    measures the page plus whatever the ambient `~/.regula/cache` happens to
    hold.

    MEASURED 2026-08-15. This gate passed standalone and failed inside the full
    suite on the same commit and the same tree, differing only in cache state:
    with the cache left warm by a suite run the fixture reported
    `[WARN] [ 63]`, and with the cache emptied it reported `[INFO] [ 43]`,
    reproduced in both directions. Cache keys are
    `relative-path : schema : context : content-sha256`, so two byte-identical
    copies of a file at the same relative path share a key while their
    provenance, which `_is_example_file` derives from the FULL path, does not
    take part in the key. An entry written while scanning a copy outside
    `examples/` can therefore be served to a scan inside it, carrying the
    20-point example penalty away with it.

    Isolating the cache here makes the gate deterministic. It does NOT fix the
    underlying collision, which is recorded as N112 and is a product change
    this session did not make.
    """
    with tempfile.TemporaryDirectory(prefix="regula-transcript-cache-") as tmp:
        env = dict(os.environ, REGULA_CACHE_DIR=tmp)
        run = subprocess.run(
            [*(cli or TREE_CLI), *argv],
            cwd=str(cwd or REPO), capture_output=True, text=True, check=False,
            timeout=600, env=env,
        )
    return run.stdout + run.stderr, run.returncode


def verify() -> tuple[list[str], int]:
    problems: list[str] = []
    checked = 0
    for entry in load_manifest():
        surface = REPO / entry["surface"]
        if not surface.is_file():
            problems.append(f"{entry['surface']}: surface does not exist")
            continue
        try:
            page = surface_text(surface)
        except SvgTextError as exc:
            problems.append(f"{entry['surface']}: {exc}")
            continue
        output, _rc = run_command(entry["command"])
        shown = normalise(output)
        printable = "regula " + " ".join(entry["command"])
        for anchor in entry["anchors"]:
            needle = normalise(anchor)
            checked += 1
            if needle not in page:
                problems.append(
                    f"{entry['surface']}: anchor {anchor!r} is not on the page. "
                    f"The manifest is asserting a line this surface does not "
                    f"contain, so it has drifted from the page it guards.")
                continue
            if needle not in shown:
                problems.append(
                    f"{entry['surface']}: the page shows {anchor!r} but "
                    f"`{printable}` does not produce it. Either the transcript "
                    f"is stale, or the page documents a command that no longer "
                    f"demonstrates it.")
    return problems, checked


def public_benchmark_surfaces(
        inventory_path: Path = PUBLIC_SURFACE_INVENTORY,
        root: Path = REPO) -> list[str]:
    """Return readable public claim surfaces from the generated inventory.

    The inventory is the ceiling as well as the floor. Internal programme
    records intentionally preserve superseded measurements and must not become
    current product promises merely because they are tracked files.
    """
    payload = json.loads(inventory_path.read_text(encoding="utf-8"))
    found = set()
    for record in payload.get("records", []):
        if record.get("classification") != "active_product":
            continue
        if not record.get("claim_capable"):
            continue
        rel = record.get("source", "").split("#", 1)[0]
        path = root / rel
        if path.suffix.lower() in BENCHMARK_SURFACE_SUFFIXES and path.is_file():
            found.add(rel)
    return sorted(found)


def _semantic_blocks(path: Path) -> list[str]:
    """Split a surface at reader-visible block boundaries.

    Binding at block level is deliberate. A raw character window can let a
    caveat or figure in the next paragraph qualify the wrong command. HTML
    paragraphs and list items are explicit blocks; Markdown and text use blank
    lines, including blank blockquote lines.
    """
    raw = path.read_text(encoding="utf-8", errors="replace")
    if path.suffix.lower() == ".html":
        pattern = re.compile(
            r"<(?P<tag>p|li|blockquote|pre)\b[^>]*>.*?</(?P=tag)>",
            re.IGNORECASE | re.DOTALL,
        )
        return [m.group(0) for m in pattern.finditer(raw)]
    return [part for part in re.split(r"\n[ \t]*(?:>[ \t]*)?\n", raw)
            if part.strip()]


def _code_commands(block: str) -> list[tuple[str, ...]]:
    """Extract local benchmark commands only from code-formatted text."""
    candidates = []
    patterns = (
        re.compile(r"<code\b[^>]*>(.*?)</code>", re.IGNORECASE | re.DOTALL),
        re.compile(r"`([^`\n]+)`"),
        re.compile(r"(?m)^\s*(python3\s+benchmarks/[^\n#]+?)\s*$"),
    )
    for pattern in patterns:
        for match in pattern.finditer(block):
            candidate = normalise(match.group(1)).rstrip(".")
            if not candidate.startswith("python3 benchmarks/"):
                continue
            try:
                argv = tuple(shlex.split(candidate))
            except ValueError:
                continue
            if argv not in candidates:
                candidates.append(argv)
    return candidates


def discover_benchmark_contracts(
        inventory_path: Path = PUBLIC_SURFACE_INVENTORY,
        root: Path = REPO) -> list[BenchmarkContract]:
    """Discover reproduce-with percentage contracts on public surfaces.

    The percentage nearest the reproduction cue that is nearest the command is
    the claimed result. That rule is simple enough to control and inspect, and
    avoids selecting an earlier historical figure or a later comparison figure
    merely because the command happens to print it.
    Blocks with several benchmark commands are refused during verification:
    one prose claim cannot unambiguously bind different programs to one result.
    """
    contracts = []
    for rel in public_benchmark_surfaces(inventory_path, root):
        for block in _semantic_blocks(root / rel):
            reader = normalise(block)
            if "reproduc" not in reader.casefold():
                continue
            figure_matches = list(PERCENT_RE.finditer(reader))
            cue_positions = [m.start() for m in re.finditer(
                r"reproduc", reader, re.IGNORECASE)]
            if not figure_matches or not cue_positions:
                continue
            for command in _code_commands(block):
                command_pos = reader.find(" ".join(command))
                cue_pos = min(cue_positions,
                              key=lambda pos: abs(pos - command_pos))
                figure_match = min(
                    figure_matches,
                    key=lambda match: abs(match.start() - cue_pos),
                )
                contracts.append(BenchmarkContract(
                    surface=rel,
                    command=command,
                    figure=figure_match.group(1),
                    context=reader[:500],
                ))
    return contracts


def validate_benchmark_command(argv: tuple[str, ...], root: Path = REPO) -> str | None:
    """Return a reason when a published command is unsafe or not local."""
    if len(argv) < 2 or argv[0] != "python3":
        return "command must begin with `python3`"
    script = Path(argv[1])
    if (script.is_absolute() or ".." in script.parts
            or script.suffix != ".py" or not script.parts
            or script.parts[0] != "benchmarks"):
        return "only repository-relative Python scripts under benchmarks/ may run"
    if not (root / script).is_file():
        return f"script does not exist: {argv[1]}"
    for token in argv[2:]:
        if (any(ch in token for ch in "|;&><`$\n\r")
                or Path(token).is_absolute() or ".." in Path(token).parts):
            return f"unsafe argument refused: {token!r}"
    return None


def benchmark_primary_result_has_figure(
        argv: tuple[str, ...], figure: str, output: str) -> bool:
    """Match a figure to the command's primary result, not any breakdown row."""
    escaped = re.escape(figure)
    script = argv[1] if len(argv) > 1 else ""
    if script == "benchmarks/label.py" and "score" in argv[2:]:
        if "--corpus" in argv:
            corpus_index = argv.index("--corpus") + 1
            if corpus_index < len(argv) and argv[corpus_index] == "random":
                return bool(re.search(
                    rf"(?m)^Headline:\s*{escaped}\s+precision\b", output))
        return bool(re.search(
            rf"(?m)^Precision:\s*{escaped}\s*\(measured\)\s*$", output))
    if script == "benchmarks/synthetic/run.py":
        return bool(re.search(rf"\bprecision\s*=\s*{escaped}(?![\d.])", output))
    return normalise(figure) in normalise(output)


def _copy_tracked_checkout(destination: Path, root: Path = REPO) -> None:
    """Copy the current contents of every tracked file into an isolated tree."""
    listed = subprocess.run(
        ["git", "ls-files", "-z"], cwd=root, capture_output=True,
        check=True,
    ).stdout.decode("utf-8", errors="surrogateescape")
    for rel in filter(None, listed.split("\0")):
        source = root / rel
        if not source.is_file():
            continue
        target = destination / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


BenchmarkRunner = Callable[[tuple[str, ...]], tuple[str, int]]


def verify_benchmark_contracts(
        contracts: list[BenchmarkContract],
        runner: BenchmarkRunner | None = None,
        root: Path = REPO) -> list[str]:
    """Execute discovered contracts and return every reproducibility defect."""
    problems = []
    grouped: dict[tuple[str, str, str], set[tuple[str, ...]]] = {}
    for contract in contracts:
        key = (contract.surface, contract.context, contract.figure)
        grouped.setdefault(key, set()).add(contract.command)
    for (surface, _context, figure), commands in grouped.items():
        if len(commands) > 1:
            rendered = ", ".join(f"`{' '.join(c)}`" for c in sorted(commands))
            problems.append(
                f"{surface}: one prose block binds {figure} to several commands "
                f"({rendered}); split the claims so each result has one "
                f"unambiguous reproduction instruction.")
    for contract in contracts:
        reason = validate_benchmark_command(contract.command, root)
        if reason:
            problems.append(
                f"{contract.surface}: `{' '.join(contract.command)}` cannot run: "
                f"{reason}")
    if problems:
        return problems

    outputs: dict[tuple[str, ...], tuple[str, int]] = {}
    if runner is not None:
        for command in {contract.command for contract in contracts}:
            outputs[command] = runner(command)
    else:
        with tempfile.TemporaryDirectory(prefix="regula-benchmark-checkout-") as tmp:
            checkout = Path(tmp) / "repo"
            _copy_tracked_checkout(checkout, root)
            env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1",
                       REGULA_CACHE_DIR=str(Path(tmp) / "cache"))
            for command in {contract.command for contract in contracts}:
                run = subprocess.run(
                    [sys.executable, *command[1:]], cwd=checkout,
                    capture_output=True, text=True, check=False, timeout=180,
                    env=env,
                )
                outputs[command] = (run.stdout + run.stderr, run.returncode)

    for contract in contracts:
        output, returncode = outputs[contract.command]
        printable = " ".join(contract.command)
        if returncode:
            tail = normalise(output)[-300:]
            problems.append(
                f"{contract.surface}: `{printable}` exited {returncode}; "
                f"published reproduction instructions must run from a clean "
                f"checkout. Output: {tail!r}")
            continue
        if not benchmark_primary_result_has_figure(
                contract.command, contract.figure, output):
            problems.append(
                f"{contract.surface}: the prose binds {contract.figure} to "
                f"`{printable}`, but that is not the command's primary result. "
                f"A secondary breakdown containing the same number does not "
                f"reproduce the claim.")
    return problems


def verify_published_benchmarks(
        inventory_path: Path = PUBLIC_SURFACE_INVENTORY,
        root: Path = REPO,
        runner: BenchmarkRunner | None = None) -> tuple[list[str], int]:
    contracts = discover_benchmark_contracts(inventory_path, root)
    return verify_benchmark_contracts(contracts, runner, root), len(contracts)


def tracked_surfaces() -> list[str]:
    """Published, human-readable tracked files, enumerated from git.

    Untracked files are not surfaces (measurement rule 4b), and the list comes
    from `git ls-files` rather than a glob so a completeness claim about
    coverage is produced by enumeration (rule 4c).
    """
    run = subprocess.run(["git", "ls-files"], cwd=REPO,
                         capture_output=True, text=True, check=True)
    return [rel for rel in run.stdout.split()
            if rel.endswith(SURFACE_SUFFIXES)
            and not rel.startswith(MARKER_SCAN_EXCLUDED_PREFIXES)]


def retired_marker_hits() -> list[str]:
    """Every published surface still showing output the CLI cannot produce."""
    hits = []
    for rel in tracked_surfaces():
        try:
            body = surface_text(REPO / rel)
        except SvgTextError as exc:
            hits.append(f"{rel}: cannot be read, so its content is unknown ({exc})")
            continue
        for marker, why in RETIRED_MARKERS.items():
            if normalise(marker) in body:
                hits.append(f"{rel}: shows {marker!r} ({why})")
        for pattern, why in RETIRED_MARKER_PATTERNS.items():
            found = re.search(pattern, body)
            if found:
                hits.append(f"{rel}: shows {found.group(0)!r} ({why})")
    return hits


def unqualified_output_hits() -> list[str]:
    """Every published surface showing current output stripped of its qualifier.

    The window is measured BACKWARDS from the match, because the tool prints the
    qualifier above the line it qualifies and a reader meets it first. 400
    characters is wide enough to span a whole `Decision:` block, which is the
    largest thing that legitimately sits between them in real output, and narrow
    enough that a caveat in a different section of a page cannot vouch for a
    transcript further down.
    """
    hits = []
    for rel in tracked_surfaces():
        try:
            body = surface_text(REPO / rel)
        except SvgTextError as exc:
            hits.append(f"{rel}: cannot be read, so its content is unknown ({exc})")
            continue
        for name, rule in QUALIFIED_OUTPUT.items():
            for found in rule["pattern"].finditer(body):
                before = body[max(0, found.start() - rule["window"]):found.start()]
                if any(q.lower() in before.lower() for q in rule["qualifiers"]):
                    continue
                shown = body[found.start():found.start() + 90].split("  ")[0]
                hits.append(
                    f"{rel}: publishes {shown.strip()!r} with no qualifier "
                    f"within {rule['window']} characters before it ({name}: "
                    f"{rule['why']})")
    return hits


def qualified_output_is_really_emitted() -> list[str]:
    """Positive proof that each rule describes output the tool actually prints.

    Without this the rules above are an author's preference. With it, a rule
    whose pattern the CLI never emits, or whose qualifier the CLI has stopped
    printing, fails here instead of quietly policing a shape that no longer
    exists. This is the same discipline `retired_markers_are_unreachable`
    applies in the opposite direction.
    """
    problems = []
    for name, rule in QUALIFIED_OUTPUT.items():
        output, _rc = run_command(rule["proof_command"])
        shown = normalise(output)
        printable = "regula " + " ".join(rule["proof_command"])
        found = rule["pattern"].search(shown)
        if not found:
            problems.append(
                f"{name}: `{printable}` does not emit the pattern this rule "
                f"polices, so the rule describes nothing the tool produces. "
                f"Remove the rule rather than keeping a check that cannot fire.")
            continue
        before = shown[max(0, found.start() - rule["window"]):found.start()]
        if not any(q.lower() in before.lower() for q in rule["qualifiers"]):
            problems.append(
                f"{name}: `{printable}` emits {found.group(0).strip()!r} but none "
                f"of its declared qualifiers appears within {rule['window']} "
                f"characters before it. The tool's own output would fail this "
                f"rule, so the rule is wrong, not the pages.")
    return problems


def retired_markers_are_unreachable(commands: list[list[str]] | None = None,
                                    cli: list[str] | None = None,
                                    cwd: str | Path | None = None,
                                    ) -> list[str]:
    """Positive proof that each marker really is retired.

    Without this the list above is an assertion. With it, a marker that the CLI
    starts emitting again fails the suite instead of silently forbidding
    wording the tool now produces.

    `cli`/`cwd` decide WHICH artefact is proved. Run against this tree the
    answer has always been yes; run against the published 1.9.0 wheel it is no,
    and nothing in this repository could say so until the parameter existed
    (N144).
    """
    commands = commands or [
        ["check", "examples/cv-screening-app"],
        ["check", "examples/cv-screening-app", "--scope", "all", "--domain", "employment"],
        ["check", "examples/customer-chatbot", "--scope", "all"],
        ["gap", "--project", "examples/cv-screening-app"],
    ]
    problems = []
    for argv in commands:
        output, _rc = run_command(argv, cli=cli, cwd=cwd)
        shown = normalise(output)
        for marker in RETIRED_MARKERS:
            if normalise(marker) in shown:
                problems.append(
                    f"`regula {' '.join(argv)}` emits {marker!r}, which "
                    f"RETIRED_MARKERS claims is retired. Remove it from that "
                    f"list rather than editing the pages that show it.")
        for pattern in RETIRED_MARKER_PATTERNS:
            found = re.search(pattern, shown)
            if found:
                problems.append(
                    f"`regula {' '.join(argv)}` emits {found.group(0)!r}, which "
                    f"RETIRED_MARKER_PATTERNS claims is retired.")
    return problems


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--list", action="store_true",
                    help="print the covered surfaces and commands, verify nothing")
    args = ap.parse_args(argv)

    if args.list:
        for entry in load_manifest():
            print(f"{entry['surface']}\n    regula {' '.join(entry['command'])}"
                  f"  ({len(entry['anchors'])} anchor(s))")
        for contract in discover_benchmark_contracts():
            print(f"{contract.surface}\n    {' '.join(contract.command)}"
                  f"  (primary result: {contract.figure})")
        return 0

    problems, checked = verify()
    benchmark_contracts = discover_benchmark_contracts()
    benchmark_checked = len(benchmark_contracts)
    benchmark_problems = verify_benchmark_contracts(benchmark_contracts)
    problems += benchmark_problems
    problems += retired_marker_hits()
    problems += retired_markers_are_unreachable()
    problems += unqualified_output_hits()
    problems += qualified_output_is_really_emitted()
    if not checked:
        print("transcript-check: FAIL — no anchors were checked, so this gate "
              "proved nothing. Either the manifest is empty or it stopped "
              "being read.", file=sys.stderr)
        return 1
    if not benchmark_checked:
        print("transcript-check: FAIL - no published benchmark contracts were "
              "checked, so benchmark reproducibility proved nothing.",
              file=sys.stderr)
        return 1
    if problems:
        print(f"transcript-check: FAIL - {len(problems)} problem(s) across "
              f"{checked} CLI anchor(s) and {benchmark_checked} benchmark "
              "contract(s):", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1
    covered_surfaces = {
        entry["surface"] for entry in load_manifest()
    } | {contract.surface for contract in benchmark_contracts}
    print(f"transcript-check: {checked} CLI anchor(s) and "
          f"{benchmark_checked} benchmark contract(s) across "
          f"{len(covered_surfaces)} surface(s); every published transcript "
          f"and benchmark result reproduces from the command its page documents")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
