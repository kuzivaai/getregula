# regula-ignore — enforcement-date prose names prohibited and high-risk obligations per deadline
#!/usr/bin/env python3
"""
Regula Timeline — EU AI Act Enforcement Dates

Displays current enforcement dates, including the Digital Omnibus
(Regulation (EU) 2026/1744, OJ 24 July 2026, in force from 27 July 2026).

Updated: 26 July 2026.

Regulatory baseline (verified sources):
- Regulation (EU) 2024/1689 (eur-lex.europa.eu/eli/reg/2024/1689/oj)
- Regulation (EU) 2026/1744, Digital Omnibus on AI, OJ 24 July 2026
  (eur-lex.europa.eu/eli/reg/2026/1744/oj); provisional agreement
  7 May 2026 (consilium.europa.eu/en/press/press-releases/2026/05/07/
   artificial-intelligence-council-and-parliament-agree-to-
   simplify-and-streamline-rules/)
- Gibson Dunn analysis, May 2026
- Latham & Watkins analysis, May 2026
- Bird & Bird, Travers Smith, Inside Privacy, White & Case (May 2026)
- Code of Practice on AI content marking — final, 10 June 2026
  (digital-strategy.ec.europa.eu/en/policies/code-practice-ai-generated-content)
- Art 50 transparency guidelines — draft, consultation closed 3 June 2026
- Art 6 high-risk classification guidelines — draft, consultation open
  until 23 June 2026
"""

import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from omnibus import (
    BINDING_NOTE,
    OMNIBUS_ENACTED,
    OMNIBUS_OJ_DATE,
    OMNIBUS_IN_FORCE_DATE,
    OMNIBUS_STATUS,
)

# Enactment-dependent suffix for every Omnibus timeline note. Derives from
# omnibus.py so the OJ flip is a one-line change there; the previous
# hardcoded suffix went stale the day the Council approved. Entry into force is
# 3 days after OJ publication, so the note keys off OMNIBUS_IN_FORCE_DATE, not
# the OJ date (asserting "in force" on the OJ date would be up to 3 days early).
_OMNIBUS_NOTE_STATUS = (
    f"In force from {OMNIBUS_IN_FORCE_DATE} (published in OJ {OMNIBUS_OJ_DATE})."
    if OMNIBUS_ENACTED
    else "Adopted by EP (16 Jun) and Council (29 Jun 2026); pending OJ publication."
)

# Row status and source for Omnibus-created milestones, likewise derived:
# "agreed" was accurate between the 7 May trilogue and OJ publication, but
# understates enacted law once the regulation is in the OJ.
_OMNIBUS_ROW_STATUS = "enacted" if OMNIBUS_ENACTED else "agreed"
_OMNIBUS_SOURCE = (
    "Regulation (EU) 2026/1744 (Digital Omnibus), OJ 24 Jul 2026"
    if OMNIBUS_ENACTED
    else "Omnibus provisional agreement, 7 May 2026"
)


# ---------------------------------------------------------------------------
# Timeline data — verified against primary sources (June 2026)
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
        "event": "Article 5 prohibitions apply (8 practices)",
        "status": "effective",
        "source": "Article 113(a)",
        "note": (
            "All 8 Article 5 prohibitions are now enforceable. "
            "Penalties: up to EUR 35M or 7% global turnover."
        ),
    },
    {
        "date": "2025-08-02",
        "event": "General-purpose AI model rules apply (Articles 51-55)",
        "status": "effective",
        "source": "Article 113(b)",
        "note": (
            "GPAI transparency requirements in effect. Model providers must "
            "document training data and provide technical documentation."
        ),
    },
    {
        "date": "2026-05-07",
        "event": "Digital Omnibus provisional agreement reached",
        "status": "effective",
        "source": "Council press release, 7 May 2026",
        "note": (
            "Council and Parliament reached provisional political agreement "
            "on the Digital Omnibus on AI. Key changes: Annex III high-risk "
            "deferred to 2 December 2027; Annex I to 2 August 2028; new "
            "Article 5 prohibition on CSAM/NCII generation (2 December 2026); "
            "watermarking for existing systems deferred to 2 December 2026; "
            "sandboxes deferred to 2 August 2027. "
            + _OMNIBUS_NOTE_STATUS
        ),
    },
    {
        "date": "2026-06-10",
        "event": "Code of Practice on AI content marking — FINAL published",
        "status": "effective",
        "source": "European Commission, 10 June 2026",
        "note": (
            "Voluntary code of practice for Article 50(2) machine-readable "
            "marking and Article 50(4) deepfake labelling. Open for "
            "signatories. Compliance with Art 50 obligations applies from "
            "2 August 2026."
        ),
    },
    {
        "date": "2026-08-02",
        "event": "Article 50 transparency obligations apply",
        "status": "current_law",
        "source": "Article 113(b); unchanged by Omnibus",
        "note": (
            "Interaction disclosure (Art 50(1)), watermarking for NEW systems "
            "(Art 50(2)), emotion recognition (Art 50(3)), and deepfake "
            "labelling (Art 50(4)) all apply from this date. Unchanged by "
            "the Omnibus. Article 49 registration also applies."
        ),
    },
    {
        "date": "2026-12-02",
        "event": "Omnibus: watermarking for EXISTING systems + Art 5 CSAM/NCII",
        "status": _OMNIBUS_ROW_STATUS,
        "source": _OMNIBUS_SOURCE,
        "note": (
            "Two obligations take effect on this date under the Omnibus: "
            "(1) Art 50(2) watermarking obligations for AI systems already "
            "on the market before 2 August 2026. (2) New Art 5 prohibition "
            "on AI systems that generate child sexual abuse material or "
            "non-consensual intimate imagery of identifiable persons. "
            + _OMNIBUS_NOTE_STATUS
        ),
    },
    {
        "date": "2026-12-31",
        "event": "Target: CEN-CENELEC harmonised standards publication",
        "status": "in_progress",
        "source": "CEN/CENELEC JTC 21; AI Assurance Institute",
        "note": (
            "prEN 18228 (AI risk management, maps to Art 9) and prEN 18282 "
            "(cybersecurity for AI, maps to Art 15) are in Public Enquiry. "
            "Publication expected Q4 2026. OJEU citation (presumption of "
            "conformity) estimated H1 2027."
        ),
    },
    {
        "date": "2027-08-02",
        "event": "Omnibus: AI regulatory sandbox establishment deadline",
        "status": _OMNIBUS_ROW_STATUS,
        "source": _OMNIBUS_SOURCE,
        "note": (
            "Member States must establish national AI regulatory sandboxes "
            "by this date. Original deadline was 2 August 2026; deferred "
            "by 12 months under the Omnibus. " + _OMNIBUS_NOTE_STATUS
        ),
    },
    {
        "date": "2027-12-02",
        "event": "Omnibus: Annex III standalone high-risk AI obligations",
        "status": _OMNIBUS_ROW_STATUS,
        "source": _OMNIBUS_SOURCE,
        "note": (
            "High-risk obligations (Articles 9-15) for standalone use-based "
            "AI systems under Annex III: biometrics, employment, education, "
            "credit scoring, law enforcement, migration, etc. Original "
            "deadline was 2 August 2026; deferred 16 months under the "
            "Omnibus. " + _OMNIBUS_NOTE_STATUS + " Multiple law firms (Bird & "
            "Bird, Travers Smith, Modulos) advise planning against this "
            "date as the baseline."
        ),
    },
    {
        "date": "2028-08-02",
        "event": "Omnibus: Annex I product-embedded high-risk AI obligations",
        "status": _OMNIBUS_ROW_STATUS,
        "source": _OMNIBUS_SOURCE,
        "note": (
            "High-risk obligations for AI systems embedded in products "
            "regulated under EU harmonisation legislation (Annex I): "
            "medical devices, machinery, toys, lifts, radio equipment. "
            "Original deadline was 2 August 2027; deferred 12 months under "
            "the Omnibus. " + _OMNIBUS_NOTE_STATUS
        ),
    },
]


STATUS_LABELS = {
    "effective": "IN EFFECT",
    "overdue": "OVERDUE",
    "current_law": "CURRENT LAW",
    "in_progress": "IN PROGRESS",
    "agreed": "AGREED (pending adoption)",
    "enacted": "ENACTED (future application date)",
}

STATUS_INDICATORS = {
    "effective": "[LIVE]",
    "overdue": "[LATE]",
    "current_law": "[LAW]",
    "in_progress": "[WIP]",
    "agreed": "[AGR]",
    "enacted": "[ENA]",
}


def format_timeline_text() -> str:
    today = date.today().isoformat()
    lines = [
        "",
        "=" * 68,
        "  Regula — EU AI Act Enforcement Timeline",
        f"  As of: {today}",
        "=" * 68,
        "",
        "  Status key:",
        "    [LIVE] = enforceable now   [LAW] = legally binding date",
        (f"    [ENA]  = enacted by the Omnibus (in force from {OMNIBUS_IN_FORCE_DATE}), future application date"
         if OMNIBUS_ENACTED
         else "    [AGR]  = agreed in Omnibus (pending OJ publication)"),
        "    [WIP]  = in progress       [LATE] = deadline missed",
        "",
        # Enacted, BINDING_NOTE already contains the full status; printing
        # OMNIBUS_STATUS as well would repeat the same sentence twice.
        f"  IMPORTANT: Digital Omnibus status: {BINDING_NOTE}"
        if OMNIBUS_ENACTED
        else f"  IMPORTANT: Digital Omnibus status: {OMNIBUS_STATUS}.\n  {BINDING_NOTE}",
        "",
    ]

    for entry in TIMELINE:
        indicator = STATUS_INDICATORS.get(entry["status"], "[???]")
        lines.append(f"  {entry['date']}  {indicator}  {entry['event']}")
        if entry.get("note"):
            note = entry["note"]
            while note:
                chunk = note[:58]
                if len(note) > 58:
                    last_space = chunk.rfind(" ")
                    if last_space > 30:
                        chunk = note[:last_space]
                lines.append(f"                         {chunk}")
                note = note[len(chunk):].strip()
        lines.append("")

    if OMNIBUS_ENACTED:
        footer_note = [
            "  " + "-" * 64,
            "  The Omnibus completed the full legislative process: EP plenary",
            "  (16 Jun 2026), Council (29 Jun 2026), signature (8 Jul 2026),",
            f"  Official Journal publication ({OMNIBUS_OJ_DATE}). The deferred",
            f"  deadlines are enacted law, in force from {OMNIBUS_IN_FORCE_DATE}.",
            "  " + "-" * 64,
        ]
    else:
        footer_note = [
            "  " + "-" * 64,
            "  Provisional agreement ≠ formal adoption. The Omnibus must",
            "  pass EP plenary, Council endorsement, and be published in",
            "  the Official Journal before new deadlines become binding.",
            "  " + "-" * 64,
        ]
    lines.extend([
        *footer_note,
        "",
        "  Sources: Regulation (EU) 2026/1744 (OJ, 24 Jul 2026), EU Council",
        "  press release (7 May 2026), Gibson Dunn, Latham & Watkins,",
        "  Bird & Bird, Travers Smith, White & Case, EC Code of Practice",
        "  on AI content marking (10 June 2026)",
        "",
    ])

    return "\n".join(lines)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="EU AI Act enforcement timeline"
    )
    parser.add_argument(
        "--format", "-f", choices=["text", "json"], default="text"
    )
    args = parser.parse_args()

    if args.format == "json":
        print(json.dumps({
            "as_of": date.today().isoformat(),
            # Enacted, BINDING_NOTE already contains the full status; the
            # concatenation would print the same sentence twice.
            "omnibus_status": (BINDING_NOTE if OMNIBUS_ENACTED
                               else f"{OMNIBUS_STATUS}. {BINDING_NOTE}"),
            "timeline": TIMELINE,
        }, indent=2))
    else:
        print(format_timeline_text())


if __name__ == "__main__":
    main()
