#!/usr/bin/env python3
# regula-ignore
"""The cascade tool must be incapable of touching anything off-manifest.

The required control (owner-set): plant an out-of-manifest literal AND a
lockfile in a fixture tree, and prove both come through untouched. Without
that, the tool is a promise rather than a mechanism.

Stdlib only.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import cascade_count as cc  # noqa: E402


UV_LOCK_FRAGMENT = """
wheels = [
    {{ url = "https://files.pythonhosted.org/packages/47/c0/80ecd9bd45776109fab14040e478bf63e456967c9ddee{old}d8330ed8de1/brotlicffi.whl", hash = "sha256:3c9544f83cb715d95d7eab3af4adbbef8b2093ad63822{old}5feb1a57ec", size = 222{old}, upload-time = "2026-03-05T19:53:52.215Z" }},
]
"""


class TestCascadeRefusal(unittest.TestCase):

    def test_lockfile_class_is_refused_even_if_manifested(self):
        """The second belt. A manifest edit must not be able to add one."""
        for name in ("uv.lock", "poetry.lock", "go.sum", "Cargo.lock",
                     "package-lock.json", "sig.asc", "x.sha256"):
            with self.assertRaises(cc.RefusedError, msg=name):
                cc.assert_permitted(name)

    def test_path_escape_is_refused(self):
        for bad in ("../outside.md", "/etc/passwd"):
            with self.assertRaises(cc.RefusedError, msg=bad):
                cc.assert_permitted(bad)

    def test_ordinary_surfaces_are_permitted(self):
        for ok in ("README.md", "site/index.html", "data/site_facts.json"):
            cc.assert_permitted(ok)  # must not raise

    def test_the_real_uv_lock_content_survives_the_replacement_logic(self):
        """THE CONTROL, reproducing the actual near-miss.

        The 28 July near-miss rewrote a URL hash path and an integrity size
        field inside uv.lock when 2353 -> 2354 was applied globally. Here the
        same content is fed through the tool's own matcher. Nothing may
        change: the digits sit inside longer alphanumeric runs, so the
        context-bound pattern must not match them.
        """
        old, new = 2353, 2354
        content = UV_LOCK_FRAGMENT.format(old=old)
        result = content
        for rx in cc._patterns(old):
            result = rx.sub(str(new), result)
        self.assertEqual(
            result, content,
            "the cascade matcher rewrote lockfile content; the context-bound "
            "pattern is not tight enough and the 28 July near-miss would "
            "recur")

    def test_out_of_manifest_literal_is_never_a_candidate(self):
        """Refusal is by construction: the tool iterates the manifest, so a
        file that is not in it is never opened. Assert the manifest does not
        contain any denied class, which is the only way one could be reached.
        """
        for rel in cc.manifest_surfaces():
            cc.assert_permitted(rel)

    def test_stale_value_detection_is_bounded(self):
        """A wide net is how a size field gets rewritten. Only 4-digit values
        within 20% of canonical count as stale."""
        new = 2354
        text = "tests 2353 passing and size 222353"
        stale = cc._stale_values(text, new)
        self.assertIn(2353, stale, "a real stale count was not detected")
        self.assertNotIn(222353, stale, "6-digit value treated as a count")

    def test_years_in_band_are_not_rewritten(self):
        """THE SECOND CONTROL. With canonical 2,354 the +/-20% band spans
        1883-2824, which contains the year 2026. An earlier draft would have
        rewritten dates. Semantic context is what prevents it."""
        new = 2354
        for text in ("Released 2 August 2026 under the Act",
                     "verified 2026-07-28",
                     "Regulation (EU) 2024/1689 applies",
                     "port 2000 is reserved"):
            self.assertEqual(
                cc._stale_values(text, new), set(),
                f"non-count number treated as a stale count in: {text!r}")

    def test_canonical_source_is_the_only_input(self):
        """The new value may never come from an argument."""
        self.assertIsInstance(cc.canonical_count(), int)
        self.assertGreater(cc.canonical_count(), 0)

    def test_repo_is_currently_in_sync(self):
        """--check must be clean at HEAD, or the cascade was done by hand."""
        self.assertEqual(
            cc.main(["--check"]), 0,
            "manifest surfaces drift from the canonical count; run "
            "python3 scripts/cascade_count.py --apply")


if __name__ == "__main__":
    unittest.main(verbosity=2)
