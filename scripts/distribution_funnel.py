#!/usr/bin/env python3
"""Build an exact-window anonymous distribution funnel from a Plausible export.

The export contains aggregates, not a visitor-level journey. Rates in this
report therefore compare aggregate counts with named denominators; they are
directional operational measures, not cohort conversion or causal estimates.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import zipfile
from datetime import date, datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "data" / "analytics_event_spec.json"


def _rows(archive: zipfile.ZipFile, name: str) -> list[dict[str, str]]:
    try:
        raw = archive.read(name)
    except KeyError as exc:
        raise ValueError(f"Plausible export is missing {name}") from exc
    return list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))))


def _integer(row: dict[str, str], key: str) -> int:
    value = row.get(key, "").strip()
    return int(float(value)) if value else 0


def _rate(numerator: int | None, denominator: int | None) -> float | None:
    if numerator is None or denominator is None or denominator <= 0:
        return None
    return round(numerator / denominator, 4)


def build_report(export_path: Path, *, generated_at: str | None = None) -> dict:
    spec = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    with zipfile.ZipFile(export_path) as archive:
        visitors = _rows(archive, "visitors.csv")
        conversions = _rows(archive, "conversions.csv")
        pages = _rows(archive, "pages.csv")

    if not visitors:
        raise ValueError("Plausible visitors.csv is empty")
    dates = sorted(date.fromisoformat(row["date"]) for row in visitors)
    start, end = dates[0], dates[-1]
    expected_days = (end - start).days + 1
    if len({row["date"] for row in visitors}) != expected_days:
        raise ValueError("Plausible visitors.csv does not contain a continuous daily window")

    event_counts = {
        row["name"]: {
            "unique_conversions": _integer(row, "unique_conversions"),
            "total_conversions": _integer(row, "total_conversions"),
        }
        for row in conversions
    }
    page_counts = {
        row["name"]: {
            "visitors": _integer(row, "visitors"),
            "pageviews": _integer(row, "pageviews"),
        }
        for row in pages
    }
    contract_applies = end >= date.fromisoformat(spec["effective_date"])

    def event(name: str) -> int | None:
        if not contract_applies:
            return None
        return event_counts.get(name, {}).get("total_conversions", 0)

    homepage_views = sum(
        page_counts.get(path, {}).get("pageviews", 0)
        for path in ("/", "/locales/de.html", "/locales/pt-br.html")
    )
    assess_views = sum(
        page_counts.get(path, {}).get("pageviews", 0)
        for path in ("/assess/", "/assess/de.html", "/assess/pt-br.html")
    )
    pricing_views = page_counts.get("/pricing.html", {}).get("pageviews", 0)

    counts = {
        "homepage_pageviews": homepage_views,
        "assessment_pageviews": assess_views,
        "pricing_pageviews": pricing_views,
        "qualifier_start": event("Qualifier Start"),
        "qualifier_complete": event("Qualifier Complete"),
        "assessment_start": event("Assessment Start"),
        "assessment_complete": event("Assessment Complete"),
        "scanner_start": event("Scanner Start"),
        "scanner_complete": event("Scanner Complete"),
        "scanner_error": event("Scanner Error"),
        "install_command_copy": event("Install Command Copy"),
        "contact_intent": event("Contact Intent"),
    }
    rates = {
        "qualifier_start_rate": _rate(counts["qualifier_start"], homepage_views),
        "qualifier_completion_rate": _rate(counts["qualifier_complete"], counts["qualifier_start"]),
        "assessment_start_rate": _rate(counts["assessment_start"], assess_views),
        "assessment_completion_rate": _rate(counts["assessment_complete"], counts["assessment_start"]),
        "scanner_start_rate": _rate(counts["scanner_start"], assess_views),
        "scanner_completion_rate": _rate(counts["scanner_complete"], counts["scanner_start"]),
        "scanner_error_rate": _rate(counts["scanner_error"], counts["scanner_start"]),
        "contact_intent_per_pricing_view": _rate(counts["contact_intent"], pricing_views),
    }

    return {
        "format_version": 1,
        "event_spec_id": spec["spec_id"],
        "event_spec_effective_date": spec["effective_date"],
        "generated_at": generated_at or datetime.now(timezone.utc).isoformat(),
        "source": {
            "kind": "plausible_aggregate_export",
            "file": export_path.name,
            "window_start": start.isoformat(),
            "window_end": end.isoformat(),
            "window_days": expected_days,
            "fresh_for_event_contract": contract_applies,
        },
        "traffic": {
            "daily_visitor_sum": sum(_integer(row, "visitors") for row in visitors),
            "pageviews": sum(_integer(row, "pageviews") for row in visitors),
            "visits": sum(_integer(row, "visits") for row in visitors),
            "note": "Daily visitor counts are summed; this is not a period-unique visitor count.",
        },
        "counts": counts,
        "rates": rates,
        "raw_event_counts": event_counts,
        "legacy_events": {
            name: value for name, value in event_counts.items()
            if name not in spec["events"]
        },
        "interpretation_limits": [
            "Plausible exports are aggregate tables and do not expose a cohort journey.",
            "Rates compare aggregate event totals with named aggregate denominators.",
            "No causal or statistical-significance claim is supported at the retained traffic level.",
            "A pre-contract export cannot establish a baseline for the current event names.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Plausible export ZIP")
    parser.add_argument("--output", type=Path, help="Write JSON report to this path")
    args = parser.parse_args(argv)
    report = build_report(args.input)
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
