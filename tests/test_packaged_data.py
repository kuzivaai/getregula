# regula-ignore
"""Every checked-in data file a shipped module reads must be packaged.

This guards a defect class, not one file. `scripts/eli_data/` was added
without a matching `package-data` entry, so the built wheel omitted it
and `scripts/build_delta_dataset.py` could not run from an installed
package. `scripts/bias_data/` had the identical failure earlier — the
comment above the `package-data` line in `pyproject.toml` records it.
Twice is a pattern, so the check is derived rather than enumerated: any
new `scripts/<name>_data/` directory must declare itself.

Deliberately reads `pyproject.toml` rather than building a wheel: the
suite must stay fast and offline, and the declaration is the thing that
actually decides what ships.
"""

import re
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPTS = REPO / "scripts"


def _package_data_globs() -> list:
    text = (REPO / "pyproject.toml").read_text(encoding="utf-8")
    m = re.search(r'^"scripts"\s*=\s*\[(.*?)\]', text,
                  re.MULTILINE | re.DOTALL)
    if not m:
        raise AssertionError(
            'pyproject.toml has no `"scripts" = [...]` package-data entry; '
            "without it no scripts/ data file ships at all")
    return re.findall(r'"([^"]+)"', m.group(1))


class TestPackagedData(unittest.TestCase):
    def test_every_data_directory_is_declared(self):
        globs = _package_data_globs()
        data_dirs = sorted(
            d for d in SCRIPTS.iterdir()
            if d.is_dir() and d.name.endswith("_data")
            and any(d.glob("*.json"))
        )
        self.assertTrue(
            data_dirs,
            "vacuity control: no scripts/*_data directories found, so this "
            "test would pass without checking anything")

        undeclared = [
            d.name for d in data_dirs
            if not any(g.startswith(f"{d.name}/") for g in globs)
        ]
        self.assertEqual(
            undeclared, [],
            f"scripts/{undeclared} contain .json files that shipped code "
            f"reads, but pyproject.toml does not declare them in "
            f"package-data, so they are absent from the built wheel. This "
            f"is the bias_data and eli_data failure repeating.")

    def test_declared_globs_actually_match_files(self):
        """A declaration that matches nothing is as bad as none at all."""
        for glob_pat in _package_data_globs():
            with self.subTest(glob=glob_pat):
                self.assertTrue(
                    list(SCRIPTS.glob(glob_pat)),
                    f"package-data declares {glob_pat!r} but nothing matches "
                    f"it; the declaration is stale and protects nothing")

    def test_eli_snapshot_is_present_and_loadable(self):
        """The specific file whose omission prompted this test."""
        sys.path.insert(0, str(SCRIPTS))
        import build_delta_dataset as bdd

        self.assertTrue(bdd.ELI_SNAPSHOT_PATH.exists(),
                        "the ELI ontology snapshot is missing")
        terms = bdd.load_eli_snapshot()
        self.assertGreater(len(terms), 100,
                           "ELI snapshot loaded but looks empty")


if __name__ == "__main__":
    unittest.main()
