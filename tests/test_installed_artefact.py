"""The guards must be able to answer for an INSTALLED artefact, not only the tree.

the prior audit: `regula-ai` 1.9.0 on PyPI prints a compliance score out of 100, a
verdict and a risk tier. Three of those strings are in this tree's
`RETIRED_MARKERS`, and `retired_markers_are_unreachable()` proves them
unreachable — about the tree. Nothing in this repository could ask the question
about the artefact, so the published product carried the one claim this project
forbids and every local gate stayed green.

the prior audit's sibling in packaging: v1.7.6 shipped `regula dpv` broken because a
data file was not in the wheel, and source tests do not catch packaging bugs.
Found again on 2026-08-17: `scripts/dashboard/index.html` was read by
`regula api-server` and named by no packaging pattern, so the installed product
answered `/v1/dashboard` with a JSON message telling the user to write a file
into site-packages.

These checks exercise the real predicates in `scripts/verify_installed_artefact.py`
against synthetic artefact roots. They deliberately do NOT build a wheel: a
ten-second build inside the suite would be the slowest test in the file and would
still only prove what the configuration already says. The build itself is run in
the release path and its result is recorded in the session record.

Written as module-level functions rather than as a TestCase, because the custom
runner binds by scanning `dir(module)` and a class-based module exposes only
class names. That is the trap N134 recorded and N129's and N134's own modules
fell into.
"""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import determination_guard as dg
import verify_installed_artefact as via
import verify_transcripts as vt

REPO = Path(__file__).resolve().parent.parent

# A determination the guard must fire on, assembled rather than written whole so
# this module is not itself a corpus of the claim it forbids.
_PLANTED_DETERMINATION = 'message = "' + "compl" + 'iant"'


def _artefact(tmp: Path, files: dict[str, str], dist="regula_ai-1.9.0") -> Path:
    """A minimal installed artefact: real files plus the RECORD that names them."""
    root = tmp
    lines = []
    for rel, text in files.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
        lines.append(f"{rel},,")
    info = root / f"{dist}.dist-info"
    info.mkdir(parents=True, exist_ok=True)
    (info / "RECORD").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return root


# --------------------------------------------------------------------------
# The packaging configuration, read rather than restated
# --------------------------------------------------------------------------

def test_the_required_data_register_is_not_stale():
    """An entry naming a file this tree does not have has outlived its premise.

    Same discipline as N123's `not_a_count_claim` and the quarantine burn-downs:
    an exclusion or a requirement that matches nothing is a defect, not a saving.
    """
    missing = [rel for rel in via.REQUIRED_PACKAGED_DATA if not (REPO / rel).exists()]
    assert missing == [], (
        f"REQUIRED_PACKAGED_DATA names files absent from the tree: {missing}")


def test_every_required_runtime_data_file_is_covered_by_a_packaging_pattern():
    """The check that was red before 2026-08-17 and is green after.

    Fail-before is on record: with `dashboard/*.html` absent from
    `[tool.setuptools.package-data]`, a wheel built from this tree omitted
    `scripts/dashboard/index.html`, and `regula api-server` served 302 bytes of
    JSON where the tree served 52,443 bytes of HTML.
    """
    uncovered = via.uncovered_required_data()
    assert uncovered == [], (
        "a wheel built from this pyproject.toml would omit required runtime "
        f"data: {uncovered}")


def test_the_packaging_coverage_check_can_fail():
    """Control: remove the pattern and the predicate must name the file.

    Without this the assertion above could pass because the predicate answers
    True for everything, which is measurement rule 4's blank gate.
    """
    real = via._package_data()
    assert via.package_data_covers("scripts/dashboard/index.html", real) is True

    neutered = {k: [p for p in v if p != "dashboard/*.html"] for k, v in real.items()}
    assert via.package_data_covers("scripts/dashboard/index.html", neutered) is False
    assert "scripts/dashboard/index.html" in via.uncovered_required_data(neutered)


def test_every_conformance_shard_is_covered_by_a_packaging_pattern():
    real = via._package_data()
    assert via.CONFORMANCE_SHARDS
    assert all(via.package_data_covers(rel, real)
               for rel in via.CONFORMANCE_SHARDS)

    neutered = {
        key: [pattern for pattern in patterns
              if pattern != "decision_conformance.v1/*.json"]
        for key, patterns in real.items()
    }
    assert all(not via.package_data_covers(rel, neutered)
               for rel in via.CONFORMANCE_SHARDS)


def test_the_installed_conformance_bundle_is_complete_and_integrity_bound():
    with tempfile.TemporaryDirectory(prefix="regula-conformance-install-") as tmp:
        root = Path(tmp)
        required = (via.CONFORMANCE_MANIFEST,) + via.CONFORMANCE_SHARDS
        for relative in required:
            source = REPO / relative
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(source.read_bytes())

        problems, count = via.check_conformance_bundle(root)
        assert problems == []
        assert count == len(via.CONFORMANCE_SHARDS) + 1

        damaged = root / via.CONFORMANCE_SHARDS[0]
        damaged.write_bytes(damaged.read_bytes() + b"\n")
        problems, _ = via.check_conformance_bundle(root)
        assert any("byte count" in problem for problem in problems)
        assert any("SHA-256" in problem for problem in problems)


def test_a_packaging_pattern_does_not_match_across_a_directory_separator():
    """`*` is a glob, not a regex. `bias_data/*.json` must not cover a nested file."""
    pd = {"scripts": ["bias_data/*.json"]}
    assert via.package_data_covers("scripts/bias_data/x.json", pd) is True
    assert via.package_data_covers("scripts/bias_data/nested/x.json", pd) is False
    assert via.package_data_covers("scripts/other/x.json", pd) is False


# --------------------------------------------------------------------------
# The determination guard, pointed at an artefact
# --------------------------------------------------------------------------

def test_the_artefact_scan_fires_on_a_determination_inside_an_installed_package():
    with tempfile.TemporaryDirectory(prefix="regula-artefact-test-") as tmp:
        root = _artefact(Path(tmp), {
            "scripts/cli_report.py": f"def badge():\n    {_PLANTED_DETERMINATION}\n",
            "scripts/clean.py": "def ok():\n    return 'indicator count'\n",
        })
        files = dg.artefact_files(root)
        scoped = [f for f in files if dg.artefact_in_scope(f)]
        findings = []
        for rel in scoped:
            findings.extend(dg.scan_file(rel, root=root))
        assert len(files) == 2, files
        assert len(scoped) == 2, scoped
        assert [f["file"] for f in findings] == ["scripts/cli_report.py"], findings


def test_the_artefact_scan_is_silent_on_a_clean_artefact():
    """The other direction, so the check above cannot pass by firing on everything."""
    with tempfile.TemporaryDirectory(prefix="regula-artefact-test-") as tmp:
        root = _artefact(Path(tmp), {
            "scripts/clean.py": "def ok():\n    return 'indicator count'\n",
            "scripts/also_clean.md": "This tool does not determine compliance.\n",
        })
        findings = []
        for rel in dg.artefact_files(root):
            if dg.artefact_in_scope(rel):
                findings.extend(dg.scan_file(rel, root=root))
        assert findings == [], findings


def test_the_artefact_scan_excludes_only_the_guards_own_source():
    """The one exclusion that must survive into an artefact scan, and no other.

    `EXCLUDED_PREFIXES` names repository paths that do not exist inside a wheel.
    Honouring them there would look like coverage and do nothing.
    """
    assert dg.artefact_in_scope("scripts/determination_guard.py") is False
    assert dg.artefact_in_scope("scripts/cli_report.py") is True
    # A repository-only historical exclusion must NOT be honoured inside an
    # installed artefact.
    assert dg.in_scope("CHANGELOG.md") is False
    assert dg.artefact_in_scope("CHANGELOG.md") is True


def test_the_artefact_scan_fails_closed_rather_than_reporting_clean():
    """Rule 4: a check that could not run is not a check that passed."""
    with tempfile.TemporaryDirectory(prefix="regula-artefact-test-") as tmp:
        empty = Path(tmp) / "nothing-here"
        empty.mkdir()
        try:
            dg.artefact_files(empty)
        except RuntimeError as exc:
            assert "RECORD" in str(exc), exc
        else:
            raise AssertionError("a root with no RECORD returned a corpus")

        missing = Path(tmp) / "absent"
        try:
            dg.artefact_files(missing)
        except RuntimeError as exc:
            assert "not a directory" in str(exc), exc
        else:
            raise AssertionError("a missing root returned a corpus")


def test_a_record_naming_a_file_that_is_not_there_is_refused():
    with tempfile.TemporaryDirectory(prefix="regula-artefact-test-") as tmp:
        root = _artefact(Path(tmp), {"scripts/clean.py": "x = 1\n"})
        (root / "regula_ai-1.9.0.dist-info" / "RECORD").write_text(
            "scripts/clean.py,,\nscripts/never_written.py,,\n", encoding="utf-8")
        try:
            dg.artefact_files(root)
        except RuntimeError as exc:
            assert "never_written" in str(exc), exc
        else:
            raise AssertionError("a RECORD naming an absent file was accepted")


# --------------------------------------------------------------------------
# The data check, and the CLI target
# --------------------------------------------------------------------------

def test_the_data_check_names_a_required_file_the_install_lacks():
    with tempfile.TemporaryDirectory(prefix="regula-artefact-test-") as tmp:
        root = Path(tmp)
        for rel in via.REQUIRED_PACKAGED_DATA:
            if rel == "scripts/dashboard/index.html":
                continue
            p = root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("{}", encoding="utf-8")
        problems, n = via.check_data(root)
        assert n == len(via.REQUIRED_PACKAGED_DATA)
        assert len(problems) == 1, problems
        assert "scripts/dashboard/index.html" in problems[0]

        (root / "scripts" / "dashboard").mkdir(parents=True, exist_ok=True)
        (root / "scripts" / "dashboard" / "index.html").write_text("<html>", encoding="utf-8")
        problems, _ = via.check_data(root)
        assert problems == [], problems


def test_the_retired_marker_check_can_be_pointed_at_another_cli():
    """The parameter N144 needed, exercised in both directions.

    A stub CLI that emits a retired marker must be caught; one that emits the
    current wording must not. Without this the `cli=` argument could be accepted
    and ignored, which is exactly how N112's first fix was inert: an environment
    variable was assumed honoured and never measured.
    """
    marker = "Verdict" + ": " + "HIGH-RISK"
    with tempfile.TemporaryDirectory(prefix="regula-cli-stub-") as tmp:
        work = Path(tmp)
        loud = work / "loud.py"
        loud.write_text(f"print({marker!r})\n", encoding="utf-8")
        quiet = work / "quiet.py"
        quiet.write_text("print('Decision: insufficient_information')\n", encoding="utf-8")

        problems = vt.retired_markers_are_unreachable(
            [["ignored"]], cli=[sys.executable, str(loud)], cwd=work)
        assert len(problems) == 1, problems
        assert marker in problems[0]

        problems = vt.retired_markers_are_unreachable(
            [["ignored"]], cli=[sys.executable, str(quiet)], cwd=work)
        assert problems == [], problems


def test_the_default_cli_target_is_still_this_tree():
    """Making the target a parameter must not have moved the default."""
    assert vt.TREE_CLI == [sys.executable, "-m", "scripts.cli"]


# --------------------------------------------------------------------------
# The module closure, computed rather than listed
# --------------------------------------------------------------------------

def test_the_import_closure_is_computed_and_reaches_the_kernel():
    """Non-vacuity: the closure must actually contain the modules at issue.

    A closure that silently returned its own roots would report every artefact
    complete, which is the shape N144 already cost this project once.
    """
    closure = via.import_closure(REPO)
    assert "decision_kernel" in closure
    assert "decision_adapters" in closure
    assert "cli" in closure
    assert len(closure) > 20, f"closure implausibly small: {closure}"


def test_the_module_check_names_a_module_the_artefact_lacks():
    with tempfile.TemporaryDirectory(prefix="regula-artefact-test-") as tmp:
        root = Path(tmp)
        (root / "scripts").mkdir(parents=True)
        for module in via.import_closure(REPO):
            if module == "decision_kernel":
                continue
            (root / "scripts" / f"{module}.py").write_text("", encoding="utf-8")
        problems, n = via.check_modules(root)
        assert n == len(via.import_closure(REPO))
        assert len(problems) == 1, problems
        assert "decision_kernel" in problems[0]

        (root / "scripts" / "decision_kernel.py").write_text("", encoding="utf-8")
        problems, _ = via.check_modules(root)
        assert problems == [], problems


def test_the_module_check_computes_its_closure_from_the_tree_not_the_artefact():
    """Otherwise a missing module shrinks the closure to fit the defect.

    An artefact holding one module would report a closure of one and pass.
    """
    with tempfile.TemporaryDirectory(prefix="regula-artefact-test-") as tmp:
        root = Path(tmp)
        (root / "scripts").mkdir(parents=True)
        (root / "scripts" / "cli.py").write_text("", encoding="utf-8")
        problems, n = via.check_modules(root)
        assert n == len(via.import_closure(REPO)), n
        assert len(problems) == n - 1, (n, len(problems))


if __name__ == "__main__":                                     # pragma: no cover
    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"PASS {name}")
            except Exception as exc:                           # noqa: BLE001
                failures += 1
                print(f"FAIL {name}: {exc}")
    print(f"{failures} failure(s)")
    raise SystemExit(1 if failures else 0)
