#!/usr/bin/env python3
"""Repository planning-record consistency checker.

Catches the class of defect where planning summaries or integrity claims
disagree with the records they describe.

Run: python3 scripts/planning_consistency.py
Exit 0 = all consistent, exit 1 = defects found.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def check_ledger_integrity() -> list[str]:
    """Validate the current ledger instead of opening a deleted backlog."""
    sys.path.insert(0, str(ROOT / "scripts"))
    import ledger_status

    errors = []
    try:
        entries = ledger_status.parse_full()
    except (OSError, ValueError) as exc:
        return [f"LEDGER cannot be enumerated: {exc}"]

    known = {nid for nid, _state, _body in entries}
    for nid, refs in ledger_status.divergences(entries):
        if not refs:
            errors.append(
                f"LEDGER {nid} is CLOSED while its status reads outstanding "
                "and has no Resolved by declaration"
            )
    for nid, _state, body in entries:
        for ref in ledger_status.resolved_by(body):
            if ref not in known:
                errors.append(f"LEDGER {nid} has missing Resolved by target {ref}")
            elif ref == nid:
                errors.append(f"LEDGER {nid} cannot resolve itself")

    legacy = ledger_status.legacy_rows()
    overlap = known.intersection(legacy)
    if overlap:
        errors.append(
            "LEDGER ids occur in both legacy and machine-state populations: "
            + ", ".join(sorted(overlap))
        )
    return errors


def planning_notes() -> list[str]:
    """Coverage limits that are important but not fabricated as defects."""
    sys.path.insert(0, str(ROOT / "scripts"))
    import ledger_status

    classifications = ledger_status.legacy_classifications()
    review_required = sum(
        row["state"] == "REVIEW_REQUIRED" for row in classifications
    )
    return [
        f"LEDGER has {len(classifications)} legacy table rows outside the "
        f"heading-state totals; {review_required} conservatively remain "
        "REVIEW_REQUIRED and ledger_status --legacy enumerates every row"
    ] if classifications else []


def check_pattern_count_consistency() -> list[str]:
    """Check that site_facts.json pattern_count matches risk_patterns.py."""
    errors = []
    import json

    facts_path = ROOT / "data" / "site_facts.json"
    if facts_path.exists():
        facts = json.loads(facts_path.read_text(encoding="utf-8"))
        claimed = facts.get("pattern_count")
        if claimed:
            # Count actual patterns in risk_patterns.py
            rp_path = ROOT / "scripts" / "risk_patterns.py"
            rp_text = rp_path.read_text(encoding="utf-8")
            # Count r"..." pattern strings in pattern lists
            actual = len(re.findall(r'r"[^"]+(?<!\\)"', rp_text))
            # This is approximate — the claim auditor does the precise check
            if abs(actual - claimed) > 5:
                errors.append(
                    f"site_facts.json pattern_count={claimed} but "
                    f"risk_patterns.py has ~{actual} regex patterns"
                )

    return errors


def check_stale_regulatory_terms() -> list[str]:
    """Detect stale Omnibus language in user-facing scripts.

    After the 7 May 2026 agreement, "trilogue in progress" and
    "proposes" (in Omnibus context) are stale in scripts/*.py.
    Blog posts may keep historical language behind editor's notes.
    """
    errors = []
    stale_patterns = [
        (re.compile(r'trilogue.{0,20}in.?progress', re.IGNORECASE), "trilogue in progress"),
        (re.compile(r'omnibus.{0,20}proposes', re.IGNORECASE), "Omnibus proposes"),
        (re.compile(r'under.?active.?negotiation', re.IGNORECASE), "under active negotiation"),
        (re.compile(r'trilogue.?failed', re.IGNORECASE), "trilogue failed"),
    ]
    scan_dirs = [ROOT / "scripts", ROOT / "configs"]
    self_path = Path(__file__).resolve()
    for d in scan_dirs:
        if not d.exists():
            continue
        for f in d.rglob("*.py"):
            if f.resolve() == self_path:
                continue
            text = f.read_text(encoding="utf-8", errors="replace")
            for pat, label in stale_patterns:
                for m in pat.finditer(text):
                    line_num = text[:m.start()].count("\n") + 1
                    errors.append(
                        f"{f.relative_to(ROOT)}:{line_num}: stale '{label}' — "
                        f"Omnibus agreed 7 May 2026"
                    )
        for f in d.rglob("*.yaml"):
            text = f.read_text(encoding="utf-8", errors="replace")
            for pat, label in stale_patterns:
                for m in pat.finditer(text):
                    line_num = text[:m.start()].count("\n") + 1
                    errors.append(
                        f"{f.relative_to(ROOT)}:{line_num}: stale '{label}' — "
                        f"Omnibus agreed 7 May 2026"
                    )
    return errors


def check_blog_index_completeness() -> list[str]:
    """Check that all blog HTML files are listed in writing.html."""
    errors = []
    blog_dir = ROOT / "site" / "blog"
    index_file = blog_dir / "writing.html"
    if not index_file.exists():
        return errors
    index_text = index_file.read_text(encoding="utf-8")
    for f in sorted(blog_dir.glob("blog-*.html")):
        fname = f.name
        if fname not in index_text:
            errors.append(f"Blog post {fname} not listed in writing.html")
    return errors


def main() -> int:
    all_errors: list[str] = []
    all_errors.extend(check_ledger_integrity())
    all_errors.extend(check_pattern_count_consistency())
    all_errors.extend(check_stale_regulatory_terms())
    all_errors.extend(check_blog_index_completeness())

    if all_errors:
        print(f"planning-consistency: {len(all_errors)} defect(s) found:")
        for e in all_errors:
            print(f"  FAIL  {e}")
        return 1
    else:
        print("planning-consistency: all executable checks passed")
        for note in planning_notes():
            print(f"  NOTE  {note}")
        return 0


if __name__ == "__main__":
    sys.exit(main())
