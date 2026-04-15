"""
Regula Security Self-Check — scan regula's own codebase with its own rules.

Known acceptable findings are documented below and excluded from the failure count.
These are tool source files, test fixtures, and synthetic examples — not real issues.

When Regula scans its own scripts/ directory, every finding is from Regula's own
implementation. The scanner naturally flags AI-related code in an AI compliance tool.
The self-check is a sanity pass: it verifies scan_files runs without error and produces
structured output. Any truly unexpected prohibited content would require manual review.
"""

from pathlib import Path


KNOWN_ACCEPTABLE = [
    # self_test.py builds synthetic prohibited/high-risk strings for testing
    {"file_pattern": "self_test.py", "reason": "synthetic test fixtures — intentional"},
    # tests/ directory may contain risk pattern examples
    {"file_pattern": "tests/", "reason": "test fixtures — intentional"},
    # risk_patterns.py contains the pattern strings themselves
    {"file_pattern": "risk_patterns.py", "reason": "pattern definitions — intentional"},
    # explain_articles.py describes prohibited practices in plain language
    {"file_pattern": "explain_articles.py", "reason": "article explanations — describes prohibited practices by design"},
    # bias_*.py modules are bias evaluation tools — expected to contain AI-related code
    {"file_pattern": "bias_", "reason": "bias evaluation modules — AI-related code by design"},
    # cli_*.py domain modules contain CLI command implementations extracted from cli.py
    {"file_pattern": "cli_", "reason": "CLI command modules — imports AI-related scanners by design"},
]


def _is_known_acceptable(finding: dict) -> tuple[bool, str]:
    """Return (True, reason) if finding matches a KNOWN_ACCEPTABLE pattern, else (False, '')."""
    file_path = finding.get("file", "")
    for entry in KNOWN_ACCEPTABLE:
        if entry["file_pattern"] and entry["file_pattern"] in file_path:
            return True, entry["reason"]
    # Findings already suppressed by a regula-ignore comment in source are acceptable
    if finding.get("suppressed", False):
        return True, "suppressed by regula-ignore in source"
    return False, ""


def run_security_self_check(format_type: str = "text") -> dict:
    """
    Scan scripts/ directory with regula's own scanner.

    Args:
        format_type: "text" prints human-readable output; "json" returns dict silently;
                     "silent" is for tests only — returns dict without any output.

    Returns dict:
    {
        "passed": bool,              # True if no unexpected findings
        "total_findings": int,       # raw count before filtering known-acceptable
        "unexpected_findings": list, # findings not in KNOWN_ACCEPTABLE
        "known_acceptable": list,    # findings that matched KNOWN_ACCEPTABLE patterns
        "message": str               # human-readable summary
    }
    """
    from report import scan_files

    scripts_dir = Path(__file__).parent
    findings = scan_files(str(scripts_dir))

    unexpected = []
    acceptable = []

    for finding in findings:
        ok, reason = _is_known_acceptable(finding)
        if ok:
            acceptable.append({**finding, "_acceptable_reason": reason})
        else:
            unexpected.append(finding)

    passed = len(unexpected) == 0

    if passed:
        message = "No unexpected findings in regula's own source."
    else:
        message = f"{len(unexpected)} unexpected finding(s) in regula's own source."

    result = {
        "passed": passed,
        "total_findings": len(findings),
        "unexpected_findings": unexpected,
        "known_acceptable": acceptable,
        "message": message,
    }

    if format_type in ("silent", "json"):
        return result

    # Text output
    print("\nRegula Security Self-Check\n")
    print(f"  Scanned: scripts/")
    print(f"  Total findings: {len(findings)}")
    print(f"  Known acceptable: {len(acceptable)} (test fixtures, pattern definitions)")
    print(f"  Unexpected findings: {len(unexpected)}\n")

    if passed:
        print(f"  PASS  No unexpected findings in regula's own source.")
    else:
        print(f"  FAIL  {len(unexpected)} unexpected finding(s) in regula's own source:")
        for f in unexpected:
            file_loc = f.get("file", "unknown")
            line = f.get("line", "?")
            tier = f.get("tier", "unknown")
            desc = f.get("description", "")
            print(f"    {file_loc}:{line}  {tier}  {desc}")

    print()
    return result
