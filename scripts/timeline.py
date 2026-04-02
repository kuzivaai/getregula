# regula-ignore
#!/usr/bin/env python3
"""
Regula Timeline — EU AI Act Enforcement Dates

Displays current enforcement dates with Digital Omnibus status.
Updated with verified information as of 25 March 2026.

Sources:
- EU AI Act implementation timeline (artificialintelligenceact.eu)
- Digital Omnibus: Parliament committees voted 101-9 on 18 March 2026
- IAPP coverage of Commission missed deadline
- Council position 13 March 2026
"""

import json
import sys
from datetime import date


# ---------------------------------------------------------------------------
# Timeline data — verified against primary sources
# ---------------------------------------------------------------------------

TIMELINE = [
    {
        "date": "2024-08-01",
        "event": "EU AI Act entered into force",
        "status": "effective",
        "source": "Regulation 2024/1689, Article 113",
    },
    {
        "date": "2025-02-02",
        "event": "Prohibited AI practices (Article 5) apply",
        "status": "effective",
        "source": "Article 113(a)",
        "note": "All 8 Article 5 prohibitions are now enforceable. Penalties: up to EUR 35M or 7% global turnover.",
    },
    {
        "date": "2025-08-02",
        "event": "General-purpose AI model rules apply",
        "status": "effective",
        "source": "Article 113(b)",
        "note": "GPAI transparency requirements in effect. Model providers must document training data and provide Safety and Security Reports.",
    },
    {
        "date": "2026-02-02",
        "event": "Article 6 guidance deadline (MISSED)",
        "status": "overdue",
        "source": "IAPP, March 2026",
        "note": "European Commission missed its own deadline for publishing guidance on high-risk classification. Draft expected 'by end of month' (not yet published as of 25 March 2026).",
    },
    {
        "date": "2026-08-02",
        "event": "High-risk AI system requirements (Articles 9-15)",
        "status": "current_law",
        "source": "Article 113(c)",
        "note": "LEGALLY BINDING DATE as of today. However, the Digital Omnibus proposes postponement (see below).",
    },
    {
        "date": "2026-10-30",
        "event": "prEN 18286 (Quality Management System) — public enquiry closed Jan 2026",
        "status": "in_progress",
        "source": "CEN/CENELEC JTC 21",
        "note": "First harmonised standard for AI Act. Addresses Article 17 (QMS). Enquiry ran 30 Oct 2025 — 22 Jan 2026. Publication expected Q4 2026.",
    },
    {
        "date": "2026-12-31",
        "event": "Target: CEN-CENELEC AI Act standards publication",
        "status": "in_progress",
        "source": "CEN/CENELEC acceleration measures, Oct 2025",
        "note": "Standards expected to cover: risk management (Art 9), data governance (Art 10), transparency (Art 13), human oversight (Art 14), accuracy/robustness (Art 15). Accelerated process adopted Oct 2025 to allow direct publication without separate Formal Vote.",
    },
    {
        "date": "2027-12-02",
        "event": "Proposed: High-risk Annex III systems deadline (Digital Omnibus)",
        "status": "proposed",
        "source": "EU Parliament committees vote 101-9, 18 March 2026",
        "note": "NOT YET LAW. Parliament plenary vote expected 26 March 2026, followed by trilogue negotiations. Would replace August 2026 deadline for Annex III systems (employment, credit, education, biometrics, etc.).",
    },
    {
        "date": "2028-08-02",
        "event": "Proposed: High-risk Annex I systems deadline (Digital Omnibus)",
        "status": "proposed",
        "source": "EU Parliament committees joint report, March 2026",
        "note": "NOT YET LAW. Would apply to AI systems under EU harmonisation legislation (machinery, medical devices, etc.).",
    },
]


STATUS_LABELS = {
    "effective": "IN EFFECT",
    "overdue": "OVERDUE",
    "current_law": "CURRENT LAW",
    "in_progress": "IN PROGRESS",
    "proposed": "PROPOSED",
}

STATUS_INDICATORS = {
    "effective": "[LIVE]",
    "overdue": "[LATE]",
    "current_law": "[LAW]",
    "in_progress": "[WIP]",
    "proposed": "[PROP]",
}


def format_timeline_text() -> str:
    today = date.today().isoformat()
    lines = [
        "",
        "=" * 64,
        "  Regula — EU AI Act Enforcement Timeline",
        f"  As of: {today}",
        "=" * 64,
        "",
        "  Status: [LIVE] = enforceable now  [LAW] = legally binding date",
        "          [PROP] = proposed, not yet law  [LATE] = deadline missed",
        "",
    ]

    for entry in TIMELINE:
        indicator = STATUS_INDICATORS.get(entry["status"], "[???]")
        lines.append(f"  {entry['date']}  {indicator}  {entry['event']}")
        if entry.get("note"):
            # Wrap note at ~60 chars
            note = entry["note"]
            while note:
                chunk = note[:58]
                if len(note) > 58:
                    # Break at last space
                    last_space = chunk.rfind(" ")
                    if last_space > 30:
                        chunk = note[:last_space]
                lines.append(f"                         {chunk}")
                note = note[len(chunk):].strip()
        lines.append("")

    lines.extend([
        "  " + "-" * 60,
        "  IMPORTANT: The August 2026 deadline remains legally binding.",
        "  The December 2027 extension is a proposal under active",
        "  negotiation and has NOT yet become law.",
        "  " + "-" * 60,
        "",
        "  Sources: artificialintelligenceact.eu, IAPP, EU Council,",
        "  EU Parliament committees joint report (18 March 2026)",
        "",
    ])

    return "\n".join(lines)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="EU AI Act enforcement timeline")
    parser.add_argument("--format", "-f", choices=["text", "json"], default="text")
    args = parser.parse_args()

    if args.format == "json":
        print(json.dumps({
            "as_of": date.today().isoformat(),
            "timeline": TIMELINE,
            "disclaimer": "August 2026 remains legally binding. December 2027 extension is proposed, not enacted.",
        }, indent=2))
    else:
        print(format_timeline_text())


if __name__ == "__main__":
    main()
