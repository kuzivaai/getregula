#!/usr/bin/env python3
# regula-ignore
"""Select a blind subset from the existing corpus for second-rater validation.

Produces a rating packet: findings with code context but NO labels.
The rater sees everything except the original label and labeller.

Usage:
    python3 benchmarks/select_blind_subset.py --n 50 --seed 2026 --output benchmarks/rater2_blind_subset.json
"""

import argparse
import json
import random
import sys
from pathlib import Path

LABELS_FILE = Path(__file__).parent / "labels.json"


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--n", type=int, default=50, help="Number of entries to select")
    parser.add_argument("--seed", type=int, default=2026, help="Random seed for reproducibility")
    parser.add_argument("--output", type=Path, default=Path("benchmarks/rater2_blind_subset.json"))
    args = parser.parse_args()

    labels = json.load(LABELS_FILE.open())
    labelled = [e for e in labels if e.get("label") in ("tp", "fp")]

    if args.n > len(labelled):
        print(f"Requested {args.n} but only {len(labelled)} labelled entries exist",
              file=sys.stderr)
        args.n = len(labelled)

    random.seed(args.seed)
    subset = random.sample(labelled, args.n)

    # Strip labels — rater must judge blind
    blind_entries = []
    for entry in subset:
        blind = {k: v for k, v in entry.items()
                 if k not in ("label", "labeller", "adjudicated", "adjudication_notes")}
        blind["label"] = ""  # empty — rater fills this in
        blind["notes"] = ""  # empty — rater provides their own rationale
        blind_entries.append(blind)

    output = {
        "corpus": "blind_subset_existing",
        "source": str(LABELS_FILE),
        "total_in_source": len(labelled),
        "selected": len(blind_entries),
        "seed": args.seed,
        "instructions": (
            "For each finding, set 'label' to 'tp' (true positive — genuinely risky) "
            "or 'fp' (false positive — pattern matched but not a real risk). "
            "Add 'notes' explaining your rationale. See LABELLING_CRITERIA.md for "
            "definitions and examples per tier."
        ),
        "labels": blind_entries,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, ensure_ascii=False))
    print(f"Blind subset: {len(blind_entries)} entries written to {args.output}")
    print(f"Seed: {args.seed} (reproducible)")

    # Per-tier breakdown
    from collections import Counter
    tiers = Counter(e["tier"] for e in blind_entries)
    for tier, count in sorted(tiers.items()):
        print(f"  {tier}: {count}")


if __name__ == "__main__":
    main()
