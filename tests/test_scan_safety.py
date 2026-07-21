#!/usr/bin/env python3
# regula-ignore
"""Tests for scripts/scan_safety.py — the shared path-safety gate.

`scan_safety.is_safe_to_scan` was extracted so that every walker over an
untrusted project tree applies the SAME symlink-escape and size checks.
Before extraction only `report.py` had the guard; `sbom.py`'s four
independent walkers did not.

The `report.py` side is covered by tests/test_scan_security.py. This file
covers the two things that were still untested after the extraction:

  1. `is_safe_to_scan` itself, as a unit — every branch of its contract,
     so the shared primitive cannot regress silently underneath both
     callers at once.
  2. `sbom.py`'s four walkers — the paths the extraction actually
     protected, which had no symlink-escape coverage of their own.

pytest-only (not registered in tests/test_classification.py), following
the tests/test_manifest_timestamp.py convention, so the custom runner's
executed-function count is unaffected.
"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from constants import MAX_FILE_SIZE_BYTES  # noqa: E402
from scan_safety import is_safe_to_scan  # noqa: E402


def _symlinks_supported(tmp: Path) -> bool:
    """Some filesystems (and Windows without developer mode) cannot create
    symlinks. Mirrors the skip convention in tests/test_scan_security.py."""
    try:
        target = tmp / "_probe_target"
        target.write_text("x")
        (tmp / "_probe_link").symlink_to(target)
    except (OSError, NotImplementedError):
        return False
    (tmp / "_probe_link").unlink()
    target.unlink()
    return True


# ── unit: is_safe_to_scan contract ────────────────────────────────

def test_ordinary_file_inside_root_is_safe():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td).resolve()
        f = root / "app.py"
        f.write_text("print('hello')")

        assert is_safe_to_scan(f, root) == (True, "")


def test_nested_file_inside_root_is_safe():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td).resolve()
        nested = root / "src" / "deep" / "mod.py"
        nested.parent.mkdir(parents=True)
        nested.write_text("x = 1")

        assert is_safe_to_scan(nested, root) == (True, "")


def test_symlink_escaping_root_is_rejected():
    """The core threat: a symlink inside the scanned repo pointing at a
    file outside it must not be readable via the scan."""
    with tempfile.TemporaryDirectory() as outside_td:
        outside = Path(outside_td).resolve()
        secret = outside / "id_rsa"
        secret.write_text("PRIVATE KEY MATERIAL")

        with tempfile.TemporaryDirectory() as td:
            root = Path(td).resolve()
            if not _symlinks_supported(root):
                return  # symlinks unsupported on this platform/filesystem
            link = root / "innocuous.py"
            link.symlink_to(secret)

            safe, reason = is_safe_to_scan(link, root)
            assert safe is False
            assert reason == "symlink_escape"


def test_symlink_resolving_inside_root_is_still_safe():
    """An in-repo symlink (e.g. a monorepo convenience link) is legitimate
    and must NOT be treated as an escape — otherwise the guard silently
    drops real files from the scan."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td).resolve()
        if not _symlinks_supported(root):
            return
        real = root / "real.py"
        real.write_text("x = 1")
        link = root / "alias.py"
        link.symlink_to(real)

        assert is_safe_to_scan(link, root) == (True, "")


def test_symlinked_ancestor_directory_escaping_root_is_rejected():
    """Escape via a symlinked *parent directory*, not the file itself.
    os.walk(followlinks=False) prevents traversal into these, but the
    guard must also hold when such a path is passed in directly."""
    with tempfile.TemporaryDirectory() as outside_td:
        outside = Path(outside_td).resolve()
        (outside / "secrets").mkdir()
        (outside / "secrets" / "token.py").write_text("TOKEN = 'x'")

        with tempfile.TemporaryDirectory() as td:
            root = Path(td).resolve()
            if not _symlinks_supported(root):
                return
            (root / "vendor").symlink_to(outside / "secrets")

            safe, reason = is_safe_to_scan(root / "vendor" / "token.py", root)
            assert safe is False
            assert reason == "symlink_escape"


def test_oversized_file_is_rejected():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td).resolve()
        big = root / "huge.py"
        # Sparse file: st_size reports the full length without writing
        # 10 MB to disk, which is what the guard actually checks.
        with open(big, "wb") as fh:
            fh.truncate(MAX_FILE_SIZE_BYTES + 1)

        safe, reason = is_safe_to_scan(big, root)
        assert safe is False
        assert reason == "oversized"


def test_file_exactly_at_size_limit_is_accepted():
    """The check is `>`, not `>=` — a file exactly at the cap is legal.
    Pinned so the boundary cannot drift unnoticed in either direction."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td).resolve()
        at_limit = root / "at_limit.py"
        with open(at_limit, "wb") as fh:
            fh.truncate(MAX_FILE_SIZE_BYTES)

        assert is_safe_to_scan(at_limit, root) == (True, "")


def test_missing_file_reports_stat_failed_not_safe():
    """A file that vanishes between walk and check (TOCTOU race) must fail
    closed, not be reported as safe."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td).resolve()

        safe, reason = is_safe_to_scan(root / "never_existed.py", root)
        assert safe is False
        assert reason == "stat_failed"


def test_broken_symlink_inside_root_fails_closed():
    """A dangling symlink resolves to a path under root, so it passes the
    escape check and fails at stat() — it must still be rejected."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td).resolve()
        if not _symlinks_supported(root):
            return
        link = root / "dangling.py"
        link.symlink_to(root / "gone.py")

        safe, reason = is_safe_to_scan(link, root)
        assert safe is False
        assert reason == "stat_failed"


# ── integration: sbom.py's four walkers ───────────────────────────

def _make_escaping_link(root: Path, outside: Path, name: str, content: str):
    """Create `outside/<name>` and a symlink to it at `root/<name>`.
    Returns False if symlinks are unsupported."""
    if not _symlinks_supported(root):
        return False
    target = outside / name
    target.write_text(content)
    (root / name).symlink_to(target)
    return True


def test_sbom_model_file_scan_ignores_escaping_symlink():
    import sbom

    with tempfile.TemporaryDirectory() as outside_td, \
            tempfile.TemporaryDirectory() as td:
        outside, root = Path(outside_td).resolve(), Path(td).resolve()
        if not _make_escaping_link(root, outside, "leaked.onnx", "binary"):
            return
        # A legitimate in-root model, to prove the walker still works.
        (root / "local.onnx").write_text("binary")

        found = {m["file_path"] for m in sbom._scan_model_files(str(root))}
        assert "local.onnx" in found
        assert "leaked.onnx" not in found


def test_sbom_dataset_file_detection_ignores_escaping_symlink():
    import sbom

    with tempfile.TemporaryDirectory() as outside_td, \
            tempfile.TemporaryDirectory() as td:
        outside, root = Path(outside_td).resolve(), Path(td).resolve()
        if not _make_escaping_link(root, outside, "leaked.csv", "a,b\n1,2\n"):
            return
        (root / "local.csv").write_text("a,b\n1,2\n")

        found = {d["path"] for d in sbom._detect_dataset_files(str(root))}
        assert "local.csv" in found
        assert "leaked.csv" not in found


def test_sbom_dataset_pattern_scan_ignores_escaping_symlink():
    """This walker READS file content, so an escape here leaks the file's
    text into the generated AI-BOM, not just its name."""
    import sbom

    with tempfile.TemporaryDirectory() as outside_td, \
            tempfile.TemporaryDirectory() as td:
        outside, root = Path(outside_td).resolve(), Path(td).resolve()
        payload = "datasets.load_dataset('leaked-secret-corpus')\n"
        if not _make_escaping_link(root, outside, "leaked.py", payload):
            return
        # Positive control: an in-root file using the SAME pattern must
        # still be detected, so a passing test cannot mean "detects nothing".
        (root / "local.py").write_text(
            "datasets.load_dataset('local-corpus')\n"
        )

        names = {d["name"] for d in sbom._scan_datasets(str(root))}
        assert "local-corpus" in names
        assert "leaked-secret-corpus" not in names


def test_sbom_model_metadata_extraction_ignores_escaping_symlink():
    """This walker parses JSON and copies up to 20 KEY NAMES into the
    AI-BOM, so an escape here leaks the structure of an out-of-repo file."""
    import sbom

    with tempfile.TemporaryDirectory() as outside_td, \
            tempfile.TemporaryDirectory() as td:
        outside, root = Path(outside_td).resolve(), Path(td).resolve()
        leaked = '{"leaked_secret_field": 1}'
        if not _make_escaping_link(root, outside, "config.json", leaked):
            return
        (root / "nested").mkdir()
        (root / "nested" / "config.json").write_text('{"local_field": 1}')

        results = sbom._extract_model_metadata(str(root))
        found = {m["path"] for m in results}
        all_fields = {f for m in results for f in m["fields_found"]}

        assert str(Path("nested") / "config.json") in found
        assert "config.json" not in found
        assert "leaked_secret_field" not in all_fields
        assert "local_field" in all_fields
