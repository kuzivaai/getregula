# regula-ignore
"""Tests for the machine-readable delta-log dataset (JSON-LD).

Guards:
- The committed dataset is exactly what the builder derives from the entries
  (single source of truth; a hand-edited or stale dataset fails).
- Every eli: term the builder emits exists in the checked-in ELI ontology
  snapshot (never-emit-a-fabricated-IRI, mirroring test_dpv_export).
- Every event in the dataset corresponds 1:1 to an entry file.
- CELEX -> ELI conversion only accepts sector-3 regulation numbers.
- The amendment relation is asserted only when the verified OJ entry exists.
"""

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import build_delta_dataset as bdd


class TestDeltaDatasetSync(unittest.TestCase):
    def test_committed_dataset_is_current(self):
        """The committed JSON-LD must byte-match a fresh render."""
        self.assertTrue(bdd.DATASET_PATH.exists(),
                        "dataset missing — run scripts/build_delta_dataset.py")
        self.assertEqual(bdd.DATASET_PATH.read_text(encoding="utf-8"),
                         bdd.render(),
                         "dataset stale — run scripts/build_delta_dataset.py")

    def test_event_count_matches_entry_files(self):
        doc = json.loads(bdd.DATASET_PATH.read_text(encoding="utf-8"))
        events = [n for n in doc["@graph"]
                  if n.get("@type") == "regula:RegulatoryDeltaEvent"]
        entry_files = sorted(bdd.ENTRIES_DIR.glob("*.json"))
        self.assertEqual(len(events), len(entry_files))
        entry_ids = {json.loads(p.read_text(encoding="utf-8"))["id"]
                     for p in entry_files}
        event_ids = {n["dct:identifier"] for n in events}
        self.assertEqual(entry_ids, event_ids)


class TestEliIriGuarantees(unittest.TestCase):
    def test_all_used_eli_terms_exist_in_snapshot(self):
        terms = bdd.load_eli_snapshot()
        self.assertGreater(len(terms), 100)
        for term in bdd.ELI_TERMS_USED:
            self.assertIn(term, terms,
                          f"eli:{term} not in the ontology snapshot")

    def test_no_undeclared_eli_keys_in_output(self):
        """Every eli:-prefixed KEY in the emitted graph must be declared in
        ELI_TERMS_USED (and therefore snapshot-validated)."""
        doc = json.loads(bdd.render())

        def walk(node):
            if isinstance(node, dict):
                for k, v in node.items():
                    if k.startswith("eli:"):
                        yield k.split(":", 1)[1]
                    yield from walk(v)
                if node.get("@type") == "eli:LegalResource":
                    yield "LegalResource"
            elif isinstance(node, list):
                for item in node:
                    yield from walk(item)

        used = set(walk(doc["@graph"]))
        undeclared = used - set(bdd.ELI_TERMS_USED)
        self.assertEqual(undeclared, set(),
                         f"eli terms emitted but not declared/validated: "
                         f"{undeclared}")

    def test_celex_to_eli_regulation(self):
        self.assertEqual(bdd._celex_to_eli("32026R1744"),
                         "http://data.europa.eu/eli/reg/2026/1744/oj")
        self.assertEqual(bdd._celex_to_eli("32024R1689"),
                         "http://data.europa.eu/eli/reg/2024/1689/oj")

    def test_celex_to_eli_rejects_non_regulation(self):
        with self.assertRaises(SystemExit):
            bdd._celex_to_eli("32026L0001")  # directive, not regulation
        with self.assertRaises(SystemExit):
            bdd._celex_to_eli("not-a-celex")


class TestAmendmentRelation(unittest.TestCase):
    def test_omnibus_amends_ai_act(self):
        doc = json.loads(bdd.DATASET_PATH.read_text(encoding="utf-8"))
        omnibus = next(n for n in doc["@graph"]
                       if n["@id"] == bdd.OMNIBUS_IRI)
        targets = {t["@id"] for t in omnibus["eli:amends"]}
        self.assertIn(bdd.AI_ACT_IRI, targets)

    def test_amendment_only_from_verified_entry(self):
        """If the OJ entry is absent, no amends relation may be asserted."""
        entries = [e for e in bdd.load_entries()
                   if e["id"] != "2026-07-24-oj-publication"]
        nodes = bdd.legal_resource_nodes(entries)
        self.assertEqual(len(nodes), 1)
        self.assertNotIn("eli:amends", nodes[0])


class TestDatasetMetadata(unittest.TestCase):
    def test_dataset_node_essentials(self):
        doc = json.loads(bdd.DATASET_PATH.read_text(encoding="utf-8"))
        ds = doc["@graph"][0]
        self.assertEqual(ds["@type"], "dcat:Dataset")
        self.assertIn("dct:license", ds)
        self.assertIn("dct:conformsTo", ds)
        note = ds["regula:vocabularyNote"]
        self.assertIn("not a ratified W3C Standard", note)

    def test_events_default_to_eu_jurisdiction(self):
        doc = json.loads(bdd.DATASET_PATH.read_text(encoding="utf-8"))
        events = [n for n in doc["@graph"]
                  if n.get("@type") == "regula:RegulatoryDeltaEvent"]
        for e in events:
            self.assertIn("regula:jurisdiction", e)


if __name__ == "__main__":
    unittest.main()
