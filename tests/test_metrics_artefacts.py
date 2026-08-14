# regula-ignore
"""N109 - a period label in a metrics artefact must describe its own data.

`data/metrics/pypi_weekly.json` recorded, every Monday from 2026-04-20 to
2026-08-10, a whole-period cumulative download total under a hard-coded
`"period": "last_7_days"`. The label was a string constant in
`.github/workflows/weekly-metrics.yaml`; nothing derived it from the payload
and nothing checked it. Measured on 2026-08-14 against the pypistats daily
series, the final row overstated weekly downloads by ~35x with mirrors
(7,259 recorded against 208 actual) and ~88x without (2,211 against 25).

The figure reached project memory as "1,282-2,177/wk" before it was caught.
It reached no published surface, which is luck rather than design: nothing
under `data/metrics/` had any test at all, which is why a monotonically
rising "weekly" series survived four months of collection.

Two properties are guarded here, because the collector fix alone would not
have caught the original defect:

1. A windowed row must carry the window it was summed over, and that window
   must actually be the width its label claims. A constant label cannot
   satisfy this, which is the point.
2. A windowed total can never exceed the all-time total it is drawn from,
   and a series of windowed totals must not be monotonically non-decreasing
   across its whole length. Cumulative data masquerading as periodic data
   fails the second test even if someone reintroduces a plausible label.
"""

from __future__ import annotations

import json
import unittest
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PYPI_ARTEFACT = REPO_ROOT / "data/metrics/pypi_weekly.json"

# Rows collected before the 2026-08-14 correction are retained with their
# values intact and their labels corrected to what they actually are. They
# are legitimately cumulative, so the windowed checks do not apply to them.
CORRECTED_LABEL = "all_time_to_collection_date"


def _load(path: Path) -> list[dict]:
    return json.loads(path.read_text())


def _windowed_rows(rows: list[dict]) -> list[dict]:
    return [r for r in rows if str(r.get("period", "")).startswith("last_")]


# The three checks below are pure functions over a row list, not assertions
# against the committed file. That separation is deliberate and is itself a
# finding: when every committed row is `all_time_to_collection_date`,
# `_windowed_rows` selects nothing and any check written only against the real
# artefact iterates an empty list and passes for the wrong reason. Measurement
# rule 4 calls that a blank gate, not a green gate. The predicates are
# therefore exercised against constructed rows by
# `TestWindowChecksDetectPlantedDefects`, which bites on every run regardless
# of what the collector has written so far, and applied to the real artefact by
# `TestPypiWeeklyArtefact`.


def window_width_violations(rows: list[dict]) -> list[str]:
    """Rows whose period label claims a width their window does not span."""
    out = []
    for row in _windowed_rows(rows):
        label = row["period"]
        start, end = row.get("window_start"), row.get("window_end")
        if start is None or end is None:
            out.append(f"{row.get('date')}: {label} with no window bounds")
            continue
        try:
            claimed = int(label.split("_")[1])
        except (IndexError, ValueError):
            out.append(f"{row.get('date')}: unparseable period label {label!r}")
            continue
        actual = (date.fromisoformat(end) - date.fromisoformat(start)).days + 1
        if claimed != actual:
            out.append(
                f"{row.get('date')}: labelled {label} but {start}..{end} "
                f"spans {actual} days"
            )
    return out


def exceeds_all_time_violations(rows: list[dict]) -> list[str]:
    """Windowed totals that exceed the all-time total they are drawn from."""
    out = []
    for row in _windowed_rows(rows):
        all_time = row.get("all_time_to_date") or {}
        for category, value in (row.get("downloads") or {}).items():
            if category in all_time and value > all_time[category]:
                out.append(
                    f"{row.get('date')}: windowed {category}={value} exceeds "
                    f"all-time {all_time[category]}"
                )
    return out


def cumulative_series_violations(rows: list[dict]) -> list[str]:
    """Windowed series that never decrease: the N109 defect's fingerprint.

    Genuine weekly traffic fluctuates. A strictly non-decreasing run across the
    whole series is what cumulative data looks like wearing a periodic label.
    """
    out = []
    for category in ("with_mirrors", "without_mirrors"):
        series = [
            r["downloads"][category]
            for r in _windowed_rows(rows)
            if category in (r.get("downloads") or {})
        ]
        if len(series) < 3:
            continue
        if all(b >= a for a, b in zip(series, series[1:])):
            out.append(
                f"{category}: series never decreases across {len(series)} "
                f"rows ({series}); that is cumulative, not periodic"
            )
    return out


def _windowed_row(date_str: str, downloads: dict, days: int = 7,
                  start: str = "2026-08-07", end: str = "2026-08-13",
                  all_time: dict | None = None) -> dict:
    """Build one syntactically valid windowed row for the synthetic checks."""
    return {
        "date": date_str,
        "period": f"last_{days}_complete_days",
        "window_start": start,
        "window_end": end,
        "downloads": dict(downloads),
        "all_time_to_date": dict(all_time or {k: v * 100 for k, v in downloads.items()}),
    }


def artefact_rows() -> list[dict]:
    """Load the committed artefact.

    Deliberately not a `setUp`: the custom runner in
    `tests/test_classification.py` binds TestCase methods directly under
    `RUNNER_ALIAS_PREFIX` and calling a bound method does NOT invoke `setUp`,
    so any state built there would be silently missing. Every method loads
    what it needs instead. See `.claude/rules/tests.md`.
    """
    if not PYPI_ARTEFACT.exists():
        raise AssertionError(
            f"{PYPI_ARTEFACT} is missing; the weekly-metrics workflow writes it"
        )
    rows = _load(PYPI_ARTEFACT)
    if not rows:
        raise AssertionError(f"{PYPI_ARTEFACT} is empty")
    return rows


class TestPypiWeeklyArtefact(unittest.TestCase):
    def test_every_row_declares_a_period(self) -> None:
        for i, row in enumerate(artefact_rows()):
            self.assertIn("period", row, f"row {i} ({row.get('date')}) has no period")

    def test_windowed_rows_carry_a_window_of_the_width_they_claim(self) -> None:
        self.assertEqual([], window_width_violations(artefact_rows()))

    def test_windowed_total_never_exceeds_all_time(self) -> None:
        self.assertEqual([], exceeds_all_time_violations(artefact_rows()))

    def test_windowed_series_is_not_cumulative(self) -> None:
        self.assertEqual([], cumulative_series_violations(artefact_rows()))

    def test_corrected_historical_rows_kept_their_values(self) -> None:
        """The 2026-08-14 correction relabels; it must never rewrite figures."""
        corrected = [r for r in artefact_rows() if r.get("period") == CORRECTED_LABEL]
        for row in corrected:
            self.assertIn(
                "period_label_corrected",
                row,
                f"row {row.get('date')} carries the corrected label without "
                f"recording when it was corrected",
            )
            # Structure, not emptiness: some historical rows legitimately have
            # `"downloads": {}` because collection failed silently that week
            # (2026-05-11, 2026-06-01 and 2026-06-29). Preserving that is part of the
            # record; the relabel must not have dropped the key.
            self.assertIn(
                "downloads",
                row,
                f"row {row.get('date')} lost its downloads key in the relabel",
            )


class TestWindowChecksDetectPlantedDefects(unittest.TestCase):
    """Exercise the three predicates against constructed rows.

    Each is a pair: clean data must pass and a planted defect must be caught.
    Without the negative half a predicate that never fires looks identical to
    one that has nothing to find, which is precisely how N109 survived.
    """

    def test_clean_windowed_rows_produce_no_violations(self) -> None:
        rows = [
            _windowed_row("2026-08-17", {"with_mirrors": 208, "without_mirrors": 25}),
            _windowed_row("2026-08-24", {"with_mirrors": 141, "without_mirrors": 19}),
            _windowed_row("2026-08-31", {"with_mirrors": 190, "without_mirrors": 31}),
        ]
        self.assertEqual([], window_width_violations(rows))
        self.assertEqual([], exceeds_all_time_violations(rows))
        self.assertEqual([], cumulative_series_violations(rows))

    def test_label_wider_than_its_window_is_caught(self) -> None:
        row = _windowed_row(
            "2026-08-17", {"with_mirrors": 208}, days=30,
            start="2026-08-07", end="2026-08-13",
        )
        found = window_width_violations([row])
        self.assertEqual(1, len(found), found)
        self.assertIn("spans 7 days", found[0])

    def test_windowed_row_without_bounds_is_caught(self) -> None:
        row = _windowed_row("2026-08-17", {"with_mirrors": 208})
        del row["window_start"]
        found = window_width_violations([row])
        self.assertEqual(1, len(found), found)
        self.assertIn("no window bounds", found[0])

    def test_window_exceeding_all_time_is_caught(self) -> None:
        row = _windowed_row(
            "2026-08-17", {"with_mirrors": 9_000},
            all_time={"with_mirrors": 7_395},
        )
        found = exceeds_all_time_violations([row])
        self.assertEqual(1, len(found), found)
        self.assertIn("exceeds all-time", found[0])

    def test_the_original_n109_series_is_caught(self) -> None:
        """The real mislabelled figures, relabelled windowed: must be caught.

        These are the actual without_mirrors values from the artefact's last
        five rows. If this predicate ever stops firing on them, it has stopped
        detecting the defect it was written for.
        """
        values = [1132, 1282, 1407, 1920, 2177]
        rows = [
            _windowed_row(f"2026-07-{6 + i * 7:02d}", {"without_mirrors": v})
            for i, v in enumerate(values)
        ]
        found = cumulative_series_violations(rows)
        self.assertEqual(1, len(found), found)
        self.assertIn("never decreases", found[0])

    def test_a_short_series_is_not_judged_cumulative(self) -> None:
        """Two rising points are not evidence; the guard must not cry wolf."""
        rows = [
            _windowed_row("2026-08-17", {"with_mirrors": 100}),
            _windowed_row("2026-08-24", {"with_mirrors": 150}),
        ]
        self.assertEqual([], cumulative_series_violations(rows))


class TestCollectorDoesNotHardcodeThePeriod(unittest.TestCase):
    """The root cause was a constant. Guard the source, not just the output."""

    WORKFLOW = REPO_ROOT / ".github/workflows/weekly-metrics.yaml"

    @staticmethod
    def _executable_lines(text: str) -> str:
        """Strip comment lines.

        The workflow documents the N109 defect by quoting the offending
        literal. Matching raw file text would flag that comment and make the
        guard unmaintainable, so only executable lines are considered.
        """
        out = []
        for line in text.split("\n"):
            stripped = line.lstrip()
            if stripped.startswith("#"):
                continue
            out.append(line)
        return "\n".join(out)

    def test_period_is_not_a_bare_last_7_days_constant(self) -> None:
        self.assertTrue(self.WORKFLOW.exists(), f"{self.WORKFLOW} is missing")
        code = self._executable_lines(self.WORKFLOW.read_text())
        self.assertNotIn(
            '"period": "last_7_days"',
            code,
            "the collector again writes a constant period label; it must "
            "derive the window from the payload's own date fields (N109)",
        )

    def test_collector_records_the_window_boundaries(self) -> None:
        text = self.WORKFLOW.read_text()
        for key in ("window_start", "window_end"):
            self.assertIn(
                key,
                text,
                f"the collector no longer records {key}, so a future reader "
                f"cannot re-derive the figure (N109)",
            )


if __name__ == "__main__":
    unittest.main()
