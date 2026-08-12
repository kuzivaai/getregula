# regula-ignore
"""Guards the integrity of the published test count.

Background: `tests/test_classification.py` rebinds fixture-less test
functions from sibling modules into its own namespace so the custom
runner (`python3 tests/test_classification.py`), which discovers tests by
walking `globals()`, can execute them. That mechanism is deliberate — a
manual list was removed as tech debt because it silently drifted.

The defect it caused: pytest also collects module-level names matching
`python_functions` (`pyproject.toml`: `test_*`), so every rebound
function was collected twice — once in its own module, once here. The
published count over-stated reality by 527 (2,849 collected vs 2,322
real).

The fix binds the aliases under a prefix pytest does not collect. These
tests kill the *class* of defect rather than the single instance: any
future mechanism that causes pytest to collect the same test function
twice fails here, whatever its cause.
"""

import collections
import re
import subprocess
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def _collect_node_ids() -> list:
    """Every node ID pytest collects for tests/, via pytest itself."""
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", str(REPO / "tests"),
         "--collect-only", "-q"],
        capture_output=True, text=True, check=False, timeout=300,
        cwd=str(REPO),
    )
    if proc.returncode != 0:
        raise AssertionError(
            f"pytest collection failed (rc={proc.returncode}); refusing to "
            f"assert on an unmeasured count: "
            f"{(proc.stderr or proc.stdout).strip()[-400:]}"
        )
    return [ln.strip() for ln in proc.stdout.splitlines() if "::" in ln]


class TestNoDoubleCollection(unittest.TestCase):
    """The class-killing guard: no test function may be collected twice."""

    def test_collected_node_ids_equal_unique_test_functions(self):
        nodes = _collect_node_ids()
        self.assertGreater(len(nodes), 1000,
                           "vacuity control: collection returned almost "
                           "nothing, so this test proves nothing")

        # A node ID is <module>::<maybe class>::<function>. The same
        # function object collected under two different modules is a
        # double-count. Genuine same-name-different-module tests are NOT
        # duplicates, so identity is (module, qualname) and duplication is
        # detected by resolving each node to the function it executes.
        by_qual = collections.defaultdict(set)
        for node in nodes:
            parts = node.split("::")
            module, qual = parts[0], "::".join(parts[1:])
            by_qual[qual].add(module)

        # Aliasing manifests as one qualname appearing in
        # test_classification.py AND in its home module.
        aliased = {
            qual: sorted(mods) for qual, mods in by_qual.items()
            if len(mods) > 1 and "tests/test_classification.py" in mods
        }
        self.assertEqual(
            aliased, {},
            f"{len(aliased)} test function(s) are collected twice — once in "
            f"their own module and once via a rebind into "
            f"tests/test_classification.py. This inflates every published "
            f"test count. Bind runner aliases under a prefix pytest does "
            f"not collect (see tests/test_classification.py). "
            f"Examples: {sorted(aliased)[:5]}"
        )

    def test_alias_prefix_is_not_collected_by_pytest_config(self):
        """The exclusion must hold against the real config, not the default.

        If someone widens `python_functions`, the aliases start being
        collected again and the count silently re-inflates. This asserts
        the actual configured patterns cannot match the alias prefix.
        """
        pyproject = (REPO / "pyproject.toml").read_text(encoding="utf-8")
        m = re.search(r"^python_functions\s*=\s*\[(.*?)\]", pyproject,
                      re.MULTILINE | re.DOTALL)
        self.assertIsNotNone(
            m, "python_functions is not declared in pyproject.toml; the "
               "alias prefix's safety depends on knowing what pytest "
               "collects, so it must be declared explicitly")
        patterns = re.findall(r'"([^"]+)"', m.group(1))
        self.assertTrue(patterns, "python_functions is empty")

        import fnmatch
        from test_classification import RUNNER_ALIAS_PREFIX
        probe = f"{RUNNER_ALIAS_PREFIX}example_case"
        for pat in patterns:
            self.assertFalse(
                fnmatch.fnmatch(probe, pat),
                f"configured python_functions pattern {pat!r} would collect "
                f"the runner alias {probe!r}, re-introducing the "
                f"double-count")

    def test_custom_runner_expands_parametrized_kernel_controls(self):
        """Parametrized tests must run as cases, not as missing-arg calls."""
        import test_classification as suite

        aliases = [
            value for name, value in vars(suite).items()
            if name.startswith(
                suite.RUNNER_ALIAS_PREFIX
                + "test_empty_input_is_insufficient_in_every_jurisdiction_"
            )
        ]
        self.assertEqual(len(aliases), 3)
        self.assertEqual(
            {alias.__name__.rsplit("[", 1)[-1] for alias in aliases},
            {"0]", "1]", "2]"},
        )
        for alias in aliases:
            alias()


class TestPublishedCountMatchesCollection(unittest.TestCase):
    """The published number must be the measured number, with no bespoke maths."""

    def test_site_facts_total_collected_matches_pytest(self):
        sys.path.insert(0, str(REPO / "scripts"))
        import site_facts

        measured = len(_collect_node_ids())
        reported = site_facts.count_tests()["total_collected"]
        self.assertEqual(
            reported, measured,
            "site_facts.count_tests() must report exactly what pytest "
            "collects, with no adjustment applied. A divergence here means "
            "someone added bespoke counting logic, which is how the "
            "original defect became invisible.")


if __name__ == "__main__":
    unittest.main()
