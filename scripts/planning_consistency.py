#!/usr/bin/env python3
"""Planning document consistency checker.

Catches the class of defect where summary counts disagree with the
underlying data — the "BACKLOG arithmetic" defect class from Session 9.

Run: python3 scripts/planning_consistency.py
Exit 0 = all consistent, exit 1 = defects found.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKLOG = ROOT / "planning" / "BACKLOG.md"


def check_backlog_status_counts() -> list[str]:
    """Recompute BACKLOG.md status counts from status lines and compare to summary table."""
    errors = []
    text = BACKLOG.read_text(encoding="utf-8")
    lines = text.splitlines()

    # Extract actual statuses from **Status:** lines
    status_counts: dict[str, int] = {}
    for line in lines:
        m = re.match(r'^\*\*Status:\*\*\s+(\w[\w ]*)', line)
        if m:
            raw = m.group(1).strip().split(" — ")[0].split(" (")[0]
            status_counts[raw] = status_counts.get(raw, 0) + 1

    # Extract summary table counts
    in_summary = False
    table_counts: dict[str, int] = {}
    for line in lines:
        if "## Summary Statistics" in line:
            in_summary = True
            continue
        if in_summary and line.startswith("| ") and "DONE" in line.upper() or \
           in_summary and line.startswith("| ") and "PARTIAL" in line.upper() or \
           in_summary and line.startswith("| ") and "NOT STARTED" in line.upper() or \
           in_summary and line.startswith("| ") and "NOT SUBMITTED" in line.upper() or \
           in_summary and line.startswith("| ") and "GATED" in line.upper():
            parts = [p.strip() for p in line.split("|") if p.strip()]
            if len(parts) >= 2:
                label = parts[0].strip("* ")
                try:
                    count = int(parts[1])
                    table_counts[label] = count
                except ValueError:
                    pass

    # Compare
    for label, actual in status_counts.items():
        table_val = table_counts.get(label)
        if table_val is not None and table_val != actual:
            errors.append(
                f"BACKLOG summary '{label}': table says {table_val}, "
                f"actual status lines = {actual}"
            )

    # Check total
    total_actual = sum(status_counts.values())
    total_tasks = len(re.findall(r'^### [A-H]\d+', text, re.MULTILINE))
    if total_actual != total_tasks:
        errors.append(
            f"BACKLOG: {total_tasks} task headings but {total_actual} status lines"
        )

    return errors


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
    all_errors.extend(check_backlog_status_counts())
    all_errors.extend(check_pattern_count_consistency())
    all_errors.extend(check_stale_regulatory_terms())
    all_errors.extend(check_blog_index_completeness())

    if all_errors:
        print(f"planning-consistency: {len(all_errors)} defect(s) found:")
        for e in all_errors:
            print(f"  FAIL  {e}")
        return 1
    else:
        print("planning-consistency: all checks passed")
        return 0


if __name__ == "__main__":
    sys.exit(main())
