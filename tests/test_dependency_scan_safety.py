#!/usr/bin/env python3
# regula-ignore
"""Dependency manifests must not be read from outside the scanned project.

issue #32. `scan_dependencies()` read every manifest with a bare
`path.read_text()`, so a symlinked `requirements.txt` pointing outside the
scanned tree was followed and its packages reported. Reproduced against
both `regula deps` and `regula sbom` — the latter reaches the same function
via `sbom.py`, so its own guarded walkers did not protect it.

pytest-only, not registered in tests/test_classification.py.
"""

import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

REPO = Path(__file__).parent.parent
CANARY = "CANARY-PKG-XYZZY"


def _escaping_project(tmp: Path, manifest: str = "requirements.txt"):
    """A project whose <manifest> is a symlink to a file outside it.
    Returns (project_dir, ok) — ok is False if symlinks are unsupported."""
    outside = tmp / "outside"
    outside.mkdir()
    proj = tmp / "proj"
    proj.mkdir()
    (outside / manifest).write_text(f"openai==1.0.0\n{CANARY}==9.9.9\n")
    try:
        (proj / manifest).symlink_to(outside / manifest)
    except (OSError, NotImplementedError):
        return proj, False
    (proj / "real.py").write_text("x = 1")
    return proj, True


def test_escaping_requirements_txt_is_not_read():
    from dependency_scan import scan_dependencies

    with tempfile.TemporaryDirectory() as td:
        proj, ok = _escaping_project(Path(td).resolve())
        if not ok:
            return
        result = scan_dependencies(str(proj))
        names = " ".join(str(d) for d in result.get("all_dependencies", []))
        assert CANARY not in names, f"read a manifest outside the project: {names}"


def test_escaping_manifest_of_every_supported_ecosystem_is_refused():
    """One symlinked manifest per ecosystem — a fix that covers only
    requirements.txt would leave eight other doors open."""
    from dependency_scan import scan_dependencies

    for manifest in ("requirements.txt", "pyproject.toml", "package.json",
                     "Pipfile", "Cargo.toml", "CMakeLists.txt",
                     "vcpkg.json", "go.mod", "build.gradle"):
        with tempfile.TemporaryDirectory() as td:
            proj, ok = _escaping_project(Path(td).resolve(), manifest)
            if not ok:
                return
            result = scan_dependencies(str(proj))
            blob = str(result)
            assert CANARY not in blob, f"{manifest} was read from outside the project"


def test_in_root_manifest_is_still_parsed():
    """Proves the tests above are not passing because nothing is detected."""
    from dependency_scan import scan_dependencies

    with tempfile.TemporaryDirectory() as td:
        proj = Path(td).resolve() / "proj"
        proj.mkdir()
        (proj / "requirements.txt").write_text("openai==1.0.0\nnumpy==1.26.0\n")

        result = scan_dependencies(str(proj))
        blob = str(result)
        assert "openai" in blob and "numpy" in blob, blob


def _run_cli(*args):
    return subprocess.run(
        [sys.executable, "-m", "scripts.cli", *args],
        cwd=str(REPO), capture_output=True, text=True, timeout=180,
    )


def test_regula_deps_does_not_leak_out_of_root_packages():
    with tempfile.TemporaryDirectory() as td:
        proj, ok = _escaping_project(Path(td).resolve())
        if not ok:
            return
        r = _run_cli("deps", str(proj), "--format", "json")
        assert CANARY not in r.stdout, r.stdout[:600]


def test_regula_sbom_does_not_leak_out_of_root_packages():
    """sbom's own walkers were guarded while it still leaked here, via
    scan_dependencies — a guard applied per-walker misses delegated reads."""
    with tempfile.TemporaryDirectory() as td:
        proj, ok = _escaping_project(Path(td).resolve())
        if not ok:
            return
        r = _run_cli("sbom", str(proj))
        assert CANARY not in r.stdout, r.stdout[:600]
