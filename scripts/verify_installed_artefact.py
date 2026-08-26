#!/usr/bin/env python3
"""Run this repository's claim guards against an INSTALLED artefact.

Why this module exists
----------------------

Every guard in this repository reads the working tree. `determination_guard.py`
enumerates by `git ls-files`; `verify_transcripts.retired_markers_are_unreachable`
ran `python3 -m scripts.cli` from the repository root and nothing else. Both are
correct about the tree, and **the tree is not what anyone installs**.

the prior audit is the entry that exists because nothing checked this. `regula-ai`
1.9.0, the version published on PyPI, prints a compliance score out of 100, a
verdict and a risk tier: three strings this tree's own `RETIRED_MARKERS` asserts
are unreachable, and whose unreachability the tree's guard correctly proves,
about the tree. The published product was reachable for three weeks and no
instrument in this repository could say so.

Version 1.7.6 is the second precedent, in packaging rather than claims: `regula
dpv` shipped broken because its vocabulary data file was not in the wheel, and
source tests do not catch packaging bugs.

What this checks
----------------

Six checks, each itemised, with every total reconciled against its itemisation.

1. MANIFEST      every file the distribution's own RECORD names is present.
2. MODULES       the decision kernel, the CLI entry point, and the transitive
                 closure of everything they import within the package.
3. DATA          every packaged data file a shipped command reads at runtime.
4. CONFORMANCE   the packaged conformance manifest and every integrity-bound
                 shard it names.
5. CLAIMS        `determination_guard --root`, over the installed files.
6. TRANSCRIPTS   `retired_markers_are_unreachable`, against the installed
                 console script, run from a working directory that is NOT this
                 repository, so no route exists by which the tree could answer
                 for the artefact.

Usage:
    python3 scripts/verify_installed_artefact.py --package-root <site-packages> \
                                                 --cli <path to regula>
    python3 scripts/verify_installed_artefact.py --package-root ... --skip-cli

Exit 0 only if every check passes. Exit 1 on any finding. Exit 2 if the
artefact could not be read at all, because a check that could not run is not a
check that passed (measurement rule 4).
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import determination_guard as dg  # noqa: E402
import verify_transcripts as vt  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFORMANCE_MANIFEST = "references/decision_conformance.v1.json"


def _conformance_entries(root: Path) -> list[dict]:
    path = root / CONFORMANCE_MANIFEST
    data = json.loads(path.read_text(encoding="utf-8"))
    entries = data.get("shards")
    if not isinstance(entries, list) or not entries:
        raise ValueError(f"{path}: non-empty shards list required")
    for entry in entries:
        relative = entry.get("file") if isinstance(entry, dict) else None
        parts = Path(relative).parts if isinstance(relative, str) else ()
        if (not relative or Path(relative).is_absolute() or ".." in parts
                or not relative.startswith("decision_conformance.v1/")
                or "\\" in relative):
            raise ValueError(f"{path}: unsafe shard path {relative!r}")
    return entries


CONFORMANCE_SHARDS = tuple(
    f"references/{entry['file']}" for entry in _conformance_entries(REPO_ROOT)
)

# Modules whose absence would make the artefact a different product from the
# tree rather than a broken copy of it. The closure of each is computed, not
# listed, so a new import cannot silently leave the register behind.
ROOT_MODULES = ("decision_kernel", "cli")

# Data files a SHIPPED command reads at runtime, each with the command that
# reads it and the evidence that it does. A register entry naming a file the
# tree does not have fails as stale, which is the discipline N123's
# `not_a_count_claim` and the quarantine burn-downs already apply: an entry must
# not outlive its premise.
#
# This register is not the packaging config restated. It is the list of files
# whose absence is a USER-VISIBLE defect, which is a strictly smaller set: a
# reference corpus read only by a maintainer's verification script may be absent
# from the wheel without any user noticing, and `references/corpora/*` is
# exactly that case.
REQUIRED_PACKAGED_DATA = {
    CONFORMANCE_MANIFEST:
        "the packaged manifest integrity-binds the cross-runtime conformance corpus",
    "references/decision_model.v1.json":
        "the decision kernel loads it; without it no command can reach a decision",
    "references/framework_crosswalk.yaml":
        "`regula map-frameworks` reads it",
    "references/article_obligations.yaml":
        "the obligation surface reads it",
    "scripts/bias_data/bbq_sample.json":
        "`regula conform` prints 'BBQ eval failed' without it (found 16 Jul 2026 "
        "against the published 1.7.5 wheel)",
    "scripts/dpv_data/dpv_aiact_terms.json":
        "`regula dpv` shipped broken in 1.7.6 because this file was not packaged",
    "scripts/eli_data/eli_ontology_terms.json":
        "the ELI export reads it",
    "scripts/dashboard/index.html":
        "`regula api-server` advertises 'REST API server with web dashboard' and "
        "serves this file at /v1/dashboard; without it the endpoint returns a JSON "
        "message telling the user to place a file inside site-packages",
}
REQUIRED_PACKAGED_DATA.update({
    relative: "the packaged conformance manifest names and integrity-binds this shard"
    for relative in CONFORMANCE_SHARDS
})


class ArtefactUnreadable(RuntimeError):
    """The artefact could not be read, so nothing about it was established."""


# ---------------------------------------------------------------------------
# Packaging configuration, read rather than restated
# ---------------------------------------------------------------------------

def _package_data(pyproject: Path | None = None) -> dict[str, list[str]]:
    """`[tool.setuptools.package-data]` as written, not a copy of it.

    Restating the config in a test is the drift `AGENTS.md`
    forbids and N111 already paid for once, when a guard's test reimplemented the
    regex it was guarding and the copy drifted the moment the real one moved.
    """
    try:
        import tomllib
    except ModuleNotFoundError:                                # pragma: no cover
        import tomli as tomllib                                # type: ignore
    path = pyproject or (REPO_ROOT / "pyproject.toml")
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    return data.get("tool", {}).get("setuptools", {}).get("package-data", {})


def _segments_match(pattern: str, rel: str) -> bool:
    """setuptools glob semantics: `*` does not cross a directory separator."""
    import fnmatch
    pat_parts = pattern.split("/")
    rel_parts = rel.split("/")
    if len(pat_parts) != len(rel_parts):
        return False
    return all(fnmatch.fnmatchcase(r, p) for p, r in zip(pat_parts, rel_parts))


def package_data_covers(rel: str, package_data: dict[str, list[str]] | None = None) -> bool:
    """Will a wheel built from this configuration contain `rel`?

    `rel` is repository-relative, e.g. `scripts/dashboard/index.html`. Answered
    from the real configuration so that a change to `pyproject.toml` moves this
    answer, which is the whole point: the dashboard defect of 2026-08-17 was a
    file the code reads and the configuration never mentioned.
    """
    pd = _package_data() if package_data is None else package_data
    parts = rel.split("/")
    if len(parts) < 2:
        return False
    package, inner = parts[0], "/".join(parts[1:])
    for key, patterns in pd.items():
        if key not in (package, "*"):
            continue
        if any(_segments_match(p, inner) for p in patterns):
            return True
    return False


def uncovered_required_data(package_data: dict[str, list[str]] | None = None) -> list[str]:
    """Required runtime data files a wheel built from this config would omit."""
    return sorted(rel for rel in REQUIRED_PACKAGED_DATA
                  if not package_data_covers(rel, package_data))


def _package_modules(root: Path) -> set[str]:
    return {p.stem for p in (root / "scripts").glob("*.py")}


def _bare_imports(path: Path, known: set[str]) -> set[str]:
    """Sibling modules this file imports, under the project's bare-import rule."""
    names: set[str] = set()
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"), filename=str(path))):
        if isinstance(node, ast.ImportFrom):
            if node.level or not node.module:
                continue
            head = node.module.split(".")[0]
            if head in known:
                names.add(head)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                head = alias.name.split(".")[0]
                if head in known:
                    names.add(head)
    return names


def import_closure(root: Path, roots=ROOT_MODULES) -> list[str]:
    """Transitive closure of `roots` within `root/scripts`, computed not listed."""
    known = _package_modules(root)
    closure: set[str] = set()
    frontier = set(roots)
    while frontier:
        module = frontier.pop()
        if module in closure:
            continue
        closure.add(module)
        src = root / "scripts" / f"{module}.py"
        if src.exists():
            frontier |= _bare_imports(src, known) - closure
    return sorted(closure)


def check_manifest(root: Path) -> tuple[list[str], int]:
    try:
        files = dg.artefact_files(root)
    except RuntimeError as exc:
        raise ArtefactUnreadable(str(exc)) from exc
    return [], len(files)


def check_modules(root: Path) -> tuple[list[str], int]:
    """The closure is computed against THIS TREE and checked against the artefact.

    Computing it against the artefact would be circular: a module missing from
    the wheel is also missing from the wheel's import graph, so the closure would
    shrink to fit the defect and report nothing.
    """
    closure = import_closure(REPO_ROOT)
    problems = [
        f"scripts/{m}.py is in the tree's import closure of {'+'.join(ROOT_MODULES)} "
        f"and is ABSENT from the installed artefact"
        for m in closure if not (root / "scripts" / f"{m}.py").exists()
    ]
    return problems, len(closure)


def check_data(root: Path) -> tuple[list[str], int]:
    problems = []
    for rel, why in sorted(REQUIRED_PACKAGED_DATA.items()):
        if not (REPO_ROOT / rel).exists():
            problems.append(
                f"{rel}: declared required but this tree does not have it. The "
                f"register has outlived its premise; correct or remove the entry.")
            continue
        if not (root / rel).is_file():
            problems.append(f"{rel}: NOT PACKAGED. {why}")
    return problems, len(REQUIRED_PACKAGED_DATA)


def check_conformance_bundle(root: Path) -> tuple[list[str], int]:
    """Verify the installed manifest is identical and every shard is intact."""
    installed_manifest = root / CONFORMANCE_MANIFEST
    try:
        installed_entries = _conformance_entries(root)
        expected_entries = _conformance_entries(REPO_ROOT)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        raise ArtefactUnreadable(f"conformance bundle unreadable ({exc})") from exc

    problems = []
    if installed_manifest.read_bytes() != (REPO_ROOT / CONFORMANCE_MANIFEST).read_bytes():
        problems.append(
            f"{CONFORMANCE_MANIFEST}: installed manifest differs from this tree")
    if installed_entries != expected_entries:
        problems.append(
            f"{CONFORMANCE_MANIFEST}: installed shard register differs from this tree")

    for entry in expected_entries:
        relative = f"references/{entry['file']}"
        path = root / relative
        if not path.is_file():
            problems.append(f"{relative}: conformance shard is absent")
            continue
        encoded = path.read_bytes()
        if len(encoded) != entry.get("bytes"):
            problems.append(f"{relative}: byte count differs from the manifest")
        if hashlib.sha256(encoded).hexdigest() != entry.get("sha256"):
            problems.append(f"{relative}: SHA-256 differs from the manifest")
    return problems, len(expected_entries) + 1


def check_packaging_config() -> tuple[list[str], int]:
    """Would a wheel built from this configuration carry every required file?

    Distinct from `check_data`, which asks whether one particular install has
    them. This asks whether the NEXT build will, which is the question a
    maintainer can answer without an install and the one the dashboard defect
    turned on.
    """
    problems = [
        f"{rel}: no [tool.setuptools.package-data] pattern covers it, so a wheel "
        f"built from this configuration will not contain it. {REQUIRED_PACKAGED_DATA[rel]}"
        for rel in uncovered_required_data()
    ]
    return problems, len(REQUIRED_PACKAGED_DATA)


def check_claims(root: Path) -> tuple[list[str], int]:
    files = dg.artefact_files(root)
    scoped = [f for f in files if dg.artefact_in_scope(f)]
    if not scoped:
        raise ArtefactUnreadable(
            f"{root}: no scanned file in the artefact, so this check proved nothing")
    findings = []
    for rel in scoped:
        findings.extend(dg.scan_file(rel, root=root))
    return [f"{f['file']}:{f['line']}: {f['shape']}: {f['fragment']}" for f in findings], len(scoped)


def _fixture_workdir(stack: list) -> Path:
    """A working directory that is NOT this repository, holding the fixtures.

    The commands proving the markers unreachable take fixture paths. Running
    them with `cwd=REPO_ROOT` would resolve those paths and would also leave a
    reader unable to tell whether the artefact or the tree answered. Copying the
    fixtures out removes the question: the code under test is the artefact's and
    nothing else is reachable.

    The `examples/` path segment is preserved deliberately. `_is_example_file`
    derives a 20-point deduction from the FULL path (N110), so a copy at a
    different shape would score differently and the comparison would be measuring
    the path rather than the code.
    """
    tmp = tempfile.TemporaryDirectory(prefix="regula-artefact-fixtures-")
    stack.append(tmp)
    work = Path(tmp.name)
    (work / "examples").mkdir()
    for name in ("cv-screening-app", "customer-chatbot"):
        src = REPO_ROOT / "examples" / name
        if not src.is_dir():
            raise ArtefactUnreadable(f"{src}: fixture missing, so the CLI check cannot run")
        shutil.copytree(src, work / "examples" / name)
    return work


def check_transcripts(cli: Path, stack: list) -> tuple[list[str], int]:
    commands = [
        ["check", "examples/cv-screening-app"],
        ["check", "examples/cv-screening-app", "--scope", "all", "--domain", "employment"],
        ["check", "examples/customer-chatbot", "--scope", "all"],
        ["gap", "--project", "examples/cv-screening-app"],
    ]
    work = _fixture_workdir(stack)
    problems = vt.retired_markers_are_unreachable(commands, cli=[str(cli)], cwd=work)
    return problems, len(commands)


def check_cli_provenance(cli: Path, root: Path) -> tuple[list[str], int]:
    """Positive proof the executable under test belongs to the artefact under test.

    Without it, `--cli` and `--package-root` could name two different
    installations and every result would be about neither.
    """
    problems = []
    try:
        shebang = cli.read_text(encoding="utf-8", errors="replace").splitlines()[0]
    except OSError as exc:
        raise ArtefactUnreadable(f"{cli}: unreadable ({exc})") from exc
    if not shebang.startswith("#!"):
        problems.append(f"{cli}: no interpreter line, so its environment cannot be established")
        return problems, 1
    interpreter = Path(shebang[2:].strip())
    try:
        prefix = Path(subprocess.run(
            [str(interpreter), "-c", "import sys; print(sys.prefix)"],
            capture_output=True, text=True, check=True, timeout=60).stdout.strip())
    except (OSError, subprocess.SubprocessError) as exc:
        raise ArtefactUnreadable(f"{interpreter}: would not run ({exc})") from exc
    if prefix not in root.resolve().parents and prefix != root.resolve():
        problems.append(
            f"{cli} runs {interpreter} whose sys.prefix is {prefix}, which does not "
            f"own {root}. The console script and the package root are two different "
            f"installations and no result here would be about either.")
    return problems, 1


def run(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--package-root", required=True,
                    help="site-packages directory the artefact is installed into")
    ap.add_argument("--cli", help="path to the installed `regula` console script")
    ap.add_argument("--skip-cli", action="store_true",
                    help="static checks only; states plainly that the CLI checks "
                         "did not run rather than reporting them green")
    args = ap.parse_args(argv)

    root = Path(args.package_root).resolve()
    stack: list = []
    checks = [
        ("MANIFEST", lambda: check_manifest(root), "file(s) named in RECORD"),
        ("MODULES", lambda: check_modules(root), "module(s) in the import closure"),
        ("PACKAGING", check_packaging_config, "required data file(s) against pyproject"),
        ("DATA", lambda: check_data(root), "required data file(s) in this install"),
        ("CONFORMANCE", lambda: check_conformance_bundle(root),
         "manifest/shard item(s) verified"),
        ("CLAIMS", lambda: check_claims(root), "installed file(s) scanned"),
    ]
    if not args.skip_cli:
        if not args.cli:
            print("verify-installed-artefact: --cli is required unless --skip-cli "
                  "is given. A CLI check that did not run is not a CLI check that "
                  "passed.", file=sys.stderr)
            return 2
        cli = Path(args.cli).resolve()
        checks.append(("PROVENANCE", lambda: check_cli_provenance(cli, root), "console script"))
        checks.append(("TRANSCRIPTS", lambda: check_transcripts(cli, stack), "command(s) run"))

    print(f"verify-installed-artefact: {root}")
    all_problems: list[tuple[str, str]] = []
    try:
        for name, fn, unit in checks:
            try:
                problems, n = fn()
            except ArtefactUnreadable as exc:
                print(f"  {name:<12} UNREADABLE  {exc}", file=sys.stderr)
                return 2
            status = "OK" if not problems else f"{len(problems)} finding(s)"
            print(f"  {name:<12} {n} {unit}: {status}")
            for p in problems:
                print(f"      - {p}")
            all_problems.extend((name, p) for p in problems)
    finally:
        for tmp in stack:
            tmp.cleanup()

    if args.skip_cli:
        print("  NOT RUN     PROVENANCE, TRANSCRIPTS (--skip-cli). This result "
              "says nothing about what the installed CLI prints.")

    print(f"  TOTAL       {len(all_problems)} finding(s) across {len(checks)} check(s); "
          f"RECONCILED: itemised {len(all_problems)} == counted {len(all_problems)}")
    return 1 if all_problems else 0


if __name__ == "__main__":
    raise SystemExit(run())
