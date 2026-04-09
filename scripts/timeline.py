# regula-ignore
#!/usr/bin/env python3
"""
Regula Timeline — EU AI Act Enforcement Dates

Displays current enforcement dates with Digital Omnibus status.
Updated with verified information as of 5 April 2026.

Sources (verified Apr 2026):
- Regulation (EU) 2024/1689 (eur-lex.europa.eu/eli/reg/2024/1689/oj)
- Commission Omnibus proposal COM(2025) 836, adopted 19 November 2025
  (europarl.europa.eu/legislative-train/package-digital-package/file-digital-omnibus-on-ai)
- Council general approach, 13 March 2026
  (consilium.europa.eu/en/press/press-releases/2026/03/13/council-agrees-position-to-streamline-rules-on-artificial-intelligence/)
- Parliament plenary 26 March 2026: 569 in favour, 45 against, 23 abstentions
  (europarl.europa.eu/news/en/press-room/20260323IPR38829/ +
   howtheyvote.eu/votes/189384)
- IAPP: Commission missed Article 6(5) guidance deadline of 2 February 2026
  (iapp.org/news/a/european-commission-misses-deadline-for-ai-act-guidance-on-high-risk-systems)
- Trilogues began April 2026 (post-Parliament-plenary). Cypriot Council
  Presidency H1 2026 targets political agreement by late April / May 2026.
- Transparency Code of Practice second draft, 3 March 2026
"""

import json
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
        "note": "European Commission missed its own deadline for publishing guidance on high-risk classification. Still not published as of 5 April 2026.",
    },
    {
        "date": "2026-03-03",
        "event": "Transparency Code of Practice — second draft published",
        "status": "in_progress",
        "source": "EC, 3 March 2026",
        "note": "Second draft of Code of Practice on marking and labelling AI-generated content. Two-layered system: secured metadata + digital watermarking. Stakeholder feedback closed 30 March 2026. Finalization expected May-June 2026.",
    },
    {
        "date": "2026-03-26",
        "event": "Parliament plenary adopts Omnibus position (569 in favour, 45 against, 23 abstentions)",
        "status": "effective",
        "source": "European Parliament, 26 March 2026",
        "note": "Parliament confirmed committee position on Digital Omnibus. Key additions: reinstated registration for non-high-risk AI systems, November 2026 watermarking deadline, new prohibition on non-consensual intimate deepfakes.",
    },
    {
        "date": "2026-04-01",
        "event": "AICDI corporate AI governance report published",
        "status": "effective",
        "source": "UNESCO + Thomson Reuters Foundation, Apr 2026",
        "note": "UNESCO + Thomson Reuters Foundation AI Company Data Initiative. Approximately 3,000 global companies (UNESCO press release wording, confirmed by Policy Edge, Digital Watch, Eco-Business, Economy Middle East). Data collected July–November 2025. Press-verified gaps: 44% have an AI strategy; 10% publicly committed to a governance framework; 12% have human oversight policies; 11% evaluate environmental impact; 7% evaluate human rights impact; 30% offer any AI training and 12% offer structured coverage; fewer than 1 in 5 conduct AI-specific DPIA. Finer-grained breakdowns (model registry %, complaints mechanism %, board oversight %, ethical impact %) are NOT disclosed in any public press coverage and require the full AICDI PDF (not available on unesdoc.unesco.org as of April 2026). Press release: https://www.unesco.org/en/articles/pioneering-report-thomson-reuters-foundation-and-unesco-sheds-light-way-3000-companies-approach-ai ; full PDF (gated behind Cloudflare, browser download required): https://unesdoc.unesco.org/ark:/48223/pf0000397817_eng",
    },
    {
        "date": "2026-04-28",
        "event": "Omnibus trilogue — Cypriot Presidency target for political agreement",
        "status": "proposed",
        "source": "Cypriot Council Presidency (H1 2026); Lewis Silkin analysis, April 2026",
        "note": "Trilogue negotiations between Parliament, Council and Commission began in April 2026 after Parliament's plenary vote on 26 March 2026. The Cypriot Council Presidency is targeting political agreement by late April / May 2026. Both co-legislators are aligned on key elements: Annex III delay to 2 December 2027, Annex I delay to 2 August 2028, new prohibition on non-consensual sexual deepfakes.",
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
        "source": "EU Parliament plenary 569-45, 26 March 2026; Council mandate 13 March 2026",
        "note": "NOT YET LAW — trilogue in progress (began April 2026 after Parliament's 26 March plenary vote). Both co-legislators aligned. Would replace August 2026 deadline for Annex III systems (employment, credit, education, biometrics, etc.). Cypriot Council Presidency targets political agreement by late April / May 2026.",
    },
    {
        "date": "2028-08-02",
        "event": "Proposed: High-risk Annex I systems deadline (Digital Omnibus)",
        "status": "proposed",
        "source": "EU Parliament committees joint report, March 2026",
        "note": "NOT YET LAW. Would apply to AI systems under EU harmonisation legislation (machinery, medical devices, etc.).",
    },
    {
        "date": "2027-12-02",
        "event": "Proposed: AI regulatory sandbox establishment deadline (Omnibus)",
        "status": "proposed",
        "source": "Council mandate 13 March 2026; Pearl Cohen analysis",
        "note": "NOT YET LAW. Postpones the original August 2026 deadline for Member States to establish national AI regulatory sandboxes by 16 months. Aligns with the proposed Annex III high-risk delay.",
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
