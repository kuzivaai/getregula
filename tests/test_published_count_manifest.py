# regula-ignore
"""The published test count may appear only where the manifest permits.

Inverted class-kill, mirroring tests/test_packaged_data.py. That test
derives what MUST be declared from the filesystem; this one enumerates
where a value is ALLOWED and then scans the repository for violations.

Why it exists: "nine published surfaces" was once carried in prose,
inherited from a label whose own components summed to ten, and repeated
without anyone counting them. The same trusting-prose-over-measurement
error produced a false claim that verify_seo gated CI. A surface list
that lives only in prose will drift again; a surface list that is
committed data and enforced by a scan cannot.

The consequence this prevents: an eleventh surface starts carrying the
count, nobody notices, and a future correction misses it — leaving a
known-false number published somewhere while every audited surface reads
correct.
"""

import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MANIFEST = REPO / "data" / "published_count_manifest.json"
SITE_FACTS = REPO / "data" / "site_facts.json"


def _manifest() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def _canonical_count() -> int:
    facts = json.loads(SITE_FACTS.read_text(encoding="utf-8"))
    return int(facts["counts"]["tests"]["total_collected"])


def _tracked_files() -> list:
    out = subprocess.run(["git", "ls-files"], cwd=str(REPO),
                         capture_output=True, text=True, check=False).stdout
    return [Path(p) for p in out.splitlines() if p]


class TestPublishedCountManifest(unittest.TestCase):
    def test_manifest_is_wellformed(self):
        m = _manifest()
        self.assertTrue(m["published_surfaces"], "manifest lists no surfaces")
        for entry in m["published_surfaces"]:
            self.assertTrue(
                (REPO / entry).exists(),
                f"manifest lists {entry} which does not exist; a stale "
                f"manifest protects nothing")
        for entry in m["non_surface_carriers"]:
            self.assertIn(entry["role"], ("source", "generated"))
            self.assertTrue((REPO / entry["path"]).exists())

    def test_count_literal_appears_nowhere_outside_the_manifest(self):
        count = _canonical_count()
        m = _manifest()
        allowed = set(m["published_surfaces"])
        allowed |= {e["path"] for e in m["non_surface_carriers"]}
        allowed_prefixes = tuple(
            e["path"] for e in m["excluded_by_design"])

        # Match the number both bare and comma-grouped, and the DE/PT-BR
        # dot-grouped form, since those defeated a manual sweep before.
        grouped = f"{count:,}"
        variants = {str(count), grouped, grouped.replace(",", ".")}
        pattern = re.compile(
            r"(?<!\d)(" + "|".join(re.escape(v) for v in sorted(variants))
            + r")(?!\d)")

        violations = []
        for rel in _tracked_files():
            posix = rel.as_posix()
            if posix in allowed or posix.startswith(allowed_prefixes):
                continue
            if rel.suffix.lower() not in (
                    ".md", ".html", ".txt", ".json", ".py", ".yaml", ".yml"):
                continue
            path = REPO / rel
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            if pattern.search(text):
                violations.append(posix)

        self.assertEqual(
            violations, [],
            f"the published test count ({count}) appears in files not "
            f"listed in data/published_count_manifest.json: {violations}. "
            f"Either add the file to the manifest (and to every future "
            f"count correction), or remove the literal. A surface that "
            f"carries the number without being in the manifest will be "
            f"missed by the next correction and left publishing a stale "
            f"figure.")

    def test_scan_would_actually_catch_a_violation(self):
        """Vacuity control: prove the scan can return a negative."""
        count = _canonical_count()
        grouped = f"{count:,}"
        pattern = re.compile(
            r"(?<!\d)(" + re.escape(str(count)) + "|"
            + re.escape(grouped) + r")(?!\d)")
        planted = f"This page claims {grouped} tests were run."
        self.assertTrue(
            pattern.search(planted),
            "the violation pattern does not match a planted literal, so a "
            "clean run of the scan above would prove nothing")

    def test_canonical_source_is_generated_not_handwritten(self):
        """The number must come from collection, never a hand-typed literal."""
        src = (REPO / "scripts" / "site_facts.py").read_text(encoding="utf-8")
        self.assertIn(
            "--collect-only", src,
            "site_facts.count_tests no longer derives the count from pytest "
            "collection; a hand-maintained count is how the double-count "
            "went unnoticed for so long")


if __name__ == "__main__":
    unittest.main()
