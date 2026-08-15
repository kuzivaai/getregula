# regula-ignore
"""The published comparison table is a claim surface about named third parties.

Three shipped homepages used to carry three hand-maintained copies of one
comparison table. That is the drift shape `site/regions/` already learned the
hard way, with the added problem that the subject is other companies: a stale
or hand-edited cell is a wrong statement about someone else's product.

`data/comparison_table.json` is the single source; `scripts/build_comparison.py`
renders it. This file guards four properties:

1. The shipped HTML matches a fresh render, so a hand edit cannot survive CI.
2. The `verified_on` stamp is inside `max_age_days`, and the staleness check
   actually fails when it is not. The negative half matters most: a freshness
   gate that never fires looks exactly like one with nothing to find.
3. Unverified cells carry the literal marker in every language, so a cell
   cannot read as a fact in German while reading as unknown in English.
4. Fairness constraints that a UK comparison must meet: every cell is filled,
   the caveat is present and dated, and no cell characterises a competitor
   with the loaded words the standard forbids.
"""

from __future__ import annotations

import json
import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import build_comparison as bc  # noqa: E402

LANGS = ("en", "de", "pt")

# Words a comparison must not use about a named competitor. The UK standard
# requires objective, verifiable, non-denigratory comparison, so the table
# states what a provider's own page says or says "not verified".
DENIGRATORY = (
    "inferior", "worse", "weak", "poor", "useless", "bloated", "overpriced",
    "rip-off", "ripoff", "outdated", "primitive", "toy", "amateur",
    "misleading", "dishonest", "fake",
)


def data() -> dict:
    return bc.load()


class TestSourceOfTruth(unittest.TestCase):
    def test_shipped_pages_match_a_fresh_render(self) -> None:
        self.assertEqual(
            [], bc.check(),
            "shipped comparison HTML differs from data/comparison_table.json; "
            "run python3 scripts/build_comparison.py --apply",
        )

    def test_every_target_page_carries_the_markers(self) -> None:
        for locale, path in bc.TARGETS.items():
            body = path.read_text(encoding="utf-8")
            self.assertIn(bc.BEGIN, body, f"{path} lost the begin marker")
            self.assertIn(bc.END, body, f"{path} lost the end marker")

    def test_the_table_appears_exactly_once_per_page(self) -> None:
        """Replacing a hand-written block must not leave the old one behind."""
        marker = 'class="cmp-table"'
        for locale, path in bc.TARGETS.items():
            found = path.read_text(encoding="utf-8").count(marker)
            # The count is bound to a name rather than interpolated inline:
            # a backslash escape inside an f-string is a syntax error before
            # Python 3.12, and this project supports 3.10.
            self.assertEqual(
                1, found,
                f"{path} carries {found} comparison tables; "
                f"the generated one must be the only one",
            )


class TestFreshness(unittest.TestCase):
    def test_the_committed_stamp_is_current(self) -> None:
        self.assertIsNone(bc.freshness_error())

    def test_a_stamp_one_day_past_the_limit_fails(self) -> None:
        d = data()
        stamped = date.fromisoformat(d["verified_on"])
        too_late = stamped + timedelta(days=int(d["max_age_days"]) + 1)
        err = bc.freshness_error(too_late, d)
        self.assertIsNotNone(
            err, "the freshness gate did not fire one day past its limit")
        self.assertIn("days old", err)

    def test_a_stamp_exactly_on_the_limit_passes(self) -> None:
        """The boundary is inclusive; an off-by-one here expires a good table."""
        d = data()
        stamped = date.fromisoformat(d["verified_on"])
        on_limit = stamped + timedelta(days=int(d["max_age_days"]))
        self.assertIsNone(bc.freshness_error(on_limit, d))

    def test_a_future_stamp_is_rejected(self) -> None:
        d = data()
        stamped = date.fromisoformat(d["verified_on"])
        err = bc.freshness_error(stamped - timedelta(days=1), d)
        self.assertIsNotNone(err, "a future-dated stamp was accepted")
        self.assertIn("future", err)


class TestCellIntegrity(unittest.TestCase):
    def test_every_row_fills_every_column_in_every_language(self) -> None:
        d = data()
        keys = [c["key"] for c in d["columns"]]
        for row in d["rows"]:
            for key in keys:
                self.assertIn(key, row["cells"],
                              f"row {row['key']} has no cell for {key}")
                for lang in LANGS:
                    value = row["cells"][key].get(lang, "").strip()
                    self.assertTrue(
                        value,
                        f"row {row['key']}, column {key}, language {lang} "
                        f"is empty; an empty cell reads as a claim of nothing",
                    )

    def test_unverified_is_marked_in_every_language_or_none(self) -> None:
        """A cell cannot be a fact in one language and unknown in another."""
        d = data()
        for row in d["rows"]:
            for col in d["columns"]:
                cell = row["cells"][col["key"]]
                marked = {
                    lang for lang in LANGS
                    if cell[lang].strip().lower() == bc.NOT_VERIFIED
                }
                self.assertIn(
                    len(marked), (0, len(LANGS)),
                    f"row {row['key']}, column {col['key']} is marked "
                    f"'{bc.NOT_VERIFIED}' in {sorted(marked)} but not in the "
                    f"other languages",
                )

    def test_a_verified_column_names_its_sources(self) -> None:
        """Any column with at least one asserted cell must cite where from."""
        d = data()
        for col in d["columns"]:
            asserted = [
                row["key"] for row in d["rows"]
                if row["cells"][col["key"]]["en"].strip().lower()
                != bc.NOT_VERIFIED
            ]
            if not asserted:
                continue
            self.assertTrue(
                d["sources"].get(col["key"]),
                f"column {col['key']} asserts {len(asserted)} cell(s) "
                f"({asserted}) but lists no source URL",
            )

    def test_no_cell_denigrates_a_competitor(self) -> None:
        d = data()
        for row in d["rows"]:
            for col in d["columns"]:
                if col["key"] == "regula":
                    continue
                for lang in LANGS:
                    lowered = row["cells"][col["key"]][lang].lower()
                    for word in DENIGRATORY:
                        self.assertNotIn(
                            word, lowered,
                            f"row {row['key']}, column {col['key']}, {lang} "
                            f"uses '{word}'; a comparison must not denigrate",
                        )

    def test_the_caveat_is_present_dated_and_names_the_marker(self) -> None:
        d = data()
        for lang in LANGS:
            caveat = d["caveat"][lang]
            self.assertIn("{date}", caveat,
                          f"{lang} caveat has no date placeholder")
            self.assertIn("not verified", caveat.lower(),
                          f"{lang} caveat does not explain the marker")
        for locale, path in bc.TARGETS.items():
            body = path.read_text(encoding="utf-8")
            self.assertIn(d["verified_on"], body,
                          f"{path} does not carry the verified stamp")

    def test_no_dashes_in_the_published_table(self) -> None:
        """Project rule: no em or en dashes in new prose, entities included."""
        raw = (REPO_ROOT / "data" / "comparison_table.json").read_text(
            encoding="utf-8")
        for bad in ("—", "–", "&mdash;", "&ndash;",
                    "&#8212;", "&#8211;", "&#x2014;", "&#x2013;"):
            self.assertNotIn(bad, raw,
                             f"comparison table source contains {bad!r}")


if __name__ == "__main__":
    unittest.main()
