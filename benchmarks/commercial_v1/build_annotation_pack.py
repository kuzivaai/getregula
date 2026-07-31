#!/usr/bin/env python3
"""Build the blinded, unlabelled Candidate C annotation pack."""

import json
from pathlib import Path


PURPOSES = [
    ("rank job applicants", "employment", "access to employment"),
    ("prioritise emergency patients", "hospital", "access to treatment"),
    ("recommend consumer credit", "bank", "access to credit"),
    ("forecast electricity demand", "utility", "service planning"),
    ("summarise legal filings", "law firm", "professional assistance"),
    ("triage visa applications", "public authority", "migration decision"),
]


def main():
    rows = []
    for index in range(30):
        purpose, context, consequence = PURPOSES[index % len(PURPOSES)]
        rows.append({
            "scenario_id": f"c-scenario-{index + 1:02d}",
            "intended_purpose": purpose,
            "provider_role": "develops and places the configured system on the market",
            "deployer_role": f"organisation operating it in a {context} context",
            "affected_person_group": "natural persons subject to or affected by the output",
            "deployment_context": context,
            "decision_consequence": consequence,
            "human_oversight_context": "a named reviewer can inspect and override outputs",
            "code_evidence": "model inference feeds a recommendation record; final workflow context is declared, not inferred from code",
            "primary_source_rules": ["Regulation (EU) 2024/1689 Articles 3(12), 6(1)-(4), Annex III"],
            "rater_1_label": None,
            "rater_2_label": None,
            "rater_1_reason": None,
            "rater_2_reason": None,
            "adjudicated_label": None,
            "adjudication_reason": None,
            "ground_truth_status": "MODEL-PROVISIONAL until independent human ratings and adjudication"
        })
    target = Path(__file__).with_name("annotation_pack.json")
    target.write_text(json.dumps(rows, indent=2) + "\n")
    print(f"wrote {len(rows)} unlabelled Candidate C scenarios")


if __name__ == "__main__":
    main()
