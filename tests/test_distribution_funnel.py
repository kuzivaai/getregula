"""Exact-window and denominator guards for the anonymous funnel report."""
from __future__ import annotations

import csv
import io
import sys
import tempfile
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from distribution_funnel import build_report  # noqa: E402


def _csv(fieldnames, rows):
    stream = io.StringIO()
    writer = csv.DictWriter(stream, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue()


def _fixture(path: Path, dates=("2026-08-24", "2026-08-25")):
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("visitors.csv", _csv(
            ["date", "visitors", "pageviews", "visits"],
            [{"date": day, "visitors": "2", "pageviews": "4", "visits": "3"} for day in dates],
        ))
        archive.writestr("conversions.csv", _csv(
            ["name", "unique_conversions", "total_conversions"],
            [
                {"name": "Qualifier Start", "unique_conversions": "2", "total_conversions": "4"},
                {"name": "Qualifier Complete", "unique_conversions": "1", "total_conversions": "2"},
                {"name": "Old Event", "unique_conversions": "1", "total_conversions": "1"},
            ],
        ))
        archive.writestr("pages.csv", _csv(
            ["name", "visitors", "pageviews"],
            [
                {"name": "/", "visitors": "3", "pageviews": "8"},
                {"name": "/assess/", "visitors": "1", "pageviews": "2"},
            ],
        ))


def test_report_uses_exact_windows_named_denominators_and_legacy_separation():
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "export.zip"
        _fixture(path)
        report = build_report(path, generated_at="2026-08-25T00:00:00+00:00")
    assert report["source"]["window_start"] == "2026-08-24"
    assert report["source"]["window_end"] == "2026-08-25"
    assert report["source"]["window_days"] == 2
    assert report["traffic"]["daily_visitor_sum"] == 4
    assert report["counts"]["homepage_pageviews"] == 8
    assert report["rates"]["qualifier_start_rate"] == 0.5
    assert report["rates"]["qualifier_completion_rate"] == 0.5
    assert report["raw_event_counts"]["Qualifier Complete"]["total_conversions"] == 2
    assert "Old Event" in report["legacy_events"]


def test_pre_contract_export_does_not_turn_missing_new_events_into_zero():
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "old.zip"
        _fixture(path, dates=("2026-08-13", "2026-08-14"))
        report = build_report(path)
    assert report["source"]["fresh_for_event_contract"] is False
    assert report["counts"]["qualifier_start"] is None
    assert report["rates"]["qualifier_start_rate"] is None


def test_report_rejects_a_discontinuous_daily_window():
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "gap.zip"
        _fixture(path, dates=("2026-08-24", "2026-08-26"))
        try:
            build_report(path)
        except ValueError as error:
            assert "continuous daily window" in str(error)
        else:
            raise AssertionError("expected a discontinuous-window failure")
